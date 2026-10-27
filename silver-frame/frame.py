"""Parametric 3D-printable frame body for the silver ornamental frame.

The frame is a rectangular "sweep" of one cross-section profile: every point of
the profile is (d, z), where d is the distance in from the outer edge and z the
height above the back. Insetting the outer rectangle by d gives mitered corners
for free, so the whole body is exact and needs only a few hundred triangles.

The carved ornaments (corner rosettes, top/bottom scroll panels, side flowers)
are not modelled yet: they sit on the flat "field" band of the profile and will
be added as relief bodies once the close-up references are ready.

Usage:
    python frame.py                      # 15 x 7.5 in outer, 1 in border
    python frame.py --width-in 20        # 20 x 10 in outer (height = width / 2)
"""

import argparse
import json
import math
from pathlib import Path

import manifold3d as m3d
import numpy as np

IN = 25.4  # mm per inch
HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------- profile

def arc(cx, cz, r, a0, a1, n=14):
    """Points on a circular arc, angles in degrees, endpoints included."""
    ts = np.radians(np.linspace(a0, a1, n + 1))
    return [(cx + r * math.cos(t), cz + r * math.sin(t)) for t in ts]


def profile(p):
    """Closed cross-section polygon (d, z), counter-clockwise in the d-z plane.

    Front, outer to inner: side wall, half-round outer bead, small cove,
    flat ornament field, inner bead, step, small bead, sloped sight edge.
    Back: rebate for glass / picture / backer.
    """
    B = p["border"]
    zb = p["bead_z"]          # outer bead centre height
    rb = p["bead_r"]
    zf = p["field_z"]         # flat field height (ornaments sit on this)
    pts = [(0.0, 0.0), (0.0, zb)]
    # outer bead: half round from the outer wall over the top
    pts += arc(rb, zb, rb, 180, 0)[1:]
    # cove down onto the field
    c = zb - zf
    pts += arc(2 * rb + c, zb, c, 180, 270)[1:]
    field_end = B - 8.0
    pts.append((field_end, zf))
    # inner bead
    pts += arc(field_end + 1.0, zf, 1.0, 180, 0)[1:]
    # step down to the inner flat
    z_step = zf - 1.2
    pts.append((field_end + 2.2, z_step))
    pts.append((field_end + 3.8, z_step))
    # small bead
    pts += arc(field_end + 4.5, z_step, 0.7, 180, 0)[1:]
    # slope down to the sight edge
    z_sight = p["rebate_depth"] + p["lip"]
    pts.append((B, z_sight))
    # rebate (back side)
    pts.append((B, p["rebate_depth"]))
    pts.append((B - p["rebate_width"], p["rebate_depth"]))
    pts.append((B - p["rebate_width"], 0.0))
    return pts


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
            # quad a+k, a+k2, b+k2, b+k
            tris.append((a + k, b + k2, a + k2))
            tris.append((a + k, b + k, b + k2))
    mesh = m3d.Mesh(vert_properties=np.array(verts, np.float32),
                    tri_verts=np.array(tris, np.uint32))
    solid = m3d.Manifold(mesh)
    if solid.volume() < 0:  # profile wound the other way
        mesh = m3d.Mesh(vert_properties=np.array(verts, np.float32),
                        tri_verts=np.array(tris, np.uint32)[:, ::-1].copy())
        solid = m3d.Manifold(mesh)
    assert solid.status() == m3d.Error.NoError, solid.status()
    return solid


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


def build(p):
    W, H = p["width"], p["height"]
    body = sweep(W, H, profile(p))
    # keyholes in the back of the top rail (y = H is the top edge)
    y_key = H - p["key_from_top"]
    for fx in p["key_xs"]:
        body -= keyhole(W * fx, y_key, p)
    full = body
    # two halves split at x = W/2, with pin holes across the seam
    halves = body - pin_holes(W / 2, p, H)
    left = halves.trim_by_plane((-1, 0, 0), -W / 2)
    right = halves.trim_by_plane((1, 0, 0), W / 2).translate((-W / 2, 0, 0))
    return full, left, right


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width-in", type=float, default=15.0, help="outer width, inches (height = width / 2)")
    ap.add_argument("--border-in", type=float, default=1.0, help="frame border width, inches")
    ap.add_argument("--out", default=str(HERE / "out"))
    a = ap.parse_args()

    W = a.width_in * IN
    p = dict(
        width=W, height=W / 2, border=a.border_in * IN,
        bead_z=13.0, bead_r=2.4, field_z=12.0,
        rebate_width=6.35, rebate_depth=6.0, lip=2.6,
        key_head=8.0, key_neck=4.0, key_len=7.0,
        key_neck_depth=3.0, key_depth=6.5, key_from_top=13.5, key_xs=(0.25, 0.75),
        pin_d=2.0, pin_depth=8.0, pin_ds=(6.5, 14.0), pin_z=6.5,
    )
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    full, left, right = build(p)
    report = {"params_mm": {k: (list(v) if isinstance(v, tuple) else round(v, 3)) for k, v in p.items()}}
    for name, s in (("frame_full", full), ("frame_left", left), ("frame_right", right)):
        lo, hi = s.bounding_box()[:3], s.bounding_box()[3:]
        n = to_stl(s, out / f"{name}.stl")
        report[name] = dict(triangles=n, volume_cm3=round(s.volume() / 1000, 2),
                            size_mm=[round(h - l, 2) for l, h in zip(lo, hi)],
                            genus=s.genus())
        print(f"{name}: {report[name]}")
    (out / "report.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
