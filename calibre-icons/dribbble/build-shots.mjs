// Renders the Dribbble shots for the Calibre icon set.
//   NODE_PATH=$(npm root -g) node dribbble/build-shots.mjs
// Writes 1600 x 1200 PNGs (plus @2x) into dribbble/.

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { icons } from '../src/icons.mjs';
import { chromeLayer, gradients } from '../src/render.mjs';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const work = join(here, '.html');
mkdirSync(work, { recursive: true });

const index = (slug) => {
  const i = icons.findIndex((x) => x.slug === slug);
  if (i < 0) throw new Error(`unknown icon ${slug}`);
  return i;
};
const fileName = (slug) => `${String(index(slug) + 1).padStart(2, '0')}-${slug}.svg`;
const img = (slug, style = '') => `<img style="${style}" src="file://${root}/chrome/${fileName(slug)}" alt="">`;
let n = 0;
const line = (slug, style = '') =>
  readFileSync(join(root, 'line', fileName(slug)), 'utf8').replace(/<svg[^>]*>/, `<svg viewBox="0 0 200 200" style="${style}">`);

const polar = (cx, cy, r, deg) => [cx + r * Math.cos((deg * Math.PI) / 180), cy + r * Math.sin((deg * Math.PI) / 180)];

// One pass of an icon's chrome rendering, for the exploded view.
//   pass: 'rim' | 'body' | 'spec' | 'accent'
function plate(slug, pass) {
  const icon = icons[index(slug)];
  const id = `x${n++}-`;
  const parts = icon.layers.map((l) => {
    const p = chromeLayer(l, id).split(/(?=<path)/);
    const [type] = l;
    if (pass === 'rim') return type === 'tube' || type === 'blue' ? p[0].replace(/stroke="#[0-9a-f]+"/, 'stroke="#59616e"') : '';
    if (pass === 'body') return type === 'tube' ? p[1] : type === 'fine' || type === 'steel' ? p.join('') : '';
    if (pass === 'spec') return type === 'tube' || type === 'blue' ? p[2] : '';
    if (pass === 'accent') return type === 'blue' ? p[0] + p[1] : ['ruby', 'sand', 'sky'].includes(type) ? p.join('') : '';
    return p.join('');
  });
  return `<svg viewBox="0 0 200 200" width="100%" height="100%"><defs>${gradients(id).join('')}</defs>
    <g fill="none" stroke-linecap="round" stroke-linejoin="round">${parts.join('')}</g></svg>`;
}

const base = `
<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
  :root { --blue: #4b7de6; --steel: #c9d0d9; --muted: #7d838d; --sans: "Manrope", sans-serif; --mono: "JetBrains Mono", monospace; }
  * { box-sizing: border-box; }
  html, body { margin: 0; }
  .shot { position: relative; width: 1600px; height: 1200px; overflow: hidden; color: #e9ecf0; font-family: var(--sans); }
  .mono { font-family: var(--mono); letter-spacing: .12em; text-transform: uppercase; }
  .chrome-text { background: linear-gradient(180deg, #ffffff 0%, #c9d0d9 30%, #59626f 46%, #e8edf2 56%, #8f98a5 80%, #dfe4ea 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
  img, .abs { position: absolute; display: block; }
  svg.layer { position: absolute; inset: 0; overflow: visible; pointer-events: none; }
</style>`;

