"""Shared helpers for the animated parts: narration timing, scene stacking, chapter titles, ORBI on a path."""
import json, math, os

from boards import *  # noqa: F401,F403
from boards import _disk, _SF, _SF2, _BK  # noqa: F401
SF, SF2, BK, disk = _SF, _SF2, _BK, _disk   # public aliases (star-imports skip underscore names)
from script import PARTS

PREMIUM, SAMPLES = True, 4


class Timing:
    """Start/end of narration lines and an estimate of when a word is spoken."""

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
    """Narration start times laid end to end with breathing room; extra = {key: added pause before it}."""
    path = os.path.join(HERE, "build", part, "vo", "durations.json")
    dur = json.load(open(path)) if os.path.exists(path) else {k: len(v) / 15.0 for k, v in PARTS[part]}
    vo, t = {}, first
    for k, _ in PARTS[part]:
        t += (extra or {}).get(k, 0.0)
        vo[k] = round(t, 2)
        t += dur[k] + gap
    return vo, t


def scenes(c, t, lst):
    """lst: [((t0, t1), t_end, fn)]; draws each active scene, cross-fading in over [t0, t1]."""
    for (t0, t1), t_end, fn in lst:
        if t0 <= t < t_end:
            a = smooth(prog(t, t0, t1))
            if a < 1:
                c.saveLayerAlpha(None, int(255 * a))
            fn(c, t)
            if a < 1:
                c.restore()


def fade(c, t, duration, fin=0.6, fout=0.7):
    a = max(1 - smooth(prog(t, 0, fin)), smooth(prog(t, duration - fout, duration)))
    if a > 0:
        c.drawPaint(fill(VOID, 255 * a))


def chapter_title(c, t, n, name, rgb, t0=0.15, t1=2.2):
    """Cinematic chapter card: number + name, light sweep, letter tracking that relaxes."""
    k = smooth(prog(t, t0, t0 + 0.8)) * (1 - smooth(prog(t, t1 - 0.6, t1)))
    if k <= 0.01:
        return
    track = lerp(26, 12, out_cubic(prog(t, t0, t1)))
    light(c, W / 2, H / 2, 700, rgb, 70 * k)
    text(c, f"CHAPTER {n}", W / 2, H / 2 - 70, 30, rgb, 255 * k, 800, spacing=12)
    text(c, name, W / 2, H / 2 + 30, 92, WHITE, 255 * k, 800, spacing=track)
    sweep = prog(t, t0 + 0.2, t0 + 1.6)
    if 0 < sweep < 1:
        x = lerp(W * 0.2, W * 0.8, in_out(sweep))
        light(c, x, H / 2 + 10, 260, lighten(rgb, 0.5), 140 * k * math.sin(math.pi * sweep))
    c.drawLine(W / 2 - 300 * k, H / 2 + 80, W / 2 + 300 * k, H / 2 + 80, stroke(rgb, 3, 200 * k))


def fly(path, t, dt=1 / 60):
    """Position, velocity and antenna lag for ORBI along path(t) -> (x, y)."""
    x, y = path(t)
    x2, y2 = path(t + dt)
    xl, yl = path(t - 0.14)
    return (x, y), ((x2 - x) / dt, (y2 - y) / dt), ((xl - x) / 380, (yl - y) / 380)


def orbi_on(c, t, path, r, expr="neutral", look=(0, 0), ears=0.2, rim=TEAL, rim2=MAGENTA, a=255, eye_rgb=None):
    (x, y), vel, lag = fly(path, t)
    sp = math.hypot(*vel)
    kw = dict(eye_rgb=eye_rgb) if eye_rgb else {}
    orbi(c, x, y, r, t, expr, look, vel, ears, 0.35 + min(1.0, sp / 800), rim=rim, rim2=rim2, a=a, antenna_lag=lag, **kw)
    return x, y


def drift_cam(t, t0, t1, x0=0, x1=0, y0=0, y1=0, z0=1.0, z1=1.08, rot0=0.0, rot1=0.0):
    k = in_out(prog(t, t0, t1))
    return Cam(lerp(x0, x1, k), lerp(y0, y1, k), lerp(z0, z1, k), lerp(rot0, rot1, k))


def shake(cam, t, t_hit, amp=10.0, decay=3.0):
    if t > t_hit:
        s = amp * math.exp(-(t - t_hit) * decay)
        cam.x += s * math.sin(t * 63)
        cam.y += s * math.cos(t * 57)
    return cam


def hold(c, cam, fn, depth=1.0):
    """Draw fn(c) in world space under cam at a parallax depth."""
    cam.push(c, depth)
    fn(c)
    cam.pop(c)


def push_screen(c, cam, depth=1.0):
    """Camera transform for objects authored in screen coordinates (0..W, 0..H). Pair with cam.pop(c)."""
    cam.push(c, depth)
    c.translate(-W / 2, -H / 2)
