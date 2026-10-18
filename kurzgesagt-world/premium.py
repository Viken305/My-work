"""Premium rendering layer on top of engine.py.

  * Procedural nebulae: multi-octave value noise + domain warp -> colour-ramped RGBA textures (cached)
  * Parallax starfield (3 depth layers) with twinkle and diffraction spikes
  * Additive light (kPlus blending) for glows, flares and plasma
  * Foreground bokeh (depth-of-field dust)
  * Lens flare: anamorphic streak + ghosts
  * Post: bloom (multi-scale), chromatic aberration, split-tone grade, vignette, film grain
  * Motion blur: temporal supersampling of sub-frames (average of N renders across a shutter)
"""
import math, os

import cv2
import numpy as np
import skia

from engine import *  # noqa: F401,F403

cv2.setNumThreads(1)
CACHE = os.path.join(HERE, "build", "cache")

# ---------------------------------------------------------------- space palette
VOID = (6, 7, 22)
DEEP = (14, 12, 44)
INDIGO2 = (32, 22, 86)
MAGENTA = (232, 62, 140)
VIOLET2 = (130, 70, 220)
TEAL = (40, 200, 210)
AMBER = (255, 170, 60)
SOLAR = (255, 214, 120)
HOTWHITE = (255, 248, 230)
RED_GIANT = (255, 96, 60)
BLUE_STAR = (150, 190, 255)


# ---------------------------------------------------------------- noise textures
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


def warped_fbm(h, w, seed=0, base=200, warp=60.0):
    qx, qy = fbm(h, w, seed + 1, base), fbm(h, w, seed + 2, base)
    mx, my = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    n = fbm(h, w, seed, base * 0.8)
    return cv2.remap(n, mx + (qx - 0.5) * warp * 2, my + (qy - 0.5) * warp * 2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


TEX_CACHE = {}


def nebula_texture(name, seed, colors, size=(1400, 900), density=1.0, warp=90.0, lo=0.35, hi=0.95):
    """RGBA skia.Image of a nebula: colours = list of (stop, rgb) ramp; alpha from a second noise field."""
    key = (name, seed)
    if key in TEX_CACHE:
        return TEX_CACHE[key]
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"neb_{name}_{seed}.png")
    if os.path.exists(path):
        img = skia.Image.open(path)
    else:
        w, h = size
        n = warped_fbm(h, w, seed, 220, warp)
        d = fbm(h, w, seed + 7, 140, 6, 0.6)
        stops = np.array([s for s, _ in colors], np.float32)
        cols = np.array([c for _, c in colors], np.float32)
        rgb = np.stack([np.interp(n, stops, cols[:, k]) for k in range(3)], -1)
        a = np.clip((n * 0.65 + d * 0.35 - lo) / (hi - lo), 0, 1) ** 1.6 * density
        # soft radial falloff so textures never show hard edges
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        fall = np.clip(1.0 - r, 0, 1)
        a *= fall * fall * (3 - 2 * fall)   # smoothstep to exactly zero at the edges
        rgba = np.dstack([rgb, np.clip(a, 0, 1) * 255]).astype(np.uint8)
        cv2.imwrite(path, cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))
        img = skia.Image.open(path)
    TEX_CACHE[key] = img
    return img


def draw_texture(c, img, cx, cy, scale=1.0, rot=0.0, a=255, blend=skia.BlendMode.kScreen):
    if a <= 1:
        return
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(a / 255)
    p.setBlendMode(blend)
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(scale, scale)
    c.drawImage(img, -img.width() / 2, -img.height() / 2, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.restore()


def circle_path(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


# ---------------------------------------------------------------- additive light
def add(rgb, a=255):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a))
    p.setBlendMode(skia.BlendMode.kPlus)
    return p


def light(c, x, y, r, rgb, a=200, core=0.0):
    """Physically-flavoured glow: wide soft falloff + optional hot core (additive)."""
    if r <= 0.5 or a <= 1:
        return
    p = skia.Paint(AntiAlias=True, Shader=radial((x, y), r, [(rgb, a), (rgb, a * 0.5), (rgb, a * 0.16), (rgb, 0)], [0, 0.25, 0.55, 1]))
    p.setBlendMode(skia.BlendMode.kPlus)
    c.drawCircle(x, y, r, p)
    if core > 0:
        c.drawCircle(x, y, r * 0.08 * core, add(HOTWHITE, 255))


