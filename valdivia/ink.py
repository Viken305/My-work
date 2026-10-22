""""Seismogram" drawing kit for the Valdivia Short.

  * Bone-white seismograph drum paper (fibres, millimetre grid, drum curvature) and black ink that bleeds slightly
  * Cut-paper layers with real soft shadows for sections (plates, magnitude squares)
  * The quake made visible: a seismograph trace that drives everything (shake, caption jitter, line wobble)
  * Ink engraving for maps: globe and Pacific chart from Natural Earth coastlines (shared with krakatoa/)
  * Captions that live in the graphics: ink-in, trace-driven shake, fault-split, ride-the-wave, sink-into-water
  * Post: paper grain, warm vignette, a touch of lens fringing, ink-red bloom only
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
BONE = (238, 231, 216)        # drum paper
SHADE = (219, 209, 189)       # paper in shadow, land fill
SEPIA = (172, 158, 132)       # grid, secondary labels
INK = (24, 23, 27)            # all linework and text
RED = (222, 52, 38)           # the quake: rupture, energy, shaking
TEAL = (18, 104, 128)         # water: sea, tsunami
BRONZE = (190, 138, 52)       # the ringing planet (part 1 and 5 only)
WHITE = (252, 249, 242)

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


MULT = skia.BlendMode.kMultiply
SCREEN = skia.BlendMode.kScreen


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


def label(c, s, x, y, size, kind="medium", rgb=INK, a=255, align="left", tracking=0.0, sigma=0.0):
    if a <= 1:
        return
    f = font(kind, size)
    w = width(s, kind, size, tracking)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    p = paint(rgb, a, sigma)
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


_PAPER = {}


def paper_image(grid=True):
    """Seismograph drum paper: warm bone white, soft uneven tone, fibres, a faint millimetre grid, and the drum's
    curvature as gentle shading at the top and bottom of the frame."""
    if grid not in _PAPER:
        n = fbm(H // 2, W // 2, 31, 240, 5)
        fib = fbm(H // 2, W // 2, 32, 5, 3, 0.7)
        streak = cv2.GaussianBlur(np.random.default_rng(6).random((H // 2, W // 2)).astype(np.float32), (0, 0),
                                  sigmaX=0.7, sigmaY=14)
        k = (n - 0.5) * 0.05 + (fib - 0.5) * 0.035 + (streak - 0.5) * 0.06
        k = cv2.resize(k, (W, H), interpolation=cv2.INTER_CUBIC)
        yy = np.linspace(-1, 1, H, dtype=np.float32)[:, None]
        drum = 1 - 0.07 * np.abs(yy) ** 3        # the paper curves away from the light at top and bottom
        rgb = np.array(BONE, np.float32)[None, None, :] * (drum + k)[..., None]
        if grid:
            g = np.zeros((H, W), np.float32)
            g[::12, :] = 0.035
            g[:, ::12] = 0.035
            g[::60, :] = 0.08
            g[:, ::60] = 0.08
            g = cv2.GaussianBlur(g, (0, 0), 0.6) * 1.6
            rgb = rgb * (1 - g[..., None]) + np.array(SEPIA, np.float32) * g[..., None]
        rgba = np.dstack([np.clip(rgb, 0, 255), np.full((H, W), 255, np.float32)]).astype(np.uint8)
        _PAPER[grid] = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    return _PAPER[grid]


def paper(c, a=255, grid=True):
    p = skia.Paint()
    p.setAlphaf(a / 255)
    c.drawImage(paper_image(grid), 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)


# ---------------------------------------------------------------- ink
def ink(c, path, rgb=INK, a=255, wd=2.0, bleed=1.0):
    """Ink line: a soft bleed into the paper under a crisp core."""
    if a <= 1:
        return
    if bleed:
        c.drawPath(path, paint(rgb, a * 0.18 * bleed, sigma=wd * 1.2 + 0.8, stroke=wd * 2.2))
    c.drawPath(path, paint(rgb, a, stroke=wd))


def glow(c, path, rgb=RED, a=255, wd=3.0, k=1.0):
    """For the quake energy only: a warm halo printed under the line (multiply keeps it ink-like on paper)."""
    c.drawPath(path, paint(rgb, a * 0.22 * k, sigma=18, stroke=wd * 7, blend=MULT))
    c.drawPath(path, paint(rgb, a * 0.35 * k, sigma=5, stroke=wd * 2.6, blend=MULT))
    c.drawPath(path, paint(rgb, a, stroke=wd))


def cutout(c, path, fill, a=255, lift=10.0, edge=INK, edge_a=200, edge_wd=1.6):
    """A cut-paper layer: soft contact shadow + long shadow, then the fill and an inked edge."""
    c.save()
    c.translate(lift * 0.35, lift * 0.9)
    c.drawPath(path, paint((40, 30, 20), a * 0.22, sigma=lift * 1.4))
    c.restore()
    c.save()
    c.translate(0, lift * 0.25)
    c.drawPath(path, paint((40, 30, 20), a * 0.28, sigma=lift * 0.35))
    c.restore()
    c.drawPath(path, paint(fill, a))
    if edge_a:
        c.drawPath(path, paint(edge, edge_a * a / 255, stroke=edge_wd))


def hatch(c, path, a=60, step=7.0, ang=60, rgb=INK, wd=1.0, cross=False):
    c.save()
    c.clipPath(path, doAntiAlias=True)
    b = path.getBounds()
    cx, cy = b.centerX(), b.centerY()
    L = math.hypot(b.width(), b.height()) / 2 + 4
    for aa in ((ang, ang + 90) if cross else (ang,)):
        r = math.radians(aa)
        dx, dy = math.cos(r), math.sin(r)
        nx, ny = -dy, dx
        k = -L
        while k <= L:
            x0, y0 = cx + nx * k, cy + ny * k
            c.drawLine(x0 - dx * L, y0 - dy * L, x0 + dx * L, y0 + dy * L, paint(rgb, a, stroke=wd))
            k += step
    c.restore()


def stipple(c, path, n=900, a=120, seed=1, rgb=INK, r=1.1):
    rng = np.random.default_rng(seed)
    b = path.getBounds()
    c.save()
    c.clipPath(path, doAntiAlias=True)
    for _ in range(n):
        c.drawCircle(b.left() + rng.random() * b.width(), b.top() + rng.random() * b.height(), r * (0.5 + rng.random()),
                     paint(rgb, a))
    c.restore()


# ---------------------------------------------------------------- the seismogram (drives the whole film)
def trace(u, seed=0, quake=0.5, quiet=0.03, width_=0.06, decay=6.0, freq=1.0):
    """Deterministic seismogram value in about -1..1 at position u (0..1). The quake starts at u=quake with a
    sharp P arrival, a bigger S arrival, then a long ringing coda."""
    s = seed * 1.37
    u = u * freq
    quake = quake * freq
    v = quiet * (math.sin(u * 211 + s) + 0.6 * math.sin(u * 517 + 2 * s) + 0.4 * math.sin(u * 1291 + s * 3))
    d = u - quake
    if d > 0:
        env = (1 - math.exp(-d / (width_ * 0.08))) * math.exp(-d * decay / max(width_ * 10, 1e-3))
        s_arr = max(0.0, d - width_ * 0.35)
        env2 = (1 - math.exp(-s_arr / (width_ * 0.05))) * math.exp(-s_arr * decay / max(width_ * 6, 1e-3)) if s_arr else 0
        osc = (math.sin(d * 900 + s) * 0.55 + math.sin(d * 2300 + 1.3 * s) * 0.3 + math.sin(d * 4100 + s) * 0.15)
        osc2 = math.sin(d * 650 + 0.7 * s) * 0.6 + math.sin(d * 1700 + s) * 0.4
        v += 0.45 * env * osc + 1.0 * env2 * osc2
    return v


def trace_path(x0, y0, w, amp, n=900, seed=0, upto=1.0, **kw):
    p = skia.Path()
    for i in range(n + 1):
        u = i / n
        if u > upto:
            break
        x, y = x0 + u * w, y0 - trace(u, seed, **kw) * amp
        (p.lineTo if i else p.moveTo)(x, y)
    return p


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


class Chart:
    """Plate carrée chart for a lon/lat box; longitudes are unwrapped so the box may cross the date line."""

    def __init__(self, lon0, lon1, lat0, lat1, x, y, w):
        self.lon0, self.lon1, self.lat0, self.lat1 = lon0, lon1, lat0, lat1
        self.x, self.y, self.k = x, y, w / (lon1 - lon0)
        self.w, self.h = w, (lat1 - lat0) * self.k

    def __call__(self, lon, lat):
        while lon < self.lon0 - 180:
            lon += 360
        while lon > self.lon0 + 180:
            lon -= 360
        return self.x + (lon - self.lon0) * self.k, self.y + (self.lat1 - lat) * self.k, 1.0

    def rect(self):
        return skia.Rect.MakeXYWH(self.x, self.y, self.w, self.h)


def land_path(proj, name="world", cull=-0.02):
    path = skia.Path()
    if isinstance(proj, Chart):
        for ring in land(name):
            lons = [ring[0][0]]
            for lon, _ in ring[1:]:   # unwrap so a ring never jumps across the date line
                d = lon - lons[-1]
                lons.append(lons[-1] + d - 360 * round(d / 360))
            mid = (min(lons) + max(lons)) / 2
            for off in (-360, 0, 360):
                m = mid + off
                if m < proj.lon0 - 60 or m > proj.lon1 + 60:
                    continue
                for i, ((_, lat), lon) in enumerate(zip(ring, lons)):
                    x = proj.x + (lon + off - proj.lon0) * proj.k
                    y = proj.y + (proj.lat1 - lat) * proj.k
                    (path.lineTo if i else path.moveTo)(x, y)
                path.close()
        return path
    for ring in land(name):
        pts = [proj(lon, lat) for lon, lat in ring]
        if max(p[2] for p in pts) < cull:
            continue
        for i, (x, y, z) in enumerate(pts):
            if z < cull:   # behind the globe: slide the point out to the limb so fills stay closed and clean
                dx, dy = x - proj.cx, y - proj.cy
                k = proj.R / max(math.hypot(dx, dy), 1e-6)
                x, y = proj.cx + dx * k, proj.cy + dy * k
            (path.lineTo if i else path.moveTo)(x, y)
        path.close()
    return path


_EQ = None


def _eq_mask():
    """Land as an equirectangular raster (1/12 degree). Natural Earth polygons are already split at the date line."""
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
    """Exact land outline on an orthographic globe: inverse-project every pixel of the disc, sample the land raster,
    then trace the mask's contours back into a vector path (no seams, no chords across the far side)."""
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
    _GLOBE[key] = path
    return path


