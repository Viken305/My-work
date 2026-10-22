// Geometry for the Calibre set: luxury watchmaking icons in polished chrome.
// Each icon is a list of layers drawn in order: [type, d, width?]
//   tube:  polished steel rod (dark rim, chrome body, specular line)
//   blue:  blued-steel rod (hands, hairsprings, pallet forks)
//   fine:  thin chrome detail line, no rim
//   steel: chrome-filled solid with a dark rim
//   ruby / sand / sky: coloured solids (jewels, sand and gold, enamel sky)
//   glass: a faint sapphire tint (chrome version only)
// Drawn on a 200 × 200 grid.

export const groups = ['Timepieces', 'Movement', 'Complications', 'Atelier'];

const r = (n) => Math.round(n * 100) / 100;
const P = (x, y) => `${r(x)} ${r(y)}`;
const polar = (cx, cy, rad, deg) => [cx + rad * Math.cos((deg * Math.PI) / 180), cy + rad * Math.sin((deg * Math.PI) / 180)];
const circle = (cx, cy, rad) => `M${P(cx - rad, cy)}A${rad} ${rad} 0 1 0 ${P(cx + rad, cy)}A${rad} ${rad} 0 1 0 ${P(cx - rad, cy)}Z`;
const ellipse = (cx, cy, rx, ry) => `M${P(cx - rx, cy)}A${rx} ${ry} 0 1 0 ${P(cx + rx, cy)}A${rx} ${ry} 0 1 0 ${P(cx - rx, cy)}Z`;
const poly = (pts, close = true) => 'M' + pts.map(([x, y]) => P(x, y)).join('L') + (close ? 'Z' : '');
const seg = (a, b) => `M${P(...a)}L${P(...b)}`;
const arc = (cx, cy, rad, a0, a1) => {
  const [x0, y0] = polar(cx, cy, rad, a0), [x1, y1] = polar(cx, cy, rad, a1);
  return `M${P(x0, y0)}A${rad} ${rad} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${P(x1, y1)}`;
};
// Tick marks around a dial.
const ticks = (cx, cy, r0, r1, n, skip = () => false, offset = -90) => {
  let d = '';
  for (let i = 0; i < n; i++) if (!skip(i)) d += seg(polar(cx, cy, r0, offset + (i * 360) / n), polar(cx, cy, r1, offset + (i * 360) / n));
  return d;
};
// Hands from a centre at clock angles (0° = 12 o'clock).
const hand = (cx, cy, len, clockDeg, tail = 0) => seg(polar(cx, cy, -tail, clockDeg - 90), polar(cx, cy, len, clockDeg - 90));
const gear = (cx, cy, root, tip, n) => {
  const pts = [], step = 360 / n;
  for (let i = 0; i < n; i++) {
    const a = i * step;
    pts.push(polar(cx, cy, root, a), polar(cx, cy, tip, a + step * 0.12), polar(cx, cy, tip, a + step * 0.42), polar(cx, cy, root, a + step * 0.54));
  }
  return poly(pts);
};
const escapeTeeth = (cx, cy, root, tip, n) => {
  const pts = [], step = 360 / n;
  for (let i = 0; i < n; i++) {
    const a = i * step;
    pts.push(polar(cx, cy, root, a), polar(cx, cy, tip, a + step * 0.7), polar(cx, cy, tip - 4, a + step * 0.86), polar(cx, cy, root, a + step * 0.9));
  }
  return poly(pts);
};
const spiral = (cx, cy, r0, r1, turns, start = 0) => {
  const pts = [], steps = Math.round(turns * 48);
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    pts.push(polar(cx, cy, r0 + (r1 - r0) * t, start + t * turns * 360));
  }
  return poly(pts, false);
};
const flutes = (cx, cy, rad, n, depth) => {
  let d = '';
  for (let i = 0; i < n; i++) {
    const a0 = (i * 360) / n, a1 = ((i + 1) * 360) / n;
    const [x1, y1] = polar(cx, cy, rad, a1), [qx, qy] = polar(cx, cy, rad + depth, (a0 + a1) / 2);
    d += (i ? '' : `M${P(...polar(cx, cy, rad, a0))}`) + `Q${P(qx, qy)} ${P(x1, y1)}`;
  }
  return d + 'Z';
};
const rect = (x, y, w, h) => `M${x} ${y}H${x + w}V${y + h}H${x}Z`;
const rrect = (x, y, w, h, k) => `M${x + k} ${y}H${x + w - k}Q${x + w} ${y} ${x + w} ${y + k}V${y + h - k}Q${x + w} ${y + h} ${x + w - k} ${y + h}H${x + k}Q${x} ${y + h} ${x} ${y + h - k}V${y + k}Q${x} ${y} ${x + k} ${y}Z`;
const sparkle = (cx, cy, s) => `M${cx} ${cy - s}Q${cx} ${cy} ${cx + s} ${cy}Q${cx} ${cy} ${cx} ${cy + s}Q${cx} ${cy} ${cx - s} ${cy}Q${cx} ${cy} ${cx} ${cy - s}Z`;
// A small part rotated about its own centre, as a path.
const rotRect = (cx, cy, w, h, deg) => {
  const pts = [[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]].map(([x, y]) => {
    const a = (deg * Math.PI) / 180;
    return [cx + x * Math.cos(a) - y * Math.sin(a), cy + x * Math.sin(a) + y * Math.cos(a)];
  });
  return poly(pts);
};

