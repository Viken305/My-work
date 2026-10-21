"""Denoise-in captions.

  * each word starts as a patch of colour static the size of the word and resolves into sharp letters as it is spoken
    (noise fades out on the same cosine schedule the picture uses, letters sharpen with a small jitter that settles)
  * the word being spoken swells slightly with the loudness of the voice (envelope of the real narration audio)
  * emphasis words switch to the serif italic in amber (your words) or violet (the model) with one scan-line sweep
  * a phrase leaves by dissolving back into grain, left to right
"""
import math, os, re

import numpy as np
import soundfile as sf
import skia

from kit import AMBER, PAPER, VIOLET, W, clamp, font, mix, out_cubic, paint, prog, smooth, spring, width
from project import P
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
    words    words drawn in the amber serif italic (lower-case, no punctuation); model: the same in violet
    anchors  {line_key: (x, y)} centre of the caption block (default y = 1380, above the Shorts UI)
    hide     {line_key: [(t0, t1)]} windows where captions are suppressed (a title says it instead)
    """

    def __init__(self, tm, env=None, words=(), model=(), anchors=None, hide=None, size=None, max_words=None, max_chars=18, skip=()):
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
        rgb = wd["rgb"] or (PAPER if speaking or t < wd["t1"] else mix(PAPER, (150, 147, 160), 0.45))
        f = font(wd["kind"], wd["size"] * swell)
        x0, y = wd["x"] - wd["w"] * (swell - 1) / 2, wd["y"]
        sz = wd["size"]
        box = skia.Rect.MakeXYWH(x0 - 8, y - sz * 0.86, wd["w"] + 16, sz * 1.12)
        if ex > 0:   # exit: letters dissolve into grain, left to right
            cx = x0
            for j, ch in enumerate(wd["text"]):
                u = clamp(ex * 1.6 - j / max(1, len(wd["text"])) * 0.6)
                adv = f.measureText(ch)
                c.drawString(ch, cx, y, f, paint(rgb, 255 * a * (1 - u) ** 1.5, sigma=6 * u))
                if 0 < u < 1:
                    _static(c, skia.Rect.MakeXYWH(cx, y - sz * 0.8, adv, sz), 150 * a * math.sin(math.pi * u), int(t * 30) + j)
                cx += adv
            return
        u0 = t - (wd["t0"] - 0.06)
        if u0 < 0:
            return
        k = clamp(u0 / 0.32)                 # 0 = pure static, 1 = clean letters
        nz = math.cos(k * math.pi / 2) ** 2
        if nz > 0.01:
            _static(c, box, 235 * a * nz * smooth(u0 / 0.06), int(t * 30) + int(wd["x"]))
        if wd["rgb"] and u0 < 0.9:   # one scan-line sweep + glow behind emphasis words
            q = out_cubic(clamp((u0 - 0.15) / 0.55))
            sx = x0 - 10 + (wd["w"] + 20) * q
            c.drawRect(skia.Rect.MakeXYWH(sx - 2, y - sz * 0.95, 4, sz * 1.25), paint(wd["rgb"], 220 * a * (1 - q), sigma=3, plus=True))
            c.drawRect(skia.Rect.MakeXYWH(sx - 18, y - sz * 0.95, 36, sz * 1.25), paint(wd["rgb"], 70 * a * (1 - q), sigma=14, plus=True))
        if wd["rgb"]:
            c.drawRRect(skia.RRect.MakeRectXY(box, 20, 20), paint(wd["rgb"], 26 * a * smooth(u0 / 0.4), sigma=24))
        rng = np.random.default_rng(int(wd["x"] * 7 + wd["y"]))
        jit = rng.normal(0, 1, (len(wd["text"]), 2))
        cx = x0
        for j, ch in enumerate(wd["text"]):
            adv = f.measureText(ch)
            if ch != " ":
                kk = clamp((u0 - j * 0.012) / 0.32)
                jj = (1 - spring(kk, 9, 14)) * 10
                al = (0.15 + 0.85 * smooth(kk)) * 255 * a
                dx, dy = jit[j] * jj
                c.drawString(ch, cx + 3, y + 5, f, paint((0, 0, 0), al * 0.5, sigma=7))
                c.drawString(ch, cx + dx, y + dy, f, paint(rgb, al, sigma=(1 - kk) * 7))
            cx += adv


_NOISE = []


def _static(c, rect, a, seed):
    """Colour TV static clipped to a rounded rect."""
    if a <= 1:
        return
    if not _NOISE:
        r = np.random.default_rng(5)
        for _ in range(8):
            n = np.clip(128 + r.normal(0, 70, (640, 360, 3)), 0, 255).astype(np.uint8)
            rgba = np.dstack([n, np.full((640, 360), 255, np.uint8)])
            _NOISE.append(skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType))
    img = _NOISE[seed % 8]
    p = skia.Paint()
    p.setAlphaf(clamp(a / 255))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(rect, 10, 10), doAntiAlias=True)
    sw, sh = min(360, rect.width() / 3), min(640, rect.height() / 3)
    ox, oy = (seed * 37) % int(361 - sw), (seed * 53) % int(641 - sh)
    src = skia.Rect.MakeXYWH(ox, oy, sw, sh)
    c.drawImageRect(img, src, rect, skia.SamplingOptions(skia.FilterMode.kNearest), p)
    c.restore()
