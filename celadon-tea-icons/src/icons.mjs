// Geometry for the Celadon set: tea-ceremony icons in glazed ceramic.
// Each icon is a list of layers drawn in order. Layer kinds:
//   clay:   raw, speckled clay
//   glaze:  a glossy glaze fill (see GLAZES in build.mjs), optionally clipped
//   drip:   where a glaze ends, as a line
//   shine:  a white gloss highlight (glazed version only)
//   paint:  a stroke in a glaze colour (painted bands, brushwork)
//   smoke:  a soft grey stroke
//   out:    an outline; line: an inner detail line
// Drawn on a 200 × 200 grid.

export const groups = ['Ceremony', 'Teaware', 'Leaf', 'Tea house'];

const r = (n) => Math.round(n * 100) / 100;
const P = (x, y) => `${r(x)} ${r(y)}`;
const polar = (cx, cy, rad, deg) => [cx + rad * Math.cos((deg * Math.PI) / 180), cy + rad * Math.sin((deg * Math.PI) / 180)];
const circle = (cx, cy, rad) => `M${P(cx - rad, cy)}A${rad} ${rad} 0 1 0 ${P(cx + rad, cy)}A${rad} ${rad} 0 1 0 ${P(cx - rad, cy)}Z`;
const ellipse = (cx, cy, rx, ry) => `M${P(cx - rx, cy)}A${rx} ${ry} 0 1 0 ${P(cx + rx, cy)}A${rx} ${ry} 0 1 0 ${P(cx - rx, cy)}Z`;
const rect = (x, y, w, h) => `M${x} ${y}H${x + w}V${y + h}H${x}Z`;

// Seeded random, so drips and speckles are the same on every build.
const rng = (seed) => () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

// A glaze edge running left to right at height y, with rounded drips hanging off it.
export function dripLine(x0, x1, y, seed = 3, depth = 12) {
  const rand = rng(seed);
  let x = x0, d = `M${P(x0, y)}`;
  while (x < x1) {
    const w = 10 + rand() * 14, k = rand() < 0.55 ? 3 + rand() * depth : rand() * 2;
    const nx = Math.min(x1, x + w);
    d += `C${P(x + (nx - x) * 0.2, y)} ${P(x + (nx - x) * 0.22, y + k)} ${P(x + (nx - x) * 0.5, y + k)}` +
      `C${P(x + (nx - x) * 0.78, y + k)} ${P(x + (nx - x) * 0.8, y)} ${P(nx, y)}`;
    x = nx;
  }
  return d;
}
// Everything above a drip line: used to clip a glaze to the top of a pot.
const above = (y, seed, depth) => `${dripLine(-10, 210, y, seed, depth)}V-10H-10Z`;

// Seeded dots inside a box (speckles, hobnails, crackle anchors).
const speckles = (x0, y0, x1, y1, n, seed = 9, min = 0.7, max = 1.5) => {
  const rand = rng(seed);
  let d = '';
  for (let i = 0; i < n; i++) d += circle(x0 + rand() * (x1 - x0), y0 + rand() * (y1 - y0), r(min + rand() * (max - min)));
  return d;
};
const crackle = (x0, y0, x1, y1, seed = 21) => {
  const rand = rng(seed);
  let d = '';
  for (let i = 0; i < 26; i++) {
    let x = x0 + rand() * (x1 - x0), y = y0 + rand() * (y1 - y0);
    d += `M${P(x, y)}`;
    for (let j = 0; j < 3; j++) { x += (rand() - 0.5) * 22; y += (rand() - 0.5) * 18; d += `L${P(x, y)}`; }
  }
  return d;
};
const hobnails = (x0, y0, x1, y1, gap, rad) => {
  let d = '';
  for (let y = y0, row = 0; y <= y1; y += gap, row++) for (let x = x0 + (row % 2 ? gap / 2 : 0); x <= x1; x += gap) d += circle(x, y, rad);
  return d;
};
const petals = (cx, cy, rad, n, rot = -90, w = 0.6) => {
  let d = '';
  for (let i = 0; i < n; i++) {
    const a = rot + (i * 360) / n;
    const [tx, ty] = polar(cx, cy, rad, a), [lx, ly] = polar(cx, cy, rad * 0.75, a - 36 * w), [rx, ry] = polar(cx, cy, rad * 0.75, a + 36 * w);
    d += `M${P(cx, cy)}C${P(lx, ly)} ${P(tx, ty)} ${P(tx, ty)}C${P(tx, ty)} ${P(rx, ry)} ${P(cx, cy)}Z`;
  }
  return d;
};
const leafShape = (cx, cy, len, wid, deg) => {
  const a = (deg * Math.PI) / 180, ux = Math.cos(a), uy = Math.sin(a);
  const p = (s, t) => P(cx + s * ux - t * uy, cy + s * uy + t * ux);
  return `M${p(-len, 0)}C${p(-len * 0.5, -wid)} ${p(len * 0.5, -wid)} ${p(len, 0)}C${p(len * 0.5, wid)} ${p(-len * 0.5, wid)} ${p(-len, 0)}Z`;
};
const midrib = (cx, cy, len, deg) => {
  const [x0, y0] = polar(cx, cy, -len * 0.85, deg), [x1, y1] = polar(cx, cy, len * 0.85, deg);
  return `M${P(x0, y0)}L${P(x1, y1)}`;
};

