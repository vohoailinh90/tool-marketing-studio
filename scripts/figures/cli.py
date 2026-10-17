"""`python3 -m scripts.figures`: build, check, render and preview the System Design figures (docs/figures.md).

  build [SPEC ...]     write system-design-101/vi/diagrams/<id>-main.svg from each spec (default: every spec in system-design-101/figures/vi)
  check [SPEC ...]     every spec is valid, its stored figure is exactly what the spec draws, the figure passes the store's SVG rules and the
                       phone-size rules, the icon set is intact; --browser also measures every line in Chromium
  render SPEC          one format to a file or stdout: svg, drawio, excalidraw or moda (--out, --scale for the editor files)
  preview SPEC         a PNG of the figure to look at, in Chromium (default build/figures/<id>.png)
  facebook SPEC        the figure as Facebook slides, one PNG per section at the studio's size (default build/figures/facebook/<id>/)
  icons                the icon names a spec may use and what each means; --verify checks the vendored files

Exit 0 when nothing is wrong, 1 for a problem in a spec or a figure, 2 when the command cannot run.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import tempfile
from pathlib import Path

from . import browser, drawio, excalidraw, facebook, icons, mobile, moda, spec as specs, svg

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "system-design-101"
SPEC_DIR = STORE / "figures" / "vi"
DIAGRAMS = STORE / "vi" / "diagrams"
LESSONS = STORE / "vi" / "lessons"
MIN_SCALE, MAX_SCALE = 0.25, 8.0
EDITORS = {"drawio": (".drawio", drawio.diagram), "excalidraw": (".excalidraw", excalidraw.board), "moda": ("-moda.xml", moda.markup)}
LESSON_ID = re.compile(r"sd-\d{2}-\d{3}")


def _write(path: Path, content: str) -> bool:
    """Writes `content` (LF line ends) unless the file already has exactly it; True when it wrote."""
    if path.is_file() and path.read_bytes() == content.encode("utf-8"):
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))
    return True


def _store_problem(markup: str) -> str | None:
    """The System Design store's own verdict on a figure (scripts/sd101_check.py), asked of a temporary file."""
    from scripts import sd101_check

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "figure.svg"
        path.write_text(markup, encoding="utf-8")
        return sd101_check.svg_problem(path)


def figure_problems(spec: dict, markup: str) -> list[str]:
    found = [f"{spec['id']}: {p}" for p in mobile.check(markup)]
    reason = _store_problem(markup)
    if reason:
        found.append(f"{spec['id']}: the figure {reason}")
    return found


def _spec_paths(names: list[str]) -> list[Path]:
    return [Path(n) for n in names] if names else sorted(SPEC_DIR.glob("*.json"))


def _load_each(paths: list[Path]) -> tuple[list[tuple[Path, dict]], list[str]]:
    """Each spec that loads with the path it came from, and the problems of the ones that do not."""
    loaded, found = [], []
    for path in paths:
        try:
            loaded.append((path, specs.load(path)))
        except specs.SpecError as exc:
            found.extend(exc.args[0])
    return loaded, found


def _load(paths: list[Path]) -> tuple[list[dict], list[str]]:
    loaded, found = _load_each(paths)
    return [spec for _, spec in loaded], found


