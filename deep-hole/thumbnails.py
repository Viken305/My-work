"""Thumbnails from the vector scene.

  python3 thumbnails.py  -> out/thumb_short.png (1080x1920) + out/thumb_wide.png (1280x720)
"""
import os

import numpy as np
import skia
from PIL import Image

import premium
from film import *  # noqa: F401,F403

T = 3.0


def snap(surf, path, w, h):
    rgb = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
    if (w, h) == (W, H):
        out = premium.post(rgb, T, bloom=0.9, ca=0.5, grain=4.0)
    else:
        out = np.clip(rgb, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(path)


def short_thumb(path):
    s = skia.Surface(W, H)
    c = s.getCanvas()
    cam = Section((960 - 640) / 0.085, 0.085, cy=960)
    void(c, T, warm=0.4)
    strata(c, cam, T, heat=1.3, labels=0)
    hole(c, cam, 12262, T, glow=1.2)
    everest(c, 270, cam.sy(0), 8849 * cam.ppm, 200, flip=True, fill_a=150)
    tower(c, W / 2 + 6, cam.sy(0), 0.5, T)
    c.drawRect(skia.Rect.MakeWH(W, 520), grad_v(0, 520, VOID, VOID, 250, 0))
    label(c, "THE DEEPEST", W / 2, 300, 112, "black", PAPER, 255, "center", tracking=0.14)
    label(c, "hole ever dug", W / 2, 450, 140, "serif", EMBER, 255, "center")
    yb = cam.sy(12262)
    c.drawRect(skia.Rect.MakeXYWH(0, yb + 30, W, 260), paint(VOID, 190, 40))
    label(c, "12,262 m", W / 2, yb + 190, 160, "mono_bold", PAPER, 255, "center")
    label(c, "EVEREST, UPSIDE DOWN", 270, cam.sy(0) + 60, 20, "mono", PAPER, 200, "center", tracking=0.15)
    snap(s, path, W, H)


def wide_thumb(path):
    w, h = 1280, 720
    s = skia.Surface(w, h)
    c = s.getCanvas()
    c.drawPaint(fillp(VOID))
    c.save()
    c.translate(-120, -260)
    c.scale(0.62, 0.62)
    cam = Section(FULL["d"], FULL["ppm"], cy=FULL["cy"] + 120)
    strata(c, cam, T, heat=1.3, labels=0)
    hole(c, cam, 12262, T, glow=1.2)
    everest(c, 270, cam.sy(0), 8849 * cam.ppm, 200, flip=True, fill_a=150)
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(560, 0, w, h), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(560, 0), (760, 0)], [skia.Color(9, 9, 10, 0), skia.Color(9, 9, 10, 245)])))
    label(c, "THE DEEPEST", 950, 250, 60, "black", PAPER, 255, "center", tracking=0.1)
    label(c, "hole ever dug", 950, 340, 78, "serif", EMBER, 255, "center")
    label(c, "12,262 m", 950, 490, 92, "mono_bold", PAPER, 255, "center")
    snap(s, path, w, h)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    short_thumb(os.path.join(out, "thumb_short.png"))
    wide_thumb(os.path.join(out, "thumb_wide.png"))
    print(os.path.join(out, "thumb_short.png"), os.path.join(out, "thumb_wide.png"))
