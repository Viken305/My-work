"""Ink captions that live on the drum paper.

  * each word soaks into the paper as it is spoken (soft ink spread -> crisp glyph) with a small spring settle
  * the trace shakes them: jitter follows a scene's shake(t) (the seismogram envelope); calm voice, steady text
  * the word being spoken swells slightly with the loudness of the voice
  * emphasis words switch to the serif italic in the colour of what they mean (red quake, teal water, bronze ring)
    and get a hand-inked wavy underline that draws in
  * a phrase leaves upward, like paper feeding past the pen
"""
import math, os, re

import numpy as np
import soundfile as sf
import skia

from ink import BONE, INK, FPS, W, clamp, font, ink, out_expo, paint, prog, smooth, spring, width
from script import DISPLAY
from timing import vo_dir

SHADOW = (40, 30, 20)


def _clean(w):
    return re.sub(r"[^\w'%°.,\-:]", "", w).strip(".,").lower()


def displayed(items):
    """Merge spoken number words into what the captions show, keeping the trailing punctuation."""
    out, i = [], 0
    while i < len(items):
        for spoken, shown in DISPLAY:
            sw = spoken.lower().split()
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

    colours  {word (lower case, no punctuation): rgb} emphasis words
    anchors  {line_key: (x, y)} centre of the caption block (default y = 1400)
    hide     {line_key: [(t0, t1)]} windows where a special caption replaces the normal one
    """

    def __init__(self, tm, env=None, colours=None, anchors=None, hide=None, size=78, max_words=3, max_chars=20,
                 skip=()):
        self.size, self.env = size, env
        self.colour = colours or {}
        self.hide = hide or {}
        self.phrases = []
        for k in tm.vo:
            if k in skip:
                continue
            ax, ay = (anchors or {}).get(k, (W / 2, 1400))
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
            p["t1"] = min(p["words"][-1]["t1"] + 0.7, nxt - 0.28)

    def _layout(self, k, g, ax, ay):
        words = []
        for a, b, w in g:
            rgb = self.colour.get(_clean(w).strip(".,!?"))
            kind = "serif_bold" if rgb else "bold"
            sz = self.size * (1.16 if rgb else 1.0)
            txt = w.rstrip(",;:") if not w.endswith((".", "?", "!")) else w
            txt = txt.rstrip(".") if not txt.endswith("..") else txt
            words.append(dict(t0=a, t1=b, text=txt, rgb=rgb, kind=kind, size=sz, w=width(txt, kind, sz)))
        space = self.size * 0.28
        total = sum(x["w"] for x in words) + space * (len(words) - 1)
        lines = [words]
        if total > 900 and len(words) > 1:
            best = min(range(1, len(words)), key=lambda i: abs(sum(x["w"] for x in words[:i]) - total / 2))
            lines = [words[:best], words[best:]]
        lh = self.size * 1.2
        y0 = ay - (len(lines) - 1) * lh / 2
        for li, ln in enumerate(lines):
            lw = sum(x["w"] for x in ln) + space * (len(ln) - 1)
            x = ax - lw / 2
            for wd in ln:
                wd["x"], wd["y"] = x, y0 + li * lh
                x += wd["w"] + space
        x0 = min(w["x"] for w in words)
        x1 = max(w["x"] + w["w"] for w in words)
        return dict(key=k, t0=words[0]["t0"] - 0.05, words=words, box=(x0, y0 - self.size, x1, y0 + (len(lines) - 1) * lh + self.size * 0.4))

    def hidden(self, key, t):
        return any(a0 <= t <= a1 for a0, a1 in self.hide.get(key, ()))

    def draw(self, c, t, shake=None, a=1.0, plate=True):
        amp = shake(t) if shake else 0.0
        rng = np.random.default_rng(int(t * FPS * 3) + 11)
        for p in self.phrases:
            if t < p["t0"] - 0.05 or t > p["t1"] + 0.45 or self.hidden(p["key"], t):
                continue
            ex_all = smooth(prog(t, p["t1"], p["t1"] + 0.4))
            if plate:   # soft paper wash so the words read over any drawing
                x0, y0, x1, y1 = p["box"]
                pa = smooth(prog(t, p["t0"] - 0.05, p["t0"] + 0.25)) * (1 - ex_all)
                c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0 - 40, y0 - 10, x1 + 40, y1 + 24), 34, 34),
                            paint(BONE, 210 * pa * a, sigma=22))
            for i, wd in enumerate(p["words"]):
                ex = smooth(prog(t, p["t1"] + i * 0.035, p["t1"] + i * 0.035 + 0.3))
                if ex >= 1:
                    continue
                self._word(c, t, wd, ex, a, amp, rng)

    def _word(self, c, t, wd, ex, a, amp, rng):
        speaking = wd["t0"] - 0.05 <= t <= wd["t1"] + 0.08
        swell = 1.0 + (0.045 * self.env(t) if self.env and speaking else 0.0)
        rgb = wd["rgb"] or INK
        f = font(wd["kind"], wd["size"] * swell)
        x0, y = wd["x"] - wd["w"] * (swell - 1) / 2, wd["y"]
        u0 = t - (wd["t0"] - 0.06)
        if u0 < 0:
            return
        al_word = 1 - ex
        dy_exit = -46 * ex
        if wd["rgb"]:   # hand-inked underline drawing in under emphasis words
            q = out_expo(u0 / 0.45)
            pth = skia.Path()
            pth.moveTo(x0, y + wd["size"] * 0.2)
            for j in range(1, 33):
                uu = j / 32 * q
                pth.lineTo(x0 + wd["w"] * uu, y + wd["size"] * 0.2 + math.sin(uu * 20 + wd["x"]) * 2.4 + dy_exit)
            ink(c, pth, wd["rgb"], 230 * a * al_word, 3.0)
        jit = amp * (1.6 if speaking else 0.7)
        cx = x0
        for j, ch in enumerate(wd["text"]):
            u = (u0 - j * 0.024) / 0.5
            adv = f.measureText(ch)
            if u > 0 and ch != " ":
                dy = -(1 - spring(u, 8, 11)) * 22 + dy_exit
                al = clamp(u * 3) * 255 * a * al_word
                blur = (1 - clamp(u * 2.4)) * 7 + ex * 6
                dx, ddy = (rng.normal(0, jit, 2) if jit > 0.05 else (0.0, 0.0))
                rot = rng.normal(0, jit * 0.45) if jit > 0.05 else 0.0
                c.save()
                c.translate(cx + dx, y + dy + ddy)
                if rot:
                    c.rotate(rot)
                c.drawString(ch, 2, 4, f, paint(SHADOW, al * 0.22, sigma=5))
                if blur > 0.3:
                    c.drawString(ch, 0, 0, f, paint(rgb, al * 0.5, sigma=blur * 1.6))
                c.drawString(ch, 0, 0, f, paint(rgb, al, sigma=blur * 0.35))
                c.restore()
            cx += adv
