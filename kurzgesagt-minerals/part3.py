"""Part 3: Recipe 2, WATER. Dissolving, salt flats, hydrothermal veins, the Naica crystal cave.

  python3 render.py part3 [--still 5,12,20]
"""
import math

import numpy as np

from common import *  # noqa: F401,F403

PART = "part3"
VO = {"W1": 0.8, "W2": 3.5, "W3": 8.8, "W4": 17.2, "W5": 27.4, "W6": 35.7}
DURATION = 40.5
TM = Timing(PART, VO)

T_DOCK = 2.9
BEAKER = (3.0, 3.5)
DROP_T = TM.word("W2", "dissolving") - 0.5
BEHIND_T = TM.word("W2", "leaving")
FLAT = (8.4, 9.0)
SHRINK = (9.4, 15.6)
SALT_T, GYP_T = TM.word("W3", "salt and"), TM.word("W3", "gypsum")
VEINS = (16.6, 17.2)
FLOW_T = TM.word("W4", "hot water") - 0.2
DEPOSIT = (TM.word("W4", "cools") - 0.2, TM.word("W4", "veins") + 0.8)
GOLD_T = TM.word("W4", "gold") - 0.15
CAVE = (26.8, 27.4)
GROWTH = (27.8, 34.4)
DRAIN = (34.4, 35.2)
LIGHTS = 35.25
BIRD_FLY = (35.9, 36.9)
SCALE_T = TM.word("W6", "twelve") - 0.1


