"""Part 2: Recipe 1, FIRE. Magma, cooling, slow crystals vs fast glass.

  python3 render.py part2 [--still 5,12,20]
"""
import math

import numpy as np

from common import *  # noqa: F401,F403

PART = "part2"
VO = {"F1": 0.8, "F2": 3.6, "F3": 11.6, "F4": 17.2, "F5": 26.6, "F6": 33.5}
DURATION = 36.5
TM = Timing(PART, VO)

T_DOCK = 2.9
CRUST = (3.0, 3.6)          # crossfade title -> crust
LENS_T = TM.word("F2", "soup") - 0.2
CAP_T = TM.word("F2", "too fast")
DIVE = (11.0, 12.0)         # zoom into the lens
COOL = (12.2, 15.2)         # magma cools
LINK = (TM.word("F3", "link") - 0.4, TM.word("F3", "link") + 1.0)
SPLIT = (16.7, 17.5)
GROW = (17.9, 23.8)
QUARTZ_T, FELD_T = TM.word("F4", "quartz"), TM.word("F4", "feldspar")
RIGHT_ON = 26.2
LAVA = (27.0, TM.word("F5", "ocean") + 0.1)
HIT = LAVA[1]
OBS_T = TM.word("F5", "freeze")
GLASS_T = VO["F6"]
BIRD_T = VO["F6"] - 0.4

LENS = (1430, 690, 280)
CHAMBER = (760, 780)
_rng = np.random.default_rng(12)
HOT = [dict(ax=_rng.uniform(140, 200), ay=_rng.uniform(120, 190), fx=_rng.uniform(1.6, 2.6), fy=_rng.uniform(1.4, 2.4),
            px=_rng.uniform(0, 6.28), py=_rng.uniform(0, 6.28), r=_rng.uniform(30, 40), rgb=SI if i % 3 == 0 else OX)
       for i in range(11)]


# ---------------------------------------------------------------- crust cross-section
def draw_crust(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, 220), [(18, 16, 50), (40, 28, 86)])))
    Stars(90, 4).draw(c, t, 0.8)
    c.drawPath(poly([(1050, 230), (1220, 90), (1290, 90), (1470, 230)]), fill((70, 52, 120)))
    c.drawPath(poly([(1220, 90), (1290, 90), (1275, 110), (1235, 110)]), fill(ORANGE))
    for k in range(3):  # smoke puffs from the volcano
        ph = (t * 0.25 + k / 3) % 1
        c.drawCircle(1255 + 30 * ph, 80 - 160 * ph, 18 + 40 * ph, fill((150, 130, 190), 120 * (1 - ph)))
    for i, (tx, h) in enumerate([(1560, 50), (1620, 66), (1690, 44), (1760, 60), (1830, 48)]):
        c.drawCircle(tx, 236 - h * 0.75, h * 0.42, fill(mix(MINT, (40, 140, 110), (i % 3) / 3)))
    for k, (y, cc) in enumerate([(220, (92, 74, 140)), (330, (78, 62, 128)), (470, (64, 50, 112)), (640, (52, 40, 96)), (830, (42, 32, 82))]):
        wavy_band(c, y, 1080, cc, k + 1, amp=14 + k * 4)
    rng = np.random.default_rng(3)
    for _ in range(160):
        c.drawCircle(rng.uniform(0, W), rng.uniform(250, 1080), rng.uniform(2, 6), fill(WHITE, 18))
    conduit = skia.Path()
    conduit.moveTo(1240, 105)
    conduit.cubicTo(1230, 350, 900, 450, 820, 640)
    conduit.lineTo(900, 660)
    conduit.cubicTo(980, 480, 1270, 380, 1270, 105)
    conduit.close()
    c.drawPath(conduit, fill(lerp_c(ORANGE, YELLOW, 0.5 + 0.5 * math.sin(t * 3))))
    cx, cy = CHAMBER
    pulse = 1 + 0.025 * math.sin(t * 2.4)
    glow(c, cx, cy, 520 * pulse, ORANGE, 140 + 30 * math.sin(t * 2.4))
    radii = [r * pulse + 8 * math.sin(t * 1.7 + i) for i, r in enumerate([300, 280, 230, 210, 250, 300, 330, 310, 260, 230, 250, 290])]
    chamber = blob_path(cx, cy, radii, 0.3)
    c.drawPath(chamber, shaded(radial((cx - 40, cy - 40), 360, [lighten(YELLOW, 0.4), YELLOW, ORANGE, (220, 70, 40)], [0, 0.3, 0.7, 1])))
    c.drawPath(chamber, stroke(lighten(YELLOW, 0.5), 5, 180))
    for i in range(7):  # rising bubbles
        ph = (t * 0.35 + i / 7) % 1
        bx = cx - 180 + i * 60 + 12 * math.sin(t * 2 + i)
        by = cy + 170 - 330 * ph
        c.drawCircle(bx, by, 8 + 10 * ph, stroke(lighten(YELLOW, 0.6), 4, 200 * math.sin(math.pi * ph)))
    # callout lens
    k = pop(t, LENS_T, 0.6)
    if k > 0:
        lx, ly, lr = LENS
        c.drawPath(poly([(cx + 90, cy - 60), (lx - lr * 0.75 * k, ly - lr * 0.66 * k), (lx - lr * 0.75 * k, ly + lr * 0.66 * k), (cx + 90, cy + 60)]), fill(YELLOW, 40 * k))
        c.drawCircle(cx + 90, cy, 64, stroke(WHITE, 5, 220 * min(1, k)))
        draw_lens(c, t, lx, ly, lr * k)
        caption(c, "TOO HOT TO HOLD HANDS", lx, ly + lr + 70, YELLOW, 30, 255 * smooth(prog(t, CAP_T, CAP_T + 0.3)))


