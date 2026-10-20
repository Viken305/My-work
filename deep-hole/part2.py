"""Part 2, the hole: the Arctic drill site at night (coordinates, 1970); top-down, the 23 cm hole against a dinner
plate; then we dive into it and fall 12,262 m with the counter.

  python3 render.py part2 [--still 1,5]
"""
from film import *  # noqa: F401,F403

PART = "part2"
VO, _end = schedule(PART, first=0.3, gap=0.55)
TM = Timing(PART, VO)
DURATION = _end + 1.5

SITE_T = 0.0
GEO_T = TM.word("A1", "in the arctic") - 0.2
YEAR_T = TM.word("A1", "1970") - 0.1
TOP_T = VO["A2"] - 0.35                         # cut to the top-down view
CM_T = TM.word("A2", "twenty") - 0.1
PLATE_T = TM.word("A2", "dinner") - 0.25
DIVE_T = VO["A3"] - 0.55                        # dive into the hole
FALL_T = TM.word("A3", "twelve") - 0.15
FALL_END = TM.word("A3", "metres", end=True) + 0.1

CAPS = Captions(TM, anchors={"A1": (W / 2, 1440), "A2": (W / 2, 1440), "A3": (W / 2, 1440)},
                emph={"superdeep", "arctic", "1970", "twenty", "three", "centimetres", "dinner", "plate"},
                hide={"A3": [(FALL_T + 0.1, DURATION)]})
SNOW = Snow(170)
DUST = Dust(70, 5)
YEAR = Counter("1970", 120, "mono_bold")


def site(c, t):
    k = in_out(prog(t, 0, TOP_T))
    c.save()
    sc = lerp(1.0, 1.12, k)
    c.translate(W / 2, 1300)
    c.scale(sc, sc)
    c.translate(-W / 2, -1300)
    c.drawRect(skia.Rect.MakeWH(W, H), grad_v(0, 1350, (6, 8, 14), (20, 24, 34)))
    stars(c, t, 0.9, 150, 3, 1100)
    aurora(c, t, 1.0)
    gy = 1350
    c.drawRect(skia.Rect.MakeLTRB(-200, gy, W + 200, H + 200), grad_v(gy, H, (58, 62, 70), (18, 19, 23)))
    for i in range(18):                                   # snowdrift lines
        y = gy + 20 + i * 30 + 6 * math.sin(i)
        c.drawLine(-100, y, W + 100, y + 8 * math.sin(i * 1.7), stroke((90, 96, 106), 1.2, 70))
    for k, (amp, yb, rgb) in enumerate(((60, gy - 20, (16, 18, 26)), (40, gy - 5, (22, 24, 32)))):   # distant hills
        xs = np.linspace(-200, W + 200, 40)
        hp = path_of([(x, yb - amp * (0.5 + 0.5 * math.sin(x * 0.006 + k * 2) * math.sin(x * 0.0021 + k))) for x in xs] + [(W + 200, gy + 5), (-200, gy + 5)], True)
        c.drawPath(hp, fillp(rgb))
    light(c, W / 2, gy - 40, 620, (255, 140, 60), 70)
    for sgn in (-1, 1):                                    # floodlight cones
        cone = path_of([(W / 2 + 40 + sgn * 60, gy - 470), (W / 2 + 40 + sgn * 520, gy + 60), (W / 2 + 40 + sgn * 260, gy + 60)], True)
        cp = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([(0, gy - 470), (0, gy + 60)],
                        [skia.Color(255, 200, 140, 40), skia.Color(255, 200, 140, 0)]), BlendMode=skia.BlendMode.kPlus)
        cp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
        c.drawPath(cone, cp)
    tower(c, W / 2 + 40, gy, 1.25, t)
    fog = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([(0, gy - 140), (0, gy + 120)],
                     [skia.Color(120, 126, 140, 0), skia.Color(120, 126, 140, 70), skia.Color(120, 126, 140, 0)]))
    c.drawRect(skia.Rect.MakeLTRB(-200, gy - 140, W + 200, gy + 120), fog)
    c.restore()
    SNOW.draw(c, t, 0.9)
    ga = smooth(prog(t, GEO_T, GEO_T + 0.4))
    if ga > 0:                                            # location HUD
        reveal(c, "69°23′46″N   30°36′31″E", 72, 320, 30, t, GEO_T, "mono", PAPER, 230, stagger=0.02, dur=0.35, rise=0.2, blur=6)
        reveal(c, "KOLA PENINSULA · RUSSIA", 72, 366, 24, t, GEO_T + 0.25, "mono", ASH, 220, tracking=0.12, stagger=0.015, dur=0.3, rise=0.2, blur=5)
        lk = out_cubic(prog(t, GEO_T, GEO_T + 0.8))
        c.drawLine(72, 392, 72 + 520 * lk, 392, stroke(ASH, 1.4, 150))
    if t > YEAR_T:
        label(c, "DRILLING BEGINS", 72, 470, 24, "mono", ASH, 220 * smooth(prog(t, YEAR_T, YEAR_T + 0.3)), tracking=0.12)
        YEAR.draw(c, 66, 600, t, YEAR_T, 1.1, EMBER, 255)


