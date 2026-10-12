import { useI18n } from "@/components/i18n-provider"
import { StatusBadge, type StatusTone } from "@/components/dashboard/status-badge"
import type { AgentState } from "@/lib/snapshot"

// Reviewing is a kind of working, so it takes the kit's warning dot: a review is where a
// person's attention is wanted. The label says the state in words, so no state is color alone.
const TONE: Record<AgentState, StatusTone> = {
  idle: "neutral",
  waiting: "neutral",
  working: "info",
  reviewing: "warning",
  done: "success",
  blocked: "failed",
}

export function StatusChip({ state }: { state: AgentState }) {
  const { t } = useI18n()
  return <StatusBadge tone={TONE[state]}>{t(`state.${state}`)}</StatusBadge>
}
