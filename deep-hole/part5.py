"""Part 5, the end: 180 °C at the bottom, the rock goes soft like hot plastic; they stop; zoom out to the crust (one
third) and the whole Earth (0.19 %); the rusty cap in the snow; "It does not scream."; cut to black (loops to the hook).

  python3 render.py part5 [--still 1,5]
"""
from film import *  # noqa: F401,F403

PART = "part5"
VO, _end = schedule(PART, first=0.3, gap=0.6, extra={"D4": 0.5})
TM = Timing(PART, VO)
DURATION = _end + 1.4

TEMP_T = TM.word("D1", "a hundred") - 0.2
EXPECT_T = TM.word("D1", "almost twice") - 0.1
SOFT_T = TM.word("D1", "less like") - 0.2
STOP_T = TM.word("D2", "stopped") - 0.05
CRUST_T = TM.word("D2", "a third") - 0.3
EARTH_T = TM.word("D2", "not even") - 0.2
PCT_T = TM.word("D2", "fifth") - 0.1
CAP_T = VO["D3"] - 0.4
CAPWORD_T = TM.word("D3", "rusty") - 0.2
NO_T = VO["D4"] - 0.1
END_T = TM.end("D4") + 0.5
EARTH_R = 6371000.0
ZOOM_T = STOP_T + 1.3
CRUST_M = 36000.0

CAPS = Captions(TM, anchors={"D1": (W / 2, 1420), "D2": (W / 2, 1420), "D3": (W / 2, 1440), "D4": (W / 2, 1180)},
                hide={"D2": [(PCT_T + 0.2, 99)]},
                emph={"hundred", "eighty", "twice", "plastic", "third", "fifth", "percent", "rusty", "scream"})
SNOW = Snow(200, 4)


def heat_scene(c, t):
    k = prog(t, 0, STOP_T)
    cam = Section(lerp(11400, 12000, in_out(k)), lerp(0.55, 0.9, in_out(k)), cy=900)
    soft = smooth(prog(t, SOFT_T, SOFT_T + 1.2))
    cool = smooth(prog(t, STOP_T, STOP_T + 0.8))
    void(c, t, warm=0.3 * (1 - cool))
    strata(c, cam, t, heat=0.9 * (1 - 0.6 * cool), soft=soft * (1 - 0.7 * cool), labels=0)
    flow = soft * (1 - 0.8 * cool)
    for i in range(16):                                   # the rock starts to flow like taffy
        y0 = 120 + i * 120
        xs = np.linspace(-20, W + 20, 60)
        amp = 6 + 46 * flow * (0.5 + 0.5 * hsh(i, 3))
        ys = y0 + amp * np.sin(xs * (0.006 + 0.003 * hsh(i, 4)) + t * (0.6 + 1.4 * flow) + i)
        c.drawPath(path_of(list(zip(xs, ys))), stroke((150, 108, 84), 1.6, 110 + 60 * flow))
    for i in range(10):                                   # glowing cracks
        x, y = hsh(i, 7) * W, 200 + hsh(i, 8) * 1300
        pul = (0.5 + 0.5 * math.sin(t * 2.2 + i)) * (1 - cool) * smooth(prog(t, TEMP_T, TEMP_T + 1.5))
        pts = [(x + 70 * math.sin(q + i), y + q * 40) for q in range(6)]
        c.drawPath(path_of(pts), stroke((255, 120, 50), 3, 160 * pul, plus=True))
        c.drawPath(path_of(pts), stroke((255, 120, 50), 12, 40 * pul, plus=True))
    hole(c, cam, 12262, t, glow=1.0 - 0.75 * cool, bit=cool < 0.95)
    if soft > 0 and cool < 1:                             # heat haze
        for i in range(14):
            y = (H - (t * 120 + i * 150) % (H + 200))
            xs = np.linspace(0, W, 40)
            c.drawPath(path_of([(x, y + 10 * math.sin(x * 0.02 + t * 4 + i)) for x in xs]), stroke((255, 170, 110), 2, 40 * soft * (1 - cool)))
    temp = 180 * (1 - (1 - prog(t, TEMP_T, TEMP_T + 1.6)) ** 2.5) if t > TEMP_T else 30 + 80 * k
    gauge(c, cam.d, t, 1 - cool, temp=temp)
    ta = smooth(prog(t, TEMP_T, TEMP_T + 0.3)) * (1 - cool)
    if ta > 0:                                            # big temperature, with the expected 100 °C ghosted under it
        c.drawRect(skia.Rect.MakeXYWH(0, 960, W, 300), paint(VOID, 150 * ta, 50))
        txt = f"{int(temp)}"
        wn = width(txt, "mono_bold", 190)
        label(c, txt, W / 2 - 40 - wn / 2, 1170, 190, "mono_bold", mix(PAPER, EMBER, clamp(temp / 180)), 255 * ta)
        label(c, "°C", W / 2 - 40 + wn / 2 + 12, 1170, 100, "serif", EMBER, 255 * ta)
        ea = smooth(prog(t, EXPECT_T, EXPECT_T + 0.4)) * ta
        if ea > 0:
            label(c, "EXPECTED", W / 2 - 150, 1232, 24, "mono", ASH, 220 * ea, "right", tracking=0.2)
            label(c, "100 °C", W / 2 - 130, 1234, 34, "mono_bold", ASH, 230 * ea)
            c.drawLine(W / 2 - 132, 1222, W / 2 - 132 + 120 * out_cubic(prog(t, EXPECT_T + 0.3, EXPECT_T + 0.7)), 1222, stroke(EMBER, 3, 255 * ea))
    if cool > 0:
        label(c, "DRILLING STOPPED", W / 2, 1120, 30, "mono_bold", PAPER, 255 * smooth(prog(t, STOP_T + 0.2, STOP_T + 0.6)), "center", tracking=0.3)


