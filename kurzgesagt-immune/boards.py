"""Storyboard key frames for "There Is a War Inside You" + the props the animated parts reuse."""
import math

import numpy as np

from cells import *  # noqa: F401,F403
from cells import _cell_body  # noqa: F401

SKIN_TOP = (250, 205, 180)
SKIN_MID = (232, 150, 140)
SKIN_DEEP = (170, 70, 90)
ACID = (170, 255, 90)
POLLEN = (255, 214, 80)


# ---------------------------------------------------------------- shared helpers
def label(c, s, x, y, rgb=WHITE, size=30, a=255, sub=None):
    if a <= 1:
        return
    text(c, s, x, y, size, rgb, a, 800, spacing=size * 0.18)
    if sub:
        text(c, sub, x, y + size * 1.05, size * 0.58, WHITE, a * 0.8, 800, spacing=size * 0.1)


def tag(c, s, x, y, rgb=ALARM, size=26):
    f = font(size, 800)
    w = f.measureText(s) + size * 1.6 + len(s) * size * 0.12
    c.drawRRect(rrect(x - w / 2, y - size * 1.05, w, size * 1.6, size * 0.8), fill((20, 6, 18), 200))
    c.drawRRect(rrect(x - w / 2, y - size * 1.05, w, size * 1.6, size * 0.8), stroke(rgb, 2.5, 230))
    text(c, s, x, y, size * 0.8, rgb, 255, 800, spacing=size * 0.12)


def arrow(c, x0, y0, x1, y1, rgb=WHITE, w=6, a=230, head=20):
    c.drawLine(x0, y0, x1, y1, stroke(rgb, w, a))
    an = math.atan2(y1 - y0, x1 - x0)
    c.drawPath(poly([(x1 + math.cos(an) * head * 0.6, y1 + math.sin(an) * head * 0.6),
                     (x1 + math.cos(an + 2.5) * head, y1 + math.sin(an + 2.5) * head),
                     (x1 + math.cos(an - 2.5) * head, y1 + math.sin(an - 2.5) * head)]), fill(rgb, a))


def human(c, x, y, h, rgb=(40, 20, 50), outline=TISSUE_HI, a=255, glow_a=0.0):
    """Simple front-facing person, feet at y."""
    c.save()
    c.translate(x, y)
    c.scale(h / 600, h / 600)
    body = skia.Path()
    body.addCircle(0, -525, 65)
    body.addRRect(rrect(-95, -450, 190, 290, 80))
    body.addRRect(rrect(-80, -190, 70, 190, 32))
    body.addRRect(rrect(10, -190, 70, 190, 32))
    body.addRRect(rrect(-140, -430, 55, 240, 27))
    body.addRRect(rrect(85, -430, 55, 240, 27))
    if glow_a > 0:
        c.drawPath(body, blur(fill(outline, glow_a * a / 255), 40))
    c.drawPath(body, shaded(linear((0, -590), (0, 0), [lighten(rgb, 0.15), rgb])))
    c.drawPath(body, stroke(outline, 6, a))
    c.restore()


def skin_wall(c, x0, y0, w, h, t, cut=0.0, cut_x=None):
    """Skin cross-section: flat dead cells stacked on top, living cells below. cut 0..1 opens a wound at cut_x."""
    cut_x = cut_x if cut_x is not None else x0 + w / 2
    c.save()
    if cut > 0:   # wound: a V-shaped gap
        gap = skia.Path()
        gap.moveTo(cut_x - 140 * cut, y0 - 10)
        gap.lineTo(cut_x + 140 * cut, y0 - 10)
        gap.lineTo(cut_x + 20 * cut, y0 + h * 0.85 * cut)
        gap.lineTo(cut_x - 20 * cut, y0 + h * 0.85 * cut)
        gap.close()
        c.clipPath(gap, skia.ClipOp.kDifference, True)
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), shaded(linear((0, y0), (0, y0 + h), [SKIN_TOP, SKIN_MID, SKIN_DEEP], [0, 0.35, 1])))
    rng = np.random.default_rng(5)
    rows = 9
    for row in range(rows):
        frac = row / rows
        ch = lerp(10, 46, frac ** 1.3)
        yy = y0 + sum(lerp(10, 46, (r / rows) ** 1.3) for r in range(row))
        if yy > y0 + h:
            break
        cw = lerp(150, 60, frac)
        off = rng.uniform(0, cw)
        x = x0 - off
        while x < x0 + w:
            ww = cw * rng.uniform(0.8, 1.2)
            rgb = mix(SKIN_TOP, SKIN_DEEP, frac * 0.9)
            c.drawRRect(rrect(x + 2, yy + 2, ww - 4, ch - 4, min(ch, ww) * 0.4), fill(lighten(rgb, 0.12), 230))
            c.drawRRect(rrect(x + 2, yy + 2, ww - 4, ch - 4, min(ch, ww) * 0.4), stroke(darken(rgb, 0.25), 2, 160))
            if frac > 0.35:
                c.drawCircle(x + ww / 2, yy + ch / 2, ch * 0.18, fill(darken(rgb, 0.4), 150))
            x += ww
    c.restore()
    if cut > 0:
        light(c, cut_x, y0 + h * 0.4 * cut, 300 * cut, (255, 60, 80), 160 * cut)


