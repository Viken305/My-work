"""BEAT DROP: the rhythm-game engine shared by every level of the full video (part1..part7).

Every spoken word is a note that slides down one of four lanes and hits the line exactly when it is said ("PERFECT"),
then flies up into the caption line. Numbers are merged into one wide gold note ("one hundred and eighty" -> 180).
The music is a four-on-the-floor track at the level's tempo; lights, rungs and the equaliser runner lock to its beat.
A part module builds `G = Game("partN")`, draws its own scene above the highway and hands the rest to G.
"""
from kit import *  # noqa: F401,F403
from script import PARTS as LINES

MAG, CYN, LIME, GOLD = (255, 46, 160), (40, 230, 255), (170, 255, 60), (255, 206, 60)
ORANGE, RED, VIOLET, WHITE = (255, 120, 40), (255, 50, 60), (150, 90, 255), (255, 255, 255)
LANES = [MAG, CYN, LIME, GOLD]
VP_Y, HIT_Y = 1030, 1420
CAP_Y = 985
TRAVEL = 1.05

ORDER = ["part1", "part2", "part3", "part4", "part5", "part6", "part7"]
# per level: card number and name, track tempo and energy, heart rate over the level, timing, stage colours
LEVELS = {
    "part1": dict(num=None, name="PRESS PLAY", bpm=112, energy=1, heart=(72, 88), first=1.0, gap=0.35, tail=0.5, rgb=(MAG, CYN)),
    "part2": dict(num=1, name="IGNITION", bpm=116, energy=2, heart=(88, 118), first=1.55, gap=0.4, tail=0.6, rgb=(GOLD, MAG)),
    "part3": dict(num=2, name="AIR", bpm=120, energy=2, heart=(118, 134), first=1.55, gap=0.4, tail=0.6, rgb=(CYN, VIOLET)),
    "part4": dict(num=3, name="FUEL", bpm=124, energy=3, heart=(134, 150), first=1.55, gap=0.4, tail=0.6, rgb=(LIME, GOLD)),
    "part5": dict(num=4, name="MAX HEART", bpm=128, energy=3, heart=(150, 180), first=1.55, gap=0.45, tail=0.7, rgb=(RED, MAG)),
    "part6": dict(num=5, name="HEAT", bpm=128, energy=3, heart=(176, 168), first=1.55, gap=0.45, tail=0.6, rgb=(ORANGE, RED)),
    "part7": dict(num="B", name="BONUS ROUND", bpm=120, energy=2, heart=(160, 64), first=1.55, gap=0.45, tail=1.4, rgb=(VIOLET, CYN)),
}

# spoken numbers become one gold note: line -> [(words, note text, burst label)]
MERGES = {
    "A3": [("twenty percent", "20%", "AT REST"), ("eighty percent", "80%", "FULL POWER")],
    "B1": [("twelve", "12", "AT REST"), ("forty", "40", "GO GO GO")],
    "B2": [("six litres", "6 L", "AT REST"), ("one hundred", "100 L", "AIR MAX")],
    "C1": [("a t p", "ATP", "FUEL")],
    "D1": [("one hundred and eighty", "180", "MAX POWER")],
    "D2": [("twenty litres", "20 L", "PUMPED"), ("four times", "4X", "COMBO")],
    "E1": [("seventy five percent", "75%", "HEAT")],
    "E2": [("a litre", "1 L", "SWEAT")],
}

def _clean(w):
    return "".join(ch for ch in w.lower() if ch.isalnum() or ch == "'")


