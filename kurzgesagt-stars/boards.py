"""Storyboard key frames for the stars video (rendered with the premium post pipeline)."""
import math

from cosmos import *  # noqa: F401,F403
from cosmos import _disk

_SF = Starfield(2)
_SF2 = Starfield(9, (500, 180, 50))
_BK = Bokeh(5)


def space(c, t, cam=None, clouds=("cloud",), teal=True, a=1.0, sf=_SF):
    cam = cam or Cam()
    c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.85, [DEEP, VOID])))
    sf.draw(c, t, cam, a)
    if teal:
        cam.push(c, 0.35)
        draw_texture(c, tex_teal(), 420, -220, 1.3, t * 0.5, 130 * a)
        cam.pop(c)
    for i, k in enumerate(clouds):
        cam.push(c, 0.5 + i * 0.15)
        fn = {"cloud": tex_cloud, "dust": tex_dust, "teal": tex_teal}[k]
        draw_texture(c, fn(), -260 + i * 380, 80 - i * 60, 1.2, -t * 0.7 + i * 40, 200 * a, skia.BlendMode.kPlus if k != "dust" else skia.BlendMode.kSrcOver)
        cam.pop(c)
    return cam


def label(c, s, x, y, rgb=WHITE, size=26, a=255, sub=None):
    text(c, s, x, y, size, rgb, a, 800, spacing=size * 0.22)
    if sub:
        text(c, sub, x, y + size * 1.35, size * 0.62, mix(rgb, WHITE, 0.4), a * 0.85, 800, spacing=size * 0.12)


def tag(c, s, x, y, rgb, size=22):
    w = font(size, 800).measureText(s) + size * 0.1 * len(s) + size * 1.4
    c.drawRRect(rrect(x - w / 2, y - size * 0.95, w, size * 1.55, size * 0.78), fill((10, 10, 30), 200))
    c.drawRRect(rrect(x - w / 2, y - size * 0.95, w, size * 1.55, size * 0.78), stroke(rgb, 2, 200))
    text(c, s, x, y + size * 0.15, size, rgb, 255, 800, spacing=size * 0.1)


def arrow(c, x0, y0, x1, y1, rgb, w=10, a=255, head=26):
    c.drawLine(x0, y0, x1, y1, stroke(rgb, w, a))
    ang = math.atan2(y1 - y0, x1 - x0)
    c.drawPath(poly([(x1 + math.cos(ang) * head * 0.6, y1 + math.sin(ang) * head * 0.6),
                     (x1 + math.cos(ang + 2.4) * head, y1 + math.sin(ang + 2.4) * head),
                     (x1 + math.cos(ang - 2.4) * head, y1 + math.sin(ang - 2.4) * head)]), fill(rgb, a))


def human(c, x, y, h, glow_rgb=None, a=255):
    """Simple side-on human silhouette (head, torso, arm), feet at y."""
    sil = (24, 26, 52)
    c.save()
    c.translate(x, y)
    c.scale(h / 600, h / 600)
    body = skia.Path()
    body.addCircle(0, -520, 62)
    body.addRRect(rrect(-80, -450, 160, 300, 70))
    body.addRRect(rrect(-62, -180, 54, 180, 26))
    body.addRRect(rrect(8, -180, 54, 180, 26))
    body.addRRect(rrect(-108, -430, 46, 230, 23))
    body.addRRect(rrect(62, -430, 46, 230, 23))
    c.drawPath(body, blur(fill(TEAL, 0.35 * a), 30))
    c.drawPath(body, shaded(linear((0, -580), (0, 0), [(40, 44, 90), sil])))
    c.drawPath(body, stroke(mix(sil, TEAL, 0.7), 6, a))
    if glow_rgb:
        for k in range(26):
            ang = k * 2.4
            px, py = math.cos(ang) * 50 * ((k * 7) % 10) / 10, -300 + math.sin(ang) * 130 * ((k * 3) % 10) / 10
            c.drawCircle(px, py, 5, add(glow_rgb, 220))
    c.restore()


