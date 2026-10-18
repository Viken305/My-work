"""Part 1: cold open. Frame 1 is the kilonova at full blast; rewind to two neutron stars; they smash together; the
gold's long road ends in a ring; title.

  python3 render.py part1 [--still 1,5]
"""
from story import *  # noqa: F401,F403

PART = "part1"
VO, _end = schedule(PART, first=0.25, gap=0.75)
DURATION = _end + 2.4
TM = Timing(PART, VO)

REWIND = (VO["H1"] + TM.dur["H1"] + 0.1, VO["H2"] + 0.5)
SMASH_T = TM.word("H2", "smashed") + 0.25
BEFORE_T = TM.word("H2", "long before") - 0.1
ROAD_T = TM.word("H2", "and getting") - 0.2
RING_T = TM.word("H2", "into your hand") - 0.1
TITLE_T = _end - 0.2
CX, CY = W / 2, 860

CAPS = Captions(TM, anchors={"H1": (W / 2, 1300), "H2": (W / 2, 380)},
                heroes={"GOLD": (W / 2, 1530, 210)},
                reacts={"SMASHED": (lambda c, x, y, t, a, s: react_collide(c, x, y, t, a, s, "SMASHED"), W / 2, 1350, 120)})


def kilo_k(t):
    """Kilonova progress: already exploding at frame 1, then rewound to nothing."""
    if t < REWIND[0]:
        return lerp(0.16, 0.42, out_cubic(prog(t, 0.0, REWIND[0])))
    return lerp(0.42, 0.0, in_out(prog(t, REWIND[0], REWIND[1])))


def draw_frame(c, t):
    zoom = lerp(1.18, 1.0, out_cubic(prog(t, 0.0, REWIND[0]))) if t < REWIND[1] else lerp(1.0, 1.06, in_out(prog(t, REWIND[1], SMASH_T)))
    sh = 22 * math.exp(-t * 3.5) + (18 * math.exp(-(t - SMASH_T) * 5) if t > SMASH_T else 0)
    cam = Cam(sh * math.sin(t * 61), sh * math.cos(t * 53), zoom)
    space_bg(c, t, cam, warm=0.5 * (1 - smooth(prog(t, REWIND[0], REWIND[1]))))
    cam.push(c, 1.0)
    c.translate(-W / 2, -H / 2)
    k = kilo_k(t)
    if t < REWIND[1] + 0.2:
        kilonova(c, CX, CY, 700, t, k, seed=5)
        if REWIND[0] < t < REWIND[1]:          # rewind streaks: particles rushing back to the centre
            u = prog(t, REWIND[0], REWIND[1])
            for i in range(26):
                an = i / 26 * 6.28 + 0.2
                d1, d2 = 700 * (1 - u) + 60, 700 * (1 - u) + 260
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
    if SMASH_T < t < ROAD_T + 0.5:
        ka = 1 - smooth(prog(t, ROAD_T - 0.8, ROAD_T + 0.4))
        c.saveLayerAlpha(None, int(255 * ka))
        kilonova(c, CX, CY, 520, t, 0.18 + 0.5 * prog(t, SMASH_T, BEFORE_T + 2.5), seed=8)
        c.restore()
    # "long before the Earth or the Sun existed": dotted outlines of the Sun and Earth, not there yet
    nb = smooth(prog(t, BEFORE_T, BEFORE_T + 0.4)) * (1 - smooth(prog(t, ROAD_T - 0.3, ROAD_T + 0.2)))
    if nb > 0:
        for (x, y, r, lab) in ((310, 1420, 120, "SUN"), (770, 1450, 70, "EARTH")):
            pe = stroke(WHITE, 4, 200 * nb)
            pe.setPathEffect(skia.DashPathEffect.Make([14, 12], t * 20))
            c.drawCircle(x, y, r, pe)
            text(c, lab, x, y + 12, 28, WHITE, 220 * nb, 800, spacing=4)
            text(c, "NOT YET", x, y + r + 50, 22, (255, 170, 130), 230 * nb, 800, spacing=3)
    # the long road: one gold nugget travels down into a ring
    if t > ROAD_T - 0.3:
        u = in_out(prog(t, ROAD_T - 0.3, RING_T + 0.8))
        nx, ny = lerp(CX, CX, u), lerp(CY, 1180, u) - 120 * math.sin(math.pi * u)
        ra = smooth(prog(t, RING_T - 0.6, RING_T))
        ring(c, CX, 1220, 0.9, t, "back", 255 * ra)
        light(c, nx, ny, 160, GOLD, 120)
        for j in range(8):
            uj = max(0.0, u - j * 0.02)
            c.drawCircle(lerp(CX, CX, uj), lerp(CY, 1180, uj) - 120 * math.sin(math.pi * uj), 10 - j, add(GOLD_HI, 160 - j * 18))
        gold_sphere(c, nx, ny, lerp(28, 46, u), (140, 110, 170))
        ring(c, CX, 1220, 0.9, t, "front", 255 * ra)
        if t > RING_T + 0.8:
            light(c, CX, 1220, 420, GOLD, 120 * math.exp(-(t - RING_T - 0.8) * 2))
            sparkle4(c, CX + 250, 1170, 34 * (0.7 + 0.3 * math.sin(t * 5)), 255)
            sparkle4(c, CX - 270, 1260, 24, 220)
    cam.pop(c)
    shake_ = CAPS.draw(c, t)
    ta = smooth(prog(t, TITLE_T, TITLE_T + 0.4))
    if ta > 0:
        tr = lerp(24, 8, out_cubic(prog(t, TITLE_T, TITLE_T + 1.5)))
        text(c, "HOW EARTH", W / 2, 330, 90, WHITE, 255 * ta, 800, spacing=tr)
        gold_word(c, "MAKES GOLD", W / 2, 470, 120, 255 * ta, lerp(1.3, 1.0, out_back(prog(t, TITLE_T, TITLE_T + 0.5), 1.4)), t)
    fade(c, t, DURATION, 0.0, 0.3)


def sfx_events():
    return [(0.0, "boom", 1.0), (0.02, "rumble", 1.0), (0.05, "shine", 0.8), (REWIND[0], "whoosh_long", 0.9), (REWIND[0] + 0.1, "riser", 0.6),
            (REWIND[1], "shimmer", 0.6), (SMASH_T - 0.4, "whoosh", 0.8), (SMASH_T, "boom", 1.0), (SMASH_T + 0.05, "shine", 0.8),
            (BEFORE_T, "pop", 0.5), (BEFORE_T + 0.3, "pop", 0.5), (ROAD_T, "slide", 0.5), (RING_T + 0.8, "chime", 0.9), (RING_T + 0.85, "ding", 0.6),
            (TITLE_T, "boom", 0.5), (TITLE_T + 0.05, "shimmer", 0.8)]


MUSIC = dict(chords=[(0.0, 43, (0, 7, 12, 15, 19, 24)), (REWIND[0], 45, (0, 7, 12, 15, 19)), (SMASH_T, 43, (0, 7, 12, 16, 19, 24)),
                     (RING_T, 48, (0, 7, 12, 16, 19))],
             plucks=[(REWIND[1], DURATION)], bpm=104, rises=[(REWIND[1], SMASH_T), (RING_T, TITLE_T)], drone=36)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
