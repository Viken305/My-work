"""Part 1: cold open. Frame 1 is a white-hot flash: the kilonova blasts outward (shockwaves, gold streaks) and holds for
~5 s; it rewinds back into two neutron stars; they smash (a short flash, not a second full explosion); the Sun and Earth
are "not yet"; one gold nugget wraps itself into a ring; title.

  python3 render.py part1 [--still 1,5]
"""
from story import *  # noqa: F401,F403

PART = "part1"
VO, _end = schedule(PART, first=0.5, gap=0.75, extra={"H2": 1.7})
DURATION = _end + 2.0
TM = Timing(PART, VO)

BLAST_END = VO["H2"] - 0.7                  # the explosion holds until here
REWIND = (BLAST_END, VO["H2"] + 0.35)
SMASH_T = TM.word("H2", "smashed") + 0.25
BEFORE_T = TM.word("H2", "long before") - 0.1
ROAD_T = TM.word("H2", "and getting") - 0.2
RING_T = TM.word("H2", "into your hand") - 0.1
WRAP = (RING_T - 0.2, RING_T + 0.9)         # the nugget stretches into the ring band
TITLE_T = _end + 0.3                       # after the last caption has cleared
CX, CY = W / 2, 860
RING_Y, RING_S = 1220, 0.9

CAPS = Captions(TM, anchors={"H1": (W / 2, 1300), "H2": (W / 2, 380)},
                heroes={"GOLD": (W / 2, 1530, 210)}, hero_once=True,
                reacts={"SMASHED": (lambda c, x, y, t, a, s: react_collide(c, x, y, t, a, s, "SMASHED"), W / 2, 1350, 120)})

_rng = np.random.default_rng(17)
DEBRIS = [(float(a), float(v), float(s), int(h)) for a, v, s, h in
          zip(_rng.uniform(0, 6.283, 90), _rng.uniform(380, 1250, 90), _rng.uniform(5, 15, 90), _rng.integers(0, 3, 90))]
SHOCKS = (0.0, 0.55, 1.9)                   # start times of the expanding shockwave rings


def blast(c, tb):
    """The kilonova at blast time tb (s since detonation): core, shockwaves, gold streaks flying out, glowing shell."""
    core = math.exp(-tb * 0.9)
    light(c, CX, CY, 900, (255, 150, 80), 110 + 80 * core)
    light(c, CX, CY, 170 + 230 * core, (255, 225, 170), 255 * (0.2 + 0.8 * core))
    kilonova(c, CX, CY, 760, tb, 0.14 + 0.3 * out_cubic(clamp(tb / 5.0)), seed=5)
    for s0 in SHOCKS:                       # shockwaves: thin, bright, fast, fading
        u = tb - s0
        if 0 < u < 2.6:
            r = 1500 * out_cubic(clamp(u / 2.6))
            fa = (1 - clamp(u / 2.6)) ** 1.5
            c.drawCircle(CX, CY, r, stroke((255, 235, 200), 16 * fa + 3, 230 * fa))
            c.drawCircle(CX, CY, r * 0.94, stroke((255, 170, 90), 40 * fa, 90 * fa))
    for an, v, sz, hue in DEBRIS:           # gold streaks: burst out fast, then coast
        d = v * (1 - math.exp(-tb * 2.2)) + v * 0.06 * tb
        sp = v * 2.2 * math.exp(-tb * 2.2) + v * 0.06
        x, y = CX + math.cos(an) * d, CY + math.sin(an) * d
        tail = min(sp * 0.09, 260)
        p = skia.Paint(AntiAlias=True, Shader=linear((x, y), (x - math.cos(an) * tail, y - math.sin(an) * tail),
                                                     [(GOLD_HI, 230), (GOLD, 0)]), Style=skia.Paint.kStroke_Style, StrokeWidth=sz * 0.9)
        p.setBlendMode(skia.BlendMode.kPlus)
        c.drawLine(x, y, x - math.cos(an) * tail, y - math.sin(an) * tail, p)
        gold_sphere(c, x, y, sz * (0.8 + 0.2 * hue), (255, 200, 140))
    for i in range(6):                      # twinkles in the cloud
        an = i * 1.1 + 0.4
        k = 0.5 + 0.5 * math.sin(tb * 4 + i * 2)
        sparkle4(c, CX + math.cos(an) * 330, CY + math.sin(an) * 300, 26 * k, 230 * k)


def ring_arc(c, cx, cy, s, k):
    """Ring band growing from its front (bottom) point in both directions; k = 1 is the whole ring."""
    outer = skia.Rect.MakeXYWH(cx - 330 * s, cy - 120 * s, 660 * s, 240 * s)
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=70 * s * (0.5 + 0.5 * k), StrokeCap=skia.Paint.kRound_Cap,
                   Shader=linear((cx - 330 * s, cy - 120 * s), (cx + 330 * s, cy + 120 * s),
                                 [GOLD_DEEP, GOLD_HI, GOLD, GOLD_MID, GOLD_HI, GOLD_DEEP], [0, 0.2, 0.4, 0.6, 0.8, 1]))
    sweep = 359.9 * k
    arc = skia.Path()
    arc.addArc(outer, 90 - sweep / 2, sweep)
    c.drawPath(arc, p)


