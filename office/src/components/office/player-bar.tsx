import { PauseIcon, PlayIcon, RotateCcwIcon } from "lucide-react"

import { useI18n } from "@/components/i18n-provider"
import { Button } from "@/components/ui/button"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { mmss } from "@/lib/format"
import type { Source } from "@/lib/api"

export const SPEEDS = [1, 2, 4, 8] as const

interface PlayerBarProps {
  source: Source
  span: { start: number; end: number } | null
  /** The position being shown; null follows the present. */
  cursor: number | null
  playing: boolean
  speed: number
  onPlaying: (playing: boolean) => void
  onSpeed: (speed: number) => void
  onSeek: (cursor: number) => void
  onRestart: () => void
  onLive: () => void
}

/** Live indicator, play/pause, speed and a position slider: the same bar replays real runs and samples. */
export function PlayerBar({ source, span, cursor, playing, speed, onPlaying, onSpeed, onSeek, onRestart, onLive }: PlayerBarProps) {
  const { t } = useI18n()
  const following = source === "live" && cursor === null
  const position = cursor ?? span?.end ?? 0

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2" role="group" aria-label={t("player.label")}>
      <span
        className="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold"
        data-state={following ? "working" : "waiting"}
      >
        <span aria-hidden="true" className={following ? "size-2 rounded-full bg-[var(--sc)]" : "size-2 rounded-full border border-muted-foreground"} />
        {source === "demo" ? t("player.sample") : following ? t("player.live") : t("player.replay")}
      </span>

      {span ? (
        <>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPlaying(!playing)}
              disabled={following}
              aria-label={playing ? t("player.pause") : t("player.play")}
            >
              {playing && !following ? <PauseIcon /> : <PlayIcon />}
              <span className="max-sm:sr-only">{playing && !following ? t("player.pause") : t("player.play")}</span>
            </Button>
            <Button variant="outline" size="sm" onClick={onRestart} aria-label={t("player.restart")}>
              <RotateCcwIcon />
              <span className="max-sm:sr-only">{t("player.restart")}</span>
            </Button>
          </div>
          <ToggleGroup
            type="single"
            variant="outline"
            size="sm"
            value={String(speed)}
            onValueChange={(value) => value && onSpeed(Number(value))}
            aria-label={t("player.speed")}
          >
            {SPEEDS.map((option) => (
              <ToggleGroupItem key={option} value={String(option)} className="font-mono text-xs">
                {option}×
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
          <label className="flex min-w-0 flex-1 items-center gap-3 basis-60">
            <span className="sr-only">{t("player.position")}</span>
            <input
              type="range"
              className="h-2 min-w-0 flex-1 accent-[var(--info)]"
              min={span.start}
              max={span.end}
              step={0.1}
              value={Math.min(Math.max(position, span.start), span.end)}
              onChange={(event) => onSeek(Number(event.target.value))}
            />
            <output className="min-w-[6.5rem] font-mono text-xs text-muted-foreground tabular-nums">
              {mmss(position - span.start)} / {mmss(span.end - span.start)}
            </output>
          </label>
          {source === "live" && !following ? (
            <Button size="sm" onClick={onLive}>
              {t("player.go_live")}
            </Button>
          ) : null}
        </>
      ) : null}
    </div>
  )
}
