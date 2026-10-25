"""Style C: low-poly 3D. Flat-shaded faceted models, soft dusk lighting, orbiting camera, clean caption chips.

A tiny painter's-algorithm 3D renderer (perspective camera, one sun, per-face jitter) drawn with Skia.
Beat: closed microwave (mug turning behind the glass) -> door swings open, roof lifts off ->
the floor rises into a 3D heat map under a standing-wave sheet -> map flattens, the turntable carries
the mug through hot and cold spots.
"""
import math

import numpy as np
import skia

from kit import (W, H, blur, clamp, fill, hexc, in_out, lerp, measure, mix, out_back, out_cubic, prog, smooth, stroke,
                 text)

DURATION = 12.0

SKY_TOP = hexc("1C2440")
SKY_BOT = hexc("47507A")
WALL = hexc("39456A")
COUNTER = hexc("C98B5A")
BODY = hexc("8FD3C1")
TRIM = hexc("2D3142")
GLASS = hexc("141826")
CAVITY = hexc("F2D9A7")
MUG = hexc("E4572E")
PLATE = hexc("DDE7EE")
COLD = hexc("3D7BFF")
WARM = hexc("FFC145")
HOT = hexc("FF4D3D")
INK = hexc("F7F4EE")
PALETTE = [("Dusk sky", SKY_TOP), ("Counter", COUNTER), ("Retro mint", BODY), ("Cavity light", CAVITY),
           ("Cold", COLD), ("Warm", WARM), ("Hot", HOT)]
FONTS_USED = [("bold", "Inter Display Bold (captions)")]

LIGHT = np.array([-0.5, 0.9, 0.6]) / np.linalg.norm([-0.5, 0.9, 0.6])
FOCAL = 1900.0

# cavity bounds (world units; microwave body is x -1..1, y 0..1.2, z -0.7..0.7, front faces +z)
CX0, CX1, CY0, CY1, CZ0, CZ1 = -0.94, 0.40, 0.06, 1.14, -0.64, 0.70
PLATE_C = ((CX0 + CX1) / 2, 0.0)


def heat_at(x, z):
    u = (x - CX0) / (CX1 - CX0)
    v = (z - CZ0) / (CZ1 - CZ0)
    return clamp(0.06 + math.sin(3 * math.pi * u) ** 2 * math.sin(2 * math.pi * v) ** 2)


def heat_col(h):
    return mix(COLD, WARM, h / 0.55) if h < 0.55 else mix(WARM, HOT, (h - 0.55) / 0.45)


# ---------------------------------------------------------------- camera
KEYS = [  # t, distance, yaw deg, pitch deg, target
    (0.0, 6.4, -34, 13, (0.0, 0.55, 0.0)),
    (3.0, 5.4, -16, 18, (0.0, 0.6, 0.0)),
    (5.5, 5.1, 10, 44, (-0.3, 0.45, 0.0)),
    (8.5, 4.9, 22, 56, (-0.3, 0.4, 0.0)),
    (12.0, 5.1, 34, 52, (-0.25, 0.45, 0.0)),
]


def catmull(t, idx):
    ts = [k[0] for k in KEYS]
    vals = [np.atleast_1d(np.array(k[idx], dtype=float)) for k in KEYS]
    i = max(0, min(len(ts) - 2, max(j for j in range(len(ts)) if t >= ts[j]) if t >= ts[0] else 0))
    u = smooth(prog(t, ts[i], ts[i + 1])) * 0.35 + prog(t, ts[i], ts[i + 1]) * 0.65
    p0, p1, p2 = vals[max(0, i - 1)], vals[i], vals[i + 1]
    p3 = vals[min(len(vals) - 1, i + 2)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


class Cam:
    def __init__(self, t):
        d, yaw, pitch = catmull(t, 1)[0], math.radians(catmull(t, 2)[0]), math.radians(catmull(t, 3)[0])
        self.target = catmull(t, 4)
        self.eye = self.target + d * np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)])
        f = self.target - self.eye
        self.f = f / np.linalg.norm(f)
        r = np.cross(self.f, [0, 1, 0])
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.f)

    def to_cam(self, p):
        q = np.asarray(p) - self.eye
        return np.array([q @ self.r, q @ self.u, q @ self.f])

    def project(self, p):
        x, y, z = self.to_cam(p)
        z = max(z, 1e-3)
        return W / 2 + FOCAL * x / z, H / 2 - FOCAL * y / z, z


