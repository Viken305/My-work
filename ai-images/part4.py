"""Part 4, making the picture.

  C1  training ran picture -> noise; the arrow flips: generating runs noise -> picture; a fresh static card lands
  C2  30 steps: each one tears a little noise off the card (noise flakes fly out), blobs -> shapes -> fur and craters
  C3  the prompt's tokens sit above the card; threads run from "cat" and "moon" into the picture and light up where
      the model looks for each word
  C4  the card splits in two: a guess without the prompt (mush) and one with it; the model pushes 7.5x further
  C5  the picture really lives on a tiny 64x64 grid; a decoder paints the full image

  python3 render.py part4 [--still 1,3.8,6.5,9.5,11.5,15.8,17.6,20.5,23,27,29.5,31.5,32.5]
"""
from film import *  # noqa: F401,F403

PART = "part4"
VO, _end = schedule(PART, first=0.4, gap=0.5)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)
DURATION = _end + 0.6

REV_T = TM.word("C1", "reverse.")
FRESH_T = TM.word("C1", "fresh")
STEP_T = TM.word("C2", "step,")
REMOVE_T = TM.word("C2", "removes")
BLOB_T, SHAPE_T, FUR_T = TM.word("C2", "blobs"), TM.word("C2", "shapes."), TM.word("C2", "fur")
DONE_T = TM.word("C2", "craters.", end=True)
STEER_T = TM.word("C3", "steer")
CAT_T, MOON_T = TM.word("C3", "cat."), TM.word("C3", "moon.")
TWO_T = TM.word("C4", "two")
WITH_T, WITHOUT_T = TM.word("C4", "with"), TM.word("C4", "without,")
PUSH_T = TM.word("C4", "pushes")
C5_T = VO["C5"]
TINY_T, SMALL_T = TM.word("C5", "tiny"), TM.word("C5", "smaller.")
DEC_T, FULL_T = TM.word("C5", "decoder"), TM.word("C5", "full")

CAPS = Captions(TM, ENV, words=WORDS, model=MODEL)
CX, CY, CWID = W / 2, 900, 740
# step schedule keyed to the narration: (time, step)
STEPS = [(FRESH_T + 0.3, 0), (STEP_T, 1), (BLOB_T, 7), (SHAPE_T, 15), (FUR_T, 23), (DONE_T, 30)]
CHIPS = ["a", "cat", "wearing", "an", "astronaut", "suit", "riding", "a", "bicycle", "on", "the", "moon", "digital", "art"]
TINY = None


def step_at(t):
    ts, ks = zip(*STEPS)
    return float(np.interp(t, ts, ks))


def to_card(x, y, cx=CX, cy=CY, w=CWID):
    """Point in the 512 drawing -> screen."""
    return cx - w / 2 + w * x / 512, cy - w / 2 + w * y / 512


def chip_layout():
    out, x, y = [], 90, 250
    for tk in CHIPS:
        wd = width(tk, "mono_bold", 30) + 40
        if x + wd > 990:
            x, y = 90, y + 76
        out.append((x, y, wd))
        x += wd + 12
    return out


CHIP_POS = chip_layout()


def tiny():
    global TINY
    if TINY is None:
        sm = cv2.resize(pic("hero"), (64, 64), interpolation=cv2.INTER_AREA)
        TINY = cv2.resize(sm, (RES, RES), interpolation=cv2.INTER_NEAREST)
    return TINY


def draw_reverse(c, t):
    """C1: TRAINING picture -> noise, the arrow flips to GENERATING noise -> picture."""
    a = smooth(prog(t, 0.0, 0.4)) * (1 - smooth(prog(t, FRESH_T - 0.2, FRESH_T + 0.2)))
    if a <= 0:
        return
    flip = in_out(prog(t, REV_T - 0.2, REV_T + 0.6))
    y = 820
    l_img = pic("train_dog") if flip < 0.5 else pure_static(1883)
    r_img = pure_static(5) if flip < 0.5 else None
    sx = abs(math.cos(flip * math.pi))
    card_at(c, l_img, 260, y, 300, 255 * a, 0, max(0.02, sx))
    if r_img is not None:
        card_at(c, r_img, 820, y, 300, 255 * a, 0, max(0.02, sx))
    else:
        r = skia.Rect.MakeXYWH(820 - 150, y - 150, 300, 300)
        c.drawRRect(skia.RRect.MakeRectXY(r, 18, 18), paint(AMBER, 200 * a * sx, stroke=2))
        label(c, "?", 820, y + 50, 150, "serif_bold", AMBER, 255 * a * sx, "center")
    # arrow
    ax0, ax1 = 430, 650
    c.drawLine(ax0, y, ax1, y, paint(VIOLET if flip < 0.5 else AMBER, 255 * a, stroke=6))
    c.drawPath(_arrow_head(ax1, y), paint(VIOLET if flip < 0.5 else AMBER, 255 * a))
    txt = "TRAINING: PICTURE → NOISE" if flip < 0.5 else "GENERATING: NOISE → PICTURE"
    label(c, txt, W / 2, 560, 30, "mono_bold", VIOLET if flip < 0.5 else AMBER, 255 * a * sx, "center", 0.12)


