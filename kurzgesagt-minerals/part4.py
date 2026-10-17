"""Part 4: Recipe 3, PRESSURE. Squeezing carbon into diamond, and the volcanic elevator.

  python3 render.py part4 [--still 5,12,20]
"""
import math

from common import *  # noqa: F401,F403

PART = "part4"
VO = {"P1": 0.8, "P2": 3.4, "P3": 6.6, "P4": 17.0, "P5": 19.4}
DURATION = 29.5
TM = Timing(PART, VO)

T_DOCK = 2.9
SQUEEZE = (3.0, 3.5)
SLABS = (TM.word("P2", "squeezing") - 0.6, TM.word("P2", "squeezing") + 0.6)
DIVE = (6.2, 6.8)
DESCEND = (6.9, TM.word("P3", "down") + 0.6)
SLAM = TM.word("P3", "crushing") - 0.3
MORPH = (TM.word("P3", "forced"), TM.word("P3", "possible") + 0.3)
GEM = (VO["P4"] - 0.2, VO["P4"] + 0.5)
ELEV = (19.0, 19.6)
AGE_T = TM.word("P5", "billions")
ROCKET = (TM.word("P5", "shot") - 0.1, TM.word("P5", "shot") + 1.3)
LAND = ROCKET[1] + 1.2

PINKISH = (255, 120, 170)


# ---------------------------------------------------------------- squeeze: carbon between rock slabs
CLUSTER = [(0, 0), (-56, -10), (56, -8), (-28, -54), (30, -52), (-26, 44), (28, 46)]


def draw_squeeze(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(60, 28, 70), (110, 36, 64)])))
    k = in_cubic(prog(t, *SLABS))
    shake = 6 * math.sin(t * 60) * (1 - smooth(prog(t, SLABS[1], SLABS[1] + 0.4))) * (k > 0.95)
    gap = lerp(330, 118, k)
    for sgn in (-1, 1):
        y = H / 2 + sgn * gap
        slab = rrect(380 + shake, (y if sgn > 0 else y - 400), 1160, 400, 40)
        soft_shadow(c, slab, 10, 18, 20, 110)
        c.drawRRect(slab, shaded(linear((0, y - 200), (0, y + 200), [(120, 90, 150), (70, 50, 100)])))
        for n in range(9):
            c.drawCircle(470 + n * 120 + (n % 2) * 30, y + sgn * 120 + (n % 3) * 30 - 30, 12 + (n % 3) * 5, fill(WHITE, 25))
        c.drawPath(poly([(960 - 34, y - sgn * 30), (960 + 34, y - sgn * 30), (960, y - sgn * 90)]), fill(WHITE, 210))
    sy = lerp(1.0, 0.72, k)
    sx = lerp(1.0, 1.18, k)
    for n, (dx, dy) in enumerate(CLUSTER):
        atom(c, 960 + dx * sx, H / 2 + dy * sy, 30, CARBON, t + n, look=(0, -1 if n % 2 else 1) if k > 0.5 else (0, 0))
        c.drawCircle(960 + dx * sx, H / 2 + dy * sy, 30, stroke(lighten(PINK, 0.5), 2, 160))
    pill_tag(c, 960, H / 2 - gap - 70, "CARBON", (200, 200, 220), pop(t, SQUEEZE[1], 0.4) * (1 - smooth(prog(t, SLABS[0], SLABS[0] + 0.3))), 26)


# ---------------------------------------------------------------- dive to 150 km and squeeze into diamond
def depth_now(t):
    return 150 * in_out(prog(t, *DESCEND))


def depth_meter(c, t, km, a=1.0):
    if a <= 0.01:
        return
    mx = 150
    c.saveLayerAlpha(None, int(255 * a))
    c.drawRRect(rrect(mx - 14, 300, 28, 640, 14), fill((20, 12, 30), 180))
    k = km / 150
    c.drawRRect(rrect(mx - 14, 300, 28, 640 * max(k, 0.04), 14), shaded(linear((0, 300), (0, 940), [YELLOW, PINK])))
    for n, v in enumerate((0, 50, 100, 150)):
        y = 320 + n * 200
        c.drawLine(mx + 14, y, mx + 34, y, stroke(WHITE, 4))
        text(c, f"{v} km", mx + 44, y + 10, 26, WHITE, 200, 800, "left")
    y = 320 + 600 * k
    c.drawCircle(mx, y, 26, fill(WHITE))
    c.drawCircle(mx, y, 14, fill(PINK))
    c.drawRRect(rrect(mx + 150, y - 25, 150, 50, 25), fill(PINK))
    text(c, f"{int(round(km))} km", mx + 225, y + 10, 28, INK, 255, 800)
    c.restore()


