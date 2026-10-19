"""scripts/mutation_check.py: what it does to Python's bytecode cache."""

from __future__ import annotations

import contextlib
import io
import json
import os
import py_compile
import subprocess
import sys
import tempfile
import textwrap
import time
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


def write_manifest(path: Path, target: str, entries: list[tuple[str, str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"target": target, "mutations": [
        {"label": f"entry {index}", "find": find, "replace": replace, "test": test}
        for index, (find, replace, test) in enumerate(entries)]}), encoding="utf-8")


class BaselineTests(unittest.TestCase):
    """A test is run on clean source once per run: the source is restored after every entry, so entries share it."""

    def scratch(self, tmp: str, tests: list[str]) -> Path:
        target = Path(tmp) / "thing.py"
        target.write_text("A = 1\nB = 2\nC = 3\n", encoding="utf-8")
        manifest = Path(tmp) / "manifest.yaml"
        write_manifest(manifest, str(target), [(f"{name} = ", f"{name} = 9 + ", test) for name, test in zip("ABC", tests)])
        return manifest

    def run_check(self, tests: list[str], outcomes: list[bool], baseline: dict | None = None) -> tuple[list, list[str]]:
        calls: list[str] = []
        queued = iter(outcomes)

        def run_test(name: str) -> bool:
            calls.append(name)
            return next(queued)

        with tempfile.TemporaryDirectory() as tmp:
            manifest = self.scratch(tmp, tests)
            with mock.patch.object(mutation_check, "run_test", run_test), mock.patch.object(mutation_check, "drop_bytecode"):
                results = mutation_check.check(manifest, allow_outside=True, baseline=baseline)
            self.assertEqual("A = 1\nB = 2\nC = 3\n", (Path(tmp) / "thing.py").read_text(encoding="utf-8"), "the source is restored")
        return results, calls

    def test_a_test_named_by_several_entries_is_run_on_clean_source_once(self) -> None:
        results, calls = self.run_check(["t.X.one"] * 3, [False, True, True, True])  # clean pass, then three mutated runs fail
        self.assertEqual(["caught"] * 3, [verdict for verdict, _, _ in results])
        self.assertEqual(4, len(calls), "one clean run and three mutated runs, not six runs")

    def test_each_different_test_gets_its_own_clean_run(self) -> None:
        results, calls = self.run_check(["t.X.one", "t.X.two", "t.X.one"], [False, True, False, True, True])
        self.assertEqual(["caught"] * 3, [verdict for verdict, _, _ in results])
        self.assertEqual(["t.X.one", "t.X.one", "t.X.two", "t.X.two", "t.X.one"], calls)

    def test_a_test_that_fails_on_clean_source_is_broken_for_every_entry_and_is_not_run_again(self) -> None:
        results, calls = self.run_check(["t.X.one"] * 3, [True])
        self.assertEqual(["BROKEN"] * 3, [verdict for verdict, _, _ in results])
        self.assertTrue(all("does not pass on unmutated source" in detail for _, _, detail in results))
        self.assertEqual(["t.X.one"], calls)

    def test_manifests_of_one_run_share_the_clean_runs(self) -> None:
        shared: dict[str, bool] = {}
        self.run_check(["t.X.one"] * 3, [False, True, True, True], baseline=shared)
        _, calls = self.run_check(["t.X.one"] * 3, [True, True, True], baseline=shared)
        self.assertEqual(3, len(calls), "the second manifest runs only its mutated runs")


THING = "VALUE = 1\nOTHER = 2\n\n\ndef flag():\n    return True\n"
TESTS = textwrap.dedent("""\
    import os
    import pathlib
    import time
    import unittest

    import thing


    class Good(unittest.TestCase):
        def test_value(self):
            self.assertEqual(1, thing.VALUE)

        def test_flag(self):
            self.assertTrue(thing.flag())


    class Vacuous(unittest.TestCase):
        def test_nothing(self):
            self.assertTrue(True)


    class Counted(unittest.TestCase):
        def test_counted(self):
            with open(os.environ["COUNT_FILE"], "a", encoding="utf-8") as handle:
                handle.write("run\\n")
            self.assertEqual((1, 2, True), (thing.VALUE, thing.OTHER, thing.flag()))


    class Slow(unittest.TestCase):
        def test_slow(self):
            time.sleep(0.5)
            self.assertEqual(1, thing.VALUE)


    class Tripwire(unittest.TestCase):
        def test_not_in_the_real_tree(self):
            self.assertNotEqual(pathlib.Path(os.environ["REAL_TREE"]).resolve(), pathlib.Path.cwd().resolve())
""")
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@example.com", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}


