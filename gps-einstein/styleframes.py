"""Style frames for the Frosted Glass look: four key shots rendered as stills, plus a contact sheet.

    python3 styleframes.py            -> out/styleframes/sf1_phone.png … sf4_title.png, contact.png
"""
import math, os, sys

import cv2
import numpy as np
import skia

from glass import (W, H, INK, CARBON, CARD, PAPER, SMOKE, AMBER, VIOLET, CYAN, mix, paint, label, width, layer, mask,
                   over, glass, shadow, defocus, shard, glass_text, backdrop, earth, orbit_points, orbit_line,
                   mini_sat, sat_mask, clock, caption, post, rrect, glow_dot, caustic_light, ellipse)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "styleframes")


# ---------------------------------------------------------------- the phone and its map
def city_map(c, x, y, w, h, t, dot, pin, seed=4):
    """A night-mode city map inside the phone screen: blocks, streets, a river, a route, the coffee pin
    and the blue dot with its accuracy halo. dot / pin: positions in screen-local units 0..1."""
    rng = np.random.default_rng(seed)
    c.save()
    c.clipRRect(rrect(x, y, w, h, 46), doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), paint((10, 22, 44), 235))
    c.translate(x + w / 2, y + h / 2)
    c.rotate(-16)
    # blocks between a jittered street grid
    xs = np.cumsum(rng.uniform(44, 78, 26)) - 900
    ys = np.cumsum(rng.uniform(44, 78, 36)) - 1250
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            if rng.random() < 0.08:
                continue
            park = rng.random() < 0.06
            r = skia.Rect.MakeLTRB(xs[i] + 5, ys[j] + 5, xs[i + 1] - 5, ys[j + 1] - 5)
            c.drawRRect(skia.RRect.MakeRectXY(r, 4, 4), paint((22, 52, 66) if park else (20, 34, 60), 255))
    for k, X in enumerate(xs):
        c.drawLine(X, -1300, X, 1300, paint((52, 74, 108) if k % 5 == 2 else (36, 54, 86), 255, stroke=10 if k % 5 == 2 else 4))
    for k, Y in enumerate(ys):
        c.drawLine(-1000, Y, 1000, Y, paint((52, 74, 108) if k % 6 == 3 else (36, 54, 86), 255, stroke=10 if k % 6 == 3 else 4))
    # river
    river = skia.Path()
    river.moveTo(-1000, 380)
    river.cubicTo(-300, 180, 200, 620, 1000, 420)
    c.drawPath(river, paint((30, 70, 120), 255, stroke=58))
    c.drawPath(river, paint(CYAN, 40, stroke=2))
    c.restore()
    c.save()
    c.clipRRect(rrect(x, y, w, h, 46), doAntiAlias=True)
    px, py = x + pin[0] * w, y + pin[1] * h
    dx, dy = x + dot[0] * w, y + dot[1] * h
    # route from the dot to the pin (dashed, amber)
    route = skia.Path()
    route.moveTo(dx, dy)
    route.cubicTo(dx + 40, dy - 120, px - 60, py + 140, px, py + 30)
    rp = paint(AMBER, 230, stroke=8)
    rp.setPathEffect(skia.DashPathEffect.Make([18, 14], -t * 60))
    c.drawPath(route, paint(AMBER, 70, sigma=8, stroke=16))
    c.drawPath(route, rp)
    # coffee pin
    c.drawCircle(px, py, 30, paint(AMBER, 255))
    c.drawCircle(px, py, 30, paint(PAPER, 255, stroke=3))
    cup = rrect(px - 11, py - 9, 20, 18, 4)
    c.drawRRect(cup, paint(INK))
    c.drawCircle(px + 12, py, 6, paint(INK, 255, stroke=3))
    label(c, "COFFEE", px, py - 48, 22, "mono_bold", AMBER, 255, "center", 0.12)
    # the blue dot
    pulse = (t * 0.8) % 1
    c.drawCircle(dx, dy, 40 + pulse * 70, paint(CYAN, 70 * (1 - pulse), stroke=3))
    c.drawCircle(dx, dy, 64, paint(CYAN, 40))
    glow_dot(c, dx, dy, 15, CYAN, 255, 3.2)
    c.drawCircle(dx, dy, 15, paint(PAPER, 255, stroke=4))
    c.restore()


