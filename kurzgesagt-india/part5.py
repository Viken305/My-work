"""Part 5: Culture. Languages, faiths and festivals, yoga/chess/cinema/cricket, the chilli's journey.

  python3 render.py part5 [--still 3,10,20]
"""
from boards import *  # noqa: F401,F403
from boards import _chilli, _dome_top

PART = "part5"
VO = {"C1": 2.2, "C2": 9.8, "C3": 20.6, "C4": 35.4}
DURATION = 46.5
TM = Timing(PART, VO)

S1 = (1.7, 2.3)
S2 = (9.3, 9.9)
S3 = (20.1, 20.7)
S4 = (34.9, 35.5)
LANG_T = TM.word("C1", "twenty-two") - 0.2
FAITH_T = [TM.word("C2", w) - 0.15 for w in ("hinduism", "buddhism", "jainism", "sikhism")]
MUSLIM_T = TM.word("C2", "muslim") - 0.3
TILE_T = [TM.word("C3", w) - 0.2 for w in ("yoga", "chess", "film", "cricket")]
SAIL = (TM.word("C4", "chillies") - 0.2, TM.word("C4", "chillies") + 4.2)
FAITH_ORDER = [0, 4, 5, 3, 1, 2]   # RELIGIONS index: om, dharma, jain hand, ik onkar, crescent, cross


def title(c, t):
    bg(c, (40, 16, 50), (110, 30, 80), t=t, dust=False)
    petals(c, t)
    rangoli(c, 960, 520, 300, out_cubic(prog(t, 0.0, 1.6)), t)
    g = smooth(prog(t, 0.6, 1.1))
    c.drawCircle(960, 520, 110 * g, fill((60, 16, 50), 230))
    indic_text(c, "५", 960, 575, 150, "deva", MARIGOLD, 255 * g)
    text(c, "CULTURE", 960, 920, 80, WHITE, 255 * g, 800, spacing=10)


WORDS = [("भारत", "deva", "HINDI"), ("ভারত", "beng", "BENGALI"), ("இந்தியா", "taml", "TAMIL"),
         ("భారతదేశం", "telu", "TELUGU"), ("ਭਾਰਤ", "guru", "PUNJABI"), ("بھارت", "arab", "URDU")]


