"""The deck brief copies what a lesson says onto the slide roles of docs/sd101-slides.md and invents nothing."""
import dataclasses
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

from scripts import sd101_slide_brief as brief
from scripts import sd101_slides

ROOT = pathlib.Path(__file__).resolve().parents[1]
STORE = ROOT / "system-design-101" / "vi"

TAIL = """
## Giới hạn cần nhớ

Hình không bao quát mọi trường hợp.

## Nhìn hình thử trả lời

Máy nào nhận phản hồi?

<details>
<summary>Xem đáp án</summary>

Máy B.

</details>

<details>
<summary>Xem sâu hơn</summary>

- Một ý sâu hơn, xem [RFC 3022](https://example.org/rfc3022).
- Ý thứ hai.

</details>

## Nguồn đối chiếu

- [RFC 3022](https://example.org/rfc3022): đối chiếu.
- [Tài liệu thứ hai](https://example.org/two): đối chiếu.
"""
GLOSSARY = """
## Từ viết tắt

- **NAT** (Network Address Translation) — dịch địa chỉ mạng: router đổi địa chỉ khi gói đi qua.
- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ.
"""


def lesson_text(body: str, glossary: bool = True) -> str:
    return "# Tiêu đề thử\n\nMột câu mở đầu.\n\n![Mô tả hình](../../diagrams/sd-01-900-main.svg)\n" + body + \
        (GLOSSARY if glossary else "") + TAIL


def figure_section(bullets: int) -> str:
    items = "\n".join(f"- **Ý {n}:** nội dung của ý {n} trong bài." for n in range(1, bullets + 1))
    return f"\n## Đọc hình\n\nVí dụ một cửa hàng.\n\n{items}\n"


def bold_section(paragraphs: int) -> str:
    items = "\n\n".join(f"**{n} · Chặng {n}.** nội dung chặng {n}." for n in range(1, paragraphs + 1))
    return f"\n## Đọc hình\n\nMở đầu của phần đọc hình.\n\n{items}\n"


SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
<text x="16" y="30" font-size="20" font-weight="bold">TIÊU ĐỀ HÌNH</text>
<text x="16" y="58" font-size="16" font-weight="normal">Phụ đề của hình</text>
<text x="30" y="100" font-size="16" font-weight="bold">1 · Thẻ</text><text x="30" y="124" font-size="16" font-weight="bold">thứ nhất</text>
<text x="30" y="150" font-size="16" font-weight="normal">Dòng một</text><text x="30" y="174" font-size="16" font-weight="normal">dòng hai</text>
<text x="30" y="250" font-size="16" font-weight="bold">2 · Thẻ hai</text>
<text x="30" y="280" font-size="16" font-weight="normal">Chỉ một dòng</text>
<text x="30" y="330" font-size="16" font-weight="bold">3 · Thẻ ba</text>
<text x="30" y="360" font-size="16" font-weight="normal"><tspan>Có</tspan><tspan> tspan</tspan></text>
</svg>"""


def strings(value):
    """Every string inside nested dicts and lists."""
    if isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, str):
        yield value


class Store:
    """A throwaway lesson store holding one lesson."""

    def __init__(self, text: str, svg: str | None = None, lesson_id: str = "sd-01-900") -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.tmp.name)
        self.lesson_id = lesson_id
        lesson = self.path / "lessons" / lesson_id
        lesson.mkdir(parents=True)
        (lesson / "lesson.md").write_text(text, encoding="utf-8")
        if svg is not None:
            (self.path / "diagrams").mkdir()
            (self.path / "diagrams" / f"{lesson_id}-main.svg").write_text(svg, encoding="utf-8")

    def build(self) -> brief.Brief:
        return brief.build(self.path, self.lesson_id)


class StructureTests(unittest.TestCase):
    def build(self, text: str, svg: str | None = None) -> tuple[brief.Brief, Store]:
        store = Store(text, svg)
        self.addCleanup(store.tmp.cleanup)
        return store.build(), store

    def test_bullets_under_the_figure_section_become_one_slide_each(self):
        result, _ = self.build(lesson_text(figure_section(3)))
        self.assertEqual(9, result.slide_count)
        self.assertEqual(["cover", "situation and goal", "concept 1 of 3", "concept 2 of 3", "concept 3 of 3",
                          "choice or summary", "check question and answer", "deep dive", "terms and sources"],
                         [slide["role"] for slide in result.slides])
        labels = [slide["material"]["concepts"][0]["label"] for slide in result.slides[2:5]]
        self.assertEqual(["Ý 1", "Ý 2", "Ý 3"], labels)
        self.assertEqual("bullets under `Đọc hình`", result.concept_source)
        self.assertEqual("System Design 101 · Bài 900 · Tiêu đề thử (sd-01-900)", result.canvas_name)

    def test_more_concepts_than_slides_are_grouped_in_order_without_loss(self):
        self.assertEqual([2, 2, 1, 1], brief.group_sizes(6, 4))
        self.assertEqual([2, 1, 1, 1], brief.group_sizes(5, 4))
        self.assertEqual([1, 1], brief.group_sizes(2, 2))
        result, _ = self.build(lesson_text(figure_section(6)))
        self.assertEqual(10, result.slide_count)
        grouped = [c["label"] for slide in result.slides[2:6] for c in slide["material"]["concepts"]]
        self.assertEqual([f"Ý {n}" for n in range(1, 7)], grouped)
        self.assertEqual(["blue", "amber", "teal", "red"], [slide["material"]["colour"] for slide in result.slides[2:6]])

    def test_one_colour_per_concept_slide_with_both_shades(self):
        result, _ = self.build(lesson_text(figure_section(4)))
        self.assertEqual([("blue", "#1F3FD1", "#7C93FF"), ("amber", "#B45309", "#FFB454"),
                          ("teal", "#0F766E", "#3DD6A0"), ("red", "#E8472B", "#FF6A4D")],
                         [(c["name"], c["on_cream"], c["on_dark"]) for c in result.colours])

    def test_bold_label_paragraphs_are_the_concepts_and_plain_ones_the_situation(self):
        result, _ = self.build(lesson_text(bold_section(3)))
        self.assertEqual("bold-label paragraphs under `Đọc hình`", result.concept_source)
        self.assertEqual("1 · Chặng 1", result.slides[2]["material"]["concepts"][0]["label"])
        situation = [item["text"] for item in result.slides[1]["material"]["lines"]]
        self.assertIn("Mở đầu của phần đọc hình.", situation)

    def test_lessons_without_a_figure_section_fall_back_to_the_figure_cards(self):
        result, _ = self.build(lesson_text(""), SVG)
        self.assertEqual("text cards of the figure (the lesson's SVG)", result.concept_source)
        cards = [slide["material"]["concepts"] for slide in result.slides[2:5]]
        self.assertEqual("1 · Thẻ thứ nhất", cards[0][0]["label"])
        self.assertEqual("Dòng một dòng hai", cards[0][0]["line"]["text"])
        self.assertEqual("Có tspan", cards[2][0]["line"]["text"])
        every_text = json.dumps(result.slides, ensure_ascii=False)
        self.assertNotIn("TIÊU ĐỀ HÌNH", every_text)  # the figure's own title and subtitle are not concepts
        self.assertNotIn("Phụ đề của hình", every_text)

    def test_a_lesson_with_no_concepts_anywhere_warns_and_still_fits_the_slide_range(self):
        result, _ = self.build(lesson_text(""))
        self.assertEqual("nowhere", result.concept_source)
        self.assertTrue(any("concept line" in warning for warning in result.warnings))
        self.assertIn(result.slide_count, brief.SLIDE_COUNTS)

    def test_check_question_answer_deep_dive_terms_and_sources(self):
        result, _ = self.build(lesson_text(figure_section(3)))
        by_role = {slide["role"]: slide["material"] for slide in result.slides}
        self.assertEqual("Máy nào nhận phản hồi?", by_role["check question and answer"]["question"][0]["text"])
        self.assertEqual("Máy B.", by_role["check question and answer"]["answer"][0]["text"])
        self.assertEqual(["Một ý sâu hơn, xem RFC 3022.", "Ý thứ hai."], [i["text"] for i in by_role["deep dive"]["lines"]])
        closing = by_role["terms and sources"]
        self.assertEqual(["NAT", "IP"], [t["abbreviation"] for t in closing["terms"]])
        self.assertEqual("dịch địa chỉ mạng", closing["terms"][0]["short_meaning"])
        self.assertEqual(["RFC 3022", "Tài liệu thứ hai"], closing["sources"])
        self.assertEqual("Hình không bao quát mọi trường hợp.",
                         by_role["choice or summary"]["sections"][0]["lines"][0]["text"])

    def test_no_address_reaches_a_slide(self):
        result, _ = self.build(lesson_text(figure_section(3)))
        self.assertNotIn("http", json.dumps(result.slides, ensure_ascii=False))

    def test_a_typed_address_is_hidden_wherever_it_is_typed_and_the_session_is_told(self):
        address = "https://shop.example:8443/items/42?view=compact#details"
        text = lesson_text(figure_section(3)).replace("nội dung của ý 1 trong bài.", f"mở {address} rồi đọc.") \
            .replace("Mô tả hình", f"Địa chỉ {address} chia thành phần").replace("Máy nào nhận phản hồi?", f"Với {address}, máy nào?")
        result, _ = self.build(text)
        every = json.dumps([result.slides, result.figure_alt], ensure_ascii=False)
        self.assertNotIn("://", every)
        self.assertIn("mở [address] rồi đọc.", every)
        self.assertTrue(any("types an address" in warning for warning in result.warnings), result.warnings)

    def test_an_address_typed_in_the_figure_is_hidden_too(self):
        svg = SVG.replace("Chỉ một dòng", "xem http://a.example/x")
        result, _ = self.build(lesson_text(""), svg)
        every = json.dumps(result.slides, ensure_ascii=False)
        self.assertNotIn("://", every)
        self.assertIn("xem [address]", every)

    def test_a_lesson_without_a_typed_address_gets_no_address_warning(self):
        result, _ = self.build(lesson_text(figure_section(3)))
        self.assertFalse([w for w in result.warnings if "address" in w], result.warnings)

    def test_the_prose_of_the_figure_section_stays_off_the_situation_slide_when_the_cards_are_the_concepts(self):
        prose = "Đoạn giải thích dài của phần đọc hình, nói lại từng thẻ."
        result, _ = self.build(lesson_text(f"\n## Đọc hình\n\n{prose}\n\nĐoạn thứ hai của phần đọc hình.\n"), SVG)
        self.assertEqual("text cards of the figure (the lesson's SVG)", result.concept_source)
        situation = [item["text"] for item in result.slides[1]["material"]["lines"]]
        self.assertEqual([], [text for text in situation if "phần đọc hình" in text])
        self.assertNotIn(prose, json.dumps(result.slides, ensure_ascii=False))
        self.assertTrue(any("left off the situation slide" in warning for warning in result.warnings), result.warnings)

    def test_a_bold_line_inside_a_numbered_card_is_a_line_of_that_card_not_a_new_concept(self):
        callout = '<text x="30" y="200" font-size="16" font-weight="bold">Chọn theo dữ liệu</text>'
        svg = SVG.replace('<text x="30" y="250"', callout + '\n<text x="30" y="250"')
        result, _ = self.build(lesson_text(""), svg)
        concepts = [c for slide in result.slides if "concepts" in slide["material"] for c in slide["material"]["concepts"]]
        self.assertEqual(["1 · Thẻ thứ nhất", "2 · Thẻ hai", "3 · Thẻ ba"], [c["label"] for c in concepts])
        self.assertEqual("Dòng một dòng hai Chọn theo dữ liệu", concepts[0]["line"]["text"])

    def test_a_term_meaning_over_the_word_budget_is_flagged_like_any_other_line(self):
        long_meaning = " ".join(["từ"] * 12)
        text = lesson_text(figure_section(3)).replace(
            "- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ.",
            f"- **IP** (Internet Protocol) — {long_meaning}.")
        result, _ = self.build(text)
        terms = {slide["role"]: slide["material"] for slide in result.slides}["terms and sources"]["terms"]
        self.assertEqual([False, True], [term["over_budget"] for term in terms])
        self.assertEqual(12, terms[1]["words"])
        markdown = brief.render(result)
        self.assertIn("IP = " + long_meaning + ".  [12 words: cut to 10 or fewer]", markdown)
        self.assertNotIn("NAT = dịch địa chỉ mạng  [", markdown)

    def test_italic_marks_go_but_a_sum_with_stars_stays(self):
        self.assertEqual("dùng load balancer và 2 * 3 * 4", brief.clean("dùng *load balancer* và 2 * 3 * 4"))
        self.assertEqual("đậm và nghiêng", brief.clean("**đậm** và *nghiêng*"))

    def test_a_tag_shaped_word_is_plain_text_in_the_json_and_escaped_in_the_markdown(self):
        text = lesson_text(figure_section(3)).replace("nội dung của ý 1 trong bài.", 'thẻ `<p class="note">` trong trang.')
        result, _ = self.build(text)
        self.assertEqual('thẻ <p class="note"> trong trang.', result.slides[2]["material"]["concepts"][0]["line"]["text"])
        markdown = brief.render(result)
        self.assertIn('thẻ \\<p class="note"> trong trang.', markdown)
        self.assertNotIn('thẻ <p class="note">', markdown)

    def test_code_blocks_and_tables_are_left_out_of_the_slide_lines_and_the_session_is_told(self):
        text = lesson_text(figure_section(3)).replace(
            "- Ý thứ hai.", "- Ý thứ hai.\n\n```python\nimport socket\nprint('x')\n```\n\n| Cột | Giá trị |\n|---|---|\n| a | 1 |")
        result, _ = self.build(text)
        every = json.dumps(result.slides, ensure_ascii=False)
        for leaked in ("import socket", "print('x')", "| Cột", "|---|"):
            self.assertNotIn(leaked, every)
        deep = {slide["role"]: slide["material"] for slide in result.slides}["deep dive"]["lines"]
        self.assertEqual(["Một ý sâu hơn, xem RFC 3022.", "Ý thứ hai."], [item["text"] for item in deep])
        self.assertTrue(any("code block or table" in warning for warning in result.warnings), result.warnings)

    def test_a_lesson_without_code_or_tables_gets_no_such_warning(self):
        result, _ = self.build(lesson_text(figure_section(3)))
        self.assertFalse([w for w in result.warnings if "code block or table" in w], result.warnings)

    def test_the_figure_description_is_guidance_in_the_header_not_slide_material(self):
        result, _ = self.build(lesson_text(figure_section(3)))
        self.assertEqual("Mô tả hình", result.figure_alt)
        self.assertNotIn("figure_alt", result.slides[1]["material"])
        self.assertIn("Mô tả hình", brief.render(result))

    def test_a_source_bullet_without_a_link_is_named_by_its_text_up_to_the_first_colon(self):
        long_name = " ".join(f"từ{n}" for n in range(1, 20))
        text = lesson_text(figure_section(3)).replace(
            "- [Tài liệu thứ hai](https://example.org/two): đối chiếu.",
            f"- Phép thử trên một máy: kết quả của một lần chạy.\n- {long_name}.")
        result, _ = self.build(text)
        names = result.slides[-1]["material"]["sources"]
        self.assertEqual(["RFC 3022", "Phép thử trên một máy", " ".join(f"từ{n}" for n in range(1, 13)) + " …"], names)

    def test_only_the_limits_and_choice_sections_feed_the_summary_slide(self):
        text = lesson_text(figure_section(3)).replace(
            "## Giới hạn cần nhớ", "## Một danh mục dài của bài\n\nNội dung rất dài của thân bài.\n\n## Giới hạn cần nhớ")
        result, _ = self.build(text)
        summary = {slide["role"]: slide["material"] for slide in result.slides}["choice or summary"]
        self.assertEqual(["Giới hạn cần nhớ"], [section["name"] for section in summary["sections"]])
        self.assertNotIn("Nội dung rất dài", json.dumps(result.slides, ensure_ascii=False))
        self.assertTrue(any("Một danh mục dài của bài" in warning for warning in result.warnings), result.warnings)

    def test_an_ordered_list_under_the_figure_section_gives_the_concepts_before_the_figure_cards_do(self):
        items = "\n".join(f"{n}. **Ý {n}.** nội dung của ý {n} trong bài." for n in range(1, 4))
        result, _ = self.build(lesson_text(f"\n## Đọc hình\n\nVí dụ một cửa hàng.\n\n{items}\n"), SVG)
        self.assertEqual("bullets under `Đọc hình`", result.concept_source)
        labels = [c["label"] for slide in result.slides if "concepts" in slide["material"]
                  for c in slide["material"]["concepts"]]
        self.assertEqual(["Ý 1", "Ý 2", "Ý 3"], labels)

    def test_the_deep_dive_is_the_details_block_that_is_not_the_answer_whatever_its_summary_says(self):
        for summary in ("Giới hạn và đánh đổi", "Đi sâu: điều kiện của ví dụ", "Xem sâu hơn"):
            with self.subTest(summary=summary):
                text = lesson_text(figure_section(3)).replace("Xem sâu hơn", summary)
                result, _ = self.build(text)
                by_role = {slide["role"]: slide["material"] for slide in result.slides}
                self.assertEqual(["Một ý sâu hơn, xem RFC 3022.", "Ý thứ hai."],
                                 [item["text"] for item in by_role["deep dive"]["lines"]])

    def test_a_lesson_without_a_takeaway_section_gets_a_recap_of_its_concepts_on_the_summary_slide(self):
        text = lesson_text(figure_section(3)).replace("## Giới hạn cần nhớ\n\nHình không bao quát mọi trường hợp.\n", "")
        result, _ = self.build(text)
        summary = {slide["role"]: slide["material"] for slide in result.slides}["choice or summary"]
        self.assertEqual(["Ý 1", "Ý 2", "Ý 3"], [item["text"] for item in summary["sections"][0]["lines"]])
        self.assertTrue(any("only recaps the concepts" in warning for warning in result.warnings), result.warnings)

    def test_the_opening_paragraph_is_cut_into_the_hook_and_the_situation(self):
        cases = {"**Câu mở đầu in đậm.** Phần bối cảnh sau đó.": ("Câu mở đầu in đậm.", "Phần bối cảnh sau đó."),
                 "Câu một. Câu hai và câu ba.": ("Câu một.", "Câu hai và câu ba.")}
        for opening, (hook, situation) in cases.items():
            with self.subTest(opening=opening):
                result, _ = self.build(lesson_text(figure_section(3)).replace("Một câu mở đầu.", opening))
                self.assertEqual(hook, result.slides[0]["material"]["hook"]["text"])
                self.assertEqual(situation, result.slides[1]["material"]["lines"][0]["text"])

    def test_a_lesson_that_says_nothing_after_its_hook_gets_a_situation_from_the_figure_description(self):
        result, _ = self.build(lesson_text(""))  # one sentence, then the figure with alt "Mô tả hình", no Đọc hình
        self.assertEqual(["Mô tả hình"], [item["text"] for item in result.slides[1]["material"]["lines"]])
        self.assertTrue(any("situation slide starts from" in warning for warning in result.warnings), result.warnings)

    def test_every_link_of_a_source_bullet_is_a_source_not_only_the_first(self):
        text = lesson_text(figure_section(3)).replace(
            "- [Tài liệu thứ hai](https://example.org/two): đối chiếu.",
            "- Tiền tố: [Tài liệu hai](https://example.org/two) và [Tài liệu ba](https://example.org/three).")
        result, _ = self.build(text)
        self.assertEqual(["RFC 3022", "Tài liệu hai", "Tài liệu ba"], result.slides[-1]["material"]["sources"])

    def test_a_group_heading_above_the_first_card_is_not_glued_to_the_card_heading(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
<text x="16" y="30" font-size="20" font-weight="bold">TIÊU ĐỀ HÌNH</text>
<text x="16" y="58" font-size="16" font-weight="normal">Phụ đề của hình</text>
<text x="20" y="100" font-size="17" font-weight="bold">Nhóm bốn cách</text><text x="20" y="122" font-size="17" font-weight="bold">chọn một khóa</text>
<text x="78" y="160" font-size="16" font-weight="bold">Chia theo dải</text>
<text x="78" y="190" font-size="16" font-weight="normal">Dòng của thẻ</text>
<text x="78" y="260" font-size="16" font-weight="bold">Băm</text><text x="78" y="284" font-size="16" font-weight="bold">chia dư</text>
<text x="78" y="314" font-size="16" font-weight="normal">Dòng của thẻ hai</text>
</svg>"""
        result, _ = self.build(lesson_text(""), svg)
        concepts = [c for slide in result.slides if "concepts" in slide["material"] for c in slide["material"]["concepts"]]
        # the group heading has no lines of its own; a heading wrapped over two lines is still one heading
        self.assertEqual(["Chia theo dải", "Băm chia dư"], [c["label"] for c in concepts])

    def test_figure_cards_without_numbers_still_open_a_card_at_every_bold_heading(self):
        svg = SVG.replace("1 · ", "").replace("2 · ", "").replace("3 · ", "")
        result, _ = self.build(lesson_text(""), svg)
        concepts = [c for slide in result.slides if "concepts" in slide["material"] for c in slide["material"]["concepts"]]
        self.assertEqual(["Thẻ thứ nhất", "Thẻ hai", "Thẻ ba"], [c["label"] for c in concepts])

    def test_words_over_the_budget_are_flagged_but_titles_are_not(self):
        eleven = " ".join(["từ"] * 11)
        text = lesson_text(figure_section(3)).replace("# Tiêu đề thử", f"# {eleven}")
        result, _ = self.build(text.replace("nội dung của ý 1 trong bài.", eleven))
        cover = result.slides[0]["material"]
        self.assertFalse(cover["title"]["over_budget"])
        self.assertTrue(result.slides[2]["material"]["concepts"][0]["line"]["over_budget"])
        self.assertFalse(result.slides[3]["material"]["concepts"][0]["line"]["over_budget"])

    def test_the_cover_offers_the_check_question_as_the_hook_question(self):
        result, _ = self.build(lesson_text(figure_section(3)))
        self.assertEqual("Máy nào nhận phản hồi?", result.slides[0]["material"]["question_candidate"]["text"])

    def test_backgrounds_bracket_the_deck_in_dark_and_repeat_at_most_once(self):
        for count in brief.SLIDE_COUNTS:
            with self.subTest(count=count):
                sequence = brief.backgrounds(count)
                self.assertEqual(count, len(sequence))
                self.assertEqual(("dark", "dark"), (sequence[0], sequence[-1]))
                repeated = [index for index, (a, b) in enumerate(zip(sequence, sequence[1:])) if a == b]
                # An odd deck alternates throughout; an even one repeats once, on the slide before the closing one.
                self.assertEqual([] if count % 2 else [count - 3], repeated)

    def test_footer_numbers_each_slide_but_the_cover(self):
        result, _ = self.build(lesson_text(figure_section(3)))
        self.assertEqual("System Design 101 · Bài 900 · 03/09", result.slides[2]["footer"])
        self.assertEqual("System Design 101 · Bài 900 · 09/09", result.slides[-1]["footer"])


