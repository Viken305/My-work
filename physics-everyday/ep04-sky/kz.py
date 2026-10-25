"""Flat-vector 'explainer' kit: gradient shapes with rim light, glows, stars, grain, and the episode's cast
(photons with faces, N2/O2 molecules, a stargazer, hills, clouds, Sun, Earth, Mars)."""
import math
import os
import zlib

import numpy as np
import skia

W, H = 1080, 1920
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")

# ---------------------------------------------------------------- palette
NAVY = (12, 20, 52)
NAVY2 = (22, 34, 84)
INDIGO = (46, 44, 120)
SPACE = (8, 10, 30)
SKY_TOP = (40, 110, 220)
SKY_BOT = (130, 200, 250)
WHITE = (250, 250, 255)
INK = (16, 18, 40)
SUN_Y = (255, 214, 92)
SUN_O = (255, 150, 60)
GRASS = (70, 190, 120)
GRASS_D = (36, 130, 96)
SPECTRUM = [("red", (255, 72, 88)), ("orange", (255, 150, 60)), ("yellow", (255, 222, 80)), ("green", (80, 220, 130)),
            ("blue", (90, 170, 255)), ("violet", (170, 100, 255))]
SPEC = dict(SPECTRUM)
N2_C = (110, 150, 255)
O2_C = (255, 110, 120)


def mix(a, b, u):
    u = max(0.0, min(1.0, u))
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))


def shade(c, k):
    return tuple(max(0, min(255, v * k)) for v in c)


def lighten(c, k):
    return tuple(v + (255 - v) * k for v in c)


def col(c, a=1.0):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(max(0, min(1, a)) * 255))


def c4(c, a=1.0):
    return skia.Color4f(c[0] / 255, c[1] / 255, c[2] / 255, max(0.0, min(1.0, a)))


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t1)


def ss(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def io(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def oc(x):
    return 1 - (1 - clamp(x)) ** 3


def oe(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def ob(x, s=1.70158):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def lerp(a, b, u):
    return a + (b - a) * u


def rng(*key):
    return np.random.default_rng(zlib.crc32(repr(key).encode()))


# ---------------------------------------------------------------- fonts
_TF = {}


def font(size, w=900):
    if w not in _TF:
        _TF[w] = skia.Typeface.MakeFromFile(os.path.join(FONTS, f"Nunito-{w}.ttf"))
    f = skia.Font(_TF[w], size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def text(c, s, x, y, size, color=WHITE, a=1.0, align="center", w=900, shadow=0.35):
    f = font(size, w)
    tw = f.measureText(s)
    if align == "center":
        x -= tw / 2
    elif align == "right":
        x -= tw
    if shadow:
        c.drawString(s, x, y + size * 0.06, f, skia.Paint(AntiAlias=True, Color=col(INK, a * shadow)))
    c.drawString(s, x, y, f, skia.Paint(AntiAlias=True, Color=col(color, a)))
    return tw


# ---------------------------------------------------------------- shapes with rim light
def circle_path(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def rrect_path(x, y, w, h, r):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect(x, y, x + w, y + h), r, r))
    return p


def poly_path(pts, close=True, smooth=False):
    p = skia.Path()
    pts = list(pts)
    if smooth and len(pts) > 2:
        m = [((pts[i][0] + pts[(i + 1) % len(pts)][0]) / 2, (pts[i][1] + pts[(i + 1) % len(pts)][1]) / 2) for i in range(len(pts))]
        p.moveTo(*m[-1])
        for i in range(len(pts)):
            p.quadTo(pts[i][0], pts[i][1], m[i][0], m[i][1])
    else:
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
    if close:
        p.close()
    return p


def union(*ps):
    out = ps[0]
    for q in ps[1:]:
        out = skia.Op(out, q, skia.PathOp.kUnion_PathOp)
    return out


def shape(c, path, color, a=1.0, light=0.22, dark=0.25, rim=5.0, grad=True, shadow=0.0, angle=(-0.6, -0.8)):
    """A flat shape lit from the top-left: soft vertical gradient, a bright crescent rim on the lit side and a darker
    one on the far side (the look of a vector explainer)."""
    b = path.getBounds()
    if shadow:
        sp = skia.Path(path)
        sp.offset(0, rim * 1.6)
        c.drawPath(sp, skia.Paint(AntiAlias=True, Color=col(shade(color, 0.35), a * shadow),
                                  MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, rim * 1.5)))
    if grad:
        sh = skia.GradientShader.MakeLinear([skia.Point(b.left(), b.top()), skia.Point(b.left() + b.width() * 0.3, b.bottom())],
                                            [c4(lighten(color, light * 0.6), a), c4(shade(color, 1 - dark * 0.5), a)])
        c.drawPath(path, skia.Paint(AntiAlias=True, Shader=sh))
    else:
        c.drawPath(path, skia.Paint(AntiAlias=True, Color=col(color, a)))
    if rim > 0:
        dx, dy = -angle[0] * rim, -angle[1] * rim
        moved = skia.Path(path)
        moved.offset(dx, dy)
        hi = skia.Op(path, moved, skia.PathOp.kDifference_PathOp)
        c.drawPath(hi, skia.Paint(AntiAlias=True, Color=col(lighten(color, 0.45), a * 0.75)))
        moved = skia.Path(path)
        moved.offset(-dx * 0.8, -dy * 0.8)
        lo = skia.Op(path, moved, skia.PathOp.kDifference_PathOp)
        c.drawPath(lo, skia.Paint(AntiAlias=True, Color=col(shade(color, 0.7), a * 0.55)))


def glow(c, x, y, r, color, a=1.0, core=0.0):
    sh = skia.GradientShader.MakeRadial(skia.Point(x, y), max(r, 0.1), [c4(color, a), c4(color, a * 0.35 * (1 - core) + a * core * 0.5),
                                                                        c4(color, 0)], [0, 0.35, 1])
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=sh, BlendMode=skia.BlendMode.kPlus))


