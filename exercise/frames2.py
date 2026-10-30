"""Second style frame for each direction (stills only).

  python3 frames2.py   -> out/frame_A2.png, out/frame_B2.png, out/frame_C2.png

  A2  RUSH HOUR · the muscle works: a factory district where trucks deliver sugar and oxygen and chimneys puff CO2
  B2  BEAT DROP · the lungs are two giant speakers; the notes spell how much air you move
  C2  FOGGED GLASS · inside a muscle fibre: myosin "rowers" pull the actin rope, powered by ATP coins
"""
import os

from PIL import Image

import beat
import city
import micro
import premium
from kit import *  # noqa: F401,F403

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


# ---------------------------------------------------------------- A2
def frame_a2(c, t):
    c.drawRect(skia.Rect.MakeWH(W, H), grad_v(0, H, city.NAVY0, city.NAVY1))
    cam = (420, 1300, 1.3)
    P = lambda x, y, z=0: city.P(x, y, z, cam)  # noqa: E731
    for gx, gy, hgt in city.BUILD:                      # dim city around the district
        if gx + gy < 2:
            city.draw_building(c, gx + 3, gy + 3, hgt * 0.7, cam, t)
    for sgn, rgb in ((-1, city.RED), (1, city.BLUE)):   # supply road
        a, b = P(-420, sgn * 22), P(420, sgn * 22)
        c.drawLine(*a, *b, stroke(mix(rgb, (0, 0, 0), 0.65), 34))
        c.drawLine(*a, *b, stroke(rgb, 3, 120, plus=True))
    # the muscle factory: a long striated building
    for i in range(9):
        x0 = -200 + i * 44
        top = [P(x0, -120, 150), P(x0 + 40, -120, 160), P(x0 + 40, -40, 160), P(x0, -40, 150)]
        side = [P(x0, -40, 0), P(x0 + 40, -40, 0), P(x0 + 40, -40, 160), P(x0, -40, 150)]
        c.drawPath(path_of(side, True), fillp((150, 30, 50) if i % 2 else (190, 46, 66)))
        c.drawPath(path_of(top, True), fillp((230, 90, 100) if i % 2 else (250, 120, 126)))
    for i, cx_ in enumerate((-150, -40, 70)):           # chimneys with CO2 puffs
        bx, by = P(cx_, -100, 160)
        c.drawRect(skia.Rect.MakeXYWH(bx - 16, by - 150, 32, 150), fillp((70, 76, 100)))
        for k in range(4):
            u = (t * 0.4 + k / 4 + i * 0.13) % 1
            r = 26 + 40 * u
            c.drawCircle(bx + 30 * u, by - 170 - 200 * u, r, fillp((170, 176, 196), 170 * (1 - u)))
        label(c, "CO2", bx + 40, by - 330, 30, "overpass_black", (200, 206, 226), 220, "center")
    sx, sy = P(-180, -40, 30)
    label(c, "MUSCLE WORKS", sx + 220, sy + 40, 34, "overpass_black", (255, 220, 220), 255)
    for i in range(7):                                   # delivery trucks: glucose cubes and oxygen bubbles
        u = (i / 7 + t * 0.08) % 1
        x, y = P(lerp(420, -40, u), 22)
        c.drawRRect(rrect(x - 34, y - 40, 68, 40, 8), fillp((40, 44, 70)))
        if i % 2:
            for k in range(3):
                c.drawRect(skia.Rect.MakeXYWH(x - 28 + k * 19, y - 64, 16, 16), fillp((250, 250, 250)))
        else:
            for k in range(3):
                c.drawCircle(x - 18 + k * 18, y - 56, 9, fillp((120, 220, 255)))
    label(c, "GLUCOSE + OXYGEN IN", *P(300, 60), 26, "mono_bold", (220, 230, 255), 230, "center")
    # sign and boards
    c.save()
    c.translate(0, city.GY)
    for px in (70, 1010):
        c.drawRect(skia.Rect.MakeXYWH(px - 14, 420, 28, H), fillp(city.STEEL))
    c.drawRect(skia.Rect.MakeXYWH(40, 410, 1000, 26), fillp(city.STEEL))
    c.drawRRect(rrect(60, 450, 960, 250, 14), fillp((10, 8, 6)))
    pitch = 9.2
    x0 = 540 - 16 * 6 * pitch / 2 + pitch * 0.5
    for li, (line, red) in enumerate((("YOUR BODY BURNS", ()), ("UP TO 10X ENERGY", (6, 7, 8)))):
        off = (16 - len(line)) / 2 * 6 * pitch
        for i, ch in enumerate(line):
            led_text(c, ch, x0 + off + i * 6 * pitch, 500 + li * 10 * pitch, pitch, lambda _: 1.0, city.RED if i in red else city.AMBER)
    c.restore()
    city.flap(c, 100, 610, "10", t, {}, "ENERGY USE", city.AMBER)
    label(c, "X REST", 260, 690, 28, "overpass", city.AMBER, 255)
    city.flap(c, 600, 610, "x10", t, {}, "OXYGEN USED", (120, 220, 255))
    label(c, "X REST", 830, 690, 28, "overpass", (120, 220, 255), 255)


