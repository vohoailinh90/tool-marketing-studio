---
name: vocab-study
description: Explain English and Japanese words, phrases and passages for the owner's vocabulary study, then fold the new words into the vocabulary page in the repository (vocab/vocab_standalone.html) with scripts/vocab.py. Use when the user pastes a word, phrase or passage and asks what it means, "giải thích từ", "phân tích đoạn văn", "từ vựng", "tổng hợp từ vựng", "thêm vào từ vựng", "xóa từ", "語彙", "単語", or asks whether a word is already stored.
---

# Vocabulary study

Content work, not a routed software requirement: the main session does it, with no `route.py`
and no subagents; the checks below are the verification. Changing the page's code or
`scripts/vocab.py` *is* a software requirement and goes through the routing flow in `CLAUDE.md`.

The owner is a Vietnamese speaker learning English (today from *Never Split the Difference*, a
negotiation book) and Japanese. Explain **in Vietnamese**; the word itself stays in its own language.
Two phases, and the line between them is the point:

1. **Explain** — the owner reads. Nothing is written to the repository.
2. **Aggregate** — only when the owner asks ("tổng hợp từ vựng"). The words explained so far go
   into `vocab/vocab_standalone.html`, then commit and push.

`docs/vocab-study.md` has the whole picture (store format, the page, commands).

## 1. Explain — writes nothing

Before explaining a word, look it up: `python3 scripts/vocab.py find "<term>"`
(`-a` also searches meanings and notes, which is how you find the near-synonyms it should be
contrasted with). If it is stored, show the stored entry and add only what is new — another sense,
another register, a better contrast.

### A word or phrase

In Vietnamese, in this order, short enough to read on one screen:

- **Nghĩa in this context first**; other senses only when they could be confused with it.
- **Văn phong**: say which of the five it is and why (§2).
- **Nuance against near-synonyms** the owner already has (`rattled` vs `flustered`), and the
  spoken ↔ written counterpart (`Văn nói: partner / sidekick`).
- **Pattern and collocations** (`end up + V-ing`, `dodge a question`) and one natural example with
  its Vietnamese gloss.
- Japanese: the reading in hiragana, why kanji or kana, the politeness level, and the 敬語 or casual
  counterpart when there is one.

### A passage

1. **Gist** — two or three sentences: what the passage argues.
2. **Walk through it** chunk by chunk. Explain the expressions that carry the meaning: the sense
   *in this context* and why the author chose it over a plainer word; idioms, phrasal verbs,
   collocations; grammar a Vietnamese reader tends to misread. Translate a sentence only where
   that makes it clearer — not the whole passage, unless asked.
3. **Từ/cụm đáng lưu** — a table in the exact 5-column format of §3, usually 6–15 rows. Leave out
   what the owner plainly knows, and what is already stored (name those in one line, from `find`).
   Quality over completeness.
4. One closing line: nothing is stored until the owner says *"tổng hợp từ vựng"*.

### Accuracy

- Say so when you are unsure of a nuance or a register. Never invent a usage, an etymology (give
  one only when certain, as `stalemate` ← chess), or a quotation from the book.
- Examples are your own short sentences. Quote the owner's passage in **at most ~12 words**, and only
  inside a note: a book's text does not belong in this repository (the checker caps field lengths).
- Gloss a figurative use by what it means *there* (`step all over her idea`), not by its literal
  dictionary sense.

## 2. What an entry is

