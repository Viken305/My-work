"""Part 1, the hook: night on Rodrigues; a dull thud like cannon fire; the camera pulls back 4,800 km across the
Indian Ocean to Krakatoa; push in; the island in section; silence; BOOM; ringing ears; title.

  python3 render.py part1 [--still 3,12,17]
"""
import math

import numpy as np
import skia

from captions import Captions, VoiceEnvelope
from cyan import *  # noqa: F401,F403
from frames import KRAKATOA, RODRIGUES, ash_column, island_path
from timing import Timing, schedule

PART = "part1"
SAMPLES = 3
VO, _end = schedule(PART, first=1.0, gap=0.5, extra={"H3": 0.5})
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)

YEAR_T = TM.word("H1", "eighteen") - 0.1
GUNS_T = TM.word("H1", "distant") - 0.1          # the sound arrives on Rodrigues
PULL_T = TM.word("H2", "the sound") - 0.1         # pull back across the ocean
FULL_T = TM.word("H2", "away.", end=True) + 0.1
PUSH_T = VO["H3"] - 0.1                            # push in on Krakatoa
SECTION_T = TM.end("H3") + 0.35                    # cut to the island in section
BOOM_T = SECTION_T + 1.7
TITLE_T = BOOM_T + 1.9
DURATION = TITLE_T + 3.6

CAPS = Captions(TM, ENV, sound={"heard", "cannon", "sound", "here."}, anchors={"H3": (W / 2, 1380)})
FULL_VIEW = (85.0, -13.5, 1060.0)                  # lon, lat, R (px per radian) of the whole-ocean view
ROD_VIEW = (RODRIGUES[0], RODRIGUES[1], 62000.0)
KRAK_VIEW = (KRAKATOA[0], KRAKATOA[1], 60000.0)
ANG = 0.7505                                       # Krakatoa -> Rodrigues, radians (4,780 km)
ASH_DUST = Ash(2500, 31)


def in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def anchored(pt, sx, sy, R):
    """Camera centre (lon, lat) that puts geographic point pt at screen (sx, sy) at scale R (small-angle approx)."""
    return (pt[0] - math.degrees((sx - W / 2) / (R * math.cos(math.radians(pt[1])))),
            pt[1] + math.degrees((sy - 860) / R))


def view(t):
    """Map camera: lon, lat, R. Zooms run in log scale (constant felt speed); the point we leave (Rodrigues) or head
    for (Krakatoa) is pinned to a screen position that glides between its place in the two views."""
    full = Ortho(FULL_VIEW[0], FULL_VIEW[1], FULL_VIEW[2], W / 2, 860)
    if t < PULL_T:
        return ROD_VIEW[0], ROD_VIEW[1], ROD_VIEW[2] * (1 + 0.06 * prog(t, 0, PULL_T))
    if t < PUSH_T:
        a, b, u, pt, frm = ROD_VIEW, FULL_VIEW, in_out(prog(t, PULL_T, FULL_T)), RODRIGUES, False
    else:
        a, b, u, pt, frm = FULL_VIEW, KRAK_VIEW, in_out(prog(t, PUSH_T, SECTION_T)) ** 1.6, KRAKATOA, True
    R = math.exp(math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * u)
    fx, fy, _ = full(*pt)
    k = 1 - u if frm else u                       # 0 = centre of the screen, 1 = its place in the whole-ocean view
    lon, lat = anchored(pt, W / 2 + (fx - W / 2) * k, 860 + (fy - 860) * k, R)
    w = k ** 4                                    # near the wide view, hand over to the exact projection centre
    return lon + (FULL_VIEW[0] - lon) * w, lat + (FULL_VIEW[1] - lat) * w, R


