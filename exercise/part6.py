"""LEVEL 5 · HEAT. The runner smokes like a messy engine; an energy bar splits into 25% motion and 75% heat; the bars
turn to fire, a thermometer climbs, and sweat drips off the runner into a jug that fills to 1 litre.

  python3 render.py part6 [--still 2,4,6,8,10]
"""
from game import *  # noqa: F401,F403

PART = "part6"
G = Game(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
PREMIUM, SAMPLES = True, 4
T_MESSY = G.w("E1", "messy")
T_75 = G.w("E1", "seventy five percent")
T_HEAT = G.w("E1", "heat")
T_E2 = VO["E2"]
T_TEMP = G.w("E2", "temperature")
T_SWEAT = G.w("E2", "sweat")
T_1L = G.w("E2", "a litre")


def heat(t):
    return smooth(prog(t, T_75, T_HEAT + 0.3))


def temp(t):
    return lerp(37.0, 38.5, in_out(prog(t, T_TEMP - 0.2, T_SWEAT)))


def energy_bar(c, t):
    a = 255 * smooth(prog(t, T_MESSY, T_MESSY + 0.3)) * (1 - smooth(prog(t, T_E2 - 0.3, T_E2)))
    if a <= 1:
        return
    x0, x1, y = 90, 990, 430
    label(c, "ENERGY USED", x0, y - 22, 28, "mono_bold", (255, 200, 160), a, "left", tracking=0.1)
    c.drawRRect(rrect(x0, y, x1 - x0, 64, 20), fillp((30, 20, 40), a))
    k = out_cubic(prog(t, T_75 - 0.1, T_75 + 0.6))
    split = x0 + (x1 - x0) * 0.25
    c.drawRRect(rrect(x0, y, (split - x0) * k + 1, 64, 20), fillp(CYN, a))
    c.drawRRect(rrect(split, y, (x1 - split) * k, 64, 20), fillp(ORANGE, a))
    if k > 0.5:
        label(c, "25% MOVE", x0 + 16, y + 46, 30, "bungee", (0, 30, 40), a, "left")
        label(c, "75% HEAT", x1 - 20, y + 46, 34, "bungee", (60, 10, 0), a, "right")
        light(c, (split + x1) / 2, y + 32, 400, ORANGE, 90 * a / 255)


def smoke(c, t, a):
    for i in range(18):
        t0 = T_MESSY - 0.2 + i * 0.12
        u = prog(t, t0, t0 + 1.6)
        if not 0 < u < 1:
            continue
        x = 540 + (hsh(i, 1) - 0.5) * 360 + 60 * math.sin(u * 4 + i)
        y = 640 - 300 * u
        c.drawCircle(x, y, 30 + 70 * u, fillp((120, 110, 130), 90 * (1 - u) * a / 255))


def shimmer(c, t, k):
    for i in range(14):
        x = 340 + i * 30
        p = skia.Path()
        p.moveTo(x, 900)
        for j in range(1, 12):
            y = 900 - j * 45
            p.lineTo(x + 14 * math.sin(t * 7 + j * 0.9 + i), y)
        c.drawPath(p, stroke(ORANGE, 3, 70 * k))


def thermometer(c, t, a):
    if a <= 1:
        return
    x, y0, y1 = 120, 440, 830
    c.drawRRect(rrect(x - 26, y0, 52, y1 - y0, 26), fillp((30, 20, 40), a))
    c.drawCircle(x, y1 + 20, 46, fillp(RED, a))
    q = (temp(t) - 36.5) / 2.5
    top = lerp(y1, y0 + 20, q)
    c.drawRRect(rrect(x - 14, top, 28, y1 + 10 - top, 14), fillp(RED, a))
    light(c, x, top, 120, RED, 120 * a / 255)
    c.drawRRect(rrect(x - 26, y0, 52, y1 - y0, 26), stroke(WHITE, 4, a))
    for k in range(5):
        yy = lerp(y1 - 40, y0 + 40, k / 4)
        c.drawLine(x + 30, yy, x + 46, yy, stroke(WHITE, 3, 0.6 * a))
    label(c, "CORE", x, y0 - 50, 26, "mono_bold", (255, 180, 180), a, "center", tracking=0.1)
    outlined(c, f"{temp(t):.1f}°", x + 90, top + 20, 54, "bungee", WHITE, a, "left", glow_rgb=RED)


def sweat(c, t, a):
    if a <= 1:
        return
    k = smooth(prog(t, T_SWEAT - 0.2, T_SWEAT + 0.3))
    for i in range(int(30 * k)):                          # drops fall off the bars
        u = ((t - T_SWEAT) * (0.9 + 0.4 * hsh(i, 2)) + hsh(i, 1)) % 1
        x = 400 + hsh(i, 3) * 280
        y = lerp(560 + 200 * hsh(i, 4), 940, u ** 1.6)
        p = skia.Path()
        p.moveTo(x, y - 22)
        p.cubicTo(x + 13, y - 2, x + 13, y + 12, x, y + 12)
        p.cubicTo(x - 13, y + 12, x - 13, y - 2, x, y - 22)
        c.drawPath(p, fillp(CYN, a * (1 - u * 0.3)))
    # the jug fills to the 1 L line
    x, y0, y1 = 930, 560, 860
    q = 0.92 * smooth(prog(t, T_SWEAT, T_1L + 0.4)) + 0.04 * math.sin(t * 8) * k
    c.drawRRect(rrect(x - 80, y0, 160, y1 - y0, 24), fillp((10, 20, 40), a))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 80, y0, x + 80, y1), 24, 24), skia.ClipOp.kIntersect, True)
    c.drawRect(skia.Rect.MakeLTRB(x - 80, lerp(y1, y0, q), x + 80, y1), fillp(CYN, 0.85 * a))
    c.restore()
    c.drawRRect(rrect(x - 80, y0, 160, y1 - y0, 24), stroke(CYN, 6, a))
    yl = lerp(y1, y0, 0.88)
    c.drawLine(x - 80, yl, x - 30, yl, stroke(WHITE, 5, a))
    label(c, "1 L", x - 20, yl + 14, 34, "bungee", WHITE, a, "left")
    label(c, "SWEAT / HOUR", x, y0 - 22, 24, "mono_bold", CYN, a, "center", tracking=0.08)


