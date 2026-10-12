#!/usr/bin/env python3
"""Turn what the agent team left on disk into one snapshot the dashboard can draw.

Two views, each a pure function of its inputs:

    claude   the Claude Code subagent roster: the budget ledger written by
             `scripts/route.py --record` plus the event log written by
             `scripts/hooks/office_events.py`
    team     one feature of the VPS pipeline (`scripts/team/team.py`): its
             `state.json` and the files the pipeline leaves beside it

`build_claude` and `build_team` take already-loaded data and a moment `now`, so
the same code serves the live dashboard (now = the wall clock) and replay
(now = any earlier moment): the events after `now` are simply not seen. IO is
confined to the `load_*` functions. Nothing here writes, and nothing runs git
inside a feature's clone, which a worker could have planted.

    python3 scripts/office/snapshot.py                 # live claude view, as JSON
    python3 scripts/office/snapshot.py --mode team
    python3 scripts/office/snapshot.py --demo claude-t3 --at 0.4
    python3 scripts/office/snapshot.py --check         # validate the demos and the empty views
"""

from __future__ import annotations

import argparse
import bisect
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SNAPSHOT_VERSION = 1
SCRIPT_DIR = Path(__file__).resolve().parent
DEMO_DIR = SCRIPT_DIR / "demo"
EVENTS_RELATIVE = Path("artifacts") / "handoff" / "office-events.jsonl"
LEDGER_RELATIVE = Path("artifacts") / "handoff" / "agent-budget.json"

# A subagent that has said nothing for this long is shown as stalled, not as working forever.
STALE_SECONDS = 900
# A spawn the harness never started (the budget hook refused it, or the user declined it) is
# shown as stalled after this long, which is well past any normal start-up.
START_TIMEOUT_SECONDS = 120
# How long the "just received" / "just handed over" tag and the return edge stay on.
TAG_SECONDS = 4
# The main session counts as working while its last tool call is this recent.
MAIN_ACTIVE_SECONDS = 30
# A progress estimate never reaches 100% before the agent has actually finished.
PROGRESS_CAP = 0.95
LOG_LINES = 8
WINDOW_MARGIN = 30

PHASES = ("analysis", "design", "implement", "verify")
TEAM_STAGES = ("spec", "tester", "coder", "review", "pack", "audit")
STATES = ("idle", "waiting", "working", "reviewing", "done", "blocked")
EDGE_STATES = ("planned", "active", "done")
LOG_KINDS = ("start", "done", "fail", "warn")
MODES = ("claude", "team")
VERDICT_RE = re.compile(r"^\s*VERDICT:\s*(APPROVE|BLOCK)\s*$", re.MULTILINE)
GATES_RESULT_RE = re.compile(r"^RESULT:\s*(PASS|FAIL)\s*\((\d+)/(\d+)", re.MULTILINE)
UTC_FORMAT = "%Y-%m-%d %H:%M:%SZ"


def parse_utc(value: Any) -> float | None:
    """`2026-10-09 08:53:20Z` (the repository's timestamp format) as epoch seconds."""
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, UTC_FORMAT).replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        return None


def clip(value: Any, limit: int = 200) -> str | None:
    if not isinstance(value, str):
        return None
    text = " ".join(value.split())
    if not text:
        return None
    return text if len(text) <= limit else text[: limit - 1] + "…"


def number(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


# ---------------------------------------------------------------------------
# Loading (the only IO)
# ---------------------------------------------------------------------------


def load_roster() -> dict[str, Any]:
    return json.loads((SCRIPT_DIR / "roster.json").read_text(encoding="utf-8"))


def read_events(path: Path) -> list[dict[str, Any]]:
    """Every well-formed event line, oldest first. A torn or foreign line is skipped, never fatal."""
    events: list[dict[str, Any]] = []
    for candidate in (path.with_name(path.name + ".1"), path):
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict) and isinstance(event.get("ev"), str) and number(event.get("ts")) is not None:
                events.append(event)
    events.sort(key=lambda item: item["ts"])  # stable: equal timestamps keep file order
    return events


