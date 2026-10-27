"""Parametric 3D-printable silver ornamental frame.

The body is a rectangular "sweep" of one cross-section profile: every point of
the profile is (d, z), where d is the distance in from the outer edge and z the
height above the back. Insetting the outer rectangle by d gives mitered corners
for free. Two rows of pearls run round the frame in channels either side of a
flat ornament field, as in ref/corner_band.webp.

Ornaments are flat-backed reliefs made from the close-up references (ornament.py):
  - acanthus scroll, traced from ref/corner_band.webp
  - corner rosette, modelled directly after the same reference (cleaner than tracing)
  - top/bottom centre panel, from ref/top_center.webp
Each corner gets a rosette and a scroll running along each rail towards the
centre; the top and bottom rails carry the centre panel over the halves' seam.

Usage:
    python frame.py                      # 15 x 7.5 in outer, 1 in border
    python frame.py --width-in 20        # 20 x 10 in outer (height = width / 2)
"""

import argparse
import json
import math
import zipfile
from pathlib import Path

import manifold3d as m3d
import numpy as np

from ornament import band_pieces, heightfield_solid, relief, rosette_height

IN = 25.4  # mm per inch
HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------- profile

def arc(cx, cz, r, a0, a1, n=14):
    """Points on a circular arc, angles in degrees, endpoints included."""
    ts = np.radians(np.linspace(a0, a1, n + 1))
    return [(cx + r * math.cos(t), cz + r * math.sin(t)) for t in ts]


def half_round(d0, d1, z, n=14):
    """Half-round bead from d0 to d1 sitting on height z (the point at d0 is left out)."""
    r = (d1 - d0) / 2
    return arc(d0 + r, z, r, 180, 0, n)[1:]


def profile(p):
    """Closed cross-section polygon (d, z), counter-clockwise in the d-z plane.

    Front, outer to inner: outer rim, pearl channel, fillet, flat ornament field,
    fillet, pearl channel, inner rim, sight edge. Back: rebate for glass / picture / backer.
    """
    zf, zr, zc = p["field_z"], p["rim_z"], p["channel_z"]
    o_rim, o_ch, o_fil, i_fil, i_ch, i_rim = p["bands"]
    pts = [(0.0, 0.0), (0.0, zr)]
    pts += half_round(0.0, o_rim, zr)
    pts += [(o_rim, zc), (o_ch, zc), (o_ch, zr)]
    pts += half_round(o_ch, o_fil, zr, 8)
    pts += [(o_fil, zf), (i_fil, zf), (i_fil, zr)]
    pts += half_round(i_fil, i_ch, zr, 8)
    pts += [(i_ch, zc), (i_rim, zc), (i_rim, zr)]
    pts += half_round(i_rim, p["border"], zr)
    # sight edge down to the rebate
    pts.append((p["border"], p["rebate_depth"]))
    pts.append((p["border"] - p["rebate_width"], p["rebate_depth"]))
    pts.append((p["border"] - p["rebate_width"], 0.0))
    return pts


def field_band(p):
    """(start, end) of the flat ornament field, mm in from the outer edge."""
    return p["bands"][2], p["bands"][3]


# ---------------------------------------------------------------- sweep

def ring(W, H, d, z):
    """Outer rectangle inset by d, at height z (4 corners, CCW seen from front)."""
    return [(d, d, z), (W - d, d, z), (W - d, H - d, z), (d, H - d, z)]


def sweep(W, H, prof):
    """Mesh the frame by sweeping the closed (d, z) profile round the rectangle."""
    verts, tris = [], []
    n = len(prof)
    for d, z in prof:
        verts += ring(W, H, d, z)
    for i in range(n):
        a, b = 4 * i, 4 * ((i + 1) % n)
        for k in range(4):
            k2 = (k + 1) % 4
            tris.append((a + k, b + k2, a + k2))
            tris.append((a + k, b + k, b + k2))
    tris = np.array(tris, np.uint32)
    for t in (tris, tris[:, ::-1].copy()):
        solid = m3d.Manifold(m3d.Mesh(vert_properties=np.array(verts, np.float32), tri_verts=t))
        if solid.volume() > 0:
            break
    assert solid.status() == m3d.Error.NoError, solid.status()
    return solid


def pearls(W, H, d, z, r, pitch):
    """Spheres round the rectangle inset by d, one on each corner, evenly spaced per side."""
    corners = [(d, d), (W - d, d), (W - d, H - d), (d, H - d)]
    ball = m3d.Manifold.sphere(r, 12)
    balls = []
    for (x0, y0), (x1, y1) in zip(corners, corners[1:] + corners[:1]):
        n = max(1, round(math.hypot(x1 - x0, y1 - y0) / pitch))
        for i in range(n):
            t = i / n
            balls.append(ball.translate((x0 + t * (x1 - x0), y0 + t * (y1 - y0), z)))
    return m3d.Manifold.compose(balls)


# ---------------------------------------------------------------- features

