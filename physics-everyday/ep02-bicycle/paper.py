"""Stop-motion cut-paper kit: paper pieces with real cast shadows, cardstock grain, bevelled cut edges,
torn edges, brads, pins, string, masking tape and marker ink, plus a frame 'boil' at 12 fps.

Every piece is drawn in screen space: the local path is transformed by the current matrix, so shadows
always fall the same way (key light top-left) however a puppet is rotated or scaled, while the paper
grain stays glued to the piece and moves with it.
"""
import math, os, zlib

import numpy as np
import skia

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")

# ---------------------------------------------------------------- palette (cardstock colours)
SKY = (163, 214, 232)
SKY2 = (196, 230, 240)
SUN = (255, 196, 54)
CREAM = (246, 238, 220)
WHITE = (250, 247, 240)
KRAFT = (196, 160, 112)
KRAFT2 = (170, 132, 88)
INK = (34, 30, 36)
RED = (226, 58, 46)
RED_D = (170, 34, 30)
TIRE = (44, 43, 48)
STEEL = (200, 204, 210)
BLUE = (47, 108, 214)
BLUE_D = (32, 76, 160)
YELLOW = (255, 210, 63)
ORANGE = (244, 140, 52)
GREEN1 = (140, 196, 112)
GREEN2 = (96, 162, 92)
GREEN3 = (62, 124, 78)
CORAL = (233, 116, 92)
SAND = (242, 212, 155)
DENIM = (64, 92, 150)
SKIN = (238, 182, 140)
HAIR = (58, 38, 26)
ROAD = (78, 78, 88)
CURB = (190, 186, 178)
PURPLE = (132, 92, 186)
TEAL = (52, 160, 160)
PINK = (244, 160, 180)
GREY = (150, 152, 160)


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def col(c, a=1.0):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(max(0, min(1, a)) * 255))


# ---------------------------------------------------------------- fonts
_TF = {}


def face(name):
    files = {"title": "BowlbyOne-Regular.ttf", "hand": "CaveatBrush-Regular.ttf", "neat": "PatrickHand-Regular.ttf",
             "inter": "InterDisplay-Black.otf", "interb": "InterDisplay-Bold.otf"}
    if name not in _TF:
        _TF[name] = skia.Typeface.MakeFromFile(os.path.join(FONTS, files[name]))
    return _TF[name]


