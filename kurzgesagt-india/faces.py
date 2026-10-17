"""Respectful flat-vector portraits of historical and political figures, in the series style.

Rules (STYLE_GUIDE.md): recognisable by real features and attire, neutral expressions, no caricature,
no exaggeration, identical treatment for every figure. "Coming to life" = blinking, breathing, small head
movements and glances only. Mouths never move: we never animate real people saying words.
"""
import math

from india_kit import *  # noqa: F401,F403

LEADERS = {
    "ashoka": dict(name="ASHOKA", years="c. 304–232 BCE", note="ARTISTIC IMPRESSION", skin=(176, 120, 84), tint=TERRACOTTA),
    "gandhi": dict(name="MAHATMA GANDHI", years="1869–1948", skin=(170, 116, 82), tint=SAFFRON),
    "nehru": dict(name="JAWAHARLAL NEHRU", years="1889–1964", skin=(206, 152, 112), tint=PEACOCK),
    "patel": dict(name="SARDAR PATEL", years="1875–1950", skin=(166, 112, 78), tint=MARIGOLD),
    "bose": dict(name="SUBHAS CHANDRA BOSE", years="1897–1945", skin=(198, 142, 102), tint=(120, 150, 90)),
    "ambedkar": dict(name="B. R. AMBEDKAR", years="1891–1956", skin=(146, 98, 68), tint=(90, 120, 230)),
    "modi": dict(name="NARENDRA MODI", years="b. 1950", skin=(192, 138, 98), tint=(150, 140, 200)),
}

INKL = (34, 26, 30)
HAIR_W = (236, 234, 230)


def _shade(rgb, k):
    return mix(rgb, (0, 0, 0), k)


def portrait(c, x, y, s, who, t=0.0, a=255, look=(0.0, 0.0), breathe=True, phase=0.0):
    """Head-and-shoulders portrait. (x, y) = centre of the face, s = face half-width in px."""
    if a <= 1 or s < 2:
        return
    L = LEADERS[who]
    skin = L["skin"]
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    br = 1 + (0.012 * math.sin(t * 1.6 + phase) if breathe else 0)
    tilt = 1.6 * math.sin(t * 0.7 + phase * 2)
    # ---- shoulders / clothing (drawn under the head)
    c.save()
    c.translate(x, y + s * 1.65)
    c.scale(1, br)
    _clothes(c, s, who, t)
    c.restore()
    # neck
    c.drawRRect(rrect(x - s * 0.34, y + s * 0.75, s * 0.68, s * 0.65, s * 0.2), fill(_shade(skin, 0.12)))
    # ---- head (tilts slightly)
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    _back_hair(c, s, who)
    ew = 0.24 if who == "gandhi" else 0.16  # Gandhi's famously large ears
    for sx in (-1, 1):  # ears
        c.drawOval(skia.Rect.MakeXYWH(sx * s * (0.86 + ew * 0.4) - s * ew, -s * 0.22, s * ew * 2, s * (0.46 + ew)), fill(_shade(skin, 0.08)))
    head = skia.Path()
    head.addOval(skia.Rect.MakeXYWH(-s * 0.88, -s * 1.08, s * 1.76, s * 2.1))
    c.drawPath(head, shaded(radial((-s * 0.3, -s * 0.4), s * 1.8, [lighten(skin, 0.12), skin, _shade(skin, 0.12)], [0, 0.6, 1])))
    _face(c, s, who, skin, t, look, phase)
    _front_hair(c, s, who)
    c.restore()
    if a < 255:
        c.restore()


