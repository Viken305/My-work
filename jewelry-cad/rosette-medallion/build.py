"""
Parametric CAD generator - acanthus rosette medallion pendant (trial).

The relief is built as a high-resolution height field from simple shapes
(boss, acanthus leaves, fleur buds, concave bowls, C-scrolls, beads), each with
its own rounded profile, combined by "highest wins".  The design has 4-fold
mirror symmetry, so one 1/8 wedge is drawn and repeated.

Back is hollowed (constant wall) to keep weight down, with a hidden tube bail.
All sizes in mm; edit PARAMS and run `python3 build.py`.

Reference photo is 225 px; the outer bud tips sit at r = 107 px.
"""
import json
import math
import os
import sys

import numpy as np
import trimesh
from manifold3d import CrossSection, FillRule, Manifold, Mesh
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely.geometry import Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from stl_clean import export_clean  # noqa: E402

PARAMS = dict(
    diameter=31.0,       # tip-to-tip diameter (outer buds)
    res=0.04,            # height-field resolution (mm)
    ground=0.80,         # background plate thickness
    boss_top=4.20,       # highest point (centre dome)
    leaf_h=1.45,         # acanthus leaf height above ground
    bud_h=1.70,          # fleur bud height above ground
    band_h=1.25,         # C-scroll band height above ground
    bowl_rim=1.20,       # bowl lip height above ground
    bowl_depth=0.95,     # how far the bowl dips below its lip
    bead_r=0.42,         # rim bead radius
    vein_depth=0.22,
    hollow_back=True,
    wall=0.80,           # wall thickness of hollowed back
    back_rim=1.0,        # solid border left around the hollow
    bail=True,
    bail_od=2.8, bail_id=1.8, bail_len=5.0,
    simplify_tol=0.002,  # mesh decimation tolerance in mm (0 = keep every triangle)
)
DENSITY = {"22K yellow (91.6%)": 17.80, "18K yellow (75%)": 15.50, "14K yellow (58.5%)": 13.00,
           "Silver 925": 10.36, "Casting wax (approx)": 1.00}

P = PARAMS
S = (P["diameter"] / 2) / 107.0          # mm per photo pixel
G = P["ground"]
RES = P["res"]
E = P["diameter"] / 2 + 0.6               # half-extent of grid
xs = np.arange(-E, E + RES / 2, RES)
N = len(xs)
X, Y = np.meshgrid(xs, xs[::-1])          # row 0 = top (y = +E)
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


# ----------------------------------------------------------------------------
# geometry helpers (shapes are defined in photo pixels, polar from north, CW)
# ----------------------------------------------------------------------------
def pol(r, th_deg):
    t = math.radians(th_deg)
    return (r * math.sin(t) * S, r * math.cos(t) * S)


def rot(pts, deg, mirror=False):
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    out = []
    for x, y in pts:
        if mirror:
            x = -x
        out.append((c * x + s * y, -s * x + c * y))  # clockwise rotation
    return out


def copies4(pts):
    return [rot(pts, k * 90) for k in range(4)]


def copies8(pts):
    return [rot(pts, k * 90, m) for k in range(4) for m in (False, True)]


SS = 3  # supersampling for anti-aliased distance fields


def to_px(pts, ss=1):
    return [((x + E) / RES * ss, (E - y) / RES * ss) for x, y in pts]


def _sd_from_image(im):
    """High-res mask image -> (low-res bool mask, signed distance in mm, +inside)."""
    m = np.asarray(im) > 127
    sd = (ndimage.distance_transform_edt(m) - ndimage.distance_transform_edt(~m)) * (RES / SS)
    sd = sd.reshape(N, SS, N, SS).mean(axis=(1, 3))
    return sd > 0, sd


def mask_polys(polys):
    im = Image.new("L", (N * SS, N * SS), 0)
    d = ImageDraw.Draw(im)
    for p in polys:
        d.polygon(to_px(p, SS), fill=255)
    return _sd_from_image(im)


