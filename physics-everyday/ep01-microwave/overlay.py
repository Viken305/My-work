"""2D layer over the 3D frame: word-by-word captions, 3D-anchored labels, brackets, equation cards, HUDs, end card."""
import math, os

import numpy as np
import skia

from kitchen import COLD, CX0, CX1, CY0, CZ0, CZ1, HOT, clamp, heat_at, lerp, out_back, out_expo, prog, smooth

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
_TF = {}
YELLOW = (255, 214, 10)


def tf(name):
    if name not in _TF:
        _TF[name] = skia.Typeface.MakeFromFile(os.path.join(FONTS, name))
    return _TF[name]


def font(size, w="black"):
    f = skia.Font(tf({"black": "InterDisplay-Black.otf", "bold": "InterDisplay-Bold.otf", "semi": "InterDisplay-SemiBold.otf"}[w]), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def paint(rgb, a=1.0, stroke=0.0):
    p = skia.Paint(AntiAlias=True, Color=skia.Color(*[int(v) for v in rgb], int(255 * clamp(a))))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeJoin(skia.Paint.kRound_Join)
        p.setStrokeCap(skia.Paint.kRound_Cap)
    return p


def project(F, cam, p):
    import gl3d as G
    view = G.look_at(cam["eye"], cam["target"], roll=cam.get("roll", 0.0))
    proj = G.perspective(math.radians(cam["fov"]), F.W / F.H, cam["near"], cam["far"])
    q = proj @ view @ np.array([*p, 1.0])
    if q[3] <= 0:
        return None
    return (q[0] / q[3] * 0.5 + 0.5) * F.W, (1 - (q[1] / q[3] * 0.5 + 0.5)) * F.H


def outlined(c, s, x, y, f, fill=(255, 255, 255), a=1.0, align="center", stroke_k=0.16):
    w = f.measureText(s)
    x0 = x - w / 2 if align == "center" else x if align == "left" else x - w
    sz = f.getSize()
    sh = paint((0, 0, 0), 0.45 * a)
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sz * 0.08))
    c.drawString(s, x0 + sz * 0.03, y + sz * 0.06, f, sh)
    c.drawString(s, x0, y, f, paint((10, 10, 14), a, sz * stroke_k))
    c.drawString(s, x0, y, f, paint(fill, a))
    return w


def chip(c, s, x, y, size, bg, a=1.0, k=1.0, fg=(255, 255, 255)):
    if a <= 0 or k <= 0:
        return
    f = font(size)
    tw = f.measureText(s)
    ph = size * 1.55
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-tw / 2 - size * 0.55, -ph / 2, tw + size * 1.1, ph), ph / 2, ph / 2), paint(bg, 0.94 * a))
    c.drawString(s, -tw / 2, size * 0.36, f, paint(fg, a))
    c.restore()


def pin(c, F, cam, p, s, bg, t, t0, t1, size=36, rise=110):
    """Label on a stalk above a 3D point."""
    a = smooth(prog(t, t0, t0 + 0.15)) * (1 - smooth(prog(t, t1 - 0.2, t1)))
    pp = project(F, cam, p)
    if a <= 0 or pp is None:
        return
    k = out_back(prog(t, t0, t0 + 0.28))
    bx, by = pp
    yy = by - rise * k
    c.drawLine(bx, by, bx, yy, paint((255, 255, 255), 0.9 * a, 4))
    c.drawCircle(bx, by, 7, paint((255, 255, 255), a))
    chip(c, s, bx, yy - size * 0.8, size, bg, a, k)


def bracket(c, p0, p1, label, a, k, size=38, up=True, color=(255, 255, 255)):
    if a <= 0 or p0 is None or p1 is None:
        return
    (x0, y0), (x1, y1) = p0, p1
    d = -1 if up else 1
    off = 34 * d
    xm = lerp(x0, x1, 0.5)
    ym = min(y0, y1) + off if up else max(y0, y1) + off
    x1k = lerp(xm, x1, k)
    x0k = lerp(xm, x0, k)
    pth = skia.Path()
    pth.moveTo(x0k, ym - off * 0.6)
    pth.lineTo(x0k, ym)
    pth.lineTo(x1k, ym)
    pth.lineTo(x1k, ym - off * 0.6)
    c.drawPath(pth, paint((10, 10, 14), a * 0.8, 11))
    c.drawPath(pth, paint(color, a, 5))
    if k > 0.6:
        outlined(c, label, xm, ym + (-22 if up else size + 18), font(size), YELLOW, a * smooth((k - 0.6) / 0.4))


