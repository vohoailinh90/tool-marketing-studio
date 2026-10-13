"""scripts/codex_round_count.py: the review count of docs/claude-to-codex.md section 16 (which sets no cap on review rounds).

Fixtures copy the shape of real connector posts (the summary table, the review
and no-findings bodies, the inline-comment thread) with synthetic content.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "codex_round_count.py"


def load_module(name: str, path: Path):
    """Load from source, never from the bytecode cache (see test_session_budget)."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


counter = load_module("codex_round_count", SCRIPT)

BOT = "chatgpt-codex-connector[bot]"
OWNER = "octo-owner"

ABOUT = (
    "<details> <summary>ℹ️ About Codex in GitHub</summary>\n<br/>\n\n"
    "[Your team has set up Codex to review pull requests in this repo]"
    "(https://chatgpt.com/codex/cloud/settings/general). Reviews are triggered when you\n"
    "- Open a pull request for review\n- Mark a draft as ready\n"
    "- Comment \"@codex review\" or \"@codex security review\".\n\n"
    "Codex reacts with \U0001F440 while any review is running, comments if it has suggestions, "
    "and reacts with \U0001F44D once all reviews finish with no findings.\n\n</details>"
)
SUMMARY = (
    "<!-- codex-pull-request-review-summary -->\n\n## Codex Review Summary\n\n"
    "This comment shows the latest Codex review activity on this pull request.\n\n"
    "| Review | Status | Commit | Review trigger |\n| --- | --- | --- | --- |\n"
    "| \U0001F4DD **Code Review** | ✅ **Completed** "
    "<relative-time datetime=\"2026-10-01T14:24:16.794722Z\">2026-10-01T14:24:16.794722Z</relative-time>"
    " | `7e7d3da` | Manual request |\n\n\n\n" + ABOUT
)


def review_body(sha: str) -> str:
    return ("\n### \U0001F4A1 Codex Review\n\nHere are some automated review suggestions for this pull request.\n\n"
            f"**Reviewed commit:** `{sha}`\n    \n\n" + ABOUT)


def clean_body(sha: str) -> str:
    return f"Codex Review: Didn't find any major issues. Hooray!\n\n**Reviewed commit:** `{sha}`\n\n" + ABOUT


def at(minute: int, second: int = 0) -> str:
    return f"2026-10-01T14:{minute:02d}:{second:02d}Z"


def comment(i: int, login: str, body: str, when: str) -> dict:
    return {"id": i, "user": {"login": login}, "body": body, "created_at": when,
            "html_url": f"https://github.com/o/r/pull/1#issuecomment-{i}"}


def review(i: int, login: str, body: str, when: str, sha: str = "d08b230db208db98a766") -> dict:
    return {"id": i, "user": {"login": login}, "body": body, "state": "COMMENTED", "commit_id": sha,
            "submitted_at": when, "html_url": f"https://github.com/o/r/pull/1#pullrequestreview-{i}"}


def ask(i: int, minute: int, text: str = "@codex review") -> dict:
    return comment(i, OWNER, text + "\n\nRound for this head.", at(minute))


def bot_review(i: int, minute: int, sha: str = "d08b230db2") -> dict:
    return review(i, BOT, review_body(sha), at(minute), sha=sha + "08db98a766")


INLINE_KEYS = ("path", "diff_hunk", "pull_request_review_id")


class Run:
    def __init__(self, test: unittest.TestCase):
        self.test = test
        self.dir = tempfile.TemporaryDirectory()
        test.addCleanup(self.dir.cleanup)
        self.n = 0

    def file(self, data=None, raw: bytes | None = None) -> str:
        self.n += 1
        path = Path(self.dir.name) / f"in{self.n}.json"
        path.write_bytes(raw if raw is not None else json.dumps(data).encode("utf-8"))
        return str(path)

    def copy(self, path: str) -> str:
        """The same bytes at a new path: every fetch is its own file."""
        return self.file(raw=Path(path).read_bytes())

    def args(self, *args: str, review_comments: bool = True, after: bool = True) -> tuple[int, str]:
        """Run main(). Unless the test passes its own or opts out, an empty --review-comments list is added,
        and each list's second fetch is a copy of its first: nothing was posted while the lists were fetched."""
        if review_comments and "--review-comments" not in args:
            args = (*args, "--review-comments", self.file([]))
        if after:
            for first, again in (("--reviews", "--reviews-after"), ("--comments", "--comments-after"),
                                 ("--review-comments", "--review-comments-after")):
                if again not in args:
                    files = [args[i + 1] for i, a in enumerate(args[:-1]) if a == first]
                    args = (*args, *[part for f in files for part in (again, self.copy(f))])
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                code = counter.main(list(args))
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue()

    def __call__(self, posts: list, review_comments=None) -> tuple[int, str]:
        """Split posts the way the GitHub API serves them and pass each list to its option."""
        inline = [p for p in posts if any(k in p for k in INLINE_KEYS)]
        reviews = [p for p in posts if "state" in p]
        comments = [p for p in posts if p not in inline and p not in reviews]
        # Each list goes in as a one-page --paginate --slurp list, which shows it is complete.
        args = ["--reviews", self.file([reviews]), "--comments", self.file([comments]),
                "--review-comments", self.file(review_comments if review_comments is not None else [inline])]
        return self.args(*args)


class RealShapeTests(unittest.TestCase):
    def setUp(self):
        self.run = Run(self)

    def test_two_real_reviews_and_the_summary_use_two_rounds(self):
        # The order of PR 198 in Shipping_Inspection: request, summary created,
        # review; request, no-findings comment; the owner's own reviews.
        comments = [ask(1, 12), comment(2, BOT, SUMMARY, at(13)), ask(3, 21),
                    comment(4, BOT, clean_body("7e7d3da508"), at(24, 15))]
        reviews = [bot_review(10, 16), review(11, OWNER, "", at(21)), review(12, OWNER, "Final review, approve.", at(35))]
        code, out = self.run(reviews + comments)
        self.assertEqual(code, 0, out)
        self.assertIn("2 review round(s) used", out)
        self.assertIn("not counted: gh:2 -- review-status summary comment", out)
        self.assertIn("round 2: gh:4 commit 7e7d3da508", out)

    def test_three_real_reviews_are_counted_without_a_limit_and_the_summary_does_not_add_a_fourth(self):
        posts = [ask(1, 1), comment(2, BOT, SUMMARY, at(1, 20)), bot_review(10, 5),
                 ask(3, 10), bot_review(11, 14), ask(4, 20), bot_review(12, 25)]
        code, out = self.run(posts)
        self.assertEqual(code, 0, out)
        self.assertIn("3 review round(s) used", out)
        self.assertNotIn("LIMIT", out)
        self.assertNotIn("round 4", out)

    def test_many_more_than_three_reviews_still_exit_zero(self):
        """The cap of three was removed on 2026-10-12: the count is information and gates nothing."""
        posts = []
        for n in range(6):
            posts += [ask(1 + n, 1 + 10 * n), bot_review(10 + n, 5 + 10 * n)]
        code, out = self.run(posts)
        self.assertEqual(code, 0, out)
        self.assertIn("6 review round(s) used, no limit", out)
        self.assertIn("OK: no review-round limit", out)
        self.assertNotIn("LIMIT", out)

    def test_two_reviews_and_the_summary_count_two_rounds_not_three(self):
        # PR 194's state before its third round: the old counter said 3 here, the summary comment taken for a round.
        posts = [ask(1, 1), comment(2, BOT, SUMMARY, at(1, 20)), bot_review(10, 5), ask(3, 10), bot_review(11, 14)]
        code, out = self.run(posts)
        self.assertEqual(code, 0, out)
        self.assertIn("2 review round(s) used", out)
        self.assertIn("OK: no review-round limit", out)
        self.assertIn("answers request gh:3", out)
        self.assertNotIn("no answer yet", out)


