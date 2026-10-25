"""2D layer for Ep. 03 (skia): serif titles, captions, gold line-art instruments, labels, bokeh dust, flashes."""
import math
import os

import numpy as np
import skia

W, H = 1080, 1920
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
GOLD = (232, 196, 124)
GOLD_D = (190, 150, 80)
IVORY = (248, 242, 228)
INK = (14, 12, 10)
_TF = {}


def tf(name):
    if name not in _TF:
        _TF[name] = skia.Typeface.MakeFromFile(os.path.join(FONTS, name))
    return _TF[name]


def serif(size, w=600, italic=False):
    f = skia.Font(tf(f"CormorantGaramond-{'Italic-' if italic else ''}{w}.ttf"), size)
    f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
    f.setSubpixel(True)
    return f


def sans(size, w="Medium"):
    f = skia.Font(tf(f"InterDisplay-{w}.otf"), size)
    f.setSubpixel(True)
    return f


def col(c, a=1.0):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(max(0, min(1, a)) * 255))


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t1)


def ease(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def text(c, s, x, y, f, color=IVORY, a=1.0, align="left", tracking=0.0, shadow=0.55):
    """Draw text with optional letter-spacing and a soft legibility shadow."""
    widths = [f.measureText(ch) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    if align == "center":
        x -= total / 2
    elif align == "right":
        x -= total
    if shadow > 0:
        sp = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), a * shadow), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
        _run(c, s, x, y + 2, f, sp, widths, tracking)
    _run(c, s, x, y, f, skia.Paint(AntiAlias=True, Color=col(color, a)), widths, tracking)
    return total


def _run(c, s, x, y, f, p, widths, tracking):
    if tracking == 0:
        c.drawString(s, x, y, f, p)
        return
    for ch, w in zip(s, widths):
        c.drawString(ch, x, y, f, p)
        x += w + tracking


def line(c, x0, y0, x1, y1, color=GOLD, w=2.0, a=1.0):
    c.drawLine(x0, y0, x1, y1, skia.Paint(AntiAlias=True, StrokeWidth=w, Color=col(color, a), StrokeCap=skia.Paint.kRound_Cap))


# ---------------------------------------------------------------- captions (spoken word in gold)
def caption(c, words, active, y=1700, a=1.0, size=50):
    f = sans(size, "SemiBold")
    space = f.measureText(" ")
    lines, cur, cw = [], [], 0
    for wd in words:
        w = f.measureText(wd)
        if cur and cw + space + w > 900:
            lines.append(cur)
            cur, cw = [], 0
        cur.append((wd, w))
        cw += (space if cw else 0) + w
    lines.append(cur)
    lh = size * 1.3
    top = y - lh * (len(lines) - 1) / 2
    idx = 0
    for li, ln in enumerate(lines):
        tw = sum(w for _, w in ln) + space * (len(ln) - 1)
        x = W / 2 - tw / 2
        for wd, w in ln:
            colr = GOLD if idx == active else IVORY
            text(c, wd, x, top + li * lh, f, colr, a * (1.0 if idx <= active else 0.82), shadow=0.8)
            x += w + space
            idx += 1


# ---------------------------------------------------------------- titles
def title_card(c, t, t0, t1, main="Why popcorn pops", kicker="THE PHYSICS OF EVERYDAY THINGS", num="Nº 03", y=760):
    if t < t0 or t > t1 + 0.6:
        return
    a = ease(prog(t, t0, t0 + 0.8)) * (1 - prog(t, t1, t1 + 0.6))
    rule = ease(prog(t, t0 + 0.1, t0 + 1.0))
    text(c, kicker, W / 2, y - 130, sans(28, "Medium"), GOLD, a, "center", tracking=6)
    line(c, W / 2 - 220 * rule, y - 92, W / 2 + 220 * rule, y - 92, GOLD, 1.5, a * 0.8)
    f = serif(150, 700, italic=True)
    rise = (1 - ease(prog(t, t0 + 0.15, t0 + 1.1))) * 18
    text(c, main, W / 2, y + 30 + rise, f, IVORY, a, "center", shadow=0.7)
    line(c, W / 2 - 60 * rule, y + 80, W / 2 + 60 * rule, y + 80, GOLD, 1.5, a * 0.8)
    text(c, num, W / 2, y + 128, serif(40, 600), GOLD, a, "center")


def end_card(c, t, t0, t1):
    if t < t0 or t > t1:
        return
    a = ease(prog(t, t0, t0 + 0.9)) * (1 - prog(t, t1 - 0.4, t1))
    rule = ease(prog(t, t0 + 0.2, t0 + 1.2))
    text(c, "The Physics of", W / 2, 700, serif(88, 600, True), IVORY, a, "center")
    text(c, "Everyday Things", W / 2, 800, serif(104, 600, True), IVORY, a, "center")
    line(c, W / 2 - 200 * rule, 856, W / 2 + 200 * rule, 856, GOLD, 1.5, a * 0.8)
    text(c, "Nº 03  ·  POPCORN", W / 2, 912, sans(26, "Medium"), GOLD, a, "center", tracking=6)
    text(c, "Follow for the next one", W / 2, 990, serif(44, 500, True), IVORY, a * 0.85, "center")


