#!/usr/bin/env python3
"""Preview of a github-radar draft pull request: what it adds, whether this workflow may draw it, and the comment that shows it.

github-radar opens a draft pull request (branch `radar/<campaign>`) that adds one campaign, `tools/github-radar/`
and nothing else. `.github/workflows/radar-preview.yml` checks that campaign, draws its images and texts with this
repository's own engine, and attaches them to the run, so the owner can look at the post before approving it.
Nothing is approved, committed or published there.

Two commands, both reading and writing only what the workflow hands them:

  plan     lists the files the pull request changed and decides. The engine of a pull request is code that would run
           on the persistent runner, so a pull request that changes anything outside `campaigns/radar-<date>[-n]/`
           and `tools/github-radar/`, or any path that is or sits under a symbolic link, is not drawn; its comment
           says why. The workflow runs both commands from the base commit, read out of git into the runner's temp
           folder (`--root` names the pull request's tree), so a pull request cannot change them before they judge it. That is not a boundary against
           someone who can already push a branch here: GitHub runs the workflow file of the pull request's merge, so
           that person can change the workflow itself, exactly as with ci.yml. Writes `ok`, `campaigns` and
           `export_paths` to GITHUB_OUTPUT.
  comment  builds the Markdown of the one comment the workflow keeps on the pull request, from the manifests the
           renderer wrote and the texts beside them.
"""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import subprocess
import sys
import uuid
from collections.abc import Mapping, Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ci_changes  # noqa: E402 - one reading of "what did this pull request change" for every workflow

ROOT = Path(__file__).resolve().parent.parent
MARKER = "<!-- radar-preview -->"
CAMPAIGN = re.compile(r"campaigns/(radar-[0-9]{4}-[0-9]{2}-[0-9]{2}(?:-[0-9]+)?)/")   # [0-9]: \d also matches other scripts' digits
DATA_PREFIXES = ("tools/github-radar/",)
CAPTION_LIMIT = 3000        # one caption
CAPTION_BUDGET = 30000      # all the captions of one comment, fences and headings included
TABLE_BUDGET = 15000        # all the rows of its table
OVERFLOW_SHOWN = 10         # slide numbers named in one row
BODY_LIMIT = 60000          # GitHub refuses a comment of 65536 characters: the budgets above keep the parts under this one
NEXT = ("Next: look at the images, then approve in the app (Publish page) or with `studio.py approve`. "
        "Publishing stays yours.")


def classify(paths: Sequence[str]) -> tuple[list[str], list[str]]:
    """(radar campaigns the paths add to, paths that are neither a radar campaign nor radar's tool data)."""
    campaigns: set[str] = set()
    outside: list[str] = []
    for path in paths:
        found = CAMPAIGN.match(path)
        if posixpath.normpath(path) != path:                   # `campaigns/radar-x/../../scripts/y.py` is not inside
            outside.append(path)
        elif found:
            campaigns.add(found.group(1))
        elif not path.startswith(DATA_PREFIXES):
            outside.append(path)
    return sorted(campaigns), outside


def symlinked(root: Path, paths: Sequence[str]) -> list[str]:
    """The changed paths that are a symbolic link: the engine would write through one, an upload would follow it.
    Only the path itself is looked at: git cannot hold a file beneath a link it tracks, so a link anywhere above a changed
    path is itself a changed path (or an unchanged one that nothing can be added under)."""
    return [path for path in paths if (root / path).is_symlink()]


def decide(changed: Sequence[str] | None, linked: Sequence[str] = ()) -> tuple[bool, list[str], list[str], str]:
    """(may the pull request be drawn, its campaigns, files outside, one-line reason)."""
    if not changed:
        return False, [], [], "the changed files could not be read, so nothing is drawn"
    if linked:
        return False, [], list(linked), f"{len(linked)} changed path(s) are or sit under a symbolic link, e.g. {safe(linked[0])}"
    campaigns, outside = classify(changed)
    if outside:
        return False, campaigns, outside, f"{len(outside)} changed file(s) are not radar data, e.g. {safe(outside[0])}"
    if not campaigns:
        return False, [], [], "no radar campaign among the changed files"
    return True, campaigns, [], f"{len(campaigns)} radar campaign(s): {', '.join(campaigns)}"


def safe(text: str) -> str:
    """Only what a slug or a path needs: a link, a mention or HTML in a file name cannot reach the comment."""
    return re.sub(r"[^A-Za-z0-9._/-]", "?", text)


