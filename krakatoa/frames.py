"""Style frames for approval.

  python3 frames.py  -> out/frame_1_map.png ... out/frame_4_sunset.png + out/style_frames.png (contact sheet)
"""
import math, os, sys

import numpy as np
import skia
from PIL import Image

from cyan import *  # noqa: F401,F403

OUT = os.path.join(HERE, "out")
KRAKATOA = (105.42, -6.10)
RODRIGUES = (63.42, -19.72)
LONDON = (-0.13, 51.5)


# ---------------------------------------------------------------- FIG 1: the map, the ring reaching Rodrigues
def map_frame(c, t):
    paper(c)
    proj = Ortho.fit(KRAKATOA, (790, 540), RODRIGUES, (250, 1100), 86, -12)
    graticule(c, proj, 0.8, step=10)
    engraved_land(c, land_path(proj, "indian_ocean"), hatch=6, key="map")
    kx, ky, _ = proj(*KRAKATOA)
    rx, ry, _ = proj(*RODRIGUES)
    R = math.hypot(rx - kx, ry - ky)
    for k, f in enumerate((0.38, 0.62, 0.84)):
        ring(c, kx, ky, R * f, SULFUR, 70 + k * 25, 1.6, fringe=False, trail=0)
    ring(c, kx, ky, R * 1.004, SULFUR, 255, 3.2)
    light(c, kx, ky, 90, LAVA, 160)
    dim_line(c, kx - 30, ky + 40, rx + 34, ry - 40, "4,800 KM", 255, PAPER, 28)
    pin(c, kx, ky, "KRAKATOA", "10:02 AM", side=1)
    pin(c, rx, ry, "RODRIGUES", "~4 HOURS LATER", side=1, rgb=SULFUR)
    fig(c, 1, "THE INDIAN OCEAN, 27 AUG 1883", 70, 290)
    label(c, "“the distant roar", rx + 28, ry + 100, 30, "serif", PAPER, 230)
    label(c, "of heavy guns”", rx + 40, ry + 138, 30, "serif", PAPER, 230)
    caption(c, ["heard", "4,800 km", "away"], t, [0.0, 0.22, 0.62], emph={0: SULFUR})


# ---------------------------------------------------------------- FIG 2: section through the island, BOOM
ASH = Ash(5000, 7, (0, 0, W, 1100))


def island_path(sea=1040):
    """Section: a broad, ragged cone with its top blown open; flanks run under the sea to the seabed."""
    rng = np.random.default_rng(21)
    # three cones as in 1883: Rakata (tallest, left), Danan (the vent, centre), Perbuwatan (low, right)
    prof = [(-40, sea + 170), (60, sea + 100), (140, sea + 20), (200, sea - 90), (255, sea - 210), (300, sea - 300),
            (340, sea - 285), (395, sea - 200), (440, sea - 215), (470, sea - 238), (505, sea - 172), (535, sea - 152),
            (590, sea - 152), (625, sea - 205), (660, sea - 242), (720, sea - 180), (780, sea - 126), (830, sea - 152),
            (865, sea - 160), (905, sea - 110), (960, sea - 25), (1040, sea + 80), (1120, sea + 150)]
    p = skia.Path()
    p.moveTo(*prof[0])
    for (x0, y0), (x1, y1) in zip(prof, prof[1:]):
        for k in range(1, 7):   # small ragged steps between the key points
            u = k / 6
            jit = 0 if k == 6 else rng.normal(0, 4)
            p.lineTo(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + jit)
    p.lineTo(1120, 1700)
    p.lineTo(-40, 1700)
    p.close()
    return p


def ash_column(c, x, y, t):
    """Billowing column: overlapping puffs with soft but readable edges, lit red-orange from the vent below."""
    rng = np.random.default_rng(5)
    puffs = []
    for k in range(90):
        u = (k / 90) ** 0.8
        spread = 26 + u * 150 + (u > 0.75) * (u - 0.75) * 900   # widens into a mushroom near the top
        puffs.append((x + rng.normal(0, spread * 0.45), y - u * 600 + rng.normal(0, 14), 36 + u * 90 + rng.random() * 30, u))
    for px, py, r, u in sorted(puffs, key=lambda p: -p[3]):
        c.drawCircle(px, py, r, paint(mix((16, 20, 32), (34, 34, 46), rng.random()), 245, sigma=r * 0.14))
        c.drawCircle(px - r * 0.25, py - r * 0.35, r * 0.6, paint(FADED, 22, sigma=r * 0.3, plus=True))
        if u < 0.6:
            c.drawCircle(px, py + r * 0.45, r * 0.65, paint(mix(SUN_O, LAVA, u * 1.6), 120 * (1 - u / 0.6), sigma=r * 0.4, plus=True))


