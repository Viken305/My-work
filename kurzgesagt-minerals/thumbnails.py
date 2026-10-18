"""Thumbnails rendered from the vector scene (crisp at any size).

  python3 thumbnails.py  -> out/thumb_short.png (1080x1920, Shorts) + out/thumb_wide.png (1280x720, long video)
"""
import math, os

import skia
from PIL import Image

from engine import *  # noqa: F401,F403
import part3

T = 38.5                       # Naica cave: lights on, the bird has landed next to the explorer
PERSON = (940, 560)            # scene coordinates of the tiny explorer (focus point)
GOLD = (255, 214, 120)


def scene(c, cx, cy, s):
    """Draw the cave scaled by s so that scene point PERSON lands at canvas point (cx, cy)."""
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    c.translate(-PERSON[0], -PERSON[1])
    part3.draw_cave(c, T)
    c.restore()


def marker(c, x, y, s, label, dx=1.0):
    """Arrow + pill label pointing at the explorer from below-right: a 'this is you' scale cue."""
    ax, ay = x + dx * 190 * s, y + 190 * s
    tx, ty = x + dx * 14 * s, y + 66 * s
    c.drawLine(ax - dx * 40 * s, ay - 30 * s, tx, ty, stroke(WHITE, 8 * s))
    an = math.atan2(ty - (ay - 30 * s), tx - (ax - dx * 40 * s))
    c.drawPath(poly([(tx + math.cos(an) * 22 * s, ty + math.sin(an) * 22 * s), (tx + math.cos(an + 2.5) * 28 * s, ty + math.sin(an + 2.5) * 28 * s),
                     (tx + math.cos(an - 2.5) * 28 * s, ty + math.sin(an - 2.5) * 28 * s)]), fill(WHITE))
    f = font(int(30 * s), 800)
    w = f.measureText(label) + 56 * s + len(label) * 3 * s
    c.drawRRect(rrect(ax - w / 2, ay - 28 * s, w, 58 * s, 29 * s), fill((20, 14, 40), 235))
    c.drawRRect(rrect(ax - w / 2, ay - 28 * s, w, 58 * s, 29 * s), stroke(WHITE, 3 * s))
    text(c, label, ax, ay + 11 * s, 30 * s, WHITE, 255, 800, spacing=3 * s)


def shadowed(c, s, x, y, size, rgb, spacing=0.0, align="center"):
    p = skia.Paint(AntiAlias=True)
    c.saveLayer(None, p)
    text(c, s, x + size * 0.04, y + size * 0.06, size, (10, 6, 24), 200, 800, align, spacing)
    c.restore()
    text(c, s, x, y, size, rgb, 255, 800, align, spacing)


def short_thumb(path):
    w, h = 1080, 1920
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    scene(c, 540, 1100, 1.9)
    c.drawRect(skia.Rect.MakeXYWH(0, 0, w, 720), shaded(linear((0, 0), (0, 720), [((12, 8, 28), 240), ((12, 8, 28), 0)])))
    c.drawRect(skia.Rect.MakeXYWH(0, 1500, w, 420), shaded(linear((0, 1500), (0, h), [((12, 8, 28), 0), ((12, 8, 28), 245)])))
    shadowed(c, "CRYSTALS", w / 2, 260, 150, WHITE, 6)
    shadowed(c, "12 METRES", w / 2, 430, 150, GOLD, 6)
    shadowed(c, "LONG", w / 2, 590, 150, WHITE, 6)
    marker(c, 540, 1100, 1.9, "THIS IS A PERSON", dx=0.25)
    shadowed(c, "HOW DID EARTH", w / 2, 1720, 64, WHITE, 4)
    shadowed(c, "MAKE THESE?", w / 2, 1810, 64, GOLD, 4)
    Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]).save(path)


def wide_thumb(path):
    w, h = 1280, 720
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    scene(c, 330, 400, 1.15)
    c.drawRect(skia.Rect.MakeXYWH(0, 0, w, h), shaded(linear((560, 0), (1000, 0), [((12, 8, 28), 0), ((12, 8, 28), 225)])))
    c.drawRect(skia.Rect.MakeXYWH(1180, 0, 100, h), fill((12, 8, 28), 225))
    shadowed(c, "CRYSTALS", 930, 240, 92, WHITE, 3)
    shadowed(c, "12 METRES", 930, 350, 92, GOLD, 3)
    shadowed(c, "LONG", 930, 460, 92, WHITE, 3)
    shadowed(c, "HOW DID EARTH MAKE THEM?", 930, 560, 30, WHITE, 2)
    marker(c, 330, 400, 1.15, "THIS IS A PERSON", dx=0.3)
    Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]).save(path)


if __name__ == "__main__":
    out = os.path.join(HERE, "out")
    short_thumb(os.path.join(out, "thumb_short.png"))
    wide_thumb(os.path.join(out, "thumb_wide.png"))
    print(os.path.join(out, "thumb_short.png"), os.path.join(out, "thumb_wide.png"))
