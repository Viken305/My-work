"""Part 2: Ancient India. Indus cities, Vedas + Buddhism + Jainism, Ashoka and his pillar, the emblem, zero.

  python3 render.py part2 [--still 3,10,20]
"""
from boards import *  # noqa: F401,F403

PART = "part2"
VO = {"A1": 2.2, "A2": 17.5, "A3": 27.4, "A4": 45.6}
DURATION = 56.5
TM = Timing(PART, VO)

S2 = (17.0, 17.6)
S3 = (26.9, 27.5)
S4 = (TM.word("A3", "the lions") - 0.5, TM.word("A3", "the lions"))
S5 = (45.1, 45.7)
DRAIN_T = TM.word("A1", "covered drains") - 0.3
BATH_T = TM.word("A1", "indus valley") - 0.3
VEDA_T = TM.word("A2", "vedas") - 0.3
BUD_T, JAIN_T = TM.word("A2", "buddhism") - 0.2, TM.word("A2", "jainism") - 0.2
WAR_T = TM.word("A3", "brutal war") - 0.2
PILLAR_T = TM.word("A3", "stone pillars") - 0.6
ZERO_T = TM.word("A4", "zero") - 0.3


def title(c, t):
    bg(c, (50, 30, 30), (110, 60, 40), t=t, dust=False)
    rangoli(c, 960, 520, 300, out_cubic(prog(t, 0.0, 1.6)), t, (TERRACOTTA, TURMERIC, MARIGOLD, SAFFRON, WHITE))
    g = smooth(prog(t, 0.6, 1.1))
    c.drawCircle(960, 520, 110 * g, fill((40, 20, 20), 230))
    indic_text(c, "२", 960, 575, 150, "deva", MARIGOLD, 255 * g)
    text(c, "ANCIENT INDIA", 960, 920, 80, WHITE, 255 * g, 800, spacing=10)


def indus(c, t):
    c.drawPaint(fill(mix(TERRACOTTA, (90, 50, 40), 0.6)))
    z = lerp(1.25, 1.0, in_out(prog(t, 1.5, 8.0)))
    cam(c, z, 960, 540)
    for i in range(12):
        for j in range(6):
            if (i, j) in ((5, 2), (6, 2), (5, 3), (6, 3)):
                continue
            g = pop(t, 1.6 + ((i - 5.5) ** 2 + (j - 2.5) ** 2) ** 0.5 * 0.18, 0.45)
            if g <= 0:
                continue
            x, y = 70 + i * 150, 120 + j * 150
            c.save()
            c.translate(x + 60, y + 60)
            c.scale(g, g)
            c.drawRRect(rrect(-60, -60, 120, 120, 10), fill(mix(TERRACOTTA, TURMERIC, ((i * 7 + j) % 5) / 8)))
            c.drawRRect(rrect(-40, -40, 80, 80, 6), fill(darken(TERRACOTTA, 0.25)))
            c.restore()
    flow = smooth(prog(t, DRAIN_T, DRAIN_T + 2.0))
    for j in range(7):
        c.drawLine(40, 105 + j * 150, 40 + (W - 80) * flow, 105 + j * 150, stroke(CYAN, 5, 160))
        for k in range(6):
            ph = (t * 0.15 + k / 6 + j * 0.1) % 1
            if ph < flow:
                c.drawCircle(40 + (W - 80) * ph, 105 + j * 150, 5, fill(WHITE, 160))
    c.drawRRect(rrect(820, 420, 270, 270, 16), fill(darken(TERRACOTTA, 0.3)))
    fill_k = smooth(prog(t, BATH_T - 1.0, BATH_T + 1.0))
    if fill_k > 0:
        c.save()
        c.clipRRect(rrect(850, 450, 210, 210, 10), doAntiAlias=True)
        c.drawRect(skia.Rect.MakeXYWH(850, 660 - 210 * fill_k, 210, 210), shaded(linear((0, 450), (0, 660), [CYAN, OCEAN])))
        c.restore()
    pill_tag(c, 955, 380, "GREAT BATH", MARIGOLD, pop(t, BATH_T, 0.4), 24)
    for k in range(4):
        x = (300 + k * 380 + t * 18) % (W + 200) - 100
        person(c, x, 105 + (1 + k % 4) * 150 + 30, 70, k + 70, t)
    c.restore()
    caption(c, "INDUS VALLEY CIVILISATION  ·  c. 2600–1900 BCE", 960, 1030, MARIGOLD, 30, 255 * smooth(prog(t, BATH_T + 0.3, BATH_T + 0.7)))


