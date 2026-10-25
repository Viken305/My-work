"""Ep. 02 'Why don't bikes fall over?' (cut-paper stop-motion, 9:16). Currently: the 20-second opening test.

  python3 voiceover.py          # narration -> build/vo
  python3 film.py               # -> out/ep02_test20.mp4
  python3 film.py --still 3,9   # single frames -> build/stills

Puppets and the set animate on twos (12 poses a second, like real stop-motion); the camera moves on ones (24 fps)
the way a motion-control rig would. The tiny re-placement 'boil' changes once per pose.
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool

import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "style-tests"))

import paper as P  # noqa: E402
from paper import *  # noqa: E402,F401,F403
import puppets as Q  # noqa: E402
from puppets import *  # noqa: E402,F401,F403

FPS = 24
TL = json.load(open(os.path.join(HERE, "build", "vo", "timeline.json")))
DURATION = 80.0


# ---------------------------------------------------------------- timing helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t1)


def out_expo(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def out_back(x, s=2.2):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def lerp(a, b, u):
    return a + (b - a) * u


def q12(t):
    """Stop-motion time: held for two frames."""
    return math.floor(t * 12 + 1e-6) / 12


def words_of(key):
    """Word timings estimated from character counts across the narrated line."""
    it = TL[key]
    ws = it["text"].split()
    n = sum(len(w) + 1 for w in ws)
    out, acc = [], 0
    for w in ws:
        s = it["start"] + it["dur"] * (acc / n) * 0.96
        acc += len(w) + 1
        out.append((w, s))
    return out


def word_t(key, prefix):
    for w, s in words_of(key):
        if w.lower().strip(".,?!:").startswith(prefix.lower()):
            return s
    raise KeyError(prefix)


# ---------------------------------------------------------------- caption pages
def pages():
    out = []
    for key in TL:
        ws = words_of(key)
        cur = []
        for i, (w, s) in enumerate(ws):
            cur.append((w, s))
            left = len(ws) - 1 - i
            brk = (w[-1] in ".,:?" and len(cur) >= 3 or len(cur) >= 7 or w == "Nope.") and (left == 0 or left > 2 or w[-1] in ".?")
            if brk or i == len(ws) - 1:
                out.append(cur)
                cur = []
    res = []
    for i, pg in enumerate(out):
        end = out[i + 1][0][1] if i + 1 < len(out) else DURATION
        res.append((pg[0][1] - 0.05, end - 0.05, pg))
    return res


PAGES = pages()


def captions(c, t):
    for i, (t0, t1, pg) in enumerate(PAGES):
        if t0 <= t < t1:
            act = max([k for k, (_, s) in enumerate(pg) if s <= t] or [0])
            u = out_back(prog(t, t0, t0 + 0.18))
            c.save()
            c.translate(W / 2, 1715)
            c.scale(lerp(0.9, 1.0, u), lerp(0.9, 1.0, u))
            c.rotate(0.8 if i % 2 else -0.6)
            c.translate(-W / 2, -1715)
            caption_strip(c, [w for w, _ in pg], act, 1715, 54, seed=40 + i)
            c.restore()


# ---------------------------------------------------------------- shots / camera
T_TITLE = word_t("03", "why")
T_MYTH = TL["04"]["start"] - 0.3
T_GYRO = word_t("04", "gyro")
T_NOPE = TL["05"]["start"]
T_JONES = TL["06"]["start"] - 0.3
T_1970 = word_t("06", "1970")
T_EXTRA = word_t("06", "extra")
T_BACK = word_t("06", "backwards")
T_CANCEL = word_t("06", "cancel")
T_RIDE = TL["07"]["start"]
WIPE = 0.32


def cam_hook(t):
    u = out_expo(prog(t, 0.0, 0.9))
    z = lerp(2.6, 1.0, u) + 0.07 * in_out(prog(t, 2.4, 5.4))
    fx, fy = lerp(560, 540, u), lerp(1010, 1000, u)
    r = -4.0 * out_back(prog(t, word_t("03", "fall"), word_t("03", "fall") + 0.25)) * (1 - prog(t, T_MYTH - 0.6, T_MYTH))
    return fx, fy, z, r


def cam_myth(t):
    u = out_expo(prog(t, T_MYTH, T_MYTH + 0.7))
    z = lerp(1.35, 1.0, u) + 0.05 * prog(t, T_MYTH + 0.7, T_NOPE)
    return 540, 900, z, 0.0


def cam_jones(t):
    zin = out_expo(prog(t, T_EXTRA - 0.15, T_EXTRA + 0.45))
    zout = out_expo(prog(t, T_CANCEL - 0.1, T_CANCEL + 0.5))
    zwide = in_out(prog(t, T_RIDE, T_RIDE + 1.6))
    z = 1.0 + 0.55 * zin - 0.55 * zout + 0.06 * zwide
    fx = 540 + (130 * zin) * (1 - zout)
    fy = 1000 + (120 * zin) * (1 - zout)
    return fx, fy, z, 0.0


def shake(t, hits, amp=10.0):
    dx = dy = 0.0
    for h in hits:
        k = t - h
        if 0 <= k < 0.35:
            e = math.exp(-k * 14) * amp
            dx += e * math.sin(k * 90)
            dy += e * math.cos(k * 77)
    return dx, dy


def apply_cam(c, cam, sh=(0, 0)):
    fx, fy, z, r = cam
    c.translate(W / 2 + sh[0], H / 2 + sh[1])
    c.scale(z, z)
    c.rotate(r)
    c.translate(-fx, -fy)


# ---------------------------------------------------------------- scene 1: the street (hook + title)
HOUSES = [(0, 220, 200, CORAL, (120, 60, 60), 2), (260, 180, 250, SAND, BLUE_D, 1), (480, 240, 180, (120, 170, 210), RED_D, 2),
          (760, 200, 230, (246, 200, 120), GREEN3, 1)]
PERIOD = 1040


def street(c, scroll, tq, palette=None):
    pal = palette or dict(sky=SKY, h1=GREEN1, h2=GREEN2, houses=HOUSES)
    piece(c, P.rect(-400, -400, W + 800, H + 800), pal["sky"], 0, rim=False, shadow=False, seed=1)
    with Blur(c, 3.0):
        for k, (x, y, s) in enumerate(((230, 520, 0.9), (860, 400, 0.7), (1400, 470, 0.8))):
            xx = (x - scroll * 0.06) % 1500 - 250
            cloud(c, xx, y, s, f"cl{k}")
        sun(c, 170, 800, 90, t=tq) if pal.get("sun", True) else None
        c.save()
        c.translate(-(scroll * 0.15) % 700, 0)
        hill(c, 980, 120, pal["h1"], 11, 0.6)
        c.translate(700, 0)
        hill(c, 980, 120, pal["h1"], 11, 0.6)
        c.restore()
    with Blur(c, 1.4):
        c.save()
        off = -(scroll * 0.3) % 900
        c.translate(off - 900, 0)
        for _ in range(3):
            hill(c, 1060, 90, pal["h2"], 12, 0.7, 2.4)
            c.translate(900, 0)
        c.restore()
        base = -(scroll * 0.55)
        n0 = int(math.floor(-base / PERIOD)) - 1
        for n in range(n0, n0 + 3):
            for i, (x, w, h, b, r, wn) in enumerate(pal["houses"]):
                hx = base + n * PERIOD + x + 40
                if -300 < hx < W + 60:
                    house(c, hx, 1200, w, h, b, r, f"h{i}", windows=wn)
    lamp_x = 900 - scroll * 1.0
    if -200 < lamp_x < W + 200:
        lamp = lamppost(c, lamp_x, 1330, 560)
        rel = 250 + 200 - lamp_x
        pigeon(c, lamp[0] - 30, lamp[1] - 2, 1.25, look=clamp(-rel / 18, -30, 30), key="pg1")
    curb(c, 1330)
    c.save()
    c.translate(-(scroll % 200), 0)
    road_side(c, 1370)
    c.restore()
    for i, (yy, L) in enumerate(((1080, 260), (1160, 340), (1250, 200), (1310, 300))):
        jit = 30 * math.sin(tq * 9 + i * 2)
        piece(c, P.wobble(P.resample(P.rrect(-60 + jit, yy, L, 14, 7), 10), 0.8, i), WHITE, 0.5, seed=200 + i, alpha=0.9)


def scene_street(c, t):
    tq = q12(t)
    scroll = 420 * tq
    street(c, scroll, tq)
    sn_x = 840 - scroll * 1.0 + 30 * tq
    if sn_x > -100:
        snail(c, sn_x, 1530, 0.55, "sn")
    bike_side(c, 250, 1520, 1.15, wheel_ang=scroll / (R * 1.15), crank=tq * 7.0, rider=kid_rider(), key="b1")
    with Blur(c, 5.0):
        c.save()
        c.translate(-(scroll * 1.6) % 1080, 0)
        grass_front(c, 1760, 77)
        c.translate(1080, 0)
        grass_front(c, 1760, 77)
        c.restore()
    series_tag(c)
    # title: words slap on one by one
    if t >= T_TITLE - 0.05:
        groups = [("WHY DON'T", 300, 104, [WHITE, YELLOW, WHITE, (255, 236, 200)], 1, INK),
                  ("BIKES", 450, 150, [RED, (240, 80, 60), RED], 2, WHITE),
                  ("FALL OVER?", 610, 104, [WHITE, YELLOW, WHITE, (255, 236, 200)], 3, INK)]
        ws = words_of("03")
        starts = [ws[0][1], ws[2][1], ws[3][1]]
        for (txt, y, sz, pal, sd, fg), t0 in zip(groups, starts):
            pop = [out_back(prog(t, t0 + 0.03 * i, t0 + 0.03 * i + 0.16), 2.6) * (1 + 0.6 * (1 - prog(t, t0 + 0.03 * i, t0 + 0.03 * i + 0.1)))
                   if t >= t0 + 0.03 * i else 0 for i in range(len(txt))]
            letters(c, txt, W / 2, y, font("title", sz), pal, seed=sd, rot_amp=4, fg=fg, pop=pop)


def series_tag(c, y=118):
    tape(c, 300, y - 40, 480, 64, -1.5, seed=4)
    hand(c, "THE PHYSICS OF EVERYDAY THINGS · 02", W / 2, y + 4, 34, INK, -1.5, "center", "neat")


# ---------------------------------------------------------------- scene 2: the gyroscope myth
def scene_myth(c, t):
    tq = q12(t)
    piece(c, P.rect(-400, -400, W + 800, H + 800), KRAFT, 0, rim=False, shadow=False, seed=2)
    gp = skia.Paint(AntiAlias=True, StrokeWidth=1.5, Color=col(KRAFT2, 0.45))
    for i in range(-360, W + 400, 90):
        c.drawLine(i, -400, i, H + 400, gp)
    for j in range(-360, H + 400, 90):
        c.drawLine(-400, j, W + 400, j, gp)
    cx, cy = W / 2, 900
    spin = tq * 9.0
    c.save()
    c.translate(cx, cy)
    c.rotate(math.degrees(spin * 0.5))
    for k, (r0, a0, span) in enumerate(((330, -40, 70), (350, 140, 70), (300, 60, 40), (310, 230, 45))):
        a = np.radians(np.linspace(a0, a0 + span, 24))
        outer = np.stack([(r0 + 14) * np.cos(a), (r0 + 14) * np.sin(a)], 1)
        inner = np.stack([r0 * np.cos(a[::-1]), r0 * np.sin(a[::-1])], 1)
        piece(c, np.vstack([outer, inner]), WHITE, 0.6, seed=300 + k)
    c.restore()
    Q.wheel(c, cx, cy, spin, r=260, key="big", z=0.9, spokes=10)
    # the mouse that grabbed on and is now going round and round
    ma = spin - 0.9
    c.save()
    c.translate(cx + 268 * math.cos(ma), cy + 268 * math.sin(ma))
    c.rotate(math.degrees(ma) + 90)
    c.scale(1.7, 1.7)
    boil(c, "mouse", 1.0)
    piece(c, P.ellipse(0, -20, 34, 22, 30), GREY, 0.5, seed=31, smooth=True)
    piece(c, circle(28, -34, 13, 18), GREY, 0.35, seed=32)
    piece(c, circle(20, -48, 11, 18), PINK, 0.3, seed=33)
    sp = skia.Path()
    for k in range(30):
        a = k / 30 * 3 * math.pi + tq * 12
        r = 6 * (1 - k / 32)
        (sp.moveTo if k == 0 else sp.lineTo)(36 + r * math.cos(a), -36 + r * math.sin(a))
    c.drawPath(sp, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2, Color=col(INK)))
    P.string(c, (-34, -14), (-90, 10 + 8 * math.sin(tq * 20)), PINK, sag=10, w=3)
    c.restore()
    series_tag(c)
    if t >= T_GYRO - 0.05:
        u = out_back(prog(t, T_GYRO - 0.05, T_GYRO + 0.15), 2.0)
        c.save()
        c.translate(W / 2, 470)
        s = lerp(1.8, 1.0, u)
        c.scale(s, s)
        chip(c, "GYROSCOPE?", 0, 0, font("title", 96), INK, WHITE, -3, 0.9 + (1 - u) * 2, seed=5)
        c.restore()
    if t >= T_NOPE:
        for k, (pts, sd) in enumerate((([(250, 500), (520, 455), (840, 430)], 1), ([(260, 432), (560, 470), (830, 500)], 2))):
            u = prog(t, T_NOPE - 0.05 + k * 0.12, T_NOPE + 0.08 + k * 0.12)
            if u > 0:
                pts = P.resample(np.array(pts, float), 8, closed=False)
                n = max(2, int(len(pts) * u))
                marker(c, pts[:n], RED, 13, seed=sd)
        if t >= T_NOPE + 0.12:
            u = out_back(prog(t, T_NOPE + 0.12, T_NOPE + 0.27), 2.0)
            c.save()
            c.translate(760, 640)
            c.scale(lerp(1.7, 1, u), lerp(1.7, 1, u))
            chip(c, "NOPE.", 0, 0, font("title", 110), WHITE, RED, 8, 1.0, seed=11)
            c.restore()


# ---------------------------------------------------------------- scene 3: 1970, the anti-gyro bike
RETRO = dict(sky=(250, 214, 150), h1=(226, 150, 80), h2=(190, 110, 60), sun=True,
             houses=[(0, 220, 200, (200, 120, 70), (110, 60, 40), 2), (260, 180, 250, (238, 196, 120), (90, 110, 70), 1),
                     (480, 240, 180, (150, 160, 90), (150, 70, 40), 2), (760, 200, 230, (220, 170, 90), (120, 70, 60), 1)])


def scene_jones(c, t):
    tq = q12(t - T_JONES)
    scroll = 360 * tq
    street(c, scroll + 3000, tq, RETRO)
    s = 1.15
    gx, gy = 250, 1520
    wa = scroll / (R * s)
    rear_pigeon = lambda cc: pigeon(cc, 30, -R - 20, 0.8, "pg3", look=6 * math.sin(tq * 5), flip=False)
    bike_side(c, gx, gy, s, wheel_ang=wa, crank=tq * 6.0, frame=(60, 120, 90), key="b3", extra=-wa * 1.6, after=rear_pigeon,
              rider=kid_rider(shirt=WHITE, pants=(90, 80, 70), helmet=None, hair=(225, 225, 230), goggles=True, stripe=(200, 200, 200),
                              key="jones"))
    with Blur(c, 5.0):
        c.save()
        c.translate(-((scroll + 3000) * 1.6) % 1080, 0)
        grass_front(c, 1760, 78, (120, 110, 50))
        c.translate(1080, 0)
        grass_front(c, 1760, 78, (120, 110, 50))
        c.restore()
    series_tag(c)
    ex = (gx + Q.EXTRA[0] * s, gy + (Q.EXTRA[1] - R) * s)
    fw = (gx + Q.BIKE["front"][0] * s, gy - R * s)
    if t >= T_1970 - 0.05:
        u = out_back(prog(t, T_1970 - 0.05, T_1970 + 0.12))
        c.save()
        c.translate(W / 2, 400)
        c.scale(lerp(2, 1, u), lerp(2, 1, u))
        letters(c, "1970", 0, 0, font("title", 170), [(240, 150, 60), (226, 90, 50), (250, 200, 90), (120, 160, 90)], seed=9, rot_amp=5)
        c.restore()
    if T_EXTRA <= t < T_CANCEL:
        u = prog(t, T_EXTRA, T_EXTRA + 0.25)
        tape(c, 650, 760, 380, 76, -3, seed=21)
        hand(c, "extra wheel!", 840, 814, 58, INK, -3, "center")
        pts = P.resample(np.array([(700, 850), (640, 900), (ex[0] + 50, ex[1] - 70)], float), 8, closed=False)
        marker(c, pts[:max(2, int(len(pts) * u))], RED_D, 6, seed=22)
    if t >= T_BACK - 0.1:
        u = out_back(prog(t, T_BACK - 0.1, T_BACK + 0.15))
        for (cx, cy, rr, a0, a1, colr, sd) in ((ex[0], ex[1], Q.EXTRA_R * s + 40, -30, -150, BLUE, 23),
                                                (fw[0], fw[1], R * s + 34, 200, 330, RED, 24)):
            a = np.radians(np.linspace(a0, a0 + (a1 - a0) * u, 30))
            if abs(a1 - a0) * u < 10:
                continue
            ctr = np.stack([cx + rr * np.cos(a), cy + rr * np.sin(a)], 1)
            tg = np.gradient(ctr, axis=0)
            tg /= np.linalg.norm(tg, axis=1, keepdims=True)
            nn = np.stack([-tg[:, 1], tg[:, 0]], 1)
            body = np.vstack([ctr[:-3] + nn[:-3] * 12, [ctr[-4] + nn[-4] * 30, ctr[-1] + tg[-1] * 20, ctr[-4] - nn[-4] * 30], (ctr[:-3] - nn[:-3] * 12)[::-1]])
            piece(c, body, colr, 1.1, seed=sd)
        if T_BACK + 0.3 <= t < T_CANCEL:
            tape(c, 560, 470 + 60, 400, 70, 2, seed=25)
            hand(c, "spins backwards", 760, 580, 50, BLUE_D, 2, "center")
    if T_CANCEL - 0.05 <= t < T_RIDE + 0.5:
        u = out_back(prog(t, T_CANCEL - 0.05, T_CANCEL + 0.12))
        c.save()
        c.translate(W / 2, 640)
        c.scale(lerp(1.8, 1, u), lerp(1.8, 1, u))
        chip(c, "GYRO EFFECT = 0", 0, 0, font("title", 78), WHITE, INK, -2, 1.0, seed=26)
        c.restore()
    if t >= T_RIDE + 0.5:
        u = out_back(prog(t, T_RIDE + 0.5, T_RIDE + 0.68))
        c.save()
        c.translate(W / 2, 660)
        c.scale(lerp(1.8, 1, u), lerp(1.8, 1, u))
        chip(c, "STILL RIDEABLE.", 0, 0, font("title", 92), WHITE, BLUE, 3, 1.1, seed=27)
        c.restore()


# ---------------------------------------------------------------- scene 4: trail, on graph paper with pins and string
T_TRAIL = TL["08"]["start"] - 0.3
T_LOOK = word_t("08", "front")
T_LINE = word_t("09", "line")
T_HERE = word_t("09", "here")
T_TOUCH = word_t("10", "touches")
T_BEHIND = word_t("10", "behind")
T_TRAILW = word_t("10", "trail")
TB = dict(s=2.4, gx=-480, gy=1340)


def trail_pts():
    s, gx, gy = TB["s"], TB["gx"], TB["gy"]
    hub = np.array([gx + Q.BIKE["front"][0] * s, gy - R * s])
    top = np.array([gx + Q.BIKE["ht_top"][0] * s, gy + (Q.BIKE["ht_top"][1] - R) * s])
    axg = Q.steer_axis_ground()
    ground = np.array([gx + axg[0] * s, gy])
    top2 = top - (ground - top) * 0.35
    return hub, top2, ground, np.array([hub[0], gy])


def graph_paper(c, color=CREAM, ink=(120, 170, 210), a=0.45):
    piece(c, P.rect(-600, -600, W + 1200, H + 1200), color, 0, rim=False, shadow=False, seed=3)
    for i in range(-600, W + 601, 40):
        w = 2.2 if i % 200 == 0 else 1.0
        c.drawLine(i, -600, i, H + 600, skia.Paint(AntiAlias=True, StrokeWidth=w, Color=col(ink, a)))
    for j in range(-600, H + 601, 40):
        w = 2.2 if j % 200 == 0 else 1.0
        c.drawLine(-600, j, W + 600, j, skia.Paint(AntiAlias=True, StrokeWidth=w, Color=col(ink, a)))


def pin_in(c, p, color, t, t0, r=13):
    if t < t0:
        return
    u = out_back(prog(t, t0, t0 + 0.15), 2.5)
    c.save()
    c.translate(*p)
    c.scale(u, u)
    pushpin(c, 0, 0, color, r)
    c.restore()


def grow_string(c, a, b, color, t, t0, dur=0.35, w=4):
    if t < t0:
        return
    u = out_expo(prog(t, t0, t0 + dur))
    string(c, a, a + (b - a) * u, color, sag=0, w=w)


def scene_trail(c, t):
    tq = q12(t)
    graph_paper(c)
    s, gx, gy = TB["s"], TB["gx"], TB["gy"]
    bike_side(c, gx, gy, s, 0.2 + 0.05 * math.sin(tq * 2), 2.2, key="b4")
    piece(c, P.rect(-600, gy, W + 1200, 26), KRAFT2, 0.6, seed=40)
    hub, top2, ground, contact = trail_pts()
    grow_string(c, top2, ground, RED, t, T_LINE)
    pin_in(c, top2, RED, t, T_LINE - 0.05)
    pin_in(c, ground, RED, t, T_HERE)
    grow_string(c, hub, contact, BLUE, t, T_TOUCH)
    pin_in(c, hub, BLUE, t, T_TOUCH - 0.05)
    pin_in(c, contact, BLUE, t, T_TOUCH + 0.3)
    if t >= word_t("09", "steering"):
        tape(c, 450, 500, 500, 80, 3, seed=13)
        hand(c, "steering axis", 700, 556, 62, RED_D, 3, "center")
        u = prog(t, word_t("09", "steering"), word_t("09", "steering") + 0.3)
        pts = P.resample(np.array([(470, 590), (380, 640), (300, 676)], float), 8, closed=False)
        marker(c, pts[:max(2, int(len(pts) * u))], RED_D, 6, seed=7)
    if t >= T_TOUCH + 0.3:
        tape(c, 640, 980, 380, 70, -3, seed=15)
        hand(c, "tyre touches", 830, 1030, 50, BLUE_D, -3, "center")
        u = prog(t, T_TOUCH + 0.3, T_TOUCH + 0.6)
        pts = P.resample(np.array([(650, 1040), (520, 1200), (contact[0] + 20, gy - 20)], float), 8, closed=False)
        marker(c, pts[:max(2, int(len(pts) * u))], BLUE_D, 5, seed=9)
    if t >= T_BEHIND:
        u = out_expo(prog(t, T_BEHIND, T_BEHIND + 0.4))
        rx0, rx1 = contact[0] - 40, ground[0] + 40
        c.save()
        c.translate(lerp(-700, 0, u), 0)
        piece(c, P.rect(rx0 - 60, gy + 40, (rx1 - rx0) + 120, 70), YELLOW, 0.5, seed=41)
        for k in range(int((rx1 - rx0 + 120) / 12)):
            x = rx0 - 60 + 6 + k * 12
            L = 26 if k % 5 == 0 else 14
            c.drawLine(x, gy + 40, x, gy + 40 + L, skia.Paint(AntiAlias=True, StrokeWidth=2, Color=col(INK)))
        c.restore()
    if t >= T_TRAILW - 0.05:
        u = prog(t, T_TRAILW - 0.05, T_TRAILW + 0.2)
        marker(c, [(contact[0], gy + 130), (lerp(contact[0], ground[0], u), gy + 130)], INK, 6, seed=4)
        marker(c, [(contact[0], gy + 116), (contact[0], gy + 144)], INK, 6, seed=5)
        if u >= 1:
            marker(c, [(ground[0], gy + 116), (ground[0], gy + 144)], INK, 6, seed=6)
        v = out_back(prog(t, T_TRAILW, T_TRAILW + 0.18))
        c.save()
        c.translate(810, gy + 92)
        c.scale(lerp(1.8, 1, v), lerp(1.8, 1, v))
        c.translate(-810, -(gy + 92))
        tape(c, 600, gy + 50, 420, 80, -2, seed=12)
        hand(c, "TRAIL ≈ 6 cm", 810, gy + 108, 64, INK, -2, "center")
        c.restore()
    # an ant hauling a crumb along the ground strip
    ant(c, -60 + 55 * tq, gy, 1.3, "ant4")
    series_tag(c)


def cam_trail(t):
    u = out_expo(prog(t, T_TRAIL, T_TRAIL + 0.6))
    z = lerp(0.8, 1.0, u) + 0.12 * out_expo(prog(t, T_LOOK - 0.1, T_LOOK + 0.5)) - 0.12 * in_out(prog(t, T_LINE - 0.4, T_LINE + 0.3))
    fy = 1000 + 120 * out_expo(prog(t, T_BEHIND - 0.2, T_BEHIND + 0.4)) * (1 - prog(t, TL["11"]["start"] - 1.2, TL["11"]["start"] - 0.5))
    z += 0.18 * out_expo(prog(t, T_BEHIND - 0.2, T_BEHIND + 0.4)) * (1 - prog(t, TL["11"]["start"] - 1.2, TL["11"]["start"] - 0.5))
    return 540, fy, z, 0.0


# ---------------------------------------------------------------- scene 5: a shopping trolley, seen from above
T_CASTER = TL["11"]["start"] - 0.3
T_SWING = word_t("11", "swing")


def trolley_state(lt):
    """Heading and position of the trolley at local time lt (integrated, deterministic)."""
    dt = 1 / 60
    x, y, th = 0.0, 0.0, 0.0
    turn_t = T_SWING - T_CASTER - 0.35
    wheels = [0.0] * 4
    n = int(max(0, lt) / dt)
    for i in range(n):
        tt = i * dt
        th_target = 0.0 if tt < turn_t else math.radians(165)
        th += (th_target - th) * min(1, dt * 3.2)
        v = 330
        x += v * math.cos(th) * dt
        y += v * math.sin(th) * dt
        for k in range(4):
            d = th - wheels[k]
            wheels[k] += d * min(1, dt * (7.0 if tt < turn_t + 0.05 else 5.5))
    return x, y, th, wheels


def scene_caster(c, t):
    lt = q12(t - T_CASTER)
    x, y, th, wheels = trolley_state(lt)
    # supermarket floor (checker tiles), fixed to the world
    piece(c, P.rect(-3000, -3000, 8000, 8000), (238, 232, 214), 0, rim=False, shadow=False, seed=5)
    cx0, cy0 = 300 + x, 1000 + y
    tile = 180
    i0, j0 = int((cx0 - 1400) // tile), int((cy0 - 1400) // tile)
    for i in range(i0, i0 + 17):
        for j in range(j0, j0 + 17):
            if (i + j) % 2 == 0:
                piece(c, P.rect(i * tile + 4, j * tile + 4, tile - 8, tile - 8), (120, 186, 180), 0.04, seed=1000 + (i * 31 + j) % 97,
                      rim=False, shadow_k=0.4)
    c.save()
    c.translate(cx0, cy0)
    c.rotate(math.degrees(th))
    boil(c, "trolley", 0.8)
    Lw, Ww = 620, 420
    piece(c, P.rrect(-Lw / 2, -Ww / 2, Lw, Ww, 26), (196, 200, 208), 1.0, seed=60)
    piece(c, P.rrect(-Lw / 2 + 22, -Ww / 2 + 22, Lw - 44, Ww - 44, 16), (150, 156, 168), 0.15, seed=61)
    gp = skia.Paint(AntiAlias=True, StrokeWidth=4, Color=col((235, 238, 242)))
    for k in range(1, 10):
        xx = -Lw / 2 + 22 + (Lw - 44) * k / 10
        c.drawLine(xx, -Ww / 2 + 22, xx, Ww / 2 - 22, gp)
    for k in range(1, 6):
        yy = -Ww / 2 + 22 + (Ww - 44) * k / 6
        c.drawLine(-Lw / 2 + 22, yy, Lw / 2 - 22, yy, gp)
    piece(c, capsule((-Lw / 2 - 40, -Ww / 2 + 30), (-Lw / 2 - 40, Ww / 2 - 30), 30), RED, 0.9, seed=62)  # handle
    # some shopping, and a stowaway
    piece(c, P.rrect(-150, -120, 140, 100, 14), (250, 230, 110), 0.5, seed=63)  # cheese
    piece(c, P.ellipse(80, 60, 70, 40, 30, 0.3), (240, 140, 60), 0.5, seed=64)  # loaf
    piece(c, P.rrect(40, -140, 90, 150, 20), (90, 160, 220), 0.5, seed=65)  # milk
    c.restore()
    pigeon(c, cx0 - 120 * math.cos(th) + 20, cy0 - 120 * math.sin(th) + 40, 1.1, "pg5", look=12 * math.sin(lt * 4))
    # casters at the four corners: pivot pin + wheel that trails behind it
    for k, (dx, dy) in enumerate(((Lw / 2 - 40, -Ww / 2 + 20), (Lw / 2 - 40, Ww / 2 - 20), (-Lw / 2 + 40, -Ww / 2 + 20), (-Lw / 2 + 40, Ww / 2 - 20))):
        px = cx0 + dx * math.cos(th) - dy * math.sin(th)
        py = cy0 + dx * math.sin(th) + dy * math.cos(th)
        a = wheels[k]
        wx, wy = px - 46 * math.cos(a), py - 46 * math.sin(a)
        c.save()
        c.translate(wx, wy)
        c.rotate(math.degrees(a))
        piece(c, P.rrect(-38, -16, 76, 32, 12), TIRE, 1.2, seed=70 + k)
        c.restore()
        piece(c, capsule((px, py), (wx, wy), 16), shade(STEEL, 0.6), 1.3, seed=74 + k)
        brad(c, px, py, 10)
    if t >= T_SWING + 0.2:
        lx, ly = cx0 - 120, cy0 - 420
        tape(c, lx - 310, ly - 50, 620, 80, -2, seed=31)
        hand(c, "the wheel trails behind its pivot", lx, ly + 4, 48, INK, -2, "center")
    series_tag(c)


def cam_caster(t):
    x, y, th, _ = trolley_state(t - T_CASTER)
    u = out_expo(prog(t, T_CASTER, T_CASTER + 0.6))
    return 300 + x, 1000 + y - 60, lerp(1.6, 1.3, u), 0.0


# ---------------------------------------------------------------- scene 6: steering into the fall (rear view)
T_STEER = TL["12"]["start"] - 0.3
T_TIP = word_t("12", "tip")
T_SWINGS = word_t("13", "swings")
T_STEERS = word_t("14", "steers")
T_UP = word_t("14", "upright")
T_CONST = TL["15"]["start"]


def steer_state(t):
    """lean (deg, - = left), steer (deg), sideways shift of the contact point (px)."""
    lean = -18 * in_out(prog(t, T_TIP - 0.6, T_TIP + 0.6))
    steer = -16 * out_expo(prog(t, T_SWINGS - 0.1, T_SWINGS + 0.4))
    back = in_out(prog(t, T_STEERS - 0.1, T_UP + 0.2))
    lean *= 1 - back
    steer *= 1 - in_out(prog(t, T_UP - 0.2, T_UP + 0.5))
    shift = -150 * back
    if t > T_CONST - 0.3:  # the constant little wobble-and-catch
        k = t - (T_CONST - 0.3)
        lean += 5 * math.sin(k * 3.4) * min(1, k)
        steer += -7 * math.sin(k * 3.4 + 0.6) * min(1, k)
    return lean, steer, shift


def scene_steer(c, t):
    tq = q12(t)
    lean, steer, shift = steer_state(tq)
    piece(c, P.rect(-600, -600, W + 1200, H + 1200), SKY, 0, rim=False, shadow=False, seed=6)
    hz = 940
    with Blur(c, 2.6):
        cloud(c, 820, 360, 0.6, "c4")
        cloud(c, 160, 520, 0.5, "c5")
        hill(c, hz, 70, GREEN1, 21, 0.6, 1.2)
        hill(c, hz + 40, 40, GREEN2, 22, 0.6, 2.8)
    road = np.array([[W / 2 - 40, hz + 30], [W / 2 + 40, hz + 30], [W + 700, H + 400], [-700, H + 400]])
    piece(c, road, ROAD, 0.4, seed=60)
    ph = (tq * 0.9) % 1.0
    for k in range(-1, 8):
        a, b = (k + ph) / 7, (k + ph + 0.45) / 7
        if b <= 0 or a >= 1.3:
            continue
        a, b = max(a, 0), b
        f0, f1 = a ** 1.8, b ** 1.8
        y0, y1 = hz + 30 + (H + 300 - hz) * f0, hz + 30 + (H + 300 - hz) * f1
        w0, w1 = 3 + 22 * f0, 3 + 22 * f1
        piece(c, np.array([[W / 2 - w0, y0], [W / 2 + w0, y0], [W / 2 + w1, y1], [W / 2 - w1, y1]]), (240, 236, 222), 0.1,
              seed=61 + (k % 7))
    with Blur(c, 1.2):
        snail(c, W / 2 + 140 - 4 * tq, hz + 90, 0.35, "sn4")
    gx, gy, s4 = W / 2 + 30 + shift, 1520, 1.5
    bike_rear(c, gx, gy, s4, lean=lean, steer=steer, key="r4", pedal=tq * 6)
    a = math.radians(lean)
    lx, ly = 0, -2 * R - 110
    com = np.array([gx + s4 * (lx * math.cos(a) - ly * math.sin(a)), gy + s4 * (lx * math.sin(a) + ly * math.cos(a))])
    if t >= T_STEER + 0.6:
        string(c, com, (com[0], gy + 20), INK, 0, 3)
        piece(c, np.array([[com[0] - 16, gy + 10], [com[0] + 16, gy + 10], [com[0], gy + 50]]), (212, 172, 72), 0.4, seed=62)
        pushpin(c, *com, YELLOW, 16)
        tape(c, 40, 1000, 300, 64, -4, seed=14)
        hand(c, "your weight", 190, 1044, 48, INK, -4, "center")
    # where the tyre touches: a blue pin that slides back under the plumb bob
    pushpin(c, gx, gy + 6, BLUE, 12)
    if T_SWINGS <= t < T_UP + 0.6:
        u = out_back(prog(t, T_SWINGS, T_SWINGS + 0.25))
        c.save()
        c.translate(530, 1550)
        c.scale(u, u)
        c.translate(-530, -1550)
        piece(c, P.arrow_shape((820, 1545), (250, 1520), bend=-60, w=42, head=86), RED, 1.2, seed=63)
        c.restore()
    if t >= T_STEERS - 0.05:
        u = out_back(prog(t, T_STEERS - 0.05, T_STEERS + 0.12))
        c.save()
        c.translate(W / 2, 470)
        c.scale(lerp(1.8, 1, u), lerp(1.8, 1, u))
        chip(c, "STEER INTO THE FALL", 0, 0, font("title", 76), WHITE, RED, 2, 0.9, seed=6)
        c.restore()
    if t >= T_CONST + 0.6:
        # thought bubble: the rider is thinking about ice cream, not balance
        u = out_back(prog(t, T_CONST + 0.6, T_CONST + 0.8))
        bx, by = com[0] + 250, com[1] - 380
        c.save()
        c.translate(bx, by)
        c.scale(u, u)
        for k, (dx, dy, r) in enumerate(((-150, 230, 14), (-120, 180, 22))):
            piece(c, circle(dx, dy, r, 20), WHITE, 0.8, seed=80 + k)
        cloud(c, 0, 40, 1.1, "thought", string_top=False)
        piece(c, np.array([[-20, 10], [20, 10], [0, 70]]), (214, 160, 90), 0.3, seed=83)
        piece(c, circle(0, 0, 24, 24), PINK, 0.4, seed=84)
        c.restore()
    series_tag(c)


def cam_steer(t):
    u = out_expo(prog(t, T_STEER, T_STEER + 0.6))
    z = lerp(1.3, 1.0, u) + 0.06 * in_out(prog(t, T_TIP - 0.5, T_STEERS))
    return 540, lerp(1100, 1000, u), z, 0.0


# ---------------------------------------------------------------- scene 7: the riderless bike
T_GHOST = TL["16"]["start"] - 0.3
T_NOBODY = word_t("17", "nobody")
T_CATCH = word_t("17", "catches") - 0.15


def scene_ghost(c, t):
    tq = q12(t)
    scroll = 380 * tq
    piece(c, P.rect(-600, -600, W + 1200, H + 1200), (250, 214, 170), 0, rim=False, shadow=False, seed=7)
    with Blur(c, 2.6):
        sun(c, 210, 520, 120, t=tq)
        c.save()
        c.translate(-(scroll * 0.15) % 700, 0)
        hill(c, 1000, 110, (232, 160, 110), 31, 0.6)
        c.translate(700, 0)
        hill(c, 1000, 110, (232, 160, 110), 31, 0.6)
        c.restore()
    with Blur(c, 1.2):
        base = -(scroll * 0.55)
        hs = [(0, 230, 240, (150, 110, 170), (80, 50, 90), 2), (300, 200, 180, (240, 190, 110), RED_D, 1),
              (560, 210, 220, (120, 170, 210), (60, 80, 130), 2), (820, 180, 200, CORAL, (110, 50, 50), 1)]
        n0 = int(math.floor(-base / PERIOD)) - 1
        for n in range(n0, n0 + 3):
            for i, (x, w, h, b, r, wn) in enumerate(hs):
                hx = base + n * PERIOD + x + 40
                if -300 < hx < W + 60:
                    house(c, hx, 1240, w, h, b, r, f"g{i}", windows=wn)
    curb(c, 1330)
    c.save()
    c.translate(-(scroll % 200), 0)
    road_side(c, 1370)
    c.restore()
    # the kid stays behind on the kerb, so they slide away with the street
    kid_sitting(c, 160 - max(0.0, scroll - 380 * q12(T_GHOST + 1.2)), 1330, 1.0, "sit5")
    for i, (yy, L) in enumerate(((1250, 300), (1330, 200), (1420, 260))):
        jit = 30 * math.sin(tq * 9 + i * 2)
        piece(c, P.wobble(P.resample(P.rrect(330 + jit, yy, L, 14, 7), 10), 0.8, i), WHITE, 0.5, seed=210 + i, alpha=0.9)
    pg = lambda cc: pigeon(cc, Q.BIKE["saddle"][0], Q.BIKE["saddle"][1] - 10, 0.65, "pg7", look=8 * math.sin(tq * 6))
    bike_side(c, 470, 1560, 1.15, wheel_ang=scroll / (R * 1.15), crank=1.2, key="b5", after=pg)
    if t >= T_NOBODY - 0.05:
        u = out_back(prog(t, T_NOBODY - 0.05, T_NOBODY + 0.12))
        c.save()
        c.translate(W / 2 + 60, 420)
        c.scale(lerp(1.8, 1, u), lerp(1.8, 1, u))
        chip(c, "NO RIDER.", 0, 0, font("title", 110), INK, WHITE, -4, 1.0, seed=7)
        c.restore()
    series_tag(c)


def cam_ghost(t):
    u = out_expo(prog(t, T_GHOST, T_GHOST + 0.6))
    return lerp(700, 540, u), 1000, lerp(1.3, 1.0, u) + 0.05 * prog(t, T_GHOST + 0.6, T_CATCH), 0.0


def scene_ghost_rear(c, t):
    tq = q12(t)
    k = max(0.0, tq - T_CATCH - 0.2)
    lean = -13 * math.exp(-k * 0.9) * math.cos(k * 4.2)
    steer = 15 * math.exp(-k * 0.9) * math.sin(k * 4.2 - 0.9)
    piece(c, P.rect(-600, -600, W + 1200, H + 1200), (250, 214, 170), 0, rim=False, shadow=False, seed=8)
    hz = 940
    with Blur(c, 2.6):
        hill(c, hz, 70, (232, 160, 110), 41, 0.6, 1.2)
        hill(c, hz + 40, 40, (200, 120, 96), 42, 0.6, 2.8)
    road = np.array([[W / 2 - 40, hz + 30], [W / 2 + 40, hz + 30], [W + 700, H + 400], [-700, H + 400]])
    piece(c, road, ROAD, 0.4, seed=90)
    ph = (tq * 0.9) % 1.0
    for kk in range(-1, 8):
        a, b = max(0, (kk + ph) / 7), (kk + ph + 0.45) / 7
        if b <= 0:
            continue
        f0, f1 = a ** 1.8, b ** 1.8
        y0, y1 = hz + 30 + (H + 300 - hz) * f0, hz + 30 + (H + 300 - hz) * f1
        w0, w1 = 3 + 22 * f0, 3 + 22 * f1
        piece(c, np.array([[W / 2 - w0, y0], [W / 2 + w0, y0], [W / 2 + w1, y1], [W / 2 - w1, y1]]), (240, 236, 222), 0.1, seed=91 + kk % 7)
    bike_rear(c, W / 2, 1500, 1.6, lean=lean, steer=steer, key="r7", rider=False)
    # the pigeon, still on the saddle, holding on
    a = math.radians(lean)
    sx, sy = 0, -2 * R - 40
    px, py = W / 2 + 1.6 * (sx * math.cos(a) - sy * math.sin(a)), 1500 + 1.6 * (sx * math.sin(a) + sy * math.cos(a))
    pigeon(c, px - 10, py, 0.9, "pg7r", look=-lean)
    if t >= T_CATCH + 0.6:
        u = out_back(prog(t, T_CATCH + 0.6, T_CATCH + 0.78))
        c.save()
        c.translate(W / 2, 520)
        c.scale(lerp(1.8, 1, u), lerp(1.8, 1, u))
        chip(c, "IT CATCHES ITSELF.", 0, 0, font("title", 78), WHITE, BLUE, 3, 0.9, seed=8)
        c.restore()
    series_tag(c)


def cam_ghost_rear(t):
    u = out_expo(prog(t, T_CATCH, T_CATCH + 0.5))
    return 540, 1000, lerp(1.4, 1.0, u), 0.0


# ---------------------------------------------------------------- scene 8: 2011, the bike with no gyro and no trail
T_2011 = TL["18"]["start"] - 0.3
T_Y2011 = word_t("18", "2011")
T_NOGYRO = word_t("18", "gyro")
T_NOTRAIL = word_t("18", "trail")
T_BAL = word_t("18", "balanced")
T_WEIGHT = word_t("18", "weight")
BLUEPRINT = (36, 78, 140)


def scene_2011(c, t):
    tq = q12(t)
    c.save()
    c.translate(-(tq * 120) % 200, 0)
    graph_paper(c, BLUEPRINT, (200, 220, 255), 0.35)
    c.restore()
    s, gx, gy = 1.35, 190, 1450
    wa = tq * 3.0
    k = max(0.0, tq - T_BAL + 0.4)
    tilt = 4 * math.exp(-k * 1.2) * math.sin(k * 6) if tq > T_BAL - 0.4 else 0.0
    weight = lambda cc: (piece(cc, capsule(Q.BIKE["ht_top"], (470, -230), 12), shade(STEEL, 0.6), 0.4, seed=95),
                         piece(cc, P.rrect(440, -290, 110, 90, 12), (90, 92, 104), 0.7, seed=96) if t >= T_WEIGHT - 0.1 else None,
                         ink_text(cc, "kg", 495, -232, font("title", 34), WHITE, "center") if t >= T_WEIGHT - 0.1 else None)
    bike_side(c, gx, gy, s, wheel_ang=wa, crank=tq * 4, frame=(240, 240, 236), key="b8", extra=-wa * 1.6, after=weight, tilt=tilt)
    piece(c, P.rect(-600, gy, W + 1200, 22), (220, 230, 250), 0.5, seed=97)
    if t >= T_Y2011 - 0.05:
        u = out_back(prog(t, T_Y2011 - 0.05, T_Y2011 + 0.12))
        c.save()
        c.translate(W / 2, 400)
        c.scale(lerp(2, 1, u), lerp(2, 1, u))
        letters(c, "2011", 0, 0, font("title", 170), [WHITE, YELLOW, WHITE, (255, 236, 200)], seed=19, rot_amp=5)
        c.restore()
        tape(c, 300, 520, 480, 60, 1.5, seed=33)
        hand(c, "Kooijman et al., Science", 540, 562, 40, INK, 1.5, "center", "neat")
    if t >= T_NOGYRO - 0.05:
        u = out_back(prog(t, T_NOGYRO - 0.05, T_NOGYRO + 0.12))
        c.save()
        c.translate(300, 720)
        c.scale(lerp(1.8, 1, u), lerp(1.8, 1, u))
        chip(c, "NO GYRO", 0, 0, font("title", 70), WHITE, RED, -4, 0.9, seed=34)
        c.restore()
    if t >= T_NOTRAIL - 0.05:
        u = out_back(prog(t, T_NOTRAIL - 0.05, T_NOTRAIL + 0.12))
        c.save()
        c.translate(780, 720)
        c.scale(lerp(1.8, 1, u), lerp(1.8, 1, u))
        chip(c, "NO TRAIL", 0, 0, font("title", 70), WHITE, RED, 3, 0.9, seed=35)
        c.restore()
    if t >= T_BAL - 0.05:
        u = out_back(prog(t, T_BAL - 0.05, T_BAL + 0.12))
        c.save()
        c.translate(W / 2, 880)
        c.scale(lerp(1.8, 1, u), lerp(1.8, 1, u))
        chip(c, "STILL BALANCED.", 0, 0, font("title", 84), WHITE, BLUE, -2, 1.0, seed=36)
        c.restore()
    if t >= T_WEIGHT:
        wx, wy = gx + 495 * s, gy + (-245 - R) * s
        u = prog(t, T_WEIGHT, T_WEIGHT + 0.3)
        tape(c, 640, 1000, 360, 70, -3, seed=37)
        hand(c, "weight, just here", 820, 1050, 48, INK, -3, "center")
        pts = P.resample(np.array([(900, 1075), (930, 1120), (wx + 30, wy - 70)], float), 8, closed=False)
        marker(c, pts[:max(2, int(len(pts) * u))], YELLOW, 7, seed=38)
    series_tag(c)


def cam_2011(t):
    u = out_expo(prog(t, T_2011, T_2011 + 0.6))
    zw = out_expo(prog(t, T_WEIGHT - 0.1, T_WEIGHT + 0.4))
    return lerp(540, 760, zw), lerp(1000, 1080, zw), lerp(1.3, 1.0, u) + 0.25 * zw, 0.0


# ---------------------------------------------------------------- scene 9: wrap-up on the street, then the end card
T_WRAP = TL["19"]["start"] - 0.3
T_LITTLE = word_t("19", "little")
T_YOU = word_t("20", "you")
T_END = TL["21"]["start"] - 0.3


def scene_wrap(c, t):
    tq = q12(t)
    scroll = 420 * tq + 2000
    street(c, scroll, tq)
    head = lambda cc: pigeon(cc, 196, -418, 0.7, "pgw", look=10 * math.sin(tq * 5))  # the pigeon has moved onto the helmet
    bike_side(c, 250, 1520, 1.15, wheel_ang=scroll / (R * 1.15), crank=tq * 7.0, rider=kid_rider(), key="b1", after=head)
    with Blur(c, 5.0):
        c.save()
        c.translate(-(scroll * 1.6) % 1080, 0)
        grass_front(c, 1760, 77)
        c.translate(1080, 0)
        grass_front(c, 1760, 77)
        c.restore()
    series_tag(c)
    if t >= T_LITTLE - 0.05:
        u = out_back(prog(t, T_LITTLE - 0.05, T_LITTLE + 0.12))
        c.save()
        c.translate(W / 2, 380)
        c.scale(lerp(1.8, 1, u), lerp(1.8, 1, u))
        chip(c, "LOTS OF LITTLE EFFECTS", 0, 0, font("title", 66), INK, WHITE, -2, 0.9, seed=41)
        c.restore()
    if t >= T_YOU - 0.05:
        u = out_back(prog(t, T_YOU - 0.05, T_YOU + 0.14), 2.6)
        c.save()
        c.translate(W / 2, 560)
        c.scale(lerp(2.2, 1, u), lerp(2.2, 1, u))
        letters(c, "+ YOU", 0, 0, font("title", 150), [RED, (240, 80, 60), RED], seed=42, rot_amp=5, fg=WHITE)
        c.restore()


def cam_wrap(t):
    u = out_expo(prog(t, T_WRAP, T_WRAP + 0.6))
    return 540, 1000, lerp(1.3, 1.0, u) + 0.06 * in_out(prog(t, T_YOU - 0.3, T_END)), 0.0


def scene_end(c, t):
    tq = q12(t)
    piece(c, P.rect(-600, -600, W + 1200, H + 1200), KRAFT, 0, rim=False, shadow=False, seed=9)
    gp = skia.Paint(AntiAlias=True, StrokeWidth=1.5, Color=col(KRAFT2, 0.45))
    for i in range(-360, W + 400, 90):
        c.drawLine(i, -400, i, H + 400, gp)
    for j in range(-360, H + 400, 90):
        c.drawLine(-400, j, W + 400, j, gp)
    lt = t - T_END
    pal = [WHITE, YELLOW, WHITE, (255, 236, 200)]
    for k, (txt, y, sz, sd) in enumerate((("THE PHYSICS", 470, 82, 51), ("OF EVERYDAY", 610, 82, 52), ("THINGS", 780, 130, 53))):
        t0 = T_END + 0.15 + 0.22 * k
        if t >= t0:
            pop = [out_back(prog(t, t0 + 0.02 * i, t0 + 0.02 * i + 0.15), 2.6) if t >= t0 + 0.02 * i else 0 for i in range(len(txt))]
            letters(c, txt, W / 2, y, font("title", sz), pal if k < 2 else [RED, (240, 80, 60)], seed=sd, rot_amp=4,
                    fg=INK if k < 2 else WHITE, pop=pop)
    if lt > 1.0:
        u = out_back(prog(lt, 1.0, 1.2))
        c.save()
        c.translate(W / 2, 980)
        c.scale(u, u)
        chip(c, "FOLLOW FOR MORE", 0, 0, font("title", 64), WHITE, BLUE, -2, 0.9, seed=54)
        c.restore()
    # a little bike rides across the bottom, the pigeon perched on its saddle
    bx = -500 + 330 * q12(lt)
    pg = lambda cc: pigeon(cc, Q.BIKE["saddle"][0], Q.BIKE["saddle"][1] - 10, 0.65, "pge", look=6)
    bike_side(c, bx, 1450, 0.8, wheel_ang=(bx + 500) / (R * 0.8), crank=1.0, key="be", after=pg)
    piece(c, P.rect(-600, 1450, W + 1200, 20), KRAFT2, 0.4, seed=55)
    tape(c, 300, 1180, 480, 64, 1.5, seed=56)
    hand(c, "Ep. 02 · Bicycles", W / 2, 1224, 44, INK, 1.5, "center", "neat")


def cam_end(t):
    u = out_expo(prog(t, T_END, T_END + 0.6))
    return 540, 960, lerp(1.25, 1.0, u), 0.0


# ---------------------------------------------------------------- compositing
SCENES = [(0.0, scene_street, cam_hook), (T_MYTH, scene_myth, cam_myth), (T_JONES, scene_jones, cam_jones),
          (T_TRAIL, scene_trail, cam_trail), (T_CASTER, scene_caster, cam_caster), (T_STEER, scene_steer, cam_steer),
          (T_GHOST, scene_ghost, cam_ghost), (T_CATCH, scene_ghost_rear, cam_ghost_rear), (T_2011, scene_2011, cam_2011),
          (T_WRAP, scene_wrap, cam_wrap), (T_END, scene_end, cam_end)]
HITS = [T_GYRO + 0.1, T_NOPE + 0.45, T_RIDE + 0.6, T_1970 + 0.08, T_CANCEL + 0.08, T_TRAILW + 0.1, T_STEERS + 0.08,
        T_NOBODY + 0.08, T_Y2011 + 0.08, T_BAL + 0.08, T_YOU + 0.1]



def draw_scene(c, idx, t):
    _, fn, cam = SCENES[idx]
    c.save()
    apply_cam(c, cam(t), shake(t, HITS))
    fn(c, t)
    c.restore()


def frame(t):
    P.CLOCK.t = t
    s = new_surface()
    c = s.getCanvas()
    c.clear(skia.ColorWHITE)
    idx = max(i for i, (t0, _, _) in enumerate(SCENES) if t >= t0)
    t0 = SCENES[idx][0]
    if idx > 0 and t < t0 + WIPE:
        # the next set is a sheet slid in over the last one (paper wipe from the right)
        u = out_expo(prog(t, t0, t0 + WIPE))
        draw_scene(c, idx - 1, t)
        x = lerp(W * 1.05, 0, u)
        sp = skia.Paint(AntiAlias=True, Color=skia.Color4f(0, 0, 0, 0.45), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
        c.drawRect(skia.Rect(x - 30, -50, x + W + 50, H + 50), sp)
        c.save()
        c.clipRect(skia.Rect(x, 0, x + W, H))
        c.translate(x, 0)
        c.rotate(-1.5 * (1 - u))
        draw_scene(c, idx, t)
        c.restore()
    else:
        draw_scene(c, idx, t)
    captions(c, t)
    warm_light(c)
    vignette(c)
    img = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    return np.ascontiguousarray(img[:, :, :3])


def _job(i):
    return frame(i / FPS).tobytes()


def render(procs=4, name="ep02_bicycles"):
    import sound
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    bdir = os.path.join(HERE, "build")
    wav = sound.render_audio(os.path.join(bdir, "mix.wav"), sys.modules[__name__])
    silent = os.path.join(bdir, f"{name}_video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    frames = range(int(DURATION * FPS))
    with Pool(procs) as pool:
        for k, buf in enumerate(pool.imap(_job, frames, chunksize=2)):
            ff.stdin.write(buf)
            if k % 48 == 0:
                print(f"frame {k}/{len(frames)}", flush=True)
    ff.stdin.close()
    ff.wait()
    out = os.path.join(HERE, "out", f"{name}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    if "--still" in sys.argv:
        from PIL import Image
        d = os.path.join(HERE, "build", "stills")
        os.makedirs(d, exist_ok=True)
        for s in sys.argv[sys.argv.index("--still") + 1].split(","):
            p = os.path.join(d, f"t{float(s):05.2f}.png")
            Image.fromarray(frame(float(s))).save(p)
            print(p)
    else:
        render(int(os.environ.get("PROCS", "4")))
