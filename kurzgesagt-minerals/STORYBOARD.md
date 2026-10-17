# How the Earth Makes Crystals: Storyboard

> The final narration lives in `script.py` (source of truth). Small wording changes from this plan were made while building.

A Kurzgesagt-style short explainer about how natural minerals form.

| | |
|---|---|
| **Runtime** | **3:38** as built (planned ~2:50; natural narration pace ran longer). 16:9, 1920×1080, 30 fps |
| **Narration** | ~430 words at a calm ~150 wpm |
| **Bonus cut** | 55 s vertical YouTube Short (9:16), cut from scenes 1, 3, 5, 8 |
| **Working title** | *How the Earth Makes Crystals* |
| **Alt titles** | *Every Crystal Has an Origin Story* · *The 4 Recipes for Making a Mineral* |

### Why ~2:50?
- The topic breaks cleanly into **4 "recipes"**: Fire, Water, Pressure, Life. Each needs about 25–30 s to land one idea and one "wow" fact.
- At under 60 s you'd only have room for one recipe, so a vertical Short works as a *teaser*, not the full story.
- 2–3 minutes keeps retention high for a new channel and is realistic to animate solo. Each scene reuses the same atom characters and backgrounds.

---

## Style Guide

### Palette
| Role | Colour | Hex |
|---|---|---|
| Background (deep space / deep earth) | Midnight navy | `#14163A` |
| Background alt | Deep purple | `#2A1E5C` |
| Rock / crust | Dusty violet | `#5B4B8A` |
| Magma / heat | Hot orange | `#FF7A3D` |
| Magma glow | Lava yellow | `#FFC94A` |
| Water | Cyan | `#3EC6E0` |
| Crystal highlight | Ice white-cyan | `#C9F4FF` |
| Life / biology | Mint green | `#5EE6A8` |
| Accent / key object | Hot pink | `#FF4F8B` |

Rules: dark background in every scene, **one** glowing accent per shot that pulls the eye, soft gradients plus long soft shadows, light film grain over everything.

### Characters
- **The Atoms**: round, flat circles with two dot eyes. Sodium = orange, Chlorine = green, Silicon = violet, Oxygen = red, Carbon = black with a white rim. They hold hands to form bonds. They're the recurring cast in every recipe.
- **The Bird** (narrator stand-in): a small round bird in a hard hat and geologist's vest. It appears at the start and end, reacting.
- **Magma Blob**: a lazy, glowing orange blob character that "relaxes" (cools) in Scene 3.

### Motion and sound rules
- Nothing is ever fully still. Idle float on every object (±4 px, 3 s sine loop) and drifting dust particles in every background.
- Ease-out-back on every pop-in (slight overshoot).
- Scene changes are **zoom-throughs**, not hard cuts (the camera flies into an object to get to the next world).
- Every pop has a soft "blip", every bond a "click", every transition a "whoosh". Ambient synth pad underneath that swells in Scene 8.

---

## Scenes

### SCENE 1: Hook (0:00–0:14)
**Narration**
> Right now, you are surrounded by crystals. The salt on your table. The screen of your phone. Even the bones inside your body. But nobody built them. The Earth did. So how?

**Visuals**
- Open on a cosy kitchen in the flat vector style. The camera pushes in on a salt shaker. Grains tumble out, and each grain is a perfect little cube that sparkles.
- Quick 3-panel split: salt cube → phone (a glowing quartz crystal inside it) → an X-ray arm with bones lit mint green.
- On "The Earth did," pull back fast out of the house, out of the city, to a spinning Earth on navy space.
- The Bird pops into the corner and tilts its head: "?"

**Sound:** quiet room tone → sparkle chimes → big whoosh on pull-back.
**Text on screen:** none. Let the visuals carry it.

---

### SCENE 2: What is a mineral? (0:14–0:34)
**Narration**
> A mineral is what happens when atoms stop wandering and start lining up. Sodium meets chlorine. They grab hands, then grab more hands, repeating the same pattern billions of times, until the pattern gets big enough to see. A crystal is just a pattern that never stopped.

**Visuals**
- Zoom INTO a salt grain. The camera falls into a navy void of floating, wandering Atom characters bumping around.
- One orange Sodium and one green Chlorine bump into each other and hold hands (*click*).
- More join. They snap into a 3D checkerboard grid that grows outward in a satisfying cascade.
- Pull out: the grid's outline *is* the cube shape of the salt grain.
- Small label pops up: **"> 6,000 known minerals"** with dozens of tiny crystal icons fanning out.

