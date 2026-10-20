"""Storyboard: one key frame per shot (drawn with the kit; every picture is vector art from art.py), laid out on sheets with timing,
voice-over, action and sound notes.

  python3 storyboard.py   -> out/storyboard_1.png ... (and out/panels/NN.png at full 1080x1920)
"""
import os
import textwrap

import cv2
import numpy as np
import skia
from PIL import Image

import art
import kit
from kit import *  # noqa: F401,F403
from script import PARTS

LINES = {k: v for part in PARTS.values() for k, v in part}
CAP_Y = 1380


def cap(c, words, emph=(), rgb=AMBER):
    """Static caption as it will look on that frame (max 3 words, emphasis in serif italic)."""
    size = 80
    ws = words.split()
    kinds = [("serif_bold" if w.strip(".,?").lower() in emph else "bold") for w in ws]
    tot = sum(width(w, k, size) for w, k in zip(ws, kinds)) + 0.32 * size * (len(ws) - 1)
    x = W / 2 - tot / 2
    for w, k in zip(ws, kinds):
        r = rgb if k == "serif_bold" else PAPER
        label(c, w, x + 3, CAP_Y + 5, size, k, INK, 200, sigma=6)
        label(c, w, x, CAP_Y, size, k, r)
        x += width(w, k, size) + 0.32 * size


def hero(name="hero"):
    return art.image(name)


def step(i, name="hero"):
    return art.step(i, name=name)


SEEDS = {"hero": 1883, "seed_a": 11, "seed_b": 22, "seed_c": 33}


def big_card(c, arr, y=430, w=760, caption=None, glow=None):
    card(c, arr, (W - w) / 2, y, w, caption, glow=glow)


# ---------------------------------------------------------------- the shots
def s01(c):
    background(c)
    prompt_box(c, art.PROMPT, 110, 250, 860, typed=None, caret=False)
    big_card(c, hero(), 440, caption=f"SEED {SEEDS['hero']} · 30 STEPS")
    label(c, "ILLUSTRATION", 910, 1240, 18, "mono", SMOKE, 200, "right", 0.2)
    cap(c, "in seconds.", emph=("seconds.",), rgb=VIOLET)


def s02(c):
    background(c)
    n = static(1883)
    img = noisy(hero(), n, 0.7)
    big_card(c, img, 440, caption="REWINDING…")
    label(c, "◀◀", W / 2, 360, 70, "bold", PAPER, 230, "center")
    cap(c, "Pure noise.", emph=("noise",), rgb=VIOLET)


def s03(c):
    background(c)
    big_card(c, noisy(hero(), static(1883), 1.0), 440, caption="STEP 0 / 30")
    for k, (x, y) in enumerate(((200, 380), (880, 1390), (150, 1450))):
        label(c, "?", x, y, 90, "serif_bold", AMBER, 120 - k * 30)
    cap(c, "turn static into", emph=("static",), rgb=VIOLET)


def s04(c):
    background(c)
    n = static(7)
    arr = (n * 60 + 128)
    draw_img(c, np.clip(arr, 0, 255), 0, 0, W, H, 70, 0)
    label(c, "HOW AI DRAWS", W / 2, 860, 104, "black", PAPER, 255, "center", 0.06)
    label(c, "from nothing", W / 2, 1010, 150, "serif_bold", AMBER, 255, "center")


def s05(c):
    background(c)
    toks = art.TOKENS
    prompt_box(c, art.PROMPT, 110, 300, 860, caret=False, a=90)
    x, y = 110, 620
    for tk in toks:
        tk = tk.replace("</w>", "")
        wd = width(tk, "mono_bold", 34) + 40
        if x + wd > 980:
            x, y = 110, y + 90
        chip(c, tk, x, y)
        x += wd + 16
    fig(c, 2, f"{len(toks)} TOKENS", 110, 560)
    cap(c, "pieces called tokens", emph=("tokens",))


def s06(c):
    background(c)
    chip(c, "cat", 110, 330)
    barcode(c, art.embedding("cat"), 110, 470, 860, 300)
    label(c, "768", W / 2, 960, 170, "mono_bold", VIOLET, 255, "center")
    label(c, "NUMBERS PER TOKEN", W / 2, 1020, 26, "mono", SMOKE, 255, "center", 0.3)
    fig(c, 3, "“cat” AS NUMBERS (ILLUSTRATION)", 110, 300)
    cap(c, "768 numbers", emph=("numbers",), rgb=VIOLET)