def read_ledger(root: Path) -> dict[str, Any] | None:
    try:
        data = json.loads((root / LEDGER_RELATIVE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) and isinstance(data.get("invocations"), list) else None


def read_agent_files(root: Path) -> dict[str, dict[str, Any]]:
    """`maxTurns`, `model` and `effort` from each `.claude/agents/*.md` front matter."""
    found: dict[str, dict[str, Any]] = {}
    directory = root / ".claude" / "agents"
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        if not lines or lines[0].strip() != "---":
            continue
        fields: dict[str, str] = {}
        for line in lines[1:]:
            if line.strip() == "---":
                break
            key, sep, value = line.partition(":")
            if sep:
                fields[key.strip()] = value.strip()
        turns = fields.get("maxTurns", "")
        found[fields.get("name") or path.stem] = {
            "max_turns": int(turns) if turns.isdigit() else None,
            "model": fields.get("model") or None,
            "effort": fields.get("effort") or None,
        }
    return found


def load_claude_inputs(root: Path) -> dict[str, Any]:
    return {
        "events": read_events(root / EVENTS_RELATIVE),
        "ledger": read_ledger(root),
        "agent_files": read_agent_files(root),
    }


def team_file_info(directory: Path, name: str) -> dict[str, Any] | None:
    path = directory / name
    try:
        stat = path.stat()
    except OSError:
        return None
    info: dict[str, Any] = {"mtime": stat.st_mtime}
    if name in ("gates.log", "verdict.md"):
        try:
            info["text"] = path.read_text(encoding="utf-8", errors="replace")[-20000:]
        except OSError:
            pass
    return info


def load_team_features(home: Path) -> list[dict[str, Any]]:
    """One record per feature under `<home>/work/*`, read as files only."""
    work = home / "work"
    features: list[dict[str, Any]] = []
    if not work.is_dir():
        return features
    for directory in sorted(work.iterdir()):
        if not directory.is_dir():
            continue
        state_path = directory / "out" / "state.json"
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            mtime = state_path.stat().st_mtime
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(state, dict):
            continue
        files = {}
        for name in ("spec.md", "gates.log", "prereview.md", "audit-pack.md", "verdict.md"):
            info = team_file_info(directory, name)
            if info is not None:
                files[name] = info
        features.append({"id": directory.name, "state": state, "updated": parse_utc(state.get("updated")) or mtime, "files": files})
    return features


# ---------------------------------------------------------------------------
# Claude view
# ---------------------------------------------------------------------------


def run_start(run: dict[str, Any]) -> float:
    return run["started"] if run["started"] is not None else run["requested"]


def assemble_runs(events: list[dict[str, Any]], now: float | None = None) -> tuple[list[dict[str, Any]], list[float]]:
    """Group spawn/start/tool/stop/result events into one record per subagent run, plus main-thread tool times.

    A request the harness never started (the budget hook refused it, or the person declined it) is closed as
    `abandoned`: at once when a later request or run of the same agent overtakes it, else, with `now`, once
    START_TIMEOUT_SECONDS have passed.
    """
    runs: list[dict[str, Any]] = []
    by_tool_use: dict[str, dict[str, Any]] = {}
    by_agent_id: dict[str, dict[str, Any]] = {}
    pending: list[dict[str, Any]] = []
    main_activity: list[float] = []

    def new_run(agent: str, ts: float, task: str | None = None, tool_use_id: str | None = None) -> dict[str, Any]:
        run = {
            "agent": agent, "task": task, "tool_use_id": tool_use_id, "agent_id": None,
            "requested": ts, "started": None, "ended": None, "status": "requested", "last_seen": ts,
            "tool_calls": 0, "note": None, "tokens": None, "duration_ms": None, "tool_uses": None,
        }
        runs.append(run)
        return run

    def finish(run: dict[str, Any], ts: float, status: str, note: str | None = None) -> None:
        if run["ended"] is None:
            run["ended"] = ts
            run["status"] = status
        if note and not run["note"]:
            run["note"] = note

    for event in events:
        kind, ts = event["ev"], float(event["ts"])
        agent = event.get("agent") if isinstance(event.get("agent"), str) else None
        agent_id = event.get("agent_id") if isinstance(event.get("agent_id"), str) else None
        tool_use_id = event.get("tool_use_id") if isinstance(event.get("tool_use_id"), str) else None
        if kind == "spawn_request":
            run = new_run(agent or "general-purpose", ts, clip(event.get("task")), tool_use_id)
            pending.append(run)
            if tool_use_id:
                by_tool_use[tool_use_id] = run
        elif kind == "start" and agent_id:
            # The newest request of that type: one the budget hook refused never starts, and the retry that
            # follows it is the newer. Parallel agents of one type may pair crosswise; spawn_result repairs that.
            run = max((item for item in pending if item["agent"] == agent), key=lambda item: item["requested"], default=None)
            if run is not None:
                pending.remove(run)
            else:  # a subagent no PreToolUse saw (an internal one, or the hook was off for the request)
                run = new_run(agent or "general-purpose", ts)
            run["agent_id"], run["started"], run["status"], run["last_seen"] = agent_id, ts, "running", ts
            by_agent_id[agent_id] = run
        elif kind == "tool":
            run = by_agent_id.get(agent_id) if agent_id else None
            if run is not None:
                run["tool_calls"] += 1
                run["last_seen"] = ts
            elif not agent_id:
                main_activity.append(ts)
        elif kind == "stop":
            run = by_agent_id.get(agent_id) if agent_id else None
            if run is not None:
                finish(run, ts, "ok", clip(event.get("note")))
        elif kind == "spawn_result":
            run = by_tool_use.get(tool_use_id) if tool_use_id else None
            if run is None and agent_id:
                run = by_agent_id.get(agent_id)
            if run is None:
                continue
            bound = by_agent_id.get(agent_id) if agent_id else None
            if bound is not None and bound is not run:
                # The start was paired with the wrong request of the same type: swap what identifies the request.
                for key in ("task", "tool_use_id", "requested"):
                    run[key], bound[key] = bound[key], run[key]
                for item in (run, bound):
                    if item["tool_use_id"]:
                        by_tool_use[item["tool_use_id"]] = item
                run = bound  # the result is the telemetry of the agent it names, not of the object found by tool_use_id
            elif agent_id and run["agent_id"] is None:
                run["agent_id"] = agent_id
                by_agent_id[agent_id] = run
            if run in pending:
                pending.remove(run)
            run["tokens"] = number(event.get("tokens"))
            run["duration_ms"] = number(event.get("duration_ms"))
            run["tool_uses"] = number(event.get("tool_uses"))
            if event.get("status") != "async_launched":
                finish(run, ts, "ok")
        elif kind == "spawn_failed":
            run = by_tool_use.get(tool_use_id) if tool_use_id else None
            if run is not None:
                if run in pending:
                    pending.remove(run)
                finish(run, ts, "failed", clip(event.get("error")))
    # A request that never started is closed as abandoned: at once when a later request or run of the same
    # agent exists (the retry that follows a refusal), else once START_TIMEOUT_SECONDS have passed.
    starts: dict[str, list[float]] = {}
    for run in runs:
        starts.setdefault(run["agent"], []).append(run_start(run))
    for moments in starts.values():
        moments.sort()
    for run in runs:
        if run["started"] is not None or run["ended"] is not None:
            continue
        moments = starts[run["agent"]]
        later = bisect.bisect_right(moments, run["requested"])
        if later < len(moments):
            run["ended"], run["status"] = moments[later], "abandoned"
        elif now is not None and now - run["requested"] > START_TIMEOUT_SECONDS:
            run["ended"], run["status"] = run["requested"] + START_TIMEOUT_SECONDS, "abandoned"
    return runs, main_activity


def window_start(ledger: dict[str, Any] | None, events: list[dict[str, Any]]) -> float | None:
    """When the requirement in progress began: the ledger's earliest charge, else the last session's first event."""
    if ledger is not None:
        stamps = [parse_utc(ledger.get("recorded_at"))]
        stamps += [parse_utc(item.get("at")) for item in ledger.get("invocations", []) if isinstance(item, dict)]
        known = [stamp for stamp in stamps if stamp is not None]
        if known:
            return min(known) - WINDOW_MARGIN
    if events:
        session = events[-1].get("session")
        same = [event["ts"] for event in events if event.get("session") == session]
        return min(same) if same else events[-1]["ts"]
    return None


def budget_view(ledger: dict[str, Any], now: float) -> list[dict[str, Any]]:
    """Base and each reserve, as of `now`, reported separately as CLAUDE.md asks."""
    spent = [item for item in ledger["invocations"] if (parse_utc(item.get("at")) or 0) <= now]
    slots = [{
        "id": "base", "cap": int(ledger.get("base") or 0), "granted": int(ledger.get("base") or 0),
        "used": sum(1 for item in spent if item.get("charged_to") == "base"),
    }]
    granted: dict[str, int] = {}
    for reserve in ledger.get("reserves", []):
        when = parse_utc(reserve.get("granted_at")) if reserve.get("granted_by") == "runtime" else None
        if when is not None and when > now:
            continue
        granted[reserve["reserve"]] = granted.get(reserve["reserve"], 0) + 1
    caps: dict[str, int] = dict(granted)
    for runtime in ledger.get("runtime_reserves", []):
        caps[runtime["reserve"]] = max(caps.get(runtime["reserve"], 0), int(runtime.get("amount", 1)))
    for name in sorted(caps):
        slots.append({
            "id": name, "cap": caps[name], "granted": granted.get(name, 0),
            "used": sum(1 for item in spent if item.get("charged_to") == name),
        })
    return slots


def expected_agents(ledger: dict[str, Any] | None) -> set[str]:
    """Roles the route says will run: the profile's floor plus agents a classification-time reserve was granted for."""
    if ledger is None:
        return set()
    names = {name for name in ledger.get("required_agents", []) if isinstance(name, str)}
    for reserve in ledger.get("reserves", []):
        if reserve.get("granted_by") == "classification":
            names.update(name for name in reserve.get("grantable_agents", []) if isinstance(name, str))
    return names


def possible_agents(ledger: dict[str, Any] | None) -> set[str]:
    """Roles that may run: expected ones plus anything a runtime reserve could still pay for."""
    names = set(expected_agents(ledger))
    if ledger is not None:
        for reserve in list(ledger.get("reserves", [])) + list(ledger.get("runtime_reserves", [])):
            names.update(name for name in reserve.get("grantable_agents", []) if isinstance(name, str))
    return names


def is_stalled(run: dict[str, Any], now: float) -> bool:
    """A running agent that has said nothing for too long."""
    return now - run["last_seen"] > STALE_SECONDS


def estimate(run: dict[str, Any], max_turns: int | None) -> float | None:
    """Tool calls over `maxTurns`: an estimate (a turn can hold several calls), never reported as complete."""
    if not max_turns:
        return None
    return min(PROGRESS_CAP, run["tool_calls"] / max_turns)


def current_phase(runs: list[dict[str, Any]], phases: dict[str, str | None]) -> str:
    known = [run for run in runs if phases.get(run["agent"])]
    if not known:
        return PHASES[0]
    last = max(known, key=run_start)
    index = PHASES.index(phases[last["agent"]])
    if last["ended"] is not None:
        index += 1
    return PHASES[index] if index < len(PHASES) else "done"


def agent_view(agent_id: str, runs: list[dict[str, Any]], expected: bool, now: float,
               info: dict[str, Any], files: dict[str, Any]) -> dict[str, Any]:
    mine = [run for run in runs if run["agent"] == agent_id]
    max_turns = files.get("max_turns")
    view: dict[str, Any] = {
        "id": agent_id, "state": "idle", "task": None, "note": None, "progress": None, "tag": None,
        "since": None, "runs": len(mine), "turns": None, "model": files.get("model"), "effort": files.get("effort"),
        "tokens": None, "duration_ms": None, "stalled": False, "kind": info.get("kind", "robot"),
    }
    active = [run for run in mine if run["ended"] is None]
    if active:
        run = max(active, key=run_start)
        stalled = is_stalled(run, now)
        reviewing = info.get("mode") == "reviewing"
        view.update(
            state="blocked" if stalled else ("reviewing" if reviewing else "working"),
            task=run["task"], progress=estimate(run, max_turns), since=run_start(run), stalled=stalled,
            tag="received" if now - run_start(run) < TAG_SECONDS else None,
            turns={"used": run["tool_calls"], "max": max_turns},
        )
        return view
    if mine:
        run = max(mine, key=run_start)  # chronology of the requests, not of their ends: an abandoned request ends late
        ok = run["status"] not in ("failed", "abandoned")
        view.update(
            state="done" if ok else "blocked", task=run["task"], note=run["note"], stalled=run["status"] == "abandoned",
            progress=1.0 if ok else estimate(run, max_turns), since=run["ended"],
            tag=("handoff" if ok else "error") if now - (run["ended"] or 0) < TAG_SECONDS else None,
            turns={"used": int(run["tool_uses"] if run["tool_uses"] is not None else run["tool_calls"]), "max": max_turns},
            tokens=run["tokens"], duration_ms=run["duration_ms"],
        )
        return view
    if expected:
        view["state"] = "waiting"
    return view


def build_lanes(roster: dict[str, Any], ledger: dict[str, Any] | None, ran: list[str]) -> list[dict[str, Any]]:
    """Roster lanes holding only the agents worth showing: ran, expected, payable by a reserve, or always-on."""
    agents = roster["agents"]
    shown = set(ran) | possible_agents(ledger) | {name for name, spec in agents.items() if spec.get("always")}
    lanes = []
    placed: set[str] = set()
    for lane in roster["lanes"]:
        members = [name for name in lane["agents"] if name in shown]
        placed.update(members)
        if members:
            lanes.append({"id": lane["id"], "color": lane["color"], "agents": members})
    known = {name for lane in roster["lanes"] for name in lane["agents"]}
    strays = sorted(name for name in shown if name not in placed and name not in known)
    if strays:
        other = roster["other_lane"]
        lanes.append({"id": other["id"], "color": other["color"], "agents": strays})
    return lanes


def new_snapshot(mode: str, now: float, live: bool) -> dict[str, Any]:
    return {
        "version": SNAPSHOT_VERSION, "mode": mode, "now": round(now, 3), "live": live,
        "span": None, "empty": False, "hints": [], "feature": None, "features": [],
        "requirement": None, "boss": {"id": "main", "kind": "robot", "state": "idle", "task": None, "waiting_for": None},
        "phase": {"steps": [], "current": None},
        "progress": {"pct": None, "agents": 0, "total": 0, "running": 0, "done": 0, "blocked": 0},
        "budget": None, "lanes": [], "agents": {}, "edges": [], "log": [], "warnings": [],
    }


def build_claude(inputs: dict[str, Any], roster: dict[str, Any], now: float, live: bool = True) -> dict[str, Any]:
    spec = roster["claude"]
    ledger = inputs.get("ledger")
    all_events = inputs.get("events") or []
    start = window_start(ledger, all_events)
    in_window = [event for event in all_events if start is None or event["ts"] >= start]
    seen = [event for event in in_window if event["ts"] <= now]
    runs, main_activity = assemble_runs(seen, now)
    expected = expected_agents(ledger)
    ran = sorted({run["agent"] for run in runs})
    lanes = build_lanes(spec, ledger, ran)

    snap = new_snapshot("claude", now, live)
    snap["boss"]["kind"] = spec["boss"]["kind"]
    snap["lanes"] = lanes
    visible = [name for lane in lanes for name in lane["agents"]]
    files = inputs.get("agent_files") or {}
    for name in visible:
        snap["agents"][name] = agent_view(name, runs, name in expected, now, spec["agents"].get(name, {}), files.get(name, {}))

    if ledger is not None:
        stamps = [parse_utc(item.get("at")) for item in ledger["invocations"] if isinstance(item, dict)]
        known_stamps = [stamp for stamp in stamps if stamp is not None]
        snap["requirement"] = {
            "id": clip(ledger.get("requirement"), 80) or None, "tier": ledger.get("tier"), "lane": ledger.get("lane") or "claude",
            "strategy": ledger.get("strategy"), "required": list(ledger.get("required_agents", [])),
        }
        snap["budget"] = budget_view(ledger, now)
    else:
        known_stamps = []
    snap["hints"] = ([] if ledger is not None else ["no_ledger"]) + ([] if seen else ["no_events"])
    snap["empty"] = ledger is None and not seen
    stamps = [event["ts"] for event in in_window] + known_stamps
    if start is not None or stamps:
        first = min(stamps + ([start + WINDOW_MARGIN] if start is not None else []))
        snap["span"] = {"start": round(first, 3), "end": round(max(stamps + [now if live else first]), 3)}

    # progress: how many of the roles the route expects have finished
    involved = sorted(expected | set(ran))
    credit = 0.0
    for name in involved:
        view = snap["agents"][name]  # build_lanes shows everything expected or run
        credit += 1.0 if view["state"] == "done" else (view["progress"] or 0.0) if view["state"] in ("working", "reviewing") else 0.0
    running = [run for run in runs if run["ended"] is None]
    snap["progress"] = {
        "pct": round(100 * credit / len(involved)) if involved else None,
        "agents": len(involved),
        "total": len(runs) + len([name for name in involved if name not in ran]),
        "running": len(running),
        "done": sum(1 for run in runs if run["ended"] is not None and run["status"] not in ("failed", "abandoned")),
        "blocked": sum(1 for view in snap["agents"].values() if view["state"] == "blocked"),
    }

    # the main session
    live_runs = [run for run in running if not is_stalled(run, now)]
    boss = snap["boss"]
    if live_runs:
        run = max(live_runs, key=run_start)
        boss.update(state="waiting", task=run["task"], waiting_for=run["agent"])
    elif any(0 <= now - stamp <= MAIN_ACTIVE_SECONDS for stamp in main_activity):
        boss["state"] = "working"
    elif involved and snap["progress"]["pct"] == 100:
        boss["state"] = "done"

    # which phase the main session is in is inferred from the roster, not observed
    phases = {name: info.get("phase") for name, info in spec["agents"].items()}
    snap["phase"] = {"steps": list(PHASES), "current": current_phase(runs, phases)}

    # edges: the main session hands work to an agent, and the agent hands the result back
    for name in visible:
        view = snap["agents"][name]
        if view["state"] in ("working", "reviewing"):
            snap["edges"].append({"from": "main", "to": name, "state": "active"})
        elif view["runs"]:
            snap["edges"].append({"from": "main", "to": name, "state": "done"})
            if view["tag"] == "handoff":
                snap["edges"].append({"from": name, "to": "main", "state": "active"})
        elif name in expected:
            snap["edges"].append({"from": "main", "to": name, "state": "planned"})

    # log: one line when a run starts and one when it ends, newest first
    entries = []
    for run in runs:
        entries.append({"t": round(run_start(run), 3), "kind": "start", "agent": run["agent"], "text": run["task"]})
        if run["ended"] is not None:
            entries.append({"t": round(run["ended"], 3), "kind": "done" if run["status"] not in ("failed", "abandoned") else "fail",
                            "agent": run["agent"], "text": run["note"]})
    entries.sort(key=lambda item: (item["t"], 0 if item["kind"] != "start" else 1))
    snap["log"] = list(reversed(entries))[:LOG_LINES]
    return snap


# ---------------------------------------------------------------------------
# Team view
# ---------------------------------------------------------------------------


def team_position(state: dict[str, Any], verdict: str | None) -> tuple[int, str]:
    """(index into TEAM_STAGES, mode) where mode is working, blocked, waiting or done."""
    stage = str(state.get("stage") or "")
    if stage.startswith("running:"):
        name = stage.split(":", 1)[1].strip()
        return (TEAM_STAGES.index(name) if name in TEAM_STAGES else 0), "working"
    if stage.startswith("blocked"):
        nxt = str(state.get("next") or "")
        return (TEAM_STAGES.index(nxt) if nxt in TEAM_STAGES else 0), "blocked"
    if stage == "ready for audit":
        if verdict == "APPROVE":
            return TEAM_STAGES.index("audit"), "done"
        if verdict == "BLOCK":
            return TEAM_STAGES.index("audit"), "blocked"
        return TEAM_STAGES.index("audit"), "waiting"
    # `team new` leaves stage "spec" until `team run`: the pipeline has not started, a person is writing the spec.
    return 0, "waiting"


def gates_result(files: dict[str, Any]) -> tuple[str, int, int] | None:
    text = (files.get("gates.log") or {}).get("text") or ""
    found = GATES_RESULT_RE.findall(text)
    if not found:
        return None
    verdict, passed, total = found[-1]
    return verdict, int(passed), int(total)


def build_team(features: list[dict[str, Any]], roster: dict[str, Any], now: float, feature_id: str | None = None,
               live: bool = True, span: dict[str, float] | None = None) -> dict[str, Any]:
    spec = roster["team"]
    snap = new_snapshot("team", now, live)
    snap["boss"].update(kind=spec["boss"]["kind"])
    snap["features"] = [item["id"] for item in features]
    snap["span"] = span
    chosen = next((item for item in features if item["id"] == feature_id), None) if feature_id else None
    if chosen is None and features:
        chosen = max(features, key=lambda item: item["updated"])
    if chosen is None:
        snap["empty"], snap["hints"] = True, ["no_features"]
        snap["lanes"] = [{"id": lane["id"], "color": lane["color"], "agents": list(lane["agents"])} for lane in spec["lanes"]]
        for name in (n for lane in spec["lanes"] for n in lane["agents"]):
            snap["agents"][name] = team_agent(name, "idle", None, spec)
        return snap

    state, files = chosen["state"], chosen["files"]
    verdict_text = (files.get("verdict.md") or {}).get("text") or ""
    match = VERDICT_RE.search(verdict_text)
    verdict = match.group(1) if match else None
    index, mode = team_position(state, verdict)
    gate = gates_result(files)
    reason = clip(str(state.get("stage") or "").partition(":")[2], 160) if mode == "blocked" and str(state.get("stage")).startswith("blocked") else None
    stage_agent = {"spec": "claude-spec", "tester": "tester", "coder": "coder", "review": "reviewer", "pack": "pack", "audit": "claude-audit"}
    models = {"tester": state.get("tester_model"), "coder": state.get("coder_model"), "reviewer": state.get("reviewer_model")}
    updated = chosen["updated"]

    snap["feature"] = chosen["id"]
    snap["requirement"] = {"id": chosen["id"], "tier": None, "lane": "team", "strategy": "team_pipeline",
                           "required": [], "base": clip(state.get("base"), 40)}
    snap["lanes"] = [{"id": lane["id"], "color": lane["color"], "agents": list(lane["agents"])} for lane in spec["lanes"]]
    for position, stage in enumerate(TEAM_STAGES):
        name = stage_agent[stage]
        if position < index:
            view = team_agent(name, "done", models.get(name), spec, progress=1.0)
        elif position > index:
            view = team_agent(name, "waiting", models.get(name), spec)
        elif mode == "blocked":
            view = team_agent(name, "blocked", models.get(name), spec, note=reason or ("BLOCK" if verdict == "BLOCK" else None))
        elif mode == "waiting":
            view = team_agent(name, "waiting", models.get(name), spec, note="awaiting_audit" if stage == "audit" else "awaiting_spec")
        elif mode == "done":
            view = team_agent(name, "done", models.get(name), spec, progress=1.0, note="APPROVE")
        else:
            running = "reviewing" if spec["agents"][name].get("mode") == "reviewing" else "working"
            view = team_agent(name, running, models.get(name), spec, since=updated)
        snap["agents"][name] = view
    # Gates run after each coder attempt, inside the coder stage. A red result is shown as blocked,
    # not done: the bar is the share of acceptance commands that pass, and the coder is retrying.
    coder_index = TEAM_STAGES.index("coder")
    if index > coder_index or (index == coder_index and gate is not None and gate[0] == "PASS"):
        snap["agents"]["gates"] = team_agent("gates", "done", None, spec, progress=1.0, note=gate_note(gate))
    elif index == coder_index and gate is not None:
        share = gate[1] / gate[2] if gate[2] else 0.0
        snap["agents"]["gates"] = team_agent("gates", "blocked", None, spec, progress=round(share, 3), note=gate_note(gate))
    else:
        snap["agents"]["gates"] = team_agent("gates", "waiting", None, spec)

    working = [view for view in snap["agents"].values() if view["state"] in ("working", "reviewing")]
    boss = snap["boss"]
    # the conductor is a script: while a stage runs it is waiting on that stage's worker
    boss["state"] = "waiting" if mode == "working" else mode
    if mode == "waiting":
        boss["waiting_for"] = stage_agent[TEAM_STAGES[index]]
    elif mode == "working" and working:
        boss["waiting_for"] = working[0]["id"]
    finished = sum(1 for view in snap["agents"].values() if view["state"] == "done" and view["id"] != "gates")
    snap["progress"] = {
        "pct": round(100 * (index + (0.5 if mode == "working" else 1.0 if mode == "done" else 0)) / len(TEAM_STAGES)),
        "agents": len(snap["agents"]), "total": len(TEAM_STAGES), "running": len(working), "done": finished,
        "blocked": sum(1 for view in snap["agents"].values() if view["state"] == "blocked"),
    }
    snap["phase"] = {"steps": list(TEAM_STAGES), "current": "done" if mode == "done" else TEAM_STAGES[index]}

    # edges follow the chain the pipeline runs in
    def edge(src: str, dst: str) -> None:
        target = snap["agents"][dst]["state"] if dst != "main" else boss["state"]
        state_name = "active" if target in ("working", "reviewing") else "done" if target == "done" else "planned"
        snap["edges"].append({"from": src, "to": dst, "state": state_name})

    snap["edges"].append({"from": "claude-spec", "to": "main", "state": "done" if index > 0 else "active"})
    for dst in ("tester", "coder", "reviewer", "pack"):
        edge("main", dst)
    edge("coder", "gates")
    if gate is not None and gate[0] == "FAIL" and index == coder_index:
        snap["edges"].append({"from": "gates", "to": "coder", "state": "active"})
    edge("pack", "claude-audit")

    entries = []
    for name, stamp, text, failed in (("claude-spec", (files.get("spec.md") or {}).get("mtime"), None, False),
                                      ("gates", (files.get("gates.log") or {}).get("mtime"), gate_note(gate), bool(gate and gate[0] == "FAIL")),
                                      ("reviewer", (files.get("prereview.md") or {}).get("mtime"), None, False),
                                      ("pack", (files.get("audit-pack.md") or {}).get("mtime"), None, False),
                                      ("claude-audit", (files.get("verdict.md") or {}).get("mtime"), verdict, verdict == "BLOCK")):
        if stamp is not None and stamp <= now:
            entries.append({"t": round(stamp, 3), "kind": "fail" if failed else "done", "agent": name, "text": text})
    if mode == "working" and working:  # state.json is saved when a stage starts, so its time is when this worker began
        entries.append({"t": round(updated, 3), "kind": "start", "agent": working[0]["id"], "text": None})
    for warning in state.get("warnings") or []:
        text = clip(str(warning), 200)
        if text:
            entries.append({"t": round(updated, 3), "kind": "warn", "agent": "main", "text": text})
            snap["warnings"].append(text)
    entries.sort(key=lambda item: item["t"], reverse=True)
    snap["log"] = entries[:LOG_LINES]
    return snap


def gate_note(gate: tuple[str, int, int] | None) -> str | None:
    return None if gate is None else f"{gate[0]} {gate[1]}/{gate[2]}"


def team_agent(name: str, state: str, model: Any, spec: dict[str, Any], progress: float | None = None,
               note: str | None = None, since: float | None = None) -> dict[str, Any]:
    kind = spec["agents"].get(name, {}).get("kind", "robot")
    return {
        "id": name, "state": state, "task": None, "note": note, "progress": progress, "tag": None, "since": since,
        "runs": 0, "turns": None, "model": clip(model, 80) if isinstance(model, str) else None, "effort": None,
        "tokens": None, "duration_ms": None, "stalled": False, "kind": kind,
    }


# ---------------------------------------------------------------------------
# Demos: recorded sample runs the same reducers replay
# ---------------------------------------------------------------------------


def demo_names() -> list[str]:
    return sorted(path.name for path in DEMO_DIR.iterdir() if path.is_dir()) if DEMO_DIR.is_dir() else []


def load_demo(name: str) -> dict[str, Any]:
    """`{mode, inputs, span}` for a bundled sample; raises KeyError for a name that is not one."""
    if name not in demo_names():
        raise KeyError(name)
    directory = DEMO_DIR / name
    meta = json.loads((directory / "meta.json").read_text(encoding="utf-8"))
    if meta["mode"] == "claude":
        events = read_events(directory / "events.jsonl")
        ledger = json.loads((directory / "ledger.json").read_text(encoding="utf-8"))
        inputs = {"events": events, "ledger": ledger, "agent_files": meta.get("agent_files", {})}
        span = {"start": meta["start"], "end": max([meta.get("end", 0)] + [event["ts"] for event in events])}
        return {"mode": "claude", "inputs": inputs, "span": span}
    frames = json.loads((directory / "frames.json").read_text(encoding="utf-8"))
    span = {"start": frames[0]["t"], "end": frames[-1]["t"]}
    return {"mode": "team", "inputs": {"frames": frames}, "span": span}


def build_demo(name: str, roster: dict[str, Any], at: float | None = None) -> dict[str, Any]:
    """The sample's snapshot at epoch `at`, or at its start when not given."""
    demo = load_demo(name)
    span = demo["span"]
    now = span["start"] if at is None else at
    if demo["mode"] == "claude":
        snap = build_claude(demo["inputs"], roster, now, live=False)
    else:
        frames = [frame for frame in demo["inputs"]["frames"] if frame["t"] <= now] or demo["inputs"]["frames"][:1]
        snap = build_team([frames[-1]["feature"]], roster, now, live=False, span=span)
    snap["span"] = span
    snap["demo"] = name
    return snap


# ---------------------------------------------------------------------------
# Validation (the schema, as code)
# ---------------------------------------------------------------------------


def validate(snap: Any) -> list[str]:
    """Every way `snap` breaks the v1 contract the UI is written against; empty means valid."""
    problems: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            problems.append(message)

    if not isinstance(snap, dict):
        return ["snapshot is not an object"]
    need(snap.get("version") == SNAPSHOT_VERSION, f"version is not {SNAPSHOT_VERSION}")
    need(snap.get("mode") in MODES, "mode is not claude or team")
    need(number(snap.get("now")) is not None, "now is not a number")
    need(isinstance(snap.get("live"), bool), "live is not a boolean")
    span = snap.get("span")
    need(span is None or (isinstance(span, dict) and number(span.get("start")) is not None and number(span.get("end")) is not None
                          and span["start"] <= span["end"]), "span is not null or {start <= end}")
    boss = snap.get("boss")
    need(isinstance(boss, dict) and boss.get("state") in STATES, "boss.state is not a known state")
    agents = snap.get("agents")
    need(isinstance(agents, dict), "agents is not an object")
    agents = agents if isinstance(agents, dict) else {}
    for name, view in agents.items():
        if not isinstance(view, dict):
            problems.append(f"agent {name}: not an object")
            continue
        need(view.get("id") == name, f"agent {name}: id differs from its key")
        need(view.get("state") in STATES, f"agent {name}: unknown state {view.get('state')!r}")
        need(view.get("kind") in ("robot", "script"), f"agent {name}: unknown avatar kind {view.get('kind')!r}")
        progress = view.get("progress")
        need(progress is None or (number(progress) is not None and 0 <= progress <= 1), f"agent {name}: progress outside 0..1")
        if view.get("state") in ("working", "reviewing") and progress is not None:
            need(progress <= PROGRESS_CAP, f"agent {name}: a running agent reports more than {PROGRESS_CAP}")
    lanes = snap.get("lanes")
    need(isinstance(lanes, list), "lanes is not a list")
    placed: list[str] = []
    for lane in lanes if isinstance(lanes, list) else []:
        members = lane.get("agents") if isinstance(lane, dict) else None
        need(isinstance(members, list) and bool(members), "a lane is empty or malformed")
        for member in members or []:
            placed.append(member)
            need(member in agents, f"lane member {member} has no agent entry")
    need(sorted(placed) == sorted(agents), "every agent must sit in exactly one lane")
    for edge in snap.get("edges") or []:
        need(isinstance(edge, dict) and edge.get("state") in EDGE_STATES, f"edge has an unknown state: {edge!r}")
        if isinstance(edge, dict):
            for end in (edge.get("from"), edge.get("to")):
                need(end == "main" or end in agents, f"edge end {end!r} is not main or an agent")
    for entry in snap.get("log") or []:
        need(isinstance(entry, dict) and entry.get("kind") in LOG_KINDS and number(entry.get("t")) is not None,
             f"log entry is malformed: {entry!r}")
    progress = snap.get("progress")
    need(isinstance(progress, dict), "progress is not an object")
    if isinstance(progress, dict):
        pct = progress.get("pct")
        need(pct is None or (isinstance(pct, int) and 0 <= pct <= 100), "progress.pct is not null or an integer 0..100")
        for key in ("agents", "total", "running", "done", "blocked"):
            need(isinstance(progress.get(key), int) and progress[key] >= 0, f"progress.{key} is not a non-negative integer")
    for slot in snap.get("budget") or []:
        need(isinstance(slot, dict) and all(isinstance(slot.get(key), int) for key in ("cap", "granted", "used")),
             f"budget slot is malformed: {slot!r}")
        if isinstance(slot, dict) and all(isinstance(slot.get(key), int) for key in ("cap", "granted", "used")):
            need(slot["used"] <= slot["granted"] <= slot["cap"], f"budget slot {slot.get('id')}: used > granted or granted > cap")
    phase = snap.get("phase")
    need(isinstance(phase, dict) and isinstance(phase.get("steps"), list), "phase.steps is not a list")
    if isinstance(phase, dict) and phase.get("current") is not None and phase.get("steps"):
        need(phase["current"] in list(phase["steps"]) + ["done"], "phase.current is not one of the steps")
    return problems


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def repo_root() -> Path:
    env_root = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(env_root) if env_root else SCRIPT_DIR.parents[1]


def team_home() -> Path:
    return Path(os.environ.get("TEAM_HOME", "/srv/team"))


def build_live(mode: str, root: Path, home: Path, now: float | None = None, at: float | None = None,
               feature: str | None = None) -> dict[str, Any]:
    """The snapshot for the real checkout: `at` replays an earlier moment, otherwise it is as of `now`."""
    roster = load_roster()
    moment = time.time() if now is None else now
    if mode == "claude":
        return build_claude(load_claude_inputs(root), roster, moment if at is None else at, live=at is None)
    return build_team(load_team_features(home), roster, moment, feature_id=feature, live=True)


def check_demos() -> list[str]:
    """Validate every bundled demo at its start, middle and end, and each empty live view."""
    roster = load_roster()
    problems: list[str] = []
    for name in demo_names():
        span = load_demo(name)["span"]
        for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
            when = span["start"] + (span["end"] - span["start"]) * fraction
            problems += [f"demo {name} at {fraction}: {item}" for item in validate(build_demo(name, roster, when))]
    with tempfile.TemporaryDirectory() as nothing:
        for mode in MODES:
            snap = build_live(mode, Path(nothing), Path(nothing))
            problems += [f"empty {mode}: {item}" for item in validate(snap)]
    return problems


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mode", choices=MODES, default="claude")
    parser.add_argument("--root", type=Path, default=None, help="checkout holding artifacts/handoff (default: this one)")
    parser.add_argument("--team-home", type=Path, default=None, help="team.py home (default: $TEAM_HOME or /srv/team)")
    parser.add_argument("--feature", help="team feature id (default: the most recently updated)")
    parser.add_argument("--demo", choices=demo_names() or None, help="render a bundled sample run instead of live data")
    parser.add_argument("--at", type=float, help="with --demo: position in the run, 0..1")
    parser.add_argument("--check", action="store_true", help="validate the demos and the empty views, then exit")
    args = parser.parse_args(argv[1:])
    if args.check:
        problems = check_demos()
        for problem in problems:
            print(problem, file=sys.stderr)
        print("snapshot schema: " + ("ok" if not problems else f"{len(problems)} problem(s)"))
        return 1 if problems else 0
    if args.demo:
        span = load_demo(args.demo)["span"]
        at = span["start"] + (span["end"] - span["start"]) * (args.at if args.at is not None else 0.0)
        snap = build_demo(args.demo, load_roster(), at)
    else:
        snap = build_live(args.mode, args.root or repo_root(), args.team_home or team_home(), feature=args.feature)
    print(json.dumps(snap, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
