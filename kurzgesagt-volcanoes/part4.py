"""Part 4: why some volcanoes ooze and others explode. Gas + runny vs sticky magma, then Pinatubo.

  python3 render.py part4 [--still 3,12,20]
"""
import math

import numpy as np

from common import *  # noqa: F401,F403

PART = "part4"
VO = {"E1": 0.6, "E2": 4.7, "E3": 9.4, "E4": 17.1, "E5": 24.0, "E6": 26.6}
DURATION = 39.5
TM = Timing(PART, VO)

SODA = (4.4, 4.9)
GAS_T = TM.word("E2", "dissolved gas") - 0.2
POP_T = TM.word("E2", "soda") - 0.1
RUNNY = (9.1, 9.6)
ESCAPE_T = TM.word("E3", "escape")
HAWAII_T = TM.word("E3", "hawaii") - 0.3
STICKY = (16.8, 17.3)
TRAP_T = TM.word("E4", "trapped") - 0.2
BUILD = (TM.word("E4", "pressure builds"), VO["E5"])
BOOM = VO["E5"] + 0.05
GLOBE = (30.0, 30.8)
COOL_T = TM.word("E6", "cooled") - 0.2
HALF_T = TM.word("E6", "half a degree") - 0.2

_stick_plume = Plume(31, 46)
_run_plume = Plume(7, 12)
_rng = np.random.default_rng(4)
BOMBS = [(float(_rng.uniform(-420, 420)), float(_rng.uniform(-900, -500)), float(_rng.uniform(8, 20))) for _ in range(16)]


# ---------------------------------------------------------------- intro split
def draw_intro(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(20, 18, 56), (60, 44, 110)])))
    wavy_band(c, 820, 1080, (40, 30, 70), 7, 16)
    volcano(c, 480, 830, 760, 220, (96, 80, 120), crater=0.2, hot=1.0, t=t)
    for k, pts in enumerate([[(470, 612), (380, 700), (300, 800)], [(500, 612), (590, 700), (680, 810)]]):
        lava_flow(c, pts, 0.6 + 0.4 * math.sin(t * 0.5 + k) ** 2, 16)
    x, y = volcano(c, 1440, 830, 560, 460, (90, 76, 116), crater=0.12, hot=1.0, t=t)
    _stick_plume.draw(c, x, y - 10, t, 330, 90, 1.0, 0.25)
    text(c, "OOZE", 480, 960, 54, LAVA_HOT, 255, 800, spacing=8)
    text(c, "EXPLODE", 1440, 960, 54, LAVA_HOT, 255, 800, spacing=8)
    look = math.sin(t * 2.2)
    bird(c, 960, 1040, 64, t, look=(look, -0.3))
    bubble_q(c, 1060, 840, pop(t, 1.6, 0.4))


# ---------------------------------------------------------------- soda bottle
def draw_soda(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [NAVY, PURPLE])))
    Dust().draw(c, t)
    bx, by = 960, 600
    popped = t >= POP_T
    shake = 6 * math.sin(t * 40) * (POP_T - 0.5 < t < POP_T)
    c.save()
    c.translate(bx + shake, by)
    bottle = skia.Path()
    bottle.moveTo(-34, -320)
    bottle.lineTo(34, -320)
    bottle.cubicTo(34, -200, 110, -160, 110, -60)
    bottle.lineTo(110, 300)
    bottle.cubicTo(110, 330, -110, 330, -110, 300)
    bottle.lineTo(-110, -60)
    bottle.cubicTo(-110, -160, -34, -200, -34, -320)
    bottle.close()
    c.drawPath(bottle, fill((90, 200, 140), 120))
    c.save()
    c.clipPath(bottle, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(-120, -150, 240, 480), shaded(linear((0, -150), (0, 330), [(255, 150, 60), (200, 70, 40)])))
    for k in range(26):
        ph = (t * (0.4 if popped else 0.04) + k / 26) % 1
        x = -80 + (k * 37) % 160
        y = 300 - 440 * ph
        c.drawCircle(x, y, 5 + (k % 3) * 3, stroke(WHITE, 2.5, 200))
    c.restore()
    c.drawPath(bottle, stroke(WHITE, 4, 150))
    c.drawRRect(rrect(-80, -40, 160, 120, 16), fill(WHITE, 230))
    text(c, "MAGMA", 0, 34, 34, INK, 255, 800, spacing=4)
    cap_y = -340 - (in_cubic(prog(t, POP_T, POP_T + 0.5)) * 500 if popped else 0)
    c.drawRRect(rrect(-42, cap_y, 84, 36, 8), fill(LAVA))
    if popped:
        for k in range(18):
            ph = prog(t, POP_T + k * 0.03, POP_T + 1.4 + k * 0.03)
            if 0 < ph < 1:
                a = -math.pi / 2 + (k - 9) * 0.07
                d = 420 * out_cubic(ph)
                c.drawCircle(d * math.cos(a), -330 + d * math.sin(a), 8 + 6 * (k % 3), fill(WHITE, 200 * (1 - ph)))
    c.restore()
    pill_tag(c, bx + 260, by + 120, "DISSOLVED GAS", WHITE, pop(t, GAS_T, 0.4), 26, down=False)