def earth(c, cx, cy, R_, a=1.0):
    """Earth in cross-section: crust line, mantle, outer and inner core, engraved."""
    if R_ > 400000:
        return
    for frac, rgb in ((1.0, (44, 40, 38)), (3480 / 6371, (90, 52, 32)), (1220 / 6371, (150, 92, 50))):
        c.drawCircle(cx, cy, R_ * frac, fillp(rgb, 255 * a))
        c.drawCircle(cx, cy, R_ * frac, stroke((150, 140, 130), 1.5, 160 * a))
    light(c, cx, cy, R_ * 0.4, (255, 150, 80), 90 * a)
    c.drawCircle(cx, cy, R_ * (1 - CRUST_M / EARTH_R), stroke(PAPER, 1.2, 120 * a))


def zoom_out(c, t):
    """From the bottom of the hole out to the crust, then to the whole planet; the surface stays pinned near the top."""
    k1 = in_out(prog(t, ZOOM_T, CRUST_T + 0.3))
    k2 = in_out(prog(t, EARTH_T, PCT_T + 1.0))
    ppm = math.exp(lerp(lerp(math.log(0.9), math.log(0.024), k1), math.log(1100 / (2 * EARTH_R)), k2))
    cy = 760
    if k2 <= 0:                                           # keep the hole's bottom and then the surface in view
        y_surf = lerp(cy - 12000 * 0.9, cy - CRUST_M * 0.5 * 0.024, k1 ** 0.35)
    else:
        y_surf = lerp(cy - CRUST_M * 0.5 * 0.024, 210, k2)
    d = (cy - y_surf) / ppm
    cam = Section(d, ppm, cy=cy)
    void(c, t)
    ex, ey, er = cam.sx(0), cam.sy(EARTH_R), EARTH_R * ppm
    if er < 400000:
        earth(c, ex, ey, er)
        c.drawCircle(ex, ey, er, stroke(PAPER, 2.5, 220))
    else:                                                 # still too big to see the curve: flat mantle below the crust
        y = cam.sy(CRUST_M)
        if y < H:
            c.drawRect(skia.Rect.MakeLTRB(0, max(0, y), W, H), grad_v(y, y + 2890000 * ppm, (52, 40, 34), (90, 52, 32)))
            c.drawLine(0, y, W, y, stroke(PAPER, 1.2, 120))
    if k2 < 0.7:
        c.saveLayerAlpha(None, int(255 * (1 - k2 / 0.7)))
        if er < 400000:
            path = skia.Path()
            path.addCircle(ex, ey, er)
            c.clipPath(path, doAntiAlias=True)
        c.clipRect(skia.Rect.MakeLTRB(0, cam.sy(0), W, cam.sy(CRUST_M)))
        strata(c, cam, t, heat=0.8, labels=0, sky=False)
        c.restore()
    hole(c, cam, 12262, t, glow=0.6, bit=False)
    ya = smooth(prog(t, CRUST_T, CRUST_T + 0.6)) * (1 - smooth(prog(t, EARTH_T, EARTH_T + 0.5)))
    if ya > 0:                                            # the crust and the hole's share of it
        y0, y1, yh = cam.sy(0), cam.sy(CRUST_M), cam.sy(12262)
        c.drawLine(0, y1, W, y1, stroke(PAPER, 2, 200 * ya))
        label(c, "BASE OF THE CRUST · ~36 km", W / 2, y1 + 44, 24, "mono", PAPER, 220 * ya, "center", tracking=0.12)
        dim_line(c, 300, y0, yh, ya, "⅓", side=-1, size=64, rgb=EMBER)
        dim_line(c, 210, y0, y1, ya * 0.7, None, rgb=ASH)
    pa = smooth(prog(t, PCT_T, PCT_T + 0.4))
    if pa > 0:
        c.drawLine(ex, ey - er - 8, ex, ey - er - 70, stroke(EMBER, 3, 255 * pa))
        label(c, "THE HOLE", ex, ey - er - 90, 24, "mono", EMBER, 255 * pa, "center", tracking=0.25)
        label(c, "CENTRE", ex, ey + 10, 22, "mono", PAPER, 200 * pa, "center", tracking=0.25)
        c.drawCircle(ex, ey, 5, fillp(PAPER, 230 * pa))
        reveal(c, "0.19%", W / 2, 1440, 150, t, PCT_T + 0.1, "mono_bold", EMBER, 255, "center", stagger=0.04, dur=0.5)
        label(c, "OF THE WAY TO THE CENTRE", W / 2, 1505, 24, "mono", PAPER, 220 * pa, "center", tracking=0.2)


