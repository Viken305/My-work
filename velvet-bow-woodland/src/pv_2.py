import sys, math; sys.path.insert(0, "src")
from pv_lib import *

# 05 WRAPPED IN PATTERN — gift boxes wrapped in the seamless papers on walnut
img = bg("wood_b", dark=0.85)
def box(pattern, w, h, bow, pscale=900):
    """Front-facing gift box with a lid, wrapped in a pattern, ribbon and a real bow on top."""
    pat = Image.open(f"final/patterns/{pattern}.jpg").convert("RGBA").resize((pscale, pscale))
    lid_h = int(h * 0.24); over = int(w * 0.05)
    b = a(bow, int(w * 0.78)); top = b.height // 2
    out = Image.new("RGBA", (w + 2 * over, h + top + 10), (0, 0, 0, 0))
    body = pat.crop((0, 0, w, h - lid_h + 10))
    shade = Image.new("RGBA", body.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(shade)
    for i in range(40): sd.line([(0, i), (w, i)], fill=(20, 5, 8, int(120 * (1 - i / 40))))
    body.alpha_composite(shade); out.alpha_composite(body, (over, top + lid_h - 10))
    lid = ImageEnhance.Brightness(pat.crop((60, 60, 60 + w + 2 * over, 60 + lid_h))).enhance(1.08)
    out.alpha_composite(lid, (0, top))
    dr = ImageDraw.Draw(out); bw = max(16, w // 12); rc = (118, 26, 40, 255)
    dr.rectangle([over + w / 2 - bw / 2, top, over + w / 2 + bw / 2, top + h], fill=rc)
    dr.line([(over + w / 2 - bw / 2 + 3, top), (over + w / 2 - bw / 2 + 3, top + h)], fill=(190, 150, 95, 255), width=2)
    dr.line([(over + w / 2 + bw / 2 - 3, top), (over + w / 2 + bw / 2 - 3, top + h)], fill=(190, 150, 95, 255), width=2)
    dr.line([(0, top + lid_h), (w + 2 * over, top + lid_h)], fill=(30, 10, 12, 140), width=3)
    out.alpha_composite(b, (int(out.width / 2 - b.width / 2), 0)); return out
place(img, box("pt02_velvet_bows_cream", 400, 360, "bows/b07_double_loop"), 470, 1120, anchor="b", sdx=24, sdy=10, blur=24, opacity=0.6)
place(img, box("pt01_woodland_friends_burgundy", 520, 470, "bows/b09_gold_satin"), 1000, 1120, anchor="b", sdx=24, sdy=10, blur=26, opacity=0.6)
place(img, box("pt03_winter_botanicals_cream", 330, 290, "bows/b04_tartan"), 1470, 1120, anchor="b", sdx=24, sdy=10, blur=22, opacity=0.6)
place(img, a("botanicals/f03_pine", 300, rot=-60), 150, 1080, opacity=0.5)
place(img, a("props/p15_sleighbells", 230, rot=15), 1650, 260, opacity=0.5)
sparkle(img, 30, seed=9, area=(0, 0, W, 300))
text(img, (W / 2, 120), "Wrapped in Woodland", font("i", 96), CREAM)
text(img, (W / 2, 205), "10 SEAMLESS PATTERNS FOR GIFT WRAP, FABRIC & PAPER GOODS", font("r", 28), GOLD, spacing=5)
save(img, "05_gift_wrap")

# 06 FABRIC SWATCH FAN — every pattern as stacked swatches
img = paper((236, 226, 210), grain=12)
import glob
pats = sorted(glob.glob("final/patterns/*.jpg"))
for i, p in enumerate(pats):
    sw = Image.open(p).convert("RGBA").resize((520, 520), Image.LANCZOS)
    sw = card(sw, 0); ang = -40 + i * 8.5
    r = sw.rotate(ang, expand=True, resample=Image.BICUBIC)
    cx = 1180 + 520 * math.sin(math.radians(ang)) * 0.55; cy = 980 - 520 * math.cos(math.radians(ang)) * 0.55
    place(img, r, cx, cy, sdx=8, sdy=12, blur=14, opacity=0.35)
text(img, (360, 380), "Ten", font("i", 140), BURG)
text(img, (360, 500), "Seamless", font("i", 110), BURG)
text(img, (360, 610), "Patterns", font("i", 110), BURG)
rule(img, 360, 690, 360)
for k, line in enumerate(["5 designs  ×  2 colourways", "burgundy & cream", "3600 × 3600 px  ·  300 DPI", "tiles in every direction"]):
    text(img, (360, 750 + k * 50), line, font("i", 34), INK)
place(img, a("botanicals/f01_holly", 200, rot=-25), 360, 1080, sdx=6, sdy=8, blur=10, opacity=0.3)
save(img, "06_pattern_swatches")

# 07 MIX & MATCH — build your own scene
img = paper(CREAM, grain=12)
text(img, (W / 2, 110), "Mix, Match & Make it Yours", font("i", 86), BURG)
text(img, (W / 2, 185), "EVERY ELEMENT IS A SEPARATE TRANSPARENT PNG", font("r", 26), GOLD, spacing=5)
parts = [("characters/c15_raccoon", 300), ("bows/b04_tartan", 260), ("props/p02_gift_stack", 260), ("botanicals/f12_winter_bouquet", 280)]
xs = [160, 470, 780, 1090]
for (n, s), x in zip(parts, xs):
    place(img, a(n, s, 330), x, 560, sdx=0, sdy=10, blur=12, opacity=0.3)
for x in [315, 625, 935]: text(img, (x, 560), "+", font("r", 90), GOLD)
text(img, (1255, 560), "=", font("r", 100), GOLD)
# composed result inside an oval frame
fr = a("frames/w03_oval_frame", 460, 600)
comp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
place(img, fr, 1530, 600, sdx=6, sdy=10, blur=14, opacity=0.3)
place(img, a("props/p02_gift_stack", 150), 1600, 760, sdx=4, sdy=6, blur=8, opacity=0.3)
place(img, a("characters/c15_raccoon", 220), 1510, 680, sdx=4, sdy=6, blur=8, opacity=0.3)
place(img, a("botanicals/f01_holly", 130, rot=20), 1430, 790, sdx=4, sdy=6, blur=8, opacity=0.3)
labels = ["a character", "a bow", "a treasure", "a botanical"]
for l, x in zip(labels, xs): text(img, (x, 790), l, font("i", 34), INK)
text(img, (1530, 960), "your own design", font("i", 34), BURG)
rule(img, W / 2, 1060, 900)
text(img, (W / 2, 1120), "70 pieces  ·  endless combinations  ·  layer them in Photoshop, Procreate, Canva or Affinity", font("i", 32), INK)
save(img, "07_mix_and_match")
print("ok")
