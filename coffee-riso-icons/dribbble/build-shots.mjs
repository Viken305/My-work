// Renders the Dribbble shots for the Coffee Riso icon set.
//   NODE_PATH=$(npm root -g) node dribbble/build-shots.mjs
// Writes 1600 x 1200 PNGs (plus @2x) into dribbble/.

import { mkdirSync, writeFileSync } from 'node:fs';
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

const file = (slug, version = 'textured') => {
  const i = icons.findIndex((x) => x.slug === slug);
  return `file://${root}/${version}/${String(i + 1).padStart(2, '0')}-${slug}.svg`;
};
const img = (slug, cls = '', style = '', version) =>
  `<img class="${cls}" style="${style}" src="${file(slug, version)}" alt="">`;

const base = `
<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
  :root { --paper: #f4f0e6; --pink: #ff48b0; --blue: #0078bf; --indigo: #002284; --tint: #ffb3dc;
          --display: "Bricolage Grotesque", Arial, sans-serif; --mono: "IBM Plex Mono", monospace; }
  * { box-sizing: border-box; }
  html, body { margin: 0; }
  .shot { position: relative; width: 1600px; height: 1200px; overflow: hidden; background: var(--paper); color: var(--indigo); font-family: var(--display); }
  .grain { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 50; }
  .ink { filter: url(#ink); mix-blend-mode: multiply; }
  .mono { font-family: var(--mono); letter-spacing: .08em; text-transform: uppercase; }
  img { display: block; position: absolute; }
</style>
<svg width="0" height="0" style="position:absolute">
  <defs>
    <filter id="ink" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="2" seed="5" result="n"/>
      <feColorMatrix in="n" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -3 0 0 0 2.75" result="m"/>
      <feComposite in="SourceGraphic" in2="m" operator="in"/>
    </filter>
    <filter id="paper" x="0" y="0" width="1" height="1">
      <feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" seed="4" stitchTiles="stitch"/>
      <feColorMatrix values="0 0 0 0 .42  0 0 0 0 .37  0 0 0 0 .3  .5 0 0 0 -.17"/>
    </filter>
    <pattern id="dots" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(22)">
      <circle cx="4.5" cy="4.5" r="2.8" fill="#ff48b0"/>
    </pattern>
  </defs>
</svg>`;
const grain = `<svg class="grain" viewBox="0 0 1600 1200" preserveAspectRatio="none"><rect width="1600" height="1200" filter="url(#paper)"/></svg>`;

// ---------- 1. Cover ----------
const cover = `${base}
<style>
  .cover .tag { position: absolute; left: 96px; top: 84px; font-size: 20px; color: var(--blue); }
  .cover h1 { position: absolute; left: 88px; top: 150px; margin: 0; font-weight: 800; font-size: 214px; line-height: .84; letter-spacing: -.03em; }
  .cover h1 span { display: block; }
  .cover h1 .b { color: var(--blue); }
  .cover h1 .p { color: var(--pink); margin-left: 6px; }
  .cover .sub { position: absolute; left: 96px; top: 760px; width: 600px; margin: 0; font-size: 34px; line-height: 1.25; font-weight: 600; }
  .cover .pills { position: absolute; left: 96px; top: 900px; display: flex; gap: 14px; flex-wrap: wrap; width: 680px; }
  .cover .pills span { border: 3px solid var(--blue); color: var(--blue); border-radius: 999px; padding: 10px 22px; font-size: 19px; font-weight: 500; }
  .cover .cats { position: absolute; left: 96px; bottom: 76px; font-size: 18px; color: var(--blue); }
  .cover .badge { position: absolute; left: 790px; top: 150px; width: 190px; height: 190px; border-radius: 50%; background: var(--blue);
    color: var(--paper); display: grid; place-content: center; text-align: center; transform: rotate(-12deg); }
  .cover .badge b { font-family: var(--display); font-size: 84px; line-height: .9; font-weight: 800; }
  .cover .badge span { font-size: 19px; margin-top: 6px; }
</style>
<div class="shot cover">
  <svg style="position:absolute;left:0;top:0" width="1600" height="1200" class="ink">
    <circle cx="1180" cy="580" r="360" fill="url(#dots)"/>
  </svg>
  <div class="tag mono">Icon set · SVG · Textured + Clean</div>
  <h1 class="ink"><span class="b">Coffee</span><span class="p">Riso</span><span class="b">Icons</span></h1>
  <p class="sub">24 two-ink risograph icons for cafés, roasters and coffee apps.</p>
  <div class="pills mono"><span>Textured + clean SVG</span><span>Figma ready</span><span>4 categories</span></div>
  ${img('pour-over', '', 'left:860px;top:236px;width:640px;height:640px')}
  ${img('espresso', '', 'left:1330px;top:70px;width:250px;height:250px;transform:rotate(8deg)')}
  ${img('croissant', '', 'left:1310px;top:860px;width:260px;height:260px;transform:rotate(-6deg)')}
  ${img('coffee-bean', '', 'left:830px;top:880px;width:230px;height:230px')}
  <div class="badge ink mono"><b>24</b><span>icons</span></div>
  <div class="cats mono">Brewing · Drinks · Beans &amp; origin · Café life</div>
  ${grain}
</div>`;

