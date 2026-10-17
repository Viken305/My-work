# There Is a War Inside You

A premium Kurzgesagt-style explainer (~4:20) about the immune system, with a new hero: **MAX, a young macrophage**.
Stage: **storyboard for review** (the full video gets built after approval).

- Script and fact sheet: `SCRIPT.md` (narration lines in `script.py`)
- Style guide (palette, MAX, cast): `STYLE_GUIDE.md`
- Storyboards, cast sheet, motion test: `out/storyboards/`

## Build
Same setup as `../kurzgesagt-stars/README.md` (skia-python, numpy, opencv-python-headless, Pillow, soundfile, kokoro-onnx, ffmpeg).
```
python cells.py           # cast sheet (MAX + supporting cells)
python motion_test.py     # 12 s motion test: MAX hunts, gulps and digests a bacterium
python storyboard.py      # storyboard sheets, one per part
python voiceover.py part1 # narration (repeat for part2 … part7)
```

## Files
- `cells.py`: MAX and the whole cast, plus the tissue environment (textures, bokeh cells, motes).
- `boards.py`: storyboard key frames and props (skin wall, blood vessel, lymph node, body map, response graph, wanted poster).
- `premium.py`, `engine.py`, `audio.py`, `render.py`, `voiceover.py`, `storyboard.py`: the shared kit from the stars video.
