"""Shared imports and helpers for the five parts: cached pictures and noise, moving cards with sheen, ambient
particles, step counter, text that resolves out of static, and the black dips between parts."""
import math

import cv2
import numpy as np
import skia

import art
from captions import Captions, VoiceEnvelope, _static  # noqa: F401

grain_patch = _static           # colour static clipped to a rect (exported name)
from kit import *  # noqa: F401,F403
from timing import Timing, schedule  # noqa: F401

SAMPLES = 3
RES = 768                       # pixel size the vector pictures are drawn at
SEED = 1883                     # the hero's "seed" shown on screen
SEEDS = {"hero": 1883, "seed_a": 11, "seed_b": 22, "seed_c": 33}

# caption emphasis: amber = your words, violet = the model
WORDS = {"sentence", "prompt", "prompt.", "words", "cat", "moon", "moon?", "kitten.", "planet.", "captions.", "mean.",
         "yours.", "words.", "cat.", "cat,", "moon.", "tokens,"}
MODEL = {"noise.", "noise", "static.", "static", "numbers.", "map", "meaning.", "guess", "guesses", "reverse.", "step,",
         "step.", "decoder", "smaller.", "billions", "model", "job.", "shapes.", "colour.", "trick.", "random"}

_IMG, _NZ = {}, {}


# ---------------------------------------------------------------- easing
def in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def back_out(x, s=1.6):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def lerp(a, b, u):
    return a + (b - a) * u


# ---------------------------------------------------------------- pictures
def pic(name, k=0.0, seed=None):
    """Vector picture `name` with diffusion noise level k (0 clean .. 1 pure static); k is quantised for caching."""
    base = _IMG.get(name)
    if base is None:
        base = _IMG[name] = art.image(name, RES)
    if k <= 0.001:
        return base
    return noisy(base, nz(seed if seed is not None else SEEDS.get(name, 7)), k)


def nz(seed):
    if seed not in _NZ:
        _NZ[seed] = static(seed, RES, cell=2)
    return _NZ[seed]


def pure_static(seed):
    return np.clip(nz(seed) * 80 + 128, 0, 255)


def guess(u, name="hero", seed=SEED):
    """The picture during generation, u = 0 (pure static) .. 1 (done): the model's blurry guess with noise on top."""
    u = clamp(u)
    k = int(u * 29.999)
    g = art.step(k, name=name, size=RES)
    n = nz(seed)
    left = math.cos(u * math.pi / 2) ** 1.6       # how much starting noise is still there
    out = g * (1 - left) + (n * 80 + 128) * left
    return np.clip(out, 0, 255)


# ---------------------------------------------------------------- drawing
def card_at(c, arr, cx, cy, w, a=255, rot=0.0, s=1.0, caption=None, glow=None, sheen=None, h=None, cap_rgb=SMOKE):
    """A picture card centred at (cx, cy), with optional rotation/scale, glow and a moving light sheen (0..1)."""
    if a <= 1 or s <= 0.001:
        return
    h = h or w * arr.shape[0] / arr.shape[1]
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(s, s)
    card(c, arr, -w / 2, -h / 2, w, None, a, glow, h)
    if sheen is not None and 0 < sheen < 1:
        r = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(r, 18, 18), doAntiAlias=True)
        x = -w / 2 - w * 0.6 + w * 2.2 * sheen
        c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeLinear(
            [(x - 160, -h / 2), (x + 160, h / 2)], [col(PAPER, 0), col(PAPER, int(70 * a / 255)), col(PAPER, 0)])))
        c.restore()
    if caption:
        label(c, caption, -w / 2 + 4, h / 2 + 40, 22, "mono", cap_rgb, a, tracking=0.12)
    c.restore()


def ambient(c, t, a=1.0, n=34, seed=2):
    """Soft floating specks (amber, violet, white) drifting upward at three depths."""
    rng = np.random.default_rng(seed)
    for i in range(n):
        depth = rng.uniform(0.3, 1.0)
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        sp = 18 + 40 * depth
        y = (y0 - t * sp) % (H + 200) - 100
        x = x0 + 30 * math.sin(t * 0.3 + i)
        rgb = (AMBER, VIOLET, PAPER)[i % 3]
        r = 2 + 5 * depth
        c.drawCircle(x, y, r * 3, paint(rgb, 22 * a * depth, sigma=r * 2.5))
        c.drawCircle(x, y, r * 0.5, paint(rgb, 90 * a * depth, sigma=1.5))


