"""Part 1, the hook: 1989; newspaper clippings; SCIENTISTS DRILL INTO HELL; a scream waveform erupts; tape-stop;
HOAX stamp; the flat line turns into the real borehole; title.

  python3 render.py part1 [--still 1,5]
"""
from film import *  # noqa: F401,F403

PART = "part1"
SAMPLES = 5
VO, _end = schedule(PART, first=0.6, gap=0.6)
TM = Timing(PART, VO)
DURATION = _end + 1.7

YEAR_T = TM.word("H1", "1989") - 0.15
SPREAD_T = TM.word("H1", "spread") - 0.1
SCI_T = TM.word("H1", "scientists") - 0.15
SCREAM_T = TM.word("H1", "screams") - 0.1
HELL_T = TM.word("H1", "hell")
STOP_T = VO["H2"] - 0.15                     # tape stop
HOAX_T = TM.word("H2", "hoax") - 0.02
REAL_T = TM.word("H2", "but") - 0.1
LINE_T = TM.word("H2", "real") - 0.1          # the flat line turns vertical
DOWN_T = TM.word("H2", "and what") - 0.1
TITLE_T = _end - 0.15

CAPS = Captions(TM, anchors={"H1": (W / 2, 1380), "H2": (W / 2, 1380)}, emph={"hell", "hoax", "real", "stranger"})
YEAR = Counter("1989", 300, "serif_up")
_rng = np.random.default_rng(4)
WAVE = _rng.standard_normal(400)
CLIPS = [  # (headline lines, final x, y, rotation, fly-in angle)
    (["THE", "WELL TO", "HELL"], 300, 620, -9, 200),
    (["SOVIET", "DRILL", "HITS HELL"], 790, 700, 7, -30),
    (["SOUNDS", "FROM BELOW"], 520, 980, -3, 100),
]


