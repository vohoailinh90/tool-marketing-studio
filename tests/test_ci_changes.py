"""scripts/ci_changes.py: which pull requests skip the CI mutation check, and how the workflow uses it."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from mkt.model import ROOT
from scripts import ci_changes

STORE = "system-design-101/vi/lessons/sd-01-009/lesson.md"
SOURCE_MAP = "brainstorm/system-design-101-vi/source-map.json"


class MutationNeededTests(unittest.TestCase):
    def test_a_push_always_runs_the_check(self):
        for event in ("push", "workflow_dispatch", ""):
            needed, _ = ci_changes.mutation_needed(event, [STORE])
            self.assertTrue(needed, event)

    def test_a_pull_request_that_changes_only_the_store_skips_it(self):
        needed, reason = ci_changes.mutation_needed("pull_request", [STORE, SOURCE_MAP, "system-design-101/vi/progress.json"])
        self.assertFalse(needed)
        self.assertIn("3 file(s)", reason)

    def test_a_pull_request_that_touches_code_tests_or_ci_runs_it(self):
        for path in ("scripts/sd101_check.py", "tests/test_sd101_check.py", ".github/workflows/ci.yml", "mkt/check.py",
                     "requirements.txt", "tests/mutations/sd101_check.yaml", "docs/agent-team.md", "README.md"):
            needed, reason = ci_changes.mutation_needed("pull_request", [STORE, path])
            self.assertTrue(needed, path)
            self.assertIn(path, reason)

    def test_other_content_directories_are_not_the_store(self):
        for path in ("campaigns/a/posts/vi/1.yaml", "brainstorm/other.md", "brainstorm/system-design-101-vi-extra/x.md",
                     "system-design-101-extra/x.md", "system-design-101", "tools/a/brief.yaml"):
            needed, _ = ci_changes.mutation_needed("pull_request", [path])
            self.assertTrue(needed, path)

    def test_a_path_that_climbs_out_of_the_store_is_not_in_it(self):
        for path in ("system-design-101/../scripts/x.py", "system-design-101//vi/x.md", "system-design-101/./x.md"):
            needed, _ = ci_changes.mutation_needed("pull_request", [path])
            self.assertTrue(needed, path)

    def test_a_change_that_cannot_be_read_runs_the_check(self):
        for changed in (None, []):
            needed, reason = ci_changes.mutation_needed("pull_request", changed)
            self.assertTrue(needed, changed)
            self.assertIn("could not be read", reason)


MANIFEST = """target: {target}
mutations:
- label: x
  find: 'x'
  replace: 'y'
  test: tests.test_tool.ToolTests.test_x
