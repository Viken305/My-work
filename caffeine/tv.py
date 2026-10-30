"""THE CAFFEINE TAPE: the shared engine of every programme on the tape (part1..part6).

The whole Short plays as one worn VHS recording of 90s TV. The VCR counter is the timeline: between programmes the
tape fast-forwards (picture tears, counter spins) from one moment after the sip to the next. Each part is a different
kind of 90s show (title card, medical tape, game show, weather report, market report) and draws its own scene; this
module draws the programme banner, the VCR on-screen display, the camcorder date stamp and the closed captions.
"""
from engine import col
from kit import *  # noqa: F401,F403
from script import PARTS as LINES

# 90s broadcast palette
TEAL, MAGENTA, PURPLE, YELLOW = (0, 206, 190), (255, 46, 150), (96, 40, 190), (255, 222, 30)
BLUE, NAVY, ORANGE, RED = (24, 70, 220), (10, 18, 70), (255, 130, 30), (235, 40, 50)
CREAM, BROWN, WHITE, BLACK = (255, 240, 214), (110, 60, 30), (255, 255, 255), (0, 0, 0)
LIME, PINK, SKY = (140, 240, 60), (255, 140, 200), (90, 190, 255)
OSD = (235, 255, 235)
STAMP = (255, 196, 60)

ORDER = ["part1", "part2", "part3", "part4", "part5", "part6"]
# per programme: banner name, colours, the story clock (seconds after the sip), line timing
PROGS = {
    "part1": dict(name=None, clock=0, first=1.6, gap=0.35, tail=0.5, rgb=(MAGENTA, TEAL)),
    "part2": dict(name="MEDICAL TAPE 7", clock=600, first=1.2, gap=0.45, tail=0.7, rgb=(TEAL, BLUE)),
    "part3": dict(name="PARK THAT MOLECULE!", clock=2700, first=1.2, gap=0.45, tail=0.7, rgb=(MAGENTA, YELLOW)),
    "part4": dict(name="THE BODY FORECAST", clock=3600, first=1.2, gap=0.4, tail=0.7, rgb=(BLUE, YELLOW)),
    "part5": dict(name="CAFFEINE MARKETS", clock=18000, first=1.2, gap=0.45, tail=0.7, rgb=(NAVY, YELLOW)),
    "part6": dict(name="PARK THAT MOLECULE!", clock=21600, first=1.2, gap=0.45, tail=2.6, rgb=(MAGENTA, YELLOW)),
}
FF = 0.95                      # length of the fast-forward at the head of each programme

# numbers read as words become digits in the captions; EMPH words are captioned in yellow
MERGES = {
    "H2": [("six hours", "6 HOURS")],
    "A1": [("ten minutes", "10 MINUTES")],
    "A2": [("forty five minutes", "45 MINUTES")],
    "C3": [("one in three", "1 IN 3")],
    "D1": [("five hours", "5 HOURS")],
    "D2": [("six hours", "6 HOURS"), ("an hour", "1 HOUR")],
    "E3": [("four cups", "4 CUPS")],
}
EMPH = {"coffee", "adenosine", "sleepier", "blocks", "adrenaline", "dopamine", "sharp", "focused", "gut", "half",
        "slowly", "crash", "early", "rewind", "caffeine", "blood", "pressure"}
CAP_SIZE, CAP_Y, CAP_ROW, CAP_CHARS = 84, 1228, 88, 24


def _clean(w):
    return "".join(ch for ch in w.lower() if ch.isalnum() or ch == "'")