def build_notes(part, tm):
    """All notes of a part: dict(t0, t1, text, gold, burst, brk, lane, line)."""
    out = []
    for key, _ in LINES[part]:
        ws = tm.words(key)
        clean = [_clean(w) for _, _, w in ws]
        merges = [(m[0].split(), m[1], m[2]) for m in MERGES.get(key, [])]
        i = 0
        while i < len(ws):
            hit = next((m for m in merges if clean[i:i + len(m[0])] == m[0]), None)
            if hit:
                j = i + len(hit[0]) - 1
                out.append(dict(t0=ws[i][0], t1=ws[j][1], text=hit[1], gold=True, burst=hit[2], brk=ws[j][2][-1] in ",.", line=key))
                merges.remove(hit)
                i = j + 1
                continue
            w = ws[i][2]
            txt = "".join(ch for ch in w.upper() if ch.isalnum() or ch == "'")
            out.append(dict(t0=ws[i][0], t1=ws[i][1], text=txt, gold=False, burst="PERFECT", brk=w[-1] in ",.?!", line=key))
            i += 1
        out[-1]["brk"] = True
    lane = 0
    for n in out:
        n["lane"] = None if n["gold"] else lane
        if not n["gold"]:
            lane = (lane + 1 + (1 if hsh(len(n["text"]), ord(n["text"][0])) > 0.62 else 0)) % 4
    # caption phrases: split at commas and full stops, then balance each stretch into lines of <= 17 characters
    segs, cur = [], []
    for n in out:
        cur.append(n)
        if n["brk"]:
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    ph = []
    for sg in segs:
        ph += _balance(sg)
    for p in ph:
        for n in p:
            n["phrase"] = p
    return out, ph


def _balance(sg, limit=17):
    """Fewest lines that fit, then the most even ones (gold notes are drawn bigger, so they count 1.6x)."""
    from itertools import combinations
    ln = lambda g: sum(len(x["text"]) * (1.6 if x["gold"] else 1) for x in g) + len(g) - 1     # noqa: E731
    if ln(sg) <= limit or len(sg) == 1:
        return [sg]
    for k in range(2, len(sg) + 1):
        best = None
        for cuts in combinations(range(1, len(sg)), k - 1):
            gs = [sg[a:b] for a, b in zip((0,) + cuts, cuts + (len(sg),))]
            if max(ln(g) for g in gs) > limit and k < len(sg):
                continue
            cost = sum(ln(g) ** 2 for g in gs)
            if best is None or cost < best[0]:
                best = (cost, gs)
        if best:
            return best[1]
    return [[n] for n in sg]


def _sched(part):
    L = LEVELS[part]
    vo, _ = schedule(part, first=L["first"], gap=L["gap"])
    tm = Timing(part, vo)
    dur = tm.end(LINES[part][-1][0]) + L["tail"]
    return vo, tm, dur