"""


class SelectedManifestsTests(unittest.TestCase):
    def test_the_real_manifests_are_chosen_by_target_entry_file_test_module_and_themselves(self):
        cases = {"scripts/ci_changes.py": "tests/mutations/ci_changes.yaml",
                 "tests/test_ci_changes.py": "tests/mutations/ci_changes.yaml",
                 "tests/mutations/sd101_claims.yaml": "tests/mutations/sd101_claims.yaml",
                 "docs/sd101-slides-handoff.md": "tests/mutations/sd101_handoff_doc.yaml"}
        for changed, manifest in cases.items():
            with self.subTest(changed):
                self.assertIn(manifest, ci_changes.selected_manifests([changed], ROOT))

    def test_a_manifest_is_chosen_by_the_file_one_of_its_entries_mutates(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            write(folder, "tests/mutations/tool.yaml", MANIFEST.format(target="scripts/tool.py")
                  + "- label: y\n  file: docs/tool.md\n  find: 'a'\n  replace: 'b'\n  test: tests.test_tool.ToolTests.test_y\n")
            write(folder, "docs/tool.md", "a\n")
            write(folder, "docs/other.md", "a\n")
            self.assertEqual(["tests/mutations/tool.yaml"], ci_changes.selected_manifests(["docs/tool.md"], folder))
            self.assertEqual([], ci_changes.selected_manifests(["docs/other.md"], folder))

    def test_an_unrelated_change_chooses_no_manifest(self):
        self.assertEqual([], ci_changes.selected_manifests(["docs/facebook-page.md"], ROOT))

    def test_a_shared_file_runs_every_manifest(self):
        for path in ("scripts/mutation_check.py", ".github/workflows/ci.yml", "requirements-dev.txt", "requirements.txt"):
            with self.subTest(path):
                self.assertTrue((ROOT / path).is_file(), "a present file, so only RUN_ALL can decide")
                self.assertIsNone(ci_changes.selected_manifests(["docs/facebook-page.md", path], ROOT))

    def test_a_shared_test_file_no_manifest_names_runs_every_manifest(self):
        for path in ("tests/support.py", "tests/fixtures/sample.json", "tests/web/office_ui_check.mts"):
            with self.subTest(path):
                self.assertIsNone(ci_changes.selected_manifests([path], ROOT))
        self.assertEqual(["tests/mutations/ci_changes.yaml"], ci_changes.selected_manifests(["tests/test_ci_changes.py"], ROOT))

    def test_a_test_module_other_tests_import_helpers_from_runs_every_manifest(self):
        self.assertIsNone(ci_changes.selected_manifests(["tests/test_render.py"], ROOT))  # tests/test_diagram.py imports it
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            write(folder, "tests/mutations/tool.yaml", MANIFEST.format(target="scripts/tool.py"))
            write(folder, "tests/test_helpers_here.py", "def helper():\n    return 1\n")
            write(folder, "tests/test_alone.py", "x = 1\n")
            self.assertEqual([], ci_changes.selected_manifests(["tests/test_helpers_here.py"], folder))
            for importer in ("from tests.test_helpers_here import helper\n", "import tests.test_helpers_here\n",
                             "from tests import test_alone, test_helpers_here\n"):
                with self.subTest(importer):
                    write(folder, "tests/test_user.py", importer)
                    self.assertIsNone(ci_changes.selected_manifests(["tests/test_helpers_here.py"], folder))

    def test_a_deleted_or_renamed_file_runs_every_manifest(self):
        self.assertIsNone(ci_changes.selected_manifests(["tests/test_gone_since_this_change.py"], ROOT))
        self.assertIsNone(ci_changes.selected_manifests(["scripts/gone_since_this_change.py"], ROOT))
        self.assertEqual([], ci_changes.selected_manifests(["system-design-101/vi/gone.md"], ROOT))

    def test_manifests_that_cannot_be_read_run_every_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            write(folder, "scripts/tool.py", "x = 1\n")  # present, so only the missing manifests can decide
            self.assertIsNone(ci_changes.selected_manifests(["scripts/tool.py"], folder))
            write(folder, "tests/mutations/broken.yaml", "target: [unclosed\n")
            self.assertIsNone(ci_changes.selected_manifests(["scripts/tool.py"], folder))


def git(folder: Path, *args: str) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", *args],
                          cwd=folder, capture_output=True, text=True, check=True).stdout.strip()


def write(folder: Path, name: str, text: str) -> None:
    path = folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ChangedFilesTests(unittest.TestCase):
    def repository(self, tmp: str) -> tuple[Path, str]:
        folder = Path(tmp)
        git(folder, "init", "-q")
        write(folder, "scripts/tool.py", "x = 1\n")
        write(folder, "system-design-101/vi/lessons/sd-01-001/lesson.md", "a\n")
        git(folder, "add", "-A")
        git(folder, "commit", "-q", "-m", "base")
        return folder, git(folder, "rev-parse", "HEAD")

    def test_lists_every_changed_path_including_odd_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, base = self.repository(tmp)
            write(folder, "system-design-101/vi/lessons/sd-01-002/bài học.md", "b\n")
            write(folder, "system-design-101/vi/with space.md", "c\n")
            git(folder, "add", "-A")
            git(folder, "commit", "-q", "-m", "more")
            self.assertEqual(["system-design-101/vi/lessons/sd-01-002/bài học.md", "system-design-101/vi/with space.md"],
                             sorted(ci_changes.changed_files(base, folder)))

    def test_a_file_moved_out_of_the_store_lists_both_places(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, base = self.repository(tmp)
            git(folder, "mv", "system-design-101/vi/lessons/sd-01-001/lesson.md", "scripts/lesson.py")
            git(folder, "commit", "-q", "-m", "move")
            self.assertEqual(["scripts/lesson.py", "system-design-101/vi/lessons/sd-01-001/lesson.md"],
                             sorted(ci_changes.changed_files(base, folder)))

    def test_an_unknown_base_or_an_empty_one_is_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, _ = self.repository(tmp)
            self.assertIsNone(ci_changes.changed_files("0" * 40, folder))
            self.assertIsNone(ci_changes.changed_files("", folder))

    def test_a_folder_that_is_not_a_repository_is_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(ci_changes.changed_files("HEAD", Path(tmp)))


class MainTests(unittest.TestCase):
    def run_main(self, folder: Path, **environ: str) -> tuple[int, str]:
        output = folder / "github_output"
        code = ci_changes.main({**environ, "GITHUB_OUTPUT": str(output)}, folder)
        return code, output.read_text(encoding="utf-8") if output.exists() else ""

    def repository(self, tmp: str, changed: str) -> tuple[Path, str]:
        folder = Path(tmp)
        git(folder, "init", "-q")
        write(folder, "scripts/tool.py", "x = 1\n")
        git(folder, "add", "-A")
        git(folder, "commit", "-q", "-m", "base")
        base = git(folder, "rev-parse", "HEAD")
        write(folder, changed, "new\n")
        git(folder, "add", "-A")
        git(folder, "commit", "-q", "-m", "change")
        return folder, base

    def test_a_store_only_pull_request_writes_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, base = self.repository(tmp, STORE)
            code, written = self.run_main(folder, GITHUB_EVENT_NAME="pull_request", PR_BASE_SHA=base)
            self.assertEqual((0, "mutation=false\nmanifests=all\n"), (code, written))

    def test_a_pull_request_that_changes_code_writes_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, base = self.repository(tmp, "scripts/other.py")  # no manifests to read in this repository: all run
            code, written = self.run_main(folder, GITHUB_EVENT_NAME="pull_request", PR_BASE_SHA=base)
            self.assertEqual((0, "mutation=true\nmanifests=all\n"), (code, written))

    def test_a_pull_request_runs_only_the_manifests_that_name_a_changed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            git(folder, "init", "-q")
            write(folder, "scripts/tool.py", "x = 1\n")
            write(folder, "scripts/other.py", "y = 1\n")
            write(folder, "tests/mutations/tool.yaml", MANIFEST.format(target="scripts/tool.py"))
            write(folder, "tests/mutations/other.yaml", MANIFEST.format(target="scripts/other.py"))
            git(folder, "add", "-A")
            git(folder, "commit", "-q", "-m", "base")
            base = git(folder, "rev-parse", "HEAD")
            write(folder, "scripts/tool.py", "x = 2\n")
            git(folder, "commit", "-qam", "change")
            code, written = self.run_main(folder, GITHUB_EVENT_NAME="pull_request", PR_BASE_SHA=base)
            self.assertEqual((0, "mutation=true\nmanifests=tests/mutations/tool.yaml\n"), (code, written))

    def test_a_pull_request_no_manifest_names_skips_the_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            git(folder, "init", "-q")
            write(folder, "scripts/tool.py", "x = 1\n")
            write(folder, "tests/mutations/tool.yaml", MANIFEST.format(target="scripts/tool.py"))
            git(folder, "add", "-A")
            git(folder, "commit", "-q", "-m", "base")
            base = git(folder, "rev-parse", "HEAD")
            write(folder, "docs/note.md", "n\n")
            git(folder, "add", "-A")
            git(folder, "commit", "-q", "-m", "docs")
            code, written = self.run_main(folder, GITHUB_EVENT_NAME="pull_request", PR_BASE_SHA=base)
            self.assertEqual((0, "mutation=false\nmanifests=all\n"), (code, written))

    def test_a_push_writes_true_even_for_store_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, base = self.repository(tmp, STORE)
            code, written = self.run_main(folder, GITHUB_EVENT_NAME="push", PR_BASE_SHA=base)
            self.assertEqual((0, "mutation=true\nmanifests=all\n"), (code, written))

    def test_an_unreadable_base_writes_true_and_does_not_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, _ = self.repository(tmp, STORE)
            code, written = self.run_main(folder, GITHUB_EVENT_NAME="pull_request", PR_BASE_SHA="0" * 40)
            self.assertEqual((0, "mutation=true\nmanifests=all\n"), (code, written))

    def test_an_unwritable_output_file_still_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, base = self.repository(tmp, STORE)
            code = ci_changes.main({"GITHUB_EVENT_NAME": "pull_request", "PR_BASE_SHA": base,
                                    "GITHUB_OUTPUT": str(folder / "missing" / "output")}, folder)
            self.assertEqual(0, code)


class WorkflowUsesItTests(unittest.TestCase):
    def engine(self) -> list[dict]:
        return yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))["jobs"]["engine"]["steps"]

    def test_the_checkout_fetches_the_history_the_diff_needs(self):
        checkout = next(step for step in self.engine() if step.get("uses", "").startswith("actions/checkout"))
        self.assertEqual(0, checkout["with"]["fetch-depth"])

    def test_the_decision_runs_before_the_mutation_check_with_the_base_of_the_pull_request(self):
        steps = self.engine()
        decide = next(index for index, step in enumerate(steps) if step.get("id") == "changes")
        mutation = next(index for index, step in enumerate(steps) if "mutation_check.py" in step.get("run", ""))
        self.assertLess(decide, mutation)
        self.assertEqual("python scripts/ci_changes.py", steps[decide]["run"])
        self.assertEqual("${{ github.event.pull_request.base.sha }}", steps[decide]["env"]["PR_BASE_SHA"])

    def mutation_step(self) -> dict:
        return next(step for step in self.engine() if "mutation_check.py" in step.get("run", ""))

    def test_the_mutation_check_skips_only_when_the_decision_says_false(self):
        self.assertEqual("steps.changes.outputs.mutation != 'false'", self.mutation_step()["if"])

    def test_the_mutation_check_runs_on_several_tree_copies_unless_the_variable_says_otherwise(self):
        self.assertIn("python scripts/mutation_check.py \"$@\" --jobs ${{ vars.MUTATION_JOBS || '2' }}",
                      self.mutation_step()["run"])

    def run_step(self, manifests: str | None) -> list[str]:
        """The arguments the step's shell passes to the checker for a given `manifests` output."""
        script = self.mutation_step()["run"].replace("python scripts/mutation_check.py", "printf '%s\\n'")
        script = script.replace("${{ vars.MUTATION_JOBS || '2' }}", "2")
        environ = {"PATH": "/usr/bin:/bin"} | ({} if manifests is None else {"MANIFESTS": manifests})
        result = subprocess.run(["bash", "-c", script], env=environ, capture_output=True, text=True, check=True)
        return result.stdout.split()

    def test_the_step_runs_the_chosen_manifests_or_all_of_them(self):
        self.assertEqual("${{ steps.changes.outputs.manifests }}", self.mutation_step()["env"]["MANIFESTS"])
        self.assertEqual(["tests/mutations/a.yaml", "tests/mutations/b.yaml", "--jobs", "2"],
                         self.run_step("tests/mutations/a.yaml tests/mutations/b.yaml"))
        for manifests in ("all", "", None):
            with self.subTest(manifests):
                self.assertEqual(["--all", "--jobs", "2"], self.run_step(manifests))


if __name__ == "__main__":
    unittest.main()