def vgrad(c, y0, y1, c0, c1, x0=-4000, x1=4000, a=1.0):
    sh = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [c4(c0, a), c4(c1, a)])
    c.drawRect(skia.Rect(x0, min(y0, y1) - 20000 if False else y0, x1, y1), skia.Paint(Shader=sh))


def fill(c, color, a=1.0):
    c.drawPaint(skia.Paint(Color=col(color, a)))


# ---------------------------------------------------------------- stars
class Stars:
    def __init__(self, n=420, seed=1, w=W * 3, h=H * 3):
        r = np.random.default_rng(seed)
        self.p = r.uniform(-1, 1, (n, 2)) * [w / 2, h / 2]
        self.s = r.uniform(0.6, 2.6, n) ** 1.6
        self.d = r.uniform(0.15, 1.0, n)   # depth for parallax
        self.ph = r.uniform(0, 6.3, n)
        self.hue = r.integers(0, 3, n)
        self.w, self.h = w, h

    def draw(self, c, t, off=(0, 0), a=1.0, streak=0.0):
        if a <= 0:
            return
        cols = [(255, 255, 255), (200, 220, 255), (255, 230, 200)]
        for (x, y), s, d, ph, hu in zip(self.p, self.s, self.d, self.ph, self.hue):
            xx = (x - off[0] * d) % self.w - self.w / 2 + W / 2
            yy = (y - off[1] * d) % self.h - self.h / 2 + H / 2
            if not (-50 < xx < W + 50 and -50 < yy < H + 50):
                continue
            tw = 0.55 + 0.45 * math.sin(t * (1.5 + d) + ph)
            al = a * tw * (0.35 + 0.65 * d)
            if streak > 0:
                L = streak * d
                c.drawLine(xx, yy, xx + L, yy, skia.Paint(AntiAlias=True, StrokeWidth=s, Color=col(cols[hu], al * 0.8),
                                                          StrokeCap=skia.Paint.kRound_Cap))
            c.drawCircle(xx, yy, s, skia.Paint(AntiAlias=True, Color=col(cols[hu], al)))
            if s > 3.2:
                sparkle(c, xx, yy, s * 3, cols[hu], al * 0.6)


def sparkle(c, x, y, r, color, a):
    p = skia.Path()
    k = r * 0.18
    p.moveTo(x, y - r)
    p.quadTo(x + k, y - k, x + r, y)
    p.quadTo(x + k, y + k, x, y + r)
    p.quadTo(x - k, y + k, x - r, y)
    p.quadTo(x - k, y - k, x, y - r)
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=col(color, a)))


