"""The cast of the immune system video, all drawn procedurally so every part can animate.

MAX, the hero: a young macrophage. A wobbly, translucent jelly body whose outline is a living function of angle, so
pseudopods grow straight out of the membrane (no glued-on limbs); big expressive eyes with lids and brows; a mouth that
opens into a full engulfing gulp; a kidney nucleus and drifting granules inside; and whatever Max has eaten slowly
dissolving in its belly, surrounded by purple digestive vesicles.

Supporting cast: bacteria (mischievous green rods with whipping flagella), viruses (faceless spiky spheres), neutrophils
(fierce lilac cells with a lobed nucleus, can burst into a DNA net), dendritic cells (violet stars with waving tendrils),
helper T cells (blue commanders with rank chevrons), killer T cells (red-orange, bandana), B cells / plasma cells (gold,
fire Y-shaped antibodies), memory cells (with a glowing star), red blood cells (biconcave discs).
"""
import math

import numpy as np

from premium import *  # noqa: F401,F403

# ---------------------------------------------------------------- body palette
BLOOD_DARK = (34, 6, 22)
TISSUE = (92, 18, 46)
TISSUE_HI = (200, 62, 92)
PLASMA = (255, 170, 150)
MAX_BODY = (112, 214, 204)
MAX_EDGE = (30, 120, 130)
MAX_NUC = (40, 110, 130)
MACRO = (214, 186, 140)      # supporting macrophage (cream "big eater")
MACRO_EDGE = (150, 110, 70)
GERM = (150, 220, 70)
GERM_DARK = (60, 120, 30)
VIRUS = (190, 70, 220)
NEUTRO = (214, 186, 236)
NEUTRO_NUC = (140, 70, 190)
DENDRI = (170, 120, 255)
HELPER = (80, 160, 255)
KILLER = (255, 96, 80)
BCELL = (235, 178, 62)
ANTIBODY = (255, 220, 110)
RBC = (220, 40, 50)
LYSO = (190, 90, 255)
ALARM = (255, 210, 90)
EYE_INK = (16, 14, 40)

MAX_EXPR = ("neutral", "happy", "determined", "shocked", "worried", "hungry", "full", "chewing")


# ---------------------------------------------------------------- shared face kit
_EXPR_MAP = {"sleepy": ("neutral", dict(eo=0.45)), "hungry": ("shocked", dict(pupil=0.4, curve=0.5, open=0.45, teeth=0.6)),
             "full": ("happy", dict(eo=0.04, lower=0.7, open=0.0, blush=1.0)), "chewing": ("neutral", dict(eo=0.55, blush=0.8, mw=0.5))}


def face(c, x, y, s, t, expr="neutral", look=(0.0, 0.0), blink=True, phase=0.0, mouth=0.0, ink=EYE_INK, brow_rgb=None, spread=0.42):
    """Shared cast face = the animated rig (rig.py) so every cell acts the same way as KAI."""
    from rig import face_rig, pose, blink_amount, POSES
    name, over = _EXPR_MAP.get(expr, (expr if expr in POSES else "neutral", {}))
    over = dict(over)
    if mouth > 0:
        over["open"] = max(over.get("open", 0.0), mouth)
    if expr == "chewing":
        over["open"] = 0.05 + 0.15 * (0.5 + 0.5 * math.sin(t * 14))
    p = pose(name, **over)
    b = blink_amount(t, (), 4.1, phase * 1.7) if blink else 0.0
    face_rig(c, x, y + s * 0.02, s * 0.95, p, look, b, ink=ink, spread=spread * 0.64)


# ---------------------------------------------------------------- MAX the macrophage
def max_outline(r, t, arms=(), gulp=None, vel=(0.0, 0.0), n=72, seed=0.0):
    """Radius per angle: wobbling membrane + pseudopods. arms: [(angle_deg, length_in_r)].
    gulp: (angle_deg, open 0..1) — two lips that part and wrap around food in that direction."""
    rad = []
    for i in range(n):
        th = 2 * math.pi * i / n
        w = (0.035 * math.sin(3 * th + t * 1.9 + seed) + 0.025 * math.sin(5 * th - t * 2.7 + seed * 2)
             + 0.018 * math.sin(8 * th + t * 3.3) + 0.012 * math.sin(11 * th - t * 4.1))
        rr = 1.0 + w
        for ang, ln in arms:
            d = math.atan2(math.sin(th - math.radians(ang)), math.cos(th - math.radians(ang)))
            width = 0.42 / (1 + ln * 1.2)
            rr += ln * math.exp(-(d / width) ** 2) * (1 + 0.04 * math.sin(t * 6 + ang))
        if gulp:
            ang, op = gulp
            d = math.atan2(math.sin(th - math.radians(ang)), math.cos(th - math.radians(ang)))
            # lips at ±(0.25+0.35op) rad reach out, centre dents in to make a mouth
            for s in (-1, 1):
                rr += 0.55 * op * math.exp(-((d - s * (0.2 + 0.32 * op)) / 0.2) ** 2)
            rr -= 0.42 * op * math.exp(-(d / (0.12 + 0.22 * op)) ** 2)
        rad.append(r * rr)
    return rad


