"""Narration for "The Loudest Sound Ever Heard" (9:16 Short, ~1:45). One entry per line of voice-over.

Numbers are written the way they must be spoken (TTS reads "1883" as "one thousand eight hundred..."); captions show
them as digits again through DISPLAY.
"""

PARTS = {
    "part1": [   # hook: the mystery on Rodrigues, back across the ocean, the blast
        ("H1", "In eighteen eighty-three, police on a tiny island in the Indian Ocean heard what sounded like distant cannon fire."),
        ("H2", "But there were no ships. The sound had come from almost five thousand kilometres away."),
        ("H3", "From here."),
    ],
    "part2": [   # how loud
        ("A1", "Sailors on a ship sixty four kilometres away wrote that the blast burst the eardrums of half the crew."),
        ("A2", "A hundred and sixty kilometres away, a pressure gauge at a gas works recorded a huge spike."),
        ("A3", "From it, scientists estimate the sound there was about a hundred and seventy two decibels. Louder than a jet engine up close."),
    ],
    "part3": [   # how far
        ("B1", "And it kept going. For four hours, the sound crossed the ocean."),
        ("B2", "That was the cannon fire on Rodrigues, almost five thousand kilometres away."),
        ("B3", "No sound in recorded history has been heard that far."),
    ],
    "part4": [   # the part nobody heard
        ("C1", "But most of the wave was too low for any ear to hear."),
        ("C2", "Barometers around the world picked it up. The pressure jumped again, and again, about every thirty four hours, for five days."),
        ("C3", "The wave went around the whole planet, three to four times in each direction."),
    ],
    "part5": [   # the cost, the sky, the child
        ("D1", "Back at Krakatoa, most of the island was gone. Tsunamis over thirty metres high struck the coasts. About thirty six thousand people died."),
        ("D2", "Ash spread around the world. For months, sunsets glowed blood red."),
        ("D3", "Then, in nineteen twenty seven, something rose from the sea in the same place."),
        ("D4", "Anak Krakatau. The child of Krakatoa. And it is still active today."),
    ],
}

# spoken words -> what the captions show
DISPLAY = [
    ("eighteen eighty-three", "1883"), ("nineteen twenty seven", "1927"),
    ("five thousand kilometres", "5,000 km"), ("sixty four kilometres", "64 km"),
    ("a hundred and sixty kilometres", "160 km"), ("a hundred and seventy two decibels", "172 decibels"),
    ("thirty four hours", "34 hours"), ("thirty metres", "30 metres"), ("thirty six thousand", "36,000"),
    ("four hours", "4 hours"), ("five days", "5 days"),
]
