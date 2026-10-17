"""Storyboard sheets, one per part: python3 storyboard.py [1 2 ...] -> out/storyboards/partN_storyboard.png"""
import os, sys, textwrap

import skia
from PIL import Image, ImageDraw, ImageFont

from boards import PANELS
from engine import FONT_FILES, H, HERE, W, finish

OUT = os.path.join(HERE, "out", "storyboards")
PW, PH, GAP, CAP = 600, 338, 30, 200


def render_panel(fn, t=2.0):
    s = skia.Surface(W, H)
    c = s.getCanvas()
    fn(c, t)
    from engine import vignette
    vignette(c, 110)
    return Image.fromarray(finish(s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType), t)).resize((PW, PH), Image.LANCZOS)


def sheet(n):
    title, timing, panels = PANELS[n]
    rows = (len(panels) + 2) // 3
    img = Image.new("RGB", (3 * PW + 4 * GAP, 170 + rows * (PH + CAP) + 30), (20, 18, 56))
    d = ImageDraw.Draw(img)
    big, mid = ImageFont.truetype(FONT_FILES[800], 46), ImageFont.truetype(FONT_FILES[800], 22)
    body, it = ImageFont.truetype(FONT_FILES[600], 19), ImageFont.truetype(FONT_FILES[600], 19)
    d.text((GAP, 34), f"PART {n} · {title}", font=big, fill=(255, 153, 51))
    d.text((GAP, 100), f"{timing}   ·   storyboard key frames (they animate in the final video)", font=mid, fill=(220, 214, 240))
    for i, (fn, key, line, action) in enumerate(panels):
        x, y = GAP + (i % 3) * (PW + GAP), 170 + (i // 3) * (PH + CAP)
        img.paste(render_panel(fn), (x, y))
        d.rectangle([x, y, x + PW - 1, y + PH - 1], outline=(255, 153, 51), width=2)
        d.text((x, y + PH + 10), f"{n}.{i + 1}  ·  {key}", font=mid, fill=(255, 194, 51))
        yy = y + PH + 42
        for ln in textwrap.wrap(line, 56)[:3]:
            d.text((x, yy), ln, font=it, fill=(255, 255, 255))
            yy += 24
        yy += 6
        for ln in textwrap.wrap(action, 58)[:4]:
            d.text((x, yy), ln, font=body, fill=(170, 220, 215))
            yy += 24
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"part{n}_storyboard.png")
    img.save(p)
    return p


if __name__ == "__main__":
    for n in [int(a) for a in sys.argv[1:]] or sorted(PANELS):
        print(sheet(n))
