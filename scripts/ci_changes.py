#!/usr/bin/env python3
"""Decide whether the CI mutation check has to run for this change, and on which manifests.

`scripts/mutation_check.py --all` is by far the longest step of the engine job. It proves that the
safety-rail tests notice their own removal, which only a change to code, tests or CI can break. A pull
request that touches nothing but the System Design store (lessons, figures, metadata, progress files and
its source map) cannot, so it skips the step. Any other pull request runs only the manifests that name a
file it changes: the manifest itself, its target, a `file:` of one of its entries, the module of a test
an entry names, or a repository module that test module imports, directly or through other repository modules, by an
import statement or by a `spec_from_file_location`/`import_module` call that names its file (owner decision 2026-10-19: the full run took about 90 minutes and every merge into main
restarted it on every open pull request). A change to the checker, the workflow, the dependencies, the
shared test setup (RUN_ALL) or any other shared test file, or a deleted or renamed file, runs every manifest. Every push to main runs every manifest, so what a pull
request leaves out is still checked once it lands. A change this script cannot read is treated as one
that needs the whole check.

In CI it reads GITHUB_EVENT_NAME and PR_BASE_SHA, prints the decision with its reason, and appends
`mutation=true` or `mutation=false`, and `manifests=all` or the space-separated manifests to run, to
GITHUB_OUTPUT. It never fails the job on its own account.
"""

from __future__ import annotations

import ast
import os
import pathlib
import posixpath
import subprocess
import sys
from collections.abc import Mapping

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFESTS = "tests/mutations"

# Only content of the System Design store: the lessons and the source map the checker reads.
STORE_PREFIXES = ("system-design-101/", "brainstorm/system-design-101-vi/")

# A change to any of these can change the verdict of every manifest, so a pull request touching one runs them all.
RUN_ALL = frozenset({"scripts/mutation_check.py", ".github/workflows/ci.yml", "requirements.txt", "requirements-dev.txt",
                     "tests/__init__.py", "tests/conftest.py", "pytest.ini", "pyproject.toml", "setup.cfg"})


def in_store(path: str) -> bool:
    """A path inside the store, spelled in its normal form (`store/../scripts/x.py` is not)."""
    return posixpath.normpath(path) == path and path.startswith(STORE_PREFIXES)


def mutation_needed(event: str, changed: list[str] | None) -> tuple[bool, str]:
    """Whether the mutation check has to run, and why."""
    if event != "pull_request":
        return True, f"{event or 'unknown event'}: the check always runs there"
    if not changed:
        return True, "the changed files could not be read, so the check runs"
    outside = [path for path in changed if not in_store(path)]
    if outside:
        return True, f"{len(outside)} changed file(s) outside the System Design store, e.g. {outside[0]}"
    return False, f"only the System Design store changed ({len(changed)} file(s))"


def test_module_file(test: str, root: pathlib.Path) -> str | None:
    """The file of the module a dotted test name lives in (`tests.test_x.Case.test_y` -> `tests/test_x.py`)."""
    parts = test.split(".")
    for end in range(len(parts), 0, -1):
        candidate = "/".join(parts[:end]) + ".py"
        if (root / candidate).is_file():
            return candidate
    return None


def manifest_files(manifest: str, root: pathlib.Path, cache: dict[str, set[str]] | None = None) -> set[str]:
    """Every file a manifest names: itself, its target, the `file:` of each entry, the module of each test, and every
    repository module those test modules import (a helper they lean on can make a guarded branch redundant)."""
    data = yaml.safe_load((root / manifest).read_text(encoding="utf-8"))
    named = {manifest, data.get("target", "")}
    tests = set()
    for entry in data.get("mutations") or []:
        named.add(entry.get("file", ""))
        tests.add(test_module_file(entry.get("test", ""), root) or "")
    tests.discard("")
    named |= tests
    for test in tests:
        named |= local_dependencies(test, root, cache)
    return {name for name in named if name}


