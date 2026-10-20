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

## 7. Story (hook first, ~1:50; final narration in SCRIPT.md)
1. **Hook (part 1).** Night on Rodrigues, 1883: a dull thud like cannon fire. The camera pulls back 4,800 km across
   the ocean to Krakatoa ("From here."), the island in section at 10:02 am, silence, **BOOM**, blown ears, title.
2. **How loud (part 2).** The ring crosses the Sunda Strait: the ship at 64 km (eardrums), the Batavia gas works at
   160 km (gauge spike), then a brass dB meter swings past talk, pain and a jet engine to about 172 dB.
3. **How far (part 3).** Pull back to the whole ocean while a clock counts the 4 hours; the ring reaches Rodrigues
   (the cannon fire again); "farthest sound in recorded history".
4. **The part nobody heard (part 4).** A hearing-range ruler with the wave below it; the globe with the wave lapping
   it; a London barograph collecting seven spikes over five days; 3–4× around each way.
5. **The cost and the child (part 5).** The island collapses (dashed "before"), a tsunami crest runs out, 36,000 in
   sober red; blood-red sunsets with ash; night sea, and in 1927 a new cone breaks the surface: Anak Krakatau, still
   active. A last distant thud loops back to the hook.

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
