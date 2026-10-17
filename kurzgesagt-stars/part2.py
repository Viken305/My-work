"""Part 2: Chapter 1, The First Stars. Rewind, Big Bang, the first elements, the dark ages, the first giant stars.

  python3 render.py part2 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part2"
VO, _end = schedule(PART, first=2.8, gap=0.75, extra={"U2": 0.6, "U5": 0.4})
DURATION = _end + 1.2
TM = Timing(PART, VO)

REWIND = (VO["U1"] - 0.3, VO["U2"] + 0.2)
BANG_T = TM.word("U2", "began") - 0.15
HOT = (BANG_T + 2.6, VO["U3"])
NUC = (VO["U3"] - 0.4, VO["U3"])
CHIP_T = [TM.word("U3", w) - 0.15 for w in ("hydrogen", "helium", "lithium")]
DARK = (VO["U4"] - 0.6, VO["U4"] + 0.4)
WEB_T = TM.word("U4", "gravity") - 1.0
IGN = (VO["U5"] - 0.5, VO["U5"])
FIRST_T = TM.word("U5", "first stars") - 0.2
GIANT_T = TM.word("U5", "giants") - 0.2
DIE = (VO["U6"] - 0.5, VO["U6"])
BOOMS = [TM.word("U6", "died") - 0.4 + i * 0.55 for i in range(4)]
ASH_T = TM.word("U6", "ashes") - 0.8

_rng = np.random.default_rng(17)
WARP = [(float(a), float(r)) for a, r in zip(_rng.uniform(0, 6.283, 260), _rng.uniform(0.0, 1.0, 260))]
NODES = [(float(x), float(y)) for x, y in zip(_rng.uniform(-850, 850, 22), _rng.uniform(-470, 470, 22))]
EDGES = sorted({tuple(sorted((i, j))) for i in range(len(NODES)) for j in sorted(range(len(NODES)), key=lambda j: math.dist(NODES[i], NODES[j]))[1:4]})
GIANTS = [3, 9, 14, 6, 18]
BENDS = {e: float(_rng.uniform(-0.35, 0.35)) for e in EDGES}


def filament(c, i, j, a):
    """Soft, curved gas filament between two web nodes."""
    if a <= 0.01:
        return
    (x0, y0), (x1, y1) = NODES[i], NODES[j]
    b = BENDS[(i, j)]
    mx, my = (x0 + x1) / 2 - (y1 - y0) * b, (y0 + y1) / 2 + (x1 - x0) * b
    path = skia.Path()
    path.moveTo(x0, y0)
    path.quadTo(mx, my, x1, y1)
    for w, al, bl in ((34, 45, 22), (14, 85, 9), (4, 90, 2)):
        p = skia.Paint(AntiAlias=True, Color=col((110, 130, 230), al * a), Style=skia.Paint.kStroke_Style, StrokeWidth=w)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, bl))
        p.setBlendMode(skia.BlendMode.kPlus)
        c.drawPath(path, p)


def web(c, t, a):
    draw_texture(c, tex_web(), 0, 0, 1.6, t * 0.4, 170 * a, skia.BlendMode.kPlus)
    for i, j in EDGES:
        filament(c, i, j, a)
    for x, y in NODES:
        light(c, x, y, 70, (130, 150, 240), 110 * a)
PLASMA = [(float(x), float(y), int(k)) for x, y, k in zip(_rng.uniform(-900, 900, 150), _rng.uniform(-520, 520, 150), _rng.choice([0, 0, 0, 0, 0, 0, 1, 1], 150))]


def rewind(c, t):
    """Time runs backwards: the starfield streams into the centre, faster and faster."""
    c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.8, [DEEP, VOID])))
    k = in_cubic(prog(t, REWIND[0], REWIND[1]))
    speed = 0.15 + 2.6 * k
    for a, r0 in WARP:
        r = ((r0 - (t - REWIND[0]) * speed * (0.6 + r0)) % 1.0) ** 1.6
        rr = 40 + r * 1300
        ln = rr * (0.03 + 0.22 * k)
        x0, y0 = W / 2 + math.cos(a) * rr, H / 2 + math.sin(a) * rr * 0.62
        x1, y1 = W / 2 + math.cos(a) * (rr + ln), H / 2 + math.sin(a) * (rr + ln) * 0.62
        p = skia.Paint(AntiAlias=True, Shader=linear((x0, y0), (x1, y1), [(BLUE_STAR, 230 * min(1, r * 3)), (BLUE_STAR, 0)]),
                       Style=skia.Paint.kStroke_Style, StrokeWidth=1.5 + 2.5 * r)
        p.setBlendMode(skia.BlendMode.kPlus)
        c.drawLine(x0, y0, x1, y1, p)
    light(c, W / 2, H / 2, 160 + 400 * k, (200, 210, 255), 90 + 120 * k)
    yrs = 13.8 * smooth(prog(t, VO["U1"] + 0.5, REWIND[1]))
    text(c, f"{yrs:4.1f} BILLION YEARS AGO", W / 2, 1000, 34, WHITE, 230 * smooth(prog(t, VO["U1"] + 0.3, VO["U1"] + 0.8)), 800, spacing=8)

    def path(tt):
        return 1350 + 60 * math.sin(tt * 0.7), 330 + 40 * math.sin(tt * 1.1)
    c.save()
    (x, y), _, _ = fly(path, t)
    c.translate(x, y)
    c.rotate(25 * math.sin(t * 1.4) * k)
    c.translate(-x, -y)
    orbi_on(c, t, path, 70, "wide", (-0.8, 0.4), -0.3 + 0.8 * k, rim=BLUE_STAR)
    c.restore()


def bang(c, t):
    """Singularity flash, white-out, then hot expanding plasma with space itself stretching."""
    c.drawPaint(fill(VOID))
    if t < BANG_T:
        light(c, W / 2, H / 2, 60 + 80 * prog(t, REWIND[1], BANG_T), HOTWHITE, 255, core=1)
        return
    u = t - BANG_T
    scale = 1 + u * 0.35
    temp = clamp(u / 7)
    for x, y, kind in PLASMA:   # space stretching: every particle moves away from every other
        px, py = W / 2 + x * scale * 0.7, H / 2 + y * scale * 0.7
        if -50 < px < W + 50 and -50 < py < H + 50:
            rgb = mix(HOTWHITE, AMBER, temp) if kind == 0 else mix(HOTWHITE, SOLAR, temp)
            c.drawCircle(px, py, 3 + 2 * kind, add(rgb, 170))
    glowr = 320 + u * 650
    fire_a = 1 - 0.55 * temp
    draw_texture(c, tex_fire(), W / 2, H / 2, 0.5 + u * 0.55, u * 9, 255 * fire_a, skia.BlendMode.kPlus)
    draw_texture(c, tex_fire(62), W / 2, H / 2, 0.35 + u * 0.4, -u * 13, 200 * fire_a, skia.BlendMode.kPlus)
    light(c, W / 2, H / 2, glowr, mix(SOLAR, AMBER, temp), 150)
    light(c, W / 2, H / 2, glowr * 0.4, HOTWHITE, 220 * (1 - 0.7 * temp))
    flash = math.exp(-u * 2.2)
    if flash > 0.02:
        c.drawPaint(add(HOTWHITE, 255 * flash))
        flare(c, W / 2, H / 2, 260, (170, 200, 255), 255 * flash)
    for k in range(3):  # expansion rings
        ph = prog(u, k * 0.6, k * 0.6 + 3.2)
        if 0 < ph < 1:
            c.drawCircle(W / 2, H / 2, 100 + 1400 * out_cubic(ph), stroke(HOTWHITE, 6 * (1 - ph), 200 * (1 - ph)))
    ta = smooth(prog(t, BANG_T + 1.2, BANG_T + 1.8))
    label(c, "THE BIG BANG", W / 2, 940, WHITE, 52, 255 * ta, sub="13.8 BILLION YEARS AGO")


def nucleosynthesis(c, t):
    """The first minutes: a hot fog of hydrogen and helium nuclei (and a pinch of lithium)."""
    c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.8, [(120, 50, 30), (40, 14, 20)])))
    draw_texture(c, tex_fire(63), W / 2, H / 2, 2.6, t * 2, 110, skia.BlendMode.kPlus)
    for i, (x, y, kind) in enumerate(PLASMA[:110]):
        jx = 14 * math.sin(t * 2.3 + i)
        jy = 14 * math.cos(t * 1.9 + i * 1.7)
        if kind == 0:
            atom_dot(c, W / 2 + x + jx, H / 2 + y + jy, 9, BLUE_STAR, t)
        else:
            atom_dot(c, W / 2 + x + jx, H / 2 + y + jy, 13, ELEMENTS["He"][1], t)
    lx, ly = W / 2 + 120 + 10 * math.sin(t * 2), H / 2 - 60
    if t > CHIP_T[2] - 0.5:
        atom_dot(c, lx, ly, 15, ELEMENTS["Li"][1], t)
        c.drawCircle(lx, ly, 40 + 6 * math.sin(t * 5), stroke(ELEMENTS["Li"][1], 3, 200))
    c.drawRect(skia.Rect.MakeXYWH(0, 760, W, 320), shaded(linear((0, 760), (0, H), [(VOID, 0), (VOID, 230)])))
    for i, (sym, share) in enumerate((("H", "~75%"), ("He", "~25%"), ("Li", "A PINCH"))):
        g = out_back(prog(t, CHIP_T[i], CHIP_T[i] + 0.55), 1.3)
        if g > 0:
            x = 620 + i * 340
            element_chip(c, x, 880, 150 * g, sym)
            text(c, share, x, 1010, 26, WHITE, 230 * min(1, g), 800, spacing=4)
    label(c, "THE FIRST FEW MINUTES", W / 2, 140, AMBER, 32, 255 * smooth(prog(t, NUC[1], NUC[1] + 0.5)))
    na = smooth(prog(t, TM.word("U3", "nothing else"), TM.word("U3", "nothing else") + 0.4))
    if na > 0:
        text(c, "NOTHING ELSE.", W / 2, 700, 40, WHITE, 255 * na, 800, spacing=10)


def dark_ages(c, t):
    """The universe goes dark; a faint cosmic web slowly gathers. ORBI's eye is the only light."""
    c.drawPaint(fill((3, 3, 10)))
    cam = drift_cam(t, DARK[0], IGN[1] + 6, 0, 60, 0, -30, 1.0, 1.12)
    webk = smooth(prog(t, DARK[1] + 1.0, WEB_T + 3.0))
    cam.push(c, 1.0)
    web(c, t, webk)
    cam.pop(c)

    def path(tt):
        return 520 + 80 * math.sin(tt * 0.45), 560 + 40 * math.sin(tt * 0.8)
    (x, y), _, _ = fly(path, t)
    look = (0.9 * math.sin(t * 0.5), 0.2)
    cone = skia.Path()
    ang = math.atan2(look[1], look[0])
    cone.moveTo(x + look[0] * 20, y)
    for s_ in (-0.35, 0.35):
        cone.lineTo(x + math.cos(ang + s_) * 900, y + math.sin(ang + s_) * 900)
    cone.close()
    cp = skia.Paint(AntiAlias=True, Shader=radial((x, y), 900, [(EYE, 70), (EYE, 0)]))
    cp.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(cone, cp)
    orbi_on(c, t, path, 85, "worried" if t < WEB_T else "neutral", look, -0.6, rim=(40, 60, 90), rim2=(80, 60, 120))
    label(c, "THE DARK AGES", W / 2, 140, (150, 170, 255), 32, 255 * smooth(prog(t, DARK[1], DARK[1] + 0.8)), sub="NO STARS · JUST COOLING GAS")