def vessel(c, x0, y, w, h, t, leak=0.0, flow=160.0, wall=TISSUE_HI, a=255, n=26):
    """Horizontal blood vessel (tube) with red blood cells flowing. leak 0..1 widens it and opens gaps."""
    hh = h * (1 + 0.35 * leak)
    top, bot = y - hh / 2, y + hh / 2
    c.drawRect(skia.Rect.MakeXYWH(x0, top, w, hh), shaded(linear((0, top), (0, bot), [(110, 14, 30, ), (170, 30, 44), (110, 14, 30)])))
    rng = np.random.default_rng(8)
    for k in range(n):
        u = (rng.random() + t * flow / w * rng.uniform(0.8, 1.2)) % 1.0
        rbc(c, x0 + u * w, y + rng.uniform(-0.32, 0.32) * hh, h * 0.15, t, rng.uniform(0.1, 0.8), a, rng.random() * 9)
    for s in (-1, 1):
        yy = y + s * hh / 2
        seg = 70
        for k in range(int(w / seg) + 1):
            gx = x0 + k * seg
            gap = leak * 18 * (0.5 + 0.5 * math.sin(k * 1.7))
            c.drawRRect(rrect(gx + gap / 2, yy - 14, seg - gap, 28, 14), shaded(linear((0, yy - 14), (0, yy + 14), [lighten(wall, 0.2), darken(wall, 0.3)])))


def lymph_node(c, x, y, s, t, a=255, glow=0.0):
    """Bean-shaped lymph node with follicles."""
    p = blob_path(x, y, [s * (1.0 + 0.18 * math.cos(2 * (2 * math.pi * i / 24)) - (0.22 if i in (5, 6, 7) else 0)) for i in range(24)], 0)
    light(c, x, y, s * 2.2, (90, 200, 210), (60 + 120 * glow) * a / 255)
    c.drawPath(p, shaded(radial((x - s * 0.3, y - s * 0.3), s * 1.6, [(120, 220, 220), (40, 120, 150), (20, 50, 90)])))
    c.drawPath(p, stroke((160, 255, 240), s * 0.03, 200))
    for k in range(7):
        an = k / 7 * 6.28 + 0.4
        c.drawCircle(x + math.cos(an) * s * 0.62, y + math.sin(an) * s * 0.5, s * 0.16, fill((170, 250, 240), 90))


def body_map(c, x, y, h, t, nodes_a=255, path_k=0.0):
    """Person outline with the lymphatic network and nodes (neck, armpits, groin)."""
    human(c, x, y, h, rgb=(30, 14, 40), outline=(120, 220, 230), glow_a=40)
    sc = h / 600
    nodes = [(-40, -440), (40, -440), (-110, -390), (110, -390), (-55, -200), (55, -200), (0, -330)]
    for i, (nx, ny) in enumerate(nodes):
        for j in range(i + 1, len(nodes)):
            if abs(nodes[i][1] - nodes[j][1]) < 160:
                c.drawLine(x + nx * sc, y + ny * sc, x + nodes[j][0] * sc, y + nodes[j][1] * sc, stroke((90, 200, 210), 3, 90))
        light(c, x + nx * sc, y + ny * sc, 30, (120, 255, 230), 160 * nodes_a / 255)
        c.drawCircle(x + nx * sc, y + ny * sc, 7, fill((180, 255, 240), nodes_a))


