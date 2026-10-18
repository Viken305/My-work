"""KAI, the killer T cell: the hero, built on the animated face rig (rig.py).

Body acting comes from the same pose: squash (stretch when shocked), perk (the receptor crown bristles up when
alert, droops when worried), lean. Secondary motion: bandana tails flutter, receptors sway with a lag.
"""
import math

from rig import *  # noqa: F401,F403

KAI_BODY = (255, 104, 84)
KAI_DARK = (40, 44, 86)
LOCK = (255, 220, 120)


def kai(c, x, y, r, t, p, look=(0.0, 0.0), blink=0.0, vel=(0.0, 0.0), rim=(255, 200, 150), a=255, hop=0.0):
    """p: pose dict from rig (Track.at). hop: extra vertical squash impulse (-1..1)."""
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    sp = math.hypot(*vel)
    c.save()
    c.translate(x, y + bob(t, r * 0.03, 2.2))
    c.rotate(p["lean"] + clamp(vel[0] / 900, -1, 1) * 8)
    sq = p["squash"] * (1 + 0.12 * hop) * (1 + 0.015 * math.sin(t * 2.6))
    # contact shadow stays unsquashed
    c.drawOval(skia.Rect.MakeXYWH(-r * 0.9, r * 1.05, r * 1.8, r * 0.28), blur(fill((60, 0, 20), 70), r * 0.1))
    c.save()
    c.translate(0, r)
    c.scale(1 / math.sqrt(sq), sq)
    c.translate(0, -r)
    # receptor crown (behind the body): longer on top like a hairdo, perk lifts and stiffens it
    perk = p["perk"]
    for k in range(17):
        an0 = math.radians(-180 + k * (360 / 17))
        top = math.sin(an0) < -0.3
        sag = (1 - min(perk, 1.0)) * 0.6 * math.cos(an0)        # drooping bends receptors downward
        an = an0 + sag * (1 if math.cos(an0) > 0 else -1) * 0.5 + 0.04 * math.sin(t * 2.4 + k * 0.7)
        ln = r * (0.32 if top else 0.16) * (0.6 + 0.4 * perk)
        bx, by = math.cos(an0) * r * 0.95, math.sin(an0) * r * 0.95
        ex, ey = math.cos(an) * (r + ln), math.sin(an) * (r + ln)
        mx, my = math.cos((an0 + an) / 2) * (r + ln * 0.5), math.sin((an0 + an) / 2) * (r + ln * 0.5)
        st = skia.Path()
        st.moveTo(bx, by)
        st.quadTo(mx, my, ex, ey)
        c.drawPath(st, stroke(darken(KAI_BODY, 0.3), r * 0.08))
        cup = skia.Path()
        cup.addArc(skia.Rect.MakeXYWH(ex - r * 0.09, ey - r * 0.09, r * 0.18, r * 0.18), math.degrees(an) + 90, 180)
        c.drawPath(cup, stroke(LOCK, r * 0.05))
    body = skia.Path()
    body.addCircle(0, 0, r)
    c.drawPath(body, blur(fill((60, 0, 20), 80), r * 0.1))
    c.drawPath(body, shaded(radial((-r * 0.35, -r * 0.3), r * 1.6, [lighten(KAI_BODY, 0.28), KAI_BODY, darken(KAI_BODY, 0.35)], [0, 0.45, 1])))
    c.save()
    c.clipPath(body, doAntiAlias=True)
    c.drawCircle(r * 0.15, r * 0.35, r * 0.6, fill(darken(KAI_BODY, 0.4), 45))      # nucleus
    rp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.2, Shader=linear((-r, -r), (r, r), [(rim, 20), (rim, 140)]))
    rp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.06))
    rp.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(body, rp)
    band = skia.Path()     # bandana rides up with raised brows
    by = -r * (0.7 + 0.05 * max(0.0, p["brow_y"]))
    band.moveTo(-r * 1.1, by)
    band.quadTo(0, by - r * 0.23, r * 1.1, by)
    band.lineTo(r * 1.1, by + r * 0.25)
    band.quadTo(0, by + r * 0.02, -r * 1.1, by + r * 0.25)
    band.close()
    c.drawPath(band, fill(KAI_DARK))
    c.drawPath(band, stroke(lighten(KAI_DARK, 0.25), r * 0.015, 160))
    c.restore()
    c.drawPath(body, stroke(darken(KAI_BODY, 0.45), r * 0.04))
    c.drawOval(skia.Rect.MakeXYWH(-r * 0.62, -r * 0.84, r * 0.5, r * 0.2), fill(WHITE, 60))
    # bandana tails: flutter faster when moving or excited
    spd = 6 + sp / 120 + 4 * max(0.0, perk - 1)
    for k in (0, 1):
        tail = skia.Path()
        tail.moveTo(r * 0.94, by + r * 0.1)
        for j in range(1, 9):
            u = j / 8
            tail.lineTo(r * (0.94 + 0.6 * u), by + r * 0.1 + r * (0.1 + 0.2 * k) * u + r * 0.09 * u * math.sin(t * spd - u * 5 + k * 1.3))
        c.drawPath(tail, stroke(KAI_DARK, r * (0.12 - 0.03 * k)))
    c.drawLine(-r * 0.66, -r * 0.08, -r * 0.47, r * 0.2, stroke(darken(KAI_BODY, 0.5), r * 0.035, 150))   # scar
    face_rig(c, look[0] * r * 0.08, r * 0.06 + look[1] * r * 0.04, r, p, look, blink, skin=KAI_BODY,
             skin_shader=lambda: radial((-r * 0.35, -r * 0.3), r * 1.6, [lighten(KAI_BODY, 0.28), KAI_BODY, darken(KAI_BODY, 0.35)], [0, 0.45, 1]))
    c.restore()
    c.restore()
    if a < 255:
        c.restore()
