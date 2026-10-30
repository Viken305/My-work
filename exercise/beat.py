"""Style B · BEAT DROP. Your workout as a rhythm game. A runner made entirely of equaliser bars pulses to the heart
rate; the heart is a speaker cone; stage lights swing on the beat.
Captions: every spoken word slides down a note lane and hits the line exactly when it is said ("PERFECT"), then gets
thrown up into the caption line. Big numbers arrive as one wide gold note ("180").

  python3 render.py beat [--still 2,4]
"""
from kit import *  # noqa: F401,F403

PART = "beat"
VO, _end = schedule(PART, first=1.3, gap=0.5)        # the first notes need time to travel down the lanes
TM = Timing(PART, VO)
DURATION = _end + 1.2

MAG, CYN, LIME, GOLD = (255, 46, 160), (40, 230, 255), (170, 255, 60), (255, 206, 60)
LANES = [MAG, CYN, LIME, GOLD]
VP_Y, HIT_Y = 1030, 1420
TRAVEL = 1.05
RAMP_T0, RAMP_T1 = 0.6, TM.end("B")


def bpm(t):
    return 72 + 108 * in_out(prog(t, RAMP_T0, RAMP_T1))


def beat_phase(t):
    ts = np.linspace(0, max(t, 1e-3), 160)
    trap = getattr(np, "trapezoid", None) or np.trapz
    return float(trap([bpm(x) / 60 for x in ts], ts))


def beat(t):
    ph = beat_phase(t) % 1.0
    return math.exp(-ph * 10) + (0.55 * math.exp(-(ph - 0.2) * 12) if ph > 0.2 else 0)


# ---------------------------------------------------------------- notes from the narration
def build_notes():
    ws = TM.words("B")
    out, i = [], 0
    clean = [w.strip(",.").lower() for _, _, w in ws]
    while i < len(ws):
        if clean[i:i + 4] == ["one", "hundred", "and", "eighty"]:
            out.append(dict(t0=ws[i][0], text="180", gold=True, comma=False))
            i += 4
            continue
        out.append(dict(t0=ws[i][0], text=ws[i][2].strip(",.").upper(), gold=False, comma=ws[i][2].endswith(",")))
        i += 1
    lane = 0
    for n in out:
        n["lane"] = None if n["gold"] else lane
        if not n["gold"]:
            lane = (lane + 1 + (1 if hsh(len(n["text"]), 3) > 0.6 else 0)) % 4
    # phrases for the caption line (max ~17 characters, break after commas, big numbers on their own)
    ph, cur = [], []
    for n in out:
        if cur and (len(" ".join(x["text"] for x in cur + [n])) > 17 or cur[-1]["gold"] or cur[-1]["comma"] or n["gold"]):
            ph.append(cur)
            cur = []
        cur.append(n)
    ph.append(cur)
    for pi, p in enumerate(ph):
        for n in p:
            n["phrase"] = pi
    return out, ph


NOTES, PHRASES = build_notes()


def lane_x(u, y):
    """u in -1..1 across the highway; perspective from the vanishing line to the hit line."""
    k = (y - VP_Y) / (HIT_Y - VP_Y)
    return 540 + u * lerp(110, 440, k)


def note_pos(d, lane):
    y = VP_Y + (HIT_Y - VP_Y) * d ** 1.6
    u = -0.75 + 0.5 * lane if lane is not None else 0.0
    return lane_x(u, y), y, lerp(0.35, 1.0, d ** 1.2)


def gem(c, x, y, sc, text, rgb, a=255, gold=False):
    size = (64 if not gold else 120) * sc
    w = width(text, "bungee", size) + 46 * sc
    h = size * 1.25
    if gold:
        w = max(w, 680 * sc)
    light(c, x, y, w * 0.8, rgb, 90 * a / 255)
    c.drawRRect(rrect(x - w / 2, y - h / 2, w, h, h * 0.35), fillp(mix(rgb, (0, 0, 0), 0.75), a))
    c.drawRRect(rrect(x - w / 2, y - h / 2, w, h, h * 0.35), stroke(rgb, 5 * sc + 1, a))
    c.drawRRect(rrect(x - w / 2 + 6 * sc, y - h / 2 + 5 * sc, w - 12 * sc, h * 0.32, h * 0.2), fillp((255, 255, 255), 40 * a / 255))
    label(c, text, x, y + size * 0.36, size, "bungee", mix(rgb, (255, 255, 255), 0.55), a, "center")


