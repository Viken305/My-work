"""WHY BORDERS ARE SHAPED THE WAY THEY ARE: the whole Short on one timeline (Paper Atlas style).

Shots come from shots.py (cut times from the real narration). Each shot draws inside the map card; the page around it
(section tag, serif headline, caption, card frame) is shared. Cuts inside a section are quick dissolves; the headline
slides when it changes. The last half-second blends into frame 0, so the Short loops.
"""
import math, os, re

import numpy as np
import skia

import geo
import shots
import timing
from atlas import (BLUE, CARD, FILLS, GREY, INK, MAP, PAPER, RED, SEA, H, W, _poly, arrow, card_frame, fillp, font,
                   halo_text, strokep, text)
from script import PARTS

FPS = 30
L, TOTAL = shots.lines()
SHOTS, _ = shots.table()          # (shot, start, end, frame, picture, motion, vo)
LINE_PART = {k: p for p, ls in PARTS.items() for k, _ in ls}
_TM = {p: timing.Timing(p, {k: L[k][0] for k, _ in ls}) for p, ls in PARTS.items()}
NEUTRAL = (238, 232, 216)
PURPLE = (120, 100, 160)


def w(k, phrase, end=False):
    return _TM[LINE_PART[k]].word(k, phrase, end)


def E(k):
    return _TM[LINE_PART[k]].end(k)


def S(k):
    return L[k][0]


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t0)


def smooth(x):
    return x * x * (3 - 2 * x)


def out_cubic(x):
    return 1 - (1 - x) ** 3


def out_back(x, s=1.7):
    x -= 1
    return 1 + x * x * ((s + 1) * x + s)


def lerp(a, b, u):
    return a + (b - a) * u


def fade(t, t0, d=0.35):
    return smooth(prog(t, t0, t0 + d))


# ------------------------------------------------------------------ cached map layers
_LAYERS = {}


def layer(key, view, res="10m", colors=None, default=None, only=None):
    """Projected country paths for a view, built once: [(a3, path, rgb)]."""
    if key in _LAYERS:
        return _LAYERS[key]
    x0, y0, x1, y1 = MAP
    out = []
    for f in geo.load(f"ne_{res}_admin_0_countries"):
        a3 = f["properties"]["ADM0_A3"]
        if only and a3 not in only:
            continue
        p = view.path(f["geometry"])
        b = p.getBounds()
        if b.right() < x0 - 200 or b.left() > x1 + 200 or b.bottom() < y0 - 200 or b.top() > y1 + 200:
            continue
        rgb = (colors or {}).get(a3) or default or FILLS[(f["properties"]["MAPCOLOR7"] - 1) % len(FILLS)]
        out.append((a3, p, rgb))
    _LAYERS[key] = out
    return out


def draw_layer(c, lay, border_a=150, lw=1.6, fill=True):
    if fill:
        for _, p, rgb in lay:
            c.drawPath(p, fillp(rgb))
    if border_a > 0:
        for _, p, _ in lay:
            c.drawPath(p, strokep(INK, lw, border_a))


_LINES = {}


def border_path(key, view, a, b):
    if key not in _LINES:
        p = skia.Path()
        for f in geo.load("ne_10m_admin_0_boundary_lines_land"):
            pr = f["properties"]
            if {pr["ADM0_A3_L"], pr["ADM0_A3_R"]} == {a, b}:
                for r in geo.rings(f["geometry"]):
                    p.addPath(view.line(r))
        _LINES[key] = p
    return _LINES[key]


def river_path(key, view, *names):
    if key not in _LINES:
        p = skia.Path()
        for f in geo.rivers(*names):
            for r in geo.rings(f["geometry"]):
                p.addPath(view.line(r))
        _LINES[key] = p
    return _LINES[key]


def reveal(c, u, direction="right", rect=MAP):
    """Clip so only the first fraction u of rect (in the given direction) shows. Call between save/restore."""
    x0, y0, x1, y1 = rect
    if direction == "right":
        r = (x0, y0, lerp(x0, x1, u), y1)
    elif direction == "left":
        r = (lerp(x1, x0, u), y0, x1, y1)
    elif direction == "up":
        r = (x0, lerp(y1, y0, u), x1, y1)
    else:
        r = (x0, y0, x1, lerp(y0, y1, u))
    c.clipRect(skia.Rect.MakeLTRB(*r))


# ------------------------------------------------------------------ hand-drawn pieces with write-on
def hand_on(c, s, x, y, size, u, rgb=RED, rot=0, align="center"):
    if u <= 0:
        return
    f = font("hand", size)
    wd = f.measureText(s)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    x0 = -wd / 2 if align == "center" else 0 if align == "left" else -wd
    c.clipRect(skia.Rect.MakeLTRB(x0 - 10, -size * 1.2, x0 + (wd + 20) * u, size * 0.6))
    c.drawString(s, x0, 0, f, fillp(rgb))
    c.restore()


def ring_on(c, x, y, rx, ry, u, rgb=RED, wd=5, rot=-8):
    if u <= 0:
        return
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    p = skia.Path()
    n = max(2, int(72 * u))
    for i in range(n + 1):
        a = -2.0 + i / 64 * 2 * math.pi
        r = 1 + 0.04 * math.sin(a * 3)
        (p.moveTo if i == 0 else p.lineTo)(rx * r * math.cos(a), ry * r * math.sin(a))
    c.drawPath(p, strokep(rgb, wd))
    c.restore()


def quad_pts(p0, p1, p2, n=40):
    return [((1 - s) ** 2 * p0[0] + 2 * (1 - s) * s * p1[0] + s * s * p2[0],
             (1 - s) ** 2 * p0[1] + 2 * (1 - s) * s * p1[1] + s * s * p2[1]) for s in (i / n for i in range(n + 1))]


def arrow_on(c, pts, u, rgb=RED, wd=5, head=22, dash=None):
    """Arrow along a polyline, drawn up to fraction u; the head appears at the end."""
    if u <= 0:
        return
    n = max(2, int(len(pts) * u))
    seg = pts[:n]
    if len(seg) < 2:
        return
    if u >= 1:
        arrow(c, seg, rgb, wd, head, dash)
    else:
        p = skia.Path()
        p.moveTo(*seg[0])
        for q in seg[1:]:
            p.lineTo(*q)
        c.drawPath(p, strokep(rgb, wd, dash=dash))


def stamp(c, s, x, y, t, t0, size=54, rgb=RED, rot=-8):
    """Rubber stamp: drops in big and lands with a slight overshoot."""
    if t < t0:
        return
    u = prog(t, t0, t0 + 0.22)
    sc = lerp(1.6, 1.0, out_cubic(u))
    f = font("monob", size)
    wd = f.measureText(s)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(sc, sc)
    a = 230 * u
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-wd / 2 - 24, -size * 0.95, wd / 2 + 24, size * 0.45), 10, 10), strokep(rgb, 6, a))
    c.drawString(s, -wd / 2, 0, f, fillp(rgb, a))
    c.restore()


