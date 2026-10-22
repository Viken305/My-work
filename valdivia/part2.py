"""Part 2: the crack. Cut-paper section of the subduction zone: the plates slide, stick, strain builds, the clock runs
to 15:11, "it let go" (the fault slices the caption), then the map: the crack tears ~1,000 km down the coast."""
from common import *  # noqa: F401,F403

PART = "part2"
VO, _end = schedule(PART, first=0.8, gap=0.55, extra={"A3": 1.1})
TM = Timing(PART, VO)
T_STICK = TM.word("A1", "sticks")
T_BUILD = TM.word("A2", "strain")
T_DATE = TM.word("A2", "twenty")
T_TIME = TM.word("A2", "eleven")
T_IT = TM.word("A2", "it let go")
T_GO = TM.word("A2", "go")
T_MAP = VO["A3"] - 0.6
T_CRACK = TM.word("A3", "crack")
T_COAST = TM.word("A3", "coast", end=True)
T_LURCH = TM.word("A3", "lurched")
T_20 = TM.word("A3", "twenty")
DURATION = _end + 1.0
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"sticks": RED, "strain": RED}),
               hide={"A2": [(T_IT - 0.1, T_GO + 2.0)]})
SEA = 760


def shake(t):
    return shake_env(t, T_GO, 1.0, 0.08, 2.2)


def strain(t):
    """0 -> 1 while the plates are stuck; snaps back after the rupture."""
    if t < T_GO:
        return 0.15 * smooth(prog(t, T_STICK - 0.4, T_STICK + 0.6)) + 0.85 * smooth(prog(t, T_BUILD, T_GO))
    return 1 - spring(prog(t, T_GO, T_GO + 0.9), 6, 12)


def moving_hatch(c, path, off, a=70, step=6, ang=-20, rgb=INK):
    c.save()
    c.clipPath(path, doAntiAlias=True)
    r = math.radians(ang)
    dx, dy = math.cos(r), math.sin(r)
    nx, ny = -dy, dx
    o = off % step
    for k in range(-260, 260):
        d = k * step + o
        x0, y0 = 540 + nx * d, 1000 + ny * d
        c.drawLine(x0 - dx * 1500, y0 - dy * 1500, x0 + dx * 1500, y0 + dy * 1500, paint(rgb, a, stroke=1.0))
    c.restore()


def layer_in(c, t, delay):
    k = out_expo(prog(t, 0.15 + delay, 0.95 + delay))
    c.translate(0, (1 - k) * 260)
    return k


