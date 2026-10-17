"""ORBI: a tiny deep-space probe, the guide of the stars video.

Design: pearl-white sphere, dark glass visor with ONE big glowing eye, two solar-panel "ears" that flap with emotion,
a springy antenna with a blinking tip, and a thruster that puffs light. Lit by the scene: rim light takes the colour
of the nearest light source. Animation principles built in: squash & stretch from velocity, banking into turns,
antenna follow-through (damped spring), anticipation via the `mood` controls.
"""
import math

from premium import *  # noqa: F401,F403

SHELL = (214, 214, 230)
SHELL_SHADE = (128, 130, 172)
VISOR = (14, 16, 34)
EYE = (90, 255, 230)
PANEL = (52, 70, 160)
PANEL_LINE = (120, 150, 255)

EXPRESSIONS = ("neutral", "happy", "wide", "squint", "worried", "sleepy")


def _eye_path(shape, er, open_):
    """Eye shapes inside the visor (local coords, eye radius er)."""
    p = skia.Path()
    if shape == "happy":        # upside-down arc ^_^
        p.moveTo(-er * 1.05, er * 0.35)
        p.quadTo(0, -er * 1.5, er * 1.05, er * 0.35)
        p.quadTo(0, -er * 0.45, -er * 1.05, er * 0.35)
        return p
    if shape == "squint":       # determined / focused slit
        p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-er, -er * 0.22, er * 2, er * 0.44), er * 0.22, er * 0.22))
        return p
    if shape == "worried":      # tilted lens with a low lid
        p.addOval(skia.Rect.MakeXYWH(-er * 0.85, -er * 0.75 * open_, er * 1.7, er * 1.5 * open_))
        lid = skia.Path()
        lid.moveTo(-er * 1.2, -er * 1.2)
        lid.lineTo(er * 1.2, -er * 1.2)
        lid.lineTo(er * 1.2, -er * 0.55)
        lid.lineTo(-er * 1.2, -er * 0.05)
        lid.close()
        return skia.Op(p, lid, skia.PathOp.kDifference_PathOp)
    if shape == "sleepy":
        p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-er * 0.9, -er * 0.1, er * 1.8, er * 0.35), er * 0.17, er * 0.17))
        return p
    sc = 1.25 if shape == "wide" else 1.0
    p.addOval(skia.Rect.MakeXYWH(-er * sc, -er * sc * open_, er * 2 * sc, er * 2 * sc * open_))
    return p


class Spring:
    """Critically-damped-ish 1D spring evaluated analytically from a target history (stateless per frame)."""

    @staticmethod
    def lag(f, t, delay=0.12, k=3):
        """Smoothed, delayed version of a function of time (cheap follow-through)."""
        return sum(f(t - delay * i / k) for i in range(k + 1)) / (k + 1)