def step_ui(c, k, x, y, a=255, n=30, w=760, rgb=VIOLET):
    """STEP k / n with a 30-segment progress bar."""
    if a <= 1:
        return
    kk = int(clamp(k, 0, n))
    label(c, "STEP", x, y, 22, "mono", SMOKE, a, tracking=0.3)
    label(c, f"{kk:2d} / {n}", x + w, y, 30, "mono_bold", rgb, a, "right", 0.05)
    seg = (w - (n - 1) * 4) / n
    for i in range(n):
        on = i < kk
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + i * (seg + 4), y + 18, seg, 8), 3, 3),
                    paint(rgb if on else SMOKE, a * (1 if on else 0.25)))
    if 0 < kk <= n:
        i = kk - 1
        c.drawCircle(x + i * (seg + 4) + seg / 2, y + 22, 16, paint(rgb, a * 0.5, sigma=10))


def resolve_text(c, text, x, y, size, kind, rgb, u, seed=0, align="left", tracking=0.0, a=255):
    """Text that resolves out of colour static (u: 0 static .. 1 crisp), letter by letter."""
    if u <= 0 or a <= 1:
        return
    f = font(kind, size)
    w = width(text, kind, size, tracking)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    n = max(1, len(text))
    for j, ch in enumerate(text):
        adv = f.measureText(ch)
        kk = clamp(u * 1.5 - j / n * 0.5)
        if ch != " ":
            nzv = math.cos(kk * math.pi / 2) ** 2
            if nzv > 0.02:
                _static(c, skia.Rect.MakeXYWH(x0 - 2, y - size * 0.82, adv + 4, size * 1.02), a * nzv * min(1, u * 8), seed + j)
            c.drawString(ch, x0, y, f, paint(rgb, a * smooth(kk), sigma=(1 - kk) * 10))
        x0 += adv + tracking * size


def thread(c, x0, y0, x1, y1, u, rgb=AMBER, a=255, bend=0.5):
    """An amber curve drawn from (x0, y0) toward (x1, y1), u = 0..1 of its length, with a glowing head."""
    if u <= 0 or a <= 1:
        return
    p = skia.Path()
    p.moveTo(x0, y0)
    p.cubicTo(x0, y0 + (y1 - y0) * bend, x1, y1 - (y1 - y0) * bend, x1, y1)
    meas = skia.PathMeasure(p, False)
    L = meas.getLength()
    seg = skia.Path()
    meas.getSegment(0, L * clamp(u), seg, True)
    c.drawPath(seg, paint(rgb, a * 0.35, sigma=6, stroke=8))
    c.drawPath(seg, paint(rgb, a, stroke=2.5))
    pos = meas.getPosTan(L * clamp(u))
    if pos:
        hx, hy = pos[0].x(), pos[0].y()
        c.drawCircle(hx, hy, 10, paint(rgb, a * 0.7, sigma=6))
        c.drawCircle(hx, hy, 4, paint(PAPER, a))


def node_box(c, cx, cy, w, h, t, text="MODEL", a=255, active=1.0):
    """The model: a violet box with a small pulsing network inside."""
    if a <= 1:
        return
    r = skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h)
    c.drawRRect(skia.RRect.MakeRectXY(r, 26, 26), paint(VIOLET, a * 0.5 * active, sigma=34))
    c.drawRRect(skia.RRect.MakeRectXY(r, 26, 26), paint(CARD, a))
    cols = [3, 4, 4, 3]
    pts = []
    for i, n in enumerate(cols):
        x = cx - w * 0.32 + w * 0.64 * i / (len(cols) - 1)
        pts.append([(x, cy - h * 0.12 + (j - (n - 1) / 2) * h * 0.16) for j in range(n)])
    for i in range(len(pts) - 1):
        for p0 in pts[i]:
            for p1 in pts[i + 1]:
                ph = math.sin(t * 6 + p0[1] * 0.05 + p1[1] * 0.03 + i) * 0.5 + 0.5
                c.drawLine(*p0, *p1, paint(VIOLET, a * (0.12 + 0.5 * ph * active), stroke=1.2))
    for layer in pts:
        for (x, y) in layer:
            c.drawCircle(x, y, 6, paint(mix(VIOLET, PAPER, 0.4), a))
    c.drawRRect(skia.RRect.MakeRectXY(r, 26, 26), paint(VIOLET, a, stroke=2.5))
    label(c, text, cx, cy + h / 2 - 26, 22, "mono_bold", VIOLET, a, "center", 0.3)


def black(c, a):
    if a > 0:
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((0, 0, 0), 255 * clamp(a)))


def edges(c, t, dur, fin=0.3, fout=0.3):
    black(c, max(1 - smooth(prog(t, 0, fin)) if fin else 0, smooth(prog(t, dur - fout, dur)) if fout else 0))


def camera(c, s=1.0, dx=0.0, dy=0.0, cx=W / 2, cy=H / 2):
    """Scale about (cx, cy) and offset; caller wraps in save/restore."""
    c.translate(cx + dx, cy + dy)
    c.scale(s, s)
    c.translate(-cx, -cy)