| Field | Rule | Example in the store |
|---|---|---|
| `term` | The form to look up. English: base form, `someone`/`something` spelled out, `+ V-ing` shown, `(v)` only to fix the part of speech. Japanese: `漢字 (よみ)`, onomatopoeia in kana. ≤ 80 characters | `逸脱 (いつだつ)`, `end up + V-ing` |
| `meaning` | Vietnamese; the sense in the passage first, one to three glosses separated by `, ` or ` / `. ≤ 200 | `Hiệu quả một cách kỳ lạ, khó giải thích` |
| `register` | **Exactly one of** `Văn nói` (spoken, informal) · `Văn viết` (written, formal) · `Trung tính` (neutral) · `Chuyên nghiệp` (business, professional) · `Chuyên ngành` (a field's technical term). Decide by how the item is used, not by how your explanation reads | `Văn nói` for `blurt out`… |
| `note` | One line the meaning cannot give: a contrast (`Mạnh hơn rattled`), the other register (`Văn nói: partner`), a collocation or a short example in quotes. ≤ 300 | `'Hit him with the numbers' = đưa thẳng số liệu ra` |
| `source` | Where it came from, spelled as already stored (`python3 scripts/vocab.py stats` lists them): `Ch.<n> <Title>` for a book chapter, a lesson or topic name otherwise | `Ch.2 Mirroring` |
| `lang` | `EN` or `JA`, detected from the term's script — never typed by hand | |
| `added` | The batch date; set by `add`, never by you | |

No `|`, line break or tab inside a field. A field over its limit is shortened by rewriting it
tighter, never by cutting it mid-sentence.

## 3. Aggregate — when the owner asks

1. **Collect** every word or phrase you explained in *this conversation* since the last aggregation
   (or the start). The conversation is the only ledger; a word already stored is skipped, so
   collecting twice is harmless. Leave out what the owner said they know or to skip. If earlier turns
   were compacted away and you cannot tell what was explained, say so and ask for the list — never guess.
2. **Source** — one label for the passage or chapter, spelled as already stored. Unknown: ask once.
3. **Write the batch** as a table to a scratch file outside the repository, one complete entry per row:

   ```
   | Từ/Cụm | Nghĩa tiếng Việt | Văn phong | Ghi chú | Nguồn |
   |---|---|---|---|---|
   | elaborate on | Giải thích thêm, mở rộng về | Trung tính | 'Could you elaborate on that?' | Ch.3 Tactical Empathy |
   ```

4. **Dry run**, then read the report line by line:

   ```bash
   python3 scripts/vocab.py add --from <batch.md> --source "<source>" --dry-run
   ```

   - `ERROR` — a row is invalid; nothing was written. Fix the row.
   - `!` *differs* — the word is stored with other content and was skipped. Compare, then drop the
     row (keep the stored one) or replace it. `--update` replaces **every** differing word in its
     file, so run it on a file holding only the rows you mean to replace.
   - `~` *same headword* — a second sense (keep) or the same word (drop the row).
   - `=` already stored — fine.
5. **Run it for real** (the same command without `--dry-run`), then `python3 scripts/vocab.py check`
   must report 0 errors.
6. **Commit and push** — only `vocab/vocab_standalone.html`:
   `vocab: add <n> words (<source>)`, `git push -u origin <session branch>`. Open a pull request only
   when the owner asks; then `CLAUDE.md`'s *Pull request lifecycle* applies unchanged.
7. **Report in Vietnamese**: how many were added, skipped and held for a decision; the added words
   (`python3 scripts/vocab.py list --new --format md`); the branch the page is on. Say plainly that the
   page reaches `main` only after a pull request is merged.

## 4. Other requests

| The owner says | You run |
|---|---|
| "xóa từ X" | `python3 scripts/vocab.py remove "X"` (the page cannot delete repository words), then check, commit, push |
| "sửa nghĩa / văn phong của X" | a one-row file, `add --update`, check, commit, push |
| the table the page copies for "từ chỉ có trên máy này" | steps 3–7; its `Nguồn` column already holds the sources |
| a `vocab_local_backup.json` or an old `vocab_backup.json` | `add --from <file> --dry-run`, then for real; words already stored are skipped |
| "đã học bao nhiêu từ", "lô mới nhất" | `stats`, `list --new` |

## 5. Never

- Never edit the data block of `vocab/vocab_standalone.html` by hand: `scripts/vocab.py` owns it, and
  `check` fails a block it did not write.
- Never commit a passage, a screenshot of the book, or the owner's private notes.
- Never mark a word known or learned on the owner's behalf: the page has no such state, by design.
