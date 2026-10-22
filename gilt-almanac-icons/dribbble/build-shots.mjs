// Renders the Dribbble shots for the Gilt Almanac icon set.
//   NODE_PATH=$(npm root -g) node dribbble/build-shots.mjs
// Writes 1600 x 1200 PNGs (plus @2x) into dribbble/.

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { icons } from '../src/icons.mjs';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const work = join(here, '.html');
mkdirSync(work, { recursive: true });

const fileName = (slug) => {
  const i = icons.findIndex((x) => x.slug === slug);
  return `${String(i + 1).padStart(2, '0')}-${slug}.svg`;
};
const img = (slug, style = '', version = 'gilt') =>
  `<img style="${style}" src="file://${root}/${version}/${fileName(slug)}" alt="">`;
// Ink files are inlined so they can take the page's ink colour.
let inlineCount = 0;
const inkSvg = (slug, style = '') =>
  readFileSync(join(root, 'ink', fileName(slug)), 'utf8')
    .replace(/<svg[^>]*>/, `<svg viewBox="0 0 200 200" style="${style}">`)
    .replace(/alm-/g, `i${inlineCount++}-`);

const ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'];
const zodiac = icons.filter((i) => i.group === 'Zodiac');
const celestial = icons.filter((i) => i.group === 'Celestial');

// Deterministic star field.
function stars(w, h, n, seed = 7, color = '#e9d9a8') {
  let s = seed;
  const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  let out = '';
  for (let i = 0; i < n; i++) {
    const r = rnd() < 0.08 ? 1.6 : 0.5 + rnd() * 0.7;
    out += `<circle cx="${(rnd() * w).toFixed(1)}" cy="${(rnd() * h).toFixed(1)}" r="${r.toFixed(2)}" opacity="${(0.25 + rnd() * 0.6).toFixed(2)}"/>`;
  }
  return `<svg class="stars" width="${w}" height="${h}" fill="${color}">${out}</svg>`;
}

const sparkle = (x, y, r, k = 0.18) =>
  `M${x} ${y - r}Q${x + r * k} ${y - r * k} ${x + r} ${y}Q${x + r * k} ${y + r * k} ${x} ${y + r}Q${x - r * k} ${y + r * k} ${x - r} ${y}Q${x - r * k} ${y - r * k} ${x} ${y - r}Z`;

const base = `
<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap">
<style>
  :root { --night: #0f1526; --deep: #0a0f1c; --paper: #f3ede1; --ink: #1d1b2e; --gold: #e2b85c; --muted: #8f8a9e;
          --foil: linear-gradient(135deg, #fbe8b4 0%, #e2b85c 28%, #a37632 50%, #f1d58b 72%, #b98b3d 100%);
          --caps: "Cinzel", serif; --serif: "Cormorant Garamond", serif; }
  * { box-sizing: border-box; }
  html, body { margin: 0; }
  .shot { position: relative; width: 1600px; height: 1200px; overflow: hidden; color: #ece4d0; font-family: var(--serif);
          background: radial-gradient(ellipse at 50% 45%, #18203a 0%, var(--night) 55%, var(--deep) 100%); }
  .stars { position: absolute; inset: 0; }
  .foil { background: var(--foil); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .caps { font-family: var(--caps); letter-spacing: .32em; text-transform: uppercase; }
  img, .abs { position: absolute; display: block; }
  svg.layer { position: absolute; inset: 0; overflow: visible; }
</style>
<svg width="0" height="0" style="position:absolute"><defs>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fbe8b4"/><stop offset=".28" stop-color="#e2b85c"/><stop offset=".5" stop-color="#a37632"/>
    <stop offset=".72" stop-color="#f1d58b"/><stop offset="1" stop-color="#b98b3d"/>
  </linearGradient>
  <linearGradient id="goldU" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1600" y2="1200">
    <stop offset="0" stop-color="#fbe8b4"/><stop offset=".28" stop-color="#e2b85c"/><stop offset=".5" stop-color="#a37632"/>
    <stop offset=".72" stop-color="#f1d58b"/><stop offset="1" stop-color="#b98b3d"/>
  </linearGradient>
</defs></svg>`;

