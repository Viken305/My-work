"""Ep. 04 'Why is the sky blue?' -- flat-vector explainer, 9:16, 30 fps, one continuous journey:
meadow -> up into space -> the Sun -> light splits into colours -> waves race to Earth -> into the air -> molecules
-> scattering -> back out to the sky -> violet? -> sunset -> Mars -> end.

  python3 voiceover.py        # narration -> build/vo
  python3 film.py             # -> out/ep04_sky.mp4
  python3 film.py --still 3,40
"""
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import captions as CAP  # noqa: E402
import kz as K  # noqa: E402
from kz import H, W, clamp, io, lerp, ob, oc, oe, prog, ss  # noqa: E402

FPS = 30
TL = json.load(open(os.path.join(HERE, "build", "vo", "timeline.json")))
DURATION = TL["20"]["start"] + TL["20"]["dur"] + 3.6
STARS = K.Stars()


def words_of(key):
    it = TL[key]
    ws = it["text"].split()
    n = sum(len(w) + 1 for w in ws)
    out, acc = [], 0
    for w in ws:
        out.append((w, it["start"] + it["dur"] * (acc / n) * 0.95))
        acc += len(w) + 1
    return out


def wt(key, prefix, nth=0):
    k = 0
    for w, s in words_of(key):
        if w.lower().strip(".,?!:'").startswith(prefix.lower()):
            if k == nth:
                return s
            k += 1
    raise KeyError((key, prefix))


def st(key):
    return TL[key]["start"]


def en(key):
    return TL[key]["start"] + TL[key]["dur"]


# ---------------------------------------------------------------- caption pages
def build_pages():
    out = []
    for key in TL:
        if key == "20":
            continue
        ws = words_of(key)
        cur = []
        for i, (w, s) in enumerate(ws):
            cur.append((w, s))
            left = len(ws) - 1 - i
            brk = (w[-1] in ".,?:" and len(cur) >= 3 or len(cur) >= 8) and (left == 0 or left > 2 or w[-1] in ".?")
            if brk or i == len(ws) - 1:
                out.append(cur)
                cur = []
    res = []
    for i, pg in enumerate(out):
        nxt = out[i + 1][0][1] if i + 1 < len(out) else pg[-1][1] + 1.5
        end = min(pg[-1][1] + 1.4, nxt - 0.06)
        res.append((pg[0][1] - 0.1, end, CAP.layout(pg)))
    return res


PAGES = build_pages()


def page_at(t):
    for t0, t1, words in PAGES:
        if t0 <= t < t1:
            return t0, t1, words
    return None


# ---------------------------------------------------------------- segment boundaries
SEG = dict(meadow=0.0, sun=st("03") - 0.35, travel=st("05") - 0.3, atmo=st("06") - 0.25, air=st("07") - 0.45,
           pinball=st("11") - 0.3, bluesky=st("12") - 0.35, violet=st("13") - 0.3, sunset=st("15") - 0.4, mars=st("18") - 0.3,
           end=st("19") - 0.35)
SEG_ORDER = ["meadow", "sun", "travel", "atmo", "air", "pinball", "bluesky", "violet", "sunset", "mars", "end"]
# how each segment is entered: (kind, duration, focus point)
ENTRY = dict(sun=("cut_space", 0.0, None), travel=("none", 0.0, None), atmo=("none", 0.0, None), air=("zoom_in", 0.7, (330, 1330)),
             pinball=("zoom_out", 0.7, (540, 820)), bluesky=("zoom_out", 0.7, (540, 900)), violet=("none", 0.0, None),
             sunset=("none", 0.0, None), mars=("none", 0.0, None), end=("zoom_out", 0.7, (540, 960)))


# ---------------------------------------------------------------- shared: the meadow
def meadow(c, t, cam_y=-1500.0, sky=None, sun_pos=None, sunset=0.0, zoom=1.0):
    """The ground-level world. World y=0 is the ground line; negative is up. sunset 0..1 recolours everything."""
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(zoom, zoom)
    c.translate(-W / 2, -H / 2 - cam_y)
    day = [(0, K.SKY_BOT), (-1800, K.SKY_TOP), (-4500, (30, 60, 150)), (-6500, K.NAVY), (-8200, K.SPACE)]
    dusk = [(0, (255, 170, 90)), (-900, (240, 100, 110)), (-2200, (110, 60, 140)), (-4500, (40, 30, 90)), (-8200, K.SPACE)]
    stops = [(y, K.mix(a, b[1], sunset)) for (y, a), b in zip(day, dusk)]
    y0, y1 = stops[0][0] + 600, stops[-1][0] - 3000
    pos = [(y0 - y) / (y0 - y1) for y, _ in stops]
    sh = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [K.c4(cc) for _, cc in stops], pos)
    c.drawRect(skia.Rect(-3000, y1 - 20000, 4000, y0 + 3000), skia.Paint(Shader=sh))
    alt = -cam_y
    STARS_A = prog(alt, 4500, 8000) + 0.6 * sunset * prog(alt, 300, 2000)
    c.restore()
    if STARS_A > 0:
        STARS.draw(c, t, (0, cam_y * 0.15), STARS_A)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(zoom, zoom)
    c.translate(-W / 2, -H / 2 - cam_y)
    if sun_pos is not None:
        sx, sy = sun_pos
        K.sun(c, sx, sy, 120, t, color=K.mix(K.SUN_Y, (255, 130, 70), sunset), corona=1.0 - 0.5 * sunset)
    for k, (x, y, s) in enumerate(((180, -950, 70), (860, -1450, 90), (420, -2300, 110), (150, -3300, 80), (900, -800, 55))):
        cc = K.mix((252, 253, 255), (255, 190, 170), sunset)
        K.cloud(c, x + 18 * math.sin(t * 0.2 + k), y, s, color=cc, seed=k)
    g1 = K.mix((90, 200, 140), (120, 80, 110), sunset * 0.8)
    g2 = K.mix(K.GRASS, (90, 60, 90), sunset * 0.8)
    g3 = K.mix(K.GRASS_D, (60, 40, 70), sunset * 0.8)
    K.hill(c, [-170, -240, -200, -260, -190, -230], -200, 1300, 900, g1)
    for k, x in enumerate((90, 210, 860, 990)):
        K.tree(c, x, -205 + 15 * math.sin(k * 2.0), 130, K.mix((46, 170, 110), (80, 50, 90), sunset * 0.8), t=t, seed=k)
    K.hill(c, [-90, -120, -70, -110, -60], -200, 1300, 900, g2)
    K.hill(c, [-20, -70, -95, -60, -10], -200, 1300, 900, g3)
    eye = K.stargazer(c, 540, -88, 150, t, shirt=K.mix((255, 196, 70), (240, 140, 90), sunset * 0.6))
    c.restore()
    # eye position in screen coords
    ex = W / 2 + (eye[0] - W / 2) * zoom
    ey = H / 2 + (eye[1] - cam_y - H / 2) * zoom
    return ex, ey