class ParallelTests(unittest.TestCase):
    """--jobs N: the same verdicts as a sequential run, from copies of the working tree, failing closed."""

    def setUp(self) -> None:
        patcher = mock.patch.dict(os.environ, {**GIT_ENV, "MUTATION_CHECK_DEPTH": "0"})
        patcher.start()
        self.addCleanup(patcher.stop)
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        # the system temporary directory is pointed at a folder of ours, so a leftover tree copy is visible
        self.scratch_root = self.tmp / "scratch"
        self.scratch_root.mkdir()
        patcher = mock.patch.object(tempfile, "tempdir", str(self.scratch_root))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.counter = self.tmp / "count.txt"
        patcher = mock.patch.dict(os.environ, {"COUNT_FILE": str(self.counter)})
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("RUNNER_TEMP", None)  # set on a CI runner; restored by the patcher above

    def repo(self, name: str = "repo", script: str | None = None, init_git: bool = True) -> Path:
        repo = self.tmp / name
        (repo / "scripts").mkdir(parents=True)
        (repo / "tests").mkdir()
        (repo / "scripts" / "mutation_check.py").write_text(
            script if script is not None else Path(mutation_check.__file__).read_text(encoding="utf-8"), encoding="utf-8")
        (repo / "thing.py").write_text(THING, encoding="utf-8")
        (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
        (repo / "tests" / "test_thing.py").write_text(TESTS, encoding="utf-8")
        self.manifest(repo, "m.yaml", [
            ("VALUE = 1", "VALUE = 7", "tests.test_thing.Good.test_value"),
            ("return True", "return False", "tests.test_thing.Good.test_flag"),
            ("VALUE = 1", "VALUE = 0", "tests.test_thing.Good.test_value"),
            ("return True", "return None", "tests.test_thing.Good.test_flag"),
            ("OTHER = 2", "OTHER = 3", "tests.test_thing.Vacuous.test_nothing"),
            ("VALUE = 1", "VALUE = 9", "tests.test_thing.Counted.test_counted"),
            ("OTHER = 2", "OTHER = 8", "tests.test_thing.Counted.test_counted"),
            ("return True", "return False", "tests.test_thing.Counted.test_counted"),
            ("VALUE = 1", "VALUE = 5", "tests.test_thing.Slow.test_slow"),
            ("NOT IN THE FILE", "x", "tests.test_thing.Good.test_value"),
            ("OTHER = 2", "OTHER = 4", "tests.test_thing.Nope.test_missing"),
        ])
        if init_git:
            for command in (["init", "--quiet", "-b", "main"], ["add", "-A"], ["commit", "--quiet", "-m", "scratch"]):
                subprocess.run(["git", *command], cwd=repo, check=True, capture_output=True)
        return repo

    def manifest(self, repo: Path, name: str, entries: list[tuple[str, str, str]]) -> None:
        write_manifest(repo / "tests" / "mutations" / name, "thing.py", entries)

    def path(self, repo: Path, name: str) -> str:
        return str(repo / "tests" / "mutations" / name)

    def main(self, repo: Path, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(mutation_check, "ROOT", repo.resolve()), \
                mock.patch.object(mutation_check, "MANIFEST_DIR", repo.resolve() / "tests" / "mutations"), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = mutation_check.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_a_parallel_run_prints_what_a_sequential_run_prints_and_exits_the_same(self) -> None:
        repo = self.repo()
        sequential = self.main(repo, self.path(repo, "m.yaml"))
        for jobs in ("2", "3"):
            with self.subTest(jobs=jobs):
                parallel = self.main(repo, self.path(repo, "m.yaml"), "--jobs", jobs)
                self.assertEqual(sequential[:2], parallel[:2])
        verdicts = [line.split()[0] for line in sequential[1].splitlines() if line.startswith("  ")]
        self.assertEqual(["caught", "caught", "caught", "caught", "SURVIVED", "caught", "caught", "caught", "caught", "BROKEN", "BROKEN"], verdicts)
        self.assertEqual(2, sequential[0], "a broken entry fails the run")

    def test_the_exit_code_of_a_parallel_run_is_the_sequential_one(self) -> None:
        repo = self.repo()
        self.manifest(repo, "clean.yaml", [("VALUE = 1", "VALUE = 7", "tests.test_thing.Good.test_value")])
        self.manifest(repo, "survives.yaml", [("OTHER = 2", "OTHER = 3", "tests.test_thing.Vacuous.test_nothing")])
        for name, expected in (("clean.yaml", 0), ("survives.yaml", 1)):
            for jobs in ("1", "2"):
                with self.subTest(manifest=name, jobs=jobs):
                    self.assertEqual(expected, self.main(repo, self.path(repo, name), "--jobs", jobs)[0])

    def test_entries_are_printed_in_manifest_order_whichever_finishes_first(self) -> None:
        repo = self.repo()
        self.manifest(repo, "order.yaml", [
            ("VALUE = 1", "VALUE = 5", "tests.test_thing.Slow.test_slow"),
            ("VALUE = 1", "VALUE = 7", "tests.test_thing.Good.test_value"),
            ("OTHER = 2", "OTHER = 3", "tests.test_thing.Vacuous.test_nothing"),
            ("VALUE = 1", "VALUE = 0", "tests.test_thing.Good.test_value"),
            ("VALUE = 1", "VALUE = 6", "tests.test_thing.Slow.test_slow"),
        ])
        labels = lambda text: [line.split()[2] for line in text.splitlines() if line.startswith("  ")]  # "entry N"
        code, out, _ = self.main(repo, self.path(repo, "order.yaml"), "--jobs", "2")
        self.assertEqual(["0", "1", "2", "3", "4"], labels(out))
        self.assertEqual(1, code)

    def test_a_test_named_by_several_entries_is_run_clean_once_in_either_mode(self) -> None:
        repo = self.repo()
        (repo / "tests" / "mutations" / "m.yaml").unlink()
        self.manifest(repo, "counted.yaml", [
            ("VALUE = 1", "VALUE = 9", "tests.test_thing.Counted.test_counted"),
            ("OTHER = 2", "OTHER = 8", "tests.test_thing.Counted.test_counted"),
        ])
        self.manifest(repo, "counted_too.yaml", [
            ("return True", "return False", "tests.test_thing.Counted.test_counted"),
            ("VALUE = 1", "VALUE = 6", "tests.test_thing.Counted.test_counted"),
        ])
        for jobs in ("1", "2"):
            with self.subTest(jobs=jobs):
                self.counter.unlink(missing_ok=True)
                self.assertEqual(0, self.main(repo, "--all", "--jobs", jobs)[0])
                self.assertEqual(5, len(self.counter.read_text(encoding="utf-8").splitlines()),
                                 "one clean run for the two manifests, then the four mutated runs")

    def test_the_real_tree_is_not_touched_and_the_workers_never_run_in_it(self) -> None:
        repo = self.repo()
        self.manifest(repo, "tripwire.yaml", [("OTHER = 2", "OTHER = 4", "tests.test_thing.Tripwire.test_not_in_the_real_tree")])
        with mock.patch.dict(os.environ, {"REAL_TREE": str(repo.resolve())}), \
                mock.patch.object(mutation_check, "check_entry", side_effect=AssertionError("the coordinator ran an entry itself")):
            code, out, _ = self.main(repo, self.path(repo, "tripwire.yaml"), "--jobs", "2")
        self.assertEqual((1, True), (code, "SURVIVED" in out), out)  # the test passes in the copy, which is the point
        self.assertEqual(THING, (repo / "thing.py").read_text(encoding="utf-8"))
        tracked = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo, capture_output=True, text=True)
        self.assertEqual("", tracked.stdout, "no tracked file of the real tree changed")

    def test_the_tree_copies_are_removed_when_the_run_ends(self) -> None:
        repo = self.repo()
        self.main(repo, self.path(repo, "m.yaml"), "--jobs", "2")
        self.assertEqual([], list(self.scratch_root.iterdir()))

    STUBS = {
        "a worker that dies": "raise SystemExit(3)\n",
        "a worker that writes nothing readable": textwrap.dedent("""\
            import sys
            open(sys.argv[sys.argv.index("--result") + 1], "w").write("not json")
            raise SystemExit(0)
            """),
        "a worker that reports a verdict it cannot have": textwrap.dedent("""\
            import json, sys
            plan = json.load(open(sys.argv[sys.argv.index("--run-group") + 1]))
            rows = [{"manifest": m, "index": i, "verdict": "great", "label": "x", "detail": "t"} for m, i in plan]
            json.dump(rows, open(sys.argv[sys.argv.index("--result") + 1], "w"))
            raise SystemExit(0)
            """),
        "a worker that dies after its first unit": textwrap.dedent("""\
            import json, sys
            plan = json.load(open(sys.argv[sys.argv.index("--run-group") + 1]))
            manifest, index = plan[0]
            row = {"manifest": manifest, "index": index, "verdict": "caught", "label": "x", "detail": "t"}
            json.dump([row], open(sys.argv[sys.argv.index("--result") + 1], "w"))
            raise SystemExit(1)
            """),
    }

    def test_an_entry_the_worker_did_not_finish_is_broken_never_caught(self) -> None:
        for number, (name, stub) in enumerate(self.STUBS.items()):
            with self.subTest(worker=name):
                repo = self.repo(f"stub-{number}", script=stub)
                self.manifest(repo, "pairs.yaml", [
                    ("VALUE = 1", "VALUE = 7", "tests.test_thing.Good.test_value"),
                    ("return True", "return False", "tests.test_thing.Good.test_flag"),
                    ("VALUE = 1", "VALUE = 0", "tests.test_thing.Good.test_value"),
                    ("return True", "return None", "tests.test_thing.Good.test_flag"),
                ])
                code, out, _ = self.main(repo, self.path(repo, "pairs.yaml"), "--jobs", "2")
                verdicts = [line.split()[0] for line in out.splitlines() if line.startswith("  ")]
                self.assertEqual(2, code, out)
                self.assertEqual(4, len(verdicts))
                if "after its first unit" in name:
                    self.assertEqual(["caught", "caught", "BROKEN", "BROKEN"], verdicts)  # each group's first unit survived the crash
                else:
                    self.assertEqual(["BROKEN"] * 4, verdicts)
                self.assertEqual([], list(self.scratch_root.iterdir()), "the copies are removed after a failure too")

    def worker_root(self, script: str) -> Path:
        root = self.tmp / "worker-root"
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "mutation_check.py").write_text(script, encoding="utf-8")
        return root

    ROWS = textwrap.dedent("""\
        import json, sys
        rows = [{"manifest": "m.yaml", "index": i, "verdict": "caught", "label": "x", "detail": "t"} for i in %s]
        json.dump(rows, open(sys.argv[sys.argv.index("--result") + 1], "w"))
        """)

    def test_a_row_for_a_unit_outside_the_group_is_not_taken_from_the_worker(self) -> None:
        group = [("m.yaml", 0), ("m.yaml", 1)]
        labels = {unit: f"entry {unit[1]}" for unit in group}
        scratch = self.tmp / "scratch-rows"
        scratch.mkdir()
        answers, clean = mutation_check.run_group_in(self.worker_root(self.ROWS % "(0, 5)"), group, labels, scratch, 0)
        self.assertEqual({("m.yaml", 0), ("m.yaml", 1)}, set(answers), "the foreign unit 5 is not an answer")
        self.assertEqual("caught", answers[("m.yaml", 0)][0])
        self.assertEqual("BROKEN", answers[("m.yaml", 1)][0], "the unit the worker skipped")
        self.assertFalse(clean)

    def test_a_result_left_by_an_earlier_group_is_not_read_for_the_next_one(self) -> None:
        group = [("m.yaml", 0), ("m.yaml", 1)]
        labels = {unit: f"entry {unit[1]}" for unit in group}
        scratch = self.tmp / "scratch-stale"
        scratch.mkdir()
        answers, clean = mutation_check.run_group_in(self.worker_root(self.ROWS % "(0, 1)"), group, labels, scratch, 0)
        self.assertEqual(["caught", "caught"], [answers[unit][0] for unit in group])
        self.assertTrue(clean)
        # the next group of the same worker slot: its worker exits 0 and writes nothing
        answers, clean = mutation_check.run_group_in(self.worker_root("raise SystemExit(0)\n"), group, labels, scratch, 0)
        self.assertEqual(["BROKEN", "BROKEN"], [answers[unit][0] for unit in group], "the file of the first group is gone")
        self.assertFalse(clean)

    def test_the_tree_copies_go_below_runner_temp_when_the_runner_sets_it(self) -> None:
        repo = self.repo()
        runner_temp = self.tmp / "runner-temp"
        runner_temp.mkdir()
        self.manifest(repo, "one.yaml", [("VALUE = 1", "VALUE = 7", "tests.test_thing.Good.test_value")])
        seen: list[Path] = []
        real = mutation_check.copy_tree

        def spy(names: list[str], destination: Path) -> None:
            seen.append(destination)
            real(names, destination)

        with mock.patch.dict(os.environ, {"RUNNER_TEMP": str(runner_temp)}), mock.patch.object(mutation_check, "copy_tree", spy):
            self.assertEqual(0, self.main(repo, self.path(repo, "one.yaml"), "--jobs", "2")[0])
        self.assertTrue(seen and all(runner_temp in path.parents for path in seen), seen)
        self.assertEqual([], list(runner_temp.iterdir()), "and they are removed again")

    def run_with_fake_groups(self, repo: Path, fake) -> None:
        self.manifest(repo, "many.yaml", [("VALUE = 1", f"VALUE = {n}", f"tests.test_thing.Good.test_{n}") for n in range(8)])
        self.main(repo, self.path(repo, "many.yaml"), "--jobs", "2")

    def test_a_worker_that_fails_stops_the_others_from_taking_new_groups(self) -> None:
        for failing in (0, 1):  # the caller waits for worker 0 first, so a failure of worker 1 must not wait behind it
            with self.subTest(failing_worker=failing):
                repo = self.repo(f"failing-{failing}")
                calls: list[int] = []

                def fake(root: Path, group: list, labels: dict, scratch: Path, number: int):
                    calls.append(number)
                    if number == failing:
                        raise RuntimeError("a worker fails")
                    time.sleep(0.3)
                    return {unit: ("caught", labels[unit], "t") for unit in group}, True

                with mock.patch.object(mutation_check, "run_group_in", fake), self.assertRaises(RuntimeError):
                    self.run_with_fake_groups(repo, fake)
                self.assertLessEqual(len(calls), 4, f"the other worker went on through the queue: {calls}")

    def test_an_interrupt_of_the_caller_stops_the_workers_from_taking_new_groups(self) -> None:
        repo = self.repo()
        calls: list[int] = []

        def fake(root: Path, group: list, labels: dict, scratch: Path, number: int):
            calls.append(number)
            time.sleep(0.3)
            return {unit: ("caught", labels[unit], "t") for unit in group}, True

        with mock.patch.object(mutation_check, "run_group_in", fake), \
                mock.patch.object(mutation_check.concurrent.futures.Future, "result", side_effect=KeyboardInterrupt), \
                self.assertRaises(KeyboardInterrupt):
            self.run_with_fake_groups(repo, fake)
        self.assertLessEqual(len(calls), 4, f"the workers went on through the queue: {calls}")
        self.assertEqual([], list(self.scratch_root.iterdir()), "and the copies are removed")

    def test_the_copy_of_a_worker_that_did_not_end_cleanly_is_made_again(self) -> None:
        repo = self.repo(script=self.STUBS["a worker that dies"])
        self.manifest(repo, "pairs.yaml", [
            ("VALUE = 1", "VALUE = 7", "tests.test_thing.Good.test_value"),
            ("return True", "return False", "tests.test_thing.Good.test_flag"),
        ])
        made: list[Path] = []
        real = mutation_check.copy_tree

        def spy(names: list[str], destination: Path) -> None:
            made.append(destination)
            real(names, destination)

        with mock.patch.object(mutation_check, "copy_tree", spy):
            code = self.main(repo, self.path(repo, "pairs.yaml"), "--jobs", "2")[0]
        self.assertEqual(2, code)
        self.assertEqual(4, len(made), "two copies at the start, and one more for each of the two groups that failed")

    def test_jobs_needs_a_git_checkout(self) -> None:
        repo = self.repo("plain", init_git=False)
        code, out, _ = self.main(repo, self.path(repo, "m.yaml"), "--jobs", "2")
        self.assertEqual(2, code)
        self.assertIn("needs a git checkout", out)

    def test_a_manifest_outside_the_repository_is_refused_with_jobs(self) -> None:
        repo = self.repo()
        outside = self.tmp / "outside.yaml"
        write_manifest(outside, "thing.py", [("VALUE = 1", "VALUE = 7", "tests.test_thing.Good.test_value")])
        code, out, _ = self.main(repo, str(outside), "--jobs", "2")
        self.assertEqual(2, code)
        self.assertIn("outside the repository", out)

    def test_an_uncommitted_target_is_refused_before_any_worker_starts(self) -> None:
        repo = self.repo()
        (repo / "thing.py").write_text(THING + "# edited\n", encoding="utf-8")
        for jobs in ("1", "2"):
            with self.subTest(jobs=jobs), mock.patch.object(mutation_check, "copy_tree", side_effect=AssertionError("started")), \
                    mock.patch.object(mutation_check, "check_entry", side_effect=AssertionError("started")):
                code, out, _ = self.main(repo, self.path(repo, "m.yaml"), "--jobs", jobs)
                self.assertEqual(2, code)
                self.assertIn("uncommitted changes in ['thing.py']", out)
        code, out, _ = self.main(repo, self.path(repo, "m.yaml"), "--jobs", "2", "--allow-dirty")
        self.assertEqual((2, 11), (code, len([line for line in out.splitlines() if line.startswith("  ")])), "--allow-dirty runs it")

    def test_jobs_must_be_a_positive_number(self) -> None:
        for bad in ("0", "-1", "two"):
            with self.subTest(jobs=bad), contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()), \
                    mock.patch.object(mutation_check, "manifests", return_value=[]), self.assertRaises(SystemExit) as stopped:
                mutation_check.main(["--all", "--jobs", bad])
            self.assertEqual(2, stopped.exception.code)