# ---------------------------------------------------------------- grain
_GR = {}


def grain(c, t, a=0.05):
    if "img" not in _GR:
        r = np.random.default_rng(9)
        imgs = []
        for k in range(4):
            v = (r.standard_normal((H // 2, W // 2)) * 40 + 128).clip(0, 255).astype(np.uint8)
            rgba = np.dstack([v, v, v, np.full_like(v, 255)])
            imgs.append(skia.Image.fromarray(np.ascontiguousarray(rgba)))
        _GR["img"] = imgs
    img = _GR["img"][int(t * 12) % 4]
    p = skia.Paint(BlendMode=skia.BlendMode.kOverlay)
    p.setAlphaf(a)
    c.drawImageRect(img, skia.Rect(0, 0, W, H), skia.SamplingOptions(skia.FilterMode.kLinear), p)


def vignette(c, a=0.45):
    sh = skia.GradientShader.MakeRadial(skia.Point(W / 2, H * 0.48), H * 0.75, [c4((0, 0, 0), 0), c4((0, 0, 0), 0), c4((0, 0, 10), a)],
                                        [0, 0.55, 1])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh))


# ---------------------------------------------------------------- the cast
def photon(c, x, y, r, color, t, look=(1, 0), mood="happy", a=1.0, seed=0, trail=0.0, wobble=1.0):
    """A glowing ball of light with a face."""
    bob = math.sin(t * 6 + seed) * r * 0.06 * wobble
    y += bob
    glow(c, x, y, r * 3.0, color, 0.55 * a)
    if trail > 0:
        lx, ly = look
        n = math.hypot(lx, ly) or 1
        for k in range(1, 7):
            glow(c, x - lx / n * r * 0.9 * k * trail, y - ly / n * r * 0.9 * k * trail, r * (1.1 - k * 0.12), color, 0.25 * a * (1 - k / 7))
    shape(c, circle_path(x, y, r), color, a, light=0.45, dark=0.2, rim=r * 0.12)
    c.drawCircle(x - r * 0.35, y - r * 0.38, r * 0.2, skia.Paint(AntiAlias=True, Color=col((255, 255, 255), 0.55 * a)))
    # face
    lx, ly = look
    n = math.hypot(lx, ly) or 1
    lx, ly = lx / n, ly / n
    blink = 1.0 if (t * 0.7 + seed * 0.37) % 3.1 > 0.12 else 0.15
    for sx in (-1, 1):
        ex, ey = x + sx * r * 0.32 + lx * r * 0.12, y - r * 0.05 + ly * r * 0.1
        eh = r * 0.26 * blink
        if mood == "sleepy":
            eh = r * 0.08
        c.drawOval(skia.Rect(ex - r * 0.16, ey - eh, ex + r * 0.16, ey + eh), skia.Paint(AntiAlias=True, Color=col(WHITE, a)))
        if eh > r * 0.1:
            c.drawCircle(ex + lx * r * 0.06, ey + ly * r * 0.06, r * 0.1, skia.Paint(AntiAlias=True, Color=col(INK, a)))
    mp = skia.Path()
    my = y + r * 0.32
    if mood == "surprised":
        c.drawOval(skia.Rect(x - r * 0.1, my - r * 0.08, x + r * 0.1, my + r * 0.14), skia.Paint(AntiAlias=True, Color=col(INK, a)))
    else:
        mp.moveTo(x - r * 0.18, my)
        mp.quadTo(x, my + r * (0.18 if mood != "sleepy" else 0.05), x + r * 0.18, my)
        c.drawPath(mp, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=max(1.5, r * 0.08), Color=col(INK, a),
                                  StrokeCap=skia.Paint.kRound_Cap))


