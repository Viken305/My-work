"""Style frames for Ep. 02 (stop-motion cut paper).  python3 frames.py  ->  out/frame_*.png + out/board.png"""
import math, os, sys

import numpy as np
import skia

import paper as P
from paper import *  # noqa: F401,F403
from puppets import *  # noqa: F401,F403
import puppets as Q

OUT = os.path.join(P.HERE, "out")


def backdrop(c, color, seed=0):
    piece(c, P.rect(-20, -20, W + 40, H + 40), color, 0, rim=False, shadow=False, seed=seed)


def finish(c):
    warm_light(c)
    vignette(c)


def series_tag(c, y=118):
    tape(c, 300, y - 40, 480, 64, -1.5, seed=4)
    hand(c, "THE PHYSICS OF EVERYDAY THINGS · 02", W / 2, y + 4, 34, INK, -1.5, "center", "neat")


# ---------------------------------------------------------------- 1: the hook / title
def f_hook(c, t=0.0):
    backdrop(c, SKY)
    with Blur(c, 3.0):
        cloud(c, 230, 520, 0.9, "c1")
        cloud(c, 860, 400, 0.7, "c2")
        sun(c, 170, 800, 90, t=t)
        hill(c, 980, 120, GREEN1, 11, 0.6)
    with Blur(c, 1.4):
        hill(c, 1060, 90, GREEN2, 12, 0.7, 2.4)
        house(c, 40, 1200, 220, 200, CORAL, (120, 60, 60), "h1")
        house(c, 300, 1200, 180, 250, SAND, BLUE_D, "h2", windows=1)
        house(c, 520, 1200, 240, 180, (120, 170, 210), RED_D, "h3")
        house(c, 800, 1200, 200, 230, (246, 200, 120), GREEN3, "h4", windows=1)
    lamp = lamppost(c, 900, 1330, 560)
    pigeon(c, lamp[0] - 30, lamp[1] - 2, 1.25, look=-14)
    curb(c, 1330)
    road_side(c, 1370)
    # speed streaks behind the rider
    for i, (yy, L) in enumerate(((1080, 260), (1160, 340), (1250, 200), (1310, 300))):
        piece(c, P.wobble(P.resample(P.rrect(-20, yy, L, 14, 7), 10), 0.8, i), WHITE, 0.5, seed=200 + i, alpha=0.9)
    bike_side(c, 250, 1520, 1.15, wheel_ang=0.7, crank=0.9, rider=kid_rider(), key="b1")
    snail(c, 840, 1530, 0.55, "sn")
    with Blur(c, 5.0):
        grass_front(c, 1760, 77)
    # title
    series_tag(c)
    pal = [WHITE, YELLOW, WHITE, (255, 236, 200)]
    letters(c, "WHY DON'T", W / 2, 300, font("title", 104), pal, seed=1, rot_amp=4)
    letters(c, "BIKES", W / 2, 450, font("title", 150), [RED, (240, 80, 60), RED], seed=2, rot_amp=5, fg=WHITE)
    letters(c, "FALL OVER?", W / 2, 610, font("title", 104), pal, seed=3, rot_amp=4)
    finish(c)