_COAST = {}


def _coast_layer(path, lines, key, rgb):
    """Old-map water lines: thin contours at fixed distances from the coast (distance transform)."""
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
        a = np.maximum(a, np.clip(1 - np.abs(d - L) / 0.8, 0, 1) * (0.55 - 0.1 * k))
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = rgb
    rgba[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    img = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
    _COAST[key] = img
    return img


def engraved_land(c, path, a=1.0, step=6.0, water_lines=(7, 15, 25), key=None, fill=SHADE, water=TEAL):
    """Ink map: teal water lines off the coast, shaded land with fine 45° hatching, inked coastline."""
    if water_lines:
        img = _coast_layer(path, water_lines, key or ("tmp", id(path)), water)
        p = skia.Paint()
        p.setAlphaf(clamp(a))
        c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.drawPath(path, paint(fill, 255 * a))
    hatch(c, path, 70 * a, step, 45, INK, 0.9)
    c.drawPath(path, paint(INK, 110 * a, sigma=1.0, stroke=2.4))
    c.drawPath(path, paint(INK, 235 * a, stroke=1.3))


def graticule(c, proj, a=1.0, step=15, rgb=SEPIA):
    p = paint(rgb, 110 * a, stroke=1.0)
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


def destination(lon, lat, bearing, ang):
    """Point at angular distance ang (rad) from (lon, lat) along bearing (rad)."""
    p1, l1 = math.radians(lat), math.radians(lon)
    p2 = math.asin(math.sin(p1) * math.cos(ang) + math.cos(p1) * math.sin(ang) * math.cos(bearing))
    l2 = l1 + math.atan2(math.sin(bearing) * math.sin(ang) * math.cos(p1), math.cos(ang) - math.sin(p1) * math.sin(p2))
    return math.degrees(l2), math.degrees(p2)


def gc_km(a, b):
    p1, p2 = math.radians(a[1]), math.radians(b[1])
    dl = math.radians(b[0] - a[0])
    return 6371 * math.acos(clamp(math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl), -1, 1))


