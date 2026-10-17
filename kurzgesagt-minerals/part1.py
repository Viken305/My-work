"""Part 1 (0:00-0:40): Scene 1 "Hook" + Scene 2 "What is a mineral?".

  python3 part1.py                 # full render -> out/part1.mp4
  python3 part1.py --still 2,7,15  # PNG stills to build/part1/stills for checking
  python3 part1.py --scale 0.5     # half-res quick preview
"""
import math, os, subprocess, sys
from multiprocessing import Pool

import numpy as np
import skia

from engine import *  # noqa: F401,F403 (drawing kit + palette)
import audio

PART = "part1"
OUT_DIR = os.path.join(HERE, "out")
BUILD = os.path.join(HERE, "build", PART)

# Narration start times (seconds). Durations come from build/part1/vo/durations.json.
VO = {"L1": 0.7, "L2": 3.9, "L3": 6.4, "L4": 8.8, "L5": 12.0, "L6": 15.2,
      "L7": 17.9, "L8": 23.1, "L9": 25.4, "L10": 28.6, "L11": 34.6}
DURATION = 40.0

# ---------------------------------------------------------------- scene 1a: kitchen
COUNTER_Y = 760
SHAKER = (1150, 690)          # pivot (centre of the salt shaker body)
KITCHEN_SPARKLES = [(0.9, 520, 300, 22), (1.3, 1132, 650, 18), (1.7, 848, 690, 16), (2.05, 690, 470, 20),
                    (2.4, 1565, 712, 17), (2.75, 1420, 640, 18), (3.05, 330, 520, 16), (3.35, 1176, 705, 20)]
POUR_T0, POUR_T1 = 4.15, 4.75   # shaker tips over
CAM_PUSH = (3.55, 4.55)
CAM_DIVE = (5.25, 6.05)
TO_PANELS = 5.85


def shaker_angle(t):
    return 138 * in_out(prog(t, POUR_T0, POUR_T1)) - 8 * math.sin(math.pi * prog(t, 5.4, 6.0))


def shaker_lift(t):
    return -70 * in_out(prog(t, POUR_T0, POUR_T1))


def _simulate_salt():
    """Salt cubes tumbling out of the shaker cap: simple gravity + bounce."""
    rng = np.random.default_rng(5)
    n, dt = 15, 1 / 600
    spawn = np.sort(rng.uniform(4.72, 5.45, n))
    out = []
    for i in range(n):
        th = math.radians(138)
        cap = (SHAKER[0] + 98 * math.sin(th), SHAKER[1] - 70 - 98 * math.cos(th))
        x, y = cap[0] + rng.uniform(-8, 8), cap[1] + rng.uniform(-4, 6)
        vx, vy = rng.uniform(-40, 170), rng.uniform(40, 140)
        ang, spin = rng.uniform(0, 90), rng.uniform(-500, 500)
        size = rng.uniform(5.5, 8.5)
        t, track, bounces = spawn[i], [], []
        while t < DURATION:
            track.append((t, x, y, ang))
            vy += 1500 * dt
            x += vx * dt
            y += vy * dt
            ang += spin * dt
            floor = COUNTER_Y - size
            if y > floor:
                y = floor
                if vy > 60:
                    bounces.append((t, min(1.0, vy / 600)))
                vy = -vy * 0.32
                vx *= 0.6
                spin *= 0.4
                if abs(vy) < 40:
                    vy, spin = 0.0, 0.0
                    ang = round(ang / 90) * 90 + 0  # settle flat
            if t > spawn[i] + 1.6:
                break
            t += dt
        out.append(dict(spawn=spawn[i], size=size, track=np.array(track), bounces=bounces))
    return out


SALT = _simulate_salt()
TARGET = min(range(len(SALT)), key=lambda i: abs(SALT[i]["track"][-1][1] - 1255))
TARGET_POS = (SALT[TARGET]["track"][-1][1], SALT[TARGET]["track"][-1][2])


def salt_state(s, t):
    tr = s["track"]
    if t < s["spawn"]:
        return None
    idx = min(int((t - s["spawn"]) * 600), len(tr) - 1)
    return tr[idx][1:]


def kitchen_camera(t):
    z = lerp(1.0, 1.08, smooth(prog(t, 0, CAM_PUSH[0])))
    fx, fy = lerp(960, 990, smooth(prog(t, 0, CAM_PUSH[0]))), 540
    p = in_out(prog(t, *CAM_PUSH))
    z, fx, fy = lerp(z, 2.3, p), lerp(fx, 1185, p), lerp(fy, 660, p)
    q = in_cubic(prog(t, *CAM_DIVE)) * 0.6 + in_out(prog(t, *CAM_DIVE)) * 0.4
    return lerp(z, 9.0, q), lerp(fx, TARGET_POS[0], q), lerp(fy, TARGET_POS[1] - 2, q)