# ---------------------------------------------------------------- 2: the gyroscope myth
def f_myth(c, t=0.0):
    backdrop(c, KRAFT)
    # cutting-mat grid printed on the kraft board
    for i in range(0, W, 90):
        c.drawLine(i, 0, i, H, skia.Paint(AntiAlias=True, StrokeWidth=1.5, Color=col(KRAFT2, 0.45)))
    for j in range(0, H, 90):
        c.drawLine(0, j, W, j, skia.Paint(AntiAlias=True, StrokeWidth=1.5, Color=col(KRAFT2, 0.45)))
    series_tag(c)
    cx, cy = W / 2, 900
    # motion arcs (cut strips) around the spinning wheel
    for k, (r0, a0, span) in enumerate(((330, -40, 70), (350, 140, 70), (300, 60, 40), (310, 230, 45))):
        a = np.radians(np.linspace(a0, a0 + span, 24))
        outer = np.stack([cx + (r0 + 14) * np.cos(a), cy + (r0 + 14) * np.sin(a)], 1)
        inner = np.stack([cx + r0 * np.cos(a[::-1]), cy + r0 * np.sin(a[::-1])], 1)
        piece(c, np.vstack([outer, inner]), WHITE, 0.6, seed=300 + k)
    Q.wheel(c, cx, cy, 0.3, r=260, key="big", z=0.9, spokes=10)
    # a mouse hanging on to the tyre for dear life
    c.save()
    c.translate(cx + 180, cy - 195)
    c.rotate(42)
    c.scale(1.7, 1.7)
    piece(c, P.ellipse(0, -20, 34, 22, 30), GREY, 0.5, seed=31, smooth=True)
    piece(c, circle(28, -34, 13, 18), GREY, 0.35, seed=32)
    piece(c, circle(20, -48, 11, 18), PINK, 0.3, seed=33)
    sp = skia.Path()
    for k in range(30):
        a = k / 30 * 3 * math.pi
        r = 6 * (1 - k / 32)
        (sp.moveTo if k == 0 else sp.lineTo)(36 + r * math.cos(a), -36 + r * math.sin(a))
    c.drawPath(sp, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2, Color=col(INK)))
    P.string(c, (-34, -14), (-90, 10), PINK, sag=10, w=3)
    c.restore()
    # the claim, on a card, crossed out in marker
    chip(c, "GYROSCOPE?", W / 2, 470, font("title", 96), INK, WHITE, -3, 0.9, seed=5)
    marker(c, [(250, 500), (520, 455), (840, 430)], RED, 13, seed=1)
    marker(c, [(260, 432), (560, 470), (830, 500)], RED, 13, seed=2)
    tape(c, 610, 1220, 360, 70, 4, seed=9)
    hand(c, "too weak to matter!", 790, 1270, 52, RED_D, 4, "center")
    marker(c, [(780, 1210), (700, 1150), (640, 1110)], RED_D, 6, seed=3)
    caption_strip(c, "Most people say it's the spinning wheels. Nope.".split(), 6, 1560, 60, seed=7)
    finish(c)