def max_cell(c, x, y, r, t, expr="neutral", look=(0.0, 0.0), vel=(0.0, 0.0), arms=(), gulp=None, belly=(), a=255,
             rim=(255, 120, 140), blink=True, mouth=0.0, face_on=True, glow_a=1.0, body_rgb=None, edge_rgb=None):
    """MAX. belly: [(dx, dy, size, digest 0..1)] items inside (bacteria being dissolved)."""
    if r <= 1 or a <= 1:
        return
    MAX_BODY_, MAX_EDGE_ = body_rgb or MAX_BODY, edge_rgb or MAX_EDGE
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    sp = math.hypot(*vel)
    stretch = 1 + clamp(sp / 2600.0, 0, 0.18)
    breathe = 1 + 0.025 * math.sin(t * 2.2)
    c.save()
    c.translate(x, y + bob(t, r * 0.03, 3.1))
    if sp > 1:
        ang = math.degrees(math.atan2(vel[1], vel[0]))
        c.rotate(ang)
        c.scale(stretch, 1 / stretch)
        c.rotate(-ang)
    c.scale(breathe, 1 / breathe)
    body = blob_path(0, 0, max_outline(r, t, arms, gulp, vel))
    # outer glow + soft drop shadow
    light(c, 0, 0, r * 2.0, MAX_BODY_, 32 * glow_a)
    c.drawPath(body, blur(fill((20, 0, 20), 90), r * 0.12))
    # jelly body: translucent, lighter towards the upper-left
    c.drawPath(body, shaded(radial((-r * 0.3, -r * 0.4), r * 1.9, [lighten(MAX_BODY_, 0.35), MAX_BODY_, mix(MAX_BODY_, MAX_EDGE_, 0.6)], [0, 0.5, 1])))
    c.save()
    c.clipPath(body, doAntiAlias=True)
    # nucleus (kidney) + granules
    nuc = blob_path(r * 0.42, r * 0.48, [r * 0.26 * (1 + 0.12 * math.sin(k * 1.7 + t * 0.7)) * (0.7 if k in (3, 4) else 1) for k in range(10)], 0.3)
    c.drawPath(nuc, fill(MAX_NUC, 55))
    c.drawPath(nuc, stroke(MAX_NUC, r * 0.02, 70))
    rng = np.random.default_rng(12)
    for k in range(26):
        gx, gy = rng.uniform(-0.75, 0.75), rng.uniform(-0.7, 0.75)
        gx += 0.05 * math.sin(t * 0.9 + k)
        gy += 0.05 * math.cos(t * 0.8 + k * 1.3)
        c.drawCircle(gx * r, gy * r, r * rng.uniform(0.015, 0.035), fill(MAX_EDGE_, 90))
    # belly: eaten bacteria dissolving, surrounded by digestive vesicles
    for bx, by, bs, dg in belly:
        if dg >= 1:
            continue
        bacterium(c, bx * r, by * r, bs * r * (1 - 0.6 * dg), t, ang=40 + 90 * dg, a=200 * (1 - dg), face_on=dg < 0.3, mood="scared", flag=False)
        for v in range(6):
            va = v / 6 * 6.28 + t * 0.8
            vd = bs * r * (1.1 - 0.4 * dg)
            c.drawCircle(bx * r + math.cos(va) * vd, by * r + math.sin(va) * vd * 0.7, r * 0.035, fill(LYSO, 170 * (1 - dg * 0.6)))
    # rim light from the scene + membrane highlights
    # rim light hugging the membrane (works for any pseudopod length), stronger on the lower-right
    rp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.22,
                    Shader=linear((-r, -r), (r, r), [(rim, 40), (rim, 150)]))
    rp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.06))
    rp.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(body, rp)
    c.drawOval(skia.Rect.MakeXYWH(-r * 0.62, -r * 0.82, r * 0.5, r * 0.2), fill(WHITE, 70))
    c.restore()
    c.drawPath(body, stroke(darken(MAX_EDGE_, 0.2), r * 0.035, 220))
    inner = skia.Path()
    inner.addPath(body, skia.Matrix.Scale(0.92, 0.92))
    c.drawPath(inner, stroke(lighten(MAX_BODY_, 0.6), r * 0.014, 110))
    if face_on:
        fx = look[0] * r * 0.12
        face(c, fx, -r * 0.2 + look[1] * r * 0.06, r * 1.15, t, expr, look, blink, 0.0, mouth)
    c.restore()
    if a < 255:
        c.restore()