def pr_base(environ: Mapping[str, str], cwd: Path | None) -> str:
    """What the pull request's changes are measured from. In CI HEAD is GitHub's merge of the pull request into its
    base, and that merge's first parent is the base as it is now, so a base that moved after the event does not put
    its own files into the pull request. Anywhere else (or on any doubt) it is the base sha the event named."""
    try:
        parents = subprocess.run(["git", "rev-list", "--parents", "-n", "1", "HEAD"], cwd=cwd, capture_output=True, text=True,
                                 check=True, timeout=60).stdout.split()
    except (OSError, subprocess.SubprocessError):
        parents = []
    return parents[1] if len(parents) == 3 else environ.get("PR_BASE_SHA", "")


def printable(text: str) -> str:
    """One line a person can read: a file name may hold a newline or a backtick, which would end a Markdown span."""
    return re.sub(r"[`\x00-\x1f\x7f]", "?", text)


def write_outputs(path: str | None, values: Mapping[str, str]) -> None:
    """Append `values` to GITHUB_OUTPUT. The delimiter is random: a file name that holds a newline and the delimiter
    cannot end its block early and set an output of its own."""
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            delimiter = f"RADAR_EOF_{uuid.uuid4().hex}"
            handle.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")


def cmd_plan(environ: Mapping[str, str], cwd: Path | None = None) -> int:
    changed = ci_changes.changed_files(pr_base(environ, cwd), cwd)
    ok, campaigns, outside, reason = decide(changed, symlinked(cwd or Path.cwd(), changed or []))
    print(f"radar_preview: {'draw' if ok else 'do not draw'}: {reason}")
    write_outputs(environ.get("GITHUB_OUTPUT"), {
        "ok": "true" if ok else "false",
        "campaigns": " ".join(campaigns) if ok else "",
        "export_paths": "\n".join(f"campaigns/{c}/export/**" for c in campaigns) if ok else "",
        "reason": reason,
        "outside": "\n".join(safe(p) for p in outside[:5]),     # a file name may hold bytes that are not UTF-8: the writer would raise
    })
    return 0


