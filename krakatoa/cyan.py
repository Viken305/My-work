""""Cyanotype & Sulfur" drawing kit for the Krakatoa Short.

  * Prussian-blue cyanotype paper (fibre noise, uneven exposure) and engraved linework
  * Orthographic globe / map projection of Natural Earth coastlines with classic engraved "water lines"
  * Sound made visible: glowing sulfur pressure rings with a chromatic leading edge
  * Mono plate labels (FIG. 3 · ...), dimension lines, a barograph card, a dB meter
  * Post: bloom on yellow/red only, blue grade, chromatic aberration, grain, vignette, motion blur
"""
import json, math, os

import cv2
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "deep-hole", "fonts")   # shared with the previous Short
cv2.setNumThreads(1)

# ---------------------------------------------------------------- palette
PRUSSIAN = (11, 30, 58)
NIGHT = (6, 16, 31)
PAPER = (230, 238, 245)       # cyanotype white
FADED = (127, 155, 184)       # secondary text, grid
SULFUR = (255, 210, 63)       # sound and pressure
LAVA = (255, 59, 47)          # fire, ash, harm
SUN_O = (255, 138, 61)
SUN_V = (91, 42, 134)
HOT = (255, 246, 222)

FONTS = {
    "regular": "InterDisplay-Regular.otf", "medium": "InterDisplay-Medium.otf", "semibold": "InterDisplay-SemiBold.otf",
    "bold": "InterDisplay-Bold.otf", "black": "InterDisplay-Black.otf",
    "serif": "NotoSerifDisplay-Italic.ttf", "serif_bold": "NotoSerifDisplay-BoldItalic.ttf",
    "mono": "NotoSansMono-Regular.ttf", "mono_bold": "NotoSansMono-Bold.ttf",
}
_TF, _F = {}, {}


# ---------------------------------------------------------------- basics
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    return 1.0 if t1 <= t0 and t >= t1 else clamp((t - t0) / (t1 - t0)) if t1 > t0 else 0.0


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


def spring(u, k=7.0, w=10.0):
    u = clamp(u)
    return 1 - math.exp(-k * u) * math.cos(w * u)


def mix(a, b, t):
    t = clamp(t)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def col(rgb, a=255):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(clamp(a / 255) * 255))


def paint(rgb, a=255, sigma=0.0, plus=False, stroke=0.0):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if sigma > 0.25:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    if plus:
        p.setBlendMode(skia.BlendMode.kPlus)
    return p


def font(kind, size):
    key = (kind, round(size, 1))
    if key not in _F:
        if kind not in _TF:
            _TF[kind] = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, FONTS[kind]))
        f = skia.Font(_TF[kind], size)
        f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
        f.setSubpixel(True)
        _F[key] = f
    return _F[key]


def width(s, kind, size, tracking=0.0):
    f = font(kind, size)
    return sum(f.measureText(ch) for ch in s) + tracking * size * max(0, len(s) - 1)


def label(c, s, x, y, size, kind="medium", rgb=PAPER, a=255, align="left", tracking=0.0, sigma=0.0, plus=False):
    if a <= 1:
        return
    f = font(kind, size)
    w = width(s, kind, size, tracking)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    p = paint(rgb, a, sigma, plus)
    for ch in s:
        c.drawString(ch, x0, y, f, p)
        x0 += f.measureText(ch) + tracking * size


# ---------------------------------------------------------------- noise + paper
def _value_noise(h, w, scale, rng):
    g = rng.random((int(h / scale) + 3, int(w / scale) + 3)).astype(np.float32)
    return cv2.resize(g, (w + int(3 * scale), h + int(3 * scale)), interpolation=cv2.INTER_CUBIC)[:h, :w]


def fbm(h, w, seed=0, base=160, octaves=6, gain=0.55):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot, sc = 1.0, 0.0, base
    for _ in range(octaves):
        out += amp * _value_noise(h, w, max(sc, 1.5), rng)
        tot += amp
        amp *= gain
        sc /= 2.0
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


_PAPER = None


