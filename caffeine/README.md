# The Caffeine Tape: "What One Coffee Does to Your Body (The Next 6 Hours)"

A ~75 s vertical Short (1080×1920, 30 fps) in a retro **90s VHS** style. Everything is drawn in code: Skia graphics, Kokoro TTS narration, a synthesised smooth-jazz bed, and sound effects.

The whole video plays as a worn VHS tape. The VCR counter is the timeline: between segments the tape fast-forwards from one moment after the sip to the next, and at the end it rewinds to 0:00:00 so the Short loops.

| Part | Counter | Segment |
|---|---|---|
| part1 | 0:00:00 | Title card: CRT switches on, chrome logo, mug mascot sips |
| part2 | 0:10:00 | *Medical Tape 7*: caffeine absorbed into the blood, ABSORBED meter to 99% |
| part3 | 0:45:00 | *Park That Molecule!*: adenosine vs caffeine in the receptor spots |
| part4 | 1:00:00 | *The Body Forecast*: adrenaline, blood pressure, dopamine; the Doppler gut radar |
| part5 | 5:00:00 | *Caffeine Markets*: half-life chart and sleep report |
| part6 | 6:00:00 | The crash, pro tips, "Be kind, rewind", rewind and stop |

Narration and the fact check with sources are in `SCRIPT.md`; titles, description and tags are in `SHORTS_POST.md`.

## Files
- `vhs.py`: the tape look.
  - Luma softening with VCR edge ringing.
  - Smeared, lagging chroma.
  - Line jitter, a crawling tracking band, head-switching noise and dropouts.
  - Fast-forward/rewind tearing, and the crash "sag".
  - Scanlines, snow, lifted blacks.
- `tv.py`: the shared show engine.
  - Programme banner, VCR on-screen display (PLAY / FF / REW / STOP, counter) and the camcorder date stamp.
  - Closed captions: white VT323 text on black boxes, numbers as digits, key words in yellow.
  - The 90s graphics kit: chrome text, starbursts, Memphis confetti, neon grid, bevelled panels, the mug mascot and the purine ring.
- `lot.py`: the game-show set shared by part3 and part6 (receptor spots, adenosine, caffeine, the SLEEPY-O-METER).
- `audio.py`: adds the `lounge` bed (electric piano, bass, drum machine, tape wow and flutter, hiss). It also adds the sounds `ff`, `rewind`, `clunk`, `crt_on`, `static`, `ding`, `buzzer`, `chime`, `radar`, `gurgle`, `slurp`, `cash`, `power_down` and `ticker`.
- `fonts/`: VT323, Shrikhand, Archivo Black, Righteous and Bowlby One (all Google Fonts, OFL).

## Build
```bash
python3 voiceover.py part1      # ... part6 (Kokoro model files in $KOKORO_DIR)
python3 render.py part3 --still 3,6,9
python3 render.py full          # -> out/full.mp4 + out/full_share.mp4
```