# ---------------------------------------------------------------- 1. meadow -> up to space
def seg_meadow(c, t, words):
    up = io(prog(t, wt("02", "up") - 0.2, wt("02", "sun") + 0.6))
    cam = lerp(-1500, -10160, up)
    meadow(c, t, cam, sun_pos=(720, -9560))
    # a curious photon peeks from behind a cloud near the start
    if t < 4.5:
        a = ss(prog(t, 1.2, 1.8)) * (1 - ss(prog(t, 4.0, 4.4)))
        K.photon(c, 930 + 30 * math.sin(t), 640 + 20 * math.sin(t * 1.3), 26, K.SUN_Y, t, look=(-1, 0.6), a=a, seed=3)


def blue_override(color=K.SPEC["blue"]):
    def f(c, wd, t, a):
        if t < wd.t0:
            return False
        since = t - wd.t0
        cc = K.mix(K.WHITE, color, K.ss(since / 0.25))
        K.text(c, wd.s, wd.x, wd.y - 10 * math.exp(-since * 4) * abs(math.sin(since * 14)), CAP.SIZE, cc, a, "left", 900, 0.3)
        return True
    return f


# ---------------------------------------------------------------- 2. the Sun, white light, the colours, the waves
SUN_XY = (120, 640)


def space_bg(c, t, off=(0, 0), streak=0.0):
    sh = skia.GradientShader.MakeRadial(skia.Point(W * 0.3, H * 0.35), H, [K.c4(K.NAVY2), K.c4(K.SPACE)])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh))
    STARS.draw(c, t, off, 1.0, streak)


def white_word(words, key="white"):
    for wd in words or []:
        if wd.key == key:
            return wd
    return None


FAN = [(860, 360 + k * 105) for k in range(6)]
WAVE_Y = dict(red=640, blue=1180)


def seg_sun(c, t, words):
    space_bg(c, t)
    K.sun(c, *SUN_XY, 300, t)
    t3 = st("03")
    wd = white_word(words)
    if wd is not None:
        PRISM_POS[0] = (wd.x, wd.y - 20, wd.x + wd.w)
    px0, py, px1 = PRISM_POS[0]
    # white beam from the Sun into the word 'White'
    u = oe(prog(t, t3 - 0.1, t3 + 0.45))
    fade = 1 - ss(prog(t, st("04") - 0.2, st("04") + 0.6))
    if u > 0 and fade > 0:
        bx0, by0 = SUN_XY[0] + 280, SUN_XY[1] + 120
        ex, ey = lerp(bx0, px0 + 20, u), lerp(by0, py, u)
        c.drawLine(bx0, by0, ex, ey, skia.Paint(AntiAlias=True, StrokeWidth=34, Color=K.col(K.WHITE, 0.25 * fade),
                                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16)))
        c.drawLine(bx0, by0, ex, ey, skia.Paint(AntiAlias=True, StrokeWidth=12, Color=K.col(K.WHITE, 0.95 * fade), StrokeCap=skia.Paint.kRound_Cap))
    # rainbow fan out of the word
    v = oe(prog(t, t3 + 0.45, t3 + 1.1))
    for k, (name, cc) in enumerate(K.SPECTRUM):
        tx, ty = FAN[k]
        if v > 0 and fade > 0:
            ex, ey = lerp(px1 - 10, tx, v), lerp(py, ty, v)
            c.drawLine(px1 - 10, py, ex, ey, skia.Paint(AntiAlias=True, StrokeWidth=22, Color=K.col(cc, 0.25 * fade),
                                                        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10)))
            c.drawLine(px1 - 10, py, ex, ey, skia.Paint(AntiAlias=True, StrokeWidth=9, Color=K.col(cc, 0.95 * fade), StrokeCap=skia.Paint.kRound_Cap))
    # the photons: born at the fan tips, then two of them become waves
    t4 = st("04")
    for k, (name, cc) in enumerate(K.SPECTRUM):
        born = t3 + 1.0 + k * 0.08
        if t < born:
            continue
        pop = ob(prog(t, born, born + 0.35))
        x, y = FAN[k]
        r = 34 * pop
        a = 1.0
        mood = "happy"
        if name in ("red", "blue"):
            m = io(prog(t, t4 - 0.1, t4 + 0.9))
            wy = WAVE_Y[name]
            lam, amp, spd = (520, 80, 90) if name == "red" else (170, 55, 260)
            ph = t * spd
            xx = lerp(x, 540 + 160 * math.sin(t * 0.3), m)
            yy = lerp(y, wy + amp * math.sin(2 * math.pi * (xx - ph) / lam), m)
            if m > 0:
                env = lambda X: min(1, max(0, (X + 60) / 200)) * min(1, max(0, (W + 60 - X) / 200))
                K.wave(c, -60, W + 60, wy, amp, lam, ph, cc, 10, a * m, glow_w=3.0, env=env)
                # wavelength bracket
                bu = oe(prog(t, wt("04", "long" if name == "red" else "short") - 0.2, wt("04", "long" if name == "red" else "short") + 0.3))
                if bu > 0:
                    by = wy - amp - 70
                    x0 = 540 - lam / 2
                    c.drawLine(x0, by, x0 + lam * bu, by, skia.Paint(AntiAlias=True, StrokeWidth=4, Color=K.col(K.WHITE, 0.9)))
                    for xb in (x0, x0 + lam * bu):
                        c.drawLine(xb, by - 16, xb, by + 16, skia.Paint(AntiAlias=True, StrokeWidth=4, Color=K.col(K.WHITE, 0.9)))
                    lab = "long & lazy" if name == "red" else "short & tight"
                    K.pill(c, lab, 540, by - 62, cc, bu, 40)
            mood = "sleepy" if name == "red" and m > 0.5 else "happy"
            K.photon(c, xx, yy, r, cc, t * (0.4 if name == "red" else 2.5), look=(1, 0), mood=mood, seed=k)
        else:
            m = io(prog(t, t4 - 0.1, t4 + 0.9))
            xx = lerp(x, 1000 + 20 * k, m)
            yy = lerp(y, 860 + (k - 2.5) * 70, m)
            K.photon(c, xx, yy, r * lerp(1, 0.6, m), cc, t, look=(-1, 0), seed=k)


