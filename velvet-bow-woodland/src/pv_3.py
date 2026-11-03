import sys, glob; sys.path.insert(0, "src")
from pv_lib import *

# 08 THE DETAILS — magnifier on the fur
img = paper(CREAM, grain=12)
fox = Image.open("final/characters/c03_fox.png").convert("RGBA")
big = fox.copy(); big.thumbnail((620, 1000), Image.LANCZOS)
place(img, big, 430, 1150, anchor="b", sdx=0, sdy=8, blur=14, opacity=0.3)
sx = big.width / fox.width
zx, zy = int(fox.width * 0.42), int(fox.height * 0.27)   # bow & chest area
crop = fox.crop((zx, zy, zx + 620, zy + 620))
R = 270; lens = Image.new("RGBA", (2 * R, 2 * R), CREAM + (255,)); lens.alpha_composite(crop.resize((2 * R, 2 * R), Image.LANCZOS))
m = Image.new("L", (2 * R, 2 * R), 0); ImageDraw.Draw(m).ellipse([0, 0, 2 * R - 1, 2 * R - 1], fill=255); lens.putalpha(m)
lx, ly = 1000, 560
tx, ty = 430 - big.width / 2 + (zx + 310) * sx, 1150 - big.height + (zy + 310) * sx
d = ImageDraw.Draw(img); d.line([(tx, ty), (lx - R * 0.7, ly + R * 0.7)], fill=GOLD, width=3)
d.ellipse([tx - 60 * 1, ty - 60, tx + 60, ty + 60], outline=GOLD, width=4)
place(img, lens, lx, ly, sdx=10, sdy=16, blur=24, opacity=0.35)
d = ImageDraw.Draw(img); d.ellipse([lx - R - 10, ly - R - 10, lx + R + 10, ly + R + 10], outline=GOLD, width=16); d.ellipse([lx - R - 14, ly - R - 14, lx + R + 14, ly + R + 14], outline=(140, 108, 60), width=3)
text(img, (1590, 360), "Every", font("i", 90), BURG); text(img, (1590, 460), "brushstroke,", font("i", 74), BURG); text(img, (1590, 550), "every whisker", font("i", 74), BURG)
rule(img, 1590, 625, 320)
for k, l in enumerate(["transparent PNG", "300 DPI", "up to 4000 px", "print up to 13 inches"]):
    text(img, (1590, 690 + k * 52), l, font("i", 36), INK)
save(img, "08_the_details")

