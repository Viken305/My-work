"""WHY BORDERS ARE SHAPED THE WAY THEY ARE: 3D globe flythrough (about 2:20).

One continuous camera flies over a real globe (globe.py) from story to story. Effects are scheduled on the
narration's word times: borders burn on as glowing lines, countries rise as slabs, mountains stand up along ridges,
pins and labels pop, years count up, and chapter cards play while the camera travels. Close-ups that the map data
can't show (El Chamizal, Baarle, the front-door house) are built as 3D geometry in the same camera, so the flight
never cuts. The last half-second blends into frame 0 so the Short loops.
"""
import math, os, re

import numpy as np
import skia

import geo
import globe as G
import timing
from globe import AMBER, CYAN, RED, RIVER, WHITE, Camera, H, Shape, W, fillp, flare, glow_fill, glow_line, mix, strokep, unit
from script import PARTS

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
_TF = {}
FONTS = {"display": "BigShoulders-Black.ttf", "bold": "Atkinson-Bold.ttf", "reg": "Atkinson-Regular.ttf",
         "mono": "MartianMono-Regular.ttf", "monob": "MartianMono-Bold.ttf"}


def font(kind, size):
    if kind not in _TF:
        _TF[kind] = skia.Typeface.MakeFromFile(os.path.join(HERE, "fonts", FONTS[kind]))
    f = skia.Font(_TF[kind], size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


# ------------------------------------------------------------------ timeline from the narration
FIRST = {"part1": 0.5, "part2": 2.0, "part3": 2.0, "part4": 2.0, "part5": 2.0, "part6": 0.9}
GAP = 0.5
EXTRA = {"N3": 0.4, "N5": 1.2, "N6": 1.0, "S2": 0.6, "S3": 0.9, "S4": 0.9, "S5": 0.8, "W2": 0.3, "W3": 1.0, "B2": 0.5}
TAIL = 1.6


def _schedule():
    L, CH, t = {}, {}, 0.0
    for part, ls in PARTS.items():
        d = timing.durations(part)
        CH[part] = t
        t += FIRST[part]
        for k, txt in ls:
            t += EXTRA.get(k, 0.0)
            L[k] = (round(t, 3), round(t + d[k], 3), txt)
            t += d[k] + GAP
        t -= GAP
    return L, CH, round(t + TAIL, 3)


L, CH, TOTAL = _schedule()
LINE_PART = {k: p for p, ls in PARTS.items() for k, _ in ls}
_TM = {p: timing.Timing(p, {k: L[k][0] for k, _ in ls}) for p, ls in PARTS.items()}


def w(k, phrase, end=False):
    return _TM[LINE_PART[k]].word(k, phrase, end)


def S(k):
    return L[k][0]


def E(k):
    return _TM[LINE_PART[k]].end(k)


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t0)


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


def out_back(x, s=1.6):
    x = clamp(x) - 1
    return 1 + x * x * ((s + 1) * x + s)


def lerp(a, b, u):
    return a + (b - a) * u


def window(t, t0, t1, fi=0.35, fo=0.45):
    """0 -> 1 over fi after t0, back to 0 over fo before t1."""
    return smooth(prog(t, t0, t0 + fi)) * (1 - smooth(prog(t, t1 - fo, t1)))


# ------------------------------------------------------------------ data used by the stories
def ll(pts):
    return np.array(pts, float)


def ellipse_ll(lon, lat, rx, ry, rot=0.0, n=90):
    a = np.linspace(0, 2 * math.pi, n)
    r = math.radians(rot)
    x, y = rx * np.cos(a), ry * np.sin(a)
    return np.stack([lon + x * math.cos(r) - y * math.sin(r), lat + x * math.sin(r) + y * math.cos(r)], 1)


def straight_all(min_deg=1.5):
    out = []
    for f in geo.load("ne_10m_admin_0_boundary_lines_land"):
        for r in geo.rings(f["geometry"]):
            out += geo.straight_runs(r, 0.03, min_deg)
    return out


D = {}


def data():
    """Load (once, before workers fork) every line and shape the film uses."""
    if D:
        return D
    D["fra_esp"] = G.border_line("FRA", "ESP")
    D["pyr"] = G.border_lines("FRA", "ESP") + G.border_lines("AND", "ESP")
    D["egy_lby"] = G.border_line("EGY", "LBY")
    D["egy_sdn"] = G.border_line("EGY", "SDN")
    D["usa_mex"] = G.border_line("USA", "MEX")
    D["chl_arg"] = G.border_line("CHL", "ARG")
    D["rivers_na"] = [G.river_line(n) for n in ("Rio Grande", "Mississippi", "Missouri", "Colorado", "Ohio")]
    D["rio"] = G.river_line("Rio Grande")
    D["zambezi"] = G.river_line("Zambezi")
    D["panj"] = G.river_line("Panj")
    D["africa"] = sorted(geo.straight_segments(), key=lambda s: -(s[0][1] + s[1][1]))
    D["straight"] = straight_all()
    usa = geo.country("USA")
    pr = [p[0] for p in usa["geometry"]["coordinates"] if -123.2 < np.mean(np.array(p[0])[:, 0]) < -122.9
          and abs(np.mean(np.array(p[0])[:, 1]) - 48.98) < 0.1]
    D["point_roberts"] = Shape("PTR", pr)
    D["bir_tawil"] = G.shape("BRT")
    brt = np.array(geo.rings(geo.country("BRT")["geometry"])[0])
    D["brt_ring"] = brt
    for a3 in ("MEX", "CHL", "NAM", "AFG", "FRA", "ESP", "TJK", "PAK"):
        D[a3] = G.shape(a3)
    D["baarle"] = baarle_geometry()
    for k in [k for k, _ in G.countries("50m")[:0]]:
        pass
    G.countries("50m")
    G.countries("10m")
    return D


# ------------------------------------------------------------------ labels, pins, badges
def text_w(s, kind, size, tracking=0.0):
    f = font(kind, size)
    return sum(f.measureText(ch) for ch in s) + tracking * size * (len(s) - 1)


def draw_text(c, s, x, y, size, kind="bold", rgb=WHITE, a=255, align="center", tracking=0.0, shadow=True, glow=None):
    if a <= 1:
        return
    f = font(kind, size)
    wd = text_w(s, kind, size, tracking)
    x0 = x - wd / 2 if align == "center" else x - wd if align == "right" else x

    def run(p, dx=0.0, dy=0.0):
        xx = x0
        for ch in s:
            c.drawString(ch, xx + dx, y + dy, f, p)
            xx += f.measureText(ch) + tracking * size
    if glow:
        run(glow_fill(glow, a * 0.55, size * 0.18))
    if shadow:
        sp = fillp((0, 0, 0), a * 0.7)
        sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.08))
        run(sp, 0, size * 0.06)
    run(fillp(rgb, a))


def pin(c, cam, lon, lat, label, t, t0, t1=1e9, rgb=WHITE, size=34, lift=110, sub=None, dot_rgb=None, side=0):
    """A label floating above a point on the ground, on a thin stalk."""
    a = window(t, t0, t1, 0.3, 0.4)
    if a <= 0:
        return
    x, y, vis = cam.point(lon, lat)
    if vis < -0.02:
        return
    k = out_back(prog(t, t0, t0 + 0.45))
    top = y - lift * k
    c.drawLine(x, y, x + side * 30 * k, top + 8, strokep(WHITE, 2.5, 200 * a))
    c.drawCircle(x, y, 7, glow_fill(dot_rgb or rgb, 200 * a, 6))
    c.drawCircle(x, y, 5, fillp(dot_rgb or rgb, 255 * a))
    draw_text(c, label, x + side * 30 * k, top, size, "monob", rgb, 255 * a, "center", 0.08)
    if sub:
        draw_text(c, sub, x + side * 30 * k, top + size * 0.95, size * 0.62, "mono", (210, 220, 235), 230 * a, "center", 0.05)