# ---------------------------------------------------------------- geometry
class Face:
    __slots__ = ("pts", "rgb", "alpha", "cull", "layer", "emit", "normal")

    def __init__(self, pts, rgb, normal, alpha=1.0, cull=True, layer=2, emit=0.0):
        self.pts = [np.asarray(p, dtype=float) for p in pts]
        self.rgb, self.alpha, self.cull, self.layer, self.emit = rgb, alpha, cull, layer, emit
        self.normal = np.asarray(normal, dtype=float)


def jitter(rgb, seed, amt=0.05):
    k = (math.sin(seed * 12.9898) * 43758.5453) % 1.0
    return mix(rgb, (255, 255, 255) if k > 0.5 else (0, 0, 0), amt * abs(k - 0.5) * 2)


def box(x0, x1, y0, y1, z0, z1, rgb, seed=0, **kw):
    v = lambda x, y, z: (x, y, z)
    faces = [
        ([v(x0, y1, z0), v(x1, y1, z0), v(x1, y1, z1), v(x0, y1, z1)], (0, 1, 0)),
        ([v(x0, y0, z0), v(x1, y0, z0), v(x1, y0, z1), v(x0, y0, z1)], (0, -1, 0)),
        ([v(x0, y0, z1), v(x1, y0, z1), v(x1, y1, z1), v(x0, y1, z1)], (0, 0, 1)),
        ([v(x0, y0, z0), v(x1, y0, z0), v(x1, y1, z0), v(x0, y1, z0)], (0, 0, -1)),
        ([v(x1, y0, z0), v(x1, y1, z0), v(x1, y1, z1), v(x1, y0, z1)], (1, 0, 0)),
        ([v(x0, y0, z0), v(x0, y1, z0), v(x0, y1, z1), v(x0, y0, z1)], (-1, 0, 0)),
    ]
    return [Face(p, jitter(rgb, seed + i), n, **kw) for i, (p, n) in enumerate(faces)]


