"""Part 7: Chapter 6, You're Winning. Overreactions (pollen, autoimmunity), the quiet daily patrol through a blood
vessel, then out to the child with a plaster and Kai in the magnifier. End card.

  python3 render.py part7 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part7"
VO, _end = schedule(PART, first=3.0, gap=0.8)
DURATION = _end + 4.2
TM = Timing(PART, VO)

POLLEN_T = TM.word("O1", "pollen") - 0.6
AUTO_T = TM.word("O1", "attacks the body") - 0.4
PATROL_T = VO["O2"] - 0.5
OUT_T = VO["O3"] - 0.5
WAR_T = TM.word("O3", "war going on") - 0.3
WIN_T = TM.word("O3", "you're winning") - 0.2
END_T = _end + 0.6

PANIC = [Track([(0.0, "neutral", 0.0), (POLLEN_T + 0.5 + 0.15 * i, "shocked", 0.2), (POLLEN_T + 1.2 + 0.15 * i, "shout", 0.25),
                (AUTO_T - 0.3, "worried", 0.5)]) for i in range(3)]
POLLEN_FACE = Track([(0.0, "happy", 0.0), (POLLEN_T + 1.0, "shocked", 0.2), (POLLEN_T + 2.0, "worried", 0.4)])
SELF_CELL = Track([(0.0, "happy", 0.0), (AUTO_T + 0.5, "shocked", 0.2), (AUTO_T + 1.3, "hurt", 0.4)])
CONFUSED = Track([(0.0, "angry", 0.0), (AUTO_T + 1.6, "worried", 0.4)])
PATROL = [Track([(0.0, "happy", 0.0), (PATROL_T + 1.5 + 0.4 * i, "laugh", 0.35), (PATROL_T + 3.0 + 0.4 * i, "happy", 0.4)]) for i in range(4)]
CHILD_TRACK = Track([(0.0, "hurt", 0.0), (OUT_T + 0.6, "neutral", 0.5), (WIN_T, "happy", 0.4), (WIN_T + 1.2, "laugh", 0.35)])
KAI_TRACK = Track([(0.0, "determined", 0.0), (WIN_T, "laugh", 0.35), (END_T - 0.2, "wink", 0.25)])


def scene_over(c, t):
    k = in_out(prog(t, 0.0, PATROL_T))
    cam = Cam(lerp(-200, 260, k), 0, lerp(1.05, 1.0, k))
    body_world(c, t, cam)
    cam.push(c, 1.0)
    # harmless pollen drifting in, neutrophils panic
    for i in range(3):
        u = out_cubic(prog(t, POLLEN_T - 0.6 + 0.3 * i, POLLEN_T + 1.2 + 0.3 * i))
        px, py = lerp(-1300, -520 + 180 * i, u), -260 + 220 * i + 20 * math.sin(t + i)
        pollen(c, px, py, 52, t + i)
        face(c, px, py - 6, 46, t, POLLEN_FACE.at(t), (0.6, 0), True, i)
    for i in range(3):
        x, y = -120 + 40 * i, -280 + 260 * i
        shake_ = 8 * math.sin(t * 40 + i) * smooth(prog(t, POLLEN_T + 1.2, POLLEN_T + 1.6)) * (1 - smooth(prog(t, AUTO_T - 0.4, AUTO_T)))
        neutrophil(c, x + shake_, y, 70, t, PANIC[i].at(t), (-0.8, 0.0), seed=i)
        if POLLEN_T + 1.2 < t < AUTO_T - 0.3:
            text(c, "!", x + 40, y - 100 - 10 * math.sin(t * 9 + i), 70, ALARM, 255, 800)
    # a confused T cell attacks one of the body's own cells
    if t > AUTO_T - 1.0:
        u = out_cubic(prog(t, AUTO_T - 1.0, AUTO_T + 0.4))
        tissue_cell(c, 700, 40, 140, t, SELF_CELL.at(t), (-0.7, 0.0), blink_amount(t, SELF_CELL.change_times(), 4.0, 0.5), hurt=0.0)
        lunge = 50 * math.sin(math.pi * prog(t, AUTO_T + 0.3, AUTO_T + 0.9))
        t_cell(c, lerp(1500, 460, u) + lunge, 60, 80, t, "killer", CONFUSED.at(t), (0.8, 0.0))
        if t > AUTO_T + 0.5:
            light(c, 600, 40, 240, (255, 90, 90), 140 * math.exp(-(t - AUTO_T - 0.5) * 2))
    cam.pop(c)
    near_blur(c, [(-80, 1040, 230), (1990, 60, 200)], t, (190, 70, 100), 0.8)
    chip(c, "ALLERGIES · OVERREACTING TO HARMLESS THINGS", 960, 110, POLLEN, t, POLLEN_T + 0.8, AUTO_T)
    chip(c, "AUTOIMMUNE DISEASE · ATTACKING THE BODY", 960, 110, (255, 150, 150), t, AUTO_T + 0.4, PATROL_T + 0.3)


def scene_patrol(c, t):
    vessel_world(c, t, Cam(t * 40, 0, 1.0), flow=320)
    cast = [("kai", 640, 560, 110), ("neu", 1000, 470, 64), ("eater", 1300, 600, 110), ("helper", 360, 460, 62)]
    for i, (kind, x, y, r) in enumerate(cast):
        x += 30 * math.sin(t * 0.8 + i)
        y += 14 * math.sin(t * 1.7 + i)
        p = PATROL[i].at(t)
        if kind == "kai":
            kai(c, x, y, r, t, p, (0.6, 0.0), blink_amount(t, (), 3.9, 0.3), vel=(260, 0))
        elif kind == "neu":
            neutrophil(c, x, y, r, t, p, (0.6, 0.0), seed=i)
        elif kind == "eater":
            eater(c, x, y, r, t, p, (-0.5, 0.0), blink_amount(t, (), 4.1, 1.1), belly=((-0.45, 0.0, 0.12, 0.8),))
        else:
            t_cell(c, x, y, r, t, "helper", p, (0.6, 0.0), seed=i)
    chip(c, "EVERY HOUR · EVERY DAY", 960, 110, (255, 220, 210), t, PATROL_T + 0.6, OUT_T + 0.3)


def scene_out(c, t):
    k = in_out(prog(t, OUT_T, WAR_T + 1.0))
    c.drawPaint(shaded(linear((0, 0), (0, H), [(110, 140, 190), (196, 150, 160)])))
    light(c, 300, 100, 900, (255, 230, 210), 50)
    c.save()
    zoom = lerp(1.6, 1.0, k)
    c.translate(W / 2, H / 2)
    c.scale(zoom, zoom)
    c.translate(-W / 2 + lerp(250, 0, k), -H / 2 + lerp(-120, 0, k))
    c.drawRect(skia.Rect.MakeXYWH(-400, 860, W + 800, 600), fill((150, 110, 130)))
    child(c, 330, 880, 120, t, CHILD_TRACK.at(t), (0.7, -0.4), blink_amount(t, CHILD_TRACK.change_times(), 3.6, 0.2))
    c.restore()
    g = out_back(prog(t, WAR_T - 0.6, WAR_T + 0.4), 1.3)
    if g > 0:
        kx, ky = 330 + 192, 880 - 204
        cx, cy, R = 1300, 400, 290 * g
        c.drawLine(kx + 40, ky - 20, lerp(kx + 40, cx - R * 0.93, g), lerp(ky - 20, cy + R * 0.3, g), stroke(WHITE, 5, 200))
        c.save()
        bubble = skia.Path()
        bubble.addCircle(cx, cy, R)
        c.clipPath(bubble, doAntiAlias=True)
        c.translate(cx - W / 2, cy - H / 2)
        body_world(c, t)
        for j in range(3):
            bacterium(c, W / 2 + 170 + j * 30, H / 2 - 130 + j * 100, 26, t + j, 30, mood=pose("worried"), tag=0.8)
        kai(c, W / 2 - 40, H / 2 + 30, 150, t, KAI_TRACK.at(t), (0.0, 0.0), blink_amount(t, KAI_TRACK.change_times(), 3.9, 0.7),
            hop=0.4 * abs(math.sin(t * 8)) * smooth(prog(t, WIN_T + 0.2, WIN_T + 0.5)))
        c.restore()
        c.drawCircle(cx, cy, R, stroke(WHITE, 14))
        c.drawCircle(cx, cy, R + 12, stroke((60, 40, 70), 4, 120))
    a1 = smooth(prog(t, WAR_T, WAR_T + 0.5))
    text(c, "THERE'S A WAR INSIDE YOU", 1300, 860, 40, WHITE, 255 * a1, 800, spacing=6)
    a2 = smooth(prog(t, WIN_T, WIN_T + 0.4))
    tr = lerp(20, 8, out_cubic(prog(t, WIN_T, WIN_T + 1.5)))
    text(c, "AND YOU'RE WINNING", 1300, 950, 62, (255, 214, 120), 255 * a2, 800, spacing=tr)
    sw = prog(t, WIN_T + 0.3, WIN_T + 1.6)
    if 0 < sw < 1:
        light(c, lerp(980, 1620, in_out(sw)), 935, 200, (255, 214, 120), 150 * math.sin(math.pi * sw))
    # end card
    e = smooth(prog(t, END_T, END_T + 0.8))
    if e > 0:
        c.drawPaint(fill((30, 4, 14), 235 * e))
        text(c, "THERE IS A", 960, 400, 40, WHITE, 255 * e, 800, spacing=12)
        text(c, "WAR INSIDE YOU", 960, 500, 96, (255, 214, 120), 255 * e, 800, spacing=lerp(26, 12, out_cubic(prog(t, END_T, END_T + 2))))
        kai(c, 960, 720, 90, t, KAI_TRACK.at(t), (0.0, 0.0), blink_amount(t, (), 3.9, 0.1), a=255 * smooth(prog(t, END_T + 0.6, END_T + 1.2)))


def draw_frame(c, t):
    if t < PATROL_T + 0.6:
        xfade(c, t, PATROL_T - 0.3, 0.9, scene_over, scene_patrol, 0.3)
    else:
        xfade(c, t, OUT_T - 0.3, 1.0, scene_patrol, scene_out, 0.35)
    chapter_title(c, t, 6, "YOU'RE WINNING", (255, 214, 120), 0.2, 2.8)
    fade(c, t, DURATION, 0.5, 1.0)


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (POLLEN_T - 0.4, "slide", 0.5), (POLLEN_T + 0.6, "pop", 0.6), (POLLEN_T + 1.2, "flicker", 0.8),
            (POLLEN_T + 1.25, "blip", 0.9), (AUTO_T - 0.8, "whoosh", 0.6), (AUTO_T + 0.5, "boom", 0.5), (PATROL_T - 0.3, "whoosh_long", 0.7),
            (PATROL_T + 0.4, "bubble", 0.5), (PATROL_T + 1.5, "chime", 0.5), (OUT_T - 0.3, "whoosh_long", 0.7), (WAR_T - 0.6, "pop", 0.8),
            (WAR_T, "swell_soft", 0.7), (WIN_T, "shine", 0.9), (WIN_T + 0.05, "chime", 0.8), (END_T, "swell_soft", 0.9), (END_T + 0.7, "ding", 0.6)]


MUSIC = dict(
    chords=[(0.0, 47, (0, 7, 12, 15, 19)), (POLLEN_T, 46, (0, 7, 12, 15, 18)), (PATROL_T, 50, (0, 7, 12, 16, 19)), (OUT_T, 48, (0, 7, 12, 16, 19)),
            (WIN_T, 50, (0, 7, 12, 16, 19, 24)), (END_T, 48, (0, 7, 12, 16, 21))],
    plucks=[(VO["O1"], POLLEN_T + 1.0), (PATROL_T, DURATION)], bpm=100, rises=[(OUT_T, WIN_T)],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
