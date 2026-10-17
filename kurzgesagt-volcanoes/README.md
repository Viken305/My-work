# Why Do Volcanoes Exist?

A Kurzgesagt-style explainer (3:29), made in the same style and with the same code kit as `../kurzgesagt-minerals`.
Final narration: `script.py`. Upload kit (title, description, chapters, sources): `DESCRIPTION.md`.

## Watch
| File | What |
|---|---|
| `out/full_share.mp4` | **The whole film**, preview quality |
| `out/part1_share.mp4` … `part5_share.mp4` | Each part on its own |
| `out/thumbnail.png` | YouTube thumbnail |

| Part | Content | Length |
|---|---|---|
| 1 | Hook + inside the Earth (hot core, solid but flowing mantle) | 0:43 |
| 2 | Three ways to melt a rock + the lava-lamp rise | 0:40 |
| 3 | Where volcanoes are: plates, Ring of Fire, ridges, hotspots | 0:45 |
| 4 | Ooze or explode: soda analogy, runny vs sticky magma, Pinatubo | 0:39.5 |
| 5 | Why we need volcanoes + outro | 0:42 |

Full-quality masters are not in git (GitHub's 100 MB limit). Re-create them with the commands below.

## Build
Same setup as `../kurzgesagt-minerals/README.md` (Git, Python 3, FFmpeg, `pip install -r requirements.txt`, Kokoro voice files in `KOKORO_DIR`). Then:
```
python voiceover.py part1        (repeat for part2 … part5)
python render.py part3 --still 5,12,20
python render.py part3
python render.py full
python thumbnail.py
```
Higher-quality upload copy: `ffmpeg -i out/full.mp4 -c:v libx264 -preset slow -crf 21 -c:a copy out/full_youtube.mp4`

## Files
- `script.py`: narration lines. `part1.py` … `part5.py`: scenes and timelines.
- `common.py`: timing, captions, cards, plus the volcano kit (cones, lava, ash plumes, magma blob, cut-away Earth, globe).
- `engine.py`, `audio.py`, `render.py`, `voiceover.py`: copied from the minerals project (art kit, sound, renderer, TTS).
