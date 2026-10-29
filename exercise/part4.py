"""LEVEL 3 · FUEL. An ATP battery drains in seconds; sugar cubes and fat drops are burned in a reactor that recharges
it again and again; then oxygen runs short, acid fizzes up in the muscle fibres and they catch fire (the burn).

  python3 render.py part4 [--still 3,6,9,12,15]
"""
from game import *  # noqa: F401,F403

PART = "part4"
G = Game(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
PREMIUM, SAMPLES = True, 4
T_ATP = G.w("C1", "a t p")
T_STORE = G.w("C1", "store")
T_FEW = G.w("C1", "few")
T_C2 = VO["C2"]
T_SUGAR = G.w("C2", "sugar")
T_FAT = G.w("C2", "fat")
T_RECH = G.w("C2", "recharge")
T_NON = G.w("C2", "nonstop")
T_C3 = VO["C3"]
T_OXY = G.w("C3", "oxygen")
T_ACID = G.w("C3", "acid")
T_BURN = G.w("C3", "that's") + 0.3      # the fire starts on "that's part of the burn"
BAT = (540, 640)


def charge(t):
    if t < T_STORE:
        return 1.0
    if t < T_RECH:                                        # drains in "a few seconds", then sits empty
        return 1 - in_cubic(prog(t, T_STORE, T_FEW + 0.5))
    u = (t - T_RECH) * G.bpm / 60 / 2                     # then recharged and spent over and over, on the beat
    return 0.25 + 0.75 * (1 - abs((u % 1) * 2 - 1)) if t > T_NON else lerp(0, 1, out_cubic(prog(t, T_RECH, T_RECH + 0.5)))


def battery(c, t, x, y, s, a):
    if a <= 1:
        return
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    w, h = 560, 220
    q = charge(t)
    rgb = LIME if q > 0.5 else GOLD if q > 0.2 else RED
    light(c, 0, 0, 420, rgb, 70 * a / 255)
    c.drawRRect(rrect(-w / 2, -h / 2, w, h, 36), fillp((10, 14, 8), a))
    c.drawRRect(rrect(w / 2 + 6, -40, 30, 80, 10), fillp(rgb, a))
    segs = 6
    for i in range(segs):
        on = q * segs - i
        if on <= 0:
            continue
        sw = (w - 60) / segs
        c.drawRRect(rrect(-w / 2 + 30 + i * sw + 6, -h / 2 + 26, (sw - 12) * clamp(on), h - 52, 14), fillp(rgb, a))
    c.drawRRect(rrect(-w / 2, -h / 2, w, h, 36), stroke(rgb, 10, a))
    outlined(c, "ATP", 0, 38, 110, "bungee", WHITE, a * 0.92, glow_rgb=rgb)
    if q < 0.05 and t < T_RECH:                           # empty: blinking LOW
        if int(t * 6) % 2 == 0:
            outlined(c, "EMPTY", 0, h / 2 + 90, 64, "bungee", RED, a, glow_rgb=RED)
    c.restore()


def countdown(c, t):
    if not (T_STORE <= t < T_FEW + 0.9):
        return
    k = (t - T_STORE) / max(0.3, (T_FEW + 0.5 - T_STORE))
    n = 3 - int(min(2, k * 3))
    u = (k * 3) % 1
    outlined(c, str(n), 880, 860 + 20 * u, 120 * (1.3 - 0.3 * out_cubic(u)), "bungee", GOLD, 255 * (1 - u * 0.6), glow_rgb=GOLD)
    label(c, "SECONDS", 880, 910, 26, "mono_bold", GOLD, 220, "center", tracking=0.1)


def reactor(c, t, a):
    if a <= 1:
        return
    x, y = 540, 815
    spin = t * 4
    light(c, x, y, 260, ORANGE, (90 + 90 * G.beat(t)) * a / 255)
    c.drawCircle(x, y, 92, fillp((30, 10, 4), a))
    for k in range(3):
        c.drawArc(skia.Rect.MakeLTRB(x - 92 + 14 * k, y - 92 + 14 * k, x + 92 - 14 * k, y + 92 - 14 * k),
                  math.degrees(spin * (1 + k * 0.4)) % 360, 220, False, stroke((ORANGE, GOLD, RED)[k], 8, a))
    c.drawCircle(x, y, 26 + 8 * G.beat(t), fillp(WHITE, a))
    if t > T_RECH:                                         # bolts up into the battery
        zap(c, [(x, y - 80), (x - 20, y - 130), (x + 15, y - 170), (x, BAT[1] + 120)], t, LIME, a * (0.6 + 0.4 * G.beat(t)), 3)
    # fuel flies in: sugar cubes from the left, fat drops from the right
    for i in range(16):
        side = -1 if i % 2 == 0 else 1
        t0 = (T_SUGAR if side < 0 else T_FAT) - 0.3 + (i // 2) * 0.32
        u = prog(t, t0, t0 + 0.7)
        if not 0 < u < 1:
            continue
        sx, sy = x + side * 560, 700 + 60 * hsh(i, 2)
        px = lerp(sx, x, in_cubic(u))
        py = lerp(sy, y, u) - 160 * math.sin(math.pi * u)
        sc = 1 - 0.5 * in_cubic(u)
        c.save()
        c.translate(px, py)
        c.rotate(u * 300 * side)
        c.scale(sc, sc)
        if side < 0:
            c.drawRRect(rrect(-30, -30, 60, 60, 8), fillp((235, 245, 255), a))
            c.drawRRect(rrect(-30, -30, 60, 60, 8), stroke(CYN, 4, a))
        else:
            p = skia.Path()
            p.moveTo(0, -38)
            p.cubicTo(30, -6, 30, 30, 0, 30)
            p.cubicTo(-30, 30, -30, -6, 0, -38)
            c.drawPath(p, fillp(GOLD, a))
            c.drawPath(p, stroke(WHITE, 3, a))
        c.restore()
    for k, (txt, xx, t0, rgb) in enumerate((("SUGAR", 150, T_SUGAR, CYN), ("FAT", 930, T_FAT, GOLD))):
        v = appear(t, t0 - 0.1)
        if v > 0:
            c.save()
            c.translate(xx, 640)
            c.scale(v, v)
            outlined(c, txt, 0, 0, 56, "bungee", rgb, a, glow_rgb=rgb)
            c.restore()
    if t > T_NON - 0.1:                                   # the loop arrows of NONSTOP
        v = appear(t, T_NON - 0.1)
        for k in range(2):
            ang = math.degrees(t * 3) + k * 180
            c.drawArc(skia.Rect.MakeLTRB(x - 150, y - 150, x + 150, y + 150), ang % 360, 120, False, stroke(LIME, 10 * v, a))


def burn(c, t):
    a = 255 * smooth(prog(t, T_C3 - 0.25, T_C3 + 0.25))
    if a <= 1:
        return
    lack = smooth(prog(t, T_OXY + 0.2, T_OXY + 1.2))
    acid = smooth(prog(t, T_ACID, T_ACID + 1.6))
    fire = smooth(prog(t, T_BURN - 0.4, T_BURN + 0.3))
    # oxygen supply bar
    label(c, "O2 SUPPLY", 110, 412, 30, "mono_bold", CYN, a, "left", tracking=0.1)
    c.drawRRect(rrect(110, 428, 860, 26, 13), fillp((30, 30, 60), a))
    o = 1 - 0.75 * lack + 0.04 * math.sin(t * 30) * lack
    c.drawRRect(rrect(110, 428, 860 * o, 26, 13), fillp(CYN if o > 0.5 else RED, a))
    if lack > 0.5 and int(t * 5) % 2 == 0:
        label(c, "LOW", 970, 412, 30, "bungee", RED, a, "right")
    # muscle fibres
    for i in range(5):
        y = 620 + i * 60
        rgb = mix(mix(RED, (120, 10, 30), 0.3 * (i % 2)), ORANGE, 0.5 * fire)
        c.drawRRect(rrect(110, y - 24, 860, 48, 24), fillp(rgb, a))
        for k in range(18):
            x = 140 + k * 48
            c.drawLine(x, y - 18, x, y + 18, stroke((90, 0, 20), 4, 0.6 * a))
    # acid bubbles
    for i in range(int(60 * acid)):
        u = (t * (0.4 + 0.3 * hsh(i, 3)) + hsh(i, 1)) % 1
        x = 130 + hsh(i, 2) * 820 + 12 * math.sin(t * 6 + i)
        y = 900 - u * 360
        r = 8 + 10 * hsh(i, 4)
        c.drawCircle(x, y, r, stroke(LIME, 3, a * (1 - u)))
        if i % 4 == 0:
            label(c, "H+", x, y - r - 4, 22, "mono_bold", LIME, a * (1 - u), "center")
    if fire > 0:                                           # the fibres catch fire
        for i in range(26):
            x = 120 + i * 33
            hgt = (60 + 60 * hsh(i, 9) + 30 * math.sin(t * 14 + i)) * fire
            base = 596
            p = skia.Path()
            p.moveTo(x - 18, base)
            p.quadTo(x - 14, base - hgt * 0.6, x + 4 * math.sin(t * 9 + i), base - hgt)
            p.quadTo(x + 14, base - hgt * 0.6, x + 18, base)
            p.close()
            c.drawPath(p, fillp(mix(ORANGE, GOLD, hsh(i, 5)), a))
            light(c, x, base - hgt * 0.4, 90, ORANGE, 70 * fire * a / 255)
        v = appear(t, T_BURN - 0.1)
        c.save()
        c.translate(540, 780)
        c.scale(v, v)
        if v > 0:
            outlined(c, "THE BURN", 0, 0, 120, "bungee_shade", ORANGE, a, glow_rgb=RED)
        c.restore()


def scene(c, t):
    k = in_out(prog(t, T_C2 - 0.3, T_C2 + 0.3))
    a1 = 255 * (1 - smooth(prog(t, T_C3 - 0.35, T_C3)))
    battery(c, t, BAT[0], lerp(BAT[1], 530, k), appear(t, 1.1) * lerp(1.0, 0.8, k), a1)
    countdown(c, t)
    reactor(c, t, a1 * smooth(prog(t, T_C2 - 0.2, T_C2 + 0.3)))
    burn(c, t)


def draw_frame(c, t):
    G.frame(c, t, scene)
    if t > T_BURN - 0.4:                                   # the screen goes hot
        k = smooth(prog(t, T_BURN - 0.4, T_BURN + 0.4)) * (0.6 + 0.4 * G.beat(t))
        c.drawPaint(skia.Paint(Color=skia.Color(255, 60, 20, int(40 * k)), BlendMode=skia.BlendMode.kPlus))


OVERLAY = G.overlay


def POST(t):
    k = smooth(prog(t, T_BURN - 0.4, T_BURN + 0.4))
    return dict(grain=3.5, ca=1.2 + 1.5 * k, bloom=1.1 + 0.3 * k)


def sfx_events():
    return G.sfx() + [(T_STORE, "tick_roll", 0.5), (T_FEW + 0.5, "flatline", 0.25), (T_SUGAR, "pop", 0.4), (T_FAT, "pop", 0.4),
                      (T_RECH, "shimmer", 0.5), (T_ACID, "boil", 0.4), (T_BURN - 0.3, "heat_roar", 0.5)]


MUSIC = G.music()

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
