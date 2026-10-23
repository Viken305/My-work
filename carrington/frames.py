"""Style frames for approval.

  python3 frames.py            -> out/style/frame_1_title.png ... frame_7_nearmiss.png + out/style/style_frames.png
  python3 frames.py aurora     -> only the frames whose name contains "aurora"
"""
import math, os, sys

import numpy as np
import skia
from PIL import Image

from lantern import *  # noqa: F401,F403
from lantern import _word_layout

OUT = os.path.join(HERE, "out", "style")
EARTH_SEA = (18, 28, 52)


# ---------------------------------------------------------------- shared pieces
def text_on_circle(c, s, cx, cy, r, start_deg, size=18, kind="mono", rgb=LIME, a=255, tracking=0.25):
    """Letters set around a ring (reading clockwise), like the engraved bezel of an instrument."""
    f = font(kind, size)
    ang = math.radians(start_deg)
    for ch in s:
        cw = f.measureText(ch) + tracking * size
        th = ang + cw / 2 / r
        c.save()
        c.translate(cx + math.cos(th) * r, cy + math.sin(th) * r)
        c.rotate(math.degrees(th) + 90)
        c.drawString(ch, -f.measureText(ch) / 2, 0, f, paint(rgb, a))
        c.restore()
        ang += cw / r


def bezel(c, cx, cy, r, a=255, text="", start=-90, ticks=120):
    c.drawCircle(cx, cy, r, paint(LIME, a * 0.7, stroke=1.2))
    c.drawCircle(cx, cy, r + 36, paint(LIME, a * 0.45, stroke=1.0))
    for k in range(ticks):
        th = k / ticks * 2 * math.pi
        L = 12 if k % 10 == 0 else 6
        c.drawLine(cx + math.cos(th) * r, cy + math.sin(th) * r, cx + math.cos(th) * (r + L), cy + math.sin(th) * (r + L),
                   paint(LIME, a * (0.8 if k % 10 == 0 else 0.45), stroke=1.1))
    if text:
        text_on_circle(c, text, cx, cy, r + 26, start, 16, "mono", LIME, a * 0.85)


def flare_bead(c, pts, a=255, k=1.0):
    """One of Carrington's 'two patches of intensely bright and white light': a kidney of white-hot light."""
    path = polyline(pts)
    path.close()
    c.drawPath(path, paint(SUN, a * 0.35 * k, sigma=40, blend=ADD))
    c.drawPath(path, paint(FLARE, a * 0.5 * k, sigma=12, blend=ADD))
    c.drawPath(path, paint(FLARE, a, sigma=1.5, blend=SCREEN))


def kidney(x, y, s, ang=0.0, n=40):
    out = []
    ca, sa = math.cos(ang), math.sin(ang)
    for k in range(n):
        th = k / n * 2 * math.pi
        rx = s * (1 + 0.25 * math.cos(2 * th))
        ry = s * 0.5 * (1 - 0.35 * math.sin(th) ** 3)
        px, py = math.cos(th) * rx, math.sin(th) * ry - 0.25 * s * math.cos(th) ** 2
        out.append((x + px * ca - py * sa, y + px * sa + py * ca))
    return out


def earth(c, proj, a=1.0, sun_dir=(-1, 0), rim=1.0, lights=0.0, key=None):
    """Earth on dark glass: indigo sea, engraved land with hatching, a day side lit from sun_dir, rim light."""
    R, cx, cy = proj.R, proj.cx, proj.cy
    disc = skia.Path()
    disc.addCircle(cx, cy, R)
    c.drawPath(disc, paint(EARTH_SEA, 255 * a))
    tint(c, disc, NIGHT, 160 * a, (3, 2), 2)
    landp = globe_land_path(proj)
    c.save()
    c.clipPath(disc, doAntiAlias=True)
    c.drawPath(landp, paint((46, 40, 52), 255 * a))
    hatch(c, landp, 70 * a, max(3.0, R / 40), 45, LIME, 0.8)
    engrave(c, landp, LIME, 200 * a, max(0.8, R / 220), 0.4)
    graticule(c, proj, 0.5 * a)
    # day side: a soft wash of limelight from the Sun's direction, night side falls to black
    sx, sy = sun_dir
    g = skia.GradientShader.MakeLinear([skia.Point(cx + sx * R, cy + sy * R), skia.Point(cx - sx * R, cy - sy * R)],
                                       [col(SUN, 70 * a), col(SUN, 0), col(VOID, 0), col(VOID, 200 * a)],
                                       [0.0, 0.45, 0.55, 0.95])
    p = skia.Paint(AntiAlias=True)
    p.setShader(g)
    c.drawPath(disc, p)
    c.restore()
    if rim:
        arc = skia.Path()
        start = math.degrees(math.atan2(sy, sx)) - 70
        arc.addArc(skia.Rect.MakeXYWH(cx - R, cy - R, 2 * R, 2 * R), start, 140)
        light(c, arc, SUN, 200 * a * rim, max(1.5, R / 90), 0.6)
    engrave(c, disc, LIME, 160 * a, 1.2, 0.3)


def caption_block(c, words, emph, y=CAP_Y, size=80, t=10.0, x=None, plate=True):
    caption(c, words, t, [0.0] * len(words), y, size, emph, plate=plate, x=x)