class Game:
    def __init__(self, part):
        self.part, self.L = part, LEVELS[part]
        self.VO, self.TM, self.DURATION = _sched(part)
        self.notes, self.phrases = build_notes(part, self.TM)
        self.bpm = self.L["bpm"]
        self.c0, self.c1 = self.L["rgb"]
        # where this level sits in the whole video: combo so far, time offset and total length (for the progress bar)
        self.combo0, self.offset, self.total, self.marks = 0, 0.0, 0.0, []
        for p in ORDER:
            if p == part:
                self.offset = self.total
                self.combo0 = sum(len(build_notes(q, _sched(q)[1])[0]) for q in ORDER[:ORDER.index(p)])
            self.marks.append(self.total)
            self.total += _sched(p)[2] if p != part else self.DURATION
        self.heart_fn = None
        self.beat0 = 0.0                 # the track's first kick
        self.flash_t = 0.0 if self.L["num"] is not None else None     # white flash and shake as the level drops in
        self.hud_a = lambda t: 255

    # ------------------------------------------------------------ time
    def phase(self, t):
        return max(0.0, t - self.beat0) * self.bpm / 60

    def beat(self, t):
        ph = self.phase(t) % 1.0
        return math.exp(-ph * 9)

    def heart(self, t):
        if self.heart_fn:
            return self.heart_fn(t)
        h0, h1 = self.L["heart"]
        return lerp(h0, h1, in_out(prog(t, 0.8, self.DURATION - 0.5)))

    def w(self, key, phrase, end=False):
        return self.TM.word(key, phrase, end)

    # ------------------------------------------------------------ the stage
    def stage(self, c, t, dim=0.0):
        c.drawPaint(fillp((6, 2, 14)))
        c.drawRect(skia.Rect.MakeWH(W, H), grad_v(0, H, mix((6, 2, 14), self.c0, 0.10), (4, 2, 10)))
        bt = self.beat(t)
        for k, (x0, rgb) in enumerate(((110, self.c0), (970, self.c1))):      # stage lights swing on the beat
            ang = math.radians(90 + (1 if k else -1) * (16 + 16 * math.sin(self.phase(t) * math.pi / 2)))
            Ln = 1500
            tip = (x0 + math.cos(ang) * Ln, 150 + math.sin(ang) * Ln)
            side = (math.cos(ang + math.pi / 2) * 170, math.sin(ang + math.pi / 2) * 170)
            beam = path_of([(x0, 150), (tip[0] + side[0], tip[1] + side[1]), (tip[0] - side[0], tip[1] - side[1])], True)
            bp = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(x0, 150), skia.Point(*tip)],
                            [skia.Color(*rgb, int((60 + 60 * bt) * (1 - dim))), skia.Color(*rgb, 0)]), BlendMode=skia.BlendMode.kPlus)
            bp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 20))
            c.drawPath(beam, bp)
        # the highway
        c.drawPath(path_of([(lane_x(-1, VP_Y), VP_Y), (lane_x(1, VP_Y), VP_Y), (lane_x(1.12, HIT_Y + 200), HIT_Y + 200),
                            (lane_x(-1.12, HIT_Y + 200), HIT_Y + 200)], True), grad_v(VP_Y, HIT_Y + 200, (14, 6, 30), (26, 10, 50), 230, 255))
        for u in (-1, -0.5, 0, 0.5, 1):
            c.drawLine(lane_x(u, VP_Y), VP_Y, lane_x(u * 1.12, HIT_Y + 200), HIT_Y + 200,
                       stroke(mix((90, 60, 160), self.c0, 0.3 * (abs(u) == 1)), 3 if abs(u) < 1 else 7, 210))
        for i in range(12):                                # rungs scroll toward you on the beat
            d = (i / 12 + self.phase(t) * 0.25) % 1
            y = VP_Y + (HIT_Y - VP_Y) * d ** 1.6
            c.drawLine(lane_x(-1, y), y, lane_x(1, y), y, stroke((80, 50, 150), 2, 170 * d))
        c.drawLine(lane_x(-1.05, HIT_Y), HIT_Y, lane_x(1.05, HIT_Y), HIT_Y, stroke(WHITE, 6))
        light(c, 540, HIT_Y, 520, mix((200, 160, 255), self.c0, 0.3), 50 + 60 * bt)
        for lane in range(4):
            x = lane_x(-0.75 + 0.5 * lane, HIT_Y)
            press = max([1 - prog(t, n["t0"], n["t0"] + 0.18) for n in self.notes if n["lane"] == lane and n["t0"] <= t] + [0])
            c.drawCircle(x, HIT_Y, 34 + 6 * press, stroke(LANES[lane], 6, 220))
            if press > 0:
                c.drawCircle(x, HIT_Y, 30, fillp(LANES[lane], 200 * press))

    # ------------------------------------------------------------ notes, bursts and the caption line
    def draw_notes(self, c, t):
        fx = []
        for n in self.notes:
            d = 1 - (n["t0"] - t) / TRAVEL
            rgb = GOLD if n["gold"] else LANES[n["lane"]]
            if 0 <= d < 1:
                x, y, sc = note_pos(d, n["lane"])
                gem(c, x, y, sc, n["text"], rgb, 255 * smooth(prog(d, 0, 0.12)), n["gold"])
            elif d >= 1 and t - n["t0"] < 0.5:
                fx.append(n)
        for n in fx:
            u = prog(t, n["t0"], n["t0"] + 0.45)
            x, y, _ = note_pos(1.0, n["lane"])
            rgb = GOLD if n["gold"] else LANES[n["lane"]]
            k = 2 if n["gold"] else 1
            c.drawCircle(x, y, 40 + 160 * out_cubic(u) * k, stroke(rgb, 10 * (1 - u) + 1, 255 * (1 - u)))
            light(c, x, y, 260 * (1 - u) * k + 60, rgb, 200 * (1 - u))
            for j in range(10 + 8 * (k - 1)):
                a = j / (10 + 8 * (k - 1)) * 2 * math.pi + n["t0"]
                r = 60 + 220 * out_cubic(u) * k
                c.drawCircle(x + math.cos(a) * r, y + math.sin(a) * r * 0.6, 7 * (1 - u) * k, fillp(rgb))
            outlined(c, n["burst"], x, y - 70 - 60 * u, 30 if not n["gold"] else 50, "bungee", WHITE, 255 * (1 - u), glow_rgb=rgb)

    def caption(self, c, t):
        cur = None
        for p in self.phrases:
            if p[0]["t0"] <= t:
                cur = p
        if cur is None:
            return
        i = self.phrases.index(cur)
        nxt = self.phrases[i + 1][0]["t0"] if i + 1 < len(self.phrases) else 1e9
        t_out = min(nxt, cur[-1]["t1"] + 1.0)
        out = smooth(prog(t, t_out - 0.12, t_out))
        if out >= 1:
            return
        sizes = [(136 if n["gold"] else 84) for n in cur]
        ws = [width(n["text"], "bungee", s) for n, s in zip(cur, sizes)]
        total = sum(ws) + 28 * (len(cur) - 1)
        fit = min(1.0, 960 / total)
        x = 540 - total * fit / 2
        for n, s, w in zip(cur, sizes, ws):
            if t >= n["t0"]:
                u = prog(t, n["t0"], n["t0"] + 0.22)
                hx, hy, _ = note_pos(1.0, n["lane"])
                tx, ty = x + w * fit / 2, CAP_Y
                px, py = lerp(hx, tx, out_cubic(u)), lerp(hy, ty, out_cubic(u)) - 120 * math.sin(math.pi * u)
                sc = lerp(0.6, 1.0, out_back(u, 2)) * (1 - 0.3 * out) * fit
                rgb = GOLD if n["gold"] else WHITE
                c.save()
                c.translate(px, py - 30)
                c.scale(sc, sc)
                outlined(c, n["text"], 0, 30, s, "bungee", rgb, 255 * (1 - out), glow_rgb=GOLD if n["gold"] else MAG)
                c.restore()
            x += (w + 28) * fit

    # ------------------------------------------------------------ HUD
    def hud(self, c, t, a=255):
        if a <= 1:
            return
        bt = self.beat(t)
        label(c, "HEART BPM", 72, 236, 30, "bungee", MAG, a)
        c.save()
        c.translate(72, 344)
        c.scale(1 + 0.05 * bt, 1 + 0.05 * bt)
        outlined(c, f"{int(round(self.heart(t))):03d}", 0, 0, 112, "bungee", WHITE, a, "left", glow_rgb=MAG)
        c.restore()
        combo = self.combo0 + sum(1 for n in self.notes if n["t0"] <= t)
        label(c, "COMBO", 1008, 236, 30, "bungee", CYN, a, "right")
        pop = max([1 - prog(t, n["t0"], n["t0"] + 0.15) for n in self.notes if n["t0"] <= t] + [0])
        c.save()
        c.translate(1008, 334)
        c.scale(1 + 0.12 * pop, 1 + 0.12 * pop)
        outlined(c, f"x{combo}", 0, 0, 86, "bungee", CYN, a, "right", glow_rgb=CYN)
        c.restore()
        # song progress along the top, with a tick for every level
        x0, x1, y = 72, 1008, 164
        c.drawRRect(rrect(x0, y - 5, x1 - x0, 10, 5), fillp((60, 40, 90), a))
        u = (self.offset + t) / self.total
        c.drawRRect(rrect(x0, y - 5, (x1 - x0) * clamp(u), 10, 5), fillp(self.c0, a))
        for m in self.marks[1:]:
            c.drawCircle(x0 + (x1 - x0) * m / self.total, y, 9, fillp(WHITE if m <= self.offset + t else (90, 70, 120), a))
        light(c, x0 + (x1 - x0) * clamp(u), y, 40, self.c0, a * 0.8)
        num = self.L["num"]
        tag = self.L["name"] if num is None else f"LV {num} · {self.L['name']}" if num != "B" else self.L["name"]
        label(c, tag, 540, 128, 26, "mono_bold", mix(self.c0, WHITE, 0.4), a * 0.9, "center", tracking=0.12)

    def level_card(self, c, t):
        """LEVEL N slams in at the start of the level (t 0.1 .. 1.35)."""
        if self.L["num"] is None or t > 1.45:
            return
        a = 255 * (1 - smooth(prog(t, 1.15, 1.42)))
        u = prog(t, 0.08, 0.34)
        sc = lerp(2.4, 1.0, out_expo(u))
        x, y = 540, 600 - 140 * in_cubic(prog(t, 1.15, 1.42))
        c.drawRect(skia.Rect.MakeXYWH(0, y - 210, W, 330), fillp((0, 0, 0), 0.55 * a * smooth(prog(t, 0.05, 0.2))))
        for k, rgb in enumerate((self.c0, self.c1)):       # two colour bars wipe across
            v = out_cubic(prog(t, 0.05 + 0.06 * k, 0.4 + 0.06 * k))
            yy = y - 200 + k * 300
            c.drawRect(skia.Rect.MakeXYWH(W * (1 - v) if k else 0, yy, W * v, 10), fillp(rgb, a))
        c.save()
        c.translate(x, y)
        c.scale(sc, sc)
        top = "LEVEL " + str(self.L["num"]) if self.L["num"] != "B" else "BONUS LEVEL"
        outlined(c, top, 0, -40, 96, "bungee", WHITE, a * smooth(u * 3), glow_rgb=self.c0)
        c.restore()
        v = out_back(prog(t, 0.34, 0.62), 2)
        if v > 0:
            name = self.L["name"] if self.L["num"] != "B" else "REWARD"
            c.save()
            c.translate(x, y + 70)
            c.scale(v, v)
            outlined(c, name, 0, 0, 120 if len(name) < 8 else 104, "bungee_shade", self.c0, a, glow_rgb=self.c0)
            c.restore()

    # ------------------------------------------------------------ a whole frame
    def frame(self, c, t, scene, scene_a=None):
        sx, sy = shake(t, self.flash_t + 0.12, 14, 7) if self.flash_t is not None else (0, 0)
        c.save()
        c.translate(sx, sy)
        self.stage(c, t)
        a = scene_a if scene_a is not None else (255 * smooth(prog(t, 0.9, 1.35)) if self.L["num"] is not None else 255)
        if a > 1:
            if a < 255:
                c.saveLayerAlpha(None, int(a))
            scene(c, t)
            if a < 255:
                c.restore()
        self.draw_notes(c, t)
        self.hud(c, t, self.hud_a(t))
        self.level_card(c, t)
        c.restore()
        if self.flash_t is not None and t >= self.flash_t:
            k = 1 - smooth(prog(t, self.flash_t, self.flash_t + 0.3))
            if k > 0:
                c.drawPaint(fillp(mix(self.c0, WHITE, 0.6), 200 * k))

    def overlay(self, c, t):
        if t < self.DURATION - 0.05:
            self.caption(c, t)

    def post(self, t):
        return dict(grain=3.5, ca=1.2, bloom=1.1)

    # ------------------------------------------------------------ sound
    def sfx(self):
        ev = []
        if self.L["num"] is not None:
            ev += [(0.1, "low_hit", 0.7), (0.34, "swish", 0.4)]
        for n in self.notes:
            ev.append((n["t0"], "trailer_hit" if n["gold"] else "note_hit", 0.55 if n["gold"] else 0.32))
        return ev

    def music(self):
        return dict(beds=[(0.0, self.DURATION, f"drive{self.bpm}_{self.L['energy']}", 0.6)])


