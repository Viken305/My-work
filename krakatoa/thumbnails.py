"""Thumbnails.

  python3 thumbnails.py  -> out/thumb_short.png (1080x1920) + out/thumb_wide.png (1280x720)
"""
import os

import numpy as np
import skia
from PIL import Image

import cyan
from cyan import *  # noqa: F401,F403
from frames import KRAKATOA, RODRIGUES, ash_column, island_path

T = 2.0


def short_thumb(c, t):
    paper(c)
    sea, vx, vy = 1040, 562, 885
    light(c, vx, vy - 120, 1000, LAVA, 130)
    for k, r in enumerate((300, 520, 760, 1040)):
        ring(c, vx, vy - 40, r, SULFUR, 255 - k * 45, 3.6 - k * 0.5, fringe=k == 0)
    c.save()
    c.translate(vx, vy)
    c.scale(0.9, 0.9)
    c.translate(-vx, -vy)
    ash_column(c, vx, vy - 40, t)
    c.restore()
    light(c, vx, vy - 10, 300, SUN_O, 230)
    light(c, vx, vy, 140, HOT, 255)
    c.drawRect(skia.Rect.MakeLTRB(0, sea, W, H), paint(mix(NIGHT, PRUSSIAN, 0.7), 245))
    for i, y in enumerate(range(sea + 6, H, 9)):
        c.drawLine(0, y, W, y, paint(PAPER, 40 - min(28, i * 0.4), stroke=1.0))
    isl = island_path()
    c.drawPath(isl, paint(mix(PRUSSIAN, PAPER, 0.1)))
    c.drawPath(isl, paint(PAPER, 230, stroke=1.8))
    c.drawLine(0, sea, W, sea, paint(PAPER, 210, stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 560), paint(NIGHT, 170, sigma=60))
    label(c, "THE LOUDEST SOUND", W / 2, 300, 76, "black", PAPER, 255, "center", tracking=0.08)
    label(c, "ever heard", W / 2, 470, 170, "serif_bold", SULFUR, 255, "center")
    c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, 1480), paint(NIGHT, 200, sigma=40))
    label(c, "HEARD 4,800 KM AWAY", W / 2, 1300, 66, "mono_bold", PAPER, 255, "center", 0.04)
    label(c, "KRAKATOA, 1883", W / 2, 1380, 34, "mono", SULFUR, 255, "center", 0.3)


def wide_thumb(path):
    w, h = 1280, 720
    s = skia.Surface(w, h)
    c = s.getCanvas()
    c.clear(col(NIGHT))
    c.save()
    c.scale(w / W, w / W)
    c.drawImage(paper_image(), 0, -700)
    c.restore()
    proj = Ortho.fit(KRAKATOA, (1080, 250), RODRIGUES, (560, 640), 86, -12)
    engraved_land(c, land_path(proj, "indian_ocean"), hatch=6, water_lines=())
    kx, ky, _ = proj(*KRAKATOA)
    rx, ry, _ = proj(*RODRIGUES)
    import math
    R = math.hypot(rx - kx, ry - ky)
    for k, f in enumerate((0.4, 0.65, 0.85)):
        ring(c, kx, ky, R * f, SULFUR, 90 + k * 30, 2.0, fringe=False, trail=0)
    ring(c, kx, ky, R, SULFUR, 255, 4.0)
    light(c, kx, ky, 120, LAVA, 230)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, 640, h), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(380, 0), (680, 0)], [col(NIGHT, 245), col(NIGHT, 0)])))
    label(c, "THE LOUDEST", 60, 230, 74, "black", PAPER, 255, tracking=0.06)
    label(c, "SOUND", 60, 310, 74, "black", PAPER, 255, tracking=0.06)
    label(c, "ever heard", 56, 440, 120, "serif_bold", SULFUR, 255)
    label(c, "4,800 KM · KRAKATOA 1883", 62, 530, 30, "mono_bold", PAPER, 230, tracking=0.1)
    rgb = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
    Image.fromarray(rgb).save(path)


if __name__ == "__main__":
    out = os.path.join(HERE, "out")
    os.makedirs(out, exist_ok=True)
    Image.fromarray(cyan.render(short_thumb, T, samples=1)).save(os.path.join(out, "thumb_short.png"))
    wide_thumb(os.path.join(out, "thumb_wide.png"))
    print(os.path.join(out, "thumb_short.png"), os.path.join(out, "thumb_wide.png"))
