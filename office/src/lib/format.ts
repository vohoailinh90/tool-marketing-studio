import { INTL_TAG, type Locale, type Translate } from "@/lib/i18n"

/** 75 -> "01:15": elapsed time in a run or a replay. */
export function mmss(seconds: number): string {
  const whole = Math.max(0, Math.floor(seconds))
  return `${String(Math.floor(whole / 60)).padStart(2, "0")}:${String(whole % 60).padStart(2, "0")}`
}

/** A moment as the viewer's clock reads it. */
export function clock(epochSeconds: number, locale: Locale): string {
  return new Intl.DateTimeFormat(INTL_TAG[locale], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(epochSeconds * 1000)
}

export function compact(value: number, locale: Locale): string {
  return new Intl.NumberFormat(INTL_TAG[locale], { notation: "compact", maximumFractionDigits: 1 }).format(value)
}

export function seconds(ms: number, locale: Locale): string {
  return `${new Intl.NumberFormat(INTL_TAG[locale], { maximumFractionDigits: 1 }).format(ms / 1000)} s`
}

/** The message for `key`, or the one for `fallbackKey` when the catalogs have no entry (an agent the roster does not name). */
export function tOr(t: Translate, key: string, fallbackKey: string, params?: Parameters<Translate>[1]): string {
  const message = t(key, params)
  return message === key ? t(fallbackKey, params) : message
}

/** The message for `key`, or `fallback` itself (an agent id, say) when the catalogs have no entry. */
export function labelOr(t: Translate, key: string, fallback: string): string {
  const message = t(key)
  return message === key ? fallback : message
}