def lerp_c(a, b, k):
    return mix(a, b, k)


def hot_atom_pos(a, tau, cx, cy, s=1.0):
    x = cx + a["ax"] * s * math.sin(a["fx"] * tau + a["px"])
    y = cy + a["ay"] * s * math.sin(a["fy"] * tau + a["py"])
    vx = a["fx"] * math.cos(a["fx"] * tau + a["px"])
    vy = a["fy"] * math.cos(a["fy"] * tau + a["py"])
    return x, y, vx, vy


def draw_lens(c, t, lx, ly, lr):
    if lr < 2:
        return
    soft_shadow(c, circle_path(lx, ly, lr), 14, 22, 26, 140)
    c.save()
    c.clipPath(circle_path(lx, ly, lr), doAntiAlias=True)
    c.drawPaint(shaded(radial((lx - 60, ly - 80), lr * 1.4, [(255, 190, 90), (240, 110, 50), (170, 50, 40)], [0, 0.6, 1])))
    s = lr / LENS[2]
    for a in HOT:
        x, y, vx, vy = hot_atom_pos(a, t * 1.6, lx, ly, s)
        streak_atom(c, x, y, a["r"] * s, a["rgb"], vx, vy)
    c.restore()
    c.drawCircle(lx, ly, lr, stroke(WHITE, 8, 240))


# ---------------------------------------------------------------- cooling: atoms slow and link up
GRID = [(i, j) for j in range(3) for i in range(5)]
COOL_ATOMS = [dict(HOT[n % len(HOT)], ax=HOT[n % len(HOT)]["ax"] * 3.2, ay=HOT[n % len(HOT)]["ay"] * 2.2,
                   px=HOT[n % len(HOT)]["px"] + n, rgb=SI if (i + j) % 2 == 0 else OX, tgt=(960 + (i - 2) * 160, 560 + (j - 1) * 160))
              for n, (i, j) in enumerate(GRID)]


def cool_tau(t):
    a, b = COOL
    if t < a:
        return t
    if t < b:
        u = t - a
        return a + u - 0.9 * u * u / (2 * (b - a))
    return a + (b - a) * 0.55 + 0.1 * (t - b)


