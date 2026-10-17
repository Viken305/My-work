"""Shared helpers for the animated parts: narration timing, camera paths, chapter titles, acting helpers."""
import json, math, os

from world import *  # noqa: F401,F403
from bigeater import eater  # noqa: F401
from script import PARTS

PREMIUM, SAMPLES = True, 4


class Timing:
    """Start of narration lines and an estimate of when a given word is spoken."""

    def __init__(self, part, vo):
        self.vo, self.text = vo, dict(PARTS[part])
        path = os.path.join(HERE, "build", part, "vo", "durations.json")
        self.dur = json.load(open(path)) if os.path.exists(path) else {k: len(v) / 15.0 for k, v in self.text.items()}

    def end(self, k):
        return self.vo[k] + self.dur[k]

    def word(self, k, w):
        s = self.text[k].lower()
        i = s.find(w.lower())
        assert i >= 0, (k, w)
        return self.vo[k] + 0.12 + (i / len(s)) * (self.dur[k] - 0.25)


def schedule(part, first=1.4, gap=0.55, extra=None):
    path = os.path.join(HERE, "build", part, "vo", "durations.json")
    dur = json.load(open(path)) if os.path.exists(path) else {k: len(v) / 15.0 for k, v in PARTS[part]}
    vo, t = {}, first
    for k, _ in PARTS[part]:
        t += (extra or {}).get(k, 0.0)
        vo[k] = round(t, 2)
        t += dur[k] + gap
    return vo, t


class CamPath:
    """Camera keyframes [(t, x, y, zoom)] with smooth easing between them + a gentle handheld drift."""

    def __init__(self, keys, drift=6.0):
        self.keys, self.drift = keys, drift

    def at(self, t):
        k = self.keys
        if t <= k[0][0]:
            x, y, z = k[0][1:]
        elif t >= k[-1][0]:
            x, y, z = k[-1][1:]
        else:
            for i in range(len(k) - 1):
                if k[i][0] <= t < k[i + 1][0]:
                    u = in_out(prog(t, k[i][0], k[i + 1][0]))
                    x, y, z = (lerp(a, b, u) for a, b in zip(k[i][1:], k[i + 1][1:]))
                    break
        d = self.drift
        return Cam(x + d * math.sin(t * 0.7) + d * 0.5 * math.sin(t * 1.9), y + d * math.cos(t * 0.6) + d * 0.4 * math.sin(t * 2.3), z)


def fade(c, t, duration, fin=0.6, fout=0.7, rgb=(30, 4, 14)):
    a = max(1 - smooth(prog(t, 0, fin)), smooth(prog(t, duration - fout, duration)))
    if a > 0:
        c.drawPaint(fill(rgb, 255 * a))


def chapter_title(c, t, n, name, rgb, t0=0.15, t1=2.6):
    k = smooth(prog(t, t0, t0 + 0.7)) * (1 - smooth(prog(t, t1 - 0.6, t1)))
    if k <= 0.01:
        return
    c.drawPaint(fill((30, 4, 14), 110 * k))
    track = lerp(26, 12, out_cubic(prog(t, t0, t1)))
    text(c, f"CHAPTER {n}", W / 2, H / 2 - 70, 30, rgb, 255 * k, 800, spacing=12)
    text(c, name, W / 2, H / 2 + 30, 92, WHITE, 255 * k, 800, spacing=track)
    sweep = prog(t, t0 + 0.2, t0 + 1.6)
    if 0 < sweep < 1:
        light(c, lerp(W * 0.2, W * 0.8, in_out(sweep)), H / 2 + 10, 260, lighten(rgb, 0.5), 120 * k * math.sin(math.pi * sweep))
    c.drawLine(W / 2 - 300 * k, H / 2 + 80, W / 2 + 300 * k, H / 2 + 80, stroke(rgb, 3, 200 * k))


def chip(c, s, x, y, rgb, t, t0, t1=None, size=26):
    """Label chip that pops in (scale overshoot) and fades out."""
    a = smooth(prog(t, t0, t0 + 0.35)) * (1 - (smooth(prog(t, t1 - 0.35, t1)) if t1 else 0))
    if a <= 0.01:
        return
    k = out_back(prog(t, t0, t0 + 0.45), 1.6)
    c.save()
    c.translate(x, y)
    c.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k)
    c.saveLayerAlpha(None, int(255 * a))
    tag(c, s, 0, 0, rgb, size)
    c.restore()
    c.restore()


def path_vel(f, t, dt=1 / 60):
    x, y = f(t)
    x2, y2 = f(t + dt)
    return (x, y), ((x2 - x) / dt, (y2 - y) / dt)
