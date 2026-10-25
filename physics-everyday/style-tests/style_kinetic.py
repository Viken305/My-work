"""Style B: kinetic typography + flat icons. Big slamming words, hard colour cuts, thick-outline icons.

Beat: your microwave doesn't heat food -> it shakes water -> 2,450,000,000 wiggles a second
-> flip, flip, flip = heat -> but not everywhere -> hot spots, cold spots.
"""
import math

import skia

from kit import W, H, blur, clamp, fill, font, hexc, lerp, measure, out_back, out_cubic, out_expo, polyline, prog, stroke, text

DURATION = 12.0

INK = hexc("111111")
PAPER = hexc("F5F1E8")
YELLOW = hexc("FFD60A")
RED = hexc("FF3D2E")
BLUE = hexc("2F6BFF")
PALETTE = [("Ink", INK), ("Paper", PAPER), ("Signal yellow", YELLOW), ("Hot red", RED), ("Cold blue", BLUE)]
FONTS_USED = [("black", "Inter Display Black (all caps)")]

SCENES = [  # start, background
    (0.0, INK), (2.0, YELLOW), (4.0, RED), (6.6, PAPER), (9.0, INK), (10.6, YELLOW),
]
WIPE = 0.22


def slam(c, s, x, y, size, rgb, t, t0, align="left", spacing=-0.03):
    """Word punches in: scale 1.4 -> 1 and fades up in ~0.18 s."""
    if t < t0:
        return 0
    p = out_expo(prog(t, t0, t0 + 0.2))
    sc = lerp(1.4, 1.0, p)
    sp = spacing * size
    w = measure(s, "black", size, sp)
    cx = x + w / 2 if align == "left" else x - w / 2 if align == "right" else x
    c.save()
    c.translate(cx, y - size * 0.36)
    c.scale(sc, sc)
    text(c, s, 0, size * 0.36, "black", size, rgb, 255 * min(1, p * 1.6), align="center", spacing=sp)
    c.restore()
    return w


def shake(t, hits, amp=14):
    dx = dy = 0.0
    for h in hits:
        k = prog(t, h, h + 0.22)
        if 0 < k < 1:
            e = (1 - k) * amp
            dx += e * math.sin(t * 97.0)
            dy += e * math.cos(t * 83.0)
    return dx, dy


# ---------------------------------------------------------------- icons (flat, thick ink outline)
def molecule(c, x, y, r, angle, o_col=RED, h_col=PAPER, line=INK):
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(angle))
    ha = math.radians(104.5 / 2)
    hs = [(math.sin(s * ha) * r * 1.15, math.cos(ha) * r * 1.15) for s in (-1, 1)]
    for hx, hy in hs:
        c.drawLine(0, 0, hx, hy, stroke(line, r * 0.16))
    for hx, hy in hs:
        c.drawCircle(hx, hy, r * 0.55, fill(h_col))
        c.drawCircle(hx, hy, r * 0.55, stroke(line, r * 0.1))
    c.drawCircle(0, 0, r, fill(o_col))
    c.drawCircle(0, 0, r, stroke(line, r * 0.1))
    c.drawCircle(-r * 0.35, -r * 0.35, r * 0.18, fill((255, 255, 255), 150))
    c.restore()


def flame(c, x, y, s, a=1.0):
    p = skia.Path()
    p.moveTo(x, y - s)
    p.cubicTo(x + s * 0.2, y - s * 0.55, x + s * 0.75, y - s * 0.3, x + s * 0.6, y + s * 0.25)
    p.cubicTo(x + s * 0.5, y + s * 0.7, x - s * 0.5, y + s * 0.7, x - s * 0.6, y + s * 0.25)
    p.cubicTo(x - s * 0.7, y - s * 0.15, x - s * 0.25, y - s * 0.35, x, y - s)
    p.close()
    c.save()
    c.translate(x, y + s * 0.6)
    c.scale(a, a)
    c.translate(-x, -(y + s * 0.6))
    c.drawPath(p, fill(RED))
    inner = skia.Path()
    inner.addOval(skia.Rect.MakeXYWH(x - s * 0.28, y - s * 0.05, s * 0.56, s * 0.62))
    c.drawPath(inner, fill(YELLOW))
    c.drawPath(p, stroke(INK, s * 0.09))
    c.restore()