def build_pages(part, tm):
    """Caption pages: [dict(t0, t1, rows=[[(t, text, emph)]])]. Two rows of at most CAP_CHARS, broken at sentences."""
    pages = []
    for li, (key, _) in enumerate(LINES[part]):
        ws = tm.words(key)
        clean = [_clean(w) for _, _, w in ws]
        merges = [(m[0].split(), m[1]) for m in MERGES.get(key, [])]
        toks, i = [], 0
        while i < len(ws):
            hit = next((m for m in merges if clean[i:i + len(m[0])] == m[0]), None)
            if hit:
                j = i + len(hit[0]) - 1
                tail = ws[j][2][-1] if ws[j][2][-1] in ",.?!" else ""
                toks.append((ws[i][0], hit[1] + tail, True))
                merges.remove(hit)
                i = j + 1
            else:
                toks.append((ws[i][0], ws[i][2].upper(), clean[i] in EMPH or clean[i].rstrip("s") in EMPH))
                i += 1
        out, pg = [], []
        for k, tk in enumerate(toks):
            n = sum(len(x[1]) + 1 for x in pg) + len(tk[1])
            if pg and n > 2 * CAP_CHARS - 6:
                out.append(pg)
                pg = []
            pg.append(tk)
            n = sum(len(x[1]) + 1 for x in pg) - 1
            end = tk[1][-1] in ".?!" or (tk[1][-1] == "," and n > 26)
            if end and k < len(toks) - 1:                      # sentences (and long clauses) start a new page
                out.append(pg)
                pg = []
        if pg:
            out.append(pg)
        out = [_rows(pg) for pg in out]
        line_end = tm.end(key)
        for pg in out:
            pages.append(dict(t0=pg[0][0][0] - 0.04, rows=pg, line=key, line_end=line_end))
    for a, b in zip(pages, pages[1:]):
        a["t1"] = min(b["t0"], a["line_end"] + 0.9) if a["line"] != b["line"] else b["t0"]
    if pages:
        pages[-1]["t1"] = pages[-1]["line_end"] + 1.0
    return pages


def _rows(pg):
    """One row if it fits, else the two-row split with the most even lengths."""
    ln = lambda xs: sum(len(x[1]) + 1 for x in xs) - 1          # noqa: E731
    if ln(pg) <= 22 or len(pg) == 1:
        return [pg]
    k = min(range(1, len(pg)), key=lambda i: max(ln(pg[:i]), ln(pg[i:])))
    return [pg[:k], pg[k:]]


def _sched(part):
    P = PROGS[part]
    vo, end = schedule(part, first=P["first"], gap=P["gap"])
    return vo, Timing(part, vo), round(end - P["gap"] + P["tail"], 2)


def hms(s):
    s = int(max(0, s))
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}"


