"""3D GLOBE ENGINE: a real sphere seen through a perspective camera, full bleed.

Natural Earth lon/lat -> unit vectors once; every frame they're rotated into the camera, projected with perspective
(optionally tilted, like a drone looking across the land), decimated to whole pixels and turned into Skia paths.
Countries can rise as 3D slabs, borders burn on as glowing lines with a bright head, the globe gets ocean depth,
an atmosphere rim, sun shading and a star field.
"""
import math

import numpy as np
import skia

import geo

W, H = 1080, 1920
CX, CY = 540, 830                      # where the camera looks (upper middle; captions sit below)
F = 2600.0                             # focal length (px) for the perspective

# palette (dark cinematic)
SPACE0, SPACE1 = (4, 8, 22), (14, 10, 34)
OCEAN0, OCEAN1 = (22, 64, 112), (8, 26, 58)
LANDS = [(196, 182, 144), (156, 176, 132), (192, 150, 124), (148, 164, 186), (176, 156, 186), (212, 194, 152), (136, 176, 158)]
EDGE = (24, 28, 40)
RED, AMBER, CYAN, WHITE = (255, 72, 56), (255, 190, 70), (90, 210, 255), (255, 255, 255)
RIVER = (80, 190, 255)


def unit(lon, lat):
    lon, lat = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)], -1)


def to_lonlat(v):
    return math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(max(-1, min(1, v[2]))))


# ------------------------------------------------------------------ data
class Shape:
    """One country (or any polygon set): rings as unit-vector arrays, a centre and an angular radius for culling."""

    def __init__(self, key, rings_ll, rgb=None, name=""):
        self.key, self.name, self.rgb = key, name, rgb
        self.rings = [unit(np.asarray(r)[:, 0], np.asarray(r)[:, 1]) for r in rings_ll if len(r) > 2]
        allv = np.concatenate(self.rings)
        c = allv.mean(0)
        self.center = c / (np.linalg.norm(c) + 1e-12)
        self.radius = float(np.degrees(np.arccos(np.clip(allv @ self.center, -1, 1)).max()))


_SETS = {}


def countries(res="50m"):
    if res not in _SETS:
        out = []
        for f in geo.load(f"ne_{res}_admin_0_countries"):
            pr = f["properties"]
            out.append(Shape(pr["ADM0_A3"], geo.rings(f["geometry"]), LANDS[(pr["MAPCOLOR7"] - 1) % len(LANDS)], pr["NAME"]))
        _SETS[res] = out
    return _SETS[res]


def shape(a3, res="10m"):
    return next(s for s in countries(res) if s.key == a3)


def chain(lines):
    """Join polylines (lists of [lon, lat]) that share end points into as few long lines as possible."""
    lines = [list(map(tuple, l)) for l in lines if len(l) > 1]
    out = []
    while lines:
        cur = lines.pop(0)
        grew = True
        while grew:
            grew = False
            for i, l in enumerate(lines):
                if _close(l[0], cur[-1]):
                    cur += l[1:]
                elif _close(l[-1], cur[-1]):
                    cur += l[::-1][1:]
                elif _close(l[-1], cur[0]):
                    cur = l[:-1] + cur
                elif _close(l[0], cur[0]):
                    cur = l[::-1][:-1] + cur
                else:
                    continue
                lines.pop(i)
                grew = True
                break
        out.append(cur)
    return out


def _close(a, b):
    return abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) < 1e-6


def border_lines(a, b):
    """Every piece of the land border between two countries (a border can be split, e.g. by Andorra)."""
    ls = []
    for f in geo.load("ne_10m_admin_0_boundary_lines_land"):
        pr = f["properties"]
        if {pr["ADM0_A3_L"], pr["ADM0_A3_R"]} == {a, b}:
            ls += geo.rings(f["geometry"])
    out = [np.array(x) for x in chain(ls) if len(x) > 3]
    return [x[::-1] if x[0, 0] > x[-1, 0] else x for x in sorted(out, key=lambda x: x[:, 0].min())]


