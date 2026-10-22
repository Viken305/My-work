// Geometry for the Gilt Almanac set. Each icon draws onto a Plate (see lib.mjs).
// Outlines are 3 px, secondary rules 1.2–2 px, engraving lines 0.9–1.2 px.

import { circle, ellipse, poly, polar, sparkle, crescent, lines, rings, spokes, Plate } from './lib.mjs';

export const groups = ['Zodiac', 'Celestial'];

// ── Zodiac coins ────────────────────────────────────────────────────────────
// Field hatching follows the sign's element: fire 45°, earth 0°, air 135°, water 90°.
const ELEMENT = { fire: 45, earth: 0, air: 135, water: 90 };

function coin(glyph, element) {
  return (p) => {
    p.line(circle(100, 100, 88), 3).line(circle(100, 100, 79), 1.4);
    for (let i = 0; i < 40; i++) {
      if (i % 10 === 0) continue;
      p.fill(circle(...polar(100, 100, 83.5, -90 + i * 9), 1.35));
    }
    for (let i = 0; i < 4; i++) p.fill(sparkle(...polar(100, 100, 83.5, -90 + i * 90), 6));
    p.hatch(circle(100, 100, 71), lines({ angle: ELEMENT[element], gap: 4 }), {
      w: 1.1,
      mask: { cutStroke: [[glyph, 22]] },
    });
    p.line(circle(100, 100, 71), 1.2);
    p.line(glyph, 6.5);
  };
}

const zodiac = [
  ['aries', 'Aries', 'fire',
    'M100 146L100 98C100 72 94 56 76 56C62 56 55 68 58 79C61 90 72 92 77 85M100 98C100 72 106 56 124 56C138 56 145 68 142 79C139 90 128 92 123 85'],
  ['taurus', 'Taurus', 'earth',
    `M58 56C60 78 78 90 100 90C122 90 140 78 142 56${circle(100, 115, 25)}`],
  ['gemini', 'Gemini', 'air',
    'M60 58C84 67 116 67 140 58M60 142C84 133 116 133 140 142M84 65L84 135M116 65L116 135'],
  ['cancer', 'Cancer', 'water',
    `${circle(72, 84, 13)}M72 71C96 58 124 60 144 78${circle(128, 116, 13)}M128 129C104 142 76 140 56 122`],
  ['leo', 'Leo', 'fire',
    `${circle(70, 112, 16)}M84 104C76 86 80 62 104 60C128 58 136 78 128 96C120 114 114 130 122 140C128 148 140 146 146 136`],
  ['virgo', 'Virgo', 'earth',
    'M46 70C50 64 56 66 56 74L56 140M56 82C58 68 78 68 78 82L78 140M78 82C80 68 100 68 100 82L100 140M100 104C110 88 136 90 136 110C136 128 120 140 98 152'],
  ['libra', 'Libra', 'air',
    'M52 142L148 142M52 120L78 120C66 110 64 94 70 82C78 64 122 64 130 82C136 94 134 110 122 120L148 120'],
  ['scorpio', 'Scorpio', 'water',
    'M48 70C52 64 58 66 58 74L58 138M58 82C60 68 80 68 80 82L80 138M80 82C82 68 102 68 102 82L102 124C102 136 110 141 122 137L144 128M131 118L145 127.5L137 141'],
  ['sagittarius', 'Sagittarius', 'fire',
    'M58 142L142 58M106 58L142 58L142 94M74 98L102 126'],
  ['capricorn', 'Capricorn', 'earth',
    'M50 70C57 62 64 65 68 78L84 132L100 76C104 62 120 62 122 78C124 96 112 120 116 134C120 148 138 150 144 137C150 124 139 112 127 116C117 119 113 128 116 134'],
  ['aquarius', 'Aquarius', 'air',
    'M50 88L67 72L84 88L100 72L117 88L134 72L150 88M50 122L67 106L84 122L100 106L117 122L134 106L150 122'],
  ['pisces', 'Pisces', 'water',
    'M64 54C88 76 88 124 64 146M136 54C112 76 112 124 136 146M70 100L130 100'],
].map(([slug, name, element, glyph]) => ({ slug, name, group: 'Zodiac', element, draw: coin(glyph, element) }));

// ── Celestial ───────────────────────────────────────────────────────────────

