"""Thumbnails.

  python3 thumbnails.py  -> out/thumb_short.png (1080x1920) + out/thumb_wide.png (1280x720)
"""
import os

import numpy as np
import skia
from PIL import Image

import kit
from film import *  # noqa: F401,F403


def split_picture(size=RES):
    """The hero, left half pure static, a soft diagonal seam into the clean right half."""
    img = pic("hero")
    st = pure_static(SEED)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    m = np.clip((xx - size * 0.3 + (yy - size / 2) * 0.25) / (size * 0.14), 0, 1)[..., None]
    return st * (1 - m) + img * m


def short_thumb(c, t):
    background(c)
    ambient(c, 3.0, 0.8)
    card_at(c, split_picture(), W / 2, 1000, 900, 255, -2, 1, None, AMBER)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 520), paint(INK, 200, sigma=50))
    label(c, "HOW AI DRAWS", W / 2, 300, 104, "black", PAPER, 255, "center", 0.05)
    label(c, "from nothing", W / 2, 450, 150, "serif_bold", AMBER, 255, "center")
    c.drawRect(skia.Rect.MakeLTRB(0, 1440, W, 1680), paint(INK, 220, sigma=40))
    label(c, "STATIC  →  PICTURE", W / 2, 1560, 54, "mono_bold", VIOLET, 255, "center", 0.08)


def wide_thumb(path):
    w, h = 1280, 720
    s = skia.Surface(w, h)
    c = s.getCanvas()
    c.clear(col(INK))
    c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeRadial((900, 360), 800, [col((34, 30, 46)), col(INK)])))
    card_at(c, split_picture(), 1000, 360, 520, 255, -2, 1, None, AMBER)
    label(c, "HOW AI", 60, 260, 96, "black", PAPER, 255, tracking=0.04)
    label(c, "DRAWS", 60, 360, 96, "black", PAPER, 255, tracking=0.04)
    label(c, "from nothing", 56, 470, 80, "serif_bold", AMBER, 255)
    label(c, "STATIC → PICTURE", 62, 560, 30, "mono_bold", VIOLET, 255, tracking=0.1)
    rgb = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
    Image.fromarray(rgb).save(path)


if __name__ == "__main__":
    out = os.path.join(HERE, "out")
    os.makedirs(out, exist_ok=True)
    Image.fromarray(kit.render(short_thumb, 2.0, samples=1)).save(os.path.join(out, "thumb_short.png"))
    wide_thumb(os.path.join(out, "thumb_wide.png"))
    print(os.path.join(out, "thumb_short.png"), os.path.join(out, "thumb_wide.png"))
