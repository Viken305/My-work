"""Part 3, the scale: 37 Eiffel Towers stacked down the hole (still 52 m short, seen in a loupe); Everest flips upside
down into the ground (3.4 km above the floor); the deepest ocean beside it; 1970 -> 1989.

  python3 render.py part3 [--still 1,5]
"""
from film import *  # noqa: F401,F403

PART = "part3"
VO, _end = schedule(PART, first=0.3, gap=0.55)
TM = Timing(PART, VO)
DURATION = _end + 1.3

STACK_T = TM.word("B1", "stack") - 0.1
STACK_END = TM.word("B1", "times", end=True)
SHORT_T = TM.word("B1", "still") - 0.1
EVEREST_T = TM.word("B2", "drop") - 0.1
FLIP_T = TM.word("B2", "upside") - 0.2
GAP_T = TM.word("B2", "three") - 0.15
OCEAN_T = TM.word("B3", "deeper") - 0.1
YEARS_T = TM.word("B3", "twenty") - 0.6
CX_STACK = 330
TOWER_M = 330.0

CAPS = Captions(TM, anchors={"B1": (W / 2, 1470), "B2": (W / 2, 1470), "B3": (W / 2, 1470)},
                emph={"thirty", "seven", "everest", "upside", "three", "kilometres", "ocean", "twenty"})
YEARS = Counter("1989", 64, "mono_bold")


def cam_at(t):
    """Starts close on the first tower at the surface, zooms out to the whole hole while the towers stack."""
    k = in_out(prog(t, STACK_T + 0.3, STACK_END + 0.25))
    ppm = math.exp(lerp(math.log(1.25), math.log(FULL["ppm"]), k))
    d = lerp(330, FULL["d"], smooth(clamp((1.25 - ppm) / (1.25 - FULL["ppm"])) ** 0.7))
    return Section(d, ppm, cy=lerp(1020, FULL["cy"], k))


def towers(c, cam, t, a=1.0, n_override=None):
    n = n_override if n_override is not None else int(37 * clamp(prog(t, STACK_T, STACK_END)) + 0.999 * (t > STACK_T))
    n = min(37, n)
    for i in range(n):
        yb = cam.sy((i + 1) * TOWER_M)
        h = TOWER_M * cam.ppm
        pop = out_back(prog(t, STACK_T + i * (STACK_END - STACK_T) / 37, STACK_T + i * (STACK_END - STACK_T) / 37 + 0.2), 2) if n_override is None else 1
        eiffel(c, CX_STACK, yb, h * pop, 230 * a, PAPER, max(1.4, min(3.0, h / 120)))
    return n


def loupe(c, t, cx, cy, r, a):
    """Magnified view of the stack's bottom against the floor of the hole."""
    if a <= 0.01:
        return
    z = 9.0
    cam = cam_at(t)
    fx, fy = CX_STACK + 70, cam.sy(12236)
    c.save()
    path = skia.Path()
    path.addCircle(cx, cy, r)
    c.clipPath(path, doAntiAlias=True)
    c.drawPaint(fillp(VOID))
    c.translate(cx, cy)
    c.scale(z, z)
    c.translate(-fx, -fy)
    strata(c, cam, t, heat=1.0, labels=0, sky=False)
    towers(c, cam, t, 1.0, 37)
    c.drawLine(0, cam.sy(12262), W, cam.sy(12262), stroke(EMBER, 3 / z, 255))
    c.restore()
    c.drawCircle(cx, cy, r, stroke(PAPER, 3, 230 * a))
    c.drawLine(CX_STACK + 8, cam.sy(12262) + 6, cx - r * 0.7, cy - r * 0.7, stroke(PAPER, 1.5, 160 * a))
    label(c, "52 m SHORT", cx, cy - r - 24, 30, "mono_bold", EMBER, 255 * a, "center")