def orbi(c, x, y, r, t, expr="neutral", look=(0.0, 0.0), vel=(0.0, 0.0), ears=0.0, thrust=0.6,
         rim=TEAL, rim2=MAGENTA, a=255, blink=True, antenna_lag=(0.0, 0.0), eye_rgb=EYE):
    """Draw ORBI centred at (x, y), body radius r.
    vel: screen velocity (px/s) -> squash/stretch + banking. ears: -1 (droop) .. 0 .. +1 (perk up/flap).
    antenna_lag: extra antenna sway (from Spring.lag of the path)."""
    if r <= 1 or a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    sp = math.hypot(*vel)
    bank = clamp(vel[0] / 900.0, -1, 1) * 18
    stretch = 1 + clamp(sp / 2400.0, 0, 0.16)
    hover = bob(t, r * 0.04, 2.6)
    c.save()
    c.translate(x, y + hover)
    c.rotate(bank)
    if sp > 1:
        ang = math.degrees(math.atan2(vel[1], vel[0]))
        c.rotate(ang)
        c.scale(stretch, 1 / stretch)
        c.rotate(-ang)

    # thruster plume (additive, behind body)
    fl = thrust * (0.85 + 0.15 * math.sin(t * 37) + 0.08 * math.sin(t * 23))
    if fl > 0.02:
        plume = skia.Path()
        plume.moveTo(-r * 0.26, r * 0.86)
        plume.quadTo(0, r * (0.9 + 1.6 * fl), r * 0.26, r * 0.86)
        plume.close()
        pp = skia.Paint(AntiAlias=True, Shader=linear((0, r * 0.86), (0, r * (0.9 + 1.5 * fl)), [(eye_rgb, 230), (rim, 0)]))
        pp.setBlendMode(skia.BlendMode.kPlus)
        c.drawPath(plume, pp)
        light(c, 0, r * 1.05, r * 1.4 * fl, eye_rgb, 120 * fl)

    # solar-panel ears (behind the shell)
    for s in (-1, 1):
        flap = ears * 22 + 6 * math.sin(t * 2.1 + s) * (0.3 + max(0, ears))
        c.save()
        c.translate(s * r * 0.92, -r * 0.05)
        c.rotate(s * (-14 - flap))
        c.drawRRect(rrect(-r * 0.06 if s > 0 else -r * 0.06, -r * 0.05, r * 0.12, r * 0.1, r * 0.03), fill(SHELL_SHADE))
        px = r * 0.08 if s > 0 else -r * 0.08 - r * 0.62
        panel = rrect(px, -r * 0.24, r * 0.62, r * 0.48, r * 0.06)
        c.drawRRect(panel, shaded(linear((px, -r * 0.24), (px + r * 0.62, r * 0.24), [lighten(PANEL, 0.25), PANEL])))
        for k in range(1, 3):
            c.drawLine(px + r * 0.62 * k / 3, -r * 0.22, px + r * 0.62 * k / 3, r * 0.22, stroke(PANEL_LINE, r * 0.015, 150))
        c.drawLine(px + r * 0.02, 0, px + r * 0.6, 0, stroke(PANEL_LINE, r * 0.015, 150))
        c.drawRRect(panel, stroke(lighten(PANEL_LINE, 0.4), r * 0.02, 120))
        # specular sweep across the panel
        sw = (t * 0.35 + (0.5 if s > 0 else 0)) % 1.6 - 0.3
        c.save()
        c.clipRRect(panel, doAntiAlias=True)
        c.drawPath(poly([(px + r * 0.62 * sw, -r * 0.3), (px + r * 0.62 * sw + r * 0.12, -r * 0.3),
                         (px + r * 0.62 * sw - r * 0.1, r * 0.3), (px + r * 0.62 * sw - r * 0.22, r * 0.3)]), fill(WHITE, 45))
        c.restore()
        c.restore()

    # antenna with follow-through
    ax, ay = antenna_lag
    sway = 10 * math.sin(t * 1.7) + ax * 30
    base = (r * 0.28, -r * 0.9)
    c.save()
    c.translate(*base)
    c.rotate(14 + sway)
    stem = skia.Path()
    stem.moveTo(0, 0)
    stem.quadTo(r * 0.05 - ay * 10, -r * 0.35, r * 0.02 - ax * 18, -r * 0.6)
    c.drawPath(stem, stroke(SHELL_SHADE, r * 0.05))
    tip = (r * 0.02 - ax * 18, -r * 0.62)
    on = 0.55 + 0.45 * (math.sin(t * 4.0) > 0.2)
    light(c, tip[0], tip[1], r * 0.35, rim2, 150 * on)
    c.drawCircle(tip[0], tip[1], r * 0.075, fill(lighten(rim2, 0.3)))
    c.restore()

    # shell: soft shadow side, rim light from the scene, specular highlight
    body = skia.Path()
    body.addCircle(0, 0, r)
    c.drawPath(body, shaded(radial((-r * 0.35, -r * 0.45), r * 1.65, [(236, 236, 246), SHELL, SHELL_SHADE, (56, 58, 100)], [0, 0.3, 0.75, 1])))
    c.save()
    c.clipPath(body, doAntiAlias=True)
    rimp = skia.Paint(AntiAlias=True, Shader=radial((-r * 0.35, -r * 0.35), r * 1.5, [(rim, 0), (rim, 0), (rim, 150)], [0, 0.76, 1]))
    rimp.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(body, rimp)
    c.drawRect(skia.Rect.MakeXYWH(-r, r * 0.38, r * 2, r * 0.08), fill(SHELL_SHADE, 120))   # panel seam
    for k in range(3):
        c.drawCircle(-r * 0.25 + k * r * 0.25, r * 0.62, r * 0.035, fill(SHELL_SHADE, 200))
    c.restore()
    c.drawOval(skia.Rect.MakeXYWH(-r * 0.6, -r * 0.86, r * 0.5, r * 0.26), fill(WHITE, 120))

    # visor
    vis = rrect(-r * 0.66, -r * 0.5, r * 1.32, r * 0.86, r * 0.42)
    c.drawRRect(vis, shaded(linear((0, -r * 0.5), (0, r * 0.36), [(28, 30, 58), VISOR])))
    c.drawRRect(vis, stroke((60, 70, 120), r * 0.035))
    # eye (blink every ~4 s)
    cyc = t % 4.2
    open_ = 1.0 - (1.0 - abs(cyc - 4.1) / 0.1 if blink and abs(cyc - 4.1) < 0.1 else 0.0)
    er = r * 0.27
    ex, ey = look[0] * r * 0.2, -r * 0.07 + look[1] * r * 0.1
    c.save()
    c.clipRRect(vis, doAntiAlias=True)
    c.translate(ex, ey)
    light(c, 0, 0, er * 3.0, eye_rgb, 90)
    ep = _eye_path(expr, er, max(0.08, open_))
    c.drawPath(ep, shaded(radial((0, -er * 0.3), er * 1.4, [lighten(eye_rgb, 0.6), eye_rgb, darken(eye_rgb, 0.25)], [0, 0.5, 1])))
    if expr in ("neutral", "wide", "worried") and open_ > 0.4:
        c.drawCircle(-er * 0.35, -er * 0.35, er * 0.22, fill(WHITE, 230))
        c.drawCircle(er * 0.3, er * 0.25, er * 0.09, fill(WHITE, 160))
    c.restore()
    # glass reflection
    refl = skia.Path()
    refl.moveTo(-r * 0.55, -r * 0.3)
    refl.quadTo(-r * 0.3, -r * 0.48, r * 0.1, -r * 0.44)
    refl.lineTo(r * 0.02, -r * 0.36)
    refl.quadTo(-r * 0.3, -r * 0.38, -r * 0.48, -r * 0.2)
    refl.close()
    c.drawPath(refl, fill(WHITE, 60))
    c.restore()
    if a < 255:
        c.restore()


