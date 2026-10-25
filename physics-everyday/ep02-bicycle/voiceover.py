"""Narration via Kokoro TTS (same voice as Ep. 01).

  python3 voiceover.py   -> build/vo/NN.wav + timeline.json (start time of every line)
Needs the Kokoro model files in KOKORO_DIR (default /tmp/claude-0/voices).
"""
import json, os

import soundfile as sf
from kokoro_onnx import Kokoro

from script import GAP, LINES

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.environ.get("KOKORO_DIR", "/tmp/claude-0/voices")
VOICE, SPEED, LANG = "am_michael", 1.12, "en-us"
LEAD = 0.3

if __name__ == "__main__":
    out = os.path.join(HERE, "build", "vo")
    os.makedirs(out, exist_ok=True)
    k = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin"))
    tl, t = {}, LEAD
    for key, text in LINES:
        t += GAP.get(key, 0.25) if key != "01" else 0.0
        samples, sr = k.create(text, voice=VOICE, speed=SPEED, lang=LANG)
        sf.write(os.path.join(out, f"{key}.wav"), samples, sr)
        d = len(samples) / sr
        tl[key] = dict(start=round(t, 3), dur=round(d, 3), text=text)
        print(f"{key} {t:6.2f} +{d:5.2f}  {text}")
        t += d
    json.dump(tl, open(os.path.join(out, "timeline.json"), "w"), indent=1)
    print(f"total {t:.2f}s")
