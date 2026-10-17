"""Helpers shared by parts 2-6: narration timing, recipe title sequence, chapter fades."""
import json, os

from engine import *  # noqa: F401,F403
from script import PARTS
from styleframes import (CARBON, OX, SI, _circle, _gem, caption, icon_down, icon_drop, icon_flame,  # noqa: F401
                         icon_sprout, prism, streak_atom, title_card, wavy_band)

DARK = (8, 8, 24)
circle_path, gem_shape = _circle, _gem


class Timing:
    """Start/end of narration lines, plus an estimate of when a given word is spoken."""

    def __init__(self, part, vo):
        self.vo, self.text = vo, dict(PARTS[part])
        path = os.path.join(HERE, "build", part, "vo", "durations.json")
        if os.path.exists(path):
            self.dur = json.load(open(path))
        else:  # no clips yet: rough speaking rate
            self.dur = {k: len(v) / 15.0 for k, v in self.text.items()}

    def start(self, k):
        return self.vo[k]

    def end(self, k):
        return self.vo[k] + self.dur[k]

    def word(self, k, w):
        s = self.text[k].lower()
        i = s.find(w.lower())
        assert i >= 0, (k, w)
        return self.vo[k] + 0.12 + (i / len(s)) * (self.dur[k] - 0.25)


def title_sequence(c, t, n, name, rgb, icon, t_in, t_dock, t_out=None):
    """Big centred RECIPE badge that docks into the corner pill."""
    k = pop(t, t_in, 0.6)
    out = in_out(prog(t, t_dock, t_dock + 0.55))
    if k > 0 and out < 1:
        x, y = lerp(W / 2, 125, out), lerp(470, 115, out)
        s = k * lerp(1.0, 0.3, out)
        a = 255 * (1 - smooth(prog(t, t_dock + 0.25, t_dock + 0.55)))
        c.saveLayerAlpha(None, int(a))
        glow(c, x, y, 260 * s, rgb, 120)
        c.drawCircle(x, y, 120 * s, fill(rgb))
        c.drawCircle(x, y, 120 * s, stroke(WHITE, 8 * s, 220))
        c.save()
        c.translate(x, y)
        c.scale(s * 3.6, s * 3.6)
        icon(c, 0, 0, 22)
        c.restore()
        ta = smooth(prog(t, t_in + 0.25, t_in + 0.6)) * (1 - out)
        text(c, f"RECIPE {n}", W / 2, 670, 34, rgb, 255 * ta, 800, spacing=10)
        text(c, name, W / 2, 770, 110, WHITE, 255 * ta, 800, spacing=12)
        c.restore()
    pa = smooth(prog(t, t_dock + 0.3, t_dock + 0.7))
    if t_out is not None:
        pa *= 1 - smooth(prog(t, t_out, t_out + 0.4))
    if pa > 0.01:
        c.saveLayerAlpha(None, int(255 * pa))
        title_card(c, n, name, rgb, icon)
        c.restore()


def title_backdrop(c, t, rgb, a=1.0):
    c.drawPaint(fill(NAVY, 255 * a))
    c.drawPaint(shaded(radial((W / 2, 480), 900, [(rgb, 70 * a), (PURPLE, 0)])))


def chapter_fade(c, t, duration, fade_in=0.5, fade_out=0.6):
    a = 1 - smooth(prog(t, 0, fade_in))
    a = max(a, smooth(prog(t, duration - fade_out, duration)))
    if a > 0:
        c.drawPaint(fill(DARK, 255 * a))


def cam(c, z, fx, fy):
    """Camera: zoom z around world point (fx, fy) placed at screen centre. Caller restores."""
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-fx, -fy)


def crossfade(c, t, t0, t1, draw_a, draw_b):
    """Draw scene a, then scene b on top with rising opacity during [t0, t1]."""
    k = smooth(prog(t, t0, t1))
    if k < 1:
        draw_a(c)
    if k > 0:
        if k < 1:
            c.saveLayerAlpha(None, int(255 * k))
        draw_b(c)
        if k < 1:
            c.restore()


def pill_tag(c, x, y, label, rgb, g=1.0, size=28, down=True):
    """Coloured name tag with a little pointer."""
    if g <= 0.01:
        return
    c.save()
    c.translate(x, y)
    c.scale(g, g)
    w = font(size, 800).measureText(label) + size * 0.07 * (len(label) - 1) + size * 1.5
    c.drawRRect(rrect(-w / 2, -size, w, size * 1.8, size * 0.9), fill(rgb))
    if down:
        c.drawPath(poly([(-10, size * 0.78), (10, size * 0.78), (0, size * 1.35)]), fill(rgb))
    text(c, label, 0, size * 0.36, size, INK, 255, 800, spacing=size * 0.07)
    c.restore()


def bubble_q(c, x, y, g, mark="?"):
    if g <= 0.01:
        return
    c.save()
    c.translate(x, y)
    c.scale(g, g)
    c.drawRRect(rrect(-48, -54, 96, 96, 30), fill(WHITE))
    c.drawPath(poly([(10, 38), (40, 38), (46, 70)]), fill(WHITE))
    text(c, mark, 0, 16, 64, INK, 255, 800)
    c.restore()
