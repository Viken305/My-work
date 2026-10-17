"""Part 1: hook (dozens of eruptions right now) + inside the Earth (hot core, solid but flowing mantle).

  python3 render.py part1 [--still 3,12,20]
"""
import math

import numpy as np

from common import *  # noqa: F401,F403

PART = "part1"
VO = {"A1": 0.6, "A2": 5.4, "A3": 10.8, "A4": 14.0, "A5": 17.8, "A6": 22.3, "A7": 31.0, "A8": 36.3}
DURATION = 43.0
TM = Timing(PART, VO)

ERUPT = (TM.word("A1", "dozens") - 0.2, TM.word("A1", "erupting") + 0.6)
CARD_T = [TM.word("A2", "islands") - 0.2, TM.word("A2", "ash") - 0.2, TM.word("A2", "history") - 0.2]
CARDS_OUT = 10.5
BIRD_T = TM.word("A3", "explode") - 0.3
DIVE = (VO["A4"] + 0.2, TM.word("A4", "way down") + 0.5)
SHIFT = (17.4, 18.3)
CORE_T = TM.word("A5", "core")
SUN_T = TM.word("A5", "sun") - 0.3
LEFT_T = TM.word("A6", "left over") - 0.2
RADIO_T = TM.word("A6", "radioactive") - 0.2
TO_MANTLE = (30.2, 31.2)
SOLID_T = TM.word("A7", "solid")
FLOW_T = TM.word("A8", "flows")
NAIL_T = TM.word("A8", "fingernails") - 0.3

_rng = np.random.default_rng(14)
VOLC = [(float(lo), float(la), 1.0) for (lo, la) in (zip(_rng.uniform(-180, 180, 40), _rng.uniform(-55, 60, 40)))]


def earth_xy(t):
    s = in_out(prog(t, *SHIFT))
    cx = lerp(960, 640, s)
    d = in_out(prog(t, *DIVE))
    return cx, 540, lerp(300, 380, d)


# ---------------------------------------------------------------- card art
def art_island(c, t):
    c.drawRect(skia.Rect.MakeXYWH(-260, 40, 520, 300), shaded(linear((0, 40), (0, 300), [CYAN, OCEAN])))
    for k in range(3):
        y = 60 + k * 40
        c.drawLine(-260, y, 260, y + 6 * math.sin(t * 2 + k), stroke(WHITE, 3, 60))
    volcano(c, 0, 70, 260, 150, (110, 150, 100), hot=0.6, t=t)
    c.drawPath(poly([(-150, 70), (150, 70), (120, 90), (-120, 90)]), fill((240, 220, 160)))
    Plume(5, 14).draw(c, 0, -80, t, 160, 50, 1.0, 0.2)


def art_ash(c, t):
    volcano(c, 0, 160, 300, 160, ROCK, hot=1.0, t=t)
    Plume(7, 26).draw(c, 0, 0, t, 260, 80, 1.0, 0.22)


def art_trilobite(c, t):
    c.drawRRect(rrect(-170, -150, 340, 300, 30), fill((150, 130, 120)))
    c.save()
    c.rotate(bob(t, 3, 4))
    c.drawOval(skia.Rect.MakeXYWH(-80, -120, 160, 230), fill((110, 92, 84)))
    c.drawPath(poly([(-80, -60), (0, -130), (80, -60)]), fill((110, 92, 84)))
    c.drawOval(skia.Rect.MakeXYWH(-80, -125, 160, 80), fill((95, 78, 72)))
    for k in range(7):
        y = -30 + k * 18
        c.drawLine(-70 + k * 3, y, 70 - k * 3, y, stroke((80, 64, 60), 5))
    c.drawLine(0, -40, 0, 100, stroke((80, 64, 60), 4))
    c.drawCircle(-30, -90, 7, fill((60, 48, 46)))
    c.drawCircle(30, -90, 7, fill((60, 48, 46)))
    c.restore()


