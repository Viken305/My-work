# 72 Hours Without Sleep

A 9:16 YouTube Short / Reel (2:16) about what happens to your body at 24, 48 and 72 hours without sleep, rendered
entirely in code: vector animation, captions, music and sound effects. One character, Sam, through one long night.

| File | What |
|---|---|
| `out/full_share.mp4` | **The Short**, ready to post (not in git; rebuild with `python3 render.py full`) |
| `out/storyboard.png` | Storyboard: 15 key frames with timecodes |
| `out/thumb_short.png` | Thumbnail (1080×1920, split face; `thumbs.py` also makes `thumb_toothpicks.png` and `thumb_wide.png`) |
| `out/captions_en.srt` | Captions to upload with the video |
| `SHORTS_POST.md` | Title, description, sources, tags, pinned comment |
| `SCRIPT.md` | Narration and fact sheet with sources |
| `STYLE_GUIDE.md` | The "Night Shift" look: palettes per act, Sam, type, captions, sound |

| Part | What | Length |
|---|---|---|
| 1 | Hook: the eye that won't close (eye darts, lid fights, heartbeat), title slam | 0:09 |
| 2 | Hours 0–21: Sam, the adenosine jar, coffee, the 04:00 body-clock low | 0:25 |
| 3 | Hour 24: the falling-mug gag, 0.10 % alcohol, amygdala +60 %, memory −40 %, hunger hormones | 0:35 |
| 4 | Hours 36–48: body on alarm, beta-amyloid +5 %, microsleeps, the road | 0:35 |
| 5 | Hour 72: hallucinations, the 1964 record, recovery, 7–9 hours, "remember the jar" | 0:31 |

`python3 render.py test20` renders the 21-second test cut (hook + hour 24 to the driving limit).

## Build
Needs Python 3, FFmpeg and `pip install -r requirements.txt` (on Linux servers also `libegl1` for Skia and
`espeak-ng` for word timing).
Narration uses Kokoro TTS: download `kokoro-v1.0.onnx` and `voices-v1.0.bin` from
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 and set `KOKORO_DIR` to that folder.
```
python3 voiceover.py part1            # narration (repeat for part2 … part5)
python3 render.py part3 --still 5,12  # quick stills -> build/part3/stills
python3 render.py part3               # one part -> out/part3.mp4 + out/part3_share.mp4
python3 render.py full                # all parts + one soundtrack -> out/full.mp4 + out/full_share.mp4
python3 extras.py storyboard          # -> out/storyboard.png (also: thumb, srt)
```

## Files
- `film.py`: the Night Shift kit (act palettes, Sam's rig, HUD, hour slams, blink wipes, rooms, the jar, brain,
  hormone meters, x-ray body, shadow figure, bed). `part1.py` … `part5.py`: the scenes.
- `premium.py`: motion blur, bloom, grain, plus the fatigue post (wobble and RGB split) and a sharp overlay pass.
- `audio.py`: synthesised effects and music beds (new here: pour, whisper, car pass, rumble strip, horn, fridge, the
  detuning "night" pad, and music mutes for microsleeps). `typo.py`: word-synced captions. `timing.py`, `engine.py`,
  `render.py`, `voiceover.py`: shared kit from `../deep-hole`.
