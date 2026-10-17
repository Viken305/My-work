"""Part 6: India today and Narendra Modi. Economy, UPI, Chandrayaan; Modi's path, policies, both views, 2024.

Balance rules (STYLE_GUIDE.md): facts in the narrator's voice, opinions attributed, the SUPPORTERS/CRITICS
panels identical in size, colour, point count and timing; Modi's card identical to every other leader's.

  python3 render.py part6 [--still 3,10,20]
"""
from boards import *  # noqa: F401,F403
from boards import _ic_card, _ic_note, _ic_pin, _ic_receipt, _ic_road, _ic_toilet

PART = "part6"
VO = {"T1": 2.2, "T2": 15.0, "T3": 32.8, "T4": 54.4, "T5": 80.0, "T6": 94.2}
DURATION = 104.5
TM = Timing(PART, VO)

S1 = (1.7, 2.3)
S2 = (14.5, 15.1)
S3 = (32.3, 32.9)
S4 = (53.9, 54.5)
S5 = (79.5, 80.1)
S6 = (93.7, 94.3)
JAPAN_T = TM.word("T1", "overtake japan") - 0.2
UPI_T = TM.word("T2", "upi") - 0.2
MOON_T = TM.word("T2", "in 2023") - 0.2
# timeline rows in chronological order, each revealed as it is narrated ("Since 2014" is said first)
STEPS = [("1950", "BORN IN VADNAGAR, GUJARAT", TM.word("T3", "born in 1950") - 0.2),
         ("RSS", "RISES THROUGH THE RSS", TM.word("T3", "rss") - 0.2),
         ("2001–14", "CHIEF MINISTER OF GUJARAT", TM.word("T3", "ran the state") - 0.2),
         ("2014–", "PRIME MINISTER OF INDIA", S3[1] + 0.3)]
STEP_T = [st[2] for st in STEPS]
POL_T = [TM.word("T4", w) - 0.2 for w in ("goods and services", "roads", "bank accounts", "toilets")]
CON_T = [TM.word("T4", "cash notes") - 0.3, TM.word("T4", "jammu") - 0.3]
CON_HEAD = TM.word("T4", "bold") - 0.2
COL_T = [TM.word("T5", "supporters") - 0.2, TM.word("T5", "critics") - 0.2]
SEATS_T = TM.word("T6", "third term") - 0.4
ALLY_T = TM.word("T6", "coalition") - 0.4


def title(c, t):
    bg(c, (16, 40, 60), (31, 100, 110), t=t, dust=False)
    rangoli(c, 960, 520, 300, out_cubic(prog(t, 0.0, 1.6)), t, (PEACOCK, SAFFRON, MARIGOLD, GREEN, WHITE))
    g = smooth(prog(t, 0.6, 1.1))
    c.drawCircle(960, 520, 110 * g, fill((14, 40, 50), 230))
    indic_text(c, "६", 960, 575, 150, "deva", MARIGOLD, 255 * g)
    text(c, "INDIA TODAY", 960, 920, 80, WHITE, 255 * g, 800, spacing=10)


ECON = [("USA", 30.5, (110, 120, 160)), ("CHINA", 20.0, (110, 120, 160)), ("GERMANY", 5.0, (110, 120, 160)),
        ("JAPAN", 4.5, (110, 120, 160)), ("INDIA", 4.3, SAFFRON)]


def economy(c, t):
    bg(c, t=t)
    k = smooth(prog(t, S1[1] + 0.3, S1[1] + 3.0))
    bars(c, 260, 860, 1400, 560, ECON, k, highlight=4 if k > 0.9 else None)
    j = smooth(prog(t, JAPAN_T, JAPAN_T + 0.6))
    if j > 0:
        c.saveLayerAlpha(None, int(255 * j))
        c.drawPath(poly([(1530, 800), (1380, 800), (1380, 780), (1330, 815), (1380, 850), (1380, 830), (1530, 830)]), fill(MARIGOLD))
        text(c, "4TH BY 2027 (PROJECTED)", 1420, 720, 26, MARIGOLD, 255, 800, spacing=2)
        c.restore()
    text(c, "MOST POPULOUS · FASTEST-GROWING MAJOR ECONOMY", 960, 180, 30, WHITE, 230 * smooth(prog(t, S1[1], S1[1] + 0.5)), 800, spacing=3)
    caption(c, "NOMINAL GDP, APPROX. TRILLION US$  ·  IMF WORLD ECONOMIC OUTLOOK, OCT 2026", 960, 1010, WHITE, 24, 255 * k)