def _face(c, s, who, skin, t, look, phase):
    # eyebrows
    bw = s * (0.09 if who in ("patel",) else 0.06)
    brow = (238, 236, 232) if who in ("gandhi", "patel", "modi") else INKL
    for sx in (-1, 1):
        b = skia.Path()  # gentle arch: calm and neutral, never stern or sad
        b.moveTo(sx * s * 0.17, -s * 0.29)
        b.quadTo(sx * s * 0.34, -s * 0.37, sx * s * 0.51, -s * 0.29)
        c.drawPath(b, stroke(brow, bw))
    # eyes (with blink)
    cyc = (t + phase * 3.1) % 4.3
    open_ = 1.0 - (1.0 - abs(cyc - 4.2) / 0.1 if abs(cyc - 4.2) < 0.1 else 0.0)
    for sx in (-1, 1):
        ex, ey = sx * s * 0.34 + look[0] * s * 0.05, -s * 0.1 + look[1] * s * 0.04
        c.save()
        c.translate(ex, ey)
        c.scale(1, max(0.1, open_))
        c.drawOval(skia.Rect.MakeXYWH(-s * 0.1, -s * 0.075, s * 0.2, s * 0.15), fill(INKL))
        c.drawCircle(-s * 0.03, -s * 0.03, s * 0.028, fill(WHITE, 220))
        c.restore()
    # nose
    c.drawPath(poly([(s * 0.02, -s * 0.02), (s * 0.1, s * 0.3), (-s * 0.06, s * 0.33)], False), stroke(_shade(skin, 0.28), s * 0.045))
    # glasses
    if who in ("gandhi", "bose", "ambedkar"):
        frame = (70, 70, 80) if who != "gandhi" else (150, 140, 120)
        wgt = s * (0.035 if who == "gandhi" else 0.06)
        for sx in (-1, 1):
            c.drawCircle(sx * s * 0.34, -s * 0.1, s * 0.22, stroke(frame, wgt))
        c.drawLine(-s * 0.12, -s * 0.12, s * 0.12, -s * 0.12, stroke(frame, wgt))
        c.drawLine(-s * 0.56, -s * 0.14, -s * 0.84, -s * 0.18, stroke(frame, wgt))
        c.drawLine(s * 0.56, -s * 0.14, s * 0.84, -s * 0.18, stroke(frame, wgt))
    if who == "modi":  # thin rimless rectangular glasses
        for sx in (-1, 1):
            c.drawRRect(rrect(sx * s * 0.34 - s * 0.21, -s * 0.24, s * 0.42, s * 0.28, s * 0.07), stroke((200, 205, 215), s * 0.025, 200))
        c.drawLine(-s * 0.13, -s * 0.14, s * 0.13, -s * 0.14, stroke((200, 205, 215), s * 0.025, 200))
    # beard / moustache
    if who == "modi":
        beard = skia.Path()
        beard.moveTo(-s * 0.84, -s * 0.05)
        beard.cubicTo(-s * 0.84, s * 0.9, -s * 0.35, s * 1.12, 0, s * 1.12)
        beard.cubicTo(s * 0.35, s * 1.12, s * 0.84, s * 0.9, s * 0.84, -s * 0.05)
        beard.cubicTo(s * 0.7, s * 0.45, s * 0.35, s * 0.4, 0, s * 0.42)
        beard.cubicTo(-s * 0.35, s * 0.4, -s * 0.7, s * 0.45, -s * 0.84, -s * 0.05)
        c.drawPath(beard, fill(HAIR_W))
        c.drawPath(_moustache(s, 0.34, 0.44), fill(HAIR_W))
        c.drawLine(-s * 0.14, s * 0.62, s * 0.14, s * 0.62, stroke(_shade(skin, 0.35), s * 0.04))
        return
    if who in ("gandhi", "patel"):
        c.drawPath(_moustache(s, 0.26 if who == "gandhi" else 0.3, 0.42), fill(HAIR_W))
    elif who == "ashoka":
        c.drawPath(_moustache(s, 0.36, 0.44), fill(INKL))
    # mouth: neutral, gentle
    m = skia.Path()
    m.moveTo(-s * 0.2, s * 0.6)
    m.quadTo(0, s * (0.7 if who in ("gandhi", "nehru") else 0.64), s * 0.2, s * 0.6)
    c.drawPath(m, stroke(_shade(skin, 0.4), s * 0.05))


def _moustache(s, w, y):
    p = skia.Path()
    p.moveTo(-s * w, s * (y + 0.08))
    p.cubicTo(-s * w * 0.8, s * (y - 0.08), -s * 0.05, s * (y - 0.1), 0, s * (y - 0.02))
    p.cubicTo(s * 0.05, s * (y - 0.1), s * w * 0.8, s * (y - 0.08), s * w, s * (y + 0.08))
    p.cubicTo(s * w * 0.5, s * (y + 0.02), -s * w * 0.5, s * (y + 0.02), -s * w, s * (y + 0.08))
    return p


def _back_hair(c, s, who):
    if who == "ashoka":
        c.drawOval(skia.Rect.MakeXYWH(-s * 1.0, -s * 1.1, s * 2.0, s * 2.0), fill(INKL))


