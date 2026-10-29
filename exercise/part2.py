"""LEVEL 1 · IGNITION. The brain fires a signal down to the adrenal glands, adrenaline floods out; a blood vessel opens
wide; then the body's blood flow as a mixing desk: the MUSCLE fader goes from 20% to 80% while the others drop.

  python3 render.py part2 [--still 2,4,7,12,15]
"""
from game import *  # noqa: F401,F403

PART = "part2"
G = Game(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
PREMIUM, SAMPLES = True, 4
T_FIRE = G.w("A1", "fires")
T_ADR = G.w("A1", "adrenaline")
T_A2 = VO["A2"]
T_OPEN = G.w("A2", "open")
T_A3 = VO["A3"]
T_20 = G.w("A3", "twenty")
T_GO = G.w("A3", "go")
T_80 = G.w("A3", "eighty")
BRAIN, KID = (540, 470), (540, 820)
CH = [("BRAIN", 0.15, 0.04, VIOLET), ("GUT", 0.25, 0.04, CYN), ("KIDNEY", 0.20, 0.03, LIME),
      ("SKIN", 0.10, 0.09, GOLD), ("MUSCLE", 0.20, 0.80, MAG)]


def brain(c, x, y, s, rgb, a=255, glow=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    light(c, 0, 0, 260, rgb, (60 + 140 * glow) * a / 255)
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(-150, -100, 150, 100))
    c.drawPath(p, fillp(mix(rgb, (0, 0, 0), 0.75), a))
    c.drawPath(p, stroke(rgb, 7, a))
    c.drawLine(0, -98, 0, 98, stroke(rgb, 5, a))
    for k in range(6):                                   # folds
        sx = -1 if k % 2 else 1
        yy = -60 + 24 * k
        q = skia.Path()
        q.moveTo(sx * 20, yy)
        q.cubicTo(sx * 60, yy - 30, sx * 90, yy + 30, sx * 128, yy - 6)
        c.drawPath(q, stroke(mix(rgb, WHITE, 0.4), 4, a * 0.8))
    c.restore()


def kidney(c, x, y, s, rgb, a=255, glow=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for sx in (-1, 1):
        p = skia.Path()
        p.moveTo(sx * 40, -70)
        p.cubicTo(sx * 150, -110, sx * 170, 90, sx * 60, 80)
        p.cubicTo(sx * 20, 70, sx * 70, 10, sx * 40, -70)
        c.drawPath(p, fillp(mix(RED, (0, 0, 0), 0.7), a))
        c.drawPath(p, stroke(RED, 6, a))
        g = path_of([(sx * 40, -78), (sx * 120, -88), (sx * 70, -140)], True)      # the adrenal gland sits on top
        light(c, sx * 80, -100, 160, rgb, (40 + 200 * glow) * a / 255)
        c.drawPath(g, fillp(mix(rgb, WHITE, 0.3 * glow), a))
        c.drawPath(g, stroke(WHITE, 4, a))
    c.restore()


def hexmol(c, x, y, r, rgb, a, rot):
    pts = [(x + math.cos(rot + k * math.pi / 3) * r, y + math.sin(rot + k * math.pi / 3) * r) for k in range(6)]
    c.drawPath(path_of(pts, True), stroke(rgb, max(2, r * 0.22), a))
    c.drawLine(pts[0][0], pts[0][1], pts[0][0] + math.cos(rot) * r, pts[0][1] + math.sin(rot) * r, stroke(rgb, max(2, r * 0.2), a))


def ignition(c, t):
    a = 255 * (1 - smooth(prog(t, T_A2 - 0.35, T_A2)))
    if a <= 1:
        return
    fire = prog(t, T_FIRE, T_FIRE + 0.45)
    brain(c, *BRAIN, appear(t, 1.2) * 1.05, VIOLET, a, glow=(1 - fire) if t > T_FIRE else 0)
    c.drawLine(BRAIN[0], BRAIN[1] + 90, KID[0], KID[1] - 150, stroke((90, 60, 140), 6, a))       # the nerve
    if T_FIRE <= t:
        for j in range(3):                                # signal pulses race down the nerve
            u = prog(t, T_FIRE + 0.18 * j, T_FIRE + 0.18 * j + 0.4)
            if 0 < u < 1:
                y = lerp(BRAIN[1] + 90, KID[1] - 150, in_cubic(u))
                zap(c, [(BRAIN[0], max(BRAIN[1] + 90, y - 120)), (BRAIN[0] + 6, y - 60), (BRAIN[0], y)], t, GOLD, a, j)
                light(c, BRAIN[0], y, 140, GOLD, 220 * a / 255)
    glow = smooth(prog(t, T_FIRE + 0.4, T_FIRE + 0.6)) * (1 - 0.5 * smooth(prog(t, T_ADR + 1.0, T_ADR + 2)))
    kidney(c, *KID, appear(t, 1.3) * 1.2, GOLD, a, glow)
    if t > T_ADR - 0.1:                                   # adrenaline floods out
        for i in range(46):
            t0 = T_ADR - 0.1 + 0.03 * i
            u = prog(t, t0, t0 + 2.2)
            if u <= 0:
                continue
            ang = hsh(i, 1) * 2 * math.pi
            r = 60 + 620 * out_cubic(u) * (0.4 + 0.6 * hsh(i, 2))
            x = KID[0] + (1 if i % 2 else -1) * 70 + math.cos(ang) * r
            y = KID[1] - 90 + math.sin(ang) * r * 0.75 - 90 * u
            hexmol(c, x, y, 22 + 14 * hsh(i, 3), GOLD, a * (1 - 0.5 * u), t * 2 + i)
        v = appear(t, T_ADR + 0.2)
        if v > 0:
            c.save()
            c.translate(540, 650)
            c.scale(v, v)
            chip(c, 0, 0, "ADRENALINE", "SURGE", GOLD, a, size=64)
            c.restore()


def vessel(c, t):
    a = 255 * smooth(prog(t, T_A2 - 0.3, T_A2 + 0.1)) * (1 - smooth(prog(t, T_A3 - 0.35, T_A3)))
    if a <= 1:
        return
    r = lerp(70, 150, out_back(prog(t, T_OPEN, T_OPEN + 0.6), 1.4))
    y = 650
    speed = lerp(260, 900, smooth(prog(t, T_OPEN, T_OPEN + 0.8)))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, y - 260, W, y + 260))
    c.drawRect(skia.Rect.MakeLTRB(0, y - r, W, y + r), fillp((60, 6, 20), a))
    for k in range(-1, 2, 2):
        c.drawLine(0, y + k * r, W, y + k * r, stroke(RED, 14, a))
        c.drawLine(0, y + k * r, W, y + k * r, stroke(RED, 40, 0.2 * a, plus=True))
        for i in range(12):                                # muscle rings in the vessel wall relax
            x = (i * 100 + 30) % W
            c.drawLine(x, y + k * r, x + 30, y + k * (r + 18), stroke(mix(RED, WHITE, 0.3), 5, 0.7 * a))
    for i in range(26):                                    # red blood cells
        x = (hsh(i, 4) * W + t * speed * (0.8 + 0.4 * hsh(i, 5))) % (W + 200) - 100
        yy = y + (hsh(i, 6) - 0.5) * 1.5 * (r - 30)
        c.save()
        c.translate(x, yy)
        c.rotate(t * 90 + i * 40)
        c.drawOval(skia.Rect.MakeLTRB(-30, -18, 30, 18), fillp(RED, a))
        c.drawOval(skia.Rect.MakeLTRB(-14, -8, 14, 8), fillp((150, 10, 30), a))
        c.restore()
    c.restore()
    v = appear(t, T_OPEN + 0.1)
    if v > 0:
        for k in (-1, 1):                                  # arrows pushing the walls apart
            c.save()
            c.translate(540, y + k * (r + 45))
            c.scale(v, v * k)
            c.drawPath(path_of([(-30, 20), (0, -20), (30, 20)]), stroke(WHITE, 10, a))
            c.restore()
        outlined(c, "WIDE OPEN", 540, y - r - 85, 64, "bungee", WHITE, a * v, glow_rgb=RED)


