"""Part 3: where volcanoes are. Plates, subduction + the Ring of Fire, mid-ocean ridges, hotspots.

  python3 render.py part3 [--still 3,12,20]
"""
import math

import numpy as np

from common import *  # noqa: F401,F403

PART = "part3"
VO = {"C1": 0.6, "C2": 6.4, "C3": 11.6, "C4": 24.6, "C5": 33.1}
DURATION = 45.0
TM = Timing(PART, VO)

CRACK = (TM.word("C1", "cracks") - 0.4, TM.word("C1", "cracks") + 1.2)
PLATES_T = TM.word("C2", "plates")
MOVE_T = TM.word("C2", "moving") - 0.2
SUB = (11.2, 11.8)
DIVE_T = TM.word("C3", "dives")
LINE_T = TM.word("C3", "line of volcanoes") - 0.2
RING = (TM.word("C3", "three quarters") - 0.6, TM.word("C3", "three quarters") - 0.1)
RING_T = TM.word("C3", "ring of fire") - 0.3
RIDGE = (24.3, 24.9)
UNSEEN_T = TM.word("C4", "ocean floor") - 0.2
HOT = (32.8, 33.4)
HAWAII_T = TM.word("C5", "hawaii") - 0.3

# plate boundaries as lon/lat polylines
CRACKS = [[(-30, -60), (-25, -30), (-15, 0), (-30, 25), (-40, 55), (-20, 75)],
          [(60, -50), (70, -20), (65, 10), (80, 35), (100, 45)],
          [(150, -45), (160, -15), (145, 10), (140, 35), (160, 55)],
          [(-120, -50), (-110, -20), (-105, 10), (-120, 40), (-130, 60)],
          [(-30, 25), (10, 30), (40, 35), (65, 10)]]


def interp(pl, n):
    out = []
    for i in range(len(pl) - 1):
        for k in range(n):
            u = k / n
            out.append((lerp(pl[i][0], pl[i + 1][0], u), lerp(pl[i][1], pl[i + 1][1], u)))
    out.append(pl[-1])
    return out


CRACK_PTS = [interp(pl, 8) for pl in CRACKS]


