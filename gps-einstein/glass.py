""""Frosted Glass" engine for the GPS Short.

Every object is a panel of frosted glass that the scene behind it shows through:
  * The frame is a float RGB array. A glass object takes the pixels behind it, blurs them (frost), bends them near
    its edge (refraction, slightly more for blue than red = dispersion), tints them, and gets a rim light on the side
    facing the key light (top left) and a soft shade on the far side.
  * Caustics: moving bands of light with rainbow fringes, on the floor and inside glass.
  * Three depth planes: blurred far glass, the sharp hero, out-of-focus shards in front.
  * Amber = you and the signal, violet = time and Einstein, cyan = light and the blue dot.
"""
import json, math, os

import cv2
import numpy as np
import skia

from kit import W, H, FPS, clamp, prog, smooth, out_cubic, spring, mix, col, paint, font, width, label  # noqa: F401
from project import P, palette

INK = palette("ink")
CARBON = palette("carbon")
CARD = palette("card")
PAPER = palette("paper")
SMOKE = palette("smoke")
AMBER = palette("amber")     # you, your phone, the signal
VIOLET = palette("violet")   # time, clocks, Einstein
CYAN = palette("cyan")       # light, beams, the blue dot
FX = P["style"]["post"]
LIGHT = (-0.62, -0.78)       # direction towards the key light (top left)
HERE = os.path.dirname(os.path.abspath(__file__))
np.seterr(divide="ignore", invalid="ignore", over="ignore")
cv2.setNumThreads(1)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)   # pixel grids, shared


# ---------------------------------------------------------------- layers
def new():
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    return s, c


def grab(s):
    a = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
    a = a.astype(np.float32)
    return a[..., :3], a[..., 3] / 255.0


def layer(fn):
    """fn(canvas) drawn on a transparent frame -> (premultiplied rgb, alpha)."""
    s, c = new()
    fn(c)
    return grab(s)


def mask(fn):
    """fn(canvas, white_paint) -> alpha 0..1 of the shape."""
    s, c = new()
    fn(c, paint((255, 255, 255)))
    return grab(s)[1]


def over(img, lay, k=1.0):
    rgb, a = lay
    return img * (1 - a[..., None] * k) + rgb * k


def add(img, lay, k=1.0):
    return img + lay[0] * k


def blur_layer(lay, sigma):
    rgb, a = lay
    return cv2.GaussianBlur(rgb, (0, 0), sigma), cv2.GaussianBlur(a, (0, 0), sigma)


# ---------------------------------------------------------------- light
_CAU = {}


def caustics(t, w, h, scale=3.0, speed=0.35, seed=0.0, squash=1.0):
    """Moving caustic bands (Dave Hoskins' water caustic), one channel, w x h. Returns float 0..~1.5."""
    key = (round(t, 3), w, h, scale, speed, seed, squash)
    if key in _CAU:
        return _CAU[key]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    px = (xx / w * scale + seed * 1.37) * 2 * math.pi - 250
    py = (yy / w * scale * squash + seed) * 2 * math.pi - 250
    ix, iy, c, inten = px.copy(), py.copy(), np.ones_like(px), 0.005
    for n in range(5):
        tt = t * speed * (1 - 3.5 / (n + 1)) + seed
        ix, iy = px + np.cos(tt - ix) + np.sin(tt + iy), py + np.sin(tt - iy) + np.cos(tt + ix)
        c += 1 / np.sqrt((px / (np.sin(ix + tt) / inten)) ** 2 + (py / (np.cos(iy + tt) / inten)) ** 2)
    c = 1.17 - (c / 5) ** 1.4
    out = np.clip(np.nan_to_num(np.abs(c) ** 8), 0, 1.5).astype(np.float32)
    if len(_CAU) > 24:
        _CAU.clear()
    _CAU[key] = out
    return out


