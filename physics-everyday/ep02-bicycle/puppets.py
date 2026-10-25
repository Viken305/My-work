"""Paper puppets and set pieces: the bike (side and rear views), the kid, the pigeon, houses, hills, sun, clouds."""
import math

import numpy as np
import skia

from paper import *  # noqa: F401,F403
import paper as P

# ---------------------------------------------------------------- bike geometry (local px, rear hub at origin)
R = 110.0
BIKE = dict(rear=(0, 0), front=(360, 0), bb=(140, 26), seat=(108, -168), saddle=(102, -182),
            ht_top=(310, -168), ht_bot=(325, -112), stem=(304, -204), grip=(272, -210), crank=46)


EXTRA, EXTRA_R = (372, -196), 72


def steer_axis_ground():
    (x0, y0), (x1, y1) = BIKE["ht_top"], BIKE["ht_bot"]
    k = (R - y1) / (y1 - y0)
    return (x1 + (x1 - x0) * k, R)


def ik(a, p, l1, l2, bend=1):
    a, p = np.asarray(a, float), np.asarray(p, float)
    d = p - a
    L = min(np.linalg.norm(d), l1 + l2 - 1e-3)
    L = max(L, abs(l1 - l2) + 1e-3)
    ang = math.atan2(d[1], d[0])
    cosA = (l1 * l1 + L * L - l2 * l2) / (2 * l1 * L)
    A = math.acos(max(-1, min(1, cosA)))
    t = ang - bend * A
    return a + l1 * np.array([math.cos(t), math.sin(t)])


def wheel(c, x, y, ang, r=R, key="w", z=0.55, rim_col=STEEL, tire=TIRE, spokes=8):
    c.save()
    c.translate(x, y)
    boil(c, key, 0.5)
    piece(c, ring(0, 0, r - 15, r), tire, z, seed=hash_s(key, 1))
    piece(c, ring(0, 0, r - 22, r - 14), rim_col, 0.12, seed=hash_s(key, 2))
    c.rotate(math.degrees(ang))
    sp = None
    for k in range(spokes):
        a = 2 * math.pi * k / spokes
        q = capsule((0, 0), ((r - 18) * math.cos(a), (r - 18) * math.sin(a)), 7, 5, 4)
        p = P.pts_path(q)
        sp = p if sp is None else union(sp, p)
    sp = union(sp, P.pts_path(circle(0, 0, 18, 24)))
    piece(c, sp, rim_col, 0.2, seed=hash_s(key, 3))
    c.restore()
    brad(c, x, y, 8)


def hash_s(*k):
    import zlib
    return zlib.crc32(repr(k).encode()) & 0xFFFF


