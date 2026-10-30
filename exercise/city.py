"""Style A · RUSH HOUR. Your body is a city at night. The heart is the power station in the middle, arteries are red
highways and veins blue ones, red blood cells are the traffic. Exercise is rush hour: the heart beats faster, the
traffic speeds up, split-flap boards flip up the numbers.
Captions: the narration lights up dot by dot on an overhead LED highway sign; emphasis words glow red.

  python3 render.py city [--still 2,4]
"""
from kit import *  # noqa: F401,F403

PART = "city"
VO, _end = schedule(PART, first=0.5, gap=0.5)
TM = Timing(PART, VO)
DURATION = _end + 1.3

NAVY0, NAVY1 = (8, 12, 30), (20, 32, 66)
AMBER = (255, 178, 60)
RED = (255, 62, 72)
BLUE = (80, 150, 255)
STEEL = (34, 40, 56)
RAMP_T0, RAMP_T1 = 0.4, TM.end("A")
EMPH = {"sprint,", "five", "times", "blood"}
S = 1.0


def ramp(t):
    return in_out(prog(t, RAMP_T0, RAMP_T1))


def bpm(t):
    return 72 + 88 * ramp(t)


def beat_phase(t):
    """Integral of the heart rate: number of beats since 0 (smooth, so the beat speeds up without jumps)."""
    n = 200
    ts = np.linspace(0, t, n)
    trap = getattr(np, "trapezoid", None) or np.trapz
    return float(trap([bpm(x) / 60 for x in ts], ts)) if t > 0 else 0.0


def beat(t):
    ph = beat_phase(t) % 1.0
    return math.exp(-ph * 9) + 0.5 * math.exp(-max(0, ph - 0.18) * 12) * (ph > 0.18)


def P(x, y, z=0.0, cam=(540, 1270, 1.0)):
    cx, cy, zz = cam
    return cx + (x - y) * 0.866 * zz, cy + (x + y) * 0.5 * zz - z * zz


# ---------------------------------------------------------------- the city
BUILD = []
for gx in range(-7, 8):
    for gy in range(-7, 8):
        if abs(gx) <= 1 or abs(gy) <= 1:              # roads run along the axes (arteries and veins)
            continue
        if gx > 0 and gy > 0 and gx + gy <= 5:          # keep the plaza in front of the heart clear
            continue
        if abs(gx) + abs(gy) > 11:
            continue
        hgt = 40 + 220 * hsh(gx, gy) ** 2 * (1 - (abs(gx) + abs(gy)) / 14)
        BUILD.append((gx, gy, hgt))
BUILD.sort(key=lambda b: b[0] + b[1])