def languages(c, t):
    bg(c, t=t)
    petals(c, t)
    n = int(clamp(prog(t, LANG_T - 0.6, LANG_T + 0.4)) * 22)
    text(c, str(n), 300, 600, 300, SAFFRON, 255, 800)
    text(c, "MAJOR LANGUAGES", 300, 700, 30, WHITE, 230 * smooth(prog(t, LANG_T, LANG_T + 0.4)), 800, spacing=4)
    for i, (w, sc, label) in enumerate(WORDS):
        g = pop(t, LANG_T + 0.6 + i * 0.35, 0.5)
        if g <= 0:
            continue
        x, y = 820 + (i % 3) * 380, 380 + (i // 3) * 360
        c.save()
        c.translate(x, y)
        c.scale(g, g)
        c.drawRRect(rrect(-160, -140, 320, 260, 30), fill((14, 12, 40), 200))
        indic_text(c, w, 0, 10, 70 if len(w) <= 5 else 48, sc, [SAFFRON, MARIGOLD, PEACOCK, RANI, GREEN, WHITE][i])
        text(c, label, 0, 90, 22, WHITE, 200, 800, spacing=4)
        c.restore()


def faiths(c, t):
    bg(c, (30, 16, 50), (90, 30, 80), t=t)
    petals(c, t)
    times = FAITH_T + [MUSLIM_T, MUSLIM_T + 0.5]
    cols = [SAFFRON, PEACOCK, RANI, MARIGOLD, GREEN, WHITE]
    for slot, ri in enumerate(FAITH_ORDER):
        g = pop(t, times[slot], 0.45)
        if g <= 0:
            continue
        x = 260 + slot * 280
        c.save()
        c.translate(x, 360)
        c.scale(g, g)
        c.drawCircle(0, 0, 100, fill((14, 12, 40), 200))
        glow(c, 0, 0, 150, cols[slot], 70)
        RELIGIONS[ri](c, 0, 0, 60, cols[slot])
        c.restore()
    for k in range(9):
        a = smooth(prog(t, S2[1] + 0.3 + k * 0.12, S2[1] + 0.8 + k * 0.12))
        if a > 0:
            diya(c, 300 + k * 165, 800, 40, t + k, 255 * a)
    for k, rgb in enumerate((RANI, MARIGOLD, PEACOCK, GREEN)):
        ph = (t * 0.35 + k * 0.25) % 1
        c.drawCircle(200 + k * 500, 620, 60 + 120 * ph, blur(fill(rgb, 140 * (1 - ph)), 40))
    caption(c, "DIWALI · HOLI · EID · CHRISTMAS · GURPURAB · BUDDHA PURNIMA", 960, 1000, WHITE, 26, 255 * smooth(prog(t, MUSLIM_T + 1.0, MUSLIM_T + 1.4)))


def tiles(c, t):
    bg(c, t=t)
    labels = [("YOGA", PEACOCK), ("CHESS", MARIGOLD), ("CINEMA", RANI), ("CRICKET", GREEN)]
    for i, (label, rgb) in enumerate(labels):
        f = prog(t, TILE_T[i], TILE_T[i] + 0.5)
        if f <= 0:
            continue
        x = 255 + i * 470
        c.save()
        c.translate(x, 500)
        c.scale(max(0.02, out_back(f)), 1)
        c.translate(-x, -500)
        c.drawRRect(rrect(x - 200, 220, 400, 560, 36), fill(mix(INDIGO, rgb, 0.25)))
        text(c, label, x, 740, 40, WHITE, 255, 800, spacing=6)
        cx, cy = x, 470
        if i == 0:
            skin = (190, 135, 98)
            c.drawOval(skia.Rect.MakeXYWH(cx - 150, cy + 80, 300, 90), fill(WHITE))
            c.drawRRect(rrect(cx - 70, cy - 90 + bob(t, 4, 4), 140, 190, 50), fill(WHITE))
            for s_ in (-1, 1):
                c.drawLine(cx + s_ * 60, cy - 50, cx + s_ * 120, cy + 70, stroke(skin, 26))
                c.drawCircle(cx + s_ * 125, cy + 85, 18, fill(skin))
            c.drawCircle(cx, cy - 150, 56, fill(skin))
            c.drawPath(_dome_top(cx, cy - 190, 58, 36), fill((30, 22, 30)))
            eyes(c, cx, cy - 140, 52, t, (0, 0), 0.2, spread=0.32, size=0.1)
            glow(c, cx, cy - 40, 200, PEACOCK, 50 + 30 * math.sin(t * 1.5))
        elif i == 1:
            for a in range(4):
                for b in range(4):
                    c.drawRect(skia.Rect.MakeXYWH(cx - 160 + a * 80, cy + 20 + b * 40, 80, 40), fill(MARBLE if (a + b) % 2 else (120, 80, 50)))
            c.drawPath(poly([(cx - 50, cy + 10), (cx + 50, cy + 10), (cx + 40, cy - 80), (cx + 60, cy - 120), (cx, cy - 190), (cx - 60, cy - 140), (cx - 40, cy - 100), (cx + 5, cy - 110), (cx - 40, cy - 40)]), fill(INK))
        elif i == 2:
            c.save()
            c.translate(cx, cy - 40)
            c.rotate(t * 60)
            c.drawCircle(0, 0, 140, fill((40, 40, 50)))
            for k in range(6):
                a = k / 6 * 6.28
                c.drawCircle(80 * math.cos(a), 80 * math.sin(a), 30, fill(mix(INDIGO, rgb, 0.25)))
            c.drawCircle(0, 0, 24, fill(rgb))
            c.restore()
        else:
            swing = 25 * math.sin(t * 3)
            c.save()
            c.translate(cx, cy + 100)
            c.rotate(swing)
            c.drawRRect(rrect(-30, -300, 60, 300, 26), fill((230, 200, 140)))
            c.drawRRect(rrect(-12, -390, 24, 100, 10), fill((60, 50, 60)))
            c.restore()
            bx = cx + 110 + 30 * math.sin(t * 3 + 1)
            c.drawCircle(bx, cy + 60, 30, fill((200, 40, 40)))
            c.drawLine(bx - 20, cy + 50, bx + 20, cy + 70, stroke(WHITE, 3, 180))
        c.restore()
    g = pop(t, TILE_T[3] + 0.6, 0.5)
    if g > 0:
        c.save()
        c.translate(1880, 820)
        c.scale(g, g)
        bird(c, 0, 0, 46, t, look=(-1, 0))
        c.restore()
    caption(c, "MORE FILMS THAN ANY OTHER COUNTRY", 960, 1000, RANI, 28, 255 * smooth(prog(t, TILE_T[2] + 0.6, TILE_T[2] + 1.0)))


def chilli(c, t):
    bg(c, (30, 60, 110), (40, 110, 160), t=t, dust=False)
    c.drawRect(skia.Rect.MakeXYWH(0, 560, W, H), shaded(linear((0, 560), (0, H), [CYAN, OCEAN])))
    c.drawPath(blob_path(100, 560, [220, 180, 260, 200, 240, 200], 0.2), fill((110, 150, 100)))
    text(c, "THE AMERICAS", 160, 300, 30, WHITE, 230, 800, spacing=4)
    draw_india(c, 1650, 560, 14, glow_a=60, neighbours=False)
    k = in_out(prog(t, *SAIL))
    sx = lerp(260, 1380, k)
    ship(c, sx, 600, 120, t, sail=MARBLE)
    land = prog(t, SAIL[1], SAIL[1] + 1.0)
    if land < 1:
        cx, cy = sx, 380 - 20 * math.sin(t * 2)
        if land > 0:
            cx, cy = lerp(sx, 1650, land), lerp(380, 860, in_cubic(land)) - 200 * math.sin(math.pi * land)
        glow(c, cx, cy, 120, (230, 40, 40), 140)
        c.drawPath(_chilli(cx, cy, 90 * (1 - 0.5 * land)), fill((220, 40, 40)))
        if land == 0:
            pill_tag(c, cx, cy - 110, "CHILLI", (230, 70, 70), 1.0, 24)
    c.drawOval(skia.Rect.MakeXYWH(1500, 840, 300, 120), fill(TERRACOTTA))
    c.drawOval(skia.Rect.MakeXYWH(1520, 840, 260, 70), fill(mix((230, 120, 40), (200, 40, 30), smooth(land))))
    if land >= 1:
        for k2 in range(3):
            ph = (t * 0.5 + k2 / 3) % 1
            c.drawLine(1600 + k2 * 50, 830 - 80 * ph, 1610 + k2 * 50, 800 - 80 * ph, stroke(WHITE, 5, 150 * (1 - ph)))
    caption(c, "CHILLIES ARRIVED ~500 YEARS AGO", 960, 1030, WHITE, 28, 255 * smooth(prog(t, SAIL[0] + 1.0, SAIL[0] + 1.4)))


def draw_frame(c, t):
    c.clear(col(INDIGO))
    scenes(c, t, [((0.0, 0.01), S1[1], title), (S1, S2[1], languages), (S2, S3[1], faiths), (S3, S4[1], tiles), (S4, DURATION + 1, chilli)])
    vignette(c)
    chapter_fade(c, t, DURATION, 0.3)


def sfx_events():
    ev = [(0.2, "shimmer", 0.6), (0.6, "pop", 0.6), (S1[0], "whoosh", 0.6), (LANG_T - 0.6, "ticks", 0.4)]
    ev += [(LANG_T + 0.6 + i * 0.35, "pop", 0.4) for i in range(6)]
    ev += [(S2[0], "whoosh", 0.6)] + [(x, "chime", 0.45) for x in FAITH_T + [MUSLIM_T, MUSLIM_T + 0.5]]
    ev += [(S2[1] + 0.3, "shimmer", 0.4), (S3[0], "whoosh", 0.6)] + [(x, "whoosh_soft", 0.4) for x in TILE_T]
    ev += [(TILE_T[3] + 0.2, "click", 0.8), (TILE_T[3] + 0.6, "pop", 0.5), (S4[0], "whoosh", 0.6), (SAIL[0], "slide", 0.4),
           (SAIL[1], "whoosh_soft", 0.5), (SAIL[1] + 1.0, "bubble", 0.6), (SAIL[1] + 1.1, "sizzle", 0.4)]
    return ev


MUSIC = dict(
    chords=[(0.0, 55, (0, 7, 12, 16, 19)), (9.3, 50, (0, 7, 12, 14, 19)), (20.1, 52, (0, 7, 12, 16, 19)),
            (27.0, 48, (0, 7, 12, 16, 21)), (34.9, 53, (0, 7, 11, 16, 19)), (41.0, 50, (0, 7, 12, 14, 19))],
    plucks=[(2.2, DURATION)], bpm=104, rises=[(SAIL[0], SAIL[1])], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
