// Behavior check for office/src/lib/feature.ts, run by tests/test_office_ui.py under Node's
// TypeScript type stripping. Exits non-zero on the first failed assertion.
import assert from "node:assert/strict"

import { answersFeature, keepFeature } from "../../office/src/lib/feature.ts"

const answer = (feature: string | null, features: string[]) => ({ feature, features })

// No filter: any answer is drawn, whatever feature it was computed for.
assert.equal(answersFeature(answer("a", ["a", "b"]), null), true)
assert.equal(answersFeature(answer(null, []), null), true)

// A filter takes the answer computed for it, and refuses an answer that is still for the previous pick.
assert.equal(answersFeature(answer("b", ["a", "b"]), "b"), true)
assert.equal(answersFeature(answer("a", ["a", "b"]), "b"), false)

// The picked feature was removed: the server falls back to another one and no longer lists it. That answer stands,
// or the page waits forever for a feature that will not come back.
assert.equal(answersFeature(answer("a", ["a"]), "b"), true)
assert.equal(answersFeature(answer(null, []), "b"), true)

// The filter is kept while the answer still lists it (also while that answer is for the previous pick) ...
assert.equal(keepFeature(answer("a", ["a", "b"]), "b"), "b")
assert.equal(keepFeature(answer("b", ["a", "b"]), "b"), "b")
// ... and dropped once it does not, which is what lets the next request ask for the default feature.
assert.equal(keepFeature(answer("a", ["a"]), "b"), null)
assert.equal(keepFeature(answer(null, []), "b"), null)
// Nothing to compare against yet, or no filter: unchanged.
assert.equal(keepFeature(null, "b"), "b")
assert.equal(keepFeature(answer("a", ["a"]), null), null)

console.log("office feature: ok")