# ---------------------------------------------------------------- the equaliser runner
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
for cx in range(330, 780, 13):
    spans, inside, y0 = [], False, 0
    for y in range(380, 960, 4):
        v = _inside(cx, y)
        if v and not inside:
            y0, inside = y, True
        elif not v and inside:
            spans.append((y0, y))
            inside = False
    if inside:
        spans.append((y0, 960))
    if spans:
        COLS.append((cx, spans))


def runner(c, t):
    bt = beat(t)
    for i, (cx, spans) in enumerate(COLS):
        lvl = clamp(0.35 + 0.65 * (bt * (0.55 + 0.45 * hsh(i, int(beat_phase(t)))) + 0.25 * math.sin(t * 9 + i * 0.7) ** 2))
        for y0, y1 in spans:
            c.drawLine(cx, y0 + 2, cx, y1 - 2, stroke((60, 40, 90), 9, 255, cap=skia.Paint.kButt_Cap))
            top = lerp(y1, y0, lvl)
            col_ = mix(CYN, MAG, (cx - 330) / 450)
            c.drawLine(cx, y1 - 2, cx, top, stroke(col_, 9, 255, cap=skia.Paint.kButt_Cap))
            c.drawLine(cx, y1 - 2, cx, top, stroke(col_, 18, 50, plus=True, cap=skia.Paint.kButt_Cap))
    hx, hy = 540, 610                                  # the heart is a speaker cone
    pulse = 1 + 0.22 * bt
    for k, r in enumerate((54, 38, 22)):
        c.drawCircle(hx, hy, r * pulse, stroke(MAG if k != 1 else (255, 255, 255), 7, 255))
    c.drawCircle(hx, hy, 10 * pulse, fillp((255, 255, 255)))
    light(c, hx, hy, 220 * pulse, MAG, 160 * bt + 40)
    for k in range(3):                                 # sound rings
        u = (beat_phase(t) + k / 3) % 1
        c.drawCircle(hx, hy, 60 + 260 * u, stroke(MAG, 4, 140 * (1 - u)))


def stage(c, t):
    c.drawPaint(fillp((6, 2, 14)))
    bt = beat(t)
    for k, (x0, rgb) in enumerate(((120, CYN), (960, MAG))):      # stage lights swing on the beat
        ang = math.radians(90 + (1 if k else -1) * (18 + 14 * math.sin(beat_phase(t) * math.pi)))
        L = 1500
        tip = (x0 + math.cos(ang) * L, 200 + math.sin(ang) * L)
        side = (math.cos(ang + math.pi / 2) * 170, math.sin(ang + math.pi / 2) * 170)
        beam = path_of([(x0, 200), (tip[0] + side[0], tip[1] + side[1]), (tip[0] - side[0], tip[1] - side[1])], True)
        bp = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(x0, 200), skia.Point(*tip)],
                        [skia.Color(*rgb, int(70 + 60 * bt)), skia.Color(*rgb, 0)]), BlendMode=skia.BlendMode.kPlus)
        bp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 20))
        c.drawPath(beam, bp)
    # the highway
    for u in (-1, -0.5, 0, 0.5, 1):
        c.drawLine(lane_x(u, VP_Y), VP_Y, lane_x(u, HIT_Y + 120), HIT_Y + 120, stroke((90, 60, 160), 3 if abs(u) < 1 else 6, 200))
    for i in range(10):                                # rungs scrolling toward you
        d = (i / 10 + beat_phase(t) * 0.25) % 1
        y = VP_Y + (HIT_Y - VP_Y) * d ** 1.6
        c.drawLine(lane_x(-1, y), y, lane_x(1, y), y, stroke((70, 40, 130), 2, 160 * d))
    c.drawLine(lane_x(-1.05, HIT_Y), HIT_Y, lane_x(1.05, HIT_Y), HIT_Y, stroke((255, 255, 255), 6))
    light(c, 540, HIT_Y, 500, (200, 160, 255), 60 + 60 * bt)
    for lane in range(4):
        x = lane_x(-0.75 + 0.5 * lane, HIT_Y)
        c.drawCircle(x, HIT_Y, 34, stroke(LANES[lane], 6, 220))


