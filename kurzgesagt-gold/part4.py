"""Part 4: The delivery and the squeeze. Meteorites rain gold onto the young Earth; gold is spread thin in the rock;
hot water carries it through cracks; an earthquake opens a crack, water flashes to steam, a gold vein is left behind.

  python3 render.py part4 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part4"
VO, _end = schedule(PART, first=0.3, gap=0.6)
DURATION = _end + 1.2
TM = Timing(PART, VO)

RAIN_T = VO["D1"] + 0.6
ROCK_T = VO["D2"] - 0.3
WATER_T = TM.word("D2", "hot water") - 0.2
QUAKE_T = TM.word("D3", "earthquake") - 0.1
STEAM_T = TM.word("D3", "steam") - 0.1
VEIN_T = TM.word("D3", "in a vein") - 0.3
CX = W / 2
CRACK = [(560, -40), (520, 300), (600, 520), (500, 780), (590, 1040), (520, 1300), (600, 1560), (560, 1960)]
_rng = np.random.default_rng(21)
SPECKS = [(float(x), float(y)) for x, y in zip(_rng.uniform(40, 1040, 90), _rng.uniform(300, 1800, 90))]

CAPS = Captions(TM, anchors={"D1": (W / 2, 330), "D2": (W / 2, 330), "D3": (W / 2, 330)},
                heroes={"GOLD": (W / 2, 1560, 170)},
                reacts={"EARTHQUAKE": (react_shake, W / 2, 1480, 96), "STEAM,": (react_steam, W / 2, 1500, 120)})


def crack_pt(k):
    seg = min(int(k * (len(CRACK) - 1)), len(CRACK) - 2)
    u = k * (len(CRACK) - 1) - seg
    return lerp(CRACK[seg][0], CRACK[seg + 1][0], u), lerp(CRACK[seg][1], CRACK[seg + 1][1], u)


def rain_scene(c, t):
    k = in_out(prog(t, 0.0, ROCK_T))
    space_bg(c, t, Cam(0, 0, lerp(1.0, 1.1, k)), warm=0.2)
    ex, ey, er = CX, 1250, 520
    light(c, ex, ey, er * 1.4, (255, 120, 60), 70)
    c.drawCircle(ex, ey, er, shaded(radial((ex - er * 0.3, ey - er * 0.4), er * 1.5, [(150, 110, 100), (90, 60, 60), (40, 26, 34)])))
    disc = skia.Path()
    disc.addCircle(ex, ey, er)
    c.save()
    c.clipPath(disc, doAntiAlias=True)
    rng = np.random.default_rng(3)
    for i in range(14):     # glowing lava cracks on the young crust
        x, y = ex + rng.uniform(-er, er), ey + rng.uniform(-er, er)
        c.drawLine(x, y, x + rng.uniform(-90, 90), y + rng.uniform(-60, 60), stroke(MAGMA, 5, 150))
    impacts = []
    for i in range(20):
        t0 = RAIN_T + i * 0.4
        if t > t0 + 0.9:
            impacts.append((ex + ((i * 173) % 800 - 400) * 0.9, ey - er * 0.7 + (i * 97 % 600), t - t0 - 0.9))
    for x, y, age in impacts:
        light(c, x, y, 90, (255, 180, 100), 220 * math.exp(-age * 2.5))
        c.drawCircle(x, y, 22, fill((40, 20, 20), 200))
        gold_sphere(c, x, y, 9, (255, 150, 90))
    c.restore()
    for i in range(20):
        t0 = RAIN_T + i * 0.4
        u = prog(t, t0, t0 + 0.9)
        if 0 < u < 1:
            tx = ex + ((i * 173) % 800 - 400) * 0.9
            ty = ey - er * 0.7 + (i * 97 % 600)
            sx, sy = tx + 700, ty - 1100
            meteor(c, lerp(sx, tx, in_cubic(u)), lerp(sy, ty, in_cubic(u)), 30 + 8 * (i % 3), t, 238)
    chip(c, "METEORITES DELIVER GOLD", W / 2, 520, GOLD, t, RAIN_T + 0.8, ROCK_T)


def rock_scene(c, t):
    quake = QUAKE_T < t
    amp = 18 * math.exp(-(t - QUAKE_T) * 1.4) if quake else 0.0
    c.save()
    c.translate(amp * math.sin(t * 61), amp * math.cos(t * 53))
    c.drawPaint(fill((30, 22, 40)))
    rock_wall(c, -40, -40, W + 80, H + 80, t, 5, (120, 86, 92))
    for k in range(9):
        y = k * 230 + 60
        c.drawRect(skia.Rect.MakeXYWH(-40, y, W + 80, 90), fill((70, 50, 70) if k % 2 else (150, 110, 100), 70))
    zoom = lerp(1.25, 1.0, out_cubic(prog(t, ROCK_T, ROCK_T + 1.5)))
    # thin cracks (before the quake) with hot water flowing through them
    open_k = out_back(prog(t, QUAKE_T, QUAKE_T + 0.5), 1.4)
    crack = skia.Path()
    crack.moveTo(*CRACK[0])
    for p in CRACK[1:]:
        crack.lineTo(*p)
    c.drawPath(crack, stroke((20, 10, 20), 10 + 70 * open_k))
    wk = smooth(prog(t, WATER_T - 0.2, WATER_T + 0.6)) * (1 - smooth(prog(t, STEAM_T, STEAM_T + 0.5)))
    if wk > 0:
        c.drawPath(crack, stroke((80, 220, 255), 6 + 40 * open_k, 200 * wk))
        for i in range(24):     # water carries specks up the crack
            u = ((t * 0.18 + i / 24) % 1.0)
            x, y = crack_pt(1 - u)
            c.drawCircle(x, y, 8, add((150, 240, 255), 200 * wk))
            if i % 3 == 0:
                gold_sphere(c, x + 10, y, 5, (150, 220, 255), 230 * wk)
    # gold spread thin through the rock: specks that drift towards the crack once water flows
    for i, (x, y) in enumerate(SPECKS):
        pull = smooth(prog(t, WATER_T + i * 0.02, WATER_T + 2.0 + i * 0.02))
        cx_, cy_ = crack_pt(clamp(y / 1960))
        px, py = lerp(x, cx_, pull), y
        if pull < 0.98:
            gold_sphere(c, px, py, 7, (200, 190, 220), 255 * (1 - pull))
    if STEAM_T - 0.2 < t:      # flash to steam
        sk = prog(t, STEAM_T - 0.2, STEAM_T + 2.5)
        for i in range(30):
            x, y = crack_pt(i / 30)
            rise = 200 * ((sk * 1.5 + i * 0.07) % 1.0)
            c.drawCircle(x + 30 * math.sin(t * 2 + i), y - rise, 30 + 30 * sk, fill(WHITE, 90 * (1 - sk)))
        if t < STEAM_T + 0.25:
            c.drawPaint(fill(WHITE, 150 * (1 - prog(t, STEAM_T - 0.2, STEAM_T + 0.25))))
    vk = smooth(prog(t, VEIN_T - 0.4, VEIN_T + 0.8))
    if vk > 0:                 # quartz vein with gold left behind
        c.drawPath(crack, stroke(QUARTZ, (10 + 70 * open_k) * 0.65 * vk, 255))
        c.drawPath(crack, stroke(WHITE, 8, 110 * vk))
        rng = np.random.default_rng(7)
        for i in range(36):
            x, y = crack_pt(rng.uniform(0.04, 0.96))
            gold_sphere(c, x + rng.uniform(-16, 16), y, rng.uniform(6, 13) * vk, (200, 190, 220))
        light(c, *crack_pt(0.5), 500, GOLD, 70 * vk)
    c.restore()
    chip(c, "SPREAD THIN THROUGH THE ROCK", W / 2, 520, (230, 220, 230), t, ROCK_T + 0.4, WATER_T)
    chip(c, "HOT WATER", W / 2, 520, (130, 230, 255), t, WATER_T + 0.3, QUAKE_T - 0.2)
    chip(c, "GOLD VEIN", W / 2, 520, GOLD, t, VEIN_T + 0.6)


def draw_frame(c, t):
    if t < ROCK_T:
        rain_scene(c, t)
    else:
        rock_scene(c, t)
        if t < ROCK_T + 0.3:
            c.drawPaint(fill(WHITE, 220 * (1 - prog(t, ROCK_T, ROCK_T + 0.3))))
    CAPS.draw(c, t)
    fade(c, t, DURATION, 0.25, 0.25)


def sfx_events():
    ev = [(0.1, "swell_soft", 0.6)] + [(RAIN_T + i * 0.4, "whoosh_soft", 0.4) for i in range(12)] + [(RAIN_T + 0.9 + i * 0.4, "boom", 0.35) for i in range(12)]
    ev += [(ROCK_T, "whoosh", 0.7), (WATER_T, "bubble", 0.7), (WATER_T + 0.8, "bubble", 0.5), (QUAKE_T, "boom", 1.0), (QUAKE_T + 0.05, "rumble", 1.0),
           (STEAM_T, "sizzle", 1.0), (STEAM_T + 0.1, "whoosh_long", 0.6), (VEIN_T, "shine", 1.0), (VEIN_T + 0.1, "chime", 0.8)]
    return ev


MUSIC = dict(chords=[(0.0, 45, (0, 7, 12, 15, 19)), (RAIN_T, 47, (0, 7, 12, 16, 19)), (ROCK_T, 43, (0, 7, 12, 15, 19)), (QUAKE_T, 41, (0, 7, 12, 15, 18)),
                     (VEIN_T, 48, (0, 7, 12, 16, 19, 24))],
             plucks=[(0.3, QUAKE_T), (VEIN_T, DURATION)], bpm=104, rises=[(WATER_T, QUAKE_T)], drone=36)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