// ── 01 Cover: the technical drawing ──────────────────────────────────────────
function cover() {
  const c = [1090, 600], R = 380;
  let ticks = '';
  for (let i = 0; i < 120; i++) {
    const a = i * 3, [x0, y0] = polar(...c, R + 14, a), [x1, y1] = polar(...c, R + (i % 10 ? 22 : 34), a);
    ticks += `M${x0.toFixed(1)} ${y0.toFixed(1)}L${x1.toFixed(1)} ${y1.toFixed(1)}`;
  }
  const spec = [['Movement', '24 icons'], ['Finish', 'Polished chrome'], ['Accents', 'Blued steel · ruby'], ['Versions', 'Chrome · Line'], ['Format', 'SVG · 200 grid']];
  return `${base}
<div class="shot" style="background:radial-gradient(circle at 68% 50%, #2b3039 0%, #15171b 42%, #08090b 100%)">
  <svg class="layer" width="1600" height="1200" fill="none" stroke="#4b7de6">
    <g opacity=".45" stroke-width="1">
      <path d="M${c[0]} 40V1160M640 ${c[1]}H1560"/>
      <circle cx="${c[0]}" cy="${c[1]}" r="${R}" stroke-dasharray="4 8"/>
      <circle cx="${c[0]}" cy="${c[1]}" r="${R - 120}" stroke-dasharray="2 10"/>
      <path d="${ticks}"/>
    </g>
    <g stroke-width="1.2" opacity=".85">
      <path d="M${c[0] - 300} 1080H${c[0] + 300}M${c[0] - 300} 1068V1092M${c[0] + 300} 1068V1092"/>
      <path d="M${c[0] - 300} 1080l12 -5v10zM${c[0] + 300} 1080l-12 -5v10z" fill="#4b7de6"/>
    </g>
  </svg>
  <div class="abs mono" style="left:${c[0] - 70}px;top:1092px;font-size:13px;color:#4b7de6">Ø 62.00 mm</div>
  <div class="abs mono" style="left:${c[0] + 20}px;top:150px;font-size:12px;color:#4b7de6;opacity:.8">12 · 00</div>
  ${img('tourbillon', `left:${c[0] - 330}px;top:${c[1] - 330}px;width:660px;height:660px`)}
  <div class="abs" style="left:110px;top:190px;width:600px">
    <div class="mono" style="font-size:15px;color:var(--blue)">Ref. CAL-24</div>
    <div class="chrome-text" style="font:200 112px/1 var(--sans);letter-spacing:.14em;margin-top:18px">CALIBRE</div>
    <div style="font:300 26px/1.4 var(--sans);color:#c9ced6;margin-top:22px;max-width:480px">Twenty-four watchmaking icons in polished chrome.</div>
    <div style="margin-top:44px;border-top:1px solid #2c3038">
      ${spec.map(([k, v]) => `<div class="mono" style="display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #2c3038;font-size:13px"><span style="color:#7d838d">${k}</span><span style="color:#e9ecf0">${v}</span></div>`).join('')}
    </div>
  </div>
  <div class="abs" style="left:96px;top:880px;display:flex;gap:18px">
    ${['wristwatch', 'moon-phase', 'escape-wheel', 'hourglass'].map((s) => `<div style="width:120px;height:120px;border:1px solid #2c3038;border-radius:16px;background:rgba(255,255,255,.02);position:relative">${img(s, 'left:10px;top:10px;width:100px;height:100px')}</div>`).join('')}
  </div>
</div>`;
}

