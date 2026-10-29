"""Part 4, hours 36-48: the 36 slam and Sam as an x-ray with inflammation spreading; the 48 slam (red) and
microsleeps, where the picture itself blacks out; then the road at night, where a few seconds of blackout cover a
football field.

  python3 render.py part4 [--still 1,5]
"""
from film import *  # noqa: F401,F403

PART = "part4"
VO, _end = schedule(PART, first=0.25, gap=0.55, extra={"C1": 0.2, "C2": 0.15})
TM = Timing(PART, VO)
DURATION = _end + 0.6

CARD1_T = TM.word("C1", "thirty") - 0.15
XRAY_T = CARD1_T + 1.3
EMERG_T = TM.word("C1", "emergency") - 0.1
STRESS_T = TM.word("C1", "stress") - 0.1
INFL_T = TM.word("C1", "inflammation") - 0.1
CARD2_T = TM.word("C2", "forty") - 0.15
FACE_T = CARD2_T + 1.3
MICRO_T = TM.word("C2", "microsleeps") - 0.05
BLACK = [(TM.word("C2", "tiny") - 0.05, 0.55), (TM.word("C2", "seconds") - 0.1, 0.7),
         (TM.word("C3", "won't") - 0.05, 0.6)]
OPEN_T = VO["C3"] - 0.1
ROAD_T = TM.word("C3", "at highway") - 0.25
FIELD_T = TM.word("C3", "football") - 0.25
OUT_T = DURATION - 0.22

CAPS = Captions(TM, anchors={k: (W / 2, 1450) for k in ("C1", "C2", "C3")}, accent=RED,
                emph={"thirty", "six", "emergency.", "stress", "inflammation", "forty", "eight", "microsleeps.",
                      "blackouts,", "open.", "notice.", "football", "field."},
                hide={"C1": [(CARD1_T, CARD1_T + 1.25)], "C2": [(CARD2_T, CARD2_T + 1.25)]})
MOTES = Motes(36, 8)


def hour_at(t):
    if t < CARD2_T:
        return 36 + 3 * prog(t, CARD1_T, CARD2_T)
    return 48 + 3 * prog(t, CARD2_T, DURATION)


def pal_at(t):
    if t < CARD2_T:
        return blend_pal(2, 3, 0.2 * smooth(prog(t, EMERG_T, EMERG_T + 1.0)))
    return blend_pal(2, 3, lerp(0.2, 1.0, smooth(prog(t, CARD2_T, CARD2_T + 0.3))))


def blackout(t):
    """1 while the picture is blacked out by a microsleep (with soft edges)."""
    k = 0.0
    for t0, d in BLACK:
        k = max(k, smooth(prog(t, t0, t0 + 0.06)) * (1 - smooth(prog(t, t0 + d, t0 + d + 0.08))))
    return k


def xray_scene(c, t, pal):
    acc = pal["acc"]
    k = smooth(prog(t, XRAY_T - 0.2, XRAY_T + 0.3))
    em = smooth(prog(t, EMERG_T, EMERG_T + 0.3))
    if em > 0:                                         # red alert pulse at the frame edges
        pul = 0.5 + 0.5 * math.sin(t * 7)
        c.drawRect(skia.Rect.MakeWH(W, H), stroke(RED, 90, 90 * em * pul))
    for i in range(14):                                # scan lines
        y = 470 + i * 60 + (t * 40) % 60
        c.drawLine(80, y, 1000, y, stroke(acc, 1.5, 40 * k))
    body_xray(c, 540, 1290, 150, t, acc, dots=smooth(prog(t, INFL_T, INFL_T + 1.6)), a=k)
    for y0, txt, t0, side in ((640, "STRESS HORMONES", STRESS_T, -1), (980, "INFLAMMATION", INFL_T, 1)):
        a = smooth(prog(t, t0, t0 + 0.3))
        if a <= 0:
            continue
        x = 90 if side < 0 else 990
        label(c, txt, x, y0, 32, "mono_bold", RED if side > 0 else acc, 255 * a, "left" if side < 0 else "right", tracking=0.05)
        ax = x + (width(txt, "mono_bold", 32, 0.05) + 40) * (1 if side < 0 else -1)
        c.drawLine(ax, y0 + 10, ax, y0 - 40, stroke(RED if side > 0 else acc, 7, 255 * a))
        c.drawPath(path_of([(ax - 16, y0 - 24), (ax, y0 - 44), (ax + 16, y0 - 24)]), stroke(RED if side > 0 else acc, 7, 255 * a))


