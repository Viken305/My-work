"""Meshes for the popcorn episode. Units: centimetres, y up."""
import math
from functools import lru_cache

import numpy as np

from lux import Geo, Rx, Ry, Rz, S, T, box, cat, cylinder, lathe, rough, sphere, srgb, star_mesh, torus

# ---------------------------------------------------------------- materials (linear colours)
GOLD_HULL = (232, 138, 26)
CROWN = (246, 214, 120)
TIP = (205, 168, 116)
CREAM = (250, 243, 224)
STARCH = (238, 220, 170)
GERM = (236, 206, 130)
WATER = (90, 170, 255)
COPPER = (236, 140, 96)
STEEL = (205, 207, 212)
BRASS = (228, 180, 90)
SLATE = (38, 40, 44)
BUTTER = (255, 196, 64)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- the kernel (a flat, tooth-shaped seed)
Y0, Y1 = -0.56, 0.42           # tip .. crown
WX, WZ = 0.40, 0.22            # half-width, half-thickness at the widest point


def kt(y):
    return (np.asarray(y) - Y0) / (Y1 - Y0)


def kwidth(t):
    """Half-width across the broad face at height t (0 tip .. 1 crown)."""
    t = np.clip(t, 0, 1)
    body = 0.11 + 0.89 * np.sin(np.pi / 2 * np.clip(t / 0.78, 0, 1)) ** 0.9
    top = np.sqrt(np.clip(1 - ((t - 0.74) / 0.26) ** 2, 0, 1))
    return WX * body * np.where(t > 0.74, top, 1.0)


def param_mesh(fn, nu, nv, cfun, **kw):
    """Surface from fn(U, V) -> (..., 3) over U in [0, 2pi) (closed) and V in [0, 1]; smooth normals."""
    U = np.linspace(0, 2 * np.pi, nu + 1)
    V = np.linspace(0, 1, nv + 1)
    UU, VV = np.meshgrid(U, V, indexing="ij")
    X = fn(UU, VV)
    du = np.gradient(X, axis=0)
    dv = np.gradient(X, axis=1)
    N = np.cross(du, dv)
    # poles: fall back to the axis direction
    nrm = np.linalg.norm(N, axis=-1, keepdims=True)
    N = np.where(nrm > 1e-9, N / np.maximum(nrm, 1e-12), 0)
    N[:, 0] = (0, -1, 0)
    N[:, -1] = (0, 1, 0)
    c = X.mean(axis=(0, 1))
    if ((X - c) * N).sum() < 0:
        N = -N
    tris, nr, uv = [], [], []
    for i in range(nu):
        for j in range(nv):
            a, b, cc, d = (i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)
            tris += [[X[a], X[b], X[cc]], [X[a], X[cc], X[d]]]
            nr += [[N[a], N[b], N[cc]], [N[a], N[cc], N[d]]]
            uv += [((UU[a] + UU[cc]) / 2, (VV[a] + VV[cc]) / 2)] * 2
    uv = np.array(uv)
    return Geo(np.array(tris, np.float32), np.array(nr, np.float32), cfun(uv[:, 0], uv[:, 1]), **kw)


def kernel_xyz(U, V):
    y = Y0 + (Y1 - Y0) * V
    t = V
    w = kwidth(t)
    th = w * (WZ / WX) * (0.85 + 0.15 * t) + 0.012
    x = w * np.cos(U)
    z = th * np.sin(U)
    y = y - 0.01 * np.exp(-(x / 0.12) ** 2) * np.clip((t - 0.9) / 0.1, 0, 1)   # dent in the crown
    return np.stack([x, y, z], -1)


def kernel_cols(U, V, seed=0):
    rng = np.random.default_rng(seed)
    crown, side, tip, germ = srgb(CROWN), srgb(GOLD_HULL), srgb(TIP), srgb((246, 222, 150))
    k1 = smoothstep(0.80, 0.95, V)[:, None]
    k2 = smoothstep(0.16, 0.04, V)[:, None]
    c = side * (1 - k1) + crown * k1
    c = c * (1 - k2) + tip * k2
    # the germ shows through the broad (+z) face as a pale teardrop
    gx = np.cos(U) / 0.5
    gy = (V - 0.42) / 0.26
    gm = (np.sin(U) > 0) * np.clip((1 - (gx * gx + gy * gy)) * 1.4, 0, 1) ** 1.5
    c = c * (1 - 0.45 * gm[:, None]) + germ * 0.45 * gm[:, None]
    c *= (1 + rng.normal(0, 0.025, (len(U), 1)))
    return c