def _front_hair(c, s, who):
    if who == "gandhi":   # bald, thin white fringe at the sides
        for sx in (-1, 1):
            c.drawPath(poly([(sx * s * 0.84, -s * 0.5), (sx * s * 0.9, -s * 0.2), (sx * s * 0.76, -s * 0.3)]), fill(HAIR_W))
        c.drawOval(skia.Rect.MakeXYWH(-s * 0.4, -s * 0.98, s * 0.5, s * 0.22), fill(WHITE, 40))
    elif who == "patel":  # bald crown, short white hair at the sides
        for sx in (-1, 1):
            c.drawPath(poly([(sx * s * 0.86, -s * 0.62), (sx * s * 0.92, -s * 0.15), (sx * s * 0.72, -s * 0.35), (sx * s * 0.7, -s * 0.66)]), fill(HAIR_W))
    elif who == "nehru":  # white Gandhi cap
        cap = poly([(-s * 0.95, -s * 0.55), (-s * 0.8, -s * 1.12), (s * 0.85, -s * 1.12), (s * 0.95, -s * 0.55)])
        c.drawPath(cap, fill((246, 244, 240)))
        c.drawLine(-s * 0.85, -s * 0.85, s * 0.9, -s * 0.85, stroke((215, 212, 205), s * 0.05))
        c.drawPath(poly([(-s * 0.95, -s * 0.55), (s * 0.95, -s * 0.55), (s * 0.9, -s * 0.66), (-s * 0.9, -s * 0.66)]), fill((225, 222, 216)))
    elif who == "bose":   # khaki peaked military cap
        c.drawPath(poly([(-s * 0.95, -s * 0.6), (-s * 0.85, -s * 1.15), (s * 0.85, -s * 1.15), (s * 0.95, -s * 0.6)]), fill((150, 140, 96)))
        c.drawPath(poly([(-s * 0.98, -s * 0.6), (s * 0.98, -s * 0.6), (s * 0.7, -s * 0.42), (-s * 0.7, -s * 0.42)]), fill((60, 50, 40)))
        c.drawCircle(0, -s * 0.85, s * 0.12, fill(MARIGOLD))
    elif who == "ambedkar":  # black hair, side parting
        p = skia.Path()
        p.moveTo(-s * 0.9, -s * 0.25)
        p.cubicTo(-s * 1.0, -s * 1.3, s * 1.0, -s * 1.35, s * 0.9, -s * 0.3)
        p.cubicTo(s * 0.7, -s * 0.8, s * 0.0, -s * 0.85, -s * 0.35, -s * 0.72)
        p.cubicTo(-s * 0.6, -s * 0.65, -s * 0.8, -s * 0.5, -s * 0.9, -s * 0.25)
        c.drawPath(p, fill(INKL))
        c.drawLine(-s * 0.35, -s * 0.72, -s * 0.2, -s * 1.05, stroke((70, 60, 66), s * 0.03))
    elif who == "modi":   # short white hair, receding at the temples
        p = skia.Path()
        p.moveTo(-s * 0.88, -s * 0.35)
        p.cubicTo(-s * 0.95, -s * 1.3, s * 0.95, -s * 1.3, s * 0.88, -s * 0.35)
        p.cubicTo(s * 0.7, -s * 0.75, s * 0.4, -s * 0.78, s * 0.2, -s * 0.82)
        p.cubicTo(0, -s * 0.86, -s * 0.4, -s * 0.78, -s * 0.7, -s * 0.75)
        p.close()
        c.drawPath(p, fill(HAIR_W))
    elif who == "ashoka":  # crown with jewels
        c.drawPath(poly([(-s * 0.95, -s * 0.62), (-s * 0.9, -s * 1.2), (-s * 0.45, -s * 1.0), (0, -s * 1.38), (s * 0.45, -s * 1.0), (s * 0.9, -s * 1.2), (s * 0.95, -s * 0.62)]), fill(TURMERIC))
        for k, jx in enumerate((-0.5, 0, 0.5)):
            c.drawCircle(s * jx, -s * 0.8, s * 0.09, fill(RANI if k != 1 else PEACOCK))
        for sx in (-1, 1):
            c.drawCircle(sx * s * 0.9, s * 0.3, s * 0.09, fill(TURMERIC))


