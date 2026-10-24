"""Episode 1 · Why your microwave heats unevenly. 9:16, about 1:31, narrated.

  python3 voiceover.py                  # narration + build/vo/timeline.json (once)
  python3 film.py --still 3,9.5,26      # quick frames -> build/stills/
  python3 film.py                       # -> out/ep01_microwave.mp4

Set, renderer and sound kit come from ../style-tests (the approved 3D kitchen test).
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool

import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "style-tests"))

import gl3d as G  # noqa: E402
from gl3d import Geo, Rx, Ry, Rz, S, T, box, cylinder, hexc, quad, sphere, srgb, torus  # noqa: E402
import kitchen as K  # noqa: E402
from kitchen import (BODY, CAT, CAT_DK, CAVITY, CREAM, CX0, CX1, CY0, CY1, CZ0, CZ1, MUG_BLUE, PLATE_C, RED, STEEL, TRIM,  # noqa: E402
                     clamp, heat_at, heat_rgb, in_out, in_out_expo, lerp, limb, mug, out_back, out_expo, prog, smooth, v3)

W, H, FPS = 1080, 1920, 30
TL = json.load(open(os.path.join(HERE, "build", "vo", "timeline.json")))


def C(key, off=0.0):
    """Cue: start of narration line `key` plus an offset."""
    return TL[key]["start"] + off


DURATION = 91.5
SHOVE, FALL0 = 87.4, 87.7
MUG_DROP = math.sqrt(2 * 3.6 / 30.0)
CRASH = FALL0 + MUG_DROP


# ---------------------------------------------------------------- state of the microwave over the film
def states(t):
    s = {}
    s["xray"] = smooth(prog(t, 7.0, 7.6)) * (1 - smooth(prog(t, 23.7, 24.0)))
    s["door"] = -math.radians(108) * out_back(prog(t, 47.1, 47.5), 1.0)
    s["lift"] = out_expo(prog(t, 47.4, 47.9))
    s["roof_a"] = 1 - smooth(prog(t, 47.65, 48.0))
    s["door_hidden"] = 55.6 <= t < 60.9 or t >= 65.4 and t < 86.4
    s["tiles"] = out_expo(prog(t, 55.8, 56.6)) * (1 - in_out(prog(t, 60.9, 61.5)))
    s["tiles_show"] = prog(t, 55.7, 56.0) * (1 - prog(t, 70.8, 71.2))
    s["plate"] = 0.0 if 55.6 <= t < 60.95 else 1.0
    s["plate_out"] = out_expo(prog(t, 71.5, 72.1))
    s["bowl_warm"] = smooth(prog(t, 61.4, 62.2))
    s["choc"] = 1 - out_expo(prog(t, 72.2, 72.8)) if 72.2 <= t else None
    s["melt"] = smooth(prog(t, 74.1, 75.7))
    s["ruler"] = out_expo(prog(t, 77.0, 77.5))
    s["lamp"] = 0.0 if 75.75 <= t < 76.0 else 1.0
    return s


# ---------------------------------------------------------------- the microwave (shell, internals, cavity contents)
def microwave(t, st):
    op, tr = [], []
    xr = st["xray"]
    XR = srgb(hexc("7CC8FF"))

    def shell(g):
        """Shell part: solid normally, translucent blue in x-ray."""
        if xr <= 0.01:
            op.append(g)
        else:
            g.C = g.C * (1 - xr) + XR * xr
            g.A[:] = 1 - 0.86 * xr
            g.E[:] = 0.5 * xr
            tr.append(g)

    door, lift, roof_a = st["door"], st["lift"], st["roof_a"]
    for g in (box(-1, 1, 0, 1.2, -0.7, -0.64, BODY, 0.02, 1, S=0.35), box(-1, -0.94, 0, 1.2, -0.7, 0.7, BODY, 0.02, 2, S=0.35),
              box(0.94, 1, 0, 1.2, -0.7, 0.7, BODY, 0.02, 3, S=0.35), box(-1, 1, 0, CY0, -0.7, 0.7, BODY, 0.02, 4, S=0.35),
              box(CX1, CX1 + 0.04, CY0, 1.14, -0.64, 0.64, BODY, 0.02, 6, S=0.35),          # partition behind the cavity wall
              box(CX1, 1, 0, 1.2, 0.64, 0.7, BODY, 0.02, 9, S=0.35)):                    # control panel face
        shell(g)
    op += [box(-0.95, -0.8, -0.04, 0.0, -0.6, -0.45, TRIM), box(0.8, 0.95, -0.04, 0.0, -0.6, -0.45, TRIM),
           box(-0.95, -0.8, -0.04, 0.0, 0.45, 0.6, TRIM), box(0.8, 0.95, -0.04, 0.0, 0.45, 0.6, TRIM)]
    shell(box(0.52, 0.88, 0.86, 1.02, 0.7, 0.71, hexc("1E3B3A"), 0.0, E=0.15))
    on = 1.0 if t < 75.75 else 0.3
    shell(box(0.56, 0.84, 0.9, 0.98, 0.705, 0.712, hexc("7CFFB2"), 0.0, E=2.5 * on))
    for k in range(3):
        y = 0.68 - k * 0.17
        shell(box(0.58, 0.82, y - 0.05, y + 0.05, 0.7, 0.74, TRIM, 0.0, 10 + k))
    if roof_a > 0.01:
        roof = box(-1, 1, 1.14, 1.2, -0.7, 0.7, BODY, 0.02, 5, S=0.35).xf(T(0, 2.2 * lift, 0) @ T(0, 0.6, 0) @ Rx(-0.5 * lift) @ T(0, -0.6, 0))
        if roof_a < 0.99:
            roof.A[:] = roof_a
            tr.append(roof)
        else:
            shell(roof)
    if lift > 0.01:
        op.append(box(-1, 1, 1.14, 1.2, -0.7, -0.64, BODY, 0.0).set(S=0.35))
    # internals: magnetron, waveguide, transformer (seen in x-ray)
    if xr > 0.01:
        mx, my, mz = 0.7, 0.4, -0.2
        glow = 0.6 + 0.4 * math.sin(t * 37) * math.sin(t * 11)
        op += [cylinder(0.13, my, my + 0.3, 20, hexc("B9BEC4"), S=1.2).xf(T(mx, 0, mz)),
               cylinder(0.16, my - 0.06, my, 20, hexc("4A4F57")).xf(T(mx, 0, mz)),
               cylinder(0.16, my + 0.3, my + 0.36, 20, hexc("4A4F57")).xf(T(mx, 0, mz)),
               cylinder(0.035, my + 0.36, my + 0.47, 10, hexc("D8C08A"), S=1.0).xf(T(mx, 0, mz)),
               sphere(0.05, 10, 8, hexc("FF8FB1"), E=2.0 * glow).xf(T(mx, my + 0.48, mz))]
        for k in range(6):
            op.append(box(mx - 0.17, mx + 0.17, my + 0.03 + k * 0.045, my + 0.04 + k * 0.045, mz - 0.17, mz + 0.17, hexc("D9DDE2"), 0.0, 60 + k, S=1.2))
        # waveguide duct from the antenna to the cavity's right wall
        wg = hexc("C9CED3")
        op += [box(CX1 + 0.04, mx + 0.16, my + 0.62, my + 0.64, mz - 0.11, mz + 0.11, wg, 0.0, S=1.0),
               box(CX1 + 0.04, mx + 0.16, my + 0.38, my + 0.40, mz - 0.11, mz + 0.11, wg, 0.0, S=1.0),
               box(CX1 + 0.04, mx + 0.16, my + 0.38, my + 0.64, mz - 0.13, mz - 0.11, wg, 0.0, S=1.0)]
        # transformer + capacitor + wires
        op += [box(0.5, 0.92, 0.08, 0.3, 0.12, 0.56, hexc("3B3F45"), 0.0, 70, S=0.4),
               cylinder(0.09, 0.3, 0.42, 16, hexc("C77B30"), S=0.8).xf(T(0.62, 0, 0.34)),
               cylinder(0.09, 0.3, 0.42, 16, hexc("C77B30"), S=0.8).xf(T(0.82, 0, 0.34)),
               cylinder(0.06, 0.06, 0.32, 14, hexc("2F6BFF"), S=0.6).xf(T(0.55, 0, -0.5)),
               limb((0.62, 0.42, 0.34), (mx, my + 0.02, mz + 0.1), 0.012, hexc("E63946")),
               limb((0.55, 0.32, -0.5), (mx - 0.08, my + 0.05, mz - 0.1), 0.012, hexc("111111"))]
    # cavity (inward quads) + the waveguide port (mica cover)
    cav = dict(S=0.1)
    cq = [quad((CX0, CY0, CZ0), (CX1, CY0, CZ0), (CX1, CY0, CZ1), (CX0, CY0, CZ1), CAVITY, **cav),
          quad((CX0, CY0, CZ0), (CX1, CY0, CZ0), (CX1, CY1, CZ0), (CX0, CY1, CZ0), CAVITY, **cav),
          quad((CX0, CY0, CZ0), (CX0, CY1, CZ0), (CX0, CY1, CZ1), (CX0, CY0, CZ1), CAVITY, **cav),
          quad((CX1, CY0, CZ0), (CX1, CY1, CZ0), (CX1, CY1, CZ1), (CX1, CY0, CZ1), CAVITY, **cav)]
    if lift <= 0.01:
        cq.append(quad((CX0, CY1, CZ0), (CX1, CY1, CZ0), (CX1, CY1, CZ1), (CX0, CY1, CZ1), CAVITY, **cav))
    for g in cq:
        if xr > 0.01:
            g.A[:] = 1 - 0.75 * xr
            tr.append(g)
        else:
            op.append(g)
    op.append(quad((CX1 - 0.002, 0.8, -0.32), (CX1 - 0.002, 1.02, -0.32), (CX1 - 0.002, 1.02, -0.08), (CX1 - 0.002, 0.8, -0.08), hexc("D8C9A8"), S=0.3))
    # door (hinged left) + glass
    if not st["door_hidden"]:
        hinge = T(-1.0, 0, 0.7) @ Ry(door) @ T(1.0, 0, -0.7)
        for b in (box(-1, -0.86, 0, 1.2, 0.7, 0.78, BODY, 0.02, 20), box(0.26, 0.42, 0, 1.2, 0.7, 0.78, BODY, 0.02, 21),
                  box(-0.86, 0.26, 0, 0.16, 0.7, 0.78, BODY, 0.02, 22), box(-0.86, 0.26, 1.04, 1.2, 0.7, 0.78, BODY, 0.02, 23)):
            shell(b.set(S=0.35).xf(hinge))
        op.append(box(0.3, 0.36, 0.3, 0.9, 0.78, 0.86, TRIM).xf(hinge))
        gl = quad((-0.86, 0.16, 0.745), (0.26, 0.16, 0.745), (0.26, 1.04, 0.745), (-0.86, 1.04, 0.745), (18, 20, 30), S=2.0, A=0.55 * (1 - 0.8 * xr)).xf(hinge)
        tr.append(gl)

    # heat-map tiles
    rise, show = st["tiles"], st["tiles_show"]
    if show > 0:
        nx, nz = 10, 8
        for i in range(nx):
            for j in range(nz):
                x0, x1 = CX0 + (CX1 - CX0) * i / nx, CX0 + (CX1 - CX0) * (i + 1) / nx
                z0, z1 = CZ0 + (CZ1 - 0.06 - CZ0) * j / nz, CZ0 + (CZ1 - 0.06 - CZ0) * (j + 1) / nz
                h = float(heat_at((x0 + x1) / 2, (z0 + z1) / 2))
                stag = clamp(rise * 1.5 - (i + j) * 0.03)
                b = box(x0 + 0.005, x1 - 0.005, CY0, CY0 + 0.012 + 0.45 * h * stag, z0 + 0.005, z1 - 0.005, (1, 1, 1), 0.0)
                col = srgb(CAVITY) * (1 - show) + heat_rgb(h) * show
                b.C[:] = col * (0.12 * show + (1 - show))
                b.E[:] = (6.0 + 9.0 * h * h) * show
                op.append(b)

    # turntable + bowl (+ spoon while stirring)
    if st["plate"] > 0 and t < 72.2:
        out = st["plate_out"]
        lift_y = 3.0 * out
        spin = t * 1.1
        px, pz = PLATE_C
        P = T(0, lift_y, 0)
        op.append(cylinder(0.5, CY0 + 0.015, CY0 + 0.045, 32, hexc("E3ECF2"), S=1.5).xf(P @ T(px, 0, pz)))
        stir = 65.4 <= t < 70.8
        bx, bz = (px, pz) if stir else (px + 0.2 * math.cos(spin), pz + 0.2 * math.sin(spin))
        op.append(cylinder(0.24, CY0 + 0.045, CY0 + 0.33, 28, hexc("F4F1EA"), r_top=0.36, caps=(True, False), S=0.8).xf(P @ T(bx, 0, bz)))
        food = food_disc(bx, bz, CY0 + 0.29 + lift_y, 0.33, spin, t)
        hcur = float(heat_at(bx, bz)) * st["bowl_warm"] * (1 - st["plate_out"])
        food.E[:] = 0.05 + 1.2 * hcur ** 2
        op.append(food)
        if stir:
            a = (t - 66.4) * 6.0 if t > 66.4 else 0.0
            sp = out_expo(prog(t, 65.9, 66.4)) * (1 - out_expo(prog(t, 68.4, 68.9)))
            if sp > 0:
                tip = v3(bx + 0.16 * math.cos(a), CY0 + 0.3, bz + 0.16 * math.sin(a))
                top = tip + v3(0.12 * math.cos(a), 0.9 * sp + 0.05, 0.12 * math.sin(a) + 0.25)
                op += [limb(tip, top, 0.025, hexc("C9CED3")), sphere(0.06, 10, 6, hexc("C9CED3"), S=1.5).xf(T(*tip) @ S(1.4, 0.4, 1))]
        # steam once it's warm
        sa = st["bowl_warm"] * (1 - out)
        if sa > 0 and not stir:
            for k in range(6):
                ph = (t * 0.6 + k / 6) % 1.0
                tr.append(sphere(0.07 + 0.09 * ph, 10, 6, (255, 255, 255), E=0.4).set(A=0.3 * sa * (1 - ph) * min(1, ph * 5))
                          .xf(T(bx + 0.06 * math.sin(k * 2.1 + t * 2), CY0 + 0.4 + ph * 0.75, bz + 0.05 * math.cos(k * 1.3 + t))))
    if st["choc"] is not None:
        op += chocolate(t, st)
    return op, tr


def food_disc(cx, cz, y, r, spin, t, rings=6, segs=28):
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
    g = Geo(P, G.flat_normals(P), G.jitter_cols(len(P), hexc("C8692F"), 0.12, 7), S=0.5, M=1.0)
    even = smooth(prog(t, 66.4, 70.0))     # stirring + standing evens it out
    g.heat_from(lambda x, yy, z: np.clip((heat_at(x, z) * 0.85 + 0.12 * np.sin(x * 9 + z * 7) ** 2) * (1 - even)
                                         + (0.62 + 0.04 * np.sin(x * 9 + z * 7)) * even, 0, 1))
    return g


# chocolate bar on the cavity floor, along the row of hot spots
CHOC_Z = CZ0 + 0.25 * (CZ1 - 0.06 - CZ0)
SPOTS = [CX0 + (CX1 - CX0) * f for f in (1 / 6, 1 / 2, 5 / 6)]
CM = (SPOTS[1] - SPOTS[0]) / 6.0          # world units per "cm" on the ruler (gap reads as 6 cm)


def chocolate(t, st):
    g = []
    slide = st["choc"]
    off = T(0, 0, 2.6 * slide)
    x0, x1 = CX0 + 0.06, CX1 - 0.06
    n = 9
    for k in range(n):
        a, b = lerp(x0, x1, k / n), lerp(x0, x1, (k + 1) / n)
        g.append(box(a + 0.006, b - 0.006, CY0, CY0 + 0.07, CHOC_Z - 0.16, CHOC_Z + 0.16, hexc("5A341C"), 0.04, 90 + k, S=0.6).xf(off))
    m = st["melt"]
    if m > 0:
        for i, x in enumerate(SPOTS):
            r = 0.095 * smooth(clamp(m * 1.3 - i * 0.12))
            if r > 0.005:
                g.append(sphere(1.0, 20, 10, hexc("6B3A1C"), S=0.6).xf(off @ T(x, CY0 + 0.07, CHOC_Z) @ S(r * 1.1, r * 0.3, r * 0.9)))
    ru = st["ruler"]
    if ru > 0:
        zr = CHOC_Z + 0.26
        R = T(0, 0.0, 1.2 * (1 - ru))
        g.append(box(x0 - 0.02, x1 + 0.02, CY0, CY0 + 0.025, zr - 0.07, zr + 0.07, hexc("F2C53D"), 0.0, S=0.4).xf(R))
        k = 0
        x = SPOTS[0] - CM * 2
        while x < x1:
            if x > x0:
                L = 0.06 if k % 5 == 0 else 0.03
                g.append(box(x - 0.003, x + 0.003, CY0 + 0.025, CY0 + 0.028, zr - 0.07, zr - 0.07 + L, (30, 30, 30), 0.0).xf(R))
            x += CM
            k += 1
    return g


# ---------------------------------------------------------------- background gags
def toaster(t):
    g = [box(2.95, 4.05, 0.0, 0.85, -0.72, 0.02, RED, 0.0, 30, S=0.7), box(2.95, 4.05, 0.0, 0.08, -0.74, 0.04, STEEL, 0.0, S=1.4),
         box(3.1, 3.9, 0.851, 0.855, -0.6, -0.48, (20, 20, 20)), box(3.1, 3.9, 0.851, 0.855, -0.24, -0.12, (20, 20, 20))]
    up = any(tp < t < tp + 1.1 for tp in (57.4, 72.0))
    g.append(box(4.05, 4.15, 0.45 if up else 0.3, 0.55 if up else 0.4, -0.42, -0.3, TRIM))
    for k, zc in enumerate((-0.54, -0.18)):
        h, spin = 0.0, 0.0
        for tp in (57.4, 72.0):
            u = t - tp - k * 0.04
            if 0 < u < 1.1:
                h = 10.5 * u - 9.55 * u * u
                spin = 2 * math.pi * (u / 1.1) * (1 if k else -1)
        yc = 0.72 + h
        g += [box(-0.32, 0.32, -0.3, 0.3, -0.045, 0.045, hexc("D9A35E"), 0.0, 40 + k, S=0.1).xf(T(3.5, yc, zc) @ Rx(spin)),
              box(-0.34, 0.34, 0.24, 0.33, -0.05, 0.05, hexc("8A5A2B"), 0.0).xf(T(3.5, yc, zc) @ Rx(spin))]
    return [x.xf(T(-0.6, 0, 0)) for x in g]


CAT_BASE = v3(4.85, 0.0, -0.45)
CAT_SCALE = 0.82
MUG_X = 5.4
NUDGES = [(56.4, 0.3), (58.9, 0.55), (72.6, 0.75)]
GLANCES = [(59.6, 60.4), (86.55, 87.3), (88.75, 99.0)]


def cat_and_mug(t, cam_eye):
    base = CAT_BASE
    g = []
    mug_z = 0.0
    for t0, b in NUDGES:
        if t > t0:
            mug_z = lerp(mug_z, b, out_expo(prog(t, t0 + 0.18, t0 + 0.35)))
    fall_t = None
    if t > SHOVE + 0.15:
        mug_z = lerp(0.75, 1.62, out_expo(prog(t, SHOVE + 0.15, FALL0)))
        if t > FALL0:
            fall_t = t - FALL0
    reach = 0.0
    for t0 in [n[0] for n in NUDGES] + [SHOVE]:
        k = prog(t, t0, t0 + 0.45)
        if 0 < k < 1:
            reach = max(reach, math.sin(math.pi * k))
    head_c = base + v3(0, 1.45, 0.15) * CAT_SCALE
    look_cam = max(smooth(prog(t, a, a + 0.15)) * (1 - smooth(prog(t, b - 0.1, b))) for a, b in GLANCES)
    tgt = v3(MUG_X, 0.3, mug_z) if fall_t is None else v3(MUG_X + 0.3, -3.6, 2.2)
    tgt = tgt * (1 - look_cam) + np.asarray(cam_eye) * look_cam
    d = tgt - head_c
    yaw = math.atan2(d[0], d[2])
    pitch = -math.atan2(d[1], math.hypot(d[0], d[2]))
    Hm = T(*head_c) @ Ry(yaw) @ Rx(clamp(pitch, -0.7, 0.5)) @ S(CAT_SCALE)
    B = T(*base) @ S(CAT_SCALE)
    breathe = 1 + 0.02 * math.sin(t * 2.4)
    g += [sphere(0.5, 18, 12, CAT, S=0.1).xf(B @ T(0, 0.62, -0.05) @ S(1.0, 1.25 * breathe, 1.05)),
          sphere(0.3, 14, 10, CREAM).xf(B @ T(0, 0.82, 0.32) @ S(1, 1.25, 0.6)),
          sphere(0.38, 18, 12, CAT, S=0.1).xf(Hm),
          sphere(0.17, 12, 8, CREAM).xf(Hm @ T(0, -0.1, 0.26) @ S(1.3, 0.8, 0.8)),
          sphere(0.045, 8, 6, hexc("E07A8A")).xf(Hm @ T(0, -0.02, 0.37))]
    blink = 0.12 if (t % 3.7) < 0.12 else 1.0
    for sx in (-1, 1):
        g.append(cylinder(0.16, 0, 0.32, 4, CAT, r_top=0.0, smooth=False).xf(Hm @ T(0.2 * sx, 0.24, 0) @ Rz(-0.35 * sx)))
        g.append(sphere(0.07, 10, 8, (18, 18, 18), S=2.0).xf(Hm @ T(0.14 * sx, 0.06, 0.31) @ S(1, 1.25 * blink, 0.6)))
        if blink > 0.5:
            g.append(sphere(0.022, 6, 4, (255, 255, 255), E=3.0).xf(Hm @ T(0.14 * sx + 0.025, 0.1, 0.355)))
        for wy in (-0.06, -0.12):
            g.append(box(0, 0.32, -0.006, 0.006, -0.006, 0.006, (245, 245, 245)).xf(
                Hm @ T(0.12 * sx, wy, 0.3) @ Rz(0.15 * sx * (1 if wy < -0.1 else -1)) @ S(sx, 1, 1)))
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
            ks = min(u, 0.6) * (1 - min(u, 0.6) / 1.4)
            py = -3.6 + max(0.0, vy * tt - 15 * tt * tt) + 0.03
            g.append(box(-0.08, 0.08, -0.03, 0.03, -0.06, 0.06, MUG_BLUE if k % 3 else (245, 245, 245), 0.0, k)
                     .xf(T(cx + vx * ks, py, cz + vz * ks) @ Ry(k * 1.3 + 6 * ks) @ Rx(k)))
    return g


# ---------------------------------------------------------------- waves: rays in x-ray, travelling/standing sheet
def rays(t, t0, t1):
    """Glowing pulses leaving the antenna, up the waveguide, then bouncing around the cavity."""
    out = []
    a = smooth(prog(t, t0, t0 + 0.3)) * (1 - smooth(prog(t, t1 - 0.4, t1)))
    if a <= 0:
        return out
    path_wg = [v3(0.7, 0.88, -0.2), v3(0.7, 0.92, -0.2), v3(CX1, 0.92, -0.2)]
    rng = np.random.default_rng(5)
    for r in range(7):
        launch = t0 + r * 0.45
        dirs = v3(-1.0, rng.uniform(-0.6, 0.4), rng.uniform(-0.8, 0.8))
        dirs /= np.linalg.norm(dirs)
        for tail in range(14):
            age = t - launch - tail * 0.025
            if age < 0:
                continue
            p = travel(age, path_wg, dirs)
            if p is None:
                continue
            fade = (1 - tail / 14) * a
            out.append(sphere(0.035 * (1 - tail / 20), 8, 6, hexc("63D7FF"), E=5.0).set(A=0.85 * fade).xf(T(*p)))
    return out


def travel(age, wg, d, speed=1.6):
    s = age * speed
    for i in range(len(wg) - 1):
        L = float(np.linalg.norm(wg[i + 1] - wg[i]))
        if s < L:
            return wg[i] + (wg[i + 1] - wg[i]) * (s / L)
        s -= L
    # inside the cavity: straight line with mirror reflections (unfolded)
    lo, hi = v3(CX0, CY0, CZ0) + 0.03, v3(CX1, CY1, CZ1 - 0.06) - 0.03
    p = wg[-1] + d * s * 1.4
    q = np.empty(3)
    for k in range(3):
        span = hi[k] - lo[k]
        u = (p[k] - lo[k]) % (2 * span)
        q[k] = lo[k] + (u if u < span else 2 * span - u)
    if s * 1.4 > 9.0:
        return None
    return q


def wave_sheet(t, mode, alpha, y0=0.62, amp=0.13, speed_hz=1.6, t_in=0.0):
    """mode 'travel' (single wave), 'bounce' (wave in, echo back, then standing), 'stand'."""
    if alpha <= 0:
        return None
    n = 60
    L = CX1 - CX0
    k = 3 * math.pi / L
    w = 2 * math.pi * speed_hz
    front = CX0 + L * smooth(prog(t, t_in, t_in + 0.9)) if mode == "bounce" else CX1
    back = CX1 - L * smooth(prog(t, t_in + 0.9, t_in + 1.8)) if mode == "bounce" else CX1
    P, Cs = [], []
    for i in range(n):
        xa, xb = CX0 + L * i / n, CX0 + L * (i + 1) / n

        def y(x):
            if mode == "travel":
                return y0 + amp * math.sin(k * 2 * (x - CX0) - w * t)
            if mode == "stand":
                return y0 + 2 * amp * math.sin(k * (x - CX0)) * math.cos(w * t)
            s = 0.0
            if x <= front:
                s += math.sin(k * (x - CX0) - w * t)
            if x >= back and t > t_in + 0.9:
                s += math.sin(k * (x - CX0) + w * t)
            return y0 + amp * s
        if mode == "bounce" and xa > front and t < t_in + 0.9:
            continue
        ya, yb = y(xa), y(xb)
        P.append([[xa, ya, -0.38], [xb, yb, -0.38], [xb, yb, 0.38]])
        P.append([[xa, ya, -0.38], [xb, yb, 0.38], [xa, ya, 0.38]])
        am = abs(math.sin(k * ((xa + xb) / 2 - CX0))) if mode != "travel" else 0.5
        c = srgb(hexc("3DB8FF")) * (1 - am * 0.5) + srgb((235, 248, 255)) * am * 0.5
        Cs += [c, c]
    if not P:
        return None
    P = np.array(P, np.float32)
    return Geo(P, G.flat_normals(P), np.array(Cs), E=1.6, A=0.55 * alpha)


def node_markers(t, a):
    out = []
    if a <= 0:
        return out
    L = CX1 - CX0
    for i in range(7):
        x = CX0 + i * L / 6
        out.append(sphere(0.035, 10, 8, hexc("2E6BFF"), E=4.0).set(A=a).xf(T(x, 0.62, 0.0)))
    for i in range(6):
        x = CX0 + (i + 0.5) * L / 6
        pulse = 0.5 + 0.5 * abs(math.cos(2 * math.pi * 1.6 * t))
        out.append(sphere(0.05 + 0.03 * pulse, 10, 8, hexc("FF4B1F"), E=5.0 * pulse).set(A=a * 0.9).xf(T(x, 0.62, 0.0)))
    return out


# ---------------------------------------------------------------- the molecule world (far from the kitchen)
MW = v3(60.0, 0.0, 0.0)
_TPL = {}


def tpl(name):
    if name not in _TPL:
        if name == "O":
            _TPL[name] = sphere(0.42, 18, 12, hexc("E63946"), S=0.8)
        elif name == "H":
            _TPL[name] = sphere(0.26, 14, 10, hexc("F4F4F4"), S=0.8)
        elif name == "bg":
            g = sphere(16.0, 24, 16, (255, 255, 255))
            ys = g.P[:, :, 1].mean(1)
            top, bot = srgb(hexc("1B2A5E")), srgb(hexc("05070F"))
            u = np.clip((ys / 16 + 1) / 2, 0, 1)[:, None]
            g.C = (bot * (1 - u) + top * u).astype(np.float32)
            g.E[:] = 1.0
            g.N = -g.N
            _TPL[name] = g
    return _TPL[name]


def copy(g):
    c = Geo.__new__(Geo)
    for k in ("P", "N", "C", "E", "S", "A", "Ht", "M"):
        setattr(c, k, getattr(g, k).copy())
    return c


FIELD_HZ = 0.9
MOLS = None


def molecule(M, heat):
    out = [copy(tpl("O")).xf(M)]
    for sx in (-1, 1):
        out.append(copy(tpl("H")).xf(M @ T(0.435 * sx, 0.336, 0)))
    if heat > 0:
        for g in out:
            g.C = g.C * (1 - 0.5 * heat) + srgb(hexc("FF6A1A")) * 0.5 * heat
            g.E[:] = 1.6 * heat
    return out


def field(t):
    return math.sin(2 * math.pi * FIELD_HZ * (t - C("07")))


def molecules(t):
    global MOLS
    if MOLS is None:
        rng = np.random.default_rng(9)
        MOLS = []
        for i in range(-3, 4):
            for j in range(-3, 4):
                for k in range(-3, 1):
                    if (i, j, k) == (0, 0, 0):
                        continue
                    p = MW + v3(i * 1.55, j * 1.55, k * 1.55) + rng.uniform(-0.35, 0.35, 3)
                    MOLS.append((p, rng.uniform(0, 2 * math.pi), rng.uniform(-0.6, 0.6), rng.uniform(0.0, 0.5)))
    out = [copy(tpl("bg")).xf(T(*MW))]
    heat = smooth(prog(t, C("08", -0.2), C("08", 0.8)))
    follow = smooth(prog(t, C("07", -0.1), C("07", 0.4)))
    e = field(t)
    jit = 0.03 + 0.18 * heat + 0.05 * follow
    for idx, (p, ph, tilt, lag) in enumerate(MOLS):
        free = ph + t * 0.4
        aligned = -math.pi / 2 * math.tanh(3 * math.sin(2 * math.pi * FIELD_HZ * (t - C("07")) - lag * 2))
        ang = free * (1 - follow) + aligned * follow
        shake = v3(math.sin(t * 13 + idx), math.sin(t * 11 + idx * 1.7), math.sin(t * 9 + idx * 2.3)) * jit
        M = T(*(p + shake)) @ Ry(tilt) @ Rz(ang + jit * math.sin(t * 17 + idx))
        out += molecule(M, heat)
    # hero molecule, closest to camera
    hero_ang = 0.25 * math.sin(t * 0.8) * (1 - follow) + (-math.pi / 2 * math.tanh(3 * e)) * follow
    Mh = T(*(MW + v3(0, 0, 1.2) + v3(math.sin(t * 13), math.sin(t * 11), 0) * jit * 0.6)) @ Rz(hero_ang) @ S(1.25)
    out += molecule(Mh, heat)
    # field arrows above and below the cloud
    fa = smooth(prog(t, C("07", -0.2), C("07", 0.3)))
    if fa > 0:
        for row_y in (3.2, -3.2):
            for i in range(-2, 3):
                c = MW + v3(i * 1.6, row_y, 0.6)
                L = 0.65 * e
                if abs(L) < 0.05:
                    continue
                a, b = c - v3(L, 0, 0), c + v3(L, 0, 0)
                out.append(limb(a, b, 0.05, hexc("FFD84A")).set(E=2.5))
                tip = b + v3(0.2 * np.sign(L), 0, 0)
                cone = cylinder(0.14, 0, 0.24, 12, hexc("FFD84A"), r_top=0.0).set(E=2.5)
                out.append(cone.xf(T(*b) @ Rz(-math.pi / 2 * np.sign(L))))
    return out


# ---------------------------------------------------------------- potato cross-section (outside-in heating)
POT = v3(-2.1, 0.44, 0.95)
POT_R = (0.58, 0.44, 0.42)


def potato(t):
    rx, ry, rz = POT_R
    creep = 0.42 * smooth(prog(t, C("09", 5.0), C("09", 9.0)))
    depth = 0.24

    def heat(x, y):
        r = np.sqrt((x / rx) ** 2 + (y / ry) ** 2)
        return np.clip((r - (1 - depth - creep)) / (depth + creep), 0, 1) ** 0.8

    out = []
    # dome (back half, skin)
    tris, nrm = [], []
    n, m = 22, 10
    for j in range(m):
        v0, v1 = (math.pi / 2) * j / m, (math.pi / 2) * (j + 1) / m
        for i in range(n):
            u0, u1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            q = lambda u, v: np.array([math.cos(u) * math.cos(v), math.sin(u) * math.cos(v), -math.sin(v)])  # noqa: E731
            a, b, c, d = q(u0, v0), q(u1, v0), q(u1, v1), q(u0, v1)
            tris += [[a, b, c], [a, c, d]]
            nrm += [[a, b, c], [a, c, d]]
    P = np.array(tris, np.float32) * np.array(POT_R, np.float32) + POT
    Nn = np.array(nrm, np.float32) / np.array(POT_R, np.float32)
    Nn /= np.linalg.norm(Nn, axis=-1, keepdims=True)
    skin = Geo(P, Nn, G.jitter_cols(len(P), hexc("A9744A"), 0.1, 3), S=0.3, M=1.0)
    skin.Ht[:] = 0.78
    out.append(skin)
    # the cut face, facing +z
    tris = []
    rings, segs = 14, 36
    for i in range(rings):
        r0, r1 = i / rings, (i + 1) / rings
        for j in range(segs):
            a0, a1 = 2 * math.pi * j / segs, 2 * math.pi * (j + 1) / segs
            p = lambda r, a: [math.cos(a) * r * rx, math.sin(a) * r * ry, 0.0]  # noqa: E731
            if i == 0:
                tris.append([p(0, 0), p(r1, a0), p(r1, a1)])
            else:
                tris += [[p(r0, a0), p(r1, a0), p(r1, a1)], [p(r0, a0), p(r1, a1), p(r0, a1)]]
    P = np.array(tris, np.float32)
    face = Geo(P + POT, np.tile([0, 0, 1.0], (len(P), 3, 1)), G.jitter_cols(len(P), hexc("F3DC96"), 0.03, 4), S=0.4, M=1.0)
    face.Ht = heat(P[:, :, 0], P[:, :, 1]).astype(np.float32)
    out.append(face)
    # the other half, skin up, lying next to it
    other = Geo(skin.P.copy(), skin.N.copy(), skin.C.copy(), S=0.3, M=1.0)
    other.P -= POT
    other.xf(T(POT[0] + 1.05, POT[1] - 0.02, POT[2] - 0.35) @ Ry(-0.5) @ Rx(-math.pi / 2) @ T(0, 0, 0))
    other.Ht[:] = 0.78
    out.append(other)
    return out


# ---------------------------------------------------------------- camera
def ease_fn(name):
    return {"io": in_out, "expo": out_expo, "ioexpo": in_out_expo, "lin": lambda x: clamp(x), "smooth": smooth}[name]


def mw(*a):
    return tuple(MW + v3(*a))


def pt(*a):
    return tuple(POT + v3(*a))


# (start, end, keys [(t, eye, target, fov)], ease, handheld, focus point, aperture)   fov = vertical, 9:16
SHOTS = [
    (0.0, 2.4, [(0.0, (-6.5, 6.0, 9.5), (-1.5, 1.0, 0.0), 74), (2.4, (-0.9, 1.6, 4.6), (-0.1, 0.6, 0.0), 62)], "ioexpo", 0.03, (0, 0.6, 0.5), 10),
    (2.4, 5.85, [(2.4, (-0.55, 0.95, 2.3), (-0.27, 0.42, 0.0), 60), (5.85, (-0.42, 0.85, 1.75), (-0.27, 0.4, 0.0), 54)], "smooth", 0.012, (-0.27, 0.4, 0.2), 22),
    (5.85, 8.1, [(5.85, (-0.6, 1.0, 3.4), (0.2, 0.6, 0.0), 62), (6.5, (1.2, 0.95, 2.8), (0.65, 0.55, 0.0), 56),
                 (8.1, (1.3, 0.95, 2.6), (0.68, 0.55, -0.1), 54)], "ioexpo", 0.02, (0.7, 0.55, 0.3), 14),
    (8.1, 11.6, [(8.1, (1.9, 0.95, 1.5), (0.7, 0.55, -0.2), 50), (11.6, (1.5, 1.35, 1.75), (0.7, 0.6, -0.2), 46)], "io", 0.015, (0.7, 0.6, -0.2), 16),
    (11.6, 15.3, [(11.6, (1.7, 1.9, 2.4), (0.5, 0.8, -0.2), 56), (15.3, (0.7, 2.0, 2.6), (0.1, 0.8, -0.2), 56)], "io", 0.015, (0.4, 0.88, -0.2), 10),
    (15.3, 18.9, [(15.3, (0.3, 2.8, 2.5), (-0.27, 0.55, 0.0), 58), (18.9, (-0.7, 2.5, 2.3), (-0.27, 0.55, 0.0), 54)], "io", 0.018, (-0.27, 0.6, 0.0), 10),
    (18.9, 24.0, [(18.9, (-1.3, 1.35, 2.3), (-0.27, 0.6, 0.0), 58), (24.0, (-0.9, 1.2, 1.9), (-0.27, 0.6, 0.0), 52)], "smooth", 0.012, (-0.27, 0.62, 0.0), 14),
    (24.0, 30.15, [(24.0, mw(0.8, 0.6, 6.5), mw(0, 0, 1.2), 62), (24.5, mw(0.4, 0.3, 4.2), mw(0, 0, 1.2), 56),
                   (30.15, mw(-0.2, 0.2, 3.6), mw(0, 0.05, 1.2), 54)], "ioexpo", 0.03, mw(0, 0, 1.2), 26),
    (30.15, 35.1, [(30.15, mw(-2.6, 1.6, 7.0), mw(0, 0.2, 0.5), 68), (35.1, mw(-1.0, 1.2, 5.8), mw(0, 0.2, 0.8), 66)], "io", 0.03, mw(0, 0, 1.2), 14),
    (35.1, 37.2, [(35.1, mw(-1.0, 1.2, 5.8), mw(0, 0.2, 0.8), 66), (35.9, mw(-0.6, 0.9, 4.2), mw(0, 0.1, 1.0), 62),
                  (37.2, mw(0.0, 0.6, 14.0), mw(0, 0.0, 0.0), 70)], "ioexpo", 0.04, mw(0, 0, 1.2), 10),
    (37.2, 42.0, [(37.2, pt(0.9, 0.9, 4.2), pt(0, -0.05, 0), 54), (42.0, pt(0.35, 0.5, 3.2), pt(0, -0.05, 0), 52)], "smooth", 0.015, pt(0, 0, 0), 14),
    (42.0, 46.6, [(42.0, pt(-0.9, 0.7, 3.3), pt(0, -0.05, 0), 52), (46.6, pt(0.7, 0.6, 3.2), pt(0, -0.05, 0), 52)], "io", 0.015, pt(0, 0, 0), 14),
    (46.6, 51.1, [(46.6, (0.6, 1.0, 3.8), (-0.2, 0.6, 0.0), 62), (47.3, (1.1, 1.35, 3.3), (-0.25, 0.6, 0.0), 62),
                  (51.1, (1.3, 3.5, 2.6), (-0.3, 0.5, 0.0), 64)], "ioexpo", 0.025, (-0.27, 0.55, 0.0), 12),
    (51.1, 55.6, [(51.1, (-0.9, 0.95, 1.9), (0.1, 0.6, -0.2), 66), (55.6, (0.25, 0.85, 1.75), (-0.6, 0.6, -0.2), 64)], "io", 0.018, (-0.27, 0.62, 0.0), 18),
    (55.6, 60.9, [(55.6, (-1.9, 2.8, 3.9), (1.3, 0.75, -0.3), 68), (58.1, (-1.7, 2.7, 3.6), (1.35, 0.75, -0.3), 66),
                  (58.4, (-1.0, 2.1, 2.2), (-0.35, 0.25, -0.3), 54), (59.5, (-0.95, 2.05, 2.1), (-0.35, 0.25, -0.3), 54),
                  (59.75, (-1.9, 2.8, 3.9), (1.3, 0.75, -0.3), 68), (60.9, (-1.8, 2.7, 3.7), (1.35, 0.75, -0.3), 67)], "ioexpo", 0.02, (-0.3, 0.4, 0.0), 14),
    (60.9, 65.4, [(60.9, (0.9, 0.62, 1.7), (-0.35, 0.35, 0.0), 62), (65.4, (-0.2, 0.55, 1.75), (-0.27, 0.35, 0.0), 58)], "io", 0.015, (-0.27, 0.4, 0.1), 22),
    (65.4, 70.8, [(65.4, (-0.27, 2.7, 1.0), (-0.27, 0.3, 0.0), 50), (70.8, (-0.27, 2.2, 0.7), (-0.27, 0.3, 0.0), 46)], "smooth", 0.012, (-0.27, 0.35, 0.0), 12),
    (70.8, 73.7, [(70.8, (-1.4, 2.6, 3.4), (0.4, 0.5, -0.2), 62), (73.7, (-1.2, 2.4, 3.0), (0.3, 0.45, -0.2), 60)], "io", 0.02, (-0.3, 0.3, -0.3), 12),
    (73.7, 76.7, [(73.7, (-0.3, 2.3, 2.5), (-0.27, 0.2, -0.3), 56), (76.7, (-0.3, 1.5, 1.3), (-0.27, 0.1, -0.33), 50)], "io", 0.015, (-0.27, 0.1, -0.33), 14),
    (76.7, 83.2, [(76.7, (-0.27, 2.6, 0.55), (-0.27, 0.06, -0.3), 54), (83.2, (-0.27, 2.3, 0.4), (-0.27, 0.06, -0.3), 52)], "smooth", 0.01, (-0.27, 0.06, -0.33), 10),
    (83.2, 86.4, [(83.2, (-0.27, 2.4, 0.45), (-0.27, 0.06, -0.3), 52), (84.0, (-1.4, 2.9, 4.6), (0.4, 0.6, -0.3), 64),
                  (86.4, (-1.5, 2.95, 4.8), (0.5, 0.6, -0.3), 64)], "ioexpo", 0.025, (-0.27, 0.3, -0.3), 8),
    (86.4, DURATION, [(86.4, (1.6, 2.2, 6.8), (4.6, 0.9, 0.0), 64), (86.85, (3.3, 1.45, 3.5), (5.0, 0.85, 0.1), 52),
                      (87.6, (3.35, 1.42, 3.45), (5.0, 0.8, 0.2), 52), (88.05, (3.4, 0.7, 4.7), (5.8, -2.7, 2.0), 62),
                      (88.55, (3.4, 0.7, 4.7), (5.8, -2.7, 2.0), 62), (88.85, (3.3, 1.45, 3.5), (5.0, 0.85, 0.1), 52),
                      (DURATION, (3.35, 1.42, 3.45), (5.0, 0.85, 0.1), 51)], "ioexpo", 0.02, (4.85, 1.2, -0.3), 10),
]
CUTS = [s[0] for s in SHOTS[1:]]


def handheld(t, amp):
    n = lambda f, p: math.sin(t * f + p) * 0.6 + math.sin(t * f * 2.31 + p * 1.7) * 0.3 + math.sin(t * f * 5.13 + p * 0.3) * 0.1  # noqa: E731
    return v3(n(1.3, 0.2), n(1.1, 1.4), n(0.9, 2.7)) * amp, n(0.7, 4.1) * amp * 0.25


def shot_at(t):
    for i, sh in enumerate(SHOTS):
        if t < sh[1] or i == len(SHOTS) - 1:
            return i, sh


def camera(t):
    i, (s0, s1, keys, ease, hh, focus, ap) = shot_at(t)
    e = ease_fn(ease)
    j = max([j for j in range(len(keys)) if keys[j][0] <= t] or [0])
    k0, k1 = keys[j], keys[min(j + 1, len(keys) - 1)]
    u = e(prog(t, k0[0], k1[0])) if k1 is not k0 else 0.0
    eye = v3(*k0[1]) * (1 - u) + v3(*k1[1]) * u
    tgt = v3(*k0[2]) * (1 - u) + v3(*k1[2]) * u
    fov = lerp(k0[3], k1[3], u)
    off, roll = handheld(t, hh)
    kick = math.exp(-(t - s0) * 9) * 0.04 * (1 if i > 0 else 0)
    if i == 2:
        roll += 0.07 * out_expo(prog(t, 5.85, 6.5))
    return dict(eye=eye + off + v3(0, kick, 0), target=tgt + off * 0.5, fov=fov, roll=roll, near=0.03, far=80.0), (s0, s1), v3(*focus), ap


# ---------------------------------------------------------------- render
LIGHTS_BASE = K.LIGHTS_BASE + [(tuple(MW + v3(-4, 5, 6)), 14.0, (1.6, 1.7, 2.0), tuple(MW - 20), tuple(MW + 20))]
SUN, SKY = K.SUN, K.SKY
CONTACT = K.CONTACT
_R = None


def get_renderer():
    global _R
    if _R is None:
        _R = G.Renderer(W, H, 1.5)
        _R.set_static(K.kitchen_static())
        _R.clear_col = SKY
    return _R


def thermal_amount(t):
    a = smooth(prog(t, 3.1, 3.4)) * (1 - smooth(prog(t, 5.6, 5.85)))
    a = max(a, smooth(prog(t, 37.2, 37.6)) * (1 - smooth(prog(t, 46.4, 46.6))))
    a = max(a, smooth(prog(t, 65.6, 66.0)) * (1 - smooth(prog(t, 70.5, 70.8))))
    return a


def thermal_wipe(t):
    for t0 in (3.1, 37.2, 65.6):
        if t0 <= t < t0 + 0.6:
            return prog(t, t0, t0 + 0.4)
    return 1.0


def scene(t, cam):
    st = states(t)
    op, tr = microwave(t, st)
    op += toaster(t) + cat_and_mug(t, cam["eye"]) + K.roomba(t)
    tr += CONTACT + [G.contact_shadow(*POT[[0, 2]], 0.6, 0.45, 0.0, 0.6)] if 37.2 <= t < 46.6 else list(CONTACT)
    if 37.2 <= t < 46.6:
        op += potato(t)
    if 24.0 <= t < 37.2:
        op += molecules(t)
    tr += rays(t, 12.4, 18.9) if 12.4 < t < 18.9 else []
    # waves
    if 18.9 <= t < 24.0:
        g = wave_sheet(t, "travel", smooth(prog(t, 18.9, 19.3)), speed_hz=1.8)
        if g is not None:
            tr.append(g)
    if 46.6 <= t < 55.8:
        a = smooth(prog(t, 48.2, 48.6))
        mode = "bounce" if t < 51.1 else "stand"
        g = wave_sheet(t, mode, a * (1 - smooth(prog(t, 55.4, 55.8))), t_in=48.4)
        if g is not None:
            tr.append(g)
        tr += node_markers(t, smooth(prog(t, C("11", 0.2), C("11", 0.8))) * (1 - smooth(prog(t, 55.4, 55.8))))
    lights = list(LIGHTS_BASE)
    lamp = st["lamp"]
    lights.append(((-0.27, 1.02, 0.0), 1.3, (3.0 * lamp, 2.4 * lamp, 1.5 * lamp), (CX0 - 0.02, CY0 - 0.02, CZ0 - 0.02), (CX1 + 0.02, 1.25, 0.9)))
    return G.cat(op), G.cat(tr), lights


def cam_speed(t):
    a, (s0, s1), _, _ = camera(t)
    t2 = t + 1 / FPS
    if t2 >= s1:
        a, _, _, _ = camera(t - 1 / FPS)
        t2 = t
    b, _, _, _ = camera(t2)
    da, db = a["target"] - a["eye"], b["target"] - b["eye"]
    ang = math.acos(clamp(float(np.dot(da, db) / np.linalg.norm(da) / np.linalg.norm(db)), -1, 1))
    return ang + np.linalg.norm(a["eye"] - b["eye"]) / max(np.linalg.norm(da), 0.3) + abs(a["fov"] - b["fov"]) * 0.01


def frame(t):
    R = get_renderer()
    _, (s0, s1), _, _ = camera(t)
    sp = cam_speed(t)
    n = 1 if sp < 0.004 else 3 if sp < 0.02 else 6
    acc = None
    for k in range(n):
        tk = min(t + (k / n) * 0.5 / FPS, s1 - 1e-4)
        cam, _, focus, ap = camera(tk)
        op, tr, lights = scene(tk, cam)
        img, depth = R.render(cam, SUN, lights, op, tr, thermal=thermal_amount(tk), thermal_x=thermal_wipe(tk))
        acc = img if acc is None else acc + img
        if k == 0:
            d0, cam0, f0, ap0 = depth, cam, focus, ap
    img = G.downsample(acc / n, W, H)
    depth = G.downsample(d0, W, H)
    fd = float(np.linalg.norm(f0 - cam0["eye"]))
    img = G.depth_of_field(img, depth, fd, ap0 * 1.0, max_sigma=8.0)
    img = G.bloom(img, 1.2, 0.3)
    img = G.vignette(G.tonemap(img, 0.85), 0.32)
    out = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    import overlay
    return overlay.draw(out, t, cam0, sys.modules[__name__])


# ---------------------------------------------------------------- main
def _job(i):
    return frame(i / FPS).tobytes()


def render(procs=2, t0=0.0, t1=None):
    import sound
    t1 = DURATION if t1 is None else t1
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    bdir = os.path.join(HERE, "build")
    os.makedirs(bdir, exist_ok=True)
    wav = sound.render_audio(os.path.join(bdir, "mix.wav"), sys.modules[__name__])
    silent = os.path.join(bdir, "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    frames = range(int(t0 * FPS), int(t1 * FPS))
    with Pool(procs) as pool:
        for k, buf in enumerate(pool.imap(_job, frames, chunksize=2)):
            ff.stdin.write(buf)
            if k % 90 == 0:
                print(f"frame {k}/{len(frames)}", flush=True)
    ff.stdin.close()
    ff.wait()
    out = os.path.join(HERE, "out", "ep01_microwave.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-ss", str(t0), "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
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
        render(int(os.environ.get("PROCS", "2")))
