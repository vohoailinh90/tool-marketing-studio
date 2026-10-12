import * as React from "react"

import { fetchSnapshot, type SnapshotParams } from "@/lib/api"
import type { Snapshot } from "@/lib/snapshot"

/** How often the live view asks again. The server re-parses its inputs only when a file changed. */
const POLL_MS = 1000

/**
 * The latest snapshot for `params`. Following the present (live, no replay position) polls;
 * a replay position or a sample is fetched once per change, and a request that is overtaken
 * by a newer one is cancelled so a slow answer can never overwrite a fresh one.
 */
export function useSnapshot(params: SnapshotParams): { snapshot: Snapshot | null; error: string | null } {
  const { mode, source, at, feature } = params
  const [snapshot, setSnapshot] = React.useState<Snapshot | null>(null)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    let cancelled = false
    let controller: AbortController | null = null

    const run = async () => {
      controller?.abort()
      controller = new AbortController()
      try {
        const next = await fetchSnapshot({ mode, source, at, feature }, controller.signal)
        if (cancelled) return
        setSnapshot(next)
        setError(null)
      } catch (caught) {
        if (cancelled || (caught instanceof DOMException && caught.name === "AbortError")) return
        setError(caught instanceof Error ? caught.message : String(caught))
      }
    }

    void run()
    const timer = source === "live" && at === null ? window.setInterval(run, POLL_MS) : undefined
    return () => {
      cancelled = true
      if (timer !== undefined) window.clearInterval(timer)
      controller?.abort()
    }
  }, [mode, source, at, feature])

  return { snapshot, error }
}
