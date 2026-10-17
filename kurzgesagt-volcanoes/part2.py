"""Part 2: where magma comes from. Three ways to melt a rock, then magma rises like a lava lamp.

  python3 render.py part2 [--still 3,12,20]
"""
import math

import numpy as np

from common import *  # noqa: F401,F403
from part1 import mantle_texture

PART = "part2"
VO = {"B1": 0.6, "B2": 4.8, "B3": 8.2, "B4": 17.4, "B5": 24.8, "B6": 29.6}
DURATION = 40.0
TM = Timing(PART, VO)

BLOB_T = TM.word("B1", "magma") - 0.2
BADGES = (TM.word("B2", "three") - 0.1, 0.3)
S1 = (7.9, 8.4)
LIFT_T = TM.word("B3", "let it rise") - 0.2
MELT = (TM.word("B3", "drops") - 0.2, TM.word("B3", "it melts") + 0.6)
S2 = (17.1, 17.6)
DROPS_T = TM.word("B4", "add water")
SALT_T = TM.word("B4", "salt") - 0.3
S3 = (24.5, 25.0)
HEAT = (TM.word("B5", "rising"), TM.word("B5", "around") + 0.6)
S4 = (29.3, 29.8)
LAMP_T = TM.word("B6", "lava lamp") - 0.3
CHAMBER = (TM.word("B6", "collects"), TM.word("B6", "surface") + 0.5)

METHODS = [("PRESSURE OFF", CYAN, icon_up), ("ADD WATER", (90, 170, 255), icon_drop), ("ADD HEAT", LAVA, icon_flame)]


def method_badge(c, t, n, x, y, g, small=False):
    if g <= 0.01:
        return
    name, rgb, icon = METHODS[n]
    r = 40 if small else 80
    c.save()
    c.translate(x, y)
    c.scale(g, g)
    glow(c, 0, 0, r * 2.2, rgb, 100)
    c.drawCircle(0, 0, r, fill(rgb))
    c.drawCircle(0, 0, r, stroke(WHITE, 5, 220))
    c.save()
    c.scale(r / 30, r / 30)
    icon(c, 0, 0, 16)
    c.restore()
    number_badge(c, r * 0.75, -r * 0.75, n + 1, WHITE, 1.0, r * 0.38)
    if small:
        text(c, name, r + 24, 12, 32, WHITE, 255, 800, "left", spacing=3)
    else:
        text(c, name, 0, r + 64, 34, WHITE, 255, 800, spacing=3)
    c.restore()


def mantle_bg(c, t, dim=0.35):
    c.drawPicture(mantle_texture())
    c.drawPaint(fill(DARK, 255 * dim))


# ---------------------------------------------------------------- intro + menu
def draw_intro(c, t):
    mantle_bg(c, t, 0.55)
    caption(c, "WHERE DOES MAGMA COME FROM?", 960, 220, WHITE, 38, 255 * smooth(prog(t, 0.6, 1.0)) * (1 - smooth(prog(t, BADGES[0] - 0.4, BADGES[0]))))
    g = pop(t, BLOB_T, 0.6) * (1 - smooth(prog(t, BADGES[0] - 0.4, BADGES[0])))
    if g > 0:
        magma_blob(c, 960, 560 + bob(t, 10, 2.5), 110 * g, t, look=(0.4 * math.sin(t * 1.5), -0.3))
        bubble_q(c, 1110, 380, pop(t, BLOB_T + 0.5, 0.4) * (1 - smooth(prog(t, BADGES[0] - 0.4, BADGES[0]))))
    for n in range(3):
        g = pop(t, BADGES[0] + n * BADGES[1], 0.5) * (1 - smooth(prog(t, S1[0], S1[1])))
        method_badge(c, t, n, 480 + n * 480, 500, g)


# ---------------------------------------------------------------- 1: take the pressure off
GRID = [(i, j) for j in range(4) for i in range(7)]
_rng = np.random.default_rng(2)
WANDER = _rng.uniform(0, 6.28, (len(GRID), 2))


