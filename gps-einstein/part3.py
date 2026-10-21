"""Part 3, four satellites, one dot.

  * Spheres: over the curve of the glass Earth, satellite 1 grows a glass bubble whose skin passes through you
    ("somewhere on a giant sphere"); two more join ("Add two more"); where all three skins meet one point flares
    ("a single point") and becomes YOU.
  * Clock: satellite 4 sends its beam; the phone's own little glass clock jitters, then locks ("fixes your phone's
    own clock").
  * Timing: a glass ruler; a pulse of light crosses 30 cm in 1 ns (shown slowed down, labelled); then the phone map:
    1 µs late and the dot slips 300 m.

  python3 render.py part3 [--still 2,6,10,16,21]
"""
from film import *  # noqa: F401,F403

PART = "part3"
VO, _end = schedule(PART)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)

S1 = TM.word("B1", "One")
GROW0, GROW1 = TM.word("B1", "puts"), TM.word("B1", "sphere.", end=True)
ADD = TM.word("B1", "Add")
NARROW, POINT = TM.word("B1", "narrow"), TM.word("B1", "point.")
THATS = TM.word("B1", "That's")
FOURTH, FIXES, CLOCK = TM.word("B2", "fourth"), TM.word("B2", "fixes"), TM.word("B2", "clock,")
NEVER = TM.word("B2", "never")
TIMING = TM.word("B3", "timing")
LIGHT, SECOND = TM.word("B3", "Light"), TM.word("B3", "second.", end=True)
MILLIONTH = TM.word("B3", "millionth,")
THREE, METRES = TM.word("B3", "three"), TM.word("B3", "metres.", end=True)
RULER0 = TM.end("B2") + 0.3
MAP0 = TM.word("B3", "Be off") - 0.35
DURATION = TM.end("B3") + 0.7

CAPS = Captions(TM, ENV, words=WORDS, model=MODEL)
EC, ER = (540, 1640), 700                      # the Earth: a big curve at the bottom
YOU = (470, 958)
SATS = [(150, 400), (950, 330), (640, 270), (1000, 700)]
RAD = [math.hypot(x - YOU[0], y - YOU[1]) for x, y in SATS]