def bike_side(c, x, ground, s=1.0, wheel_ang=0.0, crank=0.0, frame=RED, key="bike", rider=None, steer=0.0, tilt=0.0, extra=None,
              after=None):
    """Side-view bike puppet; (x, ground) = rear contact point. rider(c, pts) draws the kid in between layers."""
    B = BIKE
    c.save()
    c.translate(x, ground)
    c.rotate(tilt)
    c.scale(s, s)
    c.translate(0, -R)
    boil(c, key, 0.6)
    bb = np.array(B["bb"], float)
    near = bb + B["crank"] * np.array([math.cos(crank), math.sin(crank)])
    far = bb - B["crank"] * np.array([math.cos(crank), math.sin(crank)])
    pts = dict(near_pedal=near, far_pedal=far, **{k: np.array(v, float) for k, v in B.items() if k != "crank"})
    dk = shade(frame, 0.72)
    # far side first (darker, lower)
    piece(c, capsule(bb, far, 12), shade(TIRE, 1.2), 0.15, seed=hash_s(key, 10))
    piece(c, P.rrect(far[0] - 22, far[1] - 7, 44, 14, 4), shade(TIRE, 1.4), 0.2, seed=hash_s(key, 11))
    if rider:
        rider(c, pts, "far")
    wheel(c, 0, 0, wheel_ang, key=(key, "rw"))
    c.save()
    c.translate(*B["ht_bot"])
    c.rotate(steer)
    c.translate(-B["ht_bot"][0], -B["ht_bot"][1])
    wheel(c, B["front"][0], 0, wheel_ang, key=(key, "fw"))
    c.restore()
    if extra is not None:  # Jones' anti-gyro wheel: on a bracket above the front wheel, spun backwards
        piece(c, capsule(B["ht_top"], EXTRA, 12), shade(STEEL, 0.6), 0.4, seed=hash_s(key, 30))
        wheel(c, EXTRA[0], EXTRA[1], extra, r=EXTRA_R, key=(key, "xw"), rim_col=(120, 190, 235), spokes=6)
    # frame tubes, one cut piece (union) so it casts one shadow
    tubes = [(B["rear"], bb, 13), (B["rear"], (113, -128), 11), (bb, B["seat"], 17), (bb, (322, -122), 19),
             ((112, -128), (312, -158), 16)]
    fp = None
    for a, b, w in tubes:
        p = P.pts_path(capsule(a, b, w))
        fp = p if fp is None else union(fp, p)
    fp = union(fp, P.pts_path(capsule(B["ht_top"], B["ht_bot"], 22)))
    piece(c, fp, frame, 0.5, seed=hash_s(key, 12))
    # fork + bars
    fork = P.pts_path(capsule(B["ht_bot"], B["front"], 12))
    piece(c, fork, dk, 0.45, seed=hash_s(key, 13))
    bars = union(P.pts_path(capsule(B["ht_top"], B["stem"], 11)), P.pts_path(capsule(B["stem"], B["grip"], 11)))
    piece(c, bars, shade(STEEL, 0.75), 0.5, seed=hash_s(key, 14))
    piece(c, capsule(B["grip"], (B["grip"][0] - 26, B["grip"][1] + 4), 16), TIRE, 0.25, seed=hash_s(key, 15))
    piece(c, capsule(B["seat"], (104, -182), 9), shade(STEEL, 0.7), 0.3, seed=hash_s(key, 16))
    piece(c, wobble(P.pts_path_pts([(62, -192), (128, -196), (138, -186), (104, -176), (66, -180)]), 0.8, 3), TIRE, 0.4, smooth=True,
          seed=hash_s(key, 17))
    # chainring + crank (near)
    piece(c, circle(bb[0], bb[1], 30, 28), shade(STEEL, 0.85), 0.3, seed=hash_s(key, 18))
    piece(c, circle(bb[0], bb[1], 20, 24), shade(STEEL, 0.6), 0.1, seed=hash_s(key, 19), rim=False)
    if rider:
        rider(c, pts, "mid")
    piece(c, capsule(bb, near, 12), shade(STEEL, 0.5), 0.35, seed=hash_s(key, 20))
    piece(c, P.rrect(near[0] - 22, near[1] - 7, 44, 14, 4), TIRE, 0.4, seed=hash_s(key, 21))
    brad(c, *bb, 7)
    brad(c, *near, 5)
    brad(c, *B["ht_bot"], 6)
    if rider:
        rider(c, pts, "near")
    if after:
        after(c)
    c.restore()


def pts_path_pts(p):
    return np.asarray(p, float)


P.pts_path_pts = pts_path_pts