def phone(img, cx, cy, w, h, rot, t, dot=(0.42, 0.62), pin=(0.66, 0.36)):
    """A frosted-glass phone: a thick glass slab with rounded corners, the map glowing inside, a sheen."""
    def frame(c, p):
        c.save()
        c.rotate(rot, cx, cy)
        c.drawRRect(rrect(cx - w / 2, cy - h / 2, w, h, 82), p)
        c.restore()
    m = mask(frame)
    shadow(img, m, 50, 80, 50, 0.6)
    glass(img, m, bevel=34, refract=26, frost=12, tint=0.30, lift=10, rim=1.1, sheen=(0.28, 60, 0.12))
    inset = 24
    sw, sh = w - 2 * inset, h - 2 * inset

    def screen(c):
        c.save()
        c.rotate(rot, cx, cy)
        city_map(c, cx - sw / 2, cy - sh / 2, sw, sh, t, dot, pin)
        c.drawRRect(rrect(cx - 70, cy - sh / 2 + 22, 140, 40, 20), paint(INK, 255))     # camera island
        label(c, "9:41", cx - sw / 2 + 48, cy - sh / 2 + 54, 28, "semibold", PAPER, 230)
        c.restore()
    img = over(img, layer(screen))
    # a cover-glass glint over the screen
    gl = mask(lambda c, p: (c.save(), c.rotate(rot, cx, cy),
                            c.drawRRect(rrect(cx - sw / 2, cy - sh / 2, sw, sh, 46), p), c.restore()))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    band = np.exp(-(((xx - cx) * 0.8 + (yy - cy) * 0.6 + 120) / 70) ** 2)
    img += np.float32(PAPER) * (gl * band * 0.10)[..., None]
    return img


# ---------------------------------------------------------------- frames
def sf1_phone(t=1.3):
    """Shot 1: the glass phone with the map; Einstein's clock equation etched in glass behind it."""
    img = backdrop(t, glow=(0.42, 0.40), floor=0.76, pool=(560, 1640, 320, 60))
    img = defocus(img, lambda c: [c.drawRRect(rrect(x, y, w_, h_, 40), paint(mix(CARD, PAPER, 0.2), 120))
                                  for x, y, w_, h_ in ((-80, 260, 300, 420), (850, 980, 320, 520))], 26, 0.7)
    for s, y, size, a in (("Δτ ≈ Δt", 400, 130, 1.0), ("(1 + Φ/c² − v²/2c²)", 520, 70, 1.0)):
        img = glass_text(img, s, W / 2, y, size, "light", 0.0, tint=0.18, lift=20, caustic_t=t, rim=1.0)
    img = phone(img, 540, 1060, 470, 940, -7, t)
    img = defocus(img, lambda c: shard(c, 960, 1640, 150, 0.6), 16, 0.8)
    img = defocus(img, lambda c: shard(c, 110, 300, 110, 2.2), 12, 0.6)
    img = caption(img, ["Einstein's", "math."], hl={0: VIOLET})
    return post(img, t)


