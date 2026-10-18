"""The macrophage, 'the big eater': a plump pear-shaped cell with a polka-dot bib, stretchy arms that reach for food,
a huge rig mouth, and a belly window where swallowed bacteria visibly dissolve.  python3 bigeater.py -> sheet."""
import math

import numpy as np

from cells import bacterium, LYSO, GERM
from rig import *  # noqa: F401,F403

EATER = (78, 150, 176)
EATER_DARK = (40, 86, 112)
BIB = (250, 246, 236)
BIB_DOT = (232, 84, 96)


def _arm(c, sx, sy, tx, ty, r, side, t):
    """Stretchy pseudopod arm from shoulder (sx, sy) to hand (tx, ty), tapered, with a soft hand."""
    mx, my = (sx + tx) / 2 + side * r * 0.25, (sy + ty) / 2 + r * 0.25
    p = skia.Path()
    p.moveTo(sx, sy)
    p.quadTo(mx, my, tx, ty)
    c.drawPath(p, stroke(darken(EATER, 0.3), r * 0.26))
    c.drawPath(p, stroke(EATER, r * 0.2))
    c.drawCircle(tx, ty, r * 0.16, fill(lighten(EATER, 0.12)))
    c.drawCircle(tx, ty, r * 0.16, stroke(darken(EATER, 0.35), r * 0.03))