CARDS = [(art_island, "BUILT ISLANDS", CYAN), (art_ash, "FILLED THE SKY", ASH), (art_trilobite, "SHAPED LIFE", ORANGE)]


# ---------------------------------------------------------------- scenes
def draw_space(c, t, stars=Stars()):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(12, 12, 38), (26, 20, 66)])))
    stars.draw(c, t, 1.0)
    cx, cy, R = earth_xy(t)
    rot = -t * 8 + 30
    wedge = in_out(prog(t, DIVE[0] + 0.3, DIVE[1]))
    earth_cutaway(c, cx, cy, R, t, wedge, rot)
    if wedge < 0.2:  # glowing eruptions on the visible side
        for n, (lo, la, _) in enumerate(VOLC):
            g = pop(t, lerp(ERUPT[0], ERUPT[1], n / len(VOLC)), 0.4) * (1 - wedge * 5)
            x, y, z = globe_point(cx, cy, R, lo, la, rot)
            if g > 0 and z > 0.15:
                s = g * (0.5 + 0.5 * z)
                glow(c, x, y, 34 * s, LAVA, 230)
                c.drawCircle(x, y, 8 * s, fill(LAVA_HOT))
                for k in range(2):
                    ph = (t * 0.6 + k * 0.5 + n * 0.13) % 1
                    c.drawCircle(x + 4 * k, y - 10 * s - 26 * ph * s, (4 + 6 * ph) * s, fill(ASH, 200 * (1 - ph)))
    caption(c, "DOZENS ERUPTING RIGHT NOW", 960, 980, LAVA_HOT, 30,
            255 * smooth(prog(t, ERUPT[0] + 0.6, ERUPT[0] + 1.0)) * (1 - smooth(prog(t, CARD_T[0] - 0.4, CARD_T[0]))))
    # layer labels + core temperature
    if wedge > 0.5:
        for n, (frac, rgb, label) in enumerate(LAYERS):
            g = pop(t, DIVE[1] - 0.4 + n * 0.25, 0.4) * (1 - smooth(prog(t, TO_MANTLE[0], TO_MANTLE[0] + 0.3)))
            r = R * (frac if n == 0 else (frac + (LAYERS[n + 1][0] if n + 1 < len(LAYERS) else 0)) / 2)
            ang = math.radians(-90 + 90 * (0.25 + n * 0.17))
            px, py = cx + r * math.cos(ang) * (1.0 if n else 1.0), cy + r * math.sin(ang)
            if g > 0:
                lx = cx + R + 90
                ly = cy - R * 0.75 + n * 70
                c.drawLine(px, py, lx - 10, ly - 8, stroke(WHITE, 2, 160 * min(1, g)))
                c.drawCircle(px, py, 6, fill(WHITE, 230 * min(1, g)))
                text(c, label, lx, ly, 28, rgb if n else lighten(rgb, 0.4), 255 * min(1, g), 800, "left", spacing=3)
        k = pop(t, CORE_T + 0.2, 0.5) * (1 - smooth(prog(t, TO_MANTLE[0], TO_MANTLE[0] + 0.3)))
        pill_tag(c, cx, cy - 60, "5,000+ °C", LAVA_HOT, k, 28)
    # the Sun, for comparison
    g = pop(t, SUN_T, 0.6) * (1 - smooth(prog(t, LEFT_T - 0.5, LEFT_T)))
    if g > 0:
        sx, sy = 1480, 520
        c.save()
        c.translate(sx, sy)
        c.scale(g, g)
        glow(c, 0, 0, 300, YELLOW, 170)
        for k in range(12):
            a = k / 12 * 6.28 + t * 0.2
            c.drawLine(140 * math.cos(a), 140 * math.sin(a), 190 * math.cos(a), 190 * math.sin(a), stroke(YELLOW, 14))
        c.drawCircle(0, 0, 120, shaded(radial((-30, -30), 150, [(255, 250, 210), YELLOW, ORANGE], [0, 0.6, 1])))
        eyes(c, 0, 10, 110, t, (-1, 0))
        c.restore()
        text(c, "SUN'S SURFACE  ~5,500 °C", sx, sy + 290, 30, YELLOW, 255 * min(1, g), 800, spacing=2)
        text(c, "≈", (cx + R + sx - 200) / 2 + 40, sy + 30, 90, WHITE, 230 * min(1, g), 800)
    # where the heat comes from
    for n, (tt, label, fn) in enumerate([(LEFT_T, "LEFTOVER HEAT", inset_formation), (RADIO_T, "RADIOACTIVE DECAY", inset_decay)]):
        g = pop(t, tt, 0.55) * (1 - smooth(prog(t, TO_MANTLE[0], TO_MANTLE[0] + 0.3)))
        if g > 0:
            ix, iy = 1650, 290 + n * 440
            c.save()
            c.translate(ix, iy)
            c.scale(g, g)
            c.drawCircle(8, 14, 170, blur(fill((5, 4, 20), 120), 20))
            c.save()
            c.clipPath(circle_path(0, 0, 160), doAntiAlias=True)
            c.drawPaint(fill((16, 14, 44)))
            fn(c, t)
            c.restore()
            c.drawCircle(0, 0, 160, stroke(WHITE, 6, 230))
            c.restore()
            caption(c, label, ix, iy + 215, LAVA_HOT, 26, 255 * min(1, g))
    if wedge > 0.5:  # heat pulsing outward from the core
        for k in range(3):
            ph = (t * 0.4 + k / 3) % 1
            r = R * 0.2 + R * 0.75 * ph
            p = skia.Path()
            p.addArc(skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r), -90, 90 * wedge)
            c.drawPath(p, stroke(LAVA_HOT, 4, 120 * (1 - ph) * smooth(prog(t, CORE_T, CORE_T + 0.5))))


