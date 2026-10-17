"""Part 5: why we need volcanoes (air + oceans, fertile soil, new land, climate thermostat) + outro.

  python3 render.py part5 [--still 3,12,20]
"""
import math

import numpy as np

from common import *  # noqa: F401,F403

PART = "part5"
VO = {"G1": 0.6, "G2": 4.6, "G3": 10.8, "G4": 15.3, "G5": 20.0, "G6": 28.4, "G7": 34.8}
DURATION = 42.0
TM = Timing(PART, VO)

OWE_T = TM.word("G1", "owe")
EARLY = (4.3, 4.9)
CLOUD = (TM.word("G2", "gases"), TM.word("G2", "air") + 0.5)
OCEAN_T = TM.word("G2", "oceans") - 0.4
SOIL = (10.9, 11.4)
LAND = (15.0, 15.5)
ICE_T, HAW_T = TM.word("G4", "iceland") - 0.2, TM.word("G4", "hawaii") - 0.2
THERMO = (19.7, 20.3)
RELEASE_T = TM.word("G5", "releasing")
SOAK_T = TM.word("G5", "soak")
NIGHT = (28.1, 28.8)
ANGRY_T = TM.word("G6", "angry") - 0.2
ALIVE_T = TM.word("G7", "alive") - 0.2
END_CARD = 37.4

_p1 = Plume(41, 34)
_rng = np.random.default_rng(6)


# ---------------------------------------------------------------- deadly, but...
def draw_deadly(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(16, 12, 40), (80, 40, 90)])))
    Stars(120, 3).draw(c, t, 0.6)
    wavy_band(c, 820, 1080, (40, 26, 60), 5, 20)
    x, y = volcano(c, 960, 830, 820, 480, (86, 70, 110), crater=0.11, hot=1.0, t=t)
    _p1.draw(c, x, y - 10, t, 420, 120, 1.0, 0.22)
    for k, pts in enumerate([[(x - 10, y), (880, 480), (800, 640), (720, 820)], [(x + 10, y), (1040, 470), (1110, 640), (1200, 820)]]):
        lava_flow(c, pts, 0.8 + 0.2 * math.sin(t + k), 18)
    bow = math.sin(math.pi * prog(t, OWE_T, OWE_T + 1.0))
    bird(c, 1560, 1010, 70, t, look=(-1, 0.3 + bow), tilt=-20 * bow)
    caption(c, "BUT WE OWE THEM A LOT", 960, 1030, LAVA_HOT, 30, 255 * smooth(prog(t, OWE_T, OWE_T + 0.4)))


# ---------------------------------------------------------------- early Earth: air + oceans
def molecule(c, x, y, kind, s=1.0, a=255):
    if kind == 0:   # CO2
        for dx, rgb, r in ((-22, OX, 11), (0, (170, 170, 185), 13), (22, OX, 11)):
            c.drawCircle(x + dx * s, y, r * s, fill(rgb, a))
    else:           # H2O
        c.drawCircle(x, y, 13 * s, fill(OX, a))
        c.drawCircle(x - 15 * s, y + 10 * s, 8 * s, fill(WHITE, a))
        c.drawCircle(x + 15 * s, y + 10 * s, 8 * s, fill(WHITE, a))


