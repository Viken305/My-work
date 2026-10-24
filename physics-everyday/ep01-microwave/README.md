# Ep. 01 · Why your microwave heats unevenly

9:16 short, about 1:31, narrated, captioned, with sound. Style: the approved 3D kitchen (see `../style-tests`).
Stage: **built**. `python3 film.py` rebuilds the whole film from code -> `out/ep01_microwave.mp4`.

## Story (narration in `script.py`, with fact notes)
1. Hook: scorching hot and ice cold in the same bite (thermal-camera wipe on the food).
2. X-ray of the oven: magnetron, waveguide, pulses bouncing around the cavity; 2,450,000,000 wiggles a second.
3. Dive into the food: lopsided water molecules (δ−/δ+) twist to follow the flipping field; jostling = heat.
4. Myth: it does not cook from the inside out. Potato cross-section in thermal view, 1-2 cm hot rim, heat creeps in.
5. Hot spots: waves bounce, add up and cancel, 3D heat map, hot spots about 6 cm apart.
6. Why the plate spins; stir and let it stand (thermal view evens out).
7. Chocolate experiment: gap 6 cm, x2 = 12 cm, x 2.45 billion/s = 294,000 km/s, about the speed of light.
8. Button: the cat finally shoves the mug off the counter. End card.

Background gags all the way through: the cat nudging the mug towards the edge (and staring at camera),
the toaster launching toast, the robot vacuum bumping into the fridge, the rubber duck by the sink.

## Build
Same setup as `../style-tests` (skia-python, moderngl, opencv-python-headless, kokoro-onnx, soundfile, ffmpeg).
```
python3 voiceover.py              # narration -> build/vo/*.wav + timeline.json
python3 film.py --still 9.8,58.8  # quick frames -> build/stills/
PROCS=3 python3 film.py           # full film -> out/ep01_microwave.mp4
```

## Files
- `script.py`: narration lines + gaps; fact notes. `voiceover.py`: Kokoro TTS, writes the timeline every shot keys off.
- `film.py`: microwave states, x-ray internals, molecule world, potato, chocolate, gags, the 22-shot camera list, renderer.
- `overlay.py`: captions, 3D-anchored labels and brackets, equation cards, thermal HUD, end card.
- `sound.py`: effects on cuts and gags, microwave hum, music beds, mix and loudness.