def font(name, size):
    f = skia.Font(face(name), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


# ---------------------------------------------------------------- paper grain (seamless, periodic by construction)
def _grain(n=512, seed=7):
    rng = np.random.default_rng(seed)
    fx = np.fft.fftfreq(n)[:, None]
    fy = np.fft.fftfreq(n)[None, :]
    f = np.sqrt(fx * fx + fy * fy) + 1e-3
    out = np.zeros((n, n))
    for beta, amp in ((1.6, 1.0), (0.6, 0.35)):
        w = np.fft.fft2(rng.standard_normal((n, n)))
        g = np.real(np.fft.ifft2(w / f ** beta))
        out += amp * (g - g.mean()) / g.std()
    # fibres: short wandering strands, drawn with wrap-around so the tile stays seamless
    fib = np.zeros((n, n))
    for _ in range(900):
        x, y = rng.uniform(0, n, 2)
        a = rng.uniform(0, math.pi)
        L = rng.uniform(6, 26)
        for s in np.linspace(0, L, int(L * 2)):
            a += rng.normal(0, 0.08)
            xi, yi = int(x + s * math.cos(a)) % n, int(y + s * math.sin(a)) % n
            fib[yi, xi] = 1.0
    out = out / out.std() * 0.55 - fib * 0.9
    v = np.clip(240 + out * 9, 205, 255).astype(np.uint8)
    rgba = np.dstack([v, v, v, np.full_like(v, 255)])
    return skia.Image.fromarray(np.ascontiguousarray(rgba))


GRAIN = _grain()


# ---------------------------------------------------------------- boil (stop-motion re-placement jitter)
class _Clock:
    t = 0.0
    fps_anim = 12  # animated "on twos"
    boil = 1.0


CLOCK = _Clock()


def held():
    return int(CLOCK.t * CLOCK.fps_anim + 1e-6)


def rnd(*key):
    h = zlib.crc32(repr(key).encode())
    return np.random.default_rng(h)


def boil(c, key, amp=1.0, pivot=(0, 0)):
    """Jitter the current transform a hair: a different tiny offset for every held frame."""
    if CLOCK.boil <= 0:
        return
    r = rnd("boil", key, held())
    dx, dy = r.normal(0, 0.9 * amp * CLOCK.boil, 2)
    da = r.normal(0, 0.28 * amp * CLOCK.boil)
    c.translate(dx, dy)
    c.translate(*pivot)
    c.rotate(da)
    c.translate(-pivot[0], -pivot[1])


# ---------------------------------------------------------------- path builders
def pts_path(pts, closed=True, smooth=False):
    p = skia.Path()
    pts = np.asarray(pts, float)
    if smooth and len(pts) > 3:
        m = (pts + np.roll(pts, -1, axis=0)) / 2
        p.moveTo(*m[-1])
        for i in range(len(pts)):
            p.quadTo(pts[i][0], pts[i][1], m[i][0], m[i][1])
    else:
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
    if closed:
        p.close()
    return p


def wobble(pts, amp=1.2, seed=0, freq=3.0, closed=True):
    """Hand-cut irregularity: low-frequency displacement along the outline normal."""
    pts = np.asarray(pts, float)
    n = len(pts)
    if n < 3 or amp == 0:
        return pts
    r = np.random.default_rng(seed)
    d = np.roll(pts, -1, 0) - np.roll(pts, 1, 0)
    nrm = np.stack([d[:, 1], -d[:, 0]], 1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    seglen = np.linalg.norm(np.diff(np.vstack([pts, pts[:1]]), axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seglen)[:-1]])
    per = max(s[-1] + seglen[-1], 1)
    off = np.zeros(n)
    for k in range(1, 5):
        f = int(max(1, freq * k * per / 600))
        off += r.normal(0, 1) / k * np.sin(2 * np.pi * f * s / per + r.uniform(0, 6.3))
    return pts + nrm * (off * amp)[:, None]


def torn(pts, amp=3.0, seed=0):
    """Torn edge: wobble plus fine jagged fibres."""
    pts = resample(pts, 4.0)
    p = wobble(pts, amp * 0.8, seed, 6.0)
    r = np.random.default_rng(seed + 99)
    d = np.roll(p, -1, 0) - np.roll(p, 1, 0)
    nrm = np.stack([d[:, 1], -d[:, 0]], 1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    return p + nrm * r.normal(0, amp * 0.35, len(p))[:, None]


def resample(pts, step=6.0, closed=True):
    pts = np.asarray(pts, float)
    P = np.vstack([pts, pts[:1]]) if closed else pts
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    out = []
    for i, L in enumerate(seg):
        k = max(1, int(L / step))
        for j in range(k):
            out.append(P[i] + (P[i + 1] - P[i]) * j / k)
    if not closed:
        out.append(P[-1])
    return np.array(out)


def circle(cx, cy, r, n=None):
    n = n or max(24, int(r * 0.9))
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack([cx + r * np.cos(a), cy + r * np.sin(a)], 1)


def ellipse(cx, cy, rx, ry, n=64, rot=0.0):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x, y = rx * np.cos(a), ry * np.sin(a)
    cr, sr = math.cos(rot), math.sin(rot)
    return np.stack([cx + x * cr - y * sr, cy + x * sr + y * cr], 1)


def rect(x, y, w, h):
    return np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], float)


def rrect(x, y, w, h, r, n=6):
    r = min(r, w / 2, h / 2)
    out = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return np.array(out)


def capsule(p0, p1, w0, w1=None, n=10):
    """A limb or tube: rounded strip between two joints."""
    w1 = w0 if w1 is None else w1
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    a = math.atan2(d[1], d[0])
    out = []
    for k in range(n + 1):
        t = a + math.pi / 2 + math.pi * k / n
        out.append(p0 + w0 / 2 * np.array([math.cos(t), math.sin(t)]))
    for k in range(n + 1):
        t = a - math.pi / 2 + math.pi * k / n
        out.append(p1 + w1 / 2 * np.array([math.cos(t), math.sin(t)]))
    return np.array(out)


def ring(cx, cy, r0, r1, n=96):
    p = skia.Path()
    p.addCircle(cx, cy, r1)
    p.addCircle(cx, cy, r0, skia.PathDirection.kCCW)
    return p


def union(*paths):
    out = paths[0]
    for q in paths[1:]:
        out = skia.Op(out, q, skia.PathOp.kUnion_PathOp)
    return out


def minus(a, b):
    return skia.Op(a, b, skia.PathOp.kDifference_PathOp)


