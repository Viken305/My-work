"""PRESS PLAY (hook). A neon play button is pressed, the beat drops, the equaliser runner flies together out of bars;
the organs light up as their lanes hit; then the level select.

  python3 render.py part1 [--still 0.2,1,3,8]
"""
from game import *  # noqa: F401,F403

PART = "part1"
G = Game(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
PREMIUM, SAMPLES = True, 4
PRESS = 0.38                                          # the play button goes down
G.flash_t = G.beat0 = PRESS
G.hud_a = lambda t: 255 * smooth(prog(t, PRESS + 0.2, PRESS + 0.6))
T_GAME = G.w("H1", "rhythm")
T_ORG = G.w("H2", "every")
T_LVL = G.w("H3", "level")
ORGANS = [("BRAIN", (575, 455), (250, 430)), ("LUNGS", (520, 560), (830, 470)),
          ("HEART", (540, 610), (230, 760)), ("MUSCLE", (620, 860), (850, 820))]
TILES = [("1", "IGNITION", GOLD), ("2", "AIR", CYN), ("3", "FUEL", LIME), ("4", "MAX HEART", RED), ("5", "HEAT", ORANGE), ("B", "BONUS", VIOLET)]


def play_button(c, t):
    if t > PRESS + 0.5:
        return
    u = prog(t, PRESS, PRESS + 0.12)
    sc = (1 + 0.05 * math.sin(t * 14)) * (1 - 0.18 * math.sin(math.pi * u)) * (1 + 1.6 * in_cubic(prog(t, PRESS + 0.12, PRESS + 0.5)))
    a = 255 * (1 - smooth(prog(t, PRESS + 0.15, PRESS + 0.5)))
    c.save()
    c.translate(540, 640)
    c.scale(sc, sc)
    light(c, 0, 0, 420, MAG, 140 * a / 255)
    c.drawCircle(0, 0, 190, fillp((20, 6, 30), a))
    c.drawCircle(0, 0, 190, stroke(MAG, 14, a))
    c.drawCircle(0, 0, 222, stroke(CYN, 5, 0.7 * a))
    c.drawPath(path_of([(-55, -90), (95, 0), (-55, 90)], True), fillp(WHITE, a))
    c.restore()
    label(c, "PRESS PLAY", 540, 930, 46, "bungee", WHITE, a * (0.6 + 0.4 * (math.sin(t * 12) > 0)), "center")


def organs(c, t):
    for i, (name, (ax, ay), (bx, by)) in enumerate(ORGANS):
        v = appear(t, T_ORG + 0.15 * i)
        if v <= 0:
            continue
        a = 255 * (1 - smooth(prog(t, T_LVL - 0.3, T_LVL)))
        rgb = LANES[i]
        hit = max([1 - prog(t, n["t0"], n["t0"] + 0.25) for n in G.notes if n["lane"] == i and T_ORG <= n["t0"] <= t] + [0])
        ex, ey = lerp(ax, bx, v), lerp(ay, by, v)
        c.drawLine(ax, ay, ex, ey, stroke(rgb, 4, 0.8 * a))
        c.drawCircle(ax, ay, 9, fillp(rgb, a))
        w = width(name, "bungee", 40) + 50
        c.save()
        c.translate(ex, ey)
        c.scale(v * (1 + 0.15 * hit), v * (1 + 0.15 * hit))
        light(c, 0, 0, 200, rgb, (60 + 160 * hit) * a / 255)
        c.drawRRect(rrect(-w / 2, -34, w, 68, 34), fillp(mix(rgb, (0, 0, 0), 0.7 - 0.4 * hit), a))
        c.drawRRect(rrect(-w / 2, -34, w, 68, 34), stroke(rgb, 5, a))
        label(c, name, 0, 15, 40, "bungee", WHITE, a, "center")
        c.restore()


def level_select(c, t):
    if t < T_LVL - 0.2:
        return
    for i, (num, name, rgb) in enumerate(TILES):
        v = appear(t, T_LVL - 0.15 + 0.12 * i, 0.4)
        if v <= 0:
            continue
        col_, row = i % 3, i // 3
        x, y = 210 + col_ * 330, 500 + row * 260
        on = 1 - prog(G.phase(t) % 6 - i, 0, 1) if G.phase(t) % 6 >= i else 0     # a light runs through the tiles
        c.save()
        c.translate(x, y)
        c.scale(v, v)
        light(c, 0, 0, 220, rgb, 50 + 130 * on)
        c.drawRRect(rrect(-140, -105, 280, 210, 28), fillp(mix(rgb, (0, 0, 0), 0.78 - 0.3 * on)))
        c.drawRRect(rrect(-140, -105, 280, 210, 28), stroke(rgb, 6))
        if num != "B":
            outlined(c, num, 0, 20, 100, "bungee", WHITE, 255, glow_rgb=rgb)
        else:
            star(c, 0, -10, 52, WHITE)
        label(c, name, 0, 82, 30 if len(name) < 8 else 26, "bungee", mix(rgb, WHITE, 0.4), 255, "center")
        c.restore()


def star(c, x, y, r, rgb, a=255):
    pts = [(x + math.cos(-math.pi / 2 + k * math.pi / 5) * (r if k % 2 == 0 else r * 0.45),
            y + math.sin(-math.pi / 2 + k * math.pi / 5) * (r if k % 2 == 0 else r * 0.45)) for k in range(10)]
    c.drawPath(path_of(pts, True), fillp(rgb, a))


def scene(c, t):
    play_button(c, t)
    if t >= PRESS + 0.05:
        k = prog(t, PRESS + 0.05, PRESS + 0.6)
        for j in range(2):                               # shockwave of the drop
            u = prog(t, PRESS + 0.05 + 0.1 * j, PRESS + 0.75 + 0.1 * j)
            if 0 < u < 1:
                c.drawCircle(540, 640, 100 + 900 * out_cubic(u), stroke((MAG, CYN)[j], 16 * (1 - u) + 1, 255 * (1 - u)))
        ra = 255 * (1 - smooth(prog(t, T_LVL - 0.35, T_LVL - 0.05)))
        runner(c, G, t, 540, 670, 1.0, ra, assemble=out_cubic(k))
        organs(c, t)
        level_select(c, t)


def draw_frame(c, t):
    G.frame(c, t, scene, 255)
    if t < PRESS:                                        # before the drop the stage is dark
        c.drawPaint(fillp((0, 0, 0), 130))
        play_button(c, t)


OVERLAY, POST = G.overlay, G.post


def sfx_events():
    return G.sfx() + [(0.0, "riser", 0.35), (PRESS, "low_hit", 0.9), (PRESS, "sub_drop", 0.6), (PRESS + 0.05, "trailer_hit", 0.35)] + \
        [(T_ORG + 0.15 * i, "pop", 0.4) for i in range(4)] + [(T_LVL - 0.15 + 0.12 * i, "tick", 0.5) for i in range(6)]


MUSIC = dict(beds=[(PRESS, DURATION, f"drive{G.bpm}_1", 0.6)])

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
