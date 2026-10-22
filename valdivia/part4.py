"""Part 4: the ocean. A side view of the coast: the sea pulls back and a wave over 10 m rolls in. Then the Pacific
chart: hour-by-hour fronts, the caption rides the front, Hawaii at 15 h, Japan almost a day later, 17,000 km."""
from common import *  # noqa: F401,F403
from frames import _gc_point

PART = "part4"
VO, _end = schedule(PART, first=0.6, gap=0.6, extra={"C2": 0.4, "C3": 0.3})
TM = Timing(PART, VO)
T_MOVED = TM.word("C1", "moved")
T_WAVES = TM.word("C1", "waves")
T_10 = TM.word("C1", "ten")
T_DIED = TM.word("C1", "somewhere")
T_CHART = VO["C2"] - 0.5
T_ACROSS = TM.word("C2", "across")
T_PAC_END = TM.word("C2", "pacific", end=True)
T_JET = TM.word("C2", "almost")
T_15 = TM.word("C3", "fifteen")
T_HAW = TM.word("C3", "hawaii")
T_61 = TM.word("C3", "sixty")
T_DAY = TM.word("C3", "almost")
T_JAP = TM.word("C3", "japan")
T_17 = TM.word("C3", "seventeen")
T_140 = TM.word("C3", "hundred")
DURATION = _end + 1.1
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"died": INK, "people": INK}),
               hide={"C2": [(T_ACROSS - 0.05, T_PAC_END + 0.6)]})
HILO_D, JAPAN_D = gc_km(EPI, HILO), gc_km(EPI, JAPAN)
KMH = HILO_D / 15


def hours(t):
    t = round(t * FPS) / FPS
    if t < T_ACROSS + 1.4:
        return 9.5 * in_out(prog(t, T_CHART + 0.5, T_ACROSS + 1.4))
    if t < T_HAW:
        return lerp(9.5, 15, in_out(prog(t, T_ACROSS + 1.4, T_HAW)))
    return lerp(15, 22, in_out(prog(t, T_DAY, T_JAP)))


def dist(h):
    return (h * KMH if h <= 15 else HILO_D + (h - 15) / 7 * (JAPAN_D - HILO_D)) / 6371


# ---------------------------------------------------------------- the coast, side view
def coast(c, t):
    sea = 1000
    fig(c, 5, "THE COAST OF CHILE, 22 MAY 1960", 70, 268, size=20)
    hills = skia.Path()
    hills.moveTo(640, sea + 40)
    for x, y in ((680, 960), (760, 930), (860, 880), (940, 820), (1010, 760), (1100, 730)):
        hills.lineTo(x, y)
    hills.lineTo(1100, 1300)
    hills.lineTo(640, 1300)
    hills.close()
    back = skia.Path()
    back.moveTo(560, sea)
    for x, y in ((700, 900), (820, 780), (930, 700), (1100, 640)):
        back.lineTo(x, y)
    back.lineTo(1100, sea)
    back.close()
    cutout(c, back, mix(SHADE, SEPIA, 0.4), lift=6, edge_a=120)
    # houses on the shore
    for i, (x, y) in enumerate(((700, 958), (745, 940), (800, 918), (850, 896), (905, 862))):
        hw = 30
        hp = skia.Path()
        hp.addRect(skia.Rect.MakeXYWH(x, y - 30, hw, 30))
        hp.moveTo(x - 4, y - 30)
        hp.lineTo(x + hw / 2, y - 48)
        hp.lineTo(x + hw + 4, y - 30)
        hp.close()
        c.drawPath(hp, paint(INK, 235))
    cutout(c, hills, WHITE, lift=10)
    hatch(c, hills, 40, 9, 35, INK, 0.9)
    # the sea: pulls back, then the wave
    draw = smooth(prog(t, T_MOVED - 0.3, T_WAVES)) * (1 - smooth(prog(t, T_WAVES, T_WAVES + 0.6)))
    wx = lerp(-260, 700, in_out(prog(t, T_WAVES - 0.2, T_WAVES + 2.6)))
    A = 150 * smooth(prog(t, T_WAVES - 0.4, T_WAVES + 0.8)) * (1 - 0.7 * smooth(prog(t, T_DIED, T_DIED + 2.5)))
    level = sea + 40 * draw

    def surf(x):
        d = (x - wx) / 150
        lean = 1.0 if d < 0 else 0.45
        return level - A * math.exp(-(d * lean) ** 2) + math.sin(x * 0.03 + t * 2) * 3

    sp = skia.Path()
    sp.moveTo(-20, H)
    for x in range(-20, 760, 6):
        sp.lineTo(x, min(surf(x), sea + 300))
    sp.lineTo(760, H)
    sp.close()
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(-20, 0, 760, 1300))
    c.drawPath(sp, paint(mix(BONE, TEAL, 0.2)))
    c.save()
    c.clipPath(sp, doAntiAlias=True)
    for y in range(600, 1300, 8):
        c.drawLine(-20, y, 760, y, paint(TEAL, 110, stroke=1.0))
    c.restore()
    top = skia.Path()
    for i, x in enumerate(range(-20, 760, 6)):
        (top.lineTo if i else top.moveTo)(x, surf(x))
    ink(c, top, TEAL, 255, 2.6)
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(-20, 1300, W + 20, 1320), paint(SHADOW, 50, sigma=8))
    # height scale: 10 m against the houses (one house ~ 5 m)
    sa = appear(t, T_10 - 0.2)
    if sa > 0:
        dim_line(c, 120, sea, 120, sea - 120, "10 M", 255 * sa, TEAL, 22)
        c.drawLine(100, sea - 120, 700, sea - 120, dashed(paint(TEAL, 200 * sa, stroke=1.6), 12, 10))
        label(c, "WAVES OF MORE THAN 10 M", 160, sea - 140, 20, "mono_bold", TEAL, 255 * sa, tracking=0.12)
    da = appear(t, T_DIED + 0.3, 0.6)
    if da > 0:
        tab(c, 300, 560, 480, 110, 255 * da)
        label(c, "DEAD IN CHILE", 540, 598, 18, "mono", SEPIA, 255 * da, "center", 0.2)
        label(c, "1,000 – 6,000", 540, 650, 50, "mono_bold", INK, 255 * da, "center")
        label(c, "ESTIMATES VARY", 540, 690, 16, "mono", SEPIA, 255 * da, "center", 0.2)


