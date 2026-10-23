"""Part 5: the aurora. The sky catches fire; a small globe shows the auroral oval sliding from the poles down to
Cuba, Hawaii and Panama; in the northeastern US the light was bright enough to read a newspaper by."""
from common import *  # noqa: F401,F403
from part1 import FAR, NEAR, PINES, TENTS

PART = "part5"
VO, _end = schedule(PART, first=0.6, gap=0.6)
TM = Timing(PART, VO)
T_SKY = TM.word("D1", "sky")
T_FIRE = TM.word("D1", "fire")
T_AUR = TM.word("D2", "Auroras")
T_POLES = TM.word("D2", "poles")
T_BLAZED = TM.word("D2", "blazed")
T_CUBA = TM.word("D2", "Cuba")
T_HAWAII = TM.word("D2", "Hawaii")
T_PANAMA = TM.word("D2", "Panama")
T_NE = TM.word("D3", "northeastern")
T_READ = TM.word("D3", "read")
DURATION = _end + 1.0
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"cuba": AUR_R, "hawaii": AUR_R, "panama": AUR_R, "fire": AUR_R, "light": AUR_G}),
               anchors={k: (W / 2, 1220) for k in VO})
PINS = (("CUBA", -79.5, 22.0, T_CUBA), ("HAWAII", -157.0, 20.5, T_HAWAII), ("PANAMA", -79.5, 9.0, T_PANAMA))


def level(t):
    return 0.3 + 0.9 * smooth(prog(t, T_SKY - 0.3, T_FIRE + 0.3)) + 0.4 * hit(t, T_FIRE, 0.05, 0.8)


def newspaper(c, t):
    k = out_expo(prog(t, T_READ - 0.5, T_READ + 0.3))
    if k <= 0:
        return
    c.save()
    c.translate(lerp(-520, 80, k), 560)
    c.rotate(-5)
    w, h = 400, 300
    r = skia.Rect.MakeXYWH(0, 0, w, h)
    c.drawRect(r.makeOffset(6, 10), paint((0, 0, 0), 150, sigma=12))
    c.drawRect(r, paint(mix(CARD, AUR_G, 0.18)))
    label(c, "EXTRA", w / 2, 40, 22, "serif_bold", SEPIA, 255, "center")
    c.drawLine(16, 54, w - 16, 54, paint(SEPIA, 200, stroke=1.5))
    label(c, "SEPTEMBER 2, 1859", w / 2, 74, 12, "mono", SEPIA, 230, "center", 0.12)
    label(c, "THE AURORA", w / 2, 116, 34, "serif_roman", SEPIA, 255, "center", 0.04)
    rng = np.random.default_rng(3)
    for col_ in range(3):
        for ln in range(9):
            x0 = 18 + col_ * 126
            L = 106 * (0.6 + 0.4 * rng.random()) if ln % 4 == 3 else 106
            c.drawLine(x0, 140 + ln * 16, x0 + L, 140 + ln * 16, paint(SEPIA, 120, stroke=3))
    # the aurora light falling on the page
    g = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(w, h)], [col(AUR_G, 70), col(AUR_R, 30)], [0, 1])
    p = skia.Paint(AntiAlias=True)
    p.setShader(g)
    p.setBlendMode(SCREEN)
    c.drawRect(r, p)
    c.restore()