def boom_frame(c, t):
    paper(c)
    sea, vx, vy = 1040, 562, 885
    light(c, vx, vy - 120, 1000, LAVA, 110)
    for k, r in enumerate((330, 560, 800, 1060)):
        ring(c, vx, vy - 40, r, SULFUR, 255 - k * 50, 3.4 - k * 0.5, fringe=k == 0)
    for k in range(46):   # debris: glowing streaks with heads
        ang = math.radians(198 + k * 3.2 + math.sin(k * 7.3) * 5)
        r0, r1 = 140 + (k * 37) % 120, 360 + (k * 53) % 420
        x0, y0 = vx + math.cos(ang) * r0, vy - 60 + math.sin(ang) * r0
        x1, y1 = vx + math.cos(ang) * r1, vy - 60 + math.sin(ang) * r1
        pth = skia.Path()
        pth.moveTo(x0, y0)
        pth.lineTo(x1, y1)
        c.drawPath(pth, paint(SUN_O, 90, sigma=2, plus=True, stroke=2.2))
        c.drawCircle(x1, y1, 3 + k % 3, paint(HOT, 220, plus=True))
    ash_column(c, vx, vy - 40, t)
    light(c, vx, vy - 10, 300, SUN_O, 220)
    light(c, vx, vy, 120, HOT, 255)
    # ocean: engraved horizontal lines either side of the flanks
    c.drawRect(skia.Rect.MakeLTRB(0, sea, W, 1700), paint(mix(NIGHT, PRUSSIAN, 0.7), 240))
    for i, y in enumerate(range(sea + 6, 1700, 9)):
        c.drawLine(0, y, W, y, paint(PAPER, 40 - min(28, i * 0.4), stroke=1.0))
    c.drawLine(0, sea, W, sea, paint(PAPER, 210, stroke=2))
    isl = island_path()
    c.drawPath(isl, paint(mix(PRUSSIAN, PAPER, 0.1)))
    c.save()
    c.clipPath(isl, doAntiAlias=True)
    for i in range(-H, W + H, 7):
        c.drawLine(i, 0, i - H * 0.5, H, paint(PAPER, 46, stroke=1.0))
    for k in range(6):   # strata
        pth = skia.Path()
        pth.moveTo(-40, 1150 + k * 70)
        pth.cubicTo(300, 1090 + k * 75, 800, 1110 + k * 66, 1120, 1150 + k * 72)
        c.drawPath(pth, paint(PAPER, 80, stroke=1.2))
    conduit = skia.Path()
    conduit.moveTo(vx, vy - 10)
    conduit.cubicTo(vx + 20, 960, vx - 30, 1060, vx - 10, 1160)
    c.drawPath(conduit, paint(LAVA, 200, sigma=12, plus=True, stroke=40))
    c.drawPath(conduit, paint(SUN_O, 230, plus=True, stroke=10))
    c.drawOval(skia.Rect.MakeXYWH(vx - 170, 1130, 320, 90), paint(LAVA, 220, sigma=22, plus=True))
    c.drawOval(skia.Rect.MakeXYWH(vx - 110, 1150, 200, 50), paint(SUN_O, 230, sigma=8, plus=True))
    c.restore()
    c.drawPath(isl, paint(PAPER, 230, stroke=1.8))
    label(c, "SEA LEVEL", 1040, sea - 14, 20, "mono", PAPER, 200, "right", 0.14)
    label(c, "MAGMA", vx + 170, 1185, 20, "mono", SUN_O, 230, "left", 0.2)
    fig(c, 2, "SECTION THROUGH KRAKATOA, 10:02 AM", 70, 300)
    # BOOM: slammed in, shaking, the last letter already blowing apart into ash
    size = 250
    f = font("black", size)
    x = W / 2 - width("BOOM", "black", size) / 2
    rng = np.random.default_rng(2)
    by = 1420
    c.drawRect(skia.Rect.MakeLTRB(0, by - size, W, by + 70), paint(NIGHT, 120, sigma=60))
    for j, ch in enumerate("BOOM"):
        dx, dy = rng.normal(0, 6, 2)
        rot = rng.normal(0, 2.5)
        c.save()
        c.translate(x + dx, by + dy)
        c.rotate(rot)
        c.drawString(ch, 8, 14, f, paint((0, 0, 0), 170, sigma=16))
        if j == 3:
            c.clipRect(skia.Rect.MakeLTRB(-20, -size, f.measureText(ch) * 0.55, 60))
        c.drawString(ch, 0, 0, f, paint(SULFUR, 255))
        c.restore()
        x += f.measureText(ch)
    x0 = x - f.measureText("M") * 0.5
    for k in range(900):   # the dissolving edge: particles streaming off to the right
        u = rng.random() ** 1.6
        px = x0 + u * 380 + rng.normal(0, 10)
        py = by - size * 0.72 + rng.random() * size * 0.74 - u * 60 * rng.random()
        c.drawCircle(px, py, (1 - u) * 3.6 + 0.6, paint(SULFUR if k % 5 else HOT, 230 * (1 - u) + 20, plus=k % 5 == 0))