def draw_cooling(c, t):
    cool = smooth(prog(t, *COOL))
    top = mix((255, 170, 80), (46, 34, 92), cool)
    bot = mix((200, 70, 40), (24, 18, 56), cool)
    c.drawPaint(shaded(linear((0, 0), (0, H), [top, bot])))
    glow(c, W / 2, H / 2, 800, mix(YELLOW, VIOLET, cool), 90)
    tau = cool_tau(t) * 1.6
    link = in_out(prog(t, *LINK))
    pos = []
    for a in COOL_ATOMS:
        x, y, vx, vy = hot_atom_pos(a, tau, W / 2, 560)
        tx, ty = a["tgt"]
        pos.append((lerp(x, tx, link), lerp(y, ty, link), vx, vy))
    if link > 0:
        bonds = skia.Path()
        for n, (i, j) in enumerate(GRID):
            for di, dj in ((1, 0), (0, 1)):
                if (i + di, j + dj) in GRID:
                    m = GRID.index((i + di, j + dj))
                    bonds.moveTo(pos[n][0], pos[n][1])
                    bonds.lineTo(pos[m][0], pos[m][1])
        c.drawPath(bonds, stroke(ICE, 10, 200 * smooth(prog(t, LINK[0] + 0.6, LINK[1]))))
    for a, (x, y, vx, vy) in zip(COOL_ATOMS, pos):
        r = a["r"] * 1.5
        if cool < 0.7:
            c.saveLayerAlpha(None, int(255 * (1 - cool / 0.7)))
            streak_atom(c, x, y, r, a["rgb"], vx, vy, worried=True)
            c.restore()
        atom(c, x, y, r, a["rgb"], t, 255 * min(1, cool / 0.7) if cool < 0.7 else 255, look=(0, 0))
        if link > 0.98:
            c.drawCircle(x, y, r * 1.25, stroke(WHITE, 3, 90 * math.sin(math.pi * prog(t, LINK[1] - 0.3, LINK[1] + 0.6))))
    # thermometer
    tx, ty = 170, 300
    c.drawRRect(rrect(tx - 26, ty, 52, 420, 26), fill(WHITE, 230))
    c.drawCircle(tx, ty + 450, 52, fill(WHITE, 230))
    level = lerp(0.92, 0.35, cool)
    tc = mix((255, 80, 60), CYAN, cool)
    c.drawRRect(rrect(tx - 14, ty + 420 * (1 - level), 28, 420 * level + 20, 14), fill(tc))
    c.drawCircle(tx, ty + 450, 38, fill(tc))
    text(c, f"{int(lerp(1200, 700, cool)) // 10 * 10} °C", tx + 60, ty + 420 * (1 - level) + 12, 36, WHITE, 255, 800, "left")


# ---------------------------------------------------------------- slow vs fast
def draw_split(c, t):
    k = in_out(prog(t, *SPLIT))
    lw = W / 2
    c.save()
    c.translate(-lw * (1 - k), 0)
    c.clipRect(skia.Rect.MakeXYWH(0, 0, lw, H))
    draw_slow(c, t)
    dim = 0.45 * smooth(prog(t, RIGHT_ON, RIGHT_ON + 0.6))
    if dim:
        c.drawPaint(fill(DARK, 255 * dim))
    c.restore()
    c.save()
    c.translate(lw * (1 - k), 0)
    c.clipRect(skia.Rect.MakeXYWH(lw, 0, lw, H))
    draw_fast(c, t)
    dim = 0.55 * (1 - smooth(prog(t, RIGHT_ON, RIGHT_ON + 0.6)))
    if dim:
        c.drawPaint(fill(DARK, 255 * dim))
    c.restore()
    c.drawLine(lw, 0, lw, H, stroke(WHITE, 6, 230 * k))


CRYSTALS = [(330, 880, 330, 46, -100), (430, 890, 420, 56, -82), (540, 885, 300, 42, -64),
            (250, 900, 220, 36, -122), (620, 900, 210, 34, -48), (480, 900, 180, 30, -95)]


def draw_slow(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(48, 30, 80), (26, 18, 52)])))
    glow(c, 480, 760, 600, ORANGE, 40 + 30 * (1 - smooth(prog(t, GROW[0], GROW[1]))))
    wavy_band(c, 860, 1080, (40, 28, 72), 9, 20)
    for n, (x, y, L, w, ang) in enumerate(CRYSTALS):
        g = out_cubic(prog(t, GROW[0] + n * 0.55, GROW[0] + n * 0.55 + 2.6))
        if g > 0.02:
            prism(c, x, y, L * g, w * (0.5 + 0.5 * g), ang, ICE, glow_a=50 * g)
    for n, (x, y, s, rot) in enumerate([(160, 930, 70, -12), (740, 930, 80, 14), (690, 980, 50, -6)]):
        g = pop(t, FELD_T - 0.3 + n * 0.15, 0.5)
        if g <= 0:
            continue
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.scale(g, g)
        c.drawPath(poly([(-s, -s * 0.5), (s * 0.5, -s * 0.8), (s, -s * 0.2), (s * 0.4, s * 0.6), (-s * 0.9, s * 0.5)]), fill(lighten(PINK, 0.25)))
        c.drawPath(poly([(-s, -s * 0.5), (s * 0.5, -s * 0.8), (s * 0.2, -s * 0.1), (-s * 0.8, -s * 0.05)]), fill(lighten(PINK, 0.55)))
        c.restore()
    for n, (x, y, s) in enumerate([(380, 420, 30), (560, 520, 22), (250, 600, 18)]):
        ph = (t * 0.6 + n * 0.33) % 1
        if t > GROW[0] + 2:
            sparkle(c, x, y, s * math.sin(math.pi * ph), rot=ph * 90)
    pill_tag(c, 430, 430, "QUARTZ", ICE, pop(t, QUARTZ_T, 0.4), 26)
    pill_tag(c, 740, 820, "FELDSPAR", lighten(PINK, 0.3), pop(t, FELD_T, 0.4), 26)
    # time-lapse clock
    cx, cy = 480, 260
    c.drawCircle(cx, cy, 70, fill(WHITE))
    c.drawCircle(cx, cy, 70, stroke(INK, 8))
    for k in range(12):
        a = k / 12 * 6.28
        c.drawLine(cx + 52 * math.cos(a), cy + 52 * math.sin(a), cx + 60 * math.cos(a), cy + 60 * math.sin(a), stroke(INK, 4))
    spin = max(0.0, min(t, 25.8) - SPLIT[1])
    a1, a2 = spin * 12 - 1.0, spin * 1.0 + 0.6
    c.drawLine(cx, cy, cx + 44 * math.sin(a1), cy - 44 * math.cos(a1), stroke(INK, 5))
    c.drawLine(cx, cy, cx + 30 * math.sin(a2), cy - 30 * math.cos(a2), stroke(INK, 7))
    caption(c, "SLOW  ·  THOUSANDS OF YEARS", 480, 420 - 60, ICE, 30, 255 * smooth(prog(t, SPLIT[1], SPLIT[1] + 0.4)))


