"""Part 4, the discoveries: at ~6.7 km a microscope opens on 2-billion-year-old plankton fossils; deeper, water seeps
out of the crystals of the rock and is trapped; the mud coming up boils with hydrogen.

  python3 render.py part4 [--still 1,5]
"""
from film import *  # noqa: F401,F403

PART = "part4"
VO, _end = schedule(PART, first=0.3, gap=0.55)
TM = Timing(PART, VO)
DURATION = _end + 1.2

ZOOM_T = 0.0
FOSSIL_T = TM.word("C1", "fossils") - 0.3
SPECIES_T = TM.word("C1", "twenty") - 0.1
AGE_T = TM.word("C1", "two billion") - 0.1
WATER_T = VO["C2"] - 0.35
SQUEEZE_T = TM.word("C2", "squeezed") - 0.2
TRAP_T = TM.word("C2", "trapped") - 0.15
MUD_T = VO["C3"] - 0.35
BOIL_T = TM.word("C3", "boiling") - 0.15
H2_T = TM.word("C3", "hydrogen") - 0.15

CAPS = Captions(TM, anchors={"C1": (W / 2, 1400), "C2": (W / 2, 1400), "C3": (W / 2, 1400)},
                emph={"fossils", "plankton", "billion", "water", "rock", "boiling", "hydrogen"})
SPECIES = Counter("24", 120, "mono_bold")
DUST = Dust(60, 9)
_r = np.random.default_rng(12)
FOSSILS = [(float(x), float(y), float(s), int(k)) for x, y, s, k in zip(_r.uniform(-300, 300, 9), _r.uniform(-300, 300, 9),
                                                                         _r.uniform(36, 90, 9), _r.integers(0, 3, 9))]
GRAINS = [(float(x), float(y)) for x, y in zip(_r.uniform(80, 1000, 34), _r.uniform(300, 1450, 34))]
BUBBLES = [(float(x), float(s), float(p)) for x, s, p in zip(_r.uniform(-0.42, 0.42, 46), _r.uniform(8, 34, 46), _r.random(46))]


def descent(c, t):
    """From the full view down to ~6.7 km, close on the hole."""
    k = in_out(prog(t, 0.0, FOSSIL_T + 0.2))
    ppm = math.exp(lerp(math.log(FULL["ppm"]), math.log(2.2), k))
    fk = smooth(clamp((ppm - FULL["ppm"]) / (0.6 - FULL["ppm"])))
    cam = Section(lerp(FULL["d"], 6700, fk), ppm, cy=lerp(FULL["cy"], 900, fk))
    void(c, t, warm=0.2)
    strata(c, cam, t, heat=1.0, labels=1 - fk)
    hole(c, cam, 12262, t, glow=0.9, bit=False)
    if fk > 0.3:
        y = cam.sy(6700)
        c.drawLine(W / 2 + 30, y, W / 2 + 140, y, stroke(EMBER, 2, 230 * fk))
    gauge(c, cam.d if fk > 0.5 else 0, t, smooth(prog(fk, 0.5, 1.0)))
    return cam


def microscope(c, t, a):
    """Iris opens on drifting line-art microfossils."""
    if a <= 0.01:
        return
    cx, cy, R_ = W / 2, 860, 360 * out_cubic(a)
    c.drawCircle(cx, cy, R_ + 30, paint(VOID, 220, 30))
    c.save()
    path = skia.Path()
    path.addCircle(cx, cy, R_)
    c.clipPath(path, doAntiAlias=True)
    c.drawPaint(fillp((16, 14, 12)))
    light(c, cx - 80, cy - 100, 420, (110, 80, 50), 150)
    for i in range(140):                                   # sediment grains in the field of view
        x = cx + (hsh(i, 1) - 0.5) * 760
        y = cy + (hsh(i, 2) - 0.5) * 760 + 6 * math.sin(t * 0.3 + i)
        c.drawCircle(x, y, 1.5 + 4 * hsh(i, 3), fillp((90, 74, 60), 120))
    for i, (x, y, s, kind) in enumerate(FOSSILS):
        fa = smooth(prog(t, FOSSIL_T + 0.2 + i * 0.12, FOSSIL_T + 0.6 + i * 0.12))
        dx, dy = 10 * math.sin(t * 0.4 + i), 8 * math.cos(t * 0.35 + i)
        plankton(c, cx + x + dx, cy + y + dy, s, kind, t, 255 * fa, (236, 214, 180))
        light(c, cx + x + dx, cy + y + dy, s * 1.6, (255, 150, 80), 40 * fa)
    c.restore()
    c.drawCircle(cx, cy, R_, stroke(PAPER, 3, 230 * a))
    for i in range(60):                                   # reticle ticks
        an = i / 60 * 6.283
        L = 18 if i % 5 == 0 else 8
        c.drawLine(cx + math.cos(an) * R_, cy + math.sin(an) * R_, cx + math.cos(an) * (R_ - L), cy + math.sin(an) * (R_ - L), stroke(PAPER, 1.4, 180 * a))
    label(c, "6,700 m · MICROFOSSILS", cx, cy - R_ - 34, 24, "mono", ASH, 220 * a, "center", tracking=0.15)


