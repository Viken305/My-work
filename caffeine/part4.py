"""1:00:00 · THE BODY FORECAST (the peak). A 90s weather report: the body is the map; a lightning front (adrenaline),
a HIGH pressure system over the heart and sunshine over the brain (dopamine) roll in with their forecast tiles; then
"SHARP & FOCUSED" sunshine; then the Doppler gut radar lights up: GUT ALERT, 1 IN 3.

  python3 render.py part4 [--still 2,3.5,5.5,7.5,9.5,11.5]
"""
from tv import *  # noqa: F401,F403

PART = "part4"
G = Show(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
VHS, SAMPLES = True, 2
T_ADR = G.w("C1", "adrenaline")
T_BP = G.w("C1", "blood")
T_DOPA = G.w("C1", "dopamine")
T_C2 = VO["C2"]
T_SHARP = G.w("C2", "sharp")
T_C3 = VO["C3"]
T_ONE = G.w("C3", "one")
T_GUT = G.w("C3", "gut")
LAND = (120, 205, 120)
HEAD, HEART, ADRENAL, BELLY = (300, 500), (335, 680), (250, 800), (300, 900)


def sun(c, x, y, r, t, a=255):
    for k in range(12):
        ang = math.radians(k * 30 + t * 40)
        c.drawLine(x + r * 1.25 * math.cos(ang), y + r * 1.25 * math.sin(ang), x + r * 1.7 * math.cos(ang), y + r * 1.7 * math.sin(ang),
                   stroke(YELLOW, r * 0.22, a))
    light(c, x, y, r * 3, YELLOW, 90 * a / 255)
    c.drawCircle(x, y, r, fillp(YELLOW, a))
    c.drawCircle(x, y, r, stroke(ORANGE, r * 0.12, a))


def bolt(c, x, y, s, a=255):
    p = path_of([(x + 10 * s, y - 50 * s), (x - 22 * s, y + 6 * s), (x + 2 * s, y + 6 * s), (x - 12 * s, y + 50 * s),
                 (x + 26 * s, y - 10 * s), (x + 2 * s, y - 10 * s)], True)
    c.drawPath(p, fillp(YELLOW, a))
    c.drawPath(p, stroke(ORANGE, 4 * s, a))


def high(c, x, y, s, a=255):
    c.drawCircle(x, y, 44 * s, fillp(RED, a))
    c.drawCircle(x, y, 44 * s, stroke(WHITE, 5 * s, a))
    label(c, "H", x, y + 26 * s, 74 * s, "archivo", WHITE, a, "center")


def body_map(c, t):
    gradient_bg(c, (30, 70, 190), (10, 25, 90))
    for x in range(-40, W, 90):
        c.drawLine(x, 390, x + 60, H, stroke(WHITE, 2, 30))
    for y in range(420, H, 90):
        c.drawLine(0, y, W, y + 20, stroke(WHITE, 2, 30))
    land = skia.Path()
    land.addCircle(HEAD[0], HEAD[1], 64)
    land.addRect(skia.Rect.MakeLTRB(275, 550, 325, 600))
    land.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(185, 585, 415, 930), 60, 60))
    for side in (-1, 1):
        arm = skia.Path()
        arm.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-32, 0, 32, 330), 30, 30))
        m = skia.Matrix()
        m.setRotate(side * -14)
        m.postTranslate(300 + side * 135, 600)
        arm.transform(m)
        land.addPath(arm)
        land.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(300 + side * 60 - 42, 880, 300 + side * 60 + 42, 1160), 36, 36))
    c.save()
    c.translate(12, 14)
    c.drawPath(land, fillp(BLACK, 90))
    c.restore()
    c.drawPath(land, fillp(LAND))
    c.drawPath(land, stroke((40, 110, 50), 6))
    for x, y, name in ((395, 455, "BRAINVILLE"), (400, 640, "HEART CITY")):
        c.drawCircle(x - 18, y - 12, 7, fillp(WHITE))
        label(c, name, x, y, 36, "vt", WHITE, 230)


def tile(c, x, y, w, h, title, value, icon, t, t0, a=255, rgb=BLUE):
    v = appear(t, t0)
    if v <= 0 or a <= 1:
        return
    c.save()
    c.translate(x + w / 2, y + h / 2)
    c.scale(1, v)
    c.translate(-x - w / 2, -y - h / 2)
    panel(c, x, y, w, h, rgb, a, 14)
    icon(c, x + 70, y + h / 2, a)
    label(c, title, x + 140, y + 58, 40, "righteous", WHITE, a)
    label(c, value, x + 140, y + 110, 46, "vt", YELLOW, a)
    c.restore()


