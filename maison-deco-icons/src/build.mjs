// Builds the Maison icon set.
//   node src/build.mjs [preview-fragment-path]
// Writes gold/*.svg, mono/*.svg and preview.html next to src/.
// The optional argument also writes the preview without a doctype (for publishing as an artifact).

import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { icons, groups } from './icons.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

export const GOLD = [
  [0, '#f7e9bd'],
  [0.3, '#d6aa4e'],
  [0.48, '#fbf0c9'],
  [0.66, '#b5852f'],
  [1, '#e9c879'],
];
const RAIL = 9;   // full width of an inline stroke
const CORE = 3;   // open channel down its middle

const gradient = (id) =>
  `<linearGradient id="${id}" gradientUnits="userSpaceOnUse" x1="20" y1="10" x2="180" y2="190">` +
  GOLD.map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join('') +
  '</linearGradient>';

function svg(icon, version) {
  const id = `mai-${icon.slug}-`;
  const ink = version === 'gold' ? `url(#${id}gold)` : 'currentColor';
  const defs = version === 'gold' ? [gradient(`${id}gold`)] : [];
  const rails = icon.inline || [];
  const solid = icon.solid || [];
  const rules = (icon.rule || []).map((x) =>
    typeof x === 'string' ? { d: x, w: 2 } : Array.isArray(x) ? { d: x[0], w: x[1] } : { w: 2, ...x });

  const ruleEls = rules.map((x, i) => {
    let clip = '';
    if (x.clip) {
      defs.push(`<clipPath id="${id}clip${i}"><path d="${x.clip}"/></clipPath>`);
      clip = ` clip-path="url(#${id}clip${i})"`;
    }
    return `<path d="${x.d}" stroke-width="${x.w}"${clip}/>`;
  });

  // The hollow core: the rails are masked by themselves, white at full width and black at core width.
  if (rails.length) {
    defs.push(
      `<mask id="${id}hollow" maskUnits="userSpaceOnUse" x="-40" y="-40" width="280" height="280">` +
        `<g fill="none" stroke-linecap="round" stroke-linejoin="round">` +
        rails.map((d) => `<path d="${d}" stroke="#fff" stroke-width="${RAIL}"/>`).join('') +
        rails.map((d) => `<path d="${d}" stroke="#000" stroke-width="${CORE}"/>`).join('') +
        `</g></mask>`,
    );
  }

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <title>${icon.name}</title>
  <defs>
    ${defs.join('\n    ')}
  </defs>
  <g${icon.transform ? ` transform="${icon.transform}"` : ''}>
    <g id="solid" fill="${ink}">
      ${solid.map((d) => `<path d="${d}"/>`).join('\n      ')}
    </g>
    <g id="rule" fill="none" stroke="${ink}" stroke-linecap="round" stroke-linejoin="round">
      ${ruleEls.join('\n      ')}
    </g>
    <g id="inline" fill="none" stroke="${ink}" stroke-width="${RAIL}" stroke-linecap="round" stroke-linejoin="round"${rails.length ? ` mask="url(#${id}hollow)"` : ''}>
      ${rails.map((d) => `<path d="${d}"/>`).join('\n      ')}
    </g>
  </g>
</svg>
`;
}

const VERSIONS = [
  { key: 'gold', label: 'Gold', bg: '#0d2a22', fg: '#efe3c4', muted: '#8fa597', line: '#1f4237' },
  { key: 'mono', label: 'Mono', bg: '#f2ece0', fg: '#141414', muted: '#6e675c', line: '#ddd3c1' },
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

const inline = (out, key) =>
  out.replace(/<svg[^>]*>/, '<svg viewBox="0 0 200 200" role="img">').replace(/mai-/g, `${key}-`).replace(/ id="(solid|rule|inline)"/g, '');

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
const page = `<title>Maison Icons</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Italiana&family=Josefin+Sans:wght@300;400;600&display=swap" rel="stylesheet">
<style>
  :root { --bg: ${A.bg}; --fg: ${A.fg}; --muted: ${A.muted}; --line: ${A.line}; --gold: #d6aa4e; }
  body.alt { --bg: ${B.bg}; --fg: ${B.fg}; --muted: ${B.muted}; --line: ${B.line}; --gold: #141414; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--fg); font: 300 15px/1.5 'Josefin Sans', system-ui, sans-serif; transition: background .3s, color .3s; }
  main { max-width: 1120px; margin: 0 auto; padding: 56px 16px 80px; }
  header { display: flex; flex-wrap: wrap; gap: 24px; justify-content: space-between; align-items: end; border-bottom: 1px solid var(--line); padding-bottom: 28px; }
  h1 { font: 400 clamp(52px, 9vw, 96px)/.9 'Italiana', serif; margin: 0; letter-spacing: .14em; color: var(--gold); }
  header p { margin: 14px 0 0; color: var(--muted); max-width: 48ch; font-size: 14px; letter-spacing: .02em; }
  .controls { display: grid; gap: 10px; font-size: 12px; letter-spacing: .16em; text-transform: uppercase; }
  .seg { display: inline-flex; border: 1px solid var(--line); padding: 3px; }
  .seg button { all: unset; cursor: pointer; padding: 7px 14px; color: var(--muted); }
  .seg button[aria-pressed="true"] { background: var(--fg); color: var(--bg); }
  .seg button:focus-visible { outline: 2px solid var(--gold); }
  h2 { font: 400 30px 'Italiana', serif; letter-spacing: .14em; text-transform: uppercase; margin: 52px 0 18px; display: flex; gap: 14px; align-items: baseline; }
  h2 span { font: 400 12px 'Josefin Sans', sans-serif; color: var(--muted); letter-spacing: .1em; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); }
  figure { margin: 0; background: var(--bg); padding: 22px 16px 14px; display: grid; justify-items: center; gap: 12px; transition: background .3s; }
  figure svg { width: 100%; max-width: 132px; height: auto; color: var(--fg); }
  body[data-size="48"] figure svg { width: 48px; }
  body[data-size="24"] figure svg { width: 24px; }
  figcaption { display: grid; gap: 2px; text-align: center; font-size: 11px; }
  figcaption b { font-weight: 600; font-size: 13px; letter-spacing: .12em; text-transform: uppercase; }
  figcaption code { color: var(--muted); }
  .v-b, body.alt .v-a { display: none; }
  body.alt .v-b { display: block; }
</style>
<body data-size="full">
<main>
  <header>
    <div>
      <h1>MAISON</h1>
      <p>24 Art Deco fine-dining icons, drawn in hollow inline gold. Gold for dark lacquer grounds, Mono for any single colour.</p>
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