# ---------------------------------------------------------------- captions
_PAGES = None


def pages(F):
    global _PAGES
    if _PAGES is None:
        words = []
        for key, item in F.TL.items():
            ws = item["text"].replace("...", "… ").split()
            wts = [len(w.strip(".,?…")) + 2 + (5 if w[-1] in ".?…" else 2 if w[-1] == "," else 0) for w in ws]
            tot = sum(wts)
            t = item["start"] + 0.08
            span = item["dur"] - 0.2
            for w, wt in zip(ws, wts):
                d = span * wt / tot
                words.append((t, t + d, w.strip("…").upper()))
                t += d
        _PAGES, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) == 3 or w[2][-1] in ".?,":
                _PAGES.append(cur)
                cur = []
        if cur:
            _PAGES.append(cur)
    return _PAGES


def captions(c, F, t):
    ps = pages(F)
    for i, pg in enumerate(ps):
        t0, t1 = pg[0][0], pg[-1][1] + 0.15
        if i + 1 < len(ps):
            t1 = min(t1, ps[i + 1][0][0])
        if not (t0 <= t < t1):
            continue
        size = 92
        f = font(size)
        gap = size * 0.28
        ws = [f.measureText(w[2]) for w in pg]
        total = sum(ws) + gap * (len(pg) - 1)
        scale = min(1.0, (F.W - 90) / total)
        pop = out_back(prog(t, t0, t0 + 0.12), 2.0)
        c.save()
        c.translate(F.W / 2, F.H * 0.70)
        s = lerp(0.8, 1.0, pop) * scale
        c.scale(s, s)
        x = -total / 2
        for (ws0, we, w), ww in zip(pg, ws):
            active = ws0 <= t < we + 0.05
            outlined(c, w, x, size * 0.35, f, YELLOW if active else (255, 255, 255), align="left")
            x += ww + gap
        c.restore()


# ---------------------------------------------------------------- per-scene graphics
def thermal_hud(c, F, t):
    th = F.thermal_amount(t)
    if th <= 0:
        return
    f = font(34, "bold")
    blink = 1.0 if int(t * 2.5) % 2 == 0 else 0.35
    y = 230
    c.drawCircle(70, y - 12, 13, paint((255, 60, 60), th * blink))
    outlined(c, "THERMAL VIEW", 96, y, f, (255, 255, 255), th, "left", 0.1)
    x0, y0, bw, bh = F.W - 80, 320, 22, 380
    p = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, y0 + bh), skia.Point(0, y0)],
        [skia.Color(10, 30, 140), skia.Color(46, 107, 255), skia.Color(192, 44, 180), skia.Color(255, 75, 31), skia.Color(255, 216, 74)]))
    p.setAlphaf(th)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, bw, bh), 8, 8), p)
    f2 = font(26, "bold")
    outlined(c, "HOT", x0 - 14, y0 + 22, f2, (255, 255, 255), th, "right", 0.1)
    outlined(c, "COLD", x0 - 14, y0 + bh, f2, (255, 255, 255), th, "right", 0.1)


def big_counter(c, F, t):
    t0 = F.C("05", 1.0)
    if not (t0 <= t < 24.0):
        return
    a = smooth(prog(t, t0, t0 + 0.2)) * (1 - smooth(prog(t, 23.7, 24.0)))
    v = int(2_450_000_000 * out_expo(prog(t, t0, t0 + 1.6)))
    s = f"{v:,}"
    f = font(112)
    # fixed-width digits so the number doesn't wobble while it counts
    cell = f.measureText("0")
    widths = [cell * 0.42 if ch == "," else cell for ch in s]
    total = sum(widths)
    sc = min(1.0, (F.W - 80) / total)
    c.save()
    c.translate(F.W / 2, 330)
    c.scale(sc, sc)
    x = -total / 2
    for ch, cw in zip(s, widths):
        outlined(c, ch, x + cw / 2, 0, f, (255, 255, 255), a)
        x += cw
    c.restore()
    outlined(c, "TIMES EVERY SECOND", F.W / 2, 420, font(52), YELLOW, a * smooth(prog(t, t0 + 0.8, t0 + 1.1)))
    outlined(c, "(2.45 GHz)", F.W / 2, 485, font(36, "bold"), (255, 255, 255), a * smooth(prog(t, t0 + 1.2, t0 + 1.5)), stroke_k=0.12)


