"""Part 2: Carrington's sketch. His telescope throws the Sun onto a card in the dark; he draws the sunspot group;
at 11:18 two beads of white light flare, drift a little (A->C, B->D, as he marked them) and are gone in about five
minutes. The first solar flare ever recorded."""
from common import *  # noqa: F401,F403

PART = "part2"
VO, _end = schedule(PART, first=0.7, gap=0.55)
TM = Timing(PART, VO)
T_BEFORE = TM.word("A1", "day")
T_OBS = TM.word("A1", "observatory")
T_NAME = TM.word("A1", "Richard")
T_DRAW = TM.word("A1", "drawing")
T_AT = TM.word("A2", "At")
T_BLIND = TM.word("A2", "blinding")
T_BURST = TM.word("A2", "burst")
T_FIVE = TM.word("A2", "five")
T_GONE = TM.word("A2", "gone")
T_FIRST = TM.word("A3", "first")
DURATION = _end + 1.0
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"blinding": FLARE, "white": FLARE}),
               anchors={k: (W / 2, 1420) for k in VO})
CX, CY, R = 560, 820, 360
SPOTS = ((640, 760, 52), (700, 800, 34), (590, 800, 26), (740, 750, 20), (560, 760, 16), (660, 840, 14))
BEADS = (((620, 728), (660, 700), 30, 0.35, "A", "C"), ((700, 852), (745, 830), 24, -0.4, "B", "D"))


def _spot_path(x, y, r, k):
    rng = np.random.default_rng(3 + k)
    pen = skia.Path()
    for j in range(40):
        th = j / 40 * 2 * math.pi
        rr = r * (1 + 0.16 * math.sin(3 * th + x) + 0.06 * rng.normal())
        (pen.lineTo if j else pen.moveTo)(x + math.cos(th) * rr, y + math.sin(th) * rr * 0.8)
    pen.close()
    return pen


SPOT_PATHS = [_spot_path(x, y, r, k) for k, (x, y, r) in enumerate(SPOTS)]


def bead_level(t):
    on = hit(t, T_BLIND - 0.1, 0.06, 0.6) * 0.8 + smooth(prog(t, T_BLIND - 0.1, T_BLIND + 0.05))
    return on * (1 - smooth(prog(t, T_GONE - 0.9, T_GONE + 0.2)))


def watch(c, t, a):
    wx, wy, wr = 860, 1225, 108
    rise = (1 - out_expo(prog(t, T_AT - 0.4, T_AT + 0.4))) * 260
    wy += rise
    c.drawCircle(wx, wy - wr - 14, 14, paint(LIME, 220 * a, stroke=1.6))
    c.drawCircle(wx, wy, wr + 8, paint(VOID, 255 * a))
    face = skia.Path()
    face.addCircle(wx, wy, wr)
    tint(c, face, CARD, 60 * a, (3, 3), 2)
    engrave(c, face, LIME, 255 * a, 2.2)
    c.drawCircle(wx, wy, wr - 10, paint(LIME, 120 * a, stroke=1))
    for k in range(60):
        th = k / 60 * 2 * math.pi
        L = 10 if k % 5 == 0 else 4
        c.drawLine(wx + math.sin(th) * (wr - 12), wy - math.cos(th) * (wr - 12), wx + math.sin(th) * (wr - 12 - L),
                   wy - math.cos(th) * (wr - 12 - L), paint(LIME, 220 * a, stroke=1.2))
    for n, th in (("XII", 0), ("III", 90), ("VI", 180), ("IX", 270)):
        r = math.radians(th)
        label(c, n, wx + math.sin(r) * (wr - 40), wy - math.cos(r) * (wr - 40) + 8, 20, "serif_roman", LIME, 230 * a,
              "center")
    # minutes: winds on to 11:18, then on to 11:23 while the beads fade
    m = lerp(11 * 60 - 20, 11 * 60 + 18, out_cubic(prog(t, T_AT - 0.3, T_AT + 0.9)))
    m += 5 * in_out(prog(t, T_FIVE - 0.3, T_GONE + 0.3))
    for ang, L, wd in ((360 * (m / 60) / 12, 52, 4.0), (360 * (m % 60) / 60, 80, 2.4)):
        r = math.radians(ang)
        c.drawLine(wx, wy, wx + math.sin(r) * L, wy - math.cos(r) * L, paint(LIME, 255 * a, stroke=wd))
    c.drawCircle(wx, wy, 6, paint(SUN, 255 * a))
    hh, mm = divmod(int(round(m)), 60)
    label(c, f"{hh}:{mm:02d} A.M.", wx - wr - 22, wy + 70, 24, "mono_bold", SUN, 255 * a, "right", 0.08)