def infected_cell(c, x, y, r, t, k=0.0, a=255):
    """A body cell taken over by viruses (sad face). k 0..1: self-destruct (shrinks into fragments)."""
    if a <= 1:
        return
    if k < 0.6:
        s = 1 - 0.5 * smooth(prog(k, 0, 0.6))
        p = _cell_body(c, x, y, r * s, t, (230, 150, 140), 1.3)
        c.save()
        c.clipPath(p, doAntiAlias=True)
        for i in range(5):
            an = i / 5 * 6.28 + t * 0.3
            virus(c, x + math.cos(an) * r * 0.5 * s, y + math.sin(an) * r * 0.45 * s, r * 0.13 * s, t)
        c.restore()
        c.drawPath(p, stroke((150, 80, 90), r * 0.03))
        face(c, x, y - r * 0.25 * s, r * 0.8 * s, t, "worried", (0, 0), True, 0.4)
    else:
        u = prog(k, 0.6, 1.0)
        rng = np.random.default_rng(4)
        for i in range(14):
            an = rng.uniform(0, 6.28)
            d = r * (0.2 + 0.9 * out_cubic(u)) * rng.uniform(0.5, 1)
            c.drawCircle(x + math.cos(an) * d, y + math.sin(an) * d, r * 0.1 * (1 - u * 0.6), fill((230, 150, 140), 255 * (1 - u)))


def pollen(c, x, y, s, t, a=255):
    for k in range(18):
        an = k / 18 * 6.28 + t * 0.3
        c.drawCircle(x + math.cos(an) * s, y + math.sin(an) * s, s * 0.16, fill(darken(POLLEN, 0.15), a))
    c.drawCircle(x, y, s, shaded(radial((x - s * 0.3, y - s * 0.3), s * 1.4, [lighten(POLLEN, 0.35), POLLEN, darken(POLLEN, 0.35)])))
    for k in range(6):
        an = k / 6 * 6.28
        c.drawCircle(x + math.cos(an) * s * 0.5, y + math.sin(an) * s * 0.5, s * 0.12, fill(darken(POLLEN, 0.3), 160))


def wanted(c, x, y, w, t, a=255, germ="virus"):
    """Wanted poster with a germ portrait (vaccine metaphor)."""
    h = w * 1.3
    c.save()
    c.translate(x, y)
    c.rotate(-4 + 1.5 * math.sin(t * 1.2))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 10, -h / 2 + 14, w, h), blur(fill((0, 0, 0), 100), 12))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), shaded(linear((0, -h / 2), (0, h / 2), [(246, 228, 190), (220, 196, 150)])))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 + w * 0.05, -h / 2 + w * 0.05, w * 0.9, h - w * 0.1), stroke((120, 80, 50), w * 0.012, 200))
    text(c, "WANTED", 0, -h * 0.32, w * 0.17, (90, 50, 30), a, 800, spacing=w * 0.02)
    c.drawRect(skia.Rect.MakeXYWH(-w * 0.32, -h * 0.25, w * 0.64, w * 0.56), fill((60, 40, 50)))
    if germ == "virus":
        virus(c, 0, -h * 0.25 + w * 0.28, w * 0.15, t)
    else:
        bacterium(c, 0, -h * 0.25 + w * 0.28, w * 0.16, t, 0)
    text(c, "HARMLESS COPY", 0, h * 0.27, w * 0.075, (90, 50, 30), a, 800, spacing=w * 0.01)
    text(c, "FOR TRAINING ONLY", 0, h * 0.36, w * 0.06, (120, 70, 40), a, 800, spacing=w * 0.008)
    c.restore()


def response_graph(c, x0, y0, w, h, k1=1.0, k2=1.0, a=255):
    """Antibody level over time: slow first response vs fast big second response."""
    c.drawLine(x0, y0 + h, x0 + w, y0 + h, stroke(WHITE, 3, 200 * a / 255))
    c.drawLine(x0, y0, x0, y0 + h, stroke(WHITE, 3, 200 * a / 255))
    text(c, "IMMUNE RESPONSE", x0 - 20, y0 - 24, 20, WHITE, 200 * a / 255, 800, "left", spacing=3)
    text(c, "TIME", x0 + w, y0 + h + 40, 20, WHITE, 200 * a / 255, 800, "right", spacing=3)

    def curve(x_start, delay, peak, width, k, rgb, lab):
        p = skia.Path()
        n = 60
        for i in range(int(n * k) + 1):
            u = i / n
            xx = x_start + u * width
            v = peak * math.exp(-((u - delay) / 0.16) ** 2) if u > delay else peak * math.exp(-((u - delay) / (0.1 + 0.5 * delay)) ** 2)
            (p.moveTo if i == 0 else p.lineTo)(xx, y0 + h - v * h)
        c.drawPath(p, stroke(rgb, 6, a))
        if k > 0.6:
            text(c, lab, x_start + width * delay, y0 + h - peak * h - 24, 20, rgb, a * smooth(prog(k, 0.6, 1)), 800, spacing=3)
    curve(x0 + 10, 0.55, 0.32, w * 0.42, k1, (150, 220, 255), "1ST TIME · ~1 WEEK")
    curve(x0 + w * 0.52, 0.22, 0.92, w * 0.46, k2, (255, 214, 120), "2ND TIME · DAYS")


