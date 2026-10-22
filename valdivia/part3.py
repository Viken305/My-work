"""Part 3: how big. The seismograph drum goes wild for ~10 minutes (stopwatch), then 9.5 on the scale, 32x per step
as squares (area = energy), and the Haiti 2010 dot inside the 9.5 square with a counter to ~5,800x."""
from common import *  # noqa: F401,F403
from frames import _row

PART = "part3"
VO, _end = schedule(PART, first=0.7, gap=0.6, extra={"B2": 0.9, "B3": 0.4})
TM = Timing(PART, VO)
T_SHOOK = TM.word("B1", "shook")
T_10 = TM.word("B1", "ten")
T_95 = TM.word("B2", "nine")
T_STEP = TM.word("B2", "every")
T_32 = TM.word("B2", "thirty")
T_THOU = TM.word("B3", "thousands")
T_HAITI = TM.word("B3", "haiti's")
DURATION = _end + 1.0
T_DRUM_OUT = VO["B2"] - 0.5
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"valdivia": RED, "minutes": RED, "haiti's": INK}))

TOP, BOT, ROWS, Q_ROW, Q_U = 450, 1250, 15, 4, 0.36
GAP = (BOT - TOP) / (ROWS - 1)
P0, P1 = Q_ROW + Q_U - 0.25, Q_ROW + Q_U + 5.25


def pen_pos(t):
    """Pen position in rows (row index + fraction): races through ~10 minutes of record during part 3's first line."""
    return P0 + (P1 - P0) * in_out(prog(t, 0.15, T_DRUM_OUT - 0.2))


def minutes(t):
    return clamp((pen_pos(t) - Q_ROW - Q_U) * 2, 0, 10)


def shake(t):
    m = minutes(t)
    return 0.0 if t > T_DRUM_OUT + 0.3 else (0.9 * math.exp(-m / 5.5) if pen_pos(t) > Q_ROW + Q_U else 0.0)


def drum(c, t):
    paper(c, grid=False)
    drum_r = skia.Rect.MakeLTRB(0, TOP - 40, W, BOT + 40)
    sh = skia.GradientShader.MakeLinear([(0, TOP - 40), (0, BOT + 40)],
                                        [col(SHADE), col(WHITE), col(BONE), col(SEPIA)], [0, 0.3, 0.72, 1])
    c.drawRect(drum_r, skia.Paint(Shader=sh))
    c.drawRect(skia.Rect.MakeLTRB(0, TOP - 60, W, TOP - 40), paint(SHADOW, 60, sigma=10))
    c.drawRect(skia.Rect.MakeLTRB(0, BOT + 40, W, BOT + 70), paint(SHADOW, 90, sigma=12))
    for y in range(TOP - 30, BOT + 40, 12):
        c.drawLine(0, y, W, y, paint(SEPIA, 40, stroke=1.0))
    for x in range(120, W, 60):
        c.drawLine(x, TOP - 40, x, BOT + 40, paint(SEPIA, 55, stroke=1.0))
    p = pen_pos(t)
    now_row, now_u = int(p), p - int(p)
    x0, w = 110, 950
    c.save()
    c.clipRect(drum_r)
    for r in range(ROWS):
        y = TOP + r * GAP
        hh, mm = divmod(15 * 60 + 11 + (r - Q_ROW) * 2, 60)
        label(c, f"{hh:02d}:{mm:02d}", 24, y + 6, 17, "mono", RED if Q_ROW <= r <= now_row else INK, 190)
        if r > now_row:
            c.drawLine(x0, y, x0 + w, y, paint(SEPIA, 70, stroke=1.0))
            continue
        end = now_u if r == now_row else 1.0
        if r < Q_ROW:
            ink(c, _row(x0, y, w, lambda u: 3.0, r, 0, end), INK, 230, 1.3, 0.5)
            continue
        if r == Q_ROW:
            ink(c, _row(x0, y, w, lambda u: 3.0, r, 0, min(end, Q_U + 0.002)), INK, 230, 1.3, 0.5)
            if end > Q_U:
                amp = lambda u: 3 + 60 * smooth(prog(u, Q_U, Q_U + 0.02)) + 150 * smooth(prog(u, Q_U + 0.22, Q_U + 0.25))
                glow(c, _row(x0, y, w, amp, r, Q_U, end), RED, 235, 1.6, 0.35)
            continue
        k = r - Q_ROW
        amp = lambda u, k=k: 190 * math.exp(-(k + u) * 0.3) * (0.75 + 0.25 * math.sin(u * 11 + k))
        glow(c, _row(x0, y, w, amp, r, 0, end), RED, 220, 1.5, 0.3)
    c.restore()
    px, py = x0 + now_u * w, TOP + now_row * GAP
    a_sh = shake(t)
    py += math.sin(t * 90) * 30 * a_sh
    pen = skia.Path()
    pen.moveTo(1140, py - 300)
    pen.lineTo(px, py)
    c.drawPath(pen, paint(SHADOW, 90, sigma=8, stroke=14))
    ink(c, pen, INK, 255, 7)
    c.drawCircle(px, py, 9, paint(RED))
    c.drawCircle(px, py, 9, paint(INK, 255, stroke=2))
    label(c, "15:11", 1010, 352, 76, "mono_bold", INK, 255, "right")
    label(c, "QUAKE BEGINS · 22 MAY 1960", 1010, 388, 17, "mono", INK, 200, "right", 0.12)
    fig(c, 3, "SEISMOGRAM · 2 MIN A LINE", 70, 250, size=20)
    m = minutes(t)
    card(c, 70, 300, 330, 74)
    label(c, "SHAKING", 92, 346, 18, "mono", SEPIA, 255, tracking=0.16)
    mm, ss = divmod(int(minutes(round(t * FPS) / FPS) * 60), 60)
    label(c, f"{mm:02d}:{ss:02d}", 378, 356, 44, "mono_bold", RED, 255, "right")


