"""Environments for the immune video (all organic, never space-like) + shared staging helpers."""
import math

import numpy as np

from heroes import body_world, _tissue_layer  # noqa: F401
from boards import *  # noqa: F401,F403
from kai import kai, pose, Track, blink_amount, saccade, face_rig  # noqa: F401

PLASMA_BG = (120, 20, 40)
LYMPH_BG = (40, 56, 110)


def near_blur(c, items, t, rgb=(230, 120, 140), a=1.0):
    """Huge out-of-focus cells right in front of the lens: [(x, y, r)]. Sells depth of field."""
    for i, (x, y, r) in enumerate(items):
        xx, yy = x + 20 * math.sin(t * 0.3 + i), y + 14 * math.cos(t * 0.25 + i)
        p = skia.Paint(AntiAlias=True, Shader=radial((xx - r * 0.3, yy - r * 0.3), r * 1.4, [(lighten(rgb, 0.2), 190 * a), (rgb, 170 * a), (darken(rgb, 0.3), 150 * a)]))
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.12))
        c.drawCircle(xx, yy, r, p)
        q = fill(darken(rgb, 0.35), 110 * a)
        q.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.12))
        c.drawCircle(xx + r * 0.1, yy + r * 0.05, r * 0.32, q)


def vessel_world(c, t, cam=None, flow=260.0, a=1.0):
    """Inside a blood vessel: curved endothelial walls top and bottom, red blood cells streaming at three depths."""
    cam = cam or Cam()
    c.drawPaint(shaded(linear((0, 0), (0, H), [(70, 8, 22), (150, 24, 44), (70, 8, 22)])))
    rng = np.random.default_rng(14)
    for depth, n, size, blur_r, alpha in ((0.4, 40, 34, 6, 120), (0.7, 26, 60, 2, 200)):
        cam.push(c, depth)
        for k in range(n):
            u = (rng.random() + t * flow * depth / (W * 2)) % 1.0
            x = -W * 1.1 + u * W * 2.2
            y = rng.uniform(-0.4, 0.4) * H
            p_ = skia.Paint()
            c.saveLayerAlpha(None, alpha)
            rbc(c, x, y, size * rng.uniform(0.8, 1.2), t, rng.uniform(0.0, 0.85), 255, rng.random() * 9)
            c.restore()
        cam.pop(c)
    # endothelial walls (flattened cells with nuclei), curving like a tube
    for side in (-1, 1):
        for k in range(16):
            x0 = -150 + k * 150 + (t * 10) % 150 * 0
            yb = H / 2 + side * (H * 0.47 - 30 * math.cos((x0 - W / 2) / W * 3.0))
            cell = rrect(x0, yb - 46, 150, 92, 46)
            c.drawRRect(cell, shaded(linear((0, yb - 46), (0, yb + 46), [(214, 96, 110), (160, 52, 70)] if side < 0 else [(160, 52, 70), (214, 96, 110)])))
            c.drawRRect(cell, stroke((110, 24, 44), 3, 200))
            c.drawOval(skia.Rect.MakeXYWH(x0 + 50, yb - 14, 50, 28), fill((120, 30, 60), 200))
    c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.7, [(255, 120, 130, ), (200, 40, 60), (120, 10, 30)], [0, 0.6, 1])) if False else fill((0, 0, 0), 0))