def map_scene(c, t):
    lon, lat, R = view(t)
    proj = Ortho(lon, lat, R, W / 2, 860)
    paper(c)
    graticule(c, proj, 0.7, step=10 if R < 6000 else 1)
    zoomed = R > 6000
    engraved_land(c, land_path(proj, "indian_ocean"), hatch=6,
                  water_lines=(9, 19, 31, 46) if not zoomed else (14, 30, 50, 76, 110))
    kx, ky, _ = proj(*KRAKATOA)
    rx, ry, _ = proj(*RODRIGUES)
    # the wave arriving on Rodrigues: an arc of a ring centred 4,800 km away sweeps across the screen
    if GUNS_T - 0.6 < t < PULL_T + 1.0:
        d = math.hypot(rx - kx, ry - ky)
        r = d + (t - GUNS_T) * 900
        ring(c, kx, ky, r, SULFUR, 255 * (1 - smooth(prog(t, GUNS_T + 1.2, PULL_T + 1.0))), 3.4)
        for k in range(1, 4):
            ring(c, kx, ky, r - k * 160, SULFUR, 70 / k * (1 - prog(t, GUNS_T, PULL_T + 1)), 1.6, fringe=False, trail=0)
    # whole-ocean view: the rings and the measured distance
    full = smooth(prog(t, PULL_T, PULL_T + 1.2))
    if full > 0:
        for k, f in enumerate((0.38, 0.62, 0.84)):
            ring(c, kx, ky, R * ANG * f * (0.9 + 0.1 * full), SULFUR, (70 + k * 25) * full, 1.6, fringe=False, trail=0)
        ring(c, kx, ky, R * ANG, SULFUR, 255 * full, 3.0)
    u = prog(t, PULL_T, FULL_T)
    if u > 0:   # the distance line grows from Rodrigues back to Krakatoa, with a live count
        ex, ey = rx + (kx - rx) * out_cubic(u), ry + (ky - ry) * out_cubic(u)
        c.drawLine(rx, ry, ex, ey, paint(PAPER, 200, stroke=1.6))
        km = int(round(4800 * in_out(u) / 10) * 10)
        ka = smooth(prog(t, PULL_T, PULL_T + 0.4)) * (1 - smooth(prog(t, PUSH_T, PUSH_T + 0.3)))
        label(c, f"{km:,}", W / 2, 560, 170, "mono_bold", PAPER, 240 * ka, "center", 0.02)
        label(c, "KILOMETRES", W / 2, 630, 26, "mono", SULFUR, 240 * ka, "center", 0.4)
    a_k = smooth(prog(t, FULL_T - 0.6, FULL_T))
    if a_k > 0:
        pulse = 1 + 0.5 * math.sin(max(0, t - PUSH_T) * 9) * (t > PUSH_T)
        light(c, kx, ky, 90 * pulse, LAVA, 170 * a_k)
        pin(c, kx, ky, "KRAKATOA", "SUNDA STRAIT", a_k * 255 * (1 - prog(t, PUSH_T + 0.3, PUSH_T + 0.6)), side=-1)
    pin(c, rx, ry, "RODRIGUES", "INDIAN OCEAN", 255 * smooth(prog(t, 0.6, 1.6)) * (1 - prog(t, PUSH_T, PUSH_T + 0.3)),
        rgb=SULFUR if t > GUNS_T else PAPER, side=1)
    q = smooth(prog(t, GUNS_T + 0.3, GUNS_T + 0.9)) * (1 - smooth(prog(t, PULL_T, PULL_T + 0.6)))
    label(c, "“the distant roar", rx + 28, ry + 100, 34, "serif", PAPER, 230 * q)
    label(c, "of heavy guns”", rx + 40, ry + 142, 34, "serif", PAPER, 230 * q)
    # plate caption + the year
    fa = smooth(prog(t, 0.4, 1.2)) * (1 - smooth(prog(t, PUSH_T, PUSH_T + 0.4)))
    fig(c, 1, "THE INDIAN OCEAN, AUGUST 1883", 70, 300, fa * 255)
    ya = smooth(prog(t, YEAR_T, YEAR_T + 0.5)) * (1 - smooth(prog(t, PULL_T - 0.4, PULL_T + 0.2)))
    if ya > 0:
        label(c, "1883", W / 2, 560 - 20 * (1 - ya), 190, "mono_bold", PAPER, 235 * ya, "center", 0.04, sigma=6 * (1 - ya))