def top_view(c, t):
    """Looking straight down the hole: dark concrete, the 23 cm hole, a dinner plate laid over it."""
    zoom = lerp(1.0, 1.06, prog(t, TOP_T, DIVE_T))
    dive = in_cubic(prog(t, DIVE_T, DIVE_T + 0.65))
    sc = zoom * lerp(1.0, 9.0, dive)
    c.save()
    c.translate(W / 2, 900)
    c.scale(sc, sc)
    c.translate(-W / 2, -900)
    c.drawPaint(fillp((30, 30, 32)))
    light(c, W / 2 - 200, 600, 900, (90, 86, 80), 120)
    r = np.random.default_rng(6)
    for _ in range(260):                                  # concrete grit
        c.drawCircle(r.uniform(0, W), r.uniform(0, H), r.uniform(0.6, 2.4), fillp((70, 68, 66), r.uniform(40, 120)))
    for i in range(5):
        c.drawLine(r.uniform(0, W), r.uniform(0, H), r.uniform(0, W), r.uniform(0, H), stroke((18, 18, 20), 1.5, 120))
    R_ = 230                                              # 23 cm -> 460 px
    c.drawCircle(W / 2, 900, R_ + 34, fillp((44, 40, 38)))
    c.drawCircle(W / 2, 900, R_ + 34, stroke((90, 70, 55), 3, 200))
    for k in range(10):
        c.drawCircle(W / 2, 900, R_ * (1 - k * 0.09), fillp((3 + k, 3 + k * 0.6, 3), 255))
    light(c, W / 2, 900, R_ * 0.5, (255, 90, 30), 60 + 30 * math.sin(t * 2))
    c.restore()
    if dive > 0.95:
        return
    pa = smooth(prog(t, PLATE_T, PLATE_T + 0.5)) * (1 - dive)
    if pa > 0:                                            # dinner plate outline (26 cm) over the hole
        pr = 260 * lerp(1.15, 1.0, out_cubic(prog(t, PLATE_T, PLATE_T + 0.6)))
        p = stroke(PAPER, 3, 230 * pa)
        p.setPathEffect(skia.DashPathEffect.Make([18, 12], -t * 30))
        c.drawCircle(W / 2, 900, pr, p)
        c.drawCircle(W / 2, 900, pr * 0.66, stroke(PAPER, 1.6, 140 * pa))
        label(c, "DINNER PLATE", W / 2, 900 - pr - 40, 26, "mono", PAPER, 220 * pa, "center", tracking=0.2)
    da = smooth(prog(t, CM_T, CM_T + 0.4)) * (1 - dive)
    if da > 0:                                            # dimension line across the hole
        k = out_cubic(prog(t, CM_T, CM_T + 0.6))
        y = 900 + 300
        c.drawLine(W / 2 - 230 * k, y, W / 2 + 230 * k, y, stroke(EMBER, 3, 255 * da))
        for s in (-1, 1):
            x = W / 2 + s * 230 * k
            c.drawLine(x, y - 18, x, y + 18, stroke(EMBER, 3, 255 * da))
            c.drawLine(x, y - 40, x, y - 120, stroke(EMBER, 1.5, 120 * da))
        label(c, "23 cm", W / 2, y + 70, 54, "mono_bold", EMBER, 255 * da, "center")


