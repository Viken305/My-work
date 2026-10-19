"""Shared imports and helpers for parts 2-5."""
import math

import numpy as np
import skia

from captions import Captions, VoiceEnvelope  # noqa: F401
from cyan import *  # noqa: F401,F403
from frames import KRAKATOA, LONDON, RODRIGUES, ash_column, island_path, ship  # noqa: F401
from timing import Timing, schedule  # noqa: F401

SAMPLES = 3
BATAVIA = (106.83, -6.13)
SOUND = {"heard", "hear", "sound", "loud", "decibels", "172", "cannon", "barometers", "jumped", "wave", "planet",
         "far.", "far", "spike", "blast"}
HARM = {"eardrums", "gone.", "gone", "died.", "died", "tsunamis", "blood", "red.", "ash"}


def in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def log_lerp(a, b, u):
    return math.exp(math.log(a) + (math.log(b) - math.log(a)) * clamp(u))


def black(c, a):
    if a > 0:
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((0, 0, 0), 255 * clamp(a)))


def edges(c, t, dur, fin=0.35, fout=0.35):
    """Dip from / to black at the part boundaries."""
    black(c, max(1 - smooth(prog(t, 0, fin)) if fin else 0, smooth(prog(t, dur - fout, dur)) if fout else 0))


def sea_map(c, proj, key=None, zoomed=False, a=1.0):
    paper(c)
    graticule(c, proj, 0.7 * a, step=1 if zoomed else 10)
    engraved_land(c, land_path(proj, "indian_ocean"), a, hatch=6,
                  water_lines=(14, 30, 50, 76, 110) if zoomed else (9, 19, 31, 46), key=key)


def big_number(c, text, y, unit, a=1.0, rgb=PAPER, unit_rgb=SULFUR, size=170):
    if a <= 0:
        return
    label(c, text, W / 2, y, size, "mono_bold", rgb, 240 * a, "center", 0.02)
    label(c, unit, W / 2, y + 70, 26, "mono", unit_rgb, 240 * a, "center", 0.4)


def km_px(km, R):
    return km / 6371.0 * R