class SelfStartedReviewTests(unittest.TestCase):
    def setUp(self):
        self.run = Run(self)

    def test_the_review_codex_runs_when_the_pr_opens_does_not_count(self):
        posts = [bot_review(10, 0), ask(1, 5), bot_review(11, 8), ask(2, 10), bot_review(12, 14)]
        code, out = self.run(posts)
        self.assertEqual(code, 0, out)
        self.assertIn("2 review round(s) used", out)
        self.assertIn("not counted: gh:10", out)

    def test_three_requested_reviews_after_the_opening_run_are_counted_and_the_opening_run_is_not(self):
        posts = [bot_review(10, 0), ask(1, 5), bot_review(11, 8), ask(2, 10), bot_review(12, 14),
                 ask(3, 20), bot_review(13, 24)]
        code, out = self.run(posts)
        self.assertEqual(code, 0, out)
        self.assertIn("3 review round(s) used", out)

    def test_a_request_racing_the_opening_run_makes_it_count(self):
        # Nothing tells the two runs apart once a request came first, so both
        # count: the error is towards counting.
        posts = [ask(1, 1), bot_review(10, 2), bot_review(11, 6)]
        code, out = self.run(posts)
        self.assertIn("2 review round(s) used", out)

    def test_a_review_codex_runs_on_a_comment_without_a_mention_counts(self):
        # Shipping_Inspection PR 105: a triage comment with no mention, then a
        # full review from Codex two minutes later.
        posts = [ask(1, 1), bot_review(10, 3), comment(2, OWNER, "Triage: two findings accepted.", at(7)),
                 comment(3, BOT, clean_body("abcdef1234"), at(9))]
        code, out = self.run(posts)
        self.assertIn("2 review round(s) used", out)
        self.assertIn("round 2: gh:3 commit abcdef1234 -- no request pending", out)

    def test_an_opening_run_that_ended_in_an_error_uses_the_exemption_up(self):
        posts = [comment(2, BOT, "To use Codex here, create a Codex account and connect to GitHub.", at(0)),
                 bot_review(10, 6)]
        code, out = self.run(posts)
        self.assertIn("1 review round(s) used", out)
        self.assertIn("round 1: gh:10", out)

    def test_the_summary_comment_does_not_use_the_opening_exemption_up(self):
        posts = [comment(2, BOT, SUMMARY, at(0)), bot_review(10, 3), ask(1, 5), bot_review(11, 8)]
        code, out = self.run(posts)
        self.assertIn("1 review round(s) used", out)
        self.assertIn("not counted: gh:10", out)

    def test_a_counted_review_ends_the_opening_exemption(self):
        # No human post in between: only the counted review can end the exemption here.
        posts = [ask(1, 1), bot_review(10, 3), comment(3, BOT, clean_body("abcdef1234"), at(9))]
        code, out = self.run(posts)
        self.assertIn("2 review round(s) used", out)

    def test_only_one_opening_run_is_left_out(self):
        posts = [bot_review(10, 0), bot_review(11, 2), ask(1, 5), bot_review(12, 8)]
        code, out = self.run(posts)
        self.assertIn("2 review round(s) used", out)
        self.assertIn("not counted: gh:10", out)

    def test_a_first_review_after_a_human_post_is_not_the_opening_run(self):
        # The case Codex found: a human comment with no mention triggers the
        # first review on the PR; nothing tells it apart from the opening run
        # except that someone had posted, so it counts.
        posts = [comment(1, OWNER, "Context for reviewers.", at(0)), bot_review(10, 3)]
        code, out = self.run(posts)
        self.assertIn("1 review round(s) used", out)

    def test_a_human_post_in_the_same_second_as_the_first_review_goes_first(self):
        # Listed after the review, as the reviews are read before the comments; the tie
        # still puts the person first, so the review counts.
        code, out = self.run([bot_review(10, 5), comment(1, OWNER, "Context, no mention.", at(5))])
        self.assertIn("1 review round(s) used", out)

    def test_two_bot_posts_in_the_same_second_put_the_notice_first(self):
        # Order between two bot posts of one second must not follow input order.
        for posts in ([bot_review(10, 5), comment(2, BOT, "On it", at(5))],
                      [comment(2, BOT, "To use Codex here, create a Codex account and connect to GitHub.", at(5)),
                       bot_review(10, 5)]):
            with self.subTest(first=posts[0]["id"]):
                code, out = self.run(posts)
                self.assertIn("1 review round(s) used", out)

    def test_a_result_and_a_notice_in_one_list_count_in_either_order(self):
        # A tie inside one list, where input order is the list's own order.
        result = comment(3, BOT, clean_body("abcdef1234"), at(5))
        for notice in ("On it", "Something went wrong. Try again later."):
            for posts in ([result, comment(2, BOT, notice, at(5))], [comment(2, BOT, notice, at(5)), result]):
                with self.subTest(notice=notice, first=posts[0]["id"]):
                    code, out = self.run(posts)
                    self.assertIn("1 review round(s) used", out)

    def test_an_unrecognized_post_in_the_same_second_as_the_first_review_makes_both_count(self):
        result = comment(3, BOT, clean_body("abcdef1234"), at(5))
        for posts in ([result, comment(2, BOT, "Codex is thinking about this.", at(5))],
                      [comment(2, BOT, "Codex is thinking about this.", at(5)), result]):
            with self.subTest(first=posts[0]["id"]):
                code, out = self.run(posts)
                self.assertIn("2 review round(s) used", out)

    def test_a_fraction_of_a_second_does_not_put_a_review_before_its_request(self):
        # 14:05:05.900 and 14:05:05 are one second; within it the request goes first.
        posts = [comment(1, OWNER, "@codex review", "2026-10-01T14:05:05.900Z"),
                 review(10, BOT, review_body("abcdef1234"), at(5, 5))]
        code, out = self.run(posts)
        self.assertIn("1 review round(s) used", out)
        self.assertIn("round 1: gh:10 commit d08b230db2 -- answers request gh:1", out)

    def test_a_human_post_seen_only_in_a_thread_ends_the_opening_exemption(self):
        thread = {"id": 60, "user": {"login": OWNER}, "path": "a.py", "pull_request_review_id": 9,
                  "body": "Is this branch reachable?", "created_at": at(2),
                  "html_url": "https://github.com/o/r/pull/1#discussion_r60"}
        code, out = self.run([thread, bot_review(10, 5)])
        self.assertIn("1 review round(s) used", out)

    def test_a_request_and_its_review_in_the_same_second_count(self):
        posts = [bot_review(10, 5), ask(1, 5)]
        code, out = self.run(posts)
        self.assertIn("1 review round(s) used", out)
        self.assertIn("round 1: gh:10 commit d08b230db2 -- answers request gh:1", out)


