"""Thumbnails for "Your Body Is a Rhythm Game" (Beat Drop).

  python3 thumbnail.py      -> out/thumb_vertical.png (1080x1920, Shorts cover) + out/thumb_16x9.png (1280x720)

The cover is drawn with the same engine as the video: the Level 4 stage, the equaliser runner at full power over the
racing ECG, gold 180 BPM note on the highway, and the title on top (kept clear of the Shorts UI at the bottom/right).
"""
import os

import numpy as np
import skia
from PIL import Image

import premium
from game import *  # noqa: F401,F403
from engine import HERE

G = Game("part5")
# freeze on a kick so the lights, runner and speaker-heart are at their peak
T = max((3.0 + i / 300 for i in range(300)), key=G.beat)


DY = 250                       # the whole stage sits lower, under the title


def scene(c, t, title=True):
    c.save()
    c.translate(0, DY)
    G.stage(c, t)
    top = mix((6, 2, 14), RED, 0.10)                              # extend the stage backdrop up behind the HUD
    c.drawRect(skia.Rect.MakeLTRB(0, -DY, W, 1), grad_v(-DY, 1, top, top))
    light(c, 524, 817, 700, RED, 90)
    ecg(c, t, 860, 255)
    runner(c, G, t, 540, 880, 1.05, 255, level=lambda tt: 0.85, rgb0=MAG, rgb1=RED)
    for j, r in enumerate((260, 420, 600)):                      # shock rings off the heart
        c.drawCircle(524, 817, r, stroke(GOLD, 9 - 2.5 * j, 150 - 40 * j))
    # notes on the highway: three lane gems on their way in, the gold 180 on the hit line
    for lane, txt, d in ((0, "HEART", 0.55), (1, "LUNGS", 0.3), (3, "MUSCLE", 0.62)):
        x, y, sc = note_pos(d, lane)
        gem(c, x, y, sc, txt, LANES[lane])
    x, y, _ = note_pos(1.0, None)
    for k in range(3):
        c.drawCircle(x, y, 120 + 90 * k, stroke(GOLD, 10 - 3 * k, 200 - 60 * k))
    gem(c, x, y - 10, 1.0, "180 BPM", GOLD, gold=True)
    outlined(c, "PERFECT!", 540, HIT_Y - 120, 64, "bungee", WHITE, glow_rgb=GOLD)
    c.restore()


def ecg(c, t, y, a):
    pts = []
    for i in range(121):
        x = i * 9
        ph = G.phase(t - (W - x) / 900) % 1.0
        v = 0.0
        if ph < 0.06:
            v = -math.sin(ph / 0.06 * math.pi) * 0.25
        elif ph < 0.1:
            v = math.sin((ph - 0.06) / 0.04 * math.pi) * 1.0
        elif ph < 0.16:
            v = -math.sin((ph - 0.1) / 0.06 * math.pi) * 0.45
        pts.append((x, y - v * 260))
    p = path_of(pts)
    c.drawPath(p, stroke(RED, 22, 0.3 * a, plus=True))
    c.drawPath(p, stroke(mix(RED, WHITE, 0.3), 7, a))


def title(c, t):
    outlined(c, "YOUR BODY", 540, 395, 150, "bungee", WHITE, glow_rgb=MAG)
    outlined(c, "IS A", 540, 492, 72, "bungee", CYN, glow_rgb=CYN)
    outlined(c, "RHYTHM", 540, 640, 170, "bungee", GOLD, glow_rgb=RED, ow=0.1)
    outlined(c, "GAME", 540, 795, 170, "bungee", GOLD, glow_rgb=RED, ow=0.1)
    # the HUD corner chips, as in the video
    label(c, "HEART BPM", 60, 120, 30, "bungee", RED)
    label(c, "180", 60, 190, 72, "bungee", WHITE)
    label(c, "LV 4 · MAX HEART", 1020, 120, 30, "bungee", GOLD, 255, "right")
    label(c, "X254", 1020, 190, 72, "bungee", CYN, 255, "right")


def draw(c, t):
    scene(c, t)


def render(with_title=True):
    return premium.render_premium(draw, T, samples=1, overlay=title if with_title else None, grain=2.0, ca=1.0, bloom=1.25)


def landscape(img):
    """1280x720: the title on the left, the runner and highway cropped from the vertical cover on the right."""
    s = skia.Surface(1280, 720)
    c = s.getCanvas()
    c.drawPaint(fillp((6, 2, 14)))
    crop = Image.fromarray(img).convert("RGB").crop((60, 520 + DY - 80, 1020, 1610 + DY - 80)).resize((635, 720), Image.LANCZOS)
    arr = np.dstack([np.asarray(crop), np.full((720, 635), 255, np.uint8)])
    c.drawImage(skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType), 645, 0)
    c.drawRect(skia.Rect.MakeLTRB(560, 0, 760, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(560, 0), skia.Point(760, 0)], [skia.Color(6, 2, 14, 255), skia.Color(6, 2, 14, 0)])))
    light(c, 330, 360, 420, MAG, 70)
    outlined(c, "YOUR BODY", 330, 205, 104, "bungee", WHITE, glow_rgb=MAG)
    outlined(c, "IS A", 330, 280, 52, "bungee", CYN, glow_rgb=CYN)
    outlined(c, "RHYTHM", 330, 410, 128, "bungee", GOLD, glow_rgb=RED, ow=0.1)
    outlined(c, "GAME", 330, 540, 128, "bungee", GOLD, glow_rgb=RED, ow=0.1)
    label(c, "LEVEL 4 · MAX HEART", 330, 630, 40, "bungee", RED, 255, "center")
    return s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)


if __name__ == "__main__":
    out = os.path.join(HERE, "out")
    v = render(True)
    Image.fromarray(v).convert("RGB").save(os.path.join(out, "thumb_vertical.png"))
    Image.fromarray(landscape(render(False))).convert("RGB").save(os.path.join(out, "thumb_16x9.png"))
    print("t =", round(T, 3), "->", out)
