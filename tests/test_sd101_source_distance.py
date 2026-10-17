"""scripts/sd101_source_distance.py: the closeness ranking, on synthetic text and a fixture store (no network)."""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import tempfile
import unicodedata
import unittest
from unittest import mock

from scripts import sd101_source_distance as distance_tool

SOURCE = """---
title: 'One guide'
---

![](https://assets.example.com/one.png)

*   Postgres replicates writes
*   Redis caches 1,000 sessions
*   Kafka streams events
"""
# The same names and numbers in the same order, in Vietnamese prose.
FOLLOWS = """# Bài

## Đọc hình

- Postgres replicates writes ở bản sao.
- Redis caches 1000 phiên.
- Kafka streams events liên tục.
"""
REORDERED = """# Bài

## Đọc hình

- Kafka streams events liên tục.
- Redis caches 1000 phiên.
- Postgres replicates writes ở bản sao.
"""
DEEPENED = FOLLOWS + """
Thử nghiệm riêng: hàng đợi Rabbitmq giữ thông điệp, Cassandra chia khóa, Etcd bầu chủ, Zookeeper điều phối,
Memcached đọc nhanh, Consul đăng ký dịch vụ.
"""
UNRELATED = "# Bài\n\n## Đọc hình\n\n- Hoàn toàn khác: Mongodb lưu tài liệu, Elasticsearch đánh chỉ mục.\n"


def snapshot_for(data: bytes) -> dict:
    return {"repository": "ByteByteGoHq/system-design-101", "commit_sha": "c" * 40, "path": "data/guides/one.md",
            "blob_sha": distance_tool.blob_sha(data)}


