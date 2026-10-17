"""Storyboard key frames for every part. Each panel is a draw function f(c, t) plus notes.

These same scene drawings become the animated video once the storyboard is approved.
"""
import math

from faces import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

MAP = (560, 560, 26)   # India map placement used across scenes: cx, cy, pixels per degree


def bg(c, top=INDIGO, bottom=ROYAL, t=0.0, dust=True):
    background(c, top, bottom)
    if dust:
        Dust(50, 4, MARIGOLD).draw(c, t, 0.6)


# ================================================================ PART 1: HOOK
def p1a(c, t):
    bg(c, t=t)
    draw_india(c, *MAP)
    for i in range(6):
        person(c, 1150 + i * 120, 760, 240, i + 3, t)
    glow(c, 1150 + 2 * 120, 600, 160, SAFFRON, 160)
    person(c, 1150 + 2 * 120, 760, 240, 5, t)
    c.drawRRect(rrect(1150 + 2 * 120 - 70, 470, 140, 300, 40), stroke(SAFFRON, 6))
    text(c, "1 IN 6 HUMANS", 1450, 880, 56, SAFFRON, 255, 800, spacing=6)


def p1b(c, t):
    bg(c, t=t)
    draw_india(c, 960, 560, 22, glow_a=80)
    words = [("नमस्ते", "deva"), ("নমস্কার", "beng"), ("வணக்கம்", "taml"), ("నమస్తే", "telu"), ("ਸਤ ਸ੍ਰੀ ਅਕਾਲ", "guru"), ("آداب", "arab")]
    for i, (w, sc) in enumerate(words):
        ang = -math.pi / 2 + i * math.pi / 3 + 0.3
        indic_text(c, w, 960 + 640 * math.cos(ang), 560 + 400 * math.sin(ang) + 16, 52, sc, WHITE, 240)
    for i, fn in enumerate(RELIGIONS):
        ang = i * math.pi / 3
        x, y = 960 + 330 * math.cos(ang), 560 + 300 * math.sin(ang)
        c.drawCircle(x, y, 52, fill((14, 12, 40), 200))
        fn(c, x, y, 34, MARIGOLD)
    c.drawRRect(rrect(1560, 760, 200, 170, 20), fill(WHITE))
    c.drawRect(skia.Rect.MakeXYWH(1600, 760, 120, 14), fill(INK))
    ink_finger(c, 1660, 700, 110)
    text(c, "LARGEST ELECTIONS ON EARTH", 1660, 1000, 26, WHITE, 230, 800, spacing=3)


def p1c(c, t):
    bg(c, (40, 22, 40), (90, 40, 50), t=t, dust=False)
    split = skia.Path()
    split.moveTo(1060, 0)
    split.lineTo(W, 0)
    split.lineTo(W, H)
    split.lineTo(860, H)
    split.close()
    for i in range(7):  # ancient brick city (left)
        for j in range(5):
            x, y = 120 + i * 120, 330 + j * 120
            c.drawRRect(rrect(x, y, 96, 96, 8), fill(mix(TERRACOTTA, TURMERIC, ((i + j) % 3) / 4)))
            c.drawRect(skia.Rect.MakeXYWH(x + 30, y + 30, 36, 36), fill(darken(TERRACOTTA, 0.3)))
    c.drawLine(80, 920, 920, 920, stroke(CYAN, 8, 180))
    text(c, "c. 2600 BCE", 500, 220, 44, MARIGOLD, 255, 800, spacing=4)
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
    lander(c, 1420, 790, 160)
    text(c, "2023", 1460, 430, 44, MARIGOLD, 255, 800, spacing=4)
    c.restore()
    c.drawLine(1060, 0, 860, H, stroke(WHITE, 6, 220))


def p1d(c, t):
    bg(c, t=t)
    draw_india(c, *MAP, glow_a=140)
    indic_text(c, "भारत", 1380, 470, 170, "deva", SAFFRON)
    text(c, "INDIA", 1380, 620, 120, WHITE, 255, 800, spacing=20)
    bird(c, 1250, 960, 80, t, look=(-1, -0.5))
    bubble_q(c, 1110, 760, 1.0)


# ================================================================ PART 2: ANCIENT INDIA
def p2a(c, t):
    bg(c, (50, 30, 30), (110, 60, 40), t=t, dust=False)
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), fill(mix(TERRACOTTA, (90, 50, 40), 0.6)))
    for i in range(12):
        for j in range(6):
            if (i, j) in ((5, 2), (6, 2), (5, 3), (6, 3)):
                continue
            x, y = 70 + i * 150, 120 + j * 150
            c.drawRRect(rrect(x, y, 120, 120, 10), fill(mix(TERRACOTTA, TURMERIC, ((i * 7 + j) % 5) / 8)))
            c.drawRRect(rrect(x + 20, y + 20, 80, 80, 6), fill(darken(TERRACOTTA, 0.25)))
    for j in range(7):  # streets with covered drains
        c.drawLine(40, 105 + j * 150, W - 40, 105 + j * 150, stroke(CYAN, 5, 160))
    c.drawRRect(rrect(820, 420, 270, 270, 16), fill(darken(TERRACOTTA, 0.3)))
    c.drawRRect(rrect(850, 450, 210, 210, 10), shaded(linear((0, 450), (0, 660), [CYAN, OCEAN])))
    pill_tag(c, 955, 380, "GREAT BATH", MARIGOLD, 1.0, 24)
    caption(c, "INDUS VALLEY CIVILISATION  ·  c. 2600–1900 BCE", 960, 1030, MARIGOLD, 30)


