"""Thumbnails.

  python3 thumbnails.py  -> out/thumb_short.png (1080x1920) + out/thumb_wide.png (1280x720)
"""
import os

import cv2
from PIL import Image

from film import *  # noqa: F401,F403

DRIFT = (DOT[0] + 0.94 * 900, DOT[1] + 0.34 * 900)


def drift_extra(c, to, sw, sh):
    hx, hy = to(DOT)
    dx, dy = to(DRIFT)
    c.drawLine(hx, hy, dx, dy, paint(AMBER, 60, sigma=8, stroke=14))
    c.drawLine(hx, hy, dx, dy, paint(AMBER, 230, stroke=5))
    c.drawCircle(hx, hy, 20, paint(AMBER, 255, stroke=4))
    c.drawCircle(hx, hy, 6, paint(AMBER, 255))
    label(c, "YOU", hx, hy + 58, 26, "mono_bold", AMBER, 255, "center", 0.15)


def short_thumb(t=3.0):
    img = backdrop(t, glow=(0.5, 0.40), floor=0.86, pool=(540, 1800, 420, 70), seed=1.0)
    img = phone(img, 560, 1440, 560, 1120, -9, t, zoom=0.45, pan=(DOT[0] + 420, DOT[1] + 150), dot=DRIFT, pin=None,
                show_route=0, extra=drift_extra)
    img = chip(img, "+11 km / DAY", 560, 1150, 44, AMBER, 1.0)
    for s, y, size, rgb, glow in (("YOUR PHONE", 330, 132, PAPER, None), ("DOES", 470, 132, PAPER, None),
                                  ("EINSTEIN'S", 660, 176, mix(VIOLET, PAPER, 0.35), VIOLET), ("MATH", 830, 176, PAPER, None)):
        img = glass_text(img, s, W / 2, y, size, "black", tint=0.30, lift=30, rgb=rgb, caustic_t=t, glow=glow)
    return glass.post(img, t)


def wide_thumb(t=3.0):
    """Composed on the tall frame inside a 16:9 band (y 640..1248), then cropped and scaled to 1280x720."""
    y0 = 640
    img = backdrop(t, glow=(0.65, 0.5), floor=0.99, caustic=0.0)
    img = phone(img, 830, y0 + 370, 330, 660, -10, t, zoom=0.26, pan=(DOT[0] + 420, DOT[1] + 150), dot=DRIFT, pin=None,
                show_route=0, extra=drift_extra)
    for s, y, size, rgb, glow in (("YOUR PHONE", y0 + 150, 84, PAPER, None), ("DOES", y0 + 245, 84, PAPER, None),
                                  ("EINSTEIN'S", y0 + 375, 112, mix(VIOLET, PAPER, 0.35), VIOLET),
                                  ("MATH", y0 + 485, 112, PAPER, None)):
        img = glass_text(img, s, 50, y, size, "black", align="left", tint=0.30, lift=30, rgb=rgb, caustic_t=t, glow=glow)
    img = chip(img, "+11 km / DAY", 830, y0 + 560, 30, AMBER, 1.0)
    out = glass.post(img, t)[y0:y0 + 608]
    return cv2.resize(out, (1280, 720), interpolation=cv2.INTER_AREA)


if __name__ == "__main__":
    out = os.path.join(HERE, "out")
    os.makedirs(out, exist_ok=True)
    Image.fromarray(short_thumb()).save(os.path.join(out, "thumb_short.png"))
    Image.fromarray(wide_thumb()).save(os.path.join(out, "thumb_wide.png"))
    print(os.path.join(out, "thumb_short.png"), os.path.join(out, "thumb_wide.png"))