def sf2_orbit(t=2.0):
    """Shots 4–5: the glass Earth, six orbital planes of satellites, one hero satellite sending its signal down."""
    img = backdrop(t, glow=(0.5, 0.55), floor=0.95, caustic=0.4)
    cx, cy, R = 540, 1060, 300
    planes = [(74, -18 + k * 30, k * 0.9) for k in range(6)]
    orbits = [orbit_points(cx, cy, 470 + 14 * (k % 3), inc, rot, 220, ph) for k, (inc, rot, ph) in enumerate(planes)]

    def back(c):
        for pts in orbits:
            orbit_line(c, pts, False, CYAN, 200, 1.6)
    img = over(img, layer(back))
    img, proj = earth(img, cx, cy, R, t, lon0=-15, lat0=28)
    you = proj(-3.7, 40.4)                       # Madrid, facing us

    def front(c):
        for k, pts in enumerate(orbits):
            orbit_line(c, pts, True, CYAN, 230, 1.8)
            for j in range(5):
                x, y, z = pts[int((j / 5 + t * 0.012 + k * 0.07) % 1 * 220)]
                if z >= 0 or math.hypot(x - cx, y - cy) > R:
                    mini_sat(c, x, y, 13 if z >= 0 else 9, 0.3, 255 if z >= 0 else 110, 1 if z >= 0 else 0.3)
    img = over(img, layer(front))
    hx, hy = 800, 520
    # the signal: rings of light leaving the hero satellite and a beam down to you
    beam = layer(lambda c: (c.drawLine(hx, hy, you[0], you[1], paint(CYAN, 90, sigma=10, stroke=18)),
                            c.drawLine(hx, hy, you[0], you[1], paint(mix(CYAN, PAPER, 0.4), 230, stroke=3))))
    img = img + beam[0]
    ang = math.atan2(you[1] - hy, you[0] - hx)

    def rings(c):
        for k in range(3):
            u = ((t * 0.6) + k / 3) % 1
            r = 40 + u * 330
            c.drawArc(skia.Rect.MakeLTRB(hx - r, hy - r, hx + r, hy + r), math.degrees(ang) - 26, 52, False,
                      paint(CYAN, 255 * (1 - u) ** 1.2, stroke=5))
        glow_dot(c, you[0], you[1], 13, AMBER, 255, 3.6)
        label(c, "YOU", you[0] - 34, you[1] + 10, 30, "mono_bold", AMBER, 255, "right", 0.2)
    img = over(img, layer(rings))
    m = sat_mask(hx, hy, 70, -0.45)
    shadow(img, m, 20, 30, 20, 0.4)
    glass(img, m, bevel=14, refract=12, frost=8, tint=0.32, lift=14, rim=1.5, sheen=(0.4, 26, 0.16))
    # the atomic clock glowing inside the satellite body
    img = over(img, layer(lambda c: (glow_dot(c, hx, hy, 11, VIOLET, 255, 4.0),
                                     c.drawCircle(hx, hy, 24, paint(VIOLET, 200, stroke=2)))))
    # a small glass data card: where + when
    card = mask(lambda c, p: c.drawRRect(rrect(hx - 620, hy - 170, 420, 128, 26), p))
    glass(img, card, bevel=16, refract=10, frost=16, tint=0.42, lift=8)
    img = over(img, layer(lambda c: (label(c, "WHERE  40.4°N 3.7°W", hx - 596, hy - 118, 22, "mono", PAPER, 240),
                                     label(c, "WHEN   12:00:00.000 000 000", hx - 596, hy - 76, 22, "mono", VIOLET,
                                           255))))
    img = over(img, layer(lambda c: label(c, "20,200 km UP · 6 ORBITAL PLANES", W / 2, 290, 28, "mono", SMOKE,
                                          255, "center", 0.14)))
    img = caption(img, ["about", "30", "satellites"], hl={1: AMBER})
    return post(img, t)