// Corner labels shared by the plates.
const corners = (tl, tr, bl, br, color = '#b99a5c') => `
  <div class="abs caps" style="left:48px;top:40px;font-size:15px;color:${color}">${tl}</div>
  <div class="abs caps" style="right:48px;top:40px;font-size:15px;color:${color};text-align:right">${tr}</div>
  <div class="abs caps" style="left:48px;bottom:40px;font-size:15px;color:${color}">${bl}</div>
  <div class="abs caps" style="right:48px;bottom:40px;font-size:15px;color:${color};text-align:right">${br}</div>
  <svg class="layer" width="1600" height="1200"><rect x="24" y="24" width="1552" height="1152" fill="none" stroke="url(#goldU)" stroke-width="1.5" opacity=".7"/>
  <rect x="30" y="30" width="1540" height="1140" fill="none" stroke="url(#goldU)" stroke-width=".8" opacity=".45"/></svg>`;

// ── 01 Cover: the zodiac wheel ───────────────────────────────────────────────
function cover() {
  const cx = 800, cy = 600;
  const coins = zodiac
    .map((z, i) => {
      const a = ((-90 + i * 30) * Math.PI) / 180;
      const x = cx + 412 * Math.cos(a), y = cy + 412 * Math.sin(a);
      return img(z.slug, `left:${x - 78}px;top:${y - 78}px;width:156px;height:156px`);
    })
    .join('');
  let ticks = '';
  for (let i = 0; i < 360; i += 2) {
    const a = (i * Math.PI) / 180, r0 = i % 30 === 0 ? 290 : i % 10 === 0 ? 298 : 304;
    ticks += `M${(cx + r0 * Math.cos(a)).toFixed(1)} ${(cy + r0 * Math.sin(a)).toFixed(1)}L${(cx + 312 * Math.cos(a)).toFixed(1)} ${(cy + 312 * Math.sin(a)).toFixed(1)}`;
  }
  let spokes = '';
  for (let i = 0; i < 12; i++) {
    const a = ((-75 + i * 30) * Math.PI) / 180;
    spokes += `M${(cx + 320 * Math.cos(a)).toFixed(1)} ${(cy + 320 * Math.sin(a)).toFixed(1)}L${(cx + 492 * Math.cos(a)).toFixed(1)} ${(cy + 492 * Math.sin(a)).toFixed(1)}`;
  }
  const arc = (r) => `M${cx - r} ${cy}A${r} ${r} 0 1 1 ${cx + r} ${cy}A${r} ${r} 0 1 1 ${cx - r} ${cy}`;
  const phrase = 'Twenty-four engraved icons ✦ Zodiac &amp; Celestial ✦ Gilt &amp; Ink SVG ✦ ';
  return `${base}
<div class="shot">
  ${stars(1600, 1200, 420)}
  <svg class="layer" width="1600" height="1200" fill="none" stroke="url(#goldU)">
    <defs><path id="ring" d="${arc(506)}"/></defs>
    <circle cx="${cx}" cy="${cy}" r="540" stroke-width="2.4"/>
    <circle cx="${cx}" cy="${cy}" r="532" stroke-width="1"/>
    <circle cx="${cx}" cy="${cy}" r="494" stroke-width="1"/>
    <circle cx="${cx}" cy="${cy}" r="412" stroke-width="1" stroke-dasharray="1 7" stroke-linecap="round"/>
    <path d="${spokes}" stroke-width=".8" opacity=".6"/>
    <circle cx="${cx}" cy="${cy}" r="320" stroke-width="1.6"/>
    <path d="${ticks}" stroke-width="1"/>
    <circle cx="${cx}" cy="${cy}" r="282" stroke-width="1"/>
    <text fill="url(#goldU)" stroke="none" font-family="Cinzel" font-size="19" letter-spacing="7">
      <textPath href="#ring" textLength="${Math.round(2 * Math.PI * 506) - 30}" lengthAdjust="spacing">${phrase.toUpperCase()}${phrase.toUpperCase()}</textPath>
    </text>
    <path d="${sparkle(cx, cy - 214, 22, 0.14)}" fill="url(#goldU)" stroke="none"/>
  </svg>
  ${coins}
  <div class="abs" style="left:${cx - 280}px;top:${cy - 168}px;width:560px;text-align:center">
    <div class="caps foil" style="font-size:22px;letter-spacing:.5em;padding-left:.5em">Plate I</div>
    <div class="foil" style="font:500 132px/1 var(--caps);letter-spacing:.04em;margin-top:22px">GILT</div>
    <div class="foil" style="font:italic 400 104px/1 var(--serif);margin-top:-8px">Almanac</div>
    <div style="display:flex;align-items:center;justify-content:center;gap:16px;margin-top:22px;color:#c9ad6e">
      <span style="width:60px;height:1px;background:#b99a5c"></span>
      <span class="caps" style="font-size:16px">24 engraved icons</span>
      <span style="width:60px;height:1px;background:#b99a5c"></span>
    </div>
  </div>
  ${img('telescope', 'left:70px;bottom:70px;width:190px;height:190px;opacity:.95')}
  ${img('crescent-moon', 'right:76px;top:80px;width:170px;height:170px')}
  ${img('comet', 'left:80px;top:90px;width:150px;height:150px;opacity:.9')}
  ${img('saturn', 'right:70px;bottom:80px;width:200px;height:200px')}
</div>`;
}

