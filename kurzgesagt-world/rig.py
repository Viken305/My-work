"""Animated face rig: every expression is a set of continuous controls, so changes are real animation
(eyelids close, brows travel, the mouth reshapes) instead of swapping drawings.

Controls (a "pose"):
  eo        eye opening (upper lid), 0 closed .. 1 open
  lower     lower lid rise (happy squint), lower_curve bends it into a smile-arc
  tilt      upper-lid tilt: + angry (inner corner down), - sad
  size      eye size, pupil pupil size
  wink_l/_r extra closing per eye
  brow_y    brow height, brow_tilt (+ angry, - worried), brow_raise_l/_r one-brow raise
  curve     mouth corners: -1 frown .. 1 smile;  open 0..1;  mw width;  skew smirk;  teeth
  blush     cheeks
  body controls (used by the character): squash, perk (receptor crown), lean
"""
import math

from premium import *  # noqa: F401,F403

BASE = dict(eo=1.0, lower=0.0, lower_curve=0.0, tilt=0.0, size=1.0, pupil=0.46, wink_l=0.0, wink_r=0.0,
            brow_y=0.0, brow_tilt=0.0, brow_raise_l=0.0, brow_raise_r=0.0,
            curve=0.35, open=0.0, mw=0.8, skew=0.0, teeth=0.0, blush=0.0,
            squash=1.0, perk=1.0, lean=0.0)

POSES = {
    "neutral": {},
    "happy": dict(lower=0.5, lower_curve=1.0, brow_y=0.22, brow_tilt=-0.1, curve=1.0, open=0.32, mw=1.0, teeth=1.0, blush=0.6, perk=1.1, squash=1.03),
    "laugh": dict(eo=0.04, lower=0.78, lower_curve=1.0, brow_y=0.35, brow_tilt=-0.15, curve=1.0, open=0.8, mw=1.12, teeth=1.0, blush=1.0, perk=1.2, squash=1.06, lean=-4),
    "determined": dict(eo=0.78, tilt=0.4, brow_y=-0.25, brow_tilt=0.5, curve=0.3, mw=0.7, skew=0.55, perk=1.15),
    "focused": dict(eo=0.5, tilt=0.22, brow_y=-0.3, brow_tilt=0.3, curve=0.0, mw=0.45, perk=1.05, lean=6),
    "shocked": dict(size=1.2, pupil=0.27, brow_y=0.65, brow_tilt=-0.2, curve=0.0, open=0.7, mw=0.42, perk=1.6, squash=0.9),
    "worried": dict(eo=0.92, tilt=-0.35, brow_y=0.28, brow_tilt=-0.55, curve=-0.65, open=0.1, mw=0.6, perk=0.65, squash=0.96, lean=-3),
    "smug": dict(eo=0.6, tilt=0.05, brow_raise_r=0.55, brow_tilt=0.1, curve=0.65, mw=0.72, skew=0.85, perk=1.1, lean=4),
    "wink": dict(eo=0.95, wink_l=1.0, lower=0.2, lower_curve=1.0, brow_raise_r=0.3, curve=0.85, mw=0.85, skew=0.5, open=0.12, teeth=0.6, perk=1.15),
    "shout": dict(size=1.1, pupil=0.32, brow_y=0.5, brow_tilt=-0.45, tilt=-0.15, curve=-0.2, open=0.95, mw=0.75, teeth=0.8, perk=1.4, squash=0.94),
    "hurt": dict(eo=0.62, tilt=-0.4, brow_y=0.2, brow_tilt=-0.6, curve=-0.7, open=0.18, mw=0.6, squash=0.97),
    "exhausted": dict(eo=0.25, tilt=-0.2, brow_y=-0.05, brow_tilt=-0.3, curve=-0.3, mw=0.5, squash=0.92, perk=0.6),
    "cheer": dict(lower=0.45, lower_curve=1.0, brow_y=0.4, brow_tilt=-0.1, curve=1.0, open=0.85, mw=1.0, teeth=1.0, blush=0.7, perk=1.4, squash=1.05),
    "gulp": dict(size=1.05, pupil=0.4, brow_y=0.3, curve=0.3, open=1.0, mw=1.25, teeth=0.4, squash=1.03),
    "chew": dict(eo=0.55, lower=0.25, lower_curve=1.0, curve=0.5, open=0.0, mw=0.55, blush=0.9),
    "angry": dict(eo=0.7, tilt=0.55, brow_y=-0.35, brow_tilt=0.7, curve=-0.4, open=0.25, mw=0.75, teeth=1.0, perk=1.3),
}


