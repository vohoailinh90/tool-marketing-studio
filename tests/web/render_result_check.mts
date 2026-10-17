// Behavior check for web/src/lib/render-result.ts, run by tests/test_web_preview.py under Node's
// TypeScript type stripping. Exits non-zero on the first failed assertion.
import assert from "node:assert/strict"

import { renderOutcome } from "../../web/src/lib/render-result.ts"

const error = { level: "error" as const, where: "slide 2", message: "The diagram could not be drawn" }
const warning = { level: "warn" as const, where: "slide 1", message: "The text is small" }
const post = "/campaigns/demo/posts/vi/01-pain"
const other = "/campaigns/demo/posts/vi/02-other"

// A render the server refused: a failure, with its errors.
assert.deepEqual(renderOutcome({ rendered: false, issues: [error] }, post, post), { notes: [error], failed: true })

// A render that worked is not a failure, warnings or not.
assert.deepEqual(renderOutcome({ rendered: true, issues: [warning] }, post, post), { notes: [warning], failed: false })
assert.deepEqual(renderOutcome({ rendered: true, issues: [] }, post, post), { notes: [], failed: false })

// An answer without the field is not read as a failure.
assert.deepEqual(renderOutcome({ issues: [warning] }, post, post), { notes: [warning], failed: false })

// The user moved to another post while the render ran: the answer is not about the post on screen, failed or not.
assert.equal(renderOutcome({ rendered: false, issues: [error] }, post, other), null)
assert.equal(renderOutcome({ rendered: true, issues: [warning] }, post, other), null)

console.log("render-result: ok")
