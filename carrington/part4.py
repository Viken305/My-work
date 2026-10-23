"""Part 4: the shield. The cloud slams into Earth's magnetic field and squeezes it on the day side; at Kew the
magnetograph pen is driven right off the paper. The biggest magnetic storm on record begins."""
from common import *  # noqa: F401,F403

PART = "part4"
VO, _end = schedule(PART, first=0.6, gap=0.55)
TM = Timing(PART, VO)
T_SLAM = TM.word("C1", "slammed")
T_SQ = TM.word("C1", "squeezed")
T_KEW = TM.word("C2", "Kew")
T_DRIVEN = TM.word("C2", "driven")
T_SCALE = TM.word("C2", "scale")
T_BIG = TM.word("C3", "biggest")
T_STORM = TM.word("C3", "storm")
DURATION = _end + 1.0
CAP = Captions(TM, VoiceEnvelope(PART, VO), colours({"scale": AUR_R, "storm": AUR_R}),
               anchors={k: (W / 2, 1460) for k in VO})
CX, CY, R = 640, 1000, 120
_rng = np.random.default_rng(5)
WIND = [(_rng.random(), _rng.random(), _rng.random(), _rng.random()) for _ in range(140)]


def squash(t):
    return spring(prog(t, T_SLAM - 0.05, T_SLAM + 0.9), 6, 9)


def bow_x(y, k):
    dy = (y - CY) / 560
    calm = CX - 470 * (1 - 0.45 * dy * dy) - 30
    hit_ = CX - 330 * (1 - 0.55 * dy * dy) - 30
    return lerp(calm, hit_, k)


def pen_u(t):
    return 0.62 * prog(t, T_KEW, T_DRIVEN) + 0.38 * prog(t, T_DRIVEN, T_SCALE + 1.4)


def kew(c, t, x, y, w, h):
    a = appear(t, T_KEW - 0.35, 0.35)
    if a <= 0:
        return
    drop = (1 - out_expo(prog(t, T_KEW - 0.35, T_KEW + 0.35))) * -260
    y += drop
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 4, 4)
    c.drawRRect(r.makeOffset(0, 6), paint((0, 0, 0), 150 * a, sigma=10))
    c.drawRRect(r, paint(CARD, 255 * a))
    for k in range(1, 12):
        c.drawLine(x + k * w / 12, y + 8, x + k * w / 12, y + h - 8, paint(SEPIA, 46 * a, stroke=1))
    c.drawLine(x + 10, y + h * 0.5, x + w - 10, y + h * 0.5, paint(SEPIA, 76 * a, stroke=1))
    upto = pen_u(t)
    pts = []
    for i in range(int(700 * upto) + 1):
        u = i / 699
        pts.append((x + 14 + u * (w - 28), y + h * 0.5 - magnetogram(u, 2) * h * 0.55))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    if len(pts) > 1:
        c.drawPath(polyline(pts), paint(SEPIA, 255 * a, stroke=1.6))
    c.restore()
    if len(pts) > 1 and upto < 1:      # the pen: where it leaves the paper, it glows red
        px, py = pts[-1]
        off = py > y + h or py < y
        py = min(max(py, y), y + h)
        bloom_dot(c, px, py, 4, AUR_R if off else SEPIA, 255 * a, 1.2 if off else 0.3)
    label(c, "KEW OBSERVATORY · MAGNETOGRAPH · 1–2 SEPT 1859", x + 14, y + 30, 16, "mono_bold", SEPIA, 255 * a,
          tracking=0.1)
    fx = x + 14 + 0.32 * (w - 28)
    fa = appear(t, T_KEW + 0.6) * a
    c.drawLine(fx, y + h * 0.2, fx, y + h * 0.32, paint(SEPIA, 255 * fa, stroke=1.2))
    label(c, "FLARE", fx, y + h * 0.18, 14, "mono", SEPIA, 255 * fa, "center", 0.1)
    stamp_tab(c, "OFF THE SCALE", x + w * 0.78, y + h + 6, pop(t, T_SCALE - 0.1), AUR_R, 22, -4)