if __name__ == "__main__":
    # character sheet -> out/storyboards/orbi_sheet.png
    from PIL import Image

    def sheet(c, t):
        c.drawPaint(shaded(linear((0, 0), (0, H), [DEEP, VOID])))
        Starfield(3, (300, 90, 20)).draw(c, t, Cam(), 0.6)
        text(c, "MEET ORBI", 960, 120, 72, WHITE, 255, 800, spacing=10)
        text(c, "A TINY DEEP-SPACE PROBE · OUR GUIDE THROUGH THE LIFE OF A STAR", 960, 172, 22, TEAL, 230, 800, spacing=4)
        orbi(c, 420, 560, 210, t, "neutral", look=(0.3, 0.1), ears=0.2, rim=TEAL, rim2=MAGENTA)
        text(c, "HERO POSE", 420, 900, 24, WHITE, 200, 800, spacing=4)
        for i, (e, lab, rim, ears, look) in enumerate([("happy", "HAPPY", AMBER, 0.9, (0, 0)), ("wide", "AMAZED", BLUE_STAR, 0.5, (0, -0.2)),
                                                       ("squint", "FOCUSED", TEAL, -0.1, (0.4, 0)), ("worried", "WORRIED", RED_GIANT, -0.8, (-0.3, 0.2)),
                                                       ("sleepy", "SLEEPY", VIOLET2, -0.5, (0, 0.3)), ("neutral", "CURIOUS", MAGENTA, 0.3, (-0.6, -0.3))]):
            x, y = 960 + (i % 3) * 330, 360 + (i // 3) * 340
            orbi(c, x, y, 95, t + i, e, look=look, ears=ears, rim=rim, rim2=MAGENTA, thrust=0.45)
            text(c, lab, x, y + 175, 22, WHITE, 220, 800, spacing=4)
        text(c, "EXPRESSIVE EYE · FLAPPING PANEL EARS · SPRINGY ANTENNA · THRUSTER · RIM LIGHT FROM THE SCENE", 960, 1040, 18, WHITE, 150, 800, spacing=3)

    from premium import render_premium
    os.makedirs(os.path.join(HERE, "out", "storyboards"), exist_ok=True)
    out = os.path.join(HERE, "out", "storyboards", "orbi_sheet.png")
    Image.fromarray(render_premium(sheet, 1.3, samples=1)).save(out)
    print(out)
