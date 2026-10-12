// Where a handoff line runs between two cards. Pure, so it is tested without a browser.

export interface Rect {
  x: number
  y: number
  w: number
  h: number
}

export interface EdgeGeometry {
  d: string
  end: [number, number]
}

/** Below the source: leave its bottom, enter the target's top. Above: the reverse. Same row: side to side. */
export function edgeGeometry(a: Rect, b: Rect): EdgeGeometry {
  const ax = a.x + a.w / 2
  const ay = a.y + a.h / 2
  const bx = b.x + b.w / 2
  const by = b.y + b.h / 2
  const slack = 6
  let p0: [number, number]
  let p1: [number, number]
  let vertical = true
  if (b.y >= a.y + a.h - slack) {
    p0 = [ax, a.y + a.h]
    p1 = [bx, b.y]
  } else if (a.y >= b.y + b.h - slack) {
    p0 = [ax, a.y]
    p1 = [bx, b.y + b.h]
  } else {
    vertical = false
    if (bx > ax) {
      p0 = [a.x + a.w, ay]
      p1 = [b.x, by]
    } else {
      p0 = [a.x, ay]
      p1 = [b.x + b.w, by]
    }
  }
  const mx = (p0[0] + p1[0]) / 2
  const my = (p0[1] + p1[1]) / 2
  const d = vertical
    ? `M${p0[0]},${p0[1]} C${p0[0]},${my} ${p1[0]},${my} ${p1[0]},${p1[1]}`
    : `M${p0[0]},${p0[1]} C${mx},${p0[1]} ${mx},${p1[1]} ${p1[0]},${p1[1]}`
  return { d, end: p1 }
}

/** `el` relative to `base`, both in viewport coordinates, so scrolling does not matter. */
export function relativeRect(el: DOMRect, base: DOMRect): Rect {
  return { x: el.left - base.left, y: el.top - base.top, w: el.width, h: el.height }
}
