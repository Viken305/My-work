"""PAPER ATLAS: the simple style for "Why Borders Are Shaped the Way They Are".

Cream paper, pale flat countries with thin ink coastlines, ONE red line for the border the shot is about, a blue
river where nature drew it. A section tag and a serif headline sit on top, the map card in the middle, the caption
under it in plain bold type with the key word in red. Hand-written notes (Caveat) for callouts.
"""
import math, os

import numpy as np
import skia

import geo

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
PAPER = (243, 236, 222)
CARD = (250, 246, 236)
INK = (40, 38, 48)
GREY = (150, 144, 136)
SEA = (208, 224, 222)
RED = (206, 58, 44)
BLUE = (60, 120, 186)
# pale map fills (picked by Natural Earth MAPCOLOR7 so neighbours differ)
FILLS = [(234, 214, 168), (196, 214, 178), (232, 190, 178), (190, 206, 226), (222, 200, 226), (238, 226, 190), (204, 222, 206)]
MAP = (60, 420, 1020, 1340)            # the map card
FONTS = {"serif": "DMSerifDisplay.ttf", "bold": "Atkinson-Bold.ttf", "reg": "Atkinson-Regular.ttf",
         "mono": "MartianMono-Regular.ttf", "monob": "MartianMono-Bold.ttf", "hand": "Caveat.ttf"}
_TF = {}


def font(kind, size):
    if kind not in _TF:
        _TF[kind] = skia.Typeface.MakeFromFile(os.path.join(HERE, "fonts", FONTS[kind]))
    f = skia.Font(_TF[kind], size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def fillp(rgb, a=255):
    return skia.Paint(AntiAlias=True, Color=skia.Color(*rgb, int(a)))


def strokep(rgb, w, a=255, dash=None, cap=skia.Paint.kRound_Cap):
    p = skia.Paint(AntiAlias=True, Color=skia.Color(*rgb, int(a)), Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                   StrokeCap=cap, StrokeJoin=skia.Paint.kRound_Join)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(dash, 0))
    return p


def text(c, s, x, y, size, kind="bold", rgb=INK, align="left", a=255, tracking=0.0):
    f = font(kind, size)
    w = sum(f.measureText(ch) + tracking * size for ch in s) - tracking * size if tracking else f.measureText(s)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    if tracking:
        for ch in s:
            c.drawString(ch, x0, y, f, fillp(rgb, a))
            x0 += f.measureText(ch) + tracking * size
    else:
        c.drawString(s, x0, y, f, fillp(rgb, a))
    return w


def halo_text(c, s, x, y, size, kind="mono", rgb=INK, align="center", tracking=0.12):
    """Map label with a paper halo so it reads over lines."""
    f = font(kind, size)
    w = sum(f.measureText(ch) + tracking * size for ch in s) - tracking * size
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    halo = strokep(CARD, size * 0.28)
    xx = x0
    for ch in s:
        c.drawString(ch, xx, y, f, halo)
        xx += f.measureText(ch) + tracking * size
    xx = x0
    for ch in s:
        c.drawString(ch, xx, y, f, fillp(rgb))
        xx += f.measureText(ch) + tracking * size


# ------------------------------------------------------------------ page furniture
def page(c, num, section, headline):
    c.drawPaint(fillp(PAPER))
    text(c, f"No. {num}  ·  {section.upper()}", 70, 250, 30, "monob", RED, tracking=0.08)
    text(c, headline, 66, 345, 78, "serif", INK)


def card(c):
    x0, y0, x1, y1 = MAP
    c.drawRect(skia.Rect.MakeLTRB(x0 + 8, y0 + 10, x1 + 8, y1 + 10), fillp((0, 0, 0), 22))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), fillp(SEA))


def card_frame(c, scale_km=None, view=None):
    x0, y0, x1, y1 = MAP
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), strokep(INK, 3))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 10, y0 + 10, x1 - 10, y1 - 10), strokep(INK, 1, 120))
    # north arrow
    nx, ny = x1 - 60, y0 + 70
    c.drawPath(_poly([(nx, ny - 34), (nx + 14, ny + 10), (nx, ny), (nx - 14, ny + 10)]), fillp(INK))
    text(c, "N", nx, ny + 44, 24, "monob", INK, "center")
    if scale_km and view:                              # scale bar from the view's own scale
        lat = (view.raw(0, 0)[1])
        px_per_deg = view.s * 1.0
        km_per_deg = 111.32 * view.k if view.proj == "local" else 111.32
        L = scale_km / km_per_deg * px_per_deg
        sx, sy = x0 + 40, y1 - 44
        for i in range(4):
            c.drawRect(skia.Rect.MakeLTRB(sx + L * i / 4, sy, sx + L * (i + 1) / 4, sy + 10), fillp(INK if i % 2 == 0 else CARD))
        c.drawRect(skia.Rect.MakeLTRB(sx, sy, sx + L, sy + 10), strokep(INK, 2))
        text(c, f"{scale_km:,} km", sx + L + 14, sy + 12, 22, "mono", INK)


