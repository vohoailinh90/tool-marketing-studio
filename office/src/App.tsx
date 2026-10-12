import * as React from "react"

import { useI18n } from "@/components/i18n-provider"
import { LanguageToggle } from "@/components/language-toggle"
import { AgentSheet } from "@/components/office/agent-sheet"
import { BossCard } from "@/components/office/boss-card"
import { EventLog } from "@/components/office/event-log"
import { HandoffEdges } from "@/components/office/handoff-edges"
import { LaneSection } from "@/components/office/lane"
import { NodesProvider } from "@/components/office/nodes"
import { Notices } from "@/components/office/notices"
import { PlayerBar } from "@/components/office/player-bar"
import { ThemeToggle } from "@/components/theme-toggle"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { usePlayback } from "@/hooks/use-playback"
import { useSnapshot } from "@/hooks/use-snapshot"
import type { Source } from "@/lib/api"
import { answersFeature, keepFeature } from "@/lib/feature"
import type { Mode } from "@/lib/snapshot"

/** Where in a sample the page starts, so the first frame already has agents at work. */
const SAMPLE_START = 0.4
const SAMPLE_HOLD_MS = 2500
const MODES: Mode[] = ["claude", "team"]

export default function App() {
  const { t } = useI18n()
  const [mode, setMode] = React.useState<Mode>("claude")
  const [source, setSource] = React.useState<Source>("live")
  const [cursor, setCursor] = React.useState<number | null>(null)
  const [playing, setPlaying] = React.useState(() => !window.matchMedia("(prefers-reduced-motion: reduce)").matches)
  const [speed, setSpeed] = React.useState(2)
  const [selected, setSelected] = React.useState<string | null>(null)
  const [feature, setFeature] = React.useState<string | null>(null)
  const floor = React.useRef<HTMLDivElement>(null)
  const opener = React.useRef<HTMLElement | null>(null)

  const params = React.useMemo(() => ({ mode, source, at: cursor, feature }), [mode, source, cursor, feature])
  const { snapshot: received, error } = useSnapshot(params)
  // An answer for the previous mode or source may still be on screen for a moment: do not draw it as the new one.
  const current = received && received.mode === mode && (received.demo !== undefined) === (source === "demo") ? received : null
  const snapshot = current && answersFeature(current, feature) ? current : null
  const span = snapshot?.span ?? null

  // A feature that is gone from the answer's own list (removed while picked) cannot be asked for again: drop the pick.
  const kept = keepFeature(current, feature)
  if (kept !== feature) setFeature(kept)

  React.useEffect(() => {
    document.title = t("app.title")
  }, [t])

  // First answer: with nothing to show from this checkout, open on the sample instead of an empty floor.
  const decided = React.useRef(false)
  React.useEffect(() => {
    if (decided.current || !snapshot) return
    decided.current = true
    if (source === "live" && snapshot.empty) setSource("demo")
  }, [snapshot, source])

  // A sample always has a position: start part-way in, with work already under way.
  React.useEffect(() => {
    if (source === "demo" && cursor === null && span) setCursor(span.start + (span.end - span.start) * SAMPLE_START)
  }, [source, cursor, span])

  // The sample's pause before it plays again. Anything that moves the cursor by hand ends it, or it would fire later
  // and drag a view the person has already left (the live one, another mode) back to the start of the sample.
  const loopTimer = React.useRef<number | undefined>(undefined)
  const cancelHold = () => window.clearTimeout(loopTimer.current)
  React.useEffect(() => cancelHold, [])
  const moveCursor = (next: number | null) => {
    cancelHold()
    setCursor(next)
  }

  usePlayback({
    running: playing && cursor !== null,
    speed,
    cursor,
    span,
    onCursor: setCursor,
    onEnd: () => {
      if (source === "live") setCursor(null)
      else if (span) {
        cancelHold()
        loopTimer.current = window.setTimeout(() => setCursor(span.start), SAMPLE_HOLD_MS)
      }
    },
  })

  const changeMode = (next: Mode) => {
    setMode(next)
    moveCursor(null)
    setFeature(null)
    setSelected(null)
  }
  const changeSource = (next: Source) => {
    setSource(next)
    moveCursor(null)
    setFeature(null) // a sample ignores the feature filter, so a stale one would reject every answer
    setSelected(null)
  }

  const selectedView = snapshot && selected ? (snapshot.agents[selected] ?? null) : null
  const layoutKey = snapshot ? snapshot.lanes.map((lane) => `${lane.id}:${lane.agents.join(",")}`).join(";") : ""

  return (
    <div className="mx-auto flex max-w-[1240px] flex-col gap-5 px-[max(1rem,3vw)] py-5 pb-9">
      <Tabs value={mode} onValueChange={(value) => changeMode(value as Mode)} className="gap-5">
        <header className="flex flex-wrap items-center gap-x-5 gap-y-3">
          <h1 className="mr-auto text-xl font-extrabold tracking-tight">{t("app.title")}</h1>
          <TabsList aria-label={t("mode.label")}>
            {MODES.map((option) => (
              <TabsTrigger key={option} value={option} className="px-3.5">
                {t(`mode.${option}`)}
              </TabsTrigger>
            ))}
          </TabsList>
          <ToggleGroup
            type="single"
            variant="outline"
            size="sm"
            value={source}
            onValueChange={(value) => value && changeSource(value as Source)}
            aria-label={t("source.label")}
          >
            <ToggleGroupItem value="live">{t("source.live")}</ToggleGroupItem>
            <ToggleGroupItem value="demo">{t("source.demo")}</ToggleGroupItem>
          </ToggleGroup>
          {mode === "team" && snapshot && snapshot.features.length > 1 ? (
            <label className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">{t("team.feature")}</span>
              <select
                className="h-8 rounded-md border bg-background px-2 text-sm"
                value={snapshot.feature ?? ""}
                onChange={(event) => setFeature(event.target.value)}
              >
                {snapshot.features.map((id) => (
                  <option key={id} value={id}>
                    {id}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          <div className="flex items-center">
            <LanguageToggle />
            <ThemeToggle />
          </div>
        </header>

        <PlayerBar
          source={source}
          span={span}
          cursor={cursor}
          playing={playing}
          speed={speed}
          onPlaying={(next) => {
            if (!next) cancelHold()
            setPlaying(next)
          }}
          onSpeed={setSpeed}
          onSeek={(next) => {
            moveCursor(next)
            if (source === "live") setPlaying(false)
          }}
          onRestart={() => {
            moveCursor(span ? span.start : cursor)
            setPlaying(true)
          }}
          onLive={() => moveCursor(null)}
        />

        <Notices snapshot={snapshot} mode={mode} error={error} source={source} onSample={() => changeSource("demo")} />

        <TabsContent value={mode} className="flex flex-col gap-5">
          {snapshot ? (
            <>
              <NodesProvider>
                <div ref={floor} className="relative flex flex-col gap-7">
                  <BossCard snapshot={snapshot} />
                  <div className="flex flex-wrap gap-4" role="group" aria-label={t("lanes.label")}>
                    {snapshot.lanes.map((lane) => (
                      <LaneSection
                        key={lane.id}
                        lane={lane}
                        agents={snapshot.agents}
                        onSelect={(id, element) => {
                          opener.current = element
                          setSelected(id)
                        }}
                      />
                    ))}
                  </div>
                  <HandoffEdges edges={snapshot.edges} layoutKey={layoutKey} container={floor} />
                </div>
              </NodesProvider>
              <EventLog entries={snapshot.log} mode={mode} />
            </>
          ) : (
            <p role="status" className="py-10 text-center text-sm text-muted-foreground">
              {t("status.loading")}
            </p>
          )}
        </TabsContent>
      </Tabs>

      <p className="max-w-[90ch] text-[12.5px] leading-relaxed text-muted-foreground">
        {source === "demo" ? `${t("footer.sample")} ` : ""}
        {t("footer.estimate")}
      </p>
      <AgentSheet view={selectedView} onClose={() => setSelected(null)} restoreFocus={() => opener.current?.focus()} />
    </div>
  )
}
