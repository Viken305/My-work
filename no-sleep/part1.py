"""Part 1, the hook: an extreme close-up of Sam's eye that will not close while the clock races to 72 hours. The eye
darts around, red veins creep in, the lid fights to stay open twice (it sags, then snaps back up), the frame pulses
with a quickening heartbeat, and on "not there" a shadow figure shows up reflected in the iris. Blink. The title
letters slam in one by one with a shockwave and a glitch.

  python3 render.py part1 [--still 1,5]
"""
from film import *  # noqa: F401,F403

PART = "part1"
SAMPLES = 5
VO, _end = schedule(PART, first=0.35, gap=0.55)
TM = Timing(PART, VO)
DURATION = _end + 0.5

RACE_T0, RACE_T1 = 0.0, TM.end("H1")
GHOST_T = TM.word("H1", "not there") - 0.2
BLINK_T = VO["H2"] - 0.1
TITLE_T = BLINK_T + 0.15
SWEEP_T = TM.word("H2", "hour by hour") - 0.1
OUT_T = DURATION - 0.22
FIGHTS = [TM.word("H1", "awake") + 0.05, TM.word("H1", "brain") - 0.05]       # the lid sags, then snaps back open
BEATS = []                                                                    # heartbeat, quickening
_bt = 0.25
while _bt < BLINK_T - 0.2:
    BEATS.append(_bt)
    _bt += lerp(0.95, 0.5, _bt / BLINK_T)
SACCADES = [(0.0, 0.0, 0.0), (0.7, -0.55, -0.1), (1.35, 0.5, 0.15), (2.2, -0.2, 0.25), (2.9, 0.7, -0.2), (3.6, -0.6, 0.1),
            (4.3, 0.15, 0.0)]

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


def saccade(t):
    """Quick eye darts (70 ms) between fixations, with a tiny overshoot."""
    x = y = 0.0
    for t0, sx, sy in SACCADES:
        if t < t0:
            break
        k = out_back(prog(t, t0, t0 + 0.07), 2.2)
        x, y = lerp(x, sx, k), lerp(y, sy, k)
    return x, y


def fight(t):
    """0..1 extra lid drop: sags slowly for 0.45 s, then snaps open in 0.1 s with an overshoot."""
    v = 0.0
    for t0 in FIGHTS:
        if t0 <= t < t0 + 0.45:
            v = max(v, in_cubic(prog(t, t0, t0 + 0.45)) * 0.9)
        elif t0 + 0.45 <= t < t0 + 0.8:
            u = prog(t, t0 + 0.45, t0 + 0.8)
            v = max(v, 0.9 * (1 - out_back(u, 2.5)))
    return v


def beat(t):
    """Heartbeat pulse 0..1 (lub-dub)."""
    v = 0.0
    for b in BEATS:
        for off, g in ((0.0, 1.0), (0.2, 0.6)):
            d = t - b - off
            if 0 <= d < 0.35:
                v = max(v, g * math.exp(-d * 11))
    return v


