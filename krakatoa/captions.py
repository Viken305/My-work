"""Audio-reactive captions.

  * each word ripples in as it is spoken: its letters lift and settle with a spring one after another, like a pressure
    wave travelling through the text, rising out of a soft blur
  * the word being spoken swells slightly with the loudness of the voice (envelope of the real narration audio)
  * emphasis words switch to the serif italic in sulfur (sound) or lava (harm) and pulse one thin ring
  * a phrase leaves sideways: its words compress and blur, as if pushed by a passing wave
"""
import math, os, re

import numpy as np
import soundfile as sf
import skia

from cyan import LAVA, PAPER, SULFUR, W, clamp, font, light, mix, out_cubic, paint, prog, smooth, spring, width
from script import DISPLAY
from timing import vo_dir


def _clean(w):
    return re.sub(r"[^\w'%°.,\-]", "", w).strip(".,").lower()


def displayed(items):
    """Merge spoken number words into what the captions show: [(t0, t1, "eighteen"), (.., "eighty-three,")] ->
    [(t0, t1, "1883,")], keeping the trailing punctuation of the last spoken word."""
    out, i = [], 0
    while i < len(items):
        for spoken, shown in DISPLAY:
            sw = spoken.split()
            seg = items[i:i + len(sw)]
            if len(seg) == len(sw) and all(_clean(a[2]) == b for a, b in zip(seg, sw)):
                tail = re.sub(r"^.*?([.,?!;:]*)$", r"\1", seg[-1][2])
                out.append((seg[0][0], seg[-1][1], shown + tail))
                i += len(sw)
                break
        else:
            out.append(items[i])
            i += 1
    return out


class VoiceEnvelope:
    """Loudness of the narration over time (0..1), from the clips themselves."""

    def __init__(self, part, vo):
        self.items = []
        for k, t0 in vo.items():
            x, sr = sf.read(os.path.join(vo_dir(part), f"{k}.wav"))
            if x.ndim > 1:
                x = x.mean(1)
            hop = sr // 100
            n = len(x) // hop
            rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
            rms = np.convolve(rms, np.ones(5) / 5, "same")
            self.items.append((t0, rms / (rms.max() + 1e-9)))

    def __call__(self, t):
        for t0, e in self.items:
            i = int((t - t0) * 100)
            if 0 <= i < len(e):
                return float(e[i])
        return 0.0


