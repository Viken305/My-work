"""Part 4: Building a republic. Ambedkar's constitution, Nehru's nation-building, Green Revolution, 1991.

  python3 render.py part4 [--still 3,10,20]
"""
from boards import *  # noqa: F401,F403

PART = "part4"
VO = {"R1": 2.2, "R2": 24.6, "R3": 32.6, "R4": 41.0}
DURATION = 53.5
TM = Timing(PART, VO)

S1 = (1.7, 2.3)
S2 = (24.1, 24.7)
S3 = (32.1, 32.7)
S4 = (40.5, 41.1)
AMB_T = TM.word("R1", "ambedkar") - 0.4
VOTE_T = TM.word("R1", "every adult") - 0.2
DATE_T = TM.word("R1", "twenty-sixth") - 0.2
BUILD_T = [TM.word("R2", w) - 0.2 for w in ("dams", "steel", "universities")]
GATE_T = TM.word("R4", "opened") - 0.3
SOFT_T = TM.word("R4", "software") - 0.3


def title(c, t):
    bg(c, (20, 30, 70), (40, 50, 110), t=t, dust=False)
    k = out_cubic(prog(t, 0.0, 1.6))
    chakra(c, 960, 520, 230 * k, t * 40, WHITE, 230)
    g = smooth(prog(t, 0.6, 1.1))
    c.drawCircle(960, 520, 110 * g, fill(CHAKRA, 240))
    indic_text(c, "४", 960, 575, 150, "deva", WHITE, 255 * g)
    text(c, "BUILDING A REPUBLIC", 960, 920, 80, WHITE, 255 * g, 800, spacing=10)


def constitution(c, t):
    bg(c, t=t)
    leader_card(c, 330, 500, "ambedkar", t, 1.1 * out_back(prog(t, AMB_T, AMB_T + 0.6)), look=(0.5, 0), phase=0.6)
    op = smooth(prog(t, S1[1] + 0.3, S1[1] + 1.6))
    book(c, 1150, 430, 300, op, "THE CONSTITUTION OF INDIA")
    for i in range(10):
        g = pop(t, VOTE_T + i * 0.12, 0.45)
        if g <= 0:
            continue
        c.save()
        c.translate(760 + i * 85, 980)
        c.scale(g, g)
        person(c, 0, 0, 150, i + 30, t)
        ink_finger(c, 40, -180 - 20 * smooth(prog(t, VOTE_T + 1.5 + i * 0.05, VOTE_T + 2 + i * 0.05)), 26)
        c.restore()
    caption(c, "26 JANUARY 1950  ·  EVERY ADULT CAN VOTE", 1150, 1040, MARIGOLD, 26, 255 * smooth(prog(t, DATE_T, DATE_T + 0.4)))


def nation(c, t):
    bg(c, (20, 30, 60), (40, 70, 110), t=t)
    leader_card(c, 330, 500, "nehru", t, 1.1 * out_back(prog(t, S2[1], S2[1] + 0.6)), look=(0.5, 0), phase=1.2)
    c.drawRect(skia.Rect.MakeXYWH(640, 820, 1280, 260), fill((60, 70, 90)))
    g = out_cubic(prog(t, BUILD_T[0], BUILD_T[0] + 1.0))
    if g > 0:
        c.drawPath(poly([(700, 820), (760, 820 - 380 * g), (1020, 820 - 380 * g), (1080, 820)]), fill((180, 180, 190)))
        c.drawRect(skia.Rect.MakeXYWH(700, 820, 380, 60 * smooth(prog(t, BUILD_T[0] + 0.6, BUILD_T[0] + 1.6))), shaded(linear((0, 820), (0, 880), [CYAN, OCEAN])))
    for k in range(3):
        h = out_back(prog(t, BUILD_T[1] + k * 0.15, BUILD_T[1] + 0.6 + k * 0.15))
        if h > 0:
            top = 820 - (340 + k * 40) * h
            c.drawRect(skia.Rect.MakeXYWH(1200 + k * 90, top, 50, 820 - top), fill((120, 110, 130)))
            ph = (t * 0.4 + k / 3) % 1
            c.drawCircle(1225 + k * 90 + 20 * ph, top - 40 - 60 * ph, 30 + 30 * ph, fill((200, 200, 210), 160 * (1 - ph)))
    u = pop(t, BUILD_T[2], 0.6)
    if u > 0:
        c.save()
        c.translate(1700, 820)
        c.scale(u, u)
        c.translate(-1700, -820)
        c.drawPath(poly([(1500, 820), (1500, 560), (1700, 460), (1900, 560), (1900, 820)]), fill(MARBLE))
        for k in range(4):
            c.drawRect(skia.Rect.MakeXYWH(1530 + k * 90, 600, 40, 220), fill((200, 190, 180)))
        c.restore()
    for i, lbl in enumerate(("DAMS", "STEEL", "UNIVERSITIES")):
        text(c, lbl, (890, 1335, 1700)[i], 960, 28, WHITE, 230 * smooth(prog(t, BUILD_T[i] + 0.3, BUILD_T[i] + 0.7)), 800, spacing=4)


