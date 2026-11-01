"""Thumbnails for "Why Borders Are Shaped the Way They Are" (3D globe).

  python3 thumbnail.py      -> out/thumb_vertical.png (1080x1920, Shorts cover) + out/thumb_16x9.png (1280x720)

Drawn with the film's own globe engine: Africa and the Middle East, tilted toward the camera, with every
ruler-straight border glowing red, the Rio-Grande-style wiggles in cyan, and Bir Tawil raised as the land nobody claims.
"""
import os

import numpy as np
import skia

import film3d as F
import globe as G
from globe import AMBER, CYAN, RED, WHITE, Camera, fillp, flare, glow_fill, glow_line, strokep

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
T = 3.0                                                         # star twinkle phase only


def world(c, cam, scale=1.0):
    D = F.data()
    G.globe(c, cam, T, res="50m", border_a=150)
    # every ruler-straight border on Earth
    for a, b in D["straight"]:
        p, _ = G.line_path(cam, F.ll([a, b]), 1.0)
        glow_line(c, p, RED, 6 * scale, 255, core=True)
    # a few wiggly natural ones for contrast
    for ln in (D["zambezi"],):
        p, _ = G.line_path(cam, ln, 1.0)
        glow_line(c, p, CYAN, 4 * scale, 230)
    for ln in D["pyr"]:
        p, _ = G.line_path(cam, ln, 1.0)
        glow_line(c, p, CYAN, 4 * scale, 230)
    # Bir Tawil: the land no country wants
    G.slab(c, cam, D["bir_tawil"], (255, 214, 120), 16 * scale, top_glow=AMBER)
    x, y, vis = cam.point(33.75, 21.85)
    c.drawCircle(x, y, 60 * scale, strokep(AMBER, 5 * scale, 240, blur=3, plus=True))
    c.drawCircle(x, y, 60 * scale, strokep(AMBER, 3 * scale, 255))
    flare(c, x, y, AMBER, 16 * scale, 255)
    return x, y


def callout(c, x, y, tx, ty, lines, scale=1.0):
    """A stalk from the ring to a little two-line tag."""
    c.drawLine(x, y, tx, ty, strokep(WHITE, 3 * scale, 230))
    size = 40 * scale
    wd = max(F.text_w(s, "monob", size * (1 if i == 0 else 0.7), 0.06) for i, s in enumerate(lines)) + 44 * scale
    ht = size * 2.25
    r = skia.Rect.MakeXYWH(tx - wd / 2, ty - ht, wd, ht)
    c.drawRRect(skia.RRect.MakeRectXY(r, 14 * scale, 14 * scale), fillp((10, 14, 30), 225))
    c.drawRRect(skia.RRect.MakeRectXY(r, 14 * scale, 14 * scale), strokep(AMBER, 3 * scale, 255))
    F.draw_text(c, lines[0], tx, ty - ht + size * 1.1, size, "monob", AMBER, 255, "center", 0.06, shadow=False)
    F.draw_text(c, lines[1], tx, ty - ht + size * 1.85, size * 0.7, "monob", WHITE, 235, "center", 0.06, shadow=False)


def title(c, lines, x, y, size, align="center"):
    for i, (s, rgb) in enumerate(lines):
        F.draw_text(c, s, x, y + i * size * 0.98, size, "display", rgb, 255, align, 0.02,
                    glow=AMBER if rgb == AMBER else (60, 120, 255))


def snapshot(s):
    return s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]


def vertical():
    s = skia.Surface(G.W, G.H)
    c = s.getCanvas()
    cam = Camera(22, 16, 700, 8, 540, 1190)
    x, y = world(c, cam, 1.0)
    G.vignette(c, 150)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, G.W, 640), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 0), skia.Point(0, 640)], [skia.Color(2, 4, 16, 235), skia.Color(2, 4, 16, 0)])))
    callout(c, x + 50, y + 45, x + 190, y + 250, ["NO COUNTRY", "WANTS THIS LAND"], 1.0)
    title(c, [("WHY ARE", WHITE), ("BORDERS", WHITE), ("SHAPED", AMBER), ("LIKE THIS?", AMBER)], 540, 255, 180)
    return snapshot(s)


def wide():
    W2, H2 = 1280, 720
    s = skia.Surface(W2, H2)
    c = s.getCanvas()
    G.W, G.H = W2, H2                      # space() and the limb test use the module canvas size
    c.save()
    cam = Camera(22, 14, 420, 6, 960, 380)
    x, y = world(c, cam, 0.7)
    c.restore()
    G.W, G.H = 1080, 1920
    c.drawRect(skia.Rect.MakeWH(W2, H2), skia.Paint(Shader=skia.GradientShader.MakeRadial(
        skia.Point(W2 * 0.7, H2 * 0.5), W2 * 0.75, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 170)], [0.5, 1.0])))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, 760, H2), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 0), skia.Point(760, 0)], [skia.Color(2, 4, 16, 240), skia.Color(2, 4, 16, 0)])))
    callout(c, x + 30, y + 30, x + 110, y + 230, ["NO COUNTRY", "WANTS THIS LAND"], 0.7)
    title(c, [("WHY ARE", WHITE), ("BORDERS", WHITE), ("SHAPED", AMBER), ("LIKE THIS?", AMBER)], 60, 190, 150, "left")
    return snapshot(s)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(OUT, exist_ok=True)
    F.data()
    Image.fromarray(vertical()).save(os.path.join(OUT, "thumb_vertical.png"))
    Image.fromarray(wide()).save(os.path.join(OUT, "thumb_16x9.png"))
    print(os.path.join(OUT, "thumb_vertical.png"), os.path.join(OUT, "thumb_16x9.png"))
