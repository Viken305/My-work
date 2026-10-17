"""YouTube thumbnail (1280x720): python3 thumbnail.py -> out/thumbnail.png"""
import os

from PIL import Image

from boards import *  # noqa: F401,F403


def draw(c, t=2.0):
    bg(c, INDIGO, ROYAL, t=t, dust=False)
    glow(c, 1380, 560, 700, SAFFRON, 90)
    rangoli(c, 1380, 560, 470, 1.0, t)
    c.drawCircle(1380, 560, 330, fill(INDIGO, 235))
    draw_india(c, 1380, 590, 22, rgb=MARBLE, glow_a=120, neighbours=False)
    text(c, "HOW DID", 110, 300, 140, WHITE, 255, 800, "left", spacing=6)
    text(c, "INDIA", 110, 470, 190, SAFFRON, 255, 800, "left", spacing=8)
    text(c, "GET HERE?", 110, 620, 140, WHITE, 255, 800, "left", spacing=6)
    indic_text(c, "भारत", 110, 790, 110, "deva", MARIGOLD, 255, "left")
    bird(c, 1800, 1040, 90, t, look=(-1, -0.5))
    vignette(c, 110)


if __name__ == "__main__":
    s = skia.Surface(W, H)
    draw(s.getCanvas())
    out = os.path.join(HERE, "out", "thumbnail.png")
    Image.fromarray(finish(s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType), 2.0)).resize((1280, 720), Image.LANCZOS).save(out)
    print(out)
