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
import json
import math
import re
import sys
import tempfile
from pathlib import Path

from . import browser, drawio, excalidraw, facebook, icons, mobile, moda, scene as scenes, spec as specs, svg
from .files import write_atomic

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "system-design-101"
SPEC_DIR = STORE / "figures" / "vi"
DIAGRAMS = STORE / "vi" / "diagrams"
LESSONS = STORE / "vi" / "lessons"
MIN_SCALE, MAX_SCALE = 0.25, 8.0
STEPS_PER_UNIT = 20                   # a scale is a multiple of 1/20: its page width (320 x scale) and panel width (288 x scale) are then exact to 0.1 px, which is how an editor file keeps them
EDITORS = {"drawio": (".drawio", drawio.diagram), "excalidraw": (".excalidraw", excalidraw.board), "moda": ("-moda.xml", moda.markup)}
LESSON_ID = re.compile(r"sd-\d{2}-\d{3}")


def _write(path: Path, content: str) -> bool:
    """Writes `content` (LF line ends) unless the file already has exactly it; True when it wrote. A failed write leaves the previous file whole."""
    data = content.encode("utf-8")
    if path.is_file() and path.read_bytes() == data:
        return False
    write_atomic(path, data)
    return True


def language_problem(spec: dict) -> str | None:
    """The store is Vietnamese (`system-design-101/vi`): a spec in another language is drawn with `render`, outside it."""
    lang = spec.get("lang", "vi")
    if lang != "vi":
        return f"{spec['id']}: lang is {lang!r}, and the store holds Vietnamese lessons; draw other languages with `render`, outside the store"
    return None


def aliases(spec_path: Path, out: Path | None) -> bool:
    """True when `out` is the spec file itself, under another name, through a link or as a hard link: the output would overwrite the source
    everything is rebuilt from. An `out` that does not exist yet cannot be it."""
    try:
        return out is not None and out.exists() and spec_path.samefile(out)
    except OSError:
        return False


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


def duplicate_ids(loaded: list[tuple[Path, dict]]) -> list[str]:
    """One problem per figure id that two spec files claim: both would write the same `<id>-main.svg`."""
    seen: dict[str, Path] = {}
    found = []
    for path, spec in loaded:
        if spec["id"] in seen:
            found.append(f"{spec['id']}: the id is used by two specs, {_shown(seen[spec['id']])} and {_shown(path)}; each figure has one spec")
        else:
            seen[spec["id"]] = path
    return found