def caption(c, words, key=(), y=1460, size=60, width=940):
    """Plain bold caption; words in `key` are red and underlined. Wraps to lines that fit `width`."""
    f = font("bold", size)
    lines, cur = [], []
    for w in words.split():
        trial = " ".join(cur + [w])
        if cur and f.measureText(trial) > width:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    lines.append(cur)
    sp = f.measureText(" ")
    for li, ln in enumerate(lines):
        tot = f.measureText(" ".join(ln))
        x = (W - tot) / 2
        yy = y + li * size * 1.22
        for w in ln:
            is_key = w.strip(",.").lower() in key
            wd = f.measureText(w)
            if is_key:
                c.drawRect(skia.Rect.MakeLTRB(x - 4, yy + 8, x + f.measureText(w.strip(",.")) + 4, yy + 16), fillp(RED, 200))
            c.drawString(w, x, yy, f, fillp(RED if is_key else INK))
            x += wd + sp


def hand(c, s, x, y, size=56, rgb=RED, align="center", rot=0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    text(c, s, 0, 0, size, "hand", rgb, align)
    c.restore()


def _poly(pts, closed=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def arrow(c, pts, rgb=RED, w=5, head=22, dash=None):
    p = skia.Path()
    p.moveTo(*pts[0])
    if len(pts) == 3:
        p.quadTo(*pts[1], *pts[2])
    else:
        for q in pts[1:]:
            p.lineTo(*q)
    c.drawPath(p, strokep(rgb, w, dash=dash))
    (ax, ay), (bx, by) = pts[-2], pts[-1]
    ang = math.atan2(by - ay, bx - ax)
    tip = [(bx, by), (bx - head * math.cos(ang - 0.45), by - head * math.sin(ang - 0.45)),
           (bx - head * math.cos(ang + 0.45), by - head * math.sin(ang + 0.45))]
    c.drawPath(_poly(tip), fillp(rgb))


def ring(c, x, y, rx, ry, rgb=RED, w=5, rot=-8):
    """A hand-drawn loop around a spot."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    p = skia.Path()
    for i in range(0, 73):
        a = i / 64 * 2 * math.pi
        r = 1 + 0.04 * math.sin(a * 3)
        q = (rx * r * math.cos(a), ry * r * math.sin(a))
        (p.moveTo if i == 0 else p.lineTo)(*q)
    c.drawPath(p, strokep(rgb, w))
    c.restore()


# ------------------------------------------------------------------ map layers
def draw_countries(c, view, colors=None, default=None, borders=True, lw=1.6):
    """Fill every country in the view (pale palette, or colors[a3]); coastline ink, borders thin grey."""
    x0, y0, x1, y1 = MAP
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    paths = []
    for f in geo.countries():
        a3 = f["properties"]["ADM0_A3"]
        p = view.path(f["geometry"])
        b = p.getBounds()
        if b.right() < x0 or b.left() > x1 or b.bottom() < y0 or b.top() > y1:
            continue
        rgb = (colors or {}).get(a3) or default or FILLS[(f["properties"]["MAPCOLOR7"] - 1) % len(FILLS)]
        c.drawPath(p, fillp(rgb))
        paths.append(p)
    if borders:
        for p in paths:
            c.drawPath(p, strokep(INK, lw, 150))
    c.restore()


def draw_rivers(c, view, names, w=6, rgb=BLUE):
    x0, y0, x1, y1 = MAP
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    for f in geo.rivers(*names):
        for r in geo.rings(f["geometry"]):
            c.drawPath(view.line(r), strokep(rgb, w))
    c.restore()


def draw_border(c, view, a, b, w=9, rgb=RED):
    """The border between countries a and b, from the land-boundary lines, in the accent colour."""
    x0, y0, x1, y1 = MAP
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    for f in geo.load("ne_10m_admin_0_boundary_lines_land"):
        pr = f["properties"]
        if {pr["ADM0_A3_L"], pr["ADM0_A3_R"]} == {a, b}:
            for r in geo.rings(f["geometry"]):
                c.drawPath(view.line(r), strokep(rgb, w))
    c.restore()


def grain(img, amount=7.0, seed=1):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amount, img.shape[:2])[..., None]
    out = img.astype(np.float32)
    out[..., :3] += n
    return np.clip(out, 0, 255).astype(np.uint8)