def molecule_graphics(c, F, t, cam):
    if not (24.0 <= t < 37.2):
        return
    MW = F.MW
    a = smooth(prog(t, F.C("06", 1.4), F.C("06", 1.7))) * (1 - smooth(prog(t, 29.9, 30.15)))
    if a > 0:
        pO = project(F, cam, tuple(MW + np.array([0.0, -0.1, 1.75])))
        pH = project(F, cam, tuple(MW + np.array([0.0, 0.62, 1.7])))
        k1 = out_back(prog(t, F.C("06", 1.4), F.C("06", 1.7)))
        k2 = out_back(prog(t, F.C("06", 3.6), F.C("06", 3.9)))
        if pO:
            chip(c, "δ−  NEGATIVE", pO[0], pO[1] + 150, 40, (46, 107, 255), a, k1)
        if pH:
            chip(c, "δ+  POSITIVE", pH[0], pH[1] - 170, 40, (230, 57, 70), a * smooth(prog(t, F.C("06", 3.6), F.C("06", 3.8))), k2)
    sa = smooth(prog(t, 30.3, 30.6)) * (1 - smooth(prog(t, 36.9, 37.2)))
    if sa > 0:
        chip(c, "SLOWED DOWN ~3,000,000,000×", F.W / 2, 250, 30, (20, 22, 40), sa)
        outlined(c, "E-FIELD", F.W / 2, 330, font(40), (255, 216, 74), sa * 0.9, stroke_k=0.12)
    ha = smooth(prog(t, F.C("08", 0.1), F.C("08", 0.4))) * (1 - smooth(prog(t, 36.9, 37.2)))
    if ha > 0:
        k = out_back(prog(t, F.C("08", 0.1), F.C("08", 0.45)), 2.0)
        c.save()
        c.translate(F.W / 2, F.H * 0.42)
        c.scale(k, k)
        outlined(c, "= HEAT", 0, 0, font(150), (255, 106, 26), ha)
        c.restore()


def potato_graphics(c, F, t, cam):
    if not (37.2 <= t < 46.6):
        return
    rx, ry, _ = F.POT_R
    P = F.POT
    a = smooth(prog(t, F.C("09", 3.3), F.C("09", 3.6))) * (1 - smooth(prog(t, 46.3, 46.6)))
    k = out_expo(prog(t, F.C("09", 3.3), F.C("09", 3.9)))
    p0 = project(F, cam, tuple(P + np.array([rx, 0.0, 0.01])))
    p1 = project(F, cam, tuple(P + np.array([rx * 0.76, 0.0, 0.01])))
    if p0 and p1:
        bracket(c, p1, p0, "1–2 cm", a, k, size=44, up=True)
    ca = smooth(prog(t, F.C("09", 4.6), F.C("09", 4.9))) * (1 - smooth(prog(t, F.C("09", 7.2), F.C("09", 7.6))))
    pc = project(F, cam, tuple(P + np.array([0.0, 0.0, 0.01])))
    if pc:
        chip(c, "STILL COLD", pc[0], pc[1] + 10, 40, (46, 107, 255), ca, out_back(prog(t, F.C("09", 4.6), F.C("09", 4.9))))
    if t < F.C("09", 3.0):
        b = smooth(prog(t, 37.6, 38.0)) * (1 - smooth(prog(t, F.C("09", 2.7), F.C("09", 3.0))))
        outlined(c, "MYTH:", F.W / 2, 330, font(64), (255, 255, 255), b)
        outlined(c, "“COOKS FROM THE INSIDE OUT”", F.W / 2, 410, font(52), (255, 255, 255), b)
        if t > F.C("09", 1.0):
            k2 = out_back(prog(t, F.C("09", 1.0), F.C("09", 1.25)), 2.0)
            c.save()
            c.translate(F.W / 2, 540)
            c.rotate(-8)
            c.scale(k2, k2)
            outlined(c, "WRONG", 0, 40, font(150), (255, 59, 48), b)
            c.restore()


