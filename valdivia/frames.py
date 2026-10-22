"""Style frames for approval.

  python3 frames.py            -> out/style/frame_1_bell.png ... frame_7_title.png + out/style/style_frames.png
  python3 frames.py fault      -> only the frames whose name contains "fault"
"""
import math, os, sys

import numpy as np
import skia
from PIL import Image

from ink import *  # noqa: F401,F403
from ink import _word_layout

OUT = os.path.join(HERE, "out", "style")
EPI = (-73.41, -38.14)          # 1960 main shock epicentre (USGS)
VALDIVIA = (-73.24, -39.81)
HILO = (-155.09, 19.72)
JAPAN = (141.5, 38.9)           # Sanriku coast
RUPTURE = [(-74.0, -37.0), (-74.3, -38.5), (-74.6, -40.0), (-74.9, -41.5), (-75.2, -43.0), (-75.6, -44.5), (-75.9, -46.0)]
SHADOW = (40, 30, 20)


def tab(c, x, y, w, h, a=255):
    """A small paper tab behind a label so it reads over linework."""
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 4, 4), paint(BONE, a * 0.92))


def words_ink(c, words, x, y, size, kind="bold", rgb=INK):
    f = font(kind, size)
    for wd in words:
        for ch in wd:
            c.drawString(ch, x + 2, y + 5, f, paint(SHADOW, 60, sigma=6))
            c.drawString(ch, x, y, f, paint(rgb))
            x += f.measureText(ch)
        x += size * 0.27
    return x


def ringing_word(c, s, x, y, size, rgb=BRONZE, a=255, echoes=4, kind="serif_bold"):
    """A word that rings: the glyphs plus outline copies that grow and fade around their centre, like a struck bell."""
    f = font(kind, size)
    w = width(s, kind, size)
    cx, cy = x + w / 2, y - size * 0.34
    for k in range(echoes, 0, -1):
        sc = 1 + 0.05 * k
        c.save()
        c.translate(cx, cy)
        c.scale(sc, sc * (1 + 0.02 * (-1) ** k))
        c.translate(-cx, -cy)
        p = paint(rgb, a * (0.55 / k), stroke=1.6 - 0.2 * k)
        xx = x
        for ch in s:
            c.drawString(ch, xx, y, f, p)
            xx += f.measureText(ch)
        c.restore()
    xx = x
    for ch in s:
        c.drawString(ch, xx + 2, y + 5, f, paint(SHADOW, a * 0.25, sigma=6))
        c.drawString(ch, xx, y, f, paint(rgb, a))
        xx += f.measureText(ch)
    return w


