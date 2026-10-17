"""Props for the India video: monuments, symbols, vehicles, charts."""
import math

from india_kit import *  # noqa: F401,F403


# ---------------------------------------------------------------- symbols (religions, emblem)
def sym_om(c, x, y, s, rgb=WHITE, a=255):
    indic_text(c, "ॐ", x, y + s * 0.45, s * 1.5, "deva", rgb, a)


def sym_ik_onkar(c, x, y, s, rgb=WHITE, a=255):
    indic_text(c, "ੴ", x, y + s * 0.45, s * 1.4, "guru", rgb, a)


def sym_dharma(c, x, y, s, rgb=WHITE, a=255):
    c.drawCircle(x, y, s * 0.8, stroke(rgb, s * 0.14, a))
    c.drawCircle(x, y, s * 0.2, fill(rgb, a))
    for k in range(8):
        ang = math.radians(k * 45)
        c.drawLine(x, y, x + s * 0.8 * math.cos(ang), y + s * 0.8 * math.sin(ang), stroke(rgb, s * 0.1, a))
        c.drawCircle(x + s * 0.98 * math.cos(ang), y + s * 0.98 * math.sin(ang), s * 0.1, fill(rgb, a))


def sym_crescent(c, x, y, s, rgb=WHITE, a=255):
    m = circle_path(x, y, s * 0.8)
    cut = circle_path(x + s * 0.32, y - s * 0.1, s * 0.66)
    c.drawPath(skia.Op(m, cut, skia.PathOp.kDifference_PathOp), fill(rgb, a))
    star = [(x + s * 0.55 + s * 0.28 * math.cos(math.radians(-90 + k * 36)) * (1 if k % 2 == 0 else 0.45),
             y - s * 0.05 + s * 0.28 * math.sin(math.radians(-90 + k * 36)) * (1 if k % 2 == 0 else 0.45)) for k in range(10)]
    c.drawPath(poly(star), fill(rgb, a))


def sym_cross(c, x, y, s, rgb=WHITE, a=255):
    c.drawRRect(rrect(x - s * 0.12, y - s * 0.85, s * 0.24, s * 1.7, s * 0.06), fill(rgb, a))
    c.drawRRect(rrect(x - s * 0.55, y - s * 0.45, s * 1.1, s * 0.24, s * 0.06), fill(rgb, a))


def sym_jain_hand(c, x, y, s, rgb=WHITE, a=255):
    c.drawRRect(rrect(x - s * 0.5, y - s * 0.2, s * 1.0, s * 0.9, s * 0.35), fill(rgb, a))
    for k in range(4):
        c.drawRRect(rrect(x - s * 0.48 + k * s * 0.25, y - s * 0.85 + (abs(k - 1.5) * s * 0.1), s * 0.2, s * 0.8, s * 0.1), fill(rgb, a))
    c.drawRRect(rrect(x + s * 0.42, y - s * 0.1, s * 0.4, s * 0.2, s * 0.1), fill(rgb, a))
    sym_dharma(c, x, y + s * 0.25, s * 0.25, INDIGO, a)


RELIGIONS = [sym_om, sym_crescent, sym_cross, sym_ik_onkar, sym_dharma, sym_jain_hand]


def lion_capital(c, x, y, s, rgb=(214, 196, 160), a=255):
    """Ashoka's lion capital (simplified): abacus with wheel, three visible lions back to back. (x, y) = base centre."""
    dark = darken(rgb, 0.25)
    c.drawPath(poly([(x - s * 0.7, y), (x + s * 0.7, y), (x + s * 0.5, y - s * 0.35), (x - s * 0.5, y - s * 0.35)]), fill(dark, a))  # bell
    c.drawRect(skia.Rect.MakeXYWH(x - s * 0.8, y - s * 0.62, s * 1.6, s * 0.28), fill(rgb, a))  # abacus
    chakra(c, x, y - s * 0.48, s * 0.12, 0, darken(rgb, 0.45), a)
    for k, (dx, face) in enumerate(((-0.42, -1), (0.42, 1), (0, 0))):  # lions
        lx, ly = x + dx * s, y - s * 0.62
        c.drawRRect(rrect(lx - s * 0.22, ly - s * 0.55, s * 0.44, s * 0.55, s * 0.12), fill(rgb if k < 2 else lighten(rgb, 0.08), a))
        c.drawCircle(lx + face * s * 0.08, ly - s * 0.68, s * 0.24, fill(lighten(rgb, 0.05), a))   # mane
        c.drawCircle(lx + face * s * 0.12, ly - s * 0.66, s * 0.13, fill(dark, a))                # face
        if face == 0:
            c.drawCircle(lx, ly - s * 0.68, s * 0.27, fill(lighten(rgb, 0.1), a))
            c.drawCircle(lx, ly - s * 0.66, s * 0.14, fill(dark, a))


