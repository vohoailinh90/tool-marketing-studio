import * as React from "react"
import { useSearchParams } from "react-router-dom"

import { PostStatus } from "@/components/common"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { PostSummary } from "@/lib/api"
import { languageNames, useI18n } from "@/lib/i18n"
import { useStudio } from "@/lib/studio"

/** The post a page works on, kept in the URL (?post=…&lang=…) so links from Overview land on it. */
export function usePickedPost(): [PostSummary | null, (post: PostSummary) => void] {
  const { campaign } = useStudio()
  const [params, setParams] = useSearchParams()
  const posts = campaign?.posts.filter((p) => campaign.langs.includes(p.lang)) ?? []
  const picked = posts.find((p) => p.id === params.get("post") && p.lang === params.get("lang")) ?? posts[0] ?? null
  const pick = React.useCallback((post: PostSummary) => setParams({ post: post.id, lang: post.lang }), [setParams])
  return [picked, pick]
}

export function PostPicker({ value, onChange }: { value: PostSummary | null; onChange: (post: PostSummary) => void }) {
  const { campaign } = useStudio()
  const { t } = useI18n()
  const posts = campaign?.posts.filter((p) => campaign.langs.includes(p.lang)) ?? []
  if (posts.length === 0) return <p className="text-sm text-muted-foreground">{t("no_posts")}</p>
  const key = (p: PostSummary) => `${p.id}|${p.lang}`
  return (
    <div className="flex flex-wrap items-center gap-3">
      <Select value={value ? key(value) : ""} onValueChange={(k) => { const p = posts.find((x) => key(x) === k); if (p) onChange(p) }}>
        <SelectTrigger className="min-w-64" aria-label={t("post")}><SelectValue /></SelectTrigger>
        <SelectContent>
          {posts.map((p) => (
            <SelectItem key={key(p)} value={key(p)}>{p.id} · {languageNames[p.lang]}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      {value && <PostStatus post={value} />}
    </div>
  )
}