# ---------------------------------------------------------------- FIG 1: the Earth rings like a bell (hook)
def bell_frame(c, t):
    paper(c)
    cx, cy, R = 540, 915, 350
    proj = Ortho(-74, -20, R, cx, cy, 0)
    # the bell's voice: the slowest "football" mode (hugely exaggerated) in both phases, and fading dial rings
    tilt = math.radians(-22)
    for eps, a0, dash in ((0.07, 230, False), (-0.07, 150, True)):
        p = skia.Path()
        for k in range(361):
            th = math.radians(k)
            x = math.cos(th - tilt)
            r = R * (1.012 + eps * (3 * x * x - 1) / 2)
            (p.lineTo if k else p.moveTo)(cx + math.cos(th) * r, cy + math.sin(th) * r)
        p.close()
        pp = paint(BRONZE, a0, stroke=2.4)
        if dash:
            dashed(pp, 14, 10)
        c.drawPath(p, paint(BRONZE, a0 * 0.25, sigma=10, stroke=10, blend=MULT))
        c.drawPath(p, pp)
    for k, rr in enumerate((1.2, 1.36, 1.54)):
        q = skia.Path()
        q.addCircle(cx, cy, R * rr)
        c.drawPath(q, paint(BRONZE, 120 - k * 35, stroke=1.6 - k * 0.3))
        for j in range(72):   # instrument-dial ticks on each echo
            ang = math.radians(j * 5)
            l = 10 if j % 6 == 0 else 4
            r0 = R * rr
            c.drawLine(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0, cx + math.cos(ang) * (r0 + l),
                       cy + math.sin(ang) * (r0 + l), paint(BRONZE, 90 - k * 25, stroke=1.0))
    # the globe, lit from the top left
    disc = skia.Path()
    disc.addCircle(cx, cy, R)
    c.drawCircle(cx + 10, cy + 26, R, paint(SHADOW, 60, sigma=30))
    sh = skia.GradientShader.MakeRadial((cx - R * 0.4, cy - R * 0.45), R * 1.7, [col(WHITE), col(BONE), col(SHADE)],
                                        [0, 0.55, 1])
    c.drawCircle(cx, cy, R, skia.Paint(AntiAlias=True, Shader=sh))
    c.save()
    c.clipPath(disc, doAntiAlias=True)
    graticule(c, proj, 0.9, 15)
    engraved_land(c, globe_land_path(proj), step=5.5, water_lines=(5, 11), key="bell")
    c.restore()
    ink(c, disc, INK, 240, 2.2)
    ex, ey, _ = proj(*EPI)
    for k, r in enumerate((26, 48, 74)):
        q = skia.Path()
        q.addCircle(ex, ey, r)
        glow(c, q, RED, 220 - k * 60, 2.2 - k * 0.5, 0.7)
    star(c, ex, ey, 17)
    tab(c, ex - 300, ey - 34, 272, 82)
    pin(c, ex, ey, "VALDIVIA, CHILE", "22 MAY 1960 · 15:11", side=-1, size=24, sub_rgb=INK)
    # the record: a strain meter in California swinging slowly, hour after hour
    card(c, 70, 330, 940, 190)
    label(c, "STRAIN METER · CALIFORNIA", 96, 368, 19, "mono_bold", INK, 230, tracking=0.12)
    label(c, "ONE SWING ≈ 54 MIN", 984, 368, 19, "mono", BRONZE, 255, "right", 0.12)
    p = skia.Path()
    for i in range(801):
        u = i / 800
        mins = u * 12 * 60
        env = math.exp(-mins / 2400)
        v = env * (math.sin(mins / 54 * 2 * math.pi) * 0.75 + math.sin(mins / 35.6 * 2 * math.pi + 1) * 0.3 +
                   math.sin(mins / 20.5 * 2 * math.pi + 2) * 0.15)
        (p.lineTo if i else p.moveTo)(96 + u * 888, 448 - v * 40)
    c.drawLine(96, 448, 984, 448, paint(SEPIA, 160, stroke=1.0))
    glow(c, p, BRONZE, 255, 2.4, 0.6)
    for h in range(0, 13, 2):
        x = 96 + h / 12 * 888
        c.drawLine(x, 494, x, 502, paint(INK, 200, stroke=1.2))
        label(c, f"{h} H", x, 490, 15, "mono", SEPIA, 255, "center")
    fig(c, 1, "THE EARTH, MAY 1960", 70, 268)
    # caption: the emphasis word rings with the planet
    size, y = 80, 1415
    w1 = sum(width(wd, "bold", size) for wd in ("the", "whole", "Earth")) + 3 * size * 0.27
    w2 = width("rang", "serif_bold", size * 1.18)
    x = W / 2 - (w1 + w2) / 2
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 40, y - size, w1 + w2 + 80, size * 1.5), 30, 30),
                paint(BONE, 200, sigma=22))
    xx = words_ink(c, ["the", "whole", "Earth"], x, y, size)
    ringing_word(c, "rang", xx, y, size * 1.18)


