"""Part 5: Chapter 4, Lightning & Ice. A night globe flickering with lightning (44 per second, a ticker); Nimbus turns
into a storm cloud; then a hard cut to Antarctica: the biggest desert on Earth, with a precipitation comparison.

  python3 render.py part5 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part5"
VO, _end = schedule(PART, first=3.4, gap=1.35)
DURATION = _end + 2.4
TM = Timing(PART, VO)

STRIKE_T = TM.word("L1", "lightning is striking") - 0.3
SEC_T = TM.word("L1", "forty four") - 0.3
BILLION_T = TM.word("L1", "billion times") - 0.3
ICE_T = VO["L2"] - 0.5
ANT_T = TM.word("L2", "antarctica") - 0.3
DEF_T = VO["L3"] - 0.3
BARS_T = TM.word("L3", "less precipitation") - 0.6

NIM_TRACK = Track([(0.0, "neutral", 0.0), (STRIKE_T, "angry", 0.3), (SEC_T, "shout", 0.25), (BILLION_T + 0.5, "laugh", 0.35), (ICE_T + 0.4, "shocked", 0.2),
                   (ANT_T + 0.8, "worried", 0.4), (DEF_T + 1.0, "focused", 0.4), (BARS_T + 1.0, "smug", 0.4)])
PENGUIN_TRACK = Track([(0.0, "neutral", 0.0), (ANT_T, "happy", 0.3), (DEF_T + 0.6, "focused", 0.4), (BARS_T + 0.8, "laugh", 0.35)])
_rng = np.random.default_rng(14)
FLASH = [(float(_rng.uniform(-1, 1)), float(_rng.uniform(-1, 1)), float(_rng.uniform(0, 1))) for _ in range(60)]


def scene_storm(c, t):
    sky(c, t, mood="space")
    gx, gy, gr = 760, 560, 330
    globe(c, gx, gy, gr, t, rot=t * 0.15, tilt=0.3, night=0.85)
    on = smooth(prog(t, STRIKE_T - 0.3, STRIKE_T + 0.3))
    rate = lerp(2, 44, smooth(prog(t, SEC_T - 0.5, SEC_T + 0.5)))
    for i, (u, v, ph) in enumerate(FLASH[: int(10 + 50 * smooth(prog(t, SEC_T - 0.5, SEC_T + 0.5)))]):
        if u * u + v * v > 0.85:
            continue
        k = ((t * rate / 30 + ph) % 1.0)
        if k < 0.15:
            fl = 1 - k / 0.15
            x, y = gx + u * gr * 0.95, gy + v * gr * 0.95
            light(c, x, y, 70 + 50 * fl, (190, 200, 255), 255 * fl * on)
            lightning(c, x - 6, y - 40, x + 4, y, i, fl * on, 3)
    if t > SEC_T - 0.3:      # strike counter
        n = int(44 * max(0.0, t - SEC_T))
        a = smooth(prog(t, SEC_T - 0.3, SEC_T + 0.2)) * (1 - smooth(prog(t, ICE_T - 0.4, ICE_T)))
        text(c, f"{n:,}", 1460, 470, 96, (220, 225, 255), 255 * a, 800)
        text(c, "STRIKES SINCE THIS NUMBER APPEARED", 1460, 520, 18, WHITE, 220 * a, 800, spacing=3)
    big_number(c, "44 PER SECOND", 1460, 260, 76, (220, 225, 255), t, SEC_T, ICE_T)
    chip(c, "MORE THAN 1 BILLION A YEAR", 1460, 640, GOLD, t, BILLION_T, ICE_T)

    def path(tt):
        return 1460 + 20 * math.sin(tt * 0.8), 820 + 12 * math.sin(tt * 1.3)
    zap = smooth(prog(t, STRIKE_T, STRIKE_T + 0.3)) * (0.6 + 0.4 * (math.sin(t * 9) > 0))
    nim(c, t, NIM_TRACK, path, 110, look=(-0.8, -0.3), zap=zap, tint=((60, 70, 110), 120 * on), rim=(170, 180, 255))
    if STRIKE_T < t < STRIKE_T + 0.3:
        c.drawPaint(fill((220, 230, 255), 160 * (1 - prog(t, STRIKE_T, STRIKE_T + 0.3))))


def scene_ice(c, t):
    pan = t * 30
    sky(c, t, mood="day")
    ice_field(c, t, 820, pan)
    pa = PENGUIN_TRACK.at(t)
    for i, (x, s) in enumerate([(380, 190), (580, 150), (760, 170)]):
        penguin(c, x, 920, s, t + i * 0.3, pa, (0.6, -0.3), blink_amount(t, (), 3.6, i), flap=float(BARS_T + 0.8 < t < BARS_T + 2.2))
    big_number(c, "ANTARCTICA", 960, 200, 110, (190, 225, 255), t, ANT_T, DEF_T + 0.4, sub="THE LARGEST DESERT ON EARTH")
    # precipitation bars: Antarctica interior vs Sahara
    ba = smooth(prog(t, BARS_T - 0.4, BARS_T + 0.2))
    if ba > 0:
        x0, y0 = 1060, 640
        c.drawRRect(rrect(x0 - 60, 220, 800, 480, 30), fill((20, 40, 80), 200 * ba))
        text(c, "YEARLY RAIN OR SNOW", x0 + 340, 280, 24, WHITE, 255 * ba, 800, spacing=4)
        for k, (name, val, rgb) in enumerate([("CENTRAL SAHARA", 0.8, DESERT), ("ANTARCTIC PLATEAU", 0.5, (190, 225, 255))]):
            h = 300 * val * smooth(prog(t, BARS_T + 0.2 * k, BARS_T + 1.0 + 0.2 * k))
            bx = x0 + 120 + k * 360
            c.drawRRect(rrect(bx - 70, y0 - h, 140, h, 14), fill(rgb))
            text(c, name, bx, y0 + 40, 20, WHITE, 255 * ba, 800, spacing=3)
        text(c, "(LESS THAN ~50 MM IN PLACES)", x0 + 340, y0 + 80, 16, WHITE, 180 * ba, 800, spacing=2)
    chip(c, "A DESERT = VERY LITTLE PRECIPITATION, NOT HEAT", 960, 110, (190, 225, 255), t, DEF_T, BARS_T)

    def path(tt):
        return 640 + 20 * math.sin(tt * 0.7), 440 + 12 * math.sin(tt * 1.3)
    nim(c, t, NIM_TRACK, path, 100, look=(-0.4, 0.7), rim=(200, 230, 255), tint=((190, 220, 255), 60))


def draw_frame(c, t):
    if t < ICE_T:
        scene_storm(c, t)
    else:
        scene_ice(c, t)
        if t < ICE_T + 0.25:      # whiteout cut
            c.drawPaint(fill(WHITE, 255 * (1 - prog(t, ICE_T, ICE_T + 0.25))))
    chapter_title(c, t, 4, "LIGHTNING & ICE", (220, 225, 255), 0.2, 2.8)
    fade(c, t, DURATION, 0.5, 0.7)


def sfx_events():
    ev = [(0.2, "swell_soft", 0.6), (STRIKE_T, "boom", 0.9), (STRIKE_T + 0.02, "flicker", 0.8), (SEC_T, "riser", 0.5)]
    ev += [(SEC_T + 0.15 * i, "tink", 0.25) for i in range(20)] + [(BILLION_T, "boom", 0.6), (BILLION_T + 0.05, "shine", 0.6)]
    ev += [(ICE_T, "whoosh_long", 0.8), (ICE_T + 0.05, "shimmer", 0.9), (ANT_T, "ding", 0.7), (DEF_T + 0.5, "slide", 0.5), (BARS_T, "pop", 0.6),
           (BARS_T + 0.2, "pop", 0.6), (BARS_T + 1.0, "chime", 0.6)]
    return ev


MUSIC = dict(
    chords=[(0.0, 43, (0, 7, 12, 15, 19)), (STRIKE_T, 41, (0, 7, 12, 15, 18)), (SEC_T, 43, (0, 7, 12, 15, 19)), (ICE_T, 50, (0, 7, 12, 14, 19)),
            (DEF_T, 48, (0, 7, 12, 16, 19)), (BARS_T, 50, (0, 7, 12, 16, 21))],
    plucks=[(STRIKE_T, ICE_T), (ICE_T + 0.5, DURATION)], bpm=104, rises=[(SEC_T, BILLION_T)], drone=36,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
