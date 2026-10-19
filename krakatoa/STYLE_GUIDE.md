# The Loudest Sound Ever Heard: style guide

A 9:16 Short (~1:40) about the 1883 eruption of Krakatoa, rendered entirely in code for @BrighterMinds.

The style is new. It is not Kurzgesagt flat shapes, and it is not the graphite noir of `deep-hole/`. This one is
**"Cyanotype & Sulfur"**: the world drawn like an 1883 cyanotype (blueprint) print, with sound made visible as
glowing sulfur-yellow pressure rings. The hero of the video is **the sound wave itself**. Every scene is about where
it went, how strong it was and what it did.

## 1. Big idea
- **Sound you can see.** Pressure waves are drawn as bright rings that expand, bend around the globe and pass over
  cities. Every number about loudness lives on a physical ring or meter, never floating alone.
- **Victorian instrument, modern motion.** The look is a 19th-century scientific plate (cyanotype paper, engraved
  coastlines, barograph ink traces, brass gauge ticks), but it moves like a modern product film: springy, smooth,
  deep parallax, motion blur.
- **Quiet, then violent.** Most scenes are calm and slow. The explosion is the only moment the whole frame breaks:
  shake, chromatic split, white flash, audio dropout. Contrast is what makes it feel loud.

## 2. Palette
| Role | Colour | Hex |
|---|---|---|
| Background (deep cyanotype) | Prussian blue, almost black at the edges | `#0B1E3A` → `#06101F` |
| Paper and linework | Cyanotype white, slightly blue | `#E6EEF5` |
| Secondary text, grid, ticks | Faded blueprint | `#7F9BB8` |
| **Accent 1: sound and pressure** | Sulfur yellow | `#FFD23F` |
| **Accent 2: fire, ash, danger** | Lava crimson | `#FF3B2F` |
| Sunset scene only | Volcanic sunset gradient | `#FF3B2F` → `#FF8A3D` → `#5B2A86` |

Rules:
- Blue and white do 90% of the work. Yellow means **sound**, red means **harm**, and they never swap.
- The sunset gradient appears **once**, in the "red skies around the world" scene, so it lands as a reveal.

## 3. Texture and rendering
- **Cyanotype paper:** a large, slow, low-contrast paper fibre noise plus uneven exposure (lighter centre, darker
  vignette edges), like a real sun print.
- **Engraved linework:** coastlines, the island and the ocean are drawn with hairline hatching and contour lines, not
  flat fills. Ocean = concentric bathymetry lines that slowly drift.
- **Sound rings:** additive glow (core line + two blur passes), a faint chromatic fringe on the leading edge, and a
  thin trail of "ripple" distortion behind them that bends the linework they pass over.
- **Ash:** particle system of 8–15k soft points with curl-noise drift, depth-sorted, with depth of field.
- **Camera:** continuous, no hard cuts except at the explosion. Moves are match-moves (a ring becomes a globe, a
  barograph needle becomes a horizon line, an eardrum becomes a ring).
- **Post:** motion blur (3–5 samples), bloom only on yellow and red, gentle blue-teal grade, fine grain, vignette.
  The explosion frame gets a 2-frame white overexposure and an RGB split.

## 4. Typography
- **Captions:** *Inter Display* Bold, cyanotype white.
- **Emphasis words:** *Noto Serif Display* Italic. Sound words (BOOM, heard, loud, sound) in **sulfur yellow**;
  harm words (died, gone, wave, ash) in **lava red**.
- **Numbers and instrument labels:** *Noto Sans Mono*, set like engraved plate captions (`FIG. 3 · BAROMETER, LONDON`).
- **Title cards:** large tracked caps, `THE LOUDEST SOUND / EVER HEARD`.

## 5. Captions (premium, new for this video)
Research points the same way for 2026: the best-performing captions are speech-synced, restrained, and the
motion means something. So this video's caption system is **audio-reactive**: the words behave like sound.

1. **Word-by-word reveal timed to the real voice** (same pause-matching aligner as `deep-hole/`).
2. **Ripple-in:** each word enters with a small horizontal wave passing through its letters (letters lift 0→8 px
   and back in sequence, with a spring settle), like a pressure wave travelling through the text.
3. **Loudness drives weight:** the active word's scale and glow follow the voice envelope (±4% scale, glow on
   peaks), so stressed syllables visibly push.
4. **Emphasis words** switch to the serif italic in yellow or red, with a thin ring that pulses out from behind
   them once.
5. **The BOOM caption:** on the explosion, the word **"BOOM"** does not animate in. It slams in at full size, the
   letters shake, and a ring blasts it apart into particles that become the ash.
