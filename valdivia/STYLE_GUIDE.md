# The Day the Earth Rang Like a Bell: style guide

A 9:16 Short (**~2:35**) about the 1960 Valdivia earthquake in Chile, rendered entirely in code for @BrighterMinds.
Style frames: `python3 frames.py` writes `out/style/frame_*.png` and the contact sheet `out/style/style_frames.png`.

This style is new. It is not the dark cyanotype of `krakatoa/` or the graphite noir of `deep-hole/`. This one is
**"Seismogram"**: the whole film lives on the paper of a seismograph drum. Bone-white paper, black ink, a
millimetre grid, cut-paper layers with real shadows. The hero is **the trace**, the line the pen draws. It shakes
the captions, cracks the words, becomes a coastline, a wave front, and in the end the slow swing of the whole planet.

Going light is deliberate. Krakatoa was dark, and most science Shorts are dark, so a warm paper frame stands out in
the feed. It also lets the one red (the quake) hit as hard as a flash does on black.

## 1. Big idea
- **Everything is a recording.** Each scene is a plate in an instrument report (`FIG. 3 · SEISMOGRAM · 2 MIN A LINE`).
  Numbers live on instruments: a clock, a stopwatch, isochrons, a strain meter, an energy chart.
- **The pen drives the film.** One seismogram signal (`ink.trace`) is the master clock for motion. Its envelope
  drives camera shake, caption jitter, line wobble and the sound mix. When the pen is calm, everything is calm.
- **Calm, then violent, then a slow ring.** Part 1 opens on the quiet, slow ringing. Part 2 is still and tense
  (stuck plates). The rupture is the only moment the whole frame breaks. Part 5 brings back the slow ringing as the
  emotional peak.

## 2. Palette
| Role | Colour | Hex |
|---|---|---|
| Paper (drum) | Bone | `#EEE7D8` |
| Paper in shadow, land | Shade | `#DBD1BD` |
| Grid, secondary labels | Sepia | `#AC9E84` |
| All linework and text | Ink | `#18171B` |
| **The quake**: rupture, energy, shaking | Seismic red | `#DE3426` |
| **Water**: sea, tsunami | Pacific teal | `#126880` |
| **The ringing planet** (parts 1 and 5 only) | Bell bronze | `#BE8A34` |

Rules:
- Ink and paper do 85% of the work. At most two accents per frame.
- Red means **the ground moving**, teal means **water**, bronze means **the planet ringing**. They never swap.
- Red never appears as a fill bigger than the FIG 4 square, so it stays loud.

## 3. Texture and rendering (`ink.py`)
- **Drum paper:** warm fibre noise, vertical paper streaks, a 12 px / 60 px seismograph grid, and drum curvature
  (the paper darkens slightly toward the top and bottom of the frame).
- **Ink:** every line has a soft bleed under a crisp core. Glyphs "soak in" (blur → sharp) as they appear.
- **Cut paper:** sections (plates, mantle, hills, volcano plume, energy squares) are separate paper layers with a
  contact shadow plus a long soft shadow. During camera moves the layers parallax at different speeds (depth 0–3).
- **Engraving:** land gets fine 45° hatching. Oceans get teal "water lines" that follow the coast (distance
  transform), like an old chart.
- **Globe:** exact land outline from an inverse orthographic projection of a 1/12° land raster (`globe_land_path`),
  so the globe can spin freely without seams.
- **Post:** grain multiplied into the paper, a warm vignette, a hint of lens fringing, red-only bloom, camera shake
  driven by the trace envelope, and 3-sample motion blur.

## 4. Typography
- **Captions:** *Inter Display* Bold, ink.
- **Emphasis words:** *Noto Serif Display* Bold Italic in the accent colour of what they mean (`go` red, `kept going`
  teal, `rang` bronze) with a hand-inked wavy underline that draws in.
- **Instrument labels:** *Noto Sans Mono*, tracked caps, on paper tabs with a red rule (`FIG. 2 · CHILE, IN SECTION`).
- **Title:** *Noto Serif Display* roman caps `THE DAY THE EARTH`, then a huge bronze italic **RANG** with ringing echo
  outlines, then `like a bell` in italic.

## 5. Captions that interact with the graphics
This is the signature of the video. The base system is the same everywhere:
1. **Word-by-word, timed to the real voice** (pause-matching aligner from `krakatoa/timing.py`).
2. **Ink-in:** each letter starts as a soft ink spread and sharpens in about 6 frames, settling with a small spring.
3. **The trace shakes them:** letter jitter = trace envelope × (1.6 px on the active word, 0.7 px on the rest), with
   tiny rotations. Calm narration means rock-steady text. During the rupture the words rattle.
4. **Layout:** max 3 words per phrase, centred at y ≈ 1390–1470, never below y = 1480, nothing in the top ~220 px or
   the right ~150 px between y 900–1520 (Shorts UI).
5. **Exit:** the drum scrolls the words up and off, like paper feeding past the pen.

On top of that, **seven special moments** where the words become part of the drawing:

