"""BONUS ROUND and the end. The brain is a spinning mirror ball that throws endorphins and endocannabinoids;
"after you stop" the track tape-stops and the stage freezes while an AFTERBURN calorie counter keeps climbing; the
heart levels up and the resting rate drops; LEVEL COMPLETE, and the play button from the opening comes back (loop).

  python3 render.py part7 [--still 3,6,8,11,15,17,19,21.9]
"""
from game import *  # noqa: F401,F403
from part1 import play_button as _pb, star

PART = "part7"
G = Game(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
PREMIUM, SAMPLES = True, 4
T_ENDO = G.w("F1", "endorphins")
T_CANNA = G.w("F1", "endocannabinoids")
T_HIGH = G.w("F1", "runner's")
T_F2 = VO["F2"]
T_STOP = G.w("F2", "stop")
T_BURN = G.w("F2", "burning")
T_F3 = VO["F3"]
T_STRONG = G.w("F3", "stronger")
T_FEWER = G.w("F3", "fewer")
T_F4 = VO["F4"]
T_DONE = G.w("F4", "complete")
T_PLAY = G.w("F4", "play")
END = DURATION - 0.75                                     # the play button is back on screen
_phase = G.phase


def phase(t):
    """The stage slows to a stop with the tape-stop and stands still until the track comes back."""
    if t < T_STOP:
        return _phase(t)
    if t < T_F3:
        u = min(t - T_STOP, 0.7)
        return _phase(T_STOP) + (u - u * u / 1.4) * G.bpm / 60
    return _phase(t)


G.phase = phase
G.heart_fn = lambda t: (lerp(160, 128, in_out(prog(t, 0.5, T_STOP))) if t < T_STOP else
                        lerp(128, 96, in_out(prog(t, T_STOP, T_F3))) if t < T_F3 else
                        lerp(96, 60, in_out(prog(t, T_FEWER - 0.3, T_FEWER + 0.8))))
FROZEN = lambda t: smooth(prog(t, T_STOP, T_STOP + 0.7)) * (1 - smooth(prog(t, T_F3 - 0.1, T_F3 + 0.2)))   # noqa: E731


def mirror_ball(c, t, x, y, r, a):
    if a <= 1:
        return
    spin = t * 0.8
    for k in range(10):                                   # light beams thrown around the room
        ang = spin * 1.5 + k * 2 * math.pi / 10
        rgb = (VIOLET, CYN, MAG, GOLD, LIME)[k % 5]
        tip = (x + math.cos(ang) * 900, y + math.sin(ang) * 900)
        side = (-math.sin(ang) * 60, math.cos(ang) * 60)
        bp = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(x, y), skia.Point(*tip)],
                        [skia.Color(*rgb, int(110 * a / 255)), skia.Color(*rgb, 0)]), BlendMode=skia.BlendMode.kPlus)
        c.drawPath(path_of([(x, y), (tip[0] + side[0], tip[1] + side[1]), (tip[0] - side[0], tip[1] - side[1])], True), bp)
    c.drawLine(x, 380, x, y - r, stroke((150, 150, 170), 4, a))
    c.save()
    c.clipPath(_circle(x, y, r), skia.ClipOp.kIntersect, True)
    c.drawCircle(x, y, r, fillp((40, 30, 70), a))
    rows = 9
    for i in range(rows):                                 # mirror tiles on a turning sphere
        lat = -math.pi / 2 + (i + 0.5) / rows * math.pi
        yy = y + math.sin(lat) * r
        ring = math.cos(lat) * r
        n = max(4, int(18 * math.cos(lat)))
        for j in range(n):
            lon = (j / n) * 2 * math.pi + spin
            if math.cos(lon) < 0:
                continue
            xx = x + math.sin(lon) * ring
            sh = 0.4 + 0.6 * math.cos(lon) * (0.6 + 0.4 * math.cos(lat))
            flash = hsh(i, j, int(t * 8)) > 0.93
            tw = 2 * math.pi * ring / n * math.cos(lon) * 0.42
            c.drawRect(skia.Rect.MakeXYWH(xx - tw, yy - r / rows * 0.45, tw * 2, r / rows * 0.9),
                       fillp(WHITE if flash else mix((60, 50, 110), (220, 210, 255), sh), a))
    c.restore()
    # the folds of a brain drawn over the ball
    for k in range(5):
        q = skia.Path()
        yy = y - r * 0.6 + k * r * 0.3
        q.moveTo(x - r * 0.8, yy)
        q.cubicTo(x - r * 0.3, yy - 40, x + r * 0.1, yy + 40, x + r * 0.8, yy - 10)
        c.drawPath(q, stroke(MAG, 5, 0.6 * a))
    c.drawCircle(x, y, r, stroke(VIOLET, 6, a))
    light(c, x - r * 0.4, y - r * 0.4, 120, WHITE, 120 * a / 255)


