"""Part 5, the fix and the payoff.

  * The fix: a glass frequency card; the digits roll from 10.23 MHz down to 10.22999999543 MHz ("slow them down"); a
    launch streak ("before launch"); on the ground the satellite clock lags GROUND ("a tiny bit too slow"); it rises
    into orbit and the hands lock together ("exactly right").
  * What if: a glass Earth covered in blue dots (cities); without the fix every dot drifts away with an amber trail,
    ">10 km" tags pop up.
  * Payoff: Einstein's equation in glass ("Relativity isn't just a theory"); the phone rises into its first-frame pose
    with the dot on the coffee shop ("in your pocket"), so the Short loops.

  python3 render.py part5 [--still 1,4,7,10,12,15,18]
"""
from film import *  # noqa: F401,F403

PART = "part5"
VO, _end = schedule(PART)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)

SLOW, LAUNCH = TM.word("D1", "slow"), TM.word("D1", "launch.")
GROUND, TINY = TM.word("D1", "ground,"), TM.word("D1", "tiny")
ORBIT, EXACTLY = TM.word("D1", "orbit,"), TM.word("D1", "exactly")
WITHOUT, MAP = TM.word("D2", "Without"), TM.word("D2", "map")
TEN, TOMORROW = TM.word("D2", "ten"), TM.word("D2", "tomorrow.")
REL, POCKET = TM.word("D3", "Relativity"), TM.word("D3", "pocket,")
CHECK = TM.word("D3", "check")
WORLD0 = TM.end("D1") + 0.25
END0 = TM.word("D3", "Relativity") - 0.4
DURATION = TM.end("D3") + 1.3

CAPS = Captions(TM, ENV, words=WORDS, model=MODEL)
SEC0 = 9 * 3600 + 41 * 60 + 5.0
CITIES = [(-0.1, 51.5), (2.35, 48.9), (-3.7, 40.4), (3.4, 6.5), (31.2, 30.0), (37.6, 55.8), (29.0, 41.0), (36.8, -1.3),
          (28.0, -26.2), (12.5, 41.9), (13.4, 52.5), (55.3, 25.2), (72.9, 19.1), (-0.2, 5.6), (15.3, -4.3), (51.4, 35.7),
          (46.7, 24.7), (-7.6, 33.6), (18.0, 59.3), (21.0, 52.2), (-9.1, 38.7), (4.9, 52.4), (30.5, 50.4), (-17.4, 14.7),
          (39.3, -6.8), (32.6, 0.3), (44.4, 33.3), (67.0, 24.9), (77.2, 28.6), (-21.9, 64.1)]


def sat_y(t):
    """The satellite waits mid-frame, then launches upward on "launch"."""
    return 900 + 10 * math.sin(t * 1.2) - 2300 * in_out(prog(t, LAUNCH - 0.1, LAUNCH + 0.9)) ** 1.6


