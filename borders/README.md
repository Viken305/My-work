# Why Borders Are Shaped the Way They Are

A vertical Short (1080×1920, 30 fps, about 1:20) in the simple **Paper Atlas** style. Everything is drawn in code from
Natural Earth map data.

Full video: `out/full.mp4` and `out/full_share.mp4` (not in git; `python3 render.py full`).

| File | What |
|---|---|
| `script.py` | Narration, one part per section |
| `SCRIPT.md` | Script, fact check and sources |
| `SHOTS.md` | Shot list with in/out times and length per shot (from the real narration audio) |
| `geo.py` | Natural Earth loading, projections (Natural Earth and local equirectangular), straight-border finder |
| `atlas.py` | The Paper Atlas look: page, map card, captions, handwritten notes, map layers |
| `frames.py` | The six style frames: `out/frame_1.png` … `frame_6.png`, board `out/style_frames.png` |
| `shots.py` | Computes the shot timing and writes `SHOTS.md` |
| `film.py` | The whole Short on one timeline: every shot, captions (word by word, key words in red), headline swaps, camera pushes, dissolves, loop |
| `render.py` | Stills, a one-frame-per-shot sheet, and the full render (parallel frames, then the audio mix) |
| `audio.py` | Mixer and effects, plus the `atlas` music bed (plucked arpeggios, pad, bass, shaker) and the `pencil`, `marker` and `ruler` sounds |
| `SHORTS_POST.md` | Title, description, tags, pinned comment |

## Build
```bash
python3 geo.py fetch                         # Natural Earth data -> build/data (not in git)
for p in 1 2 3 4 5; do python3 voiceover.py part$p; done   # narration (Kokoro, $KOKORO_DIR)
python3 shots.py                             # SHOTS.md
python3 frames.py                            # style frames
python3 render.py sheet                      # one frame per shot -> build/sheet.png
python3 render.py full                       # -> out/full.mp4 + out/full_share.mp4
```