def ideas(c, t):
    bg(c, (40, 24, 50), (80, 40, 60), t=t)
    u = out_cubic(prog(t, VEDA_T, VEDA_T + 1.2))
    c.drawRRect(rrect(960 - 500 * u, 640, 1000 * u, 170, 30), fill((210, 170, 110)))
    for k in range(4):
        c.drawLine(960 - 440 * u, 690 + k * 32, 960 + 440 * u, 690 + k * 32, stroke((150, 110, 70), 6))
    glow(c, 960, 720, 500, MARIGOLD, 90 * u)
    indic_text(c, "ऋग्वेद", 960, 600, 70, "deva", MARIGOLD, 255 * smooth(prog(t, VEDA_T + 0.6, VEDA_T + 1.0)))
    for i, (fn, label, tt) in enumerate([(sym_om, "HINDUISM", VEDA_T + 1.0), (sym_dharma, "BUDDHISM", BUD_T), (sym_jain_hand, "JAINISM", JAIN_T)]):
        g = pop(t, tt, 0.5)
        if g <= 0:
            continue
        x = 560 + i * 400
        y = 300 + 40 * (1 - min(1, g))
        c.drawCircle(x, y, 90 * g, fill((14, 12, 40), 210))
        glow(c, x, y, 150, SAFFRON, 90 * min(1, g))
        c.save()
        c.translate(x, y)
        c.scale(g, g)
        fn(c, 0, 0, 56, SAFFRON)
        c.restore()
        text(c, label, x, 450, 30, WHITE, 240 * min(1, g), 800, spacing=4)


def ashoka(c, t):
    war = smooth(prog(t, WAR_T, WAR_T + 0.4)) * (1 - smooth(prog(t, WAR_T + 2.4, WAR_T + 3.2)))
    bg(c, mix((60, 30, 40), SOMBRE, war), mix((120, 60, 50), (70, 66, 84), war), t=t)
    g = out_back(prog(t, S3[1], S3[1] + 0.6))
    leader_card(c, 520, 520, "ashoka", t, 1.25 * g, look=(0.6 * smooth(prog(t, PILLAR_T, PILLAR_T + 0.5)), 0), phase=0.4)
    c.drawRect(skia.Rect.MakeXYWH(0, 940, W, 140), fill((90, 60, 50)))
    rise = out_cubic(prog(t, PILLAR_T, PILLAR_T + 1.6))
    if rise > 0:
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(0, 0, W, 950))
        c.translate(0, 820 * (1 - rise))
        ashoka_pillar(c, 1350, 950, 820)
        c.restore()
    caption(c, "KALINGA WAR  ·  c. 261 BCE", 960, 1035, MARBLE, 26, 255 * war)
    caption(c, "MESSAGES OF TOLERANCE IN STONE", 960, 1035, MARIGOLD, 26, 255 * smooth(prog(t, PILLAR_T + 1.0, PILLAR_T + 1.4)))


def emblem(c, t):
    bg(c, t=t)
    glow(c, 960, 520, 520, TURMERIC, 80)
    z = lerp(1.6, 1.0, out_cubic(prog(t, S4[0], S4[0] + 1.6)))
    c.save()
    c.translate(960, 600)
    c.scale(z, z)
    c.translate(-960, -600)
    lion_capital(c, 960, 800, 360)
    c.restore()
    indic_text(c, "सत्यमेव जयते", 960, 900, 64, "deva", WHITE, 255 * smooth(prog(t, S4[1] + 1.0, S4[1] + 1.6)))
    caption(c, "STILL INDIA'S NATIONAL EMBLEM", 960, 1010, MARIGOLD, 30, 255 * smooth(prog(t, S4[1] + 1.8, S4[1] + 2.2)))


