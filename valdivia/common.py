"""Shared imports and helpers for the six parts."""
import math

import numpy as np
import skia

from captions import Captions, VoiceEnvelope  # noqa: F401
from frames import (EPI, HILO, JAPAN, RUPTURE, VALDIVIA, SHADOW, _gc_point, _plume, _row, dead_tree,  # noqa: F401
                    ringing_word, tab, words_ink)
from ink import *  # noqa: F401,F403
from timing import Timing, schedule  # noqa: F401

SAMPLES = 3
QUAKE_WORDS = {"go", "crack", "tore", "shook", "9.5", "energy", "thousands", "quake", "erupted", "lurched", "earthquake"}
WATER_WORDS = {"sea", "tsunami", "pacific", "waves", "hawaii", "japan", "flooded", "drowned", "sank"}
RING_WORDS = {"ring", "bell", "rang", "vibrate", "swing", "note", "notes"}


def colours(extra=None):
    d = {**{w: RED for w in QUAKE_WORDS}, **{w: TEAL for w in WATER_WORDS}, **{w: BRONZE for w in RING_WORDS}}
    d.update(extra or {})
    return d


def in_cubic(x):
    return clamp(x) ** 3


def in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def lerp(a, b, u):
    return a + (b - a) * u


def drum_scroll(t, dur, fin=0.7, fout=0.6):
    """Vertical offset of the drawing at the part boundaries: it feeds in from below and leaves upward, like paper
    on a turning seismograph drum (the paper texture itself stays put)."""
    y = 0.0
    if fin:
        y += (1 - out_expo(prog(t, 0, fin))) * H * 0.55
    if fout:
        y -= in_cubic(prog(t, dur - fout, dur)) * H * 0.55
    return y


def fade_edges(t, dur, fin=0.5, fout=0.45):
    return min(smooth(prog(t, 0, fin)) if fin else 1.0, 1 - smooth(prog(t, dur - fout, dur)) if fout else 1.0)


def shake_env(t, t0, peak=1.0, rise=0.15, decay=3.0):
    """Shake envelope after an event at t0 (0..peak)."""
    if t < t0:
        return 0.0
    d = t - t0
    return peak * min(1.0, d / rise) * math.exp(-max(0.0, d - rise) / decay)


def polyline(pts, upto=1.0):
    """Path through a prefix (0..1 of the point count) of pts; returns (path, tip)."""
    p = skia.Path()
    n = len(pts)
    m = upto * (n - 1)
    k = int(m)
    if n < 2 or upto <= 0:
        return p, None
    p.moveTo(*pts[0])
    for i in range(1, min(k + 1, n)):
        p.lineTo(*pts[i])
    tip = pts[min(k, n - 1)]
    if k < n - 1:
        f = m - k
        tip = (pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f)
        p.lineTo(*tip)
    return p, tip


def pen_dot(c, x, y, rgb=INK, a=255):
    c.drawCircle(x, y, 6, paint(rgb, a))
    c.drawCircle(x, y, 13, paint(rgb, a * 0.35, sigma=6))


def globe(c, proj, a=1.0, land_a=1.0, outline=True, grid=True, key=None):
    """Lit paper globe with engraved land."""
    cx, cy, R = proj.cx, proj.cy, proj.R
    disc = skia.Path()
    disc.addCircle(cx, cy, R)
    c.drawCircle(cx + 10, cy + 26, R, paint(SHADOW, 60 * a, sigma=30))
    sh = skia.GradientShader.MakeRadial((cx - R * 0.4, cy - R * 0.45), R * 1.7,
                                        [col(WHITE, 255 * a), col(BONE, 255 * a), col(SHADE, 255 * a)], [0, 0.55, 1])
    c.drawCircle(cx, cy, R, skia.Paint(AntiAlias=True, Shader=sh))
    if land_a > 0.01:
        c.save()
        c.clipPath(disc, doAntiAlias=True)
        if grid:
            graticule(c, proj, 0.9 * land_a * a, 15)
        engraved_land(c, globe_land_path(proj, ss=1 if key is None else 2), land_a * a, step=5.5,
                      water_lines=(5, 11), key=key or ("globe", round(proj.l0, 4), round(proj.p0, 4), round(R, 1)))
        c.restore()
    if outline:
        ink(c, disc, INK, 240 * a, 2.2)