def draw_kitchen(c, t):
    z, fx, fy = kitchen_camera(t)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-fx, -fy)
    # wall
    c.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, COUNTER_Y + 400), shaded(linear((0, -200), (0, COUNTER_Y), [(66, 46, 122), (40, 28, 88)])))
    # window with night sky
    wr = rrect(250, 160, 520, 450, 26)
    soft_shadow(c, wr, 10, 14, 16, 80)
    c.drawRRect(rrect(236, 146, 548, 478, 32), fill((120, 100, 170)))
    c.save()
    c.clipRRect(wr, doAntiAlias=True)
    c.drawRRect(wr, shaded(linear((0, 160), (0, 610), [(16, 18, 52), (54, 40, 120)])))
    rng = np.random.default_rng(2)
    for _ in range(40):
        sx, sy, sr = rng.uniform(250, 770), rng.uniform(160, 600), rng.uniform(0.8, 2.4)
        c.drawCircle(sx, sy, sr, fill(WHITE, 140 + 100 * math.sin(t * 1.5 + sx)))
    glow(c, 650, 270, 110, ICE, 60)
    moon = skia.Path()
    moon.addCircle(650, 270, 44)
    cut = skia.Path()
    cut.addCircle(672, 256, 40)
    c.drawPath(skia.Op(moon, cut, skia.PathOp.kDifference_PathOp), fill((250, 240, 210)))
    # far city skyline silhouette
    for i, (bx, bh) in enumerate([(250, 90), (310, 140), (380, 70), (430, 170), (510, 110), (570, 150), (640, 80), (700, 130)]):
        c.drawRect(skia.Rect.MakeXYWH(bx, 610 - bh, 62, bh), fill((30, 22, 70)))
        for wy in range(int(610 - bh + 14), 600, 26):
            if (wy + i * 7) % 3:
                c.drawRect(skia.Rect.MakeXYWH(bx + 12, wy, 8, 10), fill(YELLOW, 120))
    c.restore()
    c.drawRect(skia.Rect.MakeXYWH(504, 160, 12, 450), fill((120, 100, 170)))
    c.drawRect(skia.Rect.MakeXYWH(250, 380, 520, 12), fill((120, 100, 170)))
    # hanging lamp + light cone
    c.drawLine(1150, -400, 1150, 200, stroke((20, 14, 40), 4))
    cone = poly([(1110, 250), (1190, 250), (1420, COUNTER_Y), (880, COUNTER_Y)])
    c.drawPath(cone, blur(shaded(linear((0, 250), (0, COUNTER_Y), [(YELLOW, 70), (YELLOW, 10)])), 18))
    c.drawPath(poly([(1105, 195), (1195, 195), (1235, 255), (1065, 255)]), shaded(linear((1065, 0), (1235, 0), [(255, 150, 90), (200, 90, 70)])))
    glow(c, 1150, 262, 70, YELLOW, 200)
    c.drawCircle(1150, 258, 16, fill((255, 240, 200)))
    # counter
    c.drawRect(skia.Rect.MakeXYWH(-400, COUNTER_Y + 26, W + 800, 700), shaded(linear((0, COUNTER_Y), (0, H + 200), [(62, 46, 112), (30, 22, 66)])))
    for dx in range(-200, W + 400, 330):
        c.drawRRect(rrect(dx + 20, COUNTER_Y + 60, 290, 400, 18), stroke((86, 68, 140), 4))
        c.drawRRect(rrect(dx + 140, COUNTER_Y + 90, 50, 10, 5), fill((150, 130, 200)))
    c.drawRRect(rrect(-400, COUNTER_Y, W + 800, 30, 8), shaded(linear((0, COUNTER_Y), (0, COUNTER_Y + 30), [(150, 128, 205), (104, 86, 160)])))
    # plant
    leaf_rot = bob(t, 3, 4.0)
    for i, (ang, ln) in enumerate([(-50, 120), (-20, 150), (10, 135), (40, 115), (-80, 90), (70, 95)]):
        c.save()
        c.translate(430, 690)
        c.rotate(ang + leaf_rot * (1 if i % 2 else -1))
        c.drawOval(skia.Rect.MakeXYWH(-16, -ln, 32, ln), fill(mix(MINT, (40, 140, 110), (i % 3) / 3)))
        c.restore()
    c.drawPath(poly([(385, 680), (475, 680), (462, COUNTER_Y), (398, COUNTER_Y)]), shaded(linear((385, 0), (475, 0), [(255, 140, 110), (210, 90, 90)])))
    # mug
    c.drawRRect(rrect(800, 670, 90, 90, 14), shaded(linear((800, 0), (890, 0), [lighten(ORANGE, 0.2), darken(ORANGE, 0.15)])))
    c.drawCircle(898, 712, 22, stroke(darken(ORANGE, 0.1), 10))
    for k in range(3):
        sy = (t * 25 + k * 20) % 60
        c.drawLine(825 + k * 18, 650 - sy, 830 + k * 18, 630 - sy, stroke(WHITE, 5, 60 * (1 - sy / 60)))
    # pepper shaker (left of salt)
    c.drawRRect(rrect(1000, 640, 70, 120, 18), fill((60, 44, 70)))
    c.drawRRect(rrect(996, 612, 78, 34, 14), shaded(linear((996, 0), (1074, 0), [(220, 220, 235), (140, 140, 165)])))
    # sugar jar
    c.drawRRect(rrect(1360, 600, 120, 160, 22), fill(ICE, 50))
    c.drawRRect(rrect(1366, 660, 108, 96, 18), fill((250, 245, 255), 210))
    c.drawRRect(rrect(1350, 584, 140, 26, 10), fill(PINK))
    c.drawRRect(rrect(1360, 600, 120, 160, 22), stroke(ICE, 3, 140))
    # bowl
    bowl = skia.Path()
    bowl.moveTo(1490, 700)
    bowl.cubicTo(1500, 770, 1640, 770, 1650, 700)
    bowl.close()
    c.drawPath(bowl, shaded(linear((1490, 0), (1650, 0), [CYAN, darken(CYAN, 0.3)])))
    for k, (ax, col_) in enumerate([(1535, (255, 90, 90)), (1575, YELLOW), (1610, (255, 90, 90))]):
        c.drawCircle(ax, 690 - (k % 2) * 8, 24, fill(col_))
    # salt cubes on the counter
    for s in SALT:
        st = salt_state(s, t)
        if st is None:
            continue
        x, y, ang = st
        c.save()
        c.translate(x, y)
        c.rotate(ang)
        sz = s["size"]
        c.drawRRect(rrect(-sz, -sz, 2 * sz, 2 * sz, sz * 0.18), shaded(linear((-sz, -sz), (sz, sz), [WHITE, (200, 225, 245)])))
        c.drawRRect(rrect(-sz, -sz, 2 * sz, 2 * sz, sz * 0.18), stroke(ICE, 0.8, 200))
        c.restore()
        if s is SALT[TARGET] and t > 5.3:
            sparkle(c, x + sz * 0.6, y - sz * 0.6, 7 * smooth(prog(t, 5.35, 5.7)), 255, rot=t * 40)
    # salt shaker
    ang, lift = shaker_angle(t), shaker_lift(t)
    c.save()
    c.translate(SHAKER[0], SHAKER[1] + lift)
    c.rotate(ang)
    body = rrect(-45, -75, 90, 145, 22)
    c.drawRRect(body, fill(ICE, 60))
    c.save()
    c.clipRRect(body, doAntiAlias=True)
    level = lerp(-20, 15, prog(t, 4.7, 5.5))
    tilt_fill = skia.Path()
    tilt_fill.addRect(skia.Rect.MakeXYWH(-60, level, 120, 120))
    c.save()
    c.rotate(-ang * 0.85)
    c.drawPath(tilt_fill, fill((245, 248, 255), 230))
    c.restore()
    c.restore()
    c.drawRRect(body, stroke(ICE, 3, 200))
    c.drawRRect(rrect(-30, -60, 10, 90, 5), fill(WHITE, 90))
    c.drawRRect(rrect(-50, -108, 100, 38, 16), shaded(linear((-50, 0), (50, 0), [(235, 235, 250), (150, 150, 175)])))
    for hx in (-18, 0, 18):
        c.drawCircle(hx, -96, 3.5, fill((90, 90, 115)))
    c.restore()
    # twinkles during "surrounded by crystals"
    for (ts, sx, sy, sz) in KITCHEN_SPARKLES:
        k = prog(t, ts, ts + 0.8)
        if 0 < k < 1:
            sparkle(c, sx, sy, sz * math.sin(math.pi * k), 255, rot=k * 90)
    c.restore()