class NotARoundTests(unittest.TestCase):
    def setUp(self):
        self.run = Run(self)

    def assert_not_counted(self, body: str, reason: str):
        posts = [ask(1, 1), comment(2, BOT, body, at(2)), bot_review(10, 6)]
        code, out = self.run(posts)
        self.assertIn("1 review round(s) used", out)
        self.assertIn(f"not counted: gh:2 -- {reason}", out)

    def test_a_usage_limit_message_is_not_a_round(self):
        self.assert_not_counted("You have reached your Codex usage limits for code reviews.", "usage-limit")

    def test_an_account_error_is_not_a_round(self):
        self.assert_not_counted("To use Codex here, create a Codex account and connect to GitHub.", "error or setup")

    def test_an_acknowledgement_is_not_a_round(self):
        self.assert_not_counted("On it", "acknowledgement or task link")

    def test_a_view_task_share_link_is_not_a_round(self):
        # The exact post Codex left on Shipping_Inspection PR 205 before its review.
        self.assert_not_counted("\n\n [View task \u2192](https://chatgpt.com/s/cd_6abf0847643481918695001cdea63390)",
                                "acknowledgement or task link")

    def test_a_task_link_is_not_a_round(self):
        self.assert_not_counted("[View task →](https://chatgpt.com/codex/tasks/task_e_abc123)",
                                "acknowledgement or task link")

    def test_every_listed_opening_is_a_notice(self):
        openings = {
            "usage-limit": ["You've reached your Codex usage limits for code reviews.", "you have hit your rate limit",
                            "You\u2019ve exceeded your usage limit.", "Codex usage limit reached.",
                            "\u26a0\ufe0f Usage limits exceeded"],
            "error or setup": ["To use Codex here create a Codex account and connect to GitHub.", "something went\nwrong",
                               "Codex ran into an error.", "Codex encountered an error.", "An error occurred."],
        }
        for reason, bodies in openings.items():
            for body in bodies:
                with self.subTest(body=body):
                    self.assert_not_counted(body, reason)

    def test_near_misses_of_the_openings_count(self):
        for body in ("Codex hit an error.", "You reached your usage limit.", "Sorry, something went wrong."):
            with self.subTest(body=body):
                code, out = self.run([comment(1, OWNER, "Context, no mention.", at(1)), comment(2, BOT, body, at(2))])
                self.assertIn("1 review round(s) used", out)
                self.assertIn("UNRECOGNIZED", out)

    def test_a_notice_of_exactly_the_short_limit_is_still_a_notice(self):
        opening = "Something went wrong. "
        body = opening + "x" * (counter.SHORT_NOTICE - len(opening))
        self.assertEqual(len(body), counter.SHORT_NOTICE)
        self.assert_not_counted(body + "\n\n" + ABOUT, "error or setup")

    def test_the_bots_inline_comments_belong_to_its_review(self):
        inline = {"id": 50, "user": {"login": BOT}, "path": "a.py", "diff_hunk": "@@", "pull_request_review_id": 10,
                  "body": "![P1 Badge](https://img.shields.io/badge/P1-orange) Fix this", "created_at": at(6)}
        code, out = self.run([ask(1, 1), bot_review(10, 6), inline])
        self.assertIn("1 review round(s) used", out)
        self.assertNotIn("gh:50", out)

    def test_mcp_review_threads_are_read_and_the_bots_thread_comments_skipped(self):
        threads = {"review_threads": [{"total_count": 2, "comments": [
            {"body": "![P2 Badge](https://img.shields.io/badge/P2-yellow) Qualify the claim", "path": "doc.md",
             "author": "chatgpt-codex-connector", "created_at": at(6),
             "html_url": "https://github.com/o/r/pull/1#discussion_r41"},
            {"body": "Fixed. @codex review", "path": "doc.md", "author": OWNER, "created_at": at(9),
             "html_url": "https://github.com/o/r/pull/1#discussion_r42"}]}], "pageInfo": {"hasNextPage": False}}
        code, out = self.run([ask(1, 1), bot_review(10, 6), bot_review(11, 12)], review_comments=threads)
        self.assertIn("2 review round(s) used", out)
        self.assertIn("answers request gh:42", out)
        self.assertNotIn("gh:41", out)


