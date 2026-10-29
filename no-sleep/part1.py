"""Part 1, the hook: an extreme close-up of Sam's eye that will not close while the clock races to 72 hours. Red
veins creep in, the lid trembles, and on "not there" a shadow figure shows up reflected in the iris. Blink. Title.

  python3 render.py part1 [--still 1,5]
"""
from film import *  # noqa: F401,F403

PART = "part1"
SAMPLES = 3
VO, _end = schedule(PART, first=0.35, gap=0.55)
TM = Timing(PART, VO)
DURATION = _end + 0.5

RACE_T0, RACE_T1 = 0.0, TM.end("H1")
GHOST_T = TM.word("H1", "not there") - 0.2
BLINK_T = VO["H2"] - 0.1
TITLE_T = BLINK_T + 0.15
SWEEP_T = TM.word("H2", "hour by hour") - 0.1
OUT_T = DURATION - 0.22

CAPS = Captions(TM, anchors={"H1": (W / 2, 1430), "H2": (W / 2, 1430)}, emph={"three", "days", "not", "there", "hour"},
                accent=CYAN)
CX, CY, HW, HH = W / 2, 860, 470, 235
_r = np.random.default_rng(7)
VEINS = []
for side in (-1, 1):
    for k in range(9):
        x0 = CX + side * HW * _r.uniform(0.75, 0.98)
        y0 = CY + _r.uniform(-0.45, 0.45) * HH * 0.6
        pts = [(x0, y0)]
        ang = math.atan2(CY - y0, CX - x0) + _r.uniform(-0.5, 0.5)
        for j in range(7):
            ang += _r.uniform(-0.45, 0.45)
            step = _r.uniform(18, 34)
            pts.append((pts[-1][0] + math.cos(ang) * step, pts[-1][1] + math.sin(ang) * step))
        VEINS.append((pts, _r.uniform(0, 0.8)))


def hour_at(t):
    return 72 * in_cubic(prog(t, RACE_T0, RACE_T1)) ** 0.8


def eye(c, t, f):
    """f = fatigue 0..1 (veins, droop, tremble)."""
    jx, jy = 3 * f * math.sin(t * 37), 2 * f * math.cos(t * 41)
    c.save()
    c.translate(jx, jy)
    c.drawRect(skia.Rect.MakeWH(W, H), shaded(radial((CX - 120, CY - 260), 1300, [(150, 140, 222), (104, 92, 186), (34, 28, 74)], [0, 0.45, 1])))
    # dark circle under the eye
    c.drawArc(skia.Rect.MakeXYWH(CX - HW * 0.9, CY + HH * 0.2, HW * 1.8, HH * 1.4), 15, 150, False,
              blur(stroke(SAM_DK, 70, 140 * f), 30))
    almond = skia.Path()
    almond.moveTo(CX - HW, CY)
    almond.quadTo(CX, CY - HH * 2, CX + HW, CY)
    almond.quadTo(CX, CY + HH * 2, CX - HW, CY)
    almond.close()
    c.save()
    c.clipPath(almond, doAntiAlias=True)
    c.drawPaint(shaded(radial((CX, CY), HW, [(236, 234, 245), (214, 206, 226), mix((180, 160, 196), (220, 120, 140), f)], [0, 0.6, 1])))
    for pts, delay in VEINS:                           # veins creep in with the hours
        k = clamp((f - delay * 0.6) / 0.5)
        if k <= 0:
            continue
        n = max(2, int(len(pts) * k))
        vp = path_of(pts[:n])
        c.drawPath(vp, stroke((214, 60, 80), 3.2, 200 * k))
    look = 18 * math.sin(t * 0.9) * (1 - f)
    ix, iy = CX + look, CY + 5
    ir = 170
    c.drawCircle(ix, iy, ir + 10, fillp((0, 0, 0), 60))
    c.drawCircle(ix, iy, ir, shaded(radial((ix, iy), ir, [(40, 90, 150), CYAN, (30, 70, 130)], [0.25, 0.7, 1])))
    for i in range(48):                                # iris fibres
        a0 = i / 48 * 2 * math.pi
        r0, r1 = ir * 0.45, ir * (0.86 + 0.12 * hsh(i, 2))
        c.drawLine(ix + math.cos(a0) * r0, iy + math.sin(a0) * r0, ix + math.cos(a0) * r1, iy + math.sin(a0) * r1,
                   stroke((200, 240, 255), 2, 70))
    pr = lerp(62, 92, f) * (1 + 0.04 * math.sin(t * 6))
    c.drawCircle(ix, iy, pr, fillp((6, 8, 16)))
    ga = smooth(prog(t, GHOST_T, GHOST_T + 0.4)) * (1 - smooth(prog(t, BLINK_T - 0.4, BLINK_T)))
    if ga > 0:                                         # a figure reflected in the eye, behind Sam
        shadow_figure(c, ix + 70, iy + 70, 22, ga, t)
        c.drawCircle(ix + 70, iy + 20, 90, fillp(PAPER, 18 * ga))
    c.drawOval(skia.Rect.MakeXYWH(ix - 95, iy - 105, 70, 52), fillp((255, 255, 255), 230))
    c.drawCircle(ix + 60, iy + 52, 12, fillp((255, 255, 255), 150))
    # upper lid: droops and trembles as the hours pass
    drop = HH * (0.18 + 0.55 * f) + 14 * f * math.sin(t * 23) * (0.5 + 0.5 * math.sin(t * 3.1))
    lid = skia.Path()
    lid.moveTo(CX - HW - 10, CY - HH * 2.2)
    lid.lineTo(CX + HW + 10, CY - HH * 2.2)
    lid.lineTo(CX + HW + 10, CY)
    lid.quadTo(CX, CY - (HH - drop) * 2, CX - HW - 10, CY)
    lid.close()
    c.drawPath(lid, shaded(linear((0, CY - HH * 2), (0, CY), [(150, 140, 222), (118, 106, 200)])))
    edge = skia.Path()
    edge.moveTo(CX - HW, CY)
    edge.quadTo(CX, CY - (HH - drop) * 2, CX + HW, CY)
    c.drawPath(edge, stroke(INK, 10, 230))
    c.restore()
    c.drawPath(almond, stroke((52, 42, 110), 10, 220))
    for i in range(11):                                # lashes on the lid edge
        u = (i + 0.5) / 11
        ex = CX - HW + 2 * HW * u
        ey = CY - (HH - drop) * 4 * u * (1 - u) * 1.0
        ang = math.radians(-90 + (u - 0.5) * 70)
        c.drawLine(ex, ey, ex + math.cos(ang) * 46, ey + math.sin(ang) * 46, stroke(INK, 7, 230))
    c.restore()