def molecule(c, x, y, s, kind, t, shake=0.0, a=1.0, seed=0, face=True, angle=None):
    """N2 (two blue spheres) or O2 (two coral spheres), jiggling; electrons buzz when shaken."""
    color = N2_C if kind == "N2" else O2_C
    r = rng("mol", seed)
    ang = (angle if angle is not None else r.uniform(0, 6.3)) + math.sin(t * 1.3 + seed) * 0.25
    jx = math.sin(t * 9 + seed) * s * 0.03 + shake * s * 0.18 * math.sin(t * 38 + seed)
    jy = math.cos(t * 7 + seed) * s * 0.03 + shake * s * 0.12 * math.cos(t * 33 + seed)
    x, y = x + jx, y + jy
    d = s * 0.55
    p1 = (x - d * math.cos(ang), y - d * math.sin(ang))
    p2 = (x + d * math.cos(ang), y + d * math.sin(ang))
    if shake > 0.01:
        glow(c, x, y, s * 2.4, lighten(color, 0.4), 0.35 * shake * a)
    shape(c, circle_path(*p1, s * 0.8), color, a, light=0.4, rim=s * 0.1)
    shape(c, circle_path(*p2, s * 0.8), shade(color, 0.92), a, light=0.4, rim=s * 0.1)
    if face:
        fx, fy = p2 if p2[1] > p1[1] else p1
        for sx in (-1, 1):
            c.drawCircle(fx + sx * s * 0.22, fy - s * 0.05, s * 0.09, skia.Paint(AntiAlias=True, Color=col(INK, a)))
        m = skia.Path()
        m.moveTo(fx - s * 0.12, fy + s * 0.16)
        m.quadTo(fx, fy + s * (0.26 if shake < 0.5 else 0.02), fx + s * 0.12, fy + s * 0.16)
        c.drawPath(m, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=max(1.2, s * 0.06), Color=col(INK, a),
                                 StrokeCap=skia.Paint.kRound_Cap))
    # electrons
    if shake > 0.01:
        for k in range(3):
            e = t * 9 + k * 2.1 + seed
            ex = x + s * 1.3 * math.cos(e) + shake * s * 0.3 * math.sin(t * 40 + k)
            ey = y + s * 0.7 * math.sin(e)
            c.drawCircle(ex, ey, s * 0.13, skia.Paint(AntiAlias=True, Color=col((255, 250, 180), a * shake)))
            glow(c, ex, ey, s * 0.4, (255, 240, 160), 0.5 * a * shake)


def wave(c, x0, x1, y, amp, lam, phase, color, width=8.0, a=1.0, glow_w=0.0, env=None):
    p = skia.Path()
    n = max(40, int(abs(x1 - x0) / 4))
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        e = env(x) if env else 1.0
        yy = y + amp * e * math.sin(2 * math.pi * (x - phase) / lam)
        (p.moveTo if i == 0 else p.lineTo)(x, yy)
    if glow_w:
        c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width * glow_w, Color=col(color, 0.25 * a),
                                 MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, width * 1.5), StrokeCap=skia.Paint.kRound_Cap))
    c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width, Color=col(color, a),
                             StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join))
    hp = skia.Path(p)
    hp.offset(-width * 0.18, -width * 0.22)
    c.drawPath(hp, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width * 0.3, Color=col(lighten(color, 0.6), 0.6 * a),
                              StrokeCap=skia.Paint.kRound_Cap))


def cloud(c, x, y, s, a=1.0, color=(250, 252, 255), seed=0):
    parts = [(0, 0, 1.0), (-1.0, 0.25, 0.7), (1.05, 0.2, 0.75), (-0.45, -0.45, 0.72), (0.5, -0.5, 0.8)]
    p = None
    for dx, dy, r in parts:
        q = circle_path(x + dx * s, y + dy * s, r * s)
        p = q if p is None else union(p, q)
    cut = rrect_path(x - 3 * s, y + 0.5 * s, 6 * s, 3 * s, 0)
    p = skia.Op(p, cut, skia.PathOp.kDifference_PathOp)
    shape(c, p, color, a, light=0.1, dark=0.18, rim=s * 0.08)


def hill(c, pts_y, x0, x1, base, color, seed=0, a=1.0):
    """A smooth ridge through heights pts_y spread across x0..x1, filled down to `base`."""
    n = len(pts_y)
    xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]
    p = skia.Path()
    p.moveTo(x0, base)
    p.lineTo(xs[0], pts_y[0])
    for i in range(1, n):
        mx = (xs[i - 1] + xs[i]) / 2
        p.cubicTo(mx, pts_y[i - 1], mx, pts_y[i], xs[i], pts_y[i])
    p.lineTo(x1, base)
    p.close()
    shape(c, p, color, a, light=0.18, dark=0.25, rim=7)