# ================================================================ panels
def p1a(c, t):
    tissue(c, t, a=0.5)
    human(c, 960, 930, 700, rgb=(36, 14, 44), outline=(255, 90, 110), glow_a=60)
    rng = np.random.default_rng(2)
    for k in range(26):
        an = rng.uniform(0, 6.28)
        d = rng.uniform(380, 640)
        x, y = 960 + math.cos(an + t * 0.1) * d * 1.3, 560 + math.sin(an + t * 0.1) * d * 0.8
        if k % 3 == 0:
            virus(c, x, y, 24, t)
        else:
            bacterium(c, x, y, 28, t, math.degrees(an) + 180, face_on=False)
    label(c, "YOU ARE UNDER ATTACK", 960, 1020, (255, 120, 130), 34)


def p1b(c, t):
    tissue(c, t, a=0.4)
    c.drawRect(skia.Rect.MakeXYWH(0, 640, W, 440), shaded(linear((0, 640), (0, H), [(225, 150, 140), (150, 60, 84)])))
    c.drawLine(0, 640, W, 640, stroke((255, 210, 190), 6, 200))
    for k, (x, ang) in enumerate([(300, 120), (620, 60), (980, 110), (1320, 70), (1640, 100)]):
        bacterium(c, x, 540 - 40 * (k % 2), 52, t + k, -ang, mood="scared" if k % 2 else "grin")
        c.drawLine(x, 610, x + 60 * math.cos(math.radians(-ang)), 610 + 60 * math.sin(math.radians(-ang)), stroke(WHITE, 3, 120))
        sparkle(c, x, 632, 30, 230, (255, 250, 230))
    label(c, "ALMOST ALL OF THEM FAIL", 960, 860, WHITE, 36)


def p1c(c, t):
    cam = Cam()
    tissue(c, t, cam)
    for k, (x, y) in enumerate([(240, 400), (360, 640), (1560, 420), (1700, 650)]):
        neutrophil(c, x, y, 60, t + k, "determined", (0.4 if x < 960 else -0.4, 0), seed=k)
    t_cell(c, 560, 420, 58, t, "helper", "determined", (0.3, 0.2))
    t_cell(c, 1380, 420, 58, t, "killer", "determined", (-0.3, 0.2))
    b_cell(c, 1360, 720, 56, t, "determined", (-0.3, -0.2))
    max_cell(c, 960, 560, 170, t, "determined", (0, 0.1), arms=((160, 0.25), (20, 0.25)))
    foreground(c, t, cam)
    text(c, "THERE IS A", 960, 150, 44, WHITE, 255, 800, spacing=10)
    text(c, "WAR INSIDE YOU", 960, 250, 92, (255, 120, 130), 255, 800, spacing=10)
    label(c, "NEARLY 2 TRILLION IMMUNE CELLS", 960, 1000, MAX_BODY, 28)


def p2a(c, t):
    tissue(c, t, a=0.4)
    skin_wall(c, 0, 520, W, 560, t)
    for k, x in enumerate((360, 900, 1500)):
        bacterium(c, x, 450, 56, t + k, 90 - 15 * k, mood="sneaky")
    label(c, "SKIN", 1600, 300, SKIN_TOP, 46, sub="LAYER UPON LAYER OF DEAD CELLS")


