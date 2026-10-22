// Renders the Dribbble shots for the Maison icon set.
//   NODE_PATH=$(npm root -g) node dribbble/build-shots.mjs
// Writes 1600 x 1200 PNGs (plus @2x) into dribbble/.

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { icons, groups } from '../src/icons.mjs';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const work = join(here, '.html');
mkdirSync(work, { recursive: true });

const fileName = (slug) => {
  const i = icons.findIndex((x) => x.slug === slug);
  if (i < 0) throw new Error(`unknown icon ${slug}`);
  return `${String(i + 1).padStart(2, '0')}-${slug}.svg`;
};
const img = (slug, style = '') => `<img style="${style}" src="file://${root}/gold/${fileName(slug)}" alt="">`;
// Mono files are inlined so they take the page's ink colour.
let n = 0;
const mono = (slug, style = '') =>
  readFileSync(join(root, 'mono', fileName(slug)), 'utf8')
    .replace(/<svg[^>]*>/, `<svg viewBox="0 0 200 200" style="${style}">`)
    .replace(/mai-/g, `m${n++}-`)
    .replace(/ id="(solid|rule|inline)"/g, '');

const polar = (cx, cy, r, deg) => [cx + r * Math.cos((deg * Math.PI) / 180), cy + r * Math.sin((deg * Math.PI) / 180)];
const f = (v) => v.toFixed(1);

// Sunburst: alternating wedges and hairlines from a centre point.
function sunburst(cx, cy, R, from, to, count, wedge = 0.05, line = 0.18) {
  let wedges = '', lines = '';
  const step = (to - from) / count;
  for (let i = 0; i < count; i++) {
    const a = from + i * step;
    const [x1, y1] = polar(cx, cy, R, a), [x2, y2] = polar(cx, cy, R, a + step / 2);
    if (i % 2 === 0) wedges += `M${cx} ${cy}L${f(x1)} ${f(y1)}L${f(x2)} ${f(y2)}Z`;
    lines += `M${cx} ${cy}L${f(x1)} ${f(y1)}`;
  }
  return `<path d="${wedges}" fill="url(#goldU)" opacity="${wedge}"/><path d="${lines}" stroke="url(#goldU)" stroke-width="1" opacity="${line}"/>`;
}

// An arch (rectangle with a semicircular top) as a path.
const arch = (x, y, w, h) => `M${x} ${y + h}V${y + w / 2}A${w / 2} ${w / 2} 0 0 1 ${x + w} ${y + w / 2}V${y + h}Z`;
const archNest = (x, y, w, h, gaps = [0, 12, 20], widths = [2.4, 1, 1]) =>
  gaps.map((g, i) => `<path d="${arch(x + g, y + g, w - 2 * g, h - 2 * g)}" fill="none" stroke="url(#goldU)" stroke-width="${widths[i]}"/>`).join('');

const diamondRule = (w, color = '#c9a14d') => `
  <div style="display:flex;align-items:center;justify-content:center;gap:14px">
    <span style="width:${w}px;height:1px;background:${color}"></span>
    <svg width="14" height="14" viewBox="-7 -7 14 14"><path d="M0 -7L7 0L0 7L-7 0Z" fill="${color}"/></svg>
    <span style="width:${w}px;height:1px;background:${color}"></span>
  </div>`;

const base = `
<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Italiana&family=Josefin+Sans:wght@300;400;600&family=Cormorant+Garamond:ital,wght@1,500&display=swap">
<style>
  :root { --emerald: #0d2a22; --lacquer: #0c0c0d; --oxblood: #4a1418; --ivory: #f2ece0; --ink: #141414; --gold: #d6aa4e;
          --foil: linear-gradient(135deg, #f7e9bd 0%, #d6aa4e 30%, #fbf0c9 48%, #b5852f 66%, #e9c879 100%);
          --display: "Italiana", serif; --sans: "Josefin Sans", sans-serif; }
  * { box-sizing: border-box; }
  html, body { margin: 0; }
  .shot { position: relative; width: 1600px; height: 1200px; overflow: hidden; color: #efe3c4; font-family: var(--sans); font-weight: 300; }
  .foil { background: var(--foil); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .caps { text-transform: uppercase; letter-spacing: .32em; }
  img, .abs { position: absolute; display: block; }
  svg.layer { position: absolute; inset: 0; overflow: visible; pointer-events: none; }
</style>
<svg width="0" height="0" style="position:absolute"><defs>
  <linearGradient id="goldU" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1600" y2="1200">
    <stop offset="0" stop-color="#f7e9bd"/><stop offset=".3" stop-color="#d6aa4e"/><stop offset=".48" stop-color="#fbf0c9"/>
    <stop offset=".66" stop-color="#b5852f"/><stop offset="1" stop-color="#e9c879"/>
  </linearGradient>
</defs></svg>`;