# ---------------------------------------------------------------- beaker: dissolve + leave behind
BX, BY, BW, BH = 960, 600, 380, 460       # beaker centre and size
_rng = np.random.default_rng(31)
IONS = [dict(src=n // 6, ph=_rng.uniform(0, 6.28, 2), f=_rng.uniform(0.4, 0.9, 2), amp=_rng.uniform(60, 140, 2),
             rgb=NA_COL if n % 2 == 0 else CL_COL, home=(BX - 120 + (n % 6) * 48, BY + BH / 2 - 40 - (n // 6) * 0 - (n % 2) * 0))
        for n in range(18)]
CUBE_X = [-90, 10, 100]


def water_level(t):
    return lerp(BY - BH / 2 + 90, BY + BH / 2 - 70, in_out(prog(t, BEHIND_T, BEHIND_T + 1.6)))


def draw_beaker(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [NAVY, (30, 40, 90)])))
    glow(c, BX, BY, 520, CYAN, 60)
    x0, y0 = BX - BW / 2, BY - BH / 2
    lvl = water_level(t)
    body = rrect(x0, y0, BW, BH, 40)
    soft_shadow(c, body, 16, 24, 22, 110)
    c.drawRRect(body, fill(ICE, 40))
    c.save()
    c.clipRRect(body, doAntiAlias=True)
    wave = skia.Path()
    wave.moveTo(x0, lvl)
    for x in range(int(x0), int(x0 + BW) + 20, 20):
        wave.lineTo(x, lvl + 6 * math.sin(x / 40 + t * 3))
    wave.lineTo(x0 + BW, y0 + BH)
    wave.lineTo(x0, y0 + BH)
    wave.close()
    c.drawPath(wave, shaded(linear((0, lvl), (0, y0 + BH), [(CYAN, 210), ((40, 110, 190), 230)])))
    # falling salt cubes that dissolve into ions
    for i, dx in enumerate(CUBE_X):
        t0 = DROP_T + i * 0.25
        k = prog(t, t0, t0 + 0.45)
        dis = smooth(prog(t, t0 + 0.6, t0 + 1.6))
        if k > 0 and dis < 1:
            y = lerp(y0 - 140, lvl + 60 + i * 25, in_cubic(k))
            cube(c, BX + dx, y, 34 * (1 - dis), t * 0.6 + i, 0.5, ICE, 255, 220, 40)
    settle = in_out(prog(t, BEHIND_T + 0.4, BEHIND_T + 2.0))
    for n, ion in enumerate(IONS):
        i = ion["src"]
        t0 = DROP_T + i * 0.25 + 0.6
        e = smooth(prog(t, t0, t0 + 1.2))
        if e <= 0 or settle >= 1:
            continue
        cx, cy = BX + CUBE_X[i], water_level(t0) + 60 + i * 25
        x = cx + ion["amp"][0] * e * math.sin(ion["f"][0] * t + ion["ph"][0])
        y = cy + ion["amp"][1] * e * 0.8 * math.sin(ion["f"][1] * t + ion["ph"][1])
        x = clamp(x, x0 + 30, x0 + BW - 30)
        y = clamp(y, lvl + 26, y0 + BH - 30)
        hx, hy = ion["home"]
        atom(c, lerp(x, hx, settle), lerp(y, hy, settle), 18, ion["rgb"], t + n, 255 * (1 - smooth(prog(t, BEHIND_T + 1.7, BEHIND_T + 2.1))))
    # crystals left behind on the bottom
    for k in range(6):
        g = pop(t, BEHIND_T + 1.75 + k * 0.08, 0.4)
        if g > 0:
            cube(c, BX - 120 + k * 48, BY + BH / 2 - 42, 18 * g, 0.6 + k, 0.5, ICE, 255, 220, 30)
    c.restore()
    c.drawRRect(body, stroke(ICE, 5, 200))
    c.drawRRect(rrect(x0 + 24, y0 + 30, 14, BH - 80, 7), fill(WHITE, 60))
    for k in range(3):  # evaporation squiggles
        ph = (t * 0.5 + k / 3) % 1
        a = 200 * math.sin(math.pi * ph) * smooth(prog(t, BEHIND_T, BEHIND_T + 0.4)) * (1 - smooth(prog(t, BEHIND_T + 2.4, BEHIND_T + 3)))
        if a > 2:
            sx = BX - 80 + k * 80
            p = skia.Path()
            p.moveTo(sx, y0 - 20 - 120 * ph)
            for j in range(1, 6):
                p.lineTo(sx + 12 * math.sin(j * 1.6), y0 - 20 - 120 * ph - j * 14)
            c.drawPath(p, stroke(WHITE, 5, a))
    pill_tag(c, BX, y0 - 60, "DISSOLVE", CYAN, pop(t, DROP_T + 0.8, 0.4) * (1 - smooth(prog(t, BEHIND_T - 0.2, BEHIND_T + 0.2))), 28)
    pill_tag(c, BX, y0 - 60, "LEAVE BEHIND", ICE, pop(t, BEHIND_T + 1.8, 0.4), 28)


# ---------------------------------------------------------------- salt flat
HZ = 520
_PIC = {}


def hex_crust():
    """Perspective hexagon salt crust, recorded once as a Skia picture."""
    if "hex" not in _PIC:
        rec = skia.PictureRecorder()
        c = rec.beginRecording(skia.Rect.MakeWH(W, H))
        c.clipRect(skia.Rect.MakeXYWH(0, HZ, W, H - HZ))
        f, camh, hs = 520.0, 140.0, 18.0
        for row in range(0, 60):
            for col_ in range(-40, 41):
                x = col_ * hs * 1.75 + (row % 2) * hs * 0.875
                z = 60 + row * hs * 1.5
                if z - hs < 25:
                    continue
                pts = [(W / 2 + (x + hs * math.cos(a)) * f / (z + hs * math.sin(a)), HZ + camh * f / (z + hs * math.sin(a)))
                       for a in [k * math.pi / 3 + math.pi / 6 for k in range(6)]]
                if max(p[0] for p in pts) < -50 or min(p[0] for p in pts) > W + 50:
                    continue
                c.drawPath(poly(pts), stroke((200, 190, 225), max(0.6, 3.5 * 60 / z), 220 * clamp(1 - (z - 60) / 900)))
        _PIC["hex"] = rec.finishRecordingAsPicture()
    return _PIC["hex"]


LAKE_R = [300, 260, 240, 270, 330, 360, 320, 290]
RIM_CUBES = [(a, s) for s, a in zip(np.linspace(1.3, 0.62, 22), np.random.default_rng(4).uniform(0, 6.28, 22))]


def lake_scale(t):
    return lerp(1.35, 0.6, in_out(prog(t, *SHRINK)))


def rim_point(a, s):
    k = int(a / 6.283 * len(LAKE_R)) % len(LAKE_R)
    r = LAKE_R[k] * s
    return 1000 + r * math.cos(a), 720 + r * math.sin(a) * 0.32


def draw_flat(c, t):
    sp = prog(t, FLAT[0], 17.0)
    sun_x, sun_y = lerp(600, 1500, sp), 300 - 140 * math.sin(math.pi * lerp(0.15, 0.85, sp))
    c.drawPaint(shaded(linear((0, 0), (0, HZ), [(60, 40, 120), mix((255, 170, 120), (255, 120, 120), sp)])))
    glow(c, sun_x, sun_y, 380, YELLOW, 170)
    c.drawCircle(sun_x, sun_y, 130, shaded(radial((sun_x - 30, sun_y - 30), 150, [(255, 245, 200), YELLOW])))
    for (mx, mw, mh, cc) in [(-100, 700, 170, (150, 90, 150)), (500, 600, 120, (180, 100, 150)), (1050, 800, 150, (140, 80, 140))]:
        c.drawPath(poly([(mx, HZ), (mx + mw * 0.45, HZ - mh), (mx + mw * 0.55, HZ - mh * 0.9), (mx + mw, HZ)]), fill(cc))
    c.drawRect(skia.Rect.MakeXYWH(0, HZ, W, H - HZ), shaded(linear((0, HZ), (0, H), [(250, 236, 236), (226, 222, 245)])))
    c.saveLayerAlpha(None, int(255 * (0.35 + 0.65 * smooth(prog(t, SHRINK[0], SHRINK[1])))))
    c.drawPicture(hex_crust())
    c.restore()
    s = lake_scale(t)
    lake = blob_path(1000, 720, [r * s for r in LAKE_R], 0.2)
    m = skia.Matrix()
    m.setScale(1.0, 0.32, 1000, 720)
    lake.transform(m)
    c.drawPath(lake, stroke(WHITE, 26, 255))
    c.drawPath(lake, shaded(linear((0, 640), (0, 800), [(120, 220, 240), (60, 170, 210)])))
    c.drawPath(lake, stroke((235, 250, 255), 4, 255))
    glow(c, 1000 + 200 * s, 700, 90, WHITE, 120)
    for (a, s0) in RIM_CUBES:
        if s < s0:
            x, y = rim_point(a, s0)
            g = out_back(clamp((s0 - s) / 0.06))
            cube(c, x, y, 13 * g, 0.6 + a, 0.5, ICE, 255, 220, 30)
    for n, (x, y, L, ang) in enumerate([(560, 880, 110, -70), (600, 890, 80, -105), (1460, 860, 120, -80), (1500, 870, 70, -50), (1420, 875, 60, -115)]):
        g = out_cubic(prog(t, GYP_T - 0.2 + n * 0.1, GYP_T + 0.6 + n * 0.1))
        if g > 0.02:
            prism(c, x, y, L * g, 13, ang, (250, 225, 215), tip=0.8)
    pill_tag(c, 1000 + 330 * s, 650, "SALT", ICE, pop(t, SALT_T, 0.4), 26)
    pill_tag(c, 1470, 730, "GYPSUM", (250, 215, 205), pop(t, GYP_T + 0.2, 0.4), 26)
    bird(c, 330, 950, 72, t, look=(0.9, -0.2 + 0.2 * math.sin(t)), tilt=4)


# ---------------------------------------------------------------- hydrothermal veins
CRACKS = [[(700, 1100), (720, 920), (660, 780), (700, 620), (640, 470), (680, 330)],
          [(1200, 1100), (1160, 940), (1230, 800), (1180, 640), (1250, 500), (1210, 360)],
          [(700, 620), (820, 560), (900, 600), (1000, 520)],
          [(1180, 640), (1060, 700), (980, 660)],
          [(1230, 800), (1380, 760), (1480, 820)]]
GOLD = [(668, 512), (1222, 560), (900, 600), (1380, 762)]


def seglen(pl):
    return [math.dist(pl[i], pl[i + 1]) for i in range(len(pl) - 1)]


def partial(pl, frac, reverse=False):
    """Polyline truncated to the first `frac` of its length (from the end if reverse)."""
    pts = pl[::-1] if reverse else pl
    L = seglen(pts)
    target, acc = sum(L) * clamp(frac), 0.0
    p = skia.Path()
    p.moveTo(*pts[0])
    for i, l in enumerate(L):
        if acc + l >= target:
            u = (target - acc) / l if l else 0
            p.lineTo(lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u))
            return p
        p.lineTo(*pts[i + 1])
        acc += l
    return p


