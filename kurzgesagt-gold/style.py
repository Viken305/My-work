"""Style frames for approval (vertical 1080x1920).  python3 style.py -> out/style/"""
import math, os

from PIL import Image

from gold import *  # noqa: F401,F403

OUT = os.path.join(HERE, "out", "style")


def caption(c, words, hi, y=1480):
    """Burned-in caption style: big ExtraBold, white with one gold word."""
    f = font(70, 800)
    widths = [f.measureText(w) + 20 for w in words]
    x = W / 2 - sum(widths) / 2
    for w, ww in zip(words, widths):
        rgb = GOLD if w == hi else WHITE
        text(c, w, x + ww / 2 + 3, y + 5, 70, (20, 10, 0), 200, 800)
        text(c, w, x + ww / 2, y, 70, rgb, 255, 800)
        x += ww


def chip(c, s, x, y, rgb=GOLD, size=30):
    f = font(size, 800)
    w = f.measureText(s) + size * 1.6 + len(s) * size * 0.12
    c.drawRRect(rrect(x - w / 2, y - size * 1.05, w, size * 1.6, size * 0.8), fill((14, 10, 30), 210))
    c.drawRRect(rrect(x - w / 2, y - size * 1.05, w, size * 1.6, size * 0.8), stroke(rgb, 3, 230))
    text(c, s, x, y, size * 0.8, rgb, 255, 800, spacing=size * 0.12)


def sheet(c, t):
    space_bg(c, t, warm=0.3)
    text(c, "MEET AURI", W / 2, 200, 96, WHITE, 255, 800, spacing=10)
    text(c, "A GOLD ATOM · 79 PROTONS · OUR GUIDE", W / 2, 260, 26, GOLD, 240, 800, spacing=4)
    exprs = [("shocked", "SHOCKED"), ("worried", "WORRIED"), ("laugh", "LAUGH"), ("determined", "DETERMINED"), ("smug", "SMUG"), ("focused", "CURIOUS")]
    for i, (e, lab) in enumerate(exprs):
        x, y = 200 + (i % 3) * 340, 1110 + (i // 3) * 360
        auri(c, x, y, 95, t + i * 0.7, pose(e), (0.3, 0.0), hard_hat=(e == "determined"))
        text(c, lab, x, y + 190, 22, WHITE, 220, 800, spacing=4)
    text(c, "POLISHED METAL · ORBITING ELECTRONS · ANIMATED FACE · HARD HAT FOR MINING SCENES", W / 2, 1830, 17, WHITE, 170, 800, spacing=2)


def sf0(c, t):
    """Cold open (first frame of the video): the kilonova at full blast, hero line slammed over it."""
    space_bg(c, t, warm=0.5)
    kilonova(c, W / 2, 860, 640, t, 0.22, seed=5)
    from kinetic import gold_word
    text(c, "THIS EXPLOSION", W / 2, 1280, 92, WHITE, 255, 800, spacing=4)
    text(c, "MADE YOUR", W / 2, 1385, 92, WHITE, 255, 800, spacing=4)
    gold_word(c, "GOLD", W / 2, 1560, 200, 255, 1.0, t)


def sf1(c, t):
    """Hook: a ring floating in space, title."""
    space_bg(c, t, warm=0.4)
    cx, cy = W / 2, 980
    light(c, cx, cy, 700, GOLD, 70)
    # gold ring (torus seen at an angle)
    for k, (w_, a_) in enumerate(((150, 255), (110, 255))):
        pass
    outer = skia.Rect.MakeXYWH(cx - 330, cy - 120, 660, 240)
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=70,
                   Shader=linear((cx - 330, cy - 120), (cx + 330, cy + 120), [GOLD_DEEP, GOLD_HI, GOLD, GOLD_MID, GOLD_HI, GOLD_DEEP], [0, 0.2, 0.4, 0.6, 0.8, 1]))
    back = skia.Path()
    back.addArc(outer, 180, 180)
    c.drawPath(back, p)
    front = skia.Path()
    front.addArc(outer, 0, 180)
    c.drawPath(front, p)
    c.drawArc(skia.Rect.MakeXYWH(cx - 300, cy - 105, 600, 210), 20, 60, False, stroke(WHITE, 8, 180))
    sparkle4(c, cx + 260, cy - 60, 40, 255)
    sparkle4(c, cx - 290, cy + 40, 26, 220)
    text(c, "HOW EARTH", W / 2, 360, 90, WHITE, 255, 800, spacing=8)
    text(c, "MAKES GOLD", W / 2, 470, 120, GOLD, 255, 800, spacing=8)
    caption(c, ["OLDER", "THAN", "THE", "SUN."], "SUN.")