// ---------- 2. Full set ----------
const groupsOrder = ['Brewing', 'Drinks', 'Beans & origin', 'Café life'];
const rows = groupsOrder
  .map(
    (g) => `
    <div class="row">
      <div class="label mono">${g.replace('&', '&amp;')}</div>
      ${icons
        .filter((x) => x.group === g)
        .map((x) => `<figure><div class="ic">${img(x.slug, '', 'position:static;width:176px;height:176px')}</div><figcaption class="mono">${x.name}</figcaption></figure>`)
        .join('')}
    </div>`
  )
  .join('');
const fullSet = `${base}
<style>
  .set { padding: 64px 70px; }
  .set header { display: flex; justify-content: space-between; align-items: end; margin-bottom: 26px; }
  .set h2 { margin: 0; font-size: 64px; font-weight: 800; letter-spacing: -.03em; line-height: 1; }
  .set h2 .p { color: var(--pink); } .set h2 .b { color: var(--blue); }
  .set header .mono { font-size: 17px; color: var(--blue); }
  .set .row { display: grid; grid-template-columns: 170px repeat(6, 1fr); align-items: center; border-top: 2px solid var(--blue); padding-block: 8px 6px; }
  .set .label { font-size: 16px; color: var(--pink); font-weight: 600; align-self: start; padding-top: 18px; }
  .set figure { margin: 0; display: grid; justify-items: center; }
  .set figcaption { font-size: 12.5px; color: var(--blue); margin-top: -4px; }
</style>
<div class="shot set">
  <header>
    <h2 class="ink"><span class="b">The full</span> <span class="p">set</span></h2>
    <div class="mono">24 icons · 4 categories · 4 px line on a 200 px grid</div>
  </header>
  ${rows}
  ${grain}
</div>`;

// ---------- 3. Print detail ----------
// Latte drawn at 5x: icon point (x, y) sits at (40 + 5x, 60 + 5y).
const detail = `${base}
<style>
  .detail .callouts { position: absolute; left: 1090px; top: 120px; width: 450px; display: grid; gap: 54px; }
  .detail .c { display: grid; gap: 6px; }
  .detail .c .mono { font-size: 15px; color: var(--pink); font-weight: 600; }
  .detail .c b { font-size: 34px; line-height: 1.1; font-weight: 800; letter-spacing: -.02em; color: var(--indigo); }
  .detail .c span { font-size: 19px; line-height: 1.4; color: var(--blue); }
  .detail .sw { display: flex; gap: 10px; margin-top: 6px; }
  .detail .sw i { width: 42px; height: 42px; border-radius: 50%; display: block; }
</style>
<div class="shot detail">
  ${img('latte-art', '', 'left:40px;top:60px;width:1000px;height:1000px')}
  <svg style="position:absolute;left:0;top:0" width="1600" height="1200" fill="none" stroke="#0078bf" stroke-width="2">
    <circle cx="390" cy="462" r="10"/><path d="M400 462 C700 400 880 170 1070 165"/>
    <circle cx="600" cy="640" r="10"/><path d="M610 640 C800 640 900 345 1070 340"/>
    <circle cx="880" cy="842" r="10"/><path d="M890 842 C990 842 980 520 1070 515"/>
  </svg>
  <div class="callouts">
    <div class="c"><div class="mono">01 · Overprint</div><b>Blue over pink makes indigo</b><span>Inks multiply like real riso, so overlaps create a third colour for free.</span></div>
    <div class="c"><div class="mono">02 · Halftone</div><b>Pink dots at 22°</b><span>A lighter tint for secondary shapes, without adding a third ink.</span></div>
    <div class="c"><div class="mono">03 · Misregistration</div><b>2.2 px off register</b><span>The pink drum sits slightly off, just like a real print run.</span></div>
    <div class="c"><div class="mono">04 · Inks</div><b>Fluorescent Pink + Blue</b>
      <div class="sw"><i style="background:#ff48b0"></i><i style="background:#0078bf"></i><i style="background:#002284"></i><i style="background:#ffb3dc"></i></div></div>
  </div>
  ${grain}
</div>`;