# ---------------------------------------------------------------- villains
def bacterium(c, x, y, s, t, ang=0.0, rgb=GERM, a=255, face_on=True, mood="grin", wiggle=1.0, flag=True, tag=0.0):
    """Rod-shaped bacterium (capsule, length 2.3s, width s) with whipping flagella and a cheeky face.
    tag 0..1: antibodies stuck to it (opsonised)."""
    if s <= 0.5 or a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    L, R = s * 1.15, s * 0.5
    # flagella
    if flag:
        for k in (-1, 0, 1):
            p = skia.Path()
            p.moveTo(-L, k * R * 0.4)
            for j in range(1, 13):
                u = j / 12
                p.lineTo(-L - u * s * 1.6, k * R * 0.4 + k * u * s * 0.3 + math.sin(u * 9 - t * 14 * wiggle + k) * s * 0.18 * u)
            c.drawPath(p, stroke(GERM_DARK, s * 0.06, 220))
    cap = rrect(-L, -R, 2 * L, 2 * R, R)
    c.drawRRect(cap, blur(fill((10, 30, 0), 80), s * 0.1))
    c.drawRRect(cap, shaded(linear((0, -R), (0, R), [lighten(rgb, 0.35), rgb, darken(rgb, 0.35)], [0, 0.45, 1])))
    for k in range(5):     # surface spots
        c.drawCircle(-L * 0.7 + k * L * 0.35, R * (0.35 if k % 2 else -0.45), s * 0.07, fill(darken(rgb, 0.3), 120))
    c.drawRRect(cap, stroke(darken(rgb, 0.45), s * 0.06))
    for k in range(10):    # pili
        px = -L * 0.8 + k * L * 0.18
        c.drawLine(px, -R, px + s * 0.03, -R - s * 0.1, stroke(darken(rgb, 0.4), s * 0.025, 200))
        c.drawLine(px, R, px - s * 0.03, R + s * 0.1, stroke(darken(rgb, 0.4), s * 0.025, 200))
    c.drawRRect(rrect(-L * 0.8, -R * 0.75, L * 1.5, R * 0.35, R * 0.18), fill(WHITE, 70))
    if face_on and s > 6:
        c.save()
        c.translate(L * 0.35, 0)
        c.rotate(-ang if abs(((ang + 180) % 360) - 180) > 90 else 0)
        if mood == "scared":
            face(c, 0, -s * 0.05, s * 0.85, t, "shocked", (0, 0), True, 1.3, 0.0, ink=(20, 40, 0))
        elif mood == "sneaky":
            face(c, 0, -s * 0.05, s * 0.85, t, "determined", (0.6, 0), True, 1.3, 0.0, ink=(20, 40, 0))
        else:
            _grin(c, 0, -s * 0.05, s * 0.85, t)
        c.restore()
    if tag > 0:
        n = int(2 + 6 * tag)
        for k in range(n):
            ta = k / 8 * 6.28 + 0.3
            ex, ey = math.cos(ta) * L * 1.02, math.sin(ta) * R * 1.05
            antibody(c, ex, ey, s * 0.42, math.degrees(ta) + 90, a=255 * min(1, tag * 2))
    c.restore()
    if a < 255:
        c.restore()


def _grin(c, x, y, s, t):
    """Mischievous face: narrow eyes with low brows, toothy grin."""
    er = s * 0.17
    for side in (-1, 1):
        ex = x + side * s * 0.27
        c.drawOval(skia.Rect.MakeXYWH(ex - er, y - er * 0.7, er * 2, er * 1.4), fill(WHITE))
        c.drawCircle(ex + er * 0.3, y, er * 0.55, fill((20, 40, 0)))
        c.drawLine(ex - side * er * 1.1, y - er * 1.3, ex + side * er * 1.1, y - er * 0.7, stroke((20, 40, 0), er * 0.4))
    p = skia.Path()
    mw = s * 0.33
    p.moveTo(x - mw, y + s * 0.25)
    p.quadTo(x, y + s * 0.6, x + mw, y + s * 0.22)
    p.close()
    c.drawPath(p, fill((30, 50, 10)))
    c.save()
    c.clipPath(p, doAntiAlias=True)
    for k in range(5):
        c.drawRect(skia.Rect.MakeXYWH(x - mw + k * mw * 0.42, y + s * 0.18, mw * 0.3, s * 0.12), fill(WHITE))
    c.restore()