# ---------------------------------------------------------------- the kid (rides the side-view bike)
def kid_rider(shirt=BLUE, pants=DENIM, skin=SKIN, helmet=YELLOW, key="kid", lean=0.0, hair=HAIR, goggles=False, stripe=YELLOW):
    def draw(c, pts, layer):
        hip = pts["saddle"] + np.array([4, -14])
        sh = hip + np.array([70 + lean, -106])
        grip = pts["grip"] + np.array([-14, -4])
        if layer == "far":
            p = pts["far_pedal"] + np.array([0, -10])
            kn = ik(hip, p, 126, 122, 1)
            piece(c, capsule(hip, kn, 38, 32), shade(pants, 0.72), 0.3, seed=hash_s(key, 1))
            piece(c, capsule(kn, p, 30, 26), shade(pants, 0.72), 0.3, seed=hash_s(key, 2))
            piece(c, P.rrect(p[0] - 18, p[1] - 8, 50, 22, 9), shade(TIRE, 1.1), 0.3, seed=hash_s(key, 3))
            el = ik(sh, grip, 70, 70, -1)
            piece(c, capsule(sh, el, 24), shade(shirt, 0.72), 0.3, seed=hash_s(key, 4))
            piece(c, capsule(el, grip, 21), shade(skin, 0.8), 0.3, seed=hash_s(key, 5))
        elif layer == "mid":
            # torso + head sit between frame and near limbs
            torso = capsule(hip + np.array([0, 4]), sh, 72, 62)
            piece(c, torso, shirt, 0.55, seed=hash_s(key, 6))
            piece(c, P.rrect(hip[0] - 34, hip[1] - 26, 72, 44, 18), pants, 0.4, seed=hash_s(key, 7))
            # stripe on shirt
            d = sh - hip
            u = d / np.linalg.norm(d)
            m = hip + d * 0.55
            piece(c, capsule(m - np.array([-u[1], u[0]]) * 30, m + np.array([-u[1], u[0]]) * 30, 12), stripe, 0.15,
                  seed=hash_s(key, 8))
            hd = sh + np.array([30, -62])
            piece(c, capsule(sh + np.array([4, -6]), hd + np.array([-8, 20]), 22), skin, 0.2, seed=hash_s(key, 9))
            piece(c, circle(hd[0], hd[1], 46, 40), skin, 0.6, seed=hash_s(key, 10), smooth=True)
            piece(c, circle(hd[0] - 30, hd[1] + 2, 12, 16), shade(skin, 0.9), 0.15, seed=hash_s(key, 11))
            # hair tuft + helmet
            piece(c, P.ellipse(hd[0] - 18, hd[1] + 6, 30, 20, 24), hair, 0.2, seed=hash_s(key, 12))
            if helmet:
                hel = np.vstack([P.ellipse(hd[0] - 4, hd[1] - 10, 56, 44, 40)[20:40], [[hd[0] + 52, hd[1] - 6]]])
                piece(c, hel, helmet, 0.5, seed=hash_s(key, 13))
                piece(c, capsule((hd[0] - 30, hd[1] - 40), (hd[0] + 10, hd[1] - 50), 9), shade(helmet, 0.8), 0.1, seed=hash_s(key, 14))
            else:  # wild scientist hair
                hp = None
                for k, (dx, dy, r) in enumerate(((-40, -30, 26), (-14, -48, 28), (18, -46, 24), (-50, 0, 22), (40, -34, 18))):
                    q = P.pts_path(P.wobble(circle(hd[0] + dx, hd[1] + dy, r, 28), 1.5, k))
                    hp = q if hp is None else union(hp, q)
                piece(c, hp, hair, 0.45, seed=hash_s(key, 15))
            # face: eye, smile (ink on paper), cheek
            if goggles:
                piece(c, ring(hd[0] + 22, hd[1] - 4, 10, 17), (70, 70, 80), 0.25, seed=hash_s(key, 16))
                c.drawCircle(hd[0] + 22, hd[1] - 4, 10, skia.Paint(AntiAlias=True, Color=col((200, 235, 245), 0.7)))
                piece(c, capsule((hd[0] - 40, hd[1] - 10), (hd[0] + 6, hd[1] - 6), 7), (70, 70, 80), 0.15, seed=hash_s(key, 17))
            c.drawCircle(hd[0] + 20, hd[1] - 2, 5.5, skia.Paint(AntiAlias=True, Color=col(INK)))
            c.drawCircle(hd[0] + 21.5, hd[1] - 4, 1.8, skia.Paint(AntiAlias=True, Color=col(WHITE)))
            sm = skia.Path()
            sm.moveTo(hd[0] + 14, hd[1] + 18)
            sm.quadTo(hd[0] + 26, hd[1] + 26, hd[0] + 36, hd[1] + 14)
            c.drawPath(sm, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3.5, Color=col(INK),
                                      StrokeCap=skia.Paint.kRound_Cap))
            c.drawCircle(hd[0] + 8, hd[1] + 12, 7, skia.Paint(AntiAlias=True, Color=col(PINK, 0.55)))
            brad(c, *hip, 7)
        else:
            p = pts["near_pedal"] + np.array([0, -10])
            kn = ik(hip, p, 126, 122, 1)
            piece(c, capsule(hip, kn, 40, 34), pants, 0.5, seed=hash_s(key, 20))
            piece(c, capsule(kn, p, 32, 27), pants, 0.5, seed=hash_s(key, 21))
            piece(c, P.rrect(p[0] - 18, p[1] - 9, 52, 24, 10), WHITE, 0.45, seed=hash_s(key, 22))
            piece(c, P.rrect(p[0] - 18, p[1] + 7, 52, 7, 3), RED, 0.1, seed=hash_s(key, 23), rim=False)
            brad(c, *kn, 6)
            el = ik(sh, grip, 70, 70, -1)
            piece(c, capsule(sh, el, 27, 24), shirt, 0.55, seed=hash_s(key, 24))
            piece(c, capsule(el, grip, 22, 19), skin, 0.55, seed=hash_s(key, 25))
            piece(c, circle(grip[0], grip[1], 15, 18), skin, 0.5, seed=hash_s(key, 26))
            brad(c, *sh, 6)
            brad(c, *el, 5)
    return draw