// Layer constructors.
const clay = (d, clip) => ({ t: 'clay', d, clip });
const glaze = (d, g, clip) => ({ t: 'glaze', d, g, clip });
const drip = (d, clip) => ({ t: 'drip', d, clip });
const shine = (d, w = 5) => ({ t: 'shine', d, w });
const paint = (d, g, w = 3, clip) => ({ t: 'paint', d, g, w, clip });
const smoke = (d, w = 2.4) => ({ t: 'smoke', d, w });
const out = (d, w = 2.6) => ({ t: 'out', d, w });
const line = (d, w = 1.8, clip) => ({ t: 'line', d, w, clip });

// ── Ceremony ──
const bowl = 'M28 64C28 112 44 140 70 148L72 162H128L130 148C156 140 172 112 172 64Z';
const yunomi = 'M62 46H138L132 146C131 156 69 156 68 146Z';
const kyusu = 'M50 112C50 84 72 72 100 72C128 72 150 84 150 112C150 140 128 152 100 152C72 152 50 140 50 112Z';
const tetsu = 'M42 120C42 90 68 80 100 80C132 80 158 90 158 120C158 150 132 164 100 164C68 164 42 150 42 120Z';

export const icons = [
  { slug: 'chawan', name: 'Matcha bowl', group: 'Ceremony', layers: [
    clay(bowl), glaze(bowl, 'shino', above(126, 4)), drip(dripLine(20, 180, 126, 4), bowl),
    glaze(ellipse(100, 64, 72, 13), 'shinoIn'), glaze(ellipse(100, 66, 60, 9), 'matcha'),
    glaze(ellipse(88, 64, 16, 3), 'froth'),
    shine('M44 84C46 102 52 116 62 126'), out(bowl), out(ellipse(100, 64, 72, 13), 2.2), line('M72 148H128', 1.6) ] },
  { slug: 'chasen', name: 'Whisk', group: 'Ceremony', layers: [
    glaze('M84 86C58 102 50 140 62 172H138C150 140 142 102 116 86Z', 'bamboo'),
    glaze('M86 30C86 24 114 24 114 30V88H86Z', 'bamboo'),
    line('M100 92C84 112 80 140 84 170M100 92C116 112 120 140 116 170M100 92V170M100 92C72 110 64 140 70 170M100 92C128 110 136 140 130 170', 1.4),
    glaze(ellipse(100, 116, 14, 18), 'bambooDark'), line('M88 104C92 118 92 128 90 132M112 104C108 118 108 128 110 132', 1.2),
    line('M86 58H114', 2), shine('M92 34V80', 3),
    out('M84 86C58 102 50 140 62 172H138C150 140 142 102 116 86Z'), out('M86 30C86 24 114 24 114 30V88H86Z') ] },
  { slug: 'chashaku', name: 'Tea scoop', group: 'Ceremony', transform: 'rotate(-28 100 100)', layers: [
    glaze('M24 100C24 92 34 88 48 90L176 96C182 96 182 104 176 104L48 110C36 112 24 108 24 100Z', 'bamboo'),
    glaze(ellipse(38, 94, 12, 6), 'matcha'),
    line('M120 93V107', 2.4), line('M114 95C116 98 116 102 114 105', 1.2),
    shine('M60 94L160 97', 2.4),
    out('M24 100C24 92 34 88 48 90L176 96C182 96 182 104 176 104L48 110C36 112 24 108 24 100Z'), out(ellipse(38, 94, 12, 6), 1.6) ] },
  { slug: 'natsume', name: 'Tea caddy', group: 'Ceremony', layers: [
    glaze('M50 98C50 70 150 70 150 98V132C150 166 50 166 50 132Z', 'lacquer'),
    glaze(petals(124, 124, 14, 5, -90, 0.7), 'gold'), glaze(circle(124, 124, 3), 'lacquer'),
    glaze(petals(80, 136, 9, 5, -60, 0.7), 'gold'),
    paint('M58 112C80 100 96 118 112 104', 'gold', 2),
    line('M50 100C50 108 150 108 150 100', 2.2),
    shine('M62 80C74 74 90 72 104 72', 4), shine('M60 116V136', 3),
    out('M50 98C50 70 150 70 150 98V132C150 166 50 166 50 132Z') ] },
  { slug: 'hishaku', name: 'Ladle', group: 'Ceremony', layers: [
    glaze('M70 98L178 158L174 166L66 106Z', 'bamboo'),
    glaze('M28 64H72V118C72 126 28 126 28 118Z', 'bamboo'), glaze(ellipse(50, 64, 22, 7), 'bambooDark'),
    line('M28 84H72', 1.8), shine('M36 72V112', 3),
    out('M70 98L178 158L174 166L66 106Z'), out('M28 64H72V118C72 126 28 126 28 118Z'), out(ellipse(50, 64, 22, 7), 2) ] },
  { slug: 'wagashi', name: 'Wagashi', group: 'Ceremony', layers: [
    clay('M24 138C24 156 176 156 176 138L168 150C150 162 50 162 32 150Z'),
    glaze(ellipse(100, 136, 76, 20), 'celadon'), glaze(ellipse(100, 134, 58, 13), 'celadonIn'),
    glaze(petals(96, 104, 34, 5, -90, 0.95), 'sakura'), line(petals(96, 104, 34, 5, -90, 0.95), 1.4), glaze(circle(96, 104, 6), 'amber'),
    glaze('M136 132L178 94L182 98L142 136Z', 'bamboo'),
    shine('M38 130C46 124 60 122 74 121', 3), shine('M84 84C88 80 94 78 98 78', 3),
    out(ellipse(100, 136, 76, 20)), out('M24 136C24 156 176 156 176 136', 2.2), out('M136 132L178 94L182 98L142 136Z', 1.6) ] },

  // ── Teaware ──
  { slug: 'kyusu', name: 'Kyusu teapot', group: 'Teaware', layers: [
    glaze('M56 104C40 100 30 86 22 70L30 66C36 80 46 88 58 90Z', 'ruri'), glaze('M146 108L186 128C190 130 188 140 182 138L142 122Z', 'ruriDark'),
    glaze(kyusu, 'ruri'), glaze(ellipse(100, 76, 34, 9), 'ruriDark'), glaze(ellipse(100, 70, 9, 6), 'ruri'),
    paint('M56 124C80 132 120 132 144 124', 'shino', 3, kyusu),
    shine('M66 92C72 84 82 80 92 79', 5),
    out('M56 104C40 100 30 86 22 70L30 66C36 80 46 88 58 90', 2.2), out('M146 108L186 128C190 130 188 140 182 138L142 122', 2.2), out(kyusu), out(ellipse(100, 76, 34, 9), 2), out(ellipse(100, 70, 9, 6), 2) ] },
  { slug: 'dobin', name: 'Dobin teapot', group: 'Teaware', layers: [
    { t: 'paintBack', d: 'M56 96C56 32 144 32 144 96', g: 'bamboo', w: 7 },
    clay('M52 132C52 158 148 158 148 132V128H52Z'),
    glaze('M48 120C48 96 72 88 100 88C128 88 152 96 152 120C152 132 148 140 140 146H60C52 140 48 132 48 120Z', 'celadon', above(140, 7, 8)),
    glaze('M150 112L184 92L188 98L156 126Z', 'celadon'),
    glaze(ellipse(100, 90, 28, 7), 'celadonIn'), glaze(ellipse(100, 84, 8, 5), 'celadon'),
    drip(dripLine(48, 152, 140, 7, 8), 'M48 120C48 96 72 88 100 88C128 88 152 96 152 120C152 158 48 158 48 120Z'),
    shine('M62 108C66 100 76 96 86 95', 5),
    out('M48 120C48 96 72 88 100 88C128 88 152 96 152 120C152 158 48 158 48 120Z'), out('M150 112L184 92L188 98L156 126', 2.2),
    out(ellipse(100, 90, 28, 7), 2), out(ellipse(100, 84, 8, 5), 2), out('M56 96C56 32 144 32 144 96', 2) ] },
  { slug: 'yunomi', name: 'Yunomi cup', group: 'Teaware', layers: [
    clay(yunomi), glaze(yunomi, 'tenmoku', above(130, 11, 14)),
    paint('M76 54L78 116M90 54L91 122M104 54V118M118 54L117 124M130 54L127 112', 'hare', 1.6, `${above(130, 11, 14)}`),
    drip(dripLine(60, 140, 130, 11, 14), yunomi),
    glaze(ellipse(100, 46, 38, 8), 'tenmokuIn'),
    shine('M72 56L74 120', 4.5),
    out(yunomi), out(ellipse(100, 46, 38, 8), 2.2), line('M70 152C80 156 120 156 130 152', 1.6) ] },
  { slug: 'gaiwan', name: 'Gaiwan', group: 'Teaware', layers: [
    glaze(ellipse(100, 152, 74, 16), 'shino'), glaze(ellipse(100, 150, 56, 10), 'shinoIn'),
    glaze('M50 98H150C150 132 128 150 100 150C72 150 50 132 50 98Z', 'shino'),
    glaze('M44 98C44 70 156 70 156 98Z', 'shino'), glaze(ellipse(100, 70, 12, 6), 'shino'),
    paint('M56 116C80 124 120 124 144 116', 'ruri', 3), paint('M52 90C80 82 120 82 148 90', 'ruri', 3),
    shine('M60 104C62 116 68 126 76 132', 4), shine('M60 86C70 80 82 78 92 78', 3),
    out(ellipse(100, 152, 74, 16)), out('M50 98C50 132 72 150 100 150C128 150 150 132 150 98'), out('M44 98C44 70 156 70 156 98Z'), out(ellipse(100, 70, 12, 6), 2) ] },
  { slug: 'yuzamashi', name: 'Cooling pitcher', group: 'Teaware', layers: [
    clay('M66 140C68 160 132 160 134 140Z'),
    glaze('M54 64H146L138 140C136 152 64 152 62 140Z', 'celadon', above(140, 13, 6)),
    glaze('M54 64L32 52L58 78Z', 'celadon'),
    line(crackle(60, 70, 140, 140), 0.9, 'M54 64H146L138 140C136 152 64 152 62 140Z'),
    glaze(ellipse(100, 64, 46, 9), 'celadonIn'),
    drip(dripLine(56, 144, 140, 13, 6), 'M54 64H146L138 140C136 160 64 160 62 140Z'),
    shine('M68 76L72 130', 4.5),
    out('M54 64H146L138 140C136 160 64 160 62 140Z'), out('M54 64L32 52L58 78', 2.2), out(ellipse(100, 64, 46, 9), 2.2) ] },
  { slug: 'tetsubin', name: 'Iron kettle', group: 'Teaware', layers: [
    { t: 'paintBack', d: 'M58 92C58 30 142 30 142 92', g: 'iron', w: 6 },
    glaze('M152 118L186 92L190 100L158 132Z', 'iron'),
    glaze(tetsu, 'iron'),
    glaze(hobnails(54, 104, 146, 156, 11, 2.8), 'ironLight', tetsu),
    glaze(ellipse(100, 84, 30, 7), 'ironDark'), glaze(ellipse(100, 78, 8, 5), 'iron'),
    shine('M56 106C60 96 70 90 82 88', 4),
    out(tetsu), out('M152 118L186 92L190 100L158 132', 2.2), out(ellipse(100, 84, 30, 7), 2), out(ellipse(100, 78, 8, 5), 2), out('M58 92C58 30 142 30 142 92', 2) ] },

  // ── Leaf ──
  { slug: 'tea-leaf', name: 'Tea leaf', group: 'Leaf', layers: [
    glaze(leafShape(100, 100, 74, 40, -45), 'matcha'),
    line(midrib(100, 100, 74, -45) + [-40, -16, 8, 32].map((s) => { const [x, y] = polar(100, 100, s, -45); const [a, b] = polar(x, y, 30, -45 - 50); const [c, d] = polar(x, y, 30, -45 + 50 + 180); return `M${P(x, y)}L${P(a, b)}M${P(x, y)}L${P(c, d)}`; }).join(''), 1.6, leafShape(100, 100, 74, 40, -45)),
    shine('M66 112C70 92 84 74 104 64', 4),
    out(leafShape(100, 100, 74, 40, -45)), out('M48 152L36 164', 3) ] },
  { slug: 'tea-sprig', name: 'Tea sprig', group: 'Leaf', layers: [
    out('M100 180C100 140 98 110 100 66', 3),
    glaze(leafShape(66, 118, 38, 20, 30), 'matcha'), glaze(leafShape(134, 100, 38, 20, -30), 'matcha'),
    glaze(leafShape(100, 46, 26, 12, -90), 'matchaLight'),
    line(midrib(66, 118, 38, 30) + midrib(134, 100, 38, -30) + midrib(100, 46, 26, -90), 1.4),
    shine('M44 106C52 100 62 98 72 100', 3), shine('M116 86C124 82 134 82 142 84', 3),
    out(leafShape(66, 118, 38, 20, 30)), out(leafShape(134, 100, 38, 20, -30)), out(leafShape(100, 46, 26, 12, -90)) ] },
  { slug: 'tea-field', name: 'Tea field', group: 'Leaf', layers: [
    glaze(circle(100, 100, 76), 'paper'),
    glaze(circle(136, 64, 14), 'amber', circle(100, 100, 76)),
    glaze('M14 116C50 80 92 74 130 92C156 104 176 104 190 98V190H14Z', 'celadon', circle(100, 100, 76)),
    glaze('M10 140C60 108 120 110 190 136V190H10Z', 'matcha', circle(100, 100, 76)),
    line('M30 108C62 88 96 86 126 98M26 124C60 102 98 100 132 112', 1.6, circle(100, 100, 76)),
    line('M20 152C64 128 120 128 182 148M24 164C70 144 120 144 180 162M30 176C72 158 124 160 176 176', 1.8, circle(100, 100, 76)),
    line('M14 116C50 80 92 74 130 92C156 104 176 104 190 98M10 140C60 108 120 110 190 136', 2.2, circle(100, 100, 76)),
    shine('M42 62C52 48 66 38 82 32', 4),
    out(circle(100, 100, 76), 3), out(circle(100, 100, 84), 1.6) ] },
  { slug: 'tea-tin', name: 'Tea tin', group: 'Leaf', layers: [
    glaze('M56 52H144V156C144 166 56 166 56 156Z', 'vermilion'),
    glaze('M52 36C52 30 148 30 148 36V58C148 64 52 64 52 58Z', 'vermilion'),
    glaze('M56 82H144V136H56Z', 'shino'),
    glaze(leafShape(100, 108, 20, 10, -40), 'matcha'), line(midrib(100, 108, 20, -40), 1.2),
    shine('M66 94V128', 3), shine('M64 62V76', 3), shine('M64 142V150', 3),
    out('M56 52H144V156C144 166 56 166 56 156Z'), out('M52 36C52 30 148 30 148 36V58C148 64 52 64 52 58Z'), line('M56 82H144M56 136H144', 2), out(leafShape(100, 108, 20, 10, -40), 1.6) ] },
  { slug: 'loose-leaf', name: 'Loose leaf', group: 'Leaf', layers: [
    clay('M30 128C34 152 166 152 170 128L160 150C140 162 60 162 40 150Z'),
    glaze(ellipse(100, 126, 72, 22), 'ruri'), glaze(ellipse(100, 124, 58, 15), 'ruriIn'),
    ...[[72, 118, 20], [92, 112, -30], [112, 118, 40], [128, 110, -10], [84, 124, 60], [104, 104, 10], [120, 126, -50], [96, 128, 25], [140, 120, 30], [64, 128, -20]]
      .map(([x, y, a]) => glaze(leafShape(x, y, 11, 4.5, a), 'matchaDark')),
    shine('M40 120C48 112 62 108 76 106', 3),
    out(ellipse(100, 126, 72, 22)), out('M30 128C34 152 166 152 170 128', 2.2) ] },
  { slug: 'matcha', name: 'Matcha powder', group: 'Leaf', layers: [
    glaze(ellipse(100, 146, 78, 18), 'shino'), glaze(ellipse(100, 144, 62, 11), 'shinoIn'),
    glaze('M44 142C56 96 84 70 100 70C116 70 144 96 156 142C130 152 70 152 44 142Z', 'matcha'),
    glaze(speckles(60, 80, 140, 140, 40, 31, 0.8, 1.6), 'matchaLight', 'M44 142C56 96 84 70 100 70C116 70 144 96 156 142Z'),
    shine('M70 118C78 100 88 86 98 80', 4),
    out(ellipse(100, 146, 78, 18)), out('M44 142C56 96 84 70 100 70C116 70 144 96 156 142', 2.4) ] },

  // ── Tea house ──
  { slug: 'tea-house', name: 'Tea house', group: 'Tea house', layers: [
    clay(rect(36, 156, 128, 16)),
    glaze(rect(50, 92, 100, 64), 'shino'),
    glaze('M76 112H124V156H76Z', 'ruri'), line('M100 112V156', 2),
    glaze('M14 98C40 92 60 70 70 46H130C140 70 160 92 186 98L180 104C150 100 120 98 100 98C80 98 50 100 20 104Z', 'iron'),
    line('M40 92H160M56 80H144M64 66H136', 1.4, 'M14 98C40 92 60 70 70 46H130C140 70 160 92 186 98L180 104C150 100 120 98 100 98C80 98 50 100 20 104Z'),
    glaze(rect(66, 34, 68, 12), 'iron'),
    shine('M72 54C66 70 56 82 44 90', 3),
    out(rect(50, 92, 100, 64)), out('M76 112H124V156H76Z', 2), out('M14 98C40 92 60 70 70 46H130C140 70 160 92 186 98L180 104C150 100 120 98 100 98C80 98 50 100 20 104Z'), out(rect(66, 34, 68, 12), 2.2), out(rect(36, 156, 128, 16), 2.2) ] },
  { slug: 'lantern', name: 'Paper lantern', group: 'Tea house', layers: [
    line('M100 12V30', 2.4),
    glaze('M48 100C48 60 72 40 100 40C128 40 152 60 152 100C152 140 128 160 100 160C72 160 48 140 48 100Z', 'paper'),
    line('M52 74C80 70 120 70 148 74M48 100H152M52 126C80 130 120 130 148 126M62 56C84 52 116 52 138 56M62 144C84 148 116 148 138 144', 1.4, 'M48 100C48 60 72 40 100 40C128 40 152 60 152 100C152 140 128 160 100 160C72 160 48 140 48 100Z'),
    glaze(rect(72, 28, 56, 14), 'lacquer'), glaze(rect(72, 158, 56, 14), 'lacquer'),
    paint(circle(100, 100, 18), 'vermilion', 4), paint(petals(100, 100, 11, 3, -90, 0.8), 'vermilion', 2.4),
    line('M100 172V188', 2.4),
    shine('M66 70C62 84 62 108 66 126', 4),
    out('M48 100C48 60 72 40 100 40C128 40 152 60 152 100C152 140 128 160 100 160C72 160 48 140 48 100Z'), out(rect(72, 28, 56, 14), 2.2), out(rect(72, 158, 56, 14), 2.2) ] },
  { slug: 'ikebana', name: 'Ikebana', group: 'Tea house', layers: [
    out('M100 110C96 80 80 60 56 40M92 84C110 70 128 64 150 62M100 110C108 90 124 78 140 30', 3),
    ...[[56, 40, 10], [150, 62, 9], [140, 30, 8], [74, 58, 7], [126, 54, 6]].map(([x, y, s]) => glaze(petals(x, y, s, 5, -90, 0.95), 'sakura')),
    ...[[56, 40], [150, 62], [140, 30]].map(([x, y]) => glaze(circle(x, y, 2.5), 'amber')),
    clay('M70 172H130L126 180H74Z'),
    glaze('M80 110H120C126 130 132 150 126 172H74C68 150 74 130 80 110Z', 'tenmoku', above(160, 17, 6)),
    drip(dripLine(66, 134, 160, 17, 6), 'M80 110H120C126 130 132 150 126 180H74C68 150 74 130 80 110Z'),
    glaze(ellipse(100, 110, 20, 5), 'tenmokuIn'),
    shine('M84 122C80 136 80 150 82 162', 3.5),
    out('M80 110H120C126 130 132 150 126 180H74C68 150 74 130 80 110Z'), out(ellipse(100, 110, 20, 5), 2) ] },
  { slug: 'incense', name: 'Incense', group: 'Tea house', layers: [
    smoke('M108 66C96 54 118 44 106 30C98 20 108 12 114 8', 2.4), smoke('M108 66C122 56 104 46 116 36', 1.6),
    line('M84 154L108 66', 2.8), glaze(circle(108, 66, 3), 'vermilion'),
    clay('M36 160C40 172 160 172 164 160L156 170C140 178 60 178 44 170Z'),
    glaze(ellipse(100, 158, 64, 16), 'celadon'), glaze(ellipse(100, 156, 48, 9), 'ash'),
    glaze(ellipse(84, 154, 7, 4), 'celadon'),
    shine('M46 154C54 148 66 146 78 145', 3),
    out(ellipse(100, 158, 64, 16)), out('M36 160C40 172 160 172 164 160', 2.2), out(ellipse(84, 154, 7, 4), 1.6) ] },
  { slug: 'sensu', name: 'Folding fan', group: 'Tea house', layers: [
    glaze('M100 160L26 96A100 100 0 0 1 174 96Z', 'paper'),
    paint('M44 106C62 96 74 112 92 100C110 88 124 106 144 94C152 90 158 92 162 96', 'ruri', 3.5, 'M100 160L26 96A100 100 0 0 1 174 96Z'),
    paint('M58 82C74 74 84 86 100 78C116 70 128 82 142 76', 'ruri', 2.4, 'M100 160L26 96A100 100 0 0 1 174 96Z'),
    glaze('M100 160L58 114A56 56 0 0 1 142 114Z', 'bamboo'),
    line([-41, -31, -21, -11, 0, 11, 21, 31, 41].map((a) => { const [x, y] = polar(100, 160, 100, -90 + a); return `M100 160L${P(x, y)}`; }).join(''), 1.2),
    glaze(circle(100, 160, 6), 'lacquer'),
    out('M100 160L26 96A100 100 0 0 1 174 96Z'), out('M58 114A56 56 0 0 1 142 114', 2) ] },
  { slug: 'bonsai', name: 'Bonsai', group: 'Tea house', layers: [
    out('M98 140C96 120 84 112 86 96C88 82 104 80 110 66M92 108C80 104 70 96 62 84M104 92C118 92 130 86 140 78', 4),
    glaze('M30 86C30 70 50 64 64 70C74 60 96 64 98 78C100 90 80 98 64 94C52 100 30 98 30 86Z', 'matcha'),
    glaze('M110 74C108 58 130 50 144 58C160 54 176 66 170 80C166 92 146 94 134 88C122 92 112 86 110 74Z', 'matcha'),
    glaze('M80 52C80 38 98 32 110 38C124 34 136 46 130 58C124 68 108 68 98 64C88 66 80 60 80 52Z', 'matchaLight'),
    glaze('M50 140H150L144 168H56Z', 'ruri'), glaze(rect(46, 134, 108, 10), 'ruriDark'),
    shine('M60 150L64 162', 3), shine('M40 80C42 74 48 72 54 72', 2.4), shine('M120 66C122 62 128 60 134 60', 2.4),
    out('M30 86C30 70 50 64 64 70C74 60 96 64 98 78C100 90 80 98 64 94C52 100 30 98 30 86Z', 2.2),
    out('M110 74C108 58 130 50 144 58C160 54 176 66 170 80C166 92 146 94 134 88C122 92 112 86 110 74Z', 2.2),
    out('M80 52C80 38 98 32 110 38C124 34 136 46 130 58C124 68 108 68 98 64C88 66 80 60 80 52Z', 2.2),
    out('M50 144H150L144 168H56Z'), out(rect(46, 134, 108, 10), 2.2) ] },
];
