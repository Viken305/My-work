"""Part 4: Chapter 3, The Runaway Moon. A clock: 1.4 billion years ago a day was under 19 hours; the Moon's tidal
pull raises bulges that brake Earth's spin; the Moon drifts away 3.8 cm a year (fingernail comparison).

  python3 render.py part4 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part4"
VO, _end = schedule(PART, first=3.4, gap=1.35)
DURATION = _end + 2.4
TM = Timing(PART, VO)

AGO_T = TM.word("D1", "one point four") - 0.3
HOURS_T = TM.word("D1", "nineteen hours") - 0.4
MOON_T = VO["D2"] - 0.5
TIDE_T = TM.word("D2", "pulls on our oceans") - 0.3
BRAKE_T = TM.word("D2", "brakes") - 0.4
DRIFT_T = VO["D3"] - 0.5
CM_T = TM.word("D3", "three point eight") - 0.3
NAIL_T = TM.word("D3", "fingernails") - 0.6

NIM_TRACK = Track([(0.0, "neutral", 0.0), (AGO_T, "focused", 0.4), (HOURS_T, "shocked", 0.2), (HOURS_T + 1.2, "happy", 0.4), (TIDE_T, "focused", 0.4),
                   (BRAKE_T, "worried", 0.4), (CM_T, "shocked", 0.2), (NAIL_T, "laugh", 0.35), (NAIL_T + 1.5, "smug", 0.4)])
MOON_TRACK = Track([(0.0, "smug", 0.0), (BRAKE_T, "wink", 0.25), (BRAKE_T + 1.0, "smug", 0.3), (DRIFT_T + 0.6, "happy", 0.4), (NAIL_T + 1.0, "wink", 0.25)])


def clock(c, x, y, r, t, hours, a=255):
    """A 24 h dial; the filled wedge shows the length of a day."""
    c.drawCircle(x, y, r, fill((20, 26, 60), a))
    c.drawCircle(x, y, r, stroke(WHITE, 6, a))
    for h in range(24):
        an = math.radians(-90 + h * 15)
        rr = r * (0.86 if h % 6 else 0.78)
        c.drawLine(x + math.cos(an) * rr, y + math.sin(an) * rr, x + math.cos(an) * r * 0.94, y + math.sin(an) * r * 0.94, stroke(WHITE, 3 if h % 6 else 5, a * 0.8))
    wedge = skia.Path()
    wedge.moveTo(x, y)
    wedge.arcTo(skia.Rect.MakeXYWH(x - r * 0.72, y - r * 0.72, r * 1.44, r * 1.44), -90, 360 * hours / 24, False)
    wedge.close()
    c.drawPath(wedge, fill(GOLD, 0.75 * a))
    an = math.radians(-90 + 360 * hours / 24)
    c.drawLine(x, y, x + math.cos(an) * r * 0.8, y + math.sin(an) * r * 0.8, stroke(WHITE, 8, a))
    c.drawCircle(x, y, 10, fill(WHITE, a))
    text(c, f"{hours:.0f} H" if hours > 23.9 else f"{hours:.1f} H", x, y + r + 60, 44, GOLD, a, 800, spacing=4)


def moon(c, x, y, r, t, p, look=(0.0, 0.0)):
    c.drawCircle(x, y, r, shaded(radial((x - r * 0.35, y - r * 0.35), r * 1.5, [(240, 240, 236), (196, 196, 196), (120, 120, 130)])))
    for dx, dy, rr in ((-0.4, 0.3, 0.18), (0.35, -0.3, 0.14), (0.2, 0.45, 0.1), (-0.15, -0.5, 0.08)):
        c.drawCircle(x + dx * r, y + dy * r, rr * r, fill((150, 150, 158)))
    face_rig(c, x, y - r * 0.05, r * 0.85, p, look, 0.0, ink=(50, 50, 70))


def scene_clock(c, t):
    sky(c, t, mood="space")
    hrs = lerp(24, 18.7, in_out(prog(t, AGO_T, HOURS_T + 0.8)))
    a = smooth(prog(t, AGO_T - 0.8, AGO_T))
    clock(c, 760, 500, 260, t, hrs, 255 * a)
    big_number(c, "1.4 BILLION YEARS AGO", 760, 140, 54, (200, 210, 255), t, AGO_T, MOON_T)
    chip(c, "A DAY LASTED LESS THAN 19 HOURS", 760, 970, GOLD, t, HOURS_T + 0.4, MOON_T)
    globe(c, 1480, 560, 170, t, rot=t * (0.2 + 1.8 * smooth(prog(t, AGO_T, HOURS_T))), tilt=0.3)

    def path(tt):
        return 1560 + 15 * math.sin(tt), 300 + 12 * math.sin(tt * 1.3)
    nim(c, t, NIM_TRACK, path, 90, look=(-0.8, 0.3), rim=(150, 200, 255))


def scene_tides(c, t):
    """Top-down Earth with an ocean bulge pulled towards the Moon; friction arrows slow the spin; Moon spirals out."""
    sky(c, t, mood="space")
    ex, ey, er = 760, 560, 230
    away = in_out(prog(t, DRIFT_T, DURATION))
    md = lerp(620, 780, away)
    man = math.radians(-14) + 0.03 * (t - MOON_T)
    mx, my = ex + math.cos(man) * md, ey + math.sin(man) * md * 0.55
    tide = smooth(prog(t, TIDE_T - 0.4, TIDE_T + 0.6))
    # ocean bulge (ellipse pointing at the Moon, slightly ahead because Earth's spin drags it)
    c.save()
    c.translate(ex, ey)
    c.rotate(math.degrees(man) + 12)
    c.drawOval(skia.Rect.MakeXYWH(-er * (1 + 0.28 * tide), -er * (1 - 0.06 * tide), er * 2 * (1 + 0.28 * tide), er * 2 * (1 - 0.06 * tide)),
               fill((70, 150, 230), 170 * tide))
    c.restore()
    globe(c, ex, ey, er, t, rot=t * lerp(0.9, 0.5, smooth(prog(t, BRAKE_T, BRAKE_T + 3))), tilt=1.3, clouds=True)
    if tide > 0.3:     # gravity pull lines
        for k in range(5):
            u = ((t * 0.8 + k / 5) % 1.0)
            x0 = lerp(mx, ex + er * 1.25 * math.cos(man), u)
            y0 = lerp(my, ey + er * 1.25 * math.sin(man) * 0.55, u)
            c.drawCircle(x0, y0, 5, fill((200, 220, 255), 200 * (1 - u)))
    b = smooth(prog(t, BRAKE_T - 0.2, BRAKE_T + 0.4))
    if b > 0:          # friction / brake arrows against the spin
        for k in range(3):
            an = math.radians(200 + k * 45)
            c.drawArc(skia.Rect.MakeXYWH(ex - er * 1.35, ey - er * 1.35, er * 2.7, er * 2.7), math.degrees(an), 30, False, stroke((255, 140, 120), 8, 230 * b))
            tx, ty = ex + math.cos(an) * er * 1.35, ey + math.sin(an) * er * 1.35
            c.drawCircle(tx, ty, 9, fill((255, 140, 120), 230 * b))
        chip(c, "TIDAL BRAKE", ex, ey + er + 90, (255, 160, 140), t, BRAKE_T, DRIFT_T + 0.2)
    if away > 0:       # spiral trail
        trail = skia.Path()
        for i in range(60):
            u = i / 59
            dd = lerp(560, md, u)
            aa = man - 0.5 * (1 - u)
            (trail.moveTo if i == 0 else trail.lineTo)(ex + math.cos(aa) * dd, ey + math.sin(aa) * dd * 0.55)
        pe = stroke(WHITE, 3, 150)
        pe.setPathEffect(skia.DashPathEffect.Make([14, 12], 0))
        c.drawPath(trail, pe)
    moon(c, mx, my, 80, t, MOON_TRACK.at(t), (-0.7, 0.2))
    big_number(c, "3.8 CM", 1180, 150, 100, (220, 225, 255), t, CM_T, DURATION, sub="FARTHER AWAY EVERY YEAR")
    if t > NAIL_T:    # fingernail comparison
        a = smooth(prog(t, NAIL_T, NAIL_T + 0.5))
        fx, fy = 1720, 760
        c.drawRRect(rrect(fx - 70, fy - 30, 140, 260, 70), fill((206, 150, 124), 255 * a))
        c.drawRRect(rrect(fx - 50, fy - 20, 100, 120, 44), fill((236, 170, 170), 255 * a))
        grow = 18 * smooth(prog(t, NAIL_T + 0.3, NAIL_T + 2.5))
        c.drawRRect(rrect(fx - 50, fy - 20 - grow, 100, 30, 14), fill((236, 228, 220), 255 * a))
        text(c, "≈ YOUR FINGERNAILS", fx, fy + 280, 26, WHITE, 255 * a, 800, spacing=4)

    def path(tt):
        return 300 + 15 * math.sin(tt), 300 + 12 * math.sin(tt * 1.3)
    nim(c, t, NIM_TRACK, path, 90, look=(0.8, 0.2), rim=(150, 200, 255))
    chip(c, "THE MOON'S GRAVITY PULLS ON OUR OCEANS", 960, 110, (190, 210, 255), t, TIDE_T, BRAKE_T)


def draw_frame(c, t):
    xfade(c, t, MOON_T - 0.4, 0.9, scene_clock, scene_tides, 0.25)
    chapter_title(c, t, 3, "THE RUNAWAY MOON", (200, 210, 255), 0.2, 2.8)
    fade(c, t, DURATION, 0.5, 0.7)


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (AGO_T - 0.6, "whoosh_long", 0.6), (AGO_T, "ticks", 0.6), (AGO_T + 1.2, "ticks", 0.6), (HOURS_T, "ding", 0.8),
            (MOON_T - 0.4, "whoosh_long", 0.7), (TIDE_T, "bubble", 0.6), (TIDE_T + 0.4, "swell_soft", 0.6), (BRAKE_T, "rumble", 0.7), (BRAKE_T + 0.5, "slide", 0.5),
            (DRIFT_T, "whoosh", 0.6), (CM_T, "pop", 0.8), (CM_T + 0.05, "shine", 0.6), (NAIL_T, "pop", 0.6), (NAIL_T + 0.5, "chime", 0.6)]


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 14, 19)), (AGO_T, 43, (0, 7, 12, 15, 19)), (HOURS_T, 47, (0, 7, 12, 16, 19)), (MOON_T, 45, (0, 7, 12, 15, 19)),
            (DRIFT_T, 48, (0, 7, 12, 16, 19)), (NAIL_T, 50, (0, 7, 12, 16, 21))],
    plucks=[(VO["D1"], DURATION)], bpm=92, rises=[(AGO_T, HOURS_T), (DRIFT_T, CM_T)], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