def sphere_scene(t):
    img = backdrop(t, glow=(0.5, 0.3), floor=0.99, caustic=0.0)
    img, proj = earth(img, EC[0], EC[1], ER, t, lon0=-8 + 0.4 * t, lat0=-42, spin=0.0)
    out_k = 1 - smooth(prog(t, FOURTH - 0.3, FOURTH + 0.4))          # bubbles give way to satellite 4
    grow = [in_out(prog(t, GROW0 - 0.1, GROW1)), in_out(prog(t, ADD + 0.1, ADD + 1.1)), in_out(prog(t, ADD + 0.3, ADD + 1.3))]
    for i in range(3):
        if grow[i] > 0:
            img = bubble(img, SATS[i][0], SATS[i][1], RAD[i] * grow[i], 0.85 * out_k + 0.15)
    meet = smooth(prog(t, NARROW, POINT))

    def marks(c):
        for i, (x, y) in enumerate(SATS):
            t0 = S1 if i == 0 else ADD + 0.05 * i if i < 3 else FOURTH - 0.1
            q = back_out(prog(t, t0, t0 + 0.4))
            if q > 0:
                mini_sat(c, x, y, 24 * q, 0.3 + 0.2 * i, 255)
                label(c, str(i + 1), x, y - 46, 30, "mono_bold", PAPER, 255 * smooth(q), "center")
        # the skins' crossings brighten toward the single point
        if meet > 0:
            for i in range(3):
                r = RAD[i]
                ang = math.degrees(math.atan2(YOU[1] - SATS[i][1], YOU[0] - SATS[i][0]))
                span = lerp(70, 8, meet)
                c.drawArc(skia.Rect.MakeLTRB(SATS[i][0] - r, SATS[i][1] - r, SATS[i][0] + r, SATS[i][1] + r),
                          ang - span / 2, span, False, paint(AMBER, 255 * meet * out_k, sigma=3, stroke=6))
        fl = pulse(t, POINT - 0.1, 0.9)
        if t > POINT - 0.1:
            c.drawCircle(*YOU, 18 + 120 * out_cubic(prog(t, POINT - 0.1, POINT + 0.8)),
                         paint(AMBER, 255 * (1 - prog(t, POINT - 0.1, POINT + 0.8)), stroke=5))
            glow_dot(c, *YOU, 14 + 6 * fl, AMBER, 255, 3.8)
        ya = smooth(prog(t, THATS, THATS + 0.4))
        label(c, "YOU", YOU[0] - 34, YOU[1] + 10, 32, "mono_bold", AMBER, 255 * ya, "right", 0.2)
        # satellite 4 talks to you
        if t > FOURTH:
            beam(c, *SATS[3], *YOU, in_out(prog(t, FOURTH + 0.1, FIXES)), CYAN, 230)
            for i in range(3):
                beam(c, *SATS[i], *YOU, smooth(prog(t, FOURTH + 0.2 * i, FIXES)), CYAN, 120, 2, head=False)
    img = over(img, layer(marks))
    # the phone's own clock: jitters, then locks on "clock"
    ca = window(t, FIXES - 0.4, RULER0 - 0.1, 0.4, 0.3)
    if ca > 0.01:
        lock = smooth(prog(t, CLOCK - 0.05, CLOCK + 0.25))
        jit = (1 - lock) * (0.8 * math.sin(t * 23) + 0.5 * math.sin(t * 37 + 1))
        secs = 10 * 3600 + 8 * 60 + 10 + (t - FIXES) + jit * 2
        img = clock(img, 760, 690, 130 * (0.85 + 0.15 * ca), secs, AMBER, "PHONE CLOCK",
                    "LOCKED" if lock > 0.5 else f"OFF BY {abs(jit) * 0.3:.4f} s", t, 0.3)
        if lock > 0:
            q = prog(t, CLOCK - 0.05, CLOCK + 0.6)
            img = over(img, layer(lambda c: c.drawCircle(760, 690, 130 + 60 * out_cubic(q), paint(CYAN, 255 * (1 - q), stroke=4))))
    return img


def ruler_scene(t):
    img = backdrop(t, glow=(0.5, 0.42), floor=0.74, pool=(540, 1500, 420, 60))
    x0, x1, y0 = 120, 960, 820
    img = card(img, 90, y0 - 40, 900, 170, 1.0, 34, tint=0.36, sheen=(0.6, 60, 0.07))
    u = in_out(prog(t, LIGHT, SECOND))

    def draw(c):
        for k in range(31):
            x = lerp(x0, x1, k / 30)
            big = k % 5 == 0
            c.drawLine(x, y0 - 20, x, y0 + (24 if big else 10), paint(PAPER, 230 if big else 120, stroke=3 if big else 1.6))
            if big:
                label(c, str(k), x, y0 + 64, 26, "mono", SMOKE, 255, "center")
        label(c, "cm", x1 + 6, y0 + 64, 22, "mono", SMOKE, 255)
        # the pulse of light: a comet with a trail
        if t > LIGHT - 0.1:
            xe = lerp(x0, x1, u)
            c.drawLine(x0, y0 - 40, xe, y0 - 40, paint(CYAN, 80, sigma=10, stroke=16))
            c.drawLine(max(x0, xe - 260), y0 - 40, xe, y0 - 40, paint(mix(CYAN, PAPER, 0.5), 230, stroke=4))
            glow_dot(c, xe, y0 - 40, 12, CYAN, 255, 4.0)
        glow_text(c, f"{u:.3f} ns", W / 2, 640, 70, "mono_bold", VIOLET, 255 * smooth(prog(t, LIGHT - 0.3, LIGHT)))
        label(c, f"LIGHT, SLOWED DOWN {SECOND - LIGHT:.1f} BILLION TIMES", W / 2, 1110, 22, "mono", SMOKE,
              255 * smooth(prog(t, LIGHT, LIGHT + 0.4)), "center", 0.16)
        if t > SECOND - 0.1:
            q = prog(t, SECOND - 0.1, SECOND + 0.5)
            c.drawCircle(x1, y0 - 40, 12 + 70 * out_cubic(q), paint(CYAN, 255 * (1 - q), stroke=4))
    img = over(img, layer(draw))
    img = glass_text(img, "PERFECT TIMING", W / 2, 470, 84, "black", tint=0.28, lift=26, caustic_t=t,
                     a=window(t, TIMING - 0.2, LIGHT - 0.2, 0.4, 0.4))
    img = chip(img, "30 cm  in  1 ns", W / 2, 1010, 34, CYAN, smooth(prog(t, SECOND - 0.2, SECOND + 0.3)))
    return img