# ---------------------------------------------------------------- scene 1b: three panels
CARD_W, CARD_H = 500, 600
CARDS = [dict(cx=420, t_in=TO_PANELS, tint=CYAN, label="SALT", sub="halite"),
         dict(cx=960, t_in=6.45, tint=PINK, label="YOUR PHONE", sub="quartz"),
         dict(cx=1500, t_in=8.85, tint=MINT, label="YOUR BONES", sub="apatite")]
PULL_BACK = 13.25
EARTH_C = (960, 560)


def card_rect(i, t):
    """Returns (cx, cy, w, h, radius, alpha) for card i."""
    cd = CARDS[i]
    cy = 520 + bob(t, 5, 3.4, i * 0.3)
    if i == 0:
        a = smooth(prog(t, TO_PANELS, TO_PANELS + 0.25))
        p = in_out(prog(t, TO_PANELS + 0.25, TO_PANELS + 0.95))
        cx, cy2 = lerp(W / 2, cd["cx"], p), lerp(H / 2, cy, p)
        w, h, r = lerp(W + 40, CARD_W, p), lerp(H + 40, CARD_H, p), lerp(0, 36, p)
    else:
        p = out_back(prog(t, cd["t_in"], cd["t_in"] + 0.6), 1.2)
        a = smooth(prog(t, cd["t_in"], cd["t_in"] + 0.25))
        cx, cy2, w, h, r = cd["cx"], lerp(H + CARD_H, cy, p), CARD_W, CARD_H, 36
    # pull back: everything shrinks into the Earth
    q = in_cubic(prog(t, PULL_BACK, PULL_BACK + 0.75))
    if q > 0:
        cx, cy2 = lerp(cx, EARTH_C[0] + (cx - 960) * 0.05, q), lerp(cy2, EARTH_C[1], q)
        w, h, r = w * (1 - q), h * (1 - q), r * (1 - q)
        a *= 1 - smooth(prog(t, PULL_BACK + 0.45, PULL_BACK + 0.75))
    return cx, cy2, w, h, r, a


def draw_salt_content(c, t, s):
    cube(c, 0, -30 * s, 120 * s, t * 0.7 + 0.6, 0.55, ICE, 255, 220, 90)
    for k, (ox, oy, ph) in enumerate([(-130, -150, 0.0), (120, 40, 0.45), (-90, 90, 0.8)]):
        tw = (t * 0.7 + ph) % 1.0
        sparkle(c, ox * s, oy * s, 18 * s * math.sin(math.pi * tw), 255, rot=tw * 90)


def draw_phone_content(c, t, s, cd):
    xr = smooth(prog(t, cd["t_in"] + 0.8, cd["t_in"] + 1.4))
    c.save()
    c.scale(s, s)
    c.rotate(-8 + bob(t, 2, 4))
    soft_shadow(c, rrect(-105, -200, 210, 400, 34), 16, 22, 18, 100)
    c.drawRRect(rrect(-105, -200, 210, 400, 34), shaded(linear((-105, 0), (105, 0), [(70, 60, 110), (36, 28, 64)])))
    screen = rrect(-92, -184, 184, 368, 24)
    c.drawRRect(screen, shaded(linear((0, -184), (0, 184), [(255, 120, 170, ), (120, 70, 210)])))
    c.save()
    c.clipRRect(screen, doAntiAlias=True)
    c.drawRRect(screen, fill((14, 12, 40), 225 * xr))
    for k in range(6):  # circuit traces
        y = -150 + k * 58
        c.drawPath(poly([(-92, y), (-40, y), (-20, y + 20), (92, y + 20)], False), stroke(CYAN, 3, 110 * xr))
    glow(c, 0, 20, 120, PINK, 170 * xr)
    _quartz(c, 0, 20, 1.0, xr)
    c.restore()
    c.drawRRect(rrect(-30, -178, 60, 12, 6), fill((20, 16, 36)))
    c.restore()


def _quartz(c, x, y, s, a):
    """Hexagonal quartz prism with pointed tip (three visible faces)."""
    if a <= 0.01:
        return
    w, h, tip = 34 * s, 90 * s, 46 * s
    faces = [([(x - w, y - h / 2), (x - w * 0.35, y - h / 2 - 6), (x - w * 0.35, y + h / 2 + 6), (x - w, y + h / 2)], lighten(PINK, 0.55)),
             ([(x - w * 0.35, y - h / 2 - 6), (x + w * 0.35, y - h / 2 - 6), (x + w * 0.35, y + h / 2 + 6), (x - w * 0.35, y + h / 2 + 6)], lighten(PINK, 0.3)),
             ([(x + w * 0.35, y - h / 2 - 6), (x + w, y - h / 2), (x + w, y + h / 2), (x + w * 0.35, y + h / 2 + 6)], PINK),
             ([(x - w, y - h / 2), (x, y - h / 2 - tip), (x - w * 0.35, y - h / 2 - 6)], WHITE),
             ([(x - w * 0.35, y - h / 2 - 6), (x, y - h / 2 - tip), (x + w * 0.35, y - h / 2 - 6)], lighten(PINK, 0.7)),
             ([(x + w * 0.35, y - h / 2 - 6), (x, y - h / 2 - tip), (x + w, y - h / 2)], lighten(PINK, 0.45))]
    for pts, cc in faces:
        c.drawPath(poly(pts), fill(cc, 255 * a))
        c.drawPath(poly(pts), stroke(WHITE, 1.5, 120 * a))


