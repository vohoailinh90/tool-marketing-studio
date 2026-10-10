import { Sparkles } from "lucide-react"
import * as React from "react"

import { AiModeSwitch, AiResults, PasteBox, ReadmeInput, type AiResult } from "@/components/ai-controls"
import { Busy, LanguageChips, PageHeader, errorText } from "@/components/common"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { api } from "@/lib/api"
import { useAiMode } from "@/lib/ai-mode"
import { languageNames, useI18n } from "@/lib/i18n"
import { useStudio } from "@/lib/studio"

function Positioning({ data }: { data: Record<string, unknown> | undefined }) {
  const { t } = useI18n()
  if (!data) return <p className="text-sm text-muted-foreground">{t("none_yet")}</p>
  const list = (value: unknown) => (Array.isArray(value) ? value.map(String) : [])
  return (
    <div className="space-y-3 text-sm">
      <p className="font-medium">{String(data.one_liner ?? "")}</p>
      <p className="text-muted-foreground">{String(data.audience ?? "")}</p>
      <ul className="list-disc space-y-1 pl-5">{list(data.pains).map((pain) => <li key={pain}>{pain}</li>)}</ul>
      {data.promise ? <p><span className="font-medium">{t("promise")}: </span>{String(data.promise)}</p> : null}
    </div>
  )
}

export function AnalysePage() {
  const { campaign, refresh } = useStudio()
  const { t } = useI18n()
  const [mode, setMode] = useAiMode()
  const [langs, setLangs] = React.useState<string[]>([])
  const [readme, setReadme] = React.useState("")
  const [busy, setBusy] = React.useState(false)
  const [results, setResults] = React.useState<AiResult[]>([])
  const [prompts, setPrompts] = React.useState<Record<string, string>>({})
  const [error, setError] = React.useState("")

  React.useEffect(() => { if (campaign) setLangs(campaign.langs) }, [campaign?.slug])
  if (!campaign) return null
  const base = `/api/campaigns/${campaign.slug}/ai`

  return (
    <div className="space-y-6">
      <PageHeader title={t("analyse_title")} description={t("analyse_help")} />
      <Card>
        <CardContent className="space-y-4">
          <LanguageChips langs={campaign.langs} value={langs} onChange={setLangs} />
          <AiModeSwitch mode={mode} setMode={setMode} />
          <ReadmeInput value={readme} onChange={setReadme} />
          {mode === "api" ? (
            <Button disabled={busy || langs.length === 0}
              onClick={async () => {
                setBusy(true); setError("")
                try {
                  const answer = await api.post<{ results: AiResult[] }>(`${base}/analyze`, { langs, readme })
                  setResults(answer.results); await refresh()
                } catch (exc) { setError(errorText(exc)) } finally { setBusy(false) }
              }}>
              <Busy on={busy}><Sparkles /> {t("analyse_button")}</Busy>
            </Button>
          ) : (
            <Button variant="outline" disabled={langs.length === 0}
              onClick={async () => {
                try { setPrompts((await api.post<{ prompts: Record<string, string> }>(`${base}/prompt`, { kind: "analyze", langs, readme })).prompts) }
                catch (exc) { setError(errorText(exc)) }
              }}>
              {t("make_prompts")}
            </Button>
          )}
          {error && <p className="text-sm text-destructive">{error}</p>}
          <AiResults results={results} />
          {mode === "paste" && Object.entries(prompts).map(([lang, prompt]) => (
            <PasteBox key={lang} lang={lang} prompt={prompt}
              onSubmit={async (text) => {
                const answer = await api.post<AiResult>(`${base}/paste`, { kind: "analyze", lang, text })
                await refresh()
                return { ...answer, lang }
              }} />
          ))}
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-3">
        {campaign.langs.map((lang) => (
          <Card key={lang}>
            <CardHeader>
              <CardTitle>{languageNames[lang]}</CardTitle>
              <CardDescription>{t("positioning")}</CardDescription>
            </CardHeader>
            <CardContent>
              <Positioning data={campaign.positioning[lang]} />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