**Sound:** curious plucky marimba, a click on each bond, rising arpeggio as the grid grows.

---

### SCENE 3: Recipe 1, FIRE (0:34–1:02)
**Narration**
> Recipe one: fire. Deep underground, rock melts into magma, a soup of atoms moving far too fast to hold on to each other. But as magma cools, the atoms slow down and begin to link up. Cool it slowly, over thousands of years underground, and the crystals grow big, like the quartz and feldspar that make up most of the Earth's crust. Cool it in seconds, like lava hitting the ocean, and the atoms freeze before they can organise. You get glass.

**Visuals**
- Title card slides in: **RECIPE 1 · FIRE** 🔥 (orange icon).
- Cross-section of the crust (layered violet strata). A glowing magma chamber pulses. Zoom in: hyperactive Atom characters zipping around with motion streaks, sweating.
- **Magma Blob** character appears, then yawns and "relaxes" while its colour shifts from yellow → orange → dark red. The atoms slow and link hands.
- **Split screen**:
  - Left, "SLOW" (clock spinning with "10,000 years"): big, beautiful hexagonal quartz and pink feldspar crystals grow.
  - Right, "FAST" (stopwatch "3 seconds"): lava hits a wave with a hiss of steam, and the atoms freeze in a jumbled mess → shiny black obsidian.
- The Bird holds up a piece of obsidian, confused at the lack of crystal.

**Sound:** low rumbling bass for magma, sizzle on lava hitting water, glassy "tink" on obsidian.

---

### SCENE 4: Recipe 2, WATER (1:02–1:34)
**Narration**
> Recipe two: water. Water is brilliant at dissolving things, and at leaving them behind. When a salty lake dries up under the sun, the minerals have nowhere to go, and crystals of salt and gypsum appear. Underground, hot water carries dissolved minerals through cracks in the rock, cools, and drops them as veins of quartz… and sometimes gold. And in one cave in Mexico, mineral-rich water sat at just the right temperature for hundreds of thousands of years. The result? Crystals twelve metres long.

**Visuals**
- Title card: **RECIPE 2 · WATER** 💧 (cyan icon).
- A lake under a big flat sun. A time-lapse sun arc runs while the water level drops, and white crystal crust blooms at the edges into a vast salt flat (hexagonal tile pattern).
- Cut-through to underground: cyan hot-water streams snake through cracks in violet rock, carrying tiny glowing atom passengers. They "get off" at cooler spots, and white quartz veins draw themselves along the cracks with a golden glint.
- **Naica, Cave of Crystals:** the camera enters a dark cave. Lights flick on to reveal giant milky-white beams crisscrossing the frame. The Bird flies in and is *tiny* next to them. A scale bar pops up: **12 m** next to a stacked silhouette of 7 people.

**Sound:** gentle water trickle, bubbling, a reverberant "ahhh" choir pad when the cave lights up.

---

### SCENE 5: Recipe 3, PRESSURE (1:34–2:00)
**Narration**
> Recipe three: pressure. Some minerals are made by squeezing. About 150 kilometres down, the weight of the rock above is crushing, and plain carbon atoms are forced into the tightest arrangement possible. That's a diamond. Most of the diamonds we've found are billions of years old, and they only reached us because volcanic eruptions shot them up to the surface faster than they could turn back into graphite.

**Visuals**
- Title card: **RECIPE 3 · PRESSURE** ⬇️ (pink icon).
- The camera dives down a vertical cross-section with a depth meter ticking: 10 km… 50 km… 150 km. The rock layers get darker and redder.
- Black Carbon atoms are loosely stacked in flat sheets (graphite, like pencil lead). Giant downward arrows labelled **"PRESSURE"** squish them, and the atoms squeeze into a tight 3D diamond lattice. A sparkle flash in the accent pink.
- **"Kimberlite elevator":** a narrow pipe of magma rockets upward like an elevator with the diamond riding inside, flashing past the depth meter in reverse. It bursts out of the ground and the diamond lands on the Bird's head. The Bird is delighted.
- Brief garnet cameo: little red crystals forming in squished rock, labelled **"also: garnet"**.

**Sound:** deep creaking pressure groan, crystalline "shing" when the diamond forms, elevator "ding" on arrival.

---

### SCENE 6: Recipe 4, LIFE (2:00–2:28)
**Narration**
> Recipe four, and the most surprising: life. Over two billion years ago, tiny microbes in the ocean began breathing out oxygen. That oxygen reacted with rocks everywhere, and thousands of brand-new minerals appeared that had never existed before. Scientists think around two-thirds of Earth's minerals may only exist because of life. And life still makes them today: shells, coral, pearls… and the bones in your body.

