"""Night Shift kit: palettes per act, Sam, the HUD clock, rooms, the adenosine jar and other props, transitions.

Look rules: one character (Sam), one long night. The clock HUD and a 0-72 h timeline are in every shot. The picture
gets tired with Sam: cool blue and clean (0-24 h), amber with grain (24-48 h), red with wobble and RGB split (48-72 h).
"""
import math

import numpy as np
import skia

from engine import FPS, H, W, clamp, in_cubic, in_out, lerp, mix, out_back, out_cubic, out_expo, prog, smooth  # noqa: F401
from engine import blur, fill, glow, linear, poly, radial, rrect, shaded, stroke  # noqa: F401
from premium import add, light  # noqa: F401
from timing import Timing, schedule  # noqa: F401
from typo import ASH, PAPER, Captions, Counter, font, label, paint, reveal, width  # noqa: F401

PREMIUM, SAMPLES = True, 4

# ---------------------------------------------------------------- palettes
SAM = (201, 195, 255)
SAM_DK = (122, 111, 201)
INK = (12, 14, 24)
ACTS = {
    1: dict(top=(12, 16, 40), bot=(28, 36, 80), wall=(30, 38, 84), floor=(16, 20, 46), acc=(127, 212, 255), dim=(43, 53, 102)),
    2: dict(top=(26, 17, 10), bot=(56, 36, 18), wall=(64, 42, 20), floor=(30, 20, 10), acc=(242, 169, 59), dim=(90, 58, 23)),
    3: dict(top=(26, 6, 14), bot=(60, 14, 32), wall=(67, 20, 42), floor=(30, 8, 18), acc=(255, 77, 109), dim=(96, 26, 50)),
}
CYAN, AMBER, RED = ACTS[1]["acc"], ACTS[2]["acc"], ACTS[3]["acc"]


def blend_pal(a, b, k):
    return {key: mix(ACTS[a][key], ACTS[b][key], k) for key in ACTS[a]}


def fillp(rgb, a=255):
    return skia.Paint(AntiAlias=True, Color=skia.Color(*[int(x) for x in rgb], int(clamp(a / 255) * 255)))


def grad_v(y0, y1, c0, c1, a0=255, a1=255):
    return skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, y0), (0, y1)], [skia.Color(*[int(x) for x in c0], int(a0)), skia.Color(*[int(x) for x in c1], int(a1))]))


def bg(c, pal):
    c.drawRect(skia.Rect.MakeWH(W, H), grad_v(0, H, pal["top"], pal["bot"]))


def hsh(*a):
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return (h % 100003) / 100003.0


def path_of(pts, closed=False):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def shake(t, t0, amp=18.0, decay=6.0):
    if t < t0:
        return 0.0, 0.0
    k = amp * math.exp(-(t - t0) * decay)
    return k * math.sin(t * 71), k * math.cos(t * 53)


def fatigue_post(f, wobble=0.0, split=0.0):
    """Post settings for a fatigue level f in 0..1."""
    return dict(grain=4.0 + 9.0 * f, ca=0.5 + 1.6 * f, bloom=0.7, wobble=wobble, split=split)


# ---------------------------------------------------------------- transitions
def blink(c, t, t_mid, half=0.22, rgb=(0, 0, 0)):
    """Eyelid wipe: black closes from top and bottom to the middle at t_mid, then opens."""
    k = 1 - abs(t - t_mid) / half
    if k <= 0:
        return
    k = smooth(k)
    hh = H / 2 * k
    p = fillp(rgb)
    top = skia.Path()
    top.moveTo(0, 0)
    top.lineTo(W, 0)
    top.lineTo(W, hh)
    top.quadTo(W / 2, hh + 160 * k, 0, hh)
    top.close()
    bot = skia.Path()
    bot.moveTo(0, H)
    bot.lineTo(W, H)
    bot.lineTo(W, H - hh)
    bot.quadTo(W / 2, H - hh - 160 * k, 0, H - hh)
    bot.close()
    c.drawPath(top, p)
    c.drawPath(bot, p)


def fade_black(c, k):
    if k > 0:
        c.drawPaint(fillp((0, 0, 0), 255 * clamp(k)))