// ---------- 4. Textured vs clean ----------
const pick = ['moka-pot', 'iced-coffee', 'roast-bag', 'cappuccino', 'origin-pin', 'pickup-bell', 'french-press', 'takeaway-cup', 'croissant'];
const half = (version) =>
  pick.map((s) => `<div class="cell">${img(s, '', 'position:static;width:210px;height:210px', version)}</div>`).join('');
const compare = `${base}
<style>
  .cmp { display: grid; grid-template-columns: 1fr 1fr; }
  .cmp .side { position: relative; padding: 72px 60px; display: grid; align-content: start; gap: 28px; }
  .cmp .side.clean { background: #ffffff; }
  .cmp h3 { margin: 0; font-size: 58px; line-height: 1; font-weight: 800; letter-spacing: -.03em; }
  .cmp .textured h3 { color: var(--pink); } .cmp .clean h3 { color: var(--blue); }
  .cmp p { margin: 0; font-size: 21px; color: var(--indigo); max-width: 30ch; line-height: 1.4; }
  .cmp .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px 0; justify-items: center; margin-top: 10px; }
  .cmp .uses { font-size: 15px; color: var(--blue); }
</style>
<div class="shot cmp">
  <div class="side textured">
    <div class="mono uses">Version 01</div>
    <h3 class="ink">Textured</h3>
    <p>Grain, halftone and misregistration built into the SVG. For websites, menus and print.</p>
    <div class="grid">${half('textured')}</div>
  </div>
  <div class="side clean">
    <div class="mono uses">Version 02</div>
    <h3>Clean</h3>
    <p>Flat fills with pre-mixed overlaps, each ink on its own layer. For Figma, Illustrator and Sketch.</p>
    <div class="grid">${half('clean')}</div>
  </div>
  <svg class="grain" viewBox="0 0 1600 1200" preserveAspectRatio="none" style="clip-path: inset(0 50% 0 0)"><rect width="1600" height="1200" filter="url(#paper)"/></svg>
</div>`;

// ---------- 5. In use ----------
const menuRows = [
  ['espresso', 'Espresso', 'Double shot, house blend', '3.00'],
  ['cappuccino', 'Cappuccino', 'Equal parts, cocoa dust', '4.20'],
  ['latte-art', 'Latte', 'Oat or whole milk', '4.50'],
  ['iced-coffee', 'Iced coffee', '18 h cold brew over ice', '4.80'],
  ['mocha', 'Mocha', 'Dark chocolate, cream', '5.00'],
  ['croissant', 'Croissant', 'Baked every morning', '3.50'],
]
  .map(
    ([s, n, d, p]) => `<div class="mi">${img(s, '', 'position:static;width:84px;height:84px')}<div><b>${n}</b><span>${d}</span></div><em>${p}</em></div>`
  )
  .join('');