def imported_names(source: str, file: str) -> set[str]:
    """Every module name Python source at repo path `file` imports, relative imports resolved: `from a import b` gives
    both `a` and `a.b`, since `b` may be a submodule."""
    package = file[:-len(".py")].replace("/", ".").rsplit(".", 1)[0] if "/" in file else ""
    names: set[str] = set()
    for node in ast.walk(ast.parse(source, filename=file)):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            origin = node.module or ""
            if node.level:  # `from ..x import y` in a/b/c.py: one dot is a.b, each further dot one package up
                parts = package.split(".") if package else []
                above = parts[:len(parts) - node.level + 1] if node.level <= len(parts) + 1 else []
                origin = ".".join(part for part in (".".join(above), origin) if part)
            if origin:
                names.add(origin)
            names.update(f"{origin}.{alias.name}" if origin else alias.name for alias in node.names)
    return names


def module_files(module: str, root: pathlib.Path) -> set[str]:
    """The repository files importing `module` runs: the module and each package above it. A bare name is also looked
    up in scripts/, which some tests put on sys.path."""
    found = set()
    parts = module.split(".")
    for base in ("", "scripts/"):
        for end in range(1, len(parts) + 1):
            stem = base + "/".join(parts[:end])
            for candidate in (stem + ".py", stem + "/__init__.py"):
                if (root / candidate).is_file():
                    found.add(candidate)
    return found


DYNAMIC_IMPORTS = ("spec_from_file_location", "import_module")
SKIPPED_FOLDERS = frozenset({".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"})


def repository_python_files(root: pathlib.Path) -> list[str]:
    """Every Python file of the repository, outside version control, dependency and build folders."""
    found = []
    for folder, folders, files in os.walk(root):
        folders[:] = [name for name in folders if name not in SKIPPED_FOLDERS]
        found += [(pathlib.Path(folder) / name).relative_to(root).as_posix() for name in files if name.endswith(".py")]
    return found


def dynamic_files(source: str, file: str, root: pathlib.Path, python_files: list[str]) -> set[str]:
    """The repository files a module loads by path (`spec_from_file_location(..., here.with_name("x.py"))`,
    `ROOT / "scripts" / "hooks" / "x.py"`): every file a `.py` string literal of it can name, next to it, from the root,
    in scripts/, or anywhere under that file name. One that names none raises, so the caller runs every manifest."""
    names = {node.value for node in ast.walk(ast.parse(source, filename=file))
             if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.endswith(".py")}
    found = set()
    for name in names:
        base = posixpath.basename(name)
        found |= {candidate for candidate in (posixpath.join(posixpath.dirname(file), name), name, "scripts/" + name)
                  if (root / candidate).is_file()}
        found |= {path for path in python_files if posixpath.basename(path) == base}
    if not found:
        raise ValueError(f"{file} loads a module by a path this script cannot read")
    return found


def local_dependencies(file: str, root: pathlib.Path, cache: dict[str, set[str]] | None = None) -> set[str]:
    """The repository Python files `file` imports, directly or through other repository files, by an import statement
    or by path. A file that cannot be read or parsed raises, so the caller runs every manifest. `cache` keeps the
    answers of one selection."""
    if cache is not None and file in cache:
        return cache[file]
    python_files: list[str] | None = None
    seen: set[str] = set()
    pending = [file]
    while pending:
        current = pending.pop()
        text = (root / current).read_text(encoding="utf-8")
        found = set().union(*(module_files(module, root) for module in imported_names(text, current)))
        if any(call in text for call in DYNAMIC_IMPORTS):
            python_files = repository_python_files(root) if python_files is None else python_files
            found |= dynamic_files(text, current, root, python_files)
        for dependency in found - seen - {file}:
            seen.add(dependency)
            pending.append(dependency)
    if cache is not None:
        cache[file] = seen
    return seen


