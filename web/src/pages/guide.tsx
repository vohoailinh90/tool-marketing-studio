import { PageHeader } from "@/components/common"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useI18n, type MessageKey } from "@/lib/i18n"

const sections: { title: MessageKey; items: MessageKey[] }[] = [
  { title: "guide_flow_title", items: ["guide_flow_1", "guide_flow_2", "guide_flow_3", "guide_flow_4", "guide_flow_5", "guide_flow_6"] },
  { title: "guide_fb_title", items: ["guide_fb_1", "guide_fb_2", "guide_fb_3", "guide_fb_4"] },
  { title: "guide_ai_title", items: ["guide_ai_1", "guide_ai_2", "guide_ai_3"] },
  { title: "guide_safe_title", items: ["guide_safe_1", "guide_safe_2", "guide_safe_3", "guide_safe_4"] },
]

export function GuidePage() {
  const { t } = useI18n()
  return (
    <div className="space-y-6">
      <PageHeader title={t("guide_title")} description={t("guide_help")} />
      <div className="grid gap-4 lg:grid-cols-2">
        {sections.map((section) => (
          <Card key={section.title}>
            <CardHeader><CardTitle>{t(section.title)}</CardTitle></CardHeader>
            <CardContent>
              <ol className="list-decimal space-y-2 pl-5 text-sm">{section.items.map((key) => <li key={key}>{t(key)}</li>)}</ol>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