@lru_cache(maxsize=8)
def kernel(seed=0, res=1.0):
    g = param_mesh(kernel_xyz, int(64 * res), int(40 * res), lambda U, V: kernel_cols(U, V, seed), S=0.9, M=-0.06)
    return rough(g, 0.16)


def k_copy(seed=0, res=1.0):
    return clone(kernel(seed, res))


# ---------------------------------------------------------------- the cutaway (kernel sliced along its broad face, z = 0)
def cutaway(heat=0.0, gel=0.0, water_glow=0.0, shell_glow=0.0, t=0.0, res=1.0):
    """Half kernel seen from +z. heat 0..1 swells the water pockets into steam; gel 0..1 melts the starch."""
    full = k_copy(0, res)
    cen = full.P.mean(axis=1)
    keep = cen[:, 2] < 0.002
    hull = rough(Geo(full.P[keep], full.N[keep], full.C[keep], S=0.9, M=-0.06), 0.16)
    nt, ns = 110, 56
    tt = np.linspace(0, 1, nt + 1)
    ss = np.linspace(-1, 1, ns + 1)
    shell_c, horny, floury, germ_c = srgb((236, 150, 40)), srgb((240, 200, 120)), srgb((250, 242, 222)), srgb((246, 224, 150))
    gel_c = srgb((255, 226, 150))
    tris, cols, spec, ro, em = [], [], [], [], []
    for i in range(nt):
        for j in range(ns):
            t0, t1, s0, s1 = tt[i], tt[i + 1], ss[j], ss[j + 1]
            q = []
            for t_, s_ in ((t0, s0), (t1, s0), (t1, s1), (t0, s1)):
                x = s_ * kwidth(t_) * 0.995
                y = Y0 + (Y1 - Y0) * t_
                if t_ > 0.9:
                    y -= 0.01 * math.exp(-(x / 0.12) ** 2) * (t_ - 0.9) / 0.1
                q.append((x, y, 0.001))
            tm, sm = (t0 + t1) / 2, (s0 + s1) / 2
            w = float(kwidth(tm))
            edge = min((1 - abs(sm)) * w, (1 - tm) * (Y1 - Y0), tm * (Y1 - Y0))
            if edge < 0.032:
                c, sp, r_, e = shell_c, 0.8, 0.2, shell_glow * 2.2
            else:
                gx, gy = (sm + 0.15) / 0.45, (tm - 0.36) / 0.24
                if gx * gx + gy * gy < 1:
                    c = germ_c
                elif (sm / 0.7) ** 2 + ((tm - 0.86) / 0.36) ** 2 < 1:
                    c = floury
                else:
                    c = horny
                c = c * (1 - gel * 0.65) + gel_c * gel * 0.65
                sp, r_, e = 0.12 + 0.88 * gel, 0.75 - 0.65 * gel, 0.04 * gel
            for tri in ((q[0], q[1], q[2]), (q[0], q[2], q[3])):
                tris.append(tri); cols.append(c); spec.append(sp); ro.append(r_); em.append(e)
    P = np.array(tris, np.float32)
    N = np.zeros_like(P)
    N[..., 2] = 1.0
    if gel > 0:
        N[..., 0] += 0.07 * gel * np.sin(P[..., 1] * 45 + t * 6)
        N[..., 1] += 0.07 * gel * np.cos(P[..., 0] * 40 + t * 5)
        N /= np.linalg.norm(N, axis=-1, keepdims=True)
    cap = Geo(P, N, np.array(cols), E=np.array(em), S=np.array(spec), M=-0.3 * gel)
    cap.Ht = np.repeat(np.array(ro, np.float32)[:, None], 3, 1)
    rng = np.random.default_rng(5)
    pos = []
    while len(pos) < 30:
        tq, sq = rng.uniform(0.18, 0.9), rng.uniform(-0.75, 0.75)
        pos.append((sq * float(kwidth(tq)), Y0 + (Y1 - Y0) * tq))
    beads = []
    for k, (x, y) in enumerate(pos):
        jit = 0.006 * heat * math.sin(t * 37 + k * 1.3)
        r0 = 0.016 + 0.006 * (k % 3)
        r = r0 * (1 + 0.7 * heat)
        b = sphere(r, 14, 9, WATER).xf(S(1, 1, 0.45)).xf(T(x + jit, y - jit, 0.004))
        b.set(S=1.0, E=0.2 + 1.0 * water_glow + 0.5 * heat, M=-0.4)
        b.C = np.broadcast_to(srgb((170, 215, 255)) if heat > 0.3 else srgb(WATER), b.C.shape).copy()
        beads.append(rough(b, 0.05))
    return cat([hull, cap] + beads)


