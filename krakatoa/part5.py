"""Part 5, the cost, the sky, the child: the island in section collapses (before = dashed ghost); a tsunami runs out
along the surface; 36,000 in sober red; blood-red sunsets with drifting ash; night sea, and in 1927 a new cone breaks
the surface: Anak Krakatau, still active. A last distant thud loops back to the hook.

  python3 render.py part5 [--still 3,8,12,16,21]
"""
from film import *  # noqa: F401,F403

PART = "part5"
VO, _end = schedule(PART, first=0.5, gap=0.55, extra={"D3": 0.3})
TM = Timing(PART, VO)
ENV = VoiceEnvelope(PART, VO)
DURATION = _end + 1.6

GONE_T = TM.word("D1", "gone.")
WAVE_T = TM.word("D1", "tsunamis") - 0.2
DIED_T = TM.word("D1", "about") - 0.1
SKY_T = VO["D2"] - 0.35
NIGHT_T = VO["D3"] - 0.35
RISE_T = TM.word("D3", "rose")
NAME_T = VO["D4"] - 0.1
ACTIVE_T = TM.word("D4", "still")

CAPS = Captions(TM, ENV, sound=SOUND, harm=HARM | {"blood red."}, hide={"D4": [(NAME_T, NAME_T + 2.2)]})
SEA = 1040
ASH = Ash(3500, 9, (0, 0, W, 1100))


def after_path():
    """What was left: half of Rakata standing as a cliff; the rest of the island gone into a drowned caldera."""
    p = skia.Path()
    p.moveTo(-40, SEA + 170)
    p.lineTo(60, SEA + 100)
    p.lineTo(140, SEA + 20)
    p.lineTo(200, SEA - 90)
    p.lineTo(255, SEA - 210)
    p.lineTo(300, SEA - 300)
    p.lineTo(318, SEA - 270)
    p.lineTo(326, SEA - 120)
    p.lineTo(340, SEA + 40)
    p.lineTo(380, SEA + 220)
    p.cubicTo(520, SEA + 330, 760, SEA + 320, 880, SEA + 230)
    p.lineTo(1040, SEA + 120)
    p.lineTo(1120, SEA + 150)
    p.lineTo(1120, 1700)
    p.lineTo(-40, 1700)
    p.close()
    return p


def child_path(h):
    """Anak Krakatau: a small cone rising from the caldera floor; h = height above the floor in px."""
    p = skia.Path()
    base, top = SEA + 290, SEA + 290 - h
    p.moveTo(470, base)
    p.cubicTo(540, base - h * 0.2, 590, top + 12, 615, top)
    p.lineTo(645, top + 6)
    p.cubicTo(670, top + 12, 720, base - h * 0.2, 790, base)
    p.close()
    return p


def sea_body(c, t):
    """Engraved water, drawn first so the rock in section sits in front of it."""
    c.drawRect(skia.Rect.MakeLTRB(-60, SEA, W + 60, 1760), paint(mix(NIGHT, PRUSSIAN, 0.7), 240))
    for i, y in enumerate(range(SEA + 6, 1760, 9)):
        wob = 3 * math.sin(t * 2 + i * 0.4)
        c.drawLine(-60, y + wob, W + 60, y - wob, paint(PAPER, 40 - min(28, i * 0.4), stroke=1.0))


def sea_surface(c, t, wave=0.0):
    """Surface line; wave in 0..1 runs a tsunami crest outward from the island (red only around the crest)."""
    xc = 420 + 720 * wave
    amp = 150 * math.sin(math.pi * clamp(wave)) ** 0.5 if 0 < wave < 1 else 0
    surf, crest = skia.Path(), skia.Path()
    started = False
    for i, x in enumerate(range(-60, W + 70, 8)):
        y = SEA - amp * math.exp(-((x - xc) / 90) ** 2) + 2 * math.sin(x * 0.03 + t * 3)
        (surf.lineTo if i else surf.moveTo)(x, y)
        if abs(x - xc) < 230 and amp > 1:
            (crest.lineTo if started else crest.moveTo)(x, y)
            started = True
    if amp > 1:
        fill = skia.Path(surf)
        fill.lineTo(W + 60, SEA + 4)
        fill.lineTo(-60, SEA + 4)
        fill.close()
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(330, 0, W + 60, H))   # the wave runs over open water, not the cliff
        c.drawPath(fill, paint(mix(NIGHT, PRUSSIAN, 0.7), 240))
        c.restore()
    c.drawPath(surf, paint(PAPER, 210, stroke=2))
    if amp > 1:
        glow_stroke(c, crest, LAVA, 255 * clamp(amp / 60), 2.6, 0.9)
        dim_line(c, xc + 130, SEA, xc + 130, SEA - amp, "30+ M", 255 * clamp(amp / 100), PAPER, 22)


