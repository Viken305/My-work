"""Part 2: The forge. Stars fuse only up to iron (gold bounces off the iron wall); two neutron stars spiral and
collide; neutrons flood atoms and gold is forged; several Earths' worth.

  python3 render.py part2 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part2"
VO, _end = schedule(PART, first=0.4, gap=0.6)
DURATION = _end + 1.4
TM = Timing(PART, VO)

LADDER = [("H", "fuse"), ("He", "atoms"), ("C", "heavier"), ("O", "ones"), ("Si", "only"), ("Fe", "iron")]
LADDER_T = [TM.word("F1", w) - 0.15 for _, w in LADDER]
BOUNCE_T = TM.word("F1", "to build") - 0.1
EXTREME_T = TM.word("F1", "far more extreme") - 0.1
SPIRAL = (VO["F2"] - 0.3, TM.word("F2", "collide") + 0.15)
COLLIDE_T = SPIRAL[1]
NEUT_T = TM.word("F3", "flooded") - 0.2
FORGE_T = TM.word("F3", "gold are forged") - 0.1
EARTHS_T = TM.word("F3", "several") - 0.1
CX, CY = W / 2, 900

CAPS = Captions(TM, anchors={"F1": (W / 2, 300), "F2": (W / 2, 330), "F3": (W / 2, 330)},
                heroes={"GOLD": (W / 2, 1260, 190), "IRON.": (W / 2, 1300, 150)},
                reacts={"COLLIDE.": (react_collide, W / 2, 1480, 130)})


def star_scene(c, t):
    """A star's core builds heavier elements in a tower; iron is a wall; a gold tile bounces off it."""
    space_bg(c, t, warm=0.6)
    sx, sy, sr = CX, 1640, 400
    light(c, sx, sy, sr * 2.2, (255, 200, 120), 120)
    c.drawCircle(sx, sy, sr, shaded(radial((sx - sr * 0.3, sy - sr * 0.4), sr * 1.4, [(255, 250, 220), (255, 200, 110), (240, 120, 50)])))
    for k in range(5):        # granulation shimmer
        an = t * 0.3 + k * 1.3
        c.drawCircle(sx + math.cos(an) * sr * 0.5, sy + math.sin(an) * sr * 0.4, sr * 0.22, fill((255, 230, 160), 50))
    for i, (sym, _) in enumerate(LADDER):
        t0 = LADDER_T[i]
        u = out_back(prog(t, t0, t0 + 0.45), 1.6)
        if u <= 0:
            continue
        y = lerp(sy - sr * 0.6, 1180 - i * 98, out_cubic(prog(t, t0, t0 + 0.45)))
        element(c, sym, CX, y, 86, 255 * min(1, u * 2), 0.6 + 0.4 * u)
    if t > LADDER_T[-1]:     # iron wall
        wy = 1180 - 5 * 98 - 72
        k = out_back(prog(t, LADDER_T[-1] + 0.1, LADDER_T[-1] + 0.5), 1.4)
        c.drawRRect(rrect(CX - 230 * k, wy - 14, 460 * k, 28, 14), fill((255, 90, 80)))
        light(c, CX, wy, 260, (255, 80, 70), 120 * k)
        text(c, "STOP", CX, wy + 9, 22, WHITE, 255 * k, 800, spacing=6)
    if t > BOUNCE_T:         # gold tile tries to stack and bounces off the wall
        u = prog(t, BOUNCE_T, BOUNCE_T + 1.4)
        wy = 1180 - 5 * 98 - 72
        y = lerp(wy - 40, wy - 200, out_cubic(u)) if u < 0.35 else wy - 200 + 150 * math.exp(-(u - 0.35) * 4) * abs(math.sin((u - 0.35) * 12))
        x = CX + 260 * (u > 0.35) * prog(u, 0.35, 1.0)
        element(c, "Au", x, y, 96, 255, 1.0)
        if 0.3 < u < 0.42:
            light(c, CX, wy, 300, (255, 120, 90), 200)
    if t > EXTREME_T:
        sh = 10 * math.exp(-(t - EXTREME_T) * 2)
        c.translate(sh * math.sin(t * 50), sh * math.cos(t * 43))


