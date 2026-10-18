"""Part 3: Chapter 2, Not a Perfect Ball. The spinning globe squashes (exaggerated) like an orange; the equator is
~21 km farther out; a cross-section shows Chimborazo's summit farther from the centre than Everest's.

  python3 render.py part3 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part3"
VO, _end = schedule(PART, first=3.4, gap=1.35)
DURATION = _end + 2.4
TM = Timing(PART, VO)

SPIN_T = TM.word("B1", "because it spins") - 0.2
ORANGE_T = TM.word("B1", "orange") - 0.5
KM_T = TM.word("B2", "twenty one") - 0.3
SECTION_T = VO["B3"] - 0.6
CHIMB_T = TM.word("B3", "chimborazo") - 0.3
EVEREST_T = TM.word("B3", "everest") - 0.4

NIM_TRACK = Track([(0.0, "neutral", 0.0), (SPIN_T, "focused", 0.4), (ORANGE_T + 0.4, "laugh", 0.35), (KM_T, "shocked", 0.2), (KM_T + 1.2, "focused", 0.4),
                   (CHIMB_T, "cheer", 0.3), (EVEREST_T + 0.8, "smug", 0.4)])
ORANGE_TRACK = Track([(0.0, "neutral", 0.0), (ORANGE_T + 0.3, "shocked", 0.2), (ORANGE_T + 1.2, "worried", 0.4)])


def orange(c, x, y, r, t, sq, p):
    c.save()
    c.translate(x, y)
    c.scale(1 + sq, 1 - sq)
    c.drawCircle(0, 0, r, shaded(radial((-r * 0.35, -r * 0.4), r * 1.5, [(255, 200, 110), (250, 150, 40), (200, 100, 20)])))
    rng = np.random.default_rng(2)
    for k in range(40):
        an, d = rng.uniform(0, 6.28), rng.uniform(0, 0.9) * r
        c.drawCircle(math.cos(an) * d, math.sin(an) * d, r * 0.02, fill((210, 110, 20), 150))
    c.drawPath(poly([(0, -r), (r * 0.25, -r * 1.25), (r * 0.4, -r * 1.1)]), fill((80, 160, 70)))
    c.restore()
    face_rig(c, x, y + r * 0.05, r * 0.8, p, (-0.5, 0.0), 0.0)


def scene_globe(c, t):
    sky(c, t, mood="space")
    sq = 0.17 * smooth(prog(t, SPIN_T, SPIN_T + 1.6))
    gx = lerp(960, 720, smooth(prog(t, ORANGE_T - 0.3, ORANGE_T + 0.6)))
    globe(c, gx, 560, 330, t, rot=t * (0.2 + 1.4 * smooth(prog(t, SPIN_T - 0.5, SPIN_T + 0.5))), tilt=0.0, bulge=sq)
    # spin arrows around the axis
    sa = smooth(prog(t, SPIN_T - 0.4, SPIN_T + 0.2))
    if sa > 0:
        c.drawLine(gx, 560 - 330 * (1 - sq) - 90, gx, 560 + 330 * (1 - sq) + 90, stroke(WHITE, 4, 160 * sa))
        r = skia.Rect.MakeXYWH(gx - 120, 560 - 330 * (1 - sq) - 70, 240, 50)
        c.drawArc(r, 200, 140, False, stroke(GOLD, 6, 230 * sa))
    o = smooth(prog(t, ORANGE_T - 0.3, ORANGE_T + 0.3))
    if o > 0:
        c.saveLayerAlpha(None, int(255 * o))
        orange(c, 1500, 560, 180, t, 0.15 * smooth(prog(t, ORANGE_T, ORANGE_T + 1.0)), ORANGE_TRACK.at(t))
        text(c, "≈", 1200, 590, 90, WHITE, 230, 800)
        c.restore()
    # equator vs pole radius
    k = smooth(prog(t, KM_T - 0.5, KM_T + 0.3))
    if k > 0:
        rx, ry = 330 * (1 + sq), 330 * (1 - sq)
        c.drawLine(gx, 560, gx + rx * k, 560, stroke(GOLD, 6))
        c.drawLine(gx, 560, gx, 560 - ry * k, stroke((150, 210, 255), 6))
        c.drawCircle(gx, 560, 8, fill(WHITE))
        text(c, "EQUATOR", gx + rx * 0.55, 540, 22, GOLD, 255 * k, 800, spacing=3)
        text(c, "POLE", gx - 40, 560 - ry * 0.55, 22, (150, 210, 255), 255 * k, 800, "right", spacing=3)
    big_number(c, "+21 KM", 1500, 250, 100, GOLD, t, KM_T, SECTION_T, sub="FARTHER OUT AT THE EQUATOR")
    if t < SECTION_T:
        def path(tt):
            return 1700 + 15 * math.sin(tt), 860 + 12 * math.sin(tt * 1.2)
        nim(c, t, NIM_TRACK, path, 90, look=(-0.8, -0.3), rim=(150, 200, 255))
    text(c, "(BULGE EXAGGERATED)", 960, 1040, 18, WHITE, 170 * smooth(prog(t, SPIN_T + 1.0, SPIN_T + 1.6)), 800, spacing=3)


def scene_section(c, t):
    """Slice through the Earth: centre at the bottom, the curved surface above; distances drawn from the centre."""
    sky(c, t, mood="day")
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(0.82, 0.82)
    c.translate(-W / 2 + 60, -H / 2 + 330)
    cx, cy, R = 960, 2700, 2050            # centre far below the frame
    k = in_out(prog(t, SECTION_T, CHIMB_T))
    # the crust (a big circle) with a slight bulge on the equator side (right)
    body = skia.Path()
    n = 120
    pts = []
    for i in range(n + 1):
        an = math.radians(-150 + 120 * i / n)
        rr = R + 400 * (i / n)            # bulge: the surface sits farther out towards the equator (right; exaggerated)
        pts.append((cx + math.cos(an) * rr, cy + math.sin(an) * rr))
    body.moveTo(*pts[0])
    for p in pts[1:]:
        body.lineTo(*p)
    body.lineTo(W + 400, H + 400)
    body.lineTo(-400, H + 400)
    body.close()
    c.drawPath(body, shaded(linear((0, 600), (0, H), [(110, 170, 100), (80, 120, 80)])))

    def surface(an_deg):
        i = (an_deg + 150) / 120
        rr = R + 400 * i
        an = math.radians(an_deg)
        return cx + math.cos(an) * rr, cy + math.sin(an) * rr, rr

    def mountain(an_deg, h, rgb, label, ta):
        x, y, rr = surface(an_deg)
        an = math.radians(an_deg)
        tipx, tipy = cx + math.cos(an) * (rr + h), cy + math.sin(an) * (rr + h)
        nx, ny = -math.sin(an), math.cos(an)
        base = 170
        c.drawPath(poly([(x - nx * base, y - ny * base), (tipx, tipy), (x + nx * base, y + ny * base)]), fill(rgb))
        c.drawPath(poly([(tipx, tipy), (tipx - nx * 40 + math.cos(an) * -50, tipy - ny * 40 + math.sin(an) * -50),
                         (tipx + nx * 40 + math.cos(an) * -50, tipy + ny * 40 + math.sin(an) * -50)]), fill(WHITE))
        text(c, label, tipx + 40, tipy - 30, 24, WHITE, 255 * ta, 800, "left", spacing=4)
        return tipx, tipy, rr + h
    ea = smooth(prog(t, EVEREST_T - 0.3, EVEREST_T + 0.3))
    ca = smooth(prog(t, CHIMB_T - 0.3, CHIMB_T + 0.3))
    ex, ey, ed = mountain(-106, 230, (130, 120, 130), "EVEREST · 8,849 M", ea)
    chx, chy, chd = mountain(-76, 160, (150, 130, 120), "CHIMBORAZO · 6,263 M", ca)
    # equator marker
    qx, qy, _ = surface(-62)
    text(c, "TOWARDS THE EQUATOR →", qx - 60, qy + 90, 22, WHITE, 220 * k, 800, "right", spacing=3)
    # reference arc at Everest's summit distance: Chimborazo pokes above it
    if ea > 0:
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(cx - ed, cy - ed, 2 * ed, 2 * ed), -125, 70)
        pe = stroke(WHITE, 3, 180 * ea)
        pe.setPathEffect(skia.DashPathEffect.Make([18, 14], 0))
        c.drawPath(arc, pe)
    # distance lines from the centre (drawn upwards, converging off-screen)
    for (tx, ty, a, rgb) in ((ex, ey, ea, (200, 200, 230)), (chx, chy, ca, GOLD)):
        if a > 0:
            dx, dy = tx - cx, ty - cy
            L = math.hypot(dx, dy)
            sx, sy = cx + dx / L * (L - 900 * a), cy + dy / L * (L - 900 * a)
            c.drawLine(sx, sy, tx, ty, stroke(rgb, 5, 230 * a))
            c.drawCircle(tx, ty, 10, fill(rgb))
    if ca > 0.5:
        c.drawLine(chx, chy, chx, chy - 70, stroke(GOLD, 3))
        c.drawRRect(rrect(chx - 72, chy - 70, 70, 40, 4), fill(GOLD))

    def path(tt):
        return chx + 120 + 15 * math.sin(tt), chy - 140 + 10 * math.sin(tt * 1.4)
    nim(c, t, NIM_TRACK, path, 80, look=(-0.6, 0.4), sparkle_=float(t > CHIMB_T + 0.3))
    chip(c, "CLOSEST POINT TO SPACE", chx, chy - 240, GOLD, t, CHIMB_T + 0.5, EVEREST_T + 0.2)
    c.restore()
    big_number(c, "+2 KM", 560, 170, 96, GOLD, t, EVEREST_T + 0.4, DURATION, sub="CHIMBORAZO'S PEAK: FARTHER FROM EARTH'S CENTRE")


def draw_frame(c, t):
    xfade(c, t, SECTION_T - 0.3, 0.9, scene_globe, scene_section, 0.3)
    chapter_title(c, t, 2, "NOT A PERFECT BALL", (150, 210, 255), 0.2, 2.8)
    fade(c, t, DURATION, 0.5, 0.7)


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (SPIN_T - 0.4, "whoosh_long", 0.7), (SPIN_T + 0.4, "slide", 0.5), (ORANGE_T, "pop", 0.8), (ORANGE_T + 0.6, "bubble", 0.5),
            (KM_T - 0.4, "slide", 0.5), (KM_T, "boom", 0.5), (KM_T + 0.05, "ding", 0.7), (SECTION_T - 0.3, "whoosh_long", 0.7), (CHIMB_T, "pop", 0.8),
            (CHIMB_T + 0.5, "chime", 0.6), (EVEREST_T, "pop", 0.7), (EVEREST_T + 0.4, "boom", 0.5), (EVEREST_T + 0.45, "shine", 0.7)]


MUSIC = dict(
    chords=[(0.0, 48, (0, 7, 12, 16, 19)), (SPIN_T, 50, (0, 7, 12, 14, 19)), (KM_T, 52, (0, 7, 12, 16, 19)), (SECTION_T, 48, (0, 7, 12, 16, 19)),
            (EVEREST_T, 50, (0, 7, 12, 16, 19, 24))],
    plucks=[(VO["B1"], DURATION)], bpm=100, rises=[(SPIN_T, KM_T), (CHIMB_T, EVEREST_T + 0.4)], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
