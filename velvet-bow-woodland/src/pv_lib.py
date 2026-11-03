"""Helpers for Creative Market preview compositions."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
W, H = 1820, 1214
CREAM, PAPER, BURG, DEEP, GOLD, SAGE, INK = (246, 239, 228), (239, 229, 212), (92, 26, 38), (58, 16, 24), (184, 148, 92), (138, 154, 128), (60, 36, 34)
F = "/usr/share/fonts/truetype/crosextra/"
def font(style, size): return ImageFont.truetype(F + {"r": "Caladea-Regular.ttf", "i": "Caladea-Italic.ttf", "b": "Caladea-Bold.ttf", "bi": "Caladea-BoldItalic.ttf"}[style], size)
_cache = {}
def asset(path, maxw, maxh=None, rot=0):
    key = path
    if key not in _cache: _cache[key] = Image.open(path).convert("RGBA")
    im = _cache[key].copy(); im.thumbnail((maxw, maxh or maxw), Image.LANCZOS)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    return im
def a(name, maxw, maxh=None, rot=0): return asset(f"final/{name}.png", maxw, maxh, rot)
def bg(name, dark=1.0, blur=0):
    im = Image.open(f"raw/bg/{name}_hi.png").convert("RGB")
    im = ImageOps.fit(im, (W, H), Image.LANCZOS)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    if dark != 1.0: im = ImageEnhance.Brightness(im).enhance(dark)
    return im.convert("RGBA")
def solid(col): return Image.new("RGBA", (W, H), col + (255,))
def paper(col=PAPER, seed=1, grain=10):
    rnd = random.Random(seed)
    base = Image.new("RGBA", (W, H), col + (255,))
    noise = Image.effect_noise((W // 2, H // 2), grain).resize((W, H)).convert("L")
    tex = Image.merge("RGBA", [noise, noise, noise, Image.new("L", (W, H), 18)])
    base.alpha_composite(tex); return base
def vignette(img, strength=0.55):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    d.ellipse([-W * .25, -H * .3, W * 1.25, H * 1.3], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(220))
    dark = Image.new("RGBA", (W, H), (20, 6, 10, int(255 * strength)))
    dark.putalpha(ImageOps.invert(m).point(lambda v: int(v * strength)))
    img.alpha_composite(dark); return img
def shadow_of(im, blur=18, opacity=0.45, color=(30, 12, 10)):
    pad = blur * 3
    al = im.getchannel("A")
    sh = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), color + (0,))
    m = Image.new("L", sh.size, 0); m.paste(al, (pad, pad))
    m = m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * opacity))
    sh.putalpha(m); return sh, pad
def place(base, im, cx, cy, shadow=True, sdx=10, sdy=16, blur=18, opacity=0.4, anchor="c"):
    x = int(cx - im.width / 2); y = int(cy - im.height / 2) if anchor == "c" else int(cy - im.height)
    if shadow:
        sh, pad = shadow_of(im, blur, opacity); base.alpha_composite(sh, (x - pad + sdx, y - pad + sdy)) if x - pad + sdx >= 0 and y - pad + sdy >= 0 else base.paste(sh, (x - pad + sdx, y - pad + sdy), sh)
    if x >= 0 and y >= 0 and x + im.width <= base.width and y + im.height <= base.height: base.alpha_composite(im, (x, y))
    else: base.paste(im, (x, y), im)
def text(base, xy, s, f, fill, anchor="mm", spacing=0):
    d = ImageDraw.Draw(base)
    if not spacing: d.text(xy, s, font=f, fill=fill, anchor=anchor); return
    widths = [d.textlength(ch, font=f) + spacing for ch in s]; total = sum(widths) - spacing
    x = xy[0] - total / 2 if anchor[0] == "m" else xy[0]
    for ch, w in zip(s, widths): d.text((x, xy[1]), ch, font=f, fill=fill, anchor="l" + anchor[1]); x += w
def rule(base, cx, y, w, col=GOLD, dia=True):
    d = ImageDraw.Draw(base); d.line([(cx - w / 2, y), (cx - 14, y)], fill=col, width=2); d.line([(cx + 14, y), (cx + w / 2, y)], fill=col, width=2)
    if dia: d.polygon([(cx, y - 7), (cx + 7, y), (cx, y + 7), (cx - 7, y)], fill=col)
def card(img, border=26, col=(250, 246, 238), radius=0):
    """Put an image on a paper card with a white border (print look)."""
    c = Image.new("RGBA", (img.width + 2 * border, img.height + 2 * border), col + (255,))
    c.alpha_composite(img.convert("RGBA"), (border, border)); return c
def sparkle(base, n=40, seed=3, col=(232, 205, 150), area=None):
    rnd = random.Random(seed); d = ImageDraw.Draw(base)
    x0, y0, x1, y1 = area or (0, 0, W, H)
    for _ in range(n):
        x, y, r = rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(2, 7)
        al = int(rnd.uniform(120, 230))
        d.polygon([(x, y - r * 2.2), (x + r * .45, y - r * .45), (x + r * 2.2, y), (x + r * .45, y + r * .45), (x, y + r * 2.2), (x - r * .45, y + r * .45), (x - r * 2.2, y), (x - r * .45, y - r * .45)], fill=col + (al,))
def save(img, name): img.convert("RGB").save(f"listing_v2/{name}.jpg", quality=93)