// ── 02 Catalogue of the heavens ─────────────────────────────────────────────
function catalogue() {
  const panel = (list, x, title) => `
    <div class="abs" style="left:${x}px;top:196px;width:700px">
      <div style="display:flex;align-items:baseline;gap:16px;border-bottom:1px solid #3b3a4a;padding-bottom:12px">
        <span class="caps foil" style="font-size:22px">${title}</span>
        <span style="font:italic 20px var(--serif);color:var(--muted)">twelve plates</span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);row-gap:46px;margin-top:30px">
        ${list
          .map(
            (icon, i) => `<div style="display:grid;justify-items:center;gap:6px">
              <span class="caps" style="font-size:13px;color:#8d7a52">${ROMAN[i]}</span>
              ${img(icon.slug, 'position:static;width:168px;height:168px')}
              <span style="font:italic 500 23px var(--serif);color:#e8dcc0">${icon.name}</span>
            </div>`,
          )
          .join('')}
      </div>
    </div>`;
  return `${base}
<div class="shot">
  ${stars(1600, 1200, 260, 19)}
  ${corners('Gilt Almanac', 'Plate II', 'Zodiac · XII', 'Celestial · XII')}
  <div class="abs" style="left:0;right:0;top:78px;text-align:center">
    <div class="caps foil" style="font-size:44px;letter-spacing:.24em;padding-left:.24em">Catalogue of the Heavens</div>
    <div style="font:italic 22px var(--serif);color:var(--muted);margin-top:6px">Twenty-four icons, engraved on a 200-point grid</div>
  </div>
  ${panel(zodiac, 70, 'Zodiac')}
  <svg class="layer" width="1600" height="1200"><path d="M800 220V1110" stroke="url(#goldU)" stroke-width="1" opacity=".55"/>
    <path d="${sparkle(800, 660, 14, 0.14)}" fill="url(#goldU)"/><circle cx="800" cy="660" r="22" fill="none" stroke="url(#goldU)" stroke-width="1"/></svg>
  ${panel(celestial, 830, 'Celestial')}
</div>`;
}