def point_at(pl, frac):
    L = seglen(pl)
    target, acc = sum(L) * (frac % 1.0), 0.0
    for i, l in enumerate(L):
        if acc + l >= target:
            u = (target - acc) / l if l else 0
            return lerp(pl[i][0], pl[i + 1][0], u), lerp(pl[i][1], pl[i + 1][1], u)
        acc += l
    return pl[-1]


def draw_veins(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, 160), [(40, 60, 120), (80, 90, 150)])))
    for k, (y, cc) in enumerate([(150, (92, 74, 140)), (300, (80, 64, 130)), (480, (68, 54, 118)), (680, (60, 44, 104)), (860, (54, 38, 92))]):
        wavy_band(c, y, 1080, cc, k + 50, amp=14)
    c.drawRect(skia.Rect.MakeXYWH(0, 130, W, 22), fill((90, 190, 130)))
    glow(c, W / 2, 1180, 700, (255, 90, 60), 170)
    text(c, "HOT", 1700, 1010, 34, (255, 140, 110), 230, 800, spacing=6)
    text(c, "COOLER", 1700, 260, 34, CYAN, 230, 800, spacing=6)
    flow = smooth(prog(t, FLOW_T, FLOW_T + 2.0))
    dep = prog(t, *DEPOSIT)
    for n, pl in enumerate(CRACKS):
        c.drawPath(poly(pl, False), stroke((26, 18, 46), 22))
        if flow > 0:
            c.drawPath(partial(pl, flow), blur(stroke(CYAN, 26, 120), 8))
            c.drawPath(partial(pl, flow), stroke(lighten(CYAN, 0.2), 10, 230))
        if dep > 0:  # quartz vein builds from the cool end down
            c.drawPath(partial(pl, smooth(dep - n * 0.05), reverse=True), stroke((245, 245, 255), 16, 255))
    if flow > 0:
        for n, pl in enumerate(CRACKS):  # dissolved-mineral passengers riding upward
            for j in range(6):
                f = (t * 0.12 + j / 6 + n * 0.13) % 1.0
                if f < flow:
                    x, y = point_at(pl, f)
                    c.drawCircle(x, y, 7, fill(WHITE, 230 * (1 - 0.6 * dep)))
    for n, (x, y) in enumerate(GOLD):
        g = pop(t, GOLD_T + n * 0.12, 0.45)
        if g > 0:
            glow(c, x, y, 50 * g, YELLOW, 170)
            c.drawPath(blob_path(x, y, [16 * g, 12 * g, 18 * g, 13 * g, 15 * g, 11 * g], 0.4), fill(YELLOW))
            c.drawCircle(x - 4 * g, y - 4 * g, 5 * g, fill(WHITE, 180))
            ph = prog(t, GOLD_T + 0.4 + n * 0.12, GOLD_T + 1.1 + n * 0.12)
            if 0 < ph < 1:
                sparkle(c, x + 14, y - 14, 22 * math.sin(math.pi * ph), rot=ph * 90)
    pill_tag(c, 1000, 470, "QUARTZ", ICE, pop(t, TM.word("W4", "quartz"), 0.4), 26)
    pill_tag(c, 1380, 700, "GOLD", YELLOW, pop(t, GOLD_T + 0.3, 0.4), 26)