def merger_scene(c, t):
    k = in_out(prog(t, SPIRAL[0], COLLIDE_T + 3))
    sh = 26 * math.exp(-(t - COLLIDE_T) * 4) if t > COLLIDE_T else 0.0
    cam = Cam(sh * math.sin(t * 61), sh * math.cos(t * 53), lerp(1.0, 1.12, k))
    space_bg(c, t, cam, warm=0.3 * smooth(prog(t, COLLIDE_T, COLLIDE_T + 1)))
    cam.push(c, 1.0)
    c.translate(-W / 2, -H / 2)
    if t < COLLIDE_T:
        pre = clamp((COLLIDE_T - t) / (COLLIDE_T - SPIRAL[0]))
        rr = 26 + 380 * pre ** 0.8
        ph = 16 * (1 - pre) ** 0.55 + t * 0.4
        for i in range(6):     # gravitational ripples
            rk = (t * (0.7 + 1.5 * (1 - pre)) + i / 6) % 1.0
            c.drawOval(skia.Rect.MakeXYWH(CX - 900 * rk, CY - 360 * rk, 1800 * rk, 720 * rk), stroke((150, 140, 255), 3, 120 * (1 - rk)))
        for s in (0, math.pi):
            x, y = CX + math.cos(ph + s) * rr, CY + math.sin(ph + s) * rr * 0.42
            for j in range(10):   # orbit trail
                pj = ph + s - j * 0.08
                c.drawCircle(CX + math.cos(pj) * rr, CY + math.sin(pj) * rr * 0.42, 10 - j * 0.8, add(NEUTRON, 120 - j * 11))
            neutron_star(c, x, y, 32, t)
        chip(c, "NEUTRON STARS", W / 2, 520, NEUTRON, t, SPIRAL[0] + 0.4, COLLIDE_T)
    else:
        kk = prog(t, COLLIDE_T, DURATION + 2)
        kilonova(c, CX, CY, 720, t, 0.06 + 0.55 * out_cubic(kk), seed=11)
        if t > NEUT_T:         # neutrons (blue) stream into seed atoms, which turn gold
            rng = np.random.default_rng(4)
            for i in range(16):
                an = rng.uniform(0, 6.28)
                d = rng.uniform(180, 520)
                ax, ay = CX + math.cos(an) * d, CY + math.sin(an) * d * 0.9
                g = smooth(prog(t, FORGE_T - 0.4 + i * 0.05, FORGE_T + 0.3 + i * 0.05))
                for j in range(6):
                    u = ((t * 1.6 + j / 6 + i * 0.13) % 1.0)
                    jx, jy = ax + math.cos(an + j) * 120 * (1 - u), ay + math.sin(an + j) * 120 * (1 - u)
                    c.drawCircle(jx, jy, 5, add(NEUTRON, 220 * (1 - g) * u))
                c.drawCircle(ax, ay, 16, fill((150, 150, 170), 255 * (1 - g)))
                if g > 0:
                    gold_sphere(c, ax, ay, 16 * (0.6 + 0.4 * out_back(g, 2)), (255, 170, 110), 255 * g)
    cam.pop(c)
    # several Earths' worth of gold: Earths line up and turn gold one by one
    if t > EARTHS_T - 0.2:
        for i in range(4):
            x = 210 + i * 220
            g = out_back(prog(t, EARTHS_T + i * 0.25, EARTHS_T + i * 0.25 + 0.5), 1.6)
            if g <= 0:
                continue
            gk = smooth(prog(t, EARTHS_T + 0.9 + i * 0.25, EARTHS_T + 1.4 + i * 0.25))
            mini_earth(c, x, 1520, 85 * g, t, gk)
        chip(c, "SEVERAL EARTHS' WORTH", W / 2, 1700, GOLD, t, EARTHS_T + 1.2)


def draw_frame(c, t):
    if t < SPIRAL[0] + 0.2:
        star_scene(c, t)
        if t > SPIRAL[0] - 0.3:
            c.drawPaint(fill((4, 4, 14), 255 * smooth(prog(t, SPIRAL[0] - 0.3, SPIRAL[0]))))
    else:
        merger_scene(c, t)
        if t < SPIRAL[0] + 0.5:
            c.drawPaint(fill((4, 4, 14), 255 * (1 - smooth(prog(t, SPIRAL[0] + 0.2, SPIRAL[0] + 0.5)))))
    CAPS.draw(c, t)
    fade(c, t, DURATION, 0.3, 0.3)


def sfx_events():
    ev = [(0.2, "swell_soft", 0.6)] + [(x, "pop", 0.6) for x in LADDER_T] + [(LADDER_T[-1] + 0.2, "click", 1.0), (BOUNCE_T + 0.45, "tink", 1.0),
                                                                        (BOUNCE_T + 0.5, "boom", 0.4), (EXTREME_T, "rumble", 0.7)]
    ev += [(SPIRAL[0], "whoosh_long", 0.7), (SPIRAL[0] + 0.3, "riser", 0.9), (COLLIDE_T, "boom", 1.0), (COLLIDE_T + 0.02, "flicker", 0.8),
           (COLLIDE_T + 0.1, "rumble", 1.0), (NEUT_T, "shimmer", 0.6), (FORGE_T, "shine", 1.0), (FORGE_T + 0.1, "chime", 0.7)]
    ev += [(EARTHS_T + i * 0.25, "pop", 0.6) for i in range(4)] + [(EARTHS_T + 0.9 + i * 0.25, "tink", 0.5) for i in range(4)]
    return ev


MUSIC = dict(chords=[(0.0, 48, (0, 7, 12, 16, 19)), (LADDER_T[-1], 46, (0, 7, 12, 15, 18)), (SPIRAL[0], 45, (0, 7, 12, 15, 19)),
                     (COLLIDE_T, 43, (0, 7, 12, 16, 19, 24)), (EARTHS_T, 48, (0, 7, 12, 16, 21))],
             plucks=[(0.3, SPIRAL[0]), (FORGE_T, DURATION)], bpm=104, rises=[(LADDER_T[0], LADDER_T[-1]), (SPIRAL[0], COLLIDE_T)], drone=36)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
