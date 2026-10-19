"""Natural Earth land (public domain) -> compact polygon lists used by the scenes.

  python3 data/prep.py   (needs ne_50m_land.geojson and ne_10m_land.geojson from naturalearthdata.com, v5.1.2)
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def rings(path):
    for f in json.load(open(path))["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            yield poly[0]


def keep(ring, box):
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    return max(xs) >= box[0] and min(xs) <= box[2] and max(ys) >= box[1] and min(ys) <= box[3]


def thin(ring, step):
    out = [ring[0]]
    for p in ring[1:]:
        if abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) >= step:
            out.append(p)
    return [[round(x, 3), round(y, 3)] for x, y in out]


world = [thin(r, 0.15) for r in rings(os.path.join(HERE, "ne_50m_land.geojson"))]
world = [r for r in world if len(r) > 3]
region = [thin(r, 0.02) for r in rings(os.path.join(HERE, "ne_10m_land.geojson")) if keep(r, (30, -50, 130, 25))]
region = [r for r in region if len(r) > 3]
json.dump(world, open(os.path.join(HERE, "world.json"), "w"), separators=(",", ":"))
json.dump(region, open(os.path.join(HERE, "indian_ocean.json"), "w"), separators=(",", ":"))
print(len(world), len(region))