# ---------------------------------------------------------------- geometry and pieces
def lane_x(u, y):
    """u in -1..1 across the highway; perspective from the vanishing line to the hit line."""
    k = (y - VP_Y) / (HIT_Y - VP_Y)
    return 540 + u * lerp(110, 440, k)


def note_pos(d, lane):
    y = VP_Y + (HIT_Y - VP_Y) * d ** 1.6
    u = -0.75 + 0.5 * lane if lane is not None else 0.0
    return lane_x(u, y), y, lerp(0.35, 1.0, d ** 1.2)


def gem(c, x, y, sc, text, rgb, a=255, gold=False):
    if a <= 1:
        return
    size = (64 if not gold else 116) * sc
    w = width(text, "bungee", size) + 46 * sc
    h = size * 1.25
    if gold:
        w = max(w, 600 * sc)
    light(c, x, y, w * 0.8, rgb, 90 * a / 255)
    c.drawRRect(rrect(x - w / 2, y - h / 2, w, h, h * 0.35), fillp(mix(rgb, (0, 0, 0), 0.75), a))
    c.drawRRect(rrect(x - w / 2, y - h / 2, w, h, h * 0.35), stroke(rgb, 5 * sc + 1, a))
    c.drawRRect(rrect(x - w / 2 + 6 * sc, y - h / 2 + 5 * sc, w - 12 * sc, h * 0.32, h * 0.2), fillp(WHITE, 40 * a / 255))
    label(c, text, x, y + size * 0.36, size, "bungee", mix(rgb, WHITE, 0.55), a, "center")