def virus(c, x, y, s, t, a=255, rgb=VIRUS, spin=20.0, tag=0.0):
    """Faceless spiky virus: capsid with spike proteins and a faint glow."""
    if s <= 0.5 or a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    light(c, x, y, s * 2.2, rgb, 60)
    rot = t * spin
    for k in range(14):
        an = math.radians(rot + k * 360 / 14)
        x1, y1 = x + math.cos(an) * s * 0.9, y + math.sin(an) * s * 0.9
        x2, y2 = x + math.cos(an) * s * 1.35, y + math.sin(an) * s * 1.35
        c.drawLine(x1, y1, x2, y2, stroke(darken(rgb, 0.2), s * 0.09))
        c.drawCircle(x2, y2, s * 0.13, fill(lighten(rgb, 0.25)))
    c.drawCircle(x, y, s, shaded(radial((x - s * 0.35, y - s * 0.4), s * 1.5, [lighten(rgb, 0.4), rgb, darken(rgb, 0.45)], [0, 0.5, 1])))
    for k in range(7):     # capsid facets
        an = math.radians(rot * 0.5 + k * 51)
        c.drawCircle(x + math.cos(an) * s * 0.55, y + math.sin(an) * s * 0.55, s * 0.2, stroke(darken(rgb, 0.3), s * 0.04, 150))
    c.drawCircle(x - s * 0.3, y - s * 0.35, s * 0.28, fill(WHITE, 60))
    if tag > 0:
        for k in range(int(2 + 6 * tag)):
            ta = k / 8 * 6.28
            antibody(c, x + math.cos(ta) * s * 1.25, y + math.sin(ta) * s * 1.25, s * 0.55, math.degrees(ta) + 90, a=255 * min(1, tag * 2))
    if a < 255:
        c.restore()


# ---------------------------------------------------------------- immune cells (supporting cast)
def _cell_body(c, x, y, r, t, rgb, seed=0.0, wob=1.0, n=40):
    rad = [r * (1 + wob * (0.04 * math.sin(3 * (2 * math.pi * i / n) + t * 2 + seed) + 0.025 * math.sin(6 * (2 * math.pi * i / n) - t * 2.6 + seed)))
           for i in range(n)]
    p = blob_path(x, y, rad)
    light(c, x, y, r * 1.9, rgb, 30)
    c.drawPath(p, blur(fill((20, 0, 20), 80), r * 0.12))
    c.drawPath(p, shaded(radial((x - r * 0.3, y - r * 0.4), r * 1.8, [lighten(rgb, 0.3), rgb, darken(rgb, 0.3)], [0, 0.45, 1])))
    return p


def _finish_body(c, p, x, y, r, rim):
    c.save()
    c.clipPath(p, doAntiAlias=True)
    rp = skia.Paint(AntiAlias=True, Shader=radial((x - r * 0.25, y - r * 0.3), r * 1.55, [(rim, 0), (rim, 0), (rim, 150)], [0, 0.72, 1]))
    rp.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(p, rp)
    c.drawOval(skia.Rect.MakeXYWH(x - r * 0.6, y - r * 0.82, r * 0.5, r * 0.22), fill(WHITE, 80))
    c.restore()


def neutrophil(c, x, y, r, t, expr="determined", look=(0.0, 0.0), a=255, rim=(255, 140, 160), seed=0.0, burst=0.0):
    """Fierce small cell with a 3-lobed nucleus. burst 0..1: explodes into a glowing DNA net."""
    if r <= 1 or a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    if burst > 0:
        net(c, x, y, r * (1 + 4 * out_cubic(burst)), t, 255 * (1 - smooth(prog(burst, 0.7, 1.0)) * 0.4), seed)
    ba = 1 - smooth(prog(burst, 0.0, 0.35))
    if ba > 0.01:
        c.saveLayerAlpha(None, int(255 * ba))
        sc = 1 + 0.4 * burst
        p = _cell_body(c, x, y, r * sc, t, NEUTRO, seed)
        c.save()
        c.clipPath(p, doAntiAlias=True)
        for k in range(3):   # lobed nucleus, low and to the side so it never reads as a mouth
            lx, ly = x + r * 0.05 + k * r * 0.24, y + r * 0.62 - (k % 2) * r * 0.1
            c.drawCircle(lx, ly, r * 0.15, fill(NEUTRO_NUC, 70))
        c.drawLine(x + r * 0.05, y + r * 0.62, x + r * 0.53, y + r * 0.62, stroke(NEUTRO_NUC, r * 0.05, 70))
        rng = np.random.default_rng(int(seed * 10) + 3)
        for k in range(16):
            c.drawCircle(x + rng.uniform(-0.7, 0.7) * r, y + rng.uniform(-0.7, 0.7) * r, r * 0.03, fill((200, 120, 200), 120))
        c.restore()
        _finish_body(c, p, x, y, r, rim)
        face(c, x + look[0] * r * 0.1, y - r * 0.15, r, t, expr, look, True, seed * 1.7)
        c.restore()
    if a < 255:
        c.restore()