def galaxy(c, x, y, r, t, a=255, tilt=0.42):
    """Spiral galaxy: dense additive star particles on 3 log-spiral arms + bulge."""
    rng = np.random.default_rng(4)
    for k in range(700):
        arm = k % 3
        u = rng.random() ** 0.7
        ang = arm * 2.094 + u * 4.6 + rng.normal(0, 0.22) + t * 0.04
        rr = r * u + rng.normal(0, r * 0.03)
        px, py = x + math.cos(ang) * rr, y + math.sin(ang) * rr * tilt
        sz = 1.2 + 2.4 * rng.random() * (1 - u * 0.5)
        c.drawCircle(px, py, sz, add(mix(SOLAR, BLUE_STAR, u), (90 + 120 * (1 - u)) * a / 255))
    light(c, x, y, r * 0.45, SOLAR, 230 * a / 255)
    light(c, x, y, r * 1.1, (200, 170, 255), 70 * a / 255)


def teaspoon(c, x, y, s):
    c.drawOval(skia.Rect.MakeXYWH(x - s * 0.45, y - s * 0.28, s * 0.9, s * 0.56), fill((200, 205, 220)))
    c.drawOval(skia.Rect.MakeXYWH(x - s * 0.36, y - s * 0.2, s * 0.72, s * 0.4), fill((150, 160, 190)))
    c.drawRRect(rrect(x + s * 0.4, y - s * 0.06, s * 1.4, s * 0.12, s * 0.06), fill((200, 205, 220)))
    light(c, x, y, s * 0.4, BLUE_STAR, 220)
    c.drawOval(skia.Rect.MakeXYWH(x - s * 0.3, y - s * 0.14, s * 0.6, s * 0.28), fill((220, 235, 255)))


# ================================================================ PART 1
def p1a(c, t):
    space(c, t, clouds=("cloud",), a=0.6)
    human(c, 760, 1000, 760, glow_rgb=SOLAR)
    for i, (sym, x, y) in enumerate((("Fe", 1150, 360), ("Ca", 1330, 560), ("O", 1150, 760))):
        element_chip(c, x, y, 150, sym)
        c.drawLine(x - 90, y, 800, 480 + i * 140, stroke(ELEMENTS[sym][1], 3, 140))
    orbi(c, 1640, 420, 95, t, "wide", (-0.8, 0.1), ears=0.6, rim=SOLAR)


def p1b(c, t):
    space(c, t, clouds=("cloud", "teal"))
    shockwave(c, 1300, 330, 520, t, 0.35)
    for i in range(14):
        ang = i / 14 * 6.28
        x, y = 1300 + math.cos(ang) * (220 + (i % 3) * 70), 330 + math.sin(ang) * (150 + (i % 3) * 50)
        atom_dot(c, x, y, 9, [AMBER, TEAL, MAGENTA, SOLAR][i % 4], t)
    c.drawRect(skia.Rect.MakeXYWH(0, 900, W, 200), shaded(linear((0, 880), (0, H), [(10, 10, 30), (4, 4, 14)])))
    human(c, 420, 960, 260)
    orbi(c, 640, 830, 70, t, "wide", (0.8, -0.8), ears=0.8, rim=AMBER)
    label(c, "LONG BEFORE THE SUN WAS BORN", 960, 1040, AMBER, 30)


def p1c(c, t):
    space(c, t, clouds=("cloud",), a=0.8)
    label(c, "YOU ARE MADE OF", 960, 300, WHITE, 46)
    text(c, "DEAD STARS", 960, 440, 140, SOLAR, 255, 800, spacing=14)
    stages = [("NEBULA", lambda x, y: draw_texture(c, tex_cloud(), x, y, 0.14, 0, 255, skia.BlendMode.kPlus)),
              ("PROTOSTAR", lambda x, y: protostar(c, x, y, 16, t, 0.8)),
              ("STAR", lambda x, y: star(c, x, y, 34, t)),
              ("RED GIANT", lambda x, y: star(c, x, y, 52, t, RED_GIANT, 0.6)),
              ("SUPERNOVA", lambda x, y: shockwave(c, x, y, 140, t, 0.28))]
    for i, (name, fn) in enumerate(stages):
        x = 300 + i * 330
        fn(x, 700)
        text(c, name, x, 820, 22, WHITE, 220, 800, spacing=4)
        if i < 4:
            arrow(c, x + 90, 700, x + 230, 700, (120, 120, 170), 4, 200, 16)
    orbi(c, 1700, 280, 80, t, "happy", (-0.5, 0.3), ears=0.9, rim=SOLAR)


