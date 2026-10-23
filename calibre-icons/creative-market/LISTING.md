# Creative Market listing: Calibre Icons

Everything to paste into **creativemarket.com/account/products/new**, field by field.

## Files

| Field | What to use |
|---|---|
| Product file | `calibre-icons-creative-market.zip` (the buyer download) |
| Preview images, in this order | `previews/01-cover.jpg` (the thumbnail), `02-parts-tray.jpg`, `03-the-finish.jpg`, `04-editions.jpg`, `05-in-use.jpg` |

The previews are 2340 × 1560 (3:2) JPEGs. If the form asks for a different size, the build script can re-render them (see "Rebuilding" below).

## Category

Graphics → Icons

## Title

Calibre: 24 Chrome Watchmaking Icons

## Short description (one line)

24 polished-chrome watch and horology icons with blued steel and ruby, in chrome and line SVG plus transparent PNGs.

## Description

Haute horlogerie, in icon form. Every line in Calibre is a polished steel rod with a graphite rim, a banded chrome body and a specular highlight, finished with heat-blued hands, ruby jewels and touches of gold. It's built for watch brands, boutiques and collector apps that need icons as refined as the watches themselves.

**What's included**

- 24 icons in 4 groups: Timepieces, Movement, Complications, Atelier
- **Chrome SVG**: polished steel, blued steel, ruby and gold, built from gradients. Looks richest on graphite or black, and works on light grounds too
- **Line SVG**: one colour (currentColor) at the same weights, recolourable for any dial or brand
- **Transparent PNGs** of both versions at 512 px and 1024 px
- A preview page to browse the whole set
- Pure vector with no filters, so it opens cleanly in Figma, Illustrator, Sketch, Affinity Designer and Inkscape

**Icons**

Timepieces: wristwatch, pocket watch, dive watch, carriage clock, hourglass, regulator clock
Movement: gear, escape wheel, balance wheel, mainspring, ruby jewel, winding crown
Complications: chronograph, moon phase, tourbillon, power reserve, world time, alarm
Atelier: loupe, screwdriver, tweezers, watch box, buckle, case back

**Perfect for** watch brands and retailers, boutique and e-commerce sites, collector and service apps, warranty cards, packaging and editorial.

## Tags

watch, icons, watchmaking, horology, chrome, luxury, icon set, svg icons, tourbillon, clock, time, metal, steel, premium, jewelry, 3d icons, skeuomorphic, ui icons, branding, figma

Creative Market may cap the number of tags. If it does, keep the first ones; they're in priority order.

## Compatible apps

Adobe Illustrator, Figma, Sketch, Affinity Designer, Inkscape

## File types

SVG, PNG

## Price

Suggested **$19** for the standard license. The chrome rendering, the accents and the niche put it at the top of the usual $12–$19 range for a set of about two dozen icons. Pick the price that fits your shop.

## Before you publish

- Check the license options on the form. The buyer README tells customers that their Creative Market license covers their use.
- "Calibre" and the reference numbers in the in-use preview are made-up mockup branding.

## Rebuilding

From `calibre-icons/`:

```sh
node src/build.mjs
NODE_PATH=$(npm root -g) node dribbble/build-shots.mjs
NODE_PATH=$(npm root -g) node creative-market/build-pack.mjs
```

Then zip `creative-market/.build/product/Calibre-Icons` as the product file.
