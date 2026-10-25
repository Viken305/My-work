# Ep. 03 — Why does popcorn pop?

Dark-studio food film, 9:16, 80 s, 24 fps. 3D in code (moderngl, headless) with a food-commercial look:
studio-softbox reflections, Fresnel, metals (copper pan, brass, gold foil), light glowing through popcorn,
shallow depth of field, drifting dust, warm grade and fine grain. Serif titles (Cormorant Garamond), gold line-art
instruments, British narration (Kokoro `bf_emma`), piano-and-pad score with close kitchen foley.

| file | what |
|---|---|
| `lux.py` | studio renderer (shader, env reflections, translucency), lathe/star/param meshes, grade |
| `props.py` | kernel, cutaway, popped popcorn, hull petals, copper pan, burner + flame, oil, bowl, champagne, butter, salt, steam |
| `lookdev.py` | look-development stills |
| `script.py` | narration + fact notes and sources |
| `voiceover.py` | Kokoro TTS -> `build/vo/` |
| `film.py` | 13 shots, cameras, pop simulation, compositing, render -> `out/ep03_popcorn.mp4` |
| `overlay.py` | titles, captions, thermometer, pressure gauge, labels, 2,900 fps readout, waveform, dust |
| `sound.py` | score, foley, voice-led mix |

```
python3 voiceover.py
python3 film.py               # PROCS=3, SS=1.6 by default; --still 3,40 for single frames
```
