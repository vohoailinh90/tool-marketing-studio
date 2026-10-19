#!/usr/bin/env python3
"""Prove that a test actually guards the behavior it names.

A passing test proves nothing on its own. A test that would still pass with the
behavior removed is worse than no test: it reports safety that is not there, and
it teaches the next reader to trust it.

This checks the only thing that settles the question — break the behavior, and
require the test to notice:

    for each mutation:
        run the named test on clean source, require it to PASS
        apply the mutation
        run the named test again, require it to FAIL
        restore the source

The clean-source run catches a test that can never pass — a typo'd class name,
a test deleted from under the manifest — which would otherwise exit non-zero and
be read as "the mutation was caught". It runs once per test in a run (the source
is restored after every mutation, so many entries naming one test share it), so
it proves the test passed this time in this environment; it does not prove the
test is deterministic, and a genuinely flaky test can still produce either
verdict by chance.

With --jobs N the entries run on N copies of the working tree at once (a
mutation rewrites its file in place, so one tree cannot run two). The verdicts
and the exit codes are the same; an entry a worker did not finish is BROKEN,
never "caught".

Per `deterministic_work` in agent-routing/policy.yaml, that loop is computable:
edit a file, run a test, read an exit code. It costs a reviewer three tool calls
per mutation and scales with the number of fixes, so no fixed subagent turn
ceiling can hold it — and a model reading test output can be wrong about whether
a test failed, where a script cannot. It belongs in the repository.

Usage:
    python3 scripts/mutation_check.py tests/mutations/<name>.yaml [tests/mutations/<other>.yaml ...]
    python3 scripts/mutation_check.py --all
    python3 scripts/mutation_check.py --all --jobs 2
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import pathlib
import queue
import shutil
import subprocess
import sys
import tempfile
import threading

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEST_SECONDS = 300  # one run of one named test; a longer one is killed and the entry is not "caught"
# A mutation runs a test, and a test may itself exercise this checker. Without a
# depth guard, mutating a guard that stops that path turns the nesting into an
# unbounded loop — which is what happened the first time this file's own guards
# were mutation-checked.
DEPTH_VAR = "MUTATION_CHECK_DEPTH"
MAX_DEPTH = 2
MANIFEST_DIR = ROOT / "tests" / "mutations"

SURVIVED = "SURVIVED"
CAUGHT = "caught"
BROKEN = "BROKEN"


class ManifestError(RuntimeError):
    """The manifest does not describe a mutation that can be applied."""


def shown(path: pathlib.Path) -> str:
    """Repo-relative where possible; a manifest may legitimately live outside it."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_porcelain(output: str) -> set[str]:
    """Every path named by `git status --porcelain`, including both sides of a rename.

    A rename is reported as `R  old -> new`, so taking `line[3:]` whole yields
    one mangled string matching neither name — which silently defeats the
    dirty-tree guard for exactly the file it was meant to protect. Both sides
    are returned, since a manifest may name either.
    """
    paths: set[str] = set()
    for line in output.splitlines():
        if not line.strip():
            continue
        entry = line[3:].strip()
        # Porcelain quotes a path containing spaces or non-ASCII.
        sides = entry.split(" -> ") if " -> " in entry else [entry]
        paths.update(side.strip().strip('"') for side in sides if side.strip())
    return paths


