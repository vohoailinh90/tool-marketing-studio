---
name: tool-campaign
description: Create or extend a marketing campaign for one of the owner's tools — read the tool's repository, write its fact brief and per-language positioning, write complete posts in Vietnamese, Japanese and English (never sentence-by-sentence translations), render and visually check the images, and prepare the demand-validation survey. Use when the user asks to market, introduce, promote or write posts for a tool, "viết bài giới thiệu tool", "quảng bá", "ツールの紹介投稿", or to add a new tool to the studio.
---

# Tool campaign

Content work, not a routed software requirement: the main session does it, and the
checks below are the verification. The owner approves and publishes — never you.

## 1. Facts first

1. Read the tool's repository (README, CLAUDE.md, what it actually does). Attach it with
   `add_repo` (read) and clone it if it is not in the session.
2. New tool: `python3 studio.py new <slug> --name "<Name>" --repo <owner/repo>`.
3. Fill `tools/<slug>/brief.yaml` with **facts only**: requirements, features (each traceable
   to the README), `claims` with `evidence` and `verified`, `limitations`,
   `story_to_confirm` (anything about the author's own story — the owner must confirm it),
   `commercial_readiness`.

## 2. Positioning per language

Write `tools/<slug>/positioning/{vi,ja,en}.yaml` — each for its own audience:
- **vi**: Vietnamese office workers (in Vietnam or at Japanese/foreign companies), Facebook on a phone.
- **ja**: people at Japanese companies (幹事, 総務, team leads); polite です・ます, empathy first.
- **en**: international teams; crisp and friendly.
Use the words that audience uses (`vocabulary`), not translated ones.

## 3. Posts

Six slots work for a first campaign: `01-pain`, `02-story`, `03-how-it-works`,
`04-before-after`, `05-survey`, `06-faq` (purposes in `mkt/ai.py` `SLOTS`). For each slot and
language, one complete file `campaigns/<slug>/posts/<lang>/<slot>.yaml`.

- Layouts and their fields: `LAYOUT_DOCS` in `mkt/layouts.py`. One idea per slide, ≤ ~30 words.
- Hook first; end every post with a question or a call to action.
- No URL anywhere: `{link}` in `first_comment` only. Status stays `draft`.
- Numbers only from the brief; estimates say so. Keep the same numbers across languages.

## 4. Check, render, look

```bash
python3 studio.py check <slug>          # 0 errors required
python3 studio.py render <slug>         # no overflow warnings
```
Then **look at the images** (Read the PNGs, or build a contact sheet): text fits, emphasis
lands on the right words, nothing reads as a literal translation.

## 5. Demand validation

Adapt `research/survey-template.md` for the tool (each language complete), and remind the
owner to set `links.survey` in `campaign.yaml` — posts cannot be approved while it is a
placeholder. After posting: `studio.py history`, feedback, metrics, then `studio.py insights`.

## Report

List the files written, the check result, anything the owner must confirm (story points,
unverified claims, the survey link), and what they do next in the app.
