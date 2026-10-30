"""Contact sheet of a part's stills:  python3 sheet.py part2  -> build/part2/sheet.png"""
import glob, os, sys

from PIL import Image

part = sys.argv[1]
fs = sorted(glob.glob(f"build/{part}/stills/*.png"))[-int(sys.argv[2]) if len(sys.argv) > 2 else 0:]
ims = [Image.open(f).resize((540, 960)) for f in fs]
s = Image.new("RGB", (540 * len(ims), 960))
for i, im in enumerate(ims):
    s.paste(im, (i * 540, 0))
s.save(f"build/{part}/sheet.png")
print(f"build/{part}/sheet.png")
