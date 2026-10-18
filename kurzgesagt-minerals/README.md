# How the Earth Makes Crystals

A Kurzgesagt-style explainer (3:38), rendered entirely in code: vector art, animation, music and sound effects.
See `STORYBOARD.md` for the original plan and `script.py` for the final narration.

## Watch
| File | What |
|---|---|
| `out/full_share.mp4` | **The whole film**, preview quality |
| `out/full_youtube.mp4` | Higher-quality upload version (local only, too big for git; re-encode from `out/full.mp4`) |
| `out/part1_share.mp4` … `part6_share.mp4` | Each part on its own |
| `out/styleframes/board.png` | Style frames |

| Part | Scenes | Length |
|---|---|---|
| 1 | Hook + What is a mineral? | 0:40 |
| 2 | Recipe 1: Fire | 0:36 |
| 3 | Recipe 2: Water | 0:40 |
| 4 | Recipe 3: Pressure | 0:30 |
| 5 | Recipe 4: Life | 0:34 |
| 6 | Deep time + outro | 0:38 |

Full-quality masters (100–700 MB) are **not** in git (GitHub's 100 MB limit). Re-create them with the commands below.

## Build on any computer
1. Install **Git**, **Python 3** and **FFmpeg**.
2. Get the code:
   ```
   git clone https://github.com/viken305/my-work.git
   cd my-work
   git checkout claude/kurzgesagt-style-analysis-yc4rv9
   cd kurzgesagt-minerals
   pip install -r requirements.txt
   ```
   (On Linux servers without a desktop, also install `libegl1` for Skia.)
3. Narration (temporary computer voice): download `kokoro-v1.0.onnx` and `voices-v1.0.bin` from
   https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 into a folder, then
   ```
   set KOKORO_DIR=C:\path\to\folder        (Windows)
   export KOKORO_DIR=/path/to/folder        (Mac / Linux)
   python voiceover.py part1                (repeat for part2 … part6)
   ```
   Using your own voice instead: record each line from `script.py` and save it as
   `build/<part>/vo/<KEY>.wav` (e.g. `build/part2/vo/F3.wav`), then re-render.
4. Render:
   ```
   python render.py part3 --still 5,12,20   # quick check frames -> build/part3/stills
   python render.py part3                   # one part -> out/part3.mp4 + out/part3_share.mp4
   python render.py full                    # whole film -> out/full.mp4 + out/full_share.mp4
   python styleframes.py                    # style frames
   ```
   One part takes ~3 minutes on a 4-core machine.

## Files
- `script.py`: all narration lines, by part.
- `part1.py` … `part6.py`: each part's scenes and timeline (narration start times in `VO`, sounds in `sfx_events`, chords in `MUSIC`).
- `engine.py`: art kit (palette, easing, glow, atoms, the bird, cubes, grain).
- `common.py`: shared helpers (word timing, recipe title badges, fades, tags).
- `styleframes.py`: style frames + shared crystal/icon drawings.
- `audio.py`: procedural music + SFX, mixed and ducked under the narration.
- `render.py`: renders parts and the full film with one continuous soundtrack.
- `voiceover.py`: temporary Kokoro TTS narration.

## Vertical 9:16 version
`python3 vertical.py` turns `out/full.mp4` into `out/vertical.mp4` (1080x1920): the whole film in the middle, a blurred fill behind it, a title on top and word-by-word captions from the narration underneath.
`python3 shorts.py` then cuts `out/vertical.mp4` to a 2:55 YouTube Short (`out/short.mp4`), dropping three side-trips (glass, diamonds rising, the oldest zircon).
