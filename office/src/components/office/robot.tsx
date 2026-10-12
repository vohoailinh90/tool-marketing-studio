import type { AgentState, AvatarKind } from "@/lib/snapshot"

/**
 * A desk with a robot (or a terminal, for a script) drawn in SVG. Colors come from CSS tokens and
 * the department's `--dept`, motion from CSS keyed on `data-state` (see index.css), so a state
 * change costs one attribute and the page's reduced-motion rule turns all of it off at once.
 */
export function Robot({ kind, state }: { kind: AvatarKind; state: AgentState }) {
  return kind === "script" ? <Terminal state={state} /> : <Bot state={state} />
}

function Bot({ state }: { state: AgentState }) {
  return (
    <svg className="bot" data-state={state} viewBox="0 0 120 84" aria-hidden="true" focusable="false">
      <rect className="desk" x="4" y="68" width="112" height="6" rx="3" />
      <g>
        <rect className="m-body" x="68" y="24" width="42" height="32" rx="5" />
        <rect className="m-line l1" x="74" y="31" width="26" height="3" rx="1.5" />
        <rect className="m-line l2" x="74" y="38" width="20" height="3" rx="1.5" />
        <rect className="m-line l3" x="74" y="45" width="30" height="3" rx="1.5" />
        <rect className="m-stand" x="85" y="56" width="8" height="8" />
        <rect className="m-base" x="78" y="63" width="22" height="4" rx="2" />
      </g>
      <g className="kb">
        <rect x="52" y="64" width="22" height="4" rx="2" />
      </g>
      <g className="rb">
        <line className="ant" x1="34" y1="9" x2="34" y2="16" />
        <circle className="ball" cx="34" cy="7" r="3.6" />
        <rect className="body" x="22" y="44" width="24" height="20" rx="7" />
        <path className="arm" d="M44 50 L58 62" />
        <rect className="head" x="17" y="16" width="34" height="27" rx="10" />
        <rect className="plate" x="21.5" y="20.5" width="25" height="16.5" rx="6.5" />
        <g className="eyes e-open">
          <circle cx="29.5" cy="28.7" r="2.5" />
          <circle cx="38.5" cy="28.7" r="2.5" />
        </g>
        <g className="eyes e-sleep">
          <path d="M27 29h5M36 29h5" />
        </g>
        <g className="eyes e-happy">
          <path d="M27 30q2.5-4 5 0M36 30q2.5-4 5 0" />
        </g>
        <g className="eyes e-x">
          <path d="M27.5 26.5l4 4m0-4l-4 4M36.5 26.5l4 4m0-4l-4 4" />
        </g>
      </g>
      <g className="badge b-done">
        <circle cx="55" cy="13" r="7" />
        <path d="M51.5 13l2.5 2.5 4-5" />
      </g>
      <g className="badge b-crit">
        <circle cx="55" cy="13" r="7" />
        <path d="M55 9.5v4.5M55 16.8v.1" />
      </g>
      <text className="zzz" x="53" y="14">
        z
      </text>
    </svg>
  )
}

function Terminal({ state }: { state: AgentState }) {
  return (
    <svg className="bot" data-state={state} viewBox="0 0 120 84" aria-hidden="true" focusable="false">
      <rect className="desk" x="4" y="68" width="112" height="6" rx="3" />
      <rect className="m-body" x="20" y="10" width="80" height="54" rx="8" />
      <circle className="term-dot" cx="30" cy="19" r="2.2" />
      <circle className="term-dot" cx="38" cy="19" r="2.2" />
      <circle className="term-dot" cx="46" cy="19" r="2.2" />
      <path className="chev" d="M30 31l6 5-6 5" />
      <rect className="m-line l1" x="42" y="34" width="34" height="3" rx="1.5" />
      <rect className="m-line l2" x="30" y="46" width="48" height="3" rx="1.5" />
      <rect className="m-line l3" x="30" y="53" width="26" height="3" rx="1.5" />
      <rect className="cursor" x="60" y="52" width="6" height="5" />
      <g className="badge b-done">
        <circle cx="98" cy="12" r="7" />
        <path d="M94.5 12l2.5 2.5 4-5" />
      </g>
      <g className="badge b-crit">
        <circle cx="98" cy="12" r="7" />
        <path d="M98 8.5v4.5M98 15.8v.1" />
      </g>
      <text className="zzz" x="92" y="22">
        z
      </text>
    </svg>
  )
}