def tree(c, x, y, s, color=(46, 160, 110), a=1.0, t=0.0, seed=0):
    sway = math.sin(t * 1.2 + seed) * s * 0.03
    shape(c, rrect_path(x - s * 0.07, y - s * 0.6, s * 0.14, s * 0.6, s * 0.05), (120, 80, 70), a, rim=s * 0.03)
    blob = union(circle_path(x + sway, y - s * 0.95, s * 0.42), circle_path(x - s * 0.25 + sway, y - s * 0.72, s * 0.3),
                 circle_path(x + s * 0.27 + sway, y - s * 0.74, s * 0.3))
    shape(c, blob, color, a, light=0.25, rim=s * 0.06)


def stargazer(c, x, y, s, t, a=1.0, look_up=1.0, shirt=(255, 196, 70)):
    """A small person standing on a hill, head tilted back, pointing at the sky."""
    tilt = -0.35 * look_up
    # legs
    for dx in (-0.12, 0.12):
        shape(c, rrect_path(x + dx * s - s * 0.07, y - s * 0.55, s * 0.14, s * 0.55, s * 0.07), (60, 70, 120), a, rim=s * 0.03)
    body = rrect_path(x - s * 0.24, y - s * 1.15, s * 0.48, s * 0.66, s * 0.2)
    shape(c, body, shirt, a, rim=s * 0.05)
    # arm pointing up
    arm = skia.Path()
    ax, ay = x + s * 0.18, y - s * 1.0
    ang = -1.15 + 0.08 * math.sin(t * 2)
    hx, hy = ax + s * 0.62 * math.cos(ang), ay + s * 0.62 * math.sin(ang)
    arm.moveTo(ax, ay)
    arm.lineTo(hx, hy)
    c.drawPath(arm, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=s * 0.13, Color=col(shade(shirt, 0.9), a),
                               StrokeCap=skia.Paint.kRound_Cap))
    c.drawCircle(hx, hy, s * 0.08, skia.Paint(AntiAlias=True, Color=col((240, 190, 150), a)))
    # head
    hx0, hy0 = x + s * 0.02, y - s * 1.42
    shape(c, circle_path(hx0, hy0, s * 0.27), (240, 190, 150), a, rim=s * 0.04)
    hair = skia.Path()
    hair.addArc(skia.Rect(hx0 - s * 0.29, hy0 - s * 0.31, hx0 + s * 0.29, hy0 + s * 0.27), 160 + math.degrees(tilt) * 0.5, 200)
    c.drawPath(hair, skia.Paint(AntiAlias=True, Color=col((70, 44, 40), a)))
    for sx in (-1, 1):
        c.drawCircle(hx0 + sx * s * 0.09 + s * 0.04, hy0 - s * 0.02 + tilt * s * 0.12, s * 0.035, skia.Paint(AntiAlias=True, Color=col(INK, a)))
    m = skia.Path()
    m.moveTo(hx0 - s * 0.06 + s * 0.04, hy0 + s * 0.1)
    m.quadTo(hx0 + s * 0.04, hy0 + s * 0.16, hx0 + s * 0.14, hy0 + s * 0.1)
    c.drawPath(m, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=s * 0.03, Color=col(INK, a),
                             StrokeCap=skia.Paint.kRound_Cap))
    return (hx0 + s * 0.04, hy0 - s * 0.02)


def sun(c, x, y, r, t, a=1.0, color=SUN_Y, corona=1.0):
    glow(c, x, y, r * 4.0 * corona, lighten(color, 0.2), 0.45 * a)
    glow(c, x, y, r * 2.0, (255, 240, 200), 0.6 * a)
    # gentle corona rays
    for k in range(14):
        ang = k / 14 * 2 * math.pi + t * 0.05
        L = r * (1.25 + 0.12 * math.sin(t * 1.3 + k * 1.7))
        p = poly_path([(x + r * 0.9 * math.cos(ang - 0.12), y + r * 0.9 * math.sin(ang - 0.12)), (x + L * math.cos(ang), y + L * math.sin(ang)),
                       (x + r * 0.9 * math.cos(ang + 0.12), y + r * 0.9 * math.sin(ang + 0.12))])
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=col(lighten(color, 0.3), 0.35 * a * corona)))
    sh = skia.GradientShader.MakeRadial(skia.Point(x - r * 0.3, y - r * 0.3), r * 1.4, [c4((255, 252, 230), a), c4(color, a), c4(SUN_O, a)],
                                        [0, 0.55, 1])
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=sh))
    rr = rng("sunspots")
    for k in range(9):
        px, py = rr.uniform(-0.6, 0.6, 2) * r
        if px * px + py * py < (0.8 * r) ** 2:
            c.drawCircle(x + px, y + py, r * rr.uniform(0.05, 0.12), skia.Paint(AntiAlias=True, Color=col(SUN_O, 0.25 * a)))


