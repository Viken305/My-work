# How Did India Get Here?

A Kurzgesagt-style explainer (~7:02) about India's history, culture, present and future, in the same style and code kit as `../kurzgesagt-minerals` and `../kurzgesagt-volcanoes`.

- Script + fact sheet: `SCRIPT.md` (narration lines in `script.py`)
- Style guide: `STYLE_GUIDE.md` (palette, motifs, portrait and political-balance rules)
- Storyboards + faces test: `out/storyboards/`
- Upload kit (title, description, chapters, sources): `DESCRIPTION.md`

## Watch
| File | What |
|---|---|
| `out/full_share.mp4` | **The whole film**, preview quality |
| `out/part1_share.mp4` … `part7_share.mp4` | Each part on its own |
| `out/thumbnail.png` | YouTube thumbnail |

| Part | Chapter | Length |
|---|---|---|
| 1 | One in six humans | 0:31 |
| 2 | Ancient India | 0:57 |
| 3 | Empires, colonial rule & freedom | 1:22 |
| 4 | Building a republic | 0:54 |
| 5 | Culture | 0:46 |
| 6 | India today & Narendra Modi | 1:45 |
| 7 | What comes next | 0:47 |

Full-quality masters are not in git (GitHub's 100 MB limit). Re-create them with the commands below.

## Build
Same setup as `../kurzgesagt-minerals/README.md` (Git, Python 3, FFmpeg, Kokoro voice files in `KOKORO_DIR`), plus `pip install -r requirements.txt` (adds `uharfbuzz` for Indian-script shaping).
```
python voiceover.py part1           (repeat for part2 … part7)
python storyboard.py                (storyboard sheets)
python faces.py; python faces_demo.py
python render.py part3 --still 5,20
python render.py part3
python render.py full
python thumbnail.py
```

## Files
- `india_kit.py`: palette, India map (Natural Earth, India point of view, `data/south_asia.json`), HarfBuzz-shaped Indic text, people, rangoli, chakra, diya, chapter badges.
- `faces.py`: respectful flat portraits of Ashoka, Gandhi, Nehru, Patel, Bose, Ambedkar and Modi (blink, breathe, glance; mouths never move).
- `props.py`: monuments, symbols, ships, train, Constitution, lander, charts.
- `boards.py`: storyboard key frames (the visual reference the parts animate).
- `part1.py` … `part7.py`: animated parts. `engine.py`, `audio.py` (with tanpura drone), `render.py`, `voiceover.py`: shared kit.
- `fonts/`: Montserrat + Noto Sans (Devanagari, Bengali, Tamil, Telugu, Gurmukhi) + Noto Naskh Arabic (Urdu), all under the SIL Open Font License.
