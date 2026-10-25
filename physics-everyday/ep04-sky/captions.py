"""Captions that are part of the picture: each word is laid out, and keywords behave (blue turns blue and bounces,
'white' shimmers through the rainbow, 'tiny' shrinks, 'red' flies straight off, 'scattering' scatters...).
Scenes can read the layout (word boxes in screen space) to make things interact with the words."""
import math

import skia

import kz as K

SIZE = 58
Y = 1650


class Word:
    def __init__(self, s, x, y, w, t0, idx):
        self.s, self.x, self.y, self.w, self.t0, self.idx = s, x, y, w, t0, idx

    @property
    def key(self):
        return self.s.lower().strip(".,?!:'\"")

    def box(self):
        return (self.x, self.y - SIZE * 0.78, self.x + self.w, self.y + SIZE * 0.22)


def layout(words, y=Y, size=SIZE, max_w=920):
    f = K.font(size, 900)
    space = f.measureText(" ")
    lines, cur, cw = [], [], 0
    for wd, t0 in words:
        w = f.measureText(wd)
        if cur and cw + space + w > max_w:
            lines.append(cur)
            cur, cw = [], 0
        cur.append((wd, w, t0))
        cw += (space if cw else 0) + w
    lines.append(cur)
    lh = size * 1.22
    top = y - lh * (len(lines) - 1) / 2
    out, idx = [], 0
    for li, ln in enumerate(lines):
        tw = sum(w for _, w, _ in ln) + space * (len(ln) - 1)
        x = K.W / 2 - tw / 2
        for wd, w, t0 in ln:
            out.append(Word(wd, x, top + li * lh, w, t0, idx))
            x += w + space
            idx += 1
    return out


COLOR_WORDS = {k: v for k, v in K.SPECTRUM}
COLOR_WORDS.update({"colour": None, "sunset": (255, 120, 80), "sunsets": (110, 160, 255), "mars": (230, 130, 80),
                    "butterscotch": (240, 180, 100), "white": (255, 255, 255), "sun": K.SUN_Y, "sunlight": K.SUN_Y,
                    "nitrogen": K.N2_C, "oxygen": K.O2_C, "atmosphere": (120, 190, 255), "sky": (130, 190, 255)})


