import * as React from "react"

/** The cursor moves smoothly in memory but is published (and so fetched) only this often. */
const PUBLISH_SECONDS = 0.2

interface Playback {
  running: boolean
  /** Replay seconds per real second. */
  speed: number
  /** The position being shown, in the snapshot's epoch seconds; null when following the present. */
  cursor: number | null
  span: { start: number; end: number } | null
  onCursor: (cursor: number) => void
  /** Called once when the cursor reaches the end of the span. */
  onEnd: () => void
}

/** Advances `cursor` in real time while `running`; a cursor set from outside (the slider) takes over. */
export function usePlayback({ running, speed, cursor, span, onCursor, onEnd }: Playback): void {
  const latest = React.useRef({ speed, span, onCursor, onEnd })
  const position = React.useRef<number | null>(cursor)
  const published = React.useRef<number | null>(null)

  React.useEffect(() => {
    latest.current = { speed, span, onCursor, onEnd }
  })

  React.useEffect(() => {
    // A cursor this hook did not publish came from outside: continue from there.
    if (cursor !== published.current) position.current = cursor
  }, [cursor])

  React.useEffect(() => {
    if (!running) return
    let frame = 0
    let last = 0
    let since = 0
    const tick = (now: number) => {
      const dt = last ? Math.min(0.25, (now - last) / 1000) : 0
      last = now
      const current = latest.current
      if (position.current !== null && current.span) {
        position.current += dt * current.speed
        since += dt
        if (position.current >= current.span.end) {
          position.current = null
          published.current = current.span.end
          current.onCursor(current.span.end)
          current.onEnd()
        } else if (since >= PUBLISH_SECONDS) {
          since = 0
          published.current = position.current
          current.onCursor(position.current)
        }
      }
      frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [running])
}