CELL = 130
_g = np.random.default_rng(31)
NX, NY = W // CELL + 3, H // CELL + 3
VERTS = np.stack(np.meshgrid(np.arange(NX) * CELL - CELL, np.arange(NY) * CELL - CELL), -1).astype(float)
VERTS += _g.uniform(-42, 42, VERTS.shape)


def crystals(c, t):
    """Deep rock as a mosaic of interlocking crystal grains; water beads out along the grain boundaries and gathers
    in a sealed pocket."""
    zoom = lerp(1.0, 1.08, prog(t, WATER_T, MUD_T))
    c.save()
    c.translate(W / 2, 860)
    c.scale(zoom, zoom)
    c.translate(-W / 2, -860)
    c.drawPaint(fillp((20, 19, 20)))
    for j in range(NY - 1):
        for i in range(NX - 1):
            q = [VERTS[j, i], VERTS[j, i + 1], VERTS[j + 1, i + 1], VERTS[j + 1, i]]
            tris = [q] if hsh(i, j) < 0.5 else [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]
            for k, poly_ in enumerate(tris):
                p = path_of([tuple(v) for v in poly_], True)
                tone = hsh(i, j, k, 3)
                c.drawPath(p, fillp(mix((40, 37, 37), (78, 70, 64), tone)))
                cx_ = sum(v[0] for v in poly_) / len(poly_)
                cy_ = sum(v[1] for v in poly_) / len(poly_)
                for m in range(2):                        # cleavage lines inside the grain
                    off = (m - 0.5) * 30
                    c.drawLine(cx_ - 26 + off, cy_ - 30, cx_ + 10 + off, cy_ + 30, stroke((120, 110, 102), 1, 50 + 40 * tone))
                c.drawPath(p, stroke((14, 13, 14), 2.5, 255))
                c.drawPath(p, stroke((130, 120, 112), 1.0, 90))
    light(c, W / 2 - 260, 500, 700, (90, 110, 140), 60)
    sq = prog(t, SQUEEZE_T - 0.6, SQUEEZE_T + 1.8)
    ta = smooth(prog(t, TRAP_T - 0.6, TRAP_T))
    pocket = (W / 2, 860)
    if sq > 0:                                            # the pocket opens: a dark cavity that fills with water
        pk = out_cubic(clamp(sq * 1.4))
        c.drawOval(skia.Rect.MakeXYWH(pocket[0] - 170 * pk, pocket[1] - 95 * pk, 340 * pk, 190 * pk), fillp((8, 10, 14)))
        lvl = clamp(sq * 1.1)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(0, pocket[1] + 95 * pk - 190 * pk * lvl, W, H))
        c.drawOval(skia.Rect.MakeXYWH(pocket[0] - 170 * pk, pocket[1] - 95 * pk, 340 * pk, 190 * pk), grad_v(pocket[1] - 95, pocket[1] + 95, (70, 110, 150), (20, 40, 70), 230, 240))
        c.restore()
        c.drawOval(skia.Rect.MakeXYWH(pocket[0] - 170 * pk, pocket[1] - 95 * pk, 340 * pk, 190 * pk), stroke(STEEL, 2.5, 200 * pk))
    for j in range(1, NY - 2):                            # droplets bead on the boundaries, then run to the pocket
        for i in range(1, NX - 2):
            if hsh(i, j, 11) > 0.55:
                continue
            v = VERTS[j, i]
            t0 = WATER_T + 0.4 + hsh(i, j, 12) * 2.2
            a = smooth(prog(t, t0, t0 + 0.4))
            if a <= 0:
                continue
            u = in_out(clamp((sq - hsh(i, j, 13) * 0.4) / 0.6))
            x = lerp(v[0], pocket[0] + (hsh(i, j, 14) - 0.5) * 200, u)
            y = lerp(v[1], pocket[1] + (hsh(i, j, 15) - 0.5) * 90, u)
            r = (5 + 5 * hsh(i, j, 16)) * (1 - 0.6 * u)
            al = 230 * a * (1 - smooth(prog(u, 0.85, 1.0)))
            c.drawCircle(x, y, r, fillp(STEEL, al))
            c.drawCircle(x - r * 0.3, y - r * 0.3, r * 0.32, fillp((235, 245, 255), al))
    c.restore()
    if ta > 0:
        p = stroke(PAPER, 2, 200 * ta)
        p.setPathEffect(skia.DashPathEffect.Make([10, 10], t * 20))
        c.drawOval(skia.Rect.MakeXYWH(W / 2 - 210, 860 - 125, 420, 250), p)
        label(c, "TRAPPED · NO WAY OUT", W / 2, 860 + 175, 26, "mono", STEEL, 230 * ta, "center", tracking=0.15)
    label(c, "BELOW 7 KM", 72, 320, 24, "mono", ASH, 220 * smooth(prog(t, WATER_T, WATER_T + 0.4)), tracking=0.2)
    label(c, "H₂O", 72, 380, 44, "serif_up", STEEL, 255 * smooth(prog(t, WATER_T + 0.3, WATER_T + 0.8)))


