"""Sound for the 3D globe version: narration placement, effects on the story beats, the music bed."""
import os

import film3d as F
from film3d import E, S, w

HERE = os.path.dirname(os.path.abspath(__file__))


def vo_clips():
    return [(t0, os.path.join(HERE, "build", F.LINE_PART[k], "vo", f"{k}.wav")) for k, (t0, _, _) in F.L.items()]


def sfx_events():
    ev = [(0.05, "shimmer", 0.35)]
    for part, *_ in F.CHAPTERS[1:5]:                                # chapter cards: a whoosh as the camera flies, a hit on the title
        ev += [(F.CH[part], "whoosh", 0.55), (F.CH[part] + 0.15, "low_hit", 0.45)]
    ev += [(w("H2", "wiggle") - 0.15, "swish", 0.35), (w("H2", "straight") - 0.15, "swish", 0.35), (w("H2", "strange") - 0.15, "pop", 0.45),
           (S("N1") + 0.3, "shimmer", 0.3), (w("N2", "rio") - 0.1, "riser", 0.25), (w("N2", "mexico") - 0.3, "pop", 0.3),
           (S("N3") + 0.1, "whoosh", 0.4), (w("N3", "shifted"), "pour", 0.35), (w("N3", "piece"), "pop", 0.4),
           (w("N4", "hundred") - 0.1, "tick_roll", 0.35), (w("N4", "nineteen"), "stamp", 0.5), (w("N4", "hand"), "swish", 0.4),
           (E("N4") + 0.1, "whoosh", 0.5), (w("N5", "split") - 0.2, "riser", 0.2), (w("N5", "pyrenees") - 0.3, "rumble_strip", 0.25),
           (E("N5") + 0.2, "whoosh", 0.45), (w("N6", "chile") - 0.2, "low_hit", 0.35), (w("N6", "andes") - 0.4, "rumble_strip", 0.2),
           (S("S1") - 0.4, "shimmer", 0.35), (E("S1") + 0.1, "whoosh", 0.4), (w("S2", "eighteen") - 0.15, "stamp", 0.5),
           (w("S2", "forty") - 0.2, "riser", 0.25), (E("S2") + 0.1, "whoosh", 0.45), (w("S3", "point") - 0.2, "low_hit", 0.35),
           (w("S3", "drive") - 0.1, "car_pass", 0.35), (E("S3") + 0.1, "whoosh", 0.45), (w("S4", "late") - 0.2, "stamp", 0.45),
           (w("S4", "split") - 0.1, "tick_roll", 0.25), (E("S4") + 0.1, "whoosh", 0.4), (w("S5", "two") - 0.1, "swish", 0.35),
           (w("S5", "bir") - 0.2, "low_hit", 0.35), (S("W1") + 0.1, "low_hit", 0.3), (w("W2", "caprivi") - 0.1, "swish", 0.35),
           (w("W2", "germany's") - 0.2, "stamp", 0.45), (w("W2", "zambezi") - 0.4, "pour", 0.3), (w("W2", "falls") - 0.1, "smash", 0.3),
           (E("W2") + 0.1, "whoosh", 0.45), (w("W3", "wakhan") - 0.1, "swish", 0.35), (w("W3", "buffer") - 0.2, "stamp", 0.45),
           (w("W3", "never") - 0.1, "riser", 0.2), (w("B1", "baarle") - 0.6, "descend", 0.35)]
    tb = w("B1", "baarle")
    ev += [(tb - 0.1 + 0.11 * i, "pop", 0.18) for i in range(0, 12, 2)]
    ev += [(w("B1", x) - 0.05, "pop", 0.35) for x in ("cafes", "gardens", "homes")]
    ev += [(S("B2") - 0.3, "whoosh", 0.4), (w("B2", "front"), "glass_ting", 0.35), (S("E1") + 0.1, "whoosh", 0.5),
           (w("E1", "rivers"), "shimmer", 0.25), (w("E1", "rulers"), "swish", 0.3), (w("E1", "deals"), "swish", 0.3),
           (w("E1", "accidents"), "pop", 0.35), (w("E2", "line"), "shimmer", 0.35), (S("E3") + 0.2, "low_hit", 0.35)]
    return ev


def music():
    return dict(beds=[(0.0, F.TOTAL, "voyage", 0.6)])
