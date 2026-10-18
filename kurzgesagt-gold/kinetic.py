"""Kinetic captions: words that animate, move around the frame and react to what they mean.

Treatments (all stay inside the Shorts safe zones):
  pop      every word pops in (scale 60% -> 112% -> 100%, rises 24 px, blur-in), the spoken word turns gold
  anchor   each phrase sits in the free space of the shot (top band, beside the hero object, near Auri) and glides
           to the next anchor instead of always living at the bottom
  hero     key words / numbers ("GOLD", "4 METRES", "22 M") slam in huge as polished gold letters with a flash,
           a tiny camera shake and sparkles, then shrink back into the line
  react    some words act out their meaning: COLLIDE (two halves smash together), SANK (letters drop one by one),
           STEAM (letters puff and dissolve), EARTHQUAKE (letters shake), OLDER (letters age from shiny to warm)
  exit     phrases leave by drifting up and fading, never just vanishing
"""
import math

from gold import *  # noqa: F401,F403

INK = (24, 12, 0)


def _word(c, w, x, y, size, rgb, a, sc=1.0, rot=0.0, blur_=0.0):
    if a <= 1:
        return
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(sc, sc)
    if blur_ > 0.3:
        p = skia.Paint()
        p.setImageFilter(skia.ImageFilters.Blur(blur_, blur_))
        c.saveLayer(None, p)
    text(c, w, size * 0.03, size * 0.07, size, INK, 0.75 * a, 800)
    stroke_p = font(int(size), 800)
    text(c, w, 0, 0, size, rgb, a, 800)
    if blur_ > 0.3:
        c.restore()
    c.restore()


def gold_word(c, w, x, y, size, a=255, sc=1.0, t=0.0):
    """Hero word in polished gold letters (gradient fill + highlight band + dark outline + glow)."""
    if a <= 1:
        return
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    f = font(int(size), 800)
    wd = f.measureText(w)
    blob = skia.TextBlob.MakeFromString(w, f)
    light(c, 0, -size * 0.35, wd * 0.8, GOLD, 90 * a / 255)
    sh = skia.Paint(AntiAlias=True, Color=col(INK, 0.8 * a))
    c.drawTextBlob(blob, -wd / 2 + size * 0.04, size * 0.08, sh)
    st = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=size * 0.06, Color=col((90, 45, 10), a))
    c.drawTextBlob(blob, -wd / 2, 0, st)
    fp = skia.Paint(AntiAlias=True, Shader=linear((0, -size * 0.75), (0, size * 0.1), [GOLD_HI, GOLD, GOLD_MID, GOLD_HI], [0, 0.45, 0.7, 1]))
    fp.setAlphaf(a / 255)
    c.drawTextBlob(blob, -wd / 2, 0, fp)
    sweep = (t * 0.6) % 1.6 - 0.3
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(-wd / 2, -size, wd, size * 1.2))
    hp = skia.Paint(AntiAlias=True, Color=col(WHITE, 0.45 * a))
    hp.setBlendMode(skia.BlendMode.kSrcATop)
    c.restore()
    for k in range(3):
        sparkle4(c, -wd / 2 + wd * ((k * 0.37 + t * 0.2) % 1), -size * (0.4 + 0.3 * (k % 2)), size * 0.12 * (0.6 + 0.4 * math.sin(t * 5 + k)), 230 * a / 255)
    c.restore()


def phrase(c, words, x, y, t, t0, size=72, hi=None, word_dt=0.22, exit_t=None, max_w=860):
    """Pop-in phrase centred at (x, y); word i appears at t0 + i*word_dt; hi = index of the gold (spoken) word.
    Wraps onto two balanced lines and shrinks to fit inside the safe width."""
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
    ex = 0.0 if exit_t is None else smooth(prog(t, exit_t, exit_t + 0.35))
    lh = size * 1.12
    for li, ln in enumerate(lines):
        total = sum(ws[i] for i in ln) + gap * (len(ln) - 1)
        cx = x - total / 2
        ly = y + (li - (len(lines) - 1) / 2) * lh
        for i in ln:
            w, ww = words[i], ws[i]
            u = prog(t, t0 + i * word_dt, t0 + i * word_dt + 0.32)
            if u > 0:
                sc = 0.6 + 0.4 * out_back(u, 2.2)
                a = 255 * smooth(u) * (1 - ex)
                _word(c, w, cx + ww / 2, ly + 24 * (1 - out_cubic(u)) - 40 * ex, size, GOLD if i == hi else WHITE, a, sc, 0.0, 6 * (1 - u))
            cx += ww + gap


