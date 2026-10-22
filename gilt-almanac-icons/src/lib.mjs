// Geometry helpers and the engraving builder used by icons.mjs.
// Every icon is drawn on a 200 × 200 grid. The token {G} stands for the ink
// (a gold gradient or currentColor) and {ID} for the file's id prefix.

const r2 = (n) => Math.round(n * 100) / 100;
const pt = (x, y) => `${r2(x)} ${r2(y)}`;
const rad = (deg) => (deg * Math.PI) / 180;

export const circle = (cx, cy, r) =>
  `M${pt(cx - r, cy)}A${r2(r)} ${r2(r)} 0 1 0 ${pt(cx + r, cy)}A${r2(r)} ${r2(r)} 0 1 0 ${pt(cx - r, cy)}Z`;

export const ellipse = (cx, cy, rx, ry) =>
  `M${pt(cx - rx, cy)}A${r2(rx)} ${r2(ry)} 0 1 0 ${pt(cx + rx, cy)}A${r2(rx)} ${r2(ry)} 0 1 0 ${pt(cx - rx, cy)}Z`;

export const poly = (pts, close = true) =>
  'M' + pts.map(([x, y]) => pt(x, y)).join('L') + (close ? 'Z' : '');

export const polar = (cx, cy, r, deg) => [cx + r * Math.cos(rad(deg)), cy + r * Math.sin(rad(deg))];

// Four-point sparkle with concave sides.
export const sparkle = (cx, cy, r, w = 0.18) => {
  const k = r * w;
  return `M${pt(cx, cy - r)}Q${pt(cx + k, cy - k)} ${pt(cx + r, cy)}Q${pt(cx + k, cy + k)} ${pt(cx, cy + r)}` +
    `Q${pt(cx - k, cy + k)} ${pt(cx - r, cy)}Q${pt(cx - k, cy - k)} ${pt(cx, cy - r)}Z`;
};

// Lit crescent of circle 1 left after removing circle 2 (arcs, not samples).
export function crescent([x1, y1, ra], [x2, y2, rb]) {
  const d = Math.hypot(x2 - x1, y2 - y1);
  const ux = (x2 - x1) / d, uy = (y2 - y1) / d;
  const a = (ra * ra - rb * rb + d * d) / (2 * d);
  const h = Math.sqrt(ra * ra - a * a);
  const P = [x1 + a * ux - h * uy, y1 + a * uy + h * ux];
  const Q = [x1 + a * ux + h * uy, y1 + a * uy - h * ux];
  // Outer arc P→Q on circle 1 stays outside circle 2; inner arc Q→P on circle 2 stays inside circle 1.
  const arc = (cx, cy, r, A, B, keep) => {
    const a0 = Math.atan2(A[1] - cy, A[0] - cx);
    let s = (Math.atan2(B[1] - cy, B[0] - cx) - a0 + 4 * Math.PI) % (2 * Math.PI);
    const m = [cx + r * Math.cos(a0 + s / 2), cy + r * Math.sin(a0 + s / 2)];
    const sweep = keep(m) ? 1 : 0;
    if (!sweep) s = 2 * Math.PI - s;
    return `A${r2(r)} ${r2(r)} 0 ${s > Math.PI ? 1 : 0} ${sweep} ${pt(...B)}`;
  };
  const outside2 = ([x, y]) => Math.hypot(x - x2, y - y2) > rb;
  const inside1 = ([x, y]) => Math.hypot(x - x1, y - y1) < ra;
  return `M${pt(...P)}${arc(x1, y1, ra, P, Q, outside2)}${arc(x2, y2, rb, Q, P, inside1)}Z`;
}

// Clip a segment to a box (Liang–Barsky). Returns null when it misses.
function clipSeg(x0, y0, x1, y1, [bx0, by0, bx1, by1]) {
  let t0 = 0, t1 = 1;
  const dx = x1 - x0, dy = y1 - y0;
  for (const [p, q] of [[-dx, x0 - bx0], [dx, bx1 - x0], [-dy, y0 - by0], [dy, by1 - y0]]) {
    if (p === 0) { if (q < 0) return null; continue; }
    const t = q / p;
    if (p < 0) { if (t > t1) return null; if (t > t0) t0 = t; }
    else { if (t < t0) return null; if (t < t1) t1 = t; }
  }
  return [x0 + t0 * dx, y0 + t0 * dy, x0 + t1 * dx, y0 + t1 * dy];
}