def flare(c, x, y, s, rgb=(120, 170, 255), a=200, center=(W / 2, H / 2)):
    """Anamorphic streak + ghost discs along the line through the frame centre."""
    if a <= 2 or s <= 0:
        return
    st = skia.Paint(AntiAlias=True, Shader=radial((0, 0), 1, [(rgb, a), (rgb, a * 0.3), (rgb, 0)], [0, 0.3, 1]))
    st.setBlendMode(skia.BlendMode.kPlus)
    c.save()
    c.translate(x, y)
    c.scale(s * 9, s * 0.18)
    c.drawCircle(0, 0, 1, st)
    c.restore()
    vx, vy = center[0] - x, center[1] - y
    for k, (f, r, gc) in enumerate(((0.6, 0.25, rgb), (1.2, 0.45, (255, 170, 120)), (1.6, 0.18, (170, 255, 200)), (2.1, 0.6, rgb))):
        gx, gy = x + vx * f, y + vy * f
        g = skia.Paint(AntiAlias=True, Shader=radial((gx, gy), s * r, [(gc, 0), (gc, a * 0.12), (gc, a * 0.05), (gc, 0)], [0, 0.7, 0.9, 1]))
        g.setBlendMode(skia.BlendMode.kPlus)
        c.drawCircle(gx, gy, s * r, g)


def spikes(c, x, y, s, rgb=HOTWHITE, a=255, n=4, rot=45.0):
    """Diffraction spikes for bright stars."""
    if s <= 0.5 or a <= 2:
        return
    for k in range(n):
        ang = math.radians(rot + k * 360 / n)
        dx, dy = math.cos(ang), math.sin(ang)
        p = skia.Paint(AntiAlias=True, Shader=linear((x, y), (x + dx * s, y + dy * s), [(rgb, a), (rgb, 0)]),
                       Style=skia.Paint.kStroke_Style, StrokeWidth=max(1.0, s * 0.03))
        p.setBlendMode(skia.BlendMode.kPlus)
        c.drawLine(x, y, x + dx * s, y + dy * s, p)
    light(c, x, y, s * 0.35, rgb, a * 0.8)


# ---------------------------------------------------------------- camera + parallax
class Cam:
    """2D camera. world point (wx, wy) at depth factor d maps to screen with zoom^d and offset*d."""

    def __init__(self, x=0.0, y=0.0, z=1.0, rot=0.0):
        self.x, self.y, self.z, self.rot = x, y, z, rot

    def push(self, c, depth=1.0):
        c.save()
        c.translate(W / 2, H / 2)
        c.rotate(self.rot * depth)
        zz = self.z ** depth
        c.scale(zz, zz)
        c.translate(-self.x * depth, -self.y * depth)

    def pop(self, c):
        c.restore()


class Starfield:
    def __init__(self, seed=1, counts=(700, 260, 70)):
        rng = np.random.default_rng(seed)
        self.layers = []
        for li, n in enumerate(counts):
            pts = (rng.random((n, 2)) - 0.5) * [W * 3.2, H * 3.2]
            sizes = rng.random(n) ** 4 * (1.2 + li * 1.4) + 0.5 + li * 0.35
            tints = [mix(WHITE, BLUE_STAR if rng.random() < 0.5 else SOLAR, rng.random() * 0.6) for _ in range(n)]
            self.layers.append((pts, sizes, rng.random(n) * 6.28, rng.uniform(0.5, 2.0, n), tints, (0.25, 0.5, 0.85)[li]))

    def draw(self, c, t, cam, a=1.0):
        for pts, sizes, ph, sp, tints, depth in self.layers:
            cam.push(c, depth)
            for i in range(len(sizes)):
                tw = 0.65 + 0.35 * math.sin(t * sp[i] + ph[i])
                r = sizes[i]
                x, y = pts[i]
                if r > 2.2:
                    spikes(c, x, y, r * 7, tints[i], 160 * tw * a)
                c.drawCircle(x, y, r * 0.6, add(tints[i], 220 * tw * a))
            cam.pop(c)


