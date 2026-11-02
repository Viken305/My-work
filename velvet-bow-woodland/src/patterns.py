"""Build seamless repeat patterns locally from the finished transparent PNGs (no API credits)."""
import random, glob, os
from PIL import Image
T = 3600  # 12 in at 300 DPI
BGS = {"burgundy": (92, 26, 38), "cream": (244, 236, 224)}
SETS = {
 "pt01_woodland_friends": (["characters/c01_fawn", "characters/c03_fox", "characters/c05_bunny", "characters/c07_bear",
                            "characters/c11_hedgehog", "characters/c14_lamb", "characters/c10_owl", "characters/c12_squirrel"], 760, 4),
 "pt02_velvet_bows": (["bows/b01_velvet_classic", "bows/b03_satin_cranberry", "bows/b04_tartan", "bows/b07_double_loop",
                       "bows/b08_sage_velvet", "bows/b10_bow_bell", "bows/b06_lace", "bows/b09_gold_satin"], 560, 5),
 "pt03_winter_botanicals": (["botanicals/f01_holly", "botanicals/f02_mistletoe", "botanicals/f04_berry_branch", "botanicals/f06_christmas_rose",
                             "botanicals/f08_eucalyptus", "botanicals/f10_poinsettia", "botanicals/f05_dried_orange", "botanicals/f11_cotton"], 640, 5),
 "pt04_festive_treasures": (["props/p03_ornament_burgundy", "props/p04_ornament_gold", "props/p01_gift", "props/p12_candycanes",
                             "props/p08_stocking", "props/p11_gingerbread", "props/p15_sleighbells", "props/p06_cocoa"], 600, 5),
 "pt05_bow_woodland_mix": (["characters/c02_fawn_stand", "characters/c06_bunny_sit", "characters/c09_mouse", "bows/b02_velvet_longtails",
                            "bows/b05_gingham", "botanicals/f01_holly", "botanicals/f06_christmas_rose", "props/p03_ornament_burgundy"], 600, 5),
}
def load(path, size):
    im = Image.open(f"final/{path}.png"); im.thumbnail((size, size), Image.LANCZOS); return im
def build(name, files, size, grid, bg, seed):
    rnd = random.Random(seed)
    tile = Image.new("RGBA", (T, T), bg + (255,))
    cell = T / grid
    order = [files[i % len(files)] for i in range(grid * grid)]; rnd.shuffle(order)
    for gy in range(grid):
        for gx in range(grid):
            f = order[gy * grid + gx]
            im = load(f, int(size * rnd.uniform(0.85, 1.1))).rotate(rnd.uniform(-12, 12), resample=Image.BICUBIC, expand=True)
            off = (cell / 2) * (gy % 2)  # half-drop for a natural toss
            cx = gx * cell + cell / 2 + off + rnd.uniform(-cell * .12, cell * .12)
            cy = gy * cell + cell / 2 + rnd.uniform(-cell * .12, cell * .12)
            x, y = int(cx - im.width / 2), int(cy - im.height / 2)
            for dx in (-T, 0, T):
                for dy in (-T, 0, T):
                    tile.paste(im, (x + dx, y + dy), im)
    return tile.convert("RGB")
os.makedirs("final/patterns", exist_ok=True)
for i, (name, (files, size, grid)) in enumerate(SETS.items()):
    for cname, bg in BGS.items():
        t = build(name, files, size, grid, bg, seed=100 + i)
        t.save(f"final/patterns/{name}_{cname}.jpg", quality=94, dpi=(300, 300))
        print(name, cname)
