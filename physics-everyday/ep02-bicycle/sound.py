"""Ep. 02 soundtrack: narration + a bouncy plucked bed (ducked) + paper and bike foley."""
import os, subprocess

import numpy as np

import audio as A
from kitchen import extra_sfx

BPM = 112


def pluck(f, d=0.9, bright=0.5, seed=0):
    """Karplus-Strong string: a nylon/ukulele-ish pluck."""
    n = int(d * A.SR)
    p = max(2, int(A.SR / f))
    r = np.random.default_rng(seed)
    buf = r.uniform(-1, 1, p)
    out = np.zeros(n)
    k = 0.5 + 0.49 * bright
    for i in range(n):
        j = i % p
        out[i] = buf[j]
        buf[j] = k * buf[j] + (1 - k) * buf[(j + 1) % p] if True else 0
        buf[j] *= 0.996
    return out * np.minimum(1, np.arange(n) / 40)


def bed(d):
    beat = 60 / BPM
    y = np.zeros((int(d * A.SR) + A.SR, 2))
    chords = [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)]
    bass = [65.4, 55.0, 43.65, 49.0]
    cache = {}

    def pl(f, dd, b, s):
        key = (round(f, 1), dd, b)
        if key not in cache:
            cache[key] = pluck(f, dd, b, s)
        return cache[key]
    t, i = 0.0, 0
    patt = [0, 2, 1, 2, 0, 2, 1, 2]
    while t < d:
        bar, step = divmod(i, 8)
        ch = chords[bar % 4]
        f = ch[patt[step]] * (2 if step in (3, 7) else 1)
        A.place(y, t, A.st(pl(f, 0.7, 0.35, i % 5) * 0.32, (step % 2 - 0.5) * 0.5))
        if step in (0, 4):
            A.place(y, t, A.st(pl(bass[bar % 4], 1.2, 0.2, 3) * 0.6))
        if step in (2, 6):  # soft shaker on the off-beat
            sh = A.fft_filter(A.noise(0.08, i), 5000, 12000) * A.env(0.08, 0.004, 0.03)
            A.place(y, t, A.st(sh * 0.12, 0.3))
        t += beat / 2
        i += 1
    y = y[: int(d * A.SR)]
    fade = np.minimum(1, np.minimum(A.T(d) / 0.3, (d - A.T(d)) / 1.0))[:, None]
    return y * np.clip(fade, 0, 1)


def sfx(kind):
    if kind == "freewheel":  # a hub ticking over, 2 s loop
        d = 2.0
        y = np.zeros(int(d * A.SR))
        for k in np.arange(0, d, 1 / 15):
            c = A.fft_filter(A.noise(0.006, int(k * 100)), 2500, 9000) * A.env(0.006, 0.0003, 0.002)
            A.place1(y, k, c, 0.5)
        return A.st(y * 0.5)
    if kind == "whirr":
        d = 4.0
        t = A.T(d)
        y = A.fft_filter(A.noise(d, 4), 300, 1800) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t))
        return A.st(A.norm(y) * 0.5, 0, 0.01)
    if kind == "scribble":
        d = 0.32
        t = A.T(d)
        y = A.fft_filter(A.noise(d), 1800, 7000) * (0.5 + 0.5 * np.sin(2 * np.pi * 24 * t)) * np.sin(np.pi * t / d)
        return A.st(A.norm(y) * 0.6, 0.1)
    if kind == "tape":
        d = 0.35
        t = A.T(d)
        y = A.fft_filter(A.noise(d), 900, 6000) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 60 * t))) * np.exp(-t * 6)
        return A.st(A.norm(y) * 0.5, -0.2)
    if kind == "squeak":  # the mouse
        d = 0.18
        t = A.T(d)
        y = np.sin(2 * np.pi * (2600 + 900 * np.sin(np.pi * t / d)) * t) * np.sin(np.pi * t / d) ** 2
        return A.st(y * 0.3, 0.4)
    if kind in ("paper_whoosh", "paper_slap", "stamp", "pop", "swish", "whoosh"):
        return A.SFX(kind)
    return extra_sfx(kind)


def events(F):
    ws = F.words_of("03")
    ev = [(0.0, "whoosh", 0.6), (0.9, "ding", 0.35)]
    ev += [(s, "paper_slap", 0.8) for s in (ws[0][1], ws[2][1], ws[3][1])]
    ev += [(F.word_t("03", "fall") + 0.02, "swish", 0.4)]
    for t0 in (F.T_MYTH, F.T_JONES):
        ev += [(t0 - 0.05, "paper_whoosh", 0.8), (t0 + 0.25, "paper_slap", 0.5)]
    ev += [(F.T_MYTH + 1.0, "squeak", 1.0), (F.T_MYTH + 2.6, "squeak", 0.9)]
    ev += [(F.T_GYRO, "stamp", 0.7), (F.T_NOPE - 0.05, "scribble", 0.9), (F.T_NOPE + 0.07, "scribble", 0.9), (F.T_NOPE + 0.12, "paper_slap", 0.9)]
    ev += [(F.T_1970 - 0.05, "stamp", 0.6), (F.T_EXTRA, "tape", 0.7), (F.T_EXTRA + 0.05, "scribble", 0.5), (F.T_EXTRA - 0.15, "swish", 0.4),
           (F.T_BACK - 0.1, "swish", 0.5), (F.T_BACK + 0.3, "tape", 0.5), (F.T_CANCEL - 0.05, "paper_slap", 0.8), (F.T_CANCEL - 0.1, "swish", 0.4),
           (F.T_RIDE + 0.5, "stamp", 0.6), (F.T_RIDE + 1.1, "ding", 0.4)]
    return ev


def render_audio(out_wav, F):
    here = os.path.dirname(os.path.abspath(F.__file__))
    n = int(F.DURATION * A.SR)
    fx = np.zeros((n, 2))
    for t0, kind, g in events(F):
        A.place(fx, t0, sfx(kind), g)
    fw = sfx("freewheel")
    for a, b in ((0.0, F.T_MYTH), (F.T_JONES, F.DURATION)):
        seg = np.tile(fw, (int((b - a) / 2.0) + 1, 1))[: int((b - a) * A.SR)].copy()
        A.place(fx, a, seg, 0.35)
    wr = sfx("whirr")
    A.place(fx, F.T_MYTH, wr[: int((F.T_JONES - F.T_MYTH) * A.SR)], 0.25)
    vo = np.zeros(n)
    for key, item in F.TL.items():
        A.place1(vo, item["start"], A.load_vo(os.path.join(here, "build", "vo", f"{key}.wav")))
    vo = A.norm(vo, 0.9)
    music = bed(F.DURATION)
    e = A.follower(vo)
    e = np.clip(e / (e.max() + 1e-9) * 2.5, 0, 1)
    mix = A.st(vo) * 0.78 + music * 0.42 * (1 - 0.55 * e)[:, None] + fx * 0.55 * (1 - 0.3 * e)[:, None]
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    import soundfile as sf
    raw = out_wav.replace(".wav", "_raw.wav")
    sf.write(raw, mix.astype(np.float32), A.SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9", "-ar", str(A.SR), out_wav], check=True)
    return out_wav
