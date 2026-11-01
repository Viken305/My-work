"""Map data and drawing for the Paper Atlas style.

Natural Earth (public domain) 1:10m countries, land boundaries, rivers and lakes, downloaded into build/data by
`python3 geo.py fetch`. Two projections: Natural Earth (world views) and a local equirectangular with cos(lat)
correction (zooms). A View maps lon/lat into a rectangle on the canvas.
"""
import json, math, os, subprocess, sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "build", "data")
FILES = ["ne_10m_admin_0_countries", "ne_10m_admin_0_boundary_lines_land", "ne_10m_rivers_lake_centerlines", "ne_10m_lakes"]
URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/{}.geojson"
_CACHE = {}


def fetch():
    os.makedirs(DATA, exist_ok=True)
    for f in FILES:
        dst = os.path.join(DATA, f + ".geojson")
        if not os.path.exists(dst):
            subprocess.run(["curl", "-sS", "-o", dst, URL.format(f)], check=True)


def load(name):
    if name not in _CACHE:
        _CACHE[name] = json.load(open(os.path.join(DATA, name + ".geojson")))["features"]
    return _CACHE[name]


def countries():
    return load("ne_10m_admin_0_countries")


def country(a3):
    return next(f for f in countries() if f["properties"]["ADM0_A3"] == a3)


def rings(geom):
    """Every ring (list of [lon, lat]) of a Polygon / MultiPolygon, or every line of a (Multi)LineString."""
    t, cs = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return cs
    if t == "MultiPolygon":
        return [r for poly in cs for r in poly]
    if t == "LineString":
        return [cs]
    if t == "MultiLineString":
        return cs
    return []


def natural_earth(lon, lat):
    """Natural Earth projection (Šavrič et al. 2011), radians out."""
    l, p = math.radians(lon), math.radians(lat)
    p2 = p * p
    p4 = p2 * p2
    x = l * (0.870700 - 0.131979 * p2 + p4 * (-0.013791 + p4 * (0.003971 * p2 - 0.001529 * p4)))
    y = p * (1.007226 + p2 * (0.015085 + p4 * (-0.044475 + 0.028874 * p2 - 0.005916 * p4)))
    return x, y


class View:
    """lon/lat box -> canvas rect (x0, y0, x1, y1), keeping the aspect (the box is centred and padded to fit)."""

    def __init__(self, rect, lon0, lon1, lat0, lat1, proj="local"):
        self.rect, self.proj = rect, proj
        self.k = math.cos(math.radians((lat0 + lat1) / 2))
        ax0, ay0 = self.raw(lon0, lat1)
        ax1, ay1 = self.raw(lon1, lat0)
        x0, y0, x1, y1 = rect
        self.s = min((x1 - x0) / (ax1 - ax0), (y1 - y0) / (ay1 - ay0))
        self.ox = (x0 + x1) / 2 - self.s * (ax0 + ax1) / 2
        self.oy = (y0 + y1) / 2 - self.s * (ay0 + ay1) / 2

    def raw(self, lon, lat):
        if self.proj == "world":
            x, y = natural_earth(lon, lat)
            return x, -y
        return lon * self.k, -lat

    def __call__(self, lon, lat):
        x, y = self.raw(lon, lat)
        return self.ox + self.s * x, self.oy + self.s * y

    def path(self, geom, close=True):
        p = skia.Path()
        p.setFillType(skia.PathFillType.kEvenOdd)
        for r in rings(geom):
            for i, (lon, lat) in enumerate(r):
                x, y = self(lon, lat)
                (p.moveTo if i == 0 else p.lineTo)(x, y)
            if close:
                p.close()
        return p

    def line(self, pts):
        p = skia.Path()
        for i, (lon, lat) in enumerate(pts):
            (p.moveTo if i == 0 else p.lineTo)(*self(lon, lat))
        return p


def rivers(*names):
    return [f for f in load("ne_10m_rivers_lake_centerlines") if (f["properties"].get("name") or "") in names]


def _dev(pts, a, b):
    """Largest distance (degrees) of pts from the chord a-b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1e-9
    return max((abs((q[0] - a[0]) * dy - (q[1] - a[1]) * dx) / L for q in pts), default=0.0)


def straight_runs(line, tol=0.03, min_deg=1.5):
    """Runs of a polyline that stay within tol degrees of one straight chord for at least min_deg degrees."""
    out, i, n = [], 0, len(line)
    while i < n - 1:
        j = i + 1
        while j + 1 < n and _dev(line[i + 1:j + 1], line[i], line[j + 1]) < tol:
            j += 1
        a, b = line[i], line[j]
        if math.hypot(b[0] - a[0], b[1] - a[1]) >= min_deg:
            out.append((a, b))
        i = j
    return out


def straight_segments(continent="Africa", tol=0.03, min_deg=1.5):
    """Straight land borders between two countries of a continent (surveyed lines, parallels and meridians)."""
    cont = {f["properties"]["ADM0_A3"]: f["properties"]["CONTINENT"] for f in countries()}
    out = []
    for f in load("ne_10m_admin_0_boundary_lines_land"):
        pr = f["properties"]
        if cont.get(pr["ADM0_A3_L"]) != continent or cont.get(pr["ADM0_A3_R"]) != continent:
            continue
        for r in rings(f["geometry"]):
            out += straight_runs(r, tol, min_deg)
    return out


def border_length(continent="Africa"):
    """Total length (degrees, rough) of land borders inside a continent: for the straight share."""
    cont = {f["properties"]["ADM0_A3"]: f["properties"]["CONTINENT"] for f in countries()}
    tot = 0.0
    for f in load("ne_10m_admin_0_boundary_lines_land"):
        pr = f["properties"]
        if cont.get(pr["ADM0_A3_L"]) == continent and cont.get(pr["ADM0_A3_R"]) == continent:
            for r in rings(f["geometry"]):
                tot += sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(r, r[1:]))
    return tot


if __name__ == "__main__" and sys.argv[1:] == ["fetch"]:
    fetch()
