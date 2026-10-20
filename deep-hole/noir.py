"""Editorial-noir drawing kit: graphite void, engraved rock strata, the borehole, a depth gauge, line-art props.

Look rules: near-black graphite, warm off-white linework, ONE accent (ember orange) for heat, the hole and emphasis;
a cold steel blue appears only for water. Fine lines, mono labels, film grain and halation from the post pass.
"""
import math

import numpy as np
import skia

from engine import H, W, clamp, lerp, mix, prog, smooth, in_out, out_cubic
from premium import add, light
from typo import ASH, EMBER, PAPER, Counter, font, label, paint

VOID = (9, 9, 10)
GRAPHITE = (22, 21, 22)
SMOKE = (40, 38, 37)
STEEL = (128, 170, 205)          # water only
HOT = (255, 186, 120)


def hsh(*a):
    """Deterministic hash -> 0..1."""
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return (h % 100003) / 100003.0


def stroke(rgb, w, a=255, plus=False):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=skia.Paint.kRound_Cap,
                   StrokeJoin=skia.Paint.kRound_Join, Color=skia.Color(*[int(x) for x in rgb], int(clamp(a / 255) * 255)))
    if plus:
        p.setBlendMode(skia.BlendMode.kPlus)
    return p


def fillp(rgb, a=255):
    return skia.Paint(AntiAlias=True, Color=skia.Color(*[int(x) for x in rgb], int(clamp(a / 255) * 255)))


def grad_v(y0, y1, c0, c1, a0=255, a1=255):
    return skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, y0), (0, y1)], [skia.Color(*c0, int(a0)), skia.Color(*c1, int(a1))]))


def void(c, t, warm=0.0, cold=0.0):
    c.drawPaint(fillp(VOID))
    c.drawRect(skia.Rect.MakeWH(W, H), grad_v(0, H, (14, 13, 14), (7, 7, 8)))
    if warm > 0:
        light(c, W / 2, H * 0.75, 1100, (120, 50, 20), 90 * warm)
    if cold > 0:
        light(c, W / 2, H * 0.3, 1000, (30, 50, 70), 90 * cold)


class Dust:
    """Fine floating particles; a few large out-of-focus ones near the lens."""

    def __init__(self, n=90, seed=3, rgb=PAPER):
        r = np.random.default_rng(seed)
        self.p = r.random((n, 2)) * [W, H]
        self.z = r.random(n) ** 2
        self.v = r.uniform(-1, 1, (n, 2)) * [8, 12]
        self.ph = r.random(n) * 6.28
        self.rgb = rgb

    def draw(self, c, t, a=1.0, scroll=0.0):
        for i in range(len(self.z)):
            z = self.z[i]
            x = (self.p[i, 0] + self.v[i, 0] * t + 14 * math.sin(t * 0.4 + self.ph[i])) % W
            y = (self.p[i, 1] + self.v[i, 1] * t - scroll * (0.3 + z * 1.4)) % H
            r = 1.0 + z * 9
            al = (70 + 90 * (1 - z)) * a * (0.6 + 0.4 * math.sin(t * 1.3 + self.ph[i]))
            if z > 0.6:
                c.drawCircle(x, y, r * 2.2, paint(self.rgb, al * 0.25, r * 1.1))
            else:
                c.drawCircle(x, y, r * 0.6, paint(self.rgb, al))


class Snow:
    def __init__(self, n=160, seed=8):
        r = np.random.default_rng(seed)
        self.p = r.random((n, 2)) * [W, H]
        self.z = r.random(n)
        self.ph = r.random(n) * 6.28

    def draw(self, c, t, a=1.0, wind=40.0):
        for i in range(len(self.z)):
            z = self.z[i]
            sp = 40 + 120 * z
            x = (self.p[i, 0] + wind * (0.5 + z) * t + 20 * math.sin(t * 0.8 + self.ph[i])) % (W + 40) - 20
            y = (self.p[i, 1] + sp * t) % (H + 40) - 20
            r = 1.2 + 4.5 * z ** 2
            c.drawCircle(x, y, r, paint((230, 232, 236), (90 + 140 * z) * a, 0.6 + 2.5 * z ** 3))