def cap_scene(c, t):
    """The rusty welded cap in the snow, close up."""
    k = prog(t, CAP_T, DURATION)
    c.save()
    sc = lerp(1.0, 1.12, k)
    c.translate(W / 2, 860)
    c.scale(sc, sc)
    c.translate(-W / 2, -860)
    c.drawPaint(grad_v(0, H, (70, 74, 82), (30, 32, 38)))
    for i in range(300):                                  # snow crust
        x, y = hsh(i, 1) * W, hsh(i, 2) * H
        c.drawCircle(x, y, 1 + 3 * hsh(i, 3), fillp((200, 205, 215), 60 + 60 * hsh(i, 4)))
    cx, cy, r = W / 2, 900, 400
    c.drawOval(skia.Rect.MakeXYWH(cx - r - 60, cy - r * 0.5 + 40, (r + 60) * 2, r * 1.0 + 60), paint((10, 10, 12), 160, 30))
    c.drawOval(skia.Rect.MakeXYWH(cx - r - 30, cy - r * 0.5 - 10, (r + 30) * 2, r * 1.0 + 40), fillp((54, 46, 42)))   # concrete collar
    c.drawOval(skia.Rect.MakeXYWH(cx - r, cy - r * 0.5, r * 2, r * 1.0),
               skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial((cx - 80, cy - 60), r * 1.3,
                          [skia.Color(150, 82, 48), skia.Color(110, 56, 34), skia.Color(62, 34, 26)])))
    for i in range(160):                                  # rust pitting
        an, rr = hsh(i, 5) * 6.283, math.sqrt(hsh(i, 6)) * r * 0.95
        c.drawCircle(cx + math.cos(an) * rr, cy + math.sin(an) * rr * 0.5, 2 + 7 * hsh(i, 7),
                     fillp(mix((70, 36, 24), (180, 104, 60), hsh(i, 8)), 120))
    c.drawOval(skia.Rect.MakeXYWH(cx - r * 0.86, cy - r * 0.43, r * 1.72, r * 0.86), stroke((60, 32, 24), 4, 200))
    for i in range(12):                                   # bolts
        an = i / 12 * 6.283
        bx, by = cx + math.cos(an) * r * 0.93, cy + math.sin(an) * r * 0.465
        c.drawCircle(bx, by, 11, fillp((80, 48, 34)))
        c.drawCircle(bx - 3, by - 3, 4, fillp((170, 110, 70)))
    c.drawLine(cx - r * 0.55, cy, cx + r * 0.55, cy, stroke((70, 38, 28), 8, 220))     # weld seam
    for i in range(30):
        x = cx - r * 0.55 + i * r * 1.1 / 30
        c.drawCircle(x, cy + 2 * math.sin(i), 6, fillp((120, 70, 46), 200))
    c.restore()
    SNOW.draw(c, t, 1.0, wind=60)
    la = smooth(prog(t, CAPWORD_T, CAPWORD_T + 0.5))
    label(c, "KOLA SUPERDEEP BOREHOLE · TODAY", W / 2, 400, 24, "mono", PAPER, 210 * la, "center", tracking=0.2)


