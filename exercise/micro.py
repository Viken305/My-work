"""Style C · FOGGED GLASS. A macro shot of skin behind a steamed-up gym window. Sweat beads swell out of the pores and
roll; water drops on the glass act as real lenses (they show the skin upside down).
Captions: a fingertip wipes each word into the fog, revealing the sharp skin through the letters; the letters drip,
and old words slowly fog over again.

  python3 render.py micro [--still 2,4]
"""
import os

import cv2

import premium
from kit import *  # noqa: F401,F403

PART = "micro"
VO, _end = schedule(PART, first=0.6, gap=0.5)
TM = Timing(PART, VO)
DURATION = _end + 1.6

SKIN0, SKIN1 = (204, 116, 86), (104, 48, 36)
FOG = (236, 240, 247)
EMPH = {"overheating,", "sweat", "litre"}
SIZE = 150
PAPER_W = (255, 255, 255)


# ---------------------------------------------------------------- the skin (cached texture)
def _skin_texture():
    path = os.path.join(premium.CACHE, "skin.png")
    if os.path.exists(path):
        return skia.Image.open(path)
    os.makedirs(premium.CACHE, exist_ok=True)
    n = premium.fbm(H, W, 4, 220, 6, 0.55)
    m = premium.fbm(H, W, 9, 40, 4, 0.6)
    rgb = np.stack([np.interp(n, [0, 1], [SKIN1[k], SKIN0[k]]) for k in range(3)], -1)
    rgb *= (0.92 + 0.12 * m)[..., None]
    img = np.clip(rgb, 0, 255).astype(np.uint8)
    for i in range(70):                                 # skin creases: a soft criss-cross
        a = hsh(i, 1) * math.pi
        x0, y0 = hsh(i, 2) * W, hsh(i, 3) * H
        L = 300 + 500 * hsh(i, 4)
        p1 = (int(x0 - math.cos(a) * L), int(y0 - math.sin(a) * L))
        p2 = (int(x0 + math.cos(a) * L), int(y0 + math.sin(a) * L))
        cv2.line(img, p1, p2, (150, 84, 66), 2, cv2.LINE_AA)
    img = cv2.GaussianBlur(img, (0, 0), 1.2)
    cv2.imwrite(path, cv2.cvtColor(np.dstack([img, np.full((H, W), 255, np.uint8)]), cv2.COLOR_RGBA2BGRA))
    return skia.Image.open(path)


def _fog_texture():
    path = os.path.join(premium.CACHE, "fog.png")
    if os.path.exists(path):
        return skia.Image.open(path)
    os.makedirs(premium.CACHE, exist_ok=True)
    n = premium.fbm(H, W, 21, 90, 6, 0.6)
    a = np.clip(205 + 70 * (n - 0.5) * 2, 0, 255)
    for i in range(7):                                  # old runs where condensation already slid down
        x = int(hsh(i, 51) * W)
        L = int(300 + 900 * hsh(i, 52))
        a[:L, max(0, x - 4):x + 4] *= 0.72
    rgba = np.dstack([np.full((H, W, 3), FOG, np.float32), a]).astype(np.uint8)
    cv2.imwrite(path, cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))
    return skia.Image.open(path)


SKIN, FOGTEX = None, None
PORES = [(hsh(i, 11) * W, 300 + hsh(i, 12) * 1500, 0.4 + 0.6 * hsh(i, 13), hsh(i, 14)) for i in range(46)]


def sweat_level(t):
    return smooth(prog(t, 0.2, DURATION - 0.5))


def droplet(c, x, y, r, a=255):
    """A sweat bead: lighter body, dark rim, bright highlight, a caustic crescent."""
    c.drawCircle(x + r * 0.15, y + r * 0.2, r * 1.05, blur(fillp((90, 40, 30), 90 * a / 255), r * 0.2))
    c.drawCircle(x, y, r, shaded(radial((x - r * 0.25, y - r * 0.3), r * 1.3, [(255, 220, 200, ), (226, 160, 136), (150, 80, 62)], [0, 0.6, 1])))
    c.drawCircle(x, y, r, stroke((120, 56, 44), max(1, r * 0.08), 160 * a / 255))
    c.drawOval(skia.Rect.MakeXYWH(x - r * 0.55, y - r * 0.6, r * 0.5, r * 0.32), fillp((255, 255, 255), 230 * a / 255))
    c.drawArc(skia.Rect.MakeXYWH(x - r * 0.7, y - r * 0.7, r * 1.4, r * 1.4), 20, 80, False, stroke((255, 240, 220), max(1, r * 0.1), 150 * a / 255))


