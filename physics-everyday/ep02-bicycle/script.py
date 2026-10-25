"""Narration for Ep. 02, test section (first ~20 s). GAP = silence before a line, in seconds.

Facts:
  * Gyroscope myth: the spinning wheels' gyroscopic effect exists but is small at riding speed.
  * David E. H. Jones (a chemist) built bikes in 1970 with an extra front wheel spun backwards to cancel the
    gyroscopic effect, and could still ride them ("The stability of the bicycle", Physics Today, April 1970).
"""

LINES = [
    ("01", "You've ridden a bike a thousand times."),
    ("02", "So here's a question almost nobody can answer."),
    ("03", "Why doesn't it fall over?"),
    ("04", "Most people say: the spinning wheels. They act like a gyroscope."),
    ("05", "Nope."),
    ("06", "In 1970, a chemist bolted on an extra wheel, spinning backwards, to cancel that out."),
    ("07", "And he could still ride it."),
]

GAP = {"02": 0.15, "03": 0.2, "04": 0.75, "05": 0.3, "06": 0.45, "07": 0.25}