def draw_early(c, t):
    sky = smooth(prog(t, OCEAN_T - 0.3, OCEAN_T + 1.0))
    c.drawPaint(shaded(linear((0, 0), (0, 700), [mix((60, 30, 40), (60, 120, 200), sky), mix((200, 90, 60), (160, 210, 240), sky)])))
    ground = 760
    c.drawRect(skia.Rect.MakeXYWH(0, ground, W, H), fill((70, 46, 52)))
    vents = [(300, 200, 160), (760, 260, 210), (1240, 220, 170), (1640, 180, 140)]
    for n, (vx, w, h) in enumerate(vents):
        x, y = volcano(c, vx, ground + 6, w * 2, h, (90, 60, 70), crater=0.18, hot=1.0, t=t)
        for k in range(5):  # gas molecules rising
            ph = (t * 0.22 + k / 5 + n * 0.17) % 1
            molecule(c, x + 30 * math.sin(k * 2 + t), y - 30 - 420 * ph, (k + n) % 2, 1.0, 255 * (1 - ph) * (1 - sky))
    cl = smooth(prog(t, *CLOUD))
    for k in range(7):
        cx = (k * 330 + t * 20) % (W + 300) - 150
        for j in range(3):
            c.drawCircle(cx + j * 60, 140 + (k % 2) * 40 - (j % 2) * 20, 60 * cl, fill(mix((120, 110, 130), WHITE, sky), 230))
    rain = smooth(prog(t, OCEAN_T - 1.2, OCEAN_T)) * (1 - sky)
    if rain > 0:
        for k in range(60):
            x = (k * 37 + t * 60) % W
            y = (k * 91 + t * 900) % 600 + 200
            c.drawLine(x, y, x - 6, y + 26, stroke((180, 210, 255), 3, 180 * rain))
    sea = in_out(prog(t, OCEAN_T - 0.4, OCEAN_T + 1.2))
    if sea > 0:
        sy = lerp(H + 10, ground - 40, sea)
        wave = skia.Path()
        wave.moveTo(0, sy)
        for x in range(0, W + 40, 40):
            wave.lineTo(x, sy + 8 * math.sin(x / 80 + t * 2))
        wave.lineTo(W, H)
        wave.lineTo(0, H)
        wave.close()
        c.drawPath(wave, shaded(linear((0, sy), (0, H), [CYAN, OCEAN])))
    caption(c, "BILLIONS OF YEARS AGO", 960, 1030, WHITE, 30, 255 * smooth(prog(t, EARLY[1], EARLY[1] + 0.4)) * (1 - smooth(prog(t, OCEAN_T, OCEAN_T + 0.3))))
    caption(c, "AIR + OCEANS", 960, 1030, CYAN, 32, 255 * smooth(prog(t, OCEAN_T + 0.4, OCEAN_T + 0.8)))


# ---------------------------------------------------------------- fertile soil
def draw_soil(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [(90, 170, 240), (200, 230, 250)])))
    glow(c, 1600, 200, 200, YELLOW, 160)
    c.drawCircle(1600, 200, 80, fill((255, 240, 180)))
    c.drawRect(skia.Rect.MakeXYWH(0, 690, W, H), fill((80, 110, 90)))
    volcano(c, 600, 700, 1300, 520, (100, 120, 110), crater=0.12, t=t)
    hill = skia.Path()
    hill.moveTo(-50, H)
    hill.cubicTo(300, 640, 1400, 600, W + 50, 700)
    hill.lineTo(W + 50, H)
    hill.close()
    c.drawPath(hill, fill((90, 60, 50)))
    c.save()
    c.clipPath(hill, doAntiAlias=True)
    for k in range(9):  # field stripes
        y = 700 + k * 48
        c.drawRect(skia.Rect.MakeXYWH(0, y, W, 24), fill((70, 46, 40)))
    c.restore()
    for n in range(28):  # crops sprouting
        x = 120 + (n % 14) * 125 + (n // 14) * 60
        y = 760 + (n // 14) * 140 + 20 * math.sin(n)
        g = out_back(prog(t, SOIL[1] + 0.3 + n * 0.06, SOIL[1] + 0.9 + n * 0.06))
        if g <= 0:
            continue
        c.drawLine(x, y, x, y - 60 * g, stroke((60, 150, 80), 6))
        c.drawOval(skia.Rect.MakeXYWH(x - 30 * g, y - 60 * g, 30 * g, 16 * g), fill(MINT))
        c.drawOval(skia.Rect.MakeXYWH(x, y - 48 * g, 30 * g, 16 * g), fill((80, 200, 120)))
    caption(c, "FERTILE VOLCANIC SOIL", 960, 1030, MINT, 30, 255 * smooth(prog(t, SOIL[1] + 0.4, SOIL[1] + 0.8)))


# ---------------------------------------------------------------- new land
def draw_land(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, 560), [(30, 30, 80), (110, 90, 160)])))
    sea = 600
    c.drawRect(skia.Rect.MakeXYWH(0, sea, W, H), shaded(linear((0, sea), (0, H), [CYAN, OCEAN])))
    for n, (ix, tt, label) in enumerate([(560, ICE_T, "ICELAND"), (1360, HAW_T, "HAWAII")]):
        g = out_cubic(prog(t, LAND[1] + n * 0.6, LAND[1] + 3.0 + n * 0.6))
        if g <= 0:
            continue
        h = 260 * g
        x, y = volcano(c, ix, sea + 30, 700 * (0.4 + 0.6 * g), h, (110, 140, 100) if n else (130, 130, 150), crater=0.14, hot=1.0, t=t, snow=n == 0)
        for k in range(6):  # steam where lava meets the sea
            ph = (t * 0.5 + k / 6 + n * 0.3) % 1
            c.drawCircle(x + h * 1.0 + (k - 2.5) * 18, sea + 10 - 160 * ph, 16 + 26 * ph, fill(WHITE, 150 * (1 - ph) * g))
        lava_flow(c, [(x + 6, y), (x + h * 0.6, sea - h * 0.4), (x + h * 1.0, sea + 20)], g, 14)
        pill_tag(c, ix, y - 80, label, LAVA_HOT if n else ICE, pop(t, tt, 0.4), 28)
    c.drawRect(skia.Rect.MakeXYWH(0, sea + 20, W, 6), fill(WHITE, 80))
    caption(c, "NEW LAND", 960, 1030, WHITE, 32, 255 * smooth(prog(t, LAND[1] + 0.3, LAND[1] + 0.7)))