def ashoka_pillar(c, x, base, h, a=255):
    rgb = (214, 196, 160)
    c.drawRect(skia.Rect.MakeXYWH(x - h * 0.035, base - h * 0.8, h * 0.07, h * 0.8), shaded(linear((x - h * 0.035, 0), (x + h * 0.035, 0), [lighten(rgb, 0.15), darken(rgb, 0.2)])))
    for k in range(4):
        c.drawLine(x - h * 0.03, base - h * (0.2 + k * 0.12), x + h * 0.03, base - h * (0.2 + k * 0.12), stroke(darken(rgb, 0.3), 2, 120))
    lion_capital(c, x, base - h * 0.8, h * 0.13, rgb, a)


def taj_mahal(c, x, base, s, a=255):
    m, sh = MARBLE, darken(MARBLE, 0.12)
    c.drawRect(skia.Rect.MakeXYWH(x - s * 1.6, base - s * 0.12, s * 3.2, s * 0.12), fill(sh, a))
    for sx in (-1, 1):  # minarets
        mx = x + sx * s * 1.45
        c.drawRect(skia.Rect.MakeXYWH(mx - s * 0.06, base - s * 1.3, s * 0.12, s * 1.2), fill(m, a))
        c.drawPath(_onion(mx, base - s * 1.3, s * 0.1, s * 0.16), fill(m, a))
    c.drawRect(skia.Rect.MakeXYWH(x - s * 0.95, base - s * 0.9, s * 1.9, s * 0.8), fill(m, a))
    c.drawRRect(rrect(x - s * 0.22, base - s * 0.8, s * 0.44, s * 0.68, s * 0.22), fill(sh, a))
    for sx in (-1, 1):
        c.drawRRect(rrect(x + sx * s * 0.6 - s * 0.12, base - s * 0.7, s * 0.24, s * 0.42, s * 0.12), fill(sh, a))
        c.drawPath(_onion(x + sx * s * 0.72, base - s * 0.9, s * 0.14, s * 0.22), fill(m, a))
    c.drawPath(_onion(x, base - s * 0.9, s * 0.48, s * 0.75), fill(m, a))
    c.drawLine(x, base - s * 1.65, x, base - s * 1.85, stroke(TURMERIC, s * 0.03, a))


def _onion(x, y, w, h):
    p = skia.Path()
    p.moveTo(x - w, y)
    p.cubicTo(x - w * 1.25, y - h * 0.55, x - w * 0.2, y - h * 0.7, x, y - h)
    p.cubicTo(x + w * 0.2, y - h * 0.7, x + w * 1.25, y - h * 0.55, x + w, y)
    p.close()
    return p


def ship(c, x, y, s, t, sail=WHITE, cargo=True, a=255):
    c.save()
    c.translate(x, y + bob(t, s * 0.04, 2.2))
    c.rotate(2 * math.sin(t * 1.3))
    c.drawPath(poly([(-s, -s * 0.1), (s, -s * 0.1), (s * 0.7, s * 0.3), (-s * 0.75, s * 0.3)]), fill((120, 80, 56), a))
    c.drawLine(0, -s * 0.1, 0, -s * 1.3, stroke((90, 60, 42), s * 0.06, a))
    c.drawPath(poly([(s * 0.05, -s * 1.25), (s * 0.75, -s * 0.35), (s * 0.05, -s * 0.3)]), fill(sail, a))
    c.drawPath(poly([(-s * 0.05, -s * 1.1), (-s * 0.6, -s * 0.35), (-s * 0.05, -s * 0.3)]), fill(darken(sail, 0.1), a))
    if cargo:
        for k, rgb in enumerate((SAFFRON, (180, 60, 40), TURMERIC)):
            c.drawCircle(-s * 0.5 + k * s * 0.3, -s * 0.18, s * 0.13, fill(rgb, a))
    c.restore()


