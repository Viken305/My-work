"""Print-ready 5x7 cards and gift tags (300 DPI) assembled from the finished art."""
import os
from PIL import Image, ImageDraw, ImageFont
CREAM, BURG, GOLD = (246, 239, 228), (92, 26, 38), (176, 141, 87)
ITAL = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"
os.makedirs("final/templates", exist_ok=True)
def art(p, w, h):
    im = Image.open(f"final/{p}.png").convert("RGBA"); im.thumbnail((w, h), Image.LANCZOS); return im
def put(base, im, cx, cy): base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
def border(c, inset, col=GOLD, w=6):
    ImageDraw.Draw(c).rectangle([inset, inset, c.width - inset, c.height - inset], outline=col, width=w)
W, H = 1500, 2100  # 5x7 in
# Card 1: fawn wreath + Merry & Bright
c = Image.new("RGBA", (W, H), CREAM + (255,)); border(c, 60)
put(c, art("frames/w01_wreath_fawn", 1150, 1150), W / 2, 760)
put(c, art("phrases/t01_merry_bright", 1000, 560), W / 2, 1640)
c.convert("RGB").save("final/templates/card01_merry_bright_5x7.jpg", quality=95, dpi=(300, 300))
# Card 2: scene top + Season's Greetings
c = Image.new("RGBA", (W, H), CREAM + (255,))
sc = Image.open("final/scenes/s04_tree_gathering.jpg").convert("RGBA")
sc = sc.resize((W - 160, int((W - 160) * sc.height / sc.width)), Image.LANCZOS).crop((0, 0, W - 160, 1400))
c.alpha_composite(sc, (80, 80)); border(c, 80, w=8)
put(c, art("phrases/t04_seasons_greetings", 1000, 460), W / 2, 1790)
c.convert("RGB").save("final/templates/card02_seasons_greetings_5x7.jpg", quality=95, dpi=(300, 300))
# Card 3: garland + fox + Warm Wishes
c = Image.new("RGBA", (W, H), CREAM + (255,)); border(c, 60)
put(c, art("frames/w04_garland_swag", 1380, 520), W / 2, 330)
put(c, art("characters/c04_fox_walk", 1150, 760), W / 2, 1010)
put(c, art("phrases/t06_warm_wishes", 1000, 480), W / 2, 1690)
c.convert("RGB").save("final/templates/card03_warm_wishes_5x7.jpg", quality=95, dpi=(300, 300))
# Gift tags 2.5x4 in, transparent corners outside the tag shape
TW, TH = 750, 1200
def tag(name, char, bow, top_col):
    t = Image.new("RGBA", (TW, TH), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    d.polygon([(110, 0), (TW - 110, 0), (TW, 110), (TW, TH), (0, TH), (0, 110)], fill=CREAM + (255,), outline=top_col, width=8)
    d.ellipse([TW / 2 - 34, 70, TW / 2 + 34, 138], fill=(0, 0, 0, 0), outline=GOLD, width=8)
    put(t, art(bow, 300, 200), TW / 2, 230)
    put(t, art(char, 520, 520), TW / 2, 610)
    f = ImageFont.truetype(ITAL, 64)
    for i, label in enumerate(("To:", "From:")):
        y = 940 + i * 120
        d.text((90, y), label, font=f, fill=BURG); d.line([(260, y + 62), (TW - 90, y + 62)], fill=GOLD, width=4)
    t.save(f"final/templates/{name}.png", dpi=(300, 300))
tag("tag01_bunny", "characters/c05_bunny", "bows/b01_velvet_classic", BURG)
tag("tag02_bear", "characters/c08_bear_stand", "bows/b04_tartan", BURG)
tag("tag03_hedgehog", "characters/c11_hedgehog", "bows/b10_bow_bell", BURG)
print("ok")
