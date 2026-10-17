import type { Issue } from "./api"

/** What the render endpoint answers: `rendered` is false when the post has check errors or an image could not be drawn. */
export type RenderAnswer = { rendered?: boolean; issues: Issue[] }

/**
 * What the preview page shows for an answer to a render requested for `started`, while `current` is the post on screen.
 * An answer that arrives after the user moved to another post is not about the post now shown, so it shows nothing (null).
 * Only an explicit `rendered: false` is a failure, so an answer without the field keeps the old, plain behavior.
 */
export function renderOutcome(answer: RenderAnswer, started: string, current: string): { notes: Issue[]; failed: boolean } | null {
  if (started !== current) return null
  return { notes: answer.issues, failed: answer.rendered === false }
}