def small_circle(proj, lon, lat, ang, n=361):
    """Points of the circle ang radians around (lon, lat), projected; breaks the line where it jumps (chart wrap)."""
    out, path, prev = [], skia.Path(), None
    for b in np.linspace(0, 360, n):
        x, y, z = proj(*destination(lon, lat, math.radians(b), ang))
        if z < 0:
            prev = None
            continue
        if prev is None or abs(x - prev[0]) > 200:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
        prev = (x, y)
        out.append((x, y))
    return path, out


# ---------------------------------------------------------------- plate furniture
def fig(c, n, text, x, y, a=255, align="left", size=22):
    """Plate caption in the style of an instrument record: FIG. 3 · SEISMOGRAM, VALDIVIA (on a paper tab)."""
    s = f"FIG. {n}  ·  {text}"
    w = width(s, "mono", size, 0.12)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    r = skia.Rect.MakeXYWH(x0 - 14, y - size * 1.05, w + 28, size * 1.6)
    c.drawRect(r.makeOffset(2, 4), paint((40, 30, 20), a * 0.18, sigma=5))
    c.drawRect(r, paint(WHITE, a * 0.95))
    c.drawLine(x0 - 14, y + size * 0.55, x0 + w + 14, y + size * 0.55, paint(RED, a, stroke=2.0))
    label(c, s, x, y, size, "mono", INK, a * 0.9, align, tracking=0.12)