def scene(c, t):
    """Sharp skin with growing sweat beads."""
    global SKIN
    if SKIN is None:
        SKIN = _skin_texture()
    drift = 14 * math.sin(t * 0.4)
    c.save()
    c.translate(W / 2, H / 2)
    sc = lerp(1.0, 1.08, prog(t, 0, DURATION))
    c.scale(sc, sc)
    c.translate(-W / 2 + drift, -H / 2)
    c.drawImage(SKIN, 0, 0)
    lv = sweat_level(t)
    for i, (x, y, s, ph) in enumerate(PORES):
        c.drawCircle(x, y, 4 + 3 * s, fillp((110, 52, 40), 200))
        grow = clamp((lv - ph * 0.5) / 0.5)
        if grow <= 0:
            continue
        r = (10 + 38 * s) * smooth(grow)
        roll = max(0.0, grow - 0.8) * 5                # the fattest beads start to roll down
        yy = y + 260 * roll ** 2 if s > 0.75 else y
        if yy > y + 2:
            c.drawLine(x, y, x, yy, stroke((236, 180, 160), r * 1.2, 90))
        droplet(c, x, yy, r)
    c.restore()
    light(c, 760, 700, 900, (255, 170, 120), 90)
    c.drawPaint(shaded(radial((700, 800), 1400, [((0, 0, 0), 0), ((0, 0, 0), 0), ((20, 6, 4), 200)], [0, 0.45, 1])))


# ---------------------------------------------------------------- the captions, wiped into the fog
def build_phrases():
    ws = TM.words("C")
    lines, cur = [], []
    for w in ws:
        txt = " ".join(x[2] for x in cur + [w])
        if cur and (len(txt) > 18 or cur[-1][2].endswith(",") or w[2].lower() == "litre"):
            lines.append(cur)
            cur = []
        cur.append(w)
    lines.append(cur)
    out = []
    for li, line in enumerate(lines):
        s = " ".join(w for _, _, w in line)
        size = min(SIZE * 1.15, SIZE * 980 / width(s, "marker", SIZE))   # each phrase fills the width
        f = font("marker", size)
        x = 540 - width(s, "marker", size) / 2
        y = 1260
        glyphs = []
        for a, b, w in line:
            emph = w.lower().strip(".") in EMPH
            for k, ch in enumerate(w):
                if ch != " ":
                    gid = f.textToGlyphs(ch)[0]
                    gp = f.getPath(gid)
                    if gp is not None:
                        gp.offset(x, y)
                        fat = skia.Path()                       # a fingertip is wider than the font's stroke
                        stroke(PAPER_W, 16).getFillPath(gp, fat)
                        gp = skia.Op(gp, fat, skia.PathOp.kUnion_PathOp)
                        u0 = a + (b - a) * k / len(w)
                        glyphs.append(dict(path=gp, t0=u0, t1=u0 + (b - a) / len(w) + 0.05, x=x, w=f.measureText(ch), emph=emph))
                x += f.measureText(ch)
            x += f.measureText(" ")
        out.append(dict(glyphs=glyphs, t0=line[0][0], t1=line[-1][1], y=y, text=s))
    for i, p in enumerate(out):                         # each phrase fogs over just before the next one is wiped in
        p["fog_t"] = out[i + 1]["t0"] - 0.3 if i + 1 < len(out) else 1e9
    return out


PHRASES = build_phrases()
DRIPS = []
for pi, p in enumerate(PHRASES):
    for gi, g in enumerate(p["glyphs"]):
        if hsh(pi, gi, 5) > 0.72:
            b = g["path"].getBounds()
            DRIPS.append(dict(x=b.left() + b.width() * (0.3 + 0.4 * hsh(pi, gi, 6)), y=b.bottom() - 6, t0=g["t1"] + 0.1 + 0.4 * hsh(gi, 7),
                              speed=90 + 140 * hsh(pi, gi, 8), phrase=pi))


def clear_mask(t, pi):
    """Clip path for phrase pi at time t: glyphs wiped so far (left to right within each glyph) plus drip trails."""
    p = PHRASES[pi]
    m = skia.Path()
    for g in p["glyphs"]:
        u = prog(t, g["t0"], g["t1"])
        if u <= 0:
            continue
        if u >= 1:
            m = skia.Op(m, g["path"], skia.PathOp.kUnion_PathOp)
            continue
        b = g["path"].getBounds()
        r = skia.Path()
        r.addRect(skia.Rect.MakeLTRB(b.left() - 4, b.top() - 4, b.left() + (b.width() + 8) * u, b.bottom() + 4))
        m = skia.Op(m, skia.Op(g["path"], r, skia.PathOp.kIntersect_PathOp), skia.PathOp.kUnion_PathOp)
    for d in DRIPS:
        if d["phrase"] != pi or t < d["t0"]:
            continue
        L = d["speed"] * (t - d["t0"]) * (0.6 + 0.4 * math.sin((t - d["t0"]) * 3) ** 2)
        tr = skia.Path()
        tr.addRRect(rrect(d["x"] - 7, d["y"] - 4, 14, L + 8, 7))
        tr.addCircle(d["x"], d["y"] + L + 6, 11)
        m = skia.Op(m, tr, skia.PathOp.kUnion_PathOp)
    return m