class StrictnessTests(unittest.TestCase):
    """A post that only looks harmless still counts: the safe direction is over-counting."""

    def setUp(self):
        self.run = Run(self)

    def test_a_summary_that_carries_a_result_counts(self):
        body = SUMMARY + "\n\n**Reviewed commit:** `7e7d3da508`\n"
        code, out = self.run([ask(1, 1), comment(2, BOT, body, at(3))])
        self.assertIn("round 1: gh:2", out)

    def test_a_summary_marker_not_at_the_start_is_unrecognized_and_counts(self):
        code, out = self.run([comment(2, BOT, " " + SUMMARY, at(3))])
        self.assertIn("round 1: gh:2 -- UNRECOGNIZED", out)
        self.assertIn("WARNING: 1 unrecognized", out)

    def test_an_unrecognized_bot_post_counts_even_with_no_request(self):
        code, out = self.run([ask(1, 1), bot_review(10, 3), ask(2, 4), bot_review(11, 6),
                              comment(5, BOT, "Some new kind of notice.", at(7))])
        self.assertEqual(code, 0, out)
        self.assertIn("3 review round(s) used", out)
        self.assertIn("unrecognized bot post(s) counted", out)

    def test_a_no_findings_verdict_without_a_commit_line_is_a_result(self):
        code, out = self.run([ask(1, 1), comment(2, BOT, "Codex Review: Didn’t find any major issues.", at(3))])
        self.assertIn("round 1: gh:2", out)

    def test_a_task_reply_with_content_counts(self):
        body = ("Reviewed the parser change: the retry loop can spin when the file is locked; "
                "I ran the tests and two fail.\n\n[View task \u2192](https://chatgpt.com/codex/tasks/task_e_abc123)")
        code, out = self.run([ask(1, 1), comment(2, BOT, body, at(3))])
        self.assertIn("round 1: gh:2 -- UNRECOGNIZED", out)

    def test_limit_or_error_words_inside_a_post_do_not_make_it_a_non_result(self):
        for body in ("Codex Review: Here are some suggestions. The retry logic ignores the rate limit.",
                     "**P1** Handle the case where the task failed silently\n\nSomething went wrong upstream.",
                     "Codex Review: once you have reached your usage limit the client retries forever."):
            with self.subTest(body=body[:30]):
                code, out = self.run([ask(1, 1), comment(2, BOT, body, at(3))])
                self.assertIn("round 1: gh:2 -- UNRECOGNIZED", out)

    def test_a_long_post_that_opens_with_an_error_is_not_a_notice(self):
        body = ("Something went wrong running the test suite, so this review is from reading the diff. "
                + "The parser retries forever when the input file is locked; the lock is never released "
                * 5)
        code, out = self.run([ask(1, 1), comment(2, BOT, body, at(3))])
        self.assertIn("round 1: gh:2 -- UNRECOGNIZED", out)

    def test_a_short_error_opening_with_a_result_marker_is_a_result(self):
        for body in ("Something went wrong with one check.\n\n**Reviewed commit:** `abcdef1234`",
                     "Something went wrong with one check. Codex Review: Didn't find any major issues.",
                     "An error occurred in one job. ![P1 Badge](https://img.shields.io/badge/P1-orange) Fix the lock."):
            with self.subTest(body=body[:40]):
                code, out = self.run([ask(1, 1), comment(2, BOT, body, at(3))])
                self.assertIn("round 1: gh:2", out)

    def test_a_result_that_also_mentions_a_quota_is_still_a_result(self):
        body = clean_body("abcdef1234") + "\nYou are close to your usage limits."
        code, out = self.run([ask(1, 1), comment(2, BOT, body, at(3))])
        self.assertIn("round 1: gh:2", out)

    def test_a_bot_review_submission_is_always_a_result(self):
        posts = [ask(1, 1), review(10, BOT, "", at(3))]
        code, out = self.run(posts)
        self.assertIn("round 1: gh:10", out)

    def test_a_notice_one_character_over_the_limit_counts(self):
        opening = "Something went wrong. "
        body = opening + "x" * (counter.SHORT_NOTICE + 1 - len(opening))
        code, out = self.run([comment(1, OWNER, "Context, no mention.", at(1)), comment(2, BOT, body, at(2))])
        self.assertIn("1 review round(s) used", out)
        self.assertIn("UNRECOGNIZED", out)

    def test_only_the_about_footer_is_set_aside_when_a_notice_is_measured(self):
        body = ("Something went wrong while posting part of this review.\n\n<details><summary>Notes</summary>\n\n"
                + "The handler drops the last page when the list is full. " * 10 + "\n</details>")
        code, out = self.run([comment(1, OWNER, "Context, no mention.", at(1)), comment(2, BOT, body, at(2))])
        self.assertIn("1 review round(s) used", out)
        self.assertIn("UNRECOGNIZED", out)

    def test_a_summary_holding_more_than_its_table_counts(self):
        body = SUMMARY.replace("\n\n\n\n<details>", "\n\nThe handler drops the last page when the list is full.\n\n<details>")
        self.assertNotEqual(body, SUMMARY)
        code, out = self.run([comment(2, BOT, body, at(1)), ask(1, 2), bot_review(10, 5)])
        self.assertIn("2 review round(s) used", out)
        self.assertIn("round 1: gh:2 -- UNRECOGNIZED", out)

    def test_a_summary_with_another_heading_or_sentence_counts(self):
        for old, new in (("## Codex Review Summary", "## Codex Review Status"),
                         ("This comment shows the latest Codex review activity on this pull request.",
                          "This comment shows what Codex found on this pull request.")):
            with self.subTest(new=new):
                code, out = self.run([comment(2, BOT, SUMMARY.replace(old, new), at(1))])
                self.assertIn("round 1: gh:2 -- UNRECOGNIZED", out)

    def test_a_summary_without_its_about_footer_is_still_a_summary(self):
        body = SUMMARY.replace(ABOUT, "")
        self.assertNotEqual(body, SUMMARY)
        code, out = self.run([comment(2, BOT, body, at(1)), bot_review(10, 5)])
        self.assertIn("0 review round(s) used", out)
        self.assertIn("not counted: gh:2 -- review-status summary comment", out)

    def test_another_bot_posting_what_codex_posts_is_refused(self):
        for body in (review_body("abcdef1234"), SUMMARY):
            with self.subTest(body=body[:20]):
                code, out = self.run([ask(1, 1), comment(2, "review-helper[bot]", body, at(3))])
                self.assertEqual(code, 2, out)
                self.assertIn("posts what Codex posts", out)

    def test_another_bot_posting_a_result_is_refused(self):
        result = "**Reviewed commit:** `abcdef1234`\n\nLooks fine."
        posts = ([comment(2, "review-helper[bot]", result, at(3))],
                 [comment(3, "app/review-helper", result, at(3))],
                 [dict(comment(4, "review-helper", result, at(3)), user={"login": "review-helper", "type": "Bot"})],
                 [dict(comment(5, "review-helper", result, at(3)), user=None,
                       author={"login": "review-helper", "is_bot": True})],
                 [review(10, "review-helper[bot]", "![P1 Badge](https://img.shields.io/badge/P1-orange) Fix", at(3))])
        for extra in posts:
            with self.subTest(first=extra[0]["id"]):
                code, out = self.run([ask(1, 1), *extra])
                self.assertEqual(code, 2, out)
                self.assertIn("posts what Codex posts", out)

    def test_another_bot_without_a_result_is_a_person(self):
        other = review(10, "copilot-pull-request-reviewer[bot]", "Copilot reviewed 2 out of 2 changed files.", at(3))
        code, out = self.run([other, bot_review(11, 5)])
        self.assertEqual(code, 0, out)
        self.assertIn("1 review round(s) used", out)

    def test_a_person_quoting_the_codex_footer_is_a_person(self):
        code, out = self.run([comment(1, OWNER, "Their footer says:\n\n" + ABOUT, at(1)), bot_review(10, 5)])
        self.assertEqual(code, 0, out)
        self.assertIn("1 review round(s) used", out)

    def test_a_login_that_only_looks_like_the_bot_is_refused(self):
        # Neither counted as the bot nor ignored: the count cannot tell, so it stops.
        body = "Codex Review: Didn't find any major issues.\n\n**Reviewed commit:** `abcdef1234`"
        for login in ("chatgpt-codex-connector-fake", "chatgpt-codex-connector-v2", "codex-bot"):
            with self.subTest(login=login):
                code, out = self.run([comment(2, login, body, at(3)), ask(1, 1)])
                self.assertEqual(code, 2, out)
                self.assertIn("looks like Codex", out)

    def test_the_bot_login_is_matched_without_regard_to_case(self):
        code, out = self.run([ask(1, 1), comment(2, "ChatGPT-Codex-Connector[bot]", clean_body("abcdef1234"), at(3))])
        self.assertIn("round 1: gh:2", out)