# ---------------------------------------------------------------- FIG 2: the plates, the stuck zone, the crack
def fault_frame(c, t):
    paper(c)
    sea = 760
    # section through the subduction zone, built as stacked cut paper
    mantle = skia.Path()
    mantle.addRect(skia.Rect.MakeLTRB(-20, 820, W + 20, 1270))
    cutout(c, mantle, mix(SHADE, SEPIA, 0.25), lift=10, edge_a=0)
    stipple(c, mantle, 2600, 70, 3)
    c.drawLine(-20, 1270, W + 20, 1270, paint(INK, 220, stroke=1.6))
    label(c, "MANTLE", 70, 1240, 20, "mono", INK, 170, tracking=0.2)
    ocean = skia.Path()
    ocean.moveTo(-20, sea)
    ocean.lineTo(600, sea)
    ocean.lineTo(530, 800)
    ocean.lineTo(440, 905)
    ocean.lineTo(-20, 868)
    ocean.close()
    c.drawPath(ocean, paint(mix(BONE, TEAL, 0.16)))
    c.save()
    c.clipPath(ocean, doAntiAlias=True)
    for y in range(sea + 8, 920, 8):
        c.drawLine(-20, y, 620, y, paint(TEAL, 110, stroke=1.0))
    c.restore()
    c.drawLine(-20, sea, 600, sea, paint(TEAL, 255, stroke=2.4))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(-20, 0, W + 20, 1270))
    nazca = skia.Path()
    nazca.moveTo(-20, 868)
    nazca.lineTo(440, 905)
    nazca.cubicTo(640, 960, 860, 1080, 1100, 1250)
    nazca.lineTo(1100, 1380)
    nazca.cubicTo(860, 1200, 620, 1080, 400, 1020)
    nazca.lineTo(-20, 985)
    nazca.close()
    cutout(c, nazca, mix(SHADE, INK, 0.12), lift=12)
    hatch(c, nazca, 70, 6, -20, INK, 1.0)
    sa = skia.Path()
    sa.moveTo(440, 905)
    sa.lineTo(530, 800)
    sa.lineTo(600, sea)
    for x, y in ((650, 748), (700, 740), (740, 716), (790, 690), (830, 640), (855, 610), (880, 562), (905, 610),
                 (940, 640), (990, 618), (1030, 650), (1100, 660)):
        sa.lineTo(x, y)
    sa.lineTo(1100, 1250)
    sa.cubicTo(860, 1080, 640, 960, 440, 905)
    sa.close()
    cutout(c, sa, WHITE, lift=16)
    hatch(c, sa, 45, 9, 35, INK, 0.9)
    c.restore()
    # magma rising from the sinking plate to the Andes volcano
    mg = skia.Path()
    mg.moveTo(915, 1140)
    mg.cubicTo(935, 1000, 862, 820, 880, 566)
    c.drawPath(mg, paint(RED, 70, sigma=12, stroke=18, blend=MULT))
    c.drawPath(mg, paint(RED, 230, stroke=3.2))
    c.drawCircle(915, 1140, 16, paint(RED, 120, sigma=8, blend=MULT))
    # the locked zone: stuck for centuries, then the rupture
    lock = skia.Path()
    lock.moveTo(450, 908)
    lock.cubicTo(560, 935, 680, 985, 790, 1050)
    glow(c, lock, RED, 255, 5.0, 1.2)
    for k in range(9):   # strain: little ticks across the locked interface
        u = 0.1 + k * 0.1
        x, y = 450 + u * 340, 908 + u * 142 - 10 * math.sin(u * 3)
        c.drawLine(x - 10, y - 24, x + 10, y + 24, paint(RED, 200, stroke=2))
    for (x, y) in ((300, 885), (600, 1065)):   # plate motion arrows
        ar = skia.Path()
        ar.moveTo(x, y)
        ar.lineTo(x + 90, y + 22)
        ink(c, ar, INK, 255, 3.2)
        hd = skia.Path()
        hd.moveTo(x + 92, y + 23)
        hd.lineTo(x + 70, y + 8)
        hd.lineTo(x + 66, y + 30)
        hd.close()
        c.drawPath(hd, paint(INK))
    label(c, "PACIFIC OCEAN", 70, 812, 22, "mono_bold", TEAL, 255, tracking=0.16)
    label(c, "~7 CM A YEAR", 300, 862, 18, "mono", INK, 230, tracking=0.12)
    label(c, "NAZCA PLATE", 90, 950, 24, "mono_bold", INK, 255, tracking=0.16)
    label(c, "SOUTH AMERICAN PLATE", 1040, 880, 24, "mono_bold", INK, 255, "right", 0.16)
    label(c, "ANDES", 880, 530, 20, "mono", INK, 220, "center", 0.2)
    dim_line(c, 470, 960, 760, 1110, "STUCK", 255, RED, 20, tick=8)
    # inset: where the crack ran
    cx0, cy0, cw, chh = 612, 236, 404, 270
    card(c, cx0, cy0, cw, chh)
    chart = Chart(-84, -60, -48.5, -32.5, cx0 + 4, cy0 + 4, cw - 8)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(cx0 + 2, cy0 + 2, cw - 4, chh - 4))
    engraved_land(c, land_path(chart, "world"), step=5, water_lines=(5, 11), key="inset")
    rp = skia.Path()
    for i, (lon, lat) in enumerate(RUPTURE):
        x, y, _ = chart(lon, lat)
        (rp.lineTo if i else rp.moveTo)(x, y)
    glow(c, rp, RED, 255, 5, 1.0)
    vx, vy, _ = chart(*VALDIVIA)
    c.restore()
    (ax, ay, _), (bx, by, _) = chart(*RUPTURE[0]), chart(*RUPTURE[-1])
    c.drawLine(ax - 22, ay, bx - 22, by, paint(RED, 220, stroke=1.4))
    for xx, yy in ((ax - 22, ay), (bx - 22, by)):
        c.drawLine(xx - 8, yy, xx + 8, yy, paint(RED, 220, stroke=1.4))
    label(c, "≈1,000 KM", min(ax, bx) - 36, (ay + by) / 2 + 8, 22, "mono_bold", RED, 255, "right", 0.08)
    pin(c, vx, vy, "VALDIVIA", None, side=1, size=20)
    label(c, "CHILE", 990, 300, 18, "mono_bold", INK, 200, "right", 0.2)
    fig(c, 2, "CHILE, IN SECTION", 70, 268, size=20)
    # caption: the crack runs through the words and the top half slips along it
    caption_split(c, ["it", "let", "go"], 1430, 120, {2: RED}, (230, 1300), (860, 1555), slip=26)