def fingertip(c, t):
    """The soft blob of the fingertip at the front of the word being written."""
    for p in PHRASES:
        for g in p["glyphs"]:
            if g["t0"] <= t < g["t1"]:
                u = prog(t, g["t0"], g["t1"])
                b = g["path"].getBounds()
                x = b.left() + b.width() * u
                y = b.top() + b.height() * (0.3 + 0.4 * math.sin(u * math.pi * 3) ** 2)
                c.drawCircle(x, y, 34, blur(fillp((255, 255, 255), 110), 14))
                return


GLASS_DROPS = [(hsh(i, 41) * W, 400 + hsh(i, 42) * 1300, 14 + 34 * hsh(i, 43) ** 2) for i in range(26)]


def lens_drops(c, sharp, t):
    """Water drops on the glass refract the scene: each shows the skin behind it, flipped and shrunk."""
    for x, y, r in GLASS_DROPS:
        yy = y + (40 * (t - 2) if r > 40 and t > 2 else 0)
        c.save()
        cp = skia.Path()
        cp.addCircle(x, yy, r)
        c.clipPath(cp, doAntiAlias=True)
        c.translate(x, yy)
        c.scale(-0.45, -0.45)
        c.translate(-x, -yy)
        c.drawImage(sharp, 0, 0)
        c.restore()
        c.drawCircle(x, yy, r, stroke((255, 255, 255), max(1.5, r * 0.08), 120))
        c.drawCircle(x - r * 0.3, yy - r * 0.35, r * 0.22, fillp((255, 255, 255), 220))
        c.drawArc(skia.Rect.MakeXYWH(x - r, yy - r, 2 * r, 2 * r), 30, 100, False, stroke((40, 20, 20), r * 0.12, 90))


def chips(c, t):
    lv = sweat_level(t)
    for i, (lab, val, rgb) in enumerate((("CORE TEMP", f"{37.0 + 1.5 * lv:.1f}°C", (255, 120, 90)),
                                         ("SWEAT", f"{1.2 * lv:.1f} L/H", (120, 200, 255)))):
        x = 72 + i * 470
        c.drawRRect(rrect(x, 220, 420, 130, 24), fillp((255, 255, 255), 70))
        c.drawRRect(rrect(x, 220, 420, 130, 24), stroke((255, 255, 255), 3, 160))
        label(c, lab, x + 28, 266, 24, "mono_bold", (60, 50, 60), 230, tracking=0.12)
        label(c, val, x + 28, 330, 60, "overpass_black", rgb, 255)


def draw_frame(c, t):
    global FOGTEX
    if FOGTEX is None:
        FOGTEX = _fog_texture()
    s = skia.Surface(W, H)
    sc = s.getCanvas()
    scene(sc, t)
    sharp = s.makeImageSnapshot()
    # fogged view: blurred scene plus condensation
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(26, 26))
    c.drawImage(sharp, 0, 0, skia.SamplingOptions(), p)
    fa = skia.Paint()
    fa.setAlphaf(0.96)
    c.drawImage(FOGTEX, 0, 0, skia.SamplingOptions(), fa)
    # wiped-clear letters
    for pi, ph in enumerate(PHRASES):
        if t < ph["t0"] - 0.1:
            continue
        refog = smooth(prog(t, ph["fog_t"], ph["fog_t"] + 0.3))
        if refog >= 1:
            continue
        m = clear_mask(t, pi)
        c.save()
        c.clipPath(m, doAntiAlias=True)
        c.saveLayerAlpha(None, int(255 * (1 - refog)))
        c.drawImage(sharp, 0, 0)
        c.drawPaint(fillp((30, 8, 4), 90))                       # through the wiped glass the skin looks deeper and sharper
        emph = any(g["emph"] and g["t0"] <= t for g in ph["glyphs"])
        if emph:
            c.drawPaint(fillp((255, 70, 30), 60))
        c.restore()
        c.restore()
        # the edge of the wiped area catches the light
        c.drawPath(m, stroke((255, 255, 255), 5, 150 * (1 - refog)))
        c.drawPath(m, blur(stroke((255, 255, 255), 14, 70 * (1 - refog)), 8))
    lens_drops(c, sharp, t)
    fingertip(c, t)
    chips(c, t)
    style_tag(c, t, "STYLE C · FOGGED GLASS", DURATION)
    k = max(1 - smooth(prog(t, 0, 0.3)), smooth(prog(t, DURATION - 0.25, DURATION)))
    if k > 0:
        c.drawPaint(fillp((0, 0, 0), 255 * k))


def POST(t):
    return dict(grain=4.5, ca=0.6, bloom=0.6)


def sfx_events():
    ev = [(0.0, "room_tone", 0.5)]
    for p in PHRASES:
        for g in p["glyphs"][::2]:
            ev.append((g["t0"], "squeak", 0.25))
    for d in DRIPS:
        ev.append((d["t0"], "drip", 0.3))
    return ev


MUSIC = dict(beds=[(0.0, DURATION, "wonder", 0.45)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
