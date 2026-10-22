// Geometry for the Maison set: Art Deco fine-dining icons.
// Each icon has three kinds of mark:
//   inline: the signature hollow double-rail stroke (9 px wide with a 3 px open core)
//   solid:  filled gold shapes (fans, flames, gems)
//   rule:   fine 2 px lines; an entry can be [d, width] or { d, w, clip } to clip it to a shape
// All drawn on a 200 × 200 grid.

export const groups = ['Service', 'Cellar', 'Delicacies', 'Kitchen'];

const r = (n) => Math.round(n * 100) / 100;
const circle = (cx, cy, rad) => `M${r(cx - rad)} ${cy}A${rad} ${rad} 0 1 0 ${r(cx + rad)} ${cy}A${rad} ${rad} 0 1 0 ${r(cx - rad)} ${cy}Z`;
const ellipse = (cx, cy, rx, ry) => `M${r(cx - rx)} ${cy}A${rx} ${ry} 0 1 0 ${r(cx + rx)} ${cy}A${rx} ${ry} 0 1 0 ${r(cx - rx)} ${cy}Z`;
const polar = (cx, cy, rad, deg) => [r(cx + rad * Math.cos((deg * Math.PI) / 180)), r(cy + rad * Math.sin((deg * Math.PI) / 180))];
const flame = (x, y, h = 20) => `M${x} ${y}C${x + 7} ${y + h * 0.5} ${x + 6} ${y + h * 0.9} ${x} ${y + h}C${x - 6} ${y + h * 0.9} ${x - 7} ${y + h * 0.5} ${x} ${y}Z`;
// Laurel leaf centred on (x, y), its long axis at angle a.
const leaf = (x, y, a, len = 13, w = 6) => {
  const [ux, uy] = [Math.cos((a * Math.PI) / 180), Math.sin((a * Math.PI) / 180)];
  const p = (s, t) => `${r(x + s * ux - t * uy)} ${r(y + s * uy + t * ux)}`;
  return `M${p(len, 0)}Q${p(0, w * 1.6)} ${p(-len, 0)}Q${p(0, -w * 1.6)} ${p(len, 0)}Z`;
};
// Fluted edge: n outward scallops around a circle.
const scallops = (cx, cy, rad, n) => {
  let d = '';
  for (let i = 0; i < n; i++) {
    const a0 = (i * 360) / n, a1 = ((i + 1) * 360) / n;
    const [x0, y0] = polar(cx, cy, rad, a0), [x1, y1] = polar(cx, cy, rad, a1);
    const b = r(rad * Math.sin(Math.PI / n));
    d += `${i ? '' : `M${x0} ${y0}`}A${b} ${b} 0 0 1 ${x1} ${y1}`;
  }
  return d + 'Z';
};
const diamond = (x, y, w, h = w) => `M${x} ${y - h}L${x + w} ${y}L${x} ${y + h}L${x - w} ${y}Z`;
const star = (cx, cy, R, ri, n = 5, rot = -90) => {
  const pts = [];
  for (let i = 0; i < n * 2; i++) pts.push(polar(cx, cy, i % 2 ? ri : R, rot + (i * 180) / n));
  return 'M' + pts.map((p) => p.join(' ')).join('L') + 'Z';
};
// Sunburst rays from a centre between two radii.
const rays = (cx, cy, r0, r1, from, to, n) => {
  let d = '';
  for (let i = 0; i < n; i++) {
    const a = from + ((to - from) * i) / (n - 1);
    const [x0, y0] = polar(cx, cy, r0, a), [x1, y1] = polar(cx, cy, r1, a);
    d += `M${x0} ${y0}L${x1} ${y1}`;
  }
  return d;
};
// Dots packed inside an ellipse (caviar, bubbles).
const beads = (cx, cy, rx, ry, gap, rad) => {
  let d = '';
  for (let y = cy - ry; y <= cy + ry; y += gap * 0.86) {
    const row = Math.round((y - cy + ry) / (gap * 0.86));
    for (let x = cx - rx + (row % 2 ? gap / 2 : 0); x <= cx + rx; x += gap) {
      if (((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 0.82) d += circle(r(x), r(y), rad);
    }
  }
  return d;
};
const lattice = (gap) => {
  let d = '';
  for (let t = -200; t <= 400; t += gap) d += `M${t} 0L${t - 200} 200M${t - 200} 0L${t} 200`;
  return d;
};

export const icons = [
  // ── Service ──
  { slug: 'cloche', name: 'Cloche', group: 'Service',
    inline: ['M38 138A62 62 0 0 1 162 138', 'M24 150H176'],
    solid: [circle(100, 66, 8), 'M86 138A14 14 0 0 1 114 138Z', 'M60 166H140L132 158H68Z'],
    rule: [rays(100, 138, 22, 50, -160, -20, 7)] },
  { slug: 'place-setting', name: 'Place setting', group: 'Service',
    inline: [circle(100, 106, 46), 'M34 84V164', 'M166 100V164'],
    solid: ['M26 40H42V70C42 78 38 82 34 82C30 82 26 78 26 70Z', 'M166 38C178 50 178 86 166 100Z', diamond(100, 106, 12, 16)],
    rule: [circle(100, 106, 32), 'M31 40V64M37 40V64', rays(100, 106, 18, 28, 0, 315, 8)] },
  { slug: 'reserved', name: 'Reserved', group: 'Service',
    inline: ['M46 160L60 58H140L154 160Z'],
    solid: [star(100, 112, 13, 5.5), 'M28 174H172L166 166H34Z'],
    rule: ['M72 84H128', 'M78 96H122', 'M72 140H128'] },
  { slug: 'menu', name: 'Menu', group: 'Service',
    inline: ['M56 178V74A44 44 0 0 1 144 74V178Z'],
    solid: ['M82 80A18 18 0 0 1 118 80Z'],
    rule: [rays(100, 80, 22, 32, -165, -15, 7), 'M76 108H124', ['M84 124H116M80 136H120M88 148H112M84 160H116', 1.6]] },
  { slug: 'candelabra', name: 'Candelabra', group: 'Service',
    inline: ['M48 100C48 128 152 128 152 100', 'M100 98V158', 'M38 98H62M88 96H112M138 98H162'],
    solid: ['M43 64H57V94H43Z', 'M93 42H107V92H93Z', 'M143 64H157V94H143Z', flame(50, 38), flame(100, 16), flame(150, 38),
      'M66 180H134L122 164H78Z'],
    rule: ['M50 82V88', 'M150 82V88'] },
  { slug: 'award', name: 'Award', group: 'Service',
    inline: ['M66 160C34 140 28 92 50 58', 'M134 160C166 140 172 92 150 58'],
    solid: [star(100, 98, 30, 13),
      ...[[38, 146, 50], [28, 120, 75], [28, 94, 100], [36, 70, 125], [162, 146, 130], [172, 120, 105], [172, 94, 80], [164, 70, 55]]
        .map(([x, y, a]) => leaf(x, y, a)),
      'M80 168H120L114 178H86Z'],
    rule: [circle(100, 98, 42)] },

  // ── Cellar ──
  { slug: 'wine-glass', name: 'Wine glass', group: 'Cellar',
    inline: ['M66 34C62 84 76 110 100 112C124 110 138 84 134 34Z', 'M100 112V160', 'M70 166H130'],
    solid: ['M75 74C78 94 88 102 100 102C112 102 122 94 125 74Z', diamond(100, 136, 6, 8)] },
  { slug: 'champagne-coupe', name: 'Champagne coupe', group: 'Cellar',
    inline: ['M40 72C48 102 74 110 100 110C126 110 152 102 160 72Z', 'M100 110V160', 'M70 166H130'],
    solid: ['M54 82C62 96 80 100 100 100C120 100 138 96 146 82Z', diamond(100, 136, 6, 8), circle(90, 56, 3.5), circle(104, 42, 3), circle(96, 28, 2.4), circle(110, 18, 2)] },
  { slug: 'decanter', name: 'Decanter', group: 'Cellar',
    inline: ['M90 34V64C60 78 48 104 52 132C56 160 76 172 100 172C124 172 144 160 148 132C152 104 140 78 110 64V34', 'M84 34H116'],
    solid: [diamond(100, 18, 9, 12), 'M62 128C64 152 80 160 100 160C120 160 136 152 138 128Z'],
    rule: ['M74 96L100 82L126 96', 'M68 112L100 96L132 112'] },
  { slug: 'martini', name: 'Martini', group: 'Cellar',
    inline: ['M42 50H158L100 114Z', 'M100 114V160', 'M70 166H130'],
    solid: ['M68 66H132L100 100Z', circle(132, 40, 9), diamond(100, 138, 6, 8)],
    rule: ['M146 24L104 80'] },
  { slug: 'cocktail-shaker', name: 'Cocktail shaker', group: 'Cellar',
    inline: ['M76 44H124L118 66H82Z', 'M74 72H126L118 178H82Z'],
    solid: ['M88 20H112V36H88Z', 'M84 100H116L115 110H85Z'],
    rule: ['M80 90H120', 'M86 122H114', 'M87 134H113'] },
  { slug: 'ice-bucket', name: 'Ice bucket', group: 'Cellar',
    inline: ['M50 102H150L136 178H64Z', 'M92 100V62C92 54 96 50 96 40V30M112 30V40C112 50 116 54 116 62V100', 'M50 114C36 114 36 132 52 132M150 114C164 114 164 132 148 132'],
    solid: ['M93 14H115V32H93Z'],
    rule: ['M64 102L72 90L82 102M120 102L128 90L138 102', 'M78 116L82 166M100 116V166M122 116L118 166'] },

  // ── Delicacies ──
  { slug: 'oyster', name: 'Oyster', group: 'Delicacies',
    inline: ['M38 104A62 62 0 0 1 162 104Z', 'M32 118H168C160 158 40 158 32 118Z'],
    solid: [circle(100, 134, 11), 'M88 104A12 12 0 0 1 112 104Z'],
    rule: [rays(100, 104, 16, 54, -168, -12, 9)] },
  { slug: 'caviar', name: 'Caviar', group: 'Delicacies',
    inline: [ellipse(100, 78, 66, 20), 'M34 78V130C34 154 166 154 166 130V78'],
    solid: [beads(100, 78, 54, 13, 8.5, 2.9), 'M58 172H142L136 164H64Z'],
    rule: ['M34 106C34 128 166 128 166 106'] },
  { slug: 'grapes', name: 'Grapes', group: 'Delicacies',
    inline: [circle(70, 78, 13), circle(100, 78, 13), circle(130, 78, 13), circle(85, 106, 13), circle(115, 106, 13), circle(100, 134, 13), 'M100 64C100 50 96 40 88 30'],
    solid: [leaf(122, 38, -20, 18, 9), circle(100, 166, 4)],
    rule: ['M100 52C112 48 120 44 124 36', 'M100 148V160'] },
  { slug: 'fish', name: 'Fish course', group: 'Delicacies',
    inline: ['M28 100C52 64 112 58 146 100C112 142 52 136 28 100Z', 'M20 166H180'],
    solid: ['M146 100L180 74V126Z', circle(56, 94, 5)],
    rule: ['M74 76C84 88 84 112 74 124', { d: 'M84 100a8 8 0 0 1 16 0a8 8 0 0 1 16 0a8 8 0 0 1 16 0M92 88a8 8 0 0 1 16 0a8 8 0 0 1 16 0M92 112a8 8 0 0 1 16 0a8 8 0 0 1 16 0', w: 1.6 }] },
  { slug: 'fruit-tart', name: 'Fruit tart', group: 'Delicacies',
    inline: [scallops(100, 104, 64, 18)],
    solid: [...Array.from({ length: 8 }, (_, i) => circle(...polar(100, 104, 34, i * 45), 8)), star(100, 104, 14, 6, 4, -90)],
    rule: [circle(100, 104, 50), circle(100, 104, 22)] },
  { slug: 'cheese', name: 'Cheese', group: 'Delicacies',
    inline: ['M26 118L150 64L174 96V152H26Z', 'M26 118L174 96'],
    solid: [circle(62, 134, 7), circle(112, 128, 9), circle(150, 138, 6), circle(88, 144, 4), ellipse(126, 88, 7, 3.5)],
    rule: ['M20 168H180'] },

  // ── Kitchen ──
  { slug: 'toque', name: "Chef's toque", group: 'Kitchen',
    inline: ['M62 116C40 112 36 78 62 74C64 48 92 42 100 58C108 42 136 48 138 74C164 78 160 112 138 116Z', 'M62 124H138V156H62Z'],
    solid: [diamond(100, 140, 7, 9)],
    rule: ['M78 128V152M122 128V152', 'M80 96C84 84 92 80 100 84M120 96C116 84 108 80 100 84'] },
  { slug: 'chef-knife', name: "Chef's knife", group: 'Kitchen',
    inline: ['M132 90H46C32 90 22 100 20 110C58 122 104 118 132 114Z', 'M144 90H174C182 90 182 114 174 114H144'],
    solid: ['M132 84H144V120H132Z', circle(156, 102, 3.5), circle(168, 102, 3.5)],
    rule: ['M44 104H126'],
    transform: 'rotate(-32 100 100)' },
  { slug: 'whisk', name: 'Whisk', group: 'Kitchen',
    inline: ['M100 118C58 92 66 28 100 22C134 28 142 92 100 118', 'M100 132V180'],
    solid: ['M90 116H110V132H90Z'],
    rule: ['M100 118C82 92 84 42 100 24C116 42 118 92 100 118', 'M100 118V24'] },
  { slug: 'saucepan', name: 'Saucepan', group: 'Kitchen',
    inline: ['M38 96H134V142C134 154 126 162 114 162H58C46 162 38 154 38 142Z', 'M134 106H182'],
    solid: ['M30 88H142V96H30Z'],
    rule: ['M58 76C52 66 64 58 58 46M86 76C80 66 92 58 86 46M114 76C108 66 120 58 114 46', 'M38 118H134'] },
  { slug: 'gateau', name: 'Gâteau', group: 'Kitchen',
    inline: ['M42 132H158V174H42Z', 'M58 98H142V132H58Z', 'M74 68H126V98H74Z'],
    solid: ['M95 44H105V66H95Z', flame(100, 22, 18)],
    rule: ['M42 146C56 160 70 160 84 146C98 160 112 160 126 146C140 160 154 160 158 152', 'M58 110C68 120 80 120 90 110C100 120 112 120 122 110C130 118 138 118 142 112', 'M74 80C82 88 92 88 100 80C108 88 118 88 126 80'] },
  { slug: 'pepper-mill', name: 'Pepper mill', group: 'Kitchen',
    inline: ['M86 36H114L118 62C128 74 128 92 118 102L126 176H74L82 102C72 92 72 74 82 62Z'],
    solid: [circle(100, 24, 8), 'M80 116H120L121 126H79Z'],
    rule: ['M84 140H116', 'M84 150H116', 'M86 62H114'] },
];
