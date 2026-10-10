import * as React from "react"

import { api, type CampaignView, type StudioState } from "@/lib/api"

type Studio = {
  state: StudioState | null
  slug: string
  setSlug: (slug: string) => void
  campaign: CampaignView | null
  error: string
  refresh: () => Promise<void>
}

const StudioContext = React.createContext<Studio | null>(null)

/** The selected campaign and the server's view of it, shared by every page. */
export function StudioProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = React.useState<StudioState | null>(null)
  const [slug, setSlug] = React.useState("")
  const [campaign, setCampaign] = React.useState<CampaignView | null>(null)
  const [error, setError] = React.useState("")

  const refresh = React.useCallback(async () => {
    try {
      const next = await api.get<StudioState>("/api/state")
      setState(next)
      const current = slug && next.campaigns.includes(slug) ? slug : (next.campaigns[0] ?? "")
      if (current !== slug) setSlug(current)
      setCampaign(current ? await api.get<CampaignView>(`/api/campaigns/${current}`) : null)
      setError("")
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc))
    }
  }, [slug])

  React.useEffect(() => {
    void refresh()
  }, [refresh])

  const value = React.useMemo(() => ({ state, slug, setSlug, campaign, error, refresh }), [state, slug, campaign, error, refresh])
  return <StudioContext.Provider value={value}>{children}</StudioContext.Provider>
}

export function useStudio() {
  const context = React.useContext(StudioContext)
  if (!context) throw new Error("useStudio must be used within a StudioProvider")
  return context
}
