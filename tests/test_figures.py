"""scripts/figures: the figure spec, the closed icon set, the layout, and the four writers (SVG for the lessons, draw.io, Excalidraw, Moda)."""

from __future__ import annotations

import base64
import contextlib
import copy
import io
import json
import os
import random
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

from scripts import sd101_check
from mkt import page as mkt_page
from scripts.figures import browser, cli, drawio, excalidraw, facebook, icons, mobile, moda, scene, spec, svg, text

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "figures"
POLLING = FIXTURES / "polling.json"
HOSTILE = '</text><script>alert(1)</script> ]]> <image href="https://x.test/a.png"/> & "quoted" \'single\' \x00\x0b'


def load(name: str = "polling.json") -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch().close()
        return True
    except Exception:
        return False


def parts_spec(count: int, flow: list[list[int]], icon: str | None = "server") -> dict:
    items = [{"name": f"Card {i}", "role": "What this card does in the flow.", **({"icon": icon} if icon else {})} for i in range(count)]
    return {"id": "t-parts", "title": "Title", "desc": "A figure drawn for a test of the layout.", "sections": [{"kind": "parts", "items": items, "flow": flow}]}


FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"a fake screenshot"


def half_write(self_, data):                                   # a stand-in for Path.write_bytes on a disk that fills after ten bytes
    with open(self_, "wb") as handle:
        handle.write(data[:10])
    raise OSError(28, "No space left on device")


def texts_of(root: ET.Element) -> str:
    return " ".join("".join(e.itertext()) for e in root.iter() if e.tag.endswith("text"))


class SpecTests(unittest.TestCase):
    def problems_after(self, change) -> list[str]:
        data = load()
        change(data)
        return spec.problems(data)

    def test_the_fixtures_are_valid_and_load(self):
        for name in ("polling.json", "stress.json", "small.json"):
            self.assertEqual(spec.problems(load(name)), [], name)
            self.assertEqual(spec.load(FIXTURES / name)["id"], load(name)["id"])

    def test_a_key_outside_the_vocabulary_is_refused_at_every_level(self):
        self.assertTrue(any("unknown keys" in p for p in self.problems_after(lambda d: d.update(colour="red"))))
        self.assertTrue(any("unknown keys" in p for p in self.problems_after(lambda d: d["sections"][0].update(x=1))))
        self.assertTrue(any("unknown keys" in p for p in self.problems_after(lambda d: d["sections"][1]["items"][0].update(svg="<g/>"))))
        self.assertTrue(any("unknown keys" in p for p in self.problems_after(lambda d: d["sections"][0]["messages"][0].update(color="red"))))

    def test_an_address_is_refused_in_any_text(self):
        for bad in ("see https://example.test/x", "go to www.example.test", "from assets.bytebytego.com", "ftp://host", "a://b", "ftp : //host", "ftp ://host", "a:/ /b",
                    "\uff46\uff54\uff50\uff1a\uff0f\uff0fhost"):
            self.assertTrue(any("address" in p for p in self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=bad))), bad)

    def test_an_icon_outside_the_set_is_refused_and_all_or_none_is_required(self):
        self.assertTrue(any("not in the icon set" in p for p in self.problems_after(lambda d: d["sections"][1]["items"][0].update(icon="<script>"))))
        self.assertTrue(any("every item or for none" in p for p in self.problems_after(lambda d: d["sections"][1]["items"][1].pop("icon"))))
        self.assertTrue(any("every item or for none" in p for p in self.problems_after(lambda d: d["sections"][0]["actors"][1].pop("icon"))))
        self.assertEqual(self.problems_after(lambda d: [i.pop("icon") for i in d["sections"][1]["items"]]), [])

    def test_a_flow_must_name_two_different_cards_once(self):
        for flow in ([[0, 9]], [[1, 1]], [[0, 1], [0, 1]], [[0]], [["a", "b"]], [[True, 2]]):
            self.assertTrue(spec.problems(parts_spec(3, flow)), flow)

    def test_counts_and_lengths_are_bounded(self):
        self.assertTrue(spec.problems(parts_spec(7, [])))
        self.assertTrue(spec.problems(parts_spec(1, [])))
        self.assertTrue(any("characters" in p for p in self.problems_after(lambda d: d.update(title="x" * 61))))
        self.assertTrue(any("characters" in p for p in self.problems_after(lambda d: d.update(desc="short"))))
        self.assertTrue(any("2-3 actors" in p for p in self.problems_after(lambda d: d["sections"][0]["actors"].append(dict(d["sections"][0]["actors"][0])) or d["sections"][0]["actors"].append({"name": "x"}))))

    def test_a_message_goes_between_two_different_actors(self):
        self.assertTrue(any("different one" in p for p in self.problems_after(lambda d: d["sections"][0]["messages"][0].update({"to": 0}))))
        self.assertTrue(any("different one" in p for p in self.problems_after(lambda d: d["sections"][0]["messages"][0].update({"to": 5}))))
        self.assertTrue(any("true or false" in p for p in self.problems_after(lambda d: d["sections"][0]["messages"][0].update(reply="yes"))))

    def test_too_many_cross_links_for_a_narrow_column_are_refused(self):
        many = [[0, 2], [0, 3], [1, 3], [1, 4], [2, 4], [0, 4]]
        self.assertTrue(any("lanes" in p for p in spec.problems(parts_spec(5, many))))
        self.assertEqual(spec.problems(parts_spec(5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]])), [])

    def test_characters_nobody_sees_but_that_change_the_drawing_are_refused(self):
        for label, bad in (("a lone surrogate", "a \ud800 b"), ("U+FFFE", "a \ufffe b"), ("a right-to-left override", "a \u202e b"),
                           ("a bidi isolate", "a \u2066 b"), ("a line separator", "a \u2028 b"), ("a carriage return", "a \r b"),
                           ("a left-to-right mark", "a \u200e b"), ("a right-to-left mark", "a \u200f b"), ("an Arabic letter mark", "a \u061c b"),
                           ("a zero-width space", "a \u200b b"), ("a byte-order mark", "a \ufeff b"), ("a soft hyphen", "a \u00ad b"),
                           ("a zero-width joiner", "a \u200d b"), ("a C1 control", "a \u0085 b"), ("DEL", "a \x7f b")):
            self.assertTrue(any("invisible character" in p for p in self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=bad))), label)
        for fine in ("Tiếng Việt, 日本語, \u00b7 và \u2192", "Ti\u0302\u0301ng Vie\u0323\u0302t (decomposed marks)", "tab\tand\nnew line"):
            self.assertEqual(self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=fine)), [], fine)

    def test_a_section_kind_that_is_not_text_is_a_problem_not_a_crash(self):
        for kind in ([], {}, [[]], 3, None, True, {"a": 1}):
            found = self.problems_after(lambda d: d["sections"][0].update(kind=kind))
            self.assertTrue(any("kind must be one of" in p for p in found), (kind, found))

    def test_bare_and_obfuscated_addresses_are_refused_and_technical_text_is_not(self):
        for bad in ("example.com", "see example.com today", "https : //example.com", "\uff45\uff58\uff41\uff4d\uff50\uff4c\uff45.com/x", "api.example.io/v1"):
            self.assertTrue(any("address" in p for p in self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=bad))), bad)
        for fine in ("Cache-Control: max-age=3600", "GET /api/v1/orders?page=2", "HTTP/2 và TLS 1.3", "Node.js 22", "v1.2.3", "Tỉ lệ 3:1 và 1/2", "Path: /api/v1", "Giờ 10:30 / 11:00"):
            self.assertEqual(self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=fine)), [], fine)

    def test_no_json_value_in_any_place_crashes_the_spec_check_and_an_accepted_spec_always_draws(self):
        rng = random.Random(20261017)
        junk = [None, True, False, 0, -1, 1.5, 10 ** 30, "", "x", " ", "\ud800", [], {}, [[]], [None], {"a": 1}, {"kind": []}, [[0, 1, 2]], "a" * 500, ["x"] * 20]

        def paths(node, prefix=()):
            yield prefix
            if isinstance(node, dict):
                for key, value in node.items():
                    yield from paths(value, prefix + (key,))
            elif isinstance(node, list):
                for i, value in enumerate(node):
                    yield from paths(value, prefix + (i,))

        base = load("stress.json")
        places = list(paths(base))
        accepted = 0
        for _ in range(2000):
            data = copy.deepcopy(base)
            for _ in range(rng.randint(1, 3)):
                path = rng.choice(places)
                if not path:
                    data = rng.choice(junk)
                    break
                node = data
                try:
                    for key in path[:-1]:
                        node = node[key]
                    if isinstance(node, dict) == isinstance(path[-1], str):      # JSON: a dict has text keys, a list has positions
                        node[path[-1]] = rng.choice(junk)
                except (KeyError, IndexError, TypeError):
                    pass                                    # an earlier change removed this place
            found = spec.problems(data)
            self.assertIsInstance(found, list)
            if not found:
                accepted += 1
                svg.figure(data)
                facebook.plan(data)
        self.assertGreater(accepted, 5)                     # the fuzz does reach the drawing code, not only the refusals

    def test_a_character_the_figure_cannot_measure_is_refused_and_the_measured_ones_are_not(self):
        for bad in ("\u2603 snowman", "emoji \U0001f600", "Greek \u03a9", "ligature \ufdfa"):
            found = self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=bad))
            self.assertTrue(any("cannot measure" in p for p in found), (bad, found))
        for fine in ("\u26a0 c\u1ea3nh b\u00e1o \u00ae \u00a9 \u2122", "\u0110\u01a1n h\u00e0ng \u0111\u00e3 giao \u2713 \u2192 \u2014 \u00b7 \u2026", "\u65e5\u672c\u8a9e\u3001\u30c6\u30b9\u30c8\u3002", "caf\u00e9 na\u00efve"):
            self.assertEqual(self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=fine)), [], fine)

    def test_an_ideographic_full_stop_between_ascii_names_is_a_dot_and_in_a_sentence_it_is_not(self):
        """A browser's address parser treats U+3002 and U+FF61 as a dot; Japanese prose uses them to end a sentence."""
        for bad in ("fb\u3002com/page", "example\u3002com", "example\uff61com", "\uff45\uff58\uff41\uff4d\uff50\uff4c\uff45\u3002\uff43\uff4f\uff4d", "a-b\u3002io/x"):
            self.assertTrue(spec.has_address(bad), bad)
            found = self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=bad))
            self.assertTrue(any("address" in p for p in found), (bad, found))
        for fine in ("\u52d5\u4f5c\u3057\u307e\u3059\u3002com\u306f", "\u3067\u3059\u3002AI\u306f", "Next\u3002 Then", "OK\u3002", "\u3053\u308c\u306f\u3002example"):
            self.assertFalse(spec.has_address(fine), fine)
            self.assertEqual(self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=fine)), [], fine)

    def test_a_mark_that_advances_in_the_font_is_refused_with_its_letter_and_the_accents_are_not(self):
        """Chromium gives many marks an advance of their own (a spacing mark, a mark of a script the font does not hold), so only measured marks pass."""
        for label, mark in (("Devanagari visarga (spacing)", "\u0903"), ("N'Ko tone mark", "\u07eb"), ("an enclosing circle", "\u20dd"),
                            ("a combining letter", "\u0363"), ("a grapheme joiner", "\u034f"), ("a half mark", "\u0350"),
                            ("a tag variation selector", "\U000e0100"), ("the emoji variation selector", "\ufe0f"), ("the text variation selector", "\ufe0e")):
            for bad in ("a" + mark, "a" + mark * 60, "\u65e5" + mark):
                found = self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=bad))
                self.assertTrue(any("cannot measure" in p for p in found), (label, bad, found))
        for fine in ("e\u0301", "x\u0301\u0323\u0302", "Vie\u0323\u0302t", "\u26a0", "a\u0300\u034e"):
            self.assertEqual(self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=fine)), [], fine)

    def test_a_combining_mark_with_no_letter_before_it_is_refused(self):
        for label, bad in (("only a mark", "\u0301"), ("two marks", "\u0301\u0301"), ("a mark after a space", "a \u0301 b"), ("a variation selector alone", "\ufe0f"),
                           ("a mark at the start", "\u0301abc"), ("a mark after a new line", "a\n\u0301")):
            found = self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=bad))
            self.assertTrue(any("combining mark with no letter" in p for p in found), (label, found))
        for fine in ("e\u0301", "x\u0301\u0323 and \u26a0", "Vie\u0323\u0302t"):
            self.assertEqual(self.problems_after(lambda d: d["sections"][2]["items"][0].update(text=fine)), [], fine)

    def test_lengths_are_counted_on_the_text_as_it_is_drawn(self):
        padded = "a" + " " * 18 + "b"                                     # 20 characters written, 3 drawn (a b)
        self.assertTrue(any("is 3 characters" in p for p in self.problems_after(lambda d: d.update(desc=padded))))
        self.assertTrue(any("is 3 characters" in p for p in self.problems_after(lambda d: d.update(desc="a\t\t\t\n\n\t\t\t\t\t\t\t\t\t\t\t\t\tb"))))
        long_gap = "x" + " " * 80 + "y"                                    # 82 written, 3 drawn: inside the title limit
        self.assertEqual(self.problems_after(lambda d: d.update(title=long_gap)), [])
        self.assertEqual(scene.build(dict(load(), title=long_gap), svg.STYLE)["items"][0]["text"], "x y")
        decomposed = "Vie\u0323\u0302t " * 8                                # 56 characters written, 48 drawn once composed
        self.assertEqual(self.problems_after(lambda d: d.update(title=decomposed + "n" * 10)), [])

    def test_a_language_outside_the_three_is_refused(self):
        self.assertTrue(any("lang" in p for p in self.problems_after(lambda d: d.update(lang="fr"))))

    def test_a_json_file_that_names_a_key_twice_or_is_not_json_is_an_error_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            twice = POLLING.read_text(encoding="utf-8").replace('"title": ', '"title": "first", "title": ', 1)   # a complete spec that names one key twice
            self.assertEqual(spec.problems(json.loads(twice)), [])
            for name, body in (("twice.json", twice), ("junk.json", "{nope"), ("list.json", "[]"), ("deep.json", "[" * 50000)):
                path = Path(tmp) / name
                path.write_text(body, encoding="utf-8")
                with self.assertRaises(spec.SpecError, msg=name):
                    spec.load(path)
            with self.assertRaises(spec.SpecError):
                spec.load(Path(tmp) / "missing.json")