def p2b(c, t):
    bg(c, (40, 24, 50), (80, 40, 60), t=t)
    c.drawRRect(rrect(460, 640, 1000, 170, 30), fill((210, 170, 110)))
    for k in range(4):
        c.drawLine(520, 690 + k * 32, 1400, 690 + k * 32, stroke((150, 110, 70), 6))
    glow(c, 960, 720, 500, MARIGOLD, 90)
    indic_text(c, "ऋग्वेद", 960, 600, 70, "deva", MARIGOLD)
    for i, (fn, label) in enumerate([(sym_om, "HINDUISM"), (sym_dharma, "BUDDHISM"), (sym_jain_hand, "JAINISM")]):
        x = 560 + i * 400
        c.drawCircle(x, 300, 90, fill((14, 12, 40), 210))
        glow(c, x, 300, 150, SAFFRON, 90)
        fn(c, x, 300, 56, SAFFRON)
        text(c, label, x, 450, 30, WHITE, 240, 800, spacing=4)


def p2c(c, t):
    bg(c, (60, 30, 40), (120, 60, 50), t=t)
    leader_card(c, 520, 520, "ashoka", t, 1.25)
    c.drawRect(skia.Rect.MakeXYWH(0, 940, W, 140), fill((90, 60, 50)))
    ashoka_pillar(c, 1350, 950, 820)
    caption(c, "AFTER THE KALINGA WAR: MESSAGES OF TOLERANCE IN STONE", 960, 1035, MARIGOLD, 26)


def p2d(c, t):
    bg(c, t=t)
    glow(c, 960, 520, 520, TURMERIC, 80)
    lion_capital(c, 960, 800, 360)
    indic_text(c, "सत्यमेव जयते", 960, 900, 64, "deva", WHITE)
    caption(c, "STILL INDIA'S NATIONAL EMBLEM", 960, 1010, MARIGOLD, 30)


def p2e(c, t):
    bg(c, t=t)
    draw_globe(c, 1200, 560, 330, -t * 5)
    for i, d in enumerate("1234567890"):
        ang = -math.pi * 0.9 + i * math.pi * 0.2
        x, y = 1200 + 470 * math.cos(ang), 560 + 400 * math.sin(ang)
        text(c, d, x, y + 30, 90, MARIGOLD if d != "0" else SAFFRON, 255, 800)
    glow(c, 400, 520, 260, SAFFRON, 140)
    indic_text(c, "०", 400, 600, 300, "deva", SAFFRON)
    text(c, "ZERO", 400, 760, 50, WHITE, 255, 800, spacing=10)
    caption(c, "THE DECIMAL SYSTEM THE WHOLE WORLD USES", 960, 1030, WHITE, 28)


# ================================================================ PART 3: EMPIRES, COLONIAL RULE, FREEDOM
def p3a(c, t):
    bg(c, (20, 30, 70), (40, 80, 130), t=t, dust=False)
    c.drawRect(skia.Rect.MakeXYWH(0, 640, W, H), shaded(linear((0, 640), (0, H), [CYAN, OCEAN])))
    for i, x in enumerate((240, 560, 860)):
        ship(c, x, 700, 90, t + i, sail=(240, 230, 210))
    glow(c, 1450, 520, 400, MARBLE, 70)
    taj_mahal(c, 1450, 640, 260)
    caption(c, "MUGHAL EMPIRE  ·  FROM 1526", 1450, 1000, MARBLE, 30)
    caption(c, "SPICES · COTTON · DIAMONDS", 520, 1000, MARIGOLD, 30)


def p3b(c, t):
    bg(c, (30, 30, 50), (70, 60, 90), t=t)
    draw_india(c, 640, 560, 24, rgb=(200, 60, 60), glow_a=60)
    c.drawRRect(rrect(1150, 300, 520, 360, 20), fill((120, 40, 40)))
    c.drawRRect(rrect(1170, 320, 480, 320, 14), fill(MARBLE))
    text(c, "EAST INDIA", 1410, 430, 46, (120, 40, 40), 255, 800, spacing=4)
    text(c, "COMPANY", 1410, 490, 46, (120, 40, 40), 255, 800, spacing=4)
    text(c, "LEDGER", 1410, 560, 26, (150, 120, 110), 255, 800, spacing=8)
    for k, (yr, label) in enumerate([("1757", "PLASSEY"), ("1857", "UPRISING"), ("1858", "CROWN RULE")]):
        pill_tag(c, 1230 + k * 180, 780, yr, MARIGOLD, 1.0, 26)
        text(c, label, 1230 + k * 180, 860, 22, WHITE, 230, 800, spacing=2)


def p3c(c, t):
    bg(c, (34, 34, 48), (64, 62, 80), t=t, dust=False)
    c.drawLine(0, 452, W, 452, stroke((120, 110, 140), 6))
    train(c, 1150, 450, 170)
    # the scale: wealth tipping out
    c.drawPath(poly([(1500, 560), (1460, 700), (1540, 700)]), fill(WHITE, 200))
    c.save()
    c.translate(1500, 560)
    c.rotate(14)
    c.drawLine(-260, 0, 260, 0, stroke(WHITE, 10, 220))
    c.drawPath(poly([(-300, 0), (-220, 0), (-240, 50), (-280, 50)]), fill(WHITE, 200))
    c.drawPath(poly([(220, 0), (300, 0), (280, 50), (240, 50)]), fill(WHITE, 200))
    c.restore()
    for k in range(7):
        c.drawCircle(1770 + (k % 2) * 14, 650 + k * 30, 14, fill(TURMERIC))
    text(c, "\"DRAIN OF WEALTH\" (DADABHAI NAOROJI)", 1500, 790, 24, MARBLE, 230, 800, spacing=2)
    c.drawRect(skia.Rect.MakeXYWH(0, 850, W, 230), fill(SOMBRE, 240))
    for k in range(6):
        person(c, 200 + k * 140, 1040, 130, k + 60, t, 150)
    c.drawPath(poly([(1050, 970), (1190, 970), (1170, 1020), (1070, 1020)]), fill((70, 66, 84)))
    text(c, "DEVASTATING FAMINES · e.g. BENGAL 1943", 1500, 990, 28, MARBLE, 230, 800, spacing=2)


