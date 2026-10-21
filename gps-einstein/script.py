"""Narration for "Your Phone Does Einstein's Math" (9:16 Short). One entry per line of voice-over.

The text lives in project.json (edited in the dashboard). Numbers are written the way they must be spoken; captions
show them as digits again through DISPLAY.
"""
from project import P

PARTS = {part["id"]: [(ln["id"], ln["text"]) for ln in part["lines"]] for part in P["parts"]}

# spoken words -> what the captions show
DISPLAY = [tuple(x) for x in P["display"]]