PRISM_POS = [(300, 1630, 520)]


def white_override():
    def f(c, wd, t, a):
        return False
    return {}


# ---------------------------------------------------------------- 3. racing to Earth
def seg_travel(c, t, words):
    lt = t - SEG["travel"]
    spd = 1400 * ss(prog(lt, 0, 0.8))
    off = (lt * spd, 0)
    space_bg(c, t, off, streak=min(160, spd * 0.12))
    sx = SUN_XY[0] - 900 * io(prog(lt, 0, 2.5))
    K.sun(c, sx, SUN_XY[1], 300 * (1 - 0.4 * io(prog(lt, 0, 2.5))), t)
    # Earth approaches from the right
    hit = wt("05", "hit")
    e = io(prog(t, SEG["travel"] + 0.5, hit + 0.3)) ** 1.6
    ex, ey, er = lerp(1400, 1150, e), lerp(820, 1900, e), lerp(30, 1000, e)
    K.planet(c, ex, ey, er, "earth", t, light_dir=(-1, -0.4))
    # the colour gang flies in formation, each trailing its own little wave
    for k, (name, cc) in enumerate(K.SPECTRUM):
        y = 560 + k * 105
        x = 420 + 30 * math.sin(t * 2 + k)
        lam = 520 - k * 60
        K.wave(c, -40, x - 30, y, 14, lam / 3, -t * 400, cc, 5, 0.85)
        mood = "surprised" if t > hit - 0.4 else ("sleepy" if name == "red" else "happy")
        K.photon(c, x, y, 30, cc, t, look=(1, 0), mood=mood, seed=k)
    # timer: 0:00 -> 8:20
    tu = io(prog(t, st("05") + 0.2, hit))
    secs = 500 * tu
    K.pill(c, f"{int(secs // 60)}:{int(secs % 60):02d}  min", 540, 260, (40, 60, 140), ss(prog(t, st("05"), st("05") + 0.3)) *
           (1 - ss(prog(t, hit + 0.3, hit + 0.7))), 48)


# ---------------------------------------------------------------- 4. the atmosphere
def seg_atmo(c, t, words):
    lt = t - SEG["atmo"]
    space_bg(c, t, ((t - SEG["travel"]) * 1400, 0), streak=60 * (1 - prog(lt, 0, 0.5)))
    K.planet(c, 1150, 1900, 1000, "earth", t, light_dir=(-1, -0.4), atmo=1.0 + 0.6 * ss(prog(lt, 0.2, 0.6)))
    a = ss(prog(lt, 0.15, 0.5))
    K.pill(c, "our atmosphere", 470, 1080, (70, 140, 255), a, 46)
    c.drawLine(560, 1120, 420, 1290, skia.Paint(AntiAlias=True, StrokeWidth=4, Color=K.col(K.WHITE, 0.8 * a)))
    for k, (name, cc) in enumerate(K.SPECTRUM):
        u = io(prog(lt, 0.0, 1.6))
        x = lerp(420, 330 + k * 8, u)
        y = lerp(560 + k * 105, 1330 + (k - 2.5) * 10, u)
        K.photon(c, x, y, 30 * (1 - 0.5 * u), cc, t, look=(-0.2, 1), mood="surprised", seed=k)


# ---------------------------------------------------------------- 5. inside the air
MOLS = []
_r = np.random.default_rng(4)
for i in range(22):
    MOLS.append(dict(x=_r.uniform(80, W - 80), y=_r.uniform(250, 1450), kind="N2" if _r.uniform() < 0.79 else "O2",
                     vx=_r.normal(0, 14), vy=_r.normal(0, 10), seed=i))
MOLS[3]["kind"] = "O2"
MOLS[7]["kind"] = "O2"


def air_bg(c, a=1.0):
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [K.c4((54, 84, 196)), K.c4((110, 165, 245))])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh))
    for k in range(3):
        K.glow(c, [200, 900, 500][k], [400, 900, 1500][k], 600, (180, 210, 255), 0.12)


def mol_pos(m, t):
    x = (m["x"] + m["vx"] * t) % (W + 200) - 100
    y = (m["y"] + m["vy"] * t) % 1400 + 200
    return x, y


def rings(c, x, y, t, t0, color, every=0.45, speed=260, a=1.0, n=6):
    if t < t0:
        return
    for k in range(n):
        age = (t - t0) - k * every
        age = age % (every * n)
        if t - t0 < k * every:
            continue
        r = 30 + age * speed
        al = a * max(0, 1 - age / (every * n))
        c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=6, Color=K.col(color, al * 0.8)))