# ---------------------------------------------------------------- runny: gas escapes, lava flows
def cross_section_bg(c):
    c.drawRect(skia.Rect.MakeXYWH(-W, -1200, 3 * W, 1800), shaded(linear((0, -600), (0, 600), [(10, 10, 34), (70, 50, 120)])))
    c.drawRect(skia.Rect.MakeXYWH(-W, 600, 3 * W, H), shaded(linear((0, 600), (0, H), [CRUST_C, (110, 50, 60)])))


def draw_runny(c, t):
    cross_section_bg(c)
    vx = 960
    x, y = volcano(c, vx, 600, 1400, 230, (100, 84, 124), crater=0.12, hot=1.0, t=t)
    # cut-away conduit and chamber
    c.drawPath(poly([(vx - 30, y), (vx + 30, y), (vx + 50, 860), (vx - 50, 860)]), fill(LAVA))
    c.drawOval(skia.Rect.MakeXYWH(vx - 260, 840, 520, 160), fill(LAVA))
    glow(c, vx, 900, 340, LAVA, 120)
    for k in range(14):  # bubbles race up and pop
        ph = (t * 0.45 + k / 14) % 1
        bx_ = vx + 20 * math.sin(k * 2.1 + t) * (1 - ph)
        by_ = lerp(960, y, ph)
        c.drawCircle(bx_, by_, 9 + (k % 3) * 3, stroke(WHITE, 3, 230 * (1 - smooth(prog(ph, 0.9, 1)))))
    for k in range(10):  # gentle fountain
        ph = (t * 1.2 + k / 10) % 1
        a = -math.pi / 2 + (k - 4.5) * 0.12
        d = 140 * math.sin(math.pi * ph)
        c.drawCircle(x + d * math.cos(a) * 0.6, y - 120 * math.sin(math.pi * ph) + 20, 9, fill(LAVA_HOT, 230))
    for k, pts in enumerate([[(x - 20, y), (760, 470), (560, 540), (330, 600)], [(x + 20, y), (1160, 470), (1380, 540), (1620, 600)]]):
        lava_flow(c, pts, smooth(prog(t, RUNNY[1] + 0.5 + k * 0.4, RUNNY[1] + 4.5 + k * 0.4)), 22)
    _run_plume.draw(c, x, y - 120, t, 120, 30, 1.0, 0.25, 0.5)
    caption(c, "RUNNY MAGMA  ·  GAS ESCAPES", 960, 1030, LAVA_HOT, 30, 255 * smooth(prog(t, ESCAPE_T, ESCAPE_T + 0.4)))
    pill_tag(c, x, y - 230, "HAWAII", LAVA_HOT, pop(t, HAWAII_T, 0.4), 28)


