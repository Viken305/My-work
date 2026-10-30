# What Happens Inside Your Body During Exercise

## Full video: Beat Drop (`part1.py` … `part7.py`, engine `game.py`)
About 1:44, 9:16. Your workout as a rhythm game: every spoken word is a note that hits the line exactly when it is
said, then flies into the caption line; numbers land as gold notes. The music is a four-on-the-floor track
(`audio.drive`) whose tempo rises level by level, and the lights, highway and runner lock to its beat. Script and
sources: `SCRIPT.md`; title, description, tags: `SHORTS_POST.md`.

| Part | Level | Scene |
|---|---|---|
| part1 | Press Play | Play button pressed, beat drop, equaliser runner assembles, organ tags, level select |
| part2 | 1 · Ignition | Brain signal to the adrenal glands, adrenaline; vessel opens wide; blood-flow mixing desk 20% → 80% |
| part3 | 2 · Air | Lungs as speakers, breaths 12 → 40, air 6 → 100 L/min; blood cells race oxygen to the muscle |
| part4 | 3 · Fuel | ATP battery drains in seconds; sugar and fat reactor recharges it; O2 runs low, acid, the burn |
| part5 | 4 · Max Heart | Runner over an ECG, heart rate locks on 180; four 5 L jugs fill, 4X stamp |
| part6 | 5 · Heat | 25% move / 75% heat bar, runner on fire, thermometer 37 → 38.5 °C, sweat jug to 1 L |
| part7 | Bonus | Mirror-ball brain (endorphins, endocannabinoids), tape-stop + afterburn, stronger heart, LEVEL COMPLETE, loop |

```
for p in 1 2 3 4 5 6 7; do python3 voiceover.py part$p; done
python3 render.py part4 --still 6,12      # check frames
python3 render.py full                    # -> out/full.mp4 + out/full_share.mp4 (not in git)
```

# Style tests

Three out-of-the-box directions for a 9:16 explainer, each with its own animation idea and caption system, rendered
entirely in code (same kit as `../no-sleep`).

| File | What |
|---|---|
| `out/style_frames.png` | All six style frames on one board |
| `out/frame_A1.png` … `frame_C2.png` | The frames at full size (1080×1920) |
| `out/reel_share.mp4` | 20-second style reel: each direction animated with narration and sound (not in git; `python3 render.py reel`) |

| Style | The world | The captions |
|---|---|---|
| **A · Rush Hour** (`city.py`) | Your body is a city at night. The heart is the power station, arteries are red highways, veins blue ones, red blood cells are the traffic. Exercise is rush hour: the heart beats faster, the traffic speeds up, the windows flicker with each pulse. | The narration lights up dot by dot on an overhead **LED highway sign**; key words glow red. Numbers flip on **split-flap boards** (blood pumped 5 → 25 L/min, heart rate 72 → 160). |
| **B · Beat Drop** (`beat.py`) | Your workout as a rhythm game. A runner made of **equaliser bars** pulses to the heart rate, the heart is a speaker cone, stage lights swing on the beat. | Every spoken word is a **note** that slides down a lane and hits the line exactly when it is said ("PERFECT"), then gets thrown up into the caption line. Big numbers arrive as one wide gold note ("180 · MAX POWER"). BPM and combo counters. |
| **C · Fogged Glass** (`micro.py`) | A macro shot of skin behind a **steamed-up gym window**: sweat beads swell out of the pores and roll; water drops on the glass act as real lenses (they show the skin upside down). | A **fingertip wipes each phrase into the fog**, revealing the sharp skin through the letters; the letters drip, then fog over again. Temperature and sweat-rate chips tick up. |

Second frames (`frames2.py`): A2 the muscle works (trucks of glucose and oxygen, CO2 chimneys), B2 the lungs as two
speakers (air in 6 → 100 L/min), C2 inside a muscle fibre (myosin "rowers" pulling actin, ATP coins).

## Facts used
- Cardiac output rises from about 5 L/min at rest to 20–25 L/min in hard exercise (about 4–5×).
- Maximum heart rate is roughly 180–200 BPM for young adults (about 220 minus age).
- Sweat rates commonly reach 1–2 L/hour in hard exercise in the heat; core temperature rises to about 38–39 °C.
- Breathing can rise from about 6 L/min at rest to 100+ L/min; energy use can rise to about 10× resting.

## Build
```
python3 voiceover.py city            # narration (also beat, micro)
python3 render.py city --still 2,4   # stills -> build/city/stills
python3 render.py reel               # the style reel -> out/reel.mp4 + out/reel_share.mp4
python3 frames2.py                   # second frames
python3 board.py                     # the style-frames board
```