def eye(c, t, f):
    """f = fatigue 0..1 (veins, droop, tremble)."""
    jx, jy = 3 * f * math.sin(t * 37), 2 * f * math.cos(t * 41)
    fi = fight(t)
    sx, sy = shake(t, FIGHTS[0] + 0.45, 10, 9)
    sx2, sy2 = shake(t, FIGHTS[1] + 0.45, 12, 9)
    c.save()
    push = in_out(prog(t, 0.0, BLINK_T))
    zs = lerp(1.0, 1.12, push) + 0.012 * beat(t)
    c.translate(CX, CY)
    c.scale(zs, zs)
    c.translate(-CX + jx + sx + sx2 + 6 * math.sin(t * 0.7), -CY + jy + sy + sy2 + 4 * math.cos(t * 0.6))
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
    lx, ly = saccade(t)
    ix, iy = CX + 90 * lx, CY + 5 + 40 * ly
    ir = 170
    c.drawCircle(ix, iy, ir + 10, fillp((0, 0, 0), 60))
    c.drawCircle(ix, iy, ir, shaded(radial((ix, iy), ir, [(40, 90, 150), CYAN, (30, 70, 130)], [0.25, 0.7, 1])))
    c.drawCircle(ix, iy, ir - 5, stroke((14, 30, 70), 12, 200))                   # limbal ring
    c.drawCircle(ix, iy, ir * 0.55, stroke((255, 214, 140), 10, 60))              # warm collarette
    for i in range(48):                                # iris fibres
        a0 = i / 48 * 2 * math.pi
        r0, r1 = ir * 0.45, ir * (0.86 + 0.12 * hsh(i, 2))
        c.drawLine(ix + math.cos(a0) * r0, iy + math.sin(a0) * r0, ix + math.cos(a0) * r1, iy + math.sin(a0) * r1,
                   stroke((200, 240, 255), 2, 70))
    pr = lerp(62, 92, f) * (1 + 0.06 * beat(t))
    c.drawCircle(ix, iy, pr, fillp((6, 8, 16)))
    ga = smooth(prog(t, GHOST_T, GHOST_T + 0.4)) * (1 - smooth(prog(t, BLINK_T - 0.4, BLINK_T)))
    if ga > 0:                                         # a figure reflected in the eye, behind Sam
        shadow_figure(c, ix + 70, iy + 70, 22, ga, t)
        c.drawCircle(ix + 70, iy + 20, 90, fillp(PAPER, 18 * ga))
    c.drawOval(skia.Rect.MakeXYWH(ix - 95, iy - 105, 70, 52), fillp((255, 255, 255), 230))
    c.drawCircle(ix + 60, iy + 52, 12, fillp((255, 255, 255), 150))
    # upper lid: droops and trembles as the hours pass
    drop = HH * (0.18 + 0.55 * f) + 14 * f * math.sin(t * 23) * (0.5 + 0.5 * math.sin(t * 3.1))
    drop = min(HH * 1.9, drop + (HH * 1.9 - drop) * fi)
    lid = skia.Path()
    lid.moveTo(CX - HW - 10, CY - HH * 2.2)
    lid.lineTo(CX + HW + 10, CY - HH * 2.2)
    lid.lineTo(CX + HW + 10, CY)
    lid.quadTo(CX, CY - (HH - drop) * 2, CX - HW - 10, CY)
    lid.close()
    ledge = CY - (HH - drop)                                              # lid edge height at the centre
    c.drawRect(skia.Rect.MakeLTRB(CX - HW, ledge - 20, CX + HW, ledge + 70), grad_v(ledge - 20, ledge + 70, (30, 20, 60), (30, 20, 60), 150, 0))
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
    bt = beat(t)
    if bt > 0:                                         # heartbeat squeezes the edges of the frame
        c.drawPaint(shaded(radial((W / 2, H / 2), W * 1.05, [((0, 0, 0), 0), ((0, 0, 0), 0), ((40, 0, 12), 200 * bt)], [0, 0.5, 1])))


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
    light(c, W / 2, 900, 700, RED, 40 + 30 * smooth(prog(t, TITLE_T, TITLE_T + 0.6)))
    s = "72 HOURS"
    size = 250
    tw = width(s, "display", size)
    f_ = font("display", size)
    land = TITLE_T + 0.05 * len(s) + 0.12
    sx, sy = shake(t, land, 16, 8)
    gl = 1 - smooth(prog(t, land, land + 0.35))        # glitch decays after the last letter lands
    jit = 0.35 + 0.65 * abs(math.sin(t * 23) * math.sin(t * 7.1))
    if t > land:                                       # shockwave ring
        u = prog(t, land, land + 0.7)
        c.drawCircle(W / 2, 830, 120 + 700 * out_cubic(u), stroke(RED, 10 * (1 - u) + 1, 200 * (1 - u)))
    x = W / 2 - tw / 2
    for i, ch in enumerate(s):
        adv = f_.measureText(ch)
        t0 = TITLE_T + i * 0.05
        u = prog(t, t0, t0 + 0.16)
        if u > 0 and ch != " ":
            sc = lerp(2.4, 1.0, out_expo(u))
            al = 255 * smooth(clamp(u * 2.5))
            cxl = x + adv / 2
            c.save()
            c.translate(cxl + sx, 900 - size * 0.36 + sy)
            c.scale(sc, sc)
            c.translate(-cxl, -(900 - size * 0.36))
            sp = (6 + 18 * gl) * jit
            for dx, rgb, aa in ((-sp, CYAN, 0.6), (sp, RED, 0.6), (0, PAPER, 1.0)):
                c.drawString(ch, x + dx, 900, f_, paint(rgb, al * aa, 0 if aa == 1.0 else 2))
            c.restore()
        x += adv
    if gl > 0.05:                                      # glitch slices: horizontal bands knocked sideways
        for k in range(5):
            y0 = 700 + hsh(k, int(t * 30)) * 220
            hgt = 10 + 30 * hsh(k, int(t * 30) + 7)
            dx = (hsh(k, int(t * 30) + 3) - 0.5) * 80 * gl
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(0, y0, W, y0 + hgt))
            c.drawRect(skia.Rect.MakeLTRB(0, y0, W, y0 + hgt), fillp((4, 4, 10)))
            label(c, s, W / 2 - tw / 2 + dx, 900, size, "display", PAPER, 255 * gl)
            c.restore()
    reveal(c, "WITHOUT SLEEP", W / 2, 1000, 50, t, land + 0.05, "mono_bold", RED, 255, "center", tracking=0.32, stagger=0.03, dur=0.3, blur=8)
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
    ev = [(b, "heartbeat", 0.45 + 0.45 * b / BLINK_T) for b in BEATS]
    n, tt = 0, 0.0
    while tt < RACE_T1:                                # ticks speed up as the counter races
        ev.append((tt, "tick", 0.35 + 0.3 * tt / RACE_T1))
        tt += lerp(0.5, 0.09, tt / RACE_T1)
        n += 1
    ev += [(f0 + 0.45, "low_hit", 0.45) for f0 in FIGHTS] + [(f0, "descend", 0.25) for f0 in FIGHTS]
    ev += [(TITLE_T + i * 0.05, "tick", 0.5) for i in range(8) if i != 2]
    ev += [(GHOST_T, "reverse_swell", 0.6),
           (BLINK_T - 0.9, "riser", 0.6), (BLINK_T, "trailer_hit", 0.9), (BLINK_T + 0.02, "sub_drop", 0.7),
           (SWEEP_T, "tick_roll", 0.5), (OUT_T - 0.1, "swish", 0.5)]
    return ev


MUSIC = dict(beds=[(0.0, BLINK_T, "tension", 0.5), (BLINK_T, DURATION, "night0", 0.5)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
