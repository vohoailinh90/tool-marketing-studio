"""A spec laid out once, as a neutral scene: positioned rectangles, text, icons, arrows and lines.

`svg.py`, `drawio.py`, `excalidraw.py` and `moda.py` only translate this scene into their own file format, so the four pictures show
the same content in the same places. The scene is one 320 px column (the width the System Design lessons are drawn for, see
`mobile.py`); `scaled()` makes a larger copy for an editor. Nothing here calls a model or the network, and every word on the scene is a
field of the spec: no label, caption or arrow text is invented.

Items are drawn in order. `rect` has a `role` (panel, card0..card3, note) that a writer maps to colours, `text` has the `lines` the
words were broken into and the index of the rectangle that holds it (`inside`), `arrow` and `line` have `pts` (an arrow ends with a
head; `src`/`dst` name the rectangles it joins), `icon`, `badge` and `tick` are round pictograms.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .spec import forward
from .text import one_line, wrap

W = 320                              # width of every scene
MARGIN, PAD = 8, 12                  # page edge to panel; panel or card edge to its content
CONTENT_X, CONTENT_W = MARGIN + PAD, W - 2 * (MARGIN + PAD)
RAIL = 12                            # distance between two lanes of cross links beside the cards


@dataclass(frozen=True)
class Style:
    """Font sizes of one writer (px). The scene reserves room for the text at these sizes."""
    title: float = 20
    subtitle: float = 15
    head: float = 17
    name: float = 16
    role: float = 15
    step_title: float = 16
    step_text: float = 15
    note: float = 15
    actor: float = 15
    msg: float = 15
    body_lh: float = 1.3
    title_lh: float = 1.2
    wscale: float = 1.0              # how much wider than text.width() (DejaVu Sans) this writer's font runs
    icons: bool = True               # draw the pictograms a spec names (a writer that cannot draw them sets False)
    icon: int = 36                   # width of a card's pictogram


def assign_rails(links: list[tuple[int, int]]) -> dict[tuple[int, int], int]:
    """Lane number (0 = nearest the cards) of each link that cannot run straight down to the next card. Two links whose card
    ranges overlap never share a lane, and of two nested links the longer one is the outer, so a short hop is not crossed by the
    long one that encloses it. Links that do not overlap share a lane."""
    spans = {link: (min(link), max(link)) for link in links}
    lanes: dict[tuple[int, int], int] = {}
    for link in sorted(spans, key=lambda x: (spans[x][1] - spans[x][0], x)):
        lo, hi = spans[link]
        used = [lanes[o] for o in lanes if not (spans[o][1] < lo or hi < spans[o][0])]
        lanes[link] = max(used, default=-1) + 1
    return lanes


def slot_order(card: int, ends: list[tuple[int, int, str]]) -> list[tuple[int, int, str]]:
    """The ends (other card, link number, 'out' or 'in') of rail links on one card, top to bottom: the links that go up first, the
    nearest on top, then the links that go down, the farthest first. That puts the longer of two nested links on the side away
    from its direction of travel, so the shorter one is not crossed where they meet the same card."""
    up = sorted((e for e in ends if e[0] < card), key=lambda e: (card - e[0], e[1], e[2]))
    down = sorted((e for e in ends if e[0] > card), key=lambda e: (e[0] - card, e[1], e[2]), reverse=True)
    return up + down


def build(spec: dict, st: Style) -> dict:
    """The scene: {"w", "h", "title", "desc", "items"}."""
    items: list[dict] = []

    def add(**kw) -> int:
        items.append(kw)
        return len(items) - 1

    def shape(s, px: float, w: float, weight: int = 400) -> list[str]:
        """The lines `s` is broken into at `px` and `weight` inside `w`."""
        return wrap(one_line(s), px, w, st.wscale, weight >= 700)

    def text(x, y, w, s, px, *, weight=400, color="ink", align="left", lh=None, inside=None) -> int:
        """Adds wrapped text and returns its height."""
        lh = lh or st.body_lh
        lines = shape(s, px, w, weight)
        h = math.ceil(len(lines) * px * lh)
        add(k="text", x=x, y=y, w=w, h=h, text=one_line(s), lines=lines, px=px, weight=weight, color=color, align=align, lh=lh, inside=inside)
        return h

    def lines_h(lines: list[str], px: float, lh: float) -> int:
        return math.ceil(len(lines) * px * lh)

    y = 16
    y += text(16, y, W - 32, spec["title"], st.title, weight=800, color="title", lh=st.title_lh) + 6
    if spec.get("subtitle"):
        y += text(16, y, W - 32, spec["subtitle"], st.subtitle, color="muted") + 6
    y += 8

    def panel(heading: str | None) -> tuple[int, float]:
        idx = add(k="rect", role="panel", x=MARGIN, y=y, w=W - 2 * MARGIN, h=0, r=14)
        top = y + PAD
        if heading:
            top += text(CONTENT_X, top, CONTENT_W, heading, st.head, weight=700, color="head") + 10
        return idx, top

    def close(idx: int, bottom: float) -> float:
        items[idx]["h"] = math.ceil(bottom + PAD - items[idx]["y"])
        return items[idx]["y"] + items[idx]["h"] + 12

    # --- parts: cards in a column, a straight arrow to the next card, a lane beside the cards for every other link ----------
    def parts(sec: dict, n: int) -> None:
        nonlocal y
        role = f"card{n % 4}"
        cards = sec["items"]
        links = [tuple(p) for p in dict.fromkeys(tuple(p) for p in sec.get("flow", []))]
        down = {a for a, b in links if forward(a, b)}
        lanes = assign_rails([lk for lk in links if not forward(*lk)])
        lane_count = max(lanes.values(), default=-1) + 1
        cw = CONTENT_W - (0 if not lane_count else 14 + RAIL * (lane_count - 1))
        pic = st.icon if st.icons and all(c.get("icon") for c in cards) else 0
        off = pic + 10 if pic else 0
        tw = cw - 2 * PAD - off
        shaped = []
        for c in cards:
            name, desc = shape(c["name"], st.name, tw, 700), shape(c["role"], st.role, tw)
            shaped.append((name, desc, max(PAD + lines_h(name, st.name, 1.25) + 4 + lines_h(desc, st.role, st.body_lh) + PAD, 2 * PAD + pic)))
        panel_idx, top = panel(sec.get("heading"))
        ys, boxes, cur = [], [], top
        for i, (_, _, h) in enumerate(shaped):
            ys.append(cur)
            cur += h + (32 if i in down else 14)
        for i, c in enumerate(cards):
            name, desc, h = shaped[i]
            boxes.append(add(k="rect", role=role, x=CONTENT_X, y=ys[i], w=cw, h=h, r=10, comp=i))
            if pic:
                add(k="icon", name=c["icon"], x=CONTENT_X + PAD, y=ys[i] + (h - pic) / 2, d=pic, role=role)
            ty = ys[i] + PAD
            ty += text(CONTENT_X + PAD + off, ty, tw, c["name"], st.name, weight=700, lh=1.25, inside=boxes[i]) + 4
            text(CONTENT_X + PAD + off, ty, tw, c["role"], st.role, inside=boxes[i])
        cx = CONTENT_X + cw / 2
        for a in sorted(down):
            add(k="arrow", pts=[(cx, ys[a] + shaped[a][2] + 2), (cx, ys[a + 1] - 2)], src=boxes[a], dst=boxes[a + 1], dashed=False, link=(a, a + 1))
        rail_links = list(lanes)
        ends: dict[int, list[tuple[int, int, str]]] = {}
        for number, (a, b) in enumerate(rail_links):
            ends.setdefault(a, []).append((b, number, "out"))
            ends.setdefault(b, []).append((a, number, "in"))
        slot: dict[tuple[int, str], float] = {}
        for card, group in ends.items():
            for rank, (_, number, end) in enumerate(slot_order(card, group)):
                slot[(number, end)] = ys[card] + shaped[card][2] * (rank + 1) / (len(group) + 1)
        edge = CONTENT_X + cw
        for number, (a, b) in enumerate(rail_links):
            lane_x = edge + 10 + RAIL * lanes[(a, b)]
            ya, yb = slot[(number, "out")], slot[(number, "in")]
            add(k="arrow", pts=[(edge, ya), (lane_x, ya), (lane_x, yb), (edge + 2, yb)], src=boxes[a], dst=boxes[b], dashed=False, link=(a, b))
        y = close(panel_idx, ys[-1] + shaped[-1][2])

    # --- steps: numbered cards, a short arrow from one number to the next ------------------------------------------------
    def steps(sec: dict, n: int) -> None:
        nonlocal y
        role, d = f"card{n % 4}", 28
        off = PAD + d + 10
        tw = CONTENT_W - off - PAD
        panel_idx, cur = panel(sec.get("heading"))
        previous = None
        for i, s in enumerate(sec["items"]):
            head, body = shape(s["title"], st.step_title, tw, 700), shape(s["text"], st.step_text, tw)
            h = max(PAD + lines_h(head, st.step_title, 1.25) + 4 + lines_h(body, st.step_text, st.body_lh) + PAD, 2 * PAD + d)
            card = add(k="rect", role=role, x=CONTENT_X, y=cur, w=CONTENT_W, h=h, r=10, step=i)
            add(k="badge", x=CONTENT_X + PAD, y=cur + PAD, d=d, label=str(i + 1), role=role)
            ty = cur + PAD
            ty += text(CONTENT_X + off, ty, tw, s["title"], st.step_title, weight=700, lh=1.25, inside=card) + 4
            text(CONTENT_X + off, ty, tw, s["text"], st.step_text, inside=card)
            if previous is not None:
                bx = CONTENT_X + PAD + d / 2
                add(k="arrow", pts=[(bx, previous[1] + 2), (bx, cur - 2)], src=previous[0], dst=card, dashed=False, step=i - 1)
            previous = (card, cur + h)
            cur += h + 22
        y = close(panel_idx, previous[1])

    # --- notes: cards with a tick -----------------------------------------------------------------------------------------
    def notes(sec: dict, n: int) -> None:
        nonlocal y
        d = 22
        off = PAD + d + 10
        tw = CONTENT_W - off - PAD
        panel_idx, cur = panel(sec.get("heading"))
        bottom = cur
        for s in sec["items"]:
            body = shape(s, st.note, tw)
            h = max(PAD + lines_h(body, st.note, st.body_lh) + PAD, 2 * PAD + d)
            card = add(k="rect", role="note", x=CONTENT_X, y=cur, w=CONTENT_W, h=h, r=10)
            add(k="tick", x=CONTENT_X + PAD, y=cur + PAD, d=d)
            text(CONTENT_X + off, cur + PAD, tw, s, st.note, inside=card)
            bottom = cur + h
            cur = bottom + 8
        y = close(panel_idx, bottom)

    # --- sequence: actors on top, a dashed lifeline under each, one arrow per message -----------------------------------------
    def sequence(sec: dict, n: int) -> None:
        nonlocal y
        role = f"card{n % 4}"
        actors, count = sec["actors"], len(sec["actors"])
        bw = 84 if count == 3 else 96
        centres = [CONTENT_X + bw / 2 + k * (CONTENT_W - bw) / (count - 1) for k in range(count)]
        pic = 28 if st.icons and all(a.get("icon") for a in actors) else 0
        names = [shape(a["name"], st.actor, bw - 12, 700) for a in actors]
        bh = 8 + (pic + 4 if pic else 0) + max(lines_h(nm, st.actor, 1.25) for nm in names) + 8
        panel_idx, top = panel(sec.get("heading"))
        for k, a in enumerate(actors):
            box = add(k="rect", role=role, x=centres[k] - bw / 2, y=top, w=bw, h=bh, r=10, seq=k)
            if pic:
                add(k="icon", name=a["icon"], x=centres[k] - pic / 2, y=top + 8, d=pic, role=role)
            text(centres[k] - bw / 2 + 6, top + 8 + (pic + 4 if pic else 0), bw - 12, a["name"], st.actor, weight=700, align="center", lh=1.25, inside=box)
        lifelines = [add(k="line", pts=[(c, top + bh), (c, top + bh)], dashed=True) for c in centres]
        cur = top + bh + 14
        for m in sec["messages"]:
            xa, xb = centres[m["from"]], centres[m["to"]]
            lo, hi = min(xa, xb), max(xa, xb)
            h = text(lo + 6, cur, hi - lo - 12, m["text"], st.msg, align="center")
            ay = cur + h + 8
            sign = 1 if xb > xa else -1
            add(k="arrow", pts=[(xa + sign * 1, ay), (xb - sign * 3, ay)], src=None, dst=None, dashed=bool(m.get("reply")), seq=True)
            cur = ay + 14
        for line, c in zip(lifelines, centres):
            items[line]["pts"] = [(c, top + bh), (c, cur - 6)]
        y = close(panel_idx, cur - 6)

    for n, sec in enumerate(spec["sections"]):
        {"parts": parts, "steps": steps, "notes": notes, "sequence": sequence}[sec["kind"]](sec, n)
    return {"w": W, "h": math.ceil(y - 12 + MARGIN), "title": one_line(spec["title"]), "desc": one_line(spec["desc"]), "items": items}


def scaled(scene: dict, k: float) -> dict:
    """The scene `k` times as large: every length, font size and point. The words and the line breaks stay."""
    if k == 1:
        return scene
    items = []
    for item in scene["items"]:
        new = dict(item)
        for key in ("x", "y", "w", "h", "d", "r", "px"):
            if key in new:
                new[key] = new[key] * k
        if "pts" in new:
            new["pts"] = [(x * k, y * k) for x, y in new["pts"]]
        items.append(new)
    return {**scene, "w": scene["w"] * k, "h": scene["h"] * k, "items": items}
