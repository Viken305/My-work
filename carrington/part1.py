"""Part 1: the hook. 1 a.m. in the Rocky Mountains, the sky so bright the miners start breakfast. The aurora swells,
the lantern irises down onto one point of light, and opens again on the Sun: the title."""
from common import *  # noqa: F401,F403

PART = "part1"
VO, _end = schedule(PART, first=0.7, gap=0.55, extra={"H3": 0.2})
TM = Timing(PART, VO)
T_ROCKY = TM.word("H1", "Rocky")
T_WOKE = TM.word("H1", "woke")
T_BREAK = TM.word("H1", "breakfast")
T_ONE = TM.word("H2", "one")
T_SKY = TM.word("H2", "sky")
T_BRIGHT = TM.word("H2", "bright")
T_SUNUP = TM.word("H2", "sun")
T_WAY = TM.word("H3", "way")
T_TITLE = TM.end("H3") + 0.35
T_HIT = T_TITLE + 1.25
DURATION = T_TITLE + 4.2
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"bright": AUR_G, "breakfast": CARD}),
               anchors={"H1": (W / 2, 1150), "H2": (W / 2, 1150), "H3": (W / 2, 1150)})
SUN_XY = (540, 640)
FAR = mountains(4, 1420, 100, 160, 0.55)
NEAR = mountains(8, 1600, 50, 120, 0.5)
_rng = np.random.default_rng(31)
PINES = [(x, min(y for xx, y in NEAR[1] if abs(xx - x) < 12) + 4, 30 + _rng.random() * 60) for x in _rng.random(70) * W]
TENTS = [(330, 46), (420, 36), (760, 52)]


def aurora_level(t):
    up = 0.25 + 0.45 * smooth(prog(t, 0.3, 4.0)) + 0.45 * smooth(prog(t, T_SKY - 0.4, T_BRIGHT + 0.6))
    return up + 0.25 * smooth(prog(t, T_WAY - 0.3, T_WAY + 0.4))