// ── 02 The parts tray ─────────────────────────────────────────────────────────
function tray() {
  const W = 218, H = 226, G = 14, X0 = (1600 - (6 * W + 5 * G)) / 2, Y0 = 186;
  const wells = icons
    .map((icon, i) => {
      const x = X0 + (i % 6) * (W + G), y = Y0 + Math.floor(i / 6) * (H + G);
      return `<div class="abs" style="left:${x}px;top:${y}px;width:${W}px;height:${H}px;border-radius:26px;background:radial-gradient(circle at 50% 40%, #1d2026, #121418 75%);box-shadow:inset 0 6px 14px rgba(0,0,0,.7), inset 0 -1px 0 rgba(255,255,255,.06), 0 1px 0 rgba(255,255,255,.05)">
        ${img(icon.slug, `left:${(W - 150) / 2}px;top:20px;width:150px;height:150px`)}
        <div class="mono" style="position:absolute;left:0;right:0;bottom:18px;text-align:center;font-size:11px;color:#8a909a"><span style="color:#4b7de6">${String(i + 1).padStart(2, '0')}</span> · ${icon.name}</div>
      </div>`;
    })
    .join('');
  return `${base}
<div class="shot" style="background:linear-gradient(180deg,#24272d,#16181c)">
  <div class="abs" style="left:40px;top:40px;right:40px;bottom:40px;border-radius:44px;background:repeating-linear-gradient(90deg, rgba(255,255,255,.018) 0 1px, transparent 1px 3px), linear-gradient(180deg,#0f1114,#0a0b0d);box-shadow:0 30px 80px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.08)"></div>
  <div class="abs" style="left:${X0}px;right:${X0}px;top:92px;display:flex;justify-content:space-between;align-items:baseline">
    <div class="chrome-text" style="font:200 46px/1 var(--sans);letter-spacing:.24em">PARTS TRAY</div>
    <div class="mono" style="font-size:13px;color:#7d838d">Calibre · <span style="color:#4b7de6">24 components</span> · chrome</div>
  </div>
  ${wells}
</div>`;
}

// ── 03 Exploded view of the finish ───────────────────────────────────────────
function exploded() {
  const passes = [
    ['rim', 'Dark rim', 'A 2.4 px graphite outline gives every rod an edge on any ground.'],
    ['body', 'Chrome body', 'A banded steel gradient, the reflection of a studio softbox.'],
    ['spec', 'Specular', 'A hairline highlight, offset up and left, sells the polish.'],
    ['accent', 'Blued steel & ruby', 'Hands and springs in heat-blued steel, jewels in ruby.'],
  ];
  const S = 400, X = 250, Y0 = 760, STEP = 150;
  const iso = 'transform:rotate(-30deg) skewX(30deg) scaleY(.86)';
  const plates = passes
    .map(([p], i) => `<div class="abs" style="left:${X}px;top:${Y0 - i * STEP - S / 2}px;width:${S}px;height:${S}px;${iso};border:1px solid rgba(201,208,217,.18);border-radius:26px;background:rgba(255,255,255,.025)">${plate('wristwatch', p)}</div>`)
    .reverse()
    .join('');
  const labels = passes
    .map(([, t, d], i) => {
      const y = Y0 - i * STEP;
      return `<svg class="layer" width="1600" height="1200"><path d="M${X + S / 2 + 190} ${y}H860" stroke="#4b7de6" stroke-width="1" stroke-dasharray="3 5"/><circle cx="${X + S / 2 + 190}" cy="${y}" r="4" fill="#4b7de6"/></svg>
        <div class="abs" style="left:880px;top:${y - 30}px;width:330px">
          <div class="mono" style="font-size:12px;color:#4b7de6">Layer 0${i + 1}</div>
          <div style="font:600 22px var(--sans);margin-top:4px">${t}</div>
          <div style="font:300 16px/1.45 var(--sans);color:#a3a9b2;margin-top:2px">${d}</div>
        </div>`;
    })
    .join('');
  return `${base}
<div class="shot" style="background:radial-gradient(circle at 30% 50%, #262a31, #121417 55%, #08090b)">
  <div class="abs" style="left:110px;top:92px">
    <div class="mono" style="font-size:13px;color:#4b7de6">Exploded view</div>
    <div class="chrome-text" style="font:200 56px/1.1 var(--sans);letter-spacing:.16em;margin-top:10px">THE FINISH</div>
  </div>
  ${plates}
  ${labels}
  <div class="abs" style="left:1250px;top:300px;width:300px;text-align:center">
    <div style="width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,#2e333b,#121417 70%);position:relative">${img('wristwatch', 'left:20px;top:20px;width:260px;height:260px')}</div>
    <div class="mono" style="font-size:12px;color:#7d838d;margin-top:22px">= Composite</div>
    <div style="font:600 22px var(--sans);margin-top:6px">Wristwatch</div>
  </div>
</div>`;
}