def fix_scene(t):
    img = backdrop(t, glow=(0.5, 0.36), floor=0.82, pool=(540, 1600, 420, 60))
    # the frequency card: 10.23 MHz -> 10.22999999543 MHz
    ca = window(t, 0.1, WORLD0 - 0.2, 0.4, 0.3)
    img = card(img, 90, 280, 900, 230, ca, 36, tint=0.4, sheen=(0.3 + 0.05 * t, 60, 0.07))
    u = in_out(prog(t, SLOW - 0.1, LAUNCH))
    target = "10.22999999543"
    shown = "10.23000000000" if u <= 0 else target if u >= 1 else \
        "".join(target[i] if u > i / len(target) else "10.23000000000"[i] for i in range(len(target)))

    def draw(c):
        label(c, "SATELLITE CLOCK, SET ON THE GROUND", W / 2, 340, 22, "mono", SMOKE, 255 * ca, "center", 0.16)
        glow_text(c, shown + " MHz", W / 2, 432, 54, "mono_bold", VIOLET if u > 0 else PAPER, 255 * ca, glow=0.4)
        label(c, "instead of 10.23 MHz", W / 2, 482, 24, "mono", SMOKE, 255 * ca * smooth(prog(t, LAUNCH - 0.2, LAUNCH + 0.3)),
              "center", 0.06)
        # launch: the satellite climbs out of frame on a streak of light
        q = prog(t, LAUNCH - 0.1, LAUNCH + 0.9)
        if 0 < q < 1:
            y = sat_y(t)
            c.drawLine(540, y + 60, 540, y + 520, paint(AMBER, 140 * (1 - q), sigma=14, stroke=28))
            c.drawLine(540, y + 60, 540, y + 440, paint(mix(AMBER, PAPER, 0.6), 255 * (1 - q), stroke=6))
    img = over(img, layer(draw))
    sa = smooth(prog(t, 0.2, 0.8))
    y = sat_y(t)
    if sa > 0.01 and y > -200:
        m = sat_mask(540, y, 88, -0.12 + 0.03 * math.sin(t)) * sa
        shadow(img, m, 20, 40, 26, 0.45)
        glass.glass(img, m, bevel=16, refract=14, frost=8, tint=0.32, lift=14, rim=1.5, sheen=(0.3 + 0.1 * t, 30, 0.16))
        img = over(img, layer(lambda c: glow_dot(c, 540, y, 13, VIOLET, 255 * sa, 4.0)))
    # the two clocks: on the ground the satellite clock lags; in orbit it locks to GROUND
    ka = window(t, GROUND - 0.3, WORLD0 - 0.2, 0.4, 0.3)
    if ka > 0.01:
        up = in_out(prog(t, ORBIT - 0.1, ORBIT + 0.8))
        lock = smooth(prog(t, EXACTLY - 0.1, EXACTLY + 0.4))
        lag = -2.5 * in_out(prog(t, TINY - 0.3, TINY + 1.2)) * (1 - lock)
        secs = SEC0 + (t - GROUND)
        img = clock(img, 290, 900, 175, secs, AMBER, "GROUND", None, t, 0.25)
        sy = lerp(900, 820, up)
        if up > 0:
            pts = orbit_points(795, sy + 80, 260, 76, -8, 200, 0.0)
            img = over(img, layer(lambda c: (orbit_line(c, pts, False, CYAN, 200 * up, 1.6),
                                             orbit_line(c, pts, True, CYAN, 230 * up, 1.6))))
        img = clock(img, 795, sy, 175, secs + lag, VIOLET, "IN ORBIT" if up > 0.5 else "SATELLITE", None, t, 0.35)
        st = "IN SYNC" if lock > 0.5 else ("TOO SLOW ON THE GROUND" if t > TINY else "")
        img = over(img, layer(lambda c: label(c, st, W / 2, 1230, 26, "mono_bold", CYAN if lock > 0.5 else SMOKE,
                                              255 * ka * smooth(prog(t, TINY, TINY + 0.3)), "center", 0.18)))
        if lock > 0:
            q = prog(t, EXACTLY - 0.1, EXACTLY + 0.7)
            img = over(img, layer(lambda c: [c.drawCircle(x, 900 if x < 500 else sy, 175 + 70 * out_cubic(q),
                                                          paint(CYAN, 255 * (1 - q), stroke=4)) for x in (290, 795)]))
    return img


def world_scene(t):
    img = backdrop(t, glow=(0.5, 0.5), floor=0.97, caustic=0.3)
    cx, cy, r = 540, 960, 400
    img, proj = earth(img, cx, cy, r, t, lon0=18 - 0.5 * (t - WORLD0), lat0=28, spin=0.0)
    d = in_out(prog(t, MAP - 0.2, TOMORROW + 0.3))
    rng = np.random.default_rng(7)
    offs = [(rng.normal(0, 1), rng.normal(0, 1)) for _ in CITIES]

    def draw(c):
        for (lon, lat), (ox, oy) in zip(CITIES, offs):
            x, y, z = proj(lon, lat)
            if z < 0.05:
                continue
            n = math.hypot(ox, oy) or 1
            dx, dy = x + ox / n * 42 * d, y + oy / n * 42 * d
            if d > 0:
                c.drawLine(x, y, dx, dy, paint(AMBER, 200 * d, stroke=2.5))
                c.drawCircle(x, y, 5, paint(AMBER, 230 * d, stroke=2))
            glow_dot(c, dx, dy, 6, CYAN, 255, 3.0)
    img = over(img, layer(draw))
    img = chip(img, "WITHOUT THE FIX", W / 2, 400, 34, VIOLET, smooth(prog(t, WITHOUT - 0.2, WITHOUT + 0.3)))
    for i, (lon, lat) in enumerate(((2.35, 48.9), (31.2, 30.0), (72.9, 19.1), (3.4, 6.5))):
        x, y, z = proj(lon, lat)
        if z > 0.1:
            img = chip(img, ">10 km", x + 90, y - 40, 24, AMBER, smooth(prog(t, TEN - 0.1 + i * 0.12, TEN + 0.2 + i * 0.12)))
    return img