def section(c, t):
    s = strain(t)
    slide = t * 14 if t < T_GO else T_GO * 14 + 0  # the plate creeps in, then stops (stuck)
    slide = min(t, T_STICK) * 14 + max(0.0, t - T_GO) * 0 + (24 * spring(prog(t, T_GO, T_GO + 0.6), 6, 10) if t > T_GO else 0)
    c.save()
    a = layer_in(c, t, 0.0)
    mantle = skia.Path()
    mantle.addRect(skia.Rect.MakeLTRB(-20, 820, W + 20, 1270))
    cutout(c, mantle, mix(SHADE, SEPIA, 0.25), 255 * a, lift=10, edge_a=0)
    stipple(c, mantle, 2600, 70 * a, 3)
    c.drawLine(-20, 1270, W + 20, 1270, paint(INK, 220 * a, stroke=1.6))
    label(c, "MANTLE", 70, 1240, 20, "mono", INK, 170 * a, tracking=0.2)
    c.restore()
    c.save()
    a = layer_in(c, t, 0.12)
    ocean = skia.Path()
    ocean.moveTo(-20, SEA)
    ocean.lineTo(600, SEA)
    ocean.lineTo(530, 800)
    ocean.lineTo(440, 905)
    ocean.lineTo(-20, 868)
    ocean.close()
    c.drawPath(ocean, paint(mix(BONE, TEAL, 0.16), 255 * a))
    c.save()
    c.clipPath(ocean, doAntiAlias=True)
    for y in range(SEA + 8, 920, 8):
        wob = math.sin(t * 1.3 + y * 0.05) * 6
        c.drawLine(-20, y + wob * 0.2, 620, y + wob * 0.2, paint(TEAL, 110 * a, stroke=1.0))
    c.restore()
    c.drawLine(-20, SEA, 600, SEA, paint(TEAL, 255 * a, stroke=2.4))
    label(c, "PACIFIC OCEAN", 70, 812, 22, "mono_bold", TEAL, 255 * a, tracking=0.16)
    c.restore()
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(-20, 0, W + 20, 1270))
    c.save()
    a = layer_in(c, t, 0.24)
    nazca = skia.Path()
    nazca.moveTo(-20, 868)
    nazca.lineTo(440, 905)
    nazca.cubicTo(640, 960, 860, 1080, 1100, 1250)
    nazca.lineTo(1100, 1380)
    nazca.cubicTo(860, 1200, 620, 1080, 400, 1020)
    nazca.lineTo(-20, 985)
    nazca.close()
    cutout(c, nazca, mix(SHADE, INK, 0.12), 255 * a, lift=12)
    moving_hatch(c, nazca, slide, 70 * a)
    label(c, "NAZCA PLATE", 90, 950, 24, "mono_bold", INK, 255 * a, tracking=0.16)
    c.restore()
    c.save()
    a = layer_in(c, t, 0.36)
    sa = skia.Path()
    pts = [(440, 905), (530, 800), (600, SEA), (650, 748), (700, 740), (740, 716), (790, 690), (830, 640), (855, 610),
           (880, 562), (905, 610), (940, 640), (990, 618), (1030, 650), (1100, 660)]
    for i, (x, y) in enumerate(pts):
        bend = 0.0
        if x < 760:            # the leading edge is dragged down while stuck...
            bend = 34 * s * (1 - (x - 440) / 320)
        elif x < 1000:         # ...and the land behind it bulges up
            bend = -14 * s * math.sin(math.pi * (x - 760) / 240)
        (sa.lineTo if i else sa.moveTo)(x, y + bend)
    sa.lineTo(1100, 1250)
    sa.cubicTo(860, 1080, 640, 960, 440 + 0, 905 + 34 * s)
    sa.close()
    cutout(c, sa, WHITE, 255 * a, lift=16)
    hatch(c, sa, 45 * a, 9, 35, INK, 0.9)
    label(c, "SOUTH AMERICAN PLATE", 1040, 880, 24, "mono_bold", INK, 255 * a, "right", 0.16)
    label(c, "ANDES", 880, 530, 20, "mono", INK, 220 * a, "center", 0.2)
    c.restore()
    c.restore()
    # plate motion arrow (stops when stuck)
    aa = appear(t, 1.2) * (1 - appear(t, T_STICK, 0.2) * 0.6)
    for (x, y) in ((300, 885),):
        ar = skia.Path()
        ar.moveTo(x, y)
        ar.lineTo(x + 90, y + 22)
        ink(c, ar, INK, 255 * aa, 3.2)
        hd = skia.Path()
        hd.moveTo(x + 92, y + 23)
        hd.lineTo(x + 70, y + 8)
        hd.lineTo(x + 66, y + 30)
        hd.close()
        c.drawPath(hd, paint(INK, 255 * aa))
    label(c, "~7 CM A YEAR", 300, 862, 18, "mono", INK, 230 * aa, tracking=0.12)
    # the locked zone
    la = smooth(prog(t, T_STICK - 0.2, T_STICK + 0.3))
    if la > 0:
        lock = skia.Path()
        lock.moveTo(450, 908 + 30 * s)
        lock.cubicTo(560, 935 + 18 * s, 680, 985 + 6 * s, 790, 1050)
        glow(c, lock, RED, 255 * la, 4 + 3 * s, 0.6 + 1.2 * s)
        for k in range(9):
            u = 0.1 + k * 0.1
            x, y = 450 + u * 340, 908 + u * 142 - 10 * math.sin(u * 3) + 26 * s * (1 - u)
            bend = 0.4 + 1.4 * s
            c.drawLine(x - 10 * bend, y - 24, x + 10 * bend, y + 24, paint(RED, 200 * la * (1 if t < T_GO else 1 - appear(t, T_GO, 0.6)), stroke=2))
        if t < T_GO + 0.5:
            dim_line(c, 470, 960, 760, 1110, "STUCK", 255 * la * (1 - appear(t, T_GO, 0.3)), RED, 20, tick=8)
    # after the rupture: slip arrows along the fault
    if t > T_GO:
        k = out_expo(prog(t, T_GO, T_GO + 0.5))
        for j, (x, y) in enumerate(((520, 900), (650, 960))):
            ar = skia.Path()
            ar.moveTo(x, y)
            ar.lineTo(x - 70 * k, y - 34 * k)
            glow(c, ar, RED, 255, 4, 0.6)
        c.drawCircle(470, 930, 140 * k, paint(RED, 140 * (1 - k), stroke=6))