# ---------------------------------------------------------------- rear view: bike + rider leaning
def bike_rear(c, x, ground, s=1.0, lean=0.0, steer=0.0, key="rear", shirt=BLUE, rider=True, pedal=0.0):
    """Seen from behind: (x, ground) is the tyre contact point; lean in degrees (+ = to the viewer's right)."""
    c.save()
    c.translate(x, ground)
    c.rotate(lean)
    c.scale(s, s)
    boil(c, key, 0.6)
    # front wheel peeks out when steered
    if abs(steer) > 0.5:
        c.save()
        c.translate(steer * 2.2, -6)
        piece(c, P.ellipse(0, -R - 30, 12 + abs(steer) * 1.6, R, 40), shade(TIRE, 1.25), 0.3, seed=hash_s(key, 1))
        c.restore()
    # handlebar (behind the rider's back)
    bar_y = -2 * R - 120
    piece(c, capsule((-118 + steer * 1.5, bar_y + 8), (118 + steer * 1.5, bar_y - 8), 13), shade(STEEL, 0.7), 0.4, seed=hash_s(key, 2))
    for sx in (-1, 1):
        piece(c, capsule((sx * 118 + steer * 1.5, bar_y - sx * 8), (sx * 136 + steer * 1.5, bar_y - sx * 8 + 6), 20), TIRE, 0.3,
              seed=hash_s(key, 3 + sx))
    # rear wheel: a tall thin slab of tyre
    piece(c, P.rrect(-15, -2 * R, 30, 2 * R, 15), TIRE, 0.55, seed=hash_s(key, 6))
    piece(c, P.rrect(-5, -2 * R + 10, 10, 2 * R - 20, 5), shade(TIRE, 1.6), 0.05, seed=hash_s(key, 7), rim=False)
    piece(c, P.rrect(-26, -R - 20, 52, 26, 8), RED, 0.4, seed=hash_s(key, 8))  # mudguard/rack
    piece(c, P.rrect(-12, -R - 54, 24, 30, 6), (255, 80, 60), 0.3, seed=hash_s(key, 9))  # reflector
    c.drawRect(skia.Rect(-7, -R - 48, 7, -R - 30), skia.Paint(AntiAlias=True, Color=col((255, 200, 180), 0.5)))
    if rider:
        hip_y = -2 * R - 40
        for sx, ph in ((-1, pedal), (1, pedal + math.pi)):
            foot_y = -R - 20 + 40 * math.sin(ph)
            knee = (sx * 62, (hip_y + foot_y) / 2 - 20)
            piece(c, capsule((sx * 26, hip_y), knee, 42, 36), DENIM if sx < 0 else shade(DENIM, 0.9), 0.45, seed=hash_s(key, 10 + sx))
            piece(c, capsule(knee, (sx * 44, foot_y), 34, 28), DENIM if sx < 0 else shade(DENIM, 0.9), 0.45, seed=hash_s(key, 13 + sx))
            piece(c, P.rrect(sx * 44 - 24, foot_y - 8, 48, 26, 10), WHITE, 0.4, seed=hash_s(key, 16 + sx))
        piece(c, P.ellipse(0, hip_y - 4, 64, 34, 40), DENIM, 0.5, seed=hash_s(key, 19))
        torso = np.array([[-62, hip_y - 10], [62, hip_y - 10], [74, hip_y - 170], [-74, hip_y - 170]])
        piece(c, P.wobble(P.resample(torso, 10), 1.0, 4), shirt, 0.55, seed=hash_s(key, 20))
        piece(c, P.rrect(-62, hip_y - 104, 124, 22, 6), YELLOW, 0.15, seed=hash_s(key, 21))
        for sx in (-1, 1):
            piece(c, capsule((sx * 66, hip_y - 160), (sx * 122 + steer * 1.5, bar_y - sx * 4), 30, 24), shirt, 0.5,
                  seed=hash_s(key, 22 + sx))
            piece(c, circle(sx * 124 + steer * 1.5, bar_y - sx * 4, 16, 18), SKIN, 0.4, seed=hash_s(key, 25 + sx))
        piece(c, capsule((0, hip_y - 168), (0, hip_y - 200), 30), SKIN, 0.3, seed=hash_s(key, 28))
        hd = (0, hip_y - 236)
        piece(c, circle(*hd, 50, 40), HAIR, 0.6, seed=hash_s(key, 29), smooth=True)
        for sx in (-1, 1):
            piece(c, P.ellipse(sx * 50, hd[1] + 6, 10, 15, 20), SKIN, 0.2, seed=hash_s(key, 30 + sx))
        hel = np.vstack([P.ellipse(0, hd[1] - 8, 60, 50, 40)[20:40], [[60, hd[1] - 8]]])
        piece(c, hel, YELLOW, 0.5, seed=hash_s(key, 33))
        for k in (-26, 0, 26):
            piece(c, capsule((k, hd[1] - 52), (k * 1.3, hd[1] - 20), 8), shade(YELLOW, 0.8), 0.08, seed=hash_s(key, 34 + k))
    c.restore()