def draw_frame(c, t):
    cam = cam_at(t)
    void(c, t, warm=0.25)
    strata(c, cam, t, heat=1.0, labels=smooth(prog(t, STACK_END, STACK_END + 0.5)) * (1 - smooth(prog(t, OCEAN_T - 0.3, OCEAN_T + 0.2))))
    hole(c, cam, 12262, t, glow=0.9)
    tower(c, W / 2 + 6, cam.sy(0), 0.13 * cam.ppm / FULL["ppm"] if cam.ppm < 0.4 else 0.13 * 4, t)
    yb = cam.sy(12262)
    c.drawLine(W / 2 + 20, yb, W / 2 + 120, yb, stroke(EMBER, 2, 230))
    label(c, "12,262 m", W / 2 + 134, yb + 12, 34, "mono_bold", EMBER, 255)
    # 1) Eiffel stack
    ta = 1 - smooth(prog(t, EVEREST_T - 0.2, EVEREST_T + 0.3))
    if t > STACK_T and ta > 0:
        n = towers(c, cam, t, ta)
        if n:
            ybn = cam.sy(n * TOWER_M)
            label(c, f"×{n}", CX_STACK - 70, ybn + 4, 40, "mono_bold", PAPER, 255 * ta, "right")
        la = smooth(prog(t, SHORT_T, SHORT_T + 0.4)) * ta
        loupe(c, t, 790, 1080, 130, la)
    # 2) Everest flips into the ground
    if t > EVEREST_T:
        ea = 1 - smooth(prog(t, OCEAN_T + 1.4, OCEAN_T + 2.0))
        h = 8849 * cam.ppm
        CXE = 270
        drop = in_out(prog(t, EVEREST_T, FLIP_T + 0.7))
        flip = in_out(prog(t, FLIP_T, FLIP_T + 0.7))
        ytop = cam.sy(0)
        c.save()
        c.translate(CXE, lerp(ytop - h - 200, ytop + h / 2, drop))
        c.scale(1, lerp(1, -1, flip))
        c.translate(0, -h / 2)
        c.saveLayerAlpha(None, int(255 * ea))
        everest(c, 0, 0, h, 240, flip=False, fill_a=170)
        c.restore()
        c.restore()
        if flip >= 1:
            label(c, "EVEREST", CXE, ytop + 80, 26, "mono", PAPER, 230 * ea, "center", tracking=0.25)
        ga = smooth(prog(t, GAP_T, GAP_T + 0.4)) * ea
        if ga > 0:
            k = out_cubic(prog(t, GAP_T, GAP_T + 0.7))
            y0, y1 = cam.sy(8849), cam.sy(8849 + 3413 * k)
            dim_line(c, CXE, y0, y1, ga, "3.4 km" if k > 0.6 else None, side=-1, size=34, rgb=EMBER)
    # 3) the deepest ocean, then 20 years
    if t > OCEAN_T:
        oa = smooth(prog(t, OCEAN_T, OCEAN_T + 0.5))
        k = out_cubic(prog(t, OCEAN_T, OCEAN_T + 1.0))
        x0, x1 = 640, 880
        ytop = cam.sy(0)
        yo = cam.sy(10935 * k)
        c.drawRect(skia.Rect.MakeLTRB(x0, ytop, x1, yo), grad_v(ytop, max(yo, ytop + 1), (40, 70, 100), (10, 22, 40), 200 * oa, 230 * oa))
        xs = np.linspace(x0, x1, 30)
        c.drawPath(path_of([(x, ytop + 4 * math.sin(x * 0.05 + t * 3)) for x in xs]), stroke(STEEL, 2, 230 * oa))
        c.drawLine(x0, yo, x1, yo, stroke(STEEL, 2.5, 255 * oa))
        label(c, "DEEPEST OCEAN", (x0 + x1) / 2, yo + 40, 22, "mono", STEEL, 230 * oa * smooth(prog(k, 0.8, 1)), "center", tracking=0.18)
        label(c, "10,935 m", (x0 + x1) / 2, yo + 80, 30, "mono_bold", STEEL, 255 * oa * smooth(prog(k, 0.8, 1)), "center")
    if t > YEARS_T:
        ya = smooth(prog(t, YEARS_T, YEARS_T + 0.3))
        k = prog(t, YEARS_T, YEARS_T + 2.4)
        # the drilling replays: a pulse of light runs down the hole as the years go by
        yy = cam.sy(12262 * in_out(k))
        light(c, W / 2, yy, 120, (255, 150, 70), 200 * ya * (1 - smooth(prog(k, 0.9, 1))))
        c.drawRect(skia.Rect.MakeXYWH(0, 1235, W, 110), paint(VOID, 170 * ya, 40))
        label(c, "1970", 160, 1310, 52, "mono_bold", ASH, 255 * ya)
        x0, x1 = 330, 750
        c.drawLine(x0, 1293, x1, 1293, stroke(ASH, 2, 160 * ya))
        c.drawLine(x0, 1293, lerp(x0, x1, in_out(k)), 1293, stroke(EMBER, 4, 255 * ya))
        YEARS.draw(c, 780, 1310, t, YEARS_T, 2.4, EMBER, 255 * ya)
    CAPS.draw(c, t)


def sfx_events():
    ev = [(0.0, "room_tone", 0.4)]
    ev += [(STACK_T + i * (STACK_END - STACK_T) / 37, "tick", 0.5 + 0.4 * i / 37) for i in range(37)]
    ev += [(STACK_END, "low_hit", 0.5), (SHORT_T, "pop", 0.6), (SHORT_T + 0.1, "glass_ting", 0.35),
           (EVEREST_T, "whoosh", 0.8), (FLIP_T, "swish", 0.7), (FLIP_T + 0.65, "low_hit", 0.9), (FLIP_T + 0.66, "sub_drop", 0.6),
           (GAP_T, "pop", 0.6), (OCEAN_T, "whoosh", 0.5), (OCEAN_T + 0.2, "drip", 0.6), (OCEAN_T + 0.7, "drip", 0.4),
           (YEARS_T, "counter", 0.55), (YEARS_T, "drill", 0.45), (YEARS_T + 2.4, "low_hit", 0.6)]
    return ev


MUSIC = dict(beds=[(0.0, DURATION, "tension", 0.42)], pulse=[(STACK_T, STACK_END + 0.2, 104)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