# ---------------------------------------------------------------- the rock column
# (top m, bottom m, name, colour, texture)
LAYERS = [
    (0, 120, "MORAINE & PERMAFROST", (52, 48, 46), "grain"),
    (120, 1800, "SANDSTONE · DOLOMITE", (46, 41, 37), "bed"),
    (1800, 4600, "BASALT · DIABASE", (36, 34, 36), "crystal"),
    (4600, 6840, "TUFF · BLACK SHALE", (31, 28, 28), "hatch"),
    (6840, 9600, "ARCHEAN GNEISS", (44, 36, 33), "wave"),
    (9600, 40000, "GRANITE-GNEISS", (50, 38, 32), "crystal"),
]


FULL = dict(d=6131.0, ppm=0.095, cy=800.0)        # the whole hole on screen (y 218 .. 1382)


class Section:
    """Cross-section camera: depth `d` (m) at screen centre, `ppm` pixels per metre, horizontal offset `x` (m)."""

    def __init__(self, d=0.0, ppm=1.0, x=0.0, cy=H / 2):
        self.d, self.ppm, self.x, self.cy = d, ppm, x, cy

    def sy(self, depth):
        return self.cy + (depth - self.d) * self.ppm

    def sx(self, xm):
        return W / 2 + (xm - self.x) * self.ppm

    def depth_at(self, y):
        return self.d + (y - self.cy) / self.ppm


def _lod_alpha(px):
    """Visibility of a texture level whose cell is `px` pixels on screen."""
    return smooth(prog(px, 10, 26)) * (1 - smooth(prog(px, 150, 320)))


def strata(c, cam, t, heat=1.0, soft=0.0, labels=1.0, sky=True, x0=0, x1=W):
    """Engraved rock column filling [x0, x1]. soft > 0 makes the deep rock sag and flow like hot plastic."""
    ytop = cam.sy(0)
    if sky and ytop > 0:
        c.drawRect(skia.Rect.MakeLTRB(x0, 0, x1, ytop), grad_v(0, max(ytop, 1), (8, 9, 12), (16, 17, 22)))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, max(0, ytop), x1, H))
    for top, bot, name, rgb, tex in LAYERS:
        y0, y1 = cam.sy(top), cam.sy(bot)
        if y1 < 0 or y0 > H:
            continue
        r0 = lighten_(rgb, 0.10)
        c.drawRect(skia.Rect.MakeLTRB(x0, max(-10, y0), x1, min(H + 10, y1)), grad_v(y0, y1, r0, rgb))
        _texture(c, cam, t, top, bot, tex, rgb, soft, x0, x1)
    # heat: the deep rock glows
    if heat > 0:
        yh0, yh1 = cam.sy(5000), cam.sy(12500)
        if yh1 > 0 and yh0 < H:
            c.drawRect(skia.Rect.MakeLTRB(x0, max(0, yh0), x1, H),
                       skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, yh0), (0, yh1)],
                                  [skia.Color(255, 80, 25, 0), skia.Color(255, 80, 25, int(55 * heat))]),
                                  BlendMode=skia.BlendMode.kPlus))
    c.restore()
    # layer boundaries + labels
    for top, bot, name, rgb, tex in LAYERS:
        y = cam.sy(top)
        if top == 0 or not (-20 < y < H + 20):
            continue
        _boundary(c, cam, t, top, soft, x0, x1)
        if labels > 0:
            label(c, name, min(x1, W) - 175, y + 34, 21, "mono", ASH, 200 * labels, align="right", tracking=0.06)
    if 0 <= ytop <= H:
        c.drawLine(x0, ytop, x1, ytop, stroke(PAPER, 2.5, 200))


def lighten_(rgb, k):
    return tuple(int(v + (255 - v) * k) for v in rgb)


