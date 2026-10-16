"""scripts/vocab.py and vocab/vocab_standalone.html: the vocabulary store, the commands that fill it, and the page that reads it."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts import vocab

REAL_PAGE = vocab.STORE
ENTRY = {"term": "dodge", "meaning": "Né tránh, lách qua", "register": "Trung tính",
         "note": "dodge a question", "source": "Ch.2 Mirroring", "lang": "EN"}
OTHER = {"term": "stalemate", "meaning": "Thế bế tắc", "register": "Văn viết", "note": "Gốc từ cờ vua",
         "source": "Ch.2 Mirroring", "lang": "EN"}
TABLE_HEAD = "| Từ/Cụm | Nghĩa tiếng Việt | Văn phong | Ghi chú | Nguồn |\n|---|---|---|---|---|\n"

COLORS = "\n".join(f'  "{name}": {{ bg: "#fff" }},' for name in vocab.REGISTERS)
PAGE = """<!DOCTYPE html>
<html><body><div id="app"></div><script>
"use strict";
@@BLOCK@@
const REGISTER_COLORS = {
@@COLORS@@
};
function rest() { return 1; }
</script></body></html>
"""


def page_text(entries: list[dict], newline: str = "\n") -> str:
    text = PAGE.replace("@@BLOCK@@", vocab.render_block(entries)).replace("@@COLORS@@", COLORS)
    return text.replace("\n", newline)


class Workspace(unittest.TestCase):
    """A temporary page to read and write, and `run` to call the command line the way a session does."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        self.page = self.dir / "page.html"

    def make(self, entries: list[dict] | None = None, newline: str = "\n") -> Path:
        self.page.write_bytes(page_text(entries or [], newline).encode("utf-8"))
        return self.page

    def stored(self) -> list[dict]:
        return vocab.Store.load(self.page).entries

    def batch(self, text: str, name: str = "batch.md") -> str:
        path = self.dir / name
        path.write_text(text, encoding="utf-8")
        return str(path)

    def run_cli(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = vocab.main(["--store", str(self.page), *argv])
        return code, out.getvalue()


class KeyTests(unittest.TestCase):
    def test_a_word_is_the_same_whatever_its_case_spacing_or_width(self):
        self.assertEqual(vocab.term_key("  Elaborate   ON "), vocab.term_key("elaborate on"))
        self.assertEqual(vocab.term_key("ＡＢＣ"), vocab.term_key("abc"))

    def test_a_kana_reading_in_brackets_is_not_part_of_the_identity(self):
        self.assertEqual(vocab.term_key("逸脱 (いつだつ)"), vocab.term_key("逸脱"))
        self.assertEqual(vocab.term_key("逸脱（いつだつ）"), vocab.term_key("逸脱"))

    def test_a_bracket_that_changes_the_sense_is_part_of_the_identity(self):
        self.assertNotEqual(vocab.term_key("trigger (v)"), vocab.term_key("trigger"))
        self.assertEqual(vocab.headword("trigger (v)"), vocab.headword("trigger"))
        self.assertEqual(vocab.headword("critical (= important)"), "critical")

    def test_language_is_read_from_the_script(self):
        self.assertEqual(vocab.detect_lang("がたがた"), "JA")
        self.assertEqual(vocab.detect_lang("ウェブ"), "JA")
        self.assertEqual(vocab.detect_lang("skill set"), "EN")

    def test_a_source_typed_two_ways_is_one_source(self):
        self.assertEqual(vocab.source_key("Ch.2 Mirroring"), vocab.source_key("ch 2 - mirroring"))
        self.assertNotEqual(vocab.source_key("Ch.2 Mirroring"), vocab.source_key("Ch.3 Mirroring"))

    def test_a_register_copied_from_the_page_with_its_emoji_is_still_a_register(self):
        self.assertEqual(vocab.normalize_register("🗣 Văn nói"), "Văn nói")
        self.assertEqual(vocab.normalize_register("⚖️ Trung tính"), "Trung tính")
        self.assertEqual(vocab.normalize_register("văn VIẾT"), "Văn viết")
        self.assertEqual(vocab.normalize_register("formal"), "formal")  # left for the validator to refuse


class ParseTests(unittest.TestCase):
    def test_a_table_is_read_without_its_header_or_separator(self):
        rows, errors = vocab.parse_table(TABLE_HEAD + "| dodge | Né tránh | Trung tính | note | Ch.2 |\n")
        self.assertEqual(errors, [])
        self.assertEqual([r.values for r in rows],
                         [{"term": "dodge", "meaning": "Né tránh", "register": "Trung tính", "note": "note", "source": "Ch.2"}])

    def test_markdown_decoration_in_cells_is_removed(self):
        rows, _ = vocab.parse_table("| **dodge** | `Né tránh`<br>lách | Trung tính |\n")
        self.assertEqual(rows[0].values["term"], "dodge")
        self.assertEqual(rows[0].values["meaning"], "Né tránh lách")

    def test_text_around_the_table_is_ignored(self):
        rows, errors = vocab.parse_table("Đây là bảng:\n\n| a | b | Văn nói |\n\nHết.")
        self.assertEqual((len(rows), errors), (1, []))

    def test_a_row_with_too_many_or_too_few_cells_is_an_error_not_a_guess(self):
        _, errors = vocab.parse_table("| a | b | c | d | e | f |\n| only | two |\n")
        self.assertEqual(len(errors), 2)
        self.assertIn("line 1", errors[0])

    def test_a_json_backup_is_read_and_its_ids_are_ignored(self):
        rows, errors = vocab.parse_input(json.dumps([{"id": 7, "term": "dodge", "meaning": "m", "register": "Văn nói", "repo": True}]))
        self.assertEqual(errors, [])
        self.assertEqual(rows[0].values, {"term": "dodge", "meaning": "m", "register": "Văn nói"})

    def test_a_json_field_nobody_knows_is_an_error(self):
        _, errors = vocab.parse_input(json.dumps([{"term": "a", "meaning": "b", "colour": "red"}]))
        self.assertTrue(any("colour" in e for e in errors), errors)

    def test_json_that_is_not_an_array_of_objects_is_an_error(self):
        self.assertTrue(vocab.parse_input("[1]")[1])
        self.assertTrue(vocab.parse_input("[{")[1])


class EntryRuleTests(unittest.TestCase):
    def errors(self, **changes) -> list[str]:
        return vocab.entry_problems({**ENTRY, **changes}, "x")[0]

    def test_a_complete_entry_has_no_problem(self):
        self.assertEqual(vocab.entry_problems(ENTRY, "x"), ([], []))

    def test_a_register_outside_the_five_is_an_error(self):
        self.assertTrue(any("register" in e for e in self.errors(register="Formal")))

    def test_a_required_field_that_is_empty_is_an_error(self):
        for name in ("term", "meaning", "source"):
            self.assertTrue(any(f"{name} is missing" in e for e in self.errors(**{name: ""})), name)

    def test_a_field_over_its_limit_is_an_error_so_no_passage_gets_stored(self):
        self.assertTrue(any("limit 300" in e for e in self.errors(note="x" * 301)))
        self.assertEqual(self.errors(note="x" * 300), [])
        self.assertTrue(any("limit 80" in e for e in self.errors(term="x" * 81)))

    def test_a_pipe_or_line_break_would_break_the_table_and_is_an_error(self):
        for text in ("a | b", "a\nb", "a\tb"):
            self.assertTrue(self.errors(note=text), repr(text))

    def test_an_unknown_field_is_an_error(self):
        self.assertTrue(any("'id'" in e for e in self.errors(id=1)))

    def test_a_date_must_be_a_real_iso_date(self):
        self.assertEqual(self.errors(added="2026-10-16"), [])
        self.assertTrue(self.errors(added="16/10/2026"))
        self.assertTrue(self.errors(added="2026-13-40"))

    def test_a_language_that_disagrees_with_the_script_is_only_a_warning(self):
        errors, warnings = vocab.entry_problems({**ENTRY, "lang": "JA"}, "x")
        self.assertEqual(errors, [])
        self.assertTrue(any("reads as EN" in w for w in warnings))

    def test_the_same_word_twice_is_an_error_even_spelled_differently(self):
        errors, _ = vocab.store_problems([ENTRY, {**ENTRY, "term": " DODGE "}])
        self.assertTrue(any("the same word" in e for e in errors), errors)

    def test_two_senses_of_one_headword_are_a_warning(self):
        _, warnings = vocab.store_problems([{**ENTRY, "term": "trigger (v)"}, {**ENTRY, "term": "trigger (n)"}])
        self.assertTrue(any("same headword" in w for w in warnings), warnings)

    def test_one_source_spelled_two_ways_is_a_warning(self):
        _, warnings = vocab.store_problems([ENTRY, {**OTHER, "source": "ch.2 mirroring"}])
        self.assertTrue(any("spelled several ways" in w for w in warnings), warnings)


class StoreFileTests(Workspace):
    def test_loading_and_saving_an_untouched_page_changes_no_byte(self):
        self.make([ENTRY, OTHER])
        before = self.page.read_bytes()
        vocab.Store.load(self.page).save()
        self.assertEqual(self.page.read_bytes(), before)

    def test_the_real_page_round_trips_byte_for_byte(self):
        target = self.dir / "real.html"
        shutil.copy(REAL_PAGE, target)
        before = target.read_bytes()
        vocab.Store.load(target).save()
        self.assertEqual(target.read_bytes(), before)

    def test_a_page_with_windows_line_ends_keeps_them(self):
        self.make([ENTRY], newline="\r\n")
        store = vocab.Store.load(self.page)
        store.entries.append(OTHER)
        store.save()
        data = self.page.read_bytes()
        self.assertEqual(data.count(b"\r\n"), data.count(b"\n"))
        self.assertEqual(self.stored(), [ENTRY, OTHER])

    def test_everything_outside_the_markers_is_left_alone(self):
        self.make([ENTRY])
        before = self.page.read_text(encoding="utf-8")
        store = vocab.Store.load(self.page)
        store.entries.append(OTHER)
        store.save()
        after = self.page.read_text(encoding="utf-8")
        cut = lambda text: (text[:text.index(vocab.BEGIN)], text[text.index(vocab.END):])
        self.assertEqual(cut(before), cut(after))

    def test_each_entry_is_one_line_ending_in_a_comma_so_a_new_word_is_a_one_line_diff(self):
        block = vocab.render_block([ENTRY, OTHER]).splitlines()
        self.assertEqual(len([line for line in block if line.startswith("  {")]), 2)
        self.assertTrue(all(line.endswith("},") for line in block if line.startswith("  {")))

    def test_text_that_could_end_the_script_is_escaped(self):
        block = vocab.render_block([{**ENTRY, "note": "</script><!-- x"}])
        self.assertNotIn("</script>", block)
        self.assertNotIn("<!--", block)
        self.assertEqual(vocab.Store.load(self.make([{**ENTRY, "note": "</script><!-- x"}])).entries[0]["note"], "</script><!-- x")

    def test_a_missing_or_doubled_marker_is_an_error_naming_the_file(self):
        self.make([ENTRY])
        text = self.page.read_text(encoding="utf-8")
        for broken in (text.replace(vocab.END, "// end"), text + "\n" + vocab.render_block([])):
            self.page.write_text(broken, encoding="utf-8")
            with self.assertRaises(vocab.StoreError) as raised:
                vocab.Store.load(self.page)
            self.assertIn("page.html", str(raised.exception))

    def test_a_block_that_is_not_json_is_an_error(self):
        self.make([ENTRY])
        self.page.write_text(self.page.read_text(encoding="utf-8").replace('"term"', "term"), encoding="utf-8")
        with self.assertRaises(vocab.StoreError):
            vocab.Store.load(self.page)

    def test_a_key_named_twice_in_one_entry_is_an_error(self):
        self.make([ENTRY])
        text = self.page.read_text(encoding="utf-8").replace('"lang": "EN"}', '"lang": "EN", "lang": "JA"}')
        self.page.write_text(text, encoding="utf-8")
        with self.assertRaises(vocab.StoreError):
            vocab.Store.load(self.page)

    def test_a_file_that_is_missing_is_reported_not_raised(self):
        code, out = self.run_cli("check")
        self.assertEqual(code, 2)
        self.assertIn("cannot be read", out)


class AddTests(Workspace):
    def test_new_words_are_appended_with_the_batch_date_and_a_detected_language(self):
        self.make([ENTRY])
        path = self.batch(TABLE_HEAD + "| 腑に落ちる (ふにおちる) | Thấm | văn viết | note | |\n| stalemate | Thế bế tắc | Văn viết | | |\n")
        code, out = self.run_cli("add", "--from", path, "--source", "Ch.3 Tactical Empathy", "--date", "2026-10-16")
        self.assertEqual(code, 0, out)
        stored = self.stored()
        self.assertEqual([e["term"] for e in stored], ["dodge", "腑に落ちる (ふにおちる)", "stalemate"])
        self.assertEqual(stored[1], {"term": "腑に落ちる (ふにおちる)", "meaning": "Thấm", "register": "Văn viết", "note": "note",
                                     "source": "Ch.3 Tactical Empathy", "lang": "JA", "added": "2026-10-16"})
        self.assertEqual(stored[0], ENTRY)  # what was stored before is not touched

    def test_a_dry_run_writes_nothing(self):
        self.make([ENTRY])
        before = self.page.read_bytes()
        code, out = self.run_cli("add", "--from", self.batch(TABLE_HEAD + "| a | b | Văn nói | | s |\n"), "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("dry run", out)
        self.assertEqual(self.page.read_bytes(), before)

    def test_adding_the_same_batch_twice_changes_nothing(self):
        self.make()
        path = self.batch(TABLE_HEAD + "| a | b | Văn nói | n | s |\n| c | d | Văn viết | n | s |\n")
        self.run_cli("add", "--from", path, "--date", "2026-10-16")
        first = self.page.read_bytes()
        code, out = self.run_cli("add", "--from", path, "--date", "2026-10-20")
        self.assertEqual(code, 0)
        self.assertIn("2 already stored", out)
        self.assertEqual(self.page.read_bytes(), first)

    def test_one_invalid_row_writes_nothing_at_all(self):
        self.make([ENTRY])
        before = self.page.read_bytes()
        path = self.batch(TABLE_HEAD + "| good | fine | Văn nói | | s |\n| bad | fine | Formal | | s |\n")
        code, out = self.run_cli("add", "--from", path)
        self.assertEqual(code, 1)
        self.assertIn("ERROR", out)
        self.assertIn("register", out)
        self.assertEqual(self.page.read_bytes(), before)

    def test_a_row_without_a_source_and_no_default_source_is_an_error(self):
        self.make()
        code, out = self.run_cli("add", "--from", self.batch(TABLE_HEAD + "| a | b | Văn nói | | |\n"))
        self.assertEqual(code, 1)
        self.assertIn("source is missing", out)

    def test_a_register_left_empty_is_an_error_not_a_silent_default(self):
        self.make()
        code, out = self.run_cli("add", "--from", self.batch("| a | b | | | s |\n"))
        self.assertEqual(code, 1)
        self.assertIn("register", out)

    def test_the_same_word_twice_in_one_batch_is_an_error(self):
        self.make()
        path = self.batch(TABLE_HEAD + "| a | b | Văn nói | | s |\n| A | c | Văn viết | | s |\n")
        code, out = self.run_cli("add", "--from", path)
        self.assertEqual(code, 1)
        self.assertIn("appears twice", out)

    def test_a_word_stored_with_other_content_is_reported_and_left_alone(self):
        self.make([ENTRY])
        before = self.page.read_bytes()
        path = self.batch(TABLE_HEAD + "| dodge | Một nghĩa khác | Văn nói | | Ch.9 |\n| new | n | Văn nói | | s |\n")
        code, out = self.run_cli("add", "--from", path, "--date", "2026-10-16")
        self.assertEqual(code, 0)
        self.assertIn("! dodge is stored with different content", out)
        self.assertIn("1 differ", out)
        stored = self.stored()
        self.assertEqual(stored[0], ENTRY)
        self.assertEqual([e["term"] for e in stored], ["dodge", "new"])
        self.assertNotEqual(self.page.read_bytes(), before)  # the new word still went in

    def test_update_replaces_the_differing_word_and_keeps_when_it_was_added(self):
        self.make([{**ENTRY, "added": "2026-10-01"}])
        path = self.batch("| dodge | Né tránh (đã sửa) | Văn nói | | Ch.2 Mirroring |\n")
        code, out = self.run_cli("add", "--from", path, "--update", "--date", "2026-10-16")
        self.assertEqual(code, 0, out)
        (entry,) = self.stored()
        self.assertEqual((entry["meaning"], entry["register"], entry["added"]), ("Né tránh (đã sửa)", "Văn nói", "2026-10-01"))

    def test_a_second_sense_of_a_stored_headword_is_added_with_a_warning(self):
        self.make([{**ENTRY, "term": "trigger (v)"}])
        code, out = self.run_cli("add", "--from", self.batch("| trigger (n) | Cò súng | Trung tính | | s |\n"))
        self.assertEqual(code, 0)
        self.assertIn("shares its headword", out)
        self.assertEqual(len(self.stored()), 2)

    def test_a_kana_reading_makes_no_new_word(self):
        self.make([{**ENTRY, "term": "逸脱 (いつだつ)", "lang": "JA"}])
        code, out = self.run_cli("add", "--from", self.batch("| 逸脱 | Sai lệch | Văn viết | | s |\n"))
        self.assertEqual(code, 0)
        self.assertEqual(len(self.stored()), 1)
        self.assertIn("1 differ", out)

    def test_input_with_no_rows_is_an_error(self):
        self.make()
        code, out = self.run_cli("add", "--from", self.batch("nothing here\n"))
        self.assertEqual(code, 1)
        self.assertIn("no table rows", out)

    def test_a_word_without_a_note_is_added_but_the_report_says_so(self):
        self.make()
        code, out = self.run_cli("add", "--from", self.batch("| a | b | Văn nói | | s |\n"))
        self.assertEqual(code, 0)
        self.assertIn("WARN", out)
        self.assertIn("no note", out)
        self.assertEqual(len(self.stored()), 1)

    def test_a_bad_date_is_refused(self):
        self.make()
        code, _ = self.run_cli("add", "--from", self.batch("| a | b | Văn nói | | s |\n"), "--date", "yesterday")
        self.assertEqual(code, 2)

    def test_a_json_backup_is_folded_in_like_a_table(self):
        self.make([ENTRY])
        backup = json.dumps([{"id": 3, **ENTRY}, {"id": 4, **OTHER, "term": "brand new"}], ensure_ascii=False)
        code, out = self.run_cli("add", "--from", self.batch(backup, "backup.json"), "--date", "2026-10-16")
        self.assertEqual(code, 0, out)
        self.assertEqual([e["term"] for e in self.stored()], ["dodge", "brand new"])

    def test_the_table_the_page_copies_is_read_back_unchanged(self):
        self.make()
        table = TABLE_HEAD + "| dodge | Né tránh, lách qua | Trung tính | dodge a question | Ch.2 Mirroring |\n"
        self.run_cli("add", "--from", self.batch(table), "--date", "2026-10-16")
        code, out = self.run_cli("list", "--format", "md")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), table.strip())


