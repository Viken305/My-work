"""Ep. 04 soundtrack: narration first; a warm, wondering synth score (pads, soft arpeggios, glassy bells)
and playful UI-style effects (whooshes on every camera journey, bloops on labels, sparkles on photons)."""
import math
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "style-tests"))
import audio as A  # noqa: E402

SR = A.SR


def saw_pad(chord, d, seed=0, bright=1400):
    t = A.T(d)
    r = np.random.default_rng(seed)
    y = np.zeros(len(t))
    for f in chord:
        for det in (-0.004, 0.0, 0.004):
            ph = r.uniform(0, 1)
            y += 2 * (((f * (1 + det)) * t + ph) % 1.0) - 1
    y = A.fft_filter(y, 60, bright)
    e = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.2)
    return y * np.clip(e, 0, 1) / (len(chord) * 3)


def bell(f, d=2.5, vel=1.0):
    t = A.T(d)
    y = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * dec) for k, a, dec in ((1, 1, 1.6), (2.76, 0.4, 3.5), (5.4, 0.15, 6)))
    return y * np.minimum(1, t / 0.002) * vel


def pluck(f, d=0.6, vel=1.0):
    t = A.T(d)
    y = sum(np.sin(2 * np.pi * f * k * t) / k for k in (1, 2, 3)) * np.exp(-t * 7)
    return y * np.minimum(1, t / 0.003) * vel


def score(F):
    d = F.DURATION
    y = np.zeros((int(d * SR) + SR * 4, 2))
    # A major lydian-ish wonder: Amaj7 - F#m9 - Dmaj7#11 - E6
    prog = [(110.0, 164.8, 207.7, 277.2), (92.5, 138.6, 164.8, 220.0), (73.4, 146.8, 185.0, 220.0), (82.4, 123.5, 164.8, 207.7)]
    bpm = 92
    beat = 60 / bpm
    bar = beat * 4
    t, i = 0.2, 0
    sunset0, mars0 = F.SEG["sunset"], F.SEG["mars"]
    while t < d - 1:
        ch = prog[i % 4]
        mood = 1.0
        A.place(y, t, A.st(saw_pad(ch, bar * 2 + 1.2, i, 900 if t < F.SEG["sun"] else 1500), (i % 2 - 0.5) * 0.4, 0.014), 0.5)
        if t > F.SEG["sun"] - 0.5:
            # arpeggio once we are moving (16ths, soft)
            notes = [ch[1] * 2, ch[2] * 2, ch[3] * 2, ch[2] * 4]
            for k in range(16):
                if t > sunset0 - 1 and t < mars0 and k % 2:
                    continue
                A.place(y, t + k * beat / 4, A.st(pluck(notes[k % 4], 0.5, 0.35 + 0.1 * (k % 4 == 0)), (k % 4 - 1.5) * 0.3), 0.3 * mood)
        if i % 2 == 0:
            for k, f in enumerate((ch[3] * 4, ch[2] * 4)):
                A.place(y, t + k * bar * 0.75, A.st(bell(f, 2.5, 0.5), (k - 0.5) * 0.6), 0.25)
        A.place(y, t, A.st(pluck(ch[0] / 2, 1.6, 0.9)), 0.5)
        t += bar
        i += 1
    y = y[: int(d * SR)]
    fade = np.minimum(1, np.minimum(A.T(d) / 1.0, (d - A.T(d)) / 2.0))[:, None]
    return y * np.clip(fade, 0, 1)


def sfx(kind, seed=0):
    r = np.random.default_rng(seed)
    if kind == "bloop":
        d = 0.18
        t = A.T(d)
        f = 500 + 500 * (t / d)
        return A.with_tail(A.st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * 0.6, r.uniform(-0.3, 0.3)), 0.15, 0.6, 6000)
    if kind == "sparkle":
        d = 0.9
        y = np.zeros(int(d * SR))
        for k in range(7):
            A.place1(y, k * 0.06, bell(r.uniform(2200, 4200), 0.6, 0.25))
        return A.st(y * 0.5, r.uniform(-0.4, 0.4), 0.02)
    if kind == "zoom":
        d = 1.0
        t = A.T(d)
        x = A.sweep(A.noise(d, seed), lambda u: 200 + 2500 * u, lambda u: 900 + 7000 * u) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
        return A.st(A.norm(x) * 0.6, 0, 0.01)
    if kind == "tick":
        return A.st(pluck(1800, 0.05, 0.5), 0.2)
    if kind == "blip":
        return A.st(pluck(r.uniform(900, 1500), 0.12, 0.5), r.uniform(-0.6, 0.6))
    if kind == "hum":
        d = 3.0
        t = A.T(d)
        y = np.sin(2 * np.pi * 220 * t + 3 * np.sin(2 * np.pi * 5 * t)) * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.5)
        return A.st(y * 0.25, 0, 0.01)
    if kind == "wobble":
        d = 1.2
        t = A.T(d)
        y = np.sin(2 * np.pi * (300 + 60 * np.sin(2 * np.pi * 14 * t)) * t) * np.exp(-t * 2.5)
        return A.st(y * 0.4, 0, 0.01)
    return A.SFX(kind)


