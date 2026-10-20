"""Part 5, same words, new noise: the finished cat dissolves back to static and splits into four static cards with
different seeds, which resolve into four different cats; three fly off and a second SEED 1883 card resolves into the
identical cat (=, lock); then prompt words stream as amber sparks into the card while it is sculpted out of noise one
last time, and the frame dissolves into full-screen static, which is where the video starts (loop).

  python3 render.py part5 [--still 1,3.4,5.6,7.8,10,12.4,13.4]
"""
from film import *  # noqa: F401,F403

PART = "part5"
VO, _end = schedule(PART, first=0.4, gap=0.5)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)

STATIC_T = TM.word("D1", "starting")
DIFF_T = TM.word("D1", "different")
SAME0 = VO["D2"]
EXACT_T = TM.word("D2", "exact")
SAME_T = TM.word("D2", "static,")
CAT2_T = TM.word("D2", "cat.")
D3_T = VO["D3"]
NOISE_T = TM.word("D3", "random")
SCULPT_T = TM.word("D3", "sculpted")
END_T = TM.end("D3")
OUT_T = END_T + 0.45
DURATION = OUT_T + 0.9

CAPS = Captions(TM, ENV, words=WORDS, model=MODEL)
GRID = [("hero", 300, 565), ("seed_a", 780, 565), ("seed_b", 300, 1050), ("seed_c", 780, 1050)]
CY = 900


def draw_seeds(c, t):
    a = 1 - smooth(prog(t, SAME0 - 0.1, SAME0 + 0.5))
    if a <= 0:
        return
    split = in_out(prog(t, STATIC_T + 0.3, STATIC_T + 1.0))
    for i, (name, gx, gy) in enumerate(GRID):
        x, y = lerp(W / 2, gx, split), lerp(CY, gy, split)
        w = lerp(740, 420, split)
        if i and split <= 0:
            continue
        # back to static, then each resolves with its own seed
        k_out = in_out(prog(t, 0.3, STATIC_T + 0.3))
        r = prog(t, DIFF_T - 0.4 + i * 0.18, DIFF_T + 0.9 + i * 0.18)
        if r <= 0:
            arr = pic("hero", k_out, SEED) if i == 0 else pure_static(SEEDS[name])
        else:
            arr = guess(r, name, SEEDS[name])
        pop = back_out(prog(t, STATIC_T + 0.3 + i * 0.05, STATIC_T + 0.9 + i * 0.05), 1.5) if i else 1
        card_at(c, arr, x, y, w, 255 * a, 0, max(0.01, pop), f"SEED {SEEDS[name]}" if split > 0.8 else None,
                AMBER if r >= 1 else None, prog(t, DIFF_T + 0.9 + i * 0.18, DIFF_T + 1.8 + i * 0.18))
    fig(c, 10, "SAME PROMPT, FOUR STARTING STATICS", 90, 330, 255 * a * split)


def draw_same(c, t):
    a = smooth(prog(t, SAME0 - 0.1, SAME0 + 0.4)) * (1 - smooth(prog(t, D3_T - 0.2, D3_T + 0.4)))
    if a <= 0:
        return
    # hero card slides from its grid slot to the left; a twin lands on the right
    m = in_out(prog(t, SAME0 - 0.1, SAME0 + 0.6))
    lx, ly = lerp(300, 285, m), lerp(565, CY, m)
    lw = lerp(420, 450, m)
    rq = back_out(prog(t, EXACT_T - 0.2, EXACT_T + 0.4), 1.4)
    k = prog(t, SAME_T + 0.1, CAT2_T + 0.1)
    left = guess(k, "hero", SEED) if k > 0 else pure_static(SEED)
    lock = t > CAT2_T + 0.1
    if t < SAME_T:   # left card still shows the finished cat, fading to its starting static
        left = pic("hero", in_out(prog(t, SAME0 + 0.3, SAME_T)), SEED)
    card_at(c, left, lx, ly, lw, 255 * a, 0, 1, f"SEED {SEED}", AMBER if lock else None)
    if rq > 0:
        card_at(c, guess(k, "hero", SEED) if k > 0 else pure_static(SEED), 795, CY, 450, 255 * a, 0, max(0.01, rq),
                f"SEED {SEED}", AMBER if lock else None)
    ea = smooth(prog(t, CAT2_T, CAT2_T + 0.3))
    label(c, "=", W / 2, CY + 30, 110, "bold", AMBER, 255 * a * ea, "center")
    if lock:
        q = prog(t, CAT2_T + 0.1, CAT2_T + 0.6)
        r = skia.Rect.MakeXYWH(60, CY - 260, W - 120, 520)
        c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), paint(AMBER, 200 * a * (1 - q), stroke=3 + 6 * (1 - q)))
        label(c, "IDENTICAL", W / 2, CY - 300, 30, "mono_bold", AMBER, 255 * a * smooth(q * 2), "center", 0.4)
    fig(c, 11, "SAME PROMPT, SAME STATIC", 90, 330, 255 * a)