def seg_air(c, t, words):
    air_bg(c)
    t_tiny = wt("07", "tiny")
    t_comp = wt("09", "trick")
    t_bar = st("10") - 0.2
    hero = (540, 820)
    # zoom factor of the molecule world: close-up -> far out (molecules become specks) -> back in on one
    z_out = io(prog(t, t_tiny - 0.2, t_tiny + 1.2))
    z_in = io(prog(t, st("08") - 0.4, st("08") + 0.6))
    scale = lerp(1.0, 0.12, z_out * (1 - z_in))
    comp = io(prog(t, t_comp - 0.3, t_comp + 0.5))
    bars = io(prog(t, t_bar, t_bar + 0.6))
    dim = 1 - 0.65 * bars
    # background crowd
    for m in MOLS:
        x, y = mol_pos(m, t)
        x = hero[0] + (x - hero[0]) * scale
        y = hero[1] + (y - hero[1]) * scale
        if math.hypot(x - hero[0], y - hero[1]) < 140 * scale and z_in > 0.5:
            continue
        a = dim * (1 - 0.8 * comp) * (1 - 0.7 * z_in * (1 - z_out) if False else 1)
        K.molecule(c, x, y, 46 * max(scale, 0.12), m["kind"], t, 0.0, a * (0.55 if z_in > 0.5 and scale > 0.9 else 1.0), m["seed"],
                   face=scale > 0.5)
    # labels: N2 / O2
    for key, kind, idx in (("nitrogen", "N2", 0), ("oxygen", "O2", 3)):
        tw = wt("07", key)
        a = ss(prog(t, tw - 0.1, tw + 0.25)) * (1 - ss(prog(t, t_tiny - 0.4, t_tiny)))
        if a > 0:
            want = (380, 640) if kind == "N2" else (720, 1000)
            m = min((mm for mm in MOLS if mm["kind"] == kind), key=lambda mm: math.hypot(mol_pos(mm, t)[0] - want[0], mol_pos(mm, t)[1] - want[1]))
            x, y = mol_pos(m, t)
            K.pill(c, f"{'N₂' if kind == 'N2' else 'O₂'}  {'78%' if kind == 'N2' else '21%'}", x, y - 95, K.N2_C if kind == "N2" else K.O2_C,
                   a, 40)
    # the giant wave appears when we zoom out: one wavelength >> a molecule
    gw = ss(prog(t, t_tiny + 0.2, t_tiny + 0.9)) * (1 - z_in)
    if gw > 0:
        K.wave(c, -100, W + 100, 820, 300, 1500, -t * 200, K.SPEC["blue"], 18, gw, glow_w=3)
        bu = oe(prog(t, wt("07", "thousand") - 0.2, wt("07", "thousand") + 0.4))
        if bu > 0:
            K.pill(c, "1 wave ≈ 1,000× a molecule", 540, 360, (40, 60, 140), bu * gw, 42)
    # the hero molecule, shaken by a rolling wave, throwing light everywhere
    if z_in > 0 and comp < 1:
        a = z_in * (1 - comp) * dim
        ph = -t * 700
        K.wave(c, -100, W + 100, hero[1], 380, 1800, ph, K.SPEC["blue"], 16, a * 0.9, glow_w=3)
        field = math.sin(2 * math.pi * (hero[0] - ph) / 1800)
        shake = 0.35 + 0.65 * abs(field)
        rings(c, *hero, t, st("08") + 1.2, (160, 210, 255), a=a)
        K.molecule(c, *hero, 80, "N2", t, shake * a, a, 1, angle=0.4)
        # scattered photons, every direction
        td = wt("08", "every") - 0.3
        if t > td:
            for k in range(10):
                ang = k / 10 * 2 * math.pi + 0.3
                age = (t - td - k * 0.05) % 1.6
                d = 90 + age * 420
                K.photon(c, hero[0] + d * math.cos(ang), hero[1] + d * math.sin(ang), 18, K.SPEC["blue"], t, look=(math.cos(ang), math.sin(ang)),
                         a=a * max(0, 1 - age / 1.6), seed=k, wobble=0)
        if t > wt("08", "electrons") - 0.1 and t < wt("08", "every"):
            K.pill(c, "electrons shake", hero[0], hero[1] - 200, (240, 190, 60), ss(prog(t, wt("08", "electrons") - 0.1,
                                                                                       wt("08", "electrons") + 0.2)) * a, 40, fg=K.INK)
    # comparison: short (blue) vs long (red)
    if comp > 0:
        a = comp * dim
        for name, y, lam, spd, strength in (("blue", 560, 200, 520, 1.0), ("red", 1180, 600, 260, 0.18)):
            cc = K.SPEC[name]
            K.wave(c, -60, W + 60, y, 70, lam, -t * spd, cc, 10, a, glow_w=2.5)
            field = abs(math.sin(2 * math.pi * (540 + t * spd) / lam))
            rings(c, 540, y, t, t_comp + 0.2, lighten_c(cc), every=0.35 if name == "blue" else 0.9, a=a * (0.9 if name == "blue" else 0.35), n=5)
            K.molecule(c, 540, y, 70, "N2" if name == "blue" else "O2", t, (0.3 + 0.7 * field) * strength * a, a, 7 + (name == "red"), angle=0.3)
            K.pill(c, "short wave: big shake" if name == "blue" else "long wave: barely a wiggle", 540, y - 190, cc, a, 38)
    # bar chart: about five times more
    if bars > 0:
        base = 1380
        for k, (name, val) in enumerate((("red", 1.0), ("blue", 5.0))):
            cc = K.SPEC[name]
            x = 380 + k * 320
            h = 120 * val * oe(prog(t, t_bar + 0.2 + k * 0.25, t_bar + 1.0 + k * 0.25))
            K.shape(c, K.rrect_path(x - 80, base - h, 160, max(h, 1), 26), cc, bars, rim=6)
            K.text(c, name, x, base + 60, 46, K.WHITE, bars)
        if t > wt("10", "five"):
            K.pill(c, "≈ 5×", 700, base - 600 - 70, (255, 220, 90), ob(prog(t, wt("10", "five"), wt("10", "five") + 0.3)), 64, fg=K.INK)


