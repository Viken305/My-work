"""Part 2: Chapter 1, More Trees Than Stars. Nimbus stargazes under the Milky Way; tilt down to a forest that fills the
world; a dot-for-dot comparison shows trees beating stars many times over.

  python3 render.py part2 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part2"
VO, _end = schedule(PART, first=3.4, gap=1.35)
DURATION = _end + 2.4
TM = Timing(PART, VO)

STARS_T = TM.word("T1", "between one hundred") - 0.3
DOWN_T = VO["T2"] - 0.6
TREES_T = TM.word("T2", "three trillion") - 0.2
COMP_T = VO["T3"] - 0.5
MANY_T = TM.word("T3", "many times") - 0.2

NIM_TRACK = Track([(0.0, "neutral", 0.0), (1.0, "focused", 0.4), (STARS_T, "shocked", 0.2), (STARS_T + 1.2, "happy", 0.4), (DOWN_T + 0.4, "neutral", 0.3),
                   (TREES_T, "shocked", 0.2), (TREES_T + 1.0, "laugh", 0.35), (COMP_T + 0.5, "focused", 0.4), (MANY_T, "cheer", 0.3)])


def scene_night(c, t):
    tilt = in_out(prog(t, DOWN_T, DOWN_T + 2.2))          # camera tilts from the sky down to the forest
    dawn = smooth(prog(t, DOWN_T + 0.8, TREES_T + 1.0))
    c.save()
    c.translate(0, tilt * 900)
    sky(c, t, Cam(0, -tilt * 400, 1.0), mood="night")
    milky_way(c, t, 255 * (1 - 0.6 * dawn))
    c.restore()
    if dawn > 0:      # morning light floods in as we look down
        c.saveLayerAlpha(None, int(255 * dawn))
        sky(c, t, mood="day")
        c.restore()
    # horizon of forests rising into view
    base = lerp(1300, 560, tilt)
    hills(c, base, mix((20, 30, 50), (90, 140, 120), dawn), t, 40, 0.003, 0.2)
    for k, (dy, n, s, sh) in enumerate([(0, 60, 90, 0.35), (140, 46, 150, 0.18), (330, 34, 230, 0.0)]):
        col = mix(mix((14, 24, 30), (56, 130, 84), dawn), (0, 0, 0), sh)
        forest_band(c, t, base + dy, n, s, 11 + k, col, 255, x_off=t * (8 + 10 * k), kinds=(1, 0, 1))
    # Nimbus lying back in the sky, then looking down
    def path(tt):
        return 1380 + 20 * math.sin(tt * 0.6), lerp(820, 260, in_out(prog(tt, DOWN_T, DOWN_T + 2.2))) + 12 * math.sin(tt * 1.1)
    look = (lambda tt: (0.3, -0.9) if tt < DOWN_T else (-0.4, 0.8))
    nim(c, t, NIM_TRACK, path, 120, look=look, rim=(180, 190, 255) if t < DOWN_T else (255, 220, 180), sparkle_=float(TREES_T + 1.0 < t < TREES_T + 2.5))
    big_number(c, "100–400 BILLION", 960, 200, 92, (220, 225, 255), t, STARS_T, DOWN_T + 0.4, sub="STARS IN THE MILKY WAY")
    big_number(c, "≈ 3 TRILLION", 960, 200, 110, (170, 240, 150), t, TREES_T, COMP_T, sub="TREES ON EARTH")


def scene_compare(c, t):
    """Dot grid: each dot = 10 billion. Stars light up first (up to 40 dots), then trees flood in (300 dots)."""
    sky(c, t, mood="day")
    c.drawPaint(fill((10, 30, 50), 160))
    gx, gy, cols, sp = 300, 310, 25, 46
    nstar, ntree = 40, 300
    ks = smooth(prog(t, COMP_T + 0.3, COMP_T + 1.3))
    kt = in_out(prog(t, COMP_T + 1.2, MANY_T + 0.8))
    for i in range(ntree):
        x, y = gx + (i % cols) * sp, gy + (i // cols) * sp
        if i < nstar * ks:
            sparkle(c, x, y, 16, 255, (230, 230, 255))
        elif i < ntree * kt:
            tree(c, x, y + 14, 36, i % 2, t, 255)
        else:
            c.drawCircle(x, y, 3, fill(WHITE, 40))
    text(c, "STARS IN OUR GALAXY: UP TO 400 BILLION", 300, 240, 26, (220, 225, 255), 255 * ks, 800, "left", spacing=3)
    text(c, "TREES ON EARTH: ~3 TRILLION", 300, 920, 34, (170, 240, 150), 255 * smooth(prog(t, COMP_T + 1.2, COMP_T + 1.8)), 800, "left", spacing=4)
    text(c, "EACH SYMBOL ≈ 10 BILLION", 1430, 920, 18, WHITE, 180 * ks, 800, "right", spacing=3)

    def path(tt):
        return 1640 + 15 * math.sin(tt), 560 + 12 * math.sin(tt * 1.4)
    nim(c, t, NIM_TRACK, path, 100, look=(-0.8, 0.4), sparkle_=float(t > MANY_T))
    chip(c, "MORE TREES THAN STARS", 960, 960, (170, 240, 150), t, MANY_T, DURATION)


def draw_frame(c, t):
    xfade(c, t, COMP_T - 0.4, 0.9, scene_night, scene_compare, 0.25)
    chapter_title(c, t, 1, "MORE TREES THAN STARS", (170, 240, 150), 0.2, 2.8)
    fade(c, t, DURATION, 0.5, 0.7)


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (1.2, "shimmer", 0.5), (STARS_T, "shine", 0.8), (STARS_T + 0.05, "boom", 0.4), (DOWN_T, "whoosh_long", 0.7),
            (DOWN_T + 1.0, "swell_soft", 0.6), (TREES_T, "boom", 0.6), (TREES_T + 0.05, "chime", 0.8), (COMP_T, "whoosh", 0.5)] + \
           [(COMP_T + 0.3 + 0.05 * i, "tink", 0.25) for i in range(0, 20, 2)] + [(COMP_T + 1.2 + 0.12 * i, "pop", 0.3) for i in range(20)] + \
           [(MANY_T, "ding", 0.7)]


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 14, 19)), (STARS_T, 47, (0, 7, 12, 16, 19)), (DOWN_T, 50, (0, 7, 12, 16, 19)), (TREES_T, 52, (0, 7, 12, 16, 19, 24)),
            (COMP_T, 50, (0, 7, 12, 16, 21))],
    plucks=[(VO["T1"], DURATION)], bpm=96, rises=[(DOWN_T, TREES_T), (COMP_T + 1.0, MANY_T)], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