# ---------------------------------------------------------------- Naica cave
BEAMS = [(-120, 820, 1500, 70, -22), (260, 1100, 1300, 62, -48), (1950, 760, 1400, 76, 200), (1700, 1150, 1150, 58, 235),
         (600, -100, 900, 50, 62), (1300, -80, 900, 54, 118), (-80, 520, 900, 48, -6)]


def draw_cave(c, t):
    lights = 0.55 + 0.45 * _flicker(t)
    c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.7, [(70, 50, 100), (30, 20, 50), (12, 8, 24)], [0, 0.5, 1])))
    for (cx, cy, rr, cc) in [(-60, 300, [420, 380, 460, 400, 440, 420, 380, 450], (24, 16, 40)),
                             (W + 60, 400, [460, 420, 400, 480, 430, 400, 440, 470], (24, 16, 40)),
                             (W / 2, H + 220, [420, 300, 330, 320, 300, 320, 340, 300], (34, 22, 54))]:
        c.drawPath(blob_path(cx, cy, rr, 0.1), fill(cc))
    grow = lerp(0.12, 1.0, smooth(prog(t, *GROWTH)))
    for n, (x, y, L, w, ang) in enumerate(BEAMS):
        g = clamp(grow * (1.08 - 0.04 * n))
        prism(c, x, y, L * g, w * (0.6 + 0.4 * g), ang, (236, 236, 226), 245, tip=0.7, glow_a=40)
    # flooded with warm mineral water until it is pumped out
    wl = lerp(-60, H + 80, in_out(prog(t, *DRAIN)))
    if wl < H + 60:
        water = skia.Path()
        water.moveTo(0, wl)
        for x in range(0, W + 40, 40):
            water.lineTo(x, wl + 10 * math.sin(x / 90 + t * 2))
        water.lineTo(W, H)
        water.lineTo(0, H)
        water.close()
        c.drawPath(water, fill((40, 150, 190), 120))
        for k in range(5):  # caustic shimmer
            x = (k * 420 + t * 40) % (W + 400) - 200
            c.drawPath(poly([(x, max(wl, 0)), (x + 60, max(wl, 0)), (x + 260, H), (x + 160, H)]), blur(fill(WHITE, 18), 14))
    # darkness, then work lights flick on
    c.drawPaint(fill(DARK, 255 * (1 - lights) * 0.7))
    glow(c, 960, 620, 520, (255, 240, 200), 60 * _flicker(t))
    if t > LIGHTS:
        hx, hy = 940, 596
        c.drawCircle(hx, hy - 52, 9, fill((255, 210, 120)))
        c.drawRRect(rrect(hx - 9, hy - 42, 18, 34, 8), fill(ORANGE))
        c.drawLine(hx - 4, hy - 10, hx - 5, hy, stroke(INK, 5))
        c.drawLine(hx + 4, hy - 10, hx + 5, hy, stroke(INK, 5))
    f = prog(t, *BIRD_FLY)
    if f > 0:
        bx = lerp(-80, 1010, out_cubic(f))
        by = lerp(260, 588, smooth(f)) - 120 * math.sin(math.pi * f)
        bird(c, bx, by, 24, t, look=(0.6, -0.6), wing=abs(math.sin(t * 22)) * (1 - smooth(prog(f, 0.85, 1.0))))
    # time-lapse while flooded
    ta = smooth(prog(t, GROWTH[0], GROWTH[0] + 0.4)) * (1 - smooth(prog(t, DRAIN[0], DRAIN[0] + 0.3)))
    if ta > 0.01:
        cx, cy = 960, 170
        c.saveLayerAlpha(None, int(255 * ta))
        c.drawCircle(cx, cy, 52, fill(WHITE))
        c.drawCircle(cx, cy, 52, stroke(INK, 6))
        a1 = (t - GROWTH[0]) * 14
        c.drawLine(cx, cy, cx + 34 * math.sin(a1), cy - 34 * math.cos(a1), stroke(INK, 5))
        c.drawLine(cx, cy, cx + 22 * math.sin(a1 / 12), cy - 22 * math.cos(a1 / 12), stroke(INK, 6))
        c.restore()
        caption(c, "HUNDREDS OF THOUSANDS OF YEARS", 960, 290, ICE, 28, 255 * ta)
    g = smooth(prog(t, SCALE_T, SCALE_T + 0.9))
    if g > 0:
        x0, y1 = 1700, 860
        y0 = lerp(y1, 180, g)
        c.drawLine(x0, y0, x0, y1, stroke(WHITE, 5))
        c.drawLine(x0 - 20, y0, x0 + 20, y0, stroke(WHITE, 5))
        c.drawLine(x0 - 20, y1, x0 + 20, y1, stroke(WHITE, 5))
        text(c, "12 m", x0 + 30, (y0 + y1) / 2 + 14, 44, WHITE, 255 * g, 800, "left")
    caption(c, "NAICA, MEXICO  ·  CAVE OF THE CRYSTALS", W / 2, 1010, ICE, 30, 255 * smooth(prog(t, LIGHTS + 0.4, LIGHTS + 0.8)))


