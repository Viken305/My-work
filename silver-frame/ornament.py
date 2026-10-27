"""Turn a straight-on photo/render of a carved ornament into a printable relief solid.

The outline comes from the background: plain white for a cut-out ornament, or the
smooth brushed field for carving shown in place on the frame band. The height map
combines:
  - a rounded "body" from the distance to the outline, so every lobe is domed,
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


def keep_large(m, min_px):
    lab, n = ndi.label(m)
    if n == 0:
        return m
    sz = ndi.sum(m, lab, np.arange(1, n + 1))
    return np.isin(lab, 1 + np.nonzero(sz >= min_px)[0])


def silhouette(L, white=0.93):
    """Foreground = everything not connected to the image border through near-white pixels."""
    lab, _ = ndi.label(L > white)
    edge = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    fg = ~np.isin(lab, edge[edge > 0])
    fg = ndi.binary_opening(fg, iterations=2)
    return ndi.binary_fill_holes(fg)


def field_mask(S, smooth=0.032, close=0):
    """Carving vs plain field on a band crop: the field is smooth at fine scale.

    Smooth patches of 100+ px are field (including gaps between leaves);
    `close` > 0 additionally rounds the outline into one solid shape.
    """
    G = ndi.gaussian_filter(ndi.gaussian_gradient_magnitude(S, 1.0), 2.0)
    bg = keep_large(ndi.binary_opening(G < smooth, iterations=2), 100)
    fg = ~bg
    if close:
        fg = ndi.binary_fill_holes(ndi.binary_closing(fg, iterations=close))
    else:  # fill only pinholes (smooth highlights on leaves), keep real gaps open
        fg |= ~keep_large(~fg, 200)
    # keep off the crop border so the relief has a clean edge all round
    m = 5
    fg[:m], fg[-m:], fg[:, :2], fg[:, -2:] = False, False, False, False
    fg = ndi.binary_opening(fg, iterations=3)  # drops thin slivers (e.g. rim edges)
    return keep_large(fg, 300)


def ornamentness(S, lo=0.012, hi=0.035):
    """0 on smooth field-like areas, 1 on busy carved detail."""
    G = ndi.gaussian_filter(ndi.gaussian_gradient_magnitude(S, 1.0), 2.0)
    return ndi.gaussian_filter(np.clip((G - lo) / (hi - lo), 0, 1), 3)


def height_map(L, fg, px_mm, relief, soft=None):
    """Relief height in mm above the base, per pixel (0 outside the outline)."""
    s = 0.1 / px_mm  # pixels per 0.1 mm
    # rounded body: rises over ~1.2 mm from the outline
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
    if soft is not None:  # sink smooth field-like patches that stayed inside the outline
        h *= 0.35 + 0.65 * soft
    h = ndi.gaussian_filter(np.clip(h, 0, None), 0.6 * s)
    h[~fg] = 0
    return h / h[fg].max() * relief


def outline_polygons(fg, px_mm, origin, tol_px=0.6):
    """Outline as polygons in mm (x right, y up); pixel `origin` (col, row) maps to (0, 0)."""
    ox, oy = origin
    padded = np.pad(ndi.gaussian_filter(fg.astype(float), 1.0), 1)
    polys = []
    for c in measure.find_contours(padded, 0.5):
        c = measure.approximate_polygon(c, tol_px) - 1  # (row, col) back to unpadded
        if len(c) < 4:
            continue
        polys.append(np.c_[(c[:, 1] - ox) * px_mm, (oy - c[:, 0]) * px_mm])
    return polys


def heightfield_block(h, origin, px_mm, base, res=0.1):
    """Closed solid: flat bottom at z=0, top at base + h, over the relief's bounding box."""
    ys, xs = np.nonzero(h > 0)
    ox, oy = origin
    x0, x1 = (xs.min() - 2 - ox) * px_mm, (xs.max() + 2 - ox) * px_mm
    y0, y1 = (oy - ys.max() - 2) * px_mm, (oy - ys.min() + 2) * px_mm
    gx = np.arange(x0, x1 + res, res)
    gy = np.arange(y0, y1 + res, res)
    X, Y = np.meshgrid(gx, gy)
    rows, cols = oy - Y / px_mm, ox + X / px_mm
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


def relief_solid(L, fg, px_mm, origin, relief_mm, base_mm, res=0.1, soft=None):
    """Flat-backed relief of L inside mask fg. Back face at z=0, image-up = +y."""
    h = height_map(L, fg, px_mm, relief_mm, soft)
    block = heightfield_block(h, origin, px_mm, base_mm, res)
    cut = m3d.Manifold.extrude(
        m3d.CrossSection(outline_polygons(fg, px_mm, origin), m3d.FillRule.EvenOdd),
        base_mm + relief_mm + 1).translate((0, 0, -0.5))
    return block ^ cut


