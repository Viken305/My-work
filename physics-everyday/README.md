# The Physics of Everyday Things

An explainer series made entirely in code. Episode 1: **Microwaves** (target 1:30 to 2:00, English, curious viewers).
Stage: **style lock**. Three 12-second style tests on the same microwave beat (standing waves leave hot and cold spots),
then a 22-second test of the chosen 3D direction in a real kitchen.

| Style | Video | Board |
|---|---|---|
| A · 3Blue1Brown (dark canvas, glowing curves, LaTeX maths) | `style-tests/out/style_3b1b.mp4` | `style-tests/out/board_3b1b.png` |
| B · Kinetic typography + icons | `style-tests/out/style_kinetic.mp4` | `style-tests/out/board_kinetic.png` |
| C · Low-poly 3D | `style-tests/out/style_lowpoly.mp4` | `style-tests/out/board_lowpoly.png` |

### Test C2 · 3D kitchen (chosen direction)
`style-tests/out/kitchen_wide.mp4` (16:9) and `style-tests/out/kitchen_tall.mp4` (9:16). Narrated, captioned, with sound.
- **Camera:** short-form 3D explainer feel (Zack D. Films reference). Hard cuts on the voice, fast swoops and crash zooms
  with an expo ease, a small handheld drift, a settle-kick after each cut, motion blur from averaged sub-frames.
- **Look:** real kitchen set (window sun with shadows, tiles, cabinets, fridge, pendant lamp), depth of field keeps
  the microwave the subject, bloom on glowing parts, filmic tone map.
- **Background gags:** a cat on the counter nudging a mug towards the edge (stares at camera, then shoves it off),
  a toaster that launches toast and catches it, a robot vacuum that keeps bumping into the fridge, a rubber duck.
- **Extras:** thermal-camera wipe on the food, word-by-word captions, synthesized sound effects and music bed.

## Build
Needs `skia-python==144.0.post2 numpy pillow` plus ffmpeg (and `libegl1` on Linux).
```
cd style-tests
python3 kit.py style_3b1b                 # -> out/style_3b1b.mp4 (same for style_kinetic, style_lowpoly)
python3 kit.py style_lowpoly --still 4,8  # quick frames -> build/style_lowpoly/
python3 boards.py                         # style-guide boards -> out/board_*.png

# 3D kitchen test (also needs moderngl, opencv-python-headless, kokoro-onnx, soundfile; libegl-mesa0 on Linux)
python3 kitchen_vo.py                     # narration (Kokoro TTS, model files in KOKORO_DIR)
python3 kitchen.py --still 3,12.5         # quick frames -> build/kitchen/
python3 kitchen.py                        # -> out/kitchen_wide.mp4
python3 kitchen.py --tall                 # -> out/kitchen_tall.mp4
```

## Files
- `fonts/`: Computer Modern (CMU Serif, SIL OFL) for the maths look, Inter Display for the sans styles.
- `style-tests/kit.py`: easing, paints, mixed-font text runs, path trimming, multiprocess renderer.
- `style-tests/style_lowpoly.py`: includes a tiny painter's-algorithm 3D renderer (camera spline, flat shading, layers).
- `style-tests/gl3d.py`: headless OpenGL renderer (moderngl/EGL): shadow-mapped sun, point lights with box masks,
  transparency, thermal-view shader, plus post (depth of field, bloom, ACES tone map, vignette).
- `style-tests/kitchen.py`: the kitchen set, animation, shot list, captions, sound. `audio.py`: shared synth kit.