def s07(c):
    background(c)
    focus = {"cat", "kitten", "moon", "planet"}
    for w, (a, b) in art.MEANING.items():
        x, y = 160 + a * 760, 380 + b * 760
        hot = w in focus
        c.drawCircle(x, y, 9 if hot else 6, paint(AMBER if hot else SMOKE, 255 if hot else 160))
        if hot:
            c.drawCircle(x, y, 26, paint(AMBER, 120, sigma=12))
        label(c, str(w), x + 16, y + 8, 28 if hot else 22, "mono_bold" if hot else "mono", AMBER if hot else SMOKE)
    fig(c, 4, "MAP OF MEANING (SIMPLIFIED)", 110, 320)
    cap(c, "near kitten", emph=("kitten",))


def s08(c):
    background(c)
    runs = ["train_dog", "train_mountain", "train_lighthouse", "seed_a", "seed_b", "paris", "seed_c", "hero", "noguide"]
    caps = ["a golden retriever", "a snowy mountain", "a lighthouse", "a cat", "a cat", "Paris", "a cat", "the moon", "?"]
    k = 0
    for row in range(5):
        for col_ in range(3):
            x, y = 60 + col_ * 330 + (row % 2) * 60, 240 + row * 300
            card(c, hero(runs[k % 9]), x, y, 260, caps[k % 9].upper(), a=200 if row != 2 else 255)
            k += 1
    cap(c, "billions of images", emph=("images",))


def s09(c):
    background(c)
    img = hero("train_dog")
    n = static(5)
    for i, k in enumerate((0, 0.25, 0.5, 0.75, 1.0)):
        card(c, noisy(img, n, k), 70 + i * 192, 560, 172, f"{int(k * 1000)}")
    fig(c, 5, "TRAINING: NOISE ADDED STEP BY STEP (OF 1,000)", 70, 500)
    c.drawLine(80, 820, 990, 820, paint(VIOLET, 200, stroke=3))
    label(c, "→", 990, 832, 40, "bold", VIOLET, 255, "right")
    cap(c, "buried in noise", emph=("noise",), rgb=VIOLET)


def s10(c):
    background(c)
    img = hero("train_dog")
    n = static(5)
    card(c, noisy(img, n, 0.55), 70, 520, 330, "NOISY PICTURE")
    r = skia.Rect.MakeXYWH(430, 590, 220, 190)
    c.drawRRect(skia.RRect.MakeRectXY(r, 24, 24), paint(VIOLET, 140, sigma=30))
    c.drawRRect(skia.RRect.MakeRectXY(r, 24, 24), paint(CARD))
    c.drawRRect(skia.RRect.MakeRectXY(r, 24, 24), paint(VIOLET, 255, stroke=3))
    label(c, "MODEL", 540, 700, 34, "mono_bold", VIOLET, 255, "center", 0.2)
    card(c, np.clip(n * 60 + 128, 0, 255), 680, 520, 330, "ITS GUESS: THE NOISE")
    fig(c, 6, "THE ONE JOB IT IS TRAINED ON", 70, 460)
    cap(c, "guess the noise", emph=("noise",), rgb=VIOLET)


def s11(c):
    background(c)
    big_card(c, noisy(hero(), static(1), 1.0), 440, caption=f"SEED {SEEDS['hero']} · STEP 0 / 30")
    label(c, "NEW RANDOM STATIC", W / 2, 390, 30, "mono_bold", VIOLET, 255, "center", 0.3)
    cap(c, "fresh random static", emph=("static",), rgb=VIOLET)


