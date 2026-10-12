// The snapshot contract, mirrored from scripts/office/snapshot.py (`validate()` is its source of truth).
// The server is the only producer, so these types describe what the page may rely on and nothing more.

export type Mode = "claude" | "team"
export type AgentState = "idle" | "waiting" | "working" | "reviewing" | "done" | "blocked"
export type EdgeState = "planned" | "active" | "done"
export type LogKind = "start" | "done" | "fail" | "warn"
export type Tag = "received" | "handoff" | "error"
export type AvatarKind = "robot" | "script"

export interface AgentView {
  id: string
  state: AgentState
  task: string | null
  note: string | null
  /** 0..1; an estimate while running (tool calls over maxTurns), exactly 1 only when finished. */
  progress: number | null
  tag: Tag | null
  since: number | null
  runs: number
  turns: { used: number; max: number | null } | null
  model: string | null
  effort: string | null
  tokens: number | null
  duration_ms: number | null
  stalled: boolean
  kind: AvatarKind
}

export interface Lane {
  id: string
  color: string
  agents: string[]
}

export interface Edge {
  from: string
  to: string
  state: EdgeState
}

export interface LogEntry {
  t: number
  kind: LogKind
  agent: string
  text: string | null
}

export interface BudgetSlot {
  id: string
  cap: number
  granted: number
  used: number
}

export interface Snapshot {
  version: 1
  mode: Mode
  now: number
  live: boolean
  span: { start: number; end: number } | null
  empty: boolean
  hints: string[]
  demo?: string
  feature: string | null
  features: string[]
  requirement: {
    id: string | null
    tier: string | null
    lane: string
    strategy: string | null
    required: string[]
  } | null
  boss: { id: "main"; kind: AvatarKind; state: AgentState; task: string | null; waiting_for: string | null }
  phase: { steps: string[]; current: string | null }
  progress: { pct: number | null; agents: number; total: number; running: number; done: number; blocked: number }
  budget: BudgetSlot[] | null
  lanes: Lane[]
  agents: Record<string, AgentView>
  edges: Edge[]
  log: LogEntry[]
  warnings: string[]
}

export const BUSY: readonly AgentState[] = ["working", "reviewing"]
