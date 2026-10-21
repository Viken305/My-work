"""Shared imports and pieces for the five parts: easing, the glass phone with its city map, glass chips and cards,
light beams and signal rings, glass bubbles (the distance spheres), counters, and the dips between parts.

A part defines draw_frame(t) -> float RGB frame (glass compositing works on the whole picture), DURATION, VO, TM,
sfx_events() and MUSIC. render.py adds post (bloom, grain, …) and motion blur.
"""
import math

import cv2
import numpy as np
import skia

import glass
from captions import Captions, VoiceEnvelope  # noqa: F401
from glass import (XX, YY, add, backdrop, blur_layer, cam, caption, caustic_light, clock, defocus, earth, ellipse,  # noqa: F401
                   fade, glass_text, glow_dot, land_path, layer, mask, mini_sat, orbit_line, orbit_points, over, rrect,
                   sat_mask, shadow, shard, Ortho)
from kit import *  # noqa: F401,F403
from project import P
from timing import Timing, schedule  # noqa: F401

SAMPLES = int(P["style"]["post"].get("samples", 1))
WORDS = set(P["words"])
MODEL = set(P["model"])


# ---------------------------------------------------------------- easing
def in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def back_out(x, s=1.6):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def lerp(a, b, u):
    return a + (b - a) * u


def pulse(t, t0, d=0.6):
    """0 -> 1 -> 0 bump around t0."""
    return math.sin(math.pi * prog(t, t0, t0 + d))


def window(t, t0, t1, fin=0.3, fout=0.3):
    """1 inside [t0, t1] with soft edges."""
    return smooth(prog(t, t0, t0 + fin)) * (1 - smooth(prog(t, t1, t1 + fout)))


# ---------------------------------------------------------------- the city map (recorded once, drawn at any zoom)
_MAP = None
MAP_ROT = -16.0


def _record_map(seed=4, R=4200):
    rng = np.random.default_rng(seed)
    rec = skia.PictureRecorder()
    c = rec.beginRecording(skia.Rect.MakeLTRB(-R, -R, R, R))
    c.drawRect(skia.Rect.MakeLTRB(-R, -R, R, R), paint((10, 22, 44)))
    xs = np.cumsum(rng.uniform(44, 78, 160)) - R
    ys = np.cumsum(rng.uniform(44, 78, 160)) - R
    xs, ys = xs[xs < R], ys[ys < R]
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            if rng.random() < 0.08:
                continue
            park = rng.random() < 0.06
            r = skia.Rect.MakeLTRB(xs[i] + 5, ys[j] + 5, xs[i + 1] - 5, ys[j + 1] - 5)
            c.drawRRect(skia.RRect.MakeRectXY(r, 4, 4), paint((22, 52, 66) if park else (20, 34, 60)))
    for k, X in enumerate(xs):
        big = k % 5 == 2
        c.drawLine(X, -R, X, R, paint((52, 74, 108) if big else (36, 54, 86), 255, stroke=10 if big else 4))
    for k, Y in enumerate(ys):
        big = k % 6 == 3
        c.drawLine(-R, Y, R, Y, paint((52, 74, 108) if big else (36, 54, 86), 255, stroke=10 if big else 4))
    # two highways and a river, readable when the map zooms out
    for a, b in (((-R, -900), (R, 300)), ((-400, -R), (700, R))):
        c.drawLine(*a, *b, paint((70, 92, 126), 255, stroke=26))
    river = skia.Path()
    river.moveTo(-R, 380)
    river.cubicTo(-900, -200, -300, 900, 300, 500)
    river.cubicTo(900, 100, 1500, 900, R, 700)
    c.drawPath(river, paint((30, 70, 120), 255, stroke=70))
    c.drawPath(river, paint(CYAN, 40, stroke=2))
    return rec.finishRecordingAsPicture()


def map_xy(p, cx, cy, zoom, pan):
    """Map coordinates -> screen, for a map centred at (cx, cy) with zoom and pan (map coords at the centre)."""
    a = math.radians(MAP_ROT)
    x, y = (p[0] - pan[0]) * zoom, (p[1] - pan[1]) * zoom
    return cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)


def phone_xy(p, cx, cy, zoom, pan, rot):
    """Map coordinates -> screen for a phone at (cx, cy) turned by rot degrees."""
    x, y = map_xy(p, cx, cy, zoom, pan)
    a = math.radians(rot)
    ox, oy = x - cx, y - cy
    return cx + ox * math.cos(a) - oy * math.sin(a), cy + ox * math.sin(a) + oy * math.cos(a)


def city_map(c, x, y, w, h, zoom=1.0, pan=(0.0, 0.0), radius=46, a=255):
    global _MAP
    if _MAP is None:
        _MAP = _record_map()
    c.save()
    c.clipRRect(rrect(x, y, w, h, radius), doAntiAlias=True)
    c.translate(x + w / 2, y + h / 2)
    c.rotate(MAP_ROT)
    c.scale(zoom, zoom)
    c.translate(-pan[0], -pan[1])
    p = skia.Paint()
    p.setAlphaf(a / 255)
    c.drawPicture(_MAP, None, p)
    c.restore()