def green(c, t):
    bg(c, (60, 120, 200), (170, 210, 240), t=t, dust=False)
    c.drawRect(skia.Rect.MakeXYWH(0, 600, W, H), fill((120, 90, 50)))
    sweep = lerp(-200, W + 400, in_out(prog(t, S3[1] + 0.5, S3[1] + 5.0)))
    for k in range(40):
        x = 40 + k * 48
        for j in range(4):
            y = 640 + j * 110
            g = clamp((sweep - x) / 300)
            sway = 4 * math.sin(t * 2 + x * 0.02)
            c.drawLine(x, y + 90, x + sway, y + 90 - 90 * (0.5 + 0.5 * g), stroke(mix((150, 120, 60), (220, 180, 60), g), 6))
            c.drawOval(skia.Rect.MakeXYWH(x + sway - 8, y + 90 - 90 * (0.5 + 0.5 * g) - 26, 16, 34), fill(mix((150, 120, 60), MARIGOLD, g)))
    person(c, 1700, 1020, 330, 6, t, wave=smooth(prog(t, S3[1] + 4.5, S3[1] + 5.2)))
    caption(c, "GREEN REVOLUTION  ·  1960s–70s", 960, 140, WHITE, 30, 255 * smooth(prog(t, S3[1], S3[1] + 0.4)))
    text(c, "FOOD AID", 220, 560, 34, WHITE, 230, 800, spacing=4)
    text(c, "→  FEEDING ITSELF", 1200, 560, 34, WHITE, 230 * smooth(prog(t, S3[1] + 4.0, S3[1] + 4.5)), 800, spacing=4)


def reforms(c, t):
    bg(c, t=t)
    op = in_out(prog(t, GATE_T, GATE_T + 1.2))
    for sgn in (-1, 1):
        c.drawRRect(rrect(560 + sgn * 170 - 30, 320, 60, 520, 10), fill((140, 130, 160)))
        w = 140 * (1 - op) + 30
        x0 = 560 + sgn * 140
        c.drawPath(poly([(x0, 360), (x0 - sgn * w, 380), (x0 - sgn * w, 800), (x0, 820)]), fill((110, 100, 130)))
    text(c, "1991", 560, 260, 70, MARIGOLD, 255, 800, spacing=6)
    n = 1 + int(10 * smooth(prog(t, GATE_T + 0.8, GATE_T + 4.0)))
    pts = [(900 + i * 50, 900 - (i ** 1.7) * 9) for i in range(n)]
    if n > 1:
        c.drawPath(poly(pts, False), stroke(GREEN, 12))
    draw_globe(c, 1580, 470, 170, -t * 6)
    for k in range(6):
        g = pop(t, SOFT_T + k * 0.12, 0.45)
        if g <= 0:
            continue
        a = k / 6 * 6.28 + t * 0.3
        x, y = 1580 + 270 * math.cos(a), 470 + 230 * math.sin(a)
        c.save()
        c.translate(x, y)
        c.scale(g, g)
        c.drawRRect(rrect(-46, -30, 92, 60, 8), fill((60, 60, 80)))
        c.drawRRect(rrect(-38, -24, 76, 46, 5), fill(PEACOCK))
        text(c, "</>", 0, 8, 22, WHITE, 230, 800)
        c.restore()
    caption(c, "ECONOMY OPENS UP  ·  SOFTWARE GOES GLOBAL", 960, 1030, WHITE, 28, 255 * smooth(prog(t, SOFT_T, SOFT_T + 0.4)))


def draw_frame(c, t):
    c.clear(col(INDIGO))
    scenes(c, t, [((0.0, 0.01), S1[1], title), (S1, S2[1], constitution), (S2, S3[1], nation), (S3, S4[1], green), (S4, DURATION + 1, reforms)])
    vignette(c)
    chapter_fade(c, t, DURATION, 0.3)


def sfx_events():
    ev = [(0.2, "shimmer", 0.6), (0.6, "pop", 0.6), (S1[0], "whoosh", 0.6), (S1[1] + 0.3, "slide", 0.5), (AMB_T, "pop", 0.6)]
    ev += [(VOTE_T + i * 0.12, "blip", 0.3) for i in range(10)] + [(DATE_T, "chime", 0.7)]
    ev += [(S2[0], "whoosh", 0.6), (S2[1], "pop", 0.5)] + [(b, "pop", 0.5) for b in BUILD_T]
    ev += [(S3[0], "whoosh", 0.6), (S3[1] + 0.5, "shimmer", 0.6), (S3[1] + 4.5, "chime", 0.5), (S4[0], "whoosh", 0.6), (GATE_T, "slide", 0.7), (GATE_T + 0.8, "riser", 0.5)]
    ev += [(SOFT_T + k * 0.12, "blip", 0.3) for k in range(6)]
    return ev


MUSIC = dict(
    chords=[(0.0, 50, (0, 7, 12, 16, 19)), (12.0, 45, (0, 7, 12, 15, 19)), (24.1, 47, (0, 7, 12, 16, 19)),
            (32.1, 52, (0, 7, 12, 16, 19)), (40.5, 50, (0, 7, 12, 14, 19)), (47.0, 55, (0, 7, 11, 16, 19))],
    plucks=[(2.2, DURATION)], bpm=96, rises=[(GATE_T + 0.8, GATE_T + 4.0)], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