# ---------------------------------------------------------------- set dressing
def hill(c, y, amp, color, seed, z=0.6, freq=1.6):
    xs = np.linspace(-60, W + 60, 60)
    r = np.random.default_rng(seed)
    ph = r.uniform(0, 6.3, 3)
    ys = y - amp * (0.55 * np.sin(xs / W * np.pi * freq + ph[0]) + 0.3 * np.sin(xs / W * np.pi * freq * 2.3 + ph[1]) + 0.15 * np.sin(
        xs / W * np.pi * 5 + ph[2]))
    pts = np.vstack([np.stack([xs, ys], 1), [[W + 60, H + 60], [-60, H + 60]]])
    piece(c, P.torn(pts, 2.5, seed), color, z, fringe=(2.4, seed), seed=seed)


def sun(c, x, y, r=96, key="sun", t=0.0):
    c.save()
    c.translate(x, y)
    boil(c, key, 0.6)
    piece(c, P.rrect(-7, 40, 14, 900, 4), (176, 132, 84), 0.3, seed=hash_s(key, 9))  # the stick it is mounted on
    c.rotate(t * 8)
    rays = []
    for k in range(12):
        a = 2 * math.pi * k / 12
        b = 0.17
        rays.append([(r * 0.8 * math.cos(a - b), r * 0.8 * math.sin(a - b)), (r * 1.45 * math.cos(a), r * 1.45 * math.sin(a)),
                     (r * 0.8 * math.cos(a + b), r * 0.8 * math.sin(a + b))])
    rp = None
    for q in rays:
        p = P.pts_path(q)
        rp = p if rp is None else union(rp, p)
    piece(c, rp, ORANGE, 0.4, seed=hash_s(key, 1))
    piece(c, circle(0, 0, r, 60), SUN, 0.7, seed=hash_s(key, 2))
    c.restore()


def cloud(c, x, y, s=1.0, key="cloud", string_top=True):
    c.save()
    c.translate(x, y)
    if string_top:
        P.string(c, (0, -2000), (0, -40 * s), (238, 236, 230), sag=0, w=2.0)
    boil(c, key, 0.5)
    parts = [(0, 0, 60), (-70, 18, 44), (70, 16, 48), (-30, -34, 46), (34, -30, 52)]
    cp = None
    for cx, cy, r in parts:
        p = P.pts_path(P.wobble(circle(cx * s, cy * s, r * s, 40), 1.2, hash_s(key, cx)), )
        cp = p if cp is None else union(cp, p)
    flat = P.pts_path(P.rect(-110 * s, 10 * s, 220 * s, 60 * s))
    cp = minus(cp, P.pts_path(P.rect(-200 * s, 52 * s, 400 * s, 200 * s)))
    del flat
    piece(c, cp, WHITE, 0.8, seed=hash_s(key, 1))
    c.restore()


