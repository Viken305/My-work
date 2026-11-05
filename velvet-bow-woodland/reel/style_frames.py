"""Style frames for the Velvet Bow Woodland reel (1080x1920, 9:16)."""
import sys, math, random
sys.path.insert(0, "src")
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
from pv_lib import font, asset, a, shadow_of, sparkle, CREAM, PAPER, BURG, DEEP, GOLD, SAGE, INK
W, H = 1080, 1920
OUT = "reel/style_frames"

def bg(name, dark=1.0, blur=0):
    im = ImageOps.fit(Image.open(f"raw/bg/{name}_hi.png").convert("RGB"), (W, H), Image.LANCZOS)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    if dark != 1.0: im = ImageEnhance.Brightness(im).enhance(dark)
    return im.convert("RGBA")
def paper(col=PAPER, grain=10):
    b = Image.new("RGBA", (W, H), col + (255,))
    n = Image.effect_noise((W // 2, H // 2), grain).resize((W, H)).convert("L")
    b.alpha_composite(Image.merge("RGBA", [n, n, n, Image.new("L", (W, H), 18)])); return b
def vignette(img, s=0.55):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse([-W*.3, -H*.15, W*1.3, H*1.15], fill=255)
    m = ImageOps.invert(m.filter(ImageFilter.GaussianBlur(200))).point(lambda v: int(v*s))
    d = Image.new("RGBA", (W, H), (20, 6, 10, 0)); d.putalpha(m); img.alpha_composite(d); return img
def place(base, im, cx, cy, shadow=True, sdx=10, sdy=18, blur=20, op=0.42):
    x, y = int(cx - im.width/2), int(cy - im.height/2)
    if shadow:
        sh, p = shadow_of(im, blur, op); base.paste(sh, (x-p+sdx, y-p+sdy), sh)
    base.paste(im, (x, y), im)
def txt(base, xy, s, f, fill, anchor="mm", shadow=None):
    d = ImageDraw.Draw(base)
    if shadow:
        l = Image.new("RGBA", base.size, (0,0,0,0)); ImageDraw.Draw(l).text((xy[0]+3, xy[1]+5), s, font=f, fill=shadow, anchor=anchor)
        base.alpha_composite(l.filter(ImageFilter.GaussianBlur(6)))
    d.text(xy, s, font=f, fill=fill, anchor=anchor)
def rule(base, cx, y, w, col=GOLD):
    d = ImageDraw.Draw(base); d.line([(cx-w/2, y), (cx-14, y)], fill=col, width=3); d.line([(cx+14, y), (cx+w/2, y)], fill=col, width=3)
    d.polygon([(cx, y-8), (cx+8, y), (cx, y+8), (cx-8, y)], fill=col)
def pill(base, cx, cy, s, f, bgc, fg, padx=44, h=None):
    d = ImageDraw.Draw(base); w = d.textlength(s, font=f) + 2*padx; h = h or f.size + 40
    sh = Image.new("RGBA", base.size, (0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([cx-w/2+4, cy-h/2+10, cx+w/2+4, cy+h/2+10], h/2, fill=(20,6,10,110))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle([cx-w/2, cy-h/2, cx+w/2, cy+h/2], h/2, fill=bgc); d.text((cx, cy), s, font=f, fill=fg, anchor="mm")
def motion_ghost(base, im, cx, cy, dx, dy, n=4):
    for k in range(n, 0, -1):
        g = im.copy(); al = g.getchannel("A").point(lambda v: int(v * 0.12 * (n-k+1)/n)); g.putalpha(al)
        base.paste(g, (int(cx - im.width/2 - dx*k), int(cy - im.height/2 - dy*k)), g)
def safe_guides(img):
    """Overlay showing Reels UI zones (for the guide sheet only)."""
    g = img.copy(); o = Image.new("RGBA", img.size, (0,0,0,0)); d = ImageDraw.Draw(o)
    d.rectangle([0, 0, W, 220], fill=(0,120,255,60)); d.rectangle([0, H-380, W, H], fill=(0,120,255,60)); d.rectangle([W-140, 900, W, H-380], fill=(0,120,255,60))
    g.alpha_composite(o); return g
def save(img, name): img.convert("RGB").save(f"{OUT}/{name}.jpg", quality=92); return img

frames = []
# SF1 — Hook: velvet, giant bow, fawn peeking
f = vignette(bg("velvet_a", 0.8), 0.6)
sparkle(f, 26, 11, area=(40, 660, W-40, 1300))
txt(f, (W/2, 330), "your Christmas designs", font("i", 74), CREAM, shadow=(10,0,0,160))
txt(f, (W/2, 430), "are missing", font("i", 74), CREAM, shadow=(10,0,0,160))
txt(f, (W/2, 560), "someone…", font("bi", 120), (236, 206, 150), shadow=(10,0,0,180))
place(f, a("bows/b02_velvet_longtails", 620, rot=-6), W/2, 960, blur=26, op=.5)
fawn = a("characters/c01_fawn", 760); place(f, fawn, W/2+40, H - 120 - fawn.height/2 + 120, blur=30)
frames.append(("01_hook", save(f, "01_hook")))

# SF2 — Cast pop-in grid
f = paper(CREAM)
txt(f, (W/2, 290), "Meet the cast", font("bi", 104), BURG); rule(f, W/2, 370, 420)
txt(f, (W/2, 425), "16 woodland friends, every one in a bow", font("i", 40), INK)
chars = ["c03_fox","c05_bunny","c07_bear","c10_owl","c11_hedgehog","c12_squirrel","c09_mouse","c13_polarbear","c14_lamb","c15_raccoon","c16_badger","c02_fawn_stand","c06_bunny_sit","c08_bear_stand","c04_fox_walk","c01_fawn"]
d = ImageDraw.Draw(f); cw, ch, x0, y0 = 240, 270, 60, 500
for i, c in enumerate(chars):
    r, col = divmod(i, 4); cx, cy = x0 + col*cw + cw/2 + 2, y0 + r*ch + ch/2
    pop = ([1]*13 + [1.12, .7, 0])[i]   # mid-animation: last ones popping
    if pop == 0:
        d.ellipse([cx-8, cy-8, cx+8, cy+8], fill=GOLD + (150,)); continue
    d.ellipse([cx-112*pop, cy-112*pop, cx+112*pop, cy+112*pop], fill=(236, 223, 204))
    im = a(f"characters/{c}", int(235*pop), int(245*pop)); place(f, im, cx, cy, sdx=4, sdy=8, blur=10, op=.3)
frames.append(("02_cast_pop", save(f, "02_cast_pop")))

# SF3 — Detail push-in on fox + bow callout
f = vignette(bg("wall_b", 0.9, 6), 0.5)
fox = a("characters/c03_fox", 1000); fx, fy = W/2 - 60, 930; place(f, fox, fx, fy, blur=34)
full = Image.open("final/characters/c03_fox.png").convert("RGBA"); k = full.width / fox.width
bx, by = 0.45 * fox.width, 0.36 * fox.height      # bow position in the placed fox
R, cx, cy = 225, 805, 650
z = full.crop((int(bx*k - R*k/2.2), int(by*k - R*k/2.2), int(bx*k + R*k/2.2), int(by*k + R*k/2.2))).resize((2*R, 2*R), Image.LANCZOS)
disc = Image.new("RGBA", (2*R, 2*R), (236, 223, 204, 255)); disc.alpha_composite(z)
m = Image.new("L", (2*R, 2*R), 0); ImageDraw.Draw(m).ellipse([0, 0, 2*R-1, 2*R-1], fill=255); disc.putalpha(m)
dd = ImageDraw.Draw(f); ox, oy = fx - fox.width/2 + bx, fy - fox.height/2 + by
dd.line([(ox, oy), (cx, cy)], fill=GOLD, width=3); dd.ellipse([ox-10, oy-10, ox+10, oy+10], outline=GOLD, width=3)
place(f, disc, cx, cy, blur=24, op=.5); dd.ellipse([cx-R-8, cy-R-8, cx+R+8, cy+R+8], outline=GOLD, width=12)
txt(f, (W/2, 260), "the little details", font("bi", 92), CREAM, shadow=(10,0,0,170))
txt(f, (W/2, 345), "velvet texture · fur · ribbon tails", font("i", 42), (236, 206, 150), shadow=(10,0,0,150))
pill(f, W/2, 1490, "4000 px · 300 DPI · transparent PNG", font("b", 40), CREAM + (255,), BURG)
frames.append(("03_details", save(f, "03_details")))

# SF4 — Build a card: elements fly onto a card
f = bg("linen_a", 1.0)
card = Image.new("RGBA", (760, 1064), (250, 246, 238, 255))
cd = ImageDraw.Draw(card); cd.rectangle([22, 22, 737, 1041], outline=GOLD, width=3)
wr = a("frames/w02_wreath_bunny", 640); card.alpha_composite(wr, ((760-wr.width)//2, 120))
place(f, card.rotate(-3, expand=True, resample=Image.BICUBIC), W/2, 1000, blur=28, op=.38)
ph = a("phrases/t01_merry_bright", 600, rot=4); motion_ghost(f, ph, W/2, 1330, 0, -46); place(f, ph, W/2, 1330, sdy=30, blur=26)
place(f, a("botanicals/f01_holly", 300, rot=-25), 170, 620, sdy=24); place(f, a("props/p03_ornament_burgundy", 230, rot=10), 930, 640, sdy=24)
txt(f, (W/2, 280), "mix & match", font("bi", 110), BURG, shadow=(255,255,255,120))
txt(f, (W/2, 375), "a finished card in minutes", font("i", 46), INK)
frames.append(("04_build_card", save(f, "04_build_card")))

# SF5 — Patterns: tilted strips sliding past
f = Image.new("RGBA", (W, H), DEEP + (255,))
names = ["pt02_velvet_bows_cream","pt01_woodland_friends_burgundy","pt03_winter_botanicals_cream","pt05_bow_woodland_mix_burgundy","pt04_festive_treasures_cream"]
big = Image.new("RGBA", (1700, 2700), (0,0,0,0)); sw = 340
for i, n in enumerate(names):
    t = Image.open(f"final/patterns/{n}.jpg").convert("RGBA").resize((900, 900), Image.LANCZOS)
    strip = Image.new("RGBA", (sw, 2700))
    off = [0, 300, 120, 450, 220][i]
    for yy in range(-off, 2700, 900): strip.paste(t.crop((200, 0, 200+sw, 900)), (0, yy))
    big.paste(strip, (i*sw, 0))
big = big.rotate(14, expand=True, resample=Image.BICUBIC)
f.alpha_composite(big, ((W-big.width)//2, (H-big.height)//2)); vignette(f, .5)
pill(f, W/2, 960, "10 seamless patterns", font("bi", 76), BURG + (255,), CREAM, padx=60, h=150)
pill(f, W/2, 1080, "5 designs × burgundy & cream", font("i", 42), CREAM + (255,), BURG, padx=40, h=80)
frames.append(("05_patterns", save(f, "05_patterns")))

# SF6 — The count: big 90 with category orbit
f = vignette(bg("velvet_a", .75), .6); sparkle(f, 40, 5, area=(40, 220, W-40, 1500))
txt(f, (W/2, 640), "90", font("b", 420), (236, 206, 150), shadow=(10,0,0,200))
txt(f, (W/2, 880), "Christmas illustrations", font("i", 62), CREAM)
chips = ["16 characters","12 bows","20 treasures","12 botanicals","4 wreaths","6 phrases","4 scenes","10 patterns","6 cards & tags"]
fc = font("b", 40); ys = [1010, 1115, 1220]
for r in range(3):
    row = chips[r*3:(r+1)*3]; d = ImageDraw.Draw(f); ws = [d.textlength(s, font=fc)+48 for s in row]; x = W/2 - (sum(ws)+18*2)/2
    for s, w in zip(row, ws): pill(f, x + w/2, ys[r], s, fc, CREAM + (255,), BURG, padx=24, h=80); x += w + 18
for nm, x, y, w, rot in [("props/p01_gift", 150, 300, 200, -10), ("props/p04_ornament_gold", 930, 290, 170, 12), ("botanicals/f02_mistletoe", 150, 1420, 230, 15), ("props/p11_gingerbread", 930, 1400, 200, -8)]:
    place(f, a(nm, w, rot=rot), x, y, blur=16)
frames.append(("06_count", save(f, "06_count")))

# SF7 — End card / CTA
f = vignette(bg("velvet_a", .85), .55)
gs = a("frames/w04_garland_swag", 1240); place(f, gs, W/2, 250 + gs.height/2 - 60, blur=20)
txt(f, (W/2, 640), "Velvet Bow", font("bi", 140), CREAM, shadow=(10,0,0,180))
txt(f, (W/2, 780), "Woodland", font("bi", 140), (236, 206, 150), shadow=(10,0,0,180)); rule(f, W/2, 880, 460)
txt(f, (W/2, 945), "Christmas clipart collection", font("i", 48), CREAM)
for nm, x, w in [("c11_hedgehog", 170, 300), ("c05_bunny", 380, 360), ("c01_fawn", 620, 430), ("c03_fox", 880, 380)]:
    im = a(f"characters/{nm}", w); place(f, im, x, 1400 - im.height/2, blur=22)
pill(f, W/2, 1510, "Now on Creative Market", font("b", 50), CREAM + (255,), BURG, padx=56, h=110)
txt(f, (W/2, 1610), "link in bio", font("i", 42), CREAM)
frames.append(("07_end_card", save(f, "07_end_card")))

# Overview board
th = 360; tw = int(th * W / H); pad = 30
sheet = Image.new("RGB", (pad + len(frames)*(tw+pad), th*2 + pad*3 + 80), (28, 10, 14)); sd = ImageDraw.Draw(sheet)
for i, (n, im) in enumerate(frames):
    x = pad + i*(tw+pad)
    sheet.paste(im.convert("RGB").resize((tw, th), Image.LANCZOS), (x, pad))
    sheet.paste(safe_guides(im).convert("RGB").resize((tw, th), Image.LANCZOS), (x, th + pad*2 + 40))
    sd.text((x + tw/2, th + pad + 22), n, font=font("r", 20), fill=CREAM, anchor="mm")
sheet.save(f"{OUT}/00_style_frames_board.jpg", quality=92)