# ---------------------------------------------------------------- B2
def lung(c, cx, cy, sx, sc, t, rgb):
    p = skia.Path()
    p.moveTo(cx, cy - 260 * sc)
    p.cubicTo(cx + sx * 220 * sc, cy - 300 * sc, cx + sx * 260 * sc, cy + 160 * sc, cx + sx * 190 * sc, cy + 250 * sc)
    p.cubicTo(cx + sx * 110 * sc, cy + 300 * sc, cx + sx * 20 * sc, cy + 220 * sc, cx, cy + 120 * sc)
    p.close()
    for k in range(5):                                   # the lung is a speaker: rings of the cone
        c.save()
        c.translate(cx + sx * 110 * sc, cy)
        f = 1 - k * 0.17
        c.scale(f, f)
        c.translate(-(cx + sx * 110 * sc), -cy)
        c.drawPath(p, stroke(rgb if k % 2 == 0 else (255, 255, 255), 6 if k else 9, 255 if k == 0 else 170))
        c.restore()
    light(c, cx + sx * 110 * sc, cy, 300 * sc, rgb, 120)
    c.drawCircle(cx + sx * 110 * sc, cy, 26 * sc, fillp((255, 255, 255)))


def frame_b2(c, t):
    beat.stage(c, t)
    sc = 1.0 + 0.1 * beat.beat(t)
    c.drawLine(540, 400, 540, 560, stroke(beat.CYN, 14))   # windpipe
    lung(c, 530, 700, -1, sc, t, beat.CYN)
    lung(c, 550, 700, 1, sc, t, beat.MAG)
    for i in range(12):                                     # VU meters at the sides
        for side, x in ((-1, 70), (1, 980)):
            on = i < 10
            col_ = beat.LIME if i < 6 else (beat.GOLD if i < 9 else beat.MAG)
            c.drawRRect(rrect(x, 920 - i * 44, 30, 34, 6), fillp(col_ if on else (40, 30, 60)))
    for n_text, lane, d in (("UP", 0, 0.95), ("TO", 2, 0.75), ("LITRES", 1, 0.45), ("OF AIR", 3, 0.2)):
        x, y, s = beat.note_pos(d, lane)
        beat.gem(c, x, y, s, n_text, beat.LANES[lane])
    x, y, s = beat.note_pos(0.62, None)
    beat.gem(c, x, y, s, "100", beat.GOLD, 255, True)
    label(c, "AIR IN", 72, 230, 34, "bungee", beat.CYN, 255)
    outlined(c, "100", 72, 340, 120, "bungee", (255, 255, 255), 255, "left", glow_rgb=beat.CYN)
    label(c, "L/MIN", 340, 340, 44, "bungee", beat.CYN, 255)
    label(c, "BREATHS", 1008, 230, 30, "bungee", beat.MAG, 255, "right")
    outlined(c, "40", 1008, 330, 90, "bungee", beat.MAG, 255, "right", glow_rgb=beat.MAG)
    outlined(c, "EVERY MINUTE", 540, 1000, 84, "bungee", (255, 255, 255), 255, glow_rgb=beat.MAG)


# ---------------------------------------------------------------- C2
def rower(c, x, y, s, t, ph, up):
    """A myosin head as a tiny rower: bean body, arms on the actin rope."""
    stroke_ = math.sin(t * 6 + ph)
    c.save()
    c.translate(x, y)
    if not up:
        c.scale(1, -1)
    c.rotate(-20 + 25 * stroke_)
    c.drawLine(0, 0, 0, -s * 1.4, stroke((255, 190, 120), s * 0.28))
    c.drawOval(skia.Rect.MakeXYWH(-s * 0.6, -s * 2.3, s * 1.2, s * 1.0), fillp((255, 214, 120)))
    c.drawCircle(-s * 0.18, -s * 1.85, s * 0.09, fillp((60, 30, 20)))
    c.drawCircle(s * 0.18, -s * 1.85, s * 0.09, fillp((60, 30, 20)))
    c.restore()