def face_scene(c, t, pal):
    room(c, t, pal, lamp=0.6, win=(-400, 0, 10, 10))
    droop = 0.55 + 0.12 * math.sin(t * 1.3)
    opened = smooth(prog(t, OPEN_T, OPEN_T + 0.3))
    lid = lerp(droop, 0.05, opened)
    sway = 3 * math.sin(t * 0.8)
    sam(c, 540, 1330, 195, t, lid=lid, bags=1.0, wide=0.35 * opened, mouth=-0.2, look=(0, 0.3 * opened),
        tilt=sway, slump=0.3 * (1 - opened), blink_phase=0.9)
    if opened > 0:
        label(c, "EYES", 70, 640, 34, "mono_bold", RED, 255 * opened, tracking=0.12)
        label(c, "OPEN", 70, 684, 34, "mono_bold", RED, 255 * opened, tracking=0.12)
        fl = 255 * opened * (0.6 + 0.4 * math.sin(t * 12))
        label(c, "BRAIN", 1010, 640, 34, "mono_bold", PAPER, fl, "right", tracking=0.12)
        label(c, "OFFLINE", 1010, 684, 34, "mono_bold", PAPER, fl, "right", tracking=0.12)


def road_scene(c, t, pal):
    acc = pal["acc"]
    c.drawPaint(fillp((8, 4, 10)))
    x0, x1 = 120, 640
    c.drawRect(skia.Rect.MakeLTRB(x0, 420, x1, H), fillp((34, 28, 36)))
    c.drawLine(x0 + 14, 420, x0 + 14, H, stroke((230, 220, 200), 6, 200))
    c.drawLine(x1 - 14, 420, x1 - 14, H, stroke((230, 220, 200), 6, 200))
    off = (t * 900) % 160
    for i in range(14):                                # centre dashes scroll past (car is moving)
        y = 420 + i * 160 + off - 160
        c.drawLine((x0 + x1) / 2, y, (x0 + x1) / 2, y + 80, stroke((240, 200, 90), 10, 230))
    fk = smooth(prog(t, FIELD_T, FIELD_T + 0.5))
    drift = 70 * smooth(prog(t, ROAD_T + 0.6, ROAD_T + 1.6)) * (1 - fk)
    cx, cy = (x0 + x1) / 2 + 120 + drift, 1250
    for sx in (-1, 1):                                 # headlight beams
        beam = path_of([(cx + sx * 40, cy - 110), (cx + sx * 140 - 40, cy - 520), (cx + sx * 140 + 60, cy - 520)], True)
        bp = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([(0, cy - 110), (0, cy - 520)],
                        [skia.Color(255, 240, 200, 120), skia.Color(255, 240, 200, 0)]), BlendMode=skia.BlendMode.kPlus)
        bp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
        c.drawPath(beam, bp)
    c.save()
    c.translate(cx, cy)
    c.rotate(drift * 0.08)
    c.drawRRect(rrect(-62, -115, 124, 230, 34), fillp(SAM_DK))
    c.drawRRect(rrect(-48, -70, 96, 70, 16), fillp((20, 20, 40)))
    c.drawRRect(rrect(-48, 30, 96, 50, 14), fillp((20, 20, 40)))
    c.drawCircle(0, -32, 22, fillp(SAM))
    for sx in (-1, 1):
        c.drawCircle(sx * 40, -112, 9, fillp((255, 250, 220)))
        c.drawCircle(sx * 42, 112, 8, fillp(RED))
    c.restore()
    if fk > 0:                                         # a few seconds of travel = a football field
        ytop = cy - 110 - 640 * fk
        bx = x0 - 50
        c.drawRect(skia.Rect.MakeLTRB(x0, ytop, x1, cy - 110), fillp(RED, 70 * fk))
        c.drawLine(bx, ytop, bx, cy - 110, stroke(RED, 4, 255 * fk))
        for y in (ytop, cy - 110):
            c.drawLine(bx - 16, y, bx + 16, y, stroke(RED, 4, 255 * fk))
        fx0, fx1 = 720, 980
        c.drawRect(skia.Rect.MakeLTRB(fx0, ytop, fx1, cy - 110), fillp((40, 120, 60), 255 * fk))
        c.drawRect(skia.Rect.MakeLTRB(fx0, ytop, fx1, cy - 110), stroke((240, 240, 240), 4, 255 * fk))
        for i in range(1, 10):
            y = lerp(ytop, cy - 110, i / 10)
            c.drawLine(fx0, y, fx1, y, stroke((240, 240, 240), 2, 150 * fk))
        c.drawLine(fx0, (ytop + cy - 110) / 2, fx1, (ytop + cy - 110) / 2, stroke((240, 240, 240), 4, 220 * fk))
        label(c, "3 SECONDS", 850, cy - 40, 30, "mono_bold", RED, 255 * fk, "center", tracking=0.1)
        label(c, "≈ 90 m", 850, cy + 20, 54, "display", PAPER, 255 * fk, "center")
        label(c, "at 110 km/h", 850, cy + 66, 26, "regular", ASH, 255 * fk, "center")


