"""Part 2, reading your words: the prompt box comes forward; the sentence snaps apart into token chips that spring
into rows; the "cat" chip unfolds into 768 numbers (violet barcode, counter); the barcode collapses into a point
that flies into a slowly orbiting map of meaning, where cat lands by kitten and moon by planet.

  python3 render.py part2 [--still 2,6,10,14,16,19]
"""
import zlib

from film import *  # noqa: F401,F403

PART = "part2"
VO, _end = schedule(PART)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)
DURATION = _end + 0.6

WORDS_T = TM.word("A1", "words")
CHOP_T = TM.word("A2", "chops")
TURN_T = TM.word("A2", "turns")
NUM_T0, NUM_T1 = TM.word("A2", "list"), TM.word("A2", "eight", end=True)
MAP_T = VO["A3"]
CAT_T, KIT_T = TM.word("A3", "Cat"), TM.word("A3", "kitten.")
MOON_T, PLAN_T = TM.word("A3", "Moon"), TM.word("A3", "planet.")
KNOWS_T = TM.word("A3", "That's")

CAPS = Captions(TM, ENV, words=WORDS, model=MODEL)
BOX_X, BOX_Y, BOX_W, FS = 90, 560, 900, 46
EMB = art.embedding("cat")
GROUPS = {"ANIMALS": ["cat", "kitten", "tiger", "dog", "puppy"], "SPACE": ["moon", "planet", "mars", "star", "astronaut", "rocket"],
          "VEHICLES": ["bicycle", "car", "train"], "PLACES": ["paris", "london", "city"], "FOOD": ["pizza", "apple", "bread"]}


def token_slots():
    """Where each token sits inside the typed sentence (same wrapping as kit.prompt_box) and in the chip rows."""
    text, lines, cur = art.PROMPT, [], ""
    for wd in text.split(" "):
        if width(cur + " " + wd, "mono", FS) > BOX_W - 70 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    src, li, pos = [], 0, 0
    for tk in art.TOKENS:
        while True:
            ln = lines[li]
            j = ln.find(tk, pos)
            if j >= 0 and (tk == "," or j == pos or ln[pos:j].strip() == ""):
                break
            li, pos = li + 1, 0
        x = BOX_X + 34 + width(ln[:j], "mono", FS)
        y = BOX_Y + 30 + FS + li * FS * 1.35
        src.append((x, y - FS * 1.2))
        pos = j + len(tk)
    dst, x, y = [], 90, 620
    for tk in art.TOKENS:
        wd = width(tk, "mono_bold", 40) + 40
        if x + wd > 990:
            x, y = 90, y + 104
        dst.append((x, y))
        x += wd + 18
    return src, dst


SRC, DST = token_slots()
CAT_I = art.TOKENS.index("cat")


def map_xy(word, t):
    """Pseudo-3D meaning map: hand-placed 2D positions plus a depth, slowly orbiting."""
    x, y = art.MEANING[word]
    z = ((zlib.crc32(word.encode()) % 1000) / 1000 - 0.5) * 0.6
    a = 0.35 * math.sin((t - MAP_T) * 0.25) - 0.1
    X = (x - 0.5) * math.cos(a) + z * math.sin(a)
    Z = -(x - 0.5) * math.sin(a) + z * math.cos(a)
    sc = 1 / (1.4 - Z)
    return W / 2 + X * 1250 * sc, 860 + (y - 0.5) * 1150 * sc, sc


def draw_tokens(c, t):
    q = prog(t, CHOP_T - 0.1, CHOP_T + 1.6)
    if q <= 0:
        return
    focus = smooth(prog(t, TURN_T - 0.2, TURN_T + 0.4))
    gone = smooth(prog(t, MAP_T - 0.2, MAP_T + 0.4))
    for i, tk in enumerate(art.TOKENS):
        u = back_out(prog(q, i * 0.035, i * 0.035 + 0.45), 1.3)
        (x0, y0), (x1, y1) = SRC[i], DST[i]
        x, y = lerp(x0, x1, u), lerp(y0, y1, u) - 40 * math.sin(math.pi * clamp(u)) * (1 if i % 2 else -0.5)
        if i == CAT_I:
            x, y = lerp(x, 90, focus), lerp(y, 360, focus)
            a = 255 * (1 - gone)
            c.save()
            camera(c, 1 + 0.3 * focus, 0, 0, x, y)
            chip(c, tk, x, y, a, AMBER, 40)
            c.restore()
            continue
        a = 255 * smooth(prog(q, i * 0.035, i * 0.035 + 0.1)) * (1 - focus)
        if a > 1:
            chip(c, tk, x, y - 120 * focus, a, AMBER, 40)


