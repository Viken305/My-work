"""Velvet Bow Woodland reel — deterministic renderer (1080x1920, 30 fps).

Every frame depends only on its time t. Visual and sound cues come from the same
CUES table, written to reel/plan/beats.json.

  python3 reel/render.py preview          # half-res contact sheet of key moments
  python3 reel/render.py video [--half]   # full render to reel/out/
"""
import sys, os, math, json, random, subprocess
sys.path.insert(0, "src")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
from pv_lib import font, a, CREAM, PAPER, BURG, DEEP, GOLD, INK

W, H, FPS = 1080, 1920, 30
BEAT = 1 / 3.0                     # music: ~180 bpm, 0.3333 s per beat
MUSIC = "reel/dl/Jingle_Bells.mp3"
MUSIC_IN = 117.69                  # offset into the track (on a beat); its final hit lands at ~18.33 s
GOLD2 = (236, 206, 150)

# scene boundaries, in beats
SCENES = [("hook", 0, 8), ("cast", 8, 18), ("details", 18, 26), ("card", 26, 34), ("patterns", 34, 40), ("count", 40, 48), ("end", 48, 58)]
DUR = 58 * BEAT + 0.0              # 19.33 s
T0 = {n: s * BEAT for n, s, e in SCENES}; T1 = {n: e * BEAT for n, s, e in SCENES}

# ---------------------------------------------------------------- easing
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def prog(t, t0, d): return clamp((t - t0) / d)
def out_cubic(x): return 1 - (1 - x) ** 3
def out_back(x, s=1.9): x -= 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def out_elastic(x):
    if x <= 0: return 0.
    if x >= 1: return 1.
    return 2 ** (-10 * x) * math.sin((x * 10 - .75) * 2 * math.pi / 3) + 1
def in_out(x): return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x

# ---------------------------------------------------------------- sprites
def with_shadow(im, blur=20, op=.42, sdx=10, sdy=18):
    P = blur * 3 + max(abs(sdx), abs(sdy))
    c = Image.new("RGBA", (im.width + 2 * P, im.height + 2 * P), (30, 12, 10, 0))
    if op > 0:
        m = Image.new("L", c.size, 0); m.paste(im.getchannel("A"), (P + sdx, P + sdy))
        m = m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * op))
        c.putalpha(m)
    c.alpha_composite(im, (P, P)); c.info["rh"] = im.height; return c