def draw_arm_content(c, t, s, cd):
    xr = smooth(prog(t, cd["t_in"] + 0.7, cd["t_in"] + 1.3))
    c.save()
    c.scale(s, s)
    c.rotate(10 + bob(t, 2, 4.5))
    c.translate(0, -30)
    c.scale(0.82, 0.82)
    skin = skia.Path()
    skin.addRRect(rrect(-72, 40, 144, 260, 60))
    skin.addRRect(rrect(-86, -70, 172, 150, 60))
    for (fx, fy, ln, ang) in [(-62, -50, 95, -18), (-28, -70, 125, -5), (8, -74, 135, 3), (44, -66, 120, 11), (84, 10, 85, 48)]:
        f = skia.Path()
        f.addRRect(rrect(-17, -ln, 34, ln + 10, 17))
        m = skia.Matrix()
        m.setRotate(ang)
        m.postTranslate(fx, fy)
        f.transform(m)
        skin.addPath(f)
    skin.setFillType(skia.PathFillType.kWinding)
    c.drawPath(skin, fill(lerp_col((210, 150, 200), (60, 70, 120), xr), 255))
    c.drawPath(skin, stroke(lerp_col((240, 190, 220), CYAN, xr), 3, 160))
    if xr > 0.01:
        bone = MINT
        glow(c, 0, 40, 220, MINT, 70 * xr)
        p = stroke(bone, 15, 255 * xr)
        c.drawLine(-28, 290, -22, 100, p)       # ulna
        c.drawLine(24, 290, 26, 100, p)         # radius
        for (bx, by) in [(-30, 70), (-8, 64), (14, 64), (34, 72), (-20, 46), (2, 42), (24, 46)]:
            c.drawCircle(bx, by, 10, fill(bone, 255 * xr))
        for (fx, fy, ln, ang) in [(-62, -50, 95, -18), (-28, -70, 125, -5), (8, -74, 135, 3), (44, -66, 120, 11), (84, 10, 85, 48)]:
            c.save()
            c.translate(fx, fy)
            c.rotate(ang)
            seg = [0, 0.42, 0.72, 0.95] if ang != 48 else [0, 0.5, 0.95]
            c.drawLine(0, 45 if ang != 48 else 10, 0, 6, stroke(bone, 11, 255 * xr))   # metacarpal
            for a0, a1 in zip(seg[:-1], seg[1:]):
                c.drawLine(0, -ln * a0 - 4, 0, -ln * a1 + 4, stroke(bone, 10, 255 * xr))
            c.restore()
    c.restore()


def lerp_col(a, b, t):
    return mix(a, b, t)


def draw_cards(c, t):
    for i, cd in enumerate(CARDS):
        if t < cd["t_in"]:
            continue
        cx, cy, w, h, r, a = card_rect(i, t)
        if a <= 0.01 or w < 2:
            continue
        c.saveLayerAlpha(None, int(255 * a))
        rr = rrect(cx - w / 2, cy - h / 2, w, h, r)
        soft_shadow(c, rr, 14, 24, 26, 120)
        c.drawRRect(rr, shaded(linear((cx, cy - h / 2), (cx, cy + h / 2), [mix(NAVY, cd["tint"], 0.12), mix(PURPLE, cd["tint"], 0.05)])))
        c.save()
        c.clipRRect(rr, doAntiAlias=True)
        glow(c, cx, cy - h * 0.1, w * 0.6, cd["tint"], 45)
        s = w / CARD_W
        c.save()
        c.translate(cx, cy - 40 * s)
        if i == 0:
            draw_salt_content(c, t, s)
        elif i == 1:
            draw_phone_content(c, t, s, cd)
        else:
            draw_arm_content(c, t, s, cd)
        c.restore()
        c.restore()
        c.drawRRect(rr, stroke(cd["tint"], 3, 90))
        la = smooth(prog(t, cd["t_in"] + 0.6, cd["t_in"] + 1.0)) * (1 if i else smooth(prog(t, TO_PANELS + 0.8, TO_PANELS + 1.2)))
        if la > 0.01:
            text(c, cd["label"], cx, cy + h / 2 - 78 * s, 40 * s, WHITE, 255 * la, 800, spacing=3 * s)
            text(c, cd["sub"], cx, cy + h / 2 - 38 * s, 26 * s, cd["tint"], 230 * la, 600, spacing=2 * s)
        c.restore()


# ---------------------------------------------------------------- scene 1c: Earth + bird
def _continents():
    rng = np.random.default_rng(21)
    blobs = []
    for (lon, lat, rad) in [(-100, 45, 32), (-60, -15, 26), (15, 45, 22), (20, 5, 28), (90, 45, 36), (135, -25, 18), (-40, 72, 14), (70, 20, 14)]:
        n = 26
        radii = rad * (0.75 + 0.5 * rng.random(n))
        radii = np.convolve(np.r_[radii[-2:], radii, radii[:2]], np.ones(5) / 5, "valid")
        blobs.append([(lon + radii[k] * math.cos(2 * math.pi * k / n) * 1.3, lat + radii[k] * math.sin(2 * math.pi * k / n))
                      for k in range(n)])
    clouds = [(lon, lat, w) for lon, lat, w in zip(rng.uniform(-180, 180, 14), rng.uniform(-60, 60, 14), rng.uniform(14, 30, 14))]
    return blobs, clouds


CONTINENTS, CLOUDS = _continents()


def _ortho(lon, lat, rot, R):
    lo, la = math.radians(lon + rot), math.radians(lat)
    x, y, z = R * math.cos(la) * math.sin(lo), -R * math.sin(la), math.cos(la) * math.cos(lo)
    if z < 0:  # behind the limb: pin to the edge so shapes wrap cleanly
        d = math.hypot(x, y) or 1.0
        x, y = x / d * R, y / d * R
    return x, y, z