# ---------------------------------------------------------------- FIG 3: the globe, the wave going round
def globe_frame(c, t):
    paper(c)
    cx, cy, R = 540, 900, 410
    proj = Ortho(55, 18, R, cx, cy, -8)
    sh = skia.GradientShader.MakeRadial((cx - R * 0.35, cy - R * 0.4), R * 1.5,
                                        [col(mix(PRUSSIAN, PAPER, 0.1)), col(NIGHT)], [0, 1])
    c.drawCircle(cx, cy, R, skia.Paint(AntiAlias=True, Shader=sh))
    c.save()
    disc = skia.Path()
    disc.addCircle(cx, cy, R)
    c.clipPath(disc, doAntiAlias=True)
    graticule(c, proj, 1.0, 15)
    engraved_land(c, land_path(proj, "world", 0.0), hatch=6, water_lines=(6, 13), key="globe")
    c.restore()
    c.drawCircle(cx, cy, R, paint(PAPER, 200, stroke=2.0))
    c.drawCircle(cx, cy, R + 6, paint(PAPER, 50, sigma=8, stroke=10))
    kx, ky, _ = proj(*KRAKATOA)
    light(c, kx, ky, 60, LAVA, 200)
    sphere_ring(c, proj, *KRAKATOA, 0.55, SULFUR, 90, 1.6)
    sphere_ring(c, proj, *KRAKATOA, 1.05, SULFUR, 150, 2.0)
    sphere_ring(c, proj, *KRAKATOA, 1.72, SULFUR, 255, 3.4)
    lx, ly, _ = proj(*LONDON)
    pin(c, lx, ly, "LONDON", "WAVE ARRIVES ~10 H LATER", side=1, size=26)
    pin(c, kx, ky, "KRAKATOA", side=-1, size=26)
    barograph(c, 120, 250, 560, 150, 1.0, 0.56, title="BAROMETER, LONDON", n=4)
    label(c, "3–4×", 920, 380, 64, "mono_bold", SULFUR, 255, "right")
    label(c, "AROUND EACH WAY", 920, 412, 18, "mono", FADED, 255, "right", 0.14)
    caption(c, ["around", "the", "planet"], t, [0.0, 0.18, 0.34], y=1440, emph={2: SULFUR})


# ---------------------------------------------------------------- FIG 4: blood-red sunsets
ASH2 = Ash(3500, 9, (0, 0, W, 1100))


