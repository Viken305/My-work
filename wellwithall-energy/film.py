"""WellWithAll Energy: 12.5 s brand reel, cut to a 120 BPM track (one beat = 0.5 s).

Structure follows the reference reel (Henki, @bymyno_ / @eun.wip):
  0.0  starburst flavours, a cut every beat (syncopated groove)
  2.0  logo + fruit stickers
  3.0  FEEL-GOOD / ENERGY, / ANYTIME slams with fizz
  4.0  four product photos, a cut every beat, claim badges
  6.0  claim stack scrolling in eighth-note jumps
  7.0  break: bass drops out, the lemon sinks (pitch slide down), then zooms in on a riser
  8.0  the drop: four-on-the-floor, a can lands on every beat
  10.0 photo collage (crash), 10.5 four-can line-up
  11.0 end card
"""
import math

import numpy as np

from kit import *

DURATION = 12.5
BEAT = 0.5
# every hard cut (audio puts a pop / tick on each, picture punches in on each)
CUTS = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0]

CLAIMS = [["80MG", "FROM TEA"], ["30%", "REAL JUICE"], ["0 ADDED", "SUGARS†"], ["4", "FLAVORS"]]
DISCLAIMER = "†Not a low calorie food. See nutrition facts panel for sugar and calorie content."


def _bubbles(c, t, seed, n=18, rgb=WHITE, a=170, speed=520):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y0, r, v = rng.uniform(40, W - 40), rng.uniform(0, H), rng.uniform(10, 34), rng.uniform(0.6, 1.3)
        y = (y0 - t * speed * v) % (H + 120) - 60
        bubble(c, x + 18 * math.sin(t * 5 + y0), y, r, rgb, a)


# ---------------------------------------------------------------- 0.0 starburst flavours
BURSTS = [("strawberry", [(255, 214, 64), (255, 240, 160)]),
          ("pineapple", [(255, 105, 160), (255, 190, 220)]),
          ("peach", [(255, 150, 70), (255, 214, 150)]),
          ("mango", [LIME, YELLOW, PINK, (255, 150, 70)])]


def s_burst(c, t):
    i = min(int(t / BEAT), 3)
    kind, tones = BURSTS[i]
    tb = t - i * BEAT
    c.clear(col(tones[1]))
    grow = 1 + 0.18 * math.exp(-tb / 0.12)
    rings = [(r * grow, tones[k % len(tones)]) for k, r in enumerate(range(1700, 150, -230))]
    starburst(c, W / 2, H / 2, rings, n=12, rot=t * 0.5 + i * 0.3, depth=0.2)
    _bubbles(c, t, 4, 10, WHITE, 140)
    s = pop(t, i * BEAT, 0.4)
    fruit(c, kind, W / 2, H / 2, 190, rot=12 * math.sin(t * 9), scale=s)


# ---------------------------------------------------------------- 2.0 logo
STICKERS = [("strawberry", 150, 1660, 230, 18), ("lemon", 960, 300, 180, -20), ("peach", 70, 470, 170, 10),
            ("mango", 990, 1480, 200, 25), ("pineapple", 900, 1840, 160, -10), ("lemon", 160, 1080, 110, 40)]


def s_logo(c, t):
    c.clear(col(CREAM))
    for k, (kind, x, y, s, r) in enumerate(STICKERS):
        sc = pop(t, 2.0 + 0.05 * k, 0.5)
        fruit(c, kind, x, y - 25 * (t - 2), s, rot=r + 15 * (t - 2), scale=sc)
    _bubbles(c, t, 9, 8, PINK, 120, 200)
    sc = pop(t, 2.0, 0.5)
    c.save()
    c.translate(W / 2, 880)
    c.scale(sc, sc)
    draw_image(c, logo(GREEN), 0, 0, 900)
    c.restore()
    e = pop(t, 2.5, 0.4)
    if e > 0:
        c.save()
        c.translate(W / 2, 1150)
        c.scale(e, e)
        c.rotate(-4)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-250, -78, 500, 156), 78, 78), paint(PINK))
        text(c, "ENERGY", 0, cap_h(104) / 2, 104, rgb=CREAM, tracking=0.0)
        c.restore()


# ---------------------------------------------------------------- 3.0 feel-good slams
def _slam(c, s, y, size, rgb, t0, t):
    if t < t0:
        return
    u = out_cubic((t - t0) / 0.12)
    sc = 1.7 - 0.7 * u
    c.save()
    c.translate(W / 2, y)
    c.scale(sc, sc)
    text(c, s, 0, cap_h(size) / 2, size, rgb=rgb, a=255 * min(1, u * 2), tracking=-0.03)
    c.restore()