# ================================================================ PART 2
def p2a(c, t):
    cam = Cam(0, 0, 1.0)
    c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.85, [DEEP, VOID])))
    _SF.draw(c, t, cam)
    for i, (k, x, y, sc, a) in enumerate((("teal", 500, 260, 1.5, 160), ("cloud", 900, 560, 1.7, 230), ("cloud", 1500, 380, 1.2, 170))):
        draw_texture(c, (tex_teal if k == "teal" else tex_cloud)(11 + i if k == "cloud" else 31), x, y, sc, i * 30, a, skia.BlendMode.kPlus)
    for i in range(40):
        x, y = 200 + (i * 173) % 1500, 200 + (i * 97) % 700
        c.drawCircle(x, y, 4, add(BLUE_STAR, 150))
    orbi(c, 1520, 820, 46, t, "wide", (-0.6, -0.4), ears=0.4, rim=MAGENTA)
    label(c, "MOSTLY HYDROGEN · LIGHT-YEARS ACROSS", 960, 1030, (220, 200, 255), 28)


def p2b(c, t):
    space(c, t, clouds=("cloud", "dust"))
    c.drawCircle(-300, 540, 900, stroke(AMBER, 26, 120))
    c.drawCircle(-300, 540, 900, blur(stroke(AMBER, 60, 90), 30))
    for (x, y, r) in ((980, 420, 60), (1250, 640, 44), (1500, 360, 36)):
        light(c, x, y, r * 3, MAGENTA, 160)
        for k in range(8):
            ang = k / 8 * 6.28
            arrow(c, x + math.cos(ang) * r * 2.4, y + math.sin(ang) * r * 2.4, x + math.cos(ang) * r * 1.3, y + math.sin(ang) * r * 1.3, (230, 210, 255), 3, 190, 12)
    tag(c, "SHOCKWAVE", 560, 220, AMBER)
    tag(c, "GRAVITY", 1250, 860, (230, 210, 255))


def p2c(c, t):
    space(c, t, Cam(0, 0, 1.0), clouds=("cloud",), a=0.7)
    protostar(c, 860, 520, 75, t, 0.92)
    orbi(c, 1560, 640, 100, t, "squint", (-0.7, -0.1), ears=0.1, rim=MAGENTA)
    tag(c, "SPINNING · DENSER · HOTTER", 900, 900, SOLAR)


def p2d(c, t):
    space(c, t, clouds=("cloud",), a=0.5)
    c.drawCircle(560, 540, 360, shaded(radial((560, 540), 360, [(200, 90, 50), (150, 50, 40), (70, 20, 30)], [0, 0.6, 1])))
    c.drawCircle(560, 540, 360, stroke(SOLAR, 4, 180))
    for k, (x, y) in enumerate(((470, 450), (650, 460), (480, 640), (660, 630))):
        atom_dot(c, x, y, 26, BLUE_STAR, t)
        text(c, "H", x, y + 10, 26, INK, 255, 800)
        arrow(c, x + (80 if x < 560 else -80) * 0.9, y, x + (40 if x < 560 else -40), y, WHITE, 4, 200, 14)
    light(c, 560, 545, 110, SOLAR, 170)
    atom_dot(c, 560, 545, 34, (255, 220, 120), t)
    text(c, "He", 560, 556, 30, INK, 255, 800)
    label(c, "HYDROGEN → HELIUM", 560, 980, SOLAR, 30, sub="CORE ≈ 10,000,000 °C")
    star(c, 1400, 500, 160, t, SOLAR, 1.2)
    flare(c, 1400, 500, 120, SOLAR, 160)
    label(c, "A STAR IS BORN", 1400, 860, WHITE, 40)
    orbi(c, 1750, 820, 70, t, "happy", (-0.6, -0.4), ears=1.0, rim=SOLAR)