class Bokeh:
    """Out-of-focus foreground dust drifting past the lens."""

    def __init__(self, seed=5, n=14, rgb=(170, 190, 255)):
        rng = np.random.default_rng(seed)
        self.p = rng.random((n, 2)) * [W * 1.4, H * 1.4] - [W * 0.2, H * 0.2]
        self.r = rng.uniform(20, 70, n)
        self.v = rng.uniform(-20, 20, (n, 2))
        self.rgb = rgb

    def draw(self, c, t, cam, a=1.0):
        cam.push(c, 1.6)
        for i in range(len(self.r)):
            x = (self.p[i, 0] + self.v[i, 0] * t) % (W * 1.6) - W * 0.3 + cam.x * 0.6
            y = (self.p[i, 1] + self.v[i, 1] * t) % (H * 1.6) - H * 0.3 + cam.y * 0.6
            p = skia.Paint(AntiAlias=True, Color=col(self.rgb, 26 * a))
            p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, self.r[i] * 0.35))
            p.setBlendMode(skia.BlendMode.kPlus)
            c.drawCircle(x, y, self.r[i], p)
        cam.pop(c)


# ---------------------------------------------------------------- post-processing
_LUT = None
_GRAIN = None
_VIG = None


def _grade_lut():
    x = np.linspace(0, 1, 256)
    s = x + 0.10 * np.sin(2 * np.pi * x) * (1 - x) * 0.9      # gentle S-curve
    lift = 0.035
    r = np.clip(lift * 0.6 + s * (1 - lift * 0.6) + 0.03 * x ** 2, 0, 1)
    g = np.clip(lift * 0.9 + s * (1 - lift * 0.9), 0, 1)
    b = np.clip(lift * 1.6 + s * (1 - lift * 1.6) - 0.02 * x ** 2, 0, 1)   # teal shadows, warm highlights
    return [(v * 255).astype(np.uint8) for v in (r, g, b)]


def post(rgb, t, bloom=0.75, ca=1.0, grain=4.0):
    """rgb: float32 HxWx3 in 0..255 (linear-ish). Returns uint8."""
    global _LUT, _GRAIN, _VIG
    if _LUT is None:
        _LUT = _grade_lut()
        rng = np.random.default_rng(3)
        _GRAIN = [(rng.normal(0, 1, (H // 2, W // 2)) * grain).astype(np.float32) for _ in range(8)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _VIG = (1 - 0.42 * np.clip(r - 0.35, 0, 1) ** 1.6)[..., None].astype(np.float32)
    img = rgb
    if bloom > 0:
        small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        lum = small.max(axis=2, keepdims=True)
        bright = small * np.clip((lum - 215) / 40, 0, 1) ** 1.5
        b1 = cv2.GaussianBlur(bright, (0, 0), 4)
        b2 = cv2.GaussianBlur(bright, (0, 0), 14)
        bl = cv2.resize(b1 * 0.7 + b2 * 0.9, (W, H), interpolation=cv2.INTER_LINEAR)
        img = img + bl * bloom
    if ca > 0:  # radial chromatic aberration: scale red out, blue in
        k = 0.0016 * ca
        Mr = np.float32([[1 + k, 0, -W / 2 * k], [0, 1 + k, -H / 2 * k]])
        Mb = np.float32([[1 - k, 0, W / 2 * k], [0, 1 - k, H / 2 * k]])
        img = img.copy()
        img[..., 0] = cv2.warpAffine(img[..., 0], Mr, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img[..., 2] = cv2.warpAffine(img[..., 2], Mb, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    img = img * _VIG
    g = _GRAIN[int(t * FPS) % len(_GRAIN)]
    img = img + cv2.resize(g, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    out = np.clip(img, 0, 255).astype(np.uint8)
    for ch in range(3):
        out[..., ch] = cv2.LUT(out[..., ch], _LUT[ch])
    return out


def snapshot(surface):
    return surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)


def render_premium(draw_frame, t, samples=3, shutter=0.5, scale=1.0, **post_kw):
    """Motion-blurred, post-processed frame. draw_frame(c, t) draws the scene."""
    s = skia.Surface(W, H)
    c = s.getCanvas()
    acc = None
    n = max(1, samples)
    for i in range(n):
        ts = t + ((i + 0.5) / n - 0.5) * shutter / FPS if n > 1 else t
        c.clear(col(VOID))
        draw_frame(c, ts)
        f = snapshot(s)
        acc = f if acc is None else acc + f
    return post(acc / n, t, **post_kw)
