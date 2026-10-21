"""Glass captions.

  * a phrase (max 3 words) sits on a small frosted-glass pill that blurs whatever is behind it
  * each word focus-pulls in as it is spoken: blurred and a little low, then sharp
  * the word being spoken swells slightly with the loudness of the voice (envelope of the real narration audio)
  * emphasis words: amber (you, your phone, the signal) or violet (time, clocks, Einstein) with a soft glow
  * a phrase leaves by blurring out as the pill shrinks away
"""
import os, re

import numpy as np
import soundfile as sf

import glass
from glass import mask, layer, over, rrect
from kit import AMBER, PAPER, SMOKE, VIOLET, W, clamp, font, mix, out_cubic, paint, prog, smooth, width
from project import P
from script import DISPLAY
from timing import vo_dir


def lerp(a, b, u):
    return a + (b - a) * u


def _clean(w):
    return re.sub(r"[^\w'%°.,\-]", "", w).strip(".,").lower()


def displayed(items):
    """Merge spoken number words into what the captions show: [(t0, t1, "thirty"), (.., "eight")] ->
    [(t0, t1, "38")], keeping the trailing punctuation of the last spoken word."""
    out, i = [], 0
    while i < len(items):
        for spoken, shown in DISPLAY:
            sw = spoken.lower().split()
            seg = items[i:i + len(sw)]
            if len(seg) == len(sw) and all(_clean(a[2]) == b.strip(".,") for a, b in zip(seg, sw)):
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
    words    words drawn in amber (lower-case, no punctuation); model: the same in violet
    anchors  {line_key: (x, y)} centre of the caption (default y from project.json, above the Shorts UI)
    hide     {line_key: [(t0, t1)]} windows where captions are suppressed (a title says it instead)
    """

    def __init__(self, tm, env=None, words=(), model=(), anchors=None, hide=None, size=None, max_words=None,
                 max_chars=20, skip=()):
        cfg = P["style"]["captions"]
        size, max_words = size or cfg["size"], max_words or cfg["max_words"]
        self.size, self.env = size, env
        self.colour = {**{w: AMBER for w in words}, **{w: VIOLET for w in model}}
        self.hide = hide or {}
        self.phrases = []
        for k in tm.vo:
            if k in skip:
                continue
            ax, ay = (anchors or {}).get(k, (W / 2, cfg["y"]))
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
            p["t1"] = min(p["words"][-1]["t1"] + 0.6, nxt - 0.22)

    def _layout(self, k, g, ax, ay):
        words = []
        for a, b, w in g:
            rgb = self.colour.get(_clean(w))
            txt = w.rstrip(",;:") if not w.endswith((".", "?", "!")) else w
            words.append(dict(t0=a, t1=b, text=txt, rgb=rgb, w=width(txt, "semibold", self.size)))
        space = self.size * 0.28
        total = sum(x["w"] for x in words) + space * (len(words) - 1)
        lines = [words]
        if total > 860 and len(words) > 1:
            best = min(range(1, len(words)), key=lambda i: abs(sum(x["w"] for x in words[:i]) - total / 2))
            lines = [words[:best], words[best:]]
        lh = self.size * 1.12
        y0 = ay - (len(lines) - 1) * lh / 2
        widest = 0
        for li, ln in enumerate(lines):
            lw = sum(x["w"] for x in ln) + space * (len(ln) - 1)
            widest = max(widest, lw)
            x = ax - lw / 2
            for wd in ln:
                wd["x"], wd["y"] = x, y0 + li * lh
                x += wd["w"] + space
        padx, pady = self.size * 0.46, self.size * 0.30
        box = (ax - widest / 2 - padx, y0 - self.size * 0.84 - pady, widest + 2 * padx,
               (len(lines) - 1) * lh + self.size * 1.10 + 2 * pady)
        return dict(key=k, t0=words[0]["t0"] - 0.08, words=words, box=box)

    def visible(self, t):
        for p in self.phrases:
            if t < p["t0"] - 0.05 or t > p["t1"] + 0.3:
                continue
            if any(a0 <= t <= a1 for a0, a1 in self.hide.get(p["key"], ())):
                continue
            yield p

    def draw(self, img, t, a=1.0):
        for p in self.visible(t):
            img = self._phrase(img, p, t, a)
        return img

    def _phrase(self, img, p, t, a):
        enter = out_cubic(prog(t, p["t0"] - 0.05, p["t0"] + 0.2))
        leave = smooth(prog(t, p["t1"], p["t1"] + 0.28))
        k = enter * (1 - leave) * a
        if k <= 0.01:
            return img
        x, y, w, h = p["box"]
        s = 0.86 + 0.14 * k
        # single-line phrases: the pill grows to the right as words arrive
        if len({wd["y"] for wd in p["words"]}) == 1:
            pad = x - p["words"][0]["x"]
            right = p["words"][0]["x"] + p["words"][0]["w"]
            for wd in p["words"][1:]:
                q = out_cubic(prog(t, wd["t0"] - 0.12, wd["t0"] + 0.12))
                right = max(right, lerp(right, wd["x"] + wd["w"], q))
            w = right - x - pad
        cx, cy = x + w / 2, y + h / 2
        bw, bh = w * s, h * s
        m = mask(lambda c, pt: c.drawRRect(rrect(cx - bw / 2, cy - bh / 2, bw, bh, bh / 2), pt)) * k
        img = glass.glass(img, m, bevel=14, refract=10, frost=18, tint=0.5, lift=4, rim=1.0, shade=0.2)

        def words(c):
            for wd in p["words"]:
                u = prog(t, wd["t0"] - 0.08, wd["t0"] + 0.18)
                if u <= 0:
                    continue
                speaking = wd["t0"] - 0.05 <= t <= wd["t1"] + 0.08
                swell = 1.0 + (0.05 * self.env(t) if self.env and speaking else 0.0)
                sz = self.size * swell
                f = font("semibold", sz)
                x0 = wd["x"] - wd["w"] * (swell - 1) / 2
                yy = wd["y"] + (1 - out_cubic(u)) * 14
                blur = (1 - smooth(u)) * 9 + leave * 10
                al = 255 * smooth(u) * k
                rgb = wd["rgb"] or (PAPER if speaking or t < wd["t1"] else mix(PAPER, SMOKE, 0.25))
                if wd["rgb"]:
                    c.drawString(wd["text"], x0, yy, f, paint(rgb, al * 0.55, sigma=14))
                c.drawString(wd["text"], x0, yy, f, paint(rgb, al, sigma=blur if blur > 0.3 else 0))
        return over(img, layer(words))