def inset_formation(c, t):
    glow(c, 0, 0, 160, LAVA, 160)
    c.drawCircle(0, 0, 70, shaded(radial((-20, -20), 90, [LAVA_HOT, LAVA, (180, 50, 30)])))
    for k in range(6):
        ph = (t * 0.8 + k / 6) % 1
        a = k / 6 * 6.28 + 0.5
        d = lerp(170, 70, ph)
        x, y = d * math.cos(a), d * math.sin(a)
        c.drawCircle(x, y, 12, fill((140, 120, 160)))
        if ph > 0.9:
            sparkle(c, x, y, 26 * (1 - (ph - 0.9) * 10), 255, YELLOW)


def inset_decay(c, t):
    for k in range(10):
        a = k * 2.39
        c.drawCircle(18 * math.cos(a) * (k % 3) * 0.6, 18 * math.sin(a) * (k % 3) * 0.6, 22, fill(LAVA if k % 2 else (150, 110, 255)))
    for k in range(5):
        ph = (t * 0.7 + k / 5) % 1
        a = k / 5 * 6.28 + 0.3
        d = 40 + 120 * ph
        glow(c, d * math.cos(a), d * math.sin(a), 22, YELLOW, 220 * (1 - ph))
        c.drawCircle(d * math.cos(a), d * math.sin(a), 6, fill(WHITE, 255 * (1 - ph)))


# ---------------------------------------------------------------- the mantle: solid, slowly flowing
_PIC = {}


def mantle_texture():
    if "m" not in _PIC:
        rng = np.random.default_rng(3)
        rec = skia.PictureRecorder()
        c = rec.beginRecording(skia.Rect.MakeXYWH(-400, -200, W + 800, H + 400))
        s = 90
        pts = {(i, j): (i * s + rng.uniform(-30, 30), j * s + rng.uniform(-30, 30)) for i in range(-5, 28) for j in range(-3, 16)}
        for i in range(-5, 27):
            for j in range(-3, 15):
                q = [pts[(i, j)], pts[(i + 1, j)], pts[(i + 1, j + 1)], pts[(i, j + 1)]]
                shade = rng.uniform(0, 1)
                c.drawPath(poly(q), fill(mix((120, 34, 40), (200, 70, 50), shade)))
                c.drawPath(poly(q), stroke((90, 24, 34), 3, 200))
        rec_pic = rec.finishRecordingAsPicture()
        _PIC["m"] = rec_pic
    return _PIC["m"]