def s_feelgood(c, t):
    late = t >= 3.75
    c.clear(col(YELLOW if late else PINK))
    _bubbles(c, t, 21, 26, WHITE, 190, 700)
    ink = PINK if late else CREAM
    size = fit("FEEL-GOOD", "black", 210, 980, -0.03)
    _slam(c, "FEEL-GOOD", 760, size, ink, 3.0, t)
    _slam(c, "ENERGY,", 980, size, GREEN if late else YELLOW, 3.25, t)
    _slam(c, "ANYTIME", 1200, size, ink, 3.5, t)


# ---------------------------------------------------------------- 4.0 product photos
def s_photos(c, t):
    i = min(int((t - 4.0) / BEAT), 3)
    key = ORDER[i]
    f = FLAVOURS[key]
    tb = t - 4.0 - i * BEAT
    c.clear(col(f["bg"]))
    text(c, "wellwithall.  Energy", W / 2, 250, 54, "bold", GREEN, tracking=0)
    img = image(key + ".jpg")
    z = 1.0 + 0.10 * tb                                   # slow push inside the frame
    sw = img.width() / z
    src = skia.Rect.MakeXYWH((img.width() - sw) / 2, (img.height() - sw) / 2, sw, sw)
    rise = 90 * (1 - out_cubic(tb / 0.14))
    c.save()
    c.translate(W / 2, 900 + rise)
    c.rotate(2.5 if i % 2 else -2.5)
    card = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-480, -480, 960, 960), 44, 44)
    c.drawRRect(card.makeOffset(0, 18), paint((0, 0, 0), 40))
    c.save()
    c.clipRRect(card, doAntiAlias=True)
    draw_image(c, img, 0, 0, 960, 960, src=src)
    c.restore()
    c.restore()
    size = fit(f["name"].upper(), "black", 150, 980, -0.03)
    sc = pop(t, 4.0 + i * BEAT + 0.03, 0.4)
    c.save()
    c.translate(W / 2, 1600)
    c.scale(sc, sc)
    text(c, f["name"].upper(), 0, cap_h(size) / 2, size, rgb=GREEN, tracking=-0.03)
    c.restore()
    b = pop(t, 4.0 + i * BEAT + 0.08, 0.45)
    if b > 0:
        c.save()
        c.translate(860, 470)
        c.scale(b, b)
        badge(c, 0, 0, 165, CLAIMS[i], rot=-12 + 40 * (t - 4.0), fill=PINK if key != "fruit_punch" else GREEN)
        c.restore()


# ---------------------------------------------------------------- 6.0 claim stack
STACK = ["TEA-SOURCED", "CAFFEINE", "REAL FRUIT", "JUICES", "NO ADDED", "SUGARS†", "GLUTEN", "FREE",
         "FEEL-GOOD", "ENERGY", "TEA-SOURCED", "CAFFEINE", "REAL FRUIT", "JUICES"]


def s_claims(c, t):
    dark = t >= 6.5
    c.clear(col(GREEN if dark else LIME))
    step = 0.25                                           # one line per eighth note, snapping
    k = int((t - 6.0) / step)
    u = out_cubic(((t - 6.0) - k * step) / 0.12)
    off = (k + u) * 2                                     # two lines per jump
    lh = 205
    for j, s in enumerate(STACK):
        y = 960 + (j - off) * lh
        if -200 < y < H + 200:
            size = fit(s, "black", 190, 1000, -0.03)
            focus = abs(y - 960) < lh * 1.5
            rgb = (CREAM if focus else LIME) if dark else (GREEN if focus else (240, 252, 200))
            text(c, s, W / 2, y + cap_h(size) / 2, size, rgb=rgb, tracking=-0.03)
    text(c, DISCLAIMER, W / 2, H - 70, 22, "semibold", CREAM if dark else GREEN, a=200, tracking=0)


# ---------------------------------------------------------------- 7.0 break
def s_break(c, t):
    tb = t - 7.0
    zoom = 1 + 2.2 * (prog(t, 7.5, 7.95) ** 3)            # riser: accelerate into the lens
    c.clear(col(CREAM))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(zoom, zoom)
    c.translate(-W / 2, -H / 2)
    drip = smooth(prog(t, 7.05, 7.5))
    c.drawPath(blob(W / 2, 1470, 200 + 260 * drip, seed=3, wob=0.1, t=t * 2), paint(LIME))
    _slam(c, "REAL", 470, 300, GREEN, 7.0, t)
    _slam(c, "FRUIT", 720, 230, PINK, 7.25, t)
    sink = 140 * smooth(prog(t, 7.0, 7.5))                # sinks with the pitch slide
    wob = 25 * math.sin(tb * 30) * prog(t, 7.5, 8.0)      # zig-zag riser wobble
    fruit(c, "lemon", W / 2, 1150 + sink, 250, rot=-15 + 40 * tb + wob + 720 * prog(t, 7.6, 8.0) ** 2,
          scale=pop(t, 7.0, 0.4))
    c.restore()
    fl = prog(t, 7.86, 7.98)
    if fl > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(WHITE, 255 * fl))


