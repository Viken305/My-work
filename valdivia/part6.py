"""Part 6: what it left behind. Cordón Caulle erupts; the coast sinks up to 2 m and the forest drowns (the caption
sinks with it); then later great quakes ring the Earth more quietly than 1960; the bell fades on the end card."""
from common import *  # noqa: F401,F403
from ink import _word_layout
from frames import _plume

PART = "part6"
VO, _end = schedule(PART, first=0.6, gap=0.6, extra={"E2": 0.3, "E3": 0.7})
TM = Timing(PART, VO)
T_VOLC = TM.word("E1", "volcano")
T_ERUPT = TM.word("E1", "erupted")
T_SANK = TM.word("E2", "sank")
T_2M = TM.word("E2", "two")
T_FLOOD = TM.word("E2", "flooded")
T_DROWN = TM.word("E2", "drowned")
T_FLATS = TM.word("E2", "tidal")
T_SCENE2 = VO["E3"] - 0.5
T_NEVER = TM.word("E3", "never")
T_1960 = TM.word("E3", "nineteen")
T_END = _end + 0.6
DURATION = T_END + 3.6
SANK_PHRASE = (VO["E2"], T_2M + 0.9)
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"loudly": BRONZE, "1960": BRONZE, "erupted": RED}),
               hide={"E2": [SANK_PHRASE]})
WATER = 1110
TREES = [(120, 470, 1), (300, 330, 2), (430, 560, 3), (610, 280, 4), (900, 520, 6), (1010, 330, 7)]


def sink(t):
    return in_out(prog(t, T_SANK - 0.2, T_SANK + 1.6))


def forest(c, t):
    fig(c, 7, "SUNKEN FOREST, NEAR VALDIVIA", 70, 268, size=20)
    sky = skia.GradientShader.MakeLinear([(0, 200), (0, WATER)], [col(BONE, 0), col(WHITE), col(mix(BONE, RED, 0.07))],
                                         [0, 0.65, 1])
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, WATER), skia.Paint(Shader=sky))
    vx, vtop = 760, 850
    g = out_cubic(prog(t, T_ERUPT - 0.1, T_ERUPT + 3.5))
    if g > 0:
        rng = np.random.default_rng(4)
        back = _plume(vx, vtop, rng, 26, 120 * g, 520 * g, 170 * g, 20 + 14 * g, 100 * g)
        cutout(c, back, mix(SEPIA, INK, 0.2), 255 * clamp(g * 4), lift=10, edge_a=150)
        hatch(c, back, 40 * clamp(g * 4), 7, 30, INK, 0.9)
        front = _plume(vx + 10, vtop - 40 * g, rng, 18, 70 * g, 380 * g, 120 * g, 16 + 10 * g, 70 * g)
        cutout(c, front, mix(SHADE, SEPIA, 0.35), 255 * clamp(g * 4), lift=8, edge_a=170)
        hatch(c, front, 30 * clamp(g * 4), 9, -30, INK, 0.9)
        la = appear(t, T_ERUPT + 0.4)
        tab(c, 330, 396, 300, 30, 290 * la)
        label(c, "CORDÓN CAULLE · ERUPTING", 620, 418, 18, "mono_bold", INK, 240 * la, "right", 0.12)
        c.drawLine(624, 412, 680, 450, paint(INK, 200 * la, stroke=1.4))
    c.drawCircle(vx, vtop + 6, 40, paint(RED, 170 * appear(t, T_ERUPT - 0.1), sigma=18, blend=MULT))
    for k, (pts, fill) in enumerate((
            ([(-20, 1000), (180, 940), (360, 975), (560, 925), (700, 900), (740, vtop + 4), (790, vtop + 4), (840, 905),
              (960, 960), (1100, 950)], mix(SHADE, SEPIA, 0.45)),
            ([(-20, 1060), (160, 1030), (330, 1050), (520, 1020), (760, 1055), (940, 1030), (1100, 1050)], mix(SHADE, INK, 0.16)))):
        p = skia.Path()
        p.moveTo(-20, WATER + 10)
        for x, y in pts:
            p.lineTo(x, y)
        p.lineTo(1100, WATER + 10)
        p.close()
        cutout(c, p, fill, lift=6 + k * 4, edge_a=140)
    # the ground the trees stand on: 150 px (2 m) above the water, then it sinks
    s = sink(t)
    base = WATER - 150 * (1 - s)
    gp = skia.Path()
    gp.moveTo(-20, base)
    for x in range(-20, W + 30, 40):
        gp.lineTo(x, base + math.sin(x * 0.02) * 6)
    gp.lineTo(W + 20, WATER + 160)
    gp.lineTo(-20, WATER + 160)
    gp.close()
    cutout(c, gp, mix(SHADE, SEPIA, 0.15), lift=8, edge_a=200)
    hatch(c, gp, 50, 8, 20, INK, 0.9)
    jit = shake_env(t, T_SANK - 0.2, 1, 0.1, 1.2)
    for x, h, sd in TREES:
        dead_tree(c, x + math.sin(t * 40 + sd) * 3 * jit, base + 4, h, sd)
    # water in front (calm surface, lines); trees show through it faintly once the ground has dropped below it
    c.drawRect(skia.Rect.MakeLTRB(0, WATER, W, H), paint(mix(BONE, TEAL, 0.15), 225 + 30 * (1 - s)))
    for y in range(WATER + 6, H, 7):
        d = (y - WATER) / (H - WATER)
        c.drawLine(0, y, W, y, paint(TEAL, 60 + 70 * d, stroke=1.0))
    if s > 0.3:
        for x, h, sd in TREES:
            for k in range(3):
                rr = ((t * 0.6 + k / 3) % 1)
                c.drawOval(skia.Rect.MakeXYWH(x - 30 - rr * 60, WATER + 2 + rr * 8, 60 + rr * 120, 10 + rr * 6),
                           paint(TEAL, 200 * (1 - rr) * s, stroke=1.4))
    c.drawLine(0, WATER, W, WATER, paint(TEAL, 255, stroke=2.2))
    oa = appear(t, T_SANK + 0.6)
    if oa > 0:
        old = WATER - 150
        c.drawLine(0, old, W, old, dashed(paint(RED, 230 * oa, stroke=2.4), 18, 12))
        tab(c, 150, old - 44, 440, 32, 290 * oa)
        label(c, "GROUND LEVEL BEFORE 22 MAY 1960", 162, old - 20, 18, "mono_bold", RED, 255 * oa, tracking=0.12)
        dim_line(c, 56, old, 56, WATER, "−2 M", 255 * appear(t, T_2M), RED, 22)
    fa = appear(t, T_FLATS - 0.1)
    if fa > 0:
        tab(c, 600, WATER + 40, 420, 34, 290 * fa)
        label(c, "FIELDS → TIDAL FLATS", 1006, WATER + 64, 20, "mono_bold", TEAL, 255 * fa, "right", 0.12)