# ---------------------------------------------------------------- 1. title
def title_frame(c, t):
    glass(c)
    stars(c, 300, 4, (0, 0, W, 1100), 200, t)
    cx, cy, R = 540, 640, 300
    bezel(c, cx, cy, R + 40, 220, "SOL  ·  1 SEPTEMBER 1859  ·  11:18 A.M.  ·  REDHILL, SURREY  ·  ", -150)
    sun_disc(c, cx, cy, R, 255, 1.0, 1)
    for (x, y, r, s) in ((600, 600, 26, 1), (640, 625, 18, 2), (570, 640, 14, 3), (665, 600, 11, 4), (548, 612, 9, 5)):
        sunspot(c, x, y, r, 255, s, 0.85, 20)
    flare_bead(c, kidney(598, 588, 20, 0.4), 255, 1.4)
    flare_bead(c, kidney(642, 642, 16, -0.3), 255, 1.4)
    label(c, "1 SEPTEMBER 1859", W / 2, 1110, 26, "mono_bold", LIME, 230, "center", 0.32)
    label(c, "THE DAY THE SUN", W / 2, 1215, 84, "serif_roman", LIME, 255, "center", 0.04)
    f = font("serif_bold", 270)
    s = "Hit Us"
    w = width(s, "serif_bold", 270)
    x = W / 2 - w / 2
    for ch in s:
        c.drawString(ch, x, 1450, f, paint(SUN, 120, sigma=30, blend=ADD))
        c.drawString(ch, x, 1450, f, paint(SUN, 255, blend=SCREEN))
        c.drawString(ch, x, 1450, f, paint(FLARE, 120, sigma=0, blend=SCREEN))
        x += f.measureText(ch)
    label(c, "the biggest solar storm ever recorded", W / 2, 1530, 44, "serif", SILVER, 255, "center")
    slide_label(c, 1, "THE CARRINGTON EVENT", 70, 150)


# ---------------------------------------------------------------- 2. Carrington's sketch
def telescope(c, a=255):
    """Brass refractor, engraved, poking in from the top left; its eyepiece throws the Sun's image on the screen."""
    c.save()
    c.translate(-40, 160)
    c.rotate(28)
    tube = skia.Path()
    tube.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(0, -42, 420, 84), 8, 8))
    tint(c, tube, (200, 150, 80), 120, (4, 3))
    engrave(c, tube, LIME, a, 1.6)
    hatch(c, tube, 40, 5, 0, LIME, 0.7)
    for x in (60, 200, 340):
        c.drawLine(x, -42, x, 42, paint(LIME, a * 0.8, stroke=2))
    ep = skia.Path()
    ep.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(420, -20, 70, 40), 5, 5))
    engrave(c, ep, LIME, a, 1.4)
    c.restore()
    return (-40 + math.cos(math.radians(28)) * 490, 160 + math.sin(math.radians(28)) * 490)


def sketch_frame(c, t):
    glass(c, VOID)
    ex, ey = telescope(c)
    cx, cy, R = 560, 820, 360
    # the beam from the eyepiece to the screen
    beam = skia.Path()
    beam.moveTo(ex, ey - 6)
    beam.lineTo(cx - R * 0.72, cy - R * 0.7)
    beam.lineTo(cx + R * 0.7, cy + R * 0.72)
    beam.lineTo(ex, ey + 6)
    beam.close()
    c.drawPath(beam, paint(CARD, 26, sigma=18, blend=ADD))
    # the projection screen: the Sun's image on Carrington's card, the only paper-bright thing in the dark room
    disc = skia.Path()
    disc.addCircle(cx, cy, R)
    c.drawCircle(cx, cy, R * 1.12, paint(CARD, 60, sigma=40, blend=ADD))
    c.drawPath(disc, paint(mix(CARD, VOID, 0.06)))
    sh = skia.GradientShader.MakeRadial(skia.Point(cx, cy), R, [col(CARD, 0), col((170, 140, 95), 170)],
                                        [0.55, 1.0])
    p = skia.Paint(AntiAlias=True)
    p.setShader(sh)
    c.drawPath(disc, p)
    c.drawPath(disc, paint(SEPIA, 230, stroke=2.2))
    c.drawLine(cx - R, cy, cx + R, cy, paint(SEPIA, 130, stroke=1.2))     # his cross-wires
    c.drawLine(cx, cy - R, cx, cy + R, paint(SEPIA, 130, stroke=1.2))
    for k in range(-3, 4):
        if k:
            c.drawLine(cx + k * R / 4, cy - 8, cx + k * R / 4, cy + 8, paint(SEPIA, 140, stroke=1.2))
    # the sunspot group, as he drew it (sepia pen, hatched penumbra)
    rng = np.random.default_rng(3)
    for (x, y, r) in ((640, 760, 52), (700, 800, 34), (590, 800, 26), (740, 750, 20), (560, 760, 16), (660, 840, 14)):
        pen = skia.Path()
        for k in range(40):
            th = k / 40 * 2 * math.pi
            rr = r * (1 + 0.16 * math.sin(3 * th + x) + 0.06 * rng.normal())
            (pen.lineTo if k else pen.moveTo)(x + math.cos(th) * rr, y + math.sin(th) * rr * 0.8)
        pen.close()
        c.drawPath(pen, paint(SEPIA, 70))
        hatch(c, pen, 160, 3.2, 35, SEPIA, 0.9)
        c.drawPath(pen, paint(SEPIA, 230, stroke=1.4))
        c.drawCircle(x + 2, y, r * 0.38, paint((50, 32, 20), 255))
    # the two beads: white light so bright it burns through the paper
    for (bx, by, s, ang), (l0, l1) in (((620, 728, 30, 0.35), ("A", "C")), ((700, 852, 24, -0.4), ("B", "D"))):
        flare_bead(c, kidney(bx, by, s, ang), 255, 1.6)
        label(c, l0, bx - s - 34, by - 18, 40, "serif_bold", SEPIA, 255)
        label(c, l1, bx + s + 70, by - 44, 36, "serif_bold", SEPIA, 230)
        c.drawPath(polyline([(bx + s, by - 8), (bx + s + 64, by - 48)]), dashed(paint(SEPIA, 170, stroke=1.4), 6, 6))
    # pocket watch
    wx, wy, wr = 860, 1225, 108
    c.drawCircle(wx, wy - wr - 14, 14, paint(LIME, 220, stroke=1.6))
    c.drawCircle(wx, wy, wr + 8, paint(VOID, 255))
    face = skia.Path()
    face.addCircle(wx, wy, wr)
    tint(c, face, CARD, 60, (3, 3), 2)
    engrave(c, face, LIME, 255, 2.2)
    c.drawCircle(wx, wy, wr - 10, paint(LIME, 120, stroke=1))
    for k in range(60):
        th = k / 60 * 2 * math.pi
        L = 10 if k % 5 == 0 else 4
        c.drawLine(wx + math.sin(th) * (wr - 12), wy - math.cos(th) * (wr - 12), wx + math.sin(th) * (wr - 12 - L),
                   wy - math.cos(th) * (wr - 12 - L), paint(LIME, 220, stroke=1.2))
    for n, th in (("XII", 0), ("III", 90), ("VI", 180), ("IX", 270)):
        r = math.radians(th)
        label(c, n, wx + math.sin(r) * (wr - 40), wy - math.cos(r) * (wr - 40) + 8, 20, "serif_roman", LIME, 230, "center")
    for ang, L, wd in ((360 * (11 + 18 / 60) / 12, 52, 4.0), (360 * 18 / 60, 80, 2.4)):
        r = math.radians(ang)
        c.drawLine(wx, wy, wx + math.sin(r) * L, wy - math.cos(r) * L, paint(LIME, 255, stroke=wd))
    c.drawCircle(wx, wy, 6, paint(SUN))
    tag(c, 70, 1170, "REDHILL, ENGLAND", LIME, 255, 22)
    tag(c, 70, 1222, "11:18 A.M. · 1 SEPT 1859", SUN, 255, 22)
    slide_label(c, 2, "CARRINGTON'S DRAWING", 70, 150)
    caption_block(c, ["two", "beads", "of", "blinding", "light"], {3: FLARE}, y=CAP_Y + 20)