def sf2(c, t):
    """The forge: two neutron stars collide, gold flung out."""
    space_bg(c, t, warm=0.2)
    cx, cy = W / 2, 820
    for k in range(5):
        r = 120 + k * 120
        c.drawOval(skia.Rect.MakeXYWH(cx - r * 1.3, cy - r * 0.5, r * 2.6, r), stroke((150, 140, 255), 3, 90 - k * 14))
    kilonova(c, cx, cy, 520, t, 0.34)
    neutron_star(c, cx - 90, cy + 30, 30, t, 120)
    chip(c, "NEUTRON STARS COLLIDE", W / 2, 300, NEUTRON, 32)
    caption(c, ["GOLD", "IS", "FORGED"], "GOLD")


def sf3(c, t):
    """The lost gold: molten Earth, gold drops sinking to the core."""
    space_bg(c, t)
    cx, cy, R = W / 2, 900, 420
    earth_section(c, cx, cy, R, t, molten=1.0)
    rng = np.random.default_rng(4)
    for i in range(26):
        an = rng.uniform(0, 6.28)
        d = R * rng.uniform(0.35, 0.95)
        x, y = cx + math.cos(an) * d, cy + math.sin(an) * d
        tx, ty = cx + math.cos(an) * (d + 60), cy + math.sin(an) * (d + 60)
        c.drawLine(x, y, tx, ty, stroke(GOLD_HI, 4, 120))
        c.drawCircle(x, y, 18, fill((40, 10, 10), 160))
        gold_sphere(c, x, y, rng.uniform(10, 15), (255, 120, 60))
    chip(c, "HEAVY METALS SINK TO THE CORE", W / 2, 300, GOLD, 30)
    caption(c, ["LOST", "TO", "THE", "CORE"], "CORE", y=1640)


def sf4(c, t):
    """The squeeze: an earthquake crack, water flashing to steam, a gold vein left behind; Auri in a hard hat."""
    c.drawPaint(fill((30, 22, 40)))
    rock_wall(c, 0, 0, W, H, t, 5, (120, 86, 92))
    for k in range(9):
        y = k * 230 + 60
        c.drawRect(skia.Rect.MakeXYWH(0, y, W, 90), fill((70, 50, 70) if k % 2 else (150, 110, 100), 70))
    crack = skia.Path()
    pts = [(560, -20), (520, 300), (600, 520), (500, 780), (590, 1040), (520, 1300), (600, 1560), (560, 1940)]
    crack.moveTo(*pts[0])
    for p_ in pts[1:]:
        crack.lineTo(*p_)
    c.drawPath(crack, stroke((20, 10, 20), 70))
    c.drawPath(crack, stroke(QUARTZ, 46))
    c.drawPath(crack, stroke((255, 255, 255), 10, 120))
    rng = np.random.default_rng(7)
    for i in range(30):      # gold flecks in the quartz vein
        k = rng.uniform(0.05, 0.95)
        seg = int(k * (len(pts) - 1))
        u = k * (len(pts) - 1) - seg
        x = lerp(pts[seg][0], pts[seg + 1][0], u) + rng.uniform(-14, 14)
        y = lerp(pts[seg][1], pts[seg + 1][1], u)
        gold_sphere(c, x, y, rng.uniform(5, 12), (200, 190, 220))
    for i in range(14):      # steam puffs
        y = 700 + i * 30
        c.drawCircle(560 + 40 * math.sin(i * 1.7), y - (i * 13) % 200, 30 + i * 2, fill(WHITE, 60))
    for s in (-1, 1):
        c.drawLine(560 + s * 120, 900, 560 + s * 220, 900, stroke((255, 220, 120), 8))
    chip(c, "EARTHQUAKE!", W / 2, 300, (255, 160, 120), 34)
    caption(c, ["LEFT", "BEHIND", "IN", "A", "VEIN"], "VEIN", y=1640)


