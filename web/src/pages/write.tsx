import { PenLine } from "lucide-react"
import * as React from "react"

import { AiModeSwitch, AiResults, PasteBox, ReadmeInput, type AiResult } from "@/components/ai-controls"
import { Busy, ChipPicker, LanguageChips, PageHeader, errorText } from "@/components/common"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import { api } from "@/lib/api"
import { useAiMode } from "@/lib/ai-mode"
import { useI18n } from "@/lib/i18n"
import { useStudio } from "@/lib/studio"

const CUSTOM = "__custom__"

export function WritePage() {
  const { campaign, state, refresh } = useStudio()
  const { t } = useI18n()
  const [mode, setMode] = useAiMode()
  const [slot, setSlot] = React.useState("01-pain")
  const [custom, setCustom] = React.useState("07-")
  const [langs, setLangs] = React.useState<string[]>([])
  const [platforms, setPlatforms] = React.useState<string[]>([])
  const [guidance, setGuidance] = React.useState("")
  const [readme, setReadme] = React.useState("")
  const [overwrite, setOverwrite] = React.useState(false)
  const [busy, setBusy] = React.useState(false)
  const [results, setResults] = React.useState<AiResult[]>([])
  const [prompts, setPrompts] = React.useState<Record<string, string>>({})
  const [error, setError] = React.useState("")

  React.useEffect(() => {
    if (campaign) { setLangs(campaign.langs); setPlatforms(campaign.platforms) }
  }, [campaign?.slug])
  if (!campaign || !state) return null

  const slots = Array.from(new Set([...state.slots.map((s) => s.id), ...campaign.slots]))
  const postId = slot === CUSTOM ? custom.trim() : slot
  const purpose = state.slots.find((s) => s.id === postId)?.purpose ?? t("custom_slot_help")
  const base = `/api/campaigns/${campaign.slug}/ai`
  const payload = { slot: postId, langs, platforms, guidance, readme, overwrite }

  return (
    <div className="space-y-6">
      <PageHeader title={t("write_title")} description={t("write_help")} />
      <Card>
        <CardContent className="grid gap-5 lg:grid-cols-2">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>{t("slot")}</Label>
              <div className="flex flex-wrap gap-2">
                <Select value={slot} onValueChange={setSlot}>
                  <SelectTrigger className="min-w-48"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {slots.map((id) => <SelectItem key={id} value={id}>{id}</SelectItem>)}
                    <SelectItem value={CUSTOM}>{t("custom_slot")}</SelectItem>
                  </SelectContent>
                </Select>
                {slot === CUSTOM && <Input value={custom} onChange={(e) => setCustom(e.target.value)} className="w-40" aria-label={t("custom_slot_id")} />}
              </div>
              <p className="text-xs text-muted-foreground">{purpose}</p>
            </div>
            <div className="space-y-2">
              <Label>{t("content_langs")}</Label>
              <LanguageChips langs={campaign.langs} value={langs} onChange={setLangs} />
            </div>
            <div className="space-y-2">
              <Label>{t("platforms")}</Label>
              <ChipPicker label={t("platforms")} value={platforms} onChange={setPlatforms}
                options={state.platforms.map((p) => ({ code: p.code, label: p.code }))} />
              <p className="text-xs text-muted-foreground">{t("platform_note")}</p>
            </div>
          </div>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="guidance">{t("guidance")}</Label>
              <Textarea id="guidance" value={guidance} onChange={(e) => setGuidance(e.target.value)} className="h-28" />
            </div>
            <ReadmeInput value={readme} onChange={setReadme} />
            <div className="flex items-center gap-2">
              <Switch id="overwrite" checked={overwrite} onCheckedChange={setOverwrite} />
              <Label htmlFor="overwrite">{t("overwrite_draft")}</Label>
            </div>
          </div>
          <div className="space-y-4 lg:col-span-2">
            <AiModeSwitch mode={mode} setMode={setMode} />
            {mode === "api" ? (
              <Button disabled={busy || !postId || langs.length === 0 || platforms.length === 0}
                onClick={async () => {
                  setBusy(true); setError("")
                  try { setResults((await api.post<{ results: AiResult[] }>(`${base}/draft`, payload)).results); await refresh() }
                  catch (exc) { setError(errorText(exc)) } finally { setBusy(false) }
                }}>
                <Busy on={busy}><PenLine /> {t("write_button", { n: langs.length })}</Busy>
              </Button>
            ) : (
              <Button variant="outline" disabled={!postId || langs.length === 0 || platforms.length === 0}
                onClick={async () => {
                  setError("")
                  try { setPrompts((await api.post<{ prompts: Record<string, string> }>(`${base}/prompt`, { kind: "post", ...payload })).prompts) }
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
                  const answer = await api.post<AiResult>(`${base}/paste`, { kind: "post", lang, text, ...payload })
                  await refresh()
                  return { ...answer, lang }
                }} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
