"""5:00:00 · CAFFEINE MARKETS (the half-life). A 90s market report: the CAFF index falls slowly as the liver works
through it; after 5 hours it is still at 50% (flashing); then the SLEEP REPORT: a big dose six hours before bed cuts
about an hour off the night. A stock ticker crawls along the bottom.

  python3 render.py part5 [--still 2,4,6,7.5,9.5,12]
"""
from tv import *  # noqa: F401,F403

PART = "part5"
G = Show(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
VHS, SAMPLES = True, 2
T_LIVER = G.w("D1", "liver")
T_SLOW = G.w("D1", "slowly")
T_FIVE = G.w("D1", "five")
T_HALF = G.w("D1", "half")
T_D2 = VO["D2"]
T_BED = G.w("D2", "bed")
T_CUT = G.w("D2", "cut")
GREEN_UP = (60, 230, 90)
CX0, CX1, CY0, CY1 = 150, 990, 540, 820           # chart plot area
HMAX = 8.0


def level(h):
    return 100 * 0.5 ** (h / 5)


def drawn_h(t):
    """Hours shown on the chart: reaches +5 h exactly on "half", then creeps on."""
    return 5 * in_out(prog(t, FF + 0.2, T_HALF)) ** 0.9 + 0.6 * smooth(prog(t, T_HALF + 0.4, T_D2))


def to_xy(h, v):
    return lerp(CX0, CX1, h / HMAX), lerp(CY1, CY0, v / 100)


def chart(c, t, a):
    if a <= 1:
        return
    panel(c, 50, 420, 980, 600, (16, 30, 90), a, 10)
    label(c, "CAFF INDEX", 80, 486, 54, "archivo", WHITE, a)
    h = drawn_h(t)
    v = level(h)
    label(c, f"{v:5.1f}", 1000, 486, 64, "vt", YELLOW, a, "right")
    label(c, f"-{100 - v:.1f}%", 820, 486, 40, "vt", RED, a, "right")
    for k in range(5):                                    # grid and axes
        y = lerp(CY1, CY0, k / 4)
        c.drawLine(CX0, y, CX1, y, stroke(WHITE, 2, 0.15 * a))
        label(c, f"{25 * k}%", CX0 - 14, y + 12, 34, "vt", WHITE, 0.7 * a, "right")
    for k in range(0, 9, 2):
        x, _ = to_xy(k, 0)
        c.drawLine(x, CY0, x, CY1, stroke(WHITE, 2, 0.12 * a))
        label(c, clock12(3600 * (k + 1))[3:], x, CY1 + 42, 34, "vt", WHITE, 0.7 * a, "center")
    pts = [to_xy(h * i / 80, level(h * i / 80)) for i in range(81)]
    fillpath = path_of(pts + [(pts[-1][0], CY1), (CX0, CY1)], True)
    c.drawPath(fillpath, grad_v(CY0, CY1, YELLOW, YELLOW, 0.35 * a, 0.02 * a))
    c.drawPath(path_of(pts), stroke(YELLOW, 7, a))
    hx, hy = pts[-1]
    light(c, hx, hy, 60, YELLOW, 140 * a / 255)
    c.drawCircle(hx, hy, 11, fillp(WHITE, a))
    # the 5-hour marker and the 50% line
    if t > T_FIVE - 0.2:
        k = smooth(prog(t, T_FIVE - 0.2, T_FIVE + 0.3))
        x5, y5 = to_xy(5, 50)
        for y in range(int(CY0), int(CY1), 26):
            c.drawLine(x5, y, x5, min(CY1, y + 14), stroke(WHITE, 4, a * k))
        label(c, "+5 HRS", x5, CY0 - 10, 38, "vt", WHITE, a * k, "center")
    if t > T_HALF - 0.1:
        k = smooth(prog(t, T_HALF - 0.1, T_HALF + 0.3))
        x5, y5 = to_xy(5, 50)
        c.drawLine(CX0, y5, CX0 + (CX1 - CX0) * k, y5, stroke(RED, 5, a))
        c.drawCircle(x5, y5, 18, stroke(RED, 6, a * k))
        if int(t * 3) % 3 != 0:
            c.drawRect(skia.Rect.MakeLTRB(x5 - 290, y5 - 130, x5 - 10, y5 - 30), fillp(RED, a * k))
            label(c, "50% STILL", x5 - 150, y5 - 86, 50, "vt", WHITE, a * k, "center")
            label(c, "IN YOUR BLOOD", x5 - 150, y5 - 44, 40, "vt", WHITE, a * k, "center")


def liver(c, t, a):
    """The liver at work: a little conveyor that slowly eats molecules."""
    if a <= 1:
        return
    v = appear(t, T_LIVER - 0.1)
    c.save()
    c.translate(240, 950)
    c.scale(v, v)
    lp = skia.Path()
    lp.moveTo(-140, -30)
    lp.cubicTo(-60, -80, 120, -70, 140, -30)
    lp.cubicTo(150, 10, 60, 50, -20, 40)
    lp.cubicTo(-90, 34, -150, 10, -140, -30)
    c.drawPath(lp, fillp((150, 50, 50), a))
    c.drawPath(lp, stroke((255, 140, 120), 5, a))
    for k in range(2):
        c.drawCircle(-40 + 50 * k, -10, 11, fillp(WHITE, a))
        c.drawCircle(-40 + 50 * k + 3 * math.sin(t * 6), -10, 5, fillp(BLACK, a))
    c.restore()
    if v > 0.5:
        dots = "." * (int(t * 3) % 4)
        label(c, "LIVER: WORKING" + dots, 410, 958, 46, "vt", (255, 160, 140), a)
        label(c, "SLOWLY", 410, 1000, 40, "vt", WHITE, 0.7 * a * smooth(prog(t, T_SLOW, T_SLOW + 0.3)))


def sleep_report(c, t, a):
    if a <= 1:
        return
    panel(c, 50, 420, 980, 600, (40, 20, 90), a, 10)
    label(c, "SLEEP REPORT", 80, 486, 54, "archivo", WHITE, a)
    mx, my = 940, 470                                     # the moon
    c.drawCircle(mx, my, 38, fillp((255, 240, 180), a))
    c.drawCircle(mx + 18, my - 12, 34, fillp((40, 20, 90), a))
    rows = [("NO CAFFEINE", 0.0, WHITE), ("BIG DOSE, 6 HRS", 1.0, ORANGE)]
    for r, (name, cut, rgb) in enumerate(rows):
        y = 610 + r * 200
        label(c, name, 90, y - 18, 44, "vt", rgb, a)
        n = 8
        k = smooth(prog(t, T_CUT - 0.1, T_CUT + 0.5)) * cut
        grow = smooth(prog(t, T_D2 + 0.2 + 0.3 * r, T_D2 + 1.0 + 0.3 * r))
        for i in range(n):
            if i / n > grow:
                continue
            x = 90 + i * 112
            lost = i == n - 1 and cut > 0
            box = fillp(RED if lost and k > 0.5 else mix(PURPLE, SKY, 0.5), a * (1 - 0.75 * k if lost else 1))
            c.drawRRect(rrect(x, y, 100, 80, 10), box)
            if lost and k > 0.5:
                c.drawLine(x + 10, y + 10, x + 90, y + 70, stroke(WHITE, 8, a))
                c.drawLine(x + 90, y + 10, x + 10, y + 70, stroke(WHITE, 8, a))
        if cut and k > 0.3:
            v = appear(t, T_CUT + 0.1)
            c.save()
            c.translate(620, y + 150)
            c.rotate(-6)
            c.scale(v, v)
            starburst(c, 0, 0, 62, 88, 14, YELLOW, t * 12)
            outlined(c, "-1 HR", 0, 16, 54, "bowlby", RED, a, ow=0.08)
            c.restore()
    label(c, "BEFORE BED", 90, 970, 40, "vt", ORANGE, a * smooth(prog(t, T_BED - 0.1, T_BED + 0.2)))


def ticker(c, t):
    c.drawRect(skia.Rect.MakeLTRB(0, 1060, W, 1130), fillp((0, 0, 30)))
    c.drawRect(skia.Rect.MakeLTRB(0, 1060, W, 1066), fillp(YELLOW))
    msg = "CAFF -50%   *   ADENOSINE +   *   LIVER: HARD AT WORK   *   SLEEP -1 HR   *   DECAF +0.0   *   "
    f = font("vt", 56)
    wd = f.measureText(msg)
    x = -(t * 160 % wd)
    while x < W:
        i = 0
        for part in msg.split("   "):
            rgb = RED if "-" in part else GREEN_UP if "+" in part else YELLOW if "*" in part else WHITE
            c.drawString(part, x + f.measureText(msg[:i]), 1114, f, fillp(rgb))
            i += len(part) + 3
        x += wd


def scene(c, t):
    gradient_bg(c, (8, 14, 60), (2, 4, 24))
    for y in range(400, H, 40):
        c.drawLine(0, y, W, y, stroke(BLUE, 1, 40))
    k = smooth(prog(t, T_D2 - 0.35, T_D2 + 0.05))
    c.save()
    c.translate(-W * in_out(k), 0)
    chart(c, t, 255)
    liver(c, t, 255)
    c.restore()
    c.save()
    c.translate(W * (1 - in_out(k)), 0)
    sleep_report(c, t, 255 * (k > 0))
    c.restore()
    ticker(c, t)


def draw_frame(c, t):
    G.frame(c, t, scene)


OVERLAY = G.overlay


def POST(t):
    return G.post(t)


def sfx_events():
    return G.sfx() + [(FF + 0.1, "cash", 0.5), (T_LIVER, "pop", 0.4), (T_FIVE, "tick_roll", 0.3), (T_HALF, "buzzer", 0.3),
                      (T_D2 - 0.3, "whoosh", 0.4), (T_CUT + 0.1, "stamp", 0.6)]


MUSIC = G.music()

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