# ---------------------------------------------------------------- 1: globe with plate cracks
def draw_plates(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(12, 12, 38), (26, 20, 66)])))
    Stars().draw(c, t)
    cx, cy, R, rot = 960, 540, 330, -t * 9 + 10
    draw_globe(c, cx, cy, R, rot)
    k = in_out(prog(t, *CRACK))
    for n, pts in enumerate(CRACK_PTS):
        m = int(len(pts) * k)
        seg = []
        for lo, la in pts[:m]:
            x, y, z = globe_point(cx, cy, R, lo, la, rot)
            if z > 0.02:
                seg.append((x, y))
            elif len(seg) > 1:
                c.drawPath(poly(seg, False), stroke(LAVA, 7, 230))
                seg = []
            else:
                seg = []
        if len(seg) > 1:
            c.drawPath(poly(seg, False), blur(stroke(LAVA, 16, 120), 6))
            c.drawPath(poly(seg, False), stroke(LAVA_HOT, 6, 240))
        for j, (lo, la) in enumerate(pts[:m:3]):
            x, y, z = globe_point(cx, cy, R, lo, la, rot)
            g = pop(t, CRACK[1] + 0.1 + (n * 7 + j) * 0.03, 0.4)
            if z > 0.15 and g > 0:
                glow(c, x, y, 26 * g, LAVA, 220)
                c.drawCircle(x, y, 7 * g, fill(LAVA_HOT))
    # plates drifting: little arrows on either side of each crack
    a = smooth(prog(t, MOVE_T, MOVE_T + 0.5))
    if a > 0:
        for n, pts in enumerate(CRACK_PTS[:4]):
            lo, la = pts[len(pts) // 2]
            for sgn in (-1, 1):
                x, y, z = globe_point(cx, cy, R, lo + sgn * (14 + 3 * math.sin(t * 1.5)), la, rot)
                if z > 0.3:
                    d = sgn if n % 2 == 0 else -sgn
                    c.drawPath(poly([(x - 18 * d, y - 9), (x + 6 * d, y - 9), (x + 6 * d, y - 18), (x + 26 * d, y), (x + 6 * d, y + 18), (x + 6 * d, y + 9), (x - 18 * d, y + 9)]), fill(WHITE, 230 * a))
    caption(c, "TECTONIC PLATES", 960, 1000, LAVA_HOT, 30, 255 * smooth(prog(t, PLATES_T, PLATES_T + 0.4)))


# ---------------------------------------------------------------- 2: subduction + a line of volcanoes
SLAB = [(-60, 360), (650, 400), (980, 520), (1250, 760), (1420, 1140)]
_plumes = [Plume(11 + n, 22) for n in range(3)]


def slab_point(u):
    L = [math.dist(SLAB[i], SLAB[i + 1]) for i in range(len(SLAB) - 1)]
    target, acc = sum(L) * clamp(u), 0.0
    for i, l in enumerate(L):
        if acc + l >= target:
            k = (target - acc) / l
            return lerp(SLAB[i][0], SLAB[i + 1][0], k), lerp(SLAB[i][1], SLAB[i + 1][1], k)
        acc += l
    return SLAB[-1]


def draw_subduction(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, 300), [(30, 24, 70), (70, 50, 120)])))
    c.drawRect(skia.Rect.MakeXYWH(0, 300, W, H), shaded(linear((0, 300), (0, H), [(170, 60, 50), (120, 30, 40)])))
    c.drawRect(skia.Rect.MakeXYWH(0, 250, 820, 110), shaded(linear((0, 250), (0, 360), [CYAN, OCEAN])))
    cont = poly([(760, 260), (W, 230), (W, 540), (1180, 560), (980, 440), (820, 330)])
    c.drawPath(cont, fill((110, 150, 100)))
    top = SLAB
    bot = [(x + 40, y + 110) for (x, y) in SLAB][::-1]
    c.drawPath(poly(top + bot), shaded(linear((0, 300), (0, 1080), [(90, 96, 130), (60, 60, 96)])))
    c.drawPath(poly(top, False), stroke((150, 160, 200), 6))
    c.drawPath(poly([(160, 330), (380, 330), (380, 310), (430, 345), (380, 380), (380, 360), (160, 360)]), fill(WHITE, 200))
    for n in range(9):
        u = ((t - SUB[0]) * 0.05 + n / 9) % 1.0
        x, y = slab_point(u)
        if u < 0.6:
            water_drop(c, x, y - 16, 12)
        else:
            r = (u - 0.6) / 0.4
            water_drop(c, x - 100 * r, y - 16 - 300 * r, 12 * (1 - 0.5 * r), 255 * (1 - r))
    # magma rising to a chain of volcanoes
    vol = [(1080, 300, 190, 150), (1320, 280, 230, 190), (1570, 270, 200, 160)]
    for n, (vx, base, w, h) in enumerate(vol):
        g = out_back(prog(t, LINE_T + n * 0.25, LINE_T + n * 0.25 + 0.7))
        if g <= 0:
            continue
        c.drawLine(vx, base, vx - 60 + n * 10, 620, stroke(LAVA, 12, 200 * min(1, g)))
        x, y = volcano(c, vx, base, w, h * g, (90, 80, 120), hot=min(1, g), t=t)
        _plumes[n].draw(c, x, y - 10, t + n, 200, 50, min(1, g), 0.2)
    magma_blob(c, 1180, 640, 60 * smooth(prog(t, DIVE_T + 0.8, DIVE_T + 2)), t, look=(0, -1))
    caption(c, "ONE PLATE DIVES UNDER ANOTHER", 960, 1000, WHITE, 28, 255 * smooth(prog(t, DIVE_T, DIVE_T + 0.4)))


