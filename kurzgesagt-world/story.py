"""Shared helpers for the animated parts: narration timing, camera paths, chapter titles, acting helpers."""
import json, math, os

from earth import *  # noqa: F401,F403
from nimbus import nimbus  # noqa: F401
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


def fade(c, t, duration, fin=0.6, fout=0.7, rgb=(6, 8, 24)):
    a = max(1 - smooth(prog(t, 0, fin)), smooth(prog(t, duration - fout, duration)))
    if a > 0:
        c.drawPaint(fill(rgb, 255 * a))


def chapter_title(c, t, n, name, rgb, t0=0.15, t1=2.6):
    k = smooth(prog(t, t0, t0 + 0.7)) * (1 - smooth(prog(t, t1 - 0.6, t1)))
    if k <= 0.01:
        return
    c.drawPaint(fill((6, 8, 24), 120 * k))
    track = lerp(26, 12, out_cubic(prog(t, t0, t1)))
    text(c, f"CHAPTER {n}", W / 2, H / 2 - 70, 30, rgb, 255 * k, 800, spacing=12)
    text(c, name, W / 2, H / 2 + 30, 92, WHITE, 255 * k, 800, spacing=track)
    sweep = prog(t, t0 + 0.2, t0 + 1.6)
    if 0 < sweep < 1:
        light(c, lerp(W * 0.2, W * 0.8, in_out(sweep)), H / 2 + 10, 260, lighten(rgb, 0.5), 120 * k * math.sin(math.pi * sweep))
    c.drawLine(W / 2 - 300 * k, H / 2 + 80, W / 2 + 300 * k, H / 2 + 80, stroke(rgb, 3, 200 * k))


def tag(c, s, x, y, rgb=GOLD, size=26):
    f = font(size, 800)
    w = f.measureText(s) + size * 1.6 + len(s) * size * 0.12
    c.drawRRect(rrect(x - w / 2, y - size * 1.05, w, size * 1.6, size * 0.8), fill((10, 16, 40), 200))
    c.drawRRect(rrect(x - w / 2, y - size * 1.05, w, size * 1.6, size * 0.8), stroke(rgb, 2.5, 230))
    text(c, s, x, y, size * 0.8, rgb, 255, 800, spacing=size * 0.12)


def big_number(c, s, x, y, size, rgb, t, t0, t1=None, sub=None):
    """Hero number that slams in (scale overshoot + flash) and fades out."""
    a = smooth(prog(t, t0, t0 + 0.25)) * (1 - (smooth(prog(t, t1 - 0.4, t1)) if t1 else 0))
    if a <= 0.01:
        return
    k = out_back(prog(t, t0, t0 + 0.5), 1.8)
    c.save()
    c.translate(x, y)
    c.scale(1.4 - 0.4 * k, 1.4 - 0.4 * k)
    text(c, s, 0, 0, size, rgb, 255 * a, 800, spacing=size * 0.06)
    if sub:
        text(c, sub, 0, size * 0.62, size * 0.26, WHITE, 230 * a, 800, spacing=size * 0.05)
    c.restore()
    if t < t0 + 0.4:
        light(c, x, y - size * 0.3, size * 2.5, rgb, 120 * a * (1 - prog(t, t0, t0 + 0.4)))


def nim(c, t, track, path, r=110, look=None, **kw):
    """Nimbus on a path with velocity-driven squash/bank and track-driven face; returns (x, y)."""
    (x, y), vel = path_vel(path, t)
    lk = look(t) if callable(look) else (look or (0.0, 0.0))
    nimbus(c, x, y, r, t, track.at(t), lk, blink_amount(t, track.change_times(), 3.8, 0.4), vel, **kw)
    return x, y


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


def xfade(c, t, t0, dur, draw_a, draw_b, push=0.25):
    """Zoom-through transition: scene A pushes in and fades while scene B settles in from slightly smaller."""
    k = in_out(prog(t, t0, t0 + dur))
    if k <= 0:
        draw_a(c, t)
        return
    if k >= 1:
        draw_b(c, t)
        return
    c.save()
    s = 1 + push * k
    c.translate(W / 2, H / 2)
    c.scale(s, s)
    c.translate(-W / 2, -H / 2)
    draw_a(c, t)
    c.restore()
    c.saveLayerAlpha(None, int(255 * k))
    s = 1 - 0.12 * (1 - k)
    c.translate(W / 2, H / 2)
    c.scale(s, s)
    c.translate(-W / 2, -H / 2)
    draw_b(c, t)
    c.restore()


