"""Shared STL export used by every generator in this folder.

Boolean operations can leave vertices ~1e-7 mm apart.  STL stores float32, so
on save such vertices fuse and leave non-manifold edges that Matrix/Rhino flag.
Here we weld vertices closer than WELD (far below casting resolution), drop
the triangles that collapse, remove zero-volume debris, then verify that the
mesh is closed and manifold *in float32* before writing.
"""
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

WELD = 1e-5  # mm


def _labels(n, pairs):
    g = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(n, n))
    return connected_components(g, directed=False)[1]


def clean_mesh(vertices, faces, min_volume=1e-3):
    v = np.asarray(vertices, dtype=np.float64)
    f = np.asarray(faces, dtype=np.int64)
    lab = _labels(len(v), cKDTree(v).query_pairs(WELD, output_type="ndarray"))
    f = lab[f]
    f = f[(f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])]
    # a face listed twice (either winding) is a zero-thickness double layer
    _, first, cnt = np.unique(np.sort(f, axis=1), axis=0, return_index=True, return_counts=True)
    f = f[np.sort(first[cnt == 1])]
    vv = np.zeros((lab.max() + 1, 3))
    vv[lab] = v
    tm = trimesh.Trimesh(vv, f, process=False)
    tm.remove_unreferenced_vertices()
    # drop disconnected zero-volume debris
    adj = tm.face_adjacency
    comp = _labels(len(tm.faces), adj)
    keep = [idx for idx in (np.where(comp == c)[0] for c in np.unique(comp))
            if len(idx) >= 4 and abs(tm.submesh([idx], append=True).volume) >= min_volume]
    tm.update_faces(np.concatenate(keep))
    tm.remove_unreferenced_vertices()
    return tm


def check(tm):
    """Edge check on the float32 positions an STL reader will see."""
    t32 = trimesh.Trimesh(np.asarray(tm.vertices, dtype=np.float32), tm.faces, process=True)
    _, cnt = np.unique(np.sort(t32.edges, axis=1), axis=0, return_counts=True)
    return {"open_edges": int((cnt == 1).sum()), "nonmanifold_edges": int((cnt > 2).sum()),
            "watertight": bool(t32.is_watertight)}


def export_clean(vertices, faces, path):
    tm = clean_mesh(vertices, faces)
    res = check(tm)
    if res["open_edges"] or res["nonmanifold_edges"]:
        raise RuntimeError(f"{path}: mesh defects after cleaning {res}")
    tm.export(path)
    return tm, res