# ---------------------------------------------------------------- HUD
def clock_text(hour):
    tot = 7 * 60 + int(hour * 60)
    day = tot // (24 * 60) + 1
    hh, mm = (tot // 60) % 24, tot % 60
    return f"DAY {day} · {hh:02d}:{mm:02d}"


def hud(c, t, hour, acc, a=1.0, glitch=0.0, title=None, sub=None):
    """Hour counter, clock, and the 0-72 h timeline. Sits at the top, clear of the Shorts interface."""
    if a <= 0.01:
        return
    x0, x1, y = 72, 1008, 352
    al = 255 * a
    s = title or f"HOUR {int(hour):02d}"
    if glitch > 0:
        jx = 8 * glitch * math.sin(t * 93)
        label(c, s, 72 - 5 * glitch + jx, 256, 50, "mono_bold", CYAN, al * 0.6)
        label(c, s, 72 + 5 * glitch + jx, 256, 50, "mono_bold", RED, al * 0.6)
    label(c, s, 72, 256, 50, "mono_bold", acc, al)
    label(c, sub or clock_text(hour), 72, 302, 24, "mono", ASH, al * 0.9, tracking=0.06)
    c.drawLine(x0, y, x1, y, stroke(PAPER, 3, 50 * a))
    xm = lerp(x0, x1, clamp(hour / 72))
    c.drawLine(x0, y, xm, y, stroke(acc, 3, al))
    for h in (0, 24, 48, 72):
        xx = lerp(x0, x1, h / 72)
        c.drawLine(xx, y - 9, xx, y + 9, stroke(PAPER, 2, 90 * a))
        label(c, f"{h}h", xx, y + 44, 20, "mono", PAPER if hour >= h else ASH, al * (0.9 if hour >= h else 0.5),
              "center" if 0 < h < 72 else ("left" if h == 0 else "right"))
    light(c, xm, y, 40, acc, 90 * a)
    c.drawCircle(xm, y, 9, fillp(acc, al))


def hour_card(c, t, t0, num, acc, dur=1.4, sub="HOURS AWAKE"):
    """Big number slam: the hour lands with a settle and a shake, then the card hands back to the scene."""
    if t < t0 or t > t0 + dur:
        return 0.0
    u = prog(t, t0, t0 + dur)
    k = 1 - smooth(prog(t, t0 + dur - 0.3, t0 + dur))
    c.save()
    c.drawPaint(fillp((0, 0, 0), 235 * k))
    sc = lerp(1.6, 1.0, out_expo(prog(t, t0, t0 + 0.28)))
    dx, dy = shake(t, t0 + 0.2, 14, 7)
    c.translate(W / 2 + dx, 980 + dy)
    c.scale(sc, sc)
    s = str(num)
    wn = width(s, "display", 520)
    label(c, s, -wn / 2, 0, 520, "display", acc, 120 * k, sigma=30)
    label(c, s, -wn / 2, 0, 520, "display", PAPER, 255 * k)
    c.restore()
    reveal(c, sub, W / 2, 1100, 44, t, t0 + 0.2, "mono_bold", acc, 255 * k, "center", tracking=0.3, stagger=0.02, dur=0.3, blur=8)
    return k * (1 - u)


# ---------------------------------------------------------------- Sam
def sam(c, x, y, s, t, lid=0.0, bags=0.0, wide=0.0, mouth=0.6, look=(0.0, 0.0), tilt=0.0, a=255, blink_phase=0.0,
        slump=0.0, outline=None, arm=0.0, prop=None, idle=1.0):
    """Sam, in a lavender hoodie. (x, y) = bottom centre, s = head radius.
    lid 0..1 = upper eyelids closing, bags 0..1 = dark circles, wide 0..1 = staring eyes, mouth -1 frown .. 1 smile,
    slump 0..1 = head drops forward, outline = rgb draws an x-ray line version instead."""
    if a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    br = math.sin(t * 2.3 + x * 0.01) * idle                 # breathing: body swells, head rides on it
    bw, bh = s * 2.1 * (1 - 0.006 * br), s * 2.5 * (1 + 0.014 * br)
    hy = -bh - s * 0.72 + slump * s * 0.35 + s * 0.02 * math.sin(t * 2.3 + 0.7 + x * 0.01) * idle
    head_tilt = 2.2 * math.sin(t * 0.9 + x * 0.003) * idle
    if outline is None:
        c.drawOval(skia.Rect.MakeXYWH(-bw * 0.62, -s * 0.12, bw * 1.24, s * 0.24), blur(fillp((0, 0, 0), 90), 10))
    body = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-bw / 2, -bh, bw, bh), s * 0.85, s * 0.85)
    if outline is not None:                            # x-ray: one silhouette line, ribs, spine, a glowing brain
        bp = skia.Path()
        bp.addRRect(body)
        hp = skia.Path()
        hp.addCircle(0, hy, s)
        sil = skia.Op(bp, hp, skia.PathOp.kUnion_PathOp)
        c.drawPath(sil, fillp(outline, 28))
        c.drawPath(sil, stroke(outline, 6, 255))
        c.drawLine(0, -bh + s * 0.2, 0, -s * 0.5, stroke(outline, 5, 150))
        for i in range(5):
            yy = -bh + s * (0.45 + i * 0.27)
            ww = bw * (0.36 - 0.02 * i)
            rib = skia.Path()
            rib.moveTo(-ww, yy + s * 0.12)
            rib.quadTo(0, yy - s * 0.12, ww, yy + s * 0.12)
            c.drawPath(rib, stroke(outline, 4, 120))
        c.drawOval(skia.Rect.MakeXYWH(-s * 0.62, hy - s * 0.62, s * 1.24, s * 0.95), stroke(outline, 4, 170))
        c.restore()
        if a < 255:
            c.restore()
        return
    c.drawRRect(body, shaded(linear((-bw / 2, -bh), (bw / 2, 0), [mix(SAM, (255, 255, 255), 0.15), mix(SAM, SAM_DK, 0.35)])))
    # hoodie pocket + strings
    c.drawRRect(rrect(-bw * 0.3, -bh * 0.42, bw * 0.6, bh * 0.24, s * 0.2), fillp(SAM_DK, 70))
    for sx in (-0.16, 0.16):
        c.drawLine(sx * s, -bh + s * 0.15, sx * s * 1.2, -bh + s * 0.75, stroke((250, 250, 255), s * 0.05, 200))
    # arm (holding a prop)
    if arm > 0:
        c.save()
        c.translate(bw * 0.42, -bh * 0.75)
        c.rotate(-50 * arm)
        c.drawRRect(rrect(-s * 0.18, 0, s * 0.36, s * 1.2, s * 0.18), fillp(mix(SAM, SAM_DK, 0.25)))
        if prop == "donut":
            c.drawCircle(0, s * 1.35, s * 0.42, fillp((242, 169, 59)))
            c.drawCircle(0, s * 1.35, s * 0.36, fillp((255, 110, 170)))
            c.drawCircle(0, s * 1.35, s * 0.13, fillp((40, 24, 12)))
        elif prop == "mug":
            c.drawRRect(rrect(-s * 0.32, s * 1.05, s * 0.64, s * 0.62, s * 0.1), fillp((245, 245, 250)))
            c.drawRect(skia.Rect.MakeXYWH(-s * 0.26, s * 1.1, s * 0.52, s * 0.12), fillp((90, 54, 30)))
        c.restore()
    # head
    c.save()
    c.translate(0, hy)
    c.rotate(slump * 8 + head_tilt)
    c.drawCircle(s * 0.06, s * 0.1, s, blur(fillp((0, 0, 0), 60), s * 0.12))
    c.drawCircle(0, 0, s, shaded(radial((-s * 0.35, -s * 0.4), s * 1.6, [mix(SAM, (255, 255, 255), 0.3), SAM, mix(SAM, SAM_DK, 0.3)], [0, 0.5, 1])))
    tuft = skia.Path()
    tuft.moveTo(-s * 0.1, -s * 0.96)
    tuft.cubicTo(-s * 0.05, -s * 1.35, s * 0.35, -s * 1.3, s * 0.25, -s * 1.05)
    c.drawPath(tuft, stroke(mix(SAM, SAM_DK, 0.4), s * 0.09))
    _face(c, s, t, lid, bags, wide, mouth, look, blink_phase)
    c.restore()
    c.restore()
    if a < 255:
        c.restore()