// Stepped Art Deco frame around the whole shot.
const frame = `
  <svg class="layer" width="1600" height="1200" fill="none" stroke="url(#goldU)">
    <path d="M60 28H1540L1572 60V1140L1540 1172H60L28 1140V60Z" stroke-width="2"/>
    <path d="M68 40H1532L1560 68V1132L1532 1160H68L40 1132V68Z" stroke-width=".8" opacity=".7"/>
  </svg>`;

// ── 01 Cover: the Deco poster ───────────────────────────────────────────────
function cover() {
  const side = (slugs, cx) =>
    slugs.map((s, i) => img(s, `left:${cx - 90}px;top:${210 + i * 300}px;width:180px;height:180px`)).join('') +
    [0, 1].map((i) => `<svg class="abs" style="left:${cx - 8}px;top:${428 + i * 300}px" width="16" height="44" viewBox="0 0 16 44"><path d="M8 0L16 22L8 44L0 22Z" fill="url(#goldU)" opacity=".85"/></svg>`).join('');
  const corner = (x, y, from) => `<svg class="layer" width="1600" height="1200">${sunburst(x, y, 230, from, from + 90, 18, 0.07, 0.35)}</svg>`;
  return `${base}
<div class="shot" style="background:radial-gradient(ellipse at 50% 100%, #15493a 0%, #0c281f 45%, #06140f 100%)">
  <svg class="layer" width="1600" height="1200">${sunburst(800, 1240, 1500, 180, 360, 64, 0.045, 0.16)}</svg>
  ${corner(40, 40, 0)}${corner(1560, 40, 90)}${corner(1560, 1160, 180)}${corner(40, 1160, 270)}
  ${frame}
  <svg class="layer" width="1600" height="1200">
    <path d="${arch(520, 120, 560, 960)}" fill="#071a14"/>
    ${archNest(520, 120, 560, 960, [0, 14, 24], [3, 1.2, 1])}
    <clipPath id="inArch"><path d="${arch(544, 144, 512, 912)}"/></clipPath>
    <g clip-path="url(#inArch)">${sunburst(800, 470, 420, 180, 360, 36, 0.06, 0.2)}</g>
    <path d="M700 1056H900L880 1036H720Z M740 1030H860L848 1018H752Z" fill="url(#goldU)"/>
  </svg>
  ${img('cloche', 'left:605px;top:250px;width:390px;height:390px')}
  <div class="abs" style="left:520px;width:560px;top:690px;text-align:center">
    <div class="foil" style="font:400 96px/1 var(--display);letter-spacing:.14em;padding-left:.14em">MAISON</div>
    <div style="margin:34px 0 28px">${diamondRule(90)}</div>
    <div class="caps" style="font-size:19px;color:#e6d3a3">24 Art Deco dining icons</div>
    <div class="caps" style="font-size:14px;color:#8fa597;margin-top:14px;letter-spacing:.4em">Gold &amp; Mono SVG</div>
  </div>
  ${side(['champagne-coupe', 'candelabra', 'oyster'], 270)}
  ${side(['martini', 'award', 'caviar'], 1330)}
</div>`;
}

// ── 02 Le Menu: the full set as four courses ────────────────────────────────
function menu() {
  const roman = ['I', 'II', 'III', 'IV'];
  const cols = groups
    .map((g, ci) => {
      const list = icons.filter((i) => i.group === g);
      return `<div class="abs" style="left:${92 + ci * 360}px;top:300px;width:336px">
        <div style="text-align:center">
          <div class="caps" style="font-size:13px;color:#8d7a52">Course ${roman[ci]}</div>
          <div class="foil" style="font:400 40px/1.2 var(--display);letter-spacing:.16em;padding-left:.16em">${g.toUpperCase()}</div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;row-gap:40px;margin-top:34px">
          ${list.map((i) => `<div style="display:grid;justify-items:center;gap:8px">${img(i.slug, 'position:static;width:160px;height:160px')}
            <span class="caps" style="font-size:12px;letter-spacing:.22em;color:#e3d5b0">${i.name}</span></div>`).join('')}
        </div>
      </div>`;
    })
    .join('');
  const dividers = [1, 2, 3].map((i) => `<path d="M${72 + i * 360} 320V1110M${78 + i * 360} 320V1110" stroke-width=".8"/>`).join('');
  return `${base}
<div class="shot" style="background:radial-gradient(ellipse at 50% 0%, #1b1b1d, #0c0c0d 60%, #060606)">
  ${frame}
  <svg class="layer" width="1600" height="1200">${sunburst(800, 112, 64, 180, 360, 14, 0.18, 0.6)}</svg>
  <div class="abs" style="left:0;right:0;top:132px;text-align:center">
    <div class="foil" style="font:400 76px/1 var(--display);letter-spacing:.3em;padding-left:.3em">LE MENU</div>
    <div class="caps" style="font-size:14px;color:#9a9286;margin-top:16px;letter-spacing:.42em">Maison · twenty-four icons in four courses</div>
  </div>
  <svg class="layer" width="1600" height="1200" fill="none" stroke="url(#goldU)" opacity=".7">${dividers}</svg>
  ${cols}
</div>`;
}