def caustic_light(t, scale=3.0, speed=0.35, seed=0.0, tint=(225, 238, 255), squash=1.0, fringe=0.35):
    """Full-frame caustic light (computed at half size), already coloured. squash > 1 flattens the pattern, as on a
    floor seen at an angle; fringe = how much the red and blue copies are pulled apart (rainbow edges)."""
    q = caustics(t, W // 2, H // 2, scale, speed, seed, squash)
    q = cv2.resize(q, (W, H), interpolation=cv2.INTER_LINEAR)
    sh = int(round(3 * fringe / 0.35))
    out = np.empty((H, W, 3), np.float32)
    out[..., 1] = q
    out[..., 0] = np.roll(q, -sh, axis=0) * fringe + q * (1 - fringe)
    out[..., 2] = np.roll(q, sh, axis=0) * fringe + q * (1 - fringe)
    return out * (np.float32(tint) / 255)


def ellipse(cx, cy, rx, ry, soft=0.5):
    """Soft elliptical pool 0..1."""
    r = np.sqrt(((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2)
    return np.clip((1 - r) / soft, 0, 1) ** 1.5


# ---------------------------------------------------------------- backdrop
_BG = {}


def backdrop(t, glow=(0.5, 0.42), floor=0.70, caustic=1.0, pool=None, seed=0.0, floor_k=1.0):
    """Deep navy studio: key-light glow, a horizon where the floor begins, caustics on the floor.
    pool = (cx, cy, rx, ry): a pool of caustic light cast through the hero glass onto the floor."""
    key = (glow, floor)
    if key not in _BG:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W * glow[0]) / W) ** 2 + ((yy - H * glow[1]) / H * 0.75) ** 2)
        g = np.clip(1 - r / 0.75, 0, 1) ** 1.6
        img = np.float32(INK) + (np.float32(CARBON) * 1.9 - np.float32(INK)) * g[..., None] * 0.85
        # the floor: slightly lifted, with a soft bright horizon line that fades to the sides
        f = np.clip((yy - H * floor) / (H * 0.3), 0, 1)
        img = img * (1 - 0.18 * f[..., None]) + np.float32(CARBON) * (0.35 * f)[..., None]
        hz = np.exp(-((yy - H * floor) / 3.0) ** 2) * np.clip(1 - np.abs(xx - W / 2) / (W * 0.62), 0, 1) ** 2
        img += np.float32(mix(CARBON, PAPER, 0.35)) * (hz * 0.35)[..., None]
        _BG[key] = img.astype(np.float32)
    img = _BG[key].copy()
    caustic *= FX.get("caustics", 1.0)
    if caustic > 0:
        cl = caustic_light(t, 2.2, 0.3, seed, squash=3.2)
        yy = np.arange(H, dtype=np.float32)[:, None]
        fl = np.clip((yy - H * floor) / 90, 0, 1) * np.clip(1 - (yy - H * floor) / (H * 0.42), 0, 1)
        img += cl * (fl * 22 * caustic * floor_k)[..., None]
        if pool:
            img += cl * (ellipse(*pool) * 120 * caustic)[..., None]
            img += np.float32(CYAN) * (ellipse(pool[0], pool[1], pool[2] * 1.3, pool[3] * 1.4, 1.0) * 0.10)[..., None]
    return img