# ---------------------------------------------------------------- Ring of Fire
def _ring_continents():
    rng = np.random.default_rng(5)
    out = []
    for (lon, lat, rad) in [(-78, 30, 30), (-70, -25, 22), (-55, 55, 16), (78, 35, 30), (70, -20, 24), (60, 60, 18)]:
        n = 24
        radii = rad * (0.75 + 0.5 * rng.random(n))
        out.append([(lon + radii[k] * math.cos(2 * math.pi * k / n) * 0.8, lat + radii[k] * math.sin(2 * math.pi * k / n) * 1.2) for k in range(n)])
    return out


RING_CONT = _ring_continents()
RING_DOTS = [(52 * math.cos(math.radians(a)), 8 + 48 * math.sin(math.radians(a))) for a in np.linspace(-200, 20, 46)]


def draw_ring(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(12, 12, 38), (26, 20, 66)])))
    Stars().draw(c, t)
    cx, cy, R = 960, 520, 360
    draw_globe(c, cx, cy, R, 0, continents=RING_CONT, night=120)
    for n, (lo, la) in enumerate(RING_DOTS):
        g = pop(t, RING[1] + n * 0.04, 0.4)
        x, y, z = globe_point(cx, cy, R, lo, -la, 0)
        if g > 0 and z > 0.05:
            pulse = 1 + 0.2 * math.sin(t * 4 + n)
            glow(c, x, y, 30 * g * pulse, LAVA, 220)
            c.drawCircle(x, y, 7 * g, fill(LAVA_HOT))
    text(c, "PACIFIC OCEAN", cx, cy + 20, 30, WHITE, 180 * smooth(prog(t, RING[1], RING[1] + 0.5)), 800, spacing=6)
    k = smooth(prog(t, RING_T, RING_T + 0.4))
    caption(c, "RING OF FIRE  ·  ~3/4 OF THE WORLD'S VOLCANOES", 960, 1000, LAVA_HOT, 30, 255 * k)


# ---------------------------------------------------------------- 3: mid-ocean ridge
_fish = np.random.default_rng(9)
FISH = [(float(_fish.uniform(0, W)), float(_fish.uniform(150, 560)), float(_fish.uniform(40, 90)), int(_fish.integers(0, 2))) for _ in range(6)]


def draw_ridge(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(40, 120, 190), (10, 30, 80)])))
    for k in range(5):
        x = 160 + k * 380 + 30 * math.sin(t * 0.3 + k)
        c.drawPath(poly([(x, -10), (x + 90, -10), (x + 260, 700), (x + 120, 700)]), blur(fill(WHITE, 16), 18))
    sep = (t - RIDGE[0]) * 12
    for sgn in (-1, 1):  # two plates moving apart
        x0 = 960 + sgn * (40 + sep)
        pts = [(x0, 760), (x0 + sgn * 300, 720), (x0 + sgn * 900, 700), (x0 + sgn * 1200, 700), (x0 + sgn * 1200, H + 10), (x0, H + 10)]
        c.drawPath(poly(pts), shaded(linear((0, 700), (0, H), [(70, 60, 100), (40, 30, 70)])))
        for k in range(3):
            ax = 960 + sgn * (360 + k * 250)
            c.drawPath(poly([(ax - 26 * sgn, 820), (ax, 820), (ax, 806), (ax + 30 * sgn, 830), (ax, 854), (ax, 840), (ax - 26 * sgn, 840)]), fill(WHITE, 160))
    glow(c, 960, 800, 260, LAVA, 200)
    c.drawRect(skia.Rect.MakeXYWH(960 - 40 - sep, 760, 80 + 2 * sep, H), shaded(linear((0, 760), (0, H), [LAVA_HOT, LAVA])))
    for k in range(7):  # fresh pillow lava
        ph = (t * 0.3 + k / 7) % 1
        x = 960 + (k - 3) * 22
        c.drawCircle(x, 770 - 30 * math.sin(math.pi * ph), 18, fill(mix(LAVA_HOT, (90, 70, 110), ph), 230))
    for k in range(10):  # bubbles
        ph = (t * 0.25 + k / 10) % 1
        c.drawCircle(940 + 40 * math.sin(k * 3 + t), 740 - 620 * ph, 6 + 4 * (k % 3), stroke(WHITE, 2, 160 * (1 - ph)))
    for (fx, fy, sp, d) in FISH:
        x = (fx + (sp if d else -sp) * t) % (W + 200) - 100
        s = 1 if d else -1
        c.save()
        c.translate(x, fy + 10 * math.sin(t + fx))
        c.scale(s, 1)
        c.drawOval(skia.Rect.MakeXYWH(-30, -14, 60, 28), fill(YELLOW))
        c.drawPath(poly([(-28, 0), (-50, -14), (-50, 14)]), fill(ORANGE))
        c.drawCircle(16, -3, 3.5, fill(INK))
        c.restore()
    caption(c, "PLATES PULL APART", 960, 120, WHITE, 30, 255 * smooth(prog(t, RIDGE[1], RIDGE[1] + 0.4)) * (1 - smooth(prog(t, UNSEEN_T, UNSEEN_T + 0.3))))
    caption(c, "MOST VOLCANIC ACTIVITY IS UNDERWATER", 960, 120, CYAN, 30, 255 * smooth(prog(t, UNSEEN_T + 0.3, UNSEEN_T + 0.7)))


