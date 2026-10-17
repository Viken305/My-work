"""Part 5: Recipe 4, LIFE. Microbes release oxygen, rocks rust, thousands of new minerals; life still makes them.

  python3 render.py part5 [--still 5,12,20]
"""
import math

import numpy as np

from common import *  # noqa: F401,F403
from part1 import draw_arm_content

PART = "part5"
VO = {"B1": 0.8, "B2": 4.9, "B3": 11.5, "B4": 19.4, "B5": 25.9}
DURATION = 33.5
TM = Timing(PART, VO)

T_DOCK = 4.0
OCEAN = (4.2, 4.8)
MOUNDS = (4.8, 6.2)
MICROBE_T = TM.word("B2", "microbes") - 0.3
O2_T = TM.word("B2", "releasing")
PAN = (11.2, 13.0)
RUST = (TM.word("B3", "reacted"), TM.word("B3", "everywhere") + 0.6)
BURST = (TM.word("B3", "thousands") - 0.1, TM.word("B3", "existed") + 0.2)
PIE = (18.9, 19.5)
SWEEP = (TM.word("B4", "two thirds") - 0.2, TM.word("B4", "two thirds") + 1.2)
CARDS = (25.4, 25.9)
CARD_T = [TM.word("B5", w) - 0.15 for w in ("shells", "coral", "pearls", "bones")]

_rng = np.random.default_rng(8)
OXY = [dict(x=_rng.uniform(150, 1250), sp=_rng.uniform(40, 80), ph=_rng.uniform(0, 1), r=_rng.uniform(12, 22),
            t0=O2_T + _rng.uniform(0, 1.8), sway=_rng.uniform(0, 6.28)) for _ in range(30)]
MOUND = [(260, 220, 200), (560, 180, 150), (820, 260, 240), (1120, 170, 130)]
ROCK = (1600, 860)
BURST_GEMS = sorted([(float(x), float(y)) for x, y in zip(_rng.uniform(1120, 1900, 44), _rng.uniform(140, 700, 44))],
                    key=lambda p: math.dist(p, ROCK))
GEM_COLS = [PINK, CYAN, YELLOW, MINT, ORANGE, (170, 130, 255), (255, 110, 110)]


# ---------------------------------------------------------------- ancient ocean
def draw_ocean(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(40, 150, 170), (16, 50, 90)])))
    for k in range(6):
        x = 200 + k * 330 + 30 * math.sin(t * 0.4 + k)
        c.drawPath(poly([(x, -10), (x + 120, -10), (x + 340, H), (x + 160, H)]), blur(fill(WHITE, 22), 20))
    wavy_band(c, 900, 1080, (30, 60, 80), 31, 20)
    for n, (sx, sw, sh) in enumerate(MOUND):
        g = out_back(prog(t, MOUNDS[0] + n * 0.2, MOUNDS[0] + n * 0.2 + 0.9))
        if g <= 0:
            continue
        for layer in range(5):
            f = 1 - layer * 0.17
            c.drawOval(skia.Rect.MakeXYWH(sx - sw * f / 2, 960 - sh * f * g, sw * f, sh * f * 2 * g), fill(mix((40, 110, 100), MINT, layer / 5)))
        for m in range(3):
            pm = pop(t, MICROBE_T + n * 0.12 + m * 0.07, 0.4)
            mx, my = sx - sw * 0.25 + m * sw * 0.25, 960 - sh * 0.82 * g - (m % 2) * 10
            puff = 1 + 0.12 * max(0.0, math.sin((t - O2_T) * 5 + m + n)) * (t > O2_T)
            atom(c, mx, my, 15 * pm * puff, MINT, t + m + n, look=(0, -1))
    # oxygen bubbles rising
    for n, o in enumerate(OXY):
        if t < o["t0"]:
            continue
        age = t - o["t0"]
        y = 760 - age * o["sp"] - 40 * o["ph"]
        x = o["x"] + 20 * math.sin(age * 1.3 + o["sway"])
        # after the pan, oxygen drifts toward the rock
        d = smooth(prog(t, RUST[0] - 1.0, RUST[1]))
        x, y = lerp(x, ROCK[0] - 200 + (n % 6) * 70, d * 0.85), lerp(max(y, 150 + (n * 37) % 300), ROCK[1] - 160 + (n % 5) * 30, d * 0.85)
        g = pop(t, o["t0"], 0.35) * (1 - smooth(prog(t, RUST[1] - 0.6, RUST[1] + 0.2)))
        if g > 0.01:
            atom(c, x, y, o["r"] * g, OX, t + n, look=(0, -1))
            c.drawCircle(x, y, (o["r"] + 8) * g, stroke(WHITE, 2, 70))
    # the rock that will rust
    c.drawPath(blob_path(*ROCK, [260, 230, 280, 240, 260, 300, 270, 250], 0.4), fill((90, 76, 110)))
    for n, (x, y, r) in enumerate([(1520, 760, 60), (1680, 820, 80), (1600, 940, 50), (1740, 940, 40), (1470, 880, 45)]):
        g = smooth(prog(t, RUST[0] + n * 0.3, RUST[0] + n * 0.3 + 1.4))
        if g > 0:
            c.drawPath(blob_path(x, y, [r * g, r * 0.8 * g, r * 1.1 * g, r * 0.9 * g, r * g, r * 0.85 * g], 0), fill((200, 80, 60)))
    pill_tag(c, ROCK[0], 560, "RUST", (230, 110, 90), pop(t, RUST[0] + 0.6, 0.4) * (1 - smooth(prog(t, BURST[0], BURST[0] + 0.3))), 26)
    for n, (x, y) in enumerate(BURST_GEMS):
        tn = lerp(BURST[0], BURST[1], n / len(BURST_GEMS))
        g = out_back(prog(t, tn, tn + 0.45))
        if g > 0:
            rgb = GEM_COLS[n % len(GEM_COLS)]
            xx, yy = lerp(ROCK[0], x, g), lerp(ROCK[1] - 100, y, g) + bob(t, 4, 2.6, n * 0.1)
            glow(c, xx, yy, 60 * g, rgb, 90)
            gem_shape(c, xx, yy, 24 * min(g, 1.0), rgb, n % 4)


