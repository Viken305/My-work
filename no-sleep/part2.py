"""Part 2, hours 0-21: Sam wakes at 07:00 (alarm ringing), the adenosine jar slides in and starts filling as the
hours tick. Coffee wraps the jar in a CAFFEINE sleeve, but the level keeps rising past it while day turns to night.
Then 04:00: Sam nods off on the sofa under the body-clock graph, body temperature at its lowest, sleep urge at its peak.

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
YAWN_T = TM.end("A2") - 0.2
NIGHT_T = VO["A3"] - 0.3                         # cut to 04:00 on the sofa
LOW_T = TM.word("A3", "lowest") - 0.15
TEMP_T = TM.word("A3", "body temperature") - 0.1
URGE_T = TM.word("A3", "urge") - 0.1
OUT_T = DURATION - 0.22

CAPS = Captions(TM, anchors={"A1": (W / 2, 1450), "A2": (W / 2, 1450), "A3": (W / 2, 1450)},
                emph={"sam.", "sam", "seven", "adenosine", "jar", "coffee", "keeps", "filling.", "four", "lowest",
                      "drops,", "strongest."}, accent=CYAN)
MOTES = Motes(40, 2)
PAL = ACTS[1]


def hour_at(t):
    if t < NIGHT_T:
        return 16 * in_out(prog(t, SEVEN_T, NIGHT_T)) ** 1.1
    return 16 + 5 * out_cubic(prog(t, NIGHT_T, LOW_T + 0.3)) + 0.6 * prog(t, LOW_T + 0.3, DURATION)


def body_temp(h):
    """Core body temperature over the day (0..1): highest early evening, lowest around 04:00-05:00."""
    return 0.5 + 0.5 * math.cos(2 * math.pi * (h - 16.5) / 24)


def night_scene(c, t):
    pal = ACTS[1]
    room(c, t, pal, moon=1.0, lamp=0.15, win=(-400, 0, 10, 10))
    light(c, 540, 1000, 700, (60, 80, 180), 50)
    # sofa
    c.drawRRect(rrect(200, 1080, 680, 210, 56), fillp((52, 60, 120)))
    c.drawRRect(rrect(150, 1150, 130, 140, 46), fillp((62, 70, 136)))
    c.drawRRect(rrect(800, 1150, 130, 140, 46), fillp((62, 70, 136)))
    # Sam nodding off: the head sinks slowly, then jerks back up
    ph = ((t - NIGHT_T) % 2.2) / 2.2
    nod = in_cubic(min(1, ph / 0.85)) if ph < 0.85 else 1 - out_back((ph - 0.85) / 0.15, 2)
    sam(c, 540, 1270, 110, t, lid=lerp(0.55, 0.95, nod), bags=0.5, mouth=-0.1, slump=nod, tilt=-6 * nod)
    # the body-clock graph
    ka = smooth(prog(t, NIGHT_T + 0.2, NIGHT_T + 0.6))
    x0, x1, y0, y1 = 110, 970, 500, 730
    c.drawRRect(rrect(x0 - 30, y0 - 70, x1 - x0 + 60, y1 - y0 + 150, 26), fillp((6, 8, 24), 170 * ka))
    label(c, "BODY CLOCK", x0, y0 - 24, 26, "mono_bold", PAPER, 255 * ka, tracking=0.12)
    for i, lab in enumerate(("07:00", "13:00", "19:00", "01:00", "07:00")):
        xx = lerp(x0, x1, i / 4)
        c.drawLine(xx, y0, xx, y1, stroke(PAPER, 1.5, 30 * ka))
        label(c, lab, xx, y1 + 40, 20, "mono", ASH, 230 * ka, "center")
    now = hour_at(t)
    def X(h):
        return lerp(x0, x1, h / 24)
    def Yt(h):
        return lerp(y1 - 20, y0 + 20, body_temp((7 + h) % 24))
    n = 80
    pts = [(X(24 * i / n), Yt(24 * i / n)) for i in range(n + 1) if 24 * i / n <= now + 0.01]
    if len(pts) > 1:
        c.drawPath(path_of(pts), stroke(CYAN, 6, 255 * ka))
        tk = smooth(prog(t, TEMP_T, TEMP_T + 0.4))
        label(c, "BODY TEMPERATURE", x0 + 10, y0 + 10, 22, "mono_bold", CYAN, 255 * ka * (0.45 + 0.55 * tk))
    urge = [(X(24 * i / n), lerp(y0 + 20, y1 - 20, body_temp((7 + 24 * i / n) % 24)))       # mirror of the temperature
            for i in range(n + 1) if 24 * i / n <= now + 0.01]
    uk = smooth(prog(t, URGE_T, URGE_T + 0.5))
    if len(urge) > 1 and uk > 0:
        c.drawPath(path_of(urge), stroke(AMBER, 5, 230 * uk))
        label(c, "URGE TO SLEEP", x1 - 10, y0 + 10, 22, "mono_bold", AMBER, 255 * uk, "right")
    xm, ym = X(now), Yt(now)
    lk = smooth(prog(t, LOW_T, LOW_T + 0.3))
    pul = 1 + 0.25 * math.sin(t * 7) * lk
    light(c, xm, ym, 70 * pul, CYAN, 140 * ka)
    c.drawCircle(xm, ym, 13, fillp(PAPER, 255 * ka))
    if lk > 0:
        lw = width("04:00 · LOWEST POINT", "mono_bold", 24)
        c.drawRRect(rrect(xm - 46 - lw, ym - 26, lw + 32, 46, 14), fillp((6, 8, 24), 230 * lk))
        label(c, "04:00 · LOWEST POINT", xm - 30, ym + 8, 24, "mono_bold", PAPER, 255 * lk, "right")



def level(hour):
    return 0.04 + 0.92 * hour / 72


def draw_frame(c, t):
    if t >= NIGHT_T:
        night_scene(c, t)
        MOTES.draw(c, t, (220, 230, 255), 0.6)
        hud(c, t, hour_at(t), CYAN, 1.0)
        CAPS.draw(c, t)
        blink(c, t, NIGHT_T, 0.18)
        if t > OUT_T:
            blink(c, t, DURATION, 0.22)
        return
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
    yawn = smooth(prog(t, YAWN_T, YAWN_T + 0.25)) * (1 - smooth(prog(t, YAWN_T + 0.9, YAWN_T + 1.2)))
    sam(c, sx, 1290, 135, t, lid=max(lid, 0.15 * night, 0.7 * yawn), bags=bags, mouth="o" if yawn > 0.4 else 0.7 - 0.5 * night,
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
    blink(c, t, NIGHT_T, 0.18)


def POST(t):
    return fatigue_post(0.1 * hour_at(t) / 16)


def sfx_events():
    ev = [(SEVEN_T, "glass_ting", 0.3)]
    for k in range(8):                                 # alarm beeps
        ev.append((SEVEN_T + k * 0.18, "tick", 0.9))
    ev += [(JAR_T, "whoosh", 0.6), (JAR_T + 0.6, "low_hit", 0.35), (STREAM_T, "shimmer", 0.35), (PUSH_T, "swish", 0.4),
           (COFFEE_T, "swish", 0.6), (COFFEE_T + 0.6, "pop", 0.6), (SLEEVE_T, "paper_slap", 0.6), (KEEPS_T, "pour", 0.6),
           (KEEPS_T + 0.6, "riser", 0.4), (NIGHT_T - 0.15, "swish", 0.45), (NIGHT_T + 0.2, "fridge", 0.25),
           (LOW_T, "low_hit", 0.45), (TEMP_T, "descend", 0.3), (URGE_T, "riser", 0.3), (OUT_T - 0.1, "swish", 0.5)]
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
