"""Narration via Kokoro TTS. Voice, speed and language come from project.json.

Usage: python3 voiceover.py part1            -> build/part1/vo/<line>.wav + durations.json (only lines that changed)
       python3 voiceover.py part1 --all      -> re-voice every line of the part
       python3 voiceover.py part1 --lines H2,H3
       python3 voiceover.py --preview af_heart 1.05 "text"  -> build/_preview/<voice>_<speed>.wav
Needs the Kokoro model files; set KOKORO_DIR (default /tmp/claude-0/voices).
A line is re-voiced when its text or the voice settings changed (hashes in build/<part>/vo/meta.json).
"""
import hashlib, json, os, sys

import soundfile as sf

from project import P
from script import PARTS

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.environ.get("KOKORO_DIR", "/tmp/claude-0/voices")


def kokoro():
    from kokoro_onnx import Kokoro
    return Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin"))


def line_hash(text, v=None):
    v = v or P["voice"]
    return hashlib.sha1(f'{v["name"]}|{v["speed"]}|{v["lang"]}|{text}'.encode()).hexdigest()[:12]


def stale_lines(part):
    """Line keys of `part` whose clip is missing or was made from different text/voice settings."""
    out = os.path.join(HERE, "build", part, "vo")
    meta = _read(os.path.join(out, "meta.json"))
    return [k for k, text in PARTS[part]
            if meta.get(k) != line_hash(text) or not os.path.exists(os.path.join(out, f"{k}.wav"))]


def _read(path):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return {}


def voice_part(part, lines=None):
    v = P["voice"]
    out = os.path.join(HERE, "build", part, "vo")
    os.makedirs(out, exist_ok=True)
    todo = lines if lines is not None else stale_lines(part)
    meta, durs = _read(os.path.join(out, "meta.json")), _read(os.path.join(out, "durations.json"))
    k = kokoro() if todo else None
    for i, (key, text) in enumerate(PARTS[part]):
        if key in todo:
            samples, sr = k.create(text, voice=v["name"], speed=v["speed"], lang=v["lang"])
            sf.write(os.path.join(out, f"{key}.wav"), samples, sr)
            durs[key] = round(len(samples) / sr, 3)
            meta[key] = line_hash(text)
            print(f"{key:4s} {durs[key]:5.2f}s  {text}", flush=True)
    keys = [key for key, _ in PARTS[part]]
    durs = {key: durs[key] for key in keys if key in durs}
    meta = {key: meta[key] for key in keys if key in meta}
    json.dump(meta, open(os.path.join(out, "meta.json"), "w"), indent=1)
    if todo or not os.path.exists(os.path.join(out, "durations.json")):
        json.dump(durs, open(os.path.join(out, "durations.json"), "w"), indent=1)
    print(f"{part}: {len(todo)} line(s) voiced", flush=True)


def preview(name, speed, text):
    d = os.path.join(HERE, "build", "_preview")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{name}_{float(speed):.2f}_{hashlib.sha1(text.encode()).hexdigest()[:8]}.wav")
    if not os.path.exists(path):
        samples, sr = kokoro().create(text, voice=name, speed=float(speed), lang=P["voice"]["lang"])
        sf.write(path, samples, sr)
    print(path)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--preview":
        preview(*args[1:4])
    else:
        part = args[0] if args else "part1"
        if "--all" in args:
            voice_part(part, [k for k, _ in PARTS[part]])
        elif "--lines" in args:
            voice_part(part, args[args.index("--lines") + 1].split(","))
        else:
            voice_part(part)