def _face(c, s, t, lid, bags, wide, mouth, look, blink_phase):
    cyc = (t + blink_phase * 4.1) % 4.1
    bl = 1 - abs(cyc - 4.0) / 0.1 if abs(cyc - 4.0) < 0.1 else 0.0
    lid = clamp(max(lid, bl))
    lx, ly = look[0] * s * 0.1, look[1] * s * 0.08
    for sx in (-1, 1):
        ex, ey = sx * s * 0.36 + lx, -s * 0.05 + ly
        if bags > 0:                                   # dark circles
            c.drawArc(skia.Rect.MakeXYWH(ex - s * 0.2, ey - s * 0.02, s * 0.4, s * 0.3), 20, 140, False,
                      stroke(SAM_DK, s * 0.045, 200 * bags))
        er = s * (0.12 + 0.1 * wide)
        if wide > 0:
            c.drawCircle(ex, ey, er, fillp((255, 255, 255), 255 * min(1, wide * 2)))
            c.drawCircle(ex + look[0] * er * 0.2, ey, er * lerp(0.95, 0.32, wide), fillp(INK))
        else:
            c.drawCircle(ex, ey, er, fillp(INK))
            c.drawCircle(ex - er * 0.3, ey - er * 0.35, er * 0.32, fillp((255, 255, 255), 220))
        if lid > 0:                                    # eyelid: skin covering the top of the eye
            c.save()
            cl = skia.Path()
            cl.addCircle(ex, ey, er * 1.12)
            c.clipPath(cl, doAntiAlias=True)
            top = ey - er * 1.15
            c.drawRect(skia.Rect.MakeLTRB(ex - er * 1.3, top, ex + er * 1.3, top + er * 2.3 * lid), fillp(mix(SAM, SAM_DK, 0.12)))
            c.restore()
            yl = ey - er * 1.15 + er * 2.3 * lid
            c.drawLine(ex - er * 1.05, yl, ex + er * 1.05, yl, stroke(INK, s * 0.04, 230 * min(1, lid * 3)))
    my = s * 0.42 + ly
    if mouth == "o":
        c.drawOval(skia.Rect.MakeXYWH(-s * 0.09 + lx, my - s * 0.08, s * 0.18, s * 0.2), fillp(INK))
        return
    m = skia.Path()
    m.moveTo(-s * 0.16 + lx, my)
    m.quadTo(lx, my + s * 0.16 * mouth, s * 0.16 + lx, my)
    c.drawPath(m, stroke(INK, s * 0.055))