class IconTests(unittest.TestCase):
    def tearDown(self):
        icons.shapes.cache_clear()
        icons.index.cache_clear()

    def copy_set(self, tmp: str) -> Path:
        target = Path(tmp) / "icons"
        shutil.copytree(icons.HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
        return target

    def verify_in(self, folder: Path) -> list[str]:
        with mock.patch.object(icons, "HERE", folder):
            icons.shapes.cache_clear()
            icons.index.cache_clear()
            try:
                return icons.verify()
            finally:
                icons.shapes.cache_clear()
                icons.index.cache_clear()

    def test_the_vendored_set_is_intact_and_every_icon_draws(self):
        self.assertEqual(icons.verify(), [])
        self.assertGreaterEqual(len(icons.NAMES), 80)
        for name in icons.NAMES:
            self.assertTrue(icons.gloss(name), name)
            ET.fromstring(icons.svg(name))

    def test_the_licence_and_the_notice_ship_with_the_icons(self):
        licence = (ROOT / "docs" / "third-party" / "lucide" / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("ISC License", licence)
        self.assertIn("scripts/figures/icons", (ROOT / "docs" / "third-party" / "lucide" / "NOTICE.md").read_text(encoding="utf-8"))
        self.assertIn("scripts/figures/icons/** -text", (ROOT / ".gitattributes").read_text(encoding="utf-8"))

    def test_a_changed_file_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.copy_set(tmp)
            (folder / "server.svg").write_text((folder / "server.svg").read_text(encoding="utf-8") + "\n", encoding="utf-8")
            self.assertTrue(any("server.svg differs" in p for p in self.verify_in(folder)))

    def test_an_extra_file_and_a_missing_file_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.copy_set(tmp)
            (folder / "extra.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'><path d='M0 0'/></svg>", encoding="utf-8")
            (folder / "lock.svg").unlink()
            found = self.verify_in(folder)
            self.assertTrue(any("extra.svg is in the folder" in p for p in found), found)
            self.assertTrue(any("lock.svg is listed" in p for p in found), found)

    def test_a_script_a_link_or_a_strange_attribute_in_an_icon_is_refused(self):
        bad = {"script": "<script>alert(1)</script>", "image": '<image href="https://x.test/a.png"/>',
               "style": '<path d="M0 0" style="fill:url(https://x.test)"/>', "fill": '<path d="M0 0" fill="red"/>',
               "onload": '<path d="M0 0" onload="x()"/>', "d": '<path d="M0 0 <script>"/>', "nested": '<path d="M0 0"><title>x</title></path>'}
        for label, body in bad.items():
            with tempfile.TemporaryDirectory() as tmp:
                folder = self.copy_set(tmp)
                (folder / "server.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg">{body}</svg>', encoding="utf-8")
                with mock.patch.object(icons, "HERE", folder):
                    icons.shapes.cache_clear()
                    with self.assertRaises(ValueError, msg=label):
                        icons.shapes("server")

    def test_group_is_plain_shapes_and_refuses_odd_arguments(self):
        out = icons.group("server", 10, 20, 36, tile="#0f766e")
        root = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{out}</svg>')
        self.assertEqual({e.tag.rsplit("}", 1)[-1] for e in root.iter()} - {"svg"}, {"circle", "g", "rect", "path", "line"} & {e.tag.rsplit("}", 1)[-1] for e in root.iter()})
        self.assertNotIn("<image", out)
        for bad in (dict(tile="red"), dict(tile="#0f766e", ink="url(#x)"), dict(tile='#0f766e" onload="x')):
            with self.assertRaises(ValueError):
                icons.group("server", 0, 0, 36, **bad)
        with self.assertRaises(ValueError):
            icons.group("server", 0, 0, 2, tile="#0f766e")
        with self.assertRaises(ValueError):
            icons.group("nope", 0, 0, 36, tile="#0f766e")

    def test_a_data_uri_decodes_to_the_icon(self):
        uri = icons.data_uri("database", size=48, tile="#1d4ed8")
        self.assertTrue(uri.startswith("data:image/svg+xml,"))
        self.assertNotIn(";", uri)
        self.assertEqual(base64.b64decode(uri.split(",", 1)[1]).decode("ascii"), icons.svg("database", size=48, tile="#1d4ed8"))


def segments(pts):
    return list(zip(pts, pts[1:]))


def crosses_inside(a, b, rect, inset=1.0) -> bool:
    """True when the straight, axis-aligned segment a-b runs through the inside of the rectangle (an edge touch is allowed)."""
    x0, y0, x1, y1 = rect["x"] + inset, rect["y"] + inset, rect["x"] + rect["w"] - inset, rect["y"] + rect["h"] - inset
    (ax, ay), (bx, by) = a, b
    lo_x, hi_x, lo_y, hi_y = min(ax, bx), max(ax, bx), min(ay, by), max(ay, by)
    return lo_x < x1 and hi_x > x0 and lo_y < y1 and hi_y > y0


def overlap(a, b) -> bool:
    """True when two axis-aligned segments lie on one line and share more than a point."""
    (ax0, ay0), (ax1, ay1), (bx0, by0), (bx1, by1) = *a, *b
    if ax0 == ax1 == bx0 == bx1:
        return min(max(ay0, ay1), max(by0, by1)) - max(min(ay0, ay1), min(by0, by1)) > 1
    if ay0 == ay1 == by0 == by1:
        return min(max(ax0, ax1), max(bx0, bx1)) - max(min(ax0, ax1), min(bx0, bx1)) > 1
    return False


class SceneTests(unittest.TestCase):
    def test_rails_are_shared_only_by_links_that_do_not_overlap_and_nest_outward(self):
        lanes = scene.assign_rails([(3, 0), (0, 2), (4, 5)])
        self.assertEqual(lanes[(0, 2)], 0)
        self.assertGreater(lanes[(3, 0)], lanes[(0, 2)])
        self.assertEqual(lanes[(4, 5)], 0)
        self.assertEqual(sorted(scene.assign_rails([(0, 3), (3, 0)]).values()), [0, 1])

    def test_the_ends_on_one_card_go_up_nearest_first_then_down_farthest_first(self):
        ends = [(5, 0, "out"), (3, 1, "out"), (0, 2, "in"), (1, 3, "in"), (4, 4, "out")]
        self.assertEqual([e[0] for e in scene.slot_order(2, ends)], [1, 0, 5, 4, 3])

    def test_random_flows_never_cross_a_card_or_share_a_line(self):
        rng = random.Random(20261017)
        checked = 0
        for _ in range(300):
            count = rng.randint(2, 6)
            pairs = [(a, b) for a in range(count) for b in range(count) if a != b]
            flow = [list(p) for p in rng.sample(pairs, rng.randint(0, min(8, len(pairs))))]
            data = parts_spec(count, flow, icon=rng.choice(["server", None]))
            if spec.problems(data):                                   # too many lanes for the column: refused by the spec, not drawn
                continue
            checked += 1
            built = scene.build(data, svg.STYLE)
            cards = {i["comp"]: i for i in built["items"] if i["k"] == "rect" and "comp" in i}
            panel = next(i for i in built["items"] if i["k"] == "rect" and i["role"] == "panel")
            arrows = [i for i in built["items"] if i["k"] == "arrow"]
            self.assertEqual(len(arrows), len({tuple(p) for p in flow}), flow)
            lines = [(arrow, seg) for arrow in arrows for seg in segments(arrow["pts"])]
            for arrow, (a, b) in lines:
                self.assertTrue(a[0] == b[0] or a[1] == b[1], f"a slanted segment in {flow}")
                for card in cards.values():
                    self.assertFalse(crosses_inside(a, b, card), f"an arrow runs through a card in {flow}")
                for point in (a, b):
                    self.assertTrue(panel["x"] <= point[0] <= panel["x"] + panel["w"] and panel["y"] <= point[1] <= panel["y"] + panel["h"], f"outside the panel in {flow}")
            for i, (arrow_a, seg_a) in enumerate(lines):
                for arrow_b, seg_b in lines[i + 1:]:
                    if arrow_a is not arrow_b:
                        self.assertFalse(overlap(seg_a, seg_b), f"two arrows share a line in {flow}")
        self.assertGreater(checked, 150)

    def test_a_chain_of_neighbour_links_uses_two_lanes_and_still_never_collides(self):
        for flow in ([[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]], [[0, 2], [2, 4], [3, 5]]):
            lanes = scene.assign_rails([tuple(p) for p in flow if not spec.forward(*p)])
            self.assertLessEqual(max(lanes.values()) + 1, 2, flow)
            data = parts_spec(6, flow)
            self.assertEqual(spec.problems(data), [], flow)
            built = scene.build(data, svg.STYLE)
            cards = [i for i in built["items"] if i["k"] == "rect" and "comp" in i]
            lines = [(a, seg) for a in built["items"] if a["k"] == "arrow" for seg in segments(a["pts"])]
            for _, (p, q) in lines:
                self.assertFalse(any(crosses_inside(p, q, card) for card in cards), flow)
            for i, (arrow_a, seg_a) in enumerate(lines):
                for arrow_b, seg_b in lines[i + 1:]:
                    self.assertTrue(arrow_a is arrow_b or not overlap(seg_a, seg_b), flow)

    def test_every_arrow_starts_and_ends_on_the_cards_it_joins(self):
        built = scene.build(parts_spec(4, [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]]), svg.STYLE)
        for arrow in (i for i in built["items"] if i["k"] == "arrow"):
            src, dst = built["items"][arrow["src"]], built["items"][arrow["dst"]]
            (x0, y0), (x1, y1) = arrow["pts"][0], arrow["pts"][-1]
            self.assertTrue(src["x"] - 3 <= x0 <= src["x"] + src["w"] + 3 and src["y"] - 3 <= y0 <= src["y"] + src["h"] + 3)
            self.assertTrue(dst["x"] - 3 <= x1 <= dst["x"] + dst["w"] + 3 and dst["y"] - 3 <= y1 <= dst["y"] + dst["h"] + 3)

    def test_text_stays_inside_the_card_that_holds_it(self):
        for name in ("polling.json", "stress.json"):
            built = scene.build(load(name), svg.STYLE)
            for item in built["items"]:
                if item["k"] == "text" and item["inside"] is not None:
                    card = built["items"][item["inside"]]
                    self.assertGreaterEqual(item["x"], card["x"], item["text"])
                    self.assertLessEqual(item["x"] + item["w"], card["x"] + card["w"] + 0.01, item["text"])
                    self.assertGreaterEqual(item["y"], card["y"], item["text"])
                    self.assertLessEqual(item["y"] + item["h"], card["y"] + card["h"] + 0.01, item["text"])

    def test_the_scene_holds_the_specs_words_and_no_others(self):
        data = load()
        words = {w for s in data["sections"] for v in json.dumps(s, ensure_ascii=False).split('"') for w in v.split()}
        words |= set(data["title"].split()) | set(data["subtitle"].split())
        for item in scene.build(data, svg.STYLE)["items"]:
            if item["k"] == "text":
                self.assertTrue(set(item["text"].split()) <= words, item["text"])
            if item["k"] == "badge":
                self.assertTrue(item["label"].isdigit())

    def test_bold_text_is_measured_in_bold(self):
        data = load()
        data["title"] = data["subtitle"] = "W" * 18                  # fits 288 px at 15 px regular (267), not in bold (298)
        built = scene.build(data, scene.Style(title=15, subtitle=15))
        title, subtitle = (next(i for i in built["items"] if i["k"] == "text" and i["color"] == c) for c in ("title", "muted"))
        self.assertGreater(len(title["lines"]), len(subtitle["lines"]))

    def test_a_scale_gives_the_same_scene_as_an_int_or_a_float(self):
        self.assertEqual(scene.scaled(scene.build(load(), svg.STYLE), 3), scene.scaled(scene.build(load(), svg.STYLE), 3.0))
        self.assertEqual(excalidraw.board(load(), 3), excalidraw.board(load(), 3.0))

    def test_a_scaled_scene_is_the_same_picture_larger(self):
        built = scene.build(load(), svg.STYLE)
        big = scene.scaled(built, 2)
        self.assertEqual(big["w"], 640)
        self.assertEqual([i["k"] for i in big["items"]], [i["k"] for i in built["items"]])
        self.assertEqual([i.get("lines") for i in big["items"]], [i.get("lines") for i in built["items"]])
        self.assertIs(scene.scaled(built, 1), built)

    def test_wrap_never_changes_the_text_or_overflows_a_box(self):
        rng = random.Random(7)
        alphabet = "abcdeAB 0123 ắềơ AI GitHub 日本語のテキスト, .-/"
        for _ in range(300):
            s = " ".join("".join(rng.choice(alphabet) for _ in range(rng.randint(1, 18))) for _ in range(rng.randint(1, 8)))
            px, box = rng.choice([14, 16, 20]), rng.choice([60, 120, 280])
            lines = text.wrap(s, px, box)
            self.assertEqual("".join(lines).replace(" ", ""), "".join(s.split()), s)
            for line in lines:
                self.assertTrue(text.width(line, px) <= box or len(line) <= 1, (line, box))


class TextTests(unittest.TestCase):
    def test_a_combining_mark_advances_nothing_and_never_starts_a_line(self):
        self.assertEqual(text.width("x\u0301", 15), text.width("x", 15))
        word = "x\u0301" * 30                                   # no composed form exists: the mark stays a character of its own
        for box in range(1, 200, 2):                         # also boxes narrower than one letter, where the first character is already too wide
            for line in text.wrap(word, 15, box):
                self.assertFalse(text.combining(line[0]), (box, line))
        self.assertEqual("".join(text.wrap(word, 15, 60)), word)

    def test_only_the_marks_measured_at_no_advance_are_measured_at_none(self):
        for o in range(0x0300, 0x034F):
            self.assertEqual(text.width("a" + chr(o), 100), text.width("a", 100), hex(o))
            self.assertTrue(text.measurable(chr(o)), hex(o))
        for o in (0x034F, 0x0350, 0x0363, 0x036F, 0x0903, 0x07EB, 0x1AB0, 0x20DD, 0xFE00, 0xFE0F, 0xFE20, 0xE0100):
            self.assertGreater(text.width("a" + chr(o), 100), text.width("a", 100), hex(o))     # an unknown mark is counted as a letter, never as nothing
            self.assertFalse(text.measurable(chr(o)), hex(o))
            self.assertTrue(text.combining(chr(o)), hex(o))                                      # but it still never starts a line
        self.assertGreater(text.width("a\u3099", 100), text.width("a", 100))                       # a dakuten is counted as the wide (CJK) character it sits in the table as

    def test_symbols_and_vietnamese_capital_d_are_measured_at_least_as_wide_as_the_font_draws_them(self):
        for char, regular, bold in (("\u26a0", 896, 896), ("\u00ae", 1000, 1000), ("\u00a9", 1000, 1000), ("\u2122", 1000, 1000), ("\u0110", 775, 838), ("\u0111", 635, 716)):
            self.assertGreaterEqual(text.width(char, 1000), regular, char)
            self.assertGreaterEqual(text.width(char, 1000, True), bold, char)

    def test_only_what_the_width_table_knows_is_measurable(self):
        self.assertTrue(all(text.measurable(c) for c in "aZ0 ~\u00e9\u1ebf\u0301\u26a0\u65e5\n"))
        self.assertFalse(any(text.measurable(c) for c in "\u2603\U0001f600\u03a9\ufdfa"))

    def test_text_is_composed_before_it_is_measured_and_drawn(self):
        data = load()
        data["title"] = "Tie\u0302\u0301ng Vie\u0323\u0302t"
        built = scene.build(data, svg.STYLE)
        titles = [i["text"] for i in built["items"] if i["k"] == "text" and i["color"] == "title"]
        self.assertEqual(titles, ["Tiếng Việt"])
        self.assertIn("Tiếng Việt", svg.figure(data))


class SvgTests(unittest.TestCase):
    def test_the_figure_passes_the_stores_own_svg_rules_and_the_phone_rules(self):
        for name in ("polling.json", "stress.json"):
            markup = svg.figure(load(name))
            self.assertIsNone(cli._store_problem(markup), name)
            self.assertEqual(mobile.check(markup), [], name)
            root = ET.fromstring(markup)
            self.assertEqual(root.get("role"), "img")
            self.assertEqual(root.get("viewBox"), f"0 0 {root.get('width')} {root.get('height')}")
            self.assertEqual(root.get("width"), "320")

    def test_only_plain_drawing_elements_and_no_address_are_used(self):
        markup = svg.figure(load())
        names = {e.tag.rsplit("}", 1)[-1] for e in ET.fromstring(markup).iter()}
        self.assertLessEqual(names, sd101_check.SVG_ELEMENTS)
        for banned in ("<image", "<script", "<foreignObject", "http://www.w3.org/1999/xlink", "href="):
            self.assertNotIn(banned, markup)
        self.assertNotIn("https://", markup)

    def test_a_reply_is_a_dashed_arrow_and_a_request_is_not(self):
        data = load()
        replies = sum(1 for m in data["sections"][0]["messages"] if m.get("reply"))
        self.assertEqual(svg.figure(data).count('stroke-dasharray="5 4"'), replies)

    def test_the_same_spec_gives_the_same_bytes(self):
        self.assertEqual(svg.figure(load()), svg.figure(copy.deepcopy(load())))

    def test_hostile_text_stays_text_everywhere(self):
        """The spec check refuses addresses and control characters; the writer escapes what is left, and what a spec check would miss."""
        data = load()
        data["title"], data["subtitle"] = HOSTILE[:60], "ok"
        data["sections"][1]["items"][0]["name"] = HOSTILE[:30]
        data["sections"][2]["items"][0]["text"] = HOSTILE[:100]
        data["desc"] = "A description with " + HOSTILE[:90]
        data["sections"][3]["items"][0] = HOSTILE
        found = spec.problems(data)
        self.assertTrue(any("address" in p for p in found), found)
        self.assertTrue(any("invisible character" in p for p in found), found)
        markup = svg.figure(data)                           # drawn anyway: the writer is the second lock
        root = ET.fromstring(markup)
        self.assertEqual({e.tag.rsplit("}", 1)[-1] for e in root.iter()} - sd101_check.SVG_ELEMENTS, set())
        self.assertNotIn("\x00", markup)
        self.assertNotIn("\x0b", markup)
        self.assertIn("alert(1)", texts_of(root))
        self.assertEqual([e for e in root.iter() if e.tag.endswith("script") or e.tag.endswith("image")], [])
        self.assertIsNone(cli._store_problem(markup))        # a link that is only text is not a link to the store's rules either

    def test_every_icon_is_drawn_from_its_own_shapes(self):
        markup = svg.figure(parts_spec(2, [[0, 1]], icon="key-round"))
        self.assertEqual(markup.count('stroke-linecap="round"'), 2)
        shapes = "".join(f"<{tag} " + " ".join(f'{k}="{"#ffffff" if v == "currentColor" else v}"' for k, v in attrs) + "/>" for tag, attrs in icons.shapes("key-round"))
        self.assertEqual(markup.count(shapes.replace("#ffffff", "#FFFFFF")), 2)
        tiles = re.findall(r'<circle cx="[\d.]+" cy="[\d.]+" r="18" fill="(#[0-9a-f]{6})"/><g transform', markup)
        self.assertEqual(tiles, [svg.ACCENT["card0"]] * 2)

    def test_text_that_is_too_small_or_runs_off_the_drawing_is_reported(self):
        markup = svg.figure(load())
        self.assertEqual(mobile.check(markup), [])
        small = markup.replace('font-size="15"', 'font-size="13"', 1)
        self.assertTrue(any("13 px on a 375 px screen" in p or "px on a 320 px screen" in p for p in mobile.check(small)))
        wide = re.sub(r'viewBox="0 0 320 (\d+)"', r'viewBox="0 0 640 \1"', markup)
        self.assertTrue(any("px on a 375 px screen" in p for p in mobile.check(wide)))
        off = markup.replace('<text x="16"', '<text x="-40"', 1)
        self.assertTrue(any("runs past the edge" in p for p in mobile.check(off)))
        narrow_only = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 20"><text x="4" y="14" font-size="14.8">Hi</text></svg>'
        self.assertEqual([p for p in mobile.check(narrow_only) if "375" in p], [])
        self.assertTrue(any("on a 320 px screen" in p for p in mobile.check(narrow_only)))
        self.assertTrue(any("no viewBox" in p for p in mobile.check('<svg xmlns="http://www.w3.org/2000/svg"/>')))
        self.assertTrue(any("not well-formed" in p for p in mobile.check("<svg")))
        self.assertTrue(any("no font-size" in p for p in mobile.check('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 10"><text x="1">a</text></svg>')))


class EditorTests(unittest.TestCase):
    def cells(self, data: dict) -> list[ET.Element]:
        return list(ET.fromstring(drawio.diagram(data)).iter("mxCell"))

    def test_every_connector_is_attached_to_two_cards_with_ports_on_their_edges(self):
        for name in ("polling.json", "stress.json"):
            cells = self.cells(load(name))
            ids = {c.get("id"): c for c in cells}
            attached = [c for c in cells if c.get("edge") and c.get("source")]
            self.assertTrue(attached, name)
            for c in attached:
                self.assertIn(c.get("source"), ids)
                self.assertIn(c.get("target"), ids)
                style = dict(p.split("=", 1) for p in c.get("style").split(";") if "=" in p)
                for key in ("exitX", "exitY", "entryX", "entryY"):
                    self.assertTrue(0 <= float(style[key]) <= 1, (key, style))

    def test_a_small_editor_scale_still_draws_and_the_icon_file_does_not_follow_it(self):
        for scale in (0.1, 0.25, 2, 8):
            drawio.diagram(load(), scale)
        for c in self.cells(load()):
            if "shape=image" in (c.get("style") or ""):
                uri = re.search(r"image=data:image/svg\+xml,([A-Za-z0-9+/=]+)", c.get("style")).group(1)
                self.assertEqual(ET.fromstring(base64.b64decode(uri)).get("width"), str(drawio.ICON_PX))

    def test_the_diagram_holds_each_line_of_text_and_each_icon_once(self):
        data = load()
        built = scene.build(data, drawio.STYLE)
        xml = drawio.diagram(data)
        for item in built["items"]:
            if item["k"] == "text":
                for line in item["lines"]:
                    self.assertIn(line.replace("&", "&amp;"), xml.replace("&amp;amp;", "&amp;").replace("&amp;", "&amp;"), line)
        icon_cells = [c for c in self.cells(data) if "shape=image" in (c.get("style") or "")]
        self.assertEqual(len(icon_cells), sum(1 for i in built["items"] if i["k"] == "icon"))
        for c in icon_cells:
            uri = re.search(r"image=data:image/svg\+xml,([A-Za-z0-9+/=]+)", c.get("style")).group(1)
            inner = base64.b64decode(uri).decode("ascii")
            self.assertEqual({e.tag.rsplit("}", 1)[-1] for e in ET.fromstring(inner).iter()} - {"svg", "circle", "g", "path", "rect", "line", "polyline", "polygon", "ellipse"}, set())

    def test_hostile_text_stays_text_in_the_three_editor_files(self):
        data = load()
        data["title"] = "Tiêu đề " + HOSTILE[:40].replace("https://x.test/a.png", "x")
        data["sections"][2]["items"][0]["text"] = HOSTILE[:100].replace("https://x.test/a.png", "x")
        files = {"drawio": drawio.diagram(data), "moda": moda.markup(data).split("\n", 1)[1]}
        for label, xml in files.items():
            root = ET.fromstring(xml)
            names = {e.tag for e in root.iter()}
            self.assertFalse({n for n in names if "script" in n.lower() or n.lower() in ("image", "img")}, label)
            self.assertNotIn("\x00", xml)
        board = json.loads(excalidraw.board(data))
        self.assertTrue(any("alert(1)" in e.get("text", "") for e in board["elements"]))
        self.assertTrue(any("alert(1)" in "".join(c.get("value") or "" for c in [x]) for x in self.cells(data)))

    def test_excalidraw_is_valid_numbered_and_repeatable(self):
        board = json.loads(excalidraw.board(load()))
        self.assertEqual(board["type"], "excalidraw")
        ids = [e["id"] for e in board["elements"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({"rectangle", "text", "arrow", "ellipse", "line"} <= {e["type"] for e in board["elements"]})
        self.assertEqual(excalidraw.board(load()), excalidraw.board(copy.deepcopy(load())))
        self.assertTrue(any(e["strokeStyle"] == "dashed" and e["type"] == "arrow" for e in board["elements"]))

    def test_moda_markup_is_well_formed_uses_the_spec_language_font_and_draws_no_pictograms(self):
        for lang, font in (("vi", "Be Vietnam Pro"), ("en", "Be Vietnam Pro"), ("ja", "Noto Sans JP")):
            data = load()
            data["lang"] = lang
            xml = moda.markup(data)
            ET.fromstring(xml.split("\n", 1)[1])
            self.assertIn(f'font-family="{font}"', xml)
        self.assertNotIn("<image", xml)
        self.assertIn('dash="', xml)

    def test_editor_files_are_twice_the_figure_by_default_and_follow_the_scale(self):
        self.assertIn('pageWidth="640"', drawio.diagram(load()))
        self.assertIn('pageWidth="480"', drawio.diagram(load(), 1.5))
        self.assertIn("640x", moda.markup(load()).splitlines()[0])


@unittest.skipUnless(chromium_available(), "Chromium not installed")
class BrowserTests(unittest.TestCase):
    def test_every_line_fits_its_box_in_the_real_font(self):
        for name in ("polling.json", "stress.json"):
            self.assertEqual(browser.measure(load(name)), [], name)

    def test_a_style_that_underestimates_the_font_is_caught(self):
        too_narrow = scene.Style(wscale=0.7)
        self.assertTrue(browser.measure(load(), too_narrow))

    def test_the_width_table_is_at_least_what_the_browser_measures_for_every_character(self):
        from playwright.sync_api import sync_playwright
        chars = [chr(c) for c in range(32, 127)] + list(text._OTHER)
        escape = {"<": "&lt;", ">": "&gt;", "&": "&amp;"}
        with sync_playwright() as p:
            chromium = p.chromium.launch()
            try:
                page = chromium.new_page()
                for weight, bold in (("normal", False), ("bold", True)):
                    body = "".join(f'<text id="t{i}" xml:space="preserve" x="0" y="50" font-size="100" font-weight="{weight}">{escape.get(c, c)}</text>' for i, c in enumerate(chars))
                    page.set_content('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="100"><g font-family="DejaVu Sans, Arial, sans-serif">' + body + "</g></svg>")
                    for i, c in enumerate(chars):
                        real = page.evaluate(f"document.getElementById('t{i}').getComputedTextLength()")
                        self.assertGreaterEqual(text.width(c, 100, bold), real - 0.6, (c, weight))
            finally:
                chromium.close()

    def test_the_marks_a_figure_may_use_advance_nothing_in_the_real_font(self):
        from playwright.sync_api import sync_playwright
        marks = [chr(o) for lo, hi in text.ZERO_MARKS for o in range(lo, hi + 1)]
        with sync_playwright() as p:
            chromium = p.chromium.launch()
            try:
                page = chromium.new_page()
                page.set_content('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="100"><g font-family="DejaVu Sans, Arial, sans-serif" font-size="100">'
                                 '<text id="t" xml:space="preserve" x="0" y="50">a</text></g></svg>')
                base = page.evaluate("document.getElementById('t').getComputedTextLength()")
                widths = page.evaluate("""(chars) => { const t = document.getElementById('t'); return chars.map(c => { t.textContent = 'a' + c; return t.getComputedTextLength(); }); }""", marks)
            finally:
                chromium.close()
        self.assertEqual([hex(ord(c)) for c, w in zip(marks, widths) if w > base + 0.6], [])

    def test_a_run_of_accents_still_fits_its_card_in_the_real_font(self):
        data = load("small.json")
        data["sections"][1]["items"] = ["a\u0301\u0323\u0302" * 30, "\u26a0" * 20 + " ge\u0300 " * 6]
        self.assertEqual(spec.problems(data), [])
        self.assertEqual(browser.measure(data), [])

    def test_a_run_of_wide_symbols_still_fits_its_card_in_the_real_font(self):
        data = load("small.json")
        data["sections"][1]["items"] = ["\u26a0" * 40, "\u00ae" * 40 + " " + "\u0110" * 30]
        self.assertEqual(spec.problems(data), [])
        self.assertEqual(browser.measure(data), [])

    def test_png_is_drawn_at_the_requested_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "f.png"
            markup = svg.figure(load())
            browser.png(markup, out, 320, int(re.search(r'height="(\d+)"', markup).group(1)), 1.0)
            self.assertEqual(out.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


def too_tall(count: int = 6) -> dict:
    data = parts_spec(count, [[i, i + 1] for i in range(count - 1)])
    for item in data["sections"][0]["items"]:
        item["role"] = "A long role that fills three lines of the card so that the section grows taller than any slide can show."
    return data


class FacebookTests(unittest.TestCase):
    def test_the_canvas_sizes_are_the_studios_own(self):
        self.assertIs(facebook.FORMATS, mkt_page.FORMATS)
        self.assertEqual(facebook.FORMATS["portrait"], (1080, 1350))
        self.assertEqual(facebook.DEFAULT, "portrait")

    def test_a_figure_becomes_one_slide_per_section_inside_the_canvas_with_readable_text(self):
        for name, fmt in (("polling.json", "portrait"), ("small.json", "portrait"), ("small.json", "square")):
            slides, problems = facebook.plan(load(name), fmt)
            width, height = facebook.FORMATS[fmt]
            self.assertEqual(problems, [], (name, fmt))
            self.assertEqual(len(slides), len(load(name)["sections"]))
            for slide in slides:
                self.assertGreaterEqual(slide["x"], facebook.PAD - 0.5)
                self.assertLessEqual(slide["x"] + slide["w"], width - facebook.PAD + 0.5)
                self.assertGreaterEqual(slide["y"], facebook.PAD - 0.5)
                self.assertLessEqual(slide["y"] + slide["h"], height - facebook.FOOT + 0.5)
                smallest = min(i["px"] for i in slide["scene"]["items"] if i["k"] == "text") * slide["k"]
                self.assertGreaterEqual(smallest, facebook.MIN_TEXT_PX)

    def test_the_square_canvas_refuses_the_tall_section_the_portrait_canvas_takes(self):
        self.assertEqual(facebook.plan(load(), "portrait")[1], [])
        self.assertTrue(any("slide 2" in p and "1080x1080" in p for p in facebook.plan(load(), "square")[1]))

    def test_the_subtitle_is_on_the_first_slide_only_and_the_title_on_every_slide(self):
        slides, _ = facebook.plan(load())
        for slide in slides:
            words = [i["text"] for i in slide["scene"]["items"] if i["k"] == "text"]
            self.assertIn(load()["title"], words)
            self.assertEqual(load()["subtitle"] in words, slide["n"] == 1)

    def test_a_section_that_cannot_be_scaled_to_readable_text_is_refused_with_its_slide_number(self):
        slides, problems = facebook.plan(too_tall())
        self.assertEqual(len(slides), 1)
        self.assertEqual(len(problems), 1)
        self.assertIn("slide 1", problems[0])
        self.assertIn("split the section", problems[0])

    def test_more_slides_than_a_post_takes_and_an_unknown_format_are_refused(self):
        data = parts_spec(2, [[0, 1]])
        data["sections"] = data["sections"] * (facebook.MAX_SLIDES + 1)
        self.assertTrue(any("at most" in p for p in facebook.plan(data)[1]))
        self.assertTrue(any("format must be" in p for p in facebook.plan(load(), "banner")[1]))

    def test_the_footer_is_the_studios_handle_bottom_left_and_the_number_bottom_right(self):
        slides, _ = facebook.plan(load())
        html = facebook.page(slides[1], len(slides), "portrait", '@page <b>&"x')
        self.assertIn("2/4", html)
        self.assertIn("@page &lt;b&gt;&amp;&quot;x", html)
        self.assertNotIn("<b>", html)
        self.assertIn("width:1080px;height:1350px", html)
        self.assertIn("<span></span><span>2/4</span>", facebook.page(slides[1], 4, "portrait", ""))

    def test_the_handle_comes_from_studio_yaml_and_is_empty_when_it_cannot_be_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(facebook.handle(root), "")
            (root / "studio.yaml").write_text("author:\n  handle: ' fb.com/page '\n", encoding="utf-8")
            self.assertEqual(facebook.handle(root), "fb.com/page")
            for body in ("author: [1]\n", "- a\n", ": : :\n", "author:\n  handle: ''\n"):
                (root / "studio.yaml").write_text(body, encoding="utf-8")
                self.assertEqual(facebook.handle(root), "", body)

    def test_a_written_slide_is_checked_for_type_size_and_weight(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "01.png"
            header = b"\x89PNG\r\n\x1a\n" + (13).to_bytes(4, "big") + b"IHDR"
            path.write_bytes(header + (1080).to_bytes(4, "big") + (1350).to_bytes(4, "big") + b"\0" * 10)
            self.assertEqual(facebook.png_problems(path), [])
            path.write_bytes(header + (1080).to_bytes(4, "big") + (1080).to_bytes(4, "big"))
            self.assertTrue(any("1080x1080" in p for p in facebook.png_problems(path)))
            path.write_bytes(header + (1080).to_bytes(4, "big") + (1350).to_bytes(4, "big") + b"\0" * (facebook.MAX_BYTES + 1))
            self.assertTrue(any("bytes" in p for p in facebook.png_problems(path)))
            path.write_bytes(b"GIF89a" + b"\0" * 30)
            self.assertEqual(facebook.png_problems(path), [f"{path.name} is not a PNG"])

    def test_the_alt_text_uses_only_the_specs_words(self):
        slides, _ = facebook.plan(load())
        lines = facebook.alt_text(load(), slides).splitlines()
        self.assertEqual(lines[0], load()["desc"])
        self.assertEqual(lines[1:], [f"{s['n']}/4: {s['heading']}" for s in slides])

    def test_a_figure_with_a_section_too_tall_for_the_standard_fails_the_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tall.json"
            path.write_text(json.dumps(too_tall()), encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["check", str(path)]), 1)
            self.assertIn("split the section", err.getvalue())
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["facebook", str(path), "--out", str(Path(tmp) / "out")]), 1)
            self.assertFalse((Path(tmp) / "out").exists())

    def test_nothing_is_written_when_the_plan_has_problems(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(browser, "png") as draw:
            files, problems = facebook.export(too_tall(), Path(tmp), ROOT)
            draw.assert_not_called()                           # refused before any slide is drawn, not after
            self.assertEqual(files, [])
            self.assertTrue(problems)
            self.assertFalse((Path(tmp) / "t-parts").exists())

    def fake_png(self, calls=None, fail_on=None, error=browser.Unavailable("no chromium")):
        """A stand-in for browser.png that writes a PNG header of the canvas size, so the export logic runs without a browser."""
        def draw(markup, path, width, height, scale=1.0):
            if calls is not None:
                calls.append(path.name)
            if fail_on is not None and len(calls or []) == fail_on:
                raise error
            path.write_bytes(b"\x89PNG\r\n\x1a\n" + (13).to_bytes(4, "big") + b"IHDR" + width.to_bytes(4, "big") + height.to_bytes(4, "big") + b"\0" * 20)
        return draw

    def old_pack(self, out: Path) -> Path:
        folder = out / "demo-small"
        folder.mkdir()
        for name in ("01.png", "02.png", "09.png", "alt.txt"):
            (folder / name).write_bytes(b"old " + name.encode())
        return folder

    def test_a_footer_handle_that_is_an_address_is_refused_before_anything_is_drawn(self):
        small = load("small.json")
        for handle in ("fb.com/your-page", "https://example.test/page", "www.example.test", "fb\u3002com/page", "ftp : // host", "\uff46\uff54\uff50\uff1a\uff0f\uff0fhost"):
            with tempfile.TemporaryDirectory() as tmp:
                root, out = Path(tmp) / "root", Path(tmp) / "out"
                root.mkdir()
                (root / "studio.yaml").write_text(f"author:\n  handle: {json.dumps(handle)}\n", encoding="utf-8")
                calls: list[str] = []
                with mock.patch.object(browser, "png", self.fake_png(calls)):
                    files, problems = facebook.export(small, out, root)
                self.assertEqual((files, calls, out.exists()), ([], [], False), handle)       # nothing drawn, nothing created
                self.assertTrue(any("author.handle" in p and "is an address" in p for p in problems), (handle, problems))
        for handle in ("@your-page", "Your Page", "", "vohoailinh90"):                         # a page name is not an address
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "root"
                root.mkdir()
                (root / "studio.yaml").write_text(f"author:\n  handle: {json.dumps(handle)}\n", encoding="utf-8")
                with mock.patch.object(browser, "png", self.fake_png([])):
                    files, problems = facebook.export(small, Path(tmp) / "out", root)
                self.assertEqual(problems, [], handle)
                self.assertTrue(files, handle)

    def test_a_pack_folder_that_is_a_file_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "demo-small").write_text("the owner's file, not a pack", encoding="utf-8")
            calls: list[str] = []
            with mock.patch.object(browser, "png", self.fake_png(calls)):
                files, problems = facebook.export(load("small.json"), out, Path(tmp))
            self.assertEqual((files, calls), ([], []))
            self.assertTrue(any("is not a folder" in p for p in problems), problems)
            self.assertEqual((out / "demo-small").read_text(encoding="utf-8"), "the owner's file, not a pack")
            self.assertEqual(sorted(p.name for p in out.iterdir()), ["demo-small"])

    def test_a_failed_export_leaves_the_previous_pack_and_no_temporary_folder(self):
        for label, fail_on, patch_size in (("the browser cannot start", 1, False), ("the second slide fails", 2, False), ("a slide is too heavy", None, True)):
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp)
                folder = self.old_pack(out)
                calls: list[str] = []
                with mock.patch.object(browser, "png", self.fake_png(calls, fail_on)), mock.patch.object(facebook, "MAX_BYTES", 10 if patch_size else facebook.MAX_BYTES):
                    if fail_on:
                        with self.assertRaises(browser.Unavailable):
                            facebook.export(load("small.json"), out, ROOT)
                    else:
                        files, problems = facebook.export(load("small.json"), out, ROOT)
                        self.assertEqual(files, [])
                        self.assertTrue(any("bytes" in p for p in problems))
                self.assertEqual(sorted(p.name for p in folder.iterdir()), ["01.png", "02.png", "09.png", "alt.txt"], label)
                self.assertEqual((folder / "01.png").read_bytes(), b"old 01.png", label)
                self.assertEqual([p.name for p in out.iterdir()], ["demo-small"], label)

    def test_two_exports_of_one_figure_at_the_same_time_do_not_share_a_staging_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            inner: list = []
            draw_once = self.fake_png()

            def draw(markup, path, width, height, scale=1.0):
                if not inner:                                   # while the first export is drawing its first slide, a second one runs to the end
                    inner.append(None)
                    inner[0] = facebook.export(load("small.json"), out, ROOT)
                draw_once(markup, path, width, height, scale)

            with mock.patch.object(browser, "png", draw):
                files, problems = facebook.export(load("small.json"), out, ROOT)
            self.assertEqual((problems, [f.name for f in files]), ([], ["01.png", "02.png"]))
            self.assertEqual(inner[0][1], [])
            self.assertEqual(sorted(p.name for p in (out / "demo-small").iterdir()), ["01.png", "02.png", "alt.txt"])
            self.assertEqual([p.name for p in out.iterdir()], ["demo-small"])

    def test_the_old_pack_is_kept_until_the_new_one_is_in_place(self):
        real = os.replace
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            folder, work = out / "pack", out / "work"
            work.mkdir()
            (work / "new.txt").write_text("new", encoding="utf-8")
            folder.mkdir()
            (folder / "old.txt").write_text("old", encoding="utf-8")

            def fails_to_install(src, dst):                     # installing the new pack never works; every other rename does
                if Path(src) == work:
                    raise OSError("disk trouble")
                return real(src, dst)

            with mock.patch("os.replace", side_effect=fails_to_install):
                with self.assertRaises(OSError):
                    facebook.swap(work, folder)
            self.assertEqual([p.name for p in folder.iterdir()], ["old.txt"])            # the previous pack is back
            self.assertTrue((work / "new.txt").is_file())
            self.assertEqual(sorted(p.name for p in out.iterdir()), ["pack", "work"])   # and no backup folder is left

            def fails_to_install_or_restore(src, dst):          # the old pack cannot even be put back
                if Path(src) == work or (Path(dst) == folder and Path(src).name == "pack" and Path(src).parent != out):
                    raise OSError("disk trouble")
                return real(src, dst)

            with mock.patch("os.replace", side_effect=fails_to_install_or_restore):
                with self.assertRaises(OSError) as caught:
                    facebook.swap(work, folder)
            self.assertIn("the previous pack is kept in", str(caught.exception))
            kept = Path(str(caught.exception).split("the previous pack is kept in ")[1])
            self.assertEqual([p.name for p in kept.iterdir()], ["old.txt"])             # not deleted: it is the only copy

    def test_the_alt_text_has_one_line_per_slide_whatever_the_specs_text_holds(self):
        data = load("small.json")
        data["desc"] = "first line\nsecond line\twith a tab, long enough to be a description"
        data["sections"][0]["heading"] = "Làm\nlần lượt"
        data["sections"][1].pop("heading")
        data["title"] = "Ba\nbước"
        slides, _ = facebook.plan(data)
        lines = facebook.alt_text(data, slides).splitlines()
        self.assertEqual(lines, ["first line second line with a tab, long enough to be a description", "1/2: Làm lần lượt", "2/2: Ba bước"])

    def test_a_competing_export_never_leaves_a_mix_of_two_packs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            three = load("small.json")
            three["sections"].append({"kind": "notes", "heading": "Thêm", "items": ["Một ý nữa.", "Và một ý khác."]})
            inner: list = []
            draw_once = self.fake_png()
            calls: list = []

            def draw(markup, path, width, height, scale=1.0):
                calls.append(path.name)
                draw_once(markup, path, width, height, scale)
                if len(calls) == 2 and not inner:               # the first export has drawn its last slide: a longer export of the same figure runs and finishes
                    inner.append(None)
                    inner[0] = facebook.export(three, out, ROOT)

            with mock.patch.object(browser, "png", draw):
                files, problems = facebook.export(load("small.json"), out, ROOT)
            self.assertEqual((problems, inner[0][1]), ([], []))
            self.assertEqual(len(inner[0][0]), 3)
            self.assertEqual(sorted(p.name for p in (out / "demo-small").iterdir()), ["01.png", "02.png", "alt.txt"])      # the last export, whole: no 03.png of the other
            self.assertEqual((out / "demo-small" / "alt.txt").read_text(encoding="utf-8").count("/2:"), 2)
            self.assertEqual([p.name for p in out.iterdir()], ["demo-small"])

    def test_swap_puts_a_folder_in_place_in_one_rename_and_gives_up_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for existing in (False, True):
                folder, work = out / "pack", out / "work"
                work.mkdir()
                (work / "new.txt").write_text("new", encoding="utf-8")
                if existing:
                    folder.mkdir()
                    (folder / "old.txt").write_text("old", encoding="utf-8")
                facebook.swap(work, folder)
                self.assertEqual([p.name for p in folder.iterdir()], ["new.txt"])
                self.assertEqual(sorted(p.name for p in out.iterdir()), ["pack"])
                shutil.rmtree(folder)
            work.mkdir()
            folder.mkdir()
            with mock.patch("os.replace", side_effect=OSError("never")):
                with self.assertRaises(OSError):
                    facebook.swap(work, folder)
            self.assertEqual(sorted(p.name for p in out.iterdir()), ["pack", "work"])

    def test_a_successful_export_replaces_the_whole_previous_pack_and_leaves_no_temporary_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            folder = self.old_pack(out)
            with mock.patch.object(browser, "png", self.fake_png()):
                files, problems = facebook.export(load("small.json"), out, ROOT)
            self.assertEqual(problems, [])
            self.assertEqual([f.name for f in files], ["01.png", "02.png"])
            self.assertEqual(sorted(p.name for p in folder.iterdir()), ["01.png", "02.png", "alt.txt"])
            self.assertNotEqual((folder / "01.png").read_bytes(), b"old 01.png")
            self.assertIn("1/2:", (folder / "alt.txt").read_text(encoding="utf-8"))
            self.assertEqual([p.name for p in out.iterdir()], ["demo-small"])

    @unittest.skipUnless(chromium_available(), "Chromium not installed")
    def test_export_writes_png_slides_of_the_exact_canvas_size_and_replaces_old_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "demo-polling").mkdir()
            (out / "demo-polling" / "09.png").write_bytes(b"stale")
            files, problems = facebook.export(load(), out, ROOT)
            self.assertEqual(problems, [])
            self.assertEqual([f.name for f in files], ["01.png", "02.png", "03.png", "04.png"])
            self.assertFalse((out / "demo-polling" / "09.png").exists())
            for file in files:
                self.assertEqual(facebook.png_problems(file), [], file.name)
            self.assertTrue((out / "demo-polling" / "alt.txt").is_file())
            self.assertEqual(cli.main(["facebook", str(FIXTURES / "small.json"), "--format", "square", "--out", str(out / "sq")]), 0)
            self.assertEqual(facebook.png_problems(out / "sq" / "demo-small" / "01.png", "square"), [])


class RobustnessTests(unittest.TestCase):
    def run_cli(self, *argv: str) -> tuple[int, str]:
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            try:
                code = cli.main(list(argv))
            except SystemExit as exc:
                code = exc.code
        return code, err.getvalue()

    def test_a_scale_that_would_draw_garbage_is_refused(self):
        for bad in ("nan", "inf", "-2", "0", "0.1", "0.24", "1e9", "8.5", "abc", "1.234567", "1.01", "2.001"):
            code, err = self.run_cli("render", str(POLLING), "--format", "drawio", "--scale", bad)
            self.assertEqual(code, 2, bad)
            self.assertIn("--scale", err)
        for good in ("0.25", "0.3", "1.5", "7.95", "8"):
            self.assertEqual(self.run_cli("render", str(POLLING), "--format", "drawio", "--scale", good)[0], 0, good)

    def test_every_scale_the_cli_accepts_is_read_back_exactly_from_every_editor_file(self):
        """A scale with more digits than the page width keeps would be recovered as another number, and `check` would call a fresh file stale."""
        small = load("small.json")
        makers = {".drawio": drawio.diagram, ".excalidraw": excalidraw.board, "-moda.xml": moda.markup}
        for step in range(5, 161):                                 # 0.25 to 8 in steps of 0.05
            scale = cli.scale_argument(str(step / 20))
            self.assertEqual(scale, step / 20)
            for suffix, make in makers.items():
                self.assertEqual(cli.stored_scale(suffix, make(small, scale)), scale, (suffix, scale))

    def test_a_file_that_cannot_be_written_is_a_sentence_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            blocker = Path(tmp) / "file"
            blocker.write_text("x", encoding="utf-8")
            code, err = self.run_cli("render", str(POLLING), "--out", str(blocker / "inside" / "f.svg"))
        self.assertEqual(code, 2)
        self.assertIn("cannot read or write a file", err)

    def test_only_a_missing_browser_gets_the_install_hint_and_a_real_bug_surfaces(self):
        with tempfile.TemporaryDirectory() as tmp:                 # every output goes under a folder the test owns: a path like /nonexistent-dir cannot be made by a user who is not root
            with mock.patch.object(browser, "png", side_effect=browser.Unavailable("no chromium")):
                code, err = self.run_cli("preview", str(POLLING), "--out", str(Path(tmp) / "preview" / "p.png"))
                self.assertEqual(code, 2)
                self.assertIn("playwright install chromium", err)
                code, err = self.run_cli("facebook", str(FIXTURES / "small.json"), "--out", str(Path(tmp) / "fb-unavailable"))
                self.assertEqual(code, 2)
                self.assertIn("playwright install chromium", err)
            with mock.patch.object(browser, "png", side_effect=RuntimeError("a bug")):
                with self.assertRaises(RuntimeError):
                    self.run_cli("preview", str(POLLING), "--out", str(Path(tmp) / "bug.png"))

    def test_a_browser_that_does_not_start_is_reported_as_unavailable(self):
        class Chromium:
            def launch(self):
                raise RuntimeError("Executable doesn't exist at /nowhere\nlong playwright banner")

        class Playwright:
            chromium = Chromium()
        with self.assertRaises(browser.Unavailable) as caught:
            browser._page(Playwright(), "<svg/>", 10, 10)
        self.assertEqual(str(caught.exception), "Executable doesn't exist at /nowhere")

    def fake_playwright(self, fail: str | None):
        """A Playwright whose browser starts and then fails at the step `fail` ('start', 'new_page', 'content', 'evaluate', 'screenshot'): the
        function standing for `sync_playwright` and the list that gets an entry each time the browser is closed."""
        from playwright.sync_api import Error, TimeoutError as PlaywrightTimeout
        closed: list[bool] = []

        class Page:
            def set_content(self, html):
                if fail == "content":
                    raise Error("Page.set_content: Target crashed\nCall log:\n  - a long banner")

            def evaluate(self, expression):
                if fail == "evaluate":
                    raise Error("Page.evaluate: Execution context was destroyed\nCall log:\n  - a long banner")
                return []

            def screenshot(self):                              # no path: the bytes come back and the caller writes them
                if fail == "screenshot":
                    raise PlaywrightTimeout("Page.screenshot: Timeout 30000ms exceeded.\nCall log:\n  - a long banner")
                if fail == "bug":
                    raise RuntimeError("a bug in our code")
                return FAKE_PNG

        class Browser:
            def new_page(self, **options):
                if fail == "new_page":
                    raise Error("Browser.new_page: Target page, context or browser has been closed")
                return Page()

            def close(self):
                closed.append(True)

        class Playwright:
            class chromium:
                launch = staticmethod(lambda: Browser())

        class Started:
            def __enter__(self):
                if fail == "start":
                    raise Error("the Playwright driver did not start\nCall log:\n  - a long banner")
                return Playwright()

            def __exit__(self, *exc):
                return False
        return (lambda: Started()), closed

    def test_a_playwright_error_after_the_browser_started_is_a_failure_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            for fail in ("start", "new_page", "content", "screenshot"):
                sync_playwright, closed = self.fake_playwright(fail)
                with mock.patch.object(browser, "_playwright", return_value=sync_playwright):
                    with self.assertRaises(browser.Failed, msg=fail) as caught:
                        browser.png("<svg/>", Path(tmp) / "x.png", 10, 10)
                self.assertNotIn("\n", str(caught.exception), fail)               # the first line of Playwright's banner, not all of it
                self.assertEqual(len(closed), 0 if fail == "start" else 1, fail)  # a browser that started is never left running
            sync_playwright, closed = self.fake_playwright("evaluate")
            with mock.patch.object(browser, "_playwright", return_value=sync_playwright), self.assertRaises(browser.Failed):
                browser.measure(load())
            self.assertEqual(len(closed), 1)
            sync_playwright, closed = self.fake_playwright("bug")
            with mock.patch.object(browser, "_playwright", return_value=sync_playwright), self.assertRaises(RuntimeError) as caught:
                browser.png("<svg/>", Path(tmp) / "x.png", 10, 10)
            self.assertNotIsInstance(caught.exception, browser.Unavailable)           # a bug of ours is not blamed on the browser
            self.assertEqual(len(closed), 1)

    def test_a_browser_that_fails_while_drawing_exits_2_and_is_not_told_to_reinstall(self):
        failed = browser.Failed("Page.screenshot: Timeout 30000ms exceeded.")
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(browser, "png", side_effect=failed):
                runs = [self.run_cli("preview", str(POLLING), "--out", str(Path(tmp) / "p.png")),
                        self.run_cli("facebook", str(FIXTURES / "small.json"), "--out", str(Path(tmp) / "fb"))]
            with mock.patch.object(browser, "measure", side_effect=failed):
                runs.append(self.run_cli("check", "--browser", str(POLLING)))
        for code, err in runs:
            self.assertEqual(code, 2, err)
            self.assertIn("Timeout 30000ms", err)
            self.assertNotIn("playwright install chromium", err)

    def test_the_text_check_without_a_browser_says_so(self):
        with mock.patch.object(browser, "measure", side_effect=browser.Unavailable("no chromium")):
            code, err = self.run_cli("check", "--browser", str(POLLING))
        self.assertEqual(code, 2)
        self.assertIn("cannot measure the text", err)

    def test_check_with_a_structurally_broken_icon_file_reports_it_instead_of_raising(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "icons"
            shutil.copytree(icons.HERE, folder, ignore=shutil.ignore_patterns("__pycache__"))
            (folder / "server.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><script>x</script></svg>', encoding="utf-8")
            self.addCleanup(icons.shapes.cache_clear)
            self.addCleanup(icons.index.cache_clear)
            with mock.patch.object(icons, "HERE", folder):
                icons.shapes.cache_clear()
                icons.index.cache_clear()
                code, err = self.run_cli("check", str(POLLING))
        self.assertEqual(code, 1)
        self.assertIn("icons: ", err)
        self.assertIn("server", err)

    def test_two_specs_for_one_figure_are_refused_before_anything_is_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "system-design-101"
            (store / "vi" / "lessons" / "sd-01-001").mkdir(parents=True)
            (store / "vi" / "diagrams").mkdir(parents=True)
            first = load()
            first["id"] = "sd-01-001"
            second = dict(first, title="A different figure")
            paths = []
            for name, data in (("a.json", first), ("b.json", second)):
                (Path(tmp) / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                paths.append(str(Path(tmp) / name))
            with mock.patch.multiple(cli, ROOT=Path(tmp), DIAGRAMS=store / "vi" / "diagrams", LESSONS=store / "vi" / "lessons"):
                code, err = self.run_cli("build", *paths)
                self.assertEqual(code, 1)
                self.assertIn("the id is used by two specs", err)
                self.assertFalse(list((store / "vi" / "diagrams").iterdir()))
                code, err = self.run_cli("check", *paths)
                self.assertEqual(code, 1)
                self.assertIn("the id is used by two specs", err)

    def test_editor_files_are_looked_for_beside_the_spec_that_was_given(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "demo-polling.json").write_text(POLLING.read_text(encoding="utf-8"), encoding="utf-8")
            beside = folder / "demo-polling.drawio"
            beside.write_text("<mxfile/>", encoding="utf-8")
            code, err = self.run_cli("check", str(folder / "demo-polling.json"))
            self.assertEqual(code, 1)
            self.assertIn(f"{beside} is not what the spec draws; render it again", err)
            beside.write_text(drawio.diagram(load()), encoding="utf-8")
            self.assertNotIn("render it again", self.run_cli("check", str(folder / "demo-polling.json"))[1])

    def test_no_command_draws_from_a_broken_icon_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "icons"
            shutil.copytree(icons.HERE, folder, ignore=shutil.ignore_patterns("__pycache__"))
            (folder / "server.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><script>x</script></svg>', encoding="utf-8")
            self.addCleanup(icons.shapes.cache_clear)
            self.addCleanup(icons.index.cache_clear)
            with mock.patch.object(icons, "HERE", folder):
                icons.shapes.cache_clear()
                icons.index.cache_clear()
                for argv in (["render", str(POLLING), "--format", "svg"], ["render", str(POLLING), "--format", "drawio"], ["render", str(POLLING), "--format", "moda"],
                             ["preview", str(POLLING), "--out", str(Path(tmp) / "p.png")], ["facebook", str(FIXTURES / "small.json"), "--out", str(Path(tmp) / "fb")],
                             ["build", str(POLLING)], ["check", str(POLLING)]):
                    code, err = self.run_cli(*argv)
                    self.assertEqual(code, 1, argv)
                    self.assertIn("icons: ", err, argv)

    def test_editor_files_kept_at_another_scale_pass_the_check_and_a_stale_one_does_not(self):
        makers = {".drawio": drawio.diagram, ".excalidraw": excalidraw.board, "-moda.xml": moda.markup}
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "demo-polling.json").write_text(POLLING.read_text(encoding="utf-8"), encoding="utf-8")
            target = str(folder / "demo-polling.json")
            for suffix, make in makers.items():
                beside = folder / f"demo-polling{suffix}"
                for scale in (0.5, 1, 1.25, 3, 7.95, 8):
                    beside.write_text(make(load(), scale), encoding="utf-8")
                    self.assertNotIn("render it again", self.run_cli("check", target)[1], (suffix, scale))
                beside.write_text(make(load(), 3).replace("Trình duyệt", "Trinh duyet", 1), encoding="utf-8")
                self.assertIn("render it again", self.run_cli("check", target)[1], suffix)
                beside.write_text("not an editor file", encoding="utf-8")
                self.assertIn("render it again", self.run_cli("check", target)[1], suffix)
                beside.unlink()

    def test_a_scale_for_svg_output_is_refused_not_ignored(self):
        for argv in (("--format", "svg", "--scale", "2"), ("--scale", "2")):              # svg is also the default format
            code, err = self.run_cli("render", str(POLLING), *argv)
            self.assertEqual(code, 2, argv)
            self.assertIn("--scale", err)
            self.assertIn("editor formats", err)
        for fmt in ("drawio", "excalidraw", "moda"):
            self.assertEqual(self.run_cli("render", str(POLLING), "--format", fmt, "--scale", "2")[0], 0, fmt)
        self.assertEqual(self.run_cli("render", str(POLLING), "--format", "svg")[0], 0)

    def test_an_editor_file_that_cannot_be_read_is_stale_not_a_traceback(self):
        deep = "[" * 100000 + "]" * 100000
        huge = json.dumps({"elements": [{"type": "rectangle", "width": 10 ** 400}]})
        hostile = {".excalidraw": (deep, huge, "[]", "{}", '{"elements": [1]}', '{"elements": [{"type": "rectangle", "width": "wide"}]}'),
                   ".drawio": ('pageWidth="' + "9" * 400 + '"', 'pageWidth="1.2.3"', "pageWidth="),
                   "-moda.xml": ("Moda canvas " + "9" * 400 + "x", "Moda canvas 1.2.3x", "Moda canvas")}
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "demo-polling.json").write_text(POLLING.read_text(encoding="utf-8"), encoding="utf-8")
            for suffix, texts in hostile.items():
                for content in texts:
                    self.assertIsNone(cli.stored_scale(suffix, content), (suffix, content[:40]))
                    (folder / f"demo-polling{suffix}").write_text(content, encoding="utf-8")
                    code, err = self.run_cli("check", str(folder / "demo-polling.json"))
                    self.assertEqual(code, 1, (suffix, content[:40]))
                    self.assertIn("render it again", err)
                (folder / f"demo-polling{suffix}").unlink()

    def test_a_write_that_fails_half_way_leaves_the_previous_file_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "figure.svg"
            target.write_text("old valid figure", encoding="utf-8")
            with mock.patch.object(Path, "write_bytes", half_write):
                with self.assertRaises(OSError):
                    cli._write(target, "<svg>new</svg>" * 50)
                code, err = self.run_cli("render", str(POLLING), "--out", str(target))
            self.assertEqual(code, 2)
            self.assertIn("cannot read or write a file", err)
            self.assertEqual(target.read_text(encoding="utf-8"), "old valid figure")
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ["figure.svg"])        # and no half-written temporary file
            self.assertTrue(cli._write(target, "new\n"))                                       # a write that works replaces it in full
            self.assertFalse(cli._write(target, "new\n"))
            self.assertEqual((target.read_bytes(), sorted(p.name for p in Path(tmp).iterdir())), (b"new\n", ["figure.svg"]))

    def test_a_screenshot_that_cannot_be_written_leaves_the_previous_preview_whole(self):
        sync_playwright, closed = self.fake_playwright(None)
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(browser, "_playwright", return_value=sync_playwright):
            target = Path(tmp) / "preview.png"
            target.write_bytes(b"old preview")
            with mock.patch.object(Path, "write_bytes", half_write):
                with self.assertRaises(OSError):
                    browser.png("<svg/>", target, 10, 10)
            self.assertEqual(target.read_bytes(), b"old preview")                              # not truncated, not partly replaced
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ["preview.png"])     # and no half-written file beside it
            self.assertEqual(len(closed), 1)
            browser.png("<svg/>", target, 10, 10)
            self.assertEqual((target.read_bytes(), sorted(p.name for p in Path(tmp).iterdir())), (FAKE_PNG, ["preview.png"]))

    def test_check_refuses_a_footer_handle_that_the_export_would_refuse(self):
        with mock.patch.object(facebook, "handle", return_value="fb.com/your-page"):
            code, err = self.run_cli("check", str(POLLING), str(FIXTURES / "small.json"))
        self.assertEqual(code, 1)
        self.assertEqual(err.count("author.handle"), 1, err)                                   # said once, not once per figure
        self.assertIn("is an address", err)
        with mock.patch.object(facebook, "handle", return_value="@your-page"):
            self.assertNotIn("author.handle", self.run_cli("check", str(POLLING), str(FIXTURES / "small.json"))[1])

    def test_build_refuses_a_spec_that_is_its_own_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "system-design-101"
            (store / "vi" / "lessons" / "sd-01-001").mkdir(parents=True)
            (store / "figures" / "vi").mkdir(parents=True)
            diagrams = store / "vi" / "diagrams"
            diagrams.mkdir(parents=True)
            data = load()
            data["id"] = "sd-01-001"
            dest = diagrams / "sd-01-001-main.svg"
            dest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            paths = [dest]
            try:
                os.link(dest, Path(tmp) / "hard.json")
                paths.append(Path(tmp) / "hard.json")
            except OSError:
                pass
            before = dest.read_bytes()
            for path in paths:
                with mock.patch.multiple(cli, ROOT=Path(tmp), DIAGRAMS=diagrams, LESSONS=store / "vi" / "lessons", SPEC_DIR=store / "figures" / "vi"):
                    code, err = self.run_cli("build", str(path))
                self.assertEqual(code, 1, (path, err))
                self.assertIn("own output file", err)
                self.assertEqual(dest.read_bytes(), before, path)
            spec_path = store / "figures" / "vi" / "sd-01-001.json"                              # the spec in its place still builds
            spec_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            dest.unlink()
            with mock.patch.multiple(cli, ROOT=Path(tmp), DIAGRAMS=diagrams, LESSONS=store / "vi" / "lessons", SPEC_DIR=store / "figures" / "vi"):
                self.assertEqual(self.run_cli("build", str(spec_path))[0], 0)
            self.assertTrue(dest.read_text(encoding="utf-8").startswith("<svg"))

    def test_a_write_goes_through_a_link_as_it_always_did(self):
        with tempfile.TemporaryDirectory() as tmp:
            real, link = Path(tmp) / "real.svg", Path(tmp) / "link.svg"
            real.write_text("old", encoding="utf-8")
            try:
                link.symlink_to(real)
            except OSError:
                self.skipTest("no symbolic links here")
            self.assertTrue(cli._write(link, "new"))
            self.assertTrue(link.is_symlink())
            self.assertEqual(real.read_text(encoding="utf-8"), "new")

    def test_an_output_that_is_the_spec_is_refused_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            spec_path = folder / "demo-polling.json"
            spec_path.write_text(POLLING.read_text(encoding="utf-8"), encoding="utf-8")
            before = spec_path.read_bytes()
            aliases = [str(spec_path), str(folder / "." / "demo-polling.json"), str(folder / "sub" / ".." / "demo-polling.json")]
            link, hard = folder / "link.json", folder / "hard.json"
            try:
                link.symlink_to(spec_path)
                os.link(spec_path, hard)
                aliases += [str(link), str(hard)]
            except OSError:
                pass
            (folder / "sub").mkdir()
            for alias in aliases:
                for argv in (("render", str(spec_path), "--out", alias), ("render", str(spec_path), "--format", "drawio", "--out", alias),
                             ("preview", str(spec_path), "--out", alias)):
                    code, err = self.run_cli(*argv)
                    self.assertEqual(code, 2, (argv, err))
                    self.assertIn("is the spec itself", err)
                    self.assertEqual(spec_path.read_bytes(), before, argv)
            self.assertEqual(self.run_cli("render", str(spec_path), "--out", str(folder / "other.svg"))[0], 0)       # another file is fine
            self.assertEqual(spec_path.read_bytes(), before)

    def test_a_tampered_icon_set_never_overwrites_a_stored_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "system-design-101"
            (store / "vi" / "lessons" / "sd-01-001").mkdir(parents=True)
            (store / "vi" / "diagrams").mkdir(parents=True)
            figure = store / "vi" / "diagrams" / "sd-01-001-main.svg"
            figure.write_text("old figure", encoding="utf-8")
            data = load()
            data["id"] = "sd-01-001"
            spec_path = Path(tmp) / "sd-01-001.json"
            spec_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with mock.patch.multiple(cli, ROOT=Path(tmp), DIAGRAMS=store / "vi" / "diagrams", LESSONS=store / "vi" / "lessons"), \
                    mock.patch.object(icons, "verify", return_value=["server.svg differs from the hash in index.json"]):
                code, err = self.run_cli("build", str(spec_path))
            self.assertEqual(code, 1)
            self.assertIn("server.svg differs", err)
            self.assertEqual(figure.read_text(encoding="utf-8"), "old figure")

    def test_a_tampered_icon_set_stops_a_build_and_an_export_before_anything_is_written(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(icons, "verify", return_value=["server.svg differs from the hash in index.json"]):
            out = Path(tmp) / "fb"
            code, err = self.run_cli("facebook", str(FIXTURES / "small.json"), "--out", str(out))
            self.assertEqual(code, 1)
            self.assertIn("server.svg differs", err)
            self.assertFalse(out.exists())
            code, err = self.run_cli("build", str(POLLING))
            self.assertEqual(code, 1)
            self.assertIn("server.svg differs", err)

    def test_an_alt_text_that_cannot_be_encoded_fails_before_a_stale_slide_is_deleted(self):
        data = load("small.json")
        data["desc"] = "A description that holds a lone surrogate \ud800 on purpose, so the text file cannot be written."
        with tempfile.TemporaryDirectory() as tmp:
            stale = Path(tmp) / "demo-small" / "09.png"
            stale.parent.mkdir()
            stale.write_bytes(b"old")
            with mock.patch.object(browser, "png") as draw, self.assertRaises(UnicodeEncodeError):
                facebook.export(data, Path(tmp), ROOT)
            draw.assert_not_called()                           # it fails before the first slide is drawn
            self.assertTrue(stale.exists())


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        store = self.tmp / "system-design-101"
        (store / "vi" / "lessons" / "sd-01-001").mkdir(parents=True)
        (store / "figures" / "vi").mkdir(parents=True)
        (store / "vi" / "diagrams").mkdir(parents=True)
        for name, value in (("ROOT", self.tmp), ("STORE", store), ("SPEC_DIR", store / "figures" / "vi"), ("DIAGRAMS", store / "vi" / "diagrams"),
                            ("LESSONS", store / "vi" / "lessons")):
            patcher = mock.patch.object(cli, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        data = load()
        data["id"] = "sd-01-001"
        self.spec_path = store / "figures" / "vi" / "sd-01-001.json"
        self.spec_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        self.figure = store / "vi" / "diagrams" / "sd-01-001-main.svg"

    def run_cli(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_build_writes_the_figure_and_check_then_passes(self):
        self.assertEqual(self.run_cli("check")[0], 1)
        code, out, err = self.run_cli("build")
        self.assertEqual((code, err), (0, ""), out)
        self.assertIn("wrote", out)
        self.assertIsNone(sd101_check.svg_problem(self.figure))
        self.assertEqual(self.run_cli("build")[1].count("unchanged"), 1)
        self.assertEqual(self.run_cli("check")[0], 0)

    def test_a_figure_that_is_not_what_the_spec_draws_fails_the_check(self):
        self.run_cli("build")
        self.figure.write_text(self.figure.read_text(encoding="utf-8").replace("Trình duyệt", "Trinh duyet"), encoding="utf-8")
        code, _, err = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("is not what the spec draws", err)

    def test_an_editor_file_beside_the_spec_must_not_go_stale(self):
        self.run_cli("build")
        beside = self.spec_path.with_suffix(".drawio")
        beside.write_text("<mxfile/>", encoding="utf-8")
        self.assertIn("render it again", self.run_cli("check")[2])
        beside.write_text(drawio.diagram(json.loads(self.spec_path.read_text(encoding="utf-8"))), encoding="utf-8")
        self.assertEqual(self.run_cli("check")[0], 0)

    def test_build_refuses_a_spec_without_a_lesson_and_an_invalid_spec(self):
        data = json.loads(self.spec_path.read_text(encoding="utf-8"))
        data["id"] = "sd-09-999"
        other = self.spec_path.with_name("sd-09-999.json")
        other.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        code, _, err = self.run_cli("build", str(other))
        self.assertEqual(code, 1)
        self.assertIn("no lesson of that id", err)
        self.assertFalse((self.figure.parent / "sd-09-999-main.svg").exists())
        data["sections"] = []
        other.write_text(json.dumps(data), encoding="utf-8")
        self.assertIn("sections must be a list", self.run_cli("build", str(other))[2])

    def test_a_figure_with_text_too_small_for_a_phone_is_never_written(self):
        with mock.patch.object(svg, "STYLE", scene.Style(name=12, role=11)):
            code, _, err = self.run_cli("build")
        self.assertEqual(code, 1)
        self.assertIn("px on a", err)
        self.assertFalse(self.figure.exists())

    def test_render_prints_or_writes_each_format_and_icons_lists_the_set(self):
        for fmt, head in (("svg", "<svg"), ("drawio", "<mxfile"), ("excalidraw", '{"type":"excalidraw"'), ("moda", "<!-- figure")):
            code, out, _ = self.run_cli("render", str(POLLING), "--format", fmt)
            self.assertEqual(code, 0)
            self.assertTrue(out.startswith(head), fmt)
        target = self.tmp / "o.drawio"
        self.assertEqual(self.run_cli("render", str(POLLING), "--format", "drawio", "--scale", "1", "--out", str(target))[0], 0)
        self.assertIn('pageWidth="320"', target.read_text(encoding="utf-8"))
        code, out, _ = self.run_cli("icons")
        self.assertEqual(code, 0)
        self.assertIn("server = ", out)
        self.assertEqual(self.run_cli("icons", "--verify")[0], 0)

    def test_the_real_store_has_no_figure_that_is_stale(self):
        with mock.patch.multiple(cli, ROOT=ROOT, STORE=ROOT / "system-design-101", SPEC_DIR=ROOT / "system-design-101" / "figures" / "vi",
                                 DIAGRAMS=ROOT / "system-design-101" / "vi" / "diagrams", LESSONS=ROOT / "system-design-101" / "vi" / "lessons"):
            self.assertEqual(self.run_cli("check")[0], 0)


if __name__ == "__main__":
    unittest.main()