def cylinder(cx, cz, r, y0, y1, n, rgb, rot=0.0, seed=0, **kw):
    out = []
    ring = [(cx + r * math.cos(rot + 2 * math.pi * i / n), cz + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    for i in range(n):
        (ax, az), (bx, bz) = ring[i], ring[(i + 1) % n]
        mid = rot + 2 * math.pi * (i + 0.5) / n
        out.append(Face([(ax, y0, az), (bx, y0, bz), (bx, y1, bz), (ax, y1, az)], jitter(rgb, seed + i, 0.08),
                        (math.cos(mid), 0, math.sin(mid)), **kw))
    out.append(Face([(x, y1, z) for x, z in ring], jitter(rgb, seed + 99, 0.04), (0, 1, 0), **kw))
    return out


def rot_y(faces, pivot, ang):
    c, s = math.cos(ang), math.sin(ang)
    px, _, pz = pivot
    for f in faces:
        f.pts = [np.array([px + c * (p[0] - px) + s * (p[2] - pz), p[1], pz - s * (p[0] - px) + c * (p[2] - pz)]) for p in f.pts]
        n = f.normal
        f.normal = np.array([c * n[0] + s * n[2], n[1], -s * n[0] + c * n[2]])
    return faces


def shift(faces, d):
    for f in faces:
        f.pts = [p + np.asarray(d) for p in f.pts]
    return faces


def tri_grid(xs, ys, fn, rgb, normal, seed, layer=0, amt=0.10):
    """Plane split into jitter-shaded triangles for the faceted look. fn(a, b) -> 3D point."""
    out = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            a, b, c, d = fn(xs[i], ys[j]), fn(xs[i + 1], ys[j]), fn(xs[i + 1], ys[j + 1]), fn(xs[i], ys[j + 1])
            out.append(Face([a, b, c], jitter(rgb, seed + i * 31 + j * 7, amt), normal, cull=False, layer=layer))
            out.append(Face([a, c, d], jitter(rgb, seed + i * 31 + j * 7 + 3, amt), normal, cull=False, layer=layer))
    return out


STATIC_ENV = (tri_grid(np.linspace(-5, 5, 9), np.linspace(-2.2, 3.5, 6), lambda a, b: (a, 0.0, b), COUNTER, (0, 1, 0), 11)
              + tri_grid(np.linspace(-6, 6, 9), np.linspace(0, 4.5, 5), lambda a, b: (a, b, -2.2), WALL, (0, 0, 1), 57))


# ---------------------------------------------------------------- the scene at time t
def build(t):
    faces = list(STATIC_ENV)
    door_ang = -math.radians(112) * in_out(prog(t, 3.0, 4.6))
    lift = in_out(prog(t, 3.6, 5.0))
    top_a = 1 - smooth(prog(t, 4.3, 5.0))

    # shell (outward faces; back faces culled)
    # Layers: interior 1.5-2 < wave sheet 2.1 < outer shell 2.2 < panel details 2.3 < door 2.4 < roof 2.5.
    # Anything inside the box that overlaps the shell on screen is behind it, so the shell always wins.
    faces += [f for f in box(-1, 1, 0, 1.2, -0.7, 0.7, BODY, 3, layer=2.2) if f.normal[1] == 0 and f.normal[2] != 1]
    faces += box(CX1, 1, 0, 1.2, 0.64, 0.7, BODY, 9, layer=2.2)                   # control block front
    faces += [Face([(-1, 0, 0.7), (CX0, 0, 0.7), (CX0, 1.2, 0.7), (-1, 1.2, 0.7)], BODY, (0, 0, 1), layer=2.2),
              Face([(CX0, 0, 0.7), (CX1, 0, 0.7), (CX1, CY0, 0.7), (CX0, CY0, 0.7)], BODY, (0, 0, 1), layer=2.2)]
    # control panel: display + buttons
    faces += [Face([(0.52, 0.86, 0.71), (0.88, 0.86, 0.71), (0.88, 1.02, 0.71), (0.52, 1.02, 0.71)], hexc("1E3B3A"), (0, 0, 1), emit=0.3, layer=2.3)]
    for k in range(3):
        y = 0.68 - k * 0.17
        faces += box(0.58, 0.82, y - 0.05, y + 0.05, 0.7, 0.74, TRIM, 40 + k, layer=2.3)
    if lift > 0.01:  # rims revealed once the roof is off
        faces += [Face([(-1, 1.2, -0.7), (CX0, 1.2, -0.7), (CX0, 1.2, 0.7), (-1, 1.2, 0.7)], BODY, (0, 1, 0), layer=2.2),
                  Face([(CX0, 1.2, -0.7), (CX1, 1.2, -0.7), (CX1, 1.2, CZ0), (CX0, 1.2, CZ0)], BODY, (0, 1, 0), layer=2.2),
                  Face([(CX1, 1.2, -0.7), (1, 1.2, -0.7), (1, 1.2, 0.7), (CX1, 1.2, 0.7)], BODY, (0, 1, 0), layer=2.2)]
    roof = [Face([(-1, 1.2, -0.7), (1, 1.2, -0.7), (1, 1.2, 0.7), (-1, 1.2, 0.7)], BODY, (0, 1, 0), alpha=top_a, layer=2.5),
            Face([(CX0, CY1, CZ0), (CX1, CY1, CZ0), (CX1, CY1, CZ1), (CX0, CY1, CZ1)], CAVITY, (0, -1, 0), alpha=top_a, layer=1.5, emit=0.6)]
    if top_a > 0.01:
        faces += shift(roof, (0, 1.9 * lift ** 1.5, 0))

    # cavity interior (inward faces, lit by the oven lamp)
    faces += [Face([(CX0, CY0, CZ0), (CX1, CY0, CZ0), (CX1, CY0, CZ1), (CX0, CY0, CZ1)], CAVITY, (0, 1, 0), layer=1.5, emit=0.6),
              Face([(CX0, CY0, CZ0), (CX1, CY0, CZ0), (CX1, CY1, CZ0), (CX0, CY1, CZ0)], CAVITY, (0, 0, 1), layer=1.5, emit=0.6),
              Face([(CX0, CY0, CZ0), (CX0, CY1, CZ0), (CX0, CY1, CZ1), (CX0, CY0, CZ1)], CAVITY, (1, 0, 0), layer=1.5, emit=0.6),
              Face([(CX1, CY0, CZ0), (CX1, CY1, CZ0), (CX1, CY1, CZ1), (CX1, CY0, CZ1)], CAVITY, (-1, 0, 0), layer=1.5, emit=0.6)]

    # door: frame + glass, hinged on the left edge
    hx, hz = -1.0, 0.7
    door = (box(-1, -0.86, 0, 1.2, 0.7, 0.78, BODY, 70, layer=2.4) + box(0.26, 0.42, 0, 1.2, 0.7, 0.78, BODY, 71, layer=2.4)
            + box(-0.86, 0.26, 0, 0.16, 0.7, 0.78, BODY, 72, layer=2.4) + box(-0.86, 0.26, 1.04, 1.2, 0.7, 0.78, BODY, 73, layer=2.4)
            + box(0.3, 0.36, 0.3, 0.9, 0.78, 0.86, TRIM, 74, layer=2.4))
    door += [Face([(-0.86, 0.16, 0.74), (0.26, 0.16, 0.74), (0.26, 1.04, 0.74), (-0.86, 1.04, 0.74)], GLASS, (0, 0, 1),
                  alpha=0.55, cull=False, layer=2.4)]
    faces += rot_y(door, (hx, 0, hz), door_ang)

    # floor heat map: tiles rise into bars, then settle flat
    rise = out_cubic(prog(t, 5.3, 6.8)) * (1 - in_out(prog(t, 9.1, 10.0)))
    show = prog(t, 5.1, 5.6)
    if show > 0:
        nx, nz = 10, 8
        for i in range(nx):
            for j in range(nz):
                x0 = CX0 + (CX1 - CX0) * i / nx
                x1 = CX0 + (CX1 - CX0) * (i + 1) / nx
                z0 = CZ0 + (CZ1 - 0.06 - CZ0) * j / nz
                z1 = CZ0 + (CZ1 - 0.06 - CZ0) * (j + 1) / nz
                h = heat_at((x0 + x1) / 2, (z0 + z1) / 2)
                stag = clamp(rise * 1.6 - (i + j) * 0.04)
                top = CY0 + 0.012 + 0.42 * h * stag
                rgb = mix(CAVITY, heat_col(h), show)
                faces += box(x0 + 0.004, x1 - 0.004, CY0, top, z0 + 0.004, z1 - 0.004, rgb, i * 9 + j, emit=0.25 * h)

    # turntable + mug (gone while the heat map is up)
    tt_a = 1 - smooth(prog(t, 4.9, 5.4)) + smooth(prog(t, 9.8, 10.4))
    if tt_a > 0.02:
        spin = t * 0.9
        px, pz = PLATE_C
        faces += cylinder(px, pz, 0.48, CY0 + 0.02, CY0 + 0.05, 14, PLATE, spin, 5, alpha=0.85 * min(1, tt_a))
        mx, mz = px + 0.26 * math.cos(spin), pz + 0.26 * math.sin(spin)
        h = heat_at(mx, mz) * smooth(prog(t, 10.0, 10.6))
        faces += cylinder(mx, mz, 0.13, CY0 + 0.05, CY0 + 0.33, 10, mix(MUG, HOT, h), spin * 1.0, 8, alpha=min(1, tt_a), emit=0.5 * h)
        faces += box(mx + 0.12, mx + 0.2, CY0 + 0.12, CY0 + 0.26, mz - 0.02, mz + 0.02, MUG, 81, alpha=min(1, tt_a))

    # standing-wave sheet across the cavity
    wa = smooth(prog(t, 5.8, 6.4)) * (1 - smooth(prog(t, 8.8, 9.4)))
    if wa > 0:
        n = 36
        for i in range(n):
            u0, u1 = i / n, (i + 1) / n
            y0 = 0.68 + 0.26 * math.sin(3 * math.pi * u0) * math.cos(t * 5.5)
            y1 = 0.68 + 0.26 * math.sin(3 * math.pi * u1) * math.cos(t * 5.5)
            x0, x1 = lerp(CX0, CX1, u0), lerp(CX0, CX1, u1)
            amp = abs(math.sin(3 * math.pi * (u0 + u1) / 2))
            faces.append(Face([(x0, y0, -0.32), (x1, y1, -0.32), (x1, y1, 0.32), (x0, y0, 0.32)], mix(COLD, (230, 245, 255), amp),
                              (0, 1, 0), alpha=0.78 * wa, cull=False, layer=2.1, emit=0.6))
    return faces


def shade(f, cam):
    n = f.normal / (np.linalg.norm(f.normal) or 1)
    to_cam = cam.eye - f.pts[0]
    if f.cull and n @ to_cam <= 0:
        return None
    if not f.cull and n @ to_cam < 0:
        n = -n
    k = 0.48 + 0.6 * max(0.0, n @ LIGHT)
    k = lerp(k, 1.05, f.emit)
    rgb = tuple(min(255, ch * k) for ch in f.rgb)
    if f.emit > 0:
        rgb = mix(rgb, (255, 236, 200), 0.12 * f.emit)
    return rgb


def draw(c, t):
    # sky gradient
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)],
                                                        [skia.Color(*SKY_TOP), skia.Color(*SKY_BOT)]))
    c.drawPaint(p)
    cam = Cam(t)
    faces = build(t)
    items = []
    for f in faces:
        rgb = shade(f, cam)
        if rgb is None:
            continue
        proj = [cam.project(q) for q in f.pts]
        if min(z for _, _, z in proj) < 0.05:
            continue
        depth = sum(z for _, _, z in proj) / len(proj)
        items.append((f.layer, -depth, proj, rgb, f.alpha))
    items.sort(key=lambda it: (it[0], it[1]))
    shadow_done = False
    for layer, _, proj, rgb, alpha in items:
        if layer > 0 and not shadow_done:
            draw_shadow(c, cam)
            shadow_done = True
        path = skia.Path()
        path.moveTo(proj[0][0], proj[0][1])
        for x, y, _ in proj[1:]:
            path.lineTo(x, y)
        path.close()
        c.drawPath(path, fill(rgb, 255 * alpha))
        if alpha >= 0.99:
            c.drawPath(path, stroke(rgb, 1.0))

    # oven lamp glow through the window / opening
    g = cam.project((PLATE_C[0], 0.6, 0.3))
    c.drawCircle(g[0], g[1], 260, blur(fill(hexc("FFD9A0"), 26 * (1 - prog(t, 5.0, 6.0) * 0.6)), 90))

    labels(c, t, cam)
    captions(c, t)
    # fade in from black
    if t < 0.6:
        c.drawRect(skia.Rect.MakeWH(W, H), fill((0, 0, 0), 255 * (1 - smooth(prog(t, 0, 0.6)))))