function sun(p) {
  for (let k = 0; k < 16; k++) {
    const a = -90 + k * 22.5;
    if (k % 2 === 0) {
      const tip = polar(100, 100, 86, a);
      const l = polar(100, 100, 40, a - 9), r = polar(100, 100, 40, a + 9);
      const mid = polar(100, 100, 40, a);
      p.hatch(poly([mid, tip, r]), lines({ angle: a, gap: 2.4 }), { w: 0.9 });
      p.line(poly([l, tip, r]), 2).line(poly([mid, tip], false), 1);
    } else {
      const tip = polar(100, 100, 68, a);
      p.line(poly([polar(100, 100, 40, a - 5), tip, polar(100, 100, 40, a + 5)]), 1.4);
      p.fill(circle(...polar(100, 100, 74, a), 1.8));
    }
  }
  p.hatch(circle(100, 100, 32), lines({ angle: 45, gap: 3 }), { mask: { cut: [circle(91, 91, 31)] } });
  p.hatch(circle(100, 100, 32), rings({ cx: 100, cy: 100, from: 6, to: 24, gap: 6 }), { w: 0.9 });
  p.line(circle(100, 100, 32), 3);
}

function crescentMoon(p) {
  const outer = [96, 104, 66], inner = [126, 88, 56];
  const shape = crescent(outer, inner);
  p.hatch(shape, lines({ angle: 60, gap: 3.2 }), { w: 1 });
  p.hatch(shape, lines({ angle: -30, gap: 3.2 }), { w: 1, mask: { keep: [circle(126, 88, 68)] } });
  p.line(shape, 3);
  p.fill(sparkle(150, 52, 8)).fill(sparkle(166, 116, 12)).fill(sparkle(178, 70, 4.5)).fill(sparkle(132, 150, 5));
}

function fullMoon(p) {
  p.hatch(circle(100, 100, 66), lines({ angle: 30, gap: 3 }), { mask: { cut: [circle(110, 91, 62)] } });
  for (const [cx, cy, r] of [[78, 70, 12], [126, 66, 8], [124, 112, 16], [80, 136, 8], [148, 100, 6], [104, 150, 5]]) {
    p.hatch(circle(cx, cy, r), lines({ angle: -45, gap: 2.2 }), { w: 0.9, mask: { cut: [circle(cx + r * 0.25, cy + r * 0.25, r)] } });
    p.line(circle(cx, cy, r), 1.6);
  }
  p.line(circle(100, 100, 66), 3);
}

function eclipse(p) {
  let corona = '';
  for (let i = 0; i < 72; i++) {
    const a = i * 5;
    const len = 8 + 16 * Math.abs(Math.sin(rad3(a))) + (i % 2 ? 0 : 7) + (i % 3 ? 0 : 4);
    corona += `M${polar(100, 100, 54, a).join(' ')}L${polar(100, 100, 54 + len, a).join(' ')}`;
  }
  p.line(corona.replace(/(\d+\.\d{3,})/g, (n) => (+n).toFixed(2)), 1.3, { mask: { cut: [circle(134, 66, 12)] } });
  p.hatch(circle(100, 100, 47), lines({ angle: 45, gap: 3 }));
  p.hatch(circle(100, 100, 47), lines({ angle: -45, gap: 3 }));
  p.line(circle(100, 100, 47), 3);
  p.line(circle(100, 100, 52), 1.2, { mask: { cut: [circle(134, 66, 12)] } });
  p.fill(sparkle(134, 66, 20, 0.14));
}
const rad3 = (deg) => (deg * 3 * Math.PI) / 180;

function saturn(p) {
  const band = ellipse(100, 100, 86, 24) + ellipse(100, 100, 62, 15);
  const backHalf = 'M55 100A45 45 0 0 1 145 100Z';
  const frontBand = 'M14 100A86 24 0 0 0 186 100L162 100A62 15 0 0 1 38 100Z';
  const hidePlanet = { cut: [frontBand], cutStroke: [[frontBand, 7]] };
  p.open('transform="rotate(-18 100 100)"');
  let grooves = '';
  for (let rx = 65; rx <= 84; rx += 3) grooves += ellipse(100, 100, rx, 15 + ((rx - 62) / 24) * 9);
  p.hatch(null, grooves, { w: 1, mask: { cut: [backHalf] } });
  p.line(ellipse(100, 100, 86, 24), 2.4, { mask: { cut: [backHalf] } });
  p.line(ellipse(100, 100, 62, 15), 1.5, { mask: { cut: [backHalf] } });
  p.hatch(circle(100, 100, 42), lines({ angle: 0, gap: 3 }), {
    mask: { keep: ['M40 80H160V88H40ZM40 104H160V116H40Z'], cut: [frontBand], cutStroke: [[frontBand, 7]] },
  });
  p.hatch(circle(100, 100, 42), lines({ angle: 60, gap: 2.8 }), {
    w: 0.9, mask: { cut: [circle(93, 93, 41), frontBand], cutStroke: [[frontBand, 7]] },
  });
  p.line(circle(100, 100, 42), 3, { mask: hidePlanet });
  p.close();
  p.fill(sparkle(40, 46, 7)).fill(sparkle(164, 160, 5)).fill(sparkle(166, 40, 4));
}

