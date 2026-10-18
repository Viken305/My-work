"""Part 1: Hook. A child under attack -> the skin turns germs away -> under the skin, the army, and Kai.

  python3 render.py part1 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part1"
VO, _end = schedule(PART, first=1.0, gap=0.7)
DURATION = _end + 2.2
TM = Timing(PART, VO)

ATTACK_T = TM.word("H1", "under attack") - 0.2
SKIN_T = VO["H2"] - 0.4                 # zoom into the skin
FAIL_T = TM.word("H2", "fail") - 0.3
DIVE_T = VO["H3"] - 0.6                 # dive under the skin
WAR_T = TM.word("H3", "war") - 0.2
IMMUNE_T = TM.word("H3", "immune system") - 0.2
KAI_T = TM.word("H3", "this is kai") - 0.1

CHILD_TRACK = Track([(0.0, "happy", 0.0), (ATTACK_T - 0.2, "shocked", 0.25), (ATTACK_T + 1.2, "worried", 0.5)])
_rng = np.random.default_rng(11)
SWARM = [(float(a), float(d), int(k)) for a, d, k in zip(_rng.uniform(0, 6.28, 22), _rng.uniform(300, 640, 22), _rng.integers(0, 3, 22))]
# skin impacts: (x, impact time, kind)
HITS = [(200 + (i * 7 % 12) * 140 + _rng.uniform(-40, 40), SKIN_T + 0.8 + i * 0.42 + _rng.uniform(-0.1, 0.1), i % 3) for i in range(14)]
ARMY = [("neu", -600, 0, 84, 0.0), ("helper", -360, -150, 72, 0.25), ("dendri", -380, 260, 66, 0.5), ("b", 360, 270, 76, 0.75),
        ("eater", 400, -130, 104, 1.0), ("neu", 620, 60, 80, 1.25)]
ARMY_TRACKS = [Track([(0.0, "neutral", 0.0), (DIVE_T + 1.2 + d, "determined", 0.3), (KAI_T + 0.4, "happy", 0.4), (KAI_T + 1.6, "determined", 0.4)])
               for _, _, _, _, d in ARMY]
KAI_TRACK = Track([(0.0, "neutral", 0.0), (KAI_T, "smug", 0.3), (KAI_T + 1.3, "wink", 0.25), (KAI_T + 2.2, "determined", 0.35)])


def microbe(c, x, y, s, t, kind, ang=0.0, mood="smug"):
    if kind == 0:
        bacterium(c, x, y, s, t, ang, mood=pose(mood) if isinstance(mood, str) else mood)
    elif kind == 1:
        virus(c, x, y, s * 0.8, t)
    else:
        fungus(c, x, y, s * 0.7, t, ang=ang)


def scene_child(c, t):
    k = in_out(prog(t, 0.0, SKIN_T + 0.4))
    zoom = lerp(1.0, 1.55, k)
    c.drawPaint(shaded(linear((0, 0), (0, H), [(60, 76, 130), (128, 100, 140)])))
    light(c, 1500, 120, 900, (255, 230, 210), 50)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(zoom, zoom)
    c.translate(-W / 2 - 160 * k, -H / 2 + 60 * k)
    c.drawRect(skia.Rect.MakeXYWH(-400, 860, W + 800, 600), fill((140, 106, 140)))
    alert = smooth(prog(t, ATTACK_T, ATTACK_T + 0.4))
    if alert > 0:
        light(c, 820, 620, 520, (255, 70, 90), 90 * alert * (0.75 + 0.25 * math.sin(t * 7)))
    p = CHILD_TRACK.at(t)
    child(c, 820, 880, 118, t, p, (0.3 * math.sin(t * 0.9), -0.2) if t < ATTACK_T else (-0.6, -0.4),
          blink_amount(t, CHILD_TRACK.change_times(), 3.6, 0.4))
    for i, (a, d, kind) in enumerate(SWARM):
        close = lerp(1.0, 0.72, smooth(prog(t, ATTACK_T, ATTACK_T + 3)))
        an = a + t * 0.25 * (1 if i % 2 else -1)
        x, y = 860 + math.cos(an) * d * 1.35 * close, 560 + math.sin(an) * d * 0.75 * close
        microbe(c, x, y, 22 + 6 * (i % 3), t + i, kind, math.degrees(an) + 90)
    c.restore()


def scene_skin(c, t):
    pan = in_out(prog(t, SKIN_T, DIVE_T + 1))
    c.save()
    c.translate(W / 2, 600)
    c.scale(1.12, 1.12)
    c.translate(-W / 2 - 120 * pan, -600)
    outside_world(c, t, 600)
    c.drawRect(skia.Rect.MakeXYWH(W, 0, 400, 600), fill((205, 175, 185)))
    skin_wall(c, -100, 600, W + 400, 480, t)
    c.drawRect(skia.Rect.MakeXYWH(-100, 600, W + 400, 480), fill((90, 10, 40), 50))
    for i, (x, th, kind) in enumerate(HITS):
        u = t - th
        if u < -1.4:
            continue
        if u < 0:          # incoming
            k = 1 + u / 1.4
            px, py = x - 160 * (1 - k), lerp(80, 556, in_cubic(k))
            ang = 100
            mood = "smug"
        else:              # bounce back, spinning, surprised
            k = out_cubic(prog(u, 0, 1.6))
            px, py = x + 260 * k * (1 if i % 2 else -1), 556 - 330 * math.sin(math.pi * k * 0.8)
            ang = 100 + 540 * k
            mood = "shocked"
            if u < 0.35:
                sparkle(c, x, 594, 60 * (1 - u / 0.35), 255, (255, 250, 230))
                for j in range(4):
                    an = math.radians(-160 + j * 45)
                    c.drawLine(x + math.cos(an) * 30, 594 + math.sin(an) * 30, x + math.cos(an) * (60 + 80 * u), 594 + math.sin(an) * (60 + 80 * u), stroke(WHITE, 4, 230 * (1 - u / 0.35)))
        microbe(c, px, py, 54, t + i, kind, ang, mood)
    c.restore()
    chip(c, "BACTERIA · VIRUSES · FUNGI", 960, 110, (255, 230, 220), t, SKIN_T + 0.6, FAIL_T - 0.3)
    chip(c, "ALMOST ALL OF THEM FAIL", 960, 110, (255, 214, 120), t, FAIL_T, DIVE_T + 0.6)


def scene_army(c, t):
    k = in_out(prog(t, DIVE_T, DURATION))
    cam = Cam(0, lerp(40, -10, k), lerp(1.0, 1.12, k))
    body_world(c, t, cam)
    cam.push(c, 1.0)
    for i, (kind, x, y, r, d) in enumerate(ARMY):
        g = out_back(prog(t, DIVE_T + 0.8 + d, DIVE_T + 1.4 + d), 1.6)
        if g <= 0:
            continue
        p = ARMY_TRACKS[i].at(t)
        rr = r * g
        yy = y + 8 * math.sin(t * 1.5 + i)
        look = (-0.6 if x > 0 else 0.6, 0.1) if t < KAI_T else ((-0.8 if x > 0 else 0.8), 0.3)
        if kind == "neu":
            neutrophil(c, x, yy, rr, t, p, look, seed=i)
        elif kind == "helper":
            t_cell(c, x, yy, rr, t, "helper", p, look, seed=i)
        elif kind == "dendri":
            dendritic(c, x, yy, rr, t, p, look, seed=i)
        elif kind == "b":
            b_cell(c, x, yy, rr, t, p, look, seed=i)
        else:
            eater(c, x, yy, rr, t, p, look, blink_amount(t, (), 4.0, i))
    # Kai hops in from below with a squash on landing
    if t > KAI_T - 0.6:
        u = prog(t, KAI_T - 0.6, KAI_T + 0.2)
        y = lerp(700, 60, out_back(u, 1.2))
        hop = -0.8 * math.sin(math.pi * prog(t, KAI_T + 0.1, KAI_T + 0.5))
        kai(c, 0, y, 175, t, KAI_TRACK.at(t), (0.0, 0.1), blink_amount(t, KAI_TRACK.change_times(), 3.9, 0.3), hop=hop)
        if KAI_T + 0.1 < t < KAI_T + 0.8:
            r0 = 170 * (1.1 + 1.2 * prog(t, KAI_T + 0.1, KAI_T + 0.8))
            c.drawCircle(0, 40, r0, stroke(WHITE, 6, 200 * (1 - prog(t, KAI_T + 0.1, KAI_T + 0.8))))
    cam.pop(c)
    near_blur(c, [(-60, 1040, 240), (1990, 80, 210)], t, (190, 70, 100), 0.9)
    ta = smooth(prog(t, WAR_T, WAR_T + 0.5)) * (1 - smooth(prog(t, KAI_T - 0.8, KAI_T - 0.2)))
    if ta > 0:
        text(c, "THERE IS A", 960, 130, 40, WHITE, 255 * ta, 800, spacing=12)
        tr = lerp(26, 12, out_cubic(prog(t, WAR_T, WAR_T + 2)))
        text(c, "WAR INSIDE YOU", 960, 230, 96, (255, 214, 120), 255 * ta, 800, spacing=tr)
    chip(c, "YOUR IMMUNE SYSTEM · NEARLY 2 TRILLION CELLS", 960, 1010, (255, 220, 210), t, IMMUNE_T, KAI_T + 0.2)
    chip(c, "KAI · A KILLER T CELL", 960, 1010, (255, 170, 150), t, KAI_T + 0.5, DURATION - 0.3)


def draw_frame(c, t):
    if t < SKIN_T + 0.9:
        xfade(c, t, SKIN_T, 0.9, scene_child, scene_skin, 0.35)
    else:
        xfade(c, t, DIVE_T, 1.0, scene_skin, scene_army, 0.3)
    fade(c, t, DURATION, 0.8, 0.6)


def sfx_events():
    ev = [(0.2, "swell_soft", 0.6), (ATTACK_T, "flicker", 0.8), (ATTACK_T + 0.05, "boom", 0.5), (SKIN_T, "whoosh_long", 0.7)]
    ev += [(th, "pop", 0.8) for _, th, _ in HITS] + [(th + 0.02, "tink", 0.5) for _, th, _ in HITS]
    ev += [(FAIL_T, "ding", 0.6), (DIVE_T, "whoosh_long", 0.8), (DIVE_T + 0.3, "bubble", 0.6)]
    ev += [(DIVE_T + 0.8 + d, "pop", 0.6) for *_, d in ARMY] + [(WAR_T, "boom", 0.7), (WAR_T + 0.05, "shine", 0.7)]
    ev += [(KAI_T - 0.5, "whoosh", 0.7), (KAI_T + 0.15, "pop", 1.0), (KAI_T + 1.3, "ding", 0.7)]
    return ev


MUSIC = dict(
    chords=[(0.0, 50, (0, 7, 12, 16, 19)), (ATTACK_T, 46, (0, 7, 12, 15, 18)), (SKIN_T, 48, (0, 7, 12, 15, 19)), (DIVE_T, 45, (0, 7, 12, 15, 19)),
            (WAR_T, 43, (0, 7, 12, 16, 19, 24)), (KAI_T, 48, (0, 7, 12, 16, 19))],
    plucks=[(0.3, ATTACK_T), (SKIN_T + 0.5, DURATION)], bpm=104, rises=[(DIVE_T - 1.5, WAR_T)],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
