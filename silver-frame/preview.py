"""Render quick preview images of the generated STLs (matplotlib, no GPU needed)."""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frame import IN, profile  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
LIGHT = np.array([-0.4, 0.5, 1.0]) / np.linalg.norm([-0.4, 0.5, 1.0])


def load_stl(path):
    data = path.read_bytes()
    n = np.frombuffer(data, np.uint32, 1, 80)[0]
    rec = np.frombuffer(data, dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")], count=n, offset=84)
    return rec["v"].astype(float)


def shade(tris):
    nrm = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
    lam = np.clip(nrm @ LIGHT, 0, 1)
    base = np.array([0.78, 0.79, 0.81])
    return np.clip(base[None] * (0.35 + 0.75 * lam[:, None]), 0, 1)


def view(ax, tris, elev, azim, title):
    pc = Poly3DCollection(tris, facecolors=shade(tris), edgecolors="none", linewidths=0)
    ax.add_collection3d(pc)
    lo, hi = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(hi - lo)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=10)


def main():
    full = load_stl(OUT / "frame_full.stl")
    left = load_stl(OUT / "frame_left.stl")

    fig = plt.figure(figsize=(14, 9), dpi=130, facecolor="white")
    view(fig.add_subplot(2, 2, 1, projection="3d"), full, 35, -60, "Front (3/4 view)")
    flipped = full.copy(); flipped[..., 2] *= -1; flipped[..., 1] *= -1
    view(fig.add_subplot(2, 2, 2, projection="3d"), flipped, 50, -70, "Back: rebate + 2 keyholes")
    view(fig.add_subplot(2, 2, 3, projection="3d"), left, 25, -20, "Left half: seam face with pin holes")

    ax = fig.add_subplot(2, 2, 4)
    W = 15 * IN
    p = dict(width=W, height=W / 2, border=IN, bead_z=13.0, bead_r=2.4, field_z=12.0,
             rebate_width=6.35, rebate_depth=6.0, lip=2.6)
    pr = np.array(profile(p) + [profile(p)[0]])
    ax.fill(pr[:, 0], pr[:, 1], color="#c9ccd1", ec="#333", lw=1)
    ax.axvspan(5.8, 17.4, ymin=0, ymax=1, color="#f2c14e", alpha=0.18)
    ax.text(11.6, 13.0, "ornament field\n(carving goes here)", ha="center", fontsize=8)
    ax.text(22.2, 3.0, "rebate\n6.35 x 6.0", ha="center", fontsize=8)
    ax.set_aspect("equal"); ax.set_xlim(-1, 27); ax.set_ylim(-1, 18)
    ax.set_xlabel("mm in from outer edge  (outer edge 0  ->  sight edge 25.4 = 1 in)")
    ax.set_ylabel("height mm")
    ax.set_title("Cross-section profile", fontsize=10)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUT / "preview.png")
    print(OUT / "preview.png")


if __name__ == "__main__":
    main()