def clock12(s):
    m = 8 * 60 + int(s // 60)                                  # the sip is at 8:00 AM
    h, mm = m // 60 % 24, m % 60
    return f"{'AM' if h < 12 else 'PM'} {(h - 1) % 12 + 1}:{mm:02d}"


class Show:
    def __init__(self, part):
        self.part = part
        self.P = PROGS[part]
        self.VO, self.TM, self.DURATION = _sched(part)
        self.pages = build_pages(part, self.TM)
        i = ORDER.index(part)
        self.prev_clock = PROGS[ORDER[i - 1]]["clock"] + 20 if i else 0
        self.first = i == 0
        self.osd_mode = None            # a part may force "REW" / "STOP" etc. via osd_fn
        self.osd_fn = None
        self.post_fn = None

    def w(self, key, phrase, end=False):
        return self.TM.word(key, phrase, end)

    # ------------------------------------------------------------ time
    def clock(self, t):
        if getattr(self, "clock_fn", None):
            v = self.clock_fn(t)
            if v is not None:
                return v
        if self.first:
            return max(0.0, t - 0.75)
        if t < FF:
            return lerp(self.prev_clock, self.P["clock"], in_out(prog(t, 0.05, FF - 0.1)))
        return self.P["clock"] + (t - FF)

    # ------------------------------------------------------------ picture
    def banner(self, c, t, a=255):
        """Programme strip: a skewed gradient bar slides in with the show's name."""
        name = self.P["name"]
        if not name or a <= 1:
            return
        rgb0, rgb1 = self.P["rgb"]
        u = out_cubic(prog(t, FF, FF + 0.45))
        x = lerp(-1100, 0, u)
        c.save()
        c.translate(x, 0)
        c.skew(-0.2, 0)
        y0, y1 = 300, 384
        sh = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([(0, 0), (1000, 0)], [col(rgb0, a), col(mix(rgb0, rgb1, 0.4), a)]))
        c.drawRect(skia.Rect.MakeLTRB(120, y0, 1060, y1), sh)
        c.drawRect(skia.Rect.MakeLTRB(120, y0, 1060, y0 + 6), fillp(WHITE, 0.7 * a))
        c.drawRect(skia.Rect.MakeLTRB(120, y1 - 8, 1060, y1), fillp(rgb1, a))
        c.drawRect(skia.Rect.MakeLTRB(80, y0, 104, y1), fillp(rgb1, a))
        c.drawRect(skia.Rect.MakeLTRB(52, y0, 66, y1), fillp(rgb1, 0.7 * a))
        c.restore()
        outlined(c, name, 600 + x, y1 - 22, 58, "righteous", WHITE, a, "center", ow=0.1, outline_rgb=mix(rgb0, BLACK, 0.6))

    def frame(self, c, t, scene):
        scene(c, t)
        self.banner(c, t)
        if self.first and t < 0.75:                       # the CRT warms up: a bright line opens into the picture
            u = prog(t, 0.22, 0.7)
            c.save()
            h = lerp(4, H, out_cubic(u)) if u > 0 else 0
            c.clipRect(skia.Rect.MakeLTRB(0, (H - h) / 2, W, (H + h) / 2), skia.ClipOp.kDifference)
            c.drawPaint(fillp(BLACK))
            c.restore()
            if 0.2 < t < 0.7:
                c.drawRect(skia.Rect.MakeLTRB(0, (H - h) / 2 - 4, W, (H + h) / 2 + 4), fillp(WHITE, 200 * (1 - u) ** 2))

    # ------------------------------------------------------------ on-screen display (sharp, drawn after the tape)
    def osd(self, c, t):
        mode = self.osd_fn(t) if self.osd_fn else None
        if mode is None:
            mode = "FF" if (not self.first and t < FF) else "PLAY"
        if self.first and t < 0.7:
            return
        blink = mode != "PLAY" or (self.first and t < 2.6)
        if mode == "STOP":
            osd_text(c, "STOP", 70, 220, 82)
            osd_rect(c, 260, 166, 52, 52)
        elif mode == "PLAY":
            if not blink or int(t * 2.5) % 2 == 0 or t > 2.6:
                osd_text(c, "PLAY", 70, 220, 82)
                osd_tri(c, 250, 192, 1, 60)
        elif mode == "FF":
            osd_tri(c, 82, 192, 1, 50)
            osd_tri(c, 132, 192, 1, 50)
            osd_text(c, "FF", 200, 220, 82)
        elif mode == "REW":
            osd_tri(c, 132, 192, -1, 50)
            osd_tri(c, 82, 192, -1, 50)
            osd_text(c, "REW", 200, 220, 82)
        osd_text(c, hms(self.clock(t)), 1010, 220, 82, align="right")
        osd_text(c, "SP", 1010, 282, 56, align="right")
        if mode != "STOP":                                      # camcorder date stamp
            osd_text(c, clock12(self.clock(t)), 70, 1478, 66, rgb=STAMP)
            osd_text(c, "OCT.30 1996", 70, 1538, 66, rgb=STAMP)

    def captions(self, c, t):
        f = font("vt", CAP_SIZE)
        for pg in self.pages:
            if not (pg["t0"] <= t < pg["t1"]):
                continue
            x0 = 540 - max(f.measureText(" ".join(x[1] for x in row)) for row in pg["rows"]) / 2   # one left edge per page
            for r, row in enumerate(pg["rows"]):
                shown = [tk for tk in row if tk[0] <= t]
                if not shown:
                    continue
                y = CAP_Y + r * CAP_ROW + (CAP_ROW if len(pg["rows"]) == 1 else 0)
                txt = " ".join(x[1] for x in shown)
                wd = f.measureText(txt)
                c.drawRect(skia.Rect.MakeLTRB(x0 - 18, y - 64, x0 + wd + 18, y + 22), fillp(BLACK, 235))
                x = x0
                for tk in shown:
                    c.drawString(tk[1], x, y, f, fillp(YELLOW if tk[2] else WHITE))
                    x += f.measureText(tk[1] + " ")
            break

    def overlay(self, c, t):
        self.osd(c, t)
        self.captions(c, t)

    def post(self, t):
        kw = dict(ff=0.0, rew=0.0, track=0.3, snow=1.0)
        if not self.first and t < FF:
            kw["ff"] = 1 - smooth(prog(t, FF - 0.25, FF))
            kw["track"] = 1.0
        if self.first and t < 0.8:
            kw["snow"] = 3.0
            kw["track"] = 1.0 - prog(t, 0.5, 0.8) * 0.7
        if self.post_fn:
            kw.update(self.post_fn(t))
        return kw

    def sfx(self):
        if self.first:
            return [(0.15, "crt_on", 0.6), (0.65, "clunk", 0.6)]
        return [(0.0, "ff", 0.55), (FF - 0.08, "clunk", 0.55)]

    def music(self, beds=None, mute=None):
        start = 0.8 if self.first else FF
        return dict(beds=beds or [(start, self.DURATION, "lounge", 0.55)], mute=mute or [])


# ---------------------------------------------------------------- OSD helpers
def osd_text(c, s, x, y, size, rgb=OSD, align="left"):
    label(c, s, x + 5, y + 5, size, "vt", BLACK, 200, align)
    label(c, s, x, y, size, "vt", rgb, 120, align, sigma=6)
    label(c, s, x, y, size, "vt", rgb, 255, align)