def relief(path, height_mm, relief_mm, base_mm, res=0.1):
    """Cut-out ornament on a white background, scaled so its height is height_mm.

    Origin: centre of the ornament's bounding box. Returns (solid, width_mm).
    """
    L = load(path)
    fg = silhouette(L)
    ys, xs = np.nonzero(fg)
    px_mm = height_mm / (ys.max() - ys.min())
    origin = ((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2)
    return relief_solid(L, fg, px_mm, origin, relief_mm, base_mm, res), (xs.max() - xs.min()) * px_mm


def band_pieces(path, band, pieces, relief_mm, base_mm, res=0.1):
    """Ornaments shown in place on a straight band photo (corner at the left, outer edge up).

    band: dict(outer_row, inner_row, corner_col) pixel positions of the band's outer edge,
          inner (sight) edge and the corner's outer edge; the band is the frame border wide.
    pieces: {name: dict(u=(u0, u1), v=(v0, v1), close=int)} crop windows in mm, where
            u runs along the rail from the corner's outer edge and v inward from the outer edge.
    Returns ({name: solid}, px_mm). Each solid is in band coordinates: x = u, y = -v.
    """
    L = load(path)
    px_mm = band["border"] / (band["inner_row"] - band["outer_row"])
    origin = (band["corner_col"], band["outer_row"])
    out = {}
    for name, pc in pieces.items():
        c0, c1 = (int(round(origin[0] + u / px_mm)) for u in pc["u"])
        r0, r1 = (int(round(origin[1] + v / px_mm)) for v in pc["v"])
        fg = np.zeros(L.shape, bool)
        fg[r0:r1, c0:c1] = field_mask(L[r0:r1, c0:c1], close=pc.get("close", 0))
        soft = None if pc.get("close") else ornamentness(L)
        out[name] = relief_solid(L, fg, px_mm, origin, relief_mm, base_mm, res, soft)
    return out, px_mm


def heightfield_solid(h, px_mm, origin, base_mm, res=0.1):
    """Flat-backed relief from a ready-made height map h (mm; 0 = no material)."""
    fg = h > 0
    block = heightfield_block(h, origin, px_mm, base_mm, res)
    cut = m3d.Manifold.extrude(
        m3d.CrossSection(outline_polygons(fg, px_mm, origin), m3d.FillRule.EvenOdd),
        base_mm + h.max() + 1).translate((0, 0, -0.5))
    return block ^ cut


def rosette_height(size, relief, px=0.04):
    """Four-petal rosette as in the corner reference, modelled directly (not traced).

    Petals point to the corners of a size x size square, small leaves point to the
    edge midpoints, and a domed boss with a ring sits in the middle.
    Returns (h, px) with h in mm on a square pixel grid centred on the rosette.
    """
    n = int(round(size / px))
    c = (np.arange(n) - (n - 1) / 2) * px
    X, Y = np.meshgrid(c, -c)
    r = np.hypot(X, Y)
    th = np.arctan2(Y, X)

    def leaf(axis, length, width, height, serr):
        a = np.angle(np.exp(1j * (th - axis)))           # angle from the leaf axis
        along, lat = r * np.cos(a), r * np.sin(a)
        t = np.clip(along / length, 0, 1)
        w = width * np.sin(np.pi * t ** 0.75) ** 0.8      # broad middle, pointed tip
        w *= 1 + serr * np.sin(along * 2 * np.pi / 2.0) * t  # lobed edge, stronger to the tip
        u = np.abs(lat) / np.maximum(w, 1e-6)             # 0 on the midrib, 1 at the edge
        inside = (along > 0) & (u < 1) & (t < 1)
        hp = height * (0.55 + 0.45 * np.sin(np.pi * np.clip(t * 1.1, 0, 1)))
        h = hp * np.sqrt(np.clip(1 - u ** 2, 0, 1)) * (1 - 0.25 * t)  # domed, thinning to the tip
        h -= 0.18 * height * np.exp(-(lat / 0.22) ** 2) * (t > 0.2)            # midrib groove
        vein = np.abs(np.sin((along - 0.9 * np.abs(lat)) * 2 * np.pi / 1.25))  # angled side veins
        h -= 0.05 * height * np.clip(1 - vein / 0.2, 0, 1) * (u > 0.25) * (u < 0.85) * (t > 0.3)
        return np.where(inside, np.clip(h, 0.05, None), 0)

    R = size / 2 * 1.3
    h = np.zeros_like(r)
    for k in range(4):
        h = np.maximum(h, leaf(np.pi / 2 * k, 0.66 * R, 1.1, 0.5 * relief, 0.15))       # small leaves
    for k in range(4):
        h = np.maximum(h, leaf(np.pi / 4 + np.pi / 2 * k, R, 2.5, 0.8 * relief, 0.14))  # petals
    # boss with a ring round it
    ring = 0.82 * relief * np.exp(-((r - 2.15) / 0.28) ** 2)
    boss = relief * np.sqrt(np.clip(1 - (r / 1.65) ** 2, 0, 1))
    h = np.where(r < 2.6, np.maximum(np.maximum(boss, ring), 0.45 * relief * (r > 1.65)), h)
    h[(np.abs(X) > size / 2) | (np.abs(Y) > size / 2)] = 0
    return ndi.gaussian_filter(h, 0.06 / px) * (h > 0), px
