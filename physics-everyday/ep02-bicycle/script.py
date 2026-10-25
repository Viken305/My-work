"""Narration for Ep. 02 'Why don't bikes fall over?'. GAP = silence before a line, in seconds.

Facts checked:
  * Gyroscopic effect of the wheels exists but is small at normal riding speeds.
  * David E. H. Jones (a chemist) built bikes in 1970 with an extra, counter-rotating front wheel to cancel the
    gyroscopic effect, and could still ride them ("The stability of the bicycle", Physics Today, April 1970).
  * Trail: the steering axis meets the ground ahead of the front tyre's contact point; typically ~5-8 cm on a
    road/city bike. A shopping-trolley caster works the same way (wheel trails behind its pivot).
  * Steering into the fall: when a bike leans, the front assembly steers toward the lean (trail + front-end mass),
    moving the contact line back under the centre of mass. Riders do the same, mostly unconsciously.
  * A riderless bike is self-stable within a speed range (for the 'benchmark' bike roughly 4-6 m/s).
  * Kooijman, Meijaard, Papadopoulos, Ruina, Schwab, Science 332 (2011): a bike with no gyroscopic effect and
    no (slightly negative) trail was still self-stable, thanks to where its masses were placed.
"""

LINES = [
    ("01", "You've ridden a bike a thousand times."),
    ("02", "So here's a question almost nobody can answer."),
    ("03", "Why doesn't it fall over?"),
    ("04", "Most people say: the spinning wheels. They act like a gyroscope."),
    ("05", "Nope."),
    ("06", "In 1970, a chemist bolted on an extra wheel, spinning backwards, to cancel that out."),
    ("07", "And he could still ride it."),
    ("08", "So what's really going on? Look at the front wheel."),
    ("09", "Draw a line through the steering. It hits the road here."),
    ("10", "But the tyre touches down a few centimetres behind it. That gap is called trail."),
    ("11", "It's the same trick that makes a shopping trolley wheel swing around and follow."),
    ("12", "Now watch what happens when a bike starts to tip."),
    ("13", "Lean left, and the front wheel swings left too."),
    ("14", "That steers the tyres right back under your weight, and you're upright again."),
    ("15", "You do this constantly, without even noticing."),
    ("16", "And here's the wild part."),
    ("17", "Push a bike with nobody on it, and it catches its own falls."),
    ("18", "In 2011, scientists built a bike with no gyro effect and no trail, and it still balanced itself, just from where its weight sat."),
    ("19", "So the real answer? Lots of little effects, working together."),
    ("20", "And the biggest one is you, steering into the fall."),
    ("21", "Follow for more physics of everyday things."),
]

GAP = {"02": 0.15, "03": 0.2, "04": 0.75, "05": 0.3, "06": 0.45, "07": 0.25, "08": 0.6, "09": 0.3, "10": 0.3, "11": 0.45,
       "12": 0.6, "13": 0.3, "14": 0.25, "15": 0.35, "16": 0.6, "17": 0.25, "18": 0.6, "19": 0.6, "20": 0.25, "21": 0.8}