def p2b(c, t):
    tissue(c, t, a=0.5)
    # tears / saliva: enzyme snipping a bacterium
    for i, (x, title, sub) in enumerate([(330, "TEARS & SALIVA", "ENZYMES"), (960, "MUCUS", "STICKY TRAP"), (1590, "STOMACH", "ACID")]):
        c.drawRRect(rrect(x - 280, 170, 560, 640, 40), fill((20, 4, 16), 170))
        c.drawRRect(rrect(x - 280, 170, 560, 640, 40), stroke(TISSUE_HI, 3, 160))
        label(c, title, x, 880, WHITE, 30, sub=sub)
    bacterium(c, 330, 480, 60, t, 20, mood="scared")
    for k in range(5):  # enzyme "pac-men" biting
        an = k / 5 * 6.28
        ex, ey = 330 + math.cos(an) * 150, 480 + math.sin(an) * 150
        mo = 0.5 + 0.5 * abs(math.sin(t * 6 + k))
        c.drawPath(_pac(ex, ey, 22, math.degrees(an) + 180, mo), fill((120, 220, 255)))
    # mucus strands
    for k in range(7):
        p = skia.Path()
        p.moveTo(700, 260 + k * 75)
        p.cubicTo(860, 220 + k * 80, 1060, 320 + k * 70, 1220, 270 + k * 75)
        c.drawPath(p, blur(stroke((170, 240, 120), 26, 110), 4))
        c.drawPath(p, stroke((210, 255, 170), 6, 120))
    for k, (x, y) in enumerate([(880, 360), (1030, 520), (920, 640)]):
        bacterium(c, x, y, 36, t + k, 30 * k, mood="scared", wiggle=3)
    # acid pool
    c.drawRect(skia.Rect.MakeXYWH(1320, 560, 540, 250), shaded(linear((0, 560), (0, 810), [ACID, darken(ACID, 0.6)])))
    for k in range(12):
        bx = 1350 + (k * 47) % 500
        by = 800 - ((t * 60 + k * 37) % 240)
        c.drawCircle(bx, by, 6 + k % 4, stroke(lighten(ACID, 0.4), 3, 200))
    bacterium(c, 1590, 560, 46, t, 10, mood="scared", a=200)
    text(c, "pH ≈ 2", 1590, 720, 40, INK, 230, 800)


def _pac(x, y, r, ang, mo):
    p = skia.Path()
    p.moveTo(x, y)
    p.arcTo(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), ang + 30 * mo, 360 - 60 * mo, False)
    p.close()
    return p


def p2c(c, t):
    tissue(c, t, a=0.4)
    skin_wall(c, 0, 520, W, 560, t, cut=1.0, cut_x=960)
    rng = np.random.default_rng(9)
    for k in range(18):
        x = 960 + rng.uniform(-200, 200)
        y = 380 + rng.uniform(-200, 420)
        bacterium(c, x, y, 26, t + k, 90 + rng.uniform(-40, 40), face_on=k % 3 == 0)
    label(c, "ONE TINY CUT", 1500, 300, (255, 120, 130), 40, sub="AND THOUSANDS OF BACTERIA RUSH IN")


def p3a(c, t):
    tissue(c, t)
    vessel(c, 0, 820, W, 220, t, leak=1.0)
    for k, (x, y) in enumerate([(600, 360), (1100, 300), (1450, 420)]):
        c.drawPath(blob_path(x, y, [70 * (1 + 0.15 * math.sin(i * 2.3)) for i in range(9)]), fill((210, 120, 130), 220))
        face(c, x, y - 8, 70, t + k, "shocked", (0, 0), True, k)
        mast_alarm(c, x, y, 150, t, (t * 0.4 + k * 0.3) % 1)
    for k, (s, rgb) in enumerate([("RED", (255, 90, 90)), ("SWOLLEN", (255, 160, 120)), ("WARM", ALARM)]):
        tag(c, s, 560 + k * 400, 120, rgb, 30)


def p3b(c, t):
    tissue(c, t)
    vessel(c, 0, 900, W, 220, t, leak=0.8)
    for k in range(6):
        x = 260 + k * 280
        y = 760 - (k % 3) * 120
        neutrophil(c, x, y, 62, t + k, "determined", (0, -0.6), seed=k)
        if k % 2 == 0:
            arrow(c, x, y - 90, x + 40, y - 190, (255, 200, 220), 5, 160, 16)
    for k in range(5):
        bacterium(c, 300 + k * 330, 200 + (k % 2) * 60, 30, t + k, 180 + k * 20)
    label(c, "NEUTROPHILS", 960, 1030, NEUTRO, 30)


def p3c(c, t):
    tissue(c, t)
    neutrophil(c, 960, 520, 90, t, burst=0.62, seed=2)
    rng = np.random.default_rng(1)
    for k in range(10):
        an = rng.uniform(0, 6.28)
        d = rng.uniform(150, 360)
        bacterium(c, 960 + math.cos(an) * d, 520 + math.sin(an) * d * 0.8, 26, t, math.degrees(an), mood="scared", wiggle=0.3)
    neutrophil(c, 380, 760, 70, t, "shocked", (0.8, -0.3), seed=4)
    label(c, "A NET OF DNA", 960, 990, (220, 170, 255), 34, sub="NEUTROPHILS FIGHT TO THE DEATH")


