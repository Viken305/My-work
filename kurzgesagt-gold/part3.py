"""Part 3: The lost gold. Gold drifts into the disk that forms the solar system; the young Earth is molten and the gold
sinks to the core; enough to coat the planet 4 metres deep (scale with people and a house).

  python3 render.py part3 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part3"
VO, _end = schedule(PART, first=0.3, gap=0.6)
DURATION = _end + 1.2
TM = Timing(PART, VO)

DISK = (0.0, VO["L2"] - 0.2)
MOLTEN_T = TM.word("L2", "molten") - 0.2
SINK_T = TM.word("L2", "sank") - 0.1
CORE_T = TM.word("L2", "into the core") - 0.1
COAT_T = VO["L3"] - 0.3
SCALE_T = TM.word("L3", "four metres") - 0.6
CX, CY = W / 2, 920
_rng = np.random.default_rng(12)
DROPS = [(float(a), float(d), float(s)) for a, d, s in zip(_rng.uniform(0, 6.28, 34), _rng.uniform(0.4, 0.93, 34), _rng.uniform(0, 1, 34))]

CAPS = Captions(TM, anchors={"L1": (W / 2, 330), "L2": (W / 2, 330), "L3": (W / 2, 330)},
                heroes={"CORE,": (W / 2, 1560, 170)},
                reacts={"SANK.": (lambda c, x, y, t, a, s: react_sank(c, x, y, t, a, s, "SANK"), W / 2, 1520, 130)})


def disk_scene(c, t):
    """Gold nuggets drift in and spiral into the protoplanetary disk; the young Earth forms and glows."""
    k = in_out(prog(t, 0.0, DISK[1]))
    space_bg(c, t, Cam(0, 0, lerp(1.0, 1.15, k)), warm=0.3)
    c.save()
    c.translate(CX, CY)
    c.scale(1, 0.38)
    for r_, a_ in ((620, 60), (480, 90), (340, 110), (220, 120)):
        c.drawCircle(0, 0, r_, stroke((255, 190, 120), 26, a_))
    c.restore()
    light(c, CX, CY, 260, (255, 220, 150), 230)
    c.drawCircle(CX, CY, 70, fill((255, 240, 200)))
    for i, (a, d, s) in enumerate(DROPS):
        u = (t * 0.08 + s) % 1.0
        rr = lerp(900, 120, prog(t, 0, DISK[1]) * 0.6 + u * 0.4)
        an = a + t * (0.6 + 300 / rr)
        x, y = CX + math.cos(an) * rr, CY + math.sin(an) * rr * 0.38
        gold_sphere(c, x, y, 7 + 5 * s, (255, 180, 120))
    ea = smooth(prog(t, DISK[1] - 2.5, DISK[1] - 1.0))
    if ea > 0:
        an = t * 0.5
        ex, ey = CX + math.cos(an) * 380, CY + math.sin(an) * 380 * 0.38
        light(c, ex, ey, 120, MAGMA, 200 * ea)
        c.drawCircle(ex, ey, 40 * ea, shaded(radial((ex - 12, ey - 12), 60, [(255, 200, 120), MAGMA, MAGMA_DEEP])))
    chip(c, "THE NEWBORN SOLAR SYSTEM", W / 2, 1500, GOLD, t, 1.0, DISK[1] - 0.3)


def core_scene(c, t):
    """Molten young Earth in cross-section; gold drops sink and pile up in the core."""
    k = in_out(prog(t, DISK[1], COAT_T))
    space_bg(c, t, Cam(0, 0, lerp(0.92, 1.05, k)))
    R = 430
    earth_section(c, CX, CY, R, t, molten=1.0, core_glow=0.4 + 0.6 * smooth(prog(t, CORE_T, CORE_T + 1.5)))
    for i in range(10):     # convection shimmer
        an = t * 0.4 + i * 0.63
        c.drawCircle(CX + math.cos(an) * R * 0.75, CY + math.sin(an) * R * 0.75, 40, fill((255, 140, 60), 40))
    for i, (a, d, s) in enumerate(DROPS):
        u = in_cubic(prog(t, SINK_T - 0.6 + s * 1.4, SINK_T + 1.6 + s * 1.4))
        dd = lerp(d, 0.16 + 0.12 * s, u)
        x, y = CX + math.cos(a) * R * dd, CY + math.sin(a) * R * dd
        if 0.02 < u < 0.98:
            tx, ty = CX + math.cos(a) * R * (dd + 0.12), CY + math.sin(a) * R * (dd + 0.12)
            c.drawLine(x, y, tx, ty, stroke(GOLD_HI, 4, 150))
        c.drawCircle(x, y, 17, fill((40, 10, 10), 120))
        gold_sphere(c, x, y, 11 + 4 * s, (255, 120, 60))
    if t > CORE_T:
        g = smooth(prog(t, CORE_T, CORE_T + 1.2))
        gold_sphere(c, CX, CY, R * 0.3 * g, (255, 150, 80), 255 * g)
        sparkle4(c, CX + 60, CY - 70, 30 * g, 255 * g)
    chip(c, "MOLTEN YOUNG EARTH", W / 2, 1560, (255, 170, 120), t, MOLTEN_T, SINK_T - 0.1)
    chip(c, "STILL IN THE CORE TODAY", W / 2, 1500, GOLD, t, CORE_T + 1.2, COAT_T)


def coat_scene(c, t):
    """The planet wrapped in a gold shell, then a ground-level slice: a 4 m gold layer next to people and a house."""
    k = in_out(prog(t, COAT_T, SCALE_T + 0.4))
    if t < SCALE_T + 0.4:
        space_bg(c, t)
        r = 380
        mini_earth(c, CX, CY, r, t, gold_k=smooth(prog(t, COAT_T + 0.3, COAT_T + 1.8)))
        light(c, CX, CY, r * 1.4, GOLD, 35 * smooth(prog(t, COAT_T + 0.3, COAT_T + 1.8)))
    else:
        u = smooth(prog(t, SCALE_T + 0.4, SCALE_T + 1.0))
        c.drawPaint(shaded(linear((0, 0), (0, H), [(60, 110, 190), (150, 190, 230)])))
        gy = 1300
        c.drawRect(skia.Rect.MakeXYWH(0, gy, W, H - gy), fill((110, 90, 70)))
        layer_h = 400 * out_back(u, 1.2)          # 4 m -> 400 px (1 m = 100 px): a slab of the layer, cut away
        sx0, sx1 = 60, 520
        c.drawRect(skia.Rect.MakeXYWH(sx0, gy - layer_h, sx1 - sx0, layer_h), shaded(linear((0, gy - layer_h), (0, gy), [GOLD_HI, GOLD, GOLD_MID])))
        side = skia.Path()
        side.moveTo(sx1, gy - layer_h)
        side.lineTo(sx1 + 70, gy - layer_h - 40)
        side.lineTo(sx1 + 70, gy - 40)
        side.lineTo(sx1, gy)
        side.close()
        c.drawPath(side, fill(GOLD_DEEP))
        top = skia.Path()
        top.moveTo(sx0, gy - layer_h)
        top.lineTo(sx0 + 70, gy - layer_h - 40)
        top.lineTo(sx1 + 70, gy - layer_h - 40)
        top.lineTo(sx1, gy - layer_h)
        top.close()
        c.drawPath(top, fill(GOLD_HI))
        for i in range(4):
            sparkle4(c, sx0 + 60 + i * 110, gy - layer_h + 50 + 50 * (i % 2), 20, 220 * u)
        for x in (680, 740):     # two people (1.8 m) for scale
            c.drawCircle(x, gy - 160, 18, fill((60, 50, 70)))
            c.drawRRect(rrect(x - 16, gy - 140, 32, 140, 14), fill((60, 50, 70)))
        hx = 820                 # small house (~3.5 m to the eaves)
        c.drawRect(skia.Rect.MakeXYWH(hx, gy - 280, 200, 280), fill((230, 220, 210)))
        c.drawPath(poly([(hx - 15, gy - 280), (hx + 100, gy - 380), (hx + 215, gy - 280)]), fill((180, 80, 70)))
        c.drawRect(skia.Rect.MakeXYWH(hx + 80, gy - 110, 40, 110), fill((120, 80, 60)))
        c.drawLine(30, gy, 30, gy - layer_h, stroke(WHITE, 5))
        c.drawLine(15, gy - layer_h, 45, gy - layer_h, stroke(WHITE, 5))
        gold_word(c, "4 M", 290, gy - layer_h - 90, 110, 255 * u, 1.0, t)
        chip(c, "OVER THE WHOLE PLANET", W / 2, 1560, GOLD, t, SCALE_T + 1.0)


def draw_frame(c, t):
    if t < DISK[1]:
        disk_scene(c, t)
    elif t < COAT_T:
        core_scene(c, t)
    else:
        coat_scene(c, t)
    for t0 in (DISK[1], COAT_T, SCALE_T + 0.4):     # flash transitions
        if t0 - 0.12 < t < t0 + 0.25:
            c.drawPaint(fill(WHITE, 200 * (1 - abs(t - t0 - 0.05) / 0.2)))
    CAPS.draw(c, t)
    fade(c, t, DURATION, 0.25, 0.25)


def sfx_events():
    return [(0.1, "swell_soft", 0.6), (1.0, "shimmer", 0.5), (DISK[1], "whoosh", 0.8), (MOLTEN_T, "rumble", 0.8), (SINK_T, "slide", 0.7)] + \
           [(SINK_T + 0.15 * i, "pop", 0.3) for i in range(6)] + [(CORE_T + 0.6, "boom", 0.5), (CORE_T + 0.65, "chime", 0.7), (COAT_T, "whoosh", 0.8),
                                                                 (COAT_T + 1.0, "shine", 0.8), (SCALE_T + 0.4, "whoosh", 0.7), (SCALE_T + 0.6, "ding", 0.9)]


MUSIC = dict(chords=[(0.0, 48, (0, 7, 12, 14, 19)), (DISK[1], 45, (0, 7, 12, 15, 19)), (CORE_T, 43, (0, 7, 12, 15, 18)), (COAT_T, 48, (0, 7, 12, 16, 19))],
             plucks=[(0.3, DURATION)], bpm=100, rises=[(SINK_T, CORE_T), (COAT_T, SCALE_T)], drone=36)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