def draw_earth(c, cx, cy, R, rot, a=1.0):
    if R < 1 or a <= 0.01:
        return
    c.saveLayerAlpha(None, int(255 * a))
    glow(c, cx, cy, R * 1.35, CYAN, 90)
    c.save()
    c.translate(cx, cy)
    c.rotate(-18)
    disc = skia.Path()
    disc.addCircle(0, 0, R)
    c.drawPath(disc, shaded(radial((-R * 0.35, -R * 0.4), R * 1.5, [(70, 150, 255), (40, 96, 220), (24, 50, 140)], [0, 0.55, 1])))
    c.save()
    c.clipPath(disc, doAntiAlias=True)
    for blob in CONTINENTS:
        pts = [_ortho(lo, la, rot, R) for lo, la in blob]
        if max(p[2] for p in pts) <= 0:
            continue
        path = smooth_closed([(p[0], p[1]) for p in pts])
        c.drawPath(path, fill((88, 205, 135)))
        c.drawPath(path, stroke((150, 235, 170), max(1.0, R * 0.008), 120))
    # ice caps
    c.drawOval(skia.Rect.MakeXYWH(-R * 0.5, -R * 1.05, R, R * 0.22), fill((240, 248, 255)))
    c.drawOval(skia.Rect.MakeXYWH(-R * 0.55, R * 0.86, R * 1.1, R * 0.2), fill((240, 248, 255)))
    for lon, lat, w in CLOUDS:
        x, y, z = _ortho(lon, lat, rot * 1.3 + 20, R)
        if z > 0.05:
            sc = 0.35 + 0.65 * z
            c.drawRRect(rrect(x - w * R / 150 * sc, y - R * 0.025, 2 * w * R / 150 * sc, R * 0.05, R * 0.025), fill(WHITE, 170 * z))
    # night side shading + rim
    c.drawPath(disc, shaded(linear((-R * 0.6, -R * 0.6), (R * 0.9, R * 0.9), [((10, 8, 40), 0), ((10, 8, 40), 0), ((10, 8, 40), 190)], [0, 0.45, 1])))
    c.restore()
    c.drawPath(disc, stroke((150, 220, 255), max(1.5, R * 0.012), 160))
    c.restore()
    c.restore()


BIRD_T = 15.0
CUBE_T = 16.15
ZOOM = (16.6, 17.55)
FLASH = (17.3, 17.95)
CUBE_POS = (960, 470)


def draw_space(c, t, stars, dust):
    zt = 1 + 0.06 * prog(t, PULL_BACK, DURATION)
    e = out_cubic(prog(t, PULL_BACK, PULL_BACK + 1.25))
    zc = in_cubic(prog(t, *ZOOM))
    zoom = lerp(1.0, 28.0, zc)
    c.save()
    c.translate(CUBE_POS[0], CUBE_POS[1])
    c.scale(zoom, zoom)
    c.translate(-CUBE_POS[0], -CUBE_POS[1])
    stars.draw(c, t, 1.0, zoom=lerp(2.2, 1.0, e) * zt)
    R = 280 * lerp(6.5, 1.0, e)
    draw_earth(c, EARTH_C[0], EARTH_C[1] + lerp(R * 0.5, 0, e) * 0 + bob(t, 3, 5), R, -t * 14 + 40, smooth(prog(t, PULL_BACK - 0.1, PULL_BACK + 0.35)))
    # the salt grain that we're about to dive into
    k = pop(t, CUBE_T, 0.5)
    if k > 0:
        cube(c, CUBE_POS[0], CUBE_POS[1] + bob(t, 6, 2.6), 60 * k, t * 0.9, 0.5, ICE, 255, 220, 110)
        sparkle(c, CUBE_POS[0] + 58, CUBE_POS[1] - 62, 22 * math.sin(math.pi * prog(t, CUBE_T + 0.25, CUBE_T + 0.95)), rot=t * 60)
    c.restore()
    # the bird (screen space, gets pushed off as we zoom)
    b = pop(t, BIRD_T, 0.5)
    if b > 0:
        off = in_cubic(prog(t, *ZOOM)) * 700
        bx, by = 1580 + off * 0.6, 1000 + off * 0.4
        c.save()
        c.translate(bx, by)
        c.scale(b, b)
        bird(c, 0, 0, 84, t, look=(-0.9, -0.4), tilt=-6 + 10 * math.sin(math.pi * prog(t, VO["L6"], VO["L6"] + 0.9)), wing=0.0)
        c.restore()
        q = pop(t, VO["L6"] + 0.05, 0.4) * (1 - smooth(prog(t, ZOOM[0], ZOOM[0] + 0.3)))
        if q > 0:
            c.save()
            c.translate(bx - 150, by - 280)
            c.scale(q, q)
            c.drawRRect(rrect(-48, -54, 96, 96, 30), fill(WHITE))
            c.drawPath(poly([(10, 38), (40, 38), (46, 70)]), fill(WHITE))
            text(c, "?", 0, 16, 64, INK, 255, 800)
            c.restore()


# ---------------------------------------------------------------- scene 2: atoms
class Wanderers:
    def __init__(self, n=26, seed=9):
        rng = np.random.default_rng(seed)
        self.base = rng.random((n, 2)) * [W - 200, H - 200] + 100
        self.f = rng.uniform(0.12, 0.3, (n, 2))
        self.ph = rng.uniform(0, 6.28, (n, 2))
        self.amp = rng.uniform(90, 220, (n, 2))
        self.r = rng.uniform(26, 42, n)
        self.blink = rng.random(n)

    def tau(self, t):
        # atoms "stop wandering": local time slows down after ~21.6 s
        t0 = 21.4
        return t if t < t0 else t0 + (t - t0) * 0.3 + 0.7 * 0.6 * (1 - math.exp(-(t - t0) / 0.6))

    def draw(self, c, t, a):
        if a <= 0.01:
            return
        tau = self.tau(t)
        spread = 1 + 0.6 * in_cubic(prog(t, 22.6, 23.6))
        for i in range(len(self.r)):
            x = self.base[i, 0] + self.amp[i, 0] * math.sin(self.f[i, 0] * tau * 6.28 + self.ph[i, 0])
            y = self.base[i, 1] + self.amp[i, 1] * math.sin(self.f[i, 1] * tau * 6.28 + self.ph[i, 1])
            x, y = W / 2 + (x - W / 2) * spread, H / 2 + (y - H / 2) * spread
            vx = math.cos(self.f[i, 0] * tau * 6.28 + self.ph[i, 0])
            vy = math.cos(self.f[i, 1] * tau * 6.28 + self.ph[i, 1])
            rgb = NA_COL if i % 2 == 0 else CL_COL
            atom(c, x, y + bob(t, 3, 2.2, i * 0.13), self.r[i], rgb, t, 255 * a, look=(vx, vy * 0.6), blink=self.blink[i])