def _shown(path: Path) -> Path:
    """The path as a sentence shows it: relative to the repository when it is inside it."""
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def scale_argument(text: str) -> float:
    """A finite scale from MIN_SCALE to MAX_SCALE: anything else would draw garbage, text too small to see or a huge file."""
    try:
        value = float(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{text!r} is not a number") from exc
    if not math.isfinite(value) or not MIN_SCALE <= value <= MAX_SCALE:
        raise argparse.ArgumentTypeError(f"must be from {MIN_SCALE:g} to {MAX_SCALE:g}")
    return value


def build(paths: list[Path], out) -> int:
    broken = [f"icons: {p}" for p in icons.verify()]
    if broken:                                               # a tampered icon file is never drawn into a stored figure
        print("\n".join(broken), file=sys.stderr)
        return 1
    loaded, found = _load(paths)
    for spec in loaded:
        if not LESSON_ID.fullmatch(spec["id"]) or not (LESSONS / spec["id"]).is_dir():
            found.append(f"{spec['id']}: there is no lesson of that id in {LESSONS.relative_to(ROOT)}; use `render` for a trial figure")
            continue
        markup = svg.figure(spec)
        problems = figure_problems(spec, markup)
        found.extend(problems)
        if not problems:
            changed = _write(DIAGRAMS / f"{spec['id']}-main.svg", markup)
            print(f"{spec['id']}: {'wrote' if changed else 'unchanged'} {(DIAGRAMS / (spec['id'] + '-main.svg')).relative_to(ROOT)}", file=out)
    for line in found:
        print(line, file=sys.stderr)
    return 1 if found else 0


def check(paths: list[Path], measure_text: bool = False) -> int:
    found = [f"icons: {p}" for p in icons.verify()]
    if found:                                                # a figure cannot be drawn from a broken icon set: say so, do not try
        print("\n".join(found), file=sys.stderr)
        return 1
    loaded, bad = _load_each(paths)
    found.extend(bad)
    for path, spec in loaded:
        markup = svg.figure(spec)
        found.extend(figure_problems(spec, markup))
        found.extend(facebook.plan(spec)[1])               # every figure can be exported to the studio's Facebook standard
        stored = DIAGRAMS / f"{spec['id']}-main.svg"
        if not stored.is_file():
            found.append(f"{spec['id']}: {stored.relative_to(ROOT)} is missing; run `python3 -m scripts.figures build`")
        elif stored.read_bytes() != markup.encode("utf-8"):
            found.append(f"{spec['id']}: {stored.relative_to(ROOT)} is not what the spec draws; run `python3 -m scripts.figures build`")
        for suffix, make in EDITORS.values():                 # an editor file kept beside the spec must not go stale
            beside = path.parent / f"{spec['id']}{suffix}"            # beside the spec that was given, wherever it is
            if beside.is_file() and beside.read_bytes() != make(spec).encode("utf-8"):
                found.append(f"{spec['id']}: {_shown(beside)} is not what the spec draws; render it again")
        if measure_text:
            try:
                found.extend(f"{spec['id']}: {p}" for p in browser.measure(spec))
            except browser.Unavailable as exc:
                print(f"cannot measure the text ({exc}); run: python -m playwright install chromium", file=sys.stderr)
                return 2
    for line in found:
        print(line, file=sys.stderr)
    if not found:
        print(f"ok: {len(loaded)} figure spec(s), {len(icons.NAMES)} icons")
    return 1 if found else 0


def render(path: Path, fmt: str, out: Path | None, scale: float | None) -> int:
    loaded, found = _load([path])
    if found:
        print("\n".join(found), file=sys.stderr)
        return 1
    spec = loaded[0]
    if fmt == "svg":
        content = svg.figure(spec)
    else:
        make = EDITORS[fmt][1]
        content = make(spec, scale) if scale is not None else make(spec)
    if out is None:
        sys.stdout.write(content)
    else:
        _write(out, content)
        print(f"wrote {out}")
    return 0


def preview(path: Path, out: Path | None, scale: float) -> int:
    loaded, found = _load([path])
    if found:
        print("\n".join(found), file=sys.stderr)
        return 1
    spec = loaded[0]
    markup = svg.figure(spec)
    height = int(re.search(r'height="(\d+)"', markup).group(1))
    target = out or ROOT / "build" / "figures" / f"{spec['id']}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        browser.png(markup, target, 320, height, scale)
    except browser.Unavailable as exc:                         # Playwright or Chromium missing: say how to get it
        print(f"cannot draw the preview ({exc}); run: python -m playwright install chromium", file=sys.stderr)
        return 2
    print(f"wrote {target}")
    return 0


def to_facebook(path: Path, fmt: str, out: Path | None) -> int:
    loaded, found = _load([path])
    if found:
        print("\n".join(found), file=sys.stderr)
        return 1
    icon_problems = [f"icons: {p}" for p in icons.verify()]
    if icon_problems:
        print("\n".join(icon_problems), file=sys.stderr)
        return 1
    try:
        files, problems = facebook.export(loaded[0], out or ROOT / "build" / "figures" / "facebook", ROOT, fmt)
    except browser.Unavailable as exc:                         # Playwright or Chromium missing: say how to get it
        print(f"cannot draw the slides ({exc}); run: python -m playwright install chromium", file=sys.stderr)
        return 2
    for line in problems:
        print(line, file=sys.stderr)
    for file in files:
        print(f"wrote {file}")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m scripts.figures", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build").add_argument("specs", nargs="*")
    p = sub.add_parser("check")
    p.add_argument("specs", nargs="*")
    p.add_argument("--browser", action="store_true", help="also measure every line of text in Chromium")
    p = sub.add_parser("render")
    p.add_argument("spec")
    p.add_argument("--format", choices=["svg", *EDITORS], default="svg")
    p.add_argument("--out", type=Path)
    p.add_argument("--scale", type=scale_argument, help="editor files only: times the 320 px figure (default 2)")
    p = sub.add_parser("preview")
    p.add_argument("spec")
    p.add_argument("--out", type=Path)
    p.add_argument("--scale", type=scale_argument, default=2.0)
    p = sub.add_parser("facebook")
    p.add_argument("spec")
    p.add_argument("--format", choices=list(facebook.FORMATS), default=facebook.DEFAULT)
    p.add_argument("--out", type=Path)
    p = sub.add_parser("icons")
    p.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    try:
        return dispatch(args)
    except OSError as exc:                                     # an unwritable --out, a vanished file: a sentence, not a traceback
        print(f"cannot read or write a file: {exc}", file=sys.stderr)
        return 2


def dispatch(args: argparse.Namespace) -> int:
    if args.command == "build":
        return build(_spec_paths(args.specs), sys.stdout)
    if args.command == "check":
        return check(_spec_paths(args.specs), args.browser)
    if args.command == "render":
        return render(Path(args.spec), args.format, args.out, args.scale)
    if args.command == "preview":
        return preview(Path(args.spec), args.out, args.scale)
    if args.command == "facebook":
        return to_facebook(Path(args.spec), args.format, args.out)
    if args.verify:
        problems = icons.verify()
        print("\n".join(problems) if problems else f"ok: {len(icons.NAMES)} icons match index.json")
        return 1 if problems else 0
    print(icons.listing())
    return 0