# ---------------------------------------------------------------- thermostat
def draw_thermo(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [NAVY, (40, 50, 100)])))
    ground = 800
    c.drawRect(skia.Rect.MakeXYWH(0, ground, W, H), fill((60, 50, 80)))
    x, y = volcano(c, 380, ground + 4, 520, 300, (90, 74, 112), crater=0.14, hot=1.0, t=t)
    # carbon released into the air ...
    r = smooth(prog(t, RELEASE_T - 0.5, RELEASE_T))
    for k in range(9):
        ph = (t * 0.12 + k / 9) % 1
        mx = lerp(x, 1500, ph)
        my = y - 80 - 280 * math.sin(math.pi * ph) * 0.9
        molecule(c, mx, my, 0, 1.2, 255 * r * (1 - smooth(prog(ph, 0.85, 1))))
    # ... and slowly soaked up again by rock
    rock = blob_path(1560, ground + 20, [200, 160, 180, 150, 190, 170, 160, 200], 0.2)
    m = skia.Matrix()
    m.setScale(1.0, 0.6, 1560, ground + 20)
    rock.transform(m)
    c.drawPath(rock, fill((110, 100, 130)))
    s = smooth(prog(t, SOAK_T - 0.5, SOAK_T))
    for k in range(30):
        xx = 1360 + (k * 53) % 400
        yy = (k * 97 + t * 500) % 380 + 300
        c.drawLine(xx, yy, xx - 4, yy + 20, stroke((180, 210, 255), 3, 150 * s))
    for k in range(5):
        ph = (t * 0.3 + k / 5) % 1
        molecule(c, 1480 + k * 40, 560 + 160 * ph, 0, 1.0, 255 * s * (1 - ph))
    # the climate stays in balance
    level = 0.5 + 0.04 * math.sin(t * 1.3)
    thermometer(c, 960, 280, level, mix(CYAN, LAVA, 0.5), None, 360)
    text(c, "CLIMATE", 960, 250, 30, WHITE, 230, 800, spacing=6)
    caption(c, "EARTH'S THERMOSTAT  ·  OVER MILLIONS OF YEARS", 960, 1030, YELLOW, 28, 255 * smooth(prog(t, THERMO[1] + 0.4, THERMO[1] + 0.8)))
    text(c, "CARBON OUT", 380, 900 + 40, 26, WHITE, 220 * r, 800, spacing=4)
    text(c, "CARBON BACK IN", 1560, 900 + 40, 26, WHITE, 220 * s, 800, spacing=4)