def _arrow_head(x, y, s=22):
    p = skia.Path()
    p.moveTo(x + s, y)
    p.lineTo(x - s * 0.4, y - s * 0.8)
    p.lineTo(x - s * 0.4, y + s * 0.8)
    p.close()
    return p


def main_card(c, t):
    """C1 end .. C3: the generating card, the step counter, noise flakes and attention."""
    a = smooth(prog(t, FRESH_T - 0.1, FRESH_T + 0.3)) * (1 - smooth(prog(t, TWO_T - 0.1, TWO_T + 0.2)))
    if a <= 0:
        return
    k = step_at(t)
    arr = guess(k / 30) if k > 0 else pure_static(SEED)
    # attention overlays
    ca = smooth(prog(t, CAT_T - 0.1, CAT_T + 0.4)) * (1 - smooth(prog(t, MOON_T - 0.3, MOON_T)))
    ma = smooth(prog(t, MOON_T - 0.1, MOON_T + 0.4)) * (1 - smooth(prog(t, TWO_T - 0.4, TWO_T)))
    if ca > 0:
        arr = heat(arr, art.attn("cat"), AMBER, ca)
    if ma > 0:
        arr = heat(arr, art.attn("moon"), AMBER, ma)
    land = back_out(prog(t, FRESH_T - 0.1, FRESH_T + 0.5), 1.3)
    # a small kick on every step
    kick = 0.0
    if 0 < k < 30:
        kick = 0.012 * math.exp(-((k % 1) * 6))
    sheen = prog(t, DONE_T - 0.2, DONE_T + 1.0)
    card_at(c, arr, CX, CY + 4 * math.sin(t * 1.2), CWID, 255 * a, 0, max(0.01, land) * (1 + kick),
            f"SEED {SEED}", AMBER if t > DONE_T else None, sheen)
    sa = 255 * a * smooth(prog(t, STEP_T - 0.5, STEP_T)) * (1 - smooth(prog(t, VO["C3"] - 0.4, VO["C3"])))
    step_ui(c, k, CX - 370, CY - CWID / 2 - 60, sa)
    # noise flakes torn off the card each step
    if REMOVE_T - 0.4 < t < DONE_T + 0.6:
        rng = np.random.default_rng(int(k))
        ph = k % 1
        for j in range(5):
            ox, oy = rng.uniform(-0.4, 0.4) * CWID, rng.uniform(-0.4, 0.4) * CWID
            ang = rng.uniform(0, 2 * math.pi)
            d = 160 * out_cubic(ph)
            fx, fy = CX + ox + math.cos(ang) * d, CY + oy + math.sin(ang) * d - 60 * ph
            sz = rng.uniform(40, 90) * (1 - 0.4 * ph)
            grain_patch(c, skia.Rect.MakeXYWH(fx - sz / 2, fy - sz / 2, sz, sz), 220 * a * (1 - ph) * (1 - k / 34),
                        int(k) * 5 + j)
    # phase tags
    for t0, t1, txt in ((BLOB_T, SHAPE_T, "BLOBS OF COLOUR"), (SHAPE_T, FUR_T, "SHAPES"), (FUR_T, DONE_T + 0.8, "FINE DETAIL")):
        ta = 255 * a * smooth(prog(t, t0, t0 + 0.25)) * (1 - smooth(prog(t, t1 - 0.1, t1 + 0.15)))
        if ta > 1:
            w = width(txt, "mono_bold", 26, 0.2) + 40
            r = skia.Rect.MakeXYWH(CX - w / 2, CY - CWID / 2 + 24, w, 50)
            c.drawRRect(skia.RRect.MakeRectXY(r, 25, 25), paint(INK, ta * 0.7))
            c.drawRRect(skia.RRect.MakeRectXY(r, 25, 25), paint(VIOLET, ta * 0.2))
            c.drawRRect(skia.RRect.MakeRectXY(r, 25, 25), paint(VIOLET, ta, stroke=2))
            label(c, txt, CX, CY - CWID / 2 + 58, 26, "mono_bold", PAPER, ta, "center", 0.2)


