"""0:00:00 · THE SIP. The TV warms up on a 90s title card: chrome CAFFEINE logo over a neon grid and Memphis confetti;
the mug mascot takes a sip (SLURP!), and a "6 HOURS" starburst pops as the tape is about to begin.

  python3 render.py part1 [--still 1,2.5,4,6]
"""
from tv import *  # noqa: F401,F403

PART = "part1"
G = Show(PART)
VO, TM, DURATION = G.VO, G.TM, G.DURATION
VHS, SAMPLES = True, 2
T_SIP = G.w("H1", "sip")
T_H2 = VO["H2"]
T_SIX = G.w("H2", "six")


def scene(c, t):
    gradient_bg(c, (40, 10, 90), (160, 20, 120))
    for k in range(9):                                     # sunset stripes behind the horizon
        y = 820 + k * 22
        c.drawRect(skia.Rect.MakeLTRB(0, y, W, y + 22 - k * 2), fillp(mix(YELLOW, MAGENTA, k / 8), 160))
    starburst(c, 540, 560, 260, 470, 16, mix(MAGENTA, PURPLE, 0.3), t * 12, 200)
    memphis(c, t, 3, 230, area=(0, 380, W, 1000))
    c.drawRect(skia.Rect.MakeLTRB(0, 1010, W, H), fillp((20, 0, 40)))
    grid_floor(c, t, 1010, TEAL, 255, 0.9)
    # the logo spins in once the picture is up
    u = out_back(prog(t, 0.8, 1.4), 1.6)
    if u > 0:
        c.save()
        c.translate(540, 560)
        c.rotate(lerp(-25, -6, min(1, u)))
        c.scale(u, u)
        label(c, "THE", -250, -150, 64, "righteous", YELLOW, 255)
        chrome_text(c, "Caffeine", 0, 20, 190, "shrik", 255, depth=18)
        c.restore()
        v = appear(t, 1.15)
        if v > 0:
            c.save()
            c.translate(560, 690)
            c.rotate(-6)
            c.scale(v, v)
            c.drawRect(skia.Rect.MakeLTRB(-300, -52, 300, 22), fillp(TEAL))
            c.drawRect(skia.Rect.MakeLTRB(-300, 14, 300, 22), fillp(YELLOW))
            label(c, "THE NEXT 6 HOURS", 0, 2, 54, "archivo", NAVY, 255, "center")
            c.restore()
    # the mascot sips
    sip = smooth(prog(t, T_SIP - 0.35, T_SIP)) * (1 - smooth(prog(t, T_SIP + 0.6, T_SIP + 1.0)))
    hop = abs(math.sin(t * 2 * math.pi * 92 / 60 / 2)) * 10
    mug(c, 540, 940 - hop - 30 * sip, 0.82 * appear(t, 1.0, 0.5), t, tilt=-24 * sip, steam=1 - sip,
        face="wired" if t > T_SIP + 0.3 else "happy", fill_k=0.85 - 0.25 * smooth(prog(t, T_SIP - 0.2, T_SIP + 0.4)))
    v = appear(t, T_SIP)
    if v > 0 and t < T_H2 + 0.3:
        c.save()
        c.translate(270, 820)
        c.rotate(-12)
        c.scale(v, v)
        starburst(c, 0, 0, 80, 120, 12, WHITE, 0)
        starburst(c, 0, 0, 70, 108, 12, YELLOW, 0)
        outlined(c, "SLURP!", 0, 16, 50, "bowlby", RED, 255, ow=0.08)
        c.restore()
    v = appear(t, T_SIX - 0.1)
    if v > 0:
        c.save()
        c.translate(850, 860)
        c.rotate(10 + 4 * math.sin(t * 3))
        c.scale(v, v)
        starburst(c, 0, 0, 110, 150, 14, RED, t * 20)
        starburst(c, 0, 0, 96, 132, 14, YELLOW, t * 20)
        outlined(c, "6", 0, 20, 110, "bowlby", RED, 255, ow=0.06)
        outlined(c, "HOURS", 0, 70, 40, "archivo", NAVY, 255, ow=0.0)
        c.restore()


def draw_frame(c, t):
    G.frame(c, t, scene)


OVERLAY = G.overlay


def POST(t):
    return G.post(t)


def sfx_events():
    return G.sfx() + [(0.85, "chime", 0.5), (T_SIP - 0.3, "slurp", 0.7), (T_SIP, "pop", 0.5), (T_SIX - 0.1, "ding", 0.45)]


MUSIC = G.music()

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