# ---------------------------------------------------------------- popped popcorn: a union of puffed-up blobs
@lru_cache(maxsize=64)
def _lobes(seed):
    r = np.random.default_rng(seed)
    n = int(r.integers(5, 9))
    dirs = r.normal(0, 1, (n, 3))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    off = r.uniform(0.28, 0.5, n)
    rad = r.uniform(0.34, 0.52, n)
    w = r.normal(0, 1, (6, 3)) * 7
    ph = r.uniform(0, 6.3, 6)
    hull_dir = r.normal(0, 1, 3)
    hull_dir /= np.linalg.norm(hull_dir)
    return dirs, off, rad, w, ph, hull_dir


def popped_r(D, seed, g=1.0):
    dirs, off, rad, w, ph, _ = _lobes(seed)
    r = np.full(len(D), 0.3 + 0.12 * g)
    for c, o, rr in zip(dirs, off * g, rad * (0.55 + 0.45 * g)):
        cd = D @ c
        disc = rr * rr - o * o * (1 - cd * cd)
        hit = np.where(disc > 0, o * cd + np.sqrt(np.maximum(disc, 0)), 0)
        r = np.maximum(r, hit)
    bump = sum(np.sin(D @ w[i] + ph[i]) for i in range(6)) / 6
    return r * (1 + 0.035 * g * bump)


def popped_cols(D, seed, g=1.0):
    _, _, _, _, _, hd = _lobes(seed)
    rng = np.random.default_rng(seed + 7)
    base = srgb(CREAM) * (1 + rng.normal(0, 0.03, (len(D), 1)))
    tint = srgb((246, 224, 168))
    k = np.clip((D @ np.array([0.3, -0.6, 0.2])) * 0.5 + 0.3, 0, 1)[:, None]
    c = base * (1 - k * 0.45) + tint * k * 0.45
    flake = (D @ hd > 0.9) & (rng.uniform(0, 1, len(D)) > 0.25)
    c[flake] = srgb((200, 120, 40))
    return c


@lru_cache(maxsize=256)
def _popped_cached(seed, gq, res):
    g = gq / 100.0
    m = star_mesh(lambda D: popped_r(D, seed, g), int(64 * res), int(40 * res), cfun=lambda D: popped_cols(D, seed, g), S=0.35, M=-0.3)
    return rough(m, 0.55)


def popped(seed=0, g=1.0, res=1.0):
    return _popped_cached(seed, int(round(g * 100)), res)


def clone(g):
    out = Geo.__new__(Geo)
    for k in ("P", "N", "C", "E", "S", "A", "Ht", "M"):
        setattr(out, k, getattr(g, k).copy())
    return out


def place(g, M):
    return clone(g).xf(M)


# ---------------------------------------------------------------- the hull opening like petals (slow-motion pop)
def hull_petals(open_, seed=0, res=1.0, spin=0.0):
    """Kernel hull cut into 7 petals that peel back from the crack (open_ 0..1+), plus flung-off fragments."""
    g = k_copy(seed, res)
    cen = g.P.mean(axis=1)
    ang = np.arctan2(cen[:, 2], cen[:, 0])
    sector = ((ang + np.pi) / (2 * np.pi) * 7).astype(int) % 7
    parts = []
    rng = np.random.default_rng(seed + 3)
    for s in range(7):
        m = sector == s
        if not m.any():
            continue
        part = Geo(g.P[m], g.N[m], g.C[m], S=0.9, M=-0.12)
        part = rough(part, 0.16)
        mid = (s + 0.5) / 7 * 2 * np.pi - np.pi
        axis_dir = np.array([-math.sin(mid), 0, math.cos(mid)])  # tangent: rotate the petal outwards about it
        pivot = np.array([math.cos(mid) * 0.12, -0.42, math.sin(mid) * 0.12])
        a = open_ * (1.5 + 0.4 * rng.uniform())
        fly = min(0.5, max(0.0, open_ - 0.55) * (0.4 + 0.5 * rng.uniform()))
        # Rodrigues rotation about axis_dir through pivot
        k = axis_dir
        K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
        R3 = np.eye(3) + math.sin(-a) * K + (1 - math.cos(-a)) * K @ K
        M = np.eye(4, dtype=np.float32)
        M[:3, :3] = R3
        M[:3, 3] = pivot - R3 @ pivot + np.array([math.cos(mid), 0.4, math.sin(mid)]) * fly
        parts.append(part.xf(Ry(spin) @ M))
    return cat(parts)


