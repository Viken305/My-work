"""Shared helpers for the exercise style tests (paints, paths, easing, poster text, a 5x7 LED font)."""
import math

import numpy as np
import skia

from engine import FPS, H, W, clamp, in_cubic, in_out, lerp, mix, out_back, out_cubic, out_expo, prog, smooth  # noqa: F401
from engine import blur, linear, radial, rrect, shaded  # noqa: F401
from premium import add, light  # noqa: F401
from timing import Timing, schedule  # noqa: F401
from typo import Captions, Counter, font, label, paint, reveal, spring, width  # noqa: F401

PREMIUM, SAMPLES = True, 4


def fillp(rgb, a=255):
    return skia.Paint(AntiAlias=True, Color=skia.Color(*[int(x) for x in rgb], int(clamp(a / 255) * 255)))


def stroke(rgb, w, a=255, plus=False, cap=skia.Paint.kRound_Cap):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=cap,
                   StrokeJoin=skia.Paint.kRound_Join, Color=skia.Color(*[int(x) for x in rgb], int(clamp(a / 255) * 255)))
    if plus:
        p.setBlendMode(skia.BlendMode.kPlus)
    return p


def grad_v(y0, y1, c0, c1, a0=255, a1=255):
    return skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, y0), (0, y1)], [skia.Color(*[int(x) for x in c0], int(a0)), skia.Color(*[int(x) for x in c1], int(a1))]))


def path_of(pts, closed=False):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def hsh(*a):
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return (h % 100003) / 100003.0


def shake(t, t0, amp=18.0, decay=6.0):
    if t < t0:
        return 0.0, 0.0
    k = amp * math.exp(-(t - t0) * decay)
    return k * math.sin(t * 71), k * math.cos(t * 53)


def outlined(c, s, x, y, size, kind, rgb, a=255, align="center", ow=0.12, glow_rgb=None, tracking=0.0, outline_rgb=(8, 6, 16)):
    """Poster text: glow, drop shadow, thick outline, fill."""
    if a <= 1:
        return
    f = font(kind, size)
    w = width(s, kind, size, tracking)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x

    def run(p, dx=0.0, dy=0.0):
        cx = x0
        for ch in s:
            c.drawString(ch, cx + dx, y + dy, f, p)
            cx += f.measureText(ch) + tracking * size
    if glow_rgb:
        run(paint(glow_rgb, 150 * a / 255, size * 0.12))
    run(paint((0, 0, 0), 190 * a / 255, size * 0.05), 0, size * 0.05)
    op = paint(outline_rgb, a)
    op.setStyle(skia.Paint.kStroke_Style)
    op.setStrokeWidth(size * ow)
    op.setStrokeJoin(skia.Paint.kRound_Join)
    run(op)
    run(paint(rgb, a))


# ---------------------------------------------------------------- 5x7 LED font (rows top to bottom, 5 bits each)
LED = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 10001 11001 10101 10011 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11111 00010 00100 00010 00001 10001 01110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    ",": "00000 00000 00000 00000 00110 00100 01000", ".": "00000 00000 00000 00000 00000 01100 01100",
    "?": "01110 10001 00001 00010 00100 00000 00100", "!": "00100 00100 00100 00100 00100 00000 00100",
    "'": "00100 00100 01000 00000 00000 00000 00000", "-": "00000 00000 00000 11111 00000 00000 00000",
    "%": "11000 11001 00010 00100 01000 10011 00011", ">": "10000 01000 00100 00010 00100 01000 10000",
    "/": "00001 00010 00010 00100 01000 01000 10000", " ": "00000 00000 00000 00000 00000 00000 00000",
    "×": "00000 10001 01010 00100 01010 10001 00000",
}


def led_text(c, s, x, y, pitch, lit, on_rgb, off_rgb=(40, 26, 10), glow=True):
    """Dot-matrix text. lit(i) -> 0..1 brightness for character i. Returns width."""
    r = pitch * 0.36
    for i, ch in enumerate(s):
        rows = LED.get(ch.upper(), LED["?"]).split()
        k = lit(i)
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                px, py = x + (i * 6 + rx) * pitch, y + ry * pitch
                if bit == "1" and k > 0.01:
                    c.drawCircle(px, py, r, fillp(mix(off_rgb, on_rgb, k)))
                    if glow:
                        c.drawCircle(px, py, r * 2.6, fillp(on_rgb, 40 * k))
                else:
                    c.drawCircle(px, py, r * 0.8, fillp(off_rgb, 255))
    return len(s) * 6 * pitch


def style_tag(c, t, txt, dur):
    """Label for the style reel: which test this is (fades in and out)."""
    a = 255 * smooth(prog(t, 0.2, 0.5)) * (1 - smooth(prog(t, dur - 0.5, dur - 0.2)))
    if a <= 1:
        return
    tw = width(txt, "mono_bold", 30, 0.12)
    c.drawRRect(rrect(540 - tw / 2 - 30, 1690, tw + 60, 64, 32), fillp((0, 0, 0), 0.7 * a))
    label(c, txt, 540, 1733, 30, "mono_bold", (255, 255, 255), a, "center", tracking=0.12)