# ---------------------------------------------------------------- 3. the crossing
def cme(c, sx, sy, ex, ey, front, a=255, seed=0, t=0.0):
    """The cloud: a bubble of twisted gold strands whose front is `front` px from the Sun, aimed at Earth."""
    rng = np.random.default_rng(seed)
    ang0 = math.atan2(ey - sy, ex - sx)
    half = math.radians(24)
    # interior: drifting particles
    for k in range(900):
        rr = front * (0.35 + 0.65 * rng.random() ** 0.6)
        th = ang0 + (rng.random() * 2 - 1) * half * (rr / front)
        x, y = sx + math.cos(th) * rr, sy + math.sin(th) * rr
        c.drawCircle(x, y, 0.6 + rng.random() * 1.6, paint(SUN, a * 0.25 * rng.random(), blend=ADD))
    # strands: the twisted flux rope as stacked bright arcs
    for k in range(34):
        r = front - k * 5 - rng.random() * 4
        if r < 30:
            break
        pts = []
        h = half * (0.9 + 0.1 * rng.random())
        for j in range(80):
            u = j / 79
            th = ang0 - h + 2 * h * u
            rr = r * (1 - 0.18 * (2 * u - 1) ** 2) + math.sin(u * 14 + k + t * 2) * 3
            pts.append((sx + math.cos(th) * rr, sy + math.sin(th) * rr))
        w = 1.6 if k else 3.4
        if k == 0:
            light(c, polyline(pts), SUN, a, w, 1.3)
        else:
            c.drawPath(polyline(pts), paint(SUN, a * 0.55 * math.exp(-k / 12), stroke=w * 0.6, blend=ADD))
    # loops of the rope
    for k in range(6):
        u = (k + 0.5) / 6
        th = ang0 - half * 0.75 + 1.5 * half * u
        rr = front * 0.78
        x, y = sx + math.cos(th) * rr, sy + math.sin(th) * rr
        o = skia.Path()
        o.addOval(skia.Rect.MakeXYWH(x - 30, y - 60, 60, 120))
        c.save()
        c.translate(x, y)
        c.rotate(math.degrees(th))
        c.translate(-x, -y)
        c.drawPath(o, paint(SUN, a * 0.35, stroke=1.4, blend=ADD))
        c.restore()
    return ang0, half


