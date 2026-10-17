"""scripts/figures: the figure spec, the closed icon set, the layout, and the four writers (SVG for the lessons, draw.io, Excalidraw, Moda)."""

from __future__ import annotations

import base64
import contextlib
import copy
import io
import json
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
        for bad in ("see https://example.test/x", "go to www.example.test", "from assets.bytebytego.com"):
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

    def test_a_language_outside_the_three_is_refused(self):
        self.assertTrue(any("lang" in p for p in self.problems_after(lambda d: d.update(lang="fr"))))

    def test_a_json_file_that_names_a_key_twice_or_is_not_json_is_an_error_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, body in (("twice.json", '{"id": "a-b", "id": "c-d"}'), ("junk.json", "{nope"), ("list.json", "[]"), ("deep.json", "[" * 50000)):
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
        self.assertTrue(any("control character" in p for p in found), found)
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
        with tempfile.TemporaryDirectory() as tmp:
            files, problems = facebook.export(too_tall(), Path(tmp), ROOT)
            self.assertEqual(files, [])
            self.assertTrue(problems)
            self.assertFalse((Path(tmp) / "t-parts").exists())

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