def clipping(c, cx, cy, w, h, rot, lines, a, ink_k=1.0, seed=0, hl=74):
    """A yellowed newspaper cutting with a heavy headline, text bars and a halftone photo."""
    if a <= 0.01:
        return
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.saveLayerAlpha(None, int(255 * a))
    shadow = skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, 150))
    shadow.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 14, -h / 2 + 24, w, h), shadow)
    paper = mix((200, 191, 174), (150, 147, 142), 1 - ink_k)
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), fillp(paper))
    r = np.random.default_rng(seed)
    for _ in range(60):
        c.drawCircle(r.uniform(-w / 2, w / 2), r.uniform(-h / 2, h / 2), r.uniform(0.5, 1.6), fillp((120, 105, 80), 50))
    ink = mix((24, 20, 18), (80, 78, 76), 1 - ink_k)
    y = -h / 2 + hl * 1.05
    for ln in lines:
        label(c, ln, -w / 2 + 34, y, hl, "black", ink, 255, tracking=-0.01)
        y += hl * 0.96
    y += 10
    pw = w * 0.42
    for i in range(int((h / 2 - y - 30) // 22)):        # columns of text
        yy = y + i * 22
        c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 34, yy, w - 68 - pw - 20 if True else 0, 8), fillp(ink, 80))
    px0, py0 = w / 2 - 34 - pw, y
    ph = h / 2 - 34 - y
    if ph > 40:                                           # halftone photo of the tower
        c.drawRect(skia.Rect.MakeXYWH(px0, py0, pw, ph), fillp(mix(paper, ink, 0.25)))
        for ix in range(int(pw // 9)):
            for iy in range(int(ph // 9)):
                xx, yy = px0 + 4.5 + ix * 9, py0 + 4.5 + iy * 9
                dx = (xx - (px0 + pw * 0.5)) / pw
                v = clamp(0.25 + 0.75 * (abs(dx) < 0.08 + 0.3 * ((yy - py0) / ph) ** 3) + 0.3 * ((yy - py0) / ph > 0.8))
                c.drawCircle(xx, yy, 4.2 * v, fillp(ink, 200))
    c.restore()
    c.restore()


def waveform(c, t, amp, y=760, a=1.0):
    """The 'scream': a jittering audio waveform with RGB split."""
    if amp <= 0.01 or a <= 0.01:
        return
    xs = np.linspace(40, W - 40, 220)
    env = np.sin(np.linspace(0, math.pi, len(xs))) ** 0.6
    k = int(t * 60) % 180
    vals = WAVE[k:k + len(xs)] if k + len(xs) <= len(WAVE) else np.resize(WAVE, len(xs))
    for dx, rgb in ((-5, (255, 40, 20)), (0, (255, 140, 60)), (5, (255, 210, 160))):
        p = skia.Path()
        ys = y + vals * env * amp * (0.8 + 0.4 * math.sin(t * 37))
        p.moveTo(xs[0] + dx, ys[0])
        for x_, y_ in zip(xs[1:], ys[1:]):
            p.lineTo(x_ + dx, y_)
        c.drawPath(p, stroke(rgb, 3, 200 * a, plus=True))


def draw_frame(c, t):
    void(c, t, warm=0.35 * smooth(prog(t, SCREAM_T - 0.5, SCREAM_T + 0.3)) * (1 - smooth(prog(t, STOP_T, HOAX_T))))
    sx, sy = shake(t, SCREAM_T, 10, 2.0)
    if t > STOP_T:
        sx, sy = shake(t, HOAX_T, 26, 7)
    c.save()
    c.translate(sx, sy)
    push = lerp(1.0, 1.08, prog(t, 0, STOP_T))
    c.translate(W / 2, 860)
    c.scale(push, push)
    c.translate(-W / 2, -860)
    drain = smooth(prog(t, STOP_T, HOAX_T))           # tape-stop drains the colour
    gone = smooth(prog(t, REAL_T, LINE_T))            # cards fall away
    # 1989
    ya = smooth(prog(t, YEAR_T, YEAR_T + 0.3)) * (1 - smooth(prog(t, SPREAD_T + 0.3, SPREAD_T + 0.9)))
    yy = lerp(860, 700, in_out(prog(t, SPREAD_T - 0.2, SPREAD_T + 0.8)))
    ys = lerp(1.0, 0.8, in_out(prog(t, SPREAD_T - 0.2, SPREAD_T + 0.8)))
    if ya > 0:
        c.save()
        c.translate(W / 2, yy)
        c.scale(ys, ys)
        YEAR.draw(c, 0, 100, t, YEAR_T, 1.1, PAPER, 255 * ya, "center")
        c.restore()
    # clippings fly in on "spread", then step aside for the headline
    for i, (lines, fx, fy, rot, ang) in enumerate(CLIPS):
        u = out_expo(prog(t, SPREAD_T + i * 0.22, SPREAD_T + i * 0.22 + 0.8))
        if u <= 0:
            continue
        side = smooth(prog(t, SCI_T - 0.3, SCI_T + 0.5))
        dx, dy = math.cos(math.radians(ang)) * 1400 * (1 - u), math.sin(math.radians(ang)) * 1400 * (1 - u)
        x = fx + dx + (fx - W / 2) * 0.9 * side
        y = fy + dy + 180 * side
        clipping(c, x, y, 470, 400, rot + 20 * (1 - u), lines, (1 - 0.6 * side) * (1 - gone), 1 - drain, seed=i, hl=58)
    # the main headline
    hu = out_expo(prog(t, SCI_T, SCI_T + 0.7))
    if hu > 0 and gone < 1:
        c.save()
        cy = 760 + 400 * in_cubic(gone)
        c.translate(W / 2, cy)
        sc = lerp(1.25, 1.0, hu)
        c.scale(sc, sc)
        c.rotate(-2 + 14 * gone)
        clipping(c, 0, 0, 760, 600, 0, ["SCIENTISTS", "DRILL INTO", "HELL"], hu * (1 - gone), 1 - drain, seed=9, hl=104)
        c.restore()
    # the scream waveform, then the tape stop flattens it
    amp = 170 * smooth(prog(t, SCREAM_T, HELL_T)) * (1 - in_out(prog(t, STOP_T, HOAX_T - 0.1)))
    if amp > 1:                               # the lights die and only the scream is left
        c.drawPaint(fillp(VOID, 175 * clamp(amp / 120)))
        light(c, W / 2, 1100, 900, (200, 50, 20), 120 * clamp(amp / 170))
    waveform(c, t, amp * 1.6, 760, 1 - drain * 0.7)
    # HOAX stamp
    if t > HOAX_T:
        u = prog(t, HOAX_T, HOAX_T + 0.18)
        sc = lerp(1.9, 1.0, out_cubic(u))
        a = smooth(clamp(u * 3)) * (1 - gone)
        c.save()
        c.translate(W / 2, 800)
        c.rotate(-8)
        c.scale(sc, sc)
        f = font("black", 210)
        wtxt = f.measureText("HOAX")
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-wtxt / 2 - 40, -190, wtxt + 80, 240), 18, 18), stroke(EMBER, 10, 255 * a))
        c.drawString("HOAX", -wtxt / 2, 0, f, fillp(EMBER, 235 * a))
        c.restore()
        for i in range(24):                  # dust puff
            an = i / 24 * 6.28
            r = 260 + 260 * out_cubic(prog(t, HOAX_T, HOAX_T + 0.8))
            c.drawCircle(W / 2 + math.cos(an) * r, 780 + math.sin(an) * r * 0.5, 6, paint(PAPER, 120 * (1 - prog(t, HOAX_T, HOAX_T + 0.8)) * (1 - gone), 4))
    c.restore()
    # the flat line becomes the borehole
    if t > STOP_T + 0.2:
        la = smooth(prog(t, STOP_T + 0.2, HOAX_T)) if t < LINE_T else 1.0
        rot = in_out(prog(t, LINE_T, LINE_T + 0.9))
        cam_k = in_out(prog(t, DOWN_T - 0.3, TITLE_T))
        if t > LINE_T + 0.4:                 # the rock appears around it and we start to descend
            cam = Section(d=lerp(-300, 2600, cam_k), ppm=lerp(0.9, 0.35, cam_k))
            ra = smooth(prog(t, LINE_T + 0.4, DOWN_T + 0.4))
            c.saveLayerAlpha(None, int(255 * ra))
            strata(c, cam, t, heat=0.6, labels=0)
            c.restore()
            hole(c, cam, 12262, t, width_m=0.23, glow=1.0, bit=False)
        c.save()
        c.translate(W / 2, 860)
        c.rotate(90 * rot)
        L = lerp(940, 4200, rot)
        c.drawLine(-L / 2, 0, L / 2, 0, stroke(EMBER, 3, 255 * la * (1 - smooth(prog(t, LINE_T + 0.5, LINE_T + 0.9)))))
        light(c, 0, 0, 300, EMBER, 80 * la * (1 - rot))
        c.restore()
    if t < TITLE_T - 0.2:
        CAPS.draw(c, t)
    if t > TITLE_T:
        c.drawRect(skia.Rect.MakeXYWH(0, 640, W, 560), paint(VOID, 170 * smooth(prog(t, TITLE_T, TITLE_T + 0.4)), 60))
        title(c, t, TITLE_T, 880)
    fade(c, t, DURATION, 0.0, 0.25)


def sfx_events():
    ev = [(0.0, "room_tone", 0.5), (YEAR_T, "tick_roll", 0.7), (YEAR_T + 1.0, "low_hit", 0.6)]
    ev += [(SPREAD_T + i * 0.22, "paper_whoosh", 0.7) for i in range(3)] + [(SPREAD_T + i * 0.22 + 0.55, "paper_slap", 0.6) for i in range(3)]
    ev += [(SCI_T - 0.25, "swish", 0.7), (SCI_T + 0.05, "paper_slap", 1.0), (SCI_T + 0.1, "low_hit", 0.7),
           (SCREAM_T - 1.2, "riser_dark", 0.9), (SCREAM_T, "scream_texture", 0.9), (STOP_T, "tape_stop", 1.0),
           (HOAX_T - 0.35, "reverse_swell", 0.8), (HOAX_T, "stamp", 1.0), (HOAX_T, "sub_drop", 0.9),
           (LINE_T, "glass_ting", 0.6), (LINE_T + 0.1, "swish", 0.6), (DOWN_T - 0.2, "descend", 0.9),
           (TITLE_T - 0.6, "reverse_swell", 0.8), (TITLE_T, "trailer_hit", 1.0), (TITLE_T + 0.02, "sub_drop", 0.8)]
    return ev


MUSIC = dict(beds=[(0.0, STOP_T, "tension", 0.55), (STOP_T + 0.75, DURATION, "deep", 0.6)], pulse=[(SCI_T, STOP_T, 92)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
