"""Generate the 16 character options with V4.1 Flash (2 options each)."""
import sys, json; sys.path.insert(0, "src")
from concurrent.futures import ThreadPoolExecutor
from recraft import generate, download

STYLE = ("Whimsical vintage storybook Christmas illustration, hand-painted gouache texture with visible brushstrokes, "
         "soft fuzzy fur, gentle pink blush cheeks, calm small dark eyes, elegant classic children's book style, "
         "muted palette of burgundy, cranberry, antique gold, cream, sage green and cocoa brown, velvet bows with thin antique gold edging. "
         "Single isolated character, full body, centered on a plain pure white background, no text, no frame, no ground shadow")

CHARS = {
 "c01_fawn":       "A baby fawn with white spots lying down with legs tucked, head turned, wearing a large burgundy velvet bow at its neck",
 "c02_fawn_stand": "A baby fawn with white spots standing on slender legs, looking back over its shoulder, a burgundy velvet bow with long ribbon tails at its neck",
 "c03_fox":        "A little fox with warm russet orange fur and a cream chest, sitting with its fluffy white-tipped tail curled around its paws, wearing a burgundy velvet bow at its neck",
 "c04_fox_walk":   "A little fox with warm russet orange fur walking, carrying a small wrapped gift with a burgundy bow in its mouth, a sage green knitted scarf",
 "c05_bunny":      "A cream and cocoa baby bunny standing upright holding a small burgundy wrapped gift with gold ribbon, a large burgundy velvet bow tied between its long ears",
 "c06_bunny_sit":  "A cream baby bunny sitting with its paws together, eyes gently closed, a cranberry satin bow tied on one ear",
 "c07_bear":       "A cocoa brown bear cub sitting and hugging a sprig of holly with red berries, wearing a burgundy and sage tartan bow at its neck",
 "c08_bear_stand": "A cocoa brown bear cub standing upright holding a lit brass lantern, wearing a burgundy velvet bow and a tiny cream knitted hat",
 "c09_mouse":      "A tiny grey-brown field mouse standing beside a tall lit cream candle, wearing a long burgundy velvet ribbon bow with flowing tails",
 "c10_owl":        "A small fluffy tawny owl perched on a short pine branch, wearing a little burgundy velvet bow at its chest",
 "c11_hedgehog":   "A round little hedgehog with soft brown spines, carrying a red apple on its back, wearing a cranberry satin bow",
 "c12_squirrel":   "A red squirrel sitting upright holding a golden acorn, its bushy tail raised, wearing a burgundy velvet bow at its neck",
 "c13_polarbear":  "A fluffy white polar bear cub sitting, wearing a burgundy velvet bow and a cream knitted scarf with sage stripes",
 "c14_lamb":       "A fluffy cream lamb with curly wool standing, wearing a burgundy velvet bow with a tiny gold bell at its neck",
 "c15_raccoon":    "A small raccoon with a striped tail sitting and holding a steaming cup of cocoa, wearing a sage green and burgundy tartan bow",
 "c16_badger":     "A cute badger with black and white face stripes standing upright holding a small wrapped gift, wearing a burgundy velvet bow",
}

def run(item):
    name, desc = item
    urls, cr = generate(f"{desc}. {STYLE}", model="recraftv4_1_flash", size="1:1", n=2)
    for i, u in enumerate(urls): download(u, f"raw/chars/{name}_{'ab'[i]}.png")
    return name, cr

with ThreadPoolExecutor(4) as ex:
    total = 0
    for name, cr in ex.map(run, CHARS.items()):
        total += cr or 0; print(name, cr)
print("total credits", total)