def draw_sculpt(c, t):
    a = smooth(prog(t, D3_T - 0.2, D3_T + 0.4))
    if a <= 0:
        return
    # the card goes noisy on "random noise", then is sculpted back by the words
    nk = in_out(prog(t, NOISE_T - 0.2, NOISE_T + 0.5)) * (1 - in_out(prog(t, SCULPT_T, END_T)))
    arr = pic("hero", nk * 0.85, SEED)
    s = 1 + 0.05 * prog(t, D3_T, OUT_T)
    card_at(c, arr, W / 2, CY, 760, 255 * a, 0, s, None, AMBER if t > END_T - 0.3 else None, prog(t, END_T - 0.4, END_T + 0.6))
    # prompt words stream in from the top as amber sparks
    rng = np.random.default_rng(4)
    for i, tk in enumerate(art.TOKENS * 2):
        t0 = SCULPT_T - 0.6 + i * 0.05
        u = prog(t, t0, t0 + 0.9)
        if 0 < u < 1:
            sx, sy = rng.uniform(100, 980), rng.uniform(200, 320)
            tx, ty = W / 2 + rng.uniform(-300, 300), CY + rng.uniform(-300, 300)
            e = in_out(u)
            x, y = lerp(sx, tx, e), lerp(sy, ty, e) - 100 * math.sin(math.pi * e)
            label(c, tk, x, y, 30 * (1 - 0.6 * e), "mono_bold", AMBER, 255 * a * (1 - e ** 3), "center")
            c.drawCircle(x, y - 10, 14 * (1 - e) + 4, paint(AMBER, 120 * (1 - e), sigma=8))
        else:
            rng.uniform(size=4)


def draw_frame(c, t):
    background(c)
    ambient(c, t, 0.6)
    draw_seeds(c, t)
    draw_same(c, t)
    draw_sculpt(c, t)
    CAPS.draw(c, t)
    # the loop: everything dissolves into full-screen static (the first frame of part 1)
    q = prog(t, OUT_T - 0.3, DURATION)
    if q > 0:
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(INK, 255 * smooth(q * 1.5)))
        grain_patch(c, skia.Rect.MakeLTRB(0, 0, W, H), 255 * smooth(q * 1.3), int(t * 30))


def post_kw(t):
    return dict(glitch=0.6 * smooth(prog(t, OUT_T - 0.2, DURATION)))


def sfx_events():
    ev = [(STATIC_T, "static_hold", 0.25), (STATIC_T + 0.3, "swish", 0.5)]
    for i in range(4):
        ev.append((DIFF_T + 0.9 + i * 0.18, "pop", 0.6))
    ev += [(SAME0 - 0.1, "whoosh", 0.4), (EXACT_T - 0.2, "pop", 0.5), (SAME_T, "static_clear", 0.3),
           (CAT2_T + 0.1, "clunk", 0.9), (NOISE_T - 0.2, "static_burst", 0.4), (SCULPT_T - 0.4, "shimmer", 0.5),
           (END_T - 0.2, "glass_ting", 0.45), (OUT_T - 0.3, "static_hold", 0.5)]
    return ev


MUSIC = dict(beds=[(0.0, DURATION, "synth", 0.65), (0.0, D3_T, "arp", 0.8)])