def fence(text: str) -> str:
    """A code fence longer than any backtick run in `text`, so the caption cannot close it and write Markdown outside."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def rendered(root: Path, campaign: str) -> tuple[list[dict], list[str]]:
    """The posts the renderer drew, and the manifests that could not be read (a committed file the renderer did not
    replace, because that post failed its check). The comment that reports a failure must not fail on one."""
    rows, unreadable = [], []
    for manifest in sorted((root / "campaigns" / campaign / "export").glob("*/*/manifest.json")):
        folder = manifest.parent
        where = f"{safe(folder.parent.name)}/{safe(folder.name)}"
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("a manifest is a JSON object")
            slides, overflow = data.get("slides", []), data.get("overflow", [])
            caption = folder / "facebook.txt"
            text = caption.read_text(encoding="utf-8") if caption.exists() else ""
        except (OSError, ValueError):                       # JSONDecodeError and UnicodeDecodeError are ValueErrors
            unreadable.append(where)
            continue
        rows.append({"where": where, "slides": len(slides) if isinstance(slides, list) else 0,
                     "overflow": [safe(str(n)) for n in overflow] if isinstance(overflow, list) else [],
                     "sha": safe(str(data.get("sha", ""))[:12]), "caption": text})
    return rows, unreadable


def build_comment(root: Path, *, plan_ok: bool, campaigns: Sequence[str], reason: str, outside: Sequence[str],
                  failed: bool, artifact_url: str, run_url: str) -> str:
    """The comment, never longer than BODY_LIMIT: past it the API refuses the post and the old comment goes on saying what it said.
    The parts are budgeted (captions, table), so this is the backstop for what no budget counts; it states nothing about the checks."""
    body = _comment(root, plan_ok=plan_ok, campaigns=campaigns, reason=reason, outside=outside, failed=failed,
                    artifact_url=artifact_url, run_url=run_url)
    if len(body) <= BODY_LIMIT:
        return body
    return "\n".join([MARKER, "### Radar preview", "",
                      f"This preview is too large for one comment, so it says nothing about the check or the drawing: read [the run]({run_url}).",
                      "", NEXT]) + "\n"


def _comment(root: Path, *, plan_ok: bool, campaigns: Sequence[str], reason: str, outside: Sequence[str],
             failed: bool, artifact_url: str, run_url: str) -> str:
    lines = [MARKER, "### Radar preview", ""]
    if not plan_ok:
        lines += ["Not drawn here: " + printable(reason) + ".", ""]
        if outside:
            lines += ["Files outside radar data:", ""] + [f"- `{safe(p)}`" for p in outside[:5]] + [""]
        lines += ["This workflow draws only pull requests that change nothing but `campaigns/radar-*/` and "
                  "`tools/github-radar/`: the engine of a pull request is code, and it would run on the shared runner. "
                  "The ordinary CI still checks this pull request.", ""]
        return "\n".join(lines)
    found = [(c, *rendered(root, c)) for c in campaigns]
    rows = [(c, r) for c, got, _ in found for r in got]
    unreadable = [f"{c}/{where}" for c, _, bad in found for where in bad]
    if failed or unreadable or not rows:
        # the claim is made only when every step succeeded and something was drawn: a skipped check or an empty drawing is not "drawn"
        lines += ["The check and the drawing were attempted with this repository's engine on the files of this pull request, "
                  "but they did not all succeed. Nothing is approved, committed or published.", ""]
    else:
        lines += ["Checked and drawn with this repository's engine from the files of this pull request. "
                  "Nothing is approved, committed or published.", ""]
    if failed or unreadable:
        lines += [f"**A step failed or a manifest could not be read: read [the run]({run_url}).**", ""]
    if unreadable:
        lines += ["Manifests that could not be read:", ""] + [f"- `{w}`" for w in unreadable[:5]] + [""]
    if rows:
        lines += ["| Campaign | Post | Slides | Slides that overflow | Drawn from |", "|---|---|---|---|---|"]
        listed, used = 0, 0
        for c, r in rows:
            overflow = ", ".join(r["overflow"][:OVERFLOW_SHOWN]) + (f" (+{len(r['overflow']) - OVERFLOW_SHOWN} more)" if len(r["overflow"]) > OVERFLOW_SHOWN else "")
            row = f"| {c} | {r['where']} | {r['slides']} | {overflow or 'none'} | `{r['sha']}` |"
            if used + len(row) > TABLE_BUDGET:
                break
            lines.append(row)
            listed, used = listed + 1, used + len(row)
        if listed < len(rows):
            lines += ["", f"{len(rows) - listed} more post(s) are not listed here: they are in the artifact."]
        if artifact_url:
            lines += ["", f"Images and texts: [download the artifact]({artifact_url}) (one zip; the same files are on [the run]({run_url})).", ""]
        else:
            lines += ["", f"The images and texts could not be attached to the run: read [the run]({run_url}).", ""]
        omitted, used = 0, 0
        for c, r in rows:
            whole = r["caption"].strip()
            caption = whole[:CAPTION_LIMIT]
            if not caption:
                continue
            bar = fence(caption)
            # a caption that is shown in part says so where a collapsed reader sees it: approving needs the whole text
            cut = f" · cut: the first {len(caption)} of {len(whole)} characters" if len(whole) > len(caption) else ""
            block = [f"<details><summary>Facebook caption · {r['where']}{cut}</summary>", "", f"{bar}text", caption, bar, ""]
            if cut:
                block += ["The rest of the caption is in `facebook.txt` beside this post, in the artifact.", ""]
            block += ["</details>", ""]
            size = sum(len(line) + 1 for line in block)
            if used + size > CAPTION_BUDGET:
                omitted += 1
                continue
            lines += block
            used += size
        if omitted:
            lines += [f"{omitted} caption(s) are not shown here: they are in the artifact, as `facebook.txt` beside each post.", ""]
    elif not unreadable:
        lines += ["No post was drawn.", ""]
    lines += [NEXT]
    return "\n".join(lines) + "\n"


def cmd_comment(args: argparse.Namespace) -> int:
    """`failed` is any step of a drawn pull request whose outcome is not `success`: a skipped check or drawing (the install
    failed before them) and a failed upload both leave the comment unable to say the pull request was checked and drawn."""
    body = build_comment(Path(args.root) if args.root else ROOT, plan_ok=args.plan_ok == "true", campaigns=args.campaigns.split(), reason=args.reason,
                         outside=[p for p in args.outside.splitlines() if p],
                         failed=any(outcome != "success" for outcome in (args.install, args.check, args.render, args.upload)),
                         artifact_url=args.artifact_url, run_url=args.run_url)
    Path(args.out).write_text(body, encoding="utf-8")
    print(f"radar_preview: comment written to {args.out} ({len(body)} characters)")
    return 0


def main(argv: Sequence[str] | None = None, environ: Mapping[str, str] | None = None, cwd: Path | None = None) -> int:
    environ = os.environ if environ is None else environ
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("plan", help="decide whether the pull request may be drawn (reads PR_BASE_SHA)")
    comment = sub.add_parser("comment", help="write the Markdown of the pull request comment")
    for name in ("plan-ok", "campaigns", "reason", "outside", "install", "check", "render", "upload", "artifact-url", "run-url"):
        comment.add_argument(f"--{name}", default="")
    comment.add_argument("--root", default="", help="the checkout holding the drawn export folders (default: this script's repository)")
    comment.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    return cmd_plan(environ, cwd) if args.command == "plan" else cmd_comment(args)


if __name__ == "__main__":
    sys.exit(main())