# ---------------------------------------------------------------- 3: trail, on graph paper with pins and string
def f_trail(c, t=0.0):
    backdrop(c, CREAM)
    for i in range(0, W + 1, 40):
        w = 2.2 if i % 200 == 0 else 1.0
        c.drawLine(i, 0, i, H, skia.Paint(AntiAlias=True, StrokeWidth=w, Color=col((120, 170, 210), 0.45)))
    for j in range(0, H + 1, 40):
        w = 2.2 if j % 200 == 0 else 1.0
        c.drawLine(0, j, W, j, skia.Paint(AntiAlias=True, StrokeWidth=w, Color=col((120, 170, 210), 0.45)))
    series_tag(c)
    s = 2.4
    gx, gy = -480, 1340  # rear contact (off-screen left): we're close on the front end
    bike_side(c, gx, gy, s, 0.2, 2.2, key="b3")
    piece(c, P.rect(-40, gy, W + 80, 26), KRAFT2, 0.6, seed=40)  # the "ground" strip
    hub = np.array([gx + Q.BIKE["front"][0] * s, gy - R * s])
    top = np.array([gx + Q.BIKE["ht_top"][0] * s, gy + (Q.BIKE["ht_top"][1] - R) * s])
    axg = Q.steer_axis_ground()
    ax_ground = np.array([gx + axg[0] * s, gy])
    contact = np.array([hub[0], gy])
    d = ax_ground - top
    top2 = top - d * 0.35
    string(c, top2, ax_ground, RED, sag=0, w=4)
    pushpin(c, *top2, RED)
    pushpin(c, *ax_ground, RED)
    string(c, hub, contact, BLUE, sag=0, w=4)
    pushpin(c, *hub, BLUE)
    pushpin(c, *contact, BLUE)
    # paper ruler measuring the trail
    rx0, rx1 = contact[0] - 40, ax_ground[0] + 40
    c.save()
    piece(c, P.rect(rx0 - 60, gy + 40, (rx1 - rx0) + 120, 70), YELLOW, 0.5, seed=41)
    for k in range(int((rx1 - rx0 + 120) / 12)):
        x = rx0 - 60 + 6 + k * 12
        L = 26 if k % 5 == 0 else 14
        c.drawLine(x, gy + 40, x, gy + 40 + L, skia.Paint(AntiAlias=True, StrokeWidth=2, Color=col(INK)))
    c.restore()
    marker(c, [(contact[0], gy + 130), (ax_ground[0], gy + 130)], INK, 6, seed=4)
    marker(c, [(contact[0], gy + 116), (contact[0], gy + 144)], INK, 6, seed=5)
    marker(c, [(ax_ground[0], gy + 116), (ax_ground[0], gy + 144)], INK, 6, seed=6)
    tape(c, 600, gy + 50, 420, 80, -2, seed=12)
    hand(c, "TRAIL ≈ 6 cm", 810, gy + 108, 64, INK, -2, "center")
    marker(c, [(600, gy + 96), (540, gy + 120), (ax_ground[0] + 10, gy + 130)], INK, 5, seed=8)
    tape(c, 450, 500, 500, 80, 3, seed=13)
    hand(c, "steering axis", 700, 556, 62, RED_D, 3, "center")
    marker(c, [(470, 590), (380, 640), (300, 676)], RED_D, 6, seed=7)
    tape(c, 640, 980, 380, 70, -3, seed=15)
    hand(c, "contact patch", 830, 1030, 50, BLUE_D, -3, "center")
    marker(c, [(650, 1040), (520, 1200), (contact[0] + 20, gy - 20)], BLUE_D, 5, seed=9)
    ant(c, 150, gy, 1.3, "ant3")
    caption_strip(c, "The tyre touches the road BEHIND where the steering points.".split(), 5, 1740, 52, seed=8)
    finish(c)


# ---------------------------------------------------------------- 4: steer into the fall (rear view)
def f_steer(c, t=0.0):
    backdrop(c, SKY)
    hz = 940
    with Blur(c, 2.6):
        cloud(c, 820, 360, 0.6, "c4")
        hill(c, hz, 70, GREEN1, 21, 0.6, 1.2)
        hill(c, hz + 40, 40, GREEN2, 22, 0.6, 2.8)
    # road receding to the horizon
    road = np.array([[W / 2 - 40, hz + 30], [W / 2 + 40, hz + 30], [W + 420, H + 40], [-420, H + 40]])
    piece(c, road, ROAD, 0.4, seed=60)
    for k in range(6):
        f0, f1 = (k / 6) ** 1.8, ((k + 0.5) / 6) ** 1.8
        y0, y1 = hz + 30 + (H - hz) * f0, hz + 30 + (H - hz) * f1
        w0, w1 = 3 + 16 * f0, 3 + 16 * f1
        piece(c, np.array([[W / 2 - w0, y0], [W / 2 + w0, y0], [W / 2 + w1, y1], [W / 2 - w1, y1]]), (240, 236, 222), 0.1,
              seed=61 + k)
    with Blur(c, 1.2):
        snail(c, W / 2 + 120, hz + 90, 0.35, "sn4")
    series_tag(c)
    gx, gy, s4, ln = W / 2 + 30, 1520, 1.5, -14
    bike_rear(c, gx, gy, s4, lean=ln, steer=-14, key="r4")
    # centre of mass: a plumb bob on a string, landing left of the tyre -> it's falling
    a = math.radians(ln)
    lx, ly = 0, -2 * R - 110
    com = np.array([gx + s4 * (lx * math.cos(a) - ly * math.sin(a)), gy + s4 * (lx * math.sin(a) + ly * math.cos(a))])
    string(c, com, (com[0], gy + 20), INK, 0, 3)
    piece(c, np.array([[com[0] - 16, gy + 10], [com[0] + 16, gy + 10], [com[0], gy + 50]]), (212, 172, 72), 0.4, seed=62)
    pushpin(c, *com, YELLOW, 16)
    tape(c, 40, com[1] - 150, 300, 64, -4, seed=14)
    hand(c, "your weight", 190, com[1] - 106, 48, INK, -4, "center")
    marker(c, [(200, com[1] - 80), (com[0] - 40, com[1] - 20)], INK, 5, seed=10)
    # big curved arrow: steer the wheel under the fall
    piece(c, P.arrow_shape((820, 1545), (250, 1520), bend=-60, w=42, head=86), RED, 1.2, seed=63)
    chip(c, "STEER INTO THE FALL", W / 2, 470, font("title", 76), WHITE, RED, 2, 0.9, seed=6)
    caption_strip(c, "Start tipping left? The front wheel turns left, right back under you.".split(), 6, 1790, 46, seed=9)
    finish(c)


