"""Shared imports and helpers for the part files."""
import math

import numpy as np
import skia

from engine import FPS, H, W, clamp, in_cubic, in_out, lerp, mix, out_back, out_cubic, out_expo, prog, smooth  # noqa: F401
from noir import *  # noqa: F401,F403
from premium import add, light  # noqa: F401
from timing import Timing, schedule  # noqa: F401
from typo import ASH, EMBER, PAPER, Captions, Counter, font, label, paint, reveal, width  # noqa: F401

PREMIUM, SAMPLES = True, 3


def fade(c, t, dur, fin=0.3, fout=0.3):
    k = min(prog(t, 0, fin) if fin > 0 else 1.0, 1 - prog(t, dur - fout, dur) if fout > 0 else 1.0)
    if k < 1:
        c.drawPaint(fillp(VOID, 255 * (1 - k)))


def shake(t, t0, amp=18.0, decay=6.0):
    if t < t0:
        return 0.0, 0.0
    k = amp * math.exp(-(t - t0) * decay)
    return k * math.sin(t * 71), k * math.cos(t * 53)


def title(c, t, t0, y=900, a=1.0, top="THE DEEPEST", bottom="hole ever dug"):
    """Title card: tracked-out sans on top, ember serif italic below."""
    tr = lerp(0.45, 0.22, out_cubic(prog(t, t0, t0 + 1.6)))
    reveal(c, top, W / 2, y, 92, t, t0, "black", PAPER, 255 * a, "center", tracking=tr, stagger=0.035, dur=0.6, blur=16)
    reveal(c, bottom, W / 2, y + 128, 118, t, t0 + 0.35, "serif", EMBER, 255 * a, "center", stagger=0.03, dur=0.6, blur=16)
    lk = out_cubic(prog(t, t0 + 0.2, t0 + 1.0))
    c.drawLine(W / 2 - 300 * lk, y + 34, W / 2 + 300 * lk, y + 34, stroke(ASH, 1.5, 160 * a))
