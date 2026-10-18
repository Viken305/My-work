"""YouTube thumbnail: python3 thumbnail.py -> out/thumbnail.png"""
import os

from PIL import Image

from story import *  # noqa: F401,F403
from premium import render_premium


def draw(c, t):
    sky(c, t, mood="space")
    globe(c, 620, 560, 400, t, rot=1.2, tilt=0.3)
    nimbus(c, 1000, 300, 150, t, pose("shocked"), (-0.6, 0.3), zap=1.0)
    text(c, "EARTH IS", 1450, 450, 70, WHITE, 255, 800, spacing=8)
    text(c, "WEIRDER", 1450, 600, 150, GOLD, 255, 800, spacing=8)
    text(c, "THAN YOU THINK", 1450, 700, 62, WHITE, 255, 800, spacing=6)


if __name__ == "__main__":
    p = os.path.join(HERE, "out", "thumbnail.png")
    Image.fromarray(render_premium(draw, 2.0, samples=1)).save(p)
    print(p)
