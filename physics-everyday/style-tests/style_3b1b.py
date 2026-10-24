"""Style A: 3Blue1Brown-style. Dark canvas, precise glowing curves, LaTeX-like serif maths.

Beat: a wave enters the oven, bounces off the far wall, the two add up to a standing wave,
and sin^2(kx) becomes a strip of hot and cold spots half a wavelength (about 6 cm) apart.
"""
import math

from kit import (W, H, blur, clamp, draw_runs, fill, hexc, in_out, lerp, mix, out_cubic, polyline, prog, smooth,
                 stroke, text, trim, runs_width)

DURATION = 12.0

BG = hexc("0E1014")
INK = hexc("ECECEC")
GREY = hexc("6B6F78")
BLUE = hexc("58C4DD")
YELLOW = hexc("F4D35E")
RED = hexc("FC6255")
PALETTE = [("Background", BG), ("Ink", INK), ("Wave / sin", BLUE), ("Echo / cos", YELLOW), ("Heat", RED), ("Guide", GREY)]
FONTS_USED = [("cm", "Computer Modern (LaTeX serif)")]

# oven cavity, in pixels
X0, X1 = 260, 1660
L = X1 - X0
CY = 470
LAM = L / 3            # three wavelengths fit: walls are nodes
K = 2 * math.pi / LAM
OMEGA = 2 * math.pi / 1.1
A = 56


def wave_path(f, a=None, b=None):
    a = X0 if a is None else a
    b = X1 if b is None else b
    if b - a < 2:
        return None
    n = max(2, int((b - a) / 3))
    return polyline([(a + (b - a) * i / n, CY - f(a + (b - a) * i / n - X0)) for i in range(n + 1)])


def glow_stroke(c, path, rgb, w, a=255):
    if path is None:
        return
    c.drawPath(path, blur(stroke(rgb, w * 4, a * 0.22), w * 2.2))
    c.drawPath(path, stroke(rgb, w, a))


