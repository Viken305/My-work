# Gilt Almanac Icons

24 celestial and zodiac icons engraved like the plates of an old star atlas. Fine parallel hatching does the shading, and the lines are printed in gold foil.

Open `preview.html` in a browser to see the whole set. You can switch between the two versions and preview the icons at 48 px and 24 px.

## Versions

| Folder | What it contains | Use it for |
|---|---|---|
| `gilt/` | A gold-foil gradient on every line | Dark backgrounds: packaging, candle and tarot labels, hero graphics, social posts |
| `ink/` | One flat colour (`currentColor`, black by default) | Any background, any brand colour, foil-stamp and letterpress artwork, app UI |

Both versions are plain vector: strokes, clip paths and masks, with no filters or blend modes, so they open cleanly in Figma, Illustrator and Sketch. To recolour the ink version in code, set the CSS `color` on the parent.

## Zodiac coins

Each sign sits on an engraved coin. The hatching in the field follows the sign's element:

| Element | Signs | Hatching |
|---|---|---|
| Fire | Aries, Leo, Sagittarius | 45° diagonal |
| Earth | Taurus, Virgo, Capricorn | Horizontal |
| Air | Gemini, Libra, Aquarius | 135° diagonal |
| Water | Cancer, Scorpio, Pisces | Vertical |

## Colours

| Role | Hex |
|---|---|
| Gold, light to dark | `#fbe8b4` `#f1d58b` `#e2b85c` `#b98b3d` `#a37632` |
| Night (suggested background) | `#0f1526` |
| Paper (suggested background) | `#f3ede1` |

## Icons

**Zodiac:** 01 Aries, 02 Taurus, 03 Gemini, 04 Cancer, 05 Leo, 06 Virgo, 07 Libra, 08 Scorpio, 09 Sagittarius, 10 Capricorn, 11 Aquarius, 12 Pisces
**Celestial:** 13 Sun, 14 Crescent moon, 15 Full moon, 16 Eclipse, 17 Saturn, 18 Comet, 19 North star, 20 Constellation, 21 Telescope, 22 Astrolabe, 23 Armillary sphere, 24 Crystal ball

## Grid

Every icon is drawn on a 200 × 200 grid. Outlines are 3 px with round caps and joins, secondary rules are 1.2–2 px, and engraving lines are 0.9–1.2 px. The hatching looks best at 40 px and up; below that it blends into a soft tone.

## Rebuilding

The geometry lives in `src/icons.mjs`, and the hatching and mask helpers live in `src/lib.mjs`. After editing either one, run:

```sh
node src/build.mjs
```

This regenerates both folders and `preview.html`.