def mud(c, t):
    """Inside the drill pipe: mud rushing up, bubbles of hydrogen, boiling."""
    x0, x1 = 230, 850
    cam = Section(9000 + (t - MUD_T) * 40, 2.0)           # rock around the pipe, drifting down as the mud rises
    strata(c, cam, t, heat=1.0, labels=0, sky=False)
    c.drawPaint(fillp(VOID, 90))
    c.drawRect(skia.Rect.MakeLTRB(x0, -10, x1, H + 10), grad_v(0, H, (70, 48, 34), (44, 30, 22)))
    for i in range(18):                                   # slow swirls in the mud
        x = x0 + hsh(i, 5) * (x1 - x0)
        y = (hsh(i, 6) * H - t * 320 * (0.5 + hsh(i, 7))) % (H + 400) - 200
        c.drawOval(skia.Rect.MakeXYWH(x - 90, y - 160, 180, 320), paint((96, 66, 46), 70, 30))
    for i in range(40):                                   # mud streaks flowing up
        x = x0 + hsh(i, 1) * (x1 - x0)
        y = (hsh(i, 2) * H - t * 600 * (0.6 + hsh(i, 3))) % (H + 300) - 150
        c.drawLine(x, y, x + 6 * math.sin(i), y + 140, stroke((110, 80, 58), 3, 90))
    boil = smooth(prog(t, BOIL_T - 0.3, BOIL_T + 0.6))
    for i, (bx, s, ph) in enumerate(BUBBLES):
        sp = 260 + 420 * hsh(i, 4)
        y = H + 60 - ((t - MUD_T) * sp + ph * H) % (H + 200)
        x = W / 2 + bx * (x1 - x0) + 12 * math.sin(t * 3 + i)
        r = s * (0.6 + 0.8 * boil)
        if boil * 46 < i:
            continue
        c.drawCircle(x, y, r, stroke((230, 200, 170), 2, 220))
        c.drawCircle(x - r * 0.35, y - r * 0.35, r * 0.22, fillp((255, 240, 220), 200))
        if i % 6 == 0 and t > H2_T:
            label(c, "H₂", x + r + 6, y + 8, 26, "mono_bold", EMBER, 255 * smooth(prog(t, H2_T, H2_T + 0.3)))
    for side in (x0, x1):                                 # pipe walls
        c.drawRect(skia.Rect.MakeLTRB(side - 18, -10, side + 18, H + 10), grad_v(0, H, (60, 58, 60), (30, 28, 30)))
        c.drawLine(side, -10, side, H + 10, stroke((150, 140, 130), 2, 160))
    light(c, W / 2, H + 100, 900, (255, 100, 40), 120 * boil)
    ha = smooth(prog(t, H2_T, H2_T + 0.4))
    if ha > 0:
        c.drawRect(skia.Rect.MakeXYWH(0, 520, W, 360), paint(VOID, 140 * ha, 50))
        reveal(c, "H₂", W / 2, 780, 260, t, H2_T, "serif", EMBER, 255, "center", stagger=0.05, dur=0.6, blur=18)
        label(c, "HYDROGEN GAS", W / 2, 850, 26, "mono", PAPER, 230 * ha, "center", tracking=0.3)
    label(c, "DRILL MUD · COMING BACK UP", 72, 320, 24, "mono", ASH, 220 * smooth(prog(t, MUD_T, MUD_T + 0.4)), tracking=0.15)