def net(c, x, y, r, t, a=255, seed=0.0):
    """NET: glowing web of DNA strands."""
    rng = np.random.default_rng(int(seed * 7) + 11)
    pts = [(x + math.cos(an) * r * d, y + math.sin(an) * r * d) for an, d in zip(rng.uniform(0, 6.28, 22), rng.uniform(0.2, 1.0, 22))]
    for i, (px, py) in enumerate(pts):
        for j in range(i + 1, len(pts)):
            qx, qy = pts[j]
            if math.hypot(px - qx, py - qy) < r * 0.55:
                p = skia.Path()
                p.moveTo(px, py)
                p.quadTo((px + qx) / 2 + math.sin(t + i) * r * 0.05, (py + qy) / 2 + math.cos(t + j) * r * 0.05, qx, qy)
                pp = stroke((220, 170, 255), max(1.2, r * 0.008), a * 0.8)
                pp.setBlendMode(skia.BlendMode.kPlus)
                c.drawPath(p, pp)
        c.drawCircle(px, py, max(1.5, r * 0.012), add((240, 210, 255), a))


def dendritic(c, x, y, r, t, expr="neutral", look=(0.0, 0.0), a=255, rim=(255, 160, 200), carry=None, seed=0.0):
    """Violet star-shaped cell with long waving tendrils. carry: rgb of an antigen fragment held up."""
    if r <= 1 or a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    for k in range(7):
        an = k / 7 * 6.28 + 0.4 + 0.12 * math.sin(t * 1.3 + k)
        p = skia.Path()
        x0, y0 = x + math.cos(an) * r * 0.7, y + math.sin(an) * r * 0.7
        p.moveTo(x0, y0)
        ln = r * (1.5 + 0.25 * math.sin(t * 0.9 + k * 2))
        bend = math.sin(t * 1.6 + k * 1.3) * 0.5
        ex, ey = x + math.cos(an + bend * 0.4) * (r + ln), y + math.sin(an + bend * 0.4) * (r + ln)
        p.quadTo(x + math.cos(an - bend * 0.5) * (r + ln * 0.5), y + math.sin(an - bend * 0.5) * (r + ln * 0.5), ex, ey)
        c.drawPath(p, stroke(darken(DENDRI, 0.15), r * 0.22))
        c.drawPath(p, stroke(DENDRI, r * 0.15))
        c.drawCircle(ex, ey, r * 0.1, fill(lighten(DENDRI, 0.3)))
    p = _cell_body(c, x, y, r, t, DENDRI, seed)
    _finish_body(c, p, x, y, r, rim)
    if carry:
        cx_, cy_ = x + r * 0.95, y - r * 0.95
        c.drawLine(x + r * 0.5, y - r * 0.4, cx_, cy_, stroke(DENDRI, r * 0.12))
        light(c, cx_, cy_, r * 0.8, carry, 140)
        c.drawPath(blob_path(cx_, cy_, [r * 0.24 * (1 + 0.2 * math.sin(k * 2.1)) for k in range(7)]), fill(carry))
    face(c, x + look[0] * r * 0.1, y - r * 0.1, r, t, expr, look, True, seed + 0.7)
    if a < 255:
        c.restore()


def _receptors(c, x, y, r, t, rgb, n=12, key=None):
    for k in range(n):
        an = k / n * 6.28 + t * 0.15
        bx, by = x + math.cos(an) * r * 0.98, y + math.sin(an) * r * 0.98
        ux, uy = math.cos(an), math.sin(an)
        c.drawLine(bx, by, bx + ux * r * 0.12, by + uy * r * 0.12, stroke(darken(rgb, 0.25), r * 0.05))
        # little cup = the receptor "lock"
        cx_, cy_ = bx + ux * r * 0.16, by + uy * r * 0.16
        cup = skia.Path()
        cup.addArc(skia.Rect.MakeXYWH(cx_ - r * 0.07, cy_ - r * 0.07, r * 0.14, r * 0.14), math.degrees(an) + 90, 180)
        c.drawPath(cup, stroke(key or lighten(rgb, 0.3), r * 0.045))