def pose(name, **over):
    p = dict(BASE)
    p.update(POSES[name])
    p.update(over)
    return p


def blend(a, b, k):
    return {key: a[key] + (b[key] - a[key]) * k for key in a}


class Track:
    """Expression timeline: [(t_start, name, transition_seconds)]. Overshoot easing gives snap and settle."""

    def __init__(self, keys, overshoot=1.25):
        self.keys = keys
        self.os = overshoot

    def at(self, t):
        cur = pose(self.keys[0][1])
        for i in range(1, len(self.keys)):
            t0, name, dur = self.keys[i]
            if t < t0:
                break
            k = out_back(prog(t, t0, t0 + dur), self.os)
            cur = blend(cur, pose(name), k)
        return cur

    def name_at(self, t):
        n = self.keys[0][1]
        for t0, name, _ in self.keys:
            if t >= t0:
                n = name
        return n

    def change_times(self):
        return [k[0] for k in self.keys[1:]]


def blink_amount(t, extra=(), period=3.7, phase=0.0):
    """0..1 lid closing: periodic blinks plus blinks at expression changes (classic animation trick)."""
    b = 0.0
    u = (t + phase) % period
    if u < 0.16:
        b = math.sin(math.pi * u / 0.16)
    for te in extra:
        if te <= t < te + 0.16:
            b = max(b, math.sin(math.pi * (t - te) / 0.16) * 0.9)
    return b


def saccade(t, targets):
    """Eye darts: targets [(t, (x, y))]; each move takes 0.09 s, then holds (with a tiny drift)."""
    cur = targets[0][1]
    for i in range(1, len(targets)):
        t0, tgt = targets[i]
        if t < t0:
            break
        k = smooth(prog(t, t0, t0 + 0.09))
        cur = (lerp(cur[0], tgt[0], k), lerp(cur[1], tgt[1], k))
    return cur[0] + 0.03 * math.sin(t * 1.7), cur[1] + 0.03 * math.cos(t * 1.3)


