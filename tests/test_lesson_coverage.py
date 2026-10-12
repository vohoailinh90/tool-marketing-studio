"""scripts/lesson_coverage.py: a lesson post must carry every block of its lesson."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import lesson_coverage as lc  # noqa: E402

LESSON = """---
lesson: demo
lang: vi
status: review
social:
  hook: "Agent có ba phần"
  question: Bạn sẽ chọn công cụ nào trước?
---

🌐 **Tiếng Việt** · [English](../../en/lessons/demo.md)

# Bài mẫu

<!-- section: objective -->
## Mục tiêu bài học

- Nói được **ba phần** của agent.
- Biết khi nào [vòng lặp](other.md) dừng.

<!-- section: concept -->
## Nội dung chính

### Công thức

![Công thức](../diagrams/agent-formula.svg)

Agent gồm bộ não, đôi tay
và một vòng lặp.

```python
print("xin chào")
```

<!-- section: quiz -->
## Tự kiểm tra

**Câu 1.** Bộ phận nào làm việc thật?

- A) LLM
- B) Công cụ

<details>
<summary>Xem đáp án</summary>

1. **B** — công cụ mới thực sự tạo file.

</details>
"""

# Markdown the extractor must split, not merge or drop.
TRICKY = """<!-- section: try-it -->
## Thử ngay

- Đường chính
  - Máy cá nhân có thư mục riêng
  - Trình duyệt không cần cài
    dòng tiếp của mục con

| Cột A | Cột B |
|---|---|
| Tháng 9 | 120 |
| Tháng 10 | 150 |

> Hãy đọc file data.csv
> rồi báo tổng doanh thu.

<kbd>Ctrl</kbd> + C dừng chương trình ngay.

---

Đoạn sau đường kẻ.
"""

SHA = "412bbb2f1a549b8eafd7b138f9ee627b8a9d1fc3"

# A course diagram: labels are <text> elements (a label's lines are <tspan>s); a step
# badge, a plus sign and an emoji are drawn as text too but carry no wording.
SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 531">
<title id="title">Công thức</title>
<desc id="desc">Bộ não: LLM + Đôi tay: công cụ</desc>
<style>.pulse { animation: pulse 2s infinite; }</style>
<text font-size="20"><tspan x="1" y="1">Bộ não: LLM</tspan></text>
<text font-size="15"><tspan x="1" y="2">hiểu yêu cầu, quyết định</tspan><tspan x="1" y="3">bước tiếp theo</tspan></text>
<text font-size="13">1</text>
<text font-size="24">+</text>
<text font-size="29">🧠</text>
<text font-size="20">Đôi tay: công cụ</text>
</svg>
"""
DIAGRAM_QUOTES = ["Bộ não: LLM", "hiểu yêu cầu, quyết định bước tiếp theo", "Đôi tay: công cụ"]


def rebuilt_post() -> dict:
    """The full post with the diagram redrawn in the features layout instead of shown as a picture."""
    post = full_post()
    post["slides"][1] = {"layout": "features", "title": "Công thức", "items": [
        {"title": "Bộ não: LLM", "text": "hiểu yêu cầu, quyết định bước tiếp theo"},
        {"title": "Đôi tay: công cụ", "text": ""}]}
    return post


def full_post() -> dict:
    return {
        "id": "demo", "status": "draft", "format": "portrait",
        "slides": [
            {"layout": "cover", "title": "Agent có **ba phần**", "subtitle": "Nói được ba phần của agent."},
            {"layout": "image", "title": "Công thức", "src": "diagrams/vi/agent-formula.png"},
            {"layout": "checklist", "title": "Agent gồm", "items": ["Agent gồm bộ não, đôi tay và một vòng lặp"]},
            {"layout": "poll", "question": "Bộ phận nào làm việc thật?", "options": ["A) LLM", "B) Công cụ"]},
        ],
        "platforms": {"facebook": {
            "caption": "Biết khi nào vòng lặp dừng.\nCode: print(\"xin chào\")\nBạn sẽ chọn công cụ nào trước?\n"
                       "Đáp án: B — công cụ mới thực sự tạo file.",
            "first_comment": "Đọc thêm: {link}",
        }},
    }