# ---------------------------------------------------------------- the Pacific
def pacific(c, t):
    chart = Chart(118, 296, -60, 62, 0, 330, W)
    h = hours(t)
    c.save()
    c.clipRect(chart.rect())
    c.drawRect(chart.rect(), paint(mix(BONE, TEAL, 0.07)))
    for lon in range(120, 300, 20):
        x, _, _ = chart(lon, 0)
        c.drawLine(x, chart.y, x, chart.y + chart.h, paint(SEPIA, 90, stroke=1.0))
    for lat in range(-60, 61, 20):
        _, y, _ = chart(180, lat)
        c.drawLine(0, y, W, y, paint(SEPIA, 90, stroke=1.0))
    for hh in (3, 6, 10, 15, 19, 22):
        if hh < h - 0.3:
            p, _ = small_circle(chart, *EPI, dist(hh), 721)
            c.drawPath(p, paint(TEAL, 120, stroke=1.5))
    if h > 0.05:
        p, front = small_circle(chart, *EPI, dist(h), 721)
        c.drawPath(p, paint(TEAL, 110, sigma=12, stroke=18, blend=MULT))
        c.drawPath(p, paint(TEAL, 255, stroke=4.0))
    engraved_land(c, land_path(chart, "world"), step=6, water_lines=(6, 13), key="pacific")
    c.restore()
    c.drawRect(chart.rect(), paint(INK, 200, stroke=1.6))
    for hh in (3, 6, 10):
        if hh < h - 0.3:
            x, y, _ = chart(*destination(*EPI, math.radians(262), hh * KMH / 6371))
            tab(c, x - 26, y - 14, 52, 26)
            label(c, f"{hh} H", x, y + 6, 16, "mono_bold", TEAL, 255, "center")
    ex, ey, _ = chart(*EPI)
    star(c, ex, ey, 15)
    label(c, "CHILE", ex - 20, ey + 46, 22, "semibold", INK, 255, "right", 0.1)
    # the caption rides the front
    if T_ACROSS - 0.05 <= t <= T_PAC_END + 0.6 and h > 2:
        _, pts = small_circle(chart, *EPI, dist(h) + 0.045, 1441)
        seg = sorted([(x, y) for x, y in pts if 40 < x < 900 and chart.y + 60 < y < chart.y + chart.h - 30])
        if len(seg) > 10:
            text = "across the entire Pacific"
            n = max(1, int(len(text) * clamp(prog(t, T_ACROSS - 0.05, T_PAC_END - 0.1))))
            fa = 1 - smooth(prog(t, T_PAC_END + 0.3, T_PAC_END + 0.6))
            caption_on_path(c, text[:n], seg, 30, 46, "serif_bold", TEAL, 255 * fa)
    # Hawaii, Japan, the great circle
    if h >= 14.9:
        s = pop(t, T_HAW - 0.1, 0.4)
        hx, hy, _ = chart(*HILO)
        tab(c, hx + 16, hy - 22, 254, 76, 255 * clamp(s))
        pin(c, hx, hy, "HAWAII", "15 HOURS · 61 DIED" if t > T_61 else "15 HOURS", 255 * clamp(s), side=1, size=24, sub_rgb=INK)
    if t > T_17 - 0.2:
        u = out_cubic(prog(t, T_17 - 0.2, T_17 + 1.2))
        gp = []
        for i in range(121):
            x, y, _ = chart(*_gc_point(EPI, JAPAN, i / 120))
            gp.append((x, y))
        p, tip = polyline(gp, u)
        c.drawPath(p, dashed(paint(INK, 200, stroke=1.8), 10, 9))
        mx, my, _ = chart(*_gc_point(EPI, JAPAN, 0.3))
        la = appear(t, T_17 + 0.6)
        tab(c, mx - 70, my - 40, 140, 30, 255 * la)
        label(c, "17,000 KM", mx, my - 18, 20, "mono_bold", INK, 255 * la, "center", 0.08)
    if h >= 21.9 or t > T_JAP:
        s = pop(t, T_JAP - 0.1, 0.4)
        jx, jy, _ = chart(*JAPAN)
        tab(c, jx + 16, jy - 22, 254, 76, 255 * clamp(s))
        pin(c, jx, jy, "JAPAN", "~1 DAY · ~140 DIED" if t > T_140 else "~1 DAY", 255 * clamp(s), side=1, size=24, sub_rgb=INK)
    # instrument: hours since the quake
    card(c, 640, 1150, 380, 110)
    label(c, "HOURS AFTER THE QUAKE", 662, 1188, 17, "mono", SEPIA, 255, tracking=0.14)
    label(c, f"{h:4.1f} H", 998, 1244, 52, "mono_bold", TEAL, 255, "right")
    ja = appear(t, T_JET - 0.1) * (1 - appear(t, VO["C3"] - 0.3))
    if ja > 0:
        card(c, 60, 1150, 540, 110, 255 * ja)
        label(c, "SPEED IN DEEP WATER", 82, 1188, 17, "mono", SEPIA, 255 * ja, tracking=0.14)
        label(c, "~750 KM/H", 82, 1244, 48, "mono_bold", TEAL, 255 * ja)
        label(c, "a jet: ~900", 580, 1240, 26, "serif", INK, 255 * ja, "right")
    fig(c, 5, "THE TSUNAMI, 22–23 MAY 1960", 70, 268, size=20)


