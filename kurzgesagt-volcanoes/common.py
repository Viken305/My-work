"""Helpers for the volcano video: narration timing, fades, captions, crystals/icons (from the minerals kit)
and the new volcano pieces: cones, lava, ash plumes, the magma blob character, the cut-away Earth."""
import json, math, os

import numpy as np

from engine import *  # noqa: F401,F403
from script import PARTS

DARK = (8, 8, 24)
LAVA = (255, 110, 40)
LAVA_HOT = (255, 200, 80)
ASH = (120, 112, 140)
ROCK = (78, 62, 118)
CRUST_C = (96, 78, 140)
MANTLE_C = (200, 70, 50)
OCEAN = (40, 96, 210)
OX = (255, 92, 92)       # oxygen atom


class Timing:
    """Start/end of narration lines, plus an estimate of when a given word is spoken."""

    def __init__(self, part, vo):
        self.vo, self.text = vo, dict(PARTS[part])
        path = os.path.join(HERE, "build", part, "vo", "durations.json")
        self.dur = json.load(open(path)) if os.path.exists(path) else {k: len(v) / 15.0 for k, v in self.text.items()}

    def start(self, k):
        return self.vo[k]

    def end(self, k):
        return self.vo[k] + self.dur[k]

    def word(self, k, w):
        s = self.text[k].lower()
        i = s.find(w.lower())
        assert i >= 0, (k, w)
        return self.vo[k] + 0.12 + (i / len(s)) * (self.dur[k] - 0.25)


# ---------------------------------------------------------------- layout helpers
def chapter_fade(c, t, duration, fade_in=0.4, fade_out=0.45):
    a = max(1 - smooth(prog(t, 0, fade_in)), smooth(prog(t, duration - fade_out, duration)))
    if a > 0:
        c.drawPaint(fill(DARK, 255 * a))


def cam(c, z, fx, fy):
    """Camera: zoom z around world point (fx, fy) placed at screen centre. Caller restores."""
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-fx, -fy)


def scenes(c, t, lst):
    """lst: [((t0, t1), t_end, fn)] -> draw each active scene, fading in over [t0, t1]."""
    for (t0, t1), t_end, fn in lst:
        if t0 <= t < t_end:
            a = smooth(prog(t, t0, t1))
            if a < 1:
                c.saveLayerAlpha(None, int(255 * a))
            fn(c, t)
            if a < 1:
                c.restore()


def caption(c, s, x, y, rgb=WHITE, size=30, a=255):
    if a <= 2:
        return
    w = font(size, 800).measureText(s) + size * 0.08 * (len(s) - 1) + size * 1.4
    c.drawRRect(rrect(x - w / 2, y - size * 1.05, w, size * 1.6, size * 0.8), fill((12, 10, 34), 200 * a / 255))
    text(c, s, x, y, size, rgb, a, 800, spacing=size * 0.08)


def pill_tag(c, x, y, label, rgb, g=1.0, size=28, down=True):
    if g <= 0.01:
        return
    c.save()
    c.translate(x, y)
    c.scale(g, g)
    w = font(size, 800).measureText(label) + size * 0.07 * (len(label) - 1) + size * 1.5
    c.drawRRect(rrect(-w / 2, -size, w, size * 1.8, size * 0.9), fill(rgb))
    if down:
        c.drawPath(poly([(-10, size * 0.78), (10, size * 0.78), (0, size * 1.35)]), fill(rgb))
    text(c, label, 0, size * 0.36, size, INK, 255, 800, spacing=size * 0.07)
    c.restore()


def bubble_q(c, x, y, g, mark="?"):
    if g <= 0.01:
        return
    c.save()
    c.translate(x, y)
    c.scale(g, g)
    c.drawRRect(rrect(-48, -54, 96, 96, 30), fill(WHITE))
    c.drawPath(poly([(10, 38), (40, 38), (46, 70)]), fill(WHITE))
    text(c, mark, 0, 16, 64, INK, 255, 800)
    c.restore()


