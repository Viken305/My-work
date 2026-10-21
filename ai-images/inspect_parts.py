"""Everything the dashboard shows about the parts, as JSON on stdout (run fresh so it always sees the saved project).

  python3 inspect_parts.py            -> {"parts": [...], "total": seconds, "voices": [...]}

Per part: duration, line start times and lengths, word times, scene anchors (the words the animation is pinned to),
sound effects, music beds, which lines need a new voice, and whether the rendered video is up to date.
"""
import importlib, io, json, os, re, sys
from contextlib import redirect_stdout

import timing
from project import HERE, P
from script import PARTS
from voiceover import MODEL_DIR, stale_lines

ANCHOR = re.compile(r'TM\.(?:word|end)\("(\w+)"(?:,\s*"([^"]+)")?')
VO_KEY = re.compile(r'VO\["(\w+)"\]')


def anchors(part):
    """{line: [words]} the part's animation code is pinned to; a line in VO[...] is needed but has no word anchor."""
    path = os.path.join(HERE, f"{part}.py")
    if not os.path.exists(path):
        return {}
    src = open(path).read()
    out = {}
    for k, w in ANCHOR.findall(src):
        out.setdefault(k, [])
        if w and w not in out[k]:
            out[k].append(w)
    for k in VO_KEY.findall(src):
        out.setdefault(k, [])
    return out


def part_info(part, offset):
    info = dict(id=part, stale_voice=stale_lines(part), anchors=anchors(part))
    try:
        info["lengths"] = json.load(open(os.path.join(timing.vo_dir(part), "durations.json")))
    except (OSError, ValueError):
        info["lengths"] = {}
    if not os.path.exists(os.path.join(HERE, f"{part}.py")):
        info.update(ready=False, error="no animation code yet (ask Claude to animate this part)")
        return info, 0.0
    missing_clips = [k for k, _ in PARTS[part] if not os.path.exists(os.path.join(timing.vo_dir(part), f"{k}.wav"))]
    if missing_clips:
        info.update(ready=False, error=f"no voice yet for {', '.join(missing_clips)}")
        return info, 0.0
    timing.MISSING.clear()
    try:
        with redirect_stdout(io.StringIO()):
            mod = importlib.import_module(part)
            import render
    except Exception as e:  # a line the animation needs was deleted, etc.
        info.update(ready=False, error=f"{type(e).__name__}: {e}")
        return info, 0.0
    tm = mod.TM
    info.update(
        ready=True, offset=offset, duration=mod.DURATION, missing_anchors=list(timing.MISSING),
        lines=[dict(id=k, start=mod.VO[k], length=tm.dur[k], words=[[round(a, 3), round(b, 3), w] for a, b, w in tm.words(k)])
               for k, _ in PARTS[part] if k in mod.VO],
        sfx=[[round(t, 3), k, round(g, 3)] for t, k, g in mod.sfx_events()],
        music=[[a, b, k, g] for a, b, k, g in mod.MUSIC.get("beds", [])],
        video=video_state(render, part),
        has_video=os.path.exists(os.path.join(render.build_dir(part), "video.mp4")),
    )
    return info, mod.DURATION


def video_state(render, part):
    """'final' / 'draft' (rendered with 1 motion-blur sample) / 'stale' (inputs changed since) / 'none'."""
    if not os.path.exists(os.path.join(render.build_dir(part), "video.mp4")):
        return "none"
    if render.up_to_date(part):
        return "final"
    os.environ["STUDIO_SAMPLES"] = "1"
    try:
        return "draft" if render.up_to_date(part) else "stale"
    finally:
        del os.environ["STUDIO_SAMPLES"]


def voices():
    try:
        import numpy as np
        return sorted(np.load(os.path.join(MODEL_DIR, "voices-v1.0.bin")).keys())
    except Exception:
        return [P["voice"]["name"]]


if __name__ == "__main__":
    parts, t = [], 0.0
    for part in PARTS:
        info, d = part_info(part, t)
        parts.append(info)
        t += d
    json.dump(dict(parts=parts, total=round(t, 2), voices=voices()), sys.stdout)
