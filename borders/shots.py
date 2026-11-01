"""Shot list with running times for the 3D globe version (times from film3d's narration schedule).

  python3 shots.py      -> SHOTS.md
"""
import os

import film3d as F

BEATS = {
    "H1": "Title over a full-frame globe turning in space",
    "H2": "Camera swings to Europe–Africa–Asia: France–Spain burns red (WIGGLY), Egypt's straight lines burn amber (RULER STRAIGHT), Afghanistan pops up as a slab (STRANGE)",
    "H3": "The three borders hold; the globe turns west",
    "N1": "Chapter card NATURE while the camera flies to North America; the Rio Grande, Mississippi, Missouri, Colorado and Ohio rivers burn on in blue",
    "N2": "Tilted close-up: the US–Mexico border burns along the Rio Grande, Mexico rises as a slab",
    "N3": "Dive into El Paso: the river (schematic) slides south, El Chamizal lights up on the US side; 1860s badge",
    "N4": "Year counter 1864 → 1963 (Chamizal Convention); the river swings back, the land returns",
    "N5": "Flight across the Atlantic to the Pyrenees: 3D peaks rise along the ridge, the border burns red",
    "N6": "Flight to South America: Chile rises as a long glowing slab, the Andes stand up along its edge, PACIFIC label",
    "S1": "Chapter card STRAIGHT LINES; the world's straight borders burn amber, one after another",
    "S2": "The 49th parallel burns west from Lake of the Woods to the Pacific; 1818 badge; CANADA / UNITED STATES / THE PRAIRIES",
    "S3": "Dive to Point Roberts: the tip rises as a slab below the line; a car drives from the US through Canada and back",
    "S4": "Flight to Africa: straight borders burn red one by one; 1884 Berlin Conference badge; 200+ PEOPLES pin",
    "S5": "Egypt–Sudan: the 1899 line (22° N) in amber, the 1902 line in cyan; Bir Tawil rises, 'claimed by no one'",
    "W1": "Chapter card DEALS; Namibia rises",
    "W2": "Caprivi Strip ringed; 1890 badge; the Zambezi burns on; the route to the sea is cut by a red ✕ at Victoria Falls",
    "W3": "Flight to the Wakhan Corridor: Afghanistan rises, Russian Empire (green) and British India (pink) close in, arrows stop short; 1895 badge",
    "B1": "Chapter card ACCIDENTS; dive into Baarle: 22 Belgian pieces rise inside the Netherlands, Dutch pieces inside them; café, garden, home pins",
    "B2": "Dive into one street: a 3D house with the border painted through it; the front door glows (= a Belgian house)",
    "E1": "Pull back to the whole globe: rivers (blue), rulers (red), deals and accidents (rings) light up on their words",
    "E2": "Every border on the globe glows as it turns",
    "E3": "THERE'S ALWAYS A STORY. The globe turns back to the opening pose; the last half-second blends into frame 0 (loop)",
}


def mmss(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


if __name__ == "__main__":
    keys = list(F.L)
    md = ["# Shot list: \"Why Borders Are Shaped the Way They Are\" (3D globe)", "",
          f"Full-bleed 3D globe flythrough, 1080×1920, 30 fps. **Running time {mmss(F.TOTAL)} ({F.TOTAL:.1f} s)**. "
          "One continuous camera: each beat runs from its line until the next one starts; chapter cards play while the camera flies.", "",
          "| Beat | In | Out | Length | Picture | Narration |", "|---|---|---|---|---|---|"]
    for i, k in enumerate(keys):
        start = 0.0 if i == 0 else (F.CH[F.LINE_PART[k]] if F.L[k][0] - F.CH[F.LINE_PART[k]] < 2.5 and keys[i - 1] and F.LINE_PART[keys[i - 1]] != F.LINE_PART[k] else F.L[k][0] - 0.25)
        end = F.TOTAL if i == len(keys) - 1 else (F.CH[F.LINE_PART[keys[i + 1]]] if F.LINE_PART[keys[i + 1]] != F.LINE_PART[k] else F.L[keys[i + 1]][0] - 0.25)
        md.append(f"| {k} | {mmss(start)} | {mmss(end)} | {end - start:.1f} s | {BEATS[k]} | {F.L[k][2]} |")
    md += ["", "## Chapters", "", "| Chapter | In | Out | Length |", "|---|---|---|---|"]
    chs = [(p, num, name) for p, num, name, _ in F.CHAPTERS]
    for i, (p, num, name) in enumerate(chs):
        a = F.CH[p]
        b = F.CH[chs[i + 1][0]] if i + 1 < len(chs) else F.TOTAL
        md.append(f"| {num} · {name.title()} | {mmss(a)} | {mmss(b)} | {b - a:.1f} s |")
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "SHOTS.md"), "w").write("\n".join(md) + "\n")
    print("total", mmss(F.TOTAL))