def first_stars(c, t):
    """Giant stars ignite along the web, then die in a chain of supernovae."""
    c.drawPaint(fill((3, 3, 10)))
    cam = drift_cam(t, IGN[0], DURATION, 60, -120, -30, 40, 1.12, 1.3)
    cam = shake(cam, t, BOOMS[0], 9, 2.0)
    cam.push(c, 1.0)
    web(c, t, 1.0)
    for n, gi in enumerate(GIANTS):
        x, y = NODES[gi]
        t_on = FIRST_T + n * 0.45
        g = out_back(prog(t, t_on, t_on + 0.7), 1.5)
        if g <= 0:
            continue
        boom = BOOMS[n % 4] + (0.3 if n == 4 else 0.0)
        if t < boom:
            star(c, x, y, 34 * g, t, BLUE_STAR, 1.0)
            if t < t_on + 0.6:
                flare(c, W / 2 + (x - cam.x) * cam.z, H / 2 + (y - cam.y) * cam.z, 70, BLUE_STAR, 200 * (1 - prog(t, t_on, t_on + 0.6)))
        else:
            shockwave(c, x, y, 230, t, prog(t, boom, boom + 3.0))
            for e, sym in enumerate(("C", "O", "Fe")):
                k = out_cubic(prog(t, boom + 0.3, boom + 2.4))
                ang = e * 2.1 + n
                atom_dot(c, x + math.cos(ang) * 240 * k, y + math.sin(ang) * 240 * k, 10, ELEMENTS[sym][1], t, 255 * (1 - smooth(prog(t, boom + 2.4, boom + 3.4))))
    cam.pop(c)
    # scale comparison: one giant next to the Sun, with ORBI
    sc = smooth(prog(t, GIANT_T, GIANT_T + 0.6)) * (1 - smooth(prog(t, BOOMS[0] - 0.6, BOOMS[0] - 0.1)))
    if sc > 0.01:
        c.saveLayerAlpha(None, int(255 * sc))
        c.drawRRect(rrect(1140, 600, 680, 400, 30), fill((8, 8, 24), 220))
        star(c, 1330, 800, 120, t, BLUE_STAR, 0.4)
        star(c, 1560, 860, 9, t, SOLAR, 0.5)
        text(c, "SUN", 1560, 900, 18, SOLAR, 230, 800, spacing=3)
        text(c, "FIRST STARS: MAYBE HUNDREDS × THE SUN'S MASS", 1480, 650, 18, WHITE, 230, 800, spacing=2)
        orbi(c, 1720, 820, 46, t, "wide", (-0.9, 0), ears=0.8, rim=BLUE_STAR)
        c.restore()
    label(c, "THE FIRST STARS", W / 2, 140, BLUE_STAR, 34, 255 * smooth(prog(t, FIRST_T, FIRST_T + 0.6)) * (1 - smooth(prog(t, DIE[0], DIE[1]))),
          sub="ONLY HYDROGEN AND HELIUM")
    ta = smooth(prog(t, ASH_T, ASH_T + 0.6))
    if ta > 0:
        c.drawRect(skia.Rect.MakeXYWH(0, 900, W, 180), shaded(linear((0, 900), (0, H), [(VOID, 0), (VOID, 220)])))
        label(c, "EVERY STAR SINCE IS BUILT FROM THEIR ASHES", W / 2, 1000, AMBER, 30, 255 * ta)