def draw_barcode(c, t):
    a = smooth(prog(t, TURN_T, TURN_T + 0.4)) * (1 - smooth(prog(t, MAP_T + 0.3, MAP_T + 0.7)))
    if a <= 0:
        return
    shown = int(768 * clamp(prog(t, NUM_T0 - 0.6, NUM_T1)))
    collapse = in_out(prog(t, MAP_T - 0.3, MAP_T + 0.5))
    x, y, w, h = 90, 520, 900, 320
    vals = EMB[:max(1, shown)]
    v = vals / (np.abs(EMB).max() + 1e-6)
    bw = w / 768
    mid = y + h / 2
    cx = W / 2
    for i, q in enumerate(v):
        bx = x + i * bw
        bx = lerp(bx, cx, collapse)
        grow = clamp((shown - i) / 40)
        hh = q * h / 2 * grow * (1 - collapse)
        c.drawRect(skia.Rect.MakeLTRB(bx, mid - max(0, hh), bx + bw * 0.8, mid - min(0, hh)),
                   paint(mix(VIOLET, PAPER, abs(q) * 0.5), 255 * a * (0.4 + 0.6 * abs(q))))
    if shown < 768 and shown > 0:
        c.drawRect(skia.Rect.MakeXYWH(x + shown * bw, y + 20, 2, h - 40), paint(PAPER, 200 * a))
    na = a * (1 - collapse)
    label(c, f"{shown}", W / 2, 1040, 170, "mono_bold", VIOLET, 255 * na, "center")
    label(c, "NUMBERS FOR ONE TOKEN", W / 2, 1100, 24, "mono", SMOKE, 255 * na, "center", 0.3)
    fig(c, 3, "“cat” AS NUMBERS (ILLUSTRATION)", 90, 480, 255 * na)
    if collapse > 0:
        c.drawCircle(cx, mid, 14 + 30 * collapse, paint(AMBER, 160 * a * collapse, sigma=16))
        c.drawCircle(cx, mid, 8, paint(PAPER, 255 * a * collapse))