# ---------------------------------------------------------------- environments
def room(c, t, pal, sun=0.0, moon=0.0, lamp=0.0, floor_y=1290, win=(90, 470, 300, 300)):
    """Sam's bedroom: wall, window (sun or moon), floor, a lamp glow."""
    bg(c, pal)
    c.drawRect(skia.Rect.MakeLTRB(0, 420, W, floor_y), grad_v(420, floor_y, pal["wall"], mix(pal["wall"], pal["top"], 0.4)))
    wx, wy, ww, wh = win
    sky = grad_v(wy, wy + wh, mix(pal["top"], (255, 150, 90), 0.5 * sun), mix(pal["bot"], (255, 200, 120), 0.6 * sun))
    c.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), sky)
    if sun > 0:
        sy = wy + wh - 70 - 110 * sun
        light(c, wx + ww * 0.6, sy, 220, (255, 170, 90), 140 * sun)
        c.drawCircle(wx + ww * 0.6, sy, 46, fillp((255, 196, 110), 255 * sun))
    if moon > 0:
        mx, my = wx + ww * 0.65, wy + 110
        light(c, mx, my, 160, (200, 210, 255), 60 * moon)
        c.drawCircle(mx, my, 38, fillp((235, 235, 255), 255 * moon))
        c.drawCircle(mx + 16, my - 10, 34, fillp(mix(pal["top"], pal["bot"], 0.3), 255 * moon))
        for i in range(9):
            c.drawCircle(wx + 30 + hsh(i, 1) * (ww - 60), wy + 30 + hsh(i, 2) * (wh - 60), 2.2,
                         fillp((255, 255, 255), 160 * moon * (0.5 + 0.5 * math.sin(t * 2 + i))))
    fr = stroke(mix(pal["wall"], (0, 0, 0), 0.45), 14)
    c.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), fr)
    c.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, stroke(mix(pal["wall"], (0, 0, 0), 0.45), 10))
    c.drawLine(wx, wy + wh / 2, wx + ww, wy + wh / 2, stroke(mix(pal["wall"], (0, 0, 0), 0.45), 10))
    c.drawRect(skia.Rect.MakeLTRB(0, floor_y, W, H), grad_v(floor_y, H, mix(pal["floor"], pal["wall"], 0.5), mix(pal["floor"], (0, 0, 0), 0.4)))
    for i in range(1, 9):                              # floorboards in perspective
        x0 = W / 2 + (i - 4.5) * 150
        c.drawLine(x0, floor_y, W / 2 + (x0 - W / 2) * 2.6, H, stroke(mix(pal["floor"], (0, 0, 0), 0.3), 3, 160))
    c.drawLine(0, floor_y, W, floor_y, stroke(mix(pal["wall"], (255, 255, 255), 0.12), 3, 120))
    if lamp > 0:
        light(c, 170, 760, 520, pal["acc"], 60 * lamp)