def draw_mantle(c, t):
    c.drawPaint(fill((110, 30, 40)))
    drift = max(0.0, t - FLOW_T) * 6
    c.save()
    c.translate(-drift, drift * 0.3)
    c.drawPicture(mantle_texture())
    c.restore()
    glow(c, W / 2, H, 900, LAVA, 60)
    caption(c, "SOLID ROCK", 960, 140, WHITE, 34, 255 * smooth(prog(t, SOLID_T, SOLID_T + 0.3)) * (1 - smooth(prog(t, FLOW_T, FLOW_T + 0.3))))
    # convection cells
    fa = smooth(prog(t, FLOW_T - 0.2, FLOW_T + 0.6))
    if fa > 0:
        for (cx, sgn) in ((560, 1), (1360, -1)):
            for k in range(3):
                a0 = t * 0.25 * sgn + k * 2.09
                p = skia.Path()
                p.addArc(skia.Rect.MakeXYWH(cx - 330, 540 - 240, 660, 480), math.degrees(a0), 80 * sgn)
                c.drawPath(p, stroke(LAVA_HOT, 16, 200 * fa))
                ae = a0 + math.radians(80 * sgn)
                ex, ey = cx + 330 * math.cos(ae), 540 + 240 * math.sin(ae)
                tx, ty = -math.sin(ae) * sgn, math.cos(ae) * sgn * (240 / 330)
                d = math.hypot(tx, ty)
                tx, ty = tx / d, ty / d
                c.drawPath(poly([(ex + tx * 34, ey + ty * 34), (ex - ty * 24, ey + tx * 24), (ex + ty * 24, ey - tx * 24)]), fill(LAVA_HOT, 220 * fa))
    # the bird knocks on it
    b = pop(t, SOLID_T - 0.6, 0.5)
    if b > 0:
        knock = max(0.0, math.sin((t - SOLID_T) * 14)) * (SOLID_T < t < SOLID_T + 1.2)
        c.save()
        c.translate(300, 1000)
        c.scale(b, b)
        bird(c, 0, 0, 74, t, look=(1, 0), tilt=12 * knock)
        c.restore()
        if knock > 0.6:
            for k in range(3):
                a = -0.6 + k * 0.6
                c.drawLine(410 + 30 * math.cos(a), 880 + 30 * math.sin(a), 410 + 60 * math.cos(a), 880 + 60 * math.sin(a), stroke(WHITE, 6))
    g = pop(t, NAIL_T, 0.5)
    if g > 0:
        c.save()
        c.translate(1560, 760)
        c.scale(g, g)
        c.drawRRect(rrect(-190, -170, 380, 300, 40), fill((16, 14, 44), 230))
        c.drawRRect(rrect(-60, -100, 120, 260, 60), fill((240, 190, 160)))
        c.drawRRect(rrect(-42, -86, 84, 100, 34), fill((255, 220, 210)))
        c.drawRRect(rrect(-42, -86, 84, 20, 10), fill(WHITE))
        for k in range(5):
            c.drawLine(110, -80 + k * 30, 140 if k % 2 else 125, -80 + k * 30, stroke(WHITE, 4))
        c.restore()
        caption(c, "A FEW CENTIMETRES A YEAR", 1560, 980, WHITE, 28, 255 * min(1, g))


