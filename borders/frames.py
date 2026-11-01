"""Style frames for "Why Borders Are Shaped the Way They Are" (Paper Atlas).

  python3 frames.py        -> out/frame_1.png ... frame_6.png + out/style_frames.png (board)
"""
import os

from PIL import Image

from atlas import *  # noqa: F401,F403
from atlas import _poly

NEUTRAL = (238, 232, 216)
OUT = os.path.join(HERE, "out")


def fit_headline(c, s, num, section):
    c.drawPaint(fillp(PAPER))
    text(c, f"No. {num}  ·  {section.upper()}", 70, 250, 30, "monob", RED, tracking=0.08)
    size = 78
    while font("serif", size).measureText(s) > 950:
        size -= 2
    text(c, s, 66, 345, size, "serif", INK)


def at(view, lon, lat):
    return view(lon, lat)


# ------------------------------------------------------------------ 1 · hook
def f1(c):
    fit_headline(c, "Borders aren't random", 1, "the hook")
    card(c)
    v = geo.View(MAP, -20, 82, -36, 60, "world")
    draw_countries(c, v)
    for a, b in [("FRA", "ESP"), ("EGY", "SDN"), ("EGY", "LBY"), ("AFG", "TJK"), ("AFG", "PAK"), ("AFG", "CHN")]:
        draw_border(c, v, a, b, 5)
    x, y = v(0.5, 42.7)
    ring(c, x, y, 70, 34)
    hand(c, "wiggly", x - 40, y - 60, 60, RED, rot=-6)
    x, y = v(28, 22)
    ring(c, x, y, 120, 70, rot=4)
    hand(c, "ruler straight", x + 10, y + 120, 60, RED, rot=-4)
    x, y = v(73, 37)
    ring(c, x, y, 66, 40, rot=-14)
    hand(c, "just strange", x - 60, y - 64, 60, RED, rot=-8)
    card_frame(c)
    caption(c, "Some wiggle, some run ruler straight, and some are just strange.", ("wiggle", "straight", "strange"))


# ------------------------------------------------------------------ 2 · nature: the Rio Grande
def f2(c):
    fit_headline(c, "Rivers draw borders", 2, "nature")
    card(c)
    v = geo.View(MAP, -108.5, -96, 23.5, 34.5)
    draw_countries(c, v, {"USA": (234, 214, 168), "MEX": (196, 214, 178)})
    draw_border(c, v, "USA", "MEX", 16)
    draw_rivers(c, v, ["Rio Grande"], 6)
    halo_text(c, "UNITED STATES", *v(-100.5, 33.2), 34)
    halo_text(c, "MEXICO", *v(-104.5, 27.0), 34)
    x, y = v(-100.6, 29.7)
    hand(c, "Rio Grande", x + 160, y + 10, 62, BLUE, rot=-18)
    x, y = v(-107.6, 31.6)
    hand(c, "no river here:", x + 60, y + 110, 44, RED, rot=-4)
    hand(c, "a straight line", x + 60, y + 154, 44, RED, rot=-4)
    for lon, lat, name in [(-106.49, 31.76, "El Paso"), (-97.5, 25.9, "Brownsville")]:
        px, py = v(lon, lat)
        c.drawCircle(px, py, 9, fillp(INK))
        halo_text(c, name.upper(), px + (14 if lon < -100 else -14), py - 18, 22, "mono", INK, "left" if lon < -100 else "right")
    # legend
    lx, ly = MAP[0] + 40, MAP[3] - 160
    c.drawRect(skia.Rect.MakeLTRB(lx - 16, ly - 40, lx + 410, ly + 64), fillp(CARD))
    c.drawRect(skia.Rect.MakeLTRB(lx - 16, ly - 40, lx + 410, ly + 64), strokep(INK, 2))
    c.drawLine(lx, ly - 10, lx + 60, ly - 10, strokep(RED, 14))
    c.drawLine(lx, ly - 10, lx + 60, ly - 10, strokep(BLUE, 5))
    text(c, "river = border", lx + 80, ly, 30, "reg", INK)
    c.drawLine(lx, ly + 36, lx + 60, ly + 36, strokep(RED, 9))
    text(c, "land border", lx + 80, ly + 46, 30, "reg", INK)
    card_frame(c, 200, v)
    caption(c, "Rivers, like the Rio Grande, between the US and Mexico.", ("rio", "grande"))


