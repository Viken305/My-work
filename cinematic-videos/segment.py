import glob, os, numpy as np
from PIL import Image
from rembg import new_session, remove
s = new_session("isnet-general-use")
for f in sorted(glob.glob("source/*")):
    n = os.path.splitext(os.path.basename(f))[0]
    im = Image.open(f).convert("RGB"); W, H = im.size
    sm = im.copy(); sm.thumbnail((1600, 1600))
    m = remove(sm, session=s, only_mask=True).resize((W, H), Image.LANCZOS)
    m.save(f"build/{n}_mask.png")
    sm.thumbnail((400, 400)); mm = m.copy(); mm.thumbnail((400, 400))
    chk = Image.new("RGB", sm.size, (200, 30, 90)); chk.paste(sm, mask=mm)
    chk.save(f"build/{n}_chk.png"); print(n, flush=True)