def paper_image():
    """Cyanotype sheet: deep Prussian blue, brighter where the 'sun' exposed it less evenly, with paper fibres."""
    global _PAPER
    if _PAPER is None:
        n = fbm(H // 2, W // 2, 11, 260, 5)
        fib = fbm(H // 2, W // 2, 12, 6, 3, 0.7)
        streak = cv2.GaussianBlur(np.random.default_rng(4).random((H // 2, W // 2)).astype(np.float32), (0, 0), sigmaX=9, sigmaY=0.6)
        yy, xx = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32)
        r = np.sqrt(((xx - W / 4) / (W / 4)) ** 2 + ((yy - H / 4.4) / (H / 4)) ** 2)
        k = np.clip(0.72 - 0.42 * r + (n - 0.5) * 0.35 + (fib - 0.5) * 0.06 + (streak - 0.5) * 0.25, 0, 1)[..., None]
        rgb = np.array(NIGHT, np.float32) + (np.array(PRUSSIAN, np.float32) * 1.45 - np.array(NIGHT, np.float32)) * k
        rgb = cv2.resize(rgb, (W, H), interpolation=cv2.INTER_CUBIC)
        rgba = np.dstack([np.clip(rgb, 0, 255), np.full((H, W), 255, np.float32)]).astype(np.uint8)
        _PAPER = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    return _PAPER


def paper(c, a=255):
    p = skia.Paint()
    p.setAlphaf(a / 255)
    c.drawImage(paper_image(), 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)


# ---------------------------------------------------------------- projection + coastlines
_LAND = {}


def land(name):
    if name not in _LAND:
        _LAND[name] = json.load(open(os.path.join(HERE, "data", f"{name}.json")))
    return _LAND[name]


class Ortho:
    """Orthographic projection centred on (lon0, lat0), then a 2D similarity (scale R, rotation, offset)."""

    def __init__(self, lon0, lat0, R, cx, cy, rot=0.0):
        self.l0, self.p0 = math.radians(lon0), math.radians(lat0)
        self.R, self.cx, self.cy, self.rot = R, cx, cy, math.radians(rot)

    def xyz(self, lon, lat):
        l, p = math.radians(lon) - self.l0, math.radians(lat)
        x = math.cos(p) * math.sin(l)
        y = math.cos(self.p0) * math.sin(p) - math.sin(self.p0) * math.cos(p) * math.cos(l)
        z = math.sin(self.p0) * math.sin(p) + math.cos(self.p0) * math.cos(p) * math.cos(l)
        return x, y, z

    def __call__(self, lon, lat):
        x, y, z = self.xyz(lon, lat)
        cr, sr = math.cos(self.rot), math.sin(self.rot)
        X, Y = x * cr - y * sr, x * sr + y * cr
        return self.cx + X * self.R, self.cy - Y * self.R, z

    @staticmethod
    def fit(a, pa, b, pb, lon0, lat0):
        """Projection that puts geographic point a at screen pa and b at pb."""
        o = Ortho(lon0, lat0, 1, 0, 0)
        (ax, ay, _), (bx, by, _) = o(*a), o(*b)
        dv = complex(bx - ax, by - ay)
        ds = complex(pb[0] - pa[0], pb[1] - pa[1])
        k = ds / dv
        R, rot = abs(k), -math.degrees(math.atan2(k.imag, k.real))
        o = Ortho(lon0, lat0, R, 0, 0, rot)
        x, y, _ = o(*a)
        return Ortho(lon0, lat0, R, pa[0] - x, pa[1] - y, rot)


def land_path(proj, name, cull=-0.02):
    path = skia.Path()
    for ring in land(name):
        pts = [proj(lon, lat) for lon, lat in ring]
        if max(p[2] for p in pts) < cull:
            continue
        first = True
        for x, y, z in pts:
            if z < cull:   # clip to the visible hemisphere by pushing back-side points onto the limb
                continue
            if first:
                path.moveTo(x, y)
                first = False
            else:
                path.lineTo(x, y)
        path.close()
    return path


_COAST = {}


def _coast_layer(path, lines, key):
    """Raster of old-map water lines: thin contours at fixed distances from the coast (distance transform)."""
    if key in _COAST:
        return _COAST[key]
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.clear(skia.ColorBLACK)
    c.drawPath(path, paint((255, 255, 255)))
    landm = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., 0] > 127
    d = cv2.distanceTransform((~landm).astype(np.uint8), cv2.DIST_L2, 5)
    a = np.zeros((H, W), np.float32)
    for k, L in enumerate(lines):
        a = np.maximum(a, np.clip(1 - np.abs(d - L) / 0.85, 0, 1) * (0.5 - 0.09 * k))
    a = np.maximum(a, np.clip(1 - np.abs(d - 3.5) / 0.8, 0, 1) * 0.22)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = PAPER
    rgba[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    img = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
    if len(_COAST) > 8:
        _COAST.clear()
    _COAST[key] = img
    return img


def engraved_land(c, path, a=1.0, hatch=7.0, water_lines=(9, 19, 31, 46), rgb=PAPER, fill=None, key=None):
    """Old-map coast: concentric water lines outside, light fill and diagonal hatching inside, hairline coast.
    key caches the water-line raster (pass one for a static camera)."""
    if water_lines:
        img = _coast_layer(path, water_lines, key or ("tmp", id(path)))
        p = skia.Paint()
        p.setAlphaf(clamp(a))
        c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.drawPath(path, paint(fill or mix(PRUSSIAN, PAPER, 0.13), 255 * a))
    c.save()
    c.clipPath(path, doAntiAlias=True)
    hp = paint(rgb, 30 * a, stroke=1.0)
    for i in range(-H, W + H, int(hatch)):
        c.drawLine(i, 0, i + H * 0.6, H, hp)
    c.restore()
    c.drawPath(path, paint(rgb, 230 * a, stroke=1.5))


def graticule(c, proj, a=1.0, step=15, rgb=FADED):
    p = paint(rgb, 60 * a, stroke=1.0)
    for lon in range(-180, 180, step):
        _poly(c, [proj(lon, lat) for lat in range(-90, 91, 3)], p)
    for lat in range(-75, 90, step):
        _poly(c, [proj(lon, lat) for lon in range(-180, 181, 3)], p)


def _poly(c, pts, p, closed=False):
    path, pen = skia.Path(), False
    for x, y, z in pts:
        if z < 0:
            pen = False
            continue
        if pen:
            path.lineTo(x, y)
        else:
            path.moveTo(x, y)
            pen = True
    if closed:
        path.close()
    c.drawPath(path, p)


def destination(lon, lat, bearing, ang):
    """Point at angular distance ang (rad) from (lon, lat) along bearing (rad)."""
    p1, l1 = math.radians(lat), math.radians(lon)
    p2 = math.asin(math.sin(p1) * math.cos(ang) + math.cos(p1) * math.sin(ang) * math.cos(bearing))
    l2 = l1 + math.atan2(math.sin(bearing) * math.sin(ang) * math.cos(p1), math.cos(ang) - math.sin(p1) * math.sin(p2))
    return math.degrees(l2), math.degrees(p2)


# ---------------------------------------------------------------- sound made visible
def glow_stroke(c, path, rgb, a=255, wd=3.0, glow=1.0):
    """Additive line: two soft blur passes + a hot core."""
    if a <= 1:
        return
    c.drawPath(path, paint(rgb, a * 0.35 * glow, sigma=22, plus=True, stroke=wd * 6))
    c.drawPath(path, paint(rgb, a * 0.6 * glow, sigma=6, plus=True, stroke=wd * 2.2))
    c.drawPath(path, paint(mix(rgb, HOT, 0.55), a, plus=True, stroke=wd))


def ring(c, x, y, r, rgb=SULFUR, a=255, wd=3.0, fringe=True, trail=3):
    """A pressure ring: bright leading edge with a chromatic fringe and a few fading echo rings behind it."""
    if r <= 0.5 or a <= 1:
        return
    path = skia.Path()
    path.addCircle(x, y, r)
    if fringe:
        q = skia.Path()
        q.addCircle(x, y, r + wd * 1.6)
        c.drawPath(q, paint((255, 80, 60), a * 0.35, sigma=2, plus=True, stroke=wd * 0.8))
        q = skia.Path()
        q.addCircle(x, y, r - wd * 1.6)
        c.drawPath(q, paint((80, 200, 255), a * 0.3, sigma=2, plus=True, stroke=wd * 0.8))
    glow_stroke(c, path, rgb, a, wd)
    for k in range(1, trail + 1):
        rr = r - k * (18 + r * 0.04)
        if rr > 2:
            q = skia.Path()
            q.addCircle(x, y, rr)
            c.drawPath(q, paint(rgb, a * 0.3 / k, plus=True, stroke=wd * 0.5))


def sphere_ring(c, proj, lon, lat, ang, rgb=SULFUR, a=255, wd=3.0, back=0.18):
    """Small circle on the globe ang radians around (lon, lat); the far side is drawn faint and dashed."""
    pts = [proj(*destination(lon, lat, math.radians(b), ang)) for b in np.linspace(0, 360, 361)]
    front, backp = skia.Path(), skia.Path()
    pf = pb = False
    for x, y, z in pts:
        if z >= 0:
            (front.lineTo if pf else front.moveTo)(x, y)
            pf, pb = True, False
        else:
            (backp.lineTo if pb else backp.moveTo)(x, y)
            pb, pf = True, False
    bp = paint(rgb, a * back, plus=True, stroke=wd * 0.6)
    bp.setPathEffect(skia.DashPathEffect.Make([10, 12], 0))
    c.drawPath(backp, bp)
    glow_stroke(c, front, rgb, a, wd)


def light(c, x, y, r, rgb, a=200):
    if r <= 0.5 or a <= 1:
        return
    sh = skia.GradientShader.MakeRadial((x, y), r, [col(rgb, a), col(rgb, a * 0.45), col(rgb, a * 0.12), col(rgb, 0)],
                                        [0, 0.22, 0.55, 1])
    p = skia.Paint(AntiAlias=True, Shader=sh)
    p.setBlendMode(skia.BlendMode.kPlus)
    c.drawCircle(x, y, r, p)


# ---------------------------------------------------------------- plate furniture
def fig(c, n, text, x, y, a=255, align="left", size=22, plate=True):
    """Engraved plate caption: FIG. 3 · BAROMETER, LONDON (on a small dark plate so it reads over any map)."""
    s = f"FIG. {n}  ·  {text}"
    if plate:
        w = width(s, "mono", size, 0.12)
        x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
        c.drawRect(skia.Rect.MakeXYWH(x0 - 14, y - size * 1.05, w + 28, size * 1.6), paint(NIGHT, a * 0.8))
        c.drawLine(x0 - 14, y + size * 0.55, x0 + w + 14, y + size * 0.55, paint(SULFUR, a * 0.8, stroke=1.4))
    label(c, s, x, y, size, "mono", PAPER if plate else FADED, a * 0.9, align, tracking=0.12)


def dim_line(c, x1, y1, x2, y2, text, a=255, rgb=PAPER, size=26, off=0):
    ang = math.atan2(y2 - y1, x2 - x1)
    p = paint(rgb, a * 0.8, stroke=1.4)
    c.drawLine(x1, y1, x2, y2, p)
    nx, ny = -math.sin(ang) * 12, math.cos(ang) * 12
    for x, y in ((x1, y1), (x2, y2)):
        c.drawLine(x - nx, y - ny, x + nx, y + ny, p)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    c.save()
    c.translate(mx, my)
    deg = math.degrees(ang)
    if deg > 90 or deg < -90:
        deg += 180
    c.rotate(deg)
    tw = width(text, "mono_bold", size, 0.08)
    c.drawRect(skia.Rect.MakeXYWH(-tw / 2 - 14, -size * 0.85 + off, tw + 28, size * 1.25), paint(NIGHT, a * 0.85))
    label(c, text, 0, off, size, "mono_bold", rgb, a, "center", tracking=0.08)
    c.restore()


def pin(c, x, y, name, sub=None, a=255, rgb=PAPER, side=1, size=30):
    c.drawCircle(x, y, 7, paint(rgb, a))
    c.drawCircle(x, y, 15, paint(rgb, a * 0.6, stroke=1.4))
    tx = x + 28 * side
    label(c, name, tx, y + size * 0.35, size, "semibold", rgb, a, "left" if side > 0 else "right", tracking=0.1)
    if sub:
        label(c, sub, tx, y + size * 0.35 + 34, 21, "mono", FADED, a, "left" if side > 0 else "right", tracking=0.1)


def barograph(c, x, y, w, h, t, spike_at, a=255, title="BAROMETER, LONDON", n=4):
    """Recording card: ruled paper, an ink trace with the pressure spike, brass ticks."""
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), paint(NIGHT, a * 0.82))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), paint(PAPER, a * 0.7, stroke=1.4))
    gp = paint(FADED, a * 0.35, stroke=1.0)
    for i in range(1, 6):
        c.drawLine(x, y + h * i / 6, x + w, y + h * i / 6, gp)
    for i in range(1, 12):
        c.drawLine(x + w * i / 12, y, x + w * i / 12, y + h, paint(FADED, a * 0.18, stroke=1.0))
    path = skia.Path()
    mid = y + h * 0.58
    for i in range(0, 241):
        u = i / 240
        v = math.sin(u * 13) * 3 + math.sin(u * 47 + 1) * 1.5
        d = (u - spike_at) * 60
        v -= h * 0.38 * math.exp(-d * d) * math.sin(d * 2.4 + 1.2) * (1 if u < t else 0)
        X = x + 14 + u * (w - 28)
        if u <= t:
            (path.lineTo if i else path.moveTo)(X, mid + v)
    glow_stroke(c, path, SULFUR, a, 2.4, 0.6)
    fig(c, n, title, x + 16, y - 16, a, size=19)


