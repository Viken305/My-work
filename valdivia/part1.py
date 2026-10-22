"""Part 1: the hook. A slow bronze trace -> it wraps into the globe, which rings -> spin to Chile -> title."""
from common import *  # noqa: F401,F403

PART = "part1"
VO, _end = schedule(PART, first=0.9, gap=0.55)
TM = Timing(PART, VO)
T_RING = TM.word("H1", "ring")
T_BELL = TM.word("H1", "bell")
T_MORPH = VO["H2"] - 0.6
T_DAYS = TM.word("H2", "days")
T_REC = TM.word("H3", "recorded")
T_HERE = TM.word("H3", "here")
T_TITLE = _end + 0.35
DURATION = T_TITLE + 5.2
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours())


def _trace_pts(t, x0=80, x1=1000, y=900, amp=60):
    pts = []
    n = 300
    for i in range(n + 1):
        u = i / n
        mins = u * 12 * 60 + t * 40
        e = 0.35 + 0.65 * smooth(prog(t, T_RING - 0.3, T_RING + 0.6))
        v = e * (math.sin(mins / 54 * 2 * math.pi) * 0.75 + math.sin(mins / 35.6 * 2 * math.pi + 1) * 0.3 +
                 math.sin(mins / 20.5 * 2 * math.pi + 2) * 0.15)
        pts.append((u, v))
    return pts


def _strip(c, t, a):
    """The opening: a strain-meter trace drawn by the pen, then wrapped into a circle (the globe's outline)."""
    m = in_out(prog(t, T_MORPH, T_MORPH + 1.9))
    draw_u = out_cubic(prog(t, 0.2, 2.8))
    cx, cy, R = 540, 880, 330
    pts = []
    for u, v in _trace_pts(t):
        lx, ly = 80 + u * 920, 900 - v * 60
        th = -math.pi / 2 + 2 * math.pi * u
        r = R + v * 10 * (1 - m * 0.6)
        gx, gy = cx + math.cos(th) * r, cy + math.sin(th) * r
        pts.append((lerp(lx, gx, m), lerp(ly, gy, m)))
    if m < 1:
        c.drawLine(80, 900, 1000, 900, paint(SEPIA, 150 * a * (1 - m), stroke=1.0))
        for h in range(0, 13, 2):
            x = 80 + h / 12 * 920
            label(c, f"{h} H", x, 960, 16, "mono", SEPIA, 255 * a * (1 - m) * appear(t, 0.6), "center")
    p, tip = polyline(pts, draw_u)
    glow(c, p, BRONZE, 255 * a, 2.6, 0.6)
    if tip and draw_u < 1:
        pen_dot(c, *tip, INK, 255 * a)
    return m


def _globe_scene(c, t):
    m = _strip(c, t, 1.0)
    # the globe fills in behind its own outline
    g = smooth(prog(t, T_MORPH + 1.2, T_MORPH + 2.2))
    spin = in_out(prog(t, VO["H3"] + 0.3, T_HERE + 0.1))
    lon = lerp(-38 + 10 * prog(t, T_MORPH, VO["H3"]), -74, spin)
    lat = lerp(2, -22, spin)
    R = lerp(330, 400, in_out(prog(t, VO["H3"] + 0.3, T_HERE + 0.4)))
    cy = 880
    ring_amt = g * (1 - 0.6 * spin)
    wob = math.sin(2 * math.pi * (t - T_MORPH) / 2.6)
    if g > 0:
        dial_rings(c, 540, cy, R, 0.8 * ring_amt, (t * 0.25) % 3)
        for eps, a0, dash in ((0.06 * wob, 230, False), (-0.06 * wob, 140, True)):
            pp = paint(BRONZE, a0 * ring_amt, stroke=2.4)
            if dash:
                dashed(pp, 14, 10)
            q = mode_outline(540, cy, R * 1.012, eps, breathe=0.012 * math.sin(2 * math.pi * t / 1.1))
            c.drawPath(q, paint(BRONZE, a0 * 0.25 * ring_amt, sigma=10, stroke=10, blend=MULT))
            c.drawPath(q, pp)
        globe(c, Ortho(lon, lat, R, 540, cy), g, g, outline=True)
    # FIG tab + the strain-meter card
    fig(c, 1, "STRAIN METER, CALIFORNIA, MAY 1960", 70, 268, 255 * appear(t, 0.4) * (1 - g), size=20)
    fig(c, 1, "THE EARTH, MAY 1960", 70, 268, 255 * g, size=20)
    ca = appear(t, T_MORPH + 1.6, 0.5)
    if ca > 0:
        c.save()
        c.translate(0, (1 - ca) * -30)
        card(c, 70, 320, 940, 150, 255 * ca)
        label(c, "STRAIN METER · CALIFORNIA", 96, 356, 18, "mono_bold", INK, 230 * ca, tracking=0.12)
        label(c, "ONE SWING ≈ 54 MIN", 984, 356, 18, "mono", BRONZE, 255 * ca, "right", 0.12)
        pts = [(96 + u * 888, 420 - v * 30) for u, v in _trace_pts(t + 3)]
        glow(c, polyline(pts)[0], BRONZE, 255 * ca, 2.0, 0.5)
        c.restore()
    # "for days": a day counter that ticks
    da = appear(t, T_DAYS - 0.1) * (1 - appear(t, VO["H3"] + 0.4))
    if da > 0:
        day = 1 + min(2, int(max(0.0, t - T_DAYS) / 0.35))
        tab(c, 760, 1214, 220, 44, 255 * da)
        label(c, f"DAY {day} OF 5", 870, 1245, 24, "mono_bold", BRONZE, 255 * da, "center", 0.1)
    # "the biggest earthquake ever recorded": a stamp
    sa = pop(t, T_REC, 0.35)
    if sa > 0 and t < T_TITLE:
        c.save()
        c.translate(540, 1300)
        c.rotate(-3)
        c.scale(1 + 0.3 * (1 - clamp(sa)), 1 + 0.3 * (1 - clamp(sa)))
        a = clamp(sa)
        c.drawRect(skia.Rect.MakeXYWH(-300, -44, 600, 76), paint(BONE, 240 * a))
        c.drawRect(skia.Rect.MakeXYWH(-300, -44, 600, 76), paint(RED, 255 * a, stroke=3))
        label(c, "M 9.5 · LARGEST EVER RECORDED", 0, 6, 28, "mono_bold", RED, 255 * a, "center", 0.08)
        c.restore()
    # "it started here": the epicentre
    if t >= T_HERE - 0.05:
        proj = Ortho(lon, lat, R, 540, cy)
        ex, ey, _ = proj(*EPI)
        k = t - T_HERE
        for j in range(3):
            q = skia.Path()
            q.addCircle(ex, ey, 18 + ((k * 40 + j * 30) % 90))
            glow(c, q, RED, 220 * (1 - ((k * 40 + j * 30) % 90) / 90), 2.0, 0.6)
        c.save()
        c.translate(ex, ey)
        s = pop(t, T_HERE, 0.4)
        c.scale(s, s)
        star(c, 0, 0, 18)
        c.restore()
        la = appear(t, T_HERE + 0.2)
        tab(c, ex - 300, ey - 34, 272, 82, 255 * la)
        pin(c, ex, ey, "VALDIVIA, CHILE", "22 MAY 1960 · 15:11", la * 255, side=-1, size=24, sub_rgb=INK)
    return m