# ------------------------------------------------------------------ 3 · straight lines: Africa
def f3(c):
    fit_headline(c, "Lines drawn on paper", 3, "straight lines")
    card(c)
    v = geo.View(MAP, -19, 53, -36, 38)
    draw_countries(c, v)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(*MAP))
    for a, b in geo.straight_segments():
        c.drawPath(v.line([a, b]), strokep(RED, 7))
    c.restore()
    # a ruler lying along the Egypt-Sudan line (22° N)
    x0, y = v(24.5, 22.0)
    x1, _ = v(37, 22.0)
    c.save()
    c.translate(0, -48)
    c.drawRect(skia.Rect.MakeLTRB(x0 - 20, y - 22, x1 + 20, y + 22), fillp((246, 232, 190), 235))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 20, y - 22, x1 + 20, y + 22), strokep(INK, 2))
    for i in range(0, int(x1 - x0) + 40, 12):
        c.drawLine(x0 - 20 + i, y + 22, x0 - 20 + i, y + 22 - (14 if i % 60 == 0 else 7), strokep(INK, 2))
    c.restore()
    hand(c, "22° N", (x0 + x1) / 2, y - 90, 50, RED, rot=-3)
    x, y = v(-12, -20)
    lx, ly = MAP[0] + 40, MAP[3] - 100
    c.drawRect(skia.Rect.MakeLTRB(lx - 16, ly - 42, lx + 400, ly + 22), fillp(CARD))
    c.drawRect(skia.Rect.MakeLTRB(lx - 16, ly - 42, lx + 400, ly + 22), strokep(INK, 2))
    c.drawLine(lx, ly - 10, lx + 60, ly - 10, strokep(RED, 7))
    text(c, "straight borders", lx + 80, ly, 30, "reg", INK)
    card_frame(c, 1000, v)
    caption(c, "European empires split up Africa with long straight lines.", ("straight", "lines."))


# ------------------------------------------------------------------ 4 · deals: the Caprivi Strip
def f4(c):
    fit_headline(c, "The Caprivi Strip", 4, "deals")
    card(c)
    v = geo.View(MAP, 11, 31, -30, -11.5)
    draw_countries(c, v, {"NAM": (232, 178, 160)}, default=NEUTRAL)
    draw_rivers(c, v, ["Zambezi"], 6)
    for name, lon, lat in [("NAMIBIA", 17, -22.5), ("ANGOLA", 17, -14), ("ZAMBIA", 26.5, -14), ("BOTSWANA", 24, -22.5),
                           ("ZIMBABWE", 29.2, -20.6), ("SOUTH AFRICA", 24, -28.3)]:
        halo_text(c, name, *v(lon, lat), 28, "mono", INK if name == "NAMIBIA" else GREY)
    x, y = v(22.5, -17.9)
    hand(c, "Caprivi Strip", x - 30, y - 70, 58, RED, rot=-5)
    arrow(c, [(x - 110, y - 52), (x - 40, y - 18)], RED, 4, 18)
    fx, fy = v(25.86, -17.92)                         # Victoria Falls
    arrow(c, [v(24.9, -17.6), (fx + 60, fy - 120), v(30.8, -16.2)], RED, 5, 24, dash=[18, 12])
    for k in (-1, 1):
        c.drawLine(fx - 24, fy - 24 * k, fx + 24, fy + 24 * k, strokep(RED, 9))
    halo_text(c, "VICTORIA FALLS", fx + 10, fy + 62, 24, "monob", BLUE, "center")
    hand(c, "to the sea", v(29.3, -15.4)[0], v(29.3, -15.4)[1] - 40, 46, RED, rot=-10)
    hand(c, "Zambezi", *v(29.6, -17.9), 48, BLUE, rot=30)
    card_frame(c, 200, v)
    caption(c, "Germany's bid to reach the Zambezi River.", ("zambezi",))