# ---------------------------------------------------------------- sticky: trapped gas, pressure, BOOM
def draw_sticky(c, t):
    build = in_cubic(prog(t, *BUILD))
    boom = t >= BOOM
    shake = (14 * build + (40 * math.exp(-(t - BOOM) * 2.5) if boom else 0)) * math.sin(t * 47)
    c.save()
    c.translate(shake, shake * 0.6)
    zo = lerp(1.0, 0.6, in_out(prog(t, BOOM + 0.2, BOOM + 3.0)))  # pull back to see the whole column
    c.translate(960, 1000)
    c.scale(zo, zo)
    c.translate(-960, -1000)
    if zo < 1:
        c.drawPaint(shaded(linear((0, -800), (0, 600), [(10, 10, 34), (70, 50, 120)])))
    cross_section_bg(c)
    vx = 960
    x, y = volcano(c, vx, 600, 760, 440, (90, 76, 116), crater=0.1, hot=1.0 if boom else 0.3 * build, t=t)
    c.drawPath(poly([(vx - 26, y + 30), (vx + 26, y + 30), (vx + 50, 860), (vx - 50, 860)]), fill((170, 70, 50)))
    c.drawOval(skia.Rect.MakeXYWH(vx - 240, 840, 480, 160), fill((170, 70, 50)))
    if not boom:
        c.drawRRect(rrect(vx - 30, y + 10, 60, 40, 10), fill((70, 60, 80)))  # the plug
    rng = np.random.default_rng(2)
    for k in range(16):  # bubbles stuck in sticky magma, swelling
        bx_ = vx + rng.uniform(-200, 200) if k < 9 else vx + rng.uniform(-30, 30)
        by_ = rng.uniform(860, 980) if k < 9 else rng.uniform(y + 80, 840)
        r = (8 + 4 * (k % 3)) * (1 + 0.9 * build) * (0 if boom else 1)
        if r > 0:
            c.drawCircle(bx_, by_, r, stroke(WHITE, 3, 220))
    if boom:
        k = out_cubic(prog(t, BOOM, BOOM + 2.6))
        _stick_plume.draw(c, x, y - 10, t, 900 * k + 100, 200 * (0.4 + 0.6 * k), 1.0, 0.3)
        for (vx_, vy_, r) in BOMBS:
            u = t - BOOM
            if u < 2.4:
                bx_ = x + vx_ * u
                by_ = y + vy_ * u + 600 * u * u
                c.drawCircle(bx_, by_, r, fill((60, 50, 70)))
                glow(c, bx_, by_, r * 2, LAVA, 160 * max(0.0, 1 - u))
        ring = prog(t, BOOM, BOOM + 1.2)
        if ring < 1:
            c.drawCircle(x, y, 1600 * out_cubic(ring), stroke(WHITE, 14 * (1 - ring), 220 * (1 - ring)))
    c.restore()
    # pressure gauge
    if not boom or t < BOOM + 0.6:
        gx, gy = 1620, 300
        c.drawCircle(gx, gy, 120, fill(WHITE))
        c.drawCircle(gx, gy, 120, stroke(INK, 10))
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(gx - 96, gy - 96, 192, 192), 30, -60)
        c.drawPath(p, stroke((230, 60, 60), 16, 255, skia.Paint.kButt_Cap))
        ang = math.radians(lerp(-220, 25, build) + (8 * math.sin(t * 30) if build > 0.6 else 0))
        c.drawLine(gx, gy, gx + 84 * math.cos(ang), gy + 84 * math.sin(ang), stroke(INK, 9))
        c.drawCircle(gx, gy, 14, fill(INK))
        text(c, "PRESSURE", gx, gy + 170, 30, WHITE, 255, 800, spacing=6)
    caption(c, "STICKY MAGMA  ·  GAS TRAPPED", 960, 1030, LAVA_HOT, 30, 255 * smooth(prog(t, TRAP_T, TRAP_T + 0.4)) * (1 - smooth(prog(t, BOOM, BOOM + 0.2))))
    f = math.sin(math.pi * prog(t, BOOM - 0.05, BOOM + 0.35))
    if f > 0:
        c.drawPaint(fill((255, 240, 220), 230 * f))
    caption(c, "MOUNT PINATUBO  ·  1991", 960, 1030, WHITE, 30, 255 * smooth(prog(t, VO["E6"], VO["E6"] + 0.4)))


