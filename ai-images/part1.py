"""Part 1, the hook: a burst of static shrinks into a card while the prompt types itself; the card denoises into the
astronaut cat ("a picture like this"); the picture rewinds into pure static ("it started as this"); "No photo. No
sketch." chips strike out; the static fast-forwards through all 30 steps into the cat on "cat on the moon"; the card
flies at the camera, the frame tears into static and the title resolves out of the grain.

  python3 render.py part1 [--still 1,4,7,12,15]
"""
from film import *  # noqa: F401,F403

PART = "part1"
VO, _end = schedule(PART, first=0.6, gap=0.5)
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)

TYPE0, TYPE1 = 0.5, TM.word("H1", "and")          # the prompt types while "Type one sentence" is said
GEN0, GEN1 = TM.word("H1", "an"), TM.word("H1", "this")
REW0 = TM.word("H2", "this.")
REW1 = REW0 + 0.9
PHOTO_T, SKETCH_T = TM.word("H2", "photo."), TM.word("H2", "sketch.")
FF0, FF1 = TM.word("H3", "turn"), TM.word("H3", "moon?", end=True)
TITLE_T = TM.end("H3") + 0.35
DURATION = TITLE_T + 2.9

CAPS = Captions(TM, ENV, words=WORDS, model=MODEL, hide={"H3": [(TITLE_T, 99)]})
CARD_Y, CARD_W = 900, 780


def picture(t):
    """What the card shows at time t."""
    if t < GEN0:
        return pure_static(SEED)
    if t < REW0:
        return guess(in_out(prog(t, GEN0, GEN1)))
    if t < FF0:
        return pic("hero", in_out(prog(t, REW0, REW1)), SEED)
    return guess(prog(t, FF0, FF1) ** 0.8)


