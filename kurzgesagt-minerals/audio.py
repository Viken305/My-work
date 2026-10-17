"""Procedural soundtrack: ambient pad + marimba plucks + SFX, ducked under the narration."""
import json, math, os, subprocess

import numpy as np
import soundfile as sf

SR = 48000
RNG = np.random.default_rng(42)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tline(d):
    return np.arange(int(d * SR)) / SR


def place(buf, t0, x, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    j0 = max(0, -i)
    x = x[j0:len(buf) - i] if i + len(x) > len(buf) else x[j0:]
    buf[max(i, 0):max(i, 0) + len(x)] += x * gain


def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) * 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def env_ad(n_or_t, a, d):
    t = n_or_t if isinstance(n_or_t, np.ndarray) else tline(n_or_t)
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)


# ---------------------------------------------------------------- instruments
def bell(f, d=1.4, amp=1.0):
    t = tline(d)
    x = sum(w * np.sin(2 * math.pi * f * r * t) * np.exp(-t * k) for r, w, k in ((1, 1, 3.0), (2.76, 0.35, 6), (5.4, 0.18, 10), (8.9, 0.08, 16)))
    return x * env_ad(t, 0.002, 10) * amp


def pluck(f, d=0.9, amp=1.0):
    t = tline(d)
    x = np.sin(2 * math.pi * f * t) + 0.35 * np.sin(4 * math.pi * f * t) * np.exp(-t * 14) + 0.12 * np.sin(2 * math.pi * 3.99 * f * t) * np.exp(-t * 25)
    return x * env_ad(t, 0.003, 0.28) * amp


def noise(d):
    return RNG.standard_normal(int(d * SR))


def sfx(kind):
    pent = [72, 74, 76, 79, 81, 84, 86, 88, 91]
    if kind == "chime":
        return bell(midi(RNG.choice(pent) + 12), 1.4, 0.5)
    if kind == "shine":
        x = sum(bell(midi(m), 2.2, 0.35) for m in (84, 88, 91, 96))
        place(x, 0.0, sfx("shimmer"), 0.6)
        return x
    if kind == "shimmer":
        out = np.zeros(int(1.6 * SR))
        for k in range(10):
            place(out, k * 0.07, bell(midi(pent[k % len(pent)] + 12), 0.9, 0.18))
        return out
    if kind in ("whoosh", "whoosh_soft", "whoosh_long"):
        d = {"whoosh": 0.9, "whoosh_soft": 0.6, "whoosh_long": 1.5}[kind]
        t = tline(d)
        lo, hi = bandpass(noise(d), 150, 900), bandpass(noise(d), 900, 5000)
        sweep = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
        mixk = np.clip(t / d * 1.4, 0, 1)
        x = (lo * (1 - mixk) + hi * mixk * 0.6) * sweep
        return x / (np.abs(x).max() + 1e-9) * 0.6
    if kind == "riser":
        d = 1.1
        t = tline(d)
        f = 200 * 2 ** (t / d * 3)
        x = 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * bandpass(noise(d), 1500, 8000) / 3
        return x * (t / d) ** 2 * 0.9
    if kind == "boom":
        d = 2.2
        t = tline(d)
        f = 60 * np.exp(-t * 0.6)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6) + 0.3 * bandpass(noise(d), 20, 200) / 4 * np.exp(-t * 2)
        return x * env_ad(t, 0.01, 50)
    if kind == "swell_soft":
        d = 2.5
        t = tline(d)
        x = sum(np.sin(2 * np.pi * midi(m) * t) for m in (57, 64, 69)) / 3
        return x * np.sin(np.pi * t / d) ** 2 * 0.25
    if kind == "tink":
        f = RNG.uniform(2600, 4200)
        x = bell(f, 0.25, 0.4)
        x[: int(0.01 * SR)] += bandpass(noise(0.01), 3000, 9000) * 0.05
        return x
    if kind == "click":
        t = tline(0.08)
        return np.sin(2 * np.pi * 1500 * t) * np.exp(-t * 90) * 0.6 + np.r_[bandpass(noise(0.004), 2000, 8000) * 0.2, np.zeros(len(t) - int(0.004 * SR))]
    if kind == "pop":
        t = tline(0.18)
        f = 320 + 520 * np.minimum(1, t / 0.06)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(t, 0.004, 0.05)
    if kind == "blip":
        t = tline(0.12)
        return np.sin(2 * np.pi * RNG.uniform(900, 1500) * t) * env_ad(t, 0.002, 0.03) * 0.6
    if kind == "slide":
        d = 0.6
        t = tline(d)
        return bandpass(noise(d), 2500, 7000) * np.sin(np.pi * t / d) * 0.08
    raise ValueError(kind)