def fiber_scene(c, t):
    c.drawRect(skia.Rect.MakeWH(W, H), grad_v(0, H, (170, 60, 80), (110, 30, 50)))
    for row, y in enumerate((760, 1240)):                # thick filaments (myosin) with rowers above and below
        c.drawRRect(rrect(-40, y - 26, W + 80, 52, 26), fillp((200, 120, 90)))
        c.drawRRect(rrect(-40, y - 26, W + 80, 20, 10), fillp((240, 170, 130), 160))
        for i in range(12):
            x = 40 + i * 90 + (25 if row else 0)
            rower(c, x, y - 26, 34, t, i * 0.7, True)
            rower(c, x, y + 26, 34, t, i * 0.7 + 1, False)
    for y in (560, 1000, 1440):                          # thin filaments (actin): twisted bead ropes
        off = (t * 60) % 44
        for i in range(30):
            x = -40 + i * 44 - off
            for k in (0, 1):
                yy = y + 14 * math.sin(i * 0.9 + k * math.pi)
                c.drawCircle(x + k * 22, yy, 17, fillp((255, 120, 140) if k else (230, 90, 120)))
    for i in range(7):                                    # ATP coins floating in
        x = 120 + i * 140 + 30 * math.sin(t + i)
        y = 640 + (i % 3) * 300 + 20 * math.cos(t * 1.3 + i)
        light(c, x, y, 90, (255, 220, 90), 120)
        hexp = path_of([(x + 44 * math.cos(a), y + 44 * math.sin(a)) for a in [k * math.pi / 3 for k in range(6)]], True)
        c.drawPath(hexp, fillp((255, 214, 80)))
        c.drawPath(hexp, stroke((255, 250, 200), 4))
        label(c, "ATP", x, y + 10, 26, "overpass_black", (120, 70, 10), 255, "center")


def frame_c2(c, t):
    s = skia.Surface(W, H)
    sc_ = s.getCanvas()
    fiber_scene(sc_, t)
    sharp = s.makeImageSnapshot()
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(26, 26))
    c.drawImage(sharp, 0, 0, skia.SamplingOptions(), p)
    if micro.FOGTEX is None:
        micro.FOGTEX = micro._fog_texture()
    fa = skia.Paint()
    fa.setAlphaf(0.8)
    c.drawImage(micro.FOGTEX, 0, 0, skia.SamplingOptions(), fa)
    m = skia.Path()
    for li, line in enumerate(("ATP POWERS", "EVERY PULL")):
        size = min(170, 170 * 960 / width(line, "marker", 170))
        f = font("marker", size)
        x = 540 - width(line, "marker", size) / 2
        y = 1000 + li * 190
        for ch in line:
            if ch != " ":
                gp = f.getPath(f.textToGlyphs(ch)[0])
                if gp is not None:
                    gp.offset(x, y)
                    fat = skia.Path()
                    stroke((255, 255, 255), 16).getFillPath(gp, fat)
                    m = skia.Op(m, skia.Op(gp, fat, skia.PathOp.kUnion_PathOp), skia.PathOp.kUnion_PathOp)
            x += f.measureText(ch)
    for dx, dy, L in ((380, 1055, 180), (700, 1245, 260), (240, 1240, 120)):   # drips
        tr = skia.Path()
        tr.addRRect(rrect(dx - 7, dy, 14, L, 7))
        tr.addCircle(dx, dy + L + 6, 11)
        m = skia.Op(m, tr, skia.PathOp.kUnion_PathOp)
    c.save()
    c.clipPath(m, doAntiAlias=True)
    c.drawImage(sharp, 0, 0)
    c.restore()
    c.drawPath(m, stroke((255, 255, 255), 5, 150))
    label(c, "INSIDE A MUSCLE FIBRE", 540, 360, 34, "mono_bold", (60, 40, 50), 230, "center", tracking=0.12)


def render(fn, name, t=2.0, split=0.0, grain=4.0):
    out = premium.render_premium(fn, t, samples=1, grain=grain, ca=0.6, bloom=0.9, split=split)
    p = os.path.join(OUT, name)
    Image.fromarray(out).save(p)
    print(p)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    render(frame_a2, "frame_A2.png")
    render(frame_b2, "frame_B2.png", t=2.3)
    render(frame_c2, "frame_C2.png")