def upi_moon(c, t):
    bg(c, t=t)
    g = pop(t, UPI_T, 0.5)
    if g > 0:
        c.save()
        c.translate(520, 520)
        c.scale(g, g)
        c.translate(-520, -520)
        phone_qr(c, 520, 520, 300, t)
        scan = (t * 0.8) % 1
        c.drawLine(390, 330 + 220 * scan, 650, 330 + 220 * scan, stroke(GREEN, 6, 200))
        c.restore()
        n = clamp(prog(t, UPI_T + 0.5, UPI_T + 3.0)) * 24
        text(c, f"{n:.0f} BILLION+", 520, 940, 54, GREEN, 255 * min(1, g), 800, spacing=4)
        text(c, "UPI PAYMENTS / MONTH", 520, 990, 26, WHITE, 220 * min(1, g), 800, spacing=4)
    text(c, "HUNDREDS OF MILLIONS OUT OF EXTREME POVERTY", 960, 110, 28, MARIGOLD, 240 * smooth(prog(t, S2[1], S2[1] + 0.5)) * (1 - smooth(prog(t, UPI_T, UPI_T + 0.4))), 800, spacing=3)
    m = smooth(prog(t, MOON_T - 0.5, MOON_T))
    if m > 0:
        c.saveLayerAlpha(None, int(255 * m))
        c.drawRRect(rrect(1000, 160, 820, 760, 40), fill((10, 10, 30)))
        c.save()
        c.clipRRect(rrect(1000, 160, 820, 760, 40), doAntiAlias=True)
        Stars(80, 6).draw(c, t)
        c.drawPath(blob_path(1410, 1100, [520, 500, 540, 510, 530, 500], 0.1), fill((150, 150, 165)))
        lander(c, 1410, lerp(260, 660, out_cubic(prog(t, MOON_T, MOON_T + 2.5))), 200)
        c.restore()
        text(c, "CHANDRAYAAN-3 · 2023", 1410, 990, 34, MARIGOLD, 255, 800, spacing=3)
        c.restore()


def modi(c, t):
    bg(c, t=t)
    leader_card(c, 430, 520, "modi", t, 1.35 * out_back(prog(t, S3[1], S3[1] + 0.6)), look=(0.5 * smooth(prog(t, STEP_T[0], STEP_T[0] + 0.5)), 0), phase=0.9)
    c.drawLine(1000, 240, 1000, 840, stroke(WHITE, 6, 150 * smooth(prog(t, S3[1], S3[1] + 0.6))))
    for row, (yr, label, tt) in enumerate(STEPS):
        g = pop(t, tt, 0.45)
        if g <= 0:
            continue
        y = 260 + row * 190
        c.drawCircle(1000, y, 22 * g, fill(MARIGOLD))
        text(c, yr, 1050, y - 6, 40, MARIGOLD, 255 * min(1, g), 800, "left", spacing=2)
        text(c, label, 1050, y + 40, 26, WHITE, 230 * min(1, g), 800, "left", spacing=2)


def policies(c, t):
    bg(c, t=t)
    icons = [("GST · 2017", _ic_receipt), ("ROADS · RAIL · AIRPORTS", _ic_road), ("500M+ BANK ACCOUNTS", _ic_card), ("100M+ TOILETS", _ic_toilet)]
    for i, (label, fn) in enumerate(icons):
        g = pop(t, POL_T[i], 0.45)
        if g <= 0:
            continue
        x = 280 + i * 455
        c.save()
        c.translate(x, 350)
        c.scale(g, g)
        c.translate(-x, -350)
        c.drawRRect(rrect(x - 190, 160, 380, 380, 34), fill((14, 12, 40), 210))
        fn(c, x, 320)
        text(c, label, x, 500, 22, WHITE, 240, 800, spacing=2)
        c.restore()
    text(c, "BOLD AND CONTROVERSIAL", 960, 640, 30, MARIGOLD, 255 * smooth(prog(t, CON_HEAD, CON_HEAD + 0.4)), 800, spacing=6)
    for i, (label, fn) in enumerate([("2016 · CASH NOTES CANCELLED", _ic_note), ("2019 · J&K SPECIAL STATUS ENDED", _ic_pin)]):
        g = pop(t, CON_T[i], 0.45)
        if g <= 0:
            continue
        x = 640 + i * 640
        c.save()
        c.translate(x, 840)
        c.scale(g, g)
        c.translate(-x, -840)
        c.drawRRect(rrect(x - 270, 690, 540, 300, 34), fill((14, 12, 40), 210))
        fn(c, x, 800)
        text(c, label, x, 950, 22, WHITE, 240, 800, spacing=2)
        c.restore()


VIEWS = [("SUPPORTERS SAY", ["MORE CONFIDENT INDIA", "MODERNISING FAST", "MORE RESPECTED ABROAD"]),
         ("CRITICS SAY", ["RISING RELIGIOUS TENSIONS", "PRESSURE ON PRESS & OPPOSITION", "NOT ENOUGH JOBS FOR YOUTH"])]


