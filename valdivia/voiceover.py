"""Narration via Kokoro TTS (same voice as krakatoa/).

Usage: python3 voiceover.py part1     -> build/part1/vo/NN.wav + durations.json
Needs the Kokoro model files; set KOKORO_DIR (default /tmp/claude-0/voices).
"""
import json, os, sys

import soundfile as sf
from kokoro_onnx import Kokoro

from script import PARTS

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.environ.get("KOKORO_DIR", "/tmp/claude-0/voices")
VOICE, SPEED, LANG = "af_heart", 1.05, "en-us"   # sample B (US female)

if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "part1"
    out = os.path.join(HERE, "build", part, "vo")
    os.makedirs(out, exist_ok=True)
    k = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin"))
    durs = {}
    for i, (key, text) in enumerate(PARTS[part]):
        samples, sr = k.create(text, voice=VOICE, speed=SPEED, lang=LANG)
        sf.write(os.path.join(out, f"{key}.wav"), samples, sr)
        durs[key] = round(len(samples) / sr, 3)
        print(f"{key:4s} {durs[key]:5.2f}s  {text}")
    json.dump(durs, open(os.path.join(out, "durations.json"), "w"), indent=1)
