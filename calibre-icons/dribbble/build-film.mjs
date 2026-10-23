// Renders the Calibre film: a 24-second H.264 MP4 showing all 24 icons.
//   node src/build.mjs
//   FORMAT=dribbble NODE_PATH=$(npm root -g) node dribbble/build-film.mjs
// FORMAT picks the output: dribbble (1600 x 1200, 4:3), 1080p (1920 x 1080) or 540p (960 x 540, the default).
// The scene is laid out at 1920 x 1080; for 4:3 the stage grows to 1920 x 1440 around it, then everything is
// captured at the scale the output needs. Chromium draws one frame per
// call to render(seconds); ffmpeg encodes them.

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
const frames = join(work, 'film-frames');
rmSync(frames, { recursive: true, force: true });
mkdirSync(frames, { recursive: true });

const SECONDS = 24, FPS = 30;
const FORMATS = {
  dribbble: { H: 1440, scale: 1600 / 1920, out: '10-film-1600x1200.mp4' },
  '1080p': { H: 1080, scale: 1, out: '11-film-1920x1080.mp4' },
  '540p': { H: 1080, scale: 0.5, out: '09-film-960x540.mp4' },
};
const F = FORMATS[process.env.FORMAT || '540p'];
if (!F) throw new Error(`FORMAT must be one of ${Object.keys(FORMATS).join(', ')}`);
const OW = Math.round(1920 * F.scale), OH = Math.round(F.H * F.scale);
const src = (i) => `file://${root}/chrome/${String(i + 1).padStart(2, '0')}-${icons[i].slug}.svg`;
const data = icons.map((icon, i) => ({ name: icon.name, group: icon.group, src: src(i) }));