# ================================================================ PART 3
def p3a(c, t):
    space(c, t, clouds=("cloud",), a=0.45)
    star(c, 960, 540, 230, t, SOLAR, 1.0)
    for k in range(12):
        ang = k / 12 * 6.28 + 0.13
        arrow(c, 960 + math.cos(ang) * 470, 540 + math.sin(ang) * 470, 960 + math.cos(ang) * 300, 540 + math.sin(ang) * 300, VIOLET2, 9, 230, 26)
        arrow(c, 960 + math.cos(ang + 0.26) * 250, 540 + math.sin(ang + 0.26) * 250, 960 + math.cos(ang + 0.26) * 400, 540 + math.sin(ang + 0.26) * 400, AMBER, 9, 230, 26)
    tag(c, "GRAVITY  →  IN", 300, 160, VIOLET2, 28)
    tag(c, "FUSION  →  OUT", 1620, 160, AMBER, 28)


def p3b(c, t):
    space(c, t, clouds=("cloud",), a=0.4)
    star(c, 960, 380, 170, t, SOLAR)
    x0, x1, y = 260, 1660, 820
    c.drawRRect(rrect(x0, y - 10, x1 - x0, 20, 10), fill((40, 40, 80)))
    c.drawRRect(rrect(x0, y - 10, (x1 - x0) * 0.46, 20, 10), shaded(linear((x0, 0), (x1, 0), [AMBER, SOLAR])))
    for v, lab in ((0, "0"), (5, "5"), (10, "10 BILLION YEARS")):
        x = x0 + (x1 - x0) * v / 10
        c.drawLine(x, y + 20, x, y + 40, stroke(WHITE, 3, 180))
        text(c, lab, x, y + 76, 22, WHITE, 200, 800, spacing=3)
    xm = x0 + (x1 - x0) * 0.46
    c.drawCircle(xm, y, 18, fill(WHITE))
    tag(c, "TODAY · 4.6 BILLION YEARS · ~HALFWAY", xm, y - 70, SOLAR, 24)
    orbi(c, 1540, 340, 80, t, "neutral", (-0.8, 0), ears=0.3, rim=SOLAR)


def p3c(c, t):
    space(c, t, clouds=("teal",), a=0.5)
    star(c, 330, 560, 40, t, RED_GIANT, 0.45)
    star(c, 830, 560, 95, t, SOLAR, 0.4)
    star(c, 1480, 540, 230, t, BLUE_STAR, 0.3)
    for x, name, life in ((330, "RED DWARF", "TRILLIONS OF YEARS"), (860, "SUN-LIKE", "~10 BILLION YEARS"), (1530, "GIANT", "A FEW MILLION YEARS")):
        label(c, name, x, 930, WHITE, 28, sub=life)
    orbi(c, 1150, 300, 70, t, "worried", (0.8, 0.2), ears=-0.6, rim=BLUE_STAR)


# ================================================================ PART 4
def p4a(c, t):
    space(c, t, clouds=(), teal=False, a=0.8)
    star(c, -80, 540, 820, t, RED_GIANT, 0.7, granule_a=50)
    for x, r, name, rgb in ((560, 12, "MERCURY", (160, 150, 150)), (700, 18, "VENUS", (230, 190, 120)), (900, 20, "EARTH?", (80, 150, 255))):
        light(c, x, 540, r * 3, rgb, 120)
        c.drawCircle(x, 540, r, fill(rgb))
        text(c, name, x, 600, 20, WHITE, 220, 800, spacing=3)
    orbi(c, 1500, 520, 100, t, "worried", (-0.9, 0), ears=-0.8, rim=RED_GIANT)
    label(c, "RED GIANT · IN ~5 BILLION YEARS", 1400, 960, RED_GIANT, 30)


def p4b(c, t):
    space(c, t, clouds=(), teal=False)
    draw_texture(c, tex_ring(), 900, 540, 0.95, t * 2, 255, skia.BlendMode.kPlus)
    white_dwarf(c, 900, 540, 10, t)
    orbi(c, 1600, 760, 90, t, "wide", (-0.8, -0.4), ears=0.7, rim=TEAL)
    label(c, "PLANETARY NEBULA", 900, 1010, (150, 230, 240), 30)