# ---------------------------------------------------------------- 4: hotspot island chain
PLUME_X = 1300
SEA = 520


def draw_hotspot(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, SEA), [(30, 24, 70), (90, 70, 140)])))
    glow(c, 300, 160, 160, YELLOW, 90)
    v = 26.0
    shift = (t - HOT[0]) * v
    islands = []
    for k in range(-2, 7):
        x = PLUME_X + 60 - k * 340 - shift + 200
        built = clamp((PLUME_X + 60 - x) / 90)
        eroded = clamp((PLUME_X - 40 - x) / 1000)
        h = 230 * built * (1 - 0.75 * eroded)
        if h > 4:
            islands.append((x, h, built, eroded))
    c.drawRect(skia.Rect.MakeXYWH(0, SEA, W, H), shaded(linear((0, SEA), (0, H), [CYAN, OCEAN])))
    plate_top = 700
    c.drawRect(skia.Rect.MakeXYWH(0, plate_top, W, 160), shaded(linear((0, plate_top), (0, plate_top + 160), [(96, 84, 120), (70, 60, 96)])))
    for k in range(7):
        ax = ((k * (W + 300) / 7 - shift) % (W + 300)) - 150
        c.drawPath(poly([(ax + 30, plate_top + 80), (ax - 10, plate_top + 80), (ax - 10, plate_top + 66), (ax - 40, plate_top + 90), (ax - 10, plate_top + 114), (ax - 10, plate_top + 100), (ax + 30, plate_top + 100)]), fill(WHITE, 150))
    c.drawRect(skia.Rect.MakeXYWH(0, plate_top + 160, W, H), shaded(linear((0, plate_top + 160), (0, H), [(170, 60, 50), (120, 30, 40)])))
    # the plume: fixed, rising from deep below
    pl = skia.Path()
    pl.moveTo(PLUME_X - 70, H + 10)
    pl.cubicTo(PLUME_X - 50, 960, PLUME_X - 90, 900, PLUME_X - 40, plate_top + 160)
    pl.lineTo(PLUME_X + 40, plate_top + 160)
    pl.cubicTo(PLUME_X + 90, 900, PLUME_X + 50, 960, PLUME_X + 70, H + 10)
    pl.close()
    glow(c, PLUME_X, plate_top + 220, 200, LAVA, 200)
    c.drawPath(pl, shaded(linear((0, plate_top + 160), (0, H), [LAVA_HOT, LAVA])))
    for (x, h, built, eroded) in islands:
        active = built > 0.2 and eroded == 0.0
        if active:
            c.drawLine(x, SEA, x, plate_top, stroke(LAVA, 10, 180 * built))
        cone = poly([(x - h * 0.75, plate_top), (x - h * 0.12, SEA - h * 0.7), (x + h * 0.12, SEA - h * 0.7), (x + h * 0.75, plate_top)])
        c.drawPath(cone, fill(mix((110, 150, 100), (90, 120, 110), eroded)))
        if active:
            glow(c, x, SEA - h * 0.7, 50, LAVA, 200)
            lava_flow(c, [(x + 6, SEA - h * 0.7), (x + h * 0.3, SEA - h * 0.3), (x + h * 0.45, SEA)], 1.0, 9)
    c.drawRect(skia.Rect.MakeXYWH(0, SEA, W, plate_top - SEA), fill(CYAN, 110))  # water in front of the submerged flanks
    c.drawRect(skia.Rect.MakeXYWH(0, SEA, W, 6), fill(WHITE, 90))
    caption(c, "HOTSPOT", PLUME_X, 1010, LAVA_HOT, 30, 255 * smooth(prog(t, HOT[1], HOT[1] + 0.4)))
    act = [i for i in islands if i[2] > 0.2 and i[3] == 0.0]
    if act:
        x, h, _, _ = act[0]
        pill_tag(c, x, SEA - h * 0.7 - 90, "HAWAII", LAVA_HOT, pop(t, HAWAII_T, 0.4), 28)
    text(c, "OLDER  ←", 260, 470, 28, WHITE, 200 * smooth(prog(t, HOT[1] + 1, HOT[1] + 1.5)), 800, spacing=4)