def as_path(shape, smooth=False):
    return shape if isinstance(shape, skia.Path) else pts_path(shape, smooth=smooth)


# ---------------------------------------------------------------- the paper piece
LIGHT = np.array([0.55, 0.85])  # direction shadows fall (screen space, down-right)


def piece(c, shape, color, z=1.0, rim=True, grain=True, shadow=True, alpha=1.0, smooth=False, fringe=None,
          seed=0, shadow_k=1.0, grain_k=1.0):
    """Draw one paper cut-out. z = how high it sits above the layer below (sets shadow size/softness)."""
    lp = as_path(shape, smooth)
    M = c.getTotalMatrix()
    dp = skia.Path(lp)
    dp.transform(M)
    c.save()
    c.resetMatrix()
    if shadow and z > 0:
        off = LIGHT * (2.0 + 7.0 * z)
        sig = 1.4 + 4.2 * z
        sp = skia.Paint(AntiAlias=True, Color=skia.Color4f(0.12, 0.08, 0.05, min(0.42, (0.22 + 0.10 * z)) * shadow_k * alpha),
                        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sig))
        c.save()
        c.translate(*off)
        if fringe:
            sp.setStyle(skia.Paint.kStrokeAndFill_Style)
            sp.setStrokeWidth(fringe[0] * 2.2 if isinstance(fringe, tuple) else fringe * 2.2)
        c.drawPath(dp, sp)
        c.restore()
        # tight contact occlusion right at the edge
        sp2 = skia.Paint(AntiAlias=True, Color=skia.Color4f(0.1, 0.06, 0.04, 0.18 * shadow_k * alpha),
                         MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 1.2))
        c.save()
        c.translate(*(LIGHT * 1.6))
        c.drawPath(dp, sp2)
        c.restore()
    if fringe:
        # torn edge: the white paper core shows as a fuzzy rim around the coloured face
        c.drawPath(dp, fringe_paint(fringe, col(WHITE), alpha))
    c.drawPath(dp, skia.Paint(AntiAlias=True, Color=col(color, alpha)))
    if grain:
        _grain(c, dp, M, seed, alpha * grain_k)
    if rim:
        c.save()
        c.clipPath(dp, skia.ClipOp.kIntersect, True)
        hp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.6, Color=skia.Color4f(1, 1, 1, 0.38 * alpha))
        q = skia.Path(dp)
        q.offset(1.4, 1.8)
        c.drawPath(q, hp)
        dk = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.6, Color=skia.Color4f(0, 0, 0, 0.16 * alpha))
        q = skia.Path(dp)
        q.offset(-1.4, -1.8)
        c.drawPath(q, dk)
        c.restore()
    c.restore()
    return dp


def fringe_paint(f, color, a=1.0, shadow_sigma=None):
    """Torn edge: the white paper core shows as a fuzzy, fibrous rim around the coloured face."""
    amp, seed = f if isinstance(f, tuple) else (f, 0)
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStrokeAndFill_Style, StrokeWidth=amp * 2.2, Color=color,
                   PathEffect=skia.DiscretePathEffect.Make(5.0, amp * 0.9, seed))
    p.setAlphaf(a * p.getAlphaf())
    if shadow_sigma:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, shadow_sigma))
    return p


def _grain(c, dp, M, seed, a):
    r = rnd("g", seed)
    lm = skia.Matrix.Concat(M, skia.Matrix())
    lm.preTranslate(float(r.uniform(0, 512)), float(r.uniform(0, 512)))
    lm.preScale(0.9, 0.9)
    gp = skia.Paint(AntiAlias=True, Shader=GRAIN.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat,
                                                            skia.SamplingOptions(skia.FilterMode.kLinear), lm),
                    BlendMode=skia.BlendMode.kMultiply)
    gp.setAlphaf(a)
    c.drawPath(dp, gp)


# ---------------------------------------------------------------- props
def brad(c, x, y, r=7, color=(212, 172, 72)):
    """Split-pin brad: the joint of every puppet."""
    piece(c, circle(x, y, r, 20), color, 0.35, rim=False, grain=False)
    c.drawCircle(x - r * 0.3, y - r * 0.35, r * 0.38, skia.Paint(AntiAlias=True, Color=skia.Color4f(1, 1, 0.9, 0.7)))
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.2, Color=col(shade(color, 0.6))))