# ---------------------------------------------------------------- FIG 3: the drum (helicorder) goes wild
def _row(x0, y, w, amp, seed, u0=0.0, u1=1.0, n=1400):
    rng = np.random.default_rng(seed)
    ph = rng.random(4) * 6.28
    p = skia.Path()
    first = True
    for i in range(n + 1):
        u = i / n
        if u < u0 or u > u1:
            continue
        v = (math.sin(u * 2 * math.pi * 23 + ph[0]) * 0.55 + math.sin(u * 2 * math.pi * 57 + ph[1]) * 0.3 +
             math.sin(u * 2 * math.pi * 131 + ph[2]) * 0.15) * (0.75 + 0.25 * math.sin(u * 2 * math.pi * 3 + ph[3]))
        (p.moveTo if first else p.lineTo)(x0 + u * w, y - v * amp(u))
        first = False
    return p


def drum_frame(c, t):
    paper(c, grid=False)
    top, bot = 450, 1250
    drum = skia.Rect.MakeLTRB(0, top - 40, W, bot + 40)
    sh = skia.GradientShader.MakeLinear([(0, top - 40), (0, bot + 40)],
                                        [col(SHADE), col(WHITE), col(BONE), col(SEPIA)], [0, 0.3, 0.72, 1])
    c.drawRect(drum, skia.Paint(Shader=sh))
    c.drawRect(skia.Rect.MakeLTRB(0, top - 60, W, top - 40), paint(SHADOW, 60, sigma=10))
    c.drawRect(skia.Rect.MakeLTRB(0, bot + 40, W, bot + 70), paint(SHADOW, 90, sigma=12))
    for y in range(top - 30, bot + 40, 12):
        c.drawLine(0, y, W, y, paint(SEPIA, 40, stroke=1.0))
    for x in range(120, W, 60):
        c.drawLine(x, top - 40, x, bot + 40, paint(SEPIA, 55, stroke=1.0))
    rows, q_row, q_u, now_row, now_u = 15, 4, 0.36, 9, 0.62
    gap = (bot - top) / (rows - 1)
    x0, w = 110, 950
    c.save()
    c.clipRect(drum)
    for r in range(rows):
        y = top + r * gap
        hh, mm = divmod(15 * 60 + 11 + (r - q_row) * 2, 60)
        label(c, f"{hh:02d}:{mm:02d}", 24, y + 6, 17, "mono", RED if q_row <= r <= now_row else INK, 190)
        if r > now_row:
            c.drawLine(x0, y, x0 + w, y, paint(SEPIA, 70, stroke=1.0))
            continue
        end = now_u if r == now_row else 1.0
        if r < q_row:
            ink(c, _row(x0, y, w, lambda u: 3.0, r, 0, end), INK, 230, 1.3, 0.5)
            continue
        if r == q_row:
            ink(c, _row(x0, y, w, lambda u: 3.0, r, 0, q_u + 0.002), INK, 230, 1.3, 0.5)
            amp = lambda u: 3 + 60 * smooth(prog(u, q_u, q_u + 0.02)) + 150 * smooth(prog(u, q_u + 0.22, q_u + 0.25))
            glow(c, _row(x0, y, w, amp, r, q_u, end), RED, 235, 1.6, 0.35)
            continue
        k = r - q_row
        amp = lambda u, k=k: 190 * math.exp(-k * 0.16) * (0.75 + 0.25 * math.sin(u * 11 + k))
        glow(c, _row(x0, y, w, amp, r, 0, end), RED, 220, 1.5, 0.3)
    c.restore()
    # the pen, writing right now
    px, py = x0 + now_u * w, top + now_row * gap
    pen = skia.Path()
    pen.moveTo(1140, py - 300)
    pen.lineTo(px, py)
    c.drawPath(pen, paint(SHADOW, 90, sigma=8, stroke=14))
    ink(c, pen, INK, 255, 7)
    c.drawCircle(px, py, 9, paint(RED))
    c.drawCircle(px, py, 9, paint(INK, 255, stroke=2))
    # the instrument readout
    label(c, "15:11", 1010, 352, 76, "mono_bold", INK, 255, "right")
    label(c, "QUAKE BEGINS · 22 MAY 1960", 1010, 388, 17, "mono", INK, 200, "right", 0.12)
    fig(c, 3, "SEISMOGRAM · 2 MIN A LINE", 70, 268, size=20)
    card(c, 600, 1300, 330, 74)
    label(c, "SHAKING", 622, 1346, 18, "mono", SEPIA, 255, tracking=0.16)
    label(c, "09:47", 908, 1356, 44, "mono_bold", RED, 255, "right")
    caption(c, ["about", "10 minutes"], 9.0, [0, 0], y=1470, size=88, emph={1: RED}, shake=lambda tt: 1.0)


