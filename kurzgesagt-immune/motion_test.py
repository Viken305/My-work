"""12 s motion test: Max spots a bacterium, reaches, gulps it down, chews and digests it.

  python3 motion_test.py   -> out/storyboards/motion_test.mp4
"""
import math, os

from boards import *  # noqa: F401,F403

PREMIUM, SAMPLES = True, 4
DURATION = 12.0
MX, MY, MR = 760, 580, 200
NOTICE, REACH, GULP, SWALLOW, CHEW_END = 2.2, 3.6, 5.4, 6.35, 9.4
BELLY0 = (0.78, -0.08)


def bac_free(t):
    x = lerp(2150, 1260, out_cubic(prog(t, 0.0, 3.0))) + 70 * smooth(prog(t, REACH, REACH + 0.9))
    return x, 470 + 30 * math.sin(t * 2.2)


def bac_pos(t):
    """Bacterium path: swims in, tries to flee, is grabbed by the pseudopod and reeled into the mouth."""
    fx, fy = bac_free(t)
    mx, my = max_pos(t)
    d = math.hypot(fx - mx, fy - my)
    tx, ty = mx + (fx - mx) / d * MR * 0.72, my + (fy - my) / d * MR * 0.72
    k = in_out(prog(t, GULP - 0.9, SWALLOW))
    return lerp(fx, tx, k), lerp(fy, ty, k)


def max_pos(t):
    lunge = math.sin(math.pi * prog(t, GULP - 0.3, SWALLOW + 0.4))
    return MX + 60 * lunge - 25 * math.sin(math.pi * prog(t, GULP - 0.8, GULP - 0.2)), MY + 10 * math.sin(t * 0.9)


def draw_frame(c, t):
    hit = SWALLOW
    cam = Cam(lerp(0, 120, in_out(prog(t, REACH, SWALLOW))), 0, lerp(1.0, 1.12, in_out(prog(t, REACH, SWALLOW))))
    if t > hit:
        s = 8 * math.exp(-(t - hit) * 6)
        cam.x += s * math.sin(t * 60)
        cam.y += s * math.cos(t * 53)
    tissue(c, t, cam)
    # background neutrophils drifting past, out of focus
    for k in range(3):
        x = (300 + k * 700 + t * 40) % 2400 - 200
        c.saveLayerAlpha(None, 110)
        neutrophil(c, x, 220 + k * 330, 34, t + k, "neutral", (1, 0), seed=k)
        c.restore()
    cam.push(c, 1.0)
    c.translate(-W / 2, -H / 2)
    # Max
    x, y = max_pos(t)
    x2, y2 = max_pos(t + 1 / 60)
    vel = ((x2 - x) * 60, (y2 - y) * 60)
    bx, by = bac_pos(t)
    look = (clamp((bx - x) / 600, -1, 1), clamp((by - y) / 400, -1, 1)) if t < SWALLOW else (0.2, 0.3)
    if t < NOTICE:
        expr, look = "neutral", (math.sin(t * 1.3) * 0.6, -0.2)
    elif t < NOTICE + 0.7:
        expr = "shocked"
    elif t < SWALLOW:
        expr = "hungry"
    elif t < CHEW_END:
        expr = "chewing"
    else:
        expr = "full"
    ang = math.degrees(math.atan2(by - y, bx - x))
    dist = math.hypot(bx - x, by - y)
    need = max(0.0, (dist - MR * 0.95) / MR)          # arm length that just touches the bacterium
    grow = out_back(prog(t, REACH + 0.2, GULP - 0.9), 1.4)
    hold = 1 - smooth(prog(t, SWALLOW - 0.35, SWALLOW))
    arms = ((ang, need * grow * hold), (ang - 34, 0.35 * grow * hold)) if grow * hold > 0.01 else ()
    op = smooth(prog(t, GULP - 0.6, GULP)) * (1 - smooth(prog(t, SWALLOW - 0.15, SWALLOW + 0.25)))
    gulp = (ang, 0.9 * op) if op > 0.01 else None
    belly = ()
    if t > SWALLOW:
        u = out_cubic(prog(t, SWALLOW, SWALLOW + 1.4))
        belly = ((lerp(BELLY0[0], -0.15, u), lerp(BELLY0[1], 0.45, u), 0.24, 0.85 * smooth(prog(t, SWALLOW + 1.0, DURATION - 0.5))),)
    if GULP - 0.2 < t < SWALLOW:   # drawn under Max so it vanishes into the mouth
        bacterium(c, bx, by, 46 * (1 - 0.3 * in_cubic(prog(t, GULP, SWALLOW))), t, 190 + 10 * math.sin(t * 3), mood="scared", wiggle=3.5)
    squash = 1 + 0.08 * math.exp(-max(0.0, t - SWALLOW) * 5) * (t > SWALLOW)
    c.save()
    c.translate(x, y)
    c.scale(squash, 1 / squash)
    max_cell(c, 0, 0, MR, t, expr, look, vel, arms, gulp, belly, rim=(255, 120, 150))
    c.restore()
    # bacterium (outside until swallowed)
    if t < GULP - 0.2:
        scared = t > REACH
        bacterium(c, bx, by, 46 * (1 - 0.3 * in_cubic(prog(t, GULP, SWALLOW))), t, 190 + 10 * math.sin(t * 3),
                  mood="scared" if scared else "grin", wiggle=3.5 if scared else 1.0)
        if NOTICE < t < NOTICE + 0.9:
            k = prog(t, NOTICE, NOTICE + 0.9)
            text(c, "!", x + 40, y - MR - 50 - 30 * out_back(k), 90, ALARM, 255 * (1 - smooth(prog(k, 0.7, 1))), 800)
    if t > CHEW_END - 0.3:   # burp bubble
        k = prog(t, CHEW_END + 0.6, CHEW_END + 1.6)
        if 0 < k < 1:
            c.drawCircle(x + 70, y - 40 - 160 * k, 16 + 14 * k, stroke((210, 255, 250), 4, 220 * (1 - k)))
    cam.pop(c)
    foreground(c, t, cam)
    ta = smooth(prog(t, 10.0, 10.6))
    if ta > 0:
        text(c, "MOTION TEST · MAX THE MACROPHAGE", 960, 990, 32, WHITE, 230 * ta, 800, spacing=8)
        text(c, "JELLY MEMBRANE · PSEUDOPODS · ENGULF · DIGEST · DEPTH OF FIELD · MOTION BLUR", 960, 1034, 17, MAX_BODY, 210 * ta, 800, spacing=4)
    a = max(1 - smooth(prog(t, 0, 0.5)), smooth(prog(t, DURATION - 0.5, DURATION)))
    if a > 0:
        c.drawPaint(fill((10, 2, 8), 255 * a))


