"""scripts/office/snapshot.py: the reducer behind the agent-office dashboard.

The demos under scripts/office/demo/ are recorded runs, so most claims here are made
against them at a chosen moment: that is exactly what the dashboard's replay does.
Rules the demos cannot reach (stalls, failures, unknown agents) use small synthetic logs.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "scripts" / "office" / "snapshot.py"
T0 = 1760000000.0  # the demos' first second


def load_module(name: str, path: Path):
    """Load from source, never from the bytecode cache (see test_session_budget)."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


snapshot = load_module("office_snapshot", SNAPSHOT_PATH)
ROSTER = snapshot.load_roster()


def at(offset: float, demo: str = "claude-t3") -> dict:
    return snapshot.build_demo(demo, ROSTER, T0 + offset)


def ev(kind: str, ts: float, **fields) -> dict:
    return {"v": 1, "ev": kind, "ts": ts, "session": "s", **fields}


def ledger(tier: str = "T1", required=("code-reviewer",), base: int = 1, recorded: float = 0.0, **extra) -> dict:
    def stamp(ts: float) -> str:
        return snapshot.datetime.fromtimestamp(ts, snapshot.timezone.utc).strftime(snapshot.UTC_FORMAT)

    return {"version": 1, "requirement": "R-1", "recorded_at": stamp(recorded), "tier": tier, "lane": "claude",
            "strategy": "s", "required_agents": list(required), "base": base, "reserves": [],
            "runtime_reserves": [], "invocations": [], **extra}


def build(events, led=None, now: float = 1000.0, files=None) -> dict:
    return snapshot.build_claude({"events": events, "ledger": led, "agent_files": files or {}}, ROSTER, now)


def run_log(agent: str, start: float, stop: float | None, calls: int = 3, uid: str = "u1", aid: str = "a1",
            note: str = "fine") -> list[dict]:
    out = [ev("spawn_request", start - 0.1, agent=agent, task="the task", tool_use_id=uid),
           ev("start", start, agent=agent, agent_id=aid)]
    out += [ev("tool", start + 1 + i, agent=agent, agent_id=aid, tool="Read") for i in range(calls)]
    if stop is not None:
        out.append(ev("stop", stop, agent=agent, agent_id=aid, note=note))
    return out