def _flicker(t):
    if t < LIGHTS:
        return 0.0
    u = t - LIGHTS
    if u < 0.5:
        return [1, 0.2, 0.9, 0.1, 1][int(u / 0.1)]
    return 1.0


# ---------------------------------------------------------------- compose
def draw_frame(c, t):
    c.clear(col(NAVY))
    if t < BEAKER[1]:
        title_backdrop(c, t, CYAN)
    scenes = [(BEAKER, FLAT[1], draw_beaker), (FLAT, VEINS[1], draw_flat), (VEINS, CAVE[1], draw_veins), (CAVE, DURATION + 1, draw_cave)]
    for (t0, t1), t_end, fn in scenes:
        if t0 <= t < t_end:
            a = smooth(prog(t, t0, t1))
            if a < 1:
                c.saveLayerAlpha(None, int(255 * a))
            fn(c, t)
            if a < 1:
                c.restore()
    title_sequence(c, t, 2, "WATER", CYAN, icon_drop, 0.3, T_DOCK)
    vignette(c)
    chapter_fade(c, t, DURATION)


def sfx_events():
    ev = [(0.3, "whoosh_soft", 0.6), (0.4, "pop", 0.8), (0.55, "swell_soft", 0.6), (T_DOCK, "whoosh_soft", 0.5)]
    ev += [(DROP_T + i * 0.25 + 0.45, "bubble", 0.7) for i in range(3)]
    ev += [(DROP_T + 0.8, "pop", 0.5), (BEHIND_T, "slide", 0.6), (BEHIND_T + 1.75, "shimmer", 0.6), (BEHIND_T + 1.8, "pop", 0.5)]
    ev += [(FLAT[0], "whoosh", 0.6), (SHRINK[0] + 1, "shimmer", 0.4), (SALT_T, "pop", 0.5), (GYP_T, "shimmer", 0.6), (GYP_T + 0.2, "pop", 0.5)]
    ev += [(VEINS[0], "whoosh", 0.6), (VEINS[0] + 0.3, "rumble", 0.6), (FLOW_T, "bubble", 0.6), (FLOW_T + 0.9, "bubble", 0.5),
           (DEPOSIT[0] + 0.3, "shimmer", 0.6), (TM.word("W4", "quartz"), "pop", 0.5), (GOLD_T, "shine", 0.8), (GOLD_T + 0.3, "pop", 0.5)]
    ev += [(CAVE[0], "whoosh_long", 0.7), (GROWTH[0], "bubble", 0.5), (GROWTH[0] + 0.3, "ticks", 0.4), (GROWTH[0] + 3, "shimmer", 0.4),
           (DRAIN[0], "whoosh_long", 0.6), (LIGHTS, "flicker", 1.0), (LIGHTS + 0.5, "swell_soft", 0.8), (BIRD_FLY[1], "pop", 0.5),
           (SCALE_T, "riser", 0.6), (SCALE_T + 0.9, "chime", 0.7)]
    return ev


MUSIC = dict(
    chords=[(0.0, 50, (0, 7, 12, 14, 16)), (8.4, 55, (0, 7, 12, 14, 19)), (16.6, 52, (0, 7, 12, 15, 19)),
            (22.0, 48, (0, 7, 12, 16, 19)), (27.0, 45, (0, 7, 12, 15, 19)), (35.2, 53, (0, 7, 11, 16, 19))],
    plucks=[(3.4, 16.4), (17.2, 26.8), (35.4, DURATION)], bpm=96, rises=[(DEPOSIT[0], DEPOSIT[1])],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
