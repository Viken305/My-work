"""project.json: the editable settings of this video (script, voice, caption words, look, sound, posting kit).

The dashboard (../studio) edits this file; every pipeline module reads its settings from here.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "project.json")


def load():
    with open(PATH) as f:
        return json.load(f)


P = load()


def rgb(hex_):
    h = hex_.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def palette(name):
    return rgb(P["style"]["palette"][name])
