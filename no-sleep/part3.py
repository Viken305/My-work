"""Part 3, hour 24 (amber): the 24 slam; 24 h awake = 0.10 % blood alcohol, past the driving limit; the brain's
front dims while the amygdala lights up (+60 %); hunger meters swap (ghrelin up, leptin down); Sam at the fridge.

  python3 render.py part3 [--still 1,5]
"""
from film import *  # noqa: F401,F403

PART = "part3"
VO, _end = schedule(PART, first=0.25, gap=0.55, extra={"B1": 0.2})
TM = Timing(PART, VO)
DURATION = _end + 0.5

CARD_T = TM.word("B1", "twenty") - 0.15
EQ_T = CARD_T + 1.45
GLASS_T = TM.word("B1", "blood") - 0.15
GAUGE_T = TM.word("B1", "that is") - 0.1
LIMIT_T = TM.word("B1", "legal") - 0.05
BRAIN_T = VO["B2"] - 0.35
DIM_T = TM.word("B2", "emotional") - 0.1
AMYG_T = TM.word("B2", "amygdala") - 0.1
SIXTY_T = TM.word("B2", "sixty") - 0.1
HUGE_T = TM.word("B2", "small") - 0.05
METER_T = VO["B3"] - 0.35
GHR_T = TM.word("B3", "hunger") - 0.1
LEP_T = TM.word("B3", "full") - 0.1
SNACK_T = TM.word("B3", "hello") - 0.2
OUT_T = DURATION - 0.22

CAPS = Captions(TM, anchors={k: (W / 2, 1450) for k in ("B1", "B2", "B3")}, accent=AMBER,
                emph={"twenty", "four", "zero", "point", "one", "percent.", "legal", "limit", "amygdala", "sixty",
                      "huge.", "hunger", "rises", "full", "drops.", "junk"},
                hide={"B1": [(CARD_T, CARD_T + 1.3)]})
MOTES = Motes(40, 5)
PCT = Counter("+60%", 190, "display")


def hour_at(t):
    return 24 + 6 * prog(t, CARD_T, DURATION)


def pal_at(t):
    return blend_pal(1, 2, smooth(prog(t, CARD_T, CARD_T + 0.3)))


def clock_icon(c, x, y, r, t, acc):
    c.drawCircle(x, y, r, fillp((0, 0, 0), 90))
    c.drawCircle(x, y, r, stroke(acc, 10))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        c.drawLine(x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8, x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9, stroke(acc, 5))
    ah = -math.pi / 2 + t * 0.6
    am = -math.pi / 2 + t * 7
    c.drawLine(x, y, x + math.cos(ah) * r * 0.45, y + math.sin(ah) * r * 0.45, stroke(PAPER, 12))
    c.drawLine(x, y, x + math.cos(am) * r * 0.7, y + math.sin(am) * r * 0.7, stroke(PAPER, 7))
    c.drawCircle(x, y, 12, fillp(acc))


def drink(c, x, y, s, t, acc):
    """A cocktail glass (x, y = bowl centre)."""
    bowl = path_of([(x - s, y - s * 0.7), (x + s, y - s * 0.7), (x, y + s * 0.4)], True)
    c.drawPath(path_of([(x - s * 0.78, y - s * 0.5), (x + s * 0.78, y - s * 0.5), (x, y + s * 0.4)], True),
               shaded(linear((0, y - s * 0.5), (0, y + s * 0.4), [mix(acc, (255, 255, 255), 0.3), mix(acc, (0, 0, 0), 0.2)])))
    c.drawPath(bowl, stroke(PAPER, 8))
    c.drawLine(x, y + s * 0.4, x, y + s * 1.25, stroke(PAPER, 8))
    c.drawLine(x - s * 0.5, y + s * 1.25, x + s * 0.5, y + s * 1.25, stroke(PAPER, 8))
    c.drawCircle(x + s * 0.45, y - s * 0.62, s * 0.18, fillp((120, 200, 90)))
    for i in range(4):
        ph = (t * 0.5 + i / 4) % 1
        c.drawCircle(x - s * 0.3 + i * s * 0.2, y - s * 0.1 + (1 - ph) * s * 0.3 - s * 0.3 * ph, 5, stroke((255, 255, 255), 2, 160 * (1 - ph)))