def draw_frame(c, t):
    paper(c)
    c.save()
    c.translate(0, drum_scroll(t, DURATION, 0.6, 0.6))
    out = in_cubic(prog(t, T_CHART, T_CHART + 0.6))
    if out < 1:
        c.save()
        c.translate(0, -out * H * 0.7)
        coast(c, t)
        c.restore()
    if t > T_CHART:
        c.save()
        c.translate(0, (1 - out_expo(prog(t, T_CHART + 0.1, T_CHART + 0.9))) * H * 0.6)
        pacific(c, t)
        c.restore()
    CAP.draw(c, t)
    c.restore()


def post_kw(t):
    return dict(shake=0.12 * smooth(prog(t, T_WAVES, T_WAVES + 1)) * (1 - smooth(prog(t, T_WAVES + 2, T_WAVES + 3))))


def sfx_events():
    return [(0.0, "paper_whoosh", 0.5), (T_MOVED - 0.4, "suck", 0.6), (T_WAVES - 0.4, "wave_roar", 1.0),
            (T_DIED, "silence_cue", 0.0), (T_CHART, "paper_whoosh", 0.6), (T_CHART + 0.4, "ocean", 0.5),
            (T_ACROSS, "whoosh", 0.4), (T_HAW - 0.1, "pop", 0.7), (T_17 - 0.2, "pen_scratch", 0.5),
            (T_17 + 0.5, "pen_scratch", 0.4), (T_JAP - 0.1, "pop", 0.7)]


MUSIC = dict(beds=[(0.0, T_DIED, "drone", 0.5), (T_DIED + 2.0, DURATION + 0.4, "aftermath", 0.8)])