def draw_pressure(c, t):
    mantle_bg(c, t, 0.45)
    method_badge(c, t, 0, 150, 130, 1.0, small=True)
    lift = in_out(prog(t, LIFT_T, LIFT_T + 1.4))
    melt = in_out(prog(t, *MELT))
    bx, by = 960, 640 - 140 * lift
    # glowing melt pool spreading behind the atoms
    if melt > 0:
        radii = [300 * melt * (1 + 0.08 * math.sin(t * 2 + k)) for k in range(10)]
        glow(c, bx, by, 520 * melt, LAVA, 140)
        c.drawPath(blob_path(bx, by, radii, 0.2), shaded(radial((bx, by - 60), 360, [LAVA_HOT, LAVA, (200, 60, 30)])))
    else:
        c.drawRRect(rrect(bx - 330, by - 180, 660, 360, 30), fill((90, 34, 46)))
    shake = 4 * (1 - lift)
    for n, (i, j) in enumerate(GRID):
        x0, y0 = bx + (i - 3) * 90, by + (j - 1.5) * 90
        x = x0 + shake * math.sin(t * 40 + n) + melt * 70 * math.sin(t * 0.9 + WANDER[n, 0])
        y = y0 + shake * math.cos(t * 37 + n) + melt * 60 * math.sin(t * 0.8 + WANDER[n, 1])
        rgb = mix((150, 110, 255) if (i + j) % 2 else (255, 92, 92), LAVA_HOT, melt * 0.5)
        atom(c, x, y, 34, rgb, t + n, look=(0, -1) if lift < 0.5 else (0, 0))
    # the weight of the rock above
    wy = lerp(by - 180 - 300, -420, in_cubic(prog(t, LIFT_T, LIFT_T + 1.0)))
    if wy > -400:
        c.drawRRect(rrect(bx - 360, wy, 720, 230, 30), shaded(linear((0, wy), (0, wy + 230), [(110, 90, 150), (70, 52, 100)])))
        text(c, "PRESSURE", bx, wy + 132, 50, WHITE, 230, 800, spacing=10)
        for k in range(3):
            ax = bx - 220 + k * 220
            c.drawPath(poly([(ax - 18, wy + 230), (ax + 18, wy + 230), (ax + 18, wy + 262), (ax + 40, wy + 262), (ax, wy + 300), (ax - 40, wy + 262), (ax - 18, wy + 262)]), fill(WHITE, 200))
    caption(c, "TOO SQUEEZED TO MELT", 960, 1000, WHITE, 30, 255 * smooth(prog(t, S1[1] + 1.0, S1[1] + 1.4)) * (1 - smooth(prog(t, LIFT_T, LIFT_T + 0.3))))
    caption(c, "PRESSURE DROPS  →  IT MELTS", 960, 1000, LAVA_HOT, 30, 255 * smooth(prog(t, MELT[0], MELT[0] + 0.4)))


# ---------------------------------------------------------------- 2: add water (subduction)
SLAB = [(-60, 250), (700, 290), (1050, 420), (1350, 700), (1560, 1140)]


def slab_point(u):
    L = [math.dist(SLAB[i], SLAB[i + 1]) for i in range(len(SLAB) - 1)]
    target, acc = sum(L) * clamp(u), 0.0
    for i, l in enumerate(L):
        if acc + l >= target:
            k = (target - acc) / l
            return lerp(SLAB[i][0], SLAB[i + 1][0], k), lerp(SLAB[i][1], SLAB[i + 1][1], k)
        acc += l
    return SLAB[-1]