def keyhole(x, y, p):
    """Undercut keyhole cut up from the back: entry hole centred at (x, y), slot running +y
    (towards the top edge) so the frame drops down onto the screw head."""
    head, neck, length = p["key_head"], p["key_neck"], p["key_len"]
    t1, t2 = p["key_neck_depth"], p["key_depth"]
    cyl = lambda r, h: m3d.Manifold.cylinder(h, r, r, 48)
    # z 0..t1: round head entry + narrow neck slot
    entry = cyl(head / 2, t1) + m3d.Manifold.cube((neck, length, t1)).translate((-neck / 2, 0, 0))
    # t1..t2: undercut channel the screw head slides along
    under = (cyl(head / 2, t2 - t1)
             + m3d.Manifold.cube((head, length, t2 - t1)).translate((-head / 2, 0, 0))
             + cyl(head / 2, t2 - t1).translate((0, length, 0))).translate((0, 0, t1))
    return (entry + under).translate((x, y, -0.01))


def pin_holes(x, p, H):
    """Horizontal alignment-pin holes along x, through the top and bottom rails at the seam."""
    r, L = p["pin_d"] / 2, 2 * p["pin_depth"]
    holes = m3d.Manifold()
    for d in p["pin_ds"]:
        for y in (d, H - d):
            c = m3d.Manifold.cylinder(L, r, r, 24).rotate((0, 90, 0))
            holes += c.translate((x - L / 2, y, p["pin_z"]))
    return holes


# ---------------------------------------------------------------- ornaments

def placements(W, H):
    """Corner-band transforms: band coords (x = along the rail from the corner, y = -inward)
    to world, for each corner and each rail leaving it. Returns {name: (2x2, offset)}."""
    return {
        # top and bottom rails, running from each corner towards the centre
        "top_left":     ([[1, 0], [0, 1]], (0, H)),
        "top_right":    ([[-1, 0], [0, 1]], (W, H)),
        "bottom_left":  ([[1, 0], [0, -1]], (0, 0)),
        "bottom_right": ([[-1, 0], [0, -1]], (W, 0)),
        # side rails, running from each corner towards the middle of the rail
        "left_down":    ([[0, -1], [-1, 0]], (0, H)),
        "left_up":      ([[0, -1], [1, 0]], (0, 0)),
        "right_down":   ([[0, 1], [-1, 0]], (W, H)),
        "right_up":     ([[0, 1], [1, 0]], (W, 0)),
    }


def place(solid, M, off, z):
    m = np.array(M, float)
    T = [[m[0, 0], m[0, 1], 0, off[0]], [m[1, 0], m[1, 1], 0, off[1]], [0, 0, 1, z]]
    return solid.transform(T)


def ornaments(p):
    """Build the ornament parts and where they go.

    Returns (parts, placed): parts = {name: (solid, copies)} for printing separately,
    placed = list of world-space solids for the assembled frame.
    """
    W, H = p["width"], p["height"]
    z = p["field_z"] - 0.05  # sink slightly so the union fuses
    f0, f1 = field_band(p)
    band = dict(border=p["border"], **p["corner_band"])
    pcs, _ = band_pieces(HERE / p["corner_image"], band, {
        "scroll": dict(u=(f1, p["scroll_end"]), v=(f0, f1)),
    }, p["orn_relief"], p["orn_base"])
    scroll = pcs["scroll"]
    h, px = rosette_height(f1 - f0 - 0.6, p["orn_relief"])
    rosette = heightfield_solid(h, px, ((h.shape[1] - 1) / 2, (h.shape[0] - 1) / 2), p["orn_base"], res=0.05)
    centre, _ = relief(HERE / p["orn_image"], f1 - f0 - 0.6, p["orn_relief"], p["orn_base"])

    placed = []
    hands = {}
    for name, (M, off) in placements(W, H).items():
        hand = "A" if np.linalg.det(M) > 0 else "B"
        placed.append(place(scroll, M, off, z))
        hands[hand] = hands.get(hand, 0) + 1
    c = (f0 + f1) / 2  # rosettes sit in the corner squares of the field (symmetric, no handedness)
    for x, y in ((c, c), (W - c, c), (c, H - c), (W - c, H - c)):
        placed.append(rosette.translate((x, y, z)))
    placed.append(centre.translate((W / 2, H - c, z)))
    placed.append(centre.rotate((0, 0, 180)).translate((W / 2, c, z)))

    parts = {"ornament_center": (centre, 2), "ornament_rosette": (rosette, 4)}
    for hand, n in sorted(hands.items()):
        parts[f"ornament_scroll_{hand}"] = (scroll if hand == "A" else scroll.mirror((1, 0, 0)), n)
    return parts, placed


# ---------------------------------------------------------------- output

def to_stl(solid, path):
    mesh = solid.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    t = np.asarray(mesh.tri_verts)
    tri = v[t]
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(t), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = nrm, tri
    with open(path, "wb") as f:
        f.write(b"silver-frame".ljust(80, b" "))
        f.write(np.uint32(len(t)).tobytes())
        f.write(rec.tobytes())
    return len(t)


