"""Part 4, Einstein's problem.

  * Two glass clocks, GROUND and ORBIT, start together and drift apart ("don't tick at the same speed"), then move up
    into a row at the top where they stay for the rest of the part (the drift is exaggerated and says so).
  * Speed: a small glass Earth; the satellite streaks round its orbit at 14,000 km/h; the ORBIT clock lags; chip
    "−7 µs / day" (SPEED).
  * Gravity: a glass funnel (how gravity curves time near Earth); the satellite rides the shallow rim; the ORBIT clock
    runs ahead; chip "+45 µs / day" (GRAVITY).
  * Sum: the chips slide into a glass card, −7 + 45 = +38 µs a day.

  python3 render.py part4 [--still 2,6,10,15,18,22]
"""
from film import *  # noqa: F401,F403

PART = "part4"
VO, _end = schedule(PART)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)

CLOCKS0, TICK = TM.word("C1", "Here's"), TM.word("C1", "tick")
FLY, FOURTEEN = TM.word("C2", "fly"), TM.word("C2", "fourteen")
EINSTEIN, SLOW = TM.word("C2", "Einstein"), TM.word("C2", "slow.")
SEVEN = TM.word("C2", "Seven")
GRAVITY, WEAKER = TM.word("C3", "gravity"), TM.word("C3", "weaker.")
FASTER = TM.word("C3", "faster.")
FORTY = TM.word("C3", "Forty")
ADD, GAIN = TM.word("C4", "Add"), TM.word("C4", "gain")
THIRTY, EVERY = TM.word("C4", "thirty"), TM.word("C4", "every")
SPEED_END = TM.end("C2") + 0.25
DURATION = TM.end("C4") + 0.8

CAPS = Captions(TM, ENV, words=WORDS, model=MODEL)
SEC0 = 10 * 3600 + 8 * 60 + 15.0


def drift(t):
    """How far the ORBIT clock's second hand is from GROUND (seconds, exaggerated for the eye)."""
    d = 0.8 * in_out(prog(t, TICK, TICK + 1.5))                     # "don't tick at the same speed"
    d -= 2.2 * in_out(prog(t, EINSTEIN, SEVEN + 0.5))                # moving clocks run slow
    d += 9.4 * in_out(prog(t, WEAKER, FORTY + 0.8))                  # weaker gravity: faster
    return d


def clocks(img, t):
    top = in_out(prog(t, TM.end("C1") + 0.1, FLY + 0.3))
    a = smooth(prog(t, CLOCKS0 - 0.3, CLOCKS0 + 0.3))
    if a <= 0.01:
        return img
    r = lerp(205, 128, top) * (0.9 + 0.1 * a)
    y = lerp(760, 420, top)
    xs = (lerp(285, 300, top), lerp(795, 780, top))
    secs = SEC0 + (t - CLOCKS0)
    d = drift(t)
    img = clock(img, xs[0], y, r, secs, AMBER, "GROUND", None, t, 0.25)
    img = clock(img, xs[1], y, r, secs + d, VIOLET, "ORBIT", None, t, 0.35)
    return img


def speed_scene(img, t, a):
    if a <= 0.01:
        return img
    cx, cy, r = 540, 1060, 170
    base = img.copy()
    pts = orbit_points(cx, cy, 330, 70, -12, 360, 0.0)
    u = (0.62 + (t - FLY) * 0.09) % 1 if t > FLY else 0.62
    k = int(u * 360)

    def back(c):
        orbit_line(c, pts, False, CYAN, 220, 1.8)
    img = over(img, layer(back))
    img, _ = earth(img, cx, cy, r, t, lon0=10 - 3 * t, lat0=20, spin=0.0)

    def front(c):
        orbit_line(c, pts, True, CYAN, 230, 1.8)
        if t > FLY - 0.2:
            for j in range(1, 40):                                   # streak behind the satellite
                x0, y0, _ = pts[(k - j) % 360]
                x1, y1, _ = pts[(k - j + 1) % 360]
                c.drawLine(x0, y0, x1, y1, paint(mix(CYAN, PAPER, 0.4), 230 * (1 - j / 40) ** 1.5, stroke=6 * (1 - j / 40) + 1))
        x, y, z = pts[k]
        mini_sat(c, x, y, 26, 0.3, 255)
    img = over(img, layer(front))
    x, y, _ = pts[k]
    img = chip(img, "14,000 km/h", x, y - 70, 30, CYAN, smooth(prog(t, FOURTEEN - 0.2, FOURTEEN + 0.3)))
    img = chip(img, "MOVING CLOCKS RUN SLOW", W / 2, 1290, 26, PAPER, window(t, EINSTEIN, SEVEN - 0.2, 0.3, 0.3))
    return base * (1 - a) + img * a