def draw_frame(c, t):
    pal = pal_at(t)
    bg(c, pal)
    if t < CARD2_T + 1.2:
        xray_scene(c, t, pal)
    elif t < ROAD_T:
        face_scene(c, t, pal)
    else:
        road_scene(c, t, pal)
    MOTES.draw(c, t, (255, 190, 200), 0.5)
    blink(c, t, ROAD_T, 0.16)
    hour_card(c, t, CARD1_T, 36, mix(AMBER, RED, 0.25), 1.35)
    hour_card(c, t, CARD2_T, 48, RED, 1.35)
    hud(c, t, hour_at(t), pal["acc"], 1.0, glitch=0.4 * smooth(prog(t, CARD2_T, CARD2_T + 1)))
    bk = blackout(t)
    if bk > 0:                                         # microsleep: the picture drops out, only a dim timer stays
        c.drawPaint(fillp((0, 0, 0), 255 * bk))
        for t0, d in BLACK:
            if t0 <= t <= t0 + d + 0.08:
                s = f"MICROSLEEP  00:0{1 + int((t - t0) * 3)}"
                label(c, s, W / 2, 980, 30, "mono", RED, 150 * bk, "center", tracking=0.12)
    CAPS.draw(c, t)
    blink(c, t, 0.0, 0.22)
    if t > OUT_T:
        blink(c, t, DURATION, 0.22)


def POST(t):
    f = 0.45 + 0.2 * prog(t, 0, CARD2_T) + 0.2 * prog(t, CARD2_T, DURATION)
    return fatigue_post(f, wobble=2.0 * prog(t, CARD2_T, DURATION), split=1.5 * prog(t, CARD2_T, DURATION))


def sfx_events():
    ev = [(CARD1_T - 0.8, "riser", 0.55), (CARD1_T, "trailer_hit", 0.85), (CARD1_T + 0.02, "sub_drop", 0.6),
          (XRAY_T, "shimmer", 0.3), (EMERG_T, "heartbeat", 0.8), (EMERG_T + 0.55, "heartbeat", 0.8),
          (EMERG_T + 1.1, "heartbeat", 0.8), (STRESS_T, "pop", 0.5), (INFL_T, "boil", 0.35),
          (CARD2_T - 0.8, "riser_dark", 0.6), (CARD2_T, "trailer_hit", 0.95), (CARD2_T + 0.02, "sub_drop", 0.7),
          (OPEN_T, "glass_ting", 0.3), (ROAD_T - 0.2, "car_pass", 0.8), (ROAD_T + 0.9, "rumble_strip", 0.7),
          (FIELD_T, "low_hit", 0.6), (FIELD_T + 0.3, "horn", 0.35), (OUT_T - 0.1, "swish", 0.5)]
    tt = 0.5
    while tt < DURATION:
        if blackout(tt) < 0.5:
            ev.append((tt, "tick", 0.22))
        tt += 1.0
    return ev


MUSIC = dict(beds=[(0.0, CARD2_T, "night1", 0.55), (CARD2_T, DURATION, "night2", 0.55)],
             mute=[(t0, t0 + d + 0.08) for t0, d in BLACK])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
