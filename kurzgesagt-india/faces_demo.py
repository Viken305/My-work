"""Test clip: how the leaders' faces come to life (blink, breathe, tilt, glance; mouths never move).

  python3 faces_demo.py   -> out/storyboards/faces_demo.mp4
"""
import os, subprocess

from faces import *  # noqa: F401,F403

DURATION = 12.0
ORDER = ["ashoka", "gandhi", "nehru", "patel", "bose", "ambedkar", "modi"]


def draw_frame(c, t):
    background(c, INDIGO, ROYAL)
    Dust(50, 4, MARIGOLD).draw(c, t, 0.7)
    grid = 1 - smooth(prog(t, 6.0, 6.6))
    if grid > 0.01:
        c.saveLayerAlpha(None, int(255 * grid))
        for i, who in enumerate(ORDER):
            cx = 260 + (i % 4) * 466 if i < 4 else 493 + (i - 4) * 466
            cy = 300 if i < 4 else 790
            g = out_back(prog(t, 0.3 + i * 0.25, 0.85 + i * 0.25))
            look = (0.0, 0.0)
            if 3.4 < t < 5.4:  # everyone glances toward the centre, then back
                k = smooth(prog(t, 3.4, 3.8)) * (1 - smooth(prog(t, 5.0, 5.4)))
                look = (clamp((960 - cx) / 600, -1, 1) * k, clamp((540 - cy) / 400, -1, 1) * k)
            leader_card(c, cx, cy, who, t, 1.05 * g, 255, look, phase=i * 0.7)
        c.restore()
    big = smooth(prog(t, 6.2, 6.9))
    if big > 0.01:
        c.saveLayerAlpha(None, int(255 * big))
        for i, who in enumerate(("gandhi", "modi")):
            leader_card(c, 600 + i * 720, 560, who, t, 2.0 * out_back(prog(t, 6.2 + i * 0.2, 6.9 + i * 0.2)), 255,
                        (0.6 * math.sin(t * 0.8 + i), 0.0), phase=i * 1.3)
        c.restore()
    text(c, "BLINK · BREATHE · GLANCE · NO LIP-SYNC", 960, 1050, 22, WHITE, 180, 800, spacing=4)
    vignette(c, 100)
    a = max(1 - smooth(prog(t, 0, 0.3)), smooth(prog(t, DURATION - 0.4, DURATION)))
    if a > 0:
        c.drawPaint(fill((8, 8, 24), 255 * a))


if __name__ == "__main__":
    import render
    v = render.render_video("faces_demo")
    out = os.path.join(HERE, "out", "storyboards", "faces_demo.mp4")
    render.encode(v, out, 24)
    print(out)