def scene(c, t):
    h = heat(t)
    energy_bar(c, t)
    shimmer(c, t, h)
    runner(c, G, t, 540, 690, 0.85, 255, heat=h, rgb0=MAG, rgb1=ORANGE)
    smoke(c, t, 255 * (1 - smooth(prog(t, T_E2 - 0.3, T_E2))))
    if h > 0:                                             # flames lick up the runner
        for i in range(14):
            x = 380 + i * 22
            hgt = (40 + 50 * hsh(i, 2) + 30 * math.sin(t * 15 + i)) * h
            base = 940 - 60 * math.sin(i / 13 * math.pi)
            p = skia.Path()
            p.moveTo(x - 16, base)
            p.quadTo(x - 10, base - hgt * 0.6, x + 4 * math.sin(t * 9 + i), base - hgt)
            p.quadTo(x + 10, base - hgt * 0.6, x + 16, base)
            p.close()
            c.drawPath(p, fillp(mix(ORANGE, GOLD, hsh(i, 5)), 200))
    ta = 255 * smooth(prog(t, T_E2 - 0.1, T_E2 + 0.3))
    thermometer(c, t, ta)
    sweat(c, t, ta)


def draw_frame(c, t):
    G.frame(c, t, scene)
    k = heat(t) * (0.7 + 0.3 * G.beat(t))
    if k > 0:
        c.drawPaint(skia.Paint(Color=skia.Color(255, 90, 20, int(26 * k)), BlendMode=skia.BlendMode.kPlus))


OVERLAY = G.overlay


def POST(t):
    k = heat(t)
    return dict(grain=3.5, ca=1.2 + 0.8 * k, bloom=1.1 + 0.25 * k, wobble=2.5 * k)


def sfx_events():
    return G.sfx() + [(T_MESSY, "metal_clank", 0.4), (T_75, "heat_roar", 0.5), (T_SWEAT, "drip", 0.6), (T_SWEAT + 0.4, "drip", 0.5),
                      (T_SWEAT + 0.8, "drip", 0.5), (T_1L, "pour", 0.4)]


MUSIC = G.music()

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
