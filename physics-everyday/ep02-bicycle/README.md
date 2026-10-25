# Ep. 02 — Why don't bikes fall over?

Cut-paper stop-motion, 9:16, 80 s. Everything is drawn in code with skia: cardstock pieces with grain, cast
shadows, cut/torn edges, brads, pins, string, masking tape and marker ink. Puppets animate on twos (12 poses/s),
the camera moves on ones (24 fps).

| file | what |
|---|---|
| `paper.py` | the paper engine (pieces, shadows, grain, boil, props, text chips) |
| `puppets.py` | bike (side + rear view), kid, scientist, pigeon, snail, ant, houses, hills, captions |
| `frames.py` | the five style frames -> `out/frame_*.png`, `out/board.png` |
| `script.py` | narration lines + fact notes and sources |
| `voiceover.py` | Kokoro TTS -> `build/vo/` + `timeline.json` |
| `film.py` | all scenes, camera, captions, render -> `out/ep02_bicycles.mp4` |
| `sound.py` | plucked music bed, paper/bike foley, mix balanced against the voice |

```
python3 frames.py
python3 voiceover.py
python3 film.py               # PROCS=4 by default; --still 3,9 for single frames
```
