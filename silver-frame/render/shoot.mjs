// node shoot.mjs   -> renders preview PNGs into ../out/
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');  // preinstalled or local
import { createServer } from 'http';
import { readFile } from 'fs/promises';
import { extname, join, resolve } from 'path';

const root = resolve(import.meta.dirname, '..');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.stl': 'application/octet-stream' };
const server = createServer(async (req, res) => {
  try {
    const p = join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
    const body = await readFile(p);
    res.writeHead(200, { 'content-type': types[extname(p)] || 'application/octet-stream' });
    res.end(body);
  } catch { res.writeHead(404); res.end(); }
}).listen(0);
const port = server.address().port;

const shots = JSON.parse(process.argv[2] || 'null') || [
  { name: 'render_front', stl: 'out/_render_assembled.stl', w: 1800, h: 1000 },
  { name: 'render_top_closeup', stl: 'out/_render_assembled.stl', w: 1600, h: 900,
    cam: '190.5,110,95', look: '190.5,178,12', fov: 32 },
  { name: 'render_corner_closeup', stl: 'out/_render_assembled.stl', w: 1600, h: 1000,
    cam: '60,95,110', look: '45,160,12', fov: 34 },
  { name: 'render_ornament_scroll', stl: 'out/ornament_scroll_A.stl', w: 1800, h: 500, fov: 20 },
  { name: 'render_ornament_rosette', stl: 'out/ornament_rosette.stl', w: 800, h: 800, fov: 20 },
  { name: 'render_ornament_center', stl: 'out/ornament_center.stl', w: 1800, h: 600, fov: 20 },
];
const browser = await chromium.launch();
for (const s of shots) {
  const page = await browser.newPage({ viewport: { width: s.w, height: s.h } });
  page.on('console', m => console.log(s.name, m.text()));
  page.on('pageerror', e => console.log(s.name, 'ERR', e.message));
  const qs = new URLSearchParams({ ...s, stl: '../' + s.stl });
  await page.goto(`http://localhost:${port}/render/view.html?${qs}`);
  await page.waitForFunction(() => window.done, null, { timeout: 300000 });
  await page.locator('canvas').screenshot({ path: join(root, 'out', s.name + '.png') });
  console.log('wrote', s.name);
  await page.close();
}
await browser.close();
server.close();
