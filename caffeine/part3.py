"""0:45:00 · PARK THAT MOLECULE! (the trick). Sleepy adenosine molecules park in the brain cell's receptor spots one by
one and the SLEEPY-O-METER climbs; a LOOK-ALIKES card shows caffeine's same double ring; then caffeine bumps every
adenosine out of its spot, the sleepy signal is crossed out (BLOCKED!) and the meter drops.

  python3 render.py part3 [--still 2,4,6.5,8.5,10.5,12.5]
"""
from lot import *  # noqa: F401,F403

PART = "part3"
G = Show(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
VHS, SAMPLES = True, 2
T_ADEN = G.w("B1", "adenosine")
T_MORE = G.w("B1", "more")
T_SLEEPIER = G.w("B1", "sleepier")
T_B2 = VO["B2"]
T_SO = G.w("B2", "so")
T_PARKS = G.w("B2", "parks")
T_BLOCKS = G.w("B2", "blocks")
DOCK_A = [T_ADEN - 0.3 + 0.55 * i for i in range(4)]          # adenosine parks, one per spot
DOCK_C = [T_PARKS - 0.15 + 0.22 * i for i in range(4)]        # caffeine takes the spots


def sleepy(t):
    v = 0.12 + 0.12 * sum(smooth(prog(t, d + 0.3, d + 0.6)) for d in DOCK_A)
    v += 0.25 * smooth(prog(t, T_MORE, T_SLEEPIER + 0.4))
    return lerp(v, 0.1, smooth(prog(t, T_BLOCKS, T_BLOCKS + 0.6)))


def scene(c, t):
    stage(c, t)
    meter(c, t, sleepy(t))
    membrane(c, t)
    for i, x in enumerate(SPOTS):
        if DOCK_A[i] + 0.5 < t < DOCK_C[i] + 0.3:
            signal(c, t, x, "sleepy")
        if t > T_BLOCKS:
            signal(c, t, x, "blocked", 255 * smooth(prog(t, T_BLOCKS + 0.08 * i, T_BLOCKS + 0.08 * i + 0.15)))
    for i, x in enumerate(SPOTS):                                # adenosine: in, parked, then bumped out
        if t < DOCK_A[i]:
            continue
        if t < DOCK_C[i] + 0.1:
            px, py = arrive(t, DOCK_A[i], x + (200 if i % 2 else -200), 600, x, DOCK_Y)
            rot = 0
        else:
            u = t - DOCK_C[i] - 0.1
            px, py = x + (i - 1.5) * 90 * min(u, 1.2) + 6 * math.sin(t * 3 + i), DOCK_Y - 260 * out_cubic(min(1, u / 0.6)) + 8 * math.sin(t * 2.5 + i)
            rot = 25 * math.sin(t * 3 + i)
        adenosine(c, px, py, 50, t, 255, "sleepy" if t < DOCK_C[i] else "open", rot)
    for i, x in enumerate(SPOTS):                                # caffeine dives in
        if t < DOCK_C[i] - 0.4:
            continue
        px, py = arrive(t, DOCK_C[i] - 0.4, x + (i - 1.5) * 60, 560, x, DOCK_Y, 0.5)
        caffeine(c, px, py, 50, t, 255)
    # LOOK-ALIKES card
    a = 255 * smooth(prog(t, T_B2 - 0.1, T_B2 + 0.2)) * (1 - smooth(prog(t, T_SO - 0.1, T_SO + 0.15)))
    if a > 1:
        v = appear(t, T_B2 - 0.1)
        c.save()
        c.translate(540, 720)
        c.scale(v, v)
        panel(c, -420, -150, 840, 330, PURPLE, a)
        outlined(c, "LOOK-ALIKES!", 0, -88, 58, "righteous", YELLOW, a, ow=0.08)
        adenosine(c, -230, 30, 56, t, a, "sleepy")
        caffeine(c, 250, 30, 56, t, a)
        label(c, "=", 20, 60, 100, "righteous", WHITE, a, "center")
        label(c, "ADENOSINE", -230, 160, 34, "vt", SKY, a, "center")
        label(c, "CAFFEINE", 250, 160, 34, "vt", ORANGE, a, "center")
        c.restore()
    v = appear(t, T_BLOCKS + 0.1)
    if v > 0:
        c.save()
        c.translate(540, 700)
        c.rotate(-8)
        c.scale(v, v)
        starburst(c, 0, 0, 140, 200, 16, YELLOW, t * 15)
        outlined(c, "BLOCKED!", 0, 30, 96, "bowlby", RED, 255, ow=0.08)
        c.restore()


def draw_frame(c, t):
    G.frame(c, t, scene)


OVERLAY = G.overlay


def POST(t):
    return G.post(t)


def sfx_events():
    ev = G.sfx() + [(d + 0.35, "pop", 0.45) for d in DOCK_A] + [(T_SLEEPIER, "buzzer", 0.25), (T_B2, "chime", 0.45)]
    ev += [(d - 0.1, "whoosh", 0.3) for d in DOCK_C[:2]] + [(d + 0.05, "stamp", 0.3) for d in DOCK_C]
    return ev + [(T_BLOCKS + 0.1, "ding", 0.6)]


MUSIC = G.music()

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