# ---------------------------------------------------------------- copper pan, burner, flame, oil
@lru_cache(maxsize=2)
def pan_static():
    outer = [(0, -0.02), (8.6, -0.02), (9.15, 0.25), (9.5, 1.4), (9.9, 4.4), (10.2, 4.95), (10.25, 5.1)]
    inner = [(10.05, 5.1), (9.75, 4.6), (9.3, 1.5), (8.9, 0.6), (8.3, 0.36), (0, 0.36)]
    o = lathe(outer, 96, COPPER, S=1.0, M=1.0)
    o = rough(o, 0.26)
    i = lathe(inner, 96, STEEL, S=1.0, M=1.0)
    i = rough(i, 0.32)
    rim = torus(10.15, 0.12, 96, 8, rgb=BRASS, S=1.0, M=1.0).xf(Rx(math.pi / 2)).xf(T(0, 5.08, 0))
    rim = rough(rim, 0.2)
    handle = cylinder(0.55, 0, 16, 20, BRASS, S=1.0, M=1.0).xf(Rz(-math.pi / 2 + 0.12)).xf(T(9.9, 3.6, 0))
    handle = rough(handle, 0.3)
    rivets = cat([sphere(0.3, 12, 8, BRASS, S=1.0, M=1.0).xf(T(9.95, 3.6 + dy, dz)) for dy, dz in ((0.5, 0.0), (-0.5, 0.0))])
    return cat([o, i, rim, handle, rough(rivets, 0.25)])


@lru_cache(maxsize=2)
def stove_static():
    top = box(-60, 60, -2.4, -2.0, -60, 60, (12, 12, 14), jit=0.0, S=1.0, M=0.0)
    top = rough(top, 0.08)
    cap = lathe([(0, -2.0), (4.2, -2.0), (4.2, -1.3), (3.6, -1.1), (0, -1.1)], 64, (30, 30, 32), S=0.5, M=1.0)
    cap = rough(cap, 0.5)
    arms = []
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        arm = box(3.0, 13.5, -0.65, -0.05, -0.4, 0.4, (26, 26, 28), jit=0.0, S=0.4, M=1.0).xf(Ry(a))
        arms.append(rough(arm, 0.6))
    return cat([top, cap] + arms)


def flame(t, level=1.0, n=28):
    """Ring of blue gas flame tongues under the pan (emissive, transparent)."""
    out = []
    if level <= 0:
        return None
    for k in range(n):
        a = 2 * math.pi * k / n
        h = (0.7 + 0.25 * math.sin(t * 23 + k * 1.7) + 0.15 * math.sin(t * 41 + k * 3.1)) * level
        tongue = cylinder(0.22, 0, h, 8, (90, 140, 255), r_top=0.02, caps=(False, False))
        tongue.xf(Rz(-0.9)).xf(Ry(-a)).xf(T(3.9 * math.cos(a), -1.15, 3.9 * math.sin(a)))
        tongue.set(E=6.0 * level, A=0.75, S=0.0)
        out.append(tongue)
        core = cylinder(0.12, 0, h * 0.5, 6, (180, 210, 255), r_top=0.01, caps=(False, False))
        core.xf(Rz(-0.9)).xf(Ry(-a)).xf(T(3.85 * math.cos(a), -1.15, 3.85 * math.sin(a)))
        core.set(E=10.0 * level, A=0.9, S=0.0)
        out.append(core)
    return cat(out)


