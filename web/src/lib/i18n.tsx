import * as React from "react"

import en from "@/locales/en.json"
import ja from "@/locales/ja.json"
import vi from "@/locales/vi.json"

export const uiLanguages = ["vi", "ja", "en"] as const
export type UiLanguage = (typeof uiLanguages)[number]
export type MessageKey = keyof typeof en

const catalogs: Record<UiLanguage, Record<string, string>> = { vi, ja, en }
const STORAGE_KEY = "tool-marketing-studio-ui-lang"

type I18n = { lang: UiLanguage; setLang: (lang: UiLanguage) => void; t: (key: MessageKey, values?: Record<string, string | number>) => string }

const I18nContext = React.createContext<I18n | null>(null)

function initial(): UiLanguage {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored && (uiLanguages as readonly string[]).includes(stored)) return stored as UiLanguage
  } catch {
    /* storage blocked: fall back to Vietnamese */
  }
  return "vi"
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = React.useState<UiLanguage>(initial)
  const setLang = React.useCallback((next: UiLanguage) => {
    setLangState(next)
    try {
      localStorage.setItem(STORAGE_KEY, next)
    } catch {
      /* ignore */
    }
  }, [])
  React.useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])
  const t = React.useCallback(
    (key: MessageKey, values?: Record<string, string | number>) => {
      let text = catalogs[lang][key] ?? catalogs.en[key] ?? key
      for (const [name, value] of Object.entries(values ?? {})) text = text.replaceAll(`{${name}}`, String(value))
      return text
    },
    [lang],
  )
  const value = React.useMemo(() => ({ lang, setLang, t }), [lang, setLang, t])
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n() {
  const context = React.useContext(I18nContext)
  if (!context) throw new Error("useI18n must be used within an I18nProvider")
  return context
}

export const languageNames: Record<string, string> = { vi: "Tiếng Việt", ja: "日本語", en: "English" }
