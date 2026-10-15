"""scripts/mutation_check.py: what it does to Python's bytecode cache."""

from __future__ import annotations

import os
import py_compile
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from scripts import mutation_check


class DropBytecodeTests(unittest.TestCase):
    def test_the_cached_bytecode_of_the_mutated_file_is_removed_and_nothing_else(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            cache = folder / "__pycache__"
            cache.mkdir()
            source = folder / "thing.py"
            source.write_text("x = 1\n", encoding="utf-8")
            mine = [cache / "thing.cpython-312.pyc", cache / "thing.cpython-313.pyc"]
            others = [cache / "thing_other.cpython-312.pyc", cache / "other.cpython-312.pyc", folder / "thing.pyc"]
            for path in mine + others:
                path.write_bytes(b"\0")
            mutation_check.drop_bytecode(source)
            self.assertEqual([False, False], [path.exists() for path in mine])
            self.assertEqual([True, True, True], [path.exists() for path in others])
            self.assertTrue(source.exists())

    def test_a_file_that_was_never_compiled_is_fine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "thing.py"
            source.write_text("x = 1\n", encoding="utf-8")
            mutation_check.drop_bytecode(source)
            self.assertTrue(source.exists())

    def test_a_stale_cache_of_the_same_size_and_second_no_longer_hides_a_mutation(self) -> None:
        """A cached .pyc that matches the file's recorded mtime and size is trusted; after drop_bytecode it is gone."""
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / "thing.py"
            source.write_text("VALUE = 'clean'\n", encoding="utf-8")
            py_compile.compile(str(source), doraise=True)
            source.write_text("VALUE = 'MUTAT'\n", encoding="utf-8")  # same size
            cached = next((folder / "__pycache__").glob("thing.*.pyc"))
            # make the file look as it did when the cache was written: same whole-second mtime
            recorded = int.from_bytes(cached.read_bytes()[8:12], "little")
            os.utime(source, (recorded, recorded))
            read = [sys.executable, "-c", "import thing; print(thing.VALUE)"]
            stale = subprocess.run(read, cwd=folder, capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual("clean", stale, "the premise: Python trusts the cache")
            mutation_check.drop_bytecode(source)
            fresh = subprocess.run(read, cwd=folder, capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual("MUTAT", fresh)

    def test_a_stale_cache_under_a_configured_prefix_no_longer_hides_a_mutation(self) -> None:
        """With PYTHONPYCACHEPREFIX set Python ignores the sibling __pycache__, so the test run must not use the prefix."""
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "src"
            prefix = Path(tmp) / "cache"
            folder.mkdir()
            prefix.mkdir()
            source = folder / "thing.py"
            source.write_text("VALUE = 'clean'\n", encoding="utf-8")
            read = [sys.executable, "-c", "import thing; print(thing.VALUE)"]
            configured = {**os.environ, "PYTHONPYCACHEPREFIX": str(prefix)}
            configured.pop("PYTHONDONTWRITEBYTECODE", None)
            subprocess.run(read, cwd=folder, env=configured, capture_output=True, text=True, check=True)
            cached = next(prefix.rglob("thing.*.pyc"))
            source.write_text("VALUE = 'MUTAT'\n", encoding="utf-8")  # same size
            recorded = int.from_bytes(cached.read_bytes()[8:12], "little")
            os.utime(source, (recorded, recorded))
            mutation_check.drop_bytecode(source)  # clears the sibling __pycache__ only
            stale = subprocess.run(read, cwd=folder, env=configured, capture_output=True, text=True, check=True)
            self.assertEqual("clean", stale.stdout.strip(), "the premise: the prefix cache is trusted and drop_bytecode misses it")
            with mock.patch.dict(os.environ, {"PYTHONPYCACHEPREFIX": str(prefix)}):
                environment = mutation_check.child_environment()
            fresh = subprocess.run(read, cwd=folder, env=environment, capture_output=True, text=True, check=True)
            self.assertEqual("MUTAT", fresh.stdout.strip())

    def test_the_test_subprocess_writes_no_bytecode_and_is_one_level_deeper(self) -> None:
        with mock.patch.dict(os.environ, {"PYTHONPYCACHEPREFIX": "/somewhere", mutation_check.DEPTH_VAR: "2"}):
            environment = mutation_check.child_environment()
        self.assertEqual("1", environment["PYTHONDONTWRITEBYTECODE"])
        self.assertEqual("3", environment[mutation_check.DEPTH_VAR])
        self.assertNotIn("PYTHONPYCACHEPREFIX", environment)

    def test_run_test_runs_the_child_environment(self) -> None:
        sentinel = {"SENTINEL": "1"}
        with mock.patch.object(mutation_check, "child_environment", return_value=sentinel), \
                mock.patch.object(mutation_check.subprocess, "run") as run:
            run.return_value.returncode = 1
            self.assertTrue(mutation_check.run_test("tests.x.Case.test"))
        self.assertIs(sentinel, run.call_args.kwargs["env"])

    def test_the_cache_is_dropped_before_the_clean_run_and_again_before_the_mutated_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "thing.py"
            target.write_text("X = 1\n", encoding="utf-8")
            manifest = Path(tmp) / "manifest.yaml"
            manifest.write_text(yaml.safe_dump({"target": str(target), "mutations": [
                {"label": "x", "find": "X = 1", "replace": "X = 2", "test": "scratch.Case.test"}]}), encoding="utf-8")
            calls: list[tuple[str, str]] = []
            outcomes = iter([False, True])  # the clean run passes, the mutated run fails

            def run_test(_target: str) -> bool:
                calls.append(("run", target.read_text(encoding="utf-8")))
                return next(outcomes)

            with mock.patch.object(mutation_check, "drop_bytecode", lambda path: calls.append(("drop", path.read_text(encoding="utf-8")))), \
                    mock.patch.object(mutation_check, "run_test", run_test):
                results = mutation_check.check(manifest, allow_outside=True)
            self.assertEqual([("drop", "X = 1\n"), ("run", "X = 1\n"), ("drop", "X = 2\n"), ("run", "X = 2\n")], calls)
            self.assertEqual("caught", results[0][0])
            self.assertEqual("X = 1\n", target.read_text(encoding="utf-8"), "the source is restored")


if __name__ == "__main__":
    unittest.main()
