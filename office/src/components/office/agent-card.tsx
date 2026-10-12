import * as React from "react"

import { useI18n } from "@/components/i18n-provider"
import { useNodes } from "@/components/office/nodes"
import { Robot } from "@/components/office/robot"
import { StatusChip } from "@/components/office/status-chip"
import { Progress } from "@/components/ui/progress"
import { describe } from "@/lib/describe"
import { labelOr, tOr } from "@/lib/format"
import { BUSY, type AgentView } from "@/lib/snapshot"
import { cn } from "@/lib/utils"

export function AgentCard({ view, onSelect }: { view: AgentView; onSelect: (id: string, opener: HTMLElement) => void }) {
  const { t } = useI18n()
  const { register } = useNodes()
  const ref = React.useCallback((element: HTMLButtonElement | null) => register(view.id, element), [register, view.id])
  const busy = BUSY.includes(view.state)
  const percent = view.progress === null ? null : Math.floor(view.progress * 100)
  const meta = [
    view.model,
    view.effort,
    view.turns ? t(view.turns.max ? "agent.turns_of" : "agent.turns", { used: view.turns.used, max: view.turns.max ?? 0 }) : null,
  ].filter(Boolean)

  const name = labelOr(t, `roster.${view.id}.name`, view.id)

  return (
    <article
      ref={ref}
      data-state={view.state}
      data-agent={view.id}
      className={cn(
        "relative z-[2] flex min-w-0 flex-col gap-1 rounded-xl border bg-card p-3 text-left text-card-foreground shadow-sm",
        "transition-[border-color,box-shadow] hover:border-muted-foreground/60 has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-ring",
        (busy || view.state === "blocked") &&
          "border-[var(--sc)] shadow-[0_0_0_3px_color-mix(in_oklab,var(--sc)_22%,transparent)]",
      )}
    >
      <div className="flex min-h-6 items-center justify-between gap-1.5">
        <StatusChip state={view.state} />
        {view.tag ? (
          <span className="rounded-md bg-foreground px-1.5 py-0.5 font-mono text-[10.5px] text-background">
            {t(`tag.${view.tag}`)}
          </span>
        ) : null}
      </div>
      <div className="flex justify-center">
        <Robot kind={view.kind} state={view.state} />
      </div>
      <h3 className="text-[13.5px] leading-tight font-bold break-words">
        {/* The name is the card's only button; its ::after covers the whole card, so the card is one click target. */}
        <button
          type="button"
          onClick={(event) => onSelect(view.id, event.currentTarget)}
          aria-label={t("agent.open", { agent: name })}
          className="cursor-pointer text-left outline-none after:absolute after:inset-0 after:rounded-xl"
        >
          {name}
        </button>
      </h3>
      <p className="text-xs text-muted-foreground">{tOr(t, `roster.${view.id}.role`, "roster.other.role")}</p>
      <p className="mt-1 line-clamp-3 min-h-[3.9em] text-[12.5px] leading-snug text-foreground/80">{describe(view, t)}</p>
      <div className="mt-0.5 flex items-center gap-2">
        <Progress value={percent} aria-label={t("agent.progress")} />
        <span className="min-w-[3.6ch] text-right font-mono text-[11.5px] text-muted-foreground tabular-nums">
          {percent === null ? "—" : `${busy ? "~" : ""}${percent}%`}
        </span>
      </div>
      <p className="mt-0.5 min-h-[1.1em] font-mono text-[10.5px] break-words text-muted-foreground">{meta.join(" · ")}</p>
    </article>
  )
}