STEAM = [(1330 + (n % 4) * 45, 640, 50 + (n * 17) % 40, HIT + n * 0.22) for n in range(16)]


def draw_fast(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(20, 18, 56), (60, 40, 110)])))
    Stars(60, 8).draw(c, t, 0.7)
    sea = skia.Path()
    sea.moveTo(W / 2, 640)
    for x in range(int(W / 2), W + 30, 30):
        sea.lineTo(x, 640 + 14 * math.sin(x / 70 + t * 1.5))
    sea.lineTo(W, H)
    sea.lineTo(W / 2, H)
    sea.close()
    c.drawPath(sea, shaded(linear((0, 620), (0, H), [CYAN, (30, 70, 150)])))
    c.drawPath(poly([(W / 2, 430), (1120, 460), (1250, 640), (1250, H), (W / 2, H)]), shaded(linear((0, 430), (0, H), [(84, 62, 128), (44, 32, 80)])))
    front = lerp(W / 2, 1340, in_cubic(prog(t, *LAVA)) * 0.4 + smooth(prog(t, *LAVA)) * 0.6)
    if front > W / 2 + 1:
        lava = skia.Path()
        lava.moveTo(W / 2, 470)
        lava.cubicTo(1150, 470, 1260, 560, 1330, 690)
        lava.lineTo(1260, 720)
        lava.cubicTo(1190, 620, 1100, 600, W / 2, 620)
        lava.close()
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(0, 0, front, H))
        hot = 1 - 0.5 * smooth(prog(t, HIT, HIT + 3))
        glow(c, min(front, 1300), 640, 220, ORANGE, 170 * hot)
        c.drawPath(lava, shaded(linear((W / 2, 0), (1330, 0), [YELLOW, ORANGE, mix((230, 70, 40), (60, 40, 70), 1 - hot)])))
        c.restore()
    for (x, y, r, t0) in STEAM:
        k = prog(t, t0, t0 + 2.2)
        if 0 < k < 1:
            c.drawCircle(x + 30 * k, y - 260 * k, r * out_cubic(min(1, k * 2.5)), fill(WHITE, 170 * (1 - k)))
    g = pop(t, OBS_T, 0.5)
    if g > 0:
        c.save()
        c.translate(1650, 885)
        c.scale(g, g)
        c.translate(-1650, -885)
        ob = poly([(1500, 930), (1580, 800), (1720, 780), (1800, 860), (1760, 960), (1600, 990)])
        soft_shadow(c, ob, 12, 18, 16, 120)
        c.drawPath(ob, shaded(linear((1500, 780), (1800, 990), [(70, 62, 100), (14, 12, 26)])))
        c.drawPath(poly([(1580, 800), (1720, 780), (1670, 860), (1560, 880)]), fill((110, 100, 150), 160))
        c.drawPath(poly([(1600, 815), (1690, 803), (1650, 830)]), fill(WHITE, 200))
        c.drawPath(ob, stroke((150, 140, 200), 3, 160))
        c.restore()
        gl = prog(t, GLASS_T + 0.2, GLASS_T + 1.0)
        if 0 < gl < 1:
            sparkle(c, 1705, 795, 34 * math.sin(math.pi * gl), rot=gl * 90)
    caption(c, "FAST  ·  SECONDS", 1440, 260, ORANGE, 30, 255 * smooth(prog(t, RIGHT_ON + 0.3, RIGHT_ON + 0.7)))
    ga = smooth(prog(t, GLASS_T, GLASS_T + 0.3))
    if ga > 0:
        caption(c, "= GLASS, NO CRYSTALS", 1650, 1050, WHITE, 26, 255 * ga)
    b = pop(t, BIRD_T, 0.5)
    if b > 0:
        c.save()
        c.translate(1300, 1020)
        c.scale(b, b)
        bird(c, 0, 0, 64, t, look=(1, 0.2), tilt=8 * math.sin(math.pi * prog(t, GLASS_T, GLASS_T + 1)))
        c.restore()
        bubble_q(c, 1390, 800, pop(t, GLASS_T + 0.2, 0.4))