def heatmap_graphics(c, F, t, cam):
    if 46.6 <= t < 55.6:
        L = CX1 - CX0
        na = smooth(prog(t, F.C("11", 0.2), F.C("11", 0.6))) * (1 - smooth(prog(t, 55.3, 55.6)))
        pin(c, F, cam, (CX0 + 1.5 * L / 6, 0.75, 0.0), "ADD UP", (255, 75, 31), t, F.C("11", 0.3), 55.6, 34, 120)
        pin(c, F, cam, (CX0 + 2 * L / 6, 0.66, 0.0), "CANCEL", (46, 107, 255), t, F.C("11", 2.4), 55.6, 34, 70)
    if 55.6 <= t < 60.9:
        u = lambda f: lerp(CX0, CX1, f)  # noqa: E731
        v = lambda f: lerp(CZ0, CZ1 - 0.06, f)  # noqa: E731
        for x, z, s, col, t0 in [(u(0.5), v(0.75), "HOT", HOT, 56.6), (u(0.833), v(0.25), "HOT", HOT, 56.8), (u(0.33), v(0.5), "DEAD", COLD, 57.2)]:
            top = CY0 + 0.45 * float(heat_at(x, z)) + 0.04
            pin(c, F, cam, (x, top, z), s, col, t, t0, 58.35, 34, 100)
        a = smooth(prog(t, 58.5, 58.7)) * (1 - smooth(prog(t, 59.55, 59.75)))
        p0 = project(F, cam, (u(1 / 6), CY0 + 0.45 * float(heat_at(u(1 / 6), v(0.25))) + 0.02, v(0.25)))
        p1 = project(F, cam, (u(0.5), CY0 + 0.45 * float(heat_at(u(0.5), v(0.25))) + 0.02, v(0.25)))
        bracket(c, p0, p1, "≈ 6 cm", a, out_expo(prog(t, 58.5, 58.9)), size=48)


def stir_graphics(c, F, t):
    if not (65.4 <= t < 70.8):
        return
    a = smooth(prog(t, 66.3, 66.5)) * (1 - smooth(prog(t, 70.4, 70.7)))
    chip(c, "1. STIR", F.W / 2, 400, 56, (255, 75, 31), a, out_back(prog(t, 66.3, 66.55)))
    b = smooth(prog(t, 68.5, 68.7)) * (1 - smooth(prog(t, 70.4, 70.7)))
    chip(c, "2. WAIT 1 MIN", F.W / 2, 510, 56, (46, 107, 255), b, out_back(prog(t, 68.5, 68.75)))
    if b > 0:
        cx, cy, r = F.W / 2, 650, 56
        frac = prog(t, 68.7, 70.4)
        c.drawCircle(cx, cy, r, paint((255, 255, 255), b * 0.9, 8))
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r), -90, 360 * frac)
        c.drawPath(arc, paint(YELLOW, b, 10))
        c.drawLine(cx, cy, cx + r * 0.7 * math.sin(2 * math.pi * frac), cy - r * 0.7 * math.cos(2 * math.pi * frac), paint((255, 255, 255), b, 6))


