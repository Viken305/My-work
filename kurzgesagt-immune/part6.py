"""Part 6: Chapter 5, Memory. A week to build the army; victory; most soldiers fade, memory cells stay; years later the
enemy returns and the army is back in days (response graph); vaccines = a harmless wanted poster.

  python3 render.py part6 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part6"
VO, _end = schedule(PART, first=3.0, gap=0.8)
DURATION = _end + 1.8
TM = Timing(PART, VO)

WEEK_T = TM.word("R1", "about a week") - 0.4
WON_T = TM.word("R1", "battle is won") - 0.3
FADE_T = TM.word("R1", "die off") - 0.3
MEM_T = TM.word("R1", "memory cells") - 0.3
YEARS_T = VO["R2"] - 0.3
RETURN_T = TM.word("R2", "same enemy") - 0.4
RECOG_T = TM.word("R2", "recognise") - 0.3
BACK_T = TM.word("R2", "back within days") - 0.4
POX_T = VO["R3"] - 0.4
VAX_T = TM.word("R3", "vaccines") - 0.4
POSTER_T = TM.word("R3", "wanted poster") - 0.5

_rng = np.random.default_rng(9)
CROWD = [(-760 + (i % 6) * 300 + float(_rng.uniform(-60, 60)), -330 + (i // 6) * 320 + float(_rng.uniform(-50, 50)), int(k)) for i, k in enumerate(_rng.integers(0, 3, 18))]
MEMS = {4: "helper", 11: "b"}          # these two become memory cells
CROWD_TRACKS = [Track([(0.0, "determined", 0.0), (WON_T + 0.1 * (i % 6), "cheer", 0.35), (FADE_T + 0.2 * (i % 7), "happy", 0.4),
                       (MEM_T + 0.6 if i in MEMS else FADE_T + 1.2 + 0.2 * (i % 7), "determined" if i in MEMS else "exhausted", 0.5)])
                for i in range(len(CROWD))]
MEM_TRACK = Track([(0.0, "determined", 0.0), (YEARS_T + 0.6, "neutral", 0.5), (RETURN_T + 0.3, "shocked", 0.2), (RECOG_T + 0.3, "smug", 0.35),
                   (BACK_T + 0.6, "determined", 0.35), (VAX_T + 0.2, "focused", 0.4), (POSTER_T + 1.6, "determined", 0.4)])
VILLAIN = Track([(0.0, "smug", 0.0), (RECOG_T + 0.4, "shocked", 0.2), (BACK_T + 0.6, "worried", 0.5)])
KAI_TRACK = Track([(0.0, "happy", 0.0), (POSTER_T + 1.4, "wink", 0.25), (POSTER_T + 2.4, "smug", 0.35)])


def crowd_cell(c, kind, x, y, r, t, p, look, memory=False, seed=0):
    if kind == 0:
        t_cell(c, x, y, r, t, "helper", p, look, seed=seed, memory=memory)
    elif kind == 1:
        b_cell(c, x, y, r, t, p, look, seed=seed, memory=memory)
    else:
        kai(c, x, y, r * 0.9, t, p, look, blink_amount(t, (), 3.8, seed))


def scene_week(c, t):
    k = in_out(prog(t, 0.0, YEARS_T + 0.6))
    cam = Cam(0, 0, lerp(1.0, 1.25, smooth(prog(t, MEM_T, YEARS_T + 0.6))))
    body_world(c, t, cam)
    cam.push(c, 1.0)
    for i, (x, y, kind) in enumerate(CROWD):
        g = out_back(prog(t, 0.4 + 0.12 * i, 0.9 + 0.12 * i), 1.5)      # the army builds up
        if g <= 0:
            continue
        mem = i in MEMS
        if mem:
            kind = 0 if MEMS[i] == "helper" else 1
            tx, ty = (-170, 0) if MEMS[i] == "helper" else (170, 0)
            u = in_out(prog(t, FADE_T + 0.4, MEM_T + 1.0))
            x, y = lerp(x, tx, u), lerp(y, ty, u)
            a = 255
        else:
            a = 255 * (1 - smooth(prog(t, FADE_T + 0.2 * (i % 7), FADE_T + 1.6 + 0.2 * (i % 7))))
            if a <= 1:
                continue
        bob_y = 10 * math.sin(t * 1.6 + i) - 30 * abs(math.sin(t * 7 + i)) * smooth(prog(t, WON_T, WON_T + 0.3)) * (1 - smooth(prog(t, FADE_T - 0.3, FADE_T)))
        c.saveLayerAlpha(None, int(a))
        crowd_cell(c, kind, x, y + bob_y - (40 * (1 - a / 255) if not mem else 0), (88 if mem else 70) * g, t + i * 0.3, CROWD_TRACKS[i].at(t),
                   (0.0, 0.2), memory=mem and t > MEM_T, seed=i)
        c.restore()
        if mem and MEM_T < t < MEM_T + 0.8:
            sparkle(c, x + 50, y - 70, 120 * (1 - prog(t, MEM_T, MEM_T + 0.8)), 255, (255, 235, 150))
    cam.pop(c)
    near_blur(c, [(-80, 1040, 230), (1990, 60, 200)], t, (190, 70, 100), 0.8)
    # day counter while the army builds
    if t < WON_T + 1.0:
        day = 1 + int(6 * clamp(prog(t, 0.6, WEEK_T + 1.2)))
        a = smooth(prog(t, 0.6, 1.0)) * (1 - smooth(prog(t, WON_T + 0.4, WON_T + 1.0)))
        c.drawRRect(rrect(1600, 70, 220, 120, 18), fill((40, 8, 20), 200 * a))
        text(c, "DAY", 1710, 115, 22, (255, 220, 210), 230 * a, 800, spacing=6)
        text(c, str(day), 1710, 172, 56, (255, 214, 120), 255 * a, 800)
    chip(c, "ABOUT A WEEK TO BUILD", 960, 110, (255, 220, 210), t, WEEK_T, WON_T)
    chip(c, "VICTORY!", 960, 110, (255, 214, 120), t, WON_T + 0.2, FADE_T + 0.4)
    chip(c, "MEMORY CELLS", 960, 980, (255, 230, 150), t, MEM_T + 0.2, YEARS_T + 0.4)


def scene_return(c, t):
    k = in_out(prog(t, YEARS_T, POX_T))
    body_world(c, t, Cam(0, 0, 1.0))
    c.drawPaint(fill((40, 6, 18), 90))
    # graph panel on the right
    gx, gy, gw, gh = 980, 200, 820, 560
    c.drawRRect(rrect(gx - 40, gy - 70, gw + 80, gh + 150, 30), fill((24, 4, 12), 200))
    response_graph(c, gx, gy, gw, gh, smooth(prog(t, YEARS_T + 0.4, YEARS_T + 2.4)), smooth(prog(t, RECOG_T, BACK_T + 1.2)))
    # memory cells on the left meet the returning enemy
    mx, my = 440, 560
    p = MEM_TRACK.at(t)
    look = (0.8, -0.2) if t > RETURN_T else (0.0, 0.2)
    burst = prog(t, BACK_T, BACK_T + 1.4)
    if burst <= 0:
        t_cell(c, mx - 120, my, 92, t, "helper", p, look, memory=True, seed=1)
        b_cell(c, mx + 120, my, 92, t + 1, p, look, memory=True, seed=2)
    else:      # instant army: copies burst out in a ring
        rng = np.random.default_rng(6)
        for j in range(14):
            an = j / 14 * 6.28
            d = 230 * out_back(clamp(burst * 1.2 - j * 0.03), 1.4)
            kind = j % 3
            crowd_cell(c, kind, mx + math.cos(an) * d, my + math.sin(an) * d * 0.7, 60, t + j * 0.3, p, (0.8, -0.2), memory=False, seed=j)
        t_cell(c, mx - 60, my, 92, t, "helper", p, look, memory=True, seed=1)
        b_cell(c, mx + 60, my, 92, t + 1, p, look, memory=True, seed=2)
    if t > RETURN_T - 0.6:
        u = out_cubic(prog(t, RETURN_T - 0.6, RETURN_T + 0.8))
        flee = in_cubic(prog(t, BACK_T + 0.6, BACK_T + 1.6))
        bacterium(c, lerp(-200, 140, u) - 400 * flee, 300 - 40 * flee, 56, t, 20, mood=VILLAIN.at(t), wiggle=4 if t > RECOG_T else 1)
    yrs = smooth(prog(t, YEARS_T, YEARS_T + 0.5)) * (1 - smooth(prog(t, RETURN_T, RETURN_T + 0.4)))
    if yrs > 0:
        n = int(lerp(1, 20, clamp(prog(t, YEARS_T, RETURN_T - 0.3))))
        text(c, f"{n} YEARS LATER…", 440, 260, 46, (255, 230, 150), 255 * yrs, 800, spacing=6)
    chip(c, "RECOGNISED AT ONCE", 440, 160, (255, 230, 150), t, RECOG_T, POX_T)


def scene_vaccine(c, t):
    k = in_out(prog(t, POX_T, DURATION))
    cam = Cam(lerp(-80, 60, k), 0, lerp(1.0, 1.08, k))
    body_world(c, t, cam)
    cam.push(c, 1.0)
    pa = out_back(prog(t, POSTER_T - 0.2, POSTER_T + 0.6), 1.4)
    if pa > 0:
        c.save()
        c.translate(0, -60)
        c.scale(pa, pa)
        wanted(c, 0, 0, 380, t)
        c.restore()
    p = MEM_TRACK.at(t)
    t_cell(c, -470, 160, 100, t, "helper", p, (0.8, -0.3) if pa > 0 else (0.3, 0.2), memory=True, seed=1)
    b_cell(c, 470, 160, 100, t + 1, p, (-0.8, -0.3) if pa > 0 else (-0.3, 0.2), memory=True, seed=2)
    kai(c, 640, 300, 100, t, KAI_TRACK.at(t), (-0.5, -0.3), blink_amount(t, KAI_TRACK.change_times(), 3.9, 0.4))
    if t < VAX_T + 0.4:   # chickenpox: spotty virus bounces off
        u = prog(t, POX_T + 0.4, VAX_T + 0.4)
        x, y = lerp(-900, -200, out_cubic(min(1, u * 2))) - 700 * in_cubic(max(0, u * 2 - 1)), -220 + 40 * math.sin(t * 3)
        virus(c, x, y, 60, t, rgb=(230, 90, 120))
    cam.pop(c)
    near_blur(c, [(-80, 1040, 230), (1990, 60, 200)], t, (190, 70, 100), 0.8)
    chip(c, "CHICKENPOX? USUALLY ONLY ONCE", 960, 110, (255, 200, 210), t, POX_T + 0.3, VAX_T)
    chip(c, "VACCINES", 960, 110, (150, 255, 200), t, VAX_T + 0.1, DURATION)
    chip(c, "TRAINED BEFORE THE REAL ENEMY ARRIVES", 960, 1000, (150, 255, 200), t, POSTER_T + 1.2, DURATION)


def draw_frame(c, t):
    if t < YEARS_T + 0.6:
        xfade(c, t, YEARS_T - 0.3, 0.9, scene_week, scene_return, 0.3)
    else:
        xfade(c, t, POX_T - 0.3, 0.9, scene_return, scene_vaccine, 0.25)
    chapter_title(c, t, 5, "MEMORY", (255, 230, 150), 0.2, 2.8)
    fade(c, t, DURATION, 0.5, 0.7)


def sfx_events():
    ev = [(0.2, "swell_soft", 0.6)] + [(0.4 + 0.12 * i, "pop", 0.35) for i in range(18)]
    ev += [(0.6 + i * (WEEK_T + 0.6) / 6, "tink", 0.5) for i in range(7)] + [(WON_T, "boom", 0.5), (WON_T + 0.05, "chime", 0.8), (FADE_T, "swell_soft", 0.6),
           (MEM_T, "shine", 0.9), (YEARS_T - 0.3, "whoosh_long", 0.7)] + [(YEARS_T + 0.3 + 0.25 * i, "ticks", 0.3) for i in range(4)]
    ev += [(RETURN_T, "slide", 0.6), (RECOG_T, "ding", 0.8), (BACK_T, "boom", 0.7), (BACK_T + 0.05, "whoosh", 0.8), (BACK_T + 0.6, "riser", 0.4),
           (POX_T - 0.3, "whoosh_long", 0.6), (POX_T + 0.9, "pop", 0.6), (VAX_T, "chime", 0.7), (POSTER_T, "pop", 0.9), (POSTER_T + 1.4, "ding", 0.6)]
    return ev


MUSIC = dict(
    chords=[(0.0, 48, (0, 7, 12, 16, 19)), (WON_T, 50, (0, 7, 12, 16, 19, 24)), (FADE_T, 45, (0, 7, 12, 15, 19)), (MEM_T, 48, (0, 7, 12, 16, 21)),
            (YEARS_T, 46, (0, 7, 12, 14, 19)), (RETURN_T, 44, (0, 7, 12, 15, 19)), (BACK_T, 48, (0, 7, 12, 16, 19, 24)), (POX_T, 50, (0, 7, 12, 16, 19))],
    plucks=[(VO["R1"], DURATION)], bpm=100, rises=[(0.6, WON_T), (RECOG_T - 1.0, BACK_T)],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