def label_in(c, s, x, y, size, t, t0, kind="mono", rgb=INK, align="center"):
    a = fade(t, t0, 0.3)
    if a <= 0:
        return
    c.save()
    c.translate(0, 12 * (1 - a))
    lay = a < 1
    if lay:
        c.saveLayerAlpha(None, int(255 * a))
    halo_text(c, s, x, y, size, kind, rgb, align)
    if lay:
        c.restore()
    c.restore()


def dot(c, x, y, r=9, rgb=INK):
    c.drawCircle(x, y, r + 3, fillp(CARD))
    c.drawCircle(x, y, r, fillp(rgb))


# ------------------------------------------------------------------ views
V_HOOK = geo.View(MAP, -20, 82, -36, 60, "world")
V_RIO = geo.View(MAP, -108.5, -96, 23.5, 34.5)
V_PYR = geo.View(MAP, -3.6, 4.6, 40.4, 45.8)
V_49 = geo.View(MAP, -127, -86, 40, 57)
V_AFR = geo.View(MAP, -19, 53, -36, 38)
V_CAP = geo.View(MAP, 11, 31, -30, -11.5)
V_WAK = geo.View(MAP, 64, 78.5, 31, 40.5)
V_END = geo.View((MAP[0], MAP[1] + 210, MAP[2], MAP[3] - 180), -128, 152, -38, 64, "world")


# ------------------------------------------------------------------ 1 · hook
def hook(c, t):
    lay = layer("hook", V_HOOK, "50m")
    draw_layer(c, lay, border_a=0)
    n = len(lay)
    order = sorted(range(n), key=lambda i: (i * 7919) % n)
    for rank, i in enumerate(order):                          # borders flicker in, country by country
        a = fade(t, 0.25 + 2.0 * rank / n, 0.25)
        if a > 0:
            c.drawPath(lay[i][1], strokep(INK, 1.6, 150 * a))
    marks = [(w("H2", "wiggle"), [("FRA", "ESP")], (0.5, 42.7), (70, 34), -8, "wiggly", (-40, -60), -6),
             (w("H2", "straight"), [("EGY", "SDN"), ("EGY", "LBY")], (28, 22), (120, 70), 4, "ruler straight", (10, 120), -4),
             (w("H2", "strange"), [("AFG", "TJK"), ("AFG", "PAK"), ("AFG", "CHN")], (73, 37), (66, 40), -14, "just strange", (-60, -64), -8)]
    for t0, pairs, (lon, lat), (rx, ry), rot, note, (dx, dy), nrot in marks:
        if t < t0 - 0.1:
            continue
        a = fade(t, t0 - 0.1, 0.25)
        for a3, b3 in pairs:
            c.drawPath(border_path(f"hook{a3}{b3}", V_HOOK, a3, b3), strokep(RED, 5, 255 * a))
        x, y = V_HOOK(lon, lat)
        ring_on(c, x, y, rx, ry, prog(t, t0, t0 + 0.45), rot=rot)
        hand_on(c, note, x + dx, y + dy, 60, prog(t, t0 + 0.15, t0 + 0.7), rot=nrot)
    t1 = S("H3") - 0.25                                       # title over the dimmed map
    if t > t1:
        k = fade(t, t1, 0.4)
        c.drawRect(skia.Rect.MakeLTRB(*MAP), fillp(PAPER, 215 * k))
        cx, cy = (MAP[0] + MAP[2]) / 2, (MAP[1] + MAP[3]) / 2
        for i, (s, size, kind, rgb) in enumerate([("A SHORT ATLAS OF", 30, "monob", RED), ("Why are borders", 96, "serif", INK),
                                                  ("shaped like this?", 96, "serif", INK)]):
            u = fade(t, t1 + 0.1 + 0.12 * i, 0.4)
            c.save()
            c.translate(0, 24 * (1 - u))
            text(c, s, cx, cy - 90 + i * 110 - (20 if i == 0 else 0), size, kind, rgb, "center", 255 * u, 0.08 if i == 0 else 0)
            c.restore()
        u = prog(t, w("H3", "reason"), w("H3", "reason") + 0.5)
        if u > 0:
            c.drawLine(cx - 230, cy + 170, lerp(cx - 230, cx + 230, out_cubic(u)), cy + 170, strokep(RED, 6))


# ------------------------------------------------------------------ 2 · nature
def rio(c, t):
    v = V_RIO
    draw_layer(c, layer("rio", v, colors={"USA": (234, 214, 168), "MEX": (196, 214, 178)}))
    t0 = w("N2", "rio")
    if t > t0 - 0.1:
        u = smooth(prog(t, t0 - 0.1, t0 + 1.7))
        c.save()
        reveal(c, u, "right")
        c.drawPath(border_path("rio_b", v, "USA", "MEX"), strokep(RED, 16))
        c.drawPath(river_path("rio_r", v, "Rio Grande"), strokep(BLUE, 6))
        c.restore()
    else:
        c.drawPath(river_path("rio_r", v, "Rio Grande"), strokep(BLUE, 4, 150 * fade(t, S("N1") + 0.6, 0.6)))
    label_in(c, "UNITED STATES", *v(-100.5, 33.2), 34, t, S("N1") + 0.1)
    label_in(c, "MEXICO", *v(-104.5, 27.0), 34, t, S("N1") + 0.3)
    for lon, lat, name, al in [(-106.49, 31.76, "EL PASO", "left"), (-97.5, 25.9, "BROWNSVILLE", "right")]:
        x, y = v(lon, lat)
        if t > S("N1") + 0.4:
            dot(c, x, y)
            label_in(c, name, x + (14 if al == "left" else -14), y - 18, 22, t, S("N1") + 0.4, "mono", INK, al)
    x, y = v(-100.6, 29.7)
    hand_on(c, "Rio Grande", x + 160, y + 10, 62, prog(t, w("N2", "grande"), w("N2", "grande") + 0.7), BLUE, -18)
    x, y = v(-107.6, 31.6)
    tm = w("N2", "mexico")
    hand_on(c, "no river here:", x + 60, y + 110, 44, prog(t, tm, tm + 0.6), RED, -4)
    hand_on(c, "a straight line", x + 60, y + 154, 44, prog(t, tm + 0.3, tm + 0.9), RED, -4)


def _ridge_points():
    pts = []
    for f in geo.load("ne_10m_admin_0_boundary_lines_land"):
        pr = f["properties"]
        if {pr["ADM0_A3_L"], pr["ADM0_A3_R"]} & {"FRA", "ESP"} and {pr["ADM0_A3_L"], pr["ADM0_A3_R"]} <= {"FRA", "ESP", "AND"}:
            for r in geo.rings(f["geometry"]):
                pts += r
    return sorted(pts)