def ground_label(c, cam, lon, lat, s, t, t0, t1=1e9, size=40, rgb=WHITE, tracking=0.25):
    a = window(t, t0, t1, 0.4, 0.4)
    if a <= 0:
        return
    x, y, vis = cam.point(lon, lat)
    if vis < 0:
        return
    draw_text(c, s, x, y + 14 * (1 - a), size, "monob", rgb, 255 * a * 0.92, "center", tracking)


def badge(c, t, year, sub, t0, t1, count_from=None, y=380):
    """A big year floating over the scene."""
    a = window(t, t0, t1, 0.3, 0.4)
    if a <= 0:
        return
    if count_from is not None:
        u = smooth(prog(t, t0, t0 + count_from[1]))
        s = str(int(round(lerp(count_from[0], int(year), u))))
    else:
        s = year
    k = out_back(prog(t, t0, t0 + 0.5), 1.2)
    c.save()
    c.translate(W / 2, y)
    c.scale(lerp(0.7, 1.0, k), lerp(0.7, 1.0, k))
    draw_text(c, s, 0, 0, 170, "display", WHITE, 255 * a, "center", 0.02, glow=AMBER)
    if sub:
        draw_text(c, sub, 0, 58, 30, "monob", AMBER, 255 * a, "center", 0.12)
    c.restore()


def ring_ll(c, cam, lon, lat, rx, ry, u, rgb=AMBER, wd=5, rot=0.0, a=255):
    if u <= 0 or a <= 1:
        return
    pts = ellipse_ll(lon, lat, rx, ry, rot)
    p, _ = G.line_path(cam, pts, u)
    glow_line(c, p, rgb, wd, a)


def burn(c, cam, pts, t, t0, dur, rgb=RED, wd=6, t_out=1e9, head=True, dash=None, h=0.0):
    """A border/river burning on along its length, with a bright head while it travels."""
    a = 255 * (1 - smooth(prog(t, t_out, t_out + 0.6)))
    u = smooth(prog(t, t0, t0 + dur)) if dur > 0 else float(t >= t0)
    if u <= 0 or a <= 1:
        return
    p, hd = G.line_path(cam, pts, u, h)
    glow_line(c, p, rgb, wd, a, dash=dash)
    if head and hd and u < 1:
        flare(c, *hd, rgb, 24, a)


def peaks(c, cam, pts, t, t0, dur=1.2, every=6, size=1.0, a=255, rgb=(170, 150, 128)):
    """Mountains standing up along a ridge line: little 3D cones with a lit and a shaded face."""
    n = len(pts)
    idx = list(range(0, n, every))
    items = []
    for j, i in enumerate(idx):
        lon, lat = pts[i]
        for side, off in ((-1, 0.0), (1, 0.0)):
            jitter = math.sin(i * 1.7 + side) * 0.08
            items.append((lon + jitter * 0.6, lat + side * 0.16 + jitter, j / max(1, len(idx)), 0.55 + 0.6 * abs(math.sin(i * 0.9 + side))))
    out = []
    for lon, lat, frac, hs in items:
        k = out_back(prog(t, t0 + dur * frac, t0 + dur * frac + 0.35))
        if k <= 0:
            continue
        x, y, vis = cam.point(lon, lat)
        if vis < 0:
            continue
        xt, yt, _ = cam.point(lon, lat, 70 * hs * size * k)
        out.append((y, x, y, xt, yt, hs))
    for _, x, y, xt, yt, hs in sorted(out):
        b = 28 * hs * size * max(0.35, min(1.4, (y - 300) / 900))
        c.drawPath(_tri([(x - b, y), (xt, yt), (x, y + b * 0.18)]), fillp(mix(rgb, (120, 110, 100), 0.1), a))
        c.drawPath(_tri([(x, y + b * 0.18), (xt, yt), (x + b, y)]), fillp(mix(rgb, (60, 60, 80), 0.55), a))
        c.drawPath(_tri([(xt - b * 0.34, yt + (y - yt) * 0.34), (xt, yt), (xt + b * 0.34, yt + (y - yt) * 0.34)]), fillp((248, 250, 255), a))
        c.drawPath(_tri([(x - b, y), (xt, yt), (x + b, y)]), strokep((40, 36, 40), 1.5, a * 0.6))


def _tri(pts):
    p = skia.Path()
    p.addPoly([skia.Point(*q) for q in pts], True)
    return p


def rise(t, t0, t1=1e9, h=40.0):
    return h * out_back(prog(t, t0, t0 + 0.7), 1.3) * (1 - smooth(prog(t, t1, t1 + 0.6)))


# ------------------------------------------------------------------ El Chamizal (schematic ground)
CHZ = (-106.455, 31.765)


def river_lat(lon, k):
    """The Rio Grande near El Paso (schematic): k=0 the 1850s course, k=1 shifted south."""
    base = CHZ[1] + 0.012 * math.sin((lon - CHZ[0]) * 22)
    bump = math.exp(-((lon - CHZ[0]) / 0.05) ** 2)
    return base + 0.016 * bump - 0.05 * bump * k


def chamizal_ground(k_river, k_patch):
    def g(c, cam):
        lons = np.linspace(CHZ[0] - 0.6, CHZ[0] + 0.6, 240)
        r_now = np.array([river_lat(x, k_river) for x in lons])
        r_old = np.array([river_lat(x, 0.0) for x in lons])
        top, bot = CHZ[1] + 0.5, CHZ[1] - 0.5
        north = np.vstack([np.stack([lons, r_now], 1), [[lons[-1], top], [lons[0], top]]])
        south = np.vstack([np.stack([lons, r_now], 1), [[lons[-1], bot], [lons[0], bot]]])
        usa, mex = (184, 168, 140), (150, 176, 124)
        for poly, rgb in ((north, usa), (south, mex)):
            p = G.ring_path(cam.project(unit(poly[:, 0], poly[:, 1]))[0])
            c.drawPath(p, fillp(rgb))
        # the patch between the old and the new course
        m = np.abs(lons - CHZ[0]) < 0.09
        patch = np.vstack([np.stack([lons[m], r_old[m]], 1), np.stack([lons[m], np.array([river_lat(x, 1.0) for x in lons[m]])], 1)[::-1]])
        pp = G.ring_path(cam.project(unit(patch[:, 0], patch[:, 1]))[0])
        if k_patch > 0:
            c.drawPath(pp, fillp(mix(mex, (250, 200, 90), 0.5 + 0.2 * k_patch), 255 * min(1, k_patch * 1.5)))
            c.drawPath(pp, strokep(AMBER, 4, 255 * min(1, k_patch * 1.5)))
        for gl in np.arange(CHZ[0] - 0.6, CHZ[0] + 0.6, 0.02):         # city blocks
            q = np.array([[gl, top], [gl, bot]])
            pth = G.ring_path(cam.project(unit(q[:, 0], q[:, 1]))[0], False)
            c.drawPath(pth, strokep((0, 0, 0), 1, 22))
        riv = np.stack([lons, r_now], 1)
        p = G.ring_path(cam.project(unit(riv[:, 0], riv[:, 1]))[0], False)
        c.drawPath(p, strokep((30, 90, 170), 22))
        glow_line(c, p, RIVER, 8, 255)
    return g


# ------------------------------------------------------------------ Baarle (schematic ground) and the house
BAARLE = (4.935, 51.44)
HOUSE = (4.9412, 51.4428)                      # on the straight east edge of piece 0