def draw_shadow(c, cam):
    pts = [cam.project((1.25 * math.cos(a), 0.002, 0.95 * math.sin(a))) for a in np.linspace(0, 2 * math.pi, 28)]
    path = skia.Path()
    path.moveTo(pts[0][0], pts[0][1])
    for x, y, _ in pts[1:]:
        path.lineTo(x, y)
    path.close()
    c.drawPath(path, blur(fill((20, 12, 10), 110), 28))


def chip(c, s, x, y, size, rgb_bg, rgb_fg, a):
    if a <= 0:
        return
    w = measure(s, "bold", size) + size * 1.1
    h = size * 1.6
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), h / 2, h / 2), fill(rgb_bg, 235 * a))
    text(c, s, x, y + size * 0.36, "bold", size, rgb_fg, 255 * a)


def labels(c, t, cam):
    a = smooth(prog(t, 7.0, 7.4)) * (1 - smooth(prog(t, 9.0, 9.4)))
    if a <= 0:
        return
    u = lambda f: lerp(CX0, CX1, f)
    v = lambda f: lerp(CZ0, CZ1 - 0.06, f)
    for i, (x, z, s, bg) in enumerate([(u(0.5), v(0.25), "HOT", HOT), (u(0.17), v(0.75), "HOT", HOT), (u(0.33), v(0.5), "COLD", COLD)]):
        top = CY0 + 0.42 * heat_at(x, z) + 0.05
        bx, by, _ = cam.project((x, top, z))
        k = out_back(prog(t, 7.0 + i * 0.15, 7.35 + i * 0.15))
        c.drawLine(bx, by, bx, by - 70 * k, stroke(INK, 3, 230 * a))
        chip(c, s, bx, by - 70 * k - 24, 30, bg, INK, a * k)


