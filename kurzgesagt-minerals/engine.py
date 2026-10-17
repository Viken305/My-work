"""Shared drawing kit for the Kurzgesagt-style minerals video (Skia, 1920x1080).

Flat vector shapes + soft gradients, glows, long soft shadows, drifting dust,
vignette and film grain. Characters: dot-eyed atoms and the hard-hat bird.
"""
import math, os

import numpy as np
import skia

W, H, FPS = 1920, 1080, 30
HERE = os.path.dirname(os.path.abspath(__file__))
# Static Montserrat instances (Skia ignores variable-font axes when drawing glyphs)
FONT_FILES = {w: os.path.join(HERE, "fonts", f"Montserrat-{w}.ttf") for w in (600, 800)}

# ---------------------------------------------------------------- palette
NAVY = (20, 22, 58)
PURPLE = (42, 30, 92)
VIOLET = (91, 75, 138)
ORANGE = (255, 122, 61)
YELLOW = (255, 201, 74)
CYAN = (62, 198, 224)
ICE = (201, 244, 255)
MINT = (94, 230, 168)
PINK = (255, 79, 139)
WHITE = (255, 255, 255)
INK = (24, 18, 48)
NA_COL = (255, 138, 72)    # sodium atom
CL_COL = (120, 222, 120)   # chlorine atom


def col(rgb, a=255):
    a = int(max(0, min(255, a)))
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), a)


def mix(c1, c2, t):
    t = clamp(t)
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))


def lighten(c, t):
    return mix(c, WHITE, t)


def darken(c, t):
    return mix(c, (0, 0, 0), t)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    """0..1 progress of t through [t0, t1]."""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def in_cubic(x):
    x = clamp(x)
    return x ** 3


def out_back(x, s=1.7):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def out_expo(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def bob(t, amp=4.0, period=3.0, phase=0.0):
    """Idle float so nothing is ever fully still."""
    return amp * math.sin(2 * math.pi * (t / period + phase))


def pop(t, t0, dur=0.45):
    """Ease-out-back pop-in scale (0 before t0)."""
    return out_back(prog(t, t0, t0 + dur))


# ---------------------------------------------------------------- paints
def fill(rgb, a=255):
    return skia.Paint(AntiAlias=True, Color=col(rgb, a))


def stroke(rgb, w, a=255, cap=skia.Paint.kRound_Cap):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a), Style=skia.Paint.kStroke_Style, StrokeWidth=w)
    p.setStrokeCap(cap)
    p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def blur(p, sigma):
    if sigma > 0.3:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    return p


def linear(p0, p1, colors, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [col(*c) if isinstance(c[0], tuple) else col(c) for c in colors], pos)


def radial(center, r, colors, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*center), max(r, 0.01), [col(*c) if isinstance(c[0], tuple) else col(c) for c in colors], pos)


def shaded(shader):
    return skia.Paint(AntiAlias=True, Shader=shader)


def rrect(x, y, w, h, r):
    return skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)


