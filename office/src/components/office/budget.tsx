import { useI18n } from "@/components/i18n-provider"
import { labelOr } from "@/lib/format"
import type { BudgetSlot, Mode } from "@/lib/snapshot"
import { cn } from "@/lib/utils"

/** Base and each reserve, side by side, as the repository's budget rule asks: never one merged number. */
export function Budget({ mode, slots }: { mode: Mode; slots: BudgetSlot[] | null }) {
  const { t } = useI18n()
  return (
    <aside className="flex flex-col gap-2.5 rounded-xl border bg-background/60 p-4" aria-label={t(`budget.title.${mode}`)}>
      <h2 className="text-xs font-bold tracking-[0.06em] text-muted-foreground uppercase">{t(`budget.title.${mode}`)}</h2>
      {slots === null ? (
        <p className="text-xs leading-snug text-muted-foreground">{t(`budget.none.${mode}`)}</p>
      ) : (
        <>
          {slots.map((slot) => (
            <div key={slot.id} className="grid grid-cols-[minmax(0,1fr)_auto_auto] items-center gap-2.5 text-[12.5px]">
              <span className="text-foreground/80">{labelOr(t, `budget.slot.${slot.id}`, slot.id)}</span>
              <span className="inline-flex gap-1" role="img" aria-label={`${slot.used}/${slot.cap}`}>
                {Array.from({ length: slot.cap }, (_, index) => (
                  <i
                    key={index}
                    className={cn(
                      "h-2 w-4 rounded-[3px] border",
                      index < slot.used
                        ? "border-info bg-info"
                        : index < slot.granted
                          ? "border-muted-foreground/60"
                          : "border-dashed border-muted-foreground/50",
                    )}
                  />
                ))}
              </span>
              <span className="min-w-[2.6rem] text-right font-mono text-xs tabular-nums">
                {slot.used}/{slot.cap}
              </span>
            </div>
          ))}
          {slots.some((slot) => slot.granted < slot.cap) ? (
            <p className="text-[11.5px] leading-snug text-muted-foreground">{t("budget.pending")}</p>
          ) : null}
          <p className="text-[11.5px] leading-snug text-muted-foreground">{t(`budget.note.${mode}`)}</p>
        </>
      )}
    </aside>
  )
}
