import { InfoIcon, TriangleAlertIcon } from "lucide-react"

import { useI18n } from "@/components/i18n-provider"
import { Button } from "@/components/ui/button"
import type { Source } from "@/lib/api"
import type { Mode, Snapshot } from "@/lib/snapshot"

// Commands are not translated: they are what the person types.
const COMMANDS: Record<string, string[]> = {
  no_ledger: ["python3 scripts/route.py --dimensions <six scores> --signals <signals> --record --requirement <id>"],
  no_events: ["cp .claude/settings.example.json .claude/settings.json"],
  no_features: ["python3 scripts/office/serve.py --team-home /srv/team"],
}

function Notice({ tone, title, body, commands, action }: {
  tone: "info" | "warning"
  title: string
  body: string
  commands?: string[]
  action?: React.ReactNode
}) {
  const Icon = tone === "warning" ? TriangleAlertIcon : InfoIcon
  return (
    <section role={tone === "warning" ? "alert" : "status"} className="flex gap-3 rounded-2xl border bg-card p-4 text-card-foreground">
      <Icon aria-hidden="true" className={tone === "warning" ? "mt-0.5 size-5 flex-none text-warning" : "mt-0.5 size-5 flex-none text-info"} />
      <div className="flex min-w-0 flex-1 flex-col gap-2">
        <h2 className="text-sm font-bold">{title}</h2>
        <p className="text-sm text-pretty text-muted-foreground">{body}</p>
        {commands?.map((command) => (
          <code key={command} className="block overflow-x-auto rounded-md bg-muted px-3 py-2 font-mono text-xs whitespace-pre">
            {command}
          </code>
        ))}
        {action}
      </div>
    </section>
  )
}

/** What the page says when the data is missing or the server cannot be reached. Never blank, never fake. */
export function Notices({ snapshot, mode, error, source, onSample }: {
  snapshot: Snapshot | null
  mode: Mode
  error: string | null
  source: Source
  onSample: () => void
}) {
  const { t } = useI18n()
  const sampleButton =
    source === "live" ? (
      <div>
        <Button size="sm" onClick={onSample}>
          {t("notice.try_sample")}
        </Button>
      </div>
    ) : undefined
  const hints = snapshot?.hints ?? []
  const nothing = hints.includes("no_ledger") && hints.includes("no_events")

  return (
    <>
      {error ? (
        <Notice tone="warning" title={t("notice.error.title")} body={t("notice.error.body", { message: error })} />
      ) : null}
      {nothing ? (
        <Notice
          tone="info"
          title={t("notice.empty.title")}
          body={t("notice.empty.body")}
          commands={[...COMMANDS.no_events, ...COMMANDS.no_ledger]}
          action={sampleButton}
        />
      ) : (
        <>
          {hints.includes("no_events") ? (
            <Notice tone="info" title={t("notice.no_events.title")} body={t("notice.no_events.body")} commands={COMMANDS.no_events} action={sampleButton} />
          ) : null}
          {hints.includes("no_ledger") ? (
            <Notice tone="info" title={t("notice.no_ledger.title")} body={t("notice.no_ledger.body")} commands={COMMANDS.no_ledger} />
          ) : null}
        </>
      )}
      {hints.includes("no_features") && mode === "team" ? (
        <Notice tone="info" title={t("notice.no_features.title")} body={t("notice.no_features.body")} commands={COMMANDS.no_features} action={sampleButton} />
      ) : null}
    </>
  )
}