def bac_scene(c, t, pal):
    acc = pal["acc"]
    k1 = out_back(prog(t, EQ_T - 0.3, EQ_T + 0.2), 1.3)
    k2 = out_back(prog(t, GLASS_T, GLASS_T + 0.5), 1.3)
    ke = smooth(prog(t, GLASS_T - 0.2, GLASS_T + 0.2))
    if k1 > 0:
        c.save()
        c.translate(280, 780)
        c.scale(k1, k1)
        clock_icon(c, 0, 0, 150, t, acc)
        c.restore()
        label(c, "24 h awake", 280, 1010, 44, "bold", PAPER, 255 * smooth(k1), "center")
    if ke > 0:
        label(c, "=", 540, 830, 150, "display", acc, 255 * ke, "center")
    if k2 > 0:
        c.save()
        c.translate(810, 760)
        c.scale(k2, k2)
        drink(c, 0, 0, 140, t, acc)
        c.restore()
        label(c, "0.10% alcohol", 810, 1010, 44, "bold", PAPER, 255 * smooth(k2), "center")
    kg = smooth(prog(t, GAUGE_T, GAUGE_T + 0.4))
    if kg > 0:                                         # blood alcohol scale with the driving limits
        x0, x1, y = 120, 960, 1200
        def X(v):
            return lerp(x0, x1, v / 0.12)
        c.drawRRect(rrect(x0, y - 22, x1 - x0, 44, 22), fillp((0, 0, 0), 120 * kg))
        c.drawRRect(rrect(X(0.05), y - 22, X(0.12) - X(0.05), 44, 22), fillp(RED, 110 * kg))
        for v in (0.0, 0.05, 0.08, 0.12):
            c.drawLine(X(v), y - 34, X(v), y + 34, stroke(PAPER, 3, 200 * kg))
            label(c, f"{v:.2f}%", X(v), y + 76, 24, "mono", ASH, 230 * kg, "center")
        lk = smooth(prog(t, LIMIT_T, LIMIT_T + 0.4))
        label(c, "DRIVING LIMIT", (X(0.05) + X(0.08)) / 2, y - 56, 24, "mono_bold", RED, 255 * lk, "center", tracking=0.1)
        nv = 0.10 * out_cubic(prog(t, GAUGE_T, GAUGE_T + 1.0))
        c.drawCircle(X(nv), y, 30, fillp(acc, 255 * kg))
        light(c, X(nv), y, 90, acc, 120 * kg)
        label(c, "SAM", X(nv), y + 9, 22, "mono_bold", INK, 255 * kg, "center")


def brain_scene(c, t, pal):
    k = out_cubic(prog(t, BRAIN_T, BRAIN_T + 0.6))
    hx, hy = shake(t, HUGE_T + 0.3, 20, 5)
    c.save()
    c.translate(540 + hx, 840 + hy + 80 * (1 - k))
    sc = 0.9 + 0.1 * k + 0.06 * smooth(prog(t, HUGE_T, HUGE_T + 0.8))
    c.scale(sc, sc)
    amyg = smooth(prog(t, AMYG_T, AMYG_T + 0.5))
    for i in range(4):                                 # alarm rings
        if amyg <= 0:
            break
        u = (t * 0.9 + i / 4) % 1
        big = 1 + 1.5 * smooth(prog(t, HUGE_T, HUGE_T + 0.6))
        r = (60 + 380 * u) * big
        c.drawCircle(-15, 82, r, stroke(RED, 6, 160 * amyg * (1 - u)))
    brain(c, 0, 0, 290, t, front_dim=smooth(prog(t, DIM_T, DIM_T + 0.8)), amyg=amyg, acc=pal["acc"])
    c.restore()
    da = smooth(prog(t, DIM_T + 0.3, DIM_T + 0.7))
    label(c, "CALM + CONTROL", 90, 520, 26, "mono_bold", ASH, 230 * da, tracking=0.1)
    c.drawLine(200, 540, 270, 660, stroke(ASH, 3, 200 * da))
    if t > SIXTY_T:
        PCT.draw(c, 540, 1345, t, SIXTY_T, 0.7, RED, 255, "center")


def meters_scene(c, t, pal):
    k = smooth(prog(t, METER_T, METER_T + 0.4))
    g = 0.3 + 0.62 * out_cubic(prog(t, GHR_T, GHR_T + 1.1))
    l = 0.75 - 0.6 * out_cubic(prog(t, LEP_T, LEP_T + 1.0))
    for x, lvl, name, sub, rgb in ((270, g, "GHRELIN", '"I\'m hungry"', pal["acc"]), (810, l, "LEPTIN", '"I\'m full"', (150, 160, 200))):
        gauge_bar(c, x - 70, 1220, 140, 560, lvl, rgb, k)
        label(c, name, x, 600, 44, "mono_bold", rgb, 255 * k, "center", tracking=0.06)
        label(c, sub, x, 1290, 36, "regular", ASH, 255 * k, "center")
    arrow(c, 270, 500, 1, pal["acc"], smooth(prog(t, GHR_T + 0.2, GHR_T + 0.5)))
    arrow(c, 810, 500, -1, (150, 160, 200), smooth(prog(t, LEP_T + 0.2, LEP_T + 0.5)))


def arrow(c, x, y, d, rgb, a):
    """Up (d=1) or down (d=-1) arrow centred on (x, y)."""
    if a <= 0:
        return
    c.drawLine(x, y + 36 * d, x, y - 36 * d, stroke(rgb, 10, 255 * a))
    c.drawPath(path_of([(x - 26, y - 12 * d), (x, y - 40 * d), (x + 26, y - 12 * d)]), stroke(rgb, 10, 255 * a))