L = 5.0  # lattice normalisation: a 10-atom edge spans -0.9..0.9


def _lattice():
    """Each site: (i, j, k, appear_time). NaCl alternates by parity."""
    sites = {(0, 0, 0): 24.55, (1, 0, 0): 24.55}

    def add(rng_ijk, t0, t1, center=(0.5, 0.5, 0.5)):
        new = [s for s in rng_ijk if s not in sites]
        # grow shell by shell so the crystal always stays a cube
        new.sort(key=lambda s: (max(abs(s[q] - center[q]) for q in range(3)),
                                sum((s[q] - center[q]) ** 2 for q in range(3))))
        for n_, s in enumerate(new):
            sites[s] = lerp(t0, t1, n_ / max(1, len(new) - 1))

    add([(i, j, 0) for i in (0, 1) for j in (0, 1)], 25.6, 25.95, (0.5, 0.5, 0))
    add([(i, j, 0) for i in range(-1, 3) for j in range(-1, 3)], 26.9, 27.9, (0.5, 0.5, 0))
    add([(i, j, k) for i in range(-2, 4) for j in range(-2, 4) for k in range(-2, 4)], 28.9, 30.6)
    add([(i, j, k) for i in range(-4, 6) for j in range(-4, 6) for k in range(-4, 6)], 30.6, 32.4)
    return sites


SITES = _lattice()
SITE_LIST = sorted(SITES.items(), key=lambda kv: kv[1])
PAIR_IN = (23.0, 24.55)
TO_CUBE = (32.9, 34.5)
TAG_T = END_TAG = 37.5


def lattice_view(t):
    """Camera for the lattice: (center xyz, screen scale, yaw, pitch)."""
    cy_ = lerp(0.0, 0.5, smooth(prog(t, 25.5, 26.0)))
    cz = lerp(0.0, 0.5, smooth(prog(t, 28.7, 30.0)))
    sc = 750
    sc = lerp(sc, 800, smooth(prog(t, 26.8, 27.9)))
    sc = lerp(sc, 560, smooth(prog(t, 28.8, 30.6)))
    sc = lerp(sc, 330, in_out(prog(t, 30.4, 32.4)))
    sc = lerp(sc, 230, in_out(prog(t, *TO_CUBE)))
    sc = lerp(sc, 150, in_out(prog(t, TAG_T, TAG_T + 0.8)))
    r = in_out(prog(t, 28.4, 30.4))
    yaw = r * 0.45 + 0.7 * smooth(prog(t, 30.4, DURATION))
    pitch = r * 0.5
    return (0.5, cy_, cz), sc, yaw, pitch


def draw_lattice(c, t):
    if t < PAIR_IN[0]:
        return
    (cx, cy_, cz), sc, yaw, pitch = lattice_view(t)
    fade_atoms = 1 - smooth(prog(t, TO_CUBE[0] + 0.5, TO_CUBE[1]))
    up = bob(t, 5, 3.0)
    # cube grows in as atoms fade
    ca = smooth(prog(t, TO_CUBE[0] + 0.2, TO_CUBE[1]))
    if fade_atoms > 0.01:
        pts = []
        for (i, j, k), ta in SITE_LIST:
            if t < ta and ta != SITES[(0, 0, 0)]:
                break
            p = ((i - cx) / L, (j - cy_) / L, (k - cz) / L)
            x, y, z, kk = project(p, sc, yaw, pitch, W / 2, H / 2 + up)
            pts.append((z, x, y, kk, (i, j, k), ta))
        # hero pair flies in from the sides
        if t < PAIR_IN[1] + 0.01:
            m = out_cubic(prog(t, *PAIR_IN))
            pts = [(0, lerp(-150, x, m) if ijk == (0, 0, 0) else lerp(W + 150, x, m), y, kk, ijk, 0)
                   for (z, x, y, kk, ijk, ta) in pts]
        spacing = sc / L
        # bonds (one path, drawn behind)
        if t > PAIR_IN[1]:
            pos = {p[4]: (p[1], p[2]) for p in pts}
            bonds = skia.Path()
            for ijk, (x, y) in pos.items():
                for d in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                    nb = (ijk[0] + d[0], ijk[1] + d[1], ijk[2] + d[2])
                    if nb in pos:
                        bonds.moveTo(x, y)
                        bonds.lineTo(*pos[nb])
            c.drawPath(bonds, stroke(ICE, max(1.2, spacing * 0.09), 120 * fade_atoms))
        pts.sort(key=lambda p: -p[0])
        big = len(pts) < 60
        for z, x, y, kk, ijk, ta in pts:
            s = pop(t, ta, 0.4) if ta > 25 else 1.0
            r = spacing * lerp(0.4, 0.27, smooth(prog(t, 28.6, 30.0))) * kk * s
            rgb = NA_COL if (ijk[0] + ijk[1] + ijk[2]) % 2 == 0 else CL_COL
            if big:
                look = (0.6 if ijk == (0, 0, 0) else -0.6, 0) if t < 25.5 else (0, 0)
                atom(c, x, y, r, rgb, t, 255 * fade_atoms, look=look, blink=(ijk[0] * 0.37 + ijk[1] * 0.71) % 1)
            else:
                # cheaper atoms for the big lattice
                shade = 0.55 + 0.45 * clamp(1 - (z + 1) / 2)
                c.drawCircle(x, y, r, fill(mix(darken(rgb, 0.5), lighten(rgb, 0.2), shade), 255 * fade_atoms))
                if r > 7:
                    c.drawCircle(x - r * 0.3, y - r * 0.35, r * 0.35, fill(WHITE, 60 * fade_atoms))
        # "hands" on the hero pair
        if PAIR_IN[1] <= t < 26.0:
            ha = 1 - smooth(prog(t, 25.6, 26.0))
            (_, x0, y0, _, _, _), (_, x1, y1, _, _, _) = [p for p in pts if p[4] in ((0, 0, 0), (1, 0, 0))][:2]
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            g = pop(t, PAIR_IN[1], 0.3)
            c.drawCircle(mx, my, 60 * (1 + prog(t, PAIR_IN[1], PAIR_IN[1] + 0.4)), stroke(WHITE, 4, 180 * (1 - prog(t, PAIR_IN[1], PAIR_IN[1] + 0.4))))
            c.drawCircle(mx - 8, my + 4, 15 * g, fill(darken(NA_COL, 0.05), 255 * ha))
            c.drawCircle(mx + 8, my + 4, 15 * g, fill(darken(CL_COL, 0.05), 255 * ha))
        # name tags
        tags = [("SODIUM", (0, 0, 0), 23.25, NA_COL, -95), ("CHLORINE", (1, 0, 0), 23.9, CL_COL, 95)]
        for label, ijk, tt, rgb, dx in tags:
            g = pop(t, tt, 0.4) * (1 - smooth(prog(t, 25.3, 25.7)))
            hit = [p for p in pts if p[4] == ijk]
            if g > 0.01 and hit:
                _, x, y, _, _, _ = hit[0]
                c.save()
                c.translate(x + dx * out_cubic(prog(t, PAIR_IN[1] - 0.6, PAIR_IN[1])), y - 125)
                c.scale(g, g)
                w = font(30, 800).measureText(label) + 44
                c.drawRRect(rrect(-w / 2, -28, w, 52, 26), fill(rgb))
                tip = -dx * 0.5 * out_cubic(prog(t, PAIR_IN[1] - 0.6, PAIR_IN[1]))
                c.drawPath(poly([(tip - 10, 23), (tip + 10, 23), (tip, 40)]), fill(rgb))
                text(c, label, 0, 10, 30, INK, 255, 800, spacing=2)
                c.restore()
    if ca > 0.01 and t < TO_CUBE[1]:
        cube(c, W / 2, H / 2 + up, sc * 1.0, yaw, pitch, ICE, 255 * ca, 220, 110 * ca)


