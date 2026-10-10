import { Megaphone, Menu } from "lucide-react"
import * as React from "react"
import { Outlet, useLocation } from "react-router-dom"

import { navItems } from "@/components/layout/nav-items"
import { SidebarNav } from "@/components/layout/sidebar-nav"
import { ThemeToggle } from "@/components/theme-toggle"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet"
import { languageNames, uiLanguages, useI18n, type UiLanguage } from "@/lib/i18n"
import { useStudio } from "@/lib/studio"

function BrandMark() {
  return (
    <div className="flex h-14 items-center gap-2 border-b border-sidebar-border px-4">
      <div className="flex size-7 items-center justify-center rounded-md bg-sidebar-primary text-sidebar-primary-foreground">
        <Megaphone className="size-4" />
      </div>
      <span className="text-sm font-semibold text-sidebar-foreground">Tool Marketing Studio</span>
    </div>
  )
}

function PageTitle() {
  const location = useLocation()
  const { t } = useI18n()
  const current = navItems.find((item) =>
    item.end ? location.pathname === item.to : location.pathname.startsWith(item.to),
  )
  return <h1 className="text-sm font-semibold">{current ? t(current.label) : "Tool Marketing Studio"}</h1>
}

function CampaignPicker() {
  const { state, slug, setSlug } = useStudio()
  const { t } = useI18n()
  if (!state || state.campaigns.length === 0) return null
  return (
    <Select value={slug} onValueChange={setSlug}>
      <SelectTrigger size="sm" aria-label={t("campaign")} className="max-w-48">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {state.campaigns.map((name) => (
          <SelectItem key={name} value={name}>
            {name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

function UiLanguagePicker() {
  const { lang, setLang, t } = useI18n()
  return (
    <Select value={lang} onValueChange={(value) => setLang(value as UiLanguage)}>
      <SelectTrigger size="sm" aria-label={t("ui_language")}>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {uiLanguages.map((code) => (
          <SelectItem key={code} value={code}>
            {languageNames[code]}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const { error } = useStudio()
  const { t } = useI18n()

  return (
    <div className="flex min-h-svh w-full bg-background text-foreground">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground md:flex">
        <BrandMark />
        <SidebarNav />
        <div className="border-t border-sidebar-border p-3 text-xs text-sidebar-foreground/60">
          {t("local_only")}
        </div>
      </aside>

      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <SheetContent side="left" className="w-64 border-sidebar-border bg-sidebar p-0 text-sidebar-foreground">
          <SheetTitle className="sr-only">Menu</SheetTitle>
          <BrandMark />
          <SidebarNav onNavigate={() => setMobileOpen(false)} />
        </SheetContent>
      </Sheet>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center gap-3 border-b px-4">
          <Button variant="ghost" size="icon" className="md:hidden" aria-label="Open menu" onClick={() => setMobileOpen(true)}>
            <Menu />
          </Button>
          <PageTitle />
          <div className="ml-auto flex items-center gap-2">
            <CampaignPicker />
            <UiLanguagePicker />
            <ThemeToggle />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          {error && (
            <p role="alert" className="mb-4 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </p>
          )}
          <Outlet />
        </main>
      </div>
    </div>
  )
}