def sinking_caption(c, t):
    if not (SANK_PHRASE[0] - 0.05 <= t <= SANK_PHRASE[1] + 0.4):
        return
    a = appear(t, SANK_PHRASE[0] - 0.05, 0.2) * (1 - smooth(prog(t, SANK_PHRASE[1], SANK_PHRASE[1] + 0.4)))
    size, y = 96, 1420
    words = ["the", "coast", "sank"]
    kinds, sizes, ws, xs, total = _word_layout(words, size, {2: TEAL})
    t_word = [VO["E2"] + 0.4, TM.word("E2", "coast"), T_SANK]
    for i in range(2):
        wa = a * appear(t, t_word[i] - 0.05, 0.25)
        label(c, words[i], xs[i], y, sizes[i], kinds[i], INK, 255 * wa)
    if t < T_SANK - 0.05:
        return
    f = font(kinds[2], sizes[2])
    drop = sink(t)
    wl = y - 14
    for top, bottom, dxk, al, rgb in [(-300, wl, 0, 255, INK)] + [(wl + k, wl + k + 5, math.sin(k * 0.35 + t * 3) * 4,
                                                                   255 * (1 - k / 80) * 0.55, TEAL) for k in range(0, 80, 5)]:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(0, y + top if top < 0 else top, W, bottom))
        x = xs[2]
        for j, ch in enumerate("sank"):
            dy = j * 9 * drop
            c.drawString(ch, x + dxk, y + dy, f, paint(rgb, al * a * appear(t, T_SANK - 0.05, 0.2)))
            x += f.measureText(ch)
        c.restore()
    gsh = skia.GradientShader.MakeLinear([(xs[2] - 60, 0), (xs[2] + ws[2] + 60, 0)],
                                         [col(TEAL, 0), col(TEAL, 255 * a), col(TEAL, 255 * a), col(TEAL, 0)], [0, 0.15, 0.85, 1])
    lp = skia.Paint(AntiAlias=True, Shader=gsh, StrokeWidth=2.4, Style=skia.Paint.kStroke_Style)
    c.drawLine(xs[2] - 60, wl, xs[2] + ws[2] + 60, wl, lp)


QUAKES = [("1964 · ALASKA", 9.2), ("2004 · SUMATRA", 9.1), ("2011 · JAPAN", 9.1), ("2010 · CHILE", 8.8)]


