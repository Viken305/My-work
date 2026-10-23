// Renders the Calibre motion shot: a 12-second seamless loop, 1600 x 1200, H.264 MP4.
//   node src/build.mjs
//   NODE_PATH=$(npm root -g) node dribbble/build-motion.mjs
// Frames are drawn by Chromium, one per tick of a render(t) function (t from 0 to 1),
// and encoded with ffmpeg. Everything that moves completes whole cycles, so the end meets the start.

import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { icons } from '../src/icons.mjs';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const work = join(here, '.html');
const frames = join(work, 'frames');
rmSync(frames, { recursive: true, force: true });
mkdirSync(frames, { recursive: true });

const SECONDS = 12, FPS = 30;
const file = (slug) => `file://${root}/chrome/${String(icons.findIndex((x) => x.slug === slug) + 1).padStart(2, '0')}-${slug}.svg`;

const C = [1090, 600], R = 380;
let ticks = '';
for (let i = 0; i < 120; i++) {
  const a = (i * 3 * Math.PI) / 180, r0 = R + 14, r1 = R + (i % 10 ? 22 : 34);
  ticks += `M${(C[0] + r0 * Math.cos(a)).toFixed(1)} ${(C[1] + r0 * Math.sin(a)).toFixed(1)}L${(C[0] + r1 * Math.cos(a)).toFixed(1)} ${(C[1] + r1 * Math.sin(a)).toFixed(1)}`;
}
const tiles = ['wristwatch', 'moon-phase', 'escape-wheel', 'hourglass'];