// ── 03 The engraver's loupe ─────────────────────────────────────────────────
function loupe() {
  const coin = { x: 96, y: 300, s: 660 };
  const zoom = 1.9, focus = [138, 136], R = 230, L = [1150, 520];
  const k = (coin.s / 200) * zoom;
  const mark = [coin.x + (focus[0] * coin.s) / 200, coin.y + (focus[1] * coin.s) / 200];
  const mr = (R / k) * (coin.s / 200);
  // Outer tangents between the marker circle and the lens.
  const ang = Math.atan2(L[1] - mark[1], L[0] - mark[0]);
  const d = Math.hypot(L[0] - mark[0], L[1] - mark[1]);
  const t = Math.acos((R - mr) / d);
  const tan = (sign) => {
    const a = ang + Math.PI + sign * (Math.PI - t);
    return `M${(mark[0] + mr * Math.cos(a)).toFixed(1)} ${(mark[1] + mr * Math.sin(a)).toFixed(1)}L${(L[0] + R * Math.cos(a)).toFixed(1)} ${(L[1] + R * Math.sin(a)).toFixed(1)}`;
  };
  const element = (label, angle, signs) => {
    let l = '';
    for (let i = -40; i <= 40; i += 6) l += `M${-40} ${i}L40 ${i}`;
    return `<div style="display:grid;grid-template-columns:62px 1fr;gap:16px;align-items:center">
      <svg viewBox="-32 -32 64 64" width="62" height="62"><defs><clipPath id="c${angle}"><circle r="26"/></clipPath></defs>
        <g clip-path="url(#c${angle})"><path d="${l}" stroke="url(#gold)" stroke-width="1.6" transform="rotate(${angle})"/></g>
        <circle r="28" fill="none" stroke="url(#gold)" stroke-width="2"/></svg>
      <div><div class="caps foil" style="font-size:16px">${label}</div><div style="font:italic 19px var(--serif);color:var(--muted)">${signs}</div></div>
    </div>`;
  };
  return `${base}
<div class="shot">
  ${stars(1600, 1200, 200, 31)}
  ${corners('Gilt Almanac', 'Plate III', 'Leo · V', 'Detail at 2×')}
  <div class="abs" style="left:96px;top:96px">
    <div class="caps foil" style="font-size:46px;letter-spacing:.2em">Every line engraved</div>
    <div style="font:italic 24px var(--serif);color:var(--muted);margin-top:4px;max-width:620px">Shading is built from real vector hatching, not textures, so it stays crisp at any size.</div>
  </div>
  ${img('leo', `left:${coin.x}px;top:${coin.y}px;width:${coin.s}px;height:${coin.s}px`)}
  <svg class="layer" width="1600" height="1200" fill="none" stroke="url(#goldU)">
    <circle cx="${mark[0].toFixed(1)}" cy="${mark[1].toFixed(1)}" r="${mr.toFixed(1)}" stroke-width="2"/>
    <path d="${tan(1)}${tan(-1)}" stroke-width="1" opacity=".7"/>
  </svg>
  <div class="abs" style="left:${L[0] - R}px;top:${L[1] - R}px;width:${2 * R}px;height:${2 * R}px;border-radius:50%;overflow:hidden;background:var(--night);box-shadow:0 30px 80px rgba(0,0,0,.55)">
    ${img('leo', `left:${R - focus[0] * k}px;top:${R - focus[1] * k}px;width:${200 * k}px;height:${200 * k}px`)}
  </div>
  <svg class="layer" width="1600" height="1200" fill="none" stroke="url(#goldU)">
    <circle cx="${L[0]}" cy="${L[1]}" r="${R + 2}" stroke-width="5"/>
    <circle cx="${L[0]}" cy="${L[1]}" r="${R + 14}" stroke-width="1.2"/>
  </svg>
  <div class="abs" style="left:880px;top:808px;width:620px;display:grid;grid-template-columns:1fr 1fr;gap:26px 34px">
    <div><div class="caps foil" style="font-size:16px">Hatching</div><div style="font:italic 20px var(--serif);color:#d9ccb0">0.9 to 1.2 px engraving lines, clipped to each form</div></div>
    <div><div class="caps foil" style="font-size:16px">Knockout</div><div style="font:italic 20px var(--serif);color:#d9ccb0">A clean halo keeps every glyph legible</div></div>
    ${element('Fire', 45, 'Aries · Leo · Sagittarius')}
    ${element('Earth', 0, 'Taurus · Virgo · Capricorn')}
    ${element('Air', 135, 'Gemini · Libra · Aquarius')}
    ${element('Water', 90, 'Cancer · Scorpio · Pisces')}
  </div>
</div>`;
}

