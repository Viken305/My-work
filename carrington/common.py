"""Shared imports and helpers for the seven parts."""
import math

import numpy as np
import skia

from captions import Captions, VoiceEnvelope  # noqa: F401
from frames import *  # noqa: F401,F403
from lantern import *  # noqa: F401,F403
from lantern import _word_layout  # noqa: F401
from timing import Timing, schedule  # noqa: F401

SAMPLES = 3
SUN_WORDS = {"sun", "flare", "sunspots", "cloud", "slammed", "squeezed", "17.6hours", "blasted", "light"}
SKY_WORDS = {"fire", "blazed", "auroras", "read", "sky"}
WIRE_WORDS = {"telegraph", "sparks", "shocks", "haywire", "grids", "satellites"}


def colours(extra=None):
    d = {**{w: SUN for w in SUN_WORDS}, **{w: AUR_G for w in SKY_WORDS}, **{w: SPARK for w in WIRE_WORDS}}
    d.update(extra or {})
    return d


def appear(t, t0, d=0.35):
    return smooth(prog(t, t0, t0 + d))


def pop(t, t0, d=0.45):
    """0..1 with a slight overshoot, for things that land."""
    return spring(prog(t, t0, t0 + d), 7, 9) if t >= t0 else 0.0


def in_cubic(x):
    return clamp(x) ** 3


def in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def hit(t, t0, rise=0.03, decay=0.35):
    """A sharp 0..1 burst after t0 (for flashes)."""
    if t < t0:
        return 0.0
    d = t - t0
    return min(1.0, d / rise) * math.exp(-max(0.0, d - rise) / decay)


def shake_env(t, t0, peak=1.0, rise=0.08, decay=0.8):
    if t < t0:
        return 0.0
    d = t - t0
    return peak * min(1.0, d / rise) * math.exp(-max(0.0, d - rise) / decay)


def slide_change(t, dur, fin=0.6, fout=0.45):
    """Lantern slide change at both ends of a part: the image is racked out of focus and dimmed as the slide is
    pulled, and focused back in as the next one drops into the carrier."""
    a = 1 - out_cubic(prog(t, 0, fin)) if fin else 0.0
    b = in_cubic(prog(t, dur - fout, dur)) if fout else 0.0
    k = max(a, b)
    return dict(defocus=k, dim=0.85 * k)


def path_upto(pts, upto=1.0):
    """Path through a prefix (0..1 of the point count) of pts; returns (path, tip)."""
    p = skia.Path()
    n = len(pts)
    m = upto * (n - 1)
    k = int(m)
    if n < 2 or upto <= 0:
        return p, None
    p.moveTo(*pts[0])
    for i in range(1, min(k + 1, n)):
        p.lineTo(*pts[i])
    tip = pts[min(k, n - 1)]
    if k < n - 1:
        f = m - k
        tip = (pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f)
        p.lineTo(*tip)
    return p, tip


def stamp_tab(c, text, x, y, k, rgb=AUR_R, size=24, rot=-3.0):
    """A cream label stamped onto the slide (k: 0..1 landing progress from pop)."""
    if k <= 0.01:
        return
    w = width(text, "mono_bold", size, 0.08) + 44
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    s = 1 + 0.25 * (1 - clamp(k))
    c.scale(s, s)
    al = 255 * clamp(k * 1.5)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -size * 1.2, w, size * 2.0), 5, 5)
    c.drawRRect(r.makeOffset(0, 6), paint((0, 0, 0), al * 0.5, sigma=8))
    c.drawRRect(r, paint(CARD, al))
    c.drawRRect(r, paint(rgb, al, stroke=2.5))
    label(c, text, 0, size * 0.35, size, "mono_bold", rgb, al, "center", 0.08)
    c.restore()


def counter(c, text, x, y, size, rgb=LIME, a=255, align="left"):
    label(c, text, x, y, size, "mono_bold", rgb, a, align)