def crossing_frame(c, t):
    glass(c)
    stars(c, 380, 7, (0, 0, W, H), 210, t)
    sx, sy, R = -120, 300, 470
    ex, ey = 860, 1150
    sun_disc(c, sx, sy, R, 255, 1.0, 2)
    c.drawPath(polyline([(sx + R * 0.66, sy + R * 0.75), (ex, ey)]), dashed(paint(SILVER, 160, stroke=1.4), 3, 9))
    ang0, half = cme(c, sx, sy, ex, ey, 1050, 255, 3, t)
    # caption riding the front of the cloud
    pts = []
    rr = 1050
    for j in range(80):
        u = j / 79
        th = ang0 - half * 0.9 + 1.8 * half * u
        pts.append((sx + math.cos(th) * (rr + 34), sy + math.sin(th) * (rr + 34)))
    caption_on_path(c, "17.6 HOURS", pts[::-1], 300, 70, "serif_bold", FLARE, 255, 1.0, SUN)
    pr = Ortho(-30, 10, 62, ex, ey)
    earth(c, pr, 1.0, (-0.7, -0.7), 1.0)
    label(c, "EARTH", ex, ey + 100, 22, "mono_bold", LIME, 230, "center", 0.2)
    # race card
    y0 = 1010
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(60, y0, 430, 230), 8, 8), paint(VOID, 210))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(60, y0, 430, 230), 8, 8), paint(LIME, 120, stroke=1.2))
    rows = (("ITS LIGHT", "8 MIN", LIME), ("A NORMAL CLOUD", "2–4 DAYS", SILVER), ("THIS CLOUD", "17.6 H", SUN))
    label(c, "SUN → EARTH · 150 MILLION KM", 86, y0 - 18, 16, "mono", SILVER, 255, tracking=0.1)
    for i, (k, v, rgb) in enumerate(rows):
        y = y0 + 60 + i * 66
        label(c, k, 86, y, 20, "mono", SILVER, 255, tracking=0.1)
        label(c, v, 466, y, 34 if i == 2 else 28, "mono_bold", rgb, 255, "right")
        if i < 2:
            c.drawLine(86, y + 22, 466, y + 22, paint(LIME, 60, stroke=1))
    slide_label(c, 3, "THE CROSSING", 70, 150)
    caption_block(c, ["and", "it", "was", "aimed", "at", "us"], {5: SUN}, y=CAP_Y + 50)


# ---------------------------------------------------------------- 4. the shield
def dipole_line(cx, cy, L, comp, stretch, tilt=-12.0, side=1, n=160):
    """One magnetic field line r = L sin^2(theta) in the screen plane, squashed on the sunward (left) side by `comp`
    and dragged out on the night side by `stretch`."""
    tr = math.radians(tilt)
    pts = []
    for j in range(n):
        th = 0.06 + (math.pi - 0.12) * j / (n - 1)
        r = L * math.sin(th) ** 2
        x, y = side * r * math.sin(th), -r * math.cos(th)
        if side < 0:
            x *= 1 - comp * clamp((r / L) ** 1.5)
        else:
            x *= 1 + stretch * clamp(r / L) ** 2
        X = x * math.cos(tr) - y * math.sin(tr)
        Y = x * math.sin(tr) + y * math.cos(tr)
        pts.append((cx + X, cy + Y))
    return pts


def kew_card(c, x, y, w, h, a=255):
    """The Kew magnetogram: the photographic trace (dark on cream) that ran right off the paper."""
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 4, 4)
    c.drawRRect(r.makeOffset(0, 6), paint((0, 0, 0), a * 0.6, sigma=10))
    c.drawRRect(r, paint(CARD, a))
    for k in range(1, 12):
        c.drawLine(x + k * w / 12, y + 8, x + k * w / 12, y + h - 8, paint(SEPIA, a * 0.18, stroke=1))
    c.drawLine(x + 10, y + h * 0.5, x + w - 10, y + h * 0.5, paint(SEPIA, a * 0.3, stroke=1))
    pts = []
    for i in range(700):
        u = i / 699
        pts.append((x + 14 + u * (w - 28), y + h * 0.5 - magnetogram(u, 2) * h * 0.55))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    c.drawPath(polyline(pts), paint(SEPIA, a, stroke=1.6))
    c.restore()
    label(c, "KEW OBSERVATORY · MAGNETOGRAPH", x + 14, y + 30, 16, "mono_bold", SEPIA, a, tracking=0.1)
    label(c, "OFF THE SCALE ↓", x + w - 16, y + 30, 16, "mono_bold", AUR_R, a, "right", tracking=0.1)
    fx = x + 14 + 0.32 * (w - 28)
    c.drawLine(fx, y + h * 0.18, fx, y + h * 0.3, paint(SEPIA, a, stroke=1.2))
    label(c, "FLARE", fx, y + h * 0.16, 14, "mono", SEPIA, a, "center", 0.1)


def shield_frame(c, t):
    glass(c)
    stars(c, 260, 9, (0, 0, W, H), 180, t)
    cx, cy, R = 640, 980, 120
    # the solar wind / cloud arriving from the left: horizontal gold streaks piling up against the shield
    rng = np.random.default_rng(5)
    for k in range(120):
        y = 520 + rng.random() * 760
        dy = (y - cy) / 560
        xb = cx - 360 * (1 - 0.55 * dy * dy) - 30           # where the field holds them off
        x0 = -40 + rng.random() * 200
        L = max(0.0, xb - x0) * (0.4 + 0.6 * rng.random())
        c.drawLine(x0 + (xb - x0 - L), y, xb - 8 * rng.random(), y,
                   paint(SUN, 30 + 90 * rng.random(), stroke=0.8 + rng.random() * 1.6, blend=ADD))
    bow = [(cx - 360 * (1 - 0.55 * ((y - cy) / 560) ** 2) - 30, y) for y in np.linspace(500, 1300, 80)]
    light(c, polyline(bow), SUN, 230, 3.0, 1.2)
    # the field: silver lines, squashed on the day side, dragged into a tail on the night side
    for i, L in enumerate((190, 260, 350, 470, 620, 800)):
        for side in (-1, 1):
            pts = dipole_line(cx, cy, L, 0.12 + 0.07 * i, 0.15 + 0.12 * i, side=side)
            pts = [(x, y) for x, y in pts if x < W + 200]
            engrave(c, polyline(pts), LIME if i < 5 else SILVER, 220 - i * 18, 1.4, 0.5)
    # the poles light up where the outer lines come down: the auroral ovals
    for sgn in (-1, 1):
        o = skia.Path()
        tr = math.radians(-12)
        px, py = cx + sgn * -math.sin(tr) * R * 0.92, cy - sgn * math.cos(tr) * R * 0.92
        o.addOval(skia.Rect.MakeXYWH(px - 48, py - 10, 96, 20))
        light(c, o, AUR_G, 255, 2.6, 1.4, None)
    pr = Ortho(-40, 15, R, cx, cy, -12)
    earth(c, pr, 1.0, (-1, 0), 1.0)
    caption_on_path(c, "squeezed", [(x - 12, y + 10) for x, y in dipole_line(cx, cy, 620, 0.47, 0.6, side=-1)[80:]], 30, 46,
                    "serif_bold", SUN, 255, 1.0, SUN)
    kew_card(c, 70, 220, 940, 190)
    slide_label(c, 4, "EARTH'S MAGNETIC FIELD", 70, 150)
    caption_block(c, ["it", "slammed", "into", "Earth's", "magnetic", "field"], {1: SUN}, y=CAP_Y + 60, size=74)


