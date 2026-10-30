"""PARK THAT MOLECULE! The game-show set shared by part3 (the trick) and part6 (the crash).

A marquee-lit stage; on its floor a brain cell's membrane with four receptor "parking spots". Adenosine (blue, sleepy,
with its sugar ring) parks there and sends the sleepy signal down into the cell; caffeine (orange, wide awake, the
same double ring) takes the spots and blocks it. The SLEEPY-O-METER at the top shows how tired you feel.
"""
from tv import *  # noqa: F401,F403

SPOTS = [210, 420, 660, 870]
MEM_Y = 1000
DOCK_Y = 922


def stage(c, t, a=255, rgb=MAGENTA):
    gradient_bg(c, (30, 6, 60), (70, 10, 90))
    for k, x in enumerate((180, 900)):                         # spotlights sweeping
        ang = math.radians(90 + 18 * math.sin(t * 0.8 + k * 2))
        p = path_of([(x, 380), (x + 900 * math.cos(ang - 0.12), 380 + 900 * math.sin(ang - 0.12)),
                     (x + 900 * math.cos(ang + 0.12), 380 + 900 * math.sin(ang + 0.12))], True)
        pp = fillp(WHITE, 26)
        pp.setBlendMode(skia.BlendMode.kPlus)
        c.drawPath(p, pp)
    # marquee bulbs around the set, chasing
    x0, y0, x1, y1 = 40, 410, 1040, 1180
    pts = []
    n = 64
    per = 2 * ((x1 - x0) + (y1 - y0))
    for i in range(n):
        d = i / n * per
        if d < x1 - x0:
            pts.append((x0 + d, y0))
        elif d < (x1 - x0) + (y1 - y0):
            pts.append((x1, y0 + d - (x1 - x0)))
        elif d < 2 * (x1 - x0) + (y1 - y0):
            pts.append((x1 - (d - (x1 - x0) - (y1 - y0)), y1))
        else:
            pts.append((x0, y1 - (d - 2 * (x1 - x0) - (y1 - y0))))
    c.drawRRect(rrect(x0, y0, x1 - x0, y1 - y0, 30), stroke(mix(rgb, BLACK, 0.3), 26, a))
    for i, (x, y) in enumerate(pts):
        on = (i + int(t * 10)) % 3 == 0
        c.drawCircle(x, y, 9, fillp(YELLOW if on else (120, 90, 40), a))
        if on:
            light(c, x, y, 34, YELLOW, 90 * a / 255)
    # below the set: stage floor
    c.drawRect(skia.Rect.MakeLTRB(0, 1200, W, H), grad_v(1200, H, (50, 10, 70), (10, 0, 20)))
    for k in range(12):
        c.drawLine(0, 1220 + k * k * 6, W, 1220 + k * k * 6, stroke(MAGENTA, 2, 60))


def meter(c, t, v, a=255):
    """SLEEPY-O-METER: green -> red bar with a needle; v 0..1."""
    if a <= 1:
        return
    label(c, "SLEEPY-O-METER", 80, 470, 40, "righteous", WHITE, a)
    x0, x1, y = 80, 1000, 492
    sh = skia.GradientShader.MakeLinear([(x0, 0), (x1, 0)], [col(LIME, a), col(YELLOW, a), col(RED, a)])
    c.drawRRect(rrect(x0, y, x1 - x0, 40, 20), skia.Paint(AntiAlias=True, Shader=sh))
    c.drawRRect(rrect(x0, y, x1 - x0, 40, 20), stroke(WHITE, 4, a))
    nx = lerp(x0 + 20, x1 - 20, clamp(v)) + 3 * math.sin(t * 23) * (v > 0.85)
    c.drawPath(path_of([(nx - 18, y - 22), (nx + 18, y - 22), (nx, y + 8)], True), fillp(WHITE, a))
    c.drawRect(skia.Rect.MakeLTRB(nx - 4, y, nx + 4, y + 40), fillp(WHITE, a))
    label(c, "zZ", 1000, 470, 40, "righteous", SKY, a, "right")


