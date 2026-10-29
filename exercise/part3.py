"""LEVEL 2 · AIR. The lungs are two speakers that pump faster (12 -> 40 breaths a minute) while air streams in
(6 -> 100 litres a minute) and the VU meters climb; then red blood cells grab oxygen and race it to the muscle.

  python3 render.py part3 [--still 2,4,7,10,12]
"""
from frames2 import lung
from game import *  # noqa: F401,F403

PART = "part3"
G = Game(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
PREMIUM, SAMPLES = True, 4
T_12 = G.w("B1", "twelve")
T_40 = G.w("B1", "forty")
T_B2 = VO["B2"]
T_6 = G.w("B2", "six")
T_100 = G.w("B2", "hundred")
T_B3 = VO["B3"]
T_GRAB = G.w("B3", "grabs")
T_RACE = G.w("B3", "races")


def breaths(t):
    return lerp(12, 40, in_out(prog(t, T_12 + 0.3, T_40 + 0.2))) if t > T_12 else 12


def flow(t):
    return lerp(6, 100, in_out(prog(t, T_6 + 0.3, T_100 + 0.3))) if t > T_6 else 6


def breath_phase(t):
    """Visual breathing: slow at rest, fast at the end (integrated so the speed-up is smooth)."""
    ts = np.linspace(0, max(t, 1e-3), 120)
    trap = getattr(np, "trapezoid", None) or np.trapz
    return float(trap([breaths(x) / 60 * 2.2 for x in ts], ts))


def air(c, t, x, top, bot, a):
    sp = lerp(250, 1400, (flow(t) - 6) / 94)
    n = int(lerp(8, 34, (flow(t) - 6) / 94))
    for i in range(n):
        y = top + ((hsh(i, 9) * 900 + t * sp * (0.8 + 0.4 * hsh(i, 2))) % (bot - top))
        xx = x + (hsh(i, 4) - 0.5) * 40
        c.drawLine(xx, y - 40, xx, y, stroke(CYN, 6, a * 0.8))


def lungs(c, t, x, y, s, a):
    if a <= 1:
        return
    ph = breath_phase(t)
    br = 0.5 + 0.5 * math.sin(ph * 2 * math.pi)
    sc = s * (0.9 + 0.12 * br + 0.04 * G.beat(t))
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    c.drawLine(x, y - 260 * s, x, y - 130 * s, stroke(CYN, 16 * s))           # windpipe
    c.drawLine(x - 10, y - 130 * s, x - 80 * s, y - 60 * s, stroke(CYN, 12 * s))
    c.drawLine(x + 10, y - 130 * s, x + 80 * s, y - 60 * s, stroke(CYN, 12 * s))
    lung(c, x - 10, y, -1, sc, t, CYN)
    lung(c, x + 10, y, 1, sc, t, VIOLET)
    if a < 255:
        c.restore()


def vu(c, t, a):
    lvl = (flow(t) - 6) / 94 * 0.8 + 0.2 * G.beat(t) + 0.08
    for side, x in ((-1, 60), (1, 990)):
        for i in range(7):
            on = i / 7 < lvl + 0.05 * math.sin(t * 13 + side)
            col_ = LIME if i < 3 else (GOLD if i < 5 else MAG)
            c.drawRRect(rrect(x, 640 - i * 36, 30, 28, 6), fillp(col_ if on else (40, 30, 60), a))


def cells(c, t):
    a = 255 * smooth(prog(t, T_B3 - 0.2, T_B3 + 0.3))
    if a <= 1:
        return
    y0 = 640
    c.drawRRect(rrect(300, y0 - 80, 620, 160, 80), fillp((40, 6, 20), a))
    c.drawRRect(rrect(300, y0 - 80, 620, 160, 80), stroke(RED, 8, a))
    for i in range(14):                                    # lane markings speed past
        x = 920 - ((i * 60 + t * 700) % 620)
        c.drawLine(x, y0, x - 26, y0, stroke((120, 40, 60), 5, a))
    # the muscle at the end of the road
    mx = 880
    hitk = 0.0
    for i in range(7):
        c.drawRRect(rrect(mx - 40 + i * 2, y0 - 200 + i * 56, 140, 46, 23), fillp(mix(RED, (60, 0, 10), 0.3 + 0.1 * (i % 2)), a))
    sp = lerp(260, 900, smooth(prog(t, T_RACE, T_RACE + 0.5)))
    for i in range(6):
        u = ((t - T_B3) * sp / 640 + i / 6) % 1
        x = lerp(350, mx - 20, u)
        loaded = 0.12 < u < 0.94 and t > T_GRAB
        c.save()
        c.translate(x, y0 + (i % 2 - 0.5) * 50)
        c.drawOval(skia.Rect.MakeLTRB(-40, -24, 40, 24), fillp(RED, a))
        c.drawOval(skia.Rect.MakeLTRB(-18, -10, 18, 10), fillp((150, 10, 30), a))
        if loaded:
            for k in range(3):
                c.drawCircle(-22 + 22 * k, -34, 11, fillp(CYN, a))
                c.drawCircle(-22 + 22 * k, -34, 22, fillp(CYN, 0.25 * a))
        if t > T_RACE:
            for k in range(3):
                c.drawLine(-60 - 40 * k, -10 + 10 * k, -110 - 40 * k, -10 + 10 * k, stroke(WHITE, 4, 0.5 * a))
        c.restore()
        if u > 0.94:
            hitk = max(hitk, 1 - prog(u, 0.94, 1.0))
    light(c, mx + 30, y0, 240, CYN, 200 * hitk * a / 255)
    label(c, "O2", 360, y0 - 115, 44, "bungee", CYN, a * smooth(prog(t, T_GRAB, T_GRAB + 0.3)), "center")
    label(c, "MUSCLE", mx + 30, y0 - 225, 34, "bungee", RED, a, "center")


def scene(c, t):
    k = in_out(prog(t, T_B3 - 0.3, T_B3 + 0.4))
    lx, ly, ls = lerp(540, 190, k), lerp(650, 640, k), lerp(0.82, 0.48, k)
    air(c, t, lx, 380, ly - 230 * ls, 255)
    lungs(c, t, lx, ly, ls * appear(t, 1.1), 255)
    vu(c, t, 255 * (1 - k))
    cells(c, t)
    ca = 255 * (1 - k)
    v = appear(t, T_12 - 0.1)
    if v > 0 and ca > 1:
        c.save()
        c.translate(185, 820)
        c.scale(v, v)
        chip(c, 0, 0, "BREATHS/MIN", f"{int(round(breaths(t)))}", CYN, ca, size=70)
        c.restore()
    v = appear(t, T_6 - 0.1)
    if v > 0 and ca > 1:
        c.save()
        c.translate(895, 820)
        c.scale(v, v)
        chip(c, 0, 0, "AIR L/MIN", f"{int(round(flow(t)))}", VIOLET, ca, size=70)
        c.restore()


def draw_frame(c, t):
    G.frame(c, t, scene)


OVERLAY, POST = G.overlay, G.post


def sfx_events():
    ev = G.sfx() + [(T_40, "wind", 0.35), (T_100, "whoosh", 0.5), (T_RACE, "car_pass", 0.4)]
    return ev


MUSIC = G.music()

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
