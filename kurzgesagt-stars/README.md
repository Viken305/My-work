# You Are Made of Dead Stars

A premium Kurzgesagt-style explainer (~4:45, 7 chapters) about the life and death of stars, with a new guide character, **ORBI**.
Stage: **built**. Each part is `partN.py` (part1 hook … part7 star stuff); `python render.py full` rebuilds the whole film from code.

- Script and fact sheet: `SCRIPT.md` (narration lines in `script.py`)
- Style guide (premium techniques, palette, ORBI): `STYLE_GUIDE.md`
- Storyboards, character sheet, motion test: `out/storyboards/`

## Premium pipeline
`premium.py` adds procedural nebula textures (fBm and domain warp), parallax starfields, bokeh, additive light,
lens flares and diffraction spikes, plus post-processing: bloom, chromatic aberration, colour grade, vignette and grain.
Motion blur comes from averaging sub-frames. Parts set `PREMIUM = True` and `render.py` uses this pipeline automatically.

## Build
Same setup as `../kurzgesagt-minerals/README.md`, plus `pip install opencv-python-headless`.
```
python orbi.py            # ORBI character sheet
python motion_test.py     # 12 s premium motion test
python storyboard.py      # storyboard sheets
python voiceover.py part1 # narration (repeat for part2 … part7)
python render.py part3    # one part -> out/part3.mp4 + out/part3_share.mp4
python render.py part3 --still 5,12  # quick stills
python render.py full     # all 7 parts + continuous soundtrack -> out/full_share.mp4
```

## Files
- `premium.py`: premium rendering layer. `orbi.py`: the ORBI character. `cosmos.py`: stars, protostar, nebulae, white dwarf, pulsar, black hole, supernova, element tiles.
- `story.py`: shared timing, scene stacking, chapter titles, ORBI-on-a-path. `part1.py` … `part7.py`: the chapters.
- `boards.py`: storyboard key frames. `storyboard.py`: sheet composer.
- `engine.py`, `audio.py`, `render.py`, `voiceover.py`: shared kit from the earlier videos.