def microwave(c, x, y, w, h, t, heat=0.0):
    body = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 34, 34)
    c.drawRRect(body, fill(PAPER))
    c.drawRRect(body, stroke(YELLOW, 12))
    wx, wy, ww, wh = x + 40, y + 40, w * 0.66, h - 80
    win = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(wx, wy, ww, wh), 18, 18)
    c.drawRRect(win, fill(INK))
    c.drawRRect(win, stroke(YELLOW, 8))
    # heat map: grid of dots, hot where sin^2 peaks
    cols, rows = 9, 4
    for i in range(cols):
        for j in range(rows):
            hval = (math.sin(math.pi * (i + 0.5) / 3) ** 2) * (math.sin(math.pi * (j + 0.5) / 2) ** 2)
            k = clamp(heat * (cols + rows) - (i + j) * 0.6)
            if k <= 0:
                continue
            px = wx + ww * (i + 0.5) / cols
            py = wy + wh * (j + 0.5) / rows
            rgb = RED if hval > 0.45 else BLUE
            r = (14 + 12 * hval) * out_back(k)
            if hval > 0.45:
                c.drawCircle(px, py, r * 2.2, blur(fill(RED, 110), 14))
            c.drawCircle(px, py, r, fill(rgb))
    px = x + 40 + ww + (w - 80 - ww) / 2
    for k in range(3):
        c.drawCircle(px, y + 90 + k * 70, 18, stroke(YELLOW, 7))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px - 40, y + h - 120, 80, 50), 10, 10), fill(YELLOW))


def counter(c, value, x, y, size, rgb):
    s = f"{value:,}"
    cell = measure("0", "black", size)
    comma = cell * 0.42
    total = sum(comma if ch == "," else cell for ch in s)
    cx = x - total / 2
    f = font("black", size)
    for ch in s:
        cw = comma if ch == "," else cell
        c.drawString(ch, cx + (cw - f.measureText(ch)) / 2, y, f, fill(rgb))
        cx += cw


# ---------------------------------------------------------------- scenes
def s1(c, t):
    slam(c, "YOUR", 150, 450, 160, PAPER, t, 0.15)
    slam(c, "MICROWAVE", 150 + measure("YOUR ", "black", 160, -4.8), 450, 160, PAPER, t, 0.45)
    slam(c, "DOESN'T HEAT FOOD.", 150, 640, 130, YELLOW, t, 1.0)


def s2(c, t):
    slam(c, "IT SHAKES", 150, 420, 170, INK, t, 2.04)
    slam(c, "WATER.", 150, 700, 270, INK, t, 2.5)
    a = prog(t, 2.1, 2.3)
    if a > 0:
        wig = math.sin((t - 2.1) * 2 * math.pi * 6) * math.radians(28)
        x, y = 1580, 520
        molecule(c, x, y, 105 * out_back(a), wig)
        for k in range(3):  # motion lines
            ang = math.radians(-140 + k * 25)
            r0, r1 = 290, 340 + 25 * math.sin(t * 30 + k)
            c.drawLine(x + r0 * math.cos(ang), y + r0 * math.sin(ang), x + r1 * math.cos(ang), y + r1 * math.sin(ang), stroke(INK, 14))
            ang = math.radians(40 + k * 25)
            c.drawLine(x + r0 * math.cos(ang), y + r0 * math.sin(ang), x + r1 * math.cos(ang), y + r1 * math.sin(ang), stroke(INK, 14))