// Parallel engraving lines at `angle` degrees, `gap` apart, cut to `box`.
export function lines({ angle = 45, gap = 3, box = [0, 0, 200, 200], phase = 0 }) {
  const [bx0, by0, bx1, by1] = box;
  const cx = (bx0 + bx1) / 2, cy = (by0 + by1) / 2;
  const R = Math.hypot(bx1 - bx0, by1 - by0) / 2 + gap;
  const dx = Math.cos(rad(angle)), dy = Math.sin(rad(angle));
  let out = '';
  for (let t = -R + phase; t <= R; t += gap) {
    const px = cx - dy * t, py = cy + dx * t;
    const s = clipSeg(px - dx * R, py - dy * R, px + dx * R, py + dy * R, box);
    if (s) out += `M${pt(s[0], s[1])}L${pt(s[2], s[3])}`;
  }
  return out;
}

// Concentric engraving rings (contour hatching for spheres and haloes).
export function rings({ cx = 100, cy = 100, from = 2, to = 100, gap = 3 }) {
  let out = '';
  for (let r = from; r <= to; r += gap) out += circle(cx, cy, r);
  return out;
}

// Spokes radiating from a centre, e.g. scale divisions.
export function spokes({ cx = 100, cy = 100, r0, r1, count, offset = 0 }) {
  let out = '';
  for (let i = 0; i < count; i++) {
    const a = offset + (360 * i) / count;
    out += `M${pt(...polar(cx, cy, r0, a))}L${pt(...polar(cx, cy, r1, a))}`;
  }
  return out;
}

// Collects one icon's defs and body.
export class Plate {
  constructor() { this.defs = []; this.body = []; this.n = 0; }

  #mask(spec) {
    // spec: { keep: [d], cut: [d], cutStroke: [[d, width]] }
    const id = `{ID}m${this.n++}`;
    const base = spec.keep ? '#000' : '#fff';
    const parts = [
      ...(spec.keep || []).map((d) => `<path d="${d}" fill="#fff"/>`),
      ...(spec.cut || []).map((d) => `<path d="${d}" fill="#000"/>`),
      ...(spec.cutStroke || []).map(([d, w]) => `<path d="${d}" fill="none" stroke="#000" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`),
    ];
    this.defs.push(`<mask id="${id}" maskUnits="userSpaceOnUse" x="-20" y="-20" width="240" height="240">` +
      `<rect x="-20" y="-20" width="240" height="240" fill="${base}"/>${parts.join('')}</mask>`);
    return ` mask="url(#${id})"`;
  }

  // Engraved shading: `strokes` (from lines/rings/spokes) clipped to the area `d`.
  hatch(d, strokes, { w = 1.1, rule = 'nonzero', mask } = {}) {
    let attrs = '';
    if (d) {
      const id = `{ID}c${this.n++}`;
      this.defs.push(`<clipPath id="${id}"><path d="${d}" clip-rule="${rule}"/></clipPath>`);
      attrs += ` clip-path="url(#${id})"`;
    }
    if (mask) attrs += this.#mask(mask);
    this.body.push(`<path d="${strokes}" stroke-width="${w}"${attrs}/>`);
    return this;
  }

  line(d, w = 3, { mask, extra = '' } = {}) {
    this.body.push(`<path d="${d}" stroke-width="${w}"${mask ? this.#mask(mask) : ''}${extra}/>`);
    return this;
  }

  fill(d, { rule } = {}) {
    this.body.push(`<path d="${d}" fill="{G}" stroke="none"${rule ? ` fill-rule="${rule}"` : ''}/>`);
    return this;
  }

  open(attrs) { this.body.push(`<g ${attrs}>`); return this; }
  close() { this.body.push('</g>'); return this; }
}
