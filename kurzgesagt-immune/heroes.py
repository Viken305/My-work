"""Hero character concepts + the new organic 'inside the body' environment.

Concepts (pick one as the guide of the video):
  PIP  - a rookie neutrophil in an oversized helmet: small, brave, first into every fight.
  KAI  - a killer T cell commando: receptor 'crown', bandana, cool and precise.
  DOT  - a red blood cell courier: travels everywhere in the blood with an oxygen-bubble backpack, sees the whole war.
"""
import math

import numpy as np

from cells import *  # noqa: F401,F403
from cells import face as _face  # noqa: F401

# ---------------------------------------------------------------- organic environment
TISSUE_BG = (150, 38, 62)
_TISSUE_CACHE = {}


def _tissue_layer(seed, spacing, base, nucleus, blur_r, w=W * 2, h=H * 2):
    """Packed living cells (jittered grid -> rounded blobs with nuclei) rendered once into an image."""
    key = (seed, spacing, base, blur_r)
    if key in _TISSUE_CACHE:
        return _TISSUE_CACHE[key]
    s = skia.Surface(int(w), int(h))
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    rng = np.random.default_rng(seed)
    cols, rows = int(w / spacing) + 2, int(h / spacing) + 2
    for j in range(rows):
        for i in range(cols):
            x = (i + 0.5 * (j % 2)) * spacing + rng.uniform(-0.18, 0.18) * spacing
            y = j * spacing * 0.86 + rng.uniform(-0.18, 0.18) * spacing
            rr = spacing * rng.uniform(0.5, 0.6)
            rad = [rr * (1 + 0.1 * math.sin(k * 1.9 + rng.uniform(0, 6))) for k in range(9)]
            p = blob_path(x, y, rad, rng.uniform(0, 6))
            tone = rng.uniform(-0.08, 0.1)
            col_ = lighten(base, tone) if tone > 0 else darken(base, -tone)
            paint = shaded(radial((x - rr * 0.3, y - rr * 0.35), rr * 1.5, [lighten(col_, 0.18), col_, darken(col_, 0.25)], [0, 0.55, 1]))
            if blur_r:
                paint.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur_r))
            c.drawPath(p, paint)
            st = stroke(darken(base, 0.35), max(1.5, spacing * 0.025), 200)
            if blur_r:
                st.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur_r))
            c.drawPath(p, st)
            nr = rr * rng.uniform(0.26, 0.34)
            np_ = fill(nucleus, 210)
            if blur_r:
                np_.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur_r))
            c.drawCircle(x + rng.uniform(-0.15, 0.15) * rr, y + rng.uniform(-0.15, 0.15) * rr, nr, np_)
            if not blur_r:
                c.drawOval(skia.Rect.MakeXYWH(x - rr * 0.55, y - rr * 0.7, rr * 0.5, rr * 0.22), fill(WHITE, 40))
    img = s.makeImageSnapshot()
    _TISSUE_CACHE[key] = img
    return img


def body_world(c, t, cam=None, a=1.0, mood="warm"):
    """Inside living tissue: a far wall of packed cells (soft), a mid layer, warm light, drifting plasma specks.
    Bright and fleshy on purpose so it never reads as outer space."""
    cam = cam or Cam()
    base = {"warm": (196, 70, 92), "cool": (120, 90, 170)}[mood]
    c.drawPaint(fill(darken(base, 0.35)))
    far = _tissue_layer(41, 150, darken(base, 0.12), darken(base, 0.45), 6)
    cam.push(c, 0.35)
    c.drawImage(far, -far.width() / 2 + 20 * math.sin(t * 0.1), -far.height() / 2)
    cam.pop(c)
    # haze between layers = depth (fluid between cells)
    c.drawPaint(fill(darken(base, 0.3), 120))
    mid = _tissue_layer(43, 260, base, darken(base, 0.4), 0)
    cam.push(c, 0.6)
    c.drawImage(mid, -mid.width() / 2, -mid.height() / 2 + 300)
    cam.pop(c)
    # gap in the tissue where the action happens: soft glowing fluid
    c.drawPaint(shaded(radial((W / 2, H * 0.5), W * 0.62, [(lighten(base, 0.25), 150), (base, 70), (base, 0)], [0, 0.5, 1])))
    _MOTES_B.draw(c, t, cam, a, flow=(20.0, -4.0))