class RequestTests(unittest.TestCase):
    def setUp(self):
        self.run = Run(self)

    def test_a_mention_anywhere_opens_a_request(self):
        for text in ("Please look again: `@codex review`", "@Codex review", "@codex security review",
                     "@codex review for regressions in the parser"):
            with self.subTest(text=text):
                code, out = self.run([comment(1, OWNER, text, at(1)), bot_review(10, 3)])
                self.assertIn("1 review round(s) used", out)

    def test_a_persons_review_that_mentions_codex_is_a_request(self):
        code, out = self.run([review(5, OWNER, "Changes look fine. @codex review", at(1)), bot_review(10, 3)])
        self.assertIn("1 review round(s) used", out)
        self.assertIn("round 1: gh:10 commit d08b230db2 -- answers request gh:5", out)

    def test_a_request_in_a_review_between_the_fetches_stops_the_count(self):
        # A review body request posted after the first fetch of the reviews and
        # answered by a comment before the comments were fetched: only the second
        # fetch of the reviews shows it.
        code, out = self.run.args("--reviews", self.run.file([[]]),
                                  "--comments", self.run.file([[comment(2, BOT, clean_body("abcdef1234"), at(3))]]),
                                  "--reviews-after", self.run.file([[review(5, OWNER, "@codex review", at(1))]]))
        self.assertEqual(code, 2, out)
        self.assertIn("the reviews changed while the lists were fetched (pullrequestreview:5)", out)

    def test_a_security_review_counts_like_any_other(self):
        posts = [ask(1, 1), bot_review(10, 3), ask(2, 4), bot_review(11, 6),
                 ask(3, 7, "@codex security review"), bot_review(12, 9)]
        code, out = self.run(posts)
        self.assertEqual(code, 0, out)
        self.assertIn("3 review round(s) used", out)

    def test_the_bots_own_mention_of_the_trigger_is_not_a_request(self):
        # The summary's About block quotes the trigger; it must not turn the
        # next self-started run into a counted round.
        # The review body is empty so that only the summary carries a mention.
        code, out = self.run([comment(2, BOT, SUMMARY, at(1)), review(10, BOT, "", at(3))])
        self.assertIn("0 review round(s) used", out)

    def test_a_notice_answers_a_request_and_a_later_review_still_counts(self):
        posts = [ask(1, 1), comment(2, BOT, "You have reached your Codex usage limits.", at(2)), bot_review(10, 30)]
        code, out = self.run(posts)
        self.assertIn("1 review round(s) used", out)
        self.assertIn("usage-limit message, answers request gh:1", out)
        self.assertIn("round 1: gh:10 commit d08b230db2 -- no request pending", out)

    def test_a_request_answered_only_by_a_notice_is_not_a_round(self):
        for notice in ("You have reached your Codex usage limits.", "Something went wrong. Try again later."):
            with self.subTest(notice=notice):
                code, out = self.run([ask(1, 1), comment(2, BOT, notice, at(2))])
                self.assertEqual(code, 0, out)
                self.assertIn("0 review round(s) used", out)

    def test_a_request_with_no_answer_yet_counts_as_a_run_in_progress(self):
        # The run may land after the lists were fetched, or leave only a reaction.
        # An "On it" or a task link is not an answer: Codex is still working.
        for posts in ([ask(1, 1)], [comment(2, BOT, SUMMARY, at(1)), ask(1, 2), comment(3, BOT, "On it", at(3))]):
            with self.subTest(posts=len(posts)):
                code, out = self.run(posts)
                self.assertIn("1 review round(s) used", out)
                self.assertIn("round 1: gh:1 -- request with no answer yet, counted as a run in progress", out)

    def test_a_review_that_landed_after_the_reviews_were_fetched_counts_through_its_request(self):
        # Two rounds done; the third request's review is not in the reviews list yet.
        posts = [ask(1, 1), bot_review(10, 3), ask(2, 5), bot_review(11, 7), ask(3, 9)]
        code, out = self.run(posts)
        self.assertEqual(code, 0, out)
        self.assertIn("3 review round(s) used", out)
        self.assertIn("request with no answer yet", out)

    def test_an_unrecognized_post_answers_no_request(self):
        # If it is not the answer, the run still in progress counts as well.
        code, out = self.run([ask(1, 1), comment(2, BOT, "Codex is thinking about this.", at(2))])
        self.assertIn("2 review round(s) used", out)
        self.assertIn("gh:1 -- request with no answer yet", out)

    def test_the_oldest_open_request_is_answered_first_and_the_rest_count(self):
        code, out = self.run([ask(1, 1), ask(2, 2), bot_review(10, 3)])
        self.assertIn("2 review round(s) used", out)
        self.assertIn("round 1: gh:10 commit d08b230db2 -- answers request gh:1", out)
        self.assertIn("round 2: gh:2 -- request with no answer yet", out)

    def test_a_request_after_the_opening_run_counts_until_answered(self):
        code, out = self.run([bot_review(10, 1), ask(1, 3)])
        self.assertIn("1 review round(s) used", out)
        self.assertIn("not counted: gh:10", out)
        self.assertIn("round 1: gh:1 -- request with no answer yet", out)

    def test_a_mention_inside_a_longer_handle_opens_no_request(self):
        code, out = self.run([comment(1, OWNER, "Thanks @codexfan review and email@codex review", at(1))])
        self.assertIn("0 review round(s) used", out)

    def test_a_hyphenated_handle_is_another_account_not_a_request(self):
        # GitHub handles may hold "-": @codex-bot is another user, and an unanswered
        # request for it would add a phantom round in progress.
        for text in ("cc @codex-review", "thanks @CODEX-review!"):
            with self.subTest(text=text):
                code, out = self.run([comment(1, OWNER, text, at(1))])
                self.assertIn("0 review round(s) used", out)
        code, out = self.run([comment(1, OWNER, "@CODEX review, please.", at(1))])
        self.assertIn("1 review round(s) used", out)

    def test_a_task_request_on_the_pr_is_not_a_pending_review(self):
        # A FIX task (section 13) is answered with a task link and commits, never a review:
        # as a review request it would stay open and pair with the next review instead.
        fix = comment(1, OWNER, "@codex\n\nMODE: FIX\n\nFix the confirmed P1 finding.", at(1))
        task = comment(2, BOT, "[View task \u2192](https://chatgpt.com/s/cd_123)", at(2))
        code, out = self.run([fix, task, ask(3, 5), bot_review(10, 8)])
        self.assertIn("1 review round(s) used", out)
        self.assertIn("round 1: gh:10 commit d08b230db2 -- answers request gh:3", out)
        code, out = self.run([fix, task])
        self.assertIn("0 review round(s) used", out)

    def test_a_task_request_still_ends_the_opening_exemption(self):
        fix = comment(1, OWNER, "@codex please fix the failing test", at(1))
        code, out = self.run([fix, bot_review(10, 5)])
        self.assertIn("1 review round(s) used", out)
        self.assertIn("round 1: gh:10 commit d08b230db2 -- no request pending", out)

    def test_a_post_without_a_mention_opens_no_request_but_ends_the_opening_exemption(self):
        # Codex also runs on comments that never mention it, so a review that
        # follows any human post may have been triggered by it: it counts.
        code, out = self.run([comment(1, OWNER, "codex review would be nice", at(1)), bot_review(10, 3)])
        self.assertIn("1 review round(s) used", out)
        self.assertIn("round 1: gh:10 commit d08b230db2 -- no request pending", out)