def s3(c, t):
    p = out_expo(prog(t, 4.04, 5.2))
    if t >= 4.04:
        sc = lerp(1.25, 1.0, out_expo(prog(t, 4.04, 4.3)))
        c.save()
        c.translate(W / 2, 520)
        c.scale(sc, sc)
        counter(c, int(round(2_450_000_000 * p)), 0, 70, 230, PAPER)
        c.restore()
    slam(c, "WIGGLES  EVERY  SECOND", W / 2, 760, 84, INK, t, 5.0, align="center", spacing=0.04)
    # pulsing sine glyph
    a = prog(t, 4.2, 4.5)
    if a > 0:
        pts = [(W / 2 - 330 + i * 4, 260 + 34 * math.sin(i * 0.12 - t * 30)) for i in range(166)]
        c.drawPath(polyline(pts), stroke(PAPER, 12, 255 * a))
    slam(c, "(that's 2.45 GHz)", W / 2, 900, 48, PAPER, t, 5.6, align="center", spacing=0.0)


def s4(c, t):
    beats = [6.85, 7.35, 7.85]
    ang = 0.0
    for b in beats:
        ang += math.pi * out_back(prog(t, b, b + 0.22), 2.2)
    a = out_back(prog(t, 6.6, 6.85))
    if a > 0:
        molecule(c, 1400, 500, 150 * a, ang)
        for b in beats:  # flip arcs
            k = prog(t, b, b + 0.35)
            if 0 < k < 1:
                arc = skia.Path()
                arc.addArc(skia.Rect.MakeXYWH(1400 - 290, 500 - 290, 580, 580), -150, 120 * k)
                c.drawPath(arc, stroke(INK, 16, 255 * (1 - k)))
    for i, b in enumerate(beats):
        slam(c, "FLIP.", 150, 330 + i * 170, 170, INK, t, b)
    if t >= 8.3:
        slam(c, "=  HEAT", 150, 900, 150, RED, t, 8.3)
        flame(c, 150 + measure("=  HEAT", "black", 150, -4.5) + 110, 830, 90, out_back(prog(t, 8.4, 8.65)))


def s5(c, t):
    slam(c, "BUT NOT", 150, 470, 140, PAPER, t, 9.04)
    slam(c, "EVERYWHERE.", 150, 620, 140, YELLOW, t, 9.4)
    a = out_back(prog(t, 9.1, 9.4))
    if a > 0:
        c.save()
        c.translate(1530, 540)
        c.scale(a * 0.82, a * 0.82)
        microwave(c, -330, -230, 660, 460, t, heat=prog(t, 9.6, 10.4))
        c.restore()


def s6(c, t):
    slam(c, "HOT SPOTS.", W / 2, 470, 220, RED, t, 10.64, align="center")
    slam(c, "COLD SPOTS.", W / 2, 720, 220, BLUE, t, 11.1, align="center")
    text(c, "THE PHYSICS OF EVERYDAY THINGS  ·  EP. 01  MICROWAVES", W / 2, 960, "black", 34, INK,
         255 * prog(t, 11.4, 11.7), spacing=4)


DRAW = [s1, s2, s3, s4, s5, s6]
HITS = [0.15, 0.45, 1.0, 2.04, 2.5, 4.04, 6.85, 7.35, 7.85, 8.3, 9.04, 9.4, 10.64, 11.1]


def draw(c, t):
    idx = max(i for i, (s, _) in enumerate(SCENES) if t >= s)
    dx, dy = shake(t, HITS)
    c.clear(fill(SCENES[idx][1]).getColor())
    if idx > 0 and t < SCENES[idx][0] + WIPE:
        # new colour wipes in from the right over the previous scene
        c.clear(fill(SCENES[idx - 1][1]).getColor())
        c.save()
        c.translate(dx, dy)
        DRAW[idx - 1](c, t)
        c.restore()
        x = W * (1 - out_expo(prog(t, SCENES[idx][0], SCENES[idx][0] + WIPE)))
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x, 0, W, H))
        c.clear(fill(SCENES[idx][1]).getColor())
    else:
        c.save()
    c.translate(dx, dy)
    DRAW[idx](c, t)
    c.restore()
