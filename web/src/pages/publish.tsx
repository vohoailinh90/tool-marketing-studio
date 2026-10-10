import { Download, ExternalLink, PlugZap, Send, ShieldCheck } from "lucide-react"
import * as React from "react"

import { Busy, CopyButton, Notice, PageHeader, errorText } from "@/components/common"
import { PostPicker, usePickedPost } from "@/components/post-picker"
import { StatusBadge } from "@/components/dashboard/status-badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { api, fileUrl, postPath, type LedgerRow, type PostView } from "@/lib/api"
import { languageNames, useI18n } from "@/lib/i18n"
import { useStudio } from "@/lib/studio"

function LedgerState({ row }: { row: LedgerRow }) {
  const { t } = useI18n()
  if (!row?.state) return <StatusBadge tone="neutral">{t("not_published")}</StatusBadge>
  const tone = row.state === "done" ? "success" : row.state === "pending" ? "warning" : "failed"
  return (
    <span className="flex flex-wrap items-center gap-2 text-sm">
      <StatusBadge tone={tone}>{t(`ledger_${row.state}` as "ledger_done")}</StatusBadge>
      {row.published_at && <span className="text-muted-foreground">{row.published_at.replace("T", " ").slice(0, 16)}</span>}
      {row.url && <a href={row.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 underline"><ExternalLink className="size-3" />{t("open")}</a>}
      {row.error && <span className="text-destructive">{row.error}</span>}
    </span>
  )
}

function MarkPosted({ path, platform, onDone }: { path: string; platform: string; onDone: () => Promise<void> }) {
  const { t } = useI18n()
  const [where, setWhere] = React.useState("")
  const [url, setUrl] = React.useState("")
  const [when, setWhen] = React.useState("")
  const [busy, setBusy] = React.useState(false)
  const [error, setError] = React.useState("")
  return (
    <div className="space-y-3 rounded-md border p-3">
      <p className="text-xs text-muted-foreground">{t("mark_posted_help")}</p>
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="space-y-1"><Label>{t("posted_where")}</Label><Input value={where} onChange={(e) => setWhere(e.target.value)} placeholder={t("posted_where_hint")} /></div>
        <div className="space-y-1"><Label>{t("posted_url")}</Label><Input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://" /></div>
        <div className="space-y-1"><Label>{t("posted_when")}</Label><Input type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} /></div>
      </div>
      <Button size="sm" variant="outline" disabled={busy}
        onClick={async () => {
          setBusy(true); setError("")
          try { await api.post(`${path}/posted`, { platform, where, url, when }); await onDone() }
          catch (exc) { setError(errorText(exc)) } finally { setBusy(false) }
        }}>
        <Busy on={busy}>{t("mark_posted_button")}</Busy>
      </Button>
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}

export function PublishPage() {
  const { campaign, state, refresh } = useStudio()
  const { t } = useI18n()
  const [picked, pick] = usePickedPost()
  const [view, setView] = React.useState<PostView | null>(null)
  const [busy, setBusy] = React.useState("")
  const [error, setError] = React.useState("")
  const [plan, setPlan] = React.useState<string[]>([])
  const [confirmOpen, setConfirmOpen] = React.useState(false)
  const [typed, setTyped] = React.useState("")
  const [done, setDone] = React.useState("")

  const path = campaign && picked ? postPath(campaign.slug, picked.lang, picked.id) : ""
  const load = React.useCallback(async () => { if (path) setView(await api.get<PostView>(path)) }, [path])
  React.useEffect(() => { setPlan([]); setError(""); setDone(""); void load().catch((e) => setError(errorText(e))) }, [load])

  async function run(name: string, action: () => Promise<void>) {
    setBusy(name); setError("")
    try { await action(); await load(); await refresh() } catch (exc) { setError(errorText(exc)) } finally { setBusy("") }
  }

  if (!campaign || !state) return null
  const pageName = state.facebook.page_name

  return (
    <div className="space-y-6">
      <PageHeader title={t("publish_title")} description={t("publish_help")}>
        <PostPicker value={picked} onChange={pick} />
      </PageHeader>
      {error && <Notice tone="error">{error}</Notice>}
      {done && <Notice tone="success">{done}</Notice>}
      {view && picked && (
        <>
          <Notice tone={view.approved ? "success" : "info"}>
            {view.approved ? `✅ ${t("approval")}: ${view.approval}` : `⛔ ${t("approval")}: ${view.approval} — ${t("approve_first")}`}
          </Notice>
          <div className="grid gap-4 xl:grid-cols-2">
            {campaign.platforms.map((platform) => {
              const isApi = state.platforms.find((p) => p.code === platform)?.api
              const row = view.ledger[platform]
              return (
                <Card key={platform}>
                  <CardHeader>
                    <CardTitle className="capitalize">{platform}</CardTitle>
                    <CardDescription>{isApi ? t("platform_api_help") : t("manual_only")}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <LedgerState row={row} />
                    <div className="space-y-1">
                      <Label>{t("tracked_link")}</Label>
                      <div className="flex items-center gap-2">
                        <code className="min-w-0 flex-1 truncate rounded bg-muted px-2 py-1 text-xs">{view.links[platform] || t("link_not_set")}</code>
                        {view.links[platform] && <CopyButton text={view.links[platform]} />}
                      </div>
                    </div>
                    <Button asChild variant="outline" size="sm">
                      <a href={fileUrl(`/files/${campaign.slug}/${picked.lang}/${picked.id}/pack/${platform}`)}>
                        <Download /> {t("download_pack")}
                      </a>
                    </Button>

                    {isApi && row?.state !== "done" && (
                      <div className="space-y-3 rounded-md border p-3">
                        <p className="text-sm">
                          {state.facebook.configured
                            ? pageName ? t("smoke_line", { page: pageName, at: state.facebook.checked_at.replace("T", " ").slice(0, 16) }) : t("smoke_needed")
                            : t("fb_not_configured")}
                        </p>
                        {row?.state === "pending" ? (
                          <div className="flex flex-wrap gap-2">
                            <Button size="sm" variant="outline" onClick={() => run("resolve", async () => { await api.post(`${path}/resolve/facebook`, { outcome: "done" }) })}>{t("resolve_done")}</Button>
                            <Button size="sm" variant="outline" onClick={() => run("resolve", async () => { await api.post(`${path}/resolve/facebook`, { outcome: "failed" }) })}>{t("resolve_failed")}</Button>
                          </div>
                        ) : (
                          <div className="flex flex-wrap gap-2">
                            <Button size="sm" variant="outline" disabled={!state.facebook.configured || busy !== ""}
                              onClick={() => run("smoke", async () => { await api.post("/api/facebook/smoke", {}) })}>
                              <Busy on={busy === "smoke"}><PlugZap /> {t("smoke_button")}</Busy>
                            </Button>
                            <Button size="sm" variant="outline" disabled={!view.approved || busy !== ""}
                              onClick={() => run("dry", async () => { setPlan((await api.post<{ steps: string[] }>(`${path}/publish/facebook`, { dry_run: true })).steps) })}>
                              <Busy on={busy === "dry"}><ShieldCheck /> {t("dry_run_button")}</Busy>
                            </Button>
                            <Button size="sm" disabled={!view.approved || !pageName || busy !== ""} onClick={() => { setTyped(""); setConfirmOpen(true) }}>
                              <Send /> {t("publish_button", { lang: languageNames[picked.lang] })}
                            </Button>
                          </div>
                        )}
                        {plan.length > 0 && <pre className="overflow-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-xs">{plan.join("\n")}</pre>}
                      </div>
                    )}
                    {(view.manual[platform] ?? []).length > 0 && (
                      <div className="space-y-1">
                        <Label>{t("manual_records")}</Label>
                        {(view.manual[platform] ?? []).map((record, index) => (
                          <p key={index} className="flex flex-wrap items-center gap-2 text-sm">
                            <StatusBadge tone="success">{record.where || t("by_hand")}</StatusBadge>
                            <span className="text-muted-foreground">{(record.published_at ?? "").replace("T", " ").slice(0, 16)}</span>
                            {record.url && <a href={record.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 underline"><ExternalLink className="size-3" />{t("open")}</a>}
                          </p>
                        ))}
                      </div>
                    )}
                    <details>
                      <summary className="cursor-pointer text-sm font-medium">{t(isApi ? "mark_posted_more" : "mark_posted_title")}</summary>
                      <div className="mt-3">
                        <MarkPosted path={path} platform={platform} onDone={async () => { await load(); await refresh(); setDone(t("posted_recorded")) }} />
                      </div>
                    </details>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </>
      )}

      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("publish_confirm_title")}</DialogTitle>
            <DialogDescription>{t("publish_confirm_explain", { page: pageName })}</DialogDescription>
          </DialogHeader>
          <pre className="max-h-40 overflow-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-xs">{(view?.texts["facebook.txt"] ?? "").slice(0, 600)}</pre>
          <div className="space-y-1">
            <Label htmlFor="page-name">{t("type_page_name", { page: pageName })}</Label>
            <Input id="page-name" value={typed} onChange={(e) => setTyped(e.target.value)} autoComplete="off" />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmOpen(false)}>{t("cancel")}</Button>
            <Button disabled={typed.trim() !== pageName.trim() || busy !== ""}
              onClick={() => run("publish", async () => {
                const row = await api.post<{ url?: string }>(`${path}/publish/facebook`, { dry_run: false, confirm_page_name: typed })
                setConfirmOpen(false); setDone(t("published", { url: row.url ?? "" }))
              })}>
              <Busy on={busy === "publish"}><Send /> {t("publish_now")}</Busy>
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