class RealLessonTests(unittest.TestCase):
    def test_the_slide_range_is_the_one_the_deck_registry_enforces(self):
        self.assertEqual(sd101_slides.SLIDE_COUNTS, brief.SLIDE_COUNTS)

    def test_every_written_lesson_yields_a_deck_inside_the_range_with_its_concepts(self):
        ids = sorted(path.parent.name for path in (STORE / "lessons").glob("sd-*/lesson.md"))
        self.assertTrue(ids)
        for lesson_id in ids:
            with self.subTest(lesson=lesson_id):
                result = brief.build(STORE, lesson_id)
                self.assertIn(result.slide_count, brief.SLIDE_COUNTS)
                self.assertEqual(result.slide_count, len(result.slides))
                self.assertNotEqual("nowhere", result.concept_source)
                self.assertFalse([w for w in result.warnings if "concept line" in w], result.warnings)
                self.assertTrue(result.slides[-1]["material"]["sources"])
                self.assertTrue(result.canvas_name.endswith(f"({lesson_id})"))
                self.assertEqual(brief.build(STORE, lesson_id), result)  # computed, so the same twice

    def test_no_written_lesson_leaves_italic_marks_or_an_unescaped_tag_in_its_brief(self):
        italic = re.compile(r"\*(?=\S)[^*\n]+?(?<=\S)\*")
        tag = re.compile(r"(?<!\\)<[A-Za-z/!]")
        for path in sorted((STORE / "lessons").glob("sd-*/lesson.md")):
            with self.subTest(lesson=path.parent.name):
                result = brief.build(STORE, path.parent.name)
                for text in strings(dataclasses.asdict(result)):  # one string at a time: a lone * in code is no italic
                    self.assertIsNone(italic.search(text), text)
                self.assertIsNone(tag.search(brief.render(result)))

    def test_no_written_lesson_puts_a_typed_address_in_its_brief(self):
        ids = sorted(path.parent.name for path in (STORE / "lessons").glob("sd-*/lesson.md"))
        for lesson_id in ids:
            with self.subTest(lesson=lesson_id):
                result = brief.build(STORE, lesson_id)
                self.assertNotIn("://", brief.render(result))
                self.assertNotIn("://", json.dumps(dataclasses.asdict(result), ensure_ascii=False))

    def test_lessons_whose_figure_has_bold_callouts_keep_the_concepts_the_lesson_names(self):
        # sd-01-007 describes six DNS policies; its figure has a bold callout inside the latency card.
        result = brief.build(STORE, "sd-01-007")
        labels = [c["label"] for slide in result.slides if "concepts" in slide["material"]
                  for c in slide["material"]["concepts"]]
        self.assertEqual(6, len(labels), labels)

    def test_a_numbered_list_under_the_figure_section_is_the_concept_list(self):
        # sd-01-035 names three concepts in an ordered list; the figure has A, B and C as separate cards
        result = brief.build(STORE, "sd-01-035")
        self.assertEqual("bullets under `Đọc hình`", result.concept_source)
        labels = [c["label"] for slide in result.slides if "concepts" in slide["material"]
                  for c in slide["material"]["concepts"]]
        self.assertEqual(["Chọn trong nhóm đích", "Theo dõi điều kiện phục vụ", "Còn phải đủ sức xử lý"], labels)

    def test_every_written_lesson_fills_the_situation_and_deep_dive_slides(self):
        for path in sorted((STORE / "lessons").glob("sd-*/lesson.md")):
            with self.subTest(lesson=path.parent.name):
                by_role = {slide["role"]: slide["material"] for slide in brief.build(STORE, path.parent.name).slides}
                self.assertTrue(by_role["situation and goal"]["lines"])
                self.assertTrue(by_role["deep dive"]["lines"])

    def test_the_markdown_and_json_forms_agree_on_the_slide_count(self):
        result = brief.build(STORE, "sd-01-005")
        self.assertIn(f"Slides: {result.slide_count} ", brief.render(result))


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(ROOT / "scripts" / "sd101_slide_brief.py"), *args],
                              capture_output=True, text=True, cwd=ROOT, timeout=30, check=False)

    def test_prints_a_brief_and_json(self):
        store = Store(lesson_text(figure_section(3)))
        self.addCleanup(store.tmp.cleanup)
        markdown = self.run_cli("sd-01-900", "--store", str(store.path))
        self.assertEqual(0, markdown.returncode, markdown.stderr)
        self.assertIn("# Deck brief: sd-01-900", markdown.stdout)
        self.assertIn("## Slide 9 of 9: terms and sources", markdown.stdout)
        data = json.loads(self.run_cli("sd-01-900", "--json", "--store", str(store.path)).stdout)
        self.assertEqual("sd-01-900", data[0]["lesson"])

    def test_an_unreadable_or_malformed_lesson_exits_1(self):
        store = Store(lesson_text(figure_section(3)))
        self.addCleanup(store.tmp.cleanup)
        for lesson_id in ("sd-01-901", "not-an-id"):
            with self.subTest(lesson=lesson_id):
                result = self.run_cli(lesson_id, "--store", str(store.path))
                self.assertEqual(1, result.returncode)
                self.assertIn(lesson_id, result.stderr)
                self.assertEqual("", result.stdout)

    def test_a_lesson_without_a_title_exits_1(self):
        store = Store("no heading here\n")
        self.addCleanup(store.tmp.cleanup)
        self.assertEqual(1, self.run_cli("sd-01-900", "--store", str(store.path)).returncode)

    def test_a_lesson_that_is_not_utf8_exits_1_with_a_message_not_a_traceback(self):
        store = Store("# title\n")
        self.addCleanup(store.tmp.cleanup)
        (store.path / "lessons" / store.lesson_id / "lesson.md").write_bytes(b"# title\n\xff\xfe broken\n")
        result = self.run_cli("sd-01-900", "--store", str(store.path))
        self.assertEqual(1, result.returncode)
        self.assertIn("not valid UTF-8", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
