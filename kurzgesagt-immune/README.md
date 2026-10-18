# There Is a War Inside You

A premium Kurzgesagt-style explainer (~4:28, 7 chapters) about the immune system, rendered entirely in code.
Hero: **KAI, a killer T cell**, on an animated face rig; every other cell acts with the same rig.

- Script and fact sheet: `SCRIPT.md` (narration lines in `script.py`)
- Style guide (palette, KAI, cast, face rig): `STYLE_GUIDE.md`
- YouTube kit (description, chapters, sources): `DESCRIPTION.md`
- Concept art: `out/storyboards/` (hero concepts, Kai acting test, big eater sheet), `out/styleframes/`, `out/thumbnail.png`

## Build
Same setup as `../kurzgesagt-stars/README.md` (skia-python, numpy, opencv-python-headless, Pillow, soundfile, kokoro-onnx, ffmpeg).
```
python voiceover.py part1            # narration (repeat for part2 … part7)
python render.py part3 --still 5,12  # quick stills -> build/part3/stills
python render.py part3               # one chapter -> out/part3.mp4 + out/part3_share.mp4
python render.py full                # all 7 chapters + one soundtrack -> out/full_share.mp4
python thumbnail.py                  # -> out/thumbnail.png
python kai_test.py                   # 14 s face-rig acting test
```

## Files
- `rig.py`: the face rig (poses, expression tracks with overshoot, blinks, eye darts). `kai.py`: KAI. `bigeater.py`: the macrophage.
- `cells.py`: the cast (bacteria, viruses, neutrophils + DNA nets, dendritic, T and B cells, antibodies, red blood cells).
- `heroes.py`: the organic tissue environment (and the original three hero concepts). `world.py`: vessel, lymph node, outside world, child, tissue cells.
- `story.py`: narration timing, camera paths, chapter titles, label chips, transitions. `part1.py` … `part7.py`: the chapters.
- `boards.py`, `storyboard.py`, `styleframes.py`: planning frames. `premium.py`, `engine.py`, `audio.py`, `render.py`, `voiceover.py`: shared kit.