def sf5(c, t):
    """Scale: all gold ever mined = a 22 m cube, next to a house and a person."""
    c.drawPaint(shaded(linear((0, 0), (0, H), [(60, 110, 190), (150, 190, 230)])))
    c.drawRect(skia.Rect.MakeXYWH(0, 1250, W, 670), fill((90, 150, 90)))
    gx, gy, s = 330, 1250, 440          # cube front face (22 m = 440 px)
    top = skia.Path()
    top.moveTo(gx, gy - s)
    top.lineTo(gx + 140, gy - s - 90)
    top.lineTo(gx + s + 140, gy - s - 90)
    top.lineTo(gx + s, gy - s)
    top.close()
    side = skia.Path()
    side.moveTo(gx + s, gy)
    side.lineTo(gx + s + 140, gy - 90)
    side.lineTo(gx + s + 140, gy - s - 90)
    side.lineTo(gx + s, gy - s)
    side.close()
    c.drawRect(skia.Rect.MakeXYWH(gx, gy - s, s, s), shaded(linear((gx, gy - s), (gx + s, gy), [GOLD_HI, GOLD, GOLD_MID])))
    c.drawPath(top, shaded(linear((gx, gy - s - 90), (gx + s, gy - s), [GOLD_HI, GOLD])))
    c.drawPath(side, shaded(linear((gx + s, 0), (gx + s + 140, 0), [GOLD_MID, GOLD_DEEP])))
    c.drawLine(gx + 30, gy - s + 30, gx + 160, gy - s + 30, stroke(WHITE, 10, 150))
    # house (about 8 m tall) and a person for scale
    hx = 840
    c.drawRect(skia.Rect.MakeXYWH(hx, gy - 130, 140, 130), fill((230, 220, 210)))
    c.drawPath(poly([(hx - 15, gy - 130), (hx + 70, gy - 190), (hx + 155, gy - 130)]), fill((180, 80, 70)))
    c.drawRect(skia.Rect.MakeXYWH(hx + 55, gy - 60, 30, 60), fill((120, 80, 60)))
    c.drawCircle(1010, gy - 32, 6, fill((60, 50, 70)))
    c.drawRect(skia.Rect.MakeXYWH(1006, gy - 26, 8, 26), fill((60, 50, 70)))
    c.drawLine(gx - 40, gy, gx - 40, gy - s, stroke(WHITE, 4))
    text(c, "22 M", gx - 60, gy - s / 2, 36, WHITE, 255, 800, "right")
    chip(c, "ALL GOLD EVER MINED", W / 2, 300, GOLD, 34)
    text(c, "≈ 212,000 TONNES", W / 2, 400, 54, WHITE, 255, 800, spacing=4)
    caption(c, ["FITS", "IN", "ONE", "CUBE"], "CUBE", y=1640)


def safe_zones(c, t):
    """Layout guide: what stays clear of the YouTube Shorts interface."""
    sf2(c, t)
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 220), fill((255, 60, 60), 70))
    c.drawRect(skia.Rect.MakeXYWH(0, 1520, W, 400), fill((255, 60, 60), 50))
    c.drawRect(skia.Rect.MakeXYWH(W - 150, 900, 150, 620), fill((255, 60, 60), 70))
    text(c, "TOP: SEARCH / BACK BUTTONS", W / 2, 120, 26, WHITE, 255, 800, spacing=3)
    text(c, "RIGHT: LIKE · COMMENT · SHARE", W - 75, 1210, 18, WHITE, 255, 800, spacing=1)
    text(c, "BOTTOM: TITLE · CHANNEL · MUSIC", W / 2, 1820, 26, WHITE, 255, 800, spacing=3)


FRAMES = [("sf0_cold_open", sf0), ("sf1_hook", sf1), ("sf2_forge", sf2), ("sf3_lost_gold", sf3), ("sf4_earthquake_vein", sf4), ("sf5_cube", sf5),
          ("layout_safe_zones", safe_zones)]

if __name__ == "__main__":
    from premium import render_premium
    os.makedirs(OUT, exist_ok=True)
    for name, fn in FRAMES:
        p = os.path.join(OUT, f"{name}.png")
        Image.fromarray(render_premium(fn, 1.4, samples=1)).save(p)
        print(p)