def t_cell(c, x, y, r, t, kind="helper", expr="neutral", look=(0.0, 0.0), a=255, rim=(255, 160, 200), key=None, seed=0.0, memory=False):
    """Helper (blue, rank chevrons) or killer (red-orange, bandana) T cell, studded with receptor cups."""
    if r <= 1 or a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    rgb = HELPER if kind == "helper" else KILLER
    _receptors(c, x, y, r, t, rgb, 12, key)
    p = _cell_body(c, x, y, r, t, rgb, seed, 0.6)
    c.save()
    c.clipPath(p, doAntiAlias=True)
    c.drawCircle(x + r * 0.15, y + r * 0.25, r * 0.55, fill(darken(rgb, 0.35), 60))   # big nucleus
    if kind == "killer":   # bandana
        band = skia.Path()
        band.moveTo(x - r * 1.1, y - r * 0.6)
        band.quadTo(x, y - r * 0.82, x + r * 1.1, y - r * 0.6)
        band.lineTo(x + r * 1.1, y - r * 0.38)
        band.quadTo(x, y - r * 0.6, x - r * 1.1, y - r * 0.38)
        band.close()
        c.drawPath(band, fill((40, 30, 60)))
    c.restore()
    if kind == "killer":
        for k in (0, 1):
            c.drawLine(x + r * 0.9, y - r * 0.5, x + r * (1.25 + 0.1 * k), y - r * (0.25 - 0.3 * k) + 0.06 * r * math.sin(t * 5 + k), stroke((40, 30, 60), r * 0.12))
    _finish_body(c, p, x, y, r, rim)
    if kind == "helper":   # rank chevrons on the "shoulder"
        for k in range(2):
            cy_ = y + r * 0.45 + k * r * 0.14
            c.drawPath(poly([(x - r * 0.62, cy_ - r * 0.07), (x - r * 0.48, cy_ + r * 0.04), (x - r * 0.34, cy_ - r * 0.07)], False), stroke((255, 220, 120), r * 0.05))
    if memory:
        sparkle(c, x + r * 0.6, y - r * 0.7, r * 0.35, 255, (255, 230, 140))
        light(c, x + r * 0.6, y - r * 0.7, r * 0.6, (255, 220, 120), 120)
    face(c, x + look[0] * r * 0.1, y - r * 0.12, r, t, expr, look, True, seed + 1.9)
    if a < 255:
        c.restore()


def b_cell(c, x, y, r, t, expr="neutral", look=(0.0, 0.0), a=255, rim=(255, 160, 200), plasma=0.0, seed=0.0, memory=False):
    """Gold B cell. plasma 0..1 morphs it into a bigger plasma cell with antibody-factory folds."""
    if r <= 1 or a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    rr = r * (1 + 0.35 * plasma)
    for k in range(10):   # surface antibodies (B cell receptors)
        an = k / 10 * 6.28 + t * 0.1
        antibody(c, x + math.cos(an) * rr * 1.05, y + math.sin(an) * rr * 1.05, rr * 0.22, math.degrees(an) + 90, a=200)
    p = _cell_body(c, x, y, rr, t, BCELL, seed, 0.6)
    c.save()
    c.clipPath(p, doAntiAlias=True)
    if plasma > 0:
        for k in range(5):   # rough ER folds
            q = skia.Path()
            yy = y - rr * 0.1 + k * rr * 0.16
            q.moveTo(x - rr * 0.75, yy)
            for j in range(1, 9):
                q.lineTo(x - rr * 0.75 + j * rr * 0.19, yy + math.sin(j * 1.5 + t * 2 + k) * rr * 0.04)
            c.drawPath(q, stroke(darken(BCELL, 0.3), rr * 0.03, 140 * plasma))
    c.drawCircle(x - rr * 0.25, y + rr * 0.3, rr * 0.35, fill(darken(BCELL, 0.4), 60))
    c.restore()
    _finish_body(c, p, x, y, rr, rim)
    if memory:
        sparkle(c, x + rr * 0.6, y - rr * 0.7, rr * 0.35, 255, (255, 255, 255))
        light(c, x + rr * 0.6, y - rr * 0.7, rr * 0.6, (255, 240, 200), 120)
    face(c, x + look[0] * rr * 0.1, y - rr * 0.12, rr, t, expr, look, True, seed + 2.3)
    if a < 255:
        c.restore()


def antibody(c, x, y, s, ang=0.0, a=255, rgb=ANTIBODY):
    """Y-shaped antibody, s = height. ang in degrees (0 = Y pointing up)."""
    if s <= 1 or a <= 1:
        return
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    w = s * 0.16
    pp = stroke(darken(rgb, 0.35), w * 1.5, a)
    p = stroke(rgb, w, a)
    for st in (pp, p):
        c.drawLine(0, s * 0.5, 0, 0, st)
        c.drawLine(0, 0, -s * 0.36, -s * 0.45, st)
        c.drawLine(0, 0, s * 0.36, -s * 0.45, st)
    c.drawCircle(0, 0, w * 0.6, fill(lighten(rgb, 0.4), a))
    c.restore()


