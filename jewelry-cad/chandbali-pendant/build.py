"""
Parametric CAD generator - Kundan/Polki chandbali pendant set (trial).

Every dimension lives in PARAMS below (millimetres).  Change a value, re-run
`python3 build.py` and all STLs + the weight report are regenerated.

Geometry was traced from the reference photo on a pixel grid and converted to
mm with PX (mm per photo pixel).  PX = 0.18 gives "normal" proportions for this
style: chandbali ~51 mm wide, chain pearls ~7 mm, drop pearl ~8 x 12 mm.

Coordinate system: X to the right, Y up, Z out of the front face.
The back of the flat plates sits on Z = 0 (flat back, ready for casting).
"""
import json
import math
import os
import sys

import numpy as np
import trimesh
from manifold3d import CrossSection, FillRule, Manifold, Mesh, OpType, set_circular_segments
from scipy.spatial import Voronoi
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

# ----------------------------------------------------------------------------
# PARAMETERS (mm)
# ----------------------------------------------------------------------------
PARAMS = dict(
    px=0.18,                 # photo scale: mm per pixel -> overall size
    back=0.80,               # back plate thickness (closed kundan back)
    rim_w=0.60,              # plain outer rim width
    rim_top=1.60,            # rim height from back
    relief_h=0.50,           # nakashi scroll relief height above ground
    curl_size=1.60,          # scroll curl radius
    wall_w=0.50,             # gold wall between polki stones
    wall_top=2.20,           # top of polki walls from back
    polki_corner=0.35,       # corner radius of polki pockets
    pave_d=1.10,             # pave diamond diameter (chandbali / motif)
    pave_gap=0.15,           # metal between pave stones
    pave_top=1.90,           # top of pave bands
    pave_band=1.40,          # pave band width
    emerald=(5.0, 7.0),      # oval cabochon w x h at chandbali bottom
    bezel_w=0.50,
    bezel_top=2.40,
    pear_stone=(6.5, 9.4),   # centre pear polki of top motif (w x h)
    barrel_d=7.9,            # middle barrel diameter (relief ground)
    barrel_len=25.7,
    tube_wall=0.70,          # hollow barrel / tube wall
    collar_len=1.6,          # pave collar at barrel ends
    collar_pave_d=1.10,
    string_hole=1.2,         # stringing hole through barrel caps
    link_gap=3.2,            # gap between parts bridged by jump rings
    lug_r=0.80, lug_hole=0.40, lug_t=0.80,
    ring_wire=0.60,
    drop_pearl=(8.2, 12.2),
    cluster_d=1.8,           # 3-stone cluster above drop pearl
    chain_tube_d=6.0, chain_tube_len=20.0,
    seed=7,
)
DENSITY = {  # g / cm3
    "22K yellow (91.6%)": 17.80,
    "18K yellow (75%)": 15.50,
    "14K yellow (58.5%)": 13.00,
    "Silver 925": 10.36,
    "Casting wax (approx)": 1.00,
}

P = PARAMS
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
set_circular_segments(0)
from manifold3d import set_min_circular_angle, set_min_circular_edge_length  # noqa: E402

set_min_circular_angle(6.0)
set_min_circular_edge_length(0.08)
rng = np.random.default_rng(P["seed"])


# ----------------------------------------------------------------------------
# 2D / 3D helpers
# ----------------------------------------------------------------------------
def polys(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    return [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon)]


def to_cs(g):
    rings = []
    for p in polys(g):
        p = p.simplify(0.004)
        rings.append(np.asarray(p.exterior.coords)[:-1])
        rings += [np.asarray(i.coords)[:-1] for i in p.interiors]
    return CrossSection(rings, FillRule.EvenOdd)


def ext(g, z0, z1):
    if g.is_empty:
        return Manifold()
    return to_cs(g).extrude(z1 - z0).translate((0, 0, z0))


def union(ms):
    ms = [m for m in ms if not m.is_empty()]
    return Manifold.batch_boolean(ms, OpType.Add) if ms else Manifold()


def circ(x, y, r):
    return Point(x, y).buffer(r, quad_segs=48)


def ellipse(x, y, a, b):
    return affinity.translate(affinity.scale(Point(0, 0).buffer(1, quad_segs=64), a, b), x, y)


def mirror_x(g):
    return affinity.scale(g, -1, 1, origin=(0, 0))


