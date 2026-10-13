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
           says why. This is a safety net for a bot pull request that carries code by accident, not a boundary
           against someone who can already push a branch here: that person can change the workflow itself, which
           runs on the same runner, exactly as with ci.yml. Writes `ok`, `campaigns` and `export_paths` to
           GITHUB_OUTPUT.
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
CAPTION_LIMIT = 3000


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
        "outside": "\n".join(outside[:5]),
    })
    return 0


def fence(text: str) -> str:
    """A code fence longer than any backtick run in `text`, so the caption cannot close it and write Markdown outside."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def rendered(root: Path, campaign: str) -> list[dict]:
    rows = []
    for manifest in sorted((root / "campaigns" / campaign / "export").glob("*/*/manifest.json")):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        folder = manifest.parent
        caption = folder / "facebook.txt"
        rows.append({"lang": safe(folder.parent.name), "post": safe(folder.name), "slides": len(data.get("slides", [])),
                     "overflow": data.get("overflow", []), "sha": str(data.get("sha", ""))[:12],
                     "caption": caption.read_text(encoding="utf-8") if caption.exists() else ""})
    return rows


def build_comment(root: Path, *, plan_ok: bool, campaigns: Sequence[str], reason: str, outside: Sequence[str],
                  failed: bool, artifact_url: str, run_url: str) -> str:
    lines = [MARKER, "### Radar preview", ""]
    if not plan_ok:
        lines += ["Not drawn here: " + printable(reason) + ".", ""]
        if outside:
            lines += ["Files outside radar data:", ""] + [f"- `{printable(p)}`" for p in outside[:5]] + [""]
        lines += ["This workflow draws only pull requests that change nothing but `campaigns/radar-*/` and "
                  "`tools/github-radar/`: the engine of a pull request is code, and it would run on the shared runner. "
                  "The ordinary CI still checks this pull request.", ""]
        return "\n".join(lines)
    lines += ["Checked and drawn with this repository's engine from the files of this pull request. "
              "Nothing is approved, committed or published.", ""]
    if failed:
        lines += [f"**A check or the drawing failed: read [the run]({run_url}).**", ""]
    rows = [(c, r) for c in campaigns for r in rendered(root, c)]
    if rows:
        lines += ["| Campaign | Post | Slides | Slides that overflow | Drawn from |", "|---|---|---|---|---|"]
        lines += [f"| {c} | {r['lang']}/{r['post']} | {r['slides']} | "
                  f"{', '.join(map(str, r['overflow'])) or 'none'} | `{r['sha']}` |" for c, r in rows]
        lines += ["", f"Images and texts: [download the artifact]({artifact_url}) (one zip; the same files are on [the run]({run_url})).", ""]
        for c, r in rows:
            caption = r["caption"].strip()[:CAPTION_LIMIT]
            if caption:
                bar = fence(caption)
                lines += [f"<details><summary>Facebook caption · {r['lang']}/{r['post']}</summary>", "",
                          f"{bar}text", caption, bar, "", "</details>", ""]
    else:
        lines += ["No post was drawn.", ""]
    lines += ["Next: look at the images, then approve in the app (Publish page) or with `studio.py approve`. "
              "Publishing stays yours."]
    return "\n".join(lines) + "\n"


def cmd_comment(args: argparse.Namespace) -> int:
    body = build_comment(ROOT, plan_ok=args.plan_ok == "true", campaigns=args.campaigns.split(), reason=args.reason,
                         outside=[p for p in args.outside.splitlines() if p],
                         failed=args.check == "failure" or args.render == "failure",
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
    for name in ("plan-ok", "campaigns", "reason", "outside", "check", "render", "artifact-url", "run-url"):
        comment.add_argument(f"--{name}", default="")
    comment.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    return cmd_plan(environ, cwd) if args.command == "plan" else cmd_comment(args)


if __name__ == "__main__":
    sys.exit(main())