def _inside(x, y):
    def cap(ax, ay, bx, by, r):
        vx, vy = bx - ax, by - ay
        u = clamp(((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy))
        return math.hypot(x - ax - u * vx, y - ay - u * vy) < r
    return (math.hypot(x - 575, y - 455) < 62 or cap(560, 520, 530, 740, 62) or      # head, torso (leaning in)
            cap(545, 560, 640, 640, 26) or cap(640, 640, 720, 580, 24) or              # front arm, punching forward
            cap(545, 565, 450, 640, 26) or cap(450, 640, 400, 720, 24) or              # back arm
            cap(530, 740, 640, 800, 34) or cap(640, 800, 620, 920, 30) or              # front leg, knee up
            cap(520, 740, 450, 840, 34) or cap(450, 840, 360, 900, 30))                # back leg, push-off


COLS = []
for _cx in range(330, 780, 13):
    _spans, _in, _y0 = [], False, 0
    for _y in range(380, 960, 4):
        _v = _inside(_cx, _y)
        if _v and not _in:
            _y0, _in = _y, True
        elif not _v and _in:
            _spans.append((_y0, _y))
            _in = False
    if _in:
        _spans.append((_y0, 960))
    if _spans:
        COLS.append((_cx, _spans))
RUN_C = (555, 670)        # centre of the runner drawing


def runner(c, g, t, x=540, y=670, s=1.0, a=255, level=None, rgb0=CYN, rgb1=MAG, heart=True, heat=0.0, assemble=1.0):
    """The equaliser runner. level(t) overrides how high the bars ride; heat (0..1) turns the bars to fire;
    assemble (0..1) flies the bars in from below."""
    if a <= 1:
        return
    bt = g.beat(t)
    c.save()
    c.translate(x, y + 10 * math.sin(g.phase(t) * math.pi) ** 2 * s)
    c.scale(s, s)
    c.translate(-RUN_C[0], -RUN_C[1])
    lay = a < 255
    if lay:
        c.saveLayerAlpha(None, int(a))
    for i, (cx, spans) in enumerate(COLS):
        base = level(t) if level else 0.35
        lvl = clamp(base + (1 - base) * (bt * (0.55 + 0.45 * hsh(i, int(g.phase(t)))) + 0.25 * math.sin(t * 9 + i * 0.7) ** 2))
        k = clamp(assemble * 1.6 - hsh(i, 7) * 0.6)
        dy = (1 - out_cubic(k)) * (700 + 300 * hsh(i, 3))
        if k <= 0:
            continue
        col_ = mix(rgb0, rgb1, (cx - 330) / 450)
        if heat > 0:
            col_ = mix(col_, mix(ORANGE, GOLD, hsh(i, 5)), heat)
        for y0, y1 in spans:
            c.drawLine(cx, y0 + 2 + dy, cx, y1 - 2 + dy, stroke((60, 40, 90), 9, 255, cap=skia.Paint.kButt_Cap))
            top = lerp(y1, y0, lvl)
            c.drawLine(cx, y1 - 2 + dy, cx, top + dy, stroke(col_, 9, 255, cap=skia.Paint.kButt_Cap))
            c.drawLine(cx, y1 - 2 + dy, cx, top + dy, stroke(col_, 18, 50, plus=True, cap=skia.Paint.kButt_Cap))
    if heart and assemble >= 1:
        hx, hy = 540, 610                                  # the heart is a speaker cone
        pulse = 1 + 0.22 * bt
        for k, r in enumerate((54, 38, 22)):
            c.drawCircle(hx, hy, r * pulse, stroke(MAG if k != 1 else WHITE, 7, 255))
        c.drawCircle(hx, hy, 10 * pulse, fillp(WHITE))
        light(c, hx, hy, 220 * pulse, MAG, 160 * bt + 40)
        for k in range(3):                                 # sound rings
            u = (g.phase(t) + k / 3) % 1
            c.drawCircle(hx, hy, 60 + 260 * u, stroke(MAG, 4, 140 * (1 - u)))
    if lay:
        c.restore()
    c.restore()


# ---------------------------------------------------------------- scene helpers
def appear(t, t0, d=0.35):
    return out_back(prog(t, t0, t0 + d), 1.8)


def chip(c, x, y, title, value, rgb, a=255, align="center", size=72):
    """A stat readout: small title over a big glowing value, on a dark pill."""
    if a <= 1:
        return
    w = max(width(value, "bungee", size), width(title, "mono_bold", 26, 0.1)) + 60
    x0 = x - w / 2 if align == "center" else x if align == "left" else x - w
    c.drawRRect(rrect(x0, y - size - 60, w, size + 92, 26), fillp((8, 4, 20), 0.82 * a))
    c.drawRRect(rrect(x0, y - size - 60, w, size + 92, 26), stroke(rgb, 4, a))
    label(c, title, x0 + w / 2, y - size - 20, 26, "mono_bold", mix(rgb, WHITE, 0.3), a, "center", tracking=0.1)
    outlined(c, value, x0 + w / 2, y + 10, size, "bungee", WHITE, a, glow_rgb=rgb)


def fader(c, x, y0, y1, v, rgb, name, a=255, val=None):
    """A mixing-desk fader: track, lit level bar, cap and name."""
    c.drawRRect(rrect(x - 9, y0, 18, y1 - y0, 9), fillp((30, 20, 50), a))
    top = lerp(y1, y0, clamp(v))
    c.drawRRect(rrect(x - 9, top, 18, y1 - top, 9), fillp(rgb, a))
    c.drawRRect(rrect(x - 9, top, 18, y1 - top, 9), stroke(rgb, 22, 0.2 * a, plus=True))
    c.drawRRect(rrect(x - 44, top - 18, 88, 36, 10), fillp((235, 235, 245), a))
    c.drawLine(x - 30, top, x + 30, top, stroke(rgb, 5, a))
    label(c, name, x, y1 + 46, 26, "mono_bold", mix(rgb, WHITE, 0.4), a, "center", tracking=0.06)
    if val is not None:
        label(c, val, x, top - 34, 34, "bungee", WHITE, a, "center")


def zap(c, pts, t, rgb, a=255, seed=0, w=6):
    """A jittering lightning line along pts."""
    q = []
    for i, (x, y) in enumerate(pts):
        j = 0 if i in (0, len(pts) - 1) else 18
        q.append((x + (hsh(i, seed, int(t * 20)) - 0.5) * j, y + (hsh(i, seed + 1, int(t * 20)) - 0.5) * j))
    p = path_of(q)
    c.drawPath(p, stroke(rgb, w * 3, 0.25 * a, plus=True))
    c.drawPath(p, stroke(WHITE, w, a))