def poly(pts, closed=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def blob_path(cx, cy, radii, angle0=0.0):
    """Smooth closed blob through points at given radii (Catmull-Rom -> cubic)."""
    n = len(radii)
    pts = [(cx + radii[i] * math.cos(angle0 + 2 * math.pi * i / n),
            cy + radii[i] * math.sin(angle0 + 2 * math.pi * i / n)) for i in range(n)]
    return smooth_closed(pts)


def smooth_closed(pts):
    n = len(pts)
    p = skia.Path()
    p.moveTo(*pts[0])
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        p.cubicTo(*c1, *c2, *p2)
    p.close()
    return p


# ---------------------------------------------------------------- text
_FONTS = {}


def font(size, weight=700):
    w = 800 if weight >= 700 else 600
    key = (round(size, 1), w)
    if key not in _FONTS:
        f = skia.Font(skia.Typeface.MakeFromFile(FONT_FILES[w]), size)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        _FONTS[key] = f
    return _FONTS[key]


def text(c, s, x, y, size, rgb=WHITE, a=255, weight=700, align="center", spacing=0.0):
    f = font(size, weight)
    if spacing:
        s_w = sum(f.measureText(ch) for ch in s) + spacing * (len(s) - 1)
        cx = x - s_w / 2 if align == "center" else x - s_w if align == "right" else x
        for ch in s:
            c.drawString(ch, cx, y, f, fill(rgb, a))
            cx += f.measureText(ch) + spacing
        return
    w = f.measureText(s)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    c.drawString(s, x0, y, f, fill(rgb, a))


# ---------------------------------------------------------------- effects
def glow(c, x, y, r, rgb, a=160):
    """Soft additive-looking glow disc."""
    c.drawCircle(x, y, r, shaded(radial((x, y), r, [(rgb, a), (rgb, a * 0.35), (rgb, 0)], [0, 0.4, 1])))


def soft_shadow(c, path_or_rrect, dx=18, dy=26, sigma=22, a=90):
    p = blur(fill((5, 4, 20), a), sigma)
    c.save()
    c.translate(dx, dy)
    if isinstance(path_or_rrect, skia.RRect):
        c.drawRRect(path_or_rrect, p)
    else:
        c.drawPath(path_or_rrect, p)
    c.restore()


def sparkle(c, x, y, size, a=255, rgb=WHITE, rot=0.0):
    """Four-point twinkle star with halo."""
    if size <= 0.5 or a <= 2:
        return
    glow(c, x, y, size * 1.6, rgb, a * 0.55)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    s, k = size, size * 0.16
    path = skia.Path()
    path.moveTo(0, -s)
    path.quadTo(k, -k, s, 0)
    path.quadTo(k, k, 0, s)
    path.quadTo(-k, k, -s, 0)
    path.quadTo(-k, -k, 0, -s)
    path.close()
    c.drawPath(path, fill(rgb, a))
    c.restore()


def background(c, top=NAVY, bottom=PURPLE):
    c.drawPaint(shaded(linear((0, 0), (0, H), [top, bottom])))


class Dust:
    """Slow drifting specks in the background (parallax by depth)."""

    def __init__(self, n=70, seed=3, rgb=ICE):
        rng = np.random.default_rng(seed)
        self.p = rng.random((n, 2)) * [W, H]
        self.v = (rng.random((n, 2)) - 0.5) * [14, 10] + [0, -6]
        self.r = rng.random(n) * 2.2 + 0.8
        self.ph = rng.random(n) * 6.28
        self.rgb = rgb

    def draw(self, c, t, a=1.0, dx=0.0, dy=0.0):
        for i in range(len(self.r)):
            x = (self.p[i, 0] + self.v[i, 0] * t + dx * self.r[i]) % (W + 40) - 20
            y = (self.p[i, 1] + self.v[i, 1] * t + dy * self.r[i]) % (H + 40) - 20
            tw = 0.55 + 0.45 * math.sin(t * 1.3 + self.ph[i])
            c.drawCircle(x, y, self.r[i], fill(self.rgb, 120 * tw * a))


class Stars:
    def __init__(self, n=220, seed=11):
        rng = np.random.default_rng(seed)
        self.p = rng.random((n, 2)) * [W * 1.6, H * 1.6] - [W * 0.3, H * 0.3]
        self.r = rng.random(n) ** 3 * 2.6 + 0.7
        self.ph = rng.random(n) * 6.28
        self.sp = rng.random(n) * 1.5 + 0.6

    def draw(self, c, t, a=1.0, zoom=1.0, cx=W / 2, cy=H / 2):
        for i in range(len(self.r)):
            x = cx + (self.p[i, 0] - W / 2) * zoom
            y = cy + (self.p[i, 1] - H / 2) * zoom
            if -10 < x < W + 10 and -10 < y < H + 10:
                tw = 0.6 + 0.4 * math.sin(t * self.sp[i] + self.ph[i])
                r = self.r[i] * (0.6 + 0.4 * zoom)
                if r > 1.8:
                    glow(c, x, y, r * 4, ICE, 50 * tw * a)
                c.drawCircle(x, y, r, fill(WHITE, 230 * tw * a))


_GRAIN = None


def finish(rgba, t):
    """Vignette is drawn in Skia; this adds animated film grain. Returns RGB uint8."""
    global _GRAIN
    if _GRAIN is None:
        rng = np.random.default_rng(7)
        _GRAIN = [(rng.normal(0, 1, (H // 2, W // 2)) * 6).astype(np.int16) for _ in range(6)]
    g = _GRAIN[int(t * FPS) % len(_GRAIN)]
    g = np.repeat(np.repeat(g, 2, 0), 2, 1)
    rgb = rgba[:, :, :3].astype(np.int16) + g[:, :, None]
    return np.clip(rgb, 0, 255).astype(np.uint8)


def vignette(c, strength=150):
    c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.75, [((0, 0, 0), 0), ((0, 0, 0), 0), ((5, 3, 18), strength)], [0, 0.55, 1])))


# ---------------------------------------------------------------- characters
def eyes(c, x, y, r, t, look=(0.0, 0.0), blink_phase=0.0, rgb=INK, spread=0.36, size=0.13):
    """Kurzgesagt-style dot eyes with a tiny highlight and occasional blink."""
    cyc = (t + blink_phase * 4.0) % 4.0
    open_ = 1.0 - (1.0 - abs(cyc - 3.9) / 0.1 if abs(cyc - 3.9) < 0.1 else 0.0)
    er = r * size
    for s in (-1, 1):
        ex = x + s * r * spread + look[0] * r * 0.12
        ey = y - r * 0.05 + look[1] * r * 0.12
        c.save()
        c.translate(ex, ey)
        c.scale(1.0, max(0.12, open_))
        c.drawCircle(0, 0, er, fill(rgb))
        c.drawCircle(-er * 0.3, -er * 0.35, er * 0.35, fill(WHITE, 220))
        c.restore()


def atom(c, x, y, r, rgb, t=0.0, a=255, look=(0, 0), blink=0.0, face=True, label=None, label_a=0):
    """Round atom character: gradient body, rim light, dot eyes."""
    if r <= 0.4 or a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    glow(c, x, y, r * 1.9, rgb, 70)
    c.drawCircle(x + r * 0.08, y + r * 0.14, r, blur(fill((5, 4, 20), 70), r * 0.18))
    c.drawCircle(x, y, r, shaded(radial((x - r * 0.35, y - r * 0.4), r * 1.6,
                                        [lighten(rgb, 0.35), rgb, darken(rgb, 0.25)], [0, 0.5, 1])))
    # crescent highlight
    hl = skia.Path()
    hl.addCircle(x - r * 0.28, y - r * 0.32, r * 0.42)
    c.drawPath(hl, fill(WHITE, 40))
    if face and r > 6:
        eyes(c, x, y, r, t, look, blink)
    if label and label_a > 1:
        text(c, label, x, y + r * 0.62, r * 0.42, WHITE, label_a, 800)
    if a < 255:
        c.restore()


def bird(c, x, y, s, t, look=(0.0, 0.0), tilt=0.0, a=255, wing=0.0):
    """The channel mascot: round blue bird in a yellow hard hat and hi-vis vest.
    (x, y) = feet centre, s = body radius."""
    if s <= 1 or a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    body = (96, 132, 255)
    # feet
    for fx in (-0.32, 0.22):
        c.drawLine(fx * s, -0.15 * s, fx * s, 0, stroke(ORANGE, s * 0.09))
        c.drawLine(fx * s, 0, fx * s + 0.16 * s, 0, stroke(ORANGE, s * 0.09))
    cy = -s * 1.05
    # shadow + body
    c.drawCircle(s * 0.08, cy + s * 0.12, s, blur(fill((5, 4, 20), 80), s * 0.15))
    c.drawCircle(0, cy, s, shaded(radial((-s * 0.4, cy - s * 0.45), s * 1.7, [lighten(body, 0.3), body, darken(body, 0.25)], [0, 0.5, 1])))
    # belly
    c.drawOval(skia.Rect.MakeXYWH(-s * 0.55, cy - s * 0.05, s * 1.05, s * 0.95), fill(lighten(body, 0.55)))
    # vest
    vest = skia.Path()
    c.save()
    clip = skia.Path()
    clip.addCircle(0, cy, s)
    c.clipPath(clip, doAntiAlias=True)
    vest.addRect(skia.Rect.MakeXYWH(-s, cy + s * 0.32, s * 2, s * 0.8))
    c.drawPath(vest, fill(ORANGE))
    c.drawRect(skia.Rect.MakeXYWH(-s, cy + s * 0.5, s * 2, s * 0.12), fill((240, 240, 210)))
    c.restore()
    # wing
    c.save()
    c.translate(s * 0.62, cy + s * 0.2)
    c.rotate(-20 - wing * 60)
    c.drawOval(skia.Rect.MakeXYWH(-s * 0.15, -s * 0.2, s * 0.55, s * 0.36), fill(darken(body, 0.15)))
    c.restore()
    # beak
    bx = -s * 0.78 + look[0] * s * 0.1
    c.drawPath(poly([(bx, cy - s * 0.08), (bx - s * 0.42, cy + s * 0.04), (bx, cy + s * 0.16)]), fill(ORANGE))
    eyes(c, -s * 0.25, cy - s * 0.18, s * 0.9, t, look, 0.3, spread=0.3, size=0.12)
    # hard hat
    c.drawPath(_hat(s, cy), shaded(linear((0, cy - s * 1.25), (0, cy - s * 0.55), [lighten(YELLOW, 0.3), darken(YELLOW, 0.1)])))
    c.drawRRect(rrect(-s * 1.0, cy - s * 0.66, s * 2.0, s * 0.16, s * 0.08), fill(darken(YELLOW, 0.12)))
    c.drawRect(skia.Rect.MakeXYWH(-s * 0.07, cy - s * 1.2, s * 0.14, s * 0.55), fill(lighten(YELLOW, 0.35)))
    c.restore()
    if a < 255:
        c.restore()


def _hat(s, cy):
    p = skia.Path()
    p.moveTo(-s * 0.82, cy - s * 0.6)
    p.cubicTo(-s * 0.82, cy - s * 1.35, s * 0.82, cy - s * 1.35, s * 0.82, cy - s * 0.6)
    p.close()
    return p


def cube(c, cx, cy, size, yaw, pitch, rgb=ICE, a=255, edge_a=200, glow_a=80):
    """Shaded solid cube (salt crystal) using a simple perspective projection."""
    pts3 = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
    proj = [project(p, size, yaw, pitch, cx, cy) for p in pts3]
    faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (3, 2, 6, 7), (0, 3, 7, 4), (1, 2, 6, 5)]
    normals = [(0, 0, -1), (0, 0, 1), (0, -1, 0), (0, 1, 0), (-1, 0, 0), (1, 0, 0)]
    light = norm3((-0.5, -0.8, -0.6))  # points toward the light: upper-left, in front
    if glow_a:
        glow(c, cx, cy, size * 2.6, rgb, glow_a * a / 255)
    drawn = []
    for f, n in zip(faces, normals):
        rn = rot3(n, yaw, pitch)
        if rn[2] < 0:  # facing camera (camera looks along +z)
            drawn.append((f, 0.1 + 0.9 * max(0.0, dot3(rn, light)) ** 1.3))
    for f, shade in drawn:
        path = poly([proj[i][:2] for i in f])
        cface = mix((38, 104, 150), lighten(rgb, 0.75), shade)
        c.drawPath(path, fill(cface, a))
        c.drawPath(path, stroke(lighten(rgb, 0.6), max(1.0, size * 0.03), edge_a * a / 255))
    return proj


def rot3(p, yaw, pitch):
    x, y, z = p
    cy_, sy = math.cos(yaw), math.sin(yaw)
    x, z = x * cy_ + z * sy, -x * sy + z * cy_
    cp, sp = math.cos(pitch), math.sin(pitch)
    y, z = y * cp - z * sp, y * sp + z * cp
    return (x, y, z)


def project(p, scale, yaw, pitch, cx, cy, dist=7.0):
    x, y, z = rot3(p, yaw, pitch)
    k = dist / (dist + z)
    return (cx + x * scale * k, cy + y * scale * k, z, k)


def dot3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm3(v):
    l = math.sqrt(dot3(v, v))
    return (v[0] / l, v[1] / l, v[2] / l)