def draw_frame(c, t):
    glass(c, VOID)
    # the telescope slides in and its eyepiece throws the Sun on the card
    c.save()
    c.translate(-260 * (1 - out_expo(prog(t, 0.1, 1.1))), -140 * (1 - out_expo(prog(t, 0.1, 1.1))))
    ex, ey = telescope(c)
    c.restore()
    ba = appear(t, 0.8, 0.5)
    beam = skia.Path()
    beam.moveTo(ex, ey - 6)
    beam.lineTo(CX - R * 0.72, CY - R * 0.7)
    beam.lineTo(CX + R * 0.7, CY + R * 0.72)
    beam.lineTo(ex, ey + 6)
    beam.close()
    c.drawPath(beam, paint(CARD, 26 * ba, sigma=18, blend=ADD))
    rr = R * out_expo(prog(t, 0.9, 1.8))
    if rr > 1:
        disc = skia.Path()
        disc.addCircle(CX, CY, rr)
        c.drawCircle(CX, CY, rr * 1.12, paint(CARD, 60, sigma=40, blend=ADD))
        c.drawPath(disc, paint(mix(CARD, VOID, 0.06)))
        sh = skia.GradientShader.MakeRadial(skia.Point(CX, CY), max(rr, 1), [col(CARD, 0), col((170, 140, 95), 170)],
                                            [0.55, 1.0])
        p = skia.Paint(AntiAlias=True)
        p.setShader(sh)
        c.drawPath(disc, p)
        c.save()
        c.clipPath(disc, doAntiAlias=True)
        wa = appear(t, 1.6, 0.5)
        c.drawPath(disc, paint(SEPIA, 230 * wa, stroke=2.2))
        c.drawLine(CX - R, CY, CX + R, CY, paint(SEPIA, 130 * wa, stroke=1.2))
        c.drawLine(CX, CY - R, CX, CY + R, paint(SEPIA, 130 * wa, stroke=1.2))
        for k in range(-3, 4):
            if k:
                c.drawLine(CX + k * R / 4, CY - 8, CX + k * R / 4, CY + 8, paint(SEPIA, 140 * wa, stroke=1.2))
        # he draws the group, spot by spot (outline traced by the pen, then hatched, then the dark core)
        for k, ((x, y, r), pen) in enumerate(zip(SPOTS, SPOT_PATHS)):
            t0 = T_NAME + k * 0.32
            u = prog(t, t0, t0 + 0.5)
            if u <= 0:
                continue
            c.drawPath(pen, paint(SEPIA, 70 * appear(t, t0 + 0.3, 0.3)))
            if u > 0.5:
                hatch(c, pen, 160 * appear(t, t0 + 0.25, 0.3), 3.2, 35, SEPIA, 0.9)
            meas = skia.PathMeasure(pen, False)
            seg = skia.Path()
            meas.getSegment(0, meas.getLength() * clamp(u * 1.4), seg, True)
            c.drawPath(seg, paint(SEPIA, 230, stroke=1.4))
            c.drawCircle(x + 2, y, r * 0.38 * smooth(prog(t, t0 + 0.3, t0 + 0.6)), paint((50, 32, 20), 255))
        c.restore()
        lv = bead_level(t)
        dr = in_out(prog(t, T_BLIND, T_GONE))
        for (p0, p1, s, ang, l0, l1) in BEADS:
            bx, by = lerp(p0[0], p1[0], dr), lerp(p0[1], p1[1], dr)
            if lv > 0.01:
                flare_bead(c, kidney(bx, by, s * (0.8 + 0.2 * lv), ang), 255 * clamp(lv), 1.6 * lv)
                c.drawCircle(bx, by, s * 2.2, paint(FLARE, 120 * clamp(lv), sigma=s * 1.2, blend=ADD))
                for k in range(6):            # glare spikes: too bright for the eye
                    th = math.radians(k * 60 + 15)
                    L = s * (2.5 + 2.5 * clamp(lv))
                    light(c, polyline([(bx - math.cos(th) * L, by - math.sin(th) * L),
                                       (bx + math.cos(th) * L, by + math.sin(th) * L)]), SUN, 160 * clamp(lv), 1.2, 0.6)
            la = appear(t, T_BLIND + 0.6, 0.4)
            label(c, l0, p0[0] - s - 34, p0[1] - 18, 40, "serif_bold", SEPIA, 255 * la)
            lc = appear(t, T_GONE - 0.3, 0.4)
            label(c, l1, p1[0] + s + 26, p1[1] - 22, 36, "serif_bold", SEPIA, 230 * lc)
            if lc > 0:
                c.drawPath(polyline([(p0[0] + s * 0.6, p0[1] - 4), (p1[0] + s * 0.4, p1[1] - 2)]),
                           dashed(paint(SEPIA, 170 * lc, stroke=1.4), 6, 6))
    tag(c, 70, 1170, "REDHILL, SOUTH OF LONDON", LIME, 255 * appear(t, T_OBS - 0.2), 22)
    tag(c, 70, 1222, "RICHARD CARRINGTON · 1 SEPT 1859", SUN, 255 * appear(t, T_NAME - 0.1), 20)
    wa = appear(t, T_AT - 0.4, 0.3)
    if wa > 0:
        watch(c, t, wa)
    stamp_tab(c, "FIRST SOLAR FLARE EVER RECORDED", 560, 1090, pop(t, T_FIRST - 0.1), SUN, 24, -2)
    slide_label(c, 2, "CARRINGTON'S DRAWING", 70, 150, 255 * appear(t, 0.5))
    CAP.draw(c, t)


def post_kw(t):
    kw = slide_change(t, DURATION)
    kw["flash"] = 0.6 * hit(t, T_BLIND - 0.1, 0.04, 0.3)
    return kw


def sfx_events():
    return [(0.25, "slide_whoosh", 0.6), (0.9, "lens", 0.5), (T_NAME, "pen_scratch", 0.45), (T_NAME + 0.9, "pen_scratch", 0.4),
            (T_AT, "clock", 0.45), (T_BLIND - 0.15, "flare_burst", 1.0), (T_FIVE, "tick_roll", 0.35),
            (T_FIRST - 0.1, "stamp", 0.8), (DURATION - 0.4, "slide_clack", 0.6)]


MUSIC = dict(beds=[(0.0, DURATION + 0.3, "music_box", 0.5), (0.0, DURATION, "projector", 0.35),
                   (T_BLIND - 0.2, DURATION + 0.3, "wonder", 0.45)])
