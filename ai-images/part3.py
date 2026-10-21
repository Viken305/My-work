"""Part 3, how it learned: a tilted wall of captioned pictures scrolls past with a rolling counter; the wall slows and
the dog card is pulled to the centre; it gets buried in noise step by step (0 -> 1,000) while snapshots drop into a
filmstrip; then the model's one job: noisy picture -> MODEL -> its guess of the noise, written as an equation
(noisy - noise = picture).

  python3 render.py part3 [--still 1.5,3.5,6,9,11,13.5,16.4]
"""
from film import *  # noqa: F401,F403

PART = "part3"
VO, _end = schedule(PART)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)
DURATION = _end + 0.6

BILL_T = TM.word("B1", "billions")
TRICK_T = TM.word("B2", "trick.")
PULL_T = TM.word("B2", "During")
BURY0, BURY1 = TM.word("B2", "buried"), TM.word("B2", "left.", end=True)
JOB_T = VO["B3"]
LOOK_T, GUESS_T = TM.word("B3", "Look"), TM.word("B3", "guess")
NOISE_T = TM.word("B3", "noise.")

CAPS = Captions(TM, ENV, words=WORDS, model=MODEL)
WALL = [("train_dog", "a golden retriever on grass"), ("train_mountain", "a snowy mountain at sunrise"),
        ("seed_a", "a black cat in a spacesuit"), ("train_lighthouse", "a lighthouse by the sea"),
        ("paris", "a cat on a bike in Paris"), ("seed_b", "a grey cat on the moon"), ("hero", "a cat on a bicycle"),
        ("seed_c", "a cream cat, digital art")]
SNAPS = (0.0, 0.25, 0.5, 0.75, 1.0)
CW = 300                              # wall card width


def wall_offset(t):
    """Scroll distance: fast, then easing to a stop as the dog is pulled out."""
    v = 900.0
    t1 = PULL_T + 0.3
    if t < t1 - 1.2:
        return v * t
    # decelerate over 1.2 s to rest
    u = clamp((t - (t1 - 1.2)) / 1.2)
    return v * (t1 - 1.2) + v * 1.2 * (u - u * u / 2)


def wall_slot(i, j, off):
    """Card (column i, row j) position on the tilted wall."""
    col_speed = (1.0, 0.75, 1.15)[i]
    x = 200 + i * 340
    y = 2100 + j * 420 - (off * col_speed) % (420 * 8) - 420 * 2
    return x, y


def draw_wall(c, t):
    a = 255 * smooth(prog(t, 0.0, 0.4)) * (1 - smooth(prog(t, PULL_T, PULL_T + 0.7)))
    if a <= 1:
        return
    off = wall_offset(t)
    c.save()
    camera(c, 1.08, 0, 0)
    c.rotate(-7, W / 2, H / 2)
    for i in range(3):
        for j in range(9):
            name, cap = WALL[(i * 3 + j) % len(WALL)]
            if i == 1 and j % 8 == 3:
                name, cap = WALL[0]
            x, y = wall_slot(i, j, off)
            if -300 < y < H + 300:
                card_at(c, pic(name), x, y, CW, a * (0.75 if i != 1 else 1), 0, 1, cap.upper()[:26])
    c.restore()
    # counter
    n = int(1e9 * 2.3 * prog(t, 0.3, BILL_T + 0.1) ** 3)
    ca = a * (1 - smooth(prog(t, PULL_T - 0.4, PULL_T)))
    c.drawRect(skia.Rect.MakeXYWH(0, 210, W, 210), paint(INK, ca * 0.8, sigma=30))
    label(c, "PICTURES STUDIED", W / 2, 285, 24, "mono", SMOKE, ca, "center", 0.35)
    txt = f"{n:,}" if t < BILL_T + 0.1 else "BILLIONS"
    label(c, txt, W / 2, 380, 92, "mono_bold", VIOLET if t > BILL_T + 0.1 else PAPER, ca, "center", 0.02)


def dog_noise(t):
    return in_out(prog(t, BURY0, BURY1)) if t < JOB_T else 1.0