def draw_word(c, wd, t, a, act, overrides=None):
    """Draw one word with its behaviour. overrides: dict(key -> callable(c, wd, t, a)) supplied by a scene."""
    key = wd.key
    since = t - wd.t0
    spoken = since >= 0
    f = K.font(SIZE, 900)
    base_a = a * (1.0 if spoken else 0.55)
    if overrides and key in overrides:
        if overrides[key](c, wd, t, base_a):
            return
    color = K.WHITE
    if spoken and key in COLOR_WORDS and COLOR_WORDS[key]:
        color = K.mix(K.WHITE, COLOR_WORDS[key], K.ss(since / 0.25))
    pop = 1.0 + 0.12 * math.exp(-max(0, since) * 8) * spoken
    c.save()
    cx, cy = wd.x + wd.w / 2, wd.y - SIZE * 0.3
    c.translate(cx, cy)
    c.scale(pop, pop)
    c.translate(-cx, -cy)
    if key == "white" and spoken:
        # a rainbow sweeps through the letters
        xs = wd.x
        for ch in wd.s:
            cw = f.measureText(ch)
            ph = (xs - wd.x) / max(wd.w, 1) - since * 1.2
            idx = int((ph % 1.0) * 6)
            cc = K.mix(K.WHITE, K.SPECTRUM[idx][1], 0.55 * math.exp(-max(0, since - 1.2) * 1.5))
            K.text(c, ch, xs, wd.y, SIZE, cc, base_a, "left", 900, 0.3)
            xs += cw
    elif key in ("tiny",) and spoken:
        s = K.lerp(1.0, 0.55, K.ob(since / 0.35))
        c.translate(cx, cy)
        c.scale(s, s)
        c.translate(-cx, -cy)
        K.text(c, wd.s, wd.x, wd.y, SIZE, color, base_a, "left", 900, 0.3)
    elif key in ("bigger", "forty") and spoken:
        s = K.lerp(1.0, 1.35, K.ob(min(1, since / 0.35))) - 0.15 * K.ss((since - 0.6) / 0.4)
        c.translate(cx, cy)
        c.scale(s, s)
        c.translate(-cx, -cy)
        K.text(c, wd.s, wd.x, wd.y, SIZE, (255, 220, 120), base_a, "left", 900, 0.3)
    elif key in ("waves", "wave") and spoken:
        xs = wd.x
        for i, ch in enumerate(wd.s):
            cw = f.measureText(ch)
            K.text(c, ch, xs, wd.y + 8 * math.sin(t * 8 - i * 0.9), SIZE, color, base_a, "left", 900, 0.3)
            xs += cw
    elif key in ("shakes",) and spoken:
        j = 5 * math.exp(-since * 2) + 1.5
        K.text(c, wd.s, wd.x + j * math.sin(t * 60), wd.y + j * math.cos(t * 53), SIZE, (255, 236, 140), base_a, "left", 900, 0.3)
    elif key in ("scattering", "scatter", "scattered") and spoken:
        xs = wd.x
        rr = K.rng("sc", wd.s, wd.idx)
        burst = K.ss(since / 0.4) * (1 - K.ss((since - 0.9) / 0.6))
        for i, ch in enumerate(wd.s):
            cw = f.measureText(ch)
            ang = rr.uniform(0, 6.3)
            d = 26 * burst * rr.uniform(0.5, 1.2)
            c.save()
            c.translate(xs + cw / 2 + d * math.cos(ang), wd.y - SIZE * 0.3 + d * math.sin(ang))
            c.rotate(25 * burst * rr.uniform(-1, 1))
            K.text(c, ch, -cw / 2, SIZE * 0.3, SIZE, (140, 190, 255), base_a, "left", 900, 0.3)
            c.restore()
            xs += cw
    elif key in ("long",) and spoken:
        s = K.lerp(1.0, 1.25, K.ob(min(1, since / 0.4)))
        c.translate(cx, cy)
        c.scale(s, 1 / s ** 0.3)
        c.translate(-cx, -cy)
        K.text(c, wd.s, wd.x, wd.y, SIZE, K.SPEC["red"], base_a, "left", 900, 0.3)
    elif key in ("short",) and spoken:
        s = K.lerp(1.0, 0.82, K.ob(min(1, since / 0.4)))
        c.translate(cx, cy)
        c.scale(s, 1.08)
        c.translate(-cx, -cy)
        K.text(c, wd.s, wd.x, wd.y, SIZE, K.SPEC["blue"], base_a, "left", 900, 0.3)
    elif key in ("direction", "everywhere") and spoken:
        xs = wd.x
        spread = 10 * K.ss(since / 0.3) * (1 - K.ss((since - 0.8) / 0.5))
        n = len(wd.s)
        for i, ch in enumerate(wd.s):
            cw = f.measureText(ch)
            K.text(c, ch, xs + (i - n / 2) * spread * 0.6, wd.y, SIZE, (150, 200, 255), base_a, "left", 900, 0.3)
            xs += cw
    else:
        K.text(c, wd.s, wd.x, wd.y, SIZE, color, base_a, "left", 900, 0.3)
    c.restore()
    if act and spoken and key not in ("white",):
        # spoken-word underline that slides in
        u = K.oc(since / 0.2)
        c.drawRoundRect(skia.Rect(wd.x, wd.y + 12, wd.x + wd.w * u, wd.y + 18), 3, 3,
                        skia.Paint(AntiAlias=True, Color=K.col(K.mix((255, 220, 120), color, 0.6), base_a * 0.9)))


def draw(c, words, t, a=1.0, overrides=None):
    act_i = max([w.idx for w in words if w.t0 <= t] or [-1])
    for wd in words:
        draw_word(c, wd, t, a, wd.idx == act_i, overrides)