# ---------------------------------------------------------------- 5. the aurora
def mountains(seed, y0, amp, n=140, rough=0.5):
    rng = np.random.default_rng(seed)
    ys = np.zeros(n)
    k = 1.0
    for o in range(6):
        ph = rng.random() * 6.28
        ys += amp * k * np.sin(np.linspace(0, (2 + o * 2.3) * math.pi, n) + ph)
        k *= rough
    pts = [(-20 + i * (W + 40) / (n - 1), y0 - abs(ys[i]) - amp * 0.3) for i in range(n)]
    p = polyline(pts)
    p.lineTo(W + 40, H + 10)
    p.lineTo(-40, H + 10)
    p.close()
    return p, pts


def tent(c, x, y, s, a=255):
    p = skia.Path()
    p.moveTo(x - s, y)
    p.lineTo(x, y - s * 1.1)
    p.lineTo(x + s, y)
    p.close()
    c.drawPath(p, paint((22, 18, 26), a))
    c.drawPath(p, paint(LIME, a * 0.75, stroke=1.2))
    door = skia.Path()
    door.moveTo(x - s * 0.18, y)
    door.lineTo(x, y - s * 0.55)
    door.lineTo(x + s * 0.18, y)
    door.close()
    c.drawPath(door, paint(CARD, a * 0.85))
    c.drawPath(door, paint(CARD, a * 0.4, sigma=10, blend=ADD))


def pine(c, x, y, h, a=255):
    p = skia.Path()
    p.moveTo(x, y - h)
    for k in range(5):
        u = (k + 1) / 5
        w = h * 0.22 * u
        p.lineTo(x + w, y - h + h * u * 0.9)
        p.lineTo(x + w * 0.35, y - h + h * u * 0.9 - h * 0.05)
    p.lineTo(x, y)
    for k in range(4, -1, -1):
        u = (k + 1) / 5
        w = h * 0.22 * u
        p.lineTo(x - w * 0.35, y - h + h * u * 0.9 - h * 0.05)
        p.lineTo(x - w, y - h + h * u * 0.9)
    p.close()
    c.drawPath(p, paint((10, 9, 13), a))
    c.drawPath(p, paint(AUR_G, a * 0.25, stroke=1.0, blend=ADD))


def aurora_frame(c, t):
    glass(c)
    sky = skia.Path()
    sky.addRect(skia.Rect.MakeWH(W, 1500))
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 1500)],
                                        [col((70, 18, 50)), col(NIGHT), col((16, 30, 40))], [0, 0.55, 1])
    p = skia.Paint(AntiAlias=True)
    p.setShader(sh)
    p.setAlphaf(0.9)
    c.drawPath(sky, p)
    stars(c, 420, 11, (0, 0, W, 1300), 230, t)
    aurora(c, t, -100, W + 100, 1080, 760, 1, 1.0, 460, 2, 0.05)
    aurora(c, t + 3, -60, W + 60, 900, 600, 2, 0.8, 380, 3, -0.08)
    aurora(c, t + 7, 200, W + 200, 1220, 520, 3, 0.9, 300, 2, 0.1)
    far, _ = mountains(4, 1420, 100, 160, 0.55)
    c.drawPath(far, paint((26, 24, 40)))
    engrave(c, far, LIME, 110, 1.0, 0.3)
    hatch(c, far, 18, 6, 70, LIME, 0.7)
    near, npts = mountains(8, 1600, 50, 120, 0.5)
    c.drawPath(near, paint((14, 12, 18)))
    engrave(c, near, LIME, 170, 1.3, 0.3)
    hatch(c, near, 26, 5, -60, LIME, 0.7)
    # aurora light falling on the ridgelines
    c.drawPath(polyline(npts), paint(AUR_G, 90, sigma=6, stroke=6, blend=ADD))
    rng = np.random.default_rng(31)
    for k in range(70):                                      # a pine fringe along the near ridge
        x = rng.random() * W
        yy = min(y for xx, y in npts if abs(xx - x) < 12) + 4
        pine(c, x, yy, 30 + rng.random() * 60)
    for x, s_ in ((330, 46), (420, 36), (760, 52)):
        yy = min(y for xx, y in npts if abs(xx - x) < 12) + 10
        tent(c, x, yy, s_)
    # the reach: a small globe with the auroral oval pushed down to the tropics
    gx, gy, gr = 840, 330, 150
    pr = Ortho(-110, 28, gr, gx, gy)
    c.drawCircle(gx, gy, gr + 14, paint(VOID, 230, sigma=8))
    earth(c, pr, 1.0, (0, -1), 0.0)
    for lat, rgb, a in ((62, AUR_G, 200), (45, AUR_G, 160), (25, AUR_R, 230)):
        light(c, lat_circle(pr, lat), rgb, a, 2.0, 0.8, None)
    for name, lon, lat, dx in (("CUBA", -79.5, 22, 1), ("HAWAII", -157, 20.5, 1), ("PANAMA", -79.5, 9.0, 1)):
        x, y, z = pr(lon, lat)
        bloom_dot(c, x, y, 3, AUR_R, 255)
        label(c, name, x + 10 * dx, y + 20, 14, "mono_bold", LIME, 255, tracking=0.1)
    tag(c, 70, 300, "THE AURORA REACHED", LIME, 255, 20)
    tag(c, 70, 350, "THE TROPICS", AUR_R, 255, 20)
    tag(c, 70, 1250, "ROCKY MOUNTAINS · ~1 A.M.", LIME, 255, 20)
    slide_label(c, 5, "THE SKY ON FIRE, 2 SEPT 1859", 70, 150)
    caption_block(c, ["bright", "enough", "to", "read", "by"], {3: AUR_G}, y=CAP_Y - 200)