def dim_line(c, x1, y1, x2, y2, text, a=255, rgb=INK, size=24, off=0, tick=11):
    ang = math.atan2(y2 - y1, x2 - x1)
    p = paint(rgb, a * 0.85, stroke=1.5)
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
    c.drawRect(skia.Rect.MakeXYWH(-tw / 2 - 12, -size * 0.85 + off, tw + 24, size * 1.25), paint(BONE, a))
    label(c, text, 0, off, size, "mono_bold", rgb, a, "center", tracking=0.08)
    c.restore()


def pin(c, x, y, name, sub=None, a=255, rgb=INK, side=1, size=28, sub_rgb=SEPIA):
    c.drawCircle(x, y, 6.5, paint(rgb, a))
    c.drawCircle(x, y, 14, paint(rgb, a * 0.7, stroke=1.4))
    tx = x + 26 * side
    al = "left" if side > 0 else "right"
    label(c, name, tx, y + size * 0.35, size, "semibold", rgb, a, al, tracking=0.1)
    if sub:
        label(c, sub, tx, y + size * 0.35 + 32, 20, "mono", sub_rgb, a, al, tracking=0.1)


def star(c, x, y, r, rgb=RED, a=255):
    p = skia.Path()
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.42
        ang = math.radians(-90 + k * 36)
        (p.lineTo if k else p.moveTo)(x + math.cos(ang) * rr, y + math.sin(ang) * rr)
    p.close()
    c.drawPath(p, paint(rgb, a * 0.3, sigma=8, blend=MULT))
    c.drawPath(p, paint(rgb, a))
    c.drawPath(p, paint(INK, a * 0.8, stroke=1.2))