def end_scene(t):
    img = backdrop(t, glow=(0.42, 0.40), floor=0.76, pool=(560, 1640, 320, 60))
    img = defocus(img, lambda c: [c.drawRRect(rrect(x, y, w_, h_, 40), paint(mix(CARD, PAPER, 0.2), 120))
                                  for x, y, w_, h_ in ((-80, 260, 300, 420), (850, 980, 320, 520))], 26, 0.7)
    ea = smooth(prog(t, REL - 0.2, REL + 0.5)) * (1 - smooth(prog(t, CHECK, CHECK + 0.8)))
    if ea > 0.01:
        img = glass_text(img, "Δτ ≈ Δt", W / 2, 400, 130, "light", tint=0.18, lift=20, caustic_t=t, a=ea, scale=0.94 + 0.06 * ea)
        img = glass_text(img, "(1 + Φ/c² − v²/2c²)", W / 2, 520, 70, "light", tint=0.18, lift=20, caustic_t=t,
                         a=smooth(prog(ea, 0.3, 1.0)))
    q = out_cubic(prog(t, POCKET - 0.7, POCKET + 0.5))
    if q > 0:
        # end on the pose of the film's first frame (part 1 at t = 0) so the Short loops
        cy = lerp(1900, 1110, q)
        rot = lerp(4, -11, q)
        img = phone(img, 540, cy, 470, 940, rot, t, pan=DOT)
        if t > CHECK:
            k = prog(t, CHECK, CHECK + 0.9)
            x, y = phone_xy(DOT, 540, cy, 1.0, DOT, rot)
            img = over(img, layer(lambda c: c.drawCircle(x, y, 20 + 90 * out_cubic(k), paint(CYAN, 255 * (1 - k), stroke=5))))
    return img


def draw_frame(t):
    if t < WORLD0:
        img = fix_scene(t)
    elif t < END0:
        img = world_scene(t)
    else:
        img = end_scene(t)
    for tc in (WORLD0, END0):
        k = 1 - abs(t - tc) / 0.3
        if k > 0:
            img = fade(img, smooth(k) * 0.85, (8, 14, 30))
    img = CAPS.draw(img, t)
    img = fade(img, max(1 - smooth(prog(t, 0, 0.3)), smooth(prog(t, DURATION - 0.35, DURATION))))
    return img


def samples_at(t):
    return 2 if LAUNCH - 0.1 < t < LAUNCH + 0.9 or POCKET - 0.7 < t < POCKET + 0.4 else 1


def sfx_events():
    return [(0.1, "clink", 0.45), (SLOW - 0.1, "dial", 0.5), (LAUNCH - 0.1, "launch", 0.55),
            (GROUND - 0.2, "clink", 0.4), (TINY, "detune", 0.2), (ORBIT - 0.1, "glass_whoosh", 0.45),
            (EXACTLY - 0.1, "lock", 0.7), (WORLD0 - 0.2, "glass_whoosh", 0.45), (MAP - 0.2, "detune", 0.55),
            (TEN - 0.1, "pop", 0.35), (TEN + 0.02, "pop", 0.35), (TEN + 0.14, "pop", 0.35), (TEN + 0.26, "pop", 0.35),
            (TOMORROW + 0.4, "sub_drop", 0.4), (END0 - 0.2, "reverse_swell", 0.45), (REL, "shimmer", 0.35),
            (POCKET - 0.6, "glass_whoosh", 0.5), (POCKET, "chime", 0.55), (CHECK, "ping", 0.5),
            (DURATION - 1.0, "chime", 0.35)]


MUSIC = dict(beds=[(0.0, WORLD0, "glass", 0.9), (WORLD0, END0, "tension", 0.55), (END0, DURATION, "resolve", 0.9)])
