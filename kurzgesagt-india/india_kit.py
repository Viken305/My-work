"""India-specific drawing pieces: the map, shaped Indic text, people, rangoli, chakra, diya, chapter badges."""
import json, math, os, struct

import numpy as np
import uharfbuzz as hb

from common import *  # noqa: F401,F403

# ---------------------------------------------------------------- palette (STYLE_GUIDE.md)
INDIGO = (20, 18, 56)
ROYAL = (43, 28, 92)
SAFFRON = (255, 153, 51)
GREEN = (63, 191, 107)
FLAG_GREEN = (19, 136, 8)
CHAKRA = (26, 42, 140)
MARIGOLD = (255, 194, 51)
PEACOCK = (31, 181, 168)
TERRACOTTA = (200, 85, 61)
TURMERIC = (232, 163, 23)
RANI = (229, 64, 126)
MARBLE = (244, 239, 230)
SOMBRE = (91, 88, 112)

FONT_DIR = os.path.join(HERE, "fonts")
SCRIPTS = {"deva": "NotoSansDevanagari", "beng": "NotoSansBengali", "taml": "NotoSansTamil",
           "telu": "NotoSansTelugu", "guru": "NotoSansGurmukhi", "arab": "NotoNaskhArabic"}
_HB, _SK = {}, {}


def indic_text(c, s, x, y, size, script="deva", rgb=WHITE, a=255, align="center"):
    """Text shaped with HarfBuzz (conjuncts, vowel signs, Arabic joining) and drawn as Skia glyphs."""
    path = os.path.join(FONT_DIR, SCRIPTS[script] + "-Bold.ttf")
    if path not in _HB:
        face = hb.Face(hb.Blob.from_file_path(path))
        _HB[path] = (face, hb.Font(face))
        _SK[path] = skia.Typeface.MakeFromFile(path)
    face, hfont = _HB[path]
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(hfont, buf, {})
    sc = size / face.upem
    total = sum(p.x_advance for p in buf.glyph_positions) * sc
    x0 = x - total / 2 if align == "center" else x - total if align == "right" else x
    pts, gl, cx = [], [], 0
    for i, p in zip(buf.glyph_infos, buf.glyph_positions):
        gl.append(i.codepoint)
        pts.append(skia.Point(x0 + (cx + p.x_offset) * sc, y - p.y_offset * sc))
        cx += p.x_advance
    blob = skia.TextBlob.MakeFromPosText(struct.pack("<%dH" % len(gl), *gl), pts, skia.Font(_SK[path], size), skia.TextEncoding.kGlyphID)
    c.drawTextBlob(blob, 0, 0, fill(rgb, a))


# ---------------------------------------------------------------- map (Natural Earth, India point-of-view boundaries)
_GEO = json.load(open(os.path.join(HERE, "data", "south_asia.json")))
LON0, LAT0 = 82.0, 22.0


def geo_xy(lon, lat, cx, cy, s):
    """Simple equirectangular projection centred on India. s = pixels per degree."""
    return cx + (lon - LON0) * s * math.cos(math.radians(LAT0)), cy - (lat - LAT0) * s


def country_path(name, cx, cy, s):
    p = skia.Path()
    for ring in _GEO[name]:
        pts = [geo_xy(lo, la, cx, cy, s) for lo, la in ring]
        p.addPoly([skia.Point(*q) for q in pts], True)
    return p


def draw_india(c, cx, cy, s, rgb=SAFFRON, a=255, glow_a=110, neighbours=True, outline=True, fill_rgb=None):
    if neighbours:
        for n in ("Pakistan", "China", "Nepal", "Bhutan", "Bangladesh", "Sri Lanka", "Myanmar", "Afghanistan"):
            np_ = country_path(n, cx, cy, s)
            c.drawPath(np_, fill((60, 50, 100), 0.55 * a))
            c.drawPath(np_, stroke((110, 96, 160), 2, 0.5 * a))
    p = country_path("India", cx, cy, s)
    if glow_a:
        c.drawPath(p, blur(fill(rgb, glow_a * a / 255), s * 0.6))
    c.drawPath(p, shaded(linear((cx, cy - 15 * s), (cx, cy + 15 * s), [lighten(fill_rgb or rgb, 0.15), darken(fill_rgb or rgb, 0.1)])) if a >= 255 else fill(fill_rgb or rgb, a))
    if outline:
        c.drawPath(p, stroke(lighten(rgb, 0.5), max(1.5, s * 0.08), 0.8 * a))
    return p


# ---------------------------------------------------------------- people (faceless-ish, diverse, series style)
SKINS = [(150, 100, 70), (178, 120, 86), (200, 145, 105), (120, 80, 58), (215, 165, 125), (165, 110, 78)]
OUTFITS = ["sari", "kurta", "turban", "hijab", "shirt", "school", "farmer", "coder"]