_MOTES_B = Motes(5, 120, (255, 220, 210))


# ---------------------------------------------------------------- PIP, the rookie neutrophil
PIP_BODY = (228, 214, 244)
PIP_SHADE = (176, 150, 214)
HELMET = (86, 116, 104)


def pip(c, x, y, r, t, expr="determined", look=(0.0, 0.0), vel=(0.0, 0.0), arm_l=0.0, arm_r=0.0, a=255, rim=(255, 150, 160), helmet_tilt=0.0):
    """PIP: round, squishy, oversized helmet that wobbles, two stubby arms (arm_l/arm_r: -1 down .. 1 raised)."""
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    sp = math.hypot(*vel)
    st = 1 + clamp(sp / 2400, 0, 0.16)
    c.save()
    c.translate(x, y + bob(t, r * 0.04, 1.6))
    if sp > 1:
        an = math.degrees(math.atan2(vel[1], vel[0]))
        c.rotate(an)
        c.scale(st, 1 / st)
        c.rotate(-an)
    sq = 1 + 0.03 * math.sin(t * 3.2)
    c.scale(sq, 1 / sq)
    c.drawCircle(r * 0.08, r * 0.14, r * 1.02, blur(fill((60, 0, 20), 90), r * 0.12))
    # arms
    for side, lift in ((-1, arm_l), (1, arm_r)):
        c.save()
        c.translate(side * r * 0.86, r * 0.18)
        c.rotate(side * (30 - 110 * lift) + 4 * math.sin(t * 3 + side))
        c.drawRRect(rrect(-r * 0.15, 0, r * 0.3, r * 0.52, r * 0.15), fill(PIP_SHADE))
        c.drawCircle(0, r * 0.5, r * 0.17, fill(PIP_BODY))
        c.drawCircle(0, r * 0.5, r * 0.17, stroke(darken(PIP_SHADE, 0.25), r * 0.03))
        c.restore()
    body = skia.Path()
    body.addCircle(0, 0, r)
    c.drawPath(body, shaded(radial((-r * 0.35, -r * 0.3), r * 1.6, [(246, 240, 252), PIP_BODY, PIP_SHADE], [0, 0.45, 1])))
    c.save()
    c.clipPath(body, doAntiAlias=True)
    rng = np.random.default_rng(2)
    for k in range(14):
        c.drawCircle(rng.uniform(-0.75, 0.75) * r, rng.uniform(0.1, 0.8) * r, r * 0.025, fill(PIP_SHADE, 160))
    rp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.2, Shader=linear((-r, -r), (r, r), [(rim, 20), (rim, 140)]))
    rp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.06))
    rp.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(body, rp)
    c.restore()
    c.drawPath(body, stroke(darken(PIP_SHADE, 0.3), r * 0.04))
    _face(c, look[0] * r * 0.1, r * 0.02 + look[1] * r * 0.05, r * 1.1, t, expr, look, True, 0.3)
    # oversized helmet with strap, wobbling with a little lag
    c.save()
    c.rotate(-8 + helmet_tilt + 4 * math.sin(t * 3.2 - 0.6))
    for sd in (-1, 1):   # chin strap hugging the outline, clear of the eyes
        strap = skia.Path()
        strap.addArc(skia.Rect.MakeXYWH(-r * 0.97, -r * 0.97, r * 1.94, r * 1.94), 90 - sd * 70 if sd > 0 else 90 + 70, 55 * (-1 if sd > 0 else 1))
        c.drawPath(strap, stroke(darken(HELMET, 0.3), r * 0.06))
    dome = skia.Path()
    dome.addArc(skia.Rect.MakeXYWH(-r * 0.98, -r * 1.25, r * 1.96, r * 1.6), 180, 180)
    dome.close()
    c.drawPath(dome, shaded(linear((0, -r * 1.25), (0, -r * 0.45), [lighten(HELMET, 0.3), HELMET])))
    c.drawRRect(rrect(-r * 1.08, -r * 0.5, r * 2.16, r * 0.2, r * 0.1), fill(darken(HELMET, 0.2)))
    c.drawOval(skia.Rect.MakeXYWH(-r * 0.55, -r * 1.12, r * 0.55, r * 0.22), fill(WHITE, 70))
    c.drawCircle(r * 0.42, -r * 0.82, r * 0.12, fill((255, 230, 140)))   # little badge
    c.drawPath(poly([(r * 0.42 + r * 0.08 * math.cos(math.radians(-90 + k * 72)) * (1 if k % 2 == 0 else 0.45),
                      -r * 0.82 + r * 0.08 * math.sin(math.radians(-90 + k * 72)) * (1 if k % 2 == 0 else 0.45)) for k in range(10)]), fill((200, 140, 40)))
    c.restore()
    c.restore()
    if a < 255:
        c.restore()


