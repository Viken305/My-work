"""Part 5, hour 72 and after: the 72 slam; the room breathes, wall patterns crawl and a shadow figure stands in the
corner until Sam looks; the 1964 record card (Randy Gardner, 264 hours); the snap back to blue as Sam sleeps, a
sleep-stage graph full of deep sleep and the jar draining; "remember the jar", then a blink back to the opening eye.

  python3 render.py part5 [--still 1,5]
"""
import part1
from film import *  # noqa: F401,F403

PART = "part5"
VO, _end = schedule(PART, first=0.25, gap=0.6, extra={"D1": 0.2, "D2": 0.15})
TM = Timing(PART, VO)
DURATION = _end + 2.3

CARD_T = TM.word("D1", "seventy") - 0.15
ROOM_T = CARD_T + 1.3
WALLS_T = TM.word("D1", "the walls") - 0.1
SHAPES_T = TM.word("D1", "shapes") - 0.1
LOOK_T = TM.word("D1", "many") - 0.1
REC_T = VO["D4"] - 0.3
GARDNER_T = TM.word("D4", "randy") - 0.1
DAYS_T = TM.word("D4", "eleven") - 0.15
GOOD_T = VO["D2"] - 0.3
DEEP_T = TM.word("D2", "deep") - 0.15
DRAIN_T = TM.word("D2", "drains") - 0.4
END_T = VO["D3"] - 0.2
NINE_T = TM.word("D3", "seven") - 0.15
JAR_T = TM.word("D3", "remember") - 0.1
HANDLE_T = TM.end("D3") + 0.3
LOOP_T = DURATION - 0.45                           # blink back into the opening eye

CAPS = Captions(TM, anchors={k: (W / 2, 1450) for k in ("D1", "D4", "D2", "D3")}, accent=RED,
                emph={"seventy", "two", "breathe.", "hallucinate.", "record?", "eleven", "days."},
                hide={"D1": [(CARD_T, CARD_T + 1.25)], "D3": [(JAR_T, DURATION)]})
CAPS_CALM = Captions(TM, anchors={"D2": (W / 2, 1450), "D3": (W / 2, 1450)}, accent=CYAN,
                     emph={"good", "news?", "deep", "sleep,", "drains.", "seven", "nine"}, skip=("D1", "D4"), hide={"D3": [(JAR_T, DURATION)]})
MOTES = Motes(40, 9)
YEAR = Counter("1964", 200, "display")
HRS = Counter("264", 240, "display")
SEPIA = dict(top=(30, 24, 18), bot=(48, 38, 28), paper=(232, 220, 196), ink=(40, 30, 22))
STAGES = [(0, "AWAKE"), (1, "REM"), (2, "LIGHT"), (3, "DEEP")]
HYP = [(0.0, 0), (0.04, 2), (0.08, 3), (0.32, 2), (0.38, 1), (0.44, 3), (0.62, 2), (0.68, 1), (0.76, 3), (0.86, 2), (0.92, 1), (1.0, 1)]


def act_k(t):
    """0 = red hallucination world, 1 = calm blue recovery."""
    return smooth(prog(t, GOOD_T, GOOD_T + 0.15))


def walls(c, t, a):
    for i in range(16):                                # crawling wallpaper lines
        y = 440 + i * 56
        p = skia.Path()
        p.moveTo(-20, y)
        for k in range(1, 23):
            x = k * 50
            p.lineTo(x, y + 14 * a * math.sin(k * 0.7 + t * 2.4 + i * 0.9))
        c.drawPath(p, stroke((120, 30, 60), 3, 150 * a))


def hallucination(c, t):
    pal = ACTS[3]
    room(c, t, pal, moon=1.0, lamp=0.5, win=(700, 470, 260, 260))
    wa = smooth(prog(t, WALLS_T, WALLS_T + 1.0))
    walls(c, t, 0.3 + 0.7 * wa)
    fig = smooth(prog(t, SHAPES_T, SHAPES_T + 0.4)) * (1 - smooth(prog(t, LOOK_T + 0.3, LOOK_T + 0.45)))
    shadow_figure(c, 880, 1290, 120, fig, t)
    look = lerp(-0.2, 1.0, smooth(prog(t, LOOK_T, LOOK_T + 0.3)))
    sam(c, 400, 1290, 140, t, wide=0.9, bags=1.0, mouth="o", look=(look, 0), tilt=4 * math.sin(t * 1.1), blink_phase=0.2)