def p3d(c, t):
    bg(c, (60, 40, 30), (150, 80, 40), t=t)
    glow(c, 960, 500, 600, SAFFRON, 90)
    leader_card(c, 960, 520, "gandhi", t, 1.3, phase=0.2)
    for (x, y, who, ph) in ((330, 320, "nehru", 1.0), (330, 770, "patel", 2.0), (1590, 540, "bose", 3.0)):
        leader_card(c, x, y, who, t, 0.78, phase=ph)


def p3e(c, t):
    bg(c, (70, 40, 40), (200, 110, 60), t=t, dust=False)
    c.drawRect(skia.Rect.MakeXYWH(0, 760, W, H), fill((170, 120, 80)))
    c.drawRect(skia.Rect.MakeXYWH(1500, 720, 420, 400), shaded(linear((0, 720), (0, H), [CYAN, OCEAN])))
    for k in range(10):
        cube(c, 1440 + (k % 5) * 18, 770 - (k // 5) * 16, 8, 0.5 + k, 0.4, MARBLE, 255, 200, 0)
    gandhi_walking(c, 1120, 860, 420, t)
    for k in range(9):
        person(c, 930 - k * 90, 850 + (k % 2) * 12, 170, k + 10, t + k * 0.2)
    bird(c, 1330, 862, 40, t, look=(1, 0))
    caption(c, "SALT MARCH  ·  1930  ·  ~385 KM", 960, 1030, WHITE, 30)


def p3f(c, t):
    bg(c, (20, 20, 50), (60, 40, 90), t=t)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(0, 0, W / 2, H))
    for k in range(7):
        x, y = 160 + k * 120, 220 + (k % 3) * 80
        for j in range(10):
            a = j / 10 * 6.28
            c.drawLine(x, y, x + 50 * math.cos(a), y + 50 * math.sin(a), stroke([SAFFRON, WHITE, GREEN][k % 3], 4))
    _flag(c, 480, 620, 360)
    text(c, "15 AUGUST 1947", 480, 960, 46, WHITE, 255, 800, spacing=4)
    c.restore()
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(W / 2, 0, W / 2, H))
    c.drawPaint(fill(SOMBRE))
    for k in range(14):
        person(c, 1060 + (k % 7) * 120, 560 + (k // 7) * 200, 150, k + 20, t, 200)
    for sgn in (-1, 1):
        c.drawPath(poly([(1440 + sgn * 300, 900), (1440 + sgn * 420, 900), (1440 + sgn * 420, 880), (1440 + sgn * 470, 910), (1440 + sgn * 420, 940), (1440 + sgn * 420, 920), (1440 + sgn * 300, 920)]), fill(MARBLE, 160))
    text(c, "PARTITION", 1440, 300, 54, MARBLE, 255, 800, spacing=10)
    text(c, "10+ MILLION UPROOTED", 1440, 370, 28, MARBLE, 220, 800, spacing=3)
    c.restore()
    c.drawLine(W / 2, 0, W / 2, H, stroke(WHITE, 5, 200))


def _flag(c, x, y, w):
    h = w * 2 / 3
    c.drawLine(x - w * 0.55, y - h * 0.5, x - w * 0.55, y + h * 1.2, stroke((200, 200, 210), 10))
    for k, rgb in enumerate((SAFFRON, WHITE, FLAG_GREEN)):
        c.drawRect(skia.Rect.MakeXYWH(x - w * 0.5, y - h * 0.5 + k * h / 3, w, h / 3), fill(rgb))
    chakra(c, x, y, h / 6 * 0.9, 0, CHAKRA)


# ================================================================ PART 4: BUILDING A REPUBLIC
def p4a(c, t):
    bg(c, t=t)
    leader_card(c, 330, 500, "ambedkar", t, 1.1)
    book(c, 1150, 430, 300, 1.0, "THE CONSTITUTION OF INDIA")
    for i in range(10):
        person(c, 760 + i * 85, 980, 150, i + 30, t)
        ink_finger(c, 760 + i * 85 + 40, 800, 26)
    caption(c, "26 JANUARY 1950  ·  EVERY ADULT CAN VOTE", 1150, 1040, MARIGOLD, 26)


def p4b(c, t):
    bg(c, (20, 30, 60), (40, 70, 110), t=t)
    leader_card(c, 330, 500, "nehru", t, 1.1)
    c.drawRect(skia.Rect.MakeXYWH(640, 820, 1280, 260), fill((60, 70, 90)))
    c.drawPath(poly([(700, 820), (760, 440), (1020, 440), (1080, 820)]), fill((180, 180, 190)))
    c.drawRect(skia.Rect.MakeXYWH(700, 820, 380, 60), shaded(linear((0, 820), (0, 880), [CYAN, OCEAN])))
    for k in range(3):
        c.drawRect(skia.Rect.MakeXYWH(1200 + k * 90, 480 - k * 40, 50, 340 + k * 40), fill((120, 110, 130)))
        c.drawCircle(1225 + k * 90, 430 - k * 40, 40, fill((200, 200, 210), 160))
    c.drawPath(poly([(1500, 820), (1500, 560), (1700, 460), (1900, 560), (1900, 820)]), fill(MARBLE))
    for k in range(4):
        c.drawRect(skia.Rect.MakeXYWH(1530 + k * 90, 600, 40, 220), fill((200, 190, 180)))
    for i, lbl in enumerate(("DAMS", "STEEL", "UNIVERSITIES")):
        text(c, lbl, (890, 1335, 1700)[i], 960, 28, WHITE, 230, 800, spacing=4)


def p4c(c, t):
    bg(c, (60, 120, 200), (170, 210, 240), t=t, dust=False)
    c.drawRect(skia.Rect.MakeXYWH(0, 600, W, H), fill((120, 90, 50)))
    for k in range(40):
        x = 40 + k * 48
        for j in range(4):
            y = 640 + j * 110
            g = clamp((x - 700) / 500)
            c.drawLine(x, y + 90, x, y, stroke(mix((150, 120, 60), (220, 180, 60), g), 6))
            c.drawOval(skia.Rect.MakeXYWH(x - 8, y - 26, 16, 34), fill(mix((150, 120, 60), MARIGOLD, g)))
    person(c, 1700, 1020, 330, 6, t)
    caption(c, "GREEN REVOLUTION  ·  1960s–70s", 960, 140, WHITE, 30)
    text(c, "FOOD AID", 220, 560, 34, WHITE, 230, 800, spacing=4)
    text(c, "→  FEEDING ITSELF", 1200, 560, 34, WHITE, 230, 800, spacing=4)


def p4d(c, t):
    bg(c, t=t)
    for sgn in (-1, 1):  # gate posts
        c.drawRRect(rrect(560 + sgn * 170 - 30, 320, 60, 520, 10), fill((140, 130, 160)))
    c.drawPath(poly([(400, 500), (300, 360), (300, 840), (400, 760)]), fill((110, 100, 130)))
    c.drawPath(poly([(720, 500), (820, 360), (820, 840), (720, 760)]), fill((110, 100, 130)))
    text(c, "1991", 560, 260, 70, MARIGOLD, 255, 800, spacing=6)
    pts = [(900 + i * 50, 900 - (i ** 1.7) * 9) for i in range(11)]
    c.drawPath(poly(pts, False), stroke(GREEN, 12))
    draw_globe(c, 1580, 470, 170, -t * 6)
    for k in range(6):
        a = k / 6 * 6.28
        c.drawRRect(rrect(1580 + 270 * math.cos(a) - 46, 470 + 230 * math.sin(a) - 30, 92, 60, 8), fill((60, 60, 80)))
        c.drawRRect(rrect(1580 + 270 * math.cos(a) - 38, 470 + 230 * math.sin(a) - 24, 76, 46, 5), fill(PEACOCK))
    caption(c, "ECONOMY OPENS UP  ·  SOFTWARE GOES GLOBAL", 960, 1030, WHITE, 28)


# ================================================================ PART 5: CULTURE
def p5a(c, t):
    bg(c, t=t)
    petals(c, t)
    text(c, "22", 300, 600, 300, SAFFRON, 255, 800)
    text(c, "MAJOR LANGUAGES", 300, 700, 30, WHITE, 230, 800, spacing=4)
    words = [("भारत", "deva", "HINDI"), ("ভারত", "beng", "BENGALI"), ("இந்தியா", "taml", "TAMIL"),
             ("భారతదేశం", "telu", "TELUGU"), ("ਭਾਰਤ", "guru", "PUNJABI"), ("بھارت", "arab", "URDU")]
    for i, (w, sc, label) in enumerate(words):
        x, y = 820 + (i % 3) * 380, 380 + (i // 3) * 360
        c.drawRRect(rrect(x - 160, y - 140, 320, 260, 30), fill((14, 12, 40), 200))
        indic_text(c, w, x, y + 10, 70 if len(w) <= 5 else 48, sc, [SAFFRON, MARIGOLD, PEACOCK, RANI, GREEN, WHITE][i])
        text(c, label, x, y + 90, 22, WHITE, 200, 800, spacing=4)


def p5b(c, t):
    bg(c, (30, 16, 50), (90, 30, 80), t=t)
    petals(c, t)
    for i, fn in enumerate(RELIGIONS):
        x = 260 + i * 280
        c.drawCircle(x, 360, 100, fill((14, 12, 40), 200))
        fn(c, x, 360, 60, [SAFFRON, GREEN, WHITE, MARIGOLD, PEACOCK, RANI][i])
    for k in range(9):
        diya(c, 300 + k * 165, 800, 40, t + k)
    for k, rgb in enumerate((RANI, MARIGOLD, PEACOCK, GREEN)):
        c.drawCircle(200 + k * 500, 620, 90, blur(fill(rgb, 120), 40))
    caption(c, "DIWALI · HOLI · EID · CHRISTMAS · GURPURAB · BUDDHA PURNIMA", 960, 1000, WHITE, 26)


def p5c(c, t):
    bg(c, t=t)
    tiles = [("YOGA", PEACOCK), ("CHESS", MARIGOLD), ("CINEMA", RANI), ("CRICKET", GREEN)]
    for i, (label, rgb) in enumerate(tiles):
        x = 255 + i * 470
        c.drawRRect(rrect(x - 200, 220, 400, 560, 36), fill(mix(INDIGO, rgb, 0.25)))
        text(c, label, x, 740, 40, WHITE, 255, 800, spacing=6)
        cx, cy = x, 470
        if i == 0:  # seated meditation (padmasana)
            skin = (190, 135, 98)
            c.drawOval(skia.Rect.MakeXYWH(cx - 150, cy + 80, 300, 90), fill(WHITE))
            c.drawRRect(rrect(cx - 70, cy - 90, 140, 190, 50), fill(WHITE))
            for sx in (-1, 1):
                c.drawLine(cx + sx * 60, cy - 50, cx + sx * 120, cy + 70, stroke(skin, 26))
                c.drawCircle(cx + sx * 125, cy + 85, 18, fill(skin))
            c.drawCircle(cx, cy - 150, 56, fill(skin))
            c.drawPath(_dome_top(cx, cy - 165, 58, 44), fill((30, 22, 30)))
            glow(c, cx, cy - 40, 200, PEACOCK, 70)
        elif i == 1:  # knight piece on a board
            for a in range(4):
                for b in range(4):
                    c.drawRect(skia.Rect.MakeXYWH(cx - 160 + a * 80, cy + 20 + b * 40, 80, 40), fill(MARBLE if (a + b) % 2 else (120, 80, 50)))
            c.drawPath(poly([(cx - 50, cy + 10), (cx + 50, cy + 10), (cx + 40, cy - 80), (cx + 60, cy - 120), (cx, cy - 190), (cx - 60, cy - 140), (cx - 40, cy - 100), (cx + 5, cy - 110), (cx - 40, cy - 40)]), fill(INK))
        elif i == 2:  # film reel
            c.drawCircle(cx, cy - 40, 140, fill((40, 40, 50)))
            for k in range(6):
                a = k / 6 * 6.28
                c.drawCircle(cx + 80 * math.cos(a), cy - 40 + 80 * math.sin(a), 30, fill(mix(INDIGO, rgb, 0.25)))
            c.drawCircle(cx, cy - 40, 24, fill(rgb))
        else:  # bat, ball and the bird in a helmet
            c.drawRRect(rrect(cx - 30, cy - 200, 60, 300, 26), fill((230, 200, 140)))
            c.drawRRect(rrect(cx - 12, cy - 290, 24, 100, 10), fill((60, 50, 60)))
            c.drawCircle(cx + 110, cy + 60, 30, fill((200, 40, 40)))
    bird(c, 1880, 820, 46, t, look=(-1, 0))
    caption(c, "MORE FILMS THAN ANY OTHER COUNTRY", 960, 1000, RANI, 28)


def p5d(c, t):
    bg(c, (30, 60, 110), (40, 110, 160), t=t, dust=False)
    c.drawRect(skia.Rect.MakeXYWH(0, 560, W, H), shaded(linear((0, 560), (0, H), [CYAN, OCEAN])))
    c.drawPath(blob_path(100, 560, [220, 180, 260, 200, 240, 200], 0.2), fill((110, 150, 100)))
    text(c, "THE AMERICAS", 160, 300, 30, WHITE, 230, 800, spacing=4)
    ship(c, 900, 600, 120, t, sail=MARBLE)
    glow(c, 900, 380, 120, (230, 40, 40), 140)
    c.drawPath(_chilli(900, 380, 90), fill((220, 40, 40)))
    c.drawLine(820, 360, 790, 330, stroke((60, 150, 80), 10))
    pill_tag(c, 900, 270, "CHILLI", (230, 70, 70), 1.0, 24)
    draw_india(c, 1650, 560, 14, glow_a=60, neighbours=False)
    c.drawOval(skia.Rect.MakeXYWH(1500, 840, 300, 120), fill(TERRACOTTA))
    c.drawOval(skia.Rect.MakeXYWH(1520, 840, 260, 70), fill((230, 120, 40)))
    caption(c, "CHILLIES ARRIVED ~500 YEARS AGO", 960, 1030, WHITE, 28)


def _dome_top(x, y, w, h):
    p = skia.Path()
    p.moveTo(x - w, y + h * 0.3)
    p.cubicTo(x - w, y - h, x + w, y - h, x + w, y + h * 0.3)
    p.close()
    return p


def _chilli(x, y, s):
    p = skia.Path()
    p.moveTo(x - s, y - s * 0.2)
    p.cubicTo(x - s * 0.3, y - s * 0.5, x + s * 0.6, y - s * 0.1, x + s, y + s * 0.5)
    p.cubicTo(x + s * 0.4, y + s * 0.2, x - s * 0.4, y + s * 0.3, x - s, y - s * 0.2)
    return p


# ================================================================ PART 6: INDIA TODAY + NARENDRA MODI
def p6a(c, t):
    bg(c, t=t)
    bars(c, 260, 860, 1400, 560, [("USA", 30, (110, 120, 160)), ("CHINA", 20, (110, 120, 160)), ("GERMANY", 5.0, (110, 120, 160)),
                                  ("JAPAN", 4.4, (110, 120, 160)), ("INDIA", 4.3, SAFFRON)], 1.0, highlight=4)
    c.drawPath(poly([(1530, 800), (1380, 800), (1380, 780), (1330, 815), (1380, 850), (1380, 830), (1530, 830)]), fill(MARIGOLD))
    text(c, "4TH BY 2027 (PROJECTED)", 1420, 720, 26, MARIGOLD, 255, 800, spacing=2)
    caption(c, "NOMINAL GDP, APPROX. TRILLION US$  ·  IMF WORLD ECONOMIC OUTLOOK, OCT 2026", 960, 1010, WHITE, 24)


def p6b(c, t):
    bg(c, t=t)
    phone_qr(c, 520, 520, 300, t)
    text(c, "24 BILLION+", 520, 940, 54, GREEN, 255, 800, spacing=4)
    text(c, "UPI PAYMENTS / MONTH", 520, 990, 26, WHITE, 220, 800, spacing=4)
    c.drawRRect(rrect(1000, 160, 820, 760, 40), fill((10, 10, 30)))
    c.save()
    c.clipRRect(rrect(1000, 160, 820, 760, 40), doAntiAlias=True)
    Stars(80, 6).draw(c, t)
    c.drawPath(blob_path(1410, 1100, [520, 500, 540, 510, 530, 500], 0.1), fill((150, 150, 165)))
    lander(c, 1410, 660, 200)
    c.restore()
    text(c, "CHANDRAYAAN-3 · 2023", 1410, 990, 34, MARIGOLD, 255, 800, spacing=3)


def p6c(c, t):
    bg(c, t=t)
    leader_card(c, 430, 520, "modi", t, 1.35)
    steps = [("1950", "BORN IN VADNAGAR, GUJARAT"), ("RSS", "RISES THROUGH THE RSS"), ("2001–14", "CHIEF MINISTER OF GUJARAT"), ("2014–", "PRIME MINISTER OF INDIA")]
    c.drawLine(1000, 240, 1000, 840, stroke(WHITE, 6, 150))
    for i, (yr, label) in enumerate(steps):
        y = 260 + i * 190
        c.drawCircle(1000, y, 22, fill(MARIGOLD))
        text(c, yr, 1050, y - 6, 40, MARIGOLD, 255, 800, "left", spacing=2)
        text(c, label, 1050, y + 40, 26, WHITE, 230, 800, "left", spacing=2)


def p6d(c, t):
    bg(c, t=t)
    icons = [("GST · 2017", _ic_receipt), ("ROADS · RAIL · AIRPORTS", _ic_road), ("500M+ BANK ACCOUNTS", _ic_card), ("100M+ TOILETS", _ic_toilet)]
    for i, (label, fn) in enumerate(icons):
        x = 280 + i * 455
        c.drawRRect(rrect(x - 190, 160, 380, 380, 34), fill((14, 12, 40), 210))
        fn(c, x, 320)
        text(c, label, x, 500, 22, WHITE, 240, 800, spacing=2)
    text(c, "BOLD AND CONTROVERSIAL", 960, 640, 30, MARIGOLD, 255, 800, spacing=6)
    for i, (label, fn) in enumerate([("2016 · CASH NOTES CANCELLED", _ic_note), ("2019 · J&K SPECIAL STATUS ENDED", _ic_pin)]):
        x = 640 + i * 640
        c.drawRRect(rrect(x - 270, 690, 540, 300, 34), fill((14, 12, 40), 210))
        fn(c, x, 800)
        text(c, label, x, 950, 22, WHITE, 240, 800, spacing=2)


def _ic_receipt(c, x, y):
    c.drawRRect(rrect(x - 70, y - 100, 140, 200, 10), fill(MARBLE))
    for k in range(5):
        c.drawLine(x - 45, y - 60 + k * 30, x + 45, y - 60 + k * 30, stroke((150, 140, 130), 6))


def _ic_road(c, x, y):
    c.drawPath(poly([(x - 30, y - 100), (x + 30, y - 100), (x + 110, y + 100), (x - 110, y + 100)]), fill((70, 70, 90)))
    for k in range(4):
        c.drawLine(x, y - 80 + k * 50, x, y - 60 + k * 50, stroke(MARIGOLD, 8))


def _ic_card(c, x, y):
    c.drawRRect(rrect(x - 110, y - 70, 220, 140, 16), fill(PEACOCK))
    c.drawRect(skia.Rect.MakeXYWH(x - 110, y - 40, 220, 26), fill(INK))
    c.drawRRect(rrect(x - 80, y + 10, 50, 36, 6), fill(MARIGOLD))


def _ic_toilet(c, x, y):
    c.drawRRect(rrect(x - 50, y - 100, 100, 70, 10), fill(MARBLE))
    c.drawOval(skia.Rect.MakeXYWH(x - 80, y - 30, 160, 60), fill(MARBLE))
    c.drawPath(poly([(x - 60, y), (x + 60, y), (x + 30, y + 100), (x - 30, y + 100)]), fill(MARBLE))


def _ic_note(c, x, y):
    c.drawRRect(rrect(x - 130, y - 60, 260, 120, 12), fill((120, 150, 110)))
    text(c, "₹", x, y + 24, 70, (60, 90, 60), 255, 800)
    c.drawLine(x - 150, y - 80, x + 150, y + 80, stroke((230, 70, 70), 12))


def _ic_pin(c, x, y):
    p = skia.Path()
    p.moveTo(x, y + 90)
    p.cubicTo(x - 90, y - 10, x - 70, y - 110, x, y - 110)
    p.cubicTo(x + 70, y - 110, x + 90, y - 10, x, y + 90)
    c.drawPath(p, fill(RANI))
    c.drawCircle(x, y - 40, 30, fill(WHITE))


def p6e(c, t):
    bg(c, t=t)
    cols = [("SUPPORTERS SAY", ["MORE CONFIDENT INDIA", "MODERNISING FAST", "MORE RESPECTED ABROAD"]),
            ("CRITICS SAY", ["RISING RELIGIOUS TENSIONS", "PRESSURE ON PRESS & OPPOSITION", "NOT ENOUGH JOBS FOR YOUTH"])]
    for i, (head, points) in enumerate(cols):
        x = 500 + i * 920
        c.drawRRect(rrect(x - 400, 150, 800, 780, 40), fill((14, 12, 40), 220))
        c.drawRRect(rrect(x - 400, 150, 800, 780, 40), stroke(MARBLE, 3, 120))
        text(c, head, x, 250, 44, MARBLE, 255, 800, spacing=6)
        for k, ptxt in enumerate(points):
            y = 420 + k * 170
            c.drawCircle(x - 320, y - 14, 18, fill(MARBLE))
            text(c, ptxt, x - 280, y, 30, WHITE, 240, 800, "left", spacing=2)
    text(c, "SAME SIZE · SAME COLOUR · SAME TIME ON SCREEN", 960, 1010, 22, WHITE, 160, 800, spacing=4)


def p6f(c, t):
    bg(c, t=t)
    hemicycle(c, 960, 800, 620, [(240, SAFFRON), (53, lighten(SAFFRON, 0.45)), (250, (140, 140, 170))])
    c.drawLine(960, 140, 960, 820, stroke(WHITE, 4, 200))
    text(c, "MAJORITY: 272", 960, 120, 30, WHITE, 255, 800, spacing=4)
    text(c, "BJP 240", 560, 900, 38, SAFFRON, 255, 800, spacing=3)
    text(c, "+ ALLIES = NDA 293", 960, 900, 34, lighten(SAFFRON, 0.45), 255, 800, spacing=3)
    text(c, "OTHER PARTIES 250", 1400, 900, 34, (170, 170, 200), 255, 800, spacing=3)
    caption(c, "2024 ELECTION  ·  THIRD TERM, COALITION GOVERNMENT", 960, 1020, WHITE, 26)


# ================================================================ PART 7: CHALLENGES, FUTURE, OUTRO
def p7a(c, t):
    bg(c, t=t)
    tiles = [("JOBS FOR YOUNG PEOPLE", PEACOCK), ("WOMEN IN PAID WORK", RANI), ("AIR POLLUTION", (150, 140, 120)), ("HEAT & WATER", SAFFRON)]
    for i, (label, rgb) in enumerate(tiles):
        x = 255 + i * 470
        c.drawRRect(rrect(x - 200, 200, 400, 600, 36), fill(mix(INDIGO, rgb, 0.25)))
        text(c, label, x, 760, 24, WHITE, 255, 800, spacing=2)
        if i == 0:
            for k in range(5):
                person(c, x - 140 + k * 70, 640, 160, k + 40, t)
        elif i == 1:
            person(c, x, 640, 300, 1, t)
            c.drawRRect(rrect(x - 80, 540, 160, 100, 10), fill((200, 205, 220)))
            c.drawRRect(rrect(x - 70, 550, 140, 80, 6), fill(PEACOCK))
        elif i == 2:
            for k in range(5):
                c.drawRect(skia.Rect.MakeXYWH(x - 160 + k * 66, 640 - 80 - k * 30 % 90, 50, 80 + k * 30 % 90), fill((90, 85, 100)))
            c.drawRect(skia.Rect.MakeXYWH(x - 200, 300, 400, 340), fill((180, 170, 150), 150))
        else:
            c.drawCircle(x, 360, 80, fill(SAFFRON))
            for k in range(6):
                c.drawLine(x - 150 + k * 60, 520, x - 130 + k * 60, 640, stroke((90, 60, 40), 6))


def p7b(c, t):
    bg(c, t=t)
    pyramid(c, 620, 900, 780, 680)
    text(c, "HALF UNDER 30", 1400, 520, 80, MARIGOLD, 255, 800, spacing=6)
    text(c, "MEDIAN AGE ~28", 1400, 600, 34, WHITE, 230, 800, spacing=4)


def p7c(c, t):
    bg(c, t=t)
    c.drawLine(200, 560, 1720, 560, stroke(WHITE, 8, 200))
    for x, yr, lines in ((200, "1947", ["NEWLY INDEPENDENT", "POOR · DIVIDED"]), (1720, "TODAY", ["LARGEST DEMOCRACY", "TOP-5 ECONOMY"])):
        c.drawCircle(x, 560, 30, fill(SAFFRON))
        text(c, yr, x, 480, 60, SAFFRON, 255, 800, spacing=4)
        for k, ln in enumerate(lines):
            text(c, ln, x, 650 + k * 44, 28, WHITE, 230, 800, spacing=3)
    for k in range(5):
        person(c, 600 + k * 180, 520, 120 + k * 25, k + 50, t)


def p7d(c, t):
    bg(c, (20, 16, 50), (240, 140, 80), t=t, dust=False)
    glow(c, 960, 900, 600, MARIGOLD, 200)
    c.drawCircle(960, 900, 180, fill((255, 210, 120)))
    draw_india(c, 960, 620, 18, glow_a=60, neighbours=False, a=200)
    c.drawRect(skia.Rect.MakeXYWH(0, 900, W, 200), fill((40, 24, 50)))
    bird(c, 1500, 905, 70, t, look=(-1, -0.3))
    indic_text(c, "भारत", 960, 230, 110, "deva", WHITE)
    text(c, "INDIA", 960, 320, 50, WHITE, 230, 800, spacing=16)


PANELS = {
    1: ("HOOK", "0:00–0:35", [
        (p1a, "H1", "\"One in every six people alive today lives in India.\"", "Map glows; a row of six people appears and one lights up saffron."),
        (p1b, "H2", "\"...hundreds of languages... every major religion... the largest elections...\"", "Greetings in six scripts orbit the map; religious symbols pop in a ring; a voter's inked finger rises."),
        (p1c, "H3", "\"...some of the world's first cities... near the south pole of the Moon.\"", "Split screen: an Indus brick city on the left; Chandrayaan-3 lands on the Moon on the right."),
        (p1d, "H4", "\"So how did India become India? And where is it going next?\"", "\"Bharat / INDIA\" title (Devanagari + English); the bird looks at the map with a question."),
    ]),
    2: ("ANCIENT INDIA", "0:35–1:30", [
        (p2a, "A1", "\"...grid streets, brick houses and covered drains...\"", "Top-down Indus city builds brick by brick; water flows through the drains; the Great Bath fills."),
        (p2b, "A2", "\"...the Vedas... Buddhism and Jainism too.\"", "A palm-leaf manuscript glows; three symbols rise above it."),
        (p2c, "A3", "\"...the emperor Ashoka... messages of tolerance into stone pillars.\"", "Ashoka's card (artistic impression) blinks to life; a stone pillar rises with the lion capital."),
        (p2d, "A3", "\"The lions... are still India's national emblem today.\"", "Camera pushes into the lion capital; the motto \"Satyameva Jayate\" (Truth alone triumphs) appears in Devanagari."),
        (p2e, "A4", "\"...the decimal number system, with zero as a number...\"", "A glowing Devanagari zero; digits 1–0 fly out around a spinning globe."),
    ]),
    3: ("EMPIRES, COLONIAL RULE & FREEDOM", "1:30–2:40", [
        (p3a, "E1", "\"...spices, cotton and diamonds... the Taj Mahal.\"", "Trade ships bob on the sea; the Taj Mahal builds itself from marble blocks."),
        (p3b, "E2", "\"Then came a company...\"", "The East India Company ledger; the map slowly turns red; dates pop: 1757, 1857, 1858."),
        (p3c, "E3", "\"...railways... draining the country's wealth... devastating famines.\"", "A train crosses; a scale tips with gold pouring out; the bottom strip turns grey and quiet for the famines."),
        (p3d, "E4", "\"...Mohandas Gandhi... Nehru, Patel and Bose.\"", "Gandhi's card comes to life at centre; Nehru, Patel and Bose cards join around him."),
        (p3e, "E4", "\"In 1930, Gandhi walked nearly 400 km to the sea...\"", "Side view: Gandhi walks with his staff; the crowd (and the bird) follow; salt crystals at the shore."),
        (p3f, "E5", "\"...independent. But it was also divided...\"", "Left: fireworks and the tricolour. Right: muted Partition scene with people moving both ways; music drops to the drone."),
    ]),
    4: ("BUILDING A REPUBLIC", "2:40–3:30", [
        (p4a, "R1", "\"...a constitution... led by B. R. Ambedkar... every adult the right to vote...\"", "Ambedkar's card; the Constitution opens; a line of diverse voters raise inked fingers."),
        (p4b, "R2", "\"...Nehru... dams, steel plants and universities.\"", "Nehru's card; a dam fills, chimneys rise, a university building appears."),
        (p4c, "R3", "\"The Green Revolution...\"", "Fields sweep from brown to gold, left to right; a farmer stands proud."),
        (p4d, "R4", "\"...in 1991... opened up its economy...\"", "Gates swing open; the growth line climbs; laptops orbit a globe."),
    ]),
    5: ("CULTURE", "3:30–4:20", [
        (p5a, "C1", "\"...twenty-two major languages...\"", "A giant \"22\"; the word India/Bharat appears in six scripts, tile by tile."),
        (p5b, "C2", "\"Hinduism, Buddhism, Jainism and Sikhism... one of the largest Muslim populations...\"", "Six symbols light up; rows of diyas; colour bursts (Holi); marigold petals float."),
        (p5c, "C3", "\"Yoga... chess... cinema... cricket...\"", "Four tiles flip in on each word; the bird appears in a cricket helmet."),
        (p5d, "C4", "\"Chillies... arrived about five hundred years ago, from the Americas.\"", "A chilli sails across the ocean and lands in a bowl of curry."),
    ]),
    6: ("INDIA TODAY & NARENDRA MODI", "4:20–5:40", [
        (p6a, "T1", "\"...fifth-largest economy... on track to overtake Japan...\"", "Bars grow; India's saffron bar edges up beside Japan; source caption shown."),
        (p6b, "T2", "\"...UPI... twenty billion payments... the Moon's south pole.\"", "A phone scans a QR code and the counter ticks up; the lander touches down."),
        (p6c, "T3", "\"Since 2014... Narendra Modi...\"", "Modi's card comes to life (same style as all leaders); timeline dots light up one by one."),
        (p6d, "T4", "\"...goods and services tax... toilets... bold and controversial moves...\"", "Four policy tiles pop in; then two \"controversial\" tiles, stated as facts."),
        (p6e, "T5", "\"Supporters say... Critics worry...\"", "Two identical panels slide in together; three points each, same timing."),
        (p6f, "T6", "\"In 2024, he won a third term... governs in a coalition.\"", "Seats fill the hemicycle; BJP falls short of the 272 line; allies join to pass it."),
    ]),
    7: ("CHALLENGES, FUTURE & OUTRO", "5:40–6:20", [
        (p7a, "F1", "\"...good jobs... women in paid work... worst air... heat waves and water shortages.\"", "Four challenge tiles appear one per phrase."),
        (p7b, "F2", "\"Half of its people are under thirty.\"", "The population pyramid builds from its wide young base."),
        (p7c, "F3", "\"In a single lifetime...\"", "Timeline from 1947 to today; the figures grow taller along it."),
        (p7d, "F4", "\"What it becomes next will shape the lives of one in six humans...\"", "Sunrise over the map; the bird watches; \"Bharat / INDIA\" end card."),
    ]),
}
