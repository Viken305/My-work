# WellWithAll Energy: brand reel

A 12.5 s vertical Reel (1080x1920, 30 fps) for WellWithAll Energy. It follows the sound and edit of the
Henki brand-identity reel (@bymyno_ / motion @eun.wip). Everything, music included, is generated from code.

    python3 render.py                 # -> out/wellwithall_energy_reel.mp4
    python3 render.py --audio         # soundtrack only -> build/mix.wav
    python3 render.py --still 2.3,8.2 # check frames -> build/stills

Needs: numpy, skia-python, pillow, soundfile, ffmpeg. Brand assets in `source/` come from wellwithall.com.
The typeface is Poppins (the site's font, OFL), in `fonts/`.

## What was taken from the reference

| Reference (measured) | This reel |
|---|---|
| ~120 BPM, deep tuned 808 kick (~62 Hz) | 120 BPM, kick that dives onto ~52 Hz |
| 0–7 s: kicks off the beat, under a wobbly chopped vocal-like hook | Kicks on 16ths 0/6/10 and 0/3/6/11/14, formant "vocal chop" hook with vibrato |
| A cut about every 0.5 s, each one with a sound | `film.CUTS` drives a pop on every cut and a zoom punch on every frame cut |
| 6.5–7.6 s break: bass gone, held tone slides down, zig-zag riser | 7–8 s: "REAL FRUIT" break, vowel slides E5 down a 5th, zig-zag riser + clap roll |
| Steady kick from 7.8 s as the product appears | Drop at 8.0 s: a can lands on every beat, claps on 2 and 4 |
| Hi-frequency bursts at 9.3 and 10.3 s on transitions | Crashes at 8.0, 10.0 (collage) and 11.0 (end card) |
| −14 LUFS, compressed, mostly mono | −14 LUFS, soft-clipped and limited, bass in the centre |

## Timeline

| t (s) | Picture | Sound |
|---|---|---|
| 0.0 | Starbursts: strawberry, pineapple, peach, mango (a cut per beat) | Syncopated groove, fruit blips |
| 2.0 | Logo + fruit stickers, ENERGY pill at 2.5 | Sparkle chime, sticker blips |
| 3.0 | FEEL-GOOD / ENERGY, / ANYTIME | Can crack + fizz, swish + thump per word |
| 4.0 | The four product photos with claim badges | Shutter + blip per photo |
| 6.0 | Claim stack jumping every eighth note | Swish per jump |
| 7.0 | Break: REAL FRUIT, lemon sinks, then zooms in | Bass drops out, pitch slide, riser |
| 8.0 | Drop: a can for each flavour | Steady kick on every beat, crash |
| 10.0 | Photo collage, then 4-can line-up | Crash, card swishes, rising blips |
| 11.0 | End card: logo, tagline, retailers, URL | Final hit + chord ring-out |

Claims and the † disclaimer use the wording on wellwithall.com. Check them with the brand before posting.
