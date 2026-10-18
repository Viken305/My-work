"""World kit for "Earth Is Weirder Than You Think": a procedural spinning globe, skies, landscapes and props."""
import math, os

import numpy as np

from premium import *  # noqa: F401,F403
from rig import face_rig, pose, Track, blink_amount  # noqa: F401

OCEAN_DEEP = (22, 60, 140)
OCEAN = (40, 110, 200)
SHALLOW = (70, 170, 220)
LAND = (96, 170, 90)
FOREST = (52, 128, 70)
DESERT = (222, 186, 120)
ICE = (236, 244, 252)
SKY_TOP = (40, 90, 180)
SKY_LOW = (130, 190, 240)
NIGHT_TOP = (8, 10, 34)
NIGHT_LOW = (30, 34, 80)
GOLD = (255, 214, 120)


# ---------------------------------------------------------------- globe
_MAP = None


def _world_map():
    """Equirectangular height + biome map (cached). Land from fBm; biomes by latitude + moisture noise."""
    global _MAP
    if _MAP is not None:
        return _MAP
    path = os.path.join(CACHE, "worldmap.npz")
    if os.path.exists(path):
        d = np.load(path)
        _MAP = d["rgb"]
        return _MAP
    os.makedirs(CACHE, exist_ok=True)
    h, w = 768, 1536

    def tile(a):      # make the noise wrap around horizontally (no seam on the globe)
        wgt = (0.5 - 0.5 * np.cos(2 * np.pi * np.arange(a.shape[1]) / a.shape[1]))[None, :]
        return a * wgt + np.roll(a, a.shape[1] // 2, axis=1) * (1 - wgt)
    n = tile(fbm(h, w, seed=17, base=220, octaves=6))
    n = (n - n.min()) / (n.max() - n.min())
    m = tile(fbm(h, w, seed=29, base=160, octaves=5))
    m = (m - m.min()) / (m.max() - m.min())
    ice_edge = 0.84 + 0.05 * (tile(fbm(h, w, seed=5, base=40, octaves=3)) - 0.5)
    lat = np.abs(np.linspace(-1, 1, h))[:, None] * np.ones((1, w))
    land = n > 0.56
    coast = (n > 0.5) & ~land
    rgb = np.zeros((h, w, 3), np.float32)
    deep = np.array(OCEAN_DEEP, np.float32)
    oc = np.array(OCEAN, np.float32)
    k = np.clip((n - 0.2) / 0.36, 0, 1)[..., None]
    rgb[:] = deep * (1 - k) + oc * k
    rgb[coast] = np.array(SHALLOW, np.float32)
    dry = (m < 0.42) & (lat > 0.15) & (lat < 0.45)
    green = np.where(m[..., None] > 0.55, np.array(FOREST, np.float32), np.array(LAND, np.float32))
    lr = np.where(dry[..., None], np.array(DESERT, np.float32), green)
    rgb[land] = lr[land]
    rgb[lat > ice_edge] = np.array((214, 226, 240), np.float32)
    _MAP = rgb.astype(np.uint8)
    np.savez_compressed(path, rgb=_MAP)
    return _MAP


def globe(c, x, y, r, t, rot=0.0, tilt=0.4, a=255, clouds=True, night=0.0, bulge=0.0):
    """Orthographic globe of radius r at (x, y); rot = longitude offset (radians); bulge squashes it (exaggerated oblateness)."""
    if r < 2 or a <= 1:
        return
    res = int(min(2 * r, 760))
    mp = _world_map()
    hh, ww = mp.shape[:2]
    yy, xx = np.mgrid[0:res, 0:res].astype(np.float32)
    u = (xx + 0.5) / res * 2 - 1
    v = (yy + 0.5) / res * 2 - 1
    d2 = u * u + v * v
    inside = d2 < 1
    z = np.sqrt(np.clip(1 - d2, 0, 1))
    # tilt about x axis
    ct, st = math.cos(tilt), math.sin(tilt)
    y2 = v * ct - z * st
    z2 = v * st + z * ct
    lat = np.arcsin(np.clip(-y2, -1, 1))
    lon = np.arctan2(u, z2) + rot
    px = ((lon / (2 * math.pi)) % 1.0 * ww).astype(np.int32) % ww
    py = ((0.5 - lat / math.pi) * hh).astype(np.int32).clip(0, hh - 1)
    col = mp[py, px].astype(np.float32)
    if clouds:
        cl = _cloud_map()
        cv = cl[py, ((px + int(t * 6)) % ww)][..., None]
        col = col * (1 - cv * 0.75) + 245 * cv * 0.75
    # lighting: sun from upper-left, terminator for night
    light_ = np.clip(0.3 + 0.72 * (-0.45 * u - 0.35 * v + 0.82 * z), 0.15, 1.0)[..., None]
    col = col * light_
    if night > 0:
        col = col * (1 - night * 0.75)
    rgba = np.zeros((res, res, 4), np.uint8)
    rgba[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    edge = np.clip((1 - np.sqrt(d2)) * res * 0.5, 0, 1)
    rgba[..., 3] = (inside * edge * 255).astype(np.uint8)
    rgba[..., :3] = (rgba[..., :3].astype(np.float32) * (rgba[..., 3:4] / 255.0)).astype(np.uint8)
    img = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    light(c, x, y, r * 1.35, (110, 170, 255), 90 * a / 255)
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(a / 255)
    c.save()
    c.translate(x, y)
    c.scale(1 + bulge, 1 - bulge)
    c.drawImageRect(img, skia.Rect.MakeXYWH(-r, -r, 2 * r, 2 * r), skia.SamplingOptions(skia.FilterMode.kLinear), p)
    atm = skia.Paint(AntiAlias=True, Shader=radial((0, 0), r * 1.08, [((120, 190, 255), 0), ((120, 190, 255), 0), ((150, 210, 255), 160 * a / 255), ((150, 210, 255), 0)],
                                                   [0, 0.88, 0.95, 1]))
    atm.setBlendMode(skia.BlendMode.kPlus)
    c.drawCircle(0, 0, r * 1.08, atm)
    c.restore()


_CL = None


def _cloud_map():
    global _CL
    if _CL is None:
        n = fbm(768, 1536, seed=41, base=90, octaves=5)
        wgt = (0.5 - 0.5 * np.cos(2 * np.pi * np.arange(1536) / 1536))[None, :]
        n = n * wgt + np.roll(n, 768, axis=1) * (1 - wgt)
        n = (n - n.min()) / (n.max() - n.min())
        _CL = np.clip((n - 0.55) / 0.25, 0, 1).astype(np.float32)
    return _CL


# ---------------------------------------------------------------- skies
SF = Starfield(8, (900, 300, 80))


def sky(c, t, cam=None, mood="day", a=1.0):
    cam = cam or Cam()
    if mood == "day":
        c.drawPaint(shaded(linear((0, 0), (0, H), [SKY_TOP, SKY_LOW])))
        light(c, W * 0.8, H * 0.15, 520, (255, 240, 210), 50)
    elif mood == "sunset":
        c.drawPaint(shaded(linear((0, 0), (0, H), [(60, 50, 130), (230, 120, 110), (255, 190, 120)], [0, 0.65, 1])))
    elif mood == "night":
        c.drawPaint(shaded(linear((0, 0), (0, H), [NIGHT_TOP, NIGHT_LOW])))
        SF.draw(c, t, cam, a)
    elif mood == "space":
        c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.8, [(16, 18, 50), (4, 5, 18)])))
        SF.draw(c, t, cam, a)
    elif mood == "storm":
        c.drawPaint(shaded(linear((0, 0), (0, H), [(30, 34, 60), (70, 76, 110)])))


