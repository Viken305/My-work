"""Shared helpers for the gold Short: narration timing, kinetic caption track, camera, element chips, small props."""
import json, math, os

from kinetic import *  # noqa: F401,F403
from kinetic import _word  # noqa: F401
from script import PARTS

PREMIUM, SAMPLES = True, 3


def durations(part):
    path = os.path.join(HERE, "build", part, "vo", "durations.json")
    return json.load(open(path)) if os.path.exists(path) else {k: len(v) / 15.0 for k, v in PARTS[part]}


def schedule(part, first=0.4, gap=0.5, extra=None):
    dur = durations(part)
    vo, t = {}, first
    for k, _ in PARTS[part]:
        t += (extra or {}).get(k, 0.0)
        vo[k] = round(t, 2)
        t += dur[k] + gap
    return vo, t


class Timing:
    def __init__(self, part, vo):
        self.vo, self.text, self.dur = vo, dict(PARTS[part]), durations(part)

    def word(self, k, w):
        s = self.text[k].lower()
        i = s.find(w.lower())
        assert i >= 0, (k, w)
        return self.vo[k] + 0.08 + (i / len(s)) * (self.dur[k] - 0.15)

    def words(self, k):
        """[(start, end, WORD)] spread over the line by character position."""
        s, out, pos = self.text[k], [], 0
        ws = s.split()
        total = sum(len(w) + 1 for w in ws)
        d = self.dur[k]
        for w in ws:
            a = self.vo[k] + 0.08 + pos / total * (d - 0.15)
            pos += len(w) + 1
            b = self.vo[k] + 0.08 + pos / total * (d - 0.15)
            out.append((a, b, w.upper()))
        return out


def _clean(w):
    return w.strip(".,!?:;'\"").replace("’", "'")


class Captions:
    """Kinetic caption track for one part.
    anchors: {line_key: (x, y)} default spot for that line's phrases (can be a function of phrase index).
    heroes:  {WORD: (x, y, size)} words that slam in as gold letters instead of appearing in the phrase.
    reacts:  {WORD: (fn, x, y, size)} words acted out by a react_* function instead of appearing in the phrase."""

    def __init__(self, tm, anchors=None, heroes=None, reacts=None, size=74, max_words=4, skip=()):
        self.tm, self.size = tm, size
        self.heroes, self.reacts = heroes or {}, reacts or {}
        self.phrases, self.specials = [], []
        for k in tm.vo:
            if k in skip:
                continue
            ws = tm.words(k)
            anchor = (anchors or {}).get(k, (W / 2, 400))
            cur = []
            groups = []
            for item in ws:
                cur.append(item)
                if len(cur) >= max_words or item[2][-1] in ".,?!:;" or len(" ".join(x[2] for x in cur)) > 22:
                    groups.append(cur)
                    cur = []
            if cur:
                groups.append(cur)
            for gi, g in enumerate(groups):
                keep = []
                for (a, b, w) in g:
                    cw = _clean(w)
                    if cw in self.heroes:
                        self.specials.append(("hero", a, cw, self.heroes[cw]))
                    elif cw in self.reacts:
                        self.specials.append(("react", a, cw, self.reacts[cw]))
                    else:
                        keep.append((a, b, w))
                if keep:
                    an = anchor(gi) if callable(anchor) else anchor
                    self.phrases.append([keep[0][0], None, keep, an])
        self.phrases.sort(key=lambda p: p[0])
        for i, p in enumerate(self.phrases):
            nxt = self.phrases[i + 1][0] if i + 1 < len(self.phrases) else p[2][-1][1] + 1.0
            p[1] = min(p[2][-1][1] + 0.9, nxt - 0.22)

    def draw(self, c, t):
        shake_ = 0.0
        for t0, t1, ws, (x, y) in self.phrases:
            if t < t0 - 0.05 or t > t1 + 0.25:
                continue
            words = [w for _, _, w in ws]
            starts = [a for a, _, _ in ws]
            hi = max([i for i, a in enumerate(starts) if a <= t] or [0])
            hi = hi if t < ws[-1][1] + 0.15 else None
            _timed_phrase(c, words, starts, x, y, t, self.size, hi, t1)
        for kind, a, w, spec in self.specials:
            if not (a - 0.05 <= t <= a + 3.0):
                continue
            if kind == "hero":
                x, y, size = spec
                shake_ += hero(c, w, x, y, t, a, size, settle=a + 1.4)
            else:
                fn, x, y, size = spec
                fa = 1 - smooth(prog(t, a + 1.3, a + 1.7))
                if fa > 0.01:
                    c.saveLayerAlpha(None, int(255 * fa))
                    fn(c, x, y - 30 * (1 - fa), t, a, size)
                    c.restore()
        return shake_


def _timed_phrase(c, words, starts, x, y, t, size, hi, exit_t, max_w=860):
    def widths(sz):
        f = font(int(sz), 800)
        return [f.measureText(w) for w in words], sz * 0.28
    ws, gap = widths(size)
    lines = [list(range(len(words)))]
    if sum(ws) + gap * (len(words) - 1) > max_w and len(words) > 1:
        best = min(range(1, len(words)), key=lambda k: abs(sum(ws[:k]) - sum(ws[k:])))
        lines = [list(range(best)), list(range(best, len(words)))]
    while max(sum(ws[i] for i in ln) + gap * (len(ln) - 1) for ln in lines) > max_w:
        size *= 0.94
        ws, gap = widths(size)
    ex = smooth(prog(t, exit_t, exit_t + 0.2))
    lh = size * 1.12
    for li, ln in enumerate(lines):
        total = sum(ws[i] for i in ln) + gap * (len(ln) - 1)
        cx = x - total / 2
        ly = y + (li - (len(lines) - 1) / 2) * lh
        for i in ln:
            u = prog(t, starts[i] - 0.06, starts[i] + 0.26)
            if u > 0:
                sc = 0.6 + 0.4 * out_back(u, 2.2)
                a = 255 * smooth(u) * (1 - ex)
                _word(c, words[i], cx + ws[i] / 2, ly + 24 * (1 - out_cubic(u)) - 40 * ex, size, GOLD if i == hi else WHITE, a, sc, 0.0, 6 * (1 - u))
            cx += ws[i] + gap