def p3d(c, t):
    cam = Cam()
    tissue(c, t, cam)
    bacterium(c, 1270, 470, 46, t, 200, mood="scared", wiggle=3)
    max_cell(c, 900, 540, 230, t, "hungry", (0.9, -0.2), gulp=(-12, 0.85), belly=((-0.35, 0.45, 0.2, 0.3), (-0.1, 0.6, 0.18, 0.7)))
    foreground(c, t, cam)
    label(c, "MACROPHAGE", 900, 960, MAX_BODY, 34, sub="SWALLOWS BACTERIA WHOLE")


def p4a(c, t):
    tissue(c, t)
    for k in range(9):
        bacterium(c, 200 + k * 190, 300 + 220 * math.sin(k * 1.9), 30, t + k, k * 40)
    neutrophil(c, 300, 760, 60, t, "worried", (0.5, -0.3))
    max_cell(c, 1600, 760, 110, t, "worried", (-0.5, -0.4))
    dendritic(c, 960, 600, 90, t, "determined", (0.3, -0.3), carry=GERM)
    label(c, "DENDRITIC CELL", 960, 1000, DENDRI, 34, sub="COLLECTS PIECES OF THE ENEMY")


def p4b(c, t):
    c.drawPaint(shaded(radial((W / 2, H / 2), W, [(20, 30, 60), (6, 8, 22)])))
    draw_texture(c, tex_lymph(), 960, 540, 1.8, t, 120, skia.BlendMode.kPlus)
    body_map(c, 520, 1020, 880, t)
    lymph_node(c, 1360, 520, 230, t, glow=0.5)
    for k in range(5):
        dendritic(c, 1040 + k * 50, 520 + 40 * math.sin(k), 20, t + k)
    c.drawLine(560, 380, 1130, 500, stroke((120, 255, 230), 4, 140))
    label(c, "LYMPH NODE", 1360, 860, (150, 255, 240), 34, sub="THE IMMUNE SYSTEM'S MILITARY BASE")


