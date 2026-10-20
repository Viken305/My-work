# The Deepest Hole Ever Dug: style guide

A 9:16 Short (~1:45) about the Kola Superdeep Borehole, rendered entirely in code. The style is deliberately **not**
Kurzgesagt. It's editorial noir: a technical plate from a geology journal, lit like a thriller.

## Look
- **Palette:** graphite black `#09090A`, warm off-white `#EDE8E0` for linework and text, warm grey `#968F88` for
  secondary text, and **one accent**, ember orange `#FF6026`, for heat, the hole and emphasis. Steel blue
  `#80AACD` appears only for water.
- **Rock:** engraved strata. Every layer has its own texture (grain, bedding lines, crystals, hatching, waves), drawn
  at the right level of detail for the zoom so nothing swims. The deep rock glows with heat.
- **The hole:** a thin ember line with a soft glow and a hot drill bit throwing sparks.
- **HUD:** a mono depth gauge (top left) and dimension lines with mono labels, like a technical drawing.
- **Post:** crushed neutral blacks, a gentle S-curve, warm halation on the brightest highlights only, heavy film
  grain, vignette, and 3–5 sample motion blur.

## Typography
- **Inter Display** (SemiBold/Black) for captions and titles.
- **Noto Serif Display Italic** in ember for emphasis words (editorial contrast).
- **Noto Sans Mono** for numbers, the gauge and labels.

## Captions (from research on premium caption design)
- Words appear **as they are spoken**. Each word's letters rise out of a soft blur with a small spring settle,
  staggered per letter (the Apple-keynote "blur-in").
- The spoken word is full white; spoken words settle to warm grey.
- **Restraint:** only 2–4 key words per line switch to the serif italic in ember with a faint glow.
- Exit: a phrase drifts up and blurs out, word by word.
- Max 3 words per phrase, 1–2 lines, kept **above y = 1480** so the Shorts interface never covers them.
- Word timing comes from the real audio. Pauses in the waveform are matched to punctuation (dynamic programming),
  and words inside each stretch are spread by espeak phoneme length.
- Numbers either count live (depth, temperature) or roll like an odometer (years).

## Sound (layered, trailer-style)
- **Impacts:** transient click + mid body + pitch-dropping boom + sub, with a stereo reverb tail.
- **Whooshes:** a sweeping band-pass whose peak lands on the cut, panned across. **Risers** stop dead into the hit.
  **Reverse swells** suck into the next hit.
- **Moment sounds:** paper slaps for the clippings, a stamp, tape stop on "hoax" (the music bus really slows to zero),
  odometer ticks, drill rumble, drips, boiling hydrogen bubbles, heat roar, the metal clank of the cap, and Arctic
  wind.
- **Music beds:** tension drone, deep pressure drone, an airy "wonder" pad for the fossils, a heat drone and a sparse
  ending. They duck under the voice with an envelope follower.
- **Mono-safe:** stereo widening on the highs only, so the bass stays in phase on phone speakers.
- **Master:** glue compression, soft clipping, loudness normalised to -14 LUFS (true peak -1.2 dB).

## Structure (hook first)
1. **Hook:** 1989 → newspaper clippings → SCIENTISTS DRILL INTO HELL → the scream → tape stop → HOAX → the flat
   line becomes the real hole → title.
2. **The hole:** the Arctic site at night, then 23 cm vs a dinner plate, then the fall to 12,262 m.
3. **Scale:** 37 Eiffel Towers (52 m short), Everest upside down (3.4 km gap), the deepest ocean, 1970 → 1989.
4. **Finds:** plankton microfossils at ~6.7 km, water squeezed from the rock, hydrogen-boiling mud.
5. **End:** 180 °C and rock like hot plastic, then they stop. A third of the crust, 0.19 % to the centre, the
   rusty cap, then "It does not scream." and a cut to black that loops back to the hook.
