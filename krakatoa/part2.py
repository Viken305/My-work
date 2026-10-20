"""Part 2, how loud: the ring crosses the Sunda Strait, reaches the ship at 64 km (eardrums) and the Batavia gas works at
160 km (a pressure spike), then a brass dB gauge swings past talk, pain and a jet engine to about 172 dB.

  python3 render.py part2 [--still 2,8,15]
"""
from film import *  # noqa: F401,F403

PART = "part2"
VO, _end = schedule(PART, first=0.6, gap=0.5)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)
DURATION = _end + 0.9

EAR_T = TM.word("A1", "eardrums")
GAUGE_T = TM.word("A2", "pressure")
SPIKE_T = TM.word("A2", "spike.")
METER_T = VO["A3"] - 0.2
DB_T = TM.word("A3", "decibels.", end=True)
JET_T = TM.word("A3", "jet")

CAPS = Captions(TM, ENV, sound=SOUND, harm=HARM)
SHIP_PT = destination(*KRAKATOA, math.radians(180), 64 / 6371)   # due south, in open water
SHIP_PT = (SHIP_PT[0], SHIP_PT[1])
PROJ = Ortho.fit(KRAKATOA, (290, 720), BATAVIA, (810, 735), 106.1, -6.3)


def ring_radius(t):
    """Radius of the blast ring on the strait map, keyed to the narration (reaches the ship on 'eardrums' and the gas
    works on 'spike')."""
    kx, ky, _ = PROJ(*KRAKATOA)
    sx, sy, _ = PROJ(*SHIP_PT)
    bx, by, _ = PROJ(*BATAVIA)
    return float(np.interp(t, [0.0, EAR_T, SPIKE_T, SPIKE_T + 3], [20, math.hypot(sx - kx, sy - ky),
                                                                     math.hypot(bx - kx, by - ky), 1500]))


def strait(c, t):
    sea_map(c, PROJ, key="strait", zoomed=True)
    kx, ky, _ = PROJ(*KRAKATOA)
    sx, sy, _ = PROJ(*SHIP_PT)
    bx, by, _ = PROJ(*BATAVIA)
    r = ring_radius(t)
    light(c, kx, ky, 110, LAVA, 200)
    ring(c, kx, ky, r, SULFUR, 255, 3.4)
    for k in range(1, 4):
        ring(c, kx, ky, r * (1 - 0.18 * k), SULFUR, 80 / k, 1.6, fringe=False, trail=0)
    pin(c, kx, ky, "KRAKATOA", None, 255, side=-1, size=26)
    # the ship: appears ahead of the ring, flashes red when hit
    sa = smooth(prog(t, 0.6, 1.4))
    hit = prog(t, EAR_T - 0.05, EAR_T + 0.6)
    if 0 < hit < 1:
        ring(c, sx, sy, 20 + 140 * out_cubic(hit), LAVA, 255 * (1 - hit), 2.6, fringe=False, trail=0)
        light(c, sx, sy, 120, LAVA, 200 * (1 - hit))
    pin(c, sx, sy, "SHIP, 64 KM", "NORHAM CASTLE", 255 * sa, rgb=LAVA if t > EAR_T else PAPER, side=1, size=26)
    dim_line(c, kx, ky + 26, sx, sy - 22, "64 KM", 255 * smooth(prog(t, 1.2, 2.0)), size=22)
    if t > EAR_T:
        label(c, "“the eardrums of over", sx - 120, sy + 120, 30, "serif", PAPER, 230 * smooth(prog(t, EAR_T, EAR_T + 0.5)))
        label(c, "half my crew…”", sx - 110, sy + 160, 30, "serif", PAPER, 230 * smooth(prog(t, EAR_T, EAR_T + 0.5)))
    # Batavia and its gas works gauge
    ba = smooth(prog(t, VO["A2"] - 0.3, VO["A2"] + 0.4))
    pin(c, bx, by, "BATAVIA, 160 KM", "GAS WORKS", 255 * ba, rgb=SULFUR if t > SPIKE_T else PAPER, side=-1, size=26)
    if t > GAUGE_T - 0.3:
        ga = smooth(prog(t, GAUGE_T - 0.3, GAUGE_T + 0.2))
        u = 0.15 + 0.85 * prog(t, GAUGE_T, SPIKE_T + 0.5)
        barograph(c, 140, 380, 800, 190, u, 0.82, 255 * ga, "PRESSURE GAUGE, BATAVIA GAS WORKS", 3)
    fig(c, 2, "THE SUNDA STRAIT, 27 AUG 1883", 70, 300, 255 * (1 - smooth(prog(t, GAUGE_T - 0.6, GAUGE_T - 0.2))))


def meter(c, t):
    paper(c)
    u = t - METER_T
    a = smooth(prog(u, 0, 0.5))
    # needle: sweeps up with the narration and lands on 172 with a little shudder
    v = 172 * out_cubic(prog(t, METER_T + 0.4, DB_T))
    if t > DB_T:
        v = 172 + 6 * math.exp(-(t - DB_T) * 5) * math.sin((t - DB_T) * 40)
    c.save()
    c.translate(W / 2, 980)
    sc = 0.9 + 0.1 * out_cubic(prog(u, 0, 0.8))
    c.scale(sc, sc)
    c.translate(-W / 2, -980)
    db_meter(c, W / 2, 980, 380, v, 255 * a)
    c.restore()
    label(c, f"{int(round(min(v, 172)))}", W / 2, 1150, 150, "mono_bold", SULFUR, 255 * a, "center", 0.02)
    label(c, "DECIBELS", W / 2, 1210, 24, "mono", PAPER, 230 * a, "center", 0.4)
    if t > JET_T - 0.2:   # the jet engine mark lights up, then the needle is past it
        ja = smooth(prog(t, JET_T - 0.2, JET_T + 0.3))
        ang = math.radians(200 + 140 * 150 / 180)
        light(c, W / 2 + math.cos(ang) * 420, 980 + math.sin(ang) * 420, 90, LAVA, 160 * ja)
    fig(c, 4, "SOUND LEVEL, 160 KM FROM THE BLAST (ESTIMATE)", W / 2, 300, 255 * a, "center", size=19)
    label(c, "+10 dB = 10× the power", W / 2, 1265, 24, "mono", FADED, 220 * smooth(prog(u, 1.5, 2.2)), "center", 0.1)


def draw_frame(c, t):
    if t < METER_T + 0.4:
        strait(c, t)
    if t > METER_T:
        c.saveLayerAlpha(None, int(255 * smooth(prog(t, METER_T, METER_T + 0.4))))
        meter(c, t)
        c.restore()
    CAPS.draw(c, t)
    edges(c, t, DURATION, 0.3, 0.3)


def sfx_events():
    kx = [(0.0, "whoosh", 0.5), (0.1, "ocean", 0.35),
          (EAR_T - 0.05, "low_hit", 0.6), (EAR_T, "ear_ring", 0.7),
          (SPIKE_T - 0.6, "pen_scratch", 0.7), (SPIKE_T - 0.02, "stamp", 0.5),
          (METER_T, "swish", 0.5), (METER_T + 0.4, "needle", 0.8), (DB_T, "trailer_hit", 0.55)]
    return kx


MUSIC = dict(beds=[(0.0, METER_T + 0.5, "deep", 0.7), (METER_T - 0.2, DURATION, "tension", 0.6)])