# ---------------------------------------------------------------- KAI, the killer T cell commando
KAI_BODY = (255, 104, 84)


def kai(c, x, y, r, t, expr="determined", look=(0.0, 0.0), vel=(0.0, 0.0), a=255, rim=(255, 200, 150)):
    """KAI: round red-orange cell, a crown of receptor 'locks' like spiky hair, bandana with flowing tails, scar."""
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    c.save()
    c.translate(x, y + bob(t, r * 0.03, 2.2))
    c.drawCircle(r * 0.08, r * 0.14, r * 1.02, blur(fill((60, 0, 20), 90), r * 0.12))
    # receptor crown: longer on top like a hairdo
    for k in range(17):
        an = math.radians(-180 + k * (360 / 17))
        ln = r * (0.32 if math.sin(an) < -0.3 else 0.16)
        bx, by = math.cos(an) * r * 0.95, math.sin(an) * r * 0.95
        ex, ey = math.cos(an) * (r + ln), math.sin(an) * (r + ln) + 0.04 * r * math.sin(t * 3 + k)
        c.drawLine(bx, by, ex, ey, stroke(darken(KAI_BODY, 0.3), r * 0.08))
        cup = skia.Path()
        cup.addArc(skia.Rect.MakeXYWH(ex - r * 0.09, ey - r * 0.09, r * 0.18, r * 0.18), math.degrees(an) + 90, 180)
        c.drawPath(cup, stroke((255, 220, 120), r * 0.05))
    body = skia.Path()
    body.addCircle(0, 0, r)
    c.drawPath(body, shaded(radial((-r * 0.35, -r * 0.3), r * 1.6, [lighten(KAI_BODY, 0.3), KAI_BODY, darken(KAI_BODY, 0.35)], [0, 0.45, 1])))
    c.save()
    c.clipPath(body, doAntiAlias=True)
    c.drawCircle(r * 0.15, r * 0.3, r * 0.6, fill(darken(KAI_BODY, 0.4), 50))
    rp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.2, Shader=linear((-r, -r), (r, r), [(rim, 20), (rim, 140)]))
    rp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.06))
    rp.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(body, rp)
    band = skia.Path()
    band.moveTo(-r * 1.1, -r * 0.55)
    band.quadTo(0, -r * 0.78, r * 1.1, -r * 0.55)
    band.lineTo(r * 1.1, -r * 0.3)
    band.quadTo(0, -r * 0.52, -r * 1.1, -r * 0.3)
    band.close()
    c.drawPath(band, fill((34, 30, 56)))
    c.restore()
    c.drawPath(body, stroke(darken(KAI_BODY, 0.45), r * 0.04))
    for k in (0, 1):   # bandana tails flutter
        p = skia.Path()
        p.moveTo(r * 0.92, -r * 0.45)
        for j in range(1, 7):
            u = j / 6
            p.lineTo(r * (0.92 + 0.55 * u), -r * 0.45 + r * (0.12 + 0.18 * k) * u + r * 0.08 * math.sin(t * 7 - u * 4 + k))
        c.drawPath(p, stroke((34, 30, 56), r * (0.13 - 0.06 * u)))
    c.drawLine(-r * 0.62, -r * 0.05, -r * 0.42, r * 0.22, stroke(darken(KAI_BODY, 0.5), r * 0.035, 160))   # scar
    _face(c, look[0] * r * 0.1, r * 0.02 + look[1] * r * 0.05, r * 1.05, t, expr, look, True, 1.1)
    c.restore()
    if a < 255:
        c.restore()