def to_3mf(solid, path):
    """Compressed 3MF (much smaller than STL for the dense assembled mesh)."""
    mesh = solid.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    t = np.asarray(mesh.tri_verts)
    vs = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in v)
    ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in t)
    model = ('<?xml version="1.0" encoding="UTF-8"?>'
             '<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources><object id="1" type="model"><mesh><vertices>{vs}</vertices>'
             f'<triangles>{ts}</triangles></mesh></object></resources>'
             '<build><item objectid="1"/></build></model>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/'
                   'package/2006/content-types"><Default Extension="rels" ContentType="application/'
                   'vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" '
                   'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/'
                   'package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" '
                   'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", model)
    return len(t)


def split_halves(solid, p):
    """Two halves at x = W/2 with alignment-pin holes across the seam."""
    W, H = p["width"], p["height"]
    s = solid - pin_holes(W / 2, p, H)
    left = s.trim_by_plane((-1, 0, 0), -W / 2)
    right = s.trim_by_plane((1, 0, 0), W / 2).translate((-W / 2, 0, 0))
    return left, right


def build(p):
    W, H = p["width"], p["height"]
    body = sweep(W, H, profile(p))
    pr, pz = p["pearl_r"], p["channel_z"] + p["pearl_r"] - p["pearl_sink"]
    o_rim, o_ch, _, _, i_ch, i_rim = p["bands"]
    body += pearls(W, H, (o_rim + o_ch) / 2, pz, pr, p["pearl_pitch"])
    body += pearls(W, H, (i_ch + i_rim) / 2, pz, pr, p["pearl_pitch"])
    # keyholes in the back of the top rail (y = H is the top edge)
    for fx in p["key_xs"]:
        body -= keyhole(W * fx, H - p["key_from_top"], p)

    parts, placed = ornaments(p)
    assembled = m3d.Manifold.batch_boolean([body] + placed, m3d.OpType.Add)
    left, right = split_halves(body, p)
    a_left, a_right = split_halves(assembled, p)
    stl = dict(frame_left=(left, 1), frame_right=(right, 1),
               frame_assembled_left=(a_left, 1), frame_assembled_right=(a_right, 1), **parts)
    return stl, assembled


def default_params(width_in=15.0, border_in=1.0):
    W = width_in * IN
    B = border_in * IN
    k = B / IN  # band layout measured from ref/corner_band.webp at a 1 in border
    return dict(
        width=W, height=W / 2, border=B,
        # ends of: outer rim | pearl channel | fillet | field | fillet | pearl channel (then inner rim)
        bands=tuple(round(x * k, 3) for x in (1.8, 3.8, 4.7, 20.8, 21.7, 23.7)),
        field_z=12.0, rim_z=12.8, channel_z=12.4,
        pearl_r=0.72, pearl_pitch=1.7, pearl_sink=0.3,
        rebate_width=6.35, rebate_depth=6.0,
        key_head=8.0, key_neck=4.0, key_len=7.0,
        key_neck_depth=3.0, key_depth=6.5, key_from_top=13.5, key_xs=(0.25, 0.75),
        pin_d=2.0, pin_depth=8.0, pin_ds=(6.5, 14.0), pin_z=6.5,
        orn_relief=2.6, orn_base=0.8,
        orn_image="ref/top_center.webp",
        corner_image="ref/corner_band.webp",
        # pixel positions of the band's outer edge, inner edge and corner in corner_band.webp
        corner_band=dict(outer_row=340, inner_row=728, corner_col=14),
        scroll_end=92.7 * k,  # mm along the rail where the scroll ends in the reference
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width-in", type=float, default=15.0, help="outer width, inches (height = width / 2)")
    ap.add_argument("--border-in", type=float, default=1.0, help="frame border width, inches")
    ap.add_argument("--out", default=str(HERE / "out"))
    a = ap.parse_args()

    p = default_params(a.width_in, a.border_in)
    if 2 * p["scroll_end"] > p["height"]:
        print("warning: side-rail scrolls overlap at this size")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stl, assembled = build(p)
    report = {"params_mm": {k: (list(v) if isinstance(v, tuple) else v if isinstance(v, (str, dict))
                                else round(v, 3)) for k, v in p.items()}, "parts": {}}
    for name, (s, copies) in stl.items():
        lo, hi = s.bounding_box()[:3], s.bounding_box()[3:]
        dense = name.startswith("frame_assembled")  # millions of triangles: compressed 3MF
        n = (to_3mf if dense else to_stl)(s, out / f"{name}.{'3mf' if dense else 'stl'}")
        report["parts"][name] = dict(print_copies=copies, triangles=n, volume_cm3=round(s.volume() / 1000, 2),
                                     size_mm=[round(h - l, 2) for l, h in zip(lo, hi)])
        print(name, report["parts"][name])
    to_stl(assembled, out / "_render_assembled.stl")  # for render/shoot.mjs, not committed
    n = to_3mf(assembled, out / "frame_assembled.3mf")
    report["parts"]["frame_assembled.3mf"] = dict(triangles=n, genus=assembled.genus())
    print("frame_assembled.3mf", n, "genus", assembled.genus())
    (out / "report.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