def rbc(c, x, y, s, t, tilt=0.0, a=255, seed=0.0):
    """Red blood cell: biconcave disc seen at an angle (tilt 0 = face-on, 1 = edge-on)."""
    if s <= 1 or a <= 1:
        return
    c.save()
    c.translate(x, y)
    c.rotate(seed * 57 + t * 10 * (seed % 1 - 0.5))
    sq = max(0.28, 1 - 0.72 * tilt)
    c.scale(1, sq)
    c.drawCircle(0, 0, s, shaded(radial((-s * 0.3, -s * 0.3), s * 1.5, [lighten(RBC, 0.25), RBC, darken(RBC, 0.4)], [0, 0.6, 1])))
    c.drawCircle(0, 0, s * 0.5, shaded(radial((s * 0.1, s * 0.1), s * 0.6, [darken(RBC, 0.35), darken(RBC, 0.15)])))
    c.drawCircle(0, 0, s, stroke(lighten(RBC, 0.3), s * 0.06, 150))
    c.restore()


def mast_alarm(c, x, y, r, t, k, rgb=ALARM, a=255):
    """Expanding alarm rings + signal molecules (k 0..1 cycles)."""
    for i in range(3):
        u = (k + i / 3) % 1.0
        c.drawCircle(x, y, r * (0.3 + 1.7 * u), stroke(rgb, r * 0.03 * (1 - u) + 1, a * (1 - u)))
    rng = np.random.default_rng(31)
    for i in range(18):
        an = rng.uniform(0, 6.28)
        d = r * (0.3 + 1.6 * ((k * 1.3 + rng.random()) % 1.0))
        c.drawCircle(x + math.cos(an) * d, y + math.sin(an) * d, r * 0.04, add(rgb, a * 0.8))


# ---------------------------------------------------------------- backgrounds
def tex_tissue(seed=81):
    return nebula_texture("tissue", seed, [(0.0, (40, 6, 24)), (0.45, (110, 22, 56)), (0.75, (200, 60, 96)), (1.0, (255, 160, 170))], density=1.0, warp=120, lo=0.3)


def tex_plasma(seed=91):
    return nebula_texture("plasma", seed, [(0.0, (60, 8, 20)), (0.5, (170, 30, 50)), (0.8, (255, 100, 90)), (1.0, (255, 210, 180))], density=0.9, warp=150, lo=0.35)


def tex_lymph(seed=95):
    return nebula_texture("lymph", seed, [(0.0, (14, 20, 50)), (0.5, (40, 80, 140)), (0.8, (90, 200, 210)), (1.0, (210, 255, 240))], density=0.9, warp=130, lo=0.35)


class CellBokeh:
    """Out-of-focus tissue cells (soft membrane rings) at different depths for a microscope depth-of-field look."""

    def __init__(self, seed=7, n=22, rgb=(255, 150, 170)):
        rng = np.random.default_rng(seed)
        self.items = [(rng.uniform(-1.4, 1.4) * W, rng.uniform(-1.4, 1.4) * H, rng.uniform(60, 240), rng.uniform(0.3, 1.9), rng.uniform(0, 6.28)) for _ in range(n)]
        self.rgb = rgb

    def draw(self, c, t, cam, near=False, a=1.0):
        for x, y, r, depth, ph in self.items:
            if (depth > 1.0) != near:
                continue
            cam.push(c, depth)
            xx, yy = x + 30 * math.sin(t * 0.2 + ph), y + 20 * math.cos(t * 0.17 + ph)
            blur_r = abs(depth - 0.9) * 28 + 2
            p = skia.Paint(AntiAlias=True, Color=col(self.rgb, (60 if near else 70) * a), Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.08)
            p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur_r))
            p.setBlendMode(skia.BlendMode.kPlus)
            c.drawCircle(xx, yy, r, p)
            q = skia.Paint(AntiAlias=True, Color=col(self.rgb, (18 if near else 24) * a))
            q.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur_r + 6))
            q.setBlendMode(skia.BlendMode.kPlus)
            c.drawCircle(xx + r * 0.2, yy + r * 0.1, r * 0.28, q)
            cam.pop(c)


class Motes:
    """Tiny particles drifting in the fluid (3 depths)."""

    def __init__(self, seed=3, n=160, rgb=(255, 200, 200)):
        rng = np.random.default_rng(seed)
        self.p = rng.random((n, 2)) * [W * 2.4, H * 2.4] - [W * 1.2, H * 1.2]
        self.d = rng.choice([0.4, 0.7, 1.0], n)
        self.s = rng.uniform(1.0, 3.2, n)
        self.ph = rng.uniform(0, 6.28, n)
        self.rgb = rgb

    def draw(self, c, t, cam, a=1.0, flow=(12.0, -6.0)):
        for depth in (0.4, 0.7, 1.0):
            cam.push(c, depth)
            idx = np.where(self.d == depth)[0]
            for i in idx:
                x = (self.p[i, 0] + flow[0] * t * depth + 14 * math.sin(t * 0.5 + self.ph[i]) + W * 1.2) % (W * 2.4) - W * 1.2
                y = (self.p[i, 1] + flow[1] * t * depth + 10 * math.cos(t * 0.4 + self.ph[i]) + H * 1.2) % (H * 2.4) - H * 1.2
                c.drawCircle(x, y, self.s[i] * depth, add(self.rgb, 120 * depth * a))
            cam.pop(c)