def _blob(lon, lat, rx, ry, seed, n=11):
    rng = np.random.default_rng(seed)
    a = np.sort(rng.uniform(0, 2 * math.pi, n))
    r = rng.uniform(0.7, 1.15, n)
    return np.stack([lon + rx * r * np.cos(a), lat + ry * r * np.sin(a)], 1)


def baarle_geometry():
    pieces = []
    spots = [(-0.02, 0.012, 0.009), (0.015, 0.016, 0.006), (0.03, -0.004, 0.008), (-0.035, -0.008, 0.007),
             (0.0, -0.016, 0.006), (0.04, 0.022, 0.005), (-0.012, 0.03, 0.006), (0.022, -0.026, 0.005),
             (-0.04, 0.024, 0.004), (0.05, 0.004, 0.004), (-0.025, -0.03, 0.006), (0.008, 0.034, 0.004)]
    for i, (dx, dy, r) in enumerate(spots):
        pieces.append(_blob(BAARLE[0] + dx, BAARLE[1] + dy, r * 1.5, r, 10 + i))
    # piece 0 gets a straight north-south east edge for the house
    hx, hy = HOUSE
    pieces[0] = np.array([[hx - 0.02, hy - 0.006], [hx - 0.008, hy - 0.0075], [hx, hy - 0.006], [hx, hy + 0.004],
                          [hx - 0.006, hy + 0.0065], [hx - 0.017, hy + 0.007], [hx - 0.024, hy + 0.002]])
    inner = {2: _blob(BAARLE[0] + 0.031, BAARLE[1] - 0.003, 0.004, 0.0028, 50), 6: _blob(BAARLE[0] - 0.012, BAARLE[1] + 0.03, 0.003, 0.002, 51)}
    belg = np.array([[BAARLE[0] - 0.6, BAARLE[1] - 0.048], [BAARLE[0] - 0.05, BAARLE[1] - 0.05], [BAARLE[0], BAARLE[1] - 0.044],
                     [BAARLE[0] + 0.06, BAARLE[1] - 0.052], [BAARLE[0] + 0.6, BAARLE[1] - 0.047], [BAARLE[0] + 0.6, BAARLE[1] - 0.6],
                     [BAARLE[0] - 0.6, BAARLE[1] - 0.6]])
    return dict(pieces=pieces, inner=inner, belgium=belg)


BE, NL = (232, 196, 120), (128, 168, 196)


def baarle_ground(t, slab_h, show_inner=1.0):
    def g(c, cam):
        geo_ = D["baarle"]
        c.drawPaint(fillp(NL))
        pb = G.ring_path(cam.project(unit(geo_["belgium"][:, 0], geo_["belgium"][:, 1]))[0])
        c.drawPath(pb, fillp(BE))
        c.drawPath(pb, strokep(RED, 4))
        for gl in np.arange(BAARLE[0] - 0.1, BAARLE[0] + 0.1, 0.004):     # field lines
            q = np.array([[gl, BAARLE[1] - 0.1], [gl + 0.01, BAARLE[1] + 0.1]])
            c.drawPath(G.ring_path(cam.project(unit(q[:, 0], q[:, 1]))[0], False), strokep((0, 0, 0), 1.2, 18))
        order = sorted(range(len(geo_["pieces"])), key=lambda i: -geo_["pieces"][i][:, 1].mean())
        for i in order:
            pc = geo_["pieces"][i]
            h = slab_h(i)
            sh = Shape(f"b{i}", [pc])
            G.slab(c, cam, sh, BE, h, 255, top_glow=AMBER if h > 2 else None)
            if i in geo_["inner"] and show_inner > 0:
                si = Shape(f"n{i}", [geo_["inner"][i]])
                G.slab(c, cam, si, NL, h * 1.6 * show_inner, 255, top_glow=CYAN)
    return g


def house(c, cam, t, glow_door):
    """A two-storey house straddling the border; walls painted back to front."""
    hx, hy = HOUSE
    mlon = 1 / (111320 * math.cos(math.radians(hy)))
    mlat = 1 / 110540
    wd, dp = 16.0, 10.0
    x0, x1 = hx - 9 * mlon, hx + 7 * mlon                       # the border (lon hx) runs through the house
    y0, y1 = hy - dp / 2 * mlat, hy + dp / 2 * mlat
    px_m = cam.R * math.pi / 180 / 110540                       # pixels per metre at this zoom
    hw, hr = 7.0 * px_m, 11.5 * px_m
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

    def P(lon, lat, h):
        xy, depth = cam.project3(unit(np.array([lon]), np.array([lat])), h)
        return (float(xy[0, 0]), float(xy[0, 1])), float(depth[0])
    faces = []
    wall_rgb = [(236, 222, 196), (214, 198, 172), (200, 184, 160), (226, 210, 186)]
    for i in range(4):
        (a0, b0), (a1, b1) = corners[i], corners[(i + 1) % 4]
        q = [P(a0, b0, 0), P(a1, b1, 0), P(a1, b1, hw), P(a0, b0, hw)]
        faces.append((sum(d for _, d in q) / 4, [xy for xy, _ in q], wall_rgb[i], "wall", i))
    ym = (y0 + y1) / 2
    ridge = [P(x0, ym, hr), P(x1, ym, hr)]
    roofs = [[P(x0, y0, hw), P(x1, y0, hw), ridge[1], ridge[0]], [P(x1, y1, hw), P(x0, y1, hw), ridge[0], ridge[1]]]
    for j, q in enumerate(roofs):
        faces.append((sum(d for _, d in q) / 4 - 1, [xy for xy, _ in q], (150, 70, 60) if j == 0 else (120, 56, 50), "roof", j))
    for gab, xx in ((0, x0), (1, x1)):
        q = [P(xx, y0, hw), P(xx, y1, hw), P(xx, ym, hr)]
        faces.append((sum(d for _, d in q) / 3, [xy for xy, _ in q], (220, 204, 180), "gable", gab))
    for depth, pts, rgb, kind, i in sorted(faces, key=lambda f: -f[0]):
        p = _tri(pts) if len(pts) == 3 else _quad(pts)
        c.drawPath(p, fillp(rgb))
        c.drawPath(p, strokep((40, 30, 30), 2.5))
        if kind == "wall" and i == 0:                           # the front (south) wall: windows, door, the line
            for wx, wy in ((-6.5, 4.6), (2.5, 4.6), (-6.5, 1.6), (4.5, 1.6)):
                win = [P(hx + (wx) * mlon, y0, (wy - 0.0) * px_m), P(hx + (wx + 2.2) * mlon, y0, wy * px_m),
                       P(hx + (wx + 2.2) * mlon, y0, (wy + 1.6) * px_m), P(hx + wx * mlon, y0, (wy + 1.6) * px_m)]
                c.drawPath(_quad([q for q, _ in win]), fillp((190, 220, 240)))
                c.drawPath(_quad([q for q, _ in win]), strokep((40, 30, 30), 2))
            door = [P(hx - 3.2 * mlon, y0, 0), P(hx - 1.6 * mlon, y0, 0), P(hx - 1.6 * mlon, y0, 2.6 * px_m), P(hx - 3.2 * mlon, y0, 2.6 * px_m)]
            dq = _quad([q for q, _ in door])
            if glow_door > 0:
                c.drawPath(dq, strokep(AMBER, 16, 220 * glow_door, blur=10, plus=True))
            c.drawPath(dq, fillp((50, 110, 86)))
            c.drawPath(dq, strokep((30, 20, 20), 2.5))
            line = [P(hx, y0, 0)[0], P(hx, y0, hw)[0]]
            p2 = skia.Path()
            p2.moveTo(*line[0])
            p2.lineTo(*line[1])
            glow_line(c, p2, RED, 5, 255, dash=[18, 12])


