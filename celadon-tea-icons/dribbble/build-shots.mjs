// Renders the Dribbble shots for the Celadon icon set.
//   NODE_PATH=$(npm root -g) node dribbble/build-shots.mjs
// Writes 1600 x 1200 PNGs (plus @2x) into dribbble/.

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { icons, groups, dripLine } from '../src/icons.mjs';
import { GLAZES, CLAY } from '../src/glazes.mjs';

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
const img = (slug, style = '') => `<img style="${style}" src="file://${root}/glazed/${fileName(slug)}" alt="">`;
let n = 0;
const line = (slug, style = '') =>
  readFileSync(join(root, 'line', fileName(slug)), 'utf8')
    .replace(/<svg[^>]*>/, `<svg viewBox="0 0 200 200" style="${style}">`)
    .replace(/cel-/g, `l${n++}-`);
const shadow = (x, y, w, h = 18, o = 0.28) =>
  `<div class="abs" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;border-radius:50%;background:radial-gradient(ellipse, rgba(60,40,20,${o}), transparent 70%)"></div>`;

const base = `
<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600&family=Zen+Kaku+Gothic+New:wght@400;500&display=swap">
<style>
  :root { --paper: #efe8dc; --ink: #2b211a; --muted: #857563; --seal: #c0392b; --mincho: "Shippori Mincho", serif; --gothic: "Zen Kaku Gothic New", sans-serif; }
  * { box-sizing: border-box; }
  html, body { margin: 0; }
  .shot { position: relative; width: 1600px; height: 1200px; overflow: hidden; color: var(--ink); font-family: var(--gothic); background: var(--paper); }
  .washi { position: absolute; inset: 0; pointer-events: none; mix-blend-mode: multiply; opacity: .3; }
  .seal { display: grid; place-items: center; background: var(--seal); color: #fff6ee; font-family: var(--mincho); font-weight: 600; border-radius: 10px; box-shadow: inset 0 0 0 3px rgba(255,255,255,.18); }
  .caps { text-transform: uppercase; letter-spacing: .3em; }
  img, .abs { position: absolute; display: block; }
  svg.layer { position: absolute; inset: 0; overflow: visible; pointer-events: none; }
</style>`;

// Washi paper: soft fibre noise multiplied over the background.
const washi = (seed = 3) => `<svg class="washi" width="1600" height="1200"><filter id="fib${seed}"><feTurbulence type="fractalNoise" baseFrequency=".035 .16" numOctaves="4" seed="${seed}"/>
  <feColorMatrix values="0 0 0 0 .55  0 0 0 0 .45  0 0 0 0 .35  0 0 0 -.9 .5"/></filter><rect width="1600" height="1200" filter="url(#fib${seed})"/></svg>`;

