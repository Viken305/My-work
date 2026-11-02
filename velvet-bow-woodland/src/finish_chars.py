import sys, shutil; sys.path.insert(0, "src")
from concurrent.futures import ThreadPoolExecutor
from recraft import crisp_upscale, remove_background, download
from finish import repair_and_trim
PICKS = {"c01_fawn":"b","c02_fawn_stand":"a","c03_fox":"b","c04_fox_walk":"b","c05_bunny":"b","c06_bunny_sit":"a",
         "c07_bear":"b","c08_bear_stand":"b","c09_mouse":"a","c10_owl":"b","c11_hedgehog":"a","c12_squirrel":"b",
         "c13_polarbear":"b","c14_lamb":"b","c15_raccoon":"b","c16_badger":"a"}
def run(kv):
    n, s = kv
    u, _ = crisp_upscale(f"raw/chars/{n}_{s}.png"); download(u, f"hires/chars/{n}.png")
    u, _ = remove_background(f"hires/chars/{n}.png"); download(u, f"hires/chars/{n}_cut.png")
    return n, repair_and_trim(f"hires/chars/{n}.png", f"hires/chars/{n}_cut.png", f"final/characters/{n}.png")
with ThreadPoolExecutor(4) as ex:
    for n, r in ex.map(run, PICKS.items()): print(n, "holes fixed/found", r)
