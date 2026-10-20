"""Soundtrack for the WellWithAll Energy reel: synthesised music + sound effects, all in code.

Modelled on the reference reel's sound (measured, not sampled):
  * 120 BPM, G major, a deep tuned 808-style kick
  * 0-7 s: syncopated kicks (not every beat) under a wobbly, chopped "vocal" hook (formant synth with vibrato)
  * 7-8 s: the break: kick and bass drop out, a held vowel slides down, then a zig-zag pitch riser into...
  * 8-11 s: the drop: four-on-the-floor, claps on 2 and 4, off-beat hats and bass
  * 11 s: final hit and ring-out
  * effects on the picture: pops on cuts, bubble blips on fruit, can-open fizz, swishes on type, crashes on transitions
Master is loud and dense like the reference: -14 LUFS integrated, limited to -1 dBTP.
"""
import math, subprocess

import numpy as np
import soundfile as sf

from film import BEAT, CUTS, DURATION

SR = 48000
S16 = BEAT / 4                     # one sixteenth note
R = np.random.default_rng(5)


# ---------------------------------------------------------------- basics
def T(d):
    return np.arange(int(d * SR)) / SR


def hz(note):
    names = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    return 440.0 * 2 ** ((names[note[:-1]] + 12 * (int(note[-1]) + 1) - 69) / 12)


def osc(freq, d, shape="sine"):
    n = int(d * SR)
    f = np.broadcast_to(np.asarray(freq, float), (n,)) if np.ndim(freq) else np.full(n, float(freq))
    ph = 2 * np.pi * np.cumsum(f) / SR
    if shape == "sine":
        return np.sin(ph)
    if shape == "saw":
        top = int(min(30, max(1, 16000 / max(f.max(), 1))))
        return sum(np.sin(k * ph) / k for k in range(1, top + 1)) * 0.6
    if shape == "tri":
        return sum(((-1) ** ((k - 1) // 2)) * np.sin(k * ph) / k ** 2 for k in range(1, 12, 2)) * 0.8
    raise ValueError(shape)


def env(d, a=0.003, decay=0.2, hold=0.0, release=0.004):
    t = T(d)
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a - hold) / max(decay, 1e-4))
    r = int(release * SR)
    if r and len(e) > r:
        e[-r:] *= np.linspace(1, 0, r)              # hard chop with a tiny fade: the "edited" sound
    return e


def noise(d):
    return R.standard_normal(int(d * SR))


def band(x, lo=None, hi=None, order=4):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** order)
    if hi:
        m *= 1 / (1 + (f / hi) ** order)
    return np.fft.irfft(X * m, len(x))


def sweep(x, f0, f1, width=1.0):
    """Band-pass whose centre glides f0 -> f1 (log), via short overlapping FFT frames."""
    n, frame, hop = len(x), 1024, 256
    out, wsum, win = np.zeros(n + frame), np.zeros(n + frame), np.hanning(frame)
    f = np.fft.rfftfreq(frame, 1 / SR)
    pad = np.concatenate([x, np.zeros(frame)])
    for i in range(0, n, hop):
        fc = f0 * (f1 / f0) ** (i / max(n - 1, 1))
        m = np.exp(-(np.log(np.maximum(f, 1) / fc) ** 2) / (2 * (0.5 * width) ** 2))
        out[i:i + frame] += np.fft.irfft(np.fft.rfft(pad[i:i + frame] * win) * m, frame) * win
        wsum[i:i + frame] += win ** 2
    return (out / np.maximum(wsum, 1e-3))[:n]


def st(x, pan=0.0):
    a = (pan + 1) * math.pi / 4
    return np.stack([x * math.cos(a), x * math.sin(a)], 1) * math.sqrt(2)


_IR = None


