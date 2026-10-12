import * as React from "react"

import { cn } from "@/lib/utils"

/**
 * A thin progress bar in the kit's conventions (a plain element styled through tokens and `cn()`).
 * The fill takes its color from `--sc`, the state color the page sets on an ancestor, so the
 * same bar reads as working, done or blocked without a variant per state.
 * `value` is 0..100; null is "no figure", drawn empty and announced without a value.
 */
function Progress({
  value,
  className,
  ...props
}: Omit<React.ComponentProps<"div">, "children"> & { value: number | null }) {
  return (
    <div
      data-slot="progress"
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={value === null ? undefined : Math.round(value)}
      className={cn("h-1.5 w-full min-w-0 overflow-hidden rounded-full bg-muted", className)}
      {...props}
    >
      <div
        className="h-full rounded-full bg-[var(--sc,var(--muted-foreground))] transition-[width] duration-300 ease-linear"
        style={{ width: `${value ?? 0}%` }}
      />
    </div>
  )
}

export { Progress }
