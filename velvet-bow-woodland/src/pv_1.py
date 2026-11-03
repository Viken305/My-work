import sys; sys.path.insert(0, "src")
from pv_lib import *

# 01 HERO — velvet stage, garland, title, the cast gathered
img = vignette(bg("velvet_a", dark=0.62), 0.6)
place(img, a("frames/w04_garland_swag", 1700, 440), W / 2, 150, opacity=0.5)
text(img, (W / 2, 375), "THE STORYBOOK CHRISTMAS COLLECTION", font("r", 30), GOLD, spacing=7)
text(img, (W / 2, 480), "Velvet Bow Woodland", font("i", 150), CREAM)
rule(img, W / 2, 582, 520)
text(img, (W / 2, 628), "90 vintage storybook illustrations  ·  patterns  ·  cards", font("i", 38), (226, 206, 176))
cast = [("characters/c09_mouse", 250), ("characters/c06_bunny_sit", 330), ("characters/c01_fawn", 430), ("characters/c03_fox", 420),
        ("characters/c07_bear", 380), ("characters/c11_hedgehog", 330), ("characters/c13_polarbear", 340)]
xs = [140, 380, 640, 910, 1180, 1430, 1675]
for (n, s), x in zip(cast, xs):
    im = a(n, s, s); place(img, im, x, 1160, anchor="b", sdx=0, sdy=8, blur=14, opacity=0.6)
sparkle(img, 22, seed=3, area=(30, 300, 330, 700)); sparkle(img, 22, seed=4, area=(W - 330, 300, W - 30, 700))
save(img, "01_hero")

# 02 MEET THE CAST — storybook programme
img = paper(CREAM, grain=14)
d = ImageDraw.Draw(img); d.rectangle([28, 28, W - 28, H - 28], outline=GOLD, width=3); d.rectangle([40, 40, W - 40, H - 40], outline=GOLD, width=1)
text(img, (W / 2, 110), "Meet the Cast", font("i", 92), BURG)
text(img, (W / 2, 180), "16 WOODLAND CHARACTERS · EACH DRESSED IN VELVET, SATIN OR TARTAN", font("r", 24), GOLD, spacing=4)
names = ["Fawn", "Fawn, standing", "Fox", "Fox, on the way", "Bunny", "Bunny, dreaming", "Bear Cub", "Bear with Lantern",
         "Candle Mouse", "Barn Owl", "Hedgehog", "Squirrel", "Polar Bear", "Lamb", "Raccoon", "Badger"]
files = ["c01_fawn", "c02_fawn_stand", "c03_fox", "c04_fox_walk", "c05_bunny", "c06_bunny_sit", "c07_bear", "c08_bear_stand",
         "c09_mouse", "c10_owl", "c11_hedgehog", "c12_squirrel", "c13_polarbear", "c14_lamb", "c15_raccoon", "c16_badger"]
cw = (W - 120) / 8
for i, (f, nm) in enumerate(zip(files, names)):
    col, row = i % 8, i // 8
    cx = 60 + cw * col + cw / 2; base_y = 600 + row * 470
    im = a(f"characters/{f}", int(cw * 0.95), 330); place(img, im, cx, base_y, anchor="b", sdx=0, sdy=6, blur=10, opacity=0.28)
    text(img, (cx, base_y + 34), nm, font("i", 27), INK)
    text(img, (cx, base_y + 70), f"No. {i + 1:02d}", font("r", 18), GOLD, spacing=3)
save(img, "02_meet_the_cast")

# 03 FLAT LAY — cards & tags on linen
img = bg("linen_a", dark=1.0)
c1 = card(Image.open("final/templates/card01_merry_bright_5x7.jpg").resize((420, 588)), 0).rotate(-7, expand=True, resample=Image.BICUBIC)
c2 = card(Image.open("final/templates/card02_seasons_greetings_5x7.jpg").resize((440, 616)), 0).rotate(4, expand=True, resample=Image.BICUBIC)
c3 = card(Image.open("final/templates/card03_warm_wishes_5x7.jpg").resize((410, 574)), 0).rotate(10, expand=True, resample=Image.BICUBIC)
place(img, c1, 560, 600, sdx=14, sdy=22, blur=22, opacity=0.38)
place(img, c3, 1260, 610, sdx=14, sdy=22, blur=22, opacity=0.38)
place(img, c2, 910, 560, sdx=16, sdy=26, blur=24, opacity=0.42)
t1 = asset("final/templates/tag01_bunny.png", 190, 300, rot=-18); place(img, t1, 260, 900, blur=12, opacity=0.35)
t2 = asset("final/templates/tag03_hedgehog.png", 180, 290, rot=14); place(img, t2, 1560, 300, blur=12, opacity=0.35)
place(img, a("bows/b02_velvet_longtails", 300, rot=25), 1560, 900, opacity=0.35)
place(img, a("props/p14_pinecones", 170, rot=-20), 330, 330, opacity=0.4)
place(img, a("props/p03_ornament_burgundy", 150), 1160, 1080, opacity=0.4)
place(img, a("botanicals/f01_holly", 220, rot=-35), 740, 1090, opacity=0.35)
save(img, "03_flat_lay_cards")

# 04 GALLERY WALL — framed scenes above the sideboard
img = bg("wall_b", dark=1.05)
def framed(path, w, frame=(110, 78, 46), mat=(248, 244, 236)):
    sc = Image.open(path).convert("RGBA"); sc = sc.resize((w, int(w * sc.height / sc.width)), Image.LANCZOS)
    m = card(sc, int(w * 0.11), mat); f = Image.new("RGBA", (m.width + 36, m.height + 36), frame + (255,))
    ImageDraw.Draw(f).rectangle([6, 6, f.width - 7, f.height - 7], outline=(150, 112, 70), width=4); f.alpha_composite(m, (18, 18)); return f
place(img, framed("final/scenes/s04_tree_gathering.jpg", 330), 910, 360, sdx=10, sdy=18, blur=20, opacity=0.45)
place(img, framed("final/scenes/s01_snowy_forest.jpg", 230, frame=(176, 140, 86)), 500, 330, sdx=10, sdy=18, blur=18, opacity=0.42)
place(img, framed("final/scenes/s03_village.jpg", 230, frame=(176, 140, 86)), 1320, 330, sdx=10, sdy=18, blur=18, opacity=0.42)
text(img, (W / 2, 1150), "4 painted scenes  ·  ready for wall art, cards & covers", font("i", 34), (250, 240, 225))
save(img, "04_gallery_wall")
print("ok")