def mask_tubes(paths):
    """paths: list of (pts, half_widths) - tapered round-ended strokes."""
    im = Image.new("L", (N * SS, N * SS), 0)
    d = ImageDraw.Draw(im)
    for pts, hw in paths:
        pp = to_px(pts, SS)
        for i in range(len(pp) - 1):
            w = (hw[i] + hw[i + 1]) / RES * SS
            d.line([pp[i], pp[i + 1]], fill=255, width=max(int(round(w)), 1))
        for (cx, cy), h in zip(pp, hw):
            r = h / RES * SS
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return _sd_from_image(im)


def dome(sd, ramp, height):
    """Rounded profile; finite edge slope so walls stay castable and smooth."""
    t = np.clip(sd / ramp, 0, 1)
    return height * (0.55 * np.sqrt(1 - (1 - t) ** 2) + 0.45 * (1 - (1 - t) ** 2))


def seg_dist(ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy or 1e-9
    t = np.clip(((X - ax) * vx + (Y - ay) * vy) / L2, 0, 1)
    return np.hypot(X - (ax + t * vx), Y - (ay + t * vy))


def spheres(H, centres, r, zc):
    for cx, cy in centres:
        d2 = (X - cx) ** 2 + (Y - cy) ** 2
        inside = d2 < r * r
        H[inside] = np.maximum(H[inside], zc + np.sqrt(r * r - d2[inside]))


# ----------------------------------------------------------------------------
# design elements
# ----------------------------------------------------------------------------
def acanthus(r0, r1, wmax, lobes, wmin_k=0.37):
    """Lobed leaf along +Y between radii r0..r1 (px). Returns outline + vein segments."""
    n = 120
    t = np.linspace(0, 1, n)
    env = wmax * np.sin(np.pi * (0.12 + 0.88 * t)) ** 0.7
    env = np.maximum(env, wmax * wmin_k * (1 - t) ** 0.5 * (t < 0.3) + 0)
    ser = 0.80 + 0.20 * np.abs(np.sin(lobes * np.pi * t)) ** 0.45
    w = env * ser
    r = r0 + (r1 - r0) * t
    right = [pol(rr, 0)[1] for rr in r]
    pts = [(ww * S, yy) for ww, yy in zip(w, right)] + [(-ww * S, yy) for ww, yy in zip(w[::-1], right[::-1])]
    veins = []
    for k in range(lobes):
        tk = (k + 0.55) / lobes
        if tk > 0.95:
            continue
        i = int(tk * (n - 1))
        y0 = pol(r0 + (r1 - r0) * max(tk - 0.14, 0.02), 0)[1]
        for sx in (-1, 1):
            veins.append(((0.0, y0), (sx * w[i] * 0.80 * S, right[i])))
    veins.append(((0.0, pol(r0 + 2, 0)[1]), (0.0, pol(r1 - 3, 0)[1])))  # midrib line
    return pts, veins


def lobe(rs, a0, length, hw0):
    """Acanthus finger: leaves the spine at radius rs, heading a0 deg off the
    axis, sweeps outward and curls its tip back.  Local +x side."""
    x, y = 0.0, rs * S
    hd = math.radians(a0)
    pts, n = [(x, y)], 40
    ds = length * S / n
    for i in range(n):
        f = i / n
        hd += math.radians(0.5 + 2.2 * f ** 2)
        x += math.sin(hd) * ds
        y += math.cos(hd) * ds
        pts.append((x, y))
    hw = [hw0 * S * (1 - 0.70 * (i / n) ** 1.3) for i in range(n + 1)]
    return pts, hw


def bowl_frame(ctr_r, ctr_th, ar, at):
    """Ellipse (px) centred at polar (ctr_r, ctr_th), axes radial ar / tangential at."""
    cx, cy = pol(ctr_r, ctr_th)
    u = np.array([math.sin(math.radians(ctr_th)), math.cos(math.radians(ctr_th))])  # outward
    v = np.array([u[1], -u[0]])  # toward increasing angle (clockwise)
    return np.array([cx, cy]), u, v, ar * S, at * S


def ellipse_pts(fr, phis, grow=0.0):
    c, u, v, ar, at = fr
    return [tuple(c + (ar + grow) * math.cos(p) * (-u) + (at + grow) * math.sin(p) * v) for p in phis]


def c_scroll(fr):
    """Band running round the bowl (boss side -> diagonal side -> outer side ->
    axis side) and finishing in an inward spiral curl."""
    phis = np.radians(np.linspace(28, 292, 90))
    pts = ellipse_pts(fr, phis, grow=2.6 * S)
    # spiral: keep turning the same way with increasing curvature
    x, y = pts[-1]
    px_, py_ = pts[-2]
    hd = math.atan2(y - py_, x - px_)
    (ax, ay), (bx, by) = np.subtract(pts[-10], pts[-20]), np.subtract(pts[-1], pts[-10])
    sgn = 1 if ax * by - ay * bx > 0 else -1
    ds = 0.35 * S
    curv = 1 / (14 * S)
    spiral = []
    for i in range(70):
        curv *= 1.045
        hd += sgn * curv * ds
        x += math.cos(hd) * ds
        y += math.sin(hd) * ds
        spiral.append((x, y))
        if 1 / curv < 1.8 * S:
            break
    path = pts + spiral
    n1, n2 = len(pts), len(spiral)
    hw = [3.3 * S * (0.75 + 0.25 * math.sin(math.pi * i / (n1 - 1))) for i in range(n1)]
    hw += [3.3 * S * 0.75 * (1 - 0.45 * i / max(n2 - 1, 1)) for i in range(n2)]
    eye = spiral[-1] if spiral else pts[-1]
    return path, hw, eye


def teardrop(r0, r1, wmax, power=0.8, tip_sharp=1.4):
    t = np.linspace(0, 1, 90)
    w = wmax * np.sin(np.pi * t) ** power * (1 - t) ** (tip_sharp - 1) * 1.0
    w = w / max(w.max(), 1e-9) * wmax
    ys = r0 + (r1 - r0) * t
    pts = [(ww * S, yy * S) for ww, yy in zip(w, ys)] + [(-ww * S, yy * S) for ww, yy in zip(w[::-1], ys[::-1])]
    return pts


def horn(sx):
    """Side petal of the fleur bud: curved tapering stroke."""
    pts = []
    for t in np.linspace(0, 1, 40):
        a = math.radians(5 + 28 * t)
        r = 74 + 15 * math.sin(math.pi * t * 0.9)
        x, y = r * math.sin(a) * S * sx, r * math.cos(a) * S
        pts.append((x, y))
    # tip curls back toward the bud
    x, y = pts[-1]
    for k in range(10):
        a = math.radians(-60 - 14 * k)
        pts.append((x + sx * 2.2 * S * math.cos(a) - sx * 2.2 * S, y + 2.2 * S * math.sin(a) + 2.2 * S * 0.9))
    hw = [S * (4.0 - 2.6 * i / (len(pts) - 1)) for i in range(len(pts))]
    return pts, hw


# ----------------------------------------------------------------------------
def build_heightfield():
    H = np.full((N, N), G)
    R = np.hypot(X, Y)
    info = {}

    # --- base disc + beaded rim --------------------------------------------
    base_r = 97 * S
    rim_hw = 4.5 * S
    H = np.maximum(H, G + 0.35 * np.sqrt(np.clip(1 - ((R - 92.5 * S) / rim_hw) ** 2, 0, 1)) ** 0.5)
    nb = 80
    spheres(H, [pol(93, 360 * k / nb) for k in range(nb)], P["bead_r"], G + 0.15)
    info["rim_beads"] = nb

    # --- concave bowls (8) ---------------------------------------------------
    fr = bowl_frame(64, 24.5, 19.5, 16.5)
    phis = np.linspace(0, 2 * math.pi, 120, endpoint=False)
    bowl = ellipse_pts(fr, phis)
    bm, sd = mask_polys(copies8(bowl))
    lip = dome(sd, 0.45, P["bowl_rim"])
    tt = np.clip(sd / (fr[4] * 0.95), 0, 1)
    dip = P["bowl_depth"] * (1 - (1 - tt) ** 2)
    Hb = np.where(bm, G + lip - dip + P["bowl_depth"] * 0.0, G)
    Hb = np.where(bm, np.maximum(Hb, G + 0.12), G)
    H = np.maximum(H, Hb)
    # inside the bowls the bowl surface replaces the rim ring
    H = np.where(bm & (Hb < H) & (R < 88 * S), Hb, H)

    # --- C-scroll bands with spiral curls -----------------------------------
    path, hw, eye = c_scroll(fr)
    tubes = [(rot(path, k * 90, m), hw) for k in range(4) for m in (False, True)]
    tm, tsd = mask_tubes(tubes)
    H = np.maximum(H, np.where(tm, G + dome(tsd, 3.3 * S * 0.75, P["band_h"]), G))
    eyes = [rot([eye], k * 90, m)[0] for k in range(4) for m in (False, True)]
    spheres(H, eyes, 1.9 * S, G + P["band_h"] - 1.9 * S * 0.6)

    # --- cardinal acanthus leaves: domed spine + separately domed lobes -----
    slope = np.clip(1 - (R - 17 * S) / (46 * S), 0, 1) * 0.70     # rises toward the boss
    spine = teardrop(17, 64, 7.5, power=0.6, tip_sharp=1.25)
    sm_, ssd = mask_polys(copies4(spine))
    Hs = G + dome(ssd, 1.05, 1.0) * (P["leaf_h"] + 0.25 + slope)
    mid = np.full((N, N), 9.0)
    for k in range(4):
        (ax, ay), (bx, by) = rot([pol(20, 0), pol(60, 0)], k * 90)
        mid = np.minimum(mid, seg_dist(ax, ay, bx, by))
    Hs -= np.where(sm_, 0.20 * np.exp(-(mid / 0.07) ** 2), 0)      # centre vein groove
    H = np.where(sm_, np.maximum(H, Hs), H)
    for (rs, a0, length, hw0) in [(22, 38, 17, 4.4), (31, 30, 18, 4.6), (40, 22, 16, 4.2), (49, 14, 12, 3.4)]:
        pts, hw = lobe(rs, a0, length, hw0)
        lm, lsd = mask_tubes([(c, hw) for c in copies8(pts)])
        Hl = G + dome(lsd, hw0 * S * 1.1, 1.0) * (P["leaf_h"] + 0.1 + slope * 0.8)
        H = np.where(lm, np.maximum(H, Hl), H)
    # berry clusters at the leaf tips
    berries = [(0, 66), (-4.5, 62.5), (4.5, 62.5), (-3, 69.5), (3, 69.5)]
    cen = []
    for bx, by in berries:
        cen += [rot([(bx * S, by * S)], k * 90)[0] for k in range(4)]
    spheres(H, cen, 2.6 * S, G + 0.55)
    info["berries"] = len(cen)

    # --- fleur buds on the axes (pointing out) -------------------------------
    bud = teardrop(71, 108, 9.5, power=0.75, tip_sharp=1.35)
    um, usd = mask_polys(copies4(bud))
    Hu = G + dome(usd, 1.0, P["bud_h"])
    H = np.where(um, np.maximum(H, Hu), H)
    horns = []
    for sx in (-1, 1):
        pts, hw2 = horn(sx)
        horns += [(rot(pts, k * 90), hw2) for k in range(4)]
    hm, hsd = mask_tubes(horns)
    H = np.maximum(H, np.where(hm, G + dome(hsd, 0.45, P["bud_h"] * 0.75), G))
    collar, csd = mask_tubes([(rot([pol(72, -9), pol(73, 0), pol(72, 9)], k * 90), [2.0 * S] * 3) for k in range(4)])
    H = np.maximum(H, np.where(collar, G + dome(csd, 0.25, P["bud_h"] * 0.95), G))

    # --- diagonal leaves (pointing out) + inner sprigs ----------------------
    dleaf, dveins = acanthus(70, 105, 10.5, 3, wmin_k=0.5)
    dleaf = rot(dleaf, 45)
    dm, dsd = mask_polys(copies4(dleaf))
    Hd = G + dome(dsd, 1.0, P["leaf_h"] * 0.95)
    vd = np.full((N, N), 9.0)
    for k in range(4):
        for a, b in dveins:
            (ax, ay), (bx, by) = rot([a, b], 45 + k * 90)
            vd = np.minimum(vd, seg_dist(ax, ay, bx, by))
    Hd -= np.where(dm, P["vein_depth"] * 0.8 * np.exp(-(vd / 0.08) ** 2), 0)
    H = np.where(dm, np.maximum(H, Hd), H)
    sprig = rot(teardrop(30, 52, 5.5, power=0.7, tip_sharp=1.5), 45)
    sm, spsd = mask_polys(copies4(sprig))
    H = np.where(sm, np.maximum(H, G + dome(spsd, 0.45, P["leaf_h"] * 0.9)), H)
    spheres(H, [rot([pol(55.5, 45 + d)], k * 90)[0] for k in range(4) for d in (-5, 0, 5)], 2.3 * S, G + 0.45)

    # --- centre boss: two rings + dome --------------------------------------
    ring = lambda rc, hw, h: np.where(np.abs(R - rc) < hw, h * np.sqrt(np.clip(1 - ((R - rc) / hw) ** 2, 0, 1)), 0)
    H = np.maximum(H, np.where(np.abs(R - 20.5 * S) < 2.8 * S, G + 1.30 + ring(20.5 * S, 2.8 * S, 0.65), 0))
    H = np.maximum(H, np.where(R < 18 * S, G + 1.55, 0))
    H = np.maximum(H, np.where(np.abs(R - 16.0 * S) < 2.0 * S, G + 1.75 + ring(16.0 * S, 2.0 * S, 0.65), 0))
    rd = 12.5 * S
    dome_h = P["boss_top"] - (G + 1.55)
    H = np.maximum(H, np.where(R < rd, G + 1.55 + dome_h * np.sqrt(np.clip(1 - (R / rd) ** 2, 0, 1)), 0))

    # --- outline -------------------------------------------------------------
    outline = (R < base_r) | um | dm | hm
    outline = ndimage.binary_closing(outline, iterations=3)
    return H, outline, info


def heightfield_solid(Z, z_bottom):
    """Watertight block: top surface Z (N x N grid), flat bottom."""
    n = Z.shape[0]
    top = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
    bot = np.c_[X.ravel(), Y.ravel(), np.full(n * n, z_bottom)]
    V = np.vstack([top, bot])
    idx = np.arange(n * n).reshape(n, n)
    a, b, c, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, :-1], idx[1:, 1:]
    ft = np.c_[np.c_[a.ravel(), c.ravel(), b.ravel()].T, np.c_[b.ravel(), c.ravel(), d.ravel()].T].T
    fb = ft[:, ::-1] + n * n
    sides = []
    for edge in (idx[0, :], idx[:, -1], idx[-1, ::-1], idx[::-1, 0]):
        e0, e1 = edge[:-1], edge[1:]
        sides.append(np.c_[e0, e1, e1 + n * n])
        sides.append(np.c_[e0, e1 + n * n, e0 + n * n])
    F = np.vstack([ft, fb] + sides).astype(np.uint32)
    p = V[F]
    if np.einsum("ij,ij->i", p[:, 0], np.cross(p[:, 1], p[:, 2])).sum() < 0:
        F = F[:, ::-1].copy()
    return Manifold(Mesh(vert_properties=V.astype(np.float32), tri_verts=F))