def circle_path(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def wavy_band(c, y0, y1, rgb, seed, amp=18, a=255):
    rng = np.random.default_rng(seed)
    ph, f = rng.uniform(0, 6.28), rng.uniform(1.5, 3.0)
    p = skia.Path()
    p.moveTo(-10, y1 + 400)
    for x in range(-10, W + 30, 30):
        p.lineTo(x, y0 + amp * math.sin(x / W * f * 6.28 + ph) + amp * 0.4 * math.sin(x / 90 + ph * 2))
    p.lineTo(W + 30, y1 + 400)
    p.close()
    c.drawPath(p, fill(rgb, a))


def card(c, cx, cy, w, h, tint, label, sub, draw_fn, t, a=1.0):
    """Rounded info card with a clipped illustration and a label."""
    if a <= 0.01:
        return
    c.saveLayerAlpha(None, int(255 * a))
    rr = rrect(cx - w / 2, cy - h / 2, w, h, 32)
    c.save()
    c.translate(14, 24)
    c.drawRRect(rr, blur(fill((5, 4, 20), 120), 26))
    c.restore()
    c.drawRRect(rr, shaded(linear((cx, cy - h / 2), (cx, cy + h / 2), [mix(NAVY, tint, 0.14), mix(PURPLE, tint, 0.05)])))
    c.save()
    c.clipRRect(rr, doAntiAlias=True)
    glow(c, cx, cy - h * 0.12, w * 0.6, tint, 45)
    c.save()
    c.translate(cx, cy - 50)
    draw_fn(c, t)
    c.restore()
    c.restore()
    c.drawRRect(rr, stroke(tint, 3, 90))
    text(c, label, cx, cy + h / 2 - 74, 34, WHITE, 255, 800, spacing=3)
    if sub:
        text(c, sub, cx, cy + h / 2 - 38, 22, tint, 230, 600, spacing=2)
    c.restore()


def number_badge(c, x, y, n, rgb, g=1.0, r=46):
    if g <= 0.01:
        return
    c.save()
    c.translate(x, y)
    c.scale(g, g)
    glow(c, 0, 0, r * 2.2, rgb, 90)
    c.drawCircle(0, 0, r, fill(rgb))
    c.drawCircle(0, 0, r, stroke(WHITE, 5, 220))
    text(c, str(n), 0, r * 0.4, r * 1.1, INK, 255, 800)
    c.restore()


def thermometer(c, x, y, level, tc, label=None, h=360):
    c.drawRRect(rrect(x - 22, y, 44, h, 22), fill(WHITE, 230))
    c.drawCircle(x, y + h + 30, 44, fill(WHITE, 230))
    c.drawRRect(rrect(x - 12, y + h * (1 - level), 24, h * level + 20, 12), fill(tc))
    c.drawCircle(x, y + h + 30, 32, fill(tc))
    if label:
        text(c, label, x + 54, y + h * (1 - level) + 12, 34, WHITE, 255, 800, "left")


# ---------------------------------------------------------------- crystals / icons (from the minerals kit)
def prism(c, x, y, L, w, ang, rgb, a=255, tip=0.55, both=False, glow_a=0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    tl = w * tip * 2
    if glow_a:
        c.drawRRect(rrect(-w, -w * 2, L + 2 * w, w * 4, w * 2), blur(fill(rgb, glow_a), w * 1.5))
    if both:
        top = [(tl, -w), (L - tl, -w), (L, 0), (0, 0)]
        bot = [(0, 0), (L, 0), (L - tl, w), (tl, w)]
    else:
        top = [(0, -w), (L - tl, -w), (L, 0), (0, 0)]
        bot = [(0, 0), (L, 0), (L - tl, w), (0, w)]
    c.drawPath(poly(top), fill(lighten(rgb, 0.45), a))
    c.drawPath(poly(bot), fill(darken(rgb, 0.12), a))
    outline = poly(top[:3] + bot[2:] + ([(0, 0)] if both else [(0, w), (0, -w)]))
    c.drawPath(outline, stroke(lighten(rgb, 0.7), max(1.2, w * 0.06), 0.8 * a))
    c.restore()


def icon_up(c, x, y, s):
    c.drawPath(poly([(x - s * 0.35, y + s), (x + s * 0.35, y + s), (x + s * 0.35, y), (x + s * 0.8, y),
                     (x, y - s), (x - s * 0.8, y), (x - s * 0.35, y)]), fill(INK))


def icon_drop(c, x, y, s):
    p = skia.Path()
    p.moveTo(x, y - s * 1.1)
    p.cubicTo(x + s * 0.4, y - s * 0.5, x + s * 0.85, y, x + s * 0.85, y + s * 0.3)
    p.cubicTo(x + s * 0.85, y + s * 1.1, x - s * 0.85, y + s * 1.1, x - s * 0.85, y + s * 0.3)
    p.cubicTo(x - s * 0.85, y, x - s * 0.4, y - s * 0.5, x, y - s * 1.1)
    c.drawPath(p, fill(INK))


def icon_flame(c, x, y, s):
    p = skia.Path()
    p.moveTo(x, y - s * 1.1)
    p.cubicTo(x + s * 0.9, y - s * 0.2, x + s * 0.8, y + s * 0.9, x, y + s * 0.9)
    p.cubicTo(x - s * 0.8, y + s * 0.9, x - s * 0.9, y - s * 0.1, x - s * 0.2, y - s * 0.5)
    p.cubicTo(x - s * 0.1, y - s * 0.1, x + s * 0.1, y - s * 0.5, x, y - s * 1.1)
    c.drawPath(p, fill(INK))


def water_drop(c, x, y, s, a=255):
    p = skia.Path()
    p.moveTo(x, y - s * 1.3)
    p.cubicTo(x + s * 0.5, y - s * 0.6, x + s, y, x + s, y + s * 0.3)
    p.cubicTo(x + s, y + s * 1.2, x - s, y + s * 1.2, x - s, y + s * 0.3)
    p.cubicTo(x - s, y, x - s * 0.5, y - s * 0.6, x, y - s * 1.3)
    c.drawPath(p, fill(CYAN, a))
    c.drawCircle(x - s * 0.35, y + s * 0.3, s * 0.22, fill(WHITE, 0.8 * a))


# ---------------------------------------------------------------- volcano pieces
def volcano(c, x, base, w, h, rgb=ROCK, crater=0.16, t=0.0, hot=0.0, snow=False):
    """Cone with curved flanks, a shaded right side and a crater. Returns crater-top (x, y)."""
    top_w = w * crater
    p = skia.Path()
    p.moveTo(x - w / 2, base)
    p.cubicTo(x - w * 0.28, base - h * 0.35, x - top_w * 0.9, base - h * 0.85, x - top_w / 2, base - h)
    p.lineTo(x + top_w / 2, base - h)
    p.cubicTo(x + top_w * 0.9, base - h * 0.85, x + w * 0.28, base - h * 0.35, x + w / 2, base)
    p.close()
    c.drawPath(p, shaded(linear((x - w / 2, 0), (x + w / 2, 0), [lighten(rgb, 0.15), rgb, darken(rgb, 0.3)], [0, 0.5, 1])))
    if snow:  # jagged snow cap, clipped to the cone
        c.save()
        c.clipPath(p, doAntiAlias=True)
        sp = [(x - w, base - h - 10)] + [(x - w / 2 + k * w / 12, base - h * (0.74 if k % 2 else 0.8)) for k in range(13)] + [(x + w, base - h - 10)]
        c.drawPath(poly(sp), fill((240, 236, 250)))
        c.restore()
    c.drawOval(skia.Rect.MakeXYWH(x - top_w / 2, base - h - top_w * 0.12, top_w, top_w * 0.24), fill(mix(darken(rgb, 0.4), LAVA, hot)))
    if hot > 0:
        glow(c, x, base - h, top_w * 1.6, LAVA, 160 * hot)
    return x, base - h


class Plume:
    """Billowing ash column: puffs rise, spread and cool from orange to grey."""

    def __init__(self, seed=1, n=34):
        rng = np.random.default_rng(seed)
        self.ph = rng.uniform(0, 1, n)
        self.dx = rng.uniform(-1, 1, n)
        self.r = rng.uniform(0.6, 1.2, n)

    def draw(self, c, x, y, t, height=600, width=160, k=1.0, speed=0.18, a=1.0):
        """k scales how far up the column has grown (0..1)."""
        if k <= 0.01:
            return
        for i in np.argsort(self.ph):
            u = (self.ph[i] + t * speed) % 1.0
            if u > k:
                continue
            spread = 0.35 + 1.4 * u ** 1.6
            px = x + self.dx[i] * width * spread * 0.6 + 30 * math.sin(t * 0.7 + i)
            py = y - height * u
            r = width * 0.45 * self.r[i] * (0.5 + spread)
            col_ = mix(LAVA, ASH, min(1.0, u * 4)) if u < 0.25 else mix(ASH, (170, 162, 188), (u - 0.25) / 0.75)
            c.drawCircle(px, py, r, fill(col_, 235 * a * min(1.0, (k - u) * 8 + 0.2)))
            c.drawCircle(px - r * 0.3, py - r * 0.3, r * 0.5, fill(WHITE, 30 * a))


def lava_flow(c, pts, k, width=22, t=0.0):
    """Glowing lava river along a polyline, revealed up to fraction k."""
    if k <= 0.01:
        return
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    target, acc = sum(L) * clamp(k), 0.0
    p = skia.Path()
    p.moveTo(*pts[0])
    for i, l in enumerate(L):
        if acc + l >= target:
            u = (target - acc) / l if l else 0
            p.lineTo(lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u))
            break
        p.lineTo(*pts[i + 1])
        acc += l
    c.drawPath(p, blur(stroke(LAVA, width * 2.2, 120), width * 0.8))
    c.drawPath(p, stroke(LAVA, width, 255))
    c.drawPath(p, stroke(LAVA_HOT, width * 0.4, 230))


def magma_blob(c, x, y, r, t, look=(0.0, -1.0), phase=0.0, a=255, face=True):
    """The magma character: a wobbly glowing blob with dot eyes."""
    if r <= 0.5 or a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    glow(c, x, y, r * 2.2, LAVA, 120)
    radii = [r * (1 + 0.08 * math.sin(t * 3 + k * 1.7 + phase)) for k in range(9)]
    p = blob_path(x, y, radii, t * 0.2)
    c.drawPath(p, shaded(radial((x - r * 0.3, y - r * 0.4), r * 1.6, [LAVA_HOT, LAVA, (210, 60, 30)], [0, 0.5, 1])))
    c.drawCircle(x - r * 0.3, y - r * 0.35, r * 0.28, fill(WHITE, 60))
    if face and r > 8:
        eyes(c, x, y, r, t, look, phase)
    if a < 255:
        c.restore()


# ---------------------------------------------------------------- globe + cut-away Earth
def _blobs(seed, specs):
    rng = np.random.default_rng(seed)
    out = []
    for (lon, lat, rad) in specs:
        n = 26
        radii = rad * (0.75 + 0.5 * rng.random(n))
        radii = np.convolve(np.r_[radii[-2:], radii, radii[:2]], np.ones(5) / 5, "valid")
        out.append([(lon + radii[k] * math.cos(2 * math.pi * k / n) * 1.3, lat + radii[k] * math.sin(2 * math.pi * k / n)) for k in range(n)])
    return out


CONTINENTS = _blobs(21, [(-100, 45, 32), (-60, -15, 26), (15, 45, 22), (20, 5, 28), (90, 45, 36), (135, -25, 18), (-40, 72, 14), (70, 20, 14)])


def ortho(lon, lat, rot, R, tilt=0.0):
    lo, la = math.radians(lon + rot), math.radians(lat)
    x, y, z = R * math.cos(la) * math.sin(lo), -R * math.sin(la), math.cos(la) * math.cos(lo)
    if z < 0:
        d = math.hypot(x, y) or 1.0
        x, y = x / d * R, y / d * R
    return x, y, z


def draw_globe(c, cx, cy, R, rot, a=1.0, land=(88, 205, 135), night=190, continents=CONTINENTS):
    if R < 1 or a <= 0.01:
        return
    c.saveLayerAlpha(None, int(255 * a))
    glow(c, cx, cy, R * 1.35, CYAN, 90)
    c.save()
    c.translate(cx, cy)
    c.rotate(-18)
    disc = circle_path(0, 0, R)
    c.drawPath(disc, shaded(radial((-R * 0.35, -R * 0.4), R * 1.5, [(70, 150, 255), (40, 96, 220), (24, 50, 140)], [0, 0.55, 1])))
    c.save()
    c.clipPath(disc, doAntiAlias=True)
    for blob in continents:
        pts = [ortho(lo, la, rot, R) for lo, la in blob]
        if max(p[2] for p in pts) <= 0:
            continue
        path = smooth_closed([(p[0], p[1]) for p in pts])
        c.drawPath(path, fill(land))
        c.drawPath(path, stroke(lighten(land, 0.3), max(1.0, R * 0.008), 120))
    c.drawOval(skia.Rect.MakeXYWH(-R * 0.5, -R * 1.05, R, R * 0.22), fill((240, 248, 255)))
    c.drawOval(skia.Rect.MakeXYWH(-R * 0.55, R * 0.86, R * 1.1, R * 0.2), fill((240, 248, 255)))
    c.drawPath(disc, shaded(linear((-R * 0.6, -R * 0.6), (R * 0.9, R * 0.9), [((10, 8, 40), 0), ((10, 8, 40), 0), ((10, 8, 40), night)], [0, 0.45, 1])))
    c.restore()
    c.drawPath(disc, stroke((150, 220, 255), max(1.5, R * 0.012), 160))
    c.restore()
    c.restore()


def globe_point(cx, cy, R, lon, lat, rot):
    """Screen position of a lon/lat on draw_globe (matches its -18 deg tilt). Returns (x, y, z)."""
    x, y, z = ortho(lon, lat, rot, R)
    a = math.radians(-18)
    return cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a), z


