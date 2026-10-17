"""Part 3: Empires, colonial rule and freedom. Trade + Mughals, the Company, the Raj, Gandhi, 1947 and Partition.

  python3 render.py part3 [--still 3,10,20]
"""
from boards import *  # noqa: F401,F403

PART = "part3"
VO = {"E1": 2.2, "E2": 15.2, "E3": 33.6, "E4": 43.2, "E5": 63.0}
DURATION = 82.5
TM = Timing(PART, VO)

S1 = (1.7, 2.3)
S2 = (14.7, 15.3)
S3 = (33.1, 33.7)
S4 = (42.7, 43.3)
SALT = (TM.word("E4", "in 1930") - 0.5, TM.word("E4", "in 1930"))
S6 = (62.5, 63.1)
TAJ_T = TM.word("E1", "taj mahal") - 0.8
MUGHAL_T = TM.word("E1", "mughal") - 0.2
YEARS = [TM.word("E2", "1757"), TM.word("E2", "uprising") - 0.4, TM.word("E2", "crown") - 0.2]
DRAIN_T = TM.word("E3", "draining") - 0.3
FAMINE_T = TM.word("E3", "famines") - 0.6
LEAD_T = [TM.word("E4", w) - 0.2 for w in ("nehru", "patel", "bose")]
DIVIDED_T = TM.word("E5", "divided") - 0.2


def title(c, t):
    bg(c, (60, 30, 30), (120, 60, 40), t=t, dust=False)
    rangoli(c, 960, 520, 300, out_cubic(prog(t, 0.0, 1.6)), t, (MARBLE, (200, 60, 60), TURMERIC, SAFFRON, WHITE))
    g = smooth(prog(t, 0.6, 1.1))
    c.drawCircle(960, 520, 110 * g, fill((40, 20, 20), 230))
    indic_text(c, "३", 960, 575, 150, "deva", MARIGOLD, 255 * g)
    text(c, "EMPIRES & FREEDOM", 960, 920, 80, WHITE, 255 * g, 800, spacing=10)


def trade(c, t):
    bg(c, (20, 30, 70), (40, 80, 130), t=t, dust=False)
    c.drawRect(skia.Rect.MakeXYWH(0, 640, W, H), shaded(linear((0, 640), (0, H), [CYAN, OCEAN])))
    for i, x in enumerate((240, 560, 860)):
        ship(c, (x + (t - S1[0]) * 20) % (W + 200) - 100 if x < 1100 else x, 700, 90, t + i, sail=(240, 230, 210))
    k = smooth(prog(t, TAJ_T, TAJ_T + 2.0))
    if k > 0:
        glow(c, 1450, 520, 400, MARBLE, 70 * k)
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(1000, 640 - 640 * k, 900, 640 * k + 10))
        taj_mahal(c, 1450, 640, 260)
        c.restore()
    caption(c, "SPICES · COTTON · DIAMONDS", 520, 1000, MARIGOLD, 30, 255 * smooth(prog(t, S1[1] + 0.5, S1[1] + 0.9)))
    caption(c, "MUGHAL EMPIRE  ·  FROM 1526", 1450, 1000, MARBLE, 30, 255 * smooth(prog(t, MUGHAL_T, MUGHAL_T + 0.4)))


def company(c, t):
    bg(c, (30, 30, 50), (70, 60, 90), t=t)
    red = smooth(prog(t, YEARS[0], YEARS[2] + 1.0))
    draw_india(c, 640, 560, 24, rgb=mix(SAFFRON, (200, 60, 60), red), glow_a=60)
    g = pop(t, S2[1] + 0.3, 0.5)
    if g > 0:
        c.save()
        c.translate(1410, 480)
        c.scale(g, g)
        c.translate(-1410, -480)
        c.drawRRect(rrect(1150, 300, 520, 360, 20), fill((120, 40, 40)))
        c.drawRRect(rrect(1170, 320, 480, 320, 14), fill(MARBLE))
        text(c, "EAST INDIA", 1410, 430, 46, (120, 40, 40), 255, 800, spacing=4)
        text(c, "COMPANY", 1410, 490, 46, (120, 40, 40), 255, 800, spacing=4)
        text(c, "LEDGER", 1410, 560, 26, (150, 120, 110), 255, 800, spacing=8)
        c.restore()
    for k, (yr, label) in enumerate([("1757", "PLASSEY"), ("1857", "UPRISING"), ("1858", "CROWN RULE")]):
        p = pop(t, YEARS[k], 0.4)
        pill_tag(c, 1230 + k * 180, 780, yr, MARIGOLD, p, 26)
        text(c, label, 1230 + k * 180, 860, 22, WHITE, 230 * min(1, p), 800, spacing=2)