class InputShapeTests(unittest.TestCase):
    def setUp(self):
        self.run = Run(self)

    def test_gh_and_graphql_field_names_are_read(self):
        reviews = [{"id": "PRR_kw1", "author": {"login": "chatgpt-codex-connector"}, "body": review_body("d08b230db2"),
                    "state": "COMMENTED", "submittedAt": at(5), "commit": {"oid": "d08b230db208db98a766"}}]
        comments = [{"id": "IC_kw1", "author": {"login": OWNER}, "body": "@codex review", "createdAt": at(1),
                     "url": "https://github.com/o/r/pull/1#issuecomment-901"},
                    {"id": "IC_kw2", "author": {"login": "chatgpt-codex-connector"}, "body": SUMMARY,
                     "createdAt": at(2), "url": "https://github.com/o/r/pull/1#issuecomment-902"}]
        code, out = self.run.args("--reviews", self.run.file([reviews]), "--comments", self.run.file([comments]))
        self.assertIn("1 review round(s) used", out)
        self.assertIn("round 1: gh:PRR_kw1 commit d08b230db2 -- answers request gh:901", out)

    def test_app_slash_login_is_the_bot(self):
        post = comment(2, "app/chatgpt-codex-connector", clean_body("abcdef1234"), at(3))
        code, out = self.run([ask(1, 1), post])
        self.assertIn("round 1: gh:2", out)

    def test_the_same_posts_passed_twice_count_once(self):
        posts = [ask(1, 1), bot_review(10, 3)]
        code, out = self.run(posts + posts)
        self.assertIn("1 review round(s) used", out)

    def test_fractional_and_offset_timestamps_order_correctly(self):
        posts = [comment(1, OWNER, "@codex review", "2026-10-01T23:30:00.5+09:00"),
                 review(10, BOT, review_body("abcdef1234"), "2026-10-01T14:31:00Z")]
        code, out = self.run(posts)
        self.assertIn("1 review round(s) used", out)

    def test_utf16_and_utf8_bom_files_are_read(self):
        text = json.dumps([[ask(1, 1)]], ensure_ascii=False)
        for raw in (b"\xef\xbb\xbf" + text.encode("utf-8"), text.encode("utf-16")):
            with self.subTest(prefix=raw[:3]):
                code, out = self.run.args("--reviews", self.run.file([[bot_review(10, 3)]]),
                                          "--comments", self.run.file(raw=raw))
                self.assertIn("1 review round(s) used", out)

    def test_paginated_slurp_pages_are_flattened(self):
        pages = [[bot_review(10, 3)], [bot_review(11, 6)]]
        code, out = self.run.args("--reviews", self.run.file(pages), "--comments", self.run.file([[ask(1, 1), ask(2, 4)]]))
        self.assertIn("2 review round(s) used", out)

    def test_one_file_per_page_is_accepted_with_the_empty_page_after_them(self):
        code, out = self.run.args("--reviews", self.run.file([bot_review(10, 3)]),
                                  "--reviews", self.run.file([bot_review(11, 6)]), "--reviews", self.run.file([]),
                                  "--comments", self.run.file([ask(1, 1), ask(2, 4)]), "--comments", self.run.file([]))
        self.assertEqual(code, 0, out)
        self.assertIn("2 review round(s) used", out)

    def test_a_flat_list_without_its_empty_next_page_is_refused(self):
        for size in (1, 20, 30):
            with self.subTest(size=size):
                page = [ask(1, 1)] + [comment(100 + i, OWNER, "noted", at(30, i)) for i in range(size - 1)]
                code, out = self.run.args("--reviews", self.run.file([]), "--comments", self.run.file(page))
                self.assertEqual(code, 2, out)
                self.assertIn("does not show it is the last page", out)

    def test_the_last_file_of_an_option_decides_whether_the_list_is_complete(self):
        code, out = self.run.args("--reviews", self.run.file([[]]), "--comments", self.run.file([[ask(1, 1)]]),
                                  "--comments", self.run.file([comment(2, OWNER, "Noted.", at(2))]))
        self.assertEqual(code, 2, out)
        self.assertIn("last page", out)

    def test_the_next_page_or_a_slurped_list_proves_the_end(self):
        page = [comment(100 + i, OWNER, "noted", at(30, i)) for i in range(29)] + [ask(1, 1)]
        for args in (("--comments", self.run.file(page), "--comments", self.run.file([])),
                     ("--comments", self.run.file([page]))):
            with self.subTest(form=len(args)):
                code, out = self.run.args("--reviews", self.run.file([[bot_review(10, 3)]]), *args)
                self.assertEqual(code, 0, out)
                self.assertIn("1 review round(s) used", out)

    def test_mcp_review_threads_without_a_last_page_proof_are_refused(self):
        for threads in ({"review_threads": [], "pageInfo": {"hasNextPage": True}}, {"review_threads": []}):
            with self.subTest(threads=threads):
                code, out = self.run([ask(1, 1)], review_comments=threads)
                self.assertEqual(code, 2, out)
                self.assertIn("does not show it is the last page", out)

    def test_ids_from_different_lists_do_not_collide(self):
        # Review 777 and issue comment 777 are two results; merging them under
        # one key would hide a real round.
        posts = [ask(1, 1), review(777, BOT, "", at(3)), ask(2, 4), comment(777, BOT, clean_body("abcdef1234"), at(6))]
        code, out = self.run(posts)
        self.assertIn("2 review round(s) used", out)
        self.assertIn("round 2: gh:777 commit abcdef1234 -- answers request gh:2", out)