// ── 01 Cover: a still life inside an ensō ─────────────────────────────────────
function cover() {
  const cx = 930, cy = 560, R = 330;
  const arc = (r, a0, a1) => {
    const p = (a) => [cx + r * Math.cos((a * Math.PI) / 180), cy + r * Math.sin((a * Math.PI) / 180)];
    const [x0, y0] = p(a0), [x1, y1] = p(a1);
    return `M${x0.toFixed(1)} ${y0.toFixed(1)}A${r} ${r} 0 1 1 ${x1.toFixed(1)} ${y1.toFixed(1)}`;
  };
  return `${base}
<div class="shot" style="background:radial-gradient(ellipse at 60% 45%, #f6f1e7, #ece3d3 70%, #e2d6c1)">
  ${washi(3)}
  <svg class="layer" width="1600" height="1200">
    <filter id="brush"><feTurbulence type="fractalNoise" baseFrequency=".04 .9" numOctaves="2" seed="5" result="t"/><feDisplacementMap in="SourceGraphic" in2="t" scale="9"/></filter>
    <g filter="url(#brush)" fill="none" stroke="#2b211a" stroke-linecap="round">
      <path d="${arc(R, 118, 62)}" stroke-width="26" opacity=".9"/>
      <path d="${arc(R - 9, 140, 40)}" stroke-width="8" opacity=".55"/>
    </g>
  </svg>
  ${shadow(cx - 220, cy + 96, 440, 44, 0.34)}
  ${img('chawan', `left:${cx - 260}px;top:${cy - 300}px;width:520px;height:520px`)}
  ${shadow(cx + 222, cy + 200, 150, 24, 0.32)}
  ${img('chasen', `left:${cx + 190}px;top:${cy + 40}px;width:210px;height:210px`)}
  ${img('chashaku', `left:${cx - 330}px;top:${cy + 150}px;width:230px;height:230px`)}
  <div class="abs" style="left:150px;top:150px;writing-mode:vertical-rl;font:500 128px/1 var(--mincho);letter-spacing:.18em">CELADON</div>
  <div class="abs seal" style="left:168px;top:1010px;width:92px;height:92px;font-size:52px">茶</div>
  <div class="abs" style="left:310px;top:160px;writing-mode:vertical-rl;font:400 20px var(--gothic);letter-spacing:.4em;color:var(--muted)">釉 · 二十四の茶道具</div>
  <div class="abs" style="right:110px;bottom:96px;text-align:right">
    <div style="font:500 30px var(--mincho);letter-spacing:.04em">24 tea-ceremony icons</div>
    <div class="caps" style="font-size:13px;color:var(--muted);margin-top:8px">Glazed ceramic · Glazed &amp; Line SVG</div>
  </div>
</div>`;
}

// ── 02 The tokonoma shelves ──────────────────────────────────────────────────
function shelves() {
  const planks = [338, 552, 766, 980];
  const items = groups
    .map((g, row) => {
      const list = icons.filter((i) => i.group === g);
      const y = planks[row];
      return `
      <div class="abs" style="left:110px;top:${y}px;width:1380px;height:20px;border-radius:3px;background:linear-gradient(180deg,#c99d6b,#9e7346 60%,#7a5531);box-shadow:0 14px 22px rgba(60,40,20,.28)"></div>
      <div class="abs" style="left:110px;top:${y + 2}px;width:1380px;height:6px;background:repeating-linear-gradient(90deg, rgba(255,255,255,.08) 0 2px, transparent 2px 9px);"></div>
      <div class="abs caps" style="left:52px;top:${y - 120}px;writing-mode:vertical-rl;font-size:12px;color:var(--muted)">${g}</div>
      ${list.map((icon, i) => {
        const x = 150 + i * 222;
        return `${img(icon.slug, `left:${x}px;top:${y - 146}px;width:156px;height:156px`)}
          <div class="abs" style="left:${x - 20}px;width:196px;top:${y + 30}px;text-align:center;font:500 16px var(--mincho)">${icon.name}</div>`;
      }).join('')}`;
    })
    .join('');
  return `${base}
<div class="shot" style="background:linear-gradient(180deg,#f1ebdf,#e6dccb)">
  ${washi(7)}
  <div class="abs" style="left:110px;right:110px;top:70px;display:flex;justify-content:space-between;align-items:end">
    <div style="font:500 52px/1 var(--mincho);letter-spacing:.06em">The tea shelf</div>
    <div style="display:flex;align-items:center;gap:16px"><span class="caps" style="font-size:13px;color:var(--muted)">Celadon · 24 pieces</span><span class="seal" style="width:46px;height:46px;font-size:26px">茶</span></div>
  </div>
  ${items}
</div>`;
}