def p4c(c, t):
    c.drawPaint(shaded(radial((W / 2, H / 2), W, [(20, 46, 70), (6, 12, 26)])))
    draw_texture(c, tex_lymph(), 960, 540, 2.0, t, 100, skia.BlendMode.kPlus)
    dendritic(c, 400, 560, 100, t, "happy", (0.5, 0), carry=GERM)
    keys = [(255, 120, 120), (120, 255, 160), (160, 160, 255), (255, 200, 90), GERM, (255, 120, 255), (120, 220, 255), (255, 160, 90)]
    for k, kc in enumerate(keys):
        x, y = 860 + (k % 4) * 260, 330 + (k // 4) * 380
        match = kc == GERM
        t_cell(c, x, y, 70, t + k, "helper", "shocked" if match else "neutral", (-0.6, 0), key=kc, seed=k)
        if match:
            light(c, x, y, 220, GERM, 140)
    label(c, "FINDING THE ONE THAT MATCHES", 960, 1010, (150, 255, 240), 30)


def p5a(c, t):
    tissue(c, t, tint=(30, 60, 120))
    # big lock & key
    c.drawCircle(560, 520, 210, shaded(radial((500, 460), 300, [lighten(HELPER, 0.4), HELPER, darken(HELPER, 0.4)])))
    cup = skia.Path()
    cup.addArc(skia.Rect.MakeXYWH(700, 440, 160, 160), 90, 180)
    c.drawLine(760, 520, 700, 520, stroke(darken(HELPER, 0.3), 26))
    c.drawPath(cup, stroke(lighten(HELPER, 0.3), 22))
    c.drawPath(blob_path(830, 520, [60 * (1 + 0.15 * math.sin(k * 2.1)) for k in range(7)]), fill(GERM))
    light(c, 800, 520, 160, GERM, 120)
    face(c, 540, 480, 210, t, "shocked", (0.8, 0))
    for k in range(9):
        t_cell(c, 1220 + (k % 3) * 200, 280 + (k // 3) * 220, 70, t + k, "helper", "determined", (-0.4, 0), key=GERM, seed=k)
    label(c, "ONE LOCK, ONE KEY", 560, 860, (150, 200, 255), 32)
    label(c, "COPIES ITSELF", 1420, 1000, (150, 200, 255), 32, sub="AN ARMY OF THOUSANDS")


def p5b(c, t):
    tissue(c, t)
    infected_cell(c, 1180, 520, 220, t)
    for k, (x, y) in enumerate([(560, 360), (500, 700)]):
        t_cell(c, x, y, 90, t + k, "killer", "determined", (0.8, 0), key=VIRUS, seed=k)
    arrow(c, 680, 520, 920, 520, (255, 150, 140), 8, 220, 26)
    label(c, "KILLER T CELLS", 560, 980, KILLER, 32, sub="INFECTED CELLS ARE ORDERED TO SELF-DESTRUCT")


def p5c(c, t):
    tissue(c, t)
    b_cell(c, 520, 540, 150, t, "determined", (0.8, 0), plasma=1.0)
    for k in range(18):
        u = (t * 0.5 + k / 18) % 1.0
        x = 720 + u * 1100
        y = 540 + math.sin(k * 2.4) * 260 * u
        antibody(c, x, y, 40, 90 + k * 40 + t * 200)
    label(c, "PLASMA CELL", 520, 860, BCELL, 34, sub="THOUSANDS OF ANTIBODIES EVERY SECOND")


def p5d(c, t):
    cam = Cam()
    tissue(c, t, cam)
    for k, (x, y) in enumerate([(1250, 330), (1450, 620), (1200, 780)]):
        bacterium(c, x, y, 44, t + k, 150 + k * 30, mood="scared", tag=1.0, wiggle=0.3)
    max_cell(c, 700, 560, 210, t, "happy", (0.8, 0), arms=((-10, 0.7), (30, 0.5)))
    foreground(c, t, cam)
    label(c, "TAGGED FOR DESTRUCTION", 960, 1000, ANTIBODY, 32)


def p6a(c, t):
    tissue(c, t, a=0.7)
    rng = np.random.default_rng(3)
    for k in range(14):
        x, y = rng.uniform(150, 1770), rng.uniform(200, 880)
        t_cell(c, x, y, 40, t + k, "helper" if k % 2 else "killer", "sleepy" if False else "neutral", a=60, seed=k)
    t_cell(c, 760, 520, 90, t, "helper", "happy", memory=True)
    b_cell(c, 1160, 540, 90, t, "happy", memory=True)
    label(c, "MEMORY CELLS", 960, 980, (255, 230, 150), 36, sub="A FEW STAY BEHIND, FOR DECADES")


def p6b(c, t):
    tissue(c, t, a=0.5)
    c.drawRRect(rrect(220, 180, 1480, 720, 30), fill((14, 4, 14), 200))
    response_graph(c, 320, 260, 1280, 520)
    label(c, "THE SECOND TIME, THE ARMY IS READY", 960, 990, (255, 214, 120), 30)


def p6c(c, t):
    tissue(c, t)
    wanted(c, 960, 500, 380, t)
    t_cell(c, 520, 620, 90, t, "helper", "determined", (0.8, -0.2), memory=True)
    b_cell(c, 1400, 620, 90, t, "determined", (-0.8, -0.2), memory=True)
    label(c, "VACCINES", 960, 980, (150, 255, 200), 36, sub="A HARMLESS WANTED POSTER")


def p7a(c, t):
    tissue(c, t)
    for k, (x, y) in enumerate([(700, 400), (1000, 620), (1250, 380)]):
        pollen(c, x, y, 70, t + k)
    for k, (x, y) in enumerate([(380, 360), (420, 700), (1560, 520)]):
        neutrophil(c, x, y, 70, t + k, "shocked", (0.6 if x < 960 else -0.6, 0), seed=k)
    label(c, "SOMETIMES IT OVERREACTS", 960, 1000, POLLEN, 32, sub="ALLERGIES · AUTOIMMUNE DISEASES")


def p7b(c, t):
    c.drawPaint(fill((60, 8, 22)))
    vessel(c, -50, 540, W + 100, 720, t, flow=200, n=40)
    max_cell(c, 760, 560, 130, t, "happy", (0.6, 0), vel=(300, 0))
    neutrophil(c, 1100, 450, 60, t, "happy", (0.6, 0))
    t_cell(c, 1260, 650, 60, t, "helper", "happy", (0.6, 0))
    label(c, "QUIETLY WINNING · EVERY DAY", 960, 1000, WHITE, 32)


def p7c(c, t):
    tissue(c, t, a=0.6)
    human(c, 480, 1000, 640, rgb=(36, 14, 44), outline=MAX_BODY, glow_a=40)
    c.drawRRect(rrect(412, 880, 54, 32, 10), fill((255, 220, 180)))     # plaster on the knee
    max_cell(c, 1260, 420, 150, t, "happy", (-0.5, 0), arms=((-60, 0.5),))
    text(c, "THERE'S A WAR INSIDE YOU", 1260, 740, 44, WHITE, 255, 800, spacing=6)
    text(c, "AND YOU'RE WINNING", 1260, 830, 64, MAX_BODY, 255, 800, spacing=8)


PANELS = {
    1: ("HOOK", "0:00–0:25", [
        (p1a, "H1", "\"Right now, as you watch this, you are under attack.\"", "A person glows with a red alert outline while bacteria and viruses circle, looking for a way in."),
        (p1b, "H2", "\"Bacteria, viruses and fungi are trying to get inside you, every single day. Almost all of them fail.\"", "Close on the skin surface: microbes bounce off with sparks."),
        (p1c, "H3", "\"...an army of nearly two trillion cells... This is your immune system.\"", "Reveal of the army with MAX in front, neutrophils, T and B cells; title THERE IS A WAR INSIDE YOU."),
    ]),
    2: ("THE WALLS", "0:25–1:00", [
        (p2a, "W1", "\"Your skin is a tough barrier of dead cells, stacked layer upon layer...\"", "Skin cross-section builds layer by layer; sneaky bacteria try to dig in and fail."),
        (p2b, "W2", "\"Tears and saliva contain enzymes... Sticky mucus traps intruders... stomach acid...\"", "Three guard posts: enzymes biting a bacterium, mucus strands trapping germs, a bubbling acid pool."),
        (p2c, "W3", "\"But walls can be breached. One tiny cut, and thousands of bacteria rush in.\"", "The wall tears open in a red flash; a flood of bacteria pours in. Hard cut to silence."),
    ]),
    3: ("FIRST RESPONDERS", "1:00–1:52", [
        (p3a, "F1", "\"...damaged cells sound the alarm... red, swollen and warm.\"", "Damaged cells pulse alarm rings; the blood vessel below swells and its wall opens gaps."),
        (p3b, "F2", "\"Out of the blood pour the first responders: neutrophils.\"", "Neutrophils squeeze through the vessel wall and charge upward toward the bacteria."),
        (p3c, "F3", "\"Some even burst open, casting out sticky nets of DNA...\"", "A neutrophil explodes into a glowing web that freezes the bacteria in place."),
        (p3d, "F4", "\"Macrophages, like Max here, swallow bacteria whole...\"", "Hero shot: MAX opens wide and engulfs a terrified bacterium; others dissolve in its belly."),
    ]),
    4: ("THE MESSENGER", "1:52–2:22", [
        (p4a, "M1", "\"...too many, or too clever... the dendritic cell.\"", "The battle goes badly; a dendritic cell grabs a fragment of the enemy and holds it up."),
        (p4b, "M2", "\"...travels through the lymphatic system to the nearest lymph node...\"", "Map of the body's lymph network; the route lights up to a bean-shaped lymph node, the base."),
        (p4c, "M3", "\"...searching for the rare cells that can recognise this exact enemy.\"", "Inside the base: T cells with different coloured locks; one matches and lights up."),
    ]),
    5: ("SPECIAL FORCES", "2:22–3:13", [
        (p5a, "S1", "\"...like a lock that fits only one kind of key... copying itself... an army of thousands.\"", "Close-up of the receptor clicking onto the fragment, then the helper T cell multiplies across the frame."),
        (p5b, "S2", "\"...killer T cells... order them to self-destruct.\"", "Killer T cells corner a virus-filled body cell, which crumbles into harmless fragments."),
        (p5c, "S3", "\"...plasma cells that pump out antibodies, thousands of them every second.\"", "A plasma cell fires streams of Y-shaped antibodies like a factory."),
        (p5d, "S4", "\"Antibodies... tag them for destruction. Max loves that.\"", "Bacteria covered in antibodies slow down; MAX happily reaches out and grabs them."),
    ]),
    6: ("MEMORY", "3:13–3:50", [
        (p6a, "R1", "\"...most of the soldiers die off. But a few stay behind: memory cells.\"", "The army fades away; two memory cells remain, each with a glowing star."),
        (p6b, "R2", "\"...the army is back within days, often before you even feel sick.\"", "Graph: a slow, small first response versus a fast, huge second response."),
        (p6c, "R3", "\"...vaccines... a harmless wanted poster...\"", "A WANTED poster of the germ is shown to memory cells, who study it."),
    ]),
    7: ("YOU'RE WINNING", "3:50–4:20", [
        (p7a, "O1", "\"Sometimes it overreacts to harmless things like pollen...\"", "Neutrophils panic at harmless pollen grains; a nod to allergies and autoimmune disease."),
        (p7b, "O2", "\"But most of the time, it quietly wins, every hour of every day...\"", "A calm patrol: MAX and friends cruise along a blood vessel."),
        (p7c, "O3", "\"...there's a war going on inside you. And you're winning.\"", "Pull out to a person with a plaster on their knee; MAX waves; end card."),
    ]),
}