def sf3_clocks(t=0.8):
    """Shot 13: the GROUND and ORBIT clocks side by side, the sum −7 + 45 = +38 µs a day on a glass card."""
    img = backdrop(t, glow=(0.5, 0.36), floor=0.72, pool=(540, 1500, 420, 60))
    img = defocus(img, lambda c: [c.drawCircle(x, y, r, paint(mix(CARD, PAPER, 0.25), 110))
                                  for x, y, r in ((90, 330, 120), (1010, 1520, 160))], 30, 0.7)
    secs = 10 * 3600 + 8 * 60 + 23.0
    img = clock(img, 285, 700, 205, secs, AMBER, "GROUND", "10:08:23.000 000", t, 0.25)
    img = clock(img, 795, 700, 205, secs + 7.5, VIOLET, "ORBIT", "10:08:23.000 038", t, 0.35)
    # the drift between the two second hands
    img = over(img, layer(lambda c: (label(c, "+38 µs", 540, 440, 36, "mono_bold", VIOLET, 255, "center", 0.05),
                                     label(c, "HAND DRIFT EXAGGERATED", 540, 476, 18, "mono", SMOKE, 200, "center",
                                           0.2))))
    x0, y0, w_, h_ = 110, 1070, 860, 210
    card = mask(lambda c, p: c.drawRRect(rrect(x0, y0, w_, h_, 40), p))
    shadow(img, card, 20, 40, 30, 0.45)
    glass(img, card, bevel=22, refract=14, frost=18, tint=0.4, lift=8, rim=1.3, sheen=(0.7, 50, 0.07))

    def sums(c):
        items = [("−7", PAPER, "SPEED"), ("+", SMOKE, ""), ("45", PAPER, "GRAVITY"), ("=", SMOKE, ""),
                 ("+38", VIOLET, "µs / DAY")]
        xs = [210, 330, 450, 590, 780]
        for (s, rgb, sub), x in zip(items, xs):
            if rgb == VIOLET:
                label(c, s, x, y0 + 128, 96, "mono_bold", rgb, 150, "center", sigma=14)
            label(c, s, x, y0 + 128, 96 if sub else 70, "mono_bold" if sub else "mono", rgb, 255, "center")
            if sub:
                label(c, sub, x, y0 + 176, 22, "mono", SMOKE, 255, "center", 0.2)
    img = over(img, layer(sums))
    img = caption(img, ["gain", "38", "µs"], hl={1: VIOLET, 2: VIOLET})
    return post(img, t)


def sf4_title(t=3.0):
    """Shot 3: the title in glass letters, caustics moving inside them, an orbit arc behind."""
    img = backdrop(t, glow=(0.5, 0.45), floor=0.80, caustic=1.2, pool=(540, 1650, 420, 80), seed=1.0)
    pts = orbit_points(540, 900, 620, 72, -14, 260, 0.0)
    img = over(img, layer(lambda c: (orbit_line(c, pts, False, CYAN, 255, 2), orbit_line(c, pts, True, CYAN, 255, 2),
                                     mini_sat(c, pts[205][0], pts[205][1], 18, 0.2))))
    img = over(img, layer(lambda c: label(c, "HOW GPS USES RELATIVITY", W / 2, 560, 30, "mono", SMOKE, 255,
                                          "center", 0.3)))
    for s, y, size, rgb, glow in (("YOUR PHONE", 740, 128, PAPER, None), ("DOES", 880, 128, PAPER, None),
                                  ("EINSTEIN'S", 1060, 168, mix(VIOLET, PAPER, 0.35), VIOLET),
                                  ("MATH", 1220, 168, PAPER, None)):
        img = glass_text(img, s, W / 2, y, size, "black", 0.0, tint=0.30, lift=30, rgb=rgb, caustic_t=t, glow=glow)
    img = defocus(img, lambda c: shard(c, 940, 330, 130, 1.1), 14, 0.7)
    img = defocus(img, lambda c: shard(c, 120, 1500, 170, 3.6), 18, 0.7)
    return post(img, t)


FRAMES = [("sf1_phone", sf1_phone), ("sf2_orbit", sf2_orbit), ("sf3_clocks", sf3_clocks), ("sf4_title", sf4_title)]


def contact(paths):
    ims = [cv2.resize(cv2.imread(p), (W // 2, H // 2), interpolation=cv2.INTER_AREA) for p in paths]
    gap = 24
    sheet = np.full((H // 2 + 2 * gap, len(ims) * (W // 2 + gap) + gap, 3), 12, np.uint8)
    for i, im in enumerate(ims):
        x = gap + i * (W // 2 + gap)
        sheet[gap:gap + H // 2, x:x + W // 2] = im
    cv2.imwrite(os.path.join(OUT, "contact.png"), sheet)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    want = sys.argv[1:]
    paths = []
    for name, fn in FRAMES:
        p = os.path.join(OUT, name + ".png")
        if not want or name in want:
            img = fn()
            cv2.imwrite(p, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            print("wrote", p)
        paths.append(p)
    if all(os.path.exists(p) for p in paths):
        contact(paths)
