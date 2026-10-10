import * as React from "react"

import { useStudio } from "@/lib/studio"

/** "api" calls Claude directly; "paste" shows the prompt for claude.ai and checks the pasted answer. */
export function useAiMode() {
  const { state } = useStudio()
  const [mode, setMode] = React.useState<"api" | "paste" | null>(null)
  const effective = mode ?? (state?.ai.has_key ? "api" : "paste")
  return [effective, setMode] as const
}