def draw_frame(c, t):
    scenes(c, t, [((0.0, 0.01), REWIND[1] + 0.05, rewind), ((REWIND[1], REWIND[1] + 0.05), HOT[1] + 0.6, bang),
                  (NUC, DARK[1], nucleosynthesis), (DARK, IGN[1], dark_ages), (IGN, DURATION + 1, first_stars)])
    chapter_title(c, t, 1, "THE FIRST STARS", BLUE_STAR, 0.2, 2.5)
    fade(c, t, DURATION, 0.5, 0.5)


def sfx_events():
    ev = [(0.2, "swell_soft", 0.6), (REWIND[0], "riser", 0.6), (REWIND[0] + 1.2, "whoosh_long", 0.7), (REWIND[1] - 1.0, "riser", 1.0),
          (BANG_T - 0.05, "boom", 1.0), (BANG_T, "whoosh_long", 1.0), (BANG_T + 0.3, "rumble", 1.0), (BANG_T + 1.6, "rumble", 0.8),
          (NUC[0], "whoosh", 0.6)] + [(x, "pop", 0.6) for x in CHIP_T] + [(x + 0.1, "chime", 0.4) for x in CHIP_T]
    ev += [(DARK[0], "whoosh_long", 0.5), (WEB_T, "swell_soft", 0.6), (IGN[0], "riser", 0.6)]
    ev += [(FIRST_T + n * 0.45, "shine", 0.6) for n in range(5)] + [(GIANT_T, "pop", 0.5)]
    ev += [(b, "boom", 0.8) for b in BOOMS] + [(BOOMS[0], "whoosh_long", 0.7), (ASH_T, "shimmer", 0.6)]
    return ev


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 14, 19)), (REWIND[1], 41, (0, 7, 12, 16, 19, 24)), (NUC[0], 43, (0, 7, 12, 16, 19)),
            (DARK[0], 40, (0, 7, 12)), (IGN[0], 45, (0, 7, 12, 16, 19, 23)), (DIE[0], 41, (0, 7, 12, 15, 19))],
    plucks=[(NUC[0], DARK[0]), (IGN[0] + 0.5, DURATION)], bpm=90, rises=[(REWIND[0] + 1, REWIND[1]), (IGN[0], FIRST_T)], drone=33,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