# ------------------------------------------------------------------ 5 · deals: the Wakhan Corridor
def f5(c):
    fit_headline(c, "The Wakhan Corridor", 4, "deals")
    card(c)
    v = geo.View(MAP, 64, 78.5, 31, 40.5)
    draw_countries(c, v, {"AFG": (232, 178, 160)}, default=NEUTRAL)
    draw_border(c, v, "AFG", "TJK", 7, (120, 100, 160))
    draw_border(c, v, "AFG", "PAK", 7, (120, 100, 160))
    draw_rivers(c, v, ["Panj", "Amu  Darya"], 5)
    halo_text(c, "AFGHANISTAN", *v(66.5, 34.3), 30, "monob", INK)
    for name, sub, lon, lat in [("RUSSIAN EMPIRE", "today: Tajikistan", 69.5, 39.3), ("BRITISH INDIA", "today: Pakistan", 72.2, 33.0)]:
        x, y = v(lon, lat)
        halo_text(c, name, x, y, 34, "monob", (120, 100, 160))
        halo_text(c, sub, x, y + 38, 22, "mono", GREY)
    halo_text(c, "CHINA", *v(77.2, 38.2), 26, "mono", GREY)
    x, y = v(73.2, 37.05)
    ring(c, x, y, 150, 40, rot=-6)
    hand(c, "Wakhan Corridor", x - 20, y + 92, 58, RED, rot=-4)
    w0, w1 = v(73.0, 37.35), v(73.0, 36.85)
    halo_text(c, "~13 km at its narrowest", x + 40, y + 150, 24, "mono", INK)
    card_frame(c, 200, v)
    caption(c, "A buffer, so two empires would never touch.", ("buffer,",))


# ------------------------------------------------------------------ 6 · Baarle: the front-door rule
def flag(c, x, y, kind, w=90, h=60):
    if kind == "B":
        for i, rgb in enumerate([(30, 30, 30), (250, 210, 40), (220, 40, 50)]):
            c.drawRect(skia.Rect.MakeXYWH(x + i * w / 3, y, w / 3, h), fillp(rgb))
    else:
        for i, rgb in enumerate([(174, 28, 40), (255, 255, 255), (33, 70, 139)]):
            c.drawRect(skia.Rect.MakeXYWH(x, y + i * h / 3, w, h / 3), fillp(rgb))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), strokep(INK, 2))


def house(c, x, y, w, h, wall, roof, door_x=None):
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fillp(wall))
    c.drawPath(_poly([(x - 16, y), (x + w / 2, y - h * 0.5), (x + w + 16, y)]), fillp(roof))
    c.drawPath(_poly([(x - 16, y), (x + w / 2, y - h * 0.5), (x + w + 16, y)]), strokep(INK, 3))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), strokep(INK, 3))
    for wx in (x + w * 0.12, x + w * 0.62):
        if door_x is not None and abs(wx + w * 0.13 - door_x) < w * 0.2:
            continue
        c.drawRect(skia.Rect.MakeXYWH(wx, y + h * 0.18, w * 0.26, h * 0.26), fillp((200, 220, 230)))
        c.drawRect(skia.Rect.MakeXYWH(wx, y + h * 0.18, w * 0.26, h * 0.26), strokep(INK, 3))
    if door_x is not None:
        c.drawRect(skia.Rect.MakeXYWH(door_x - 40, y + h - 170, 80, 170), fillp((60, 110, 90)))
        c.drawRect(skia.Rect.MakeXYWH(door_x - 40, y + h - 170, 80, 170), strokep(INK, 3))
        c.drawCircle(door_x + 22, y + h - 84, 6, fillp((230, 200, 90)))