def race_counter(c, t, a=1.0):
    hrs = hour_at(t)
    hh = int(hrs)
    mm = int((hrs - hh) * 60)
    ss = int(((hrs - hh) * 3600) % 60)
    txt = f"{hh:02d}:{mm:02d}:{ss:02d}"
    tw = width(txt, "mono_bold", 104)
    acc = CYAN if hrs < 24 else (AMBER if hrs < 48 else RED)
    c.drawRRect(rrect(W / 2 - tw / 2 - 40, 1150, tw + 80, 190, 30), blur(fillp((10, 8, 30), 150 * a), 30))
    label(c, txt, W / 2 - tw / 2, 1250, 104, "mono_bold", acc, 120 * a, sigma=18)
    label(c, txt, W / 2 - tw / 2, 1250, 104, "mono_bold", PAPER, 255 * a)
    s = "HOURS AWAKE"
    label(c, s, W / 2 - width(s, "mono", 26, 0.3) / 2, 1306, 26, "mono", ASH, 230 * a, tracking=0.3)


def title(c, t):
    c.drawPaint(fillp((4, 4, 10)))
    u = prog(t, TITLE_T, TITLE_T + 0.4)
    sc = lerp(1.25, 1.0, out_expo(u))
    g = 0.6 + 0.4 * math.sin(t * 17) * math.sin(t * 5.3)
    c.save()
    c.translate(W / 2, 900)
    c.scale(sc, sc)
    s = "72 HOURS"
    tw = width(s, "display", 250)
    for dx, rgb, al in ((-9 * g, CYAN, 150), (9 * g, RED, 150), (0, PAPER, 255)):
        label(c, s, -tw / 2 + dx, 0, 250, "display", rgb, al * smooth(u * 2))
    c.restore()
    reveal(c, "WITHOUT SLEEP", W / 2, 1000, 50, t, TITLE_T + 0.25, "mono_bold", RED, 255, "center", tracking=0.32, stagger=0.025, dur=0.35, blur=8)
    sweep = in_out(prog(t, SWEEP_T, SWEEP_T + 1.3))
    hud(c, t, 72 * sweep, CYAN if sweep < 0.34 else (AMBER if sweep < 0.67 else RED), smooth(prog(t, TITLE_T + 0.2, TITLE_T + 0.5)))


def draw_frame(c, t):
    if t < BLINK_T:
        f = clamp(hour_at(t) / 72)
        eye(c, t, f)
        race_counter(c, t)
    else:
        title(c, t)
    blink(c, t, BLINK_T, 0.2)
    if t > OUT_T:
        blink(c, t, DURATION, 0.22)
    CAPS.draw(c, t)


def POST(t):
    f = clamp(hour_at(t) / 72) if t < BLINK_T else 0.4
    return fatigue_post(f, split=4 * f if t < BLINK_T else 0)


def sfx_events():
    ev = [(0.0, "heartbeat", 0.5)]
    n, tt = 0, 0.0
    while tt < RACE_T1:                                # ticks speed up as the counter races
        ev.append((tt, "tick", 0.35 + 0.3 * tt / RACE_T1))
        tt += lerp(0.5, 0.09, tt / RACE_T1)
        n += 1
    ev += [(1.6, "heartbeat", 0.6), (2.6, "heartbeat", 0.75), (3.4, "heartbeat", 0.9), (GHOST_T, "reverse_swell", 0.6),
           (BLINK_T - 0.9, "riser", 0.6), (BLINK_T, "trailer_hit", 0.9), (BLINK_T + 0.02, "sub_drop", 0.7),
           (SWEEP_T, "tick_roll", 0.5), (OUT_T - 0.1, "swish", 0.5)]
    return ev


MUSIC = dict(beds=[(0.0, BLINK_T, "tension", 0.5), (BLINK_T, DURATION, "night0", 0.5)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
