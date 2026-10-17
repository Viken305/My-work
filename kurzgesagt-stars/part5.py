"""Part 5: Chapter 4, A Quiet End. Red giant, planetary nebula, white dwarf.

  python3 render.py part5 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part5"
VO, _end = schedule(PART, first=2.8, gap=0.8)
DURATION = _end + 1.6
TM = Timing(PART, VO)

SWELL = (TM.word("D1", "swell") - 0.4, TM.word("D1", "maybe earth") + 0.6)
EAT = [TM.word("D1", "mercury") - 0.1, TM.word("D1", "venus") - 0.1]
NEB = (VO["D2"] - 0.5, VO["D2"])
SHED = (TM.word("D2", "shed") - 0.3, VO["D3"])
WD = (VO["D3"] - 0.5, VO["D3"])
PLANETS = [(560, 12, "MERCURY", (160, 150, 150)), (700, 18, "VENUS", (230, 190, 120)), (900, 20, "EARTH?", (80, 150, 255))]


def giant(c, t):
    cam = drift_cam(t, 0, NEB[1], 0, 0, 0, 0, 1.0, 0.92)
    space(c, t, cam, clouds=(), teal=False, a=0.8)
    k = in_out(prog(t, *SWELL))
    sx = lerp(330, -80, k)
    r = lerp(110, 820, k)
    rgb = mix(SOLAR, RED_GIANT, smooth(prog(t, SWELL[0], SWELL[0] + 2.5)))
    star(c, sx, 540, r, t, rgb, lerp(0.8, 0.6, k), granule_a=lerp(34, 55, k))
    for i, (x, pr, name, prgb) in enumerate(PLANETS):
        eaten = i < 2 and t > EAT[i] and sx + r > x - pr
        if eaten:
            fl = math.exp(-(t - EAT[i]) * 3)
            light(c, x, 540, 60, RED_GIANT, 200 * fl)
            continue
        light(c, x, 540, pr * 3, prgb, 120)
        c.drawCircle(x, 540, pr, fill(prgb))
        text(c, name, x, 600, 20, WHITE, 220, 800, spacing=3)
        if i == 2:
            heat = smooth(prog(sx + r, x - 200, x - pr))
            light(c, x, 540, 50, RED_GIANT, 150 * heat)

    def path(tt):
        kk = in_out(prog(tt, *SWELL))
        return lerp(1450, 1620, kk) + 20 * math.sin(tt), 520 + 15 * math.sin(tt * 1.2)
    worried = t > SWELL[0] + 1.5
    orbi_on(c, t, path, 100, "worried" if worried else "neutral", (-0.9, 0), -0.8 if worried else 0.2, rim=mix(SOLAR, RED_GIANT, k))
    label(c, "RED GIANT · IN ~5 BILLION YEARS", 1400, 960, RED_GIANT, 30, 255 * smooth(prog(t, SWELL[0] + 1.0, SWELL[0] + 1.6)))


def nebula(c, t):
    cam = drift_cam(t, NEB[0], WD[1], 0, 0, 0, 0, 1.25, 1.0)
    space(c, t, cam, clouds=(), teal=False)
    k = out_cubic(prog(t, SHED[0], SHED[1] + 2.0))
    cam.push(c, 0.95)
    # the swollen star loosening into the nebula
    rk = 1 - smooth(prog(t, SHED[0], SHED[0] + 2.5))
    if rk > 0.01:
        star(c, 0, 0, 280 * rk + 30, t, RED_GIANT, 0.5, a=255 * rk)
    draw_texture(c, tex_ring(), 0, 0, lerp(0.35, 1.0, k), t * 2.5, 255 * smooth(prog(t, SHED[0], SHED[0] + 1.5)), skia.BlendMode.kPlus)
    draw_texture(c, tex_ring(44), 0, 0, lerp(0.25, 0.8, k), -t * 3.5, 140 * smooth(prog(t, SHED[0] + 0.5, SHED[0] + 2.0)), skia.BlendMode.kPlus)
    white_dwarf(c, 0, 0, 10, t, 255 * smooth(prog(t, SHED[0] + 1.0, SHED[0] + 2.0)))
    cam.pop(c)

    def path(tt):
        return 1600 + 30 * math.sin(tt * 0.7), 760 + 20 * math.sin(tt)
    orbi_on(c, t, path, 90, "wide", (-0.8, -0.4), 0.7, rim=TEAL)
    label(c, "PLANETARY NEBULA", 960, 1010, (150, 230, 240), 30, 255 * smooth(prog(t, TM.word("D2", "planetary") - 0.3, TM.word("D2", "planetary") + 0.3)))


def dwarf(c, t):
    space(c, t, Cam(0, 0, 1.0), clouds=(), teal=False, a=0.8)
    cool = smooth(prog(t, WD[1] + 1.5, DURATION))
    g = out_back(prog(t, WD[1], WD[1] + 0.7), 1.2)
    c.saveLayerAlpha(None, int(255 * (1 - 0.25 * cool)))
    white_dwarf(c, 760, 520, 120 * g, t)
    c.restore()
    e = out_back(prog(t, WD[1] + 0.5, WD[1] + 1.2), 1.2)
    earth(c, 1260, 520, 120 * e, t)
    text(c, "≈", 1010, 545, 90, WHITE, 230 * min(1, e), 800)
    label(c, "WHITE DWARF", 760, 760, BLUE_STAR, 30, 255 * min(1, g), sub="ABOUT THE SIZE OF EARTH")
    label(c, "EARTH", 1260, 760, (120, 180, 255), 30, 255 * min(1, e))
    label(c, "COOLING FOR BILLIONS OF YEARS", 960, 980, WHITE, 24, 255 * smooth(prog(t, TM.word("D3", "cooling") - 0.2, TM.word("D3", "cooling") + 0.3)))


def draw_frame(c, t):
    scenes(c, t, [((0.0, 0.01), NEB[1], giant), (NEB, WD[1], nebula), (WD, DURATION + 1, dwarf)])
    chapter_title(c, t, 4, "A QUIET END", RED_GIANT, 0.2, 2.5)
    fade(c, t, DURATION, 0.5, 0.7)


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (SWELL[0], "rumble", 0.9), (SWELL[0] + 2.0, "rumble", 0.8), (EAT[0], "sizzle", 0.6), (EAT[1], "sizzle", 0.7),
            (SWELL[1] - 1.0, "riser", 0.4), (NEB[0], "whoosh_long", 0.6), (SHED[0], "swell_soft", 0.8), (SHED[0] + 1.5, "shimmer", 0.7),
            (WD[0], "whoosh", 0.5), (WD[1], "pop", 0.6), (WD[1] + 0.5, "pop", 0.5), (WD[1] + 1.0, "chime", 0.5)]


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 15, 19)), (SWELL[0], 41, (0, 7, 12, 15, 18)), (NEB[0], 46, (0, 7, 12, 14, 19)), (WD[0], 43, (0, 7, 12, 14, 19))],
    plucks=[(NEB[1], DURATION)], bpm=84, rises=[(SWELL[0], SWELL[1])], drone=33,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