def house(c, x, base, w, h, body, roof, key, door=True, windows=2):
    c.save()
    c.translate(x, base)
    boil(c, key, 0.4)
    piece(c, P.wobble(P.resample(P.rect(0, -h, w, h), 12), 0.8, hash_s(key, 1)), body, 0.5, seed=hash_s(key, 1))
    piece(c, P.wobble(P.resample(np.array([[-18, -h + 4], [w / 2, -h - w * 0.45], [w + 18, -h + 4]]), 12), 0.8, hash_s(key, 2)), roof,
          0.6, seed=hash_s(key, 2))
    for i in range(windows):
        wx = w * (i + 1) / (windows + 1) - 22
        piece(c, P.rect(wx, -h * 0.78, 44, 50), (255, 226, 140), 0.18, seed=hash_s(key, 3 + i))
        piece(c, P.rect(wx + 20, -h * 0.78, 5, 50), shade(body, 0.7), 0.06, seed=hash_s(key, 10 + i), rim=False)
    if door:
        piece(c, P.rrect(w / 2 - 26, -96, 52, 96, 10), shade(roof, 0.9), 0.2, seed=hash_s(key, 20))
        brad(c, w / 2 + 14, -46, 4)
    c.restore()


def lamppost(c, x, ground, h=760, key="lamp"):
    c.save()
    c.translate(x, ground)
    boil(c, key, 0.4)
    piece(c, P.rrect(-11, -h, 22, h, 6), (58, 70, 84), 0.6, seed=hash_s(key, 1))
    piece(c, P.rrect(-26, -24, 52, 24, 6), (58, 70, 84), 0.5, seed=hash_s(key, 2))
    arm = capsule((0, -h + 10), (90, -h + 10), 14)
    piece(c, arm, (58, 70, 84), 0.6, seed=hash_s(key, 3))
    piece(c, np.array([[60, -h + 14], [120, -h + 14], [104, -h + 54], [76, -h + 54]]), (255, 232, 160), 0.5, seed=hash_s(key, 4))
    c.restore()
    return (x + 90, ground - h + 3)


def pigeon(c, x, y, s=1.0, key="pigeon", look=0.0, bob=0.0, flip=False):
    """Pigeon perched with its feet at (x, y)."""
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    boil(c, key, 0.8)
    for dx in (-8, 8):
        piece(c, capsule((dx, -14), (dx + 2, 0), 5), ORANGE, 0.15, seed=hash_s(key, dx))
    piece(c, P.ellipse(0, -40, 48, 30, 40, -0.15), (138, 142, 160), 0.5, seed=hash_s(key, 1), smooth=True)
    piece(c, np.array([[-36, -44], [-86, -34], [-80, -52], [-30, -58]]), (92, 96, 112), 0.4, seed=hash_s(key, 2))
    piece(c, P.ellipse(-6, -42, 34, 18, 30, -0.25), (110, 114, 132), 0.3, seed=hash_s(key, 3), smooth=True)
    c.save()
    c.translate(30, -64 + bob)
    c.rotate(look)
    piece(c, P.ellipse(0, 6, 18, 22, 24), (92, 150, 130), 0.25, seed=hash_s(key, 4))  # iridescent neck
    piece(c, circle(4, -12, 21, 28), (124, 128, 148), 0.4, seed=hash_s(key, 5))
    piece(c, np.array([[22, -14], [40, -8], [22, -4]]), (226, 170, 120), 0.2, seed=hash_s(key, 6))
    c.drawCircle(11, -17, 6, skia.Paint(AntiAlias=True, Color=col(ORANGE)))
    c.drawCircle(12, -17, 3, skia.Paint(AntiAlias=True, Color=col(INK)))
    c.restore()
    c.restore()