def p4c(c, t):
    space(c, t, clouds=(), teal=False, a=0.8)
    white_dwarf(c, 760, 520, 120, t)
    earth(c, 1260, 520, 120, t)
    text(c, "≈", 1010, 545, 90, WHITE, 230, 800)
    label(c, "WHITE DWARF", 760, 760, BLUE_STAR, 30, sub="ABOUT THE SIZE OF EARTH")
    label(c, "EARTH", 1260, 760, (120, 180, 255), 30)
    label(c, "COOLING FOR BILLIONS OF YEARS", 960, 980, WHITE, 24)


# ================================================================ PART 5
def p5a(c, t):
    space(c, t, clouds=("cloud",), a=0.4)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(0, 0, 820, H))
    star(c, 820, 540, 400, t, BLUE_STAR, 0.25)
    c.restore()
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(820, 0, 1100, H))
    onion(c, 820, 540, 400, ["H", "He", "C", "O", "Si", "Fe"])
    c.restore()
    for i, sym in enumerate(["H", "He", "C", "O", "Si", "Fe"]):
        rr = 400 * (1 - (i + 0.5) / 6)
        ang = math.radians(-50 + i * 18)
        px, py = 820 + rr * math.cos(ang), 540 + rr * math.sin(ang)
        lx, ly = 1400, 220 + i * 120
        c.drawLine(px, py, lx - 20, ly - 10, stroke(WHITE, 2, 160))
        c.drawCircle(px, py, 6, fill(WHITE))
        name, rgb = ELEMENTS[sym]
        text(c, f"{sym} · {name}", lx, ly, 30, lighten(rgb, 0.3), 255, 800, "left", spacing=3)
    label(c, "HEAVIER AND HEAVIER · ALL THE WAY TO IRON", 960, 1030, WHITE, 26)


def p5b(c, t):
    space(c, t, clouds=("dust",), a=0.6)
    _, rgb = ELEMENTS["Fe"]
    c.drawCircle(960, 520, 150, shaded(radial((920, 480), 200, [lighten(rgb, 0.3), rgb, darken(rgb, 0.4)])))
    for k in range(16):
        ang = k / 16 * 6.28
        arrow(c, 960 + math.cos(ang) * 440, 520 + math.sin(ang) * 440, 960 + math.cos(ang) * 200, 520 + math.sin(ang) * 200, WHITE, 6, 220, 20)
    text(c, "Fe", 960, 550, 90, WHITE, 255, 800)
    tag(c, "LESS THAN A SECOND", 960, 960, (255, 140, 120), 30)
    orbi(c, 1640, 300, 80, t, "wide", (-0.9, 0.5), ears=-0.3, rim=(255, 140, 120))


def p5c(c, t):
    space(c, t, clouds=("cloud",), a=0.6)
    shockwave(c, 700, 470, 700, t, 0.12)
    galaxy(c, 1580, 260, 220, t)
    orbi(c, 1500, 760, 90, t, "squint", (-1, -0.2), (-900, 0), ears=-0.5, rim=AMBER, thrust=1.0)
    c.drawRect(skia.Rect.MakeXYWH(0, 930, W, 150), shaded(linear((0, 930), (0, H), [(VOID, 0), (VOID, 220)])))
    label(c, "SUPERNOVA", 960, 990, AMBER, 46, sub="CAN BRIEFLY OUTSHINE A WHOLE GALAXY")


def p5d(c, t):
    space(c, t, clouds=(), teal=False)
    c.drawLine(960, 80, 960, 1000, stroke(WHITE, 2, 60))
    neutron_star(c, 480, 450, 22, t, beam=16)
    teaspoon(c, 420, 820, 90)
    label(c, "NEUTRON STAR", 480, 960, BLUE_STAR, 30, sub="A TEASPOON ≈ A BILLION TONNES")
    black_hole(c, 1440, 470, 110, t)
    label(c, "BLACK HOLE", 1440, 960, AMBER, 30, sub="IF THE CORE IS HEAVY ENOUGH")


