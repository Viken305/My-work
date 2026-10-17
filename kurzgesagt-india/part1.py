"""Part 1: Hook. One in six humans, languages/religions/elections, first cities to the Moon, the question.

  python3 render.py part1 [--still 3,10,20]
"""
from boards import *  # noqa: F401,F403

PART = "part1"
VO = {"H1": 0.6, "H2": 5.5, "H3": 17.5, "H4": 25.7}
DURATION = 31.5
TM = Timing(PART, VO)

S2 = (5.0, 5.6)
S3 = (17.0, 17.6)
S4 = (25.2, 25.8)
SIX_T = TM.word("H1", "six")
LANG_T, REL_T, VOTE_T = TM.word("H2", "languages") - 0.3, TM.word("H2", "religion") - 0.3, TM.word("H2", "voting") - 0.3
CITY_T, MOON_T = S3[1], TM.word("H3", "landed") - 0.3
Q_T = TM.word("H4", "how")


def one_in_six(c, t):
    bg(c, t=t)
    k = smooth(prog(t, 0.2, 1.4))
    draw_india(c, MAP[0], MAP[1] + 30 * (1 - k), MAP[2] * lerp(0.9, 1.0, k), a=255 * k)
    for i in range(6):
        g = pop(t, 1.0 + i * 0.15, 0.5)
        if g > 0:
            c.save()
            c.translate(1150 + i * 120, 760)
            c.scale(g, g)
            if i == 2 and t > SIX_T:
                glow(c, 0, -160, 160, SAFFRON, 160 * smooth(prog(t, SIX_T, SIX_T + 0.4)))
            person(c, 0, 0, 240, i + 3 if i != 2 else 5, t)
            c.restore()
    h = smooth(prog(t, SIX_T, SIX_T + 0.4))
    if h > 0:
        c.drawRRect(rrect(1150 + 2 * 120 - 70, 470, 140, 300, 40), stroke(SAFFRON, 6, 255 * h))
        text(c, "1 IN 6 HUMANS", 1450, 880, 56, SAFFRON, 255 * h, 800, spacing=6)


WORDS = [("नमस्ते", "deva"), ("নমস্কার", "beng"), ("வணக்கம்", "taml"), ("నమస్తే", "telu"), ("ਸਤ ਸ੍ਰੀ ਅਕਾਲ", "guru"), ("آداب", "arab")]


def diversity(c, t):
    bg(c, t=t)
    draw_india(c, 960, 560, 22, glow_a=80)
    for i, (w, sc) in enumerate(WORDS):
        g = smooth(prog(t, LANG_T + i * 0.2, LANG_T + i * 0.2 + 0.5))
        ang = -math.pi / 2 + i * math.pi / 3 + 0.3 + 0.01 * (t - S2[0])
        r = lerp(460, 640, out_cubic(g))
        indic_text(c, w, 900 + r * math.cos(ang), 540 + r * 0.66 * math.sin(ang) + 16, 52, sc, WHITE, 240 * g)
    for i, fn in enumerate(RELIGIONS):
        g = pop(t, REL_T + i * 0.15, 0.45)
        if g <= 0:
            continue
        ang = i * math.pi / 3
        x, y = 930 + 250 * math.cos(ang), 560 + 235 * math.sin(ang)
        c.save()
        c.translate(x, y)
        c.scale(g, g)
        c.drawCircle(0, 0, 52, fill((14, 12, 40), 200))
        fn(c, 0, 0, 34, MARIGOLD)
        c.restore()
    g = pop(t, VOTE_T, 0.5)
    if g > 0:
        c.save()
        c.translate(1660, 930)
        c.scale(g, g)
        c.translate(-1660, -930)
        c.translate(60, 40)
        c.drawRRect(rrect(1560, 760, 200, 170, 20), fill(WHITE))
        c.drawRect(skia.Rect.MakeXYWH(1600, 760, 120, 14), fill(INK))
        ink_finger(c, 1660, 700 - 30 * out_back(prog(t, VOTE_T + 0.3, VOTE_T + 0.8)), 110)
        c.restore()
        text(c, "LARGEST ELECTIONS ON EARTH", 1560, 1050, 26, WHITE, 230 * min(1, g), 800, spacing=3)


