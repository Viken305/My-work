"""Narration for "The Day the Earth Rang Like a Bell" (9:16 Short, ~2:25). One entry per line of voice-over.

Numbers are written the way they must be spoken (TTS reads "1960" as "one thousand nine hundred..."); captions show
them as digits again through DISPLAY.
"""

PARTS = {
    "part1": [   # hook: the planet rings, then back to where it started
        ("H1", "In May nineteen sixty, the whole Earth started to ring. Like a bell."),
        ("H2", "Instruments around the world felt the planet itself swelling and shrinking, slowly. For days."),
        ("H3", "It was the biggest earthquake ever recorded. And it started here."),
    ],
    "part2": [   # the crack
        ("A1", "Off the coast of Chile, one plate of the Earth's crust slides under another. Usually, it doesn't slide. It sticks."),
        ("A2", "For centuries, the strain kept building. Then, on the twenty second of May, at eleven minutes past three in the afternoon, it let go."),
        ("A3", "A crack about a thousand kilometres long tore open along the coast. In places, the rock lurched by as much as twenty metres."),
    ],
    "part3": [   # how big
        ("B1", "In the city of Valdivia, the ground shook for about ten minutes."),
        ("B2", "Scientists rated it nine point five. Every step up that scale means about thirty two times more energy."),
        ("B3", "So this one released thousands of times more energy than the earthquake that destroyed Haiti's capital in twenty ten."),
    ],
    "part4": [   # the ocean
        ("C1", "Then the sea moved. Waves up to twenty five metres high hit the coast of Chile. Somewhere between one and six thousand people died."),
        ("C2", "But the tsunami kept going, across the entire Pacific, almost as fast as a passenger jet."),
        ("C3", "Fifteen hours later, it struck Hawaii and killed sixty one people. Almost a day later, it reached Japan, seventeen thousand kilometres away, and killed about a hundred and forty more."),
    ],
    "part5": [   # the bell
        ("D1", "And the energy didn't stay near Chile. It travelled through the whole planet, until the Earth itself started to vibrate."),
        ("D2", "Its deepest note was one slow swing, about every fifty four minutes. A bell far too low to hear."),
        ("D3", "It was the first time scientists clearly heard the whole planet ring. And its notes told them what the inside of the Earth is like."),
    ],
    "part6": [   # what it left behind
        ("E1", "Two days after the quake, a volcano nearby erupted."),
        ("E2", "Parts of the coast sank by about two metres. The sea flooded in, and whole forests drowned. Many of those dead trees are still standing in the water today."),
        ("E3", "Since then, instruments have heard the Earth ring after every great earthquake. But never as loudly as in nineteen sixty."),
    ],
}

# spoken words -> what the captions show
DISPLAY = [
    ("nineteen sixty", "1960"), ("twenty ten", "2010"), ("twenty second of May", "22 May"),
    ("eleven minutes past three in the afternoon", "3:11 pm"), ("a thousand kilometres", "1,000 km"),
    ("twenty metres", "20 metres"), ("ten minutes", "10 minutes"), ("nine point five", "9.5"),
    ("thirty two times", "32×"), ("twenty five metres", "25 metres"), ("one and six thousand", "1,000 and 6,000"),
    ("Fifteen hours", "15 hours"), ("sixty one", "61"), ("seventeen thousand kilometres", "17,000 km"),
    ("a hundred and forty", "140"), ("fifty four minutes", "54 minutes"), ("two metres", "2 metres"),
]

if __name__ == "__main__":
    WPS = 236 / 105   # words per second of the finished Krakatoa Short (voice, pauses and visual holds included)
    total = 0
    for part, lines in PARTS.items():
        n = sum(len(s.split()) for _, s in lines)
        total += n
        print(f"{part}: {n:3d} words  ~{n / WPS:5.1f} s")
    print(f"total: {total} words  ~{total / WPS:.0f} s  (+ ~4 s title card)")