class TextTests(unittest.TestCase):
    def test_blob_sha_is_the_git_blob_id(self) -> None:
        self.assertEqual(distance_tool.blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_source_body_drops_front_matter_and_images(self) -> None:
        body = distance_tool.source_body(SOURCE)
        self.assertNotIn("title:", body)
        self.assertNotIn("assets.example.com", body)
        self.assertIn("Redis caches", body)

    def test_link_destinations_are_not_vocabulary_of_the_source_or_the_lesson(self) -> None:
        text = "Postgres [replicates data](https://hosting.example/pathsegment/guide) and Redis, see https://bareurl.example/other for more, then [Kafka](relativefolder/pathword.md).\n"
        for tokens in (distance_tool.signal_tokens(distance_tool.source_body(text)),
                       distance_tool.signal_tokens(distance_tool.lesson_prose(text))):
            self.assertEqual(tokens, ["postgres", "replicates", "data", "redis", "kafka"])
        self.assertEqual(distance_tool.signal_tokens(distance_tool.source_body("Kafka ![shot](https://img.example/a.png) streams\n")), ["kafka", "streams"])

    def test_signal_tokens_keep_names_and_numbers_in_order_and_drop_noise(self) -> None:
        tokens = distance_tool.signal_tokens("Redis caches 1,000 sessions; trong đó với dữ liệu a 7 và 42 Redis again with-hyphen_part")
        self.assertEqual(tokens[:3], ["redis", "caches", "1000"])
        self.assertEqual(tokens.count("redis"), 1)           # first appearance only
        self.assertIn("42", tokens)
        self.assertNotIn("7", tokens)                         # one digit is not a signal
        self.assertNotIn("with", tokens)                      # stop word
        self.assertIn("hyphen", tokens)                       # compound words are split
        self.assertNotIn("dữ", tokens)

    def test_a_vietnamese_word_is_dropped_whole_not_cut_into_ascii_fragments(self) -> None:
        text = "chuyển nghiệm nguyên Postgres khuyến"
        self.assertEqual(distance_tool.signal_tokens(text), ["postgres"])
        # the same text with the marks as separate combining characters (NFD) must give the same answer
        self.assertEqual(distance_tool.signal_tokens(unicodedata.normalize("NFD", text)), ["postgres"])

    def test_vietnamese_words_without_marks_are_language_not_names(self) -> None:
        # one syllable each, no diacritic: the ASCII test alone would keep them
        words = "theo nhau giao danh gian chia khai truy trang ngay minh sang nhanh tham trung khung sinh xong quen giai thao"
        self.assertEqual(distance_tool.signal_tokens(words), [])
        # English technical words of a similar shape are kept
        self.assertEqual(distance_tool.signal_tokens("train main chain route client server"),
                         ["train", "main", "chain", "route", "client", "server"])

    def test_a_name_that_fits_a_vietnamese_syllable_is_kept_when_listed(self) -> None:
        text = "CoAP QUIC ping long theo nhau"
        # TECHNICAL_NAMES lists names that only the lessons use; the English sources supply the rest through `keep`
        self.assertEqual(distance_tool.signal_tokens(text), ["coap"])
        self.assertEqual(distance_tool.signal_tokens(text, frozenset({"quic", "ping", "long"})), ["coap", "quic", "ping", "long"])

    def test_shaped_names_are_the_words_of_a_guide_that_look_like_vietnamese_syllables(self) -> None:
        self.assertEqual(distance_tool.shaped_names("Short/long polling over QUIC, ping the Postgres server"), {"long", "quic", "ping"})

    def test_angle_brackets_inside_code_are_kept_as_text(self) -> None:
        lesson = ("# T\n\nDùng `<trace-id>` và <details>Zookeeper</details>.\n\n```html\n<p class=\"note\">Etcd</p>\n```\n"
                  "<!-- hidden Consul -->\n")
        tokens = distance_tool.signal_tokens(distance_tool.lesson_prose(lesson))
        for kept in ("trace", "note", "etcd", "zookeeper"):
            self.assertIn(kept, tokens)
        for dropped in ("details", "consul"):
            self.assertNotIn(dropped, tokens)

    def test_shaped_names_ignore_vietnamese_words_written_with_combining_marks(self) -> None:
        # "nhie" would be a syllable-shaped fragment of NFD "nhiều"; the whole word has a mark, so it is no English name
        self.assertEqual(distance_tool.shaped_names(unicodedata.normalize("NFD", "nhiều trường")), set())

    def test_html_markup_is_not_vocabulary_in_the_lesson_or_the_source(self) -> None:
        lesson = "# T\n\n<details>\n<summary>Xem</summary>\n\nPostgres replicates.\n\n</details>\n<!-- hidden Zookeeper note -->\n"
        self.assertEqual(distance_tool.signal_tokens(distance_tool.lesson_prose(lesson)), ["postgres", "replicates"])
        self.assertEqual(distance_tool.signal_tokens(distance_tool.source_body("<div><span>Redis</span></div>\n")), ["redis"])

    def test_words_shorter_than_the_minimum_are_not_signals(self) -> None:
        self.assertEqual(distance_tool.signal_tokens("api tcp udp http"), ["http"])

    def test_lcs_length(self) -> None:
        self.assertEqual(distance_tool.lcs_length(list("abcde"), list("ace")), 3)
        self.assertEqual(distance_tool.lcs_length(list("abc"), list("cba")), 1)
        self.assertEqual(distance_tool.lcs_length([], list("abc")), 0)

    def test_lesson_prose_leaves_out_the_glossary_the_sources_and_link_targets(self) -> None:
        lesson = ("# T\n\n![alt text](../../diagrams/x.svg)\n\n## Từ viết tắt\n\n- **GLOSSARYWORD** (Full Form) — x\n\n"
                  "## Đọc hình\n\nPlain [link text](https://example.com/hidden-target) end.\n\n## Nguồn đối chiếu\n\n- SOURCELISTWORD\n")
        prose = distance_tool.lesson_prose(lesson)
        self.assertIn("Plain", prose)
        self.assertIn("link text", prose)
        for left_out in ("GLOSSARYWORD", "SOURCELISTWORD", "hidden-target", "diagrams"):
            self.assertNotIn(left_out, prose)

    def test_a_heading_like_line_inside_a_code_fence_does_not_split_the_lesson(self) -> None:
        lesson = "# T\n\n## Đọc hình\n\nPostgres replicates.\n\n```sh\n## Từ viết tắt\ncurl Kafka\n```\n\nRedis caches.\n"
        self.assertEqual(list(distance_tool.sections(lesson)), ["", "Đọc hình"])
        self.assertEqual(distance_tool.signal_tokens(distance_tool.lesson_prose(lesson)), ["postgres", "replicates", "curl", "kafka", "redis", "caches"])

    def test_lesson_units_count_the_reading_section_items(self) -> None:
        lesson = "# T\n\n- outside\n\n## Đọc hình\n\n1. one\n2. two\n**Bold lead.** three\n\ntext\n\n## Khác\n\n- elsewhere\n"
        self.assertEqual(distance_tool.lesson_units(lesson), 3)


class DistanceTests(unittest.TestCase):
    def test_a_lesson_that_replays_its_source_scores_high_and_one_that_adds_nothing_has_no_novelty(self) -> None:
        numbers = distance_tool.distance(SOURCE, FOLLOWS)
        self.assertAlmostEqual(numbers["coverage"], 0.9)    # 9 of the source's 10 names ("sessions" is "phiên" here)
        self.assertEqual(numbers["order"], 1.0)
        self.assertAlmostEqual(numbers["replay"], 0.9)
        self.assertLess(numbers["novelty"], 0.2)
        self.assertGreater(numbers["closeness"], 0.8)

    def test_the_same_vocabulary_in_another_order_lowers_order_but_not_coverage(self) -> None:
        followed, reordered = distance_tool.distance(SOURCE, FOLLOWS), distance_tool.distance(SOURCE, REORDERED)
        self.assertEqual(reordered["coverage"], followed["coverage"])
        self.assertLess(reordered["order"], followed["order"])
        self.assertLess(reordered["closeness"], followed["closeness"])

    def test_new_material_of_the_lessons_own_raises_novelty_and_lowers_closeness(self) -> None:
        followed, deepened = distance_tool.distance(SOURCE, FOLLOWS), distance_tool.distance(SOURCE, DEEPENED)
        self.assertGreater(deepened["novelty"], followed["novelty"] + 0.3)
        self.assertLess(deepened["closeness"], followed["closeness"] * 0.7)

    def test_a_lesson_with_nothing_in_common_scores_zero(self) -> None:
        numbers = distance_tool.distance(SOURCE, UNRELATED)
        self.assertEqual(numbers["coverage"], 0.0)
        self.assertEqual(numbers["closeness"], 0.0)

    def test_unit_mirror_compares_item_counts_and_is_none_for_a_single_item(self) -> None:
        self.assertEqual(distance_tool.distance(SOURCE, FOLLOWS)["unit_mirror"], 1.0)
        self.assertIsNone(distance_tool.distance(SOURCE, "# T\n\n## Đọc hình\n\n- only one\n")["unit_mirror"])


class MetadataTests(unittest.TestCase):
    META = {"source_snapshot": {"repository": "ByteByteGoHq/system-design-101"},
            "claims": [{"source": "https://github.com/ByteByteGoHq/system-design-101/blob/x/y.md"},
                       {"source": "https://bytebytego.com/guides/one"},
                       {"sources": ["https://www.rfc-editor.org/rfc/rfc9110", "https://docs.python.org/3/library/http.html",
                                    "https://docs.python.org/3/library/ssl.html"]}],
            "verification": {"claims": {}}}

    def test_independent_hosts_leave_out_the_source_itself(self) -> None:
        self.assertEqual(distance_tool.independent_hosts(self.META), ["docs.python.org", "www.rfc-editor.org"])

    def test_own_evidence_needs_a_recorded_run_or_measurement(self) -> None:
        self.assertFalse(distance_tool.own_evidence({"claims": [{"verified_by": "Đã đọc tài liệu"}]}))
        self.assertTrue(distance_tool.own_evidence({"claims": [{"verified_by": "Chạy thử trên máy cục bộ"}]}))
        self.assertTrue(distance_tool.own_evidence({"claims": [], "verification": {"claims": {"evidence": "measured on 3 hosts"}}}))

    def test_a_negated_run_is_not_evidence_and_the_recorded_phrasing_is_read(self) -> None:
        # sd-02-002 says it was not run; sd-01-003 says "Chạy máy chủ giả cục bộ" (ran a fake server locally).
        self.assertFalse(distance_tool.own_evidence({"claims": [{"verified_by": "Suy luận của người biên soạn; chưa chạy thử trên sản phẩm nào."}]}))
        self.assertFalse(distance_tool.own_evidence({"claims": [{"verified_by": "Not tested on any product."}]}))
        self.assertTrue(distance_tool.own_evidence({"claims": [{"verified_by": "Chạy máy chủ giả cục bộ ngày 2026-10-16."}]}))

    def test_a_run_in_one_clause_is_not_cancelled_by_a_negation_in_another(self) -> None:
        self.assertTrue(distance_tool.recorded_run("Chạy Postgres 16 cục bộ: 20 phiên; trang tài liệu chưa mở được."))
        self.assertTrue(distance_tool.recorded_run("Không đọc được tài liệu. Chạy thử cục bộ."))     # the negation ends with its clause
        self.assertFalse(distance_tool.recorded_run("Lợi ích nguồn nêu, không phải bảo đảm hoặc số đo cho mọi hệ thống."))

    def test_the_scope_of_the_claims_step_counts_as_a_record(self) -> None:
        self.assertTrue(distance_tool.own_evidence({"claims": [], "verification": {"claims": {"scope": "Chạy PostgreSQL 16.15 và SQLite."}}}))


class FetchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cache = pathlib.Path(self.tmp.name) / "cache"
        self.cache.mkdir()

    def test_a_cached_body_whose_blob_sha_matches_the_pin_is_returned(self) -> None:
        data = SOURCE.encode()
        snapshot = snapshot_for(data)
        (self.cache / f"{snapshot['blob_sha']}.md").write_bytes(data)
        self.assertEqual(distance_tool.fetch_source(snapshot, self.cache, offline=True), SOURCE)

    def test_a_cached_body_with_another_blob_sha_is_rejected_and_removed(self) -> None:
        snapshot = snapshot_for(SOURCE.encode())
        cached = self.cache / f"{snapshot['blob_sha']}.md"
        cached.write_bytes(b"tampered")
        with self.assertRaises(ValueError):
            distance_tool.fetch_source(snapshot, self.cache, offline=True)
        self.assertFalse(cached.exists())

    def test_a_pinned_id_that_is_not_a_git_object_id_is_refused_before_it_becomes_a_file_name(self) -> None:
        snapshot = snapshot_for(SOURCE.encode())
        for bad in ("../../escape", "A" * 40, "abc", 7):
            with self.assertRaises(ValueError):
                distance_tool.fetch_source({**snapshot, "blob_sha": bad}, self.cache, offline=True)
        self.assertEqual(list(self.cache.iterdir()), [])

    def test_a_snapshot_that_cannot_become_a_download_address_is_refused_without_a_request(self) -> None:
        snapshot = snapshot_for(SOURCE.encode())
        for key, bad in (("repository", "owner/../other"), ("repository", "https://evil.example/x"), ("commit_sha", "main"),
                         ("path", "data/../../secret.md"), ("path", "../x.md"), ("path", "")):
            with self.subTest(key=key, value=bad), self.assertRaises(ValueError), \
                    mock.patch.object(distance_tool.urllib.request, "urlopen", side_effect=AssertionError("a request was made")):
                distance_tool.fetch_source({**snapshot, key: bad}, self.cache, offline=False)

    def test_offline_without_a_cache_entry_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            distance_tool.fetch_source(snapshot_for(SOURCE.encode()), self.cache, offline=True)


class SurveyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = pathlib.Path(self.tmp.name)
        self.cache, self.store = base / "cache", base / "store"
        self.cache.mkdir()
        for lesson_id, text in (("sd-01-001", DEEPENED), ("sd-01-002", FOLLOWS)):
            (self.store / "lessons" / lesson_id).mkdir(parents=True)
            (self.store / "lessons" / lesson_id / "lesson.md").write_text(text, encoding="utf-8")
            (self.store / "metadata").mkdir(exist_ok=True)
            (self.store / "metadata" / f"{lesson_id}.json").write_text(json.dumps(
                {"title_vi": lesson_id, "source_snapshot": snapshot_for(SOURCE.encode()), "claims": []}), encoding="utf-8")
        data = SOURCE.encode()
        (self.cache / f"{distance_tool.blob_sha(data)}.md").write_bytes(data)

    def test_the_closest_lesson_comes_first(self) -> None:
        rows, problems = distance_tool.survey(self.store, self.cache, offline=True)
        self.assertEqual(problems, [])
        self.assertEqual([row["id"] for row in rows], ["sd-01-002", "sd-01-001"])

    def test_main_prints_a_table_and_writes_the_numbers(self) -> None:
        report = pathlib.Path(self.tmp.name) / "report.json"
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = distance_tool.main(["--store", str(self.store), "--cache-dir", str(self.cache), "--offline", "--json", str(report)])
        self.assertEqual(code, 0)
        self.assertIn("sd-01-002", out.getvalue())
        self.assertEqual([row["id"] for row in json.loads(report.read_text(encoding="utf-8"))["lessons"]], ["sd-01-002", "sd-01-001"])

    def test_main_exits_2_when_a_lesson_cannot_be_measured(self) -> None:
        (self.cache / f"{distance_tool.blob_sha(SOURCE.encode())}.md").unlink()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = distance_tool.main(["--store", str(self.store), "--cache-dir", str(self.cache), "--offline"])
        self.assertEqual(code, 2)

    def test_a_metadata_file_that_is_not_json_is_reported_not_raised(self) -> None:
        (self.store / "metadata" / "sd-01-002.json").write_text("{not json", encoding="utf-8")
        rows, problems = distance_tool.survey(self.store, self.cache, offline=True)
        self.assertEqual([row["id"] for row in rows], ["sd-01-001"])
        self.assertEqual(len(problems), 1)
        self.assertIn("sd-01-002", problems[0])

    def test_metadata_of_the_wrong_shape_is_reported_for_that_lesson_only(self) -> None:
        path = self.store / "metadata" / "sd-01-002.json"
        for broken in ({"claims": None}, {"claims": [], "verification": ["x"]}):
            meta = {"title_vi": "x", "source_snapshot": snapshot_for(SOURCE.encode()), **broken}
            path.write_text(json.dumps(meta), encoding="utf-8")
            with self.subTest(broken=broken):
                rows, problems = distance_tool.survey(self.store, self.cache, offline=True)
                self.assertEqual([row["id"] for row in rows], ["sd-01-001"])
                self.assertEqual(len(problems), 1)
                self.assertIn("sd-01-002", problems[0])

    def test_a_name_used_by_another_guide_is_kept_for_every_lesson(self) -> None:
        # "ping" fits the shape of a Vietnamese syllable. Guide one uses it as a name; lesson two is written from guide two
        # and uses it too, so it is vocabulary of lesson two (not of its source) and counts as novelty there.
        first, second = "*   Redis ping\n*   Kafka streams\n", "*   Postgres replicates writes\n*   Etcd leases\n"
        for data in (first, second):
            (self.cache / f"{distance_tool.blob_sha(data.encode())}.md").write_bytes(data.encode())
        for lesson_id, data, text in (("sd-01-001", first, "# T\n\n## Đọc hình\n\n- Redis ping\n- Kafka streams\n"),
                                      ("sd-01-002", second, "# T\n\n## Đọc hình\n\n- Postgres replicates writes\n- Etcd leases ping\n")):
            (self.store / "lessons" / lesson_id / "lesson.md").write_text(text, encoding="utf-8")
            (self.store / "metadata" / f"{lesson_id}.json").write_text(json.dumps(
                {"title_vi": lesson_id, "source_snapshot": snapshot_for(data.encode()), "claims": []}), encoding="utf-8")
        rows, problems = distance_tool.survey(self.store, self.cache, offline=True)
        self.assertEqual(problems, [])
        novelty = {row["id"]: row["novelty"] for row in rows}
        self.assertEqual(novelty["sd-01-001"], 0.0)
        self.assertGreater(novelty["sd-01-002"], 0.1)    # "ping" is counted as the lesson's own word

    def test_a_cache_inside_the_repository_is_refused(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            distance_tool.main(["--store", str(self.store), "--cache-dir", str(distance_tool.ROOT / "source-cache"), "--offline"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