def lighten_c(cc):
    return K.lighten(cc, 0.4)


# ---------------------------------------------------------------- 6. pinball across the sky
SKY_MOLS = []
_r = np.random.default_rng(12)
for gx in range(9):
    for gy in range(13):
        SKY_MOLS.append((60 + gx * 120 + _r.uniform(-40, 40), 160 + gy * 110 + _r.uniform(-35, 35)))


def zigzag(seed, n=14):
    r = np.random.default_rng(seed)
    p = list(SKY_MOLS[r.integers(0, 9)])
    pts = [(-40, p[1] - 60), tuple(p)]
    for _ in range(n):
        best = None
        for q in SKY_MOLS:
            d = math.hypot(q[0] - p[0], q[1] - p[1])
            if 90 < d < 260 and (best is None or r.uniform() < 0.25):
                best = q
        p = best if best else p
        pts.append(tuple(p))
    return pts


ZIGS = [zigzag(s) for s in range(6)]


def along(pts, u):
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:])]
    L = sum(seg) * clamp(u)
    for (a, b), s in zip(zip(pts[:-1], pts[1:]), seg):
        if L <= s:
            k = L / max(s, 1e-6)
            return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, (b[0] - a[0], b[1] - a[1])
        L -= s
    return pts[-1][0], pts[-1][1], (1, 0)


def seg_pinball(c, t, words):
    lt = t - SEG["pinball"]
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [K.c4((50, 90, 210)), K.c4((120, 180, 250))])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh))
    for k, (x, y) in enumerate(SKY_MOLS):
        K.molecule(c, x, y, 13, "N2" if k % 5 else "O2", t, 0.0, 0.8, k, face=False)
    # straight-through photons
    t_fly = wt("11", "fly")
    for k, name in enumerate(("red", "orange", "yellow")):
        for rep in range(3):
            u = (lt * 0.42 - k * 0.12 - rep * 0.33) % 1.0
            x, y = -80 + u * (W + 300), 200 + k * 60 + rep * 300 + u * 520
            K.photon(c, x, y, 22, K.SPEC[name], t, look=(1, 0.5), seed=k * 3 + rep, trail=0.6, wobble=0)
    # blue pinballs: leave a fading trail of their bounces
    tb = wt("11", "blue")
    for k, pts in enumerate(ZIGS):
        u = clamp((t - tb + 0.3 - k * 0.25) / 6.0)
        if u <= 0:
            continue
        seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:])]
        L = sum(seg) * u
        p = skia.Path()
        p.moveTo(*pts[0])
        acc = 0
        for (a, b), s in zip(zip(pts[:-1], pts[1:]), seg):
            if acc + s > L:
                kk = (L - acc) / s
                p.lineTo(a[0] + (b[0] - a[0]) * kk, a[1] + (b[1] - a[1]) * kk)
                break
            p.lineTo(*b)
            acc += s
        c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4, Color=K.col((170, 210, 255), 0.6),
                                 PathEffect=skia.DashPathEffect.Make([12, 10], 0)))
        x, y, d = along(pts, u)
        K.photon(c, x, y, 22, K.SPEC["blue"], t, look=d, seed=20 + k, wobble=0)


def fly_override(direction):
    def f(c, wd, t, a):
        if t < wd.t0 + 0.35:
            return False
        u = (t - wd.t0 - 0.35)
        dx = direction * (u * 900 + 200 * u * u)
        cc = K.SPEC.get(wd.key, K.WHITE)
        K.text(c, wd.s, wd.x + dx, wd.y, CAP.SIZE, cc, a, "left", 900, 0.3)
        return True
    return f


def bounce_override():
    def f(c, wd, t, a):
        if t < wd.t0:
            return False
        u = t - wd.t0
        dx = 30 * math.sin(u * 7) * math.exp(-u * 0.6)
        dy = -abs(40 * math.sin(u * 9)) * math.exp(-u * 0.8)
        K.text(c, wd.s, wd.x + dx, wd.y + dy, CAP.SIZE, K.SPEC["blue"], a, "left", 900, 0.3)
        return True
    return f


# ---------------------------------------------------------------- 7. back to the meadow: the blue sky
SKY_SOURCES = [(np.random.default_rng(30 + k).uniform(-100, W + 100), np.random.default_rng(60 + k).uniform(100, 1000)) for k in range(16)]


def seg_bluesky(c, t, words):
    lt = t - SEG["bluesky"]
    eye = meadow(c, t)
    a = ss(prog(lt, 0.3, 1.0))
    for k, (sx, sy) in enumerate(SKY_SOURCES):
        u = ((lt * 0.6 + k * 0.137) % 1.0)
        x, y = lerp(sx, eye[0], u), lerp(sy, eye[1], u)
        c.drawLine(sx, sy, eye[0], eye[1], skia.Paint(AntiAlias=True, StrokeWidth=3, Color=K.col((180, 220, 255), 0.25 * a)))
        K.photon(c, x, y, 16, K.SPEC["blue"], t, look=(eye[0] - sx, eye[1] - sy), a=a * min(1, (1 - u) * 5), seed=k, wobble=0)
    if t > wt("12", "blue") - 0.1:
        K.glow(c, 540, 600, 900, (120, 190, 255), 0.25 * ss(prog(t, wt("12", "blue"), wt("12", "blue") + 0.6)))