const html = `<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
  html, body { margin: 0; }
  .stage { position: relative; width: 1600px; height: 1200px; overflow: hidden; color: #e9ecf0; font-family: Manrope, sans-serif;
           background: radial-gradient(circle at 68% 50%, #2b3039 0%, #15171b 42%, #08090b 100%); }
  .abs { position: absolute; }
  .mono { font-family: "JetBrains Mono", monospace; letter-spacing: .12em; text-transform: uppercase; }
  .chrome { background: linear-gradient(180deg, #ffffff 0%, #c9d0d9 15%, #59626f 23%, #e8edf2 28%, #8f98a5 40%, #dfe4ea 50%, #c9d0d9 65%, #59626f 73%, #e8edf2 78%, #8f98a5 90%, #ffffff 100%);
            background-size: 100% 200%; -webkit-background-clip: text; background-clip: text; color: transparent; }
  .tile { width: 120px; height: 120px; border: 1px solid #2c3038; border-radius: 16px; background: rgba(255,255,255,.02); position: relative; }
  .tile img { position: absolute; left: 10px; top: 10px; width: 100px; height: 100px; }
  .tile i { position: absolute; inset: -1px; border-radius: 16px; border: 1.5px solid #4b7de6; box-shadow: 0 0 28px rgba(75,125,230,.45), inset 0 0 22px rgba(75,125,230,.18); opacity: 0; }
</style>
<div class="stage">
  <svg class="abs" style="left:0;top:0" width="1600" height="1200" fill="none" stroke="#4b7de6">
    <g opacity=".45" stroke-width="1">
      <path d="M${C[0]} 40V1160M640 ${C[1]}H1560"/>
      <circle cx="${C[0]}" cy="${C[1]}" r="${R}" stroke-dasharray="4 8"/>
      <circle cx="${C[0]}" cy="${C[1]}" r="${R - 120}" stroke-dasharray="2 10"/>
      <g id="ring"><path d="${ticks}"/></g>
    </g>
    <path id="sweepArc" d="" stroke="#9cc1ff" stroke-width="2.4" stroke-linecap="round" opacity=".9"/>
  </svg>
  <div class="abs" style="left:${C[0] - 360}px;top:${C[1] - 360}px;width:720px;height:720px;border-radius:50%;background:radial-gradient(circle, rgba(75,125,230,.14), transparent 65%)"></div>
  <img id="tb" class="abs" src="${file('tourbillon')}" style="left:${C[0] - 330}px;top:${C[1] - 330}px;width:660px;height:660px">
  <div id="sweep" class="abs" style="left:0;top:0;width:1600px;height:1200px;mix-blend-mode:soft-light;pointer-events:none"></div>
  <div class="abs" style="left:110px;top:190px;width:600px">
    <div class="mono" style="font-size:15px;color:#4b7de6">Ref. CAL-24</div>
    <div id="title" class="chrome" style="font:200 112px/1 Manrope;letter-spacing:.14em;margin-top:18px">CALIBRE</div>
    <div style="font:300 26px/1.4 Manrope;color:#c9ced6;margin-top:22px;max-width:480px">Twenty-four watchmaking icons in polished chrome.</div>
    <div class="mono" style="display:flex;align-items:center;gap:16px;margin-top:40px;font-size:13px;color:#7d838d">
      <svg width="64" height="64" viewBox="-32 -32 64 64"><circle r="29" fill="none" stroke="#2c3038" stroke-width="2"/>
        <path d="${Array.from({ length: 12 }, (_, i) => { const a = (i * 30 * Math.PI) / 180; return `M${(24 * Math.sin(a)).toFixed(1)} ${(-24 * Math.cos(a)).toFixed(1)}L${(28 * Math.sin(a)).toFixed(1)} ${(-28 * Math.cos(a)).toFixed(1)}`; }).join('')}" stroke="#59626f" stroke-width="1.6"/>
        <path id="hand" d="M0 6V-24" stroke="#4b7de6" stroke-width="2.6" stroke-linecap="round"/><circle r="3" fill="#c9d0d9"/></svg>
      <span>Tourbillon · one turn, twelve seconds</span>
    </div>
  </div>
  <div class="abs" style="left:96px;top:880px;display:flex;gap:18px">
    ${tiles.map((s) => `<div class="tile"><img src="${file(s)}"><i></i></div>`).join('')}
  </div>
</div>
<script>
  const tb = document.getElementById('tb'), ring = document.getElementById('ring'), hand = document.getElementById('hand');
  const title = document.getElementById('title'), sweep = document.getElementById('sweep'), arc = document.getElementById('sweepArc');
  const glows = [...document.querySelectorAll('.tile i')];
  const C = ${JSON.stringify(C)}, R = ${R};
  window.render = (t) => {
    tb.style.transform = 'rotate(' + (360 * t) + 'deg)';
    ring.setAttribute('transform', 'rotate(' + (-36 * t) + ' ' + C[0] + ' ' + C[1] + ')');
    hand.setAttribute('transform', 'rotate(' + (360 * t) + ')');
    title.style.backgroundPosition = '0 ' + (200 * t) + '%';
    // Two light sweeps per loop, each crossing the frame in 60% of its half.
    const p = (t * 2) % 1, x = -30 + (p / 0.6) * 160;
    sweep.style.background = p < 0.6
      ? 'linear-gradient(105deg, transparent ' + (x - 12) + '%, rgba(255,255,255,.55) ' + x + '%, transparent ' + (x + 12) + '%)'
      : 'transparent';
    // A bright arc that runs round the blueprint ring once per loop.
    const a0 = 360 * t - 90, a1 = a0 + 40, rad = (d) => d * Math.PI / 180, r = R - 120;
    arc.setAttribute('d', 'M' + (C[0] + r * Math.cos(rad(a0))) + ' ' + (C[1] + r * Math.sin(rad(a0))) + 'A' + r + ' ' + r + ' 0 0 1 ' + (C[0] + r * Math.cos(rad(a1))) + ' ' + (C[1] + r * Math.sin(rad(a1))));
    // Tiles light one after another, each easing in and out over its quarter.
    glows.forEach((g, i) => {
      const d = Math.min(Math.abs(t * 4 - i - 0.5), Math.abs(t * 4 - i - 0.5 + 4), Math.abs(t * 4 - i - 0.5 - 4));
      g.style.opacity = Math.max(0, Math.cos(Math.min(d, 1) * Math.PI / 2)) ** 2;
    });
  };
</script>`;

const path = join(work, '07-motion.html');
writeFileSync(path, html);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });
await page.goto(`file://${path}`);
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(600);
const total = SECONDS * FPS;
for (let i = 0; i < total; i++) {
  await page.evaluate((t) => window.render(t), i / total);
  await page.screenshot({ path: join(frames, `${String(i).padStart(4, '0')}.png`) });
}
// A still of the first frame, for the post thumbnail if Dribbble asks for one.
await page.evaluate(() => window.render(0));
await page.screenshot({ path: join(here, '07-motion-poster.png') });
await browser.close();

execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', join(frames, '%04d.png'),
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', join(here, '07-motion.mp4')]);
rmSync(frames, { recursive: true, force: true });
console.log(`Encoded ${total} frames to dribbble/07-motion.mp4`);