def mixer(c, t):
    a = 255 * smooth(prog(t, T_A3 - 0.2, T_A3 + 0.2))
    if a <= 1:
        return
    c.drawRRect(rrect(70, 400, 940, 480, 36), fillp((14, 8, 30), a))
    c.drawRRect(rrect(70, 400, 940, 480, 36), stroke((120, 80, 200), 4, a))
    label(c, "BLOOD FLOW MIX", 540, 450, 34, "mono_bold", (200, 180, 255), a, "center", tracking=0.12)
    k = in_out(prog(t, T_GO, T_80))
    for i, (name, rest, hard, rgb) in enumerate(CH):
        x = 170 + i * 185
        v = lerp(rest, hard, k) * smooth(prog(t, T_A3 + 0.05 * i, T_A3 + 0.5 + 0.05 * i))
        big = name == "MUSCLE" and t > T_20 - 0.05
        fader(c, x, 520, 790, v, rgb, name, a, f"{int(round(v * 100))}%" if big else None)
        if big:
            light(c, x, lerp(790, 520, v), 160, MAG, 120 * a / 255)


def scene(c, t):
    ignition(c, t)
    vessel(c, t)
    mixer(c, t)


def draw_frame(c, t):
    G.frame(c, t, scene)


OVERLAY, POST = G.overlay, G.post


def sfx_events():
    return G.sfx() + [(T_FIRE, "shimmer", 0.45), (T_ADR, "reverse_swell", 0.4), (T_OPEN, "whoosh", 0.5),
                      (T_A3 - 0.1, "swish", 0.35), (T_GO, "riser", 0.35)]


MUSIC = G.music()

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
