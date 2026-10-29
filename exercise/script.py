"""Narration for "What Happens Inside Your Body During Exercise".
city / beat / micro: the three style tests (one line each). part1..part7: the full Beat Drop video, one level per part.
Facts and sources: SCRIPT.md.
"""

PARTS = {
    "city": [("A", "During a sprint, your heart pumps up to five times more blood every minute.")],
    "beat": [("B", "Push hard, and your heart can hit around one hundred and eighty beats per minute.")],
    "micro": [("C", "And to keep you from overheating, your skin can sweat more than a litre an hour.")],

    # ---------------------------------------------------------------- the full video
    "part1": [   # hook: press play
        ("H1", "The moment you start exercising, your body turns into a rhythm game."),
        ("H2", "Every organ has to hit its notes, right on time."),
        ("H3", "Here is what happens inside, level by level."),
    ],
    "part2": [   # level 1: ignition
        ("A1", "Within seconds, your brain fires a signal, and adrenaline floods your blood."),
        ("A2", "Your heart speeds up, and the blood vessels in your muscles open wide."),
        ("A3", "At rest, your muscles get about twenty percent of your blood. Go hard, and that jumps to eighty percent."),
    ],
    "part3": [   # level 2: air
        ("B1", "Your breathing goes from about twelve breaths a minute, to forty or more."),
        ("B2", "Air flow jumps from six litres a minute, to around one hundred."),
        ("B3", "Your blood grabs that oxygen, and races it straight to your muscles."),
    ],
    "part4": [   # level 3: fuel
        ("C1", "Muscles run on a tiny molecule called A T P, but they only store enough for a few seconds."),
        ("C2", "So your body burns sugar and fat to recharge it, nonstop."),
        ("C3", "When oxygen can't keep up, acid builds up in your muscles. That's part of the burn."),
    ],
    "part5": [   # level 4: max heart
        ("D1", "Push hard, and your heart can hit around one hundred and eighty beats per minute."),
        ("D2", "Pumping up to twenty litres of blood every minute. That's four times more than at rest."),
    ],
    "part6": [   # level 5: heat
        ("E1", "But muscles are messy engines. About seventy five percent of their energy becomes heat."),
        ("E2", "So your core temperature climbs, and your skin can sweat more than a litre an hour."),
    ],
    "part7": [   # bonus round and the end
        ("F1", "Then comes the bonus round. Your brain releases endorphins and endocannabinoids, the chemicals behind the runner's high."),
        ("F2", "And after you stop, your body keeps burning extra calories while it recovers."),
        ("F3", "Train often, and your heart gets stronger, so it needs fewer beats at rest."),
        ("F4", "Level complete. Hit play again tomorrow."),
    ],
}
