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
REACT_T = CARD_T + 1.3                          # the falling-mug gag
DROP_T = TM.word("B1", "reaction") - 0.15
EQ_T = TM.word("B1", "someone") - 0.2           # 24 h awake = 0.10 % alcohol
GLASS_T = TM.word("B1", "blood") - 0.15
GAUGE_T = TM.word("B1", "that is") - 0.1
LIMIT_T = TM.word("B1", "legal") - 0.05
BRAIN_T = VO["B2"] - 0.35
DIM_T = TM.word("B2", "emotional") - 0.1
AMYG_T = TM.word("B2", "amygdala") - 0.1
SIXTY_T = TM.word("B2", "sixty") - 0.1
HUGE_T = TM.word("B2", "small") - 0.05
MEM_T = VO["B4"] - 0.3                          # memory: cards fly into the hippocampus, 40 % bounce off
HIPPO_T = TM.word("B4", "hippocampus") - 0.1
FORTY_T = TM.word("B4", "forty") - 0.1
METER_T = VO["B3"] - 0.35
GHR_T = TM.word("B3", "hunger") - 0.1
LEP_T = TM.word("B3", "full") - 0.1
SNACK_T = TM.word("B3", "hello") - 0.2
OUT_T = DURATION - 0.22

CAPS = Captions(TM, anchors={"B1": (W / 2, 1450), "B2": (W / 2, 1490), "B4": (W / 2, 1490), "B3": (W / 2, 1450)}, accent=AMBER,
                emph={"memory", "hippocampus,", "forty", "less", "twenty", "four", "zero", "point", "one", "percent.", "legal", "limit", "amygdala", "sixty",
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


SHARDS = [(math.radians(200 + 140 * hsh(i, 1)), 500 + 700 * hsh(i, 2), 14 + 16 * hsh(i, 3), 600 * (hsh(i, 4) - 0.5)) for i in range(11)]
FLOOR = 1290


def mug_y(t):
    """Mug falls from the shelf under gravity and hits the floor."""
    d = max(0.0, t - DROP_T)
    return min(FLOOR - 40, 600 + 0.5 * 4200 * d * d)


IMPACT_T = DROP_T + math.sqrt(2 * (FLOOR - 40 - 600) / 4200)


def reaction_scene(c, t, pal):
    room(c, t, pal, lamp=0.8, win=(-400, 0, 10, 10))
    c.drawRect(skia.Rect.MakeXYWH(700, 640, 330, 22), fillp(mix(pal["dim"], (0, 0, 0), 0.2)))     # shelf
    for i, (bx, bh, rgb) in enumerate(((730, 110, (120, 70, 40)), (770, 130, (60, 90, 130)), (812, 96, (150, 60, 60)))):
        c.drawRRect(rrect(bx, 640 - bh, 34, bh, 4), fillp(rgb))
    # the mug: wobbles, falls, smashes
    if t < IMPACT_T:
        wob = 6 * math.sin((t - DROP_T + 0.3) * 30) * smooth(prog(t, DROP_T - 0.3, DROP_T)) if t < DROP_T else 0
        rot = 0 if t < DROP_T else 380 * (t - DROP_T)
        mx = 930 + (0 if t < DROP_T else 60 * (t - DROP_T))
        my = mug_y(t)
        c.save()
        c.translate(mx, my)
        c.rotate(wob + rot)
        mug(c, 0, 40, 85, 0, 255, 0.7 if t < DROP_T else 0, t)
        c.restore()
    else:
        d = t - IMPACT_T
        sp = out_cubic(prog(t, IMPACT_T, IMPACT_T + 0.5))                        # coffee spreads on the floor
        c.drawOval(skia.Rect.MakeXYWH(960 - 170 * sp, FLOOR - 8 - 22 * sp, 340 * sp, 44 * sp), fillp((90, 54, 30), 230))
        for ang, v, sz, spin in SHARDS:
            x = 960 + math.cos(ang) * v * d * 0.5
            y = min(FLOOR + 6, FLOOR - 30 + math.sin(ang) * v * d + 0.5 * 3000 * d * d)
            c.save()
            c.translate(x, y)
            c.rotate(spin * d)
            c.drawPath(path_of([(-sz, 0), (0, -sz * 0.7), (sz * 0.8, sz * 0.4)], True), fillp((245, 245, 250)))
            c.restore()
        if d < 0.25:
            light(c, 960, FLOOR - 30, 260, (255, 240, 220), 160 * (1 - d / 0.25))
    late = DROP_T + 0.85                                                         # Sam reacts much too late
    reach = out_back(prog(t, late, late + 0.35), 1.6)
    track = smooth(prog(t, DROP_T + 0.35, DROP_T + 0.9))
    shocked = smooth(prog(t, late + 0.3, late + 0.5))
    sam(c, 430, FLOOR, 135, t, lid=lerp(0.5, 0.1, shocked), bags=0.65, mouth="o" if shocked > 0.5 else -0.1,
        look=(lerp(0.6, 1.0, track), lerp(-0.6, 0.8, track)), arm=reach, tilt=lerp(0, 8, reach))
    # reaction-time bars
    ka = smooth(prog(t, REACT_T + 0.2, REACT_T + 0.6))
    if ka > 0:
        label(c, "REACTION TIME", 72, 470, 28, "mono_bold", PAPER, 255 * ka, tracking=0.12)
        for i, (name, rgb, t0, full) in enumerate((("RESTED", CYAN, DROP_T, 0.3), ("SAM", pal["acc"], DROP_T, 0.82))):
            y = 520 + i * 56
            label(c, name, 72, y + 26, 22, "mono", ASH, 255 * ka)
            c.drawRRect(rrect(200, y, 470, 30, 15), fillp((0, 0, 0), 110 * ka))
            g = full * out_cubic(prog(t, t0, t0 + (0.35 if i == 0 else 1.5)))
            if g > 0.01:
                c.drawRRect(rrect(200, y, 470 * g, 30, 15), fillp(rgb, 255 * ka))


def drink(c, x, y, s, t, acc, slosh=0.0):
    """A cocktail glass (x, y = bowl centre). slosh tilts the drink's surface."""
    d = slosh * s * 0.16
    c.drawPath(path_of([(x - s * 0.78, y - s * 0.5 + d), (x + s * 0.78, y - s * 0.5 - d), (x, y + s * 0.4)], True),
               shaded(linear((0, y - s * 0.5), (0, y + s * 0.4), [mix(acc, (255, 255, 255), 0.3), mix(acc, (0, 0, 0), 0.2)])))
    bowl = path_of([(x - s, y - s * 0.7), (x + s, y - s * 0.7), (x, y + s * 0.4)], True)
    c.drawPath(bowl, stroke(PAPER, 8))
    c.drawLine(x - s * 0.62, y - s * 0.6, x - s * 0.2, y + s * 0.1, stroke((255, 255, 255), 6, 90))   # glass highlight
    c.drawLine(x, y + s * 0.4, x, y + s * 1.25, stroke(PAPER, 8))
    c.drawLine(x - s * 0.5, y + s * 1.25, x + s * 0.5, y + s * 1.25, stroke(PAPER, 8))
    c.drawLine(x + s * 0.1, y - s * 0.9 - d, x + s * 0.45, y - s * 0.62 - d, stroke((200, 190, 170), 4))   # cocktail stick
    c.drawCircle(x + s * 0.45, y - s * 0.62 - d, s * 0.16, fillp((120, 200, 90)))
    for i in range(4):
        ph = (t * 0.5 + i / 4) % 1
        c.drawCircle(x - s * 0.3 + i * s * 0.2, y - s * 0.1 + (1 - ph) * s * 0.3 - s * 0.3 * ph, 5, stroke((255, 255, 255), 2, 160 * (1 - ph)))


def bac_scene(c, t, pal):
    acc = pal["acc"]
    bg(c, pal)
    light(c, 540, 820, 700, acc, 50)
    # clock spins in from the left, hands racing then settling
    k1 = prog(t, EQ_T, EQ_T + 0.55)
    if k1 > 0:
        cx = lerp(-200, 280, out_back(k1, 1.4))
        c.save()
        c.translate(cx, 780)
        c.rotate(lerp(-200, 0, out_cubic(k1)))
        clock_icon(c, 0, 0, 150, t * (1 + 9 * (1 - out_cubic(prog(t, EQ_T, EQ_T + 1.5)))), acc)
        c.restore()
        reveal(c, "24 h awake", 280, 1010, 46, t, EQ_T + 0.35, "bold", PAPER, 255, "center", stagger=0.02, dur=0.3, rise=0.3, outline=5)
    # glass drops in from above and sloshes
    k2 = prog(t, GLASS_T - 0.1, GLASS_T + 0.45)
    if k2 > 0:
        gy = lerp(-300, 760, out_back(k2, 1.8))
        d = max(0.0, t - GLASS_T - 0.25)
        slosh = math.exp(-d * 3.0) * math.sin(d * 13) if t > GLASS_T + 0.25 else 0.0
        c.save()
        c.translate(810, gy)
        c.rotate(4 * slosh)
        drink(c, 0, 0, 140, t, acc, slosh)
        c.restore()
        reveal(c, "0.10% alcohol", 810, 1010, 46, t, GLASS_T + 0.35, "bold", PAPER, 255, "center", stagger=0.02, dur=0.3, rise=0.3, outline=5)
    # the equals sign stamps down between them
    ke = prog(t, GLASS_T + 0.3, GLASS_T + 0.5)
    if ke > 0:
        sc = lerp(2.2, 1.0, out_expo(ke))
        c.save()
        c.translate(540, 790)
        c.scale(sc, sc)
        c.drawRRect(rrect(-46, -38, 92, 22, 8), fillp(acc, 255 * smooth(ke * 2)))
        c.drawRRect(rrect(-46, 16, 92, 22, 8), fillp(acc, 255 * smooth(ke * 2)))
        c.restore()
    # blood alcohol scale with the driving limits; the needle swings past and settles at 0.10
    kg = prog(t, GAUGE_T - 0.1, GAUGE_T + 0.4)
    if kg > 0:
        x0, x1 = 120, 960
        y = lerp(1500, 1200, out_cubic(kg))
        ga = smooth(kg * 1.5)
        def X(v):
            return lerp(x0, x1, v / 0.12)
        nv = 0.10 * out_back(prog(t, GAUGE_T + 0.2, GAUGE_T + 1.3), 2.0)
        nv += 0.002 * math.sin(t * 9) * smooth(prog(t, GAUGE_T + 1.3, GAUGE_T + 1.8))
        c.drawRRect(rrect(x0, y - 22, x1 - x0, 44, 22), fillp((0, 0, 0), 130 * ga))
        over = smooth(prog(nv, 0.045, 0.055))
        flash = 0.6 + 0.4 * math.sin(t * 14) if over > 0 else 0
        c.drawRRect(rrect(X(0.05), y - 22, X(0.12) - X(0.05), 44, 22), fillp(RED, (70 + 110 * over * flash) * ga))
        c.drawRRect(rrect(x0, y - 22, max(44, X(nv) - x0), 44, 22), fillp(acc, 150 * ga))
        for v in (0.0, 0.05, 0.08, 0.12):
            c.drawLine(X(v), y - 34, X(v), y + 34, stroke(PAPER, 3, 200 * ga))
            label(c, f"{v:.2f}%", X(v), y + 76, 24, "mono", ASH, 230 * ga, "center")
        lk = prog(t, LIMIT_T, LIMIT_T + 0.2)
        if lk > 0:
            sc = lerp(1.8, 1.0, out_expo(lk))
            c.save()
            mx = (X(0.05) + X(0.08)) / 2
            c.translate(mx, y - 64)
            c.scale(sc, sc)
            label(c, "DRIVING LIMIT", 0, 0, 26, "mono_bold", RED, 255 * smooth(lk * 2), "center", tracking=0.1)
            c.restore()
        light(c, X(nv), y, 110, acc, 140 * ga)
        c.drawCircle(X(nv), y, 34, fillp(acc, 255 * ga))
        c.drawCircle(X(nv), y, 34, stroke(PAPER, 4, 255 * ga))
        label(c, "SAM", X(nv), y + 9, 22, "mono_bold", INK, 255 * ga, "center")


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
        PCT.draw(c, 540, 1315, t, SIXTY_T, 0.7, RED, 255, "center")


MEM_PCT = Counter("-40%", 190, "display")
CARDS = [(i, 1.0 if i % 5 in (1, 3) else 0.0, hsh(i, 21), "A7BX3K9Q2ZM5R8PW4N"[i]) for i in range(18)]


def hippocampus(cx, cy, s):
    """A curled seahorse-like tube inside the brain (path)."""
    p = skia.Path()
    p.moveTo(cx - 0.32 * s, cy + 0.14 * s)
    p.cubicTo(cx - 0.18 * s, cy + 0.42 * s, cx + 0.16 * s, cy + 0.44 * s, cx + 0.26 * s, cy + 0.26 * s)
    p.cubicTo(cx + 0.34 * s, cy + 0.1 * s, cx + 0.16 * s, cy + 0.02 * s, cx + 0.1 * s, cy + 0.14 * s)
    return p


def memory_scene(c, t, pal):
    acc = pal["acc"]
    k = in_out(prog(t, MEM_T, MEM_T + 0.8))
    c.save()
    c.translate(540, lerp(840, 820, k))
    sc = lerp(1.0, 1.08, k)
    c.scale(sc, sc)
    brain(c, 0, 0, 290, t, front_dim=0.6, amyg=0.3 * (1 - k), acc=acc)
    hk = smooth(prog(t, HIPPO_T, HIPPO_T + 0.4))
    hp = hippocampus(0, 0, 290)
    glow_p = stroke(CYAN, 34, 90 * (0.3 + 0.7 * hk))
    glow_p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
    c.drawPath(hp, glow_p)
    c.drawPath(hp, stroke(CYAN, 16, 255 * (0.4 + 0.6 * hk)))
    c.restore()
    tx, ty = 540 + 0.0 * 290 * sc, 820 + 0.3 * 290 * sc                         # where the cards are headed
    if hk > 0:
        label(c, "HIPPOCAMPUS", 1000, 1160, 34, "mono_bold", CYAN, 255 * hk, "right", tracking=0.06)
        label(c, "saves new memories", 1000, 1204, 30, "regular", ASH, 255 * hk, "right")
        c.drawLine(820, 1130, tx + 70, ty + 30, stroke(CYAN, 3, 200 * hk))
    for i, bounce, r, ch in CARDS:                     # new information arriving
        t0 = MEM_T + 0.4 + i * 0.33
        u = prog(t, t0, t0 + 0.55)
        if u <= 0:
            continue
        side = -1 if i % 2 else 1
        sx, sy = W / 2 + side * 660, 480 + 760 * r
        rejected = bounce > 0
        if not rejected:
            if u >= 1:
                continue
            e = in_cubic(u)
            x, y = lerp(sx, tx, e), lerp(sy, ty, e)
            sz, a = lerp(120, 36, e), 255 * (1 - smooth(prog(u, 0.85, 1)))
            rgb = CYAN
        else:
            e = out_cubic(min(1, u / 0.55))
            x, y = lerp(sx, tx, 0.75 * e), lerp(sy, ty, 0.75 * e)
            d = max(0, t - t0 - 0.3)
            x += side * 260 * d
            y += -300 * d + 1400 * d * d
            sz, a = lerp(120, 80, e), 255 * (1 - smooth(prog(t, t0 + 0.9, t0 + 1.2)))
            rgb = RED
        if a <= 1:
            continue
        c.save()
        c.translate(x, y)
        c.rotate(side * 20 * (1 - u) + (side * 200 * max(0, t - t0 - 0.3) if rejected else 0))
        c.drawRRect(rrect(-sz / 2, -sz / 2, sz, sz, sz * 0.18), fillp((14, 16, 30), a))
        c.drawRRect(rrect(-sz / 2, -sz / 2, sz, sz, sz * 0.18), stroke(rgb, max(2, sz * 0.06), a))
        label(c, ch, 0, sz * 0.2, sz * 0.55, "mono_bold", rgb, a, "center")
        if rejected and t > t0 + 0.3:                  # bounced off: crossed out
            xk = smooth(prog(t, t0 + 0.3, t0 + 0.45))
            q = sz * 0.6 * xk
            c.drawLine(-q, -q, q, q, stroke(RED, 7, a))
            c.drawLine(-q, q, q, -q, stroke(RED, 7, a))
        c.restore()
    if t > FORTY_T:
        MEM_PCT.draw(c, 540, 1315, t, FORTY_T, 0.7, RED, 255, "center")


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
    shx, shy = shake(t, IMPACT_T, 14, 8) if t < EQ_T else shake(t, GLASS_T + 0.5, 12, 8)
    c.save()
    c.translate(shx, shy)
    if t < CARD_T:
        c.drawPaint(fillp((0, 0, 0)))
    elif t < EQ_T:
        reaction_scene(c, t, pal)
    elif t < BRAIN_T:
        bac_scene(c, t, pal)
    elif t < MEM_T:
        brain_scene(c, t, pal)
    elif t < METER_T:
        memory_scene(c, t, pal)
    elif t < SNACK_T:
        meters_scene(c, t, pal)
    else:
        fridge_scene(c, t, pal)
    c.restore()
    MOTES.draw(c, t, (255, 220, 170), 0.6)
    blink(c, t, EQ_T, 0.14)
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
          (DROP_T - 0.3, "tick_roll", 0.25), (DROP_T, "swish", 0.5), (IMPACT_T, "smash", 0.9), (DROP_T + 0.85, "whoosh", 0.35),
          (EQ_T - 0.1, "whoosh", 0.55), (EQ_T + 0.4, "pop", 0.5), (GLASS_T - 0.1, "swish", 0.55), (GLASS_T + 0.3, "glass_ting", 0.5),
          (GLASS_T + 0.45, "stamp", 0.7), (GAUGE_T - 0.1, "swish", 0.45), (GAUGE_T + 0.2, "riser", 0.3), (LIMIT_T, "low_hit", 0.6),
          (BRAIN_T - 0.2, "whoosh", 0.6), (AMYG_T, "heartbeat", 0.8), (AMYG_T + 0.6, "heartbeat", 0.8),
          (SIXTY_T, "counter", 0.5), (HUGE_T + 0.3, "low_hit", 0.7), (MEM_T, "shimmer", 0.35), (HIPPO_T, "glass_ting", 0.35),
          (FORTY_T, "counter", 0.5), (FORTY_T + 0.7, "low_hit", 0.5), (METER_T - 0.2, "swish", 0.5),
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