export const icons = [
  // ── Timepieces ──
  { slug: 'wristwatch', name: 'Wristwatch', group: 'Timepieces', layers: [
    ['steel', 'M74 18H126L120 58H80Z'], ['steel', 'M80 142H120L126 182H74Z'],
    ['fine', 'M78 30H122M77 40H123M80 160H120M78 170H122', 1.4],
    ['steel', rrect(146, 92, 12, 16, 3)],
    ['tube', circle(100, 100, 46), 7],
    ['fine', ticks(100, 100, 32, 39, 12), 2.4], ['fine', ticks(100, 100, 37, 39, 60, (i) => i % 5 === 0), 1],
    ['blue', hand(100, 100, 24, 300, 6), 4.5], ['blue', hand(100, 100, 33, 60, 8), 3.5],
    ['steel', circle(100, 100, 4.5)] ] },
  { slug: 'pocket-watch', name: 'Pocket watch', group: 'Timepieces', layers: [
    ['tube', circle(100, 30, 12), 5], ['steel', rrect(92, 44, 16, 14, 3)],
    ['tube', circle(100, 114, 56), 6],
    ['fine', circle(100, 114, 46), 1.4],
    ['fine', ticks(100, 114, 38, 45, 12), 2.4],
    ['fine', circle(100, 140, 11), 1.4], ['fine', hand(100, 140, 8, 120), 1.6],
    ['blue', hand(100, 114, 26, 320, 6), 4.5], ['blue', hand(100, 114, 36, 40, 8), 3.5],
    ['steel', circle(100, 114, 4.5)] ] },
  { slug: 'diver', name: 'Dive watch', group: 'Timepieces', layers: [
    ['steel', rrect(150, 92, 12, 16, 3)], ['steel', 'M146 84L156 88V112L146 116Z'],
    ['tube', circle(100, 100, 56), 9],
    ['fine', ticks(100, 100, 52, 60, 12, (i) => i === 0), 2],
    ['sand', poly([[100, 50], [92, 38], [108, 38]])],
    ['tube', circle(100, 100, 42), 3],
    ['sand', ticks(100, 100, 30, 38, 12, (i) => i % 3 !== 0)],
    ['fine', ticks(100, 100, 30, 38, 4), 5],
    ['blue', hand(100, 100, 22, 300, 6), 6], ['blue', hand(100, 100, 32, 70, 8), 4.5],
    ['steel', circle(100, 100, 5)] ] },
  { slug: 'carriage-clock', name: 'Carriage clock', group: 'Timepieces', layers: [
    ['tube', 'M76 58C76 30 124 30 124 58', 5],
    ['tube', 'M50 60H150V168H50Z', 6],
    ['tube', 'M50 78H150', 3], ['tube', 'M50 150H150', 3],
    ['steel', rect(46, 168, 16, 10)], ['steel', rect(138, 168, 16, 10)],
    ['tube', circle(100, 114, 28), 4],
    ['fine', ticks(100, 114, 20, 25, 12), 1.8],
    ['blue', hand(100, 114, 14, 300, 4), 3.5], ['blue', hand(100, 114, 21, 60, 5), 3],
    ['steel', circle(100, 114, 3.5)] ] },
  { slug: 'hourglass', name: 'Hourglass', group: 'Timepieces', layers: [
    ['glass', 'M66 40C66 78 92 88 92 100C92 112 66 122 66 160H134C134 122 108 112 108 100C108 88 134 78 134 40Z'],
    ['sand', 'M78 64H122C118 80 104 88 100 96C96 88 82 80 78 64Z'], ['sand', 'M72 158C76 138 92 132 100 128C108 132 124 138 128 158Z'],
    ['fine', 'M100 98V128', 1.6],
    ['tube', 'M66 40C66 78 92 88 92 100C92 112 66 122 66 160M134 40C134 78 108 88 108 100C108 112 134 122 134 160', 3],
    ['tube', 'M54 38V162M146 38V162', 6],
    ['steel', rrect(40, 22, 120, 16, 4)], ['steel', rrect(40, 162, 120, 16, 4)] ] },
  { slug: 'regulator', name: 'Regulator clock', group: 'Timepieces', layers: [
    ['tube', 'M60 30H140V176H60Z', 5],
    ['tube', 'M60 30L100 12L140 30', 4],
    ['tube', circle(100, 64, 26), 4], ['fine', ticks(100, 64, 18, 23, 12), 1.6],
    ['blue', hand(100, 64, 13, 330, 3), 3], ['blue', hand(100, 64, 19, 80, 4), 2.6],
    ['fine', rect(72, 96, 56, 72), 1.4],
    ['tube', 'M100 92V150', 3], ['steel', circle(100, 152, 12)],
    ['fine', circle(100, 152, 6), 1.4] ] },

  // ── Movement ──
  { slug: 'gear', name: 'Gear', group: 'Movement', layers: [
    ['tube', gear(100, 100, 58, 72, 18), 4],
    ['tube', circle(100, 100, 44), 4],
    ['tube', [0, 72, 144, 216, 288].map((a) => seg(polar(100, 100, 12, a - 90), polar(100, 100, 44, a - 90))).join(''), 5],
    ['steel', circle(100, 100, 13)], ['ruby', circle(100, 100, 5)] ] },
  { slug: 'escape-wheel', name: 'Escape wheel', group: 'Movement', layers: [
    ['tube', escapeTeeth(100, 120, 44, 62, 15), 3.5],
    ['tube', circle(100, 120, 34), 4],
    ['tube', [45, 135, 225, 315].map((a) => seg(polar(100, 120, 8, a), polar(100, 120, 34, a))).join(''), 4],
    ['steel', circle(100, 120, 9)],
    ['blue', 'M100 50L56 34M100 50L144 34M100 50V18', 5],
    ['ruby', rotRect(56, 36, 8, 14, -20)], ['ruby', rotRect(144, 36, 8, 14, 20)],
    ['steel', circle(100, 50, 6)] ] },
  { slug: 'balance-wheel', name: 'Balance wheel', group: 'Movement', layers: [
    ['blue', spiral(100, 100, 5, 30, 4.5), 1.8],
    ['tube', circle(100, 100, 54), 6],
    ['tube', seg([46, 100], [154, 100]), 4],
    ...Array.from({ length: 12 }, (_, i) => ['steel', circle(...polar(100, 100, 54, i * 30 + 15), 4.5)]),
    ['steel', circle(100, 100, 7)], ['ruby', circle(100, 100, 3)] ] },
  { slug: 'mainspring', name: 'Mainspring', group: 'Movement', layers: [
    ['tube', gear(100, 100, 66, 74, 40), 2.5],
    ['tube', circle(100, 100, 62), 4],
    ['blue', spiral(100, 100, 14, 54, 4.2, 30), 4],
    ['steel', circle(100, 100, 12)], ['fine', 'M92 100H108', 2.4] ] },
  { slug: 'ruby-jewel', name: 'Ruby jewel', group: 'Movement', layers: [
    ['tube', circle(100, 100, 64), 7], ['tube', circle(100, 100, 52), 3],
    ['ruby', poly([...Array.from({ length: 8 }, (_, i) => polar(100, 100, 44, i * 45 + 22.5))]), 'outline'],
    ['fine', poly([...Array.from({ length: 8 }, (_, i) => polar(100, 100, 24, i * 45 + 22.5))]) +
      Array.from({ length: 8 }, (_, i) => seg(polar(100, 100, 24, i * 45 + 22.5), polar(100, 100, 44, i * 45 + 22.5))).join(''), 1.3],
    ['steel', circle(100, 100, 6)],
    ...[0, 90, 180, 270].map((a) => ['steel', circle(...polar(100, 100, 58, a + 45), 5)]) ] },
  { slug: 'crown', name: 'Winding crown', group: 'Movement', layers: [
    ['tube', flutes(100, 100, 60, 24, 7), 4],
    ['steel', circle(100, 100, 44)],
    ['fine', circle(100, 100, 36), 1.4],
    ['fine', Array.from({ length: 36 }, (_, i) => seg(polar(100, 100, 16, i * 10), polar(100, 100, 34, i * 10))).join(''), 1],
    ['sand', circle(100, 100, 12)], ['fine', circle(100, 100, 6), 1.2] ] },

  // ── Complications ──
  { slug: 'chronograph', name: 'Chronograph', group: 'Complications', layers: [
    ['steel', rotRect(...polar(100, 100, 58, -45), 10, 14, 45)], ['steel', rotRect(...polar(100, 100, 58, 45), 10, 14, -45)],
    ['steel', rrect(150, 93, 12, 14, 3)],
    ['tube', circle(100, 100, 52), 7],
    ['fine', ticks(100, 100, 44, 48, 60), 1],
    ['fine', circle(100, 74, 12) + circle(76, 106, 12) + circle(124, 106, 12), 1.8],
    ['blue', hand(100, 74, 9, 40) + hand(76, 106, 9, 250) + hand(124, 106, 9, 130), 2.2],
    ['blue', hand(100, 100, 30, 330, 6), 4], ['blue', hand(100, 100, 40, 30, 4), 3],
    ['tube', hand(100, 100, 44, 150, 12), 1.6],
    ['steel', circle(100, 100, 4.5)] ] },
  { slug: 'moon-phase', name: 'Moon phase', group: 'Complications', layers: [
    ['sky', 'M36 126A64 64 0 0 1 164 126Z'],
    ['sand', sparkle(70, 82, 6)], ['sand', sparkle(128, 70, 5)], ['sand', sparkle(146, 104, 4)], ['sand', sparkle(86, 108, 3.5)],
    ['sand', circle(104, 92, 20)],
    ['fine', circle(98, 88, 4) + circle(110, 100, 3), 1.2],
    ['steel', 'M36 126A30 30 0 0 1 96 126Z'], ['steel', 'M104 126A30 30 0 0 1 164 126Z'],
    ['tube', 'M28 128A72 72 0 0 1 172 128Z', 6],
    ['fine', Array.from({ length: 13 }, (_, i) => seg(polar(100, 128, 78, 180 + i * 15), polar(100, 128, i % 3 ? 82 : 86, 180 + i * 15))).join(''), 1.6] ] },
  { slug: 'tourbillon', name: 'Tourbillon', group: 'Complications', layers: [
    ['tube', circle(100, 100, 62), 4],
    ['fine', gear(100, 100, 66, 72, 48), 1.2],
    ['blue', circle(100, 100, 34), 3],
    ['blue', spiral(100, 100, 4, 22, 3), 1.4],
    ['tube', [0, 120, 240].map((a) => seg([100, 100], polar(100, 100, 62, a - 90))).join(''), 6],
    ...[0, 120, 240].map((a) => ['steel', circle(...polar(100, 100, 62, a - 90), 7)]),
    ['steel', circle(100, 100, 11)], ['ruby', circle(100, 100, 5)] ] },
  { slug: 'power-reserve', name: 'Power reserve', group: 'Complications', layers: [
    ['tube', arc(100, 128, 66, 200, 340), 6],
    ['fine', Array.from({ length: 15 }, (_, i) => seg(polar(100, 128, 52, 200 + i * 10), polar(100, 128, i % 7 === 0 ? 62 : 58, 200 + i * 10))).join(''), 1.8],
    ['ruby', circle(...polar(100, 128, 40, 206), 5)], ['sand', circle(...polar(100, 128, 40, 334), 5)],
    ['blue', seg([100, 128], polar(100, 128, 56, 300)), 4.5],
    ['steel', circle(100, 128, 8)],
    ['tube', 'M44 160H156', 4] ] },
  { slug: 'world-time', name: 'World time', group: 'Complications', layers: [
    ['tube', circle(100, 100, 70), 3],
    ['fine', ticks(100, 100, 64, 70, 24), 1.8],
    ['sky', circle(100, 100, 50)],
    ['tube', ellipse(100, 100, 22, 50) + 'M50 100H150M56 76H144M56 124H144', 2.5],
    ['tube', circle(100, 100, 50), 5],
    ['blue', hand(100, 100, 62, 40), 3.5], ['steel', circle(100, 100, 5)] ] },
  { slug: 'alarm', name: 'Alarm', group: 'Complications', layers: [
    ['steel', 'M42 66A26 26 0 0 1 80 40Z'], ['steel', 'M120 40A26 26 0 0 1 158 66Z'],
    ['tube', 'M100 54V38M86 38H114', 4],
    ['tube', 'M66 160L54 178M134 160L146 178', 5],
    ['tube', circle(100, 112, 50), 7],
    ['fine', ticks(100, 112, 36, 42, 12), 2.2],
    ['blue', hand(100, 112, 22, 320, 5), 4.5], ['blue', hand(100, 112, 32, 60, 6), 3.5],
    ['sand', hand(100, 112, 30, 200), 2], ['steel', circle(100, 112, 4.5)] ] },

  // ── Atelier ──
  { slug: 'loupe', name: 'Loupe', group: 'Atelier', layers: [
    ['steel', rotRect(144, 144, 20, 64, -45)],
    ['fine', [-24, -16, -8, 0, 8, 16, 24].map((o) => seg([144 + o * 0.707 - 9 * 0.707, 144 + o * 0.707 + 9 * 0.707], [144 + o * 0.707 + 9 * 0.707, 144 + o * 0.707 - 9 * 0.707])).join(''), 1.2],
    ['tube', seg([116, 116], [124, 124]), 8],
    ['glass', circle(82, 82, 46)],
    ['fine', 'M58 70C62 58 70 52 80 48', 3],
    ['tube', circle(82, 82, 48), 8] ] },
  { slug: 'screwdriver', name: 'Screwdriver', group: 'Atelier', transform: 'rotate(-45 100 100)', layers: [
    ['tube', 'M100 112V178', 4], ['fine', 'M97 178H103', 2],
    ['steel', rrect(86, 40, 28, 74, 6)],
    ['fine', 'M94 50V104M100 50V104M106 50V104', 1.3],
    ['blue', circle(100, 30, 10), 4], ['steel', circle(100, 30, 6)] ] },
  { slug: 'tweezers', name: 'Tweezers', group: 'Atelier', layers: [
    ['tube', 'M94 24C86 80 80 140 86 178', 6],
    ['tube', 'M106 24C114 80 120 140 114 178', 6],
    ['fine', 'M88 80L112 80', 1.4],
    ['steel', rrect(88, 16, 24, 20, 6)],
    ['ruby', circle(100, 182, 4)] ] },
  { slug: 'watch-box', name: 'Watch box', group: 'Atelier', layers: [
    ['steel', 'M34 104L50 40H150L166 104Z'],
    ['sky', 'M48 98L60 50H140L152 98Z'],
    ['tube', 'M30 104H170V164H30Z', 5],
    ['fine', 'M30 120H170', 1.4],
    ['steel', rrect(92, 128, 16, 12, 2)],
    ['tube', circle(100, 80, 18), 3], ['blue', hand(100, 80, 10, 300) + hand(100, 80, 13, 60), 2.2] ] },
  { slug: 'buckle', name: 'Buckle', group: 'Atelier', layers: [
    ['steel', rrect(74, 16, 52, 48, 6)], ['steel', rrect(74, 136, 52, 48, 6)],
    ['fine', 'M78 32H122M78 48H122M78 152H122M78 168H122', 1.4],
    ['tube', rrect(56, 70, 88, 60, 18), 7],
    ['tube', 'M56 100H144', 4],
    ['blue', 'M100 100V60', 5] ] },
  { slug: 'case-back', name: 'Case back', group: 'Atelier', layers: [
    ['tube', circle(100, 100, 66), 6],
    ...Array.from({ length: 6 }, (_, i) => ['steel', rotRect(...polar(100, 100, 66, i * 60 - 90), 12, 14, i * 60)]),
    ['fine', circle(100, 100, 56), 1.4],
    ['glass', circle(100, 100, 42)],
    ['fine', gear(100, 100, 24, 30, 12) + circle(100, 100, 18), 1.4],
    ['ruby', circle(100, 100, 4)],
    ['tube', circle(100, 100, 42), 4] ] },
];