def _shown(path: Path) -> Path:
    """The path as a sentence shows it: relative to the repository when it is inside it."""
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def scale_argument(text: str) -> float:
    """A finite scale from MIN_SCALE to MAX_SCALE in steps of 0.05: anything else would draw garbage, text too small to see or a huge file,
    or a size that `check` could not read back from the editor file it wrote (a scale that is not a multiple of 0.05 loses digits in it)."""
    try:
        value = float(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{text!r} is not a number") from exc
    if not math.isfinite(value) or not MIN_SCALE <= value <= MAX_SCALE:
        raise argparse.ArgumentTypeError(f"must be from {MIN_SCALE:g} to {MAX_SCALE:g}")
    steps = round(value * STEPS_PER_UNIT)
    if abs(value * STEPS_PER_UNIT - steps) > 1e-9:
        raise argparse.ArgumentTypeError("must be a multiple of 0.05")
    return steps / STEPS_PER_UNIT


def broken_icons() -> bool:
    """Prints the problems of the icon set and says whether there are any: nothing is drawn from a broken or tampered set."""
    problems = icons.verify()
    for problem in problems:
        print(f"icons: {problem}", file=sys.stderr)
    return bool(problems)


def browser_unavailable(doing: str, exc: browser.Unavailable) -> int:
    """Says why Chromium could not be used and returns the exit status 2. Only a browser that is missing is told how to install it."""
    hint = "" if isinstance(exc, browser.Failed) else "; run: python -m playwright install chromium"
    print(f"cannot {doing} ({exc}){hint}", file=sys.stderr)
    return 2


def stored_scale(suffix: str, text: str) -> float | None:
    """The scale an editor file was drawn at, read from the file itself (draw.io: the page width, Moda: the canvas width, Excalidraw: the width
    of the first panel), or None when it cannot be read: a file kept at the scale `render --scale` gave it is still current."""
    try:
        if suffix == ".drawio":
            width = float(re.search(r'pageWidth="([\d.]+)"', text).group(1))
        elif suffix == "-moda.xml":
            width = float(re.search(r"Moda canvas ([\d.]+)x", text).group(1))
        else:
            panel = next(e for e in json.loads(text)["elements"] if e["type"] == "rectangle")
            width = panel["width"] / (scenes.W - 2 * scenes.MARGIN) * scenes.W
    except (AttributeError, ValueError, KeyError, StopIteration, TypeError, RecursionError, OverflowError):       # nested too deep, a number too large: not readable, so not current
        return None
    scale = round(width / scenes.W, 4)
    return scale if MIN_SCALE <= scale <= MAX_SCALE else None


def build(paths: list[Path], out) -> int:
    if broken_icons():                                       # a tampered icon file is never drawn into a stored figure
        return 1
    loaded, found = _load_each(paths)
    clashes = duplicate_ids(loaded)
    if clashes:                                               # two specs for one figure: nothing is written, whichever came last would win
        print("\n".join(found + clashes), file=sys.stderr)
        return 1
    for path, spec in loaded:
        if not LESSON_ID.fullmatch(spec["id"]) or not (LESSONS / spec["id"]).is_dir():
            found.append(f"{spec['id']}: there is no lesson of that id in {LESSONS.relative_to(ROOT)}; use `render` for a trial figure")
            continue
        wrong = language_problem(spec)
        if wrong:                                                       # an English figure must not replace a Vietnamese lesson's
            found.append(wrong)
            continue
        if aliases(path, DIAGRAMS / f"{spec['id']}-main.svg"):          # the figure would be written over its own spec
            found.append(f"{spec['id']}: {_shown(path)} is the figure's own output file; keep the spec in {SPEC_DIR.relative_to(ROOT)}")
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
    if broken_icons():                                       # a figure cannot be drawn from a broken icon set: say so, do not try
        return 1
    found: list[str] = []
    loaded, bad = _load_each(paths)
    found.extend(bad)
    found.extend(duplicate_ids(loaded))
    for path, spec in loaded:                                 # a spec kept in the store's folder is a store figure
        if path.resolve().parent == SPEC_DIR.resolve() and language_problem(spec):
            found.append(language_problem(spec))
    if loaded:                                                # the footer of every slide: the export would refuse it, so a figure is not Facebook-ready
        reason = facebook.handle_problem(facebook.handle(ROOT))
        if reason:
            found.append(reason)
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
            if beside.is_file():
                text = beside.read_bytes().decode("utf-8", "replace")
                scale = stored_scale(suffix, text)             # drawn at its own scale: compared at that one
                if beside.read_bytes() != (make(spec, scale) if scale else make(spec)).encode("utf-8"):
                    found.append(f"{spec['id']}: {_shown(beside)} is not what the spec draws; render it again")
        if measure_text:
            try:
                found.extend(f"{spec['id']}: {p}" for p in browser.measure(spec))
            except browser.Unavailable as exc:
                return browser_unavailable("measure the text", exc)
    for line in found:
        print(line, file=sys.stderr)
    if not found:
        print(f"ok: {len(loaded)} figure spec(s), {len(icons.NAMES)} icons")
    return 1 if found else 0


def render(path: Path, fmt: str, out: Path | None, scale: float | None) -> int:
    if broken_icons():
        return 1
    loaded, found = _load([path])
    if found:
        print("\n".join(found), file=sys.stderr)
        return 1
    if aliases(path, out):
        print(f"--out {out} is the spec itself; give another file", file=sys.stderr)
        return 2
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
    if broken_icons():
        return 1
    loaded, found = _load([path])
    if found:
        print("\n".join(found), file=sys.stderr)
        return 1
    if aliases(path, out):
        print(f"--out {out} is the spec itself; give another file", file=sys.stderr)
        return 2
    spec = loaded[0]
    markup = svg.figure(spec)
    height = int(re.search(r'height="(\d+)"', markup).group(1))
    target = out or ROOT / "build" / "figures" / f"{spec['id']}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        browser.png(markup, target, 320, height, scale)
    except browser.Unavailable as exc:                         # Playwright or Chromium missing, or failed while drawing
        return browser_unavailable("draw the preview", exc)
    print(f"wrote {target}")
    return 0


def to_facebook(path: Path, fmt: str, out: Path | None) -> int:
    loaded, found = _load([path])
    if found:
        print("\n".join(found), file=sys.stderr)
        return 1
    if broken_icons():
        return 1
    try:
        files, problems = facebook.export(loaded[0], out or ROOT / "build" / "figures" / "facebook", ROOT, fmt)
    except browser.Unavailable as exc:                         # Playwright or Chromium missing, or failed while drawing
        return browser_unavailable("draw the slides", exc)
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
    if args.command == "render" and args.format == "svg" and args.scale is not None:
        parser.error("--scale applies to the editor formats (drawio, excalidraw, moda); an svg is always drawn at 320 px")
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