def _quad(pts):
    p = skia.Path()
    p.addPoly([skia.Point(*q) for q in pts], True)
    return p


# ------------------------------------------------------------------ camera path
def camera_keys():
    k = []

    def key(t, lon, lat, R, tilt=0.0):
        k.append((t, lon, lat, R, tilt))
    # 1 hook: the globe turns, then frames Europe-Africa-Asia
    key(0.0, -40, 18, 620)
    key(S("H2") - 0.2, 8, 24, 660)
    key(S("H2") + 0.9, 30, 30, 900, 8)
    key(E("H2") + 0.2, 36, 31, 920, 10)
    key(E("H3"), 10, 28, 700)
    # 2 nature
    key(S("N1") + 0.2, -98, 33, 1500, 14)
    key(E("N1"), -101, 31, 2400, 24)
    key(S("N2") + 0.6, -102.5, 30.0, 4300, 36)
    key(E("N2") + 0.1, -103.2, 30.4, 5200, 38)
    key(S("N3") + 1.0, CHZ[0], CHZ[1] - 0.01, 130000, 42)
    key(E("N4"), CHZ[0] + 0.004, CHZ[1] - 0.01, 150000, 46)
    key(S("N5") + 0.6, 0.8, 42.5, 7600, 42)
    key(E("N5") + 0.1, 1.2, 42.6, 8400, 46)
    key(S("N6") + 0.6, -70.5, -36.0, 1500, 30)
    key(E("N6") + 0.1, -71.0, -38.0, 1650, 34)
    # 3 straight lines
    key(S("S1") + 0.2, -30, 25, 760, 0)
    key(E("S1"), -40, 27, 800, 6)
    key(S("S2") + 0.5, -104, 48.0, 2700, 36)
    key(E("S2") + 0.1, -108, 48.5, 2900, 38)
    key(S("S3") + 0.9, -122.98, 48.99, 95000, 40)
    key(E("S3"), -122.96, 49.0, 105000, 44)
    key(S("S4") + 0.6, 17, 4, 1180, 12)
    key(E("S4"), 19, 2, 1250, 16)
    key(S("S5") + 0.6, 31.0, 22.4, 4600, 36)
    key(w("S5", "patch") - 0.2, 32.2, 22.3, 5600, 38)
    key(w("S5", "bir") + 0.5, 33.6, 21.55, 19000, 20)
    key(E("S5") + 0.1, 33.65, 21.55, 20500, 22)
    # 4 deals
    key(S("W1") + 0.4, 21.5, -18.6, 3000, 30)
    key(E("W2") + 0.1, 22.5, -18.4, 3300, 34)
    key(S("W3") + 0.6, 71.5, 36.6, 4600, 38)
    key(E("W3") + 0.1, 72.2, 36.8, 5000, 42)
    # 5 accidents: dive into Baarle, then into one house
    key(S("B1") - 0.8, 4.9, 51.0, 30000, 30)
    key(w("B1", "baarle") + 0.2, BAARLE[0], BAARLE[1] - 0.012, 700000, 46)
    key(E("B1") - 0.4, BAARLE[0] + 0.004, BAARLE[1] - 0.008, 760000, 50)
    key(S("B2") + 0.4, HOUSE[0] - 0.00001, HOUSE[1] - 0.00004, 3.0e8, 62)
    key(E("B2") + 0.3, HOUSE[0] + 0.00001, HOUSE[1] - 0.00004, 3.2e8, 64)
    # 6 ending: back out to the whole world, ending where the film began
    key(S("E1") + 1.2, -10, 25, 760, 0)
    key(E("E2"), -26, 21, 660, 0)
    key(TOTAL, -40, 18, 620, 0)
    return k


KEYS = None


def cam_at(t):
    return G.camera_at(t, KEYS)


# ------------------------------------------------------------------ chapters and captions
CHAPTERS = [("part1", "01", "THE HOOK", ""), ("part2", "02", "NATURE", "rivers & mountains"),
            ("part3", "03", "STRAIGHT LINES", "drawn on paper"), ("part4", "04", "DEALS", "empires trading land"),
            ("part5", "05", "ACCIDENTS", "history left behind"), ("part6", "06", "THE STORY", "")]


def chapter_at(t):
    cur = CHAPTERS[0]
    for ch in CHAPTERS:
        if t >= CH[ch[0]]:
            cur = ch
    return cur


def chapter_card(c, t):
    for part, num, name, sub in CHAPTERS[1:5]:
        t0 = CH[part] + 0.15
        a = window(t, t0, t0 + 2.0, 0.3, 0.45)
        if a <= 0:
            continue
        c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial(
            skia.Point(W / 2, 760), 700, [skia.Color(0, 0, 10, int(150 * a)), skia.Color(0, 0, 10, 0)])))
        draw_text(c, f"CHAPTER {num}", W / 2, 640, 34, "monob", AMBER, 255 * a, "center", 0.3)
        for i, ch in enumerate(name):
            pass
        k = out_cubic(prog(t, t0, t0 + 0.6))
        size = 230 if len(name) < 9 else 170
        c.save()
        c.translate(0, 40 * (1 - k))
        draw_text(c, name, W / 2, 830, size, "display", WHITE, 255 * a, "center", lerp(0.25, 0.04, k), glow=(80, 140, 255))
        c.restore()
        if sub:
            draw_text(c, sub, W / 2, 910, 46, "bold", (220, 230, 245), 230 * a * smooth(prog(t, t0 + 0.3, t0 + 0.7)), "center")
        c.drawLine(W / 2 - 200 * k, 690, W / 2 + 200 * k, 690, strokep(AMBER, 3, 255 * a))


def hud(c, t):
    part, num, name, _ = chapter_at(t)
    a = 1 - window(t, CH[part] + 0.1, CH[part] + 2.0, 0.2, 0.3) if part != "part1" else 1.0
    a *= 1 - smooth(prog(t, TOTAL - 0.8, TOTAL - 0.3))
    a *= smooth(prog(t, 2.6, 3.0)) if part == "part1" else 1.0
    if a > 0.01:
        draw_text(c, num, 64, 236, 54, "display", AMBER, 255 * a, "left")
        draw_text(c, name, 126, 230, 30, "monob", WHITE, 230 * a, "left", 0.2)
    segs = [CH[p] for p, *_ in CHAPTERS] + [TOTAL]                # progress across the chapters
    x0, x1, y = 64, W - 64, 166
    gap = 10
    n = len(CHAPTERS)
    sw = (x1 - x0 - gap * (n - 1)) / n
    for i in range(n):
        u = prog(t, segs[i], segs[i + 1])
        xa = x0 + i * (sw + gap)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(xa, y, sw, 6), 3, 3), fillp(WHITE, 60))
        if u > 0:
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(xa, y, sw * u, 6), 3, 3), fillp(AMBER, 230))


MERGES = {"N3": [("eighteen hundreds", "1800s")], "N4": [("nineteen sixty three", "1963"), ("a hundred", "100")],
          "S2": [("eighteen eighteen", "1818"), ("forty ninth", "49th")], "S4": [("eighteen hundreds", "1800s")]}
KEYW = {"H2": {"wiggle", "straight", "strange"}, "H3": {"story"}, "N1": {"nature"}, "N2": {"rio", "grande"},
        "N3": {"move", "mexico", "american"}, "N4": {"1963"}, "N5": {"pyrenees"}, "N6": {"chile", "andes", "pacific"},
        "S1": {"paper"}, "S2": {"49th"}, "S3": {"point", "roberts", "canada"}, "S4": {"straight"}, "S5": {"bir", "tawil", "neither"},
        "W1": {"deals"}, "W2": {"caprivi", "strip", "zambezi", "victoria", "falls"}, "W3": {"wakhan", "buffer"},
        "B1": {"accidents", "baarle"}, "B2": {"front", "door"}, "E1": {"rivers", "rulers", "deals", "accidents"},
        "E2": {"decision"}, "E3": {"story"}}


