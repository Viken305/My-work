"""YouTube thumbnail (1280x720): python3 thumbnail.py -> out/thumbnail.png"""
import os

from PIL import Image

from common import *  # noqa: F401,F403


def draw(c, t=3.0):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(14, 10, 40), (90, 40, 90)])))
    Stars(160, 8).draw(c, t, 0.8)
    glow(c, 1260, 380, 700, LAVA, 120)
    x, y = volcano(c, 1260, 1000, 1100, 640, (80, 62, 108), crater=0.1, hot=1.0, t=t)
    Plume(77, 48).draw(c, x, y - 10, t, 520, 170, 1.0, 0.2)
    for pts in ([(x - 8, y), (1200, 480), (1150, 600), (1080, 720), (1060, 860), (980, 1000)],
                [(x + 8, y), (1320, 470), (1380, 600), (1360, 740), (1470, 880), (1540, 1000)]):
        lava_flow(c, pts, 1.0, 26)
    bird(c, 1700, 1040, 90, t, look=(-1, -0.6))
    text(c, "WHY DO", 120, 330, 150, WHITE, 255, 800, "left", spacing=6)
    text(c, "VOLCANOES", 120, 490, 150, LAVA_HOT, 255, 800, "left", spacing=6)
    text(c, "EXIST?", 120, 650, 150, WHITE, 255, 800, "left", spacing=6)
    vignette(c, 120)


if __name__ == "__main__":
    s = skia.Surface(W, H)
    draw(s.getCanvas())
    img = Image.fromarray(finish(s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType), 3.0))
    out = os.path.join(HERE, "out", "thumbnail.png")
    img.resize((1280, 720), Image.LANCZOS).save(out)
    print(out)