// ── 04 Three editions ─────────────────────────────────────────────────────────
function editions() {
  const cards = [
    { name: 'Black DLC', ref: 'Chrome', bg: 'linear-gradient(160deg,#16181c,#0a0b0d)', ink: null, fg: '#e9ecf0', muted: '#7d838d', set: ['wristwatch', 'chronograph', 'balance-wheel', 'tourbillon', 'ruby-jewel', 'loupe'] },
    { name: 'White ceramic', ref: 'Line · graphite', bg: 'linear-gradient(160deg,#ffffff,#e9ebee)', ink: '#15181d', fg: '#15181d', muted: '#7d838d', set: ['pocket-watch', 'gear', 'moon-phase', 'mainspring', 'tweezers', 'case-back'] },
    { name: 'Navy dial', ref: 'Line · silver', bg: 'radial-gradient(circle at 50% 30%,#1f3a7a,#0d1a3d 70%)', ink: '#dfe5ef', fg: '#ffffff', muted: '#8fa3cc', set: ['diver', 'escape-wheel', 'world-time', 'alarm', 'screwdriver', 'hourglass'] },
  ];
  const W = 452, G = 34, X0 = (1600 - (3 * W + 2 * G)) / 2;
  return `${base}
<div class="shot" style="background:linear-gradient(180deg,#3a3e46,#1d2025)">
  <div class="abs" style="left:0;right:0;top:70px;text-align:center">
    <div class="mono" style="font-size:13px;color:#9cc1ff">Two versions · every dial</div>
    <div style="font:200 50px/1.2 var(--sans);letter-spacing:.2em;margin-top:8px;color:#f2f4f7">THE EDITIONS</div>
  </div>
  ${cards
    .map((c, i) => {
      const x = X0 + i * (W + G);
      const icon = (s) => (c.ink ? line(s, `width:172px;height:172px;color:${c.ink}`) : `<img src="file://${root}/chrome/${fileName(s)}" style="position:static;width:172px;height:172px">`);
      return `<div class="abs" style="left:${x}px;top:220px;width:${W}px;height:900px;border-radius:40px;background:${c.bg};box-shadow:0 40px 80px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.12);padding:46px 40px">
        <div class="mono" style="font-size:12px;color:${c.muted}">Edition 0${i + 1} · ${c.ref}</div>
        <div style="font:300 34px/1.2 var(--sans);letter-spacing:.06em;color:${c.fg};margin-top:8px">${c.name}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px 10px;justify-items:center;margin-top:44px">${c.set.map(icon).join('')}</div>
        <div class="mono" style="position:absolute;left:40px;right:40px;bottom:40px;display:flex;justify-content:space-between;font-size:11px;color:${c.muted};border-top:1px solid ${c.ink ? c.muted + '55' : '#2c3038'};padding-top:16px"><span>${c.ink ? 'currentColor' : 'Chrome · blued steel'}</span><span>SVG · 200 grid</span></div>
      </div>`;
    })
    .join('')}
</div>`;
}