def cloud_puff(c, x, y, s, a=200, rgb=(236, 242, 252)):
    for dx, dy, rr in ((0, 0, 1.0), (-0.9, 0.25, 0.7), (0.9, 0.2, 0.75), (-0.4, -0.35, 0.65), (0.45, -0.3, 0.6)):
        c.drawCircle(x + dx * s, y + dy * s, rr * s, fill(rgb, a))


def milky_way(c, t, a=255):
    c.save()
    c.rotate(-22, W / 2, H / 2)
    draw_texture(c, nebula_texture("milky", 13, [(0.0, (10, 10, 40)), (0.5, (70, 60, 140)), (0.8, (200, 170, 220)), (1.0, (255, 240, 240))],
                                   density=0.95, warp=120, lo=0.4), W / 2, H * 0.45, 1.7, t * 0.2, 170 * a / 255, skia.BlendMode.kPlus)
    rng = np.random.default_rng(3)
    for k in range(500):
        x = rng.uniform(-200, W + 200)
        y = H * 0.45 + rng.normal(0, 90)
        tw = 0.6 + 0.4 * math.sin(t * rng.uniform(1, 3) + k)
        c.drawCircle(x, y, rng.uniform(0.6, 1.8), add((255, 250, 240), 200 * tw * a / 255))
    c.restore()