def draw_frame(c, t):
    background(c)
    ambient(c, t, 0.7)
    # camera: a slow push-in, then a fast dolly into the card before the title
    fly = in_out(prog(t, TITLE_T - 0.45, TITLE_T + 0.05))
    s = 1.0 + 0.04 * prog(t, 0, TITLE_T) + 2.2 * fly ** 2
    c.save()
    camera(c, s, 0, 0, W / 2, CARD_Y)
    # prompt box types itself
    pa = 255 * smooth(prog(t, 0.3, 0.7))
    typed = len(art.PROMPT) * prog(t, TYPE0, TYPE1)
    prompt_box(c, art.PROMPT, 120, 250, 840, pa, typed=typed, t=t)
    # the card: born from a full-screen static burst
    born = out_cubic(prog(t, 0.05, 0.75))
    w = lerp(W * 1.9, CARD_W, born)
    float_y = 6 * math.sin(t * 1.3)
    rot = (1 - born) * -4 + 0.6 * math.sin(t * 0.7)
    rew = prog(t, REW0, REW1)
    sheen = prog(t, GEN1 - 0.2, GEN1 + 1.0) if t < REW0 else prog(t, FF1 - 0.1, FF1 + 0.9)
    glow = AMBER if GEN1 < t < REW0 or t > FF1 else None
    k = int(30 * prog(t, FF0, FF1) ** 0.8)
    cap = f"SEED {SEED} · {'30 STEPS' if t < REW0 or t > FF1 else 'REWINDING…' if t < REW1 else f'STEP {k} / 30'}"
    card_at(c, picture(t), W / 2, CARD_Y + float_y, w, 255, rot, 1.0, cap if born > 0.9 else None, glow, sheen)
    if GEN1 - 0.1 < t < REW0:
        label(c, "ILLUSTRATION", W / 2 + CARD_W / 2 - 4, CARD_Y + CARD_W / 2 + 40 + float_y, 18, "mono", SMOKE,
              180 * smooth(prog(t, GEN1, GEN1 + 0.5)), "right", 0.2)
    # rewind symbol
    if REW0 - 0.1 < t < REW1 + 0.4:
        ra = 255 * smooth(prog(t, REW0 - 0.1, REW0 + 0.1)) * (1 - smooth(prog(t, REW1, REW1 + 0.4)))
        label(c, "◀◀", W / 2, CARD_Y - CARD_W / 2 - 60, 64, "bold", PAPER, ra, "center")
    # "No photo. No sketch." chips that strike through
    for i, (t0, txt) in enumerate(((PHOTO_T, "PHOTO"), (SKETCH_T, "SKETCH"))):
        q = prog(t, t0 - 0.15, t0 + 0.25)
        if q > 0 and t < FF0 + 0.3:
            ca = 255 * smooth(q) * (1 - smooth(prog(t, FF0 - 0.2, FF0 + 0.3)))
            x = W / 2 - 330 + i * 360
            y = CARD_Y + CARD_W / 2 - 40 - 22 * back_out(q)
            cw = chip(c, txt, x, y, ca, PAPER, 34, 0.12) if ca > 1 else 0
            st = smooth(prog(t, t0 + 0.15, t0 + 0.4))
            c.drawLine(x - 8, y + 30, x - 8 + (cw + 16) * st, y + 30, paint(VIOLET, ca, stroke=5))
    # step counter during the fast-forward
    fa = 255 * smooth(prog(t, FF0 - 0.2, FF0 + 0.1)) * (1 - smooth(prog(t, FF1 + 0.3, FF1 + 0.6)))
    step_ui(c, 30 * prog(t, FF0, FF1) ** 0.8, W / 2 - 380, CARD_Y - CARD_W / 2 - 70, fa)
    c.restore()
    # title: the frame tears into static and the title resolves out of it
    if t > TITLE_T - 0.15:
        q = prog(t, TITLE_T - 0.15, TITLE_T + 0.2)
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(INK, 255 * smooth(q)))
        sa = 255 * (1 - 0.75 * smooth(prog(t, TITLE_T + 0.2, TITLE_T + 1.2)))
        grain_patch(c, skia.Rect.MakeLTRB(0, 0, W, H), sa * smooth(q), int(t * 30))
        u = prog(t, TITLE_T + 0.15, TITLE_T + 1.4)
        resolve_text(c, "HOW AI DRAWS", W / 2, 860, 100, "black", PAPER, u, 3, "center", 0.06)
        resolve_text(c, "from nothing", W / 2, 1010, 150, "serif_bold", AMBER, prog(t, TITLE_T + 0.45, TITLE_T + 1.7), 9, "center")
        ga = smooth(prog(t, TITLE_T + 1.2, TITLE_T + 2.0))
        c.drawRect(skia.Rect.MakeXYWH(W / 2 - 160 * ga, 1070, 320 * ga, 3), paint(AMBER, 200 * ga))
    CAPS.draw(c, t)
    edges(c, t, DURATION, 0.0, 0.25)


def post_kw(t):
    g = max(0.0, 1 - abs(t - REW0 - 0.3) / 0.45) * 0.5 + max(0.0, 1 - abs(t - TITLE_T) / 0.25) * 0.9
    g += max(0.0, 1 - t / 0.35) * 0.6
    return dict(glitch=g)


def sfx_events():
    return [(0.0, "static_burst", 0.9), (0.45, "typing", 0.8), (GEN0 - 0.1, "static_clear", 0.45),
            (GEN1, "shimmer", 0.35), (REW0 - 0.05, "rewind", 0.8), (REW0 + 0.2, "static_hold", 0.28),
            (REW1 + 2.4, "static_hold", 0.22), (PHOTO_T, "snap", 0.6), (SKETCH_T, "snap", 0.6),
            (FF0 - 0.05, "steps_fast", 0.9), (TITLE_T - 0.4, "riser", 0.4), (TITLE_T, "static_burst", 0.8),
            (TITLE_T + 0.1, "title_hit", 0.9)]


MUSIC = dict(beds=[(0.0, REW0, "synth", 0.55), (FF0 - 0.3, DURATION, "arp", 0.9), (TITLE_T, DURATION, "synth", 0.7)])
