"""scripts/radar_preview.py and .github/workflows/radar-preview.yml: what a radar pull request may have the shared runner
draw, what the comment says, and that the workflow can neither approve nor publish nor run the pull request's code."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from mkt.model import ROOT
from scripts import radar_preview

WORKFLOW = ROOT / ".github/workflows/radar-preview.yml"
CAMPAIGN = "radar-2026-10-13-5"
POST = f"campaigns/{CAMPAIGN}/posts/vi/01-x.yaml"


def workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def steps() -> list[dict]:
    return workflow()["jobs"]["preview"]["steps"]


class ClassifyTests(unittest.TestCase):
    def test_a_radar_campaign_and_the_radar_tool_data_may_be_drawn(self):
        ok, campaigns, outside, _ = radar_preview.decide([POST, f"campaigns/{CAMPAIGN}/campaign.yaml", "tools/github-radar/brief.yaml"])
        self.assertTrue(ok)
        self.assertEqual([CAMPAIGN], campaigns)
        self.assertEqual([], outside)

    def test_a_second_run_of_the_day_and_two_campaigns_are_both_found(self):
        _, campaigns, _, _ = radar_preview.decide([f"campaigns/radar-2026-10-13/campaign.yaml", f"campaigns/{CAMPAIGN}/campaign.yaml"])
        self.assertEqual(["radar-2026-10-13", CAMPAIGN], campaigns)

    def test_code_is_never_drawn_because_the_engine_would_run_on_the_shared_runner(self):
        for path in ("mkt/render.py", "studio.py", "scripts/radar_preview.py", ".github/workflows/ci.yml", "requirements.txt",
                     "docs/agent-team.md", "tests/test_render.py"):
            ok, _, outside, reason = radar_preview.decide([POST, path])
            self.assertFalse(ok, path)
            self.assertEqual([path], outside)
            self.assertIn(path, reason)

    def test_a_path_that_climbs_out_of_the_campaign_is_outside(self):
        ok, _, outside, _ = radar_preview.decide([POST, f"campaigns/{CAMPAIGN}/../../mkt/render.py"])
        self.assertFalse(ok)
        self.assertEqual([f"campaigns/{CAMPAIGN}/../../mkt/render.py"], outside)

    def test_other_campaigns_and_look_alike_folders_are_outside(self):
        for path in ("campaigns/outlook-rsvp-tool/posts/vi/1.yaml", "campaigns/radar-evil/campaign.yaml",
                     "campaigns/radar-2026-10-13-x/campaign.yaml", "campaigns/radar-2026-10-13", "tools/github-radar-extra/brief.yaml",
                     "campaigns/radar-\u0662\u0660\u0662\u0666-10-13/campaign.yaml",           # Arabic-Indic digits are not a date
                     "tools/other/brief.yaml", "tools/github-radar"):
            ok, _, outside, _ = radar_preview.decide([POST, path])
            self.assertFalse(ok, path)
            self.assertEqual([path], outside, path)

    def test_nothing_to_draw_when_the_changes_cannot_be_read_or_hold_no_campaign(self):
        for changed in (None, [], ["tools/github-radar/brief.yaml"]):
            ok, campaigns, _, _ = radar_preview.decide(changed)
            self.assertFalse(ok, changed)
            self.assertEqual([], campaigns)


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


class PlanTests(unittest.TestCase):
    def plan(self, files: dict[str, str]) -> dict[str, str]:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            git(repo, "init", "-q")
            (repo / "README.md").write_text("x", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "base")
            base = git(repo, "rev-parse", "HEAD")
            for rel, text in files.items():
                (repo / rel).parent.mkdir(parents=True, exist_ok=True)
                (repo / rel).write_text(text, encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "radar")
            out = Path(tmp) / "output"
            self.assertEqual(0, radar_preview.main(["plan"], {"PR_BASE_SHA": base, "GITHUB_OUTPUT": str(out)}, cwd=repo))
            return parse_outputs(out.read_text(encoding="utf-8"))

    def test_a_radar_pull_request_is_planned_with_one_export_path_per_campaign(self):
        got = self.plan({POST: "a", "campaigns/radar-2026-10-13/campaign.yaml": "b", "tools/github-radar/brief.yaml": "c"})
        self.assertEqual("true", got["ok"])
        self.assertEqual(f"radar-2026-10-13 {CAMPAIGN}", got["campaigns"])
        self.assertEqual(f"campaigns/radar-2026-10-13/export/**\ncampaigns/{CAMPAIGN}/export/**", got["export_paths"])

    def test_a_pull_request_that_also_changes_code_is_not_planned_and_names_the_file(self):
        got = self.plan({POST: "a", "mkt/render.py": "print('x')"})
        self.assertEqual("false", got["ok"])
        self.assertEqual("", got["campaigns"] + got["export_paths"])
        self.assertEqual("mkt/render.py", got["outside"])

    def test_a_file_name_cannot_end_its_output_block_and_set_an_output_of_its_own(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            git(repo, "init", "-q")
            (repo / "README.md").write_text("x", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "base")
            base = git(repo, "rev-parse", "HEAD")
            evil = "x\nRADAR_EOF\nok<<RADAR_EOF\ntrue\nRADAR_EOF\n"
            (repo / evil).write_text("y", encoding="utf-8")
            (repo / POST).parent.mkdir(parents=True)
            (repo / POST).write_text("a", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "radar")
            out = Path(tmp) / "output"
            radar_preview.main(["plan"], {"PR_BASE_SHA": base, "GITHUB_OUTPUT": str(out)}, cwd=repo)
            got = parse_outputs(out.read_text(encoding="utf-8"))
            self.assertEqual("false", got["ok"])
            self.assertEqual({"ok", "campaigns", "export_paths", "reason", "outside"}, set(got))

    def test_a_symbolic_link_in_a_campaign_is_not_drawn_even_when_the_path_looks_like_radar_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            git(repo, "init", "-q")
            (repo / "README.md").write_text("x", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "base")
            base = git(repo, "rev-parse", "HEAD")
            (repo / "campaigns" / CAMPAIGN).mkdir(parents=True)
            (repo / "campaigns" / CAMPAIGN / "campaign.yaml").write_text("a", encoding="utf-8")
            (repo / "campaigns" / CAMPAIGN / "export").symlink_to("/etc")           # the engine would write through it
            (repo / "tools" / "github-radar").mkdir(parents=True)
            (repo / "tools" / "github-radar" / "brief.yaml").symlink_to("/etc/hostname")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "radar")
            out = Path(tmp) / "output"
            radar_preview.main(["plan"], {"PR_BASE_SHA": base, "GITHUB_OUTPUT": str(out)}, cwd=repo)
            got = parse_outputs(out.read_text(encoding="utf-8"))
            self.assertEqual("false", got["ok"])
            self.assertEqual({f"campaigns/{CAMPAIGN}/export", "tools/github-radar/brief.yaml"}, set(got["outside"].splitlines()))
            self.assertIn("symbolic link", got["reason"])

    def test_a_base_that_moved_after_the_event_does_not_put_its_files_into_the_pull_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            git(repo, "init", "-q", "-b", "main")
            (repo / "README.md").write_text("x", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "base")
            event_base = git(repo, "rev-parse", "HEAD")
            git(repo, "checkout", "-q", "-b", "radar/x")
            (repo / POST).parent.mkdir(parents=True)
            (repo / POST).write_text("a", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "radar")
            git(repo, "checkout", "-q", "main")
            (repo / "mkt.py").write_text("code someone else merged after the pull request was opened", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "main moved")
            git(repo, "merge", "-q", "--no-ff", "-m", "merge ref", "radar/x")           # what GitHub checks out for the event
            out = Path(tmp) / "output"
            radar_preview.main(["plan"], {"PR_BASE_SHA": event_base, "GITHUB_OUTPUT": str(out)}, cwd=repo)
            got = parse_outputs(out.read_text(encoding="utf-8"))
            self.assertEqual(("true", CAMPAIGN), (got["ok"], got["campaigns"]))

    def test_an_unreadable_base_is_not_planned(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "output"
            self.assertEqual(0, radar_preview.main(["plan"], {"PR_BASE_SHA": "", "GITHUB_OUTPUT": str(out)}))
            self.assertEqual("false", parse_outputs(out.read_text(encoding="utf-8"))["ok"])


def parse_outputs(text: str) -> dict[str, str]:
    """GITHUB_OUTPUT as the runner reads it: `name<<DELIMITER`, the value's lines, then the delimiter alone on a line."""
    values, key, delimiter, lines = {}, None, None, []
    for line in text.splitlines():
        if key is None:
            key, delimiter = line.split("<<", 1)
        elif line == delimiter:
            values[key] = "\n".join(lines)
            key, lines = None, []
        else:
            lines.append(line)
    return values