def views(c, t):
    """Both panels slide in together and look identical; each one's points reveal while it is narrated."""
    bg(c, t=t)
    slide = out_cubic(prog(t, S5[1], S5[1] + 0.7))
    for i, (head, points) in enumerate(VIEWS):
        x = 500 + i * 920 + (1 - slide) * (-700 if i == 0 else 700)
        c.drawRRect(rrect(x - 400, 150, 800, 780, 40), fill((14, 12, 40), 220))
        c.drawRRect(rrect(x - 400, 150, 800, 780, 40), stroke(MARBLE, 3, 120))
        text(c, head, x, 250, 44, MARBLE, 255, 800, spacing=6)
        t0 = COL_T[i]
        for k, ptxt in enumerate(points):
            g = smooth(prog(t, t0 + 0.6 + k * 0.9, t0 + 1.0 + k * 0.9))
            y = 420 + k * 170
            c.drawCircle(x - 320, y - 14, 18 * g, fill(MARBLE))
            text(c, ptxt, x - 280, y, 30, WHITE, 240 * g, 800, "left", spacing=2)


def election(c, t):
    bg(c, t=t)
    k = smooth(prog(t, SEATS_T, SEATS_T + 2.5))
    a = smooth(prog(t, ALLY_T, ALLY_T + 1.2))
    hemicycle(c, 960, 800, 620, [(240, SAFFRON), (53, mix((140, 140, 170), lighten(SAFFRON, 0.45), a)), (250, (140, 140, 170))], k)
    c.drawLine(960, 140, 960, 820, stroke(WHITE, 4, 200 * smooth(prog(t, S6[1], S6[1] + 0.5))))
    text(c, "MAJORITY: 272", 960, 120, 30, WHITE, 255 * smooth(prog(t, S6[1], S6[1] + 0.5)), 800, spacing=4)
    text(c, "BJP 240", 560, 900, 38, SAFFRON, 255 * k, 800, spacing=3)
    text(c, "+ ALLIES = NDA 293", 960, 900, 34, lighten(SAFFRON, 0.45), 255 * a, 800, spacing=3)
    text(c, "OTHER PARTIES 250", 1400, 900, 34, (170, 170, 200), 255 * k, 800, spacing=3)
    caption(c, "2024 ELECTION  ·  THIRD TERM, COALITION GOVERNMENT", 960, 1020, WHITE, 26, 255 * a)


def draw_frame(c, t):
    c.clear(col(INDIGO))
    scenes(c, t, [((0.0, 0.01), S1[1], title), (S1, S2[1], economy), (S2, S3[1], upi_moon), (S3, S4[1], modi),
                  (S4, S5[1], policies), (S5, S6[1], views), (S6, DURATION + 1, election)])
    vignette(c)
    chapter_fade(c, t, DURATION, 0.3)


def sfx_events():
    ev = [(0.2, "shimmer", 0.6), (0.6, "pop", 0.6), (S1[0], "whoosh", 0.6), (S1[1] + 0.3, "riser", 0.5), (JAPAN_T, "chime", 0.6),
          (S2[0], "whoosh", 0.6), (UPI_T, "pop", 0.6), (UPI_T + 0.5, "ticks", 0.5), (MOON_T, "whoosh_long", 0.6), (MOON_T + 2.5, "boom", 0.4),
          (S3[0], "whoosh", 0.6), (S3[1], "pop", 0.6)]
    ev += [(x, "blip", 0.4) for x in STEP_T]
    ev += [(S4[0], "whoosh", 0.6)] + [(x, "pop", 0.5) for x in POL_T] + [(x, "pop", 0.5) for x in CON_T]
    ev += [(S5[0], "whoosh", 0.6), (S5[1], "slide", 0.5)]
    ev += [(COL_T[i] + 0.6 + k * 0.9, "blip", 0.3) for i in range(2) for k in range(3)]   # identical sounds for both sides
    ev += [(S6[0], "whoosh", 0.6), (SEATS_T, "ticks", 0.4), (ALLY_T, "chime", 0.5)]
    return ev


MUSIC = dict(
    chords=[(0.0, 50, (0, 7, 12, 14, 19)), (14.5, 55, (0, 7, 12, 16, 19)), (32.3, 48, (0, 7, 12, 16, 19)),
            (53.9, 50, (0, 7, 12, 14, 17)), (79.5, 45, (0, 7, 12, 14, 19)), (93.7, 48, (0, 7, 12, 16, 19))],
    plucks=[(2.2, 79.4), (94.0, DURATION)], bpm=96, rises=[(S1[1] + 0.3, S1[1] + 3.0)], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
