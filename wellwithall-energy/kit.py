"""Drawing kit for the WellWithAll Energy brand reel (Henki-style flat motion design).

  * Brand palette sampled from wellwithall.com (logo green, headline pink, the four flavour colours)
  * Flat fruit illustrations (strawberry, lemon, peach, mango, pineapple) with one highlight each
  * Zig-zag starbursts, bubbles, sticker badges, doodle-pattern energy cans
  * Poppins type (the site's typeface) with spring pops and slide-ins
"""
import math, os

import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette
GREEN = (20, 63, 38)          # logo
PINK = (251, 37, 94)          # "FEEL-GOOD ENERGY" headline
CREAM = (255, 249, 236)
WHITE = (255, 255, 255)
RED = (230, 57, 70)
CORAL = (244, 120, 104)
YELLOW = (255, 214, 64)
LEMON = (255, 236, 120)
ORANGE = (247, 147, 30)
MANGO = (255, 176, 46)
LIME = (190, 230, 90)
LEAF = (64, 168, 74)
BLUSH = (255, 196, 206)
PEACHY = (255, 190, 130)

# the four flavours: name, can colour, doodle colour, photo background, fruit
FLAVOURS = {
    "strawberry_lemonade": dict(name="Strawberry Lemonade", can=LEMON, ink=PINK, bg=(252, 233, 121), fruit="strawberry"),
    "fruit_punch": dict(name="Fruit Punch", can=RED, ink=BLUSH, bg=(252, 215, 220), fruit="pineapple"),
    "peach": dict(name="Peach", can=CORAL, ink=(255, 222, 205), bg=(248, 200, 120), fruit="peach"),
    "tropical_mango": dict(name="Tropical Mango", can=ORANGE, ink=LEMON, bg=(220, 240, 150), fruit="mango"),
}
ORDER = ["strawberry_lemonade", "fruit_punch", "peach", "tropical_mango"]

FONTS = {"semibold": "Poppins-SemiBold.ttf", "bold": "Poppins-Bold.ttf", "xbold": "Poppins-ExtraBold.ttf",
         "black": "Poppins-Black.ttf"}
_TF, _F, _IMG = {}, {}, {}


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


def out_back(x, s=2.2):
    x = clamp(x) - 1
    return 1 + x * x * ((s + 1) * x + s)


def spring(u, k=6.0, w=13.0):
    """0 -> 1 with an overshoot wobble: the 'pop' every element enters with."""
    u = max(0.0, u)
    return 1 - math.exp(-k * u) * math.cos(w * u)


def pop(t, t0, dur=0.45):
    return spring((t - t0) / dur) if t >= t0 else 0.0


def mix(a, b, u):
    return tuple(int(round(x + (y - x) * u)) for x, y in zip(a, b))


# ---------------------------------------------------------------- paint and type
def col(rgb, a=255):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(clamp(a, 0, 255)))


def paint(rgb, a=255, stroke=0.0, cap=skia.Paint.kRound_Cap):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def font(kind, size):
    if kind not in _TF:
        _TF[kind] = skia.Typeface.MakeFromFile(os.path.join(HERE, "fonts", FONTS[kind]))
    key = (kind, round(size, 1))
    if key not in _F:
        f = skia.Font(_TF[kind], size)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        f.setSubpixel(True)
        _F[key] = f
    return _F[key]


def text_w(s, kind, size, tracking=0.0):
    return font(kind, size).measureText(s) + tracking * size * max(len(s) - 1, 0)


def text(c, s, x, y, size, kind="black", rgb=GREEN, a=255, align="center", tracking=-0.02):
    """Baseline-anchored text; tracking in ems (Poppins Black sets tight)."""
    f = font(kind, size)
    w = text_w(s, kind, size, tracking)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    p = paint(rgb, a)
    if tracking == 0:
        c.drawString(s, x0, y, f, p)
        return w
    for ch in s:
        c.drawString(ch, x0, y, f, p)
        x0 += f.measureText(ch) + tracking * size
    return w


def cap_h(size):
    return size * 0.70          # Poppins cap height ~0.70 em


def fit(s, kind, size, max_w, tracking=-0.02):
    w = text_w(s, kind, size, tracking)
    return size if w <= max_w else size * max_w / w


# ---------------------------------------------------------------- images
def image(name):
    if name not in _IMG:
        _IMG[name] = skia.Image.open(os.path.join(HERE, "source", name))
    return _IMG[name]