function comet(p) {
  const tail = 'M134 46C100 56 58 88 24 126C38 148 50 160 62 174C92 128 124 92 156 70Z';
  p.hatch(tail, lines({ angle: 138, gap: 3.2 }), { w: 1, mask: { cut: [circle(146, 58, 17)] } });
  p.line('M134 46C100 56 58 88 24 126', 2, { mask: { cut: [circle(146, 58, 17)] } });
  p.line('M156 70C124 92 92 128 62 174', 2, { mask: { cut: [circle(146, 58, 17)] } });
  p.line('M140 60C110 76 76 108 44 150', 1.4, { mask: { cut: [circle(146, 58, 17)] } });
  p.hatch(null, rings({ cx: 146, cy: 58, from: 17, to: 29, gap: 3 }), { w: 0.9, mask: { cut: [tail] } });
  p.line(circle(146, 58, 12), 3);
  p.hatch(circle(146, 58, 12), lines({ angle: 45, gap: 2.6 }), { w: 0.9, mask: { cut: [circle(142, 54, 11)] } });
  p.fill(sparkle(46, 46, 8)).fill(sparkle(176, 132, 7)).fill(sparkle(116, 164, 5));
}

function northStar(p) {
  const pts = [], valleys = [];
  for (let k = 0; k < 8; k++) {
    pts.push(polar(100, 100, k % 2 ? 46 : 86, -90 + k * 45));
    valleys.push(polar(100, 100, 15, -90 + k * 45 + 22.5));
  }
  const outline = poly(pts.flatMap((q, k) => [q, valleys[k]]));
  p.line(circle(100, 100, 58), 1.5, { mask: { cut: [outline], cutStroke: [[outline, 9]] } });
  p.line(circle(100, 100, 64), 1, { mask: { cut: [outline], cutStroke: [[outline, 9]] } });
  p.hatch(null, spokes({ r0: 58, r1: 64, count: 72 }), { w: 1, mask: { cut: [outline], cutStroke: [[outline, 9]] } });
  for (let k = 0; k < 8; k++) {
    p.hatch(poly([[100, 100], pts[k], valleys[k]]), lines({ angle: -90 + k * 45, gap: 2.4 }), { w: 0.9 });
    p.line(poly([[100, 100], pts[k]], false), 1.2);
  }
  p.line(outline, 2.4);
  p.fill(circle(100, 100, 3.5));
}

function constellation(p) {
  const stars = [[30, 66, 7], [56, 70, 8], [80, 84, 8], [100, 100, 9], [104, 134, 8], [146, 142, 9], [154, 106, 10]];
  const polaris = [158, 38, 13];
  const halos = [...stars, polaris].map(([x, y]) => circle(x, y, 9));
  p.line(circle(158, 38, 74), 1, { extra: ' stroke-dasharray="1 6"' });
  p.line(circle(158, 38, 128), 1, { extra: ' stroke-dasharray="1 6"' });
  p.line(poly(stars.slice(0, 4).map(([x, y]) => [x, y]).concat([[104, 134], [146, 142], [154, 106], [100, 100]]), false), 1.6, { mask: { cut: halos } });
  p.line('M154 106L158 38', 1.2, { mask: { cut: halos }, extra: ' stroke-dasharray="3 5"' });
  for (const [x, y, r] of stars) p.fill(sparkle(x, y, r));
  p.fill(sparkle(...polaris, 0.12)).line(circle(158, 38, 5), 1.2);
  for (const [x, y] of [[40, 128], [70, 160], [128, 64], [178, 88], [184, 170], [24, 30], [96, 30], [130, 178], [60, 112]]) p.fill(circle(x, y, 1.4));
}

function telescope(p) {
  p.line('M100 128L64 178M100 128L136 178M100 128L102 184', 3);
  p.line('M78 158L124 158', 1.4);
  p.line('M100 112L100 128', 4);
  p.fill(circle(100, 128, 5));
  p.open('transform="rotate(-28 100 100)"');
  const tube = 'M40 92L150 84L150 116L40 108Z';
  p.hatch(tube, lines({ angle: 0, gap: 2.8 }), { mask: { keep: ['M30 101L160 102L160 130L30 130Z'] } });
  p.line(tube, 3);
  p.hatch('M74 88L82 88L82 112L74 112Z', lines({ angle: 90, gap: 2.4 }), { w: 0.9, mask: { keep: [tube] } });
  p.line('M74 89.6L74 110.4M82 89L82 111', 1.6);
  p.hatch('M150 80H164V120H150Z', lines({ angle: 90, gap: 2.4 }), { w: 0.9 });
  p.line('M150 80H164V120H150Z', 3);
  p.line('M40 95H26V105H40', 3);
  p.line('M26 97H20V103H26', 2);
  p.line('M92 112L100 112L100 108', 3);
  p.close();
  p.fill(sparkle(48, 40, 9)).fill(sparkle(178, 30, 5)).fill(sparkle(30, 76, 4));
}

