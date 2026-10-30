"""0:10:00 · MEDICAL TAPE 7. An old educational video: a green phosphor cutaway of the body; the coffee drops into the
stomach, caffeine molecules seep through the gut wall into the red blood vessels and race off, while the ABSORBED
meter climbs to 99% by 45 minutes.

  python3 render.py part2 [--still 1.5,3,5,7.5]
"""
from tv import *  # noqa: F401,F403

PART = "part2"
G = Show(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
VHS, SAMPLES = True, 2
T_A1 = VO["A1"]
T_10 = G.w("A1", "ten")
T_SLIP = G.w("A1", "slipping")
T_BLOOD = G.w("A1", "blood")
T_A2 = VO["A2"]
T_45 = G.w("A2", "forty")
T_ALL = G.w("A2", "all")
PHOS = (90, 255, 140)
VESSEL = (255, 60, 70)
# the body (x, y): neck, shoulders, torso
BODY = [(380, 420), (380, 470), (200, 520), (170, 600), (190, 1130), (680, 1130), (700, 600), (670, 520), (490, 470), (490, 420)]
STOM = (500, 700)
AORTA = [(330, 440), (330, 1130)]
VEIN = [(600, 1130), (600, 760), (560, 520), (540, 440)]


def vessel_x(y):
    return 600 if y > 760 else lerp(560, 600, (y - 520) / 240) if y > 520 else lerp(540, 560, (y - 440) / 80)


def absorbed(t):
    return 99 * smooth(prog(t, T_SLIP, T_45 + 0.4)) ** 0.8


def gut_path():
    """The small intestine: a coiled tube under the stomach."""
    pts = []
    for i in range(160):
        u = i / 159
        a = u * 6 * math.pi
        pts.append((440 + 120 * math.sin(a) * (1 - 0.25 * u), 820 + 230 * u + 26 * math.cos(a)))
    return path_of(pts)


def on_path(pts, u):
    seg = [(math.dist(a, b)) for a, b in zip(pts, pts[1:])]
    d = u * sum(seg)
    for (a, b), s in zip(zip(pts, pts[1:]), seg):
        if d <= s:
            k = d / s
            return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
        d -= s
    return pts[-1]


def scene(c, t):
    gradient_bg(c, (6, 14, 60), (4, 8, 30))
    for x in range(0, W, 60):                               # oscilloscope grid
        c.drawLine(x, 390, x, H, stroke(PHOS, 1.5, 40))
    for y in range(390, H, 60):
        c.drawLine(0, y, W, y, stroke(PHOS, 1.5, 40))
    label(c, "FIG. 2  -  ABSORPTION", 70, 455, 44, "vt", PHOS, 220)
    # body outline, esophagus, stomach, gut
    c.drawPath(path_of(BODY), stroke(PHOS, 14, 50))
    c.drawPath(path_of(BODY), stroke(PHOS, 5, 255))
    c.drawPath(path_of([(435, 420), (440, 560), (470, 640)]), stroke(PHOS, 4, 230))
    st_ = skia.Path()
    st_.addOval(skia.Rect.MakeLTRB(STOM[0] - 100, STOM[1] - 70, STOM[0] + 100, STOM[1] + 70))
    c.save()
    c.rotate(-18, STOM[0], STOM[1])
    c.drawPath(st_, fillp(PHOS, 40))
    lvl = smooth(prog(t, 0.3, 1.2)) * (1 - 0.7 * smooth(prog(t, T_SLIP, T_45)))
    c.save()
    c.clipPath(st_, skia.ClipOp.kIntersect, True)
    top = STOM[1] + 70 - 120 * lvl
    c.drawRect(skia.Rect.MakeLTRB(STOM[0] - 110, top + 6 * math.sin(t * 5), STOM[0] + 110, STOM[1] + 80), fillp(BROWN, 230))
    c.restore()
    c.drawPath(st_, stroke(PHOS, 5))
    c.restore()
    c.drawPath(gut_path(), stroke(PHOS, 22, 60))
    c.drawPath(gut_path(), stroke(PHOS, 5, 230))
    # blood vessels, pulsing
    pul = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 1.2)
    for pts in (AORTA, VEIN):
        c.drawPath(path_of(pts), stroke(VESSEL, 26, 70 + 40 * pul))
        c.drawPath(path_of(pts), stroke(VESSEL, 10, 255))
    for y in (860, 960, 1060):                                # capillaries from the gut wall to the vessels
        c.drawLine(330, y, 380, y + 10, stroke(VESSEL, 5, 220))
        c.drawLine(600, y - 20, 560, y, stroke(VESSEL, 5, 220))
    # coffee drop down the esophagus at the start
    u = prog(t, 0.2, 1.0)
    if 0 < u < 1:
        x, y = on_path([(435, 420), (440, 560), (470, 640), (500, 700)], u)
        c.drawCircle(x, y, 18, fillp(BROWN))
        c.drawCircle(x, y, 18, stroke(PHOS, 3))
    # caffeine molecules: out of stomach / gut, through the wall, then away in the blood
    rate = smooth(prog(t, T_SLIP - 0.3, T_SLIP + 0.5)) * (1 - 0.6 * smooth(prog(t, T_ALL, T_ALL + 1.0)))
    for i in range(40):
        t0 = T_SLIP - 0.6 + i * 0.14
        if t < t0 or hsh(i, 9) > 0.35 + 0.65 * rate:
            continue
        uu = (t - t0) / 2.4
        if uu > 1:
            continue
        side = i % 2
        sx, sy = (STOM[0] - 40 + 80 * hsh(i, 1), STOM[1]) if i % 3 == 0 else (440 + 160 * (hsh(i, 2) - 0.5), 850 + 200 * hsh(i, 3))
        vx = 330 if side == 0 else 600
        ventry = (vx, sy)
        if uu < 0.35:                                      # through the gut wall into the nearest vessel
            x, y = lerp(sx, ventry[0], in_out(uu / 0.35)), lerp(sy, ventry[1], in_out(uu / 0.35))
        else:                                              # then carried up toward the heart
            y = lerp(sy, 440, in_cubic((uu - 0.35) / 0.65))
            x = vx if side == 0 else vessel_x(y)
        light(c, x, y, 40, ORANGE, 120)
        purine(c, x, y, 13, ORANGE, 255, 3.5)
    labs = [("STOMACH", 620, 650, 0.6), ("GUT", 600, 1060, T_SLIP - 0.4), ("BLOOD", 150, 640, T_BLOOD - 0.2)]
    for txt, x, y, t0 in labs:
        a = 255 * smooth(prog(t, t0, t0 + 0.3))
        if a > 1:
            c.drawRect(skia.Rect.MakeXYWH(x - 8, y - 38, width(txt, "vt", 46) + 16, 48), fillp(BLACK, 0.7 * a))
            label(c, txt, x, y, 46, "vt", PHOS if txt != "BLOOD" else VESSEL, a)
    # ABSORBED meter
    a = 255 * smooth(prog(t, T_10 - 0.3, T_10))
    if a > 1:
        x0, y0, y1 = 790, 560, 1100
        panel(c, x0, y0 - 110, 230, y1 - y0 + 150, (10, 40, 30), a)
        v = absorbed(t) / 100
        for k in range(20):
            on = k / 20 < v
            yy = y1 - 20 - k * 25
            c.drawRect(skia.Rect.MakeLTRB(x0 + 40, yy - 18, x0 + 190, yy), fillp(ORANGE if on else (30, 60, 40), a))
        label(c, f"{int(round(absorbed(t)))}%", x0 + 115, y0 - 40, 84, "vt", ORANGE, a, "center")
        label(c, "ABSORBED", x0 + 115, y0 - 2, 40, "vt", PHOS, a, "center")
    if t > T_45:                                              # 45 MIN stamp
        v = appear(t, T_45)
        c.save()
        c.translate(540, 860)
        c.rotate(-8)
        c.scale(v, v)
        c.drawRect(skia.Rect.MakeLTRB(-190, -70, 190, 40), fillp(BLACK, 200))
        c.drawRect(skia.Rect.MakeLTRB(-190, -70, 190, 40), stroke(ORANGE, 7))
        label(c, "ALMOST ALL IN", 0, 0, 62, "vt", ORANGE, 255, "center")
        c.restore()


def draw_frame(c, t):
    G.frame(c, t, scene)


OVERLAY = G.overlay


def POST(t):
    return G.post(t)


def sfx_events():
    return G.sfx() + [(0.9, "drip", 0.5), (T_SLIP, "boil", 0.3), (T_10, "tick_roll", 0.35), (T_45 - 0.2, "counter", 0.35),
                      (T_45 + 0.1, "stamp", 0.6)]


MUSIC = G.music()

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
