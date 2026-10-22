// Builds the Calibre icon set.
//   node src/build.mjs [preview-fragment-path]
// Writes chrome/*.svg, line/*.svg and preview.html next to src/.
// The optional argument also writes the preview without a doctype (for publishing as an artifact).

import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { icons, groups } from './icons.mjs';
import { svg } from './render.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

const VERSIONS = [
  { key: 'chrome', label: 'Chrome', bg: '#0e0f12', fg: '#e9ecf0', muted: '#8a909a', line: '#23262c' },
  { key: 'line', label: 'Line', bg: '#eceef1', fg: '#15181d', muted: '#6b717b', line: '#d6d9de' },
];

const files = {};
for (const { key } of VERSIONS) {
  mkdirSync(join(root, key), { recursive: true });
  icons.forEach((icon, i) => {
    const name = `${String(i + 1).padStart(2, '0')}-${icon.slug}.svg`;
    const out = svg(icon, key);
    writeFileSync(join(root, key, name), out);
    (files[icon.slug] ||= {})[key] = { name, out };
  });
}

const inline = (out, key) => out.replace(/<svg[^>]*>/, '<svg viewBox="0 0 200 200" role="img">').replace(/cal-/g, `${key}-`);

const cells = (key) =>
  groups
    .map((g) => {
      const list = icons.filter((icon) => icon.group === g);
      return `<section>
  <h2>${g}<span>${list.length}</span></h2>
  <div class="grid">
${list.map((icon) => `    <figure>${inline(files[icon.slug][key].out, key)}<figcaption><b>${icon.name}</b><code>${files[icon.slug][key].name}</code></figcaption></figure>`).join('\n')}
  </div>
</section>`;
    })
    .join('\n');

const [A, B] = VERSIONS;
const page = `<title>Calibre Icons</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root { --bg: ${A.bg}; --fg: ${A.fg}; --muted: ${A.muted}; --line: ${A.line}; --accent: #4b7de6; }
  body.alt { --bg: ${B.bg}; --fg: ${B.fg}; --muted: ${B.muted}; --line: ${B.line}; --accent: #1a3a8f; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--fg); font: 400 15px/1.5 'Manrope', system-ui, sans-serif; transition: background .3s, color .3s; }
  main { max-width: 1120px; margin: 0 auto; padding: 56px 16px 80px; }
  header { display: flex; flex-wrap: wrap; gap: 24px; justify-content: space-between; align-items: end; border-bottom: 1px solid var(--line); padding-bottom: 28px; }
  h1 { font: 300 clamp(52px, 9vw, 96px)/.9 'Manrope', sans-serif; margin: 0; letter-spacing: .22em; }
  header p { margin: 14px 0 0; color: var(--muted); max-width: 48ch; font-size: 14px; }
  .ref { font: 500 12px 'JetBrains Mono', monospace; color: var(--accent); letter-spacing: .12em; }
  .controls { display: grid; gap: 10px; font: 500 12px 'JetBrains Mono', monospace; }
  .seg { display: inline-flex; border: 1px solid var(--line); border-radius: 999px; padding: 3px; }
  .seg button { all: unset; cursor: pointer; padding: 6px 14px; border-radius: 999px; color: var(--muted); }
  .seg button[aria-pressed="true"] { background: var(--fg); color: var(--bg); }
  .seg button:focus-visible { outline: 2px solid var(--accent); }
  h2 { font: 300 24px 'Manrope', sans-serif; letter-spacing: .24em; text-transform: uppercase; margin: 52px 0 18px; display: flex; gap: 14px; align-items: baseline; }
  h2 span { font: 500 12px 'JetBrains Mono', monospace; color: var(--muted); letter-spacing: 0; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); }
  figure { margin: 0; background: var(--bg); padding: 22px 16px 14px; display: grid; justify-items: center; gap: 12px; transition: background .3s; }
  figure svg { width: 100%; max-width: 132px; height: auto; color: var(--fg); }
  body[data-size="48"] figure svg { width: 48px; }
  body[data-size="24"] figure svg { width: 24px; }
  figcaption { display: grid; gap: 2px; text-align: center; font-size: 11px; }
  figcaption b { font-weight: 600; font-size: 13px; }
  figcaption code { font-family: 'JetBrains Mono', monospace; color: var(--muted); }
  .v-b, body.alt .v-a { display: none; }
  body.alt .v-b { display: block; }
</style>
<body data-size="full">
<main>
  <header>
    <div>
      <div class="ref">REF. CAL-24</div>
      <h1>CALIBRE</h1>
      <p>24 watchmaking icons in polished chrome with blued-steel hands and ruby jewels. Chrome for rich grounds, Line for any single colour.</p>
    </div>
    <div class="controls">
      <div class="seg" role="group" aria-label="Version">
        <button data-v="a" aria-pressed="true">${A.label}</button><button data-v="b" aria-pressed="false">${B.label}</button>
      </div>
      <div class="seg" role="group" aria-label="Size">
        <button data-s="full" aria-pressed="true">Full</button><button data-s="48" aria-pressed="false">48 px</button><button data-s="24" aria-pressed="false">24 px</button>
      </div>
    </div>
  </header>
  <div class="v-a">
${cells(A.key)}
  </div>
  <div class="v-b">
${cells(B.key)}
  </div>
</main>
<script>
  const press = (sel, b) => document.querySelectorAll(sel).forEach((x) => x.setAttribute('aria-pressed', x === b));
  document.querySelectorAll('[data-v]').forEach((b) => b.onclick = () => { document.body.classList.toggle('alt', b.dataset.v === 'b'); press('[data-v]', b); });
  document.querySelectorAll('[data-s]').forEach((b) => b.onclick = () => { document.body.dataset.size = b.dataset.s; press('[data-s]', b); });
</script>
</body>
`;

writeFileSync(join(root, 'preview.html'), `<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n${page}</html>\n`);
if (process.argv[2]) writeFileSync(process.argv[2], page);
console.log(`${icons.length} icons × 2 versions written`);
