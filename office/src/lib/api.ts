import type { Mode, Snapshot } from "@/lib/snapshot"

export type Source = "live" | "demo"

export interface SnapshotParams {
  mode: Mode
  source: Source
  /** Epoch seconds to replay; null follows the present (live) or the start of the sample (demo). */
  at: number | null
  feature: string | null
}

/** The sample that matches each view; the server lists them at /api/health. */
export const DEMO_FOR: Record<Mode, string> = { claude: "claude-t3", team: "team-f12" }

export function snapshotUrl({ mode, source, at, feature }: SnapshotParams): string {
  const query = new URLSearchParams()
  if (source === "demo") query.set("demo", DEMO_FOR[mode])
  else {
    query.set("mode", mode)
    if (feature) query.set("feature", feature)
  }
  if (at !== null) query.set("at", String(at))
  return `/api/snapshot?${query}`
}

export class SnapshotError extends Error {}

export async function fetchSnapshot(params: SnapshotParams, signal: AbortSignal): Promise<Snapshot> {
  const response = await fetch(snapshotUrl(params), { signal, cache: "no-store" })
  if (!response.ok) throw new SnapshotError(`HTTP ${response.status}`)
  const data: unknown = await response.json()
  if (typeof data !== "object" || data === null || (data as { version?: unknown }).version !== 1) {
    throw new SnapshotError("unexpected snapshot version")
  }
  return data as Snapshot
}