function astrolabe(p) {
  const c = [100, 108];
  p.line(circle(100, 21, 9), 2.6);
  p.line('M86 38C88 31 95 29 100 30C105 29 112 31 114 38', 3);
  p.line(circle(...c, 72), 3).line(circle(...c, 63), 1.4).line(circle(...c, 56), 1.2);
  p.hatch(null, spokes({ cx: c[0], cy: c[1], r0: 63, r1: 72, count: 24 }), { w: 1.4 });
  p.hatch(null, spokes({ cx: c[0], cy: c[1], r0: 56, r1: 63, count: 120 }), { w: 0.8 });
  p.hatch(circle(...c, 40), rings({ cx: 100, cy: 152, from: 8, to: 80, gap: 6 }), { w: 1 });
  p.line(circle(...c, 40), 1.4);
  p.line(circle(100, 100, 34), 2);
  const [ax, ay] = polar(...c, 66, -35), [bx, by] = polar(...c, 66, 145);
  p.line(`M${ax.toFixed(2)} ${ay.toFixed(2)}L${bx.toFixed(2)} ${by.toFixed(2)}`, 4.5);
  p.fill(circle(...c, 6)).line(circle(...c, 9), 1.2);
}

function armillary(p) {
  const c = [100, 88];
  p.line(circle(...c, 64), 2.6).line(circle(...c, 57), 1.4);
  p.hatch(null, spokes({ cx: c[0], cy: c[1], r0: 57, r1: 64, count: 72 }), { w: 0.9 });
  p.line(ellipse(...c, 64, 15), 2.2).line(ellipse(...c, 22, 64), 1.4);
  p.open('transform="rotate(-24 100 88)"');
  const band = ellipse(...c, 60, 24) + ellipse(...c, 60, 15);
  p.hatch(band, lines({ angle: 90, gap: 4.5, box: [30, 50, 170, 130] }), { w: 1, rule: 'evenodd' });
  p.line(ellipse(...c, 60, 24), 2).line(ellipse(...c, 60, 15), 1.4);
  p.line('M100 16L100 160', 1.6);
  p.close();
  p.hatch(circle(...c, 10), rings({ cx: 96, cy: 84, from: 3, to: 16, gap: 2.6 }), { w: 0.9 });
  p.line(circle(...c, 10), 2.4);
  p.line('M100 152L100 166', 4).fill(circle(100, 158, 4.5));
  const base = 'M68 184L132 184L121 166L79 166Z';
  p.hatch(base, lines({ angle: 90, gap: 3.4 }), { w: 1 });
  p.line(base, 2.6);
}

function crystalBall(p) {
  const c = [100, 86];
  p.hatch(circle(...c, 58), rings({ cx: 116, cy: 70, from: 50, to: 100, gap: 3 }), { w: 1 });
  p.line('M64 66C70 50 84 40 98 38', 3);
  p.line('M60 82C60 78 61 74 62 71', 3);
  p.line(circle(...c, 58), 3);
  p.fill(sparkle(94, 78, 13)).fill(sparkle(118, 102, 7)).fill(sparkle(116, 62, 4));
  const base = 'M72 150L128 150L144 178L56 178Z';
  p.hatch(base, lines({ angle: 90, gap: 3.6 }), { w: 1 });
  p.line(base, 3);
  p.line('M64 138C74 150 126 150 136 138', 3);
  p.line('M56 184L144 184', 3);
}

const celestial = [
  ['sun', 'Sun', sun],
  ['crescent-moon', 'Crescent moon', crescentMoon],
  ['full-moon', 'Full moon', fullMoon],
  ['eclipse', 'Eclipse', eclipse],
  ['saturn', 'Saturn', saturn],
  ['comet', 'Comet', comet],
  ['north-star', 'North star', northStar],
  ['constellation', 'Constellation', constellation],
  ['telescope', 'Telescope', telescope],
  ['astrolabe', 'Astrolabe', astrolabe],
  ['armillary-sphere', 'Armillary sphere', armillary],
  ['crystal-ball', 'Crystal ball', crystalBall],
].map(([slug, name, draw]) => ({ slug, name, group: 'Celestial', draw }));

export const icons = [...zodiac, ...celestial].map((icon) => {
  const p = new Plate();
  icon.draw(p);
  return { ...icon, defs: p.defs, body: p.body };
});