def oil(t, r=8.85, y=0.45, shimmer=1.0):
    n, m = 72, 10
    tris, nr = [], []
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        for j in range(m):
            r0, r1 = r * j / m, r * (j + 1) / m
            pts = [(r0, a0), (r1, a0), (r1, a1), (r0, a1)]
            P = [(rr * math.cos(aa), y, rr * math.sin(aa)) for rr, aa in pts]
            Nn = []
            for rr, aa in pts:
                x, z = rr * math.cos(aa), rr * math.sin(aa)
                nx = 0.06 * shimmer * math.sin(x * 2.3 + t * 3.1) * math.cos(z * 1.7 - t * 2.3)
                nz = 0.06 * shimmer * math.cos(x * 1.9 - t * 2.7) * math.sin(z * 2.1 + t * 3.3)
                v = np.array([nx, 1, nz])
                Nn.append(v / np.linalg.norm(v))
            tris += [[P[0], P[1], P[2]], [P[0], P[2], P[3]]]
            nr += [[Nn[0], Nn[1], Nn[2]], [Nn[0], Nn[2], Nn[3]]]
    g = Geo(np.array(tris), np.array(nr), srgb((235, 205, 140)), S=0.6, A=0.08, M=0.0)
    return rough(g, 0.03)


# ---------------------------------------------------------------- serving: slate, bowl
@lru_cache(maxsize=2)
def slate_static():
    s = box(-40, 40, -1.2, 0.0, -30, 30, SLATE, jit=0.0, S=0.35, M=0.0)
    s = rough(s, 0.7)
    floor = box(-200, 200, -6.0, -1.2, -200, 200, (20, 16, 13), jit=0.0, S=0.2)
    floor = rough(floor, 0.8)
    return cat([s, floor])


@lru_cache(maxsize=2)
def bowl_static():
    out = [(0, 0.0), (5.0, 0.0), (5.4, 0.4), (8.4, 4.2), (10.6, 7.6), (11.0, 8.0)]
    inn = [(10.6, 8.0), (10.1, 7.5), (7.9, 4.3), (4.8, 1.2), (0, 0.9)]
    o = rough(lathe(out, 96, (22, 22, 24), S=0.5, M=0.0), 0.55)
    i = rough(lathe(inn, 96, (16, 16, 18), S=1.0, M=0.0), 0.12)
    rim = rough(torus(10.8, 0.22, 96, 8, rgb=(28, 28, 30), S=0.8).xf(Rx(math.pi / 2)).xf(T(0, 8.0, 0)), 0.2)
    return cat([o, i, rim])


@lru_cache(maxsize=2)
def bowl_pile(n=120, seed=11):
    """Popcorn heaped in the bowl (bowl interior is a cone-ish surface; heap rises above the rim)."""
    rng = np.random.default_rng(seed)
    parts = []
    tries = 0
    pos = []
    while len(pos) < n and tries < 5000:
        tries += 1
        x, z = rng.uniform(-9.5, 9.5, 2)
        rr = math.hypot(x, z)
        if rr > 9.6:
            continue
        top = 9.6 + 3.2 * (1 - (rr / 9.6) ** 2)
        y = rng.uniform(2.5, top)
        if any((x - a) ** 2 + (y - b) ** 2 + (z - c) ** 2 < 2.3 for a, b, c in pos):
            continue
        pos.append((x, y, z))
    for k, (x, y, z) in enumerate(pos):
        s = rng.uniform(1.25, 1.6)
        M = T(x, y, z) @ Ry(rng.uniform(0, 6.3)) @ Rx(rng.uniform(0, 6.3)) @ S(s)
        parts.append(place(popped(k % 24, 1.0, 0.8), M))
    return cat(parts), pos