def raj(c, t):
    bg(c, (34, 34, 48), (64, 62, 80), t=t, dust=False)
    c.drawLine(0, 452, W, 452, stroke((120, 110, 140), 6))
    train(c, lerp(-300, 1150, out_cubic(prog(t, S3[1], S3[1] + 2.5))), 450, 170)
    d = smooth(prog(t, DRAIN_T, DRAIN_T + 0.6))
    if d > 0:
        c.saveLayerAlpha(None, int(255 * d))
        c.drawPath(poly([(1500, 560), (1460, 700), (1540, 700)]), fill(WHITE, 200))
        c.save()
        c.translate(1500, 560)
        c.rotate(14 * smooth(prog(t, DRAIN_T + 0.3, DRAIN_T + 1.2)))
        c.drawLine(-260, 0, 260, 0, stroke(WHITE, 10, 220))
        c.drawPath(poly([(-300, 0), (-220, 0), (-240, 50), (-280, 50)]), fill(WHITE, 200))
        c.drawPath(poly([(220, 0), (300, 0), (280, 50), (240, 50)]), fill(WHITE, 200))
        c.restore()
        for k in range(7):
            ph = (t * 0.8 + k / 7) % 1
            c.drawCircle(1770 + (k % 2) * 14, 620 + 200 * ph, 14, fill(TURMERIC, 255 * (1 - ph)))
        text(c, "\"DRAIN OF WEALTH\" (DADABHAI NAOROJI)", 1500, 790, 24, MARBLE, 230, 800, spacing=2)
        c.restore()
    f = smooth(prog(t, FAMINE_T, FAMINE_T + 1.0))
    if f > 0:
        c.drawRect(skia.Rect.MakeXYWH(0, 850 + 230 * (1 - f), W, 230), fill(SOMBRE, 240))
        for k in range(6):
            person(c, 200 + k * 140, 1040 + 230 * (1 - f), 130, k + 60, t * 0.4, 150)
        text(c, "DEVASTATING FAMINES · e.g. BENGAL 1943", 1500, 990 + 230 * (1 - f), 28, MARBLE, 230, 800, spacing=2)


def leaders(c, t):
    bg(c, (60, 40, 30), (150, 80, 40), t=t)
    glow(c, 960, 500, 600, SAFFRON, 90)
    leader_card(c, 960, 520, "gandhi", t, 1.3 * out_back(prog(t, S4[1], S4[1] + 0.6)), phase=0.2)
    for i, (x, y, who) in enumerate(((330, 320, "nehru"), (330, 770, "patel"), (1590, 540, "bose"))):
        leader_card(c, x, y, who, t, 0.78 * out_back(prog(t, LEAD_T[i], LEAD_T[i] + 0.55)), look=(0.6 if x < 960 else -0.6, 0), phase=i + 1)


