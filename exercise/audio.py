"""Sound design: synthesised in stereo, then mixed with the narration.

Every effect is built from layers (the way trailer sound is made):
  impacts  = transient click + mid body + pitch-dropping low end + sub, sent to a stereo reverb
  whooshes = noise through a band-pass that sweeps, peaking where the picture moves, panned across
  risers   = rising noise band + rising tone with accelerating tremolo, stopping dead into the hit
  swells   = a reversed reverb tail that sucks into the next hit
Music beds are slow drones and pads, ducked under the voice with an envelope follower. A tape stop warps the music
bus itself (playback slows to zero). The master gets glue compression, soft clipping and loudness normalisation.
"""
import math, subprocess

import numpy as np
import soundfile as sf

SR = 48000
R = np.random.default_rng(11)


# ---------------------------------------------------------------- basics
def T(d):
    return np.arange(int(d * SR)) / SR


def noise(d, seed=None):
    r = np.random.default_rng(seed) if seed is not None else R
    return r.standard_normal(int(d * SR))


def osc(freq, d, shape="sine"):
    """Oscillator with a frequency that may be an array (glides). Band-limited-ish saw via additive partials."""
    n = int(d * SR)
    f = np.broadcast_to(np.asarray(freq, float), (n,)) if np.ndim(freq) else np.full(n, float(freq))
    ph = 2 * np.pi * np.cumsum(f) / SR
    if shape == "sine":
        return np.sin(ph)
    if shape == "saw":
        top = int(min(24, max(1, 18000 / max(f.max(), 1))))
        return sum(np.sin(k * ph) / k for k in range(1, top + 1)) * 0.6
    if shape == "tri":
        return sum(((-1) ** ((k - 1) // 2)) * np.sin(k * ph) / k ** 2 for k in range(1, 12, 2)) * 0.8
    raise ValueError(shape)


def env(d, a=0.005, decay=0.3, hold=0.0, curve=1.0):
    t = T(d)
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a - hold) / max(decay, 1e-4))
    return e ** curve


def fft_filter(x, lo=None, hi=None, order=4):
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** order)
    if hi:
        m *= 1 / (1 + (f / hi) ** order)
    return np.fft.irfft(X * m, n)


def sweep(x, lo_curve, hi_curve, q_boost=0.0, frame=2048, hop=512):
    """Time-varying band-pass (STFT). lo/hi curves are functions of u in [0, 1] -> Hz."""
    n = len(x)
    win = np.hanning(frame)
    out = np.zeros(n + frame)
    norm = np.zeros(n + frame)
    f = np.fft.rfftfreq(frame, 1 / SR)
    pad = np.concatenate([x, np.zeros(frame)])
    for i in range(0, n, hop):
        u = i / max(n - 1, 1)
        lo, hi = lo_curve(u), hi_curve(u)
        m = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4)
        if q_boost:
            fc = math.sqrt(lo * hi)
            m *= 1 + q_boost * np.exp(-((np.log(np.maximum(f, 1)) - math.log(fc)) ** 2) / 0.02)
        seg = np.fft.irfft(np.fft.rfft(pad[i:i + frame] * win) * m, frame)
        out[i:i + frame] += seg * win
        norm[i:i + frame] += win ** 2
    return (out / np.maximum(norm, 1e-3))[:n]


def norm(x, peak=1.0):
    return x / (np.abs(x).max() + 1e-9) * peak


def st(x, pan=0.0, width=0.0):
    """Mono -> stereo with equal-power pan (-1..1) and optional Haas width (seconds of delay on one side)."""
    a = (pan + 1) * math.pi / 4
    l, r = x * math.cos(a), x * math.sin(a)
    if width:                                  # Haas widening on the highs only: the bass stays mono and in phase
        k = int(width * SR)
        lo = fft_filter(r, None, 250)
        hi = r - lo
        r = lo + (np.concatenate([np.zeros(k), hi[:-k]]) if k else hi)
    return np.stack([l, r], 1) * math.sqrt(2)


def st_move(x, p0, p1):
    """Stereo with a pan that moves from p0 to p1."""
    p = np.linspace(p0, p1, len(x))
    a = (p + 1) * math.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1) * math.sqrt(2)


_IR = {}


