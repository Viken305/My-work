# Celadon Icons

24 tea-ceremony icons in glazed ceramic. Each piece is fired in its own glaze (celadon, tenmoku, shino, cobalt ruri, amber, iron or lacquer) over speckled raw clay, with drips where the glaze stops, a gloss highlight and a warm brown outline.

Open `preview.html` in a browser to see the whole set. You can switch between the two versions and preview the icons at 48 px and 24 px.

## Versions

| Folder | What it contains | Use it for |
|---|---|---|
| `glazed/` | Full colour: glaze gradients, speckled clay, drips and gloss | Tea brands, cafés, packaging, menus, editorial, app illustrations |
| `line/` | One colour (`currentColor`, black by default) with the same outlines, drips and brushwork | Any background and any brand colour, stamps, print, app UI |

Both versions are plain vector: paths, gradients and clip paths, with no filters, so they open cleanly in Figma, Illustrator and Sketch.

## Glazes

| Glaze | Highlight · body · pooled |
|---|---|
| Celadon 青磁 | `#e3f1e4` `#9fcbb1` `#4f8a72` |
| Tenmoku 天目 | `#a35a2c` `#4a2414` `#1a0b05` |
| Shino 志野 | `#fffaf0` `#efe2cc` `#cfb594` |
| Ruri 瑠璃 | `#8fb0ea` `#2f56a8` `#14295e` |
| Ame 飴釉 | `#ffd98a` `#e09a35` `#a35f12` |
| Matcha 抹茶 | `#c9e08a` `#8cb043` `#4f7020` |
| Tetsu 鉄釉 | `#6a6763` `#34312e` `#141210` |
| Urushi 漆 | `#4a3a36` `#1c1414` `#070505` |
| Clay | `#e6c9a3` → `#b88b60`, speckles `#5a3d26` |
| Outline | `#3a2a1f` |

The full palette, including the inner-glaze and accent shades, lives in `src/glazes.mjs`.

## Icons

**Ceremony:** 01 Matcha bowl, 02 Whisk, 03 Tea scoop, 04 Tea caddy, 05 Ladle, 06 Wagashi
**Teaware:** 07 Kyusu teapot, 08 Dobin teapot, 09 Yunomi cup, 10 Gaiwan, 11 Cooling pitcher, 12 Iron kettle
**Leaf:** 13 Tea leaf, 14 Tea sprig, 15 Tea field, 16 Tea tin, 17 Loose leaf, 18 Matcha powder
**Tea house:** 19 Tea house, 20 Paper lantern, 21 Ikebana, 22 Incense, 23 Folding fan, 24 Bonsai

## Grid

Every icon is drawn on a 200 × 200 grid. Outlines are 2.2–3 px and detail lines 1–2 px, with round caps and joins. Drips and speckles are seeded, so every rebuild comes out identical.

## Rebuilding

The geometry lives in `src/icons.mjs` and the colours in `src/glazes.mjs`. After editing either one, run:

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
