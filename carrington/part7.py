"""Part 7: the near miss. Today's night side, strung with power grids and satellites. On 23 July 2012 a cloud at
least as strong as 1859 left the Sun's far side and hit the STEREO-A spacecraft (about 121 degrees ahead of Earth).
The region it came from had faced Earth about nine days earlier; the Sun's rotation is run backwards to show it."""
from common import *  # noqa: F401,F403

PART = "part7"
VO, _end = schedule(PART, first=0.6, gap=0.55)
TM = Timing(PART, VO)
T_WONDER = TM.word("F1", "wonder")
T_TODAY = TM.word("F1", "Today")
T_POWER = TM.word("F1", "power")
T_SATS = TM.word("F1", "satellites")
T_JULY = TM.word("F2", "July")
T_STRONG = TM.word("F2", "strong")
T_BLAST = TM.word("F2", "blasted")
T_MISSED = TM.word("F3", "missed")
T_NINE = TM.word("F3", "nine")
T_FACING = TM.word("F3", "facing")
T_END = TM.end("F3")
DURATION = T_END + 2.4
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"9days": AUR_R, "missed": AUR_R, "wonder": AUR_G}),
               anchors={k: (W / 2, 1290) for k in VO})
SX, SY, RS, RO = 400, 760, 78, 470
E_DEG, ST_DEG = 48.0, 48.0 - 121.0
EX, EY = SX + math.cos(math.radians(E_DEG)) * RO, SY + math.sin(math.radians(E_DEG)) * RO
TX, TY = SX + math.cos(math.radians(ST_DEG)) * RO, SY + math.sin(math.radians(ST_DEG)) * RO


def spot_deg(t):
    """Where the active region faces: at the eruption it faces STEREO-A; on 'nine days earlier' the Sun's spin is
    run backwards until it faces Earth."""
    return lerp(ST_DEG, E_DEG, in_out(prog(t, T_NINE - 0.1, T_FACING + 0.1)))


def diagram(c, t):
    a = appear(t, T_JULY - 0.3, 0.5)
    if a <= 0:
        return
    orbit = skia.Path()
    orbit.addArc(skia.Rect.MakeXYWH(SX - RO, SY - RO, 2 * RO, 2 * RO), E_DEG,
                 -360 * out_cubic(prog(t, T_JULY - 0.3, T_JULY + 1.0)))
    c.drawPath(orbit, dashed(paint(SILVER, 150 * a, stroke=1.3), 4, 8))
    # the 2012 cloud, fired toward STEREO-A
    u = prog(t, T_BLAST - 0.15, T_BLAST + 1.1)
    if u > 0:
        fr = lerp(RS, RO + 70, out_cubic(u))
        fa = 1 - 0.5 * smooth(prog(t, T_MISSED, T_NINE))
        for k in range(10):
            rr = fr - k * 26
            if rr <= RS:
                break
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(SX - rr, SY - rr, 2 * rr, 2 * rr), ST_DEG - 26, 52)
            if k == 0:
                light(c, arc, SUN, 255 * fa, 3.2, 1.3)
            else:
                c.drawPath(arc, paint(SUN, 150 * math.exp(-k / 4) * fa, stroke=1.3, blend=ADD))
        cone = skia.Path()
        cone.moveTo(SX, SY)
        cone.arcTo(skia.Rect.MakeXYWH(SX - fr, SY - fr, 2 * fr, 2 * fr), ST_DEG - 26, 52, False)
        cone.close()
        c.drawPath(cone, paint(SUN, 30 * fa, sigma=10, blend=ADD))
    sun_disc(c, SX, SY, RS * (0.6 + 0.4 * out_expo(prog(t, T_JULY - 0.3, T_JULY + 0.5))), 255 * a, 1.0, 3, t)
    # the active region, and the Sun's spin run backwards
    d = spot_deg(t)
    r_ = math.radians(d)
    sunspot(c, SX + math.cos(r_) * RS * 0.78, SY + math.sin(r_) * RS * 0.78, 9, 255 * a, 5, 0.7, d)
    sa = appear(t, T_NINE - 0.2, 0.3)
    if sa > 0:
        spin = skia.Path()
        spin.addArc(skia.Rect.MakeXYWH(SX - RS - 34, SY - RS - 34, 2 * RS + 68, 2 * RS + 68), ST_DEG, d - ST_DEG)
        engrave(c, spin, LIME, 220 * sa, 1.6)
        ax, ay = SX + math.cos(r_) * (RS + 34), SY + math.sin(r_) * (RS + 34)
        tang = r_ + math.pi / 2
        for s_ in (-1, 1):
            c.drawLine(ax, ay, ax - math.cos(tang + s_ * 0.5) * 14, ay - math.sin(tang + s_ * 0.5) * 14,
                       paint(LIME, 220 * sa, stroke=1.6))
        label(c, "THE SUN TURNS", SX - RS - 40, SY + RS + 70, 16, "mono", LIME, 220 * sa, "left", 0.12)
    fa = appear(t, T_FACING - 0.1, 0.3)
    if fa > 0:
        pth, tip = path_upto([(SX, SY), (EX, EY)], out_cubic(prog(t, T_FACING - 0.1, T_FACING + 0.4)))
        c.drawPath(pth, dashed(paint(AUR_R, 220 * fa, stroke=2), 6, 6))
        label(c, "9 DAYS EARLIER:", (SX + EX) / 2 + 30, (SY + EY) / 2 - 6, 18, "mono_bold", AUR_R, 255 * fa, tracking=0.08)
        label(c, "STRAIGHT AT US", (SX + EX) / 2 + 30, (SY + EY) / 2 + 18, 18, "mono_bold", AUR_R, 255 * fa, tracking=0.08)
    pr = Ortho(-60 + t * 4, 10, 34, EX, EY)
    earth(c, pr, a, ((SX - EX) / RO, (SY - EY) / RO), 1.0)
    ma = hit(t, T_MISSED, 0.05, 0.6)
    if ma > 0.02:
        c.drawCircle(EX, EY, 34 + 40 * (1 - ma), paint(LIME, 200 * ma, stroke=2))
    label(c, "EARTH", EX + 48, EY + 8, 20, "mono_bold", LIME, 230 * a, tracking=0.2)
    satellite(c, TX, TY, -30, 255 * a, 1.1)
    hk = hit(t, T_BLAST + 0.75, 0.04, 0.5)
    if hk > 0.02:
        bloom_dot(c, TX, TY, 8, SUN, 255 * hk, 2.0)
    tag(c, TX + 40, TY + 50, "STEREO-A · HIT", SUN, 255 * appear(t, T_BLAST + 0.8), 18)
    tag(c, 70, 300, "23 JULY 2012", SUN, 255 * appear(t, T_JULY), 22)
    tag(c, 70, 352, "AT LEAST AS STRONG AS 1859", LIME, 255 * appear(t, T_STRONG - 0.2), 22)


