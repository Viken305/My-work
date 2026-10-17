"""YouTube thumbnail: python3 thumbnail.py -> out/thumbnail.png"""
import os

from PIL import Image

from story import *  # noqa: F401,F403
from premium import render_premium


def draw(c, t):
    body_world(c, t)
    rng = np.random.default_rng(2)
    for k, (x, y) in enumerate([(1180, 150), (1420, 110), (1700, 170), (1860, 420), (1150, 900), (1420, 960), (1720, 920)]):
        bacterium(c, x, y, 50, t + k, rng.uniform(0, 360), mood=pose("shocked"), wiggle=3)
    c.drawPaint(shaded(radial((1400, 560), 700, [((30, 4, 14), 170), ((30, 4, 14), 0)])))
    kai(c, 640, 600, 330, t, pose("angry"), (0.6, 0.0), 0.0)
    near_blur(c, [(1990, 1040, 260)], t, (190, 70, 100), 0.9)
    text(c, "THERE IS A", 1400, 420, 64, WHITE, 255, 800, spacing=8)
    text(c, "WAR", 1400, 590, 190, (255, 214, 120), 255, 800, spacing=10)
    text(c, "INSIDE YOU", 1400, 720, 96, WHITE, 255, 800, spacing=8)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "thumbnail.png")
    Image.fromarray(render_premium(draw, 2.0, samples=1)).save(p)
    print(p)