# ---------------------------------------------------------------- 5: the riderless bike
def f_ghost(c, t=0.0):
    backdrop(c, (250, 214, 170))
    with Blur(c, 2.6):
        sun(c, 210, 520, 120)
        hill(c, 1000, 110, (232, 160, 110), 31, 0.6)
    with Blur(c, 1.2):
        hill(c, 1090, 80, (200, 120, 96), 32, 0.7, 2.2)
        house(c, 640, 1240, 230, 240, (150, 110, 170), (80, 50, 90), "h51")
        house(c, 890, 1240, 200, 180, (240, 190, 110), RED_D, "h52", windows=1)
    curb(c, 1330)
    road_side(c, 1370)
    series_tag(c)
    # the kid has hopped off and is watching from the kerb, ice cream forgotten
    kid_sitting(c, 90, 1330, 1.0, "sit5")
    for i, (yy, L) in enumerate(((1250, 300), (1330, 200), (1420, 260))):
        piece(c, P.wobble(P.resample(P.rrect(330, yy, L, 14, 7), 10), 0.8, i), WHITE, 0.5, seed=210 + i, alpha=0.9)
    bike_side(c, 470, 1560, 1.15, wheel_ang=1.4, crank=2.0, key="b5")
    # a pigeon has claimed the empty saddle
    sx = 470 + Q.BIKE["saddle"][0] * 1.15
    sy = 1560 + (Q.BIKE["saddle"][1] - R) * 1.15 - 12
    pigeon(c, sx, sy, 0.75, "pg5", look=8)
    chip(c, "NO RIDER.", W / 2 + 60, 420, font("title", 110), INK, WHITE, -4, 1.0, seed=7)
    chip(c, "STILL UPRIGHT.", W / 2 - 20, 580, font("title", 92), WHITE, BLUE, 3, 0.9, seed=8)
    caption_strip(c, "Give an empty bike a push and it balances itself.".split(), 7, 1760, 56, seed=10)
    finish(c)


FRAMES = [("hook", f_hook), ("myth", f_myth), ("trail", f_trail), ("steer", f_steer), ("ghost", f_ghost)]


def render_frame(name, fn, t=0.0):
    P.CLOCK.t = t
    s = new_surface()
    c = s.getCanvas()
    c.clear(skia.ColorWHITE)
    fn(c, t)
    path = os.path.join(OUT, f"frame_{name}.png")
    save_png(s, path)
    return path


def board(paths):
    from PIL import Image, ImageDraw, ImageFont
    k = 0.38
    tw, th = int(W * k), int(H * k)
    gap = 40
    bw = gap + len(paths) * (tw + gap)
    img = Image.new("RGB", (bw, th + 2 * gap + 70), (34, 30, 36))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(os.path.join(P.FONTS, "BowlbyOne-Regular.ttf"), 30)
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = gap + i * (tw + gap)
        img.paste(im, (x, gap))
        d.text((x, gap + th + 18), f"{i + 1}  {os.path.basename(p)[6:-4].upper()}", font=f, fill=(246, 238, 220))
    out = os.path.join(OUT, "board.png")
    img.save(out)
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    paths = [render_frame(n, f) for n, f in FRAMES if not only or n in only]
    if not only:
        print(board(paths))
    print("\n".join(paths))