# ---------------------------------------------------------------- glass
def glass(img, m, bevel=24.0, refract=16.0, frost=9.0, tint=0.30, rgb=None, rim=1.0, disp=0.35, lift=8.0,
          shade=0.35, sheen=None, inner=None):
    """Composite a frosted-glass object with alpha m over img (in place, returns img).
    bevel: width of the rounded edge in px; refract: how far the edge bends the scene; frost: blur behind;
    sheen = (pos, width, k): a diagonal glint band (pos 0..1 across the object, k = 0..1 of paper white);
    inner: extra float RGB added inside."""
    ys, xs = np.nonzero(m > 0.004)
    if not len(xs):
        return img
    pad = int(refract * 2 + frost * 3 + 6)
    x0, x1 = max(0, xs.min() - pad), min(W, xs.max() + pad + 1)
    y0, y1 = max(0, ys.min() - pad), min(H, ys.max() + pad + 1)
    sub = img[y0:y1, x0:x1]
    mm = m[y0:y1, x0:x1]
    refract *= FX.get("refraction", 1.0)
    blur = cv2.GaussianBlur(sub, (0, 0), frost) if frost > 0 else sub
    d = cv2.distanceTransform((mm > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    u = np.clip(d / bevel, 0, 1)
    hgt = cv2.GaussianBlur(1 - (1 - u) ** 2, (0, 0), 1.0)
    gy, gx = np.gradient(hgt)
    nx, ny = -gx * bevel * 0.5, -gy * bevel * 0.5
    edge = 1 - u
    hh, ww = mm.shape
    X, Y = np.meshgrid(np.arange(ww, dtype=np.float32), np.arange(hh, dtype=np.float32))
    out = np.empty_like(sub)
    for ch, k in enumerate((1 - disp, 1.0, 1 + disp)):
        out[..., ch] = cv2.remap(blur[..., ch], X - nx * refract * k, Y - ny * refract * k, cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_REFLECT)
    out = out * (1 - tint) + np.float32(rgb or CARD) * tint + lift
    ndl = nx * LIGHT[0] + ny * LIGHT[1]
    out += np.float32(PAPER) * (np.clip(ndl, 0, 1) * edge ** 1.5 * 0.32 * rim)[..., None]
    out *= (1 - np.clip(-ndl, 0, 1) * edge * shade)[..., None]
    rl = np.exp(-((d - 1.0) / 1.2) ** 2)
    out += np.float32(PAPER) * (rl * (0.15 + 0.85 * np.clip(ndl * 0.6 + 0.4, 0, 1)) * 0.6 * rim)[..., None]
    if sheen:
        pos, wd, k = sheen
        ax = (X + Y * 0.55)
        a0, a1 = ax[mm > 0.5].min(), ax[mm > 0.5].max()
        band = np.exp(-((ax - (a0 + (a1 - a0) * pos)) / wd) ** 2) * u
        out += np.float32(PAPER) * (band * k)[..., None]
    if inner is not None:
        out += inner[y0:y1, x0:x1]
    img[y0:y1, x0:x1] = sub * (1 - mm[..., None]) + out * mm[..., None]
    return img


def shadow(img, m, dx=26, dy=46, blur=34, k=0.5):
    """Soft shadow of a glass object, cast away from the key light."""
    q = cv2.resize(m, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    M = np.float32([[1, 0, dx / 4], [0, 1, dy / 4]])
    q = cv2.GaussianBlur(cv2.warpAffine(q, M, (W // 4, H // 4)), (0, 0), blur / 4)
    img *= (1 - cv2.resize(q, (W, H)) * k)[..., None]
    return img


def defocus(img, fn, sigma=14, k=1.0):
    """An out-of-focus foreground element: fn(canvas) drawn, blurred and added as light."""
    lay = blur_layer(layer(fn), sigma)
    return img * (1 - lay[1][..., None] * 0.35 * k) + lay[0] * k


def shard(c, x, y, s, rot, a=255):
    """A glass shard (for foreground bokeh): a thin bright rim and a faint body."""
    path = skia.Path()
    pts = [(0, -1), (0.62, 0.35), (-0.18, 0.9), (-0.7, -0.1)]
    cr, sr = math.cos(rot), math.sin(rot)
    for i, (px, py) in enumerate(pts):
        X, Y = x + (px * cr - py * sr) * s, y + (px * sr + py * cr) * s
        path.moveTo(X, Y) if i == 0 else path.lineTo(X, Y)
    path.close()
    c.drawPath(path, paint(mix(CARD, PAPER, 0.3), a * 0.35))
    c.drawPath(path, paint(PAPER, a, stroke=3))


def glass_text(img, s, x, y, size, kind="black", tracking=0.0, align="center", tint=0.26, lift=34, rgb=None,
               caustic_t=None, glow=None, rim=1.2, a=1.0, scale=1.0):
    """Text made of glass: the scene bends through each letter, with a rim light and caustics moving inside.
    a fades it (0..1); scale grows it about its centre."""
    if a <= 0.01:
        return img
    def shape(c, p):
        if scale != 1.0:
            c.translate(x, y - size * 0.35)
            c.scale(scale, scale)
            c.translate(-x, -(y - size * 0.35))
        label(c, s, x, y, size, kind, (255, 255, 255), 255, align, tracking)
    m = mask(shape) * a
    if glow:
        g = cv2.GaussianBlur(m, (0, 0), size * 0.22)
        img += np.float32(glow) * (g * 0.55)[..., None]
    inner = None
    if caustic_t is not None:
        inner = caustic_light(caustic_t, 3.4, 0.4, 2.0) * 120
    return glass(img, m, bevel=max(4.0, size * 0.075), refract=size * 0.08, frost=5, tint=tint, rgb=rgb or PAPER,
                 lift=lift, rim=rim, inner=inner, shade=0.25)


def text_width(s, kind, size, tracking=0.0):
    return width(s, kind, size, tracking)


def rrect(x, y, w, h, r):
    return skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)


def glow_dot(c, x, y, r, rgb, a=255, halo=3.0):
    c.drawCircle(x, y, r * halo, paint(rgb, a * 0.22, sigma=r * halo * 0.6))
    c.drawCircle(x, y, r * 1.6, paint(rgb, a * 0.35, sigma=r * 0.8))
    c.drawCircle(x, y, r, paint(mix(rgb, PAPER, 0.35), a))


# ---------------------------------------------------------------- earth
_LAND = None


def land():
    global _LAND
    if _LAND is None:
        _LAND = json.load(open(os.path.join(HERE, "data", "world.json")))
    return _LAND


class Ortho:
    """Orthographic globe view centred on (lon0, lat0) with radius R at (cx, cy)."""

    def __init__(self, lon0, lat0, R, cx, cy):
        self.l0, self.p0, self.R, self.cx, self.cy = math.radians(lon0), math.radians(lat0), R, cx, cy

    def __call__(self, lon, lat):
        l, p = math.radians(lon) - self.l0, math.radians(lat)
        x = math.cos(p) * math.sin(l)
        y = math.cos(self.p0) * math.sin(p) - math.sin(self.p0) * math.cos(p) * math.cos(l)
        z = math.sin(self.p0) * math.sin(p) + math.cos(self.p0) * math.cos(p) * math.cos(l)
        return self.cx + x * self.R, self.cy - y * self.R, z


def land_path(proj):
    path = skia.Path()
    for ring in land():
        pts = [proj(lon, lat) for lon, lat in ring]
        if max(p[2] for p in pts) < 0:
            continue
        first = True
        for x, y, z in pts:
            if z < -0.02:
                continue
            path.moveTo(x, y) if first else path.lineTo(x, y)
            first = False
        path.close()
    return path


def earth(img, cx, cy, r, t, lon0=-20.0, lat0=22.0, spin=4.0):
    """A glass Earth: a dark-blue glass sphere with raised frosted continents, a graticule, a cyan atmosphere rim,
    a key-light highlight and a night side."""
    proj = Ortho(lon0 + spin * t, lat0, r, cx, cy)
    disc = mask(lambda c, p: c.drawCircle(cx, cy, r, p))
    shadow(img, disc, 40, 70, 60, 0.55)
    atm = cv2.GaussianBlur(mask(lambda c, p: c.drawCircle(cx, cy, r * 1.03, p)), (0, 0), r * 0.06)
    img += np.float32(CYAN) * (np.clip(atm - disc, 0, 1) * 0.9)[..., None]
    glass(img, disc, bevel=r * 0.55, refract=r * 0.12, frost=16, tint=0.62, rgb=(16, 44, 92), lift=6, rim=0.9,
          shade=0.55)
    clip = skia.Path()
    clip.addCircle(cx, cy, r - 1)
    lp = land_path(proj)
    lm = mask(lambda c, p: (c.clipPath(clip, doAntiAlias=True), c.drawPath(lp, p)))
    glass(img, lm, bevel=5, refract=4, frost=3, tint=0.38, rgb=mix(PAPER, CYAN, 0.25), lift=14, rim=0.8, shade=0.2)

    def grid(c):
        c.clipPath(clip, doAntiAlias=True)
        for lat in range(-60, 61, 30):
            pts = [proj(lon, lat) for lon in range(-180, 181, 4)]
            _poly(c, pts, paint(PAPER, 34, stroke=1.4))
        for lon in range(-180, 180, 30):
            pts = [proj(lon, lat) for lat in range(-88, 89, 4)]
            _poly(c, pts, paint(PAPER, 34, stroke=1.4))
    img = over(img, layer(grid))
    # night side (lower right) and the key-light highlight (upper left)
    dx, dy = (XX - cx) / r, (YY - cy) / r
    inside = disc
    night = np.clip((dx * 0.62 + dy * 0.78) * 0.9 + 0.05, 0, 1) ** 1.3
    img *= (1 - night * inside * 0.62)[..., None]
    hl = np.exp(-(((dx + 0.42) ** 2 + (dy + 0.48) ** 2) / 0.06)) * inside
    img += np.float32(PAPER) * (hl * 0.16)[..., None]
    return img, proj


def _poly(c, pts, p):
    path, pen = skia.Path(), False
    for x, y, z in pts:
        if z < 0:
            pen = False
            continue
        path.lineTo(x, y) if pen else path.moveTo(x, y)
        pen = True
    c.drawPath(path, p)


def orbit_points(cx, cy, R, incl, rot, n=180, phase=0.0):
    """A circular orbit seen in perspective: incl tilts it away from the viewer (deg), rot turns it on screen (deg).
    Returns [(x, y, z)], z > 0 = in front of the Earth."""
    i, ro = math.radians(incl), math.radians(rot)
    out = []
    for k in range(n + 1):
        th = 2 * math.pi * k / n + phase
        x, y, z = math.cos(th), math.sin(th) * math.cos(i), math.sin(th) * math.sin(i)
        X, Y = x * math.cos(ro) - y * math.sin(ro), x * math.sin(ro) + y * math.cos(ro)
        out.append((cx + X * R, cy + Y * R, z))
    return out


def orbit_line(c, pts, front, rgb=CYAN, a=255, wd=2.0):
    """Draw the front (z >= 0) or back half of an orbit with a soft glow."""
    path, pen = skia.Path(), False
    for x, y, z in pts:
        if (z >= 0) != front:
            pen = False
            continue
        path.lineTo(x, y) if pen else path.moveTo(x, y)
        pen = True
    k = 1.0 if front else 0.35
    c.drawPath(path, paint(rgb, a * 0.35 * k, sigma=6, stroke=wd * 4))
    c.drawPath(path, paint(mix(rgb, PAPER, 0.3), a * 0.9 * k, stroke=wd))


def mini_sat(c, x, y, s, ang=0.0, a=255, lit=1.0):
    """A small satellite drawn as light glass: body, two solar wings, a cyan beacon."""
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(ang))
    for sx in (-1, 1):
        wing = rrect(sx * s * 0.62 - (s * 1.5 if sx < 0 else 0), -s * 0.32, s * 1.5, s * 0.64, s * 0.08)
        c.drawRRect(wing, paint(mix(CARD, CYAN, 0.25), a * 0.55))
        c.drawRRect(wing, paint(PAPER, a * 0.75, stroke=max(1.0, s * 0.06)))
        for k in (1, 2):
            gx = sx * s * 0.62 + (k * s * 0.5 if sx > 0 else -k * s * 0.5)
            c.drawLine(gx, -s * 0.3, gx, s * 0.3, paint(PAPER, a * 0.35, stroke=1))
    c.drawLine(-s * 0.62, 0, s * 0.62, 0, paint(PAPER, a * 0.7, stroke=max(1.0, s * 0.08)))
    body = rrect(-s * 0.45, -s * 0.45, s * 0.9, s * 0.9, s * 0.18)
    c.drawRRect(body, paint(mix(CARD, PAPER, 0.25), a * 0.85))
    c.drawRRect(body, paint(PAPER, a, stroke=max(1.0, s * 0.07)))
    c.restore()
    glow_dot(c, x, y, max(1.6, s * 0.14), CYAN, a * lit, 3.5)


def sat_mask(x, y, s, ang=0.0):
    """Mask of a hero satellite (body + wings) for full glass rendering."""
    def draw(c, p):
        c.save()
        c.translate(x, y)
        c.rotate(math.degrees(ang))
        for sx in (-1, 1):
            c.drawRRect(rrect(sx * s * 0.66 - (s * 1.6 if sx < 0 else 0), -s * 0.36, s * 1.6, s * 0.72, s * 0.07), p)
        c.drawRRect(rrect(-s * 0.5, -s * 0.5, s, s, s * 0.2), p)
        c.restore()
    return mask(draw)


# ---------------------------------------------------------------- clock
def clock(img, cx, cy, r, secs, accent, name, readout=None, t=0.0, sheen=0.3):
    """A glass clock: frosted disc, engraved ticks, paper hands, an accent second hand with a glow,
    a mono name under it and an optional readout."""
    disc = mask(lambda c, p: c.drawCircle(cx, cy, r, p))
    shadow(img, disc, 30, 55, 40, 0.5)
    inner = np.zeros((H, W, 3), np.float32)
    glass(img, disc, bevel=r * 0.16, refract=r * 0.09, frost=14, tint=0.36, lift=10, rim=1.3,
          sheen=(sheen, 70, 0.10))
    face = mask(lambda c, p: c.drawCircle(cx, cy, r * 0.8, p))
    img *= (1 - face * 0.12)[..., None]
    del inner

    def draw(c):
        for k in range(60):
            a = 2 * math.pi * k / 60
            big = k % 5 == 0
            r0 = r * (0.70 if big else 0.75)
            c.drawLine(cx + math.sin(a) * r0, cy - math.cos(a) * r0, cx + math.sin(a) * r * 0.79,
                       cy - math.cos(a) * r * 0.79, paint(PAPER, 230 if big else 110, stroke=4 if big else 1.6))

        def hand(ang, ln, wd, rgb, a=255, tail=0.12, glow=False):
            x1, y1 = cx + math.sin(ang) * r * ln, cy - math.cos(ang) * r * ln
            x0, y0 = cx - math.sin(ang) * r * tail, cy + math.cos(ang) * r * tail
            if glow:
                c.drawLine(x0, y0, x1, y1, paint(rgb, 140, sigma=8, stroke=wd * 4))
            c.drawLine(x0, y0, x1, y1, paint(rgb, a, stroke=wd))
        hand(2 * math.pi * (secs / 43200), 0.42, 9, PAPER)
        hand(2 * math.pi * (secs / 3600), 0.62, 6, PAPER)
        hand(2 * math.pi * (secs / 60), 0.72, 3, accent, glow=True, tail=0.2)
        c.drawCircle(cx, cy, 10, paint(accent))
        c.drawCircle(cx, cy, 4, paint(INK))
        label(c, name, cx, cy + r + 62, 30, "mono", accent, 255, "center", 0.32)
        if readout:
            label(c, readout, cx, cy + r + 110, 26, "mono", SMOKE, 255, "center", 0.12)
    return over(img, layer(draw))


# ---------------------------------------------------------------- captions
def caption(img, words, y=None, size=None, hl=None, a=1.0):
    """Kinetic caption on a small frosted-glass pill. words: list of str; hl: {word_index: rgb}."""
    cfg = P["style"]["captions"]
    y = y or cfg["y"]
    size = size or cfg["size"]
    hl = hl or {}
    gap = size * 0.28
    ws = [width(w, "semibold", size) for w in words]
    tw = sum(ws) + gap * (len(words) - 1)
    padx, pady = size * 0.48, size * 0.34
    x0 = W / 2 - tw / 2
    m = mask(lambda c, p: c.drawRRect(rrect(x0 - padx, y - size * 0.86 - pady, tw + 2 * padx, size * 1.12 + 2 * pady,
                                            (size * 1.12 + 2 * pady) / 2), p)) * a
    glass(img, m, bevel=14, refract=10, frost=18, tint=0.5, lift=4, rim=1.0, shade=0.2)

    def draw(c):
        x = x0
        for i, (w, wd) in enumerate(zip(words, ws)):
            rgb = hl.get(i, PAPER)
            if i in hl:
                label(c, w, x, y, size, "semibold", rgb, 160 * a, sigma=12)
            label(c, w, x, y, size, "semibold", rgb, 255 * a)
            x += wd + gap
    return over(img, layer(draw))


# ---------------------------------------------------------------- post
_GRAIN = _VIG = None


def post(img, t, bloom=1.0, ca=1.0, grain=4.0):
    """Bloom on bright light, a soft highlight roll-off, chromatic fringe at the frame edges, vignette, grain."""
    global _GRAIN, _VIG
    bloom, ca, grain = bloom * FX["bloom"], ca * FX["ca"], grain * FX["grain"]
    if _GRAIN is None:
        rng = np.random.default_rng(5)
        _GRAIN = [(rng.normal(0, 1, (H // 2, W // 2))).astype(np.float32) for _ in range(8)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _VIG = (1 - 0.5 * np.clip(r - 0.45, 0, 1) ** 1.4)[..., None].astype(np.float32)
    if bloom > 0:
        small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        m = np.clip((small.max(axis=2, keepdims=True) - 150) / 90, 0, 1)
        b = cv2.GaussianBlur(small * m, (0, 0), 4) * 0.45 + cv2.GaussianBlur(small * m, (0, 0), 16) * 0.65
        img = img + cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR) * bloom
    k = 0.0012 * ca
    if k > 0:
        Mr = np.float32([[1 + k, 0, -W / 2 * k], [0, 1 + k, -H / 2 * k]])
        Mb = np.float32([[1 - k, 0, W / 2 * k], [0, 1 - k, H / 2 * k]])
        img = img.copy()
        img[..., 0] = cv2.warpAffine(img[..., 0], Mr, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img[..., 2] = cv2.warpAffine(img[..., 2], Mb, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    knee = 205.0
    img = np.where(img > knee, knee + (img - knee) / (1 + (img - knee) / 70), img)
    g = cv2.resize(_GRAIN[int(t * FPS) % 8], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    img = img * _VIG + g * grain
    return np.clip(img, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- camera and frames
def cam(img, s=1.0, cx=W / 2, cy=H / 2, dx=0.0, dy=0.0, rot=0.0):
    """Camera move on the finished picture: scale s about (cx, cy), then shift; small moves only (raster)."""
    if s == 1.0 and dx == 0 and dy == 0 and rot == 0:
        return img
    M = cv2.getRotationMatrix2D((cx, cy), rot, s)
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def fade(img, k, rgb=(0, 0, 0)):
    """Dip towards a colour (black by default), k 0..1."""
    if k <= 0:
        return img
    return img * (1 - k) + np.float32(rgb) * k


def render(draw, t, samples=1, shutter=0.5, **kw):
    """draw(t) -> float RGB frame. Motion blur = average of `samples` sub-frames across half a frame; then post."""
    if samples <= 1:
        return post(draw(t), t, **kw)
    acc = None
    for i in range(samples):
        ts = t + ((i + 0.5) / samples - 0.5) * shutter / FPS
        f = draw(ts)
        acc = f if acc is None else acc + f
    return post(acc / samples, t, **kw)
