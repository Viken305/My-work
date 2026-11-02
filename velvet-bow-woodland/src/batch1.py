import sys, json; sys.path.insert(0, "src")
from recraft import generate_with_ref, download
STYLE = ("whimsical storybook Christmas illustration, hand-painted gouache texture, soft fuzzy fur, gentle blush cheeks, "
         "calm small eyes, vintage children's book style, palette of burgundy, cranberry, antique gold, cream, sage and cocoa brown, "
         "single isolated character centered on a plain pure white background, no text, no frame, no shadow on ground")
ITEMS = {
 "02_fox":  "A little red fox sitting with its fluffy tail curled around its paws, wearing a cranberry satin bow with antique gold trim tied at its neck",
 "03_bunny":"A cream-and-cocoa baby bunny standing upright holding a small wrapped gift, a large burgundy velvet bow tied between its long ears",
 "04_bear": "A cocoa brown bear cub sitting and hugging a sprig of holly, wearing a sage green and burgundy tartan bow at its neck",
 "05_mouse":"A tiny grey-brown field mouse standing beside a lit cream candle, wearing a long burgundy velvet ribbon bow with flowing tails",
}
log = {}
for name, desc in ITEMS.items():
    urls, cr, sid = generate_with_ref(f"{desc}. {STYLE}", ["raw/compare_recraftv4_1.png"], n=2)
    for i, u in enumerate(urls): download(u, f"raw/{name}_{chr(97+i)}.png")
    log[name] = {"credits": cr, "style_id": sid}; print(name, cr, sid)
json.dump(log, open("raw/batch1_log.json", "w"), indent=1)
