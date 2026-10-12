import * as React from "react"

import { useNodes } from "@/components/office/nodes"
import { edgeGeometry, relativeRect, type EdgeGeometry } from "@/lib/edges"
import type { Edge } from "@/lib/snapshot"

// Agent ids are free text (a plugin's agents are `plugin:name`), so the pair key joins with a control character.
const SEP = "\u001f"

/**
 * The lines between cards. Geometry is measured from the real DOM, so it follows any layout; it is
 * measured again only when the set of lines or the floor's size changes. A line's state (planned,
 * active, done) is just an attribute, so a poll that changes only states re-measures nothing.
 */
export function HandoffEdges({
  edges,
  layoutKey,
  container,
}: {
  edges: Edge[]
  /** Changes when cards come or go, so lines are re-measured. */
  layoutKey: string
  container: React.RefObject<HTMLElement | null>
}) {
  const nodes = useNodes()
  const [geometry, setGeometry] = React.useState<Record<string, EdgeGeometry>>({})
  const [size, setSize] = React.useState({ width: 0, height: 0 })
  const pairsKey = edges.map((edge) => `${edge.from}${SEP}${edge.to}`).join("\n")

  const measure = React.useCallback(() => {
    const box = container.current
    if (!box) return
    const base = box.getBoundingClientRect()
    const next: Record<string, EdgeGeometry> = {}
    for (const pair of pairsKey ? pairsKey.split("\n") : []) {
      const [from, to] = pair.split(SEP)
      const a = nodes.get(from)
      const b = nodes.get(to)
      if (a && b) next[pair] = edgeGeometry(relativeRect(a.getBoundingClientRect(), base), relativeRect(b.getBoundingClientRect(), base))
    }
    setGeometry(next)
    setSize({ width: base.width, height: base.height })
  }, [container, nodes, pairsKey])

  React.useLayoutEffect(() => {
    measure()
  }, [measure, layoutKey])

  React.useEffect(() => {
    const box = container.current
    if (!box) return
    const observer = new ResizeObserver(measure)
    observer.observe(box)
    void document.fonts?.ready.then(measure)
    return () => observer.disconnect()
  }, [container, measure])

  // Active lines last, so they are drawn over the quiet ones.
  const ordered = [...edges].sort((x, y) => Number(x.state === "active") - Number(y.state === "active"))

  return (
    <svg
      className="pointer-events-none absolute inset-0 z-[1] overflow-visible"
      width={size.width}
      height={size.height}
      viewBox={`0 0 ${size.width} ${size.height}`}
      aria-hidden="true"
      focusable="false"
    >
      {ordered.map((edge) => {
        const shape = geometry[`${edge.from}${SEP}${edge.to}`]
        if (!shape) return null
        return (
          <g key={`${edge.from}${SEP}${edge.to}`} className="edge" data-s={edge.state}>
            <path d={shape.d} />
            <circle cx={shape.end[0]} cy={shape.end[1]} r={3.4} />
          </g>
        )
      })}
    </svg>
  )
}