def logo(tint=GREEN):
    """The stacked wellwithall logo, ink keyed out of its white background and recoloured."""
    key = ("logo", tint)
    if key not in _IMG:
        from PIL import Image
        g = np.asarray(Image.open(os.path.join(HERE, "source", "logo_stacked.png")).convert("L"), np.float32)
        alpha = np.clip((235 - g) / (235 - 30), 0, 1)
        h, w = g.shape
        rgba = np.zeros((h, w, 4), np.uint8)
        rgba[..., 0], rgba[..., 1], rgba[..., 2] = tint
        rgba[..., 3] = (alpha * 255).astype(np.uint8)
        _IMG[key] = skia.Image.fromarray(rgba, colorType=skia.ColorType.kRGBA_8888_ColorType)
    return _IMG[key]


def draw_image(c, img, cx, cy, w, h=None, a=255, src=None):
    h = h if h is not None else w * img.height() / img.width()
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(clamp(a / 255))
    src = src or skia.Rect.MakeWH(img.width(), img.height())
    c.drawImageRect(img, src, skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h),
                    skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)


# ---------------------------------------------------------------- shapes
def star_path(cx, cy, r_out, r_in, n, rot=0.0):
    p = skia.Path()
    for k in range(2 * n):
        r = r_out if k % 2 == 0 else r_in
        a = rot + k * math.pi / n
        (p.moveTo if k == 0 else p.lineTo)(cx + r * math.cos(a), cy + r * math.sin(a))
    p.close()
    return p


def starburst(c, cx, cy, rings, n=12, rot=0.0, depth=0.22):
    """Concentric zig-zag stars, outermost first: rings = [(radius, rgb), ...]."""
    for r, rgb in rings:
        c.drawPath(star_path(cx, cy, r, r * (1 - depth), n, rot), paint(rgb))


def blob(cx, cy, r, seed=0, wob=0.12, n=7, t=0.0):
    """Soft organic splat: a circle with a few low-frequency bumps (the Henki fruit-splash shapes)."""
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 2 * math.pi, 3)
    p = skia.Path()
    steps = 72
    for k in range(steps + 1):
        a = 2 * math.pi * k / steps
        rr = r * (1 + wob * (math.sin(n * a + ph[0] + t) * 0.6 + math.sin(3 * a + ph[1] - t) * 0.4))
        (p.moveTo if k == 0 else p.lineTo)(cx + rr * math.cos(a), cy + rr * math.sin(a))
    p.close()
    return p


def bubble(c, x, y, r, rgb=WHITE, a=200):
    c.drawCircle(x, y, r, paint(rgb, a, stroke=max(2.0, r * 0.16)))
    c.drawCircle(x - r * 0.35, y - r * 0.35, r * 0.18, paint(rgb, a))


def badge(c, cx, cy, r, lines, rot=0.0, fill=PINK, ink=WHITE, n=14):
    """Spiky sticker with 1-2 lines of text, rotated (the Henki 'NEW' sticker)."""
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.drawPath(star_path(0, 0, r, r * 0.84, n, 0), paint(fill))
    size = r * (0.42 if len(lines) == 1 else 0.34)
    y0 = -(len(lines) - 1) * size * 0.5 + cap_h(size) / 2
    for i, s in enumerate(lines):
        sz = fit(s, "black", size, r * 1.45)
        text(c, s, 0, y0 + i * size * 1.0, sz, rgb=ink)
    c.restore()


# ---------------------------------------------------------------- fruit (drawn around (0, 0), unit radius ~ s)
def _shine(c, x, y, rx, ry, rot=-30, a=150):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.drawOval(skia.Rect.MakeXYWH(-rx, -ry, 2 * rx, 2 * ry), paint(WHITE, a))
    c.restore()


def _leaf(c, x, y, s, rot, rgb=LEAF):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    p = skia.Path()
    p.moveTo(0, 0)
    p.quadTo(s * 0.5, -s * 0.45, s, 0)
    p.quadTo(s * 0.5, s * 0.45, 0, 0)
    c.drawPath(p, paint(rgb))
    c.restore()


