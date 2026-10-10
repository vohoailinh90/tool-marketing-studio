import { AlertTriangle, Check, CircleX, Copy, Loader2 } from "lucide-react"
import * as React from "react"

import { StatusBadge, type StatusTone } from "@/components/dashboard/status-badge"
import { Button } from "@/components/ui/button"
import type { Issue, PostSummary } from "@/lib/api"
import { languageNames, useI18n } from "@/lib/i18n"
import { cn } from "@/lib/utils"

export function PageHeader({ title, description, children }: { title: string; description?: string; children?: React.ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div className="space-y-1">
        <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
        {description && <p className="max-w-3xl text-sm text-muted-foreground">{description}</p>}
      </div>
      {children}
    </div>
  )
}

/** Check results from the server. Errors block approval and publishing; warnings are advice. */
export function IssueList({ issues, emptyText }: { issues: Issue[]; emptyText?: string }) {
  const { t } = useI18n()
  if (issues.length === 0) {
    return (
      <p className="flex items-center gap-2 text-sm text-success">
        <Check className="size-4" /> {emptyText ?? t("check_clean")}
      </p>
    )
  }
  return (
    <ul className="flex flex-col gap-1.5">
      {issues.map((issue, index) => (
        <li key={index} className="flex gap-2 text-sm">
          {issue.level === "error" ? (
            <CircleX className="mt-0.5 size-4 shrink-0 text-destructive" aria-label="error" />
          ) : (
            <AlertTriangle className="mt-0.5 size-4 shrink-0 text-warning" aria-label="warning" />
          )}
          <span>
            <span className="text-muted-foreground">{issue.where}: </span>
            {issue.message}
          </span>
        </li>
      ))}
    </ul>
  )
}

/** Multi-select as toggle buttons (languages, platforms). */
export function ChipPicker({ options, value, onChange, label }: {
  options: { code: string; label: string }[]
  value: string[]
  onChange: (next: string[]) => void
  label: string
}) {
  return (
    <div role="group" aria-label={label} className="flex flex-wrap gap-2">
      {options.map((option) => {
        const on = value.includes(option.code)
        return (
          <Button
            key={option.code}
            type="button"
            size="sm"
            variant={on ? "default" : "outline"}
            aria-pressed={on}
            onClick={() => onChange(on ? value.filter((v) => v !== option.code) : [...value, option.code])}
          >
            {on && <Check />}
            {option.label}
          </Button>
        )
      })}
    </div>
  )
}

export function LanguageChips({ langs, value, onChange }: { langs: string[]; value: string[]; onChange: (v: string[]) => void }) {
  const { t } = useI18n()
  return (
    <ChipPicker label={t("content_langs")} value={value} onChange={onChange}
      options={langs.map((code) => ({ code, label: languageNames[code] ?? code }))} />
  )
}

export function CopyButton({ text }: { text: string }) {
  const { t } = useI18n()
  const [done, setDone] = React.useState(false)
  return (
    <Button
      type="button"
      size="sm"
      variant="outline"
      onClick={async () => {
        await navigator.clipboard.writeText(text)
        setDone(true)
        setTimeout(() => setDone(false), 1500)
      }}
    >
      {done ? <Check /> : <Copy />}
      {done ? t("copied") : t("copy")}
    </Button>
  )
}

export function Busy({ on, children }: { on: boolean; children: React.ReactNode }) {
  return (
    <>
      {on && <Loader2 className="animate-spin" />}
      {children}
    </>
  )
}

export function Notice({ tone = "info", children, className }: { tone?: "info" | "error" | "success"; children: React.ReactNode; className?: string }) {
  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      className={cn(
        "rounded-md border px-3 py-2 text-sm",
        tone === "error" && "border-destructive/30 bg-destructive/10 text-destructive",
        tone === "success" && "border-success/30 bg-success/10 text-success",
        tone === "info" && "border-border bg-muted/50 text-foreground",
        className,
      )}
    >
      {children}
    </div>
  )
}

/** One badge for where a post stands: errors → draft → ready → approved → published. */
export function PostStatus({ post }: { post: PostSummary }) {
  const { t } = useI18n()
  const published = Object.values(post.published).some((state) => state === "done")
  let tone: StatusTone = "neutral"
  let label = t("status_draft")
  if (post.errors > 0) {
    tone = "failed"
    label = t("status_errors", { n: post.errors })
  } else if (published) {
    tone = "success"
    label = t("status_published")
  } else if (post.approved) {
    tone = "info"
    label = t("status_approved")
  } else if (post.status === "ready") {
    tone = "warning"
    label = t("status_ready")
  }
  return <StatusBadge tone={tone}>{label}</StatusBadge>
}

export function errorText(exc: unknown): string {
  return exc instanceof Error ? exc.message : String(exc)
}