def render_audio(out_wav, F):
    here = os.path.dirname(os.path.abspath(F.__file__))
    n = int(F.DURATION * SR)
    fx = np.zeros((n, 2))
    S, wt, st = F.SEG, F.wt, F.st
    ev = [(wt("02", "up") - 0.1, "zoom", 0.9), (st("03") - 0.1, "swish", 0.5), (st("03") + 0.45, "sparkle", 0.9),
          (st("03") + 1.0, "bloop", 0.7), (st("04") - 0.1, "swish", 0.4), (wt("04", "long"), "wobble", 0.6), (wt("04", "short"), "blip", 0.7),
          (wt("04", "long"), "bloop", 0.5), (wt("04", "short"), "bloop", 0.5), (S["travel"], "whoosh", 0.8), (wt("05", "hit") - 0.2, "low_hit", 0.6),
          (st("06") + 0.1, "bloop", 0.6), (S["air"] - 0.1, "zoom", 0.9), (wt("07", "nitrogen"), "bloop", 0.6), (wt("07", "oxygen"), "bloop", 0.6),
          (wt("07", "tiny") - 0.2, "descend", 0.4), (wt("07", "thousand"), "bloop", 0.6), (st("08") - 0.4, "zoom", 0.6),
          (wt("08", "shakes"), "wobble", 0.7), (wt("08", "every") - 0.3, "sparkle", 0.8), (wt("09", "scattering"), "sparkle", 0.6),
          (wt("09", "trick") - 0.3, "swish", 0.5), (st("10") - 0.2, "swish", 0.4), (wt("10", "five"), "bloop", 0.8),
          (S["pinball"], "zoom", 0.7), (S["bluesky"], "zoom", 0.7), (wt("12", "blue", 1), "sparkle", 0.8), (S["violet"] + 0.4, "bloop", 0.7),
          (st("14") - 0.3, "swish", 0.5), (wt("14", "some") - 0.3, "swish", 0.5), (wt("14", "eyes") - 0.4, "swish", 0.5),
          (st("15"), "reverse_swell", 0.4), (st("16") - 0.4, "zoom", 0.6), (wt("16", "forty"), "bloop", 0.7),
          (wt("17", "orange") - 1.2, "zoom", 0.5), (S["mars"], "whoosh", 0.6), (wt("18", "dusty") - 0.6, "zoom", 0.7),
          (wt("18", "blue"), "sparkle", 0.7), (S["end"], "zoom", 0.6), (st("20") - 0.2, "sparkle", 0.9), (st("20"), "low_hit", 0.4)]
    k = st("05") + 0.2
    while k < wt("05", "hit"):
        ev.append((k, "tick", 0.5))
        k += 0.25
    rr = np.random.default_rng(2)
    tb = wt("11", "blue")
    for tt in np.arange(tb, tb + 6.0, 0.23):
        ev.append((float(tt + rr.uniform(-0.05, 0.05)), "blip", 0.35))
    for i, (t0, kind, g) in enumerate(ev):
        A.place(fx, t0, sfx(kind, i), g)
    vo = np.zeros(n)
    for key, item in F.TL.items():
        A.place1(vo, item["start"], A.load_vo(os.path.join(here, "build", "vo", f"{key}.wav")))
    vo = A.norm(vo, 0.9)
    music = score(F)
    rms = lambda x: np.sqrt(np.mean(np.square(x))) + 1e-12
    speech = np.abs(vo) > 0.02
    v_rms = rms(vo[speech])
    music *= (v_rms * 10 ** (-16 / 20)) / rms(music[np.any(music != 0, axis=1)])
    fx *= (v_rms * 10 ** (-12 / 20)) / rms(fx[np.any(fx != 0, axis=1)])
    lim = np.abs(vo).max() * 0.6
    fx = np.tanh(fx / lim) * lim
    e = A.follower(vo, 0.01, 0.4)
    e = np.clip(e / (np.percentile(e[speech], 60) + 1e-9), 0, 1)
    mix = A.st(vo) + music * (1 - 0.55 * e)[:, None] + fx * (1 - 0.4 * e)[:, None]
    mix /= np.abs(mix).max() / 0.95
    import soundfile as sf
    raw = out_wav.replace(".wav", "_raw.wav")
    sf.write(raw, mix.astype(np.float32), SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9", "-ar", str(SR), out_wav], check=True)
    return out_wav
