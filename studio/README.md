# BrighterMinds Video Studio

A dashboard for making the code-rendered science Shorts. It runs on your computer and you open it in a browser.

```
pip install -r studio/requirements.txt      # once (ffmpeg must be installed too)
python3 studio/server.py                    # then open http://localhost:8765
```

Narration uses the Kokoro voice model. Download `kokoro-v1.0.onnx` and `voices-v1.0.bin` from
https://github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0) into one folder and point to it:
`export KOKORO_DIR=/path/to/that/folder`.

## What you can do

| Screen | |
|---|---|
| **Projects** | All videos with a progress bar (script, voice, scenes, render, post). Start a new video from a topic. |
| **1 Script & Voice** | Edit any line; add or delete lines; live total length. Click words to highlight them amber (your words) or violet (the model). Pick the narrator, speed, pause between lines, extra pause before a line. Only changed lines get a new voice. "Say it → show it" (spoken "seven hundred…" shown as "768"). |
| **2 Scenes & Timeline** | Shots, a 9:16 player with the safe zones, and a timeline of parts, shots, voice, highlights, the words the animation is pinned to, sound effects and music. "Frame here" renders the exact frame at the playhead. Per-sound volumes; hear a part's sound mix; render a part. |
| **3 Style & Sound** | Colours, caption size / words per caption / height, glow, grain, colour fringing, glitch, motion blur, the sound mix levels and loudness target, every music bed and sound effect, the vector art library. "Render frame" previews a frame with the new settings. |
| **4 Render & Publish** | Draft (fast) or final quality. Only parts whose inputs changed are rendered again. Job queue with progress, logs and Stop. Files, loudness check, a pre-post checklist, the posting kit (title, description, tags, pinned comment), version history with restore, and Save to GitHub (code and settings only, never videos). |

Everything you change is saved to the project's `project.json` automatically (Ctrl+S saves at once), and every save keeps
a copy you can restore.

## How it fits together

* `studio/server.py` (standard library only) serves the app in `studio/app/` and runs the project's own tools as
  background jobs: `voiceover.py`, `render.py`, `thumbnails.py`, `storyboard.py`.
* Each video folder with a `project.json` is a studio project (today: `ai-images/`). Its engine reads all settings from
  that file (`project.py`), and `inspect_parts.py` reports timings, pinned words, sounds and what is out of date.
* The animation of each part is code (`partN.py`). If you edit a line so it no longer contains a word the animation is
  pinned to (underlined in the script), the scene falls back to the middle of the line and the dashboard warns you.
  Lines the animation uses can be edited but not deleted.
* New things (a new kind of animation, a new drawing, the scenes for a brand-new topic) are code: ask Claude, and they
  show up in the dashboard as options.

`mockups/` holds the first design pictures of this dashboard.
