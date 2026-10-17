"""12-second premium motion test: nebula parallax, ORBI fly-in with motion blur, collapse + ignition, flare.

  python3 motion_test.py    -> out/storyboards/motion_test.mp4
"""
import os

from cosmos import *  # noqa: F401,F403

PREMIUM, SAMPLES = True, 4
DURATION = 12.0
_SF = Starfield(2)
_BK = Bokeh(5)
IGNITE = 7.2


def path_orbi(t):
    """ORBI's flight: swoops in from the left with anticipation, settles, then reacts to the ignition."""
    k = out_back(prog(t, 0.8, 3.0), 1.1)
    x = lerp(-250, 1380, k) + 30 * math.sin(t * 0.9)
    y = lerp(820, 610, smooth(prog(t, 0.8, 3.0))) + 20 * math.sin(t * 1.3)
    recoil = smooth(prog(t, IGNITE, IGNITE + 0.25)) * (1 - smooth(prog(t, IGNITE + 0.25, IGNITE + 1.6)))
    return x + 90 * recoil, y + 30 * recoil


def draw_frame(c, t):
    cam = Cam(lerp(-80, 80, smooth(prog(t, 0, DURATION))), lerp(30, -20, smooth(prog(t, 0, DURATION))), lerp(1.0, 1.12, in_out(prog(t, 0, DURATION))))
    shake = math.exp(-max(0.0, t - IGNITE) * 3) * (t > IGNITE) * 6
    cam.x += shake * math.sin(t * 61)
    cam.y += shake * math.cos(t * 53)
    c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.8, [DEEP, VOID])))
    _SF.draw(c, t, cam)
    cam.push(c, 0.35)
    draw_texture(c, tex_teal(), 300, -150, 1.4, t * 0.6, 150)
    cam.pop(c)
    cam.push(c, 0.55)
    draw_texture(c, tex_cloud(), -120, 60, 1.25, -t * 0.8, 210, skia.BlendMode.kPlus)
    cam.pop(c)
    # the clump collapsing into a protostar, then igniting
    cx, cy = -60, 20
    coll = smooth(prog(t, 2.5, IGNITE))
    cam.push(c, 0.8)
    draw_texture(c, tex_cloud(12), cx, cy, lerp(0.75, 0.18, coll), t * 25 * coll, 255 * (1 - smooth(prog(t, IGNITE - 0.5, IGNITE + 0.5))))
    if t < IGNITE + 0.3:
        protostar(c, cx, cy, lerp(36, 26, coll), t, coll, 255 * smooth(prog(t, 3.0, 4.5)))
    if t >= IGNITE - 0.1:
        g = out_back(prog(t, IGNITE, IGNITE + 1.2), 1.4)
        star(c, cx, cy, 70 * g, t, SOLAR, 1.0)
        shockwave(c, cx, cy, 700, t, prog(t, IGNITE, IGNITE + 3.2))
    cam.pop(c)
    # ORBI
    x, y = path_orbi(t)
    dt = 1 / 60
    x2, y2 = path_orbi(t + dt)
    vel = ((x2 - x) / dt, (y2 - y) / dt)
    lag = ((path_orbi(t - 0.12)[0] - x) / 400, (path_orbi(t - 0.12)[1] - y) / 400)
    expr = "neutral" if t < 4.2 else ("squint" if t < IGNITE else ("wide" if t < IGNITE + 1.6 else "happy"))
    look = (-0.8, -0.1) if t > 3.2 else (0.4, 0)
    ears = 0.2 if t < IGNITE else (1.0 if t < IGNITE + 1.6 else 0.7)
    rim = mix(TEAL, SOLAR, smooth(prog(t, IGNITE, IGNITE + 0.6)))
    orbi(c, x, y, 110, t, expr, look, vel, ears, 0.4 + min(1.0, math.hypot(*vel) / 900), rim=rim, rim2=MAGENTA, antenna_lag=lag)
    _BK.draw(c, t, cam)
    # title
    ta = smooth(prog(t, 9.6, 10.4))
    if ta > 0:
        text(c, "PREMIUM MOTION TEST", 960, 980, 34, WHITE, 230 * ta, 800, spacing=10)
        text(c, "MOTION BLUR · BLOOM · PARALLAX · DEPTH OF FIELD · LENS FLARE · COLOUR GRADE", 960, 1025, 18, TEAL, 210 * ta, 800, spacing=4)
    a = max(1 - smooth(prog(t, 0, 0.5)), smooth(prog(t, DURATION - 0.5, DURATION)))
    if a > 0:
        c.drawPaint(fill(VOID, 255 * a))


if __name__ == "__main__":
    import render
    v = render.render_video("motion_test")
    out = os.path.join(HERE, "out", "storyboards", "motion_test.mp4")
    render.encode(v, out, 22)
    print(out)