const inUse = `${base}
<style>
  .use { background: var(--paper); }
  .use .menu { position: absolute; left: 90px; top: 92px; width: 660px; height: 1010px; background: #fbf8f1; transform: rotate(-3deg);
    box-shadow: 0 2px 4px rgb(60 40 20 / .12), 0 30px 60px -20px rgb(60 40 20 / .35); padding: 56px 56px; }
  .use .menu .brand { font-size: 15px; color: var(--pink); font-weight: 600; }
  .use .menu h4 { margin: 8px 0 26px; font-size: 76px; line-height: .9; font-weight: 800; letter-spacing: -.04em; color: var(--blue); }
  .use .mi { display: grid; grid-template-columns: 84px 1fr auto; gap: 18px; align-items: center; padding-block: 10px; border-top: 2px dashed rgb(0 120 191 / .45); }
  .use .mi b { display: block; font-size: 28px; font-weight: 800; color: var(--indigo); }
  .use .mi span { font-size: 17px; color: var(--blue); }
  .use .mi em { font-style: normal; font-family: var(--mono); font-size: 24px; color: var(--pink); font-weight: 600; }
  .use .panel { position: absolute; right: 0; top: 0; width: 720px; height: 1200px; background: var(--blue); }
  .use .phone { position: absolute; left: 960px; top: 110px; width: 450px; height: 940px; border-radius: 64px; background: #101119; padding: 14px;
    box-shadow: 0 40px 80px -20px rgb(0 20 60 / .6); }
  .use .screen { width: 100%; height: 100%; border-radius: 52px; background: var(--paper); overflow: hidden; padding: 66px 28px 28px; position: relative; }
  .use .screen .top { display: flex; justify-content: space-between; font-size: 13px; color: var(--blue); }
  .use .screen h5 { margin: 14px 0 20px; font-size: 40px; line-height: 1; font-weight: 800; letter-spacing: -.03em; color: var(--indigo); }
  .use .chips { display: flex; gap: 10px; }
  .use .chip { flex: 1; background: #fff; border-radius: 22px; padding: 8px 0 10px; display: grid; justify-items: center; font-size: 12px; color: var(--indigo); font-family: var(--mono); }
  .use .chip.on { background: var(--blue); color: var(--paper); }
  .use .feat { margin-top: 18px; border-radius: 30px; background: var(--tint); height: 300px; position: relative; padding: 22px; }
  .use .feat .mono { font-size: 12px; color: var(--indigo); }
  .use .feat b { display: block; font-size: 32px; color: var(--indigo); font-weight: 800; margin-top: 6px; letter-spacing: -.02em; }
  .use .feat .price { font-family: var(--mono); font-size: 20px; color: var(--indigo); margin-top: 4px; }
  .use .feat .add { position: absolute; left: 22px; bottom: 22px; background: var(--blue); color: var(--paper); border-radius: 999px; padding: 12px 24px; font-size: 16px; font-weight: 600; }
  .use .row2 { margin-top: 16px; background: #fff; border-radius: 24px; display: grid; grid-template-columns: 70px 1fr; align-items: center; gap: 10px; padding: 8px 18px 8px 8px; }
  .use .row2 b { display: block; font-size: 18px; color: var(--indigo); }
  .use .row2 span { font-size: 14px; color: var(--blue); }
</style>
<div class="shot use">
  <div class="panel"></div>
  <div class="menu">
    <div class="brand mono">Overprint Coffee · Est. 2026</div>
    <h4>Today's<br>menu</h4>
    ${menuRows}
  </div>
  <div class="phone"><div class="screen">
    <div class="top mono"><span>9:41</span><span>Overprint</span></div>
    <h5>What are we brewing today?</h5>
    <div class="chips">
      <div class="chip on">${img('pour-over', '', 'position:static;width:58px;height:58px')}Brew</div>
      <div class="chip">${img('latte-art', '', 'position:static;width:58px;height:58px')}Drinks</div>
      <div class="chip">${img('coffee-bean', '', 'position:static;width:58px;height:58px')}Beans</div>
      <div class="chip">${img('croissant', '', 'position:static;width:58px;height:58px')}Bakery</div>
    </div>
    <div class="feat">
      <div class="mono">Today's pick</div>
      <b>Iced coffee</b>
      <div class="price">4.80</div>
      <div class="add">Add to order</div>
      ${img('iced-coffee', '', 'right:4px;bottom:6px;width:250px;height:250px')}
    </div>
    <div class="row2">${img('stamp-card', '', 'position:static;width:62px;height:62px')}<div><b>5 of 8 stamps</b><span>3 more for a free drink</span></div></div>
    <div class="row2">${img('pickup-bell', '', 'position:static;width:62px;height:62px')}<div><b>Ready for pickup</b><span>Order #214 · Counter 2</span></div></div>
  </div></div>
  ${grain}
</div>`;

const shots = [
  ['01-cover', cover],
  ['02-full-set', fullSet],
  ['03-print-detail', detail],
  ['04-textured-vs-clean', compare],
  ['05-in-use', inUse],
];

const browser = await chromium.launch();
for (const scale of [1, 2]) {
  const page = await browser.newPage({ viewport: { width: 1600, height: 1200 }, deviceScaleFactor: scale });
  for (const [name, html] of shots) {
    const path = join(work, `${name}.html`);
    writeFileSync(path, html);
    await page.goto(`file://${path}`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(400);
    await page.screenshot({ path: join(here, `${name}${scale === 2 ? '@2x' : ''}.png`), clip: { x: 0, y: 0, width: 1600, height: 1200 } });
  }
  await page.close();
}
await browser.close();
console.log(`Rendered ${shots.length} shots at 1x and 2x`);
