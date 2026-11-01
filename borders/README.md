# Why Borders Are Shaped the Way They Are

A vertical Short (1080×1920, 30 fps, about 2:22): a full-screen **3D globe flythrough** drawn entirely in code from Natural Earth data.

- **Camera:** one continuous perspective camera flies over a real globe from story to story. Long moves zoom out on the way, like a flight.
- **Effects:** borders burn on as glowing lines with a bright head, and countries rise as 3D slabs. Mountains stand up along the Pyrenees and the Andes. Pins and labels pop, years count up, and chapter cards play during the flights.
- **Close-ups:** El Chamizal, Baarle and the front-door house are built as 3D geometry in the same camera, so the flight never cuts.

Full video: `out/full.mp4` and `out/full_share.mp4` (not in git).

| File | What |
|---|---|
| `script.py` | Narration, one part per chapter |
| `SCRIPT.md` | Script, fact check and sources |
| `SHOTS.md` | Beat list with in/out times (from the real narration audio), written by `shots.py` |
| `globe.py` | The 3D engine: pinhole camera over the sphere, true horizon, back-face clamping, pixel decimation, slabs, glow lines, atmosphere, stars |
| `film3d.py` | The film: narration schedule, camera key path, every story beat, schematic close-ups, chapter cards, HUD, word-timed captions, loop |
| `sound.py` | Narration placement, effects on the beats, the `voyage` music bed |
| `render.py` | Stills, contact sheets and the full render (parallel frames, then the mix) |
| `audio.py` | Mixer and effects, plus the `voyage` and `atlas` beds and the `pencil`, `marker` and `ruler` sounds |
| `geo.py` | Natural Earth loading and the straight-border finder |
| `SHORTS_POST.md` | Title, description, tags, pinned comment |
| `film_atlas.py`, `render_atlas.py`, `shots_atlas.py`, `atlas.py`, `frames.py` | The earlier flat "Paper Atlas" version and its style frames |

## Build
```bash
python3 geo.py fetch                                        # Natural Earth data -> build/data (not in git)
for p in 1 2 3 4 5 6; do python3 voiceover.py part$p; done  # narration (Kokoro, $KOKORO_DIR)
python3 shots.py                                            # SHOTS.md
python3 render.py sheet 5,20,40,60,80,100,120,140           # contact sheet -> build/sheet3d.png
python3 render.py full                                      # -> out/full.mp4 + out/full_share.mp4
```
