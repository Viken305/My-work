"""Ep. 03 soundtrack: narration first; a slow, warm piano-and-pad score; close-miked kitchen foley.
Stems are balanced against the voice (music ~17 dB under it and ducking further while she talks)."""
import math
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "style-tests"))
import audio as A  # noqa: E402

SR = A.SR


def piano(f, d=3.5, vel=1.0):
    t = A.T(d)
    y = sum(np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k * k)) * np.exp(-t * (0.9 + 0.7 * k)) / k ** 1.2 for k in range(1, 7))
    y *= np.minimum(1, t / 0.004) * vel
    hammer = A.fft_filter(A.noise(0.02), 1500, 6000) * A.env(0.02, 0.0005, 0.006) * 0.15 * vel
    y[:len(hammer)] += hammer
    return y


def pad(chord, d, seed=0):
    t = A.T(d)
    r = np.random.default_rng(seed)
    y = sum(np.sin(2 * np.pi * f * (1 + det) * t + r.uniform(0, 6)) for f in chord for det in (-0.0025, 0.0, 0.0025))
    y = A.fft_filter(y, None, 1800)
    e = np.minimum(1, t / 1.5) * np.minimum(1, (d - t) / 1.5)
    return y * np.clip(e, 0, 1) / (len(chord) * 3)


def score(F):
    d = F.DURATION
    y = np.zeros((int(d * SR) + SR * 4, 2))
    # D major-ish, warm: Dmaj9 - Bm7 - Gmaj7 - A(sus)
    prog = [(146.8, 220.0, 277.2, 329.6), (123.5, 185.0, 220.0, 293.7), (98.0, 196.0, 246.9, 293.7), (110.0, 220.0, 293.7, 329.6)]
    bar = 60 / 66 * 4
    t, i = 0.4, 0
    climax0, climax1 = F.SH["climax"], F.SH["slow"]
    while t < d - 2:
        ch = prog[i % 4]
        if not (climax0 - 0.5 < t < climax1 + 2.5):
            A.place(y, t, A.st(pad(ch, bar + 1.5, i), (i % 2 - 0.5) * 0.3, 0.012), 0.55)
            for k, f in enumerate((ch[1] * 2, ch[2] * 2, ch[3] * 2, ch[2] * 2)):
                A.place(y, t + k * bar / 4 + 0.02 * k, A.st(piano(f, 3.0, 0.5 - 0.05 * k), (k - 1.5) * 0.25), 0.35)
            A.place(y, t, A.st(piano(ch[0] / 2, 4.0, 0.7)), 0.4)
        t += bar
        i += 1
    # tension under the climax: a low pulse that stops dead at the pop
    k = climax0
    while k < climax1 - 0.05:
        A.place(y, k, A.st(A.boom(60, 40, 0.35, 0.05) * 0.5), 0.6)
        k += max(0.18, 0.55 - (k - climax0) * 0.08)
    y = y[: int(d * SR)]
    fade = np.minimum(1, np.minimum(A.T(d) / 1.0, (d - A.T(d)) / 1.5))[:, None]
    return y * np.clip(fade, 0, 1)