def fall(c, t):
    """The plunge: depth follows the counter; the camera zooms out until the whole hole fits."""
    u = prog(t, DIVE_T + 0.62, FALL_END)
    e = 1 - (1 - u) ** 2.4
    depth = 12262 * e
    zk = in_out(prog(t, DIVE_T + 0.4, FALL_END + 0.3))
    ppm = math.exp(lerp(math.log(3.0), math.log(FULL['ppm']), zk))
    fk = smooth(clamp((0.5 - ppm) / (0.5 - FULL['ppm'])))
    cam = Section(d=lerp(depth, FULL['d'], fk), ppm=ppm, cy=lerp(H / 2, FULL['cy'], fk))
    void(c, t, warm=0.3 * e)
    strata(c, cam, t, heat=0.5 + 0.5 * e, labels=smooth(prog(t, FALL_END - 0.6, FALL_END + 0.4)))
    hole(c, cam, max(depth, 1), t, glow=1.0)
    sp = (1 - u) * (u > 0) * 1.0
    if sp > 0.02:                                         # speed streaks
        for i in range(30):
            x = (hsh(i, 1) * W)
            y = (hsh(i, 2) * H - t * 3000 * (0.5 + hsh(i, 3))) % (H + 400) - 200
            c.drawLine(x, y, x, y + 160 + 200 * hsh(i, 4), stroke(PAPER, 1.4, 90 * sp))
    DUST.draw(c, t, 0.7, scroll=depth * ppm)
    gauge(c, depth, t, smooth(prog(t, DIVE_T + 0.5, DIVE_T + 0.9)))
    ca = smooth(prog(t, FALL_T, FALL_T + 0.2)) * (1 - smooth(prog(t, FALL_END + 0.6, FALL_END + 1.1)))
    if ca > 0:                                            # the big number
        c.drawRect(skia.Rect.MakeXYWH(0, 1200, W, 320), paint(VOID, 150 * ca, 50))
        txt = f"{int(round(depth)):,}"
        wn = width(txt, "mono_bold", 168)
        x0 = W / 2 - 40 - wn / 2
        sg = 9 * (1 - u) ** 1.5 if u < 1 else 0                  # the fast-changing digits blur
        label(c, txt[:-3], x0, 1390, 168, "mono_bold", PAPER, 255 * ca)
        label(c, txt[-3:], x0 + width(txt[:-3], "mono_bold", 168), 1390, 168, "mono_bold", PAPER, 255 * ca, sigma=sg)
        label(c, "m", x0 + wn + 14, 1390, 90, "serif", EMBER, 255 * ca)
        label(c, "DEEP", W / 2, 1460, 26, "mono", ASH, 220 * ca, "center", tracking=0.4)
    if t > FALL_END + 0.9:
        yb = cam.sy(12262)
        la = smooth(prog(t, FALL_END + 0.9, FALL_END + 1.3))
        c.drawLine(W / 2 + 20, yb, W / 2 + 120, yb, stroke(EMBER, 2, 230 * la))
        label(c, "12,262 m", W / 2 + 134, yb + 12, 34, "mono_bold", EMBER, 255 * la)


def draw_frame(c, t):
    if t < TOP_T:
        site(c, t)
        if t > TOP_T - 0.25:
            c.drawPaint(fillp(VOID, 255 * smooth(prog(t, TOP_T - 0.25, TOP_T))))
    elif t < DIVE_T + 0.62:
        top_view(c, t)
        if t < TOP_T + 0.25:
            c.drawPaint(fillp(VOID, 255 * (1 - smooth(prog(t, TOP_T, TOP_T + 0.25)))))
        if t > DIVE_T + 0.35:
            c.drawPaint(fillp(VOID, 255 * smooth(prog(t, DIVE_T + 0.35, DIVE_T + 0.62))))
    else:
        fall(c, t)
        if t < DIVE_T + 0.85:
            c.drawPaint(fillp(VOID, 255 * (1 - smooth(prog(t, DIVE_T + 0.62, DIVE_T + 0.85)))))
    CAPS.draw(c, t)
    fade(c, t, DURATION, 0.0, 0.0)


def sfx_events():
    return [(0.0, "wind", 0.7), (2.0, "wind", 0.5), (GEO_T, "tick_roll", 0.45), (YEAR_T, "counter", 0.5), (YEAR_T + 1.1, "low_hit", 0.55),
            (TOP_T - 0.3, "swish", 0.6), (TOP_T, "low_hit", 0.4), (CM_T, "pop", 0.6), (PLATE_T, "glass_ting", 0.4),
            (DIVE_T - 0.4, "reverse_swell", 0.8), (DIVE_T + 0.1, "descend", 1.0), (FALL_T, "drill", 0.7), (FALL_T, "counter", 0.6),
            (FALL_END - 0.9, "riser", 0.6), (FALL_END, "trailer_hit", 0.9), (FALL_END + 0.02, "sub_drop", 0.8)]


MUSIC = dict(beds=[(0.0, TOP_T, "deep", 0.5), (TOP_T, DURATION, "tension", 0.45)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