# ---------------------------------------------------------------- FIG 4: how big? energy as area
def magnitude_frame(c, t):
    paper(c)
    x0, y0, S = 110, 1180, 820
    side = lambda m: S * 32 ** ((m - 9.5) / 2)
    big = skia.Path()
    big.addRect(skia.Rect.MakeXYWH(x0, y0 - S, S, S))
    cutout(c, big, mix(BONE, RED, 0.16), lift=14, edge=RED, edge_a=240, edge_wd=2.4)
    hatch(c, big, 70, 9, 45, RED, 1.2)
    label(c, "9.5", x0 + S - 30, y0 - S + 120, 120, "black", RED, 255, "right")
    label(c, "CHILE 1960", x0 + S - 30, y0 - S + 160, 24, "mono_bold", RED, 255, "right", 0.14)
    s = side(9.1)
    jp = skia.Path()
    jp.addRect(skia.Rect.MakeXYWH(x0, y0 - s, s, s))
    cutout(c, jp, WHITE, lift=10)
    hatch(c, jp, 45, 9, -45, INK, 1.0)
    label(c, "9.1", x0 + s - 24, y0 - s + 76, 70, "black", INK, 255, "right")
    label(c, "JAPAN 2011", x0 + s - 24, y0 - s + 108, 20, "mono_bold", INK, 255, "right", 0.14)
    s = side(8.0)
    sq = skia.Path()
    sq.addRect(skia.Rect.MakeXYWH(x0, y0 - s, s, s))
    cutout(c, sq, SHADE, lift=4)
    label(c, "8.0", x0 + s + 12, y0 - 14, 26, "mono_bold", INK, 255)
    s = side(7.0)
    c.drawRect(skia.Rect.MakeXYWH(x0, y0 - s, s, s), paint(INK))
    c.drawLine(x0 + s + 2, y0 - s - 2, x0 + 150, y0 - 150, paint(INK, 230, stroke=1.4))
    c.drawCircle(x0 + s / 2, y0 - s / 2, 16, paint(RED, 230, stroke=2))
    label(c, "7.0 · HAITI 2010", x0 + 158, y0 - 146, 26, "mono_bold", INK, 255)
    label(c, "that tiny dot", x0 + 158, y0 - 110, 28, "serif", INK, 240)
    label(c, "AREA = ENERGY  ·  EACH WHOLE STEP ≈ 32×", x0, y0 + 56, 20, "mono", INK, 200, tracking=0.12)
    # the counter the caption is pinned to, inside the 9.5 square
    label(c, "≈5,800×", x0 + S - 30, y0 - S + 330, 104, "black", RED, 255, "right")
    label(c, "THE ENERGY OF HAITI 2010", x0 + S - 30, y0 - S + 372, 20, "mono_bold", RED, 255, "right", 0.12)
    fig(c, 4, "HOW BIG WAS IT?", 70, 268, size=20)
    caption(c, ["thousands", "of times", "more"], 9.0, [0, 0, 0], y=1400, size=78, emph={0: RED})


# ---------------------------------------------------------------- FIG 5: the tsunami crosses the Pacific
def _gc_point(a, b, f):
    """Point a fraction f along the great circle from a to b."""
    l1, p1, l2, p2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.acos(clamp(math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(l2 - l1), -1, 1))
    A, B = math.sin((1 - f) * d) / math.sin(d), math.sin(f * d) / math.sin(d)
    x = A * math.cos(p1) * math.cos(l1) + B * math.cos(p2) * math.cos(l2)
    y = A * math.cos(p1) * math.sin(l1) + B * math.cos(p2) * math.sin(l2)
    z = A * math.sin(p1) + B * math.sin(p2)
    return math.degrees(math.atan2(y, x)), math.degrees(math.atan2(z, math.hypot(x, y)))


HILO_D, JAPAN_D = gc_km(EPI, HILO), gc_km(EPI, JAPAN)