def clock(c, t):
    da = appear(t, T_DATE - 0.1)
    if da <= 0:
        return
    sec = 57 + 3 * clamp(prog(round(t * FPS) / FPS, T_TIME, T_GO))
    mm, ss = (11, 0) if sec >= 60 else (10, int(sec))
    big = t >= T_TIME - 0.1
    card(c, 620, 320, 400, 150, 255 * da)
    label(c, "22 MAY 1960", 820, 372, 26, "mono_bold", INK, 255 * da, "center", 0.12)
    if big:
        rgb = RED if t >= T_GO else INK
        label(c, f"15:{mm:02d}:{ss:02d}", 820, 446, 60, "mono_bold", rgb, 255 * appear(t, T_TIME - 0.1), "center")


def strain_meter(c, t):
    a = appear(t, T_BUILD - 0.3) * (1 - appear(t, T_MAP, 0.4))
    if a <= 0:
        return
    s = strain(t)
    tab(c, 70, 330, 380, 80, 255 * a)
    label(c, "STRAIN", 86, 362, 18, "mono", SEPIA, 255 * a, tracking=0.2)
    c.drawRect(skia.Rect.MakeXYWH(86, 378, 340, 16), paint(INK, 200 * a, stroke=1.4))
    c.drawRect(skia.Rect.MakeXYWH(88, 380, 336 * clamp(s), 12), paint(RED, 255 * a))
    yrs = int(lerp(1575, 1960, smooth(prog(t, T_BUILD, T_DATE)))) if t < T_GO else 1960
    label(c, f"{yrs}", 426, 362, 18, "mono_bold", INK, 255 * a, "right")


def split_caption(c, t):
    if not (T_IT - 0.1 <= t <= T_GO + 2.0):
        return
    a = appear(t, T_IT - 0.1, 0.2) * (1 - smooth(prog(t, T_GO + 1.6, T_GO + 2.0)))
    slip = 30 * out_expo(prog(t, T_GO, T_GO + 0.22))
    line = smooth(prog(t, T_GO - 0.05, T_GO + 0.08))
    c.save()
    c.translate(0, -30 * smooth(prog(t, T_GO + 1.6, T_GO + 2.0)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(230, 1300, 620, 180), 40, 40), paint(BONE, 200 * a, sigma=24))
    if line > 0:
        caption_split(c, ["it", "let", "go"], 1440, 130, {2: RED}, (230, 1300), (860, 1560), slip=slip, a=a)
    else:
        kinds, sizes, ws, xs, total = _word_layout(["it", "let", "go"], 130, {2: RED})
        for i, wd in enumerate(["it", "let", "go"]):
            wa = a * appear(t, [T_IT, T_IT + 0.12, T_GO - 0.02][i], 0.12)
            label(c, wd, xs[i], 1440, sizes[i], kinds[i], RED if i == 2 else INK, 255 * wa)
    c.restore()


from ink import _word_layout  # noqa: E402