def train(c, x, y, s, a=255):
    for k in range(4):
        cx = x - k * s * 1.25
        c.drawRRect(rrect(cx - s * 0.55, y - s * 0.7, s * 1.1, s * 0.6, s * 0.1), fill((150, 40, 40) if k else (40, 40, 50), a))
        for w in (-0.3, 0.3):
            c.drawCircle(cx + w * s, y - s * 0.08, s * 0.12, fill((30, 30, 36), a))
        if k:
            for wn in range(3):
                c.drawRect(skia.Rect.MakeXYWH(cx - s * 0.42 + wn * s * 0.32, y - s * 0.6, s * 0.2, s * 0.18), fill(MARIGOLD, 0.8 * a))
    c.drawRect(skia.Rect.MakeXYWH(x + s * 0.1, y - s * 1.0, s * 0.18, s * 0.32), fill((40, 40, 50), a))
    c.drawLine(x - 6 * s, y + 2, x + 2 * s, y + 2, stroke((120, 110, 140), 4, a))


def book(c, x, y, s, open_=1.0, title="", rgb=(140, 40, 50), a=255):
    """Big open book (the Constitution). open_ 0..1."""
    w = s * (0.9 + 0.9 * open_)
    c.drawRRect(rrect(x - w, y - s * 0.65, w * 2, s * 1.3, s * 0.06), fill(darken(rgb, 0.2), a))
    if open_ > 0.2:
        for sx in (-1, 1):
            c.drawRRect(rrect(x + (0 if sx > 0 else -w * 0.96), y - s * 0.6, w * 0.96, s * 1.2, s * 0.04), fill(MARBLE, a))
            for k in range(8):
                ly = y - s * 0.45 + k * s * 0.12
                c.drawLine(x + sx * w * 0.12, ly, x + sx * w * (0.85 - 0.1 * (k % 3)), ly, stroke((150, 140, 130), s * 0.025, a))
        c.drawLine(x, y - s * 0.6, x, y + s * 0.6, stroke((180, 170, 160), s * 0.03, a))
    if title:
        text(c, title, x, y + s * 0.85, s * 0.16, WHITE, a, 800, spacing=s * 0.02)


def ink_finger(c, x, y, s, a=255):
    """A voter's raised finger with the indelible ink mark."""
    skin = (190, 135, 98)
    c.drawRRect(rrect(x - s * 0.35, y - s * 0.2, s * 0.7, s * 0.8, s * 0.25), fill(skin, a))
    c.drawRRect(rrect(x - s * 0.12, y - s * 1.0, s * 0.24, s * 0.95, s * 0.12), fill(skin, a))
    c.drawRRect(rrect(x - s * 0.08, y - s * 0.98, s * 0.16, s * 0.2, s * 0.06), fill((250, 220, 210), a))
    c.drawLine(x - s * 0.1, y - s * 0.72, x + s * 0.1, y - s * 0.72, stroke((70, 50, 160), s * 0.07, a))


