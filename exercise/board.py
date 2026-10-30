"""Style-frames board: the three directions side by side, two frames each, with their caption idea.

  python3 board.py   -> out/style_frames.png
"""
import os

from PIL import Image

from kit import *  # noqa: F401,F403

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
STYLES = [
    ("A", "RUSH HOUR", "Body as a city at night: heart = power station.",
     "CAPTIONS: dot-matrix highway sign, lit as spoken", (255, 178, 60)),
    ("B", "BEAT DROP", "Workout as a rhythm game: a runner made of EQ bars.",
     "CAPTIONS: words are notes that hit on the beat", (255, 46, 160)),
    ("C", "FOGGED GLASS", "Macro skin behind a steamed-up gym window.",
     "CAPTIONS: wiped into the fog by a fingertip", (120, 200, 255)),
]


def main():
    tw, th, pad = 400, 711, 36
    sw = 3 * tw * 2 + 0                                     # placeholder (recomputed below)
    sw = pad + 3 * (2 * tw + 16 + pad)
    sh = 230 + th + 260
    s = skia.Surface(sw, sh)
    c = s.getCanvas()
    c.drawPaint(fillp((10, 10, 16)))
    label(c, "WHAT HAPPENS INSIDE YOUR BODY DURING EXERCISE", pad, 90, 64, "display", (240, 240, 250), 255)
    label(c, "STYLE FRAMES · THREE DIRECTIONS · 9:16", pad, 140, 26, "mono", (150, 156, 180), 255, tracking=0.1)
    for i, (key, name, idea, cap, rgb) in enumerate(STYLES):
        x = pad + i * (2 * tw + 16 + pad)
        y = 200
        label(c, f"{key} · {name}", x, y, 44, "overpass_black", rgb, 255)
        for j in (1, 2):
            img = Image.open(os.path.join(OUT, f"frame_{key}{j}.png")).convert("RGB").resize((tw, th), Image.LANCZOS)
            sk = skia.Image.fromarray(np.dstack([np.asarray(img), np.full((th, tw), 255, np.uint8)]))
            c.drawImage(sk, x + (j - 1) * (tw + 16), y + 30)
        label(c, idea, x, y + th + 80, 24, "bold", (230, 232, 240), 255)
        label(c, cap, x, y + th + 124, 22, "mono_bold", rgb, 255, tracking=0.04)
    p = os.path.join(OUT, "style_frames.png")
    Image.fromarray(s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]).save(p)
    print(p)


if __name__ == "__main__":
    main()
