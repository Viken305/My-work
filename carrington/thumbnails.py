"""Thumbnails:  python3 thumbnails.py  -> out/thumb_short.png (1080x1920) + out/thumb_wide.png (1280x720)"""
import os

import numpy as np
import skia
from PIL import Image

import part1
from frames import bezel, flare_bead, kidney
from lantern import (ADD, FLARE, HERE, LIME, SCREEN, SILVER, SUN, VOID, col, font, glass, label, paint, render,
                     stars, sun_disc, sunspot, width)

OUT = os.path.join(HERE, "out")


def wide(c):
    """Drawn on a 1920x1080 surface, resized to 1280x720."""
    c.save()
    c.scale(1920 / 1080, 1)          # one glass plate stretched across the wide frame (no seam)
    glass(c)
    c.restore()
    stars(c, 300, 4, (0, 0, 1920, 1080), 200)
    cx, cy, R = 1450, 540, 360
    bezel(c, cx, cy, R + 40, 220, "SOL  ·  1 SEPTEMBER 1859  ·  11:18 A.M.  ·  REDHILL, SURREY  ·  ", -150)
    sun_disc(c, cx, cy, R, 255, 1.0, 1)
    for (x, y, r, s) in ((60, -40, 30, 1), (108, -10, 21, 2), (24, 6, 16, 3), (138, -40, 13, 4), (0, -28, 10, 5)):
        sunspot(c, cx + x, cy + y, r, 255, s, 0.85, 20)
    flare_bead(c, kidney(cx + 58, cy - 54, 24, 0.4), 255, 1.8)
    flare_bead(c, kidney(cx + 110, cy + 6, 19, -0.3), 255, 1.8)
    label(c, "1 SEPTEMBER 1859", 96, 300, 30, "mono_bold", LIME, 230, tracking=0.3)
    label(c, "THE DAY THE SUN", 90, 420, 96, "serif_roman", LIME, 255, tracking=0.03)
    f = font("serif_bold", 300)
    x = 80
    for ch in "Hit Us":
        c.drawString(ch, x, 720, f, paint(SUN, 120, sigma=30, blend=ADD))
        c.drawString(ch, x, 720, f, paint(SUN, 255, blend=SCREEN))
        c.drawString(ch, x, 720, f, paint(FLARE, 120, blend=SCREEN))
        x += f.measureText(ch)
    label(c, "the biggest solar storm ever recorded", 96, 820, 50, "serif", SILVER, 255)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(render(part1.draw_frame, part1.DURATION - 1.0, samples=1, flicker=0, weave=0)).save(
        os.path.join(OUT, "thumb_short.png"))
    s = skia.Surface(1920, 1080)
    c = s.getCanvas()
    c.clear(col(VOID))
    wide(c)
    img = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
    Image.fromarray(img).resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, "thumb_wide.png"))
    print("ok")