def render_fixture(root: Path, caption: str, overflow: list[int]) -> None:
    folder = root / "campaigns" / CAMPAIGN / "export" / "vi" / "01-x"
    folder.mkdir(parents=True)
    (folder / "manifest.json").write_text(json.dumps({"sha": "0123456789abcdef", "slides": ["01.png", "02.png", "03.png"],
                                                      "overflow": overflow}), encoding="utf-8")
    (folder / "facebook.txt").write_text(caption, encoding="utf-8")


def render_fixture_once(root: Path) -> None:
    if not (root / "campaigns" / CAMPAIGN / "export" / "vi" / "01-x").exists():
        render_fixture(root, "Caption", [])


def comment(root: Path, **over) -> str:
    args = dict(plan_ok=True, campaigns=[CAMPAIGN], reason="", outside=[], failed=False,
                artifact_url="https://example.test/artifact", run_url="https://example.test/run")
    args.update(over)
    return radar_preview.build_comment(root, **args)


class CommentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_it_starts_with_the_marker_the_workflow_looks_for_and_links_the_images(self):
        render_fixture(self.root, "Caption", [])
        body = comment(self.root)
        self.assertTrue(body.startswith(radar_preview.MARKER + "\n"))
        self.assertIn("| radar-2026-10-13-5 | vi/01-x | 3 | none | `0123456789ab` |", body)
        self.assertIn("(https://example.test/artifact)", body)
        self.assertIn("Nothing is approved, committed or published.", body)

    def test_overflowing_slides_are_listed(self):
        render_fixture(self.root, "Caption", [2, 3])
        self.assertIn("| 2, 3 |", comment(self.root))

    def test_a_caption_cannot_close_its_fence_or_ping_anyone(self):
        caption = "Hello @octocat\n```\n## injected heading\n````\nmore"
        render_fixture(self.root, caption, [])
        body = comment(self.root)
        self.assertIn("`````text\n" + caption + "\n`````", body)           # five backticks: longer than the longest run inside
        outside_fence = body.replace("`````text\n" + caption + "\n`````", "")
        self.assertNotIn("@octocat", outside_fence)
        self.assertNotIn("injected heading", outside_fence)

    def test_a_very_long_caption_is_cut(self):
        render_fixture(self.root, "x" * 10000, [])
        self.assertLess(len(comment(self.root)), 6000)

    def test_a_failure_points_at_the_run(self):
        render_fixture(self.root, "Caption", [])
        self.assertIn("A step failed or a manifest could not be read: read [the run](https://example.test/run)",
                      comment(self.root, failed=True))
        self.assertNotIn("failed", comment(self.root, failed=False))

    def test_every_step_that_did_not_succeed_makes_the_comment_say_so(self):
        # install failed -> the check and the drawing are `skipped`; upload failed -> check and drawing stay `success`
        everything = {"install": "success", "check": "success", "render": "success", "upload": "success"}
        for step in everything:
            for outcome in ("failure", "skipped", "cancelled"):
                with self.subTest(step=step, outcome=outcome):
                    out = self.root / f"{step}-{outcome}.md"
                    self.run_comment({**everything, step: outcome}, out)
                    self.assertIn("A step failed", out.read_text(encoding="utf-8"))
        ok = self.root / "ok.md"
        self.run_comment(everything, ok)
        self.assertNotIn("A step failed", ok.read_text(encoding="utf-8"))

    def run_comment(self, outcomes: dict[str, str], out: Path) -> None:
        render_fixture_once(self.root)
        original = radar_preview.ROOT
        radar_preview.ROOT = self.root
        try:
            code = radar_preview.main(["comment", "--plan-ok=true", f"--campaigns={CAMPAIGN}", "--reason=", "--outside=",
                                       *[f"--{step}={outcome}" for step, outcome in outcomes.items()],
                                       "--artifact-url=https://a", "--run-url=https://r", f"--out={out}"])
        finally:
            radar_preview.ROOT = original
        self.assertEqual(0, code)

    def test_a_manifest_that_cannot_be_read_does_not_stop_the_comment_that_reports_the_failure(self):
        render_fixture(self.root, "Caption", [])                                         # one good post
        export = self.root / "campaigns" / CAMPAIGN / "export" / "vi"
        for name, content in (("bad-json", b"{not json"), ("a-list", b"[1, 2]"), ("not-utf8", b"\xff\xfe\x00{")):
            (export / name).mkdir()
            (export / name / "manifest.json").write_bytes(content)
        (export / "odd-types").mkdir()
        (export / "odd-types" / "manifest.json").write_text('{"slides": 5, "overflow": "x", "sha": ["a"]}', encoding="utf-8")
        body = comment(self.root)
        for name in ("bad-json", "a-list", "not-utf8"):
            self.assertIn(f"`radar-2026-10-13-5/vi/{name}`", body)
        self.assertIn("A step failed or a manifest could not be read", body)
        self.assertIn("| radar-2026-10-13-5 | vi/01-x | 3 | none |", body)               # the readable post is still reported
        self.assertIn("| vi/odd-types | 0 | none |", body.replace("radar-2026-10-13-5 | ", ""))   # odd types are read as empty, not as an error

    def test_a_missing_artifact_link_is_not_published_as_an_empty_link(self):
        render_fixture(self.root, "Caption", [])
        body = comment(self.root, artifact_url="")
        self.assertNotIn("download the artifact", body)
        self.assertNotIn("]()", body)
        self.assertIn("could not be attached to the run", body)

    def test_a_pull_request_that_is_not_drawn_says_why_and_lists_at_most_five_files(self):
        body = comment(self.root, plan_ok=False, reason="7 changed file(s) are not radar data", campaigns=[],
                       outside=[f"mkt/f{i}.py" for i in range(7)])
        self.assertTrue(body.startswith(radar_preview.MARKER))
        self.assertIn("Not drawn here: 7 changed file(s) are not radar data.", body)
        self.assertIn("`mkt/f4.py`", body)
        self.assertNotIn("mkt/f5.py", body)

    def test_a_file_name_cannot_break_out_of_its_code_span(self):
        body = comment(self.root, plan_ok=False, reason="1 changed file(s) are not radar data", campaigns=[],
                       outside=["a`b\n## injected"])
        self.assertIn("- `a?b????injected`", body)               # backtick, newline, '#' and space all become '?'
        self.assertNotIn("\n## injected", body)

    def test_the_reason_is_one_printable_line(self):
        body = comment(self.root, plan_ok=False, reason="x`y\nz", campaigns=[], outside=[])
        self.assertIn("Not drawn here: x?y?z.", body)

    def test_a_post_or_language_folder_name_cannot_put_a_link_or_html_in_the_comment(self):
        folder = self.root / "campaigns" / CAMPAIGN / "export" / "v<b>i" / "[x](evil.test)@octocat"       # no "/": that would nest
        folder.mkdir(parents=True)
        (folder / "manifest.json").write_text(json.dumps({"sha": "0123456789abcdef", "slides": ["01.png"], "overflow": []}), encoding="utf-8")
        body = comment(self.root)
        self.assertIn("| v?b?i/?x??evil.test??octocat | 1 |", body)          # the row exists, with the name made safe
        self.assertNotIn("](evil.test)", body)
        self.assertNotIn("<b>", body)
        self.assertNotIn("@octocat", body)

    def test_the_file_named_in_the_reason_cannot_carry_a_link(self):
        ok, _, _, reason = radar_preview.decide([POST, "[x](http://evil.test)@octocat.py"])
        self.assertFalse(ok)
        self.assertNotIn("](", reason)
        self.assertNotIn("@", reason)

    def test_a_campaign_without_a_drawing_says_so(self):
        self.assertIn("No post was drawn.", comment(self.root))

    def test_the_command_writes_the_file_the_workflow_posts(self):
        render_fixture(self.root, "Caption", [])
        out = self.root / "comment.md"
        original = radar_preview.ROOT
        radar_preview.ROOT = self.root
        try:
            code = radar_preview.main(["comment", "--plan-ok=true", f"--campaigns={CAMPAIGN}", "--reason=", "--outside=-x\nmkt/y.py",
                                       "--install=success", "--check=success", "--render=failure", "--upload=success", "--artifact-url=https://a", "--run-url=https://r",
                                       f"--out={out}"])
        finally:
            radar_preview.ROOT = original
        self.assertEqual(0, code)
        self.assertIn("A step failed", out.read_text(encoding="utf-8"))


