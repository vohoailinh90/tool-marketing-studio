import { Download, ExternalLink, MessageSquarePlus, RefreshCw } from "lucide-react"
import * as React from "react"

import { Busy, Notice, PageHeader, errorText } from "@/components/common"
import { StatusBadge } from "@/components/dashboard/status-badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Textarea } from "@/components/ui/textarea"
import { api, postPath, type HistoryRow } from "@/lib/api"
import { languageNames, useI18n } from "@/lib/i18n"

const TOTAL_FIELDS = ["reactions", "comments", "shares"] as const

function toCsv(rows: HistoryRow[]): string {
  const head = ["published_at", "tool", "post", "lang", "platform", "where", "method", "comments", "url"]
  const cell = (v: unknown) => `"${String(v ?? "").replaceAll('"', '""')}"`
  return [head.join(","), ...rows.map((r) => [r.published_at, r.tool_name, r.post, r.lang, r.platform, r.where, r.method, r.comments, r.url].map(cell).join(","))].join("\n")
}

export function HistoryPage() {
  const { t } = useI18n()
  const [rows, setRows] = React.useState<HistoryRow[] | null>(null)
  const [busy, setBusy] = React.useState("")
  const [error, setError] = React.useState("")
  const [note, setNote] = React.useState("")
  const [target, setTarget] = React.useState<HistoryRow | null>(null)
  const [pasted, setPasted] = React.useState("")
  const [totals, setTotals] = React.useState<Record<string, string>>({})

  const load = React.useCallback(async () => { setRows((await api.get<{ rows: HistoryRow[] }>("/api/history")).rows) }, [])
  React.useEffect(() => { void load().catch((e) => setError(errorText(e))) }, [load])

  async function run(name: string, action: () => Promise<string>) {
    setBusy(name); setError(""); setNote("")
    try { setNote(await action()); await load() } catch (exc) { setError(errorText(exc)) } finally { setBusy("") }
  }

  return (
    <div className="space-y-6">
      <PageHeader title={t("history_title")} description={t("history_help")}>
        {rows && rows.length > 0 && (
          <Button variant="outline" size="sm" onClick={() => {
            const blob = new Blob([toCsv(rows)], { type: "text/csv" })
            const link = document.createElement("a")
            link.href = URL.createObjectURL(blob); link.download = "posting-history.csv"; link.click()
          }}><Download /> CSV</Button>
        )}
      </PageHeader>
      {error && <Notice tone="error">{error}</Notice>}
      {note && <Notice tone="success">{note}</Notice>}
      <Card>
        <CardContent>
          {rows === null ? <p className="text-sm text-muted-foreground">{t("loading")}</p> : rows.length === 0 ? (
            <p className="text-sm text-muted-foreground">{t("history_empty")}</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t("col_when")}</TableHead>
                  <TableHead>{t("col_tool")}</TableHead>
                  <TableHead>{t("post")}</TableHead>
                  <TableHead>{t("col_platform")}</TableHead>
                  <TableHead>{t("col_where")}</TableHead>
                  <TableHead className="text-right">{t("col_reactions")}</TableHead>
                  <TableHead className="text-right">{t("col_comments")}</TableHead>
                  <TableHead>{t("col_actions")}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((row, index) => {
                  const path = postPath(row.campaign, row.lang, row.post)
                  const scannable = row.platform === "facebook" && row.method === "api" && row.state === "done"
                  return (
                    <TableRow key={index}>
                      <TableCell className="whitespace-nowrap tabular-nums">{row.published_at.replace("T", " ").slice(0, 16)}</TableCell>
                      <TableCell>{row.tool_name}</TableCell>
                      <TableCell>
                        <span className="font-medium">{row.post}</span>
                        <span className="text-muted-foreground"> · {languageNames[row.lang] ?? row.lang}</span>
                      </TableCell>
                      <TableCell className="capitalize">{row.platform}</TableCell>
                      <TableCell>
                        <span className="flex flex-wrap items-center gap-2">
                          <StatusBadge tone={row.state === "done" ? "success" : "warning"}>{row.method === "api" ? t("by_api") : t("by_hand")}</StatusBadge>
                          {row.where}
                          {row.url && <a href={row.url} target="_blank" rel="noreferrer" aria-label={t("open")}><ExternalLink className="size-3.5" /></a>}
                        </span>
                      </TableCell>
                      <TableCell className="text-right tabular-nums">{row.totals.reactions ?? "—"}</TableCell>
                      <TableCell className="text-right tabular-nums">{row.comments}</TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {scannable && (
                            <Button size="sm" variant="ghost" disabled={busy !== ""} title={t("scan_comments")}
                              onClick={() => run(`scan${index}`, async () => {
                                const result = await api.post<{ comments: number }>(`${path}/feedback/scan`, {})
                                return t("scan_done", { n: result.comments })
                              })}>
                              <Busy on={busy === `scan${index}`}><RefreshCw /></Busy>
                              <span className="sr-only">{t("scan_comments")}</span>
                            </Button>
                          )}
                          <Button size="sm" variant="ghost" title={t("add_comments")} onClick={() => { setTarget(row); setPasted(""); setTotals({}) }}>
                            <MessageSquarePlus />
                            <span className="sr-only">{t("add_comments")}</span>
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={target !== null} onOpenChange={(open) => { if (!open) setTarget(null) }}>
        <DialogContent className="sm:max-w-xl">
          <DialogHeader>
            <DialogTitle>{t("add_comments")}</DialogTitle>
            <DialogDescription>{t("add_comments_help")}</DialogDescription>
          </DialogHeader>
          <Textarea value={pasted} onChange={(e) => setPasted(e.target.value)} className="h-48" placeholder={t("add_comments_placeholder")} />
          <div className="grid grid-cols-3 gap-3">
            {TOTAL_FIELDS.map((field) => (
              <div key={field} className="space-y-1">
                <Label>{t(`col_${field}` as "col_reactions")}</Label>
                <Input inputMode="numeric" value={totals[field] ?? ""} onChange={(e) => setTotals({ ...totals, [field]: e.target.value.replace(/\D/g, "") })} />
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setTarget(null)}>{t("cancel")}</Button>
            <Button disabled={busy !== "" || (!pasted.trim() && Object.values(totals).every((v) => !v))}
              onClick={() => target && run("paste", async () => {
                const result = await api.post<{ comments: number }>(`${postPath(target.campaign, target.lang, target.post)}/feedback`,
                  { platform: target.platform, text: pasted, totals })
                setTarget(null)
                return t("comments_saved", { n: result.comments })
              })}>
              <Busy on={busy === "paste"}>{t("save")}</Busy>
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