def strawberry(c, s):
    p = skia.Path()
    p.moveTo(0, s * 1.0)
    p.cubicTo(-s * 0.55, s * 0.75, -s * 1.0, s * 0.05, -s * 0.85, -s * 0.45)
    p.cubicTo(-s * 0.7, -s * 0.85, s * 0.7, -s * 0.85, s * 0.85, -s * 0.45)
    p.cubicTo(s * 1.0, s * 0.05, s * 0.55, s * 0.75, 0, s * 1.0)
    c.drawPath(p, paint(RED))
    _shine(c, -s * 0.45, -s * 0.2, s * 0.1, s * 0.28, rot=20, a=170)
    for x, y in [(-.35, .1), (.05, -.15), (.4, .05), (-.1, .4), (.25, .45), (-.5, -.3), (.55, -.35), (.05, .75)]:
        c.drawOval(skia.Rect.MakeXYWH(x * s - s * .035, y * s - s * .05, s * .07, s * .1), paint(LEMON))
    star = star_path(0, -s * 0.62, s * 0.5, s * 0.2, 5, -math.pi / 2)
    c.drawPath(star, paint(LEAF))
    c.drawRect(skia.Rect.MakeXYWH(-s * 0.05, -s * 1.0, s * 0.1, s * 0.32), paint(LEAF))


def lemon(c, s):
    p = skia.Path()
    p.moveTo(-s * 1.05, 0)
    p.cubicTo(-s * 0.85, -s * 0.85, s * 0.85, -s * 0.85, s * 1.05, 0)
    p.cubicTo(s * 0.85, s * 0.85, -s * 0.85, s * 0.85, -s * 1.05, 0)
    c.drawPath(p, paint(YELLOW))
    _shine(c, -s * 0.35, -s * 0.32, s * 0.28, s * 0.09, rot=-12, a=170)


def peach(c, s):
    c.drawCircle(0, 0, s, paint(PEACHY))
    c.drawCircle(s * 0.25, s * 0.15, s * 0.78, paint(CORAL, 150))
    p = skia.Path()
    p.moveTo(-s * 0.05, -s * 0.95)
    p.quadTo(-s * 0.45, -s * 0.1, -s * 0.1, s * 0.7)
    c.drawPath(p, paint((214, 90, 82), 200, stroke=s * 0.07))
    _leaf(c, s * 0.05, -s * 0.95, s * 0.75, -25)
    _shine(c, -s * 0.5, -s * 0.35, s * 0.12, s * 0.25, rot=25, a=150)


def mango(c, s):
    p = skia.Path()
    p.moveTo(-s * 0.2, -s * 0.95)
    p.cubicTo(s * 0.9, -s * 1.05, s * 1.15, s * 0.35, s * 0.35, s * 0.9)
    p.cubicTo(-s * 0.35, s * 1.25, -s * 1.15, s * 0.6, -s * 0.95, -s * 0.1)
    p.cubicTo(-s * 0.85, -s * 0.6, -s * 0.6, -s * 0.9, -s * 0.2, -s * 0.95)
    c.drawPath(p, paint(MANGO))
    c.save()
    c.clipPath(p, doAntiAlias=True)
    c.drawCircle(s * 0.75, -s * 0.65, s * 0.8, paint((240, 90, 60), 170))
    c.restore()
    _leaf(c, -s * 0.2, -s * 0.95, s * 0.8, -150)
    _shine(c, -s * 0.5, 0, s * 0.11, s * 0.3, rot=15, a=150)


def pineapple(c, s):
    for k, rot in enumerate((-150, -115, -90, -65, -30)):
        _leaf(c, 0, -s * 0.75, s * (0.75 if k in (0, 4) else 0.95), rot, LEAF if k % 2 else (40, 130, 60))
    body = skia.RRect.MakeOval(skia.Rect.MakeXYWH(-s * 0.68, -s * 0.85, s * 1.36, s * 1.8))
    c.drawRRect(body, paint(YELLOW))
    c.save()
    c.clipRRect(body, doAntiAlias=True)
    for k in range(-6, 7):
        c.drawLine(k * s * 0.3 - s, -s, k * s * 0.3 + s, s, paint(ORANGE, 200, stroke=s * 0.05))
        c.drawLine(k * s * 0.3 + s, -s, k * s * 0.3 - s, s, paint(ORANGE, 200, stroke=s * 0.05))
    c.restore()
    _shine(c, -s * 0.35, -s * 0.25, s * 0.1, s * 0.3, rot=10, a=140)


FRUIT = {"strawberry": strawberry, "lemon": lemon, "peach": peach, "mango": mango, "pineapple": pineapple}


def fruit(c, kind, x, y, s, rot=0.0, scale=1.0):
    if scale <= 0.01:
        return
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(scale, scale)
    FRUIT[kind](c, s)
    c.restore()


# ---------------------------------------------------------------- the can
_DOODLES = {}


