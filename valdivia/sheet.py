"""Contact sheet of a part's stills (for review):  python3 sheet.py part1"""
import glob, os, sys

from PIL import Image

d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", sys.argv[1], "stills")
ps = sorted(glob.glob(os.path.join(d, "t*.png")))
w, h = 360, 640
s = Image.new("RGB", (len(ps) * (w + 10) + 10, h + 20), (30, 30, 30))
for i, p in enumerate(ps):
    s.paste(Image.open(p).resize((w, h), Image.LANCZOS), (10 + i * (w + 10), 10))
s.save(os.path.join(d, "sheet.png"))
print(os.path.join(d, "sheet.png"))