def since(c, t):
    fig(c, 8, "THE EARTH RINGING, BY EARTHQUAKE", 70, 268, size=20)
    y0 = 340
    rows = QUAKES + [("1960 · CHILE", 9.5)]
    for i, (name, m) in enumerate(rows):
        last = i == len(rows) - 1
        ta = (T_1960 - 0.2) if last else (VO["E3"] + 0.3 + i * 0.45)
        a = appear(t, ta, 0.4)
        if a <= 0:
            continue
        y = y0 + i * 150 + (40 if last else 0)
        h = 130 if last else 110
        c.save()
        c.translate((1 - out_expo(prog(t, ta, ta + 0.6))) * 120, 0)
        card(c, 70, y, 940, h, 255 * a)
        amp = 10 ** (1.5 * (m - 9.5))       # relative size (seismic moment)
        rgb = BRONZE
        label(c, name, 96, y + 34, 18, "mono_bold", INK, 255 * a, tracking=0.12)
        label(c, f"M {m}", 984, y + 34, 18, "mono_bold", RED if last else INK, 255 * a, "right", 0.12)
        pts = []
        for k in range(301):
            u = k / 300
            pts.append((96 + u * 888, y + h * 0.62 - math.sin(2 * math.pi * u * 4 - t * 2.2) * (h * 0.32) * amp * math.exp(-u * 0.6)))
        c.drawLine(96, y + h * 0.62, 984, y + h * 0.62, paint(SEPIA, 140 * a, stroke=1.0))
        glow(c, polyline(pts, out_cubic(prog(t, ta, ta + 0.9)))[0], rgb, 255 * a, 3.0 if last else 2.0, 0.8 if last else 0.4)
        c.restore()
    ra = appear(t, T_1960 + 0.6)
    if ra > 0:
        label(c, "RELATIVE SIZE OF EACH QUAKE'S RINGING (SEISMIC MOMENT)", 540, 1140, 16, "mono", SEPIA, 255 * ra, "center", 0.1)


def end_card(c, t):
    u = t - T_END
    pts = []
    for i in range(601):
        x = i / 600
        pts.append((-20 + x * (W + 40), 1150 - math.sin(2 * math.pi * x * 2.2 - u * 1.4) * 70 * math.exp(-u * 0.25)))
    c.drawLine(-20, 1150, W + 20, 1150, paint(SEPIA, 160, stroke=1.0))
    p, tip = polyline(pts, out_cubic(prog(u, 0.0, 1.4)))
    glow(c, p, BRONZE, 255, 2.4, 0.6)
    if tip and u < 1.4:
        pen_dot(c, *tip)
    s = pop(u, 0.25, 0.5)
    if s > 0:
        w = width("1960", "serif_bold", 240)
        ring_word(c, "1960", W / 2 - w / 2, 800, 240, BRONZE, clamp(s * 1.5), strike=u - 0.25)
    label(c, "THE DAY THE EARTH RANG LIKE A BELL", W / 2, 920, 24, "mono_bold", INK, 255 * appear(u, 0.8), "center", 0.14)
    label(c, "@BrighterMinds", W / 2, 1420, 34, "semibold", INK, 255 * appear(u, 1.3), "center", 0.04)


def draw_frame(c, t):
    paper(c)
    c.save()
    c.translate(0, drum_scroll(t, DURATION, 0.6, 0.0))
    out = in_cubic(prog(t, T_SCENE2, T_SCENE2 + 0.6))
    if out < 1:
        c.save()
        c.translate(0, -out * H * 0.7)
        forest(c, t)
        c.restore()
    out2 = in_cubic(prog(t, T_END - 0.3, T_END + 0.3))
    if T_SCENE2 < t and out2 < 1:
        c.save()
        c.translate(0, (1 - out_expo(prog(t, T_SCENE2 + 0.1, T_SCENE2 + 0.9))) * H * 0.6 - out2 * H * 0.7)
        since(c, t)
        c.restore()
    if t > T_END - 0.2:
        c.save()
        c.translate(0, (1 - out_expo(prog(t, T_END - 0.1, T_END + 0.7))) * H * 0.6)
        end_card(c, t)
        c.restore()
    CAP.draw(c, t, lambda tt: 0.4 * shake_env(tt, T_SANK - 0.2, 1, 0.1, 1.2), plate=t > T_SCENE2)
    sinking_caption(c, t)
    c.restore()
    fo = smooth(prog(t, DURATION - 0.6, DURATION))
    if fo > 0:
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(BONE, 255 * fo))


def post_kw(t):
    return dict(shake=0.25 * shake_env(t, T_SANK - 0.2, 1, 0.1, 1.2))


def sfx_events():
    ev = [(0.0, "paper_whoosh", 0.5), (T_ERUPT - 0.1, "eruption", 0.9), (T_SANK - 0.25, "deep_rumble", 0.9),
          (T_FLOOD - 0.2, "wave_roar", 0.6), (T_SCENE2, "paper_whoosh", 0.6)]
    ev += [(VO["E3"] + 0.3 + i * 0.45, "pen_scratch", 0.35) for i in range(4)]
    ev += [(T_1960 - 0.2, "pen_scratch", 0.5), (T_END - 0.2, "paper_whoosh", 0.5), (T_END + 0.25, "bell", 1.0)]
    return ev


MUSIC = dict(beds=[(0.0, T_SCENE2, "aftermath", 0.8), (T_SCENE2, DURATION + 0.4, "piano", 0.8)])