def sym(g):
    return unary_union([g, mirror_x(g)])


def polys_pts(g):
    return [g] if isinstance(g, Point) else list(getattr(g, "geoms", []))


def points_along(line, pitch, margin=0.0):
    L = line.length
    if line.is_ring:
        n = max(int(L // pitch), 1)
        return [line.interpolate(i * L / n) for i in range(n)], L / n
    usable = L - 2 * margin
    n = max(int(usable // pitch) + 1, 1)
    step = usable / max(n - 1, 1)
    return [line.interpolate(margin + i * step) for i in range(n)], step


# ----------------------------------------------------------------------------
# Stone seats
# ----------------------------------------------------------------------------
def pave_cutter(d, top):
    """Bright-cut pave seat cut downwards from Z=top (axis +Z)."""
    rh = d * 0.32
    girdle_z = top - 0.30
    cone_h = (d / 2 - rh) * math.tan(math.radians(41))
    seat = Manifold.cylinder(0.45, d / 2 * 1.02).translate((0, 0, girdle_z))
    cone = Manifold.cylinder(cone_h, rh, d / 2 * 1.02).translate((0, 0, girdle_z - cone_h))
    hole = Manifold.cylinder(top + 1.0, rh).translate((0, 0, -0.5))
    return union([seat, cone, hole])


def brilliant(d):
    """Simple round brilliant body (for renders only)."""
    crown = Manifold.cylinder(d * 0.16, d / 2, d * 0.28)
    pav = Manifold.cylinder(d * 0.43, 0.0, d / 2).translate((0, 0, -d * 0.43))
    return union([crown, pav])


def grain(r):
    return Manifold.sphere(r, 12)


def pave_row(path, d, top, gap, both_edges=True, band=None):
    """Seats + grains + gem bodies along a shapely line."""
    pitch = d + gap
    pts, step = points_along(path, pitch, margin=d * 0.6)
    cut, grains, gems = [], [], []
    hw = (band or (d + 0.3)) / 2
    for i, p in enumerate(pts):
        cut.append(pave_cutter(d, top).translate((p.x, p.y, 0)))
        gems.append(brilliant(d).translate((p.x, p.y, top - 0.30)))
    # grains between neighbouring stones, on both band edges
    pos = [path.project(p) for p in pts]
    mids = [(pos[i] + pos[i + 1]) / 2 for i in range(len(pos) - 1)]
    if path.is_ring and len(pos) > 1:
        mids.append((pos[-1] + path.length + pos[0]) / 2 % path.length)
    for s in mids:
        a = path.interpolate(s)
        b = path.interpolate(min(s + 0.05, path.length))
        tx, ty = b.x - a.x, b.y - a.y
        n = math.hypot(tx, ty) or 1
        nx, ny = -ty / n, tx / n
        for sgn in ((-1, 1) if both_edges else (1,)):
            off = (hw - 0.22) * sgn
            grains.append(grain(0.24).translate((a.x + nx * off, a.y + ny * off, top)))
    return union(cut), union(grains), union(gems), len(pts)


def polki_cells(seeds, clip, wall, corner):
    pts = np.vstack([seeds, [[1e3 * math.cos(a), 1e3 * math.sin(a)] for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]])
    vor = Voronoi(pts)
    pockets = []
    for i in range(len(seeds)):
        reg = vor.regions[vor.point_region[i]]
        cell = Polygon(vor.vertices[reg]).intersection(clip)
        pk = cell.buffer(-(wall / 2 + corner), join_style="mitre").buffer(corner)
        pk = max(polys(pk), key=lambda q: q.area) if polys(pk) else None
        if pk is not None and pk.area > 0.8:
            pockets.append(pk)
    return pockets


# ----------------------------------------------------------------------------
# Nakashi scroll relief
# ----------------------------------------------------------------------------
def curl_path(size):
    """Centre-line (x, y) and stroke width of one nakashi curl."""
    T = 1.45 * math.pi
    t = np.linspace(0, T, 72)
    r = size * (0.30 + 0.70 * t / T)
    x, y = r * np.cos(t), r * np.sin(t)
    w = size * 0.62 * (0.30 + 0.70 * np.sin(np.pi * np.clip(t / T, 0, 1) * 0.92) ** 0.8)
    w[-8:] *= np.linspace(1, 0.2, 8)
    return x, y, w


def sweep_solid(x, y, w, h, z0, depth=0.25, m=16):
    """Closed tube along (x, y) with an elliptical section: half-width w/2,
    height h above z0 and `depth` buried below it -> a rounded relief stroke."""
    dx, dy = np.gradient(x), np.gradient(y)
    n = np.hypot(dx, dy)
    nx, ny = -dy / n, dx / n
    phi = np.linspace(0, 2 * math.pi, m, endpoint=False)
    c, s = np.cos(phi), np.sin(phi)
    zz = np.where(s > 0, h, depth) * s
    a = (w[:, None] / 2) * c[None, :]
    V = np.stack([x[:, None] + nx[:, None] * a, y[:, None] + ny[:, None] * a,
                  z0 + np.broadcast_to(zz, a.shape)], -1).reshape(-1, 3)
    N = len(x)
    F = []
    for i in range(N - 1):
        for j in range(m):
            a0, a1 = i * m + j, i * m + (j + 1) % m
            b0, b1 = a0 + m, a1 + m
            F += [(a0, b0, a1), (a1, b0, b1)]
    c0, c1 = len(V), len(V) + 1
    V = np.vstack([V, [x[0], y[0], z0], [x[-1], y[-1], z0]])
    for j in range(m):
        F.append((c0, j, (j + 1) % m))
        F.append((c1, (N - 1) * m + (j + 1) % m, (N - 1) * m + j))
    F = np.array(F, dtype=np.uint32)
    # orientation check (signed volume)
    p = V[F]
    vol = np.einsum("ij,ij->i", p[:, 0], np.cross(p[:, 1], p[:, 2])).sum()
    if vol < 0:
        F = F[:, ::-1].copy()
    return Manifold(Mesh(vert_properties=V.astype(np.float32), tri_verts=F))


def curl_solid(px_, py_, size, rot, flip, h, z0):
    x, y, w = curl_path(size)
    if flip:
        y = -y
    cr, sr = math.cos(rot), math.sin(rot)
    X, Y = px_ + cr * x - sr * y, py_ + sr * x + cr * y
    head = Manifold.sphere(1, 24).scale((size * 0.30, size * 0.30, h * 1.05)).translate((X[0], Y[0], z0))
    return sweep_solid(X, Y, w, h, z0) + head


def scroll_layout(region, size, spacing_k=1.42, half=True, tries=12000):
    """Poisson-disk placement of curls inside `region` -> (x, y, size, rot, flip)."""
    work = region.intersection(box(0, -1e3, 1e3, 1e3)) if half else region
    minx, miny, maxx, maxy = work.bounds
    sp = size * spacing_k
    pts = []
    inner = work.buffer(-size * 0.35)
    for _ in range(tries):
        p = (rng.uniform(minx, maxx), rng.uniform(miny, maxy))
        if not inner.contains(Point(p)):
            continue
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > sp * sp for q in pts):
            pts.append(p)
    return [(x, y, size * rng.uniform(0.85, 1.15), rng.uniform(0, 2 * math.pi), bool(rng.integers(2)))
            for x, y in pts]


def scroll_relief(region, size, z0, h, half=True, tries=8000):
    """Rounded nakashi relief clipped to `region` (mirror-symmetric if half)."""
    lay = scroll_layout(region, size, half=half, tries=tries)
    rel = union([curl_solid(x, y, s, r, f, h, z0) for x, y, s, r, f in lay])
    if half:
        rel = rel ^ Manifold.cube((500, 500, 50)).translate((0, -250, -25))
        rel = rel + rel.mirror((1, 0, 0))
    return rel ^ ext(region, z0 - 1, z0 + h + 1)


# ----------------------------------------------------------------------------
# Lugs and jump rings
# ----------------------------------------------------------------------------
def lug(x, y, z):
    """Flat ring tab, hole along Z, centred on plane z."""
    g = circ(0, 0, P["lug_r"]).difference(circ(0, 0, P["lug_hole"]))
    return ext(g, -P["lug_t"] / 2, P["lug_t"] / 2).translate((x, y, z))


def jump_ring(x, y_a, y_b, z):
    """Round jump ring in the YZ plane passing through two lug holes."""
    R = abs(y_b - y_a) / 2
    wire = P["ring_wire"] / 2
    torus = Manifold.revolve(CrossSection.circle(wire, 24).translate((R, 0)), 48)
    # revolve is about Z; rotate so the ring lies in YZ plane
    return torus.rotate((0, 90, 0)).translate((x, (y_a + y_b) / 2, z))


def lug_hole_cut(x, y, z):
    return Manifold.cylinder(P["lug_t"] + 2, P["lug_hole"], center=True).translate((x, y, z))


# ----------------------------------------------------------------------------
# Image -> mm
# ----------------------------------------------------------------------------
S = P["px"]
CX, CY = 347.0, 449.0  # chandbali opening centre in the photo


def ip(x, y):
    return ((x - CX) * S, (CY - y) * S)


def icirc(x, y, r):
    return circ(*ip(x, y), r * S)


# ----------------------------------------------------------------------------
# PART 1 - CHANDBALI
# ----------------------------------------------------------------------------
def build_chandbali():
    B, RT, WT, PT = P["back"], P["rim_top"], P["wall_top"], P["pave_top"]
    top_cut = box(-1e3, -1e3, 1e3, ip(0, 398)[1])
    lobes = unary_union([icirc(286, 490, 80), icirc(408, 490, 80), icirc(347, 563, 82), icirc(347, 449, 81)])
    lobes = sym(lobes.intersection(box(0, -1e3, 1e3, 1e3)))
    opening = icirc(347, 449, 67)
    outline = lobes.intersection(top_cut).difference(opening)
    outline = outline.buffer(0.4).buffer(-0.8).buffer(0.4)  # soften notches

    pave_ring = icirc(347, 449, 67 + P["pave_band"] / S).difference(opening).intersection(outline)
    band_outer = icirc(347, 470, 105).intersection(box(-1e3, -1e3, 1e3, ip(0, 405)[1]))
    band = band_outer.difference(pave_ring.buffer(0.01)).difference(opening).intersection(outline.buffer(-P["rim_w"]))

    # polki seeds: inner arc row + outer bottom row
    seeds = []
    r1 = 86 * S
    ytop = ip(0, 412)[1]
    a0 = math.asin(min(ytop / r1, 1))
    angs = np.linspace(-math.pi - a0, a0, 15)
    seeds += [(r1 * math.cos(a), r1 * math.sin(a)) for a in angs]
    r2 = 112 * S
    seeds += [(r2 * math.cos(math.radians(-90 + d)), r2 * math.sin(math.radians(-90 + d))) for d in (-27, -16, -5.3, 5.3, 16, 27)]
    seeds = np.array(seeds)
    seeds[:, 0] = np.round(seeds[:, 0], 6)
    pockets = polki_cells(seeds, band, P["wall_w"], P["polki_corner"])

    # emerald with pave halo
    ex, ey = ip(347, 607)
    ea, eb = P["emerald"][0] / 2, P["emerald"][1] / 2
    em = ellipse(ex, ey, ea, eb)
    bezel = ellipse(ex, ey, ea + P["bezel_w"], eb + P["bezel_w"])
    halo = ellipse(ex, ey, ea + P["bezel_w"] + P["pave_band"], eb + P["bezel_w"] + P["pave_band"])

    scroll_region = outline.buffer(-P["rim_w"]).difference(band.buffer(P["wall_w"] / 2 + 0.05)) \
        .difference(pave_ring.buffer(0.05)).difference(halo.buffer(0.05))
    relief = scroll_relief(scroll_region.buffer(-0.15), P["curl_size"], B, P["relief_h"])

    gold = [
        ext(outline, 0, B),                                       # back plate
        ext(outline.difference(outline.buffer(-P["rim_w"])), 0, RT),  # rim
        relief,                                                   # nakashi relief
        ext(band.buffer(P["wall_w"] / 2).intersection(outline), 0, WT),  # polki gallery
        ext(pave_ring, 0, PT),
        ext(halo.difference(bezel), 0, PT),
        ext(bezel, 0, P["bezel_top"]),
    ]
    body = union(gold)
    cuts = [ext(unary_union(pockets), B, WT + 1), ext(em, B, 5),
            ext(ellipse(ex, ey, ea * 0.55, eb * 0.6), -1, B + 0.1)]  # light hole behind emerald

    ring_line = LineString([(math.cos(a) * (67 * S + P["pave_band"] / 2), math.sin(a) * (67 * S + P["pave_band"] / 2))
                            for a in np.linspace(math.asin((ip(0, 398)[1] - 0.8) / (67 * S + 0.7)), -math.pi - math.asin((ip(0, 398)[1] - 0.8) / (67 * S + 0.7)), 300)])
    c1, g1, gm1, n1 = pave_row(ring_line, P["pave_d"], PT, P["pave_gap"], band=P["pave_band"])
    halo_line = ellipse(ex, ey, ea + P["bezel_w"] + P["pave_band"] / 2, eb + P["bezel_w"] + P["pave_band"] / 2).exterior
    c2, g2, gm2, n2 = pave_row(halo_line, P["pave_d"] * 0.9, PT, P["pave_gap"], band=P["pave_band"])

    body = body - union(cuts + [c1, c2])
    body = union([body, g1, g2])

    # lugs on the crescent tips
    tip_y = ip(0, 398)[1]
    lugs = [lug(sx * 55 * S, tip_y + P["lug_r"] - 0.45, P["lug_t"] / 2) for sx in (-1, 1)]
    body = union([body] + lugs) - union([lug_hole_cut(sx * 55 * S, tip_y + P["lug_r"] - 0.45, 0) for sx in (-1, 1)])

    gems = [ext(unary_union([p.buffer(-0.05) for p in pockets]), B + 0.02, WT - 0.15), gm1, gm2]
    cab = Manifold.sphere(1, 64).scale((ea - 0.03, eb - 0.03, 1.9)).translate((ex, ey, B + 0.02)) \
        ^ Manifold.cube((20, 20, 10)).translate((ex - 10, ey - 10, B + 0.02))
    info = dict(polki=len(pockets), pave=n1 + n2, emerald="%.1f x %.1f oval cab" % P["emerald"],
                lug_y=tip_y + P["lug_r"] - 0.45, lug_x=55 * S, emerald_body=cab)
    return body, union(gems), info


# ----------------------------------------------------------------------------
# PART 2 - TOP MOTIF
# ----------------------------------------------------------------------------
def build_top_motif():
    B, WT, PT = P["back"], P["wall_top"], P["pave_top"]

    def tp(dx, y):
        return (dx * S, (CY - y) * S)

    petals = [(59.5, 299), (36.8, 301), (45.7, 277.5), (39.2, 252.5), (23, 238.2), (13, 214.5)]
    seeds = [tp(0, 231)] + [tp(sx * dx, y) for dx, y in petals for sx in (-1, 1)]
    pw, ph = P["pear_stone"]
    pcx, pcy = tp(0, 311)  # bottom of pear stone
    rr = pw / 2
    pear = unary_union([circ(pcx, pcy + rr, rr)]).union(Point(pcx, pcy + ph).buffer(0.05)).convex_hull
    halo_in = pear.buffer(P["bezel_w"])
    halo = pear.buffer(P["bezel_w"] + P["pave_band"])

    outer = unary_union([circ(*tp(sx * dx, y), 19.5 * S) for dx, y in petals for sx in (-1, 1)] + [circ(*tp(0, 219), 19 * S)])
    body2d = unary_union([outer, MultiPolygon([circ(*s, 0.1) for s in seeds]).convex_hull, halo.buffer(0.5)])
    body2d = body2d.buffer(0.6).buffer(-0.6)
    body2d = body2d.intersection(box(-1e3, tp(0, 321)[1], 1e3, 1e3))
    body2d = sym(body2d.intersection(box(0, -1e3, 1e3, 1e3)))

    clip = body2d.buffer(-P["rim_w"]).difference(halo.buffer(P["wall_w"] / 2))
    pockets = polki_cells(np.array(seeds), clip, P["wall_w"], P["polki_corner"])

    body = union([
        ext(body2d, 0, B),
        ext(body2d.difference(halo.buffer(0.01)), 0, WT),        # gallery (walls left after pockets)
        ext(halo.difference(halo_in), 0, PT),
        ext(halo_in.difference(pear), 0, P["bezel_top"]),
    ])
    line = pear.buffer(P["bezel_w"] + P["pave_band"] / 2).exterior
    c, g, gm, n = pave_row(line, P["pave_d"], PT, P["pave_gap"], band=P["pave_band"])
    body = body - union([ext(unary_union(pockets), B, WT + 1), ext(pear, B, 5),
                         ext(pear.buffer(-1.2), -1, B + 0.1), c])
    body = union([body, g])

    bottom = tp(0, 321)[1]
    lug_pts = [(sx * 47 * S, bottom - P["lug_r"] + 0.45) for sx in (-1, 1)]
    # chain loops on the shoulders: where a 35 deg ray from the motif centre leaves the outline
    ox, oy = tp(0, 268)
    a = math.radians(35)
    hit = LineString([(ox, oy), (ox + 40 * math.cos(a), oy + 40 * math.sin(a))]).intersection(body2d.exterior)
    hit = min(polys_pts(hit), key=lambda p: p.distance(Point(ox, oy)))
    off = P["lug_r"] - 0.45
    chain_pts = [(sx * (hit.x + off * math.cos(a)), hit.y + off * math.sin(a)) for sx in (-1, 1)]
    body = union([body] + [lug(x, y, P["lug_t"] / 2) for x, y in lug_pts + chain_pts])
    body = body - union([lug_hole_cut(x, y, 0) for x, y in lug_pts + chain_pts])
    gems = union([ext(unary_union([p.buffer(-0.05) for p in pockets]), B + 0.02, WT - 0.15),
                  ext(pear.buffer(-0.05), B + 0.02, P["bezel_top"] - 0.2), gm])
    return body, gems, dict(polki=len(pockets) + 1, pave=n, lug_pts=lug_pts, bottom=bottom)


# ----------------------------------------------------------------------------
# PART 3 - ENGRAVED BARREL (also used for chain tubes)
# ----------------------------------------------------------------------------
def build_barrel(D, L, collar_len, both_collars=True, seed_shift=0):
    R = D / 2
    Rin = R - P["tube_wall"]
    C = 2 * math.pi * R
    v0, v1 = collar_len, L - collar_len
    # periodic scroll pattern in (u, v)
    region = box(0, v0 + 0.1, C, v1 - 0.1)
    lay = scroll_layout(region, P["curl_size"] * 0.95, half=False, tries=4000)
    h = P["relief_h"] * 0.9
    flat = union([curl_solid(x + k * C, y, s, r, f, h, 0.0) for x, y, s, r, f in lay for k in (-1, 0, 1)])
    flat = (flat ^ ext(box(0, v0 + 0.1, C, v1 - 0.1), -1, 2)).refine_to_length(0.3)

    def wrap(v):
        u, w, h = v[:, 0], v[:, 1], v[:, 2]
        rr = R + h
        a = u / R
        return np.c_[rr * np.cos(a), rr * np.sin(a), w]

    relief = flat.warp_batch(wrap)
    tube = Manifold.cylinder(L - 2 * 0.3, R, circular_segments=160).translate((0, 0, 0.3))
    col_r = R + 0.55
    collars = []
    gems = []
    ends = [(0.0, 1)] + ([(L, -1)] if both_collars else [(L, -1)])
    for zc, d in ends:
        has_pave = both_collars or zc == 0.0
        cl = collar_len if has_pave else 0.6
        z0 = zc if d == 1 else zc - cl
        col = Manifold.cylinder(cl, col_r, circular_segments=160).translate((0, 0, z0))
        collars.append(col)
    body = union([tube, relief] + collars)
    body = body - Manifold.cylinder(L - 2 * 0.6, Rin, circular_segments=120).translate((0, 0, 0.6))
    body = body - Manifold.cylinder(L + 2, P["string_hole"] / 2, circular_segments=48).translate((0, 0, -1))
    # radial pave seats in collars
    cuts, grains = [], []
    pd = P["collar_pave_d"]
    for zc, d in ends:
        if not (both_collars or zc == 0.0):
            continue
        zm = zc + d * collar_len / 2
        n = int(2 * math.pi * col_r // (pd + P["pave_gap"]))
        for i in range(n):
            a = 360 * i / n
            cut = pave_cutter(pd, col_r).translate((0, 0, 0)) ^ Manifold.cylinder(col_r + 2, 3, center=False)
            cuts.append(cut.rotate((0, 90, 0)).rotate((0, 0, a)).translate((0, 0, zm)))
            gems.append(brilliant(pd).translate((0, 0, col_r - 0.30)).rotate((0, 90, 0)).rotate((0, 0, a)).translate((0, 0, zm)))
            for s in (-1, 1):
                grains.append(grain(0.22).translate((0, 0, col_r)).rotate((0, 90, 0)).rotate((0, 0, a + 180 / n))
                              .translate((0, 0, zm + s * (collar_len / 2 - 0.25))))
    body = union([body - union(cuts)] + grains)
    # lay along X, centred
    body = body.translate((0, 0, -L / 2)).rotate((0, 90, 0))
    gems = union(gems).translate((0, 0, -L / 2)).rotate((0, 90, 0))
    return body, gems, dict(pave=len(cuts), outer_r=R + P["relief_h"] * 0.9)


# ----------------------------------------------------------------------------
# PART 4 - DROP (3-stone cluster + pearl cap)
# ----------------------------------------------------------------------------
def build_drop():
    d = P["cluster_d"]
    cup_r = d / 2 + 0.35
    sp = d + 0.45
    centres = [(-sp / 2, 0), (sp / 2, 0), (0, -sp * 0.866)]
    zc = 1.0
    body, cuts, gems = [], [], []
    for x, y in centres:
        body.append(Manifold.cylinder(1.6, cup_r, cup_r * 0.75, 64).translate((x, y, zc - 0.8)).rotate((0, 0, 0)))
        cuts.append(pave_cutter(d, zc + 0.8).translate((x, y, 0)))
        gems.append(brilliant(d).translate((x, y, zc + 0.5)))
    top_lug_y = cup_r + P["lug_r"] - 0.4
    body.append(lug(0, top_lug_y, zc))
    # stem + bell cap below
    yb = -sp * 0.866 - cup_r
    stem = Manifold.cylinder(1.6, 0.45, 0.45, 32).rotate((90, 0, 0)).translate((0, yb + 0.3, zc))
    cap = (Manifold.sphere(1.7, 64) - Manifold.sphere(1.25, 64)) ^ Manifold.cube((5, 2, 5), center=True).translate((0, 1.0, 0))
    cap_y = yb - 1.3
    cap = cap.translate((0, cap_y - 1.0, zc))
    peg = Manifold.cylinder(5.0, 0.4, 0.4, 24).rotate((90, 0, 0)).translate((0, cap_y - 0.6, zc))
    m = union(body + [stem, cap, peg]) - union(cuts) - lug_hole_cut(0, top_lug_y, zc)
    pa, pb = P["drop_pearl"][0] / 2, P["drop_pearl"][1] / 2
    pearl = Manifold.sphere(1, 96).scale((pa, pb, pa)).translate((0, cap_y - 1.0 - pb + 0.4, zc))
    pearl = pearl - Manifold.cylinder(5.0, 0.45, 0.45, 24).rotate((90, 0, 0)).translate((0, cap_y - 0.6, zc))
    return m, union(gems), pearl, dict(top_lug_y=top_lug_y, z=zc)


# ----------------------------------------------------------------------------
# ASSEMBLY
# ----------------------------------------------------------------------------
def export(m, name, color=None):
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    f = np.asarray(mesh.tri_verts)
    tm = trimesh.Trimesh(v, f, process=False)
    path = os.path.join(OUT_DIR, name)
    tm.export(path)
    return path, tm


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("building chandbali ...", flush=True)
    chand, chand_gems, ci = build_chandbali()
    print("building top motif ...", flush=True)
    top, top_gems, ti = build_top_motif()
    print("building barrel ...", flush=True)
    barrel, barrel_gems, bi = build_barrel(P["barrel_d"], P["barrel_len"], P["collar_len"])
    print("building drop ...", flush=True)
    drop, drop_gems, pearl, di = build_drop()
    print("building chain tube ...", flush=True)
    tube, tube_gems, _ = build_barrel(P["chain_tube_d"], P["chain_tube_len"], 1.3, both_collars=False)

    zc = P["lug_t"] / 2          # lug plane of the flat parts
    gap, lr = P["link_gap"], P["lug_r"] - 0.45
    Rb = bi["outer_r"]
    # place barrel above chandbali: chandbali lug at ci['lug_y'] (local)
    bottom_lug_y_local = -(Rb + lr)        # relative to barrel centre
    top_lug_y_local = (Rb + lr)
    hole_d = max(gap - 0.7, 2 * P["lug_r"] + 0.5)  # lug hole-centre distance = jump ring diameter
    barrel_y = ci["lug_y"] + hole_d - bottom_lug_y_local
    top_dy = (barrel_y + top_lug_y_local + hole_d) - ti["lug_pts"][0][1]

    def barrel_lugs():
        pts = [(sx * ci["lug_x"], bottom_lug_y_local) for sx in (-1, 1)] + \
              [(ti["lug_pts"][1][0] * sx, top_lug_y_local) for sx in (-1, 1)] + [(0.0, bottom_lug_y_local)]
        add = union([lug(x, y, 0) for x, y in pts])
        hole = union([lug_hole_cut(x, y, 0) for x, y in pts])
        return add, hole, pts

    add, hole, lug_pts = barrel_lugs()
    barrel = (union([barrel, add]) - hole).translate((0, barrel_y, zc))
    barrel_gems = barrel_gems.translate((0, barrel_y, zc))
    top = top.translate((0, top_dy, 0))
    top_gems = top_gems.translate((0, top_dy, 0))

    drop_dy = barrel_y + bottom_lug_y_local - hole_d - di["top_lug_y"]
    drop_t = (0, drop_dy, zc - di["z"])
    drop = drop.translate(drop_t)
    drop_gems = drop_gems.translate(drop_t)
    pearl = pearl.translate(drop_t)

    rings = []
    for sx in (-1, 1):
        rings.append(jump_ring(sx * ci["lug_x"], ci["lug_y"], ci["lug_y"] + hole_d, zc))
        ya = barrel_y + top_lug_y_local
        rings.append(jump_ring(sx * ti["lug_pts"][1][0], ya, ya + hole_d, zc))
    rings.append(jump_ring(0, barrel_y + bottom_lug_y_local - hole_d, barrel_y + bottom_lug_y_local, zc))
    rings = union(rings)

    # green beads + collar beads (reference only)
    L = P["barrel_len"]
    beads = union([Manifold.sphere(1, 64).scale((2.6, 3.8, 3.8)).translate((sx * (L / 2 + 2.6), barrel_y, zc)) for sx in (-1, 1)])

    parts = {
        "01_chandbali.stl": chand,
        "02_top_motif.stl": top,
        "03_barrel.stl": barrel,
        "04_drop_cluster_cap.stl": drop,
        "05_jump_rings_x5.stl": rings,
        "06_chain_tube_x1.stl": tube,
    }
    report = {"params": P, "parts": {}, "stones": {}}
    total_vol = 0.0
    qty = {"06_chain_tube_x1.stl": 2}
    for name, m in parts.items():
        export(m, name)
        vol = m.volume() / 1000.0  # cm3
        q = qty.get(name, 1)
        report["parts"][name] = {"qty": q, "volume_cm3": round(vol, 4), "manifold_ok": m.status().name,
                                 "weights_g": {k: round(vol * q * d, 2) for k, d in DENSITY.items()},
                                 "bbox_mm": [round(x, 2) for x in m.bounding_box()]}
        total_vol += vol * q
    report["total_volume_cm3"] = round(total_vol, 4)
    report["total_weights_g"] = {k: round(total_vol * d, 2) for k, d in DENSITY.items()}
    report["stones"] = {
        "polki_chandbali": ci["polki"], "polki_top_motif": ti["polki"],
        "pave_rounds_chandbali": ci["pave"], "pave_rounds_top_motif": ti["pave"],
        "pave_rounds_barrel_collars": bi["pave"], "cluster_rounds": 3,
        "emerald_cab": ci["emerald"], "drop_pearl_mm": P["drop_pearl"],
    }

    assembly = union([chand, top, barrel, drop, rings])
    export(assembly, "00_pendant_assembly_gold.stl")
    gems_all = union([chand_gems, top_gems, barrel_gems, drop_gems])
    export(gems_all, "ref_diamonds_polki.stl")
    export(pearl, "ref_pearl.stl")
    export(union([beads, ci["emerald_body"]]), "ref_green_beads_emerald.stl")
    bb = assembly.bounding_box()
    report["assembly_size_mm"] = {"width": round(bb[3] - bb[0], 2), "height": round(bb[4] - bb[1], 2),
                                  "depth": round(bb[5] - bb[2], 2)}
    with open(os.path.join(OUT_DIR, "weight_report.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    print(json.dumps({k: report[k] for k in ("total_weights_g", "assembly_size_mm", "stones")}, indent=2))
    for n, r in report["parts"].items():
        print(f"{n:32s} qty {r['qty']}  {r['volume_cm3']:.3f} cm3  22K {r['weights_g']['22K yellow (91.6%)']:.2f} g  {r['manifold_ok']}")


if __name__ == "__main__":
    main()