def draw_water(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(170, 60, 50), (120, 30, 40)])))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, 900, 200), shaded(linear((0, 0), (0, 200), [CYAN, OCEAN])))
    cont = poly([(820, 120), (W, 80), (W, 420), (1300, 440), (1080, 330), (900, 240)])
    c.drawPath(cont, fill((110, 150, 100)))
    c.drawPath(poly([(820, 120), (W, 80), (W, 130), (860, 170)]), fill((140, 180, 120)))
    top = SLAB
    bot = [(x + 40, y + 120) for (x, y) in SLAB][::-1]
    slab = poly(top + bot)
    c.drawPath(slab, shaded(linear((0, 200), (0, 1080), [(90, 96, 130), (60, 60, 96)])))
    c.drawPath(poly(top, False), stroke((150, 160, 200), 6))
    # plate motion arrow
    c.drawPath(poly([(200, 230), (420, 230), (420, 210), (470, 245), (420, 280), (420, 260), (200, 260)]), fill(WHITE, 200))
    # water riding down, then released into the hot mantle
    k = smooth(prog(t, DROPS_T - 0.3, DROPS_T + 0.3))
    for n in range(10):
        u = ((t - S2[0]) * 0.05 + n / 10) % 1.0
        x, y = slab_point(u)
        if u < 0.62:
            water_drop(c, x, y - 18, 14, 255 * k)
        else:
            rise = (u - 0.62) / 0.38
            water_drop(c, x - 120 * rise, y - 18 - 360 * rise, 14 * (1 - rise * 0.5), 255 * k * (1 - rise))
    melt = smooth(prog(t, DROPS_T + 1.0, DROPS_T + 3.5))
    if melt > 0:
        magma_blob(c, 1120, 560, 90 * melt, t, look=(0.3, -1))
    caption(c, "WATER LOWERS THE MELTING POINT", 700, 1000, (150, 210, 255), 28, 255 * smooth(prog(t, DROPS_T + 1.2, DROPS_T + 1.6)))
    # salt-on-ice analogy
    g = pop(t, SALT_T, 0.5)
    if g > 0:
        ix, iy = 1600, 680
        c.save()
        c.translate(ix, iy)
        c.scale(g, g)
        c.drawRRect(rrect(-190, -170, 380, 330, 36), fill((16, 14, 44), 230))
        m = smooth(prog(t, SALT_T + 0.5, SALT_T + 3.0))
        c.drawOval(skia.Rect.MakeXYWH(-130 * (0.4 + m), 80, 260 * (0.4 + m), 40), fill(CYAN, 160))
        s = 70 * (1 - 0.6 * m)
        c.drawRRect(rrect(-s, 100 - 2 * s, 2 * s, 2 * s, s * 0.25), fill(ICE, 230))
        c.drawRRect(rrect(-s, 100 - 2 * s, 2 * s, 2 * s, s * 0.25), stroke(WHITE, 3))
        for q in range(9):
            c.drawRect(skia.Rect.MakeXYWH(-s * 0.8 + (q % 3) * s * 0.7, 100 - 2 * s - 8 + (q // 3) * 6, 9, 9), fill(WHITE))
        c.restore()
        caption(c, "LIKE SALT ON ICE", ix, iy + 230, WHITE, 24, 255 * min(1, g))
    method_badge(c, t, 1, 150, 490, 1.0, small=True)


# ---------------------------------------------------------------- 3: add heat
def draw_heat(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(70, 56, 110), (40, 30, 70)])))
    for k, (y, cc) in enumerate([(150, (96, 78, 140)), (360, (84, 66, 128)), (600, (72, 56, 114)), (820, (62, 46, 100))]):
        wavy_band(c, y, 1080, cc, 80 + k, 14)
    h = in_out(prog(t, *HEAT))
    up = in_out(prog(t, S3[0], HEAT[0] + 1.0))
    dike = skia.Path()
    tip = lerp(1100, 420, up)
    dike.moveTo(900, H + 20)
    dike.cubicTo(930, 800, 990, tip + 120, 960, tip)
    dike.cubicTo(1000, tip + 140, 1040, 800, 1040, H + 20)
    dike.close()
    glow(c, 970, tip + 200, 260 + 320 * h, LAVA, 140 + 60 * h)
    for k in range(10):  # surrounding rock starting to melt
        a = k / 10 * 6.28
        r = 170 + 40 * (k % 3)
        x, y = 970 + r * math.cos(a), tip + 260 + r * 0.8 * math.sin(a)
        g = smooth(prog(h, k / 14, k / 14 + 0.4))
        if g > 0:
            c.drawPath(blob_path(x, y, [40 * g, 30 * g, 45 * g, 35 * g, 42 * g, 30 * g], k), fill(mix((200, 80, 60), LAVA_HOT, g), 230))
    c.drawPath(dike, shaded(linear((0, tip), (0, H), [LAVA_HOT, LAVA])))
    method_badge(c, t, 2, 150, 130, 1.0, small=True)
    caption(c, "HOT MAGMA MELTS ITS SURROUNDINGS", 960, 1000, LAVA_HOT, 28, 255 * smooth(prog(t, HEAT[0] + 0.6, HEAT[0] + 1.0)))


# ---------------------------------------------------------------- lava lamp + rising to a chamber
LAMP = (360, 540)
RISERS = [(0.0, -60), (0.33, 40), (0.66, -20)]


