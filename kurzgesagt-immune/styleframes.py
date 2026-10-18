"""Style frames: one finished-quality frame per chapter.  python3 styleframes.py [1 3 ...] -> out/styleframes/"""
import math, os, sys

from world import *  # noqa: F401,F403

OUT = os.path.join(HERE, "out", "styleframes")


def sf1(c, t):
    """Hook: the army, with Kai front and centre."""
    cam = Cam(0, 0, 1.0)
    body_world(c, t, cam)
    neutrophil(c, 300, 430, 82, t, "determined", (0.5, 0.1), seed=1)
    neutrophil(c, 1640, 470, 78, t + 1, "determined", (-0.5, 0.1), seed=2)
    dendritic(c, 520, 760, 62, t, "determined", (0.4, -0.3))
    b_cell(c, 1420, 770, 76, t, "determined", (-0.4, -0.3))
    t_cell(c, 620, 330, 70, t, "helper", "determined", (0.4, 0.3))
    macrophage(c, 1290, 330, 110, t, "determined", (-0.4, 0.3))
    kai_at(c, 960, 600, 230, t, "determined", (0.0, 0.05))
    near_blur(c, [(-60, 980, 260), (1980, 140, 230)], t, (200, 80, 110))
    text(c, "THERE IS A", 960, 120, 40, WHITE, 255, 800, spacing=12)
    text(c, "WAR INSIDE YOU", 960, 215, 96, (255, 214, 120), 255, 800, spacing=12)
    label(c, "NEARLY 2 TRILLION IMMUNE CELLS", 960, 1030, (255, 220, 210), 26)


def sf2(c, t):
    """The walls: outside air above, the skin barrier below, microbes bouncing off; Kai inside, unbothered."""
    outside_world(c, t, 600)
    skin_wall(c, 0, 600, W, 480, t)
    c.drawRect(skia.Rect.MakeXYWH(0, 600, W, 480), fill((90, 10, 40), 50))
    rng = np.random.default_rng(3)
    for k, (x, y, ang) in enumerate([(240, 470, 110), (560, 530, 70), (870, 400, 100), (1180, 520, 80), (1460, 440, 120), (1730, 520, 60)]):
        if k % 3 == 2:
            virus(c, x, y, 40, t + k)
        else:
            bacterium(c, x, y, 52, t + k, -ang, mood="scared" if k % 2 else "sneaky")
        if y > 480:
            sparkle(c, x + 10, 594, 46, 240, (255, 250, 230))
            for j in range(3):
                an = math.radians(-150 + j * 60)
                c.drawLine(x + 10 + math.cos(an) * 40, 590 + math.sin(an) * 40, x + 10 + math.cos(an) * 70, 590 + math.sin(an) * 70, stroke(WHITE, 4, 200))
    kai_at(c, 1650, 900, 120, t, "smug", (-0.6, -0.8), rim=(255, 180, 160))
    tag(c, "SKIN · LAYER UPON LAYER OF DEAD CELLS", 520, 790, (255, 230, 220), 26)
    text(c, "OUTSIDE", 120, 70, 20, (180, 120, 100), 220, 800, "left", spacing=6)


def sf3(c, t):
    """First responders: neutrophils pour out of a leaky vessel, one bursts into a DNA net, a macrophage feeds; Kai watches."""
    body_world(c, t)
    vessel(c, -40, 960, W + 80, 230, t, leak=0.9)
    for k, (x, y) in enumerate([(260, 760), (520, 640), (760, 780)]):
        neutrophil(c, x, y, 66, t + k, "determined", (0.4, -0.7), seed=k)
        c.drawLine(x, y - 90, x + 30, y - 170, stroke((255, 220, 230), 5, 140))
    neutrophil(c, 1000, 380, 80, t, burst=0.6, seed=5)
    rng = np.random.default_rng(1)
    for k in range(9):
        an = rng.uniform(0, 6.28)
        d = rng.uniform(140, 330)
        bacterium(c, 1000 + math.cos(an) * d, 380 + math.sin(an) * d * 0.7, 28, t, math.degrees(an), mood="scared", wiggle=0.2)
    bacterium(c, 470, 260, 40, t, 200, mood="scared", wiggle=3)
    macrophage(c, 280, 300, 130, t, "hungry", (0.9, -0.2), gulp=(-5, 0.75), belly=((-0.3, 0.45, 0.2, 0.4),))
    kai_at(c, 1720, 640, 210, t, "shocked", (-0.9, -0.3), rim=(255, 210, 190))
    near_blur(c, [(1900, 1040, 220)], t, (210, 90, 110))
    tag(c, "NEUTROPHILS", 520, 520, (240, 220, 255), 26)
    tag(c, "NET OF DNA", 1000, 120, (220, 170, 255), 26)