def cross(c, x, y, s=26):
    c.drawLine(x - s, y, x + s, y, strokep((255, 255, 255), 8))
    c.drawLine(x, y - s * 0.6, x, y + s * 0.6, strokep((255, 255, 255), 8))


def f6(c):
    fit_headline(c, "A border through the house", 5, "baarle")
    x0, y0, x1, y1 = MAP
    c.drawRect(skia.Rect.MakeLTRB(x0 + 8, y0 + 10, x1 + 8, y1 + 10), fillp((0, 0, 0), 22))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), fillp((222, 234, 238)))
    gy = 1110
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    c.drawRect(skia.Rect.MakeLTRB(x0, gy, x1, y1), fillp((196, 190, 180)))
    for i in range(0, 960, 64):                         # paving
        c.drawLine(x0 + i, gy, x0 + i - 120, y1, strokep((176, 170, 160), 2))
    c.restore()
    house(c, x0 + 40, 760, 250, 350, (214, 170, 140), (150, 70, 60))
    house(c, x0 + 340, 700, 360, 410, (232, 214, 186), (110, 90, 80), door_x=x0 + 470)
    house(c, x0 + 750, 780, 180, 330, (190, 160, 140), (130, 80, 70))
    bx = x0 + 560                                       # the border, painted across the pavement and up the wall
    c.drawLine(bx, 700, bx, gy, strokep(RED, 7, dash=[22, 14]))
    c.drawPath(_poly([(bx, gy), (bx - 60, y1)], False), strokep((255, 255, 255), 10, dash=[30, 18]))
    for k, yy in enumerate((1170, 1250)):
        cross(c, bx - 30 - 30 * k, yy)
        text(c, "B", bx - 90 - 30 * k, yy + 12, 32, "monob", (255, 255, 255), "center")
        text(c, "NL", bx + 30 - 30 * k, yy + 12, 32, "monob", (255, 255, 255), "center")
    flag(c, x0 + 60, y0 + 40, "B")
    text(c, "BELGIUM", x0 + 170, y0 + 82, 30, "monob", INK)
    flag(c, x1 - 150, y0 + 40, "NL")
    text(c, "NETHERLANDS", x1 - 170, y0 + 82, 30, "monob", INK, "right")
    c.drawRect(skia.Rect.MakeLTRB(x0 + 30, 1180, x0 + 380, 1310), fillp(CARD, 235))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 30, 1180, x0 + 380, 1310), strokep(INK, 2))
    hand(c, "front door in Belgium", x0 + 205, 1236, 46, RED)
    hand(c, "= a Belgian house", x0 + 205, 1288, 42, RED)
    arrow(c, [(x0 + 300, 1176), (x0 + 360, 1110), (x0 + 412, 1050)], RED, 5, 22)
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), strokep(INK, 3))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 10, y0 + 10, x1 - 10, y1 - 10), strokep(INK, 1, 120))
    caption(c, "Your house belongs to whichever country your front door is in.", ("front", "door"))


FRAMES = [f1, f2, f3, f4, f5, f6]


def render(fn):
    s = skia.Surface(W, H)
    fn(s.getCanvas())
    img = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    return Image.fromarray(grain(img)).convert("RGB")


if __name__ == "__main__":
    import sys
    os.makedirs(OUT, exist_ok=True)
    pick = [int(a) for a in sys.argv[1:]] or range(1, 7)
    imgs = []
    for i in pick:
        im = render(FRAMES[i - 1])
        im.save(os.path.join(OUT, f"frame_{i}.png"))
        imgs.append(im)
    if len(imgs) == 6:
        board = Image.new("RGB", (3 * 540 + 4 * 30, 2 * 960 + 3 * 30), PAPER)
        for k, im in enumerate(imgs):
            board.paste(im.resize((540, 960), Image.LANCZOS), (30 + (k % 3) * 570, 30 + (k // 3) * 990))
        board.save(os.path.join(OUT, "style_frames.png"))
    print("ok", list(pick))
