import sys; sys.path.insert(0, "src")
from concurrent.futures import ThreadPoolExecutor
from recraft import generate, download
BG = {
 "linen": "Top-down flat lay product photography of an empty soft cream linen tablecloth with gentle natural folds, soft window light, warm cozy Christmas mood, a few small pine sprigs and dried orange slices only at the very corners, large empty center, no text",
 "wood": "Top-down flat lay photography of an empty dark walnut wooden table surface, warm soft light, subtle wood grain, cozy Christmas evening mood, a few tiny gold fairy lights scattered only near the edges, large empty center, no text",
 "wall": "Interior photography of a cozy vintage living room with a plain warm cream painted wall taking up the upper two thirds of the image, a dark wooden sideboard at the bottom with candles, small pine garland and a few wrapped gifts, soft warm light, the wall is completely empty, no pictures, no text",
 "velvet": "Close-up photography of rich deep burgundy crushed velvet fabric filling the whole frame, soft luxurious folds, warm subtle light, no objects, no text",
}
def run(kv):
    n, p = kv
    urls, cr = generate(p, model="recraftv4_1_flash", size="3:2", n=2)
    for i, u in enumerate(urls): download(u, f"raw/bg/{n}_{'ab'[i]}.png")
    return n, cr
with ThreadPoolExecutor(4) as ex:
    for n, cr in ex.map(run, BG.items()): print(n, cr)
