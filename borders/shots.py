"""Shot list with running times, from the real narration lengths (build/<part>/vo/durations.json).

  python3 shots.py      -> prints the table and writes SHOTS.md
Timing rule: each section starts 0.4 s in, lines are 0.45 s apart, and each section ends 0.6 s after its last line.
"""
import os

from script import PARTS
from timing import durations

FIRST, GAP, TAIL = 0.4, 0.45, 0.6
# (shot, starts on line, frame, picture, motion)
SHOTS = [
    ("1A", "H1", "", "World map on paper, every border thin grey", "Slow push-in; borders flicker in country by country"),
    ("1B", "H2", "frame_1", "Three red rings: Pyrenees *wiggly*, Egypt–Sudan *ruler straight*, Wakhan *just strange*", "Each ring is hand-drawn on its word"),
    ("1C", "H3", "", "Title: *Why Are Borders Shaped Like This?*", "Map dims, title types on in serif"),
    ("2A", "N1", "frame_2", "US–Mexico: the Rio Grande traces in blue, the red border rides on it", "River draws El Paso → Gulf on \"Rio Grande\""),
    ("2B", "N3", "", "France–Spain: the Pyrenees in relief shading, border along the ridge", "Border draws along the crest"),
    ("2C", "N4", "", "Split screen: river + ridge, labels *easy to see / hard to cross*", "Two quick stamps"),
    ("3A", "S1", "", "A ruler and pencil draw a line across a blank paper map", "Pencil draws, ruler slides away"),
    ("3B", "S2", "", "US–Canada: the 49th parallel, \"1818\" date stamp, prairie", "Line snaps straight west across the prairies"),
    ("3C", "S3", "frame_3", "Africa: every straight border lights up red, ruler on 22° N", "Red lines appear one by one"),
    ("4A", "W1", "", "Card: *the strange shapes are deals*, handshake stamp", "Stamp"),
    ("4B", "W2", "frame_4", "Namibia + Caprivi Strip, the Zambezi, the dashed route crossed out at Victoria Falls", "Strip grows out of Namibia; route dashes east, red ✕ at the falls"),
    ("4C", "W3", "frame_5", "Wakhan Corridor between \"Russian Empire\" and \"British India\"", "Both empires' colours slide in, stop at the corridor"),
    ("5A", "B1", "", "Baarle: patchwork of Belgian and Dutch pieces (schematic), zoom to one street", "Pieces pop in, push into the street"),
    ("5B", "B2", "frame_6", "A house with the border through it; front door in Belgium", "Border paints across pavement and up the wall"),
    ("5C", "B3", "", "Pull back to the world: rivers blue, straight lines red, deals circled", "Fast pull-back; hold; fade to paper (loops to 1A)"),
]


def lines():
    """Every narration line with its start and end on the full timeline, plus each section's end."""
    out, t0, ends = {}, 0.0, {}
    for part, ls in PARTS.items():
        d = durations(part)
        t = t0 + FIRST
        for k, txt in ls:
            out[k] = (round(t, 2), round(t + d[k], 2), txt)
            t += d[k] + GAP
        t0 = t - GAP + TAIL
        ends[part] = round(t0, 2)
    return out, round(t0, 2)


def mmss(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def table():
    L, total = lines()
    keys = [k for p in PARTS.values() for k, _ in p]
    rows = []
    for i, (shot, k, frame, pic, motion) in enumerate(SHOTS):
        start = 0.0 if i == 0 else L[k][0] - 0.25
        end = total if i == len(SHOTS) - 1 else L[SHOTS[i + 1][1]][0] - 0.25
        a, b = keys.index(k), keys.index(SHOTS[i + 1][1]) if i + 1 < len(SHOTS) else len(keys)
        vo = " ".join(L[x][2] for x in keys[a:b])
        rows.append((shot, start, end, frame, pic, motion, vo))
    return rows, total


if __name__ == "__main__":
    rows, total = table()
    md = ["# Shot list: \"Why Borders Are Shaped the Way They Are\"", "",
          f"Paper Atlas style, 1080×1920, 30 fps. **Running time {mmss(total)} ({total:.1f} s)**, {len(rows)} shots. "
          "Times come from the generated narration (Kokoro af_heart); cuts land 0.25 s before the line that opens the shot. "
          "Style frames are in `out/` (`frame_1.png` … `frame_6.png`, board `style_frames.png`).", "",
          "| Shot | In | Out | Length | Frame | Picture | Motion | Narration |", "|---|---|---|---|---|---|---|---|"]
    for shot, s, e, frame, pic, motion, vo in rows:
        md.append(f"| {shot} | {mmss(s)} | {mmss(e)} | {e - s:.1f} s | {frame or '—'} | {pic} | {motion} | {vo} |")
    secs = {}
    for shot, s, e, *_ in rows:
        secs.setdefault(shot[0], [s, e])[1] = e
    names = {"1": "Hook", "2": "Nature", "3": "Straight lines", "4": "Deals", "5": "Baarle + ending"}
    md += ["", "## Sections", "", "| Section | In | Out | Length |", "|---|---|---|---|"]
    for k, (s, e) in secs.items():
        md.append(f"| {k} · {names[k]} | {mmss(s)} | {mmss(e)} | {e - s:.1f} s |")
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "SHOTS.md"), "w").write("\n".join(md) + "\n")
    for shot, s, e, *_ in rows:
        print(shot, mmss(s), mmss(e), f"{e - s:.1f}")
    print("total", mmss(total))
