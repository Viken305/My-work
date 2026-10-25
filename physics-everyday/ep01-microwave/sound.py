"""Soundtrack: narration + music bed (ducked) + synthesized effects on every cut, pop and gag."""
import os, subprocess

import numpy as np

import audio as A
from kitchen import extra_sfx


def sfx(kind):
    if kind == "beep":
        d = 0.9
        t = A.T(d)
        y = np.zeros(len(t))
        for k in range(3):
            m = (t >= k * 0.28) & (t < k * 0.28 + 0.16)
            y += np.sin(2 * np.pi * 2000 * t) * m * 0.5
        return A.st(y)
    if kind == "flip":
        d = 0.08
        t = A.T(d)
        y = np.sin(2 * np.pi * (300 + 900 * t / d) * t) * np.exp(-t * 40)
        return A.st(y * 0.5, 0.0)
    return extra_sfx(kind)


def events(F):
    C = F.C
    ev = [(0.0, "whoosh", 0.7), (2.35, "swish", 0.5), (3.1, "tick_roll", 0.35), (5.8, "swish", 0.6), (6.7, "reverse_swell", 0.5),
          (8.05, "swish", 0.5), (C("03", 1.6), "pop", 0.6), (11.55, "swish", 0.45), (12.4, "riser", 0.25), (12.9, "pop", 0.5),
          (15.25, "swish", 0.5), (15.5, "pop", 0.4), (18.85, "swish", 0.5), (C("05", 1.0), "counter", 0.45),
          (23.95, "whoosh", 0.7), (24.05, "low_hit", 0.45), (C("06", 1.4), "pop", 0.5), (C("06", 3.6), "pop", 0.5),
          (30.1, "swish", 0.45), (35.1, "riser", 0.3), (C("08", 0.1), "stamp", 0.6), (35.9, "whoosh", 0.4),
          (37.15, "whoosh", 0.6), (37.3, "tick_roll", 0.35), (C("09", 1.0), "stamp", 0.6), (C("09", 3.3), "pop", 0.5),
          (C("09", 4.6), "pop", 0.4), (46.55, "swish", 0.5), (47.1, "door_clunk", 0.8), (47.45, "pop", 0.7),
          (48.3, "riser", 0.22), (51.05, "swish", 0.45), (C("11", 0.3), "pop", 0.4), (C("11", 2.4), "pop", 0.4),
          (55.55, "swish", 0.5), (55.85, "low_hit", 0.45), (56.6, "pop", 0.35), (56.8, "pop", 0.35), (57.2, "pop", 0.35),
          (57.4, "toast_pop", 0.3), (58.35, "swish", 0.45), (58.5, "stamp", 0.45), (59.7, "swish", 0.4),
          (60.85, "swish", 0.5), (65.35, "swish", 0.45), (65.6, "tick_roll", 0.3), (66.3, "pop", 0.5), (68.5, "pop", 0.5),
          (70.75, "swish", 0.45), (71.5, "whoosh", 0.4), (72.0, "toast_pop", 0.28), (72.25, "paper_whoosh", 0.5),
          (73.65, "swish", 0.45), (74.0, "counter", 0.35), (75.75, "beep", 0.45), (76.65, "swish", 0.45),
          (77.0, "paper_slap", 0.5), (77.6, "pop", 0.45), (79.5, "pop", 0.45), (80.8, "pop", 0.45), (83.15, "whoosh", 0.6),
          (83.3, "pop", 0.5), (83.9, "trailer_hit", 0.45), (86.35, "whoosh", 0.7), (86.85, "low_hit", 0.3),
          (F.SHOVE, "swish", 0.3), (F.CRASH, "crash", 0.65), (88.75, "swish", 0.35), (89.3, "ding", 0.5), (89.6, "low_hit", 0.35)]
    # each flip of the field in the molecule shots
    t, half = C("07"), 0.5 / F.FIELD_HZ
    while t < 37.0:
        ev.append((t, "flip", 0.18))
        t += half
    ev += [(t, "bump", 0.1) for t in np.arange(1.43, F.DURATION, 2.6)]
    return ev


def render_audio(out_wav, F):
    here = os.path.dirname(os.path.abspath(F.__file__))
    n = int(F.DURATION * A.SR)
    fx = np.zeros((n, 2))
    cache = {}
    for t0, kind, g in events(F):
        if kind not in cache or kind in ("swish", "whoosh", "paper_whoosh", "tick"):
            cache[kind] = sfx(kind)
        A.place(fx, t0, cache[kind], g)
    hum = sfx("hum")
    for a, b in ((0.0, 24.0), (73.7, 75.75)):
        seg = np.tile(hum, (int((b - a) / 6.0) + 1, 1))[: int((b - a) * A.SR)].copy()
        k = int(0.15 * A.SR)
        seg[:k] *= np.linspace(0, 1, k)[:, None]
        seg[-k:] *= np.linspace(1, 0, k)[:, None]
        A.place(fx, a, seg, 0.3)
    vo = np.zeros(n)
    for key, item in F.TL.items():
        A.place1(vo, item["start"], A.load_vo(os.path.join(here, "build", "vo", f"{key}.wav")))
    vo = A.norm(vo, 0.9)
    music = np.zeros((n, 2))
    A.place(music, 0.0, A.bed("wonder", 47.0, 2), 1.0)
    A.place(music, 46.6, A.bed("wonder", 40.5, 3), 1.0)
    A.place(music, 86.4, A.bed("end", F.DURATION - 86.4 + 1.0, 4), 1.2)
    e = A.follower(vo)
    e = np.clip(e / (e.max() + 1e-9) * 2.5, 0, 1)
    mix = A.st(vo) * 0.75 + music * 0.38 * (1 - 0.6 * e)[:, None] + fx * 0.55 * (1 - 0.3 * e)[:, None]
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    import soundfile as sf
    raw = out_wav.replace(".wav", "_raw.wav")
    sf.write(raw, mix.astype(np.float32), A.SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9", "-ar", str(A.SR), out_wav], check=True)
    return out_wav