def _wavy_y(xs, y, amp, f, ph):
    return y + amp * np.sin(xs * f + ph)


def _boundary(c, cam, t, depth, soft, x0, x1):
    xs = np.linspace(x0, x1, 60)
    amp = 3 + 0.004 * cam.ppm * 400
    deep = clamp((depth - 6000) / 6000)
    ph = hsh(depth) * 6.28 + soft * deep * t * 1.6
    ys = _wavy_y(xs, cam.sy(depth), amp + soft * deep * 40, 0.012, ph)
    p = skia.Path()
    p.moveTo(xs[0], ys[0])
    for x, y in zip(xs[1:], ys[1:]):
        p.lineTo(x, y)
    c.drawPath(p, stroke((120, 112, 104), 2, 170))


def _texture(c, cam, t, top, bot, tex, rgb, soft, x0, x1):
    line_rgb = lighten_(rgb, 0.35)
    for S in (5, 40, 320, 2560):                       # metres per texture cell, one level per zoom range
        px = S * cam.ppm
        la = _lod_alpha(px)
        if la <= 0.02:
            continue
        d0 = max(top, cam.depth_at(-px))
        d1 = min(bot, cam.depth_at(H + px))
        if d1 <= d0:
            continue
        k0, k1 = int(d0 // S), int(d1 // S) + 1
        xm0 = cam.x + (x0 - W / 2) / cam.ppm
        xm1 = cam.x + (x1 - W / 2) / cam.ppm
        i0, i1 = int(xm0 // S) - 1, int(xm1 // S) + 1
        if (k1 - k0) * (i1 - i0) > 1600:
            continue
        for k in range(k0, k1):
            yk = cam.sy(k * S)
            deep = clamp((k * S - 6000) / 6000)
            sag = soft * deep
            if tex in ("bed", "wave") and k * S >= top:
                xs = np.linspace(x0, x1, 40)
                amp = (0.18 if tex == "bed" else 0.32) * px + sag * 30
                ys = _wavy_y(xs, yk, amp * (0.4 + 0.6 * hsh(k, S)), 6.0 / max(px * 6, 1), hsh(k, S, 7) * 6.28 + sag * t * 1.4)
                p = skia.Path()
                p.moveTo(xs[0], ys[0])
                for x, y in zip(xs[1:], ys[1:]):
                    p.lineTo(x, y)
                c.drawPath(p, stroke(line_rgb, 1.3, 120 * la))
            for i in range(i0, i1):
                hx = hsh(i, k, S, 1)
                if tex == "grain":
                    for j in range(3):
                        x = cam.sx((i + hsh(i, k, S, j, 2)) * S) + sag * 20 * math.sin(t + k)
                        y = cam.sy((k + hsh(i, k, S, j, 3)) * S)
                        c.drawCircle(x, y, 0.06 * px + 0.8, fillp(line_rgb, 130 * la))
                elif tex == "crystal" and hx < 0.7:
                    x = cam.sx((i + hsh(i, k, S, 4)) * S) + sag * 24 * math.sin(t * 1.3 + i)
                    y = cam.sy((k + hsh(i, k, S, 5)) * S)
                    r = px * (0.12 + 0.12 * hsh(i, k, S, 6))
                    an = hsh(i, k, S, 7) * 3.14
                    pts = [(x + math.cos(an + q * 1.5708) * r * (1.0 if q % 2 else 0.55), y + math.sin(an + q * 1.5708) * r * (1.0 if q % 2 else 0.55)) for q in range(4)]
                    p = skia.Path()
                    p.addPoly(pts, True)
                    c.drawPath(p, stroke(line_rgb, 1.2, 140 * la))
                elif tex == "hatch" and hx < 0.6:
                    x = cam.sx((i + hsh(i, k, S, 4)) * S)
                    y = cam.sy((k + hsh(i, k, S, 5)) * S) + sag * 20 * math.sin(t + i)
                    L = px * 0.28
                    for q in range(3):
                        c.drawLine(x + q * px * 0.08, y, x + q * px * 0.08 + L * 0.6, y - L, stroke(line_rgb, 1.2, 120 * la))


def hole(c, cam, depth, t, width_m=0.23, glow=1.0, bit=True):
    """The borehole from the surface down to `depth` metres, with a hot drill bit at its tip."""
    x = cam.sx(0)
    y0, y1 = max(-20, cam.sy(0)), cam.sy(depth)
    if y1 < -20:
        return
    y1c = min(y1, H + 40)
    w = max(3.0, width_m * cam.ppm)
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2, y0, x + w / 2, y1c), fillp((4, 3, 3)))
    gp = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([(0, y0), (0, y1c)],
                    [skia.Color(255, 96, 38, int(60 * glow)), skia.Color(255, 120, 50, int(230 * glow))]))
    gp.setBlendMode(skia.BlendMode.kPlus)
    gp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6 + w * 0.3))
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2 - 3, y0, x + w / 2 + 3, y1c), gp)
    c.drawLine(x - w / 2, y0, x - w / 2, y1c, stroke(EMBER, 1.6, 200 * glow))
    c.drawLine(x + w / 2, y0, x + w / 2, y1c, stroke(EMBER, 1.6, 200 * glow))
    if bit and y1 < H + 40:
        light(c, x, y1, 90 + w, (255, 120, 50), 230 * glow)
        light(c, x, y1, 26 + w * 0.5, HOT, 255 * glow)
        for i in range(10):              # sparks
            u = (t * 2.3 + i / 10) % 1.0
            an = -math.pi / 2 + (hsh(i, 9) - 0.5) * 2.6
            r = 18 + 90 * u
            c.drawCircle(x + math.cos(an) * r, y1 + math.sin(an) * r * 0.6 + 40 * u * u, 2.2 * (1 - u), add(HOT, 255 * (1 - u) * glow))