def record(c, t):
    k = smooth(prog(t, REC_T, REC_T + 0.3))
    c.drawRect(skia.Rect.MakeWH(W, H), grad_v(0, H, SEPIA["top"], SEPIA["bot"]))
    c.save()
    c.translate(540, 940)
    c.rotate(-2 + 2 * k)
    c.drawRect(skia.Rect.MakeXYWH(-430, -470, 860, 860), blur(fillp((0, 0, 0), 120), 24))
    c.drawRect(skia.Rect.MakeXYWH(-440, -480, 860, 860), fillp(SEPIA["paper"]))
    label(c, "SAN DIEGO · 1964", -380, -400, 30, "mono_bold", (120, 96, 70), 255, tracking=0.12)
    if t > REC_T + 0.2:
        YEAR.draw(c, -390, -220, t, REC_T + 0.2, 0.8, SEPIA["ink"], 255)
    ga = smooth(prog(t, GARDNER_T, GARDNER_T + 0.4))
    label(c, "RANDY GARDNER, 17", -380, -140, 42, "mono_bold", SEPIA["ink"], 255 * ga, tracking=0.04)
    label(c, "high-school science project", -380, -90, 32, "regular", (120, 96, 70), 255 * ga)
    if t > DAYS_T:
        HRS.draw(c, -390, 120, t, DAYS_T, 0.9, (190, 40, 50), 255)
        label(c, "HOURS", 20, 50, 46, "mono_bold", SEPIA["ink"], 255 * smooth(prog(t, DAYS_T + 0.5, DAYS_T + 0.8)), tracking=0.1)
        label(c, "AWAKE", 20, 108, 46, "mono_bold", SEPIA["ink"], 255 * smooth(prog(t, DAYS_T + 0.5, DAYS_T + 0.8)), tracking=0.1)
    for i in range(11):                                # eleven days, crossed off one by one
        x, y = -380 + (i % 6) * 128, 170 + (i // 6) * 100
        c.drawRect(skia.Rect.MakeXYWH(x, y, 96, 84), stroke(SEPIA["ink"], 4, 255 * ga))
        label(c, str(i + 1), x + 48, y + 56, 34, "mono_bold", SEPIA["ink"], 200 * ga, "center")
        xk = smooth(prog(t, DAYS_T + 0.1 + i * 0.12, DAYS_T + 0.25 + i * 0.12))
        if xk > 0:
            c.drawLine(x + 6, y + 6, x + 6 + 84 * xk, y + 6 + 72 * xk, stroke((200, 40, 50), 8))
    c.restore()


def hypnogram(c, t, a, t0, t1):
    x0, x1, y0, dy = 230, 990, 500, 78
    for lvl, name in STAGES:
        y = y0 + lvl * dy
        label(c, name, 80, y + 9, 24, "mono_bold", CYAN if name == "DEEP" else ASH, 255 * a)
        c.drawLine(x0, y, x1, y, stroke(PAPER, 1.5, 40 * a))
    u = prog(t, t0, t1)
    pts = []
    for (ua, la), (ub, lb) in zip(HYP[:-1], HYP[1:]):
        if ua > u:
            break
        xb = lerp(x0, x1, min(ub, u))
        pts += [(lerp(x0, x1, ua), y0 + la * dy), (xb, y0 + la * dy)]
        if ub <= u:
            pts.append((xb, y0 + lb * dy))
        if la == 3:                                    # deep sleep blocks glow
            c.drawRect(skia.Rect.MakeLTRB(lerp(x0, x1, ua), y0 + 2.6 * dy, xb, y0 + 3.4 * dy), fillp(CYAN, 70 * a))
    if len(pts) > 1:
        c.drawPath(path_of(pts), stroke(CYAN, 6, 255 * a))
        light(c, pts[-1][0], pts[-1][1], 40, CYAN, 120 * a)


def recovery(c, t):
    pal = ACTS[1]
    room(c, t, pal, moon=1.0, lamp=0.2, win=(-400, 0, 10, 10))
    bed(c, 470, 1300, 760, pal)
    c.drawRRect(rrect(880, 1150, 160, 140, 12), fillp(mix(pal["dim"], (0, 0, 0), 0.3)))
    sleeping_sam(c, 250, 1120, 100, t, pal)
    hypnogram(c, t, smooth(prog(t, GOOD_T + 0.2, GOOD_T + 0.6)), GOOD_T + 0.3, END_T - 0.2)
    lv = lerp(level72(), 0.04, in_out(prog(t, DRAIN_T, END_T)))
    jar(c, 960, 1140, 120, 220, lv, t, CYAN, 1.0, label_a=0.0)
    label(c, "ADENOSINE", 960, 840, 22, "mono_bold", CYAN, 230, "center", tracking=0.1)
    for i in range(3):                                 # z z z
        u = (t * 0.5 + i / 3) % 1
        label(c, "z", 360 + 40 * u + i * 20, 1000 - 160 * u, 40 + 30 * u, "display", SAM, 255 * math.sin(math.pi * u))


def level72():
    return 0.04 + 0.92


NIGHTS = Counter("7-9", 380, "display")


def ending(c, t):
    pal = ACTS[1]
    bg(c, pal)
    light(c, 540, 900, 700, CYAN, 40)
    out = smooth(prog(t, JAR_T - 0.25, JAR_T + 0.05))
    if t < JAR_T + 0.1:                                # the takeaway number
        a = 255 * (1 - out)
        if t > NINE_T:
            NIGHTS.draw(c, 540, 980, t, NINE_T, 0.8, PAPER, a, "center")
        reveal(c, "HOURS A NIGHT", W / 2, 1090, 56, t, NINE_T + 0.5, "mono_bold", CYAN, a, "center", tracking=0.2, stagger=0.02, dur=0.3, blur=8)
        for i in range(9):                             # nine little moons for nine hours
            k = smooth(prog(t, NINE_T + 0.6 + i * 0.06, NINE_T + 0.8 + i * 0.06))
            mx, my = 540 + (i - 4) * 96, 620
            col_ = CYAN if i < 7 else (90, 130, 200)
            c.drawCircle(mx, my, 28 * k, fillp(col_, a))
            c.drawCircle(mx + 12, my - 8, 25 * k, fillp(pal["top"], a))
        label(c, "for most adults", W / 2, 1160, 38, "regular", ASH, a * smooth(prog(t, NINE_T + 0.8, NINE_T + 1.1)), "center")
    k = out_back(prog(t, JAR_T - 0.05, JAR_T + 0.45), 1.3)
    if t > JAR_T - 0.05:
        c.save()
        c.translate(540, 1110)
        sc = lerp(0.6, 1.15, k)
        c.scale(sc, sc)
        jar(c, 0, 0, 230, 430, 0.04 + 0.06 * smooth(prog(t, JAR_T, DURATION)), t, CYAN, 1.0, label_a=0.0)
        c.restore()
    reveal(c, "REMEMBER", W / 2, 1330, 130, t, JAR_T, "display", PAPER, 255, "center", stagger=0.03, dur=0.4, blur=12, outline=10)
    reveal(c, "THE JAR", W / 2, 1460, 130, t, JAR_T + 0.3, "display", CYAN, 255, "center", stagger=0.03, dur=0.4, blur=12, outline=10)
    handle(c, t, HANDLE_T, y=470)


def draw_frame(c, t):
    if t < REC_T:
        hallucination(c, t)
    elif t < GOOD_T:
        record(c, t)
    elif t < END_T:
        recovery(c, t)
    else:
        ending(c, t)
    if t > LOOP_T:
        part1.eye(c, t, 0.0)
    calm = act_k(t)
    MOTES.draw(c, t, mix((255, 190, 200), (220, 230, 255), calm), 0.6)
    for tc in (REC_T, GOOD_T, END_T):
        blink(c, t, tc, 0.16)
    hour_card(c, t, CARD_T, 72, RED, 1.35)
    if t < REC_T:
        hud(c, t, 72, RED, 1.0, glitch=0.6 + 0.4 * smooth(prog(t, WALLS_T, WALLS_T + 1)))
    elif t < GOOD_T:
        hud(c, t, 72, (200, 160, 110), 1.0, title="THE RECORD", sub="264 HOURS · 1964")
    elif t < LOOP_T:
        hud(c, t, 72, CYAN, 1.0, title="SLEEPING", sub="RECOVERY · DEEP SLEEP REBOUND")
    if t >= GOOD_T:
        CAPS_CALM.draw(c, t)
    blink(c, t, 0.0, 0.22)
    blink(c, t, LOOP_T, 0.2)


def OVERLAY(c, t):
    """Captions in the hallucination and record stretches stay sharp while the picture warps."""
    if t < GOOD_T:
        CAPS.draw(c, t)


def POST(t):
    if t < REC_T:
        w = smooth(prog(t, WALLS_T, WALLS_T + 1.0))
        return fatigue_post(0.9, wobble=3 + 9 * w, split=3 + 5 * w)
    if t < GOOD_T:
        return fatigue_post(0.6)
    return fatigue_post(0.0)


def sfx_events():
    ev = [(CARD_T - 0.9, "riser_dark", 0.6), (CARD_T, "trailer_hit", 1.0), (CARD_T + 0.02, "sub_drop", 0.8),
          (WALLS_T, "whisper", 0.55), (SHAPES_T, "reverse_swell", 0.7), (SHAPES_T + 0.3, "whisper", 0.6),
          (LOOK_T + 0.3, "low_hit", 0.7), (REC_T - 0.2, "paper_whoosh", 0.7), (REC_T + 0.1, "paper_slap", 0.8),
          (REC_T + 0.2, "counter", 0.5), (DAYS_T, "counter", 0.5)]
    ev += [(DAYS_T + 0.1 + i * 0.12, "tick", 0.6) for i in range(11)]
    ev += [(GOOD_T, "glass_ting", 0.5), (GOOD_T + 0.1, "shimmer", 0.5), (DRAIN_T, "pour", 0.45), (END_T, "whoosh", 0.4),
           (NINE_T, "counter", 0.45), (NINE_T + 0.6, "shimmer", 0.35), (JAR_T - 0.1, "whoosh", 0.4),
           (JAR_T, "low_hit", 0.5), (LOOP_T, "swish", 0.5)]
    tt = 0.5
    while tt < GOOD_T:
        ev.append((tt + 0.08 * math.sin(tt * 3), "tick", 0.22))   # the clock tick goes off-beat
        tt += 1.0
    return ev


MUSIC = dict(beds=[(0.0, REC_T, "night2", 0.6), (REC_T, GOOD_T, "tension", 0.35), (GOOD_T, DURATION, "wonder", 0.6)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