// ── 03 Anatomy of the inline ─────────────────────────────────────────────────
function anatomy() {
  const o = { x: 70, y: 250, s: 3.9 };
  const at = (u, v) => [o.x + u * o.s, o.y + v * o.s];
  const callouts = [
    { p: at(...polar(100, 104, 62, -58)), y: 330, t: 'Open core', d: 'A true mask, not a painted line, so the core stays transparent on any background.' },
    { p: at(...polar(100, 104, 65.5, -24)), y: 510, t: 'Inline rail', d: 'Every outline is a 9 px stroke with its centre cut away, the signature Deco double line.' },
    { p: at(...polar(100, 104, 38, -31.5)), y: 690, t: 'Fine rule', d: '2 px rays and details for the sunbursts and fans.' },
    { p: at(108, 134), y: 870, t: 'Solid gold', d: 'Filled accents: pearls, flames, gems and stepped bases.' },
  ];
  const lines = callouts
    .map((c) => `<circle cx="${f(c.p[0])}" cy="${f(c.p[1])}" r="7" fill="none" stroke="#f7e9bd" stroke-width="2"/>
      <circle cx="${f(c.p[0])}" cy="${f(c.p[1])}" r="2.5" fill="#f7e9bd"/>
      <path d="M${f(c.p[0] + 7)} ${f(c.p[1])}L${f(Math.max(c.p[0] + 40, 860))} ${c.y}H930" stroke="url(#goldU)" stroke-width="1.2" fill="none"/>`)
    .join('');
  const texts = callouts
    .map((c) => `<div class="abs" style="left:950px;top:${c.y - 16}px;width:540px">
      <div class="caps foil" style="font-size:20px;font-weight:600;letter-spacing:.26em">${c.t}</div>
      <div style="font-size:19px;color:#b9c6bc;margin-top:6px;line-height:1.45">${c.d}</div></div>`)
    .join('');
  return `${base}
<div class="shot" style="background:radial-gradient(ellipse at 30% 50%, #12392e, #0b241d 55%, #06140f)">
  ${frame}
  <div class="abs" style="left:110px;top:96px">
    <div class="foil" style="font:400 62px/1 var(--display);letter-spacing:.16em">ANATOMY OF THE INLINE</div>
    <div class="caps" style="font-size:14px;color:#8fa597;margin-top:16px;letter-spacing:.36em">Oyster · shown at 3.9×</div>
  </div>
  ${img('oyster', `left:${o.x}px;top:${o.y}px;width:${200 * o.s}px;height:${200 * o.s}px`)}
  <svg class="layer" width="1600" height="1200">${lines}</svg>
  ${texts}
  <div class="abs" style="left:950px;top:1000px;display:flex;align-items:center;gap:22px">
    <svg width="180" height="72" viewBox="0 0 180 72">
      <rect x="0" y="6" width="180" height="18" fill="url(#goldU)"/><rect x="0" y="48" width="180" height="18" fill="url(#goldU)"/>
      <path d="M0 27V45" stroke="#8fa597" stroke-dasharray="2 3"/>
    </svg>
    <div class="caps" style="font-size:15px;color:#e6d3a3;line-height:1.9">3 px rail<br>3 px core<br>3 px rail</div>
  </div>
</div>`;
}