class InputErrorTests(unittest.TestCase):
    def setUp(self):
        self.run = Run(self)

    def assert_input_error(self, *, data=None, raw: bytes | None = None, fragment: str, option: str = "--comments"):
        files = {"--reviews": self.run.file([]), "--comments": self.run.file([])}
        files[option] = self.run.file(data, raw=raw)
        code, out = self.run.args(*[part for pair in files.items() for part in pair])
        self.assertEqual(code, 2, out)
        self.assertIn("INPUT ERROR", out)
        self.assertIn(fragment, out)
        self.assertNotIn("OK: no review-round limit", out)

    def test_a_post_without_a_login_is_an_error(self):
        self.assert_input_error(data=[{"id": 1, "body": "@codex review", "created_at": at(1)}], fragment="user.login")

    def test_a_bot_post_without_a_timestamp_is_an_error(self):
        self.assert_input_error(data=[{"id": 1, "user": {"login": BOT}, "body": "x"}], fragment="timestamp")

    def test_an_impossible_timestamp_is_an_error_not_a_crash(self):
        for stamp in ("2026-13-45T00:00:00Z", "2026-01-01T24:00:00Z", "2026-01-01T00:00:00+99:00"):
            with self.subTest(stamp=stamp):
                self.assert_input_error(data=[comment(1, OWNER, "@codex review", stamp)], fragment="timestamp")

    def test_broken_json_is_an_error(self):
        self.assert_input_error(raw=b"[{", fragment="not valid JSON")

    def test_an_empty_file_is_an_error_not_zero_rounds(self):
        self.assert_input_error(raw=b"  \n", fragment="empty")

    def test_undecodable_bytes_are_an_error(self):
        self.assert_input_error(raw=b"[\xff\xfe\xfd]", fragment="neither UTF-8")

    def test_an_object_of_the_wrong_shape_is_an_error(self):
        self.assert_input_error(data={"items": []}, fragment="expected a list")

    def test_reviews_passed_as_comments_are_an_error(self):
        self.assert_input_error(data=[bot_review(10, 3)], fragment="not one of the issue comments")

    def test_inline_comments_passed_as_issue_comments_are_an_error(self):
        inline = {"id": 5, "user": {"login": BOT}, "path": "a.py", "body": "![P1 Badge](x)", "created_at": at(3)}
        self.assert_input_error(data=[inline], fragment="not one of the issue comments")

    def test_a_thread_missing_some_of_its_comments_is_an_error(self):
        threads = {"review_threads": [{"total_count": 3, "comments": [
            {"body": "@codex review", "path": "a.py", "author": OWNER, "created_at": at(1),
             "html_url": "https://github.com/o/r/pull/1#discussion_r41"}]}], "pageInfo": {"hasNextPage": False}}
        code, out = self.run([bot_review(10, 5)], review_comments=threads)
        self.assertEqual(code, 2, out)
        self.assertIn("holds 1 of its 3 comments", out)

    def test_a_thread_without_a_valid_comment_count_is_an_error(self):
        # The page of threads can be complete while a thread's own comments are not:
        # without its count, a cut thread could hide a request.
        comment_41 = {"body": "@codex review", "path": "a.py", "author": OWNER, "created_at": at(1),
                      "html_url": "https://github.com/o/r/pull/1#discussion_r41"}
        for count in (None, "1", True, -1):
            with self.subTest(count=count):
                thread = {"comments": [comment_41]} if count is None else {"total_count": count, "comments": [comment_41]}
                threads = {"review_threads": [thread], "pageInfo": {"hasNextPage": False}}
                code, out = self.run([bot_review(10, 5)], review_comments=threads)
                self.assertEqual(code, 2, out)
                self.assertIn("has no comment count (total_count)", out)

    def test_a_review_with_neither_an_id_nor_a_url_is_an_error(self):
        anonymous = {"user": {"login": BOT}, "body": review_body("abcdef1234"), "state": "COMMENTED",
                     "submitted_at": at(3)}
        self.assert_input_error(data=[[anonymous]], fragment="neither an id nor a URL", option="--reviews")

    def test_issue_comments_or_reviews_passed_as_review_comments_are_an_error(self):
        for data in ([ask(1, 1)], [bot_review(10, 3)]):
            with self.subTest(first=data[0]["id"]):
                self.assert_input_error(data=data, fragment="not one of the review-thread comments",
                                        option="--review-comments")

    def test_a_codex_inline_comment_newer_than_every_review_is_refused(self):
        inline = {"id": 50, "user": {"login": BOT}, "path": "a.py", "pull_request_review_id": 11,
                  "body": "![P1 Badge](https://img.shields.io/badge/P1-orange) Fix this", "created_at": at(9),
                  "html_url": "https://github.com/o/r/pull/1#discussion_r50"}
        for reviews in ([bot_review(10, 6)], []):
            with self.subTest(reviews=len(reviews)):
                code, out = self.run([ask(1, 1), *reviews, inline])
                self.assertEqual(code, 2, out)
                self.assertIn("newer than every Codex review", out)

    def test_inline_comments_stamped_just_after_their_review_belong_to_it(self):
        """PR 31's real shape: the review at :16, its inline comments a second later."""
        for second in (1, 59):
            inline = {"id": 50, "user": {"login": BOT}, "path": "a.py", "pull_request_review_id": 10,
                      "body": "![P1 Badge](https://img.shields.io/badge/P1-orange) Fix this", "created_at": at(6, second),
                      "html_url": "https://github.com/o/r/pull/1#discussion_r50"}
            with self.subTest(second=second):
                code, out = self.run([ask(1, 1), bot_review(10, 6), inline])
                self.assertEqual(code, 0, out)
                self.assertIn("1 review round(s) used", out)
        late = {"id": 51, "user": {"login": BOT}, "path": "a.py", "pull_request_review_id": 11,
                "body": "![P1 Badge](https://img.shields.io/badge/P1-orange) Fix this", "created_at": at(7, 1),
                "html_url": "https://github.com/o/r/pull/1#discussion_r51"}
        code, out = self.run([ask(1, 1), bot_review(10, 6), late])
        self.assertEqual(code, 2, out)
        self.assertIn("newer than every Codex review", out)

    def test_a_failure_inside_the_script_exits_2(self):
        from unittest import mock
        with mock.patch.object(counter, "count", side_effect=ValueError("boom")):
            code, out = self.run([ask(1, 1)])
        self.assertEqual(code, 2, out)
        self.assertIn("INTERNAL ERROR -- ValueError: boom", out)

    def test_comments_passed_as_reviews_are_an_error(self):
        self.assert_input_error(data=[ask(1, 1)], fragment="not one of the PR reviews", option="--reviews")

    def test_a_thread_with_no_comment_list_is_an_error(self):
        self.assert_input_error(data={"review_threads": [{"comments": None}]}, fragment="no list of comments",
                                option="--review-comments")

    def test_reviews_without_comments_are_refused(self):
        code, out = self.run.args("--reviews", self.run.file([bot_review(10, 3)]))
        self.assertEqual(code, 2, out)
        self.assertIn("both --reviews and --comments", out)

    def test_a_count_without_review_comments_is_refused(self):
        # A request posted in a thread that the count cannot see would make its
        # review pass for the uncounted opening run.
        code, out = self.run.args("--reviews", self.run.file([]), "--comments", self.run.file([]),
                                  "--review-comments-after", self.run.file([]), review_comments=False)
        self.assertEqual(code, 2, out)
        self.assertIn("give --review-comments too", out)

    def test_a_count_without_every_second_fetch_is_refused(self):
        lists = {"--reviews": self.run.file([[]]), "--comments": self.run.file([[]]),
                 "--review-comments": self.run.file([[]])}
        seconds = {flag + "-after": self.run.copy(f) for flag, f in lists.items()}
        for missing in seconds:
            with self.subTest(missing=missing):
                given = [part for flag, f in {**lists, **seconds}.items() if flag != missing for part in (flag, f)]
                code, out = self.run.args(*given, after=False)
                self.assertEqual(code, 2, out)
                self.assertIn("--comments-after", out)

    def test_one_file_named_for_both_fetches_is_refused(self):
        # A second fetch that rereads the first file proves nothing was posted meanwhile only by assumption.
        reviews = self.run.file([[]])
        code, out = self.run.args("--reviews", reviews, "--comments", self.run.file([[]]), "--reviews-after", reviews)
        self.assertEqual(code, 2, out)
        self.assertIn("are the same file", out)

    def test_another_spelling_of_one_file_is_the_same_file(self):
        comments = self.run.file([[ask(1, 1)]])
        link = str(Path(self.run.dir.name) / "link.json")
        os.link(comments, link)
        dotted = os.path.join(os.path.dirname(comments), ".", os.path.basename(comments))  # pathlib drops the "."
        for alias in (dotted, link):
            with self.subTest(alias=alias):
                code, out = self.run.args("--reviews", self.run.file([[]]), "--comments", comments,
                                          "--comments-after", alias)
                self.assertEqual(code, 2, out)
                self.assertIn("are the same file", out)

    def test_reviews_that_changed_between_the_fetches_are_refused(self):
        # A review that lands while the lists are fetched may answer a request
        # posted after the comments were read: the snapshot is not one moment.
        first, later = [[ask(1, 1)]], [[bot_review(10, 5)]]
        for before, after in (([[]], later), (later, [[]])):
            with self.subTest(added=before == [[]]):
                code, out = self.run.args("--reviews", self.run.file(before), "--comments", self.run.file(first),
                                          "--reviews-after", self.run.file(after))
                self.assertEqual(code, 2, out)
                self.assertIn("the reviews changed while the lists were fetched (pullrequestreview:10)", out)

    def test_a_post_edited_between_the_fetches_is_refused(self):
        # An edit keeps the post's id, so only its content shows it: a person's comment
        # that gains a mention, or the summary comment that gains a result.
        summary = comment(2, BOT, SUMMARY, at(2))
        with_result = comment(2, BOT, SUMMARY + "\n\n**Reviewed commit:** `abcdef1234`", at(2))
        mention_added = ([comment(1, OWNER, "looks good", at(1))], [comment(1, OWNER, "looks good @codex review", at(1))])
        for before, after in (mention_added, ([summary], [with_result])):
            with self.subTest(before=before[0]["body"][:20]):
                code, out = self.run.args("--reviews", self.run.file([[]]), "--comments", self.run.file([before]),
                                          "--comments-after", self.run.file([after]))
                self.assertEqual(code, 2, out)
                self.assertIn("(edited)", out)
                self.assertIn("the issue comments changed while the lists were fetched", out)

    def test_a_request_and_its_result_posted_while_the_lists_were_fetched_stop_the_count(self):
        # Posted after the first fetch of the comments, answered before the last
        # fetch: only the second fetch of the comments shows them (#205 round 1).
        late = [ask(3, 20), comment(4, BOT, clean_body("abcdef1234"), at(23))]
        code, out = self.run.args("--reviews", self.run.file([[]]), "--comments", self.run.file([[ask(1, 1)]]),
                                  "--comments-after", self.run.file([[ask(1, 1), *late]]))
        self.assertEqual(code, 2, out)
        self.assertIn("the issue comments changed while the lists were fetched (issuecomment:3, issuecomment:4)", out)

    def test_a_thread_request_posted_while_the_lists_were_fetched_stops_the_count(self):
        thread = {"id": 60, "user": {"login": OWNER}, "path": "a.py", "body": "@codex review", "created_at": at(9),
                  "html_url": "https://github.com/o/r/pull/1#discussion_r60"}
        code, out = self.run.args("--reviews", self.run.file([[]]), "--comments", self.run.file([[]]),
                                  "--review-comments", self.run.file([[]]),
                                  "--review-comments-after", self.run.file([[thread]]))
        self.assertEqual(code, 2, out)
        self.assertIn("the review comments changed while the lists were fetched (discussion_r:60)", out)

    def test_the_second_fetch_of_the_reviews_is_checked_like_the_first(self):
        for after, fragment in (([[ask(1, 1)]], "not one of the PR reviews"), ([bot_review(10, 5)], "last page")):
            with self.subTest(fragment=fragment):
                code, out = self.run.args("--reviews", self.run.file([[bot_review(10, 5)]]),
                                          "--comments", self.run.file([[]]), "--reviews-after", self.run.file(after))
                self.assertEqual(code, 2, out)
                self.assertIn(fragment, out)

    def test_a_missing_file_is_an_error(self):
        code, out = self.run.args("--reviews", str(Path(self.run.dir.name) / "absent.json"),
                                  "--comments", self.run.file([]), "--reviews-after", self.run.file([]))
        self.assertEqual(code, 2, out)
        self.assertIn("INPUT ERROR", out)
        self.assertIn("absent.json", out)


