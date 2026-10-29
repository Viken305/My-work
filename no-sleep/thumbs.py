"""Creative thumbnails (1080x1920 for Shorts / Reels, 1280x720 for feeds).

  python3 thumbs.py   -> out/thumb_split.png, out/thumb_toothpicks.png, out/thumb_wide.png

  split       Sam's face cracked down the middle: hour 0 (calm, blue) against hour 72 (bloodshot, red, glitching),
              with the shadow figure behind the red half.
  toothpicks  Sam propping both eyelids open with toothpicks, eyes veined, the HUD stuck at HOUR 72.
"""
import os

import numpy as np
from PIL import Image

import premium
from film import *  # noqa: F401,F403

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
T = 2.0


def outlined(c, s, x, y, size, kind, rgb, align="center", ow=0.12, glow_rgb=None, tracking=0.0):
    """Big poster text: glow, drop shadow, thick dark outline, fill."""
    f = font(kind, size)
    w = width(s, kind, size, tracking)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    def run(p, dx=0.0, dy=0.0):
        cx = x0
        for ch in s:
            c.drawString(ch, cx + dx, y + dy, f, p)
            cx += f.measureText(ch) + tracking * size
    if glow_rgb:
        run(paint(glow_rgb, 150, size * 0.12))
    run(paint((0, 0, 0), 200, size * 0.05), 0, size * 0.05)
    op = paint((8, 6, 16), 255)
    op.setStyle(skia.Paint.kStroke_Style)
    op.setStrokeWidth(size * ow)
    op.setStrokeJoin(skia.Paint.kRound_Join)
    run(op)
    run(paint(rgb, 255))


def big_eye(c, cx, cy, hw, hh, f, lid=0.15, look=(0.0, 0.0), wide=0.0, seed=1):
    """Close-up eye. f = fatigue (veins, redness), lid = upper lid drop 0..1, wide = small staring pupil."""
    almond = skia.Path()
    almond.moveTo(cx - hw, cy)
    almond.quadTo(cx, cy - hh * 2, cx + hw, cy)
    almond.quadTo(cx, cy + hh * 2, cx - hw, cy)
    almond.close()
    c.save()
    c.clipPath(almond, doAntiAlias=True)
    c.drawPaint(shaded(radial((cx, cy), hw, [(246, 244, 250), (226, 218, 234), mix((190, 176, 206), (230, 110, 130), f)], [0, 0.6, 1])))
    rng = np.random.default_rng(seed)
    for side in (-1, 1):                                # veins
        for k in range(int(14 * f)):
            x0 = cx + side * hw * rng.uniform(0.7, 0.98)
            y0 = cy + rng.uniform(-0.4, 0.4) * hh * 0.7
            pts = [(x0, y0)]
            ang = math.atan2(cy - y0, cx - x0) + rng.uniform(-0.5, 0.5)
            for j in range(8):
                ang += rng.uniform(-0.5, 0.5)
                st_ = rng.uniform(0.04, 0.07) * hw
                pts.append((pts[-1][0] + math.cos(ang) * st_, pts[-1][1] + math.sin(ang) * st_))
            c.drawPath(path_of(pts), stroke((210, 40, 64), hw * 0.009, 230))
    ir = hh * 0.78
    ix, iy = cx + look[0] * hw * 0.25, cy + look[1] * hh * 0.25
    c.drawCircle(ix, iy, ir + hw * 0.02, fillp((0, 0, 0), 70))
    iris = mix(CYAN, RED, 0.0)
    c.drawCircle(ix, iy, ir, shaded(radial((ix, iy), ir, [(40, 90, 150), iris, (24, 60, 120)], [0.25, 0.7, 1])))
    c.drawCircle(ix, iy, ir - hw * 0.01, stroke((14, 30, 70), hw * 0.028, 210))
    for i in range(56):
        a0 = i / 56 * 2 * math.pi
        r0, r1 = ir * 0.45, ir * (0.86 + 0.12 * hsh(i, seed))
        c.drawLine(ix + math.cos(a0) * r0, iy + math.sin(a0) * r0, ix + math.cos(a0) * r1, iy + math.sin(a0) * r1,
                   stroke((210, 245, 255), hw * 0.004, 80))
    pr = ir * lerp(0.42, 0.2, wide)
    c.drawCircle(ix, iy, pr, fillp((6, 8, 16)))
    c.drawOval(skia.Rect.MakeXYWH(ix - ir * 0.55, iy - ir * 0.62, ir * 0.42, ir * 0.3), fillp((255, 255, 255), 235))
    c.drawCircle(ix + ir * 0.36, iy + ir * 0.3, ir * 0.07, fillp((255, 255, 255), 160))
    drop = hh * 2 * lid
    edge = skia.Path()
    edge.moveTo(cx - hw - 4, cy - hh * 2.2)
    edge.lineTo(cx + hw + 4, cy - hh * 2.2)
    edge.lineTo(cx + hw + 4, cy)
    edge.quadTo(cx, cy - (hh - drop) * 2, cx - hw - 4, cy)
    edge.close()
    ledge = cy - (hh - drop)
    c.drawRect(skia.Rect.MakeLTRB(cx - hw, ledge - 10, cx + hw, ledge + hh * 0.35), grad_v(ledge - 10, ledge + hh * 0.35, (30, 20, 60), (30, 20, 60), 140, 0))
    c.drawPath(edge, fillp(mix(SAM, SAM_DK, 0.15)))
    c.restore()
    line = skia.Path()
    line.moveTo(cx - hw, cy)
    line.quadTo(cx, cy - (hh - drop) * 2, cx + hw, cy)
    c.drawPath(line, stroke(INK, hw * 0.035))
    c.drawPath(almond, stroke((60, 48, 120), hw * 0.025, 220))
    return ledge


