# Why Borders Are Shaped the Way They Are

A vertical Short (1080×1920, 30 fps, about 1:20) in the simple **Paper Atlas** style. Everything is drawn in code from
Natural Earth map data.

**Stage: style frames and timing**. Animation comes next.

| File | What |
|---|---|
| `script.py` | Narration, one part per section |
| `SCRIPT.md` | Script, fact check and sources |
| `SHOTS.md` | Shot list with in/out times and length per shot (from the real narration audio) |
| `geo.py` | Natural Earth loading, projections (Natural Earth and local equirectangular), straight-border finder |
| `atlas.py` | The Paper Atlas look: page, map card, captions, handwritten notes, map layers |
| `frames.py` | The six style frames: `out/frame_1.png` … `frame_6.png`, board `out/style_frames.png` |
| `shots.py` | Computes the shot timing and writes `SHOTS.md` |

## Build
```bash
python3 geo.py fetch                         # Natural Earth data -> build/data (not in git)
for p in 1 2 3 4 5; do python3 voiceover.py part$p; done   # narration (Kokoro, $KOKORO_DIR)
python3 shots.py                             # SHOTS.md
python3 frames.py                            # style frames
```
