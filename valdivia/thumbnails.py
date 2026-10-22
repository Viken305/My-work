"""Thumbnails:  python3 thumbnails.py  -> out/thumb_short.png (1080x1920) + out/thumb_wide.png (1280x720)"""
import math, os

import numpy as np
import skia
from PIL import Image

from common import BRONZE, EPI, H, HERE, INK, RED, W, Ortho, dial_rings, globe, glow, label, mode_outline, paint, \
    paper, post, ring_word, star, trace, width, BONE, SEPIA, col

OUT = os.path.join(HERE, "out")


def short(c):
    paper(c)
    cx, cy, R = 540, 1020, 380
    dial_rings(c, cx, cy, R, 1.0, 0.4)
    for eps, a0 in ((0.07, 230), (-0.07, 140)):
        q = mode_outline(cx, cy, R * 1.012, eps)
        c.drawPath(q, paint(BRONZE, a0 * 0.3, sigma=10, stroke=10))
        c.drawPath(q, paint(BRONZE, a0, stroke=2.6))
    proj = Ortho(-74, -20, R, cx, cy)
    globe(c, proj, 1.0, 1.0, key="thumb")
    ex, ey, _ = proj(*EPI)
    for r in (30, 60, 95):
        q = skia.Path()
        q.addCircle(ex, ey, r)
        glow(c, q, RED, 230, 3.0, 0.8)
    star(c, ex, ey, 24)
    label(c, "THE EARTH", W / 2, 360, 120, "black", INK, 255, "center", 0.01)
    w = width("RANG", "serif_bold", 230)
    ring_word(c, "RANG", W / 2 - w / 2, 580, 230, BRONZE, 1.0, strike=0.35)
    label(c, "9.5", 880, 1560, 130, "black", RED, 255, "right")
    label(c, "LARGEST EVER", 880, 1600, 26, "mono_bold", RED, 255, "right", 0.12)


def wide(c):
    """Drawn on a 1920x1080 surface (two paper sheets side by side), resized to 1280x720."""
    paper(c)
    c.save()
    c.translate(1080, 0)
    paper(c)
    c.restore()
    c.save()
    cx, cy, R = 1450, 540, 380
    dial_rings(c, cx, cy, R, 1.0, 0.4)
    proj = Ortho(-74, -20, R, cx, cy)
    for eps, a0 in ((0.07, 230), (-0.07, 140)):
        q = mode_outline(cx, cy, R * 1.012, eps)
        c.drawPath(q, paint(BRONZE, a0, stroke=2.6))
    globe(c, proj, 1.0, 1.0, key="thumbw")
    ex, ey, _ = proj(*EPI)
    star(c, ex, ey, 24)
    label(c, "THE DAY THE EARTH", 90, 330, 92, "black", INK, 255)
    ring_word(c, "RANG", 90, 600, 250, BRONZE, 1.0, strike=0.35)
    label(c, "like a bell · Chile 1960 · M 9.5", 96, 720, 52, "serif", INK, 255)
    c.restore()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.clear(col(BONE))
    short(c)
    img = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
    Image.fromarray(post(img, 0.0)).save(os.path.join(OUT, "thumb_short.png"))
    s = skia.Surface(1920, 1080)
    c = s.getCanvas()
    c.clear(col(BONE))
    wide(c)
    img = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
    Image.fromarray(img).resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, "thumb_wide.png"))
    print("ok")