def snail(c, x, y, s=1.0, key="snail", helmet=True):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    boil(c, key, 0.6)
    body = np.vstack([P.ellipse(0, 0, 70, 14, 30)[15:30], [[70, -4], [84, -36], [96, -40], [92, -4]]])
    piece(c, body, (214, 196, 150), 0.3, seed=hash_s(key, 1))
    for dx in (82, 92):
        piece(c, capsule((dx, -34), (dx + 6, -62), 4), (214, 196, 150), 0.15, seed=hash_s(key, dx))
        c.drawCircle(dx + 6, -63, 4, skia.Paint(AntiAlias=True, Color=col(INK)))
    piece(c, circle(-6, -38, 40, 40), (196, 118, 70), 0.5, seed=hash_s(key, 2))
    sp = skia.Path()
    for k in range(60):
        a = k / 60 * 4 * math.pi
        r = 34 * (1 - k / 66)
        (sp.moveTo if k == 0 else sp.lineTo)(-6 + r * math.cos(a), -38 + r * math.sin(a))
    c.drawPath(sp, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4, Color=col(shade((196, 118, 70), 0.6))))
    if helmet:
        hel = np.vstack([P.ellipse(90, -42, 18, 14, 20)[10:20], [[108, -42]]])
        piece(c, hel, RED, 0.25, seed=hash_s(key, 3))
    c.restore()


def road_side(c, top, color=ROAD, key="road"):
    piece(c, P.rect(-300, top, W + 700, H - top + 300), color, 0.4, seed=hash_s(key, 1))
    for i in range(-1, 9):
        x = i * 200 - 40
        piece(c, P.wobble(P.resample(P.rect(x, top + 120, 120, 16), 10), 0.8, i), (240, 236, 222), 0.1, seed=hash_s(key, 10 + i))


def curb(c, top, key="curb"):
    piece(c, P.rect(-300, top, W + 700, 40), CURB, 0.5, seed=hash_s(key, 1))
    piece(c, P.rect(-300, top - 120, W + 700, 120), (214, 208, 196), 0.4, seed=hash_s(key, 2))
    for i in range(7):
        c.drawLine(i * 180 + 40, top - 120, i * 180 + 10, top, skia.Paint(AntiAlias=True, StrokeWidth=2, Color=col(shade(CURB, 0.75))))


def caption_strip(c, words, active, y, size=58, seed=0, max_w=940):
    """Narration caption on a torn strip of paper; the spoken word sits on a yellow chip."""
    fnt = font("title", size)
    space = fnt.measureText(" ")
    lines, cur, cw = [], [], 0
    for wd in words:
        w = fnt.measureText(wd)
        if cur and cw + space + w > max_w:
            lines.append(cur)
            cur, cw = [], 0
        cur.append((wd, w))
        cw += (space if cw else 0) + w
    lines.append(cur)
    lh = size * 1.18
    top = y - lh * len(lines) / 2
    strip = P.torn(P.rect(60, top - 34, W - 120, lh * len(lines) + 48), 3.5, seed)
    c.save()
    c.rotate(-0.6)
    piece(c, strip, WHITE, 0.7, seed=seed, fringe=None)
    idx = 0
    for li, line in enumerate(lines):
        tw = sum(w for _, w in line) + space * (len(line) - 1)
        x = W / 2 - tw / 2
        by = top + lh * (li + 0.78)
        for wd, w in line:
            if idx == active:
                piece(c, P.wobble(P.resample(P.rect(x - 10, by - size * 0.86, w + 20, size * 1.04), 8), 1.0, seed + idx), YELLOW, 0.3,
                      seed=seed + idx)
            ink_text(c, wd, x, by, fnt, INK)
            x += w + space
            idx += 1
    c.restore()


def grass_front(c, y, seed=0, color=GREEN3):
    xs = np.arange(-40, W + 60, 34)
    r = np.random.default_rng(seed)
    pts = [(-40, H + 40)]
    for x in xs:
        pts += [(x, y + r.uniform(-6, 10)), (x + 17, y - r.uniform(30, 70))]
    pts += [(W + 60, y), (W + 60, H + 40)]
    piece(c, np.array(pts, float), color, 1.4, seed=seed)
    for i in range(6):
        fx, fy = r.uniform(40, W - 40), y + r.uniform(10, 90)
        c.save()
        c.translate(fx, fy)
        pet = None
        for k in range(5):
            a = 2 * math.pi * k / 5
            p = P.pts_path(circle(26 * math.cos(a), 26 * math.sin(a), 20, 20))
            pet = p if pet is None else union(pet, p)
        piece(c, pet, [WHITE, PINK, YELLOW][i % 3], 1.6, seed=seed + 10 + i)
        piece(c, circle(0, 0, 14, 18), ORANGE if i % 3 != 2 else CORAL, 0.3, seed=seed + 20 + i)
        c.restore()