# ---------------------------------------------------------------- compose
def draw_frame(c, t):
    c.clear(col(NAVY))

    def space(c_, t_):
        if t_ >= TO_MANTLE[0]:
            cx, cy, R = earth_xy(t_)
            z = lerp(1.0, 6.0, in_cubic(prog(t_, *TO_MANTLE)))
            cam(c_, z, cx + R * 0.5, cy - R * 0.62)
            draw_space(c_, t_)
            c_.restore()
        else:
            draw_space(c_, t_)
        # cards over the dimmed globe
        for i, (fn, label, tint) in enumerate(CARDS):
            p = out_back(prog(t_, CARD_T[i], CARD_T[i] + 0.55), 1.2)
            q = in_cubic(prog(t_, CARDS_OUT, CARDS_OUT + 0.5))
            if p > 0 and q < 1:
                cy = lerp(H + 400, 520, p) + q * 900 + bob(t_, 5, 3.4, i * 0.3)
                card(c_, 460 + i * 500, cy, 440, 540, tint, label, None, fn, t_)
        b = pop(t_, BIRD_T, 0.5) * (1 - smooth(prog(t_, DIVE[0], DIVE[0] + 0.4)))
        if b > 0:
            c_.save()
            c_.translate(1600, 1010)
            c_.scale(b, b)
            bird(c_, 0, 0, 80, t_, look=(-1, -0.5))
            c_.restore()
            bubble_q(c_, 1460, 780, pop(t_, BIRD_T + 0.3, 0.4) * (1 - smooth(prog(t_, DIVE[0], DIVE[0] + 0.3))))

    scenes(c, t, [((0.0, 0.01), TO_MANTLE[1] + 0.1, space), ((TO_MANTLE[1] - 0.3, TO_MANTLE[1] + 0.1), DURATION + 1, draw_mantle)])
    vignette(c)
    chapter_fade(c, t, DURATION)


def sfx_events():
    ev = [(0.4, "swell_soft", 0.6)]
    ev += [(lerp(ERUPT[0], ERUPT[1], n / 12), "pop", 0.25) for n in range(12)]
    ev += [(ERUPT[0] + 0.6, "rumble", 0.5)]
    ev += [(tc, "whoosh_soft", 0.6) for tc in CARD_T] + [(tc + 0.4, "chime", 0.4) for tc in CARD_T]
    ev += [(CARDS_OUT, "whoosh", 0.5), (BIRD_T, "pop", 0.6), (BIRD_T + 0.3, "pop", 0.5),
           (DIVE[0], "riser", 0.8), (DIVE[0] + 0.6, "whoosh_long", 0.7), (DIVE[1], "boom", 0.6)]
    ev += [(DIVE[1] - 0.4 + n * 0.25, "blip", 0.4) for n in range(4)]
    ev += [(CORE_T + 0.2, "pop", 0.5), (SUN_T, "swell_soft", 0.7), (LEFT_T, "pop", 0.6), (RADIO_T, "pop", 0.6), (RADIO_T + 0.4, "shimmer", 0.5),
           (TO_MANTLE[0], "whoosh_long", 0.8), (TO_MANTLE[0] + 0.5, "rumble", 0.6),
           (SOLID_T, "click", 1.0), (SOLID_T + 0.22, "click", 1.0), (SOLID_T + 0.45, "click", 1.0),
           (FLOW_T, "rumble", 0.5), (NAIL_T, "pop", 0.6)]
    return ev


MUSIC = dict(
    chords=[(0.0, 50, (0, 7, 12, 15, 19)), (5.2, 46, (0, 7, 12, 16, 19)), (10.6, 48, (0, 7, 12, 14, 19)),
            (13.8, 45, (0, 7, 12, 15, 19)), (22.0, 41, (0, 7, 12, 16, 19)), (30.2, 43, (0, 7, 12, 15, 19)),
            (36.0, 46, (0, 7, 11, 16, 19))],
    plucks=[(5.4, 13.6), (17.8, 30.0), (36.3, DURATION)], bpm=96, rises=[(DIVE[0], DIVE[1])],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