# ---------------------------------------------------------------- trees & landscapes
def tree(c, x, y, s, kind=0, t=0.0, a=255, rgb=None, sway=1.0):
    """Stylised tree with base at (x, y). kind 0 = round broadleaf, 1 = conifer, 2 = palm."""
    w = 3 * math.sin(t * 1.2 + x * 0.01) * sway
    if kind == 1:
        rgb = rgb or (40, 110, 80)
        c.drawRect(skia.Rect.MakeXYWH(x - s * 0.06, y - s * 0.35, s * 0.12, s * 0.35), fill((100, 70, 50), a))
        for k in range(3):
            yy = y - s * (0.3 + 0.28 * k)
            ww = s * (0.42 - 0.1 * k)
            c.drawPath(poly([(x - ww + w * k * 0.4, yy), (x + ww + w * k * 0.4, yy), (x + w * (k + 1) * 0.5, yy - s * 0.45)]),
                       fill(darken(rgb, 0.08 * k) if k else rgb, a))
        return
    if kind == 2:
        c.drawLine(x, y, x + s * 0.1 + w, y - s, stroke((140, 100, 60), s * 0.07, a))
        for k in range(6):
            an = math.radians(-160 + k * 28)
            c.drawLine(x + s * 0.1 + w, y - s, x + s * 0.1 + w + math.cos(an) * s * 0.45, y - s + math.sin(an) * s * 0.3 + s * 0.12, stroke((60, 140, 70), s * 0.08, a))
        return
    rgb = rgb or FOREST
    c.drawRect(skia.Rect.MakeXYWH(x - s * 0.06, y - s * 0.45, s * 0.12, s * 0.45), fill((110, 76, 52), a))
    for dx, dy, rr in ((0, -0.62, 0.34), (-0.22, -0.5, 0.24), (0.22, -0.5, 0.25)):
        c.drawCircle(x + dx * s + w, y + dy * s, rr * s, shaded(radial((x + dx * s + w - rr * s * 0.3, y + dy * s - rr * s * 0.4), rr * s * 1.5,
                                                                      [(lighten(rgb, 0.2), a), (rgb, a), (darken(rgb, 0.3), a)])))


def hills(c, y0, rgb, t=0.0, amp=60, freq=0.004, phase=0.0, a=255, x_off=0.0):
    p = skia.Path()
    p.moveTo(-50, H + 50)
    for x in range(-50, W + 60, 30):
        xx = x + x_off
        p.lineTo(x, y0 - amp * (0.6 * math.sin(xx * freq + phase) + 0.4 * math.sin(xx * freq * 2.3 + phase * 1.7)))
    p.lineTo(W + 50, H + 50)
    p.close()
    c.drawPath(p, fill(rgb, a))
    return p