# ---------------------------------------------------------------- 6. the telegraph
def morse_tape(c, text, x0, y, x1, a=255, burn_from=None, t=0.0):
    """Paper tape from the register: embossed dots and dashes with the letters pencilled under them. Past
    burn_from the tape scorches, curls black and glows at the edge."""
    h = 96
    r = skia.Rect.MakeLTRB(x0, y - h / 2, x1, y + h / 2)
    c.drawRect(r.makeOffset(0, 8), paint((0, 0, 0), a * 0.6, sigma=10))
    c.drawRect(r, paint(CARD, a))
    for k in range(int((x1 - x0) / 9)):
        c.drawLine(x0 + k * 9, y - h / 2, x0 + k * 9 + 4, y + h / 2, paint(SEPIA, a * 0.04, stroke=1))
    x = x0 + 40
    f = font("mono_bold", 22)
    for ch in text.upper():
        if ch == " ":
            x += 30
            continue
        code = MORSE.get(ch, "")
        cw = 0
        for sym in code:
            L = 6 if sym == "." else 22
            c.drawRoundRect(skia.Rect.MakeXYWH(x + cw, y - 26, L, 8), 4, 4, paint(SEPIA, a))
            cw += L + 6
        c.drawString(ch, x + cw / 2 - f.measureText(ch) / 2, y + 26, f, paint(SEPIA, a * 0.85))
        x += max(cw, 18) + 16
    if burn_from is not None:
        # charring: darken toward the burnt end, a ragged glowing edge, ember specks, smoke
        rng = np.random.default_rng(2)
        wob = np.cumsum(rng.normal(0, 9, 31))
        edge = [(burn_from + wob[k] - wob.mean() + 14 * math.sin(k * 0.5), y - h / 2 - 2 + k * (h + 4) / 30)
                for k in range(31)]
        burnt = polyline(edge)
        burnt.lineTo(x1 + 2, y + h / 2)
        burnt.lineTo(x1 + 2, y - h / 2)
        burnt.close()
        scorch = skia.GradientShader.MakeLinear([skia.Point(burn_from - 160, 0), skia.Point(burn_from, 0)],
                                                [col((90, 50, 20), 0), col((60, 30, 10), 220)], [0, 1])
        p = skia.Paint(AntiAlias=True)
        p.setShader(scorch)
        c.save()
        c.clipRect(r)
        c.drawRect(skia.Rect.MakeLTRB(burn_from - 160, y - h / 2, burn_from + 60, y + h / 2), p)
        c.drawPath(burnt, paint(VOID, 255))
        c.restore()
        light(c, polyline(edge), (255, 120, 40), 255, 2.4, 1.3, (255, 230, 160))
        for k in range(40):
            ex = burn_from + rng.normal(0, 30)
            ey = y - h / 2 - rng.random() ** 2 * 160
            bloom_dot(c, ex, ey, 1 + rng.random() * 1.6, (255, 140, 50), 200 * rng.random())
        for k in range(5):
            sm = skia.Path()
            sx = burn_from + rng.normal(0, 20)
            sm.moveTo(sx, y - h / 2)
            for j in range(1, 30):
                sm.lineTo(sx + math.sin(j * 0.4 + k + t) * (8 + j * 1.4), y - h / 2 - j * 14)
            c.drawPath(sm, paint(SILVER, 30, sigma=6, stroke=8))


def pole(c, x, y0, y1, a=255):
    c.drawLine(x, y0, x, y1, paint(LIME, a * 0.9, stroke=6))
    hatch_r = skia.Path()
    hatch_r.addRect(skia.Rect.MakeLTRB(x - 3, y0, x + 3, y1))
    c.drawLine(x - 70, y0 + 30, x + 70, y0 + 30, paint(LIME, a * 0.9, stroke=5))
    for dx in (-56, 56):
        c.drawRoundRect(skia.Rect.MakeXYWH(x + dx - 7, y0 + 8, 14, 22), 5, 5, paint(LIME, a))
    return [(x - 56, y0 + 10), (x + 56, y0 + 10)]


def telegraph_key(c, x, y, a=255):
    base = skia.Path()
    base.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, 380, 60), 10, 10))
    tint(c, base, (120, 70, 40), 160, (3, 3))
    engrave(c, base, LIME, a, 1.6)
    hatch(c, base, 40, 6, 10, LIME, 0.7)
    lev = skia.Path()
    lev.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + 40, y - 46, 320, 22), 8, 8))
    c.save()
    c.rotate(-4, x + 60, y - 30)
    tint(c, lev, (200, 150, 80), 150, (3, 3))
    engrave(c, lev, LIME, a, 1.6)
    knob = skia.Path()
    knob.addOval(skia.Rect.MakeXYWH(x + 300, y - 86, 90, 52))
    c.drawPath(knob, paint((20, 16, 20), a))
    tint(c, knob, (40, 30, 30), 200, (2, 2))
    engrave(c, knob, LIME, a, 1.6)
    c.restore()
    for px in (x + 60, x + 200):
        c.drawCircle(px, y - 10, 16, paint(VOID, a))
        engrave(c, _circle(px, y - 10, 16), LIME, a, 1.4)
    # the spark that jumped at the operator's hand
    rng = np.random.default_rng(9)
    for k in range(5):
        pts = [(x + 200, y - 26)]
        for j in range(8):
            px, py = pts[-1]
            pts.append((px + rng.normal(14, 10), py - rng.normal(12, 8)))
        light(c, polyline(pts), SPARK, 255 - k * 30, 1.6, 1.0)