def camp(c, t):
    cam = lerp(220, 0, in_out(prog(t, 0.0, T_BRIGHT + 0.8)))       # tilt up from the camp to the sky
    glass(c)
    sky = skia.Path()
    sky.addRect(skia.Rect.MakeWH(W, 1700))
    lv = aurora_level(t)
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 1500)],
                                        [col(mix((40, 14, 40), (90, 20, 60), lv - 0.6)), col(NIGHT), col((16, 30, 40))],
                                        [0, 0.55, 1])
    p = skia.Paint(AntiAlias=True)
    p.setShader(sh)
    p.setAlphaf(0.9)
    c.drawPath(sky, p)
    c.save()
    c.translate(0, cam * 0.2)
    stars(c, 420, 11, (0, -100, W, 1400), 230 * (1.1 - 0.4 * clamp(lv - 0.4)), t)
    c.restore()
    c.save()
    c.translate(0, cam * 0.45)
    aurora(c, t, -100, W + 100, 1080, 760, 1, lv, 460, 2, 0.05)
    aurora(c, t + 3, -60, W + 60, 900, 600, 2, lv * 0.8, 380, 3, -0.08)
    aurora(c, t + 7, 200, W + 200, 1220, 520, 3, lv * 0.9, 300, 2, 0.1)
    c.restore()
    c.save()
    c.translate(0, cam * 0.75)
    c.drawPath(FAR[0], paint((26, 24, 40)))
    engrave(c, FAR[0], LIME, 110, 1.0, 0.3)
    hatch(c, FAR[0], 18, 6, 70, LIME, 0.7)
    c.restore()
    c.save()
    c.translate(0, cam)
    c.drawPath(NEAR[0], paint((14, 12, 18)))
    engrave(c, NEAR[0], LIME, 170, 1.3, 0.3)
    hatch(c, NEAR[0], 26, 5, -60, LIME, 0.7)
    c.drawPath(polyline(NEAR[1]), paint(AUR_G, 90 * lv, sigma=6, stroke=6, blend=ADD))
    for x, y, h in PINES:
        pine(c, x, y, h)
    for i, (x, s_) in enumerate(TENTS):
        yy = min(y for xx, y in NEAR[1] if abs(xx - x) < 12) + 10
        tent(c, x, yy, s_, 255)
        lit = appear(t, T_WOKE + i * 0.35, 0.3)       # lamps come on inside as the miners wake
        if lit > 0:
            c.drawCircle(x, yy - s_ * 0.25, s_ * 1.4, paint((255, 170, 90), 50 * lit, sigma=s_ * 0.8, blend=ADD))
    # the breakfast fire and its smoke
    fx = 560
    fy = min(y for xx, y in NEAR[1] if abs(xx - fx) < 12) + 8
    fa = appear(t, T_BREAK - 0.2, 0.5)
    if fa > 0:
        fl = 0.8 + 0.2 * math.sin(t * 23) * math.sin(t * 7)
        c.drawCircle(fx, fy - 6, 60, paint((255, 140, 60), 70 * fa * fl, sigma=30, blend=ADD))
        for k in range(5):
            ph = (t * 0.7 + k / 5) % 1
            c.drawCircle(fx + math.sin(ph * 9 + k) * 10, fy - 8 - ph * 26, 7 * (1 - ph), paint((255, 190, 90), 220 * fa * (1 - ph), blend=ADD))
        for k in range(4):
            sm = []
            for j in range(40):
                u = j / 39
                sm.append((fx + math.sin(u * 5 + t * 0.8 + k) * (6 + u * 40) + u * 50, fy - 20 - u * 300))
            c.drawPath(polyline(sm), paint(SILVER, 40 * fa, sigma=8, stroke=10))
    c.restore()
    tag(c, 70, 300, "ROCKY MOUNTAINS · 2 SEPT 1859", LIME, 255 * appear(t, T_ROCKY - 0.2), 20)
    ka = pop(t, T_ONE)
    if ka > 0:
        stamp_tab(c, "1:00 A.M.", 860, 420, ka, AUR_R, 30, 4)