def dirty_files() -> set[str]:
    """Paths git reports as modified, staged or untracked."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    return parse_porcelain(result.stdout)


def load_manifest(path: pathlib.Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("mutations"), list):
        raise ManifestError(f"{path}: expected a mapping with a 'mutations' list")
    for index, entry in enumerate(data["mutations"]):
        missing = {"label", "find", "replace", "test"} - set(entry or {})
        if missing:
            raise ManifestError(f"{path}: mutation {index} is missing {sorted(missing)}")
    return data


def resolve(entry: dict, manifest: dict) -> pathlib.Path:
    return ROOT / entry.get("file", manifest.get("target", ""))


def mutate(source: str, entry: dict, where: pathlib.Path) -> str:
    """Apply one mutation, refusing anything that does not land exactly once.

    A `find` that matches zero times is a manifest that has drifted from the
    code; one that matches twice mutates an unintended site. Either way the
    result would be reported as a verdict about a change that was never made,
    which is the failure this script exists to prevent.
    """
    occurrences = source.count(entry["find"])
    if occurrences != 1:
        raise ManifestError(
            f"{shown(where)}: {entry['label']!r} matched {occurrences} times, "
            "expected exactly 1 — the manifest has drifted from the source"
        )
    return source.replace(entry["find"], entry["replace"], 1)


def drop_bytecode(source: pathlib.Path) -> None:
    """Delete the cached bytecode of `source`, so the next run compiles the file as it is now.

    Python trusts a cached .pyc whose recorded source mtime (whole seconds) and size equal the file's, so a
    mutation of the same size written in the same second as an earlier compile would run the earlier code.
    """
    for cached in (source.parent / "__pycache__").glob(f"{source.stem}.*.pyc"):
        cached.unlink(missing_ok=True)


def child_environment() -> dict[str, str]:
    """The environment a test subprocess runs in.

    It writes no bytecode, so a mutated file leaves none behind, and it reads none from a configured cache prefix:
    with PYTHONPYCACHEPREFIX set Python loads compiled code from that tree and ignores the sibling __pycache__ that
    drop_bytecode() clears, so a stale entry there would run the unmutated file. Without the prefix it reads the
    sibling cache, which drop_bytecode() has just emptied for the mutated file.
    """
    environment = dict(os.environ)
    environment[DEPTH_VAR] = str(depth() + 1)
    environment.pop("PYTHONPYCACHEPREFIX", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def run_test(target: str) -> bool:
    """True when the test failed, which is what a mutation must cause."""
    result = subprocess.run(
        [sys.executable, "-m", "unittest", target],
        cwd=ROOT, capture_output=True, text=True, check=False, env=child_environment(),
        timeout=TEST_SECONDS,
    )
    return result.returncode != 0


def depth() -> int:
    try:
        return int(os.environ.get(DEPTH_VAR, "0"))
    except ValueError:
        return 0


def inside_repo(path: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(ROOT)
    except ValueError:
        return False
    return True


def check_entry(entry: dict, manifest: dict, baseline: dict[str, bool], allow_outside: bool = False) -> tuple[str, str, str]:
    """Apply one mutation and report whether its named test noticed.

    `baseline` maps a test to whether it failed on clean source. The source is restored after every entry, so
    a test shown to pass (or fail) on it once is not run on it again: many entries name the same test.
    """
    where = resolve(entry, manifest)
    if not allow_outside and not inside_repo(where):
        return BROKEN, entry["label"], f"outside the repository: {shown(where)}"
    if not where.is_file():
        return BROKEN, entry["label"], f"no such file: {shown(where)}"
    if entry["test"] not in baseline:
        drop_bytecode(where)
        baseline[entry["test"]] = run_test(entry["test"])
    if baseline[entry["test"]]:
        # A missing or already-failing test exits non-zero for reasons that
        # have nothing to do with the mutation, and "non-zero" is exactly
        # what this script reads as caught. Without this baseline, a typo in
        # a class name produces a green verdict for a behavior nothing
        # guards — which is the failure the whole script exists to prevent.
        return BROKEN, entry["label"], f"{entry['test']} does not pass on unmutated source (missing, or already failing)"
    original = where.read_text(encoding="utf-8")
    try:
        mutated = mutate(original, entry, where)
    except ManifestError as exc:
        # One drifted entry must not hide the verdicts of the others: report
        # it in place and keep going, then fail the run at the end.
        return BROKEN, entry["label"], str(exc)
    try:
        where.write_text(mutated, encoding="utf-8")
        drop_bytecode(where)
        caught = run_test(entry["test"])
    finally:
        # Restore before anything else can fail: a crash mid-run must never
        # leave a mutated source behind. If the restore write itself fails
        # there is nothing left to try, so name the file unmistakably —
        # an exception whose message does not say which file is corrupted
        # leaves the operator worse off than no message.
        try:
            where.write_text(original, encoding="utf-8")
        except OSError as exc:
            print(f"  !! NOT RESTORED: {shown(where)} is still mutated ({exc}). "
                  "Restore it from git before running anything else.", file=sys.stderr)
            raise
    return (CAUGHT if caught else SURVIVED), entry["label"], entry["test"]


def check(manifest_path: pathlib.Path, allow_outside: bool = False,
          baseline: dict[str, bool] | None = None) -> list[tuple[str, str, str]]:
    """Apply each mutation of a manifest and report whether its named test noticed.

    `allow_outside` exists for this script's own tests, which mutate a scratch
    file in a temporary directory. It is never set from the command line: a
    manifest is repository content, and a `file:` that escapes the repository
    would rewrite paths the dirty-tree guard cannot see, since git reports
    nothing about a file it does not track.

    `baseline` is shared by the manifests of one run, so a test is run on clean source once, not once per entry.
    """
    manifest = load_manifest(manifest_path)
    baseline = {} if baseline is None else baseline
    return [check_entry(entry, manifest, baseline, allow_outside) for entry in manifest["mutations"]]


def manifests(selected: list[str] | None) -> list[pathlib.Path]:
    if selected:
        return list(dict.fromkeys(pathlib.Path(name).resolve() for name in selected))
    return sorted(MANIFEST_DIR.glob("*.yaml"))


# --- parallel mode -----------------------------------------------------------------------------------------
# A mutation rewrites its target in place, so two cannot run in one tree. With --jobs N every worker gets its own
# copy of the working tree and runs a group of entries (all those naming one test, so the group shares one clean
# run) by starting that copy's own scripts/mutation_check.py: ROOT, the bytecode handling and the depth guard are
# the ones a sequential run has. The real tree is only read.

Unit = tuple[str, int]  # a manifest relative to ROOT, and the index of an entry in it


class ParallelError(RuntimeError):
    """The parallel run could not be set up."""


def tree_files() -> list[str]:
    """The files of the working tree a test may need: tracked and untracked, not ignored (uncommitted edits count)."""
    try:
        listing = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                                 cwd=ROOT, capture_output=True, check=False, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ParallelError(f"--jobs needs a git checkout: git could not run ({exc})") from exc
    if listing.returncode != 0:
        raise ParallelError(f"--jobs needs a git checkout: {listing.stderr.decode('utf-8', 'replace').strip()}")
    return [name for name in listing.stdout.decode("utf-8", "surrogateescape").split("\0") if name]


def copy_tree(names: list[str], destination: pathlib.Path) -> None:
    for name in names:
        source = ROOT / name
        target = destination / name
        if source.is_symlink():
            target.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(os.readlink(source), target)
        elif source.is_file():  # a tracked file deleted in the working tree is simply absent from the copy
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def run_group(plan: pathlib.Path, result: pathlib.Path) -> int:
    """Worker side: run the listed (manifest, index) units in this tree, writing the results after every unit."""
    units = json.loads(plan.read_text(encoding="utf-8"))
    loaded: dict[str, dict] = {}
    baseline: dict[str, bool] = {}
    done = []
    for manifest_name, index in units:
        if manifest_name not in loaded:
            loaded[manifest_name] = load_manifest(ROOT / manifest_name)
        manifest = loaded[manifest_name]
        verdict, label, detail = check_entry(manifest["mutations"][index], manifest, baseline)
        done.append({"manifest": manifest_name, "index": index, "verdict": verdict, "label": label, "detail": detail})
        result.write_text(json.dumps(done), encoding="utf-8")  # a crash later keeps what is already known
    return 0


def run_group_in(root: pathlib.Path, group: list[Unit], labels: dict[Unit, str], scratch: pathlib.Path,
                 number: int) -> tuple[dict[Unit, tuple[str, str, str]], bool]:
    """Coordinator side: run one group in the tree copy `root`. A unit with no valid result comes back BROKEN.

    The second value says whether the worker answered every unit and exited cleanly; when it did not, it may have been
    killed in the middle of a mutation, so the copy may still carry one and must not be used again."""
    plan, result = scratch / f"plan-{number}.json", scratch / f"result-{number}.json"
    plan.write_text(json.dumps(group), encoding="utf-8")
    result.unlink(missing_ok=True)
    problem = ""
    try:
        finished = subprocess.run(
            [sys.executable, str(root / "scripts" / "mutation_check.py"), "--run-group", str(plan), "--result", str(result)],
            cwd=root, capture_output=True, text=True, check=False, timeout=TEST_SECONDS * (2 * len(group) + 1))
        if finished.returncode != 0:
            problem = f"worker exited {finished.returncode}: {finished.stderr.strip()[-300:]}"
    except subprocess.TimeoutExpired:
        problem = "worker timed out"
    answers: dict[Unit, tuple[str, str, str]] = {}
    try:
        for item in json.loads(result.read_text(encoding="utf-8")):
            unit = (item["manifest"], item["index"])
            if unit in group and item["verdict"] in (CAUGHT, SURVIVED, BROKEN):
                answers[unit] = (item["verdict"], item["label"], item["detail"])
    except (OSError, ValueError, KeyError, TypeError):
        problem = problem or "worker left no readable result"
    clean = not problem and len(answers) == len(group)
    for unit in group:
        # Fail closed: a worker that died must never turn the entries it did not finish into "caught".
        answers.setdefault(unit, (BROKEN, labels[unit], f"no verdict from the worker ({problem or 'result incomplete'})"))
    return answers, clean


def run_parallel(paths: list[pathlib.Path], jobs: int) -> dict[Unit, tuple[str, str, str]]:
    """Run every entry of `paths` on `jobs` tree copies and return the verdicts by (manifest, index)."""
    by_test: dict[str, list[Unit]] = {}
    labels: dict[Unit, str] = {}
    for path in paths:
        if not inside_repo(path):
            raise ParallelError(f"{shown(path)} is outside the repository; --jobs runs manifests of this repository only")
        name = path.resolve().relative_to(ROOT).as_posix()
        for index, entry in enumerate(load_manifest(path)["mutations"]):
            by_test.setdefault(entry["test"], []).append((name, index))
            labels[(name, index)] = entry["label"]
    groups = sorted(by_test.values(), key=len, reverse=True)  # the big groups first, the small ones fill the gaps
    names = tree_files()
    queue_of_groups: queue.Queue[list[Unit]] = queue.Queue()
    for group in groups:
        queue_of_groups.put(group)
    verdicts: dict[Unit, tuple[str, str, str]] = {}
    lock = threading.Lock()
    stop = threading.Event()  # set when the run is failing: the workers finish the group in hand and take no more
    finished = 0

    def work(root: pathlib.Path, scratch: pathlib.Path, number: int) -> None:
        nonlocal finished
        try:
            while not stop.is_set():
                try:
                    group = queue_of_groups.get_nowait()
                except queue.Empty:
                    return
                answers, clean = run_group_in(root, group, labels, scratch, number)
                with lock:
                    verdicts.update(answers)
                    finished += 1
                    if finished % 25 == 0 or finished == len(groups):
                        print(f"  mutation_check: {finished}/{len(groups)} test groups done", file=sys.stderr, flush=True)
                if not clean:  # a worker killed in the middle of a mutation leaves the file mutated: start from a fresh copy
                    shutil.rmtree(root, ignore_errors=True)
                    copy_tree(names, root)
        except BaseException:
            stop.set()  # a failing worker stops the others at once, whichever future the caller happens to be waiting on
            raise

    workers = max(1, min(jobs, len(groups)))
    # Below RUNNER_TEMP where the Actions runner sets it: the runner empties that folder between jobs, which also
    # covers a run that is killed outright (a pull request run cancelled by a newer push leaves nothing to clean up).
    with tempfile.TemporaryDirectory(prefix="mutation-check-", dir=os.environ.get("RUNNER_TEMP") or None) as scratch_name:
        scratch = pathlib.Path(scratch_name)
        roots = []
        for number in range(workers):
            root = scratch / f"tree-{number}"
            copy_tree(names, root)
            roots.append(root)
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            try:
                for future in [pool.submit(work, root, scratch, number) for number, root in enumerate(roots)]:
                    future.result()
            except BaseException:
                stop.set()
                raise
    return verdicts


def positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", nargs="*", help="manifests to run; omit with --all")
    parser.add_argument("--all", action="store_true", help="run every manifest")
    parser.add_argument(
        "--allow-dirty", action="store_true",
        help="run even with uncommitted changes to the files being mutated",
    )
    parser.add_argument(
        "--jobs", type=positive_int, default=1, metavar="N",
        help="run N entries at once, each worker in its own copy of the working tree (default 1: in this tree)",
    )
    parser.add_argument("--run-group", metavar="PLAN", help=argparse.SUPPRESS)  # the worker side of --jobs
    parser.add_argument("--result", metavar="FILE", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.run_group:
        if not args.result:
            parser.error("--run-group needs --result")
    elif not args.manifest and not args.all:
        parser.error("give a manifest path or --all")

    if depth() >= MAX_DEPTH:
        print(f"  refusing to run at nesting depth {depth()}: a test under mutation "
              "invoked this checker again. Narrow that test's target.")
        return 2

    if args.run_group:
        return run_group(pathlib.Path(args.run_group), pathlib.Path(args.result))

    selected = manifests(args.manifest)
    loaded: dict[pathlib.Path, dict] = {}
    for path in selected:
        try:
            loaded[path] = load_manifest(path)
        except (ManifestError, yaml.YAMLError) as exc:
            print(f"  ERROR  {exc}")
            return 2

    # Before anything is started: the files about to be rewritten (in this tree, or in the copies of it) must be committed.
    dirty = dirty_files()
    for manifest in loaded.values():
        conflicts = {entry.get("file", manifest.get("target", "")) for entry in manifest["mutations"]} & dirty
        if conflicts and not args.allow_dirty:
            print(f"  ERROR  uncommitted changes in {sorted(conflicts)}.")
            print("         This rewrites those files; commit or stash first, "
                  "or pass --allow-dirty if you accept the risk.")
            return 2

    survivors = 0
    broken = 0
    baseline: dict[str, bool] = {}
    verdicts: dict[Unit, tuple[str, str, str]] = {}
    if args.jobs > 1:
        try:
            verdicts = run_parallel(selected, args.jobs)
        except ParallelError as exc:
            print(f"  ERROR  {exc}")
            return 2
    for path in selected:
        manifest = loaded[path]
        print(f"\n{shown(path)}")
        if args.jobs > 1:
            name = path.resolve().relative_to(ROOT).as_posix()
            results = [verdicts[(name, index)] for index in range(len(manifest["mutations"]))]
        else:
            results = check(path, baseline=baseline)
        for verdict, label, detail in results:
            shown_detail = detail if verdict == BROKEN else detail.split(".")[-1][:44]
            print(f"  {verdict:9s} {label:46s} {shown_detail}")
            survivors += verdict == SURVIVED
            broken += verdict == BROKEN

    print()
    if broken:
        print(f"{broken} manifest entry/entries could not be applied — the manifest has "
              "drifted from the source. A verdict was not produced for them.")
        return 2
    if survivors:
        print(f"{survivors} mutation(s) SURVIVED: the named test does not guard the "
              "behavior it claims to. Fix the test, not this script.")
        return 1
    print("Every mutation was caught. No test in these manifests is vacuous.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