def reverb_ir(seconds=2.4, damp=5000, seed=1):
    key = (seconds, damp, seed)
    if key not in _IR:
        r = np.random.default_rng(seed)
        t = T(seconds)
        chans = []
        for ch in range(2):
            nz = r.standard_normal(len(t)) * np.exp(-t * 6.9 / seconds)
            nz = fft_filter(nz, 180, damp, 2)
            er = np.zeros(len(t))                     # a few early reflections
            for k in range(8):
                er[int(r.uniform(0.007, 0.06) * SR)] += r.uniform(0.2, 0.6)
            chans.append(nz * 0.9 + er)
        ir = np.stack(chans, 1)
        _IR[key] = ir / np.sqrt((ir ** 2).sum(0)).max()
    return _IR[key]


def convolve(x, ir):
    """x: (n, 2) stereo; ir: (m, 2). FFT convolution, output length n + m."""
    n = len(x) + len(ir)
    N = 1 << (n - 1).bit_length()
    out = np.zeros((n, 2))
    for ch in range(2):
        out[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch], N) * np.fft.rfft(ir[:, ch], N), N)[:n]
    return out


def with_tail(x_st, wet=0.35, seconds=2.2, damp=5000):
    """Adds a reverb tail to a short stereo effect (returns a longer buffer)."""
    ir = reverb_ir(seconds, damp)
    y = convolve(x_st, ir) * wet
    y[:len(x_st)] += x_st
    return y


# ---------------------------------------------------------------- effect layers
def click(d=0.012, hi=2500):
    return fft_filter(noise(d), hi, 16000) * env(d, 0.0005, d / 4)


def body(d=0.25, lo=180, hi=900):
    return fft_filter(noise(d), lo, hi) * env(d, 0.002, d / 4)


def boom(f0=110, f1=40, d=1.4, drop=0.35):
    t = T(d)
    f = f1 + (f0 - f1) * np.exp(-t / drop)
    return np.tanh(osc(f, d) * env(d, 0.003, d / 3.2) * 1.6)


def sub(f0=60, f1=28, d=1.8):
    t = T(d)
    f = f1 + (f0 - f1) * np.exp(-t / (d / 2.5))
    return osc(f, d) * env(d, 0.01, d / 2.8)


