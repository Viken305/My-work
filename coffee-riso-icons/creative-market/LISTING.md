# Creative Market listing: Coffee Riso Icons

Everything to paste into **creativemarket.com/account/products/new**, field by field.

## Files

| Field | What to use |
|---|---|
| Product file | `coffee-riso-icons-creative-market.zip` (the buyer download, about 12 MB) |
| Preview images, in this order | `previews/01-cover.jpg` (the thumbnail), `02-full-set.jpg`, `03-print-detail.jpg`, `04-textured-vs-clean.jpg`, `05-in-use.jpg` |

The previews are 2340 × 1560 (3:2) JPEGs. If the form asks for a different size, the build script can re-render them (see "Rebuilding" below).

## Category

Graphics → Icons

## Title

Coffee Riso Icons: 24 Risograph SVG Icons

## Short description (one line)

24 two-ink risograph coffee icons in textured and clean SVG, plus transparent PNGs.

## Description

Bring the warmth of a real print shop to your café brand. Coffee Riso is a set of 24 specialty-coffee icons printed the risograph way, in two inks: Fluorescent Pink and Blue. Where the inks overlap they mix into a deep indigo, a halftone gives a lighter pink, and the pink layer sits slightly off register, just like a real print run.

**What's included**

- 24 icons in 4 categories: Brewing, Drinks, Beans & origin, Café life
- **Textured SVG**: ink grain, halftone dots and misregistration built into the vector. Ideal for websites, menus, posters and packaging
- **Clean SVG**: flat colours with pre-mixed overlaps, each ink on its own named layer. Ready for Figma, Illustrator, Sketch, Affinity Designer and Inkscape
- **Transparent PNGs** of both versions at 512 px and 1024 px
- A preview page to browse the whole set
- 200 × 200 grid with 4 px round linework, consistent across every icon

**Icons**

Brewing: pour-over, French press, moka pot, gooseneck kettle, hand grinder, cold-brew jar
Drinks: espresso, latte, cappuccino, iced coffee, takeaway cup, mocha
Beans & origin: coffee bean, coffee cherry, roast bag, scoop of beans, origin pin, roast level
Café life: croissant, milk pitcher, portafilter, loyalty card, café front, pickup bell

**Perfect for** café and roaster branding, menus and chalkboards, coffee apps and websites, packaging, loyalty cards and social posts.

**Good to know:** the textured effect is made with SVG filters, which browsers display perfectly. Some design apps flatten filters, so use the Clean SVGs or the PNGs when editing in Figma or Illustrator.

## Tags

coffee, icons, risograph, riso, cafe, coffee shop, icon set, svg icons, barista, latte, espresso, menu, halftone, print, two color, retro, branding, packaging, food and drink, roaster

Creative Market may cap the number of tags. If it does, keep the first ones; they're in priority order.

## Compatible apps

Adobe Illustrator, Figma, Sketch, Affinity Designer, Inkscape (plus any browser for the textured SVGs)

## File types

SVG, PNG

## Price

Suggested **$14** for the standard license. Premium icon sets of about two dozen icons usually sit between $12 and $19. Pick the price that fits your shop.

## Before you publish

- Check the license options on the form. The buyer README tells customers that their Creative Market license covers their use.
- "Overprint Coffee" in the in-use preview is a made-up café name.

## Rebuilding

From `coffee-riso-icons/`:

```sh
node src/build.mjs
NODE_PATH=$(npm root -g) node dribbble/build-shots.mjs
NODE_PATH=$(npm root -g) node creative-market/build-pack.mjs
```

Then convert `creative-market/previews/*.png` to JPEG (quality 92) and zip `creative-market/.build/product/Coffee-Riso-Icons` as the product file.