def lander(c, x, y, s, a=255):
    """Chandrayaan-3's Vikram lander (simplified): gold box, solar panel, four legs."""
    for sx in (-1, 1):
        c.drawLine(x + sx * s * 0.4, y - s * 0.3, x + sx * s * 0.75, y, stroke((180, 180, 190), s * 0.06, a))
        c.drawLine(x + sx * s * 0.68, y, x + sx * s * 0.85, y, stroke((180, 180, 190), s * 0.08, a))
    c.drawRRect(rrect(x - s * 0.5, y - s * 0.85, s * 1.0, s * 0.6, s * 0.06), shaded(linear((x - s * 0.5, 0), (x + s * 0.5, 0), [(250, 210, 90), (200, 150, 40)])))
    c.drawRect(skia.Rect.MakeXYWH(x - s * 0.36, y - s * 1.12, s * 0.72, s * 0.24), fill((40, 60, 140), a))
    for k in range(4):
        c.drawLine(x - s * 0.36 + k * s * 0.24, y - s * 1.12, x - s * 0.36 + k * s * 0.24, y - s * 0.88, stroke((90, 110, 190), 2, a))
    text(c, "ISRO", x, y - s * 0.5, s * 0.16, (60, 40, 20), a, 800)


def phone_qr(c, x, y, s, t, a=255):
    c.drawRRect(rrect(x - s * 0.5, y - s, s, s * 2, s * 0.14), fill((30, 30, 44), a))
    c.drawRRect(rrect(x - s * 0.44, y - s * 0.92, s * 0.88, s * 1.84, s * 0.1), fill(WHITE, a))
    rng = np.random.default_rng(1)
    cell = s * 0.06
    for i in range(11):
        for j in range(11):
            if rng.random() > 0.5 or (i < 3 and j < 3) or (i > 7 and j < 3) or (i < 3 and j > 7):
                c.drawRect(skia.Rect.MakeXYWH(x - s * 0.33 + i * cell, y - s * 0.55 + j * cell, cell, cell), fill(INK, a))
    c.drawRRect(rrect(x - s * 0.3, y + s * 0.3, s * 0.6, s * 0.18, s * 0.09), fill(GREEN, a))
    text(c, "PAY", x, y + s * 0.44, s * 0.12, WHITE, a, 800)


def hemicycle(c, cx, cy, r, groups, k=1.0, t=0.0):
    """Parliament seats as dots in semicircle rows. groups = [(count, rgb)], k reveals seats left to right."""
    total = sum(n for n, _ in groups)
    rows = 9
    seats = []
    for row in range(rows):
        rr = r * (0.45 + 0.55 * row / (rows - 1))
        n = int(round(total * rr / sum(r * (0.45 + 0.55 * q / (rows - 1)) for q in range(rows))))
        for i in range(n):
            ang = math.pi - math.pi * (i + 0.5) / n
            seats.append((ang, cx + rr * math.cos(ang), cy - rr * math.sin(ang)))
    seats.sort(key=lambda s: -s[0])
    seats = seats[:total]
    colors = [rgb for n, rgb in groups for _ in range(n)]
    for i, ((ang, x, y), rgb) in enumerate(zip(seats, colors)):
        g = clamp((k * total - i) / 30)
        if g > 0:
            c.drawCircle(x, y, r * 0.024 * g, fill(rgb))


def bars(c, x0, base, w, h, data, k=1.0, highlight=None):
    """Bar chart: data = [(label, value, rgb)]."""
    vmax = max(v for _, v, _ in data)
    bw = w / len(data)
    for i, (label, v, rgb) in enumerate(data):
        bh = h * v / vmax * clamp(k * 1.3 - i * 0.08)
        x = x0 + i * bw + bw * 0.15
        c.drawRRect(rrect(x, base - bh, bw * 0.7, bh, 10), fill(rgb))
        if highlight == i:
            glow(c, x + bw * 0.35, base - bh / 2, bh * 0.6, rgb, 90)
        text(c, label, x + bw * 0.35, base + 40, 24, WHITE, 230, 800, spacing=2)


def pyramid(c, cx, base, w, h, k=1.0, young=MARIGOLD):
    """Population pyramid: wide young base."""
    bands = 12
    for i in range(bands):
        frac = 1.0 - i / bands
        width = w * (0.25 + 0.75 * frac ** 0.7) * clamp(k * 1.3 - i * 0.05)
        y = base - (i + 1) * h / bands
        rgb = young if i < 6 else PEACOCK
        c.drawRRect(rrect(cx - width / 2, y + 3, width, h / bands - 6, 6), fill(rgb))