def ocean_captions(c, t):
    """Screen-space captions (outside the camera move)."""
    if t >= PIE[1]:
        return
    caption(c, "OVER 2 BILLION YEARS AGO", 960, 1030, MINT, 30, 255 * smooth(prog(t, VO["B2"], VO["B2"] + 0.4)) * (1 - smooth(prog(t, PAN[0], PAN[0] + 0.4))))
    caption(c, "OXYGEN + ROCK", 960, 1030, (255, 150, 140), 30, 255 * smooth(prog(t, PAN[0] + 0.3, PAN[0] + 0.7)) * (1 - smooth(prog(t, BURST[0], BURST[0] + 0.4))))
    caption(c, "THOUSANDS OF NEW MINERALS", 960, 1030, WHITE, 32, 255 * smooth(prog(t, BURST[0] + 0.5, BURST[0] + 0.9)) * (1 - smooth(prog(t, PIE[0], PIE[1]))))


# ---------------------------------------------------------------- 2/3 pie
def draw_pie(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [NAVY, (20, 50, 60)])))
    Dust(50, 5, MINT).draw(c, t, 0.8)
    cx, cy, r = 700, 540, 300
    glow(c, cx, cy, r * 1.6, MINT, 70)
    oval = skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r)
    c.drawOval(oval, fill(VIOLET))
    sw = 240 * in_out(prog(t, *SWEEP))
    if sw > 0.5:
        p = skia.Path()
        p.moveTo(cx, cy)
        p.arcTo(oval, -90, sw, False)
        p.close()
        c.drawPath(p, shaded(radial((cx - 80, cy - 80), r * 1.4, [lighten(MINT, 0.25), MINT, darken(MINT, 0.2)])))
    c.drawCircle(cx, cy, r * 0.55, fill(NAVY))
    c.drawCircle(cx, cy, r, stroke(WHITE, 5, 200))
    k = smooth(prog(t, SWEEP[0] + 0.3, SWEEP[1]))
    text(c, "~2/3", cx, cy + 34, 96, WHITE, 255 * k, 800)
    for n in range(10):  # a ring of mineral icons orbiting
        a = n / 10 * 6.28 + t * 0.25
        x, y = cx + math.cos(a) * r * 1.28, cy + math.sin(a) * r * 1.28
        gem_shape(c, x, y, 18 * pop(t, PIE[1] + n * 0.05, 0.4), GEM_COLS[n % len(GEM_COLS)], n % 4)
    ta = smooth(prog(t, SWEEP[1] - 0.2, SWEEP[1] + 0.3))
    text(c, "OF EARTH'S MINERALS", 1440, 480, 46, WHITE, 255 * ta, 800, spacing=3)
    text(c, "MAY ONLY EXIST", 1440, 548, 46, WHITE, 255 * ta, 800, spacing=3)
    text(c, "BECAUSE OF LIFE", 1440, 616, 46, MINT, 255 * ta, 800, spacing=3)
    bird(c, 1440, 900, 58, t, look=(-1, -0.4), a=255 * pop(t, SWEEP[1] + 0.4, 0.5) if t > SWEEP[1] + 0.4 else 0)


