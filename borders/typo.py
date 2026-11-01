"""Typography and the caption system.

Caption treatment:
  * each word appears as it is spoken; its letters rise out of a soft blur with a small spring settle, staggered
  * the word being spoken is full white, spoken words settle to grey; emphasis words switch to the tall condensed
    display face, upper case, in the act's accent colour with a faint glow (only a few per line)
  * a phrase leaves by drifting up and blurring out, word by word
  * numbers can roll in like an odometer (Counter)
"""
import math, os, re

import skia

from engine import H, HERE, W, clamp, fill, prog, smooth

FONTS = {
    "regular": "Atkinson-Regular.ttf", "medium": "Atkinson-Regular.ttf", "semibold": "Atkinson-Bold.ttf",
    "bold": "Atkinson-Bold.ttf", "black": "BigShoulders-Black.ttf", "serif": "BigShoulders-Black.ttf",
    "display": "BigShoulders-Black.ttf", "mono": "MartianMono-Regular.ttf", "mono_bold": "MartianMono-Bold.ttf",
    "overpass": "Overpass-800.ttf", "overpass_black": "Overpass-900.ttf", "bungee": "Bungee-400.ttf",
    "bungee_shade": "BungeeShade-400.ttf", "marker": "PermanentMarker-400.ttf",
    "vt": "VT323-Regular.ttf", "shrik": "Shrikhand.ttf", "archivo": "ArchivoBlack.ttf", "righteous": "Righteous.ttf",
    "bowlby": "BowlbyOne.ttf",
}
_TF, _F = {}, {}

PAPER = (236, 238, 247)        # cool off-white text
ASH = (149, 155, 184)          # spoken / secondary text
EMBER = (255, 77, 109)         # alarm red (act 3); each act passes its own accent to Captions


def font(kind, size):
    key = (kind, round(size, 1))
    if key not in _F:
        if kind not in _TF:
            _TF[kind] = skia.Typeface.MakeFromFile(os.path.join(HERE, "fonts", FONTS[kind]))
        f = skia.Font(_TF[kind], size)
        f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
        f.setSubpixel(True)
        _F[key] = f
    return _F[key]


def width(s, kind, size, tracking=0.0):
    f = font(kind, size)
    return sum(f.measureText(ch) for ch in s) + tracking * size * max(0, len(s) - 1)


def paint(rgb, a=255, sigma=0.0, plus=False):
    p = skia.Paint(AntiAlias=True, Color=skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(clamp(a / 255) * 255)))
    if sigma > 0.25:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    if plus:
        p.setBlendMode(skia.BlendMode.kPlus)
    return p


def label(c, s, x, y, size, kind="medium", rgb=PAPER, a=255, align="left", tracking=0.0, sigma=0.0):
    """Static text line. tracking is in em (0.1 = 10% of the size between letters)."""
    if a <= 1:
        return
    f = font(kind, size)
    w = width(s, kind, size, tracking)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    p = paint(rgb, a, sigma)
    if not tracking:
        c.drawString(s, x0, y, f, p)
        return
    for ch in s:
        c.drawString(ch, x0, y, f, p)
        x0 += f.measureText(ch) + tracking * size


def spring(u, k=7.0, w=10.0):
    """0 -> 1 with a small overshoot."""
    u = clamp(u)
    return 1 - math.exp(-k * u) * math.cos(w * u)


