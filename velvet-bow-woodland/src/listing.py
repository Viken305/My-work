"""Creative Market preview images (1820x1214)."""
import glob, os
from PIL import Image, ImageDraw, ImageFont
W, H = 1820, 1214
CREAM, BURG, GOLD = (246, 239, 228), (92, 26, 38), (176, 141, 87)
IT = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"; RG = "/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf"
os.makedirs("listing", exist_ok=True)
def th(p, s):
    im = Image.open(p).convert("RGBA"); im.thumbnail((s, s), Image.LANCZOS); return im
def grid(files, title, out, bg=CREAM, cols=None, pad=30, top=150):
    c = Image.new("RGBA", (W, H), bg + (255,)); d = ImageDraw.Draw(c)
    col = BURG if bg == CREAM else CREAM
    d.text((W / 2, 80), title, font=ImageFont.truetype(IT, 64), fill=col, anchor="mm")
    n = len(files); cols = cols or min(n, 8); rows = (n + cols - 1) // cols
    cw, ch = (W - 2 * pad) / cols, (H - top - pad) / rows
    for i, f in enumerate(files):
        im = th(f, int(min(cw, ch) * 0.9))
        cx = pad + (i % cols) * cw + cw / 2; cy = top + (i // cols) * ch + ch / 2
        c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
    c.convert("RGB").save(f"listing/{out}", quality=92)
# Cover
c = Image.new("RGBA", (W, H), CREAM + (255,)); d = ImageDraw.Draw(c)
d.rectangle([30, 30, W - 30, H - 30], outline=GOLD, width=4)
picks = ["c01_fawn", "c05_bunny", "c03_fox", "c07_bear", "c10_owl", "c11_hedgehog", "c14_lamb"]
xs = [80 + 237 * i + 118 for i in range(7)]
for x, p in zip(xs, picks):
    im = th(f"final/characters/{p}.png", 225 if p in ("c01_fawn", "c07_bear") else 400); im.thumbnail((225, 420)); c.alpha_composite(im, (int(x - im.width / 2), 960 - im.height))
d.text((W / 2, 210), "Velvet Bow Woodland", font=ImageFont.truetype(IT, 120), fill=BURG, anchor="mm")
d.text((W / 2, 320), "90 VINTAGE CHRISTMAS ILLUSTRATIONS  ·  PNG 300 DPI  ·  PATTERNS  ·  CARDS", font=ImageFont.truetype(RG, 34), fill=GOLD, anchor="mm")
d.text((W / 2, 1120), "70 transparent elements  ·  4 scenes  ·  10 seamless patterns  ·  6 card & tag templates", font=ImageFont.truetype(RG, 32), fill=BURG, anchor="mm")
c.convert("RGB").save("listing/01_cover.jpg", quality=92)
grid(sorted(glob.glob("final/characters/*.png")), "16 Woodland Characters", "02_characters.jpg")
grid(sorted(glob.glob("final/bows/*.png")) + sorted(glob.glob("final/botanicals/*.png")), "12 Bows & Ribbons  ·  12 Winter Botanicals", "03_bows_botanicals.jpg", cols=8)
grid(sorted(glob.glob("final/props/*.png")), "20 Festive Treasures", "04_props.jpg", cols=7)
grid(sorted(glob.glob("final/frames/*.png")) + sorted(glob.glob("final/phrases/*.png")), "4 Wreaths & Frames  ·  6 Hand-Lettered Phrases", "05_frames_phrases.jpg", cols=5)
grid(sorted(glob.glob("final/scenes/*.jpg")), "4 Painted Scenes", "06_scenes.jpg", cols=4)
grid(sorted(glob.glob("final/patterns/*.jpg")), "10 Seamless Patterns", "07_patterns.jpg", cols=5)
grid(sorted(glob.glob("final/templates/*")), "Cards & Gift Tags", "08_templates.jpg", bg=(70, 52, 58), cols=3)
print("ok")
