""""Static & Signal" drawing kit for the AI image Short.

  * Warm carbon studio background with moving grain
  * Real-model images on floating cards with mono label strips
  * Colour static (Gaussian noise) mixed with images on the model's own noise schedule
  * Amber = your words (prompt box, token chips, attention threads); violet = the model (maths, steps, bars)
  * Post: bloom on amber/violet only, slight chromatic aberration, grain, vignette, motion blur
"""
import json, math, os

import cv2
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "deep-hole", "fonts")
RUNS = os.path.join(HERE, "data", "runs")
cv2.setNumThreads(1)

# ---------------------------------------------------------------- palette
from project import P, palette  # noqa: E402

CARBON = palette("carbon")
INK = palette("ink")
PAPER = palette("paper")
SMOKE = palette("smoke")
AMBER = palette("amber")      # your words
VIOLET = palette("violet")    # the model
CARD = palette("card")
FX = P["style"]["post"]       # dashboard multipliers for bloom, chromatic aberration, grain, glitch

FONTS = {
    "light": "InterDisplay-Light.otf", "regular": "InterDisplay-Regular.otf", "medium": "InterDisplay-Medium.otf", "semibold": "InterDisplay-SemiBold.otf",
    "bold": "InterDisplay-Bold.otf", "black": "InterDisplay-Black.otf",
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
    if sigma > 0.25:
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


# ---------------------------------------------------------------- images
_IMG = {}


def sk_image(arr):
    """uint8 HxWx3 -> skia.Image"""
    a = np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(a), colorType=skia.kRGBA_8888_ColorType)


def load(path):
    """Image from data/runs/<path> as float32 RGB 0..255 (cached)."""
    if path not in _IMG:
        _IMG[path] = cv2.cvtColor(cv2.imread(os.path.join(RUNS, path)), cv2.COLOR_BGR2RGB).astype(np.float32)
    return _IMG[path]


def meta(run):
    return json.load(open(os.path.join(RUNS, run, "meta.json")))


def static(seed, size=512, cell=1):
    """Colour TV static: Gaussian noise per pixel (mean grey), optionally blocky."""
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (size // cell, size // cell, 3)).astype(np.float32)
    if cell > 1:
        n = cv2.resize(n, (size, size), interpolation=cv2.INTER_NEAREST)
    return n


def noisy(img, noise, k):
    """Diffusion forward process in pixel space: k=0 clean, k=1 pure noise (cosine schedule)."""
    ab = math.cos(clamp(k) * math.pi / 2) ** 2
    x = img / 127.5 - 1
    return np.clip((math.sqrt(ab) * x + math.sqrt(1 - ab) * noise + 1) * 127.5, 0, 255)


def draw_img(c, arr, x, y, w, h=None, a=255, radius=18):
    """Draw an RGB float/uint8 array into a rounded rect."""
    h = h or w * arr.shape[0] / arr.shape[1]
    img = sk_image(np.clip(arr, 0, 255).astype(np.uint8))
    r = skia.Rect.MakeXYWH(x, y, w, h)
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(r, radius, radius), doAntiAlias=True)
    p = skia.Paint()
    p.setAlphaf(a / 255)
    c.drawImageRect(img, r, skia.SamplingOptions(skia.CubicResampler.Mitchell()), p)
    c.restore()


def card(c, arr, x, y, w, caption=None, a=255, glow=None, h=None):
    """A floating picture card: soft shadow, image, thin frame, mono caption strip below."""
    h = h or w * arr.shape[0] / arr.shape[1]
    r = skia.Rect.MakeXYWH(x, y, w, h)
    c.drawRRect(skia.RRect.MakeRectXY(r.makeOffset(0, 18), 22, 22), paint(INK, a * 0.8, sigma=26))
    if glow:
        c.drawRRect(skia.RRect.MakeRectXY(r, 22, 22), paint(glow, a * 0.5, sigma=30))
    draw_img(c, arr, x, y, w, h, a)
    c.drawRRect(skia.RRect.MakeRectXY(r, 18, 18), paint(PAPER, a * 0.55, stroke=1.6))
    if caption:
        label(c, caption, x + 4, y + h + 40, 22, "mono", SMOKE, a, tracking=0.12)


# ---------------------------------------------------------------- UI pieces
def prompt_box(c, text, x, y, w, a=255, typed=None, caret=True, t=0.0, size=34):
    """Amber-edged input box with mono text typed live."""
    if a <= 1:
        return
    s = text if typed is None else text[:int(typed)]
    lines, cur = [], ""
    for wd in s.split(" "):
        if width(cur + " " + wd, "mono", size) > w - 70 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    h = 60 + len(lines) * size * 1.35
    r = skia.Rect.MakeXYWH(x, y, w, h)
    c.drawRRect(skia.RRect.MakeRectXY(r, 20, 20), paint(CARD, a * 0.92))
    c.drawRRect(skia.RRect.MakeRectXY(r, 20, 20), paint(AMBER, a * 0.35, sigma=14, stroke=4))
    c.drawRRect(skia.RRect.MakeRectXY(r, 20, 20), paint(AMBER, a * 0.9, stroke=2))
    label(c, "PROMPT", x + 30, y - 16, 18, "mono_bold", AMBER, a, tracking=0.3)
    yy = y + 30 + size
    for ln in lines:
        label(c, ln, x + 34, yy, size, "mono", PAPER, a)
        yy += size * 1.35
    if caret and (int(t * 2.2) % 2 == 0 or (typed is not None and typed < len(text))):
        cx = x + 34 + width(lines[-1], "mono", size) + 6
        c.drawRect(skia.Rect.MakeXYWH(cx, yy - size * 1.35 - size * 0.8, size * 0.5, size * 0.95), paint(AMBER, a))
    return h


