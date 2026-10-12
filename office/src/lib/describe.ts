import { tOr } from "@/lib/format"
import type { Translate } from "@/lib/i18n"
import type { AgentView } from "@/lib/snapshot"

/** What a card says about the agent right now, in the words of the viewer's language. */
export function describe(view: AgentView, t: Translate): string {
  switch (view.state) {
    case "working":
    case "reviewing":
      return view.task ?? t("agent.working")
    case "blocked":
      return view.stalled ? t("agent.stalled") : (view.note ?? view.task ?? t("agent.blocked"))
    case "done":
      return view.note ?? view.task ?? t("agent.done")
    case "waiting":
      if (view.note === "awaiting_audit") return t("team.awaiting_audit")
      if (view.note === "awaiting_spec") return t("team.awaiting_spec")
      return t("agent.waiting")
    default:
      return tOr(t, `roster.${view.id}.idle`, "agent.idle")
  }
}