# ---------------------------------------------------------------- 8. why not violet?
def seg_violet(c, t, words):
    lt = t - SEG["violet"]
    t14 = st("14")
    pan = io(prog(t, t14 - 0.3, t14 + 0.5)) + io(prog(t, wt("14", "some") - 0.3, wt("14", "some") + 0.4)) + \
        io(prog(t, wt("14", "eyes") - 0.4, wt("14", "eyes") + 0.3))
    # the meadow sky stays behind, the cards slide over it
    meadow(c, t)
    va = ob(prog(lt, 0.4, 0.8)) * (1 - ss(prog(t, t14 - 0.3, t14)))
    if va > 0:
        K.photon(c, 540, 760, 90 * va, K.SPEC["violet"], t, look=(0, -1), mood="surprised", seed=5)
        K.pill(c, "?", 650, 620, (255, 255, 255), va, 70, fg=K.SPEC["violet"])
    if t < t14 - 0.3:
        return
    ca = ss(prog(t, t14 - 0.3, t14 + 0.2))
    c.save()
    c.translate(-pan * W, 0)
    for k in range(3):
        cx = W / 2 + k * W
        K.shape(c, K.rrect_path(cx - 440, 380, 880, 900, 60), (24, 30, 80), ca * 0.93, rim=8, shadow=0.6)
        K.text(c, ["1  less in sunlight", "2  soaked up high", "3  eyes prefer blue"][k], cx, 470, 50, K.WHITE, ca)
    # card 1: the solar spectrum (a little violet, a lot of blue/green)
    cx = W / 2
    x0, x1, yb = cx - 360, cx + 360, 1150
    bar = skia.GradientShader.MakeLinear([skia.Point(x1, 0), skia.Point(x0, 0)], [K.c4(cc) for _, cc in K.SPECTRUM])
    c.drawRect(skia.Rect(x0, yb, x1, yb + 30), skia.Paint(Shader=bar))
    p = skia.Path()
    for i in range(101):
        u = i / 100
        val = math.exp(-((u - 0.62) / 0.33) ** 2) * (0.35 + 0.65 * ss(u / 0.35))
        (p.moveTo if i == 0 else p.lineTo)(x1 - u * (x1 - x0), yb - 20 - 520 * val)
    c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=10, Color=K.col((255, 230, 120), ca),
                             StrokeCap=skia.Paint.kRound_Cap))
    K.photon(c, x0 + 40, yb - 160, 34, K.SPEC["violet"], t, look=(1, -1), mood="surprised", a=ca, seed=2)
    # card 2: violet soaked up in a high layer
    cx = W / 2 + W
    c.drawRect(skia.Rect(cx - 440, 640, cx + 440, 760), skia.Paint(Color=K.col((150, 110, 200), 0.45 * ca)))
    K.text(c, "high, thin air", cx, 720, 34, K.WHITE, ca * 0.8, w=800)
    for k in range(4):
        u = ((t * 0.5 + k * 0.25) % 1.0)
        x = cx - 300 + k * 200
        if k % 2 == 0:
            y = 560 + u * 120
            K.photon(c, x, y, 26, K.SPEC["violet"], t, look=(0, 1), a=ca * (1 - ss((u - 0.6) / 0.4)), seed=k, mood="surprised")
        else:
            y = 560 + u * 600
            K.photon(c, x, y, 26, K.SPEC["blue"], t, look=(0, 1), a=ca, seed=k)
    # card 3: the eye's sensitivity
    cx = W / 2 + 2 * W
    eye = skia.Path()
    eye.moveTo(cx - 220, 720)
    eye.quadTo(cx, 560, cx + 220, 720)
    eye.quadTo(cx, 880, cx - 220, 720)
    K.shape(c, eye, (245, 245, 255), ca, rim=5)
    K.shape(c, K.circle_path(cx, 720, 90), (80, 140, 230), ca, rim=6)
    c.drawCircle(cx, 720, 42, skia.Paint(AntiAlias=True, Color=K.col(K.INK, ca)))
    c.drawCircle(cx - 22, 698, 14, skia.Paint(AntiAlias=True, Color=K.col(K.WHITE, ca)))
    for k, (name, val) in enumerate((("violet", 0.12), ("blue", 0.55), ("green", 1.0))):
        x = cx - 220 + k * 220
        h = 260 * val * oe(prog(t, wt("14", "eyes") + 0.2 + k * 0.15, wt("14", "eyes") + 0.8 + k * 0.15))
        K.shape(c, K.rrect_path(x - 60, 1220 - h, 120, max(h, 1), 22), K.SPEC[name], ca, rim=5)
    c.restore()


# ---------------------------------------------------------------- 9. sunset
def seg_sunset(c, t, words):
    lt = t - SEG["sunset"]
    dusk = io(prog(t, st("15"), st("15") + 2.6))
    diag = io(prog(t, st("16") - 0.4, st("16") + 0.6)) * (1 - io(prog(t, wt("17", "orange") - 1.2, wt("17", "orange") - 0.4)))
    final = io(prog(t, wt("17", "orange") - 1.2, wt("17", "orange") - 0.4))
    sun_y = lerp(-1250, -170, io(prog(t, st("15"), st("15") + 3.0)))
    sun_y = lerp(sun_y, -60, final)
    if diag < 1:
        meadow(c, t, sun_pos=(820, sun_y), sunset=max(dusk, final))
    if diag > 0:
        c.save()
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=K.col((14, 14, 46), diag)))
        STARS.draw(c, t, (0, 0), diag)
        # the planet, a shell of air, you on top
        px, py, pr = 540, 2950, 1700
        sh_a = diag
        c.drawCircle(px, py, pr + 260, skia.Paint(AntiAlias=True, Color=K.col((90, 150, 255), 0.28 * sh_a)))
        K.planet(c, px, py, pr, "earth", t, a=sh_a, atmo=0.0, light_dir=(-1, -0.2))
        you = (540, py - pr - 10)
        K.photon(c, you[0], you[1] - 24, 24, (255, 196, 70), t, look=(-1, -0.3), a=sh_a, seed=1)
        # overhead path (short) and horizon path (long)
        top = (540, py - pr - 260)
        u = oe(prog(t, st("16") + 0.3, st("16") + 1.0))
        c.drawLine(top[0], top[1] - 200, top[0], lerp(top[1] - 200, you[1] - 50, u), skia.Paint(AntiAlias=True, StrokeWidth=10, Color=K.col(K.SUN_Y, sh_a)))
        K.pill(c, "noon: short trip", 760, top[1] - 120, (60, 80, 160), sh_a * u, 36)
        ly = you[1] - 40
        hx0 = px - math.sqrt((pr + 260) ** 2 - (py - ly) ** 2)
        v = oe(prog(t, wt("16", "cross") - 0.2, wt("16", "cross") + 0.6))
        c.drawLine(-50, ly, lerp(-50, you[0] - 40, v), ly, skia.Paint(AntiAlias=True, StrokeWidth=10, Color=K.col((255, 150, 80), sh_a)))
        if v > 0:
            c.drawLine(hx0, ly + 34, you[0] - 40, ly + 34, skia.Paint(AntiAlias=True, StrokeWidth=4, Color=K.col(K.WHITE, sh_a * v)))
            K.pill(c, "sunset: up to 40× more air", 420, ly + 110, (240, 110, 80), sh_a * ss(prog(t, wt("16", "forty"), wt("16", "forty") + 0.3)), 38)
        # photons crossing the long path: blues get knocked out one by one
        t17 = st("17")
        if t > t17 - 0.3:
            for k in range(8):
                name = ["red", "blue", "orange", "blue", "yellow", "blue", "red", "blue"][k]
                u = clamp((t - t17 + 0.3 - k * 0.32) / 2.6)
                if u <= 0:
                    continue
                x = lerp(hx0 - 60, you[0] - 60, u)
                y = ly
                a2 = sh_a
                if name == "blue":
                    kick = clamp((u - (0.18 + 0.1 * (k % 3))) / 0.25)
                    if kick > 0:
                        x += 40 * kick
                        y -= 520 * kick * (1 if k % 2 else -0.6)
                        a2 *= 1 - kick
                K.photon(c, x, y, 22, K.SPEC[name], t, look=(1, 0), a=a2, seed=k, wobble=0)
        c.restore()