def pacific_frame(c, t):
    paper(c)
    chart = Chart(118, 296, -60, 62, 0, 330, W)
    kmh = HILO_D / 15
    c.save()
    c.clipRect(chart.rect())
    c.drawRect(chart.rect(), paint(mix(BONE, TEAL, 0.07)))
    for lon in range(120, 300, 20):
        x, _, _ = chart(lon, 0)
        c.drawLine(x, chart.y, x, chart.y + chart.h, paint(SEPIA, 90, stroke=1.0))
    for lat in range(-60, 61, 20):
        _, y, _ = chart(180, lat)
        c.drawLine(0, y, W, y, paint(SEPIA, 90, stroke=1.0))
    fronts = [(3, 90), (6, 110), (10, 140), (19, 120), (22, 90)]
    for hrs, a0 in fronts:
        d = (hrs * kmh if hrs <= 15 else HILO_D + (hrs - 15) / 7 * (JAPAN_D - HILO_D)) / 6371
        p, _ = small_circle(chart, *EPI, d, 721)
        c.drawPath(p, paint(TEAL, a0, stroke=1.6))
    ang_h = HILO_D / 6371
    p, _ = small_circle(chart, *EPI, ang_h, 721)
    c.drawPath(p, paint(TEAL, 110, sigma=12, stroke=18, blend=MULT))
    c.drawPath(p, paint(TEAL, 255, stroke=4.0))
    engraved_land(c, land_path(chart, "world"), step=6, water_lines=(6, 13), key="pacific")
    c.restore()
    c.drawRect(chart.rect(), paint(INK, 200, stroke=1.6))
    for hrs in (3, 6, 10):   # hour marks on the fronts, toward the south-west
        x, y, _ = chart(*destination(*EPI, math.radians(262), hrs * kmh / 6371))
        tab(c, x - 26, y - 14, 52, 26)
        label(c, f"{hrs} H", x, y + 6, 16, "mono_bold", TEAL, 255, "center")
    gp = skia.Path()
    for i in range(121):
        x, y, _ = chart(*_gc_point(EPI, JAPAN, i / 120))
        (gp.lineTo if i else gp.moveTo)(x, y)
    c.drawPath(gp, dashed(paint(INK, 160, stroke=1.6), 10, 9))
    ex, ey, _ = chart(*EPI)
    star(c, ex, ey, 15)
    label(c, "CHILE", ex - 20, ey + 46, 22, "semibold", INK, 255, "right", 0.1)
    hx, hy, _ = chart(*HILO)
    tab(c, hx + 16, hy - 22, 254, 76)
    pin(c, hx, hy, "HAWAII", "15 HOURS · 61 DIED", side=1, size=24, sub_rgb=INK)
    jx, jy, _ = chart(*JAPAN)
    tab(c, jx + 16, jy - 22, 254, 76)
    pin(c, jx, jy, "JAPAN", "~1 DAY · ~140 DIED", side=1, size=24, sub_rgb=INK)
    mx, my, _ = chart(*_gc_point(EPI, JAPAN, 0.3))
    tab(c, mx - 70, my - 40, 140, 30)
    label(c, "17,000 KM", mx, my - 18, 20, "mono_bold", INK, 255, "center", 0.08)
    # the caption rides the wave front itself
    _, pts = small_circle(chart, *EPI, ang_h + 0.045, 1441)
    seg = sorted([(x, y) for x, y in pts if 110 < x < 640 and chart.y + 300 < y < chart.y + chart.h - 40])
    caption_on_path(c, "across the entire Pacific", seg, 20, 44, "serif_bold", TEAL, 255)
    fig(c, 5, "THE TSUNAMI, 22–23 MAY 1960", 70, 268, size=20)
    card(c, 110, 1150, 820, 130)
    label(c, "SPEED IN DEEP WATER", 140, 1192, 18, "mono", SEPIA, 255, tracking=0.14)
    label(c, "~750 KM/H", 140, 1256, 60, "mono_bold", TEAL, 255)
    label(c, "almost a jet plane", 900, 1250, 34, "serif", INK, 255, "right")
    caption(c, ["the tsunami", "kept going"], 9.0, [0, 0], y=1420, size=80, emph={1: TEAL})


# ---------------------------------------------------------------- FIG 6: the sunken forest, the volcano
def dead_tree(c, x, base, h, seed, a=255):
    """A drowned tree: a tapering trunk with a snapped, jagged top, bark lines and a few broken limbs."""
    rng = np.random.default_rng(seed)
    w0 = 16 + h * 0.035
    w1 = w0 * 0.45
    lean = rng.normal(0, 8)
    p = skia.Path()
    p.moveTo(x - w0, base)
    p.cubicTo(x - w0 * 0.9, base - h * 0.4, x - w1 + lean * 0.6, base - h * 0.8, x - w1 + lean, base - h)
    for k in range(5):   # the snapped top
        p.lineTo(x - w1 + lean + (k + 1) * w1 * 2 / 5, base - h - (rng.random() * 34 if k % 2 == 0 else -rng.random() * 8))
    p.cubicTo(x + w1 + lean * 0.6, base - h * 0.8, x + w0 * 0.9, base - h * 0.4, x + w0, base)
    p.close()
    for k in range(int(2 + rng.integers(0, 3))):   # broken limbs
        u = 0.4 + rng.random() * 0.45
        y = base - h * u
        side = -1 if k % 2 else 1
        L = 40 + rng.random() * 60
        b = skia.Path()
        b.moveTo(x + lean * u, y)
        b.quadTo(x + side * L * 0.6, y - L * 0.15, x + side * L, y - L * (0.45 + rng.random() * 0.4))
        c.drawPath(b, paint(INK, a, stroke=7 * (1 - u) + 3))
    c.drawPath(p, paint(mix(INK, SEPIA, 0.08), a))
    c.save()
    c.clipPath(p, doAntiAlias=True)
    for k in range(-3, 4):   # bark: thin pale lines down the trunk
        xx = x + k * w0 * 0.28 + lean * 0.5
        c.drawLine(xx, base, xx + lean * 0.4, base - h - 40, paint(SEPIA, 70, stroke=1.2))
    c.drawLine(x - w0 * 0.75, base, x - w1 + lean, base - h, paint(BONE, 90, stroke=3))   # lit edge
    c.restore()