RIDGE = None


def pyrenees(c, t):
    global RIDGE
    v = V_PYR
    draw_layer(c, layer("pyr", v, colors={"FRA": (190, 206, 226), "ESP": (234, 214, 168), "AND": (232, 190, 178)}))
    if RIDGE is None:
        RIDGE = _ridge_points()
    t0 = w("N3", "ridges")
    u = smooth(prog(t, t0 - 0.2, t0 + 1.6))
    xa, xb = v(-2.0, 43)[0], v(3.4, 43)[0]
    for i, (lon, lat) in enumerate(RIDGE[::16]):                # hachure peaks either side of the crest
        x, y = v(lon, lat)
        k = fade(t, S("N3") - 0.2 + 1.2 * (x - xa) / (xb - xa), 0.3)
        if k <= 0:
            continue
        for dy, s in ((-34, 0.8), (30, 1.0)):
            yy = y + dy + 8 * math.sin(i * 1.7)
            hw = 13 * s
            c.drawPath(_poly([(x - hw, yy + 8 * s), (x, yy - 11 * s), (x + hw, yy + 8 * s)], False), strokep((120, 106, 90), 2.5, 150 * k))
    if u > 0:
        c.save()
        reveal(c, u, "right")
        p = skia.Path()
        for a, b in (("FRA", "ESP"), ("FRA", "AND"), ("AND", "ESP")):
            p.addPath(border_path(f"pyr{a}{b}", v, a, b))
        c.drawPath(p, strokep(RED, 9))
        c.restore()
    label_in(c, "FRANCE", *v(1.5, 44.6), 36, t, S("N3"))
    label_in(c, "SPAIN", *v(-1.0, 41.4), 36, t, S("N3") + 0.2)
    label_in(c, "ANDORRA", *v(1.55, 42.25), 20, t, S("N3") + 0.4)
    tp = w("N3", "pyrenees")
    x, y = v(-0.2, 42.6)
    hand_on(c, "the Pyrenees", x - 40, y - 120, 64, prog(t, tp, tp + 0.7), RED, -5)
    arrow_on(c, quad_pts((x - 60, y - 100), (x - 20, y - 70), (x, y - 26), 20), prog(t, tp + 0.3, tp + 0.7), RED, 4, 18)
    stamp(c, "EASY TO SEE", *v(-1.2, 45.0), t, w("N4", "see") - 0.05, 46, RED, -6)
    stamp(c, "HARD TO CROSS", *v(2.2, 40.9), t, w("N4", "cross") - 0.05, 46, RED, 5)


# ------------------------------------------------------------------ 3 · straight lines
def graticule(c, a=60):
    x0, y0, x1, y1 = MAP
    for i in range(1, 8):
        y = lerp(y0, y1, i / 8)
        c.drawLine(x0, y, x1, y, strokep(GREY, 1.5, a, dash=[10, 8]))
    for i in range(1, 8):
        x = lerp(x0, x1, i / 8)
        c.drawLine(x, y0, x, y1, strokep(GREY, 1.5, a, dash=[10, 8]))


def ruler(c, x0, y0, x1, y1, a=255, wd=46):
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    ln = math.hypot(x1 - x0, y1 - y0)
    c.save()
    c.translate(x0, y0)
    c.rotate(ang)
    c.drawRect(skia.Rect.MakeLTRB(0, -wd, ln, 0), fillp((246, 232, 190), a))
    c.drawRect(skia.Rect.MakeLTRB(0, -wd, ln, 0), strokep(INK, 2, a))
    for i in range(0, int(ln), 12):
        c.drawLine(i, 0, i, -(16 if i % 60 == 0 else 8), strokep(INK, 2, a))
    c.restore()


def pencil(c, x, y, ang=-30, a=255):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.drawPath(_poly([(0, 0), (34, -12), (34, 12)]), fillp((236, 214, 170), a))
    c.drawPath(_poly([(0, 0), (11, -4), (11, 4)]), fillp(INK, a))
    c.drawRect(skia.Rect.MakeLTRB(34, -12, 250, 12), fillp((240, 190, 60), a))
    c.drawLine(34, 0, 250, 0, strokep((210, 160, 40), 2, a))
    c.drawRect(skia.Rect.MakeLTRB(250, -12, 280, 12), fillp((200, 200, 205), a))
    c.drawRect(skia.Rect.MakeLTRB(280, -12, 310, 12), fillp((230, 140, 150), a))
    c.drawRect(skia.Rect.MakeLTRB(34, -12, 310, 12), strokep(INK, 2, a))
    c.restore()


def paper(c, t):
    x0, y0, x1, y1 = MAP
    c.drawRect(skia.Rect.MakeLTRB(*MAP), fillp(CARD))
    graticule(c)
    ts = S("S1")
    k = out_cubic(prog(t, ts - 0.1, ts + 0.5))
    ax, ay, bx, by = x0 + 90, y0 + 640, x1 - 90, y0 + 300
    off = (1 - k) * -700
    ruler(c, ax + off, ay + off * 0.1, bx + off, by + off * 0.1, 255 * k)
    td = w("S1", "drawn") - 0.1
    u = smooth(prog(t, td, td + 1.5))
    if u > 0:
        px, py = lerp(ax, bx, u), lerp(ay, by, u)
        c.drawLine(ax, ay + 4, px, py + 4, strokep(RED, 6))
        pencil(c, px, py + 4, -40 + 8 * math.sin(t * 9), 255 * (1 - fade(t, td + 1.7, 0.3)))
    tf = w("S1", "far")
    hand_on(c, "far from the land", (x0 + x1) / 2 + 120, y0 + 560, 56, prog(t, tf, tf + 0.7), RED, -14)
    tp = w("S1", "paper")
    hand_on(c, "on paper", x0 + 260, y0 + 210, 56, prog(t, tp - 0.1, tp + 0.5), INK, -14)


