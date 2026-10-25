"""Narration for Ep. 03 'Why does popcorn pop?'. GAP = silence before a line, in seconds.

Facts checked:
  * Popcorn kernels pop best at about 13.5-14 % moisture by weight.
  * The hull (pericarp) is tough and nearly watertight, so the water can't escape as it heats.
  * Inside, the water turns to superheated steam; pressure reaches roughly 135 psi, about 9 atmospheres.
  * The starch gelatinises (turns into a hot, molten gel) as it heats.
  * Popping happens at about 180 C (Virot & Ponomarenko, J. R. Soc. Interface, 2015, filmed at 2,900 frames/s).
  * The gel blows out into a foam that sets almost instantly as it cools; volume grows by up to ~40x.
  * The 'pop' sound comes from the sudden release of water vapour (the pressure drop), not from the hull cracking;
    the authors liken it to a champagne cork.
  * Kernels jump: a 'leg' of starch pushes against the pan and flips the kernel, within a few milliseconds.
  * Unpopped kernels ('old maids') usually have a damaged or leaky hull, or too little water, so pressure never builds.
"""

LINES = [
    ("01", "This is a corn kernel. Hard as a pebble."),
    ("02", "And in about a minute, it's going to explode."),
    ("03", "Inside, locked in the starch, is a little water. About fourteen percent of its weight."),
    ("04", "And wrapped around it all, a shell so tough, it's almost airtight."),
    ("05", "Now add heat."),
    ("06", "Normally, water boils away at a hundred degrees. But here, the steam has nowhere to go."),
    ("07", "So the pressure climbs. To around nine times the air around you."),
    ("08", "Meanwhile, the starch softens into a hot, molten gel."),
    ("09", "Then, at about one hundred and eighty degrees,"),
    ("10", "the shell gives way."),
    ("11", "The steam bursts out, and the gel blows into a foam, up to forty times bigger, and sets solid almost instantly."),
    ("12", "And that pop? It isn't the shell cracking. It's the steam escaping, like a cork from a bottle of champagne."),
    ("13", "Popcorn even jumps. A leg of starch kicks the pan, and flips the kernel into the air, in just a few thousandths of a second."),
    ("14", "And the duds at the bottom? Their shells leaked, so the pressure never built."),
    ("15", "So every bowl of popcorn is really hundreds of tiny pressure cookers, failing at exactly the right moment."),
    ("16", "The physics of everyday things."),
]

GAP = {"02": 0.45, "03": 2.2, "04": 0.55, "05": 0.9, "06": 0.8, "07": 0.5, "08": 0.6, "09": 0.8, "10": 0.7,
       "11": 2.2, "12": 1.1, "13": 1.1, "14": 1.1, "15": 1.1, "16": 1.3}