if __name__ == "__main__":
    unittest.main()


class ManifestSelectionTests(unittest.TestCase):
    """CI passes the manifests a pull request touches (scripts/ci_changes.py); every one of them must run, each once."""

    def test_every_manifest_named_is_run_once_in_the_order_given(self) -> None:
        names = ["tests/mutations/ci_changes.yaml", "tests/mutations/sd101_claims.yaml", "tests/mutations/ci_changes.yaml"]
        self.assertEqual([mutation_check.ROOT / names[0], mutation_check.ROOT / names[1]],
                         mutation_check.manifests([str(mutation_check.ROOT / name) for name in names]))

    def test_no_manifest_named_means_every_manifest(self) -> None:
        self.assertEqual(sorted(mutation_check.MANIFEST_DIR.glob("*.yaml")), mutation_check.manifests([]))

    def test_the_command_line_takes_several_manifests(self) -> None:
        checked: list[Path] = []
        with mock.patch.object(mutation_check, "check", lambda path, **_: checked.append(path) or []), \
                mock.patch.object(mutation_check, "dirty_files", return_value=set()), contextlib.redirect_stdout(io.StringIO()):
            code = mutation_check.main([str(mutation_check.ROOT / "tests/mutations/ci_changes.yaml"),
                                        str(mutation_check.ROOT / "tests/mutations/sd101_claims.yaml")])
        self.assertEqual(0, code)
        self.assertEqual(["ci_changes.yaml", "sd101_claims.yaml"], [path.name for path in checked])