# ---------------------------------------------------------------- DOT, the red blood cell courier
DOT_BODY = (232, 52, 66)


def dot(c, x, y, r, t, expr="happy", look=(0.0, 0.0), vel=(0.0, 0.0), turn=0.25, a=255, rim=(255, 200, 190), arm_l=0.0, arm_r=0.0):
    """DOT: a biconcave disc seen at an angle (turn 0 face-on .. 1 edge-on), oxygen-bubble backpack, little arms."""
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    sp = math.hypot(*vel)
    c.save()
    c.translate(x, y + bob(t, r * 0.04, 2.0))
    c.rotate(clamp(vel[0] / 900, -1, 1) * 10 + 4 * math.sin(t * 1.4))
    sq = max(0.55, 1 - 0.45 * turn)
    c.drawOval(skia.Rect.MakeXYWH(-r + r * 0.08, -r * sq * 0.92 + r * 0.16, r * 2, r * 2 * sq * 0.92), blur(fill((60, 0, 20), 90), r * 0.12))
    # backpack: oxygen bubbles in a strap net, peeking out behind
    for k, (bx, by, br) in enumerate([(-0.95, -0.55, 0.3), (-1.1, -0.15, 0.24), (-0.8, -0.95, 0.2)]):
        cx_, cy_ = bx * r, by * r * sq + 0.03 * r * math.sin(t * 2 + k)
        c.drawCircle(cx_, cy_, br * r, shaded(radial((cx_ - br * r * 0.3, cy_ - br * r * 0.3), br * r * 1.3, [(255, 255, 255), (190, 230, 255), (120, 170, 230)])))
        c.drawCircle(cx_, cy_, br * r, stroke((90, 130, 200), r * 0.025))
        text(c, "O₂", cx_, cy_ + br * r * 0.25, br * r * 0.7, (60, 90, 160), 220, 800)
    c.drawLine(-r * 0.9, -r * 0.7 * sq, -r * 0.2, -r * 0.92 * sq, stroke((120, 70, 40), r * 0.06))
    for side, lift in ((-1, arm_l), (1, arm_r)):
        c.save()
        c.translate(side * r * 0.92, r * 0.25 * sq)
        c.rotate(side * (35 - 110 * lift) + 5 * math.sin(t * 3 + side))
        c.drawRRect(rrect(-r * 0.11, 0, r * 0.22, r * 0.42, r * 0.11), fill(darken(DOT_BODY, 0.25)))
        c.drawCircle(0, r * 0.42, r * 0.13, fill(DOT_BODY))
        c.restore()
    c.scale(1, sq)
    disc = skia.Path()
    disc.addCircle(0, 0, r)
    c.drawPath(disc, shaded(radial((-r * 0.35, -r * 0.4), r * 1.6, [lighten(DOT_BODY, 0.35), DOT_BODY, darken(DOT_BODY, 0.4)], [0, 0.5, 1])))
    # the dimple (biconcave centre)
    c.drawCircle(0, r * 0.04, r * 0.62, shaded(radial((-r * 0.12, -r * 0.1), r * 0.66, [darken(DOT_BODY, 0.42), darken(DOT_BODY, 0.2), (DOT_BODY, 0)], [0, 0.65, 1])))
    ring = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.16, Shader=linear((0, -r), (0, r), [(lighten(DOT_BODY, 0.4), 200), (lighten(DOT_BODY, 0.1), 60)]))
    ring.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.05))
    c.drawCircle(0, 0, r * 0.74, ring)
    c.save()
    c.clipPath(disc, doAntiAlias=True)
    rp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.2, Shader=linear((-r, -r), (r, r), [(rim, 20), (rim, 140)]))
    rp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.06))
    rp.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(disc, rp)
    c.restore()
    c.drawPath(disc, stroke(darken(DOT_BODY, 0.45), r * 0.04))
    c.drawOval(skia.Rect.MakeXYWH(-r * 0.62, -r * 0.82, r * 0.55, r * 0.24), fill(WHITE, 90))
    c.scale(1, 1 / sq)
    _face(c, look[0] * r * 0.1, -r * 0.02 * sq + look[1] * r * 0.05, r * 1.0, t, expr, look, True, 2.0)
    c.restore()
    if a < 255:
        c.restore()