# ---------------------------------------------------------------- instruments (gold line art)
def thermometer(c, t, t0, t1, value, x=W / 2, y=330):
    if t < t0 or t > t1 + 0.5:
        return
    a = ease(prog(t, t0, t0 + 0.5)) * (1 - prog(t, t1, t1 + 0.5))
    f = serif(150, 600)
    s = f"{int(round(value))}"
    w = f.measureText(s)
    text(c, s, x - 30, y, f, IVORY, a, "center", shadow=0.7)
    text(c, "°C", x - 30 + w / 2 + 8, y - 70, serif(54, 600), GOLD, a)
    # a thin arc that fills with temperature
    r = 150
    rect = skia.Rect(x - r - 30, y - 105 - r, x + r - 30, y - 105 + r)
    del rect
    bar_w = 420
    bx, by = x - bar_w / 2 - 30, y + 40
    line(c, bx, by, bx + bar_w, by, GOLD, 1.5, a * 0.35)
    u = clamp(value / 200)
    line(c, bx, by, bx + bar_w * u, by, GOLD, 3, a)
    for v in (100, 180):
        xx = bx + bar_w * v / 200
        line(c, xx, by - 10, xx, by + 10, GOLD, 1.5, a * 0.7)
        text(c, f"{v}", xx, by + 40, sans(22, "Medium"), GOLD, a * 0.8, "center", shadow=0)


def gauge(c, t, t0, t1, value, x=W / 2, y=420, r=170):
    """Pressure gauge in atmospheres, 0..10."""
    if t < t0 or t > t1 + 0.5:
        return
    a = ease(prog(t, t0, t0 + 0.5)) * (1 - prog(t, t1, t1 + 0.5))
    a0, a1 = 140, 400
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2, Color=col(GOLD, a * 0.8))
    c.drawArc(skia.Rect(x - r, y - r, x + r, y + r), a0, a1 - a0, False, p)
    bg = skia.Paint(AntiAlias=True, Color=col((0, 0, 0), a * 0.35), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
    c.drawCircle(x, y, r * 0.9, bg)
    for k in range(11):
        ang = math.radians(a0 + (a1 - a0) * k / 10)
        r0 = r - (22 if k % 5 == 0 else 12)
        line(c, x + r0 * math.cos(ang), y + r0 * math.sin(ang), x + r * math.cos(ang), y + r * math.sin(ang), GOLD, 2, a)
        if k % 5 == 0 or k == 9:
            rr = r - 48
            text(c, str(k), x + rr * math.cos(ang), y + rr * math.sin(ang) + 10, serif(34, 600), IVORY, a * 0.85, "center", shadow=0)
    # filled arc up to the value
    hp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=6, Color=col(GOLD, a), StrokeCap=skia.Paint.kRound_Cap)
    c.drawArc(skia.Rect(x - r + 4, y - r + 4, x + r - 4, y + r - 4), a0, (a1 - a0) * clamp(value / 10), False, hp)
    ang = math.radians(a0 + (a1 - a0) * clamp(value / 10))
    line(c, x - 22 * math.cos(ang), y - 22 * math.sin(ang), x + (r - 30) * math.cos(ang), y + (r - 30) * math.sin(ang), IVORY, 3, a)
    c.drawCircle(x, y, 8, skia.Paint(AntiAlias=True, Color=col(GOLD, a)))
    text(c, f"{value:.1f}", x, y + r * 0.62, serif(64, 600), IVORY, a, "center")
    text(c, "ATMOSPHERES", x, y + r * 0.62 + 36, sans(18, "Medium"), GOLD, a, "center", tracking=4, shadow=0)


def label(c, t, t0, anchor, text_, sub=None, side=1, dx=170, dy=-120, t1=None):
    """Gold dot on the subject, a hairline to a serif label."""
    if t < t0 or (t1 is not None and t > t1 + 0.4) or anchor is None:
        return
    a = ease(prog(t, t0, t0 + 0.4)) * (1 - (prog(t, t1, t1 + 0.4) if t1 else 0))
    ax, ay = anchor
    u = ease(prog(t, t0, t0 + 0.45))
    ex, ey = ax + dx * side * u, ay + dy * u
    c.drawCircle(ax, ay, 7, skia.Paint(AntiAlias=True, Color=col(GOLD, a)))
    c.drawCircle(ax, ay, 14, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.5, Color=col(GOLD, a * 0.6)))
    line(c, ax, ay, ex, ey, GOLD, 1.6, a)
    line(c, ex, ey, ex + 60 * side * u, ey, GOLD, 1.6, a)
    tx = ex + (70 if side > 0 else -70)
    al = "left" if side > 0 else "right"
    text(c, text_, tx, ey + 14, serif(58, 600), IVORY, a, al)
    if sub:
        text(c, sub, tx, ey + 56, sans(22, "Medium"), GOLD, a * 0.9, al, tracking=3)