// ── 03 Glaze study: potter's test tiles ──────────────────────────────────────
function tiles() {
  const list = [
    ['celadon', '青磁', 'Celadon'], ['tenmoku', '天目', 'Tenmoku'], ['shino', '志野', 'Shino'], ['ruri', '瑠璃', 'Ruri'],
    ['amber', '飴釉', 'Ame'], ['matcha', '抹茶', 'Matcha'], ['iron', '鉄釉', 'Tetsu'], ['lacquer', '漆', 'Urushi'],
  ];
  const W = 270, H = 330, G = 56, X0 = (1600 - (4 * W + 3 * G)) / 2;
  const tile = ([g, kanji, name], i) => {
    const x = X0 + (i % 4) * (W + G), y = 210 + Math.floor(i / 4) * 470;
    const [hi, mid, lo] = GLAZES[g];
    const shape = `M18 0H${W - 18}Q${W} 0 ${W} 18V${H - 18}Q${W} ${H} ${W - 18} ${H}H18Q0 ${H} 0 ${H - 18}V18Q0 0 18 0Z`;
    return `<svg class="abs" style="left:${x}px;top:${y}px;filter:drop-shadow(0 18px 22px rgba(60,40,20,.28))" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
      <defs>
        <radialGradient id="t${i}" cx=".3" cy=".25" r="1"><stop offset="0" stop-color="${hi}"/><stop offset=".55" stop-color="${mid}"/><stop offset="1" stop-color="${lo}"/></radialGradient>
        <linearGradient id="c${i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${CLAY[0]}"/><stop offset="1" stop-color="${CLAY[1]}"/></linearGradient>
        <clipPath id="k${i}"><path d="${shape}"/></clipPath>
        <mask id="h${i}"><rect width="${W}" height="${H}" fill="#fff"/><circle cx="${W / 2}" cy="34" r="13" fill="#000"/></mask>
      </defs>
      <g clip-path="url(#k${i})" mask="url(#h${i})">
        <rect width="${W}" height="${H}" fill="url(#c${i})"/>
        <path d="${dripLine(-10, W + 10, 228, 5 + i * 7, 26)}V-10H-10Z" fill="url(#t${i})"/>
        <path d="M30 60C26 110 28 170 36 214" stroke="#fff" stroke-opacity=".6" stroke-width="10" fill="none" stroke-linecap="round"/>
      </g>
      <path d="${shape}" fill="none" stroke="#3a2a1f" stroke-width="2"/>
      <circle cx="${W / 2}" cy="34" r="13" fill="none" stroke="#3a2a1f" stroke-width="2"/>
      <text x="${W - 22}" y="${H - 24}" text-anchor="end" font-family="Zen Kaku Gothic New" font-size="13" fill="#5a3d26" letter-spacing="3">No.${String(i + 1).padStart(2, '0')}</text>
    </svg>
    <div class="abs" style="left:${x}px;width:${W}px;top:${y + H + 22}px;display:flex;justify-content:space-between;align-items:baseline">
      <span style="font:600 30px var(--mincho)">${kanji}</span><span class="caps" style="font-size:13px;color:var(--muted)">${name}</span>
    </div>`;
  };
  return `${base}
<div class="shot" style="background:linear-gradient(180deg,#f3ede2,#e7ddcc)">
  ${washi(11)}
  <div class="abs" style="left:${X0}px;top:84px">
    <div style="font:500 52px/1 var(--mincho);letter-spacing:.04em">Glaze study</div>
    <div class="caps" style="font-size:13px;color:var(--muted);margin-top:14px">Eight glazes over speckled clay, as a potter's test tiles</div>
  </div>
  <div class="abs seal" style="right:${X0}px;top:84px;width:64px;height:64px;font-size:34px">釉</div>
  ${list.map(tile).join('')}
</div>`;
}