// ── 04 Gilt | Ink, split on a diagonal ──────────────────────────────────────
function split() {
  const picks = ['sun', 'aries', 'crescent-moon', 'north-star', 'scorpio', 'saturn', 'astrolabe', 'libra', 'eclipse', 'pisces', 'crystal-ball', 'telescope'];
  const size = 250;
  const pos = (i) => [240 + (i % 4) * 290, 175 + Math.floor(i / 4) * 300];
  const gilt = picks.map((s, i) => img(s, `left:${pos(i)[0]}px;top:${pos(i)[1]}px;width:${size}px;height:${size}px`)).join('');
  const ink = picks.map((s, i) => inkSvg(s, `position:absolute;left:${pos(i)[0]}px;top:${pos(i)[1]}px;width:${size}px;height:${size}px;color:var(--ink)`)).join('');
  const cut = [[1180, 0], [620, 1200]];
  return `${base}
<div class="shot" style="background:var(--paper)">
  <div class="abs" style="inset:0;clip-path:polygon(${cut[0][0]}px 0,1600px 0,1600px 1200px,${cut[1][0]}px 1200px)">
    <div class="abs" style="inset:0;background:var(--paper)"></div>
    ${ink}
    <div class="abs" style="right:70px;bottom:60px;text-align:right;color:var(--ink)">
      <div class="caps" style="font-size:40px;letter-spacing:.24em">Ink</div>
      <div style="font:italic 24px var(--serif);color:#5d576a">One flat colour. Any colour.<br>Ready for foil stamping and letterpress.</div>
    </div>
  </div>
  <div class="abs" style="inset:0;clip-path:polygon(0 0,${cut[0][0]}px 0,${cut[1][0]}px 1200px,0 1200px)">
    <div class="abs" style="inset:0;background:radial-gradient(ellipse at 30% 40%, #18203a, var(--night) 60%, var(--deep))"></div>
    ${stars(1600, 1200, 220, 43)}
    ${gilt}
    <div class="abs" style="left:70px;top:58px">
      <div class="caps foil" style="font-size:40px;letter-spacing:.24em">Gilt</div>
      <div style="font:italic 24px var(--serif);color:var(--muted)">Gold-foil gradient<br>for dark grounds.</div>
    </div>
  </div>
  <svg class="layer" width="1600" height="1200"><path d="M${cut[0][0]} 0L${cut[1][0]} 1200" stroke="url(#goldU)" stroke-width="3"/></svg>
</div>`;
}