def big_number(c, t, t0, t1, s, sub, y=470):
    if t < t0 or t > t1 + 0.5:
        return
    a = ease(prog(t, t0, t0 + 0.4)) * (1 - prog(t, t1, t1 + 0.5))
    sc = 1.0 + 0.12 * (1 - ease(prog(t, t0, t0 + 0.5)))
    c.save()
    c.translate(W / 2, y)
    c.scale(sc, sc)
    text(c, s, 0, 0, serif(190, 600, True), IVORY, a, "center", shadow=0.8)
    c.restore()
    text(c, sub, W / 2, y + 70, sans(24, "Medium"), GOLD, a, "center", tracking=6)


def rec(c, t, t0, t1, fps="2,900 FPS", y=150):
    if t < t0 or t > t1:
        return
    a = ease(prog(t, t0, t0 + 0.3)) * (1 - prog(t, t1 - 0.3, t1))
    blink = 1.0 if int(t * 2) % 2 == 0 else 0.35
    c.drawCircle(W / 2 - 150, y - 9, 9, skia.Paint(AntiAlias=True, Color=col((230, 60, 50), a * blink)))
    text(c, fps, W / 2 - 128, y, sans(28, "SemiBold"), IVORY, a, tracking=3)
    ms = (t - t0) * 1000 / 120.0
    text(c, f"{ms:6.1f} ms", W / 2 + 160, y, sans(28, "Medium"), GOLD, a, "right")


def strike(c, t, t0, x0, y0, x1, y1, a=1.0):
    if t < t0:
        return
    u = ease(prog(t, t0, t0 + 0.3))
    line(c, x0, y0, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, (220, 70, 60), 4, a)


def dashed_path(c, pts, t, t0, dur=0.6, color=GOLD):
    if t < t0 or len(pts) < 2:
        return
    u = ease(prog(t, t0, t0 + dur))
    n = max(2, int(len(pts) * u))
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:n]:
        p.lineTo(*q)
    pa = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3, Color=col(color, 0.95),
                    PathEffect=skia.DashPathEffect.Make([14, 12], 0))
    c.drawPath(p, pa)


def waveform(c, t, t0, t1, y=380, amp=110):
    if t < t0 or t > t1 + 0.4:
        return
    a = ease(prog(t, t0, t0 + 0.3)) * (1 - prog(t, t1, t1 + 0.4))
    u = ease(prog(t, t0, t0 + 1.2))
    p = skia.Path()
    x0, x1 = 120, 960
    n = 300
    for i in range(int(n * u)):
        x = x0 + (x1 - x0) * i / n
        s = i / n
        env = math.exp(-((s - 0.32) / 0.035) ** 2) * 1.0 + math.exp(-max(0, s - 0.32) * 9) * 0.35 * (s > 0.32)
        yy = y + amp * env * math.sin(i * 1.9) * (0.6 + 0.4 * math.sin(i * 0.37))
        (p.moveTo if i == 0 else p.lineTo)(x, yy)
    c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.5, Color=col(GOLD, a)))
    line(c, x0, y, x1, y, GOLD, 1, a * 0.3)


# ---------------------------------------------------------------- atmosphere
class Motes:
    """Dust drifting in the key light: soft out-of-focus specks."""

    def __init__(self, n=55, seed=1):
        r = np.random.default_rng(seed)
        self.p = r.uniform(0, 1, (n, 2)) * [W, H]
        self.v = r.normal(0, 1, (n, 2)) * [6, 4] + [4, -7]
        self.s = r.uniform(2, 14, n)
        self.a = r.uniform(0.04, 0.22, n)
        self.ph = r.uniform(0, 6.3, n)

    def draw(self, c, t, k=1.0, seed_shift=0.0):
        if k <= 0:
            return
        for (x, y), (vx, vy), s, a, ph in zip(self.p, self.v, self.s, self.a, self.ph):
            xx = (x + vx * t + 12 * math.sin(t * 0.6 + ph)) % W
            yy = (y + vy * t) % H
            pa = skia.Paint(AntiAlias=True, Color=col((255, 226, 180), a * k * (0.7 + 0.3 * math.sin(t * 1.3 + ph))),
                            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, s * 0.6), BlendMode=skia.BlendMode.kPlus)
            c.drawCircle(xx, yy, s, pa)


def flash(c, a):
    if a > 0:
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=col((255, 246, 230), a), BlendMode=skia.BlendMode.kPlus))


def fade(c, a):
    if a > 0:
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=col((0, 0, 0), a)))


def bottom_scrim(c, a=1.0):
    g = skia.GradientShader.MakeLinear([skia.Point(0, H - 520), skia.Point(0, H)],
                                       [skia.Color4f(0, 0, 0, 0), skia.Color4f(0, 0, 0, 0.55 * a)])
    c.drawRect(skia.Rect(0, H - 520, W, H), skia.Paint(Shader=g))
