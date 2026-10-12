import type * as React from "react"

import { useI18n } from "@/components/i18n-provider"
import { AgentCard } from "@/components/office/agent-card"
import { labelOr } from "@/lib/format"
import type { AgentView, Lane } from "@/lib/snapshot"

// One card is about 204px wide with its gap; a lane gets room in proportion to its cards.
const CARD_BASIS = 204

export function LaneSection({
  lane,
  agents,
  onSelect,
}: {
  lane: Lane
  agents: Record<string, AgentView>
  onSelect: (id: string, opener: HTMLElement) => void
}) {
  const { t } = useI18n()
  const tint = "color-mix(in oklab, var(--dept) var(--lane-mix), var(--card))"
  const style = {
    "--dept": `var(--dept-${lane.color})`,
    flex: `${lane.agents.length} 1 ${lane.agents.length * CARD_BASIS}px`,
    background: tint,
    borderColor: "color-mix(in oklab, var(--dept) 28%, var(--border))",
  } as React.CSSProperties
  // The label sits over the handoff lines in the same tint as the lane, so a line passes behind it.
  const behind = { background: tint } as React.CSSProperties

  return (
    <section className="min-w-0 rounded-2xl border p-3" style={style} aria-labelledby={`lane-${lane.id}`}>
      <div className="flex items-center gap-2 px-1 pb-2.5">
        <span aria-hidden="true" className="size-2.5 flex-none rounded-full bg-[var(--dept)]" />
        <h2 id={`lane-${lane.id}`} className="relative z-[2] rounded-md px-1.5 text-[11.5px] font-bold tracking-[0.09em] text-muted-foreground uppercase" style={behind}>
          {labelOr(t, `lane.${lane.id}`, lane.id)}
        </h2>
        <span className="relative z-[2] ml-auto rounded-md px-1.5 font-mono text-[11px] text-muted-foreground" style={behind}>
          {t("lane.count", { count: lane.agents.length })}
        </span>
      </div>
      <div className="grid grid-cols-[repeat(auto-fit,minmax(10.5rem,1fr))] gap-2.5">
        {lane.agents.map((id) => (
          <AgentCard key={id} view={agents[id]} onSelect={onSelect} />
        ))}
      </div>
    </section>
  )
}
