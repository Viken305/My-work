"""Storyboard: one frame per shot, rendered from the real animation at the middle of the shot's narration line, laid
out on a sheet with the line, the action and the sound notes from project.json.

  python3 storyboard.py   -> out/panels/NN.png (1080x1920) + out/storyboard_1.png
Narration clips must exist (python3 voiceover.py partN).
"""
import importlib, os, textwrap

import numpy as np
import skia
from PIL import Image

import render
from kit import INK, PAPER, SMOKE, AMBER, H, HERE, W, col, label
from project import P

LINES = {ln["id"]: (part["id"], ln["text"]) for part in P["parts"] for ln in part["lines"]}


def panel_time(mod, line):
    t0 = mod.VO[line]
    return t0 + mod.TM.dur[line] * 0.7


def main():
    out = os.path.join(HERE, "out", "panels")
    os.makedirs(out, exist_ok=True)
    shots = P["shots"]
    for s in shots:
        part, _ = LINES[s["line"]]
        mod = importlib.import_module(part)
        Image.fromarray(render.frame(mod, panel_time(mod, s["line"]))).save(os.path.join(out, f"{s['n']:02d}.png"))
        print(f"panel {s['n']:02d}", flush=True)
    cols, pw, ph, notes = 4, 360, 640, 250
    rows = (len(shots) + cols - 1) // cols
    sw, sh = cols * (pw + 40) + 40, rows * (ph + notes + 40) + 140
    surf = skia.Surface(sw, sh)
    c = surf.getCanvas()
    c.clear(col(INK))
    label(c, P["title"].upper() + " · STORYBOARD", 40, 80, 40, "black", PAPER)
    for i, s in enumerate(shots):
        r, k = divmod(i, cols)
        x, y = 40 + k * (pw + 40), 140 + r * (ph + notes + 40)
        arr = np.asarray(Image.open(os.path.join(out, f"{s['n']:02d}.png")).convert("RGBA").resize((pw, ph)))
        c.drawImage(skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType), x, y)
        label(c, f"{s['n']:02d} · {s['line']}", x, y + ph + 34, 24, "mono_bold", AMBER)
        yy = y + ph + 66
        for txt, rgb in ((LINES[s["line"]][1], PAPER), (s["action"], SMOKE), ("♪ " + s["sound"], SMOKE)):
            for ln in textwrap.wrap(txt, 40)[:3]:
                label(c, ln, x, yy, 17, "mono", rgb)
                yy += 22
            yy += 8
    Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]).save(
        os.path.join(HERE, "out", "storyboard_1.png"))
    print(os.path.join(HERE, "out", "storyboard_1.png"))


if __name__ == "__main__":
    main()
