# Earth Is Weirder Than You Think

A premium Kurzgesagt-style explainer (~4:16, 8 parts) of surprising facts about our planet, rendered entirely in code.
Guide: **NIMBUS, a little cloud** on the animated face rig (`rig.py`, shared with the immune video).

- Script and fact sheet with sources: `SCRIPT.md` (narration in `script.py`)
- YouTube kit: `DESCRIPTION.md` · Character sheet: `out/storyboards/nimbus_sheet.png` · Thumbnail: `out/thumbnail.png`

## Build
Same setup as `../kurzgesagt-stars/README.md` (skia-python, numpy, opencv-python-headless, Pillow, soundfile, kokoro-onnx, ffmpeg).
```
python voiceover.py part1            # narration (repeat for part2 … part8)
python render.py part3 --still 5,12  # quick stills
python render.py full                # all parts + one soundtrack -> out/full_share.mp4
python nimbus.py                     # character sheet
python thumbnail.py                  # thumbnail
```

## Files
- `nimbus.py`: Nimbus (puffy breathing body, puff hands, rain / lightning / sparkle moods). `rig.py`: face rig.
- `earth.py`: procedural spinning globe (fBm continents, biomes, ice caps, clouds, night side, bulge), skies, Milky Way, trees, hills, dunes, ice, penguins, ants, lightning, people.
- `story.py`: narration timing, camera paths, chapter titles, chips, big numbers, transitions. `part1.py` … `part8.py`: the chapters.
- `premium.py`, `engine.py`, `audio.py`, `render.py`, `voiceover.py`: shared kit.