def _plume(cx, cy, rng, n, spread, rise, drift, r0, r1):
    p = skia.Path()
    for k in range(n):
        u = (k / n) ** 0.8
        q = skia.Path()
        q.addCircle(cx + rng.normal(0, 10 + u * spread) + u * drift, cy - u * rise, r0 + u * r1 + rng.random() * 18)
        p = skia.Op(p, q, skia.PathOp.kUnion_PathOp) or p
    return p


def forest_frame(c, t):
    paper(c, grid=False)
    water = 1110
    sky = skia.GradientShader.MakeLinear([(0, 200), (0, water)], [col(BONE), col(WHITE), col(mix(BONE, RED, 0.07))],
                                         [0, 0.65, 1])
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, water), skia.Paint(Shader=sky))
    # the volcano erupting in the distance (Cordón Caulle, two days after the quake)
    vx, vtop = 760, 850
    rng = np.random.default_rng(4)
    back = _plume(vx, vtop, rng, 26, 120, 520, 170, 34, 100)
    cutout(c, back, mix(SEPIA, INK, 0.2), lift=10, edge_a=150)
    hatch(c, back, 40, 7, 30, INK, 0.9)
    front = _plume(vx + 10, vtop - 40, rng, 18, 70, 380, 120, 26, 70)
    cutout(c, front, mix(SHADE, SEPIA, 0.35), lift=8, edge_a=170)
    hatch(c, front, 30, 9, -30, INK, 0.9)
    c.drawCircle(vx, vtop + 6, 40, paint(RED, 170, sigma=18, blend=MULT))
    tab(c, 330, 396, 300, 30, 290)
    label(c, "CORDÓN CAULLE · ERUPTING", 620, 418, 18, "mono_bold", INK, 240, "right", 0.12)
    c.drawLine(624, 412, 680, 450, paint(INK, 200, stroke=1.4))
    for k, (pts, fill) in enumerate((
            ([(-20, 1000), (180, 940), (360, 975), (560, 925), (700, 900), (740, vtop + 4), (790, vtop + 4), (840, 905),
              (960, 960), (1100, 950)], mix(SHADE, SEPIA, 0.45)),
            ([(-20, 1060), (160, 1030), (330, 1050), (520, 1020), (760, 1055), (940, 1030), (1100, 1050)], mix(SHADE, INK, 0.16)))):
        p = skia.Path()
        p.moveTo(-20, water + 10)
        for x, y in pts:
            p.lineTo(x, y)
        p.lineTo(1100, water + 10)
        p.close()
        cutout(c, p, fill, lift=6 + k * 4, edge_a=140)
    lava = skia.Path()
    lava.moveTo(748, vtop + 6)
    lava.quadTo(735, vtop + 40, 712, vtop + 64)
    c.drawPath(lava, paint(RED, 230, stroke=3))
    # water
    c.drawRect(skia.Rect.MakeLTRB(0, water, W, H), paint(mix(BONE, TEAL, 0.15)))
    trees = [(120, 470, 1), (300, 330, 2), (430, 560, 3), (610, 280, 4), (900, 520, 6), (1010, 330, 7)]
    # reflections: flipped, faded with depth, broken into slices that drift sideways like ripples
    for k in range(0, 300, 6):
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(0, water + k, W, water + k + 6))
        c.translate(math.sin(k * 0.21) * 5, 0)
        c.translate(0, 2 * water)
        c.scale(1, -1)
        for x, h, s in trees:
            dead_tree(c, x, water, h, s, int(110 * (1 - k / 300)))
        c.restore()
    for y in range(water + 6, H, 7):
        d = (y - water) / (H - water)
        c.drawLine(0, y, W, y, paint(TEAL, 60 + 70 * d, stroke=1.0))
    for x, h, s in trees:
        dead_tree(c, x, water + 4, h, s)
        for k in range(3):
            c.drawOval(skia.Rect.MakeXYWH(x - 34 - k * 24, water + 2 + k * 7, 68 + k * 48, 10 + k * 4),
                       paint(TEAL, 210 - k * 55, stroke=1.4))
    c.drawLine(0, water, W, water, paint(TEAL, 255, stroke=2.2))
    # where the ground used to be
    old = water - 150
    c.drawLine(0, old, W, old, dashed(paint(RED, 230, stroke=2.4), 18, 12))
    tab(c, 150, old - 44, 440, 32, 290)
    label(c, "GROUND LEVEL BEFORE 22 MAY 1960", 162, old - 20, 18, "mono_bold", RED, 255, tracking=0.12)
    dim_line(c, 56, old, 56, water, "−2 M", 255, RED, 22)
    fig(c, 6, "SUNKEN FOREST, NEAR VALDIVIA", 70, 268, size=20)
    # caption: "sank" slips under a waterline drawn through the words
    size, y = 96, 1420
    words = ["the", "ground", "sank"]
    kinds, sizes, ws, xs, total = _word_layout(words, size, {2: TEAL})
    words_ink(c, words[:2], xs[0], y, size)
    f = font(kinds[2], sizes[2])
    wl = y - 14
    for top, bottom, dxk, al in [(-200, wl, 0, 255)] + [(wl + k, wl + k + 5, math.sin(k * 0.35) * 4, 255 * (1 - k / 80) * 0.55)
                                                       for k in range(0, 80, 5)]:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(0, y + top if top < 0 else top, W, bottom))
        x = xs[2]
        for j, ch in enumerate("sank"):
            dy = j * 8
            c.drawString(ch, x + dxk, y + dy, f, paint(TEAL if top >= wl else INK, al))
            x += f.measureText(ch)
        c.restore()
    g = skia.GradientShader.MakeLinear([(xs[2] - 60, 0), (xs[2] + ws[2] + 60, 0)],
                                       [col(TEAL, 0), col(TEAL, 255), col(TEAL, 255), col(TEAL, 0)], [0, 0.15, 0.85, 1])
    lp = skia.Paint(AntiAlias=True, Shader=g, StrokeWidth=2.4, Style=skia.Paint.kStroke_Style)
    c.drawLine(xs[2] - 60, wl, xs[2] + ws[2] + 60, wl, lp)


