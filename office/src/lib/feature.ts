// Which answer belongs to the feature the person picked. Pure, so it is tested without a browser.

/** The two fields of a snapshot that say which feature it was computed for and which ones exist. */
export interface FeatureAnswer {
  feature: string | null
  features: string[]
}

/**
 * Is `answer` the one to draw for the pick `wanted`? No pick takes any answer; a pick takes only the answer computed for
 * it, so an answer for the previous pick is not drawn as the new one's. A pick the answer does not list at all (removed
 * while picked) never matches: `keepFeature` drops it, and the next request asks for the default feature.
 */
export function answersFeature(answer: FeatureAnswer, wanted: string | null): boolean {
  return wanted === null || answer.feature === wanted
}

/** The pick to keep after seeing `answer`: dropped once the answer's own list no longer has it. */
export function keepFeature(answer: FeatureAnswer | null, wanted: string | null): string | null {
  return wanted !== null && answer !== null && !answer.features.includes(wanted) ? null : wanted
}
