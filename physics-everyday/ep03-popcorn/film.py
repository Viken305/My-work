"""Ep. 03 'Why does popcorn pop?' -- dark-studio food film, 9:16, 24 fps.

  python3 voiceover.py         # narration -> build/vo
  python3 film.py              # -> out/ep03_popcorn.mp4      (PROCS=3 by default)
  python3 film.py --still 3,40 # single frames -> build/stills
"""
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lux as L  # noqa: E402
import overlay as O  # noqa: E402
import props as Pr  # noqa: E402
from lux import Rx, Ry, Rz, S, T, cat  # noqa: E402

W, H, FPS = 1080, 1920, 24
SS = float(os.environ.get("SS", "1.6"))
TL = json.load(open(os.path.join(HERE, "build", "vo", "timeline.json")))
DURATION = 80.0


# ---------------------------------------------------------------- timing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t1)


def ss(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def io(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def oe(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def lerp(a, b, u):
    return a + (b - a) * u


def lerp3(a, b, u):
    return tuple(lerp(x, y, u) for x, y in zip(a, b))


def words_of(key):
    it = TL[key]
    ws = it["text"].split()
    n = sum(len(w) + 1 for w in ws)
    out, acc = [], 0
    for w in ws:
        out.append((w, it["start"] + it["dur"] * (acc / n) * 0.95))
        acc += len(w) + 1
    return out


def wt(key, prefix):
    for w, s in words_of(key):
        if w.lower().strip(".,?!:").startswith(prefix.lower()):
            return s
    raise KeyError(prefix)


def st(key):
    return TL[key]["start"]


def en(key):
    return TL[key]["start"] + TL[key]["dur"]


# ---------------------------------------------------------------- shot boundaries
SH = dict(hero=0.0, cut=st("03") - 0.7, fire=st("05") - 0.35, inside=wt("06", "but") - 0.15, climax=st("09") - 0.45,
          slow=wt("10", "way") + 0.15, sound=st("12") - 0.4, cork=wt("12", "like") - 0.1, jump=st("13") - 0.45,
          duds=st("14") - 0.45, finale=st("15") - 0.45, end=st("16") - 0.4, stinger=st("16") + 3.6, black=st("16") + 5.3)
ORDER = ["hero", "cut", "fire", "inside", "climax", "slow", "sound", "cork", "jump", "duds", "finale", "end", "stinger", "black"]

STUDIO = dict(dir=(0.55, -0.75, -0.35), col=(3.0, 2.55, 2.0), center=(0, 0, 0), extent=4.0, dist=30.0,
              env_key_dir=(-0.55, 0.75, 0.35), env_key_col=(2.4, 2.0, 1.6), env_rim_dir=(0.7, 0.3, -0.65),
              env_rim_col=(1.3, 1.5, 1.9), env_amb=(0.018, 0.016, 0.014), env_floor=(0.004, 0.003, 0.002))
RIM = (1.1, 1.35, 1.9)


def orbit(target, dist, yaw, pitch, fov, roll=0.0):
    tx, ty, tz = target
    y, p = math.radians(yaw), math.radians(pitch)
    eye = (tx + dist * math.cos(p) * math.sin(y), ty + dist * math.sin(p), tz + dist * math.cos(p) * math.cos(y))
    return dict(eye=eye, target=target, fov=fov, roll=roll)


def tremble(t, amp, seed=0):
    return (amp * math.sin(t * 61 + seed), amp * 0.6 * math.sin(t * 47 + seed * 2), amp * math.sin(t * 53 + seed * 3))


# ---------------------------------------------------------------- the pop itself
def pop_geo(lt, seed=0, res=1.0, base=None, spin=0.0, steam=True, leg=None):
    """Kernel popping at local time lt (seconds of *slowed* time; 0 = the shell gives way)."""
    base = np.eye(4, dtype=np.float32) if base is None else base
    if lt < 0:
        return Pr.place(Pr.kernel(seed, res), base), None
    open_ = ss(prog(lt, 0.0, 2.2)) * 1.25
    g = ss(prog(lt, 0.15, 5.0)) ** 0.75
    parts = [Pr.hull_petals(open_, seed, res).xf(base)]
    if g > 0.01:
        foam = Pr.popped(seed + 3, max(0.05, g), res)
        s = lerp(0.6, 1.25, g)
        parts.append(Pr.place(foam, base @ T(0, 0.12 * g, 0) @ Ry(spin) @ S(s)))
    trans = None
    if steam:
        c = (base @ np.array([0, 0.2, 0, 1.0]))[:3]
        trans = Pr.puffs(c, lt, 0.05, n=10, size=0.55, seed=seed, life=4.0, alpha=0.07)
    return cat(parts), trans


# ---------------------------------------------------------------- shots
def shot_hero(t):
    lt = t - SH["hero"]
    shake = tremble(t, 0.006 * prog(t, wt("02", "explode") - 0.1, wt("02", "explode") + 0.2) * (1 - prog(t, 6.0, 6.6)))
    rot = 0.35 + lt * 0.22
    k = Pr.place(Pr.kernel(0, 1.6), T(shake[0], 0.75 + 0.03 * math.sin(lt * 1.3) + shake[1], shake[2]) @ Ry(rot) @ Rz(0.12))
    sh = Pr.place(Pr.kernel(1, 0.6), T(-1.6, 0.21, -2.2) @ Ry(1.0) @ Rx(math.pi / 2))
    sh2 = Pr.place(Pr.kernel(2, 0.6), T(1.4, 0.21, -3.4) @ Ry(2.2) @ Rx(math.pi / 2))
    opaque = cat([Pr.slate_static(), k, sh, sh2])
    push = oe(prog(t, wt("02", "explode") - 0.05, wt("02", "explode") + 0.5)) * 0.35
    cam = orbit((0, 0.72, 0), lerp(4.2, 3.2, io(prog(lt, 0, 6.5))) - push, lerp(28, 8, io(prog(lt, 0, 7))), lerp(14, 9, prog(lt, 0, 7)), 24)
    light = dict(STUDIO, extent=3.5)
    lights = [((-2.0, 2.2, -2.6), 3.5, RIM), ((2.5, 0.5, -1.5), 3.0, (1.4, 0.9, 0.5))]
    return cam, light, opaque, None, lights, dict(dof=34, exposure=0.95, motes=1.0)


def shot_cut(t):
    lt = t - SH["cut"]
    lift = oe(prog(lt, 0.2, 1.3))
    water = ss(prog(t, wt("03", "water") - 0.3, wt("03", "water") + 0.4))
    shell = ss(prog(t, wt("04", "shell") - 0.2, wt("04", "shell") + 0.5)) * (1 - 0.6 * prog(t, en("04"), en("04") + 0.8))
    c = Pr.cutaway(heat=0.0, water_glow=water, shell_glow=shell, t=t).xf(T(0, 0.85, 0))
    full = Pr.k_copy(0)
    cen = full.P.mean(axis=1)
    m = cen[:, 2] >= 0.002
    front = L.Geo(full.P[m], full.N[m], full.C[m], S=0.9, M=-0.06)
    front = L.rough(front, 0.16).xf(T(0, 0.85 + lift * 2.6, lift * 0.6))
    opaque = cat([Pr.slate_static(), c, front if lift < 0.99 else None])
    cam = orbit((0, 0.86, 0), lerp(3.5, 3.0, io(prog(lt, 0, 9))), lerp(-6, 6, io(prog(lt, 0, 9.5))), 6, 30)
    light = dict(STUDIO, dir=(0.4, -0.5, -0.75), col=(1.5, 1.3, 1.05), extent=3.0)
    lights = [((-2.0, 2.0, -2.0), 3.0, RIM)]
    return cam, light, opaque, None, lights, dict(dof=26, exposure=0.72, motes=0.6)


PAN_KERNELS = [(x, z, i) for i, (x, z) in enumerate(np.random.default_rng(1).uniform(-6.5, 6.5, (40, 2))) if math.hypot(x, z) < 7.6]


def pan_kernels(t, pop_from=None, res=0.5, skip=()):
    out = []
    for x, z, i in PAN_KERNELS:
        if i in skip:
            continue
        sh = tremble(t, 0.02 * (pop_from is not None), i)
        out.append(Pr.place(Pr.kernel(i % 3, res), T(x + sh[0], 0.58, z + sh[2]) @ Ry(i * 1.7) @ Rx(math.pi / 2)))
    return cat(out)


def shot_fire(t):
    lt = t - SH["fire"]
    ign = wt("05", "heat")
    level = oe(prog(t, ign - 0.1, ign + 0.35))
    opaque = cat([Pr.stove_static(), Pr.pan_static(), pan_kernels(t)])
    trans = cat([Pr.flame(t, level), Pr.oil(t, shimmer=0.3 + 0.7 * prog(t, ign, ign + 4))])
    cam = orbit((0, 0.8, 0), lerp(30, 21, io(prog(lt, 0, 6))), lerp(-20, 10, io(prog(lt, 0, 6))), lerp(42, 24, io(prog(lt, 0, 6))), 34)
    light = dict(STUDIO, extent=16.0, dist=60)
    lights = [((0, -1.0, 0), 7.0, tuple(np.array((0.6, 1.0, 3.2)) * level)), ((-15, 12, -20), 30.0, RIM),
              ((14, 6, 10), 25.0, (0.9, 0.6, 0.35))]
    return cam, light, opaque, trans, lights, dict(dof=7.0, exposure=0.95, motes=0.5)


def shot_inside(t):
    lt = t - SH["inside"]
    heat = ss(prog(t, SH["inside"], wt("07", "nine") + 0.3)) * 0.85 + 0.15 * prog(t, st("08"), SH["climax"])
    gel = ss(prog(t, wt("08", "softens") - 0.2, wt("08", "gel") + 0.6))
    sh = tremble(t, 0.004 + 0.01 * heat, 3)
    c = Pr.cutaway(heat=heat, gel=gel, water_glow=0.6, shell_glow=0.25 + 0.4 * heat, t=t).xf(T(sh[0], 0.85 + sh[1], 0))
    opaque = cat([Pr.slate_static(), c])
    cam = orbit((0, 0.96, 0), lerp(3.5, 3.1, io(prog(lt, 0, 9.5))), lerp(8, -4, io(prog(lt, 0, 10))), 4, 30)
    light = dict(STUDIO, dir=(0.4, -0.5, -0.75), col=(1.5, 1.3, 1.0), extent=3.0)
    lights = [((-2.0, 2.0, -2.0), 3.0, RIM), ((0.0, -0.3, 1.2), 1.6, (2.2 * heat, 0.9 * heat, 0.3 * heat))]
    return cam, light, opaque, None, lights, dict(dof=26, exposure=0.72, motes=0.4)


HERO_BASE = T(0.6, 0.58, 1.2) @ Ry(2.1) @ Rx(math.pi / 2)


def shot_climax(t):
    lt = t - SH["climax"]
    tq = prog(t, SH["climax"], SH["slow"])
    shk = tremble(t, 0.004 + 0.03 * tq ** 2, 9)
    hero = Pr.place(Pr.kernel(0, 1.0), T(*shk) @ HERO_BASE)
    opaque = cat([Pr.stove_static(), Pr.pan_static(), pan_kernels(t, 1, skip=()), hero])
    trans = cat([Pr.flame(t, 1.0), Pr.oil(t, shimmer=1.0)])
    tgt = (0.6, 0.6, 1.2)
    cam = orbit(tgt, lerp(5.0, 3.6, io(prog(lt, 0, 4.2))), 20, lerp(18, 12, prog(lt, 0, 4)), 26)
    light = dict(STUDIO, extent=6.0, center=tgt)
    lights = [((0.6, -1.0, 1.2), 5.0, (0.6, 1.0, 3.2)), ((-3, 3, -4), 6.0, RIM), ((3, 1.5, 2), 5.0, (1.4, 0.8, 0.4))]
    return cam, light, opaque, trans, lights, dict(dof=30, exposure=0.95, motes=0.3, focus_pt=tgt)


def shot_slow(t, angle=0.0, lt0=None):
    """The pop at 2,900 frames per second (shown ~120x slower)."""
    lt = (t - SH["slow"]) if lt0 is None else lt0
    pg, puff = pop_geo(lt * 0.95, 0, 1.0, base=HERO_BASE @ Rx(-math.pi / 2) @ T(0, 0, 0) @ Rx(math.pi / 2) if False else HERO_BASE,
                       spin=0.3)
    opaque = cat([Pr.stove_static(), Pr.pan_static(), pan_kernels(t, None), pg])
    trans = cat([Pr.flame(t * 0.05, 1.0), Pr.oil(t * 0.05, shimmer=0.4), puff])
    tgt = (0.6, 0.75 + 0.3 * prog(lt, 0, 6), 1.2)
    cam = orbit(tgt, lerp(4.2, 7.5, io(prog(lt, 0, 7))), 20 + angle + lt * 6, lerp(8, 18, io(prog(lt, 0, 8))), 28)
    light = dict(STUDIO, extent=6.0, center=tgt)
    lights = [((0.6, -1.0, 1.2), 5.0, (0.6, 1.0, 3.2)), ((-3, 3, -4), 6.0, RIM), ((3, 1.5, 2), 5.0, (1.4, 0.8, 0.4))]
    return cam, light, opaque, trans, lights, dict(dof=26, exposure=0.8, motes=0.2, focus_pt=tgt)


def shot_sound(t):
    lt = t - SH["sound"]
    cam, light, opaque, trans, lights, fx = shot_slow(t, angle=-70, lt0=0.4 + lt * 0.55)
    # a second, bigger steam jet: the steam is what makes the sound
    extra = Pr.puffs((0.6, 0.8, 1.2), 0.4 + lt * 0.55, 0.05, n=12, size=0.8, seed=12, life=3.5, alpha=0.1)
    trans = cat([trans, extra])
    return cam, light, opaque, trans, lights, fx


def shot_cork(t):
    lt = t - SH["cork"]
    tp = wt("12", "cork") + 0.05
    u = max(0.0, t - tp)
    y = 30.6 + 26 * u * 0.6 - 9 * u * u * 0.3
    M = T(0.8 * u, y, 0.3 * u) @ Rz(-2.4 * u) @ Rx(0.8 * u)
    opaque = cat([Pr.slate_static(), Pr.bottle_static(), Pr.cork(M)])
    trans = Pr.puffs((0, 31.2, 0), u, 0.0, n=22, size=2.2, seed=21, life=2.6, alpha=0.22) if u > 0 else None
    cam = orbit((0, 29.5, 0), lerp(26, 22, io(prog(lt, 0, 3))), lerp(30, 18, io(prog(lt, 0, 3))), 6, 30)
    light = dict(STUDIO, extent=34.0, dist=90, center=(0, 20, 0))
    lights = [((-15, 34, -20), 40.0, RIM), ((18, 26, 6), 30.0, (1.0, 0.75, 0.45))]
    return cam, light, opaque, trans, lights, dict(dof=6.0, exposure=0.95, motes=0.8)


def shot_jump(t):
    """Side view on the pan floor: the starch leg kicks and the kernel flips into the air."""
    lt = t - SH["jump"]
    kick = wt("13", "leg") - SH["jump"]
    flip = wt("13", "flips") - SH["jump"]
    floor = Pr.slate_static()
    pan = L.rough(L.box(-40, 40, -1.0, 0.0, -30, 30, Pr.COPPER, jit=0.0, S=1.0, M=1.0), 0.22)
    pg_lt = (lt - kick + 0.4) * 0.9
    up = max(0.0, lt - flip)
    hy = 0.2 + 3.2 * up - 1.6 * up * up
    hy = max(hy, 0.2)
    rot = 2.6 * oe(prog(up, 0, 1.6))
    base = T(-0.2 + 0.6 * up, hy, 0) @ Rz(rot) @ Rx(math.pi / 2)
    pg, puff = pop_geo(pg_lt, 4, 1.0, base=base, spin=0.5)
    parts = [pan, pg]
    if 0 <= pg_lt and up < 0.35:  # the leg: a column of starch pushing on the pan
        Lg = min(0.6, pg_lt * 0.8) * (1 - prog(up, 0.1, 0.35))
        if Lg > 0.01:
            leg = L.cylinder(0.11, 0, Lg, 16, Pr.CREAM, r_top=0.15, S=0.3, M=-0.4).xf(T(-0.05, -Lg + 0.02, 0))
            parts.append(L.rough(leg, 0.5).xf(T(-0.2 + 0.6 * up, hy - 0.05, 0)))
    opaque = cat(parts)
    tgt = (0.3, 0.9, 0)
    cam = dict(eye=(lerp(0.0, 0.6, prog(lt, 0, 7)), 1.1, 8.5), target=tgt, fov=32)
    light = dict(STUDIO, extent=6.0, center=tgt, dir=(0.35, -0.8, -0.45))
    lights = [((-3, 2.5, -3), 6.0, RIM), ((3, 1.0, 2), 5.0, (1.4, 0.8, 0.4))]
    return cam, light, opaque, puff, lights, dict(dof=12, exposure=0.95, motes=0.3, focus_pt=(0.3, 0.9, 0), jump=(base, up))


DUDS = [(1.2, 0.8, 0), (-0.9, 1.6, 1), (0.3, -1.4, 2)]


def shot_duds(t):
    lt = t - SH["duds"]
    rng = np.random.default_rng(8)
    pops = []
    for k in range(26):
        x, z = rng.uniform(-7.5, 7.5, 2)
        if math.hypot(x, z) > 8.0 or math.hypot(x - 0.2, z) < 2.6:
            continue
        pops.append(Pr.place(Pr.popped(k % 24, 1.0, 0.6), T(x, 1.3, z) @ Ry(k) @ Rx(k * 0.7) @ S(1.3)))
    duds = [Pr.place(Pr.kernel(s, 0.8), T(x, 0.58, z) @ Ry(s * 2.0) @ Rx(math.pi / 2)) for x, z, s in DUDS]
    opaque = cat([Pr.stove_static(), Pr.pan_static()] + pops + duds)
    leak = Pr.puffs((1.2, 0.75, 0.8), lt, 0.3, n=8, size=0.18, seed=5, life=2.2, alpha=0.18)
    trans = cat([Pr.oil(t, shimmer=0.3), leak])
    tgt = (0.6, 0.6, 0.6)
    cam = orbit(tgt, lerp(16, 5.5, io(prog(lt, 0, 3.4))), lerp(10, 30, io(prog(lt, 0, 4.5))), lerp(72, 34, io(prog(lt, 0, 3.4))), 30)
    light = dict(STUDIO, extent=14.0, dist=60)
    lights = [((-12, 10, -15), 25.0, RIM), ((10, 5, 8), 20.0, (0.9, 0.6, 0.35))]
    return cam, light, opaque, trans, lights, dict(dof=lerp(5, 22, io(prog(lt, 0, 3.4))), exposure=0.9, motes=0.4, focus_pt=tgt)


def shot_finale(t, end=False):
    lt = t - SH["finale"]
    pile, _ = Pr.bowl_pile()
    dud = Pr.place(Pr.kernel(1, 1.0), T(13.5, 0.2, 7.0) @ Ry(0.7) @ Rx(math.pi / 2) @ S(1.3))
    opaque = cat([Pr.slate_static(), Pr.bowl_static(), pile, dud])
    bs = st("15") + 0.3
    trans = cat([Pr.butter_stream(bs, t, (1.5, 40, 0.5), (0.5, 11.5, 0.5)) if t < st("16") + 1.0 else None,
                 Pr.salt(t, st("15") + 2.2, center=(-1.0, 26, 1.0))])
    cam = orbit((0, 9.0, 0), lerp(38, 32, io(prog(lt, 0, 9))), lerp(-25, 15, io(prog(lt, 0, 14))), lerp(26, 20, io(prog(lt, 0, 9))), 32)
    light = dict(STUDIO, extent=26.0, dist=80)
    lights = [((-20, 18, -25), 45.0, RIM), ((22, 10, 14), 35.0, (1.0, 0.7, 0.4))]
    return cam, light, opaque, trans, lights, dict(dof=6.0 + 6.0 * end, exposure=0.85 - 0.3 * end * prog(t, SH['end'], SH['end'] + 1.0), motes=0.9, focus_pt=(0, 9, 0))


def shot_stinger(t):
    lt = t - SH["stinger"]
    pile, _ = Pr.bowl_pile()
    tp = 0.9
    pl = (lt - tp) * 12.0
    up = max(0.0, lt - tp - 0.08)
    base = T(13.5 + 4 * up, 0.2 + 14 * up - 20 * up * up, 7.0) @ Ry(0.7) @ Rz(9 * up) @ Rx(math.pi / 2) @ S(1.3)
    sh = tremble(t, 0.02 * prog(lt, 0.2, tp), 2)
    pg, puff = pop_geo(pl, 1, 1.0, base=T(*sh) @ base, steam=True)
    opaque = cat([Pr.slate_static(), Pr.bowl_static(), pile, pg])
    tgt = (13.5, 0.8, 7.0)
    cam = orbit(tgt, 7.5, 60, 8, 30)
    light = dict(STUDIO, extent=20.0, dist=80)
    lights = [((-20, 18, -25), 45.0, RIM), ((22, 10, 14), 35.0, (1.0, 0.7, 0.4))]
    return cam, light, opaque, puff, lights, dict(dof=18, exposure=0.9, motes=0.5, focus_pt=tgt)


SHOTS = dict(hero=shot_hero, cut=shot_cut, fire=shot_fire, inside=shot_inside, climax=shot_climax, slow=shot_slow, sound=shot_sound,
             cork=shot_cork, jump=shot_jump, duds=shot_duds, finale=shot_finale, end=lambda t: shot_finale(t, True), stinger=shot_stinger)


def shot_at(t):
    name = "hero"
    for k in ORDER:
        if t >= SH[k]:
            name = k
    return name


# ---------------------------------------------------------------- overlays per shot
PAGES = None


def pages():
    out = []
    for key in TL:
        if key == "16":
            continue
        ws = words_of(key)
        cur = []
        for i, (w, s) in enumerate(ws):
            cur.append((w, s))
            left = len(ws) - 1 - i
            brk = (w[-1] in ".,?" and len(cur) >= 3 or len(cur) >= 7) and (left == 0 or left > 2 or w[-1] in ".?")
            if brk or i == len(ws) - 1:
                out.append((key, cur))
                cur = []
    res = []
    for i, (key, pg) in enumerate(out):
        end = min(pg[-1][1] + 1.2, out[i + 1][1][0][1] - 0.05) if i + 1 < len(out) else pg[-1][1] + 1.5
        res.append((pg[0][1] - 0.08, end, pg))
    return res


PAGES = pages()


def draw_overlay(c, t, name, VP, fx):
    def proj(p):
        q, z = L.project(VP, [p], W, H)
        return tuple(q[0]) if z[0] < 1 else None
    if name == "hero":
        O.title_card(c, t, wt("02", "explode") + 0.75, SH["cut"] - 0.15)
    if name == "cut":
        O.label(c, t, wt("03", "fourteen") - 0.1, proj((0.09, 0.97, 0.0)), "≈ 14% water", "LOCKED IN THE STARCH", side=1, dx=150, dy=-330,
                t1=en("03") + 0.5)
        O.label(c, t, wt("04", "shell") - 0.1, proj((-0.30, 0.92, 0.0)), "The hull", "ALMOST AIRTIGHT", side=-1, dx=150, dy=-300)
    if name == "fire":
        tv = 20 + 80 * ss(prog(t, st("06"), wt("06", "hundred") + 0.4))
        O.thermometer(c, t, st("06") - 0.2, SH["inside"] + 0.2, tv)
    if name == "inside":
        tv = 100 + 70 * ss(prog(t, SH["inside"], SH["climax"]))
        p = 1 + 8.3 * ss(prog(t, st("07"), wt("07", "nine") + 0.25)) + 0.15 * math.sin(t * 7) * prog(t, wt("07", "nine"), 99)
        O.gauge(c, t, st("07") - 0.3, SH["climax"] - 0.2, min(p, 9.6), y=360, r=150)
        O.label(c, t, wt("08", "gel"), proj((0.08, 0.84, 0.0)), "Molten starch", "GEL, NOT GRAINS", side=1, dx=120, dy=330)
        O.thermometer(c, t, SH["inside"], SH["climax"] - 0.2, tv, y=900) if t < st("07") - 0.4 else None
    if name == "climax":
        tv = 170 + 10 * ss(prog(t, SH["climax"], wt("09", "eighty") + 0.3))
        O.thermometer(c, t, SH["climax"], SH["slow"] - 0.1, tv)
    if name == "slow":
        O.rec(c, t, SH["slow"] + 0.1, SH["sound"])
        O.big_number(c, t, wt("11", "forty") - 0.1, en("11") + 0.4, "40×", "BIGGER, IN A BLINK", y=380)
    if name == "sound":
        O.waveform(c, t, SH["sound"] + 0.2, SH["cork"] - 0.2, y=420)
        O.text(c, "Shell cracking", O.W / 2, 620, O.serif(56, 600, True), O.IVORY,
               O.ease(O.prog(t, wt("12", "isn't"), wt("12", "isn't") + 0.3)) * (1 - O.prog(t, SH["cork"] - 0.4, SH["cork"])), "center")
        O.strike(c, t, wt("12", "cracking") + 0.1, O.W / 2 - 190, 604, O.W / 2 + 190, 604)
        O.text(c, "Steam escaping", O.W / 2, 720, O.serif(70, 600, True), O.GOLD,
               O.ease(O.prog(t, wt("12", "steam"), wt("12", "steam") + 0.3)) * (1 - O.prog(t, SH["cork"] - 0.4, SH["cork"])), "center")
    if name == "jump":
        base, up = fx["jump"]
        pts = []
        for k in range(40):
            u = k / 39 * 1.6
            hy = max(0.2, 0.2 + 3.2 * u - 1.6 * u * u)
            q = proj((-0.2 + 0.6 * u, hy, 0))
            if q:
                pts.append(q)
        O.dashed_path(c, pts, t, wt("13", "flips"), 1.0)
        O.big_number(c, t, wt("13", "thousandths") - 0.2, en("13") + 0.4, "≈ 3 ms", "TO LEAP", y=500)
    if name == "duds":
        d = DUDS[0]
        O.label(c, t, wt("14", "leaked") - 0.1, proj((d[0], 0.62, d[1])), "A leaky hull", "NO PRESSURE, NO POP", side=-1, dx=160, dy=-260)
    if name == "end":
        O.end_card(c, t, SH["end"] + 0.1, SH["stinger"] - 0.1)


def captions(c, t):
    for t0, t1, pg in PAGES:
        if t0 <= t < t1:
            act = max([k for k, (_, s) in enumerate(pg) if s <= t] or [0])
            a = O.ease(O.prog(t, t0, t0 + 0.2)) * (1 - O.prog(t, t1 - 0.2, t1))
            O.caption(c, [w for w, _ in pg], act, 1690, a)


# ---------------------------------------------------------------- frame
_R = None
MOTES = O.Motes()


def renderer():
    global _R
    if _R is None:
        _R = L.Lux(W, H, SS)
        _R.clear_col = (0.0035, 0.0028, 0.0022)
    return _R


def frame(t):
    name = shot_at(t)
    if name == "black":
        img = np.zeros((H, W, 3), np.float32)
        VP = None
        fx = {}
    else:
        cam, light, opaque, trans, lights, fx = SHOTS[name](t)
        R = renderer()
        img, depth, VP = R.render(cam, light, opaque, trans, lights)
        img = np.nan_to_num(img, nan=0.0, posinf=20.0, neginf=0.0)
        depth = np.nan_to_num(depth, nan=100.0, posinf=100.0)
        fp = fx.get("focus_pt", cam["target"])
        focus = float(np.linalg.norm(np.subtract(cam["eye"], fp)))
        img = L.depth_of_field(img, depth, focus, fx.get("dof", 10) * focus * SS / 1.5)
        img = L.bloom(img, 1.6, 0.2)
        img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
        img = L.tonemap(img, fx.get("exposure", 0.9))
        img = L.vignette(img, 0.38)
        img = L.grade(img.astype(np.float32), t)
    rgba = np.dstack([(img * 255).astype(np.uint8), np.full((H, W), 255, np.uint8)])
    surf = skia.Surface(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType)
    with surf as c:
        if name != "black":
            MOTES.draw(c, t, fx.get("motes", 0.5))
            O.bottom_scrim(c, 1.0)
            draw_overlay(c, t, name, VP, fx)
        # pop flashes and dips
        for tf, a in ((SH["slow"], 0.55), (wt("12", "cork") + 0.05, 0.25), (SH["stinger"] + 0.9, 0.35)):
            O.flash(c, a * math.exp(-max(0, t - tf) * 9) * (t >= tf))
        for k in ORDER[1:]:
            d = abs(t - SH[k])
            if k in ("slow", "black"):
                continue
            O.fade(c, 0.9 * max(0, 1 - d / 0.12))
        O.fade(c, 1 - prog(t, 0, 0.8))
        captions(c, t)
    out = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]
    return np.ascontiguousarray(out)


def _job(i):
    return frame(i / FPS).tobytes()


def render(procs=3, name="ep03_popcorn"):
    import sound
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    bdir = os.path.join(HERE, "build")
    wav = sound.render_audio(os.path.join(bdir, "mix.wav"), sys.modules[__name__])
    silent = os.path.join(bdir, f"{name}_video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
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
        d = os.path.join(HERE, "build", "stills")
        os.makedirs(d, exist_ok=True)
        for s in sys.argv[sys.argv.index("--still") + 1].split(","):
            p = os.path.join(d, f"t{float(s):05.2f}.png")
            cv2.imwrite(p, frame(float(s))[:, :, ::-1])
            print(p, shot_at(float(s)))
    else:
        render(int(os.environ.get("PROCS", "3")))
