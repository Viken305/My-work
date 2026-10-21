"""Part 2, clocks in the sky: the glass Earth rises into frame; an altitude line climbs 20,200 km "above you"; six
orbits draw themselves and about thirty satellites pop in and circle; a hero glass satellite slides in ("Each one"),
its atomic clock glows inside it, it sends rings of light ("shouting the same message") and a glass card fills in
WHERE (the satellite's own position) and WHEN; the message travels down to your phone as a beam ("a split second later"), a stopwatch stops at
0.0674 s, and delay x speed of light = 20,200 km ("how far away the satellite is").

  python3 render.py part2 [--still 1,3,6,9,13,16]
"""
from film import *  # noqa: F401,F403

PART = "part2"
VO, _end = schedule(PART)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)

ALT0, ABOVE = TM.word("A1", "Twenty"), TM.word("A1", "above")
SATS0, SATS1 = TM.word("A1", "thirty"), TM.word("A1", "satellites", end=True)
CIRCLE = TM.word("A1", "circle")
HERO0 = TM.word("A2", "Each")
ATOMIC = TM.word("A2", "atomic")
SHOUT = TM.word("A2", "shouting")
WHERE, WHEN = TM.word("A2", "where"), TM.word("A2", "exact")
HEARS, LATER = TM.word("A3", "hears"), TM.word("A3", "later.")
DELAY, FAR = TM.word("A3", "delay"), TM.word("A3", "far")
DURATION = TM.end("A3") + 0.7

CAPS = Captions(TM, ENV, words=WORDS, model=MODEL)
CX, CY, R = 540, 1060, 300
PLANES = [(74, -18 + k * 30, k * 0.9) for k in range(6)]
YOU_LL = (-3.7, 40.4)                         # Madrid, facing us
HX, HY = 800, 520                             # the hero satellite


def earth_pose(t):
    rise = out_cubic(prog(t, 0.0, 2.2))
    back = in_out(prog(t, HERO0 - 0.2, HERO0 + 0.8))
    cy = lerp(1700, CY, rise) + 30 * back
    r = lerp(380, R, rise) - 20 * back
    return CX, cy, r


