# The Physics of Everyday Things

An explainer series made entirely in code. Episode 1: **Microwaves** (target 1:30 to 2:00, English, curious viewers).
Stage: **style lock**. Three 12-second style tests on the same microwave beat (standing waves leave hot and cold spots).

| Style | Video | Board |
|---|---|---|
| A · 3Blue1Brown (dark canvas, glowing curves, LaTeX maths) | `style-tests/out/style_3b1b.mp4` | `style-tests/out/board_3b1b.png` |
| B · Kinetic typography + icons | `style-tests/out/style_kinetic.mp4` | `style-tests/out/board_kinetic.png` |
| C · Low-poly 3D | `style-tests/out/style_lowpoly.mp4` | `style-tests/out/board_lowpoly.png` |

## Build
Needs `skia-python==144.0.post2 numpy pillow` plus ffmpeg (and `libegl1` on Linux).
```
cd style-tests
python3 kit.py style_3b1b                 # -> out/style_3b1b.mp4 (same for style_kinetic, style_lowpoly)
python3 kit.py style_lowpoly --still 4,8  # quick frames -> build/style_lowpoly/
python3 boards.py                         # style-guide boards -> out/board_*.png
```

## Files
- `fonts/`: Computer Modern (CMU Serif, SIL OFL) for the maths look, Inter Display for the sans styles.
- `style-tests/kit.py`: easing, paints, mixed-font text runs, path trimming, multiprocess renderer.
- `style-tests/style_lowpoly.py`: includes a tiny painter's-algorithm 3D renderer (camera spline, flat shading, layers).
