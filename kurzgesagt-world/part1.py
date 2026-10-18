"""Part 1: Hook. A familiar landscape (ocean, forest, ground) -> pull up into space -> meet Nimbus -> dive back down.

  python3 render.py part1 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part1"
VO, _end = schedule(PART, first=0.8, gap=1.0)
DURATION = _end + 1.6
TM = Timing(PART, VO)

OCEAN_T = TM.word("H1", "blue oceans") - 0.2
FOREST_T = TM.word("H1", "green forests") - 0.2
GROUND_T = TM.word("H1", "solid ground") - 0.2
UP_T = VO["H2"] - 0.2
STRANGE_T = TM.word("H2", "stranger") - 0.2
GUIDE_T = TM.word("H2", "from above") - 0.8
NIMBUS_T = TM.word("H3", "this is nimbus") - 0.2
GO_T = TM.word("H3", "let's go") - 0.2

NIM_TRACK = Track([(0.0, "neutral", 0.0), (GUIDE_T, "smug", 0.3), (NIMBUS_T, "happy", 0.35), (NIMBUS_T + 1.0, "wink", 0.25),
                   (NIMBUS_T + 2.0, "happy", 0.3), (GO_T, "cheer", 0.3)])


def landscape(c, t):
    """A slow pan along the 'normal' world: ocean, forest, solid ground."""
    pan = in_out(prog(t, 0.0, UP_T + 0.5)) * 2600
    sky(c, t, mood="day")
    for k, x in enumerate((300, 900, 1500)):
        cloud_puff(c, (x - pan * 0.1 + t * 12) % (W + 400) - 200, 160 + 40 * k, 60 + 10 * k, 170)
    hills(c, 620, (110, 150, 200), t, 50, 0.002, 0.4, 255, pan * 0.3)
    # ocean on the left, forest in the middle, meadow on the right (all in one strip)
    c.save()
    c.translate(-pan, 0)
    c.drawRect(skia.Rect.MakeXYWH(-400, 720, 1500, 400), shaded(linear((0, 720), (0, H), [OCEAN, OCEAN_DEEP])))
    for k in range(12):
        y = 740 + k * 28
        p = skia.Path()
        p.moveTo(-400, y)
        for x in range(-400, 1120, 40):
            p.lineTo(x, y + 6 * math.sin(x * 0.03 + t * 2 + k))
        c.drawPath(p, stroke(SHALLOW, 3, 120))
    beach = skia.Path()
    beach.moveTo(1100, H)
    beach.cubicTo(1080, 820, 1150, 740, 1300, 700)
    beach.lineTo(4400, 700)
    beach.lineTo(4400, H)
    beach.close()
    c.drawPath(beach, fill((236, 214, 160)))
    c.drawRect(skia.Rect.MakeXYWH(1300, 690, 3200, 400), shaded(linear((0, 690), (0, H), [LAND, darken(LAND, 0.3)])))
    rng = np.random.default_rng(4)
    for i in range(70):
        x = 1400 + i * 24 + rng.uniform(-10, 10)
        tree(c, x, 720 + rng.uniform(0, 260) * (i % 3 == 0), 150 * rng.uniform(0.8, 1.2), i % 2, t, 255)
    for i in range(30):      # meadow flowers
        x = 3300 + i * 36
        c.drawCircle(x, 760 + (i * 37) % 200, 7, fill([(255, 220, 90), (255, 140, 160), WHITE][i % 3]))
    c.restore()
    chip(c, "BLUE OCEANS", 960, 110, SHALLOW, t, OCEAN_T, FOREST_T)
    chip(c, "GREEN FORESTS", 960, 110, (150, 230, 140), t, FOREST_T, GROUND_T)
    chip(c, "SOLID GROUND", 960, 110, (240, 220, 160), t, GROUND_T, UP_T + 0.4)


def space_scene(c, t):
    """Pull up into space; the globe spins; Nimbus floats in and introduces itself, then dives towards Earth."""
    k = in_out(prog(t, UP_T, STRANGE_T + 1.5))
    dive = in_cubic(prog(t, GO_T + 0.6, DURATION))
    sky(c, t, Cam(0, 0, 1.0), mood="space")
    gr = lerp(1500, 350, k) * (1 + 2.5 * dive)
    globe(c, 640 + 300 * dive, lerp(1900, 660, k) + 500 * dive, gr, t, rot=t * 0.12, tilt=lerp(0.05, 0.3, k))
    q = smooth(prog(t, STRANGE_T, STRANGE_T + 0.5)) * (1 - smooth(prog(t, NIMBUS_T - 0.5, NIMBUS_T)))
    for i in range(5):        # question marks orbiting the globe
        an = t * 0.6 + i * 1.256
        x, y = 640 + math.cos(an) * 480, 660 + math.sin(an) * 190
        text(c, "?", x, y, 70 + 10 * math.sin(t * 3 + i), GOLD, 255 * q * (0.5 + 0.5 * math.sin(an) + 0.3), 800)

    def path(tt):
        u = out_back(prog(tt, GUIDE_T, GUIDE_T + 1.6), 1.2)
        d = in_cubic(prog(tt, GO_T + 0.5, GO_T + 1.6))
        return lerp(2200, 1360, u) + lerp(0, -600, d) + 20 * math.sin(tt * 0.9), lerp(340, 420, u) + lerp(0, 500, d) + 15 * math.sin(tt * 1.3)
    if t > GUIDE_T - 0.2:
        wave = NIMBUS_T < t < NIMBUS_T + 1.6
        (x, y), _ = path_vel(path, t)
        hands = (None, (x + 150 + 15 * math.sin(t * 12), y - 120)) if wave else (None, None)
        nim(c, t, NIM_TRACK, path, 150, look=(-0.6, 0.2) if t < GO_T else (-0.8, 0.6), hands=hands, sparkle_=float(NIMBUS_T < t < NIMBUS_T + 2.0),
            rim=(150, 200, 255))
    chip(c, "NIMBUS", 1360, 640, (220, 235, 255), t, NIMBUS_T + 0.2, GO_T + 0.4, size=34)
    text(c, "EARTH IS", 960, 100, 46, WHITE, 255 * smooth(prog(t, STRANGE_T, STRANGE_T + 0.5)) * (1 - smooth(prog(t, GUIDE_T, GUIDE_T + 0.5))), 800, spacing=12)
    text(c, "WEIRDER THAN YOU THINK", 960, 190, 80, GOLD, 255 * smooth(prog(t, STRANGE_T + 0.3, STRANGE_T + 0.8)) * (1 - smooth(prog(t, GUIDE_T, GUIDE_T + 0.5))),
         800, spacing=lerp(24, 10, out_cubic(prog(t, STRANGE_T + 0.3, STRANGE_T + 2.0))))
    if dive > 0:
        c.drawPaint(fill((200, 230, 255), 255 * smooth(prog(dive, 0.6, 1.0))))


def draw_frame(c, t):
    xfade(c, t, UP_T - 0.4, 1.0, landscape, space_scene, 0.0)
    fade(c, t, DURATION, 0.7, 0.4, rgb=(200, 230, 255))


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (OCEAN_T, "bubble", 0.5), (FOREST_T, "shimmer", 0.4), (GROUND_T, "pop", 0.5), (UP_T - 0.4, "whoosh_long", 0.8),
            (UP_T + 0.6, "riser", 0.5), (STRANGE_T, "boom", 0.6), (STRANGE_T + 0.05, "shine", 0.7), (GUIDE_T, "slide", 0.6), (NIMBUS_T, "chime", 0.7),
            (NIMBUS_T + 1.0, "ding", 0.6), (GO_T + 0.4, "whoosh_long", 0.9), (DURATION - 0.6, "shimmer", 0.6)]


MUSIC = dict(
    chords=[(0.0, 50, (0, 7, 12, 16, 19)), (UP_T, 48, (0, 7, 12, 14, 19)), (STRANGE_T, 45, (0, 7, 12, 15, 19)), (NIMBUS_T, 50, (0, 7, 12, 16, 21))],
    plucks=[(0.4, UP_T), (NIMBUS_T, DURATION)], bpm=100, rises=[(UP_T, STRANGE_T), (GO_T, DURATION)], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