6. **Exit:** words compress and blur sideways, as if pushed by a passing wave.
7. **Layout:** max 3 words per phrase, 1–2 lines, centred at y≈1380, never below y=1480 (Shorts UI safe zone),
   nothing in the top ~220 px or the right ~150 px between y 900–1520.
8. **Numbers** count live on instruments: a dB needle that swings, a distance that counts up along the ring, an
   odometer for the year.

## 6. Sound design (the most important part of this video)
The topic is sound, so the mix has to be the best yet.
- **Before the explosion:** sparse. Ocean swell, gulls, wooden ship creaks, a low uneasy drone, distant rumbles
  growing.
- **The explosion:** a 3-stage event. (1) A pre-suck: all audio pulls back with a reverse swell. (2) The hit: a
  layered impact (transient crack + mid body + pitch-dropping boom + 25 Hz sub) with heavy saturation.
  (3) **The ringing:** everything cuts to a high-pitched tinnitus tone with muffled, low-passed sound underneath,
  as if the viewer's own ears were damaged, then slowly recovers over ~3 s.
- **Distance:** every time the camera follows the wave to a farther place, the boom is heard again, more muffled,
  delayed and quieter (low-pass + reverb + time offset), so the viewer *hears* distance.
- **Rodrigues:** the sound arrives as a dull "heavy guns" thud, 4 hours later (with a ticking clock).
- **Barographs:** a pen-scratch ink sound and a soft tick each time the wave passes a city.
- **Water:** tsunami as a deep, rising roar, handled with restraint (no cartoon sounds around deaths).
- **Music beds:** a slow cello-like drone that builds to the explosion, silence after it, then a warm, sad pad for the
  sunsets, ending on a single low note.
- **Master:** ducking under the voice, mono-safe lows, -14 LUFS, true peak -1.2 dB.

## 7. Story (hook first, ~1:40)
1. **Hook (0–12 s).** Black. A faint thud. "In 1883, police on a tiny island in the Indian Ocean heard what sounded
   like distant cannon fire. There were no ships. The sound had come from almost five thousand kilometres away."
   Camera pulls back from Rodrigues across the ocean to Krakatoa. Title: *THE LOUDEST SOUND EVER HEARD*.
2. **The island (12–30 s).** Krakatoa, 27 August 1883, after a night of eruptions. A clock ticks to 10:02 am.
   The island seen in section: magma, sea water, pressure building. Silence. **BOOM.**
3. **How loud (30–50 s).** Rings expand. A ship 64 km away: half the crew's eardrums burst. A gas plant gauge
   160 km away jumps off its scale: about 172 decibels, louder than standing next to a jet engine. A dB meter shows
   why every 10 dB is ten times the power.
4. **How far (50–68 s).** The ring crosses the ocean. Four hours later it reaches Rodrigues, 4,800 km away. Back to
   the hook: that was the "cannon fire".
5. **The invisible part (68–85 s).** Most of the wave was too low to hear. The globe appears; the ring wraps around
   it. Barometers in cities around the world twitch, about every 34 hours, for 5 days. It went around the planet
   three to four times in each direction.
6. **The cost and the sky (85–100 s).** Most of the island was gone. Tsunamis over 30 m high. About 36,000 people
   died. Then the ash spread around the world, and the sunsets turned blood red for months.
7. **End (100–108 s).** In 1927, a new island rose from the same spot: Anak Krakatau, "Child of Krakatoa". It is
   still erupting today. The last sound is a soft thud, which loops back to the hook.

## 8. Fact sheet (status)
| Claim | Status |
|---|---|
| Final explosion 27 Aug 1883, ~10:02 am local | Widely cited; some sources give 10:41 for a later blast. We use "just after 10 am". |
| Heard on Rodrigues as "the roar of heavy guns", ~4,800 km away, ~4 h later | Confirmed by several accounts |
| Ship (Norham Castle) ~64 km away, "eardrums of over half my crew" shattered | Widely quoted from the captain's log; we say "half the crew" |
| ~172 dB at ~160 km (Batavia gasworks gauge, +2.5 inHg) | **An estimate**, said as "about 172 decibels" |
| Pressure wave recorded worldwide for 5 days, about every 34 h; 3–4 times round each way | Confirmed (barograph records) |
| Most (over 2/3) of the island collapsed | Confirmed |
| Tsunamis over 30 m; ~36,000 dead (official 36,417) | Confirmed range; we use rounded, conservative figures |
| Red sunsets worldwide for months | Confirmed (Britannica) |
| Anak Krakatau emerged 1927; partly collapsed in 2018 | Confirmed |
| New York fire engines called out for the red sky | **Not used**: only weak sources |
