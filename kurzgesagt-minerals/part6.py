"""Part 6: Deep time (the 4.4-billion-year-old zircon) + outro.

  python3 render.py part6 [--still 5,12,20]
"""
import math

from common import *  # noqa: F401,F403

PART = "part6"
VO = {"D1": 0.8, "D2": 5.0, "D3": 10.9, "O1": 19.4, "O2": 25.9, "O3": 30.5}
DURATION = 38.0
TM = Timing(PART, VO)

GROW = (1.2, 5.5)
AUS_T = TM.word("D2", "australia")
AGE_T = TM.word("D2", "four point four")
LINE = (10.6, 11.8)
GAP_T = TM.word("D3", "hundred and fifty")
LIFE_T = TM.word("D3", "before life") + 0.25
ALL_T = TM.word("D3", "everything")
RECAP = (18.6, 19.2)
BADGE_T = [TM.word("O1", w) - 0.1 for w in ("fire", "water", "pressure", "and life")]
MERGE = (TM.word("O1", "slowly") - 0.1, TM.word("O1", "arranging") + 0.4)
BEAUTY_T = TM.word("O1", "beautiful")
NIGHT = (25.3, 26.0)
LOOK_T = TM.word("O3", "look")
END_CARD = 34.0
ZIRCON_RGB = (235, 140, 125)


# ---------------------------------------------------------------- zircon + timeline
def zircon(c, x, y, s, t):
    glow(c, x, y, 340 * s, PINK, 110)
    glow(c, x, y, 160 * s, (255, 200, 180), 120)
    c.save()
    c.translate(x, y)
    c.rotate(bob(t, 4, 5))
    c.scale(s, s)
    prism(c, -70, 190, 400, 78, -72, ZIRCON_RGB, tip=0.9, both=True)
    c.restore()


def draw_deep(c, t):
    c.drawPaint(shaded(radial((W / 2, 420), W * 0.6, [(30, 24, 60), (8, 6, 20)])))
    Stars(160, 17).draw(c, t, 0.6)
    g = in_out(prog(t, *GROW))
    up = in_out(prog(t, LINE[0] - 0.4, LINE[1]))
    s = lerp(0.06, 1.0, g) * lerp(1.0, 0.55, up) * pop(t, 0.6, 0.5)
    zx, zy = W / 2, lerp(470, 330, up)
    if s > 0:
        zircon(c, zx, zy - 40 * s, s, t)
        tw = prog(t, AGE_T + 0.3, AGE_T + 1.2)
        if 0 < tw < 1:
            sparkle(c, zx + 120 * s, zy - 110 * s, 40 * math.sin(math.pi * tw), rot=tw * 90)
    fade_txt = 1 - smooth(prog(t, LINE[0] - 0.4, LINE[0]))
    caption(c, "JACK HILLS, AUSTRALIA", W / 2, 850, ICE, 30, 255 * smooth(prog(t, AUS_T, AUS_T + 0.4)) * fade_txt)
    a = smooth(prog(t, AGE_T, AGE_T + 0.4))
    if a > 0:
        y = lerp(720, 700, up)
        text(c, "4.4 BILLION YEARS", W / 2, y, lerp(70, 54, up), WHITE, 255 * a, 800, spacing=4)
        text(c, "THE OLDEST PIECE OF EARTH EVER FOUND", W / 2, y + 50, 26, PINK, 230 * a * fade_txt, 800, spacing=4)
    draw_timeline(c, t)


def draw_timeline(c, t):
    k = in_out(prog(t, *LINE))
    if k <= 0:
        return
    x0, x1, y = 160, 1760, 900
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(0, 0, x0 + (x1 - x0) * k + 30, H))
    c.drawRRect(rrect(x0, y - 8, x1 - x0, 16, 8), shaded(linear((x0, 0), (x1, 0), [ORANGE, PINK, CYAN, MINT])))
    c.restore()

    def xat(ga):
        return x0 + (4.6 - ga) / 4.6 * (x1 - x0)

    marks = [(4.54, "EARTH FORMS", ORANGE, LINE[0] + 0.2, 1), (4.4, "ZIRCON", PINK, LINE[0] + 0.5, -1),
             (3.7, "EARLIEST LIFE", MINT, LIFE_T, 1), (2.4, "OXYGEN", CYAN, ALL_T - 0.3, -1),
             (0.23, "DINOSAURS", YELLOW, ALL_T, -1)]
    for ga, label, rgb, tt, up in marks:
        g = pop(t, tt, 0.45)
        if g <= 0:
            continue
        x = xat(ga)
        c.drawCircle(x, y, 16 * g, fill(rgb))
        c.drawCircle(x, y, 16 * g, stroke(WHITE, 4))
        la = smooth(prog(t, tt + 0.1, tt + 0.4))
        dy = 0 if up < 0 else 10
        text(c, label, x, y + up * 52 + dy, 22, WHITE, 230 * la, 800, spacing=2)
        text(c, f"{ga} BILLION YRS AGO" if ga >= 1 else f"{int(ga * 1000)} MILLION YRS AGO", x, y + up * 80 + dy, 16, rgb, 220 * la, 800)
    g = smooth(prog(t, GAP_T, GAP_T + 0.5))
    if g > 0:  # bracket: zircon formed ~150 million years after Earth
        xa, xb = xat(4.54), xat(4.4)
        c.drawPath(poly([(xa, y - 120), (xa, y - 132), (xb, y - 132), (xb, y - 120)], False), stroke(WHITE, 3, 220 * g))
        text(c, "~150 MILLION YEARS", (xa + xb) / 2 + 120, y - 146, 20, WHITE, 230 * g, 800, spacing=2)
    yg = pop(t, ALL_T + 0.4, 0.4)
    if yg > 0:
        c.drawCircle(x1, y, 7 * yg, fill(WHITE))
        text(c, "YOU", x1, y + 52, 22, WHITE, 255 * min(1, yg), 800, spacing=2)
        text(c, "NOW", x1, y + 80, 16, MINT, 220 * min(1, yg), 800)


