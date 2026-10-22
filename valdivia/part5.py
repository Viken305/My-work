"""Part 5: the bell. Waves spread round the globe until the whole planet vibrates (the 0S2 'football' mode, hugely
exaggerated), one swing ~54 min, far below hearing, then a cut-away: what the notes revealed inside the Earth."""
from common import *  # noqa: F401,F403

PART = "part5"
VO, _end = schedule(PART, first=0.6, gap=0.6, extra={"D2": 0.4, "D3": 0.5})
TM = Timing(PART, VO)
T_THROUGH = TM.word("D1", "travelled")
T_VIB = TM.word("D1", "vibrate")
T_NOTE = TM.word("D2", "deepest")
T_54 = TM.word("D2", "fifty")
T_LOW = TM.word("D2", "bell")
T_FIRST = TM.word("D3", "first")
T_RING = TM.word("D3", "ring")
T_INSIDE = TM.word("D3", "inside")
DURATION = _end + 1.0
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"energy": RED, "chile": INK, "planet": BRONZE, "heard": BRONZE}))
CX, CY, R = 540, 860, 360


def sphere_ring(c, proj, lon, lat, ang, rgb, a=255, wd=3.0):
    pts = [proj(*destination(lon, lat, math.radians(b), ang)) for b in np.linspace(0, 360, 361)]
    front, back = skia.Path(), skia.Path()
    pf = pb = False
    for x, y, z in pts:
        if z >= 0:
            (front.lineTo if pf else front.moveTo)(x, y)
            pf, pb = True, False
        else:
            (back.lineTo if pb else back.moveTo)(x, y)
            pb, pf = True, False
    c.drawPath(back, dashed(paint(rgb, a * 0.3, stroke=wd * 0.6), 10, 12))
    glow(c, front, rgb, a, wd, 0.5)


def vib(t):
    """Amount the whole globe rings (0..1)."""
    return smooth(prog(t, T_VIB - 0.6, T_VIB + 0.6)) * (1 - 0.5 * smooth(prog(t, T_INSIDE - 0.5, T_INSIDE + 0.5)))


def draw_globe(c, t):
    lon = lerp(-95, -60, prog(t, 0, DURATION))
    proj = Ortho(lon, -12, R, CX, CY)
    v = vib(t)
    # slowed-down swing so the eye can follow it: one swing every 2.6 s stands in for 54 minutes
    ph = math.sin(2 * math.pi * (t - T_VIB) / 2.6) if t > T_VIB - 0.6 else 0.0
    eps = 0.075 * v * ph
    if v > 0:
        dial_rings(c, CX, CY, R, 0.9 * v, (t * 0.3) % 3)
    # the globe itself is drawn stretched in the same mode, so the land deforms with it
    c.save()
    tl = math.radians(-22)
    c.translate(CX, CY)
    c.rotate(math.degrees(tl))
    c.scale(1 + eps, 1 - eps * 0.5)
    c.rotate(-math.degrees(tl))
    c.translate(-CX, -CY)
    globe(c, proj, 1.0, 1.0, key=None)
    # waves spreading through and around the planet from Chile
    if t < T_VIB + 1.2:
        for k in range(4):
            u = prog(t, 0.2 + k * 0.7, T_VIB + 0.4 + k * 0.3)
            if 0 < u < 1:
                sphere_ring(c, proj, *EPI, 0.1 + u * (math.pi - 0.2), RED, 255 * (1 - u ** 3), 3.0)
    ex, ey, ez = proj(*EPI)
    if ez > 0:
        star(c, ex, ey, 14)
    c.restore()
    if v > 0:
        for sgn, a0, dash in ((1, 230, False), (-1, 140, True)):
            pp = paint(BRONZE, a0 * v, stroke=2.4)
            if dash:
                dashed(pp, 14, 10)
            q = mode_outline(CX, CY, R * 1.01, sgn * 0.075 * abs(ph) + 0.002)
            c.drawPath(q, paint(BRONZE, a0 * 0.25 * v, sigma=10, stroke=10, blend=MULT))
            c.drawPath(q, pp)
    return proj