def parallel(c, t):
    v = V_49
    draw_layer(c, layer("49", v, colors={"CAN": (222, 200, 226), "USA": (234, 214, 168)}))
    label_in(c, "CANADA", *v(-100, 54.5), 38, t, S("S2") - 0.2)
    label_in(c, "UNITED STATES", *v(-104, 44.0), 38, t, S("S2"))
    tl = w("S2", "latitude")
    k = fade(t, tl, 0.4)
    if k > 0:
        y = v(0, 49)[1]
        c.drawLine(MAP[0], y, MAP[2], y, strokep(INK, 2, 160 * k, dash=[14, 10]))
        halo_text(c, "49° N", MAP[0] + 80, y - 16, 26, "monob", INK) if k > 0.5 else None
    tf = w("S2", "forty")
    xa, ya = v(-95.15, 49.0)
    xr, _ = v(-114.06, 49.0)
    xp, _ = v(-123.03, 49.0)
    u = smooth(prog(t, tf - 0.1, tf + 1.3))
    if u > 0:
        c.drawLine(xa, ya, lerp(xa, xr, u), ya, strokep(RED, 10))
    tb = E("S2") - 0.4
    u2 = smooth(prog(t, tb, tb + 0.9))
    if u2 > 0:
        c.drawLine(xr, ya, lerp(xr, xp, u2), ya, strokep(RED, 6, dash=[16, 10]))
        label_in(c, "extended 1846", (xr + xp) / 2, ya + 44, 22, t, tb + 0.4, "mono", RED)
    stamp(c, "1818", *v(-118, 53.2), t, w("S2", "eighteen") - 0.05, 60, RED, -8)
    hand_on(c, "the 49th parallel", (xa + xr) / 2, ya - 40, 58, prog(t, w("S2", "ninth"), w("S2", "ninth") + 0.7), RED, -3)
    tpr = w("S2", "prairies")
    if t > tpr - 0.1:
        for i in range(14):                                     # grass ticks on the plains
            gx, gy = v(-112 + 1.6 * i + 0.6 * math.sin(i * 2.3), 51.0 - (i % 3) * 0.6)
            a = 255 * fade(t, tpr - 0.1 + 0.03 * i, 0.2)
            for dx, h in ((-6, 14), (0, 20), (6, 13)):
                c.drawLine(gx, gy, gx + dx, gy - h, strokep((90, 130, 70), 3, a))
        hand_on(c, "the prairies", *v(-103, 51.9), 50, prog(t, tpr, tpr + 0.6), (70, 110, 50), -4)


STRAIGHT = None


def africa(c, t):
    global STRAIGHT
    v = V_AFR
    draw_layer(c, layer("afr", v))
    if STRAIGHT is None:
        segs = geo.straight_segments()
        STRAIGHT = sorted(segs, key=lambda s: -(s[0][1] + s[1][1]))        # north to south
    t0, t1 = w("S3", "split") - 0.1, w("S3", "lines", end=True) + 0.3
    n = len(STRAIGHT)
    for i, (a, b) in enumerate(STRAIGHT):
        ts = lerp(t0, t1, i / n)
        u = out_cubic(prog(t, ts, ts + 0.3))
        if u > 0:
            (xa, ya), (xb, yb) = v(*a), v(*b)
            c.drawLine(xa, ya, lerp(xa, xb, u), lerp(ya, yb, u), strokep(RED, 7))
    tr = w("S3", "straight")
    k = out_cubic(prog(t, tr, tr + 0.4))
    if k > 0:
        x0, y = v(24.5, 22.0)
        x1, _ = v(37, 22.0)
        c.save()
        c.translate(0, -48 - 300 * (1 - k))
        ruler(c, x0 - 20, y + 22, x1 + 20, y + 22, 235 * k, 44)
        c.restore()
        hand_on(c, "22° N", (x0 + x1) / 2, y - 90, 50, prog(t, tr + 0.3, tr + 0.7), RED, -3)
    th = w("S3", "hundreds")
    x, y = v(-10, -20)
    hand_on(c, "200+ peoples", x + 30, y, 56, prog(t, th, th + 0.6), RED, -6)
    hand_on(c, "split by borders", x + 30, y + 52, 48, prog(t, th + 0.3, th + 0.9), RED, -6)
    label_in(c, "1880s – 1900s", *v(-9, 2), 26, t, w("S3", "late"), "monob", INK)


# ------------------------------------------------------------------ 4 · deals
def treaty(c, t):
    x0, y0, x1, y1 = MAP
    c.drawRect(skia.Rect.MakeLTRB(*MAP), fillp((214, 200, 176)))
    t0 = S("W1") - 0.3
    k = out_cubic(prog(t, t0, t0 + 0.45))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 900 * (1 - k)
    c.save()
    c.translate(cx, cy)
    c.rotate(-4)
    c.drawRect(skia.Rect.MakeLTRB(-330 + 10, -400 + 14, 330 + 10, 400 + 14), fillp((0, 0, 0), 40))
    c.drawRect(skia.Rect.MakeLTRB(-330, -400, 330, 400), fillp((250, 244, 228)))
    c.drawRect(skia.Rect.MakeLTRB(-330, -400, 330, 400), strokep(INK, 2))
    text(c, "TREATY", 0, -300, 80, "serif", INK, "center")
    text(c, "between the Empires", 0, -248, 30, "serif", GREY, "center")
    for i in range(9):
        wl = 480 - 80 * ((i * 37) % 3)
        c.drawRect(skia.Rect.MakeLTRB(-260, -190 + i * 34, -260 + wl, -180 + i * 34), fillp((200, 192, 176)))
    for j, sx in enumerate((-150, 150)):                        # two signatures scribble on
        u = prog(t, t0 + 0.4 + 0.3 * j, t0 + 0.9 + 0.3 * j)
        if u > 0:
            pts = [(sx - 90 + 180 * s, 250 - 20 * math.sin(s * 14 + j) - 10 * math.sin(s * 5)) for s in (i / 40 for i in range(int(40 * u) + 1))]
            if len(pts) > 1:
                p = skia.Path()
                p.moveTo(*pts[0])
                for q in pts[1:]:
                    p.lineTo(*q)
                c.drawPath(p, strokep((30, 50, 110), 4))
        c.drawLine(sx - 110, 280, sx + 110, 280, strokep(INK, 2))
    td = w("W1", "deals")
    if t > td - 0.05:
        u = prog(t, td - 0.05, td + 0.2)
        sc = lerp(1.5, 1.0, out_cubic(u))
        c.save()
        c.translate(200, 120)
        c.scale(sc, sc)
        for r, rgb in ((78, (160, 30, 30)), (66, (196, 50, 40))):
            c.drawPath(geo_blob(r), fillp(rgb, 255 * u))
        text(c, "DEAL", 0, 12, 34, "monob", (250, 220, 200), "center", 255 * u)
        c.restore()
    c.restore()


def geo_blob(r):
    p = skia.Path()
    for i in range(41):
        a = i / 40 * 2 * math.pi
        rr = r * (1 + 0.06 * math.sin(a * 7) + 0.03 * math.sin(a * 13))
        (p.moveTo if i == 0 else p.lineTo)(rr * math.cos(a), rr * math.sin(a))
    p.close()
    return p