def side(m, S=820):
    return S * 32 ** ((m - 9.5) / 2)


def scale_scene(c, t):
    fig(c, 4, "HOW BIG WAS IT?", 70, 268, size=20)
    # 9.5 on the magnitude ruler
    ra = appear(t, VO["B2"] - 0.1) * (1 - appear(t, T_STEP - 0.2, 0.4))
    if ra > 0:
        y = 900
        c.drawLine(110, y, 970, y, paint(INK, 230 * ra, stroke=2))
        for mg in range(5, 11):
            x = 110 + (mg - 5) / 5 * 860
            c.drawLine(x, y - 14, x, y + 14, paint(INK, 230 * ra, stroke=1.6))
            label(c, str(mg), x, y + 50, 26, "mono_bold", INK, 220 * ra, "center")
        mx = 110 + (lerp(5, 9.5, out_expo(prog(t, T_95, T_95 + 0.9))) - 5) / 5 * 860
        tri = skia.Path()
        tri.moveTo(mx, y - 18)
        tri.lineTo(mx - 14, y - 44)
        tri.lineTo(mx + 14, y - 44)
        tri.close()
        c.drawPath(tri, paint(RED, 255 * ra))
        s = pop(t, T_95 + 0.05, 0.5)
        c.save()
        c.translate(540, 700)
        c.scale(0.6 + 0.4 * s, 0.6 + 0.4 * s)
        big_label(c, "9.5", 0, 0, 260, RED, ra * clamp(s * 2))
        c.restore()
        label(c, "MAGNITUDE (MOMENT)", 540, 990, 20, "mono", SEPIA, 255 * ra, "center", 0.16)
    # squares: area = energy
    x0, y0, S = 110, 1180, 820
    if t >= T_STEP - 0.2:
        a = appear(t, T_STEP - 0.2)
        grow = out_expo(prog(t, T_32, T_32 + 0.9))
        s85 = side(8.5)
        s95 = lerp(s85, S, grow)
        big = skia.Path()
        big.addRect(skia.Rect.MakeXYWH(x0, y0 - s95, s95, s95))
        if grow > 0:
            cutout(c, big, mix(BONE, RED, 0.16), 255 * a, lift=14, edge=RED, edge_a=240, edge_wd=2.4)
            hatch(c, big, 70 * a, 9, 45, RED, 1.2)
            la = appear(t, T_32 + 0.5)
            label(c, "9.5", x0 + s95 - 30, y0 - s95 + 120, 120, "black", RED, 255 * la, "right")
            label(c, "CHILE 1960", x0 + s95 - 30, y0 - s95 + 160, 24, "mono_bold", RED, 255 * la, "right", 0.14)
        sm = skia.Path()
        sm.addRect(skia.Rect.MakeXYWH(x0, y0 - s85, s85, s85))
        fa = a * (1 - appear(t, VO["B3"], 0.4))
        if fa > 0:
            cutout(c, sm, WHITE, 255 * fa, lift=8)
            label(c, "8.5", x0 + s85 / 2, y0 - s85 / 2 + 14, 40, "mono_bold", INK, 255 * fa, "center")
            xa = pop(t, T_32 + 0.2, 0.5)
            if xa > 0:
                c.save()
                c.translate(x0 + s85 + 150, y0 - s85 - 80)
                c.scale(clamp(xa), clamp(xa))
                big_label(c, "×32", 0, 30, 110, RED, fa)
                c.restore()
                label(c, "ONE STEP UP = ~32× THE ENERGY", x0, y0 + 56, 20, "mono", INK, 220 * fa, tracking=0.12)
        # B3: the full chart with Japan, 8.0 and the Haiti dot
        if t > VO["B3"] - 0.2:
            for k, (m, name) in enumerate(((9.1, "JAPAN 2011"), (8.0, ""))):
                aa = appear(t, VO["B3"] + 0.2 * k, 0.4)
                s = side(m)
                r = skia.Path()
                r.addRect(skia.Rect.MakeXYWH(x0, y0 - s, s, s))
                cutout(c, r, WHITE if k == 0 else SHADE, 255 * aa, lift=10 - 6 * k)
                if k == 0:
                    hatch(c, r, 45 * aa, 9, -45, INK, 1.0)
                    label(c, "9.1", x0 + s - 24, y0 - s + 76, 70, "black", INK, 255 * aa, "right")
                    label(c, name, x0 + s - 24, y0 - s + 108, 20, "mono_bold", INK, 255 * aa, "right", 0.14)
                else:
                    label(c, "8.0", x0 + s + 12, y0 - 14, 26, "mono_bold", INK, 255 * aa)
            ha = appear(t, T_HAITI - 0.3, 0.3)
            s = side(7.0)
            c.drawRect(skia.Rect.MakeXYWH(x0, y0 - s, s, s), paint(INK, 255 * ha))
            if ha > 0:
                k = (t - T_HAITI) % 1.0
                c.drawCircle(x0 + s / 2, y0 - s / 2, 14 + 30 * k, paint(RED, 230 * ha * (1 - k), stroke=2))
                c.drawCircle(x0 + s / 2, y0 - s / 2, 16, paint(RED, 230 * ha, stroke=2))
                c.drawLine(x0 + s + 2, y0 - s - 2, x0 + 150, y0 - 150, paint(INK, 230 * ha, stroke=1.4))
                label(c, "7.0 · HAITI 2010", x0 + 158, y0 - 146, 26, "mono_bold", INK, 255 * ha)
                label(c, "that tiny dot", x0 + 158, y0 - 110, 28, "serif", INK, 240 * ha)
            ca = appear(t, T_THOU - 0.2)
            if ca > 0:
                v = 5800 * out_expo(prog(round(t * FPS) / FPS, T_THOU, T_THOU + 1.6))
                big_label(c, f"≈{v:,.0f}×", x0 + S - 30, y0 - S + 330, 104, RED, ca, "right")
                label(c, "THE ENERGY OF HAITI 2010", x0 + S - 30, y0 - S + 372, 20, "mono_bold", RED, 255 * ca, "right", 0.12)