def s12(c):
    background(c)
    for i, s_ in enumerate((2, 6, 12, 28)):
        x, y = 90 + (i % 2) * 460, 330 + (i // 2) * 520
        card(c, step(s_), x, y, 440, f"STEP {s_ + 1} · MODEL'S GUESS")
    fig(c, 7, "THE MODEL'S GUESS, STEP BY STEP", 90, 290)
    cap(c, "Then shapes.", emph=("shapes",), rgb=VIOLET)


def _attn(word):
    return art.attn(word)


def s13(c):
    background(c)
    card(c, heat(hero(), _attn("cat")), 90, 420, 440, "WHERE IT LOOKS FOR “cat”")
    card(c, heat(hero(), _attn("moon")), 550, 420, 440, "WHERE IT LOOKS FOR “moon”")
    chip(c, "cat", 230, 300)
    chip(c, "moon", 680, 300)
    for x0, x1 in ((280, 310), (740, 770)):
        p = skia.Path()
        p.moveTo(x0, 360)
        p.cubicTo(x0, 400, x1, 390, x1, 520)
        c.drawPath(p, paint(AMBER, 220, stroke=2.5))
    fig(c, 8, "ATTENTION: WORD → PLACE", 90, 960)
    cap(c, "looking for moon", emph=("moon",))


def s14(c):
    background(c)
    card(c, hero("noguide"), 90, 440, 440, "WITHOUT YOUR PROMPT")
    card(c, hero(), 550, 440, 440, "WITH IT, PUSHED 7.5×", glow=AMBER)
    label(c, "→", W / 2, 700, 70, "bold", AMBER, 255, "center")
    fig(c, 9, "GUIDANCE", 90, 380)
    cap(c, "pushes harder", emph=("harder",), rgb=VIOLET)


def s15(c):
    background(c)
    small = cv2.resize(hero(), (64, 64), interpolation=cv2.INTER_AREA)
    card(c, cv2.resize(small, (512, 512), interpolation=cv2.INTER_NEAREST), 90, 520, 300, "64 × 64 × 4")
    r = skia.Rect.MakeXYWH(420, 600, 160, 140)
    c.drawRRect(skia.RRect.MakeRectXY(r, 20, 20), paint(CARD))
    c.drawRRect(skia.RRect.MakeRectXY(r, 20, 20), paint(VIOLET, 255, stroke=3))
    label(c, "DECODER", 500, 680, 22, "mono_bold", VIOLET, 255, "center", 0.15)
    card(c, hero(), 610, 470, 400, "512 × 512 × 3")
    label(c, "48× SMALLER", 240, 470, 34, "mono_bold", VIOLET, 255, "center", 0.1)
    cap(c, "48 times smaller", emph=("smaller",), rgb=VIOLET)


def s16(c):
    background(c)
    for i, (n, sd) in enumerate(SEEDS.items()):
        x, y = 90 + (i % 2) * 460, 330 + (i // 2) * 520
        card(c, hero(n), x, y, 440, f"SEED {sd}")
    fig(c, 10, "SAME PROMPT, 4 DIFFERENT STARTING STATICS", 90, 290)
    cap(c, "a different cat", emph=("cat",))


def s17(c):
    background(c)
    sd = SEEDS["hero"]
    card(c, hero(), 90, 520, 440, f"SEED {sd}")
    card(c, hero(), 550, 520, 440, f"SEED {sd}")
    label(c, "=", W / 2, 790, 90, "bold", PAPER, 255, "center")
    cap(c, "exact same cat", emph=("same",), rgb=VIOLET)


def s18(c):
    background(c)
    big_card(c, noisy(hero(), static(1883), 0.5), 440, caption="→ STEP 0")
    cap(c, "sculpted by words", emph=("words",))


SHOTS = [  # fn, time, VO key, action, sound
    (s01, "0:00–0:04", "H1", "Finished hero picture on a floating card, its prompt above; small 'ILLUSTRATION' tag. Slow push-in.", "Soft synth chord; card 'whoosh' in."),
    (s02, "0:04–0:07", "H2", "The picture REWINDS: noise floods back over it (the real forward-noise maths).", "Tape-rewind zip; hiss rises with the noise."),
    (s03, "0:07–0:11", "H2", "Pure static fills the card. Hold one beat.", "Full static hiss, then 1 beat of silence."),
    (s04, "0:11–0:16", "H3", "Static plays forward at 4× speed into the cat (30 steps), then the title resolves out of grain.", "Ticks speed up; hiss falls away; title hit."),
    (s05, "0:16–0:24", "A1–A2", "Prompt box; the sentence snaps apart into tokens (amber chips).", "Key clicks; a 'snap' per chip."),
    (s06, "0:24–0:29", "A2", "The 'cat' chip unfolds into 768 numbers (violet barcode). Counter to 768.", "Data sparkle, rising counter ticks."),
    (s07, "0:29–0:38", "A3", "Chips fly into a map of meaning. cat lands by kitten, moon by planet.", "Soft pings as each word lands."),
    (s08, "0:38–0:44", "B1", "A wall of captioned pictures scrolls up fast.", "Fast shutter flicker, music lifts."),
    (s09, "0:44–0:51", "B2", "One picture (dog) gets buried in noise across 5 cards, 0 → 1,000.", "Hiss grows card by card."),
    (s10, "0:51–0:58", "B3", "Noisy picture → MODEL box → its guess: the noise. The model's one job.", "Glassy 'click' as the guess appears."),
    (s11, "0:58–1:02", "C1", "Hard reset: brand-new static on the card, SEED shown, STEP 0/30.", "Static burst; music drops to pulse."),
    (s12, "1:02–1:12", "C2", "Steps: blobs of colour → shapes → fur and craters. Step counter runs 1 → 30.", "Rising tick per step; hiss fades."),
    (s13, "1:12–1:19", "C3", "Amber threads from the 'cat' and 'moon' chips into the picture; a glow shows where it looks.", "String pluck per thread."),
    (s14, "1:19–1:26", "C4", "Split: the same seed without the prompt (mush) vs with it, pushed 7.5×.", "Two-note 'push' swell."),
    (s15, "1:26–1:34", "C5", "The real work happens on a tiny 64×64 grid; a decoder blows it up to full size. '48× smaller'.", "Low 'whomp' as it scales up."),
    (s16, "1:34–1:40", "D1", "Same prompt, 4 seeds, 4 different cats (pop in one by one).", "4 pops on the beat."),
    (s17, "1:40–1:44", "D2", "Same seed twice → identical cats, '='.", "Lock-in 'clunk'."),
    (s18, "1:44–1:52", "D3", "Final cat dissolves back into static, which becomes the opening frame (loop).", "Hiss swells, cut to silence; loops."),
]


def sheet(shots, n0, path):
    pw, ph, gap, tx = 340, 604, 40, 300
    cols = 3
    rows = (len(shots) + cols - 1) // cols
    sw, sh = gap + cols * (pw + gap), 150 + rows * (ph + tx + gap)
    s = skia.Surface(sw, sh)
    c = s.getCanvas()
    c.clear(col(CARBON))
    label(c, "HOW AI DRAWS FROM NOTHING · STORYBOARD", gap, 70, 34, "black", PAPER, 255, tracking=0.06)
    label(c, f"SHEET {n0 // 6 + 1} · 9:16 SHORT · ~1:52 · ALL PICTURES DRAWN IN CODE", gap, 112, 20, "mono",
          SMOKE, 255, tracking=0.15)
    os.makedirs(os.path.join(HERE, "out", "panels"), exist_ok=True)
    for i, (fn, tm, vo, act, sfx) in enumerate(shots):
        frame = kit.render(lambda c, t: fn(c), 0.0, samples=1)
        Image.fromarray(frame).save(os.path.join(HERE, "out", "panels", f"{n0 + i + 1:02d}.png"))
        x, y = gap + (i % cols) * (pw + gap), 150 + (i // cols) * (ph + tx + gap)
        img = sk_image(cv2.resize(frame, (pw, ph), interpolation=cv2.INTER_AREA))
        c.drawImage(img, x, y)
        c.drawRect(skia.Rect.MakeXYWH(x, y, pw, ph), paint(SMOKE, 120, stroke=1))
        label(c, f"{n0 + i + 1:02d}", x, y + ph + 40, 30, "mono_bold", AMBER, 255)
        label(c, tm, x + pw, y + ph + 40, 20, "mono", SMOKE, 255, "right", 0.1)
        keys = vo.split("–")
        text = LINES[keys[0]] if len(keys) == 1 else LINES[keys[0]] + " " + LINES["A" + keys[1][-1]]
        yy = y + ph + 74
        for ln in textwrap.wrap("“" + text + "”", 40)[:4]:
            label(c, ln, x, yy, 17, "serif", PAPER, 235)
            yy += 23
        yy += 6
        for ln in textwrap.wrap(act, 42)[:4]:
            label(c, ln, x, yy, 16, "medium", PAPER, 200)
            yy += 21
        for ln in textwrap.wrap("SFX: " + sfx, 38)[:2]:
            label(c, ln, x, yy + 4, 15, "mono", VIOLET, 230)
            yy += 20
    rgb = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
    Image.fromarray(rgb).save(path)
    print(path)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    for k in range(0, len(SHOTS), 6):
        sheet(SHOTS[k:k + 6], k, os.path.join(HERE, "out", f"storyboard_{k // 6 + 1}.png"))