# ---------------------------------------------------------------- recap: four recipes become one crystal
BADGES = [("FIRE", ORANGE, icon_flame), ("WATER", CYAN, icon_drop), ("PRESSURE", PINK, icon_down), ("LIFE", MINT, icon_sprout)]
BX = [480, 800, 1120, 1440]


def draw_recap(c, t):
    c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.7, [(40, 30, 90), (10, 8, 30)])))
    Dust(60, 12).draw(c, t)
    m = in_out(prog(t, *MERGE))
    for i, (name, rgb, icon) in enumerate(BADGES):
        g = pop(t, BADGE_T[i], 0.5)
        if g <= 0:
            continue
        x, y = lerp(BX[i], W / 2, m), lerp(540 + bob(t, 6, 3, i * 0.25), 540, m)
        s = g * lerp(1.0, 0.3, m)
        a = 255 * (1 - smooth(prog(m, 0.75, 1.0)))
        if a <= 1:
            continue
        c.saveLayerAlpha(None, int(a))
        glow(c, x, y, 160 * s, rgb, 120)
        c.drawCircle(x, y, 80 * s, fill(rgb))
        c.drawCircle(x, y, 80 * s, stroke(WHITE, 6 * s, 220))
        c.save()
        c.translate(x, y)
        c.scale(2.4 * s, 2.4 * s)
        icon(c, 0, 0, 22)
        c.restore()
        text(c, name, x, y + 140 * s, 34 * s, WHITE, 255 * (1 - m), 800, spacing=4)
        c.restore()
    f = math.sin(math.pi * prog(t, MERGE[1] - 0.15, MERGE[1] + 0.35))
    g = out_back(prog(t, MERGE[1] - 0.1, MERGE[1] + 0.6))
    if g > 0:
        for k, rgb in enumerate([ORANGE, CYAN, PINK, MINT]):
            a = t * 0.8 + k * math.pi / 2
            glow(c, W / 2 + 90 * math.cos(a), 540 + 60 * math.sin(a), 260 * g, rgb, 90)
        c.save()
        c.translate(W / 2, 540 + bob(t, 6, 3))
        c.rotate(-90 + 4 * math.sin(t * 0.8))
        c.scale(g, g)
        prism(c, -200, 0, 400, 78, 0, ICE, tip=0.8, both=True, glow_a=60)
        c.restore()
        b = prog(t, BEAUTY_T, BEAUTY_T + 1.2)
        if 0 < b < 1:
            for k in range(6):
                a = k / 6 * 6.28 + 0.3
                sparkle(c, W / 2 + math.cos(a) * 260 * out_cubic(b), 540 + math.sin(a) * 200 * out_cubic(b), 30 * math.sin(math.pi * b), rot=b * 120)
    if f > 0:
        c.drawPaint(fill(WHITE, 170 * f))


