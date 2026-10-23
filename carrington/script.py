"""Narration for "The Day the Sun Hit Us" (9:16 Short, ~2:20). One entry per line of voice-over.

Numbers are written the way they must be spoken; captions show them as digits again through DISPLAY.
Every claim is checked in SCRIPT.md (sources at the end).
"""

PARTS = {
    "part1": [   # hook: miners making breakfast at 1 a.m.
        ("H1", "On the night of September the second, eighteen fifty nine, gold miners in the Rocky Mountains woke up, and started making breakfast."),
        ("H2", "It was one in the morning. The sky was so bright, they thought the sun was up."),
        ("H3", "And in a way... it was."),
    ],
    "part2": [   # Carrington's sketch
        ("A1", "The day before, in his observatory south of London, astronomer Richard Carrington was drawing sunspots."),
        ("A2", "At eighteen minutes past eleven, two beads of blinding white light burst out of them. In about five minutes, they were gone."),
        ("A3", "He had just seen the first solar flare ever recorded."),
    ],
    "part3": [   # the crossing
        ("B1", "Its light reached Earth in about eight minutes. But the sun had also hurled a vast cloud of magnetised gas into space."),
        ("B2", "Clouds like that usually take a few days to reach us. This one took just seventeen point six hours."),
        ("B3", "And it was aimed right at Earth."),
    ],
    "part4": [   # the shield
        ("C1", "It slammed into Earth's magnetic field, and squeezed it."),
        ("C2", "At Kew Observatory near London, the instruments recording the field were driven right off the scale."),
        ("C3", "The biggest magnetic storm in recorded history had begun."),
    ],
    "part5": [   # the aurora
        ("D1", "Then the sky caught fire."),
        ("D2", "Auroras, usually seen only near the poles, blazed over Cuba, Hawaii, and even Panama."),
        ("D3", "In the northeastern United States, people could read a newspaper by their light."),
    ],
    "part6": [   # the telegraph
        ("E1", "And the telegraph, the internet of eighteen fifty nine, went haywire. Wires threw sparks, and some operators got electric shocks."),
        ("E2", "Between Boston and Portland, two operators unplugged their batteries completely,"),
        ("E3", "and kept on sending messages, powered by the sky alone."),
    ],
    "part7": [   # the near miss
        ("F1", "Back then, it was a wonder. Today, a storm like that could knock out power grids and satellites."),
        ("F2", "And in July twenty twelve, one nearly did. A cloud at least as strong blasted off the sun."),
        ("F3", "It missed us. But nine days earlier, the spot it came from was facing Earth."),
    ],
}

# spoken words -> what the captions show
DISPLAY = [
    ("September the second eighteen fifty nine", "September 2nd, 1859"), ("eighteen fifty nine", "1859"),
    ("one in the morning", "1 a.m."), ("eighteen minutes past eleven", "11:18 a.m."), ("five minutes", "5 minutes"),
    ("eight minutes", "8 minutes"), ("seventeen point six hours", "17.6 hours"), ("twenty twelve", "2012"),
    ("nine days", "9 days"),
]

if __name__ == "__main__":
    WPS = 236 / 105
    total = 0
    for part, lines in PARTS.items():
        n = sum(len(s.split()) for _, s in lines)
        total += n
        print(f"{part}: {n:3d} words  ~{n / WPS:5.1f} s")
    print(f"total: {total} words  ~{total / WPS:.0f} s")