def caprivi(c, t):
    v = V_CAP
    draw_layer(c, layer("cap", v, colors={"NAM": (232, 178, 160)}, default=NEUTRAL))
    for name, lon, lat, dt in [("NAMIBIA", 17, -22.5, 0.0), ("ANGOLA", 17, -14, 0.2), ("ZAMBIA", 26.5, -14, 0.3),
                               ("BOTSWANA", 24, -22.5, 0.4), ("ZIMBABWE", 29.2, -20.6, 0.5), ("SOUTH AFRICA", 24, -28.3, 0.6)]:
        label_in(c, name, *v(lon, lat), 28, t, S("W2") - 0.2 + dt, "mono", INK if name == "NAMIBIA" else GREY)
    tc = w("W2", "caprivi")
    pulse = fade(t, tc - 0.1, 0.3) * (1 - fade(t, tc + 1.4, 0.5))
    if pulse > 0:
        nam = [p for a3, p, _ in layer("cap", v) if a3 == "NAM"][0]
        c.drawPath(nam, strokep(RED, 5, 255 * pulse))
    x, y = v(22.5, -17.9)
    hand_on(c, "Caprivi Strip", x - 30, y - 70, 58, prog(t, tc, tc + 0.7), RED, -5)
    arrow_on(c, [(x - 110 + 70 * s, y - 52 + 34 * s) for s in (i / 10 for i in range(11))], prog(t, tc + 0.4, tc + 0.7), RED, 4, 18)
    label_in(c, "1890 · traded with Britain", *v(18.6, -19.6), 22, t, w("W2", "germany's"), "mono", RED)
    tz = w("W2", "zambezi")
    u = smooth(prog(t, tz - 0.3, tz + 1.0))
    c.save()
    reveal(c, 0.15 + 0.85 * u, "right")
    c.drawPath(river_path("zam", v, "Zambezi"), strokep(BLUE, 6, 120 + 135 * u))
    c.restore()
    hand_on(c, "Zambezi", *v(29.6, -17.9), 48, prog(t, tz + 0.2, tz + 0.8), BLUE, 30)
    fx, fy = v(25.86, -17.92)
    tb = w("W2", "but")
    route = quad_pts(v(24.9, -17.6), (fx + 60, fy - 120), v(30.8, -16.2), 30)
    arrow_on(c, route, prog(t, tb - 0.2, tb + 0.6), RED, 5, 24, dash=[18, 12])
    tf = w("W2", "falls")
    if t > tf - 0.1:
        u = prog(t, tf - 0.1, tf + 0.12)
        s = lerp(1.8, 1.0, u)
        for k in (-1, 1):
            c.drawLine(fx - 24 * s, fy - 24 * k * s, fx + 24 * s, fy + 24 * k * s, strokep(RED, 9, 255 * u))
        label_in(c, "VICTORIA FALLS", fx + 10, fy + 62, 24, t, tf, "monob", BLUE)
    ts = w("W2", "sea")
    x2, y2 = v(29.3, -15.4)
    hand_on(c, "to the sea", x2, y2 - 40, 46, prog(t, ts - 0.1, ts + 0.5), RED, -10)


def wakhan(c, t):
    v = V_WAK
    draw_layer(c, layer("wak", v, colors={"AFG": (232, 178, 160)}, default=NEUTRAL))
    c.drawPath(river_path("panj", v, "Panj", "Amu  Darya"), strokep(BLUE, 5))
    label_in(c, "AFGHANISTAN", *v(66.5, 34.3), 30, t, S("W3") - 0.3, "monob", INK)
    label_in(c, "CHINA", *v(77.2, 38.2), 26, t, S("W3"), "mono", GREY)
    tw = w("W3", "wakhan")
    x, y = v(73.2, 37.05)
    ring_on(c, x, y, 150, 40, prog(t, tw - 0.1, tw + 0.4), rot=-6)
    hand_on(c, "Wakhan Corridor", x - 20, y + 92, 58, prog(t, tw + 0.1, tw + 0.8), RED, -4)
    tt = w("W3", "thin")
    label_in(c, "~13 km at its narrowest", x + 40, y + 150, 24, t, tt, "mono", INK)
    for who, a3, lon, lat, sub, d in [("british", "PAK", 72.2, 33.0, "today: Pakistan", "up"), ("russian", "TJK", 69.5, 39.3, "today: Tajikistan", "down")]:
        te = w("W3", who)
        u = smooth(prog(t, te - 0.15, te + 0.9))
        if u > 0:
            c.save()
            reveal(c, u, d)
            c.drawPath(border_path(f"wak{a3}", v, "AFG", a3), strokep(PURPLE, 7))
            c.restore()
        bx, by = v(lon, lat)
        label_in(c, "BRITISH INDIA" if a3 == "PAK" else "RUSSIAN EMPIRE", bx, by, 34, t, te - 0.1, "monob", PURPLE)
        label_in(c, sub, bx, by + 38, 22, t, te + 0.2, "mono", GREY)
    tn = w("W3", "never")
    for (sx, sy), (ex, ey) in [((v(70.5, 38.6)), (x - 40, y - 46)), ((v(72.6, 33.6)), (x - 30, y + 40))]:
        arrow_on(c, quad_pts((sx, sy), ((sx + ex) / 2 + 40, (sy + ey) / 2), (ex, ey), 20), prog(t, tn, tn + 0.5), PURPLE, 4, 18)
    label_in(c, "1895", *v(65.5, 39.6), 30, t, tn + 0.3, "monob", PURPLE)


# ------------------------------------------------------------------ 5 · Baarle and the end
def _blob(cx, cy, r, seed, n=9):
    rng = np.random.default_rng(seed)
    pts = []
    for i in range(n):
        a = i / n * 2 * math.pi + rng.uniform(-0.2, 0.2)
        rr = r * rng.uniform(0.65, 1.2)
        pts.append((cx + rr * math.cos(a), cy + rr * 0.85 * math.sin(a)))
    return _poly(pts)


BAARLE = [(220, 640, 70), (390, 560, 52), (560, 700, 90), (760, 600, 60), (880, 760, 48), (300, 860, 80), (500, 930, 44),
          (690, 900, 72), (860, 980, 40), (240, 1060, 50), (420, 1120, 66), (640, 1080, 46), (820, 1150, 56), (560, 820, 30)]
NL_IN = {2: (575, 705, 30), 7: (700, 905, 24), 10: (430, 1125, 22)}
SANDB, DUSTYB = (234, 214, 168), (190, 206, 226)