def section_scene(c, t):
    """The island in section, before and after the blast."""
    e = t - BOOM_T
    sea, vx, vy = 1040, 562, 885
    sx, sy = 0.0, 0.0
    if e > 0:   # camera shake
        k = 34 * math.exp(-e * 2.2)
        sx, sy = k * math.sin(t * 61), k * math.cos(t * 47)
    paper(c)
    c.save()
    c.translate(sx, sy)
    # before: magma breathing, a thin plume
    glow = 0.5 + 0.5 * math.sin(t * 5) if e < 0 else 1.0
    if e < 0:
        c.save()
        c.translate(vx, vy)
        c.scale(0.28, 0.32)
        c.translate(-vx, -vy)
        ash_column(c, vx, vy, t)
        c.restore()
    else:
        light(c, vx, vy - 120, 1000, LAVA, 130 * math.exp(-e * 0.4))
        for k, dl in enumerate((0.0, 0.18, 0.4, 0.7)):
            ee = e - dl
            if ee > 0:
                ring(c, vx, vy - 40, 120 + ee * 1250 * (1 - 0.25 * min(1, ee)), SULFUR, (255 - k * 45) * math.exp(-ee * 0.5),
                     3.6 - k * 0.5, fringe=k == 0)
        for k in range(46):   # debris streaks fly out and fall
            ang = math.radians(198 + k * 3.2 + math.sin(k * 7.3) * 5)
            sp = 500 + (k * 53) % 420
            r1 = 60 + sp * min(e, 2.5) * (1 - 0.18 * min(e, 2.5))
            r0 = max(40, r1 - 120 - sp * 0.15)
            fall = 120 * e * e
            x0, y0 = vx + math.cos(ang) * r0, vy - 60 + math.sin(ang) * r0 + fall * 0.5
            x1, y1 = vx + math.cos(ang) * r1, vy - 60 + math.sin(ang) * r1 + fall
            a = 255 * math.exp(-e * 0.7)
            pth = skia.Path()
            pth.moveTo(x0, y0)
            pth.lineTo(x1, y1)
            c.drawPath(pth, paint(SUN_O, 100 * a / 255, sigma=2, plus=True, stroke=2.2))
            c.drawCircle(x1, y1, 3 + k % 3, paint(HOT, a, plus=True))
        g = out_cubic(prog(e, 0, 2.2))
        c.save()
        c.translate(vx, vy)
        c.scale(0.4 + 0.75 * g, 0.4 + 0.75 * g)
        c.translate(-vx, -vy)
        ash_column(c, vx, vy - 40, t)
        c.restore()
        light(c, vx, vy - 10, 300, SUN_O, 230 * math.exp(-e * 0.6))
        light(c, vx, vy, 140, HOT, 255 * math.exp(-e * 1.2))
    c.drawRect(skia.Rect.MakeLTRB(-60, sea, W + 60, 1760), paint(mix(NIGHT, PRUSSIAN, 0.7), 240))
    for i, y in enumerate(range(sea + 6, 1760, 9)):
        wob = 3 * math.sin(t * 2 + i * 0.4) * (1 + 6 * math.exp(-max(e, 0) * 1.5) * (e > 0))
        c.drawLine(-60, y + wob, W + 60, y - wob, paint(PAPER, 40 - min(28, i * 0.4), stroke=1.0))
    c.drawLine(-60, sea, W + 60, sea, paint(PAPER, 210, stroke=2))
    isl = island_path()
    c.drawPath(isl, paint(mix(PRUSSIAN, PAPER, 0.1)))
    c.save()
    c.clipPath(isl, doAntiAlias=True)
    for i in range(-H, W + H, 7):
        c.drawLine(i, 0, i - H * 0.5, H, paint(PAPER, 46, stroke=1.0))
    for k in range(6):
        pth = skia.Path()
        pth.moveTo(-40, 1150 + k * 70)
        pth.cubicTo(300, 1090 + k * 75, 800, 1110 + k * 66, 1120, 1150 + k * 72)
        c.drawPath(pth, paint(PAPER, 80, stroke=1.2))
    conduit = skia.Path()
    conduit.moveTo(vx, vy - 10)
    conduit.cubicTo(vx + 20, 960, vx - 30, 1060, vx - 10, 1160)
    c.drawPath(conduit, paint(LAVA, 200 * glow, sigma=12, plus=True, stroke=40))
    c.drawPath(conduit, paint(SUN_O, 230 * glow, plus=True, stroke=10))
    c.drawOval(skia.Rect.MakeXYWH(vx - 170, 1130, 320, 90), paint(LAVA, 220 * glow, sigma=22, plus=True))
    c.restore()
    c.drawPath(isl, paint(PAPER, 230, stroke=1.8))
    label(c, "SEA LEVEL", 1040, sea - 14, 20, "mono", PAPER, 200, "right", 0.14)
    c.restore()
    # plate + the clock, before the blast
    pa = 255 * (1 - smooth(prog(e, -0.1, 0.0)))
    fig(c, 2, "SECTION THROUGH KRAKATOA", 70, 300, pa)
    if e < 0:
        k = smooth(prog(t, SECTION_T + 0.1, SECTION_T + 0.5))
        label(c, "27 AUGUST 1883", W / 2, 420, 30, "mono", PAPER, 220 * k, "center", 0.3)
        label(c, "10:02 AM", W / 2, 550, 120, "mono_bold", SULFUR, 255 * k, "center", 0.04)
    boom_word(c, t, e)
    if t > TITLE_T - 0.2:
        title(c, t)


