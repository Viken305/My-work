// Builds the Creative Market pack for the Calibre icon set.
//   node src/build.mjs && NODE_PATH=$(npm root -g) node dribbble/build-shots.mjs
//   NODE_PATH=$(npm root -g) node creative-market/build-pack.mjs
// Writes:
//   creative-market/previews/*.jpg      3:2 product images (2340 x 1560), widened from the Dribbble shots
//   creative-market/.build/product/     what buyers download: SVGs, PNG exports, README, preview page

import { cpSync, mkdirSync, readdirSync, readFileSync, rmSync, unlinkSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { icons } from '../src/icons.mjs';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const shots = join(root, 'dribbble', '.html');
const previews = join(here, 'previews');
const product = join(here, '.build', 'product', 'Calibre-Icons');
rmSync(join(here, '.build'), { recursive: true, force: true });
rmSync(previews, { recursive: true, force: true });
mkdirSync(previews, { recursive: true });
mkdirSync(product, { recursive: true });

const W = 1800, H = 1200, SCALE = 1.3; // 2340 x 1560 output

const browser = await chromium.launch();

// ── Product previews: each 4:3 shot centred on a 3:2 canvas that carries its background ──
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: SCALE });
for (const file of readdirSync(shots).filter((f) => f.endsWith('.html')).sort()) {
  await page.goto(`file://${join(shots, file)}`);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(({ W, H }) => {
    const shot = document.querySelector('.shot');
    const cs = getComputedStyle(shot);
    const stage = document.createElement('div');
    // The shot's gradient moves to the wider stage so it runs unbroken edge to edge.
    stage.style.cssText = `position:relative;width:${W}px;height:${H}px;overflow:hidden;background:${cs.background}`;
    shot.style.background = 'transparent';
    shot.parentNode.insertBefore(stage, shot);
    shot.style.position = 'absolute';
    shot.style.left = `${(W - 1600) / 2}px`;
    shot.style.top = '0';
    shot.style.overflow = 'visible';
    stage.appendChild(shot);
    document.body.style.margin = '0';
  }, { W, H });
  await page.waitForTimeout(400);
  const out = join(previews, file.replace('.html', '.png'));
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: W, height: H } });
  execFileSync('python3', ['-c', `from PIL import Image; Image.open('${out}').convert('RGB').save('${out.replace('.png', '.jpg')}', quality=92, optimize=True)`]);
  unlinkSync(out);
}
await page.close();

// ── PNG exports of every icon, both versions, at 512 and 1024 px ──
const png = await browser.newPage({ viewport: { width: 1024, height: 1024 } });
for (const version of ['chrome', 'line']) {
  for (const size of [512, 1024]) {
    const dir = join(product, 'PNG', version === 'chrome' ? 'Chrome' : 'Line', `${size}px`);
    mkdirSync(dir, { recursive: true });
    await png.setViewportSize({ width: size, height: size });
    for (const [i, icon] of icons.entries()) {
      const name = `${String(i + 1).padStart(2, '0')}-${icon.slug}`;
      const svg = readFileSync(join(root, version, `${name}.svg`), 'utf8').replace(/width="200" height="200"/, `width="${size}" height="${size}"`);
      await png.setContent(`<body style="margin:0;background:transparent;color:#15181d">${svg}</body>`);
      await png.screenshot({ path: join(dir, `${name}.png`), omitBackground: true, clip: { x: 0, y: 0, width: size, height: size } });
    }
  }
}
await browser.close();

// ── SVGs, preview page and the buyer README ──
cpSync(join(root, 'chrome'), join(product, 'SVG', 'Chrome'), { recursive: true });
cpSync(join(root, 'line'), join(product, 'SVG', 'Line'), { recursive: true });
cpSync(join(root, 'preview.html'), join(product, 'Preview.html'));
cpSync(join(here, 'README-buyer.txt'), join(product, 'README.txt'));

console.log(`Previews written to ${previews}; product files in ${product}`);
