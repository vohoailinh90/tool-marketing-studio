import * as React from "react"

/** Where each card (and the boss) is in the DOM, by agent id, so a handoff line can find both ends. */
export interface Nodes {
  register: (id: string, element: HTMLElement | null) => void
  get: (id: string) => HTMLElement | undefined
}

const NodesContext = React.createContext<Nodes | null>(null)

export function NodesProvider({ children }: { children: React.ReactNode }) {
  const map = React.useRef(new Map<string, HTMLElement>())
  const value = React.useMemo<Nodes>(
    () => ({
      register: (id, element) => {
        if (element) map.current.set(id, element)
        else map.current.delete(id)
      },
      get: (id) => map.current.get(id),
    }),
    [],
  )
  return <NodesContext.Provider value={value}>{children}</NodesContext.Provider>
}

export function useNodes(): Nodes {
  const context = React.useContext(NodesContext)
  if (!context) throw new Error("useNodes must be used within a NodesProvider")
  return context
}