def membrane(c, t, a=255):
    c.drawRect(skia.Rect.MakeLTRB(60, MEM_Y, 1020, 1165), fillp((90, 20, 70), a))
    for k in range(48):                                          # lipid heads
        x = 70 + k * 20
        c.drawCircle(x, MEM_Y + 6 + 2 * math.sin(t * 3 + k), 8, fillp(PINK, a))
        c.drawCircle(x, MEM_Y + 46 + 2 * math.sin(t * 3 + k + 1), 8, fillp(PINK, a))
        c.drawLine(x, MEM_Y + 12, x, MEM_Y + 40, stroke(PINK, 2, 0.6 * a))
    for x in SPOTS:                                              # receptor sockets
        p = skia.Path()
        p.moveTo(x - 72, 870)
        p.lineTo(x - 72, 950)
        p.quadTo(x - 72, 990, x - 32, 990)
        p.lineTo(x + 32, 990)
        p.quadTo(x + 72, 990, x + 72, 950)
        p.lineTo(x + 72, 870)
        c.drawPath(p, stroke(TEAL, 34, a))
        c.drawPath(p, stroke(mix(TEAL, WHITE, 0.4), 10, a))
        c.drawRect(skia.Rect.MakeLTRB(x - 72, MEM_Y, x + 72, MEM_Y + 56), fillp(TEAL, a))
    label(c, "BRAIN CELL", 540, 1150, 40, "vt", PINK, 0.9 * a, "center")


def signal(c, t, x, kind, a=255):
    """Under a spot: the sleepy signal (blue Zz drifting into the cell) or a red BLOCKED cross."""
    if a <= 1:
        return
    if kind == "sleepy":
        for k in range(2):
            u = (t * 0.9 + k * 0.5) % 1
            label(c, "Z", x - 10 + 14 * math.sin(u * 6), MEM_Y + 80 + 60 * u, 40 - 10 * u, "righteous", SKY, a * (1 - u))
    else:
        c.drawLine(x - 30, MEM_Y + 70, x + 30, MEM_Y + 120, stroke(RED, 12, a))
        c.drawLine(x + 30, MEM_Y + 70, x - 30, MEM_Y + 120, stroke(RED, 12, a))


def adenosine(c, x, y, s, t, a=255, face="sleepy", rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    hexa, pent = purine(c, 0, 0, s, SKY, 0, 1)
    c.drawPath(path_of(hexa, True), fillp(mix(SKY, BLACK, 0.3), 0.9 * a))
    c.drawPath(path_of(pent, True), fillp(mix(SKY, BLACK, 0.3), 0.9 * a))
    purine(c, 0, 0, s, SKY, a, 0.2 * s)
    # the sugar ring that caffeine lacks
    rx, ry = s * 1.45, s * 1.6
    c.drawLine(pent[4][0], pent[4][1], rx, ry - s * 0.5, stroke(SKY, 0.18 * s, a))
    ring = [(rx + s * 0.55 * math.cos(math.radians(-90 + 72 * i)), ry + s * 0.55 * math.sin(math.radians(-90 + 72 * i))) for i in range(5)]
    c.drawPath(path_of(ring, True), fillp(mix(SKY, WHITE, 0.4), a))
    c.drawPath(path_of(ring, True), stroke(SKY, 0.12 * s, a))
    ex = -s * 0.78
    for dx in (-s * 0.28, s * 0.28):
        if face == "sleepy":
            c.drawLine(ex + dx - s * 0.14, -s * 0.05, ex + dx + s * 0.14, -s * 0.05, stroke(WHITE, s * 0.1, a))
        else:
            c.drawCircle(ex + dx, -s * 0.05, s * 0.12, fillp(WHITE, a))
    c.restore()


def caffeine(c, x, y, s, t, a=255, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    light(c, 0, 0, s * 2.4, ORANGE, 70 * a / 255)
    hexa, pent = purine(c, 0, 0, s, ORANGE, 0, 1)
    c.drawPath(path_of(hexa, True), fillp(mix(ORANGE, BLACK, 0.25), 0.95 * a))
    c.drawPath(path_of(pent, True), fillp(mix(ORANGE, BLACK, 0.25), 0.95 * a))
    for (px, py), (dx, dy) in ((hexa[1], (-0.5, 0.6)), (hexa[3], (-0.6, -0.5)), (pent[3], (0.6, 0.5))):   # methyl groups
        c.drawLine(px, py, px + dx * s * 0.7, py + dy * s * 0.7, stroke(ORANGE, 0.16 * s, a))
        c.drawCircle(px + dx * s * 0.75, py + dy * s * 0.75, s * 0.16, fillp(YELLOW, a))
    purine(c, 0, 0, s, ORANGE, a, 0.2 * s)
    ex = -s * 0.78
    for dx in (-s * 0.28, s * 0.28):
        c.drawCircle(ex + dx, -s * 0.05, s * 0.17, fillp(WHITE, a))
        c.drawCircle(ex + dx + s * 0.04 * math.sin(t * 9), -s * 0.05, s * 0.07, fillp(BLACK, a))
    c.restore()


def arrive(t, t0, x0, y0, x1, y1, d=0.6):
    """Position of a molecule flying in at t0 and settling into place with a small bounce."""
    u = prog(t, t0, t0 + d)
    return lerp(x0, x1, out_cubic(u)), lerp(y0, y1, out_back(u, 1.4))