def baarle(c, t):
    x0, y0, x1, y1 = MAP
    c.drawRect(skia.Rect.MakeLTRB(*MAP), fillp(DUSTYB))
    belg = skia.Path()
    belg.moveTo(x0, y1 - 90)
    for i in range(13):
        belg.lineTo(x0 + i * 80, y1 - 110 + 22 * math.sin(i * 1.9))
    belg.lineTo(x1, y1)
    belg.lineTo(x0, y1)
    belg.close()
    c.drawPath(belg, fillp(SANDB))
    c.drawPath(belg, strokep(RED, 5))
    ts, te = S("B1") - 0.2, w("B1", "deals", end=True)
    for i, (bx, by, r) in enumerate(BAARLE):
        u = out_back(prog(t, lerp(ts, te, i / len(BAARLE)), lerp(ts, te, i / len(BAARLE)) + 0.3))
        if u <= 0:
            continue
        c.save()
        c.translate(x0 + bx - 60, by)
        c.scale(u, u)
        p = _blob(0, 0, r, i)
        c.drawPath(p, fillp(SANDB))
        c.drawPath(p, strokep(RED, 4))
        if i in NL_IN:
            nx, ny, nr = NL_IN[i]
            q = _blob(nx - bx, ny - by, nr, 100 + i, 7)
            c.drawPath(q, fillp(DUSTYB))
            c.drawPath(q, strokep(RED, 3))
        text(c, "B", 0, 10, 28 if r > 40 else 20, "monob", INK, "center")
        c.restore()
    label_in(c, "BELGIUM", (x0 + x1) / 2, y1 - 36, 30, t, S("B1"), "monob", INK)
    label_in(c, "NETHERLANDS", (x0 + x1) / 2, y0 + 70, 30, t, S("B1"), "monob", INK)
    label_in(c, "SCHEMATIC", x1 - 110, y0 + 70, 18, t, S("B1"), "mono", GREY)
    for word, (px, py) in [("cafes", (560 - 60 + x0 + 70, 660)), ("gardens", (300 - 60 + x0 - 60, 830)), ("homes", (690 - 60 + x0 + 60, 860))]:
        tw = w("B1", word)
        k = out_back(prog(t, tw - 0.05, tw + 0.25))
        if k > 0:
            c.save()
            c.translate(px, py)
            c.scale(k, k)
            c.drawCircle(0, 0, 34, fillp(CARD))
            c.drawCircle(0, 0, 34, strokep(INK, 3))
            icon(c, word)
            c.restore()


def icon(c, kind):
    if kind == "cafes":
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-14, -8, 10, 14), 4, 4), fillp(INK))
        c.drawCircle(13, 2, 7, strokep(INK, 3))
        for dx in (-6, 2):
            c.drawLine(dx, -14, dx + 2, -22, strokep(INK, 2))
    elif kind == "gardens":
        c.drawLine(0, 18, 0, -2, strokep((90, 70, 50), 4))
        c.drawCircle(0, -8, 13, fillp((90, 140, 80)))
    else:
        c.drawPath(_poly([(-16, -2), (0, -18), (16, -2)]), fillp(RED))
        c.drawRect(skia.Rect.MakeLTRB(-12, -2, 12, 16), fillp(INK))


def flag(c, x, y, kind, wd=90, h=60):
    cols = [(30, 30, 30), (250, 210, 40), (220, 40, 50)] if kind == "B" else [(174, 28, 40), (255, 255, 255), (33, 70, 139)]
    for i, rgb in enumerate(cols):
        r = skia.Rect.MakeXYWH(x + i * wd / 3, y, wd / 3, h) if kind == "B" else skia.Rect.MakeXYWH(x, y + i * h / 3, wd, h / 3)
        c.drawRect(r, fillp(rgb))
    c.drawRect(skia.Rect.MakeXYWH(x, y, wd, h), strokep(INK, 2))


def house(c, x, y, wd, h, wall, roof, door_x=None, door_glow=0.0):
    c.drawRect(skia.Rect.MakeXYWH(x, y, wd, h), fillp(wall))
    c.drawPath(_poly([(x - 16, y), (x + wd / 2, y - h * 0.5), (x + wd + 16, y)]), fillp(roof))
    c.drawPath(_poly([(x - 16, y), (x + wd / 2, y - h * 0.5), (x + wd + 16, y)]), strokep(INK, 3))
    c.drawRect(skia.Rect.MakeXYWH(x, y, wd, h), strokep(INK, 3))
    for wx in (x + wd * 0.12, x + wd * 0.62):
        if door_x is not None and abs(wx + wd * 0.13 - door_x) < wd * 0.2:
            continue
        c.drawRect(skia.Rect.MakeXYWH(wx, y + h * 0.18, wd * 0.26, h * 0.26), fillp((200, 220, 230)))
        c.drawRect(skia.Rect.MakeXYWH(wx, y + h * 0.18, wd * 0.26, h * 0.26), strokep(INK, 3))
    if door_x is not None:
        if door_glow > 0:
            c.drawRect(skia.Rect.MakeXYWH(door_x - 52, y + h - 182, 104, 182), strokep(RED, 6, 255 * door_glow))
        c.drawRect(skia.Rect.MakeXYWH(door_x - 40, y + h - 170, 80, 170), fillp((60, 110, 90)))
        c.drawRect(skia.Rect.MakeXYWH(door_x - 40, y + h - 170, 80, 170), strokep(INK, 3))
        c.drawCircle(door_x + 22, y + h - 84, 6, fillp((230, 200, 90)))


def street(c, t):
    x0, y0, x1, y1 = MAP
    c.drawRect(skia.Rect.MakeLTRB(*MAP), fillp((222, 234, 238)))
    gy = 1110
    c.drawRect(skia.Rect.MakeLTRB(x0, gy, x1, y1), fillp((196, 190, 180)))
    for i in range(0, 1100, 64):
        c.drawLine(x0 + i, gy, x0 + i - 120, y1, strokep((176, 170, 160), 2))
    tf = w("B2", "front")
    glow = fade(t, tf - 0.1, 0.25)
    house(c, x0 + 40, 760, 250, 350, (214, 170, 140), (150, 70, 60))
    house(c, x0 + 340, 700, 360, 410, (232, 214, 186), (110, 90, 80), door_x=x0 + 470, door_glow=glow)
    house(c, x0 + 750, 780, 180, 330, (190, 160, 140), (130, 80, 70))
    bx = x0 + 560
    t0 = S("B2") - 0.3
    u = smooth(prog(t, t0, t0 + 1.0))
    if u > 0:
        yb = lerp(y1, 700, u)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x0, yb, x1, y1))
        c.drawLine(bx, 700, bx, gy, strokep(RED, 7, dash=[22, 14]))
        c.drawLine(bx, gy, bx - 60, y1, strokep((255, 255, 255), 10, dash=[30, 18]))
        c.restore()
    for k, yy in enumerate((1170, 1250)):
        a = 255 * fade(t, t0 + 0.3 + 0.15 * k, 0.2)
        cx = bx - 30 - 30 * k
        c.drawLine(cx - 26, yy, cx + 26, yy, strokep((255, 255, 255), 8, a))
        c.drawLine(cx, yy - 16, cx, yy + 16, strokep((255, 255, 255), 8, a))
        text(c, "B", cx - 60, yy + 12, 32, "monob", (255, 255, 255), "center", a)
        text(c, "NL", cx + 60, yy + 12, 32, "monob", (255, 255, 255), "center", a)
    flag(c, x0 + 60, y0 + 40, "B")
    text(c, "BELGIUM", x0 + 170, y0 + 82, 30, "monob", INK)
    flag(c, x1 - 150, y0 + 40, "NL")
    text(c, "NETHERLANDS", x1 - 170, y0 + 82, 30, "monob", INK, "right")
    tb = w("B2", "door", end=True)
    k = fade(t, tb - 0.1, 0.3)
    if k > 0:
        c.drawRect(skia.Rect.MakeLTRB(x0 + 30, 1180, x0 + 380, 1310), fillp(CARD, 235 * k))
        c.drawRect(skia.Rect.MakeLTRB(x0 + 30, 1180, x0 + 380, 1310), strokep(INK, 2, 255 * k))
    hand_on(c, "front door in Belgium", x0 + 205, 1236, 46, prog(t, tb, tb + 0.6), RED)
    hand_on(c, "= a Belgian house", x0 + 205, 1288, 42, prog(t, tb + 0.4, tb + 0.9), RED)
    arrow_on(c, quad_pts((x0 + 300, 1176), (x0 + 360, 1110), (x0 + 412, 1050), 16), prog(t, tf, tf + 0.4), RED, 5, 22)


