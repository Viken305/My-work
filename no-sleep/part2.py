"""Part 2, hours 0-16: Sam wakes at 07:00 (alarm ringing), the adenosine jar slides in and starts filling as the
hours tick. Coffee wraps the jar in a CAFFEINE sleeve, but the level keeps rising past it while day turns to night.

  python3 render.py part2 [--still 1,5]
"""
from film import *  # noqa: F401,F403

PART = "part2"
VO, _end = schedule(PART, first=0.45, gap=0.5)
TM = Timing(PART, VO)
DURATION = _end + 0.6

WAKE_T = TM.word("A1", "meet sam") - 0.1
SEVEN_T = TM.word("A1", "seven") - 0.1
JAR_T = TM.word("A1", "a chemical") - 0.2
STREAM_T = TM.word("A1", "building") - 0.1
PUSH_T = VO["A2"] - 0.2
COFFEE_T = TM.word("A2", "coffee") - 0.25
SLEEVE_T = TM.word("A2", "hide") - 0.1
KEEPS_T = TM.word("A2", "but the jar") - 0.1
OUT_T = DURATION - 0.22

CAPS = Captions(TM, anchors={"A1": (W / 2, 1450), "A2": (W / 2, 1450)},
                emph={"sam.", "sam", "seven", "adenosine", "jar", "coffee", "keeps", "filling."}, accent=CYAN)
MOTES = Motes(40, 2)
PAL = ACTS[1]


def hour_at(t):
    return 16 * in_out(prog(t, SEVEN_T, DURATION)) ** 1.1


def level(hour):
    return 0.04 + 0.92 * hour / 72


def draw_frame(c, t):
    hr = hour_at(t)
    night = smooth(prog(hr, 9, 14))
    push = in_out(prog(t, PUSH_T, PUSH_T + 1.2))
    jar_in = out_back(prog(t, JAR_T, JAR_T + 0.7), 1.2)
    c.save()
    zx, zy = lerp(W / 2, 800, push), lerp(H / 2, 1010, push)
    sc = lerp(1.0, 1.18, push)
    c.translate(zx, zy)
    c.scale(sc, sc)
    c.translate(-zx, -zy)
    room(c, t, PAL, sun=1 - night, moon=night, lamp=0.4 + 0.6 * night)
    # nightstand + alarm clock
    c.drawRRect(rrect(60, 1110, 200, 180, 14), fillp(mix(PAL["dim"], (0, 0, 0), 0.3)))
    hh = 7 + int(hr)
    mm = int((hr % 1) * 60)
    ring = smooth(prog(t, SEVEN_T, SEVEN_T + 0.2)) * (1 - smooth(prog(t, SEVEN_T + 1.4, SEVEN_T + 1.7)))
    alarm_clock(c, 160, 1050, 70, t, f"{hh % 24:02d}:{mm:02d}", ring)
    sx = lerp(W / 2, 400, smooth(prog(t, JAR_T - 0.2, JAR_T + 0.6)))
    lid = 1 - smooth(prog(t, WAKE_T, WAKE_T + 0.5))
    holding = smooth(prog(t, COFFEE_T + 0.4, COFFEE_T + 0.8))
    bags = 0.35 * smooth(prog(hr, 8, 16))
    sam(c, sx, 1290, 135, t, lid=max(lid, 0.15 * night), bags=bags, mouth=0.7 - 0.5 * night,
        look=(0.8 * smooth(prog(t, JAR_T, JAR_T + 0.4)), 0), arm=holding, prop="mug" if holding > 0.2 else None)
    # coffee mug flies in
    mk = prog(t, COFFEE_T, COFFEE_T + 0.6)
    if 0 < mk < 1:
        mx = lerp(-150, sx + 120, out_cubic(mk))
        mug(c, mx, lerp(800, 960, out_cubic(mk)), 70, lerp(-30, 0, mk), 255, 1.0, t)
    # the jar
    jx = lerp(W + 260, 790, jar_in)
    lv = level(hr)
    sleeve = smooth(prog(t, SLEEVE_T, SLEEVE_T + 0.7))
    jar(c, jx, 1240, 230, 430, lv, t, CYAN, 1.0, label_a=smooth(prog(t, JAR_T + 0.4, JAR_T + 0.8)), sleeve=sleeve,
        glow_k=smooth(prog(t, KEEPS_T, KEEPS_T + 0.5)))
    if t > STREAM_T and t < PUSH_T + 1.0:                # adenosine drifting from Sam's head into the jar
        ka = smooth(prog(t, STREAM_T, STREAM_T + 0.4)) * (1 - smooth(prog(t, PUSH_T + 0.5, PUSH_T + 1.0)))
        hx, hy = sx + 60, 1290 - 135 * 2.5 - 135 * 0.72
        for i in range(14):
            u = (t * 0.45 + i / 14) % 1
            px = lerp(hx, jx, u)
            py = lerp(hy, 1240 - 430 - 30, u) - 140 * math.sin(math.pi * u)
            c.drawCircle(px, py, 8, fillp(CYAN, 220 * ka * math.sin(math.pi * u)))
            light(c, px, py, 30, CYAN, 60 * ka)
    if t > KEEPS_T:                                    # arrow: still rising above the sleeve
        ka = smooth(prog(t, KEEPS_T, KEEPS_T + 0.4))
        ly = 1240 - 430 * 0.94 * lv - 8
        ax = jx + 160
        c.drawLine(ax, ly + 60, ax, ly - 40, stroke(CYAN, 6, 255 * ka))
        c.drawPath(path_of([(ax - 18, ly - 22), (ax, ly - 48), (ax + 18, ly - 22)]), stroke(CYAN, 6, 255 * ka))
    MOTES.draw(c, t, (220, 230, 255), 0.8)
    c.restore()
    hud(c, t, hr, CYAN, smooth(prog(t, 0.2, 0.6)))
    CAPS.draw(c, t)
    blink(c, t, 0.0, 0.25)
    if t > OUT_T:
        blink(c, t, DURATION, 0.22)


def POST(t):
    return fatigue_post(0.1 * hour_at(t) / 16)


def sfx_events():
    ev = [(SEVEN_T, "glass_ting", 0.3)]
    for k in range(8):                                 # alarm beeps
        ev.append((SEVEN_T + k * 0.18, "tick", 0.9))
    ev += [(JAR_T, "whoosh", 0.6), (JAR_T + 0.6, "low_hit", 0.35), (STREAM_T, "shimmer", 0.35), (PUSH_T, "swish", 0.4),
           (COFFEE_T, "swish", 0.6), (COFFEE_T + 0.6, "pop", 0.6), (SLEEVE_T, "paper_slap", 0.6), (KEEPS_T, "pour", 0.6),
           (KEEPS_T + 0.6, "riser", 0.4), (OUT_T - 0.1, "swish", 0.5)]
    tt = 0.6
    while tt < DURATION:
        ev.append((tt, "tick", 0.22))
        tt += 1.0
    return ev


MUSIC = dict(beds=[(0.0, DURATION, "night0", 0.55)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