def _doodle_paths(seed, w, h):
    """Random squiggles, zig-zags, rings and arrows like the WellWithAll can art (built once per flavour)."""
    if seed in _DOODLES:
        return _DOODLES[seed]
    rng = np.random.default_rng(seed)
    paths = []
    cell = w / 3.2
    for gy in np.arange(cell * 0.5, h, cell):
        for gx in np.arange(cell * 0.4, w, cell):
            x, y = gx + rng.uniform(-cell * .2, cell * .2), gy + rng.uniform(-cell * .2, cell * .2)
            kind = rng.integers(0, 4)
            p = skia.Path()
            r = cell * rng.uniform(0.22, 0.34)
            if kind == 0:                                   # zig-zag
                p.moveTo(x - r, y)
                for k in range(1, 6):
                    p.lineTo(x - r + 2 * r * k / 5, y + (r * 0.5 if k % 2 else -r * 0.5))
            elif kind == 1:                                 # ring
                p.addCircle(x, y, r * 0.6)
            elif kind == 2:                                 # squiggle
                p.moveTo(x - r, y)
                for k in range(1, 4):
                    p.quadTo(x - r + (2 * k - 1) * r / 3, y + (r if k % 2 else -r) * 0.8, x - r + 2 * k * r / 3, y)
            else:                                           # little bolt
                p.moveTo(x - r * .3, y - r)
                p.lineTo(x + r * .2, y - r * .1)
                p.lineTo(x - r * .2, y + r * .1)
                p.lineTo(x + r * .3, y + r)
            paths.append(p)
    _DOODLES[seed] = paths
    return paths


def can(c, flavour, cx, cy, h, rot=0.0, squash=0.0):
    """Upright 12oz slim can, bottom-centre anchored at (cx, cy); squash > 0 flattens it on a beat."""
    f = FLAVOURS[flavour]
    w = h * 0.36
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(1 + squash * 0.6, 1 - squash)
    x0, y0 = -w / 2, -h
    body = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, w, h), w * 0.12, w * 0.12)
    c.drawRRect(body, paint((206, 210, 214)))
    c.save()
    c.clipRRect(body, doAntiAlias=True)
    top = h * 0.07
    label_top, split = y0 + top, y0 + h * 0.52
    c.drawRect(skia.Rect.MakeLTRB(x0, label_top, x0 + w, split), paint(WHITE))
    c.drawRect(skia.Rect.MakeLTRB(x0, split, x0 + w, -h * 0.03), paint(f["can"]))
    c.save()
    c.translate(x0, split)
    ink = paint(f["ink"], 255, stroke=w * 0.035)
    for p in _doodle_paths(ORDER.index(flavour) + 3, w, h * 0.47):
        c.drawPath(p, ink)
    c.restore()
    for k in range(5):                                       # silver top ridges
        c.drawLine(x0, y0 + top * (0.2 + 0.18 * k), x0 + w, y0 + top * (0.2 + 0.18 * k), paint((160, 166, 172), 255, stroke=1.5))
    text(c, "wellwithall.", 0, label_top + h * 0.075, w * 0.13, "bold", GREEN)
    text(c, "Energy", 0, label_top + h * 0.15, w * 0.24, "bold", (30, 30, 30), tracking=-0.03)
    pill_w = w * 0.78
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-pill_w / 2, label_top + h * 0.18, pill_w, h * 0.04), h * .02, h * .02)
    c.drawRRect(r, paint(f["can"] if f["can"] != LEMON else PINK))
    sz = fit(f["name"], "semibold", w * 0.085, pill_w * 0.9, 0)
    text(c, f["name"], 0, label_top + h * 0.18 + h * 0.02 + cap_h(sz) / 2, sz, "semibold", WHITE, tracking=0)
    for i, s in enumerate(["80mg Natural Caffeine", "No Added Sugars†"]):
        text(c, s, 0, label_top + h * (0.285 + i * 0.045), w * 0.07, "semibold", (60, 60, 60), tracking=0)
    # cylinder shading: dark edges, one specular stripe
    g = skia.GradientShader.MakeLinear([skia.Point(x0, 0), skia.Point(x0 + w, 0)],
                                       [skia.Color(0, 0, 0, 70), skia.Color(0, 0, 0, 0), skia.Color(255, 255, 255, 90),
                                        skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 90)], [0, 0.25, 0.33, 0.6, 1.0])
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), skia.Paint(Shader=g))
    c.restore()
    c.restore()


# ---------------------------------------------------------------- frame
def new_canvas():
    surf = skia.Surface(W, H)
    return surf, surf.getCanvas()


def to_rgb(surf):
    return np.asarray(surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType))[..., :3]