def tsprite(s, f, fill, shadow=(10, 0, 0, 160), blur=6):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); l, t, r, b = d.textbbox((0, 0), s, font=f)
    P = 30; im = Image.new("RGBA", (r - l + 2 * P, b - t + 2 * P), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((P - l + 3, P - t + 5), s, font=f, fill=shadow)
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).text((P - l, P - t), s, font=f, fill=fill); return im
def pillsprite(s, f, bgc, fg, padx=44, h=None):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); w = int(d.textlength(s, font=f) + 2 * padx); h = h or f.size + 40
    P = 30; im = Image.new("RGBA", (w + 2 * P, h + 2 * P), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([P + 4, P + 10, P + w + 4, P + h + 10], h / 2, fill=(20, 6, 10, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    dd = ImageDraw.Draw(im); dd.rounded_rectangle([P, P, P + w, P + h], h / 2, fill=bgc); dd.text((P + w / 2, P + h / 2), s, font=f, fill=fg, anchor="mm")
    return im
def put(base, spr, cx, cy, scale=1., rot=0., alpha=1.):
    if alpha <= 0.003 or scale <= 0.01: return
    im = spr
    if abs(scale - 1) > 1e-3: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.05: im = im.rotate(rot, resample=Image.BILINEAR, expand=True)
    if alpha < 0.997:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(round(cx - im.width / 2)), int(round(cy - im.height / 2))
    # clip to canvas
    l, t = max(0, -x), max(0, -y); r, b = min(im.width, base.width - x), min(im.height, base.height - y)
    if r <= l or b <= t: return
    if (l, t, r, b) != (0, 0, im.width, im.height): im = im.crop((l, t, r, b))
    base.alpha_composite(im, (x + l, y + t))

# ---------------------------------------------------------------- backgrounds
def bgimg(name, dark=1., blur=0, over=1.12):
    im = ImageOps.fit(Image.open(f"raw/bg/{name}_hi.png").convert("RGB"), (int(W * over), int(H * over)), Image.LANCZOS)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    if dark != 1: im = ImageEnhance.Brightness(im).enhance(dark)
    return im
def vig_layer(s=.55):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse([-W * .3, -H * .15, W * 1.3, H * 1.15], fill=255)
    m = ImageOps.invert(m.filter(ImageFilter.GaussianBlur(200))).point(lambda v: int(v * s))
    d = Image.new("RGBA", (W, H), (20, 6, 10, 0)); d.putalpha(m); return d
def drift(img, t, z0=1.0, z1=1.06, dur=3.0, dx=0, dy=0):
    """Slow push-in on an oversized background."""
    z = lerp(z0, z1, clamp(t / dur)); ow, oh = img.size
    # crop a window of (W*ow/W/z) scaled back to W
    win_w, win_h = ow / z, oh / z
    cx, cy = ow / 2 + dx * t, oh / 2 + dy * t
    box = (cx - win_w / 2, cy - win_h / 2, cx + win_w / 2, cy + win_h / 2)
    return img.resize((W, H), Image.BILINEAR, box=box).convert("RGBA")
def paper_bg(col=CREAM, grain=10, seed=1):
    random.seed(seed); b = Image.new("RGBA", (W, H), col + (255,))
    n = Image.effect_noise((W // 2, H // 2), grain).resize((W, H)).convert("L")
    b.alpha_composite(Image.merge("RGBA", [n, n, n, Image.new("L", (W, H), 18)])); return b
def sparkles(base, t, n, seed, area, col=(232, 205, 150)):
    rnd = random.Random(seed); d = ImageDraw.Draw(base); x0, y0, x1, y1 = area
    for _ in range(n):
        x, y, r = rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(2.5, 7.5)
        ph, sp = rnd.uniform(0, 6.28), rnd.uniform(1.5, 3.5)
        k = .5 + .5 * math.sin(t * sp + ph); k = k ** 2
        if k < .05: continue
        r *= .6 + .6 * k; al = int(230 * k)
        d.polygon([(x, y - r * 2.2), (x + r * .45, y - r * .45), (x + r * 2.2, y), (x + r * .45, y + r * .45), (x, y + r * 2.2), (x - r * .45, y + r * .45), (x - r * 2.2, y), (x - r * .45, y - r * .45)], fill=col + (al,))
def rule(base, cx, y, w, col=GOLD, k=1.):
    if k <= 0: return
    d = ImageDraw.Draw(base); hw = w / 2 * k
    d.line([(cx - hw, y), (cx - 14, y)], fill=col, width=3); d.line([(cx + 14, y), (cx + hw, y)], fill=col, width=3)
    d.polygon([(cx, y - 8), (cx + 8, y), (cx, y + 8), (cx - 8, y)], fill=col)

# ---------------------------------------------------------------- cue table (shared by picture + sound)
CUES = []
def cue(t, kind, gain=0., note=""): CUES.append({"t": round(t, 4), "sfx": kind, "gain_db": gain, "note": note}); return t

# ---------------------------------------------------------------- assets (built once)
class A: pass
def build():
    A.vel = bgimg("velvet_a", .8); A.vel2 = bgimg("velvet_a", .75); A.wall = bgimg("wall_b", .9, 6); A.linen = bgimg("linen_a", 1.)
    A.vig6 = vig_layer(.6); A.vig5 = vig_layer(.5)
    A.paper = paper_bg(CREAM)
    # S1 hook
    A.h1 = tsprite("your Christmas designs", font("i", 74), CREAM); A.h2 = tsprite("are missing", font("i", 74), CREAM)
    A.h3 = tsprite("someone…", font("bi", 120), GOLD2, (10, 0, 0, 180))
    A.bow = with_shadow(a("bows/b02_velvet_longtails", 620), 26, .5)
    A.fawn = with_shadow(a("characters/c01_fawn", 760), 30)
    # S2 cast
    A.t_cast = tsprite("Meet the cast", font("bi", 104), BURG, None); A.t_cast2 = tsprite("16 woodland friends, every one in a bow", font("i", 40), INK, None)
    A.chars = ["c03_fox", "c05_bunny", "c07_bear", "c10_owl", "c11_hedgehog", "c12_squirrel", "c09_mouse", "c13_polarbear", "c14_lamb", "c15_raccoon", "c16_badger", "c02_fawn_stand", "c06_bunny_sit", "c08_bear_stand", "c04_fox_walk", "c01_fawn"]
    A.cs = [with_shadow(a(f"characters/{c}", 235, 245), 10, .3, 4, 8) for c in A.chars]
    disc = Image.new("RGBA", (232, 232), (0, 0, 0, 0)); ImageDraw.Draw(disc).ellipse([4, 4, 228, 228], fill=(236, 223, 204, 255)); A.disc = disc
    # S3 details
    fox = a("characters/c03_fox", 1000); A.fox_w, A.fox_h = fox.size; A.fox = with_shadow(fox, 34)
    A.fox_full = Image.open("final/characters/c03_fox.png").convert("RGBA")
    A.t_det = tsprite("the little details", font("bi", 92), CREAM, (10, 0, 0, 170)); A.t_det2 = tsprite("velvet texture · fur · ribbon tails", font("i", 42), GOLD2, (10, 0, 0, 150))
    A.p_det = pillsprite("4000 px · 300 DPI · transparent PNG", font("b", 40), CREAM + (255,), BURG)
    # S4 card
    card = Image.new("RGBA", (760, 1064), (250, 246, 238, 255)); ImageDraw.Draw(card).rectangle([22, 22, 737, 1041], outline=GOLD, width=3)
    A.card = with_shadow(card, 28, .38); A.wreath = with_shadow(a("frames/w02_wreath_bunny", 640), 14, .3, 4, 8)
    A.phrase = with_shadow(a("phrases/t01_merry_bright", 600), 26, .42, 10, 30)
    A.holly = with_shadow(a("botanicals/f01_holly", 300), 20, .42, 10, 24); A.orn = with_shadow(a("props/p03_ornament_burgundy", 230), 20, .42, 10, 24)
    A.t_mix = tsprite("mix & match", font("bi", 110), BURG, (255, 255, 255, 120)); A.t_mix2 = tsprite("a finished card in minutes", font("i", 46), INK, None)
    # S5 patterns
    names = ["pt02_velvet_bows_cream", "pt01_woodland_friends_burgundy", "pt03_winter_botanicals_cream", "pt05_bow_woodland_mix_burgundy", "pt04_festive_treasures_cream"]
    A.strips = []
    for n in names:
        t = Image.open(f"final/patterns/{n}.jpg").convert("RGB").resize((900, 900), Image.LANCZOS).crop((200, 0, 540, 900))
        col = Image.new("RGB", (340, 900 * 5)); [col.paste(t, (0, k * 900)) for k in range(5)]; A.strips.append(col)
    A.p_pat = pillsprite("10 seamless patterns", font("bi", 76), BURG + (255,), CREAM, 60, 150)
    A.p_pat2 = pillsprite("5 designs × burgundy & cream", font("i", 42), CREAM + (255,), BURG, 40, 80)
    # S6 count
    A.t_90 = tsprite("Christmas illustrations", font("i", 62), CREAM, (10, 0, 0, 150))
    chips = ["16 characters", "12 bows", "20 treasures", "12 botanicals", "4 wreaths", "6 phrases", "4 scenes", "10 patterns", "6 cards & tags"]
    A.chips = [pillsprite(s, font("b", 40), CREAM + (255,), BURG, 24, 80) for s in chips]
    A.props6 = [(with_shadow(a(n, w, rot=r), 16), x, y) for n, x, y, w, r in [("props/p01_gift", 150, 300, 200, -10), ("props/p04_ornament_gold", 930, 290, 170, 12), ("botanicals/f02_mistletoe", 150, 1420, 230, 15), ("props/p11_gingerbread", 930, 1400, 200, -8)]]
    # S7 end
    A.garland = with_shadow(a("frames/w04_garland_swag", 1240), 20)
    A.e1 = tsprite("Velvet Bow", font("bi", 140), CREAM, (10, 0, 0, 180)); A.e2 = tsprite("Woodland", font("bi", 140), GOLD2, (10, 0, 0, 180))
    A.e3 = tsprite("Christmas clipart collection", font("i", 48), CREAM, (10, 0, 0, 140))
    A.endchars = [(with_shadow(a(f"characters/{n}", w), 22), x) for n, x, w in [("c11_hedgehog", 170, 300), ("c05_bunny", 380, 360), ("c01_fawn", 620, 430), ("c03_fox", 880, 380)]]
    A.cta = pillsprite("Now on Creative Market", font("b", 50), CREAM + (255,), BURG, 56, 110)
    A.bio = tsprite("link in bio", font("i", 42), CREAM, (10, 0, 0, 140))

# ---------------------------------------------------------------- scenes (u = local time in seconds)
B = BEAT
def s_hook(u):
    f = drift(A.vel, u, 1.0, 1.07, 2.8); f.alpha_composite(A.vig6)
    sparkles(f, u, 26, 11, (40, 660, W - 40, 1300))
    # text: word groups land on beats
    for spr, y, t0 in [(A.h1, 330, 0.5 * B), (A.h2, 430, 2 * B), (A.h3, 560, 3.5 * B)]:
        k = prog(u, t0, .35)
        if spr is A.h3: put(f, spr, W / 2, y, lerp(.6, 1, out_back(k)), 0, k)
        else: put(f, spr, W / 2, y + 30 * (1 - out_cubic(k)), 1, 0, k)
    # bow drops and swings
    k = prog(u, 0, .55); y = lerp(-400, 960, out_cubic(k))
    sw = 9 * math.exp(-3.2 * max(0, u - .4)) * math.sin(max(0, u - .4) * 9) if u > .4 else -8 * (1 - k)
    put(f, A.bow, W / 2, y, 1, -6 + sw, 1)
    # fawn rises
    k = out_back(prog(u, 4 * B, .55), 1.2); fh = A.fawn.height
    put(f, A.fawn, W / 2 + 40, lerp(H + fh / 2, H - A.fawn.info["rh"] / 2, k), 1, 0, 1)
    return f
def cast_pos(i):
    r, col = divmod(i, 4); return 60 + col * 240 + 122, 500 + r * 270 + 135
def s_cast(u):
    f = A.paper.copy(); k = out_cubic(prog(u, 0, .4))
    put(f, A.t_cast, W / 2, lerp(200, 290, k), 1, 0, k); rule(f, W / 2, 370, 420, k=out_cubic(prog(u, .2, .4)))
    put(f, A.t_cast2, W / 2, 425, 1, 0, prog(u, .35, .3))
    for i, spr in enumerate(A.cs):
        t0 = CAST_T[i] - T0["cast"]; k = prog(u, t0, .32)
        if k <= 0: continue
        cx, cy = cast_pos(i); s = out_back(k, 2.4)
        put(f, A.disc, cx, cy, s * (1 + .03 * math.sin(u * 3 + i)), 0, 1)
        put(f, spr, cx, cy - 4 * math.sin(u * 4 + i * .7) * k, s, 6 * (1 - k) * (-1) ** i, 1)
    return f
def s_details(u):
    f = drift(A.wall, u, 1.06, 1.0, 2.7); f.alpha_composite(A.vig5)
    fx, fy = W / 2 - 60, 930
    k = out_cubic(prog(u, 0, .45)); put(f, A.fox, lerp(-500, fx, k), fy, 1, lerp(-8, 0, k))
    put(f, A.t_det, W / 2, 260, 1, 0, prog(u, .1, .3)); put(f, A.t_det2, W / 2, 345, 1, 0, prog(u, .3, .3))
    # magnifier
    km = prog(u, 3 * B, .45)
    if km > 0:
        bx, by = 0.45 * A.fox_w, 0.36 * A.fox_h; ox, oy = fx - A.fox_w / 2 + bx, fy - A.fox_h / 2 + by
        R, cx, cy = 225, 805, 650; s = out_back(km, 1.6)
        mx, my = lerp(ox, cx, out_cubic(km)), lerp(oy, cy, out_cubic(km))
        d = ImageDraw.Draw(f); d.ellipse([ox - 10, oy - 10, ox + 10, oy + 10], outline=GOLD, width=3)
        d.line([(ox, oy), (mx, my)], fill=GOLD, width=3)
        kz = 1 / (2.2 + .5 * prog(u, 3 * B, 2.0)); k_ = A.fox_full.width / A.fox_w; hw = R * k_ * kz
        z = A.fox_full.resize((2 * R, 2 * R), Image.BILINEAR, box=(bx * k_ - hw, by * k_ - hw, bx * k_ + hw, by * k_ + hw))
        disc = Image.new("RGBA", (2 * R + 24, 2 * R + 24), (0, 0, 0, 0)); disc.alpha_composite(Image.new("RGBA", (2 * R, 2 * R), (236, 223, 204, 255)), (12, 12)); disc.alpha_composite(z, (12, 12))
        m = Image.new("L", disc.size, 0); ImageDraw.Draw(m).ellipse([12, 12, 12 + 2 * R, 12 + 2 * R], fill=255); disc.putalpha(m)
        ImageDraw.Draw(disc).ellipse([2, 2, 2 * R + 21, 2 * R + 21], outline=GOLD, width=12)
        put(f, with_shadow(disc, 24, .5), mx, my, s, 0, 1)
    k = prog(u, 5 * B, .35); put(f, A.p_det, W / 2, 1490 + 40 * (1 - out_cubic(k)), lerp(.8, 1, out_back(k)), 0, k)
    return f
def s_card(u):
    f = drift(A.linen, u, 1.0, 1.05, 2.7)
    put(f, A.t_mix, W / 2, 280, 1, 0, prog(u, 0, .3)); put(f, A.t_mix2, W / 2, 375, 1, 0, prog(u, .2, .3))
    k = out_cubic(prog(u, 0, .4)); cy = lerp(H + 700, 1000, k); put(f, A.card, W / 2, cy, 1, -3)
    kw = prog(u, 2 * B, .35)
    if kw > 0: put(f, A.wreath, W / 2 + 8, cy - 532 + 120 + 320, lerp(1.35, 1, out_back(kw, 1.4)), -3, kw)
    kh = out_back(prog(u, 3.5 * B, .35), 1.5); put(f, A.holly, lerp(-250, 170, kh), lerp(400, 620, kh), 1, -25 + 40 * (1 - kh))
    ko = out_back(prog(u, 4.5 * B, .35), 1.5); put(f, A.orn, lerp(W + 200, 930, ko), lerp(420, 640, ko), 1, 10 - 40 * (1 - ko))
    kp = prog(u, 5.5 * B, .4); put(f, A.phrase, W / 2, lerp(H + 300, 1330, out_back(kp, 1.3)), 1, 4, 1 if kp > 0 else 0)
    return f
def s_patterns(u):
    f = Image.new("RGBA", (W, H), DEEP + (255,))
    big = Image.new("RGB", (1700, 2700), DEEP)
    for i, col in enumerate(A.strips):
        sp = (420 if i % 2 else -420); off = int(([0, 300, 120, 450, 220][i] + 900 * 2 + sp * u) % 900)
        big.paste(col.crop((0, off, 340, off + 2700)), (i * 340, 0))
    big = big.convert("RGBA").rotate(14, expand=True, resample=Image.BILINEAR)
    f.alpha_composite(big, ((W - big.width) // 2, (H - big.height) // 2)); f.alpha_composite(A.vig5)
    k = prog(u, 1 * B, .35); put(f, A.p_pat, W / 2, 960, lerp(.5, 1, out_back(k, 2)), 0, k)
    k = prog(u, 2.5 * B, .3); put(f, A.p_pat2, W / 2, 1080 + 30 * (1 - out_cubic(k)), 1, 0, k)
    return f
def s_count(u):
    f = drift(A.vel2, u, 1.0, 1.05, 2.7); f.alpha_composite(A.vig6); sparkles(f, u, 40, 5, (40, 220, W - 40, 1500))
    n = int(round(90 * out_cubic(prog(u, 0, 4 * B))))
    land = prog(u, 4 * B, .3); s = 1 + .12 * math.sin(math.pi * land)
    put(f, tsprite(str(n), font("b", 420), GOLD2, (10, 0, 0, 200)), W / 2, 640, s)
    put(f, A.t_90, W / 2, 880, 1, 0, prog(u, .3, .3))
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    for r in range(3):
        row = A.chips[r * 3:(r + 1) * 3]; ws = [c.width - 60 for c in row]; x = W / 2 - (sum(ws) + 36) / 2
        for j, (c, w) in enumerate(zip(row, ws)):
            k = prog(u, CHIP_T[r] - T0["count"] + j * .07, .3); put(f, c, x + w / 2, [1010, 1115, 1220][r], out_back(k, 2), 0, min(1, k * 3)); x += w + 18
    for i, (spr, x, y) in enumerate(A.props6):
        k = out_back(prog(u, .1 + i * .08, .4), 1.6); put(f, spr, x, y + 8 * math.sin(u * 2.2 + i), k, 4 * math.sin(u * 1.7 + i))
    return f
def s_end(u):
    f = drift(A.vel, u, 1.06, 1.0, 3.2); f.alpha_composite(A.vig5)
    sparkles(f, u, 30, 21, (40, 420, W - 40, 1150))
    k = prog(u, 0, .6); gy = 250 + A.garland.height / 2 - 60 - 120
    put(f, A.garland, W / 2, lerp(-A.garland.height / 2, gy, out_back(k, 1.3)), 1, 2 * math.sin(u * 1.4))
    k = prog(u, 2 * B, .45); put(f, A.e1, W / 2, 640 + 40 * (1 - out_cubic(k)), 1, 0, k)
    k = prog(u, 3 * B, .45); put(f, A.e2, W / 2, 780 + 40 * (1 - out_cubic(k)), 1, 0, k)
    rule(f, W / 2, 880, 460, k=out_cubic(prog(u, 4 * B, .4))); put(f, A.e3, W / 2, 945, 1, 0, prog(u, 4.5 * B, .3))
    for i, (spr, x) in enumerate(A.endchars):
        t0 = END_T[i] - T0["end"]; k = prog(u, t0, .45)
        if k <= 0: continue
        hop = math.sin(math.pi * clamp(k)) * 70; y = 1400 - spr.info["rh"] / 2
        put(f, spr, x, lerp(H + 300, y, out_cubic(k)) - hop * (k < 1), 1, 0, 1)
    k = prog(u, CTA_T - T0["end"], .35); pulse = 1 + .035 * math.sin(max(0, u - (CTA_T - T0["end"]) - .4) * 5.5) * (u > CTA_T - T0["end"] + .4)
    put(f, A.cta, W / 2, 1510, out_back(k, 2) * pulse, 0, min(1, 3 * k))
    put(f, A.bio, W / 2, 1610, 1, 0, prog(u, CTA_T - T0["end"] + .3, .3))
    # final fade to deep burgundy
    fade = prog(u, T1["end"] - T0["end"] - .25, .25)
    if fade > 0: f.alpha_composite(Image.new("RGBA", (W, H), DEEP + (int(255 * fade),)))
    return f
FN = {"hook": s_hook, "cast": s_cast, "details": s_details, "card": s_card, "patterns": s_patterns, "count": s_count, "end": s_end}

# ---------------------------------------------------------------- timeline & cues
CAST_T = [T0["cast"] + 1 * B + i * B / 2 for i in range(16)]             # pops on eighth notes
CHIP_T = [T0["count"] + (4.2 + 0.8 * r) * B for r in range(3)]
END_T = [T0["end"] + (5 + i * .5) * B for i in range(4)]
CTA_T = T0["end"] + 7 * B
TR = 0.2                                                                 # push transition length
def build_cues():
    CUES.clear()
    for n, s, e in SCENES[1:]: cue(s * B - TR / 2, "swish", -9, f"push into {n}")
    h = T0["hook"]; cue(h + 0.0, "swish_soft", -10, "bow drops"); cue(h + 0.5, "pop_soft", -16, "bow lands")
    cue(h + .5 * B, "pop_soft", -18, "line 1"); cue(h + 2 * B, "pop_soft", -18, "line 2"); cue(h + 3.5 * B, "bell", -9, "someone…")
    cue(h + 4 * B, "chime", -13, "fawn rises")
    for i, t in enumerate(CAST_T): cue(t, f"pop{i % 4}", -10 - (i % 3), f"cast {A.chars[i]}")
    d = T0["details"]; cue(d + 3 * B, "chime", -12, "magnifier"); cue(d + 5 * B, "pop_soft", -14, "spec pill")
    c = T0["card"]; cue(c + 2 * B, "pop0", -11, "wreath"); cue(c + 3.5 * B, "swish_soft", -12, "holly"); cue(c + 4.5 * B, "swish_soft", -12, "ornament")
    cue(c + 5.5 * B, "swish", -12, "phrase"); cue(c + 5.5 * B + .3, "bell", -12, "phrase lands")
    p = T0["patterns"]; cue(p + .05, "whoosh", -10, "strips"); cue(p + B, "pop1", -10, "pattern pill"); cue(p + 2.5 * B, "pop_soft", -15, "sub pill")
    q = T0["count"]
    for k in range(10): cue(q + 4 * B * out_cubic_inv(k / 10), "tick", -20, "count tick")
    cue(q + 4 * B, "bell", -9, "90 lands")
    for r, t in enumerate(CHIP_T):
        for j in range(3): cue(t + j * .07, f"pop{(r + j) % 4}", -15, "chip")
    e = T0["end"]; cue(e + .05, "swish_soft", -11, "garland"); cue(e + .45, "pop_soft", -15, "garland lands")
    for t in END_T: cue(t + .4, "pop2", -13, "char hop")
    cue(CTA_T, "bell", -8, "CTA")
def out_cubic_inv(y): return 1 - (1 - y) ** (1 / 3)

def frame(t):
    names = [n for n, s, e in SCENES]
    i = max(k for k, (n, s, e) in enumerate(SCENES) if s * B <= t + 1e-9)
    n = names[i]; u = t - T0[n]
    # vertical push transition around each cut
    if i > 0 and u < TR / 2:
        prev = names[i - 1]; return push(FN[prev](T1[prev] - T0[prev] + u), FN[n](u), .5 + u / TR)
    if i < len(names) - 1 and T1[n] - t < TR / 2:
        nxt = names[i + 1]; return push(FN[n](u), FN[nxt](0), .5 - (T1[n] - t) / TR)
    return FN[n](u)
def push(a_, b_, x):
    x = in_out(clamp(x)); off = int(H * x); f = Image.new("RGBA", (W, H))
    f.paste(a_.crop((0, off, W, H)), (0, 0)); f.paste(b_.crop((0, 0, W, off)), (0, H - off)) if off > 0 else None
    return f

# ---------------------------------------------------------------- audio
SFX = {"pop0": "reel/dl/pop1.ogg", "pop1": "reel/dl/pop5.ogg", "pop2": "reel/dl/pop6.ogg", "pop3": "reel/dl/pop3.ogg",
       "pop_soft": "reel/dl/z_pops/3pops/pop1.ogg", "tick": "reel/dl/pop2.ogg",
       "swish": "reel/dl/z_swish/swishes/swish-3.wav", "swish_soft": "reel/dl/z_swish/swishes/swish-9.wav",
       "whoosh": "reel/dl/whoosh2_0.wav", "bell": "reel/dl/bell_ding3.wav", "chime": "reel/dl/bell_ding2.wav"}
SR = 48000
def load(path, ss=0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-i", path] + (["-t", str(dur)] if dur else []) + ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
def mix(out_wav):
    n = int((DUR + .1) * SR); mixb = np.zeros((n, 2), np.float32)
    mus = load(MUSIC, MUSIC_IN, DUR + .1)[:n]; fi = int(.03 * SR); mus[:fi] *= np.linspace(0, 1, fi)[:, None]
    mixb[:len(mus)] += mus * 10 ** (-3 / 20)
    cache = {}
    for c in CUES:
        if c["sfx"] not in cache:
            x = load(SFX[c["sfx"]])
            if c["sfx"] == "whoosh": x = x[:int(1.2 * SR)] * np.linspace(1, 0, int(1.2 * SR))[:, None] ** 2
            # trim leading silence so the transient lands on the frame
            on = np.argmax(np.abs(x).max(1) > .02 * np.abs(x).max()); x = x[on:]
            cache[c["sfx"]] = x / (np.abs(x).max() + 1e-9)
        x = cache[c["sfx"]] * 10 ** (c["gain_db"] / 20); s = int(c["t"] * SR)
        if s < 0: x = x[-s:]; s = 0
        e = min(n, s + len(x)); mixb[s:e] += x[:e - s]
    import scipy.io.wavfile as wf
    wf.write(out_wav, SR, mixb)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    build(); build_cues()
    os.makedirs("reel/plan", exist_ok=True); os.makedirs("reel/out", exist_ok=True); os.makedirs("reel/cache", exist_ok=True)
    json.dump({"fps": FPS, "beat_s": BEAT, "duration_s": DUR, "music": {"file": "Jingle Bells — Kevin MacLeod (incompetech.com), CC BY 4.0", "in_s": MUSIC_IN},
               "scenes": [{"name": n, "t0": s * B, "t1": e * B} for n, s, e in SCENES], "cues": CUES}, open("reel/plan/beats.json", "w"), indent=1)
    if mode == "preview":
        ts = [float(x) for x in sys.argv[2:]] or [.3, 1.0, 1.6, 2.5, 3.2, 4.0, 5.5, 6.9, 7.8, 9.4, 10.5, 11.4, 12.4, 13.9, 15.0, 16.3, 17.2, 18.5]
        th = 480; tw = int(th * W / H); cols = 9; rows = math.ceil(len(ts) / cols)
        sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 40) + 10), (20, 8, 10)); d = ImageDraw.Draw(sheet)
        for k, t in enumerate(ts):
            r, c = divmod(k, cols); im = frame(t).convert("RGB").resize((tw, th), Image.BILINEAR)
            sheet.paste(im, (10 + c * (tw + 10), 10 + r * (th + 40))); d.text((10 + c * (tw + 10) + tw / 2, r * (th + 40) + th + 28), f"{t:.2f}s", font=font("r", 20), fill=CREAM, anchor="mm")
        sheet.save("reel/cache/preview_sheet.jpg", quality=88); print("reel/cache/preview_sheet.jpg")
        return
    half = "--half" in sys.argv; ow, oh = (W // 2, H // 2) if half else (W, H)
    wav = "reel/cache/mix.wav"; mix(wav)
    out = "reel/cache/silent.mp4"; nf = int(round(DUR * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for k in range(nf):
        im = frame(k / FPS).convert("RGB")
        if half: im = im.resize((ow, oh), Image.BILINEAR)
        p.stdin.write(im.tobytes())
        if k % 60 == 0: print(f"frame {k}/{nf}", flush=True)
    p.stdin.close(); p.wait()
    final = "reel/out/velvet_bow_woodland_reel_v1" + ("_half" if half else "") + ".mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-i", wav, "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", final], check=True)
    print(final)

if __name__ == "__main__": main()