# 09 HERBARIUM — winter botanicals specimen sheet
img = paper((233, 222, 199), grain=18, seed=5)
d = ImageDraw.Draw(img); d.rectangle([34, 34, W - 34, H - 34], outline=(150, 118, 72), width=2)
text(img, (W / 2, 100), "A Winter Herbarium", font("i", 84), (78, 46, 30))
text(img, (W / 2, 168), "TWELVE BOTANICAL SPECIMENS", font("r", 24), (150, 118, 72), spacing=7)
labels = ["Holly", "Mistletoe", "Pine", "Winterberry", "Dried Orange", "Christmas Rose", "Cedar", "Eucalyptus", "Pine & Cone", "Poinsettia", "Cotton", "Winter Posy"]
latin = ["Ilex aquifolium", "Viscum album", "Pinus sylvestris", "Ilex verticillata", "Citrus sinensis", "Helleborus niger", "Juniperus", "Eucalyptus cinerea", "Pinus nigra", "Euphorbia pulcherrima", "Gossypium", "Bouquet d'hiver"]
fs = sorted(glob.glob("final/botanicals/*.png")); cw, ch = (W - 120) / 6, 470
for i, f in enumerate(fs):
    cx = 60 + (i % 6) * cw + cw / 2; by = 600 + (i // 6) * ch
    place(img, asset(f, int(cw * 0.82), 330), cx, by, anchor="b", sdx=3, sdy=5, blur=6, opacity=0.25)
    d = ImageDraw.Draw(img); d.rectangle([cx - 105, by + 14, cx + 105, by + 96], outline=(150, 118, 72), width=1)
    text(img, (cx, by + 40), f"No. {i + 1}  ·  {labels[i]}", font("i", 24), (78, 46, 30))
    text(img, (cx, by + 74), latin[i], font("i", 18), (130, 100, 62))
save(img, "09_herbarium")

# 10 ADVENT OF TREASURES — 20 numbered tiles on velvet
img = vignette(bg("velvet_a", dark=0.55), 0.5)
text(img, (W / 2, 95), "Twenty Festive Treasures", font("i", 84), CREAM)
text(img, (W / 2, 160), "AN ADVENT OF LITTLE DETAILS", font("r", 24), GOLD, spacing=7)
fs = sorted(glob.glob("final/props/*.png")); tw, th_ = 312, 228; gx, gy = 20, 18
x0 = (W - (5 * tw + 4 * gx)) / 2; y0 = 210
for i, f in enumerate(fs):
    x = x0 + (i % 5) * (tw + gx); y = y0 + (i // 5) * (th_ + gy)
    tile = Image.new("RGBA", (tw, th_), (247, 240, 228, 255)); td = ImageDraw.Draw(tile)
    td.rectangle([6, 6, tw - 7, th_ - 7], outline=GOLD, width=2)
    td.text((20, 14), f"{i + 1}", font=font("i", 34), fill=BURG)
    it = asset(f, 190, 190); tile.alpha_composite(it, (int(tw / 2 - it.width / 2 + 14), int(th_ / 2 - it.height / 2 + 4)))
    place(img, tile, x + tw / 2, y + th_ / 2, sdx=6, sdy=10, blur=12, opacity=0.55)
save(img, "10_advent_treasures")

# 11 RIBBON ATELIER — bows hanging from a brass rail
img = paper(CREAM, grain=12, seed=7)
d = ImageDraw.Draw(img)
text(img, (W / 2, 95), "The Ribbon Atelier", font("i", 88), BURG)
text(img, (W / 2, 165), "12 BOWS & RIBBONS  ·  VELVET  ·  SATIN  ·  TARTAN  ·  GINGHAM  ·  LACE", font("r", 23), GOLD, spacing=4)
for ry in (250, 730):
    d.line([(70, ry), (W - 70, ry)], fill=(150, 116, 64), width=10); d.line([(70, ry - 3), (W - 70, ry - 3)], fill=(214, 182, 120), width=3)
    for ex in (70, W - 70): d.ellipse([ex - 16, ry - 16, ex + 16, ry + 16], fill=(150, 116, 64))
fs = sorted(glob.glob("final/bows/*.png")); cw = (W - 160) / 6
import random; rnd = random.Random(4)
for i, f in enumerate(fs):
    cx = 80 + (i % 6) * cw + cw / 2; ry = 250 if i < 6 else 730
    drop = rnd.randint(50, 110); d = ImageDraw.Draw(img); d.line([(cx, ry + 4), (cx, ry + drop)], fill=(170, 140, 100), width=2)
    b = asset(f, int(cw * 0.88), 360, rot=rnd.uniform(-5, 5))
    place(img, b, cx, ry + drop + b.height / 2 - 10, sdx=6, sdy=12, blur=12, opacity=0.25)
save(img, "11_ribbon_atelier")

# 12 PHRASES — lettering cards on linen
img = bg("linen_a", dark=1.02)
fs = sorted(glob.glob("final/phrases/*.png")); rots = [-5, 3, -2, 4, -3, 6]
pos = [(470, 380), (910, 330), (1350, 380), (470, 840), (910, 880), (1350, 840)]
for f, r, (x, y) in zip(fs, rots, pos):
    c = Image.new("RGBA", (400, 290), (250, 246, 238, 255)); ph = asset(f, 350, 240)
    c.alpha_composite(ph, (int(200 - ph.width / 2), int(145 - ph.height / 2)))
    place(img, c.rotate(r, expand=True, resample=Image.BICUBIC), x, y, sdx=10, sdy=16, blur=16, opacity=0.35)
place(img, a("bows/b10_bow_bell", 210, rot=-15), 1660, 620, opacity=0.35)
place(img, a("props/p04_ornament_gold", 140, rot=10), 150, 620, opacity=0.35)
pill = Image.new("RGBA", (760, 74), (250, 246, 238, 235)); place(img, pill, W / 2, 1140, sdx=4, sdy=6, blur=10, opacity=0.25)
text(img, (W / 2, 1140), "6 script phrases  ·  transparent PNG", font("i", 36), BURG)
save(img, "12_phrases")

# 13 WHAT'S INSIDE
img = vignette(solid(DEEP), 0.35)
text(img, (W / 2, 95), "What's Inside", font("i", 92), CREAM)
rule(img, W / 2, 160, 420)
rows = [("16", "Woodland Characters", "characters/c05_bunny"), ("12", "Bows & Ribbons", "bows/b07_double_loop"), ("20", "Festive Treasures", "props/p10_lantern"),
        ("12", "Winter Botanicals", "botanicals/f12_winter_bouquet"), ("4", "Wreaths & Frames", "frames/w01_wreath_fawn"), ("6", "Script Phrases", "phrases/t03_joy"),
        ("4", "Painted Scenes", None), ("10", "Seamless Patterns", None), ("6", "Card & Tag Templates", None)]
for i, (n, label, icon) in enumerate(rows):
    col, row = i % 3, i // 3; cx = 330 + col * 580; cy = 330 + row * 250
    tile = Image.new("RGBA", (520, 210), (74, 22, 32, 255)); ImageDraw.Draw(tile).rectangle([4, 4, 515, 205], outline=GOLD, width=2)
    place(img, tile, cx, cy, shadow=False)
    if icon: place(img, a(icon, 170, 170), cx - 160, cy, sdx=0, sdy=6, blur=8, opacity=0.5)
    elif "Scenes" in label: place(img, asset("final/scenes/s02_fireside.jpg", 120, 165, rot=-6), cx - 160, cy, blur=8, opacity=0.5)
    elif "Patterns" in label: place(img, asset("final/patterns/pt05_bow_woodland_mix_cream.jpg", 150, 150, rot=6), cx - 160, cy, blur=8, opacity=0.5)
    else: place(img, asset("final/templates/tag02_bear.png", 100, 165, rot=-8), cx - 160, cy, blur=8, opacity=0.5)
    text(img, (cx + 70, cy - 30), n, font("i", 76), GOLD); text(img, (cx + 70, cy + 45), label, font("i", 32), CREAM)
text(img, (W / 2, 1120), "300 DPI  ·  TRANSPARENT PNG  ·  JPG  ·  COMMERCIAL USE PER CREATIVE MARKET LICENSE", font("r", 24), GOLD, spacing=4)
save(img, "13_whats_inside")
print("ok")
