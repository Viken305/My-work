"""Narration for Ep. 04 'Why is the sky blue?'. GAP = silence before a line, in seconds.

Facts checked:
  * Sunlight is a mix of all visible wavelengths (roughly 380-750 nm); it looks white.
  * Light from the Sun takes about 8 minutes 20 seconds to reach Earth.
  * Air is ~78 % nitrogen and ~21 % oxygen; N2/O2 molecules (~0.3 nm) are ~1,000x smaller than visible wavelengths.
  * The light's oscillating field drives the molecules' electrons, which re-radiate in (nearly) all directions:
    Rayleigh scattering, with intensity proportional to 1 / wavelength^4.
  * (700 nm / 450 nm)^4 ~ 5.8, (650/450)^4 ~ 4.4 -> blue is scattered roughly five times more than red.
  * The sky isn't violet: less violet in sunlight, some absorbed high in the atmosphere, and our eyes are far less
    sensitive to violet than to blue.
  * At sunset sunlight crosses up to ~38x more air (air mass at the horizon), so blue is scattered out; reds remain.
  * On Mars, fine dust makes daytime skies butterscotch and sunsets blue (Curiosity / Spirit images).
"""

LINES = [
    ("01", "Look up on a clear day, and the sky is blue. Obviously."),
    ("02", "But the light up there comes from the Sun. And sunlight isn't blue. It's white."),
    ("03", "White light is really every colour, mixed together."),
    ("04", "And each colour is a wave. Red waves are long and lazy. Blue waves are short and tight."),
    ("05", "For about eight minutes, they race through empty space, until they hit something."),
    ("06", "Our atmosphere."),
    ("07", "Air is mostly nitrogen and oxygen. Molecules so tiny, a single wave of light is a thousand times bigger."),
    ("08", "When a wave rolls past, it shakes the molecule's electrons, and the molecule throws light back out, in every direction."),
    ("09", "This is called scattering. And here's the trick: tiny molecules scatter short waves far better than long ones."),
    ("10", "Blue light gets scattered about five times more than red."),
    ("11", "So red, orange and yellow mostly fly straight through, while blue pinballs from molecule to molecule, all across the sky."),
    ("12", "Wherever you look, blue light is coming at you from every direction. That's the blue sky."),
    ("13", "But wait. Violet waves are even shorter. So why isn't the sky violet?"),
    ("14", "The Sun sends us less violet to begin with, some gets soaked up high in the air, and our eyes are just much better at seeing blue."),
    ("15", "Now, watch the sunset."),
    ("16", "When the Sun is low, its light has to cross up to forty times more air to reach you."),
    ("17", "By the time it arrives, the blue has been scattered away. What's left are the long waves. Orange, and red."),
    ("18", "And on Mars, with its thin, dusty air, it's the other way around. Butterscotch days, and blue sunsets."),
    ("19", "Same Sun. Different air."),
    ("20", "The physics of everyday things."),
]

GAP = {"02": 0.5, "03": 0.5, "04": 0.5, "05": 0.6, "06": 0.4, "07": 0.8, "08": 0.6, "09": 0.6, "10": 0.5, "11": 0.5,
       "12": 0.5, "13": 0.8, "14": 0.5, "15": 0.8, "16": 0.6, "17": 0.5, "18": 0.9, "19": 0.8, "20": 0.8}