def box(c, x, y, w, d, h, cam, top, left, right, windows=0.0, seed=0):
    pts = lambda a: P(*a, cam=cam)  # noqa: E731
    t_ = [pts((x, y, h)), pts((x + w, y, h)), pts((x + w, y + d, h)), pts((x, y + d, h))]
    l_ = [pts((x, y + d, 0)), pts((x + w, y + d, 0)), pts((x + w, y + d, h)), pts((x, y + d, h))]
    r_ = [pts((x + w, y, 0)), pts((x + w, y + d, 0)), pts((x + w, y + d, h)), pts((x + w, y, h))]
    c.drawPath(path_of(l_, True), fillp(left))
    c.drawPath(path_of(r_, True), fillp(right))
    c.drawPath(path_of(t_, True), fillp(top))
    if windows > 0:                                   # lit windows on the two visible faces
        for face, (ax, ay, bx, by) in enumerate(((x, y + d, x + w, y + d), (x + w, y, x + w, y + d))):
            for row in range(int(h // 22)):
                for col in range(3):
                    if hsh(seed, face, row, col) > 0.55:
                        u = (col + 0.5) / 3
                        px, py = P(lerp(ax, bx, u), lerp(ay, by, u), 14 + row * 22, cam=cam)
                        rgb = AMBER if hsh(seed, row, col, 9) > 0.3 else (150, 220, 255)
                        c.drawRect(skia.Rect.MakeXYWH(px - 3, py - 4, 6, 7), fillp(rgb, 200 * windows))


def heart_station(c, t, cam, k=1.0):
    bt = beat(t)
    x, y = P(0, 0, 0, cam)
    zz = cam[2]
    for i in range(3):                                # pulse rings on the ground, one per beat
        ph = (beat_phase(t) + i / 3) % 1
        r = (60 + 260 * ph) * zz
        c.drawOval(skia.Rect.MakeXYWH(x - r, y - r * 0.5, 2 * r, r), stroke(RED, 4 * zz, 200 * (1 - ph) * k))
    light(c, x, y - 120 * zz, 380 * zz * (1 + 0.15 * bt), RED, (110 + 80 * bt) * k)
    sc = zz * (1 + 0.09 * bt)
    c.save()
    c.translate(x, y - 125 * zz)
    c.scale(sc, sc)
    hp = skia.Path()
    hp.moveTo(0, 90)
    hp.cubicTo(-150, -10, -110, -140, 0, -70)
    hp.cubicTo(110, -140, 150, -10, 0, 90)
    hp.close()
    c.drawPath(hp, shaded(radial((-30, -60), 190, [(255, 140, 150), (230, 30, 60), (120, 0, 30)], [0, 0.5, 1])))
    c.drawPath(hp, stroke((255, 200, 200), 4, 200))
    for i, (ax, ay) in enumerate(((-40, -92), (0, -100), (36, -96))):     # the great vessels as pipes on the roof
        c.drawRRect(rrect(ax - 12, ay - 50, 24, 60, 10), fillp(RED if i != 1 else BLUE))
    c.drawPath(skia.Path().addCircle(-48, -40, 18), fillp((255, 255, 255), 90))
    c.restore()
    return x, y + 70 * zz


def roads(c, t, cam):
    L = 7.6 * 60
    speed = bpm(t) / 72
    for axis in (0, 1):
        for sgn in (-1, 1):
            # artery lanes (red, outbound) and vein lanes (blue, inbound) side by side
            for lane, rgb, out in ((-22, RED, 1), (22, BLUE, -1)):
                def pt(u):
                    d = sgn * u * L
                    return P(d, lane, 0, cam) if axis == 0 else P(lane, d, 0, cam)
                a, b = pt(0.12), pt(1.0)
                c.drawLine(*a, *b, stroke(mix(rgb, (0, 0, 0), 0.65), 30 * cam[2]))
                c.drawLine(*a, *b, stroke(rgb, 3 * cam[2], 120, plus=True))
                for i in range(22):                   # red blood cells as traffic
                    u = (i / 22 + out * t * 0.12 * speed + hsh(axis, sgn, lane, i) * 0.04) % 1.0
                    if out < 0:
                        u = 1 - u
                    uu = 0.12 + 0.88 * u
                    px, py = pt(uu)
                    rr = 9 * cam[2]
                    col_ = (230, 40, 60) if out > 0 else (90, 60, 170)
                    c.drawOval(skia.Rect.MakeXYWH(px - rr, py - rr * 0.55, rr * 2, rr * 1.1), fillp(col_))
                    c.drawOval(skia.Rect.MakeXYWH(px - rr * 0.45, py - rr * 0.25, rr * 0.9, rr * 0.5), fillp(mix(col_, (0, 0, 0), 0.35)))
                    light(c, px, py, rr * 3 * (0.6 + 0.4 * speed), rgb, 40)


def city(c, t, cam):
    for gx, gy, hgt in BUILD:
        if gx + gy < 0:
            draw_building(c, gx, gy, hgt, cam, t)
    roads(c, t, cam)
    lx, ly = heart_station(c, t, cam)
    for gx, gy, hgt in BUILD:
        if gx + gy >= 0:
            draw_building(c, gx, gy, hgt, cam, t)
    tw = width("HEART POWER STATION", "mono_bold", 22, 0.1)
    c.drawRRect(rrect(lx - tw / 2 - 16, ly - 30, tw + 32, 44, 10), fillp((10, 8, 20), 200))
    label(c, "HEART POWER STATION", lx, ly, 22, "mono_bold", (255, 210, 210), 240, "center", tracking=0.1)


def draw_building(c, gx, gy, hgt, cam, t):
    x, y = gx * 60 - 25, gy * 60 - 25
    d = math.hypot(gx, gy)
    glowk = 0.5 + 0.5 * beat(t - d * 0.05)            # windows flicker with the pulse spreading out
    box(c, x, y, 50, 50, hgt, cam, (44, 56, 96), (22, 30, 58), (30, 40, 74), windows=0.6 + 0.4 * glowk, seed=gx * 31 + gy)


# ---------------------------------------------------------------- signs
class LEDCaption:
    """Narration on a two-line dot-matrix highway sign. Characters light up as their word is spoken."""

    def __init__(self, tm, key, cols=16):
        words = tm.words(key)
        lines, cur = [], []
        for w in words:
            txt = " ".join(x[2] for x in cur + [w]).upper()
            if cur and len(txt) > cols:
                lines.append(cur)
                cur = []
            cur.append(w)
        lines.append(cur)
        self.pages = [lines[i:i + 2] for i in range(0, len(lines), 2)]
        self.cols = cols

    def draw(self, c, t, x, y, pitch):
        for pi, page in enumerate(self.pages):
            t0 = page[0][0][0]
            t1 = self.pages[pi + 1][0][0][0] - 0.05 if pi + 1 < len(self.pages) else 1e9
            if not (t0 - 0.1 <= t < t1):
                continue
            for li, line in enumerate(page):
                s, starts, emph = "", [], []
                for a, b, w in line:
                    if s:
                        s += " "
                        starts.append(a)
                        emph.append(False)
                    for ch in w.upper():
                        s += ch
                        starts.append(a)
                        emph.append(w.lower() in EMPH)
                off = (self.cols - len(s)) / 2
                base_x = x + off * 6 * pitch
                for i, ch in enumerate(s):
                    k = smooth(prog(t, starts[i] + i * 0.012 - 0.04, starts[i] + i * 0.012 + 0.08))
                    on = RED if emph[i] else AMBER
                    led_text(c, ch, base_x + i * 6 * pitch, y + li * 10 * pitch, pitch, lambda _: k, on)
            return
        # blank board
        for li in range(2):
            led_text(c, " " * self.cols, x, y + li * 10 * pitch, pitch, lambda _: 0, AMBER)


CAP = LEDCaption(TM, "A")


GY = -150                                              # the sign sits high, clear of the city


def gantry(c, t):
    c.save()
    c.translate(0, GY)
    for px in (70, 1010):                               # posts
        c.drawRect(skia.Rect.MakeXYWH(px - 14, 420, 28, H), fillp(STEEL))
        c.drawRect(skia.Rect.MakeXYWH(px - 14, 420, 8, H), fillp((60, 68, 90)))
    c.drawRect(skia.Rect.MakeXYWH(40, 410, 1000, 26), fillp(STEEL))
    for i in range(20):                                 # truss
        x = 50 + i * 50
        c.drawLine(x, 412, x + 50, 434, stroke((60, 68, 90), 3))
    c.drawRRect(rrect(60, 450, 960, 250, 14), fillp((10, 8, 6)))
    c.drawRRect(rrect(60, 450, 960, 250, 14), stroke((70, 76, 96), 6))
    pitch = 9.2
    CAP.draw(c, t, 540 - 16 * 6 * pitch / 2 + pitch * 0.5, 500, pitch)
    c.restore()


def flap(c, x, y, txt, t, change_t, label_txt, rgb):
    """Split-flap board: each digit tile flips when its value changes."""
    tw, th = 64, 92
    label(c, label_txt, x, y - 16, 20, "mono_bold", (180, 190, 210), 230, tracking=0.1)
    for i, ch in enumerate(txt):
        tx = x + i * (tw + 8)
        c.drawRRect(rrect(tx, y, tw, th, 8), fillp((20, 22, 30)))
        fl = change_t.get(i, -9)
        u = prog(t, fl, fl + 0.12)
        sy = abs(math.cos(u * math.pi)) if 0 < u < 1 else 1.0
        c.save()
        c.translate(tx + tw / 2, y + th / 2)
        c.scale(1, max(0.05, sy))
        f = font("overpass_black", 72)
        wch = f.measureText(ch)
        c.drawString(ch, -wch / 2, 26, f, paint(rgb, 255))
        c.restore()
        c.drawLine(tx, y + th / 2, tx + tw, y + th / 2, stroke((0, 0, 0), 3))
    return x + len(txt) * (tw + 8)


def digits_with_flips(value_fn, t, n, fmt):
    """Current text plus, for each digit, the time it last changed (for the flip)."""
    cur = fmt.format(int(value_fn(t)))
    flips = {}
    for i in range(n):
        tt = t
        for _ in range(12):                             # look back up to 0.12 s for a change
            tt -= 0.01
            if fmt.format(int(value_fn(max(0, tt))))[i] != cur[i]:
                flips[i] = tt
                break
    return cur, flips


def boards(c, t):
    co = lambda tt: 5 + 20 * ramp(tt)  # noqa: E731
    txt, fl = digits_with_flips(co, t, 2, "{:02d}")
    xe = flap(c, 100, 760 + GY, txt, t, fl, "BLOOD PUMPED", AMBER)
    label(c, "L/MIN", xe + 6, 840 + GY, 28, "overpass", AMBER, 255)
    txt, fl = digits_with_flips(bpm, t, 3, "{:03d}")
    xe = flap(c, 600, 760 + GY, txt, t, fl, "HEART RATE", RED)
    label(c, "BPM", xe + 6, 840 + GY, 28, "overpass", RED, 255)


def draw_frame(c, t):
    c.drawRect(skia.Rect.MakeWH(W, H), grad_v(0, H, NAVY0, NAVY1))
    for i in range(70):                                 # haze stars
        c.drawCircle(hsh(i, 1) * W, 400 + hsh(i, 2) * 500, 1.6, fillp((200, 210, 255), 90))
    z = lerp(1.3, 1.52, in_out(prog(t, 0, DURATION)))
    cam = (540 + 30 * math.sin(t * 0.3), 1180 - 30 * prog(t, 0, DURATION), z)
    city(c, t, cam)
    c.drawRect(skia.Rect.MakeLTRB(0, 1500, W, H), grad_v(1500, H, NAVY1, (4, 6, 14), 0, 255))
    gantry(c, t)
    boards(c, t)
    style_tag(c, t, "STYLE A · RUSH HOUR", DURATION)
    k = max(1 - smooth(prog(t, 0, 0.3)), smooth(prog(t, DURATION - 0.25, DURATION)))
    if k > 0:
        c.drawPaint(fillp((0, 0, 0), 255 * k))


def POST(t):
    return dict(grain=4.0, ca=0.5, bloom=1.0)


def sfx_events():
    ev = [(0.0, "whoosh", 0.4), (VO["A"], "tick_roll", 0.25)]
    tt = 0.2
    while tt < DURATION:                                 # heartbeat that speeds up with the ramp
        ev.append((tt, "heartbeat", 0.5 + 0.3 * ramp(tt)))
        tt += 60 / bpm(tt)
    ev += [(TM.word("A", "five") - 0.05, "low_hit", 0.5), (DURATION - 0.6, "swish", 0.4)]
    return ev


MUSIC = dict(beds=[(0.0, DURATION, "pulse_bed", 0.5)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
