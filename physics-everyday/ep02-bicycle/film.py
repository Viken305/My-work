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
DURATION = 22.5


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
            brk = w[-1] in ".,:?" and len(cur) >= 3 or len(cur) >= 7 or w == "Nope."
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


# ---------------------------------------------------------------- compositing
SCENES = [(0.0, scene_street, cam_hook), (T_MYTH, scene_myth, cam_myth), (T_JONES, scene_jones, cam_jones)]
HITS = [T_GYRO + 0.1, T_NOPE + 0.45, T_RIDE + 0.6, T_1970 + 0.08, T_CANCEL + 0.08]


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


def render(procs=4, name="ep02_test20"):
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
