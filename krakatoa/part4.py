"""Part 4, the part nobody heard: the globe; the pressure wave runs round and round it (out to the antipode and back,
again and again); a London barometer trace collects a spike each time the wave passes, over five days.

Wave timing is real-ish: one lap of the planet takes ~34 h, so London (11,700 km away) gets passes at about 10, 24,
44, 58, 78, 92 and 112 hours: seven spikes in five days. Video time maps linearly onto those 120 hours.

  python3 render.py part4 [--still 2,7,13]
"""
from film import *  # noqa: F401,F403

PART = "part4"
VO, _end = schedule(PART, first=0.5, gap=0.5)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)
DURATION = _end + 1.0

LAP_H = 34.0
T0, T1 = 0.4, TM.end("C3")                       # video span that covers hours 0..120
BARO_T = VO["C2"] - 0.2
EACH_T = TM.word("C3", "three")

CAPS = Captions(TM, ENV, sound=SOUND | {"barometers"}, harm=HARM)


def _ang(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    return math.acos(math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(math.radians(lon2 - lon1)))


D_LON = _ang(*KRAKATOA, *LONDON)                 # ~1.84 rad
PASSES = sorted(h for k in range(4) for h in (LAP_H * (k + D_LON / (2 * math.pi)), LAP_H * (k + 1 - D_LON / (2 * math.pi))) if h < 120)


def hours(t):
    return 120.0 * prog(t, T0, T1)


def globe(c, t, a=1.0):
    cx, cy, R = 540, 960, 400
    proj = Ortho(62 - 10 * prog(t, 0, DURATION), 16, R, cx, cy, -8)
    sh = skia.GradientShader.MakeRadial((cx - R * 0.35, cy - R * 0.4), R * 1.5, [col(mix(PRUSSIAN, PAPER, 0.1)), col(NIGHT)], [0, 1])
    c.drawCircle(cx, cy, R, skia.Paint(AntiAlias=True, Shader=sh))
    c.save()
    disc = skia.Path()
    disc.addCircle(cx, cy, R)
    c.clipPath(disc, doAntiAlias=True)
    graticule(c, proj, 1.0, 15)
    engraved_land(c, land_path(proj, "world", 0.0), hatch=6, water_lines=(6, 13))
    c.restore()
    c.drawCircle(cx, cy, R, paint(PAPER, 200, stroke=2.0))
    c.drawCircle(cx, cy, R + 6, paint(PAPER, 50, sigma=8, stroke=10))
    kx, ky, kz = proj(*KRAKATOA)
    if kz > 0:
        light(c, kx, ky, 60, LAVA, 200)
    # the wave front: phase grows one lap per 34 h; out to the antipode, then converging back
    ph = 2 * math.pi * hours(t) / LAP_H
    for k, lag in enumerate((0.0, 0.25, 0.5)):
        p = (ph - lag) % (2 * math.pi)
        if ph - lag < 0.02:
            continue
        ang = p if p <= math.pi else 2 * math.pi - p
        fade = math.exp(-hours(t) / 90)               # each lap a little weaker
        sphere_ring(c, proj, *KRAKATOA, max(ang, 0.02), SULFUR, (255 if k == 0 else 90 / k) * (0.45 + 0.55 * fade), 3.2 - k)
    lx, ly, lz = proj(*LONDON)
    if lz > 0:
        recent = min([abs(hours(t) - h) for h in PASSES] + [99])
        glow = math.exp(-recent * 0.6)
        light(c, lx, ly, 70, SULFUR, 200 * glow)
        pin(c, lx, ly, "LONDON", None, 255 * a, rgb=SULFUR if glow > 0.3 else PAPER, side=1, size=24)
    if kz > 0:
        pin(c, kx, ky, "KRAKATOA", None, 255 * a, side=-1, size=24)


def baro_card(c, t, a):
    """Five days of barograph paper; the ink trace is drawn up to the current hour with a spike at every pass."""
    x, y, w, h = 90, 330, 900, 200
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), paint(NIGHT, a * 0.85))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), paint(PAPER, a * 0.7, stroke=1.4))
    for i in range(1, 5):
        X = x + w * i / 5
        c.drawLine(X, y, X, y + h, paint(FADED, a * 0.35, stroke=1.0))
    for i in range(5):
        label(c, f"DAY {i + 1}", x + w * (i + 0.5) / 5, y + h + 30, 18, "mono", FADED, a, "center", 0.15)
    hr = hours(t)
    path = skia.Path()
    mid = y + h * 0.6
    for i in range(0, 601):
        hh = 120 * i / 600
        if hh > hr:
            break
        v = math.sin(hh * 0.9) * 2 + math.sin(hh * 2.7 + 1) * 1.2
        for n, pk in enumerate(PASSES):
            d = (hh - pk) * 1.6
            v -= h * 0.36 * math.exp(-0.18 * n) * math.exp(-d * d) * math.sin(d * 2.2 + 1.2)
        X = x + 10 + (w - 20) * hh / 120
        (path.lineTo if i else path.moveTo)(X, mid + v)
    glow_stroke(c, path, SULFUR, a, 2.2, 0.6)
    n = sum(1 for pk in PASSES if hr > pk)
    fig(c, 6, "BAROMETER, LONDON, 27 AUG – 1 SEP 1883", x, y - 18, a, size=18)
    label(c, f"{n}", x + w - 10, y + 70, 64, "mono_bold", SULFUR, a, "right")
    label(c, "PASSES", x + w - 10, y + 100, 18, "mono", FADED, a, "right", 0.2)