def imports_module(source: str, file: str, module: str) -> bool:
    """Whether Python source at repo path `file` imports `module` in any form: `import a.b`, `import x, a.b as c`,
    `from a.b import n`, `from a import b`, `from a import (x,\n b)`, or relative (`from .b import n`, `from . import b`)."""
    package = file[:-len(".py")].replace("/", ".").rsplit(".", 1)[0] if "/" in file else ""
    for node in ast.walk(ast.parse(source, filename=file)):
        if isinstance(node, ast.Import):
            if any(alias.name == module or alias.name.startswith(module + ".") for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = package.split(".") if package else []
                base = ".".join(parts[:len(parts) - node.level + 1]) if node.level - 1 <= len(parts) else ""
                origin = ".".join(part for part in (base, node.module or "") if part)
            else:
                origin = node.module or ""
            if origin == module or origin.startswith(module + "."):
                return True
            if any(f"{origin}.{alias.name}" == module for alias in node.names):
                return True
    return False


def imported_by_other_tests(path: str, root: pathlib.Path) -> bool:
    """Whether another test file imports this test module (`from tests.test_render import ...`, in any import form): its
    helpers then decide tests no manifest names it for. A file that cannot be read or parsed counts as importing it."""
    module = path[:-len(".py")].replace("/", ".")
    try:
        for other in (root / "tests").rglob("*.py"):
            name = other.relative_to(root).as_posix()
            if name != path and imports_module(other.read_text(encoding="utf-8"), name, module):
                return True
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError):
        return True
    return False


def shared_test_file(path: str, root: pathlib.Path) -> bool:
    """A file under tests/ that every test may lean on but no manifest names: support code, fixtures, the web checks the
    tests run, and a test module other tests import helpers from."""
    name = posixpath.basename(path)
    if not path.startswith("tests/") or path.startswith("tests/mutations/"):
        return False
    if name.startswith("test_") and name.endswith(".py"):
        return imported_by_other_tests(path, root)
    return True


def selected_manifests(changed: list[str], root: pathlib.Path) -> list[str] | None:
    """The manifests that name a changed file, or None when every manifest has to run: a RUN_ALL file or shared test
    file changed, a changed file is gone (deleted or renamed, so a manifest may still name what is no longer there), or
    the manifests could not be read or name something that is not a file (`target: []`)."""
    if any(path in RUN_ALL or shared_test_file(path, root) for path in changed):
        return None
    if any(not in_store(path) and not (root / path).exists() for path in changed):
        return None
    folder = root / MANIFESTS
    try:
        names = sorted(path.relative_to(root).as_posix() for path in folder.glob("*.yaml"))
        if not names:
            return None
        wanted = set(changed)
        cache: dict[str, set[str]] = {}
        return [name for name in names if manifest_files(name, root, cache) & wanted]
    except (OSError, ValueError, AttributeError, TypeError, SyntaxError, yaml.YAMLError):
        return None


def changed_files(base: str, cwd: pathlib.Path | None = None) -> list[str] | None:
    """Paths that differ between `base` and HEAD, or None when git cannot say."""
    if not base:
        return None
    command = ["git", "diff", "--name-only", "--no-renames", "-z", base, "HEAD"]
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, encoding="utf-8", errors="surrogateescape",
                                check=False, timeout=60)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return [path for path in result.stdout.split("\0") if path]


def main(environ: Mapping[str, str] | None = None, cwd: pathlib.Path | None = None) -> int:
    environ = os.environ if environ is None else environ
    event = environ.get("GITHUB_EVENT_NAME", "")
    changed = changed_files(environ.get("PR_BASE_SHA", ""), cwd) if event == "pull_request" else None
    needed, reason = mutation_needed(event, changed)
    chosen: list[str] | None = None
    if needed and event == "pull_request" and changed:
        chosen = selected_manifests(changed, cwd or ROOT)
        if chosen == []:
            needed, reason = False, f"{reason}, but no mutation manifest names a changed file"
        elif chosen:
            reason = f"{reason}; {len(chosen)} manifest(s) name a changed file: {' '.join(chosen)}"
        else:
            reason = f"{reason}; every manifest runs (a shared file changed, or the manifests could not be read)"
    print(f"ci_changes: the mutation check {'runs' if needed else 'is skipped'}: {reason}")
    output = environ.get("GITHUB_OUTPUT")
    if output:
        try:
            with open(output, "a", encoding="utf-8") as handle:
                handle.write(f"mutation={'true' if needed else 'false'}\n")
                handle.write(f"manifests={' '.join(chosen) if chosen else 'all'}\n")
        except OSError as error:
            print(f"ci_changes: could not write {output}: {error}; the step output stays unset, so the check runs",
                  file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