class WorkflowTests(unittest.TestCase):
    def test_it_runs_only_on_pull_requests_that_touch_a_radar_campaign_and_never_on_pull_request_target(self):
        config = workflow()
        triggers = config[True] if True in config else config["on"]
        self.assertEqual(["pull_request"], list(triggers))
        self.assertEqual(["campaigns/radar-*/**"], triggers["pull_request"]["paths"])

    def test_the_token_can_read_the_code_and_write_the_one_comment_and_nothing_else(self):
        self.assertEqual({"contents": "read", "pull-requests": "write"}, workflow()["permissions"])

    def test_only_a_branch_of_this_repository_named_radar_runs_on_the_shared_runner(self):
        job = workflow()["jobs"]["preview"]
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", job["if"])
        self.assertIn("startsWith(github.event.pull_request.head.ref, 'radar/')", job["if"])
        self.assertIn("vars.CI_RUNNER || 'self-hosted'", job["runs-on"])

    def test_the_checkout_does_not_leave_the_token_in_the_workspace_of_a_persistent_runner(self):
        checkout = next(s for s in steps() if s.get("uses", "").startswith("actions/checkout"))
        self.assertIs(False, checkout["with"]["persist-credentials"])

    def test_a_newer_push_replaces_the_run_of_the_same_pull_request(self):
        concurrency = workflow()["concurrency"]
        self.assertIn("github.event.pull_request.number", concurrency["group"])
        self.assertIs(True, concurrency["cancel-in-progress"])

    def test_no_script_interpolates_anything_a_pull_request_controls(self):
        for step in steps():
            for expression in re.findall(r"\$\{\{(.*?)\}\}", step.get("run", ""), re.S):
                self.assertEqual("runner.environment == 'github-hosted' && '--with-deps' || ''", expression.strip(), step.get("name"))

    def test_it_never_approves_publishes_or_commits(self):
        for step in steps():
            run = step.get("run", "")
            for word in ("approve", "publish", "git push", "git commit", "pack"):
                self.assertNotIn(word, run, step.get("name"))

    def test_it_draws_only_what_the_plan_allowed(self):
        gated = {s["name"] for s in steps() if "steps.plan.outputs.ok == 'true'" in str(s.get("if", ""))}
        self.assertTrue({"Install", "Check the campaign", "Draw the images and texts"} <= gated, gated)

    def test_the_comment_it_edits_is_its_own_and_carries_the_marker_of_the_script(self):
        script = next(s for s in steps() if s.get("uses", "").startswith("actions/github-script"))["with"]["script"]
        self.assertIn("github-actions[bot]", script)
        self.assertIn(radar_preview.MARKER, script)

    def test_a_failed_check_or_drawing_still_fails_the_run_after_the_comment_is_posted(self):
        names = [s.get("name") for s in steps()]
        last = steps()[-1]
        self.assertEqual("Fail when the check or the drawing failed", names[-1])
        self.assertLess(names.index("Keep one comment on the pull request"), len(names) - 1)
        self.assertIn("steps.check.outcome == 'failure'", last["if"])
        self.assertIn("steps.render.outcome == 'failure'", last["if"])

    def test_the_comment_is_told_the_outcome_of_every_step_it_reports_on(self):
        step = next(s for s in steps() if s.get("name") == "Write the comment")
        for name, outcome in (("INSTALL", "steps.install.outcome"), ("CHECK", "steps.check.outcome"),
                              ("RENDER", "steps.render.outcome"), ("UPLOAD", "steps.upload.outcome")):
            self.assertIn(outcome, step["env"][name])
            self.assertIn(f'--{name.lower()}="${name}"', step["run"])
        self.assertTrue(any(s.get("id") == "install" for s in steps()))

    def test_the_checks_and_the_drawing_do_not_stop_the_comment(self):
        by_name = {s.get("name"): s for s in steps()}
        self.assertIs(True, by_name["Check the campaign"]["continue-on-error"])
        self.assertIs(True, by_name["Draw the images and texts"]["continue-on-error"])


if __name__ == "__main__":
    unittest.main()