def draw_finale(c, t):
    """Solid salt crystal + '6,000+ known minerals' tag."""
    if t < TO_CUBE[1]:
        return
    (_, _, _), sc, yaw, pitch = lattice_view(t)
    lift = -90 * in_out(prog(t, TAG_T, TAG_T + 0.8))
    up = bob(t, 5, 3.0)
    cube(c, W / 2, H / 2 + up + lift, sc, yaw, pitch, ICE, 255, 220, 110)
    g = prog(t, 35.6, 36.4)
    if 0 < g < 1:
        sparkle(c, W / 2 + sc * 0.95, H / 2 - sc * 0.95 + up + lift, 46 * math.sin(math.pi * g), rot=g * 120)
    if t > TAG_T:
        icons = 14
        for n in range(icons):
            tn = TAG_T + 0.15 + n * 0.05
            k = out_back(prog(t, tn, tn + 0.5))
            if k <= 0:
                continue
            ang = -math.pi * 1.1 + n / (icons - 1) * math.pi * 1.2  # arc over the crystal
            rad = lerp(0, 330 + 40 * (n % 2), k)
            x, y = W / 2 + rad * math.cos(ang) * 1.25, H / 2 + lift + rad * math.sin(ang) * 0.75 + bob(t, 4, 2.5, n * 0.2)
            gem(c, x, y, 26 * k, n, t)
        ta = smooth(prog(t, TAG_T + 0.5, TAG_T + 0.9))
        text(c, "6,000+", W / 2, H / 2 + 285, 84, WHITE, 255 * ta, 800)
        text(c, "KNOWN MINERALS", W / 2, H / 2 + 342, 34, CYAN, 255 * ta, 700, spacing=6)


GEM_COLS = [PINK, CYAN, YELLOW, MINT, ORANGE, (170, 130, 255), (255, 110, 110)]


def gem(c, x, y, s, n, t):
    rgb = GEM_COLS[n % len(GEM_COLS)]
    kind = n % 4
    c.save()
    c.translate(x, y)
    c.rotate(bob(t, 8, 3.0, n * 0.17))
    glow(c, 0, 0, s * 2.2, rgb, 60)
    if kind == 0:   # octahedron
        c.drawPath(poly([(0, -s * 1.3), (-s, 0), (0, s * 1.3)]), fill(lighten(rgb, 0.3)))
        c.drawPath(poly([(0, -s * 1.3), (s, 0), (0, s * 1.3)]), fill(darken(rgb, 0.1)))
    elif kind == 1:  # hex prism
        c.drawPath(poly([(-s * 0.6, -s), (0, -s * 1.5), (s * 0.6, -s), (s * 0.6, s), (-s * 0.6, s)]), fill(rgb))
        c.drawPath(poly([(-s * 0.6, -s), (0, -s * 1.5), (0, s), (-s * 0.6, s)]), fill(lighten(rgb, 0.35)))
    elif kind == 2:  # rhomb
        c.drawPath(poly([(-s * 1.1, -s * 0.2), (-s * 0.3, -s), (s * 1.1, -s * 0.4), (s * 0.3, s * 0.7)]), fill(rgb))
        c.drawPath(poly([(-s * 1.1, -s * 0.2), (-s * 0.3, -s), (s * 0.3, s * 0.7)]), fill(lighten(rgb, 0.3)))
    else:            # cut gem
        c.drawPath(poly([(-s, -s * 0.3), (-s * 0.5, -s * 0.8), (s * 0.5, -s * 0.8), (s, -s * 0.3), (0, s)]), fill(rgb))
        c.drawPath(poly([(-s, -s * 0.3), (s, -s * 0.3), (0, s)]), fill(darken(rgb, 0.15)))
        c.drawPath(poly([(-s * 0.5, -s * 0.8), (s * 0.5, -s * 0.8), (s * 0.25, -s * 0.3), (-s * 0.25, -s * 0.3)]), fill(lighten(rgb, 0.4)))
    c.restore()