class CamPath:
    def __init__(self, keys, drift=5.0):
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
        return Cam(x + d * math.sin(t * 0.7), y + d * math.cos(t * 0.6), z)


def fade(c, t, duration, fin=0.3, fout=0.5, rgb=(4, 4, 14)):
    a = max(1 - smooth(prog(t, 0, fin)) if fin > 0 else 0.0, smooth(prog(t, duration - fout, duration)) if fout > 0 else 0.0)
    if a > 0:
        c.drawPaint(fill(rgb, 255 * a))


def chip(c, s, x, y, rgb, t, t0, t1=None, size=30):
    a = smooth(prog(t, t0, t0 + 0.3)) * (1 - (smooth(prog(t, t1 - 0.3, t1)) if t1 else 0))
    if a <= 0.01:
        return
    k = out_back(prog(t, t0, t0 + 0.4), 1.6)
    f = font(size, 800)
    w = f.measureText(s) + size * 1.6 + len(s) * size * 0.12
    c.save()
    c.translate(x, y)
    c.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k)
    c.saveLayerAlpha(None, int(255 * a))
    c.drawRRect(rrect(-w / 2, -size * 1.05, w, size * 1.6, size * 0.8), fill((14, 10, 30), 210))
    c.drawRRect(rrect(-w / 2, -size * 1.05, w, size * 1.6, size * 0.8), stroke(rgb, 3, 230))
    text(c, s, 0, 0, size * 0.8, rgb, 255, 800, spacing=size * 0.12)
    c.restore()
    c.restore()


ELEM = {"H": (150, 200, 255), "He": (255, 220, 120), "C": (130, 130, 150), "O": (255, 110, 110), "Si": (180, 150, 255),
        "Fe": (230, 140, 90), "Au": GOLD}


def element(c, sym, x, y, s, a=255, sc=1.0):
    if a <= 1:
        return
    rgb = ELEM[sym]
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    c.saveLayerAlpha(None, int(a))
    light(c, 0, 0, s * 1.4, rgb, 110)
    c.drawRRect(rrect(-s / 2, -s / 2, s, s, s * 0.18), shaded(linear((0, -s / 2), (0, s / 2), [mix((20, 20, 50), rgb, 0.65), mix((20, 20, 50), rgb, 0.3)])))
    c.drawRRect(rrect(-s / 2, -s / 2, s, s, s * 0.18), stroke(lighten(rgb, 0.4), s * 0.035, 220))
    text(c, sym, 0, s * 0.17, s * 0.5, WHITE, 255, 800)
    c.restore()
    c.restore()


def mini_earth(c, x, y, r, t, gold_k=0.0, a=255):
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    light(c, x, y, r * 1.6, (110, 170, 255), 90)
    c.drawCircle(x, y, r, shaded(radial((x - r * 0.35, y - r * 0.4), r * 1.5, [(90, 170, 255), (40, 100, 210), (20, 40, 110)])))
    disc = skia.Path()
    disc.addCircle(x, y, r)
    c.save()
    c.clipPath(disc, doAntiAlias=True)
    for dx, dy, rr in ((-0.35, -0.2, 0.42), (0.35, 0.25, 0.36), (0.1, -0.55, 0.25)):
        c.drawCircle(x + (dx + 0.15 * math.sin(t * 0.3)) * r, y + dy * r, rr * r, fill((90, 170, 90)))
    c.restore()
    if gold_k > 0:
        gold_sphere(c, x, y, r * (0.97 + 0.03 * gold_k), (90, 120, 200), 255 * gold_k)
    if a < 255:
        c.restore()


def ring(c, cx, cy, s, t, part="both", a=255):
    """Polished gold ring seen at an angle (back or front half so things can pass through it)."""
    outer = skia.Rect.MakeXYWH(cx - 330 * s, cy - 120 * s, 660 * s, 240 * s)
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=70 * s,
                   Shader=linear((cx - 330 * s, cy - 120 * s), (cx + 330 * s, cy + 120 * s),
                                 [GOLD_DEEP, GOLD_HI, GOLD, GOLD_MID, GOLD_HI, GOLD_DEEP], [0, 0.2, 0.4, 0.6, 0.8, 1]))
    p.setAlphaf(a / 255)
    if part in ("back", "both"):
        arc = skia.Path()
        arc.addArc(outer, 180, 180)
        c.drawPath(arc, p)
    if part in ("front", "both"):
        arc = skia.Path()
        arc.addArc(outer, 0, 180)
        c.drawPath(arc, p)
        sw = (t * 0.5) % 1.6 - 0.3
        c.drawArc(skia.Rect.MakeXYWH(cx - 300 * s, cy - 105 * s, 600 * s, 210 * s), 20 + 140 * sw, 40, False, stroke(WHITE, 8 * s, 170 * a / 255))