# ---------------------------------------------------------------- compose
def draw_frame(c, t):
    c.clear(col(NAVY))
    if t < CRUST[1]:
        title_backdrop(c, t, ORANGE)
    if t >= CRUST[0] and t < DIVE[1] + 0.2:
        a = smooth(prog(t, *CRUST))
        c.saveLayerAlpha(None, int(255 * a))
        z = lerp(1.4, 1.0, in_out(prog(t, CRUST[0], 6.0)))
        fx, fy = lerp(1250, 960, in_out(prog(t, CRUST[0], 6.0))), lerp(380, 540, in_out(prog(t, CRUST[0], 6.0)))
        dz = in_cubic(prog(t, *DIVE))
        z, fx, fy = lerp(z, 4.6, dz), lerp(fx, LENS[0], dz), lerp(fy, LENS[1], dz)
        cam(c, z, fx, fy)
        draw_crust(c, t)
        c.restore()
        c.restore()
    if DIVE[1] - 0.25 <= t < SPLIT[1]:
        a = smooth(prog(t, DIVE[1] - 0.25, DIVE[1] + 0.2))
        c.saveLayerAlpha(None, int(255 * a))
        draw_cooling(c, t)
        c.restore()
    if t >= SPLIT[0]:
        draw_split(c, t)
    title_sequence(c, t, 1, "FIRE", ORANGE, icon_flame, 0.3, T_DOCK)
    vignette(c)
    chapter_fade(c, t, DURATION)


def sfx_events():
    return [(0.3, "whoosh_soft", 0.6), (0.4, "pop", 0.8), (0.55, "boom", 0.5), (T_DOCK, "whoosh_soft", 0.5),
            (3.4, "rumble", 0.9), (LENS_T, "pop", 0.7), (CAP_T, "blip", 0.5), (7.8, "rumble", 0.6),
            (DIVE[0] + 0.1, "riser", 0.7), (DIVE[1] - 0.1, "whoosh", 0.6),
            (COOL[0] + 0.5, "swell_soft", 0.7), (LINK[0] + 0.5, "click", 0.8), (LINK[0] + 0.7, "click", 0.6),
            (LINK[0] + 0.9, "click", 0.6), (LINK[1], "chime", 0.6),
            (SPLIT[0], "whoosh_long", 0.8), (SPLIT[1] + 0.2, "ticks", 0.6), (SPLIT[1] + 1.8, "ticks", 0.5),
            (GROW[0] + 0.5, "shimmer", 0.6), (GROW[0] + 2.5, "shimmer", 0.5), (QUARTZ_T, "pop", 0.5), (FELD_T, "pop", 0.5),
            (RIGHT_ON, "whoosh_soft", 0.5), (LAVA[0], "rumble", 0.7), (HIT, "sizzle", 1.0), (HIT + 0.8, "sizzle", 0.7),
            (OBS_T, "tink", 0.9), (GLASS_T + 0.2, "chime", 0.6), (BIRD_T, "pop", 0.6), (GLASS_T + 0.2, "pop", 0.5)]


MUSIC = dict(
    chords=[(0.0, 52, (0, 7, 12, 15, 19)), (6.0, 48, (0, 7, 12, 16, 19)), (11.5, 50, (0, 7, 12, 14, 17)),
            (17.0, 55, (0, 7, 11, 16, 19)), (22.0, 48, (0, 7, 12, 16, 21)), (26.4, 50, (0, 7, 12, 15, 19)),
            (31.0, 52, (0, 7, 12, 15, 19))],
    plucks=[(12.0, 26.0), (29.0, DURATION)], bpm=96, rises=[(GROW[0], GROW[0] + 3.5)],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