def _circle(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def sparkles(c, t, a):
    for i in range(40):
        u = (t * 0.5 + hsh(i, 1)) % 1
        x = hsh(i, 2) * W
        y = 400 + hsh(i, 3) * 540
        s = math.sin(u * math.pi)
        rgb = (VIOLET, CYN, MAG, GOLD)[i % 4]
        c.drawLine(x - 14 * s, y, x + 14 * s, y, stroke(rgb, 4, a * s))
        c.drawLine(x, y - 14 * s, x, y + 14 * s, stroke(rgb, 4, a * s))


def bonus(c, t):
    a = 255 * (1 - smooth(prog(t, T_F2 - 0.3, T_F2 + 0.1)))
    if a <= 1:
        return
    sparkles(c, t, a)
    mirror_ball(c, t, 540, 620, 170 * appear(t, 1.2), a)
    for txt, t0, rgb, (x, y) in (("ENDORPHINS", T_ENDO, VIOLET, (300, 860)), ("ENDOCANNABINOIDS", T_CANNA, CYN, (640, 440))):
        v = appear(t, t0 - 0.05)
        if v > 0:
            w = width(txt, "bungee", 40) + 50
            c.save()
            c.translate(x, y)
            c.scale(v, v)
            c.rotate(-4 if x < 540 else 4)
            light(c, 0, 0, w * 0.6, rgb, 100 * a / 255)
            c.drawRRect(rrect(-w / 2, -36, w, 72, 36), fillp(mix(rgb, (0, 0, 0), 0.6), a))
            c.drawRRect(rrect(-w / 2, -36, w, 72, 36), stroke(rgb, 5, a))
            label(c, txt, 0, 15, 40, "bungee", WHITE, a, "center")
            c.restore()
    v = appear(t, T_HIGH - 0.05)
    if v > 0:
        c.save()
        c.translate(800, 860)
        c.scale(v, v)
        c.rotate(-6)
        outlined(c, "RUNNER'S HIGH", 0, 0, 52, "bungee", GOLD, a, glow_rgb=MAG)
        c.restore()


def afterburn(c, t):
    a = 255 * smooth(prog(t, T_F2 - 0.1, T_F2 + 0.3)) * (1 - smooth(prog(t, T_F3 - 0.3, T_F3)))
    if a <= 1:
        return
    fz = FROZEN(t)
    runner(c, G, t, 540, 690, 0.85, a, level=lambda tt: 0.35 - 0.25 * fz, rgb0=mix(CYN, (90, 90, 120), fz), rgb1=mix(MAG, (90, 90, 120), fz))
    if fz > 0.01:                                         # pause icon
        c.drawRRect(rrect(470, 420, 44, 120, 10), fillp(WHITE, a * fz))
        c.drawRRect(rrect(566, 420, 44, 120, 10), fillp(WHITE, a * fz))
    k = smooth(prog(t, T_BURN - 0.2, T_BURN + 0.3))
    if k > 0:
        for i in range(12):                               # the fire keeps going under the stopped runner
            x = 400 + i * 25
            hgt = (40 + 40 * hsh(i, 2) + 20 * math.sin(t * 13 + i)) * k
            p = skia.Path()
            p.moveTo(x - 14, 930)
            p.quadTo(x - 9, 930 - hgt * 0.6, x + 3 * math.sin(t * 9 + i), 930 - hgt)
            p.quadTo(x + 9, 930 - hgt * 0.6, x + 14, 930)
            p.close()
            c.drawPath(p, fillp(mix(ORANGE, GOLD, hsh(i, 5)), a))
        kcal = int(12 + 64 * prog(t, T_BURN, T_F3))
        c.save()
        c.translate(870, 620)
        c.scale(appear(t, T_BURN - 0.1), appear(t, T_BURN - 0.1))
        chip(c, 0, 0, "AFTERBURN", f"+{kcal}", ORANGE, a * k, size=64)
        label(c, "KCAL", 0, 70, 26, "mono_bold", ORANGE, a * k, "center", tracking=0.1)
        c.restore()


def heart_shape(x, y, s):
    p = skia.Path()
    p.moveTo(x, y + 90 * s)
    p.cubicTo(x - 160 * s, y - 20 * s, x - 90 * s, y - 140 * s, x, y - 60 * s)
    p.cubicTo(x + 90 * s, y - 140 * s, x + 160 * s, y - 20 * s, x, y + 90 * s)
    p.close()
    return p


def stronger(c, t):
    a = 255 * smooth(prog(t, T_F3 - 0.2, T_F3 + 0.2)) * (1 - smooth(prog(t, T_F4 - 0.3, T_F4)))
    if a <= 1:
        return
    grow = out_back(prog(t, T_STRONG - 0.2, T_STRONG + 0.3), 2)
    s = (1.3 + 0.35 * grow) * (1 + 0.08 * G.beat(t))
    hy = lerp(640, 700, in_out(prog(t, T_FEWER - 0.4, T_FEWER)))
    light(c, 540, hy - 20, 300 * s, RED, 120 * a / 255)
    c.drawPath(heart_shape(540, hy, s), fillp(mix(RED, (0, 0, 0), 0.4), a))
    c.drawPath(heart_shape(540, hy, s), stroke(mix(RED, WHITE, 0.3), 8, a))
    lu = min(1, grow) * (1 - smooth(prog(t, T_FEWER - 0.4, T_FEWER - 0.1)))
    if lu > 0:
        outlined(c, "LEVEL UP", 540, 440, 60, "bungee", LIME, a * lu, glow_rgb=LIME)
        for k in (-1, 1):
            c.drawPath(path_of([(540 + k * 250 - 30, 520), (540 + k * 250, 480), (540 + k * 250 + 30, 520)]), stroke(LIME, 10, a * lu))
    v = appear(t, T_FEWER - 0.1)
    if v > 0:
        hr = int(round(lerp(72, 60, in_out(prog(t, T_FEWER, T_FEWER + 0.8)))))
        c.save()
        c.translate(540, 530)
        c.scale(v, v)
        chip(c, 0, 0, "RESTING HEART RATE", f"{hr} BPM", RED, a, size=58)
        c.restore()


def complete(c, t):
    if t < T_F4 - 0.2:
        return
    a = 255 * (1 - smooth(prog(t, END - 0.35, END)))
    v = out_back(prog(t, T_F4 - 0.1, T_F4 + 0.3), 2)
    c.save()
    c.translate(540, 520)
    c.scale(v, v)
    outlined(c, "LEVEL", 0, -40, 110, "bungee", WHITE, a, glow_rgb=VIOLET)
    outlined(c, "COMPLETE", 0, 80, 116, "bungee_shade", GOLD, a, glow_rgb=GOLD)
    c.restore()
    for i in range(3):
        u = out_back(prog(t, T_DONE + 0.1 + 0.15 * i, T_DONE + 0.4 + 0.15 * i), 2.5)
        if u > 0:
            light(c, 360 + 180 * i, 720 - 20 * (i == 1), 160, GOLD, 120 * a / 255)
            star(c, 360 + 180 * i, 720 - 20 * (i == 1), 70 * u, GOLD, a)
    total = G.combo0 + len(G.notes)
    label(c, f"FULL COMBO · x{total}", 540, 860, 40, "bungee", CYN, a * smooth(prog(t, T_DONE + 0.5, T_DONE + 0.8)), "center")
    for i in range(70):                                    # confetti
        u = prog(t, T_DONE, T_DONE + 2.6)
        if u <= 0:
            break
        x = hsh(i, 1) * W + 80 * math.sin(t * 3 + i)
        y = 300 + (hsh(i, 2) * 300 + 900 * u * (0.5 + 0.5 * hsh(i, 3))) % 800
        c.save()
        c.translate(x, y)
        c.rotate(t * 300 * (hsh(i, 4) - 0.5) + i * 30)
        c.drawRect(skia.Rect.MakeXYWH(-10, -5, 20, 10), fillp((MAG, CYN, LIME, GOLD, VIOLET)[i % 5], a * (1 - u * 0.5)))
        c.restore()


def scene(c, t):
    bonus(c, t)
    afterburn(c, t)
    stronger(c, t)
    complete(c, t)


def draw_frame(c, t):
    G.frame(c, t, scene)
    if t > END - 0.4:                                      # back to the start: the play button (the Short loops)
        k = smooth(prog(t, END - 0.4, END))
        c.drawPaint(fillp((0, 0, 0), 130 * k))
        c.save()
        c.translate(540, 640)
        c.scale(k, k)
        c.translate(-540, -640)
        _pb(c, 0.0)
        c.restore()


OVERLAY = G.overlay


def POST(t):
    fz = FROZEN(t)
    return dict(grain=3.5 + 3 * fz, ca=1.2, bloom=1.1 - 0.3 * fz)


def sfx_events():
    ev = [e for e in G.sfx() if not (T_STOP + 0.2 < e[0] < T_F3 - 0.05)]
    return ev + [(T_ENDO, "shimmer", 0.5), (T_CANNA, "shimmer", 0.4), (T_STOP, "tape_stop", 0.8),
                 (T_BURN, "heat_roar", 0.3), (T_F3 - 0.05, "low_hit", 0.6), (T_STRONG, "heartbeat", 0.9),
                 (T_DONE, "trailer_hit", 0.5), (T_DONE + 0.1, "pop", 0.5), (T_DONE + 0.25, "pop", 0.5), (T_DONE + 0.4, "pop", 0.5)]


MUSIC = dict(beds=[(0.0, DURATION, f"drive{G.bpm}_{G.L['energy']}", 0.6)], mute=[(T_STOP + 0.7, T_F3 - 0.05)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
