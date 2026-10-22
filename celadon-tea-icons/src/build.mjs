// Builds the Celadon icon set.
//   node src/build.mjs [preview-fragment-path]
// Writes glazed/*.svg, line/*.svg and preview.html next to src/.
// The optional argument also writes the preview without a doctype (for publishing as an artifact).

import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { icons, groups } from './icons.mjs';
import { GLAZES, CLAY, OUTLINE } from './glazes.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

const rng = (seed) => () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
const speckleField = (seed) => {
  const rand = rng(seed);
  let d = '';
  for (let i = 0; i < 170; i++) {
    const x = (rand() * 200).toFixed(1), y = (rand() * 200).toFixed(1), rr = (0.6 + rand() * 0.9).toFixed(2);
    d += `M${x} ${y}m-${rr} 0a${rr} ${rr} 0 1 0 ${rr * 2} 0a${rr} ${rr} 0 1 0 -${rr * 2} 0`;
  }
  return d;
};

function svg(icon, version, prefix = 'cel') {
  const id = `${prefix}-${icon.slug}-`;
  const glazed = version === 'glazed';
  const defs = [];
  const used = new Set();
  let n = 0;
  const clipAttr = (d) => {
    if (!d) return '';
    const cid = `${id}c${n++}`;
    defs.push(`<clipPath id="${cid}"><path d="${d}"/></clipPath>`);
    return ` clip-path="url(#${cid})"`;
  };
  const fillOf = (g) => { used.add(g); return `url(#${id}${g})`; };

  const body = icon.layers.map((L) => {
    const { t, d, g, w } = L;
    if (glazed) {
      switch (t) {
        case 'clay': {
          const c = clipAttr(d);
          return `<path d="${d}" fill="url(#${id}clay)"/><path d="${speckleField(icon.slug.length * 97)}" fill="#5a3d26" fill-opacity=".5"${c}/>`;
        }
        case 'glaze': return `<g${clipAttr(L.clip)}><path d="${d}" fill="${fillOf(g)}"/></g>`;
        case 'drip': return `<path d="${d}" stroke="${OUTLINE}" stroke-opacity=".45" stroke-width="1.6"${clipAttr(L.clip)}/>`;
        case 'shine': return `<path d="${d}" stroke="#fff" stroke-opacity=".78" stroke-width="${w}"/>`;
        case 'paint': return `<path d="${d}" stroke="${GLAZES[g][1]}" stroke-width="${w}"${clipAttr(L.clip)}/>`;
        case 'paintBack':
          return `<path d="${d}" stroke="${OUTLINE}" stroke-width="${w + 3}"/><path d="${d}" stroke="${GLAZES[g][1]}" stroke-width="${w}"/>` +
            `<path d="${d}" stroke="${GLAZES[g][0]}" stroke-width="${(w * 0.3).toFixed(1)}" transform="translate(-.6 -.8)"/>`;
        case 'smoke': return `<path d="${d}" stroke="#a8a29a" stroke-opacity=".85" stroke-width="${w}"/>`;
        case 'out': return `<path d="${d}" stroke="${OUTLINE}" stroke-width="${w}"/>`;
        case 'line': return `<path d="${d}" stroke="${OUTLINE}" stroke-width="${w}"${clipAttr(L.clip)}/>`;
      }
    } else {
      switch (t) {
        case 'clay': case 'shine': return '';
        case 'glaze': return `<path d="${d}" stroke-width="1.6"${clipAttr(L.clip)}/>`;
        case 'drip': return `<path d="${d}" stroke-width="1.6"${clipAttr(L.clip)}/>`;
        case 'paint': return `<path d="${d}" stroke-width="${Math.min(w, 2.4)}"${clipAttr(L.clip)}/>`;
        case 'paintBack': return `<path d="${d}" stroke-width="3"/>`;
        case 'smoke': return `<path d="${d}" stroke-width="1.8"/>`;
        case 'out': case 'line': return `<path d="${d}" stroke-width="${w}"${clipAttr(L.clip)}/>`;
      }
    }
    throw new Error(`unknown layer ${t} in ${icon.slug}`);
  }).filter(Boolean);

  if (glazed) {
    defs.unshift(
      `<linearGradient id="${id}clay" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${CLAY[0]}"/><stop offset="1" stop-color="${CLAY[1]}"/></linearGradient>`,
      ...[...used].map((g) => `<radialGradient id="${id}${g}" cx=".34" cy=".28" r=".9"><stop offset="0" stop-color="${GLAZES[g][0]}"/><stop offset=".55" stop-color="${GLAZES[g][1]}"/><stop offset="1" stop-color="${GLAZES[g][2]}"/></radialGradient>`),
    );
  }

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <title>${icon.name}</title>
  <defs>
    ${defs.join('\n    ')}
  </defs>
  <g fill="none" stroke="${glazed ? 'none' : 'currentColor'}" stroke-linecap="round" stroke-linejoin="round"${icon.transform ? ` transform="${icon.transform}"` : ''}>
    ${body.join('\n    ')}
  </g>
</svg>
`;
}

const VERSIONS = [
  { key: 'glazed', label: 'Glazed', bg: '#efe8dc', fg: '#2b211a', muted: '#857563', line: '#ddd2c0' },
  { key: 'line', label: 'Line', bg: '#f7f3ec', fg: '#2b211a', muted: '#857563', line: '#e4dccd' },
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

const inline = (out, key) => out.replace(/<svg[^>]*>/, '<svg viewBox="0 0 200 200" role="img">').replace(/cel-/g, `${key}-`);

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
const page = `<title>Celadon Icons</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;600&family=Zen+Kaku+Gothic+New:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root { --bg: ${A.bg}; --fg: ${A.fg}; --muted: ${A.muted}; --line: ${A.line}; --seal: #c0392b; }
  body.alt { --bg: ${B.bg}; --fg: ${B.fg}; --muted: ${B.muted}; --line: ${B.line}; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--fg); font: 400 15px/1.6 'Zen Kaku Gothic New', system-ui, sans-serif; transition: background .3s; }
  main { max-width: 1120px; margin: 0 auto; padding: 56px 16px 80px; }
  header { display: flex; flex-wrap: wrap; gap: 24px; justify-content: space-between; align-items: end; border-bottom: 1px solid var(--line); padding-bottom: 28px; }
  .title { display: flex; align-items: center; gap: 18px; }
  h1 { font: 400 clamp(52px, 9vw, 92px)/.95 'Shippori Mincho', serif; margin: 0; letter-spacing: .08em; }
  .seal { width: 54px; height: 54px; border-radius: 8px; background: var(--seal); color: #fff; display: grid; place-items: center; font: 600 28px 'Shippori Mincho', serif; }
  header p { margin: 14px 0 0; color: var(--muted); max-width: 48ch; font-size: 14px; }
  .controls { display: grid; gap: 10px; font-size: 13px; }
  .seg { display: inline-flex; border: 1px solid var(--line); border-radius: 999px; padding: 3px; background: rgba(255,255,255,.4); }
  .seg button { all: unset; cursor: pointer; padding: 6px 14px; border-radius: 999px; color: var(--muted); }
  .seg button[aria-pressed="true"] { background: var(--fg); color: var(--bg); }
  .seg button:focus-visible { outline: 2px solid var(--seal); }
  h2 { font: 400 28px 'Shippori Mincho', serif; letter-spacing: .06em; margin: 52px 0 18px; display: flex; gap: 14px; align-items: baseline; }
  h2 span { font: 400 12px 'Zen Kaku Gothic New', sans-serif; color: var(--muted); }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); }
  figure { margin: 0; background: var(--bg); padding: 22px 16px 14px; display: grid; justify-items: center; gap: 12px; transition: background .3s; }
  figure svg { width: 100%; max-width: 132px; height: auto; color: var(--fg); }
  body[data-size="48"] figure svg { width: 48px; }
  body[data-size="24"] figure svg { width: 24px; }
  figcaption { display: grid; gap: 2px; text-align: center; font-size: 11px; }
  figcaption b { font: 600 16px 'Shippori Mincho', serif; }
  figcaption code { color: var(--muted); }
  .v-b, body.alt .v-a { display: none; }
  body.alt .v-b { display: block; }
</style>
<body data-size="full">
<main>
  <header>
    <div>
      <div class="title"><h1>Celadon</h1><span class="seal" aria-hidden="true">茶</span></div>
      <p>24 tea-ceremony icons in glazed ceramic: celadon, tenmoku, shino and cobalt glazes over speckled clay. Glazed in full colour, Line in any single colour.</p>
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
