"""Part 4: Chapter 3, Life. Gravity vs fusion, the Sun's lifetime, small vs giant stars.

  python3 render.py part4 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part4"
VO, _end = schedule(PART, first=2.8, gap=0.75)
DURATION = _end + 1.4
TM = Timing(PART, VO)

GRAV_T = TM.word("L1", "gravity") - 0.2
FUS_T = TM.word("L1", "fusion") - 0.2
SUN = (VO["L2"] - 0.6, VO["L2"])
HALF_T = TM.word("L2", "halfway") - 0.4
SIZE = (VO["L3"] - 0.6, VO["L3"])
STAR_T = [TM.word("L3", "red dwarf") - 0.3, TM.word("L3", "trillions") - 0.4, TM.word("L3", "giant stars") - 0.3]


def tug(c, t):
    cam = drift_cam(t, 0, SUN[1], 0, 0, 0, 0, 1.15, 1.0)
    space(c, t, cam, clouds=("cloud",), a=0.45)
    g_in = smooth(prog(t, GRAV_T, GRAV_T + 0.6))
    g_out = smooth(prog(t, FUS_T, FUS_T + 0.6))
    osc = math.sin((t - FUS_T) * 3.2) * math.exp(-max(0.0, t - FUS_T) * 0.45) * (t > FUS_T)
    squeeze = 0.08 * g_in * (1 - g_out) + 0.05 * osc
    r = 230 * (1 - squeeze)
    star(c, 960, 540, r, t, SOLAR, 0.9)
    for k in range(12):
        ang = k / 12 * 6.28 + 0.13
        if g_in > 0:
            d = 470 - 60 * math.sin(t * 3 + k) * 0.3 - 40 * (1 - g_in)
            arrow(c, 960 + math.cos(ang) * d, 540 + math.sin(ang) * d, 960 + math.cos(ang) * (r + 50), 540 + math.sin(ang) * (r + 50), VIOLET2, 9, 230 * g_in, 26)
        if g_out > 0:
            a2 = ang + 0.26
            d2 = r + 20 + 160 * g_out + 15 * math.sin(t * 3 + k)
            arrow(c, 960 + math.cos(a2) * (r - 10), 540 + math.sin(a2) * (r - 10), 960 + math.cos(a2) * d2, 540 + math.sin(a2) * d2, AMBER, 9, 230 * g_out, 26)
    if g_in > 0:
        tag(c, "GRAVITY  →  IN", 300, 160, VIOLET2, 28)
    if g_out > 0:
        tag(c, "FUSION  →  OUT", 1620, 160, AMBER, 28)
    bal = smooth(prog(t, VO["L2"], VO["L2"] + 0.6))
    if bal > 0:
        c.saveLayerAlpha(None, int(255 * bal))
        tag(c, "BALANCED", 960, 960, WHITE, 30)
        c.restore()


def sun_life(c, t):
    space(c, t, Cam(0, 0, 1.0), clouds=("cloud",), a=0.4)
    star(c, 960, 360, 160, t, SOLAR, 0.8)
    x0, x1, y = 260, 1660, 800
    c.drawRRect(rrect(x0, y - 10, x1 - x0, 20, 10), fill((40, 40, 80)))
    fill_k = 0.46 * in_out(prog(t, SUN[1] + 0.8, HALF_T + 0.4))
    c.drawRRect(rrect(x0, y - 10, (x1 - x0) * fill_k, 20, 10), shaded(linear((x0, 0), (x1, 0), [AMBER, SOLAR])))
    for v, lab in ((0, "BIRTH"), (5, "5"), (10, "~10 BILLION YEARS")):
        x = x0 + (x1 - x0) * v / 10
        c.drawLine(x, y + 20, x, y + 40, stroke(WHITE, 3, 180))
        text(c, lab, x, y + 76, 22, WHITE, 200, 800, spacing=3)
    xm = x0 + (x1 - x0) * fill_k
    c.drawCircle(xm, y, 18, fill(WHITE))
    light(c, xm, y, 60, SOLAR, 160)
    yrs = 4.6 * fill_k / 0.46
    text(c, f"{yrs:.1f} BILLION YEARS", xm, y - 50, 26, SOLAR, 255 * smooth(prog(t, SUN[1] + 0.8, SUN[1] + 1.2)), 800, spacing=3)
    ha = smooth(prog(t, HALF_T, HALF_T + 0.4))
    if ha > 0:
        c.saveLayerAlpha(None, int(255 * ha))
        tag(c, "TODAY · ROUGHLY HALFWAY", xm, y - 120, SOLAR, 24)
        c.restore()

    def path(tt):
        return 1480 + 40 * math.sin(tt * 0.6), 320 + 25 * math.sin(tt * 0.9)
    orbi_on(c, t, path, 80, "happy" if t > HALF_T else "neutral", (-0.8, 0), 0.4, rim=SOLAR)


SIZES = [(330, 40, RED_GIANT, 0.45, "RED DWARF", "TRILLIONS OF YEARS", 1.0),
         (830, 95, SOLAR, 0.4, "SUN-LIKE", "~10 BILLION YEARS", 0.42),
         (1480, 230, BLUE_STAR, 0.3, "GIANT", "A FEW MILLION YEARS", 0.06)]


def sizes(c, t):
    space(c, t, Cam(0, 0, 1.0), clouds=("teal",), a=0.5)
    for i, (x, r, rgb, cor, name, life, bar) in enumerate(SIZES):
        g = out_back(prog(t, STAR_T[i], STAR_T[i] + 0.7), 1.2)
        if g <= 0:
            continue
        flick = 1 + (0.04 * math.sin(t * 13) if i == 2 else 0)
        star(c, x, 500, r * g * flick, t, rgb, cor)
        label(c, name, x, 830, WHITE, 28, 255 * min(1, g), sub=life)
        # lifetime bar (relative)
        bk = in_out(prog(t, STAR_T[i] + 0.4, STAR_T[i] + 1.8))
        bw = 380 * bar * bk
        c.drawRRect(rrect(x - 190, 900, 380, 12, 6), fill((40, 40, 80), 200 * min(1, g)))
        c.drawRRect(rrect(x - 190, 900, max(6, bw), 12, 6), fill(rgb, 230))
        if i == 0 and bk > 0.95:
            arrow(c, x + 190, 906, x + 240, 906, rgb, 4, 230, 14)

    def path(tt):
        k = smooth(prog(tt, STAR_T[2], STAR_T[2] + 1.2))
        return lerp(1080, 1150, k) + 20 * math.sin(tt), lerp(300, 260, k) + 10 * math.sin(tt * 1.4)
    orbi_on(c, t, path, 70, "worried" if t > STAR_T[2] else "neutral", (0.8, 0.2) if t > STAR_T[2] else (-0.8, 0.2), -0.6 if t > STAR_T[2] else 0.3, rim=BLUE_STAR)


def draw_frame(c, t):
    scenes(c, t, [((0.0, 0.01), SUN[1], tug), (SUN, SIZE[1], sun_life), (SIZE, DURATION + 1, sizes)])
    chapter_title(c, t, 3, "LIFE", SOLAR, 0.2, 2.5)
    fade(c, t, DURATION, 0.5, 0.6)


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (GRAV_T, "whoosh", 0.6), (GRAV_T + 0.2, "rumble", 0.5), (FUS_T, "whoosh", 0.6), (FUS_T + 0.2, "shimmer", 0.5),
            (VO["L2"], "chime", 0.5), (SUN[0], "whoosh", 0.5), (SUN[1] + 0.8, "riser", 0.4), (HALF_T, "pop", 0.6),
            (SIZE[0], "whoosh", 0.5)] + [(x, "pop", 0.6) for x in STAR_T] + [(STAR_T[2] + 0.3, "sizzle", 0.4)]


MUSIC = dict(
    chords=[(0.0, 48, (0, 7, 12, 16, 19)), (SUN[0], 53, (0, 7, 12, 16, 19)), (SIZE[0], 50, (0, 7, 12, 14, 19)), (STAR_T[2], 46, (0, 7, 12, 15, 19))],
    plucks=[(VO["L1"], DURATION)], bpm=96, rises=[(SUN[1] + 0.8, HALF_T)], drone=33,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