LAYERS = [(1.0, CRUST_C, "CRUST"), (0.985, MANTLE_C, "MANTLE"), (0.55, (255, 150, 60), "OUTER CORE"), (0.2, (255, 235, 170), "INNER CORE")]


def earth_cutaway(c, cx, cy, R, t, wedge, rot=0.0):
    """Globe with a quarter-wedge cut out showing the layers (wedge 0..1 opens the cut)."""
    draw_globe(c, cx, cy, R, rot)
    if wedge <= 0.01:
        return
    sweep = 90 * wedge
    for frac, rgb, _ in LAYERS:
        r = R * frac
        p = skia.Path()
        p.moveTo(cx, cy)
        p.arcTo(skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r), -90, sweep, False)
        p.close()
        if frac < 0.6:
            c.drawPath(p, shaded(radial((cx, cy), r, [lighten(rgb, 0.3), rgb])))
        else:
            c.drawPath(p, shaded(radial((cx, cy), r, [lighten(rgb, 0.15), rgb, darken(rgb, 0.15)], [0, 0.85, 1])))
    glow(c, cx, cy, R * 0.35 * wedge, (255, 240, 200), 200)
    c.drawLine(cx, cy, cx, cy - R, stroke(WHITE, 3, 160))
    a = math.radians(-90 + sweep)
    c.drawLine(cx, cy, cx + R * math.cos(a), cy + R * math.sin(a), stroke(WHITE, 3, 160))