def _circle(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def telegraph_frame(c, t):
    glass(c)
    stars(c, 200, 13, (0, 0, W, 700), 150, t)
    aurora(c, t, -100, W + 100, 760, 560, 6, 0.75, 360, 2)
    # poles and wires sag across the top, the current in them pulsing blue-white
    tops = []
    for x, y0 in ((150, 560), (560, 510), (970, 470)):
        tops.append(pole(c, x, y0, 1070))
    for w_ in range(2):
        for (a0, b0) in zip(tops, tops[1:]):
            p0, p1 = a0[w_], b0[w_]
            pts = [(lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u) + 40 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 40)]
            engrave(c, polyline(pts), LIME, 200, 1.6)
            light(c, polyline(pts), SPARK, 120, 1.2, 0.8, None)
            for k in range(3):
                u = (t * 0.6 + k / 3 + w_ * 0.17) % 1
                x, y = pts[int(u * 39)]
                bloom_dot(c, x, y, 3, SPARK, 255)
    # a crackle at an insulator
    rng = np.random.default_rng(4)
    ix, iy = tops[1][1]
    for k in range(7):
        pts = [(ix, iy)]
        ang = rng.random() * 6.28
        for j in range(6):
            ang += rng.normal(0, 0.7)
            pts.append((pts[-1][0] + math.cos(ang) * 14, pts[-1][1] + math.sin(ang) * 14))
        light(c, polyline(pts), SPARK, 230, 1.4, 1.1)
    bloom_dot(c, ix, iy, 8, SPARK, 255, 1.5)
    morse_tape(c, "we are working with the auroral current", -20, 1110, W + 20, 255, 860, t)
    telegraph_key(c, 120, 1300)
    tag(c, 70, 290, "BOSTON — PORTLAND", LIME, 255, 22)
    tag(c, 70, 342, "BATTERIES DISCONNECTED", SPARK, 255, 22)
    slide_label(c, 6, "THE TELEGRAPH, 2 SEPT 1859", 70, 150)
    caption_block(c, ["running", "on", "the", "sky"], {3: AUR_G}, y=CAP_Y + 60, size=96, plate=True)


# ---------------------------------------------------------------- 7. the near miss
def city_limb(c, cx, cy, R, a=255, seed=21):
    """The night side of today's Earth: city lights strung together by the power grid."""
    limb = skia.Path()
    limb.addCircle(cx, cy, R)
    c.drawPath(limb, paint(EARTH_SEA, a))
    tint(c, limb, NIGHT, 140, (3, 2), 2)
    rng = np.random.default_rng(seed)
    pts = []
    for k in range(150):                                        # cities: clusters of lights
        th = math.radians(-90 + rng.normal(0, 22))
        rr = R - 20 - rng.random() ** 1.2 * 420
        pts.append((cx + math.cos(th) * rr, cy + math.sin(th) * rr, 0.4 + rng.random()))
    c.save()
    c.clipPath(limb, doAntiAlias=True)
    for i, (x, y, s) in enumerate(pts):                        # the grid: each city wired to its two nearest
        d = sorted(range(len(pts)), key=lambda j: (pts[j][0] - x) ** 2 + (pts[j][1] - y) ** 2)
        for j in d[1:4]:
            if math.hypot(pts[j][0] - x, pts[j][1] - y) < 140:
                c.drawLine(x, y, pts[j][0], pts[j][1], paint(SPARK, a * 0.3, stroke=0.9, blend=ADD))
    for x, y, s in pts:
        for k in range(int(8 * s)):
            bloom_dot(c, x + rng.normal(0, 9 * s), y + rng.normal(0, 5 * s), 0.6 + rng.random() ** 3 * 1.6, CARD,
                      a * (0.5 + 0.5 * rng.random()), 0.7)
    c.restore()
    atm = skia.Path()
    atm.addArc(skia.Rect.MakeXYWH(cx - R, cy - R, 2 * R, 2 * R), 200, 140)
    light(c, atm, SPARK, a * 0.7, 2.0, 0.8)