def db_meter(c, x, y, r, value, a=255, marks=((0, "0"), (60, "TALK"), (120, "PAIN"), (150, "JET"), (172, "KRAKATOA"))):
    """Brass-instrument style arc gauge, 0..180 dB."""
    c.drawArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 200, 140, False, paint(PAPER, a * 0.8, stroke=2.0))
    for v in range(0, 181, 10):
        ang = math.radians(200 + 140 * v / 180)
        l = 26 if v % 30 == 0 else 12
        c.drawLine(x + math.cos(ang) * r, y + math.sin(ang) * r, x + math.cos(ang) * (r - l), y + math.sin(ang) * (r - l),
                   paint(PAPER, a * 0.75, stroke=1.6))
    for v, name in marks:
        ang = math.radians(200 + 140 * v / 180)
        rgb = SULFUR if v >= 172 else LAVA if v >= 120 else FADED
        label(c, name, x + math.cos(ang) * (r + 40), y + math.sin(ang) * (r + 40) + 8, 20, "mono_bold", rgb, a, "center", 0.1)
    ang = math.radians(200 + 140 * clamp(value / 180))
    needle = skia.Path()
    needle.moveTo(x, y)
    needle.lineTo(x + math.cos(ang) * (r - 8), y + math.sin(ang) * (r - 8))
    glow_stroke(c, needle, SULFUR, a, 3.0)
    c.drawCircle(x, y, 12, paint(PAPER, a))


