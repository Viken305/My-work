"""Part 3: the crossing. The flare's light reaches Earth in about 8 minutes; then the cloud leaves the Sun and
crosses the 150 million km in 17.6 hours (a typical cloud takes days). Its hour count rides on its leading edge."""
from common import *  # noqa: F401,F403

PART = "part3"
VO, _end = schedule(PART, first=0.6, gap=0.55)
TM = Timing(PART, VO)
T_LIGHT = TM.word("B1", "light")
T_EARTH1 = TM.word("B1", "Earth")
T_8 = TM.word("B1", "eight")
T_HURL = TM.word("B1", "hurled")
T_CLOUD = TM.word("B1", "cloud")
T_FEW = TM.word("B2", "few")
T_176 = TM.word("B2", "seventeen")
T_AIMED = TM.word("B3", "aimed")
T_EARTH3 = TM.word("B3", "Earth")
DURATION = _end + 1.0
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"earth": LIME, "us": SUN}), anchors={k: (W / 2, 1440) for k in VO})
SX, SY, SR = -120, 300, 470
EX, EY = 860, 1150
D_EARTH = math.hypot(EX - SX, EY - SY)


def front_of(t):
    u = in_out(prog(t, T_HURL - 0.2, T_176 + 0.35))
    return lerp(SR * 0.9, D_EARTH - 90, u), u


def draw_frame(c, t):
    glass(c)
    stars(c, 380, 7, (0, 0, W, H), 210, t)
    k = out_expo(prog(t, 0.0, 1.0))
    sun_disc(c, SX - 200 * (1 - k), SY - 120 * (1 - k), SR, 255, 1.0, 2, t * 0.6)
    # the dashed Sun-Earth line, drawn as the light sets off
    la = appear(t, T_LIGHT - 0.4, 0.4)
    p0 = (SX + (EX - SX) * SR / D_EARTH, SY + (EY - SY) * SR / D_EARTH)
    pth, tip = path_upto([p0, (EX, EY)], out_cubic(prog(t, T_LIGHT - 0.3, T_LIGHT + 0.7)))
    if tip:
        c.drawPath(pth, dashed(paint(SILVER, 160 * la, stroke=1.4), 3, 9))
    # the flash of light racing ahead: 8 minutes
    u = prog(t, T_LIGHT - 0.1, T_LIGHT + 0.7)
    if 0 < u < 1:
        x, y = lerp(p0[0], EX, out_cubic(u)), lerp(p0[1], EY, out_cubic(u))
        bloom_dot(c, x, y, 5, FLARE, 255, 1.6)
    # the cloud
    front, fu = front_of(t)
    if t > T_HURL - 0.2:
        ang0, half = cme(c, SX, SY, EX, EY, front, 255 * appear(t, T_HURL - 0.2, 0.3), 3, t)
        if fu > 0.08:
            pts = []
            for j in range(80):
                v = j / 79
                th = ang0 - half * 0.9 + 1.8 * half * v
                pts.append((SX + math.cos(th) * (front + 34), SY + math.sin(th) * (front + 34)))
            hrs = 17.6 * fu
            caption_on_path(c, f"{hrs:4.1f} HOURS", pts[::-1], 220, 62, "serif_bold", FLARE, 255 * appear(t, T_HURL + 0.6),
                            1.0, SUN)
    ea = appear(t, T_EARTH1 - 0.3, 0.5)
    if ea > 0:
        pr = Ortho(-30 + t * 3, 10, 62 * (0.7 + 0.3 * out_expo(prog(t, T_EARTH1 - 0.3, T_EARTH1 + 0.4))), EX, EY)
        earth(c, pr, ea, (-0.7, -0.7), 1.0)
        label(c, "EARTH", EX, EY + 100, 22, "mono_bold", LIME, 230 * ea, "center", 0.2)
    # reticle: it was aimed at us
    ra = pop(t, T_AIMED - 0.1, 0.5)
    if ra > 0:
        rr = 120 - 30 * clamp(ra)
        al = 255 * clamp(ra)
        c.drawCircle(EX, EY, rr, paint(AUR_R, al, stroke=2))
        for q in range(4):
            th = q * math.pi / 2 + t * 0.6
            c.drawLine(EX + math.cos(th) * (rr - 14), EY + math.sin(th) * (rr - 14), EX + math.cos(th) * (rr + 18),
                       EY + math.sin(th) * (rr + 18), paint(AUR_R, al, stroke=2.4))
    # race card
    ca = appear(t, T_8 - 0.4, 0.4)
    y0 = 1010
    if ca > 0:
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(60, y0, 450, 230), 8, 8)
        c.drawRRect(r, paint(VOID, 210 * ca))
        c.drawRRect(r, paint(LIME, 120 * ca, stroke=1.2))
        label(c, "SUN → EARTH · 150 MILLION KM", 86, y0 - 18, 16, "mono", SILVER, 255 * ca, tracking=0.1)
        rows = (("ITS LIGHT", "8 MIN", LIME, T_8), ("A TYPICAL CLOUD", "DAYS", SILVER, T_FEW),
                ("THIS CLOUD", "17.6 H", SUN, T_176))
        for i, (kk, v, rgb, t0) in enumerate(rows):
            y = y0 + 60 + i * 66
            ra_ = pop(t, t0 - 0.15, 0.45)
            if ra_ <= 0:
                continue
            al = 255 * clamp(ra_ * 1.5)
            label(c, kk, 86, y, 20, "mono", SILVER, al, tracking=0.1)
            c.save()
            c.translate(486, y)
            sc = 1 + 0.4 * (1 - clamp(ra_)) if i == 2 else 1
            c.scale(sc, sc)
            label(c, v, 0, 0, 34 if i == 2 else 28, "mono_bold", rgb, al, "right")
            c.restore()
            if i < 2:
                c.drawLine(86, y + 22, 486, y + 22, paint(LIME, 60 * ca, stroke=1))
    slide_label(c, 3, "THE CROSSING", 70, 150, 255 * appear(t, 0.4))
    CAP.draw(c, t)


def post_kw(t):
    kw = slide_change(t, DURATION)
    kw["flash"] = 0.25 * hit(t, T_HURL - 0.2, 0.05, 0.4)
    return kw


def sfx_events():
    return [(0.25, "slide_whoosh", 0.6), (T_LIGHT - 0.1, "swish", 0.5), (T_8 - 0.1, "pop", 0.5),
            (T_HURL - 0.25, "solar_roar", 1.0), (T_FEW - 0.1, "pop", 0.4), (T_176 - 0.1, "stamp", 0.7),
            (T_AIMED - 0.1, "lock_on", 0.7), (DURATION - 0.4, "slide_clack", 0.6)]


MUSIC = dict(beds=[(0.0, DURATION + 0.3, "tension", 0.55), (0.0, DURATION, "projector", 0.3)],
             pulse=[(T_HURL, DURATION, 96)])