// ── 04 Four lacquers: gold and mono in Deco arches ───────────────────────────
function lacquers() {
  const panels = [
    ['Emerald', '#0d2a22', 'gold', ['champagne-coupe', 'oyster', 'candelabra']],
    ['Black lacquer', '#0c0c0d', 'gold', ['decanter', 'cloche', 'grapes']],
    ['Oxblood', '#4a1418', 'gold', ['wine-glass', 'fruit-tart', 'award']],
    ['Ivory', '#f2ece0', 'mono', ['martini', 'fish', 'toque']],
  ];
  const W = 320, G = 44, X0 = (1600 - (4 * W + 3 * G)) / 2, Y = 210, H = 880;
  const shapes = panels.map(([, bg], i) => `<path d="${arch(X0 + i * (W + G), Y, W, H)}" fill="${bg}"/>${archNest(X0 + i * (W + G), Y, W, H, [0, 10], [2, .8])}`).join('');
  const content = panels
    .map(([name, bg, v, slugs], i) => {
      const x = X0 + i * (W + G);
      const ink = v === 'mono' ? '#141414' : null;
      const icon = (s, j) => (v === 'mono'
        ? mono(s, `position:absolute;left:${x + 70}px;top:${Y + 120 + j * 222}px;width:176px;height:176px;color:${ink}`)
        : img(s, `left:${x + 70}px;top:${Y + 120 + j * 222}px;width:176px;height:176px`));
      return slugs.map(icon).join('') +
        `<div class="abs" style="left:${x}px;width:${W}px;top:${Y + H - 108}px;text-align:center">
          <div style="font:400 26px var(--display);letter-spacing:.14em;color:${ink || '#efe3c4'}">${name.toUpperCase()}</div>
          <div class="caps" style="font-size:12px;margin-top:6px;color:${ink ? '#6e675c' : '#a49a80'}">${v === 'mono' ? 'Mono · any colour' : 'Gold'}</div>
        </div>`;
    })
    .join('');
  return `${base}
<div class="shot" style="background:radial-gradient(ellipse at 50% 30%, #2a241b, #17140f 60%, #0d0b08)">
  <div class="abs" style="left:0;right:0;top:78px;text-align:center">
    <div class="foil" style="font:400 60px/1 var(--display);letter-spacing:.24em;padding-left:.24em">GOLD &amp; MONO</div>
    <div class="caps" style="font-size:14px;color:#a49a80;margin-top:16px;letter-spacing:.4em">One set for every lacquer</div>
  </div>
  <svg class="layer" width="1600" height="1200">${shapes}</svg>
  ${content}
</div>`;
}

