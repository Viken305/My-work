"""Part 1, the hook: the glass phone with its map; Einstein's clock equation forms in glass above it ("Einstein's
math"); the camera pushes onto the map and the blue dot drifts away from you, the map zooming out as the error
counts up to 11 km, then 22 and 33 km a day ("every single day"); it snaps back, the equation returns for "Einstein"
and the coffee shop pulses for "coffee shop?"; the phone flies at the camera and the title forms in glass.

  python3 render.py part1 [--still 1,4,7,12]
"""
from film import *  # noqa: F401,F403

PART = "part1"
VO, _end = schedule(PART)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)

EQ0, EQ1 = TM.word("H1", "Einstein's"), TM.word("H1", "math.", end=True)
OUT0 = TM.word("H2", "Without")
ZOOM0 = TM.word("H2", "blue")
DRIFT0, DRIFT1 = TM.word("H2", "drift"), TM.word("H2", "kilometres", end=True)
DAY1, DAY2 = TM.word("H2", "single"), TM.word("H2", "day.")
BACK0 = TM.word("H3", "So")
EIN = TM.word("H3", "Einstein")
SHOP = TM.word("H3", "coffee")
TITLE_T = TM.end("H3") + 0.3
DURATION = TITLE_T + 2.8

CAPS = Captions(TM, ENV, words=WORDS, model=MODEL, hide={"H3": [(TITLE_T - 0.3, 99)]})
PER_KM = 240.0                                 # map units per kilometre (a block is ~250 m)
DIR = (0.94, 0.34)                             # the direction the dot drifts (map coordinates)


def drift_km(t):
    """How far the dot has drifted (km): 11 km by the end of "kilometres", 22 on "single", 33 on "day"."""
    k = 11 * in_out(prog(t, DRIFT0, DRIFT1 + 0.2))
    k += 11 * in_out(prog(t, DAY1 - 0.1, DAY1 + 0.35)) + 11 * in_out(prog(t, DAY2 - 0.1, DAY2 + 0.35))
    return k * (1 - in_out(prog(t, BACK0, BACK0 + 0.7)))


def view(t):
    """Phone pose and map zoom/pan over time."""
    push = in_out(prog(t, ZOOM0 - 0.1, ZOOM0 + 0.8)) * (1 - in_out(prog(t, BACK0 + 0.1, BACK0 + 1.0)))
    w, h = lerp(470, 640, push), lerp(940, 1280, push)
    cx = 540 + 4 * math.sin(t * 0.6)
    cy = lerp(lerp(1110, 1060, out_cubic(prog(t, 0, 2.5))), 900, push) + 8 * math.sin(t * 1.1)
    rot = lerp(lerp(-11, -7, out_cubic(prog(t, 0, 3.0))), -3, push)
    km = drift_km(t)
    zoom = 1.0 / (1 + 0.55 * min(km, 11) + 0.05 * max(0, km - 11)) if km > 0 else 1.0
    zoom = min(1.0, max(zoom, 0.12)) if km > 0.05 else 1.0
    d = km * PER_KM
    dot = (DOT[0] + DIR[0] * d, DOT[1] + DIR[1] * d)
    span = min(d, 11 * PER_KM)
    pan = (DOT[0] + DIR[0] * span / 2, DOT[1] + DIR[1] * span / 2)
    return w, h, cx, cy, rot, zoom, pan, dot, km


def phone_scene(t):
    img = backdrop(t, glow=(0.42, 0.40), floor=0.76, pool=(560, 1640, 320, 60))
    img = defocus(img, lambda c: [c.drawRRect(rrect(x, y, w_, h_, 40), paint(mix(CARD, PAPER, 0.2), 120))
                                  for x, y, w_, h_ in ((-80 + 10 * math.sin(t * 0.3), 260, 300, 420),
                                                       (850, 980 + 12 * math.sin(t * 0.4), 320, 520))], 26, 0.7)
    # Einstein's clock equation: forms on "Einstein's math", leaves on "Without it", returns on "Einstein" (H3)
    ea = smooth(prog(t, EQ0 - 0.1, EQ1)) * (1 - smooth(prog(t, OUT0 - 0.1, OUT0 + 0.4)))
    ea = max(ea, smooth(prog(t, EIN - 0.1, EIN + 0.5)) * (1 - smooth(prog(t, TITLE_T - 0.4, TITLE_T - 0.1))))
    if ea > 0.01:
        rise = (1 - ea) * 30
        img = glass_text(img, "Δτ ≈ Δt", W / 2, 400 + rise, 130, "light", tint=0.18, lift=20, caustic_t=t, rim=1.0,
                         a=ea, scale=0.94 + 0.06 * ea)
        img = glass_text(img, "(1 + Φ/c² − v²/2c²)", W / 2, 520 + rise, 70, "light", tint=0.18, lift=20, caustic_t=t,
                         rim=1.0, a=smooth(prog(ea, 0.3, 1.0)))
    w, h, cx, cy, rot, zoom, pan, dot, km = view(t)
    home = DOT

    def extra(c, to, sw, sh):
        if km > 0.02:
            hx, hy = to(home)
            dx, dy = to(dot)
            c.drawLine(hx, hy, dx, dy, paint(AMBER, 60, sigma=8, stroke=14))
            c.drawLine(hx, hy, dx, dy, paint(AMBER, 220, stroke=4))
            # where you really are
            c.drawCircle(hx, hy, 20, paint(AMBER, 255, stroke=4))
            c.drawCircle(hx, hy, 6, paint(AMBER, 255))
            label(c, "YOU", hx - 30, hy + 8, 24, "mono_bold", AMBER, 255, "right", 0.15)
            # scale bar, bottom left of the screen
            km_bar = 120 / (zoom * PER_KM)
            label(c, f"{km_bar:.1f} km" if km_bar < 10 else f"{km_bar:.0f} km", cx - sw / 2 + 40, cy + sh / 2 - 70,
                  22, "mono", SMOKE, 255)
            c.drawLine(cx - sw / 2 + 40, cy + sh / 2 - 52, cx - sw / 2 + 160, cy + sh / 2 - 52, paint(SMOKE, 255, stroke=3))
    show_dot = dot
    img = phone(img, cx, cy, w, h, rot, t, zoom=zoom, pan=pan, dot=show_dot, pin=PIN,
                show_route=1.0 - smooth(prog(km, 0.0, 0.8)), extra=extra)
    # the error counter and the day counter (glass chips above the map)
    ca = smooth(prog(t, DRIFT0, DRIFT0 + 0.3)) * (1 - smooth(prog(t, BACK0, BACK0 + 0.4)))
    if ca > 0.01:
        img = chip(img, f"ERROR  +{km:4.1f} km", cx, cy - h / 2 + 150, 34, AMBER, ca)
        day = 1 + (t > DAY1 - 0.05) + (t > DAY2 - 0.05)
        da = smooth(prog(t, DRIFT1 - 0.1, DRIFT1 + 0.2)) * ca
        img = chip(img, f"DAY {day}", cx, cy - h / 2 + 235, 26, VIOLET, da)
    # the coffee shop pulses on "coffee shop?"
    if SHOP - 0.2 < t < TITLE_T:
        q = prog(t, SHOP, SHOP + 0.8)
        px, py = phone_xy(PIN, cx, cy, zoom, pan, rot)
        img = over(img, layer(lambda c: c.drawCircle(px, py, 30 + 90 * out_cubic(q), paint(AMBER, 255 * (1 - q), stroke=5))))
    return img