def draw_steer(c, t):
    """C3: token chips above the card; threads into the picture for cat and moon."""
    a = smooth(prog(t, VO["C3"] - 0.2, VO["C3"] + 0.4)) * (1 - smooth(prog(t, TWO_T - 0.3, TWO_T)))
    if a <= 0:
        return
    pulse = smooth(prog(t, STEER_T, STEER_T + 0.3)) * (1 - smooth(prog(t, STEER_T + 1.0, STEER_T + 1.6)))
    for i, (tk, (x, y, wd)) in enumerate(zip(CHIPS, CHIP_POS)):
        hot = (tk == "cat" and t > CAT_T - 0.2 and t < MOON_T - 0.2) or (tk == "moon" and t > MOON_T - 0.2)
        e = back_out(prog(t, VO["C3"] - 0.2 + i * 0.03, VO["C3"] + 0.3 + i * 0.03), 1.4)
        ca = 255 * a * (1 if hot or pulse > 0.2 else 0.55)
        c.save()
        camera(c, max(0.01, e) * (1.15 if hot else 1), 0, 0, x + wd / 2, y + 25)
        chip(c, tk, x, y, ca, AMBER, 30, 0.35 if hot else 0.12)
        c.restore()
        if pulse > 0:   # every word sends a faint thread into the picture
            tx, ty = to_card(80 + (i * 37) % 360, 150 + (i * 53) % 300)
            thread(c, x + wd / 2, y + 52, tx, ty, pulse, AMBER, 90 * a * pulse)
    for tk, t0, tgt in (("cat", CAT_T, (276, 255)), ("moon", MOON_T, (330, 470))):
        x, y, wd = CHIP_POS[CHIPS.index(tk)]
        u = prog(t, t0 - 0.35, t0 + 0.15)
        fade = 1 - smooth(prog(t, MOON_T - 0.3, MOON_T)) if tk == "cat" else 1.0
        tx, ty = to_card(*tgt)
        thread(c, x + wd / 2, y + 52, tx, ty, out_cubic(u), AMBER, 255 * a * fade)
    fig(c, 8, "ATTENTION: WHERE EACH WORD IS LOOKED FOR", 90, 215, 255 * a * smooth(prog(t, CAT_T - 0.3, CAT_T)))


def draw_guidance(c, t):
    """C4: two guesses side by side, then the push."""
    a = smooth(prog(t, TWO_T - 0.2, TWO_T + 0.3)) * (1 - smooth(prog(t, C5_T - 0.3, C5_T + 0.1)))
    if a <= 0:
        return
    sp = in_out(prog(t, TWO_T - 0.2, TWO_T + 0.6))
    push = in_out(prog(t, PUSH_T, PUSH_T + 1.0))
    w = lerp(CWID, 450, sp)
    lx, rx = lerp(CX, 285, sp), lerp(CX, 795, sp)
    right = art.step(int(lerp(16, 29, push)), size=RES)
    wa = smooth(prog(t, WITHOUT_T - 0.3, WITHOUT_T + 0.2))
    card_at(c, pic("noguide"), lx, CY, w, 255 * a * max(sp, 0.01), 0, 1, "WITHOUT YOUR PROMPT" if wa > 0.5 else None)
    card_at(c, right, rx, CY, w, 255 * a, 0, 1 + 0.06 * push, "WITH IT" if push < 0.5 else "WITH IT, PUSHED 7.5×",
            AMBER if push > 0 else None, prog(t, PUSH_T + 0.6, PUSH_T + 1.6), cap_rgb=AMBER if push > 0.5 else SMOKE)
    ta = smooth(prog(t, WITH_T - 0.2, WITH_T + 0.2))
    label(c, "TWO GUESSES, EVERY STEP", W / 2, 560, 28, "mono_bold", VIOLET, 255 * a * sp, "center", 0.2)
    if push > 0:
        y = CY + 310
        x0, x1 = 285, lerp(285, 940, push)
        c.drawLine(x0, y, x1, y, paint(AMBER, 255 * a, stroke=5))
        c.drawPath(_arrow_head(x1, y, 18), paint(AMBER, 255 * a))
    _ = ta