def planet(c, x, y, r, kind, t, a=1.0, atmo=1.0, light_dir=(-1, -0.3)):
    """Earth or Mars, with a glowing atmosphere rim and a soft night side."""
    if kind == "earth":
        base, land, glow_c = (40, 110, 230), (70, 200, 120), (110, 190, 255)
    else:
        base, land, glow_c = (210, 110, 70), (170, 80, 55), (240, 180, 120)
    if atmo > 0:
        glow(c, x, y, r * 1.25, glow_c, 0.55 * a * atmo)
        c.drawCircle(x, y, r * 1.04, skia.Paint(AntiAlias=True, Color=col(glow_c, 0.35 * a * atmo)))
    c.save()
    clip = circle_path(x, y, r)
    c.clipPath(clip, skia.ClipOp.kIntersect, True)
    sh = skia.GradientShader.MakeRadial(skia.Point(x - r * 0.4, y - r * 0.4), r * 1.6, [c4(lighten(base, 0.25), a), c4(base, a)])
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=sh))
    rr = rng("land", kind)
    for k in range(9 if kind == "earth" else 14):
        px, py = rr.uniform(-1, 1, 2) * r
        px += (t * r * 0.01) % (2 * r) - r * 0.0
        bs = r * rr.uniform(0.15, 0.4)
        blob = union(circle_path(px + x, py + y, bs), circle_path(px + x + bs * 0.6, py + y + bs * 0.3, bs * 0.7),
                     circle_path(px + x - bs * 0.5, py + y + bs * 0.4, bs * 0.6))
        if kind == "earth":
            c.drawPath(blob, skia.Paint(AntiAlias=True, Color=col(land, a)))
        else:
            c.drawCircle(px + x, py + y, bs * 0.4, skia.Paint(AntiAlias=True, Color=col(land, a * 0.7)))
    if kind == "earth":
        for k in range(6):
            px, py = rr.uniform(-1, 1, 2) * r
            c.drawOval(skia.Rect(x + px - r * 0.3, y + py - r * 0.05, x + px + r * 0.3, y + py + r * 0.05),
                       skia.Paint(AntiAlias=True, Color=col(WHITE, 0.55 * a)))
    # night side
    lx, ly = light_dir
    sh = skia.GradientShader.MakeLinear([skia.Point(x + lx * r * 0.2, y + ly * r * 0.2), skia.Point(x - lx * r, y - ly * r)],
                                        [c4((0, 0, 20), 0), c4((0, 0, 20), 0.78 * a)])
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=sh))
    c.restore()


def arrow(c, x0, y0, x1, y1, color, w=10, a=1.0, head=30):
    ang = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - head * 0.8 * math.cos(ang), y1 - head * 0.8 * math.sin(ang)
    c.drawLine(x0, y0, bx, by, skia.Paint(AntiAlias=True, StrokeWidth=w, Color=col(color, a), StrokeCap=skia.Paint.kRound_Cap))
    p = poly_path([(x1, y1), (x1 - head * math.cos(ang - 0.45), y1 - head * math.sin(ang - 0.45)),
                   (x1 - head * math.cos(ang + 0.45), y1 - head * math.sin(ang + 0.45))])
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=col(color, a)))


def pill(c, s, x, y, color, a=1.0, size=40, fg=WHITE, pad=26):
    """A rounded label tag."""
    f = font(size, 900)
    w = f.measureText(s) + pad * 2
    h = size * 1.45
    shape(c, rrect_path(x - w / 2, y - h / 2, w, h, h / 2), color, a, rim=4)
    text(c, s, x, y + size * 0.36, size, fg, a, shadow=0)
    return w