# ---------------------------------------------------------------- particles
class Ash:
    def __init__(self, n=9000, seed=3, box=(0, 0, W, H)):
        rng = np.random.default_rng(seed)
        self.p = rng.random((n, 2)) * [box[2] - box[0], box[3] - box[1]] + [box[0], box[1]]
        self.z = rng.random(n) ** 2
        self.ph = rng.random(n) * 6.28
        self.v = rng.normal(0, 1, (n, 2))

    def draw(self, c, t, rgb=(40, 40, 52), a=1.0, wind=(18, -6), tint=None):
        for i in range(len(self.z)):
            z = self.z[i]
            x = self.p[i, 0] + (wind[0] + self.v[i, 0] * 6) * t * (0.4 + z) + math.sin(t * 0.7 + self.ph[i]) * 8
            y = self.p[i, 1] + (wind[1] + self.v[i, 1] * 4) * t * (0.4 + z)
            r = 0.8 + z * 3.2
            blur = abs(z - 0.35) * 5
            c.drawCircle(x % W, y % H, r, paint(tint or rgb, (60 + 160 * z) * a, sigma=blur))


# ---------------------------------------------------------------- captions (audio-reactive)
CAP_Y = 1380


def caption(c, words, t, t0s, y=CAP_Y, size=84, env=None, emph=None, dur=0.55, a=1.0):
    """One phrase. Each word ripples in at its spoken time: letters lift 0 -> 8 px and settle with a spring, in order,
    like a pressure wave passing through the text. The active word swells with the voice envelope (env(t) in 0..1).
    emph maps word index -> colour; those words switch to the serif italic and pulse a ring once."""
    emph = emph or {}
    kinds = ["serif_bold" if i in emph else "bold" for i in range(len(words))]
    sizes = [size * (1.12 if i in emph else 1.0) for i in range(len(words))]
    space = size * 0.28
    total = sum(width(wd, k, s) for wd, k, s in zip(words, kinds, sizes)) + space * (len(words) - 1)
    x = W / 2 - total / 2
    active = max([i for i, ts in enumerate(t0s) if t >= ts] or [-1])
    for i, wd in enumerate(words):
        k, s = kinds[i], sizes[i]
        wdw = width(wd, k, s)
        u0 = t - t0s[i]
        if u0 < -0.05:
            x += wdw + space
            continue
        rgb = emph.get(i, PAPER)
        swell = 1.0 + (0.04 * env(t) if env and i == active else 0)
        f = font(k, s * swell)
        cx = x
        if i in emph and u0 > 0:
            q = out_cubic(u0 / 0.7)
            rr = wdw * (0.55 + 0.6 * q)
            pth = skia.Path()
            pth.addOval(skia.Rect.MakeXYWH(x + wdw / 2 - rr, y - s * 0.32 - rr * 0.42, rr * 2, rr * 0.84))
            c.drawPath(pth, paint(rgb, 150 * (1 - q) * a, sigma=3, plus=True, stroke=2.4))
            light(c, x + wdw / 2, y - s * 0.3, wdw * 0.9, rgb, 40 * a)
        for j, ch in enumerate(wd):
            u = (u0 - j * 0.028) / dur
            if u <= 0:
                cx += f.measureText(ch)
                continue
            lift = math.sin(clamp(u * 1.6) * math.pi) * 9 * (1 - clamp(u))
            sp = spring(u, 8, 11)
            dy = (1 - sp) * 26 - lift
            al = clamp(u * 3) * 255 * a
            blur = max(0.0, (1 - clamp(u * 2.2)) * 9)
            c.drawString(ch, cx + 3, y + dy + 5, f, paint((0, 4, 12), al * 0.55, sigma=7))
            c.drawString(ch, cx, y + dy, f, paint(rgb, al, sigma=blur))
            cx += f.measureText(ch)
        x += wdw * swell + space