def scene(c, t):
    body_map(c, t)
    # weather moving in over the body
    if t > T_ADR - 0.2:
        v = appear(t, T_ADR - 0.2)
        for k in range(3):
            bolt(c, ADRENAL[0] - 40 + 40 * k, ADRENAL[1] + 10 * math.sin(t * 6 + k), 0.7 * v * (0.8 + 0.3 * (int(t * 8 + k) % 2)))
    if t > T_BP - 0.1:
        high(c, HEART[0], HEART[1], appear(t, T_BP - 0.1) * (1 + 0.06 * math.sin(t * 8)))
    if t > T_DOPA - 0.1:
        k = 1 + 0.35 * smooth(prog(t, T_SHARP - 0.2, T_SHARP + 0.3))
        sun(c, HEAD[0], HEAD[1] - 10, 40 * appear(t, T_DOPA - 0.1) * k, t)
    # forecast tiles
    fa = 255 * (1 - smooth(prog(t, T_C3 - 0.2, T_C3 + 0.2)))
    tile(c, 570, 440, 460, 140, "ADRENALINE", "RISING", lambda c, x, y, a: bolt(c, x, y, 0.8, a), t, T_ADR - 0.1, fa)
    tile(c, 570, 600, 460, 140, "BLOOD PRESS.", "TICKING UP", lambda c, x, y, a: high(c, x, y, 0.8, a), t, T_BP - 0.1, fa)
    tile(c, 570, 760, 460, 140, "DOPAMINE", "MOOD: SUNNY", lambda c, x, y, a: sun(c, x, y, 26, t, a), t, T_DOPA - 0.1, fa)
    v = appear(t, T_C2 - 0.1)
    if v > 0 and fa > 1:
        c.save()
        c.translate(800, 1010)
        c.rotate(-4)
        c.scale(v, v)
        panel(c, -230, -80, 460, 160, ORANGE, fa, 18)
        outlined(c, "SHARP &", 0, -10, 52, "righteous", WHITE, fa, ow=0.08)
        outlined(c, "FOCUSED", 0, 54, 60, "archivo", YELLOW, fa, ow=0.08)
        c.restore()
    # Doppler gut radar
    a = 255 * smooth(prog(t, T_C3 - 0.1, T_C3 + 0.3))
    if a > 1:
        cx, cy, r = BELLY[0], BELLY[1], 170
        c.drawCircle(cx, cy, r, fillp((0, 30, 10), 0.7 * a))
        for k in (1, 2, 3):
            c.drawCircle(cx, cy, r * k / 3, stroke(LIME, 3, 0.7 * a))
        hot = smooth(prog(t, T_GUT - 0.6, T_GUT + 0.2))
        for i in range(9):                                   # storm cells, growing hotter toward "gut"
            bx = cx + (hsh(i, 1) - 0.5) * r * 1.1
            by = cy + (hsh(i, 2) - 0.5) * r * 1.1
            br = (24 + 30 * hsh(i, 3)) * (0.6 + 0.6 * hot) * (1 + 0.1 * math.sin(t * 5 + i))
            for rr, rgb in ((1.0, LIME), (0.65, YELLOW), (0.35, RED)):
                if rgb == RED and hot < 0.4:
                    continue
                c.drawCircle(bx, by, br * rr, fillp(rgb, 0.85 * a))
        ang = t * 4
        c.drawLine(cx, cy, cx + r * math.cos(ang), cy + r * math.sin(ang), stroke(LIME, 6, a))
        c.drawCircle(cx, cy, r, stroke(LIME, 6, a))
        c.drawRect(skia.Rect.MakeLTRB(cx - 175, cy + r + 12, cx + 175, cy + r + 62), fillp(BLACK, 0.75 * a))
        label(c, "DOPPLER GUT RADAR", cx, cy + r + 50, 42, "vt", LIME, a, "center")
        if t > T_GUT - 0.1 and int(t * 4) % 2 == 0:
            c.drawRect(skia.Rect.MakeLTRB(580, 520, 1030, 610), fillp(RED, a))
            label(c, "GUT ALERT!", 805, 588, 66, "archivo", WHITE, a, "center")
        v = appear(t, T_ONE - 0.1)
        if v > 0:
            c.save()
            c.translate(800, 820)
            c.rotate(8)
            c.scale(v, v)
            starburst(c, 0, 0, 130, 175, 16, YELLOW, t * 10)
            outlined(c, "1 IN 3", 0, 18, 74, "bowlby", RED, a, ow=0.08)
            label(c, "PEOPLE", 0, 70, 34, "archivo", NAVY, a, "center")
            c.restore()


def draw_frame(c, t):
    G.frame(c, t, scene)


OVERLAY = G.overlay


def POST(t):
    return G.post(t)


def sfx_events():
    return G.sfx() + [(FF + 0.1, "chime", 0.5), (T_ADR, "static", 0.35), (T_BP, "pop", 0.45), (T_DOPA, "shimmer", 0.4),
                      (T_SHARP, "ding", 0.4), (T_C3, "radar", 0.5), (T_C3 + 1.2, "radar", 0.4), (T_GUT - 0.2, "gurgle", 0.6),
                      (T_ONE, "stamp", 0.4)]


MUSIC = G.music()

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