def pushpin(c, x, y, color=RED, r=13):
    M = c.getTotalMatrix()
    c.save()
    c.resetMatrix()
    q = M.mapXY(x, y)
    x, y = q.x(), q.y()
    sp = skia.Paint(AntiAlias=True, Color=skia.Color4f(0, 0, 0, 0.35), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 4))
    c.drawCircle(x + 9, y + 14, r * 0.9, sp)
    g = skia.GradientShader.MakeRadial(skia.Point(x - r * 0.35, y - r * 0.4), r * 1.3,
                                       [col(shade(color, 1.35)), col(color), col(shade(color, 0.55))], [0, 0.45, 1])
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=g))
    c.drawCircle(x - r * 0.35, y - r * 0.4, r * 0.28, skia.Paint(AntiAlias=True, Color=skia.Color4f(1, 1, 1, 0.75)))
    c.restore()


def string(c, p0, p1, color=RED, sag=6.0, w=3.0, n=30):
    """Thread pulled between two pins, with a cast shadow."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    t = np.linspace(0, 1, n)[:, None]
    pts = p0 + (p1 - p0) * t
    pts[:, 1] += sag * np.sin(np.pi * t[:, 0])
    path = pts_path(pts, closed=False)
    M = c.getTotalMatrix()
    dp = skia.Path(path)
    dp.transform(M)
    c.save()
    c.resetMatrix()
    sp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, Color=skia.Color4f(0, 0, 0, 0.28),
                    MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 2.2))
    q = skia.Path(dp)
    q.offset(5, 8)
    c.drawPath(q, sp)
    st = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, Color=col(color), StrokeCap=skia.Paint.kRound_Cap)
    c.drawPath(dp, st)
    st2 = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w * 0.35, Color=skia.Color4f(1, 1, 1, 0.35))
    q = skia.Path(dp)
    q.offset(-0.6, -0.6)
    c.drawPath(q, st2)
    c.restore()


def tape(c, x, y, w, h, rot=0.0, seed=0, color=(236, 222, 178)):
    """A strip of masking tape (translucent, zig-zag torn ends)."""
    r = np.random.default_rng(seed)
    top = [(x + w * i / 12, y + r.normal(0, 0.4)) for i in range(13)]
    right = [(x + w + (2.5 if i % 2 else -2.5), y + h * i / 6) for i in range(1, 6)]
    bot = [(x + w - w * i / 12, y + h + r.normal(0, 0.4)) for i in range(13)]
    left = [(x + (2.5 if i % 2 else -2.5), y + h - h * i / 6) for i in range(1, 6)]
    pts = np.array(top + right + bot + left)
    c.save()
    c.translate(x + w / 2, y + h / 2)
    c.rotate(rot)
    c.translate(-(x + w / 2), -(y + h / 2))
    piece(c, pts, color, 0.12, rim=False, alpha=0.88, seed=seed, shadow_k=0.6)
    c.restore()


def ink_text(c, text, x, y, fnt, color=INK, align="left", alpha=1.0):
    w = fnt.measureText(text)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    c.drawString(text, x, y, fnt, skia.Paint(AntiAlias=True, Color=col(color, alpha)))
    return w


def chip(c, text, cx, cy, fnt, fg=INK, bg=WHITE, rot=0.0, z=0.7, pad=(22, 14), seed=0, torn_edge=False):
    """A word printed on its own cut-out card."""
    w = fnt.measureText(text)
    m = fnt.getMetrics()
    capH = -m.fCapHeight if m.fCapHeight else fnt.getSize() * 0.7
    capH = abs(capH)
    bw, bh = w + pad[0] * 2, capH + pad[1] * 2
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    boil(c, ("chip", text, seed), 0.6)
    shp = wobble(resample(rect(-bw / 2, -bh / 2, bw, bh), 8), 1.3, seed)
    piece(c, shp, bg, z, seed=seed, fringe=(3.0, seed) if torn_edge else None)
    ink_text(c, text, -w / 2, capH / 2, fnt, fg)
    c.restore()
    return bw, bh


def letters(c, text, cx, cy, fnt, palette, seed=0, z=0.9, spacing=0.0, rot_amp=5.0, fg=INK, pop=None):
    """Title made of individually cut letters, each on its own card, ransom-note style but tidy."""
    r = np.random.default_rng(seed)
    ws = [fnt.measureText(ch) for ch in text]
    pad = fnt.getSize() * 0.16
    widths = [(w + pad * 2 if ch != " " else fnt.getSize() * 0.3) for ch, w in zip(text, ws)]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    capH = abs(fnt.getMetrics().fCapHeight)
    for i, (ch, w, bw) in enumerate(zip(text, ws, widths)):
        rot = r.normal(0, rot_amp)
        dy = r.normal(0, 6)
        colr = palette[i % len(palette)]
        s = 1.0 if pop is None else pop[i] if i < len(pop) else 1.0
        if ch != " " and s > 0.01:
            bh = capH + pad * 2.2
            c.save()
            c.translate(x + bw / 2, cy + dy)
            c.rotate(rot)
            c.scale(s, s)
            boil(c, ("let", seed, i), 0.7)
            shp = wobble(resample(rect(-bw / 2, -bh / 2, bw, bh), 8), 1.2, seed * 31 + i)
            piece(c, shp, colr, z, seed=seed * 31 + i)
            fgc = fg if sum(colr) > 420 else WHITE
            ink_text(c, ch, -w / 2, capH / 2, fnt, fgc)
            c.restore()
        x += bw + spacing


def marker(c, pts, color=RED, w=9.0, alpha=0.92, seed=0):
    """Felt-tip marker stroke: slightly uneven width, ink pooled at the ends."""
    pts = np.asarray(pts, float)
    pts = resample(pts, 6, closed=False)
    r = np.random.default_rng(seed)
    pts = pts + r.normal(0, 0.6, pts.shape)
    p = pts_path(pts, closed=False, smooth=False)
    pa = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, Color=col(color, alpha),
                    StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join, BlendMode=skia.BlendMode.kMultiply)
    c.drawPath(p, pa)
    for e in (pts[0], pts[-1]):
        c.drawCircle(e[0], e[1], w * 0.55, skia.Paint(AntiAlias=True, Color=col(shade(color, 0.8), 0.5), BlendMode=skia.BlendMode.kMultiply))


def hand(c, text, x, y, size, color=INK, rot=0.0, align="left", face_name="hand", alpha=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    w = ink_text(c, text, 0, 0, font(face_name, size), color, align, alpha)
    c.restore()
    return w


def arrow_shape(p0, p1, bend=0.0, w=34, head=70, n=40):
    """A cut-paper arrow along a (possibly curved) path, as an outline polygon."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    L = np.linalg.norm(d)
    nrm = np.array([-d[1], d[0]]) / L
    t = np.linspace(0, 1, n)
    ctr = p0[None] + d[None] * t[:, None] + nrm[None] * (bend * 4 * t * (1 - t))[:, None]
    cut = int(n * (1 - head / L))
    cut = max(2, min(n - 2, cut))
    tg = np.gradient(ctr, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True)
    nn = np.stack([-tg[:, 1], tg[:, 0]], 1)
    left = ctr[:cut] + nn[:cut] * w / 2
    right = ctr[:cut] - nn[:cut] * w / 2
    base = ctr[cut]
    hn = nn[cut]
    tip = ctr[-1]
    return np.vstack([left, [base + hn * w * 1.25], [tip], [base - hn * w * 1.25], right[::-1]])