**Visuals**
- Title card: **RECIPE 4 · LIFE** 🌱 (mint icon).
- An ancient ocean in teal. Tiny green microbe characters (cute blobs) puff out little red Oxygen atoms like bubbles.
- The oxygen drifts to the rocks. Iron-rich rocks rust red. Then a **cascade of new crystal icons** pops onto the screen, filling it in a grid of dozens and dozens of colourful shapes.
- Counter animates: **"Minerals on Earth"** ticking upward, and a pie chart overlay highlights **~2/3 linked to life** in mint.
- Montage: seashell → coral reef → pearl in an oyster → back to the mint X-ray arm from Scene 1 (a callback).

**Sound:** bubbly playful synth, cascading chime run as the mineral icons explode onto screen.

---

### SCENE 7: Zoom out, deep time (2:28–2:42)
**Narration**
> The oldest piece of Earth we've ever found is a mineral: a tiny zircon crystal from Australia, 4.4 billion years old. It formed when Earth was only about 150 million years old. Before life. Before almost everything.

*(Fact-check fix: the original line said "before the oceans", but that zircon is itself evidence of liquid water 4.4 billion years ago.)*

**Visuals**
- A single tiny pink zircon grain glows alone on a black background. The camera pulls back slowly: Jack Hills, Australia → a young, molten, cratered Earth → a timeline bar stretching left across the screen, with "now" as a tiny dot at the far right.
- The music thins out to one sustained note.

**Sound:** music drops to near silence, a single soft piano note.

---

### SCENE 8: Outro, optimistic ending (2:42–2:52)
**Narration**
> Fire, water, pressure and life, slowly arranging atoms into something beautiful. The Earth has been making crystals for billions of years. And now, for a little while, you get to look at them.

**Visuals**
- A quick 4-panel recap with the recipe icons: 🔥 💧 ⬇️ 🌱. They merge into one glowing crystal that slowly rotates.
- The crystal reflects into the Bird's eye. The Bird is sitting on a rock under a starry sky, looking at a geode it just cracked open.
- Fade to end card: channel logo, "Sources in description", and two video thumbnails.

**Sound:** full swell of the ambient pad, then soft fade.

---

## Shot / timing summary

| # | Scene | Time | Duration | Key "wow" |
|---|---|---|---|---|
| 1 | Hook | 0:00 | 14 s | You are surrounded by crystals |
| 2 | What is a mineral | 0:14 | 20 s | Crystal = pattern that never stopped |
| 3 | Fire | 0:34 | 28 s | Slow = crystals, fast = glass |
| 4 | Water | 1:02 | 32 s | 12 m Naica crystals |
| 5 | Pressure | 1:34 | 26 s | Diamond elevator |
| 6 | Life | 2:00 | 28 s | ~2/3 of minerals need life |
| 7 | Deep time | 2:28 | 14 s | 4.4-billion-year-old zircon |
| 8 | Outro | 2:42 | ~10 s | Optimistic close |

## 55 s YouTube Short cut (9:16)
1. **0–8 s:** Scene 1 hook (salt → phone → bones), reframed vertically.
2. **8–20 s:** Scene 3, slow vs fast stacked top/bottom instead of side by side.
3. **20–38 s:** Scene 5, the diamond dive (a vertical depth dive fits 9:16 perfectly).
4. **38–50 s:** Scene 4, the Naica cave reveal.
5. **50–55 s:** "There are 4 recipes. Full video on the channel →"

## Thumbnail concept
The Bird, tiny, standing in the Naica cave between giant glowing white crystals on a navy background. Big text: **"EARTH IS A CRYSTAL FACTORY"**.

## Fact sources (for the description)
- Mineral definition and count: International Mineralogical Association (IMA) list of minerals (> 6,000 species).
- Mineral evolution and the oxygen link: Hazen, R. M. et al., *Mineral evolution*, American Mineralogist (2008), and later work by Hazen on biologically mediated minerals.
- Naica crystals: García-Ruiz, J. M. et al., *Formation of natural gypsum megacrystals in Naica, Mexico*, Geology (2007).
- Diamond formation depth and age: Shirey, S. B. & Shigley, J. E., *Recent advances in understanding the geology of diamonds*, Gems & Gemology (2013).
- Oldest zircon: Wilde, S. A. et al., *Evidence from detrital zircons for the existence of continental crust and oceans on the Earth 4.4 Gyr ago*, Nature (2001).