def head(c, cx, cy, r):
    c.drawCircle(cx + r * 0.04, cy + r * 0.06, r, blur(fillp((0, 0, 0), 120), r * 0.08))
    c.drawCircle(cx, cy, r, shaded(radial((cx - r * 0.35, cy - r * 0.4), r * 1.6, [mix(SAM, (255, 255, 255), 0.3), SAM, mix(SAM, SAM_DK, 0.35)], [0, 0.5, 1])))
    tuft = skia.Path()
    tuft.moveTo(cx - r * 0.1, cy - r * 0.96)
    tuft.cubicTo(cx - r * 0.05, cy - r * 1.35, cx + r * 0.35, cy - r * 1.3, cx + r * 0.25, cy - r * 1.05)
    c.drawPath(tuft, stroke(mix(SAM, SAM_DK, 0.4), r * 0.08))


def crack_path(x, y0, y1, seed=5):
    rng = np.random.default_rng(seed)
    pts, y = [(x, y0)], y0
    while y < y1:
        y += rng.uniform(40, 90)
        pts.append((x + rng.uniform(-38, 38), min(y, y1)))
    return pts


def split_thumb():
    s = skia.Surface(W, H)
    c = s.getCanvas()
    cx, cy, r = 540, 1010, 470
    crack = crack_path(cx, 0, H)
    left = path_of([(0, 0)] + crack + [(0, H)], True)
    right = path_of([(W, 0)] + crack + [(W, H)], True)
    # left half: hour 0, calm
    c.save()
    c.clipPath(left, doAntiAlias=True)
    c.drawPaint(shaded(linear((0, 0), (0, H), [(16, 24, 64), (34, 46, 110)])))
    light(c, 260, 760, 700, CYAN, 70)
    head(c, cx, cy, r)
    big_eye(c, cx - r * 0.42, cy - r * 0.05, r * 0.36, r * 0.2, 0.0, lid=0.18, look=(0.25, 0.0))
    m = skia.Path()
    m.moveTo(cx - r * 0.34, cy + r * 0.5)
    m.quadTo(cx - r * 0.14, cy + r * 0.64, cx - r * 0.02, cy + r * 0.54)
    c.drawPath(m, stroke(INK, r * 0.04))
    c.restore()
    # right half: hour 72, wrecked
    c.save()
    c.clipPath(right, doAntiAlias=True)
    c.drawPaint(shaded(linear((0, 0), (0, H), [(40, 6, 18), (80, 14, 38)])))
    for i in range(18):                                 # crawling wall lines
        y = 300 + i * 90
        p = skia.Path()
        p.moveTo(500, y)
        for k in range(1, 14):
            p.lineTo(500 + k * 50, y + 22 * math.sin(k * 0.8 + i))
        c.drawPath(p, stroke((130, 30, 64), 4, 160))
    shadow_figure(c, 930, 760, 120, 1.0, T)
    light(c, 820, 900, 700, RED, 80)
    head(c, cx, cy, r)
    c.drawCircle(cx, cy, r, fillp((255, 60, 90), 40))
    c.drawArc(skia.Rect.MakeXYWH(cx + r * 0.02, cy + r * 0.1, r * 0.8, r * 0.42), 15, 150, False, blur(stroke(SAM_DK, r * 0.11, 235), r * 0.03))
    big_eye(c, cx + r * 0.43, cy - r * 0.06, r * 0.42, r * 0.25, 1.0, lid=-0.06, look=(-0.1, 0.05), wide=1.0, seed=3)
    c.drawOval(skia.Rect.MakeXYWH(cx + r * 0.08, cy + r * 0.48, r * 0.16, r * 0.2), fillp(INK))
    c.restore()
    # the crack itself
    cp = path_of(crack)
    c.drawPath(cp, stroke((255, 255, 255), 16, 60))
    c.drawPath(cp, stroke((8, 6, 16), 9))
    c.drawPath(cp, stroke((255, 240, 220), 3, 230))
    # labels on each half
    outlined(c, "HOUR 0", 270, 420, 110, "display", CYAN, glow_rgb=CYAN)
    for dx, rgb in ((-7, CYAN), (7, RED)):
        label(c, "HOUR 72", 800 + dx, 420, 110, "display", rgb, 150, "center")
    outlined(c, "HOUR 72", 800, 420, 110, "display", PAPER, glow_rgb=RED)
    # headline
    c.drawRect(skia.Rect.MakeLTRB(0, 1420, W, H), grad_v(1420, 1700, (6, 4, 12), (6, 4, 12), 0, 235))
    outlined(c, "NO SLEEP", W / 2, 1620, 230, "display", PAPER, glow_rgb=RED)
    outlined(c, "WHAT IT DOES TO YOU", W / 2, 1730, 78, "display", AMBER)
    snap(s, os.path.join(OUT, "thumb_split.png"), split=3)