def gauge(c, depth, t, a=1.0, temp=None, x=72, y=300):
    """Depth readout (top-left) and a ruler that scrolls with the depth."""
    if a <= 0.01:
        return
    label(c, "DEPTH", x, y, 22, "mono", ASH, 220 * a, tracking=0.25)
    txt = f"{int(depth):,}".replace(",", " ") + " m"
    label(c, txt, x, y + 62, 56, "mono_bold", PAPER, 255 * a)
    if temp is not None:
        label(c, "TEMP", x, y + 120, 22, "mono", ASH, 220 * a, tracking=0.25)
        label(c, f"{int(temp)} °C", x, y + 170, 44, "mono_bold", mix(PAPER, EMBER, clamp((temp - 60) / 120)), 255 * a)
    ry0, ry1 = y + 230, y + 1000            # ruler
    c.drawLine(x, ry0, x, ry1, stroke(ASH, 1.5, 120 * a))
    step = 100
    off = (depth % step) / step
    for i in range(-1, 12):
        yy = ry0 + (i - off) * (ry1 - ry0) / 10
        if ry0 <= yy <= ry1:
            big = (int(depth // step) + i) % 5 == 0
            c.drawLine(x, yy, x + (26 if big else 12), yy, stroke(PAPER if big else ASH, 1.5, 200 * a))
    c.drawPath(skia.Path().addPoly([(x + 34, ry0 + (ry1 - ry0) * 0.5), (x + 48, ry0 + (ry1 - ry0) * 0.5 - 8), (x + 48, ry0 + (ry1 - ry0) * 0.5 + 8)], True),
               fillp(EMBER, 255 * a))


def dim_line(c, x, y0, y1, a, txt=None, side=1, size=26, rgb=PAPER):
    """Vertical dimension line with end ticks and an optional label."""
    if a <= 0:
        return
    c.drawLine(x, y0, x, y1, stroke(rgb, 2, 220 * a))
    for y in (y0, y1):
        c.drawLine(x - 12, y, x + 12, y, stroke(rgb, 2, 220 * a))
    if txt:
        label(c, txt, x + side * 22, (y0 + y1) / 2 + size * 0.35, size, "mono_bold", rgb, 255 * a, align="left" if side > 0 else "right")


# ---------------------------------------------------------------- line-art props
def path_of(pts, closed=False):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def eiffel(c, x, yb, h, a=255, rgb=PAPER, w=2.0):
    """Line drawing of the Eiffel Tower, base centre (x, yb), height h px."""
    s = h / 330.0
    L = lambda u, v: (x + u * s, yb - v * s)       # noqa: E731  (u: half-width metres, v: height metres)
    legs = [(-62, 0), (-34, 57), (-22, 116), (-9, 276), (0, 330)]
    for side in (-1, 1):
        c.drawPath(path_of([L(side * abs(u), v) for u, v in legs]), stroke(rgb, w, a))
    for v, u in ((57, 34), (116, 22), (276, 9)):
        c.drawLine(*L(-u - 4, v), *L(u + 4, v), stroke(rgb, w, a))
    arc = skia.Path()
    arc.moveTo(*L(-50, 0))
    arc.quadTo(*L(0, 50), *L(50, 0))
    c.drawPath(arc, stroke(rgb, w * 0.8, a * 0.8))


def _ridge(n=160, seed=4):
    r = np.random.default_rng(seed)
    u = np.linspace(-1, 1, n)
    base = np.clip(1 - np.abs(u) ** 0.9, 0, 1)
    jag = np.zeros(n)
    for k, amp in ((5, 0.16), (13, 0.09), (31, 0.05)):
        jag += amp * np.interp(np.linspace(0, k, n), np.arange(k + 1), r.uniform(-1, 1, k + 1))
    v = np.clip(base + jag * (0.3 + base), 0, None)
    v[0] = v[-1] = 0
    v /= v.max()
    return u, v


_RIDGE = _ridge()


def everest(c, x, ytop, h, a=255, flip=True, rgb=PAPER, fill_a=0):
    """Mountain silhouette h px tall with a jagged ridge and snow line; flip=True hangs it summit-down."""
    u, v = _RIDGE
    wd = h * 0.38
    Y = (lambda vv: ytop + vv * h) if flip else (lambda vv: ytop + h - vv * h)    # noqa: E731
    pts = [(x + uu * wd, Y(vv)) for uu, vv in zip(u, v)]
    p = path_of(pts, closed=True)
    if fill_a:
        y0, y1 = (ytop, ytop + h)
        c.drawPath(p, grad_v(y0, y1, (70, 66, 64) if not flip else (36, 34, 34), (36, 34, 34) if not flip else (70, 66, 64), fill_a, fill_a))
    c.drawPath(p, stroke(rgb, 2.2, a))
    snow = [(x + uu * wd, Y(vv)) for uu, vv in zip(u, v) if vv > 0.72]
    if len(snow) > 1:
        c.drawPath(path_of(snow), stroke((255, 255, 255), 5, a))


def tower(c, x, gy, s, t, a=255):
    """The Kola drill site: tall derrick tower with a hall at its foot, a few lit windows."""
    dark = (14, 14, 17)
    c.drawRect(skia.Rect.MakeLTRB(x - 210 * s, gy - 120 * s, x + 230 * s, gy), fillp(dark, a))
    c.drawRect(skia.Rect.MakeLTRB(x - 60 * s, gy - 520 * s, x + 60 * s, gy - 100 * s), fillp(dark, a))
    c.drawPath(path_of([(x - 60 * s, gy - 520 * s), (x, gy - 590 * s), (x + 60 * s, gy - 520 * s)], True), fillp(dark, a))
    for k in range(9):                      # lattice
        y = gy - 120 * s - k * 44 * s
        c.drawLine(x - 60 * s, y, x + 60 * s, y - 44 * s, stroke((60, 58, 60), 1.4, a))
        c.drawLine(x + 60 * s, y, x - 60 * s, y - 44 * s, stroke((60, 58, 60), 1.4, a))
    for i in range(7):
        wx = x - 190 * s + i * 60 * s
        on = hsh(i, 4) > 0.35
        c.drawRect(skia.Rect.MakeXYWH(wx, gy - 80 * s, 26 * s, 34 * s), fillp((255, 170, 90) if on else (30, 30, 34), a * (0.85 if on else 1)))
        if on:
            light(c, wx + 13 * s, gy - 63 * s, 50 * s, (255, 140, 60), 90 * a / 255)
    bl = 0.5 + 0.5 * math.sin(t * 3.0)      # red aviation light
    light(c, x, gy - 600 * s, 40 * s, (255, 60, 40), 220 * bl * a / 255)
    c.drawCircle(x, gy - 600 * s, 4 * s, fillp((255, 90, 70), a))


def aurora(c, t, a=1.0):
    for k in range(3):
        p = skia.Path()
        xs = np.linspace(-100, W + 100, 50)
        ys = 380 + k * 70 + 60 * np.sin(xs * 0.004 + t * 0.15 + k) + 30 * np.sin(xs * 0.011 - t * 0.2)
        p.moveTo(xs[0], ys[0])
        for x, y in zip(xs[1:], ys[1:]):
            p.lineTo(x, y)
        pp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=120 - k * 30,
                        Color=skia.Color(70, 160, 140, int(28 * a)), BlendMode=skia.BlendMode.kPlus)
        pp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 50))
        c.drawPath(p, pp)


