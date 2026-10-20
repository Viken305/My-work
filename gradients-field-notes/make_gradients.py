"""Original grainy mesh-gradient collection ("Field Notes").

Each piece: colour anchors blended in OKLab over a domain-warped plane,
then a soft light sweep and film grain. Fully seeded, so reproducible.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 3000, 2000

FIELD_NOTES = [
    ("01", "Tidepool Ember",   ["#0B3C49", "#1F6F78", "#6FC2B0", "#FF7A59", "#FFD3B5"], 11),
    ("02", "Ultraviolet Dusk", ["#140832", "#4B1D7A", "#B0368F", "#F06E7C", "#FFC07A"], 23),
    ("03", "Matcha Static",    ["#0F2A1D", "#3E6B48", "#9CC69B", "#E9F5DB", "#C9A93E"], 37),
    ("04", "Chrome Peach",     ["#2B2D42", "#8DA9C4", "#F6E7DA", "#F7A072", "#E85D4A"], 41),
    ("05", "Midnight Citrus",  ["#050A30", "#1B2CC1", "#00C2A8", "#C8F169", "#F9F871"], 53),
    ("06", "Rosewater Smoke",  ["#2E1F27", "#6E3B57", "#B07A92", "#E8C3CB", "#F7ECEE"], 67),
    ("07", "Solar Lichen",     ["#17181B", "#3B5A2A", "#8A9A3B", "#E0A800", "#F2E8C9"], 71),
    ("08", "Glacier Bloom",    ["#3F5E8C", "#7FA7D6", "#CFE6F2", "#F7D6E0", "#F28CB1"], 83),
]

# Series 2: more in the Tidepool Ember / Ultraviolet Dusk directions
TIDE_AND_DUSK = [
    ("T1", "Tidepool Ember II",  FIELD_NOTES[0][2], 101),
    ("T2", "Tidepool Ember III", FIELD_NOTES[0][2], 113),
    ("T3", "Reef Lantern",       ["#072E3A", "#145C64", "#4FB3A9", "#FF9466", "#FFE3C8"], 127),
    ("T4", "Saltwater Apricot",  ["#0E4A55", "#3A8F8E", "#A8DCD1", "#FFB38A", "#FF6F4F"], 139),
    ("T5", "Kelp Sunset",        ["#062A2F", "#0F5257", "#5C9E8F", "#F2795A", "#F9C9A7"], 151),
    ("D1", "Ultraviolet Dusk II",  FIELD_NOTES[1][2], 163),
    ("D2", "Ultraviolet Dusk III", FIELD_NOTES[1][2], 173),
    ("D3", "Neon Vesper",        ["#0F0526", "#3A1670", "#8E2DA8", "#FF5E8A", "#FFB26B"], 181),
    ("D4", "Orchid Afterglow",   ["#1C0B36", "#5A2380", "#C04A9E", "#FF8A8A", "#FFD3A1"], 191),
    ("D5", "Plum Ember",         ["#120621", "#43175F", "#9C2F7A", "#E85D5D", "#FFA35C"], 199),
    ("X1", "Ember Dusk",         ["#0B3C49", "#1F6F78", "#B0368F", "#F06E7C", "#FFC07A"], 211),
    ("X2", "Lilac Tide",         ["#123B4A", "#3E7F8C", "#C27BC0", "#F7A1A6", "#FFE0B8"], 223),
]

SERIES = {
    "field-notes": ("FIELD NOTES  —  8 original grain-mesh gradients", FIELD_NOTES),
    "tide-and-dusk": ("TIDE & DUSK  —  12 more in the Tidepool / Ultraviolet direction", TIDE_AND_DUSK),
}


def hex_to_srgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def srgb_to_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)


M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
               [0.2119034982, 0.6806995451, 0.1073969566],
               [0.0883024619, 0.2817188376, 0.6299787005]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
               [1.9779984951, -2.4285922050, 0.4505937099],
               [0.0259040371, 0.7827717662, -0.8086757660]])


def to_oklab(rgb):
    lms = srgb_to_linear(rgb) @ M1.T
    return np.cbrt(lms) @ M2.T


def from_oklab(lab):
    lms = (lab @ np.linalg.inv(M2).T) ** 3
    return linear_to_srgb(lms @ np.linalg.inv(M1).T)


def warp_field(x, y, rng, octaves=4, amp=0.22):
    """Smooth pseudo-noise from summed random sinusoids."""
    dx = np.zeros_like(x)
    dy = np.zeros_like(y)
    for o in range(octaves):
        f = 1.3 * (1.9 ** o)
        a = amp / (1.8 ** o)
        th1, th2 = rng.uniform(0, 2 * np.pi, 2)
        p1, p2 = rng.uniform(0, 2 * np.pi, 2)
        dx += a * np.sin(f * (x * np.cos(th1) + y * np.sin(th1)) * np.pi + p1)
        dy += a * np.sin(f * (x * np.cos(th2) + y * np.sin(th2)) * np.pi + p2)
    return x + dx, y + dy


def render(colors, seed, w=W, h=H):
    rng = np.random.default_rng(seed)
    aspect = w / h
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    x = xs / h  # 0..aspect
    y = ys / h  # 0..1
    # two passes of warping for liquid folds
    wx, wy = warp_field(x, y, rng)
    wx, wy = warp_field(wx, wy, rng, octaves=3, amp=0.12)

    labs = np.array([to_oklab(hex_to_srgb(c)) for c in colors])
    # dark anchor first gets a wider footprint; brightest stays a focal glow
    n_anchor = 8
    idx = np.concatenate([np.arange(len(colors)), rng.integers(0, len(colors), n_anchor - len(colors))])
    # softmax in log space: sharp colour regions, no underflow to black
    logws = []
    for i in idx:
        cx, cy = rng.uniform(-0.1, aspect + 0.1), rng.uniform(-0.1, 1.1)
        s = rng.uniform(0.16, 0.30) * (1.3 if i == 0 else 1.0)
        d2 = (wx - cx) ** 2 + (wy - cy) ** 2
        logws.append((-2.2 * (d2 / (2 * s * s)) ** 0.85).astype(np.float32))
    logws = np.stack(logws)
    wts = np.exp(logws - logws.max(axis=0))
    wsum = wts.sum(axis=0)
    acc = np.einsum("khw,kc->hwc", wts, labs[idx].astype(np.float32))
    lab = acc / wsum[..., None]

    # soft diagonal light sweep, applied to OKLab lightness
    ang = rng.uniform(0, 2 * np.pi)
    sweep = np.cos((x * np.cos(ang) + y * np.sin(ang)) * 1.6 + rng.uniform(0, 6))
    lab[..., 0] += 0.035 * sweep
    rgb = from_oklab(lab.reshape(-1, 3)).reshape(h, w, 3)

    # film grain: luminance-weighted, slightly stronger in midtones
    lum = rgb.mean(axis=2, keepdims=True)
    grain = rng.normal(0, 1, (h, w, 1)).astype(np.float32)
    rgb = rgb + grain * (0.028 + 0.03 * lum * (1 - lum))
    return (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)


def contact_sheet(thumbs, meta, title, path):
    tw, th = 720, 480
    pad, label = 40, 90
    cols = 4
    rows = -(-len(thumbs) // cols)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * pad, rows * (th + label) + (rows + 1) * pad + 110), "#F4F1EC")
    d = ImageDraw.Draw(sheet)
    try:
        big = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
        mid = ImageFont.truetype("DejaVuSans.ttf", 24)
        sm = ImageFont.truetype("DejaVuSansMono.ttf", 18)
    except OSError:
        big = mid = sm = ImageFont.load_default()
    d.text((pad, 40), title, fill="#1A1A1A", font=big)
    for k, (im, (num, name, colors, _)) in enumerate(zip(thumbs, meta)):
        cx = pad + (k % cols) * (tw + pad)
        cy = 110 + pad + (k // cols) * (th + label + pad)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (cx, cy))
        d.text((cx, cy + th + 10), f"{num}  {name}", fill="#1A1A1A", font=mid)
        sx = cx
        for c in colors:
            d.rectangle([sx, cy + th + 48, sx + 26, cy + th + 74], fill=c)
            sx += 30
        d.text((sx + 8, cy + th + 52), " ".join(c.lstrip("#") for c in colors[:3]) + " …", fill="#666", font=sm)
    sheet.save(path, quality=92)


# usage: make_gradients.py OUT_DIR [field-notes|tide-and-dusk]
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
series = sys.argv[2] if len(sys.argv) > 2 else "field-notes"
title, palettes = SERIES[series]

thumbs = []
for num, name, colors, seed in palettes:
    img = Image.fromarray(render(colors, seed))
    slug = name.lower().replace(" ", "-")
    img.save(OUT / f"{num}-{slug}.png", optimize=True)
    thumbs.append(img)
    print("wrote", num, name, flush=True)

contact_sheet(thumbs, palettes, title, OUT / f"00-{series}-contact-sheet.jpg")
(OUT / "palettes.json").write_text(json.dumps(
    [{"id": n, "name": nm, "colors": c, "seed": s} for n, nm, c, s in palettes], indent=2))