def toothpick_thumb():
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.drawPaint(shaded(radial((540, 900), 1300, [(96, 24, 44), (40, 8, 18), (12, 2, 6)], [0, 0.5, 1])))
    for i in range(30):                                 # clock ticks around the head
        a = i / 30 * 2 * math.pi
        rr = 720
        c.drawLine(540 + math.cos(a) * rr, 980 + math.sin(a) * rr, 540 + math.cos(a) * (rr - (50 if i % 5 == 0 else 24)),
                   980 + math.sin(a) * (rr - (50 if i % 5 == 0 else 24)), stroke(RED, 8 if i % 5 == 0 else 4, 170))
    cx, cy, r = 540, 1000, 430
    head(c, cx, cy, r)
    for k, sx in enumerate((-1, 1)):
        ex = cx + sx * r * 0.38
        ey = cy - r * 0.05
        ex = cx + sx * r * 0.42
        ledge = big_eye(c, ex, ey, r * 0.38, r * 0.24, 1.0, lid=-0.08, look=(0.0, 0.0), wide=0.85, seed=7 + k)
        c.drawArc(skia.Rect.MakeXYWH(ex - r * 0.34, ey + r * 0.2, r * 0.68, r * 0.34), 20, 140, False, blur(stroke(SAM_DK, r * 0.08, 230), r * 0.02))
        # toothpick propping the lid open, braced outside the iris from the lower lid to the upper lid
        tx0, ty0 = ex + sx * r * 0.26, ey + r * 0.14
        tx1, ty1 = ex + sx * r * 0.21, ey - r * 0.26
        c.drawLine(tx0 + 4, ty0 + 6, tx1 + 4, ty1 + 6, stroke((0, 0, 0), 22, 90))
        c.drawLine(tx0, ty0, tx1, ty1, stroke((222, 184, 120), 18))
        c.drawLine(tx0, ty0, tx1, ty1, stroke((250, 222, 170), 6, 200))
        for (px, py) in ((tx0, ty0), (tx1, ty1)):
            c.drawCircle(px, py, 10, fillp((180, 140, 80)))
    m = skia.Path()
    m.moveTo(cx - r * 0.16, cy + r * 0.6)
    m.quadTo(cx, cy + r * 0.52, cx + r * 0.16, cy + r * 0.6)
    c.drawPath(m, stroke(INK, r * 0.04))
    for i in range(3):                                  # sweat drops
        x, y = cx + r * (0.75 + 0.06 * i), cy - r * (0.55 - 0.25 * i)
        drop = skia.Path()
        drop.moveTo(x, y - 30)
        drop.quadTo(x + 22, y + 6, x, y + 18)
        drop.quadTo(x - 22, y + 6, x, y - 30)
        c.drawPath(drop, fillp((150, 210, 255), 230))
    # HUD stuck at 72
    for dx, rgb in ((-6, CYAN), (6, RED)):
        label(c, "HOUR 72", 72 + dx, 300, 80, "mono_bold", rgb, 150)
    label(c, "HOUR 72", 72, 300, 80, "mono_bold", PAPER, 255)
    c.drawLine(72, 360, 1008, 360, stroke(RED, 6))
    c.drawCircle(1008, 360, 14, fillp(RED))
    light(c, 1008, 360, 70, RED, 160)
    c.drawRect(skia.Rect.MakeLTRB(0, 1440, W, H), grad_v(1440, 1680, (8, 2, 6), (8, 2, 6), 0, 235))
    outlined(c, "72 HOURS", W / 2, 1640, 210, "display", PAPER, glow_rgb=RED)
    outlined(c, "NO SLEEP", W / 2, 1760, 100, "display", RED)
    snap(s, os.path.join(OUT, "thumb_toothpicks.png"), split=2)