def mode_outline(cx, cy, R, eps, tilt=-22.0, breathe=0.0, n=240):
    """Outline of the globe deformed in the slowest 'football' mode (eps) plus the breathing mode (breathe)."""
    tl = math.radians(tilt)
    p = skia.Path()
    for k in range(n + 1):
        th = 2 * math.pi * k / n
        x = math.cos(th - tl)
        r = R * (1 + breathe + eps * (3 * x * x - 1) / 2)
        (p.lineTo if k else p.moveTo)(cx + math.cos(th) * r, cy + math.sin(th) * r)
    p.close()
    return p


def dial_rings(c, cx, cy, R, a=1.0, phase=0.0):
    """Faint bronze echo rings with instrument ticks around the ringing globe; phase pushes them outward."""
    for k in range(3):
        rr = R * (1.2 + 0.17 * ((k + phase) % 3))
        fa = a * (1 - ((k + phase) % 3) / 3)
        q = skia.Path()
        q.addCircle(cx, cy, rr)
        c.drawPath(q, paint(BRONZE, 120 * fa, stroke=1.5))
        for j in range(72):
            ang = math.radians(j * 5)
            l = 10 if j % 6 == 0 else 4
            c.drawLine(cx + math.cos(ang) * rr, cy + math.sin(ang) * rr, cx + math.cos(ang) * (rr + l),
                       cy + math.sin(ang) * (rr + l), paint(BRONZE, 90 * fa, stroke=1.0))


def ring_word(c, s, x, y, size, rgb=BRONZE, a=1.0, strike=0.0, kind="serif_bold"):
    """A word that rings: echo outlines expand out of it after a strike (strike = seconds since the strike)."""
    if a <= 0.01:
        return
    f = font(kind, size)
    w = width(s, kind, size)
    cx, cy = x + w / 2, y - size * 0.34
    for k in range(4):
        ph = (strike * 1.1 + k / 4) % 1.0 if strike > 0 else (k + 1) / 5
        sc = 1 + 0.22 * ph
        fa = (1 - ph) * a * (0.6 if strike > 0 else 0.35)
        c.save()
        c.translate(cx, cy)
        c.scale(sc, sc)
        c.translate(-cx, -cy)
        p = paint(rgb, 255 * fa, stroke=1.4)
        xx = x
        for ch in s:
            c.drawString(ch, xx, y, f, p)
            xx += f.measureText(ch)
        c.restore()
    xx = x
    for ch in s:
        c.drawString(ch, xx + 2, y + 5, f, paint(SHADOW, 60 * a, sigma=6))
        c.drawString(ch, xx, y, f, paint(rgb, 255 * a))
        xx += f.measureText(ch)


def counter_text(v, fmt="{:,.0f}"):
    return fmt.format(v)


def big_label(c, text, x, y, size, rgb=INK, a=1.0, align="center", kind="black", tracking=0.0):
    if a <= 0.01:
        return
    w = width(text, kind, size, tracking)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    label(c, text, x0 + 3, y + 6, size, kind, SHADOW, 50 * a, "left", tracking, sigma=7)
    label(c, text, x0, y, size, kind, rgb, 255 * a, "left", tracking)


def pop(t, t0, d=0.45):
    """0..1 with a slight overshoot, for things that land."""
    return spring(prog(t, t0, t0 + d), 7, 9) if t >= t0 else 0.0


def appear(t, t0, d=0.35):
    return smooth(prog(t, t0, t0 + d))