def full_manifest() -> dict:
    dests = {
        "social#01": ("slide:1", "Agent có ba phần"),
        "social#02": ("caption", "Bạn sẽ chọn công cụ nào trước?"),
        "objective#01": ("slide:1", "Nói được ba phần của agent"),
        "objective#02": ("caption", "Biết khi nào vòng lặp dừng"),
        "concept#01": ("slide:2", "Công thức"),
        "concept#02": ("slide:2", ""),
        "concept#03": ("slide:3", "Agent gồm bộ não, đôi tay và một vòng lặp"),
        "concept#04": ("caption", 'print("xin chào")'),
        "quiz#01": ("slide:4", "Bộ phận nào làm việc thật?"),
        "quiz#02": ("slide:4", "A) LLM"),
        "quiz#03": ("slide:4", "B) Công cụ"),
        "quiz#04": ("caption", "công cụ mới thực sự tạo file"),
    }
    blocks = []
    for block in lc.extract(LESSON):
        dest, evidence = dests[block["key"]]
        blocks.append({**block, "dest": dest, "evidence": evidence})
    return {
        "lesson": "demo", "lang": "vi",
        "source": {"repo": "vohoailinh90/Agentic-coding-course", "commit": SHA,
                   "path": "course/vi/lessons/demo.md"},
        "post": "../posts/vi/demo.yaml",
        "blocks": blocks,
    }


class ExtractTests(unittest.TestCase):
    def test_blocks_are_every_paragraph_item_heading_code_and_diagram_in_sections(self):
        blocks = lc.extract(LESSON)
        self.assertEqual([b["key"] for b in blocks], [
            "social#01", "social#02", "objective#01", "objective#02", "concept#01", "concept#02", "concept#03", "concept#04",
            "quiz#01", "quiz#02", "quiz#03", "quiz#04"])
        self.assertEqual([b["kind"] for b in blocks], [
            "hook", "question", "item", "item", "heading", "diagram", "para", "code", "para", "item", "item", "item"])

    def test_text_drops_markdown_links_and_emphasis_and_joins_lines(self):
        blocks = {b["key"]: b for b in lc.extract(LESSON)}
        self.assertEqual(blocks["objective#01"]["source"], "Nói được ba phần của agent.")
        self.assertEqual(blocks["objective#02"]["source"], "Biết khi nào vòng lặp dừng.")
        self.assertEqual(blocks["concept#03"]["source"], "Agent gồm bộ não, đôi tay và một vòng lặp.")
        self.assertEqual(blocks["concept#02"]["source"], "agent-formula")

    def test_title_language_bar_and_html_lines_are_not_blocks(self):
        sources = " ".join(b["source"] for b in lc.extract(LESSON))
        self.assertNotIn("Bài mẫu", sources)
        self.assertNotIn("English", sources)
        self.assertNotIn("Xem đáp án", sources)