def salt_march(c, t):
    bg(c, (70, 40, 40), (200, 110, 60), t=t, dust=False)
    walk = (t - SALT[0]) * 28
    c.drawRect(skia.Rect.MakeXYWH(0, 760, W, H), fill((170, 120, 80)))
    sea_x = 2100 - walk * 0.9
    c.drawRect(skia.Rect.MakeXYWH(sea_x, 720, 1200, 400), shaded(linear((0, 720), (0, H), [CYAN, OCEAN])))
    for k in range(10):
        cube(c, sea_x - 60 + (k % 5) * 18, 770 - (k // 5) * 16, 8, 0.5 + k, 0.4, MARBLE, 255, 200, 0)
    for k in range(6):  # passing palms
        px = (k * 420 - walk * 0.5) % (W + 300) - 150
        c.drawLine(px, 760, px + 20, 560, stroke((110, 80, 60), 14))
        for a in range(5):
            ang = math.radians(200 + a * 35)
            c.drawLine(px + 20, 560, px + 20 + 90 * math.cos(ang), 560 + 50 * math.sin(ang), stroke((90, 150, 90), 14))
    gandhi_walking(c, 1120, 860, 420, t)
    for k in range(9):
        person(c, 930 - k * 90, 850 + (k % 2) * 12, 170, k + 10, t + k * 0.2)
    bird(c, 1330, 862 - abs(math.sin(t * 5)) * 8, 40, t, look=(1, 0))
    km = int(clamp((t - SALT[1]) / 10) * 385)
    caption(c, f"SALT MARCH  ·  1930  ·  {km} KM", 960, 1030, WHITE, 30, 255 * smooth(prog(t, SALT[1], SALT[1] + 0.4)))


def independence(c, t):
    split = smooth(prog(t, DIVIDED_T, DIVIDED_T + 1.0))
    bg(c, (20, 20, 50), (60, 40, 90), t=t)
    lw = lerp(W, W / 2, split)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(0, 0, lw, H))
    cx = lw / 2
    for k in range(7):
        ph = (t * 0.5 + k / 7) % 1
        x, y = cx - 360 + k * 120, 200 + (k % 3) * 80
        for j in range(10):
            a = j / 10 * 6.28
            c.drawLine(x, y, x + 60 * ph * math.cos(a), y + 60 * ph * math.sin(a), stroke([SAFFRON, WHITE, GREEN][k % 3], 4, 255 * (1 - ph)))
    _flag(c, cx, 620, 360)
    text(c, "15 AUGUST 1947", cx, 960, 46, WHITE, 255, 800, spacing=4)
    c.restore()
    if split > 0:
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(lw, 0, W - lw, H))
        c.drawPaint(fill(SOMBRE))
        for k in range(14):
            d = 1 if k % 2 else -1
            x = 1060 + (k % 7) * 120 + d * 30 * (t - DIVIDED_T)
            person(c, x, 560 + (k // 7) * 200, 150, k + 20, t * 0.5, 200)
        for sgn in (-1, 1):
            c.drawPath(poly([(1440 + sgn * 300, 900), (1440 + sgn * 420, 900), (1440 + sgn * 420, 880), (1440 + sgn * 470, 910), (1440 + sgn * 420, 940), (1440 + sgn * 420, 920), (1440 + sgn * 300, 920)]), fill(MARBLE, 160))
        text(c, "PARTITION", 1440, 300, 54, MARBLE, 255, 800, spacing=10)
        text(c, "10+ MILLION UPROOTED", 1440, 370, 28, MARBLE, 220, 800, spacing=3)
        text(c, "200,000 TO 2 MILLION DEATHS", 1440, 420, 24, MARBLE, 200 * smooth(prog(t, DIVIDED_T + 6, DIVIDED_T + 7)), 800, spacing=3)
        c.restore()
        c.drawLine(lw, 0, lw, H, stroke(WHITE, 5, 200))


def _flag(c, x, y, w):
    h = w * 2 / 3
    c.drawLine(x - w * 0.55, y - h * 0.5, x - w * 0.55, y + h * 1.2, stroke((200, 200, 210), 10))
    for k, rgb in enumerate((SAFFRON, WHITE, FLAG_GREEN)):
        c.drawRect(skia.Rect.MakeXYWH(x - w * 0.5, y - h * 0.5 + k * h / 3, w, h / 3), fill(rgb))
    chakra(c, x, y, h / 6 * 0.9, 0, CHAKRA)


def draw_frame(c, t):
    c.clear(col(INDIGO))
    scenes(c, t, [((0.0, 0.01), S1[1], title), (S1, S2[1], trade), (S2, S3[1], company), (S3, S4[1], raj),
                  (S4, SALT[1], leaders), (SALT, S6[1], salt_march), (S6, DURATION + 1, independence)])
    vignette(c)
    chapter_fade(c, t, DURATION, 0.3)


def sfx_events():
    ev = [(0.2, "shimmer", 0.6), (0.6, "pop", 0.6), (S1[0], "whoosh", 0.6), (TAJ_T, "shimmer", 0.6), (MUGHAL_T, "pop", 0.4),
          (S2[0], "whoosh", 0.6), (S2[1] + 0.3, "pop", 0.6)] + [(y, "pop", 0.5) for y in YEARS]
    ev += [(S3[0], "whoosh", 0.6), (S3[1], "rumble", 0.5), (DRAIN_T, "slide", 0.4), (DRAIN_T + 0.5, "tink", 0.4), (S4[0], "whoosh", 0.6), (S4[1], "pop", 0.6)]
    ev += [(x, "pop", 0.5) for x in LEAD_T]
    ev += [(SALT[0], "whoosh", 0.6), (S6[0], "whoosh", 0.6), (S6[1], "swell_soft", 0.8), (S6[1] + 0.4, "chime", 0.7), (S6[1] + 1.0, "chime", 0.5)]
    return ev


MUSIC = dict(
    chords=[(0.0, 50, (0, 7, 12, 14, 19)), (14.7, 46, (0, 7, 12, 15, 19)), (33.1, 45, (0, 7, 12, 15, 19)),
            (42.7, 50, (0, 7, 12, 16, 19)), (TM.word("E4", "in 1930") - 0.5, 48, (0, 7, 12, 16, 19)), (62.5, 50, (0, 7, 12, 16, 21)),
            (DIVIDED_T, 45, (0, 7, 12, 15))],
    plucks=[(2.2, 33.0), (42.8, DIVIDED_T)], bpm=96, rises=[(S6[0] - 2.0, S6[0])], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