def mask_to_cs(mask, inset=0.0):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure()
    cs = plt.contour(X, Y, mask.astype(float), levels=[0.5])
    polys = []
    for seg in cs.allsegs[0]:
        if len(seg) > 3:
            polys.append(Polygon(seg).buffer(0))
    plt.close(fig)
    g = unary_union(polys)
    # keep outer rings only (holes are not expected in the outline)
    g = unary_union([Polygon(p.exterior) for p in getattr(g, "geoms", [g])])
    g = g.buffer(-0.05).buffer(0.05)
    if inset:
        g = g.buffer(-inset)
    rings = []
    for p in getattr(g, "geoms", [g]):
        p = p.simplify(0.01)
        rings.append(np.asarray(p.exterior.coords)[:-1])
    return CrossSection(rings, FillRule.EvenOdd), g


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"grid {N} x {N} @ {RES} mm ...", flush=True)
    H, outline, info = build_heightfield()
    H = ndimage.gaussian_filter(H, 1.1)   # soften pixel steps (~0.05 mm)
    cs, outline_poly = mask_to_cs(outline)
    prism = cs.extrude(10).translate((0, 0, -1))
    body = heightfield_solid(np.maximum(H, 0.3), 0.0) ^ prism

    if P["hollow_back"]:
        r = int(round(P["wall"] / RES))
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        foot = xx * xx + yy * yy <= r * r
        cav = ndimage.grey_erosion(H, footprint=foot) - P["wall"]
        cav = np.minimum(ndimage.gaussian_filter(cav, 3), H - P["wall"])
        cs_in, _ = mask_to_cs(outline, inset=P["back_rim"])
        if P["bail"]:  # keep solid metal where the bail is soldered
            bail_y = 97 * S - 2.6
            keep = (np.abs(X) < P["bail_len"] / 2 + 0.6) & (np.abs(Y - bail_y) < P["bail_od"] / 2 + 0.5)
            cav[keep] = -0.5
        cav = np.where(cav > 0.15, cav, -0.5)
        cavity = heightfield_solid(cav, -1.0) ^ cs_in.extrude(10).translate((0, 0, -2))
        body = body - cavity

    if P["bail"]:
        L, ro, ri = P["bail_len"], P["bail_od"] / 2, P["bail_id"] / 2
        tube = (Manifold.cylinder(L, ro, circular_segments=64) - Manifold.cylinder(L + 1, ri, circular_segments=64).translate((0, 0, -0.5)))
        tube = tube.rotate((0, 90, 0)).translate((-L / 2, 97 * S - 2.6, -ro + 0.35))
        body = body + tube

    body = body.simplify(P["simplify_tol"])
    pieces = sum(1 for p in body.decompose() if p.volume() > 1e-3)
    if pieces != 1:
        raise RuntimeError(f"medallion is {pieces} separate pieces, expected 1 (bail or a feature is not attached)")
    mesh = body.to_mesh64()
    tm, mesh_check = export_clean(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts),
                                  os.path.join(OUT_DIR, "rosette_medallion.stl"))
    vol = body.volume() / 1000
    bb = body.bounding_box()
    rep = {
        "params": P, "status": body.status().name, "triangles": len(tm.faces), "mesh_check": mesh_check,
        "size_mm": {"width": round(bb[3] - bb[0], 2), "height": round(bb[4] - bb[1], 2), "thickness": round(bb[5] - bb[2], 2)},
        "volume_cm3": round(vol, 4),
        "weights_g": {k: round(vol * d, 2) for k, d in DENSITY.items()},
        "elements": info,
    }
    with open(os.path.join(OUT_DIR, "weight_report.json"), "w") as fh:
        json.dump(rep, fh, indent=2)
    print(json.dumps({k: rep[k] for k in ("status", "mesh_check", "triangles", "size_mm", "volume_cm3", "weights_g")}, indent=2))


if __name__ == "__main__":
    main()