def sunset_frame(c, t):
    paper(c)
    hz = 1060
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, hz)], [col(NIGHT, 0), col(SUN_V, 170), col(LAVA, 225), col(SUN_O, 255)],
                                         [0.0, 0.4, 0.82, 1.0])
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, hz), skia.Paint(Shader=sky))
    light(c, 640, hz - 30, 700, LAVA, 120)
    for y in range(240, hz, 6):   # etched sky: the plate's horizontal engraving lines
        c.drawLine(0, y, W, y, paint(NIGHT, 26 + 20 * (1 - y / hz), stroke=1.4))
    c.drawCircle(640, hz - 40, 92, paint(HOT, 255))
    light(c, 640, hz - 40, 280, SUN_O, 200)
    rng = np.random.default_rng(8)
    for k, (y0, a0) in enumerate(((360, 120), (520, 150), (700, 130), (860, 110))):   # bands of ash cloud, lit from below
        pth = skia.Path()
        pth.moveTo(-50, y0)
        for x in range(-50, W + 60, 30):
            pth.lineTo(x, y0 + math.sin(x * 0.009 + k * 2) * 30 + math.sin(x * 0.027 + k) * 10)
        c.drawPath(pth, paint((40, 14, 38), a0, sigma=18, stroke=46))
        c.drawPath(pth, paint(SUN_O, 90, sigma=1.5, plus=True, stroke=1.4))
    ASH2.draw(c, 3.0, (60, 20, 30), 0.6, tint=(50, 16, 30))
    # sea: engraved lines and a broken glitter path under the sun
    c.drawRect(skia.Rect.MakeLTRB(0, hz, W, H), paint(NIGHT, 245))
    for y in range(hz + 6, 1760, 7):
        d = (y - hz) / 700
        c.drawLine(0, y, W, y, paint(PAPER, 28 * (1 - d), stroke=1.0))
        spread = 30 + d * 380
        for _ in range(int(6 + 10 * (1 - d))):
            x = 640 + rng.normal(0, spread * 0.45)
            q = math.exp(-((x - 640) / spread) ** 2)
            ln = (8 + rng.random() * 40) * (1 - d * 0.5)
            c.drawLine(x - ln / 2, y, x + ln / 2, y, paint(mix(HOT, SUN_O, d * 2), 255 * q * (1 - d) ** 1.4, plus=True, stroke=1.8))
    c.drawLine(0, hz, W, hz, paint(PAPER, 160, stroke=1.4))
    ship(c, 270, hz + 4, 1.0)
    fig(c, 7, "SUNSET, ALL AROUND THE WORLD, 1883", 70, 300, size=20)
    caption(c, ["skies", "turned", "blood red"], t, [0.0, 0.2, 0.45], y=1440, emph={2: LAVA})


def ship(c, x, y, s):
    """Three-masted barque silhouette."""
    p = skia.Path()
    p.moveTo(x - 90 * s, y - 22 * s)
    p.lineTo(x + 100 * s, y - 22 * s)
    p.lineTo(x + 80 * s, y)
    p.lineTo(x - 76 * s, y)
    p.close()
    for mx, mh in ((-50, 150), (8, 180), (62, 140)):
        p.addRect(skia.Rect.MakeXYWH(x + (mx - 2) * s, y - (22 + mh) * s, 4 * s, mh * s))
        for k in range(3):
            w = (46 - k * 10) * s
            yy = y - (40 + k * mh * 0.3) * s
            p.addRect(skia.Rect.MakeXYWH(x + mx * s - w / 2, yy - mh * 0.24 * s, w, mh * 0.22 * s))
    c.drawPath(p, paint((14, 6, 18), 245))


FRAMES = [("frame_1_map", map_frame, 1.1), ("frame_2_boom", boom_frame, 1.0),
          ("frame_3_globe", globe_frame, 1.2), ("frame_4_sunset", sunset_frame, 1.4)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    paths = []
    for name, fn, t in FRAMES:
        p = os.path.join(OUT, f"{name}.png")
        paths.append(p)
        if only and not any(o in name for o in only):
            continue
        kw = dict(flash=0.06, split=0.3) if "boom" in name else {}
        Image.fromarray(render(fn, t, samples=1, **kw)).save(p)
        print(p)
    sheet = Image.new("RGB", (4 * 540 + 5 * 24, 960 + 48), (6, 16, 31))
    for i, p in enumerate(paths):
        if os.path.exists(p):
            sheet.paste(Image.open(p).resize((540, 960), Image.LANCZOS), (24 + i * 564, 24))
    sheet.save(os.path.join(OUT, "style_frames.png"))
