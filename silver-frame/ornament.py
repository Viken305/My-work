"""Turn a straight-on photo/render of a carved ornament into a printable relief solid.

The silhouette comes from the white background. The height map combines:
  - a rounded "body" from the distance to the silhouette edge, so every lobe is domed,
  - the image's own light/dark pattern (bright = raised, dark outlines = grooves),
which is how a carver reads a metal-render reference. It is an approximation of
the real depth, good enough for a 2-3 mm relief.
"""

import numpy as np
import manifold3d as m3d
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure


def load(path):
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(float) / 255
    return rgb @ [0.299, 0.587, 0.114]


def silhouette(L, white=0.93):
    """Foreground = everything not connected to the image border through near-white pixels."""
    lab, _ = ndi.label(L > white)
    edge = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    fg = ~np.isin(lab, edge[edge > 0])
    fg = ndi.binary_opening(fg, iterations=2)
    return ndi.binary_fill_holes(fg)


def height_map(L, fg, px_mm, relief):
    """Relief height in mm above the base, per pixel (0 outside the silhouette)."""
    s = 0.1 / px_mm  # pixels per 0.1 mm
    # rounded body: rises over ~1.2 mm from the silhouette edge
    dist = ndi.distance_transform_edt(fg) * px_mm
    body = np.sqrt(np.clip(dist / 1.2, 0, 1))
    # image detail: smoothed brightness, normalised to the ornament's own range
    Ls = ndi.gaussian_filter(L, 1.8 * s)
    lo, hi = np.percentile(Ls[fg], [3, 97])
    detail = np.clip((Ls - lo) / (hi - lo), 0, 1)
    # the dark outlines between leaves become V-grooves that separate the elements
    groove = ndi.gaussian_filter(np.clip((0.30 - ndi.gaussian_filter(L, 1.0 * s)) / 0.2, 0, 1), 0.8 * s)
    # broad shading (large blur) lifts big masses like the central flower a little
    broad = ndi.gaussian_filter(np.where(fg, detail, 0), 12 * s)
    broad /= max(broad[fg].max(), 1e-6)
    h = (0.45 + 0.35 * detail + 0.20 * broad - 0.30 * groove) * body
    h = ndi.gaussian_filter(np.clip(h, 0, None), 0.6 * s)
    h[~fg] = 0
    return h / h[fg].max() * relief


def outline_polygons(fg, px_mm, tol_px=0.6):
    """Silhouette outline as polygons in mm (x right, y up), origin at the ornament centre."""
    ys, xs = np.nonzero(fg)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    padded = np.pad(ndi.gaussian_filter(fg.astype(float), 1.0), 1)
    polys = []
    for c in measure.find_contours(padded, 0.5):
        c = measure.approximate_polygon(c, tol_px) - 1  # (row, col) back to unpadded
        if len(c) < 4:
            continue
        polys.append(np.c_[(c[:, 1] - cx) * px_mm, (cy - c[:, 0]) * px_mm])
    return polys, (cx, cy)


def heightfield_block(h, centre, px_mm, base, res=0.1):
    """Closed solid: flat bottom at z=0, top at base + h, over the ornament's bounding box."""
    ys, xs = np.nonzero(h > 0)
    cx, cy = centre
    x0, x1 = (xs.min() - 2 - cx) * px_mm, (xs.max() + 2 - cx) * px_mm
    y0, y1 = (cy - ys.max() - 2) * px_mm, (cy - ys.min() + 2) * px_mm
    gx = np.arange(x0, x1 + res, res)
    gy = np.arange(y0, y1 + res, res)
    X, Y = np.meshgrid(gx, gy)
    rows, cols = cy - Y / px_mm, cx + X / px_mm
    Z = base + ndi.map_coordinates(h, [rows, cols], order=1, mode="constant")
    ny, nx = Z.shape
    top = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
    bot = np.c_[X.ravel(), Y.ravel(), np.zeros(Z.size)]
    verts = np.r_[top, bot]
    idx = np.arange(nx * ny).reshape(ny, nx)
    a, b, c, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]
    quads = np.stack([a, b, c, d], -1).reshape(-1, 4)
    off = nx * ny
    tris = [quads[:, [0, 1, 2]], quads[:, [0, 2, 3]],                 # top (+z)
            quads[:, [0, 2, 1]] + off, quads[:, [0, 3, 2]] + off]     # bottom (-z)
    # side walls along the boundary ring
    ring = np.r_[idx[0, :], idx[1:, -1], idx[-1, -2::-1], idx[-2:0:-1, 0]]
    r2 = np.roll(ring, -1)
    tris += [np.c_[ring, r2 + off, r2], np.c_[ring, ring + off, r2 + off]]
    tris = np.vstack(tris)
    solid = m3d.Manifold(m3d.Mesh(vert_properties=verts.astype(np.float32),
                                  tri_verts=tris.astype(np.uint32)))
    if solid.volume() <= 0:
        solid = m3d.Manifold(m3d.Mesh(vert_properties=verts.astype(np.float32),
                                      tri_verts=tris[:, ::-1].astype(np.uint32).copy()))
    assert solid.status() == m3d.Error.NoError, solid.status()
    return solid


def relief(path, height_mm, relief_mm, base_mm, res=0.1):
    """Flat-backed relief solid, ornament height (image vertical) = height_mm.

    Origin: centre of the ornament's bounding box, back face at z=0, image-up = +y.
    Returns (solid, width_mm).
    """
    L = load(path)
    fg = silhouette(L)
    ys, xs = np.nonzero(fg)
    px_mm = height_mm / (ys.max() - ys.min())
    h = height_map(L, fg, px_mm, relief_mm)
    polys, centre = outline_polygons(fg, px_mm)
    block = heightfield_block(h, centre, px_mm, base_mm, res)
    cut = m3d.Manifold.extrude(m3d.CrossSection(polys, m3d.FillRule.EvenOdd),
                               base_mm + relief_mm + 1).translate((0, 0, -0.5))
    solid = block ^ cut
    return solid, (xs.max() - xs.min()) * px_mm