def draw_frame(c, t):
    if t < WATER_T:
        cam = descent(c, t)
        microscope(c, t, smooth(prog(t, FOSSIL_T, FOSSIL_T + 0.7)) * (1 - smooth(prog(t, WATER_T - 0.5, WATER_T))))
        if t > SPECIES_T:
            sa = smooth(prog(t, SPECIES_T, SPECIES_T + 0.3)) * (1 - smooth(prog(t, WATER_T - 0.5, WATER_T)))
            SPECIES.draw(c, W - 72, 380, t, SPECIES_T, 0.9, EMBER, 255 * sa, "right")
            label(c, "SPECIES OF PLANKTON", W - 72, 425, 24, "mono", PAPER, 230 * sa, "right", tracking=0.15)
        if t > AGE_T:
            aa = smooth(prog(t, AGE_T, AGE_T + 0.4)) * (1 - smooth(prog(t, WATER_T - 0.5, WATER_T)))
            reveal(c, "~2 billion years old", W / 2, 1290, 52, t, AGE_T, "serif", PAPER, 255 * aa, "center")
    elif t < MUD_T:
        crystals(c, t)
        if t < WATER_T + 0.3:
            c.drawPaint(fillp(VOID, 255 * (1 - smooth(prog(t, WATER_T, WATER_T + 0.3)))))
    else:
        mud(c, t)
        if t < MUD_T + 0.3:
            c.drawPaint(fillp(VOID, 255 * (1 - smooth(prog(t, MUD_T, MUD_T + 0.3)))))
    for t0 in (WATER_T, MUD_T):                           # dip to black between the discoveries
        if t0 - 0.25 < t < t0:
            c.drawPaint(fillp(VOID, 255 * smooth(prog(t, t0 - 0.25, t0))))
    DUST.draw(c, t, 0.5)
    CAPS.draw(c, t)


def sfx_events():
    return [(0.0, "descend", 0.8), (0.3, "room_tone", 0.4), (FOSSIL_T, "glass_ting", 0.5), (FOSSIL_T + 0.1, "shimmer", 0.7),
            (SPECIES_T, "counter", 0.4), (AGE_T, "low_hit", 0.45), (WATER_T - 0.25, "swish", 0.6), (WATER_T, "low_hit", 0.4),
            (WATER_T + 0.4, "drip", 0.6), (WATER_T + 0.9, "drip", 0.5), (SQUEEZE_T, "drip", 0.6), (SQUEEZE_T + 0.5, "drip", 0.5),
            (SQUEEZE_T + 1.0, "drip", 0.6), (TRAP_T, "pop", 0.6), (MUD_T - 0.25, "swish", 0.6), (MUD_T, "low_hit", 0.5),
            (MUD_T + 0.1, "boil", 0.6), (BOIL_T, "boil", 0.9), (BOIL_T + 2.0, "boil", 0.8), (H2_T - 0.5, "reverse_swell", 0.6),
            (H2_T, "trailer_hit", 0.6)]


MUSIC = dict(beds=[(0.0, WATER_T, "wonder", 0.55), (WATER_T, MUD_T, "deep", 0.5), (MUD_T, DURATION, "heat", 0.4)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
