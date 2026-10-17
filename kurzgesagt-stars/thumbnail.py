"""YouTube thumbnail: python3 thumbnail.py -> out/thumbnail.png"""
import os

from PIL import Image

from story import *  # noqa: F401,F403
from premium import render_premium


def draw(c, t):
    space(c, t, Cam(0, 0, 1.0), clouds=("cloud", "teal"), a=0.9)
    draw_texture(c, tex_fire(64), 400, 540, 0.85, 20, 170, skia.BlendMode.kPlus)
    draw_texture(c, tex_ring(45), 400, 540, 0.9, -30, 160, skia.BlendMode.kPlus)
    shockwave(c, 400, 540, 430, t, 0.3)
    light(c, 400, 540, 260, HOTWHITE, 255, core=2)
    spikes(c, 400, 540, 300, (220, 230, 255), 220)
    for i, sym in enumerate(["Fe", "Ca", "Au"]):
        element_chip(c, 1140 + i * 180, 820, 130, sym, 255, glow_a=170)
    orbi(c, 1720, 230, 95, t, "wide", (-0.9, 0.3), ears=0.8, rim=AMBER)
    text(c, "YOU ARE MADE OF", 1320, 470, 60, WHITE, 255, 800, spacing=6)
    text(c, "DEAD STARS", 1320, 620, 128, SOLAR, 255, 800, spacing=6)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    img = render_premium(draw, 3.0, samples=1)
    p = os.path.join(HERE, "out", "thumbnail.png")
    Image.fromarray(img).save(p)
    print(p)