def person(c, x, y, h, k=0, t=0.0, a=255, look=(0, 0), wave=0.0):
    """Standing figure, feet at (x, y), height h. k picks skin + outfit deterministically."""
    if a <= 1 or h < 2:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    skin = SKINS[k % len(SKINS)]
    style = OUTFITS[(k * 3 + 1) % len(OUTFITS)]
    cloth = [RANI, PEACOCK, SAFFRON, (90, 120, 220), MARIGOLD, (240, 240, 245), (110, 160, 90), (70, 70, 90)][(k * 5 + 2) % 8]
    r = h * 0.16
    hy = y - h + r
    by = bob(t, h * 0.01, 2.4, k * 0.37)
    c.save()
    c.translate(0, by)
    body = rrect(x - h * 0.17, hy + r * 0.9, h * 0.34, h * 0.62, h * 0.12)
    c.drawRRect(body, fill(cloth))
    if style == "sari":
        c.drawPath(poly([(x - h * 0.17, hy + r * 1.2), (x + h * 0.05, hy + r * 1.0), (x + h * 0.17, y - h * 0.15), (x + h * 0.02, y - h * 0.12)]), fill(lighten(cloth, 0.35)))
    elif style == "kurta":
        c.drawLine(x, hy + r * 1.1, x, hy + r * 2.4, stroke(darken(cloth, 0.25), h * 0.02))
    elif style == "school":
        c.drawPath(poly([(x - h * 0.05, hy + r * 1.0), (x + h * 0.05, hy + r * 1.0), (x, hy + r * 2.0)]), fill(CHAKRA))
    elif style == "farmer":
        c.drawRRect(rrect(x - h * 0.17, y - h * 0.34, h * 0.34, h * 0.2, h * 0.05), fill(WHITE))
    elif style == "coder":
        c.drawRRect(rrect(x - h * 0.12, hy + r * 1.8, h * 0.24, h * 0.14, h * 0.02), fill((200, 205, 220)))
    # legs
    c.drawLine(x - h * 0.07, y - h * 0.08, x - h * 0.07, y, stroke(darken(cloth, 0.4), h * 0.06))
    c.drawLine(x + h * 0.07, y - h * 0.08, x + h * 0.07, y, stroke(darken(cloth, 0.4), h * 0.06))
    # head
    c.drawCircle(x, hy, r, fill(skin))
    if style == "turban":
        c.drawPath(_dome(x, hy - r * 0.15, r * 1.12, r * 0.95), fill(SAFFRON if k % 2 else (230, 60, 60)))
    elif style == "hijab":
        c.drawPath(_dome(x, hy + r * 0.1, r * 1.25, r * 1.25), fill(cloth if cloth != WHITE else PEACOCK))
        c.drawCircle(x, hy + r * 0.1, r * 0.78, fill(skin))
    elif style in ("sari", "school") and k % 2 == 0:
        c.drawPath(_dome(x, hy - r * 0.2, r * 1.05, r * 0.9), fill((30, 22, 30)))
        c.drawCircle(x + r * 0.9, hy + r * 0.1, r * 0.35, fill((30, 22, 30)))
    else:
        c.drawPath(_dome(x, hy - r * 0.25, r * 1.02, r * 0.8), fill((30, 22, 30) if k % 3 else (220, 220, 225)))
    eyes(c, x, hy + r * 0.12, r, t, look, k * 0.13, spread=0.32, size=0.11)
    if wave:
        c.drawLine(x + h * 0.15, hy + r * 1.3, x + h * 0.3, hy - r * (0.2 + 0.4 * wave), stroke(skin, h * 0.06))
    c.restore()
    if a < 255:
        c.restore()


def _dome(x, y, w, h):
    p = skia.Path()
    p.moveTo(x - w, y + h * 0.15)
    p.cubicTo(x - w, y - h * 1.1, x + w, y - h * 1.1, x + w, y + h * 0.15)
    p.close()
    return p


def crowd(c, x0, y0, w, rows, cols, h, t, a=255, highlight=None, seed=0):
    for j in range(rows):
        for i in range(cols):
            k = seed + j * cols + i
            x = x0 + (i + 0.5 * (j % 2)) * w / cols
            y = y0 + j * h * 0.45
            person(c, x, y, h * (0.85 + 0.15 * j / max(1, rows - 1)), k, t, a)
            if highlight and highlight(i, j):
                glow(c, x, y - h * 0.6, h * 0.7, SAFFRON, 120)