def ending(c, t):
    v = V_END
    lay = layer("end", v, "50m")
    tz = w("B3", "frozen")
    draw_layer(c, lay, border_a=110 + 100 * fade(t, tz, 0.5), lw=1.2)
    tr = w("B3", "rivers")
    k = fade(t, tr - 0.1, 0.3)
    if k > 0:
        c.drawPath(river_path("end_rio", v, "Rio Grande"), strokep(BLUE, 5, 255 * k))
        c.drawPath(river_path("end_zam", v, "Zambezi"), strokep(BLUE, 4, 255 * k))
    tu = w("B3", "rulers")
    u = smooth(prog(t, tu - 0.1, tu + 0.6))
    if u > 0:
        for a, b in STRAIGHT or geo.straight_segments():
            (xa, ya), (xb, yb) = v(*a), v(*b)
            c.drawLine(xa, ya, lerp(xa, xb, u), lerp(ya, yb, u), strokep(RED, 3.5))
        xa, ya = v(-95.15, 49)
        xb, yb = v(-123.03, 49)
        c.drawLine(xa, ya, lerp(xa, xb, u), lerp(ya, yb, u), strokep(RED, 3.5))
    td = w("B3", "deals")
    for i, (lon, lat, r) in enumerate([(23.5, -17.9, 24), (73, 37, 22)]):
        x, y = v(lon, lat)
        ring_on(c, x, y, r * 1.6, r, prog(t, td + 0.1 * i, td + 0.4 + 0.1 * i), RED, 4)
    ta = w("B3", "accidents")
    x, y = v(4.93, 51.44)
    ring_on(c, x, y, 26, 20, prog(t, ta, ta + 0.4), RED, 4)
    hand_on(c, "Baarle", x + 10, y - 30, 36, prog(t, ta + 0.1, ta + 0.5), RED, -6)
    tt = w("B3", "story", end=True)
    cx = (MAP[0] + MAP[2]) / 2
    for i, (s, size, kind, y) in enumerate([("Every border", 88, "serif", MAP[1] + 130), ("is a story.", 88, "serif", MAP[3] - 60)]):
        u = fade(t, (S("B3") - 0.1) + 0.25 * i, 0.4)
        c.save()
        c.translate(0, 20 * (1 - u))
        text(c, s, cx, y, size, kind, INK, "center", 255 * u)
        c.restore()
    if tt:
        pass


# ------------------------------------------------------------------ shot table
# shot -> (draw, section no., section, headline, camera push (zoom at end, focus lon/lat or card point), view)
SPEC = {
    "1A": (hook, 1, "the hook", "Borders aren't random", 1.05, None, True),
    "1B": (hook, 1, "the hook", "Borders aren't random", 1.0, None, True),
    "1C": (hook, 1, "the hook", "Borders aren't random", 1.0, None, True),
    "2A": (rio, 2, "nature", "Rivers draw borders", 1.06, None, True),
    "2B": (pyrenees, 2, "nature", "So do mountain ridges", 1.05, None, True),
    "2C": (pyrenees, 2, "nature", "So do mountain ridges", 1.0, None, True),
    "3A": (paper, 3, "straight lines", "Lines drawn on paper", 1.03, None, False),
    "3B": (parallel, 3, "straight lines", "The 49th parallel", 1.05, None, True),
    "3C": (africa, 3, "straight lines", "Africa, by ruler", 1.04, None, True),
    "4A": (treaty, 4, "deals", "Strange shapes are deals", 1.0, None, False),
    "4B": (caprivi, 4, "deals", "The Caprivi Strip", 1.05, None, True),
    "4C": (wakhan, 4, "deals", "The Wakhan Corridor", 1.05, None, True),
    "5A": (baarle, 5, "accidents", "Baarle, the patchwork town", 1.45, (560, 760), False),
    "5B": (street, 5, "accidents", "A border through the house", 1.03, None, False),
    "5C": (ending, 5, "accidents", "Rivers, rulers, deals", 1.0, None, True),
}
CUTS = [(s[0], s[1], s[2]) for s in SHOTS]
XF = 0.3                                                       # dissolve length at a cut


def shot_at(t):
    for i, (name, s, e) in enumerate(CUTS):
        if t < e or i == len(CUTS) - 1:
            return i
    return len(CUTS) - 1


def card_content(c, t, i):
    name, s, e = CUTS[i]
    draw, *_rest = SPEC[name]
    zoom_end, focus = SPEC[name][4], SPEC[name][5]
    x0, y0, x1, y1 = MAP
    fx, fy = focus or ((x0 + x1) / 2, (y0 + y1) / 2)
    if name == "5A":                                           # push into the street at the end of the shot
        z = lerp(1.0, zoom_end, smooth(prog(t, e - 1.4, e + XF)) ** 1.5)
    else:
        z = lerp(1.0, zoom_end, smooth(prog(t, s, e)))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(*MAP))
    c.drawRect(skia.Rect.MakeLTRB(*MAP), fillp(SEA))
    c.translate(fx, fy)
    c.scale(z, z)
    c.translate(-fx, -fy)
    draw(c, t)
    c.restore()