# ---------------------------------------------------------------- photographic finish
def vignette(c, strength=0.42):
    g = skia.GradientShader.MakeRadial(skia.Point(W * 0.48, H * 0.44), H * 0.78,
                                       [skia.Color4f(0, 0, 0, 0), skia.Color4f(0, 0, 0, 0), skia.Color4f(0.08, 0.03, 0, strength)],
                                       [0, 0.55, 1])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=g))


def warm_light(c, k=1.0):
    """Key light pooled top-left (a desk lamp over the set), falling off to the bottom-right."""
    g = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(W, H)],
                                       [skia.Color4f(1, 0.93, 0.78, 0.16 * k), skia.Color4f(1, 1, 1, 0), skia.Color4f(0.2, 0.25, 0.45, 0.14 * k)],
                                       [0, 0.5, 1])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=g, BlendMode=skia.BlendMode.kSoftLight))


class Blur:
    """Depth of field: draw a far layer inside `with Blur(c, sigma):`."""

    def __init__(self, c, sigma):
        self.c, self.s = c, sigma

    def __enter__(self):
        if self.s > 0.05:
            self.c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(self.s, self.s)))
        else:
            self.c.save()

    def __exit__(self, *a):
        self.c.restore()


def new_surface():
    return skia.Surface(W, H)


def save_png(surf, path):
    surf.makeImageSnapshot().save(path, skia.kPNG)