# ---------------------------------------------------------------- champagne
@lru_cache(maxsize=2)
def bottle_static():
    prof = [(0, 0), (4.3, 0), (4.45, 0.4), (4.45, 17.5), (4.2, 19.5), (3.0, 22.5), (1.65, 25.0), (1.5, 27.0), (1.5, 29.6),
            (1.7, 29.8), (1.7, 30.4), (1.45, 30.6)]
    glass = rough(lathe(prof, 72, (6, 34, 18), S=1.0, M=0.0), 0.03)
    foil_p = [(1.62, 24.2), (1.56, 26.5), (1.6, 29.7), (1.82, 29.9), (1.82, 30.5), (1.5, 30.7)]
    foil = lathe(foil_p, 72, (220, 170, 70), S=1.0, M=1.0)
    rng = np.random.default_rng(2)
    foil.N = foil.N + rng.normal(0, 0.12, foil.N.shape).astype(np.float32)
    foil.N /= np.linalg.norm(foil.N, axis=-1, keepdims=True)
    foil = rough(foil, 0.3)
    label = lathe([(4.47, 6.0), (4.47, 12.5)], 72, (236, 226, 200), S=0.3)
    label = rough(label, 0.6)
    return cat([glass, foil, label])


def cork(M):
    c = cylinder(0.95, 0, 2.2, 28, (196, 160, 110), S=0.2)
    top = lathe([(0.95, 2.2), (1.25, 2.5), (1.25, 3.0), (0, 3.15)], 28, (180, 140, 92), S=0.2)
    return rough(cat([c, top]), 0.8).xf(M)


# ---------------------------------------------------------------- butter + salt + steam
def butter_stream(t0, t, start, end, thick=0.36):
    """A pour of melted butter falling from `start` and landing at `end` (grows from the top for t0..)."""
    if t < t0:
        return None
    u = min(1.0, (t - t0) / 0.5)
    pts = []
    start, end = np.asarray(start, float), np.asarray(end, float)
    for k in range(24):
        s = k / 23 * u
        p = start + (end - start) * s
        p[0] += 0.4 * math.sin(s * 3 + t * 2.0)
        pts.append(p)
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        d = b - a
        L = np.linalg.norm(d)
        if L < 1e-4:
            continue
        seg = cylinder(thick, 0, L, 12, BUTTER, caps=(False, False))
        # align +y to d
        y = d / L
        x = np.cross(y, [0, 0, 1.0])
        if np.linalg.norm(x) < 1e-6:
            x = np.array([1.0, 0, 0])
        x /= np.linalg.norm(x)
        z = np.cross(x, y)
        M = np.eye(4, dtype=np.float32)
        M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, a
        seg.xf(M)
        out.append(seg)
    g = cat(out)
    if g is None:
        return None
    g.set(S=1.0, E=0.0, M=-0.3)
    return rough(g, 0.06)


def salt(t, t0, n=60, seed=4, center=(0, 22, 0), floor=11.5):
    if t < t0:
        return None
    rng = np.random.default_rng(seed)
    out = []
    for k in range(n):
        x, z = rng.normal(0, 2.2, 2)
        delay = rng.uniform(0, 1.6)
        lt = t - t0 - delay
        if lt < 0:
            continue
        y = center[1] - 3.0 * lt - 1.0 * lt * lt
        if y < floor:
            continue
        s = rng.uniform(0.12, 0.3)
        flake = box(-s, s, -s * 0.25, s * 0.25, -s * 0.8, s * 0.8, (250, 250, 252), jit=0.0, S=1.0, M=-0.5)
        flake.xf(Ry(rng.uniform(0, 6) + lt * 3)).xf(Rx(rng.uniform(0, 6) + lt * 2)).xf(T(center[0] + x, y, center[2] + z))
        out.append(rough(flake, 0.05))
    return cat(out)


def puffs(center, t, t0, n=10, size=1.0, seed=0, rise=1.0, life=2.5, alpha=0.12, warm=False):
    """Steam: soft transparent spheres billowing up from a point."""
    if t < t0:
        return None
    rng = np.random.default_rng(seed)
    out = []
    for k in range(n):
        lt = t - t0 - rng.uniform(0, life * 0.5)
        if lt < 0 or lt > life:
            continue
        u = lt / life
        d = rng.normal(0, 1, 3)
        d[1] = abs(d[1]) * 1.5 + 0.8
        d /= np.linalg.norm(d)
        p = np.asarray(center, float) + d * size * (0.3 + 2.2 * u ** 0.6) * rise
        r = size * (0.25 + 0.9 * u ** 0.7)
        s = sphere(r, 14, 9, (240, 240, 250) if not warm else (255, 238, 210))
        s.xf(T(*p))
        s.set(A=alpha * (1 - u) ** 1.5 * min(1, lt * 6), S=0.0, E=0.06)
        out.append(rough(s, 1.0))
    return cat(out)
