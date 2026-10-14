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

    def test_an_output_value_cannot_end_its_own_block_and_set_an_output_of_its_own(self):
        # the planner now makes every path printable before it writes it; the writer still must not trust its values
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "output"
            hostile = "x\nRADAR_EOF\nok<<RADAR_EOF\ntrue\nRADAR_EOF\n"
            radar_preview.write_outputs(str(out), {"outside": hostile, "ok": "false"})
            got = parse_outputs(out.read_text(encoding="utf-8"))
            self.assertEqual({"outside", "ok"}, set(got))
            self.assertEqual("false", got["ok"])
            self.assertEqual(hostile, got["outside"])

    def test_a_file_name_that_is_not_utf8_does_not_stop_the_planner_from_answering(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            git(repo, "init", "-q")
            (repo / "README.md").write_text("x", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "base")
            base = git(repo, "rev-parse", "HEAD")
            (repo / POST).parent.mkdir(parents=True)
            (repo / POST).write_text("a", encoding="utf-8")
            (repo / "mkt").mkdir()
            try:
                Path(os.fsdecode(os.fsencode(repo) + b"/mkt/bad\xff.py")).write_bytes(b"x")      # a name that is not valid UTF-8
            except OSError:
                self.skipTest("this file system cannot hold a name that is not UTF-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "radar")
            out = Path(tmp) / "output"
            self.assertEqual(0, radar_preview.main(["plan"], {"PR_BASE_SHA": base, "GITHUB_OUTPUT": str(out)}, cwd=repo))
            got = parse_outputs(out.read_text(encoding="utf-8"))
            self.assertEqual("false", got["ok"])
            self.assertEqual("mkt/bad?.py", got["outside"])

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


def render_many(root: Path, count: int, caption, overflow: list[int] | None = None) -> None:
    """`count` drawn posts of the fixture campaign, the caption of post n being `caption(n)`."""
    for n in range(count):
        folder = root / "campaigns" / CAMPAIGN / "export" / "vi" / f"post-{n:03d}"
        folder.mkdir(parents=True)
        (folder / "manifest.json").write_text(json.dumps({"sha": "0123456789abcdef", "slides": ["01.png"], "overflow": overflow or []}),
                                              encoding="utf-8")
        (folder / "facebook.txt").write_text(caption(n), encoding="utf-8")


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

    def test_a_caption_that_is_cut_says_so_where_a_collapsed_reader_sees_it_and_points_at_the_whole_text(self):
        render_fixture(self.root, "x" * 10000, [])
        body = comment(self.root)
        summary = next(line for line in body.splitlines() if line.startswith("<details><summary>"))
        self.assertIn("cut: the first 3000 of 10000 characters", summary)
        self.assertIn("`facebook.txt` beside this post, in the artifact", body)

    def test_a_caption_that_fits_is_not_marked_as_cut(self):
        render_fixture(self.root, "x" * radar_preview.CAPTION_LIMIT + "  \n", [])          # trailing blanks are not part of the caption
        body = comment(self.root)
        self.assertNotIn("cut:", body)
        self.assertNotIn("The rest of the caption", body)

    def test_many_long_captions_leave_the_comment_under_the_size_github_accepts(self):
        render_many(self.root, 30, lambda n: f"Caption {n:03d} " + "x" * 2980)               # 30 x 3000 characters
        body = comment(self.root)
        shown = body.count("<details>")
        self.assertLess(len(body), radar_preview.BODY_LIMIT)
        self.assertLess(radar_preview.BODY_LIMIT, 65536)
        self.assertTrue(body.startswith(radar_preview.MARKER + "\n"))
        self.assertTrue(0 < shown < 30, shown)
        self.assertIn(f"{30 - shown} caption(s) are not shown here", body)
        self.assertIn("Caption 000 ", body)                                                   # the first are kept
        self.assertNotIn("Caption 029 ", body)
        self.assertTrue(body.rstrip().endswith(radar_preview.NEXT))                           # and the last line survives the cut
        self.assertIn("| radar-2026-10-13-5 | vi/post-029 |", body)                          # every post is still in the table

    def test_a_caption_that_is_all_backticks_counts_its_fences_in_the_budget(self):
        render_many(self.root, 12, lambda n: "`" * 3000)                                      # fences of 3001 backticks, twice each
        body = comment(self.root)
        self.assertLess(len(body), radar_preview.BODY_LIMIT)
        self.assertNotIn("too large for one comment", body)                                   # the budget held; the backstop did not have to
        self.assertTrue(0 < body.count("<details>") < 12, body.count("<details>"))

    def test_very_many_posts_are_not_all_listed_and_a_long_overflow_list_is_cut(self):
        render_many(self.root, 400, lambda n: "", overflow=list(range(1, 51)))
        body = comment(self.root)
        self.assertLess(len(body), radar_preview.BODY_LIMIT)
        rows = [line for line in body.splitlines() if line.startswith("| radar-2026-10-13-5 |")]
        self.assertTrue(0 < len(rows) < 400, len(rows))
        self.assertIn(f"{400 - len(rows)} more post(s) are not listed here", body)
        self.assertIn("(+40 more)", rows[0])
        self.assertNotIn("11, 12", rows[0])

    def test_a_comment_that_no_budget_counts_is_replaced_by_a_short_one_that_claims_nothing(self):
        body = comment(self.root, plan_ok=False, reason="r", outside=["a" * 20000 for _ in range(5)])
        self.assertLess(len(body), 2000)
        self.assertTrue(body.startswith(radar_preview.MARKER + "\n"))
        self.assertIn("too large for one comment", body)
        self.assertIn("(https://example.test/run)", body)
        self.assertNotIn("Checked and drawn", body)
        self.assertNotIn("approve in the app", body)                                          # it says nothing about the check: no invitation either

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

    def test_a_pull_request_whose_campaign_was_removed_gets_a_comment_that_replaces_the_old_one(self):
        ok, campaigns, outside, reason = radar_preview.decide(["tools/github-radar/brief.yaml"])
        self.assertEqual((False, [], []), (ok, campaigns, outside))
        body = comment(self.root, plan_ok=ok, reason=reason, campaigns=campaigns, outside=outside)
        self.assertTrue(body.startswith(radar_preview.MARKER + "\n"))                     # the workflow edits its own comment by this marker
        self.assertIn("Not drawn here: no radar campaign among the changed files.", body)
        self.assertNotIn("Checked and drawn", body)

    def test_the_claim_that_the_pull_request_was_checked_and_drawn_is_made_only_when_it_was(self):
        render_fixture(self.root, "Caption", [])
        self.assertIn("Checked and drawn", comment(self.root))                                   # every step succeeded, a post was drawn
        for label, body in (("a step failed", comment(self.root, failed=True)),
                            ("nothing was drawn", comment(self.root / "nothing-here"))):
            with self.subTest(label):
                self.assertNotIn("Checked and drawn", body)
                self.assertIn("were attempted", body)
                self.assertIn("did not all succeed", body)
        export = self.root / "campaigns" / CAMPAIGN / "export" / "vi" / "bad"
        export.mkdir()
        (export / "manifest.json").write_text("{not json", encoding="utf-8")
        body = comment(self.root)                                                                # a manifest could not be read
        self.assertNotIn("Checked and drawn", body)
        self.assertIn("Manifests that could not be read", body)

    def test_the_invitation_to_approve_is_made_only_when_the_pull_request_was_checked_and_drawn(self):
        render_fixture(self.root, "Caption", [])
        self.assertTrue(comment(self.root).rstrip().endswith(radar_preview.NEXT))                # every step succeeded, a post was drawn
        for label, body in (("a step failed", comment(self.root, failed=True)),
                            ("nothing was drawn", comment(self.root / "nothing-here"))):
            with self.subTest(label):
                self.assertNotIn("approve", body.replace("Nothing is approved", ""))
                self.assertTrue(body.rstrip().endswith(radar_preview.RETRY), body)
        export = self.root / "campaigns" / CAMPAIGN / "export" / "vi" / "bad"
        export.mkdir()
        (export / "manifest.json").write_text("{not json", encoding="utf-8")
        body = comment(self.root)                                                                # a manifest could not be read
        self.assertNotIn("approve in the app", body)
        self.assertTrue(body.rstrip().endswith(radar_preview.RETRY), body)

    def test_a_campaign_without_a_drawing_says_so(self):
        self.assertIn("No post was drawn.", comment(self.root))

    def test_the_comment_reads_the_drawn_files_of_the_checkout_it_is_given(self):
        render_fixture(self.root, "A caption only the given checkout has", [])
        out = self.root / "comment.md"
        code = radar_preview.main(["comment", "--plan-ok=true", f"--campaigns={CAMPAIGN}", f"--root={self.root}", "--install=success",
                                   "--check=success", "--render=success", "--upload=success", "--artifact-url=https://a",
                                   "--run-url=https://r", f"--out={out}"])
        self.assertEqual(0, code)
        self.assertIn("A caption only the given checkout has", out.read_text(encoding="utf-8"))

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
    def test_it_runs_on_every_push_to_a_pull_request_never_on_pull_request_target_and_without_a_path_filter(self):
        config = workflow()
        triggers = config[True] if True in config else config["on"]
        self.assertEqual(["pull_request"], list(triggers))
        # a path filter looks at the whole diff: a push that removes the campaign would never run, and the comment that says
        # "drawn" would stay on a pull request that no longer holds the campaign
        self.assertNotIn("paths", triggers["pull_request"])
        self.assertNotIn("paths-ignore", triggers["pull_request"])
        self.assertIn("synchronize", triggers["pull_request"]["types"])

    def test_the_token_can_read_the_code_and_write_the_one_comment_and_nothing_else(self):
        self.assertEqual({"contents": "read", "pull-requests": "write"}, workflow()["permissions"])

    def test_only_a_branch_of_this_repository_named_radar_runs_on_the_shared_runner(self):
        job = workflow()["jobs"]["preview"]
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", job["if"])
        self.assertIn("startsWith(github.event.pull_request.head.ref, 'radar/')", job["if"])
        self.assertIn("vars.CI_RUNNER || 'self-hosted'", job["runs-on"])

    def test_the_planner_and_the_comment_writer_run_from_the_base_commit_not_from_the_pull_request(self):
        by_name = {s.get("name"): s for s in steps()}
        copy = by_name["The planner, from the base branch"]["run"]
        # the base commit is the first parent of the merge this run checked out; its files are read out of git
        self.assertIn('set -- $(git rev-list --parents -n 1 HEAD)', copy)
        self.assertIn('[ "$#" -eq 3 ]', copy)                                       # HEAD must be that merge
        self.assertIn('git show "$2:scripts/$script"', copy)                         # $2 = first parent = base; $3 would be the pull request
        self.assertIn("radar_preview.py ci_changes.py", copy)                        # the planner and the one module it imports
        self.assertIn('"$RUNNER_TEMP/trusted/scripts/$script"', copy)                # outside the workspace the pull request controls
        for step in steps():
            run = step.get("run", "")
            self.assertNotIn("python scripts/radar_preview.py", run, step.get("name"))     # that path is the pull request's own copy
            self.assertNotIn("python trusted/", run, step.get("name"))                      # a workspace folder is the pull request's too
        self.assertEqual('python "$RUNNER_TEMP/trusted/scripts/radar_preview.py" plan', by_name["Which files does this pull request change?"]["run"])
        write = by_name["Write the comment"]["run"]
        self.assertIn('python "$RUNNER_TEMP/trusted/scripts/radar_preview.py" comment', write)
        self.assertIn('--root="$GITHUB_WORKSPACE"', write)               # the trusted script reads the pull request's drawn files
        names = [s.get("name") or s.get("id") for s in steps()]
        self.assertLess(names.index("The planner, from the base branch"), names.index("Which files does this pull request change?"))

    def run_planner_copy_step(self, repo: Path, runner_temp: Path) -> subprocess.CompletedProcess:
        step = next(s for s in steps() if s.get("name") == "The planner, from the base branch")
        return subprocess.run(["bash", "-e", "-c", step["run"]], cwd=repo, env={**os.environ, "RUNNER_TEMP": str(runner_temp)},
                              capture_output=True, text=True)

    def test_the_planner_copy_step_reads_the_base_version_even_when_the_pull_request_replaces_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, temp = Path(tmp) / "repo", Path(tmp) / "temp"
            repo.mkdir()
            temp.mkdir()
            git(repo, "init", "-q", "-b", "main")
            (repo / "scripts").mkdir()
            (repo / "scripts" / "radar_preview.py").write_text("BASE planner", encoding="utf-8")
            (repo / "scripts" / "ci_changes.py").write_text("BASE ci_changes", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "base")
            git(repo, "checkout", "-q", "-b", "radar/x")
            (repo / "scripts" / "radar_preview.py").write_text("PULL REQUEST planner: rm -rf everything", encoding="utf-8")
            (repo / "scripts" / "ci_changes.py").unlink()
            (repo / "trusted").symlink_to(tmp)                                  # a folder of the workspace the pull request points elsewhere
            (repo / POST).parent.mkdir(parents=True)
            (repo / POST).write_text("a", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "radar")
            git(repo, "checkout", "-q", "main")
            (repo / "notes.txt").write_text("the base moved after the pull request was opened", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "main moved")
            git(repo, "merge", "-q", "--no-ff", "-m", "merge ref", "radar/x")       # what GitHub checks out for a pull_request event
            done = self.run_planner_copy_step(repo, temp)
            self.assertEqual(0, done.returncode, done.stderr)
            self.assertEqual("BASE planner", (temp / "trusted" / "scripts" / "radar_preview.py").read_text(encoding="utf-8"))
            self.assertEqual("BASE ci_changes", (temp / "trusted" / "scripts" / "ci_changes.py").read_text(encoding="utf-8"))
            self.assertEqual({"radar_preview.py", "ci_changes.py"}, {p.name for p in (temp / "trusted" / "scripts").iterdir()})

    def test_the_planner_copy_step_refuses_a_head_that_is_not_the_merge_of_the_pull_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, temp = Path(tmp) / "repo", Path(tmp) / "temp"
            repo.mkdir()
            temp.mkdir()
            git(repo, "init", "-q", "-b", "main")
            (repo / "scripts").mkdir()
            (repo / "scripts" / "radar_preview.py").write_text("x", encoding="utf-8")
            (repo / "scripts" / "ci_changes.py").write_text("x", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "one commit, no merge")
            done = self.run_planner_copy_step(repo, temp)
            self.assertNotEqual(0, done.returncode)
            self.assertIn("not the merge", done.stdout + done.stderr)
            self.assertFalse((temp / "trusted").exists())

    def test_there_is_one_checkout_and_none_into_a_folder_of_the_workspace(self):
        # actions/checkout empties the folder it is given, and resolves a symbolic link the pull request carries
        checkouts = [s for s in steps() if s.get("uses", "").startswith("actions/checkout")]
        self.assertEqual(1, len(checkouts))
        self.assertNotIn("path", checkouts[0].get("with", {}))

    def test_an_export_the_pull_request_carried_is_cleared_before_anything_can_fail_or_be_uploaded(self):
        # the upload and the comment run even after a failed install, check or drawing: the clearing must come first
        names = [s.get("name") for s in steps()]
        clear = next(s for s in steps() if s.get("name") == "Clear the exports the pull request carried")
        self.assertLess(names.index("Which files does this pull request change?"), names.index(clear["name"]))
        for later in ("Install", "Check the campaign", "Draw the images and texts", "Attach the images and texts to the run"):
            self.assertLess(names.index(clear["name"]), names.index(later), later)
        self.assertIn("steps.plan.outputs.ok == 'true'", clear["if"])
        self.assertNotIn("always()", clear["if"])
        self.assertIn('rm -rf -- "campaigns/$campaign/export"', clear["run"])
        self.assertIn("for campaign in $CAMPAIGNS", clear["run"])           # only the campaigns the plan found, from the environment

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

    def test_nothing_is_drawn_from_data_the_check_refused(self):
        draw = next(s for s in steps() if s.get("id") == "render")
        condition = str(draw["if"])
        self.assertIn("steps.plan.outputs.ok == 'true'", condition)
        self.assertIn("steps.check.outcome == 'success'", condition)
        self.assertNotIn("always()", condition)             # a status function would run it after a failed install as well

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