def lymph_world(c, t, cam=None, a=1.0):
    """Inside a lymph node: cool blue-violet, a reticular fibre mesh, crowds of resting lymphocytes out of focus."""
    cam = cam or Cam()
    c.drawPaint(shaded(radial((W / 2, H * 0.45), W * 0.9, [(70, 90, 160), LYMPH_BG, (16, 20, 50)], [0, 0.6, 1])))
    rng = np.random.default_rng(21)
    cam.push(c, 0.4)
    for k in range(70):
        x, y = rng.uniform(-1.2, 1.2) * W, rng.uniform(-1.2, 1.2) * H
        r = rng.uniform(30, 55)
        p = skia.Paint(AntiAlias=True, Shader=radial((x - r * 0.3, y - r * 0.3), r * 1.4, [(170, 200, 255, ), (110, 140, 220), (60, 80, 160)]))
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 7))
        p.setAlphaf(0.55)
        c.drawCircle(x, y, r, p)
    cam.pop(c)
    cam.push(c, 0.65)
    pts = [(rng.uniform(-1.1, 1.1) * W, rng.uniform(-1.1, 1.1) * H) for _ in range(46)]
    for i, (x, y) in enumerate(pts):
        for j in range(i + 1, len(pts)):
            qx, qy = pts[j]
            if math.hypot(x - qx, y - qy) < 420:
                pp = skia.Path()
                pp.moveTo(x, y)
                pp.quadTo((x + qx) / 2 + 40 * math.sin(i + j), (y + qy) / 2 + 40 * math.cos(i * j), qx, qy)
                c.drawPath(pp, stroke((150, 190, 255), 5, 70))
        c.drawCircle(x, y, 9, fill((180, 210, 255), 120))
    cam.pop(c)
    c.drawPaint(shaded(radial((W / 2, H * 0.5), W * 0.6, [((120, 160, 255), 60), ((120, 160, 255), 0)])))


def outside_world(c, t, ground_y=600):
    """Above the skin: bright, airy, a little hazy (contrast with the fleshy inside)."""
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, ground_y), shaded(linear((0, 0), (0, ground_y), [(150, 170, 210), (205, 175, 185)])))
    light(c, 1500, 60, 700, (255, 240, 220), 60)
    rng = np.random.default_rng(6)
    for k in range(40):   # dust in the air
        c.drawCircle(rng.uniform(0, W), rng.uniform(0, ground_y), rng.uniform(1.5, 4), fill(WHITE, 90))


def macrophage(c, x, y, r, t, expr="hungry", look=(0.0, 0.0), **kw):
    max_cell(c, x, y, r, t, expr, look, body_rgb=MACRO, edge_rgb=MACRO_EDGE, rim=(255, 200, 170), **kw)


def kai_at(c, x, y, r, t, expr="determined", look=(0.0, 0.0), hop=0.0, rim=(255, 200, 150), **over):
    kai(c, x, y, r, t, pose(expr, **over), look, 0.0, hop=hop, rim=rim)


def tissue_cell(c, x, y, r, t, p, look=(0.0, 0.0), blink=0.0, hurt=1.0, seed=0.0, rgb=(214, 110, 128)):
    """A body (tissue) cell character: soft pink blob with a nucleus; 'hurt' adds a crack and a bruise."""
    pth = blob_path(x, y, [r * (1 + 0.08 * math.sin(k * 2.3 + seed) + 0.03 * math.sin(t * 2 + k)) for k in range(12)], seed)
    c.drawPath(pth, blur(fill((40, 0, 20), 90), r * 0.1))
    c.drawPath(pth, shaded(radial((x - r * 0.3, y - r * 0.35), r * 1.6, [lighten(rgb, 0.22), rgb, darken(rgb, 0.3)], [0, 0.5, 1])))
    c.save()
    c.clipPath(pth, doAntiAlias=True)
    c.drawCircle(x + r * 0.35, y + r * 0.42, r * 0.28, fill(darken(rgb, 0.35), 90))
    if hurt > 0:
        cr = skia.Path()
        cr.moveTo(x - r * 0.9, y - r * 0.55)
        cr.lineTo(x - r * 0.62, y - r * 0.42)
        cr.lineTo(x - r * 0.7, y - r * 0.25)
        cr.lineTo(x - r * 0.45, y - r * 0.12)
        c.drawPath(cr, stroke((90, 20, 40), r * 0.05, 220 * hurt))
        c.drawCircle(x - r * 0.55, y + r * 0.35, r * 0.18, fill((150, 60, 120), 90 * hurt))
    c.restore()
    c.drawPath(pth, stroke(darken(rgb, 0.45), r * 0.04))
    face_rig(c, x + look[0] * r * 0.08, y - r * 0.08, r * 0.95, p, look, blink)