def face_rig(c, x, y, s, p, look=(0.0, 0.0), blink=0.0, ink=(16, 14, 40), skin=(255, 104, 84), spread=0.27, skin_shader=None):
    """skin_shader: the body's own shader (same coordinates) so eyelids match the shading exactly."""
    lid_paint = (lambda: shaded(skin_shader())) if skin_shader else (lambda: fill(darken(skin, 0.06)))
    er = s * 0.2 * p["size"]
    for side in (-1, 1):
        ex, ey = x + side * s * spread, y
        w, h = er, er * 1.12
        wink = p["wink_l"] if side < 0 else p["wink_r"]
        eo = clamp(p["eo"] * (1 - blink) * (1 - wink), 0.0, 1.2)
        lower = clamp(p["lower"] + wink * 0.35, 0.0, 0.95)
        tilt = p["tilt"] * (-side)          # inner corner = towards the centre
        oval = skia.Rect.MakeXYWH(ex - w, ey - h, 2 * w, 2 * h)
        # the visible part of the eye = oval minus what the lids cover (no skin plates, so no colour mismatch)
        top = ey - h + 2 * h * (1 - eo)
        lc = p["lower_curve"] * lower
        bot = max(ey + h - 2 * h * lower, top + h * 0.1)
        vis = skia.Path()
        vis.moveTo(ex - w * 1.4, top - tilt * h * 0.9)
        vis.lineTo(ex + w * 1.4, top + tilt * h * 0.9)
        if lower > 0.01:
            vis.lineTo(ex + w * 1.4, bot + h * 0.35 * lc)
            vis.quadTo(ex, bot - h * 0.55 * lc, ex - w * 1.4, bot + h * 0.35 * lc)
        else:
            vis.lineTo(ex + w * 1.4, ey + h * 1.6)
            vis.lineTo(ex - w * 1.4, ey + h * 1.6)
        vis.close()
        ov = skia.Path()
        ov.addOval(oval)
        shown = skia.Op(ov, vis, skia.PathOp.kIntersect_PathOp) if eo > 0.06 else None
        if shown is not None and not shown.isEmpty():
            c.save()
            c.clipPath(shown, doAntiAlias=True)
            c.drawOval(oval, fill((252, 252, 255)))
            lx, ly = look[0] * w * 0.42, look[1] * h * 0.35
            pr = er * p["pupil"] / 0.46 * 0.58
            c.drawCircle(ex + lx, ey + ly, pr, fill(ink))
            c.drawCircle(ex + lx - pr * 0.35, ey + ly - pr * 0.4, pr * 0.34, fill(WHITE, 235))
            c.drawCircle(ex + lx + pr * 0.3, ey + ly + pr * 0.3, pr * 0.12, fill(WHITE, 150))
            c.drawRect(skia.Rect.MakeXYWH(ex - w * 1.4, top - h * 0.6, w * 2.8, h * 0.75), fill(ink, 28))   # lid shadow
            c.restore()
            c.drawPath(shown, stroke(ink, er * 0.13, 230))
            # heavier upper-lid line
            c.save()
            c.clipRRect(skia.RRect.MakeOval(skia.Rect.MakeXYWH(ex - w * 1.05, ey - h * 1.05, w * 2.1, h * 2.1)), doAntiAlias=True)
            c.drawLine(ex - w * 1.4, top - tilt * h * 0.9, ex + w * 1.4, top + tilt * h * 0.9, stroke(ink, er * 0.2))
            c.restore()
        else:
            # closed: a curved lid line (smiling ^ when the lower lid is curved, soft u otherwise)
            cy_ = ey + h * 0.25
            bend = h * (1.0 * lc - 0.35 * (1 - lc))
            cl = skia.Path()
            cl.moveTo(ex - w * 0.95, cy_ + tilt * h * 0.4 * -1)
            cl.quadTo(ex, cy_ - bend, ex + w * 0.95, cy_ + tilt * h * 0.4)
            c.drawPath(cl, stroke(ink, er * 0.22))
        # brows
        raise_ = p["brow_raise_l"] if side < 0 else p["brow_raise_r"]
        by = ey - h * 1.45 - (p["brow_y"] + raise_) * er
        bt = p["brow_tilt"] * er * 0.55
        inner = (ex - side * w * 0.95, by + bt)
        outer = (ex + side * w * 1.05, by - bt * 0.6)
        bp = skia.Path()
        bp.moveTo(*inner)
        bp.quadTo((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - er * 0.25, *outer)
        c.drawPath(bp, stroke(ink, er * 0.34))
    # cheeks
    if p["blush"] > 0.02:
        for side in (-1, 1):
            c.drawOval(skia.Rect.MakeXYWH(x + side * s * 0.47 - s * 0.1, y + s * 0.2, s * 0.2, s * 0.1), blur(fill((255, 150, 170), 140 * p["blush"]), s * 0.03))
    # mouth: corners move with curve/skew, lips part with open
    my = y + s * 0.36
    w = s * 0.28 * p["mw"]
    lc = my - p["curve"] * s * 0.07 + p["skew"] * s * 0.03
    rc = my - p["curve"] * s * 0.07 - p["skew"] * s * 0.06
    up = my + p["curve"] * s * 0.09 * (1 - p["open"] * 0.7) - p["open"] * s * 0.05
    lo = my + p["curve"] * s * 0.09 + p["open"] * s * 0.32
    xl, xr = x - w + p["skew"] * s * 0.03, x + w + p["skew"] * s * 0.04
    if lo - up > s * 0.012:
        m = skia.Path()
        m.moveTo(xl, lc)
        m.quadTo(x, up, xr, rc)
        m.quadTo(x, lo + (lo - up) * 0.3, xl, lc)
        m.close()
        c.drawPath(m, fill((60, 12, 30)))
        c.save()
        c.clipPath(m, doAntiAlias=True)
        if p["teeth"] > 0.02:
            c.drawRect(skia.Rect.MakeXYWH(xl, up - s * 0.02, xr - xl, s * 0.06 * p["teeth"] + s * 0.02), fill(WHITE, 240))
        c.drawOval(skia.Rect.MakeXYWH(x - w * 0.55, lo - (lo - up) * 0.25, w * 1.1, (lo - up) * 0.9), fill((255, 110, 130)))
        c.restore()
        c.drawPath(m, stroke(ink, s * 0.03))
    else:
        m = skia.Path()
        m.moveTo(xl, lc)
        m.quadTo(x, up, xr, rc)
        c.drawPath(m, stroke(ink, s * 0.045))
