import sys; sys.path.insert(0, "src")
from recraft import generate, download
P = ("Whimsical storybook Christmas illustration of a baby fawn wearing a large burgundy velvet bow "
     "around its neck, hand-painted gouache texture, soft fuzzy fur, gentle blush cheeks, calm small eyes, "
     "vintage children's book style, palette of burgundy, cranberry, antique gold, cream, sage and cocoa brown, "
     "single isolated character centered on a plain pure white background, no text, no frame")
for m in ["recraftv4_1_flash", "recraftv4_1"]:
    urls, cr = generate(P, model=m)
    download(urls[0], f"raw/compare_{m}.png"); print(m, "credits", cr)