def reverb(x_st, wet=0.25, seconds=1.3):
    global _IR
    if _IR is None:
        r, t = np.random.default_rng(2), T(seconds)
        _IR = np.stack([band(r.standard_normal(len(t)) * np.exp(-t * 6.9 / seconds), 250, 7000, 2) for _ in range(2)], 1)
        _IR /= np.sqrt((_IR ** 2).sum(0))
    n = len(x_st) + len(_IR)
    wetsig = np.stack([np.fft.irfft(np.fft.rfft(x_st[:, k], n) * np.fft.rfft(_IR[:, k], n), n) for k in range(2)], 1)
    out = np.zeros((n, 2))
    out[:len(x_st)] += x_st
    return out + wetsig * wet


def place(buf, t0, x, gain=1.0):
    x = st(x) if x.ndim == 1 else x
    i = int(round(t0 * SR))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[:j - i] * gain


# ---------------------------------------------------------------- drums
def kick(drop=False):
    d = 0.45 if drop else 0.38
    t = T(d)
    f = 52 + 120 * np.exp(-t / 0.035)               # tuned 808 kick: pitch dives onto ~G1/A1
    x = np.tanh(1.6 * osc(f, d) * env(d, 0.001, 0.22 if drop else 0.18))
    x[:int(0.004 * SR)] += band(noise(0.004), 1500, 6000) * 0.5
    return x


def clap():
    x = np.zeros(int(0.3 * SR))
    for k, g in enumerate((0.6, 0.8, 1.0)):
        b = band(noise(0.3), 900, 5200) * env(0.3, 0.001, 0.012 if k < 2 else 0.11)
        i = int(k * 0.009 * SR)
        x[i:] += b[:len(x) - i] * g
    return x * 0.6


def hat(open_=False):
    d = 0.18 if open_ else 0.05
    return band(noise(d), 7000, None) * env(d, 0.001, 0.06 if open_ else 0.014) * 0.5


def shaker():
    return band(noise(0.07), 4500, 11000) * env(0.07, 0.012, 0.02) * 0.3


def crash(d=1.6):
    x = band(noise(d), 3500, None) * env(d, 0.002, 0.55)
    x += band(noise(d), 9000, None) * env(d, 0.001, 0.2) * 0.6
    return x * 0.45


# ---------------------------------------------------------------- tonal
def bass(note, d):
    f = hz(note)
    x = osc(f, d) + 0.35 * osc(2 * f, d) + 0.15 * band(osc(f, d, "saw"), None, 900)
    return np.tanh(1.4 * x * env(d, 0.004, 0.16, release=0.01)) * 0.8


def pluck(note, d=0.22):
    """Bubbly marimba-ish pluck (sine + bright partial that dies fast)."""
    f = hz(note)
    return (osc(f, d) * env(d, 0.002, 0.11) + 0.5 * osc(4 * f, d) * env(d, 0.001, 0.025)) * 0.5


VOWELS = {"oo": [(320, 1.0), (800, 0.4), (2500, 0.1)], "ah": [(750, 1.0), (1200, 0.7), (2600, 0.25)],
          "ee": [(300, 0.9), (2300, 0.6), (3000, 0.3)], "oh": [(500, 1.0), (900, 0.6), (2500, 0.15)]}


def vox(freq, d, vowel="ah", vib=0.35, vib_rate=6.0, chop=True):
    """Formant 'vocal chop': saw through vowel resonances, with vibrato -> the wobbly harmonics in the reference."""
    t = T(d)
    base = np.broadcast_to(np.asarray(freq, float), t.shape) if np.ndim(freq) else np.full(t.shape, float(freq))
    f = base * 2 ** (vib * np.sin(2 * np.pi * vib_rate * t) * np.minimum(1, t / 0.08) / 12)
    src = osc(f, d, "saw")
    X = np.fft.rfft(src)
    fr = np.fft.rfftfreq(len(src), 1 / SR)
    m = sum(g * np.exp(-((fr - fc) / (fc * 0.12)) ** 2) for fc, g in VOWELS[vowel]) + 0.02
    x = np.fft.irfft(X * m, len(src))
    e = env(d, 0.008, 0.6 if chop else 4.0, hold=d * 0.4, release=0.006 if chop else 0.08)
    return x / (np.abs(x).max() + 1e-9) * e * 0.55