def draw_frame(c, t):
    if t < REWIND[1]:
        zoom = lerp(1.0, 1.16, in_out(prog(t, 0.0, BLAST_END)))
    else:
        zoom = lerp(1.0, 1.06, in_out(prog(t, REWIND[1], SMASH_T)))
    sh = 30 * math.exp(-t * 3.0) + sum(10 * math.exp(-(t - s0) * 5) for s0 in SHOCKS[1:] if t > s0)
    sh += 18 * math.exp(-(t - SMASH_T) * 5) if t > SMASH_T else 0
    cam = Cam(sh * math.sin(t * 61), sh * math.cos(t * 53), zoom)
    space_bg(c, t, cam, warm=0.6 * (1 - smooth(prog(t, REWIND[0], REWIND[1]))))
    cam.push(c, 1.0)
    c.translate(-W / 2, -H / 2)
    if t < REWIND[0]:
        blast(c, t)
    elif t < REWIND[1]:                     # rewind: the blast plays backwards and collapses (no flash at the end)
        u = prog(t, REWIND[0], REWIND[1])
        c.saveLayerAlpha(None, int(255 * (1 - smooth(prog(u, 0.55, 1.0)))))
        blast(c, lerp(BLAST_END, 0.8, in_cubic(u)))
        c.restore()
        for i in range(26):
            an = i / 26 * 6.28 + 0.2
            d1, d2 = 700 * (1 - u) + 40, 700 * (1 - u) + 260
            c.drawLine(CX + math.cos(an) * d2, CY + math.sin(an) * d2, CX + math.cos(an) * d1, CY + math.sin(an) * d1,
                       stroke(GOLD_HI, 4, 200 * math.sin(math.pi * u)))
    # the two neutron stars: appear out of the rewind, spiral, smash
    if REWIND[1] - 0.4 < t < SMASH_T + 0.1:
        pre = clamp((SMASH_T - t) / (SMASH_T - REWIND[1] + 0.4))
        rr = 30 + 340 * pre ** 0.7
        ph = 9 * (1 - pre) ** 0.5 + t * 0.4
        a = smooth(prog(t, REWIND[1] - 0.4, REWIND[1]))
        for ring_i in range(4):
            rk = (t * 0.9 + ring_i / 4) % 1.0
            c.drawOval(skia.Rect.MakeXYWH(CX - 700 * rk, CY - 280 * rk, 1400 * rk, 560 * rk), stroke((150, 140, 255), 3, 110 * (1 - rk) * a))
        for s in (0, math.pi):
            neutron_star(c, CX + math.cos(ph + s) * rr, CY + math.sin(ph + s) * rr * 0.42, 30, t, 255 * a)
    if SMASH_T < t < SMASH_T + 1.2:         # the smash: one short flash and a single ring, not a second full explosion
        u = prog(t, SMASH_T, SMASH_T + 1.2)
        light(c, CX, CY, 500 * (1 - u * 0.5), (255, 230, 190), 255 * (1 - u) ** 2)
        c.drawCircle(CX, CY, 900 * out_cubic(u), stroke((255, 235, 200), 10 * (1 - u) + 2, 220 * (1 - u)))
        if t < SMASH_T + 0.15:
            c.drawPaint(add(HOTWHITE, 200 * (1 - prog(t, SMASH_T, SMASH_T + 0.15))))
    if SMASH_T < t < ROAD_T + 0.3:          # a little gold dust left drifting from the smash point
        u = t - SMASH_T
        da = 1 - smooth(prog(t, ROAD_T - 0.6, ROAD_T + 0.3))
        for an, v, sz, _ in DEBRIS[:30]:
            d = v * 0.35 * (1 - math.exp(-u * 1.5))
            gold_sphere(c, CX + math.cos(an) * d, CY + math.sin(an) * d, sz * 0.5, (255, 200, 140), 255 * da)
        light(c, CX, CY, 120, GOLD, 160 * da)
    # "long before the Earth or the Sun existed": dotted outlines of the Sun and Earth, not there yet
    nb = smooth(prog(t, BEFORE_T, BEFORE_T + 0.4)) * (1 - smooth(prog(t, ROAD_T - 0.3, ROAD_T + 0.2)))
    if nb > 0:
        for (x, y, r, lab) in ((310, 1420, 120, "SUN"), (770, 1450, 70, "EARTH")):
            pe = stroke(WHITE, 4, 200 * nb)
            pe.setPathEffect(skia.DashPathEffect.Make([14, 12], t * 20))
            c.drawCircle(x, y, r, pe)
            text(c, lab, x, y + 12, 28, WHITE, 220 * nb, 800, spacing=4)
            text(c, "NOT YET", x, y + r + 50, 22, (255, 170, 130), 230 * nb, 800, spacing=3)
    # the long road: one gold nugget travels down to the ring's front edge, then stretches into the band
    if t > ROAD_T - 0.3:
        fx, fy = CX, RING_Y + 120 * RING_S          # front (bottom) point of the ring
        u = in_out(prog(t, ROAD_T - 0.3, WRAP[0]))
        nx, ny = CX, lerp(CY, fy, u) - 140 * math.sin(math.pi * u)
        wk = in_out(prog(t, WRAP[0], WRAP[1]))
        ga = smooth(prog(t, WRAP[0] - 0.8, WRAP[0]))  # faint ghost of the ring it is about to become
        pe = stroke(GOLD_HI, 3, 90 * ga * (1 - wk))
        pe.setPathEffect(skia.DashPathEffect.Make([16, 14], t * 30))
        c.drawOval(skia.Rect.MakeXYWH(CX - 330 * RING_S, RING_Y - 120 * RING_S, 660 * RING_S, 240 * RING_S), pe)
        if wk > 0:
            ring_arc(c, CX, RING_Y, RING_S, wk)
        light(c, nx, ny, 160, GOLD, 120 * (1 - wk))
        if wk < 1:
            for j in range(8):
                uj = max(0.0, u - j * 0.02)
                c.drawCircle(CX, lerp(CY, fy, uj) - 140 * math.sin(math.pi * uj), 10 - j, add(GOLD_HI, (160 - j * 18) * (1 - wk)))
            gold_sphere(c, nx, ny, lerp(28, 44, u) * (1 - 0.85 * wk), (140, 110, 170))
        if t > WRAP[1]:
            ring(c, CX, RING_Y, RING_S, t, "front", 255 * smooth(prog(t, WRAP[1], WRAP[1] + 0.2)))
            light(c, CX, RING_Y, 420, GOLD, 140 * math.exp(-(t - WRAP[1]) * 2))
            sparkle4(c, CX + 250, RING_Y - 50, 34 * (0.7 + 0.3 * math.sin(t * 5)), 255)
            sparkle4(c, CX - 270, RING_Y + 40, 24, 220)
    cam.pop(c)
    if t < 0.45:                            # frame 1: white-hot
        c.drawPaint(add(HOTWHITE, 255 * (1 - smooth(prog(t, 0.0, 0.45)))))
    if t < TITLE_T + 0.2:
        CAPS.draw(c, t)
    ta = smooth(prog(t, TITLE_T, TITLE_T + 0.4))
    if ta > 0:
        tr = lerp(24, 8, out_cubic(prog(t, TITLE_T, TITLE_T + 1.2)))
        text(c, "HOW EARTH", W / 2, 330, 90, WHITE, 255 * ta, 800, spacing=tr)
        gold_word(c, "MAKES GOLD", W / 2, 470, 120, 255 * ta, lerp(1.3, 1.0, out_back(prog(t, TITLE_T, TITLE_T + 0.5), 1.4)), t)
    fade(c, t, DURATION, 0.0, 0.3)


