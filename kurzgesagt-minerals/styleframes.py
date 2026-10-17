"""Style frames: one finished key frame per upcoming scene, to lock the look before animating.

  python3 styleframes.py          # -> out/styleframes/NN_name.png + board.png
  python3 styleframes.py 3 4      # only frames 3 and 4
"""
import math, os, sys

import numpy as np
import skia
from PIL import Image, ImageDraw, ImageFont

from engine import *  # noqa: F401,F403

OUT = os.path.join(HERE, "out", "styleframes")
T = 2.0  # idle-animation time used for every still
SI = (150, 110, 255)   # silicon atom
OX = (255, 92, 92)     # oxygen atom
CARBON = (52, 46, 70)


# ---------------------------------------------------------------- shared bits
def title_card(c, n, name, rgb, icon):
    x, y = 70, 60
    w = 120 + font(46, 800).measureText(name) + 40
    soft_shadow(c, rrect(x, y, w, 110, 55), 6, 10, 14, 90)
    c.drawRRect(rrect(x, y, w, 110, 55), fill((16, 14, 44), 220))
    c.drawRRect(rrect(x, y, w, 110, 55), stroke(rgb, 3, 200))
    c.drawCircle(x + 55, y + 55, 38, fill(rgb))
    icon(c, x + 55, y + 55, 22)
    text(c, f"RECIPE {n}", x + 112, y + 44, 22, rgb, 255, 800, "left", spacing=4)
    text(c, name, x + 110, y + 90, 46, WHITE, 255, 800, "left", spacing=3)


def icon_flame(c, x, y, s):
    p = skia.Path()
    p.moveTo(x, y - s * 1.1)
    p.cubicTo(x + s * 0.9, y - s * 0.2, x + s * 0.8, y + s * 0.9, x, y + s * 0.9)
    p.cubicTo(x - s * 0.8, y + s * 0.9, x - s * 0.9, y - s * 0.1, x - s * 0.2, y - s * 0.5)
    p.cubicTo(x - s * 0.1, y - s * 0.1, x + s * 0.1, y - s * 0.5, x, y - s * 1.1)
    c.drawPath(p, fill(INK))
    c.drawCircle(x, y + s * 0.4, s * 0.35, fill(YELLOW))


def icon_drop(c, x, y, s):
    p = skia.Path()
    p.moveTo(x, y - s * 1.1)
    p.cubicTo(x + s * 0.4, y - s * 0.5, x + s * 0.85, y, x + s * 0.85, y + s * 0.3)
    p.cubicTo(x + s * 0.85, y + s * 1.1, x - s * 0.85, y + s * 1.1, x - s * 0.85, y + s * 0.3)
    p.cubicTo(x - s * 0.85, y, x - s * 0.4, y - s * 0.5, x, y - s * 1.1)
    c.drawPath(p, fill(INK))
    c.drawCircle(x - s * 0.3, y + s * 0.35, s * 0.18, fill(WHITE, 200))


def icon_down(c, x, y, s):
    c.drawPath(poly([(x - s * 0.35, y - s), (x + s * 0.35, y - s), (x + s * 0.35, y), (x + s * 0.8, y),
                     (x, y + s), (x - s * 0.8, y), (x - s * 0.35, y)]), fill(INK))


def icon_sprout(c, x, y, s):
    c.drawLine(x, y + s, x, y - s * 0.2, stroke(INK, s * 0.25))
    c.drawOval(skia.Rect.MakeXYWH(x - s * 1.0, y - s * 0.9, s * 0.95, s * 0.55), fill(INK))
    c.drawOval(skia.Rect.MakeXYWH(x + s * 0.05, y - s * 1.2, s * 0.95, s * 0.55), fill(INK))


