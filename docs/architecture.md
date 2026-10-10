# Architecture

## Engine (`mkt/`)

| Module | Role |
|---|---|
| `model.py` | Loads `studio.yaml`, briefs, positioning, campaigns, posts (`posts/<lang>/<id>.yaml`) |
| `check.py` | Every computable rule: layouts and fields, statuses, no URL in post text, image paths confined to the campaign/tool folder, platform limits (X weighted length), TODO/placeholder links blocking ready posts, cross-language number parity, unsourced numbers for AI drafts |
| `layouts.py`, `page.py`, `theme.css`, `text.py` | 15 slide layouts → HTML; every string escaped; only `**hl**` / `~~strike~~` marks |
| `render.py`, `fonts.py` | HTML per slide → Playwright Chromium → PNG; text auto-shrinks to 0.7 and overflow is reported; webfonts cached in `.fonts/` and served by route interception |
| `links.py` | Tracked link per post × language × platform (utm or Google Forms `{source}`), QR via segno |
| `approvals.py` | `content_sha` over everything the audience sees; approval valid only while the hash matches |
| `publish.py` | Manual packs (zip); Facebook Page publisher; smoke check; ledger with `pending → done/failed` written before the first remote call; O_EXCL publish lock; exact-value token redaction |
| `history.py`, `feedback.py` | Posting history across campaigns, multiple manual postings per platform; comments scanned from the Page or pasted (stored without names, gitignored) |
| `metrics.py`, `survey.py`, `insights.py` | Counts → rates → GO / NOT_YET / INSUFFICIENT_DATA per language; survey CSV counts; inputs for AI insights |
| `ai.py` | Claude prompts per language (never translation), YAML answer → sanitize (draft status, known keys only) → same checks → one repair turn; paste mode; insights with verbatim-quote check |
| `server.py` | FastAPI: Host allow-list, per-session token on every `/api` call and `?t=` on `/files`, JSON-only bodies, `no-store`; maps HTTP to the engine and holds no rules of its own |

## App (`web/`)

React 19 + Tailwind v4 + Radix, components copied from the Automation UI Kit. `lib/api.ts`
sends the session token from the `<meta name="studio-token">` the server injects into
`index.html`. `web/dist` is committed; `app.py` serves it with uvicorn on 127.0.0.1.

## Safety rails (and the test that proves each one)

- No URL or outside file can enter a published image or caption → `tests/test_check.py`
- Approval is void after any edit → `tests/test_publish.py`
- Dry-run sends nothing; real send needs smoke + typed Page name → `tests/test_publish.py`
- A post whose outcome is unknown is never re-sent → `tests/test_publish.py`
- Tokens never appear in errors → `tests/test_publish.py`
- Other websites cannot drive the API → `tests/test_server.py`
- AI output is always a draft and only uses sourced numbers → `tests/test_ai.py`

`tests/mutations/*.yaml` break each rail and require its test to fail
(`python3 scripts/mutation_check.py --all`).

## Unverified here

The Facebook Graph API request shapes were written from the documented pattern
(unpublished photos → feed with `attached_media` → comment) but could not be exercised
against Facebook from the build environment. `publish --smoke facebook` checks the token
and Page first; make the first real post to a test Page.
