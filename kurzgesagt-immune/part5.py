"""Part 5: Chapter 4, Special Forces. The lock clicks and one helper T cell becomes an army; helpers send in killer T
cells (Kai leads) to make an infected cell self-destruct; B cells become plasma-cell factories; antibodies tag bacteria
so the big eater can catch them.

  python3 render.py part5 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part5"
VO, _end = schedule(PART, first=3.0, gap=0.8)
DURATION = _end + 1.8
TM = Timing(PART, VO)

LOCK_T = TM.word("S1", "lock") - 0.3
CLICK_T = TM.word("S1", "finds its match") - 0.1
COPY_T = TM.word("S1", "copying") - 0.4
ARMY_T = TM.word("S1", "army of thousands") - 0.3
CMD_T = VO["S2"] - 0.5
KILL_T = TM.word("S2", "killer t cells") - 0.3
KAI_T = TM.word("S2", "like kai") - 0.2
HUNT_T = TM.word("S2", "hunt down") - 0.2
DESTRUCT_T = TM.word("S2", "self-destruct") - 0.4
B_T = VO["S3"] - 0.5
WAKE_T = TM.word("S3", "wake up") - 0.2
PLASMA_T = TM.word("S3", "plasma cells") - 0.3
FIRE_T = TM.word("S3", "antibodies") - 0.3
TAG_T = VO["S4"] - 0.4
EAT_T = TM.word("S4", "big eaters") - 0.8

HELPER_TRACK = Track([(0.0, "neutral", 0.0), (CLICK_T, "shocked", 0.2), (CLICK_T + 0.8, "cheer", 0.35), (COPY_T, "determined", 0.4)])
CMD_TRACK = Track([(0.0, "determined", 0.0), (KILL_T - 0.3, "shout", 0.25), (KILL_T + 1.2, "determined", 0.4), (DESTRUCT_T + 0.4, "smug", 0.4)])
KAI_TRACK = Track([(0.0, "determined", 0.0), (KAI_T, "smug", 0.3), (KAI_T + 0.9, "wink", 0.2), (HUNT_T, "focused", 0.35),
                   (DESTRUCT_T - 0.5, "angry", 0.3), (DESTRUCT_T + 1.4, "smug", 0.4)])
CLONES = [Track([(0.0, "determined", 0.0), (HUNT_T + 0.2 * i, "focused", 0.35), (DESTRUCT_T + 1.4 + 0.2 * i, "happy", 0.4)]) for i in range(4)]
INFECTED = Track([(0.0, "worried", 0.0), (HUNT_T + 0.6, "shocked", 0.2), (HUNT_T + 1.6, "hurt", 0.4), (DESTRUCT_T - 0.3, "exhausted", 0.5)])
B_TRACK = Track([(0.0, "neutral", 0.0), (B_T, "neutral", 0.0), (WAKE_T, "shocked", 0.2), (WAKE_T + 0.8, "determined", 0.4),
                 (FIRE_T + 0.4, "shout", 0.25), (FIRE_T + 2.0, "determined", 0.4)])
BAC_TAG = [Track([(0.0, "smug", 0.0), (TAG_T + 0.6 + 0.3 * i, "shocked", 0.2), (TAG_T + 1.6 + 0.3 * i, "worried", 0.5)]) for i in range(4)]
EATER_TRACK = Track([(0.0, "neutral", 0.0), (TAG_T + 1.4, "happy", 0.35), (EAT_T, "gulp", 0.2), (EAT_T + 0.5, "chew", 0.15), (EAT_T + 1.3, "gulp", 0.2),
                     (EAT_T + 1.8, "chew", 0.15), (EAT_T + 2.6, "laugh", 0.35)])


# ---------------------------------------------------------------- scene A: lock & key, then the clone army
def scene_clone(c, t):
    pull = in_out(prog(t, COPY_T - 0.5, ARMY_T + 1.0))
    zoom = lerp(2.6, 0.55, pull)
    lymph_world(c, t, Cam(0, 0, lerp(1.25, 1.0, pull)))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(zoom, zoom)
    # generations: 1 -> 2 -> 4 -> 8 -> 16 -> 32
    gens = 5
    tg = [COPY_T + i * 0.85 for i in range(gens)]
    cells = [(0.0, 0.0)]
    r = 120
    for gi in range(gens):
        k = prog(t, tg[gi], tg[gi] + 0.6)
        if k <= 0:
            break
        nxt = []
        for j, (x, y) in enumerate(cells):
            ang = (gi * 1.3 + j * 0.9)
            d = r * 1.15 * out_back(k, 1.3)
            nxt += [(x - math.cos(ang) * d, y - math.sin(ang) * d), (x + math.cos(ang) * d, y + math.sin(ang) * d)]
        cells = nxt if k >= 1 else nxt
    p = HELPER_TRACK.at(t)
    for j, (x, y) in enumerate(cells):
        jitter = 6 * math.sin(t * 2 + j)
        t_cell(c, x + jitter, y, r * 0.95, t + j * 0.31, "helper", p, (0.0, 0.1), key=GERM, seed=j, rim=(90, 120, 200))
    if t < COPY_T:   # the fragment flies into one receptor lock: click
        u = out_back(prog(t, LOCK_T, CLICK_T), 1.5)
        fx, fy = lerp(560, r * 1.12, u), lerp(-300, 0, u)
        c.drawPath(blob_path(fx, fy, [r * 0.16 * (1 + 0.2 * math.sin(k_ * 2.1)) for k_ in range(7)]), fill(GERM))
        light(c, fx, fy, r * 0.5, GERM, 160)
        if t > CLICK_T:
            g = prog(t, CLICK_T, CLICK_T + 0.6)
            c.drawCircle(r * 1.12, 0, r * (0.3 + 1.2 * g), stroke((220, 255, 150), 8, 255 * (1 - g)))
    c.restore()
    near_blur(c, [(60, 60, 200), (1880, 1020, 220)], t, (90, 120, 200), 0.8)
    chip(c, "ONE LOCK · ONE KEY", 960, 110, (190, 220, 255), t, LOCK_T, COPY_T)
    n = len(cells)
    if t > COPY_T + 0.3:
        txt = f"× {n}" if t < ARMY_T else "× THOUSANDS"
        text(c, txt, 960, 1010, 46, (210, 255, 140), 255 * smooth(prog(t, COPY_T + 0.3, COPY_T + 0.7)), 800, spacing=6)


# ---------------------------------------------------------------- scene B: commander -> killers -> infected cell
def scene_kill(c, t):
    k = in_out(prog(t, CMD_T, B_T))
    cam = Cam(lerp(-240, 160, k), lerp(0, 20, k), lerp(1.1, 1.0, k))
    body_world(c, t, cam)
    cam.push(c, 1.0)
    # commander helper T cell shouting orders
    cx, cy = -620, -200
    t_cell(c, cx, cy + 6 * math.sin(t * 1.6), 100, t, "helper", CMD_TRACK.at(t), (0.8, 0.3), seed=1)
    if KILL_T - 0.3 < t < KILL_T + 1.4:      # sound waves from the shout
        for j in range(3):
            u = ((t - KILL_T) * 1.6 + j / 3) % 1.0
            c.drawArc(skia.Rect.MakeXYWH(cx + 60 - 120 * u, cy - 120 * u - 60, 240 * u + 120, 240 * u + 120), -40, 80, False, stroke(ALARM, 6, 220 * (1 - u)))
    # infected cell (taken over by viruses)
    ix, iy = 420, 60
    dk = prog(t, DESTRUCT_T, DESTRUCT_T + 1.4)
    if dk < 1:
        if dk <= 0:
            pth = blob_path(ix, iy, [210 * (1 + 0.06 * math.sin(k_ * 2.3) + 0.02 * math.sin(t * 2 + k_)) for k_ in range(12)], 0.4)
            c.drawPath(pth, blur(fill((40, 0, 20), 90), 20))
            c.drawPath(pth, shaded(radial((ix - 60, iy - 70), 340, [(240, 170, 160), (210, 130, 130), (150, 80, 100)])))
            c.save()
            c.clipPath(pth, doAntiAlias=True)
            for j in range(7):
                an = j / 7 * 6.28 + t * 0.4
                virus(c, ix + math.cos(an) * 120, iy + 40 + math.sin(an) * 90, 26, t + j)
            c.restore()
            c.drawPath(pth, stroke((140, 70, 90), 6))
            face(c, ix, iy - 70, 170, t, INFECTED.at(t), (-0.6, 0.0), True, 0.4)
        else:     # self-destruct: shrinks and breaks into tidy fragments
            rng = np.random.default_rng(4)
            for j in range(22):
                an = rng.uniform(0, 6.28)
                d = 200 * (0.2 + 0.9 * out_cubic(dk)) * rng.uniform(0.4, 1)
                c.drawCircle(ix + math.cos(an) * d, iy + math.sin(an) * d, 20 * (1 - dk * 0.6), fill((230, 160, 150), 255 * (1 - dk)))
            for j in range(7):   # trapped viruses fall apart too
                an = j / 7 * 6.28
                virus(c, ix + math.cos(an) * 160 * out_cubic(dk), iy + math.sin(an) * 120 * out_cubic(dk), 26 * (1 - dk), t, a=255 * (1 - dk))
            if dk < 0.3:
                light(c, ix, iy, 320, HOTWHITE, 220 * (1 - dk / 0.3))
    # killers arrive: Kai leads, clones behind
    arrive = out_cubic(prog(t, KILL_T, HUNT_T + 0.8))
    for i in range(4):
        ang = math.radians(120 + i * 35)
        hx, hy = ix + math.cos(ang) * 320, iy + math.sin(ang) * 250
        x = lerp(-1300 - 150 * i, hx, arrive)
        y = lerp(300 + 60 * i, hy, arrive) + 8 * math.sin(t * 2 + i)
        kai(c, x, y, 70, t + i * 0.4, CLONES[i].at(t), (0.9, -0.2), blink_amount(t, (), 3.8, i))
    kx = lerp(-1100, ix - 330, out_cubic(prog(t, KAI_T - 1.0, HUNT_T + 0.6)))
    lunge = 70 * math.sin(math.pi * prog(t, DESTRUCT_T - 0.5, DESTRUCT_T + 0.3))
    kai(c, kx + lunge, iy + 10, 130, t, KAI_TRACK.at(t), (0.9, 0.0), blink_amount(t, KAI_TRACK.change_times(), 3.9, 0.2),
        hop=0.5 * math.sin(math.pi * prog(t, DESTRUCT_T - 0.5, DESTRUCT_T + 0.3)))
    if DESTRUCT_T - 0.2 < t < DESTRUCT_T + 0.4:     # the 'kill signal' passed on contact
        u = prog(t, DESTRUCT_T - 0.2, DESTRUCT_T + 0.4)
        c.drawLine(kx + lunge + 120, iy, lerp(kx + lunge + 120, ix - 150, u), iy, stroke(KILLER, 10, 255))
    cam.pop(c)
    near_blur(c, [(-80, 1040, 230), (1990, 60, 200)], t, (190, 70, 100), 0.8)
    chip(c, "HELPER T CELL · THE COMMANDER", 960, 110, HELPER, t, CMD_T + 0.3, KILL_T + 0.4)
    chip(c, "KILLER T CELLS", 960, 110, (255, 170, 150), t, KILL_T + 0.6, HUNT_T + 0.6)
    chip(c, "INFECTED BY VIRUSES", 960, 110, (255, 190, 190), t, HUNT_T + 0.8, DESTRUCT_T)
    chip(c, "SELF-DESTRUCT", 960, 110, (255, 150, 130), t, DESTRUCT_T + 0.1, B_T + 0.5)


# ---------------------------------------------------------------- scene C+D: plasma cell factory, tagging, the big eater
def scene_factory(c, t):
    k = in_out(prog(t, B_T, DURATION))
    cam = Cam(lerp(-160, 120, k), 0, lerp(1.05, 0.95, k))
    body_world(c, t, cam)
    cam.push(c, 1.0)
    bx, by = -560, -40
    plasma = smooth(prog(t, PLASMA_T, PLASMA_T + 1.0))
    wake = smooth(prog(t, WAKE_T - 0.2, WAKE_T + 0.3))
    b_cell(c, bx, by + 6 * math.sin(t * 1.4), 120, t, B_TRACK.at(t), (0.8, 0.0), plasma=plasma)
    if WAKE_T - 0.5 < t < WAKE_T + 0.4:     # a helper bumps it awake
        u = prog(t, WAKE_T - 0.5, WAKE_T + 0.4)
        t_cell(c, bx - 260 + 120 * math.sin(math.pi * u), by - 160, 60, t, "helper", pose("cheer"), (0.8, 0.5))
    elif t < WAKE_T - 0.5:
        t_cell(c, bx - 300, by - 180, 60, t, "helper", pose("happy"), (0.8, 0.5))
    # antibody stream
    fire = smooth(prog(t, FIRE_T, FIRE_T + 0.5))
    rng = np.random.default_rng(3)
    tgt = [(380 + 170 * (i % 2), -280 + 180 * i) for i in range(4)]
    for j in range(60):
        start = FIRE_T + j * 0.09
        u = prog(t, start, start + 2.2)
        if u <= 0 or u >= 1 or fire <= 0:
            continue
        aim = tgt[j % 4]
        sx, sy = bx + 160, by
        ex, ey = aim[0] + rng.uniform(-80, 80), aim[1] + rng.uniform(-60, 60)
        x = lerp(sx, ex, out_cubic(u))
        y = lerp(sy, ey, out_cubic(u)) - 90 * math.sin(math.pi * u)
        antibody(c, x, y, 46, 90 + 600 * u + j * 30, 255 * (1 - smooth(prog(u, 0.85, 1.0))))
    # bacteria get tagged and slow down; the eater scoops two
    ex_, ey_ = 860, 80
    for i, (tx, ty) in enumerate(tgt):
        tag = smooth(prog(t, TAG_T + 0.3 * i, TAG_T + 1.4 + 0.3 * i))
        slow = 1 - 0.85 * tag
        x = tx + 40 * math.sin(t * 2.4 * slow + i) * slow
        y = ty + 30 * math.cos(t * 2.0 * slow + i) * slow
        bite = EAT_T + (1.3 if i == 3 else 0.0) if i in (1, 3) else None
        if bite is not None:
            pullk = in_cubic(prog(t, bite - 0.6, bite))
            if t > bite:
                continue
            x, y = lerp(x, ex_ - 40, pullk), lerp(y, ey_ + 30, pullk)
        bacterium(c, x, y, 54, t, 160 + 20 * i, mood=BAC_TAG[i].at(t), wiggle=0.4 + 3 * (1 - tag), tag=tag)
    if t > TAG_T + 0.6:
        u = out_cubic(prog(t, TAG_T + 0.6, TAG_T + 2.0))
        belly = []
        for j, b in enumerate((EAT_T, EAT_T + 1.3)):
            if t > b:
                belly.append(((-0.48 if j == 0 else 0.48), 0.0, 0.13, 0.5 * smooth(prog(t, b + 0.5, b + 6))))
        hands = [None, None]
        for j, (b, ti) in enumerate(((EAT_T, 1), (EAT_T + 1.3, 3))):
            if b - 0.9 < t < b - 0.05:
                tx, ty = tgt[ti]
                hands[j] = (lerp(lerp(1600, ex_, u) - 220, tx, smooth(prog(t, b - 0.9, b - 0.6))), ty)
        chomp = max([math.exp(-(t - b) * 8) for b in (EAT_T, EAT_T + 1.3) if t > b] + [0.0])
        eater(c, lerp(1600, ex_, u), ey_, 170, t, EATER_TRACK.at(t), (-0.8, 0.0), blink_amount(t, EATER_TRACK.change_times(), 4.1, 1.0),
              hands, belly, chomp=chomp)
    cam.pop(c)
    near_blur(c, [(-80, 1040, 230), (1990, 60, 200)], t, (190, 70, 100), 0.8)
    chip(c, "B CELL", 960, 110, BCELL, t, B_T + 0.3, PLASMA_T)
    chip(c, "PLASMA CELL · THOUSANDS OF ANTIBODIES PER SECOND", 960, 110, BCELL, t, PLASMA_T + 0.3, TAG_T + 0.2)
    chip(c, "TAGGED FOR DESTRUCTION", 960, 110, ANTIBODY, t, TAG_T + 0.6, DURATION)


def draw_frame(c, t):
    if t < CMD_T + 0.5:
        xfade(c, t, CMD_T - 0.5, 1.0, scene_clone, scene_kill, 0.3)
    else:
        xfade(c, t, B_T - 0.3, 0.9, scene_kill, scene_factory, 0.25)
    chapter_title(c, t, 4, "SPECIAL FORCES", HELPER, 0.2, 2.8)
    fade(c, t, DURATION, 0.5, 0.7)


def sfx_events():
    ev = [(0.2, "swell_soft", 0.6), (LOCK_T, "slide", 0.5), (CLICK_T, "click", 1.0), (CLICK_T + 0.05, "shine", 0.8)]
    ev += [(COPY_T + i * 0.85, "pop", 0.6 + 0.08 * i) for i in range(5)] + [(COPY_T + i * 0.85 + 0.05, "bubble", 0.5) for i in range(5)]
    ev += [(ARMY_T, "boom", 0.6), (CMD_T - 0.5, "whoosh_long", 0.6), (KILL_T - 0.3, "blip", 0.9), (KILL_T, "whoosh", 0.8), (KAI_T + 0.9, "ding", 0.6),
           (HUNT_T, "riser", 0.6), (DESTRUCT_T - 0.2, "click", 0.9), (DESTRUCT_T, "boom", 0.8), (DESTRUCT_T + 0.05, "shimmer", 0.7)]
    ev += [(B_T - 0.3, "whoosh_long", 0.6), (WAKE_T - 0.1, "pop", 0.7), (PLASMA_T, "swell_soft", 0.6)] + [(FIRE_T + 0.18 * i, "tink", 0.35) for i in range(16)]
    ev += [(TAG_T + 0.3 * i + 0.4, "click", 0.5) for i in range(4)] + [(EAT_T, "pop", 1.0), (EAT_T + 0.02, "bubble", 0.8), (EAT_T + 1.3, "pop", 1.0),
                                                                      (EAT_T + 1.32, "bubble", 0.8), (EAT_T + 2.6, "chime", 0.6)]
    return ev


MUSIC = dict(
    chords=[(0.0, 52, (0, 7, 12, 16, 19)), (CLICK_T, 50, (0, 7, 12, 16, 19, 24)), (CMD_T, 45, (0, 7, 12, 15, 19)), (HUNT_T, 43, (0, 7, 12, 15, 18)),
            (DESTRUCT_T, 45, (0, 7, 12, 16, 19)), (B_T, 48, (0, 7, 12, 16, 19)), (TAG_T, 50, (0, 7, 12, 16, 21))],
    plucks=[(VO["S1"], DURATION)], bpm=108, rises=[(COPY_T, ARMY_T), (HUNT_T, DESTRUCT_T)],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