if __name__ == "__main__":
    import os
    from PIL import Image

    def sheet(c, t):
        body_world(c, t)
        c.drawPaint(fill((40, 6, 18), 70))
        text(c, "PICK THE HERO", 960, 96, 64, WHITE, 255, 800, spacing=10)
        text(c, "THREE CHARACTER CONCEPTS · SET INSIDE THE BODY", 960, 146, 20, (255, 210, 200), 230, 800, spacing=5)
        cols = [(330, "PIP", "THE ROOKIE NEUTROPHIL", "SMALL, BRAVE, FIRST INTO EVERY FIGHT", (240, 228, 252)),
                (960, "KAI", "THE KILLER T CELL", "COOL, PRECISE SPECIAL FORCES", (255, 150, 120)),
                (1590, "DOT", "THE RED BLOOD CELL", "A COURIER WHO SEES THE WHOLE WAR", (255, 140, 150))]
        for x, name, role, tagline, rgb in cols:
            c.drawRRect(rrect(x - 290, 190, 580, 860, 40), fill((40, 6, 18), 150))
            c.drawRRect(rrect(x - 290, 190, 580, 860, 40), stroke(rgb, 3, 180))
            text(c, name, x, 640, 70, rgb, 255, 800, spacing=12)
            text(c, role, x, 684, 20, WHITE, 230, 800, spacing=4)
            text(c, tagline, x, 716, 15, WHITE, 170, 800, spacing=2)
        pip(c, 330, 420, 140, t, "determined", (0.2, 0), arm_r=0.9, arm_l=0.1)
        kai(c, 960, 430, 135, t, "determined", (0.3, 0))
        dot(c, 1590, 430, 150, t, "happy", (0, 0), turn=0.35, arm_l=0.2, arm_r=0.85)
        for i, e in enumerate(("happy", "shocked", "worried")):
            pip(c, 170 + i * 160, 880, 52, t + i * 0.37, e, (0, 0), arm_l=0.6 if e == "happy" else 0, arm_r=0.6 if e == "happy" else 0)
            kai(c, 800 + i * 160, 880, 50, t + i * 0.37, ("happy", "shocked", "worried")[i])
            dot(c, 1430 + i * 160, 880, 56, t + i * 0.37, e, turn=0.35)
        for x in (330, 960, 1590):
            text(c, "HAPPY · SHOCKED · WORRIED", x, 990, 14, WHITE, 160, 800, spacing=3)

    from premium import render_premium
    out = os.path.join(HERE, "out", "storyboards", "hero_concepts.png")
    Image.fromarray(render_premium(sheet, 1.3, samples=1)).save(out)
    print(out)