def sfx(kind, seed=0):
    r = np.random.default_rng(seed)
    if kind == "kernel_pop":       # real-time pop: sharp crack + hollow body
        y = np.zeros(int(0.25 * SR))
        c = A.fft_filter(A.noise(0.012, seed), 1200, 9000) * A.env(0.012, 0.0003, 0.003)
        y[:len(c)] += A.norm(c)
        b = A.osc(r.uniform(380, 620), 0.12) * A.env(0.12, 0.001, 0.03)
        y[:len(b)] += b * 0.5
        return A.with_tail(A.st(y, r.uniform(-0.5, 0.5)), 0.12, 0.6, 7000)
    if kind == "slow_pop":         # the pop slowed down: a deep, breathy 'whoomp'
        d = 2.8
        t = A.T(d)
        y = A.fft_filter(A.noise(d, 3), 40, 900) * np.exp(-t * 1.6) * np.minimum(1, t / 0.03)
        b = A.boom(70, 30, 2.0, 0.2)[: len(y)]
        y[:len(b)] += b * 0.8
        return A.with_tail(A.st(A.norm(y) * 0.9, 0, 0.01), 0.3, 2.5, 3000)
    if kind == "ignite":
        d = 1.2
        t = A.T(d)
        y = A.fft_filter(A.noise(d, 4), 150, 3000) * np.minimum(1, t / 0.05) * np.exp(-t * 2.2)
        y += A.fft_filter(A.noise(d, 5), 2000, 7000) * np.exp(-t * 18) * 0.5
        return A.st(A.norm(y) * 0.8, 0, 0.01)
    if kind == "burner":           # steady gas roar, 4 s loop
        d = 4.0
        y = A.fft_filter(A.noise(d, 6), 120, 1600)
        return A.st(A.norm(y) * 0.35, 0, 0.015)
    if kind == "sizzle":           # oil: crackle of tiny bursts, 4 s loop
        d = 4.0
        y = A.fft_filter(A.noise(d, 7), 3000, 11000) * 0.2
        for k in range(160):
            tt = r.uniform(0, d - 0.01)
            cl = A.fft_filter(A.noise(0.006, k), 2500, 10000) * A.env(0.006, 0.0002, 0.002)
            A.place1(y, tt, cl, r.uniform(0.2, 0.8))
        return A.st(A.norm(y) * 0.5, 0, 0.01)
    if kind == "cork":
        y = np.zeros(int(0.6 * SR))
        p = A.osc(900, 0.04) * A.env(0.04, 0.0005, 0.012)
        y[:len(p)] += p
        hiss = A.fft_filter(A.noise(0.5, 9), 2500, 12000) * np.exp(-A.T(0.5) * 5)
        y[int(0.01 * SR):int(0.01 * SR) + len(hiss)] += hiss * 0.6
        return A.with_tail(A.st(y), 0.25, 1.2, 8000)
    if kind == "fizz":
        d = 3.0
        y = np.zeros(int(d * SR))
        for k in range(500):
            tt = r.uniform(0, d - 0.01)
            A.place1(y, tt, A.osc(r.uniform(3000, 8000), 0.004) * A.env(0.004, 0.0002, 0.0015), r.uniform(0.05, 0.3) * (1 - tt / d))
        return A.st(y, 0, 0.02)
    if kind == "pour":
        d = 3.0
        t = A.T(d)
        y = A.fft_filter(A.noise(d, 11), 200, 1400) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t)) * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.5)
        return A.st(A.norm(y) * 0.4, -0.2)
    if kind == "salt":
        d = 2.0
        y = np.zeros(int(d * SR))
        for k in range(90):
            tt = r.uniform(0, d - 0.01)
            A.place1(y, tt, A.osc(r.uniform(4000, 9000), 0.003) * A.env(0.003, 0.0001, 0.001), r.uniform(0.05, 0.25))
        return A.st(y, 0.2, 0.02)
    if kind == "steam":
        d = 2.0
        t = A.T(d)
        y = A.fft_filter(A.noise(d, 12), 1500, 9000) * np.minimum(1, t / 0.05) * np.exp(-t * 1.4)
        return A.st(A.norm(y) * 0.4, 0, 0.01)
    if kind == "leak":
        d = 3.0
        t = A.T(d)
        y = A.fft_filter(A.noise(d, 13), 3000, 9000) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)) * np.minimum(1, t / 0.4)
        return A.st(A.norm(y) * 0.15, 0.3)
    if kind == "tick":
        return A.st(A.fft_filter(A.noise(0.01, seed), 2000, 8000) * A.env(0.01, 0.0003, 0.003) * 0.4)
    return A.SFX(kind)