def _c(s):
    return re.sub(r"[^\w']", "", s).lower()


def build_pages():
    pages = []
    for k in L:
        ws = _TM[LINE_PART[k]].words(k)
        toks, i = [], 0
        merges = [(m.split(), d) for m, d in MERGES.get(k, [])]
        while i < len(ws):
            hit = next(((m, d) for m, d in merges if [_c(x[2]) for x in ws[i:i + len(m)]] == m), None)
            if hit:
                j = i + len(hit[0]) - 1
                punct = re.sub(r"[\w']", "", ws[j][2])
                toks.append((ws[i][0], hit[1] + punct, _c(hit[1]) in KEYW.get(k, set())))
                i = j + 1
            else:
                toks.append((ws[i][0], ws[i][2], _c(ws[i][2]) in KEYW.get(k, set())))
                i += 1
        cur = []
        for n, tk in enumerate(toks):
            cur.append(tk)
            length = len(" ".join(x[1] for x in cur))
            rest = len(toks) - n - 1
            if rest >= 3 and (length > 44 or (tk[1][-1] in ".," and length > 22 and rest > 3)):
                pages.append([k, cur])
                cur = []
        if cur:
            pages.append([k, cur])
    out = []
    for i, (k, toks) in enumerate(pages):
        t0 = toks[0][0] - 0.15
        nxt = pages[i + 1][1][0][0] - 0.15 if i + 1 < len(pages) else TOTAL
        t1 = min(nxt, E(k) + 0.6)
        out.append((t0, t1, toks))
    return out


PAGES = None


def captions(c, t, y=1470, size=64, width=920):
    f = font("bold", size)
    sp = f.measureText(" ")
    for t0, t1, toks in PAGES:
        if not (t0 <= t < t1):
            continue
        a = smooth(prog(t, t0, t0 + 0.12)) * (1 - smooth(prog(t, t1 - 0.12, t1)))
        lines, cur = [], []
        for tk in toks:
            trial = " ".join(x[1] for x in cur + [tk])
            if cur and f.measureText(trial) > width:
                lines.append(cur)
                cur = [tk]
            else:
                cur.append(tk)
        lines.append(cur)
        for li, ln in enumerate(lines):
            tot = f.measureText(" ".join(x[1] for x in ln))
            x = (W - tot) / 2
            yy = y + li * size * 1.2
            for ts, s, key in ln:
                said = t >= ts
                k = out_back(prog(t, ts, ts + 0.2), 2.0)
                rgb = (AMBER if key else WHITE)
                alpha = (255 if said else 120) * a
                c.save()
                wd = f.measureText(s)
                c.translate(x + wd / 2, yy - size * 0.35)
                sc = lerp(1.0, 1.0 + (0.06 if key else 0.0), 1 - abs(1 - k)) if said else 1.0
                c.scale(sc, sc)
                c.translate(-(x + wd / 2), -(yy - size * 0.35))
                sh = fillp((0, 0, 0), alpha * 0.8)
                sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
                c.drawString(s, x, yy + 4, f, sh)
                if key and said:
                    c.drawString(s, x, yy, f, glow_fill(AMBER, alpha * 0.5, 10))
                c.drawString(s, x, yy, f, fillp(rgb, alpha))
                c.restore()
                x += wd + sp


# ------------------------------------------------------------------ the stories, frame by frame
def dims(t):
    """Which countries to keep bright (others fade to slate), and how much."""
    spans = [((S("N6") - 0.6, E("N6") + 0.8), ("CHL",), 0.55),
             ((S("S5") - 0.2, E("S5") + 0.6), ("EGY", "SDN", "BRT"), 0.45),
             ((S("W1") - 0.3, E("W2") + 0.6), ("NAM",), 0.5),
             ((S("W3") - 0.2, E("W3") + 0.6), ("AFG", "TJK", "PAK"), 0.5)]
    for (t0, t1), keep, amt in spans:
        a = window(t, t0, t1, 0.6, 0.6)
        if a > 0:
            return {"keep": keep, "amount": amt * a}
    return None


EMPIRE_RU, EMPIRE_GB = (120, 190, 130), (226, 140, 160)


def colors(t):
    cols = {"MEX": (196, 214, 178), "USA": (196, 182, 144), "CAN": (176, 156, 186)}
    k = window(t, w("W3", "british") - 0.2, E("W3") + 0.8, 0.5, 0.6)
    if k > 0:
        cols["PAK"] = mix((148, 164, 186), EMPIRE_GB, k)
    k = window(t, w("W3", "russian") - 0.2, E("W3") + 0.8, 0.5, 0.6)
    if k > 0:
        cols["TJK"] = mix((156, 176, 132), EMPIRE_RU, k)
    if S("S5") - 1 < t < E("S5") + 1.5:
        cols["EGY"], cols["SDN"] = (222, 196, 140), (200, 160, 120)
    return cols


def ground_for(t, cam):
    """Close-ups that build their own ground in the same camera."""
    # El Chamizal: fade the schematic in as the camera dives
    if S("N3") + 0.2 < t < E("N4") + 1.4 and cam.R > 25000:
        k_river = smooth(prog(t, w("N3", "shifted"), w("N3", "shifted") + 1.2)) * (1 - smooth(prog(t, w("N4", "hand"), w("N4", "hand") + 1.0)))
        k_patch = smooth(prog(t, w("N3", "piece"), w("N3", "piece") + 0.5)) * (1 - smooth(prog(t, E("N4") + 0.3, E("N4") + 0.9)))
        return chamizal_ground(k_river, k_patch), smooth(prog(cam.R, 25000, 70000))
    if S("B1") - 0.5 < t < E("B2") + 1.0 and cam.R > 90000:
        t_b = w("B1", "baarle")
        tdeal = w("B1", "deals")

        def slab_h(i):
            down = 1 - smooth(prog(t, S("B2") - 0.6, S("B2") + 0.4))
            return 26 * out_back(prog(t, t_b - 0.1 + 0.11 * i, t_b + 0.5 + 0.11 * i)) * down
        return baarle_ground(t, slab_h, smooth(prog(t, tdeal, tdeal + 0.5))), smooth(prog(cam.R, 90000, 250000))
    return None, 0.0


def draw_world(c, t):
    cam = cam_at(t)
    g, k = ground_for(t, cam)
    dm = dims(t)
    if g is None or k < 1:
        G.globe(c, cam, t, dim=dm, colors=colors(t))
    if g is not None and k > 0:
        c.saveLayerAlpha(None, int(255 * k))
        G.globe(c, cam, t, ground=g)
        c.restore()
    stories(c, cam, t)
    return cam