def chip(c, text, x, y, a=255, rgb=AMBER, size=34, fill=0.15):
    """Rounded token chip; returns its width."""
    w = width(text, "mono_bold", size) + 40
    r = skia.Rect.MakeXYWH(x, y, w, size * 1.7)
    c.drawRRect(skia.RRect.MakeRectXY(r, size * 0.6, size * 0.6), paint(rgb, a * fill))
    c.drawRRect(skia.RRect.MakeRectXY(r, size * 0.6, size * 0.6), paint(rgb, a, stroke=2))
    label(c, text, x + 20, y + size * 1.2, size, "mono_bold", rgb, a)
    return w


def barcode(c, vals, x, y, w, h, a=255, rgb=VIOLET):
    """An embedding as thin vertical bars around a midline (real values)."""
    v = np.asarray(vals, np.float32)
    v = v / (np.abs(v).max() + 1e-6)
    bw = w / len(v)
    mid = y + h / 2
    for i, q in enumerate(v):
        c.drawRect(skia.Rect.MakeLTRB(x + i * bw, mid - max(0, q) * h / 2, x + (i + 0.8) * bw, mid - min(0, q) * h / 2),
                   paint(mix(VIOLET, PAPER, abs(q) * 0.5) if rgb == VIOLET else rgb, a * (0.4 + 0.6 * abs(q))))


def heat(arr, m, rgb=AMBER, k=1.0):
    """Overlay a 16x16 attention map on an image as a soft amber glow (and dim the rest)."""
    m = cv2.resize(m.astype(np.float32), arr.shape[1::-1], interpolation=cv2.INTER_CUBIC)
    m = np.clip((m - m.min()) / (m.max() - m.min() + 1e-6), 0, 1)[..., None]
    out = arr * (1 - 0.6 * k + 0.6 * k * m)
    return np.clip(out + np.array(rgb, np.float32) * m * 0.55 * k, 0, 255)


def fig(c, n, text, x, y, a=255, align="left", size=20):
    label(c, f"FIG. {n} · {text}", x, y, size, "mono", SMOKE, a, align, 0.18)


_BG = None


def background(c, t=0.0):
    """Studio backdrop: a soft warm-violet glow behind centre, falling to ink (cached as an image)."""
    global _BG
    if _BG is None:
        s = skia.Surface(W, H)
        s.getCanvas().drawPaint(skia.Paint(Shader=skia.GradientShader.MakeRadial(
            (W / 2, H * 0.42), H * 0.75, [col(mix(CARBON, (30, 27, 40), 0.6)), col(CARBON), col(INK)], [0, 0.55, 1])))
        _BG = s.makeImageSnapshot()
    c.drawImage(_BG, 0, 0)


# ---------------------------------------------------------------- post
_GRAIN = _VIG = None


def post(img, t, bloom=1.0, ca=0.6, grain=6.0, glitch=0.0, flash=0.0):
    """img float32 HxWx3. Bloom only on amber and violet light. glitch: horizontal tearing bands + RGB split."""
    global _GRAIN, _VIG
    bloom, ca, grain, glitch = bloom * FX["bloom"], ca * FX["ca"], grain * FX["grain"], glitch * FX["glitch"]
    if _GRAIN is None:
        rng = np.random.default_rng(3)
        _GRAIN = [(rng.normal(0, 1, (H // 2, W // 2)) * grain).astype(np.float32) for _ in range(8)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _VIG = (1 - 0.55 * np.clip(r - 0.4, 0, 1) ** 1.4)[..., None].astype(np.float32)
    if bloom > 0:
        small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        mx = small.max(axis=2, keepdims=True)
        mn = small.min(axis=2, keepdims=True)
        sat = np.clip((mx - mn - 90) / 90, 0, 1) * np.clip((mx - 160) / 80, 0, 1)
        b1 = cv2.GaussianBlur(small * sat, (0, 0), 5)
        b2 = cv2.GaussianBlur(small * sat, (0, 0), 18)
        img = img + cv2.resize(b1 * 0.6 + b2 * 0.8, (W, H), interpolation=cv2.INTER_LINEAR) * bloom
    k = 0.0015 * ca
    if k > 0:
        Mr = np.float32([[1 + k, 0, -W / 2 * k], [0, 1 + k, -H / 2 * k]])
        Mb = np.float32([[1 - k, 0, W / 2 * k], [0, 1 - k, H / 2 * k]])
        img = img.copy()
        img[..., 0] = cv2.warpAffine(img[..., 0], Mr, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img[..., 2] = cv2.warpAffine(img[..., 2], Mb, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if glitch > 0:
        rng = np.random.default_rng(int(t * FPS * 7))
        img = img.copy()
        for _ in range(int(3 + 9 * glitch)):
            y0 = int(rng.uniform(0, H - 40))
            h = int(rng.uniform(6, 22 + 120 * glitch))
            img[y0:y0 + h] = np.roll(img[y0:y0 + h], int(rng.normal(0, 60 * glitch)), axis=1)
        sh = int(14 * glitch)
        if sh:
            img[..., 0] = np.roll(img[..., 0], sh, axis=1)
            img[..., 2] = np.roll(img[..., 2], -sh, axis=1)
    if flash > 0:
        img = img + (255 - img) * flash
    img = img * _VIG + cv2.resize(_GRAIN[int(t * FPS) % 8], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)


def render(draw, t, samples=3, shutter=0.5, **kw):
    s = skia.Surface(W, H)
    c = s.getCanvas()
    acc = None
    for i in range(samples):
        ts = t + ((i + 0.5) / samples - 0.5) * shutter / FPS if samples > 1 else t
        c.clear(col(INK))
        draw(c, ts)
        f = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
        acc = f if acc is None else acc + f
    return post(acc / samples, t, **kw)
