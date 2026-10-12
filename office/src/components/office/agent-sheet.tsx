import type * as React from "react"

import { useI18n } from "@/components/i18n-provider"
import { StatusChip } from "@/components/office/status-chip"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { describe } from "@/lib/describe"
import { clock, compact, labelOr, seconds, tOr } from "@/lib/format"
import { BUSY, type AgentView } from "@/lib/snapshot"

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[7.5rem_minmax(0,1fr)] gap-3 border-t py-2 text-sm first:border-t-0">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="min-w-0 break-words">{children}</dd>
    </div>
  )
}

/** Everything the snapshot knows about one agent, so a card can stay small. */
export function AgentSheet({ view, onClose, restoreFocus }: { view: AgentView | null; onClose: () => void; restoreFocus: () => void }) {
  const { t, locale } = useI18n()
  const percent = view?.progress == null ? null : Math.floor(view.progress * 100)
  const busy = view !== null && BUSY.includes(view.state)

  return (
    <Sheet open={view !== null} onOpenChange={(open) => !open && onClose()}>
      {view ? (
        <SheetContent
          side="right"
          closeLabel={t("detail.close")}
          className="overflow-y-auto sm:max-w-md"
          onCloseAutoFocus={(event) => {
            // No trigger element owns this dialog, so hand focus back to the card that opened it.
            event.preventDefault()
            restoreFocus()
          }}
        >
          <SheetHeader>
            <SheetTitle className="text-lg">{labelOr(t, `roster.${view.id}.name`, view.id)}</SheetTitle>
            <SheetDescription>{tOr(t, `roster.${view.id}.role`, "roster.other.role")}</SheetDescription>
            <div className="pt-1">
              <StatusChip state={view.state} />
            </div>
          </SheetHeader>
          <dl className="px-4 pb-6">
            <Row label={t("detail.now")}>{describe(view, t)}</Row>
            {view.task && view.note ? <Row label={t("detail.task")}>{view.task}</Row> : null}
            <Row label={t("detail.progress")}>
              {percent === null ? "—" : `${busy ? "~" : ""}${percent}%`}
              {busy ? <span className="mt-1 block text-xs text-muted-foreground">{t("detail.progress_hint")}</span> : null}
            </Row>
            {view.turns ? (
              <Row label={t("detail.turns")}>
                {view.turns.max ? `${view.turns.used} / ${view.turns.max}` : view.turns.used}
                <span className="mt-1 block text-xs text-muted-foreground">{t("detail.turns_hint")}</span>
              </Row>
            ) : null}
            {view.model ? <Row label={t("detail.model")}>{view.model}</Row> : null}
            {view.effort ? <Row label={t("detail.effort")}>{view.effort}</Row> : null}
            {view.tokens !== null ? <Row label={t("detail.tokens")}>{compact(view.tokens, locale)}</Row> : null}
            {view.duration_ms !== null ? <Row label={t("detail.duration")}>{seconds(view.duration_ms, locale)}</Row> : null}
            <Row label={t("detail.runs")}>{view.runs}</Row>
            {view.since !== null ? <Row label={t("detail.since")}>{clock(view.since, locale)}</Row> : null}
          </dl>
        </SheetContent>
      ) : null}
    </Sheet>
  )
}
