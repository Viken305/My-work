"""Cast + props for "How Earth Makes Gold" (vertical 1080x1920).

AURI, the guide: a gold atom. A polished, metallic gold ball (real reflections: dark rim, warm mid, a bright window
highlight and a sky-coloured reflection band) circled by three tilted electron orbits with glowing electrons, on the
shared face rig (rig.py) so every expression change is animated.
"""
import math

import numpy as np

from premium import *  # noqa: F401,F403
from rig import face_rig, pose, Track, blink_amount  # noqa: F401

GOLD = (236, 170, 52)
GOLD_HI = (255, 226, 150)
GOLD_MID = (200, 128, 30)
GOLD_DEEP = (110, 56, 16)
NAVY = (10, 12, 36)
NIGHT = (18, 20, 58)
MAGMA = (255, 96, 40)
MAGMA_DEEP = (150, 30, 30)
QUARTZ = (236, 232, 224)
NEUTRON = (150, 200, 255)


# ---------------------------------------------------------------- metal shading
def gold_sphere(c, x, y, r, env=(90, 120, 200), a=255):
    """Metallic gold ball: dark rim, warm body, sharp window highlight, environment band reflection."""
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    c.drawCircle(x, y, r, shaded(radial((x - r * 0.3, y - r * 0.35), r * 1.45,
                                        [GOLD_HI, GOLD, GOLD_MID, GOLD_DEEP, (50, 24, 8)], [0, 0.18, 0.5, 0.82, 1])))
    body = skia.Path()
    body.addCircle(x, y, r)
    c.save()
    c.clipPath(body, doAntiAlias=True)
    # environment reflection: a curved band of the sky colour across the lower half
    band = skia.Path()
    band.addOval(skia.Rect.MakeXYWH(x - r * 1.3, y + r * 0.15, r * 2.6, r * 1.2))
    p = skia.Paint(AntiAlias=True, Shader=linear((x, y + r * 0.2), (x, y + r), [(env, 90), (env, 0)]))
    p.setBlendMode(skia.BlendMode.kScreen)
    c.drawPath(band, p)
    # bounce light from below
    light(c, x, y + r * 1.1, r * 0.9, (255, 180, 90), 70)
    c.restore()
    # crisp window highlight + small secondary
    c.drawRRect(rrect(x - r * 0.55, y - r * 0.68, r * 0.42, r * 0.22, r * 0.11), fill(WHITE, 170))
    c.drawCircle(x - r * 0.05, y - r * 0.6, r * 0.06, fill(WHITE, 190))
    c.drawCircle(x, y, r, stroke((90, 50, 15), max(1.5, r * 0.025), 200))
    if a < 255:
        c.restore()


def sparkle4(c, x, y, s, a=255, rgb=WHITE):
    p = skia.Path()
    p.moveTo(x, y - s)
    p.quadTo(x, y, x + s, y)
    p.quadTo(x, y, x, y + s)
    p.quadTo(x, y, x - s, y)
    p.quadTo(x, y, x, y - s)
    c.drawPath(p, add(rgb, a))


# ---------------------------------------------------------------- AURI
def auri(c, x, y, r, t, p, look=(0.0, 0.0), blink=0.0, vel=(0.0, 0.0), env=(90, 120, 200), a=255, orbits=1.0, hard_hat=False):
    """AURI the gold atom. p: rig pose. orbits: 0..1 visibility of the electron rings."""
    if a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    sp = math.hypot(*vel)
    hover = bob(t, r * 0.05, 2.8)
    c.save()
    c.translate(x, y + hover)
    c.rotate(clamp(vel[0] / 900, -1, 1) * 10)
    st = 1 + clamp(sp / 2400, 0, 0.15)
    if sp > 1:
        an = math.degrees(math.atan2(vel[1], vel[0]))
        c.rotate(an)
        c.scale(st, 1 / st)
        c.rotate(-an)
    c.scale(1 / math.sqrt(p["squash"]), p["squash"])
    rings = [(r * 1.65, r * 0.48, -18 + 4 * math.sin(t * 0.7), 1.3), (r * 1.55, r * 0.42, 52, -1.0), (r * 1.6, r * 0.45, 128, 0.8)]

    def ring(k, front):
        rx, ry, rot, sp_ = rings[k]
        c.save()
        c.rotate(rot)
        oval = skia.Rect.MakeXYWH(-rx, -ry, 2 * rx, 2 * ry)
        start, sweep = (0, 180) if front else (180, 180)
        arc = skia.Path()
        arc.addArc(oval, start, sweep)
        c.drawPath(arc, stroke((255, 230, 160), r * 0.035, (200 if front else 110) * orbits))
        ang = (t * sp_ * 1.6 + k * 2.1) % (2 * math.pi)
        ex, ey = math.cos(ang) * rx, math.sin(ang) * ry
        if (ey > 0) == front:
            light(c, ex, ey, r * 0.32, (120, 220, 255), 200 * orbits)
            c.drawCircle(ex, ey, r * 0.075, fill((220, 250, 255), 255 * orbits))
        c.restore()
    for k in range(3):
        ring(k, False)
    c.drawOval(skia.Rect.MakeXYWH(-r * 0.9, r * 1.05, r * 1.8, r * 0.3), blur(fill((0, 0, 20), 70), r * 0.1))
    gold_sphere(c, 0, 0, r, env)
    if hard_hat:
        dome = skia.Path()
        dome.addArc(skia.Rect.MakeXYWH(-r * 0.85, -r * 1.12, r * 1.7, r * 1.3), 180, 180)
        dome.close()
        c.drawPath(dome, shaded(linear((0, -r * 1.12), (0, -r * 0.45), [(255, 220, 90), (230, 170, 30)])))
        c.drawRRect(rrect(-r * 0.98, -r * 0.52, r * 1.96, r * 0.16, r * 0.08), fill((220, 150, 20)))
        light(c, 0, -r * 0.85, r * 0.5, (255, 255, 220), 160)
        c.drawCircle(0, -r * 0.85, r * 0.12, fill((255, 255, 230)))
    face_rig(c, look[0] * r * 0.08, r * 0.05 + look[1] * r * 0.05, r * 0.92, p, look, blink, ink=(60, 30, 10), skin=GOLD, spread=0.28)
    for k in range(3):
        ring(k, True)
    c.restore()
    if a < 255:
        c.restore()