class OtherCommandTests(Workspace):
    def test_check_passes_a_valid_store_and_fails_each_kind_of_damage(self):
        self.make([ENTRY, OTHER])
        self.assertEqual(self.run_cli("check")[0], 0)
        self.make([ENTRY, {**OTHER, "register": "Formal"}])
        self.assertEqual(self.run_cli("check")[0], 1)
        self.make([ENTRY, {**ENTRY}])
        self.assertEqual(self.run_cli("check")[0], 1)

    def test_check_fails_a_page_whose_register_colours_drifted_from_the_five(self):
        self.make([ENTRY])
        self.page.write_text(self.page.read_text(encoding="utf-8").replace('"Văn nói": { bg: "#fff" },\n', ""), encoding="utf-8")
        code, out = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("REGISTER_COLORS", out)

    def test_check_fails_a_block_edited_by_hand_and_fmt_repairs_it(self):
        self.make([ENTRY])
        self.page.write_text(self.page.read_text(encoding="utf-8").replace('{"term": "dodge", "meaning"', '{"meaning"', 1)
                             .replace('"Né tránh, lách qua",', '"Né tránh, lách qua", "term": "dodge",', 1), encoding="utf-8")
        code, out = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("fmt", out)
        self.assertEqual(self.run_cli("fmt")[0], 0)
        self.assertEqual(self.run_cli("check")[0], 0)

    def test_fmt_refuses_an_invalid_store(self):
        self.make([{**ENTRY, "register": "Formal"}])
        before = self.page.read_bytes()
        self.assertEqual(self.run_cli("fmt")[0], 1)
        self.assertEqual(self.page.read_bytes(), before)

    def test_find_exits_zero_when_the_word_is_stored_and_one_when_it_is_not(self):
        self.make([ENTRY, OTHER])
        code, out = self.run_cli("find", "  DODGE ")
        self.assertEqual(code, 0)
        self.assertIn("dodge", out)
        code, out = self.run_cli("find", "nowhere")
        self.assertEqual(code, 1)
        self.assertIn("is not stored", out)

    def test_find_looks_in_meanings_and_notes_only_when_asked(self):
        self.make([ENTRY])
        self.assertEqual(self.run_cli("find", "question")[0], 1)
        self.assertEqual(self.run_cli("find", "-a", "question")[0], 0)

    def test_list_new_is_the_latest_batch_only(self):
        self.make([{**ENTRY, "added": "2026-10-01"}, {**OTHER, "added": "2026-10-16"}, {**ENTRY, "term": "old"}])
        code, out = self.run_cli("list", "--new")
        self.assertEqual(code, 0)
        self.assertIn("stalemate", out)
        self.assertNotIn("dodge", out)
        self.assertNotIn("old", out)

    def test_list_filters_by_language_and_by_a_source_however_it_is_spelled(self):
        self.make([ENTRY, {**OTHER, "term": "がたがた", "lang": "JA", "source": "Nhật 1"}])
        self.assertEqual(self.run_cli("list", "--lang", "JA")[1].count("\n"), 1)
        self.assertIn("がたがた", self.run_cli("list", "--source", "nhật  1")[1])

    def test_stats_counts_by_language_register_and_batch(self):
        self.make([{**ENTRY, "added": "2026-10-16"}, OTHER])
        code, out = self.run_cli("stats")
        self.assertEqual(code, 0)
        self.assertIn("words: 2  latest batch: 2026-10-16", out)
        self.assertIn("lang: EN 2", out)

    def test_remove_deletes_by_exact_word_and_refuses_an_unknown_one_without_writing(self):
        self.make([ENTRY, OTHER])
        before = self.page.read_bytes()
        code, out = self.run_cli("remove", "stalemate", "unknown")
        self.assertEqual(code, 1)
        self.assertIn("nothing written", out)
        self.assertEqual(self.page.read_bytes(), before)
        self.assertEqual(self.run_cli("remove", " Stalemate ")[0], 0)
        self.assertEqual([e["term"] for e in self.stored()], ["dodge"])

    def test_remove_dry_run_writes_nothing(self):
        self.make([ENTRY])
        before = self.page.read_bytes()
        self.assertEqual(self.run_cli("remove", "dodge", "--dry-run")[0], 0)
        self.assertEqual(self.page.read_bytes(), before)

    def test_bad_arguments_exit_two(self):
        self.make()
        self.assertEqual(self.run_cli("nonsense")[0], 2)