# ---------------------------------------------------------------- life still makes them
CW, CH = 380, 520
CARD_X = [300, 740, 1180, 1620]
CARD_INFO = [("SHELLS", "calcite", ORANGE), ("CORAL", "aragonite", PINK), ("PEARLS", "aragonite", ICE), ("BONES", "apatite", MINT)]


def draw_shell(c, t, s):
    c.save()
    c.scale(s, s)
    c.rotate(bob(t, 3, 4))
    fan = skia.Path()
    fan.moveTo(0, 110)
    fan.cubicTo(-200, 40, -160, -150, 0, -150)
    fan.cubicTo(160, -150, 200, 40, 0, 110)
    c.drawPath(fan, shaded(linear((0, -150), (0, 110), [(255, 200, 160), (240, 130, 100)])))
    for k in range(9):
        a = math.radians(-150 + k * 15)
        c.drawLine(0, 100, 150 * math.cos(a), 100 + 230 * math.sin(a) * 0.95, stroke((200, 100, 80), 5, 160))
    c.drawPath(poly([(-50, 110), (50, 110), (30, 140), (-30, 140)]), fill((240, 140, 110)))
    c.restore()


def draw_coral(c, t, s):
    c.save()
    c.scale(s, s)

    def branch(x, y, ang, ln, d):
        if d == 0:
            c.drawCircle(x, y, 9, fill(lighten(PINK, 0.4)))
            return
        sway = 4 * math.sin(t * 1.2 + d + x * 0.01)
        x2 = x + ln * math.cos(math.radians(ang + sway))
        y2 = y + ln * math.sin(math.radians(ang + sway))
        c.drawLine(x, y, x2, y2, stroke(mix(PINK, ORANGE, 0.3 * d / 4), 6 + d * 5))
        branch(x2, y2, ang - 28, ln * 0.72, d - 1)
        branch(x2, y2, ang + 26, ln * 0.7, d - 1)

    branch(0, 160, -90, 110, 4)
    c.restore()


def draw_pearl(c, t, s):
    c.save()
    c.scale(s, s)
    c.save()
    c.translate(0, -30)
    c.rotate(-24 + bob(t, 3, 3))
    c.drawOval(skia.Rect.MakeXYWH(-150, -120, 300, 130), fill((110, 96, 130)))
    c.drawOval(skia.Rect.MakeXYWH(-134, -104, 268, 100), shaded(linear((0, -104), (0, 0), [(240, 230, 250), (200, 190, 230)])))
    c.restore()
    c.drawOval(skia.Rect.MakeXYWH(-160, 20, 320, 140), fill((110, 96, 130)))
    c.drawOval(skia.Rect.MakeXYWH(-140, 34, 280, 104), shaded(linear((0, 34), (0, 138), [(240, 230, 250), (190, 180, 225)])))
    glow(c, 0, 66, 120, WHITE, 120)
    c.drawCircle(0, 66, 44, shaded(radial((-14, 52), 60, [WHITE, (235, 230, 245), (200, 195, 225)], [0, 0.5, 1])))
    c.drawCircle(-14, 52, 10, fill(WHITE, 230))
    c.restore()