def sf4(c, t):
    """The base: inside a lymph node, a dendritic cell shows the enemy; the one matching T cell lights up. Kai looks on."""
    lymph_world(c, t)
    dendritic(c, 420, 560, 110, t, "happy", (0.6, -0.1), carry=GERM, rim=(170, 210, 255))
    keys = [(255, 120, 120), (120, 255, 160), (160, 160, 255), GERM, (255, 120, 255), (120, 220, 255)]
    for k, kc in enumerate(keys):
        x, y = 820 + (k % 3) * 280, 340 + (k // 3) * 340
        match = kc == GERM
        if match:
            light(c, x, y, 300, GERM, 230, core=0)
            c.drawCircle(x, y, 120, stroke(GERM, 6, 230))
            tag(c, "MATCH!", x, y - 150, GERM, 26)
            c.drawLine(420 + 130, 560 - 120, x - 110, y, stroke(GERM, 4, 160))
        t_cell(c, x, y, 82, t + k, "helper", "shocked" if match else "neutral", (-0.7, 0), key=kc, seed=k, rim=(170, 210, 255))
    kai_at(c, 1690, 640, 170, t, "focused", (-0.8, 0.0), rim=(150, 200, 255))
    near_blur(c, [(60, 60, 200), (1880, 80, 160)], t, (90, 120, 200))
    label(c, "LYMPH NODE", 960, 1020, (190, 220, 255), 30)


def sf5(c, t):
    """Special forces: Kai and his clones corner an infected cell; a plasma cell fires antibodies at bacteria."""
    body_world(c, t)
    b_cell(c, 260, 260, 110, t, "determined", (0.7, 0.2), plasma=1.0)
    for k in range(14):
        u = k / 14
        antibody(c, 400 + u * 1200, 300 + 60 * math.sin(u * 7), 34, 90 + k * 37)
    for k, (x, y) in enumerate([(1500, 230), (1700, 330)]):
        bacterium(c, x, y, 40, t + k, 160, mood="scared", tag=1.0, wiggle=0.3)
    infected_cell(c, 1300, 680, 200, t)
    for k, (x, y, r) in enumerate([(330, 640, 92), (420, 880, 88), (210, 860, 80)]):
        kai_at(c, x, y, r, t + k * 0.7, "determined", (0.9, -0.1))
    kai_at(c, 780, 690, 190, t, "angry", (0.9, 0.0), rim=(255, 220, 160))
    near_blur(c, [(1960, 1060, 240)], t, (200, 80, 110))
    tag(c, "KILLER T CELLS", 520, 1030, (255, 170, 150), 26)


def sf6(c, t):
    """Memory: after the battle, memory cells study a wanted poster (vaccines)."""
    body_world(c, t)
    c.drawPaint(fill((255, 200, 160), 18))
    wanted(c, 960, 470, 400, t)
    t_cell(c, 480, 640, 100, t, "helper", "focused", (0.8, -0.3), memory=True)
    b_cell(c, 1440, 640, 100, t, "focused", (-0.8, -0.3), memory=True)
    kai_at(c, 1640, 910, 110, t, "wink", (-0.4, -0.3))
    near_blur(c, [(-40, 1000, 230)], t, (200, 80, 110))
    label(c, "MEMORY CELLS", 960, 1010, (255, 230, 150), 32)


def sf7(c, t):
    """Outro: a child hugging a knee with a plaster; a magnifier into the knee shows Kai, victorious. End line."""
    c.drawPaint(shaded(linear((0, 0), (0, H), [(110, 140, 190), (196, 150, 160)])))
    light(c, 300, 100, 900, (255, 230, 210), 50)
    c.drawRect(skia.Rect.MakeXYWH(0, 860, W, 220), fill((150, 110, 130)))
    child(c, 330, 880, 120, t)
    kx, ky = 330 + 192, 880 - 204
    cx, cy, R = 1300, 400, 290
    c.drawLine(kx + 40, ky - 20, cx - R * 0.93, cy + R * 0.3, stroke(WHITE, 5, 200))
    c.save()
    bubble = skia.Path()
    bubble.addCircle(cx, cy, R)
    c.clipPath(bubble, doAntiAlias=True)
    c.translate(cx - W / 2, cy - H / 2)
    body_world(c, t)
    for k in range(3):
        bacterium(c, W / 2 + 170 + k * 30, H / 2 - 130 + k * 100, 26, t + k, 30, mood="scared", tag=0.8)
    kai_at(c, W / 2 - 40, H / 2 + 30, 150, t, "laugh", (0.0, 0.0))
    c.restore()
    c.drawCircle(cx, cy, R, stroke(WHITE, 14))
    c.drawCircle(cx, cy, R + 12, stroke((60, 40, 70), 4, 120))
    text(c, "THERE'S A WAR INSIDE YOU", 1300, 860, 40, WHITE, 255, 800, spacing=6)
    text(c, "AND YOU'RE WINNING", 1300, 950, 62, (255, 214, 120), 255, 800, spacing=8)


FRAMES = {1: (sf1, "HOOK"), 2: (sf2, "THE WALLS"), 3: (sf3, "FIRST RESPONDERS"), 4: (sf4, "THE MESSENGER"),
          5: (sf5, "SPECIAL FORCES"), 6: (sf6, "MEMORY"), 7: (sf7, "YOU'RE WINNING")}

if __name__ == "__main__":
    from PIL import Image
    from premium import render_premium
    os.makedirs(OUT, exist_ok=True)
    for n in [int(a) for a in sys.argv[1:]] or sorted(FRAMES):
        fn, name = FRAMES[n]
        p = os.path.join(OUT, f"sf{n}_{name.lower().replace(' ', '_').replace(chr(39), '')}.png")
        Image.fromarray(render_premium(fn, 1.6, samples=1)).save(p)
        print(p)
