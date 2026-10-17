"""14 s acting test for KAI: every expression change is animated by the face rig.

  python3 kai_test.py [--still 1,2.3]   -> out/storyboards/kai_test.mp4
"""
import math, os

from heroes import body_world  # noqa: F401
from cells import bacterium, virus, ALARM
from kai import *  # noqa: F401,F403

PREMIUM, SAMPLES = True, 4
DURATION = 14.0
KX, KY, KR = 880, 600, 250

TRACK = Track([(0.0, "neutral", 0.0), (2.2, "shocked", 0.22), (3.5, "focused", 0.45), (4.7, "determined", 0.4),
               (6.6, "laugh", 0.35), (8.3, "smug", 0.5), (9.5, "wink", 0.25), (10.5, "worried", 0.5),
               (12.0, "determined", 0.35)])
LOOK = [(0.0, (0.0, 0.0)), (0.6, (-0.8, -0.2)), (1.3, (0.7, -0.3)), (1.9, (0.2, 0.1)), (2.2, (0.9, -0.2)),
        (5.8, (0.9, 0.0)), (6.6, (0.6, 0.3)), (8.3, (-0.2, -0.1)), (9.5, (0.0, 0.0)), (10.5, (-0.6, -0.5)),
        (11.2, (0.7, -0.5)), (12.0, (0.2, 0.0))]
LABELS = ["NEUTRAL", "SHOCKED", "FOCUSED", "DETERMINED", "LAUGH", "SMUG", "WINK", "WORRIED", "DETERMINED"]


def bac(t):
    """Bacterium sneaks in, freezes under Kai's stare, then flees."""
    x = lerp(2150, 1500, out_cubic(prog(t, 1.2, 2.8))) + lerp(0, 900, in_cubic(prog(t, 5.9, 7.2)))
    y = 520 + 25 * math.sin(t * 2.0) - 80 * smooth(prog(t, 5.9, 7.0))
    return x, y


def draw_frame(c, t):
    cam = Cam(lerp(0, 60, in_out(prog(t, 3.4, 4.6))), 0, lerp(1.0, 1.08, in_out(prog(t, 3.4, 4.6))) - 0.06 * smooth(prog(t, 10.4, 11.2)))
    body_world(c, t, cam)
    cam.push(c, 1.0)
    c.translate(-W / 2, -H / 2)
    # a big shadowy virus drifts past behind for the worried beat
    va = smooth(prog(t, 10.2, 10.8)) * (1 - smooth(prog(t, 12.4, 13.2)))
    if va > 0:
        virus(c, lerp(-200, 900, prog(t, 10.2, 13.2)), 230, 150, t, a=150 * va)
    bx, by = bac(t)
    if t < 7.4:
        scared = t > 3.5
        bacterium(c, bx, by, 50, t, 180 + 8 * math.sin(t * 3), mood="scared" if scared else "grin", wiggle=4 if t > 5.9 else (0.3 if scared else 1))
    p = TRACK.at(t)
    hop = math.sin(math.pi * prog(t, 2.2, 2.6)) - 0.5 * math.sin(math.pi * prog(t, 2.6, 2.95))     # startle jump + settle
    hop += 0.6 * abs(math.sin(t * 9)) * smooth(prog(t, 6.6, 6.9)) * (1 - smooth(prog(t, 7.9, 8.3)))  # laugh shake
    y_off = -60 * math.sin(math.pi * prog(t, 2.2, 2.75))
    look = saccade(t, LOOK)
    blink = blink_amount(t, TRACK.change_times(), 3.9, 1.2)
    kai(c, KX, KY + y_off, KR, t, p, look, blink, hop=hop)
    if 2.2 < t < 3.2:   # surprise marks
        k = prog(t, 2.2, 3.2)
        for i, an in enumerate((-120, -90, -60)):
            a = math.radians(an)
            d0, d1 = KR * 1.45, KR * (1.6 + 0.25 * out_back(k))
            c.drawLine(KX + math.cos(a) * d0, KY - 60 + math.sin(a) * d0, KX + math.cos(a) * d1, KY - 60 + math.sin(a) * d1,
                       stroke(ALARM, 9, 255 * (1 - smooth(prog(k, 0.6, 1)))))
    cam.pop(c)
    # expression label (for review)
    i = [k[0] for k in TRACK.keys].index(max(k[0] for k in TRACK.keys if k[0] <= max(t, 0.0)))
    t0 = TRACK.keys[i][0]
    la = smooth(prog(t, t0, t0 + 0.3)) * (1 - smooth(prog(t, (TRACK.keys[i + 1][0] if i + 1 < len(TRACK.keys) else DURATION) - 0.25,
                                                             TRACK.keys[i + 1][0] if i + 1 < len(TRACK.keys) else DURATION)))
    text(c, LABELS[i], 960, 1010, 30, WHITE, 230 * la, 800, spacing=10)
    text(c, "KAI · FACE RIG ACTING TEST", 960, 60, 22, (255, 210, 200), 200, 800, spacing=6)
    a = max(1 - smooth(prog(t, 0, 0.5)), smooth(prog(t, DURATION - 0.5, DURATION)))
    if a > 0:
        c.drawPaint(fill((30, 4, 12), 255 * a))


EVENTS = [(0.3, "swell_soft", 0.6), (1.4, "slide", 0.4), (2.2, "pop", 1.0), (2.22, "blip", 0.9), (3.5, "whoosh_soft", 0.4),
          (4.7, "click", 0.8), (5.9, "whoosh", 0.7), (6.6, "bubble", 0.7)] + [(6.7 + i * 0.22, "tink", 0.4) for i in range(6)] + \
         [(8.3, "slide", 0.4), (9.5, "ding", 0.7), (10.3, "rumble", 0.7), (10.5, "flicker", 0.5), (12.0, "click", 0.9), (12.05, "shine", 0.6)]
MUSIC = dict(chords=[(0.0, 50, (0, 7, 12, 16, 19)), (2.2, 52, (0, 7, 12, 15, 19)), (6.6, 50, (0, 7, 12, 16, 21)),
                     (10.4, 46, (0, 7, 12, 15, 18)), (12.0, 50, (0, 7, 12, 16, 19))],
             plucks=[(0.5, 10.3), (12.0, DURATION)], bpm=104, rises=[(3.5, 4.7), (11.0, 12.0)])

if __name__ == "__main__":
    import sys
    import audio
    import render
    if "--still" in sys.argv:
        render.stills("kai_test", [float(x) for x in sys.argv[sys.argv.index("--still") + 1].split(",")])
        raise SystemExit
    v = render.render_video("kai_test")
    wav = os.path.join(HERE, "build", "kai_test", "mix.wav")
    audio.render_mix(wav, DURATION, [], EVENTS, MUSIC)
    master = os.path.join(HERE, "build", "kai_test", "master.mp4")
    render.mux(v, wav, master)
    out = os.path.join(HERE, "out", "storyboards", "kai_test.mp4")
    render.encode(master, out, 22)
    print(out)
