"""Part 3, how far: pull back from the strait to the whole Indian Ocean while the ring keeps travelling; a clock counts
the four hours; the ring reaches Rodrigues (the 'cannon fire' again); a record plate.

  python3 render.py part3 [--still 2,6,11]
"""
from film import *  # noqa: F401,F403

PART = "part3"
VO, _end = schedule(PART, first=0.5, gap=0.5)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)
DURATION = _end + 1.0

ARRIVE_T = TM.word("B2", "cannon")          # the ring reaches Rodrigues
RECORD_T = VO["B3"]
FULL = (85.0, -13.5, 1060.0)
STRAIT = (105.9, -6.3, 21000.0)
ANG = 0.7505

CAPS = Captions(TM, ENV, sound=SOUND | {"cannon"}, harm=HARM)


def camera(t):
    u = in_out(prog(t, 0.2, VO["B1"] + 2.8))
    R = log_lerp(STRAIT[2], FULL[2], u)
    k = (math.log(STRAIT[2]) - math.log(R)) / (math.log(STRAIT[2]) - math.log(FULL[2]))
    k = k ** 0.7
    return STRAIT[0] + (FULL[0] - STRAIT[0]) * k, STRAIT[1] + (FULL[1] - STRAIT[1]) * k, R


def draw_frame(c, t):
    lon, lat, R = camera(t)
    proj = Ortho(lon, lat, R, W / 2, 860)
    sea_map(c, proj, zoomed=R > 6000)
    kx, ky, _ = proj(*KRAKATOA)
    rx, ry, _ = proj(*RODRIGUES)
    # the travelling ring: angular radius grows with time and touches Rodrigues on 'cannon'
    ang = ANG * (prog(t, 0.0, ARRIVE_T) ** 0.85) + 0.05 * max(0, t - ARRIVE_T)
    r = R * ang
    light(c, kx, ky, 90, LAVA, 180)
    ring(c, kx, ky, r, SULFUR, 255 * (1 - 0.6 * smooth(prog(t, ARRIVE_T + 0.8, DURATION))), 3.4)
    for k in range(1, 4):
        ring(c, kx, ky, r * (1 - 0.16 * k), SULFUR, 70 / k, 1.6, fringe=False, trail=0)
    pin(c, kx, ky, "KRAKATOA", None, 255, side=-1, size=26)
    ra = smooth(prog(t, 1.5, 2.5))
    hit = t > ARRIVE_T
    pin(c, rx, ry, "RODRIGUES", "4,800 KM", 255 * ra, rgb=SULFUR if hit else PAPER, side=1)
    if hit:
        q = prog(t, ARRIVE_T, ARRIVE_T + 0.8)
        ring(c, rx, ry, 20 + 120 * out_cubic(q), SULFUR, 255 * (1 - q), 2.4, fringe=False, trail=0)
        label(c, "“the distant roar", rx + 28, ry + 100, 32, "serif", PAPER, 230 * smooth(q * 2))
        label(c, "of heavy guns”", rx + 40, ry + 140, 32, "serif", PAPER, 230 * smooth(q * 2))
    # clock: time since the blast, keyed to the ring (4 hours at Rodrigues)
    hours = min(4.0, 4.0 * ang / ANG)
    hh, mm = int(hours), int((hours % 1) * 60)
    ca = smooth(prog(t, 0.3, 0.9)) * (1 - smooth(prog(t, RECORD_T - 0.3, RECORD_T + 0.2)))
    label(c, "TIME SINCE THE BLAST", W / 2, 470, 24, "mono", PAPER, 220 * ca, "center", 0.35)
    label(c, f"{hh}:{mm:02d}", W / 2, 620, 150, "mono_bold", SULFUR, 255 * ca, "center", 0.04)
    label(c, "HOURS", W / 2, 680, 24, "mono", FADED, 220 * ca, "center", 0.4)
    # record plate
    pa = smooth(prog(t, RECORD_T - 0.1, RECORD_T + 0.5))
    if pa > 0:
        big_number(c, "4,800 KM", 600, "FARTHEST SOUND IN RECORDED HISTORY", pa, size=140)
    fig(c, 5, "THE INDIAN OCEAN, 27 AUG 1883", 70, 300, 255 * smooth(prog(t, 2.0, 2.8)))
    CAPS.draw(c, t)
    edges(c, t, DURATION, 0.3, 0.3)


def sfx_events():
    return [(0.0, "descend", 0.5), (0.1, "ocean", 0.45), (2.0, "tick_roll", 0.35),
            (ARRIVE_T - 0.15, "distant_guns", 1.0), (RECORD_T, "low_hit", 0.45)]


MUSIC = dict(beds=[(0.0, DURATION, "night", 0.9), (ARRIVE_T - 1.0, DURATION, "wonder", 0.5)])