def rock_hatch(c, path, a=1.0):
    c.drawPath(path, paint(mix(PRUSSIAN, PAPER, 0.1), 255 * a))
    c.save()
    c.clipPath(path, doAntiAlias=True)
    for i in range(-H, W + H, 7):
        c.drawLine(i, 0, i - H * 0.5, H, paint(PAPER, 46 * a, stroke=1.0))
    c.restore()
    c.drawPath(path, paint(PAPER, 230 * a, stroke=1.8))


def collapse(c, t):
    paper(c)
    sea_body(c, t)
    g = smooth(prog(t, GONE_T - 0.4, GONE_T + 0.4))
    before = island_path()
    dash = paint(PAPER, 200 * g, stroke=2.0)
    dash.setPathEffect(skia.DashPathEffect.Make([14, 10], 0))
    if g < 1:
        rock_hatch(c, before, 1 - g)
    rock_hatch(c, after_path(), g)
    c.drawPath(before, dash)
    if 0 < g < 1 or (t > GONE_T and t < GONE_T + 1.6):   # rubble falling into the caldera
        rng = np.random.default_rng(3)
        e = t - (GONE_T - 0.4)
        for i in range(160):
            x0, y0 = rng.uniform(380, 900), rng.uniform(SEA - 230, SEA - 20)
            y = y0 + 260 * e * e * rng.uniform(0.6, 1.2)
            if y < SEA + 300:
                c.drawCircle(x0 + rng.normal(0, 8) * e, y, rng.uniform(1.5, 4), paint(PAPER, 160 * clamp(1.6 - e)))
    label(c, "BEFORE", 640, SEA - 280, 22, "mono_bold", PAPER, 220 * g, "center", 0.25)
    label(c, "AFTER", 230, SEA - 340, 22, "mono_bold", SULFUR, 220 * g, "center", 0.25)
    sea_surface(c, t, prog(t, WAVE_T, WAVE_T + 3.4))
    label(c, "SEA LEVEL", 1040, SEA - 14, 20, "mono", PAPER, 200, "right", 0.14)
    fig(c, 7, "KRAKATOA, BEFORE AND AFTER", 70, 300, 255 * (1 - smooth(prog(t, DIED_T - 0.2, DIED_T + 0.3))))
    da = smooth(prog(t, DIED_T, DIED_T + 0.6))
    if da > 0:   # sober: the scene dims, one red number
        black(c, 0.7 * da)
        big_number(c, "36,000", 640, "PEOPLE, MOSTLY FROM THE TSUNAMIS", da, rgb=LAVA, unit_rgb=PAPER, size=170)


def sunset(c, t):
    paper(c)
    u = prog(t, SKY_T, NIGHT_T)
    hz, sy = 1060, 1000 + 70 * u
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, hz)], [col(NIGHT, 0), col(SUN_V, 170), col(LAVA, 225), col(SUN_O, 255)],
                                         [0.0, 0.4, 0.82, 1.0])
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, hz), skia.Paint(Shader=sky))
    light(c, 640, hz - 30, 700, LAVA, 120)
    for y in range(240, hz, 6):
        c.drawLine(0, y, W, y, paint(NIGHT, 26 + 20 * (1 - y / hz), stroke=1.4))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 0, W, hz))
    c.drawCircle(640, sy, 92, paint(HOT, 255))
    light(c, 640, sy, 280, SUN_O, 200)
    c.restore()
    for k, (y0, a0) in enumerate(((360, 120), (520, 150), (700, 130), (860, 110))):
        pth = skia.Path()
        pth.moveTo(-50, y0)
        for x in range(-50, W + 60, 30):
            pth.lineTo(x, y0 + math.sin(x * 0.009 + k * 2 + t * 0.15) * 30 + math.sin(x * 0.027 + k) * 10)
        c.drawPath(pth, paint((40, 14, 38), a0, sigma=18, stroke=46))
        c.drawPath(pth, paint(SUN_O, 90, sigma=1.5, plus=True, stroke=1.4))
    ASH.draw(c, t, (60, 20, 30), 0.6, tint=(50, 16, 30))
    c.drawRect(skia.Rect.MakeLTRB(0, hz, W, H), paint(NIGHT, 245))
    rng = np.random.default_rng(int(t * 6))
    for y in range(hz + 6, 1760, 7):
        d = (y - hz) / 700
        c.drawLine(0, y, W, y, paint(PAPER, 28 * (1 - d), stroke=1.0))
        spread = 30 + d * 380
        for _ in range(int(6 + 10 * (1 - d))):
            x = 640 + rng.normal(0, spread * 0.45)
            q = math.exp(-((x - 640) / spread) ** 2)
            ln = (8 + rng.random() * 40) * (1 - d * 0.5)
            c.drawLine(x - ln / 2, y, x + ln / 2, y, paint(mix(HOT, SUN_O, d * 2), 255 * q * (1 - d) ** 1.4 * (1 - u * 0.6), plus=True, stroke=1.8))
    c.drawLine(0, hz, W, hz, paint(PAPER, 160, stroke=1.4))
    ship(c, 200 + 40 * u, hz + 4, 1.0)
    fig(c, 8, "SUNSET, AROUND THE WORLD, 1883–84", 70, 300, 255, size=20)