def satellite(c, x, y, ang, a=255, s=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    body = skia.Path()
    body.addRect(skia.Rect.MakeXYWH(-9, -7, 18, 14))
    c.drawPath(body, paint(VOID, a))
    engrave(c, body, LIME, a, 1.3, 0.3)
    for sg in (-1, 1):
        pnl = skia.Path()
        pnl.addRect(skia.Rect.MakeXYWH(sg * 13 - (34 if sg < 0 else 0), -8, 34, 16))
        c.drawPath(pnl, paint(NIGHT, a))
        hatch(c, pnl, a * 0.8, 5, 90, LIME, 0.8)
        engrave(c, pnl, LIME, a, 1.1, 0.3)
    c.restore()


def nearmiss_frame(c, t):
    """23 July 2012: a cloud as strong as 1859 left the Sun's far side. The region that fired it had faced Earth
    about 9 days earlier, before the Sun's rotation carried it round. It hit the STEREO-A spacecraft instead."""
    glass(c)
    stars(c, 360, 17, (0, 0, W, H), 200, t)
    sx, sy, Rs = 400, 760, 78
    Ro = 470
    orbit = skia.Path()
    orbit.addCircle(sx, sy, Ro)
    c.drawPath(orbit, dashed(paint(SILVER, 150, stroke=1.3), 4, 8))
    e_deg, st_deg = 48.0, 48.0 - 121.0                      # STEREO-A was about 121 degrees ahead of Earth
    ex, ey = sx + math.cos(math.radians(e_deg)) * Ro, sy + math.sin(math.radians(e_deg)) * Ro
    tx, ty = sx + math.cos(math.radians(st_deg)) * Ro, sy + math.sin(math.radians(st_deg)) * Ro
    # the cloud, fired toward STEREO-A
    for k in range(10):
        rr = Ro + 70 - k * 26
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(sx - rr, sy - rr, 2 * rr, 2 * rr), st_deg - 26, 52)
        if k == 0:
            light(c, arc, SUN, 255, 3.2, 1.3)
        else:
            c.drawPath(arc, paint(SUN, 150 * math.exp(-k / 4), stroke=1.3, blend=ADD))
    cone = skia.Path()
    cone.moveTo(sx, sy)
    cone.arcTo(skia.Rect.MakeXYWH(sx - Ro - 70, sy - Ro - 70, 2 * Ro + 140, 2 * Ro + 140), st_deg - 26, 52, False)
    cone.close()
    c.drawPath(cone, paint(SUN, 30, sigma=10, blend=ADD))
    sun_disc(c, sx, sy, Rs, 255, 1.0, 3)
    # the active region now (facing STEREO-A) and nine days earlier (facing Earth), with the Sun's spin
    for deg, a_, lab in ((st_deg, 255, None), (e_deg, 120, "9 DAYS EARLIER")):
        r_ = math.radians(deg)
        px, py = sx + math.cos(r_) * Rs * 0.78, sy + math.sin(r_) * Rs * 0.78
        sunspot(c, px, py, 9, a_, 5, 0.7, deg)
    spin = skia.Path()
    spin.addArc(skia.Rect.MakeXYWH(sx - Rs - 34, sy - Rs - 34, 2 * Rs + 68, 2 * Rs + 68), e_deg - 8, -(e_deg - st_deg) + 16)
    engrave(c, spin, LIME, 220, 1.6)
    r_ = math.radians(st_deg + 8)
    ax, ay = sx + math.cos(r_) * (Rs + 34), sy + math.sin(r_) * (Rs + 34)
    tang = r_ - math.pi / 2
    for s_ in (-1, 1):
        c.drawLine(ax, ay, ax + math.cos(tang + math.pi + s_ * 0.5) * -14, ay + math.sin(tang + math.pi + s_ * 0.5) * -14,
                   paint(LIME, 220, stroke=1.6))
    label(c, "THE SUN TURNS", sx - Rs - 40, sy + Rs + 70, 16, "mono", LIME, 220, "left", 0.12)
    c.drawPath(polyline([(sx, sy), (ex, ey)]), dashed(paint(AUR_R, 170, stroke=1.4), 6, 6))
    label(c, "9 DAYS EARLIER:", (sx + ex) / 2 + 26, (sy + ey) / 2 - 6, 16, "mono_bold", AUR_R, 255, tracking=0.08)
    label(c, "STRAIGHT AT US", (sx + ex) / 2 + 26, (sy + ey) / 2 + 16, 16, "mono_bold", AUR_R, 255, tracking=0.08)
    pr = Ortho(-60, 10, 34, ex, ey)
    earth(c, pr, 1.0, ((sx - ex) / Ro, (sy - ey) / Ro), 1.0)
    label(c, "EARTH", ex + 48, ey + 8, 20, "mono_bold", LIME, 230, tracking=0.2)
    satellite(c, tx, ty, -30, 255, 1.1)
    bloom_dot(c, tx, ty, 6, SUN, 255, 1.4)
    tag(c, tx + 40, ty + 50, "STEREO-A · HIT", SUN, 255, 18)
    tag(c, 70, 300, "23 JULY 2012", SUN, 255, 22)
    tag(c, 70, 352, "AS STRONG AS 1859", LIME, 255, 22)
    city_limb(c, 540, 2700, 1300)
    satellite(c, 220, 1330, 20, 220, 0.8)
    satellite(c, 900, 1400, -15, 220, 0.8)
    slide_label(c, 7, "THE NEAR MISS", 70, 150)
    caption_block(c, ["it", "missed", "us", "by", "nine", "days"], {4: AUR_R, 5: AUR_R}, y=CAP_Y - 120)


FRAMES = [("1_title", title_frame), ("2_sketch", sketch_frame), ("3_crossing", crossing_frame),
          ("4_shield", shield_frame), ("5_aurora", aurora_frame), ("6_telegraph", telegraph_frame),
          ("7_nearmiss", nearmiss_frame)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    want = sys.argv[1] if len(sys.argv) > 1 else ""
    paths = []
    for name, fn in FRAMES:
        p = os.path.join(OUT, f"frame_{name}.png")
        if want in name:
            Image.fromarray(render(fn, 2.0, samples=1)).save(p)
            print(p)
        paths.append(p)
    if not want:
        w, h = 360, 640
        sheet = Image.new("RGB", (4 * (w + 12) + 12, 2 * (h + 12) + 12), (8, 7, 9))
        for i, p in enumerate(paths):
            sheet.paste(Image.open(p).resize((w, h), Image.LANCZOS), (12 + (i % 4) * (w + 12), 12 + (i // 4) * (h + 12)))
        sheet.save(os.path.join(OUT, "style_frames.png"))