const html = `<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
  html, body { margin: 0; }
  .stage { position: relative; width: 1920px; height: ${F.H}px; overflow: hidden; color: #e9ecf0; font-family: Manrope, sans-serif;
           background: radial-gradient(ellipse at 50% 60%, #22324f 0%, #12161e 45%, #07080a 100%); }
  .abs { position: absolute; }
  .mono { font-family: "JetBrains Mono", monospace; letter-spacing: .14em; text-transform: uppercase; }
  .chrome { background: linear-gradient(180deg, #ffffff 0%, #c9d0d9 30%, #59626f 46%, #e8edf2 56%, #8f98a5 80%, #dfe4ea 100%);
            -webkit-background-clip: text; background-clip: text; color: transparent; }
  .icon { position: absolute; left: 0; top: 0; width: 400px; height: 400px; margin: -200px 0 0 -200px; will-change: transform; }
  .center { position: absolute; left: 0; right: 0; text-align: center; }
</style>
<div class="stage">
<div class="abs" style="left:0;top:${(F.H - 1080) / 2}px;width:1920px;height:1080px">
  <div class="abs" style="left:360px;top:620px;width:1200px;height:380px;border-radius:50%;background:radial-gradient(ellipse, rgba(75,125,230,.3), transparent 70%);filter:blur(12px)"></div>
  <img id="bgTb" class="abs" src="${src(icons.findIndex((x) => x.slug === 'tourbillon'))}" style="left:1180px;top:120px;width:1000px;height:1000px;filter:blur(7px)">
  <div id="sweep" class="abs" style="left:0;right:0;top:${-(F.H - 1080) / 2}px;height:${F.H}px;mix-blend-mode:soft-light;pointer-events:none"></div>
  <div id="title" class="center" style="top:0">
    <div class="chrome" style="font:300 230px/1.1 Manrope;letter-spacing:.06em;padding-left:.06em">CALIBRE</div>
  </div>
  <div id="sub" class="center" style="top:640px;font:300 34px Manrope;color:#eef2f8;letter-spacing:.04em">24 watchmaking icons in polished chrome</div>
  ${data.map((d, i) => `<img class="icon" id="i${i}" src="${d.src}">`).join('')}
  <div id="label" class="center" style="top:860px">
    <div id="num" class="mono" style="font-size:20px;color:#4b7de6"></div>
    <div id="name" style="font:300 54px Manrope;margin-top:8px;letter-spacing:.02em"></div>
    <div id="grp" class="mono" style="font-size:16px;color:#7d838d;margin-top:8px"></div>
  </div>
  <div id="dots" class="center" style="top:1030px;display:flex;justify-content:center;gap:10px">${data.map((_, i) => `<i id="d${i}" style="width:8px;height:8px;border-radius:50%;background:#59626f;display:block"></i>`).join('')}</div>
  <div id="end" class="center mono" style="top:960px;font-size:20px;color:#9cc1ff">SVG · Chrome &amp; Line · Blued steel &amp; ruby</div>
</div>
</div>
<script>
  const N = ${data.length}, data = ${JSON.stringify(data.map(({ name, group }) => ({ name, group })))};
  const $ = (id) => document.getElementById(id);
  const els = data.map((_, i) => $('i' + i)), dots = data.map((_, i) => $('d' + i));
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const smooth = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
  const lerp = (a, b, k) => a + (b - a) * k;

  // Scene timing in seconds.
  const INTRO = 3, CAR0 = 3.8, CAR1 = 21, GRID = 21, GRID_DUR = 1.6;
  const STEP = (CAR1 - CAR0) / (N - 1);

  // Carousel position: hold on each icon, then glide to the next.
  const carouselP = (t) => {
    const x = clamp((t - CAR0) / STEP, 0, N - 1), k = Math.floor(x), f = x - k;
    return k + smooth((f - 0.35) / 0.65);
  };
  const carousel = (i, p) => {
    const d = i - p, a = Math.abs(d);
    const x = 960 + Math.sign(d) * (a <= 1 ? 360 * a : 360 + (a - 1) * 230);
    const s = Math.max(0.28, Math.pow(0.6, a)) * 1.05;
    return { x, y: 480, s, o: clamp(1 - 0.3 * (a - 0.5)), b: Math.min(6, a * 2) };
  };
  const grid = (i) => {
    const col = i % 8, row = Math.floor(i / 8);
    return { x: 330 + col * 180, y: 470 + row * 170, s: 0.36, o: 1, b: 0 };
  };

  window.render = (t) => {
    // Background tourbillon and title.
    const introIn = smooth(t / 1.2), toCar = smooth((t - INTRO) / (CAR0 - INTRO));
    $('bgTb').style.opacity = (0.32 * introIn * (1 - toCar)).toFixed(3);
    $('bgTb').style.transform = 'rotate(' + (t * 24) + 'deg) scale(' + lerp(1.1, 1, introIn) + ')';
    const titleY = lerp(330, 40, toCar), titleS = lerp(lerp(1.08, 1, introIn), 0.42, toCar);
    $('title').style.transform = 'translateY(' + titleY + 'px) scale(' + titleS + ')';
    $('title').style.opacity = introIn;
    $('sub').style.opacity = (smooth((t - 1.4) / 0.8) * (1 - toCar)).toFixed(3);
    const sw = (t - 1.0) / 1.4;
    $('sweep').style.background = sw > 0 && sw < 1
      ? 'linear-gradient(105deg, transparent ' + (sw * 160 - 42) + '%, rgba(255,255,255,.6) ' + (sw * 160 - 30) + '%, transparent ' + (sw * 160 - 18) + '%)' : 'transparent';

    // Icons: carousel, then fly into the grid.
    const p = carouselP(t), show = smooth((t - INTRO) / (CAR0 - INTRO));
    els.forEach((el, i) => {
      let c = carousel(i, p);
      if (t >= GRID) {
        const u = smooth((t - GRID - i * 0.025) / GRID_DUR), g = grid(i), from = carousel(i, N - 1);
        const fromO = from.o;
        c = { x: lerp(from.x, g.x, u), y: lerp(from.y, g.y, u), s: lerp(from.s, g.s, u), o: lerp(fromO, 1, u), b: lerp(from.b, 0, u) };
      }
      el.style.transform = 'translate(' + c.x + 'px,' + c.y + 'px) scale(' + c.s + ')';
      el.style.opacity = (c.o * show).toFixed(3);
      el.style.filter = (c.b > 0.1 ? 'blur(' + c.b.toFixed(2) + 'px) ' : '') + 'drop-shadow(0 30px 40px rgba(0,0,0,.6))';
      el.style.zIndex = String(100 - Math.round(Math.abs(i - p) * 4));
    });

    // Label for the icon nearest the centre, fading between icons.
    const k = Math.round(p), f = Math.abs(p - k);
    const labelO = show * (1 - smooth((t - GRID) / 0.5)) * (1 - smooth((f - 0.1) / 0.3));
    $('num').textContent = String(k + 1).padStart(2, '0') + ' / ' + N;
    $('name').textContent = data[k].name;
    $('grp').textContent = data[k].group;
    $('label').style.opacity = labelO.toFixed(3);
    dots.forEach((d, i) => { d.style.background = i === k ? '#4b7de6' : '#3a3f48'; });
    $('dots').style.opacity = (show * (1 - smooth((t - GRID) / 0.5))).toFixed(3);
    $('end').style.opacity = smooth((t - GRID - 1.4) / 0.8).toFixed(3);
  };
</script>`;

const path = join(work, 'film.html');
writeFileSync(path, html);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: F.H }, deviceScaleFactor: F.scale });
await page.goto(`file://${path}`);
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(800);
// TEST=1.5,4,12,22.4,23.9 renders only those moments as stills next to the frames, for checking layout.
if (process.env.TEST) {
  for (const t of process.env.TEST.split(',').map(Number)) {
    await page.evaluate((x) => window.render(x), t);
    await page.screenshot({ path: join(work, `film-test-${process.env.FORMAT || '540p'}-${t}.png`) });
  }
  await browser.close();
  process.exit(0);
}
const total = SECONDS * FPS;
for (let i = 0; i < total; i++) {
  await page.evaluate((t) => window.render(t), i / FPS);
  await page.screenshot({ path: join(frames, `${String(i).padStart(4, '0')}.png`) });
}
await browser.close();

const out = join(here, F.out);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', join(frames, '%04d.png'),
  '-vf', `scale=${OW}:${OH}:flags=lanczos`, '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
rmSync(frames, { recursive: true, force: true });
console.log(`Encoded ${total} frames to ${out}`);
