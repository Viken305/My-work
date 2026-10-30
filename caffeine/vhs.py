"""The tape: turns a clean Skia frame into a worn VHS playback.

  * luma loses detail and gets the edge-enhancement halo of a VCR; chroma is smeared sideways and lags to the right
  * every scan line wobbles a little (time-base error); a tracking band crawls near the bottom; head-switching noise
    tears the last lines; white dropouts flick across; fast-forward rips the picture into bands
  * lifted blacks, warm highlights, soft scanlines, CRT vignette, snow
OSD and closed captions are drawn after this pass (the VCR and the TV draw them, not the tape), so they stay sharp.
"""
import math

import cv2
import numpy as np
import skia

from engine import FPS, H, W, col

cv2.setNumThreads(1)
_X = np.arange(W, dtype=np.float32)[None, :].repeat(H, 0)
_Y = np.arange(H, dtype=np.float32)[:, None].repeat(W, 1)
_ROWS = np.arange(H, dtype=np.float32)
_SCAN = (0.93 + 0.07 * np.cos(_ROWS * 2 * np.pi / 6))[:, None, None].astype(np.float32)
_r = np.sqrt(((_X - W / 2) / (W / 2)) ** 2 * 0.8 + ((_Y - H / 2) / (H / 2)) ** 2)
_VIG = (1 - 0.5 * np.clip(_r - 0.55, 0, 1) ** 1.4)[..., None].astype(np.float32)
del _r
_SNOW = [np.random.default_rng(s).normal(0, 1, (H // 2, W // 2)).astype(np.float32) for s in range(6)]


def _smooth_noise(rng, n, k):
    x = rng.normal(0, 1, n // k + 3).astype(np.float32)
    return np.interp(np.arange(n) / k, np.arange(len(x)), x).astype(np.float32)


def post(img, t, ff=0.0, rew=0.0, track=0.3, snow=1.0, sag=0.0, bloom=0.5, jitter=1.0, chroma=1.0):
    """img: float32 HxWx3 RGB 0..255 -> uint8.  ff / rew: 0..1 fast-forward or rewind tearing; sag: the crash
    (picture drains, sinks and stretches); track: strength of the crawling tracking band."""
    fr = int(round(t * FPS))
    rng = np.random.default_rng(fr * 7919 + 13)
    # glow on bright parts (CRT phosphor bloom)
    if bloom > 0:
        small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        b = cv2.GaussianBlur(np.clip(small - 165, 0, None), (0, 0), 7)
        img = img + cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR) * bloom
    R, G, B = img[..., 0], img[..., 1], img[..., 2]
    Yl = 0.299 * R + 0.587 * G + 0.114 * B
    U, V = B - Yl, R - Yl
    # luma: soft horizontally, then the VCR's sharpening ring
    Yl = cv2.blur(Yl, (5, 1))
    Yl = Yl + 0.55 * (Yl - cv2.GaussianBlur(Yl, (0, 0), sigmaX=6, sigmaY=0.1))
    # chroma: low bandwidth, smeared to the right
    cw = max(16, int(W / (8 + 4 * chroma)))
    U = cv2.resize(cv2.resize(U, (cw, H // 2), interpolation=cv2.INTER_AREA), (W, H), interpolation=cv2.INTER_LINEAR)
    V = cv2.resize(cv2.resize(V, (cw, H // 2), interpolation=cv2.INTER_AREA), (W, H), interpolation=cv2.INTER_LINEAR)
    sh = int(6 + 4 * chroma)
    U = np.roll(U, sh, 1)
    V = np.roll(V, sh, 1)
    sat = 1.12 * (1 - 0.85 * sag)
    U *= sat
    V *= sat
    # per-line horizontal offsets
    off = _smooth_noise(rng, H, 3) * 0.7 * jitter + 1.2 * jitter * math.sin(t * 2.1) * np.sin(_ROWS / 260 + t * 3)
    yb = H * (0.80 + 0.12 * ((t * 0.07) % 1))                     # tracking band crawls down the frame
    band = np.exp(-((_ROWS - yb) / 34) ** 2) * track
    off += band * (18 * _smooth_noise(rng, H, 2))
    hs = _ROWS > H - 30                                          # head switching
    off[hs] += 22 + 10 * rng.random()
    tear = max(ff, rew)
    if tear > 0:
        for _ in range(int(3 + 9 * tear)):
            y0 = int(rng.integers(0, H))
            hgt = int(rng.integers(20, 140))
            off[y0:y0 + hgt] += (rng.random() - 0.5) * 160 * tear
        off += _smooth_noise(rng, H, 40) * 30 * tear
    mapx = _X - off[:, None]
    my = _Y
    if tear > 0:                                                  # vertical roll while winding
        roll = ((t * (900 if ff else -1100)) % H) * tear
        my = (_Y + roll) % H
    if sag > 0:                                                   # the picture sinks and stretches
        my = np.clip(_Y * (1 - 0.18 * sag) + 0, 0, H - 1) if tear == 0 else my
    Yl = cv2.remap(Yl, mapx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    U = cv2.remap(U, mapx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    V = cv2.remap(V, mapx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    # tracking band and dropouts: white streaks
    nb = band[:, None] * (rng.random((H, 1)) > 0.55) * 120 * rng.random((H, 1))
    Yl = Yl + nb * (np.sin(_X / (9 + 6 * rng.random()) + rng.random() * 6) > 0.2)
    for _ in range(int(rng.integers(1, 4) + 30 * tear)):
        y0, x0 = int(rng.integers(0, H - 3)), int(rng.integers(0, W))
        Yl[y0:y0 + 2, x0:x0 + int(rng.integers(20, 160))] += 160
    R = Yl + V
    B = Yl + U
    G = (Yl - 0.299 * R - 0.114 * B) / 0.587
    out = np.stack([R, G, B], -1)
    # snow, scanlines, vignette, grade (lifted blacks, warm highlights)
    g = cv2.resize(_SNOW[fr % len(_SNOW)], (W, H), interpolation=cv2.INTER_NEAREST)
    out = out + g[..., None] * (5 + 40 * tear) * snow
    out = out * _SCAN * _VIG
    if sag > 0:
        out = out * (1 - 0.35 * sag)
    out = 12 + out * 0.94
    out[..., 0] *= 1.03
    out[..., 2] *= 0.96
    return np.clip(out, 0, 255).astype(np.uint8)


def snapshot(surface):
    return surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)


def render(draw_frame, t, samples=2, shutter=0.7, overlay=None, **kw):
    s = skia.Surface(W, H)
    c = s.getCanvas()
    acc = None
    for i in range(max(1, samples)):
        ts = t + ((i + 0.5) / samples - 0.5) * shutter / FPS if samples > 1 else t
        c.clear(col((0, 0, 0)))
        draw_frame(c, ts)
        f = snapshot(s)
        acc = f if acc is None else acc + f
    out = post(acc / max(1, samples), t, **kw)
    if overlay is None:
        return out
    c.clear(skia.Color4f(0, 0, 0, 0))
    overlay(c, t)
    ov = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.float32)
    al = ov[..., 3:4] / 255.0
    return np.clip(ov[..., :3] * al + out * (1 - al), 0, 255).astype(np.uint8)