def _clothes(c, s, who, t):
    """Shoulders + clothing, local origin = top centre of the shoulders."""
    sh = skia.Path()
    sh.moveTo(-s * 1.9, s * 1.6)
    sh.cubicTo(-s * 1.9, s * 0.2, -s * 1.2, -s * 0.2, 0, -s * 0.25)
    sh.cubicTo(s * 1.2, -s * 0.2, s * 1.9, s * 0.2, s * 1.9, s * 1.6)
    sh.close()
    if who == "gandhi":       # white khadi shawl
        c.drawPath(sh, fill((240, 236, 226)))
        for k in range(4):
            c.drawLine(-s * 1.3 + k * s * 0.45, s * 0.1, -s * 1.0 + k * s * 0.55, s * 1.5, stroke((215, 208, 195), s * 0.05))
    elif who == "patel":      # white kurta + shawl
        c.drawPath(sh, fill((242, 240, 234)))
        c.drawPath(poly([(-s * 1.9, s * 1.6), (-s * 1.5, 0), (-s * 0.5, -s * 0.1), (s * 0.3, s * 1.6)]), fill((226, 220, 206)))
    elif who == "nehru":      # achkan with high collar + rose
        c.drawPath(sh, fill((214, 196, 160)))
        c.drawRRect(rrect(-s * 0.42, -s * 0.3, s * 0.84, s * 0.35, s * 0.1), fill((200, 180, 142)))
        for k in range(3):
            c.drawCircle(0, s * 0.25 + k * s * 0.4, s * 0.06, fill((150, 130, 100)))
        c.drawCircle(-s * 0.8, s * 0.45, s * 0.16, fill((220, 50, 70)))
        c.drawPath(poly([(-s * 0.8, s * 0.55), (-s * 0.7, s * 0.8), (-s * 0.9, s * 0.8)]), fill((60, 150, 80)))
    elif who == "bose":       # khaki uniform
        c.drawPath(sh, fill((150, 140, 96)))
        c.drawPath(poly([(-s * 0.45, -s * 0.25), (0, s * 0.45), (s * 0.45, -s * 0.25), (s * 0.25, -s * 0.3), (0, s * 0.15), (-s * 0.25, -s * 0.3)]), fill((130, 120, 80)))
        for k in range(3):
            c.drawCircle(0, s * 0.6 + k * s * 0.35, s * 0.06, fill(MARIGOLD))
    elif who == "ambedkar":   # blue suit, white shirt, tie
        c.drawPath(sh, fill((50, 70, 160)))
        c.drawPath(poly([(-s * 0.5, -s * 0.25), (0, s * 1.6), (s * 0.5, -s * 0.25)]), fill(WHITE))
        c.drawPath(poly([(-s * 0.1, -s * 0.15), (s * 0.1, -s * 0.15), (s * 0.16, s * 1.2), (0, s * 1.4), (-s * 0.16, s * 1.2)]), fill((170, 40, 60)))
        c.drawPath(poly([(-s * 0.5, -s * 0.25), (-s * 0.1, s * 0.9), (-s * 0.7, s * 0.2)]), fill((40, 56, 130)))
        c.drawPath(poly([(s * 0.5, -s * 0.25), (s * 0.1, s * 0.9), (s * 0.7, s * 0.2)]), fill((40, 56, 130)))
    elif who == "modi":       # white kurta + sleeveless high-collar vest (neutral grey)
        c.drawPath(sh, fill((244, 242, 238)))
        vest = skia.Path()
        vest.moveTo(-s * 1.25, s * 1.6)
        vest.cubicTo(-s * 1.3, s * 0.4, -s * 0.9, -s * 0.05, -s * 0.42, -s * 0.2)
        vest.lineTo(s * 0.42, -s * 0.2)
        vest.cubicTo(s * 0.9, -s * 0.05, s * 1.3, s * 0.4, s * 1.25, s * 1.6)
        vest.close()
        c.drawPath(vest, fill((132, 136, 150)))
        c.drawRRect(rrect(-s * 0.42, -s * 0.3, s * 0.84, s * 0.3, s * 0.08), fill((118, 122, 136)))
        c.drawLine(0, 0, 0, s * 1.6, stroke((105, 108, 122), s * 0.05))
        c.drawRRect(rrect(-s * 0.95, s * 0.55, s * 0.4, s * 0.08, s * 0.03), fill((105, 108, 122)))
    elif who == "ashoka":     # draped royal robe + necklace
        c.drawPath(sh, fill((200, 110, 70)))
        c.drawPath(poly([(-s * 1.9, s * 1.6), (-s * 1.0, -s * 0.1), (s * 0.2, s * 1.6)]), fill(TURMERIC))
        neck = skia.Path()
        neck.addArc(skia.Rect.MakeXYWH(-s * 0.6, -s * 0.6, s * 1.2, s * 1.1), 20, 140)
        c.drawPath(neck, stroke(MARIGOLD, s * 0.08))