def zero(c, t):
    bg(c, t=t)
    draw_globe(c, 1200, 560, 330, -t * 5)
    for i, d in enumerate("1234567890"):
        k = out_cubic(prog(t, S5[1] + 0.6 + i * 0.25, S5[1] + 1.6 + i * 0.25))
        if k <= 0:
            continue
        ang = -math.pi * 0.9 + i * math.pi * 0.2 + 0.05 * (t - S5[0])
        x, y = lerp(400, 1200 + 470 * math.cos(ang), k), lerp(560, 560 + 400 * math.sin(ang), k)
        text(c, d, x, y + 30, 90, MARIGOLD if d != "0" else SAFFRON, 255, 800)
    g = pop(t, ZERO_T, 0.6)
    glow(c, 400, 520, 260, SAFFRON, 140 * min(1, g))
    c.save()
    c.translate(400, 520)
    c.scale(max(g, 0.001), max(g, 0.001))
    indic_text(c, "०", 0, 80, 300, "deva", SAFFRON)
    c.restore()
    text(c, "ZERO", 400, 760, 50, WHITE, 255 * min(1, g), 800, spacing=10)
    caption(c, "THE DECIMAL SYSTEM THE WHOLE WORLD USES", 960, 1030, WHITE, 28, 255 * smooth(prog(t, ZERO_T + 2.5, ZERO_T + 3.0)))


def draw_frame(c, t):
    c.clear(col(INDIGO))
    scenes(c, t, [((0.0, 0.01), 2.3, title), ((1.7, 2.3), S2[1], indus), (S2, S3[1], ideas), (S3, S4[1], ashoka),
                  (S4, S5[1], emblem), (S5, DURATION + 1, zero)])
    vignette(c)
    chapter_fade(c, t, DURATION, 0.3)


def sfx_events():
    ev = [(0.2, "shimmer", 0.6), (0.6, "pop", 0.6), (1.7, "whoosh", 0.6)] + [(1.6 + k * 0.25, "click", 0.3) for k in range(10)]
    ev += [(DRAIN_T, "bubble", 0.5), (BATH_T - 1.0, "bubble", 0.4), (BATH_T, "pop", 0.5), (S2[0], "whoosh", 0.6), (VEDA_T, "slide", 0.4),
           (VEDA_T + 0.6, "chime", 0.5), (VEDA_T + 1.0, "pop", 0.5), (BUD_T, "pop", 0.5), (JAIN_T, "pop", 0.5), (S3[0], "whoosh", 0.6),
           (S3[1], "pop", 0.5), (WAR_T, "boom", 0.5), (PILLAR_T, "rumble", 0.6), (PILLAR_T + 1.6, "chime", 0.5), (S4[0], "whoosh", 0.6),
           (S4[1] + 1.0, "shimmer", 0.6), (S5[0], "whoosh", 0.6), (ZERO_T, "shine", 0.8)]
    ev += [(S5[1] + 0.6 + i * 0.25, "blip", 0.3) for i in range(10)]
    return ev


MUSIC = dict(
    chords=[(0.0, 50, (0, 7, 12, 13, 19)), (7.0, 46, (0, 7, 12, 16, 19)), (17.0, 50, (0, 7, 12, 14, 19)),
            (26.9, 45, (0, 7, 12, 15, 19)), (37.0, 43, (0, 7, 12, 16, 19)), (45.1, 50, (0, 7, 12, 16, 21))],
    plucks=[(2.2, 26.5), (37.5, DURATION)], bpm=96, rises=[(ZERO_T + 0.3, ZERO_T + 3.0)], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