def alarm_clock(c, x, y, s, t, txt="07:00", ring=0.0, acc=CYAN):
    jx = 5 * ring * math.sin(t * 60)
    c.save()
    c.translate(x + jx, y)
    c.drawRRect(rrect(-s, -s * 0.62, s * 2, s * 1.24, s * 0.25), fillp((24, 28, 58)))
    c.drawRRect(rrect(-s, -s * 0.62, s * 2, s * 1.24, s * 0.25), stroke(acc, 3, 180))
    wt = width(txt, "mono_bold", s * 0.62)
    label(c, txt, -wt / 2, s * 0.22, s * 0.62, "mono_bold", acc, 255)
    light(c, 0, 0, s * 1.6, acc, 40)
    c.restore()
    if ring > 0:
        for k in range(2):
            r = s * (1.3 + 0.35 * k + 0.2 * ((t * 3) % 1))
            for sg in (-1, 1):
                c.drawArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), -90 + sg * 60 - 18, 36, False,
                          stroke(acc, 4, 200 * ring * (1 - 0.4 * k)))


def jar(c, x, y, w, h, level, t, acc, a=1.0, label_a=1.0, sleeve=0.0, sleeve_txt="CAFFEINE", glow_k=0.0):
    """The adenosine jar. (x, y) = bottom centre. level 0..1."""
    if a <= 0.01:
        return
    al = 255 * a
    left, top = x - w / 2, y - h
    body = rrect(left, top, w, h, w * 0.16)
    c.drawRRect(body, fillp((255, 255, 255), 18 * a))
    # liquid
    lv = clamp(level)
    if lv > 0.001:
        c.save()
        c.clipRRect(body, doAntiAlias=True)
        ly = y - h * 0.94 * lv - 8
        wave = skia.Path()
        wave.moveTo(left, ly)
        for i in range(41):
            xx = left + w * i / 40
            wave.lineTo(xx, ly + 7 * math.sin(i * 0.5 + t * 3.2) * (0.4 + 0.6 * lv))
        wave.lineTo(x + w / 2, y)
        wave.lineTo(left, y)
        wave.close()
        c.drawPath(wave, shaded(linear((0, ly), (0, y), [(mix(acc, (255, 255, 255), 0.25), al * 0.9), (mix(acc, (0, 0, 0), 0.35), al)])))
        for i in range(10):                            # bubbles
            bx = left + w * (0.15 + 0.7 * hsh(i, 3))
            ph = (t * (0.3 + 0.3 * hsh(i, 4)) + hsh(i, 5)) % 1
            by = y - ph * (y - ly)
            c.drawCircle(bx + 6 * math.sin(t * 2 + i), by, 4 + 5 * hsh(i, 6), stroke((255, 255, 255), 2, 120 * a * (1 - ph)))
        c.restore()
        if glow_k > 0:
            light(c, x, ly + (y - ly) / 2, w * 1.1, acc, 70 * glow_k * a)
    if sleeve > 0:                                     # coffee sleeve hides the level
        sh = h * 0.62 * smooth(sleeve)
        c.drawRRect(rrect(left - 10, y - sh - 4, w + 20, sh + 8, 22), fillp((96, 58, 32), al * 0.72))
        c.drawRRect(rrect(left - 10, y - sh - 4, w + 20, sh + 8, 22), stroke((150, 98, 60), 4, al))
        if sleeve > 0.7:
            tw = width(sleeve_txt, "mono_bold", 34, 0.12)
            label(c, sleeve_txt, x - tw / 2, y - sh / 2 + 12, 34, "mono_bold", (240, 220, 200), al * smooth(prog(sleeve, 0.7, 1)), tracking=0.12)
    # glass: rim highlight, lid
    c.drawRRect(body, stroke((230, 236, 255), 6, 200 * a))
    c.drawLine(left + w * 0.14, top + h * 0.12, left + w * 0.14, top + h * 0.6, stroke((255, 255, 255), 8, 70 * a))
    c.drawRRect(rrect(left - 18, top - 46, w + 36, 58, 16), fillp((210, 214, 235), al))
    c.drawRRect(rrect(left - 18, top - 46, w + 36, 58, 16), stroke((150, 156, 190), 3, al))
    if label_a > 0:
        tw = width("ADENOSINE", "mono_bold", 30, 0.14)
        label(c, "ADENOSINE", x - tw / 2, top - 78, 30, "mono_bold", acc, al * label_a, tracking=0.14)
        tw = width("sleep pressure", "regular", 30)
        label(c, "sleep pressure", x - tw / 2, y + 56, 30, "regular", ASH, al * label_a)


