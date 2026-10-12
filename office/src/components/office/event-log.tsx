import { useI18n } from "@/components/i18n-provider"
import { clock, labelOr } from "@/lib/format"
import type { LogEntry, Mode } from "@/lib/snapshot"
import { cn } from "@/lib/utils"

const GLYPH: Record<LogEntry["kind"], string> = { start: "→", done: "✓", fail: "✕", warn: "!" }

export function EventLog({ entries, mode }: { entries: LogEntry[]; mode: Mode }) {
  const { t, locale } = useI18n()
  return (
    <section className="rounded-2xl border bg-card px-4 pt-3.5 pb-4 text-card-foreground" aria-labelledby="log-title">
      <h2 id="log-title" className="mb-2 text-xs font-bold tracking-[0.06em] text-muted-foreground uppercase">
        {t("log.title")}
      </h2>
      {entries.length === 0 ? (
        <p className="py-3 text-sm text-muted-foreground">{t("log.empty")}</p>
      ) : (
        <ol className="flex flex-col">
          {entries.map((entry, index) => (
            <li
              key={`${entry.t}-${entry.agent}-${entry.kind}-${index}`}
              className="grid grid-cols-[3.5rem_minmax(0,1fr)] gap-x-3 gap-y-0.5 border-t py-1.5 text-[13px] first:border-t-0 sm:grid-cols-[3.5rem_9.5rem_minmax(0,1fr)]"
            >
              <time className="font-mono text-xs text-muted-foreground tabular-nums" dateTime={new Date(entry.t * 1000).toISOString()}>
                {clock(entry.t, locale)}
              </time>
              <b className="font-semibold break-words">
                {entry.agent === "main" ? t(`boss.${mode}.name`) : labelOr(t, `roster.${entry.agent}.name`, entry.agent)}
              </b>
              <span className="col-start-2 min-w-0 text-foreground/80 sm:col-start-3">
                <span
                  className={cn(
                    "mr-1.5 inline-block font-bold",
                    entry.kind === "start" && "text-info",
                    entry.kind === "done" && "text-success",
                    entry.kind === "fail" && "text-destructive",
                    entry.kind === "warn" && "text-foreground",
                  )}
                >
                  {GLYPH[entry.kind]} {t(`log.kind.${entry.kind}`)}
                </span>
                {entry.text}
              </span>
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