def render_audio(out_wav, F):
    here = os.path.dirname(os.path.abspath(F.__file__))
    n = int(F.DURATION * SR)
    fx = np.zeros((n, 2))
    SH, wt, st = F.SH, F.wt, F.st
    ev = [(wt("02", "explode") - 0.05, "reverse_swell", 0.4), (SH["cut"] + 0.15, "swish", 0.35), (wt("05", "heat") - 0.1, "ignite", 0.9),
          (SH["inside"], "swish", 0.3), (SH["slow"] - 0.02, "slow_pop", 1.0), (SH["slow"] - 0.02, "trailer_hit", 0.5),
          (SH["slow"] + 0.1, "steam", 0.7), (SH["sound"] + 0.2, "slow_pop", 0.6), (wt("12", "cork") + 0.05, "cork", 0.9),
          (wt("12", "cork") + 0.12, "fizz", 0.7), (wt("13", "leg") - 0.1, "slow_pop", 0.5), (wt("13", "flips"), "swish", 0.5),
          (SH["duds"] + 0.3, "leak", 0.8), (st("15") + 0.3, "pour", 0.8), (st("15") + 2.2, "salt", 0.8),
          (SH["stinger"] + 0.9, "kernel_pop", 1.2), (SH["stinger"] + 0.95, "swish", 0.4)]
    # ticking as the pressure needle climbs
    k = st("07")
    while k < wt("07", "nine") + 0.3:
        ev.append((k, "tick", 0.5))
        k += 0.11
    # real-time popping in the pan under the finale transition and the duds shot
    r = np.random.default_rng(3)
    for tt in r.uniform(SH["duds"] - 0.6, SH["duds"] + 0.8, 14):
        ev.append((float(tt), "kernel_pop", r.uniform(0.3, 0.7)))
    for i, (t0, kind, g) in enumerate(ev):
        A.place(fx, t0, sfx(kind, i), g)
    # beds: burner + sizzle while we are at the stove
    for a, b, kind, g in ((wt("05", "heat"), SH["inside"], "burner", 0.5), (wt("05", "heat") + 0.5, SH["inside"], "sizzle", 0.5),
                          (SH["climax"], SH["slow"], "burner", 0.5), (SH["climax"], SH["slow"], "sizzle", 0.7),
                          (SH["duds"], SH["finale"], "sizzle", 0.35)):
        loop = sfx(kind)
        seg = np.tile(loop, (int((b - a) / (len(loop) / SR)) + 1, 1))[: int((b - a) * SR)].copy()
        m = int(0.25 * SR)
        seg[:m] *= np.linspace(0, 1, m)[:, None]
        seg[-m:] *= np.linspace(1, 0, m)[:, None]
        A.place(fx, a, seg, g)
    vo = np.zeros(n)
    for key, item in F.TL.items():
        A.place1(vo, item["start"], A.load_vo(os.path.join(here, "build", "vo", f"{key}.wav")))
    vo = A.norm(vo, 0.9)
    music = score(F)
    rms = lambda x: np.sqrt(np.mean(np.square(x))) + 1e-12
    speech = np.abs(vo) > 0.02
    v_rms = rms(vo[speech])
    music *= (v_rms * 10 ** (-17 / 20)) / rms(music[np.any(music != 0, axis=1)])
    fx *= (v_rms * 10 ** (-11 / 20)) / rms(fx[np.any(fx != 0, axis=1)])
    lim = np.abs(vo).max() * 0.7
    fx = np.tanh(fx / lim) * lim
    e = A.follower(vo, 0.01, 0.4)
    e = np.clip(e / (np.percentile(e[speech], 60) + 1e-9), 0, 1)
    mix = A.st(vo) + music * (1 - 0.6 * e)[:, None] + fx * (1 - 0.45 * e)[:, None]
    mix /= np.abs(mix).max() / 0.95
    import soundfile as sf
    raw = out_wav.replace(".wav", "_raw.wav")
    sf.write(raw, mix.astype(np.float32), SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9", "-ar", str(SR), out_wav], check=True)
    return out_wav