# ---------------------------------------------------------------- night outro with the geode
def draw_night(c, t):
    z = lerp(1.0, 1.12, smooth(prog(t, NIGHT[0], DURATION)))
    cam(c, z, 1000, 700)
    c.drawPaint(shaded(linear((0, -200), (0, H), [(10, 10, 34), (50, 32, 100)])))
    c.save()
    c.rotate(-18, W / 2, H / 2)
    c.drawOval(skia.Rect.MakeXYWH(-200, 220, W + 400, 260), blur(fill((150, 120, 230), 50), 60))
    c.restore()
    Stars(320, 23).draw(c, t, 1.0)
    for k in range(3):  # shooting star
        ph = prog(t, 27.5 + k * 3.7, 28.3 + k * 3.7)
        if 0 < ph < 1:
            sx, sy = 300 + k * 500 + 500 * ph, 120 + k * 40 + 160 * ph
            c.drawLine(sx, sy, sx - 140, sy - 45, stroke(WHITE, 3, 220 * math.sin(math.pi * ph)))
    for (y, cc, seed) in [(700, (34, 24, 70), 41), (800, (24, 18, 52), 42), (900, (16, 12, 38), 43)]:
        wavy_band(c, y, 1080, cc, seed, 40)
    rock = blob_path(1240, 880, [200, 160, 150, 170, 190, 200, 180, 170], 0.0)
    m = skia.Matrix()
    m.setScale(1.0, 0.55, 1240, 880)
    rock.transform(m)
    c.drawPath(rock, fill((60, 48, 96)))
    gx, gy, gr = 860, 890, 150
    pulse = 1 + 0.08 * math.sin(t * 1.6)
    glow(c, gx, gy - 30, 380 * pulse, (190, 120, 255), 120)
    c.drawOval(skia.Rect.MakeXYWH(gx - gr, gy - gr * 0.7, gr * 2, gr * 1.4), fill((120, 100, 120)))
    inner = skia.Path()
    inner.addOval(skia.Rect.MakeXYWH(gx - gr * 0.82, gy - gr * 0.56, gr * 1.64, gr * 1.12))
    c.save()
    c.clipPath(inner, doAntiAlias=True)
    c.drawPaint(shaded(radial((gx, gy), gr, [(80, 30, 140), (150, 80, 230), (200, 160, 255)], [0, 0.6, 1])))
    for k in range(18):
        a = k / 18 * 6.28
        x, y = gx + math.cos(a) * gr * 0.82, gy + math.sin(a) * gr * 0.56
        tx, ty = gx + math.cos(a) * gr * 0.15, gy + math.sin(a) * gr * 0.1
        nx, ny = -math.sin(a) * 16, math.cos(a) * 11
        c.drawPath(poly([(x + nx, y + ny), (tx, ty), (x - nx, y - ny)]), fill(lighten((150, 80, 230), 0.15 + 0.4 * (k % 3) / 2)))
    c.restore()
    for n, (x, y, s) in enumerate([(gx - 40, gy - 30, 24), (gx + 50, gy + 10, 16), (gx - 10, gy + 30, 14)]):
        ph = (t * 0.5 + n * 0.37) % 1
        sparkle(c, x, y, s * math.sin(math.pi * ph), rot=ph * 90)
    turn = smooth(prog(t, LOOK_T, LOOK_T + 0.5))
    bird(c, 1220, 812, 82, t, look=(lerp(-1, 0, turn), lerp(0.4, 0, turn)), tilt=-4 * (1 - turn))
    glow(c, 1130, 700, 120, (190, 120, 255), 50)
    c.restore()
    ea = smooth(prog(t, END_CARD, END_CARD + 0.8))
    if ea > 0:
        text(c, "HOW THE EARTH", W / 2, 190, 64, WHITE, 255 * ea, 800, spacing=8)
        text(c, "MAKES CRYSTALS", W / 2, 268, 64, WHITE, 255 * ea, 800, spacing=8)
        text(c, "SOURCES IN THE DESCRIPTION", W / 2, 330, 22, (200, 170, 255), 220 * ea, 800, spacing=6)


# ---------------------------------------------------------------- compose
def draw_frame(c, t):
    c.clear(col(DARK))
    scenes = [((0.0, 0.01), RECAP[1], draw_deep), (RECAP, NIGHT[1], draw_recap), (NIGHT, DURATION + 1, draw_night)]
    for (t0, t1), t_end, fn in scenes:
        if t0 <= t < t_end:
            a = smooth(prog(t, t0, t1))
            if a < 1:
                c.saveLayerAlpha(None, int(255 * a))
            fn(c, t)
            if a < 1:
                c.restore()
    vignette(c)
    chapter_fade(c, t, DURATION, 0.5, 1.4)


def sfx_events():
    ev = [(0.6, "chime", 0.5), (GROW[0], "riser", 0.4), (AUS_T, "pop", 0.4), (AGE_T, "shine", 0.8),
          (LINE[0], "whoosh_long", 0.6), (LINE[0] + 0.2, "blip", 0.5), (LINE[0] + 0.5, "blip", 0.5), (GAP_T, "pop", 0.4),
          (LIFE_T, "blip", 0.5), (ALL_T - 0.3, "blip", 0.5), (ALL_T, "blip", 0.5), (ALL_T + 0.4, "chime", 0.5),
          (RECAP[0], "whoosh", 0.5)]
    ev += [(tb, "pop", 0.7) for tb in BADGE_T]
    ev += [(MERGE[0], "riser", 0.8), (MERGE[1], "shine", 1.0), (BEAUTY_T, "shimmer", 0.7),
           (NIGHT[0], "whoosh_long", 0.5), (NIGHT[0] + 0.4, "swell_soft", 0.8), (LOOK_T, "chime", 0.4), (END_CARD, "swell_soft", 0.7)]
    return ev


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 15, 19)), (5.0, 41, (0, 7, 12, 16, 19)), (10.6, 43, (0, 7, 12, 14, 19)),
            (18.6, 48, (0, 7, 12, 16, 19)), (22.0, 53, (0, 7, 11, 16, 19)), (25.3, 45, (0, 7, 12, 14, 19)),
            (30.0, 41, (0, 7, 11, 16, 19)), (34.0, 48, (0, 7, 12, 16, 19, 24))],
    plucks=[(18.8, 25.2), (26.0, 34.0)], bpm=96, rises=[(MERGE[0], MERGE[1])],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