def ground_y(x, y0, amp=60, freq=0.004, phase=0.0, x_off=0.0):
    xx = x + x_off
    return y0 - amp * (0.6 * math.sin(xx * freq + phase) + 0.4 * math.sin(xx * freq * 2.3 + phase * 1.7))


def forest_band(c, t, y0, n, s, seed, rgb, a=255, x_off=0.0, kinds=(0, 1)):
    rng = np.random.default_rng(seed)
    xs = np.sort(rng.uniform(-100, W + 100, n))
    for i, x in enumerate(xs):
        xx = (x - x_off) % (W + 200) - 100
        tree(c, xx, y0 + rng.uniform(-10, 10), s * rng.uniform(0.75, 1.25), kinds[i % len(kinds)], t, a, mix(rgb, (0, 0, 0), rng.uniform(0, 0.15)))


def dunes(c, t, y0, rgb=DESERT, x_off=0.0):
    for k, (yy, amp, sh) in enumerate([(y0 - 80, 50, 0.85), (y0, 70, 1.0), (y0 + 120, 60, 0.92)]):
        p = hills(c, yy, mix(rgb, (120, 70, 50), 0.25 * (1 - sh) + 0.1 * (2 - k)), t, amp, 0.003 + 0.001 * k, k * 1.7, 255, x_off * (0.4 + 0.3 * k))
    light(c, W * 0.8, H * 0.2, 600, (255, 220, 160), 50)


def ice_field(c, t, y0, x_off=0.0):
    hills(c, y0 - 140, (150, 176, 214), t, 90, 0.002, 0.3, 255, x_off * 0.3)
    hills(c, y0 - 40, (176, 198, 228), t, 40, 0.004, 1.1, 255, x_off * 0.6)
    hills(c, y0 + 80, (200, 216, 238), t, 25, 0.006, 2.0, 255, x_off)
    rng = np.random.default_rng(5)
    for k in range(40):      # wind-blown snow
        u = (t * 0.4 + rng.random()) % 1.0
        c.drawCircle(W * (1.1 - 1.3 * u), rng.uniform(0, H), rng.uniform(1.5, 3.5), fill(WHITE, 160))


def penguin(c, x, y, s, t, p=None, look=(0.0, 0.0), blink=0.0, flap=0.0):
    """Tiny penguin character with base at (x, y)."""
    b = skia.Path()
    b.addOval(skia.Rect.MakeXYWH(x - s * 0.42, y - s * 1.1, s * 0.84, s * 1.1))
    c.drawOval(skia.Rect.MakeXYWH(x - s * 0.5, y - s * 0.05, s, s * 0.14), fill((60, 80, 120), 80))
    c.drawPath(b, fill((30, 34, 54)))
    c.drawOval(skia.Rect.MakeXYWH(x - s * 0.3, y - s * 0.86, s * 0.6, s * 0.84), fill((222, 228, 240)))
    for side in (-1, 1):
        c.save()
        c.translate(x + side * s * 0.4, y - s * 0.7)
        c.rotate(side * (15 + 40 * flap * abs(math.sin(t * 12))))
        c.drawOval(skia.Rect.MakeXYWH(-s * 0.08, 0, s * 0.16, s * 0.5), fill((30, 34, 54)))
        c.restore()
    c.drawPath(poly([(x - s * 0.08, y - s * 0.74), (x + s * 0.08, y - s * 0.74), (x, y - s * 0.62)]), fill((255, 170, 60)))
    for side in (-1, 1):
        c.drawOval(skia.Rect.MakeXYWH(x + side * s * 0.16 - s * 0.1, y - s * 0.06, s * 0.2, s * 0.08), fill((255, 170, 60)))
    face_rig(c, x, y - s * 0.84, s * 0.42, p or pose("neutral"), look, blink, spread=0.34)


def bolt_path(x0, y0, x1, y1, seed, jag=40, n=9):
    rng = np.random.default_rng(seed)
    p = skia.Path()
    p.moveTo(x0, y0)
    for i in range(1, n):
        u = i / n
        p.lineTo(lerp(x0, x1, u) + rng.uniform(-jag, jag), lerp(y0, y1, u))
    p.lineTo(x1, y1)
    return p


