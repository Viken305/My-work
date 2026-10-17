"""Part 7: Challenges, the future, and outro.

  python3 render.py part7 [--still 3,10,20]
"""
from boards import *  # noqa: F401,F403

PART = "part7"
VO = {"F1": 2.2, "F2": 18.6, "F3": 23.6, "F4": 34.8}
DURATION = 47.0
TM = Timing(PART, VO)

S1 = (1.7, 2.3)
S2 = (18.1, 18.7)
S3 = (23.1, 23.7)
S4 = (34.3, 34.9)
CH_T = [TM.word("F1", w) - 0.3 for w in ("good jobs", "women", "worst air", "climate")]
HALF_T = TM.word("F2", "half") - 0.2
END_CARD = 41.8


def title(c, t):
    bg(c, (60, 30, 20), (180, 90, 40), t=t, dust=False)
    rangoli(c, 960, 520, 300, out_cubic(prog(t, 0.0, 1.6)), t, (SAFFRON, MARIGOLD, RANI, PEACOCK, WHITE))
    g = smooth(prog(t, 0.6, 1.1))
    c.drawCircle(960, 520, 110 * g, fill((60, 26, 20), 230))
    indic_text(c, "७", 960, 575, 150, "deva", MARIGOLD, 255 * g)
    text(c, "WHAT COMES NEXT", 960, 920, 80, WHITE, 255 * g, 800, spacing=10)


def challenges(c, t):
    bg(c, t=t)
    tiles = [("JOBS FOR YOUNG PEOPLE", PEACOCK), ("WOMEN IN PAID WORK", RANI), ("AIR POLLUTION", (150, 140, 120)), ("HEAT & WATER", SAFFRON)]
    for i, (label, rgb) in enumerate(tiles):
        g = out_back(prog(t, CH_T[i], CH_T[i] + 0.55), 1.2)
        if g <= 0:
            continue
        x = 255 + i * 470
        y_off = (1 - g) * 700
        c.save()
        c.translate(0, y_off)
        c.drawRRect(rrect(x - 200, 200, 400, 600, 36), fill(mix(INDIGO, rgb, 0.25)))
        text(c, label, x, 760, 24, WHITE, 255, 800, spacing=2)
        if i == 0:
            for k in range(5):
                person(c, x - 140 + k * 70, 640, 160, k + 40, t)
            c.drawRRect(rrect(x - 40, 360, 80, 60, 10), fill((120, 80, 50)))
            c.drawRRect(rrect(x - 16, 346, 32, 18, 6), stroke((120, 80, 50), 6))
        elif i == 1:
            person(c, x, 640, 300, 1, t)
            c.drawRRect(rrect(x - 80, 540, 160, 100, 10), fill((200, 205, 220)))
            c.drawRRect(rrect(x - 70, 550, 140, 80, 6), fill(PEACOCK))
        elif i == 2:
            for k in range(5):
                c.drawRect(skia.Rect.MakeXYWH(x - 160 + k * 66, 640 - 80 - (k * 30) % 90, 50, 80 + (k * 30) % 90), fill((90, 85, 100)))
            haze = 0.6 + 0.2 * math.sin(t * 0.8)
            c.drawRect(skia.Rect.MakeXYWH(x - 200, 300, 400, 340), fill((180, 170, 150), 150 * haze))
        else:
            glow(c, x, 360, 160, SAFFRON, 120 + 40 * math.sin(t * 2))
            c.drawCircle(x, 360, 80, fill(SAFFRON))
            for k in range(6):
                c.drawLine(x - 150 + k * 60, 520, x - 130 + k * 60, 640, stroke((90, 60, 40), 6))
        c.restore()


def young(c, t):
    bg(c, t=t)
    pyramid(c, 620, 900, 780, 680, smooth(prog(t, S2[1], S2[1] + 2.0)))
    g = smooth(prog(t, HALF_T, HALF_T + 0.5))
    text(c, "HALF UNDER 30", 1400, 520, 80, MARIGOLD, 255 * g, 800, spacing=6)
    text(c, "MEDIAN AGE ~28", 1400, 600, 34, WHITE, 230 * g, 800, spacing=4)


