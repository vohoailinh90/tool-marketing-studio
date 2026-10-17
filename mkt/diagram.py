"""The `diagram` slide layout: Mermaid source, drawn into an SVG inside the slide's own page.

A post gives Mermaid text (a flowchart, a sequence diagram or a state machine); the image shows
it in the campaign's colours and fonts. The layout itself only prints the escaped source — the page
on disk stays script-free under the same CSP as every other slide. The renderer then loads the
vendored Mermaid bundle into the open page through the browser's debugger channel (which the page's
CSP does not govern), draws each diagram with `securityLevel: strict`, and measures how large the
text ended up, so a diagram too crowded to read on a phone is a warning, not a surprise.

What `source_problems` refuses is what Mermaid could do beyond drawing: links and click handlers,
HTML, init directives and front matter (they would change the theme or the security level), CSS
(`style`, `classDef`) and any diagram type that was not tried against the theme. A highlight is a
named tone instead: `A:::hl`, `class A,B bad`. That list is the early, friendly answer in `studio.py check`;
the barrier is the second check, on the SVG Mermaid drew: a link, image or script there fails the diagram.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

BUNDLE = Path(__file__).with_name("vendor") / "mermaid" / "mermaid.min.js"
# mermaid@11.17.2, dist/mermaid.min.js (mkt/vendor/mermaid/README.md). A bundle that differs is never run.
MERMAID_SHA256 = "581ed7d74bd9048d0e3a91363927d72ef22942d7722546b27f7cc29e35390eb8"

TYPES = ("flowchart", "graph", "sequenceDiagram", "stateDiagram-v2")
TONES = ("hl", "ok", "bad", "warn", "muted")
MAX_CHARS = 2400
MAX_LINES = 40
FONT_PX = 26            # Mermaid's text size before the diagram is scaled to the slide
MIN_TEXT_PX = 22        # below this, on a 1080 px wide image, the text is too small for a phone
MAX_UPSCALE = 1.4       # a small diagram grows at most this much, so three boxes do not become posters

# A statement that starts with one of these is refused, in any letter case (Mermaid reads `LINK` and `Click` too) and also when
# the command stands alone on its line and its arguments follow on the next. Everything else a diagram can say is drawing.
# `;` also separates statements (`A --> B; style A fill:#f00` restyles A), so lines are split at it by `split_statements`.
# This is the early, friendly answer; the check in `RENDER_JS` on the drawn SVG is the barrier against a link, image or script.
FORBIDDEN_STATEMENT = re.compile(r"^\s*(?:click|href|call|callback|links?|classDef|style|linkStyle)(?:\s|$)|^\s*acc(?:Title|Descr)\b",
                                 re.IGNORECASE)
CLASS_STATEMENT = re.compile(r"^\s*class\s+\S+\s+(\w+)\s*$")
TONE_SUFFIX = re.compile(r":::\s*(\w+)")
# `<` opens HTML when a letter, `/` or `!` follows; arrows (`<-->`, `<<->>`, `<|`) never do. `<br>` is a line break.
HTML_TAG = re.compile(r"<\s*[/!A-Za-z]")
LINE_BREAK = re.compile(r"<\s*br\s*/?\s*>", re.IGNORECASE)
STATE_MARKER = re.compile(r"<<\s*(?:choice|fork|join)\s*>>", re.IGNORECASE)      # `state c <<choice>>` in a state diagram
FORBIDDEN_TEXT = re.compile(r"javascript:|vbscript:|data:[a-z]+/|&#|%%\{|@\s*\{", re.IGNORECASE)


class DiagramError(ValueError):
    pass


ENTITY_TAIL = re.compile(r"[#&][A-Za-z0-9]+$")          # `#59` or `&amp` right before a `;`: an entity code, not a separator


def split_statements(line: str) -> list[str]:
    """Where `;` really ends a statement: not inside a double-quoted string, not inside a bracketed label
    (`A[pick a style; click Next]`), and not as the end of an entity code (`#59;`, `&amp;`)."""
    parts, current, quoted, depth = [], "", False, 0
    for char in line:
        if char == '"':
            quoted = not quoted
        elif not quoted and char in "[({":
            depth += 1
        elif not quoted and char in "])}":
            depth = max(depth - 1, 0)
        if char == ";" and not quoted and depth == 0 and not ENTITY_TAIL.search(current):
            parts.append(current)
            current = ""
        else:
            current += char
    parts.append(current)
    return parts


def source_problems(source) -> list[str]:
    """Why this Mermaid source may not go on an image; empty when it may."""
    if not isinstance(source, str):
        return ["a diagram's source must be text"]
    text = unicodedata.normalize("NFKC", source)
    lines = text.splitlines()
    problems = []
    if len(text) > MAX_CHARS or len(lines) > MAX_LINES:
        problems.append(f"diagram too long ({len(lines)} lines, {len(text)} characters; "
                        f"at most {MAX_LINES} and {MAX_CHARS}): split it over two slides")
    statements = [line for line in lines if line.strip() and not line.strip().startswith("%%")]
    if not statements:
        return problems + [f"diagram has no content; start with one of: {', '.join(TYPES)}"]
    first = statements[0].split()
    if first[0] not in TYPES:
        problems.append(f"diagram must start with one of: {', '.join(TYPES)} (got '{first[0]}')")
    if FORBIDDEN_TEXT.search(text):
        problems.append("diagram contains a directive, script, URL scheme or @{ } node attribute (it can load an image) that is not allowed")
    if HTML_TAG.search(STATE_MARKER.sub(" ", LINE_BREAK.sub(" ", text))):
        problems.append("diagram labels cannot contain HTML (only <br/> for a line break)")
    parts = [part for line in statements for part in split_statements(line)]
    for statement in parts:
        if FORBIDDEN_STATEMENT.match(statement):
            problems.append(f"'{statement.split()[0]}' is not allowed in a diagram "
                            "(no links, clicks or CSS; highlight with :::hl, :::ok, :::bad, :::warn or :::muted)")
            break
    tones = [m.group(1) for m in TONE_SUFFIX.finditer(text)]
    tones += [m.group(1) for m in map(CLASS_STATEMENT.match, parts) if m]
    unknown = sorted({tone for tone in tones if tone not in TONES})
    if unknown:
        problems.append(f"unknown tone {', '.join(unknown)}: use {', '.join(TONES)}")
    return problems


def bundle() -> str:
    """The vendored Mermaid, only if it is byte for byte the pinned one."""
    data = BUNDLE.read_bytes()
    if hashlib.sha256(data).hexdigest() != MERMAID_SHA256:
        raise DiagramError(f"{BUNDLE.name} is not the pinned Mermaid build (see mkt/vendor/mermaid/README.md)")
    return data.decode("utf-8")


# Runs in the slide page, after the bundle. Colours come from the page's own CSS variables, so a
# campaign's accent is the diagram's accent; it returns one entry per diagram.
RENDER_JS = """
async (opt) => {
  const slide = document.querySelector('.slide');
  // Any CSS colour (color-mix and color(srgb …) included) as #rrggbb, read back from one painted pixel.
  const norm = (value) => {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 1;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    ctx.fillStyle = value; ctx.fillRect(0, 0, 1, 1);
    const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data;
    return '#' + [r, g, b].map((v) => v.toString(16).padStart(2, '0')).join('');
  };
  const colour = (name) => {
    const probe = document.createElement('i');
    probe.style.color = 'var(' + name + ')'; slide.appendChild(probe);
    const value = getComputedStyle(probe).color; probe.remove(); return norm(value);
  };
  const c = {};
  for (const name of ['accent', 'accent-soft', 'accent-strong', 'ink', 'muted', 'line', 'paper', 'card',
                      'ok', 'ok-soft', 'bad', 'bad-soft', 'warn', 'warn-soft']) c[name] = colour('--' + name);
  // WCAG relative luminance: white text on a dark accent, ink on a light one.
  const luminance = (hex) => {
    const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
      .map((v) => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)));
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  // tone: [fill, border, text]; hl is the one solid colour, for the step the slide is about.
  const tones = {
    hl: [c.accent, c['accent-strong'], luminance(c.accent) < 0.18 ? '#ffffff' : c.ink],
    ok: [c['ok-soft'], c.ok, c.ink], bad: [c['bad-soft'], c.bad, c.ink],
    warn: [c['warn-soft'], c.warn, c.ink], muted: ['#f1f5f9', '#94a3b8', c.muted],
  };
  const family = getComputedStyle(slide).fontFamily;
  const figures = [...document.querySelectorAll('.diagram')];
  const sample = figures.map((f) => f.querySelector('.diagram__src').textContent).join('');
  await Promise.all(['"Be Vietnam Pro"', '"Noto Sans JP"'].map((f) => document.fonts.load('600 ' + opt.fontPx + 'px ' + f, sample)));
  await document.fonts.ready;
  const px = opt.fontPx + 'px';
  mermaid.initialize({
    startOnLoad: false, securityLevel: 'strict', theme: 'base', logLevel: 'fatal', suppressErrorRendering: true,
    fontFamily: family, fontSize: opt.fontPx,
    themeVariables: {
      fontFamily: family, fontSize: px, background: c.paper, textColor: c.ink,
      primaryColor: c['accent-soft'], primaryBorderColor: c.accent, primaryTextColor: c.ink,
      secondaryColor: c.card, secondaryBorderColor: c.line, secondaryTextColor: c.ink,
      tertiaryColor: c.card, tertiaryBorderColor: c.line, tertiaryTextColor: c.ink,
      lineColor: c.muted, edgeLabelBackground: c.paper, clusterBkg: c.card, clusterBorder: c.line,
      actorBkg: c['accent-soft'], actorBorder: c.accent, actorTextColor: c.ink, actorLineColor: c.line,
      signalColor: c.muted, signalTextColor: c.ink, labelBoxBkgColor: c['accent-soft'], labelBoxBorderColor: c.accent,
      labelTextColor: c.ink, loopTextColor: c.ink, noteBkgColor: c['warn-soft'], noteBorderColor: c.warn, noteTextColor: c.ink,
      activationBkgColor: c['accent-soft'], activationBorderColor: c.accent, sequenceNumberColor: '#ffffff',
    },
    themeCSS: '.node rect,.node polygon,.node circle,.node ellipse,.node path{stroke-width:3px}'
      + '.flowchart-link,.edgePath .path,.transition,.relationshipLine{stroke-width:3px}'
      + '.cluster rect{rx:18;ry:18;stroke-width:2.5px}.actor{stroke-width:3px}'
      + '.messageLine0,.messageLine1{stroke-width:3px}'
      + '.nodeLabel,.edgeLabel,.label,text,.messageText,.actor-man text{font-weight:600}',
    flowchart: { useMaxWidth: false, htmlLabels: true, wrappingWidth: 300, nodeSpacing: 44, rankSpacing: 56, padding: 18, curve: 'basis' },
    sequence: { useMaxWidth: false, wrap: true, width: 200, actorMargin: 48, messageMargin: 44, boxMargin: 12,
                actorFontSize: opt.fontPx, noteFontSize: opt.fontPx, messageFontSize: opt.fontPx,
                actorFontWeight: 600, noteFontWeight: 600, messageFontWeight: 600 },
    state: { useMaxWidth: false },
  });
  const classDefs = Object.entries(tones).map(([name, [fill, stroke, text]]) =>
    'classDef ' + name + ' fill:' + fill + ',stroke:' + stroke + ',stroke-width:4px,color:' + text).join('\\n');
  const results = [];
  let count = 0;
  for (const figure of figures) {
    const pre = figure.querySelector('.diagram__src');
    const lines = pre.textContent.split('\\n');
    let head = lines.findIndex((line) => line.trim() && !line.trim().startsWith('%%'));
    if (!/^(flowchart|graph|stateDiagram)/.test((lines[head] || '').trim())) head = -1;
    const source = head < 0 ? pre.textContent
      : lines.slice(0, head + 1).concat([classDefs], lines.slice(head + 1)).join('\\n');
    try {
      const { svg } = await mermaid.render('diagram-' + count++, source);
      const art = document.createElement('div');
      art.className = 'diagram__art';
      art.innerHTML = svg;
      // Strict mode still turns `click … href` into a link and `A@{ img: … }` into a picture of any file the
      // page may read; a diagram carries neither, nor a script.
      if (art.querySelector('a, script, iframe, object, embed, image, img')) throw new Error('links, images and scripts are not allowed in a diagram');
      const drawing = art.querySelector('svg');
      const box = drawing.viewBox.baseVal;
      drawing.removeAttribute('width'); drawing.removeAttribute('height');
      drawing.style.maxWidth = Math.round(box.width * opt.maxUpscale) + 'px';
      pre.replaceWith(art);
      results.push({ ok: true });
    } catch (error) {
      results.push({ ok: false, error: String((error && error.message) || error).split('\\n').slice(0, 4).join(' | ').slice(0, 300) });
    }
  }
  // How large the text really is once the SVG is scaled into its box: called again after fit().
  window.diagramText = () => [...document.querySelectorAll('.diagram__art svg')].map((drawing) => {
    const box = drawing.viewBox.baseVal, rect = drawing.getBoundingClientRect();
    return opt.fontPx * Math.min(rect.width / box.width, rect.height / box.height);
  });
  return results;
}
"""


def render_in_page(page) -> None:
    """Draw every `diagram` figure of the slide page `page` has open. Raises DiagramError when one cannot be drawn."""
    session = page.context.new_cdp_session(page)
    try:
        loaded = session.send("Runtime.evaluate", {"expression": bundle(), "silent": True})
    finally:
        session.detach()
    if loaded.get("exceptionDetails"):
        raise DiagramError("the Mermaid library did not load")
    results = page.evaluate(RENDER_JS, {"fontPx": FONT_PX, "maxUpscale": MAX_UPSCALE})
    failed = [item["error"] for item in results if not item.get("ok")]
    if failed:
        raise DiagramError(f"Mermaid cannot draw this diagram: {failed[0]}")


def text_warnings(page) -> list[str]:
    """Advice for diagrams whose text ended up too small to read; call after the slide has been fitted."""
    sizes = page.evaluate("window.diagramText ? window.diagramText() : []")
    smallest = min(sizes, default=None)
    if smallest is not None and smallest < MIN_TEXT_PX:
        return [f"diagram text is only about {smallest:.0f} px on a 1080 px image (want {MIN_TEXT_PX}+): "
                "use fewer boxes, shorter labels, flowchart TD instead of LR, or split it over two slides"]
    return []