# ---------------------------------------------------------------- outro: the Earth is alive
def draw_night(c, t):
    z = lerp(1.0, 1.1, smooth(prog(t, NIGHT[0], DURATION)))
    cam(c, z, 1000, 640)
    c.drawPaint(shaded(linear((0, -200), (0, H), [(10, 10, 34), (60, 34, 90)])))
    c.save()
    c.rotate(-14, W / 2, H / 2)
    c.drawOval(skia.Rect.MakeXYWH(-200, 160, W + 400, 240), blur(fill((150, 120, 230), 45), 60))
    c.restore()
    Stars(300, 31).draw(c, t, 1.0)
    beat = 0.0
    for k in range(2):  # heartbeat pulses on "alive"
        beat += math.exp(-((t - (ALIVE_T + 0.35 + k * 0.45)) / 0.09) ** 2)
    x, y = volcano(c, 1320, 760, 900, 420, (60, 44, 90), crater=0.1, hot=1.0, t=t)
    glow(c, x, y, 200 + 220 * beat, LAVA, 140 + 100 * beat)
    _p1.draw(c, x, y - 10, t, 260, 70, 1.0, 0.12, 0.8)
    lava_flow(c, [(x - 6, y), (1250, 460), (1180, 620), (1080, 780)], 1.0, 14)
    for (yy, cc, seed) in [(760, (34, 22, 60), 61), (880, (22, 14, 42), 62)]:
        wavy_band(c, yy, 1080, cc, seed, 30)
    # the bird roasting a marshmallow over a little lava stream
    lava_flow(c, [(300, 960), (520, 940), (760, 970), (1000, 950)], 1.0, 16)
    c.drawPath(blob_path(560, 900, [70, 60, 66, 58, 72, 64], 0.3), fill((50, 36, 72)))
    turn = smooth(prog(t, ALIVE_T + 1.0, ALIVE_T + 1.5))
    bird(c, 560, 846, 70, t, look=(lerp(1, 0, turn), lerp(0.4, 0, turn)))
    c.drawLine(620, 790, 760, 900, stroke((150, 110, 80), 6))
    toast = smooth(prog(t, NIGHT[1], ALIVE_T))
    c.drawRRect(rrect(748, 888, 34, 30, 10), fill(mix((250, 245, 235), (200, 130, 70), toast)))
    glow(c, 765, 940, 90, LAVA, 90)
    c.restore()
    ea = smooth(prog(t, END_CARD, END_CARD + 0.8))
    if ea > 0:
        text(c, "WHY VOLCANOES EXIST", W / 2, 230, 70, WHITE, 255 * ea, 800, spacing=8)
        text(c, "SOURCES IN THE DESCRIPTION", W / 2, 290, 22, (220, 180, 255), 220 * ea, 800, spacing=6)


# ---------------------------------------------------------------- compose
def draw_frame(c, t):
    c.clear(col(NAVY))
    scenes(c, t, [((0.0, 0.01), EARLY[1], draw_deadly), (EARLY, SOIL[1], draw_early), (SOIL, LAND[1], draw_soil),
                  (LAND, THERMO[1], draw_land), (THERMO, NIGHT[1], draw_thermo), (NIGHT, DURATION + 1, draw_night)])
    vignette(c)
    chapter_fade(c, t, DURATION, 0.4, 1.4)


def sfx_events():
    return [(0.4, "rumble", 0.7), (OWE_T, "pop", 0.4), (EARLY[0], "whoosh_long", 0.6), (EARLY[0] + 0.5, "rumble", 0.5),
            (CLOUD[0], "swell_soft", 0.5), (OCEAN_T - 1.2, "sizzle", 0.3), (OCEAN_T, "bubble", 0.6), (OCEAN_T + 0.6, "chime", 0.5),
            (SOIL[0], "whoosh", 0.6)] + [(SOIL[1] + 0.3 + n * 0.25, "blip", 0.3) for n in range(7)] + [
            (LAND[0], "whoosh", 0.6), (LAND[1], "rumble", 0.6), (LAND[1] + 0.5, "sizzle", 0.5), (ICE_T, "pop", 0.6), (HAW_T, "pop", 0.6),
            (THERMO[0], "whoosh", 0.6), (RELEASE_T, "bubble", 0.4), (SOAK_T, "sizzle", 0.3), (SOAK_T + 0.3, "chime", 0.4),
            (NIGHT[0], "whoosh_long", 0.6), (NIGHT[0] + 0.5, "swell_soft", 0.7), (ALIVE_T + 0.35, "boom", 0.5), (ALIVE_T + 0.8, "boom", 0.4),
            (END_CARD, "swell_soft", 0.7)]


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 15, 19)), (4.3, 41, (0, 7, 12, 16, 19)), (10.5, 48, (0, 7, 12, 16, 19)),
            (15.0, 53, (0, 7, 11, 16, 19)), (19.7, 50, (0, 7, 12, 14, 17)), (28.1, 45, (0, 7, 12, 14, 19)),
            (34.6, 41, (0, 7, 11, 16, 19)), (37.4, 48, (0, 7, 12, 16, 19, 24))],
    plucks=[(4.6, 28.0), (28.6, 37.0)], bpm=96, rises=[(OCEAN_T - 1.5, OCEAN_T)],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