class RealStoreTests(unittest.TestCase):
    def test_the_vocabulary_page_in_the_repository_passes_its_own_check(self):
        store = vocab.Store.load(REAL_PAGE)
        errors, _ = vocab.store_problems(store.entries)
        self.assertEqual(errors, [])
        self.assertTrue(store.is_canonical(), "run `python3 scripts/vocab.py fmt`")
        self.assertEqual(store.page_registers(), list(vocab.REGISTERS))

    def test_the_repository_words_keep_the_forty_five_the_owner_started_with(self):
        terms = {vocab.term_key(e["term"]) for e in vocab.Store.load(REAL_PAGE).entries}
        for word in ("がたがた", "逸脱", "laughably simple", "critical (= important)", "mirror (v)"):
            self.assertIn(vocab.term_key(word), terms, word)

    def test_the_page_has_no_other_data_block_or_copy_of_the_words(self):
        text = REAL_PAGE.read_text(encoding="utf-8")
        self.assertEqual(text.count("const SEED"), 1)
        self.assertEqual(text.count(vocab.BEGIN), 1)


def chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch().close()
        return True
    except Exception:
        return False


V1_KEY, V2_KEY = "vocab-linh-standalone-v1", "vocab-linh-standalone-v2"
SAMPLE_KEYS = ["Elaborate   ON", "ＡＢＣ", "逸脱 (いつだつ)", "逸脱（いつだつ）", "trigger (v)", "critical (= important)", "  x  "]