// ── 04 Two hanging scrolls ────────────────────────────────────────────────────
function scrolls() {
  const scroll = (x, brocade, title, icons3, glazed) => `
    <svg class="layer" width="1600" height="1200"><path d="M${x + 60} 104L${x + 250} 40L${x + 440} 104" fill="none" stroke="#5a3d26" stroke-width="2.4"/>
      <circle cx="${x + 250}" cy="34" r="7" fill="none" stroke="#5a3d26" stroke-width="2.4"/></svg>
    <div class="abs" style="left:${x - 10}px;top:96px;width:520px;height:22px;border-radius:11px;background:linear-gradient(180deg,#8a6038,#5a3d26)"></div>
    <div class="abs" style="left:${x}px;top:116px;width:500px;height:956px;background:${brocade};box-shadow:0 30px 60px rgba(60,40,20,.3)">
      <div style="position:absolute;left:56px;right:56px;top:88px;bottom:110px;background:#f7f1e6;box-shadow:inset 0 0 0 1px rgba(90,61,38,.25)">
        ${icons3.map((s, i) => (glazed ? img(s, `left:${(388 - 200) / 2 - 10}px;top:${40 + i * 230}px;width:220px;height:220px`) : `<div style="position:absolute;left:${(388 - 220) / 2}px;top:${40 + i * 230}px">${line(s, 'width:220px;height:220px;color:#2b211a')}</div>`)).join('')}
        <div style="position:absolute;right:16px;top:28px;writing-mode:vertical-rl;font:500 22px var(--mincho);letter-spacing:.3em">${title}</div>
      </div>
    </div>
    <div class="abs" style="left:${x - 16}px;top:1066px;width:532px;height:30px;border-radius:15px;background:linear-gradient(180deg,#3a2a1f,#1f1611)"></div>
    <div class="abs" style="left:${x - 30}px;top:1068px;width:26px;height:26px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#e8d3a8,#9d7330)"></div>
    <div class="abs" style="left:${x + 504}px;top:1068px;width:26px;height:26px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#e8d3a8,#9d7330)"></div>`;
  const label = (x, t, d) => `<div class="abs" style="left:${x}px;width:500px;top:1110px;text-align:center"><span style="font:500 24px var(--mincho)">${t}</span><span class="caps" style="font-size:12px;color:var(--muted);margin-left:14px">${d}</span></div>`;
  return `${base}
<div class="shot" style="background:radial-gradient(ellipse at 50% 30%, #f4eee3, #e3d8c5 75%)">
  ${washi(13)}
  ${scroll(200, 'linear-gradient(180deg,#a9bfae,#8ea795)', '釉 · Glazed', ['tetsubin', 'yunomi', 'ikebana'], true)}
  ${scroll(900, 'linear-gradient(180deg,#3d4a6b,#2a3552)', '墨 · Line', ['tetsubin', 'yunomi', 'ikebana'], false)}
  ${label(200, 'Glazed', 'Full colour')}${label(900, 'Line', 'One colour, any colour')}
</div>`;
}