def lifetime(c, t):
    bg(c, t=t)
    k = in_out(prog(t, S3[1], S3[1] + 6.0))
    c.drawLine(200, 560, 200 + 1520 * k, 560, stroke(WHITE, 8, 200))
    for x, yr, lines, tt in ((200, "1947", ["NEWLY INDEPENDENT", "POOR · DIVIDED"], S3[1]), (1720, "TODAY", ["LARGEST DEMOCRACY", "TOP-5 ECONOMY"], S3[1] + 5.6)):
        g = pop(t, tt, 0.5)
        if g <= 0:
            continue
        c.drawCircle(x, 560, 30 * g, fill(SAFFRON))
        text(c, yr, x, 480, 60, SAFFRON, 255 * min(1, g), 800, spacing=4)
        for j, ln in enumerate(lines):
            text(c, ln, x, 650 + j * 44, 28, WHITE, 230 * min(1, g), 800, spacing=3)
    for j in range(5):
        x = 600 + j * 180
        if 200 + 1520 * k > x:
            person(c, x, 520, 120 + j * 25, j + 50, t)


def sunrise(c, t):
    rise = out_cubic(prog(t, S4[0], S4[0] + 5.0))
    bg(c, (20, 16, 50), mix((60, 40, 90), (240, 140, 80), rise), t=t, dust=False)
    glow(c, 960, 900, 600, MARIGOLD, 200 * rise)
    c.drawCircle(960, lerp(1150, 900, rise), 180, fill((255, 210, 120)))
    draw_india(c, 960, 650, 16, glow_a=60, neighbours=False, a=200)
    c.drawRect(skia.Rect.MakeXYWH(0, 900, W, 200), fill((40, 24, 50)))
    b = pop(t, S4[1] + 0.5, 0.5)
    if b > 0:
        c.save()
        c.translate(1500, 905)
        c.scale(b, b)
        bird(c, 0, 0, 70, t, look=(-1, -0.3))
        c.restore()
    ea = smooth(prog(t, END_CARD, END_CARD + 0.8))
    if ea > 0:
        indic_text(c, "भारत", 960, 150, 100, "deva", WHITE, 255 * ea)
        text(c, "INDIA", 960, 230, 46, WHITE, 230 * ea, 800, spacing=16)
        text(c, "SOURCES IN THE DESCRIPTION", 960, 1010, 22, MARIGOLD, 220 * ea, 800, spacing=6)


def draw_frame(c, t):
    c.clear(col(INDIGO))
    scenes(c, t, [((0.0, 0.01), S1[1], title), (S1, S2[1], challenges), (S2, S3[1], young), (S3, S4[1], lifetime), (S4, DURATION + 1, sunrise)])
    vignette(c)
    chapter_fade(c, t, DURATION, 0.3, 1.4)


def sfx_events():
    ev = [(0.2, "shimmer", 0.6), (0.6, "pop", 0.6), (S1[0], "whoosh", 0.6)] + [(x, "whoosh_soft", 0.5) for x in CH_T]
    ev += [(S2[0], "whoosh", 0.6), (S2[1], "riser", 0.4), (HALF_T, "chime", 0.6), (S3[0], "whoosh", 0.6), (S3[1], "pop", 0.5),
           (S3[1] + 5.6, "pop", 0.5), (S4[0], "whoosh_long", 0.6), (S4[0] + 0.5, "swell_soft", 0.8), (S4[1] + 0.5, "pop", 0.4), (END_CARD, "swell_soft", 0.7)]
    return ev


MUSIC = dict(
    chords=[(0.0, 50, (0, 7, 12, 15, 19)), (8.0, 46, (0, 7, 12, 16, 19)), (18.1, 55, (0, 7, 12, 16, 19)),
            (23.1, 48, (0, 7, 12, 16, 19)), (34.3, 50, (0, 7, 12, 14, 19)), (END_CARD, 50, (0, 7, 12, 16, 19, 24))],
    plucks=[(2.2, 34.0), (34.8, END_CARD)], bpm=96, rises=[(S3[1], S3[1] + 5.6)], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
