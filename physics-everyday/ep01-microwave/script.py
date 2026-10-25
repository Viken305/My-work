"""Episode 1 narration: why microwaves heat unevenly (and how to measure the speed of light with chocolate).

Fact notes
- Domestic microwave ovens run at 2.45 GHz; wavelength = c / f = 3e8 / 2.45e9 = 12.2 cm.
- Standing waves in the cavity: neighbouring hot spots sit half a wavelength apart, about 6 cm.
- Heating is dielectric: polar water molecules keep re-aligning with the oscillating field and jostle their neighbours.
  (Not "friction between molecules" in the everyday sense, and not "cooking from the inside out".)
- Penetration depth in watery food at 2.45 GHz is roughly 1-2 cm; thicker centres warm by conduction.
- Chocolate test: 2 x 6.1 cm x 2.45e9 /s = 3.0e8 m/s, the speed of light.
"""

LINES = [
    ("01", "Ever notice your microwave leaves food scorching hot... and ice cold, in the same bite?"),
    ("02", "Here's what's actually going on."),
    ("03", "Hidden behind the buttons is a magnetron. It turns electricity into microwaves, a kind of invisible light."),
    ("04", "They get piped into the box, and bounce around inside."),
    ("05", "These waves wiggle back and forth two point four five billion times every second."),
    ("06", "Water molecules are lopsided. One end is slightly negative, the other slightly positive."),
    ("07", "So every time the wave flips, they twist to follow it, crashing into their neighbors."),
    ("08", "All that jostling is heat."),
    ("09", "And no, it doesn't cook from the inside out. Microwaves only reach a centimeter or two into food. The middle has to wait for the heat to creep in."),
    ("10", "Now, the hot spots. Those waves bounce off the metal walls."),
    ("11", "Where they line up, they add up. Where they cancel out, almost nothing happens."),
    ("12", "So you get a pattern of hot spots and dead spots, about six centimeters apart."),
    ("13", "That's why the plate spins. It drags your food through the hot spots."),
    ("14", "Still cold in the middle? Stop halfway, give it a stir, and let it stand for a minute."),
    ("15", "Want to see the pattern yourself? Take out the plate, and heat a bar of chocolate for twenty seconds."),
    ("16", "Measure the gap between the melted spots, double it, and multiply by two point four five billion."),
    ("17", "You just measured the speed of light. With chocolate."),
]
GAP = {"02": 0.25, "03": 0.35, "05": 0.4, "06": 0.45, "08": 0.2, "09": 0.5, "10": 0.6, "13": 0.5, "14": 0.5, "15": 0.6, "17": 0.45}