def pad(chords, end):
    out = np.zeros(int((end + 3) * SR))
    for n, (t0, root, iv) in enumerate(chords):
        t1 = chords[n + 1][0] if n + 1 < len(chords) else end
        d = t1 - t0 + 2.0
        t = tline(d)
        e = np.minimum(1, t / 1.8) * np.clip((d - t) / 2.0, 0, 1)
        x = np.zeros_like(t)
        for k, i in enumerate(iv):
            f = midi(root + i)
            for det in (-0.004, 0.004):
                for h in range(1, 6):
                    x += np.sin(2 * np.pi * f * (1 + det) * h * t + k + h) / h ** 1.6 * 0.05
        x += 0.12 * np.sin(2 * np.pi * midi(root - 12) * t)
        x *= 1 + 0.15 * np.sin(2 * np.pi * 0.2 * t)
        place(out, t0 - 0.3, x * e)
    return out


def plucks(chords, start, bpm, rise, end):
    out = np.zeros(int((end + 3) * SR))
    step = 60 / bpm / 2
    t, k = start, 0
    while t < end - 0.5:
        ch = [c for c in chords if c[0] <= t][-1]
        r = (t - rise[0]) / (rise[1] - rise[0]) if rise[0] <= t < rise[1] else (-1 if t < rise[0] else 2)
        pattern = [0, 2, 1, 3, 2, 4, 3, 1]
        iv = ch[2][pattern[k % 8] % len(ch[2])]
        lift = 12 * int(max(0, min(1, r)) * 2) if 0 <= r <= 1 else 0
        amp = 0.09 if r < 0 else 0.09 + 0.06 * min(1, max(0, r)) if r <= 1 else 0.07
        place(out, t, pluck(midi(ch[1] + 12 + iv + lift), 0.9, amp))
        t += step / 2 if 0 <= r <= 1 else step
        k += 1
    return out


# ---------------------------------------------------------------- mix
def load_vo(path):
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
    return x


def render_mix(out_wav, duration, vo_times, vo_dir, events, music):
    n = int(duration * SR)
    vo = np.zeros(n)
    for key, t0 in vo_times.items():
        place(vo, t0, load_vo(os.path.join(vo_dir, f"{key}.wav")))
    vo /= np.abs(vo).max() + 1e-9
    fx = np.zeros(n)
    for t0, kind, gain in events:
        place(fx, t0, sfx(kind), gain)
    mus = pad(music["chords"], music["end"])[:n] + plucks(music["chords"], music["pluck_from"], music["pluck_bpm"], music["rise"], music["end"])[:n]
    # duck music + sfx under narration
    win = int(0.25 * SR)
    env = np.convolve(np.abs(vo), np.ones(win) / win, "same")
    env = np.clip(env / (env.max() + 1e-9) * 3, 0, 1)
    duck = 1 - 0.45 * env
    fade = np.ones(n)
    tail = int(1.2 * SR)
    fade[-tail:] = np.linspace(1, 0, tail)
    fade[: int(0.4 * SR)] = np.linspace(0, 1, int(0.4 * SR))
    mixd = vo * 0.85 + mus * 0.55 * duck * fade + fx * 0.32 * (1 - 0.25 * env)
    mixd = np.tanh(mixd * 1.1) / np.tanh(1.1)
    stereo = np.stack([mixd, mixd], 1)
    raw = out_wav.replace(".wav", "_raw.wav")
    sf.write(raw, stereo.astype(np.float32), SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "loudnorm=I=-15:TP=-1.5:LRA=11",
                    "-ar", str(SR), out_wav], check=True)
    return out_wav
