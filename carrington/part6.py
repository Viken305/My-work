"""Part 6: the telegraph. Wires throw sparks and operators get shocks; between Boston and Portland the operators
disconnect their batteries and keep working on the current the storm drives through the lines. The register prints
the Boston operator's words onto the tape."""
from common import *  # noqa: F401,F403

PART = "part6"
VO, _end = schedule(PART, first=0.6, gap=0.55)
TM = Timing(PART, VO)
T_TEL = TM.word("E1", "telegraph")
T_NET = TM.word("E1", "internet")
T_HAY = TM.word("E1", "haywire")
T_SPARKS = TM.word("E1", "sparks")
T_SHOCK = TM.word("E1", "shocks")
T_BOSTON = TM.word("E2", "Boston")
T_UNPLUG = TM.word("E2", "unplugged")
T_SEND = TM.word("E3", "sending")
T_POWER = TM.word("E3", "powered")
T_SKY = TM.word("E3", "sky")
DURATION = _end + 1.2
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"unplugged": AUR_R, "alone": AUR_G}),
               anchors={k: (W / 2, 1460) for k in VO})
MSG = "WE ARE WORKING WITH THE AURORAL CURRENT"
POLES = ((150, 560), (560, 510), (970, 470))
TAPE_Y, TAPE_X1 = 1110, 940


def tape_glyphs():
    """[(x, kind, w)] symbols and [(x, ch)] letters along the tape, x from the start of the message."""
    syms, letters, x = [], [], 0
    for ch in MSG:
        if ch == " ":
            x += 30
            continue
        cw = 0
        for s in MORSE[ch]:
            L = 6 if s == "." else 22
            syms.append((x + cw, L))
            cw += L + 6
        letters.append((x + max(cw, 18) / 2, ch))
        x += max(cw, 18) + 16
    return syms, letters, x


SYMS, LETTERS, MSG_W = tape_glyphs()
SPEED = MSG_W / (DURATION - 0.6 - T_SEND)


def wire_pts(i, w_):
    p0, p1 = POLES[i], POLES[i + 1]
    a = (p0[0] + (56 if w_ else -56), p0[1] + 10)
    b = (p1[0] + (56 if w_ else -56), p1[1] + 10)
    return [(lerp(a[0], b[0], u), lerp(a[1], b[1], u) + 40 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 40)]


def wild(t):
    """How wild the current in the wires is."""
    return 0.25 + 0.75 * smooth(prog(t, T_HAY - 0.3, T_HAY + 0.4)) + 0.6 * hit(t, T_SPARKS, 0.05, 0.6)


def crackle(c, x, y, seed, a=255):
    rng = np.random.default_rng(seed)
    for k in range(7):
        pts = [(x, y)]
        ang = rng.random() * 6.28
        for j in range(6):
            ang += rng.normal(0, 0.7)
            pts.append((pts[-1][0] + math.cos(ang) * 14, pts[-1][1] + math.sin(ang) * 14))
        light(c, polyline(pts), SPARK, a * 0.9, 1.4, 1.1)
    bloom_dot(c, x, y, 8, SPARK, a, 1.5)


def batteries(c, t, x, y):
    a = appear(t, T_BOSTON - 0.2, 0.4)
    if a <= 0:
        return
    off = smooth(prog(t, T_UNPLUG - 0.1, T_UNPLUG + 0.2))
    for k in range(3):
        jar = skia.Path()
        jar.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + k * 90, y, 64, 90), 8, 8))
        c.drawPath(jar, paint(VOID, 230 * a))
        tint(c, jar, mix(SPARK, SILVER, off), 90 * a * (1 - 0.6 * off), (2, 2), 2)
        engrave(c, jar, LIME, 230 * a, 1.4, 0.3)
        c.drawRect(skia.Rect.MakeXYWH(x + k * 90 + 14, y - 14, 10, 16), paint(LIME, 230 * a))
        c.drawRect(skia.Rect.MakeXYWH(x + k * 90 + 40, y - 14, 10, 16), paint(LIME, 230 * a))
    # the switch: closed, then thrown open
    sx, sy = x + 280, y + 20
    c.drawCircle(sx, sy, 6, paint(LIME, 255 * a))
    ang = math.radians(lerp(0, -55, off))
    c.drawLine(sx, sy, sx + math.cos(ang) * 60, sy + math.sin(ang) * 60, paint(LIME, 255 * a, stroke=4))
    c.drawCircle(sx + 60, sy, 6, paint(LIME, 255 * a, stroke=1.6))
    c.drawLine(x + 32, y - 14, x + 32, y - 40, paint(LIME, 200 * a, stroke=1.6))
    c.drawLine(x + 32, y - 40, sx, y - 40, paint(LIME, 200 * a, stroke=1.6))
    c.drawLine(sx, y - 40, sx, sy, paint(LIME, 200 * a, stroke=1.6))
    k = pop(t, T_UNPLUG, 0.4)
    if k > 0:
        cx, cy = x + 135, y + 45
        L = 70 * clamp(k)
        c.drawLine(cx - L, cy - L * 0.7, cx + L, cy + L * 0.7, paint(AUR_R, 255, stroke=6))
        c.drawLine(cx - L, cy + L * 0.7, cx + L, cy - L * 0.7, paint(AUR_R, 255, stroke=6))


