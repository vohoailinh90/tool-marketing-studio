import { CheckCheck, ImageIcon, RefreshCw, Save } from "lucide-react"
import * as React from "react"

import { Busy, IssueList, Notice, PageHeader, errorText } from "@/components/common"
import { PostPicker, usePickedPost } from "@/components/post-picker"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { api, fileUrl, postPath, type Issue, type PostView } from "@/lib/api"
import { languageNames, useI18n } from "@/lib/i18n"
import { renderOutcome, type RenderAnswer } from "@/lib/render-result"
import { useStudio } from "@/lib/studio"

export function PreviewPage() {
  const { campaign, refresh } = useStudio()
  const { t } = useI18n()
  const [picked, pick] = usePickedPost()
  const [view, setView] = React.useState<PostView | null>(null)
  const [yaml, setYaml] = React.useState("")
  const [busy, setBusy] = React.useState("")
  const [notes, setNotes] = React.useState<Issue[]>([])
  const [error, setError] = React.useState("")
  const [confirmOpen, setConfirmOpen] = React.useState(false)
  const [read, setRead] = React.useState(false)
  const [stamp, setStamp] = React.useState(0)
  const [renderFailed, setRenderFailed] = React.useState(false)

  const path = campaign && picked ? postPath(campaign.slug, picked.lang, picked.id) : ""
  // The post on screen now: an action that was started for another post must not write into this one when it ends.
  const live = React.useRef(path)
  React.useEffect(() => { live.current = path }, [path])
  const load = React.useCallback(async () => {
    if (!path) return
    const next = await api.get<PostView>(path)
    setView(next); setYaml(next.yaml)
  }, [path])
  React.useEffect(() => { setNotes([]); setError(""); setRenderFailed(false); void load().catch((exc) => setError(errorText(exc))) }, [load])

  async function run(name: string, action: () => Promise<void>) {
    const started = path
    setBusy(name); setError(""); setRenderFailed(false)
    try { await action(); if (live.current === started) await load(); await refresh() } catch (exc) { setError(errorText(exc)) } finally { setBusy("") }
  }

  if (!campaign) return null
  const dirty = view !== null && yaml !== view.yaml

  return (
    <div className="space-y-6">
      <PageHeader title={t("preview_title")} description={t("preview_help")}>
        <PostPicker value={picked} onChange={pick} />
      </PageHeader>
      {error && <Notice tone="error">{error}</Notice>}
      {view && picked && (
        <div className="grid gap-6 xl:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
          <Card>
            <CardHeader>
              <CardTitle>{t("edit_yaml")}</CardTitle>
              <CardDescription>{t("edit_yaml_help")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea value={yaml} onChange={(e) => setYaml(e.target.value)} spellCheck={false}
                className="h-[28rem] font-mono text-xs leading-relaxed" aria-label={t("edit_yaml")} />
              <div className="flex flex-wrap gap-2">
                <Button size="sm" disabled={!dirty || busy !== ""}
                  onClick={() => run("save", async () => { setNotes((await api.put<{ issues: Issue[] }>(path, { yaml })).issues) })}>
                  <Busy on={busy === "save"}><Save /> {t("save")}</Busy>
                </Button>
                <Button size="sm" variant="outline" disabled={dirty || busy !== ""}
                  onClick={() => run("status", async () => { await api.post(`${path}/status`, { status: view.status === "draft" ? "ready" : "draft" }) })}>
                  {view.status === "draft" ? t("mark_ready") : t("mark_draft")}
                </Button>
              </div>
              <IssueList issues={notes.length ? notes : view.issues} />
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><ImageIcon className="size-4" /> {t("images")}</CardTitle>
                <CardDescription>
                  {view.manifest.rendered_at ? t("rendered_at", { at: view.manifest.rendered_at }) : t("not_rendered")}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button size="sm" disabled={dirty || busy !== ""}
                  onClick={() => run("render", async () => {
                    const outcome = renderOutcome(await api.post<RenderAnswer>(`${path}/render`, {}), path, live.current)
                    if (outcome) { setNotes(outcome.notes); setRenderFailed(outcome.failed); setStamp(Date.now()) }
                  })}>
                  <Busy on={busy === "render"}><RefreshCw /> {t("render_button")}</Busy>
                </Button>
                {busy === "render" && <p className="text-xs text-muted-foreground">{t("rendering")}</p>}
                {renderFailed && <Notice tone="error">{t("render_failed")}</Notice>}
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                  {(view.manifest.slides ?? []).map((name) => {
                    const src = fileUrl(`/files/${campaign.slug}/${picked.lang}/${picked.id}/${name}`) + `&v=${stamp}`
                    return (
                      <a key={name} href={src} target="_blank" rel="noreferrer" className="group block">
                        <img src={src} alt={name} className="aspect-[4/5] w-full rounded-md border object-cover transition group-hover:opacity-90" />
                        <span className="text-xs text-muted-foreground">{name}</span>
                      </a>
                    )
                  })}
                </div>
                {Object.keys(view.texts).length > 0 && (
                  <Tabs defaultValue={Object.keys(view.texts)[0]}>
                    <TabsList>
                      {Object.keys(view.texts).map((name) => <TabsTrigger key={name} value={name}>{name}</TabsTrigger>)}
                    </TabsList>
                    {Object.entries(view.texts).map(([name, text]) => (
                      <TabsContent key={name} value={name}>
                        <pre className="max-h-72 overflow-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-sm">{text}</pre>
                      </TabsContent>
                    ))}
                  </Tabs>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><CheckCheck className="size-4" /> {t("approval")}</CardTitle>
                <CardDescription>{view.approved ? `✅ ${view.approval}` : view.approval}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {view.blockers.length > 0 ? (
                  <>
                    <p className="text-sm font-medium">{t("cannot_approve")}</p>
                    <ul className="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                      {view.blockers.map((b) => <li key={b}>{b}</li>)}
                    </ul>
                  </>
                ) : !view.approved ? (
                  <Button onClick={() => { setRead(false); setConfirmOpen(true) }}>{t("approve_button")}</Button>
                ) : null}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("approve_title")}</DialogTitle>
            <DialogDescription>{t("approve_explain")}</DialogDescription>
          </DialogHeader>
          <div className="flex items-start gap-3">
            <Switch id="read-all" checked={read} onCheckedChange={setRead} />
            <Label htmlFor="read-all" className="leading-snug">
              {t("approve_confirm", { lang: picked ? languageNames[picked.lang] : "" })}
            </Label>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmOpen(false)}>{t("cancel")}</Button>
            <Button disabled={!read || busy !== ""}
              onClick={() => run("approve", async () => { await api.post(`${path}/approve`, { confirm: true }); setConfirmOpen(false) })}>
              <Busy on={busy === "approve"}>{t("approve_button")}</Busy>
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