def sfx_events():
    return [(0.0, "boom", 1.0), (0.02, "rumble", 1.0), (0.05, "shine", 0.8), (SHOCKS[1], "boom", 0.5), (SHOCKS[2], "whoosh", 0.5),
            (1.0, "shimmer", 0.6), (REWIND[0], "whoosh_long", 0.9), (REWIND[0] + 0.1, "riser", 0.6),
            (REWIND[1], "shimmer", 0.6), (SMASH_T - 0.4, "whoosh", 0.8), (SMASH_T, "boom", 1.0), (SMASH_T + 0.05, "shine", 0.8),
            (BEFORE_T, "pop", 0.5), (BEFORE_T + 0.3, "pop", 0.5), (ROAD_T, "slide", 0.5), (WRAP[0], "shimmer", 0.6),
            (WRAP[1], "chime", 0.9), (WRAP[1] + 0.05, "ding", 0.6), (TITLE_T, "boom", 0.5), (TITLE_T + 0.05, "shimmer", 0.8)]


MUSIC = dict(chords=[(0.0, 43, (0, 7, 12, 15, 19, 24)), (REWIND[0], 45, (0, 7, 12, 15, 19)), (SMASH_T, 43, (0, 7, 12, 16, 19, 24)),
                     (RING_T, 48, (0, 7, 12, 16, 19))],
             plucks=[(REWIND[1], DURATION)], bpm=104, rises=[(REWIND[1], SMASH_T), (RING_T, TITLE_T)], drone=36)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
