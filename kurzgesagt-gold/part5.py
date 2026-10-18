"""Part 5: The punchline. All gold ever mined fits in a 22 m cube (next to a house and a person); a fast recap of the
four steps; the ring; the last frame flashes back into the explosion so a replay loops seamlessly.

  python3 render.py part5 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part5"
VO, _end = schedule(PART, first=0.3, gap=0.6)
DURATION = _end + 1.6
TM = Timing(PART, VO)

CUBE_T = 0.0
NUM_T = TM.word("O1", "twenty two") - 0.1
RECAP_T = VO["O2"] - 0.3
STEPS = [TM.word("O2", w) - 0.2 for w in ("forged", "lost to the core", "rained down", "squeezed out")]
RING_T = VO["O3"] - 0.4
LOOP_T = DURATION - 0.6

CAPS = Captions(TM, anchors={"O1": (W / 2, 330), "O2": (W / 2, 330), "O3": (W / 2, 330)})


def cube_scene(c, t):
    k = in_out(prog(t, 0.0, RECAP_T))
    c.drawPaint(shaded(linear((0, 0), (0, H), [(60, 110, 190), (150, 190, 230)])))
    light(c, 900, 200, 600, (255, 240, 210), 60)
    gy = 1300
    c.drawRect(skia.Rect.MakeXYWH(0, gy, W, H - gy), fill((90, 150, 90)))
    for i in range(30):
        c.drawLine(i * 40, gy + 20 + (i * 37) % 300, i * 40 + 10, gy + 5 + (i * 37) % 300, stroke((70, 130, 70), 4))
    g = out_back(prog(t, 0.4, 1.6), 1.2)
    s = 440 * g
    gx = 330
    top = poly([(gx, gy - s), (gx + 140 * g, gy - s - 90 * g), (gx + s + 140 * g, gy - s - 90 * g), (gx + s, gy - s)])
    side = poly([(gx + s, gy), (gx + s + 140 * g, gy - 90 * g), (gx + s + 140 * g, gy - s - 90 * g), (gx + s, gy - s)])
    c.drawOval(skia.Rect.MakeXYWH(gx - 40, gy - 30, s + 220, 70), fill((40, 60, 40), 100))
    c.drawRect(skia.Rect.MakeXYWH(gx, gy - s, s, s), shaded(linear((gx, gy - s), (gx + s, gy), [GOLD_HI, GOLD, GOLD_MID])))
    c.drawPath(top, shaded(linear((gx, gy - s - 90), (gx + s, gy - s), [GOLD_HI, GOLD])))
    c.drawPath(side, shaded(linear((gx + s, 0), (gx + s + 140, 0), [GOLD_MID, GOLD_DEEP])))
    sw = (t * 0.4) % 1.6 - 0.3
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(gx, gy - s, s, s))
    c.drawPath(poly([(gx + s * sw, gy - s), (gx + s * sw + 90, gy - s), (gx + s * sw - 110, gy), (gx + s * sw - 200, gy)]), fill(WHITE, 60))
    c.restore()
    if g > 0.9:
        sparkle4(c, gx + s + 120, gy - s - 60, 34 * (0.7 + 0.3 * math.sin(t * 5)), 255)
    hx = 840                       # house (~8 m) and a person for scale
    c.drawRect(skia.Rect.MakeXYWH(hx, gy - 130, 140, 130), fill((230, 220, 210)))
    c.drawPath(poly([(hx - 15, gy - 130), (hx + 70, gy - 190), (hx + 155, gy - 130)]), fill((180, 80, 70)))
    c.drawRect(skia.Rect.MakeXYWH(hx + 55, gy - 60, 30, 60), fill((120, 80, 60)))
    c.drawCircle(1010, gy - 32, 6, fill((60, 50, 70)))
    c.drawRect(skia.Rect.MakeXYWH(1006, gy - 26, 8, 26), fill((60, 50, 70)))
    na = smooth(prog(t, NUM_T, NUM_T + 0.3))
    if na > 0:
        c.drawLine(gx - 40, gy, gx - 40, gy - s, stroke(WHITE, 5, 255 * na))
        c.drawLine(gx - 60, gy - s, gx - 20, gy - s, stroke(WHITE, 5, 255 * na))
        hero(c, "22 M", W / 2, 640, t, NUM_T, 170)
    chip(c, "ALL GOLD EVER MINED", W / 2, 520, GOLD, t, 0.6, NUM_T - 0.1)
    text(c, "≈ 212,000 TONNES", W / 2, 1560, 50, WHITE, 255 * smooth(prog(t, 1.4, 1.8)) * (1 - smooth(prog(t, RECAP_T - 0.4, RECAP_T))), 800, spacing=4)


def recap_scene(c, t):
    """Four steps light up in a vertical chain: collision -> core -> meteors -> vein."""
    space_bg(c, t, warm=0.2)
    ys = [640, 900, 1160, 1420]
    labels = ["FORGED WHEN STARS COLLIDED", "LOST TO THE CORE", "RAINED DOWN FROM SPACE", "SQUEEZED OUT BY EARTHQUAKES"]
    if t < STEPS[0] + 0.3:   # "something golden": a nugget spins in, then shrinks into the first step of the chain
        u = in_out(prog(t, STEPS[0] - 0.7, STEPS[0] + 0.3))
        g = out_back(prog(t, RECAP_T, RECAP_T + 0.7), 1.4)
        nx, ny = lerp(W / 2, 150, u), lerp(1000, 640, u)
        light(c, nx, ny, 380 * (1 - 0.7 * u), GOLD, 90 * g)
        gold_sphere(c, nx, ny, lerp(170, 40, u) * g, (255, 200, 140))
        sparkle4(c, nx + 130 * (1 - u), ny - 120 * (1 - u), 40 * g * (0.7 + 0.3 * math.sin(t * 5)), 255 * (1 - u))
        for j in range(12):
            an = j / 12 * 6.28 + t * 0.6
            d = lerp(260, 60, u)
            c.drawCircle(nx + math.cos(an) * d, ny + math.sin(an) * d, 5, add(GOLD_HI, 160 * g * (1 - u)))
    for i, (y, lab) in enumerate(zip(ys, labels)):
        g = out_back(prog(t, STEPS[i], STEPS[i] + 0.45), 1.6)
        if g <= 0:
            continue
        x = 150
        if i < 3:
            c.drawLine(x, y + 70, x, lerp(y + 70, ys[i + 1] - 70, smooth(prog(t, STEPS[i + 1] - 0.3, STEPS[i + 1]))), stroke(GOLD, 6, 200))
        c.save()
        c.translate(x, y)
        c.scale(g, g)
        c.drawCircle(0, 0, 70, fill((20, 18, 50)))
        c.drawCircle(0, 0, 70, stroke(GOLD, 5))
        if i == 0:
            kilonova(c, 0, 0, 80, t, 0.35, seed=2)
        elif i == 1:
            earth_section(c, 0, 0, 52, t)
            gold_sphere(c, 0, 0, 16, (255, 140, 80))
        elif i == 2:
            meteor(c, 10, 10, 14, t, 238)
        else:
            c.drawLine(-8, -55, 8, 55, stroke(QUARTZ, 18))
            for j in range(4):
                gold_sphere(c, -4 + j * 3, -36 + j * 24, 6, (200, 190, 220))
        c.restore()
        text(c, lab, x + 100, y + 12, 32, WHITE if t < STEPS[i] + 0.8 else (235, 225, 210), 255 * min(1, g), 800, "left", spacing=2)


def ring_scene(c, t):
    space_bg(c, t, warm=0.4)
    light(c, W / 2, 960, 600, GOLD, 60)
    g = out_back(prog(t, RING_T, RING_T + 0.8), 1.3)
    ring(c, W / 2, 960, 0.95 * g, t, "both")
    sparkle4(c, W / 2 + 270, 900, 40 * (0.7 + 0.3 * math.sin(t * 5)) * g, 255)
    sparkle4(c, W / 2 - 290, 1020, 26 * g, 220)


def draw_frame(c, t):
    if t < RECAP_T:
        cube_scene(c, t)
    elif t < RING_T:
        recap_scene(c, t)
    else:
        ring_scene(c, t)
    for t0 in (RECAP_T, RING_T):
        if t0 - 0.1 < t < t0 + 0.25:
            c.drawPaint(fill(WHITE, 180 * (1 - abs(t - t0 - 0.05) / 0.2)))
    CAPS.draw(c, t)
    if t > LOOP_T:            # flash into the opening explosion so a replay loops seamlessly
        u = prog(t, LOOP_T, DURATION)
        kilonova(c, W / 2, 860, 700, t, 0.02 + 0.14 * u, seed=5)
        c.drawPaint(fill(HOTWHITE, 200 * u))


def sfx_events():
    return [(0.1, "swell_soft", 0.6), (0.4, "rumble", 0.6), (1.4, "boom", 0.6), (1.45, "shine", 0.8), (NUM_T, "boom", 0.7), (NUM_T + 0.05, "ding", 0.9),
            (RECAP_T, "whoosh", 0.7)] + [(x, "pop", 0.8) for x in STEPS] + [(x + 0.05, "tink", 0.5) for x in STEPS] + \
           [(RING_T, "whoosh", 0.6), (RING_T + 0.5, "chime", 0.9), (LOOP_T, "riser", 0.6), (DURATION - 0.1, "boom", 0.8)]


MUSIC = dict(chords=[(0.0, 48, (0, 7, 12, 16, 19)), (NUM_T, 50, (0, 7, 12, 16, 19, 24)), (RECAP_T, 45, (0, 7, 12, 15, 19)),
                     (RING_T, 48, (0, 7, 12, 16, 21))],
             plucks=[(0.3, DURATION)], bpm=104, rises=[(0.3, NUM_T), (STEPS[0], STEPS[-1])], drone=36)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
