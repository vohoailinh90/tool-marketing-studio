import {
  BarChart3,
  FileText,
  History,
  Images,
  LayoutDashboard,
  Lightbulb,
  PenLine,
  Send,
  type LucideIcon,
} from "lucide-react"

import type { MessageKey } from "@/lib/i18n"

export type NavItem = { to: string; label: MessageKey; icon: LucideIcon; end: boolean }

export type NavGroup = { label: MessageKey | null; items: NavItem[] }

/** Grouped like the kit's sidebar: the content workflow in order, then what happened after. */
export const navGroups: NavGroup[] = [
  {
    label: null,
    items: [{ to: "/", label: "nav_overview", icon: LayoutDashboard, end: true }],
  },
  {
    label: "nav_group_create",
    items: [
      { to: "/analyse", label: "nav_analyse", icon: Lightbulb, end: false },
      { to: "/write", label: "nav_write", icon: PenLine, end: false },
      { to: "/preview", label: "nav_preview", icon: Images, end: false },
      { to: "/publish", label: "nav_publish", icon: Send, end: false },
    ],
  },
  {
    label: "nav_group_learn",
    items: [
      { to: "/history", label: "nav_history", icon: History, end: false },
      { to: "/insights", label: "nav_insights", icon: BarChart3, end: false },
      { to: "/guide", label: "nav_guide", icon: FileText, end: false },
    ],
  },
]

export const navItems: NavItem[] = navGroups.flatMap((group) => group.items)