def draw_latent(c, t):
    """C5: the picture shrinks to a 64x64 grid, then a decoder paints it full size."""
    a = smooth(prog(t, C5_T - 0.3, C5_T + 0.3))
    if a <= 0:
        return
    shrink = in_out(prog(t, TINY_T - 0.3, TINY_T + 0.7))
    to_dec = in_out(prog(t, DEC_T - 0.1, DEC_T + 0.6))
    grow = in_out(prog(t, FULL_T - 0.6, FULL_T + 0.4))
    # ghost outline of the full size
    ga = 255 * a * smooth(prog(t, SMALL_T - 0.9, SMALL_T - 0.4)) * (1 - to_dec)
    if ga > 1:
        r = skia.Rect.MakeXYWH(CX - CWID / 2, CY - CWID / 2, CWID, CWID)
        p = paint(PAPER, ga * 0.6, stroke=2)
        p.setPathEffect(skia.DashPathEffect.Make([14, 10], 0))
        c.drawRRect(skia.RRect.MakeRectXY(r, 18, 18), p)
        label(c, "512 × 512 PIXELS × 3 COLOURS", CX, CY - CWID / 2 - 24, 22, "mono", SMOKE, ga, "center", 0.15)
    w = lerp(CWID, 250, shrink)
    x = lerp(CX, lerp(CX, 200, to_dec), 1)
    x = lerp(CX, 200, to_dec) if to_dec > 0 else CX
    img = tiny() if shrink > 0.5 else pic("hero")
    if grow < 1:
        card_at(c, img, x, CY, w, 255 * a * (1 - smooth(prog(t, FULL_T - 0.3, FULL_T))), 0, 1,
                "64 × 64 × 4 NUMBERS" if shrink > 0.8 else None, VIOLET if shrink > 0.5 else None)
        if shrink > 0.5:   # the latent grid
            ga2 = 120 * a * smooth((shrink - 0.5) * 2) * (1 - grow)
            for i in range(1, 16):
                xx = x - w / 2 + w * i / 16
                yy = CY - w / 2 + w * i / 16
                c.drawLine(xx, CY - w / 2, xx, CY + w / 2, paint(VIOLET, ga2, stroke=1))
                c.drawLine(x - w / 2, yy, x + w / 2, yy, paint(VIOLET, ga2, stroke=1))
    na = 255 * a * smooth(prog(t, SMALL_T - 0.8, SMALL_T - 0.2)) * (1 - smooth(prog(t, DEC_T - 0.3, DEC_T)))
    label(c, "48×", CX, CY + 300, 150, "mono_bold", VIOLET, na, "center")
    label(c, "FEWER NUMBERS", CX, CY + 360, 26, "mono", SMOKE, na, "center", 0.35)
    # decoder
    da = smooth(prog(t, DEC_T - 0.3, DEC_T + 0.2)) * (1 - grow)
    if da > 0:
        node_box(c, CX + 60, CY, 230, 220, t, "DECODER", 255 * a * da, 0.5 + 0.5 * smooth(prog(t, DEC_T + 0.4, DEC_T + 0.8)))
        thread(c, 200 + 125, CY, CX + 60 - 115, CY, prog(t, DEC_T + 0.1, DEC_T + 0.5), VIOLET, 255 * a * da, 0)
    if grow > 0:
        gx = lerp(CX + 175, CX, grow)
        card_at(c, pic("hero"), gx, CY, lerp(120, CWID, grow), 255 * a, 0, 1, f"SEED {SEED} · FULL IMAGE" if grow > 0.9 else None,
                AMBER, prog(t, FULL_T + 0.2, FULL_T + 1.2))
    fig(c, 9, "WHERE THE WORK REALLY HAPPENS", 90, 330, 255 * a * (1 - grow))


def draw_frame(c, t):
    background(c)
    ambient(c, t, 0.6)
    draw_reverse(c, t)
    main_card(c, t)
    draw_steer(c, t)
    draw_guidance(c, t)
    draw_latent(c, t)
    CAPS.draw(c, t)
    edges(c, t, DURATION, 0.25, 0.25)


def post_kw(t):
    g = 0.5 * max(0.0, 1 - abs(t - FRESH_T) / 0.3) + 0.3 * max(0.0, 1 - abs(t - REV_T - 0.2) / 0.3)
    return dict(glitch=g)


def sfx_events():
    ev = [(0.0, "whoosh", 0.4), (REV_T - 0.1, "rewind", 0.45), (FRESH_T - 0.05, "static_burst", 0.8),
          (FRESH_T + 0.1, "static_clear", 0.3)]
    # one tick per step, keyed to the step schedule
    last = 0
    for i in range(int(STEPS[0][0] * 100), int(DONE_T * 100) + 1):
        tt = i / 100
        k = int(step_at(tt))
        if k > last:
            ev.append((tt, "tick", 0.5 + 0.02 * k))
            last = k
    ev += [(DONE_T, "glass_ting", 0.5), (STEER_T, "shimmer", 0.35), (CAT_T - 0.35, "pluck", 0.7),
           (MOON_T - 0.35, "pluck", 0.7), (TWO_T - 0.2, "swish", 0.5), (PUSH_T, "push", 0.9),
           (TINY_T - 0.3, "descend", 0.4), (SMALL_T, "low_hit", 0.45), (DEC_T, "swish", 0.4), (FULL_T - 0.6, "whomp", 0.8),
           (FULL_T + 0.2, "shimmer", 0.4)]
    return ev


MUSIC = dict(beds=[(0.0, DURATION, "synth", 0.6), (STEP_T - 0.5, DONE_T + 1.5, "arp", 0.9), (TWO_T, DURATION, "arp", 0.7)])