def cities_to_moon(c, t):
    bg(c, (40, 22, 40), (90, 40, 50), t=t, dust=False)
    for i in range(7):
        for j in range(5):
            g = pop(t, CITY_T + (i + j) * 0.06, 0.4)
            if g <= 0:
                continue
            x, y = 120 + i * 120, 330 + j * 120
            c.save()
            c.translate(x + 48, y + 48)
            c.scale(g, g)
            c.drawRRect(rrect(-48, -48, 96, 96, 8), fill(mix(TERRACOTTA, TURMERIC, ((i + j) % 3) / 4)))
            c.drawRect(skia.Rect.MakeXYWH(-18, -18, 36, 36), fill(darken(TERRACOTTA, 0.3)))
            c.restore()
    c.drawLine(80, 920, 80 + 840 * smooth(prog(t, CITY_T + 0.5, CITY_T + 1.5)), 920, stroke(CYAN, 8, 180))
    text(c, "c. 2600 BCE", 500, 220, 44, MARIGOLD, 255 * smooth(prog(t, CITY_T, CITY_T + 0.4)), 800, spacing=4)
    wipe = in_out(prog(t, MOON_T - 0.6, MOON_T))
    if wipe > 0:
        off = (1 - wipe) * 1100
        split = poly([(1060 + off, 0), (W + off, 0), (W + off, H), (860 + off, H)])
        c.save()
        c.clipPath(split, doAntiAlias=True)
        c.drawPaint(fill((10, 10, 30)))
        Stars(120, 2).draw(c, t)
        draw_globe(c, 1700, 220, 90, -t * 6)
        moon = skia.Path()
        moon.moveTo(700, H)
        moon.cubicTo(1100, 700, 1700, 680, W + 100, 760)
        moon.lineTo(W + 100, H)
        moon.close()
        c.drawPath(moon, fill((150, 150, 165)))
        for (x, y, r) in [(1300, 900, 40), (1600, 960, 60), (1750, 840, 30)]:
            c.drawCircle(x, y, r, fill((125, 125, 140)))
        land = out_cubic(prog(t, MOON_T, MOON_T + 2.0))
        ly = lerp(300, 790, land)
        if land < 1:
            glow(c, 1420, ly + 20, 80, MARIGOLD, 160 * (1 - land))
        lander(c, 1420, ly, 160)
        if land >= 1:
            dust = prog(t, MOON_T + 2.0, MOON_T + 3.0)
            if dust < 1:
                c.drawOval(skia.Rect.MakeXYWH(1420 - 200 * dust - 60, 780, 400 * dust + 120, 30), fill((200, 200, 210), 160 * (1 - dust)))
        text(c, "2023", 1460, 430, 44, MARIGOLD, 255 * smooth(prog(t, MOON_T + 1.5, MOON_T + 2)), 800, spacing=4)
        c.restore()
        c.drawLine(1060 + off, 0, 860 + off, H, stroke(WHITE, 6, 220))


def question(c, t):
    bg(c, t=t)
    draw_india(c, *MAP, glow_a=140)
    g = smooth(prog(t, S4[1], S4[1] + 0.6))
    indic_text(c, "भारत", 1380, 470 + 30 * (1 - g), 170, "deva", SAFFRON, 255 * g)
    text(c, "INDIA", 1380, 620, 120, WHITE, 255 * smooth(prog(t, S4[1] + 0.3, S4[1] + 0.9)), 800, spacing=20)
    b = pop(t, Q_T, 0.5)
    if b > 0:
        c.save()
        c.translate(1250, 960)
        c.scale(b, b)
        bird(c, 0, 0, 80, t, look=(-1, -0.5))
        c.restore()
        bubble_q(c, 1110, 760, pop(t, Q_T + 0.4, 0.4))


def draw_frame(c, t):
    c.clear(col(INDIGO))
    scenes(c, t, [((0.0, 0.01), S2[1], one_in_six), (S2, S3[1], diversity), (S3, S4[1], cities_to_moon), (S4, DURATION + 1, question)])
    vignette(c)
    chapter_fade(c, t, DURATION)


def sfx_events():
    ev = [(0.3, "swell_soft", 0.6)] + [(1.0 + i * 0.15, "blip", 0.35) for i in range(6)] + [(SIX_T, "chime", 0.7)]
    ev += [(S2[0], "whoosh", 0.6)] + [(LANG_T + i * 0.2, "blip", 0.3) for i in range(6)] + [(REL_T + i * 0.15, "pop", 0.35) for i in range(6)]
    ev += [(VOTE_T, "pop", 0.6), (VOTE_T + 0.4, "click", 0.7), (S3[0], "whoosh", 0.6), (CITY_T, "shimmer", 0.4),
           (MOON_T - 0.6, "whoosh_long", 0.7), (MOON_T, "riser", 0.6), (MOON_T + 2.0, "boom", 0.5), (MOON_T + 2.1, "chime", 0.6),
           (S4[0], "whoosh", 0.6), (S4[1], "swell_soft", 0.7), (Q_T, "pop", 0.6), (Q_T + 0.4, "pop", 0.5)]
    return ev


MUSIC = dict(
    chords=[(0.0, 50, (0, 7, 12, 14, 19)), (5.0, 45, (0, 7, 12, 16, 19)), (11.0, 47, (0, 7, 12, 15, 19)),
            (17.0, 43, (0, 7, 12, 16, 19)), (25.2, 50, (0, 7, 12, 14, 19))],
    plucks=[(5.5, DURATION)], bpm=96, rises=[(MOON_T - 1.5, MOON_T)], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