# ---------------------------------------------------------------- FIG 7: title card
def title_frame(c, t):
    paper(c)
    y = 1150
    c.drawLine(-20, y, W + 20, y, paint(SEPIA, 180, stroke=1.0))
    p = trace_path(-20, y, W + 40, 130, 1600, seed=3, quake=0.5, quiet=0.025, width_=0.25, decay=1.0, freq=0.5)
    glow(c, p, RED, 255, 2.0, 0.7)
    label(c, "THE DAY THE EARTH", W / 2, 560, 84, "serif_roman", INK, 255, "center", 0.02)
    w = width("RANG", "serif_bold", 210)
    ringing_word(c, "RANG", W / 2 - w / 2, 770, 210, BRONZE, 255, 5)
    label(c, "like a bell", W / 2, 870, 70, "serif", INK, 255, "center")
    label(c, "VALDIVIA, CHILE  ·  22 MAY 1960", W / 2, 1420, 24, "mono_bold", INK, 255, "center", 0.16)
    label(c, "THE BIGGEST EARTHQUAKE EVER RECORDED", W / 2, 1462, 19, "mono", INK, 190, "center", 0.18)


FRAMES = [("frame_1_bell", bell_frame), ("frame_2_fault", fault_frame), ("frame_3_drum", drum_frame),
          ("frame_4_magnitude", magnitude_frame), ("frame_5_pacific", pacific_frame),
          ("frame_6_forest", forest_frame), ("frame_7_title", title_frame)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    paths = []
    for name, fn in FRAMES:
        p = os.path.join(OUT, f"{name}.png")
        paths.append(p)
        if only and not any(o in name for o in only):
            continue
        kw = dict(shake=0.25) if "drum" in name else {}
        Image.fromarray(render(fn, 9.0, samples=1, **kw)).save(p)
        print(p)
    n = len(paths)
    sheet = Image.new("RGB", (n * 432 + (n + 1) * 20, 768 + 40), BONE)
    for i, p in enumerate(paths):
        if os.path.exists(p):
            sheet.paste(Image.open(p).resize((432, 768), Image.LANCZOS), (20 + i * 452, 20))
    sheet.save(os.path.join(OUT, "style_frames.png"))