def title(c, t):
    u = t - T_TITLE
    glass(c)
    stars(c, 300, 4, (0, 0, W, 1100), 200 * appear(t, T_TITLE, 0.6), t)
    cx, cy = SUN_XY
    k = out_expo(prog(t, T_TITLE, T_TITLE + 1.0))
    R = 300 * (0.6 + 0.4 * k)
    c.save()
    c.translate(cx, cy)
    c.rotate(u * 2.5)
    c.translate(-cx, -cy)
    bezel(c, cx, cy, R + 40, 220 * appear(t, T_TITLE + 0.3, 0.6),
          "SOL  ·  1 SEPTEMBER 1859  ·  11:18 A.M.  ·  REDHILL, SURREY  ·  ", -150)
    c.restore()
    sun_disc(c, cx, cy, R, 255 * appear(t, T_TITLE, 0.3), 1.0, 1, u * 1.5)
    sg = R / 300
    for (x, y, r, s) in ((600, 600, 26, 1), (640, 625, 18, 2), (570, 640, 14, 3), (665, 600, 11, 4), (548, 612, 9, 5)):
        sunspot(c, cx + (x - cx) * sg, cy + (y - cy) * sg, r * sg, 255, s, 0.85, 20)
    fl = appear(t, T_HIT - 0.35, 0.2) * (1 + 0.8 * hit(t, T_HIT - 0.35, 0.03, 0.4))
    if fl > 0:
        flare_bead(c, kidney(cx + 58 * sg, cy - 52 * sg, 20 * sg, 0.4), 255, 1.4 * fl)
        flare_bead(c, kidney(cx + 102 * sg, cy + 2 * sg, 16 * sg, -0.3), 255, 1.4 * fl)
    label(c, "1 SEPTEMBER 1859", W / 2, 1110, 26, "mono_bold", LIME, 230 * appear(t, T_TITLE + 0.5), "center", 0.32)
    s = "THE DAY THE SUN"
    f = font("serif_roman", 84)
    x0 = W / 2 - width(s, "serif_roman", 84, 0.04) / 2
    for j, ch in enumerate(s):
        uu = (t - T_TITLE - 0.45 - j * 0.03) / 0.45
        if uu > 0:
            projected_char(c, ch, x0, 1215, f, LIME, 255 * clamp(uu * 2.5), out_cubic(uu))
        x0 += f.measureText(ch) + 0.04 * 84
    hk = pop(t, T_HIT, 0.5)
    if hk > 0:
        s = "Hit Us"
        f = font("serif_bold", 270)
        w = width(s, "serif_bold", 270)
        c.save()
        c.translate(W / 2, 1370)
        sc = 1.35 - 0.35 * hk
        c.scale(sc, sc)
        c.translate(-W / 2, -1370)
        x = W / 2 - w / 2
        al = clamp(hk * 2)
        for ch in s:
            c.drawString(ch, x, 1450, f, paint(SUN, 120 * al, sigma=30, blend=ADD))
            c.drawString(ch, x, 1450, f, paint(SUN, 255 * al, blend=SCREEN))
            c.drawString(ch, x, 1450, f, paint(FLARE, 120 * al, blend=SCREEN))
            x += f.measureText(ch)
        c.restore()
    label(c, "the biggest solar storm ever recorded", W / 2, 1530, 44, "serif", SILVER, 255 * appear(t, T_HIT + 0.5, 0.5),
          "center")
    slide_label(c, 1, "THE CARRINGTON EVENT", 70, 150, 255 * appear(t, T_TITLE + 0.2))


def draw_frame(c, t):
    if t < T_TITLE:
        camp(c, t)
        CAP.draw(c, t)
        r = lerp(1400, 0, in_cubic(prog(t, T_TITLE - 0.75, T_TITLE)))      # iris closes on a point in the sky
        if r < 1400:
            iris(c, *SUN_XY, max(r, 0.5))
            bloom_dot(c, *SUN_XY, 4 + 10 * prog(t, T_TITLE - 0.75, T_TITLE), SUN, 255 * prog(t, T_TITLE - 0.6, T_TITLE))
    else:
        title(c, t)
        r = lerp(0, 1400, out_cubic(prog(t, T_TITLE, T_TITLE + 0.7)))
        if r < 1400:
            iris(c, *SUN_XY, max(r, 0.5))


def post_kw(t):
    kw = slide_change(t, DURATION, fin=0.0, fout=0.45)
    kw["flash"] = 0.55 * hit(t, T_HIT - 0.35, 0.03, 0.25) + 0.35 * hit(t, T_HIT, 0.02, 0.2)
    kw["shake"] = shake_env(t, T_HIT, 0.9, 0.04, 0.35)
    return kw


def sfx_events():
    return [(0.0, "wind", 0.5), (0.4, "aurora_hum", 0.6), (T_WOKE, "tent_rustle", 0.45), (T_BREAK - 0.2, "fire_crackle", 0.5),
            (T_ONE, "clock", 0.45), (T_SKY - 0.3, "aurora_swell", 0.8), (T_TITLE - 0.9, "reverse_swell", 0.8),
            (T_TITLE - 0.05, "slide_clack", 0.7), (T_HIT - 0.35, "flare_burst", 0.7), (T_HIT, "title_hit", 1.0),
            (DURATION - 0.4, "slide_clack", 0.6)]


MUSIC = dict(beds=[(0.0, T_TITLE - 0.2, "music_box", 0.55), (0.0, DURATION, "projector", 0.35),
                   (T_TITLE, DURATION + 0.4, "deep", 0.5)])