def SFX(kind):
    """Returns a stereo buffer for one effect."""
    if kind == "low_hit":
        x = norm(click()) * 0.5
        y = np.zeros(int(1.6 * SR))
        y[:len(x)] += x
        b = body(0.3, 150, 700)
        y[:len(b)] += norm(b) * 0.6
        y[:int(1.4 * SR)] += boom(95, 42, 1.4) * 1.0
        return with_tail(st(y), 0.3, 2.4, 3500)
    if kind == "trailer_hit":
        d = 3.2
        t = T(d)
        y = boom(80, 36, d, 0.5) * 1.1
        brass = sum(osc(f * (1 + 0.003 * k), d, "saw") for k, f in enumerate((55, 55.3, 82.4, 110.2)))
        cut = lambda u: 300 + 2600 * math.exp(-u * 6) + 200     # noqa: E731
        brass = sweep(brass, lambda u: 30, cut)
        y += norm(brass) * env(d, 0.02, 1.0) * 0.8
        metal = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in ((317, 3), (523, 4), (911, 6), (1427, 8)))
        y += metal * 0.08
        cl = click(0.02, 1800)
        y[:len(cl)] += norm(cl) * 0.7
        return with_tail(st(norm(y)), 0.45, 3.5, 3000)
    if kind == "sub_drop":
        return st(sub(70, 26, 2.2))
    if kind == "stamp":
        y = np.zeros(int(0.8 * SR))
        b = boom(130, 55, 0.6, 0.08)
        y[:len(b)] += b * 0.9
        s = fft_filter(noise(0.09), 400, 4200) * env(0.09, 0.001, 0.025)
        y[:len(s)] += norm(s) * 0.9
        return with_tail(st(y), 0.22, 1.2, 4500)
    if kind == "paper_whoosh":
        d = 0.6
        x = sweep(noise(d), lambda u: 300 + 1200 * u, lambda u: 1500 + 5000 * u) * np.sin(np.pi * np.clip(T(d) / d, 0, 1)) ** 1.5
        return st_move(norm(x) * 0.8, R.uniform(-0.8, -0.3), R.uniform(0.3, 0.8))
    if kind == "paper_slap":
        y = np.zeros(int(0.3 * SR))
        s = fft_filter(noise(0.05), 300, 6000) * env(0.05, 0.0005, 0.012)
        y[:len(s)] += norm(s)
        b = boom(160, 80, 0.15, 0.03)
        y[:len(b)] += b * 0.5
        return with_tail(st(y, R.uniform(-0.3, 0.3)), 0.15, 0.9, 5000)
    if kind in ("swish", "whoosh", "descend"):
        d = {"swish": 0.38, "whoosh": 1.0, "descend": 2.6}[kind]
        t = T(d)
        pk = 0.7 if kind != "descend" else 0.25
        shape = np.where(t / d < pk, (t / d / pk) ** 2.2, np.exp(-(t / d - pk) / (0.12 if kind != "descend" else 0.35)))
        if kind == "descend":
            x = sweep(noise(d), lambda u: 900 * (1 - u) + 60, lambda u: 4000 * (1 - u) ** 2 + 300, 1.5)
            x = norm(x) + 0.6 * norm(fft_filter(noise(d), 25, 140))
            y = norm(x * shape) * 0.9
            return with_tail(st_move(y, 0.0, 0.0), 0.3, 2.0, 2500)
        lo = (lambda u: 600 + 2500 * u) if kind == "swish" else (lambda u: 200 + 1500 * math.sin(math.pi * min(u / 0.7, 1)) ** 2)
        hi = (lambda u: 3000 + 9000 * u) if kind == "swish" else (lambda u: 900 + 5000 * math.sin(math.pi * min(u / 0.7, 1)))
        x = sweep(noise(d), lo, hi, 1.2) * shape
        return st_move(norm(x) * 0.8, -0.7, 0.7)
    if kind in ("riser_dark", "riser"):
        d = 2.0 if kind == "riser" else 2.6
        t = T(d)
        u = t / d
        nz = sweep(noise(d), lambda v: 200 + 3000 * v ** 2, lambda v: 900 + 9000 * v ** 2, 2.0)
        tone = osc(70 + 500 * u ** 2.2, d, "saw")
        trem = 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(3 + 26 * u ** 2) / SR)
        y = (norm(nz) * 0.7 + norm(fft_filter(tone, 40, 2500)) * 0.45 * trem) * u ** 2.4
        y[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))      # stops dead into the hit
        return st(norm(y) * 0.9, 0, 0.012)
    if kind == "reverse_swell":
        d = 0.9
        hit = np.zeros(int(0.05 * SR))
        hit[:] = norm(fft_filter(noise(0.05), 200, 6000)) * env(0.05, 0.001, 0.015)
        tail = with_tail(st(hit), 1.0, 1.4, 4000)[:int(d * SR)]
        y = tail[::-1] * np.linspace(0.2, 1, len(tail))[:, None] ** 2
        return y / (np.abs(y).max() + 1e-9) * 0.9
    if kind == "scream_texture":
        d = 1.8
        t = T(d)
        y = np.zeros(len(t))
        for k, (f0, f1) in enumerate(((620, 1180), (860, 540), (1340, 1900), (410, 700))):
            vib = 1 + 0.035 * np.sin(2 * np.pi * (5.5 + k) * t)
            y += osc((f0 + (f1 - f0) * (t / d) ** 0.7) * vib, d, "saw") * (0.5 if k else 0.8)
        y = sweep(y, lambda u: 400 + 300 * u, lambda u: 2500 + 1500 * math.sin(u * 7), 3.0)
        wind = sweep(noise(d), lambda u: 500 + 400 * math.sin(u * 9), lambda u: 1400 + 600 * math.sin(u * 9), 4.0)
        y = np.tanh((norm(y) * 0.8 + norm(wind) * 0.6) * 2.5) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.5
        return with_tail(st(norm(y) * 0.7, 0, 0.018), 0.6, 2.8, 3500)
    if kind == "tape_whir":
        d = 0.7
        t = T(d)
        f = 180 * (1 - t / d) ** 1.5 + 20
        y = osc(f, d, "saw") * (1 - t / d) * 0.5 + fft_filter(noise(d), 100, 1200 * (1 - 0.8)) * 0.15 * (1 - t / d)
        return st(norm(y) * 0.6)
    if kind == "glass_ting":
        d = 2.2
        t = T(d)
        y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in ((2093, 1, 2.2), (5130, 0.5, 4), (7905, 0.25, 7), (3311, 0.3, 3)))
        return with_tail(st(y * 0.5, 0.15, 0.006), 0.5, 2.6, 9000)
    if kind == "tick":
        d = 0.05
        t = T(d)
        y = np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 180)
        cl = norm(click(0.006, 4000)) * 0.4
        y[:len(cl)] += cl
        return st(y * 0.6, R.uniform(-0.2, 0.2))
    if kind in ("tick_roll", "counter"):
        d = 1.2 if kind == "tick_roll" else 2.0
        y = np.zeros((int((d + 0.2) * SR), 2))
        n = 22 if kind == "tick_roll" else 34
        for i in range(n):
            u = i / n
            tt = d * (1 - (1 - u) ** 2.2)              # ticks slow down as the digits settle
            place(y, tt, SFX("tick"), 0.5 + 0.5 * (1 - u))
        return y
    if kind == "pop":
        d = 0.12
        t = T(d)
        y = osc(500 + 700 * (1 - np.exp(-t * 40)), d) * env(d, 0.002, 0.04)
        return with_tail(st(y * 0.6, R.uniform(-0.3, 0.3)), 0.2, 0.8, 7000)
    if kind == "room_tone":
        d = 6.0
        common, l, r = (fft_filter(noise(d), 30, 400) for _ in range(3))
        return np.stack([common + 0.5 * l, common + 0.5 * r], 1) * 0.2
    if kind == "drill":
        d = 4.0
        t = T(d)
        rum = fft_filter(noise(d), 25, 160)
        grind = fft_filter(noise(d), 500, 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * 9.3 * t)) ** 3
        harm = sum(np.sin(2 * np.pi * f * t * (1 + 0.004 * np.sin(2 * np.pi * 0.7 * t))) / k for k, f in enumerate((73, 146, 221, 331), 1))
        y = norm(rum) * 0.8 + norm(grind) * 0.25 + norm(harm) * 0.3
        y *= np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.6)
        return with_tail(st(norm(y) * 0.8, 0, 0.01), 0.25, 1.8, 2000)
    if kind == "boil":
        d = 3.0
        y = np.zeros(int((d + 0.3) * SR))
        for i in range(70):
            tt = R.uniform(0, d)
            dd = R.uniform(0.04, 0.09)
            f0 = R.uniform(180, 420)
            tb = T(dd)
            b = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2.2 * tb / dd)) / SR) * np.exp(-tb * 45)
            place1(y, tt, b, R.uniform(0.2, 0.7) * min(1, tt / 0.6))
        y += fft_filter(noise(d + 0.3), 2000, 9000) * 0.05 * np.minimum(1, T(d + 0.3) / 0.8)
        y += fft_filter(noise(d + 0.3), 40, 200) * 0.25
        return with_tail(st(norm(y) * 0.8, 0, 0.012), 0.2, 1.4, 4000)
    if kind == "drip":
        d = 0.25
        t = T(d)
        y = osc(700 + 1400 * (1 - np.exp(-t * 60)), d) * env(d, 0.001, 0.05)
        return with_tail(st(y * 0.6, R.uniform(-0.4, 0.4)), 0.6, 2.0, 8000)
    if kind == "shimmer":
        d = 2.4
        y = np.zeros(int((d + 0.5) * SR))
        notes = [1318.5, 1567.98, 1975.5, 2349.3, 2637.0, 3135.9]
        for i in range(26):
            tt = d * i / 26 + R.uniform(0, 0.05)
            f = notes[R.integers(len(notes))]
            tb = T(0.6)
            g = np.sin(2 * np.pi * f * tb) * np.exp(-tb * 7) * np.minimum(1, tb / 0.004)
            place1(y, tt, g, 0.25 * math.sin(math.pi * i / 26) + 0.05)
        return with_tail(st(y, 0, 0.01), 0.6, 3.0, 9000)
    if kind == "heat_roar":
        d = 4.0
        t = T(d)
        roar = sweep(noise(d), lambda u: 40, lambda u: 300 + 900 * u, 0.8)
        crack = np.zeros(len(t))
        for i in range(60):
            k = int(R.uniform(0, d - 0.01) * SR)
            crack[k:k + 200] += R.uniform(-1, 1) * np.exp(-np.arange(200) / 30)
        y = norm(roar) * np.minimum(1, t / 1.5) + crack * 0.25
        return with_tail(st(norm(y) * 0.8, 0, 0.015), 0.25, 2.0, 3000)
    if kind == "metal_clank":
        d = 2.0
        t = T(d)
        y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in ((214, 1, 3), (539, 0.7, 4), (967, 0.5, 6), (1531, 0.35, 8), (2203, 0.2, 11)))
        cl = click(0.01, 1500)
        y[:len(cl)] += norm(cl) * 0.8
        return with_tail(st(norm(y) * 0.8, 0.1), 0.35, 2.2, 5000)
    if kind == "wind":
        d = 6.0
        t = T(d)
        y = sweep(noise(d), lambda u: 250 + 200 * math.sin(u * 5), lambda u: 900 + 500 * math.sin(u * 3 + 1), 2.5)
        y *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.21 * t) ** 2
        return st(norm(y) * 0.5, 0, 0.02) * np.minimum(1, np.minimum(t, d - t) / 1.0)[:, None]
    if kind == "heartbeat":
        y = np.zeros(int(0.9 * SR))
        for tt, g in ((0, 1.0), (0.22, 0.7)):
            b = boom(70, 40, 0.3, 0.06)
            place1(y, tt, b, g)
        return st(y * 0.9)
    if kind == "kick":
        d = 0.35
        t = T(d)
        f = 45 + 110 * np.exp(-t * 30)
        y = osc(f, d) * np.exp(-t * 9)
        cl = norm(click(0.004, 3000)) * 0.3
        y[:len(cl)] += cl
        return st(np.tanh(y * 1.8) * 0.8)
    if kind == "note_hit":
        d = 0.5
        t = T(d)
        f0 = R.choice([523.3, 659.3, 784.0, 1046.5])
        y = sum(np.sin(2 * np.pi * f0 * k * t) / k ** 1.3 for k in (1, 2, 3, 4)) * np.exp(-t * 9)
        y += fft_filter(noise(d), 4000, 14000) * np.exp(-t * 40) * 0.3
        return with_tail(st(norm(y) * 0.6, R.uniform(-0.4, 0.4), 0.006), 0.25, 1.2, 9000)
    if kind == "squeak":
        d = 0.16
        t = T(d)
        f = R.uniform(1700, 2600) * (1 + 0.04 * np.sin(2 * np.pi * 38 * t))
        y = osc(f, d, "tri") * np.sin(np.pi * t / d) ** 2
        return st(y * 0.25, R.uniform(-0.3, 0.3))
    if kind == "smash":
        d = 1.6
        t = T(d)
        y = fft_filter(noise(d), 1500, 12000) * np.exp(-t * 18) * 0.9
        for i in range(14):                            # ceramic fragments ringing and skittering
            tt = R.uniform(0, 0.5) ** 1.5
            tb = T(0.25)
            f0 = R.uniform(2200, 6500)
            g = np.sin(2 * np.pi * f0 * tb) * np.exp(-tb * R.uniform(25, 60))
            place1(y, tt, g, R.uniform(0.15, 0.4))
        b = boom(180, 90, 0.25, 0.05)
        y[:len(b)] += b * 0.6
        return with_tail(st(norm(y) * 0.85, 0.4, 0.008), 0.25, 1.4, 7000)
    if kind == "pour":
        d = 2.2
        t = T(d)
        y = fft_filter(noise(d), 300, 3000) * 0.3
        for i in range(40):
            tt = R.uniform(0, d - 0.1)
            dd = R.uniform(0.03, 0.07)
            tb = T(dd)
            b = np.sin(2 * np.pi * np.cumsum(R.uniform(300, 900) * (1 + 1.5 * tb / dd)) / SR) * np.exp(-tb * 50)
            place1(y, tt, b, R.uniform(0.2, 0.5))
        y *= np.minimum(1, t / 0.2) * np.minimum(1, (d - t) / 0.4)
        return with_tail(st(norm(y) * 0.6, -0.2, 0.01), 0.2, 1.2, 6000)
    if kind == "whisper":
        d = 2.4
        t = T(d)
        y = np.zeros((len(t), 2))
        for i in range(6):
            dd = R.uniform(0.25, 0.5)
            tb = T(dd)
            sy = sweep(noise(dd), lambda u: 1800 + 1500 * u, lambda u: 5200 + 2000 * u, 2.5)
            sy *= np.sin(np.pi * tb / dd) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * tb))
            place(y, R.uniform(0, d - dd), st(norm(sy) * 0.5, R.choice([-0.9, 0.9])))
        return with_tail(y, 0.5, 2.5, 6000)
    if kind == "car_pass":
        d = 3.0
        t = T(d)
        f = 90 * (1 + 0.15 * np.tanh((1.5 - t) * 3))
        eng = osc(f, d, "saw")
        eng = fft_filter(eng, 40, 900) + fft_filter(noise(d), 100, 1400) * 0.6
        e = np.exp(-((t - 1.5) / 0.8) ** 2)
        return st_move(norm(eng * e) * 0.7, -0.8, 0.8)
    if kind == "rumble_strip":
        d = 1.0
        t = T(d)
        y = fft_filter(noise(d), 40, 400) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 28 * t)))
        return st(norm(y) * 0.8 * np.minimum(1, (d - t) / 0.2), 0.3)
    if kind == "horn":
        d = 1.1
        t = T(d)
        y = (osc(415, d, "saw") + osc(349, d, "saw")) * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.08)
        return with_tail(st(norm(fft_filter(y, 200, 3000)) * 0.6, 0.4), 0.3, 1.5, 5000)
    if kind == "fridge":
        d = 3.0
        t = T(d)
        y = sum(np.sin(2 * np.pi * f * t) / k for k, f in enumerate((60, 120, 180), 1)) + fft_filter(noise(d), 80, 600) * 0.3
        return st(norm(y) * 0.35 * np.minimum(1, np.minimum(t, d - t) / 0.3))
    if kind == "flatline":
        d = 1.2
        t = T(d)
        y = np.sin(2 * np.pi * 1000 * t) * np.minimum(1, t / 0.01) * np.exp(-np.maximum(0, t - 0.8) * 8)
        return st(y * 0.18)
    raise KeyError(kind)