def chocolate_graphics(c, F, t, cam):
    if 73.7 <= t < 76.7:
        a = smooth(prog(t, 73.9, 74.1)) * (1 - smooth(prog(t, 76.4, 76.7)))
        sec = max(0, 20 - int(20 * prog(t, 74.0, 75.7)))
        pp = project(F, cam, (0.7, 0.94, 0.75))
        if pp:
            chip(c, f"0:{sec:02d}", pp[0], pp[1] - 90, 44, (20, 22, 40), a, out_back(prog(t, 73.9, 74.15)), fg=(124, 255, 178))
        chip(c, "⏩ 20 SECONDS", F.W / 2, 330, 46, (255, 75, 31), a, out_back(prog(t, 73.9, 74.15)))
    if 76.7 <= t < 86.4:
        z = F.CHOC_Z
        y = CY0 + 0.075
        p0 = project(F, cam, (F.SPOTS[0], y, z - 0.05))
        p1 = project(F, cam, (F.SPOTS[1], y, z - 0.05))
        a = smooth(prog(t, 77.5, 77.7)) * (1 - smooth(prog(t, 83.0, 83.2)))
        bracket(c, p0, p1, "6 cm", a, out_expo(prog(t, 77.5, 78.0)), size=50)
        lines = [(77.6, "GAP  ≈  6 cm", (255, 255, 255)),
                 (79.5, "× 2  =  12 cm   (ONE WAVE)", (255, 255, 255)),
                 (80.8, "× 2,450,000,000 / s", (255, 255, 255)),
                 (83.3, "= 294,000 km/s", YELLOW)]
        card_a = smooth(prog(t, 77.6, 77.8)) * (1 - smooth(prog(t, 86.1, 86.4)))
        if card_a > 0:
            n_vis = sum(1 for t0, _, _ in lines if t >= t0)
            hgt = 70 + 78 * n_vis
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(60, 190, F.W - 120, hgt), 30, 30), paint((14, 16, 30), 0.78 * card_a))
            for i, (t0, s, col) in enumerate(lines):
                if t < t0:
                    continue
                k = out_back(prog(t, t0, t0 + 0.2), 2.0)
                c.save()
                c.translate(F.W / 2, 268 + i * 78)
                c.scale(k, k)
                sz = 58 if i < 3 else 66
                outlined(c, s, 0, 0, font(sz), col, card_a, stroke_k=0.1)
                c.restore()
        ra = smooth(prog(t, 83.9, 84.1)) * (1 - smooth(prog(t, 86.1, 86.4)))
        if ra > 0:
            k = out_back(prog(t, 83.9, 84.15), 2.0)
            c.save()
            c.translate(F.W / 2, F.H * 0.47)
            c.scale(k, k)
            outlined(c, "SPEED OF LIGHT", 0, 0, font(104), YELLOW, ra)
            outlined(c, "(real value: 299,792 km/s)", 0, 70, font(38, "bold"), (255, 255, 255), ra, stroke_k=0.12)
            c.restore()


def labels_xray(c, F, t, cam):
    pin(c, F, cam, (0.7, 0.72, -0.2), "MAGNETRON", (255, 75, 31), t, F.C("03", 1.6), 11.6, 40, 150)
    pin(c, F, cam, (0.56, 1.04, -0.2), "WAVEGUIDE", (46, 107, 255), t, 12.9, 15.3, 36, 130)
    a = smooth(prog(t, 15.5, 15.7)) * (1 - smooth(prog(t, 18.7, 18.9)))
    chip(c, "MICROWAVES = INVISIBLE LIGHT", F.W / 2, 300, 36, (20, 22, 40), a, out_back(prog(t, 15.5, 15.75)))


def end_card(c, F, t):
    a = smooth(prog(t, 89.6, 90.0))
    if a <= 0:
        return
    c.drawRect(skia.Rect.MakeWH(F.W, F.H), paint((8, 10, 20), 0.55 * a))
    k = out_back(prog(t, 89.6, 89.9), 1.8)
    c.save()
    c.translate(F.W / 2, F.H * 0.42)
    c.scale(k, k)
    outlined(c, "THE PHYSICS OF", 0, 0, font(70), (255, 255, 255), a)
    outlined(c, "EVERYDAY THINGS", 0, 86, font(86), YELLOW, a)
    outlined(c, "EP. 01  ·  MICROWAVES", 0, 160, font(40, "bold"), (255, 255, 255), a, stroke_k=0.1)
    c.restore()


def flashes(c, F, t):
    for tc in (5.85, 24.0, 37.2, 46.6, 86.4):
        if tc <= t < tc + 0.12:
            c.drawRect(skia.Rect.MakeWH(F.W, F.H), paint((255, 255, 255), 0.35 * (1 - prog(t, tc, tc + 0.12))))


def draw(img, t, cam, F):
    rgba = np.dstack([img, np.full(img.shape[:2], 255, np.uint8)]).copy()
    surf = skia.Surface(rgba)
    c = surf.getCanvas()
    thermal_hud(c, F, t)
    labels_xray(c, F, t, cam)
    big_counter(c, F, t)
    molecule_graphics(c, F, t, cam)
    potato_graphics(c, F, t, cam)
    heatmap_graphics(c, F, t, cam)
    stir_graphics(c, F, t)
    chocolate_graphics(c, F, t, cam)
    if t < 89.6:
        captions(c, F, t)
    end_card(c, F, t)
    flashes(c, F, t)
    return np.ascontiguousarray(rgba[:, :, :3])