// ── 05 In use: menu, matchbox, reservations ──────────────────────────────────
function inUse() {
  const dishes = [
    ['oyster', 'Les Huîtres', 'Gillardeau No.2, mignonette', '38'],
    ['caviar', 'Le Caviar', 'Osciètre, blinis tièdes', '95'],
    ['fish', 'Le Poisson', 'Turbot, beurre blanc, caviar', '64'],
    ['cheese', 'Les Fromages', 'Comté 36 mois, figues', '22'],
    ['fruit-tart', 'La Tarte', 'Fruits rouges, crème vanille', '18'],
    ['champagne-coupe', 'Le Champagne', 'Blanc de blancs, la coupe', '26'],
  ];
  return `${base}
<div class="shot" style="background:radial-gradient(ellipse at 45% 35%, #5a1b20, #3a0f13 60%, #220709)">
  <div class="abs" style="left:120px;top:110px;width:470px;height:950px;background:var(--ivory);transform:rotate(-4deg);box-shadow:0 40px 80px rgba(0,0,0,.5);color:var(--ink);padding:70px 54px">
    <div style="position:absolute;inset:16px;border:2px solid #b5852f"></div>
    <div style="position:absolute;inset:24px;border:1px solid #b5852f"></div>
    ${mono('cloche', 'display:block;width:110px;height:110px;margin:0 auto;color:#141414')}
    <div style="text-align:center;font:400 54px/1 var(--display);letter-spacing:.28em;padding-left:.28em;margin-top:6px">MAISON</div>
    <div class="caps" style="text-align:center;font-size:11px;color:#7b7262;margin-top:10px">Menu du soir</div>
    <div style="margin:22px 0 10px">${diamondRule(70, '#b5852f')}</div>
    ${dishes.map(([s, t, d, p]) => `<div style="display:grid;grid-template-columns:70px 1fr auto;align-items:center;gap:14px;margin-top:26px">
      ${mono(s, 'width:66px;height:66px;color:#141414')}
      <div><div style="font:400 27px var(--display);letter-spacing:.06em">${t}</div><div style="font-size:14px;color:#6e675c">${d}</div></div>
      <div style="font:400 24px var(--display)">${p}</div></div>`).join('')}
  </div>
  <div class="abs" style="left:640px;top:610px;width:330px;height:440px;background:linear-gradient(160deg,#123a2f,#0a2219);transform:rotate(7deg);box-shadow:0 40px 70px rgba(0,0,0,.5);border-radius:6px">
    <div style="position:absolute;inset:14px;border:1.5px solid #c9a14d"></div>
    <div style="position:absolute;left:0;right:0;top:0;height:30px;background:repeating-linear-gradient(90deg,#5b3d1f 0 3px,#3e2a14 3px 6px);border-radius:6px 6px 0 0;opacity:.85"></div>
    ${img('champagne-coupe', 'left:65px;top:70px;width:200px;height:200px')}
    <div class="foil" style="position:absolute;left:0;right:0;top:290px;text-align:center;font:400 40px var(--display);letter-spacing:.3em;padding-left:.3em">MAISON</div>
    <div class="caps" style="position:absolute;left:0;right:0;top:350px;text-align:center;font-size:11px;color:#a5b8ac">Paris · Est. 1925</div>
  </div>
  <div class="abs" style="left:1080px;top:96px;width:400px;height:850px;border-radius:56px;background:#0a0a0a;padding:13px;box-shadow:0 50px 90px rgba(0,0,0,.55);transform:rotate(4deg)">
    <div style="position:relative;width:100%;height:100%;border-radius:44px;overflow:hidden;background:linear-gradient(180deg,#123a2f,#081c15)">
      <svg style="position:absolute;inset:0" width="374" height="824">${sunburst(187, 330, 420, 180, 360, 24, 0.06, 0.22)}</svg>
      <div class="caps" style="position:absolute;left:0;right:0;top:60px;text-align:center;font-size:12px;color:#8fa597">Reservations</div>
      <div class="foil" style="position:absolute;left:0;right:0;top:84px;text-align:center;font:400 40px var(--display);letter-spacing:.24em;padding-left:.24em">MAISON</div>
      ${img('candelabra', 'left:107px;top:150px;width:160px;height:160px')}
      <div style="position:absolute;left:28px;right:28px;top:340px">
        <div class="caps" style="font-size:11px;color:#8fa597">Friday 23 October</div>
        <div style="display:flex;gap:8px;margin-top:12px">${['19:00', '20:30', '21:45'].map((t, i) => `<div style="flex:1;text-align:center;padding:12px 0;border:1px solid ${i === 1 ? '#d6aa4e' : '#2a5244'};color:${i === 1 ? '#f7e9bd' : '#a5b8ac'};font-size:16px">${t}</div>`).join('')}</div>
        <div style="display:grid;grid-template-columns:52px 1fr;gap:14px;align-items:center;margin-top:26px;padding:16px;border:1px solid #2a5244">
          ${img('reserved', 'position:static;width:52px;height:52px')}
          <div><div style="font:400 22px var(--display);letter-spacing:.06em">Table for two</div><div style="font-size:13px;color:#8fa597">Salon Doré · window</div></div>
        </div>
        <div style="display:grid;grid-template-columns:52px 1fr;gap:14px;align-items:center;margin-top:12px;padding:16px;border:1px solid #2a5244">
          ${img('champagne-coupe', 'position:static;width:52px;height:52px')}
          <div><div style="font:400 22px var(--display);letter-spacing:.06em">Champagne</div><div style="font-size:13px;color:#8fa597">On arrival · blanc de blancs</div></div>
        </div>
        <div class="caps" style="margin-top:28px;text-align:center;padding:18px 0;background:var(--foil);color:#0b241d;font-size:14px;font-weight:600">Confirm</div>
      </div>
    </div>
  </div>
</div>`;
}

const shots = [
  ['01-cover', cover()],
  ['02-le-menu', menu()],
  ['03-anatomy', anatomy()],
  ['04-gold-and-mono', lacquers()],
  ['05-in-use', inUse()],
];

const browser = await chromium.launch();
for (const scale of [1, 2]) {
  const page = await browser.newPage({ viewport: { width: 1600, height: 1200 }, deviceScaleFactor: scale });
  for (const [name, html] of shots) {
    const path = join(work, `${name}.html`);
    writeFileSync(path, html);
    await page.goto(`file://${path}`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(500);
    await page.screenshot({ path: join(here, `${name}${scale === 2 ? '@2x' : ''}.png`), clip: { x: 0, y: 0, width: 1600, height: 1200 } });
  }
  await page.close();
}
await browser.close();
console.log(`Rendered ${shots.length} shots at 1x and 2x`);