def cutaway(c, t, proj):
    """A wedge cut out of the globe showing the layers the ringing revealed (radii to scale)."""
    w = out_expo(prog(t, T_INSIDE - 0.3, T_INSIDE + 0.9))
    if w <= 0:
        return
    sweep = 100 * w
    wedge = skia.Path()
    wedge.moveTo(CX, CY)
    wedge.arcTo(skia.Rect.MakeXYWH(CX - R, CY - R, 2 * R, 2 * R), -80, sweep, False)
    wedge.close()
    c.save()
    c.clipPath(wedge, doAntiAlias=True)
    c.drawCircle(CX + 6, CY + 10, R, paint(SHADOW, 90, sigma=14))
    for rr, fill, name in ((1.0, mix(SHADE, SEPIA, 0.35), "MANTLE"), (3480 / 6371, mix(BONE, BRONZE, 0.45), "OUTER CORE"),
                           (1220 / 6371, BRONZE, "INNER CORE")):
        c.drawCircle(CX, CY, R * rr, paint(fill))
        c.drawCircle(CX, CY, R * rr, paint(INK, 200, stroke=1.4))
    stipple(c, wedge, 1400, 60, 5)
    c.restore()
    c.drawPath(wedge, paint(INK, 230, stroke=1.8))
    la = appear(t, T_INSIDE + 0.5)
    for (rr, name, sub), ang in zip(((0.78, "MANTLE", "SOLID ROCK"), (0.37, "OUTER CORE", "LIQUID METAL"),
                                     (0.1, "INNER CORE", "SOLID METAL")), (-70, -50, -30)):
        a = math.radians(ang)
        x, y = CX + math.cos(a) * R * rr, CY + math.sin(a) * R * rr
        lx = CX + R + 20
        ly = CY - R * 0.55 + (ang + 70) * 4.2
        c.drawLine(x, y, lx - 8, ly - 8, paint(INK, 220 * la, stroke=1.3))
        c.drawCircle(x, y, 4, paint(INK, 255 * la))
        tab(c, lx - 190, ly - 34, 200, 54, 255 * la)
        label(c, name, lx, ly - 10, 18, "mono_bold", INK, 255 * la, "right", 0.1)
        label(c, sub, lx, ly + 12, 14, "mono", SEPIA, 255 * la, "right", 0.12)


def readouts(c, t):
    fig(c, 6, "THE EARTH RINGING, MAY 1960", 70, 268, size=20)
    a = appear(t, T_NOTE - 0.2) * (1 - appear(t, T_FIRST - 0.2))
    if a > 0:
        card(c, 70, 300, 940, 150, 255 * a)
        label(c, "THE DEEPEST NOTE", 96, 336, 18, "mono_bold", INK, 230 * a, tracking=0.12)
        label(c, "MODE 0S2 · ONE SWING ≈ 54 MIN", 984, 336, 18, "mono", BRONZE, 255 * a, "right", 0.1)
        n = 300
        pts = []
        for i in range(n + 1):
            u = i / n
            pts.append((96 + u * 888, 405 - math.sin(2 * math.pi * u * 3 - t * 2) * 34))
        glow(c, polyline(pts)[0], BRONZE, 255 * a, 2.4, 0.5)
        for k in range(4):
            x = 96 + k * 888 / 3
            c.drawLine(x, 440, x, 448, paint(INK, 200 * a, stroke=1.2))
            label(c, f"{k * 54} MIN", x, 438, 14, "mono", SEPIA, 255 * a, "center")
    ha = appear(t, T_LOW - 0.1) * (1 - appear(t, T_FIRST - 0.2))
    if ha > 0:
        tab(c, 120, 1250, 840, 60, 255 * ha)
        label(c, "WE HEAR 20 – 20,000 HZ", 150, 1290, 22, "mono_bold", INK, 255 * ha)
        label(c, "THIS NOTE: 0.0003 HZ", 930, 1290, 22, "mono_bold", BRONZE, 255 * ha, "right")
    sa = pop(t, T_FIRST + 0.2, 0.35)
    if sa > 0:
        c.save()
        c.translate(540, 340)
        c.rotate(-3)
        k = clamp(sa)
        c.scale(1 + 0.3 * (1 - k), 1 + 0.3 * (1 - k))
        c.drawRect(skia.Rect.MakeXYWH(-330, -44, 660, 76), paint(BONE, 240 * k))
        c.drawRect(skia.Rect.MakeXYWH(-330, -44, 660, 76), paint(BRONZE, 255 * k, stroke=3))
        label(c, "FIRST CLEAR RECORD OF THE EARTH RINGING", 0, 6, 22, "mono_bold", BRONZE, 255 * k, "center", 0.06)
        c.restore()


def draw_frame(c, t):
    paper(c)
    c.save()
    c.translate(0, drum_scroll(t, DURATION, 0.6, 0.6))
    proj = draw_globe(c, t)
    cutaway(c, t, proj)
    readouts(c, t)
    CAP.draw(c, t)
    c.restore()


def post_kw(t):
    return dict(shake=0.0)


def sfx_events():
    return [(0.0, "paper_whoosh", 0.5), (0.3, "deep_rumble", 0.7), (T_VIB - 0.05, "bell", 1.0), (T_VIB + 2.6, "bell", 0.5),
            (T_54, "bell", 0.6), (T_LOW + 0.2, "sub_drop", 0.5), (T_FIRST + 0.2, "stamp", 0.8),
            (T_RING, "bell", 0.7), (T_INSIDE - 0.3, "paper_whoosh", 0.6), (T_INSIDE + 0.4, "paper_slap", 0.5)]


MUSIC = dict(beds=[(0.0, DURATION + 0.4, "wonder", 0.7)])