# ================================================================ PART 6
def p6a(c, t):
    space(c, t, clouds=("cloud", "teal"))
    draw_texture(c, tex_ring(43), 520, 540, 0.8, 0, 200, skia.BlendMode.kPlus)
    for i, sym in enumerate(["C", "O", "Si", "Fe", "Ca"]):
        x, y = 980 + i * 190, 340 + (i % 2) * 260
        c.drawLine(560, 540, x - 70, y, stroke(ELEMENTS[sym][1], 3, 120))
        element_chip(c, x, y, 130, sym)
    label(c, "SCATTERED INTO SPACE", 960, 1010, WHITE, 28)


def p6b(c, t):
    space(c, t, clouds=("teal",), a=0.6)
    for k in range(2):
        ang = t * 1.5 + k * math.pi
        x, y = 700 + math.cos(ang) * 120, 520 + math.sin(ang) * 50
        neutron_star(c, x, y, 16, t, beam=14)
    p = skia.Path()
    for k in range(80):
        ang = k * 0.25
        rr = 360 - k * 3
        (p.moveTo if k == 0 else p.lineTo)(700 + math.cos(ang) * rr, 520 + math.sin(ang) * rr * 0.42)
    c.drawPath(p, stroke(VIOLET2, 3, 140))
    light(c, 700, 520, 260, (255, 200, 120), 160)
    element_chip(c, 1380, 470, 240, "Au", glow_a=200)
    label(c, "NEUTRON STARS COLLIDE", 700, 980, BLUE_STAR, 28, sub="FORGING HEAVY ELEMENTS")
    label(c, "MUCH OF EARTH'S GOLD", 1380, 760, (255, 210, 90), 28, sub="LIKELY MADE THIS WAY")


def p6c(c, t):
    space(c, t, clouds=("cloud",), a=0.6)
    _disk(c, 760, 540, 50, 520, 0.25, t, 255, "back")
    star(c, 760, 540, 60, t)
    _disk(c, 760, 540, 50, 520, 0.25, t, 255, "front")
    for k, (r, rgb) in enumerate(((150, (180, 160, 150)), (230, (230, 190, 120)), (320, (80, 150, 255)), (420, (230, 120, 80)))):
        ang = 0.6 + k * 1.3
        px, py = 760 + math.cos(ang) * r * 1.6, 540 + math.sin(ang) * r * 0.4
        c.drawCircle(px, py, 10 + k * 2, fill(rgb))
    earth(c, 1450, 520, 170, t)
    label(c, "OUR SOLAR SYSTEM", 1450, 820, (120, 180, 255), 30, sub="ABOUT 4.6 BILLION YEARS AGO")


def p6d(c, t):
    c.drawPaint(shaded(linear((0, 0), (0, H), [VOID, (30, 24, 70)])))
    _SF2.draw(c, t, Cam(), 1.0)
    c.save()
    c.rotate(-18, W / 2, H / 2)
    draw_texture(c, tex_cloud(13), 960, 420, 1.5, 0, 150, skia.BlendMode.kPlus)
    c.restore()
    galaxy(c, 1450, 260, 260, t, 150)
    hill = skia.Path()
    hill.moveTo(-20, H)
    hill.cubicTo(400, 800, 1200, 760, W + 20, 880)
    hill.lineTo(W + 20, H)
    hill.close()
    c.drawPath(hill, fill((8, 8, 20)))
    human(c, 760, 880, 260, glow_rgb=SOLAR)
    orbi(c, 980, 760, 60, t, "happy", (-0.3, -0.8), ears=0.6, rim=TEAL)
    text(c, "YOU'RE MADE OF THEM", 960, 1020, 40, WHITE, 240, 800, spacing=10)


