""""Magic Lantern" drawing kit for the Carrington Short.

  * Every scene is a hand-painted glass lantern slide thrown on a screen in a dark room (the 1850s medium):
    warm black glass, a projector hot-spot, limelight-white engraved linework
  * Hand tinting: transparent dyes laid on by brush, mottled and slightly off-register from the engraving
  * Light is additive: the Sun, the aurora and the current in the wires glow and halate like real projected light
  * The magnetogram (the Kew needle trace) is the master signal: it drives flicker, sparks and caption jitter
  * Captions are projected: each letter pulls into focus (soft, large, colour-split -> sharp)
  * Post: projector flicker and gate weave, halation on all highlights, dust on the glass, grain
"""
import json, math, os

import cv2
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "deep-hole", "fonts")          # shared fonts
DATA_DIR = os.path.join(HERE, "..", "krakatoa", "data")            # shared Natural Earth coastlines
cv2.setNumThreads(1)

# ---------------------------------------------------------------- palette
VOID = (13, 11, 15)            # opaque glass, the dark room
GLASS = (27, 22, 36)           # night glass
NIGHT = (44, 34, 82)           # indigo dye for skies
LIME = (255, 242, 216)         # limelight: all linework and text
SILVER = (150, 142, 136)       # secondary labels, faint engraving
CARD = (236, 222, 190)         # the paper of labels, the projection screen, the telegraph tape
SEPIA = (92, 70, 48)           # ink on CARD
SUN = (255, 178, 52)           # the Sun and everything it throws at us
FLARE = (255, 252, 240)        # white-hot: the flare only
AUR_G = (84, 255, 168)         # aurora green (oxygen, low)
AUR_R = (255, 64, 104)         # aurora crimson (oxygen, high)
SPARK = (150, 214, 255)        # electric current in our wires

FONTS = {
    "regular": "InterDisplay-Regular.otf", "medium": "InterDisplay-Medium.otf", "semibold": "InterDisplay-SemiBold.otf",
    "bold": "InterDisplay-Bold.otf", "black": "InterDisplay-Black.otf", "light": "InterDisplay-Light.otf",
    "serif": "NotoSerifDisplay-Italic.ttf", "serif_bold": "NotoSerifDisplay-BoldItalic.ttf",
    "serif_roman": "NotoSerifDisplay-Regular.ttf",
    "mono": "NotoSansMono-Regular.ttf", "mono_bold": "NotoSansMono-Bold.ttf",
}
_TF, _F = {}, {}


# ---------------------------------------------------------------- basics
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t1)


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


def out_expo(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def spring(u, k=7.0, w=10.0):
    u = clamp(u)
    return 1 - math.exp(-k * u) * math.cos(w * u)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(a, b, t):
    t = clamp(t)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def col(rgb, a=255):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(clamp(a / 255) * 255))


def paint(rgb, a=255, sigma=0.0, stroke=0.0, blend=None, cap=True):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if sigma > 0.25:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    if blend:
        p.setBlendMode(blend)
    return p


ADD = skia.BlendMode.kPlus
SCREEN = skia.BlendMode.kScreen
MULT = skia.BlendMode.kMultiply


def dashed(p, on, off, phase=0):
    p.setPathEffect(skia.DashPathEffect.Make([on, off], phase))
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


def label(c, s, x, y, size, kind="medium", rgb=LIME, a=255, align="left", tracking=0.0, sigma=0.0, blend=None):
    if a <= 1:
        return
    f = font(kind, size)
    w = width(s, kind, size, tracking)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    p = paint(rgb, a, sigma, blend=blend)
    for ch in s:
        c.drawString(ch, x0, y, f, p)
        x0 += f.measureText(ch) + tracking * size


def polyline(pts):
    p = skia.Path()
    for i, (x, y) in enumerate(pts):
        (p.lineTo if i else p.moveTo)(x, y)
    return p


# ---------------------------------------------------------------- noise + glass
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


def _img(rgba):
    return skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType,
                                alphaType=skia.kUnpremul_AlphaType)


_GLASS = {}