def fridge_scene(c, t, pal):
    room(c, t, pal, moon=0.0, sun=0.0, lamp=0.3, win=(-400, 0, 10, 10))
    fx, fy, fw, fh = 70, 560, 360, 730
    c.drawRRect(rrect(fx, fy, fw, fh, 26), fillp((210, 200, 186)))
    c.drawRect(skia.Rect.MakeXYWH(fx + 22, fy + 22, fw - 44, fh - 44), shaded(radial((fx + fw / 2, fy + 200), 500, [(255, 248, 220), (240, 220, 170)])))
    for i in range(3):
        c.drawLine(fx + 22, fy + 200 + i * 170, fx + fw - 22, fy + 200 + i * 170, stroke((200, 190, 160), 6))
    for i, (ox, oy, r, rgb) in enumerate(((90, 160, 40, (240, 90, 80)), (210, 150, 52, (120, 200, 90)), (130, 320, 46, (242, 169, 59)), (250, 500, 44, (255, 110, 170)))):
        c.drawCircle(fx + ox, fy + oy, r, fillp(rgb))
    light(c, fx + fw + 120, fy + fh / 2, 700, (255, 220, 160), 130)
    door = path_of([(fx + fw, fy), (fx + fw + 120, fy + 60), (fx + fw + 120, fy + fh - 60), (fx + fw, fy + fh)], True)
    c.drawPath(door, fillp((180, 170, 156)))
    k = out_back(prog(t, SNACK_T, SNACK_T + 0.5))
    sam(c, 760, 1290, 120, t, lid=0.35, bags=0.7, mouth="o", look=(-0.6, 0.2), arm=k, prop="donut", blink_phase=0.4)
    for i in range(5):                                 # cravings orbiting
        a = t * 1.2 + i * 1.25
        x, y = 760 + math.cos(a) * 300, 760 + math.sin(a) * 120
        c.drawCircle(x, y, 34 * k, fillp((242, 169, 59)))
        c.drawCircle(x, y, 28 * k, fillp((255, 110, 170)))
        c.drawCircle(x, y, 10 * k, fillp((40, 24, 12)))


def draw_frame(c, t):
    pal = pal_at(t)
    bg(c, pal)
    if t < CARD_T + 1.2:
        room(c, t, ACTS[1], moon=1.0, lamp=1.0)
        sam(c, 400, 1290, 135, t, lid=0.25 + 0.3 * prog(t, 0, CARD_T), bags=0.5, mouth=0.0)
    elif t < BRAIN_T:
        bac_scene(c, t, pal)
    elif t < METER_T:
        brain_scene(c, t, pal)
    elif t < SNACK_T:
        meters_scene(c, t, pal)
    else:
        fridge_scene(c, t, pal)
    MOTES.draw(c, t, (255, 220, 170), 0.6)
    for tc in (BRAIN_T, METER_T, SNACK_T):
        blink(c, t, tc, 0.16)
    hour_card(c, t, CARD_T, 24, AMBER, 1.4)
    hud(c, t, hour_at(t), mix(CYAN, AMBER, smooth(prog(t, CARD_T, CARD_T + 0.5))), 1.0)
    CAPS.draw(c, t)
    blink(c, t, 0.0, 0.22)
    if t > OUT_T:
        blink(c, t, DURATION, 0.22)


def POST(t):
    return fatigue_post(0.25 + 0.15 * prog(t, CARD_T, DURATION))


def sfx_events():
    ev = [(CARD_T - 0.8, "riser", 0.6), (CARD_T, "trailer_hit", 0.9), (CARD_T + 0.02, "sub_drop", 0.6),
          (EQ_T - 0.3, "pop", 0.6), (GLASS_T, "glass_ting", 0.45), (GAUGE_T, "swish", 0.4), (LIMIT_T, "low_hit", 0.5),
          (BRAIN_T - 0.2, "whoosh", 0.6), (AMYG_T, "heartbeat", 0.8), (AMYG_T + 0.6, "heartbeat", 0.8),
          (SIXTY_T, "counter", 0.5), (HUGE_T + 0.3, "low_hit", 0.7), (METER_T - 0.2, "swish", 0.5),
          (GHR_T, "riser", 0.35), (LEP_T, "descend", 0.4), (SNACK_T - 0.1, "fridge", 0.6), (SNACK_T + 0.2, "pop", 0.5),
          (OUT_T - 0.1, "swish", 0.5)]
    tt = 0.5
    while tt < DURATION:
        ev.append((tt, "tick", 0.2))
        tt += 1.0
    return ev


MUSIC = dict(beds=[(0.0, CARD_T, "night0", 0.5), (CARD_T, DURATION, "night1", 0.55)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
