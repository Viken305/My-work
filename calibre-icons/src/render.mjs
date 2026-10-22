// Renders Calibre icons to SVG in two versions: chrome (polished steel) and line (one colour).
// Shared by build.mjs and dribbble/build-shots.mjs.

// Polished steel: hard reflection bands, like chrome catching a studio softbox.
export const CHROME = [[0, '#ffffff'], [0.16, '#c9d0d9'], [0.3, '#6b7584'], [0.38, '#2a313b'], [0.46, '#e8edf2'], [0.62, '#a3acb8'], [0.78, '#4a5361'], [0.9, '#cfd6de'], [1, '#f5f7f9']];
export const BLUED = [[0, '#9cc1ff'], [0.3, '#3f6fd8'], [0.5, '#163587'], [0.72, '#4b7de6'], [1, '#12286a']];
export const RUBY = [[0, '#ff9aa8'], [0.45, '#d4143a'], [1, '#5c0418']];
export const SAND = [[0, '#fff1c9'], [0.5, '#e0b864'], [1, '#9d7330']];
export const SKY = [[0, '#2b56b8'], [1, '#0b1a4a']];
export const RIM = '#0d1015';

const stops = (list) => list.map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join('');
export const gradients = (id) => [
  `<linearGradient id="${id}chrome" gradientUnits="userSpaceOnUse" x1="0" y1="14" x2="34" y2="190">${stops(CHROME)}</linearGradient>`,
  `<linearGradient id="${id}plate" gradientUnits="userSpaceOnUse" x1="10" y1="0" x2="190" y2="200">${stops(CHROME)}</linearGradient>`,
  `<linearGradient id="${id}blue" gradientUnits="userSpaceOnUse" x1="20" y1="10" x2="180" y2="190">${stops(BLUED)}</linearGradient>`,
  `<radialGradient id="${id}ruby" cx=".35" cy=".3" r=".8">${stops(RUBY)}</radialGradient>`,
  `<linearGradient id="${id}sand" x1="0" y1="0" x2="1" y2="1">${stops(SAND)}</linearGradient>`,
  `<linearGradient id="${id}sky" x1="0" y1="0" x2="0" y2="1">${stops(SKY)}</linearGradient>`,
  `<radialGradient id="${id}glass" cx=".3" cy=".25" r=".9"><stop offset="0" stop-color="#f4f8ff" stop-opacity=".5"/><stop offset=".55" stop-color="#9fbde6" stop-opacity=".14"/><stop offset="1" stop-color="#7fa6d9" stop-opacity=".04"/></radialGradient>`,
];

export function chromeLayer([type, d, w], id) {
  const u = (g) => `url(#${id}${g})`;
  switch (type) {
    case 'tube':
      return `<path d="${d}" stroke="${RIM}" stroke-width="${w + 2.4}"/>` +
        `<path d="${d}" stroke="${u('chrome')}" stroke-width="${w}"/>` +
        `<path d="${d}" stroke="#fff" stroke-width="${Math.max(0.8, w * 0.22).toFixed(2)}" stroke-opacity=".8" transform="translate(-.5 -.7)"/>`;
    case 'blue':
      return `<path d="${d}" stroke="#08112e" stroke-width="${w + 2}"/>` +
        `<path d="${d}" stroke="${u('blue')}" stroke-width="${w}"/>` +
        `<path d="${d}" stroke="#d6e6ff" stroke-width="${Math.max(0.6, w * 0.2).toFixed(2)}" stroke-opacity=".7" transform="translate(-.4 -.6)"/>`;
    case 'fine':
      return `<path d="${d}" stroke="${u('chrome')}" stroke-width="${w}"/>`;
    case 'steel':
      return `<path d="${d}" fill="${u('plate')}" stroke="${RIM}" stroke-width="1.6"/>`;
    case 'ruby':
      return `<path d="${d}" fill="${u('ruby')}" stroke="#3a0610" stroke-width="1.2"/>`;
    case 'sand':
      return w ? `<path d="${d}" stroke="${u('sand')}" stroke-width="${w}"/>` : `<path d="${d}" fill="${u('sand')}" stroke="#3b2a10" stroke-width="1"/>`;
    case 'sky':
      return `<path d="${d}" fill="${u('sky')}"/>`;
    case 'glass':
      return `<path d="${d}" fill="${u('glass')}"/>`;
    default:
      throw new Error(`unknown layer ${type}`);
  }
}

export function lineLayer([type, d, w]) {
  switch (type) {
    case 'tube': case 'blue': case 'fine':
      return `<path d="${d}" stroke-width="${w}"/>`;
    case 'steel':
      return `<path d="${d}" stroke-width="2.4"/>`;
    case 'sand':
      return w ? `<path d="${d}" stroke-width="${w}"/>` : `<path d="${d}" fill="currentColor"/>`;
    case 'ruby':
      return w === 'outline' ? `<path d="${d}" stroke-width="2.4"/>` : `<path d="${d}" fill="currentColor"/>`;
    case 'sky': case 'glass':
      return '';
    default:
      throw new Error(`unknown layer ${type}`);
  }
}

export function svg(icon, version) {
  const id = `cal-${icon.slug}-`;
  const chrome = version === 'chrome';
  const body = icon.layers.map((l) => (chrome ? chromeLayer(l, id) : lineLayer(l))).filter(Boolean);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <title>${icon.name}</title>
${chrome ? `  <defs>\n    ${gradients(id).join('\n    ')}\n  </defs>\n` : ''}  <g fill="none" stroke="${chrome ? 'none' : 'currentColor'}" stroke-linecap="round" stroke-linejoin="round"${icon.transform ? ` transform="${icon.transform}"` : ''}>
    ${body.join('\n    ')}
  </g>
</svg>
`;
}