class CommandLineTests(unittest.TestCase):
    def test_non_ascii_input_on_a_cp1252_console_prints_ascii(self):
        comments = [[ask(1, 1), comment(2, BOT, SUMMARY, at(2))]]
        env = dict(os.environ, PYTHONIOENCODING="cp1252")
        tmp = Path(tempfile.mkdtemp())
        files = {"rv.json": [[bot_review(10, 3)]], "rc.json": [[]], "rv2.json": [[bot_review(10, 3)]], "rc2.json": [[]],
                 "c.json": comments, "c2.json": comments}
        for name, data in files.items():
            (tmp / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.addCleanup((tmp / name).unlink)
        result = subprocess.run([sys.executable, str(SCRIPT), "--reviews", str(tmp / "rv.json"),
                                 "--comments", str(tmp / "c.json"), "--review-comments", str(tmp / "rc.json"),
                                 "--reviews-after", str(tmp / "rv2.json"), "--comments-after", str(tmp / "c2.json"),
                                 "--review-comments-after", str(tmp / "rc2.json")],
                                capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(b"1 review round(s) used", result.stdout)
        result.stdout.decode("ascii")  # raises if anything non-ASCII was printed

    def test_stdin_is_refused(self):
        # A pipe cannot show which fetch it holds: `--reviews - < r2.json` with `--reviews-after r2.json`
        # would compare one fetch with itself.
        tmp = Path(tempfile.mkdtemp())
        names = ["c.json", "rc.json", "r2.json", "c2.json", "rc2.json"]
        for name in names:
            (tmp / name).write_text("[[]]", encoding="utf-8")
            self.addCleanup((tmp / name).unlink)
        with (tmp / "r2.json").open("rb") as piped:
            result = subprocess.run([sys.executable, str(SCRIPT), "--reviews", "-", "--comments", str(tmp / "c.json"),
                                     "--review-comments", str(tmp / "rc.json"), "--reviews-after", str(tmp / "r2.json"),
                                     "--comments-after", str(tmp / "c2.json"),
                                     "--review-comments-after", str(tmp / "rc2.json")],
                                    stdin=piped, capture_output=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(b"stdin (-) is not accepted", result.stderr)

    @unittest.skipIf(os.name == "nt" or not os.path.exists("/dev/stdin"), "needs POSIX /dev/stdin and /dev/null")
    def test_a_source_that_is_not_a_regular_file_is_refused(self):
        # `cat r2.json | ... --reviews /dev/stdin --reviews-after r2.json` compares one fetch with itself.
        tmp = Path(tempfile.mkdtemp())
        names = ["c.json", "rc.json", "r2.json", "c2.json", "rc2.json"]
        for name in names:
            (tmp / name).write_text("[[]]", encoding="utf-8")
            self.addCleanup((tmp / name).unlink)
        for source, piped in (("/dev/stdin", b"[[]]"), (os.devnull, None)):
            with self.subTest(source=source):
                result = subprocess.run([sys.executable, str(SCRIPT), "--reviews", source,
                                         "--comments", str(tmp / "c.json"), "--review-comments", str(tmp / "rc.json"),
                                         "--reviews-after", str(tmp / "r2.json"), "--comments-after", str(tmp / "c2.json"),
                                         "--review-comments-after", str(tmp / "rc2.json")],
                                        input=piped, capture_output=True)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(b"is not a regular file", result.stderr)


class PolicyConsistencyTests(unittest.TestCase):
    def test_the_protocol_and_the_script_agree_there_is_no_review_cap(self):
        doc = (ROOT / "docs" / "claude-to-codex.md").read_text(encoding="utf-8")
        self.assertRegex(doc, r"(?m)^- Maximum review rounds per PR: none\b",
                         "docs/claude-to-codex.md section 16 no longer states that reviews have no cap")
        self.assertIsNone(counter.MAX_REVIEW_ROUNDS)

    def test_the_protocol_names_this_script(self):
        doc = (ROOT / "docs" / "claude-to-codex.md").read_text(encoding="utf-8")
        self.assertIn("scripts/codex_round_count.py", doc)


if __name__ == "__main__":
    unittest.main()