FCC = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
FCC += [(0.5, 0.5, 0), (0.5, 0.5, 1), (0.5, 0, 0.5), (0.5, 1, 0.5), (0, 0.5, 0.5), (1, 0.5, 0.5)]
INNER = [(0.25, 0.25, 0.25), (0.75, 0.75, 0.25), (0.75, 0.25, 0.75), (0.25, 0.75, 0.75)]
DPTS = [(x - 0.5, y - 0.5, z - 0.5) for (x, y, z) in FCC + INNER]
DBONDS = [(a, b) for a in range(len(FCC), len(DPTS)) for b in range(len(FCC))
          if abs(math.dist(DPTS[a], DPTS[b]) - math.sqrt(3) / 4) < 1e-6]
GRAPH = [(960 + (n % 6 - 2.5) * 92 + (n // 6 % 2) * 46, 540 + (n // 6 - 1) * 150) for n in range(18)]


def draw_deep(c, t):
    km = depth_now(t)
    d = km / 150
    c.drawPaint(shaded(linear((0, 0), (0, H), [mix((60, 40, 110), (70, 26, 60), d), mix((80, 50, 120), (140, 40, 60), d)])))
    scroll = in_out(prog(t, *DESCEND)) * 2400
    for k in range(12):  # rock layers rushing past
        y = (k * 260 - scroll) % 3120 - 300
        wavy_band(c, y, y + 260, mix((90, 70, 140), (150, 44, 62), clamp(k / 11 * 0.5 + d * 0.5)), 60 + k, 16, 140)
    if t < DESCEND[1] + 0.5:  # the surface leaving the top of the frame
        sy = 300 - scroll
        if sy > -120:
            c.drawRect(skia.Rect.MakeXYWH(0, sy - 400, W, 400), shaded(linear((0, sy - 400), (0, sy), [NAVY, (50, 40, 110)])))
            c.drawRect(skia.Rect.MakeXYWH(0, sy - 10, W, 22), fill((90, 190, 130)))
            bird(c, 1400, sy - 8, 54, t, look=(-0.3, 1))
    depth_meter(c, t, km)
    # pressure arrows slam in once we arrive
    sl = out_back(prog(t, SLAM, SLAM + 0.45), 1.2)
    if sl > 0:
        for x in (560, 960, 1360, 1760):
            for sgn, y0 in ((1, -150), (-1, H + 150)):
                y = lerp(y0, 60 if sgn > 0 else 1020, sl) + 8 * math.sin(t * 8 + x) * sgn
                c.drawPath(poly([(x - 30, y), (x + 30, y), (x + 30, y + 70 * sgn), (x + 60, y + 70 * sgn), (x, y + 130 * sgn),
                                 (x - 60, y + 70 * sgn), (x - 30, y + 70 * sgn)]), fill(WHITE, 200))
        text(c, "PRESSURE", 960, 250, 34, WHITE, 230 * smooth(prog(t, SLAM + 0.2, SLAM + 0.5)), 800, spacing=10)
    # carbon: loose sheets -> diamond cage
    ca = smooth(prog(t, DESCEND[1] - 0.6, DESCEND[1]))
    if ca > 0:
        m = in_out(prog(t, *MORPH))
        yaw = 0.55 + 0.25 * (t - MORPH[0])
        proj = [project(p, 330, yaw, 0.42, 1250, 560) for p in DPTS]
        pos = [(lerp(gx + 290, px, m), lerp(gy, py, m), lerp(1.0, kk, m)) for (gx, gy), (px, py, _, kk) in zip(GRAPH, proj)]
        c.saveLayerAlpha(None, int(255 * ca * (1 - smooth(prog(t, GEM[0], GEM[1])))))
        if m > 0.6:
            glow(c, 1250, 560, 330, PINK, 120 * smooth(prog(m, 0.6, 1)))
            bonds = skia.Path()
            for a, b in DBONDS:
                bonds.moveTo(*pos[a][:2])
                bonds.lineTo(*pos[b][:2])
            c.drawPath(bonds, stroke(lighten(PINK, 0.6), 8, 230 * smooth(prog(m, 0.6, 1))))
        if m < 0.4:
            sheets = skia.Path()
            for n in range(18):
                if n % 6 != 5:
                    sheets.moveTo(*pos[n][:2])
                    sheets.lineTo(*pos[n + 1][:2])
            c.drawPath(sheets, stroke((150, 150, 180), 6, 200 * (1 - m / 0.4)))
        order = sorted(range(18), key=lambda i: -proj[i][2] if m > 0.5 else i)
        jitter = 3 * math.sin(t * 40) * (1 - m) * (sl > 0.5)
        for i in order:
            x, y, kk = pos[i]
            atom(c, x + jitter, y, 26 * kk, CARBON, t + i, face=True, look=(0, 0))
            c.drawCircle(x + jitter, y, 26 * kk, stroke(lighten(PINK, 0.6), 3, 220))
        c.restore()
        pill_tag(c, 1250, 300, "LOOSE SHEETS", (200, 200, 220), pop(t, DESCEND[1] - 0.2, 0.4) * (1 - smooth(prog(t, MORPH[0], MORPH[0] + 0.3))), 26)
    # that's a diamond
    g = pop(t, GEM[0] + 0.1, 0.6)
    if g > 0:
        glow(c, 1250, 560, 420 * g, PINK, 150)
        diamond_gem(c, 1250, 500, 200 * g, t)
        ph = prog(t, GEM[0] + 0.4, GEM[0] + 1.4)
        if 0 < ph < 1:
            sparkle(c, 1360, 430, 60 * math.sin(math.pi * ph), rot=ph * 90)
        caption(c, "DIAMOND", 1250, 800, PINK, 34, 255 * smooth(prog(t, GEM[0] + 0.3, GEM[0] + 0.6)))
    f = math.sin(math.pi * prog(t, GEM[0], GEM[0] + 0.5))
    if f > 0:
        c.drawPaint(fill((255, 230, 240), 200 * f))


def diamond_gem(c, x, y, s, t, rgb=(255, 214, 236)):
    """Brilliant-cut diamond, side view: crown + pavilion facets."""
    c.save()
    c.translate(x, y)
    c.rotate(bob(t, 3, 4))
    crown_y, girdle, table = -s * 0.45, s, s * 0.55
    c.drawPath(poly([(-girdle, 0), (-table, crown_y), (table, crown_y), (girdle, 0)]), fill(lighten(rgb, 0.5)))
    c.drawPath(poly([(-girdle, 0), (girdle, 0), (0, s * 1.1)]), fill(rgb))
    facets = [([(-table, crown_y), (-table * 0.3, 0), (-girdle, 0)], 0.75), ([(-table, crown_y), (table * 0.0, crown_y), (-table * 0.3, 0)], 0.9),
              ([(table, crown_y), (table * 0.3, 0), (girdle, 0)], 0.35), ([(-girdle, 0), (-table * 0.3, 0), (0, s * 1.1)], 0.7),
              ([(girdle, 0), (table * 0.3, 0), (0, s * 1.1)], 0.15), ([(-table * 0.3, 0), (table * 0.3, 0), (0, s * 1.1)], 0.45)]
    for pts, k in facets:
        c.drawPath(poly(pts), fill(mix(darken(rgb, 0.25), WHITE, k), 230))
    c.drawPath(poly([(-girdle, 0), (-table, crown_y), (table, crown_y), (girdle, 0), (0, s * 1.1)]), stroke(WHITE, max(2, s * 0.02), 230))
    c.drawLine(-girdle, 0, girdle, 0, stroke(WHITE, max(2, s * 0.015), 200))
    c.restore()


# ---------------------------------------------------------------- volcanic elevator
SURF = 420
VENT = 860


def pipe_path():
    p = skia.Path()
    p.moveTo(VENT - 70, SURF)
    p.cubicTo(VENT - 40, 650, VENT - 18, 900, VENT - 14, H + 20)
    p.lineTo(VENT + 14, H + 20)
    p.cubicTo(VENT + 18, 900, VENT + 40, 650, VENT + 70, SURF)
    p.close()
    return p


def gem_track(t):
    """Diamond position: waiting at depth, rocketing up the pipe, arcing onto the bird."""
    r = prog(t, *ROCKET)
    if r < 1:
        y = lerp(1000, SURF - 40, in_cubic(r) * 0.7 + smooth(r) * 0.3)
        return VENT + 6 * math.sin(t * 30) * (r > 0), y, r
    a = prog(t, ROCKET[1], LAND)
    x = lerp(VENT, 1215, a)
    y = lerp(SURF - 40, SURF - 186, a) - 330 * math.sin(math.pi * a)
    return x, y, 1.0


def draw_elevator(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, SURF), [(14, 14, 44), (52, 38, 104)])))
    Stars(80, 9).draw(c, t, 0.7)
    for k, (y, cc) in enumerate([(SURF, (92, 74, 140)), (540, (86, 56, 120)), (680, (100, 46, 96)), (820, (120, 42, 76)), (960, (140, 44, 62))]):
        wavy_band(c, y, 1080, cc, k + 70, amp=10 + k * 3)
    c.drawRect(skia.Rect.MakeXYWH(0, SURF - 8, W, 18), fill((90, 190, 130)))
    hot = smooth(prog(t, ROCKET[0] - 0.3, ROCKET[0])) * (1 - 0.6 * smooth(prog(t, ROCKET[1] + 0.5, LAND + 1)))
    c.drawPath(pipe_path(), fill(mix((70, 40, 80), ORANGE, hot)))
    if hot > 0:
        glow(c, VENT, 760, 300, ORANGE, 120 * hot)
    c.drawPath(poly([(VENT - 210, SURF), (VENT - 80, SURF - 90), (VENT + 80, SURF - 90), (VENT + 210, SURF)]), fill((70, 52, 120)))
    depth_meter(c, t, 150 * (1 - clamp((1000 - gem_track(t)[1]) / (1000 - SURF + 40))) if t < ROCKET[1] else 0)
    # eruption puffs
    for n in range(10):
        k = prog(t, ROCKET[1] - 0.1 + n * 0.08, ROCKET[1] + 1.6 + n * 0.08)
        if 0 < k < 1:
            ang = -math.pi / 2 + (n - 4.5) * 0.18
            c.drawCircle(VENT + math.cos(ang) * 260 * k, SURF - 90 + math.sin(ang) * 300 * k, 40 + 60 * k,
                         fill(mix(ORANGE, (120, 110, 150), k), 200 * (1 - k)))
    bx, by = 1215, SURF + 4
    landed = t >= LAND
    joy = smooth(prog(t, LAND, LAND + 0.3)) * (1 - smooth(prog(t, LAND + 1.6, LAND + 2.2)))
    bird(c, bx, by, 64, t, look=(-0.8, -0.6) if not landed else (0, -1), tilt=-6 * joy, wing=joy)
    x, y, r = gem_track(t)
    if landed:
        x, y = bx + 2, SURF - 196 + bob(t, 2, 1.5)
    if r > 0 and not landed and t < ROCKET[1]:
        for k in range(4):
            c.drawLine(x - 18 + k * 12, y + 40, x - 18 + k * 12, y + 140, stroke(YELLOW, 6, 160))
    glow(c, x, y, 90, PINK, 150)
    diamond_gem(c, x, y, 34, t)
    pill_tag(c, VENT + 240, 960, "BILLIONS OF YEARS OLD", PINKISH, pop(t, AGE_T, 0.4) * (1 - smooth(prog(t, ROCKET[0], ROCKET[0] + 0.3))), 26)
    if landed:
        sparkle(c, x + 30, y - 30, 26 * math.sin(math.pi * prog(t, LAND, LAND + 0.8)), rot=40)