def glass_image(base=GLASS):
    """The dark slide: warm black glass with a faint painted mottle and the cool pull of the projector hot-spot."""
    if base not in _GLASS:
        n = fbm(H // 2, W // 2, 41, 260, 5)
        brush = cv2.GaussianBlur(np.random.default_rng(3).random((H // 2, W // 2)).astype(np.float32), (0, 0),
                                 sigmaX=18, sigmaY=2.5)          # horizontal brush drag of the black varnish
        k = 1 + (n - 0.5) * 0.35 + (brush - 0.5) * 0.9
        k = cv2.resize(k, (W, H), interpolation=cv2.INTER_CUBIC)
        rgb = np.array(base, np.float32)[None, None, :] * k[..., None]
        rgba = np.dstack([np.clip(rgb, 0, 255), np.full((H, W), 255, np.float32)]).astype(np.uint8)
        _GLASS[base] = _img(rgba)
    return _GLASS[base]


def glass(c, base=GLASS, a=255):
    p = skia.Paint()
    p.setAlphaf(a / 255)
    c.drawImage(glass_image(base), 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)


_MOTTLE = None


def mottle_image():
    """Alpha-only texture for hand-laid dye: pooled at brush ends, thin in the middle, with fine pigment."""
    global _MOTTLE
    if _MOTTLE is None:
        a = fbm(H // 2, W // 2, 77, 90, 5) * 0.65 + fbm(H // 2, W // 2, 78, 6, 2) * 0.35
        a = cv2.resize(0.55 + 0.45 * a, (W, H), interpolation=cv2.INTER_CUBIC)
        rgba = np.zeros((H, W, 4), np.uint8)
        rgba[..., :3] = 255
        rgba[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
        _MOTTLE = _img(rgba)
    return _MOTTLE


def tint(c, path, rgb, a=200, off=(5, 4), blur=3.0, blend=SCREEN):
    """Hand-tinted dye on the glass: mottled, soft-edged and a few pixels off-register from the engraving."""
    if a <= 1:
        return
    c.save()
    c.translate(*off)
    m = skia.Paint(AntiAlias=True)
    m.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    c.saveLayer(None, None)
    c.drawPath(path, m)
    p = skia.Paint()
    p.setColorFilter(skia.ColorFilters.Blend(col(rgb, a), skia.BlendMode.kSrcIn))
    p.setBlendMode(skia.BlendMode.kSrcIn)
    c.translate(-off[0], -off[1])
    c.drawImage(mottle_image(), 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.restore()
    c.restore()
    # the dye layer above was composited normally; a second pass in `blend` gives it the glow of light through glass
    if blend:
        c.save()
        c.translate(*off)
        c.drawPath(path, paint(rgb, a * 0.12, sigma=blur * 4, blend=blend))
        c.restore()


# ---------------------------------------------------------------- linework + light
def engrave(c, path, rgb=LIME, a=255, wd=1.6, halo=0.6):
    """Engraved line on the slide: a thin bright core with a little halation (light leaking through the scratch)."""
    if a <= 1:
        return
    if halo:
        c.drawPath(path, paint(rgb, a * 0.22 * halo, sigma=wd * 2 + 1.5, stroke=wd * 3, blend=SCREEN))
    c.drawPath(path, paint(rgb, a, stroke=wd))


def light(c, path, rgb=SUN, a=255, wd=3.0, k=1.0, core=FLARE):
    """Projected light: wide bloom, tight bloom, coloured line, hot white core. Additive."""
    if a <= 1:
        return
    c.drawPath(path, paint(rgb, a * 0.18 * k, sigma=26, stroke=wd * 9, blend=ADD))
    c.drawPath(path, paint(rgb, a * 0.38 * k, sigma=7, stroke=wd * 3, blend=ADD))
    c.drawPath(path, paint(rgb, a, stroke=wd, blend=SCREEN))
    if core:
        c.drawPath(path, paint(core, a * 0.7, stroke=max(0.8, wd * 0.35), blend=SCREEN))


def bloom_dot(c, x, y, r, rgb, a=255, k=1.0):
    c.drawCircle(x, y, r * 6, paint(rgb, a * 0.08 * k, sigma=r * 4, blend=ADD))
    c.drawCircle(x, y, r * 2.2, paint(rgb, a * 0.35 * k, sigma=r, blend=ADD))
    c.drawCircle(x, y, r, paint(mix(rgb, FLARE, 0.6), a, blend=SCREEN))


def hatch(c, path, a=60, step=7.0, ang=60, rgb=LIME, wd=1.0, cross=False, wobble=0.0, seed=0):
    c.save()
    c.clipPath(path, doAntiAlias=True)
    b = path.getBounds()
    cx, cy = b.centerX(), b.centerY()
    L = math.hypot(b.width(), b.height()) / 2 + 4
    rng = np.random.default_rng(seed)
    for aa in ((ang, ang + 90) if cross else (ang,)):
        r = math.radians(aa)
        dx, dy = math.cos(r), math.sin(r)
        nx, ny = -dy, dx
        k = -L
        while k <= L:
            j = rng.normal(0, wobble) if wobble else 0
            x0, y0 = cx + nx * (k + j), cy + ny * (k + j)
            c.drawLine(x0 - dx * L, y0 - dy * L, x0 + dx * L, y0 + dy * L, paint(rgb, a, stroke=wd))
            k += step
    c.restore()


def stipple(c, path, n=900, a=120, seed=1, rgb=LIME, r=1.1):
    rng = np.random.default_rng(seed)
    b = path.getBounds()
    c.save()
    c.clipPath(path, doAntiAlias=True)
    for _ in range(n):
        c.drawCircle(b.left() + rng.random() * b.width(), b.top() + rng.random() * b.height(), r * (0.5 + rng.random()),
                     paint(rgb, a))
    c.restore()


def stars(c, n=260, seed=4, rect=(0, 0, W, H), a=255, t=0.0, twinkle=1.0):
    rng = np.random.default_rng(seed)
    x0, y0, w, h = rect
    for i in range(n):
        x, y = x0 + rng.random() * w, y0 + rng.random() * h
        m = rng.random() ** 3
        tw = 0.75 + 0.25 * math.sin(t * (1.5 + rng.random() * 3) + i) * twinkle
        r = 0.6 + m * 1.8
        c.drawCircle(x, y, r * 3, paint(LIME, a * 0.08 * m * tw, sigma=r * 2, blend=ADD))
        c.drawCircle(x, y, r, paint(LIME, a * (0.25 + 0.75 * m) * tw, blend=SCREEN))


# ---------------------------------------------------------------- the magnetogram (drives the whole film)
def magnetogram(u, seed=0, crochet=0.32, storm=0.62, quiet=0.025):
    """Deterministic needle reading (about -1..1, negative = field pushed down) at position u in 0..1.
    A quiet daily wobble, the small sharp 'crochet' at the moment of the flare, then the storm: a sudden jump when
    the cloud hits, a long violent main phase that runs off the scale, and a slow recovery."""
    s = seed * 1.37
    v = quiet * (math.sin(u * 37 + s) + 0.5 * math.sin(u * 151 + 2 * s) + 0.3 * math.sin(u * 433 + 3 * s))
    v += 0.10 * math.exp(-((u - crochet) / 0.004) ** 2)                      # the flare's crochet
    d = u - storm
    if d > 0:
        v += 0.35 * (1 - math.exp(-d / 0.004)) * math.exp(-d / 0.03)          # sudden commencement
        main = (1 - math.exp(-d / 0.03)) * math.exp(-d / 0.25)
        jag = math.sin(d * 310 + s) * 0.45 + math.sin(d * 870 + 2 * s) * 0.3 + math.sin(d * 2100 + s) * 0.25
        v -= 1.5 * main * (0.7 + 0.5 * jag)
    return v


# ---------------------------------------------------------------- projection + coastlines
_LAND = {}


def land(name):
    if name not in _LAND:
        _LAND[name] = json.load(open(os.path.join(DATA_DIR, f"{name}.json")))
    return _LAND[name]


class Ortho:
    """Orthographic projection centred on (lon0, lat0), then a 2D similarity (scale R, rotation, offset)."""

    def __init__(self, lon0, lat0, R, cx, cy, rot=0.0):
        self.l0, self.p0 = math.radians(lon0), math.radians(lat0)
        self.R, self.cx, self.cy, self.rot = R, cx, cy, math.radians(rot)

    def __call__(self, lon, lat):
        l, p = math.radians(lon) - self.l0, math.radians(lat)
        x = math.cos(p) * math.sin(l)
        y = math.cos(self.p0) * math.sin(p) - math.sin(self.p0) * math.cos(p) * math.cos(l)
        z = math.sin(self.p0) * math.sin(p) + math.cos(self.p0) * math.cos(p) * math.cos(l)
        cr, sr = math.cos(self.rot), math.sin(self.rot)
        X, Y = x * cr - y * sr, x * sr + y * cr
        return self.cx + X * self.R, self.cy - Y * self.R, z


_EQ = None


def _eq_mask():
    global _EQ
    if _EQ is None:
        m = np.zeros((2160, 4320), np.uint8)
        for ring in land("world"):
            pts = np.array([[(lon + 180) * 12, (90 - lat) * 12] for lon, lat in ring], np.float32)
            cv2.fillPoly(m, [np.round(pts * 4).astype(np.int32)], 255, lineType=cv2.LINE_8, shift=2)
        _EQ = m
    return _EQ


_GLOBE = {}


def globe_land_path(proj, ss=2):
    """Exact land outline on an orthographic globe (inverse-projected land raster traced back to vectors)."""
    key = (proj.l0, proj.p0, proj.R, proj.cx, proj.cy, proj.rot)
    if key in _GLOBE:
        return _GLOBE[key]
    R = proj.R
    n = int(2 * R * ss) + 2
    g = (np.arange(n, dtype=np.float32) / ss - R)
    X, Yd = np.meshgrid(g, g)
    Y = -Yd
    cr, sr = math.cos(-proj.rot), math.sin(-proj.rot)
    x, y = (X * cr - Y * sr) / R, (X * sr + Y * cr) / R
    rho2 = x * x + y * y
    inside = rho2 <= 1
    z = np.sqrt(np.clip(1 - rho2, 0, 1))
    lat = np.degrees(np.arcsin(np.clip(z * math.sin(proj.p0) + y * math.cos(proj.p0), -1, 1)))
    lon = np.degrees(proj.l0 + np.arctan2(x, z * math.cos(proj.p0) - y * math.sin(proj.p0)))
    lon = (lon + 180) % 360 - 180
    eq = _eq_mask()
    iy = np.clip(((90 - lat) * 12).astype(np.int32), 0, 2159)
    ix = np.clip(((lon + 180) * 12).astype(np.int32), 0, 4319)
    m = np.where(inside, eq[iy, ix], 0).astype(np.uint8)
    m = cv2.GaussianBlur(m, (0, 0), 0.8 * ss)
    _, m = cv2.threshold(m, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    path = skia.Path()
    path.setFillType(skia.PathFillType.kEvenOdd)
    ox, oy = proj.cx - R, proj.cy - R
    for cnt in contours:
        if len(cnt) < 3:
            continue
        for i, (px, py) in enumerate(cnt[:, 0, :]):
            (path.lineTo if i else path.moveTo)(ox + px / ss, oy + py / ss)
        path.close()
    if len(_GLOBE) > 6:
        _GLOBE.clear()
    _GLOBE[key] = path
    return path


def graticule(c, proj, a=1.0, step=15, rgb=SILVER, wd=0.9):
    p = paint(rgb, 90 * a, stroke=wd)
    for lon in range(-180, 180, step):
        _poly(c, [proj(lon, lat) for lat in range(-90, 91, 3)], p)
    for lat in range(-75, 90, step):
        _poly(c, [proj(lon, lat) for lon in range(-180, 181, 3)], p)


def _poly(c, pts, p):
    path, pen = skia.Path(), False
    for x, y, z in pts:
        if z < 0:
            pen = False
            continue
        (path.lineTo if pen else path.moveTo)(x, y)
        pen = True
    c.drawPath(path, p)


def lat_circle(proj, lat, n=361):
    path, pen = skia.Path(), False
    for lon in np.linspace(-180, 180, n):
        x, y, z = proj(lon, lat)
        if z < 0:
            pen = False
            continue
        (path.lineTo if pen else path.moveTo)(x, y)
        pen = True
    return path


# ---------------------------------------------------------------- slide furniture
def slide_label(c, n, text, x, y, a=255, align="left", size=20):
    """The paper label every lantern slide carried: cream tab, slide number, red thumb-spot."""
    s = f"SLIDE {n}  ·  {text}"
    w = width(s, "mono", size, 0.12) + 34
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0 - 14, y - size * 1.1, w + 28, size * 1.7), 4, 4)
    c.drawRRect(r.makeOffset(0, 4), paint((0, 0, 0), a * 0.5, sigma=6))
    c.drawRRect(r, paint(CARD, a * 0.96))
    c.drawCircle(x0 + 6, y - size * 0.27, 7, paint(AUR_R, a * 0.9))
    label(c, s, x0 + 26, y, size, "mono", SEPIA, a, tracking=0.12)


def tag(c, x, y, text, rgb=LIME, a=255, size=20, align="left", kind="mono_bold"):
    """A small mono callout on dark glass, with a thin rule under it."""
    w = width(text, kind, size, 0.1)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    c.drawRect(skia.Rect.MakeXYWH(x0 - 12, y - size * 1.05, w + 24, size * 1.55), paint(VOID, a * 0.75, sigma=4))
    label(c, text, x0, y, size, kind, rgb, a, tracking=0.1)
    c.drawLine(x0, y + size * 0.4, x0 + w, y + size * 0.4, paint(rgb, a * 0.6, stroke=1.2))


def leader(c, x0, y0, x1, y1, rgb=LIME, a=255):
    c.drawLine(x0, y0, x1, y1, paint(rgb, a * 0.8, stroke=1.3))
    c.drawCircle(x0, y0, 3.5, paint(rgb, a))


def dim_line(c, x1, y1, x2, y2, text, a=255, rgb=LIME, size=22, tick=10):
    ang = math.atan2(y2 - y1, x2 - x1)
    p = paint(rgb, a * 0.85, stroke=1.4)
    c.drawLine(x1, y1, x2, y2, p)
    nx, ny = -math.sin(ang) * tick, math.cos(ang) * tick
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
    c.drawRect(skia.Rect.MakeXYWH(-tw / 2 - 12, -size * 0.85, tw + 24, size * 1.25), paint(VOID, a))
    label(c, text, 0, 0, size, "mono_bold", rgb, a, "center", tracking=0.08)
    c.restore()


def iris(c, cx, cy, r, a=255):
    """Lantern iris: everything outside the circle goes to the dark room."""
    p = skia.Path()
    p.addRect(skia.Rect.MakeWH(W, H))
    p.addCircle(cx, cy, r)
    p.setFillType(skia.PathFillType.kEvenOdd)
    c.drawPath(p, paint(VOID, a))
    c.drawCircle(cx, cy, r, paint(VOID, a * 0.8, sigma=r * 0.05, stroke=r * 0.08))


# ---------------------------------------------------------------- the Sun
_SUNTEX = {}


def sun_texture(R, seed=0):
    """Granulation + limb darkening for a disc of radius R, as an RGBA image (alpha = disc)."""
    key = (int(R), seed)
    if key not in _SUNTEX:
        n = int(2 * R) + 4
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
        r = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / R
        mu = np.sqrt(np.clip(1 - r ** 2, 0, 1))
        limb = 1 - 0.62 * (1 - mu) - 0.2 * (1 - mu) ** 2              # limb darkening
        g1 = fbm(n, n, 90 + seed, max(R / 70, 2.0), 2, 0.5)
        gran = 1 - np.abs(g1 - 0.5) * 2                               # bright cells, dark lanes
        mot = fbm(n, n, 91 + seed, R / 3, 3)
        fac = np.clip((fbm(n, n, 92 + seed, R / 14, 3) - 0.62) * 4, 0, 1) * np.clip((r - 0.7) / 0.3, 0, 1)
        v = limb * (0.8 + 0.22 * gran ** 1.5 + 0.08 * (mot - 0.5)) + 0.12 * fac
        rgb = np.stack([255 * np.clip(v * 1.05, 0, 1), 205 * v ** 1.25, 95 * v ** 2.2], -1)
        alpha = np.clip((1 - r) * R * 0.8, 0, 1)
        rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
        if len(_SUNTEX) > 8:
            _SUNTEX.clear()
        _SUNTEX[key] = _img(rgba)
    return _SUNTEX[key]


def sun_disc(c, cx, cy, R, a=255, corona=1.0, seed=0, rot=0.0):
    if corona:
        for rr, al, sg in ((2.6, 0.10, R * 0.9), (1.6, 0.22, R * 0.35), (1.15, 0.45, R * 0.08)):
            c.drawCircle(cx, cy, R * rr * 0.75, paint(SUN, a * al * corona, sigma=sg, blend=ADD))
    img = sun_texture(R, seed)
    p = skia.Paint()
    p.setAlphaf(a / 255)
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.drawImage(img, -img.width() / 2, -img.height() / 2, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.restore()


def sunspot(c, x, y, r, a=255, seed=0, squash=1.0, ang=0.0):
    """An engraved sunspot: dark ragged umbra, a fibrous penumbra drawn as radial strokes."""
    rng = np.random.default_rng(seed)
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(1, squash)
    pen = skia.Path()
    um = skia.Path()
    for k in range(48):
        th = k / 48 * 2 * math.pi
        rp = r * (1 + 0.18 * math.sin(3 * th + seed) + 0.1 * rng.normal())
        ru = r * 0.45 * (1 + 0.25 * math.sin(2 * th + 2 * seed) + 0.1 * rng.normal())
        (pen.lineTo if k else pen.moveTo)(math.cos(th) * rp, math.sin(th) * rp)
        (um.lineTo if k else um.moveTo)(math.cos(th) * ru, math.sin(th) * ru)
    pen.close()
    um.close()
    c.drawPath(pen, paint((120, 60, 20), a * 0.75, sigma=r * 0.08))
    for k in range(70):
        th = rng.random() * 2 * math.pi
        r0, r1 = r * 0.42, r * (0.85 + 0.25 * rng.random())
        c.drawLine(math.cos(th) * r0, math.sin(th) * r0, math.cos(th) * r1, math.sin(th) * r1,
                   paint((70, 30, 10), a * 0.5, stroke=0.9))
    c.drawPath(um, paint((28, 12, 6), a))
    c.restore()


# ---------------------------------------------------------------- the aurora
def aurora(c, t, x0, x1, base_y, height, seed=0, a=1.0, n=420, folds=3, lean=0.0):
    """A curtain: a folded ribbon of vertical rays, green at the foot fading to crimson at the top, rippling.
    Additive, drawn twice (soft bloom + crisp rays)."""
    rng = np.random.default_rng(seed)
    ph = rng.random(6) * 6.28
    sh = skia.GradientShader.MakeLinear(
        [skia.Point(0, base_y), skia.Point(0, base_y - height)],
        [col(AUR_G, 255), col(mix(AUR_G, AUR_R, 0.35), 200), col(AUR_R, 170), col(AUR_R, 0)],
        [0.0, 0.25, 0.6, 1.0])
    hem = []
    for pas in range(2):
        for i in range(n):
            u = i / (n - 1)
            x = x0 + (x1 - x0) * u
            fold = math.sin(u * folds * 2 * math.pi + ph[0] + t * 0.6) * 60 + math.sin(u * 13 + ph[1] - t * 0.9) * 18
            y = base_y + fold * 0.6 + math.sin(u * 5 + ph[2]) * 40
            br = (0.5 + 0.5 * math.sin(u * 37 + ph[3] + t * 2.2)) * (0.6 + 0.4 * math.sin(u * 9 + ph[4] - t * 0.7))
            br *= math.sin(math.pi * u) ** 0.6
            hgt = height * (0.6 + 0.4 * math.sin(u * 7 + ph[5] + t * 0.5))
            p = skia.Paint(AntiAlias=True)
            p.setShader(sh)
            p.setBlendMode(ADD)
            p.setStyle(skia.Paint.kStroke_Style)
            if pas == 0:
                p.setStrokeWidth(7)
                p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
                p.setAlphaf(clamp(0.07 * br * a))
            else:
                if i % 2:
                    continue
                p.setStrokeWidth(1.1 + 1.2 * (math.sin(u * 211 + ph[0]) > 0.6))
                p.setAlphaf(clamp(0.5 * br * a))
            c.save()
            c.translate(0, y - base_y)
            c.drawLine(x, base_y, x + lean * hgt, base_y - hgt, p)
            c.restore()
            if pas:
                hem.append((x, y, br))
    # the hem: the sharp bright green lower edge every curtain has
    for k in range(1, len(hem)):
        (xa, ya, ba), (xb, yb, bb) = hem[k - 1], hem[k]
        c.drawLine(xa, ya, xb, yb, paint(AUR_G, 255 * a * clamp(0.25 + 0.75 * ba), stroke=1.6, blend=ADD))
        c.drawLine(xa, ya, xb, yb, paint(AUR_G, 120 * a * ba, sigma=6, stroke=8, blend=ADD))


# ---------------------------------------------------------------- captions (projected into focus)
CAP_Y = 1390


def _word_layout(words, size, emph, x=None):
    kinds = ["serif_bold" if i in emph else "bold" for i in range(len(words))]
    sizes = [size * (1.14 if i in emph else 1.0) for i in range(len(words))]
    space = size * 0.27
    ws = [width(wd, k, s) for wd, k, s in zip(words, kinds, sizes)]
    total = sum(ws) + space * (len(words) - 1)
    x = W / 2 - total / 2 if x is None else x
    xs = []
    for w_ in ws:
        xs.append(x)
        x += w_ + space
    return kinds, sizes, ws, xs, total


def projected_char(c, ch, x, y, f, rgb, al, focus, glow_rgb=None):
    """One letter thrown by the lantern. focus 0..1: out of focus = large, soft and split into red/blue fringes;
    in focus = crisp. Emphasis letters also halate in their colour."""
    if al <= 1:
        return
    blur = (1 - focus) * 9
    split = (1 - focus) * 7
    sc = 1 + (1 - focus) * 0.18
    cw = f.measureText(ch)
    c.save()
    c.translate(x + cw / 2, y)
    c.scale(sc, sc)
    c.translate(-cw / 2, 0)
    if glow_rgb:
        c.drawString(ch, 0, 0, f, paint(glow_rgb, al * 0.55, sigma=14, blend=ADD))
    if split > 0.4:
        c.drawString(ch, -split, 0, f, paint((255, 60, 60), al * 0.5, sigma=blur * 0.6, blend=ADD))
        c.drawString(ch, split, 0, f, paint((60, 120, 255), al * 0.5, sigma=blur * 0.6, blend=ADD))
    c.drawString(ch, 0, 0, f, paint(rgb, al * (0.55 + 0.45 * focus), sigma=blur * 0.5))
    c.restore()


def caption(c, words, t, t0s, y=CAP_Y, size=80, emph=None, jitter=None, dur=0.45, a=1.0, plate=True, x=None):
    """Projected captions. Each word is pulled into focus at its spoken time. emph maps word index -> colour;
    those words switch to the serif italic and halate. jitter(t) in 0..1 (the magnetogram) shakes the active word."""
    emph = emph or {}
    kinds, sizes, ws, xs, total = _word_layout(words, size, emph, x)
    if total > W - 130:                     # never wider than the safe area
        size *= (W - 130) / total
        kinds, sizes, ws, xs, total = _word_layout(words, size, emph, x)
    if plate:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(xs[0] - 40, y - size * 0.95, total + 80, size * 1.5),
                                          30, 30), paint(VOID, 170 * a, sigma=24))
    active = max([i for i, ts in enumerate(t0s) if t >= ts] or [-1])
    amp = jitter(t) if jitter else 0.0
    rng = np.random.default_rng(int(t * FPS) + 11)
    for i, wd in enumerate(words):
        u0 = t - t0s[i]
        if u0 < -0.05:
            continue
        f = font(kinds[i], sizes[i])
        rgb = emph.get(i, LIME)
        cx = xs[i]
        for j, ch in enumerate(wd):
            u = (u0 - j * 0.022) / dur
            if u <= 0:
                cx += f.measureText(ch)
                continue
            jit = amp * (1.8 if i == active else 0.6)
            dx, dy = rng.normal(0, jit, 2) if jit > 0.05 else (0, 0)
            projected_char(c, ch, cx + dx, y + dy, f, rgb, clamp(u * 2.5) * 255 * a, out_cubic(u),
                           rgb if i in emph else None)
            cx += f.measureText(ch)
    return xs, ws


def caption_on_path(c, text, pts, start, size=64, kind="bold", rgb=LIME, a=255, spacing=1.0, glow_rgb=None):
    """Letters riding a polyline (a field line, the edge of the cloud), each rotated to the local tangent."""
    f = font(kind, size)
    seg = [0.0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg.append(seg[-1] + math.hypot(x1 - x0, y1 - y0))

    def at(d):
        i = int(np.searchsorted(seg, d)) - 1
        i = max(0, min(i, len(pts) - 2))
        u = (d - seg[i]) / max(seg[i + 1] - seg[i], 1e-6)
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, math.degrees(math.atan2(y1 - y0, x1 - x0))

    d = start
    for ch in text:
        cw = f.measureText(ch) * spacing
        x, y, ang = at(d + cw / 2)
        c.save()
        c.translate(x, y)
        c.rotate(ang)
        if glow_rgb:
            c.drawString(ch, -cw / 2, 0, f, paint(glow_rgb, a * 0.5, sigma=12, blend=ADD))
        c.drawString(ch, -cw / 2, 0, f, paint(rgb, a))
        c.restore()
        d += cw


MORSE = {"A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....", "I": "..",
         "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
         "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--..",
         "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-", "5": ".....", "6": "-....",
         "7": "--...", "8": "---..", "9": "----.", ".": ".-.-.-", ",": "--..--", "?": "..--.."}


# ---------------------------------------------------------------- post (the projector)
_GRAIN = _VIG = _DUST = None


def _dust():
    """Specks and a couple of hairs on the slide glass (dark in highlights, faint everywhere)."""
    rng = np.random.default_rng(12)
    m = np.zeros((H, W), np.float32)
    for _ in range(140):
        cv2.circle(m, (int(rng.random() * W), int(rng.random() * H)), int(1 + rng.random() ** 4 * 4), 1.0, -1,
                   cv2.LINE_AA)
    for _ in range(3):
        x, y = rng.random() * W, rng.random() * H
        pts = []
        ang = rng.random() * 6.28
        for k in range(60):
            ang += rng.normal(0, 0.12)
            x, y = x + math.cos(ang) * 4, y + math.sin(ang) * 4
            pts.append((x, y))
        cv2.polylines(m, [np.int32(pts)], False, 0.8, 1, cv2.LINE_AA)
    return cv2.GaussianBlur(m, (0, 0), 0.8)


def post(img, t, halation=1.0, ca=0.8, grain=5.0, flicker=1.0, weave=1.0, shake=0.0):
    """img float32 HxWx3. The projector: hot-spot falloff, halation (warm bloom around every bright light), lens
    fringing, flicker and gate weave from the limelight and the slide carrier, dust on the glass, grain."""
    global _GRAIN, _VIG, _DUST
    if _GRAIN is None:
        rng = np.random.default_rng(5)
        _GRAIN = [(rng.normal(0, 1, (H // 2, W // 2)) * grain).astype(np.float32) for _ in range(8)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.46) / (H * 0.6)) ** 2)
        v = 1.06 - 0.5 * np.clip(r - 0.25, 0, 1) ** 1.6
        _VIG = np.dstack([v, v ** 1.08, v ** 1.2]).astype(np.float32)     # lamp falloff, warm at the edge
        _DUST = _dust()
        m = np.zeros((H, W), np.float32)
        cv2.rectangle(m, (34, 34), (W - 35, H - 35), 1.0, -1)
        m = cv2.GaussianBlur(m, (0, 0), 14)
        _VIG = _VIG * (0.28 + 0.72 * m)[..., None]
    rng = np.random.default_rng(int(t * FPS) * 7 + 1)
    dx = weave * 0.7 * math.sin(t * 5.1) + (rng.normal(0, shake * 9) if shake > 0 else 0)
    dy = weave * 0.9 * math.sin(t * 3.7 + 1) + (rng.normal(0, shake * 9) if shake > 0 else 0)
    if abs(dx) + abs(dy) > 0.05:
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if halation > 0:
        small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        lum = small.max(axis=2, keepdims=True)
        hi = small * np.clip((lum - 238) / 17, 0, 1)
        b = cv2.GaussianBlur(hi, (0, 0), 5) * 0.35 + cv2.GaussianBlur(hi, (0, 0), 20) * 0.4
        b = b * np.array([1.0, 0.8, 0.62], np.float32)                       # halation runs warm
        img = img + cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR) * halation
    k = 0.0014 * ca
    if k > 0:
        Mr = np.float32([[1 + k, 0, -W / 2 * k], [0, 1 + k, -H / 2 * k]])
        Mb = np.float32([[1 - k, 0, W / 2 * k], [0, 1 - k, H / 2 * k]])
        img = img.copy()
        img[..., 0] = cv2.warpAffine(img[..., 0], Mr, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img[..., 2] = cv2.warpAffine(img[..., 2], Mb, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    fl = 1 + flicker * (0.018 * math.sin(t * 47.0) + 0.012 * math.sin(t * 13.3 + 2) + 0.01 * rng.normal())
    img = img * _VIG * fl
    img = img * (1 - _DUST[..., None] * 0.35) + _DUST[..., None] * 6
    g = cv2.resize(_GRAIN[int(t * FPS) % 8], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    img = img + g * (0.6 + img / 255 * 1.4)
    return np.clip(img, 0, 255).astype(np.uint8)


def render(draw, t, samples=3, shutter=0.5, **kw):
    s = skia.Surface(W, H)
    c = s.getCanvas()
    acc = None
    for i in range(samples):
        ts = t + ((i + 0.5) / samples - 0.5) * shutter / FPS if samples > 1 else t
        c.clear(col(VOID))
        draw(c, ts)
        f = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
        acc = f if acc is None else acc + f
    return post(acc / samples, t, **kw)