# ---------------------------------------------------------------- motifs
def rangoli(c, cx, cy, r, k=1.0, t=0.0, palette=(RANI, MARIGOLD, PEACOCK, SAFFRON, WHITE)):
    """Symmetric rangoli flower; k blooms it from the centre."""
    if k <= 0.01:
        return
    c.save()
    c.translate(cx, cy)
    c.rotate(t * 6)
    rings = [(1.0, 16, palette[0]), (0.78, 12, palette[1]), (0.58, 10, palette[2]), (0.38, 8, palette[3]), (0.2, 6, palette[4])]
    for n, (f, petals, rgb) in enumerate(rings):
        rr = r * f * clamp(k * 1.4 - n * 0.12)
        if rr <= 1:
            continue
        for p in range(petals):
            c.save()
            c.rotate(360 / petals * p + n * 9)
            petal = skia.Path()
            petal.moveTo(0, 0)
            petal.cubicTo(rr * 0.25, -rr * 0.35, rr * 0.25, -rr * 0.8, 0, -rr)
            petal.cubicTo(-rr * 0.25, -rr * 0.8, -rr * 0.25, -rr * 0.35, 0, 0)
            c.drawPath(petal, fill(rgb))
            c.drawCircle(0, -rr * 1.06, rr * 0.05, fill(WHITE, 220))
            c.restore()
    c.drawCircle(0, 0, r * 0.08 * min(1.0, k * 2), fill(WHITE))
    c.restore()


def chakra(c, cx, cy, r, rot=0.0, rgb=CHAKRA, a=255):
    c.drawCircle(cx, cy, r, stroke(rgb, r * 0.09, a))
    c.drawCircle(cx, cy, r * 0.14, fill(rgb, a))
    for k in range(24):
        ang = math.radians(rot + k * 15)
        c.drawLine(cx + r * 0.14 * math.cos(ang), cy + r * 0.14 * math.sin(ang), cx + r * 0.92 * math.cos(ang), cy + r * 0.92 * math.sin(ang), stroke(rgb, r * 0.035, a))
        a2 = math.radians(rot + k * 15 + 7.5)
        c.drawCircle(cx + r * 0.95 * math.cos(a2), cy + r * 0.95 * math.sin(a2), r * 0.035, fill(rgb, a))


def diya(c, x, y, s, t=0.0, a=255):
    glow(c, x, y - s * 0.9, s * 2.2, MARIGOLD, 160 * a / 255)
    flame = skia.Path()
    fl = 1 + 0.1 * math.sin(t * 9 + x)
    flame.moveTo(x, y - s * 1.5 * fl)
    flame.quadTo(x + s * 0.35, y - s * 0.6, x, y - s * 0.35)
    flame.quadTo(x - s * 0.35, y - s * 0.6, x, y - s * 1.5 * fl)
    c.drawPath(flame, fill(MARIGOLD, a))
    bowl = skia.Path()
    bowl.moveTo(x - s, y - s * 0.4)
    bowl.cubicTo(x - s * 0.8, y + s * 0.35, x + s * 0.8, y + s * 0.35, x + s, y - s * 0.4)
    bowl.close()
    c.drawPath(bowl, fill(TERRACOTTA, a))


def petals(c, t, n=40, seed=3, a=1.0):
    """Floating marigold petals (culture-scene dust)."""
    rng = np.random.default_rng(seed)
    base = rng.random((n, 2)) * [W, H]
    sp = rng.uniform(15, 40, n)
    for i in range(n):
        x = (base[i, 0] + 20 * math.sin(t * 0.6 + i)) % W
        y = (base[i, 1] + sp[i] * t) % (H + 40) - 20
        c.save()
        c.translate(x, y)
        c.rotate(t * 40 + i * 30)
        c.drawOval(skia.Rect.MakeXYWH(-7, -4, 14, 8), fill(MARIGOLD if i % 3 else SAFFRON, 200 * a))
        c.restore()


DEVA_DIGITS = "०१२३४५६७८९"


def chapter_badge(c, n, name, rgb, a=255):
    """Top-left chapter pill: Devanagari numeral + English numeral + name."""
    if a <= 2:
        return
    c.saveLayerAlpha(None, int(a))
    x, y = 60, 52
    w = 200 + font(40, 800).measureText(name) + 40
    c.drawRRect(rrect(x, y, w, 96, 48), fill((14, 12, 40), 225))
    c.drawRRect(rrect(x, y, w, 96, 48), stroke(rgb, 3, 200))
    c.drawCircle(x + 48, y + 48, 36, fill(rgb))
    indic_text(c, DEVA_DIGITS[n], x + 48, y + 64, 44, "deva", INK)
    text(c, str(n), x + 104, y + 62, 34, rgb, 255, 800, "left")
    text(c, name, x + 140, y + 62, 34, WHITE, 255, 800, "left", spacing=3)
    c.restore()