def border_line(a, b, west_to_east=True):
    """The land border between two countries as one ordered polyline (lon/lat array)."""
    ls = []
    for f in geo.load("ne_10m_admin_0_boundary_lines_land"):
        pr = f["properties"]
        if {pr["ADM0_A3_L"], pr["ADM0_A3_R"]} == {a, b}:
            ls += geo.rings(f["geometry"])
    best = max(chain(ls), key=len)
    arr = np.array(best)
    if west_to_east and arr[0, 0] > arr[-1, 0]:
        arr = arr[::-1]
    return arr


def river_line(*names, west_to_east=True):
    ls = []
    for f in geo.rivers(*names):
        ls += geo.rings(f["geometry"])
    best = max(chain(ls), key=len)
    arr = np.array(best)
    if west_to_east and arr[0, 0] > arr[-1, 0]:
        arr = arr[::-1]
    return arr


# ------------------------------------------------------------------ camera
class Camera:
    """A pinhole camera hovering over the globe. It looks at (lon, lat) from distance F; R is the globe radius in px
    (zoom); tilt (deg) swings the camera south so it looks north across the land toward a real, curved horizon."""

    def __init__(self, lon, lat, R, tilt=0.0, cx=CX, cy=CY, roll=0.0):
        self.lon, self.lat, self.R, self.tilt, self.cx, self.cy = lon, lat, R, tilt, cx, cy
        l, p = math.radians(lon), math.radians(lat)
        f = np.array([math.cos(p) * math.cos(l), math.cos(p) * math.sin(l), math.sin(p)])
        e = np.array([-math.sin(l), math.cos(l), 0.0])
        n = np.cross(f, e)
        if roll:
            r = math.radians(roll)
            e, n = e * math.cos(r) + n * math.sin(r), -e * math.sin(r) + n * math.cos(r)
        self.M = np.stack([e, n, f])                            # local = M @ world: x east, y north, z up
        th = math.radians(tilt)
        self.C = np.array([0.0, -F * math.sin(th), F * math.cos(th)])     # camera, relative to the target point
        self.w = np.array([0.0, math.sin(th), -math.cos(th)])            # forward
        self.v = np.array([0.0, math.cos(th), math.sin(th)])             # screen up
        cv = self.C - np.array([0.0, 0.0, -R])                            # sphere centre -> camera
        self.dist = float(np.linalg.norm(cv))
        self.chat = cv / self.dist                                        # (local) direction of the camera's sub-point
        self.alpha = math.acos(min(1.0, R / self.dist))                   # angular radius of the visible cap
        self.ca, self.sa = math.cos(self.alpha), math.sin(self.alpha)
        self.view = math.degrees(math.asin(min(1.0, 1700.0 / max(R, 1.0)))) + 4

    def _screen(self, P, h):
        Q = P * (self.R + h)
        Q[:, 2] -= self.R
        d = Q - self.C
        depth = d @ self.w
        depth = np.maximum(depth, 1.0)
        return np.stack([self.cx + F * d[:, 0] / depth, self.cy - F * (d @ self.v) / depth], 1), depth

    def project(self, V, h=0.0, clamp_back=True):
        """Unit vectors (N,3) -> screen (N,2), visibility margin (N,), front mask. h lifts points off the surface (px).
        Hidden points slide along a great circle onto the horizon, so filled shapes stay closed and in place."""
        P = V @ self.M.T
        cosb = P @ self.chat
        front = cosb > self.ca
        if clamp_back and not front.all():
            Q = P[~front]
            cb = cosb[~front][:, None]
            perp = Q - cb * self.chat
            perp /= np.linalg.norm(perp, axis=1, keepdims=True) + 1e-12
            P = P.copy()
            P[~front] = self.chat * self.ca + perp * self.sa
        xy, _ = self._screen(P, h)
        return xy, cosb - self.ca, front

    def project3(self, V, h):
        """Screen points and depth (bigger = farther), for painter's sorting of 3D objects."""
        return self._screen(V @ self.M.T, h)

    def point(self, lon, lat, h=0.0):
        xy, d, _ = self.project(unit(np.array([lon]), np.array([lat])), h, clamp_back=False)
        return float(xy[0, 0]), float(xy[0, 1]), float(d[0])

    def visible(self, sh):
        cw = self.M.T @ self.chat
        ang = math.degrees(math.acos(max(-1, min(1, float(sh.center @ cw)))))
        if ang - sh.radius > math.degrees(self.alpha):
            return False
        ang_f = math.degrees(math.acos(max(-1, min(1, float(sh.center @ self.M[2])))))
        return ang_f - sh.radius < self.view

    def limb(self):
        """Screen centre and radius of the globe's disc (exact for tilt 0, close enough tilted)."""
        xy, depth = self._screen(np.array([[0.0, 0.0, 0.0]]), -self.R)        # the sphere centre
        r = F * self.R / math.sqrt(max(1.0, self.dist ** 2 - self.R ** 2))
        return float(xy[0, 0]), float(xy[0, 1]), r


