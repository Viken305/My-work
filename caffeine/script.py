"""Narration for "What One Coffee Does to Your Body (The Next 6 Hours)", the retro VHS Short.
Each part is one "programme" on the tape; the VCR counter fast-forwards between them. Facts and sources: SCRIPT.md.
"""

PARTS = {
    "part1": [   # 0:00:00 the sip (title card)
        ("H1", "You take one sip of coffee."),
        ("H2", "Here's what happens inside your body, for the next six hours."),
    ],
    "part2": [   # 0:10:00 absorption (medical tape)
        ("A1", "Within about ten minutes, caffeine starts slipping from your gut into your blood."),
        ("A2", "By forty five minutes, almost all of it is in."),
    ],
    "part3": [   # 0:45:00 the trick (game show)
        ("B1", "All day, your brain builds up a chemical called adenosine. The more you have, the sleepier you feel."),
        ("B2", "Caffeine is shaped a lot like it. So it parks in adenosine's spots, and blocks the sleepy signal."),
    ],
    "part4": [   # 1:00:00 the peak (weather report)
        ("C1", "With the brakes off, adrenaline rises, your blood pressure ticks up, and dopamine lifts your mood."),
        ("C2", "You feel sharp and focused."),
        ("C3", "And for nearly one in three people, it wakes up the gut too."),
    ],
    "part5": [   # 5:00:00 half-life (market report)
        ("D1", "But your liver breaks caffeine down slowly. After about five hours, half of it is still in your blood."),
        ("D2", "A big dose, even six hours before bed, can cut your sleep by about an hour."),
    ],
    "part6": [   # 6:00:00 the crash, and the end
        ("E1", "Meanwhile, adenosine kept piling up behind the block."),
        ("E2", "When the caffeine wears off, it all rushes in at once. That's the crash."),
        ("E3", "So drink it early, and for most adults, keep it under about four cups a day."),
        ("E4", "Be kind. Rewind."),
    ],
}