class TrickyMarkdownTests(unittest.TestCase):
    def setUp(self):
        self.blocks = lc.extract(TRICKY)
        self.sources = [b["source"] for b in self.blocks]

    def test_nested_list_items_are_blocks_of_their_own(self):
        self.assertIn("Đường chính", self.sources)
        self.assertIn("Máy cá nhân có thư mục riêng", self.sources)
        self.assertIn("Trình duyệt không cần cài dòng tiếp của mục con", self.sources)

    def test_every_table_row_is_a_block_and_the_rule_row_is_not(self):
        rows = [b["source"] for b in self.blocks if b["kind"] == "row"]
        self.assertEqual(rows, ["Cột A · Cột B", "Tháng 9 · 120", "Tháng 10 · 150"])

    def test_a_quote_is_one_block_without_its_markers(self):
        quotes = [b["source"] for b in self.blocks if b["kind"] == "quote"]
        self.assertEqual(quotes, ["Hãy đọc file data.csv rồi báo tổng doanh thu."])

    def test_social_hook_and_question_are_blocks(self):
        blocks = {b["key"]: b for b in lc.extract(LESSON)}
        self.assertEqual(blocks["social#01"]["source"], "Agent có ba phần")
        self.assertEqual(blocks["social#02"]["kind"], "question")

    def test_a_line_that_starts_with_a_tag_is_text(self):
        self.assertIn("Ctrl + C dừng chương trình ngay.", self.sources)

    def test_a_rule_is_layout(self):
        self.assertIn("Đoạn sau đường kẻ.", self.sources)
        self.assertFalse(any("---" in source for source in self.sources))

    def test_an_unclosed_fence_is_an_error(self):
        with self.assertRaises(lc.InputError):
            lc.extract("<!-- section: concept -->\n```python\nprint(1)\n<!-- section: quiz -->\n")


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        (self.root / "posts" / "vi").mkdir(parents=True)
        (self.root / "coverage").mkdir()
        self.write(full_post(), full_manifest())

    def write(self, post: dict, manifest: dict) -> Path:
        (self.root / "posts" / "vi" / "demo.yaml").write_text(yaml.safe_dump(post, allow_unicode=True),
                                                             encoding="utf-8")
        path = self.root / "coverage" / "demo.yaml"
        path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return path

    def problems(self, post=None, manifest=None, course_dir=None) -> list[str]:
        path = self.write(post or full_post(), manifest or full_manifest())
        return lc.check(path, course_dir)

    def test_a_complete_manifest_passes(self):
        self.assertEqual(self.problems(), [])

    def test_evidence_missing_from_its_slide_fails(self):
        manifest = full_manifest()
        manifest["blocks"][6]["evidence"] = "agent tự mở file được"
        self.assertTrue(any("concept#03" in p and "is not in one text field slide:3 shows" in p
                            for p in self.problems(manifest=manifest)))

    def test_evidence_on_another_slide_does_not_count(self):
        manifest = full_manifest()
        manifest["blocks"][6]["dest"] = "slide:1"
        self.assertTrue(any("concept#03" in p for p in self.problems(manifest=manifest)))

    def test_the_first_comment_cannot_carry_knowledge(self):
        manifest = full_manifest()
        manifest["blocks"][11]["dest"] = "first_comment"
        self.assertTrue(any("quiz#04" in p and "first comment" in p for p in self.problems(manifest=manifest)))

    def test_a_slide_that_does_not_exist_fails(self):
        manifest = full_manifest()
        manifest["blocks"][2]["dest"] = "slide:9"
        self.assertTrue(any("slide:9 does not exist" in p for p in self.problems(manifest=manifest)))

    def test_one_word_evidence_for_a_long_block_fails(self):
        manifest = full_manifest()
        manifest["blocks"][6]["evidence"] = "vòng lặp"
        self.assertTrue(any("concept#03" in p and "too short" in p for p in self.problems(manifest=manifest)))

    def test_three_words_cannot_stand_in_for_a_long_paragraph(self):
        post = full_post()
        long = ("Agent chỉ sửa được lỗi mà nó quan sát được, nên nếu không được phép chạy thử chương trình "
                "thì nó không thấy lỗi và không biết mình sai ở đâu cả")
        post["slides"][2]["items"] = [long]
        manifest = full_manifest()
        manifest["blocks"][6].update(source=long, evidence="Agent chỉ sửa")
        problems = self.problems(post=post, manifest=manifest)
        self.assertTrue(any("concept#03" in p and "the quotes show 3 of the 10 words needed" in p for p in problems),
                        problems)

    def test_several_quotes_add_up(self):
        post = full_post()
        post["slides"][2]["items"] = ["Agent gồm bộ não", "đôi tay và một vòng lặp"]
        manifest = full_manifest()
        manifest["blocks"][6]["evidence"] = ["Agent gồm bộ não", "đôi tay và một vòng lặp"]
        self.assertEqual(self.problems(post=post, manifest=manifest), [])

    def test_a_quote_cannot_span_two_fields(self):
        post = full_post()
        post["slides"][2]["items"] = ["Agent gồm bộ não, đôi tay", "và một vòng lặp"]
        problems = self.problems(post=post)
        self.assertTrue(any("concept#03" in p and "not in one text field" in p for p in problems), problems)

    def test_hidden_fields_are_not_evidence(self):
        post = full_post()
        post["slides"][2]["tone"] = "Agent gồm bộ não, đôi tay và một vòng lặp"
        post["slides"][2]["items"] = ["khác hẳn"]
        self.assertTrue(any("concept#03" in p for p in self.problems(post=post)))

    def test_one_quote_cannot_prove_two_blocks(self):
        manifest = full_manifest()
        manifest["blocks"][3].update(dest="slide:3", evidence="Agent gồm bộ não, đôi tay và một vòng lặp")
        self.assertTrue(any("already prove" in p for p in self.problems(manifest=manifest)))

    def test_overlapping_quotes_count_each_word_once(self):
        post = full_post()
        long = ("Agent chỉ sửa được lỗi mà nó quan sát được, nên nếu không được phép chạy thử chương trình "
                "thì nó không thấy lỗi và không biết mình sai ở đâu cả")
        post["slides"][2]["items"] = ["Agent chỉ sửa được lỗi"]
        manifest = full_manifest()
        manifest["blocks"][6].update(source=long, evidence=[
            "Agent chỉ sửa được lỗi", "Agent chỉ sửa được", "chỉ sửa được lỗi", "Agent chỉ sửa"])
        problems = self.problems(post=post, manifest=manifest)
        self.assertTrue(any("concept#03" in p and "show 5 of the 10 words" in p for p in problems), problems)

    def test_a_field_the_layout_does_not_draw_is_not_evidence(self):
        post = full_post()
        post["slides"][2] = {"layout": "stat", "before": "1", "after": "2", "label": "nhãn",
                             "value": "Agent gồm bộ não, đôi tay và một vòng lặp"}
        self.assertTrue(any("concept#03" in p for p in self.problems(post=post)))

    def test_the_manifest_cannot_point_at_another_post(self):
        manifest = full_manifest()
        manifest["post"] = "../posts/vi/other.yaml"
        self.assertTrue(any("post must be ../posts/vi/demo.yaml" in p for p in self.problems(manifest=manifest)))

    def test_the_manifest_cannot_point_at_another_lesson(self):
        manifest = full_manifest()
        manifest["source"]["path"] = "course/vi/lessons/short.md"
        self.assertTrue(any("source.path must be course/vi/lessons/demo.md" in p
                            for p in self.problems(manifest=manifest)))

    def test_a_code_block_must_be_shown_whole(self):
        manifest = full_manifest()
        manifest["blocks"][7]["source"] = 'print("xin chào")\nprint("tạm biệt các bạn")'
        self.assertTrue(any("concept#04" in p and "not shown whole" in p for p in self.problems(manifest=manifest)))

    def test_code_without_its_punctuation_is_not_shown(self):
        post = full_post()
        post["platforms"]["facebook"]["caption"] = post["platforms"]["facebook"]["caption"].replace(
            'print("xin chào")', "print xin chào")
        self.assertTrue(any("concept#04" in p and "not shown whole" in p for p in self.problems(post=post)))

    def test_zero_padded_slide_numbers_share_their_words(self):
        manifest = full_manifest()
        manifest["blocks"][3].update(dest="slide:03", evidence="Agent gồm bộ não, đôi tay và một vòng lặp")
        self.assertTrue(any("already prove" in p for p in self.problems(manifest=manifest)))

    def test_a_flow_total_without_minutes_is_not_evidence(self):
        post = full_post()
        post["slides"][2] = {"layout": "flow", "title": "Các bước", "steps": [{"text": "một"}, {"text": "hai"}],
                             "total_label": "Agent gồm bộ não, đôi tay và một vòng lặp"}
        self.assertTrue(any("concept#03" in p for p in self.problems(post=post)))

    def test_a_cta_hint_is_not_evidence(self):
        post = full_post()
        post["slides"][2] = {"layout": "cta", "title": "Đọc tiếp", "hint": "Agent gồm bộ não, đôi tay và một vòng lặp"}
        self.assertTrue(any("concept#03" in p for p in self.problems(post=post)))

    def test_a_short_block_may_quote_itself_whole(self):
        self.assertFalse(any("quiz#02" in p for p in self.problems()))

    def test_a_diagram_must_be_the_image_on_its_slide(self):
        post = full_post()
        post["slides"][1]["src"] = "diagrams/vi/other.png"
        self.assertTrue(any("diagram 'agent-formula'" in p for p in self.problems(post=post)))

    def test_a_diagram_rebuilt_without_evidence_fails(self):
        post = full_post()
        post["slides"][1] = {"layout": "features", "title": "Công thức",
                             "items": [{"title": "Bộ não: LLM", "text": "hiểu yêu cầu, quyết định bước tiếp theo"}]}
        problems = self.problems(post=post, manifest=full_manifest())
        self.assertTrue(any("concept#02" in p and "show 0 of the 3 words needed" in p for p in problems), problems)

    def test_an_image_slide_of_another_diagram_is_not_a_rebuild(self):
        # Its title and caption carry the diagram's words, but the picture is another diagram's: still wrong.
        post = full_post()
        post["slides"][1] = {"layout": "image", "src": "diagrams/vi/other.png",
                             "title": "Bộ não: LLM", "caption": "Đôi tay: công cụ"}
        manifest = full_manifest()
        manifest["blocks"][5]["evidence"] = ["Bộ não: LLM", "Đôi tay: công cụ"]
        problems = self.problems(post=post, manifest=manifest)
        self.assertTrue(any("diagram 'agent-formula' is not the image on slide:2" in p for p in problems), problems)

    def test_a_diagram_rebuilt_in_a_layout_passes_with_its_words_quoted(self):
        post = full_post()
        post["slides"][1] = {"layout": "features", "title": "Công thức",
                             "items": [{"title": "Bộ não: LLM", "text": "hiểu yêu cầu, quyết định bước tiếp theo"}]}
        manifest = full_manifest()
        manifest["blocks"][5]["evidence"] = ["Bộ não: LLM", "hiểu yêu cầu, quyết định bước tiếp theo"]
        self.assertEqual(self.problems(post=post, manifest=manifest), [])

    def test_more_than_ten_slides_fails(self):
        post = full_post()
        post["slides"] += [{"layout": "cover", "title": "thêm"}] * 7
        self.assertTrue(any("11 slides" in p for p in self.problems(post=post)))

    def test_a_block_listed_twice_fails(self):
        manifest = full_manifest()
        manifest["blocks"].append(dict(manifest["blocks"][2]))
        self.assertTrue(any("listed twice" in p for p in self.problems(manifest=manifest)))

    def test_a_short_commit_fails(self):
        manifest = full_manifest()
        manifest["source"]["commit"] = "412bbb2"
        self.assertTrue(any("40-character" in p for p in self.problems(manifest=manifest)))