def lerp(a, b, u):
    return a + (b - a) * u


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def inout(x):
    x = max(0.0, min(1.0, x))
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def slerp_ll(a, b, u):
    va, vb = unit(np.array(a[0]), np.array(a[1])), unit(np.array(b[0]), np.array(b[1]))
    om = math.acos(max(-1, min(1, float(va @ vb))))
    if om < 1e-6:
        return (a[0], a[1]), 0.0
    v = (math.sin((1 - u) * om) * va + math.sin(u * om) * vb) / math.sin(om)
    return to_lonlat(v), math.degrees(om)


def camera_at(t, keys):
    """keys: [(t, lon, lat, R, tilt)] -> Camera. Long moves zoom out on the way (a hop), like a flight."""
    if t <= keys[0][0]:
        return Camera(*keys[0][1:])
    for (t0, *a), (t1, *b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            u = inout((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            (lon, lat), ang = slerp_ll(a[:2], b[:2], u)
            lr = lerp(math.log(a[2]), math.log(b[2]), u)
            near = max(0.0, min(1.0, math.log(max(1.0, min(a[2], b[2]) / 1200.0)) / 1.5))   # no hop between globe-wide views
            hop = min(2.6, ang / 18.0) * near * math.sin(math.pi * u)
            lr = min(lr, lr - hop) if hop > 0 else lr
            return Camera(lon, lat, math.exp(lr), lerp(a[3], b[3], u))
    return Camera(*keys[-1][1:])


# ------------------------------------------------------------------ paths
def ring_path(xy, close=True):
    q = np.round(xy * 2) / 2                                    # half-pixel grid, drop repeats
    keep = np.ones(len(q), bool)
    keep[1:] = np.any(q[1:] != q[:-1], axis=1)
    q = xy[keep]
    if len(q) < 2:
        return None
    p = skia.Path()
    p.addPoly([skia.Point(x, y) for x, y in q.tolist()], close)
    return p


def shape_path(cam, sh, h=0.0):
    p = skia.Path()
    p.setFillType(skia.PathFillType.kEvenOdd)
    any_ = False
    for r in sh.rings:
        xy, _, front = cam.project(r, h)
        if not front.any():
            continue
        if xy[:, 0].max() < -200 or xy[:, 0].min() > W + 200 or xy[:, 1].max() < -200 or xy[:, 1].min() > H + 200:
            continue
        rp = ring_path(xy)
        if rp is not None:
            p.addPath(rp)
            any_ = True
    return p if any_ else None


def line_path(cam, ll, u=1.0, h=0.0):
    """Polyline (lon/lat array) drawn up to fraction u of its length; returns path and the head point."""
    V = unit(ll[:, 0], ll[:, 1])
    xy, _, front = cam.project(V, h, clamp_back=False)
    if u < 1.0:
        seg = np.linalg.norm(np.diff(ll, axis=0), axis=1)
        cum = np.concatenate([[0], np.cumsum(seg)])
        L = cum[-1] * max(0.0, u)
        n = int(np.searchsorted(cum, L))
        if n <= 0:
            return None, None
        if n < len(cum):
            k = (L - cum[n - 1]) / max(1e-9, cum[n] - cum[n - 1])
            head = xy[n - 1] + (xy[n] - xy[n - 1]) * k
            xy = np.vstack([xy[:n], head])
            front = np.concatenate([front[:n], [front[n]]])
    xy = xy[front] if not front.all() else xy
    if len(xy) < 2:
        return None, None
    return ring_path(xy, False), (float(xy[-1, 0]), float(xy[-1, 1]))


# ------------------------------------------------------------------ paint helpers
def fillp(rgb, a=255):
    return skia.Paint(AntiAlias=True, Color=skia.Color(*[int(v) for v in rgb], int(max(0, min(255, a)))))


def strokep(rgb, w, a=255, blur=0.0, plus=False, cap=skia.Paint.kRound_Cap, dash=None):
    p = skia.Paint(AntiAlias=True, Color=skia.Color(*[int(v) for v in rgb], int(max(0, min(255, a)))),
                   Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=cap, StrokeJoin=skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if plus:
        p.setBlendMode(skia.BlendMode.kPlus)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(dash, 0))
    return p


def glow_fill(rgb, a, blur, plus=True):
    p = fillp(rgb, a)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if plus:
        p.setBlendMode(skia.BlendMode.kPlus)
    return p


def mix(a, b, u):
    return tuple(int(lerp(x, y, u)) for x, y in zip(a, b))


def glow_line(c, p, rgb, w=6.0, a=255, core=True, dash=None):
    """A neon line: wide soft bloom, tighter glow, hot core."""
    if p is None or a <= 1:
        return
    c.drawPath(p, strokep(rgb, w * 5, a * 0.35, blur=w * 3, plus=True))
    c.drawPath(p, strokep(rgb, w * 2.2, a * 0.6, blur=w * 0.9, plus=True))
    c.drawPath(p, strokep(rgb, w, a, dash=dash))
    if core:
        c.drawPath(p, strokep(mix(rgb, WHITE, 0.65), w * 0.4, a, dash=dash))


def flare(c, x, y, rgb, r=26, a=255):
    c.drawCircle(x, y, r * 2.4, glow_fill(rgb, a * 0.35, r * 1.4))
    c.drawCircle(x, y, r * 0.8, glow_fill(mix(rgb, WHITE, 0.5), a * 0.8, r * 0.4))
    c.drawCircle(x, y, r * 0.28, fillp(WHITE, a))


# ------------------------------------------------------------------ the world
_STARS = np.random.default_rng(7).uniform([0, 0, 0.3], [W, H, 1.0], (380, 3))


def space(c, cam, t):
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 0), skia.Point(0, H)], [skia.Color(*SPACE1), skia.Color(*SPACE0)])))
    drift = (cam.lon * 3) % W
    for x, y, b in _STARS:
        xx = (x - drift * b) % W
        tw = 0.6 + 0.4 * math.sin(t * 2 + x)
        c.drawCircle(xx, y, 1.6 * b, fillp(WHITE, 200 * b * tw))