def kid_sitting(c, x, y, s=1.0, key="sit", mouth="o", cone=True):
    """The kid sat on the kerb: (x, y) = where the seat meets the kerb top."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    boil(c, key, 0.6)
    for dx, sh_ in ((-14, 0.8), (14, 1.0)):
        piece(c, capsule((dx, -20), (dx + 90, -10), 40, 36), shade(DENIM, sh_), 0.45, seed=hash_s(key, 1, dx))
        piece(c, capsule((dx + 90, -10), (dx + 100, 110), 34, 30), shade(DENIM, sh_), 0.45, seed=hash_s(key, 2, dx))
        piece(c, P.rrect(dx + 84, 102, 56, 26, 10), WHITE, 0.4, seed=hash_s(key, 3, dx))
        brad(c, dx + 90, -10, 5)
    piece(c, capsule((0, -20), (14, -150), 74, 64), BLUE, 0.55, seed=hash_s(key, 4))
    piece(c, P.rrect(-26, -100, 74, 18, 6), YELLOW, 0.12, seed=hash_s(key, 5))
    hd = (24, -212)
    piece(c, circle(*hd, 48, 40), SKIN, 0.6, seed=hash_s(key, 6), smooth=True)
    piece(c, P.ellipse(hd[0] - 22, hd[1] + 4, 28, 22, 24), HAIR, 0.2, seed=hash_s(key, 7))
    hel = np.vstack([P.ellipse(hd[0] - 2, hd[1] - 12, 56, 44, 40)[20:40], [[hd[0] + 54, hd[1] - 12]]])
    piece(c, hel, YELLOW, 0.5, seed=hash_s(key, 8))
    c.drawCircle(hd[0] + 14, hd[1] - 2, 5.5, skia.Paint(AntiAlias=True, Color=col(INK)))
    c.drawCircle(hd[0] + 36, hd[1] - 2, 5.5, skia.Paint(AntiAlias=True, Color=col(INK)))
    if mouth == "o":
        c.drawOval(skia.Rect(hd[0] + 18, hd[1] + 16, hd[0] + 34, hd[1] + 34), skia.Paint(AntiAlias=True, Color=col(INK)))
    # arm holding the ice cream (forgotten, mid-air)
    sh = (22, -140)
    el = (60, -92)
    hand_ = (96, -128)
    piece(c, capsule(sh, el, 26, 23), BLUE, 0.55, seed=hash_s(key, 9))
    piece(c, capsule(el, hand_, 22, 19), SKIN, 0.55, seed=hash_s(key, 10))
    if cone:
        piece(c, np.array([[82, -140], [114, -140], [98, -84]]), (214, 160, 90), 0.4, seed=hash_s(key, 11))
        piece(c, circle(98, -156, 22, 24), PINK, 0.5, seed=hash_s(key, 12))
        piece(c, np.array([[110, -146], [118, -128], [112, -120]]), PINK, 0.3, seed=hash_s(key, 13))  # the drip
    piece(c, circle(*hand_, 15, 18), SKIN, 0.5, seed=hash_s(key, 14))
    brad(c, *sh, 6)
    brad(c, *el, 5)
    c.restore()


def ant(c, x, y, s=1.0, key="ant", crumb=True):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    boil(c, key, 0.8)
    lp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.4, Color=col(INK), StrokeCap=skia.Paint.kRound_Cap)
    for k, dx in enumerate((-6, 2, 10)):
        ph = (held() + k) % 2
        c.drawLine(dx, -10, dx - 8 + ph * 6, 2, lp)
        c.drawLine(dx, -10, dx + 6 - ph * 6, 2, lp)
    for i, (dx, r) in enumerate(((-12, 8), (2, 5.5), (14, 7))):
        piece(c, P.ellipse(dx, -12, r * 1.2, r, 16), INK, 0.2, seed=hash_s(key, i), rim=False)
    c.drawLine(18, -16, 26, -28, lp)
    if crumb:
        piece(c, P.wobble(circle(30, -40, 15, 14), 2.0, 3), (232, 196, 128), 0.4, seed=hash_s(key, 9))
    c.restore()