def place1(buf, t0, x, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    x = x[:len(buf) - i]
    buf[i:i + len(x)] += x * gain


def place(buf, t0, x, gain=1.0):
    """Adds stereo x (n, 2) into stereo buf at time t0."""
    i = int(t0 * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    j0 = max(0, -i)
    x = x[j0:]
    i = max(i, 0)
    x = x[:len(buf) - i]
    buf[i:i + len(x)] += x * gain


# ---------------------------------------------------------------- music beds
def bed(kind, d, seed=0):
    """A continuous musical bed of length d seconds (stereo)."""
    t = T(d)
    r = np.random.default_rng(seed)
    if kind == "tension":
        drone = osc(55, d, "saw") + osc(55.4, d, "saw") * 0.8 + osc(82.4, d, "saw") * 0.5
        drone = sweep(drone, lambda u: 30, lambda u: 380 + 220 * math.sin(u * 9) ** 2)
        hi = sum(np.sin(2 * np.pi * f * t + r.uniform(0, 6)) for f in (880, 932.3, 1318.5)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.31 * t))
        y = st(norm(drone) * 0.7, -0.1, 0.01) + st(hi * 0.05, 0.3, 0.02)
    elif kind == "deep":
        y0 = sum(np.sin(2 * np.pi * f * t + r.uniform(0, 6)) * a for f, a in ((41.2, 1), (61.7, 0.5), (82.4, 0.35), (123.5, 0.15)))
        y0 *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.09 * t)
        press = sweep(noise(d, seed), lambda u: 40, lambda u: 220 + 120 * math.sin(u * 4) ** 2)
        air = sum(np.sin(2 * np.pi * f * t + r.uniform(0, 6)) for f in (329.6, 493.9, 587.3)) * 0.04 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t + 1))
        y = st(y0 * 0.6 + norm(press) * 0.25, 0, 0.01) + st(air, -0.2, 0.017)
    elif kind == "wonder":
        chords = [(220, 261.6, 329.6, 493.9), (174.6, 261.6, 329.6, 440), (196, 246.9, 293.7, 440)]
        y = np.zeros((len(t), 2))
        seg = d / len(chords)
        for i, ch in enumerate(chords):
            tt = T(seg + 1.5)
            e = np.minimum(1, tt / 1.2) * np.minimum(1, np.maximum(0, seg + 1.5 - tt) / 1.4)
            pad = sum(np.sin(2 * np.pi * f * (1 + det) * tt + r.uniform(0, 6)) for f in ch for det in (-0.003, 0.003)) * e
            place(y, i * seg, st(pad * 0.12, (i - 1) * 0.3, 0.015))
        y += st(sum(np.sin(2 * np.pi * f * t) for f in (55, 82.4)) * 0.25)
    elif kind == "heat":
        u = t / d
        drone = osc(41.2 * (1 + 0.04 * u), d, "saw") + osc(43.65 * (1 + 0.04 * u), d, "saw") * 0.7
        drone = np.tanh(sweep(drone, lambda v: 30, lambda v: 200 + 900 * v) * (1.5 + 2 * u))
        rum = fft_filter(noise(d, seed), 25, 120) * (0.5 + 0.5 * u)
        y = st(norm(drone) * 0.6 + norm(rum) * 0.4, 0, 0.012)
    elif kind == "end":
        y = st(fft_filter(noise(d, seed), 200, 1200) * 0.06, 0, 0.02)
        for i, f in enumerate((110, 164.8, 130.8, 98)):           # sparse low piano-ish notes
            tt = T(4.0)
            note = sum(np.sin(2 * np.pi * f * k * tt) * np.exp(-tt * (1.2 + k)) / k for k in (1, 2, 3, 4.01))
            place(y, 0.3 + i * 2.2, st(note * 0.35, (i % 2 - 0.5) * 0.4))
    elif kind.startswith("night"):
        # lo-fi synth pad; each act detunes it a little more (night0 clean ... night2 sour)
        lvl = int(kind[-1])
        det = (0.0015, 0.006, 0.016)[lvl]
        chords = [(110, 164.8, 220, 261.6, 329.6), (98, 146.8, 196, 246.9, 293.7), (87.3, 130.8, 174.6, 220, 261.6), (98, 146.8, 196, 246.9, 329.6)]
        y = np.zeros((len(t), 2))
        seg = 4.0
        for i in range(int(d / seg) + 1):
            ch = chords[i % len(chords)]
            tt = T(seg + 1.6)
            e = np.minimum(1, tt / 1.0) * np.minimum(1, np.maximum(0, seg + 1.6 - tt) / 1.4)
            wob = 1 + det * np.sin(2 * np.pi * (0.13 + 0.05 * lvl) * tt + i)
            pad = sum(np.sin(2 * np.pi * f * wob * (1 + s_ * det) * tt + r.uniform(0, 6)) for f in ch for s_ in (-1, 1)) * e
            pad = fft_filter(pad, 60, 2400 - 500 * lvl)
            place(y, i * seg, st(pad * 0.08, (i % 2 - 0.5) * 0.3, 0.015))
        y += st(np.sin(2 * np.pi * 55 * t) * 0.18 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.1 * t)))
        if lvl == 2:
            y += st(fft_filter(noise(d, seed), 300, 1400) * 0.05 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.37 * t)), 0, 0.02)
    elif kind in ("pulse_bed", "synthwave"):
        bpm_ = 120 if kind == "pulse_bed" else 128
        step = 60 / bpm_ / 2
        roots = (55, 43.65, 49, 41.2) if kind == "pulse_bed" else (55, 65.4, 49, 43.65)
        y = np.zeros((len(t), 2))
        n = int(d / step)
        for i in range(n):                             # eighth-note bass plus an arpeggio on top
            bar = (i // 16) % 4
            r0 = roots[bar]
            tb = T(step * 0.95)
            bass = osc(r0 * (2 if i % 2 else 1), step * 0.95, "saw") * np.exp(-tb * 6)
            place(y, i * step, st(fft_filter(bass, 30, 700) * 0.25))
            arp = [4, 6, 8, 12][i % 4] if kind == "synthwave" else [8, 12, 10, 12][i % 4]
            ton = osc(r0 * arp, step * 0.95, "saw") * np.exp(-tb * 10)
            place(y, i * step, st(fft_filter(ton, 300, 5000) * 0.07, (i % 2 - 0.5) * 0.6, 0.008))
        pad = sum(np.sin(2 * np.pi * f * t + r.uniform(0, 6)) for f in (220, 277.2, 329.6)) * 0.03
        y += st(pad, 0, 0.015)
    elif kind == "silence":
        y = np.zeros((len(t), 2))
    else:
        raise KeyError(kind)
    fade = np.minimum(1, np.minimum(t / 0.6, (d - t) / 0.8))[:, None]
    return y * np.clip(fade, 0, 1)


def pulse(d, bpm):
    y = np.zeros((int(d * SR), 2))
    beat = 60.0 / bpm
    k = 0
    while k * beat < d:
        place(y, k * beat, SFX("heartbeat"), 0.6 + 0.4 * (k * beat / d))
        k += 1
    return y


# ---------------------------------------------------------------- mix
def load_vo(path):
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:                               # band-limited (FFT) resampling: no aliasing images
        n2 = int(round(len(x) * SR / sr))
        X = np.fft.rfft(x)
        Y = np.zeros(n2 // 2 + 1, complex)
        m = min(len(X), len(Y))
        Y[:m] = X[:m]
        x = np.fft.irfft(Y, n2) * (n2 / len(x))
    return x


def follower(x, attack=0.03, release=0.35):
    """Envelope follower on |x| (block-wise for speed)."""
    hop = int(0.005 * SR)
    a = np.abs(x)
    blocks = a[: len(a) // hop * hop].reshape(-1, hop).max(1)
    e = np.zeros(len(blocks))
    ka, kr = math.exp(-0.005 / attack), math.exp(-0.005 / release)
    v = 0.0
    for i, b in enumerate(blocks):
        v = ka * v + (1 - ka) * b if b > v else kr * v + (1 - kr) * b
        e[i] = v
    centers = (np.arange(len(e)) + 0.5) * hop
    return np.interp(np.arange(len(a)), centers, e)     # smooth gain, no zipper noise


def tape_stop(bus, t0, dur=0.7):
    """Playback of the bus slows from 1x to 0 over dur seconds starting at t0; then silence until the bus resumes."""
    i0, n = int(t0 * SR), int(dur * SR)
    if i0 + n >= len(bus):
        return
    tau = np.arange(n) / SR
    pos = i0 + (tau - tau ** 2 / (2 * dur)) * SR
    for ch in range(2):
        bus[i0:i0 + n, ch] = np.interp(pos, np.arange(len(bus)), bus[:, ch]) * np.linspace(1, 0.2, n)


def render_mix(out_wav, duration, vo_clips, events, music):
    """vo_clips [(t, wav)], events [(t, kind, gain)],
    music dict(beds=[(t0, t1, kind, gain)], pulse=[(t0, t1, bpm)], mute=[(t0, t1)])."""
    n = int(duration * SR)
    vo = np.zeros(n)
    for t0, path in vo_clips:
        x = load_vo(path)
        k = int(0.006 * SR)
        x[:k] *= np.linspace(0, 1, k)
        x[-k:] *= np.linspace(1, 0, k)
        place1(vo, t0, x)
    vo = norm(vo, 0.9)
    mus = np.zeros((n, 2))
    for i, (t0, t1, kind, g) in enumerate(music.get("beds", [])):
        place(mus, t0, bed(kind, t1 - t0 + 0.8, seed=i), g)
    for t0, t1, bpm in music.get("pulse", []):
        place(mus, t0, pulse(t1 - t0, bpm), 0.5)
    fx = np.zeros((n, 2))
    stops = []
    for t0, kind, g in events:
        if kind == "tape_stop":
            stops.append(t0)
            place(fx, t0, SFX("tape_whir"), g * 0.8)
            continue
        place(fx, t0, SFX(kind), g)
    for t0 in stops:
        tape_stop(mus, t0)
    for t0, t1 in music.get("mute", []):              # microsleeps: music and effects drop out, the voice stays
        i0, i1 = int(t0 * SR), int(t1 * SR)
        k = int(0.03 * SR)
        g = np.ones(n)
        g[max(0, i0):max(0, i1)] = 0.0
        g = np.convolve(g, np.ones(k) / k, "same")
        mus *= g[:, None]
        fx *= g[:, None]
    # side-chain: music and effects make room for the voice
    e = follower(vo)
    e = np.clip(e / (e.max() + 1e-9) * 2.5, 0, 1)
    duck_m = (1 - 0.6 * e)[:, None]
    duck_f = (1 - 0.3 * e)[:, None]
    voice = st(vo, 0.0) * 0.72
    mix = voice + mus * 0.42 * duck_m + fx * 0.5 * duck_f
    # glue compression on the master (slow RMS), then soft clip
    lvl = follower(mix.mean(1), 0.01, 0.25)
    gain = np.where(lvl > 0.35, (0.35 + (lvl - 0.35) / 3) / np.maximum(lvl, 1e-6), 1.0)[:, None]
    mix = np.tanh(mix * gain * 1.2) / np.tanh(1.2)
    raw = out_wav.replace(".wav", "_raw.wav")
    sf.write(raw, mix.astype(np.float32), SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9", "-ar", str(SR), out_wav], check=True)
    return out_wav
