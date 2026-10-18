"""NIMBUS, a little cloud who drifts around the world: the guide of this video.

Fluffy body made of overlapping puffs that breathe and roll; two small puff 'hands' that point, wave and cover the eyes;
the shared face rig (rig.py) so every expression change is animated; weather moods: rain when sad, a tiny lightning bolt
when shocked or angry, sunbeam sparkle when happy. Squash/stretch and banking from velocity.  python3 nimbus.py -> sheet.
"""
import math

from rig import *  # noqa: F401,F403

CLOUD = (216, 224, 242)
CLOUD_SHADE = (156, 170, 214)
CLOUD_DEEP = (100, 112, 172)
PUFFS = [(0.0, -0.32, 0.62), (-0.48, -0.12, 0.48), (0.5, -0.14, 0.5), (-0.82, 0.18, 0.36), (0.84, 0.16, 0.38),
         (-0.36, 0.3, 0.46), (0.34, 0.3, 0.48), (0.0, 0.18, 0.62), (0.2, -0.55, 0.36), (-0.24, -0.5, 0.32)]


def _body(r, t, sq):
    p = skia.Path()
    for i, (px, py, pr) in enumerate(PUFFS):
        b = 1 + 0.045 * math.sin(t * 2.1 + i * 1.7)
        p.addCircle(px * r * (1 + 0.04 * math.sin(t * 1.3 + i)), py * r * sq, pr * r * b)
    p.setFillType(skia.PathFillType.kWinding)
    return skia.Op(p, skia.Path(), skia.PathOp.kUnion_PathOp) or p


def _hand(c, x, y, s, rim):
    c.drawCircle(x, y, s, shaded(radial((x - s * 0.3, y - s * 0.3), s * 1.5, [(232, 237, 248), CLOUD, CLOUD_SHADE], [0, 0.5, 1])))
    c.drawCircle(x, y, s, stroke(CLOUD_DEEP, s * 0.12, 200))