# ---------------------------------------------------------------- post
_GRAIN = _VIG = _LUT = None


def _lut():
    """Cyanotype grade: lifted, cool shadows; clean whites; slight teal in the mids."""
    x = np.linspace(0, 1, 256)
    s = 0.7 * x + 0.3 * x * x * (3 - 2 * x)
    r = np.clip(0.012 + s * 0.985, 0, 1)
    g = np.clip(0.02 + s * 0.985, 0, 1)
    b = np.clip(0.045 + s * 0.96, 0, 1)
    return [(v * 255).astype(np.uint8) for v in (r, g, b)]


def post(img, t, bloom=1.0, ca=0.7, grain=5.0, flash=0.0, split=0.0):
    """img float32 HxWx3. Bloom only on saturated warm light (sulfur and lava), so the white linework stays crisp."""
    global _GRAIN, _VIG, _LUT
    if _LUT is None:
        _LUT = _lut()
        rng = np.random.default_rng(3)
        _GRAIN = [(rng.normal(0, 1, (H // 2, W // 2)) * grain).astype(np.float32) for _ in range(8)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _VIG = (1 - 0.6 * np.clip(r - 0.35, 0, 1) ** 1.4)[..., None].astype(np.float32)
    if bloom > 0:
        small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        mx = small.max(axis=2, keepdims=True)
        warm = np.clip((small[..., 0] - small[..., 2] - 60) / 120, 0, 1)[..., None] * np.clip((mx - 170) / 70, 0, 1)
        hot = np.clip((mx - 245) / 10, 0, 1)
        bright = small * np.maximum(warm, hot * 0.5)
        b1 = cv2.GaussianBlur(bright, (0, 0), 5)
        b2 = cv2.GaussianBlur(bright, (0, 0), 18)
        img = img + cv2.resize(b1 * 0.8 + b2 * 1.0, (W, H), interpolation=cv2.INTER_LINEAR) * bloom
    k = 0.0016 * ca + split * 0.012
    if k > 0:
        Mr = np.float32([[1 + k, 0, -W / 2 * k], [0, 1 + k, -H / 2 * k]])
        Mb = np.float32([[1 - k, 0, W / 2 * k], [0, 1 - k, H / 2 * k]])
        img = img.copy()
        img[..., 0] = cv2.warpAffine(img[..., 0], Mr, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img[..., 2] = cv2.warpAffine(img[..., 2], Mb, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    img = img * _VIG
    if flash > 0:
        img = img + (np.array(HOT, np.float32) - img) * flash
    img = img + cv2.resize(_GRAIN[int(t * FPS) % 8], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    out = np.clip(img, 0, 255).astype(np.uint8)
    for ch in range(3):
        out[..., ch] = cv2.LUT(out[..., ch], _LUT[ch])
    return out


def render(draw, t, samples=3, shutter=0.5, **kw):
    s = skia.Surface(W, H)
    c = s.getCanvas()
    acc = None
    for i in range(samples):
        ts = t + ((i + 0.5) / samples - 0.5) * shutter / FPS if samples > 1 else t
        c.clear(col(NIGHT))
        draw(c, ts)
        f = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
        acc = f if acc is None else acc + f
    return post(acc / samples, t, **kw)
