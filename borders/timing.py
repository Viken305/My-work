"""Narration timing: where each line starts (schedule) and when each word is spoken (align).

Word times come from the real audio: pauses in the waveform are matched to the punctuation in the text, then the words
inside each spoken stretch are spread by phoneme length (espeak phonemes, the same front-end the TTS uses).
Results are cached in build/<part>/vo/words.json.
"""
import json, os, re

import numpy as np
import soundfile as sf

from script import PARTS

HERE = os.path.dirname(os.path.abspath(__file__))


def vo_dir(part):
    return os.path.join(HERE, "build", part, "vo")


def durations(part):
    return json.load(open(os.path.join(vo_dir(part), "durations.json")))


def schedule(part, first=0.4, gap=0.5, extra=None):
    """Start time of each line: lines follow each other with `gap` seconds between, plus optional extra per line."""
    dur = durations(part)
    vo, t = {}, first
    for k, _ in PARTS[part]:
        t += (extra or {}).get(k, 0.0)
        vo[k] = round(t, 3)
        t += dur[k] + gap
    return vo, t


def _phoneme_weights(words):
    try:
        import espeakng_loader
        from phonemizer.backend.espeak.wrapper import EspeakWrapper
        EspeakWrapper.set_library(espeakng_loader.get_library_path())
        EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
        from phonemizer import phonemize
        ph = phonemize([re.sub(r"[^\w']", " ", w) for w in words], language="en-us", backend="espeak", strip=True)
        return [max(1.0, len(p.replace(" ", "")) + 0.8 * sum(ch in "aeiouæɑɔəɛɪʊʌɜ" for ch in p)) for p in ph]
    except Exception:
        return [max(1.0, len(w)) for w in words]


def _speech_segments(wav):
    x, sr = sf.read(wav)
    if x.ndim > 1:
        x = x.mean(1)
    hop = int(sr * 0.01)
    rms = np.sqrt(np.convolve(x ** 2, np.ones(hop * 3) / (hop * 3), "same")[::hop])
    thr = max(rms.max() * 0.04, 1e-4)
    loud = rms > thr
    idx = np.where(loud)[0]
    t0, t1 = idx[0] * 0.01, idx[-1] * 0.01 + 0.03
    gaps, run = [], None                   # silent stretches strictly inside the speech
    for i in range(idx[0], idx[-1]):
        if not loud[i] and run is None:
            run = i
        elif loud[i] and run is not None:
            if i - run >= 9:               # >= 90 ms of silence
                gaps.append((run * 0.01, i * 0.01))
            run = None
    return t0, t1, gaps


def _match(expected, gaps, strength):
    """Monotonic matching of pauses to punctuation breaks (DP). Returns [(break_index, gap)]."""
    n, m = len(expected), len(gaps)
    INF = 1e9
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            c0 = cost[i][j]
            if c0 >= INF:
                continue
            if i < n and c0 + 0.35 * strength[i] < cost[i + 1][j]:         # break with no pause
                cost[i + 1][j], back[i + 1][j] = c0 + 0.35 * strength[i], (i, j, None)
            if j < m and c0 + 0.25 < cost[i][j + 1]:                        # pause inside a phrase
                cost[i][j + 1], back[i][j + 1] = c0 + 0.25, (i, j, None)
            if i < n and j < m:
                g = gaps[j]
                cc = c0 + (expected[i] - (g[0] + g[1]) / 2) ** 2 / 0.25
                if cc < cost[i + 1][j + 1]:
                    cost[i + 1][j + 1], back[i + 1][j + 1] = cc, (i, j, (i, g))
    out, i, j = [], n, m
    while (i, j) != (0, 0):
        pi, pj, pair = back[i][j]
        if pair:
            out.append(pair)
        i, j = pi, pj
    return sorted(out)


def align_line(text, wav):
    """[(start, end, word)] relative to the start of the clip."""
    words = text.split()
    t0, t1, gaps = _speech_segments(wav)
    wts = _phoneme_weights(words)
    cum = np.cumsum(wts) / sum(wts)
    breaks = [i for i, w in enumerate(words[:-1]) if w[-1] in ".,?!;:"]
    expected = [t0 + (t1 - t0) * cum[i] for i in breaks]
    strength = [2 if words[i][-1] in ".?!" else 1 for i in breaks]
    pairs = _match(expected, gaps, strength)
    anchors = [(-1, t0, t0)] + [(breaks[k], g[0], g[1]) for k, g in pairs] + [(len(words) - 1, t1, t1)]
    out = []
    for (wa, _, sa), (wb, eb, _) in zip(anchors[:-1], anchors[1:]):
        g = list(range(wa + 1, wb + 1))
        ws = [wts[i] for i in g]
        acc = sa
        for i, wt in zip(g, ws):
            d = (eb - sa) * wt / sum(ws)
            out.append((round(float(acc), 3), round(float(acc + d), 3), words[i]))
            acc += d
    return out


def words(part):
    """{line_key: [(start, end, word)]} relative to each clip, cached."""
    path = os.path.join(vo_dir(part), "words.json")
    src = os.path.join(vo_dir(part), "durations.json")
    if os.path.exists(path) and os.path.getmtime(path) >= os.path.getmtime(src):
        return {k: [tuple(x) for x in v] for k, v in json.load(open(path)).items()}
    res = {k: align_line(text, os.path.join(vo_dir(part), f"{k}.wav")) for k, text in PARTS[part]}
    json.dump(res, open(path, "w"), indent=0)
    return res


class Timing:
    """Absolute word times for one part, given its line schedule."""

    def __init__(self, part, vo):
        self.vo, self.dur = vo, durations(part)
        self.text = dict(PARTS[part])
        self.rel = words(part)

    def words(self, k):
        return [(self.vo[k] + a, self.vo[k] + b, w) for a, b, w in self.rel[k]]

    def word(self, k, phrase, end=False):
        """Start (or end) time of the first occurrence of `phrase` (one or more words) in line k."""
        ws = self.rel[k]
        target = [re.sub(r"[^\w']", "", p).lower() for p in phrase.split()]
        clean = [re.sub(r"[^\w']", "", w).lower() for _, _, w in ws]
        for i in range(len(clean) - len(target) + 1):
            if clean[i:i + len(target)] == target:
                return self.vo[k] + (ws[i + len(target) - 1][1] if end else ws[i][0])
        raise KeyError((k, phrase))

    def end(self, k):
        return self.vo[k] + self.rel[k][-1][1]