DOT = (-60.0, 130.0)       # the blue dot (map coordinates)
PIN = (110.0, -170.0)      # the coffee shop


def coffee_pin(c, px, py, a=255, s=1.0, tag=True):
    c.drawCircle(px, py, 30 * s, paint(AMBER, a))
    c.drawCircle(px, py, 30 * s, paint(PAPER, a, stroke=3 * s))
    c.drawRRect(rrect(px - 11 * s, py - 9 * s, 20 * s, 18 * s, 4 * s), paint(INK, a))
    c.drawCircle(px + 12 * s, py, 6 * s, paint(INK, a, stroke=3 * s))
    if tag:
        label(c, "COFFEE", px, py - 48 * s, 22 * s, "mono_bold", AMBER, a, "center", 0.12)


def blue_dot(c, dx, dy, t, a=255, s=1.0, halo=True):
    if halo:
        u = (t * 0.8) % 1
        c.drawCircle(dx, dy, (40 + u * 70) * s, paint(CYAN, 70 * (1 - u) * a / 255, stroke=3))
        c.drawCircle(dx, dy, 64 * s, paint(CYAN, 40 * a / 255))
    glow_dot(c, dx, dy, 15 * s, CYAN, a, 3.2)
    c.drawCircle(dx, dy, 15 * s, paint(PAPER, a, stroke=4 * s))


def route(c, a, b, t, alpha=255):
    path = skia.Path()
    path.moveTo(*a)
    path.cubicTo(a[0] + 40, a[1] - 120, b[0] - 60, b[1] + 140, b[0], b[1] + 30)
    rp = paint(AMBER, alpha * 0.9, stroke=8)
    rp.setPathEffect(skia.DashPathEffect.Make([18, 14], -t * 60))
    c.drawPath(path, paint(AMBER, alpha * 0.27, sigma=8, stroke=16))
    c.drawPath(path, rp)


def phone(img, cx, cy, w, h, rot, t, zoom=1.0, pan=(0.0, 0.0), dot=DOT, pin=PIN, show_route=1.0, extra=None,
          screen_a=255, sheen=0.28):
    """A frosted-glass phone: a thick glass slab with rounded corners and the night map glowing inside.
    extra(c, map_to_screen, sw, sh) draws more on the screen (inside the phone's rotation)."""
    def frame(c, p):
        c.save()
        c.rotate(rot, cx, cy)
        c.drawRRect(rrect(cx - w / 2, cy - h / 2, w, h, 82 * w / 470), p)
        c.restore()
    m = mask(frame)
    shadow(img, m, 50, 80, 50, 0.6)
    glass.glass(img, m, bevel=34 * w / 470, refract=26, frost=12, tint=0.30, lift=10, rim=1.1,
                sheen=(sheen, 60, 0.12))
    inset = 24 * w / 470
    sw, sh = w - 2 * inset, h - 2 * inset
    sx, sy = cx - sw / 2, cy - sh / 2

    def screen(c):
        c.save()
        c.rotate(rot, cx, cy)
        city_map(c, sx, sy, sw, sh, zoom, pan, 46 * w / 470, screen_a)
        to = lambda p: map_xy(p, cx, cy, zoom, pan)  # noqa: E731
        c.save()
        c.clipRRect(rrect(sx, sy, sw, sh, 46 * w / 470), doAntiAlias=True)
        k = w / 470
        if show_route > 0 and dot is not None and pin is not None:
            route(c, to(dot), to(pin), t, 255 * show_route)
        if pin is not None:
            coffee_pin(c, *to(pin), 255, k)
        if dot is not None:
            blue_dot(c, *to(dot), t, 255, k)
        if extra:
            extra(c, to, sw, sh)
        c.restore()
        c.drawRRect(rrect(cx - 70 * k, sy + 22 * k, 140 * k, 40 * k, 20 * k), paint(INK, 255))     # camera island
        label(c, "9:41", sx + 48 * k, sy + 54 * k, 28 * k, "semibold", PAPER, 230)
        c.restore()
    img = over(img, layer(screen))
    gl = mask(lambda c, p: (c.save(), c.rotate(rot, cx, cy), c.drawRRect(rrect(sx, sy, sw, sh, 46 * w / 470), p),
                            c.restore()))
    band = np.exp(-(((XX - cx) * 0.8 + (YY - cy) * 0.6 + 120) / 70) ** 2)
    img += np.float32(PAPER) * (gl * band * 0.10)[..., None]
    return img