def notes(c, t):
    hit_fx = []
    for n in NOTES:
        d = 1 - (n["t0"] - t) / TRAVEL
        rgb = GOLD if n["gold"] else LANES[n["lane"]]
        if 0 <= d < 1:
            x, y, sc = note_pos(d, n["lane"])
            gem(c, x, y, sc, n["text"], rgb, 255, n["gold"])
        elif d >= 1 and t - n["t0"] < 0.5:
            hit_fx.append(n)
    for n in hit_fx:                                   # PERFECT burst on the hit line
        u = prog(t, n["t0"], n["t0"] + 0.45)
        x, y, _ = note_pos(1.0, n["lane"])
        rgb = GOLD if n["gold"] else LANES[n["lane"]]
        c.drawCircle(x, y, 40 + 160 * out_cubic(u) * (2 if n["gold"] else 1), stroke(rgb, 10 * (1 - u) + 1, 255 * (1 - u)))
        light(c, x, y, 260 * (1 - u) + 60, rgb, 200 * (1 - u))
        for k in range(10):
            a = k / 10 * 2 * math.pi + n["t0"]
            r = 60 + 220 * out_cubic(u)
            c.drawCircle(x + math.cos(a) * r, y + math.sin(a) * r * 0.6, 7 * (1 - u), fillp(rgb))
        word = "PERFECT" if not n["gold"] else "MAX POWER"
        outlined(c, word, x, y - 70 - 60 * u, 30 if not n["gold"] else 52, "bungee", (255, 255, 255), 255 * (1 - u), glow_rgb=rgb)


def caption_line(c, t):
    """The words that have been hit fly up into the line above the highway."""
    cur = None
    for pi, p in enumerate(PHRASES):
        if p[0]["t0"] <= t:
            cur = pi
    if cur is None:
        return
    p = PHRASES[cur]
    nxt = PHRASES[cur + 1][0]["t0"] if cur + 1 < len(PHRASES) else 1e9
    out = smooth(prog(t, nxt - 0.12, nxt))
    sizes = [(140 if n["gold"] else 84) for n in p]
    ws = [width(n["text"], "bungee", s) for n, s in zip(p, sizes)]
    total = sum(ws) + 28 * (len(p) - 1)
    x = 540 - total / 2
    for n, s, w in zip(p, sizes, ws):
        if t < n["t0"]:
            x += w + 28
            continue
        u = prog(t, n["t0"], n["t0"] + 0.22)
        hx, hy, _ = note_pos(1.0, n["lane"])
        tx, ty = x + w / 2, 985
        px, py = lerp(hx, tx, out_cubic(u)), lerp(hy, ty, out_cubic(u)) - 120 * math.sin(math.pi * u)
        sc = lerp(0.6, 1.0, out_back(u, 2)) * (1 - 0.3 * out)
        rgb = GOLD if n["gold"] else (255, 255, 255)
        c.save()
        c.translate(px, py - 30)
        c.scale(sc, sc)
        outlined(c, n["text"], 0, 30, s, "bungee", rgb, 255 * (1 - out), glow_rgb=GOLD if n["gold"] else MAG)
        c.restore()
        x += w + 28


def hud(c, t):
    label(c, "BPM", 72, 230, 34, "bungee", MAG, 255)
    v = f"{int(bpm(t)):03d}"
    bt = beat(t)
    c.save()
    c.translate(72, 340)
    c.scale(1 + 0.05 * bt, 1 + 0.05 * bt)
    outlined(c, v, 0, 0, 120, "bungee", (255, 255, 255), 255, "left", glow_rgb=MAG)
    c.restore()
    combo = sum(1 for n in NOTES if n["t0"] <= t)
    label(c, "COMBO", 1008, 230, 30, "bungee", CYN, 255, "right")
    outlined(c, f"x{combo}", 1008, 330, 90, "bungee", CYN, 255, "right", glow_rgb=CYN)


def draw_frame(c, t):
    stage(c, t)
    runner(c, t)
    notes(c, t)
    hud(c, t)
    style_tag(c, t, "STYLE B · BEAT DROP", DURATION)
    k = max(1 - smooth(prog(t, 0, 0.3)), smooth(prog(t, DURATION - 0.25, DURATION)))
    if k > 0:
        c.drawPaint(fillp((0, 0, 0), 255 * k))


def OVERLAY(c, t):
    if t < DURATION - 0.25:
        caption_line(c, t)


def POST(t):
    return dict(grain=3.5, ca=1.2, bloom=1.1)


def sfx_events():
    ev = [(0.0, "riser", 0.4)]
    tt = 0.3
    while tt < DURATION:
        ev.append((tt, "kick", 0.8))
        tt += 60 / bpm(tt)
    for n in NOTES:
        ev.append((n["t0"], "trailer_hit" if n["gold"] else "note_hit", 0.8 if n["gold"] else 0.5))
    return ev


MUSIC = dict(beds=[(0.0, DURATION, "synthwave", 0.55)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