def tape(c, t):
    a = appear(t, T_SEND - 0.6, 0.4)
    if a <= 0:
        return
    printed = max(0.0, (t - T_SEND + 0.3) * SPEED)
    h = 96
    r = skia.Rect.MakeLTRB(-20, TAPE_Y - h / 2, TAPE_X1, TAPE_Y + h / 2)
    c.drawRect(r.makeOffset(0, 8), paint((0, 0, 0), 150 * a, sigma=10))
    c.drawRect(r, paint(CARD, 255 * a))
    off = TAPE_X1 - 40 - printed
    for k in range(int(TAPE_X1 / 9) + 2):
        x = k * 9 - (printed % 9)
        c.drawLine(x, TAPE_Y - h / 2, x + 4, TAPE_Y + h / 2, paint(SEPIA, 10 * a, stroke=1))
    c.save()
    c.clipRect(r)
    for x, L in SYMS:
        if x <= printed:
            c.drawRoundRect(skia.Rect.MakeXYWH(off + x, TAPE_Y - 26, L, 8), 4, 4, paint(SEPIA, 255 * a))
    f = font("mono_bold", 22)
    for x, ch in LETTERS:
        if x + 10 <= printed:
            c.drawString(ch, off + x - f.measureText(ch) / 2, TAPE_Y + 26, f, paint(SEPIA, 220 * a))
    c.restore()
    # the register the tape feeds out of
    reg = skia.Path()
    reg.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(TAPE_X1 - 10, TAPE_Y - 90, 160, 180), 10, 10))
    c.drawPath(reg, paint(VOID, 255 * a))
    tint(c, reg, (120, 70, 40), 120 * a, (3, 3))
    engrave(c, reg, LIME, 255 * a, 1.6)
    for k, (gx, gy, gr) in enumerate(((TAPE_X1 + 40, TAPE_Y - 40, 26), (TAPE_X1 + 70, TAPE_Y + 30, 18))):
        c.save()
        c.translate(gx, gy)
        c.rotate(t * (120 if k else -180))
        for j in range(10):
            c.drawLine(0, 0, gr, 0, paint(LIME, 200 * a, stroke=1.2))
            c.rotate(36)
        c.restore()
        c.drawCircle(gx, gy, gr, paint(LIME, 220 * a, stroke=1.4))
    label(c, "BOSTON → PORTLAND", 70, TAPE_Y - 70, 18, "mono_bold", LIME, 255 * a, tracking=0.1)


def draw_frame(c, t):
    glass(c)
    stars(c, 200, 13, (0, 0, W, 700), 150, t)
    sky = 0.55 + 0.6 * smooth(prog(t, T_POWER - 0.3, T_SKY + 0.3))
    aurora(c, t, -100, W + 100, 1000, 780, 6, sky, 380, 2)
    aurora(c, t + 4, 100, W + 200, 860, 520, 9, sky * 0.6, 260, 3, -0.06)
    pa = appear(t, 0.2, 0.6)
    tops = []
    for i, (x, y0) in enumerate(POLES):
        rise = (1 - out_expo(prog(t, 0.1 + i * 0.12, 0.9 + i * 0.12))) * 500
        tops.append(pole(c, x, y0 + rise, 1070 + rise, 255 * pa))
    wl = wild(t)
    green = smooth(prog(t, T_POWER - 0.2, T_SKY + 0.2))
    cur = mix(SPARK, AUR_G, green)
    wa = appear(t, 0.9, 0.5)
    for w_ in range(2):
        for i in range(2):
            pts = wire_pts(i, w_)
            engrave(c, polyline(pts), LIME, 200 * wa, 1.6)
            fl = 0.7 + 0.3 * math.sin(t * 40 + i * 2 + w_) * wl
            light(c, polyline(pts), cur, 110 * wa * wl * fl, 1.2, 0.8, None)
            for k in range(3 + int(3 * wl)):
                u = (t * (0.5 + 1.2 * wl) + k / (3 + int(3 * wl)) + w_ * 0.17) % 1
                x, y = pts[int(u * 39)]
                bloom_dot(c, x, y, 3, cur, 255 * wa)
    # sparks at the insulators: one big burst on "sparks", then the line keeps crackling
    for k, (tt, pi, wi) in enumerate(((T_SPARKS - 0.1, 1, 1), (T_SPARKS + 0.5, 0, 0), (T_SPARKS + 1.3, 2, 0),
                                      (T_SPARKS + 2.2, 1, 0), (T_SHOCK + 1.5, 0, 1), (T_BOSTON + 1.0, 2, 1))):
        e = hit(t, tt, 0.03, 0.25)
        if e > 0.02:
            x, y = POLES[pi][0] + (56 if wi else -56), POLES[pi][1] + 10
            crackle(c, x, y, k * 7 + int(t * 20) % 3, 255 * e)
    telegraph_key_anim(c, 120, 1300, t)
    batteries(c, t, 600, 1260)
    tape(c, t)
    tag(c, 70, 290, "THE INTERNET OF 1859", LIME, 255 * appear(t, T_NET - 0.2), 22)
    tag(c, 70, 342, "BATTERIES DISCONNECTED", AUR_R, 255 * appear(t, T_UNPLUG), 22)
    tag(c, 70, 394, "RUNNING ON THE AURORA'S CURRENT", AUR_G, 255 * appear(t, T_POWER - 0.1), 22)
    slide_label(c, 6, "THE TELEGRAPH, 2 SEPT 1859", 70, 150, 255 * appear(t, 0.4))
    CAP.draw(c, t, shake=lambda tt: 0.6 * hit(tt, T_SHOCK, 0.03, 0.4) + 0.3 * hit(tt, T_SPARKS, 0.03, 0.4))