# ---------------------------------------------------------------- props
SF = Starfield(8, (500, 180, 50))


def space_bg(c, t, cam=None, a=1.0, warm=0.0):
    cam = cam or Cam()
    c.drawPaint(shaded(radial((W / 2, H * 0.45), H * 0.8, [mix(NIGHT, (60, 30, 50), warm), NAVY, (4, 4, 14)], [0, 0.6, 1])))
    SF.draw(c, t, cam, a)


def neutron_star(c, x, y, r, t, a=255):
    for s in (1, -1):        # beams
        c.save()
        c.translate(x, y)
        c.rotate(t * 90 + (0 if s > 0 else 180))
        p = skia.Paint(AntiAlias=True, Shader=linear((0, 0), (0, -r * 12), [(NEUTRON, 160 * a / 255), (NEUTRON, 0)]))
        p.setBlendMode(skia.BlendMode.kPlus)
        c.drawPath(poly([(-r * 0.25, 0), (r * 0.25, 0), (r * 1.2, -r * 12), (-r * 1.2, -r * 12)]), p)
        c.restore()
    light(c, x, y, r * 6, NEUTRON, 160 * a / 255)
    c.drawCircle(x, y, r, shaded(radial((x - r * 0.3, y - r * 0.3), r * 1.4, [WHITE, (200, 225, 255), (120, 160, 230)])))


def kilonova(c, x, y, R, t, k, seed=3):
    """Collision fireball (k 0..1): flash, expanding shell, and gold nuggets flung outward."""
    if k <= 0:
        return
    fl = math.exp(-k * 6)
    light(c, x, y, R * (0.6 + 1.4 * k), (255, 200, 120), 255 * (0.35 + 0.65 * fl))
    rr = R * out_cubic(k)
    sh = skia.Paint(AntiAlias=True, Shader=radial((x, y), rr + 1, [((255, 150, 60), 0), ((255, 150, 60), 0), ((255, 210, 140), 200 * (1 - k * 0.7)), ((255, 120, 60), 0)],
                                                   [0, 0.72, 0.92, 1]))
    sh.setBlendMode(skia.BlendMode.kPlus)
    c.drawCircle(x, y, rr + 1, sh)
    rng = np.random.default_rng(seed)
    for i in range(70):
        an = rng.uniform(0, 6.28)
        d = rr * rng.uniform(0.3, 1.05)
        s = rng.uniform(6, 16) * (1 - 0.4 * k)
        gx, gy = x + math.cos(an) * d, y + math.sin(an) * d
        gold_sphere(c, gx, gy, s, (200, 120, 80), 255 * min(1, (1 - k) * 2.2))
    if fl > 0.02:
        c.drawPaint(add(HOTWHITE, 255 * fl * 0.8))


def earth_section(c, cx, cy, R, t, molten=1.0, core_glow=1.0):
    """Earth cut in half: crust, mantle, outer core, inner core (molten makes it all red-hot)."""
    layers = [(1.0, mix((90, 130, 90), (120, 40, 40), molten)), (0.94, mix((170, 70, 50), (180, 50, 40), molten)), (0.52, (220, 110, 40)), (0.3, (236, 170, 52))]
    for f, rgb in layers:
        c.drawCircle(cx, cy, R * f, shaded(radial((cx - R * f * 0.3, cy - R * f * 0.3), R * f * 1.4, [lighten(rgb, 0.15), rgb, darken(rgb, 0.3)])))
    light(c, cx, cy, R * 0.45, GOLD, 110 * core_glow)


def meteor(c, x, y, s, t, ang=225, a=255):
    an = math.radians(ang)
    tx, ty = x - math.cos(an) * s * 7, y - math.sin(an) * s * 7
    p = skia.Paint(AntiAlias=True, Shader=linear((x, y), (tx, ty), [((255, 200, 120), a), ((255, 120, 60), 0)]), Style=skia.Paint.kStroke_Style, StrokeWidth=s * 1.4)
    p.setBlendMode(skia.BlendMode.kPlus)
    c.drawLine(x, y, tx, ty, p)
    c.drawCircle(x, y, s, shaded(radial((x - s * 0.3, y - s * 0.3), s * 1.4, [(180, 160, 150), (110, 90, 90), (60, 50, 60)])))
    gold_sphere(c, x + s * 0.2, y - s * 0.1, s * 0.3, (200, 120, 80))


def rock_wall(c, x0, y0, w, h, t, seed=5, rgb=(90, 70, 90)):
    """Layered rock with grains."""
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), shaded(linear((0, y0), (0, y0 + h), [lighten(rgb, 0.1), darken(rgb, 0.35)])))
    rng = np.random.default_rng(seed)
    for i in range(160):
        c.drawCircle(x0 + rng.uniform(0, w), y0 + rng.uniform(0, h), rng.uniform(2, 7), fill(lighten(rgb, rng.uniform(-0.2, 0.25)), 160))