def osd_tri(c, x, y, d, s):
    p = path_of([(x - d * s * 0.42, y - s * 0.5), (x + d * s * 0.5, y), (x - d * s * 0.42, y + s * 0.5)], True)
    c.save()
    c.translate(5, 5)
    c.drawPath(p, fillp(BLACK, 200))
    c.restore()
    c.drawPath(p, fillp(OSD))


def osd_rect(c, x, y, w, h):
    c.drawRect(skia.Rect.MakeXYWH(x + 5, y + 5, w, h), fillp(BLACK, 200))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fillp(OSD))


# ---------------------------------------------------------------- 90s graphics kit
def appear(t, t0, d=0.35):
    return out_back(prog(t, t0, t0 + d), 2.0)


def gradient_bg(c, top, bottom, a=255):
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), grad_v(0, H, top, bottom, a, a))


def memphis(c, t, seed=1, a=255, cols=(TEAL, MAGENTA, YELLOW, PURPLE), n=26, area=(0, 380, W, 1180)):
    """Floating Memphis-style confetti: squiggles, triangles, rings and dot grids, drifting slowly."""
    x0, y0, x1, y1 = area
    for i in range(n):
        rgb = cols[i % len(cols)]
        x = x0 + (hsh(seed, i, 1) * (x1 - x0) + t * 14 * (hsh(seed, i, 2) - 0.5)) % (x1 - x0)
        y = y0 + (hsh(seed, i, 3) * (y1 - y0) + t * 10 * (hsh(seed, i, 4) - 0.5)) % (y1 - y0)
        rot = t * 30 * (hsh(seed, i, 5) - 0.5) + 360 * hsh(seed, i, 6)
        s = 0.7 + 0.6 * hsh(seed, i, 7)
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.scale(s, s)
        k = i % 4
        if k == 0:
            pts = [(-50 + 10 * j, 12 * (1 if j % 2 else -1)) for j in range(11)]
            c.drawPath(path_of(pts), stroke(rgb, 9, a))
        elif k == 1:
            c.drawPath(path_of([(0, -30), (28, 20), (-28, 20)], True), fillp(rgb, a))
        elif k == 2:
            c.drawCircle(0, 0, 22, stroke(rgb, 8, a))
        else:
            for jx in range(3):
                for jy in range(3):
                    c.drawCircle(-20 + 20 * jx, -20 + 20 * jy, 5, fillp(rgb, a))
        c.restore()


def grid_floor(c, t, horizon, rgb, a=255, speed=0.6, bottom=H):
    """Perspective neon grid scrolling toward the viewer."""
    for i in range(-14, 15):
        c.drawLine(540 + i * 30, horizon, 540 + i * 260, bottom, stroke(rgb, 3, a * 0.8))
    for k in range(14):
        u = ((k + t * speed) % 14) / 14
        y = horizon + (bottom - horizon) * u ** 2.2
        c.drawLine(0, y, W, y, stroke(rgb, 2 + 3 * u, a * (0.3 + 0.7 * u)))
    c.drawLine(0, horizon, W, horizon, stroke(rgb, 4, a))


def starburst(c, x, y, r0, r1, n, rgb, rot=0.0, a=255):
    pts = []
    for i in range(2 * n):
        ang = math.radians(rot) + math.pi * i / n
        r = r1 if i % 2 == 0 else r0
        pts.append((x + r * math.cos(ang), y + r * math.sin(ang)))
    c.drawPath(path_of(pts, True), fillp(rgb, a))


def chrome_text(c, s, x, y, size, kind="shrik", a=255, depth=16, side=PURPLE, top=(255, 255, 255), mid=(120, 200, 255),
                low=(255, 120, 200), outline=NAVY):
    """90s chrome logo text: extruded sides, sky-to-sunset chrome face with a horizon line, dark outline."""
    if a <= 1:
        return
    f = font(kind, size)
    wd = f.measureText(s)
    x0 = x - wd / 2
    for k in range(depth, 0, -1):
        c.drawString(s, x0 + k * 0.6, y + k, f, fillp(mix(side, BLACK, 0.4 * k / depth), a))
    op = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=size * 0.08, Color=col(outline, a))
    op.setStrokeJoin(skia.Paint.kRound_Join)
    c.drawString(s, x0, y, f, op)
    asc = size * 0.75
    sh = skia.GradientShader.MakeLinear([(0, y - asc), (0, y)], [col(top, a), col(mid, a), col(NAVY, a), col(low, a), col(top, a)],
                                        [0, 0.48, 0.5, 0.55, 1.0])
    c.drawString(s, x0, y, f, skia.Paint(AntiAlias=True, Shader=sh))