# ---------------------------------------------------------------- effects
def mouth_pop():
    d = 0.06
    t = T(d)
    return osc(260 + 900 * (1 - np.exp(-t / 0.012)), d) * env(d, 0.001, 0.018) * 0.7


def blip(f0=500, f1=1700):
    d = 0.09
    t = T(d)
    return osc(f0 * (f1 / f0) ** np.minimum(1, t / 0.05), d) * env(d, 0.002, 0.035) * 0.45


def can_open():
    """'tsk-PSSHT' + carbonation crackle."""
    d = 1.3
    x = np.zeros(int(d * SR))
    x[:int(0.02 * SR)] += band(noise(0.02), 2000, 6000) * env(0.02, 0.0005, 0.004) * 1.2
    i = int(0.03 * SR)
    hiss = sweep(noise(0.45), 6000, 3000, 1.2) * env(0.45, 0.004, 0.12)
    x[i:i + len(hiss)] += hiss * 0.9
    n = len(x)
    pos = R.integers(i, n, 260)                      # fizz: sparse bright clicks thinning out
    for p in pos:
        if R.random() < math.exp(-(p - i) / (0.5 * SR)):
            k = min(n - p, 60)
            x[p:p + k] += R.uniform(-1, 1) * np.exp(-np.arange(k) / 8.0) * 0.5
    return band(x, 1500, 14000, 2)


def swish(d=0.2, f0=900, f1=6000):
    return sweep(noise(d), f0, f1, 0.9) * np.sin(np.pi * T(d) / d) ** 2 * 0.8


def thump():
    d = 0.16
    t = T(d)
    return osc(130 * np.exp(-t / 0.08) + 50, d) * env(d, 0.001, 0.06) * 0.8


def shutter():
    x = np.zeros(int(0.08 * SR))
    for k in (0, int(0.028 * SR)):
        b = band(noise(0.02), 2500, 9000) * env(0.02, 0.0005, 0.004)
        x[k:k + len(b)] += b
    return x * 0.7


def chime(notes=("G5", "B5", "D6", "G6"), gap=0.045):
    x = np.zeros(int(1.2 * SR))
    for k, nt in enumerate(notes):
        f = hz(nt)
        b = (osc(f, 1.0) + 0.3 * osc(2.76 * f, 1.0)) * env(1.0, 0.002, 0.35)
        i = int(k * gap * SR)
        x[i:i + len(b)] += b * 0.22
    return x


# ---------------------------------------------------------------- the music
CHORDS = {0: ("G", ["G3", "B3", "D4"]), 1: ("E", ["E3", "G3", "B3"]), 2: ("C", ["C3", "E3", "G3"]),
          3: ("D", ["D3", "F#3", "A3"]), 4: ("G", ["G3", "B3", "D4"]), 5: ("E", ["E3", "G3", "B3"])}
HOOK = [(0, "D5", 2, "ah"), (2, "B4", 1, "oo"), (3, "D5", 1, "ah"), (6, "E5", 2, "ee"), (8, "D5", 1, "ah"),
        (10, "B4", 2, "oh"), (12, "A4", 1, "oo"), (13, "B4", 1, "ah"), (14, "G4", 2, "oh")]
KICKS_A, KICKS_B = [0, 6, 10], [0, 3, 6, 11, 14]


