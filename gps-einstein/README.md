# Your Phone Does Einstein's Math

A 9:16 Short (about 1:55) about why GPS only works because of Einstein's relativity, rendered entirely in code in
the **Frosted Glass** style (see `STYLE_GUIDE.md`, which also has the checked fact sheet). It is a studio project:
`python3 ../studio/server.py` edits `project.json` and runs the tools below.

```
python3 voiceover.py part1          # narration (Kokoro; set KOKORO_DIR), only changed lines are re-voiced
python3 render.py part3 --still 2,6 # check frames -> build/part3/stills
python3 render.py part3             # one part -> out/part3.mp4
python3 render.py full              # the film -> out/full.mp4, out/full_share.mp4, out/youtube_upload_cover.mp4
python3 thumbnails.py               # out/thumb_short.png, out/thumb_wide.png
python3 storyboard.py               # out/panels/NN.png + out/storyboard_1.png
python3 styleframes.py              # the four look-development frames
```

| File | |
|---|---|
| `kit.py` | frame size, palette, easing, fonts, text |
| `glass.py` | the Frosted Glass engine: glass compositing (frost, edge refraction with dispersion, rim light, sheen), caustics, studio backdrop, glass Earth (Natural Earth coastlines in `data/`), orbits, satellites, clocks, glass text, post |
| `film.py` | shared pieces: the phone and its city map, chips, cards, beams, signal rings, glass bubbles |
| `captions.py` | word-synced captions on a frosted pill that grows as words arrive |
| `part1.py` … `part5.py` | the five parts; each pins its animation to spoken words (`TM.word`) |
| `audio.py` | synthesised sound: glass chimes, clinks, pings, lock chime, launch, the glass pad with its clock tick |

| Part | Lines | What happens |
|---|---|---|
| 1 Hook | H1–H3 | glass phone, Einstein's clock equation, the blue dot drifts 11 → 33 km over three days, title |
| 2 Clocks in the sky | A1–A3 | glass Earth, 20,200 km, ≈30 satellites on 6 orbits, atomic clock, WHERE (the satellite's own position) + WHEN, delay × c = distance |
| 3 Four satellites | B1–B3 | three glass spheres meet at one point (you), the 4th satellite locks the phone clock, light crosses 30 cm in 1 ns, 1 µs late = 300 m |
| 4 Einstein's problem | C1–C4 | GROUND vs ORBIT clocks, speed −7 µs, the gravity funnel +45 µs, sum +38 µs a day |
| 5 Fix and payoff | D1–D3 | 10.23 → 10.22999999543 MHz, launch, IN SYNC, the what-if world, back to the phone (loops to the first frame) |

Honesty on screen: the clock-hand drift is labelled as exaggerated, the light pulse is labelled with how much it is
slowed down, and the equation uses ≈ (it is the weak-field approximation).
