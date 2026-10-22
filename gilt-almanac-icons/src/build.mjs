// Builds the Gilt Almanac icon set.
//   node src/build.mjs [preview-fragment-path]
// Writes gilt/*.svg, ink/*.svg and preview.html next to src/.
// The optional argument also writes the preview without a doctype (for publishing as an artifact).

import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { icons, groups } from './icons.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

export const GOLD = [
  [0, '#fbe8b4'],
  [0.28, '#e2b85c'],
  [0.5, '#a37632'],
  [0.72, '#f1d58b'],
  [1, '#b98b3d'],
];
export const NIGHT = '#0f1526';
export const PAPER = '#f3ede1';
export const INK = '#1d1b2e';

const gradient = (id) =>
  `<linearGradient id="${id}" gradientUnits="userSpaceOnUse" x1="18" y1="12" x2="182" y2="188">` +
  GOLD.map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join('') +
  '</linearGradient>';

function svg(icon, version) {
  const id = `alm-${icon.slug}-`;
  const ink = version === 'gilt' ? `url(#${id}gold)` : 'currentColor';
  const sub = (s) => s.replaceAll('{ID}', id).replaceAll('{G}', ink);
  const defs = [...(version === 'gilt' ? [gradient(`${id}gold`)] : []), ...icon.defs.map(sub)];
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <title>${icon.name}</title>
  <defs>
    ${defs.join('\n    ')}
  </defs>
  <g fill="none" stroke="${ink}" stroke-linecap="round" stroke-linejoin="round">
    ${icon.body.map(sub).join('\n    ')}
  </g>
</svg>
`;
}

const files = {};
for (const version of ['gilt', 'ink']) {
  mkdirSync(join(root, version), { recursive: true });
  icons.forEach((icon, i) => {
    const name = `${String(i + 1).padStart(2, '0')}-${icon.slug}.svg`;
    const out = svg(icon, version);
    writeFileSync(join(root, version, name), out);
    (files[icon.slug] ||= {})[version] = { name, out };
  });
}

// Inline copy for the preview: unique ids per version, no xml title clutter.
const inline = (out, version) =>
  out
    .replace(/<svg[^>]*>/, '<svg viewBox="0 0 200 200" role="img">')
    .replace(/alm-/g, `${version}-`);

const cells = (version) =>
  groups
    .map((g) => {
      const list = icons.filter((icon) => icon.group === g);
      return `<section>
  <h2>${g}<span>${list.length}</span></h2>
  <div class="grid">
${list
  .map((icon) => {
    const f = files[icon.slug][version];
    return `    <figure>${inline(f.out, version)}<figcaption><b>${icon.name}</b><code>${f.name}</code></figcaption></figure>`;
  })
  .join('\n')}
  </div>
</section>`;
    })
    .join('\n');

const page = `<title>Gilt Almanac Icons</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root { --night: ${NIGHT}; --paper: ${PAPER}; --ink: ${INK}; --gold: #e2b85c; --muted: #8c8aa0; --line: #232b44; --bg: var(--night); --fg: #ece4d0; }
  body.ink { --bg: var(--paper); --fg: var(--ink); --muted: #6f6a78; --line: #ddd4c2; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--fg); font: 15px/1.5 'IBM Plex Mono', ui-monospace, monospace; transition: background .3s, color .3s; }
  main { max-width: 1120px; margin: 0 auto; padding: 56px 16px 80px; }
  header { display: flex; flex-wrap: wrap; gap: 24px; justify-content: space-between; align-items: end; border-bottom: 1px solid var(--line); padding-bottom: 28px; }
  h1 { font: 500 clamp(44px, 8vw, 84px)/.9 'Cormorant Garamond', serif; margin: 0; letter-spacing: -.01em; }
  h1 em { color: var(--gold); }
  body.ink h1 em { color: inherit; }
  header p { margin: 12px 0 0; color: var(--muted); max-width: 46ch; font-size: 13px; }
  .controls { display: grid; gap: 10px; font-size: 12px; }
  .seg { display: inline-flex; border: 1px solid var(--line); border-radius: 999px; padding: 3px; }
  .seg button { all: unset; cursor: pointer; padding: 6px 14px; border-radius: 999px; color: var(--muted); }
  .seg button[aria-pressed="true"] { background: var(--fg); color: var(--bg); }
  .seg button:focus-visible { outline: 2px solid var(--gold); }
  h2 { font: 600 28px 'Cormorant Garamond', serif; margin: 48px 0 18px; display: flex; gap: 12px; align-items: baseline; }
  h2 span { font: 12px 'IBM Plex Mono', monospace; color: var(--muted); }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); }
  figure { margin: 0; background: var(--bg); padding: 22px 16px 14px; display: grid; justify-items: center; gap: 12px; transition: background .3s; }
  figure svg { width: 100%; max-width: 132px; height: auto; color: var(--ink); }
  body[data-size="48"] figure svg { width: 48px; }
  body[data-size="24"] figure svg { width: 24px; }
  figcaption { display: grid; gap: 2px; text-align: center; font-size: 11px; }
  figcaption b { font: 600 17px 'Cormorant Garamond', serif; }
  figcaption code { color: var(--muted); }
  .v-ink, body.ink .v-gilt { display: none; }
  body.ink .v-ink { display: block; }
</style>
<body data-size="full">
<main>
  <header>
    <div>
      <h1>Gilt <em>Almanac</em></h1>
      <p>24 celestial and zodiac icons engraved like an old star atlas. Gilt for dark grounds, Ink for any single colour.</p>
    </div>
    <div class="controls">
      <div class="seg" role="group" aria-label="Version">
        <button data-v="gilt" aria-pressed="true">Gilt</button><button data-v="ink" aria-pressed="false">Ink</button>
      </div>
      <div class="seg" role="group" aria-label="Size">
        <button data-s="full" aria-pressed="true">Full</button><button data-s="48" aria-pressed="false">48 px</button><button data-s="24" aria-pressed="false">24 px</button>
      </div>
    </div>
  </header>
  <div class="v-gilt">
${cells('gilt')}
  </div>
  <div class="v-ink">
${cells('ink')}
  </div>
</main>
<script>
  const press = (sel, b) => document.querySelectorAll(sel).forEach((x) => x.setAttribute('aria-pressed', x === b));
  document.querySelectorAll('[data-v]').forEach((b) => b.onclick = () => { document.body.classList.toggle('ink', b.dataset.v === 'ink'); press('[data-v]', b); });
  document.querySelectorAll('[data-s]').forEach((b) => b.onclick = () => { document.body.dataset.size = b.dataset.s; press('[data-s]', b); });
</script>
</body>
`;

writeFileSync(join(root, 'preview.html'), `<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n${page}</html>\n`);
if (process.argv[2]) writeFileSync(process.argv[2], page);
console.log(`${icons.length} icons × 2 versions written`);