def headline_block(c, t):
    """Section tag + serif headline; on a change the old one lifts away and the new one rises in."""
    i = shot_at(t)
    name, s, _ = CUTS[i]
    cur = SPEC[name]
    prev = SPEC[CUTS[i - 1][0]] if i > 0 else None
    changed = prev is not None and (prev[2], prev[3]) != (cur[2], cur[3])
    same_tag = prev is not None and prev[1:3] == cur[1:3]
    k_out = fade(t, s - 0.25, 0.22) if changed else 1.0       # the old headline lifts away first ...
    k_in = fade(t, s - 0.02, 0.32) if changed else 1.0        # ... then the new one rises in
    for spec, a, dy in ((prev, 1 - k_out, -30 * k_out), (cur, k_in, 30 * (1 - k_in))):
        if spec is None or a <= 0.01 or (spec is prev and not changed):
            continue
        _, num, section, head = spec[:4]
        if not same_tag or spec is cur:
            ta = 255 if same_tag else 255 * a
            text(c, f"No. {num}  ·  {section.upper()}", 70, 250, 30, "monob", RED, a=ta, tracking=0.08)
        c.save()
        c.translate(0, dy)
        size = 78
        while font("serif", size).measureText(head) > 950:
            size -= 2
        text(c, head, 66, 345, size, "serif", INK, a=255 * a)
        c.restore()


def card_chrome(c, t):
    x0, y0, x1, y1 = MAP
    c.drawRect(skia.Rect.MakeLTRB(x0 + 8, y0 + 10, x1 + 8, y1 + 10), fillp((0, 0, 0), 22))


def card_border(c, t):
    i = shot_at(t)
    x0, y0, x1, y1 = MAP
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), strokep(INK, 3))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 10, y0 + 10, x1 - 10, y1 - 10), strokep(INK, 1, 120))
    if SPEC[CUTS[i][0]][6]:
        nx, ny = x1 - 60, y0 + 70
        c.drawCircle(nx, ny + 10, 46, fillp(CARD, 200))
        c.drawPath(_poly([(nx, ny - 34), (nx + 14, ny + 10), (nx, ny), (nx - 14, ny + 10)]), fillp(INK))
        text(c, "N", nx, ny + 44, 24, "monob", INK, "center")


# ------------------------------------------------------------------ captions
MERGES = {"S2": [("eighteen eighteen", "1818"), ("forty ninth", "49th")], "S3": [("eighteen hundreds", "1800s")]}
KEYS = {"H2": {"wiggle", "straight", "strange"}, "N1": {"nature"}, "N2": {"rio", "grande"}, "N3": {"pyrenees"},
        "S1": {"paper"}, "S2": {"49th"}, "S3": {"straight"}, "W1": {"deals"}, "W2": {"caprivi", "strip", "zambezi"},
        "W3": {"wakhan", "buffer"}, "B1": {"baarle"}, "B2": {"front", "door"}, "B3": {"story"}}


def _c(s):
    return re.sub(r"[^\w']", "", s).lower()


def build_pages():
    pages = []
    for k in L:
        ws = _TM[LINE_PART[k]].words(k)
        toks, i = [], 0
        merges = [(m.split(), d) for m, d in MERGES.get(k, [])]
        while i < len(ws):
            hit = next(((m, d) for m, d in merges if [_c(x[2]) for x in ws[i:i + len(m)]] == m), None)
            if hit:
                j = i + len(hit[0]) - 1
                punct = re.sub(r"[\w']", "", ws[j][2])
                toks.append((ws[i][0], hit[1] + punct, _c(hit[1]) in KEYS.get(k, set())))
                i = j + 1
            else:
                toks.append((ws[i][0], ws[i][2], _c(ws[i][2]) in KEYS.get(k, set())))
                i += 1
        cur = []
        for n, tk in enumerate(toks):
            cur.append(tk)
            length = len(" ".join(x[1] for x in cur))
            rest = len(toks) - n - 1
            if rest >= 3 and (length > 58 or (tk[1][-1] in ".," and length > 24 and rest > 3)):
                pages.append([k, cur])
                cur = []
        if cur:
            pages.append([k, cur])
    out = []
    for i, (k, toks) in enumerate(pages):
        t0 = toks[0][0] - 0.2
        nxt = pages[i + 1][1][0][0] - 0.2 if i + 1 < len(pages) else TOTAL
        t1 = min(nxt, E(k) + 0.9) if (i + 1 == len(pages) or pages[i + 1][0] != k) else nxt
        out.append((t0, t1, toks))
    return out


PAGES = build_pages()


def captions(c, t, y=1460, size=60, width=940):
    f = font("bold", size)
    sp = f.measureText(" ")
    for t0, t1, toks in PAGES:
        if not (t0 <= t < t1):
            continue
        a = fade(t, t0, 0.15) * (1 - fade(t, t1 - 0.15, 0.15))
        lines, cur = [], []
        for tk in toks:
            trial = " ".join(x[1] for x in cur + [tk])
            if cur and f.measureText(trial) > width:
                lines.append(cur)
                cur = [tk]
            else:
                cur.append(tk)
        lines.append(cur)
        for li, ln in enumerate(lines):
            tot = f.measureText(" ".join(x[1] for x in ln))
            x = (W - tot) / 2
            yy = y + li * size * 1.22
            for ts, s, key in ln:
                said = t >= ts
                rgb = (RED if key else INK) if said else (196, 186, 170)
                if key and said:
                    u = out_cubic(prog(t, ts, ts + 0.25))
                    core = s.rstrip(",.?!")
                    c.drawRect(skia.Rect.MakeLTRB(x - 4, yy + 8, x - 4 + (f.measureText(core) + 8) * u, yy + 16), fillp(RED, 200 * a))
                c.drawString(s, x, yy, f, fillp(rgb, 255 * a))
                x += f.measureText(s) + sp


# ------------------------------------------------------------------ the frame
_GRAIN = None


def draw(c, t):
    c.drawPaint(fillp(PAPER))
    headline_block(c, t)
    card_chrome(c, t)
    i = shot_at(t)
    name, s, e = CUTS[i]
    if i > 0 and t < s + XF:                                   # dissolve from the previous shot
        card_content(c, t, i - 1)
        c.saveLayerAlpha(skia.Rect.MakeLTRB(*MAP), int(255 * smooth(prog(t, s, s + XF))))
        card_content(c, t, i)
        c.restore()
    else:
        card_content(c, t, i)
    card_border(c, t)
    captions(c, t)


def frame(t):
    global _GRAIN
    s = skia.Surface(W, H)
    draw(s.getCanvas(), t)
    img = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
    if t > TOTAL - 0.5:                                       # blend into frame 0 so the loop is seamless
        s0 = skia.Surface(W, H)
        draw(s0.getCanvas(), 0.0)
        img0 = s0.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
        k = smooth(prog(t, TOTAL - 0.5, TOTAL))
        img = (img * (1 - k) + img0 * k).astype(np.uint8)
    if _GRAIN is None:
        _GRAIN = np.random.default_rng(3).normal(0, 6, (H, W, 1)).astype(np.int16)
    return np.clip(img.astype(np.int16) + _GRAIN, 0, 255).astype(np.uint8)


def warm():
    """Build every cached layer once (before forking workers)."""
    for name, s, e in CUTS:
        surf = skia.Surface(W, H)
        draw(surf.getCanvas(), (s + e) / 2)
