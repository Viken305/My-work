"""Basics for the GPS Short: frame size, palette, easing, fonts and text. The Frosted Glass look itself is in glass.py.

  * Amber = you and the signal; violet = time and Einstein; cyan = light and the blue dot
"""
import math, os

import skia

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "deep-hole", "fonts")

# ---------------------------------------------------------------- palette
from project import P, palette  # noqa: E402

CARBON = palette("carbon")
INK = palette("ink")
PAPER = palette("paper")
SMOKE = palette("smoke")
AMBER = palette("amber")      # you, your phone, the signal
VIOLET = palette("violet")    # time, clocks, Einstein
CYAN = palette("cyan")        # light, beams, the blue dot
CARD = palette("card")
FX = P["style"]["post"]       # dashboard multipliers for bloom, chromatic aberration, grain, refraction, caustics

FONTS = {
    "light": "InterDisplay-Light.otf", "regular": "InterDisplay-Regular.otf", "medium": "InterDisplay-Medium.otf",
    "semibold": "InterDisplay-SemiBold.otf", "bold": "InterDisplay-Bold.otf", "black": "InterDisplay-Black.otf",
    "serif": "NotoSerifDisplay-Italic.ttf", "serif_bold": "NotoSerifDisplay-BoldItalic.ttf",
    "mono": "NotoSansMono-Regular.ttf", "mono_bold": "NotoSansMono-Bold.ttf",
}
_TF, _F = {}, {}


# ---------------------------------------------------------------- basics
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    return 1.0 if t1 <= t0 and t >= t1 else clamp((t - t0) / (t1 - t0)) if t1 > t0 else 0.0


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


def spring(u, k=7.0, w=10.0):
    u = clamp(u)
    return 1 - math.exp(-k * u) * math.cos(w * u)


def mix(a, b, t):
    t = clamp(t)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def col(rgb, a=255):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(clamp(a / 255) * 255))


def paint(rgb, a=255, sigma=0.0, plus=False, stroke=0.0):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if sigma > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    if plus:
        p.setBlendMode(skia.BlendMode.kPlus)
    return p


def font(kind, size):
    key = (kind, round(size, 1))
    if key not in _F:
        if kind not in _TF:
            _TF[kind] = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, FONTS[kind]))
        f = skia.Font(_TF[kind], size)
        f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
        f.setSubpixel(True)
        _F[key] = f
    return _F[key]


def width(s, kind, size, tracking=0.0):
    f = font(kind, size)
    return sum(f.measureText(ch) for ch in s) + tracking * size * max(0, len(s) - 1)


def label(c, s, x, y, size, kind="medium", rgb=PAPER, a=255, align="left", tracking=0.0, sigma=0.0, plus=False):
    if a <= 1:
        return
    f = font(kind, size)
    w = width(s, kind, size, tracking)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    p = paint(rgb, a, sigma, plus)
    for ch in s:
        c.drawString(ch, x0, y, f, p)
        x0 += f.measureText(ch) + tracking * size
