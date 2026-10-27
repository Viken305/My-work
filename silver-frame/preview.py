"""Plot the frame cross-section to out/profile.png. 3D renders come from render/shoot.mjs."""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frame import default_params, field_band, profile  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"


def main():
    p = default_params()
    pr = np.array(profile(p) + [profile(p)[0]])
    f0, f1 = field_band(p)
    fig, ax = plt.subplots(figsize=(9, 5), dpi=130)
    ax.fill(pr[:, 0], pr[:, 1], color="#c9ccd1", ec="#333", lw=1)
    ax.axvspan(f0, f1, color="#f2c14e", alpha=0.18)
    ax.text((f0 + f1) / 2, p["field_z"] + 1.2,
            f"ornament field {f1 - f0:.1f} mm\n(ornaments glue on here)", ha="center", fontsize=8)
    B, rw, rd = p["border"], p["rebate_width"], p["rebate_depth"]
    ax.text(B - rw / 2, rd / 2, f"rebate\n{rw} x {rd}", ha="center", va="center", fontsize=8)
    ax.set_aspect("equal"); ax.set_xlim(-1, B + 1.5); ax.set_ylim(-1, 19)
    ax.set_xlabel(f"mm in from outer edge  (outer edge 0  ->  sight edge {B:.1f})")
    ax.set_ylabel("height mm")
    ax.set_title("Frame cross-section", fontsize=10)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "profile.png")
    print(OUT / "profile.png")


if __name__ == "__main__":
    main()