def draw_cards(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [NAVY, PURPLE])))
    Dust().draw(c, t)
    for i, (label, sub, rgb) in enumerate(CARD_INFO):
        t0 = CARD_T[i]
        p = out_back(prog(t, t0, t0 + 0.55), 1.2)
        if p <= 0:
            continue
        cx, cy = CARD_X[i], lerp(H + CH, 540 + bob(t, 5, 3.4, i * 0.3), p)
        rr = rrect(cx - CW / 2, cy - CH / 2, CW, CH, 32)
        soft_shadow(c, rr, 14, 24, 26, 120)
        c.drawRRect(rr, shaded(linear((cx, cy - CH / 2), (cx, cy + CH / 2), [mix(NAVY, rgb, 0.14), mix(PURPLE, rgb, 0.05)])))
        c.save()
        c.clipRRect(rr, doAntiAlias=True)
        glow(c, cx, cy - 60, 300, rgb, 50)
        c.save()
        c.translate(cx, cy - 50)
        if i == 0:
            draw_shell(c, t, 0.95)
        elif i == 1:
            draw_coral(c, t, 0.95)
        elif i == 2:
            draw_pearl(c, t, 1.0)
        else:
            draw_arm_content(c, t, 0.66, dict(t_in=t0 - 0.4))
        c.restore()
        c.restore()
        c.drawRRect(rr, stroke(rgb, 3, 90))
        text(c, label, cx, cy + CH / 2 - 74, 38, WHITE, 255, 800, spacing=3)
        text(c, sub, cx, cy + CH / 2 - 36, 24, rgb, 230, 600, spacing=2)


# ---------------------------------------------------------------- compose
def draw_frame(c, t):
    c.clear(col(NAVY))
    if t < OCEAN[1]:
        title_backdrop(c, t, MINT)
    z = lerp(1.0, 1.18, in_out(prog(t, *PAN)))
    fx, fy = lerp(960, 1300, in_out(prog(t, *PAN))), lerp(540, 520, in_out(prog(t, *PAN)))

    def ocean(c_, t_):
        cam(c_, z, fx, fy)
        draw_ocean(c_, t_)
        c_.restore()

    scenes = [(OCEAN, PIE[1], ocean), (PIE, CARDS[1], draw_pie), (CARDS, DURATION + 1, draw_cards)]
    for (t0, t1), t_end, fn in scenes:
        if t0 <= t < t_end:
            a = smooth(prog(t, t0, t1))
            if a < 1:
                c.saveLayerAlpha(None, int(255 * a))
            fn(c, t)
            if a < 1:
                c.restore()
    ocean_captions(c, t)
    title_sequence(c, t, 4, "LIFE", MINT, icon_sprout, 0.3, T_DOCK)
    vignette(c)
    chapter_fade(c, t, DURATION)


def sfx_events():
    ev = [(0.3, "whoosh_soft", 0.6), (0.4, "pop", 0.8), (0.55, "swell_soft", 0.7), (T_DOCK, "whoosh_soft", 0.5),
          (OCEAN[0], "bubble", 0.5), (MOUNDS[0], "slide", 0.4), (MICROBE_T, "pop", 0.5), (MICROBE_T + 0.3, "pop", 0.4),
          (O2_T, "bubble", 0.8), (O2_T + 1.0, "bubble", 0.7), (O2_T + 2.0, "bubble", 0.6), (PAN[0], "whoosh_soft", 0.5),
          (RUST[0], "sizzle", 0.3), (RUST[0] + 0.6, "pop", 0.4)]
    ev += [(lerp(BURST[0], BURST[1], n / 16), "blip", 0.35) for n in range(16)]
    ev += [(BURST[0], "riser", 0.6), (BURST[0] + 0.6, "shimmer", 0.7), (PIE[0], "whoosh", 0.6), (SWEEP[0], "riser", 0.5),
           (SWEEP[1], "chime", 0.7), (SWEEP[1] + 0.4, "pop", 0.5), (CARDS[0], "whoosh", 0.6)]
    ev += [(tc, "whoosh_soft", 0.5) for tc in CARD_T] + [(tc + 0.4, "chime", 0.45) for tc in CARD_T]
    return ev


MUSIC = dict(
    chords=[(0.0, 53, (0, 7, 12, 16, 19)), (4.2, 50, (0, 7, 12, 14, 17)), (11.0, 55, (0, 7, 12, 14, 19)),
            (15.0, 48, (0, 7, 12, 16, 21)), (18.9, 53, (0, 7, 11, 16, 19)), (25.4, 55, (0, 7, 12, 16, 19)),
            (29.5, 48, (0, 7, 12, 16, 19))],
    plucks=[(4.9, DURATION)], bpm=96, rises=[(BURST[0], BURST[1])],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