def card(c, x, y, w, h, a=255, lift=8):
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 6, 6)
    c.drawRRect(r.makeOffset(lift * 0.3, lift), paint((40, 30, 20), a * 0.25, sigma=lift * 1.3))
    c.drawRRect(r, paint(WHITE, a))
    c.drawRRect(r, paint(INK, a * 0.5, stroke=1.2))


# ---------------------------------------------------------------- captions that live in the graphics
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


def _ink_char(c, ch, x, y, f, rgb, al, blur, rot=0.0, shadow=True):
    if al <= 1:
        return
    if rot:
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        x = y = 0
    if shadow:
        c.drawString(ch, x + 2, y + 4, f, paint((40, 30, 20), al * 0.22, sigma=5))
    if blur > 0.3:   # ink still soaking in: a soft spread under a forming glyph
        c.drawString(ch, x, y, f, paint(rgb, al * 0.5, sigma=blur * 1.6))
    c.drawString(ch, x, y, f, paint(rgb, al, sigma=blur * 0.4))
    if rot:
        c.restore()


def caption(c, words, t, t0s, y=CAP_Y, size=82, emph=None, shake=None, dur=0.5, a=1.0, plate=True):
    """Ink-in captions. Each word soaks into the paper at its spoken time (blurred spread -> crisp glyph) with a
    small downward spring. shake(t) in 0..1 (the seismogram envelope) jitters the letters, stronger on the active
    word. emph maps word index -> colour; those words switch to the serif italic and get an inked underline."""
    emph = emph or {}
    kinds, sizes, ws, xs, total = _word_layout(words, size, emph)
    if plate:   # a soft paper wash behind the line so it reads over any drawing
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(W / 2 - total / 2 - 36, y - size * 0.95, total + 72,
                                                              size * 1.45), 30, 30), paint(BONE, 200 * a, sigma=22))
    active = max([i for i, ts in enumerate(t0s) if t >= ts] or [-1])
    amp = shake(t) if shake else 0.0
    rng = np.random.default_rng(int(t * FPS) + 7)
    for i, wd in enumerate(words):
        u0 = t - t0s[i]
        if u0 < -0.05:
            continue
        k, s, rgb = kinds[i], sizes[i], emph.get(i, INK)
        f = font(k, s)
        cx = xs[i]
        if i in emph and u0 > 0:
            q = out_expo(u0 / 0.5)
            pth = skia.Path()
            pth.moveTo(xs[i], y + s * 0.2)
            for j in range(31):
                uu = j / 30 * q
                pth.lineTo(xs[i] + ws[i] * uu, y + s * 0.2 + math.sin(uu * 22 + i) * 2.5)
            ink(c, pth, rgb, 230 * a, 3.2)
        for j, ch in enumerate(wd):
            u = (u0 - j * 0.025) / dur
            if u <= 0:
                cx += f.measureText(ch)
                continue
            sp = spring(u, 8, 11)
            dy = -(1 - sp) * 22
            jit = amp * (1.6 if i == active else 0.7)
            dx, dyy = rng.normal(0, jit, 2) if jit > 0.05 else (0, 0)
            _ink_char(c, ch, cx + dx, y + dy + dyy, f, rgb, clamp(u * 3) * 255 * a, max(0.0, (1 - clamp(u * 2.4)) * 7),
                      rng.normal(0, jit * 0.5) if jit > 0.05 else 0.0)
            cx += f.measureText(ch)


