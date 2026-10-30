"""Contact sheet of stills: python3 sheet.py out.png a.png b.png ..."""
import sys
from PIL import Image
out, files = sys.argv[1], sys.argv[2:]
ims = [Image.open(f).resize((360, 640)) for f in files]
cols = min(5, len(ims))
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 370, rows * 650), (0, 0, 0))
for i, im in enumerate(ims):
    sheet.paste(im, ((i % cols) * 370, (i // cols) * 650))
sheet.save(out)
