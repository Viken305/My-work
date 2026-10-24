"""Narration for the kitchen test via Kokoro TTS (temporary voice; swap for a real read later).

  python3 kitchen_vo.py   -> build/kitchen/vo/NN.wav + durations.json
Needs the Kokoro model files in KOKORO_DIR (default /tmp/claude-0/voices).
"""
import json, os

import soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.environ.get("KOKORO_DIR", "/tmp/claude-0/voices")
VOICE, SPEED, LANG = "am_michael", 1.12, "en-us"

LINES = [
    ("01", "Ever notice your microwave leaves food scorching hot... and ice cold, in the same bite?"),
    ("02", "That's because the microwaves bounce off the metal walls inside."),
    ("03", "They pile up into a pattern. Some spots get blasted. Others get almost nothing."),
    ("04", "That's why the plate spins. It drags your food through the hot spots."),
]

if __name__ == "__main__":
    out = os.path.join(HERE, "build", "kitchen", "vo")
    os.makedirs(out, exist_ok=True)
    k = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin"))
    durs = {}
    for key, text in LINES:
        samples, sr = k.create(text, voice=VOICE, speed=SPEED, lang=LANG)
        sf.write(os.path.join(out, f"{key}.wav"), samples, sr)
        durs[key] = round(len(samples) / sr, 3)
        print(f"{key} {durs[key]:5.2f}s  {text}")
    json.dump(durs, open(os.path.join(out, "durations.json"), "w"), indent=1)