@unittest.skipUnless(chromium_available(), "Chromium not installed")
class PageTests(Workspace):
    """The page in a real browser: what it shows, what it keeps, and what it refuses."""

    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def make_page(self, entries: list[dict]) -> Path:
        """A copy of the real page (its code) holding these words instead of the repository's."""
        shutil.copy(REAL_PAGE, self.page)
        store = vocab.Store.load(self.page)
        store.entries = copy.deepcopy(entries)
        store.save()
        return self.page

    def open(self, page_path: Path | None = None, *, v1=None, v2=None):
        """Open a page with this browser storage; the storage is written once, so a reload keeps the page's own changes."""
        context = self.browser.new_context()
        self.addCleanup(context.close)
        seed = {V1_KEY: v1, V2_KEY: v2}
        context.add_init_script(
            "(() => { const seed = %s; if (localStorage.getItem('seeded')) return; localStorage.setItem('seeded', '1');"
            " for (const k in seed) if (seed[k] !== null) localStorage.setItem(k, JSON.stringify(seed[k])); })();" % json.dumps(seed))
        page = context.new_page()
        self.errors: list[str] = []
        page.on("pageerror", lambda e: self.errors.append(str(e)))
        page.on("console", lambda m: self.errors.append(m.text) if m.type == "error" else None)
        page.goto((page_path or REAL_PAGE).as_uri())
        return page

    def local_words(self, page) -> list[dict]:
        return json.loads(page.evaluate(f"localStorage.getItem('{V2_KEY}')"))["local"]

    def test_every_repository_word_is_listed_and_the_page_raises_no_error(self):
        page = self.open()
        self.assertEqual(page.locator("tbody tr").count(), len(vocab.Store.load(REAL_PAGE).entries))
        self.assertEqual(self.errors, [])

    def test_words_the_old_version_kept_move_to_this_machine_and_the_old_copy_stays(self):
        old = [{"id": 1, "term": "elaborate on", "meaning": "x", "register": "Trung tính", "note": "", "source": "s", "lang": "EN"},
               {"id": 99, "term": "brand new word", "meaning": "từ của tôi", "register": "Văn nói", "note": "", "source": "tay", "lang": "EN"}]
        page = self.open(v1=old)
        self.assertEqual([w["term"] for w in self.local_words(page)], ["brand new word"])
        self.assertEqual(json.loads(page.evaluate(f"localStorage.getItem('{V1_KEY}')")), old)
        self.assertEqual(page.locator(".mark-local").count(), 1)
        self.assertEqual(page.locator("tbody tr").count(), len(vocab.Store.load(REAL_PAGE).entries) + 1)
        self.assertEqual(self.errors, [])

    def test_only_a_word_kept_on_this_machine_can_be_deleted_from_the_page(self):
        page = self.open(v2={"version": 2, "local": [dict(ENTRY, term="mine")]})
        self.assertEqual(page.locator(".del-btn").count(), 1)
        page.locator(".del-btn").click()
        self.assertEqual(self.local_words(page), [])
        self.assertEqual(page.locator(".del-btn").count(), 0)

    def test_a_local_word_the_repository_has_since_gained_is_dropped_from_the_local_list(self):
        self.make_page([ENTRY])
        page = self.open(self.page, v2={"version": 2, "local": [dict(ENTRY, term="  DODGE "), dict(OTHER)]})
        self.assertEqual([w["term"] for w in self.local_words(page)], ["stalemate"])

    def test_the_latest_batch_is_marked_new_and_the_filter_shows_only_it(self):
        self.make_page([{**ENTRY, "added": "2026-10-01"}, {**OTHER, "added": "2026-10-16"}, {**OTHER, "term": "plain"}])
        page = self.open(self.page)
        self.assertEqual(page.locator(".mark-new").count(), 1)
        page.click("#only-new")
        self.assertEqual(page.locator("tbody tr").count(), 1)
        self.assertIn("stalemate", page.inner_text("tbody"))
        self.assertEqual(self.errors, [])

    def test_nothing_is_marked_new_when_the_repository_has_no_dated_batch(self):
        self.make_page([ENTRY])
        page = self.open(self.page)
        self.assertEqual(page.locator(".mark-new").count(), 0)
        self.assertEqual(page.locator("#only-new").count(), 0)

    def test_adding_by_hand_refuses_a_word_the_repository_already_has(self):
        self.make_page([ENTRY])
        page = self.open(self.page)
        page.click("text=Thêm tay")
        fields = page.locator(".field-input")
        fields.nth(0).fill("  Dodge ")
        fields.nth(1).fill("khác")
        page.click("text=Lưu từ mới")
        self.assertEqual(self.local_words(page), [])
        self.assertIn("đã có", page.inner_text(".primary-btn"))

    def test_adding_by_hand_keeps_a_new_word_on_this_machine(self):
        self.make_page([ENTRY])
        page = self.open(self.page)
        page.click("text=Thêm tay")
        page.locator(".field-input").nth(0).fill("brand new")
        page.locator(".field-input").nth(1).fill("mới tinh")
        page.click("text=Lưu từ mới")
        self.assertEqual([w["term"] for w in self.local_words(page)], ["brand new"])

    def test_the_paste_import_skips_words_already_stored_and_says_how_many(self):
        self.make_page([ENTRY])
        page = self.open(self.page)
        page.click("text=Cập nhật từ vựng")
        page.click("summary")
        page.locator("textarea").fill(TABLE_HEAD + "| dodge | m | Văn nói | | s |\n| fresh | m | 🗣 Văn nói | n | s |\n")
        page.click("#paste-import")
        self.assertIn("1 từ trùng", page.inner_text("#paste-import"))
        self.assertEqual([(w["term"], w["register"]) for w in self.local_words(page)], [("fresh", "Văn nói")])

    def test_the_table_the_page_copies_is_what_the_command_line_reads(self):
        local = [dict(ENTRY, term="mine one"), dict(OTHER, term="腑に落ちる (ふにおちる)", note="a | b\nc")]
        page = self.open(v2={"version": 2, "local": local})
        table = page.evaluate("wordsAsTable(localWords())")
        rows, errors = vocab.parse_table(table)
        self.assertEqual(errors, [])
        self.assertEqual([r.values["term"] for r in rows], ["mine one", "腑に落ちる (ふにおちる)"])
        self.assertEqual(rows[1].values["note"], "a / b c")

    def test_the_page_and_the_script_agree_on_what_makes_two_words_the_same(self):
        page = self.open()
        for sample in SAMPLE_KEYS:
            self.assertEqual(page.evaluate("(s) => termKey(s)", sample), vocab.term_key(sample), repr(sample))
        for sample in ("逸脱 (いつだつ)", "skill set", "がたがた", "ウェブ"):
            self.assertEqual(page.evaluate("(s) => detectLang(s)", sample), vocab.detect_lang(sample), sample)

    def test_the_registers_the_page_colours_are_the_ones_the_script_accepts(self):
        page = self.open()
        self.assertEqual(page.evaluate("Object.keys(REGISTER_COLORS)"), list(vocab.REGISTERS))

    def test_the_backup_holds_only_this_machines_words_and_restoring_it_skips_stored_ones(self):
        self.make_page([ENTRY])
        page = self.open(self.page, v2={"version": 2, "local": [dict(OTHER)]})
        with page.expect_download() as download:
            page.click("text=Sao lưu")
        saved = json.loads(Path(download.value.path()).read_text(encoding="utf-8"))
        self.assertEqual([w["term"] for w in saved], ["stalemate"])
        # the same backup, now with a stored word added, restored into an empty browser
        backup = self.dir / "backup.json"
        backup.write_text(json.dumps(saved + [ENTRY]), encoding="utf-8")
        fresh = self.open(self.page)
        fresh.once("dialog", lambda dialog: (self.__setattr__("dialog", dialog.message), dialog.accept()))
        fresh.set_input_files("input[type=file]", str(backup))
        fresh.wait_for_function(f"localStorage.getItem('{V2_KEY}').includes('stalemate')")
        self.assertEqual([w["term"] for w in self.local_words(fresh)], ["stalemate"])
        self.assertIn("1 từ đã có", self.dialog)


if __name__ == "__main__":
    unittest.main()
