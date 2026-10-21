# BrighterMinds Video Studio: dashboard mockups

Static mockups of a dashboard for making the code-rendered science Shorts (based on `ai-images/`).
Nothing is wired up yet. These pages only show the layout and the options.

| Screen | What you do there |
|---|---|
| `01_projects` | All videos with pipeline status; start a new video (topic, format, length, style preset, voice, rules) |
| `02_script` | Edit the script line by line, live total duration, voice and speed, caption highlight words, spoken→shown replacements, fact check |
| `03_scenes` | Shot list, 9:16 preview with safe zones, timeline (parts, shots, voice, captions, SFX, music, post FX), per-shot animation options |
| `04_style` | Palette, type, caption style, sound palette, post effects with before/after, vector art library, rules |
| `05_render` | Render queue (only changed parts re-render), quick stills, loudness check, output files, pre-post checklist, posting kit, save/upload |

Rebuild the PNGs: `sh mockups/shoot.sh` (headless Chromium) → `mockups/out/`.
Thumbnails in `mockups/assets/` are downscaled frames and art from `ai-images/`.