def draw_frame(c, t):
    paper(c)
    c.save()
    c.translate(0, drum_scroll(t, DURATION, 0.6, 0.6))
    out = in_cubic(prog(t, T_DRUM_OUT, T_DRUM_OUT + 0.6))
    if out < 1:
        c.save()
        c.translate(0, -out * H * 0.7)
        drum(c, t)
        c.restore()
    if t > T_DRUM_OUT:
        c.save()
        c.translate(0, (1 - out_expo(prog(t, T_DRUM_OUT + 0.1, T_DRUM_OUT + 0.9))) * H * 0.6)
        scale_scene(c, t)
        c.restore()
    CAP.draw(c, t, shake)
    c.restore()


def post_kw(t):
    return dict(shake=0.6 * shake(t), ca=0.6 + shake(t))


def sfx_events():
    ev = [(0.0, "paper_whoosh", 0.5), (0.3, "quake_tail", 0.9)]
    ev += [(0.2 + i * 0.32, "pen_scratch", 0.35) for i in range(int((T_DRUM_OUT - 0.4) / 0.32))]
    ev += [(T_DRUM_OUT, "paper_whoosh", 0.6), (T_95 + 0.3, "stamp", 0.9), (T_95, "needle", 0.4),
           (T_STEP, "paper_slap", 0.6), (T_32, "riser", 0.4), (T_32 + 0.15, "low_hit", 0.8),
           (VO["B3"] + 0.0, "paper_slap", 0.5), (VO["B3"] + 0.2, "paper_slap", 0.4), (T_THOU, "counter", 0.7),
           (T_HAITI - 0.3, "pop", 0.7)]
    return ev


MUSIC = dict(beds=[(0.0, T_DRUM_OUT + 0.4, "tension", 0.5), (T_DRUM_OUT, DURATION + 0.4, "pulse_bed", 0.6)])
