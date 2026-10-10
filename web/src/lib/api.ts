/** Calls to the local studio server. Every call carries the session token the server
 *  put in index.html; without it the server refuses, so other sites cannot use it. */

export type Issue = { level: "error" | "warn"; where: string; message: string }
export type Usage = { input_tokens: number; output_tokens: number }

export type StudioState = {
  campaigns: string[]
  langs: { code: string; name: string }[]
  platforms: { code: string; api: boolean }[]
  slots: { id: string; purpose: string }[]
  ai: { has_key: boolean; model: string }
  facebook: { configured: boolean; page_name: string; checked_at: string }
}

export type PostSummary = {
  id: string
  lang: string
  status: string
  approved: boolean
  approval: string
  rendered: boolean
  thumb: string | null
  errors: number
  warnings: number
  published: Record<string, string | null>
}

export type CampaignView = {
  slug: string
  tool: string
  tool_name: string
  brand: { emoji?: string; accent?: string }
  langs: string[]
  platforms: string[]
  slots: string[]
  goal: string
  links: Record<string, "configured" | "placeholder">
  positioning: Record<string, Record<string, unknown>>
  posts: PostSummary[]
  issues: Issue[]
}

export type LedgerRow = {
  state?: string
  url?: string
  error?: string
  method?: string
  published_at?: string
  where?: string
} | null

export type PostView = {
  id: string
  lang: string
  status: string
  yaml: string
  issues: Issue[]
  manifest: { slides?: string[]; texts?: string[]; overflow?: number[]; rendered_at?: string; sha?: string }
  texts: Record<string, string>
  approved: boolean
  approval: string
  blockers: string[]
  links: Record<string, string>
  ledger: Record<string, LedgerRow>
  manual: Record<string, NonNullable<LedgerRow>[]>
}

export type HistoryRow = {
  campaign: string
  tool: string
  tool_name: string
  post: string
  lang: string
  platform: string
  state: string
  method: string
  published_at: string
  url: string
  where: string
  comments: number
  totals: Record<string, number>
  scanned_at: string
}

export type Insight = {
  summary?: string
  demand?: { level?: string; reasoning?: string }
  by_language?: { lang: string; signal: string; notes?: string }[]
  requests?: { need: string; mentions?: number; quotes?: string[] }[]
  objections?: { objection: string; mentions?: number; response?: string }[]
  segments?: { who: string; why?: string }[]
  next_steps?: { priority: number; action: string; why?: string; evidence?: string; effort?: string }[]
  next_posts?: string[]
  questions?: string[]
}

export type MetricsLang = {
  lang: string
  verdict: "GO" | "NOT_YET" | "INSUFFICIENT_DATA"
  lines: string[]
  totals: Record<string, number | null>
  rates: Record<string, { value: number | null; n: number }>
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

function token(): string {
  return document.querySelector<HTMLMetaElement>('meta[name="studio-token"]')?.content ?? ""
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const response = await fetch(path, {
    method,
    headers: { "X-Studio-Token": token(), ...(body !== undefined ? { "Content-Type": "application/json" } : {}) },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new ApiError(response.status, (data as { detail?: string }).detail ?? response.statusText)
  return data as T
}

export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body: unknown = {}) => request<T>("POST", path, body),
  put: <T>(path: string, body: unknown) => request<T>("PUT", path, body),
}

/** Images and zip files are plain links, so the token goes in the query string. */
export function fileUrl(path: string): string {
  return `${path}?t=${encodeURIComponent(token())}`
}

export function postPath(slug: string, lang: string, id: string): string {
  return `/api/campaigns/${slug}/posts/${lang}/${id}`
}