def prism(c, x, y, L, w, ang, rgb, a=255, tip=0.55, both=False, glow_a=0):
    """Elongated hexagonal crystal seen from the side: light/dark facets + pointed tip(s)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    tl = w * tip * 2
    b0 = tl if both else 0
    if glow_a:
        c.drawRRect(rrect(-w, -w * 2, L + 2 * w, w * 4, w * 2), blur(fill(rgb, glow_a), w * 1.5))
    if both:
        top = [(tl, -w), (L - tl, -w), (L, 0), (0, 0)]
        bot = [(0, 0), (L, 0), (L - tl, w), (tl, w)]
    else:
        top = [(0, -w), (L - tl, -w), (L, 0), (0, 0)]
        bot = [(0, 0), (L, 0), (L - tl, w), (0, w)]
    c.drawPath(poly(top), fill(lighten(rgb, 0.45), a))
    c.drawPath(poly(bot), fill(darken(rgb, 0.12), a))
    c.drawPath(poly([(b0, -w * 0.15), (L - tl * 0.3, -w * 0.15), (L - tl * 0.25, 0), (b0, 0)]), fill(WHITE, 0.45 * a))
    c.drawLine(L - tl, -w, L - tl, w, stroke(darken(rgb, 0.2), max(1, w * 0.05), 0.5 * a))
    if both:
        c.drawLine(tl, -w, tl, w, stroke(darken(rgb, 0.2), max(1, w * 0.05), 0.5 * a))
    outline = poly(top[:3] + bot[2:] + ([(0, 0)] if both else [(0, w), (0, -w)]))
    c.drawPath(outline, stroke(lighten(rgb, 0.7), max(1.2, w * 0.06), 0.8 * a))
    c.restore()


def wavy_band(c, y0, y1, rgb, seed, amp=18, a=255):
    rng = np.random.default_rng(seed)
    ph, f = rng.uniform(0, 6.28), rng.uniform(1.5, 3.0)
    p = skia.Path()
    p.moveTo(-10, y1 + 400)
    for x in range(-10, W + 30, 30):
        p.lineTo(x, y0 + amp * math.sin(x / W * f * 6.28 + ph) + amp * 0.4 * math.sin(x / 90 + ph * 2))
    p.lineTo(W + 30, y1 + 400)
    p.close()
    c.drawPath(p, fill(rgb, a))


def streak_atom(c, x, y, r, rgb, vx, vy, worried=True):
    """Hot, hyperactive atom with motion streaks."""
    sp = math.hypot(vx, vy) or 1
    for k in range(3):
        o = (k - 1) * r * 0.45
        nx, ny = -vy / sp * o, vx / sp * o
        c.drawLine(x + nx - vx / sp * r * 0.6, y + ny - vy / sp * r * 0.6,
                   x + nx - vx / sp * r * (2.4 - abs(k - 1) * 0.6), y + ny - vy / sp * r * (2.4 - abs(k - 1) * 0.6),
                   stroke(WHITE, r * 0.18, 110))
    atom(c, x, y, r, rgb, T, look=(vx / sp, vy / sp))
    if worried:
        c.drawPath(_drop(x + r * 0.95, y - r * 0.75, r * 0.22), fill(ICE, 230))


def _drop(x, y, s):
    p = skia.Path()
    p.moveTo(x, y - s * 1.4)
    p.quadTo(x + s, y, x, y + s)
    p.quadTo(x - s, y, x, y - s * 1.4)
    return p


def caption(c, s, x, y, rgb=WHITE, size=30, a=255):
    w = font(size, 800).measureText(s) + size * 0.08 * (len(s) - 1) + size * 1.4
    c.drawRRect(rrect(x - w / 2, y - size * 1.05, w, size * 1.6, size * 0.8), fill((12, 10, 34), 200))
    text(c, s, x, y, size, rgb, a, 800, spacing=size * 0.08)


# ---------------------------------------------------------------- 1. fire: magma chamber
def sf_fire_chamber(c):
    c.drawPaint(shaded(linear((0, 0), (0, 220), [(18, 16, 50), (40, 28, 86)])))
    Stars(90, 4).draw(c, T, 0.8)
    # surface + volcano
    c.drawPath(poly([(1050, 230), (1220, 90), (1290, 90), (1470, 230)]), fill((70, 52, 120)))
    c.drawPath(poly([(1220, 90), (1290, 90), (1275, 110), (1235, 110)]), fill(ORANGE))
    for i, (tx, h) in enumerate([(1560, 50), (1620, 66), (1690, 44), (1760, 60), (1830, 48)]):
        c.drawLine(tx, 236, tx, 236 - h * 0.6, stroke((50, 36, 80), 7))
        c.drawCircle(tx, 236 - h * 0.75, h * 0.42, fill(mix(MINT, (40, 140, 110), (i % 3) / 3)))
    layers = [(220, (92, 74, 140)), (330, (78, 62, 128)), (470, (64, 50, 112)), (640, (52, 40, 96)), (830, (42, 32, 82))]
    for k, (y, cc) in enumerate(layers):
        wavy_band(c, y, 1080, cc, k + 1, amp=14 + k * 4)
    # dots of texture in strata
    rng = np.random.default_rng(3)
    for _ in range(160):
        x, y = rng.uniform(0, W), rng.uniform(250, 1080)
        c.drawCircle(x, y, rng.uniform(2, 6), fill(WHITE, 18))
    # conduit + chamber
    conduit = skia.Path()
    conduit.moveTo(1240, 105)
    conduit.cubicTo(1230, 350, 900, 450, 820, 640)
    conduit.lineTo(900, 660)
    conduit.cubicTo(980, 480, 1270, 380, 1270, 105)
    conduit.close()
    c.drawPath(conduit, fill(ORANGE))
    glow(c, 760, 780, 520, ORANGE, 150)
    chamber = blob_path(760, 780, [300, 280, 230, 210, 250, 300, 330, 310, 260, 230, 250, 290], 0.3)
    c.drawPath(chamber, shaded(radial((720, 740), 360, [lighten(YELLOW, 0.4), YELLOW, ORANGE, (220, 70, 40)], [0, 0.3, 0.7, 1])))
    c.drawPath(chamber, stroke(lighten(YELLOW, 0.5), 5, 180))
    for (bx, by, br) in [(640, 720, 22), (820, 860, 16), (900, 700, 12), (700, 900, 18), (560, 820, 10)]:
        c.drawCircle(bx, by, br, stroke(lighten(YELLOW, 0.6), 4, 170))
    # callout lens
    lx, ly, lr = 1430, 690, 280
    c.drawPath(poly([(850, 700), (lx - lr * 0.75, ly - lr * 0.66), (lx - lr * 0.75, ly + lr * 0.66), (850, 820)]), fill(YELLOW, 40))
    c.drawCircle(850, 760, 64, stroke(WHITE, 5, 220))
    soft_shadow(c, _circle(lx, ly, lr), 14, 22, 26, 140)
    c.save()
    c.clipPath(_circle(lx, ly, lr), doAntiAlias=True)
    c.drawPaint(shaded(radial((lx - 60, ly - 80), lr * 1.4, [(255, 190, 90), (240, 110, 50), (170, 50, 40)], [0, 0.6, 1])))
    rng = np.random.default_rng(12)
    for i in range(11):
        ax, ay = lx + rng.uniform(-220, 220), ly + rng.uniform(-200, 200)
        if math.hypot(ax - lx, ay - ly) > lr - 50:
            continue
        ang = rng.uniform(0, 6.28)
        streak_atom(c, ax, ay, rng.uniform(30, 40), SI if i % 3 == 0 else OX, math.cos(ang), math.sin(ang))
    c.restore()
    c.drawCircle(lx, ly, lr, stroke(WHITE, 8, 240))
    caption(c, "TOO HOT TO HOLD HANDS", lx, ly + lr + 70, YELLOW, 30)
    title_card(c, 1, "FIRE", ORANGE, icon_flame)


def _circle(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


# ---------------------------------------------------------------- 2. fire: slow vs fast
def sf_fire_split(c):
    # left: slow cooling underground
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(0, 0, W / 2, H))
    c.drawPaint(shaded(linear((0, 0), (0, H), [(48, 30, 80), (26, 18, 52)])))
    glow(c, 480, 760, 600, ORANGE, 70)
    wavy_band(c, 860, 1080, (40, 28, 72), 9, 20)
    crystals = [(330, 880, 330, 46, -100, ICE), (430, 890, 420, 56, -82, ICE), (540, 885, 300, 42, -64, ICE),
                (250, 900, 220, 36, -122, ICE), (620, 900, 210, 34, -48, ICE), (480, 900, 180, 30, -95, ICE)]
    for (x, y, L, w, ang, rgb) in crystals:
        prism(c, x, y, L, w, ang, rgb, glow_a=50)
    for (x, y, s, rot) in [(160, 930, 70, -12), (740, 930, 80, 14), (690, 980, 50, -6)]:  # pink feldspar blocks
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.drawPath(poly([(-s, -s * 0.5), (s * 0.5, -s * 0.8), (s, -s * 0.2), (s * 0.4, s * 0.6), (-s * 0.9, s * 0.5)]), fill(lighten(PINK, 0.25)))
        c.drawPath(poly([(-s, -s * 0.5), (s * 0.5, -s * 0.8), (s * 0.2, -s * 0.1), (-s * 0.8, -s * 0.05)]), fill(lighten(PINK, 0.55)))
        c.restore()
    for (x, y, s) in [(380, 420, 30), (560, 520, 22), (250, 600, 18)]:
        sparkle(c, x, y, s, rot=20)
    # clock
    cx, cy = 480, 260
    c.drawCircle(cx, cy, 70, fill(WHITE))
    c.drawCircle(cx, cy, 70, stroke(INK, 8))
    for k in range(12):
        a = k / 12 * 6.28
        c.drawLine(cx + 52 * math.cos(a), cy + 52 * math.sin(a), cx + 60 * math.cos(a), cy + 60 * math.sin(a), stroke(INK, 4))
    c.drawLine(cx, cy, cx + 30, cy - 28, stroke(INK, 7))
    c.drawLine(cx, cy, cx - 6, cy + 44, stroke(INK, 5))
    caption(c, "SLOW  ·  THOUSANDS OF YEARS", 480, 420, ICE, 30)
    c.restore()
    # right: lava meets the sea
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(W / 2, 0, W / 2, H))
    c.drawPaint(shaded(linear((0, 0), (0, H), [(20, 18, 56), (60, 40, 110)])))
    Stars(60, 8).draw(c, T, 0.7)
    sea = skia.Path()
    sea.moveTo(W / 2, 640)
    for x in range(int(W / 2), W + 30, 30):
        sea.lineTo(x, 640 + 14 * math.sin(x / 70))
    sea.lineTo(W, H)
    sea.lineTo(W / 2, H)
    sea.close()
    c.drawPath(sea, shaded(linear((0, 620), (0, H), [CYAN, (30, 70, 150)])))
    # lava flow from the left cliff
    lava = skia.Path()
    lava.moveTo(W / 2, 470)
    lava.cubicTo(1150, 470, 1260, 560, 1330, 690)
    lava.lineTo(1260, 720)
    lava.cubicTo(1190, 620, 1100, 600, W / 2, 620)
    lava.close()
    c.drawPath(poly([(W / 2, 430), (1120, 460), (1250, 640), (1250, H), (W / 2, H)]), shaded(linear((0, 430), (0, H), [(84, 62, 128), (44, 32, 80)])))
    glow(c, 1300, 690, 220, ORANGE, 170)
    c.drawPath(lava, shaded(linear((W / 2, 0), (1330, 0), [YELLOW, ORANGE, (230, 70, 40)])))
    # steam
    for (x, y, r) in [(1330, 600, 70), (1400, 540, 90), (1300, 500, 60), (1480, 470, 80), (1380, 430, 55)]:
        c.drawCircle(x, y, r, fill(WHITE, 150))
    # obsidian chunk
    ob = poly([(1500, 930), (1580, 800), (1720, 780), (1800, 860), (1760, 960), (1600, 990)])
    soft_shadow(c, ob, 12, 18, 16, 120)
    c.drawPath(ob, shaded(linear((1500, 780), (1800, 990), [(70, 62, 100), (14, 12, 26)])))
    c.drawPath(poly([(1580, 800), (1720, 780), (1670, 860), (1560, 880)]), fill((110, 100, 150), 160))
    c.drawPath(poly([(1600, 815), (1690, 803), (1650, 830)]), fill(WHITE, 200))
    c.drawPath(ob, stroke((150, 140, 200), 3, 160))
    sparkle(c, 1705, 795, 24, rot=10)
    caption(c, "FAST  ·  SECONDS", 1440, 260, ORANGE, 30)
    text(c, "= GLASS, NO CRYSTALS", 1650, 1050, 26, WHITE, 230, 800)
    c.restore()
    c.drawLine(W / 2, 0, W / 2, H, stroke(WHITE, 6, 230))
    glow(c, W / 2, H / 2, 120, WHITE, 60)


# ---------------------------------------------------------------- 3. water: salt flat
def sf_water_flat(c):
    hz = 520
    c.drawPaint(shaded(linear((0, 0), (0, hz), [(60, 40, 120), (255, 140, 120)])))
    glow(c, 1400, 300, 380, YELLOW, 170)
    c.drawCircle(1400, 300, 130, shaded(radial((1370, 270), 150, [(255, 245, 200), YELLOW])))
    for (mx, mw, mh, cc) in [(-100, 700, 170, (150, 90, 150)), (500, 600, 120, (180, 100, 150)), (1050, 800, 150, (140, 80, 140))]:
        c.drawPath(poly([(mx, hz), (mx + mw * 0.45, hz - mh), (mx + mw * 0.55, hz - mh * 0.9), (mx + mw, hz)]), fill(cc))
    c.drawRect(skia.Rect.MakeXYWH(0, hz, W, H - hz), shaded(linear((0, hz), (0, H), [(250, 236, 236), (226, 222, 245)])))
    # perspective hexagon salt crust
    f, camh = 520.0, 140.0

    def proj(x, z):
        return W / 2 + x * f / z, hz + camh * f / z

    hs = 18.0
    for row in range(-2, 60):
        for col_ in range(-40, 41):
            x = col_ * hs * 1.75 + (row % 2) * hs * 0.875
            z = 60 + row * hs * 1.5
            pts = [proj(x + hs * math.cos(a), z + hs * math.sin(a)) for a in [k * math.pi / 3 + math.pi / 6 for k in range(6)]]
            if z <= 10 or max(p[0] for p in pts) < -50 or min(p[0] for p in pts) > W + 50:
                continue
            fade = clamp(1 - (z - 60) / 900)
            c.drawPath(poly(pts), stroke((200, 190, 225), max(0.6, 3.5 * 60 / z), 220 * fade))
    # shrinking lake with salt rim
    lake = blob_path(1000, 720, [300, 260, 240, 270, 330, 360, 320, 290], 0.2)
    m = skia.Matrix()
    m.setScale(1.0, 0.32, 1000, 720)
    lake.transform(m)
    c.drawPath(lake, stroke(WHITE, 26, 255))
    c.drawPath(lake, shaded(linear((0, 640), (0, 800), [(120, 220, 240), (60, 170, 210)])))
    c.drawPath(lake, stroke((235, 250, 255), 4, 255))
    glow(c, 1200, 700, 90, WHITE, 120)
    # salt cubes growing on the rim
    for (x, y, s) in [(720, 742, 16), (760, 770, 12), (1280, 700, 14), (1310, 735, 18), (1000, 816, 15), (890, 812, 11)]:
        cube(c, x, y, s, 0.6, 0.5, ICE, 255, 220, 40)
    # the bird with a tiny sun hat
    bird(c, 470, 930, 70, T, look=(0.9, -0.2), tilt=4)
    for (x, y, s) in [(1160, 680, 22), (820, 735, 16)]:
        sparkle(c, x, y, s, rot=15)
    caption(c, "WATER LEAVES, MINERALS STAY", W / 2, 1020, WHITE, 30)
    title_card(c, 2, "WATER", CYAN, icon_drop)


# ---------------------------------------------------------------- 4. water: Naica cave
def sf_water_naica(c):
    c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.7, [(70, 50, 100), (30, 20, 50), (12, 8, 24)], [0, 0.5, 1])))
    # cave walls
    for (cx, cy, rr, cc) in [(-60, 300, [420, 380, 460, 400, 440, 420, 380, 450], (24, 16, 40)),
                             (W + 60, 400, [460, 420, 400, 480, 430, 400, 440, 470], (24, 16, 40)),
                             (W / 2, H + 220, [420, 300, 330, 320, 300, 320, 340, 300], (34, 22, 54))]:
        c.drawPath(blob_path(cx, cy, rr, 0.1), fill(cc))
    beams = [(-120, 820, 1500, 70, -22), (260, 1100, 1300, 62, -48), (1950, 760, 1400, 76, 200), (1700, 1150, 1150, 58, 235),
             (600, -100, 900, 50, 62), (1300, -80, 900, 54, 118), (-80, 520, 900, 48, -6)]
    for (x, y, L, w, ang) in beams:
        prism(c, x, y, L, w, ang, (236, 236, 226), 245, tip=0.7, glow_a=40)
    # light from a headlamp
    glow(c, 960, 620, 520, (255, 240, 200), 60)
    # tiny explorers for scale
    bx, by = 1010, 588
    bird(c, bx, by, 24, T, look=(0.6, -0.6))
    hx, hy = 940, 596
    c.drawCircle(hx, hy - 52, 9, fill((255, 210, 120)))
    c.drawRRect(rrect(hx - 9, hy - 42, 18, 34, 8), fill(ORANGE))
    c.drawLine(hx - 4, hy - 10, hx - 5, hy, stroke(INK, 5))
    c.drawLine(hx + 4, hy - 10, hx + 5, hy, stroke(INK, 5))
    # scale bar
    x0, y0, y1 = 1700, 180, 860
    c.drawLine(x0, y0, x0, y1, stroke(WHITE, 5))
    c.drawLine(x0 - 20, y0, x0 + 20, y0, stroke(WHITE, 5))
    c.drawLine(x0 - 20, y1, x0 + 20, y1, stroke(WHITE, 5))
    text(c, "12 m", x0 + 30, (y0 + y1) / 2 + 14, 44, WHITE, 255, 800, "left")
    caption(c, "NAICA, MEXICO  ·  ~500,000 YEARS OF GROWTH", W / 2, 1010, ICE, 30)
    title_card(c, 2, "WATER", CYAN, icon_drop)


# ---------------------------------------------------------------- 5. pressure: diamond
def sf_pressure(c):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(70, 30, 70), (140, 40, 60)])))
    for k, (y, cc) in enumerate([(0, (60, 26, 64)), (150, (78, 30, 66)), (310, (96, 34, 64)), (780, (120, 38, 60)), (930, (140, 44, 58))]):
        wavy_band(c, y, 1080, cc, 20 + k, 16)
    glow(c, 1150, 560, 560, (255, 120, 90), 70)
    # pressure arrows
    for x in (560, 960, 1360, 1760):
        for sgn, y in ((1, 60), (-1, 1020)):
            c.drawPath(poly([(x - 30, y), (x + 30, y), (x + 30, y + 70 * sgn), (x + 60, y + 70 * sgn), (x, y + 130 * sgn),
                             (x - 60, y + 70 * sgn), (x - 30, y + 70 * sgn)]), fill(WHITE, 200))
    text(c, "PRESSURE", 960, 250, 34, WHITE, 230, 800, spacing=10)
    # graphite sheets (left) -> diamond lattice (right)
    gx, gy = 640, 600
    for layer in range(3):
        yy = gy - 80 + layer * 80
        for i in range(-3, 4):
            for j in range(2):
                ax = gx + i * 46 + j * 23
                ay = yy + j * 18
                atom(c, ax, ay, 16, CARBON, T, face=(layer == 2 and j == 1))
    caption(c, "GRAPHITE  (PENCIL LEAD)", gx, 800, ICE, 26)
    c.drawPath(poly([(880, 570), (980, 570), (980, 540), (1040, 600), (980, 660), (980, 630), (880, 630)]), fill(YELLOW))
    # diamond: carbon atoms locked in a tight 3D cage + the gem
    dx, dy = 1330, 560
    fcc = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    fcc += [(0.5, 0.5, 0), (0.5, 0.5, 1), (0.5, 0, 0.5), (0.5, 1, 0.5), (0, 0.5, 0.5), (1, 0.5, 0.5)]
    inner = [(0.25, 0.25, 0.25), (0.75, 0.75, 0.25), (0.75, 0.25, 0.75), (0.25, 0.75, 0.75)]
    pts = [(x - 0.5, y - 0.5, z - 0.5) for (x, y, z) in fcc + inner]
    pr = [project(p, 300, 0.55, 0.42, dx, dy) for p in pts]
    path = skia.Path()
    for a_ in range(len(fcc), len(pts)):          # each inner atom bonds to its 4 neighbours
        for b_ in range(len(fcc)):
            if abs(math.dist(pts[a_], pts[b_]) - math.sqrt(3) / 4) < 1e-6:
                path.moveTo(pr[a_][0], pr[a_][1])
                path.lineTo(pr[b_][0], pr[b_][1])
    edges = skia.Path()
    for a_ in range(8):
        for b_ in range(a_ + 1, 8):
            if abs(math.dist(pts[a_], pts[b_]) - 1) < 1e-6:
                edges.moveTo(pr[a_][0], pr[a_][1])
                edges.lineTo(pr[b_][0], pr[b_][1])
    glow(c, dx, dy, 300, PINK, 120)
    c.drawPath(edges, stroke(WHITE, 2, 70))
    c.drawPath(path, stroke(lighten(PINK, 0.6), 8, 230))
    for n_, (x, y, z, k) in sorted(enumerate(pr), key=lambda q: -q[1][2]):  # far to near
        atom(c, x, y, 26 * k, CARBON, T, face=n_ >= len(fcc))
        c.drawCircle(x, y, 26 * k, stroke(lighten(PINK, 0.6), 3, 220))
    sparkle(c, dx + 150, dy - 170, 40, rot=12)
    caption(c, "DIAMOND", dx, 850, PINK, 30)
    # depth meter
    mx = 150
    c.drawRRect(rrect(mx - 14, 300, 28, 640, 14), fill((20, 12, 30), 180))
    for n, km in enumerate((0, 50, 100, 150)):
        y = 320 + n * 200
        c.drawLine(mx + 14, y, mx + 34, y, stroke(WHITE, 4))
        text(c, f"{km} km", mx + 44, y + 10, 26, WHITE, 230, 800, "left")
    c.drawRRect(rrect(mx - 14, 300, 28, 640, 14), shaded(linear((0, 300), (0, 940), [(YELLOW, 255), (PINK, 255)])))
    c.drawCircle(mx, 920, 26, fill(WHITE))
    c.drawCircle(mx, 920, 14, fill(PINK))
    title_card(c, 3, "PRESSURE", PINK, icon_down)


# ---------------------------------------------------------------- 6. life: oxygen
def sf_life(c):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(40, 150, 170), (16, 50, 90)])))
    for k in range(6):  # light rays
        x = 200 + k * 330
        c.drawPath(poly([(x, -10), (x + 120, -10), (x + 340, H), (x + 160, H)]), blur(fill(WHITE, 22), 20))
    # sea floor + stromatolites
    wavy_band(c, 900, 1080, (30, 60, 80), 31, 20)
    for (sx, sw, sh) in [(260, 220, 200), (560, 180, 150), (820, 260, 240), (1120, 170, 130)]:
        for layer in range(5):
            f = 1 - layer * 0.17
            c.drawOval(skia.Rect.MakeXYWH(sx - sw * f / 2, 960 - sh * f, sw * f, sh * f * 2), fill(mix((40, 110, 100), MINT, layer / 5)))
        # microbes on top puffing oxygen
        for m in range(3):
            mx, my = sx - sw * 0.25 + m * sw * 0.25, 960 - sh * 0.82 - (m % 2) * 10
            atom(c, mx, my, 15, MINT, T + m, look=(0, -1))
    rng = np.random.default_rng(5)
    for i in range(22):
        x = rng.uniform(150, 1250)
        y = rng.uniform(150, 720)
        atom(c, x, y, rng.uniform(12, 22), OX, T + i, look=(0, -1))
        c.drawCircle(x, y, 26, stroke(WHITE, 2, 70))
    # rust-red rock + new minerals bursting out
    rock = blob_path(1600, 860, [260, 230, 280, 240, 260, 300, 270, 250], 0.4)
    c.drawPath(rock, fill((90, 76, 110)))
    for (x, y, r) in [(1520, 760, 60), (1680, 820, 80), (1600, 940, 50), (1740, 940, 40)]:
        c.drawPath(blob_path(x, y, [r, r * 0.8, r * 1.1, r * 0.9, r, r * 0.85], 0), fill((200, 80, 60)))
    gems = [(1450, 520, PINK, 0), (1580, 440, YELLOW, 1), (1720, 470, CYAN, 2), (1820, 580, MINT, 3), (1380, 640, ORANGE, 1),
            (1660, 560, (170, 130, 255), 0)]
    for (x, y, rgb, kind) in gems:
        glow(c, x, y, 70, rgb, 110)
        _gem(c, x, y, 34, rgb, kind)
    # counter
    c.drawRRect(rrect(1350, 150, 480, 170, 30), fill((10, 20, 40), 200))
    text(c, "MINERALS ON EARTH", 1590, 205, 26, MINT, 255, 800, spacing=4)
    text(c, "~ 2/3", 1590, 280, 60, WHITE, 255, 800)
    text(c, "NEED LIFE", 1590, 312, 22, WHITE, 200, 800, spacing=4)
    title_card(c, 4, "LIFE", MINT, icon_sprout)


def _gem(c, x, y, s, rgb, kind):
    c.save()
    c.translate(x, y)
    if kind == 0:
        c.drawPath(poly([(0, -s * 1.3), (-s, 0), (0, s * 1.3)]), fill(lighten(rgb, 0.3)))
        c.drawPath(poly([(0, -s * 1.3), (s, 0), (0, s * 1.3)]), fill(darken(rgb, 0.1)))
    elif kind == 1:
        c.drawPath(poly([(-s * 0.6, -s), (0, -s * 1.5), (s * 0.6, -s), (s * 0.6, s), (-s * 0.6, s)]), fill(rgb))
        c.drawPath(poly([(-s * 0.6, -s), (0, -s * 1.5), (0, s), (-s * 0.6, s)]), fill(lighten(rgb, 0.35)))
    elif kind == 2:
        c.drawPath(poly([(-s * 1.1, -s * 0.2), (-s * 0.3, -s), (s * 1.1, -s * 0.4), (s * 0.3, s * 0.7)]), fill(rgb))
        c.drawPath(poly([(-s * 1.1, -s * 0.2), (-s * 0.3, -s), (s * 0.3, s * 0.7)]), fill(lighten(rgb, 0.3)))
    else:
        c.drawPath(poly([(-s, -s * 0.3), (-s * 0.5, -s * 0.8), (s * 0.5, -s * 0.8), (s, -s * 0.3), (0, s)]), fill(rgb))
        c.drawPath(poly([(-s, -s * 0.3), (s, -s * 0.3), (0, s)]), fill(darken(rgb, 0.15)))
    c.restore()


# ---------------------------------------------------------------- 7. deep time: zircon
def sf_deep_time(c):
    c.drawPaint(shaded(radial((W / 2, 420), W * 0.6, [(30, 24, 60), (8, 6, 20)])))
    Stars(160, 17).draw(c, T, 0.6)
    zx, zy = W / 2, 400
    glow(c, zx, zy, 340, PINK, 110)
    glow(c, zx, zy, 160, (255, 200, 180), 120)
    prism(c, zx - 70, zy + 190, 400, 78, -72, (235, 140, 125), tip=0.9, both=True)
    sparkle(c, zx + 120, zy - 70, 36, rot=20)
    text(c, "4.4 BILLION YEARS", zx, 690, 64, WHITE, 255, 800, spacing=4)
    text(c, "THE OLDEST PIECE OF EARTH EVER FOUND", zx, 740, 26, PINK, 230, 800, spacing=4)
    # timeline
    x0, x1, y = 160, 1760, 900
    c.drawRRect(rrect(x0, y - 8, x1 - x0, 16, 8), shaded(linear((x0, 0), (x1, 0), [ORANGE, PINK, CYAN, MINT])))
    marks = [(4.5, "EARTH FORMS", ORANGE), (4.4, "ZIRCON", PINK), (3.7, "FIRST LIFE", MINT), (2.4, "OXYGEN", CYAN)]
    for ga, label, rgb in marks:
        x = x0 + (4.6 - ga) / 4.6 * (x1 - x0)
        up = -1 if label in ("ZIRCON", "OXYGEN") else 1
        c.drawCircle(x, y, 16, fill(rgb))
        c.drawCircle(x, y, 16, stroke(WHITE, 4))
        text(c, label, x, y + up * 52 + (10 if up > 0 else 0), 22, WHITE, 230, 800, spacing=2)
        text(c, f"{ga} BILLION", x, y + up * 80 + (10 if up > 0 else 0), 18, rgb, 220, 800)
    c.drawCircle(x1, y, 6, fill(WHITE))
    text(c, "YOU", x1, y - 30, 22, WHITE, 255, 800, spacing=2)


# ---------------------------------------------------------------- 8. outro: geode under the stars
def sf_outro(c):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(10, 10, 34), (50, 32, 100)])))
    # milky way band
    c.save()
    c.rotate(-18, W / 2, H / 2)
    c.drawOval(skia.Rect.MakeXYWH(-200, 220, W + 400, 260), blur(fill((150, 120, 230), 50), 60))
    c.restore()
    Stars(320, 23).draw(c, T, 1.0)
    for (y, cc, seed) in [(700, (34, 24, 70), 41), (800, (24, 18, 52), 42), (900, (16, 12, 38), 43)]:
        wavy_band(c, y, 1080, cc, seed, 40)
    # rock
    rock = blob_path(1240, 880, [200, 160, 150, 170, 190, 200, 180, 170], 0.0)
    m = skia.Matrix()
    m.setScale(1.0, 0.55, 1240, 880)
    rock.transform(m)
    c.drawPath(rock, fill((60, 48, 96)))
    # geode
    gx, gy, gr = 860, 890, 150
    glow(c, gx, gy - 30, 380, (190, 120, 255), 120)
    shell = skia.Path()
    shell.addOval(skia.Rect.MakeXYWH(gx - gr, gy - gr * 0.7, gr * 2, gr * 1.4))
    c.drawPath(shell, fill((120, 100, 120)))
    inner = skia.Path()
    inner.addOval(skia.Rect.MakeXYWH(gx - gr * 0.82, gy - gr * 0.56, gr * 1.64, gr * 1.12))
    c.drawPath(inner, fill((236, 230, 240)))
    c.save()
    c.clipPath(inner, doAntiAlias=True)
    c.drawPaint(shaded(radial((gx, gy), gr, [(80, 30, 140), (150, 80, 230), (200, 160, 255)], [0, 0.6, 1])))
    for k in range(18):
        a = k / 18 * 6.28
        x, y = gx + math.cos(a) * gr * 0.82, gy + math.sin(a) * gr * 0.56
        tx, ty = gx + math.cos(a) * gr * 0.15, gy + math.sin(a) * gr * 0.1
        nx, ny = -math.sin(a) * 16, math.cos(a) * 11
        c.drawPath(poly([(x + nx, y + ny), (tx, ty), (x - nx, y - ny)]), fill(lighten((150, 80, 230), 0.15 + 0.4 * (k % 3) / 2)))
    c.restore()
    for (x, y, s) in [(gx - 40, gy - 30, 24), (gx + 50, gy + 10, 16)]:
        sparkle(c, x, y, s, rot=10)
    # the bird, sitting and looking at it, lit by the crystal glow
    bird(c, 1220, 812, 82, T, look=(-1, 0.4), tilt=-4)
    glow(c, 1130, 700, 120, (190, 120, 255), 50)
    text(c, "FIRE  ·  WATER  ·  PRESSURE  ·  LIFE", W / 2, 200, 34, WHITE, 230, 800, spacing=6)


FRAMES = [("01_fire_chamber", "Scene 3 · Fire: magma is too hot for atoms to bond", sf_fire_chamber),
          ("02_fire_slow_fast", "Scene 3 · Fire: slow cooling = crystals, fast = glass", sf_fire_split),
          ("03_water_salt_flat", "Scene 4 · Water: a drying lake leaves salt behind", sf_water_flat),
          ("04_water_naica", "Scene 4 · Water: the 12 m crystals of Naica", sf_water_naica),
          ("05_pressure_diamond", "Scene 5 · Pressure: graphite squeezed into diamond", sf_pressure),
          ("06_life_oxygen", "Scene 6 · Life: microbes' oxygen creates new minerals", sf_life),
          ("07_deep_time_zircon", "Scene 7 · Deep time: the 4.4-billion-year-old zircon", sf_deep_time),
          ("08_outro_geode", "Scene 8 · Outro: the bird and a glowing geode", sf_outro)]


def render(fn):
    s = skia.Surface(W, H)
    c = s.getCanvas()
    fn(c)
    vignette(c)
    return finish(s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType), T)


def board(paths, labels, out):
    tw, th, pad, lab = 960, 540, 24, 56
    rows = (len(paths) + 1) // 2
    sheet = Image.new("RGB", (2 * tw + 3 * pad, rows * (th + lab + pad) + pad + 90), NAVY)
    d = ImageDraw.Draw(sheet)
    f_big = ImageFont.truetype(FONT_FILES[800], 44)
    f = ImageFont.truetype(FONT_FILES[600], 26)
    d.text((pad, 26), "HOW THE EARTH MAKES CRYSTALS  ·  STYLE FRAMES", font=f_big, fill=WHITE)
    for i, (p, l) in enumerate(zip(paths, labels)):
        x, y = pad + (i % 2) * (tw + pad), 100 + (i // 2) * (th + lab + pad)
        sheet.paste(Image.open(p).resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x, y + th + 12), l, font=f, fill=ICE)
    sheet.save(out)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    pick = {int(a) for a in sys.argv[1:]}
    paths, labels = [], []
    for n, (name, label, fn) in enumerate(FRAMES, 1):
        p = os.path.join(OUT, f"{name}.png")
        if not pick or n in pick:
            Image.fromarray(render(fn)).save(p)
            print(p)
        paths.append(p)
        labels.append(label)
    if all(os.path.exists(p) for p in paths):
        board(paths, labels, os.path.join(OUT, "board.png"))