def _title(c, t):
    u = t - T_TITLE
    y = 1150
    c.drawLine(-20, y, W + 20, y, paint(SEPIA, 180 * appear(u, 0.3), stroke=1.0))
    pts = []
    for i in range(1601):
        uu = i / 1600
        pts.append((-20 + uu * (W + 40), y - trace(uu, 3, 0.5, 0.025, 0.25, 1.0, 0.5) * 130))
    p, tip = polyline(pts, out_cubic(prog(u, 0.2, 2.0)))
    glow(c, p, RED, 255, 2.0, 0.7)
    if tip and u < 2.0:
        pen_dot(c, *tip)
    a1 = appear(u, 0.35, 0.5)
    label(c, "THE DAY THE EARTH", W / 2, 560 + (1 - a1) * 20, 84, "serif_roman", INK, 255 * a1, "center", 0.02)
    s = pop(u, 0.95, 0.5)
    if s > 0:
        w = width("RANG", "serif_bold", 210)
        c.save()
        c.translate(W / 2, 700)
        sc = 1.25 - 0.25 * s
        c.scale(sc, sc)
        c.translate(-W / 2, -700)
        ring_word(c, "RANG", W / 2 - w / 2, 770, 210, BRONZE, clamp(s * 1.5), strike=u - 0.95)
        c.restore()
    a3 = appear(u, 1.5, 0.5)
    label(c, "like a bell", W / 2, 870, 70, "serif", INK, 255 * a3, "center")
    a4 = appear(u, 2.1, 0.5)
    label(c, "VALDIVIA, CHILE  ·  22 MAY 1960", W / 2, 1420, 24, "mono_bold", INK, 255 * a4, "center", 0.16)


def draw_frame(c, t):
    paper(c)
    out = in_cubic(prog(t, T_TITLE - 0.1, T_TITLE + 0.55))
    if out < 1:
        c.save()
        c.translate(0, -out * H * 0.6)
        _globe_scene(c, t)
        CAP.draw(c, t)
        c.restore()
    if t >= T_TITLE:
        c.save()
        c.translate(0, (1 - out_expo(prog(t, T_TITLE + 0.05, T_TITLE + 0.8))) * H * 0.6 + drum_scroll(t, DURATION, 0, 0.55))
        _title(c, t)
        c.restore()


def post_kw(t):
    return dict(shake=0.25 * shake_env(t, T_HERE, 1, 0.05, 0.4) + 0.2 * shake_env(t, T_TITLE + 0.95, 1, 0.03, 0.3))


def sfx_events():
    ev = [(0.15, "pen_scratch", 0.5), (1.0, "pen_scratch", 0.4), (1.9, "pen_scratch", 0.35),
          (T_RING - 0.05, "bell", 0.9), (T_MORPH + 0.2, "paper_whoosh", 0.5), (T_MORPH + 1.7, "bell", 0.55),
          (T_DAYS, "tick", 0.6), (T_DAYS + 0.35, "tick", 0.6), (T_DAYS + 0.7, "tick", 0.6),
          (VO["H3"] + 0.3, "whoosh", 0.45), (T_REC, "stamp", 0.8), (T_HERE - 0.02, "low_hit", 0.8),
          (T_TITLE - 0.1, "paper_whoosh", 0.6), (T_TITLE + 0.3, "pen_scratch", 0.5), (T_TITLE + 1.0, "pen_scratch", 0.45),
          (T_TITLE + 0.93, "title_hit", 0.8), (T_TITLE + 0.95, "bell", 1.0)]
    return ev


MUSIC = dict(beds=[(0.0, T_TITLE + 0.2, "drone", 0.7), (T_TITLE, DURATION + 0.4, "piano", 0.7)])