def child(c, t):
    paper(c)
    e = t - RISE_T
    h = 330 * out_cubic(prog(t, RISE_T - 0.3, RISE_T + 2.2)) + 40
    sea_body(c, t)
    rock_hatch(c, after_path())
    cone = child_path(h)
    rock_hatch(c, cone)
    top = SEA + 290 - h
    if e > 0:   # steam and glow where it breaks the surface, then small eruptions
        light(c, 630, top, 160, LAVA, 180 * clamp(e))
        if top < SEA:
            c.save()
            c.translate(630, top)
            s = 0.18 + 0.08 * math.sin(t * 3)
            c.scale(s, s)
            c.translate(-630, -top)
            ash_column(c, 630, top, t)
            c.restore()
    if t > ACTIVE_T:
        q = (t - ACTIVE_T) % 1.4 / 1.4
        ring(c, 630, top - 20, 40 + 260 * out_cubic(q), SULFUR, 160 * (1 - q), 2.0, fringe=False, trail=0)
    sea_surface(c, t)
    label(c, "SEA LEVEL", 1040, SEA - 14, 20, "mono", PAPER, 200, "right", 0.14)
    ya = smooth(prog(t, RISE_T - 1.0, RISE_T - 0.4)) * (1 - smooth(prog(t, NAME_T - 0.3, NAME_T)))
    big_number(c, "1927", 560, "SAME PLACE, 44 YEARS LATER", ya, size=170)
    na = smooth(prog(t, NAME_T, NAME_T + 0.6)) * (1 - smooth(prog(t, DURATION - 1.0, DURATION - 0.5)))
    if na > 0:
        tr = 0.4 + (0.18 - 0.4) * out_cubic(prog(t, NAME_T, NAME_T + 1.6))
        label(c, "ANAK KRAKATAU", W / 2, 470, 78, "black", PAPER, 255 * na, "center", tracking=tr)
        k2 = smooth(prog(t, NAME_T + 0.9, NAME_T + 1.5))
        label(c, "child of Krakatoa", W / 2, 600, 92, "serif_bold", SULFUR, 255 * na * k2, "center")
    fig(c, 9, "THE SAME SPOT, 1927 → TODAY", 70, 300, 255 * smooth(prog(t, NIGHT_T, NIGHT_T + 0.6)), size=20)


def draw_frame(c, t):
    if t < SKY_T + 0.4:
        collapse(c, t)
    if SKY_T < t < NIGHT_T + 0.4:
        c.saveLayerAlpha(None, int(255 * smooth(prog(t, SKY_T, SKY_T + 0.4))))
        sunset(c, t)
        c.restore()
    if t > NIGHT_T:
        c.saveLayerAlpha(None, int(255 * smooth(prog(t, NIGHT_T, NIGHT_T + 0.4))))
        child(c, t)
        c.restore()
    CAPS.draw(c, t)
    edges(c, t, DURATION, 0.3, 0.6)


def sfx_events():
    return [(0.0, "whoosh", 0.4), (GONE_T - 0.5, "rumble", 0.4), (GONE_T - 0.1, "low_hit", 0.45),
            (WAVE_T, "wave_roar", 0.7), (SKY_T, "wind", 0.45), (RISE_T - 0.2, "rise_water", 0.6),
            (NAME_T, "title_hit", 0.45), (ACTIVE_T, "low_hit", 0.25), (DURATION - 0.9, "distant_guns", 0.7)]


MUSIC = dict(beds=[(0.0, DIED_T + 0.5, "deep", 0.6), (DIED_T - 0.3, NIGHT_T + 0.5, "aftermath", 1.2),
                   (SKY_T, NIGHT_T + 0.4, "wonder", 0.45), (NIGHT_T, DURATION, "end", 0.9)])
