"""Part 8: Outro, Still Unexplored. Nimbus sinks its gaze into the ocean: a sonar sweep maps only a quarter of the
floor; dark water hides the rest (glowing deep-sea creatures); pull back to the globe and the end card.

  python3 render.py part8 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part8"
VO, _end = schedule(PART, first=2.4, gap=1.2)
DURATION = _end + 4.2
TM = Timing(PART, VO)

MAP_T = TM.word("O1", "quarter") - 0.4
DARK_T = VO["O2"] - 0.3
SECRET_T = VO["O3"] - 0.4
END_T = _end + 0.5

NIM_TRACK = Track([(0.0, "focused", 0.0), (MAP_T, "shocked", 0.2), (MAP_T + 1.4, "worried", 0.4), (DARK_T + 1.0, "focused", 0.4),
                   (SECRET_T + 1.0, "happy", 0.4), (END_T - 0.8, "wink", 0.25), (END_T + 0.4, "happy", 0.3)])
ANGLER = Track([(0.0, "neutral", 0.0), (DARK_T + 1.6, "smug", 0.35), (DARK_T + 3.0, "wink", 0.25)])


def anglerfish(c, x, y, s, t, p):
    lx, ly = x + s * 1.1, y - s * 0.9 + 6 * math.sin(t * 2)
    c.drawLine(x + s * 0.4, y - s * 0.5, lx, ly, stroke((80, 70, 110), s * 0.06))
    light(c, lx, ly, s * 1.4, (140, 255, 220), 230)
    c.drawCircle(lx, ly, s * 0.1, fill((220, 255, 240)))
    body = skia.Path()
    body.addOval(skia.Rect.MakeXYWH(x - s, y - s * 0.65, s * 1.9, s * 1.3))
    c.drawPath(body, fill((60, 52, 90)))
    c.drawPath(poly([(x - s * 0.9, y), (x - s * 1.5, y - s * 0.5), (x - s * 1.5, y + s * 0.5)]), fill((50, 44, 80)))
    for k in range(6):
        tx = x + s * 0.3 + k * s * 0.1
        c.drawPath(poly([(tx, y + s * 0.15), (tx + s * 0.05, y + s * 0.32), (tx + s * 0.1, y + s * 0.15)]), fill((230, 230, 240)))
    face_rig(c, x + s * 0.25, y - s * 0.2, s * 0.45, p, (0.4, 0.0), 0.0, ink=(10, 10, 30))


def scene_ocean(c, t):
    """Cross-section of the ocean: bright surface at the top, sonar fan maps a strip, darkness below."""
    k = in_out(prog(t, 0.0, DARK_T + 2))
    depth = lerp(0, 560, k)
    c.drawPaint(shaded(linear((0, -depth), (0, H + 900 - depth), [(70, 160, 230), (20, 60, 140), (4, 10, 34)], [0, 0.35, 1])))
    sy = 200 - depth
    if sy > -50:
        c.drawRect(skia.Rect.MakeXYWH(0, sy - 300, W, 300), shaded(linear((0, sy - 300), (0, sy), [(120, 180, 240), (170, 210, 250)])))
        p = skia.Path()
        p.moveTo(0, sy)
        for x in range(0, W + 40, 40):
            p.lineTo(x, sy + 8 * math.sin(x * 0.02 + t * 2))
        c.drawPath(p, stroke(WHITE, 4, 180))
    # sea floor profile far below
    fy = 1300 - depth
    floor = skia.Path()
    floor.moveTo(-50, H + 600)
    pts = []
    for x in range(-50, W + 60, 20):
        y = fy + 90 * math.sin(x * 0.004 + 1) + 40 * math.sin(x * 0.013) + 140 * math.exp(-((x - 1300) / 160) ** 2) * -1
        pts.append((x, y))
        floor.lineTo(x, y)
    floor.lineTo(W + 60, H + 600)
    floor.close()
    c.drawPath(floor, shaded(linear((0, fy - 150), (0, fy + 400), [(70, 56, 80), (30, 24, 40)])))
    c.drawPath(floor, stroke((110, 90, 120), 4, 200))
    # the mapped quarter: a sonar fan from a little ship sweeps and leaves a coloured, detailed strip
    sw = smooth(prog(t, MAP_T - 1.0, MAP_T + 1.2))
    shipx = lerp(200, 640, sw)
    if sy > -50:
        c.drawPath(poly([(shipx - 50, sy - 8), (shipx + 50, sy - 8), (shipx + 34, sy + 14), (shipx - 34, sy + 14)]), fill((230, 90, 70)))
        c.drawRect(skia.Rect.MakeXYWH(shipx - 10, sy - 40, 20, 32), fill(WHITE))
    if sw > 0:
        fan = skia.Path()
        fan.moveTo(shipx, sy + 14)
        fan.lineTo(shipx - 160, fy)
        fan.lineTo(shipx + 160, fy)
        fan.close()
        fp = skia.Paint(AntiAlias=True, Shader=linear((0, sy), (0, fy), [((120, 255, 220), 90), ((120, 255, 220), 10)]))
        fp.setBlendMode(skia.BlendMode.kPlus)
        c.drawPath(fan, fp)
        strip = skia.Path()
        x_end = 480 * sw          # a quarter of the width
        first = True
        for x, y in pts:
            if x > x_end:
                break
            (strip.moveTo if first else strip.lineTo)(x, y)
            first = False
        c.drawPath(strip, stroke((120, 255, 200), 8))
        for x, y in pts:
            if x > x_end:
                break
            c.drawLine(x, y, x, y + 30, stroke(mix((255, 120, 80), (80, 200, 255), (y - fy + 150) / 300), 18, 200))
    big_number(c, "~25% MAPPED", 1300, 300 - depth * 0.3, 96, (140, 255, 210), t, MAP_T + 0.4, SECRET_T, sub="OF THE OCEAN FLOOR, IN DETAIL")
    # deep-sea glow creatures once it gets dark
    if t > DARK_T:
        a = smooth(prog(t, DARK_T, DARK_T + 1.2))
        rng = np.random.default_rng(8)
        for i in range(30):
            x = rng.uniform(0, W) + 20 * math.sin(t * 0.5 + i)
            y = rng.uniform(450, 1000) + 15 * math.cos(t * 0.6 + i)
            c.drawCircle(x, y, 3, add((120, 255, 220), 200 * a * (0.5 + 0.5 * math.sin(t * 3 + i))))
        anglerfish(c, lerp(-200, 1200, out_cubic(prog(t, DARK_T + 0.6, SECRET_T + 1.0))), 700, 110, t, ANGLER.at(t))
        text(c, "KILOMETRES OF DARK WATER", 960, 1000, 26, (160, 220, 255), 230 * a, 800, spacing=6)

    def path(tt):
        return 1560 + 20 * math.sin(tt * 0.7), lerp(140, 380, in_out(prog(tt, 0.0, DARK_T + 2))) + 12 * math.sin(tt * 1.3)
    nim(c, t, NIM_TRACK, path, 100, look=(-0.4, 0.8), rim=(140, 220, 255), tint=((20, 40, 90), 90 * k))


def scene_end(c, t):
    sky(c, t, mood="space")
    k = out_cubic(prog(t, SECRET_T - 0.4, SECRET_T + 2.4))
    globe(c, 960, lerp(1500, 560, k), lerp(900, 300, k), t, rot=t * 0.1, tilt=0.3)
    for i in range(6):      # secrets glinting on the globe
        an = t * 0.4 + i * 1.05
        x, y = 960 + math.cos(an) * 220, lerp(1500, 560, k) + math.sin(an * 1.3) * 180
        sparkle(c, x, y, 26 * (0.6 + 0.4 * math.sin(t * 4 + i)), 230 * k, GOLD)

    def path(tt):
        return 1460 + 20 * math.sin(tt * 0.7), 360 + 12 * math.sin(tt * 1.3)
    hands = (None, (1460 + 150 + 15 * math.sin(t * 12), 240)) if t > END_T else (None, None)
    nim(c, t, NIM_TRACK, path, 120, look=(-0.7, 0.3), rim=(150, 200, 255), hands=hands, sparkle_=float(t > SECRET_T + 1.0))
    e = smooth(prog(t, END_T, END_T + 0.8))
    if e > 0:
        c.drawPaint(fill((6, 8, 24), 238 * e))
        text(c, "EARTH IS", 960, 430, 46, WHITE, 255 * e, 800, spacing=12)
        text(c, "WEIRDER THAN YOU THINK", 960, 530, 84, GOLD, 255 * e, 800, spacing=lerp(24, 10, out_cubic(prog(t, END_T, END_T + 2))))
        nimbus(c, 960, 740, 80, t, NIM_TRACK.at(t), (0.0, 0.0), blink_amount(t, (), 3.8, 0.2), a=255 * smooth(prog(t, END_T + 0.6, END_T + 1.2)))


def draw_frame(c, t):
    xfade(c, t, SECRET_T - 0.6, 1.0, scene_ocean, scene_end, 0.3)
    chapter_title(c, t, 7, "STILL UNEXPLORED", (140, 255, 210), 0.2, 2.4)
    fade(c, t, DURATION, 0.5, 1.0)


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (0.6, "bubble", 0.5), (MAP_T - 1.0, "slide", 0.5)] + [(MAP_T - 1.0 + 0.4 * i, "blip", 0.4) for i in range(6)] + \
           [(MAP_T + 0.4, "ding", 0.7), (DARK_T, "rumble", 0.6), (DARK_T + 0.8, "shimmer", 0.6), (DARK_T + 3.0, "pop", 0.5), (SECRET_T - 0.6, "whoosh_long", 0.8),
            (SECRET_T + 0.6, "swell_soft", 0.8), (SECRET_T + 1.2, "shine", 0.6), (END_T, "swell_soft", 0.9), (END_T + 0.7, "chime", 0.7)]


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 14, 19)), (MAP_T, 47, (0, 7, 12, 16, 19)), (DARK_T, 43, (0, 7, 12, 15, 19)), (SECRET_T, 48, (0, 7, 12, 16, 19)),
            (END_T, 50, (0, 7, 12, 16, 19, 24))],
    plucks=[(VO["O1"], DARK_T), (SECRET_T, DURATION)], bpm=92, rises=[(SECRET_T, END_T)], drone=36,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
