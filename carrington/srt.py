"""English subtitles for the full film:  python3 srt.py  -> out/captions_en.srt (lines as shown in the captions)"""
import importlib, os

from captions import displayed
from lantern import HERE
from render import PARTS


def stamp(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


if __name__ == "__main__":
    out, offset, n = [], 0.0, 0
    for name in PARTS:
        mod = importlib.import_module(name)
        for p in mod.CAP.phrases:
            n += 1
            text = " ".join(w["text"] for w in p["words"])
            out.append(f"{n}\n{stamp(offset + p['t0'])} --> {stamp(offset + p['t1'] + 0.2)}\n{text}\n")
        offset += mod.DURATION
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    open(os.path.join(HERE, "out", "captions_en.srt"), "w").write("\n".join(out))
    print(n, "cues", f"{offset:.1f}s")