def horizon(cam, n=240):
    """The globe's true outline on screen: the rim of the cap the camera can see."""
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ch = cam.chat
    u1 = np.cross(ch, [1.0, 0.0, 0.0])
    u1 /= np.linalg.norm(u1)
    u2 = np.cross(ch, u1)
    P = ch * cam.ca + (np.outer(np.cos(a), u1) + np.outer(np.sin(a), u2)) * cam.sa
    xy, _ = cam._screen(P, 0.0)
    p = skia.Path()
    p.addPoly([skia.Point(x, y) for x, y in xy.tolist()], True)
    return p


def globe(c, cam, t, res="auto", dim=None, colors=None, border_a=120, graticule=True, land_a=255, skip=(), ground=None):
    """Space, atmosphere, ocean, countries, shading. Returns {key: path} of the drawn countries.
    ground: draw this instead of the countries (a function c, cam -> None), for close-ups with their own geometry."""
    hz = horizon(cam)
    b = hz.getBounds()
    limb_on = not (b.left() < -40 and b.top() < -40 and b.right() > W + 40 and b.bottom() > H + 40)
    gx, gy, gr = cam.limb()
    shade = max(0.0, min(1.0, (2200 - cam.R) / 1200))            # sun shading only while it reads as a globe
    space(c, cam, t)
    if limb_on:
        c.drawPath(hz, strokep(CYAN, gr * 0.05 + 10, 110, blur=gr * 0.05 + 8, plus=True))         # atmosphere
        c.drawPath(hz, strokep((140, 210, 255), 6, 140, blur=5, plus=True))
    oc = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        skia.Point(gx - gr * 0.35, gy - gr * 0.4), max(gr * 1.5, H), [skia.Color(*OCEAN0), skia.Color(*OCEAN1)]))
    c.save()
    c.clipPath(hz, doAntiAlias=True)
    c.drawPaint(oc)
    if graticule:
        _graticule(c, cam)
    paths = {}
    if ground is not None:
        ground(c, cam)
    else:
        if res == "auto":
            res = "50m" if cam.R < 3000 else "10m"
        for sh in countries(res):
            if sh.key in skip or not cam.visible(sh):
                continue
            p = shape_path(cam, sh)
            if p is None:
                continue
            rgb = (colors or {}).get(sh.key) or sh.rgb
            if dim and sh.key not in dim.get("keep", ()):
                rgb = mix(rgb, (52, 62, 86), dim.get("amount", 0.0))
            c.drawPath(p, fillp(rgb, land_a))
            paths[sh.key] = p
        for p in paths.values():
            c.drawPath(p, strokep(EDGE, 1.4 if res == "50m" else 1.8, border_a))
    if shade > 0:                                               # sun from the upper left, night toward the rim
        sp = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
            skia.Point(gx - gr * 0.3, gy - gr * 0.35), gr * 1.45,
            [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, int(40 * shade)), skia.Color(0, 4, 20, int(190 * shade))], [0.0, 0.55, 1.0]))
        c.drawPaint(sp)
        c.drawCircle(gx - gr * 0.38, gy - gr * 0.42, gr * 0.5, glow_fill((255, 250, 230), 26 * shade, gr * 0.3))
    c.restore()
    if limb_on:
        c.drawPath(hz, strokep((150, 220, 255), 2.5, 140))
    return paths