_CB, _CB_NEAR, _MOTES = CellBokeh(7), CellBokeh(9, 10, (255, 190, 200)), Motes()


def tissue(c, t, cam=None, a=1.0, tint=None, tex=None):
    """Warm, deep 'inside the body' environment: gradient, two parallax tissue layers, bokeh cells, motes."""
    cam = cam or Cam()
    c.drawPaint(shaded(radial((W / 2, H * 0.45), W * 0.9, [(70, 12, 38), BLOOD_DARK, (14, 2, 12)], [0, 0.6, 1])))
    cam.push(c, 0.3)
    draw_texture(c, tex or tex_tissue(), 0, 0, 2.4, t * 0.6, 150 * a, skia.BlendMode.kPlus)
    cam.pop(c)
    _CB.draw(c, t, cam, False, a)
    cam.push(c, 0.6)
    draw_texture(c, tex_tissue(82), 300, 120, 1.8, -t * 0.8, 90 * a, skia.BlendMode.kPlus)
    cam.pop(c)
    _MOTES.draw(c, t, cam, a)
    if tint:
        c.drawPaint(fill(tint, 40))


def foreground(c, t, cam=None, a=1.0):
    """Near, very blurred cells that drift past the lens (draw last)."""
    _CB_NEAR.draw(c, t, cam or Cam(), True, a)


if __name__ == "__main__":
    # character sheet -> out/storyboards/cast_sheet.png
    import os
    from PIL import Image

    def sheet(c, t):
        tissue(c, t, a=0.8)
        text(c, "MEET MAX", 520, 110, 76, WHITE, 255, 800, spacing=10)
        text(c, "A YOUNG MACROPHAGE · OUR HERO", 520, 160, 22, MAX_BODY, 230, 800, spacing=4)
        max_cell(c, 520, 520, 230, t, "happy", (0.2, 0.0), arms=((200, 0.35), (-20, 0.25)), belly=((-0.35, 0.5, 0.2, 0.5),))
        text(c, "WOBBLY JELLY BODY · ARMS GROW OUT OF THE MEMBRANE · EATEN GERMS DISSOLVE INSIDE", 520, 860, 16, WHITE, 190, 800, spacing=2)
        for i, (e, lab, kw) in enumerate([("determined", "DETERMINED", {}), ("shocked", "SHOCKED", {}), ("hungry", "HUNGRY", {"gulp": (0, 0.7)}),
                                          ("worried", "WORRIED", {}), ("chewing", "CHEWING", {}), ("full", "FULL", {"belly": ((-0.25, 0.55, 0.22, 0.2),)})]):
            x, y = 1180 + (i % 3) * 240, 330 + (i // 3) * 300
            max_cell(c, x, y, 82, t + i * 0.7, e, (0.3 if e == "hungry" else 0, 0), **kw)
            text(c, lab, x, y + 140, 18, WHITE, 220, 800, spacing=3)
        # supporting cast strip
        y = 960
        cast = [(lambda x: bacterium(c, x, y - 10, 34, t, 0), "BACTERIUM"), (lambda x: virus(c, x, y - 10, 30, t), "VIRUS"),
                (lambda x: neutrophil(c, x, y - 10, 46, t), "NEUTROPHIL"), (lambda x: dendritic(c, x, y - 10, 34, t), "DENDRITIC"),
                (lambda x: t_cell(c, x, y - 10, 44, t, "helper"), "HELPER T"), (lambda x: t_cell(c, x, y - 10, 44, t, "killer", "determined"), "KILLER T"),
                (lambda x: b_cell(c, x, y - 10, 42, t, "happy"), "B CELL"), (lambda x: rbc(c, x, y - 10, 40, t, 0.35), "RED BLOOD CELL")]
        c.drawRect(skia.Rect.MakeXYWH(0, 880, W, 200), fill((10, 2, 10), 150))
        for i, (fn, lab) in enumerate(cast):
            x = 140 + i * 235
            fn(x)
            text(c, lab, x, y + 80, 15, WHITE, 210, 800, spacing=2)

    from premium import render_premium
    out = os.path.join(HERE, "out", "storyboards", "cast_sheet.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    Image.fromarray(render_premium(sheet, 1.3, samples=1)).save(out)
    print(out)
