"""Part 7: Chapter 6, Star Stuff. Elements scatter, neutron stars collide (gold), a new solar system, you.

  python3 render.py part7 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part7"
VO, _end = schedule(PART, first=2.8, gap=0.8, extra={"X4": 0.4})
DURATION = _end + 4.6
TM = Timing(PART, VO)

SCATTER_T = TM.word("X1", "scatters") - 0.3
MERGE = (VO["X2"] - 0.5, VO["X2"])
COLLIDE = TM.word("X2", "collide") + 0.5
GOLD_T = TM.word("X2", "gold") - 0.3
SYSTEM = (VO["X3"] - 0.5, VO["X3"])
CLOUD_T = TM.word("X3", "new clouds") - 0.2
STARS_T = TM.word("X3", "new stars") - 0.2
PLANETS_T = TM.word("X3", "new planets") - 0.2
OURS_T = TM.word("X3", "our solar system") - 0.3
HILL = (VO["X4"] - 0.6, VO["X4"])
LOOK_T = TM.word("X4", "look up") - 0.2
MADE_T = TM.word("X4", "made of them") - 0.2
END_T = _end + 0.4

CHIPS = ["C", "O", "Si", "Fe", "Ca", "Au"]
_rng = np.random.default_rng(77)
DEBRIS = [(float(a), float(s), int(k)) for a, s, k in zip(_rng.uniform(-1.1, 1.1, 120), _rng.uniform(0.3, 1.0, 120), _rng.integers(0, 5, 120))]
PLANETS = [(150, 9, (180, 160, 150)), (220, 13, (230, 190, 120)), (300, 14, (80, 150, 255)), (380, 11, (230, 120, 80)), (560, 34, (220, 180, 140))]


def scatter(c, t):
    cam = drift_cam(t, 0, MERGE[1], -120, 260, 0, 0, 1.1, 0.95)
    space(c, t, cam, clouds=("cloud", "teal"), a=0.6)
    cam.push(c, 0.9)
    ox, oy = -520, 0
    draw_texture(c, tex_ring(43), ox, oy, 0.75 + 0.03 * t, t * 2, 210, skia.BlendMode.kPlus)
    draw_texture(c, tex_fire(65), ox, oy, 0.5 + 0.02 * t, -t * 3, 90, skia.BlendMode.kPlus)
    neutron_star(c, ox, oy, 9, t, beam=10)
    k = prog(t, SCATTER_T - 1.0, SCATTER_T + 7.0)
    # glittering debris streaming outward
    for a, s, ci in DEBRIS:
        u = (k * 1.6 * s + s * 0.37) % 1.0
        d = 120 + 1500 * u
        x, y = ox + math.cos(a) * d, oy + math.sin(a) * d * 0.7
        cc = ELEMENTS[CHIPS[ci]][1]
        c.drawCircle(x, y, 2.5 + 2 * s, add(cc, 200 * math.sin(math.pi * u)))
    # named elements riding the flow, each with a soft trail
    for i, sym in enumerate(CHIPS[:5]):
        g = smooth(prog(t, SCATTER_T + i * 0.35, SCATTER_T + i * 0.35 + 0.6))
        if g <= 0:
            continue
        u = out_cubic(prog(t, SCATTER_T + i * 0.35, SCATTER_T + i * 0.35 + 4.5))
        ang = -0.75 + i * 0.37
        d = 160 + 900 * u
        x, y = ox + math.cos(ang) * d, oy + math.sin(ang) * d * 0.8 + 30 * math.sin(t + i)
        rgb = ELEMENTS[sym][1]
        p = skia.Paint(AntiAlias=True, Shader=linear((ox, oy), (x, y), [(rgb, 0), (rgb, 150 * g)]), Style=skia.Paint.kStroke_Style, StrokeWidth=4)
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3))
        c.drawLine(ox + math.cos(ang) * 120, oy + math.sin(ang) * 96, x, y, p)
        element_chip(c, x, y, 130 * (0.6 + 0.4 * g), sym, 255 * g)
    cam.pop(c)

    def path(tt):
        u = out_cubic(prog(tt, SCATTER_T, SCATTER_T + 5.0))
        return lerp(1250, 1580, u) + 20 * math.sin(tt), lerp(820, 760, u) + 15 * math.sin(tt * 1.3)
    orbi_on(c, t, path, 80, "happy" if t > SCATTER_T + 1 else "neutral", (-0.7, -0.4), 0.6, rim=TEAL)
    label(c, "SCATTERED INTO SPACE", 960, 1010, WHITE, 28, 255 * smooth(prog(t, SCATTER_T + 0.6, SCATTER_T + 1.2)))


def merger(c, t):
    cam = shake(drift_cam(t, MERGE[0], SYSTEM[1], 0, 0, 0, 0, 0.95, 1.12), t, COLLIDE, 18, 2.0)
    space(c, t, cam, clouds=("teal",), a=0.5)
    cam.push(c, 1.0)
    cx, cy = -300, 0
    pre = clamp((COLLIDE - t) / (COLLIDE - MERGE[0]))
    if t < COLLIDE:
        # inspiral: orbit shrinks and speeds up, ripples of spacetime spread out
        rr = 30 + 330 * pre ** 0.8
        ph = 18 * (1 - pre) ** 0.6 * 3 + t * 0.5
        for ring in range(5):
            rk = ((t * 0.9 + ring / 5) % 1.0)
            c.drawOval(skia.Rect.MakeXYWH(cx - 900 * rk, cy - 380 * rk, 1800 * rk, 760 * rk), stroke(VIOLET2, 2, 110 * (1 - rk) * (1 - pre * 0.5)))
        for s in (0, math.pi):
            x, y = cx + math.cos(ph + s) * rr, cy + math.sin(ph + s) * rr * 0.42
            neutron_star(c, x, y, 16, t, beam=12)
    else:
        u = t - COLLIDE
        light(c, cx, cy, 600 * (1 - math.exp(-u * 2)) + 100, (255, 190, 110), 230 * math.exp(-u * 0.35))
        draw_texture(c, tex_fire(66), cx, cy, 0.2 + 0.6 * out_cubic(prog(u, 0, 5)), u * 6, 220 * math.exp(-u * 0.25), skia.BlendMode.kPlus)
        shockwave(c, cx, cy, 700, t, prog(u, 0, 4.5))
        rng = np.random.default_rng(9)
        for i in range(40):  # golden sparks flung out of the kilonova
            ang = rng.uniform(0, 6.28)
            d = 80 + 700 * out_cubic(prog(u, 0, 3.5)) * rng.uniform(0.4, 1.0)
            c.drawCircle(cx + math.cos(ang) * d, cy + math.sin(ang) * d * 0.7, 3 + 3 * rng.random(), add((255, 210, 90), 230 * math.exp(-u * 0.4)))
    cam.pop(c)
    c.drawPaint(add(HOTWHITE, 255 * math.exp(-max(0.0, t - COLLIDE) * 4) * (t > COLLIDE)))
    label(c, "NEUTRON STARS COLLIDE", 660, 980, BLUE_STAR, 28, 255 * smooth(prog(t, MERGE[1], MERGE[1] + 0.6)) * (1 - smooth(prog(t, GOLD_T - 0.3, GOLD_T))))
    g = out_back(prog(t, GOLD_T, GOLD_T + 0.8), 1.3)
    if g > 0:
        sh = 0.5 + 0.5 * math.sin(t * 2.5)
        element_chip(c, 1420, 460, 250 * g, "Au", 255 * min(1, g), glow_a=170 + 60 * sh)
        sweep = prog(t, GOLD_T + 0.6, GOLD_T + 1.6)
        if 0 < sweep < 1:
            light(c, lerp(1300, 1540, sweep), lerp(340, 580, sweep), 90, HOTWHITE, 180 * math.sin(math.pi * sweep))
        label(c, "MUCH OF EARTH'S GOLD", 1420, 760, (255, 210, 90), 30, 255 * min(1, g), sub="LIKELY MADE THIS WAY")


def system(c, t):
    zoom = in_out(prog(t, OURS_T + 1.0, HILL[0] + 0.3))
    ex, ey = None, None
    cam = drift_cam(t, SYSTEM[0], OURS_T + 1.0, 0, 0, 0, 0, 1.0, 1.1)
    space(c, t, cam, clouds=("cloud",), a=0.6)
    cam.push(c, 1.0)
    # earth's position (orbit) for the camera push
    e_ang = 0.9 + t * 0.12
    ex, ey = math.cos(e_ang) * 300 * 1.6, math.sin(e_ang) * 300 * 0.42
    c.scale(1 + 7 * zoom ** 2, 1 + 7 * zoom ** 2)
    c.translate(lerp(0, -ex, zoom), lerp(0, -ey, zoom))
    # a fresh cloud seeded with heavy elements gathers
    gk = smooth(prog(t, CLOUD_T, STARS_T + 1.0))
    draw_texture(c, tex_cloud(16), 0, 0, lerp(1.2, 0.45, gk), t * 6 * gk, 255 * (1 - 0.6 * smooth(prog(t, PLANETS_T, OURS_T))), skia.BlendMode.kPlus)
    for i, (a, s, ci) in enumerate(DEBRIS[:60]):
        rr = (700 - 520 * gk) * s
        aa = a * 3 + t * (0.3 + gk) * 300 / max(rr, 40)
        c.drawCircle(math.cos(aa) * rr, math.sin(aa) * rr * lerp(1.0, 0.42, gk), 4.0, add(ELEMENTS[CHIPS[ci]][1], 230 * (1 - smooth(prog(t, PLANETS_T, OURS_T + 1.0)))))
    dk = smooth(prog(t, STARS_T, PLANETS_T + 0.6))
    if dk > 0:
        disk(c, 0, 0, 40, 620, 0.42, t, 220 * dk * (1 - smooth(prog(t, OURS_T, OURS_T + 2))), "back")
        star(c, 0, 0, 70 * out_back(prog(t, STARS_T, STARS_T + 1.0), 1.2), t, SOLAR, 0.8, a=255 * (1 - smooth(prog(zoom, 0.05, 0.4))))
        disk(c, 0, 0, 40, 620, 0.42, t, 220 * dk * (1 - smooth(prog(t, OURS_T, OURS_T + 2))), "front")
    pk = smooth(prog(t, PLANETS_T, PLANETS_T + 1.2))
    if pk > 0:
        for k, (r, pr, rgb) in enumerate(PLANETS):
            c.drawOval(skia.Rect.MakeXYWH(-r * 1.6, -r * 0.42, r * 3.2, r * 0.84), stroke(WHITE, 1.2 / (1 + 7 * zoom ** 2), 40 * pk))
            ang = 0.9 + t * 0.12 if k == 2 else 0.4 + k * 1.7 + t * 0.12 * (300 / r) ** 1.5
            px, py = math.cos(ang) * r * 1.6, math.sin(ang) * r * 0.42
            if k == 2:
                earth(c, px, py, pr * pk, t)
            else:
                light(c, px, py, pr * 2.5, rgb, 90 * pk)
                c.drawCircle(px, py, pr * pk, shaded(radial((px - pr * 0.4, py - pr * 0.4), pr * 1.6, [lighten(rgb, 0.3), darken(rgb, 0.4)])))
    cam.pop(c)

    def path(tt):
        return 1560 + 30 * math.sin(tt * 0.7), 300 + 20 * math.sin(tt)
    orbi_on(c, t, path, 80, "wide" if t > PLANETS_T else "neutral", (-0.8, 0.4), 0.4, rim=SOLAR, a=255 * (1 - zoom))
    la = smooth(prog(t, OURS_T, OURS_T + 0.6)) * (1 - smooth(prog(t, HILL[0] - 0.6, HILL[0])))
    label(c, "OUR SOLAR SYSTEM", 960, 980, (120, 180, 255), 32, 255 * la, sub="ABOUT 4.6 BILLION YEARS AGO")


def hill(c, t):
    rise = in_out(prog(t, HILL[0], LOOK_T + 2.5))
    c.drawPaint(shaded(linear((0, 0), (0, H), [VOID, (30, 24, 70)])))
    sky = Cam(0, lerp(-260, 0, rise), 1.0)
    SF2.draw(c, t, sky, 1.0)
    SF.draw(c, t, sky, 0.6)
    c.save()
    c.translate(0, lerp(-200, 0, rise))
    c.rotate(-18, W / 2, H / 2)
    draw_texture(c, tex_cloud(13), 960, 420, 1.6, t * 0.3, 160, skia.BlendMode.kPlus)
    draw_texture(c, tex_teal(33), 1200, 380, 1.2, -t * 0.4, 90, skia.BlendMode.kPlus)
    c.restore()
    galaxy(c, 1500, 220 + lerp(-200, 0, rise), 180, t, 130)
    # shooting star
    ss = prog(t, MADE_T - 2.0, MADE_T - 1.2)
    if 0 < ss < 1:
        x, y = lerp(500, 1100, ss), lerp(120, 300, ss)
        p = skia.Paint(AntiAlias=True, Shader=linear((x - 160, y - 48), (x, y), [(WHITE, 0), (WHITE, 230)]), Style=skia.Paint.kStroke_Style, StrokeWidth=3)
        c.drawLine(x - 160, y - 48, x, y, p)
    c.save()
    c.translate(0, lerp(300, 0, rise))
    hill_p = skia.Path()
    hill_p.moveTo(-20, H)
    hill_p.cubicTo(400, 800, 1200, 760, W + 20, 880)
    hill_p.lineTo(W + 20, H)
    hill_p.close()
    c.drawPath(hill_p, fill((8, 8, 20)))
    glow = SOLAR if t > MADE_T else None
    human(c, 760, 880, 260, glow_rgb=glow)
    if t > MADE_T:  # starlight sparkling inside the person
        light(c, 760, 740, 160, SOLAR, 120 * smooth(prog(t, MADE_T, MADE_T + 1.0)))
    c.restore()

    def path(tt):
        land = out_cubic(prog(tt, HILL[0], LOOK_T))
        return lerp(1300, 980, land) + 10 * math.sin(tt * 0.8), lerp(420, 760, land) + 8 * math.sin(tt * 1.4) + lerp(300, 0, in_out(prog(tt, HILL[0], LOOK_T + 2.5)))
    expr = "happy" if t > MADE_T else "neutral"
    orbi_on(c, t, path, 60, expr, (-0.3, -0.8), 0.6, rim=TEAL)
    ma = smooth(prog(t, MADE_T, MADE_T + 0.8)) * (1 - smooth(prog(t, END_T, END_T + 0.6)))
    tr = lerp(24, 10, out_cubic(prog(t, MADE_T, MADE_T + 2.0)))
    text(c, "YOU'RE MADE OF THEM", 960, 1020, 44, WHITE, 245 * ma, 800, spacing=tr)


def end_card(c, t):
    k = smooth(prog(t, END_T, END_T + 0.8))
    c.drawPaint(fill(VOID, 200 * k))
    light(c, W / 2, H / 2, 700, SOLAR, 60 * k)
    label(c, "YOU ARE MADE OF", 960, 420, WHITE, 40, 255 * k)
    tr = lerp(36, 14, out_cubic(prog(t, END_T + 0.2, END_T + 2.0)))
    text(c, "DEAD STARS", 960, 560, 130, SOLAR, 255 * smooth(prog(t, END_T + 0.3, END_T + 0.9)), 800, spacing=tr)
    sw = prog(t, END_T + 0.6, END_T + 2.2)
    if 0 < sw < 1:
        light(c, lerp(560, 1360, in_out(sw)), 520, 220, SOLAR, 150 * math.sin(math.pi * sw))


def draw_frame(c, t):
    scenes(c, t, [((0.0, 0.01), MERGE[1], scatter), (MERGE, SYSTEM[1], merger), (SYSTEM, HILL[1], system), (HILL, DURATION + 1, hill)])
    if t > END_T:
        end_card(c, t)
    chapter_title(c, t, 6, "STAR STUFF", TEAL, 0.2, 2.5)
    fade(c, t, DURATION, 0.5, 1.0)


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (SCATTER_T, "whoosh_long", 0.6), (SCATTER_T + 0.2, "shimmer", 0.6)] + \
           [(SCATTER_T + i * 0.35, "pop", 0.4) for i in range(5)] + \
           [(MERGE[0], "whoosh", 0.5), (COLLIDE - 2.5, "riser", 0.9), (COLLIDE, "boom", 1.0), (COLLIDE + 0.1, "rumble", 0.8),
            (GOLD_T, "chime", 0.8), (GOLD_T + 0.6, "shine", 0.6), (SYSTEM[0], "whoosh_long", 0.6), (STARS_T, "shine", 0.6),
            (PLANETS_T, "shimmer", 0.6), (OURS_T + 1.0, "riser", 0.5), (HILL[0], "swell_soft", 0.8), (MADE_T - 2.0, "shimmer", 0.5),
            (MADE_T, "chime", 0.7), (END_T + 0.3, "shine", 0.7), (END_T + 0.4, "swell_soft", 0.9)]


MUSIC = dict(
    chords=[(0.0, 48, (0, 7, 12, 16, 19)), (MERGE[0], 44, (0, 7, 12, 15, 19)), (COLLIDE, 46, (0, 7, 12, 16, 19, 24)),
            (SYSTEM[0], 41, (0, 7, 12, 16, 19)), (HILL[0], 43, (0, 7, 12, 14, 19)), (MADE_T, 48, (0, 7, 12, 16, 19, 24))],
    plucks=[(VO["X1"], COLLIDE - 2.5), (GOLD_T, HILL[0])], bpm=90, rises=[(COLLIDE - 2.5, COLLIDE), (OURS_T, HILL[0])], drone=33,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