def draw_bury(c, t):
    q = in_out(prog(t, PULL_T - 0.2, PULL_T + 0.8))
    if q <= 0:
        return
    out = in_out(prog(t, JOB_T - 0.2, JOB_T + 0.7))
    k = dog_noise(t)
    # the dog card flies from its wall slot to the centre
    x0, y0 = W / 2, 1300
    cx, cy, w = lerp(x0, W / 2, q), lerp(y0, 820, q), lerp(CW, 700, q)
    s = 1 - 0.55 * out
    cx, cy = lerp(cx, 230, out), lerp(cy, 840, out)
    show_k = k if out < 0.5 else 0.55
    card_at(c, pic("train_dog", show_k, 5), cx, cy, w, 255, (1 - q) * -7, s,
            None if out > 0.1 else f"NOISE STEP {int(1000 * k):4d} / 1000", None, prog(t, PULL_T + 0.5, PULL_T + 1.4))
    ta = 255 * smooth(prog(t, PULL_T + 0.3, PULL_T + 0.8)) * (1 - out)
    label(c, "TRAINING", W / 2, 245, 28, "mono_bold", VIOLET, ta, "center", 0.4)
    # noise meter
    if ta > 1:
        x, y, mw = 170, 1290, 740
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, mw, 10), 5, 5), paint(SMOKE, ta * 0.3))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, mw * k, 10), 5, 5), paint(VIOLET, ta))
    # filmstrip snapshots drop out of the card as the noise passes each level
    for i, lvl in enumerate(SNAPS):
        tt = BURY0 + (BURY1 - BURY0) * (0.08 + 0.84 * i / 4)
        u = back_out(prog(t, tt, tt + 0.5), 1.2)
        fa = 255 * smooth(prog(t, tt, tt + 0.2)) * (1 - out)
        if fa > 1:
            fx = 150 + i * 195
            fy = lerp(820, 370, u)
            card_at(c, pic("train_dog", lvl, 5), fx, fy, 170, fa, 0, 1, f"{int(lvl * 1000)}")


def draw_job(c, t):
    a = smooth(prog(t, JOB_T + 0.2, JOB_T + 0.8))
    if a <= 0:
        return
    node_box(c, W / 2, 840, 260, 240, t, "MODEL", 255 * a, 0.3 + 0.7 * smooth(prog(t, LOOK_T, LOOK_T + 0.6)))
    thread(c, 230 + 165, 840, W / 2 - 130, 840, prog(t, LOOK_T, LOOK_T + 0.5), VIOLET, 255 * a, 0.0)
    gq = prog(t, GUESS_T, GUESS_T + 0.6)
    thread(c, W / 2 + 130, 840, 850 - 165, 840, gq, VIOLET, 255 * a, 0.0)
    ga = 255 * a * smooth(prog(t, GUESS_T + 0.3, GUESS_T + 0.7))
    card_at(c, pure_static(5), 850, 840, 330, ga, 0, 0.45 + 0.55 * back_out(prog(t, GUESS_T + 0.3, GUESS_T + 0.8)), None,
            VIOLET, None)
    label(c, "NOISY PICTURE", 230, 1040, 22, "mono", SMOKE, 255 * a, "center", 0.15)
    label(c, "ITS GUESS: THE NOISE", 850, 1040, 22, "mono_bold", VIOLET, ga, "center", 0.15)
    fig(c, 6, "THE ONE JOB IT IS TRAINED ON", 90, 560, 255 * a)
    # the equation: noisy - noise = picture
    eq = smooth(prog(t, NOISE_T - 0.1, NOISE_T + 0.5))
    if eq > 0:
        y, w = 1160, 170
        items = [(pic("train_dog", 0.55, 5), 190), ("−", 335), (pure_static(5), 480), ("=", 625), (pic("train_dog"), 770)]
        for i, (it, x) in enumerate(items):
            e = back_out(prog(t, NOISE_T - 0.1 + i * 0.08, NOISE_T + 0.4 + i * 0.08), 1.4)
            if isinstance(it, str):
                label(c, it, x, y + 22, 70, "bold", PAPER, 255 * eq, "center")
            else:
                card_at(c, it, x, y, w, 255 * eq, 0, max(0.01, e), None, AMBER if i == 4 else None)


def draw_frame(c, t):
    background(c)
    ambient(c, t, 0.6)
    draw_wall(c, t)
    draw_bury(c, t)
    draw_job(c, t)
    CAPS.draw(c, t)
    edges(c, t, DURATION, 0.25, 0.25)


def post_kw(t):
    return dict(glitch=0.25 * max(0.0, 1 - abs(t - BURY1) / 0.3))


def sfx_events():
    ev = [(0.0, "whoosh", 0.5), (0.2, "tick_roll", 0.35), (1.4, "tick_roll", 0.35), (BILL_T + 0.1, "low_hit", 0.5),
          (PULL_T - 0.1, "swish", 0.55), (BURY0 - 0.2, "static_clear", 0.0)]
    ev = [e for e in ev if e[2] > 0]
    ev.append((BURY0, "static_hold", 0.18))
    ev.append((BURY0 + 2.4, "static_hold", 0.3))
    for i in range(5):
        ev.append((BURY0 + (BURY1 - BURY0) * (0.08 + 0.84 * i / 4), "pop", 0.4))
    ev += [(JOB_T + 0.2, "whoosh", 0.4), (LOOK_T, "pluck", 0.5), (GUESS_T + 0.3, "glass_ting", 0.4),
           (NOISE_T, "snap", 0.5), (NOISE_T + 0.32, "shimmer", 0.35)]
    return ev


MUSIC = dict(beds=[(0.0, PULL_T + 0.5, "arp", 1.0), (0.0, DURATION, "synth", 0.6)])