def caption_split(c, words, y, size, emph, p0, p1, slip=18.0, rgb_line=RED, a=1.0):
    """The caption cut by the fault: everything above the line p0->p1 slides along it by `slip` px."""
    emph = emph or {}
    kinds, sizes, ws, xs, total = _word_layout(words, size, emph)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    far = 3000
    above = skia.Path()
    above.moveTo(p0[0] - ux * far, p0[1] - uy * far)
    above.lineTo(p1[0] + ux * far, p1[1] + uy * far)
    above.lineTo(p1[0] + ux * far + uy * far, p1[1] + uy * far - ux * far)
    above.lineTo(p0[0] - ux * far + uy * far, p0[1] - uy * far - ux * far)
    above.close()
    for side, (ox, oy) in (("below", (0, 0)), ("above", (ux * slip, uy * slip))):
        c.save()
        if side == "above":
            c.clipPath(above, doAntiAlias=True)
        else:
            c.clipPath(above, skia.ClipOp.kDifference, True)
        c.translate(ox, oy)
        for i, wd in enumerate(words):
            f = font(kinds[i], sizes[i])
            cx = xs[i]
            for ch in wd:
                _ink_char(c, ch, cx, y, f, emph.get(i, INK), 255 * a, 0)
                cx += f.measureText(ch)
        c.restore()
    pth = skia.Path()
    pth.moveTo(p0[0] - ux * 40, p0[1] - uy * 40)
    pth.lineTo(p1[0] + ux * 40, p1[1] + uy * 40)
    glow(c, pth, rgb_line, 255 * a, 2.6)


def caption_on_path(c, text, pts, start, size=64, kind="bold", rgb=INK, a=255, spacing=1.0):
    """Letters riding a polyline (e.g. the tsunami front), each rotated to the local tangent."""
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
        c.drawString(ch, -cw / 2 + 2, 4, f, paint((40, 30, 20), a * 0.2, sigma=4))
        c.drawString(ch, -cw / 2, 0, f, paint(rgb, a))
        c.restore()
        d += cw


# ---------------------------------------------------------------- post
_GRAIN = _VIG = None


def post(img, t, bloom=1.0, ca=0.6, grain=4.0, shake=0.0):
    """img float32 HxWx3 on paper. Paper grain is multiplied in (darkens like real fibre), a warm vignette, red-only
    bloom for the quake energy, a touch of lens fringing toward the edges, and optional camera shake."""
    global _GRAIN, _VIG
    if _GRAIN is None:
        rng = np.random.default_rng(5)
        _GRAIN = [(rng.normal(0, 1, (H // 2, W // 2)) * grain).astype(np.float32) for _ in range(8)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        v = 1 - 0.32 * np.clip(r - 0.45, 0, 1) ** 1.5
        _VIG = np.dstack([v, v ** 1.15, v ** 1.35]).astype(np.float32)   # edges fall off warm, like old paper
    if shake > 0:
        rng = np.random.default_rng(int(t * FPS))
        dx, dy = rng.normal(0, shake * 10, 2)
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if bloom > 0:
        small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        red = np.clip((small[..., 0] - small[..., 1] - 80) / 90, 0, 1)[..., None]
        b = cv2.GaussianBlur(small * red, (0, 0), 10)
        tint = np.array([0.0, -0.55, -0.6], np.float32) * 0.5   # red bloom on paper: pulls green and blue down
        img = img + cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR)[..., :1] * tint * bloom
    k = 0.0012 * ca
    if k > 0:
        Mr = np.float32([[1 + k, 0, -W / 2 * k], [0, 1 + k, -H / 2 * k]])
        Mb = np.float32([[1 - k, 0, W / 2 * k], [0, 1 - k, H / 2 * k]])
        img = img.copy()
        img[..., 0] = cv2.warpAffine(img[..., 0], Mr, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img[..., 2] = cv2.warpAffine(img[..., 2], Mb, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    img = img * _VIG
    g = cv2.resize(_GRAIN[int(t * FPS) % 8], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    img = img * (1 + g / 255 * 2.2)
    return np.clip(img, 0, 255).astype(np.uint8)


def render(draw, t, samples=3, shutter=0.5, **kw):
    s = skia.Surface(W, H)
    c = s.getCanvas()
    acc = None
    for i in range(samples):
        ts = t + ((i + 0.5) / samples - 0.5) * shutter / FPS if samples > 1 else t
        c.clear(col(BONE))
        draw(c, ts)
        f = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
        acc = f if acc is None else acc + f
    return post(acc / samples, t, **kw)