// ── 05 In use: service app, certificate, service ticket ──────────────────────
function inUse() {
  const steps = [['loupe', 'Inspection', 'Done · 21 Oct'], ['case-back', 'Movement serviced', 'Done · 22 Oct'], ['balance-wheel', 'Regulation', 'In progress · ±2 s/day'], ['buckle', 'Ready for collection', 'Est. 28 Oct']];
  return `${base}
<div class="shot" style="background:radial-gradient(circle at 40% 30%, #4a4f58, #2a2d33 55%, #17191d)">
  <div class="abs" style="left:110px;top:150px;width:520px;height:730px;background:#f6f3ec;transform:rotate(-5deg);box-shadow:0 40px 80px rgba(0,0,0,.45);padding:64px 56px;color:#1a2036">
    <div style="position:absolute;inset:18px;border:1px solid #c8c2b4"></div>
    ${line('tourbillon', 'display:block;width:120px;height:120px;margin:0 auto;color:#1a3a8f')}
    <div style="text-align:center;font:200 40px var(--sans);letter-spacing:.3em;padding-left:.3em;margin-top:14px">CALIBRE</div>
    <div class="mono" style="text-align:center;font-size:11px;color:#7a7568;margin-top:6px">Certificate of authenticity</div>
    <div style="margin-top:44px;font-family:var(--mono);font-size:13px;letter-spacing:.06em">
      ${[['Reference', 'CAL-24 / 7700'], ['Case', 'Steel, 41 mm'], ['Movement', 'Automatic, 28,800 vph'], ['Jewels', '31 rubies'], ['Serial', 'Nº 0418']].map(([k, v]) => `<div style="display:flex;justify-content:space-between;padding:11px 0;border-bottom:1px solid #ddd6c7"><span style="color:#7a7568">${k}</span><span>${v}</span></div>`).join('')}
    </div>
    <div style="display:flex;justify-content:center;gap:26px;margin-top:40px">${['ruby-jewel', 'gear', 'crown'].map((s) => line(s, 'width:56px;height:56px;color:#1a3a8f')).join('')}</div>
  </div>
  <div class="abs" style="left:640px;top:700px;width:380px;height:240px;border-radius:22px;background:linear-gradient(150deg,#1c1f24,#0b0c0e);transform:rotate(6deg);box-shadow:0 30px 60px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.1);padding:30px 32px">
    <div class="mono" style="font-size:11px;color:#7d838d">Service ticket</div>
    <div style="font:300 30px var(--sans);letter-spacing:.06em;margin-top:6px">Nº 0418</div>
    <div class="mono" style="font-size:12px;color:#9cc1ff;margin-top:8px">Collect from 28 Oct</div>
    ${img('screwdriver', 'right:24px;top:50px;width:150px;height:150px')}
  </div>
  <div class="abs" style="left:1090px;top:110px;width:400px;height:850px;border-radius:58px;background:#050506;padding:13px;box-shadow:0 50px 90px rgba(0,0,0,.6), inset 0 0 0 2px #3a3e46;transform:rotate(3deg)">
    <div style="position:relative;width:100%;height:100%;border-radius:46px;overflow:hidden;background:radial-gradient(circle at 50% 22%,#262a31,#0c0d10 60%)">
      <div class="mono" style="position:absolute;left:0;right:0;top:58px;text-align:center;font-size:11px;color:#7d838d">Atelier service</div>
      <div style="position:absolute;left:0;right:0;top:80px;text-align:center;font:300 30px var(--sans);letter-spacing:.2em">CALIBRE</div>
      ${img('wristwatch', 'left:97px;top:140px;width:180px;height:180px')}
      <div style="position:absolute;left:0;right:0;top:330px;text-align:center"><span class="mono" style="font-size:11px;color:#9cc1ff;border:1px solid #2b56b8;border-radius:99px;padding:6px 12px">Ref. CAL-24 / 7700</span></div>
      <div style="position:absolute;left:24px;right:24px;top:390px">
        ${steps.map(([s, t, d], i) => `<div style="display:grid;grid-template-columns:60px 1fr;gap:12px;align-items:center;padding:12px 10px;border-bottom:1px solid #22252b;opacity:${i === 3 ? .55 : 1}">
          ${img(s, 'position:static;width:58px;height:58px')}
          <div><div style="font:600 18px var(--sans)">${t}</div><div class="mono" style="font-size:11px;color:${i === 2 ? '#9cc1ff' : '#7d838d'};letter-spacing:.06em">${d}</div></div></div>`).join('')}
      </div>
    </div>
  </div>
</div>`;
}

const shots = [
  ['01-cover', cover()],
  ['02-parts-tray', tray()],
  ['03-the-finish', exploded()],
  ['04-editions', editions()],
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