def mug(c, x, y, s, tilt=0.0, a=255, steam=0.0, t=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.drawRRect(rrect(-s * 0.55, -s, s * 1.1, s * 1.2, s * 0.18), fillp((245, 245, 250), a))
    c.drawArc(skia.Rect.MakeXYWH(s * 0.38, -s * 0.75, s * 0.5, s * 0.6), -90, 180, False, stroke((245, 245, 250), s * 0.12, a))
    c.drawRect(skia.Rect.MakeXYWH(-s * 0.47, -s * 0.92, s * 0.94, s * 0.16), fillp((90, 54, 30), a))
    c.restore()
    for i in range(3):
        if steam <= 0:
            break
        ph = (t * 0.6 + i / 3) % 1
        sp = skia.Path()
        sx = x - s * 0.3 + i * s * 0.3
        sp.moveTo(sx, y - s * 1.1)
        sp.cubicTo(sx - 20, y - s * 1.4 - ph * 60, sx + 20, y - s * 1.6 - ph * 60, sx, y - s * 1.9 - ph * 60)
        c.drawPath(sp, stroke((255, 255, 255), 5, 110 * steam * (1 - ph)))


def brain(c, cx, cy, s, t, front_dim=0.0, amyg=0.0, acc=AMBER):
    """Side view of a brain (front faces left). front_dim dims the prefrontal cortex, amyg lights the amygdala."""
    def P(u, v):
        return cx + u * s, cy + v * s
    outline = skia.Path()
    pts = [(-1.0, 0.15), (-0.98, -0.3), (-0.75, -0.7), (-0.3, -0.92), (0.2, -0.9), (0.62, -0.7), (0.92, -0.3),
           (0.95, 0.12), (0.78, 0.42), (0.45, 0.52), (0.2, 0.7), (-0.05, 0.62), (-0.45, 0.6), (-0.85, 0.45)]
    from engine import smooth_closed
    outline = smooth_closed([P(u, v) for u, v in pts])
    c.drawPath(outline, shaded(radial(P(-0.2, -0.3), s * 1.5, [mix(acc, (255, 255, 255), 0.25), mix(acc, (0, 0, 0), 0.25)])))
    # folds
    folds = [((-0.75, -0.3), (-0.5, -0.55), (-0.2, -0.4)), ((-0.6, 0.1), (-0.3, -0.1), (0.0, 0.05)),
             ((0.05, -0.6), (0.3, -0.4), (0.55, -0.55)), ((0.2, -0.1), (0.45, 0.05), (0.75, -0.1)),
             ((-0.85, -0.05), (-0.7, 0.2), (-0.45, 0.3)), ((0.0, 0.3), (0.3, 0.25), (0.55, 0.35))]
    for a0, a1, a2 in folds:
        fp = skia.Path()
        fp.moveTo(*P(*a0))
        fp.quadTo(*P(*a1), *P(*a2))
        c.drawPath(fp, stroke(mix(acc, (0, 0, 0), 0.45), s * 0.035, 200))
    c.drawPath(outline, stroke(mix(acc, (255, 255, 255), 0.4), s * 0.03, 220))
    # brain stem + cerebellum
    c.drawRRect(rrect(cx + 0.18 * s, cy + 0.55 * s, 0.2 * s, 0.5 * s, 0.08 * s), fillp(mix(acc, (0, 0, 0), 0.3)))
    c.drawOval(skia.Rect.MakeXYWH(cx + 0.42 * s, cy + 0.38 * s, 0.5 * s, 0.32 * s), fillp(mix(acc, (0, 0, 0), 0.2)))
    if front_dim > 0:                                  # prefrontal cortex going dark
        c.save()
        c.clipPath(outline, doAntiAlias=True)
        c.drawCircle(*P(-0.85, -0.25), s * 0.62, blur(fillp((10, 6, 4), 210 * front_dim), s * 0.12))
        c.restore()
    if amyg > 0:
        ax, ay = P(-0.05, 0.28)
        pul = 0.75 + 0.25 * math.sin(t * 9)
        light(c, ax, ay, s * 0.9 * amyg, RED, 200 * amyg * pul)
        c.drawCircle(ax, ay, s * 0.09, fillp((255, 120, 140), 255 * min(1, amyg * 2)))


def gauge_bar(c, x, y, w, h, level, rgb, a=1.0):
    """Vertical meter (x, y = bottom-left)."""
    c.drawRRect(rrect(x, y - h, w, h, 18), fillp((0, 0, 0), 120 * a))
    c.drawRRect(rrect(x, y - h, w, h, 18), stroke(mix(rgb, (255, 255, 255), 0.2), 4, 200 * a))
    lh = (h - 20) * clamp(level)
    if lh > 1:
        c.drawRRect(rrect(x + 10, y - 10 - lh, w - 20, lh, 10), fillp(rgb, 255 * a))
        light(c, x + w / 2, y - 10 - lh, w * 1.2, rgb, 60 * a)


def body_xray(c, x, y, s, t, acc, dots=0.0, a=1.0):
    """Sam as an x-ray outline with spreading inflammation dots."""
    sam(c, x, y, s, t, outline=acc, a=255 * a)
    bw, bh = s * 2.1, s * 2.5
    c.drawRRect(rrect(x - bw / 2 + 14, y - bh + 14, bw - 28, bh - 28, s * 0.7), fillp(acc, 30 * a))
    # heart
    hx, hy = x - s * 0.25, y - bh * 0.7
    pul = 1 + 0.12 * max(0, math.sin(t * 9.0)) ** 8
    c.drawCircle(hx, hy, s * 0.22 * pul, fillp(RED, 230 * a))
    light(c, hx, hy, s * 0.7, RED, 90 * a)
    n = int(60 * dots)
    for i in range(n):
        px = x + (hsh(i, 11) - 0.5) * (bw - 50)
        py = y - 30 - hsh(i, 12) * (bh - 60)
        if hsh(i, 13) < 0.25:
            py = y - bh - s * 0.72 + (hsh(i, 14) - 0.5) * s * 1.2
            px = x + (hsh(i, 15) - 0.5) * s * 1.2
        k = smooth(prog(dots * 60, i, i + 4))
        r = (5 + 7 * hsh(i, 16)) * k * (0.8 + 0.2 * math.sin(t * 4 + i))
        light(c, px, py, r * 4, RED, 70 * a * k)
        c.drawCircle(px, py, r, fillp((255, 120, 140), 230 * a * k))


def shadow_figure(c, x, y, s, a, t):
    if a <= 0.01:
        return
    c.save()
    p = blur(fillp((0, 0, 0), 235 * a), 6)
    c.drawOval(skia.Rect.MakeXYWH(x - s * 0.5, y - s * 3.0, s, s * 1.15), p)
    sh = skia.Path()
    sh.moveTo(x - s * 0.9, y)
    sh.cubicTo(x - s * 0.8, y - s * 1.6, x - s * 0.4, y - s * 2.0, x, y - s * 2.0)
    sh.cubicTo(x + s * 0.4, y - s * 2.0, x + s * 0.8, y - s * 1.6, x + s * 0.9, y)
    sh.close()
    c.drawPath(sh, p)
    for sx in (-1, 1):
        c.drawCircle(x + sx * s * 0.17, y - s * 2.5, s * 0.06, fillp(RED, 255 * a))
        light(c, x + sx * s * 0.17, y - s * 2.5, s * 0.3, RED, 120 * a)
    c.restore()


def bed(c, x, y, w, pal, a=255):
    c.drawRRect(rrect(x - w / 2, y - 120, w, 140, 30), fillp(mix(pal["dim"], (0, 0, 0), 0.25), a))
    c.drawRRect(rrect(x - w / 2 - 20, y - 330, 50, 360, 20), fillp(mix(pal["dim"], (0, 0, 0), 0.4), a))
    c.drawRRect(rrect(x - w / 2 + 40, y - 200, 220, 90, 40), fillp((235, 238, 250), a))


def sleeping_sam(c, x, y, s, t, pal):
    """Sam asleep under a blanket. (x, y) = head centre."""
    br = 1 + 0.03 * math.sin(t * 1.6)
    c.drawCircle(x, y, s, shaded(radial((x - s * 0.3, y - s * 0.4), s * 1.6, [mix(SAM, (255, 255, 255), 0.3), SAM, mix(SAM, SAM_DK, 0.3)], [0, 0.5, 1])))
    for sx in (-1, 1):
        ex = x + sx * s * 0.36
        a0 = skia.Path()
        a0.moveTo(ex - s * 0.14, y)
        a0.quadTo(ex, y + s * 0.1, ex + s * 0.14, y)
        c.drawPath(a0, stroke(INK, s * 0.05))
    c.drawCircle(x, y + s * 0.42, s * 0.06, fillp(INK))
    bl = skia.Path()
    bl.moveTo(x + s * 0.7, y + s * 0.9)
    bl.cubicTo(x + s * 1.2, y - s * 0.3 * br, x + s * 4.6, y - s * 0.5 * br, x + s * 5.2, y + s * 0.9)
    bl.close()
    c.drawPath(bl, shaded(linear((x, y - s), (x, y + s), [mix(pal["acc"], (40, 60, 140), 0.55), (36, 50, 120)])))
    c.drawPath(bl, stroke(mix(pal["acc"], (255, 255, 255), 0.2), 3, 120))


class Motes:
    """Slow floating dust in the room light."""

    def __init__(self, n=50, seed=3):
        r = np.random.default_rng(seed)
        self.p = r.random((n, 2)) * [W, H]
        self.v = (r.random((n, 2)) - 0.5) * [16, 12] + [0, -5]
        self.s = r.random(n) * 2.5 + 1
        self.ph = r.random(n) * 6.28

    def draw(self, c, t, rgb, a=1.0):
        for i in range(len(self.s)):
            x = (self.p[i, 0] + self.v[i, 0] * t) % (W + 40) - 20
            y = (self.p[i, 1] + self.v[i, 1] * t) % (H + 40) - 20
            tw = 0.5 + 0.5 * math.sin(t * 1.4 + self.ph[i])
            c.drawCircle(x, y, self.s[i], fillp(rgb, 90 * tw * a))


def handle(c, t, t0, a=1.0, y=1560):
    if t < t0:
        return
    k = smooth(prog(t, t0, t0 + 0.5)) * a
    s = "@BrighterMinds"
    label(c, s, W / 2 - width(s, "mono_bold", 34) / 2, y, 34, "mono_bold", PAPER, 230 * k)
