// Which answer belongs to the feature the person picked. Pure, so it is tested without a browser.

/** The two fields of a snapshot that say which feature it was computed for and which ones exist. */
export interface FeatureAnswer {
  feature: string | null
  features: string[]
}

/**
 * Is `answer` the one to draw for the pick `wanted`? No pick takes any answer; a pick takes the answer computed for it.
 * An answer that does not list `wanted` at all can only be the server falling back (the feature was removed, or a sample
 * ignores the pick): it stands, so the page never sits on the loading state waiting for a feature that is gone.
 */
export function answersFeature(answer: FeatureAnswer, wanted: string | null): boolean {
  return wanted === null || answer.feature === wanted || !answer.features.includes(wanted)
}

/** The pick to keep after seeing `answer`: dropped once the answer's own list no longer has it. */
export function keepFeature(answer: FeatureAnswer | null, wanted: string | null): string | null {
  return wanted !== null && answer !== null && !answer.features.includes(wanted) ? null : wanted
}
