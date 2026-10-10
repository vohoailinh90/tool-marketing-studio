import { Lightbulb, Plus, Sparkles, TrendingUp } from "lucide-react"
import * as React from "react"

import { AiModeSwitch, PasteBox, type AiResult } from "@/components/ai-controls"
import { Busy, IssueList, Notice, PageHeader, errorText } from "@/components/common"
import { StatusBadge, type StatusTone } from "@/components/dashboard/status-badge"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Textarea } from "@/components/ui/textarea"
import { api, type Insight, type Issue, type MetricsLang } from "@/lib/api"
import { useAiMode } from "@/lib/ai-mode"
import { languageNames, useI18n } from "@/lib/i18n"
import { useStudio } from "@/lib/studio"

const verdictTone: Record<string, StatusTone> = { GO: "success", NOT_YET: "warning", INSUFFICIENT_DATA: "neutral" }
const levelTone: Record<string, StatusTone> = { strong: "success", moderate: "info", weak: "warning", unclear: "neutral" }
const COUNT_FIELDS = ["reach", "reactions", "comments", "shares", "link_clicks", "survey_responses", "signups", "dms"] as const

function pct(value: number | null) {
  return value === null ? "—" : `${(value * 100).toFixed(1)}%`
}

function MetricsCards({ langs }: { langs: MetricsLang[] }) {
  const { t } = useI18n()
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {langs.map((m) => (
        <Card key={m.lang}>
          <CardHeader>
            <CardTitle className="flex items-center justify-between gap-2">
              {languageNames[m.lang]}
              <StatusBadge tone={verdictTone[m.verdict]}>{t(`verdict_${m.verdict}` as "verdict_GO")}</StatusBadge>
            </CardTitle>
            <CardDescription>{t("verdict_help")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(m.rates).map(([name, rate]) => (
                <div key={name} className="rounded-md bg-muted/60 p-2">
                  <p className="text-xs text-muted-foreground">{t(`rate_${name}` as "rate_click_rate")}</p>
                  <p className="font-semibold tabular-nums">{pct(rate.value)}</p>
                  <p className="text-xs text-muted-foreground">n = {rate.n}</p>
                </div>
              ))}
            </div>
            <ul className="space-y-1 text-xs text-muted-foreground">{m.lines.map((line) => <li key={line}>{line}</li>)}</ul>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

function AddNumbers({ onSaved }: { onSaved: () => Promise<void> }) {
  const { campaign } = useStudio()
  const { t } = useI18n()
  const [form, setForm] = React.useState<Record<string, string>>({ date: new Date().toISOString().slice(0, 10) })
  const [busy, setBusy] = React.useState(false)
  const [error, setError] = React.useState("")
  if (!campaign) return null
  const set = (key: string, value: string) => setForm({ ...form, [key]: value })
  const choice = (key: string, values: string[], label: string) => (
    <div className="space-y-1">
      <Label>{label}</Label>
      <Select value={form[key] ?? ""} onValueChange={(v) => set(key, v)}>
        <SelectTrigger className="w-full"><SelectValue placeholder="—" /></SelectTrigger>
        <SelectContent>{values.map((v) => <SelectItem key={v} value={v}>{v}</SelectItem>)}</SelectContent>
      </Select>
    </div>
  )
  return (
    <details className="rounded-md border p-3">
      <summary className="flex cursor-pointer items-center gap-2 text-sm font-medium"><Plus className="size-4" /> {t("add_numbers")}</summary>
      <p className="mt-2 text-xs text-muted-foreground">{t("add_numbers_help")}</p>
      <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="space-y-1"><Label>{t("col_when")}</Label><Input type="date" value={form.date ?? ""} onChange={(e) => set("date", e.target.value)} /></div>
        {choice("post", campaign.slots, t("post"))}
        {choice("lang", campaign.langs, t("content_langs"))}
        {choice("platform", campaign.platforms, t("col_platform"))}
        {COUNT_FIELDS.map((field) => (
          <div key={field} className="space-y-1">
            <Label>{t(`count_${field}` as "count_reach")}</Label>
            <Input inputMode="numeric" value={form[field] ?? ""} onChange={(e) => set(field, e.target.value.replace(/\D/g, ""))} />
          </div>
        ))}
      </div>
      <Button className="mt-3" size="sm" disabled={busy || !form.post || !form.lang || !form.platform}
        onClick={async () => {
          setBusy(true); setError("")
          try { await api.post(`/api/campaigns/${campaign.slug}/metrics`, form); await onSaved(); setForm({ date: form.date }) }
          catch (exc) { setError(errorText(exc)) } finally { setBusy(false) }
        }}>
        <Busy on={busy}>{t("save")}</Busy>
      </Button>
      {error && <p className="mt-2 text-sm text-destructive">{error}</p>}
    </details>
  )
}

function Report({ report, date, lang }: { report: Insight; date: string; lang: string }) {
  const { t } = useI18n()
  const level = report.demand?.level ?? "unclear"
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex flex-wrap items-center gap-2">
            <TrendingUp className="size-4" /> {t("demand")}
            <StatusBadge tone={levelTone[level] ?? "neutral"}>{t(`level_${level}` as "level_strong")}</StatusBadge>
            <Badge variant="outline">{date} · {languageNames[lang] ?? lang}</Badge>
          </CardTitle>
          <CardDescription>{report.demand?.reasoning}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <p>{report.summary}</p>
          {(report.by_language ?? []).length > 0 && (
            <div className="flex flex-wrap gap-2">
              {(report.by_language ?? []).map((row) => (
                <span key={row.lang} className="flex items-center gap-2 rounded-md border px-2 py-1">
                  {languageNames[row.lang] ?? row.lang}
                  <StatusBadge tone={levelTone[row.signal] ?? "neutral"}>{t(`level_${row.signal}` as "level_strong")}</StatusBadge>
                  <span className="text-xs text-muted-foreground">{row.notes}</span>
                </span>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Lightbulb className="size-4" /> {t("next_steps")}</CardTitle></CardHeader>
        <CardContent>
          <ol className="space-y-3">
            {[...(report.next_steps ?? [])].sort((a, b) => a.priority - b.priority).map((step) => (
              <li key={step.priority} className="flex gap-3">
                <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">{step.priority}</span>
                <div className="space-y-1 text-sm">
                  <p className="font-medium">{step.action} {step.effort && <Badge variant="outline">{step.effort}</Badge>}</p>
                  <p className="text-muted-foreground">{step.why}</p>
                  {step.evidence && <p className="text-xs text-muted-foreground">{t("evidence")}: {step.evidence}</p>}
                </div>
              </li>
            ))}
          </ol>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>{t("requests")}</CardTitle></CardHeader>
          <CardContent>
            <Table>
              <TableHeader><TableRow><TableHead>{t("need")}</TableHead><TableHead className="text-right">{t("mentions")}</TableHead></TableRow></TableHeader>
              <TableBody>
                {(report.requests ?? []).map((row) => (
                  <TableRow key={row.need}>
                    <TableCell>
                      <p>{row.need}</p>
                      {(row.quotes ?? []).map((q) => <p key={q} className="mt-1 border-l-2 pl-2 text-xs italic text-muted-foreground">“{q}”</p>)}
                    </TableCell>
                    <TableCell className="text-right tabular-nums">{row.mentions ?? 0}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>{t("objections")}</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm">
            {(report.objections ?? []).map((row) => (
              <div key={row.objection}>
                <p className="font-medium">{row.objection} <span className="text-muted-foreground">({row.mentions ?? 0})</span></p>
                <p className="text-muted-foreground">{row.response}</p>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>{t("next_posts")}</CardTitle></CardHeader>
          <CardContent><ul className="list-disc space-y-1 pl-5 text-sm">{(report.next_posts ?? []).map((p) => <li key={p}>{p}</li>)}</ul></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>{t("questions")}</CardTitle></CardHeader>
          <CardContent><ul className="list-disc space-y-1 pl-5 text-sm">{(report.questions ?? []).map((q) => <li key={q}>{q}</li>)}</ul></CardContent>
        </Card>
      </div>
    </div>
  )
}

export function InsightsPage() {
  const { campaign } = useStudio()
  const { t, lang: uiLang } = useI18n()
  const [mode, setMode] = useAiMode()
  const [metrics, setMetrics] = React.useState<{ rows: number; langs: MetricsLang[] } | null>(null)
  const [reports, setReports] = React.useState<{ date: string; lang: string; report: Insight }[]>([])
  const [reportLang, setReportLang] = React.useState<string>(uiLang)
  const [survey, setSurvey] = React.useState("")
  const [busy, setBusy] = React.useState(false)
  const [issues, setIssues] = React.useState<Issue[] | null>(null)
  const [prompt, setPrompt] = React.useState("")
  const [error, setError] = React.useState("")
  const [shown, setShown] = React.useState(0)

  const slug = campaign?.slug
  const load = React.useCallback(async () => {
    if (!slug) return
    setMetrics(await api.get(`/api/campaigns/${slug}/metrics`))
    setReports((await api.get<{ reports: typeof reports }>(`/api/campaigns/${slug}/insights`)).reports)
  }, [slug])
  React.useEffect(() => { void load().catch((e) => setError(errorText(e))) }, [load])
  if (!campaign) return null
  const base = `/api/campaigns/${campaign.slug}/ai/insights`
  const current = reports[shown]

  return (
    <div className="space-y-6">
      <PageHeader title={t("insights_title")} description={t("insights_help")} />
      {error && <Notice tone="error">{error}</Notice>}

      <section className="space-y-3">
        <h3 className="text-sm font-semibold">{t("numbers_title")}</h3>
        {metrics && metrics.rows === 0 && <Notice>{t("no_numbers")}</Notice>}
        {metrics && <MetricsCards langs={metrics.langs} />}
        <AddNumbers onSaved={load} />
      </section>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Sparkles className="size-4" /> {t("ai_analysis")}</CardTitle>
          <CardDescription>{t("ai_analysis_help")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-end gap-4">
            <div className="space-y-1">
              <Label>{t("report_language")}</Label>
              <Select value={reportLang} onValueChange={setReportLang}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>{["vi", "ja", "en"].map((code) => <SelectItem key={code} value={code}>{languageNames[code]}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <AiModeSwitch mode={mode} setMode={setMode} />
          </div>
          <div className="space-y-1">
            <Label htmlFor="survey">{t("survey_summary")}</Label>
            <Textarea id="survey" value={survey} onChange={(e) => setSurvey(e.target.value)} className="h-24" placeholder={t("survey_summary_hint")} />
          </div>
          {mode === "api" ? (
            <Button disabled={busy}
              onClick={async () => {
                setBusy(true); setError(""); setIssues(null)
                try {
                  const answer = await api.post<{ issues: Issue[] }>(base, { lang: reportLang, survey })
                  setIssues(answer.issues); await load(); setShown(0)
                } catch (exc) { setError(errorText(exc)) } finally { setBusy(false) }
              }}>
              <Busy on={busy}><Sparkles /> {t("analyse_demand")}</Busy>
            </Button>
          ) : (
            <Button variant="outline" onClick={async () => {
              try { setPrompt((await api.post<{ prompt: string }>(`${base}/prompt`, { lang: reportLang, survey })).prompt) }
              catch (exc) { setError(errorText(exc)) }
            }}>{t("make_prompts")}</Button>
          )}
          {issues && <IssueList issues={issues} />}
          {mode === "paste" && prompt && (
            <PasteBox lang={reportLang} prompt={prompt} onSubmit={async (text) => {
              const answer = await api.post<AiResult>(`${base}/paste`, { lang: reportLang, survey, text })
              await load(); setShown(0)
              return { ...answer, lang: reportLang, saved: answer.saved ? String(answer.saved) : null }
            }} />
          )}
        </CardContent>
      </Card>

      {reports.length > 0 && current && (
        <section className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-sm font-semibold">{t("reports")}</h3>
            {reports.map((r, index) => (
              <Button key={`${r.date}-${r.lang}`} size="sm" variant={index === shown ? "default" : "outline"} onClick={() => setShown(index)}>
                {r.date} · {r.lang}
              </Button>
            ))}
          </div>
          <Report report={current.report} date={current.date} lang={current.lang} />
        </section>
      )}
    </div>
  )
}