def stories(c, cam, t):
    # ---- 1 hook
    t_out = E("H3") + 0.2
    burn(c, cam, D["fra_esp"], t, w("H2", "wiggle") - 0.15, 0.6, RED, 5, t_out)
    burn(c, cam, D["egy_lby"], t, w("H2", "straight") - 0.15, 0.5, AMBER, 5, t_out)
    burn(c, cam, D["egy_sdn"], t, w("H2", "straight") - 0.05, 0.5, AMBER, 5, t_out)
    if w("H2", "strange") - 0.3 < t < t_out + 0.7:
        G.slab(c, cam, D["AFG"], (232, 150, 120), rise(t, w("H2", "strange") - 0.15, t_out, 22), top_glow=CYAN)
    pin(c, cam, 0.5, 42.8, "WIGGLY", t, w("H2", "wiggle"), t_out, RED, 28, 90)
    pin(c, cam, 25, 26, "RULER STRAIGHT", t, w("H2", "straight"), t_out, AMBER, 28, 120)
    pin(c, cam, 66, 34, "STRANGE", t, w("H2", "strange"), t_out, CYAN, 28, 120)
    # title
    a = window(t, 0.0, S("H2") - 0.1, 0.01, 0.4)
    if a > 0:
        draw_text(c, "WHY ARE BORDERS", W / 2, 330, 118, "display", WHITE, 255 * a, "center", 0.03, glow=(80, 140, 255))
        draw_text(c, "SHAPED LIKE THIS?", W / 2, 450, 118, "display", AMBER, 255 * a, "center", 0.03)
    # ---- 2 nature: rivers of North America, the Rio Grande border
    t_riv = S("N1") + 0.3
    for i, rv in enumerate(D["rivers_na"]):
        burn(c, cam, rv, t, t_riv + 0.35 * i, 1.6, RIVER, 4 if i else 5, E("N2") + 0.3 if i else S("N3") + 0.4, head=True)
    pin(c, cam, -101.2, 29.6, "RIO GRANDE", t, w("N2", "rio"), E("N2") + 0.2, RIVER, 30, 120)
    burn(c, cam, D["usa_mex"], t, w("N2", "rio") - 0.1, 1.6, RED, 6, S("N3") + 0.5)
    if S("N2") - 0.2 < t < S("N3") + 0.8:
        G.slab(c, cam, D["MEX"], (196, 214, 178), rise(t, w("N2", "mexico") - 0.3, S("N3") + 0.2, 18), top_glow=None)
    ground_label(c, cam, -100.5, 33.6, "UNITED STATES", t, S("N2"), S("N3") + 0.3, 40)
    ground_label(c, cam, -104.0, 27.0, "MEXICO", t, S("N2") + 0.2, S("N3") + 0.3, 44)
    # El Chamizal
    t_ch = S("N3") + 0.8
    ground_label(c, cam, CHZ[0] - 0.02, CHZ[1] + 0.16, "EL PASO · USA", t, t_ch, E("N4") + 0.3, 36)
    ground_label(c, cam, CHZ[0] + 0.02, CHZ[1] - 0.075, "CIUDAD JUÁREZ · MEXICO", t, t_ch + 0.2, E("N4") + 0.3, 30)
    pin(c, cam, CHZ[0], CHZ[1] - 0.004, "EL CHAMIZAL", t, w("N3", "piece") + 0.1, E("N4") + 0.4, AMBER, 34, 150, sub="schematic")
    badge(c, t, "1860s", "THE RIVER MOVES", w("N3", "eighteen") - 0.1, w("N3", "piece") - 0.1)
    badge(c, t, "1963", "CHAMIZAL CONVENTION", w("N4", "hundred") - 0.1, E("N4") + 0.4, count_from=(1864, w("N4", "nineteen") - w("N4", "hundred") + 0.2))
    # Pyrenees
    t_p = S("N5")
    for j, piece in enumerate(D["pyr"]):
        burn(c, cam, piece, t, w("N5", "split") - 0.2 + 0.5 * j, 1.2, RED, 6, E("N5") + 0.6)
    if t_p - 0.5 < t < E("N5") + 1.2:
        ridge = np.vstack(D["pyr"])
        ridge = ridge[np.argsort(ridge[:, 0])]
        peaks(c, cam, ridge, t, w("N5", "pyrenees") - 0.3, 1.0, every=14, size=1.7, a=255 * (1 - smooth(prog(t, E("N5") + 0.4, E("N5") + 1.0))))
    ground_label(c, cam, 2.2, 44.2, "FRANCE", t, t_p + 0.2, E("N5") + 0.5, 44)
    ground_label(c, cam, -1.2, 41.2, "SPAIN", t, t_p + 0.4, E("N5") + 0.5, 44)
    pin(c, cam, 0.6, 42.75, "PYRENEES", t, w("N5", "pyrenees"), E("N5") + 0.4, WHITE, 30, 200)
    # Chile and the Andes
    t_c = S("N6")
    if t_c - 0.8 < t < E("N6") + 1.4:
        G.slab(c, cam, D["CHL"], (236, 140, 96), rise(t, w("N6", "chile") - 0.2, E("N6") + 0.6, 46), top_glow=AMBER)
        peaks(c, cam, D["chl_arg"], t, w("N6", "andes") - 0.4, 1.0, every=30, size=1.1,
              a=255 * (1 - smooth(prog(t, E("N6") + 0.5, E("N6") + 1.1))))
    pin(c, cam, -70.3, -30.5, "ANDES", t, w("N6", "andes"), E("N6") + 0.5, WHITE, 30, 150, side=1)
    ground_label(c, cam, -80.5, -36.0, "PACIFIC", t, w("N6", "pacific") - 0.1, E("N6") + 0.5, 40, (170, 210, 255))
    pin(c, cam, -71.5, -40, "CHILE", t, w("N6", "chile"), E("N6") + 0.5, AMBER, 34, 130, sub="~4,300 km long", side=-1)
    # ---- 3 straight lines
    t_s = S("S1") - 0.4
    segs = D["straight"]
    for i, (a_, b_) in enumerate(segs):
        ts = t_s + 2.4 * i / len(segs)
        burn(c, cam, ll([a_, b_]), t, ts, 0.3, AMBER, 4, E("S1") + 0.4, head=False)
    pin(c, cam, -30, 52, "DRAWN ON PAPER", t, w("S1", "paper"), E("S1") + 0.2, AMBER, 30, 10)
    p49 = ll([[-95.15, 49.0], [-110, 49.0], [-123.03, 49.0]])
    burn(c, cam, p49, t, w("S2", "forty") - 0.2, 2.0, RED, 7, E("S3") + 0.4, dash=None)
    badge(c, t, "1818", "THE US & BRITAIN AGREE", w("S2", "eighteen") - 0.15, E("S2") - 0.2)
    ground_label(c, cam, -106, 54.6, "CANADA", t, S("S2") - 0.2, S("S3") + 0.6, 46)
    ground_label(c, cam, -103, 45.0, "UNITED STATES", t, S("S2"), S("S3") + 0.6, 42)
    pin(c, cam, -100, 49.0, "49° N", t, w("S2", "ninth") + 0.1, S("S3") + 0.4, RED, 30, 140)
    pin(c, cam, -104, 51.3, "THE PRAIRIES", t, w("S2", "prairies"), S("S3") + 0.4, (200, 230, 150), 26, 90)
    # Point Roberts
    t_r = S("S3")
    if t_r - 0.6 < t < E("S3") + 1.0:
        G.slab(c, cam, D["point_roberts"], (196, 182, 144), rise(t, w("S3", "point") - 0.2, E("S3") + 0.4, 30), top_glow=AMBER)
    route = ll([[-122.756, 48.990], [-122.756, 49.004], [-122.80, 49.03], [-122.95, 49.04], [-123.05, 49.025], [-123.063, 49.0], [-123.063, 48.986]])
    td = w("S3", "drive") - 0.1
    burn(c, cam, route, t, td, 2.0, CYAN, 4, E("S3") + 0.4, head=False, dash=[16, 12])
    u = smooth(prog(t, td, td + 2.0))
    if 0 < u and t < E("S3") + 0.4:
        p, hd = G.line_path(cam, route, max(0.01, u))
        if hd:
            car(c, hd[0], hd[1])
    pin(c, cam, -123.06, 48.982, "POINT ROBERTS", t, w("S3", "point"), E("S3") + 0.3, AMBER, 32, 200, sub="USA", side=-1)
    ground_label(c, cam, -122.72, 49.16, "CANADA", t, t_r + 0.6, E("S3") + 0.3, 44)
    ground_label(c, cam, -122.78, 48.955, "USA", t, t_r + 0.8, E("S3") + 0.3, 44)
    for lon in (-122.756, -123.063):
        x, y, v = cam.point(lon, 49.0)
        a = window(t, w("S3", "canada") - 0.3, E("S3") + 0.3)
        if a > 0 and v > 0:
            c.drawCircle(x, y, 16, glow_fill(CYAN, 200 * a, 10))
            c.drawCircle(x, y, 9, fillp(WHITE, 255 * a))
    # Africa
    t_a = w("S4", "split") - 0.1
    segs = D["africa"]
    for i, (a_, b_) in enumerate(segs):
        ts = lerp(t_a, w("S4", "lines", end=True) + 0.4, i / len(segs))
        burn(c, cam, ll([a_, b_]), t, ts, 0.35, RED, 6, E("S4") + 0.6, head=True)
    badge(c, t, "1884", "BERLIN CONFERENCE", w("S4", "late") - 0.2, w("S4", "lines") + 0.3)
    pin(c, cam, 8, -8, "200+ PEOPLES", t, w("S4", "hundreds"), E("S4") + 0.4, AMBER, 30, 120, sub="split by borders")
    # Bir Tawil
    l1899 = ll([[25.0, 22.0], [31.0, 22.0], [36.9, 22.0]])
    burn(c, cam, l1899, t, w("S5", "two") - 0.1, 1.2, AMBER, 6, E("S5") + 0.8)
    burn(c, cam, D["brt_ring"], t, w("S5", "different") - 0.1, 1.2, CYAN, 5, E("S5") + 0.8)
    if S("S5") < t < E("S5") + 1.2:
        G.slab(c, cam, D["bir_tawil"], (236, 210, 150), rise(t, w("S5", "bir") - 0.2, E("S5") + 0.6, 34), top_glow=CYAN)
    pin(c, cam, 28.5, 22.0, "1899 LINE", t, w("S5", "two") + 0.2, E("S5") + 0.5, AMBER, 28, 110, sub="22° N")
    pin(c, cam, 33.7, 21.85, "BIR TAWIL", t, w("S5", "bir"), E("S5") + 0.5, CYAN, 34, 170, sub="claimed by no one")
    ground_label(c, cam, 29.5, 24.6, "EGYPT", t, w("S5", "egypt") - 0.1, E("S5") + 0.6, 50)
    ground_label(c, cam, 30.5, 19.0, "SUDAN", t, w("S5", "sudan") - 0.1, E("S5") + 0.6, 50)
    # ---- 4 deals: the Caprivi Strip
    t_w = S("W1")
    if t_w - 0.6 < t < E("W2") + 1.0:
        G.slab(c, cam, D["NAM"], (236, 160, 120), rise(t, t_w + 0.1, E("W2") + 0.4, 30), top_glow=AMBER)
    ring_ll(c, cam, 23.2, -17.95, 2.6, 0.75, prog(t, w("W2", "caprivi") - 0.1, w("W2", "caprivi") + 0.5), AMBER, 5, a=255 * (1 - smooth(prog(t, E("W2") + 0.2, E("W2") + 0.7))))
    pin(c, cam, 22.0, -17.7, "CAPRIVI STRIP", t, w("W2", "caprivi"), E("W2") + 0.4, AMBER, 32, 170)
    badge(c, t, "1890", "GERMANY & BRITAIN TRADE", w("W2", "germany's") - 0.2, w("W2", "but") - 0.2)
    burn(c, cam, D["zambezi"], t, w("W2", "zambezi") - 0.4, 1.6, RIVER, 6, E("W2") + 0.5)
    seaway = ll([[24.0, -17.6], [25.86, -17.92], [29.0, -16.2], [33.0, -16.5], [36.0, -18.8]])
    burn(c, cam, seaway, t, w("W2", "reach") - 0.1, 1.4, AMBER, 4, E("W2") + 0.4, head=True, dash=[18, 12], h=14)
    tf = w("W2", "falls")
    fx, fy, fv = cam.point(25.86, -17.92)
    a = window(t, tf - 0.1, E("W2") + 0.4, 0.15)
    if a > 0 and fv > 0:
        sc = lerp(2.0, 1.0, out_cubic(prog(t, tf - 0.1, tf + 0.15)))
        for k in (-1, 1):
            c.drawLine(fx - 30 * sc, fy - 30 * k * sc, fx + 30 * sc, fy + 30 * k * sc, strokep(RED, 22, 120 * a, blur=10, plus=True))
            c.drawLine(fx - 30 * sc, fy - 30 * k * sc, fx + 30 * sc, fy + 30 * k * sc, strokep(RED, 11, 255 * a))
    pin(c, cam, 25.86, -17.92, "VICTORIA FALLS", t, tf + 0.1, E("W2") + 0.4, RIVER, 28, 110, side=1)
    ground_label(c, cam, 17.0, -22.3, "NAMIBIA", t, t_w + 0.3, E("W2") + 0.4, 46)
    # the Wakhan Corridor
    t_k = S("W3")
    if t_k - 0.5 < t < E("W3") + 1.0:
        G.slab(c, cam, D["AFG"], (236, 160, 120), rise(t, w("W3", "afghanistan's") - 0.2, E("W3") + 0.5, 24), top_glow=AMBER)
    ring_ll(c, cam, 73.4, 37.0, 1.9, 0.38, prog(t, w("W3", "wakhan") - 0.1, w("W3", "wakhan") + 0.5), CYAN, 5, -8, 255 * (1 - smooth(prog(t, E("W3") + 0.3, E("W3") + 0.8))))
    pin(c, cam, 73.0, 37.0, "WAKHAN CORRIDOR", t, w("W3", "wakhan"), E("W3") + 0.5, CYAN, 30, 220, sub="~13 km at its narrowest")
    pin(c, cam, 69.5, 38.8, "RUSSIAN EMPIRE", t, w("W3", "russian") - 0.05, E("W3") + 0.5, EMPIRE_RU, 30, 140)
    pin(c, cam, 71.5, 33.6, "BRITISH INDIA", t, w("W3", "british") - 0.05, E("W3") + 0.5, EMPIRE_GB, 30, 90)
    badge(c, t, "1895", "THE BUFFER IS DRAWN", w("W3", "buffer") - 0.2, E("W3") + 0.4)
    tn = w("W3", "never")
    for (s0, s1, rgb) in (((70.5, 38.4), (73.0, 37.5), EMPIRE_RU), ((72.6, 34.6), (73.4, 36.6), EMPIRE_GB)):
        u = out_cubic(prog(t, tn - 0.1, tn + 0.6))
        a = 255 * (1 - smooth(prog(t, E("W3") + 0.3, E("W3") + 0.8)))
        if u > 0 and a > 1:
            pts = ll([s0, [lerp(s0[0], s1[0], u), lerp(s0[1], s1[1], u)]])
            p, hd = G.line_path(cam, pts, 1.0, h=20)
            glow_line(c, p, rgb, 7, a)
            if hd:
                flare(c, *hd, rgb, 18, a)
    # ---- 5 accidents: Baarle
    t_b = w("B1", "baarle")
    for word, (lon, lat), icon_ in (("cafes", (BAARLE[0] - 0.008, BAARLE[1] + 0.012), "cafe"),
                                     ("gardens", (BAARLE[0] + 0.024, BAARLE[1] + 0.016), "garden"),
                                     ("homes", (BAARLE[0] + 0.03, BAARLE[1] - 0.012), "home")):
        tw = w("B1", word)
        a = window(t, tw - 0.05, S("B2") - 0.2, 0.2, 0.3)
        if a > 0:
            x, y, v = cam.point(lon, lat)
            if v > 0:
                k = out_back(prog(t, tw - 0.05, tw + 0.3))
                c.drawLine(x, y, x, y - 110 * k, strokep(WHITE, 3, 220 * a))
                c.drawCircle(x, y - 110 * k, 44 * k, fillp((20, 24, 40), 230 * a))
                c.drawCircle(x, y - 110 * k, 44 * k, strokep(AMBER, 4, 255 * a))
                icon(c, icon_, x, y - 110 * k, k, a)
    ground_label(c, cam, BAARLE[0] - 0.035, BAARLE[1] + 0.04, "NETHERLANDS", t, t_b, S("B2") - 0.3, 44, (230, 240, 255))
    ground_label(c, cam, BAARLE[0], BAARLE[1] - 0.06, "BELGIUM", t, t_b + 0.2, S("B2") - 0.3, 44, (255, 240, 210))
    pin(c, cam, BAARLE[0] - 0.02, BAARLE[1] + 0.012, "BELGIAN PIECES", t, w("B1", "medieval"), S("B2") - 0.3, AMBER, 26, 130, sub="22 of them, inside NL")
    # the house
    tb2 = S("B2") - 0.2
    if tb2 < t < E("B2") + 1.4 and cam.R > 2e7:
        house(c, cam, t, window(t, w("B2", "front") - 0.1, E("B2") + 1.2, 0.25))
        # the border painted across the street
        x0, y0, _ = cam.point(HOUSE[0], HOUSE[1] - 0.0002)
        x1, y1, _ = cam.point(HOUSE[0], HOUSE[1] - 0.0000455)
        p = skia.Path()
        p.moveTo(x0, y0)
        p.lineTo(x1, y1)
        glow_line(c, p, RED, 7, 255, dash=[24, 16])
        ground_label(c, cam, HOUSE[0] - 0.00009, HOUSE[1] - 0.00012, "BELGIUM", t, tb2 + 0.3, E("B2") + 1.0, 52, (255, 230, 170))
        ground_label(c, cam, HOUSE[0] + 0.000065, HOUSE[1] - 0.00012, "NETHERLANDS", t, tb2 + 0.4, E("B2") + 1.0, 40, (200, 225, 255))
        pin(c, cam, HOUSE[0] - 0.000033, HOUSE[1] - 0.0000455, "FRONT DOOR", t, w("B2", "front"), E("B2") + 1.0, AMBER, 34, 190, sub="= a Belgian house", side=-1)
    # ---- 6 ending: everything at once
    t1 = S("E1")
    if t > t1 - 0.2:
        fade_out = 1 - smooth(prog(t, TOTAL - 1.4, TOTAL - 0.5))
        ka = window(t, w("E1", "rivers") - 0.1, TOTAL, 0.3, 1.2) * fade_out
        if ka > 0:
            for rv in (D["rio"], D["zambezi"]) + tuple(D["rivers_na"][1:]):
                p, _ = G.line_path(cam, rv, 1.0)
                glow_line(c, p, RIVER, 4, 255 * ka)
        kr = window(t, w("E1", "rulers") - 0.1, TOTAL, 0.3, 1.2) * fade_out
        if kr > 0:
            for a_, b_ in D["straight"]:
                p, _ = G.line_path(cam, ll([a_, b_]), 1.0)
                glow_line(c, p, RED, 3.5, 255 * kr, core=False)
        kd = prog(t, w("E1", "deals") - 0.1, w("E1", "deals") + 0.5)
        ring_ll(c, cam, 22.5, -18.5, 6, 3, kd, AMBER, 4, a=255 * fade_out)
        ring_ll(c, cam, 70, 35, 7, 4, kd, AMBER, 4, a=255 * fade_out)
        kx = prog(t, w("E1", "accidents") - 0.1, w("E1", "accidents") + 0.4)
        ring_ll(c, cam, 4.9, 51.4, 3, 1.6, kx, CYAN, 4, a=255 * fade_out)
        ring_ll(c, cam, -106.4, 31.7, 3, 1.6, kx, CYAN, 4, a=255 * fade_out)
        kl = window(t, w("E2", "line") - 0.2, TOTAL, 0.8, 1.4) * fade_out
        if kl > 0:
            for sh in G.countries("50m"):
                if cam.visible(sh):
                    p = G.shape_path(cam, sh)
                    if p is not None:
                        c.drawPath(p, strokep((255, 236, 200), 2.2, 150 * kl, blur=2, plus=True))
        a = window(t, S("E3") + 0.2, TOTAL - 0.3, 0.5, 0.6)
        if a > 0:
            draw_text(c, "THERE'S ALWAYS", W / 2, 330, 112, "display", WHITE, 255 * a, "center", 0.04, glow=(80, 140, 255))
            draw_text(c, "A STORY.", W / 2, 450, 132, "display", AMBER, 255 * a, "center", 0.04)


