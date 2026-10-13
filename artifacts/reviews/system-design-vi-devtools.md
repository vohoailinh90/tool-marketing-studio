# DevTools & Productivity — author verification

Scope: sd-09-001 through sd-09-020, requested on 2026-10-13.
This is author verification, not an independent technical approval.

- Twenty original Vietnamese lesson drafts, question/answer pairs and SVG figures.
- Source bodies retrieved using GitHub at commit b28380a4710c5ec9638ec037d4168e288f334cba.
- Each retrieved body verified against its Git blob OID; SHA-256 and byte counts in metadata.
- No upstream image retrieved, embedded or traced.
- Titles and source-body-read flags updated only for the twenty source-map entries.
- Full roster remains 404 positions, fifteen categories, four shared-source pairs.
- Index lists written lessons in source-map order; next_id remains sd-01-008.
- User explicitly selected category sd-09 before the remaining category sd-01 lessons.
- PR #40 is already merged at 5831cdcef96a2c83664e02d83a4e803cf47f259c.
- Existing seven lessons and their metadata are unchanged.

## Mobile checks

Chromium 141 through Playwright, rendered Markdown with all details open.
Twenty complete lessons checked at viewport widths 320, 375 and 430 pixels.
No document horizontal overflow at any width.
All SVG text bounding boxes lie inside their viewBox.
SVG viewBox width is 352; text is 18px; body margin is 16px per side.
Minimum effective text: 18 × 288 / 352 = 14.73px at 320px.
Minimum effective text: 18 × 343 / 352 = 17.54px at 375px.
Screenshots captured locally; contact sheet of all twenty inspected.
No claims of live GitHub rendering, real-device testing or learner testing.

## Checks and open work

`scripts/sd101_check.py`: 27 lessons, zero problems.
`scripts/layout_check.py`: zero errors.
`git diff --check`: clean.
`pytest -q tests/test_sd101_check.py`: 209 passed, 2960 subtests passed.

Primary-reference retrieval attempted for 55 distinct URLs: 38 returned HTTP 200,
sixteen returned HTTP 403 and one Ceph history URL returned HTTP 404.
The broken Ceph link was replaced with the project's repository.
Successful retrieval is not recorded as verification of every claim.
Claims remain pending; historical AI features and corporate affiliations are not
presented as fully verified current product facts. Technical review remains pending.
The source's “20 projects” body contains 21 names; the lesson records that discrepancy.

All twenty lessons remain draft, not done or approved. Learner testing not performed.
Independent PR review is required; no automatic merge, deployment or publishing.