def draw_frame(c, t):
    glass(c)
    stars(c, 360, 17, (0, 0, W, H), 200, t)
    ga = appear(t, 0.1, 0.6) * (1 - appear(t, T_TODAY - 0.3, 0.6))      # 1859's wonder, fading into today
    if ga > 0.01:
        aurora(c, t, -100, W + 100, 1100, 760, 1, 0.9 * ga, 420, 2, 0.05)
        aurora(c, t + 3, -60, W + 60, 920, 560, 2, 0.7 * ga, 320, 3, -0.08)
    # today's night side rises into view
    cy = lerp(3500, 2700, out_expo(prog(t, T_TODAY - 0.4, T_TODAY + 1.2)))
    city_limb(c, 540, cy, 1300, 255 * (0.45 + 0.55 * appear(t, T_POWER - 0.2, 0.4)))
    for k, (x0, y0, x1, y1, ang) in enumerate(((-80, 1380, 220, 1330, 20), (1160, 1460, 900, 1400, -15))):
        u = out_cubic(prog(t, T_SATS - 0.6 + k * 0.2, T_SATS + 0.6 + k * 0.2))
        if u > 0:
            satellite(c, lerp(x0, x1, u) + 6 * math.sin(t * 0.7 + k), lerp(y0, y1, u), ang, 220, 0.8)
    wa = appear(t, 0.3, 0.4) * (1 - appear(t, T_TODAY - 0.2, 0.4))
    tag(c, 70, 300, "1859: A WONDER", AUR_G, 255 * wa, 22)
    ta = appear(t, T_TODAY - 0.2, 0.4) * (1 - appear(t, T_JULY - 0.6, 0.3))
    tag(c, 70, 300, "TODAY: POWER GRIDS · SATELLITES", SPARK, 255 * ta, 22)
    diagram(c, t)
    slide_label(c, 7, "THE NEAR MISS", 70, 150, 255 * appear(t, 0.4))
    CAP.draw(c, t)
    r = lerp(1600, 0, in_cubic(prog(t, DURATION - 1.4, DURATION - 0.35)))    # the lantern irises down on Earth
    if r < 1600:
        iris(c, EX, EY, max(r, 0.5))


def post_kw(t):
    kw = slide_change(t, DURATION, fout=0.0)
    kw["flash"] = 0.2 * hit(t, T_BLAST - 0.1, 0.04, 0.3)
    kw["dim"] = max(kw["dim"], smooth(prog(t, DURATION - 0.4, DURATION)))
    return kw


def sfx_events():
    return [(0.25, "slide_whoosh", 0.6), (T_TODAY - 0.4, "rise_hum", 0.6), (T_POWER - 0.2, "electric_buzz", 0.5),
            (T_SATS - 0.4, "swish", 0.4), (T_JULY - 0.3, "lens", 0.5), (T_BLAST - 0.2, "solar_roar", 0.9),
            (T_BLAST + 0.75, "low_hit", 0.6), (T_MISSED, "glass_ting", 0.5), (T_NINE - 0.15, "rewind", 0.8),
            (T_FACING - 0.1, "lock_on", 0.7), (DURATION - 1.4, "reverse_swell", 0.6), (DURATION - 0.4, "lamp_off", 0.8)]


MUSIC = dict(beds=[(0.0, DURATION + 0.4, "wonder", 0.55), (T_NINE - 0.5, DURATION + 0.4, "deep", 0.5),
                   (0.0, DURATION - 0.3, "projector", 0.3)])