def reveal(c, s, x, y, size, t, t0, kind="semibold", rgb=PAPER, a=255, align="left", tracking=0.0, stagger=0.022,
           dur=0.5, rise=0.42, blur=11.0, shadow=True, outline=0.0):
    """Text whose letters rise out of a blur, one after another, starting at t0. outline = dark stroke width."""
    if t < t0 - 0.02 or a <= 1:
        return
    f = font(kind, size)
    w = width(s, kind, size, tracking)
    cx = x - w / 2 if align == "center" else x - w if align == "right" else x
    glyphs = []
    for i, ch in enumerate(s):
        u = prog(t, t0 + i * stagger, t0 + i * stagger + dur)
        if u > 0 and ch != " ":
            glyphs.append((ch, cx, y + size * rise * (1 - spring(u)), blur * (1 - smooth(u)) ** 2, a * smooth(clamp(u * 1.8))))
        cx += f.measureText(ch) + tracking * size
    # all shadows, then all outlines, then all fills, so no letter's outline cuts into its neighbour
    if shadow:
        for ch, gx, gy, sg, al in glyphs:
            c.drawString(ch, gx, gy + size * 0.06, f, paint((0, 0, 0), al * 0.6, 7 + sg))
    if outline > 0:
        for ch, gx, gy, sg, al in glyphs:
            op = paint((6, 6, 14), al * 0.92, sg)
            op.setStyle(skia.Paint.kStroke_Style)
            op.setStrokeWidth(outline)
            op.setStrokeJoin(skia.Paint.kRound_Join)
            c.drawString(ch, gx, gy, f, op)
    for ch, gx, gy, sg, al in glyphs:
        c.drawString(ch, gx, gy, f, paint(rgb, al, sg))


def _clean(w):
    return re.sub(r"[^\w'%°.,\-]", "", w).strip(".,").lower()


class Captions:
    """Word-synced captions for one part.

    tm       timing.Timing for the part
    anchors  {line_key: (x, y)} centre of the caption block for that line (default lower third)
    emph     words drawn in the accent display face (lower-case, no punctuation)
    hide     {line_key: [(t0, t1)]} windows where captions are suppressed (a big on-screen title says it instead)
    """

    def __init__(self, tm, anchors=None, emph=(), hide=None, size=88, max_words=3, max_chars=17, skip=(), accent=EMBER):
        self.size, self.emph, self.accent = size, set(emph), accent
        self.hide = hide or {}
        self.phrases = []
        for k in tm.vo:
            if k in skip:
                continue
            ax, ay = (anchors or {}).get(k, (W / 2, 1400))
            cur, groups = [], []
            for item in tm.words(k):
                cur.append(item)
                text_len = len(" ".join(x[2] for x in cur))
                if len(cur) >= max_words or item[2][-1] in ".,?!:;" or text_len > max_chars:
                    groups.append(cur)
                    cur = []
            if cur:
                groups.append(cur)
            for g in groups:
                self.phrases.append(self._layout(k, g, ax, ay))
        self.phrases.sort(key=lambda p: p["t0"])
        for i, p in enumerate(self.phrases):
            nxt = self.phrases[i + 1]["t0"] if i + 1 < len(self.phrases) else p["words"][-1]["t1"] + 1.2
            p["t1"] = min(p["words"][-1]["t1"] + 0.7, nxt - 0.34)

    def _layout(self, k, g, ax, ay):
        words = []
        for a, b, w in g:
            e = _clean(w) in self.emph
            kind = "serif" if e else "semibold"
            sz = self.size * (1.3 if e else 1.0)
            txt = w.rstrip(",;:") if not w.endswith((".", "?", "!")) else w
            if e:
                txt = txt.upper()
            words.append(dict(t0=a, t1=b, text=txt, emph=e, kind=kind, size=sz, w=width(txt, kind, sz)))
        space = self.size * 0.27
        total = sum(x["w"] for x in words) + space * (len(words) - 1)
        lines = [words]
        if total > 920 and len(words) > 1:            # two lines, split near the middle
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

    def draw(self, c, t):
        """Spoken word: full white and a quick scale pop. Spoken words settle slightly dimmer. Emphasis words: accent
        colour, display face, glow. Every word has a dark outline and shadow so it reads over any picture."""
        for p in self.phrases:
            if t < p["t0"] - 0.05 or t > p["t1"] + 0.4:
                continue
            if any(a <= t <= b for a, b in self.hide.get(p["key"], ())):
                continue
            drift = -8 * prog(t, p["t0"], p["t1"])
            for i, wd in enumerate(p["words"]):
                ex = prog(t, p["t1"] + i * 0.03, p["t1"] + i * 0.03 + 0.2)      # exit: drift up + blur out
                if ex >= 1 or t < wd["t0"] - 0.08:
                    continue
                speaking = wd["t0"] - 0.05 <= t <= wd["t1"] + 0.08
                rgb = PAPER if speaking else (212, 216, 232)
                if wd["emph"]:
                    rgb = tuple(min(255, v + 35) for v in self.accent) if speaking else self.accent
                a = 255 * (1 - smooth(ex))
                y = wd["y"] + drift - 26 * smooth(ex)
                ol = wd["size"] * 0.11
                if ex > 0:
                    f = font(wd["kind"], wd["size"])
                    op = paint((6, 6, 14), a * 0.9, 9 * ex)
                    op.setStyle(skia.Paint.kStroke_Style)
                    op.setStrokeWidth(ol)
                    c.drawString(wd["text"], wd["x"], y, f, op)
                    c.drawString(wd["text"], wd["x"], y, f, paint(rgb, a, 9 * ex))
                    continue
                u = prog(t, wd["t0"] - 0.06, wd["t0"] + 0.3)
                sc = 1.0 + (0.2 if wd["emph"] else 0.1) * (1 - spring(u, 9.0, 12.0))       # pop as it is spoken
                cx, cy = wd["x"] + wd["w"] / 2, y - wd["size"] * 0.34
                c.save()
                c.translate(cx, cy)
                c.scale(sc, sc)
                c.translate(-cx, -cy)
                if wd["emph"] and t > wd["t0"]:
                    gl = smooth(prog(t, wd["t0"], wd["t0"] + 0.35))
                    label(c, wd["text"], wd["x"], y, wd["size"], wd["kind"], self.accent, 120 * gl, sigma=18)
                reveal(c, wd["text"], wd["x"], y, wd["size"], t, wd["t0"] - 0.06, wd["kind"], rgb, a,
                       stagger=0.014 if wd["emph"] else 0.01, dur=0.32, rise=0.3, outline=ol)
                c.restore()