def draw_frame(c, t):
    paper(c)
    ga = smooth(prog(t, 0.0, 0.8))
    c.save()
    s = 0.85 + 0.15 * out_cubic(prog(t, 0, 1.6))
    c.translate(W / 2, 960)
    c.scale(s, s)
    c.translate(-W / 2, -960)
    globe(c, t, ga)
    c.restore()
    if t < BARO_T + 0.2:   # too low to hear: a hearing-range ruler with the wave below it
        ia = smooth(prog(t, VO["C1"] + 0.2, VO["C1"] + 0.8)) * (1 - smooth(prog(t, BARO_T - 0.3, BARO_T + 0.2)))
        hearing_ruler(c, ia * 255)
    ea = smooth(prog(t, EACH_T - 0.1, EACH_T + 0.4))
    if t > BARO_T:
        baro_card(c, t, 255 * smooth(prog(t, BARO_T, BARO_T + 0.5)) * (1 - ea))
    if ea > 0:
        big_number(c, "3–4×", 470, "AROUND THE PLANET, EACH WAY", ea, size=150)
    CAPS.draw(c, t)
    edges(c, t, DURATION, 0.3, 0.3)


def hearing_ruler(c, a):
    """Log frequency ruler, 1 Hz .. 20 kHz: the human range bracketed, the pressure wave far below it."""
    if a <= 1:
        return
    x0, x1, y = 120, 960, 470
    fx = lambda f: x0 + (x1 - x0) * math.log10(f / 0.01) / math.log10(20000 / 0.01)   # noqa: E731
    c.drawLine(x0, y, x1, y, paint(PAPER, a * 0.7, stroke=1.6))
    for f, s in ((0.01, "0.01"), (0.1, "0.1"), (1, "1"), (20, "20"), (1000, "1k"), (20000, "20k Hz")):
        X = fx(f)
        c.drawLine(X, y - 10, X, y + 10, paint(PAPER, a * 0.7, stroke=1.4))
        label(c, s, X, y + 40, 18, "mono", FADED, a, "center", 0.1)
    c.drawRect(skia.Rect.MakeLTRB(fx(20), y - 26, fx(20000), y - 14), paint(PAPER, a * 0.5))
    label(c, "HUMAN HEARING", (fx(20) + fx(20000)) / 2, y - 40, 20, "mono", PAPER, a, "center", 0.2)
    light(c, fx(0.03), y, 70, SULFUR, a * 0.7)
    c.drawCircle(fx(0.03), y, 9, paint(SULFUR, a))
    label(c, "THE WAVE", fx(0.03), y - 40, 20, "mono_bold", SULFUR, a, "center", 0.2)
    fig(c, 5, "INFRASOUND: TOO LOW TO HEAR", x0, 300, a, size=19)


def sfx_events():
    ev = [(0.0, "whoosh", 0.5)]
    for h in PASSES:   # a soft pen scratch every time the trace spikes
        tt = T0 + (T1 - T0) * h / 120
        if tt > BARO_T:
            ev.append((tt - 0.3, "pen_scratch", 0.55))
    ev.append((EACH_T, "low_hit", 0.35))
    return ev


MUSIC = dict(beds=[(0.0, DURATION, "wonder", 0.7), (0.0, DURATION, "deep", 0.45)])