def title_scene(t):
    u = t - TITLE_T
    img = backdrop(t, glow=(0.5, 0.45), floor=0.80, caustic=1.2, pool=(540, 1650, 420, 80), seed=1.0)
    pts = orbit_points(540, 900, 620, 72, -14, 260, 0.0)
    oa = 255 * smooth(prog(u, 0.2, 1.2))
    k = int(205 + 18 * u) % 260
    img = over(img, layer(lambda c: (orbit_line(c, pts, False, CYAN, oa, 2), orbit_line(c, pts, True, CYAN, oa, 2),
                                     mini_sat(c, pts[k][0], pts[k][1], 18, 0.2, oa))))
    img = over(img, layer(lambda c: label(c, "HOW GPS USES RELATIVITY", W / 2, 560, 30, "mono", SMOKE,
                                          255 * smooth(prog(u, 1.0, 1.6)), "center", 0.3)))
    for i, (s, y, size, rgb, glow) in enumerate((("YOUR PHONE", 740, 128, PAPER, None), ("DOES", 880, 128, PAPER, None),
                                                 ("EINSTEIN'S", 1060, 168, mix(VIOLET, PAPER, 0.35), VIOLET),
                                                 ("MATH", 1220, 168, PAPER, None))):
        q = prog(u, 0.05 + i * 0.16, 0.55 + i * 0.16)
        if q > 0:
            img = glass_text(img, s, W / 2, y + (1 - out_cubic(q)) * 40, size, "black", tint=0.30, lift=30, rgb=rgb,
                             caustic_t=t, glow=glow if q > 0.6 else None, a=smooth(q), scale=1.12 - 0.12 * out_cubic(q))
    img = defocus(img, lambda c: shard(c, 940 - 20 * u, 330 + 10 * u, 130, 1.1 + 0.05 * u), 14, 0.7)
    img = defocus(img, lambda c: shard(c, 120 + 15 * u, 1500, 170, 3.6 - 0.04 * u), 18, 0.7)
    return img


def draw_frame(t):
    if t < TITLE_T:
        img = phone_scene(t)
        # the camera flies into the phone just before the title
        fly = in_out(prog(t, TITLE_T - 0.45, TITLE_T))
        if fly > 0:
            img = cam(img, 1 + 1.6 * fly ** 2, W / 2, 900)
            img = fade(img, fly ** 1.5 * 0.9, (8, 14, 30))
    else:
        img = title_scene(t)
        img = fade(img, 1 - smooth(prog(t, TITLE_T, TITLE_T + 0.35)), (8, 14, 30))
    img = CAPS.draw(img, t)
    img = fade(img, max(1 - smooth(prog(t, 0, 0.5)), smooth(prog(t, DURATION - 0.25, DURATION))))
    return img


def samples_at(t):
    return 2 if TITLE_T - 0.45 < t < TITLE_T or BACK0 < t < BACK0 + 0.8 else 1


def sfx_events():
    return [(0.05, "chime", 0.5), (EQ0 - 0.05, "shimmer", 0.35), (ZOOM0 - 0.1, "glass_whoosh", 0.55),
            (DRIFT0 - 0.05, "detune", 0.45), (DRIFT0, "tick_roll", 0.45), (DAY1 - 0.05, "pop", 0.6),
            (DAY2 - 0.05, "pop", 0.7), (BACK0 - 0.1, "reverse_swell", 0.5), (BACK0 + 0.6, "clink", 0.5),
            (EIN - 0.05, "shimmer", 0.25), (SHOP, "ping", 0.55), (TITLE_T - 0.6, "riser", 0.35),
            (TITLE_T, "title_hit", 0.85), (TITLE_T + 0.05, "chime", 0.6)]


MUSIC = dict(beds=[(0.0, TITLE_T, "glass", 0.9), (TITLE_T, DURATION, "synth", 0.6)])