def draw_map(c, t):
    a = smooth(prog(t, MAP_T + 0.2, MAP_T + 1.2))
    if a <= 0:
        return
    pts = {w: map_xy(w, t) for w in art.MEANING}
    # cluster glows once "that's how it knows what you mean"
    ga = smooth(prog(t, KNOWS_T - 0.2, KNOWS_T + 0.6))
    for g, ws in GROUPS.items():
        xs = [pts[w][0] for w in ws]
        ys = [pts[w][1] for w in ws]
        cx_, cy_ = sum(xs) / len(xs), sum(ys) / len(ys)
        r = max(math.hypot(x - cx_, y - cy_) for x, y in zip(xs, ys)) + 48
        c.drawCircle(cx_, cy_, r, paint(VIOLET, 40 * ga * a, sigma=30))
        c.drawCircle(cx_, cy_, r, paint(VIOLET, 90 * ga * a, stroke=1.5))
        label(c, g, cx_, cy_ - r - 14, 24, "mono_bold", VIOLET, 230 * ga * a, "center", 0.3)
    # faint grid lines between neighbours
    hot = {"cat": CAT_T, "kitten": KIT_T, "moon": MOON_T, "planet": PLAN_T}
    for w0, w1, t0 in (("cat", "kitten", KIT_T), ("moon", "planet", PLAN_T)):
        u = out_cubic(prog(t, t0 - 0.1, t0 + 0.4))
        if u > 0:
            (x0, y0, _), (x1, y1, _) = pts[w0], pts[w1]
            c.drawLine(x0, y0, lerp(x0, x1, u), lerp(y0, y1, u), paint(AMBER, 230 * a, stroke=3))
            label(c, "NEAR", (x0 + x1) / 2, (y0 + y1) / 2 - 18, 18, "mono_bold", AMBER, 230 * u * a, "center", 0.3)
    for w, (x, y, sc) in sorted(pts.items(), key=lambda kv: kv[1][2]):
        h = max([smooth(prog(t, ht - 0.15, ht + 0.25)) for ww, ht in hot.items() if ww == w] + [0])
        appear = smooth(prog(t, MAP_T + 0.3 + (zlib.crc32(w.encode()) % 10) * 0.06, MAP_T + 0.9 + (zlib.crc32(w.encode()) % 10) * 0.06))
        al = a * appear
        rgb = mix(SMOKE, AMBER, h)
        c.drawCircle(x, y, (6 + 6 * h) * sc * 1.4, paint(rgb, 255 * al))
        if h > 0:
            c.drawCircle(x, y, 40 * sc, paint(AMBER, 140 * h * al, sigma=16))
        label(c, w, x + 16, y + 9, (30 + 12 * h) * sc * 1.25, "mono_bold" if h > 0.5 else "mono", mix(SMOKE, PAPER, h), 255 * al)
    fig(c, 4, "MAP OF MEANING (SIMPLIFIED)", 90, 250, 255 * a)
    # the cat vector flies in and lands on "cat"
    fl = in_out(prog(t, MAP_T + 0.3, MAP_T + 1.3))
    if 0 < fl < 1:
        x, y, _ = pts["cat"]
        fx, fy = lerp(W / 2, x, fl), lerp(680, y, fl) - 120 * math.sin(math.pi * fl)
        c.drawCircle(fx, fy, 26, paint(AMBER, 180, sigma=14))
        c.drawCircle(fx, fy, 8, paint(PAPER))


def draw_frame(c, t):
    background(c)
    ambient(c, t, 0.6)
    # prompt box: comes forward, letters glitch on "words", then its text breaks into tokens
    ba = 255 * smooth(prog(t, 0.0, 0.5)) * (1 - smooth(prog(t, CHOP_T - 0.05, CHOP_T + 0.25)))
    if ba > 1:
        c.save()
        s = 0.92 + 0.08 * out_cubic(prog(t, 0, 0.8))
        camera(c, s, 0, 0, W / 2, BOX_Y + 80)
        prompt_box(c, art.PROMPT, BOX_X, BOX_Y, BOX_W, ba, caret=False, size=FS)
        c.restore()
        g = max(0.0, 1 - abs(t - WORDS_T - 0.15) / 0.35)
        if g > 0:
            grain_patch(c, skia.Rect.MakeXYWH(BOX_X + 20, BOX_Y + 30, BOX_W - 40, 140), 120 * g, int(t * 30))
    draw_tokens(c, t)
    fa = 255 * smooth(prog(t, CHOP_T + 0.4, CHOP_T + 0.9)) * (1 - smooth(prog(t, TURN_T - 0.2, TURN_T + 0.2)))
    fig(c, 2, f"{len(art.TOKENS)} TOKENS", 90, 570, fa)
    draw_barcode(c, t)
    draw_map(c, t)
    CAPS.draw(c, t)
    edges(c, t, DURATION, 0.25, 0.25)


def post_kw(t):
    return dict(glitch=max(0.0, 1 - abs(t - WORDS_T - 0.15) / 0.3) * 0.35)


def sfx_events():
    ev = [(0.0, "whoosh", 0.4), (WORDS_T, "static_burst", 0.3)]
    for i in range(len(art.TOKENS)):
        ev.append((CHOP_T + i * 0.035 * 1.6 + 0.15, "snap", 0.35))
    ev += [(TURN_T, "swish", 0.4), (NUM_T0 - 0.6, "counter", 0.5), (NUM_T1, "sparkle", 0.45),
           (MAP_T - 0.2, "whoosh", 0.5), (MAP_T + 1.2, "pop", 0.5), (KIT_T, "pluck", 0.6), (PLAN_T, "pluck", 0.6),
           (KNOWS_T, "shimmer", 0.35)]
    return ev


MUSIC = dict(beds=[(0.0, DURATION, "synth", 0.6), (0.0, DURATION, "arp", 0.8)])
