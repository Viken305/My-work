"""LEVEL 4 · MAX HEART. The equaliser runner at full power over a racing ECG; the heart rate locks onto 180 with the
gold note; then four 5-litre jugs fill one after another (20 L a minute) and a 4X stamp lands.

  python3 render.py part5 [--still 2,4,6,8,10]
"""
from game import *  # noqa: F401,F403

PART = "part5"
G = Game(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
PREMIUM, SAMPLES = True, 4
T_PUSH = VO["D1"]
T_180 = G.w("D1", "one hundred and eighty")
T_D2 = VO["D2"]
T_20 = G.w("D2", "twenty")
T_EVERY = G.w("D2", "every")
T_4X = G.w("D2", "four")
T_REST = G.w("D2", "rest")
G.heart_fn = lambda t: lerp(150, 180, in_out(prog(t, T_PUSH, T_180 + 0.1))) + (2 * math.sin(t * 3) if t > T_180 + 0.5 else 0)


def ecg(c, t, y, a):
    """A heart trace racing right to left; one spike per beat."""
    pts = []
    for i in range(121):
        x = i * 9
        ph = G.phase(t - (W - x) / 900) % 1.0
        v = 0.0
        if ph < 0.06:
            v = -math.sin(ph / 0.06 * math.pi) * 0.25
        elif ph < 0.1:
            v = math.sin((ph - 0.06) / 0.04 * math.pi) * 1.0
        elif ph < 0.16:
            v = -math.sin((ph - 0.1) / 0.06 * math.pi) * 0.45
        elif 0.3 < ph < 0.42:
            v = math.sin((ph - 0.3) / 0.12 * math.pi) * 0.2
        pts.append((x, y - v * 200))
    p = path_of(pts)
    c.drawPath(p, stroke(RED, 16, 0.25 * a, plus=True))
    c.drawPath(p, stroke(mix(RED, WHITE, 0.3), 5, a))


def jugs(c, t):
    a = 255 * smooth(prog(t, T_D2 - 0.25, T_D2 + 0.2))
    if a <= 1:
        return
    label(c, "BLOOD PUMPED · EVERY MINUTE", 540, 430, 30, "mono_bold", (255, 170, 190), a, "center", tracking=0.08)
    fill = clamp(1 + 3 * in_out(prog(t, T_20 - 0.4, T_EVERY + 0.3)), 0, 4) if t > T_D2 else 1
    for i in range(4):
        x = 180 + i * 240
        y0, y1 = 520, 820
        q = clamp(fill - i)
        v = appear(t, T_D2 + 0.08 * i)
        c.save()
        c.translate(x, (y0 + y1) / 2)
        c.scale(v, v)
        c.translate(-x, -(y0 + y1) / 2)
        body = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 90, y0 + 30, x + 90, y1), 30, 30)
        c.drawRRect(body, fillp((30, 6, 16), a))
        c.save()
        c.clipRRect(body, skia.ClipOp.kIntersect, True)
        lvl = lerp(y1, y0 + 30, q)
        wave = skia.Path()
        wave.moveTo(x - 90, y1)
        for k in range(19):
            xx = x - 90 + k * 10
            wave.lineTo(xx, lvl + 8 * math.sin(t * 8 + k * 0.7 + i) * (0.3 + 0.7 * (0 < q < 1)))
        wave.lineTo(x + 90, y1)
        wave.close()
        c.drawPath(wave, grad_v(y0, y1, mix(RED, WHITE, 0.15), (140, 0, 30), a, a))
        c.restore()
        c.drawRRect(rrect(x - 40, y0, 80, 36, 10), stroke(RED, 6, a))
        c.drawRRect(body, stroke(RED if q > 0 else (120, 60, 90), 7, a))
        label(c, "5 L", x, y1 - 30, 40, "bungee", WHITE, a * (0.5 + 0.5 * (q > 0.99)), "center")
        c.restore()
    label(c, "AT REST", 180, 880, 26, "mono_bold", (255, 170, 190), a, "center", tracking=0.1)
    v = out_back(prog(t, T_4X, T_4X + 0.25), 2.5)
    if v > 0:                                              # the 4X stamp
        c.save()
        c.translate(540, 680)
        c.rotate(-8)
        c.scale(lerp(2.2, 1.0, v), lerp(2.2, 1.0, v))
        c.drawRRect(rrect(-210, -120, 420, 220, 30), fillp((20, 4, 10), 0.85 * a * min(1, v)))
        c.drawRRect(rrect(-210, -120, 420, 220, 30), stroke(GOLD, 12, a * min(1, v)))
        outlined(c, "4X", 0, 60, 190, "bungee", GOLD, a * min(1, v), glow_rgb=GOLD)
        c.restore()


def scene(c, t):
    k = smooth(prog(t, T_D2 - 0.35, T_D2))
    a = 255 * (1 - k)
    if a > 1:
        maxed = smooth(prog(t, T_180, T_180 + 0.2))
        ecg(c, t, 690, a * (0.5 + 0.5 * maxed))
        runner(c, G, t, 540, 680, 0.95 + 0.06 * maxed, a, level=lambda tt: 0.35 + 0.5 * maxed, rgb0=MAG, rgb1=RED)
        if t > T_180:
            u = prog(t, T_180, T_180 + 0.7)
            for j in range(3):
                uu = clamp(u * 1.4 - 0.2 * j)
                if 0 < uu < 1:
                    c.drawCircle(540, 610, 80 + 700 * out_cubic(uu), stroke(GOLD, 14 * (1 - uu) + 1, a * (1 - uu)))
            light(c, 540, 610, 500, GOLD, 120 * (1 - u) * a / 255)
            v = appear(t, T_180 + 0.15)
            c.save()
            c.translate(540, 425)
            c.scale(v, v)
            outlined(c, "MAX HEART RATE", 0, 0, 50, "bungee", GOLD, a * (v > 0), glow_rgb=RED)
            c.restore()
    jugs(c, t)


def draw_frame(c, t):
    G.frame(c, t, scene)
    if T_180 <= t < T_180 + 0.25:
        c.drawPaint(fillp(GOLD, 90 * (1 - prog(t, T_180, T_180 + 0.25))))


OVERLAY = G.overlay


def POST(t):
    k = 1 - prog(t, T_180, T_180 + 0.6) if t > T_180 else 0
    return dict(grain=3.5, ca=1.2 + 4 * k, bloom=1.1 + 0.4 * k)


def sfx_events():
    return G.sfx() + [(T_PUSH, "riser", 0.4), (T_180, "low_hit", 0.8), (T_20 - 0.3, "pour", 0.5), (T_4X, "stamp", 0.8)]


MUSIC = G.music()

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