def panel(c, x, y, w, h, rgb, a=255, r=18):
    """Bevelled broadcast panel: gradient face, light top edge, dark bottom edge."""
    c.drawRRect(rrect(x + 10, y + 12, w, h, r), fillp(BLACK, 0.45 * a))
    c.drawRRect(rrect(x, y, w, h, r), grad_v(y, y + h, mix(rgb, WHITE, 0.25), mix(rgb, BLACK, 0.35), a, a))
    c.drawRRect(rrect(x + 4, y + 4, w - 8, h * 0.45, r - 4), fillp(WHITE, 0.12 * a))
    c.drawRRect(rrect(x, y, w, h, r), stroke(mix(rgb, WHITE, 0.6), 4, a))


def purine(c, x, y, s, rgb, a=255, w=7):
    """The double ring at the heart of both caffeine and adenosine (hexagon fused to a pentagon)."""
    hx = x - 0.78 * s                                        # hexagon and pentagon share one vertical edge
    hexa = [(hx + s * math.cos(math.radians(30 + 60 * i)), y + s * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    px = hx + 1.554 * s
    pent = [(px + 0.851 * s * math.cos(math.radians(144 + 72 * i)), y + 0.851 * s * math.sin(math.radians(144 + 72 * i))) for i in range(5)]
    c.drawPath(path_of(hexa, True), stroke(rgb, w, a))
    c.drawPath(path_of(pent, True), stroke(rgb, w, a))
    return hexa, pent


def mug(c, x, y, s, t, a=255, tilt=0.0, face="happy", steam=1.0, body=RED, fill_k=0.85):
    """The mascot: a chunky diner mug with a face and wiggly steam. (x, y) = centre of the mug body."""
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s, s)
    if steam > 0:
        for k in range(3):
            pts = [(-60 + 60 * k + 16 * math.sin(t * 4 + j * 0.8 + k), -170 - j * 22) for j in range(9)]
            c.drawPath(path_of(pts), stroke(WHITE, 12, 0.55 * a * steam * (0.6 + 0.4 * math.sin(t * 2 + k))))
    c.drawRRect(rrect(-150 + 14, -120 + 20, 300, 270, 40), fillp(BLACK, 0.4 * a))
    c.drawPath(path_of([(150, -60), (215, -60), (230, 0), (215, 60), (150, 60)]), stroke(mix(body, BLACK, 0.2), 30, a))
    c.drawRRect(rrect(-150, -120, 300, 270, 40), grad_v(-120, 150, mix(body, WHITE, 0.15), mix(body, BLACK, 0.25), a, a))
    c.drawRect(skia.Rect.MakeLTRB(-150, -40, 150, -12), fillp(WHITE, 0.9 * a))
    c.drawOval(skia.Rect.MakeLTRB(-150, -150, 150, -90), fillp(mix(body, WHITE, 0.5), a))
    c.drawOval(skia.Rect.MakeLTRB(-132, -142, 132, -98), fillp(BROWN, a * fill_k + (1 - fill_k) * 0))
    c.drawOval(skia.Rect.MakeLTRB(-80, -134, 20, -116), fillp(mix(BROWN, WHITE, 0.3), 0.6 * a))
    blink = (t * 0.6 % 1) > 0.93
    ey = 40
    for ex in (-55, 55):
        if face == "sleepy" or blink:
            c.drawLine(ex - 20, ey, ex + 20, ey, stroke(BLACK, 9, a))
        elif face == "wired":
            c.drawCircle(ex, ey, 28, fillp(WHITE, a))
            c.drawCircle(ex, ey, 9, fillp(BLACK, a))
        else:
            c.drawCircle(ex, ey, 15, fillp(BLACK, a))
            c.drawCircle(ex + 5, ey - 5, 5, fillp(WHITE, a))
    if face == "sleepy":
        c.drawLine(-25, 100, 25, 100, stroke(BLACK, 8, a))
    else:
        mp = skia.Path()
        mp.moveTo(-40, 88)
        mp.quadTo(0, 130 if face != "wired" else 140, 40, 88)
        c.drawPath(mp, stroke(BLACK, 9, a))
    c.drawCircle(-95, 85, 18, fillp(PINK, 0.6 * a))
    c.drawCircle(95, 85, 18, fillp(PINK, 0.6 * a))
    c.restore()