class DemoReplayTests(unittest.TestCase):
    def test_a_running_agent_reports_its_tool_calls_over_max_turns_as_progress(self) -> None:
        view = at(10)["agents"]["requirement-analyst"]
        self.assertEqual(view["state"], "working")
        self.assertEqual(view["turns"], {"used": 2, "max": 8})
        self.assertAlmostEqual(view["progress"], 2 / 8)

    def test_a_finished_agent_is_done_at_exactly_100_and_hands_over(self) -> None:
        view = at(17.5)["agents"]["requirement-analyst"]
        self.assertEqual((view["state"], view["progress"], view["tag"]), ("done", 1.0, "handoff"))
        self.assertEqual(view["note"], "3 giả định đã chốt, 1 câu hỏi cho người")
        self.assertEqual(view["turns"], {"used": 6, "max": 8})

    def test_reviewers_and_critics_are_shown_as_reviewing(self) -> None:
        self.assertEqual(at(35)["agents"]["architecture-critic"]["state"], "reviewing")
        self.assertEqual(at(10)["agents"]["requirement-analyst"]["state"], "working")

    def test_an_expected_agent_waits_and_a_standby_one_stays_idle(self) -> None:
        agents = at(10)["agents"]
        self.assertEqual(agents["architecture-critic"]["state"], "waiting")
        self.assertEqual(agents["architect"]["state"], "idle")
        self.assertEqual(agents["test-engineer"]["state"], "idle")

    def test_replay_never_sees_events_after_now(self) -> None:
        early = at(10)
        self.assertEqual(early["agents"]["architecture-critic"]["runs"], 0)
        self.assertEqual([entry["agent"] for entry in early["log"] if entry["kind"] == "start"], ["requirement-analyst"])
        self.assertEqual(at(10)["now"], T0 + 10)

    def test_the_budget_is_rebuilt_as_of_the_moment_and_reports_base_and_reserves_apart(self) -> None:
        def slots(offset: float) -> dict:
            return {slot["id"]: (slot["used"], slot["granted"], slot["cap"]) for slot in at(offset)["budget"]}

        self.assertEqual(slots(10), {"base": (0, 3, 3), "analyst_reserve": (1, 1, 1), "escalation_reserve": (0, 0, 1)})
        self.assertEqual(slots(60), {"base": (2, 3, 3), "analyst_reserve": (1, 1, 1), "escalation_reserve": (0, 0, 1)})
        self.assertEqual(slots(70), {"base": (2, 3, 3), "analyst_reserve": (1, 1, 1), "escalation_reserve": (1, 1, 1)})

    def test_the_main_session_waits_on_a_running_subagent_and_works_between_them(self) -> None:
        waiting = at(10)["boss"]
        self.assertEqual((waiting["state"], waiting["waiting_for"]), ("waiting", "requirement-analyst"))
        self.assertEqual(at(19)["boss"]["state"], "working")

    def test_the_run_finishes_at_100_percent_and_the_main_session_goes_done_when_quiet(self) -> None:
        end = at(112)
        self.assertEqual(end["progress"]["pct"], 100)
        self.assertEqual((end["boss"]["state"], end["phase"]["current"]), ("done", "done"))
        self.assertNotEqual(at(77.5)["boss"]["state"], "done", "the main session was active a second ago")

    def test_progress_counts_expected_roles_not_events(self) -> None:
        self.assertEqual(at(33.6)["progress"]["pct"], 44)  # analyst done + critic one third, of three roles
        self.assertEqual(at(0)["progress"]["pct"], 0)

    def test_the_phase_follows_the_last_agent_run(self) -> None:
        self.assertEqual(at(0)["phase"]["current"], "analysis")
        self.assertEqual(at(10)["phase"]["current"], "analysis")
        self.assertEqual(at(20)["phase"]["current"], "design")
        self.assertEqual(at(45)["phase"]["current"], "implement")
        self.assertEqual(at(55)["phase"]["current"], "verify")

    def test_only_the_agents_worth_showing_appear(self) -> None:
        agents = set(at(10)["agents"])
        self.assertEqual(agents, {"requirement-analyst", "architecture-critic", "architect", "implementer",
                                  "code-reviewer-t3", "test-engineer", "code-reviewer-verify"})
        self.assertNotIn("code-reviewer", agents, "the T1/T2 reviewer is not part of a T3 route")

    def test_edges_are_planned_active_or_done_and_the_return_edge_shows_only_while_handing_over(self) -> None:
        edges = {(edge["from"], edge["to"]): edge["state"] for edge in at(33.6)["edges"]}
        self.assertEqual(edges[("main", "requirement-analyst")], "done")
        self.assertEqual(edges[("main", "architecture-critic")], "active")
        self.assertEqual(edges[("main", "code-reviewer-t3")], "planned")
        self.assertNotIn(("requirement-analyst", "main"), edges)
        self.assertEqual({(e["from"], e["to"]): e["state"] for e in at(17.5)["edges"]}[("requirement-analyst", "main")], "active")

    def test_every_sampled_moment_of_both_demos_is_a_valid_snapshot(self) -> None:
        for name in snapshot.demo_names():
            span = snapshot.load_demo(name)["span"]
            for step in range(0, 61):
                when = span["start"] + (span["end"] - span["start"]) * step / 60
                self.assertEqual(snapshot.validate(snapshot.build_demo(name, ROSTER, when)), [], f"{name} at step {step}")

    def test_the_demo_events_are_what_the_real_hook_wrote_and_hold_no_prompt_text(self) -> None:
        text = (ROOT / "scripts" / "office" / "demo" / "claude-t3" / "events.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("prompt never stored", text)
        self.assertNotIn("transcript", text)


class ReducerRuleTests(unittest.TestCase):
    def test_a_running_agent_that_has_gone_quiet_is_shown_stalled_not_working(self) -> None:
        events = run_log("architect", 100, None)
        quiet = build(events, now=100 + snapshot.STALE_SECONDS + 10)["agents"]["architect"]
        self.assertEqual((quiet["state"], quiet["stalled"]), ("blocked", True))
        self.assertEqual(build(events, now=130)["agents"]["architect"]["state"], "working")

    def test_progress_never_reaches_100_before_the_agent_stops(self) -> None:
        events = run_log("architect", 100, None, calls=40)
        view = build(events, now=300, files={"architect": {"max_turns": 10}})["agents"]["architect"]
        self.assertEqual(view["progress"], snapshot.PROGRESS_CAP)

    def test_a_missing_max_turns_gives_no_progress_figure_rather_than_a_made_up_one(self) -> None:
        view = build(run_log("architect", 100, None), now=130)["agents"]["architect"]
        self.assertIsNone(view["progress"])

    def test_a_failed_spawn_blocks_the_agent_until_a_later_run_succeeds(self) -> None:
        failed = [ev("spawn_request", 100, agent="architect", task="x", tool_use_id="u1"),
                  ev("spawn_failed", 101, agent="architect", tool_use_id="u1", error="quota")]
        view = build(failed, now=102)["agents"]["architect"]
        self.assertEqual((view["state"], view["tag"]), ("blocked", "error"))
        self.assertIsNone(build(failed, now=110)["agents"]["architect"]["tag"], "the error tag is momentary")
        retried = failed + run_log("architect", 200, 210, uid="u2", aid="a2")
        self.assertEqual(build(retried, now=300)["agents"]["architect"]["state"], "done")

    def test_a_spawn_the_harness_has_not_started_yet_already_counts_as_working(self) -> None:
        events = [ev("spawn_request", 100, agent="architect", task="x", tool_use_id="u1")]
        self.assertEqual(build(events, now=101)["agents"]["architect"]["state"], "working")

    def test_a_refused_request_does_not_steal_the_start_of_the_retry_that_follows_it(self) -> None:
        """The budget hook refusing a spawn leaves a request that never starts; the retry is the newer one."""
        events = [ev("spawn_request", 100, agent="code-reviewer", task="DENIED by budget", tool_use_id="u1"),
                  ev("spawn_request", 200, agent="code-reviewer", task="the real one", tool_use_id="u2"),
                  ev("start", 201, agent="code-reviewer", agent_id="X")]
        runs, _ = snapshot.assemble_runs(events)
        self.assertEqual([(run["task"], run["agent_id"]) for run in runs], [("DENIED by budget", None), ("the real one", "X")])
        view = build(events, now=205)["agents"]["code-reviewer"]
        self.assertEqual((view["state"], view["task"], view["stalled"]), ("reviewing", "the real one", False))

    def test_an_abandoned_request_never_outranks_a_later_run_of_the_same_agent(self) -> None:
        refused = [ev("spawn_request", 100, agent="code-reviewer", task="DENIED", tool_use_id="u1")]
        real = run_log("code-reviewer", 400, 410, uid="u2", aid="a2")
        self.assertEqual(build(refused, now=100 + snapshot.START_TIMEOUT_SECONDS + 5)["agents"]["code-reviewer"]["state"], "blocked")
        later = build(refused + real, now=500)["agents"]["code-reviewer"]
        self.assertEqual((later["state"], later["stalled"]), ("done", False))
        self.assertEqual(build(refused + real, now=500)["progress"]["blocked"], 0)

    def test_a_retry_that_finishes_inside_the_start_timeout_outranks_the_refused_request_at_every_moment(self) -> None:
        """The refused request is abandoned when the retry overtakes it, and it never ranks above that retry."""
        events = [ev("spawn_request", 100, agent="code-reviewer", task="REFUSED by budget", tool_use_id="u1"),
                  ev("spawn_request", 105, agent="code-reviewer", task="RETRY", tool_use_id="u2"),
                  ev("start", 106, agent="code-reviewer", agent_id="X"),
                  ev("stop", 115, agent="code-reviewer", agent_id="X", note="retry done"),
                  ev("spawn_result", 115.1, agent="code-reviewer", tool_use_id="u2", agent_id="X", status="completed", tool_uses=4)]
        running = build(events[:3], now=110)
        self.assertEqual((running["agents"]["code-reviewer"]["task"], running["progress"]["running"]), ("RETRY", 1))
        for now in (120, 150, 230, 1000):
            snap = build(events, now=now)
            view = snap["agents"]["code-reviewer"]
            self.assertEqual((view["state"], view["task"], view["stalled"]), ("done", "RETRY", False), f"at {now}")
            self.assertEqual((snap["progress"]["blocked"], snap["progress"]["running"]), (0, 0), f"at {now}")
            self.assertEqual(snap["boss"]["state"] in ("waiting",), False, f"at {now}")

    def test_the_latest_run_is_ranked_by_chronology_whatever_end_an_abandoned_request_was_given(self) -> None:
        """agent_view's own contract: an abandoned request's synthetic end must never lift it above a newer run."""
        def synthetic(**fields) -> dict:
            run = {"agent": "code-reviewer", "task": None, "tool_use_id": None, "agent_id": None, "requested": 0.0, "started": None,
                   "ended": None, "status": "requested", "last_seen": 0.0, "tool_calls": 0, "note": None, "tokens": None,
                   "duration_ms": None, "tool_uses": None}
            run.update(fields)
            return run

        abandoned = synthetic(requested=100.0, ended=500.0, status="abandoned", task="REFUSED", last_seen=100.0)
        retry = synthetic(requested=105.0, started=106.0, ended=115.0, status="ok", task="RETRY", last_seen=115.0, tool_uses=4)
        for order in ([abandoned, retry], [retry, abandoned]):
            view = snapshot.agent_view("code-reviewer", order, False, 1000.0, {}, {})
            self.assertEqual((view["state"], view["task"], view["stalled"]), ("done", "RETRY", False))

    def test_the_result_lands_on_the_run_of_the_agent_it_names_after_a_crosswise_repair(self) -> None:
        """Telemetry and completion belong to the agent the result names, not to whichever object matched its tool_use_id."""
        start = [ev("spawn_request", 100.0, agent="architect", task="first task", tool_use_id="u1"),
                 ev("spawn_request", 100.1, agent="architect", task="second task", tool_use_id="u2"),
                 ev("start", 101.0, agent="architect", agent_id="A"), ev("start", 101.2, agent="architect", agent_id="B"),
                 ev("tool", 102, agent="architect", agent_id="A", tool="Read"), ev("tool", 103, agent="architect", agent_id="B", tool="Read")]
        results = [ev("spawn_result", 110.0, agent="architect", tool_use_id="u1", agent_id="A", status="completed", tool_uses=7, tokens=1000),
                   ev("spawn_result", 111.0, agent="architect", tool_use_id="u2", agent_id="B", status="completed", tool_uses=3, tokens=500)]
        with_stops = start + [ev("stop", 109.0, agent="architect", agent_id="A", note="A done"),
                              ev("stop", 110.5, agent="architect", agent_id="B", note="B done")] + results
        runs, _ = snapshot.assemble_runs(with_stops, 200)
        by_agent = {run["agent_id"]: (run["task"], run["ended"], run["tool_uses"], run["tokens"]) for run in runs}
        self.assertEqual(by_agent, {"A": ("first task", 109.0, 7, 1000), "B": ("second task", 110.5, 3, 500)})
        runs, _ = snapshot.assemble_runs(start + results, 200)  # no stop events: the results alone must close both
        self.assertEqual({run["agent_id"]: run["ended"] for run in runs}, {"A": 110.0, "B": 111.0})
        self.assertEqual(build(start + results, now=200)["progress"]["running"], 0)

    def test_the_result_repairs_two_parallel_agents_of_one_type_that_started_crosswise(self) -> None:
        """Two critics start; the starts pair with the requests newest-first, so the result puts the tasks right."""
        events = [ev("spawn_request", 100.0, agent="architect", task="first task", tool_use_id="u1"),
                  ev("spawn_request", 100.1, agent="architect", task="second task", tool_use_id="u2"),
                  ev("start", 101.0, agent="architect", agent_id="A"),   # really the first request's agent
                  ev("start", 101.2, agent="architect", agent_id="B"),
                  ev("spawn_result", 110.0, agent="architect", tool_use_id="u1", agent_id="A", status="completed"),
                  ev("spawn_result", 111.0, agent="architect", tool_use_id="u2", agent_id="B", status="completed")]
        before, _ = snapshot.assemble_runs(events[:4])
        self.assertEqual({run["agent_id"]: run["task"] for run in before}, {"A": "second task", "B": "first task"})
        after, _ = snapshot.assemble_runs(events)
        self.assertEqual({run["agent_id"]: run["task"] for run in after}, {"A": "first task", "B": "second task"})
        self.assertEqual({run["agent_id"]: run["tool_use_id"] for run in after}, {"A": "u1", "B": "u2"})

    def test_a_spawn_that_never_started_is_stalled_after_the_start_timeout_and_the_main_session_stops_waiting(self) -> None:
        events = [ev("spawn_request", 100, agent="architect", task="x", tool_use_id="u1")]
        late = build(events, now=100 + snapshot.START_TIMEOUT_SECONDS + 5)
        self.assertEqual((late["agents"]["architect"]["state"], late["agents"]["architect"]["stalled"]), ("blocked", True))
        self.assertNotEqual(late["boss"]["state"], "waiting")
        self.assertEqual(snapshot.validate(late), [])

    def test_a_background_launch_keeps_running_until_its_stop_event(self) -> None:
        events = run_log("architect", 100, None) + [
            ev("spawn_result", 101, agent="architect", tool_use_id="u1", agent_id="a1", status="async_launched")]
        self.assertEqual(build(events, now=150)["agents"]["architect"]["state"], "working")
        events.append(ev("stop", 160, agent="architect", agent_id="a1", note="ok"))
        self.assertEqual(build(events, now=170)["agents"]["architect"]["state"], "done")

    def test_a_completed_result_ends_a_run_even_when_no_stop_event_arrived(self) -> None:
        events = run_log("architect", 100, None) + [
            ev("spawn_result", 110, agent="architect", tool_use_id="u1", agent_id="a1", status="completed", tool_uses=5)]
        view = build(events, now=120)["agents"]["architect"]
        self.assertEqual((view["state"], view["turns"]["used"]), ("done", 5))

    def test_an_agent_type_outside_the_roster_gets_an_other_lane(self) -> None:
        snap = build(run_log("Explore", 100, 110), now=120)
        self.assertEqual([lane["id"] for lane in snap["lanes"] if "Explore" in lane["agents"]], ["other"])
        self.assertEqual(snapshot.validate(snap), [])

    def test_main_thread_tool_calls_are_activity_not_agent_work(self) -> None:
        snap = build([ev("tool", 995.0, tool="Edit")], now=1000.0)
        self.assertEqual(snap["boss"]["state"], "working")
        self.assertEqual(snap["progress"]["running"], 0)
        self.assertEqual(build([ev("tool", 900.0, tool="Edit")], now=1000.0)["boss"]["state"], "idle")

    def test_without_a_ledger_the_view_says_so_and_still_shows_what_ran(self) -> None:
        snap = build(run_log("architect", 100, 110), None, now=120)
        self.assertEqual(snap["hints"], ["no_ledger"])
        self.assertIsNone(snap["budget"])
        self.assertEqual(snap["agents"]["architect"]["state"], "done")

    def test_nothing_at_all_is_an_empty_state_with_both_hints(self) -> None:
        snap = build([], None, now=120)
        self.assertEqual((snap["empty"], snap["hints"]), (True, ["no_ledger", "no_events"]))
        self.assertIsNone(snap["span"])
        self.assertEqual(snapshot.validate(snap), [])

    def test_a_ledger_without_events_hints_that_the_hook_is_not_running(self) -> None:
        snap = build([], ledger(), now=120)
        self.assertEqual((snap["empty"], snap["hints"]), (False, ["no_events"]))
        self.assertEqual(snap["agents"]["code-reviewer"]["state"], "waiting")

    def test_events_from_before_the_requirement_began_are_left_out(self) -> None:
        old = run_log("architecture-critic", 100, 110, uid="old", aid="old")
        new = run_log("code-reviewer", 5000, 5010, uid="new", aid="new")
        snap = build(old + new, ledger(recorded=4990.0), now=5020)
        self.assertEqual(snap["agents"]["code-reviewer"]["state"], "done")
        self.assertNotIn("architecture-critic", snap["agents"])

    def test_without_a_ledger_only_the_latest_session_is_shown(self) -> None:
        first = [{**event, "session": "old"} for event in run_log("architect", 100, 110, uid="a", aid="a")]
        second = [{**event, "session": "new"} for event in run_log("implementer", 500, 510, uid="b", aid="b")]
        snap = build(first + second, None, now=520)
        self.assertEqual(snap["agents"]["implementer"]["state"], "done")
        self.assertEqual(snap["agents"]["architect"]["runs"], 0)

    def test_the_route_decides_who_is_shown_and_who_is_expected(self) -> None:
        snap = build([], ledger(tier="T1"), now=10)
        self.assertEqual(snap["agents"]["code-reviewer"]["state"], "waiting")
        for hidden in ("code-reviewer-t3", "architecture-critic", "requirement-analyst", "test-engineer"):
            self.assertNotIn(hidden, snap["agents"])
        reserve = {"reserve": "escalation_reserve", "amount": 1, "grantable_agents": ["test-engineer"], "grant_condition": "x"}
        t2 = ledger(tier="T2", runtime_reserves=[reserve])
        self.assertEqual(build([], t2, now=10)["agents"]["test-engineer"]["state"], "idle")

    def test_a_t0_route_has_no_progress_to_report(self) -> None:
        snap = build([], ledger(tier="T0", required=(), base=0), now=10)
        self.assertIsNone(snap["progress"]["pct"])
        self.assertEqual(snapshot.validate(snap), [])

    def test_torn_and_foreign_lines_are_skipped_when_reading_the_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "office-events.jsonl"
            good = json.dumps(ev("tool", 5.0, tool="Read"))
            path.write_text(f'{good}\n{{"v":1,"ev":"tool","ts":\nnot json\n[1,2]\n{{"ev":"x"}}\n{good}\n', encoding="utf-8")
            self.assertEqual(len(snapshot.read_events(path)), 2)

    def test_the_rotated_generation_is_read_before_the_current_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "office-events.jsonl"
            path.write_text(json.dumps(ev("tool", 20.0)) + "\n", encoding="utf-8")
            path.with_name(path.name + ".1").write_text(json.dumps(ev("tool", 10.0)) + "\n", encoding="utf-8")
            self.assertEqual([event["ts"] for event in snapshot.read_events(path)], [10.0, 20.0])

    def test_max_turns_come_from_the_agent_files_front_matter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents = Path(tmp) / ".claude" / "agents"
            agents.mkdir(parents=True)
            (agents / "x.md").write_text("---\nname: critic\nmodel: sonnet\nmaxTurns: 12\neffort: high\n---\nbody\n", encoding="utf-8")
            (agents / "y.md").write_text("no front matter\n", encoding="utf-8")
            self.assertEqual(snapshot.read_agent_files(Path(tmp)), {"critic": {"max_turns": 12, "model": "sonnet", "effort": "high"}})


class TeamViewTests(unittest.TestCase):
    def view(self, offset: float) -> dict:
        return at(offset, "team-f12")

    def test_the_stage_in_state_json_decides_which_worker_is_running(self) -> None:
        for offset, running in ((10, "tester"), (25, "coder"), (55, "reviewer"), (65, "pack")):
            snap = self.view(offset)
            working = [name for name, view in snap["agents"].items() if view["state"] in ("working", "reviewing")]
            self.assertEqual(working, [running], f"at {offset}")

    def test_a_feature_that_has_only_been_created_is_waiting_for_its_spec_not_busy(self) -> None:
        snap = self.view(0)
        self.assertEqual([name for name, view in snap["agents"].items() if view["state"] in ("working", "reviewing")], [])
        spec = snap["agents"]["claude-spec"]
        self.assertEqual((spec["state"], spec["note"]), ("waiting", "awaiting_spec"))
        self.assertEqual((snap["boss"]["state"], snap["boss"]["waiting_for"]), ("waiting", "claude-spec"))
        self.assertEqual(snap["progress"]["pct"], 0)

    def test_earlier_stages_are_done_and_later_ones_wait(self) -> None:
        agents = self.view(25)["agents"]
        self.assertEqual((agents["claude-spec"]["state"], agents["tester"]["state"]), ("done", "done"))
        self.assertEqual((agents["reviewer"]["state"], agents["pack"]["state"], agents["claude-audit"]["state"]), ("waiting",) * 3)

    def test_the_gates_log_result_shows_on_the_gates_card(self) -> None:
        self.assertEqual(self.view(55)["agents"]["gates"]["note"], "PASS 12/12")
        self.assertEqual(self.view(10)["agents"]["gates"]["state"], "waiting")

    def test_red_gates_are_blocked_with_the_share_that_passes_and_green_gates_are_done(self) -> None:
        red = self.view(36)["agents"]["gates"]
        self.assertEqual((red["state"], red["note"], red["progress"]), ("blocked", "FAIL 9/12", 0.75))
        self.assertEqual(self.view(36)["agents"]["coder"]["state"], "working", "the coder is retrying")
        green = self.view(55)["agents"]["gates"]
        self.assertEqual((green["state"], green["progress"]), ("done", 1.0))

    def test_the_log_is_built_from_the_files_the_pipeline_leaves(self) -> None:
        log = self.view(36)["log"]
        self.assertEqual([(entry["agent"], entry["kind"]) for entry in log],
                         [("coder", "start"), ("gates", "fail"), ("claude-spec", "done")])

    def test_models_come_from_state_json_only_once_they_are_recorded(self) -> None:
        self.assertIsNone(self.view(10)["agents"]["tester"]["model"])
        self.assertEqual(self.view(25)["agents"]["tester"]["model"], "sample/free-a")
        self.assertEqual(self.view(55)["agents"]["coder"]["model"], "sample/free-d")

    def test_ready_for_audit_waits_for_the_human_then_the_verdict_decides(self) -> None:
        waiting = self.view(75)
        self.assertEqual((waiting["agents"]["claude-audit"]["state"], waiting["agents"]["claude-audit"]["note"]),
                         ("waiting", "awaiting_audit"))
        self.assertEqual((waiting["boss"]["state"], waiting["boss"]["waiting_for"]), ("waiting", "claude-audit"))
        approved = self.view(86)
        self.assertEqual((approved["boss"]["state"], approved["progress"]["pct"]), ("done", 100))
        self.assertEqual(approved["agents"]["claude-audit"]["state"], "done")

    def test_a_block_verdict_blocks_the_audit_card(self) -> None:
        demo = snapshot.load_demo("team-f12")
        feature = copy.deepcopy(demo["inputs"]["frames"][-1]["feature"])
        feature["files"]["verdict.md"]["text"] = "VERDICT: BLOCK\n"
        snap = snapshot.build_team([feature], ROSTER, feature["updated"])
        self.assertEqual((snap["agents"]["claude-audit"]["state"], snap["boss"]["state"]), ("blocked", "blocked"))

    def test_a_blocked_stage_blocks_that_stage_with_the_reason(self) -> None:
        feature = {"id": "F1", "updated": 50.0, "files": {},
                   "state": {"stage": "blocked: no tester model produced tests", "next": "tester"}}
        snap = snapshot.build_team([feature], ROSTER, 60.0)
        self.assertEqual((snap["agents"]["tester"]["state"], snap["agents"]["tester"]["note"]),
                         ("blocked", "no tester model produced tests"))
        self.assertEqual(snap["boss"]["state"], "blocked")
        self.assertEqual(snap["agents"]["coder"]["state"], "waiting")

    def test_pipeline_warnings_are_surfaced(self) -> None:
        snap = self.view(65)
        self.assertEqual(len(snap["warnings"]), 1)
        self.assertIn("warn", [entry["kind"] for entry in snap["log"]])

    def test_the_most_recently_updated_feature_is_shown_unless_one_is_asked_for(self) -> None:
        old = {"id": "A", "updated": 10.0, "files": {}, "state": {"stage": "spec"}}
        new = {"id": "B", "updated": 20.0, "files": {}, "state": {"stage": "running: tester"}}
        self.assertEqual(snapshot.build_team([old, new], ROSTER, 30.0)["feature"], "B")
        chosen = snapshot.build_team([old, new], ROSTER, 30.0, feature_id="A")
        self.assertEqual((chosen["feature"], chosen["features"]), ("A", ["A", "B"]))

    def test_no_features_is_an_empty_state(self) -> None:
        snap = snapshot.build_team([], ROSTER, 30.0)
        self.assertEqual((snap["empty"], snap["hints"]), (True, ["no_features"]))
        self.assertEqual(snapshot.validate(snap), [])

    def test_features_are_read_from_files_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            out = home / "work" / "F7" / "out"
            out.mkdir(parents=True)
            (out / "state.json").write_text(json.dumps({"stage": "running: coder", "next": "coder",
                                                        "updated": "2026-10-09 08:53:20Z"}), encoding="utf-8")
            (home / "work" / "F7" / "gates.log").write_text("# gates\nRESULT: FAIL (1/3 passed)\n", encoding="utf-8")
            (home / "work" / "F8").mkdir()  # no state.json: not a feature
            (home / "work" / "stray.txt").write_text("x", encoding="utf-8")
            features = snapshot.load_team_features(home)
            self.assertEqual([item["id"] for item in features], ["F7"])
            self.assertEqual(snapshot.gates_result(features[0]["files"]), ("FAIL", 1, 3))
            self.assertEqual(features[0]["updated"], snapshot.parse_utc("2026-10-09 08:53:20Z"))

    def test_a_corrupt_state_json_is_skipped_not_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "work" / "F1" / "out"
            out.mkdir(parents=True)
            (out / "state.json").write_text("{not json", encoding="utf-8")
            self.assertEqual(snapshot.load_team_features(Path(tmp)), [])


class ValidateTests(unittest.TestCase):
    def good(self) -> dict:
        return at(33.6)

    def test_a_good_snapshot_has_no_problems(self) -> None:
        self.assertEqual(snapshot.validate(self.good()), [])

    def test_each_contract_break_is_reported(self) -> None:
        def broken(mutate) -> list[str]:
            snap = copy.deepcopy(self.good())
            mutate(snap)
            return snapshot.validate(snap)

        cases = {
            "an unknown state": lambda s: s["agents"]["architect"].update(state="sleeping"),
            "progress above 1": lambda s: s["agents"]["architect"].update(progress=1.5),
            "a running agent at 100%": lambda s: s["agents"]["architecture-critic"].update(progress=1.0),
            "a lane member without an agent": lambda s: s["lanes"][0]["agents"].append("ghost"),
            "an empty lane": lambda s: s["lanes"][0]["agents"].clear(),
            "an agent in no lane": lambda s: s["lanes"][3]["agents"].pop(),
            "an edge to nowhere": lambda s: s["edges"].append({"from": "main", "to": "ghost", "state": "active"}),
            "an unknown edge state": lambda s: s["edges"][0].update(state="glowing"),
            "budget used beyond granted": lambda s: s["budget"][0].update(used=9),
            "a percentage above 100": lambda s: s["progress"].update(pct=101),
            "a bad mode": lambda s: s.update(mode="other"),
            "a phase that is not a step": lambda s: s["phase"].update(current="lunch"),
            "an inverted span": lambda s: s["span"].update(start=s["span"]["end"] + 1),
        }
        for label, mutate in cases.items():
            self.assertTrue(broken(mutate), f"validate() accepted {label}")

    def test_a_non_object_is_rejected(self) -> None:
        self.assertEqual(snapshot.validate([]), ["snapshot is not an object"])


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SNAPSHOT_PATH), *args], capture_output=True, text=True, cwd=ROOT, timeout=60)

    def test_check_passes_on_the_bundled_demos(self) -> None:
        result = self.run_cli("--check")
        self.assertEqual((result.returncode, result.stdout.strip()), (0, "snapshot schema: ok"))

    def test_a_demo_renders_as_json(self) -> None:
        result = self.run_cli("--demo", "claude-t3", "--at", "0.5")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["demo"], "claude-t3")

    def test_the_live_view_of_an_empty_checkout_is_an_empty_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("--root", tmp, "--team-home", tmp)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(json.loads(result.stdout)["empty"])


if __name__ == "__main__":
    unittest.main()