def lightning(c, x0, y0, x1, y1, seed, k=1.0, w=6):
    """Lightning bolt with glow; k 0..1 fades it (flash decays quickly)."""
    if k <= 0.01:
        return
    p = bolt_path(x0, y0, x1, y1, seed)
    g = stroke((180, 200, 255), w * 6, 120 * k)
    g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, w * 2))
    g.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(p, g)
    c.drawPath(p, stroke((250, 250, 255), w, 255 * k))
    light(c, x1, y1, 160, (200, 210, 255), 160 * k)


def ant(c, x, y, s, t, ang=0.0, p=None, look=(0.0, 0.0), walk=1.0, a=255, rgb=(70, 40, 34)):
    """Ant character seen from the side: three body segments, six legs that walk, antennae, rig face on the head."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    for i in range(3):     # legs
        for side in (-1, 1):
            ph = t * 14 * walk + i * 2.1 + (0 if side > 0 else math.pi)
            lx = -s * 0.15 + i * s * 0.3
            c.drawLine(lx, s * 0.1, lx + s * 0.25 * math.sin(ph) * side * 0.8, s * 0.55, stroke(darken(rgb, 0.2), s * 0.07, 255))
    c.drawOval(skia.Rect.MakeXYWH(-s * 1.05, -s * 0.32, s * 0.72, s * 0.6), fill(rgb))          # abdomen
    c.drawOval(skia.Rect.MakeXYWH(-s * 0.38, -s * 0.18, s * 0.5, s * 0.34), fill(lighten(rgb, 0.1)))  # thorax
    c.drawCircle(s * 0.45, -s * 0.12, s * 0.34, shaded(radial((s * 0.35, -s * 0.25), s * 0.5, [lighten(rgb, 0.35), rgb])))
    for side in (-1, 1):   # antennae
        an = math.radians(-60 + side * 18) + 0.15 * math.sin(t * 6 + side)
        ax, ay = s * 0.55 + math.cos(an) * s * 0.55, -s * 0.38 + math.sin(an) * s * 0.55
        q = skia.Path()
        q.moveTo(s * 0.55, -s * 0.38)
        q.quadTo(s * 0.6, -s * 0.8, ax, ay)
        c.drawPath(q, stroke(darken(rgb, 0.1), s * 0.05))
        c.drawCircle(ax, ay, s * 0.06, fill(rgb))
    c.drawOval(skia.Rect.MakeXYWH(-s * 0.9, -s * 0.26, s * 0.3, s * 0.12), fill(WHITE, 50))
    if p is not None and s > 10:
        face_rig(c, s * 0.5, -s * 0.12, s * 0.3, p, look, 0.0, ink=(20, 10, 10), spread=0.36)
    if a < 255:
        c.restore()
    c.restore()


def human(c, x, y, h, rgb=(80, 90, 140), a=255, wave=0.0, t=0.0):
    """Simple friendly person (feet at y)."""
    s = h / 600
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawOval(skia.Rect.MakeXYWH(-90, -14, 180, 28), fill((20, 20, 40), 60))
    body = skia.Path()
    body.addCircle(0, -520, 62)
    body.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-90, -448, 180, 280), 80, 80))
    body.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-76, -190, 66, 190), 30, 30))
    body.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(10, -190, 66, 190), 30, 30))
    c.drawPath(body, fill(rgb, a))
    c.save()
    c.translate(-100, -420)
    c.rotate(20)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-26, 0, 52, 220), 26, 26), fill(rgb, a))
    c.restore()
    c.save()
    c.translate(100, -420)
    c.rotate(-20 - 140 * wave + 20 * wave * math.sin(t * 8))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-26, 0, 52, 220), 26, 26), fill(rgb, a))
    c.restore()
    c.drawCircle(0, -520, 62, fill(lighten(rgb, 0.15), a))
    c.restore()