CAPTIONS = [
    (0.4, 3.2, "Why do microwaves heat unevenly?", 54),
    (5.6, 8.9, "Waves bounce between the metal walls and stack up.", 40),
    (9.0, 10.5, "Some spots get blasted. Others barely warm.", 40),
    (10.6, 12.2, "So the turntable drags your food through them.", 40),
]


def captions(c, t):
    for t0, t1, s, size in CAPTIONS:
        a = smooth(prog(t, t0, t0 + 0.35)) * (1 - smooth(prog(t, t1 - 0.3, t1)))
        if a <= 0:
            continue
        dy = 18 * (1 - out_cubic(prog(t, t0, t0 + 0.4)))
        w = measure(s, "bold", size) + 64
        x0, y0 = 90, H - 110 - size * 1.6 + dy
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, w, size * 1.7), 18, 18), fill((14, 16, 30), 170 * a))
        text(c, s, x0 + 32, y0 + size * 1.17, "bold", size, INK, 255 * a, align="left")


# ---------------------------------------------------------------- post: soft vignette
_VIG = None


def post(img, t):
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _VIG = (1 - 0.32 * np.clip(r - 0.45, 0, 1) ** 1.6)[..., None].astype(np.float32)
    return (img.astype(np.float32) * _VIG).astype(np.uint8)