def leader_card(c, cx, cy, who, t=0.0, scale=1.0, a=255, look=(0.0, 0.0), phase=0.0, show_name=True):
    """Portrait inside a rounded card with name + years (same style for every figure)."""
    if a <= 1 or scale <= 0.01:
        return
    L = LEADERS[who]
    w, h = 340 * scale, 420 * scale
    c.saveLayerAlpha(None, int(a))
    rr = rrect(cx - w / 2, cy - h / 2, w, h, 30 * scale)
    c.save()
    c.translate(10 * scale, 18 * scale)
    c.drawRRect(rr, blur(fill((5, 4, 20), 120), 20 * scale))
    c.restore()
    c.drawRRect(rr, shaded(radial((cx, cy - h * 0.15), h * 0.8, [mix(INDIGO, L["tint"], 0.45), mix(INDIGO, L["tint"], 0.15)])))
    c.save()
    c.clipRRect(rr, doAntiAlias=True)
    glow(c, cx, cy - h * 0.12, w * 0.6, L["tint"], 70)
    portrait(c, cx, cy - h * 0.2, 64 * scale, who, t, 255, look, phase=phase)
    c.restore()
    c.drawRRect(rr, stroke(lighten(L["tint"], 0.4), 3 * scale, 160))
    if show_name:
        c.drawRRect(rrect(cx - w / 2, cy + h / 2 - 96 * scale, w, 96 * scale, 0), fill((10, 8, 30), 170))
        ns = min(24.0, 24.0 * (w - 30 * scale) / (font(24 * scale, 800).measureText(L["name"]) + 2 * scale * len(L["name"]) + 1e-6) / scale) * scale
        text(c, L["name"], cx, cy + h / 2 - 54 * scale, ns, WHITE, 255, 800, spacing=ns / 12)
        text(c, L["years"], cx, cy + h / 2 - 22 * scale, 20 * scale, lighten(L["tint"], 0.3), 230, 600, spacing=1.5 * scale)
        if "note" in L:
            text(c, L["note"], cx, cy - h / 2 + 30 * scale, 14 * scale, WHITE, 170, 800, spacing=2 * scale)
    c.restore()


def gandhi_walking(c, x, y, h, t, a=255):
    """Side-view Gandhi on the Salt March: shawl, walking staff, steady stride."""
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    skin = LEADERS["gandhi"]["skin"]
    st = math.sin(t * 4.0)
    for k, sgn in ((0, 1), (1, -1)):  # legs
        ang = 0.35 * st * sgn
        c.drawLine(x, y - h * 0.42, x + math.sin(ang) * h * 0.42, y - h * 0.42 + math.cos(ang) * h * 0.42, stroke(_shade(skin, 0.1 * k), h * 0.05))
    c.drawPath(poly([(x - h * 0.12, y - h * 0.72), (x + h * 0.14, y - h * 0.72), (x + h * 0.16, y - h * 0.38), (x - h * 0.14, y - h * 0.38)]), fill((240, 236, 226)))
    c.drawPath(poly([(x - h * 0.13, y - h * 0.74), (x + h * 0.16, y - h * 0.74), (x + h * 0.02, y - h * 0.45)]), fill((226, 220, 206)))
    c.drawLine(x + h * 0.26, y - h * 0.9, x + h * 0.3 + 0.03 * h * st, y, stroke((150, 110, 70), h * 0.025))
    c.drawLine(x + h * 0.1, y - h * 0.66, x + h * 0.27, y - h * 0.6, stroke(skin, h * 0.04))
    c.drawCircle(x + h * 0.03, y - h * 0.84, h * 0.1, fill(skin))
    c.drawCircle(x + h * 0.11, y - h * 0.85, h * 0.035, stroke((150, 140, 120), h * 0.01))
    if a < 255:
        c.restore()


if __name__ == "__main__":
    # faces test sheet -> out/storyboards/faces.png
    from PIL import Image
    os.makedirs(os.path.join(HERE, "out", "storyboards"), exist_ok=True)
    s = skia.Surface(W, H)
    c = s.getCanvas()
    background(c, INDIGO, ROYAL)
    order = ["ashoka", "gandhi", "nehru", "patel", "bose", "ambedkar", "modi"]
    for i, who in enumerate(order):
        cx = 260 + (i % 4) * 466 if i < 4 else 493 + (i - 4) * 466
        cy = 300 if i < 4 else 790
        leader_card(c, cx, cy, who, 1.0, 1.05)
    vignette(c, 90)
    out = os.path.join(HERE, "out", "storyboards", "faces.png")
    Image.fromarray(finish(s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType), 1.0)).save(out)
    print(out)
