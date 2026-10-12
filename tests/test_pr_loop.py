"""The pull-request loop (CLAUDE.md, *Pull request lifecycle*) is prose, so what a test can pin is that
every piece of it still exists and still points at the others: the mandate, the protocol section it
cites, the scripts it gates on, and the lane runbooks that must not drift from it.

Nothing here judges the rule. A check whose answer is computable belongs in a script, and the round
count and the task-comment render already are. This only stops the rule being edited out of one place
while the other places go on citing it.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE_MD = ROOT / "CLAUDE.md"
PROTOCOL = ROOT / "docs" / "claude-to-codex.md"

LIFECYCLE_HEADING = "## Pull request lifecycle"
PROTOCOL_SUBSECTION = "### The loop every PR goes through"

# Everything that must say "every PR runs the lifecycle" and name where it is defined.
POINTERS = [
    ROOT / "docs" / "codex-lane.md",
    ROOT / ".claude" / "skills" / "codex-lane" / "SKILL.md",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def lifecycle_section() -> str:
    text = read(CLAUDE_MD)
    start = text.find(LIFECYCLE_HEADING)
    if start < 0:
        return ""
    following = re.search(r"^## ", text[start + len(LIFECYCLE_HEADING):], re.MULTILINE)
    end = start + len(LIFECYCLE_HEADING) + following.start() if following else len(text)
    return text[start:end]


class PullRequestLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.section = lifecycle_section()
        self.assertTrue(self.section, f"CLAUDE.md lost its {LIFECYCLE_HEADING!r} section")

    def test_the_mandate_covers_every_tier_and_lane(self) -> None:
        self.assertIn("at any tier, in any lane", self.section)
        self.assertIn("T0 typo fix included", self.section)

    def test_the_loop_has_all_six_steps_in_order(self) -> None:
        steps = re.findall(r"^(\d)\. \*\*", self.section, re.MULTILINE)
        self.assertEqual(steps, ["1", "2", "3", "4", "5", "6"])
        # review first, merge only after the clean exit, the next task last
        positions = [self.section.find(marker) for marker in
                     ("Open, then Codex review", "Validate every finding", "Fix, then have the new head reviewed",
                      "Stop when the review is clean", "Merge it yourself", "Then continue")]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn(-1, positions)

    def test_the_gates_are_the_scripts_that_exist(self) -> None:
        for script in ("scripts/codex_round_count.py",):
            self.assertIn(script, self.section)
            self.assertTrue((ROOT / script).is_file(), f"{script} is cited but missing")

    def test_the_cap_is_cited_not_restated(self) -> None:
        """A number copied here is a second source of truth; §16 and the policy already agree on it."""
        self.assertIn("§16", self.section)
        self.assertNotRegex(self.section, r"\b(three|3) (review )?rounds\b")

    def test_an_unreviewed_pr_is_never_merged(self) -> None:
        self.assertIn("is never merged", self.section)
        self.assertIn("BLOCKED", self.section)
        self.assertIn("do not merge", self.section)

    def test_the_trigger_string_ban_keeps_the_intentional_comment_exception(self) -> None:
        """Step 1 posts the trigger comment; the ban on the literal string elsewhere must not contradict it (section 3)."""
        self.assertIn("except the intentional trigger comments the protocol authorizes", self.section)
        self.assertIn("each review request of steps 1 and 3, a security review", self.section)
        self.assertIn("each task-contract request (BRAINSTORM, INVESTIGATE, AUDIT, IMPLEMENT, FIX)", self.section)

    def test_the_trigger_exception_names_every_task_contract_mode(self) -> None:
        """The exception must list exactly the modes section 5 defines, or a supported mode becomes forbidden."""
        modes = re.search(r'^mode: "([A-Z |]+)"', read(PROTOCOL), re.MULTILINE)
        self.assertIsNotNone(modes, "section 5 no longer lists the task-contract modes")
        listed = [m.strip() for m in modes.group(1).split("|")]
        self.assertGreaterEqual(len(listed), 5)
        self.assertIn(f"each task-contract request ({', '.join(listed)})", self.section)

    def test_the_next_task_is_never_invented(self) -> None:
        self.assertIn("never invent work", self.section)
        self.assertIn("the user explicitly asked for", self.section)

    def test_a_task_needing_an_unmerged_pr_waits(self) -> None:
        self.assertIn("needs the code of a PR that is not merged", self.section)
        self.assertIn("skip it rather than stack", self.section)

    def test_there_is_no_review_cap_and_the_two_exits_remain(self) -> None:
        """The owner removed the limit of three on 2026-10-12. The loop must say so, name what bounds it instead,
        and keep the two ways out: a disagreement and a genuine blocker."""
        self.assertIn("**No review cap.**", self.section)
        self.assertIn("2026-10-12", self.section)
        for phrase in ("once per head SHA", "may follow the standard one on the same head", "never while a request is unanswered", "disagreement",
                       "genuine blocker (§20)", "do not merge", "reworded or moved",
                       "other than a P2/P3 whose recorded rejection stands", "rules, not script gates",
                       "when no code change is pending escalate at once", "a P2/P3 stands at once"):
            self.assertIn(phrase, self.section)
        protocol = read(PROTOCOL)
        no_limit = protocol[protocol.index("### No review limit"):protocol.index("## 17. ")]
        for phrase in ("A disagreement.", "A genuine blocker", "Never request a review command for a head that command already reviewed",
                       "a required security review may follow the standard review on the same head",
                       "substantially the same issue", "prose rules, not script gates",
                       "When no code change is pending there is no new head to review",
                       "the recorded rejection stands at once"):
            self.assertIn(phrase, no_limit)
        loop = protocol[protocol.index(PROTOCOL_SUBSECTION):protocol.index("A human is needed only for")]
        self.assertIn("a P2/P3 whose rejection stands", loop)
        self.assertIn("a rejected P0/P1 is open until", loop)
        self.assertIn("every review command the work requires", loop)

    def test_section_11_applies_the_same_head_rule_per_review_command(self) -> None:
        """Section 11 gates every review request, so it must agree with section 16's per-command rule."""
        protocol = read(PROTOCOL)
        gate = protocol[protocol.index("## 11. "):protocol.index("## 12. ")]
        self.assertIn("for the review command being requested", gate)
        self.assertIn("a required security review follows the standard review", gate)
        self.assertIn("must not request the same review command again for a PR head SHA it already reviewed", gate)
        self.assertNotIn("repeated reviews for the same PR head SHA", gate)

    def test_no_summary_ends_the_loop_on_one_clean_review(self) -> None:
        """A security-sensitive route needs every required review command clean on the head; every summary must say so."""
        stale = ("until a review of the current head is clean", "until a review is clean",
                 "until a review of the\n   current head is clean")
        for path in (CLAUDE_MD, PROTOCOL, *POINTERS):
            text = read(path)
            for phrase in stale:
                with self.subTest(path=path.name, phrase=phrase[:30]):
                    self.assertNotIn(phrase, text)

    def test_nothing_still_speaks_of_a_last_allowed_review(self) -> None:
        """The cap-shaped wording must be gone everywhere the rule lives, or an agent follows the stale half."""
        stale = ("last allowed review", "cap permitting", "Reaching the review limit", "while the cap allows",
                 "review count allows", "the cap in §16 still holds")
        files = [CLAUDE_MD, PROTOCOL, *POINTERS]
        for path in files:
            text = read(path).replace("\n", " ")
            for phrase in stale:
                with self.subTest(path=path.name, phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_a_lane_fallback_never_waives_the_pr_review(self) -> None:
        """Re-recording a blocked requirement in the claude lane moves the work; the PR still needs its review."""
        phrase = "never waives the PR's Codex review"
        for path in (CLAUDE_MD, PROTOCOL, ROOT / "docs" / "codex-lane.md",
                     ROOT / ".claude" / "skills" / "codex-lane" / "SKILL.md"):
            with self.subTest(path=path.name):
                self.assertIn(phrase, read(path).replace("\n", " "))

    def test_a_thumbs_up_only_clean_run_can_end_the_loop(self) -> None:
        """Section 16 says a clean review may leave only a thumbs-up, so the exit must accept it for the requested head."""
        protocol = read(PROTOCOL).replace("\n", " ")
        exit_rule = protocol[protocol.index("**Exit when clean.**"):]
        exit_rule = exit_rule[:exit_rule.index("A fix pushed after the last review")]
        for phrase in ("only a thumbs-up", "👍 reaction on that command's request comment",
                       "provided the PR head has not moved since that request was posted"):
            self.assertIn(phrase, exit_rule)
        sec14 = protocol[protocol.index("## 14. "):protocol.index("## 15. ")]
        sec17 = protocol[protocol.index("## 17. "):protocol.index("## 18. ")]
        self.assertIn("only the bot's 👍 reaction on the request comment", sec14)
        self.assertIn("👍 reaction on the request comment is such a response too", sec17)
        self.assertIn("the bot's 👍 on that command's request counts as such a review", self.section)

    def test_every_protocol_section_it_cites_exists(self) -> None:
        protocol = read(PROTOCOL)
        cited = {int(n) for n in re.findall(r"§(\d+)", self.section)}
        self.assertTrue({11, 13, 14, 16, 17, 18, 20} <= cited, f"the section stopped citing: {cited}")
        for number in cited:
            self.assertRegex(protocol, rf"(?m)^## {number}\. ", f"CLAUDE.md cites §{number}; the protocol has no such section")

    def test_the_protocol_carries_the_loop_inside_section_20(self) -> None:
        protocol = read(PROTOCOL)
        self.assertEqual(protocol.count(PROTOCOL_SUBSECTION), 1)
        sec20 = protocol.index("## 20. ")
        sec21 = protocol.index("## 21. ")
        self.assertTrue(sec20 < protocol.index(PROTOCOL_SUBSECTION) < sec21, "the loop left section 20")
        self.assertIn("mandatory for every PR", protocol[sec20:sec21])
        # section 11 is where the first review is requested and must point at the loop
        sec11 = protocol.index("## 11. ")
        sec12 = protocol.index("## 12. ")
        self.assertIn("The loop every PR goes through", protocol[sec11:sec12])

    def test_the_routing_flow_and_the_delegation_section_point_at_it(self) -> None:
        text = read(CLAUDE_MD)
        self.assertRegex(text, r"(?m)^8\. If the work ships as a pull request, run it through \*Pull request lifecycle\*")
        delegation = text[text.index("## Delegating to Codex Cloud"):text.index(LIFECYCLE_HEADING)]
        self.assertIn("*Pull request lifecycle*", delegation)

    def test_every_lane_runbook_names_the_lifecycle(self) -> None:
        for path in POINTERS:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertRegex(read(path).replace("\n", " "), r"Pull request\s+lifecycle",
                                 f"{path.name} does not name the lifecycle")



if __name__ == "__main__":
    unittest.main()
