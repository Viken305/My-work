# Coffee Riso Icons

24 specialty-coffee icons in a two-ink risograph style: Fluorescent Pink (`#ff48b0`) and Blue (`#0078bf`), overprinted and slightly out of register.

Open `preview.html` in a browser to see the whole set. You can switch between the two versions and preview the icons at 48 px and 24 px.

## Versions

| Folder | What it contains | Use it for |
|---|---|---|
| `textured/` | Ink grain, halftone dots, misregistration, multiply blending | Websites, menus, print, hero graphics |
| `clean/` | Flat fills and clip paths only, with overlaps pre-mixed into solid colours | Figma, Illustrator and Sketch, app UI, small sizes |

The textured files rely on SVG filters and `mix-blend-mode`, so design tools may flatten or drop those effects. Use the clean files for editing.

Clean files keep each ink on its own named group (`tint`, `pink`, `blue`, `blue-over-tint`, `blue-over-pink`), so colours can be swapped per layer.

## Colours

| Role | Hex |
|---|---|
| Pink ink | `#ff48b0` |
| Blue ink | `#0078bf` |
| Pink halftone (clean) | `#ffb3dc` |
| Blue over pink | `#002284` |
| Blue over halftone | `#0054a5` |

## Icons

**Brewing:** 01 Pour-over, 02 French press, 03 Moka pot, 04 Gooseneck kettle, 05 Hand grinder, 06 Cold-brew jar
**Drinks:** 07 Espresso, 08 Latte, 09 Cappuccino, 10 Iced coffee, 11 Takeaway cup, 12 Mocha
**Beans & origin:** 13 Coffee bean, 14 Coffee cherry, 15 Roast bag, 16 Scoop of beans, 17 Origin pin, 18 Roast level
**Café life:** 19 Croissant, 20 Milk pitcher, 21 Portafilter, 22 Loyalty card, 23 Café front, 24 Pickup bell

## Grid

Every icon is drawn on a 200 × 200 grid. Blue linework is 4 px with round caps and joins, handles are 6–7 px, and detail lines are 2.5–3.5 px.

## Rebuilding

The geometry lives in `src/icons.mjs`. After editing it, run:

```sh
node src/build.mjs
```

This regenerates both folders and `preview.html`.

## Rebuilding the Dribbble shots

The shots are rendered from `dribbble/build-shots.mjs` with Playwright (Chromium). From this folder, run:

```sh
node src/build.mjs                                   # SVGs first; the shots use them
NODE_PATH=$(npm root -g) node dribbble/build-shots.mjs
```

This writes the 1600 × 1200 PNGs and @2x PNGs into `dribbble/`. To make the @2x JPEGs used for upload (Pillow required):

```sh
python3 -c "from PIL import Image; import glob, os
for f in glob.glob('dribbble/*@2x.png'):
    Image.open(f).convert('RGB').save(f[:-4] + '.jpg', quality=92, optimize=True); os.remove(f)"
```