# ---------------------------------------------------------------- 10. Mars
def seg_mars(c, t, words):
    lt = t - SEG["mars"]
    zoom_in = io(prog(t, wt("18", "dusty") - 0.6, wt("18", "dusty") + 0.4))
    if zoom_in < 1:
        space_bg(c, t, (lt * 120, 0))
        u = io(prog(lt, 0, 1.6))
        K.planet(c, lerp(-300, 220, 1 - u * 0.0) - u * 500, 1500, 500, "earth", t, light_dir=(-1, -0.3))
        mx, my, mr = lerp(1300, 560, u), 900, lerp(140, 260, u)
        sc = lerp(1.0, 8.0, zoom_in)
        c.save()
        c.translate(mx, my)
        c.scale(sc, sc)
        c.translate(-mx, -my)
        K.planet(c, mx, my, mr, "mars", t, light_dir=(-1, -0.3), atmo=0.5)
        c.restore()
        K.pill(c, "Mars", mx, my - mr - 60, (210, 110, 70), ss(prog(lt, 0.8, 1.2)) * (1 - zoom_in), 46)
        if zoom_in > 0:
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=K.col((220, 160, 100), zoom_in)))
        if zoom_in < 0.98:
            return
    blue_set = io(prog(t, wt("18", "blue") - 0.5, wt("18", "blue") + 0.8))
    top = K.mix((226, 168, 108), (60, 50, 70), blue_set)
    bot = K.mix((246, 206, 150), (140, 110, 100), blue_set)
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 1400)], [K.c4(top), K.c4(bot)])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh))
    sy = lerp(520, 1220, blue_set)
    if blue_set > 0:
        K.glow(c, 600, sy, 700, (110, 160, 255), 0.75 * blue_set)
    K.sun(c, 600, sy, 60, t, color=(255, 246, 220), corona=0.3)
    for k in range(40):
        rr = K.rng("dust", k)
        x = (rr.uniform(0, W) + t * rr.uniform(10, 40)) % W
        y = rr.uniform(200, 1400)
        c.drawCircle(x, y, rr.uniform(2, 5), skia.Paint(AntiAlias=True, Color=K.col((255, 225, 180), 0.35)))
    K.hill(c, [1240, 1180, 1220, 1150, 1210], -100, W + 100, H + 50, K.mix((190, 100, 60), (90, 50, 50), blue_set * 0.7))
    K.hill(c, [1340, 1300, 1320, 1280, 1330], -100, W + 100, H + 50, K.mix((160, 80, 50), (70, 40, 40), blue_set * 0.7))
    # a small rover
    rx, ry = 760, 1290
    K.shape(c, K.rrect_path(rx - 80, ry - 70, 160, 50, 12), (235, 235, 240), 1.0, rim=4)
    for dx in (-60, 0, 60):
        K.shape(c, K.circle_path(rx + dx, ry - 12, 18), (60, 60, 70), 1.0, rim=3)
    c.drawLine(rx + 40, ry - 70, rx + 40, ry - 130, skia.Paint(AntiAlias=True, StrokeWidth=6, Color=K.col((235, 235, 240))))
    K.shape(c, K.rrect_path(rx + 20, ry - 150, 50, 26, 6), (235, 235, 240), 1.0, rim=3)
    K.pill(c, "butterscotch day", 540, 380, (200, 130, 70), ss(prog(t, wt("18", "butterscotch"), wt("18", "butterscotch") + 0.3)) * (1 - blue_set), 44)
    K.pill(c, "blue sunset", 540, 380, (70, 120, 220), ss(prog(t, wt("18", "blue") + 0.2, wt("18", "blue") + 0.5)), 44)