def draw_frame(c, t):
    if t < ZOOM_T:
        heat_scene(c, t)
    elif t < CAP_T:
        zoom_out(c, t)
    else:
        cap_scene(c, t)
        if t < CAP_T + 0.4:
            c.drawPaint(fillp(VOID, 255 * (1 - smooth(prog(t, CAP_T, CAP_T + 0.4)))))
    if CAP_T - 0.4 < t < CAP_T:
        c.drawPaint(fillp(VOID, 255 * smooth(prog(t, CAP_T - 0.4, CAP_T))))
    if t > NO_T - 0.3:                                    # the last line sits alone on a dimmed frame
        c.drawPaint(fillp(VOID, 170 * smooth(prog(t, NO_T - 0.3, NO_T + 0.2))))
    CAPS.draw(c, t)
    if t > END_T:                                         # hard cut to black: the hook starts from black again
        c.drawPaint(fillp(VOID))


def sfx_events():
    return [(0.0, "heat_roar", 0.8), (2.5, "heat_roar", 0.7), (TEMP_T, "counter", 0.5), (SOFT_T, "heat_roar", 1.0),
            (SOFT_T + 0.3, "sub_drop", 0.6), (STOP_T - 0.05, "tape_stop", 0.9), (STOP_T + 0.1, "low_hit", 0.7),
            (ZOOM_T, "descend", 0.6), (CRUST_T + 0.4, "pop", 0.5), (EARTH_T, "whoosh", 0.8), (EARTH_T + 0.6, "whoosh", 0.6),
            (PCT_T + 0.1, "glass_ting", 0.5), (PCT_T + 0.15, "low_hit", 0.5), (CAP_T - 0.3, "swish", 0.5), (CAP_T, "wind", 0.8),
            (CAP_T + 4.0, "wind", 0.7), (CAPWORD_T + 0.3, "metal_clank", 0.5), (NO_T + 2.0, "wind", 0.4)]


MUSIC = dict(beds=[(0.0, STOP_T, "heat", 0.55), (STOP_T + 0.8, CAP_T, "deep", 0.5), (CAP_T, NO_T - 0.2, "end", 0.6)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