class Counter:
    """Odometer number: every digit rolls up to its value; the last digits spin longest. Non-digits stay put."""

    def __init__(self, value_text, size, kind="mono_bold"):
        self.s, self.size, self.kind = value_text, size, kind
        f = font(kind, size)
        self.adv = {ch: f.measureText(ch) for ch in set(value_text) | set("0123456789")}
        self.dw = max(self.adv[d] for d in "0123456789")

    def width(self, tracking=0.0):
        return sum(self.dw if ch.isdigit() else self.adv[ch] for ch in self.s) + tracking * self.size * (len(self.s) - 1)

    def draw(self, c, x, y, t, t0, dur=1.6, rgb=PAPER, a=255, align="left", tracking=0.0):
        if t < t0 - 0.02 or a <= 1:
            return
        f = font(self.kind, self.size)
        wtot = self.width(tracking)
        cx = x - wtot / 2 if align == "center" else x - wtot if align == "right" else x
        digits = [i for i, ch in enumerate(self.s) if ch.isdigit()]
        al = a * smooth(prog(t, t0, t0 + 0.2))
        for i, ch in enumerate(self.s):
            if not ch.isdigit():
                c.drawString(ch, cx, y, f, paint(rgb, al))
                cx += self.adv[ch] + tracking * self.size
                continue
            rank = digits.index(i)
            d_end = t0 + dur * (0.55 + 0.45 * (rank + 1) / len(digits))
            u = prog(t, t0, d_end)
            e = 1 - (1 - u) ** 3                          # ease out
            spins = 1 + rank // 2
            pos = (int(ch) + 10 * spins) * e               # rolling position in digit units
            speed = (int(ch) + 10 * spins) * 3 * (1 - u) ** 2 / max(d_end - t0, 0.1)
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(cx - 4, y - self.size * 0.8, cx + self.dw + 4, y + self.size * 0.14))
            base = math.floor(pos)
            frac = pos - base
            for k in (-1, 0, 1):
                dig = (base + k) % 10
                yy = y + (k - frac) * self.size * 1.0
                sg = min(10, speed * 0.6)
                dx = (self.dw - self.adv[str(dig)]) / 2
                c.drawString(str(dig), cx + dx, yy, f, paint(rgb, al, sg))
            c.restore()
            cx += self.dw + tracking * self.size