PANELS = {
    1: ("HOOK", "0:00–0:25", [
        (p1a, "S1", "\"The iron in your blood. The calcium in your bones. The oxygen you just breathed in...\"", "A glowing human silhouette; element tiles Fe, Ca and O pop out of it one by one; ORBI drifts in, amazed."),
        (p1b, "S2", "\"...forged inside stars that lived and died long before the Sun was born.\"", "Pull back to a night sky: a distant star explodes; element sparks fly; ORBI and a person look up."),
        (p1c, "S3", "\"...follow the life of a star. From its first spark, to its spectacular end.\"", "Title \"You are made of DEAD STARS\"; the life cycle builds left to right; ORBI ready to go."),
    ]),
    2: ("BIRTH OF A STAR", "0:25–1:07", [
        (p2a, "B1", "\"...enormous clouds of gas and dust, mostly hydrogen, light-years across.\"", "Slow parallax drift through layered nebulae; tiny ORBI for scale; hydrogen glints."),
        (p2b, "B2", "\"...the shockwave of a distant explosion... gravity takes over.\"", "An amber shock front sweeps through the cloud; knots of gas brighten as arrows pull inward."),
        (p2c, "B3", "\"The clump pulls in more and more gas, spinning faster, getting denser, and hotter.\"", "Protostar with a spinning accretion disk and jets; ORBI squints into the glare."),
        (p2d, "B4", "\"...ten million degrees... fusing into helium... A star is born.\"", "Core cut-away: hydrogen smashes into helium with a flash; then IGNITION with lens flare; ORBI cheers."),
    ]),
    3: ("THE LIFE OF A STAR", "1:07–1:45", [
        (p3a, "L1", "\"...a tug of war. Gravity tries to crush it inward. Fusion pushes outward.\"", "Violet arrows push in, amber arrows push out, pulsing against each other around the star."),
        (p3b, "L2", "\"Our Sun... four and a half billion years... roughly halfway through.\"", "Timeline bar fills to 4.6 of ~10 billion years; marker labelled TODAY."),
        (p3c, "L3", "\"Small red dwarf stars... trillions of years... Giant stars... a few million.\"", "Three stars grow in by size with their lifetimes; ORBI looks worried next to the giant."),
    ]),
    4: ("DEATH OF A SUN-LIKE STAR", "1:45–2:18", [
        (p4a, "D1", "\"...our Sun will swell into a red giant... swallowing Mercury and Venus, and maybe Earth.\"", "The Sun swells into a red giant that fills the left of frame; Mercury and Venus vanish; ORBI backs away."),
        (p4b, "D2", "\"...a glowing shell called a planetary nebula.\"", "The outer layers drift off into a slowly turning, glowing ring; ORBI gazes."),
        (p4c, "D3", "\"...a white dwarf, about the size of Earth, slowly cooling...\"", "Side-by-side size comparison with Earth; the white dwarf dims slowly."),
    ]),
    5: ("DEATH OF A GIANT", "2:18–3:05", [
        (p5a, "G1", "\"...carbon, oxygen, silicon, all the way to iron.\"", "The giant splits open to reveal its onion-like core layers, labelled from H to Fe."),
        (p5b, "G2", "\"...fusing iron costs energy... in less than a second, the core collapses.\"", "Silence; arrows slam inward on the iron core; ORBI's eye goes wide."),
        (p5c, "G3", "\"...a supernova, an explosion that can briefly outshine an entire galaxy.\"", "White-out flash, lens flare, shockwave; ORBI is blown backwards with motion blur; a galaxy for comparison."),
        (p5d, "G4", "\"A neutron star... a teaspoon... a billion tonnes. Or... a black hole.\"", "Split screen: a spinning pulsar with a glowing teaspoon; a black hole with its lensed accretion disk."),
    ]),
    6: ("STAR STUFF", "3:05–3:43", [
        (p6a, "X1", "\"Every exploding star scatters the elements it made out into space.\"", "Element tiles stream out of a supernova remnant along glowing trails."),
        (p6b, "X2", "\"When neutron stars collide... Much of the gold on Earth was likely made this way.\"", "Two neutron stars spiral together into a kilonova; a gold Au tile shines."),
        (p6c, "X3", "\"...new stars, and new planets... about four and a half billion years ago.\"", "A new disk forms the Sun and planets; zoom to Earth."),
        (p6d, "X4", "\"...you're not just looking at the stars. You're made of them.\"", "A person and ORBI on a hill under the Milky Way; specks of starlight glow inside the person; end card."),
    ]),
}