# ---------------------------------------------------------------- 8.0 the drop
def s_drop(c, t):
    i = min(int((t - 8.0) / BEAT), 3)
    key = ORDER[i]
    f = FLAVOURS[key]
    tb = t - 8.0 - i * BEAT
    c.clear(col(CREAM))
    c.drawPath(blob(W / 2, 1000, 430 + 40 * math.exp(-tb / 0.1), seed=i + 7, wob=0.09, t=t * 3), paint(f["bg"]))
    fall = 1 - min(1.0, spring(tb / 0.32, 7, 11))         # drops in from above and settles
    land = math.exp(-tb / 0.07) * 0.14 if tb > 0.0 else 0
    can(c, key, W / 2, 1530 - 1400 * fall, 1050, rot=4 * math.sin(t * 6), squash=land)
    for k in range(4):                                     # fruit orbiting the can, popping on the eighth notes
        a = t * 1.8 + k * math.pi / 2
        x, y = W / 2 + 380 * math.cos(a), 1000 + 560 * math.sin(a)
        eighth = (t - 8.0) % 0.25
        sc = 1 + 0.18 * math.exp(-eighth / 0.06)
        fruit(c, f["fruit"] if k % 2 == 0 else "lemon", x, y, 95, rot=a * 40, scale=sc * pop(t, 8.0 + i * BEAT + 0.04 * k))
    text(c, f["name"].upper(), W / 2, 220, fit(f["name"].upper(), "black", 110, 980), rgb=GREEN)


# ---------------------------------------------------------------- 10.0 collage / line-up
def s_collage(c, t):
    if t < 10.5:
        c.clear(col(CREAM))
        spots = [(330, 560, -6), (760, 760, 5), (320, 1200, 4), (750, 1400, -5)]
        for k, (x, y, r) in enumerate(spots):
            u = out_cubic(prog(t, 10.0 + 0.06 * k, 10.18 + 0.06 * k))
            if u <= 0:
                continue
            c.save()
            c.translate(x + (1 - u) * 900, y)
            c.rotate(r)
            card = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-260, -260, 520, 520), 30, 30)
            c.drawRRect(card.makeOffset(0, 12), paint((0, 0, 0), 40))
            c.save()
            c.clipRRect(card, doAntiAlias=True)
            draw_image(c, image(ORDER[k] + ".jpg"), 0, 0, 520, 520)
            c.restore()
            c.restore()
        return
    c.clear(col(PINK))
    _bubbles(c, t, 33, 16, WHITE, 120, 400)
    text(c, "4 FLAVORS", W / 2, 470, 190, rgb=CREAM, tracking=-0.03)
    for k, key in enumerate(ORDER):
        sc = pop(t, 10.5 + 0.0625 * k, 0.35)
        if sc > 0:
            c.save()
            c.translate(W / 2 + (k - 1.5) * 250, 1500)
            c.scale(sc, sc)
            can(c, key, 0, 0, 760, rot=(k - 1.5) * 3)
            c.restore()


# ---------------------------------------------------------------- 11.0 end card
def s_end(c, t):
    c.clear(col(CREAM))
    for k, (kind, x, y, s, r) in enumerate(STICKERS[:4]):
        fruit(c, kind, x, y + 40, s * 0.8, rot=r + 8 * (t - 11), scale=pop(t, 11.0 + 0.05 * k, 0.5))
    sc = pop(t, 11.0, 0.5)
    c.save()
    c.translate(W / 2, 800)
    c.scale(sc, sc)
    draw_image(c, logo(GREEN), 0, 0, 820)
    c.restore()
    a = 255 * smooth(prog(t, 11.15, 11.35))
    text(c, "Feel-good energy, anytime.", W / 2, 1080, 66, "bold", GREEN, a=a, tracking=-0.01)
    a = 255 * smooth(prog(t, 11.3, 11.5))
    text(c, "Walmart  ·  Target  ·  Amazon", W / 2, 1190, 44, "semibold", (70, 100, 80), a=a, tracking=0)
    text(c, "wellwithall.com", W / 2, 1290, 56, "bold", PINK, a=a, tracking=0)


SCENES = [(0.0, s_burst), (2.0, s_logo), (3.0, s_feelgood), (4.0, s_photos), (6.0, s_claims), (7.0, s_break),
          (8.0, s_drop), (10.0, s_collage), (11.0, s_end)]


def punch(t):
    """Every cut lands with a quick zoom that settles (the bounce the reference has on every edit)."""
    last = max([x for x in CUTS if x <= t], default=0.0)
    return 1 + 0.045 * math.exp(-(t - last) / 0.09)


def draw_frame(t):
    surf, c = new_canvas()
    scene = [f for t0, f in SCENES if t >= t0][-1]
    z = punch(t)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    scene(c, t)
    c.restore()
    return to_rgb(surf)