def funnel_scene(img, t, a):
    if a <= 0.01:
        return img
    cx, base_y = 540, 930
    rings = []
    for k in range(1, 11):
        rx = 40 + k * 46
        y = base_y + 360 / (k + 0.9)
        rings.append((rx, rx * 0.26, y))

    def draw(c):
        for i, (rx, ry, y) in enumerate(rings):
            c.drawOval(skia.Rect.MakeLTRB(cx - rx, y - ry, cx + rx, y + ry),
                       paint(CYAN, (60 + 14 * i) * a, stroke=1.6 + 0.12 * i))
        for s in range(16):                                         # spokes down the funnel
            th = 2 * math.pi * s / 16
            path = skia.Path()
            for i, (rx, ry, y) in enumerate(rings):
                px, py = cx + rx * math.cos(th), y + ry * math.sin(th)
                path.moveTo(px, py) if i == 0 else path.lineTo(px, py)
            c.drawPath(path, paint(CYAN, 70 * a, stroke=1.4))
        lab = smooth(prog(t, GRAVITY, GRAVITY + 0.4))
        label(c, "STRONG GRAVITY", cx, rings[0][2] + 130, 22, "mono", SMOKE, 255 * a * lab, "center", 0.16)
        label(c, "WEAKER GRAVITY", cx + rings[-1][0] - 10, rings[-1][2] - 70, 22, "mono", VIOLET, 255 * a * lab, "right", 0.16)
    img2 = over(img.copy(), layer(draw))
    rx, ry, y = rings[0]
    img2, _ = earth(img2, cx, y - 30, 78, t, lon0=-20 - 4 * t, lat0=20, spin=0.0)
    th = (t - GRAVITY) * 0.7 - 0.4
    rx, ry, y = rings[-1]
    sx, sy = cx + rx * math.cos(th), y + ry * math.sin(th)
    rim = smooth(prog(t, WEAKER - 0.2, WEAKER + 0.3))
    img2 = over(img2, layer(lambda c: (c.drawOval(skia.Rect.MakeLTRB(cx - rx, y - ry, cx + rx, y + ry),
                                                  paint(VIOLET, 200 * rim, sigma=6, stroke=6)),
                                       mini_sat(c, sx, sy, 24, 0.3, 255))))
    return img * (1 - a) + img2 * a


def sum_scene(img, t):
    q = in_out(prog(t, ADD, ADD + 0.8))
    a = smooth(prog(t, ADD - 0.1, ADD + 0.4))
    if a <= 0.01:
        return img
    x0, y0, w_, h_ = 110, 1040, 860, 220
    img = card(img, x0, y0, w_, h_, a, 40, tint=0.4, sheen=(0.7, 50, 0.07))
    ra = smooth(prog(t, THIRTY - 0.1, THIRTY + 0.3))

    def sums(c):
        items = [("−7", PAPER, "SPEED", 230), ("+", SMOKE, "", 345), ("45", PAPER, "GRAVITY", 460), ("=", SMOKE, "", 590),
                 ("+38", VIOLET, "µs / DAY", 770)]
        for s, rgb, sub, x in items:
            if rgb == VIOLET:
                if ra <= 0:
                    continue
                label(c, s, x, y0 + 138, 104, "mono_bold", rgb, 160 * ra, "center", sigma=16)
                label(c, s, x, y0 + 138, 104 * (1.15 - 0.15 * out_cubic(ra)), "mono_bold", rgb, 255 * ra, "center")
            else:
                label(c, s, x, y0 + 138, 100 if sub else 72, "mono_bold" if sub else "mono", rgb, 255 * a * q, "center")
            if sub:
                label(c, sub, x, y0 + 186, 22, "mono", SMOKE, 255 * a * (q if rgb != VIOLET else ra), "center", 0.2)
    return over(img, layer(sums))


def draw_frame(t):
    img = backdrop(t, glow=(0.5, 0.36), floor=0.82, pool=(540, 1600, 420, 60), caustic=0.8)
    sa = window(t, FLY - 0.3, SPEED_END, 0.5, 0.45)
    fa = window(t, SPEED_END - 0.1, ADD + 0.2, 0.5, 0.5)
    img = speed_scene(img, t, sa)
    img = funnel_scene(img, t, fa)
    img = clocks(img, t)
    # the two contributions as chips under the clocks, then they slide into the sum
    slide = in_out(prog(t, ADD, ADD + 0.6))
    ca = smooth(prog(t, SEVEN - 0.1, SEVEN + 0.3)) * (1 - slide)
    img = chip(img, "−7 µs / day", lerp(300, 230, slide), lerp(720, 1140, slide), 30, PAPER, ca, sub="SPEED")
    ga = smooth(prog(t, FORTY - 0.1, FORTY + 0.3)) * (1 - slide)
    img = chip(img, "+45 µs / day", lerp(780, 460, slide), lerp(720, 1140, slide), 30, PAPER, ga, sub="GRAVITY")
    img = sum_scene(img, t)
    ex = smooth(prog(t, CLOCKS0 + 1.0, CLOCKS0 + 1.6))
    img = over(img, layer(lambda c: label(c, "HAND DRIFT EXAGGERATED", W / 2, 272, 20, "mono", SMOKE, 200 * ex, "center", 0.2)))
    if t > EVERY - 0.2:
        img = over(img, layer(lambda c: glow_text(c, "+38 µs", 540, 430, 40, "mono_bold", VIOLET,
                                                  255 * smooth(prog(t, EVERY - 0.2, EVERY + 0.3)))))
    img = CAPS.draw(img, t)
    img = fade(img, max(1 - smooth(prog(t, 0, 0.3)), smooth(prog(t, DURATION - 0.25, DURATION))))
    return img


def samples_at(t):
    return 2 if FLY - 0.2 < t < SPEED_END else 1


def sfx_events():
    ev = [(CLOCKS0 - 0.2, "clink", 0.5), (TICK, "detune", 0.25), (TM.end("C1"), "glass_whoosh", 0.45),
          (FLY - 0.1, "whoosh", 0.6), (FOURTEEN, "tick_roll", 0.35), (EINSTEIN, "shimmer", 0.3),
          (SEVEN, "clink", 0.55), (SPEED_END - 0.1, "glass_whoosh", 0.45), (WEAKER - 0.2, "riser", 0.3),
          (FORTY, "clink", 0.6), (ADD, "glass_whoosh", 0.4), (ADD + 0.6, "clink", 0.45),
          (THIRTY - 0.05, "low_hit", 0.45), (THIRTY, "chime", 0.55), (EVERY, "ping", 0.4)]
    return ev


MUSIC = dict(beds=[(0.0, DURATION, "glass", 0.9)])