def _graticule(c, cam, step=15):
    p = skia.Path()
    for lat in range(-75, 90, step):
        ll = np.stack([np.linspace(-180, 180, 145), np.full(145, lat)], 1)
        xy, _, fr = cam.project(unit(ll[:, 0], ll[:, 1]), clamp_back=False)
        _add_runs(p, xy, fr)
    for lon in range(-180, 180, step):
        ll = np.stack([np.full(73, lon), np.linspace(-90, 90, 73)], 1)
        xy, _, fr = cam.project(unit(ll[:, 0], ll[:, 1]), clamp_back=False)
        _add_runs(p, xy, fr)
    c.drawPath(p, strokep((120, 190, 255), 1.4, 45))


def _add_runs(p, xy, fr):
    start = None
    for i, f in enumerate(list(fr) + [False]):
        if f and start is None:
            start = i
        elif not f and start is not None:
            if i - start > 1:
                p.addPoly([skia.Point(x, y) for x, y in xy[start:i].tolist()], False)
            start = None


def slab(c, cam, sh, rgb, height, a=255, top_glow=None):
    """A country raised off the globe as a 3D slab: stacked walls, then a lit top."""
    if height <= 0.5:
        p = shape_path(cam, sh)
        if p is not None:
            c.drawPath(p, fillp(rgb, a))
        return p
    base = shape_path(cam, sh, 0)
    if base is not None:
        c.drawPath(base, glow_fill((0, 0, 0), 120 * a / 255, 10 + height * 0.25, plus=False))     # contact shadow
    n = max(3, int(height / 3))
    wall = mix(rgb, (20, 20, 30), 0.5)
    for i in range(n):
        p = shape_path(cam, sh, height * i / n)
        if p is not None:
            c.drawPath(p, fillp(mix(wall, rgb, 0.4 * i / n), a))
    top = shape_path(cam, sh, height)
    if top is not None:
        c.drawPath(top, fillp(mix(rgb, WHITE, 0.12), a))
        c.drawPath(top, strokep(mix(rgb, WHITE, 0.6), 2.5, a))
        if top_glow:
            c.drawPath(top, strokep(top_glow, 10, a * 0.5, blur=8, plus=True))
    return top


def vignette(c, a=170):
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
        skia.Point(W / 2, H * 0.45), H * 0.72, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, a)], [0.55, 1.0])))
