#!/usr/bin/env python3
"""Decide whether the CI mutation check has to run for this change.

`scripts/mutation_check.py --all` is about 27 of the 30 minutes of the engine job. It proves that the
safety-rail tests notice their own removal, which only a change to code, tests or CI can break. A pull
request that touches nothing but the System Design store (lessons, figures, metadata, progress files and
its source map) cannot, so it skips the step. Every push to main, and every pull request that touches
anything else, runs it. A change this script cannot read is treated as one that needs the check.

In CI it reads GITHUB_EVENT_NAME and PR_BASE_SHA, prints the decision with its reason, and appends
`mutation=true` or `mutation=false` to GITHUB_OUTPUT. It never fails the job on its own account.
"""

from __future__ import annotations

import os
import pathlib
import posixpath
import subprocess
import sys
from collections.abc import Mapping

# Only content of the System Design store: the lessons and the source map the checker reads.
STORE_PREFIXES = ("system-design-101/", "brainstorm/system-design-101-vi/")


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
    print(f"ci_changes: the mutation check {'runs' if needed else 'is skipped'}: {reason}")
    output = environ.get("GITHUB_OUTPUT")
    if output:
        try:
            with open(output, "a", encoding="utf-8") as handle:
                handle.write(f"mutation={'true' if needed else 'false'}\n")
        except OSError as error:
            print(f"ci_changes: could not write {output}: {error}; the step output stays unset, so the check runs",
                  file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