def wide_thumb():
    """1280x720: the split face on the left, headline on the right."""
    full = Image.open(os.path.join(OUT, "thumb_split.png")).crop((40, 450, 1040, 1450)).resize((720, 720), Image.LANCZOS)
    s = skia.Surface(1280, 720)
    c = s.getCanvas()
    c.drawPaint(fillp((8, 6, 16)))
    img = skia.Image.fromarray(np.dstack([np.asarray(full), np.full((720, 720), 255, np.uint8)]))
    c.drawImage(img, 0, 0)
    c.drawRect(skia.Rect.MakeLTRB(560, 0, 1280, 720), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(560, 0), (760, 0)], [skia.Color(8, 6, 16, 0), skia.Color(8, 6, 16, 250)])))
    outlined(c, "NO SLEEP", 1010, 300, 150, "display", PAPER, glow_rgb=RED)
    outlined(c, "FOR 72 HOURS", 1010, 400, 74, "display", RED)
    outlined(c, "what happens to your body", 1010, 470, 34, "bold", AMBER, ow=0.15)
    rgb = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
    Image.fromarray(rgb).save(os.path.join(OUT, "thumb_wide.png"))


def snap(s, path, split=0):
    rgb = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
    out = premium.post(rgb, T, bloom=0.6, ca=0.6, grain=5.0, split=split)
    Image.fromarray(out).save(path)
    print(path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    split_thumb()
    toothpick_thumb()
    wide_thumb()