def boom_word(c, t, e):
    """BOOM slams in, shakes, then blows apart into particles from the right."""
    if e < 0.03 or e > 2.2:
        return
    size = 250
    f = font("black", size)
    slam = 1 + 0.6 * (1 - spring(prog(e, 0.03, 0.33), 9, 13))
    by = 1420
    total = width("BOOM", "black", size)
    rng = np.random.default_rng(int(t * 30))
    c.save()
    c.translate(W / 2, by - size * 0.35)
    c.scale(slam, slam)
    c.translate(-W / 2, -(by - size * 0.35))
    x = W / 2 - total / 2
    for j, ch in enumerate("BOOM"):
        adv = f.measureText(ch)
        dis = clamp((e - 0.9 - (3 - j) * 0.12) / 0.5)          # dissolve, right letter first
        jit = 9 * math.exp(-e * 2)
        dx, dy = rng.normal(0, jit, 2)
        if dis < 1:
            c.save()
            c.translate(x + dx, by + dy)
            c.drawString(ch, 8, 14, f, paint((0, 0, 0), 170 * (1 - dis), sigma=16))
            c.drawString(ch, 0, 0, f, paint(SULFUR, 255 * (1 - dis) ** 1.5, sigma=6 * dis))
            c.restore()
        if dis > 0:
            pr = np.random.default_rng(j)
            n = 260
            px = x + pr.random(n) * adv
            py = by - pr.random(n) * size * 0.72
            vxs, vys = 380 + pr.random(n) * 520, -80 - pr.random(n) * 260
            tt = (e - 0.9 - (3 - j) * 0.12) * pr.uniform(0.6, 1.2, n)
            for i in range(n):
                if tt[i] <= 0:
                    continue
                al = 230 * clamp(1 - tt[i] / 1.1)
                c.drawCircle(px[i] + vxs[i] * tt[i], py[i] + vys[i] * tt[i] + 120 * tt[i] ** 2, 1.2 + 2.6 * (1 - clamp(tt[i])),
                             paint(SULFUR if i % 5 else HOT, al, plus=i % 5 == 0))
        x += adv
    c.restore()


def title(c, t):
    u = t - TITLE_T
    a = smooth(prog(u, -0.2, 0.4)) * (1 - smooth(prog(t, DURATION - 0.5, DURATION)))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(NIGHT, 150 * a))
    tr = 0.42 + (0.2 - 0.42) * out_cubic(prog(u, 0, 1.8))
    y = 880
    for i, ch in enumerate(["THE LOUDEST SOUND"]):
        k = smooth(prog(u, 0, 0.5))
        label(c, ch, W / 2, y + 18 * (1 - k), 74, "black", PAPER, 255 * a * k, "center", tracking=tr, sigma=10 * (1 - k))
    k2 = smooth(prog(u, 0.3, 0.9))
    label(c, "ever heard", W / 2, y + 150 + 18 * (1 - k2), 150, "serif_bold", SULFUR, 255 * a * k2, "center", sigma=10 * (1 - k2))
    q = out_cubic(prog(u, 0.3, 1.6))
    ring(c, W / 2, y + 60, 120 + 520 * q, SULFUR, 160 * (1 - q) * a, 2.2, fringe=False, trail=1)
    lk = out_cubic(prog(u, 0.2, 1.0))
    c.drawLine(W / 2 - 300 * lk, y + 40, W / 2 + 300 * lk, y + 40, paint(FADED, 180 * a, stroke=1.5))


def draw_frame(c, t):
    if t < SECTION_T:
        map_scene(c, t)
    else:
        section_scene(c, t)
    if t < 1.0:   # fade up from black
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((0, 0, 0), 255 * (1 - smooth(t / 1.0))))
    cut = prog(t, SECTION_T - 0.12, SECTION_T) * (1 - prog(t, SECTION_T, SECTION_T + 0.25))
    if cut > 0:   # the push ends in a flash of light into the section
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(HOT, 200 * cut, plus=True))
    if t < TITLE_T - 0.3:
        CAPS.draw(c, t)


def post_kw(t):
    e = t - BOOM_T
    if e < 0:
        return {}
    return dict(flash=0.9 * math.exp(-e * 9), split=1.2 * math.exp(-e * 2.5))


def sfx_events():
    ev = [(0.0, "ocean", 0.6), (9.0, "ocean", 0.5),
          (GUNS_T, "distant_guns", 1.0),
          (PULL_T + 0.2, "whoosh", 0.55),
          (PUSH_T, "whoosh", 0.7),
          (BOOM_T - 5.0, "rumble", 0.28),
          (SECTION_T, "low_hit", 0.2),
          (BOOM_T - 1.4, "tick", 0.8), (BOOM_T - 0.7, "tick", 0.9),
          (BOOM_T - 0.9, "suck", 0.9),
          (BOOM_T, "krakatoa", 0.95),
          (BOOM_T + 0.08, "deafen", 3.4),
          (TITLE_T, "title_hit", 0.55)]
    return ev


MUSIC = dict(beds=[(0.0, PULL_T + 1.5, "night", 0.8),
                   (PULL_T - 0.5, BOOM_T - 0.8, "cello", 0.85),
                   (BOOM_T + 1.4, DURATION, "aftermath", 1.0)])