def draw_rise(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [NAVY, PURPLE])))
    Dust().draw(c, t)
    # lava lamp
    g = pop(t, S4[0] + 0.2, 0.6)
    if g > 0:
        lx, ly = LAMP
        c.save()
        c.translate(lx, ly)
        c.scale(g, g)
        glass = skia.Path()
        glass.moveTo(-70, 300)
        glass.cubicTo(-150, 120, -120, -150, -50, -280)
        glass.lineTo(50, -280)
        glass.cubicTo(120, -150, 150, 120, 70, 300)
        glass.close()
        c.drawPath(glass, shaded(linear((0, -280), (0, 300), [(120, 60, 170), (70, 30, 120)])))
        c.save()
        c.clipPath(glass, doAntiAlias=True)
        for n in range(4):
            ph = (t * 0.09 + n / 4) % 1
            y = lerp(260, -260, 0.5 - 0.5 * math.cos(ph * 6.28))
            magma_blob(c, 25 * math.sin(n * 2 + t * 0.4), y, 36 + 10 * (n % 2), t, face=n == 1, phase=n)
        c.restore()
        c.drawPath(glass, stroke(WHITE, 4, 120))
        c.drawPath(poly([(-90, 300), (90, 300), (130, 420), (-130, 420)]), fill((180, 180, 200)))
        c.drawPath(poly([(-50, -280), (50, -280), (30, -360), (-30, -360)]), fill((180, 180, 200)))
        c.restore()
        caption(c, "LIKE A LAVA LAMP", lx, 1010, WHITE, 26, 255 * smooth(prog(t, LAMP_T, LAMP_T + 0.4)))
    # crust cross-section with a volcano
    cx0 = 760
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(cx0, 0, W - cx0, H))
    c.drawRect(skia.Rect.MakeXYWH(cx0, 0, W, 330), shaded(linear((0, 0), (0, 330), [(20, 18, 56), (60, 44, 110)])))
    c.drawRect(skia.Rect.MakeXYWH(cx0, 330, W, H), shaded(linear((0, 330), (0, H), [CRUST_C, (150, 50, 50)])))
    wavy_band(c, 820, 1080, (160, 56, 52), 91, 12)
    chamber = in_out(prog(t, *CHAMBER))
    vx = 1340
    volcano(c, vx, 340, 520, 240, ROCK, hot=chamber, t=t)
    c.drawLine(vx, 120 + 220, vx, 560, stroke(mix((70, 50, 90), LAVA, chamber), 16))
    ch = skia.Path()
    ch.addOval(skia.Rect.MakeXYWH(vx - 220, 540, 440, 150))
    c.drawPath(ch, fill((60, 40, 70)))
    if chamber > 0:
        c.save()
        c.clipPath(ch, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeXYWH(vx - 230, 690 - 150 * chamber, 460, 160), shaded(linear((0, 540), (0, 690), [LAVA_HOT, LAVA])))
        c.restore()
        glow(c, vx, 620, 260 * chamber, LAVA, 120)
    c.drawPath(ch, stroke(LAVA_HOT, 3, 160))
    for n, (ph0, dx) in enumerate(RISERS):
        u = ((t - S4[0]) * 0.11 + ph0) % 1.0
        y = lerp(1120, 640, u)
        a = 255 * min(1.0, u * 6) * (1 - smooth(prog(u, 0.85, 1.0)))
        magma_blob(c, vx + dx + 20 * math.sin(t + n), y, 46, t, look=(0, -1), phase=n, a=a)
    c.restore()
    c.drawLine(cx0, 0, cx0, H, stroke(WHITE, 4, 160))
    caption(c, "MAGMA CHAMBER", vx, 760 + 30, LAVA_HOT, 26, 255 * smooth(prog(t, CHAMBER[0] + 0.3, CHAMBER[0] + 0.7)))


# ---------------------------------------------------------------- compose
def draw_frame(c, t):
    c.clear(col(NAVY))
    scenes(c, t, [((0.0, 0.01), S1[1], draw_intro), (S1, S2[1], draw_pressure), (S2, S3[1], draw_water),
                  (S3, S4[1], draw_heat), (S4, DURATION + 1, draw_rise)])
    vignette(c)
    chapter_fade(c, t, DURATION)


def sfx_events():
    ev = [(0.4, "rumble", 0.5), (BLOB_T, "pop", 0.7), (BLOB_T + 0.5, "pop", 0.5)]
    ev += [(BADGES[0] + n * BADGES[1], "pop", 0.6) for n in range(3)]
    ev += [(S1[0], "whoosh", 0.6), (S1[1] + 0.5, "rumble", 0.5), (LIFT_T, "whoosh_long", 0.7), (MELT[0], "sizzle", 0.4), (MELT[0] + 0.3, "swell_soft", 0.6),
           (S2[0], "whoosh", 0.6), (DROPS_T, "bubble", 0.6), (DROPS_T + 2.0, "bubble", 0.5), (DROPS_T + 1.5, "pop", 0.5),
           (SALT_T, "pop", 0.6), (SALT_T + 0.8, "shimmer", 0.4),
           (S3[0], "whoosh", 0.6), (HEAT[0], "rumble", 0.7), (HEAT[0] + 0.8, "sizzle", 0.5),
           (S4[0], "whoosh", 0.6), (LAMP_T, "bubble", 0.6), (CHAMBER[0], "rumble", 0.6), (CHAMBER[0] + 0.5, "swell_soft", 0.6)]
    return ev


MUSIC = dict(
    chords=[(0.0, 46, (0, 7, 12, 15, 19)), (4.6, 48, (0, 7, 12, 16, 19)), (8.0, 50, (0, 7, 12, 14, 17)),
            (17.0, 45, (0, 7, 12, 15, 19)), (24.4, 41, (0, 7, 12, 16, 19)), (29.2, 46, (0, 7, 11, 16, 19)),
            (35.0, 48, (0, 7, 12, 16, 19))],
    plucks=[(4.8, DURATION)], bpm=96, rises=[(MELT[0], MELT[1])],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
