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

SHA = "412bbb2f1a549b8eafd7b138f9ee627b8a9d1fc3"


def full_post() -> dict:
    return {
        "id": "demo", "status": "draft", "format": "portrait",
        "slides": [
            {"layout": "cover", "title": "Agent có **ba phần**", "subtitle": "Nói được ba phần của agent."},
            {"layout": "image", "title": "Công thức", "src": "diagrams/vi/agent-formula.png"},
            {"layout": "checklist", "title": "Agent gồm", "items": ["bộ não, đôi tay và một vòng lặp"]},
            {"layout": "poll", "question": "Bộ phận nào làm việc thật?", "options": ["A) LLM", "B) Công cụ"]},
        ],
        "platforms": {"facebook": {
            "caption": "Biết khi nào vòng lặp dừng.\nCode: print(\"xin chào\")\n"
                       "Đáp án: B — công cụ mới thực sự tạo file.",
            "first_comment": "Đọc thêm: {link}",
        }},
    }


def full_manifest() -> dict:
    dests = {
        "objective#01": ("slide:1", "Nói được ba phần của agent"),
        "objective#02": ("caption", "Biết khi nào vòng lặp dừng"),
        "concept#01": ("slide:2", "Công thức"),
        "concept#02": ("slide:2", ""),
        "concept#03": ("slide:3", "bộ não, đôi tay và một vòng lặp"),
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
            "objective#01", "objective#02", "concept#01", "concept#02", "concept#03", "concept#04",
            "quiz#01", "quiz#02", "quiz#03", "quiz#04"])
        self.assertEqual([b["kind"] for b in blocks], [
            "item", "item", "heading", "diagram", "para", "code", "para", "item", "item", "item"])

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
        manifest["blocks"][4]["evidence"] = "agent tự mở file được"
        self.assertTrue(any("concept#03" in p and "is not on slide:3" in p for p in self.problems(manifest=manifest)))

    def test_evidence_on_another_slide_does_not_count(self):
        manifest = full_manifest()
        manifest["blocks"][4]["dest"] = "slide:1"
        self.assertTrue(any("concept#03" in p for p in self.problems(manifest=manifest)))

    def test_the_first_comment_cannot_carry_knowledge(self):
        manifest = full_manifest()
        manifest["blocks"][9]["dest"] = "first_comment"
        self.assertTrue(any("quiz#04" in p and "first comment" in p for p in self.problems(manifest=manifest)))

    def test_a_slide_that_does_not_exist_fails(self):
        manifest = full_manifest()
        manifest["blocks"][0]["dest"] = "slide:9"
        self.assertTrue(any("slide:9 does not exist" in p for p in self.problems(manifest=manifest)))

    def test_one_word_evidence_for_a_long_block_fails(self):
        manifest = full_manifest()
        manifest["blocks"][4]["evidence"] = "vòng lặp"
        self.assertTrue(any("at least 3 words" in p for p in self.problems(manifest=manifest)))

    def test_a_short_block_may_quote_itself_whole(self):
        self.assertFalse(any("quiz#02" in p for p in self.problems()))

    def test_a_diagram_must_be_the_image_on_its_slide(self):
        post = full_post()
        post["slides"][1]["src"] = "diagrams/vi/other.png"
        self.assertTrue(any("diagram 'agent-formula'" in p for p in self.problems(post=post)))

    def test_more_than_ten_slides_fails(self):
        post = full_post()
        post["slides"] += [{"layout": "cover", "title": "thêm"}] * 7
        self.assertTrue(any("11 slides" in p for p in self.problems(post=post)))

    def test_a_block_listed_twice_fails(self):
        manifest = full_manifest()
        manifest["blocks"].append(dict(manifest["blocks"][0]))
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
        git = ["git", "-C", str(self.course)]
        subprocess.run(["git", "init", "-q", str(self.course)], check=True)
        subprocess.run(git + ["add", "."], check=True)
        subprocess.run(git + ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "lesson"], check=True)
        self.sha = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True,
                                  check=True).stdout.strip()
        self.studio = self.root / "studio"
        (self.studio / "posts" / "vi").mkdir(parents=True)
        (self.studio / "coverage").mkdir()

    def problems(self, manifest: dict) -> list[str]:
        manifest["source"]["commit"] = self.sha
        (self.studio / "posts" / "vi" / "demo.yaml").write_text(yaml.safe_dump(full_post(), allow_unicode=True),
                                                               encoding="utf-8")
        path = self.studio / "coverage" / "demo.yaml"
        path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return lc.check(path, self.course)

    def test_a_manifest_matching_the_lesson_passes(self):
        self.assertEqual(self.problems(full_manifest()), [])

    def test_a_dropped_block_fails(self):
        manifest = full_manifest()
        del manifest["blocks"][5]
        self.assertTrue(any("concept#04" in p and "not in the manifest" in p for p in self.problems(manifest)))

    def test_reworded_source_text_fails(self):
        manifest = full_manifest()
        manifest["blocks"][4]["source"] = "Agent gồm bộ não."
        self.assertTrue(any("concept#03" in p and "differs" in p for p in self.problems(manifest)))

    def test_an_invented_block_fails(self):
        manifest = full_manifest()
        manifest["blocks"].append({"key": "concept#99", "kind": "para", "source": "x", "dest": "slide:1",
                                   "evidence": "Agent có ba phần"})
        self.assertTrue(any("concept#99: not a block of the lesson" in p for p in self.problems(manifest)))


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
        bad_manifest["blocks"][0]["evidence"] = "không có ở đây đâu"
        good.write_text(yaml.safe_dump(bad_manifest, allow_unicode=True), encoding="utf-8")
        self.assertEqual(lc.main(["check", str(good)]), 1)


if __name__ == "__main__":
    unittest.main()
