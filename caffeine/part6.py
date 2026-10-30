"""6:00:00 · PARK THAT MOLECULE! (the crash) and the end. Adenosine piles up behind the caffeine that blocks the spots;
caffeine wears off, all of it rushes in, the SLEEPY-O-METER slams to max: CRASH (the tape sags and the music grinds to
a halt). Then the PRO TIPS card, the "BE KIND, REWIND" sticker, and the tape rewinds to 0:00:00 and stops, so the
Short loops back into the TV switching on.

  python3 render.py part6 [--still 3,6,8,11,14,16]
"""
from lot import *  # noqa: F401,F403

PART = "part6"
G = Show(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
VHS, SAMPLES = True, 2
T_E1 = VO["E1"]
T_PILE = G.w("E1", "piling")
T_E2 = VO["E2"]
T_WEARS = G.w("E2", "wears")
T_RUSH = G.w("E2", "rushes")
T_CRASH = G.w("E2", "crash")
T_E3 = VO["E3"]
T_EARLY = G.w("E3", "early")
T_ADULTS = G.w("E3", "adults")
T_FOUR = G.w("E3", "four")
T_E4 = VO["E4"]
T_REW = TM.end("E4") + 0.35
T_STOP = DURATION - 0.75
N = 18
PILE = [(170 + (i % 6) * 148 + 30 * ((i // 6) % 2), 790 - (i // 6) * 82) for i in range(N)]


def crowd(t):
    return int(4 + (N - 4) * smooth(prog(t, FF, T_PILE + 0.8)))


def sleepy(t):
    v = 0.12 + 0.88 * out_cubic(prog(t, T_RUSH, T_RUSH + 0.5))
    return v


def sag(t):
    return smooth(prog(t, T_CRASH - 0.1, T_CRASH + 0.5)) * (1 - smooth(prog(t, T_E3 - 0.5, T_E3 - 0.1)))


def lot_scene(c, t):
    stage(c, t)
    meter(c, t, sleepy(t))
    membrane(c, t)
    rushed = t > T_RUSH
    for i, x in enumerate(SPOTS):
        if rushed and t > T_RUSH + 0.3 + 0.08 * i:
            signal(c, t, x, "sleepy")
        elif not rushed:
            signal(c, t, x, "blocked")
    # caffeine holds the spots, then wears off and drifts away
    for i, x in enumerate(SPOTS):
        u = prog(t, T_WEARS + 0.12 * i, T_WEARS + 0.12 * i + 0.8)
        if u >= 1:
            continue
        caffeine(c, x + (i - 1.5) * 200 * in_cubic(u), DOCK_Y - 500 * in_cubic(u), 50 * (1 - 0.5 * u), t, 255 * (1 - u))
    # adenosine piling up behind the block, then rushing in
    n = crowd(t)
    for i in range(n):
        t_in = FF + 0.1 if i < 4 else FF + (T_PILE + 0.8 - FF) * (i - 4) / (N - 4)
        side = -1 if i % 2 else 1
        bx, by = PILE[i]
        x, y = arrive(t, t_in, bx + side * 700, by - 100, bx, by, 0.5)
        x += 5 * math.sin(t * 7 + i)
        y += 6 * math.sin(t * 5 + i * 1.3)
        if rushed:
            k = out_cubic(prog(t, T_RUSH + 0.03 * i, T_RUSH + 0.03 * i + 0.4))
            tx, ty = (SPOTS[i], DOCK_Y) if i < 4 else (SPOTS[i % 4] + (i // 4 - 2) * 34, DOCK_Y - 70 - 30 * (i // 4))
            x, y = lerp(x, tx, k), lerp(y, ty, k)
        adenosine(c, x, y, 40 if i >= 4 else 50, t, 255, "sleepy" if rushed else "open", 8 * math.sin(t * 4 + i))
    if not rushed and t > FF:
        c.drawRect(skia.Rect.MakeLTRB(270, 542, 810, 598), fillp(BLACK, 200))
        label(c, f"ADENOSINE WAITING: {n}", 540, 588, 50, "vt", SKY, 255, "center")
    v = appear(t, T_CRASH - 0.05, 0.3)
    if v > 0 and t < T_E3 - 0.2:
        c.save()
        c.translate(540, 700)
        c.rotate(-10 + 4 * math.sin(t * 20) * (t < T_CRASH + 0.4))
        c.scale(v * 1.1, v * 1.1)
        starburst(c, 0, 0, 170, 240, 18, RED, t * 8)
        starburst(c, 0, 0, 150, 215, 18, YELLOW, t * 8)
        outlined(c, "CRASH!", 0, 36, 120, "bowlby", RED, 255, ow=0.08)
        c.restore()


def tips(c, t, a):
    if a <= 1:
        return
    v = appear(t, T_E3 - 0.2, 0.4)
    c.save()
    c.translate(540, 800)
    c.scale(v, v)
    c.translate(-540, -800)
    panel(c, 90, 470, 900, 640, TEAL, a, 24)
    chrome_text(c, "Pro Tips", 540, 590, 100, "shrik", a, depth=10)
    rows = [(T_EARLY - 0.2, "DRINK IT EARLY", 690), (T_FOUR - 0.2, "UNDER ~4 CUPS A DAY", 880)]
    for t0, txt, y in rows:
        k = appear(t, t0)
        if k <= 0:
            continue
        c.save()
        c.translate(150, y)
        c.scale(k, k)
        c.drawRRect(rrect(-10, -46, 64, 64, 12), fillp(WHITE, a))
        c.drawPath(path_of([(4, -16), (20, 2), (46, -34)]), stroke((20, 150, 60), 10, a))
        outlined(c, txt, 84, 2, 56, "archivo", WHITE, a, "left", ow=0.1, outline_rgb=NAVY)
        c.restore()
    if t > T_EARLY:                                          # a morning sun rises behind the first tip
        k = smooth(prog(t, T_EARLY, T_EARLY + 0.6))
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(760, 700, 960, 790))
        c.drawCircle(880, lerp(820, 770, k), 46, fillp(YELLOW, a))
        c.restore()
        c.drawLine(780, 790, 960, 790, stroke(WHITE, 5, a))
        label(c, "AM", 880, 830, 36, "vt", WHITE, a * k, "center")
    for i in range(4):                                       # four little mugs
        k = appear(t, T_FOUR + 0.1 * i)
        if k > 0:
            mug(c, 260 + i * 140, 1000, 0.32 * k, t + i, a, steam=0.6)
    if t > T_ADULTS:
        label(c, "(MOST ADULTS)", 860, 1050, 46, "vt", WHITE, a * smooth(prog(t, T_ADULTS, T_ADULTS + 0.3)), "center")
    c.restore()


def sticker(c, t):
    v = appear(t, T_E4 - 0.1, 0.4)
    if v <= 0:
        return
    c.save()
    c.translate(540, 760)
    c.rotate(-7)
    c.scale(v, v)
    c.drawRRect(rrect(-330 + 12, -150 + 14, 660, 300, 28), fillp(BLACK, 120))
    c.drawRRect(rrect(-330, -150, 660, 300, 28), fillp(WHITE))
    c.drawRRect(rrect(-310, -130, 620, 260, 20), fillp(RED))
    outlined(c, "BE KIND", 0, -18, 104, "archivo", WHITE, 255, ow=0.06, outline_rgb=(120, 0, 0))
    for k in range(2):
        c.drawPath(path_of([(-160 + 70 * k, 70), (-100 + 70 * k, 30), (-100 + 70 * k, 110)], True), fillp(YELLOW))
    outlined(c, "REWIND", 50, 105, 84, "archivo", YELLOW, 255, ow=0.06, outline_rgb=(120, 0, 0))
    c.restore()


def scene(c, t):
    lot_scene(c, t)
    k = smooth(prog(t, T_E3 - 0.4, T_E3))
    if k > 0:
        c.drawPaint(fillp((10, 0, 30), 170 * k))
        tips(c, t, 255 * (1 - smooth(prog(t, T_E4 - 0.3, T_E4))))
        sticker(c, t)
    if t > T_STOP:                                           # STOP: VCR blue, then black (the loop starts dark)
        c.drawPaint(fillp((20, 40, 200)))
        if t > T_STOP + 0.35:
            c.drawPaint(fillp(BLACK))


def draw_frame(c, t):
    G.frame(c, t, scene)


def osd_mode(t):
    if t > T_STOP + 0.35:
        return "OFF"
    if t > T_STOP:
        return "STOP"
    if t > T_REW:
        return "REW"
    return None


def clock(t):
    if t > T_REW:
        return lerp(PROGS[PART]["clock"] + T_REW - FF, 0, in_cubic(prog(t, T_REW, T_STOP)))
    return None


G.osd_fn = osd_mode
G.clock_fn = clock


def OVERLAY(c, t):
    if osd_mode(t) == "OFF":
        return
    G.overlay(c, t)


def POST(t):
    kw = G.post(t)
    kw["sag"] = sag(t)
    if T_REW < t < T_STOP:
        kw["rew"] = 1.0
        kw["track"] = 1.0
    if t > T_STOP + 0.35:
        kw.update(snow=0.3, track=0.0, jitter=0.0)
    return kw


def sfx_events():
    ev = G.sfx() + [(T_PILE, "boil", 0.3), (T_WEARS, "whoosh", 0.4), (T_RUSH - 0.1, "car_pass", 0.4), (T_RUSH + 0.3, "smash", 0.3),
                    (T_CRASH - 0.05, "power_down", 0.8), (T_CRASH, "tape_stop", 1.0), (T_E3 - 0.3, "chime", 0.5),
                    (T_EARLY, "ding", 0.35), (T_FOUR + 0.1, "pop", 0.4), (T_E4 - 0.1, "stamp", 0.6),
                    (T_REW, "rewind", 0.6), (T_STOP, "clunk", 0.6)]
    return ev


# the bed fades over the 0.8 s after its end, inside the tape stop; a fresh one starts with the tips
MUSIC = G.music(beds=[(FF, T_CRASH - 0.1, "lounge", 0.55), (T_E3 - 0.2, T_REW, "lounge", 0.55)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
