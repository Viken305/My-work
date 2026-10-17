# You Are Made of Dead Stars

A premium Kurzgesagt-style explainer (~3:45) about the life and death of stars, with a new guide character, **ORBI**.
Stage: **storyboard for review** (the full video gets built after approval).

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
python voiceover.py part1 # narration (repeat for part2 … part6)
```

## Files
- `premium.py`: premium rendering layer. `orbi.py`: the ORBI character. `cosmos.py`: stars, protostar, nebulae, white dwarf, pulsar, black hole, supernova, element tiles.
- `boards.py`: storyboard key frames. `storyboard.py`: sheet composer.
- `engine.py`, `audio.py`, `render.py`, `voiceover.py`: shared kit from the earlier videos.
