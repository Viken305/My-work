import sys, glob, os
from PIL import Image, ImageDraw
g, out = sys.argv[1], sys.argv[2]; S = int(sys.argv[3]) if len(sys.argv) > 3 else 300
names = sorted({os.path.basename(f)[:-6] for f in glob.glob(f"raw/{g}/*_a.png")})
cols = 6; rows = (len(names) + cols - 1) // cols
c = Image.new("RGB", (cols * 2 * S // 1, rows * S), "white")
c = Image.new("RGB", (cols * S, rows * 2 * S), "white"); d = ImageDraw.Draw(c)
for k, n in enumerate(names):
    for j, s in enumerate("ab"):
        x, y = (k % cols) * S, (k // cols) * 2 * S + j * S
        im = Image.open(f"raw/{g}/{n}_{s}.png").convert("RGB"); im.thumbnail((S, S)); c.paste(im, (x, y))
        d.rectangle([x, y, x + S - 1, y + S - 1], outline=(200, 200, 200)); d.text((x + 4, y + 4), f"{n[:3]}{s}", fill="black")
c.save(out, quality=82)