def draw_frame(c, t):
    lv = level(t)
    glass(c)
    sky = skia.Path()
    sky.addRect(skia.Rect.MakeWH(W, 1700))
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 1500)],
                                        [col(mix((40, 14, 40), (130, 24, 60), lv - 0.5)), col(NIGHT), col((16, 30, 40))],
                                        [0, 0.55, 1])
    p = skia.Paint(AntiAlias=True)
    p.setShader(sh)
    p.setAlphaf(0.9)
    c.drawPath(sky, p)
    stars(c, 420, 11, (0, -100, W, 1400), 230 * (1.1 - 0.5 * clamp(lv - 0.4)), t)
    rise = 260 * (1 - out_expo(prog(t, T_SKY - 0.4, T_FIRE + 0.4)))
    c.save()
    c.translate(0, rise)
    aurora(c, t, -100, W + 100, 1080, 760, 1, lv, 460, 2, 0.05)
    aurora(c, t + 3, -60, W + 60, 900, 600, 2, lv * 0.8, 380, 3, -0.08)
    aurora(c, t + 7, 200, W + 200, 1220, 520, 3, lv * 0.9, 300, 2, 0.1)
    c.restore()
    c.drawPath(FAR[0], paint((26, 24, 40)))
    engrave(c, FAR[0], LIME, 110, 1.0, 0.3)
    hatch(c, FAR[0], 18, 6, 70, LIME, 0.7)
    c.drawPath(NEAR[0], paint((14, 12, 18)))
    engrave(c, NEAR[0], LIME, 170, 1.3, 0.3)
    hatch(c, NEAR[0], 26, 5, -60, LIME, 0.7)
    c.drawPath(polyline(NEAR[1]), paint(AUR_G, 90 * min(lv, 1.3), sigma=6, stroke=6, blend=ADD))
    for x, y, h in PINES:
        pine(c, x, y, h)
    for x, s_ in TENTS:
        yy = min(y for xx, y in NEAR[1] if abs(xx - x) < 12) + 10
        tent(c, x, yy, s_)
    # the reach of the aurora
    ga = appear(t, T_AUR - 0.3, 0.4)
    if ga > 0:
        gx, gy, gr = 840, 330, 150 * (0.8 + 0.2 * out_expo(prog(t, T_AUR - 0.3, T_AUR + 0.4)))
        pr = Ortho(-110 + 4 * math.sin(t * 0.3), 28, gr, gx, gy)
        c.drawCircle(gx, gy, gr + 14, paint(VOID, 230 * ga, sigma=8))
        earth(c, pr, ga, (0, -1), 0.0)
        lat = lerp(64, 23, in_out(prog(t, T_BLAZED - 0.2, T_PANAMA + 0.2)))
        light(c, lat_circle(pr, 64), AUR_G, 160 * ga, 1.6, 0.6, None)
        light(c, lat_circle(pr, lat), AUR_R if lat < 45 else AUR_G, 240 * ga, 2.4, 1.0, None)
        for name, lon, la_, t0 in PINS:
            k = pop(t, t0 - 0.1, 0.4)
            if k > 0:
                x, y, z = pr(lon, la_)
                bloom_dot(c, x, y, 3 * k, AUR_R, 255 * clamp(k))
                label(c, name, x + 10, y + 20, 14, "mono_bold", LIME, 255 * clamp(k), tracking=0.1)
        tag(c, 70, 300, "THE AURORA REACHED", LIME, 255 * appear(t, T_BLAZED - 0.2), 20)
        tag(c, 70, 350, "THE TROPICS", AUR_R, 255 * appear(t, T_CUBA - 0.2), 20)
    newspaper(c, t)
    tag(c, 70, 940, "NORTHEASTERN U.S. · 2 SEPT 1859", LIME, 255 * appear(t, T_NE - 0.2), 18)
    slide_label(c, 5, "THE SKY ON FIRE", 70, 150, 255 * appear(t, 0.4))
    CAP.draw(c, t)


def post_kw(t):
    kw = slide_change(t, DURATION)
    kw["flash"] = 0.2 * hit(t, T_FIRE, 0.05, 0.4)
    return kw


def sfx_events():
    return [(0.25, "slide_whoosh", 0.6), (0.2, "aurora_hum", 0.8), (T_SKY - 0.3, "aurora_swell", 1.0),
            (T_FIRE, "low_hit", 0.6), (T_AUR - 0.3, "lens", 0.4), (T_CUBA - 0.1, "pop", 0.45),
            (T_HAWAII - 0.1, "pop", 0.45), (T_PANAMA - 0.1, "pop", 0.5), (T_READ - 0.5, "paper_whoosh", 0.6),
            (DURATION - 0.4, "slide_clack", 0.6)]


MUSIC = dict(beds=[(0.0, DURATION + 0.3, "wonder", 0.65), (0.0, DURATION, "projector", 0.3)])
