"""Thumbnails rendered from the vector scene (crisp at any size).

  python3 thumbnails.py  -> out/thumb_short.png (1080x1920, Shorts) + out/thumb_wide.png (1280x720, long video)
"""
import math, os

import skia
from PIL import Image

from story import *  # noqa: F401,F403

T = 1.2                        # the kilonova a moment into the cold open
INK = (10, 6, 24)


def shadowed(c, s, x, y, size, rgb, spacing=0.0, align="center"):
    text(c, s, x + size * 0.04, y + size * 0.06, size, INK, 200, 800, align, spacing)
    text(c, s, x, y, size, rgb, 255, 800, align, spacing)


def blast(c, cx, cy, r, ring_s):
    """Kilonova behind, the ring in front catching its light, a nugget falling into it."""
    kilonova(c, cx, cy, r, T, 0.32, seed=5)
    light(c, cx, cy + r * 0.55, r * 0.9, GOLD, 120)
    ring(c, cx, cy + r * 0.55, ring_s, T, "back")
    gold_sphere(c, cx, cy + r * 0.48, 46 * ring_s / 0.9, (140, 110, 170))
    ring(c, cx, cy + r * 0.55, ring_s, T, "front")
    sparkle4(c, cx + 260 * ring_s, cy + r * 0.5, 40 * ring_s, 255)
    sparkle4(c, cx - 280 * ring_s, cy + r * 0.6, 26 * ring_s, 230)


def snap(surf, path):
    Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]).save(path)


def short_thumb(path):
    w, h = 1080, 1920
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    space_bg(c, T, warm=0.6)
    blast(c, w / 2, 900, 640, 1.0)
    c.drawRect(skia.Rect.MakeXYWH(0, 0, w, 760), shaded(linear((0, 0), (0, 760), [(INK, 230), (INK, 0)])))
    c.drawRect(skia.Rect.MakeXYWH(0, 1480, w, 440), shaded(linear((0, 1480), (0, h), [(INK, 0), (INK, 245)])))
    shadowed(c, "THIS EXPLOSION", w / 2, 300, 100, WHITE, 4)
    shadowed(c, "MADE YOUR", w / 2, 430, 100, WHITE, 4)
    gold_word(c, "GOLD", w / 2, 640, 230, 255, 1.0, T)
    shadowed(c, "OLDER THAN", w / 2, 1700, 70, WHITE, 4)
    shadowed(c, "THE SUN", w / 2, 1800, 70, GOLD_HI, 4)
    snap(surf, path)


def wide_thumb(path):
    w, h = 1280, 720
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    space_bg(c, T, warm=0.6)
    c.save()
    c.translate(340, 300)
    c.scale(0.5, 0.5)
    blast(c, 0, 0, 640, 1.0)
    c.restore()
    c.drawRect(skia.Rect.MakeXYWH(0, 0, w, h), shaded(linear((620, 0), (1000, 0), [(INK, 0), (INK, 225)])))
    shadowed(c, "THIS EXPLOSION", 950, 220, 58, WHITE, 2)
    shadowed(c, "MADE YOUR", 950, 300, 58, WHITE, 2)
    gold_word(c, "GOLD", 950, 450, 150, 255, 1.0, T)
    shadowed(c, "OLDER THAN THE SUN", 950, 560, 34, WHITE, 2)
    snap(surf, path)


if __name__ == "__main__":
    out = os.path.join(HERE, "out")
    os.makedirs(out, exist_ok=True)
    short_thumb(os.path.join(out, "thumb_short.png"))
    wide_thumb(os.path.join(out, "thumb_wide.png"))
    print(os.path.join(out, "thumb_short.png"), os.path.join(out, "thumb_wide.png"))
