import { CheckCircle2, FileStack, Link2, Send } from "lucide-react"
import { Link } from "react-router-dom"

import { IssueList, PageHeader, PostStatus } from "@/components/common"
import { StatCard } from "@/components/stat-card"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { fileUrl } from "@/lib/api"
import { languageNames, useI18n } from "@/lib/i18n"
import { useStudio } from "@/lib/studio"

export function OverviewPage() {
  const { campaign } = useStudio()
  const { t } = useI18n()
  if (!campaign) return <p className="text-sm text-muted-foreground">{t("loading")}</p>

  const posts = campaign.posts.filter((p) => campaign.langs.includes(p.lang))
  const approved = posts.filter((p) => p.approved).length
  const published = posts.filter((p) => Object.values(p.published).some((s) => s === "done")).length
  const linksReady = Object.values(campaign.links).every((state) => state === "configured")

  return (
    <div className="space-y-6">
      <PageHeader title={`${campaign.brand.emoji ?? ""} ${campaign.tool_name}`} description={campaign.goal} />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label={t("kpi_posts")} value={String(posts.length)} hint={t("kpi_posts_hint", { langs: campaign.langs.length, slots: campaign.slots.length })} icon={FileStack} />
        <StatCard label={t("kpi_approved")} value={`${approved}/${posts.length}`} hint={t("kpi_approved_hint")} icon={CheckCircle2} />
        <StatCard label={t("kpi_published")} value={String(published)} hint={t("kpi_published_hint")} icon={Send} />
        <StatCard label={t("kpi_links")} value={linksReady ? t("ready") : t("not_ready")}
          hint={linksReady ? t("kpi_links_ok") : t("kpi_links_missing")} trend={linksReady ? "up" : "down"} icon={Link2} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t("matrix_title")}</CardTitle>
          <CardDescription>{t("matrix_help")}</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("post")}</TableHead>
                {campaign.langs.map((lang) => <TableHead key={lang}>{languageNames[lang]}</TableHead>)}
              </TableRow>
            </TableHeader>
            <TableBody>
              {campaign.slots.map((slot) => (
                <TableRow key={slot}>
                  <TableCell className="font-medium">{slot}</TableCell>
                  {campaign.langs.map((lang) => {
                    const post = posts.find((p) => p.id === slot && p.lang === lang)
                    return (
                      <TableCell key={lang}>
                        {post ? (
                          <Link to={`/preview?post=${slot}&lang=${lang}`} className="flex items-center gap-3 hover:opacity-80">
                            {post.thumb ? (
                              <img src={fileUrl(`/files/${campaign.slug}/${lang}/${slot}/${post.thumb}`)} alt=""
                                className="h-14 w-11 rounded border object-cover" />
                            ) : (
                              <span className="flex h-14 w-11 items-center justify-center rounded border border-dashed text-[10px] text-muted-foreground">PNG</span>
                            )}
                            <PostStatus post={post} />
                          </Link>
                        ) : (
                          <Badge variant="outline">{t("missing")}</Badge>
                        )}
                      </TableCell>
                    )
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t("workflow_title")}</CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="list-decimal space-y-2 pl-5 text-sm">
              <li>{t("workflow_1")}</li>
              <li>{t("workflow_2")}</li>
              <li>{t("workflow_3")}</li>
              <li>{t("workflow_4")}</li>
              <li>{t("workflow_5")}</li>
            </ol>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>{t("campaign_checks")}</CardTitle>
            <CardDescription>{t("campaign_checks_help")}</CardDescription>
          </CardHeader>
          <CardContent>
            <IssueList issues={campaign.issues} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