EVENTS = [(0.3, "swell_soft", 0.6), (0.6, "bubble", 0.4), (NOTICE, "blip", 0.9), (NOTICE + 0.05, "pop", 0.6), (REACH, "slide", 0.7),
          (REACH + 0.4, "whoosh_soft", 0.5), (GULP - 0.3, "whoosh", 0.7), (SWALLOW, "pop", 1.0), (SWALLOW + 0.02, "bubble", 0.9)] + \
         [(SWALLOW + 0.4 + i * 0.36, "tink", 0.35) for i in range(7)] + [(CHEW_END + 0.6, "bubble", 0.8), (CHEW_END + 0.7, "chime", 0.5)]
MUSIC = dict(chords=[(0.0, 50, (0, 7, 12, 16, 19)), (NOTICE, 52, (0, 7, 12, 15, 19)), (SWALLOW, 50, (0, 7, 12, 16, 21))],
             plucks=[(0.5, DURATION)], bpm=104, rises=[(REACH, SWALLOW)])

if __name__ == "__main__":
    import sys
    import audio
    import render
    if "--still" in sys.argv:
        render.stills("motion_test", [float(x) for x in sys.argv[sys.argv.index("--still") + 1].split(",")])
        raise SystemExit
    v = render.render_video("motion_test")
    wav = os.path.join(HERE, "build", "motion_test", "mix.wav")
    audio.render_mix(wav, DURATION, [], EVENTS, MUSIC)
    master = os.path.join(HERE, "build", "motion_test", "master.mp4")
    render.mux(v, wav, master)
    out = os.path.join(HERE, "out", "storyboards", "motion_test.mp4")
    render.encode(master, out, 22)
    print(out)
