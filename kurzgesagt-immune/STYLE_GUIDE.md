# Style guide: There Is a War Inside You

## 1. Look
Microscope-cinematic. We are always *inside* living tissue: warm, deep crimson and magenta, with
out-of-focus cells (soft membrane rings) floating at several depths, fluid motes drifting, and a few blurred
cells passing right in front of the lens. The same premium pipeline as the stars video: procedural textures,
additive light, depth of field, motion blur (4 sub-frames), bloom, chromatic aberration, colour grade and grain.

## 2. Palette
| Role | Colour |
|---|---|
| Tissue (background) | deep crimson `#22061A` → `#5C122E` → highlights `#C83E5C` |
| KAI (hero) | red-orange `#FF6854`, navy bandana `#282C56`, gold receptor locks |
| Big eater (macrophage) | teal `#4E96B0`, bib cream with red dots |
| Bacteria | lime green `#96DC46` |
| Viruses | violet `#BE46DC` |
| Neutrophils | lilac-white `#ECCCFA` |
| Dendritic cells | lavender `#AA78FF` |
| Helper T / Killer T | blue `#50A0FF` / red-orange `#FF6050` |
| B cells, antibodies | gold `#EBB23E` / `#FFDC6E` |
| Alarm signals | warm yellow `#FFD25A` |
| Lymph node (chapter 3 base) | cool teal-blue, the one chapter that leaves the warm palette |

## 3. KAI (hero) and the face rig
KAI is a killer T cell: a round red-orange cell with a crown of receptor "locks" like spiky hair, a navy bandana with
flowing tails and a small scar. Cool, confident, a little smug.
- **Face rig (`rig.py`):** eyes, upper/lower lids, brows and mouth are continuous controls. Every expression is a pose
  of those controls, so changes are real animation: lids slide, brows travel, the mouth reshapes, with overshoot.
  Extra blinks fire at expression changes, and eyes dart (saccades) to targets.
- **Body acting:** squash and stretch, the receptor crown bristles when alert and droops when worried, the bandana
  tails flutter faster with excitement.
- **Everyone acts:** neutrophils, tissue cells, bacteria, T and B cells and the big eater all use the same rig, each
  with its own expression timeline.

## 3b. The big eater (macrophage)
A plump, pear-shaped teal cell with a polka-dot bib, stretchy arms that reach for food, a huge mouth, and swallowed
bacteria visibly dissolving inside in purple digestive bubbles.

## 4. Supporting cast
Bacteria (cheeky green rods with whipping flagella and toothy grins; terrified when caught), viruses (faceless,
spiky, coldly glowing), neutrophils (small, fierce, lobed nucleus; can burst into a glowing DNA net), dendritic cells
(lavender stars with waving tendrils; carry a glowing fragment of the enemy), helper T cells (blue, rank chevrons,
receptor "locks"), killer T cells (red-orange, bandana), B / plasma cells (gold; fire Y-shaped antibodies),
memory cells (wear a little glowing star), red blood cells (biconcave discs that stream past in vessels).

## 5. Typography
Montserrat ExtraBold, sparse and wide-tracked. On-screen labels name each new cell type the first time it appears.

## 6. Sound
Procedural pad and plucks, slightly bouncier (100–110 bpm) than the stars video; squelchy bubbles, pops and
chimes for the big eater; low rumbles for the breach; a riser into every big reveal.

## 7. Length
| Part | Chapter | Length |
|---|---|---|
| 1 | Hook | 0:27 |
| 2 | The walls | 0:36 |
| 3 | First responders | 0:54 |
| 4 | The messenger | 0:31 |
| 5 | Special forces | 0:51 |
| 6 | Memory | 0:39 |
| 7 | You're winning | 0:31 |
| | **Total** | **~4:28** |
