"""Storyboard sheet, Shorts thumbnail and an .srt caption file, all from the real film code and timings.

  python3 extras.py storyboard   -> out/storyboard.png (20 key frames with timecodes)
  python3 extras.py thumb        -> out/thumb_short.png (1080x1920)
  python3 extras.py srt          -> out/captions_en.srt
"""
import importlib, os, sys

import skia
from PIL import Image

import render
from film import *  # noqa: F401,F403
from script import PARTS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
BOARD = [  # (part, local time, shot title)
    ("part1", 1.15, "Cold open: the lid fights sleep"),
    ("part1", 6.6, "Title: 72 hours without sleep"),
    ("part2", 2.5, "Hour 0: Sam wakes at 07:00"),
    ("part2", 13.5, "Adenosine jar, coffee sleeve"),
    ("part2", 22.4, "04:00: body clock at its lowest"),
    ("part3", 1.0, "Hour 24 slam"),
    ("part3", 3.15, "Reaction time: the mug smashes"),
    ("part3", 10.6, "24 h awake = 0.10% alcohol"),
    ("part3", 17.0, "Amygdala +60%"),
    ("part3", 25.9, "Hippocampus: 40% less memory"),
    ("part3", 34.0, "Hunger hormones, the fridge"),
    ("part4", 5.5, "Hour 36: body on alarm"),
    ("part4", 18.9, "Beta-amyloid +5%"),
    ("part4", 27.0, "Hour 48: eyes open, brain off"),
    ("part4", 33.5, "Microsleep: 3 s = 90 m"),
    ("part5", 3.0, "Hour 72: the walls breathe"),
    ("part5", 13.6, "The record: 264 hours"),
    ("part5", 17.0, "Recovery: deep sleep"),
    ("part5", 24.8, "7-9 hours a night"),
    ("part5", 29.0, "Remember the jar"),
]


def offsets():
    off, t = {}, 0.0
    for name in render.PARTS:
        off[name] = t
        t += importlib.import_module(name).DURATION
    return off, t


def tc(sec):
    return f"{int(sec // 60)}:{sec % 60:04.1f}"


def storyboard():
    off, total = offsets()
    tw, th, cols, pad, cap = 324, 576, 5, 28, 92
    rows = (len(BOARD) + cols - 1) // cols
    sw, sh = cols * tw + (cols + 1) * pad, rows * (th + cap) + (rows + 1) * pad + 150
    s = skia.Surface(sw, sh)
    c = s.getCanvas()
    c.drawPaint(fillp((10, 12, 22)))
    label(c, "72 HOURS WITHOUT SLEEP", pad, 82, 64, "display", PAPER, 255)
    label(c, f"STORYBOARD · 9:16 SHORT · {tc(total)} · {len(BOARD)} KEY FRAMES", pad, 124, 22, "mono", ASH, 255, tracking=0.08)
    for i, (part, t, title) in enumerate(BOARD):
        mod = importlib.import_module(part)
        img = Image.fromarray(render.frame(mod, t)).resize((tw, th), Image.LANCZOS)
        x = pad + (i % cols) * (tw + pad)
        y = 150 + pad + (i // cols) * (th + cap + pad)
        sk = skia.Image.fromarray(np.dstack([np.asarray(img), np.full((th, tw), 255, np.uint8)]))
        c.drawImage(sk, x, y)
        g = off[part] + t
        acc = CYAN if g < off["part3"] else AMBER if g < off["part4"] + 8 else RED
        if part == "part5" and t > 14:
            acc = CYAN
        label(c, f"{i + 1:02d}", x, y + th + 38, 26, "mono_bold", acc, 255)
        label(c, tc(g), x + tw, y + th + 38, 22, "mono", ASH, 255, "right")
        label(c, title, x, y + th + 74, 21, "bold", PAPER, 255)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "storyboard.png")
    Image.fromarray(s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]).save(p)
    print(p)


def thumb():
    import part1
    import premium
    s = skia.Surface(W, H)
    c = s.getCanvas()
    part1.eye(c, 4.4, 0.85)
    c.drawRect(skia.Rect.MakeWH(W, 560), grad_v(0, 560, (8, 6, 20), (8, 6, 20), 235, 0))
    c.drawRect(skia.Rect.MakeLTRB(0, 1150, W, H), grad_v(1150, 1500, (8, 6, 20), (8, 6, 20), 0, 240))
    for dx, rgb, a in ((-8, CYAN, 170), (8, RED, 170), (0, PAPER, 255)):
        label(c, "72 HOURS", W / 2 + dx, 360, 230, "display", rgb, a, "center")
    label(c, "WITHOUT SLEEP", W / 2, 450, 60, "mono_bold", RED, 255, "center", tracking=0.25)
    label(c, "WHAT HAPPENS TO", W / 2, 1360, 64, "display", PAPER, 255, "center")
    label(c, "YOUR BODY", W / 2, 1450, 96, "display", AMBER, 255, "center")
    rgb = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
    out = premium.post(rgb, 1.0, bloom=0.7, ca=0.8, grain=6.0)
    p = os.path.join(OUT, "thumb_short.png")
    Image.fromarray(out).save(p)
    print(p)


def srt():
    from timing import Timing
    off, _ = offsets()
    lines, n = [], 1
    for name in render.PARTS:
        mod = importlib.import_module(name)
        tm = Timing(name, mod.VO)
        for key, text in PARTS[name]:
            a, b = off[name] + tm.vo[key], off[name] + tm.end(key)
            f = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(x % 1 * 1000):03d}"  # noqa: E731
            lines.append(f"{n}\n{f(a)} --> {f(b)}\n{text}\n")
            n += 1
    p = os.path.join(OUT, "captions_en.srt")
    open(p, "w").write("\n".join(lines))
    print(p)


if __name__ == "__main__":
    {"storyboard": storyboard, "thumb": thumb, "srt": srt}[sys.argv[1]]()