# ---------------------------------------------------------------- compose
_STATE = {}


def draw_frame(c, t):
    if not _STATE:
        _STATE.update(stars=Stars(), dust=Dust(), wander=Wanderers())
    st = _STATE
    c.clear(col(NAVY))
    if t < TO_PANELS + 0.3:
        draw_kitchen(c, t)
    if TO_PANELS <= t < FLASH[1]:
        if t >= PULL_BACK - 0.2:
            background(c, (12, 12, 38), (26, 20, 66))
            draw_space(c, t, st["stars"], st["dust"])
        elif t >= TO_PANELS + 0.25:
            background(c)
            st["dust"].draw(c, t)
        draw_cards(c, t)
    if t >= FLASH[0] + 0.3:
        background(c)
        st["dust"].draw(c, t, 1.0)
        st["wander"].draw(c, t, 1 - smooth(prog(t, 22.7, 23.5)))
        draw_lattice(c, t)
        draw_finale(c, t)
    # white-ice flash as we fall into the salt grain
    f = math.sin(math.pi * prog(t, *FLASH))
    if f > 0:
        c.drawPaint(fill(ICE, 255 * f ** 0.7))
    vignette(c)
    end = smooth(prog(t, DURATION - 0.7, DURATION))
    if end > 0:
        c.drawPaint(fill((8, 8, 24), 255 * end))


def render(t, scale=1.0):
    s = skia.Surface(int(W * scale), int(H * scale))
    c = s.getCanvas()
    c.scale(scale, scale)
    draw_frame(c, t)
    arr = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    if scale != 1.0:
        return arr[:, :, :3].copy()
    return finish(arr, t)


def _job(args):
    i, scale = args
    return render(i / FPS, scale).tobytes()


# ---------------------------------------------------------------- audio cues
def sfx_events():
    ev = [(VO["L1"] + 0.1, "swell_soft", 0.6)]
    ev += [(ts, "chime", 0.5) for (ts, _, _, _) in KITCHEN_SPARKLES]
    ev += [(CAM_PUSH[0], "whoosh_soft", 0.45), (POUR_T0, "slide", 0.4)]
    for s in SALT:
        for (tb, v) in s["bounces"][:2]:
            ev.append((tb, "tink", 0.25 + 0.5 * v))
    ev += [(5.4, "chime", 0.7), (CAM_DIVE[0] + 0.2, "whoosh", 0.7)]
    ev += [(CARDS[1]["t_in"], "whoosh_soft", 0.6), (CARDS[1]["t_in"] + 0.8, "shimmer", 0.7),
           (CARDS[2]["t_in"], "whoosh_soft", 0.6), (CARDS[2]["t_in"] + 0.7, "shimmer", 0.6)]
    ev += [(PULL_BACK, "whoosh_long", 1.0), (PULL_BACK + 0.4, "boom", 0.9)]
    ev += [(BIRD_T, "pop", 0.7), (VO["L6"] + 0.05, "pop", 0.6), (CUBE_T, "pop", 0.6), (CUBE_T + 0.3, "chime", 0.6)]
    ev += [(ZOOM[0], "riser", 0.9), (FLASH[0] + 0.25, "shimmer", 0.9)]
    ev += [(23.25, "pop", 0.6), (23.9, "pop", 0.6), (PAIR_IN[1], "click", 1.0), (PAIR_IN[1], "chime", 0.5)]
    last = 0
    for _, ta in SITE_LIST[2:]:
        if ta - last > 0.06:
            ev.append((ta, "click", 0.45 if ta < 28 else 0.22))
            last = ta
    ev += [(28.5, "riser", 0.6), (TO_CUBE[0] + 0.4, "shimmer", 0.8), (35.6, "shine", 0.9)]
    ev += [(TAG_T + 0.15 + n * 0.05, "blip", 0.35) for n in range(14)]
    ev += [(TAG_T + 0.5, "chime", 0.6)]
    return ev


MUSIC = dict(
    # (start, chord root midi, chord intervals): ambient pad progression
    chords=[(0.0, 57, (0, 7, 12, 14, 16)), (6.0, 53, (0, 7, 11, 16, 19)), (12.0, 48, (0, 7, 12, 16, 21)),
            (17.6, 55, (0, 7, 12, 14, 19)), (23.0, 57, (0, 7, 12, 15, 19)), (28.5, 53, (0, 7, 11, 16, 19)),
            (34.5, 48, (0, 7, 12, 16, 19))],
    pluck_from=17.9, pluck_bpm=96, rise=(28.5, 34.5), end=DURATION,
)


# ---------------------------------------------------------------- main
def main():
    args = sys.argv[1:]
    scale = float(args[args.index("--scale") + 1]) if "--scale" in args else 1.0
    if "--still" in args:
        from PIL import Image
        os.makedirs(os.path.join(BUILD, "stills"), exist_ok=True)
        for ts in args[args.index("--still") + 1].split(","):
            img = render(float(ts), scale)
            p = os.path.join(BUILD, "stills", f"t{float(ts):05.2f}.png")
            Image.fromarray(img).save(p)
            print(p)
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    wav = os.path.join(BUILD, "mix.wav")
    audio.render_mix(wav, DURATION, VO, os.path.join(BUILD, "vo"), sfx_events(), MUSIC)
    w, h = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
    silent = os.path.join(BUILD, "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{int(W * scale)}x{int(H * scale)}", "-r", str(FPS), "-i", "-",
                           "-vf", f"crop={w}:{h}:0:0", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                           "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    n = int(DURATION * FPS)
    with Pool(os.cpu_count()) as pool:
        for k, buf in enumerate(pool.imap(_job, [(i, scale) for i in range(n)], chunksize=4)):
            ff.stdin.write(buf)
            if k % 60 == 0:
                print(f"frame {k}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    out = os.path.join(OUT_DIR, f"{PART}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