def eater(c, x, y, r, t, p, look=(0.0, 0.0), blink=0.0, hands=(None, None), belly=(), a=255, rim=(255, 190, 170), chomp=0.0):
    """p: rig pose. hands: target points (world) for left/right arm or None for resting. belly: [(dx, dy, size, digest)].
    chomp: 0..1 impulse that squashes the body on a bite."""
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    c.save()
    c.translate(x, y + bob(t, r * 0.025, 2.6))
    sq = p["squash"] * (1 - 0.06 * chomp)
    c.drawOval(skia.Rect.MakeXYWH(-r * 0.95, r * 0.95, r * 1.9, r * 0.3), blur(fill((40, 0, 20), 70), r * 0.1))
    # resting arm positions
    rest = [(-r * 1.15, r * 0.45 + r * 0.05 * math.sin(t * 2.1)), (r * 1.15, r * 0.45 + r * 0.05 * math.sin(t * 2.1 + 1))]
    arms = []
    for i, side in enumerate((-1, 1)):
        h = hands[i]
        hx, hy = (h[0] - x, h[1] - y) if h else rest[i]
        arms.append((side * r * 0.82, r * 0.2, hx, hy, side))
    for sx, sy, hx, hy, side in arms:     # arms behind the body
        _arm(c, sx, sy, hx, hy, r, side, t)
    c.save()
    c.translate(0, r)
    c.scale(1 / math.sqrt(sq), sq)
    c.translate(0, -r)
    n = 48
    rad = []
    for i in range(n):
        th = 2 * math.pi * i / n
        pear = 1 + 0.1 * math.sin(th)                    # heavier at the bottom
        rad.append(r * pear * (1 + 0.02 * math.sin(3 * th + t * 2) + 0.012 * math.sin(5 * th - t * 2.6)))
    body = blob_path(0, r * 0.05, rad)
    c.drawPath(body, blur(fill((40, 0, 20), 80), r * 0.1))
    c.drawPath(body, shaded(radial((-r * 0.35, -r * 0.35), r * 1.7, [lighten(EATER, 0.3), EATER, darken(EATER, 0.35)], [0, 0.45, 1])))
    c.save()
    c.clipPath(body, doAntiAlias=True)
    # swallowed bacteria show through the translucent body (lower half), each in a glowing digestive bubble
    for bx, by, bs, dg in belly:
        if dg >= 1:
            continue
        cx_, cy_ = bx * r, r * 0.66 + by * r
        c.drawCircle(cx_, cy_, bs * r * 1.5, fill(lighten(EATER, 0.4), 110 * (1 - dg * 0.5)))
        bacterium(c, cx_, cy_, bs * r * (1 - 0.55 * dg), t, 20 + 120 * dg, a=220 * (1 - dg), face_on=dg < 0.35,
                  mood="scared", flag=dg < 0.5, wiggle=0.6)
        for v in range(7):
            va = v / 7 * 6.28 + t * 1.1
            vd = bs * r * (1.3 - 0.4 * dg)
            c.drawCircle(cx_ + math.cos(va) * vd, cy_ + math.sin(va) * vd * 0.8, r * 0.03, fill(LYSO, 200 * (1 - dg * 0.5)))
    rng = np.random.default_rng(5)
    for k in range(18):
        c.drawCircle(rng.uniform(-0.8, 0.8) * r, rng.uniform(-0.8, 0.2) * r, r * rng.uniform(0.015, 0.03), fill(darken(EATER, 0.25), 120))
    rp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.2, Shader=linear((-r, -r), (r, r), [(rim, 20), (rim, 140)]))
    rp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.06))
    rp.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(body, rp)
    c.restore()
    c.drawPath(body, stroke(darken(EATER, 0.45), r * 0.035))
    c.drawOval(skia.Rect.MakeXYWH(-r * 0.6, -r * 0.85, r * 0.5, r * 0.2), fill(WHITE, 60))
    # face (big mouth)
    face_rig(c, look[0] * r * 0.08, -r * 0.22 + look[1] * r * 0.04, r * 1.0, p, look, blink, spread=0.3)
    # bib tied under the mouth (drawn over the body, under nothing): a little napkin with polka dots
    by = -r * 0.22 + r * 1.0 * (0.36 + 0.09 * p["curve"] + 0.42 * p["open"]) + r * 0.08
    bib = skia.Path()
    bib.moveTo(-r * 0.34, by)
    bib.quadTo(0, by + r * 0.07, r * 0.34, by)
    bib.lineTo(r * 0.22, by + r * 0.3)
    bib.quadTo(0, by + r * 0.42, -r * 0.22, by + r * 0.3)
    bib.close()
    c.drawPath(bib, blur(fill((30, 0, 20), 60), r * 0.04))
    c.drawPath(bib, fill(BIB))
    c.save()
    c.clipPath(bib, doAntiAlias=True)
    for k in range(6):
        c.drawCircle(-r * 0.2 + (k % 3) * r * 0.2 + (r * 0.1 if (k // 3) % 2 else 0), by + r * 0.1 + (k // 3) * r * 0.14, r * 0.04, fill(BIB_DOT))
    c.restore()
    c.drawPath(bib, stroke((200, 190, 180), r * 0.02))
    for side in (-1, 1):   # ties
        c.drawCircle(side * r * 0.34, by, r * 0.05, fill(BIB))
    c.restore()
    c.restore()
    if a < 255:
        c.restore()


if __name__ == "__main__":
    import os
    from PIL import Image
    from heroes import body_world
    from premium import render_premium

    def sheet(c, t):
        body_world(c, t)
        text(c, "THE BIG EATER · MACROPHAGE", 960, 90, 46, WHITE, 255, 800, spacing=8)
        eater(c, 520, 560, 210, t, pose("happy"), (0.2, 0), belly=((-0.45, 0.0, 0.14, 0.4), (0.45, 0.05, 0.13, 0.8)))
        bacterium(c, 1060, 420, 40, t, 200, mood="scared", wiggle=3)
        eater(c, 1300, 360, 120, t, pose("gulp"), (-0.5, -0.2), hands=((1080, 400), (1090, 470)))
        eater(c, 1150, 800, 100, t, pose("chew"), (0, 0), belly=((-0.45, 0, 0.15, 0.1),))
        eater(c, 1600, 800, 100, t, pose("shocked"), (0.5, 0))
    out = os.path.join(HERE, "out", "storyboards", "big_eater.png")
    Image.fromarray(render_premium(sheet, 1.3, samples=1)).save(out)
    print(out)