class SourceTests(unittest.TestCase):
    """--course-dir: the manifest must list exactly the lesson's blocks at the pinned commit."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.course = self.root / "course-repo"
        lesson = self.course / "course" / "vi" / "lessons" / "demo.md"
        lesson.parent.mkdir(parents=True)
        lesson.write_text(LESSON, encoding="utf-8")
        diagram = self.course / "course" / "vi" / "diagrams" / "agent-formula.svg"
        diagram.parent.mkdir(parents=True)
        diagram.write_text(SVG, encoding="utf-8")
        git = ["git", "-C", str(self.course)]
        subprocess.run(["git", "init", "-q", str(self.course)], check=True)
        subprocess.run(git + ["add", "."], check=True)
        subprocess.run(git + ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "lesson"], check=True)
        self.sha = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True,
                                  check=True).stdout.strip()
        self.studio = self.root / "studio"
        (self.studio / "posts" / "vi").mkdir(parents=True)
        (self.studio / "coverage").mkdir()

    def problems(self, manifest: dict, post: dict | None = None) -> list[str]:
        manifest["source"]["commit"] = self.sha
        (self.studio / "posts" / "vi" / "demo.yaml").write_text(yaml.safe_dump(post or full_post(), allow_unicode=True),
                                                               encoding="utf-8")
        path = self.studio / "coverage" / "demo.yaml"
        path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return lc.check(path, self.course)

    def test_a_manifest_matching_the_lesson_passes(self):
        self.assertEqual(self.problems(full_manifest()), [])

    def test_a_dropped_block_fails(self):
        manifest = full_manifest()
        del manifest["blocks"][7]
        self.assertTrue(any("concept#04" in p and "not in the manifest" in p for p in self.problems(manifest)))

    def test_reworded_source_text_fails(self):
        manifest = full_manifest()
        manifest["blocks"][6]["source"] = "Agent gồm bộ não."
        self.assertTrue(any("concept#03" in p and "differs" in p for p in self.problems(manifest)))

    def test_an_invented_block_fails(self):
        manifest = full_manifest()
        manifest["blocks"].append({"key": "concept#99", "kind": "para", "source": "x", "dest": "slide:1",
                                   "evidence": "Agent có ba phần"})
        self.assertTrue(any("concept#99: not a block of the lesson" in p for p in self.problems(manifest)))

    def test_a_rebuilt_diagram_passes_when_it_shows_the_diagram_words(self):
        manifest = full_manifest()
        manifest["blocks"][5]["evidence"] = DIAGRAM_QUOTES
        self.assertEqual(self.problems(manifest, rebuilt_post()), [])

    def test_a_rebuilt_diagram_must_show_most_of_its_words(self):
        manifest = full_manifest()
        manifest["blocks"][5]["evidence"] = [DIAGRAM_QUOTES[0], DIAGRAM_QUOTES[2]]  # 7 of the 15 words; 9 are needed
        problems = self.problems(manifest, rebuilt_post())
        self.assertTrue(any("concept#02" in p and "show 7 of the 9 words needed (15 in the diagram)" in p
                            for p in problems), problems)

    def test_a_rebuilt_diagram_may_reuse_words_that_prove_prose_blocks(self):
        # The diagram restates the prose, so one drawn label can prove both the diagram and a paragraph.
        manifest = full_manifest()
        manifest["blocks"][5]["evidence"] = DIAGRAM_QUOTES
        manifest["blocks"][6].update(dest="slide:2", evidence="Bộ não: LLM")
        self.assertEqual(self.problems(manifest, rebuilt_post()), [])

    def test_a_rebuilt_diagram_must_quote_the_diagram_not_other_words(self):
        filler = "xin chào các bạn hôm nay trời đẹp quá nhỉ"  # 9 words drawn on the slide, none of them the diagram's
        post = full_post()
        post["slides"][1] = {"layout": "features", "title": "Công thức", "items": [{"title": filler, "text": ""}]}
        manifest = full_manifest()
        manifest["blocks"][5]["evidence"] = [filler]
        problems = self.problems(manifest, post)
        self.assertTrue(any("concept#02" in p and "is not wording of the diagram 'agent-formula'" in p
                            for p in problems), problems)

    def test_quoting_one_diagram_phrase_again_adds_nothing(self):
        manifest = full_manifest()
        manifest["blocks"][5]["evidence"] = [DIAGRAM_QUOTES[0]] * 5  # 3 words of the diagram, five times
        problems = self.problems(manifest, rebuilt_post())
        self.assertTrue(any("concept#02" in p and "show 3 of the 9 words needed" in p for p in problems), problems)

    def test_a_phrase_inside_a_label_counts_for_its_own_words(self):
        manifest = full_manifest()
        manifest["blocks"][5]["evidence"] = ["Bộ não: LLM", "yêu cầu, quyết định bước tiếp theo", "Đôi tay: công cụ"]
        self.assertEqual(self.problems(manifest, rebuilt_post()), [])  # 3 + 6 + 4 = 13 of 15

    def test_a_label_the_diagram_repeats_is_credited_once_per_drawn_copy(self):
        # Ten copies of one label in the SVG, one copy on the slide: quoting it six times covers six copies
        # of the diagram but shows the reader one.
        repeated = ('<svg xmlns="http://www.w3.org/2000/svg">' + "<text>Bộ não LLM</text>" * 10 + "</svg>")
        diagram = self.course / "course" / "vi" / "diagrams" / "agent-formula.svg"
        diagram.write_text(repeated, encoding="utf-8")
        git = ["git", "-C", str(self.course)]
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "repeat"], check=True)
        self.sha = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True,
                                  check=True).stdout.strip()
        post = full_post()
        post["slides"][1] = {"layout": "features", "title": "Công thức", "items": [{"title": "Bộ não LLM", "text": ""}]}
        manifest = full_manifest()
        manifest["blocks"][5]["evidence"] = ["Bộ não LLM"] * 6
        problems = self.problems(manifest, post)
        self.assertTrue(any("concept#02" in p and "show 3 of the 18 words needed (30 in the diagram)" in p
                            for p in problems), problems)

    def test_a_diagram_missing_from_the_course_fails(self):
        manifest = full_manifest()
        manifest["blocks"][5]["evidence"] = DIAGRAM_QUOTES
        shutil.rmtree(self.course / "course" / "vi" / "diagrams")
        git = ["git", "-C", str(self.course)]
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "drop"], check=True)
        self.sha = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True,
                                  check=True).stdout.strip()
        problems = self.problems(manifest, rebuilt_post())
        self.assertTrue(any("concept#02" in p and "cannot read course/vi/diagrams/agent-formula.svg" in p
                            for p in problems), problems)


class DiagramLabelTests(unittest.TestCase):
    def test_a_label_is_one_string_with_its_lines_joined_and_badges_and_signs_left_out(self):
        self.assertEqual(lc.diagram_labels(SVG), [
            "Bộ não: LLM", "hiểu yêu cầu, quyết định bước tiếp theo", "Đôi tay: công cụ"])

    def test_the_description_and_the_style_are_not_labels(self):
        labels = " ".join(lc.diagram_labels(SVG))
        self.assertNotIn("animation", labels)
        self.assertNotIn("+ Đôi", labels)

    def test_a_diagram_that_is_not_svg_is_an_input_error(self):
        with self.assertRaises(lc.InputError):
            lc.diagram_labels("<svg><text>chưa đóng")


class AllTests(unittest.TestCase):
    def test_a_course_post_without_a_manifest_fails(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        campaign = root / "campaigns" / "agentic-coding-course"
        (campaign / "posts" / "vi").mkdir(parents=True)
        (campaign / "posts" / "vi" / "demo.yaml").write_text(yaml.safe_dump(full_post(), allow_unicode=True),
                                                            encoding="utf-8")
        self.assertEqual(lc.main(["check", "--all", "--root", str(root)]), 1)
        (campaign / "coverage").mkdir()
        (campaign / "coverage" / "demo.yaml").write_text(yaml.safe_dump(full_manifest(), allow_unicode=True),
                                                        encoding="utf-8")
        self.assertEqual(lc.main(["check", "--all", "--root", str(root)]), 0)


class CliTests(unittest.TestCase):
    def test_check_exits_1_on_failure_and_0_on_success(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        (root / "posts" / "vi").mkdir(parents=True)
        (root / "coverage").mkdir()
        (root / "posts" / "vi" / "demo.yaml").write_text(yaml.safe_dump(full_post(), allow_unicode=True),
                                                        encoding="utf-8")
        good = root / "coverage" / "demo.yaml"
        good.write_text(yaml.safe_dump(full_manifest(), allow_unicode=True), encoding="utf-8")
        self.assertEqual(lc.main(["check", str(good)]), 0)
        bad_manifest = full_manifest()
        bad_manifest["blocks"][2]["evidence"] = "không có ở đây đâu"
        good.write_text(yaml.safe_dump(bad_manifest, allow_unicode=True), encoding="utf-8")
        self.assertEqual(lc.main(["check", str(good)]), 1)


if __name__ == "__main__":
    unittest.main()
