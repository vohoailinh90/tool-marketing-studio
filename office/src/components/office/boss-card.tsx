import * as React from "react"
import { CheckIcon } from "lucide-react"

import { useI18n } from "@/components/i18n-provider"
import { Budget } from "@/components/office/budget"
import { useNodes } from "@/components/office/nodes"
import { Robot } from "@/components/office/robot"
import { StatusChip } from "@/components/office/status-chip"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { labelOr } from "@/lib/format"
import type { Translate } from "@/lib/i18n"
import type { Snapshot } from "@/lib/snapshot"
import { cn } from "@/lib/utils"

function bossLine(snapshot: Snapshot, t: Translate): string {
  const { boss } = snapshot
  if (boss.waiting_for) {
    const agent = labelOr(t, `roster.${boss.waiting_for}.name`, boss.waiting_for)
    return boss.task ? t("boss.waiting_for_task", { agent, task: boss.task }) : t("boss.waiting_for", { agent })
  }
  return t(`boss.state.${boss.state}`)
}

export function BossCard({ snapshot }: { snapshot: Snapshot }) {
  const { t } = useI18n()
  const { register } = useNodes()
  const ref = React.useCallback((element: HTMLDivElement | null) => register("main", element), [register])
  const { mode, boss, requirement, progress, phase } = snapshot
  const steps = phase.steps
  const current = phase.current === "done" ? steps.length : steps.indexOf(phase.current ?? "")
  const chips = [requirement?.tier, requirement?.strategy].filter((chip): chip is string => Boolean(chip))
  const stats = [
    ["agents", progress.agents],
    ["total", progress.total],
    ["running", progress.running],
    ["done", progress.done],
    ["blocked", progress.blocked],
  ] as const

  return (
    <Card
      ref={ref}
      data-state={boss.state}
      className={cn(
        "relative z-[2] grid gap-x-8 gap-y-5 rounded-2xl border-[color-mix(in_oklab,var(--dept-yellow)_30%,var(--border))] px-5 py-5 sm:px-6",
        "bg-[color-mix(in_oklab,var(--dept-yellow)_7%,var(--card))]",
        "md:grid-cols-[auto_minmax(0,1fr)] lg:grid-cols-[auto_minmax(0,1fr)_17.5rem] lg:items-center",
      )}
      style={{ "--dept": "var(--dept-yellow)" } as React.CSSProperties}
    >
      <div className="flex w-full flex-row flex-wrap items-center gap-x-3 gap-y-1 md:w-44 md:flex-col md:text-center">
        <div className="w-24 md:w-36">
          <Robot kind={boss.kind} state={boss.state} />
        </div>
        <div className="flex flex-col gap-0.5 md:items-center">
          <h2 className="text-base font-extrabold">{t(`boss.${mode}.name`)}</h2>
          <p className="text-xs text-pretty text-muted-foreground">{t(`boss.${mode}.role`)}</p>
        </div>
        <StatusChip state={boss.state} />
      </div>

      <div className="flex min-w-0 flex-col gap-3">
        <div className="flex flex-wrap items-center gap-1.5 font-mono text-xs text-muted-foreground">
          {chips.map((chip, index) => (
            <span
              key={chip}
              className={cn("rounded-md px-2 py-px", index === 0 && /^T\d$/.test(chip) ? "bg-foreground text-background" : "border border-input")}
            >
              {chip}
            </span>
          ))}
        </div>
        <h2 className="text-xl font-extrabold tracking-tight text-balance sm:text-2xl">
          {requirement?.id ?? t("requirement.unnamed")}
        </h2>
        <p className="min-h-[2.9em] text-[13px] text-pretty text-muted-foreground">{bossLine(snapshot, t)}</p>
        <div className="flex items-center gap-4" data-state="working">
          <Progress className="h-3" value={progress.pct} aria-label={t("progress.label")} />
          <span className="min-w-[3.3ch] text-right text-3xl font-extrabold tracking-tight tabular-nums sm:text-4xl">
            {progress.pct === null ? "—" : `${progress.pct}%`}
          </span>
        </div>
        {progress.pct === null ? <p className="text-xs text-muted-foreground">{t("progress.none")}</p> : null}
        <ol className="flex flex-wrap gap-1.5" aria-label={t("phase.label")}>
          {steps.map((step, index) => {
            const status = index < current ? "past" : index === current ? "now" : "next"
            return (
              <li
                key={step}
                aria-current={status === "now" ? "step" : undefined}
                className={cn(
                  "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold",
                  status === "next" && "border-dashed text-muted-foreground",
                  status === "past" && "bg-card text-foreground/80",
                  status === "now" && "border-info bg-[color-mix(in_oklab,var(--info)_11%,var(--card))] text-foreground",
                )}
              >
                {status === "past" ? <CheckIcon className="size-3 text-success" aria-hidden="true" /> : null}
                {t(`phase.${step}`)}
              </li>
            )
          })}
        </ol>
        <dl className="mt-1 grid grid-cols-3 gap-y-3 sm:grid-cols-5">
          {stats.map(([key, value], index) => (
            <div
              key={key}
              className={cn("flex flex-col px-3 first:pl-0 sm:border-l sm:first:border-l-0", index === 3 && "max-sm:pl-0")}
            >
              <dd className="order-1 text-[28px] leading-tight font-extrabold tracking-tight tabular-nums">{value}</dd>
              <dt className="order-2 flex items-center gap-1.5 text-xs text-muted-foreground">
                {key === "blocked" && value > 0 ? <span aria-hidden="true" className="size-1.5 rounded-full bg-destructive" /> : null}
                {t(`stats.${key}`)}
              </dt>
            </div>
          ))}
        </dl>
      </div>

      <div className="md:col-span-2 lg:col-span-1">
        <Budget mode={mode} slots={snapshot.budget} />
      </div>
    </Card>
  )
}
