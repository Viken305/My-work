# Maison Icons

24 Art Deco fine-dining icons. Every outline is drawn as a hollow inline rail, the double gold line of 1920s menus, posters and hotel lobbies, set off with sunburst fans and solid gold accents.

Open `preview.html` in a browser to see the whole set. You can switch between the two versions and preview the icons at 48 px and 24 px.

## Versions

| Folder | What it contains | Use it for |
|---|---|---|
| `gold/` | A champagne-gold gradient on every mark | Dark grounds: emerald, black lacquer, oxblood. Menus, packaging, signage, hero graphics |
| `mono/` | One flat colour (`currentColor`, black by default) | Any background and any brand colour, foil-stamp and print artwork, app UI |

The hollow core is a real mask, not a painted line, so it stays transparent on any background. Each file keeps its marks in three named groups (`solid`, `rule`, `inline`). The files use only paths, a gradient, clip paths and one mask: no filters, so they open cleanly in Figma, Illustrator and Sketch.

## Anatomy

| Mark | Spec |
|---|---|
| Inline rail | 9 px stroke with a 3 px open core (3 · 3 · 3), round caps and joins |
| Rule | 2 px (1.6 px for fine detail) |
| Solid | Filled gold: fans, flames, gems, stepped bases |

## Colours

| Role | Hex |
|---|---|
| Gold, light to dark | `#fbf0c9` `#f7e9bd` `#e9c879` `#d6aa4e` `#b5852f` |
| Emerald (suggested background) | `#0d2a22` |
| Black lacquer | `#0c0c0d` |
| Oxblood | `#4a1418` |
| Ivory | `#f2ece0` |

## Icons

**Service:** 01 Cloche, 02 Place setting, 03 Reserved, 04 Menu, 05 Candelabra, 06 Award
**Cellar:** 07 Wine glass, 08 Champagne coupe, 09 Decanter, 10 Martini, 11 Cocktail shaker, 12 Ice bucket
**Delicacies:** 13 Oyster, 14 Caviar, 15 Grapes, 16 Fish course, 17 Fruit tart, 18 Cheese
**Kitchen:** 19 Chef's toque, 20 Chef's knife, 21 Whisk, 22 Saucepan, 23 Gâteau, 24 Pepper mill

## Grid

Every icon is drawn on a 200 × 200 grid. The inline rails need some size to read as double lines: they look best at 40 px and up, and at 24 px they read as a single bold line.

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
