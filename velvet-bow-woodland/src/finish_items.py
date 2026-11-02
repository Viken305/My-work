import sys, os; sys.path.insert(0, "src")
from concurrent.futures import ThreadPoolExecutor
from recraft import crisp_upscale, remove_background, download
from finish import repair_and_trim
from PIL import Image
PICKS = {
 "bows": dict(b01_velvet_classic="b", b02_velvet_longtails="a", b03_satin_cranberry="a", b04_tartan="b", b05_gingham="b",
   b06_lace="b", b07_double_loop="a", b08_sage_velvet="b", b09_gold_satin="b", b10_bow_bell="a", b11_ribbon_wave="a", b12_ribbon_tartan_curl="a"),
 "props": dict(p01_gift="b", p02_gift_stack="b", p03_ornament_burgundy="a", p04_ornament_gold="b", p05_candles="b", p06_cocoa="b",
   p07_teacup="a", p08_stocking="a", p09_sled="b", p10_lantern="a", p11_gingerbread="b", p12_candycanes="a", p13_books="b",
   p14_pinecones="b", p15_sleighbells="a", p16_nutcracker="b", p17_tree_pot="b", p18_snowglobe="b", p19_mittens="a", p20_skates="b"),
 "botanicals": dict(f01_holly="b", f02_mistletoe="b", f03_pine="a", f04_berry_branch="a", f05_dried_orange="b", f06_christmas_rose="a",
   f07_cedar="a", f08_eucalyptus="b", f09_pine_bouquet="a", f10_poinsettia="b", f11_cotton="a", f12_winter_bouquet="a"),
 "frames": dict(w01_wreath_fawn="b", w02_wreath_bunny="a", w03_oval_frame="b", w04_garland_swag="b"),
 "phrases": dict(t01_merry_bright="b", t02_oh_deer="a", t03_joy="a", t04_seasons_greetings="a", t05_noel="a", t06_warm_wishes="b"),
}
SCENES = dict(s01_snowy_forest="a", s02_fireside="a", s03_village="a", s04_tree_gathering="b")
DEEP = {"f03_pine", "f07_cedar", "f09_pine_bouquet", "w04_garland_swag"}
CENTER = {"w01_wreath_fawn", "w02_wreath_bunny", "w03_oval_frame"}
jobs = [(g, n, s) for g, d in PICKS.items() for n, s in d.items()]
def run(j):
    g, n, s = j
    os.makedirs(f"hires/{g}", exist_ok=True); os.makedirs(f"final/{g}", exist_ok=True)
    if not os.path.exists(f"hires/{g}/{n}_cut.png"):
        u, _ = crisp_upscale(f"raw/{g}/{n}_{s}.png"); download(u, f"hires/{g}/{n}.png")
        u, _ = remove_background(f"hires/{g}/{n}.png"); download(u, f"hires/{g}/{n}_cut.png")
    repair_and_trim(f"hires/{g}/{n}.png", f"hires/{g}/{n}_cut.png", f"final/{g}/{n}.png",
                    white_reach=None if n in DEEP else 6, clear_center=n in CENTER)
    return n
def scene(kv):
    n, s = kv
    os.makedirs("final/scenes", exist_ok=True)
    if not os.path.exists(f"hires/{n}.png"):
        u, _ = crisp_upscale(f"raw/scenes/{n}_{s}.png"); download(u, f"hires/{n}.png")
    Image.open(f"hires/{n}.png").convert("RGB").save(f"final/scenes/{n}.jpg", quality=95, dpi=(300, 300))
    return n
with ThreadPoolExecutor(5) as ex:
    done = list(ex.map(run, jobs)) + list(ex.map(scene, SCENES.items()))
print("done", len(done))