// ── 05 In use: tea house menu, tea box, steeping app ─────────────────────────
function inUse() {
  const menu = [['chawan', 'Matcha', 'Usucha, whisked to order', '9'], ['kyusu', 'Sencha', 'Uji, first flush', '7'], ['yunomi', 'Gyokuro', 'Shade-grown, 50°C', '12'], ['tetsubin', 'Hojicha', 'Roasted over charcoal', '6'], ['wagashi', 'Wagashi', 'Seasonal nerikiri', '5']];
  return `${base}
<div class="shot" style="background:repeating-linear-gradient(92deg, rgba(0,0,0,.06) 0 2px, transparent 2px 13px), linear-gradient(160deg,#5b4030,#3a281c 60%,#2a1c13)">
  <div class="abs" style="left:110px;top:100px;width:470px;height:960px;background:#f6f0e4;transform:rotate(-3deg);box-shadow:0 40px 80px rgba(0,0,0,.45);padding:64px 52px">
    ${washi(17).replace('width="1600" height="1200"', 'width="470" height="960"')}
    <div style="display:flex;justify-content:space-between;align-items:start">
      <div><div class="caps" style="font-size:12px;color:var(--muted)">Tea house</div><div style="font:500 56px/1.05 var(--mincho);margin-top:6px">Hanare</div></div>
      <div class="seal" style="width:58px;height:58px;font-size:32px">離</div>
    </div>
    <div style="height:1px;background:#d6cbb6;margin:30px 0 8px"></div>
    ${menu.map(([s, t, d, p]) => `<div style="display:grid;grid-template-columns:96px 1fr auto;gap:16px;align-items:center;padding:14px 0;border-bottom:1px solid #e3d9c6">
      <div style="position:relative;width:96px;height:96px">${img(s, 'left:0;top:0;width:96px;height:96px')}</div>
      <div><div style="font:600 26px var(--mincho)">${t}</div><div style="font-size:14px;color:var(--muted)">${d}</div></div>
      <div style="font:500 24px var(--mincho)">${p}</div></div>`).join('')}
  </div>
  <div class="abs" style="left:630px;top:620px;width:390px;height:390px;transform:rotate(8deg);background:linear-gradient(135deg,#d9b98c,#c49a68);box-shadow:0 34px 60px rgba(0,0,0,.45);border-radius:6px">
    <div style="position:absolute;inset:0;background:repeating-linear-gradient(35deg, rgba(90,61,38,.05) 0 2px, transparent 2px 6px);border-radius:6px"></div>
    <div style="position:absolute;left:0;right:0;top:170px;height:54px;background:#2a3552"></div>
    <div style="position:absolute;left:50%;top:40px;transform:translateX(-50%)">${line('tea-sprig', 'width:130px;height:130px;color:#2b211a')}</div>
    <div class="seal" style="position:absolute;left:163px;top:174px;width:46px;height:46px;font-size:26px">茶</div>
    <div style="position:absolute;left:0;right:0;top:250px;text-align:center;font:500 34px var(--mincho);color:#2b211a">Uji Sencha</div>
    <div class="caps" style="position:absolute;left:0;right:0;top:300px;text-align:center;font-size:12px;color:#5a3d26">First flush · 80 g</div>
  </div>
  <div class="abs" style="left:1080px;top:100px;width:410px;height:860px;border-radius:58px;background:#16110d;padding:13px;box-shadow:0 50px 90px rgba(0,0,0,.55);transform:rotate(3deg)">
    <div style="position:relative;width:100%;height:100%;border-radius:46px;overflow:hidden;background:#f4eee3">
      <div class="caps" style="position:absolute;left:0;right:0;top:58px;text-align:center;font-size:11px;color:var(--muted)">Steep</div>
      <div style="position:absolute;left:0;right:0;top:78px;text-align:center;font:600 32px var(--mincho)">Gyokuro</div>
      <svg style="position:absolute;left:62px;top:140px" width="260" height="260" viewBox="0 0 260 260">
        <circle cx="130" cy="130" r="116" fill="none" stroke="#e1d6c3" stroke-width="10"/>
        <circle cx="130" cy="130" r="116" fill="none" stroke="#4f8a72" stroke-width="10" stroke-linecap="round" stroke-dasharray="${(2 * Math.PI * 116 * 0.62).toFixed(1)} 999" transform="rotate(-90 130 130)"/>
      </svg>
      ${img('yunomi', 'left:117px;top:190px;width:150px;height:150px')}
      <div style="position:absolute;left:0;right:0;top:420px;text-align:center;font:500 54px var(--mincho)">1:14</div>
      <div class="caps" style="position:absolute;left:0;right:0;top:488px;text-align:center;font-size:12px;color:var(--muted)">50°C · second infusion</div>
      <div style="position:absolute;left:24px;right:24px;top:540px;display:grid;gap:10px">
        ${[['tetsubin', 'Water', '50°C, rested'], ['chashaku', 'Leaf', '6 g'], ['kyusu', 'Infusion', '2 of 3']].map(([s, t, d]) => `<div style="display:grid;grid-template-columns:62px 1fr;gap:10px;align-items:center;padding:8px 12px;background:#fff;border-radius:18px;box-shadow:0 2px 0 #e3d9c6">
          <div style="position:relative;width:62px;height:62px">${img(s, 'left:0;top:0;width:62px;height:62px')}</div>
          <div><div style="font:600 19px var(--mincho)">${t}</div><div style="font-size:13px;color:var(--muted)">${d}</div></div></div>`).join('')}
      </div>
    </div>
  </div>
</div>`;
}

const shots = [
  ['01-cover', cover()],
  ['02-tea-shelf', shelves()],
  ['03-glaze-study', tiles()],
  ['04-glazed-and-line', scrolls()],
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
    await page.waitForTimeout(600);
    await page.screenshot({ path: join(here, `${name}${scale === 2 ? '@2x' : ''}.png`), clip: { x: 0, y: 0, width: 1600, height: 1200 } });
  }
  await page.close();
}
await browser.close();
console.log(`Rendered ${shots.length} shots at 1x and 2x`);
