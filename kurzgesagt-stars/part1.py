"""Part 1: Hook. Your atoms were made in stars.

  python3 render.py part1 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part1"
VO, _end = schedule(PART, first=1.2, gap=0.7)
DURATION = _end + 1.6
TM = Timing(PART, VO)

CHIP_T = [TM.word("S1", w) - 0.15 for w in ("iron", "calcium", "oxygen")]
NONE_T = TM.word("S1", "none of it")
S2 = (VO["S2"] - 0.6, VO["S2"])
BOOM_T = TM.word("S2", "died") - 0.2
S3 = (VO["S3"] - 0.6, VO["S3"])
LIFE_T = TM.word("S3", "first spark") - 0.3
EXIT = (DURATION - 1.8, DURATION)


def orbi_path_a(t):
    k = out_back(prog(t, 0.8, 3.2), 1.0)
    return lerp(W + 200, 1580, k) + 18 * math.sin(t * 0.9), lerp(260, 420, smooth(prog(t, 0.8, 3.2))) + 14 * math.sin(t * 1.3)


def body(c, t):
    cam = drift_cam(t, 0, S2[1], 0, -40, 20, -10, 1.0, 1.1)
    space(c, t, cam, clouds=("cloud",), a=0.55)
    push_screen(c, cam)
    human(c, 760, 1000, 760, glow_rgb=SOLAR if t > CHIP_T[0] else None)
    for i, (sym, x, y) in enumerate((("Fe", 1150, 360), ("Ca", 1330, 560), ("O", 1150, 760))):
        g = out_back(prog(t, CHIP_T[i], CHIP_T[i] + 0.55), 1.3)
        if g <= 0:
            continue
        sx, sy = lerp(800, x, out_cubic(min(1, g))), lerp(480 + i * 140, y, out_cubic(min(1, g)))
        c.drawLine(800, 480 + i * 140, sx - 90 * min(1, g), sy, stroke(ELEMENTS[sym][1], 3, 140 * min(1, g)))
        pulse = 1 + 0.06 * math.sin((t - NONE_T) * 6) * (t > NONE_T)
        element_chip(c, sx, sy, 150 * g * pulse, sym, glow_a=120 + 80 * smooth(prog(t, NONE_T, NONE_T + 0.5)))
    cam.pop(c)
    expr = "wide" if t < NONE_T else "neutral"
    orbi_on(c, t, orbi_path_a, 95, expr, (-0.8, 0.1), 0.6, rim=SOLAR)


def sky(c, t):
    cam = drift_cam(t, S2[0], S3[1], 0, 0, -60, 40, 1.15, 1.0)
    cam = shake(cam, t, BOOM_T, 7, 2.5)
    space(c, t, cam, clouds=("cloud", "teal"))
    push_screen(c, cam, 0.7)
    k = prog(t, BOOM_T, BOOM_T + 4.5)
    if t < BOOM_T:
        star(c, 1300, 330, 40 + 8 * smooth(prog(t, S2[0], BOOM_T)), t, RED_GIANT, 0.8)
    else:
        shockwave(c, 1300, 330, 560, t, k)
        for i in range(16):
            ang = i / 16 * 6.28 + 0.2
            d = (180 + (i % 3) * 70) * out_cubic(prog(t, BOOM_T + 0.2, BOOM_T + 3.0))
            atom_dot(c, 1300 + math.cos(ang) * d, 330 + math.sin(ang) * d * 0.7, 9, [AMBER, TEAL, MAGENTA, SOLAR][i % 4], t, 255 * smooth(prog(t, BOOM_T + 0.2, BOOM_T + 0.6)))
    cam.pop(c)
    c.drawRect(skia.Rect.MakeXYWH(0, 900, W, 200), shaded(linear((0, 880), (0, H), [(10, 10, 30), (4, 4, 14)])))
    human(c, 420, 960, 260)
    orbi(c, 640, 830 + bob(t, 6, 2.4), 70, t, "wide" if t > BOOM_T else "neutral", (0.8, -0.8), ears=0.8 if t > BOOM_T else 0.2, rim=AMBER)
    label(c, "LONG BEFORE THE SUN WAS BORN", 960, 1040, AMBER, 30, 255 * smooth(prog(t, BOOM_T + 0.8, BOOM_T + 1.3)))


STAGES = ["NEBULA", "PROTOSTAR", "STAR", "RED GIANT", "SUPERNOVA"]


def title(c, t):
    cam = drift_cam(t, S3[0], DURATION, 0, 0, 0, 0, 1.0, 1.06)
    space(c, t, cam, clouds=("cloud",), a=0.8)
    a1 = smooth(prog(t, S3[1], S3[1] + 0.6))
    label(c, "YOU ARE MADE OF", 960, 300, WHITE, 46, 255 * a1)
    tr = lerp(40, 14, out_cubic(prog(t, S3[1] + 0.3, S3[1] + 2.0)))
    text(c, "DEAD STARS", 960, 440, 140, SOLAR, 255 * smooth(prog(t, S3[1] + 0.3, S3[1] + 0.9)), 800, spacing=tr)
    sw = prog(t, S3[1] + 0.5, S3[1] + 2.0)
    if 0 < sw < 1:
        light(c, lerp(500, 1420, in_out(sw)), 400, 240, SOLAR, 150 * math.sin(math.pi * sw))
    draws = [lambda x, y: draw_texture(c, tex_cloud(), x, y, 0.14, t * 8, 255, skia.BlendMode.kPlus),
             lambda x, y: protostar(c, x, y, 16, t, 0.8),
             lambda x, y: star(c, x, y, 34, t),
             lambda x, y: star(c, x, y, 52, t, RED_GIANT, 0.6),
             lambda x, y: shockwave(c, x, y, 140, t, 0.28)]
    for i, name in enumerate(STAGES):
        g = out_back(prog(t, LIFE_T + i * 0.45, LIFE_T + i * 0.45 + 0.6))
        if g <= 0:
            continue
        x = 300 + i * 330
        c.save()
        c.translate(x, 700)
        c.scale(g, g)
        c.translate(-x, -700)
        draws[i](x, 700)
        c.restore()
        text(c, name, x, 860, 22, WHITE, 220 * min(1, g), 800, spacing=4)
        if i < 4 and g >= 1:
            arrow(c, x + 90, 700, x + 90 + 140 * smooth(prog(t, LIFE_T + i * 0.45 + 0.4, LIFE_T + i * 0.45 + 0.8)), 700, (120, 120, 170), 4, 200, 16)

    def path(tt):
        k = in_cubic(prog(tt, *EXIT))
        return lerp(1700, 960, k) + 10 * math.sin(tt), lerp(280, 520, k) + 8 * math.sin(tt * 1.3)
    k = in_cubic(prog(t, *EXIT))
    orbi_on(c, t, path, 80 * (1 - 0.85 * k), "happy" if t < EXIT[0] else "squint", (-0.5, 0.3), 0.9, rim=SOLAR, a=255 * (1 - smooth(prog(t, EXIT[1] - 0.5, EXIT[1]))))


def draw_frame(c, t):
    scenes(c, t, [((0.0, 0.01), S2[1], body), (S2, S3[1], sky), (S3, DURATION + 1, title)])
    fade(c, t, DURATION, 0.8, 0.5)


def sfx_events():
    ev = [(0.3, "swell_soft", 0.7), (0.8, "whoosh", 0.5)] + [(x, "pop", 0.6) for x in CHIP_T] + [(x + 0.1, "chime", 0.4) for x in CHIP_T]
    ev += [(NONE_T, "shimmer", 0.6), (S2[0], "whoosh_long", 0.6), (BOOM_T - 1.0, "riser", 0.7), (BOOM_T, "boom", 1.0), (BOOM_T + 0.1, "whoosh_long", 0.6),
           (S3[0], "whoosh", 0.5), (S3[1] + 0.3, "swell_soft", 0.8), (S3[1] + 0.5, "shine", 0.7)]
    ev += [(LIFE_T + i * 0.45, "blip", 0.4) for i in range(5)] + [(EXIT[0], "whoosh_long", 0.7)]
    return ev


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 15, 19)), (S2[0], 41, (0, 7, 12, 16, 19)), (S3[0], 48, (0, 7, 12, 16, 19, 24))],
    plucks=[(S3[1], DURATION)], bpm=90, rises=[(BOOM_T - 1.5, BOOM_T)], drone=33,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