def chile_map(c, t):
    a = smooth(prog(t, T_MAP, T_MAP + 0.8))
    if a <= 0:
        return
    chart = Chart(-84, -62, -49.5, -31.5, 40, 320, 1000)
    rect = skia.Rect.MakeXYWH(40, 320, 1000, chart.h)
    c.save()
    c.translate(0, (1 - out_expo(prog(t, T_MAP, T_MAP + 0.9))) * 500)
    card(c, 36, 316, 1008, chart.h + 8, 255 * a)
    c.save()
    c.clipRect(rect)
    c.drawRect(rect, paint(mix(BONE, TEAL, 0.06), 255 * a))
    for lat in range(-48, -31, 4):
        _, y, _ = chart(-70, lat)
        c.drawLine(40, y, 1040, y, paint(SEPIA, 90 * a, stroke=1.0))
        label(c, f"{-lat}°S", 1030, y - 6, 15, "mono", SEPIA, 255 * a, "right")
    engraved_land(c, land_path(chart, "world"), a, step=6, water_lines=(8, 18, 30), key="chile_big")
    pts = [chart(lon, lat)[:2] for lon, lat in RUPTURE]
    dense = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for k in range(12):
            dense.append((x0 + (x1 - x0) * k / 12, y0 + (y1 - y0) * k / 12))
    dense.append(pts[-1])
    u = out_cubic(prog(t, T_CRACK, T_COAST + 0.3))
    if u > 0:
        p, tip = polyline(dense, u)
        glow(c, p, RED, 255, 6, 1.2)
        if tip and u < 1:
            light_tip = skia.Path()
            light_tip.addCircle(*tip, 14)
            c.drawPath(light_tip, paint(RED, 160, sigma=10, blend=MULT))
    c.restore()
    ex, ey, _ = chart(*EPI)
    star(c, ex, ey, 16, RED, 255 * a)
    vx, vy, _ = chart(*VALDIVIA)
    tab(c, vx + 18, vy - 20, 170, 34, 255 * a)
    pin(c, vx, vy, "VALDIVIA", None, 255 * a, side=1, size=22)
    if u > 0:
        (ax, ay), (bx, by) = pts[0], pts[-1]
        X = min(ax, bx) - 60
        yb = ay + (by - ay) * u
        c.drawLine(X, ay, X, yb, paint(RED, 230, stroke=1.6))
        c.drawLine(X - 9, ay, X + 9, ay, paint(RED, 230, stroke=1.6))
        c.drawLine(X - 9, yb, X + 9, yb, paint(RED, 230, stroke=1.6))
        u = out_cubic(prog(round(t * FPS) / FPS, T_CRACK, T_COAST + 0.3))
        km = 1000 if u > 0.985 else round(1000 * u, -1)
        tab(c, X - 230, (ay + yb) / 2 - 30, 210, 46)
        label(c, f"≈{km:,.0f} KM", X - 30, (ay + yb) / 2 + 4, 30, "mono_bold", RED, 255, "right")
    sa = pop(t, T_LURCH, 0.4)
    if sa > 0:
        c.save()
        c.translate(300, 1180)
        c.scale(clamp(sa), clamp(sa))
        tab(c, -190, -50, 380, 96)
        label(c, "SLIP", 0, -18, 18, "mono", SEPIA, 255, "center", 0.2)
        label(c, "UP TO 20 M", 0, 30, 40, "mono_bold", RED, 255, "center")
        c.restore()
    c.restore()


def draw_frame(c, t):
    paper(c)
    c.save()
    c.translate(0, drum_scroll(t, DURATION, 0.0, 0.6))
    out = in_cubic(prog(t, T_MAP - 0.1, T_MAP + 0.6))
    if out < 1:
        c.save()
        c.translate(0, -out * 700)
        section(c, t)
        clock(c, t)
        strain_meter(c, t)
        c.restore()
    fig(c, 2, "CHILE, IN SECTION" if t < T_MAP + 0.2 else "THE CRACK, 22 MAY 1960", 70, 268, size=20)
    chile_map(c, t)
    # the rupture: a red paper flash
    fl = 1 - smooth(prog(t, T_GO, T_GO + 0.35)) if t >= T_GO else 0
    if fl > 0:
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(RED, 110 * fl, blend=MULT))
    CAP.draw(c, t, shake)
    split_caption(c, t)
    c.restore()


def post_kw(t):
    return dict(shake=0.9 * shake(t), ca=0.6 + 2.0 * shake_env(t, T_GO, 1, 0.02, 0.4))


def sfx_events():
    return [(0.1, "paper_whoosh", 0.5), (0.3, "paper_slap", 0.5), (0.45, "paper_slap", 0.4), (0.6, "paper_slap", 0.4),
            (T_STICK, "stamp", 0.6), (T_BUILD, "strain_creak", 0.7), (T_DATE, "tick", 0.6), (T_TIME, "clock", 0.7),
            (T_GO - 1.4, "rumble", 0.8), (T_GO - 0.02, "crack", 1.0), (T_GO, "quake", 1.0),
            (T_MAP, "paper_whoosh", 0.5), (T_CRACK, "tear", 0.9), (T_LURCH, "low_hit", 0.6)]


MUSIC = dict(beds=[(0.0, T_GO - 0.1, "tension", 0.7), (T_GO + 3.0, DURATION + 0.4, "drone", 0.5)])