# ---------------------------------------------------------------- haze around the world, planet cools
def draw_haze(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(12, 12, 38), (26, 20, 66)])))
    Stars().draw(c, t)
    cx, cy, R = 820, 540, 360
    draw_globe(c, cx, cy, R, -t * 8 + 60)
    spread = smooth(prog(t, GLOBE[1], COOL_T + 1.5))
    c.save()
    c.clipPath(circle_path(cx, cy, R * 1.04), doAntiAlias=True)
    for k in range(3):
        w = R * (0.25 + 0.9 * spread) * (1 - k * 0.25)
        c.drawOval(skia.Rect.MakeXYWH(cx - R * 1.1, cy + 40 - w / 2, R * 2.2, w), blur(fill((230, 220, 170), 70), 26))
    for k in range(40):
        ph = (t * 0.05 + k / 40) % 1
        x = cx - R + 2 * R * ph
        y = cy + 40 + (k % 7 - 3) * R * 0.12 * spread
        c.drawCircle(x, y, 4, fill((240, 230, 190), 150 * spread))
    c.restore()
    c.drawCircle(cx, cy, R * 1.06, stroke((230, 220, 170), 10, 90 * spread))
    caption(c, "ASH + GAS SPREAD AROUND THE WORLD", cx, 1010, (240, 230, 190), 28, 255 * smooth(prog(t, GLOBE[1], GLOBE[1] + 0.4)))
    level = lerp(0.62, 0.48, smooth(prog(t, HALF_T, HALF_T + 1.2)))
    tc = mix((255, 120, 90), CYAN, smooth(prog(t, HALF_T, HALF_T + 1.2)))
    thermometer(c, 1480, 260, level, tc, None, 420)
    g = pop(t, HALF_T + 0.4, 0.5)
    pill_tag(c, 1640, 520, "−0.5 °C", CYAN, g, 34, down=False)
    text(c, "GLOBAL AVERAGE", 1500, 860 + 60, 24, WHITE, 220 * smooth(prog(t, COOL_T, COOL_T + 0.5)), 800, spacing=4)


# ---------------------------------------------------------------- compose
def draw_frame(c, t):
    c.clear(col(NAVY))
    scenes(c, t, [((0.0, 0.01), SODA[1], draw_intro), (SODA, RUNNY[1], draw_soda), (RUNNY, STICKY[1], draw_runny),
                  (STICKY, GLOBE[1], draw_sticky), (GLOBE, DURATION + 1, draw_haze)])
    vignette(c)
    chapter_fade(c, t, DURATION)


def sfx_events():
    return [(0.4, "rumble", 0.5), (1.6, "pop", 0.5), (SODA[0], "whoosh", 0.6), (GAS_T, "bubble", 0.5), (GAS_T + 0.2, "pop", 0.4),
            (POP_T, "pop", 1.0), (POP_T + 0.05, "sizzle", 0.8), (RUNNY[0], "whoosh", 0.6), (ESCAPE_T, "bubble", 0.7),
            (ESCAPE_T + 1.2, "bubble", 0.6), (RUNNY[1] + 1, "sizzle", 0.4), (HAWAII_T, "pop", 0.5),
            (STICKY[0], "whoosh", 0.6), (TRAP_T, "bubble", 0.4), (BUILD[0], "rumble", 0.8), (BUILD[0] + 2.4, "rumble", 1.0),
            (BUILD[0] + 3.5, "riser", 1.0), (BOOM, "boom", 1.0), (BOOM + 0.05, "whoosh_long", 1.0), (BOOM + 0.1, "rumble", 1.0),
            (BOOM + 1.5, "rumble", 0.8), (GLOBE[0], "whoosh_long", 0.6), (HALF_T, "riser", 0.4), (HALF_T + 0.4, "chime", 0.7)]


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 15, 19)), (4.4, 48, (0, 7, 12, 16, 19)), (9.1, 53, (0, 7, 12, 16, 19)),
            (16.8, 44, (0, 7, 12, 15, 18)), (24.0, 40, (0, 7, 12, 15, 19)), (30.0, 45, (0, 7, 12, 14, 19)),
            (35.0, 41, (0, 7, 11, 16, 19))],
    plucks=[(4.7, 16.6), (30.5, DURATION)], bpm=96, rises=[(BUILD[0], BUILD[1])],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