def telegraph_key_anim(c, x, y, t):
    a = appear(t, 0.5, 0.5)
    base = skia.Path()
    base.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, 380, 60), 10, 10))
    tint(c, base, (120, 70, 40), 160 * a, (3, 3))
    engrave(c, base, LIME, 255 * a, 1.6)
    hatch(c, base, 40 * a, 6, 10, LIME, 0.7)
    # the key taps out the message once the tape starts
    tap = 0.0
    if t > T_SEND - 0.3:
        printed = (t - T_SEND + 0.3) * SPEED
        tap = 1.0 if any(xx <= printed <= xx + L for xx, L in SYMS) else 0.0
    lev = skia.Path()
    lev.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + 40, y - 46, 320, 22), 8, 8))
    c.save()
    c.rotate(-4 + 3 * tap, x + 60, y - 30)
    tint(c, lev, (200, 150, 80), 150 * a, (3, 3))
    engrave(c, lev, LIME, 255 * a, 1.6)
    knob = skia.Path()
    knob.addOval(skia.Rect.MakeXYWH(x + 300, y - 86, 90, 52))
    c.drawPath(knob, paint((20, 16, 20), 255 * a))
    engrave(c, knob, LIME, 255 * a, 1.6)
    c.restore()
    for px in (x + 60, x + 200):
        c.drawCircle(px, y - 10, 16, paint(VOID, 255 * a))
        q = skia.Path()
        q.addCircle(px, y - 10, 16)
        engrave(c, q, LIME, 255 * a, 1.4)
    e = hit(t, T_SHOCK - 0.1, 0.03, 0.35)
    if e > 0.02:
        rng = np.random.default_rng(9 + int(t * 30) % 4)
        for k in range(6):
            pts = [(x + 200, y - 26)]
            for j in range(8):
                px, py = pts[-1]
                pts.append((px + rng.normal(14, 10), py - rng.normal(12, 8)))
            light(c, polyline(pts), SPARK, 255 * e, 1.6, 1.0)
        bloom_dot(c, x + 200, y - 26, 10, SPARK, 255 * e, 1.6)


def post_kw(t):
    kw = slide_change(t, DURATION)
    kw["flash"] = 0.25 * hit(t, T_SPARKS - 0.1, 0.03, 0.2) + 0.35 * hit(t, T_SHOCK - 0.1, 0.03, 0.2)
    kw["shake"] = 0.5 * hit(t, T_SHOCK - 0.1, 0.03, 0.3)
    kw["flicker"] = 1 + 1.5 * wild(t) * (1 - smooth(prog(t, T_UNPLUG, T_UNPLUG + 1)))
    return kw


def morse_events():
    """A click for every dot and dash as the tape prints, in time with the picture."""
    out = []
    for x, L in SYMS:
        tt = T_SEND - 0.3 + x / SPEED
        if tt < DURATION - 0.5:
            out.append((tt, "morse_dot" if L < 10 else "morse_dash", 0.45))
    return out


def sfx_events():
    ev = [(0.25, "slide_whoosh", 0.6), (0.4, "wire_hum", 0.6), (T_HAY - 0.2, "electric_buzz", 0.7)]
    ev += [(T_SPARKS - 0.1, "spark", 1.0), (T_SPARKS + 0.5, "spark", 0.5), (T_SPARKS + 1.3, "spark", 0.4),
           (T_SPARKS + 2.2, "spark", 0.35), (T_SHOCK - 0.1, "zap", 1.0), (T_SHOCK + 1.5, "spark", 0.3),
           (T_BOSTON + 1.0, "spark", 0.3), (T_UNPLUG, "switch", 0.8), (T_POWER - 0.2, "aurora_swell", 0.6),
           (DURATION - 0.4, "slide_clack", 0.6)]
    return ev + morse_events()


MUSIC = dict(beds=[(0.0, DURATION + 0.3, "tension", 0.45), (T_UNPLUG, DURATION + 0.3, "wonder", 0.5),
                   (0.0, DURATION, "projector", 0.3)])