def draw_frame(c, t):
    glass(c)
    stars(c, 260, 9, (0, 0, W, H), 180, t)
    k = squash(t)
    arrive = out_cubic(prog(t, 0.0, T_SLAM))
    # the cloud's gas streaming in from the left, piling up against the field
    for (r0, r1, r2, r3) in WIND:
        y = 520 + r0 * 860
        xb = bow_x(y, k)
        front = lerp(-200, xb, arrive)
        L = 120 + 260 * r1
        x0 = (front - L - ((t * (500 + 400 * r2) + r3 * 900) % 900)) if arrive >= 1 else front - L - r3 * 400
        x1 = min(x0 + L, front)
        if x1 > x0:
            c.drawLine(x0, y, x1, y, paint(SUN, 30 + 90 * r2, stroke=0.8 + r3 * 1.6, blend=ADD))
    if arrive > 0.05:
        bow = [(lerp(-200, bow_x(y, k), arrive), y) for y in np.linspace(540, 1460, 80)]
        light(c, polyline(bow), SUN, 230 * arrive * (1 + 0.6 * hit(t, T_SLAM, 0.03, 0.4)), 3.0, 1.2)
    # the field: squashed on the day side, dragged into a tail on the night side
    pole_glow = 0.6 + 0.9 * appear(t, T_SLAM, 0.6) + 0.8 * appear(t, T_BIG - 0.2, 0.6)
    for i, L in enumerate((190, 260, 350, 470, 620, 800)):
        for side in (-1, 1):
            pts = dipole_line(CX, CY, L, (0.12 + 0.07 * i) * k, (0.15 + 0.12 * i) * k, side=side)
            pts = [(x, y) for x, y in pts if x < W + 200]
            engrave(c, polyline(pts), LIME if i < 5 else SILVER, 220 - i * 18, 1.4, 0.5)
    for sgn in (-1, 1):
        o = skia.Path()
        tr = math.radians(-12)
        px, py = CX + sgn * -math.sin(tr) * R * 0.92, CY - sgn * math.cos(tr) * R * 0.92
        o.addOval(skia.Rect.MakeXYWH(px - 48, py - 10, 96, 20))
        light(c, o, AUR_G if sgn > 0 or t < T_BIG else mix(AUR_G, AUR_R, 0.5), 200 * min(pole_glow, 1.6) / 1.6,
              2.0 + 1.4 * pole_glow, 1.0 * pole_glow, None)
    pr = Ortho(-40 + t * 2, 15, R, CX, CY, -12)
    earth(c, pr, 1.0, (-1, 0), 1.0)
    sa = appear(t, T_SQ - 0.1, 0.35)
    if sa > 0:
        caption_on_path(c, "squeezed", [(x - 12, y + 10) for x, y in dipole_line(CX, CY, 620, 0.47 * k, 0.6 * k, side=-1)[80:]],
                        30, 46, "serif_bold", SUN, 255 * sa, 1.0, SUN)
    kew(c, t, 70, 220, 940, 190)
    stamp_tab(c, "BIGGEST MAGNETIC STORM ON RECORD", 560, 560, pop(t, T_STORM - 0.1), AUR_R, 24, 2)
    slide_label(c, 4, "EARTH'S MAGNETIC FIELD", 70, 150, 255 * appear(t, 0.4))
    CAP.draw(c, t, shake=lambda tt: needle(tt))


def needle(t):
    """How hard the needle (and everything with it) is shaking."""
    u = pen_u(t)
    storm = abs(magnetogram(u, 2)) * 0.6 if t > T_DRIVEN else 0.0
    return shake_env(t, T_SLAM, 1.0, 0.04, 0.5) + storm * (1 - prog(t, T_SCALE + 1.5, T_BIG + 1.5)) * 0.8


def post_kw(t):
    kw = slide_change(t, DURATION)
    kw["flash"] = 0.3 * hit(t, T_SLAM, 0.03, 0.25)
    kw["shake"] = 0.8 * shake_env(t, T_SLAM, 1.0, 0.04, 0.45) + 0.25 * needle(t) * (t > T_DRIVEN)
    kw["flicker"] = 1 + 2.5 * needle(t)
    return kw


def sfx_events():
    return [(0.25, "slide_whoosh", 0.6), (0.3, "solar_roar", 0.6), (T_SLAM - 0.05, "impact", 1.0),
            (T_SQ, "field_groan", 0.7), (T_KEW - 0.35, "paper_slap", 0.6), (T_KEW, "pen_scratch", 0.5),
            (T_DRIVEN - 0.1, "needle_scrawl", 0.8), (T_SCALE - 0.1, "stamp", 0.8), (T_BIG - 0.2, "aurora_swell", 0.6),
            (T_STORM - 0.1, "stamp", 0.7), (DURATION - 0.4, "slide_clack", 0.6)]


MUSIC = dict(beds=[(0.0, DURATION + 0.3, "tension", 0.6), (0.0, DURATION, "projector", 0.3)],
             pulse=[(0.0, DURATION, 104)])
