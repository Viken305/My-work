"""Part 7: Chapter 6, The Real Majority. Close on the forest floor: a marching ant column; a counter climbs to
20 quadrillion; one person vs 2.5 million ants; a balance scale: all ants ≈ a fifth of all humans' weight.

  python3 render.py part7 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part7"
VO, _end = schedule(PART, first=3.4, gap=1.35)
DURATION = _end + 2.4
TM = Timing(PART, VO)

COUNT_T = TM.word("A1", "twenty quadrillion") - 0.4
PERSON_T = VO["A2"] - 0.4
SCALE_T = VO["A3"] - 0.5
WEIGH_T = TM.word("A3", "a fifth") - 0.4

NIM_TRACK = Track([(0.0, "neutral", 0.0), (1.2, "focused", 0.4), (COUNT_T, "shocked", 0.2), (COUNT_T + 1.4, "worried", 0.4), (PERSON_T + 0.8, "laugh", 0.35),
                   (SCALE_T + 0.5, "focused", 0.4), (WEIGH_T + 0.4, "shocked", 0.2), (WEIGH_T + 1.4, "smug", 0.4)])
LEADER = Track([(0.0, "determined", 0.0), (COUNT_T + 0.6, "smug", 0.35), (PERSON_T + 1.0, "wink", 0.25), (PERSON_T + 2.0, "smug", 0.3)])


def floor_scene(c, t):
    zoom = lerp(1.0, 0.65, in_out(prog(t, COUNT_T, PERSON_T)))
    c.drawPaint(shaded(linear((0, 0), (0, H), [(90, 140, 90), (60, 100, 60)])))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(zoom, zoom)
    c.translate(-W / 2, -H / 2)
    # giant grass blades and a pebble for scale
    rng = np.random.default_rng(3)
    for k in range(30):
        x = rng.uniform(-400, W + 400)
        h = rng.uniform(300, 900)
        sway = 20 * math.sin(t * 1.2 + k)
        p = skia.Path()
        p.moveTo(x - 18, H + 200)
        p.quadTo(x + sway * 0.5, H - h * 0.5, x + sway, H - h)
        p.quadTo(x + sway * 0.5 + 10, H - h * 0.5, x + 18, H + 200)
        c.drawPath(p, fill(mix((70, 150, 70), (40, 100, 50), rng.random())))
    c.drawRect(skia.Rect.MakeXYWH(-800, 760, W + 1600, 900), shaded(linear((0, 760), (0, H + 400), [(140, 110, 80), (100, 76, 56)])))
    c.drawOval(skia.Rect.MakeXYWH(1320, 640, 320, 180), shaded(radial((1420, 680), 220, [(180, 180, 176), (120, 120, 120)])))
    # ant column marching along the soil
    n = int(10 + 40 * smooth(prog(t, COUNT_T - 0.5, PERSON_T)))
    for i in range(n):                       # back rows: smaller ants
        x = (i * 97 - t * 90) % (W + 1200) - 600
        ant(c, x, 790 + (i % 2) * 20, 28, t + i * 0.13, 0)
    for i in range(9):                       # front row: big ants, the leader has a face
        x = (i * 260 + 200 - t * 120) % (W + 800) - 400
        if i == 4:
            x = 900 + 40 * math.sin(t * 0.5)
        ant(c, x, 900, 70 if i != 4 else 95, t + i * 0.13, 0, LEADER.at(t) if i == 4 else None, (0.5, -0.3), walk=1.0 if i != 4 else 0.6)
    c.restore()

    def path(tt):
        return 1500 + 20 * math.sin(tt * 0.7), 260 + 12 * math.sin(tt * 1.3)
    nim(c, t, NIM_TRACK, path, 100, look=(-0.6, 0.7), rim=(255, 230, 170))
    if t > COUNT_T - 0.3:
        u = smooth(prog(math.floor(round(t * 30) / 30 * 12) / 12, COUNT_T - 0.3, COUNT_T + 1.4))
        n = int(20e15 * u ** 3)
        a = smooth(prog(t, COUNT_T - 0.3, COUNT_T)) * (1 - smooth(prog(t, PERSON_T - 0.4, PERSON_T)))
        text(c, f"{n:,}", 900, 230, 70, WHITE, 255 * a, 800)
        text(c, "ANTS ON EARTH · ~20 QUADRILLION", 900, 290, 24, GOLD, 255 * a * smooth(prog(t, COUNT_T + 1.2, COUNT_T + 1.6)), 800, spacing=4)


def person_scene(c, t):
    sky(c, t, mood="day")
    c.drawRect(skia.Rect.MakeXYWH(0, 820, W, 260), fill((110, 160, 90)))
    human(c, 420, 900, 520, (90, 110, 170), 255, wave=smooth(prog(t, PERSON_T + 0.6, PERSON_T + 1.0)), t=t)
    text(c, "1 PERSON", 420, 980, 34, WHITE, 255, 800, spacing=6)
    text(c, "=", 760, 600, 90, WHITE, 230, 800)
    # a swarm grid of ants filling the right side
    k = smooth(prog(t, PERSON_T, PERSON_T + 2.0))
    cols = 26
    for i in range(int(26 * 16 * k)):
        x = 900 + (i % cols) * 36 + 6 * math.sin(t * 3 + i)
        y = 260 + (i // cols) * 36
        ant(c, x, y, 11, t + i * 0.07, math.degrees(math.sin(t + i)) * 0.3)
    text(c, "≈ 2,500,000 ANTS", 1360, 900, 48, GOLD, 255 * smooth(prog(t, PERSON_T + 0.8, PERSON_T + 1.3)), 800, spacing=6)
    text(c, "(EACH DOT HERE IS ABOUT 6,000 ANTS)", 1360, 950, 18, WHITE, 200 * smooth(prog(t, PERSON_T + 1.3, PERSON_T + 1.8)), 800, spacing=3)


def scale_scene(c, t):
    sky(c, t, mood="day")
    c.drawRect(skia.Rect.MakeXYWH(0, 900, W, 180), fill((110, 160, 90)))
    tilt = math.radians(lerp(0, -14, out_back(prog(t, WEIGH_T - 0.6, WEIGH_T + 0.6), 1.6)))
    px, py = 960, 420
    c.drawRect(skia.Rect.MakeXYWH(px - 14, py, 28, 480), fill((120, 100, 80)))
    c.drawPath(poly([(px - 140, 900), (px + 140, 900), (px, 820)]), fill((120, 100, 80)))
    c.save()
    c.translate(px, py)
    c.rotate(math.degrees(tilt))
    c.drawRect(skia.Rect.MakeXYWH(-560, -10, 1120, 20), fill((150, 125, 100)))
    c.restore()
    for side in (-1, 1):
        ex, ey = px + side * 560 * math.cos(tilt), py + side * 560 * math.sin(tilt)
        c.drawLine(ex, ey, ex - 140, ey + 200, stroke((150, 125, 100), 4))
        c.drawLine(ex, ey, ex + 140, ey + 200, stroke((150, 125, 100), 4))
        c.drawOval(skia.Rect.MakeXYWH(ex - 180, ey + 190, 360, 40), fill((170, 145, 120)))
        if side < 0:      # humans: a crowd
            for k in range(14):
                human(c, ex - 150 + (k % 7) * 50, ey + 200 - (k // 7) * 30, 120, mix((90, 110, 170), (200, 120, 110), (k % 4) / 4))
            text(c, "ALL HUMANS", ex, ey + 300, 26, WHITE, 255, 800, spacing=5)
        else:             # ants: a heap
            for k in range(70):
                ax = ex - 140 + (k * 37) % 280
                ay = ey + 190 - (k // 10) * 12 - 20 * math.sin(math.pi * ((k * 37) % 280) / 280)
                ant(c, ax, ay, 12, t + k * 0.1, 0)
            text(c, "ALL ANTS", ex, ey + 300, 26, GOLD, 255, 800, spacing=5)
    big_number(c, "≈ 1/5", 960, 200, 110, GOLD, t, WEIGH_T, DURATION, sub="AS HEAVY AS ALL OF HUMANITY")

    def path(tt):
        return 960 + 20 * math.sin(tt * 0.7), 560 + 12 * math.sin(tt * 1.3)
    nim(c, t, NIM_TRACK, path, 80, look=(0.6, 0.3), rim=(255, 230, 170))


def draw_frame(c, t):
    if t < PERSON_T + 0.4:
        xfade(c, t, PERSON_T - 0.5, 0.9, floor_scene, person_scene, 0.25)
    else:
        xfade(c, t, SCALE_T - 0.4, 0.9, person_scene, scale_scene, 0.25)
    chapter_title(c, t, 6, "THE REAL MAJORITY", GOLD, 0.2, 2.8)
    fade(c, t, DURATION, 0.5, 0.7)


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (1.0, "ticks", 0.4), (2.0, "ticks", 0.4), (COUNT_T, "riser", 0.7), (COUNT_T + 1.4, "boom", 0.6),
            (COUNT_T + 1.45, "ding", 0.8), (PERSON_T - 0.5, "whoosh_long", 0.6), (PERSON_T + 0.6, "pop", 0.6)] + \
           [(PERSON_T + 0.2 * i, "ticks", 0.3) for i in range(10)] + [(SCALE_T - 0.4, "whoosh_long", 0.6), (WEIGH_T, "slide", 0.6), (WEIGH_T + 0.5, "pop", 0.8),
                                                                     (WEIGH_T + 0.55, "chime", 0.7)]


MUSIC = dict(
    chords=[(0.0, 48, (0, 7, 12, 16, 19)), (COUNT_T, 46, (0, 7, 12, 15, 19)), (PERSON_T, 50, (0, 7, 12, 16, 19)), (SCALE_T, 48, (0, 7, 12, 16, 21)),
            (WEIGH_T, 50, (0, 7, 12, 16, 19, 24))],
    plucks=[(VO["A1"], DURATION)], bpm=108, rises=[(COUNT_T, COUNT_T + 1.4), (SCALE_T, WEIGH_T)], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