// ── 05 In use: tarot, candle, app ───────────────────────────────────────────
function inUse() {
  return `${base}
<div class="shot" style="background:radial-gradient(ellipse at 40% 30%, #d8cbb2, #bfae90 70%, #a99878)">
  <!-- Tarot card -->
  <div class="abs" style="left:110px;top:150px;width:400px;height:680px;border-radius:22px;background:linear-gradient(160deg,#18203a,#0d1222);transform:rotate(-7deg);box-shadow:0 40px 70px rgba(40,28,10,.45);padding:22px">
    <div style="position:absolute;inset:18px;border:2px solid #c9a24f;border-radius:12px"></div>
    <div style="position:absolute;inset:26px;border:1px solid #8e7036;border-radius:8px"></div>
    ${stars(400, 680, 70, 5)}
    <div class="caps foil" style="position:absolute;top:56px;left:0;right:0;text-align:center;font-size:30px">XVIII</div>
    ${img('crescent-moon', 'left:40px;top:150px;width:320px;height:320px')}
    <div class="caps foil" style="position:absolute;bottom:60px;left:0;right:0;text-align:center;font-size:30px;letter-spacing:.3em;padding-left:.3em">The Moon</div>
  </div>
  <!-- Candle -->
  <div class="abs" style="left:600px;top:250px;width:380px;height:620px">
    <div style="position:absolute;left:30px;right:30px;top:0;height:70px;border-radius:14px 14px 4px 4px;background:linear-gradient(90deg,#8b6a2c,#e7c77a 40%,#9a7633)"></div>
    <div style="position:absolute;left:0;right:0;top:62px;bottom:0;border-radius:30px;background:linear-gradient(90deg,#141a2b,#2a3350 35%,#121726);box-shadow:0 40px 70px rgba(40,28,10,.45)"></div>
    <div style="position:absolute;left:34px;right:34px;top:170px;height:360px;background:var(--paper);border-radius:6px;padding:26px 20px;text-align:center;color:var(--ink)">
      <div class="caps" style="font-size:22px;letter-spacing:.42em;padding-left:.42em">Nocturne</div>
      <div style="height:1px;background:#bfb39b;margin:12px 30px"></div>
      ${inkSvg('leo', 'width:170px;height:170px;color:var(--ink);display:block;margin:6px auto')}
      <div style="font:italic 500 30px var(--serif)">Leo</div>
      <div class="caps" style="font-size:12px;color:#6b6476;margin-top:6px">Amber · Saffron · Smoke</div>
    </div>
  </div>
  <!-- Phone -->
  <div class="abs" style="left:1070px;top:110px;width:420px;height:860px;border-radius:58px;background:#0b0b10;padding:14px;box-shadow:0 50px 90px rgba(40,28,10,.5);transform:rotate(5deg)">
    <div style="position:relative;width:100%;height:100%;border-radius:46px;overflow:hidden;background:linear-gradient(180deg,#18203a,#0d1222)">
      ${stars(392, 832, 90, 77)}
      <div style="position:absolute;left:0;right:0;top:56px;text-align:center">
        <div class="caps" style="font-size:12px;color:var(--muted)">Thursday · 22 October</div>
        <div style="font:italic 500 34px var(--serif);margin-top:6px">Tonight's sky</div>
      </div>
      ${img('leo', 'left:86px;top:150px;width:220px;height:220px')}
      <div style="position:absolute;left:0;right:0;top:380px;text-align:center">
        <div class="caps foil" style="font-size:20px">Sun in Leo</div>
        <div style="font:italic 19px var(--serif);color:#cfc3a8;margin-top:4px;padding:0 40px">A bold night for beginnings. Say the thing out loud.</div>
      </div>
      ${[
        ['crescent-moon', 'Moon in Pisces', 'Waxing crescent · 21%'],
        ['saturn', 'Saturn stations', 'Retrograde from 11:04'],
        ['comet', 'Meteor shower', 'Peaks after midnight'],
      ]
        .map(
          ([s, a, b], i) => `<div style="position:absolute;left:24px;right:24px;top:${520 + i * 92}px;height:78px;border:1px solid #2f3756;border-radius:18px;background:rgba(255,255,255,.03);display:flex;align-items:center;gap:12px;padding:0 14px">
            ${img(s, 'position:static;width:58px;height:58px')}
            <div><div style="font:600 21px var(--serif)">${a}</div><div style="font:italic 16px var(--serif);color:var(--muted)">${b}</div></div></div>`,
        )
        .join('')}
    </div>
  </div>
  <div class="abs caps" style="left:110px;bottom:70px;font-size:15px;color:#5a4a2c">Gilt Almanac · Plate V · Tarot, candle label, astrology app</div>
</div>`;
}

const shots = [
  ['01-cover', cover()],
  ['02-catalogue', catalogue()],
  ['03-engraving-detail', loupe()],
  ['04-gilt-vs-ink', split()],
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