# ---------------------------------------------------------------- glass chips, cards, beams, bubbles
def chip(img, text, x, y, size=30, rgb=PAPER, a=1.0, kind="mono_bold", align="center", padx=0.7, pady=0.5,
         tracking=0.08, sub=None):
    """A small frosted-glass tag with mono text. (x, y) = text baseline anchor. Returns img."""
    if a <= 0.01:
        return img
    tw = width(text, kind, size, tracking)
    x0 = x - tw / 2 if align == "center" else x - tw if align == "right" else x
    px, py = size * padx, size * pady
    bh = size * 1.05 + 2 * py + (size * 0.9 if sub else 0)
    bw = tw + 2 * px
    if sub:
        bw = max(bw, width(sub, "mono", size * 0.6, 0.15) + 2 * px)
        x0 = min(x0, x - bw / 2 + px) if align == "center" else x0
    s = 0.9 + 0.1 * a
    bx, by = x0 - px, y - size * 0.82 - py
    m = mask(lambda c, p: c.drawRRect(rrect(bx + bw * (1 - s) / 2, by + bh * (1 - s) / 2, bw * s, bh * s,
                                            min(26, bh / 2)), p)) * a
    img = glass.glass(img, m, bevel=12, refract=8, frost=16, tint=0.45, lift=6, rim=1.0, shade=0.2)

    def draw(c):
        if rgb != PAPER:
            label(c, text, x, y, size, kind, rgb, 140 * a, align, tracking, sigma=10)
        label(c, text, x, y, size, kind, rgb, 255 * a, align, tracking)
        if sub:
            label(c, sub, bx + bw / 2, y + size * 0.95, size * 0.6, "mono", SMOKE, 255 * a, "center", 0.15)
    return over(img, layer(draw))


def card(img, x, y, w, h, a=1.0, r=30, tint=0.42, sheen=None, shade_k=0.45):
    """An empty frosted-glass card (draw on it afterwards)."""
    if a <= 0.01:
        return img
    s = 0.92 + 0.08 * a
    m = mask(lambda c, p: c.drawRRect(rrect(x + w * (1 - s) / 2, y + h * (1 - s) / 2, w * s, h * s, r), p)) * a
    shadow(img, m, 20, 40, 30, shade_k * a)
    return glass.glass(img, m, bevel=20, refract=12, frost=18, tint=tint, lift=8, rim=1.2, sheen=sheen)


def beam(c, x0, y0, x1, y1, u, rgb=CYAN, a=255, wd=3.0, head=True):
    """A light beam from (x0, y0) growing to u (0..1) of the way to (x1, y1), with a bright travelling head."""
    if u <= 0 or a <= 1:
        return
    xe, ye = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    c.drawLine(x0, y0, xe, ye, paint(rgb, a * 0.35, sigma=10, stroke=wd * 6))
    c.drawLine(x0, y0, xe, ye, paint(mix(rgb, PAPER, 0.4), a * 0.9, stroke=wd))
    if head and u < 1:
        glow_dot(c, xe, ye, wd * 3, rgb, a, 3.5)


def rings(c, x, y, t, t0, ang=None, spread=52, n=3, r0=40, r1=330, rate=0.6, rgb=CYAN, a=255, wd=5):
    """Signal rings leaving (x, y) from time t0 (as arcs toward angle `ang` in degrees, or full circles)."""
    if t < t0 or a <= 1:
        return
    for k in range(n):
        age = (t - t0) * rate - k / n
        if age < 0:
            continue
        u = age % 1
        r = r0 + u * (r1 - r0)
        al = a * (1 - u) ** 1.2
        if ang is None:
            c.drawCircle(x, y, r, paint(rgb, al, stroke=wd))
        else:
            c.drawArc(skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r), ang - spread / 2, spread, False,
                      paint(rgb, al, stroke=wd))


def bubble(img, cx, cy, r, a=1.0, rgb=CYAN):
    """A huge glass sphere (soap-bubble thin): bends what is behind it at the rim, faint tint, bright rim light."""
    if a <= 0.01 or r < 4:
        return img
    m = mask(lambda c, p: c.drawCircle(cx, cy, r, p)) * a
    img = glass.glass(img, m, bevel=min(60, r * 0.3), refract=min(22, r * 0.1), frost=2, tint=0.10, rgb=rgb, lift=3,
                      rim=0.9, shade=0.1)
    return over(img, layer(lambda c: (c.drawCircle(cx, cy, r, paint(rgb, 90 * a, sigma=8, stroke=6)),
                                      c.drawCircle(cx, cy, r, paint(mix(rgb, PAPER, 0.5), 200 * a, stroke=2)))))


def roll(value, digits, u):
    """A number rolling up to `value` (u 0..1) as text with `digits` decimals."""
    return f"{value * out_cubic(u):.{digits}f}"


def glow_text(c, s, x, y, size, kind, rgb, a=255, align="center", tracking=0.0, glow=0.55):
    label(c, s, x, y, size, kind, rgb, a * glow, align, tracking, sigma=size * 0.14)
    label(c, s, x, y, size, kind, rgb, a, align, tracking)


def tick_sound_times(t0, t1, every=1.0):
    out, t = [], t0
    while t < t1:
        out.append(t)
        t += every
    return out