def music():
    n = int((DURATION + 0.5) * SR)
    drums, tone = np.zeros((n, 2)), np.zeros((n, 2))
    for bar in range(6):
        t0 = bar * 4 * BEAT
        root, triad = CHORDS[bar]
        drop = bar >= 4
        if bar == 5:                                 # bar 5 is cut short by the end hit at 11.0
            root, triad = ("C", ["C3", "E3", "G3"])
        for s in range(16):
            ts = t0 + s * S16
            if bar == 3 and ts >= 7.0:               # the break: no drums, no bass, no hook
                break
            if bar == 5 and ts >= 11.0:
                break
            kicks = [0, 4, 8, 12] if drop else (KICKS_A if bar % 2 == 0 else KICKS_B)
            if s in kicks:
                place(drums, ts, kick(drop), 1.0)
                place(tone, ts, bass(root + ("1" if drop else "2"), S16 * (2 if drop else 3)), 0.7)
            if drop and s % 4 == 2:
                place(tone, ts, bass(root + "2", S16 * 1.6), 0.55)
                place(drums, ts, st(hat(True), 0.25), 0.5)
            if s in (4, 12):
                place(drums, ts, reverb(st(clap()), 0.25)[:int(0.6 * SR)], 0.55 if drop else 0.4)
            if drop:
                place(drums, ts, st(hat(), -0.3 if s % 2 else 0.3), 0.32 if s % 2 else 0.2)
            else:
                place(drums, ts, st(shaker(), 0.35 if s % 2 else -0.35), 0.8 if s % 2 else 0.4)
            if s in (0, 3, 6, 10, 12) and not (bar == 3 and s > 8):
                for k, nt in enumerate(triad):
                    nt2 = nt[:-1] + str(int(nt[-1]) + 1)
                    place(tone, ts + k * 0.012, st(pluck(nt2), (k - 1) * 0.5), 0.22)
        for s, nt, ln, vw in HOOK:
            ts = t0 + s * S16
            if (bar == 3 and ts >= 7.0) or ts >= 11.0:
                continue
            up = nt[:-1] + str(int(nt[-1]) + (1 if drop and s in (6, 8) else 0))
            place(tone, ts, st(vox(hz(up), ln * S16 * 0.92, vw), 0.1 if s % 4 else -0.1), 0.42)
    # ---- the break (7.0-8.0): a held vowel slides down, then a zig-zag riser, then silence before the drop
    d = 0.5
    t = T(d)
    slide = hz("E5") * 2 ** (-7 * smoothstep(t / d) / 12)
    place(tone, 7.0, reverb(st(vox(slide, d, "ah", vib=0.6, vib_rate=7, chop=False)), 0.35)[:int(0.55 * SR)], 0.55)
    d = 0.44
    t = T(d)
    rate = 6 + 26 * (t / d) ** 2
    zig = hz("A4") * 2 ** ((12 * t / d + 2.5 * np.sign(np.sin(2 * np.pi * np.cumsum(rate) / SR))) / 12)
    place(tone, 7.5, st(vox(zig, d, "ee", vib=0, chop=True)), 0.4)
    place(tone, 7.5, st(swish(0.44, 400, 9000) * np.linspace(0.3, 1.2, int(0.44 * SR))), 0.6)
    for k in range(8):                                # clap roll speeding up into the drop
        place(drums, 7.5 + 0.44 * (1 - (1 - k / 8) ** 1.6), st(clap()), 0.12 + 0.05 * k)
    # ---- final hit
    place(drums, 11.0, kick(True), 1.1)
    place(drums, 11.0, st(crash(1.5)), 0.7)
    place(tone, 11.0, bass("G1", 1.0), 0.8)
    for k, nt in enumerate(["G4", "B4", "D5"]):
        place(tone, 11.0, reverb(st(vox(hz(nt), 1.3, "ah", vib=0.25, chop=False), (k - 1) * 0.6), 0.4), 0.3)
    return drums, tone