def nimbus(c, x, y, r, t, p, look=(0.0, 0.0), blink=0.0, vel=(0.0, 0.0), rain=0.0, zap=0.0, hands=(None, None), a=255,
           rim=(255, 210, 160), tint=None, sparkle_=0.0):
    """p: rig pose. hands: (x, y) world points for the left/right puff hands, or None for resting at the sides.
    rain / zap / sparkle_: 0..1 weather moods. tint: optional colour wash (e.g. grey storm cloud, warm sunset)."""
    if a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    sp = math.hypot(*vel)
    bank = clamp(vel[0] / 900.0, -1, 1) * 10
    hover = bob(t, r * 0.05, 3.0)
    # rain (behind)
    if rain > 0.01:
        for k in range(14):
            u = (t * 1.6 + k * 0.137) % 1.0
            dx = (k / 13 - 0.5) * r * 1.4
            dy = r * 0.55 + u * r * 1.6
            c.drawLine(x + dx, y + hover + dy, x + dx - r * 0.03, y + hover + dy + r * 0.14, stroke((140, 190, 255), r * 0.04, 230 * rain * (1 - u)))
    if zap > 0.01:
        bolt = skia.Path()
        bx, by = x + r * 0.1, y + hover + r * 0.55
        bolt.moveTo(bx, by)
        bolt.lineTo(bx - r * 0.18, by + r * 0.42)
        bolt.lineTo(bx + r * 0.02, by + r * 0.4)
        bolt.lineTo(bx - r * 0.14, by + r * 0.85)
        bolt.lineTo(bx + r * 0.22, by + r * 0.3)
        bolt.lineTo(bx + r * 0.02, by + r * 0.32)
        bolt.close()
        light(c, bx, by + r * 0.4, r * 0.9, (255, 240, 140), 200 * zap)
        c.drawPath(bolt, fill((255, 236, 120), 255 * zap))
    c.save()
    c.translate(x, y + hover)
    c.rotate(bank)
    st = 1 + clamp(sp / 2400.0, 0, 0.16)
    if sp > 1:
        ang = math.degrees(math.atan2(vel[1], vel[0]))
        c.rotate(ang)
        c.scale(st, 1 / st)
        c.rotate(-ang)
    sq = p["squash"]
    c.scale(1 / math.sqrt(sq), sq)
    body = _body(r, t, 1.0)
    c.drawPath(body, blur(fill((20, 30, 80), 60), r * 0.12))
    sh = shaded(radial((-r * 0.35, -r * 0.6), r * 2.0, [(232, 237, 248), CLOUD, CLOUD_SHADE, CLOUD_DEEP], [0, 0.35, 0.75, 1]))
    c.drawPath(body, sh)
    c.save()
    c.clipPath(body, doAntiAlias=True)
    # soft inner puff shading: each puff gets a light top and a shaded bottom
    for i, (px, py, pr) in enumerate(PUFFS):
        b = 1 + 0.045 * math.sin(t * 2.1 + i * 1.7)
        cx_, cy_ = px * r, py * r
        c.drawCircle(cx_, cy_ + pr * r * 0.35, pr * r * b * 0.9, fill(CLOUD_SHADE, 70))
        c.drawCircle(cx_ - pr * r * 0.2, cy_ - pr * r * 0.3, pr * r * b * 0.6, fill((236, 240, 250), 70))
    if tint:
        c.drawPaint(fill(tint[0], tint[1]))
    rp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.22, Shader=linear((-r, -r), (r, r), [(rim, 10), (rim, 90)]))
    rp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.07))
    rp.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(body, rp)
    c.restore()
    c.drawPath(body, stroke(CLOUD_DEEP, r * 0.035, 230))
    face_rig(c, look[0] * r * 0.08, r * 0.08 + look[1] * r * 0.05, r * 0.82, p, look, blink, ink=(30, 34, 70), skin=CLOUD, spread=0.3)
    c.restore()
    # hands: little puffs (world space so they can reach)
    for i, side in enumerate((-1, 1)):
        h = hands[i]
        hx, hy = (h if h else (x + side * r * 1.05, y + hover + r * 0.35 + r * 0.04 * math.sin(t * 2.4 + side)))
        _hand(c, hx, hy, r * 0.17, rim)
    if sparkle_ > 0.01:
        for k in range(3):
            an = t * 1.5 + k * 2.1
            sparkle(c, x + math.cos(an) * r * 1.2, y + hover - r * 0.4 + math.sin(an) * r * 0.5, r * 0.18 * sparkle_, 255 * sparkle_, (255, 240, 170))
    if a < 255:
        c.restore()


if __name__ == "__main__":
    import os
    from PIL import Image
    from premium import render_premium

    def sheet(c, t):
        c.drawPaint(shaded(linear((0, 0), (0, H), [(40, 90, 180), (110, 160, 220)])))
        light(c, 1600, 120, 700, (255, 240, 200), 40)
        text(c, "MEET NIMBUS", 960, 110, 72, WHITE, 255, 800, spacing=10)
        text(c, "A LITTLE CLOUD WHO DRIFTS AROUND THE WORLD", 960, 160, 22, (230, 245, 255), 230, 800, spacing=4)
        nimbus(c, 480, 560, 230, t, pose("happy"), (0.2, 0), sparkle_=1.0, hands=(None, (720, 330)))
        for i, (e, lab, kw) in enumerate([("shocked", "SHOCKED", dict(zap=1.0)), ("worried", "SAD", dict(rain=1.0)), ("laugh", "LAUGH", {}),
                                          ("smug", "SMUG", {}), ("focused", "CURIOUS", {}), ("wink", "WINK", {})]):
            x, y = 1070 + (i % 3) * 290, 380 + (i // 3) * 360
            nimbus(c, x, y, 105, t + i * 0.6, pose(e), (0.3, 0), **kw)
            text(c, lab, x, y + 190, 20, WHITE, 230, 800, spacing=4)
    os.makedirs(os.path.join(HERE, "out", "storyboards"), exist_ok=True)
    out = os.path.join(HERE, "out", "storyboards", "nimbus_sheet.png")
    Image.fromarray(render_premium(sheet, 1.3, samples=1)).save(out)
    print(out)