class Captions:
    """Word-synced captions for one part.

    tm       timing.Timing for the part
    sound    words drawn in the sulfur serif italic (lower-case, no punctuation); harm: the same in lava
    anchors  {line_key: (x, y)} centre of the caption block (default y = 1380, above the Shorts UI)
    hide     {line_key: [(t0, t1)]} windows where captions are suppressed (a title says it instead)
    """

    def __init__(self, tm, env=None, sound=(), harm=(), anchors=None, hide=None, size=80, max_words=3, max_chars=18, skip=()):
        self.size, self.env = size, env
        self.colour = {**{w: SULFUR for w in sound}, **{w: LAVA for w in harm}}
        self.hide = hide or {}
        self.phrases = []
        for k in tm.vo:
            if k in skip:
                continue
            ax, ay = (anchors or {}).get(k, (W / 2, 1380))
            cur, groups = [], []
            for item in displayed(tm.words(k)):
                cur.append(item)
                if len(cur) >= max_words or item[2][-1] in ".,?!:;" or len(" ".join(x[2] for x in cur)) > max_chars:
                    groups.append(cur)
                    cur = []
            if cur:
                groups.append(cur)
            for g in groups:
                self.phrases.append(self._layout(k, g, ax, ay))
        self.phrases.sort(key=lambda p: p["t0"])
        for i, p in enumerate(self.phrases):
            nxt = self.phrases[i + 1]["t0"] if i + 1 < len(self.phrases) else p["words"][-1]["t1"] + 1.2
            p["t1"] = min(p["words"][-1]["t1"] + 0.7, nxt - 0.3)

    def _layout(self, k, g, ax, ay):
        words = []
        for a, b, w in g:
            rgb = self.colour.get(_clean(w))
            kind = "serif_bold" if rgb else "bold"
            sz = self.size * (1.14 if rgb else 1.0)
            txt = w.rstrip(",;:") if not w.endswith((".", "?", "!")) else w
            words.append(dict(t0=a, t1=b, text=txt, rgb=rgb, kind=kind, size=sz, w=width(txt, kind, sz)))
        space = self.size * 0.32
        total = sum(x["w"] for x in words) + space * (len(words) - 1)
        lines = [words]
        if total > 900 and len(words) > 1:
            best = min(range(1, len(words)), key=lambda i: abs(sum(x["w"] for x in words[:i]) - total / 2))
            lines = [words[:best], words[best:]]
        lh = self.size * 1.18
        y0 = ay - (len(lines) - 1) * lh / 2
        for li, ln in enumerate(lines):
            lw = sum(x["w"] for x in ln) + space * (len(ln) - 1)
            x = ax - lw / 2
            for wd in ln:
                wd["x"], wd["y"] = x, y0 + li * lh
                x += wd["w"] + space
        return dict(key=k, t0=words[0]["t0"] - 0.05, words=words)

    def draw(self, c, t, a=1.0):
        for p in self.phrases:
            if t < p["t0"] - 0.05 or t > p["t1"] + 0.4:
                continue
            if any(a0 <= t <= a1 for a0, a1 in self.hide.get(p["key"], ())):
                continue
            for i, wd in enumerate(p["words"]):
                ex = smooth(prog(t, p["t1"] + i * 0.03, p["t1"] + i * 0.03 + 0.24))
                if ex >= 1:
                    continue
                self._word(c, t, wd, ex, a)

    def _word(self, c, t, wd, ex, a):
        speaking = wd["t0"] - 0.05 <= t <= wd["t1"] + 0.08
        swell = 1.0 + (0.05 * self.env(t) if self.env and speaking else 0.0)
        rgb = wd["rgb"] or (PAPER if speaking or t < wd["t1"] else mix(PAPER, (150, 170, 192), 0.45))
        f = font(wd["kind"], wd["size"] * swell)
        x0, y = wd["x"] - wd["w"] * (swell - 1) / 2, wd["y"]
        if ex > 0:   # exit: pushed sideways by the wave, squeezed and blurred
            c.save()
            c.translate(x0 + 40 * ex, y)
            c.scale(1 + 0.25 * ex, 1 - 0.2 * ex)
            c.drawString(wd["text"], 0, 0, f, paint(rgb, 255 * a * (1 - ex), sigma=10 * ex))
            c.restore()
            return
        u0 = t - (wd["t0"] - 0.06)
        if u0 < 0:
            return
        if wd["rgb"]:   # one ring pulse + a faint glow behind emphasis words
            q = out_cubic(u0 / 0.7)
            rr = wd["w"] * (0.55 + 0.6 * q)
            pth = skia.Path()
            pth.addOval(skia.Rect.MakeXYWH(x0 + wd["w"] / 2 - rr, y - wd["size"] * 0.32 - rr * 0.42, rr * 2, rr * 0.84))
            c.drawPath(pth, paint(wd["rgb"], 160 * (1 - q) * a, sigma=3, plus=True, stroke=2.4))
            light(c, x0 + wd["w"] / 2, y - wd["size"] * 0.3, wd["w"] * 0.9, wd["rgb"], 38 * a * smooth(u0 / 0.3))
        cx = x0
        for j, ch in enumerate(wd["text"]):
            u = (u0 - j * 0.022) / 0.5
            adv = f.measureText(ch)
            if u > 0 and ch != " ":
                lift = math.sin(clamp(u * 1.6) * math.pi) * 9 * (1 - clamp(u))
                dy = (1 - spring(u, 8, 11)) * 24 - lift
                al = clamp(u * 3) * 255 * a
                blur = (1 - clamp(u * 2.2)) * 9
                c.drawString(ch, cx + 3, y + dy + 5, f, paint((0, 4, 12), al * 0.55, sigma=7))
                c.drawString(ch, cx, y + dy, f, paint(rgb, al, sigma=blur))
            cx += adv
