import { Bot, ClipboardPaste, FileUp } from "lucide-react"
import * as React from "react"

import { Busy, CopyButton, IssueList, Notice } from "@/components/common"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import type { Issue, Usage } from "@/lib/api"
import { languageNames, useI18n } from "@/lib/i18n"
import { useStudio } from "@/lib/studio"

export function AiModeSwitch({ mode, setMode }: { mode: "api" | "paste"; setMode: (m: "api" | "paste") => void }) {
  const { t } = useI18n()
  const { state } = useStudio()
  return (
    <div className="flex flex-wrap items-center gap-3 rounded-md border px-3 py-2">
      {mode === "api" ? <Bot className="size-4" /> : <ClipboardPaste className="size-4" />}
      <Label htmlFor="ai-mode" className="text-sm">{t("ai_mode_paste")}</Label>
      <Switch id="ai-mode" checked={mode === "paste"} onCheckedChange={(on) => setMode(on ? "paste" : "api")} />
      <span className="text-xs text-muted-foreground">
        {mode === "api"
          ? state?.ai.has_key
            ? t("ai_mode_api_on", { model: state.ai.model })
            : t("no_api_key")
          : t("ai_mode_paste_help")}
      </span>
    </div>
  )
}

/** The tool README goes to the AI only when asked: it is someone's text, not instructions. */
export function ReadmeInput({ value, onChange }: { value: string; onChange: (text: string) => void }) {
  const { t } = useI18n()
  const [on, setOn] = React.useState(false)
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Switch id="use-readme" checked={on} onCheckedChange={(next) => { setOn(next); if (!next) onChange("") }} />
        <Label htmlFor="use-readme">{t("use_readme")}</Label>
      </div>
      {on && (
        <div className="space-y-2">
          <label className="inline-flex cursor-pointer items-center gap-2 text-sm text-muted-foreground">
            <FileUp className="size-4" />
            <input type="file" accept=".md,.txt" className="text-sm"
              onChange={async (event) => { const file = event.target.files?.[0]; if (file) onChange(await file.text()) }} />
          </label>
          <Textarea value={value} onChange={(e) => onChange(e.target.value)} placeholder={t("readme_paste")} className="h-32 font-mono text-xs" />
        </div>
      )}
    </div>
  )
}

export type AiResult = { lang: string; issues?: Issue[]; saved?: string | null; usage?: Usage; error?: string }

export function AiResults({ results }: { results: AiResult[] }) {
  const { t } = useI18n()
  if (results.length === 0) return null
  return (
    <div className="space-y-3">
      {results.map((result) => (
        <div key={result.lang} className="space-y-2 rounded-md border p-3">
          <p className="text-sm font-semibold">{languageNames[result.lang] ?? result.lang}</p>
          {result.error && <Notice tone="error">{result.error}</Notice>}
          {result.issues && <IssueList issues={result.issues} />}
          {result.saved && <Notice tone="success">{t("saved_to", { path: result.saved })}</Notice>}
          {result.usage && (
            <p className="text-xs text-muted-foreground">
              {t("tokens_used", { input: result.usage.input_tokens, output: result.usage.output_tokens })}
            </p>
          )}
        </div>
      ))}
    </div>
  )
}

/** Copy-paste mode for one language: the prompt to copy, a box for the answer, and the check. */
export function PasteBox({ lang, prompt, onSubmit }: { lang: string; prompt: string; onSubmit: (text: string) => Promise<AiResult> }) {
  const { t } = useI18n()
  const [text, setText] = React.useState("")
  const [busy, setBusy] = React.useState(false)
  const [result, setResult] = React.useState<AiResult | null>(null)
  return (
    <div className="space-y-3 rounded-md border p-3">
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-semibold">{languageNames[lang] ?? lang}</p>
        <CopyButton text={prompt} />
      </div>
      <details>
        <summary className="cursor-pointer text-xs text-muted-foreground">{t("show_prompt")}</summary>
        <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-xs">{prompt}</pre>
      </details>
      <Textarea value={text} onChange={(e) => setText(e.target.value)} placeholder={t("paste_answer")} className="h-32 font-mono text-xs" />
      <Button size="sm" disabled={!text.trim() || busy}
        onClick={async () => { setBusy(true); try { setResult(await onSubmit(text)) } finally { setBusy(false) } }}>
        <Busy on={busy}>{t("check_and_save")}</Busy>
      </Button>
      {result && <AiResults results={[result]} />}
    </div>
  )
}