def stars(c, t, a=1.0, n=120, seed=2, ymax=900):
    r = np.random.default_rng(seed)
    pts = r.random((n, 2)) * [W, ymax]
    ph = r.random(n) * 6.28
    sz = r.random(n) ** 3 * 2.2 + 0.6
    for i in range(n):
        tw = 0.6 + 0.4 * math.sin(t * 1.5 + ph[i])
        c.drawCircle(pts[i, 0], pts[i, 1], sz[i], fillp((230, 232, 240), 200 * tw * a))


def plankton(c, x, y, r, kind, t, a=255, rgb=PAPER):
    """Line-art microfossils: radiolarian (spiky lattice sphere), diatom (ribbed disc), foram (chambered spiral)."""
    rot = t * 0.15 + hsh(kind, int(x)) * 6
    if kind == 0:
        c.drawCircle(x, y, r, stroke(rgb, 1.6, a))
        c.drawCircle(x, y, r * 0.62, stroke(rgb, 1.2, a * 0.7))
        for i in range(14):
            an = rot + i * 6.283 / 14
            c.drawLine(x + math.cos(an) * r, y + math.sin(an) * r, x + math.cos(an) * r * 1.45, y + math.sin(an) * r * 1.45, stroke(rgb, 1.4, a))
            c.drawCircle(x + math.cos(an + 0.22) * r * 0.81, y + math.sin(an + 0.22) * r * 0.81, r * 0.07, stroke(rgb, 1, a * 0.8))
    elif kind == 1:
        c.drawCircle(x, y, r, stroke(rgb, 1.8, a))
        for i in range(24):
            an = rot + i * 6.283 / 24
            c.drawLine(x + math.cos(an) * r * 0.25, y + math.sin(an) * r * 0.25, x + math.cos(an) * r * 0.95, y + math.sin(an) * r * 0.95, stroke(rgb, 1, a * 0.75))
        c.drawCircle(x, y, r * 0.22, stroke(rgb, 1.4, a))
    else:
        p = skia.Path()
        for i in range(60):
            an = rot + i * 0.2
            rr = r * 0.08 * math.exp(i * 0.04)
            q = (x + math.cos(an) * rr, y + math.sin(an) * rr)
            p.moveTo(*q) if i == 0 else p.lineTo(*q)
        c.drawPath(p, stroke(rgb, 1.6, a))
        for i in range(6):
            an = rot + i * 1.05
            rr = r * 0.08 * math.exp((i * 1.05 / 0.2) * 0.04)
            c.drawCircle(x + math.cos(an) * rr, y + math.sin(an) * rr, rr * 0.45, stroke(rgb, 1.2, a * 0.8))
