"""Look-development stills for the props: python3 lookdev.py -> build/lookdev/*.png"""
import math
import os
import sys

import cv2
import numpy as np

import lux as L
import props as Pr
from lux import Rx, Ry, T, cat

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920

STUDIO = dict(dir=(0.55, -0.75, -0.35), col=(3.2, 2.7, 2.1), center=(0, 0, 0), extent=6.0, dist=30.0,
              env_key_dir=(-0.55, 0.75, 0.35), env_key_col=(2.6, 2.2, 1.7), env_rim_dir=(0.7, 0.3, -0.65), env_rim_col=(1.4, 1.6, 2.0),
              env_amb=(0.02, 0.018, 0.016), env_floor=(0.004, 0.003, 0.002))


def finish(img, depth, focus, dof, t=0.0, exposure=0.9, bloom=0.18):
    img = L.depth_of_field(img, depth, focus, dof)
    img = L.bloom(img, 1.6, bloom)
    img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
    img = L.tonemap(img, exposure)
    img = L.vignette(img, 0.35)
    img = L.grade(img.astype(np.float32), t)
    return (img * 255).astype(np.uint8)


def save(name, rgb):
    d = os.path.join(HERE, "build", "lookdev")
    os.makedirs(d, exist_ok=True)
    cv2.imwrite(os.path.join(d, name + ".png"), rgb[:, :, ::-1])
    print(name)


if __name__ == "__main__":
    R = L.Lux(W, H, 1.5)
    R.clear_col = (0.004, 0.003, 0.0025)
    which = sys.argv[1:] or ["kernel", "cut", "pop", "pan", "bowl", "bottle"]
    if "kernel" in which:
        k = Pr.place(Pr.kernel(0), T(0, 0.56, 0) @ Ry(-0.4))
        g = cat([Pr.slate_static(), k])
        cam = dict(eye=(1.6, 1.3, 3.2), target=(0, 0.42, 0), fov=26)
        img, d, _ = R.render(cam, dict(STUDIO, extent=3.0), g, lights=[((-2.0, 1.5, -2.5), 3.0, (1.2, 1.5, 2.2))])
        save("kernel", finish(img, d, np.linalg.norm(np.subtract(cam["eye"], cam["target"])), 2.6))
    if "cut" in which:
        c = Pr.cutaway(heat=0.0, water_glow=1.0, shell_glow=0.6).xf(T(0, 0.58, 0))
        g = cat([Pr.slate_static(), c])
        cam = dict(eye=(0.35, 0.75, 2.2), target=(0, 0.5, 0), fov=30)
        img, d, _ = R.render(cam, dict(STUDIO, extent=3.0, dir=(0.45, -0.55, -0.7)), g, lights=[((-2.0, 1.5, -2.5), 3.0, (1.2, 1.5, 2.2))])
        save("cut", finish(img, d, 2.0, 2.0))
    if "pop" in which:
        p = Pr.place(Pr.popped(3, 1.0), T(0, 1.0, 0) @ Ry(0.3))
        g = cat([Pr.slate_static(), p])
        cam = dict(eye=(2.4, 1.6, 3.4), target=(0, 0.9, 0), fov=30)
        img, d, _ = R.render(cam, dict(STUDIO, extent=4.0), g, lights=[((-2.0, 2.5, -3.5), 5.0, (2.0, 1.7, 1.4))])
        save("pop", finish(img, d, 4.2, 2.0))
    if "pan" in which:
        ks = cat([Pr.place(Pr.kernel(i % 3, 0.6), T(*xz, ) @ Ry(i) @ Rx(1.5)) for i, xz in
                  enumerate([(x, 0.62, z) for x, z in np.random.default_rng(1).uniform(-6, 6, (24, 2)) if math.hypot(x, z) < 7.5])])
        g = cat([Pr.stove_static(), Pr.pan_static(), ks])
        tr = cat([Pr.flame(0.3), Pr.oil(0.3)])
        cam = dict(eye=(0, 16, 26), target=(0, 1.0, 0), fov=34)
        img, d, _ = R.render(cam, dict(STUDIO, extent=18.0, center=(0, 0, 0), dist=60), g, tr,
                             lights=[((0, -1.0, 0), 6.0, (0.5, 0.9, 3.0)), ((-15, 12, -20), 30.0, (1.5, 1.7, 2.2))])
        save("pan", finish(img, d, 30, 6.0))
    if "bowl" in which:
        pile, _ = Pr.bowl_pile()
        g = cat([Pr.slate_static(), Pr.bowl_static(), pile])
        cam = dict(eye=(0, 30, 34), target=(0, 6, 0), fov=34)
        img, d, _ = R.render(cam, dict(STUDIO, extent=22.0, dist=80), g,
                             lights=[((-20, 16, -25), 40.0, (1.2, 1.4, 2.0))])
        save("bowl", finish(img, d, 44, 6.0))
    if "bottle" in which:
        g = cat([Pr.slate_static(), Pr.bottle_static(), Pr.cork(T(0, 30.6, 0))])
        cam = dict(eye=(10, 28, 30), target=(0, 24, 0), fov=34)
        img, d, _ = R.render(cam, dict(STUDIO, extent=30.0, dist=90), g, lights=[((-15, 30, -20), 40.0, (1.4, 1.6, 2.2))])
        save("bottle", finish(img, d, 33, 4.0))