# ---------------------------------------------------------------- compose
def draw_frame(c, t):
    c.clear(col(NAVY))
    scenes(c, t, [((0.0, 0.01), SUB[1], draw_plates), (SUB, RING[1], draw_subduction), (RING, RIDGE[1], draw_ring),
                  (RIDGE, HOT[1], draw_ridge), (HOT, DURATION + 1, draw_hotspot)])
    vignette(c)
    chapter_fade(c, t, DURATION)


def sfx_events():
    ev = [(0.4, "swell_soft", 0.5), (CRACK[0], "rumble", 0.7), (CRACK[0] + 0.3, "sizzle", 0.3)]
    ev += [(CRACK[1] + 0.1 + n * 0.12, "pop", 0.25) for n in range(10)]
    ev += [(PLATES_T, "blip", 0.5), (MOVE_T, "slide", 0.5), (SUB[0], "whoosh", 0.6), (DIVE_T, "rumble", 0.7), (DIVE_T + 0.6, "bubble", 0.5)]
    ev += [(LINE_T + n * 0.25, "boom", 0.5) for n in range(3)]
    ev += [(RING[0], "whoosh_long", 0.7)] + [(RING[1] + n * 0.15, "blip", 0.25) for n in range(12)]
    ev += [(RING_T, "swell_soft", 0.7), (RIDGE[0], "whoosh", 0.6), (RIDGE[0] + 0.3, "bubble", 0.6), (RIDGE[0] + 2, "rumble", 0.4),
           (UNSEEN_T, "bubble", 0.6), (HOT[0], "whoosh", 0.6), (HOT[0] + 0.4, "rumble", 0.6), (HAWAII_T, "pop", 0.6), (HAWAII_T + 0.3, "chime", 0.5)]
    return ev


MUSIC = dict(
    chords=[(0.0, 48, (0, 7, 12, 16, 19)), (6.2, 45, (0, 7, 12, 15, 19)), (11.2, 50, (0, 7, 12, 14, 17)),
            (18.0, 46, (0, 7, 11, 16, 19)), (24.3, 43, (0, 7, 12, 15, 19)), (32.8, 48, (0, 7, 12, 16, 19)),
            (39.0, 53, (0, 7, 11, 16, 19))],
    plucks=[(0.6, DURATION)], bpm=96, rises=[(RING[1], RING[1] + 2.0)],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