def draw(c, t):
    c.clear(fill(BG).getColor())

    # ---- title: written in, then lifts to the top
    up = in_out(prog(t, 1.6, 2.4))
    size = lerp(76, 50, up)
    y = lerp(H / 2 + 20, 120, up)
    title = [("Why does a microwave heat ", "cm", INK, False), ("unevenly", "cm_it", YELLOW, False), ("?", "cm", INK, False)]
    draw_runs(c, title, W / 2, y, size, reveal=prog(t, 0.1, 1.4))

    # ---- the cavity draws itself
    d = out_cubic(prog(t, 2.2, 3.2))
    if d > 0:
        top, bot = CY - 170, CY + 170
        for path in (polyline([(X0, top), (X0, bot)]), polyline([(X1, top), (X1, bot)])):
            c.drawPath(trim(path, d), stroke(INK, 6))
        for yy in (top, bot):
            c.drawPath(trim(polyline([(X0, yy), (X1, yy)]), d), stroke(GREY, 2, 160))
        c.drawPath(trim(polyline([(X0, CY), (X1, CY)]), d), stroke(GREY, 1.5, 90))
        wa = 255 * prog(t, 2.8, 3.3) * (1 - prog(t, 8.2, 8.6))
        text(c, "metal wall", X0, bot + 44, "cm_it", 30, GREY, wa)
        text(c, "metal wall", X1, bot + 44, "cm_it", 30, GREY, wa)

    # ---- travelling wave in (blue), echo back (yellow)
    tw = t - 3.0
    front = X0 + L * smooth(prog(t, 3.0, 4.3))
    back = X1 - L * smooth(prog(t, 4.3, 5.6))
    sum_a = smooth(prog(t, 5.4, 6.3))
    parts_a = 255 * (1 - 0.75 * sum_a) * (1 - smooth(prog(t, 7.8, 8.6)))
    if t > 3.0:
        inc = wave_path(lambda x: A * math.sin(K * x - OMEGA * tw), X0, front)
        glow_stroke(c, inc, BLUE, 4, parts_a)
    if t > 4.3:
        ref = wave_path(lambda x: A * math.sin(K * x + OMEGA * tw), back, X1)
        glow_stroke(c, ref, YELLOW, 4, parts_a)
    if 3.2 < t < 6.0:
        a = 255 * prog(t, 3.2, 3.6) * (1 - prog(t, 5.0, 5.4))
        label = "the wave goes in" if t < 4.6 else "...and bounces back"
        text(c, label, W / 2, CY - 210, "cm_it", 34, BLUE if t < 4.6 else YELLOW, a)

    # ---- they add up: a standing wave
    if sum_a > 0:
        st = wave_path(lambda x: 2 * A * math.sin(K * x) * math.cos(OMEGA * tw))
        glow_stroke(c, st, INK, 5, 255 * sum_a)
        a = 255 * prog(t, 5.7, 6.1) * (1 - prog(t, 7.6, 8.0))
        text(c, "together they make a standing wave", W / 2, CY - 210, "cm_it", 34, INK, a)

    # nodes: points that never move
    nd = prog(t, 7.0, 7.8)
    if nd > 0:
        for i in range(7):
            x = X0 + i * LAM / 2
            r = 9 * out_cubic(clamp(nd * 7 - i))
            if r > 0.5:
                c.drawCircle(x, CY, r * 2.2, blur(fill(BLUE, 70), 8))
                c.drawCircle(x, CY, r, fill(BLUE))

    # ---- equation
    eq_move = in_out(prog(t, 8.2, 9.0))
    eq_y = lerp(760, 1000, eq_move)
    eq_size = lerp(56, 44, eq_move)
    eq = [("E", "cm_it", INK, False), ("(", "cm", INK, False), ("x", "cm_it", INK, False), (", ", "cm", INK, False),
          ("t", "cm_it", INK, False), (")  =  2", "cm", INK, False), ("E", "cm_it", INK, False), ("0", "cm", INK, True),
          ("  sin(", "cm", BLUE, False), ("kx", "cm_it", BLUE, False), (")", "cm", BLUE, False),
          ("  cos(", "cm", YELLOW, False), ("ωt", "cm_it", YELLOW, False), (")", "cm", YELLOW, False)]
    if t > 6.0:
        draw_runs(c, eq, W / 2, eq_y, eq_size, reveal=prog(t, 6.0, 7.0))

    # ---- heat strip: brightness of heating ~ sin^2(kx)
    hs = prog(t, 8.6, 9.8)
    if hs > 0:
        sy0, sy1 = 712, 760
        xe = X0 + L * in_out(hs)
        step = 4
        x = X0
        while x < xe:
            h = math.sin(K * (x - X0)) ** 2
            c.drawRect(skia_rect(x, sy0, step + 0.6, sy1 - sy0), fill(mix(hexc("1C3A5E"), RED, h ** 1.4)))
            x += step
        c.drawRect(skia_rect(X0, sy0, L, sy1 - sy0), stroke(GREY, 1.5, 140))
        la = 255 * prog(t, 9.6, 10.1)
        for i in range(6):
            text(c, "hot", X0 + LAM / 4 + i * LAM / 2, sy0 - 14, "cm_it", 28, RED, la)
        text(c, "cold", X0 + LAM / 2, sy1 + 36, "cm_it", 28, BLUE, la)
        text(c, "cold", X0 + LAM * 1.5, sy1 + 36, "cm_it", 28, BLUE, la)

        # brace between two hot spots: lambda/2
        br = out_cubic(prog(t, 10.0, 10.8))
        if br > 0:
            xa, xb = X0 + LAM * 1.75, X0 + LAM * 2.25
            yb = sy1 + 28
            m = (xa + xb) / 2
            bp = polyline([(xa, yb), (xa + 8, yb + 14), (m - 10, yb + 14), (m, yb + 26),
                           (m + 10, yb + 14), (xb - 8, yb + 14), (xb, yb)])
            c.drawPath(trim(bp, br), stroke(INK, 3))
            draw_runs(c, [("λ", "cm_it", INK, False), ("/2  ", "cm", INK, False), ("≈", "sym", INK, False),
                          ("  6 cm", "cm", INK, False)],
                      m, yb + 76, 38, reveal=prog(t, 10.4, 11.2))

    text(c, "The Physics of Everyday Things", W - 60, H - 40, "cm_it", 24, GREY, 200 * prog(t, 11.0, 11.6), align="right")


def skia_rect(x, y, w, h):
    import skia
    return skia.Rect.MakeXYWH(x, y, w, h)
