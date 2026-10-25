"""Style test C2: the microwave in a real kitchen. Fast, cut-to-the-voice camera (Zack D. Films-style shorts),
3D lighting with window sun, depth of field, motion blur, thermal-camera wipe, sound design and narration.

Background gags (never the focus, there to be spotted): a cat on the fridge slowly pushing a mug off the edge
(and staring at the camera before the final shove), a toaster that launches toast and catches it again,
a robot vacuum that keeps bumping into the fridge, a rubber duck by the sink.

  python3 kitchen_vo.py                  # narration (once)
  python3 kitchen.py                     # -> out/kitchen_wide.mp4 (16:9)
  python3 kitchen.py --tall              # -> out/kitchen_tall.mp4 (9:16)
  python3 kitchen.py --still 3,8.5,12    # quick frames -> build/kitchen/
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool

import numpy as np
import skia

import gl3d as G
from gl3d import Geo, Rx, Ry, Rz, S, T, box, cylinder, hexc, quad, sphere, srgb, torus

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
VO_START = {"01": 0.3, "02": 5.9, "03": 9.8, "04": 15.0}
DURATION = 22.0


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t1)


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def out_expo(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def out_back(x, s=1.4):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def in_out_expo(x):
    x = clamp(x)
    if x in (0.0, 1.0):
        return x
    return 2 ** (20 * x - 10) / 2 if x < 0.5 else (2 - 2 ** (-20 * x + 10)) / 2


def lerp(a, b, t):
    return a + (b - a) * t


def v3(*a):
    return np.array(a, np.float64)


# ---------------------------------------------------------------- palette (sRGB)
WALL = hexc("ECE4D6")
TILE = hexc("F4F1EA")
GROUT = hexc("BDB4A6")
WOOD = hexc("B47A48")
FLOOR = hexc("8C5E3C")
CAB = hexc("3E5A6B")
CAB_DK = hexc("2E4452")
BRASS = hexc("C9A15A")
BODY = hexc("8FD3C1")
TRIM = hexc("2D3142")
CAVITY = hexc("F2E2BF")
STEEL = hexc("C8CCD0")
FRIDGE = hexc("E6E6E2")
RED = hexc("D9483B")
CAT = hexc("E5893B")
CAT_DK = hexc("B8652A")
CREAM = hexc("F6E3C6")
MUG_BLUE = hexc("3F7FD1")
COLD = hexc("3D7BFF")
WARM = hexc("FFC145")
HOT = hexc("FF4D3D")

# microwave cavity (world units, about 4 units per metre; microwave x -1..1, y 0..1.2, z -0.7..0.7)
CX0, CX1, CY0, CY1, CZ0, CZ1 = -0.94, 0.40, 0.06, 1.14, -0.64, 0.70
PLATE_C = ((CX0 + CX1) / 2, 0.0)


def heat_at(x, z):
    u = (np.asarray(x) - CX0) / (CX1 - CX0)
    v = (np.asarray(z) - CZ0) / (CZ1 - CZ0)
    return np.clip(0.04 + (np.sin(3 * np.pi * u) ** 2 * np.sin(2 * np.pi * v) ** 2) ** 1.3, 0, 1)


# thermal-camera ramp (same stops as the shader's thermal view), so blue never mixes into lavender
RAMP = [srgb(hexc(c)) for c in ("0A1E8C", "2E6BFF", "C02CB4", "FF4B1F", "FFD84A")]


def heat_rgb(h):
    x = clamp(float(h)) * (len(RAMP) - 1)
    i = min(int(x), len(RAMP) - 2)
    return RAMP[i] + (RAMP[i + 1] - RAMP[i]) * (x - i)


# ---------------------------------------------------------------- the static kitchen
def kitchen_static():
    g = []
    # floor planks
    for i in range(16):
        z0 = -1.25 + i * 1.0
        for j in range(5):
            x0 = -11.5 + j * 5.5 + (i % 3) * 1.8 - 1.8
            g.append(box(max(-11.5, x0), min(13, x0 + 5.5), -3.62, -3.6, z0, z0 + 0.98, FLOOR, 0.10, i * 7 + j, S=0.15))
    # walls (back wall with a window hole, thickness gives the window a reveal)
    wz0, wz1 = -1.55, -1.25
    g += [box(-11.5, 13, -3.6, 1.3, wz0, wz1, WALL, 0.0), box(-11.5, 13, 4.6, 7.2, wz0, wz1, WALL, 0.0),
          box(-11.5, -9.0, 1.3, 4.6, wz0, wz1, WALL, 0.0), box(-5.0, 13, 1.3, 4.6, wz0, wz1, WALL, 0.0),
          box(-11.8, -11.5, -3.6, 7.2, -1.55, 16, WALL, 0.0, 3), box(13, 13.3, -3.6, 7.2, -1.55, 16, WALL, 0.0, 4),
          box(-11.8, 13.3, 7.2, 7.4, -1.55, 16, hexc("F3EFE7"), 0.0)]
    # window frame + mullions + sill
    fr = hexc("FAFAF7")
    g += [box(-9.1, -4.9, 1.2, 1.32, -1.6, -0.95, fr, 0.0), box(-9.1, -4.9, 4.58, 4.7, -1.6, -1.2, fr, 0.0),
          box(-9.1, -8.98, 1.3, 4.6, -1.6, -1.2, fr, 0.0), box(-5.02, -4.9, 1.3, 4.6, -1.6, -1.2, fr, 0.0),
          box(-7.06, -6.94, 1.3, 4.6, -1.45, -1.35, fr, 0.0), box(-9.0, -5.0, 2.9, 3.0, -1.45, -1.35, fr, 0.0)]
    # backsplash tiles (subway, offset rows)
    for r in range(9):
        y0 = 0.0 + r * 0.25
        off = 0.25 if r % 2 else 0.0
        x = -11.5 - off
        k = 0
        while x < 6.6:
            x0, x1 = max(x, -11.5), min(x + 0.5, 6.6)
            if not (-9.05 < (x0 + x1) / 2 < -4.95 and y0 > 1.15):
                g.append(box(x0 + 0.012, x1 - 0.012, y0 + 0.012, y0 + 0.238, -1.25, -1.22, TILE, 0.04, r * 100 + k, S=0.5))
            x += 0.5
            k += 1
    g.append(box(-11.5, 6.6, 0.0, 2.25, -1.25, -1.244, GROUT, 0.0))   # just in front of the wall (no z-fighting)
    # lower cabinets + counter (with a sink hole)
    g += [box(-11.5, 6.4, -3.25, -0.16, -1.25, 1.22, CAB_DK, 0.0), box(-11.5, 6.4, -3.6, -3.25, -1.25, 0.95, hexc("1F2A33"), 0.0)]
    for i, x0 in enumerate(np.arange(-11.4, 6.3, 1.95)):
        x1 = min(x0 + 1.88, 6.35)
        g.append(box(x0, x1, -3.15, -0.3, 1.22, 1.3, CAB, 0.02, 200 + i))
        g.append(box(x0 + 0.15, x0 + 0.21, -1.4, -0.75, 1.3, 1.38, BRASS, 0.0, S=1.2))
    top = dict(S=0.25)
    g += [box(-11.5, -8.6, -0.16, 0.0, -1.25, 1.4, WOOD, 0.03, 300, **top), box(-5.4, 6.4, -0.16, 0.0, -1.25, 1.4, WOOD, 0.03, 301, **top),
          box(-8.6, -5.4, -0.16, 0.0, -1.25, -0.85, WOOD, 0.03, 302, **top), box(-8.6, -5.4, -0.16, 0.0, 0.95, 1.4, WOOD, 0.03, 303, **top)]
    # sink basin (inward faces) + faucet + rubber duck
    sx0, sx1, sz0, sz1, sy = -8.6, -5.4, -0.85, 0.95, -1.0
    g += [quad((sx0, sy, sz0), (sx1, sy, sz0), (sx1, sy, sz1), (sx0, sy, sz1), STEEL, S=1.0),
          quad((sx0, sy, sz0), (sx1, sy, sz0), (sx1, 0, sz0), (sx0, 0, sz0), STEEL, S=1.0),
          quad((sx0, sy, sz1), (sx1, sy, sz1), (sx1, 0, sz1), (sx0, 0, sz1), STEEL, S=1.0),
          quad((sx0, sy, sz0), (sx0, sy, sz1), (sx0, 0, sz1), (sx0, 0, sz0), STEEL, S=1.0),
          quad((sx1, sy, sz0), (sx1, sy, sz1), (sx1, 0, sz1), (sx1, 0, sz0), STEEL, S=1.0)]
    g += [cylinder(0.12, 0, 1.6, 16, STEEL, S=1.4).xf(T(-7.0, 0, -1.05)),
          torus(0.45, 0.07, 16, 8, math.pi, STEEL, S=1.4).xf(T(-7.0, 1.6, -0.6) @ Ry(math.pi / 2)),
          cylinder(0.08, -0.2, 0, 12, STEEL, S=1.4).xf(T(-7.0, 1.6, -0.15))]
    duck = [sphere(0.22, 14, 10, hexc("FFD23F")).xf(T(-5.0, 0.2, 1.05) @ S(1.3, 0.9, 1.0)),
            sphere(0.14, 14, 10, hexc("FFD23F")).xf(T(-4.82, 0.48, 1.08)),
            sphere(0.06, 10, 6, hexc("FF8A1F")).xf(T(-4.65, 0.45, 1.1) @ S(1.6, 0.6, 1)),
            sphere(0.03, 8, 6, (15, 15, 15)).xf(T(-4.72, 0.54, 1.2))]
    g += duck
    # windowsill plant
    g.append(cylinder(0.26, 1.32, 1.75, 16, hexc("C4643C"), r_top=0.32).xf(T(-6.2, 0, -1.1)))
    for i in range(7):
        a = i * 2 * math.pi / 7
        g.append(sphere(0.12, 10, 8, hexc("3F8F4A"), jit=0.1, seed=i).xf(
            T(-6.2 + 0.18 * math.cos(a), 1.95 + 0.12 * (i % 3), -1.1 + 0.12 * math.sin(a)) @ Ry(-a) @ Rz(0.6) @ S(3.2, 0.5, 1.1)))
    # floating shelf above the microwave with jars
    g.append(box(-3.0, 2.6, 3.5, 3.62, -1.25, -0.4, WOOD, 0.02, 400, S=0.2))
    for i, (x, h, c) in enumerate([(-2.4, 0.7, hexc("E9C46A")), (-1.6, 0.55, hexc("F4A261")), (-0.9, 0.8, hexc("D7E3E8")),
                                   (0.4, 0.6, hexc("A3B18A")), (1.3, 0.5, hexc("E76F51"))]):
        g.append(cylinder(0.24, 3.62, 3.62 + h, 18, c, S=0.6).xf(T(x, 0, -0.85)))
        g.append(cylinder(0.26, 3.62 + h, 3.62 + h + 0.08, 18, TRIM).xf(T(x, 0, -0.85)))
    # upper cabinets
    for (x0, x1) in ((2.9, 6.4), (-11.5, -9.4)):
        g.append(box(x0, x1, 3.0, 6.4, -1.25, 0.05, CAB_DK, 0.0))
        mid = (x0 + x1) / 2
        g += [box(x0 + 0.05, mid - 0.03, 3.05, 6.35, 0.05, 0.12, CAB, 0.02, 500), box(mid + 0.03, x1 - 0.05, 3.05, 6.35, 0.05, 0.12, CAB, 0.02, 501),
              box(mid - 0.2, mid - 0.14, 3.2, 3.8, 0.12, 0.2, BRASS, 0.0, S=1.2), box(mid + 0.14, mid + 0.2, 3.2, 3.8, 0.12, 0.2, BRASS, 0.0, S=1.2)]
    # kettle, fruit bowl
    kx = -4.4
    g += [cylinder(0.45, 0, 0.95, 24, STEEL, r_top=0.3, S=1.5).xf(T(kx, 0, -0.5)),
          sphere(0.08, 10, 8, TRIM).xf(T(kx, 1.0, -0.5)),
          torus(0.32, 0.05, 16, 8, math.pi, TRIM, S=0.4).xf(T(kx, 0.95, -0.5) @ Ry(math.pi / 2)),
          cylinder(0.07, 0, 0.5, 10, STEEL, r_top=0.05, S=1.5).xf(T(kx - 0.5, 0.35, -0.5) @ Rz(0.9))]
    g += [cylinder(0.32, 0.0, 0.32, 24, hexc("EFEAE0"), r_top=0.62, caps=(True, False), S=0.6).xf(T(-3.4, 0, 0.5))]
    for i, (dx, dz) in enumerate([(-0.18, 0.05), (0.2, -0.05), (0.0, 0.25)]):
        g.append(sphere(0.22, 14, 10, hexc("F08A24"), S=0.3).xf(T(-3.4 + dx, 0.42, 0.5 + dz)))
    # fridge
    fx0, fx1, fz1 = 6.6, 10.6, 1.7
    g += [box(fx0, fx1, -3.6, 5.0, -1.25, fz1 - 0.08, FRIDGE, 0.0, S=0.6),
          box(fx0 + 0.04, fx1 - 0.04, 1.85, 4.96, fz1 - 0.08, fz1, FRIDGE, 0.0, S=0.6),
          box(fx0 + 0.04, fx1 - 0.04, -3.5, 1.75, fz1 - 0.08, fz1, FRIDGE, 0.0, S=0.6),
          box(fx0 + 0.3, fx0 + 0.42, 2.3, 4.1, fz1, fz1 + 0.18, STEEL, 0.0, S=1.4),
          box(fx0 + 0.3, fx0 + 0.42, -1.5, 1.3, fz1, fz1 + 0.18, STEEL, 0.0, S=1.4)]
    for i, (x, y, c) in enumerate([(8.2, 3.6, hexc("E63946")), (9.4, 3.1, hexc("2A9D8F")), (8.9, 4.2, hexc("F4A261")), (9.8, 0.6, hexc("457B9D"))]):
        g.append(box(x, x + 0.5, y, y + 0.62, fz1, fz1 + 0.02, hexc("FFF8E7"), 0.0, i))
        g.append(sphere(0.08, 10, 6, c).xf(T(x + 0.25, y + 0.55, fz1 + 0.05)))
    # pendant lamp
    g += [cylinder(0.02, 5.6, 7.2, 6, TRIM).xf(T(-1.0, 0, 2.2)),
          cylinder(0.9, 4.95, 5.6, 24, hexc("2F5D50"), r_top=0.12, caps=(False, True), S=0.5).xf(T(-1.0, 0, 2.2)),
          sphere(0.22, 12, 8, (255, 230, 190), E=6.0).xf(T(-1.0, 5.05, 2.2))]
    return G.cat(g)


# ---------------------------------------------------------------- dynamic parts
def microwave(t, thermal_on):
    op, tr = [], []
    door = -math.radians(108) * out_back(prog(t, 5.8, 6.25), 1.0)
    lift = out_expo(prog(t, 6.1, 6.6))
    roof_a = 1 - smooth(prog(t, 6.35, 6.7))
    # shell
    op += [box(-1, 1, 0, 1.2, -0.7, -0.64, BODY, 0.0, 1, S=0.35), box(-1, -0.94, 0, 1.2, -0.7, 0.7, BODY, 0.0, 2, S=0.35),
           box(CX1, 1, 0, 1.2, -0.7, 0.7, BODY, 0.0, 3, S=0.35), box(-1, 1, 0, CY0, -0.7, 0.7, BODY, 0.0, 4, S=0.35),
           box(-0.95, -0.8, -0.04, 0.0, -0.6, -0.45, TRIM), box(0.8, 0.95, -0.04, 0.0, -0.6, -0.45, TRIM),
           box(-0.95, -0.8, -0.04, 0.0, 0.45, 0.6, TRIM), box(0.8, 0.95, -0.04, 0.0, 0.45, 0.6, TRIM)]
    op.append(box(0.52, 0.88, 0.86, 1.02, 0.7, 0.71, hexc("1E3B3A"), 0.0, E=0.15))
    op.append(box(0.56, 0.84, 0.9, 0.98, 0.705, 0.712, hexc("7CFFB2"), 0.0, E=2.5 if t < 5.8 else 0.6))
    for k in range(3):
        y = 0.68 - k * 0.17
        op.append(box(0.58, 0.82, y - 0.05, y + 0.05, 0.7, 0.74, TRIM, 0.0, 10 + k))
    if roof_a > 0.01:
        roof = box(-1, 1, 1.14, 1.2, -0.7, 0.7, BODY, 0.0, 5, S=0.35).xf(T(0, 2.2 * lift, 0) @ T(0, 0.6, 0) @ Rx(-0.5 * lift) @ T(0, -0.6, 0))
        (op if roof_a > 0.99 else tr).append(roof.set(A=roof_a))
    if lift > 0.01:
        op.append(box(-1, 1, 1.14, 1.2, -0.7, -0.64, BODY, 0.0).set(S=0.35))
    # cavity (inward quads, lamp-lit)
    cav = dict(S=0.1)
    op += [quad((CX0, CY0, CZ0), (CX1, CY0, CZ0), (CX1, CY0, CZ1), (CX0, CY0, CZ1), CAVITY, **cav),
           quad((CX0, CY0, CZ0), (CX1, CY0, CZ0), (CX1, CY1, CZ0), (CX0, CY1, CZ0), CAVITY, **cav),
           quad((CX0, CY0, CZ0), (CX0, CY1, CZ0), (CX0, CY1, CZ1), (CX0, CY0, CZ1), CAVITY, **cav),
           quad((CX1, CY0, CZ0), (CX1, CY1, CZ0), (CX1, CY1, CZ1), (CX1, CY0, CZ1), CAVITY, **cav)]
    if lift <= 0.01:
        op.append(quad((CX0, CY1, CZ0), (CX1, CY1, CZ0), (CX1, CY1, CZ1), (CX0, CY1, CZ1), CAVITY, **cav))
    # door (hinged on the left), glass
    hinge = T(-1.0, 0, 0.7) @ Ry(door) @ T(1.0, 0, -0.7)
    door_parts = [] if 9.7 <= t < 14.9 else [
        box(-1, -0.86, 0, 1.2, 0.7, 0.78, BODY, 0.0, 20), box(0.26, 0.42, 0, 1.2, 0.7, 0.78, BODY, 0.0, 21),
        box(-0.86, 0.26, 0, 0.16, 0.7, 0.78, BODY, 0.0, 22), box(-0.86, 0.26, 1.04, 1.2, 0.7, 0.78, BODY, 0.0, 23),
        box(0.3, 0.36, 0.3, 0.9, 0.78, 0.86, TRIM)]
    for b in door_parts:
        op.append(b.set(S=0.35).xf(hinge))
    if door_parts:
        tr.append(quad((-0.86, 0.16, 0.745), (0.26, 0.16, 0.745), (0.26, 1.04, 0.745), (-0.86, 1.04, 0.745), (18, 20, 30), S=2.0, A=0.55).xf(hinge))

    # heat-map tiles: rise, then settle flat
    rise = out_expo(prog(t, 9.9, 10.7)) * (1 - in_out(prog(t, 14.9, 15.5)))
    show = prog(t, 9.8, 10.1)
    if show > 0:
        nx, nz = 10, 8
        for i in range(nx):
            for j in range(nz):
                x0, x1 = CX0 + (CX1 - CX0) * i / nx, CX0 + (CX1 - CX0) * (i + 1) / nx
                z0, z1 = CZ0 + (CZ1 - 0.06 - CZ0) * j / nz, CZ0 + (CZ1 - 0.06 - CZ0) * (j + 1) / nz
                h = float(heat_at((x0 + x1) / 2, (z0 + z1) / 2))
                stag = clamp(rise * 1.5 - (i + j) * 0.03)
                top = CY0 + 0.012 + 0.45 * h * stag
                col = srgb(CAVITY) * (1 - show) + heat_rgb(h) * show
                b = box(x0 + 0.005, x1 - 0.005, CY0, top, z0 + 0.005, z1 - 0.005, (1, 1, 1), 0.0)
                b.C[:] = col
                b.C[:] = col * (0.12 * show + (1 - show))
                b.E[:] = (6.0 + 9.0 * h * h) * show
                op.append(b)

    # turntable + bowl of food
    tt = 1 - smooth(prog(t, 9.6, 9.9)) + smooth(prog(t, 15.2, 15.6))
    if tt > 0.02:
        spin = t * 1.1
        px, pz = PLATE_C
        op.append(cylinder(0.5, CY0 + 0.015, CY0 + 0.045, 32, hexc("E3ECF2"), S=1.5).xf(T(px, 0, pz)))
        bx, bz = px + 0.2 * math.cos(spin), pz + 0.2 * math.sin(spin)
        bowl = cylinder(0.24, CY0 + 0.045, CY0 + 0.33, 28, hexc("F4F1EA"), r_top=0.36, caps=(True, False), S=0.8).xf(T(bx, 0, bz))
        food = food_disc(bx, bz, CY0 + 0.29, 0.33, spin)
        warm = smooth(prog(t, 15.6, 16.2))
        hcur = float(heat_at(bx, bz)) * warm
        food.E[:] = 0.05 + 1.2 * hcur ** 2
        for gg in (bowl, food):
            gg.M[:] = 1.0
        op += [bowl, food]
        # steam once it is hot
        sa = smooth(prog(t, 16.0, 16.6))
        if sa > 0:
            for k in range(6):
                ph = (t * 0.6 + k / 6) % 1.0
                tr.append(sphere(0.07 + 0.09 * ph, 10, 6, (255, 255, 255), E=0.4).set(A=0.32 * sa * (1 - ph) * min(1, ph * 5))
                          .xf(T(bx + 0.06 * math.sin(k * 2.1 + t * 2), CY0 + 0.4 + ph * 0.75, bz + 0.05 * math.cos(k * 1.3 + t))))

    # the wave sheet: travelling in (6.6), echo (7.6), standing (8.8+)
    wa = smooth(prog(t, 6.5, 6.9)) * (1 - smooth(prog(t, 10.4, 10.9)))
    if wa > 0:
        n = 60
        L = CX1 - CX0
        k = 3 * math.pi / L
        w = 2 * math.pi * 1.6
        front = CX0 + L * smooth(prog(t, 6.6, 7.5))
        back = CX1 - L * smooth(prog(t, 7.5, 8.4))
        P, C = [], []
        for i in range(n):
            xa, xb = CX0 + L * i / n, CX0 + L * (i + 1) / n

            def y(x):
                s = 0.0
                if x <= front:
                    s += math.sin(k * (x - CX0) - w * t)
                if x >= back and t > 7.5:
                    s += math.sin(k * (x - CX0) + w * t)
                return 0.62 + 0.13 * s
            ya, yb = y(xa), y(xb)
            if xa > front and t < 7.5:
                continue
            P.append([[xa, ya, -0.38], [xb, yb, -0.38], [xb, yb, 0.38]])
            P.append([[xa, ya, -0.38], [xb, yb, 0.38], [xa, ya, 0.38]])
            amp = abs(math.sin(k * ((xa + xb) / 2 - CX0)))
            c = srgb(hexc("3DB8FF")) * (1 - amp * 0.5) + srgb((235, 248, 255)) * amp * 0.5
            C += [c, c]
        if P:
            P = np.array(P, np.float32)
            tr.append(Geo(P, G.flat_normals(P), np.array(C), E=1.6, A=0.55 * wa))
    return op, tr


def food_disc(cx, cz, y, r, spin, rings=6, segs=28):
    tris = []
    for i in range(rings):
        r0, r1 = r * i / rings, r * (i + 1) / rings
        for j in range(segs):
            a0, a1 = 2 * math.pi * j / segs, 2 * math.pi * (j + 1) / segs
            def p(rr, a):
                bump = 0.03 * math.sin(3 * a + rr * 20 + spin) * (1 - rr / r) + 0.05 * (1 - (rr / r) ** 2)
                return [cx + rr * math.cos(a), y + bump, cz + rr * math.sin(a)]
            if i == 0:
                tris.append([p(0, 0), p(r1, a1), p(r1, a0)])
            else:
                tris += [[p(r0, a0), p(r1, a1), p(r1, a0)], [p(r0, a0), p(r0, a1), p(r1, a1)]]
    P = np.array(tris, np.float32)
    g = Geo(P, G.flat_normals(P), G.jitter_cols(len(P), hexc("C8692F"), 0.12, 7), S=0.5)
    # thermal view: patchy, the real standing-wave pattern + lumps
    g.heat_from(lambda x, yy, z: np.clip(heat_at(x, z) * 0.85 + 0.12 * np.sin(x * 9 + z * 7) ** 2, 0, 1))
    return g


def toaster(t):
    return [x.xf(T(-0.6, 0, 0)) for x in _toaster(t)]


def _toaster(t):
    g = [box(2.95, 4.05, 0.0, 0.85, -0.72, 0.02, RED, 0.0, 30, S=0.7),
         box(2.95, 4.05, 0.0, 0.08, -0.74, 0.04, STEEL, 0.0, S=1.4),
         box(3.1, 3.9, 0.851, 0.855, -0.6, -0.48, (20, 20, 20)), box(3.1, 3.9, 0.851, 0.855, -0.24, -0.12, (20, 20, 20)),
         box(4.05, 4.15, 0.45 if 11.0 < t < 12.1 else 0.3, 0.55 if 11.0 < t < 12.1 else 0.4, -0.42, -0.3, TRIM)]
    tp = 11.0
    for k, zc in enumerate((-0.54, -0.18)):
        u = t - tp - k * 0.04
        if 0 < u < 1.1:
            h = 10.5 * u - 9.55 * u * u                      # up ~2.9 units and back in 1.1 s
            spin = 2 * math.pi * (u / 1.1) * (1 if k else -1)
        else:
            h, spin = 0.0, 0.0
        yc = 0.72 + h
        s = box(-0.32, 0.32, -0.3, 0.3, -0.045, 0.045, hexc("D9A35E"), 0.0, 40 + k, S=0.1)
        crust = box(-0.34, 0.34, 0.24, 0.33, -0.05, 0.05, hexc("8A5A2B"), 0.0)
        g += [x.xf(T(3.5, yc, zc) @ Rx(spin)) for x in (s, crust)]
    return g


CAT_BASE = v3(4.85, 0.0, -0.45)
CAT_SCALE = 0.82
MUG_X = 5.4
SHOVE = 19.7
MUG_DROP = math.sqrt(2 * 3.6 / 30.0)          # counter to floor


def cat_and_mug(t, cam_eye):
    """Cat on the counter. Nudges the mug towards the edge at 10.4 and 12.3, glances at the camera,
    then the long stare, then shoves it off at SHOVE."""
    base = CAT_BASE
    g = []
    mug_z = 0.0
    for t0, b in ((10.4, 0.4), (12.3, 0.75)):
        if t > t0:
            mug_z = lerp(mug_z, b, out_expo(prog(t, t0 + 0.18, t0 + 0.35)))
    fall_t = None
    if t > SHOVE + 0.15:
        mug_z = lerp(0.75, 1.62, out_expo(prog(t, SHOVE + 0.15, SHOVE + 0.3)))
        if t > SHOVE + 0.3:
            fall_t = t - (SHOVE + 0.3)
    reach = 0.0
    for t0 in (10.4, 12.3, SHOVE):
        k = prog(t, t0, t0 + 0.45)
        if 0 < k < 1:
            reach = max(reach, math.sin(math.pi * k))
    head_c = base + v3(0, 1.45, 0.15) * CAT_SCALE
    look_cam = max(smooth(prog(t, 13.2, 13.4)) * (1 - smooth(prog(t, 13.9, 14.1))),
                   smooth(prog(t, 19.0, 19.15)) * (1 - smooth(prog(t, 19.62, 19.72))),
                   smooth(prog(t, 21.0, 21.2)))
    tgt = v3(MUG_X, 0.3, mug_z)
    if fall_t is not None:
        tgt = v3(MUG_X + 0.3, -3.6, 2.2)
    tgt = tgt * (1 - look_cam) + np.asarray(cam_eye) * look_cam
    d = tgt - head_c
    yaw = math.atan2(d[0], d[2])
    pitch = -math.atan2(d[1], math.hypot(d[0], d[2]))
    H = T(*head_c) @ Ry(yaw) @ Rx(clamp(pitch, -0.7, 0.5)) @ S(CAT_SCALE)
    B = T(*base) @ S(CAT_SCALE)
    breathe = 1 + 0.02 * math.sin(t * 2.4)
    g += [sphere(0.5, 18, 12, CAT, S=0.1).xf(B @ T(0, 0.62, -0.05) @ S(1.0, 1.25 * breathe, 1.05)),
          sphere(0.3, 14, 10, CREAM).xf(B @ T(0, 0.82, 0.32) @ S(1, 1.25, 0.6)),
          sphere(0.38, 18, 12, CAT, S=0.1).xf(H),
          sphere(0.17, 12, 8, CREAM).xf(H @ T(0, -0.1, 0.26) @ S(1.3, 0.8, 0.8)),
          sphere(0.045, 8, 6, hexc("E07A8A")).xf(H @ T(0, -0.02, 0.37))]
    blink = 0.12 if (t % 3.7) < 0.12 else 1.0
    for sx in (-1, 1):
        g.append(cylinder(0.16, 0, 0.32, 4, CAT, r_top=0.0, smooth=False).xf(H @ T(0.2 * sx, 0.24, 0) @ Rz(-0.35 * sx)))
        g.append(sphere(0.07, 10, 8, (18, 18, 18), S=2.0).xf(H @ T(0.14 * sx, 0.06, 0.31) @ S(1, 1.25 * blink, 0.6)))
        if blink > 0.5:
            g.append(sphere(0.022, 6, 4, (255, 255, 255), E=3.0).xf(H @ T(0.14 * sx + 0.025, 0.1, 0.355)))
        for wy in (-0.06, -0.12):
            g.append(box(0, 0.32, -0.006, 0.006, -0.006, 0.006, (245, 245, 245)).xf(
                H @ T(0.12 * sx, wy, 0.3) @ Rz(0.15 * sx * (1 if wy < -0.1 else -1)) @ S(sx, 1, 1)))
    for i in range(3):
        g.append(sphere(0.2, 10, 6, CAT_DK).xf(B @ T(0, 0.75 + i * 0.22, -0.48) @ S(1.6, 0.25, 0.4)))
    g.append(cylinder(0.11, 0, 0.55, 10, CAT).xf(B @ T(-0.2, 0, 0.38)))
    g.append(sphere(0.13, 10, 8, CREAM).xf(B @ T(-0.2, 0.04, 0.45) @ S(1, 0.6, 1.3)))
    shoulder = base + v3(0.25, 0.75, 0.3) * CAT_SCALE
    paw_rest = base + v3(0.2, 0.06, 0.45) * CAT_SCALE
    paw_hit = v3(MUG_X - 0.05, 0.25, mug_z - 0.24)
    paw = paw_rest * (1 - reach) + paw_hit * reach + v3(0, 0.3 * math.sin(math.pi * reach), 0)
    g.append(limb(shoulder, paw, 0.11 * CAT_SCALE, CAT))
    g.append(sphere(0.13 * CAT_SCALE, 10, 8, CREAM).xf(T(*paw) @ S(1.2, 0.6, 1)))
    flick = 1 + 2.5 * reach
    for i in range(16):
        a = i / 15
        p = base + (v3(-0.35 - 0.5 * a, 0.12 + 0.05 * math.sin(a * 3), -0.45 + 0.75 * a ** 1.5) +
                    v3(0, 0.25 * a * a, 0) * math.sin(t * 2.2 * flick + a * 2.5)) * CAT_SCALE
        g.append(sphere((0.11 - 0.035 * a) * CAT_SCALE, 8, 6, CAT_DK if i % 5 == 4 else CAT).xf(T(*p)))
    # the mug: sliding, falling, breaking
    if fall_t is None:
        g += mug(MUG_X, 0.0, mug_z, 0.0)
    elif fall_t < MUG_DROP:
        g += mug(MUG_X + 0.2 * fall_t, -15.0 * fall_t ** 2, 1.62 + 1.2 * fall_t, -7.0 * fall_t, axis="x")
    else:
        u = fall_t - MUG_DROP
        rng = np.random.default_rng(3)
        cx, cz = MUG_X + 0.2 * MUG_DROP, 1.62 + 1.2 * MUG_DROP
        for k in range(10):
            vx, vz, vy = rng.uniform(-3, 3), rng.uniform(-1.0, 3.0), rng.uniform(1.5, 3.5)
            tt = min(u, 2 * vy / 30.0)
            k_slide = min(u, 0.6) * (1 - min(u, 0.6) / 1.4)
            py = -3.6 + max(0.0, vy * tt - 15 * tt * tt) + 0.03
            spin = k * 1.3 + 6 * k_slide
            g.append(box(-0.08, 0.08, -0.03, 0.03, -0.06, 0.06, MUG_BLUE if k % 3 else (245, 245, 245), 0.0, k)
                     .xf(T(cx + vx * k_slide, py, cz + vz * k_slide) @ Ry(spin) @ Rx(k)))
    return g


def limb(a, b, r, rgb):
    a, b = np.asarray(a), np.asarray(b)
    d = b - a
    L = float(np.linalg.norm(d))
    y = d / L
    x = np.cross(y, [0, 0, 1.0])
    if np.linalg.norm(x) < 1e-6:
        x = np.array([1.0, 0, 0])
    x /= np.linalg.norm(x)
    z = np.cross(x, y)
    M = np.eye(4, dtype=np.float32)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, a
    return cylinder(r, 0, L, 10, rgb).xf(M)


def mug(x, y, z, tilt, axis="z"):
    M = T(x, y, z) @ (Rx(-tilt) if axis == "x" else Rz(-tilt))
    return [cylinder(0.2, 0, 0.42, 20, MUG_BLUE, caps=(True, False), S=0.9).xf(M),
            cylinder(0.17, 0.36, 0.37, 20, hexc("4A2C1A")).xf(M),
            torus(0.11, 0.035, 12, 6, 2 * math.pi, MUG_BLUE, S=0.9).xf(M @ T(0.22, 0.22, 0))]


def roomba(t):
    period = 2.6
    u = (t % period) / period
    if u < 0.55:                       # drive into the fridge...
        x, yaw = lerp(3.6, 5.85, u / 0.55), 0.0
    else:                              # ...bonk, reverse, try again
        k = (u - 0.55) / 0.45
        x = 5.85 - 0.6 * smooth(k / 0.4) if k < 0.4 else lerp(5.25, 3.6, smooth((k - 0.4) / 0.6))
        yaw = 0.25 * math.sin(math.pi * k)
    bump = max(0.0, 1 - abs(u - 0.55) / 0.04)
    M = T(x, -3.6, 2.9) @ Ry(yaw) @ Rz(0.06 * bump)
    return [cylinder(0.65, 0.0, 0.2, 28, hexc("2B2D33"), S=0.8).xf(M),
            cylinder(0.5, 0.2, 0.22, 28, hexc("4A4E57"), S=1.0).xf(M),
            cylinder(0.06, 0.22, 0.23, 10, (60, 200, 255), E=4.0).xf(M @ T(0.25, 0, 0))]


# ---------------------------------------------------------------- camera: shots cut to the voice
def ease_fn(name):
    return {"io": in_out, "expo": out_expo, "ioexpo": in_out_expo, "lin": lambda x: clamp(x), "smooth": smooth}[name]


# each shot: (start, end, keys [(t, eye, target, fov)], ease, handheld, focus target, aperture)
SHOTS = [
    (0.0, 2.6, [(0.0, (-9.5, 6.4, 10.5), (-2.0, 1.2, 0.0), 52), (2.6, (-1.2, 1.7, 4.9), (-0.15, 0.62, 0.0), 40)], "ioexpo", 0.03, (0, 0.6, 0.5), 14),
    (2.6, 5.7, [(2.6, (-0.7, 0.95, 2.2), (-0.27, 0.45, 0.0), 34), (5.7, (-0.45, 0.82, 1.55), (-0.27, 0.4, 0.0), 30)], "smooth", 0.012, (-0.27, 0.4, 0.2), 30),
    (5.7, 7.7, [(5.7, (0.8, 1.0, 3.4), (-0.2, 0.6, 0.0), 38), (6.25, (1.1, 1.35, 3.1), (-0.25, 0.6, 0.0), 40),
                (7.7, (1.6, 3.3, 2.4), (-0.3, 0.5, 0.0), 44)], "ioexpo", 0.025, (-0.27, 0.55, 0.0), 18),
    (7.7, 9.7, [(7.7, (-0.9, 0.95, 1.9), (0.1, 0.6, -0.2), 46), (9.7, (0.25, 0.85, 1.75), (-0.6, 0.6, -0.2), 44)], "io", 0.018, (-0.27, 0.62, 0.0), 26),
    (9.7, 14.9, [(9.7, (-2.3, 2.5, 3.7), (1.1, 0.6, -0.3), 40), (11.8, (-2.0, 2.4, 3.4), (1.2, 0.6, -0.3), 38),
                 (12.1, (-1.5, 2.2, 1.9), (-0.45, 0.3, -0.25), 36), (13.4, (-1.4, 2.15, 1.8), (-0.45, 0.3, -0.25), 35),
                 (13.65, (-2.3, 2.5, 3.7), (1.1, 0.6, -0.3), 40), (14.9, (-2.1, 2.4, 3.5), (1.2, 0.6, -0.3), 39)], "ioexpo", 0.02, (-0.3, 0.4, 0.0), 20),
    (14.9, 17.4, [(14.9, (0.9, 0.62, 1.7), (-0.35, 0.35, 0.0), 40), (17.4, (-0.2, 0.55, 1.75), (-0.27, 0.35, 0.0), 36)], "io", 0.015, (-0.27, 0.4, 0.1), 30),
    (17.4, 18.9, [(17.4, (-0.4, 0.8, 2.2), (-0.27, 0.4, 0.0), 36), (18.3, (-6.5, 2.2, 13.5), (1.6, 1.0, 0.0), 50),
                  (18.9, (-6.6, 2.25, 13.6), (1.7, 1.0, 0.0), 49)], "ioexpo", 0.03, (0.5, 0.8, 0.5), 6),
    (18.9, 22.0, [(18.9, (0.6, 2.8, 7.8), (4.2, 0.9, 0.0), 42), (19.35, (3.0, 1.5, 3.6), (5.0, 0.85, 0.1), 30),
                  (19.95, (3.1, 1.45, 3.5), (5.0, 0.8, 0.2), 30), (20.45, (3.3, 0.6, 4.6), (5.8, -2.6, 1.9), 40),
                  (20.95, (3.3, 0.6, 4.6), (5.8, -2.6, 1.9), 40), (21.25, (3.0, 1.5, 3.6), (5.0, 0.85, 0.1), 31),
                  (22.0, (3.05, 1.48, 3.55), (5.0, 0.85, 0.1), 30)], "ioexpo", 0.02, (4.75, 1.3, -0.2), 10),
]


TALL = False


def handheld(t, amp):
    n = lambda f, p: math.sin(t * f + p) * 0.6 + math.sin(t * f * 2.31 + p * 1.7) * 0.3 + math.sin(t * f * 5.13 + p * 0.3) * 0.1  # noqa: E731
    return v3(n(1.3, 0.2), n(1.1, 1.4), n(0.9, 2.7)) * amp, n(0.7, 4.1) * amp * 0.25


def shot_at(t):
    for i, sh in enumerate(SHOTS):
        if t < sh[1] or i == len(SHOTS) - 1:
            return i, sh
    return len(SHOTS) - 1, SHOTS[-1]


def camera(t):
    i, (s0, s1, keys, ease, hh, focus, ap) = shot_at(t)
    e = ease_fn(ease)
    if t <= keys[0][0]:
        k0 = k1 = keys[0]
        u = 0.0
    else:
        j = max(j for j in range(len(keys)) if keys[j][0] <= t)
        k0, k1 = keys[j], keys[min(j + 1, len(keys) - 1)]
        u = e(prog(t, k0[0], k1[0])) if k1 is not k0 else 0.0
    eye = v3(*k0[1]) * (1 - u) + v3(*k1[1]) * u
    tgt = v3(*k0[2]) * (1 - u) + v3(*k1[2]) * u
    fov = lerp(k0[3], k1[3], u)
    off, roll = handheld(t, hh)
    # tiny settle "kick" right after each cut so cuts land with energy
    kick = math.exp(-(t - s0) * 9) * 0.04 if i > 0 else 0.0
    eye = eye + off + v3(0, kick, 0)
    tgt = tgt + off * 0.5
    if TALL:
        hfov = 2 * math.atan(math.tan(math.radians(fov) / 2) * 16 / 9) * 0.7
        fov = math.degrees(2 * math.atan(math.tan(hfov / 2) * 16 / 9))
    return dict(eye=eye, target=tgt, fov=fov, roll=roll, near=0.05, far=80.0), (s0, s1), v3(*focus), ap


# ---------------------------------------------------------------- frame
LIGHTS_BASE = [
    ((-1.0, 4.9, 2.2), 6.0, (2.4, 1.85, 1.2), None, None),         # pendant
    ((2.0, 4.5, 9.0), 13.0, (0.35, 0.38, 0.46), None, None),       # soft fill from the room
]
SUN = dict(dir=(0.35, -0.55, 0.75), col=(3.4, 2.95, 2.3), sky=(0.24, 0.27, 0.33), ground=(0.16, 0.12, 0.09),
           center=(-2.0, 0.0, 2.0), extent=14.0)
SKY = (2.2, 2.45, 2.75)

_R = None
CONTACT = [G.contact_shadow(0, 0, 1.35, 0.95, 0.0, 0.7), G.contact_shadow(2.9, -0.35, 0.8, 0.55, 0.0, 0.6),
           G.contact_shadow(-4.4, -0.5, 0.6, 0.6, 0.0, 0.6), G.contact_shadow(4.75, -0.35, 0.75, 0.7, 0.0, 0.6), G.contact_shadow(-3.4, 0.5, 0.75, 0.75, 0.0, 0.5),
           G.contact_shadow(8.6, 1.9, 2.6, 0.9, -3.6, 0.6), G.contact_shadow(-6.2, -1.1, 0.4, 0.3, 1.31, 0.5)]


def get_renderer(w, h, ss):
    global _R
    if _R is None:
        _R = G.Renderer(w, h, ss)
        _R.set_static(kitchen_static())
    return _R


def scene(t, cam):
    thermal = smooth(prog(t, 3.25, 3.55)) * (1 - smooth(prog(t, 5.55, 5.7)))
    op, tr = microwave(t, thermal)
    op += toaster(t) + cat_and_mug(t, cam["eye"]) + roomba(t)
    tr += CONTACT
    lamp_on = 1.0
    lights = list(LIGHTS_BASE)
    lights.append(((-0.27, 1.02, 0.0), 1.3, (3.0 * lamp_on, 2.4 * lamp_on, 1.5 * lamp_on), (CX0 - 0.02, CY0 - 0.02, CZ0 - 0.02), (CX1 + 0.02, 1.25, 0.9)))
    return G.cat(op), G.cat(tr), lights, thermal


def render_hdr(R, t):
    cam, _, focus, ap = camera(t)
    op, tr, lights, thermal = scene(t, cam)
    wipe = prog(t, 3.25, 3.6)
    R.clear_col = SKY
    img, depth = R.render(cam, SUN, lights, op, tr, thermal=thermal, thermal_x=wipe if t < 5.0 else 1.0)
    return img, depth, cam, focus, ap


def cam_speed(t):
    a, (s0, s1), _, _ = camera(t)
    t2 = t + 1 / FPS
    if t2 >= s1:                       # measure backwards at the end of a shot
        a, _, _, _ = camera(t - 1 / FPS)
        t2 = t
    b, _, _, _ = camera(t2)
    da = a["target"] - a["eye"]
    db = b["target"] - b["eye"]
    ang = math.acos(clamp(float(np.dot(da, db) / np.linalg.norm(da) / np.linalg.norm(db)), -1, 1))
    mv = np.linalg.norm(a["eye"] - b["eye"]) / max(np.linalg.norm(da), 0.3)
    return ang + mv + abs(a["fov"] - b["fov"]) * 0.01


def frame(t, w, h, ss=1.5):
    R = get_renderer(w, h, ss)
    _, (s0, s1), _, _ = camera(t)
    sp = cam_speed(t)
    n = 1 if sp < 0.004 else 3 if sp < 0.02 else 6
    acc = None
    for k in range(n):
        tk = min(t + (k / n) * 0.5 / FPS, s1 - 1e-4)     # 180-degree shutter, never across a cut
        img, depth, cam, focus, ap = render_hdr(R, tk)
        acc = img if acc is None else acc + img
        if k == 0:
            depth0, cam0, focus0, ap0 = depth, cam, focus, ap
    img = acc / n
    img = G.downsample(img, w, h)
    depth = G.downsample(depth0, w, h)
    fd = float(np.linalg.norm(focus0 - cam0["eye"]))
    img = G.depth_of_field(img, depth, fd, ap0 * (w / 1920), max_sigma=7.0 * (w / 1920) + 1)
    img = G.bloom(img, 1.2, 0.3)
    img = G.vignette(G.tonemap(img, 0.85), 0.32)
    out = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    return overlay(out, t, cam0, w, h)


# ---------------------------------------------------------------- overlays: captions, labels, thermal HUD
FONT_DIR = os.path.join(HERE, "..", "fonts")
_TF = {}


def tf(name):
    if name not in _TF:
        _TF[name] = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, name))
    return _TF[name]


def project(cam, p, w, h):
    view = G.look_at(cam["eye"], cam["target"], roll=cam.get("roll", 0.0))
    proj = G.perspective(math.radians(cam["fov"]), w / h, cam["near"], cam["far"])
    q = proj @ view @ np.array([*p, 1.0])
    if q[3] <= 0:
        return None
    return (q[0] / q[3] * 0.5 + 0.5) * w, (1 - (q[1] / q[3] * 0.5 + 0.5)) * h


def word_timings():
    """Words spread over each narration clip by syllable-ish weight (chars), with pauses at punctuation."""
    d = json.load(open(os.path.join(HERE, "build", "kitchen", "vo", "durations.json")))
    from kitchen_vo import LINES
    out = []
    for key, text in LINES:
        words = text.replace("...", "… ").split()
        wts = [len(wd.strip(".,?…")) + 2 + (5 if wd[-1] in ".?…" else 2 if wd[-1] == "," else 0) for wd in words]
        tot = sum(wts)
        t = VO_START[key] + 0.1
        span = d[key] - 0.25
        for wd, wt in zip(words, wts):
            dur = span * wt / tot
            out.append((t, t + dur, wd.strip("…").upper(), key))
            t += dur
    return out


_WORDS = None


def caption_pages():
    """Groups of up to 3 words; a page ends at punctuation."""
    global _WORDS
    if _WORDS is None:
        ws = word_timings()
        pages, cur = [], []
        for w in ws:
            cur.append(w)
            if len(cur) == 3 or w[2][-1] in ".?," or (cur and w is ws[-1]):
                pages.append(cur)
                cur = []
        if cur:
            pages.append(cur)
        _WORDS = pages
    return _WORDS


def overlay(img, t, cam, w, h):
    rgba = np.dstack([img, np.full(img.shape[:2], 255, np.uint8)]).copy()
    surf = skia.Surface(rgba)
    c = surf.getCanvas()
    sc = w / 1920 if w > h else w / 1080
    tall = h > w
    # thermal HUD
    th = smooth(prog(t, 3.3, 3.5)) * (1 - smooth(prog(t, 5.5, 5.7)))
    if th > 0:
        f = skia.Font(tf("InterDisplay-Bold.otf"), 30 * sc)
        blink = 1.0 if int(t * 2.5) % 2 == 0 else 0.35
        c.drawCircle(70 * sc, (h * 0.12 if tall else 74 * sc), 11 * sc, skia.Paint(AntiAlias=True, Color=skia.Color(255, 60, 60, int(255 * th * blink))))
        c.drawString("THERMAL VIEW", 92 * sc, (h * 0.12 if tall else 74 * sc) + 11 * sc, f, skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, int(235 * th))))
        # temperature scale
        x0, y0, bw, bh = w - 70 * sc, (h * 0.3 if tall else 120 * sc), 18 * sc, 300 * sc
        p = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
            [skia.Point(0, y0 + bh), skia.Point(0, y0)],
            [skia.Color(10, 20, 120), skia.Color(30, 90, 255), skia.Color(230, 30, 160), skia.Color(255, 120, 0), skia.Color(255, 255, 160)]))
        p.setAlphaf(th)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, bw, bh), 6 * sc, 6 * sc), p)
        f2 = skia.Font(tf("InterDisplay-Bold.otf"), 22 * sc)
        wp = skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, int(230 * th)))
        c.drawString("HOT", x0 - 52 * sc, y0 + 18 * sc, f2, wp)
        c.drawString("COLD", x0 - 62 * sc, y0 + bh, f2, wp)
    # 3D-anchored labels on the heat map
    la = smooth(prog(t, 11.9, 12.15)) * (1 - smooth(prog(t, 14.6, 14.9)))
    if la > 0:
        u = lambda f: lerp(CX0, CX1, f)  # noqa: E731
        v = lambda f: lerp(CZ0, CZ1 - 0.06, f)  # noqa: E731
        items = [(u(0.5), v(0.25), "HOT", HOT, 12.0), (u(0.17), v(0.75), "HOT", HOT, 12.15), (u(0.33), v(0.5), "COLD", COLD, 13.65)]
        for x, z, s, col, t0 in items:
            top = CY0 + 0.45 * float(heat_at(x, z)) + 0.05
            pp = project(cam, (x, top, z), w, h)
            k = out_back(prog(t, t0, t0 + 0.25))
            if pp is None or k <= 0:
                continue
            bx, by = pp
            f = skia.Font(tf("InterDisplay-Black.otf"), 34 * sc)
            tw = f.measureText(s)
            ph = 54 * sc
            yy = by - 90 * sc * k
            lp = skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, int(220 * la)), StrokeWidth=3 * sc, Style=skia.Paint.kStroke_Style)
            c.drawLine(bx, by, bx, yy, lp)
            c.save()
            c.translate(bx, yy - ph / 2)
            c.scale(k, k)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-tw / 2 - 18 * sc, -ph / 2, tw + 36 * sc, ph), ph / 2, ph / 2),
                        skia.Paint(AntiAlias=True, Color=skia.Color(*col, int(240 * la))))
            c.drawString(s, -tw / 2, 12 * sc, f, skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, int(255 * la))))
            c.restore()
    # captions: 1-3 words, current word in yellow, punchy pop-in
    pages = caption_pages()
    for pi, page in enumerate(pages):
        t0, t1 = page[0][0], page[-1][1] + 0.12
        if pi + 1 < len(pages):
            t1 = min(t1, pages[pi + 1][0][0])
        if not (t0 <= t < t1):
            continue
        size = (92 if tall else 78) * sc
        f = skia.Font(tf("InterDisplay-Black.otf"), size)
        gap = size * 0.28
        widths = [f.measureText(wd[2]) for wd in page]
        total = sum(widths) + gap * (len(page) - 1)
        cy = h * (0.70 if tall else 0.86)
        pop = out_back(prog(t, t0, t0 + 0.12), 2.0)
        c.save()
        c.translate(w / 2, cy - size * 0.35)
        c.scale(lerp(0.8, 1.0, pop), lerp(0.8, 1.0, pop))
        x = -total / 2
        for (ws, we, wd, _), ww in zip(page, widths):
            active = ws <= t < we + 0.05
            outline = skia.Paint(AntiAlias=True, Color=skia.Color(10, 10, 14), Style=skia.Paint.kStroke_Style, StrokeWidth=size * 0.16)
            outline.setStrokeJoin(skia.Paint.kRound_Join)
            shadow = skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, 120))
            shadow.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.08))
            c.drawString(wd, x + size * 0.03, size * 0.35 + size * 0.06, f, shadow)
            c.drawString(wd, x, size * 0.35, f, outline)
            col = skia.Color(255, 214, 10) if active else skia.Color(255, 255, 255)
            c.drawString(wd, x, size * 0.35, f, skia.Paint(AntiAlias=True, Color=col))
            x += ww + gap
        c.restore()
    # quick flash on the hard cuts into the reveal and the wide shot
    for tc in (5.7, 17.4, 18.9):
        a = (1 - prog(t, tc, tc + 0.12)) if t >= tc else 0
        if a > 0:
            c.drawRect(skia.Rect.MakeWH(w, h), skia.Paint(Color=skia.Color(255, 255, 255, int(70 * a))))
    return np.ascontiguousarray(rgba[:, :, :3])


# ---------------------------------------------------------------- sound
def sfx_events():
    ev = [(0.0, "whoosh", 0.7), (2.55, "swish", 0.6), (3.25, "tick_roll", 0.35), (5.62, "swish", 0.7),
          (5.85, "door_clunk", 0.9), (6.1, "pop", 0.8), (6.55, "riser", 0.3), (7.68, "swish", 0.5), (9.65, "swish", 0.55),
          (9.95, "low_hit", 0.5), (11.0, "toast_pop", 0.35), (12.0, "stamp", 0.5), (13.6, "swish", 0.4),
          (14.85, "swish", 0.6), (17.35, "whoosh", 0.8), (18.85, "whoosh", 0.7), (19.75, "swish", 0.3), (20.49, "crash", 0.6),
          (21.25, "swish", 0.35), (21.6, "ding", 0.5)]
    ev += [(t, "bump", 0.18) for t in np.arange(1.43, 21, 2.6)]
    return ev


def extra_sfx(kind):
    import audio as A
    if kind == "door_clunk":
        y = np.zeros(int(0.6 * A.SR))
        b = A.boom(140, 70, 0.3, 0.05)
        y[:len(b)] += b * 0.8
        cl = A.fft_filter(A.noise(0.04), 800, 6000) * A.env(0.04, 0.0005, 0.01)
        y[:len(cl)] += A.norm(cl) * 0.6
        return A.with_tail(A.st(y), 0.15, 0.6, 4000)
    if kind == "toast_pop":
        d = 0.35
        t = A.T(d)
        spring = np.sin(2 * np.pi * (900 + 600 * np.exp(-t * 20)) * t) * np.exp(-t * 14) * 0.5
        cl = A.norm(A.click(0.01, 2500)) * 0.8
        spring[:len(cl)] += cl
        return A.st(spring, 0.4)
    if kind == "crash":
        d = 1.2
        t = A.T(d)
        y = A.fft_filter(A.noise(d), 2000, 14000) * np.exp(-t * 7)
        for f in (2400, 3700, 5100, 6900):
            y += np.sin(2 * np.pi * f * t) * np.exp(-t * 9) * 0.2
        y[:int(0.02 * A.SR)] += A.norm(A.body(0.02, 300, 3000))
        return A.with_tail(A.st(A.norm(y) * 0.8, 0.5), 0.2, 0.8, 7000)
    if kind == "ding":
        d = 2.0
        t = A.T(d)
        y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in ((1568, 1, 2.0), (3136, 0.3, 4), (4704, 0.12, 6)))
        return A.with_tail(A.st(y * 0.6), 0.25, 1.4, 8000)
    if kind == "bump":
        y = A.boom(90, 60, 0.15, 0.03) * 0.6
        return A.st(y, 0.6)
    if kind == "hum":
        d = 6.0
        t = A.T(d)
        y = (np.sin(2 * np.pi * 60 * t) * 0.5 + np.sin(2 * np.pi * 120 * t) * 0.3 + A.fft_filter(A.noise(d), 200, 900) * 0.15)
        return A.st(y * 0.5)
    return A.SFX(kind)


def render_audio(out_wav):
    import audio as A
    import soundfile as sf
    n = int(DURATION * A.SR)
    mix = np.zeros((n, 2))
    fx = np.zeros((n, 2))
    for t0, kind, g in sfx_events():
        A.place(fx, t0, extra_sfx(kind), g)
    hum = extra_sfx("hum")
    hum[-int(0.15 * A.SR):] *= np.linspace(1, 0, int(0.15 * A.SR))[:, None]
    A.place(fx, 0.0, hum[: int(5.85 * A.SR)], 0.35)
    vo = np.zeros(n)
    for key, t0 in VO_START.items():
        A.place1(vo, t0, A.load_vo(os.path.join(HERE, "build", "kitchen", "vo", f"{key}.wav")))
    vo = A.norm(vo, 0.9)
    music = A.bed("wonder", DURATION + 0.5, 2)[:n]
    e = A.follower(vo)
    e = np.clip(e / (e.max() + 1e-9) * 2.5, 0, 1)
    mix = A.st(vo) * 0.75 + music * 0.35 * (1 - 0.6 * e)[:, None] + fx * 0.55 * (1 - 0.3 * e)[:, None]
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    raw = out_wav.replace(".wav", "_raw.wav")
    sf.write(raw, mix.astype(np.float32), A.SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9", "-ar", str(A.SR), out_wav], check=True)
    return out_wav


# ---------------------------------------------------------------- main
_ARGS = None


def _init(w, h):
    global _ARGS, TALL
    _ARGS = (w, h)
    TALL = h > w


def _job(i):
    return frame(i / FPS, *_ARGS).tobytes()


def render(tall=False, procs=2):
    w, h = (1080, 1920) if tall else (1920, 1080)
    name = "kitchen_tall" if tall else "kitchen_wide"
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    bdir = os.path.join(HERE, "build", "kitchen")
    os.makedirs(bdir, exist_ok=True)
    wav = render_audio(os.path.join(bdir, "mix.wav"))
    silent = os.path.join(bdir, f"{name}_video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    n = int(DURATION * FPS)
    with Pool(procs, initializer=_init, initargs=(w, h)) as pool:
        for k, buf in enumerate(pool.imap(_job, range(n), chunksize=2)):
            ff.stdin.write(buf)
            if k % 60 == 0:
                print(f"{name}: {k}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    out = os.path.join(HERE, "out", f"{name}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    tall = "--tall" in sys.argv
    TALL = tall
    if "--still" in sys.argv:
        from PIL import Image
        w, h = (1080, 1920) if tall else (1920, 1080)
        d = os.path.join(HERE, "build", "kitchen")
        os.makedirs(d, exist_ok=True)
        for s in sys.argv[sys.argv.index("--still") + 1].split(","):
            p = os.path.join(d, f"{'tall' if tall else 'wide'}_t{float(s):05.2f}.png")
            Image.fromarray(frame(float(s), w, h)).save(p)
            print(p)
    else:
        render(tall, int(os.environ.get("PROCS", "2")))