def icon(c, kind, x, y, k, a):
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    al = 255 * a
    if kind == "cafe":
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-16, -8, 10, 16), 4, 4), fillp(WHITE, al))
        c.drawCircle(13, 3, 7, strokep(WHITE, 3.5, al))
        for dx in (-8, 0):
            c.drawLine(dx, -14, dx + 2, -24, strokep(WHITE, 2.5, al))
    elif kind == "garden":
        c.drawLine(0, 20, 0, 0, strokep((200, 160, 110), 5, al))
        c.drawCircle(0, -8, 15, fillp((120, 210, 120), al))
    else:
        c.drawPath(_tri([(-18, -2), (0, -20), (18, -2)]), fillp(RED, al))
        c.drawRect(skia.Rect.MakeLTRB(-13, -2, 13, 18), fillp(WHITE, al))
    c.restore()


def car(c, x, y):
    c.drawCircle(x, y, 26, glow_fill(CYAN, 160, 14))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 20, y - 11, x + 20, y + 11), 6, 6), fillp(WHITE))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 10, y - 9, x + 9, y + 9), 3, 3), fillp((40, 120, 200)))


# ------------------------------------------------------------------ frame
_GRAIN = None


def scrim(c):
    c.drawRect(skia.Rect.MakeLTRB(0, 1240, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 1240), skia.Point(0, 1700)], [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 10, 190)])))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 320), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 0), skia.Point(0, 320)], [skia.Color(0, 0, 10, 150), skia.Color(0, 0, 10, 0)])))


def draw(c, t):
    draw_world(c, t)
    G.vignette(c, 150)
    scrim(c)
    chapter_card(c, t)
    hud(c, t)
    captions(c, t)


def setup():
    global KEYS, PAGES
    data()
    if KEYS is None:
        KEYS = camera_keys()
    if PAGES is None:
        PAGES = build_pages()


def frame(t):
    global _GRAIN
    setup()
    s = skia.Surface(W, H)
    draw(s.getCanvas(), t)
    img = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
    if t > TOTAL - 0.5:
        s0 = skia.Surface(W, H)
        draw(s0.getCanvas(), 0.0)
        img0 = s0.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
        k = smooth(prog(t, TOTAL - 0.5, TOTAL))
        img = (img * (1 - k) + img0 * k).astype(np.uint8)
    if _GRAIN is None:
        _GRAIN = np.random.default_rng(3).normal(0, 4, (H, W, 1)).astype(np.int16)
    return np.clip(img.astype(np.int16) + _GRAIN, 0, 255).astype(np.uint8)
