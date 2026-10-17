"""Part 3: Chapter 2, First Responders. One continuous camera move through a vertical slice of tissue:
the wound above, the battlefield in the middle, a blood vessel below.

  python3 render.py part3 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part3"
VO, _end = schedule(PART, first=3.2, gap=0.8)
DURATION = _end + 2.6
TM = Timing(PART, VO)

# ---------------------------------------------------------------- beats (from the narration)
ALARM_T = TM.word("F1", "sound the alarm") - 0.3
VESSEL_T = TM.word("F1", "blood vessels") - 0.6
LEAK_T = TM.word("F1", "widen") - 0.2
RED_T = TM.word("F1", "red") - 0.2
NEUTRO_T = TM.word("F2", "neutrophils") - 0.3
EXIT0 = VO["F2"] + 0.2
FIGHT_T = TM.word("F2", "attack") - 0.4
BURST_T = TM.word("F3", "burst open") - 0.2
NET_T = TM.word("F3", "nets of dna") - 0.3
PUS_T = TM.word("F3", "pus") - 0.3
EATER_T = VO["F4"] - 0.4
BITES = [TM.word("F4", "swallow") + 0.1, TM.word("F4", "dissolve") + 0.2, TM.word("F4", "single") + 0.1, TM.word("F4", "dozens") + 0.1]

VY, VH = 560, 220                      # vessel centre / height (world)
KAI = (760, 560)                       # Kai rides in the vessel
CAM = CamPath([(0.0, 0, -420, 1.0), (VO["F1"], 0, -250, 1.22), (VESSEL_T, 0, -230, 1.25), (VESSEL_T + 2.2, 130, 400, 1.18),
               (EXIT0, 80, 400, 1.2), (EXIT0 + 3.4, 40, 300, 1.12), (FIGHT_T + 1.2, 0, -150, 1.05), (VO["F3"], 60, -170, 1.1),
               (BURST_T - 0.2, 220, -180, 1.42), (NET_T + 2.0, 220, -180, 1.34), (PUS_T + 0.6, 0, -60, 0.98), (EATER_T, -80, -80, 1.0),
               (EATER_T + 2.4, -320, -140, 1.22), (DURATION, -300, -140, 1.28)])

# ---------------------------------------------------------------- cast
_rng = np.random.default_rng(31)
NET_C = (230, -180)
# bacteria: (home, role) roles: net / neu<i> / eat<i>
BAC = []
for i in range(8):
    an = i / 8 * 6.28 + 0.3
    BAC.append(((NET_C[0] + math.cos(an) * 220, NET_C[1] + math.sin(an) * 150), "net"))
for i, hp in enumerate([(-420, -620), (400, 160), (-420, 60)]):
    BAC.append((hp, f"neu{i}"))
for i, hp in enumerate([(-170, -320), (-60, -40), (-200, 60), (-20, -230)]):
    BAC.append((hp, f"eat{i}"))
BAC_SEED = [(_rng.uniform(0, 6.28), _rng.uniform(0.4, 2.4)) for _ in BAC]

TISSUE = [((-800, -400), 86, 0.0), ((30, -480), 80, 1.1), ((590, -30), 84, 2.2)]
TISSUE_TRACKS = [Track([(0.0, "hurt", 0.0), (ALARM_T + 0.15 * i, "shout", 0.25), (ALARM_T + 1.6 + 0.15 * i, "hurt", 0.4),
                        (ALARM_T + 2.3 + 0.2 * i, "shout", 0.25), (LEAK_T + 0.5, "worried", 0.5), (FIGHT_T + 0.5, "happy", 0.5)])
                 for i in range(3)]

# neutrophils: exit x, exit time, target role
NEU = [(-60, EXIT0 + 0.0, "net"), (-420, EXIT0 + 0.5, "neu0"), (380, EXIT0 + 0.9, "neu1"), (-250, EXIT0 + 1.3, "neu2"),
       (180, EXIT0 + 1.7, "patrol0"), (-600, EXIT0 + 2.1, "patrol1"), (440, EXIT0 + 2.5, "patrol2")]
PATROL = [(120, 90), (-1000, 140), (700, -330)]
NEU_TRACKS = []
for i, (_, te, role) in enumerate(NEU):
    keys = [(0.0, "worried", 0.0), (te + 0.5, "determined", 0.3), (FIGHT_T + 0.3 + 0.2 * i, "angry", 0.35)]
    if role == "net":
        keys += [(BURST_T - 1.0, "focused", 0.4), (BURST_T - 0.35, "shout", 0.2)]
    elif role.startswith("neu"):
        keys += [(FIGHT_T + 2.6 + 0.3 * i, "chew", 0.3), (PUS_T - 0.4 + 0.25 * i, "exhausted", 0.8)]
    else:
        keys += [(PUS_T + 0.5, "worried", 0.5)]
    NEU_TRACKS.append(Track(keys))
DIE = {1: 0.0, 2: 0.35, 3: 0.7}        # these neutrophils die in battle (pus)

BAC_TRACKS = [Track([(0.0, "smug", 0.0), (NEUTRO_T + 0.8 + 0.1 * (i % 5), "shocked", 0.25), (NEUTRO_T + 2.0 + 0.1 * (i % 5), "worried", 0.5)])
              for i in range(len(BAC))]
KAI_TRACK = Track([(0.0, "neutral", 0.0), (ALARM_T + 0.6, "shocked", 0.22), (ALARM_T + 1.8, "focused", 0.45), (LEAK_T + 0.6, "worried", 0.5),
                   (EXIT0 + 0.6, "cheer", 0.35), (EXIT0 + 3.6, "determined", 0.5), (PUS_T + 0.3, "worried", 0.5), (BITES[1], "smug", 0.5)])
EATER_TRACK = Track([(0.0, "happy", 0.0)] + sum([[(b - 0.9, "shocked", 0.2), (b - 0.6, "gulp", 0.25), (b, "chew", 0.15)] for b in BITES], []) +
                    [(BITES[-1] + 1.4, "laugh", 0.4)])


# ---------------------------------------------------------------- motion
def bac_wander(i, t):
    (hx, hy), _ = BAC[i]
    ph, sp = BAC_SEED[i]
    x = hx + 40 * math.sin(t * 0.6 * sp + ph) + 20 * math.sin(t * 1.3 + ph * 2)
    y = hy + 30 * math.cos(t * 0.5 * sp + ph)
    enter = out_cubic(prog(t, 0.2 + 0.18 * i, 2.6 + 0.18 * i))      # pour in through the wound above
    return lerp(hx * 0.3, x, enter), lerp(-1200, y, enter)


def neu_pos(i, t):
    """Neutrophil path: wait in the blood, squeeze through the vessel wall, rush to the target."""
    ex, te, role = NEU[i]
    wall = VY - VH * 0.5 - 10
    if t < te:
        return ex + 30 * math.sin(t * 2 + i), VY - 40 + 20 * math.sin(t * 1.6 + i), 0.0
    if t < te + 0.8:
        u = in_out(prog(t, te, te + 0.8))
        return ex, lerp(VY - 40, wall - 70, u), u
    if role == "net":
        tgt = NET_C
    elif role.startswith("neu"):
        j = int(role[3:])
        b = 8 + j
        tgt = bac_wander(b, min(t, FIGHT_T + 1.8))
        tgt = (tgt[0] - 70, tgt[1] + 20)
    else:
        tgt = PATROL[int(role[6:])]
    u = out_cubic(prog(t, te + 0.8, te + 0.8 + 3.2))
    x = lerp(ex, tgt[0], u) + 25 * math.sin(t * 1.4 + i) * u
    y = lerp(wall - 70, tgt[1], u) + 18 * math.cos(t * 1.2 + i) * u
    if i in DIE:
        sink = smooth(prog(t, PUS_T + DIE[i], PUS_T + DIE[i] + 2.5))
        y += 160 * sink
    return x, y, 1.0


def squeeze_of(phase):
    """Diapedesis: thin and tall while crossing the wall, overshoot pop when out."""
    if phase <= 0:
        return (1.0, 1.0)
    if phase < 1:
        k = math.sin(math.pi * phase)
        return (1 - 0.45 * k, 1 + 0.5 * k)
    return (1.0, 1.0)


def net_catch(i, t):
    """Bacteria caught in the NET: pulled to the web and stuck, struggling."""
    x, y = bac_wander(i, t)
    k = out_cubic(prog(t, NET_T - 0.2, NET_T + 1.2))
    if k <= 0:
        return x, y, 0.0
    an = (i / 8) * 6.28 + 0.3
    sx, sy = NET_C[0] + math.cos(an) * 150 + 8 * math.sin(t * 9 + i), NET_C[1] + math.sin(an) * 105 + 6 * math.cos(t * 8 + i)
    return lerp(x, sx, k), lerp(y, sy, k), k


def eater_pos(t):
    u = out_cubic(prog(t, EATER_T, EATER_T + 2.2))
    return lerp(-1350, -390, u), -150 + 12 * math.sin(t * 1.3)


def eat_state(j, t):
    """For eater-bacterium j: (x, y, alive, scale). Reach, pull to mouth, gone at the bite."""
    b = 11 + j
    bx, by = bac_wander(b, t)
    bite = BITES[j]
    ex, ey = eater_pos(t)
    mouth = (ex, ey - 0.22 * 190 + 0.36 * 190 + 30)
    k = in_cubic(prog(t, bite - 0.75, bite))
    return lerp(bx, mouth[0], k), lerp(by, mouth[1], k), t < bite, 1 - 0.45 * k


# ---------------------------------------------------------------- drawing
def vessel_at(c, t):
    leak = smooth(prog(t, LEAK_T, LEAK_T + 2.5))
    hh = VH * (1 + 0.3 * leak)
    top, bot = VY - hh / 2, VY + hh / 2
    c.drawRect(skia.Rect.MakeXYWH(-2200, top, 4400, hh), shaded(linear((0, top), (0, bot), [(100, 12, 30), (175, 32, 48), (100, 12, 30)])))
    light(c, 0, VY, 900, (255, 90, 80), 20 + 30 * leak)
    rng = np.random.default_rng(8)
    for k in range(46):
        u = (rng.random() + t * 260 / 4400 * rng.uniform(0.7, 1.2)) % 1.0
        rbc(c, -2200 + u * 4400, VY + rng.uniform(-0.33, 0.33) * hh, 30, t, rng.uniform(0.1, 0.85), 255, rng.random() * 9)
    # Kai, clinging on inside the vessel while the blood rushes past
    p = KAI_TRACK.at(t)
    look = (-0.3, -0.9) if ALARM_T + 0.5 < t < EXIT0 + 4 else (-0.6, -0.4)
    kai(c, KAI[0], KAI[1] + 8 * math.sin(t * 1.7), 96, t, p, look, blink_amount(t, KAI_TRACK.change_times(), 3.9, 0.6), vel=(-120, 0))
    # walls: segments open into gaps where neutrophils squeeze through
    gaps = [(ex, te) for ex, te, _ in NEU]
    for s in (-1, 1):
        yy = VY + s * hh / 2
        x = -2200
        while x < 2200:
            seg = 90
            gapw = 0
            for gx, te in gaps:
                if s < 0 and abs(x + seg / 2 - gx) < seg * 0.6:
                    gapw = max(gapw, 70 * smooth(prog(t, te - 0.6, te)) * (1 - 0.6 * smooth(prog(t, te + 0.9, te + 2.0))))
            gapw = max(gapw, leak * 14 * (0.5 + 0.5 * math.sin(x * 0.07)))
            w = seg - gapw
            for half in (0, 1):
                hw = w / 2
                xx = x + (0 if half == 0 else seg - hw)
                c.drawRRect(rrect(xx + 2, yy - 16, hw - 4, 32, 16), shaded(linear((0, yy - 16), (0, yy + 16), [lighten(TISSUE_HI, 0.18), darken(TISSUE_HI, 0.3)])))
            x += seg


def draw_frame(c, t):
    cam = CAM.at(t)
    body_world(c, t, cam)
    cam.push(c, 1.0)
    vessel_at(c, t)
    # alarm: rings + signal molecules drifting down towards the vessel
    for i, ((x, y), r, sd) in enumerate(TISSUE):
        if ALARM_T < t < FIGHT_T:
            k = ((t - ALARM_T) * 0.7 + i * 0.33) % 1.0
            a = smooth(prog(t, ALARM_T, ALARM_T + 0.5)) * (1 - smooth(prog(t, FIGHT_T - 1, FIGHT_T)))
            for j in range(3):
                u = (k + j / 3) % 1.0
                c.drawCircle(x, y, r * (1.1 + 1.8 * u), stroke(ALARM, 6 * (1 - u) + 1, 220 * (1 - u) * a))
            rngm = np.random.default_rng(40 + i)
            for j in range(14):
                u = ((t - ALARM_T) * 0.25 + rngm.random()) % 1.0
                mx = x + rngm.uniform(-120, 120) + 30 * math.sin(t + j)
                my = lerp(y, VY - VH * 0.6, u)
                c.drawCircle(mx, my, 6, add(ALARM, 200 * a * math.sin(math.pi * u)))
    for i, ((x, y), r, sd) in enumerate(TISSUE):
        tr = TISSUE_TRACKS[i]
        tissue_cell(c, x, y, r, t, tr.at(t), (0.0, 0.6) if t > LEAK_T else (0.2 * (i - 1), -0.2),
                    blink_amount(t, tr.change_times(), 4.3, i * 1.3), seed=sd)
    # NET (behind the bacteria it holds)
    if t > BURST_T:
        k = prog(t, BURST_T, BURST_T + 1.4)
        net(c, NET_C[0], NET_C[1], 60 + 240 * out_cubic(k), t, 255, seed=5)
        if t < BURST_T + 0.6:
            light(c, NET_C[0], NET_C[1], 420, (230, 190, 255), 255 * math.exp(-(t - BURST_T) * 6), core=1)
    # bacteria
    for i, ((hx, hy), role) in enumerate(BAC):
        p = BAC_TRACKS[i].at(t)
        if role == "net":
            x, y, k = net_catch(i, t)
            bacterium(c, x, y, 34, t, 40 * i + 15 * math.sin(t * 2 + i), mood=p, wiggle=4.0 if k > 0.5 else 1.2)
        elif role.startswith("neu"):
            j = int(role[3:])
            nx, ny, _ = neu_pos(1 + j, t)
            x, y = bac_wander(i, t)
            ke = in_cubic(prog(t, FIGHT_T + 1.8 + 0.3 * j, FIGHT_T + 2.6 + 0.3 * j))
            if ke >= 1:
                continue
            x, y = lerp(x, nx, ke), lerp(y, ny, ke)
            bacterium(c, x, y, 34 * (1 - 0.6 * ke), t, 30 * i, mood=p, wiggle=1.5 + 3 * ke, a=255 * (1 - ke ** 3))
        else:
            j = int(role[3:])
            x, y, alive, sc = eat_state(j, t)
            if alive:
                bacterium(c, x, y, 34 * sc, t, 30 * i + 20 * math.sin(t), mood=p, wiggle=3.5 if t > BITES[j] - 1.2 else 1.2)
    # neutrophils
    for i, (ex, te, role) in enumerate(NEU):
        if role == "net" and t > BURST_T + 0.6:
            continue
        x, y, ph = neu_pos(i, t)
        tr = NEU_TRACKS[i]
        p = tr.at(t)
        sq = squeeze_of(ph if t < te + 0.8 else 2)
        if te + 0.8 <= t < te + 1.3:      # pop out with overshoot
            u = prog(t, te + 0.8, te + 1.3)
            k = math.sin(math.pi * u) * (1 - u)
            sq = (1 + 0.25 * k, 1 - 0.2 * k)
        burst = prog(t, BURST_T, BURST_T + 0.6) if role == "net" else 0.0
        if role == "net" and BURST_T - 0.6 < t < BURST_T:     # swelling + glow before the burst
            g = prog(t, BURST_T - 0.6, BURST_T)
            light(c, x, y, 200 * (1 + g), (230, 180, 255), 200 * g)
            sq = (1 + 0.15 * g + 0.03 * math.sin(t * 60), 1 + 0.15 * g)
        look = (0.0, -0.8) if t < te + 1.0 else ((0.6, -0.3) if x < 0 else (-0.6, -0.3))
        if i in DIE and t > PUS_T + DIE[i]:
            d = smooth(prog(t, PUS_T + DIE[i], PUS_T + DIE[i] + 1.8))
            c.saveLayerAlpha(None, int(255 * (1 - 0.45 * d)))
            neutrophil(c, x, y, 60, t, p, look, seed=i, burst=burst, blink=blink_amount(t, tr.change_times(), 4.0, i), squeeze=sq)
            c.drawCircle(x, y, 64, fill((120, 110, 130), 120 * d))
            c.restore()
        else:
            neutrophil(c, x, y, 60, t, p, look, seed=i, burst=burst, blink=blink_amount(t, tr.change_times(), 4.0, i), squeeze=sq)
    # the big eater
    if t > EATER_T - 0.2:
        ex, ey = eater_pos(t)
        hands = [None, None]
        belly = []
        chomp = 0.0
        for j, b in enumerate(BITES):
            bx, by, alive, _ = eat_state(j, t)
            if b - 1.2 < t < b - 0.05:
                reach = smooth(prog(t, b - 1.2, b - 0.8))
                rest = (ex + 1.15 * 190 * (1 if j % 2 else -1), ey + 0.45 * 190)
                hands[j % 2] = (lerp(rest[0], bx, reach), lerp(rest[1], by, reach))
            if t >= b:
                u = out_cubic(prog(t, b, b + 1.0))
                side = -1 if j % 2 == 0 else 1
                belly.append((lerp(0.0, side * (0.5 + 0.08 * (j // 2)), u), lerp(-0.4, 0.06 - 0.14 * (j // 2), u), 0.12, 0.7 * smooth(prog(t, b + 0.6, b + 9.0))))
                chomp = max(chomp, math.exp(-(t - b) * 8))
        p = EATER_TRACK.at(t)
        if p["mw"] < 0.7 and any(b < t < b + 1.0 for b in BITES):    # chewing motion
            p = dict(p)
            p["open"] = 0.06 + 0.12 * (0.5 + 0.5 * math.sin(t * 16))
        target = None
        for j, b in enumerate(BITES):
            if b - 1.4 < t < b:
                target = eat_state(j, t)[:2]
        look = (clamp((target[0] - ex) / 300, -1, 1), clamp((target[1] - ey) / 300, -1, 1)) if target else (0.3, 0.1)
        eater(c, ex, ey, 190, t, p, look, blink_amount(t, EATER_TRACK.change_times(), 4.2, 2.0), hands, belly, chomp=chomp)
    cam.pop(c)
    near_blur(c, [(-80 - cam.x * 0.4, 1060 - cam.y * 0.3, 240), (2010 - cam.x * 0.4, 60 - cam.y * 0.3, 210)], t, (190, 70, 100), 0.9)
    # warm inflammation grade
    heat = smooth(prog(t, RED_T, RED_T + 1.0)) * (1 - smooth(prog(t, FIGHT_T, FIGHT_T + 3)))
    if heat > 0:
        c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.75, [((255, 80, 60), 0), ((255, 80, 60), 70 * heat)], [0.4, 1])))
    # labels
    chip(c, "ALARM SIGNALS", 960, 110, ALARM, t, ALARM_T + 0.4, VESSEL_T + 0.6)
    for k, (s, rgb) in enumerate([("RED", (255, 120, 110)), ("SWOLLEN", (255, 170, 130)), ("WARM", ALARM)]):
        chip(c, s, 620 + k * 340, 110, rgb, t, RED_T + 0.25 * k, VO["F2"] + 0.4)
    chip(c, "NEUTROPHILS", 960, 110, (240, 220, 255), t, NEUTRO_T, FIGHT_T + 1.5)
    chip(c, "NET OF DNA", 960, 110, (220, 170, 255), t, NET_T, PUS_T - 0.3)
    chip(c, "PUS = DEAD NEUTROPHILS", 960, 110, (230, 220, 230), t, PUS_T + 0.2, EATER_T)
    chip(c, "MACROPHAGE · THE BIG EATER", 960, 110, (150, 220, 240), t, TM.word("F4", "macrophages") - 0.2, BITES[2])
    n = sum(1 for b in BITES if t > b)
    if n:
        k = out_back(prog(t, max(b for b in BITES if t > b), max(b for b in BITES if t > b) + 0.4), 2.0)
        text(c, f"× {n}", 1720, 180, 70 * (0.7 + 0.3 * k), (150, 220, 240), 255 * smooth(prog(t, BITES[0], BITES[0] + 0.3)) * (1 - smooth(prog(t, DURATION - 1.2, DURATION - 0.6))), 800)
    chapter_title(c, t, 2, "FIRST RESPONDERS", ALARM, 0.2, 2.9)
    fade(c, t, DURATION, 0.6, 0.8)


def sfx_events():
    ev = [(0.2, "swell_soft", 0.6), (0.5, "whoosh_long", 0.6)] + [(0.4 + 0.18 * i, "bubble", 0.2) for i in range(0, 15, 3)]
    ev += [(ALARM_T + 0.15 * i, "blip", 0.8) for i in range(3)] + [(ALARM_T + 2.3, "ding", 0.6), (VESSEL_T, "whoosh_long", 0.6), (LEAK_T, "rumble", 0.5),
           (RED_T, "swell_soft", 0.5)]
    ev += [(te + 0.4, "pop", 0.7) for _, te, _ in NEU] + [(te + 0.1, "slide", 0.3) for _, te, _ in NEU]
    ev += [(FIGHT_T, "whoosh", 0.7), (FIGHT_T + 2.0, "bubble", 0.6), (FIGHT_T + 2.4, "bubble", 0.6), (BURST_T - 0.6, "riser", 0.6), (BURST_T, "boom", 0.6),
           (BURST_T + 0.05, "shimmer", 0.9), (NET_T, "sizzle", 0.4), (PUS_T, "flicker", 0.4), (EATER_T, "slide", 0.5)]
    for b in BITES:
        ev += [(b - 1.1, "whoosh_soft", 0.5), (b, "pop", 1.0), (b + 0.02, "bubble", 0.8), (b + 0.3, "tink", 0.4), (b + 0.55, "tink", 0.4)]
    ev += [(BITES[-1] + 1.4, "chime", 0.7), (DURATION - 1.5, "swell_soft", 0.5)]
    return ev


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 15, 19)), (ALARM_T, 44, (0, 7, 12, 15, 18)), (VO["F2"], 47, (0, 7, 12, 16, 19)), (VO["F3"], 45, (0, 7, 12, 15, 19)),
            (BURST_T, 43, (0, 7, 12, 16, 19, 24)), (PUS_T, 41, (0, 7, 12, 15, 19)), (EATER_T, 48, (0, 7, 12, 16, 19)), (BITES[-1] + 1.4, 50, (0, 7, 12, 16, 21))],
    plucks=[(VO["F1"], ALARM_T), (VO["F2"], PUS_T), (EATER_T, DURATION)], bpm=104, rises=[(EXIT0 - 1.5, EXIT0), (BURST_T - 2.5, BURST_T)],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