def hero(c, w, x, y, t, t0, size=200, settle=None):
    """Slam-in hero word; returns a small shake offset the caller can add to the camera."""
    u = prog(t, t0, t0 + 0.45)
    if u <= 0:
        return 0.0
    sc = lerp(2.4, 1.0, out_cubic(u)) * (1 + 0.06 * math.sin(math.pi * clamp((t - t0 - 0.45) / 0.25)))
    if settle:
        k = smooth(prog(t, settle, settle + 0.5))
        sc *= lerp(1.0, 0.42, k)
    gold_word(c, w, x, y, size, 255 * smooth(u * 2), sc, t)
    if t0 < t < t0 + 0.25:
        light(c, x, y - size * 0.3, size * 3, GOLD_HI, 160 * (1 - prog(t, t0, t0 + 0.25)))
    return 14 * math.exp(-max(0.0, t - t0 - 0.35) * 9) * (t > t0 + 0.35)


def react_collide(c, x, y, t, t0, size=110):
    """COLLIDE: COLL and IDE fly in from both sides and smash together with a flash."""
    u = in_cubic(prog(t, t0, t0 + 0.5))
    f = font(size, 800)
    a1, a2 = "COLL", "IDE"
    w1, w2 = f.measureText(a1), f.measureText(a2)
    _word(c, a1, x - w2 / 2 - lerp(700, 0, u), y, size, WHITE, 255 * smooth(prog(t, t0, t0 + 0.15)))
    _word(c, a2, x + w1 / 2 + lerp(700, 0, u), y, size, WHITE, 255 * smooth(prog(t, t0, t0 + 0.15)))
    if t > t0 + 0.5:
        k = prog(t, t0 + 0.5, t0 + 0.9)
        light(c, x, y - size * 0.3, 380, (255, 200, 120), 230 * (1 - k))
        for i in range(10):
            an = i / 10 * 6.28
            c.drawLine(x + math.cos(an) * 60, y - size * 0.3 + math.sin(an) * 60, x + math.cos(an) * (80 + 240 * k), y - size * 0.3 + math.sin(an) * (80 + 240 * k),
                       stroke(GOLD_HI, 6, 255 * (1 - k)))


def react_sank(c, x, y, t, t0, size=110, word="SANK"):
    """SANK: letters drop one by one with a little bounce."""
    f = font(size, 800)
    xs = x - f.measureText(word) / 2
    for i, ch in enumerate(word):
        cw = f.measureText(ch)
        u = prog(t, t0 + i * 0.12, t0 + i * 0.12 + 0.6)
        dy = 150 * out_back(u, 1.5)
        _word(c, ch, xs + cw / 2, y + dy, size, GOLD if u > 0.6 else WHITE, 255 * smooth(prog(t, t0 - 0.2, t0)))
        xs += cw


def react_steam(c, x, y, t, t0, size=110, word="STEAM"):
    """STEAM: letters rise, wobble and dissolve into puffs."""
    f = font(size, 800)
    xs = x - f.measureText(word) / 2
    for i, ch in enumerate(word):
        cw = f.measureText(ch)
        u = prog(t, t0 + i * 0.08, t0 + i * 0.08 + 1.4)
        rise = 160 * u
        wob = 18 * math.sin(t * 6 + i) * u
        _word(c, ch, xs + cw / 2 + wob, y - rise, size, WHITE, 255 * (1 - smooth(prog(u, 0.45, 1.0))), 1 + 0.25 * u, wob * 0.4, 14 * smooth(prog(u, 0.3, 1.0)))
        if u > 0.3:
            c.drawCircle(xs + cw / 2 + wob, y - rise - size * 0.4, size * 0.5 * u, fill(WHITE, 60 * (1 - u)))
        xs += cw


def react_shake(c, x, y, t, t0, size=110, word="EARTHQUAKE"):
    """EARTHQUAKE: letters jitter independently, decaying."""
    f = font(size, 800)
    xs = x - f.measureText(word) / 2
    amp = 16 * math.exp(-max(0.0, t - t0) * 1.6) * (t > t0)
    for i, ch in enumerate(word):
        cw = f.measureText(ch)
        dx, dy = amp * math.sin(t * 61 + i * 2.1), amp * math.cos(t * 53 + i * 1.7)
        _word(c, ch, xs + cw / 2 + dx, y + dy, size, (255, 170, 130), 255 * smooth(prog(t, t0 - 0.2, t0)), 1.0, dx * 0.6)
        xs += cw
