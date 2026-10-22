// Builds the coffee risograph icon set.
//   node src/build.mjs [preview-fragment-path]
// Writes textured/*.svg, clean/*.svg and preview.html next to src/.
// The optional argument also writes the preview without a doctype (for publishing as an artifact).

import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { icons, groups } from './icons.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

const INK = {
  pink: '#ff48b0',      // Riso Fluorescent Pink
  blue: '#0078bf',      // Riso Blue
  tint: '#ffb3dc',      // flat stand-in for the pink halftone (clean version)
  overPink: '#002284',  // blue printed over pink (multiply)
  overTint: '#0054a5',  // blue printed over the pink halftone (multiply)
};
const BLUE_ATTRS = (color) =>
  `fill="none" stroke="${color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"`;
const MISREGISTER = 'translate(2.2 -1.6)';

const fill = (list, map) =>
  list.map((s) => s.replace(/\{([TPB])\}/g, (_, k) => map[k])).join('\n    ');

// Shapes that define an overlap area: filled with the given token, never stroke-only.
const areas = (list, token) =>
  list
    .filter((s) => s.includes(`fill="{${token}}"`))
    .map((s) => s.replace(/\s(fill|stroke|stroke-width|stroke-linecap)="[^"]*"/g, ''))
    .join('\n    ');

const open = (title) =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">\n  <title>${title}</title>`;

function textured(icon) {
  const id = `riso-${icon.slug}`;
  return `${open(icon.name)}
  <defs>
    <filter id="${id}-ink-p" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="2" seed="11" result="n"/>
      <feColorMatrix in="n" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -3 0 0 0 2.65" result="m"/>
      <feComposite in="SourceGraphic" in2="m" operator="in"/>
    </filter>
    <filter id="${id}-ink-b" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="2" seed="23" result="n"/>
      <feColorMatrix in="n" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -3 0 0 0 2.65" result="m"/>
      <feComposite in="SourceGraphic" in2="m" operator="in"/>
    </filter>
    <pattern id="${id}-dots" width="4.6" height="4.6" patternUnits="userSpaceOnUse" patternTransform="rotate(22)">
      <circle cx="2.3" cy="2.3" r="1.45" fill="${INK.pink}"/>
    </pattern>
  </defs>
  <g style="mix-blend-mode:multiply" filter="url(#${id}-ink-p)" transform="${MISREGISTER}">
    ${fill([...icon.tint, ...icon.pink], { T: `url(#${id}-dots)`, P: INK.pink, B: INK.blue })}
  </g>
  <g style="mix-blend-mode:multiply" filter="url(#${id}-ink-b)" ${BLUE_ATTRS(INK.blue)}>
    ${fill(icon.blue, { B: INK.blue })}
  </g>
</svg>
`;
}

function clean(icon) {
  const id = `riso-${icon.slug}`;
  const blue = (color) => fill(icon.blue, { B: color });
  return `${open(icon.name)}
  <defs>
    <clipPath id="${id}-tint-area">
    ${areas(icon.tint, 'T')}
    </clipPath>
    <clipPath id="${id}-pink-area">
    ${areas(icon.pink, 'P')}
    </clipPath>
  </defs>
  <g id="tint">
    ${fill(icon.tint, { T: INK.tint })}
  </g>
  <g id="pink">
    ${fill(icon.pink, { P: INK.pink })}
  </g>
  <g id="blue" ${BLUE_ATTRS(INK.blue)}>
    ${blue(INK.blue)}
  </g>
  <g id="blue-over-tint" clip-path="url(#${id}-tint-area)" ${BLUE_ATTRS(INK.overTint)}>
    ${blue(INK.overTint)}
  </g>
  <g id="blue-over-pink" clip-path="url(#${id}-pink-area)" ${BLUE_ATTRS(INK.overPink)}>
    ${blue(INK.overPink)}
  </g>
</svg>
`;
}

// Inline copies for the preview page need ids that stay unique per version.
const inline = (svg, version) =>
  svg
    .replace(/<svg [^>]*>/, '<svg viewBox="0 0 200 200" role="img">')
    .replace(/(id="|url\(#)riso-/g, `$1${version}-`)
    .replace(/\s?id="(tint|pink|blue|blue-over-tint|blue-over-pink)"/g, '');

mkdirSync(join(root, 'textured'), { recursive: true });
mkdirSync(join(root, 'clean'), { recursive: true });

const files = icons.map((icon, i) => {
  const file = `${String(i + 1).padStart(2, '0')}-${icon.slug}.svg`;
  const t = textured(icon);
  const c = clean(icon);
  writeFileSync(join(root, 'textured', file), t);
  writeFileSync(join(root, 'clean', file), c);
  return { icon, file, t, c };
});

const card = ({ icon, file, t, c }) => `
      <figure class="card">
        <div class="paper">
          <div class="v v-textured">${inline(t, 'tx').replace('<svg ', `<svg aria-label="${icon.name}, textured" `)}</div>
          <div class="v v-clean">${inline(c, 'cl').replace('<svg ', `<svg aria-label="${icon.name}, clean" `)}</div>
        </div>
        <figcaption><span class="name">${icon.name}</span><span class="file">${file.replace('.svg', '')}</span></figcaption>
      </figure>`;

const sections = groups
  .map(
    (g) => `
    <section>
      <h2>${g.replace('&', '&amp;')} <span>${files.filter((f) => f.icon.group === g).length}</span></h2>
      <div class="grid">${files.filter((f) => f.icon.group === g).map(card).join('')}
      </div>
    </section>`
  )
  .join('');

const page = `<title>Coffee Riso Icons</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: a printer's proof sheet. Toolbar on top, then four groups of six paper swatches. */
:root {
  --bg: #e9e6df;
  --fg: #1b1a2e;
  --muted: #625f72;
  --line: #d2cec4;
  --paper: #f4f0e6;
  --pink: ${INK.pink};
  --blue: ${INK.blue};
  --chip: #ffffff;
  --display: "Bricolage Grotesque", "Arial Narrow", Arial, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --bg: #16151d; --fg: #eeeaf4; --muted: #a29fb2; --line: #2d2b38; --chip: #23212d; color-scheme: dark; }
}
:root[data-theme="dark"] { --bg: #16151d; --fg: #eeeaf4; --muted: #a29fb2; --line: #2d2b38; --chip: #23212d; color-scheme: dark; }
body { background: var(--bg); color: var(--fg); font-family: var(--display); font-size: 16px; line-height: 1.5; }
.wrap {
  max-width: 1120px; margin: 0 auto; padding-block: 48px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
}
header { display: grid; gap: 12px; margin-bottom: 28px; }
.eyebrow, .file, h2 span, .ctl-label { font-family: var(--mono); font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
h1 { margin: 0; font-size: clamp(40px, 8vw, 84px); line-height: .95; font-weight: 700; letter-spacing: -.02em; text-wrap: balance; }
h1 .p { color: var(--pink); }
h1 .b { color: var(--blue); }
header p { margin: 0; max-width: 62ch; color: var(--muted); }
.controls { display: flex; flex-wrap: wrap; gap: 12px 24px; align-items: center; padding-block: 14px; border-block: 1px solid var(--line); margin-bottom: 8px; }
.seg { display: inline-flex; gap: 8px; align-items: center; }
.seg button {
  font: 500 13px var(--mono); padding: 7px 12px; border-radius: 999px; cursor: pointer;
  border: 1px solid var(--line); background: var(--chip); color: var(--fg);
}
.seg button[aria-pressed="true"] { background: var(--fg); color: var(--bg); border-color: var(--fg); }
.seg button:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }
section { padding-top: 28px; }
h2 { font-size: 24px; margin: 0 0 14px; display: flex; gap: 10px; align-items: baseline; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 16px; }
.card { margin: 0; min-width: 0; }
.paper { aspect-ratio: 1; max-width: 100%; background: var(--paper); border-radius: 3px; display: grid; place-items: center; box-shadow: 0 1px 0 rgb(0 0 0 / .06); }
.v { display: grid; place-items: center; width: 100%; height: 100%; }
.v svg { display: block; width: var(--icon, 100%); height: var(--icon, 100%); }
.v-clean { display: none; }
body.show-clean .v-clean { display: grid; }
body.show-clean .v-textured { display: none; }
body.size-48 { --icon: 48px; }
body.size-24 { --icon: 24px; }
figcaption { display: grid; gap: 2px; margin-top: 8px; }
.name { font-weight: 700; font-size: 15px; }
.file { font-size: 11px; }
.foot { margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--line); color: var(--muted); font-size: 14px; max-width: 70ch; }
@media (max-width: 440px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; } }
</style>

<main class="wrap">
  <header>
    <div class="eyebrow">Icon set · 24 icons · 2 inks · SVG</div>
    <h1>Coffee <span class="p">Riso</span> <span class="b">Icons</span></h1>
    <p>A two-ink risograph set for specialty coffee: Fluorescent Pink and Blue on uncoated paper, printed slightly out of register. Every icon ships as a textured SVG with grain and halftone, and a clean SVG of flat, editable shapes.</p>
  </header>
  <div class="controls">
    <div class="seg" role="group" aria-label="Version">
      <span class="ctl-label">Version</span>
      <button type="button" id="v-textured" aria-pressed="true">Textured</button>
      <button type="button" id="v-clean" aria-pressed="false">Clean</button>
    </div>
    <div class="seg" role="group" aria-label="Size">
      <span class="ctl-label">Size</span>
      <button type="button" id="s-full" aria-pressed="true">Full</button>
      <button type="button" id="s-48" aria-pressed="false">48 px</button>
      <button type="button" id="s-24" aria-pressed="false">24 px</button>
    </div>
  </div>
  ${sections}
  <p class="foot">Textured files use SVG filters and blend modes, so they look right in browsers and on websites. Clean files use only flat fills and clip paths, so they open correctly in Figma, Illustrator and Sketch. Overlaps in the clean files are pre-mixed: blue over pink becomes deep indigo, blue over the halftone becomes mid blue.</p>
</main>

<script>
  (function () {
    var b = document.body;
    function pick(ids, active, apply) {
      ids.forEach(function (id) { document.getElementById(id).setAttribute('aria-pressed', String(id === active)); });
      apply();
    }
    var versions = ['v-textured', 'v-clean'];
    versions.forEach(function (id) {
      document.getElementById(id).addEventListener('click', function () {
        pick(versions, id, function () { b.classList.toggle('show-clean', id === 'v-clean'); });
      });
    });
    var sizes = ['s-full', 's-48', 's-24'];
    sizes.forEach(function (id) {
      document.getElementById(id).addEventListener('click', function () {
        pick(sizes, id, function () {
          b.classList.remove('size-48', 'size-24');
          if (id !== 's-full') b.classList.add('size-' + id.slice(2));
        });
      });
    });
  })();
</script>
`;

writeFileSync(join(root, 'preview.html'), `<!doctype html>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n${page}`);
if (process.argv[2]) writeFileSync(process.argv[2], page);
console.log(`Built ${files.length} icons x 2 versions`);