| Moment | Caption behaviour | Frame |
|---|---|---|
| "the whole Earth **rang**" | `rang` rings: outline copies pulse out of the word at the 54-min mode's rhythm (sped up), in sync with the globe's deformed outlines | FIG 1 |
| "it let **go**" | The fault line from the section slices through the caption, and the top half of the words **slips** 26 px along it, with a crack sound | FIG 2 |
| "about **10 minutes**" | The words shake with the live trace. A stopwatch card above counts 00:00 → ~10:00 as the pen runs | FIG 3 |
| "**thousands** of times more" | The caption is pinned to the energy counter: `≈5,800×` counts up as the squares grow from the Haiti dot to the 9.5 square | FIG 4 |
| "across the entire Pacific" | The words **ride the tsunami front**. Each letter sits on the wave line, rotated to its tangent, and travels with it | FIG 5 |
| "the ground **sank**" | `sank` drops letter by letter below a waterline drawn through the caption. Below the line it turns teal and ripples | FIG 6 |
| Title | **RANG** strikes like a bell: the echo outlines expand once, and the seismogram under the title is drawn by the pen | FIG 7 |

## 6. Motion language ("10-year studio" rules)
- **No linear moves.** Moves in use `out_expo` (fast start, long settle). Moves out use `in_cubic`. Things that land
  overshoot slightly (`spring(k=8, w=11)`).
- **Overlap everything.** Nothing starts at the same frame. Letters step 0.025 s apart, labels 4 frames after their
  line, and cut-paper layers 2–3 frames apart by depth.
- **One camera, no hard cuts** except the rupture and the title. Transitions are match-moves:
  globe → zoom to Chile → the coastline becomes the section's sea floor → the locked fault becomes the pen line →
  the helicorder → the trace's peaks become the energy squares → the 9.5 square folds into the Pacific chart →
  the tsunami front wraps around the globe (FIG 1 callback) → the globe's ring becomes the waterline of the forest.
- **Lines draw themselves.** Coastlines, traces, fronts and dimension lines animate with a moving pen dot
  (path trim + ink bleed at the tip).
- **Hold the frame for the important numbers.** About 0.6 s of stillness after 9.5, 25 metres, 61, 140 and 54 minutes.
- **The rupture (part 2, "it let go"):** 3 frames of stillness → 2-frame red paper flash → split caption slips →
  camera shake follows the trace for ~4 s, then decays.
- **Drum scroll transitions:** between parts the paper scrolls vertically like a recording drum turning, carrying the
  old scene off the top while the next is drawn in from the bottom.

## 7. Sound design
- **Paper and pen:** a soft scratch while lines draw, pitch following pen speed. A small tick each time a grid
  minute passes on the helicorder.
- **The rupture:** deep sub rumble (25–40 Hz) that builds for 2 s → a low crack → rolling rumble that follows the
  trace envelope for 10 s, then fades under narration.
- **The bell:** a real bell partial set (fundamental + inharmonic partials at 2.0, 2.7, 3.9×) pitched to a low C,
  struck once at the hook and once in part 5, with a 15 s decay. This is the emotional motif of the film.
- **Water:** a long deep swell for the tsunami, never cartoonish. Silence for one beat on the death tolls.
- **Music:** sparse felt piano + bowed low strings. Cut to silence at "it let go", come back after the shaking, and
  resolve on the bell note at the end.
- **Master:** ducking under the voice, mono-safe lows, −14 LUFS, true peak −1.2 dB.

## 8. Storyboard (by part)
1. **Hook.** Paper. A strain-meter trace swings slowly (bronze). Pull back: it's the outline of the globe itself,
   deforming in and out (FIG 1). "It started here": spin to Chile, red star, title (FIG 7).
2. **The crack.** Dive through the coast into the section (FIG 2). Plates slide as cut paper. The locked zone glows
   and strain ticks bend. 3:11 pm clock. The rupture with the split caption. The inset map draws the 1,000 km crack.
3. **How big.** The helicorder drum (FIG 3): quiet lines, then the pen goes wild in red. A stopwatch counts to ~10 min.
   The trace's peaks become squares: Haiti's dot, 8.0, Japan 9.1, then the 9.5 square slams in (FIG 4).
4. **The ocean.** The 9.5 square folds down into the Pacific chart (FIG 5). Teal fronts expand from Chile with hour
   marks. The caption rides the front. Hawaii at 15 h (61), Japan at ~22 h (~140), and a 750 km/h card.
5. **The bell.** The fronts wrap around the globe. The whole planet deforms in the 0S2 shape, and the strain trace
   returns. The bell is struck (sound). Labels for the 54-min note and the 20-min breathing mode. Cut-away inner
   layers (crust, mantle, core) briefly appear as paper rings: "what the inside is like".
6. **What it left.** The globe's ring becomes the waterline. Sunken forest, the dashed old ground level, −2 m, and
   Cordón Caulle erupting behind (FIG 6). Last line: the pen on a fresh drum draws one last slow swing, and the bell
   fades.

## 9. Fact sheet
See `SCRIPT.md`.