# ---------------------------------------------------------------- 11. end
def seg_end(c, t, words):
    lt = t - SEG["end"]
    split = io(prog(lt, 0, 0.8))
    title = io(prog(t, st("20") - 0.2, st("20") + 0.6))
    # left: Earth sunset, right: Mars sunset, separated by a diagonal
    left = skia.Path()
    left.moveTo(0, 0)
    left.lineTo(W * 0.62, 0)
    left.lineTo(W * 0.38, H)
    left.lineTo(0, H)
    left.close()
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [K.c4((90, 50, 130)), K.c4((255, 140, 80))])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=K.col((50, 44, 60))))
    c.save()
    c.clipPath(left, skia.ClipOp.kIntersect, True)
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh))
    K.sun(c, 260, 1180, 90, t, color=(255, 150, 80), corona=0.6)
    K.hill(c, [1300, 1250, 1290, 1240], -50, W, H + 50, (70, 40, 80))
    K.text(c, "Earth", 230, 360, 64, K.WHITE, split)
    c.restore()
    c.save()
    right = skia.Path()
    right.addRect(skia.Rect(0, 0, W, H))
    right = skia.Op(right, left, skia.PathOp.kDifference_PathOp)
    c.clipPath(right, skia.ClipOp.kIntersect, True)
    sh2 = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [K.c4((60, 50, 70)), K.c4((150, 120, 105))])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh2))
    K.glow(c, 820, 1180, 500, (110, 160, 255), 0.8)
    K.sun(c, 820, 1180, 60, t, color=(255, 246, 220), corona=0.3)
    K.hill(c, [1300, 1260, 1280, 1250], 0, W + 50, H + 50, (90, 50, 45))
    K.text(c, "Mars", 850, 360, 64, K.WHITE, split)
    c.restore()
    c.drawLine(W * 0.62, 0, W * 0.38, H, skia.Paint(AntiAlias=True, StrokeWidth=8, Color=K.col(K.WHITE, 0.9)))
    if title > 0:
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=K.col(K.NAVY, 0.88 * title)))
        STARS.draw(c, t, (0, 0), title)
        K.text(c, "THE PHYSICS OF", W / 2, 740, 64, K.WHITE, title, w=800)
        K.text(c, "EVERYDAY THINGS", W / 2, 840, 96, K.WHITE, title)
        K.pill(c, "Nº 04  ·  why the sky is blue", W / 2, 960, (70, 140, 255), title, 38)
        for k, (name, cc) in enumerate(K.SPECTRUM):
            ang = t * 0.8 + k / 6 * 2 * math.pi
            K.photon(c, W / 2 + 330 * math.cos(ang), 840 + 330 * math.sin(ang) * 0.55, 30 * title, cc, t, look=(-math.cos(ang), -math.sin(ang)),
                     a=title, seed=k)


SEGS = dict(meadow=seg_meadow, sun=seg_sun, travel=seg_travel, atmo=seg_atmo, air=seg_air, pinball=seg_pinball, bluesky=seg_bluesky,
            violet=seg_violet, sunset=seg_sunset, mars=seg_mars, end=seg_end)


def overrides_for(name, t):
    o = {"blue": blue_override(), "sky": None}
    o.pop("sky")
    if name == "pinball":
        o.update({"red,": fly_override(1), "red": fly_override(1), "orange": fly_override(1), "yellow": fly_override(1),
                  "blue": bounce_override()})
    return o


def seg_at(t):
    name = "meadow"
    for k in SEG_ORDER:
        if t >= SEG[k]:
            name = k
    return name


def draw_seg(c, name, t, words):
    c.save()
    SEGS[name](c, t, words)
    c.restore()


def frame(t):
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    c.clear(K.col(K.SPACE))
    pg = page_at(t)
    words = pg[2] if pg else None
    name = seg_at(t)
    kind, dur, focus = ENTRY.get(name, ("none", 0, None))
    t0 = SEG[name]
    if kind in ("zoom_in", "zoom_out") and t < t0 + dur:
        i = SEG_ORDER.index(name)
        prev = SEG_ORDER[i - 1]
        u = io(prog(t, t0, t0 + dur))
        fx, fy = focus
        # outgoing scene flies past the camera (zoom in) or shrinks away (zoom out); incoming scales into place
        s_out = lerp(1.0, 6.0, u) if kind == "zoom_in" else lerp(1.0, 0.25, u)
        s_in = lerp(0.2, 1.0, u) if kind == "zoom_in" else lerp(3.5, 1.0, u)
        c.save()
        c.translate(fx, fy)
        c.scale(s_out, s_out)
        c.translate(-fx, -fy)
        draw_seg(c, prev, t, words)
        c.restore()
        c.saveLayer(None, skia.Paint(Color=K.col((255, 255, 255), ss(u * 1.4))))
        c.translate(fx, fy)
        c.scale(s_in, s_in)
        c.translate(-fx, -fy)
        draw_seg(c, name, t, words)
        c.restore()
    else:
        draw_seg(c, name, t, words)
    K.vignette(c, 0.35)
    # captions
    if pg:
        t0p, t1p, ws = pg
        a = K.ss(prog(t, t0p, t0p + 0.2)) * (1 - K.ss(prog(t, t1p - 0.2, t1p)))
        sc = skia.GradientShader.MakeLinear([skia.Point(0, H - 520), skia.Point(0, H)], [K.c4((0, 0, 0), 0), K.c4((5, 8, 30), 0.55 * a)])
        c.drawRect(skia.Rect(0, H - 520, W, H), skia.Paint(Shader=sc))
        CAP.draw(c, ws, t, a, overrides_for(name, t))
    K.grain(c, t, 0.06)
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=K.col((0, 0, 0), 1 - prog(t, 0, 0.6) + prog(t, DURATION - 0.8, DURATION))))
    return np.ascontiguousarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3])


def _job(i):
    return frame(i / FPS).tobytes()


def render(procs=4, name="ep04_sky"):
    import sound
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    bdir = os.path.join(HERE, "build")
    wav = sound.render_audio(os.path.join(bdir, "mix.wav"), sys.modules[__name__])
    silent = os.path.join(bdir, f"{name}_video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    frames = range(int(DURATION * FPS))
    with Pool(procs) as pool:
        for k, buf in enumerate(pool.imap(_job, frames, chunksize=4)):
            ff.stdin.write(buf)
            if k % 150 == 0:
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
            p = os.path.join(d, f"t{float(s):06.2f}.png")
            Image.fromarray(frame(float(s))).save(p)
            print(p, seg_at(float(s)))
    else:
        render(int(os.environ.get("PROCS", "4")))
