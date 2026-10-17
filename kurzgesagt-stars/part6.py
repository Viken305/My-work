"""Part 6: Chapter 5, A Violent End. Onion core, iron, collapse, supernova, neutron star / black hole.

  python3 render.py part6 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part6"
VO, _end = schedule(PART, first=2.8, gap=0.75, extra={"G3": 0.9})
DURATION = _end + 1.6
TM = Timing(PART, VO)

LAYERS = ["H", "He", "C", "O", "Si", "Fe"]
LAYER_T = [VO["G1"] + 2.6, VO["G1"] + 3.2] + [TM.word("G1", w) - 0.15 for w in ("carbon", "oxygen", "silicon", "iron")]
IRON = (VO["G2"] - 0.5, VO["G2"])
OFF_T = TM.word("G2", "switches off") - 0.2
COLLAPSE = TM.word("G2", "collapses") - 0.3
BOOM = VO["G3"] - 0.35
REMNANT = (VO["G4"] - 0.5, VO["G4"])
NS_T = TM.word("G4", "neutron star") - 0.3
SPOON_T = TM.word("G4", "teaspoon") - 0.3
BH_T = TM.word("G4", "black hole") - 0.5


def onion_scene(c, t):
    cam = drift_cam(t, 0, IRON[1], 0, 0, 0, 0, 1.0, 1.1)
    space(c, t, cam, clouds=("cloud",), a=0.4)
    split = in_out(prog(t, VO["G1"] + 1.4, VO["G1"] + 2.6))
    cx, cy, R = 820, 540, 400
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(0, 0, cx + (1 - split) * 1200, H))
    star(c, cx, cy, R, t, BLUE_STAR, 0.25)
    c.restore()
    if split > 0:
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(cx + (1 - split) * 1200, 0, W, H))
        for i, sym in enumerate(LAYERS):
            g = smooth(prog(t, LAYER_T[i], LAYER_T[i] + 0.5))
            if g <= 0:
                continue
            rr = R * (1 - i / len(LAYERS)) * (0.85 + 0.15 * g)
            _, rgb = ELEMENTS[sym]
            c.drawCircle(cx, cy, rr, shaded(radial((cx, cy), rr, [lighten(rgb, 0.25), rgb, darken(rgb, 0.2)], [0, 0.7, 1])))
            c.drawCircle(cx, cy, rr, stroke(WHITE, 2, 90))
        c.restore()
    for i, sym in enumerate(LAYERS):
        g = smooth(prog(t, LAYER_T[i] + 0.1, LAYER_T[i] + 0.5))
        if g <= 0:
            continue
        rr = R * (1 - (i + 0.5) / 6)
        ang = math.radians(-50 + i * 18)
        px, py = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
        lx, ly = 1400, 220 + i * 120
        c.drawLine(px, py, lerp(px, lx - 20, g), lerp(py, ly - 10, g), stroke(WHITE, 2, 160 * g))
        c.drawCircle(px, py, 6, fill(WHITE, 255 * g))
        name, rgb = ELEMENTS[sym]
        text(c, f"{sym} · {name}", lx, ly, 30, lighten(rgb, 0.3), 255 * g, 800, "left", spacing=3)
    label(c, "HEAVIER AND HEAVIER", 820, 1030, WHITE, 26, 255 * smooth(prog(t, LAYER_T[2], LAYER_T[2] + 0.5)))


def iron_scene(c, t):
    hit = shake(drift_cam(t, IRON[0], BOOM, 0, 0, 0, 0, 1.0, 1.15), t, COLLAPSE + 0.35, 14, 4)
    space(c, t, hit, clouds=("dust",), a=0.6)
    off = smooth(prog(t, OFF_T, OFF_T + 0.6))
    col_k = in_cubic(prog(t, COLLAPSE, COLLAPSE + 0.4))
    _, rgb = ELEMENTS["Fe"]
    hit.push(c, 1.0)
    r = 150 * (1 - 0.82 * col_k)
    glow_rgb = mix(AMBER, (80, 40, 40), off)
    light(c, 0, -20, 420 * (1 - off * 0.7), glow_rgb, 160)
    c.drawCircle(0, -20, r, shaded(radial((-40, -60), r * 1.4, [lighten(rgb, 0.3 * (1 - off)), mix(rgb, (90, 60, 60), off), darken(rgb, 0.5)])))
    if r > 60:
        text(c, "Fe", 0, 10, 90 * r / 150, WHITE, 255, 800)
    n = 16
    for k in range(n):
        ang = k / n * 6.28
        d0 = lerp(480, r + 60, in_cubic(prog(t, OFF_T + 0.3, COLLAPSE + 0.3)))
        arrow(c, math.cos(ang) * (d0 + 200), -20 + math.sin(ang) * (d0 + 200), math.cos(ang) * d0, -20 + math.sin(ang) * d0, WHITE, 6, 220 * smooth(prog(t, OFF_T + 0.2, OFF_T + 0.6)), 20)
    if t > COLLAPSE + 0.35:
        light(c, 0, -20, 300, HOTWHITE, 255 * math.exp(-(t - COLLAPSE - 0.35) * 6), core=2)
    hit.pop(c)
    a = smooth(prog(t, OFF_T, OFF_T + 0.4))
    if a > 0:
        c.saveLayerAlpha(None, int(255 * a))
        tag(c, "FURNACE OFF", 960, 120, (255, 140, 120), 30)
        c.restore()
    a2 = smooth(prog(t, COLLAPSE - 0.6, COLLAPSE))
    if a2 > 0:
        c.saveLayerAlpha(None, int(255 * a2))
        tag(c, "LESS THAN A SECOND", 960, 960, (255, 140, 120), 30)
        c.restore()

    def path(tt):
        return 1640 + 20 * math.sin(tt), 300 + 15 * math.sin(tt * 1.3)
    orbi_on(c, t, path, 80, "wide" if t > OFF_T else "neutral", (-0.9, 0.5), -0.3, rim=(255, 140, 120))


def supernova(c, t):
    cam = shake(drift_cam(t, BOOM, REMNANT[1], 0, 0, 0, 0, 1.2, 0.95), t, BOOM, 26, 1.6)
    space(c, t, cam, clouds=("cloud",), a=0.6)
    k = prog(t, BOOM, BOOM + 6.5)
    cam.push(c, 0.9)
    # lingering remnant: turbulent fire shell that keeps growing after the blast
    u = out_cubic(prog(t, BOOM + 0.3, BOOM + 9.0))
    ra = smooth(prog(t, BOOM + 0.4, BOOM + 2.0))
    draw_texture(c, tex_fire(64), -160, -40, 0.25 + 0.75 * u, t * 3, 170 * ra, skia.BlendMode.kPlus)
    draw_texture(c, tex_ring(45), -160, -40, 0.3 + 0.8 * u, -t * 4, 150 * ra, skia.BlendMode.kPlus)
    shockwave(c, -160, -40, 820, t, k)
    # the dying star stays a blinding point: brighter than the galaxy beside it
    sn = 0.55 + 0.45 * math.exp(-max(0.0, t - BOOM) * 0.8)
    light(c, -160, -40, 240, HOTWHITE, 255 * sn * ra, core=2)
    spikes(c, -160, -40, 230 * sn, (220, 230, 255), 200 * ra)
    cam.pop(c)
    ga = smooth(prog(t, TM.word("G3", "galaxy") - 0.6, TM.word("G3", "galaxy")))
    if ga > 0:
        galaxy(c, 1560, 250, 190, t, 200 * ga)
        text(c, "A WHOLE GALAXY", 1560, 400, 20, WHITE, 200 * ga, 800, spacing=3)

    def path(tt):
        u = tt - BOOM
        blast = 1 - math.exp(-max(0.0, u) * 2.2)
        return 1200 + 520 * blast + 20 * math.sin(tt), 640 + 160 * blast - 60 * math.sin(math.pi * clamp(u / 1.4))
    expr = "wide" if t < BOOM + 2.2 else "squint"
    orbi_on(c, t, path, 90, expr, (-1, -0.2), -0.5 if t < BOOM + 2.2 else 0.3, rim=AMBER)
    c.drawPaint(add(HOTWHITE, 255 * math.exp(-max(0.0, t - BOOM) * 3.5)))
    c.drawRect(skia.Rect.MakeXYWH(0, 930, W, 150), shaded(linear((0, 930), (0, H), [(VOID, 0), (VOID, 220)])))
    label(c, "SUPERNOVA", 960, 990, AMBER, 46, 255 * smooth(prog(t, BOOM + 0.8, BOOM + 1.4)), sub="CAN BRIEFLY OUTSHINE A WHOLE GALAXY")


def remnants(c, t):
    space(c, t, Cam(0, 0, 1.0), clouds=(), teal=False)
    div = smooth(prog(t, BH_T - 0.4, BH_T + 0.4))
    c.drawLine(960, 80, 960, 80 + 920 * div, stroke(WHITE, 2, 60))
    ng = out_back(prog(t, NS_T, NS_T + 0.7), 1.2)
    nx = lerp(960, 480, div)
    if ng > 0:
        neutron_star(c, nx, 450, 22 * ng, t, beam=16)
        sg = out_back(prog(t, SPOON_T, SPOON_T + 0.6), 1.2)
        if sg > 0:
            teaspoon(c, nx - 60, 820, 90 * sg)
            text(c, "≈ 1,000,000,000 TONNES", nx + 120, 830, 22, BLUE_STAR, 255 * min(1, sg), 800, "left", spacing=2)
        label(c, "NEUTRON STAR", nx, 960, BLUE_STAR, 30, 255 * min(1, ng), sub="ABOUT THE SIZE OF A CITY")
    bg = out_back(prog(t, BH_T, BH_T + 0.9), 1.1)
    if bg > 0:
        black_hole(c, 1440, 470, 110 * bg, t)
        label(c, "BLACK HOLE", 1440, 960, AMBER, 30, 255 * min(1, bg), sub="IF THE CORE IS HEAVY ENOUGH")


def draw_frame(c, t):
    scenes(c, t, [((0.0, 0.01), IRON[1], onion_scene), (IRON, BOOM, iron_scene), ((BOOM, BOOM + 0.01), REMNANT[1], supernova),
                  (REMNANT, DURATION + 1, remnants)])
    chapter_title(c, t, 5, "A VIOLENT END", AMBER, 0.2, 2.5)
    fade(c, t, DURATION, 0.5, 0.6)


def sfx_events():
    ev = [(0.2, "swell_soft", 0.6), (VO["G1"] + 1.4, "slide", 0.6)] + [(x, "pop", 0.5) for x in LAYER_T]
    ev += [(IRON[0], "whoosh", 0.5), (OFF_T, "flicker", 0.8), (OFF_T + 0.3, "riser", 1.0), (COLLAPSE, "whoosh", 1.0), (COLLAPSE + 0.35, "boom", 0.8),
           (BOOM - 0.05, "boom", 1.0), (BOOM, "whoosh_long", 1.0), (BOOM + 0.1, "rumble", 1.0), (BOOM + 1.5, "rumble", 0.9),
           (REMNANT[0], "whoosh", 0.5), (NS_T, "shine", 0.6), (SPOON_T, "pop", 0.6), (BH_T, "boom", 0.6), (BH_T + 0.3, "riser", 0.4)]
    return ev


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 14, 19)), (IRON[0], 44, (0, 7, 12, 15, 18)), (OFF_T, 40, (0, 7)), (BOOM, 45, (0, 7, 12, 16, 19, 24)),
            (REMNANT[0], 43, (0, 7, 12, 15, 19))],
    plucks=[(VO["G1"], OFF_T), (REMNANT[1], DURATION)], bpm=96, rises=[(LAYER_T[2], LAYER_T[5])], drone=33,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