def smoothstep(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- effects timeline (locked to film.py)
def effects():
    n = int((DURATION + 0.5) * SR)
    fx = np.zeros((n, 2))
    for k, c in enumerate(CUTS):
        if c in (3.0, 8.0, 10.0, 11.0):
            continue
        place(fx, c, st(mouth_pop(), (-0.3, 0.3)[k % 2]), 0.55)
    for k in range(4):                                # starburst fruit pops
        place(fx, k * BEAT + 0.02, st(blip(450 + 60 * k, 1500 + 200 * k), 0.0), 0.5)
    place(fx, 2.0, reverb(st(chime()), 0.3), 0.6)    # logo sparkle
    for k in range(6):
        place(fx, 2.0 + 0.05 * k, st(blip(600, 1900), (-0.6, 0.6)[k % 2]), 0.35)
    place(fx, 2.5, st(blip(400, 1200)), 0.5)          # ENERGY pill
    place(fx, 2.94, st(can_open()), 0.9)             # can crack + fizz into FEEL-GOOD
    for t0 in (3.0, 3.25, 3.5):                       # type slams
        place(fx, t0 - 0.06, st(swish(0.12, 1500, 7000)), 0.5)
        place(fx, t0, st(thump()), 0.6)
    place(fx, 3.75, st(blip(700, 2200)), 0.4)
    for k in range(4):                                # product photos: shutter + badge blip
        place(fx, 4.0 + k * BEAT, st(shutter(), 0.2), 0.6)
        place(fx, 4.08 + k * BEAT, st(blip(500, 1600), 0.4), 0.35)
    for k in range(4):                                # claim stack jumps, one swish per eighth
        place(fx, 6.0 + k * 0.25 - 0.03, st(swish(0.14, 1200, 5000), (-0.4, 0.4)[k % 2]), 0.35)
    place(fx, 7.0, st(thump()), 0.6)
    place(fx, 7.25, st(thump()), 0.5)
    place(fx, 8.0, st(crash(1.4)), 0.6)              # the drop
    for k in range(4):                                # can landing on each beat
        place(fx, 8.0 + k * BEAT + 0.05, st(blip(900, 300)), 0.35)
    place(fx, 10.0, st(crash(0.9)), 0.55)            # collage (the reference's hi-band burst)
    for k in range(4):
        place(fx, 10.0 + 0.06 * k - 0.04, st(swish(0.16, 700, 6000), 0.5), 0.4)
    for k in range(4):                                # line-up cans pop in on sixteenths
        place(fx, 10.5 + 0.0625 * k, st(blip(500 + 150 * k, 1500 + 300 * k), (k - 1.5) * 0.4), 0.4)
    place(fx, 11.0, reverb(st(chime(("D5", "G5", "B5", "D6"))), 0.35), 0.55)
    return fx


# ---------------------------------------------------------------- mix + master
def duck(sig, kick_times, depth=0.35, rel=0.16):
    """Pump the tonal bus under each kick (the dance-pop 'breathing')."""
    g = np.ones(len(sig))
    for t0 in kick_times:
        i = int(t0 * SR)
        k = min(len(g) - i, int(0.5 * SR))
        if k > 0:
            g[i:i + k] = np.minimum(g[i:i + k], 1 - depth * np.exp(-np.arange(k) / (rel * SR)))
    return sig * g[:, None]


def render(out_wav):
    drums, tone = music()
    drop_kicks = [8.0 + k * BEAT for k in range(6)] + [11.0]
    tone = duck(tone, drop_kicks)
    mixbus = drums * 0.9 + tone * 0.8 + effects() * 0.85
    mixbus = mixbus[:int(DURATION * SR)]
    fade = int(0.4 * SR)
    mixbus[-fade:] *= np.linspace(1, 0, fade)[:, None]
    mixbus = np.tanh(mixbus * 1.2) / 1.2                # glue / soft clip
    raw = out_wav.replace(".wav", "_raw.wav")
    sf.write(raw, mixbus / np.abs(mixbus).max() * 0.7, SR, subtype="FLOAT")
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "ebur128", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    lufs = float(meas.rsplit("I:", 1)[1].split("LUFS")[0])
    gain = -14.0 - lufs
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                    f"volume={gain:.2f}dB,alimiter=limit=0.89:attack=1:release=40:level=disabled",
                    "-ar", str(SR), "-c:a", "pcm_s24le", out_wav], check=True)
    return out_wav


if __name__ == "__main__":
    import sys
    print(render(sys.argv[1] if len(sys.argv) > 1 else "mix.wav"))
