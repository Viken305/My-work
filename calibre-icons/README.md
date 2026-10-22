# Calibre Icons

24 luxury watchmaking icons in polished chrome. Every line is a steel rod with a dark rim, a banded chrome body and a specular highlight, with heat-blued steel hands, ruby jewels and gold accents.

Open `preview.html` in a browser to see the whole set. You can switch between the two versions and preview the icons at 48 px and 24 px.

## Versions

| Folder | What it contains | Use it for |
|---|---|---|
| `chrome/` | Polished chrome, blued steel, ruby and gold, built from gradients | Dark or light grounds: boutiques, watch apps, product pages, hero graphics |
| `line/` | One flat colour (`currentColor`, black by default) at the same weights | Any background and any brand colour, engraving, print, app UI |

Both versions are plain vector: strokes, fills and gradients only, with no filters, so they open cleanly in Figma, Illustrator and Sketch.

## How the chrome is built

Each rod is drawn three times, in this order:

| Pass | Spec |
|---|---|
| Rim | Graphite `#0d1015`, the rod width plus 2.4 px |
| Body | A banded steel gradient at the rod width |
| Specular | White at 22 % of the rod width, 80 % opacity, nudged up and left |

Blued steel uses the same three passes with a blue gradient.

## Colours

| Role | Hex |
|---|---|
| Chrome bands | `#ffffff` `#e8edf2` `#c9d0d9` `#a3acb8` `#6b7584` `#4a5361` `#2a313b` |
| Blued steel | `#9cc1ff` `#4b7de6` `#3f6fd8` `#163587` `#12286a` |
| Ruby | `#ff9aa8` `#d4143a` `#5c0418` |
| Gold | `#fff1c9` `#e0b864` `#9d7330` |
| Graphite (suggested background) | `#0e0f12` |

## Icons

**Timepieces:** 01 Wristwatch, 02 Pocket watch, 03 Dive watch, 04 Carriage clock, 05 Hourglass, 06 Regulator clock
**Movement:** 07 Gear, 08 Escape wheel, 09 Balance wheel, 10 Mainspring, 11 Ruby jewel, 12 Winding crown
**Complications:** 13 Chronograph, 14 Moon phase, 15 Tourbillon, 16 Power reserve, 17 World time, 18 Alarm
**Atelier:** 19 Loupe, 20 Screwdriver, 21 Tweezers, 22 Watch box, 23 Buckle, 24 Case back

## Grid

Every icon is drawn on a 200 × 200 grid. Main rods are 6–9 px, secondary rods 3–5 px and fine details 1–2.4 px, all with round caps and joins. The chrome reads best at 48 px and up.

## Rebuilding

The geometry lives in `src/icons.mjs` and the chrome and line rendering in `src/render.mjs`. After editing either one, run:

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
