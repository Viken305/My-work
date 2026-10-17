# How the Earth Makes Crystals

Kurzgesagt-style explainer, rendered entirely in code. See `STORYBOARD.md` for the plan.

| Part | Scenes | Length | File |
|---|---|---|---|
| 1 | Hook + What is a mineral? | 0:40 | `out/part1_share.mp4` |

## Render
```
pip install skia-python kokoro-onnx soundfile numpy pillow   # + ffmpeg, libegl1
# Kokoro TTS model files (temporary narration voice):
#   https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
export KOKORO_DIR=/path/to/models
python3 voiceover.py part1        # narration -> build/part1/vo
python3 part1.py --still 5,24,36  # check frames
python3 part1.py                  # full render -> out/part1.mp4
```

- `engine.py`: palette, easing, glows, atoms, the bird, cubes, grain.
- `audio.py`: procedural pad, plucks and SFX, ducked under the narration.
- `script.py`: narration lines. Replace `build/<part>/vo/*.wav` with a real voice recording (same file names) and re-render.