def map_scene(t):
    img = backdrop(t, glow=(0.42, 0.40), floor=0.76, pool=(560, 1640, 320, 60))
    slip = in_out(prog(t, THREE - 0.1, METRES))
    d = 0.3 * 240 * slip                                 # 300 m in map units (240 per km)
    dot = (DOT[0] + d * 0.94, DOT[1] + d * 0.34)

    def extra(c, to, sw, sh):
        if slip > 0:
            hx, hy = to(DOT)
            dx, dy = to(dot)
            c.drawCircle(hx, hy, 20, paint(AMBER, 255, stroke=4))
            c.drawLine(hx, hy, dx, dy, paint(AMBER, 230, stroke=4))
            for x, y in ((hx, hy), (dx, dy)):
                c.drawLine(x, y - 34, x, y - 14, paint(PAPER, 220, stroke=2))
            label(c, "300 m", (hx + dx) / 2, (hy + dy) / 2 - 44, 30, "mono_bold", AMBER, 255 * slip, "center")
    img = phone(img, 540, 1000, 520, 1040, -5 + 1.5 * math.sin(t * 0.5), t, zoom=3.0, pan=DOT, dot=dot, pin=None,
                show_route=0, extra=extra)
    img = chip(img, "1 µs LATE", W / 2, 400, 38, VIOLET, smooth(prog(t, MILLIONTH - 0.2, MILLIONTH + 0.2)))
    return img


def draw_frame(t):
    if t < RULER0:
        img = sphere_scene(t)
    elif t < MAP0:
        img = ruler_scene(t)
    else:
        img = map_scene(t)
    for tc in (RULER0, MAP0):
        k = 1 - abs(t - tc) / 0.3
        if k > 0:
            img = fade(img, smooth(k) * 0.85, (8, 14, 30))
    img = CAPS.draw(img, t)
    img = fade(img, max(1 - smooth(prog(t, 0, 0.3)), smooth(prog(t, DURATION - 0.25, DURATION))))
    return img


def sfx_events():
    return [(S1, "pop", 0.5), (GROW0, "glass_whoosh", 0.45), (GROW1 - 0.2, "chime", 0.3),
            (ADD, "pop", 0.45), (ADD + 0.12, "pop", 0.45), (ADD + 0.2, "glass_whoosh", 0.4),
            (NARROW - 0.2, "riser", 0.3), (POINT - 0.1, "chime", 0.6), (THATS, "ping", 0.5),
            (FOURTH - 0.1, "pop", 0.5), (FOURTH + 0.1, "swish", 0.4), (FIXES - 0.2, "tick_roll", 0.35),
            (CLOCK - 0.05, "lock", 0.6), (RULER0 - 0.2, "glass_whoosh", 0.5), (TIMING, "clink", 0.4),
            (LIGHT - 0.1, "swish", 0.45), (SECOND - 0.1, "ping", 0.55), (MAP0 - 0.2, "glass_whoosh", 0.45),
            (MILLIONTH - 0.1, "clink", 0.45), (THREE - 0.1, "swish", 0.5), (METRES - 0.2, "low_hit", 0.35)]


MUSIC = dict(beds=[(0.0, DURATION, "glass", 0.9)])