# ---------------------------------------------------------------- compose
def draw_frame(c, t):
    c.clear(col(NAVY))
    if t < SQUEEZE[1]:
        title_backdrop(c, t, PINK)
    scenes = [(SQUEEZE, DIVE[1], draw_squeeze), (DIVE, ELEV[1], draw_deep), (ELEV, DURATION + 1, draw_elevator)]
    for (t0, t1), t_end, fn in scenes:
        if t0 <= t < t_end:
            a = smooth(prog(t, t0, t1))
            if a < 1:
                c.saveLayerAlpha(None, int(255 * a))
            fn(c, t)
            if a < 1:
                c.restore()
    title_sequence(c, t, 3, "PRESSURE", PINK, icon_down, 0.3, T_DOCK)
    vignette(c)
    chapter_fade(c, t, DURATION)


def sfx_events():
    return [(0.3, "whoosh_soft", 0.6), (0.4, "pop", 0.8), (0.55, "boom", 0.5), (T_DOCK, "whoosh_soft", 0.5),
            (SQUEEZE[1], "pop", 0.5), (SLABS[0], "slide", 0.6), (SLABS[1] - 0.05, "boom", 0.8),
            (DIVE[0], "whoosh_long", 0.8), (DESCEND[0], "rumble", 0.8), (DESCEND[0] + 2.5, "rumble", 0.7),
            (SLAM, "boom", 1.0), (SLAM + 0.1, "whoosh", 0.5), (MORPH[0], "rumble", 0.6), (MORPH[0] + 1, "riser", 0.6),
            (MORPH[1] - 0.6, "click", 0.7), (MORPH[1] - 0.4, "click", 0.6), (GEM[0], "shine", 1.0),
            (ELEV[0], "whoosh_soft", 0.6), (AGE_T, "pop", 0.5), (ROCKET[0] - 0.3, "rumble", 0.9), (ROCKET[0], "riser", 0.9),
            (ROCKET[1], "boom", 1.0), (ROCKET[1] + 0.1, "whoosh_long", 0.7), (LAND, "ding", 0.9), (LAND + 0.1, "pop", 0.6)]


MUSIC = dict(
    chords=[(0.0, 49, (0, 7, 12, 15, 19)), (6.2, 45, (0, 7, 12, 15, 19)), (11.5, 46, (0, 7, 11, 15, 19)),
            (16.8, 52, (0, 7, 11, 16, 19)), (19.2, 49, (0, 7, 12, 16, 19)), (24.5, 54, (0, 7, 11, 16, 19))],
    plucks=[(6.8, 16.5), (19.4, DURATION)], bpm=96, rises=[(MORPH[0], MORPH[1])],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