def draw_frame(t):
    img = backdrop(t, glow=(0.5, 0.55), floor=0.95, caustic=0.4)
    cx, cy, r = earth_pose(t)
    orbits = [orbit_points(cx, cy, r * (1.57 + 0.047 * (k % 3)), inc, rot, 220, ph)
              for k, (inc, rot, ph) in enumerate(PLANES)]
    draw_in = [in_out(prog(t, CIRCLE - 0.6 + k * 0.12, CIRCLE + 0.5 + k * 0.12)) for k in range(6)]
    oa = 255 * smooth(prog(t, SATS0 - 0.6, SATS0))

    def back(c):
        for pts, u in zip(orbits, draw_in):
            if u > 0:
                orbit_line(c, pts[:max(2, int(len(pts) * u))], False, CYAN, 200 * oa / 255, 1.6)
    img = over(img, layer(back))
    img, proj = earth(img, cx, cy, r, t, lon0=-15 - 0.6 * t, lat0=28, spin=0.0)
    you = proj(*YOU_LL)

    def front(c):
        for k, (pts, u) in enumerate(zip(orbits, draw_in)):
            if u > 0:
                orbit_line(c, pts[:max(2, int(len(pts) * u))], True, CYAN, 230 * oa / 255, 1.8)
            for j in range(5):
                q = back_out(prog(t, SATS0 + (k * 5 + j) * 0.024, SATS0 + (k * 5 + j) * 0.024 + 0.35))
                if q <= 0:
                    continue
                x, y, z = pts[int((j / 5 + t * 0.012 + k * 0.07) % 1 * 220)]
                if z >= 0 or math.hypot(x - cx, y - cy) > r:
                    mini_sat(c, x, y, (13 if z >= 0 else 9) * q, 0.3, 255 if z >= 0 else 110, 1 if z >= 0 else 0.3)
        # the altitude line: from you straight up 20,200 km to the orbit shell
        la = window(t, ABOVE - 0.3, HERO0 - 0.2, 0.4, 0.4)
        if la > 0.01:
            ux, uy = you[0] - cx, you[1] - cy
            n = math.hypot(ux, uy) or 1
            top = (cx + ux / n * r * 1.6, cy + uy / n * r * 1.6 - 40)
            u = out_cubic(prog(t, ABOVE - 0.3, ABOVE + 0.5))
            ex, ey = lerp(you[0], top[0], u), lerp(you[1], top[1], u)
            p = paint(PAPER, 200 * la, stroke=2)
            p.setPathEffect(skia.DashPathEffect.Make([10, 8], 0))
            c.drawLine(you[0], you[1], ex, ey, p)
            c.drawLine(ex - 14, ey, ex + 14, ey, paint(PAPER, 220 * la, stroke=2))
        glow_dot(c, you[0], you[1], 13, AMBER, 255 * smooth(prog(t, 1.2, 2.0)), 3.6)
        label(c, "YOU", you[0] - 34, you[1] + 10, 30, "mono_bold", AMBER, 255 * smooth(prog(t, 1.4, 2.2)), "right", 0.2)
    img = over(img, layer(front))
    la = window(t, ABOVE - 0.1, HERO0 - 0.2, 0.4, 0.4)
    if la > 0.01:
        ux, uy = you[0] - cx, you[1] - cy
        n = math.hypot(ux, uy) or 1
        img = chip(img, "20,200 km", you[0] + ux / n * r * 0.95 + 120, you[1] + uy / n * r * 0.95 - 150, 30, PAPER, la)
    img = over(img, layer(lambda c: label(c, "≈30 SATELLITES · 6 ORBITAL PLANES", W / 2, 290, 26, "mono", SMOKE,
                                          255 * window(t, SATS1, WHERE - 0.5, 0.5, 0.4), "center", 0.14)))

    # the hero satellite: slides in, its atomic clock glows, it sends the message
    hq = out_cubic(prog(t, HERO0 - 0.15, HERO0 + 0.7))
    if hq > 0:
        hx, hy = lerp(1250, HX, hq), lerp(250, HY, hq)
        ang = math.atan2(you[1] - hy, you[0] - hx)
        travel = in_out(prog(t, HEARS - 0.1, LATER))
        sent = t > SHOUT - 0.1

        def signal(c):
            if sent:
                rings(c, hx, hy, t, SHOUT - 0.1, math.degrees(ang), 56, 3, 40, 340, 0.6, CYAN,
                      230 * (1 - smooth(prog(t, HEARS, HEARS + 0.6))))
            beam(c, hx, hy, you[0], you[1], travel, CYAN, 255 * (1 - 0.4 * smooth(prog(t, FAR + 1.0, DURATION))))
            if t > LATER - 0.05:
                q = prog(t, LATER - 0.05, LATER + 0.6)
                c.drawCircle(you[0], you[1], 14 + 80 * out_cubic(q), paint(AMBER, 255 * (1 - q), stroke=4))
        img = over(img, layer(signal))
        m = sat_mask(hx, hy, 70 * (0.6 + 0.4 * hq), -0.45)
        shadow(img, m, 20, 30, 20, 0.4)
        glass.glass(img, m, bevel=14, refract=12, frost=8, tint=0.32, lift=14, rim=1.5, sheen=(0.4 + 0.1 * math.sin(t), 26, 0.16))
        ga = smooth(prog(t, ATOMIC - 0.1, ATOMIC + 0.4))
        tick = 0.5 + 0.5 * math.cos(2 * math.pi * (t - ATOMIC)) ** 8 if ga > 0 else 0
        img = over(img, layer(lambda c: (glow_dot(c, hx, hy, 11, VIOLET, 255 * ga * (0.75 + 0.25 * tick), 4.0),
                                         c.drawCircle(hx, hy, 24, paint(VIOLET, 200 * ga, stroke=2)))))
        img = chip(img, "ATOMIC CLOCK", hx + 30, hy + 120, 22, VIOLET, window(t, ATOMIC, SHOUT + 0.6, 0.3, 0.4))
        # the message card: WHERE and WHEN
        ca = window(t, WHERE - 0.25, HEARS + 0.3, 0.3, 0.5)
        if ca > 0.01:
            bx, by = 40, 330
            img = card(img, bx, by, 660, 160, ca, 26)
            POS = "51.9°N 21.3°E · ALT 20,190 km"
            nw = int(len(POS) * prog(t, WHERE, WHERE + 0.9))
            ns = (t - WHEN) % 1.0 if t > WHEN else 0.0
            when = f"12:00:{int(ns * 60):02d}.{int(ns * 1e9) % 1000000000:09d}"[:21]
            img = over(img, layer(lambda c: (
                label(c, "WHERE", bx + 26, by + 64, 24, "mono", SMOKE, 255 * ca, tracking=0.1),
                label(c, POS[:nw], bx + 140, by + 64, 26, "mono_bold", PAPER, 255 * ca),
                label(c, "WHEN", bx + 26, by + 118, 24, "mono", SMOKE, 255 * ca * smooth(prog(t, WHEN - 0.2, WHEN)), tracking=0.1),
                label(c, when, bx + 140, by + 118, 28, "mono_bold", VIOLET, 255 * ca * smooth(prog(t, WHEN - 0.2, WHEN))))))
        # the stopwatch near you, then delay x speed of light = distance
        sw = window(t, HEARS - 0.1, DURATION, 0.3, 1)
        if sw > 0.01:
            dt = 0.0674 * in_out(prog(t, HEARS - 0.1, LATER))
            img = chip(img, f"{dt:.4f} s", you[0] - 150, you[1] + 120, 30, AMBER, sw)
        ea = window(t, DELAY - 0.1, DURATION, 0.35, 1)
        if ea > 0.01:
            img = card(img, 90, 250, 900, 200, ea, 30)
            ra = smooth(prog(t, FAR - 0.1, FAR + 0.4))
            img = over(img, layer(lambda c: (
                label(c, "0.0674 s  ×  299,792 km/s", W / 2, 326, 40, "mono_bold", PAPER, 255 * ea, "center"),
                label(c, "DELAY          SPEED OF LIGHT", W / 2, 362, 20, "mono", SMOKE, 255 * ea, "center", 0.2),
                glow_text(c, "≈ 20,200 km", W / 2, 420, 46, "mono_bold", CYAN, 255 * ra))))
    img = CAPS.draw(img, t)
    img = fade(img, max(1 - smooth(prog(t, 0, 0.35)), smooth(prog(t, DURATION - 0.25, DURATION))))
    return img


def sfx_events():
    ev = [(0.0, "glass_whoosh", 0.6), (ABOVE - 0.2, "tick_roll", 0.35), (CIRCLE - 0.4, "shimmer", 0.4),
          (HERO0 - 0.2, "glass_whoosh", 0.5), (HERO0 + 0.4, "clink", 0.5), (ATOMIC, "chime", 0.45),
          (WHERE - 0.1, "dial", 0.35), (WHEN - 0.1, "tick_roll", 0.3), (HEARS - 0.1, "swish", 0.5),
          (LATER - 0.05, "ping", 0.6), (DELAY, "clink", 0.4), (FAR - 0.1, "chime", 0.4)]
    ev += [(SATS0 + i * 0.12, "pop", 0.25) for i in range(6)]
    ev += [(SHOUT - 0.1 + i / 0.6 / 3, "ping", 0.22) for i in range(int((HEARS - SHOUT) * 0.6 * 3) + 1)]
    return ev


MUSIC = dict(beds=[(0.0, DURATION, "glass", 0.9)])
