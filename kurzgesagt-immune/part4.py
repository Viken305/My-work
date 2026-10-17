"""Part 4: Chapter 3, The Messenger. The battle goes badly; a dendritic cell grabs a piece of the enemy, rides the lymph
to a lymph node (body map zoom), and searches the crowd of T cells for the one whose lock fits.

  python3 render.py part4 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part4"
VO, _end = schedule(PART, first=3.0, gap=0.8)
DURATION = _end + 1.8
TM = Timing(PART, VO)

DC_T = TM.word("M1", "dendritic") - 0.6
GRAB_T = VO["M2"] - 0.3
TRAVEL_T = TM.word("M2", "travels") - 0.2
MAP_T = TM.word("M2", "lymphatic") - 0.2
NODE_T = TM.word("M2", "lymph node") - 0.1
SEARCH_T = VO["M3"] - 0.3
MATCH_T = TM.word("M3", "exact enemy") - 0.4

_rng = np.random.default_rng(4)
SWARM = [(float(x), float(y), float(p)) for x, y, p in zip(_rng.uniform(-850, 850, 26), _rng.uniform(-420, 380, 26), _rng.uniform(0, 6.28, 26))]
DC_TRACK = Track([(0.0, "neutral", 0.0), (DC_T + 0.5, "determined", 0.35), (GRAB_T + 0.3, "happy", 0.35), (TRAVEL_T + 0.5, "focused", 0.4),
                  (SEARCH_T, "determined", 0.35), (MATCH_T, "cheer", 0.3)])
TIRED = [Track([(0.0, "determined", 0.0), (1.4 + 0.5 * i, "worried", 0.5), (3.6 + 0.4 * i, "exhausted", 0.7), (DC_T + 0.8, "shocked", 0.25),
                (DC_T + 1.8, "happy", 0.4)]) for i in range(3)]
LOCKS = [(255, 120, 120), (120, 255, 160), (160, 160, 255), (255, 200, 90), (255, 120, 255), GERM, (120, 220, 255)]
MATCH_I = 5
T_TRACKS = []
for i in range(len(LOCKS)):
    visit = SEARCH_T + 0.35 * i
    if i == MATCH_I:
        T_TRACKS.append(Track([(0.0, "neutral", 0.0), (visit, "focused", 0.3), (MATCH_T, "shocked", 0.2), (MATCH_T + 0.8, "cheer", 0.35)]))
    else:
        T_TRACKS.append(Track([(0.0, "neutral", 0.0), (visit, "focused", 0.3), (visit + 0.45, "worried", 0.35), (visit + 1.4, "neutral", 0.5)]))


def battle(c, t):
    k = in_out(prog(t, 0.0, GRAB_T + 1.0))
    cam = Cam(lerp(-100, 120, k), 0, lerp(0.95, 1.12, k))
    body_world(c, t, cam)
    cam.push(c, 1.0)
    for i, (x, y, ph) in enumerate(SWARM):        # bacteria multiplying everywhere
        g = smooth(prog(t, 0.3 + i * 0.12, 0.9 + i * 0.12))
        if g <= 0:
            continue
        bx, by = x + 30 * math.sin(t * 0.8 + ph), y + 20 * math.cos(t * 0.7 + ph)
        if i < 12 and t > 2.0 + 0.3 * i:          # some split in two
            dk = prog(t, 2.0 + 0.3 * i, 2.8 + 0.3 * i)
            divide(c, bx, by, 32 * g, t, dk, lambda cc, xx, yy, rr: bacterium(cc, xx, yy, rr, t, math.degrees(ph), mood=pose("laugh" if dk > 0.5 else "smug")), axis=ph)
        else:
            bacterium(c, bx, by, 32 * g, t, math.degrees(ph), mood=pose("smug"))
    for i, (x, y) in enumerate([(-640, 260), (-260, 330)]):
        neutrophil(c, x, y + 8 * math.sin(t + i), 66, t, TIRED[i].at(t), (0.4, -0.2), seed=i)
    eater(c, 620, 260, 140, t, TIRED[2].at(t), (-0.4, -0.2), blink_amount(t, TIRED[2].change_times(), 4.0, 1.0),
          belly=((-0.45, 0.0, 0.13, 0.3), (0.45, 0.0, 0.12, 0.5), (-0.5, -0.15, 0.11, 0.2), (0.5, -0.15, 0.11, 0.4)))
    # the dendritic cell drifts in, a tendril grabs a fragment
    if t > DC_T - 0.4:
        u = out_cubic(prog(t, DC_T - 0.4, DC_T + 1.6))
        dx, dy = lerp(-1200, -40, u), -40 + 12 * math.sin(t * 1.2)
        carry = GERM if t > GRAB_T + 0.2 else None
        if GRAB_T - 0.7 < t < GRAB_T + 0.3:       # reach out to the nearest bacterium
            bx, by = SWARM[3][0] + 30 * math.sin(t * 0.8 + SWARM[3][2]), SWARM[3][1]
            r = smooth(prog(t, GRAB_T - 0.7, GRAB_T - 0.2)) * (1 - smooth(prog(t, GRAB_T, GRAB_T + 0.3)))
            c.drawLine(dx + 60, dy - 40, lerp(dx + 60, bx, r), lerp(dy - 40, by, r), stroke(DENDRI, 18))
            c.drawCircle(lerp(dx + 60, bx, r), lerp(dy - 40, by, r), 14, fill(lighten(DENDRI, 0.3)))
        dendritic(c, dx, dy, 96, t, DC_TRACK.at(t), (0.6, -0.3), carry=carry, rim=(255, 180, 220))
        if GRAB_T < t < GRAB_T + 0.6:
            sparkle(c, dx + 90, dy - 90, 70 * (1 - prog(t, GRAB_T, GRAB_T + 0.6)), 255, GERM)
    cam.pop(c)
    near_blur(c, [(-80, 1040, 230), (1990, 60, 200)], t, (190, 70, 100), 0.8)
    chip(c, "TOO MANY · TOO CLEVER", 960, 110, (255, 160, 150), t, 1.6, DC_T)
    chip(c, "DENDRITIC CELL · THE MESSENGER", 960, 110, DENDRI, t, DC_T + 0.4, MAP_T)


def body_map_scene(c, t):
    """Zoom out to the whole body: the route through the lymph network lights up to the nearest node."""
    c.drawPaint(shaded(radial((W / 2, H / 2), W, [(40, 50, 100), (10, 12, 34)])))
    draw_texture(c, tex_lymph(), 960, 540, 1.8, t * 2, 90, skia.BlendMode.kPlus)
    k = in_out(prog(t, MAP_T - 0.6, NODE_T + 0.4))
    zoom = lerp(2.4, 1.0, smooth(prog(t, MAP_T - 0.6, MAP_T + 1.2))) * lerp(1.0, 3.2, in_cubic(prog(t, NODE_T, NODE_T + 1.2)))
    hx, hy = 960, 1000
    nx, ny = hx - 110 * 900 / 600, hy - 390 * 900 / 600        # armpit node (body_map coords)
    fx, fy = lerp(hx - 60 * 1.5, nx, smooth(prog(t, NODE_T - 0.4, NODE_T + 1.0))), lerp(hy - 250 * 1.5, ny, smooth(prog(t, NODE_T - 0.4, NODE_T + 1.0)))
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(zoom, zoom)
    c.translate(-fx, -fy)
    body_map(c, hx, hy, 900, t)
    # wound on the forearm + route up to the armpit node
    wx, wy = hx - 140 * 1.5, hy - 200 * 1.5
    c.drawCircle(wx, wy, 12, fill((255, 80, 90)))
    light(c, wx, wy, 60, (255, 80, 90), 160)
    route = skia.Path()
    route.moveTo(wx, wy)
    route.cubicTo(wx - 20, wy - 120, nx - 30, ny + 110, nx, ny)
    meas = skia.PathMeasure(route, False)
    L = meas.getLength()
    prg = smooth(prog(t, MAP_T, NODE_T + 0.2))
    seg = skia.Path()
    meas.getSegment(0, L * prg, seg, True)
    c.drawPath(seg, stroke((120, 255, 230), 7, 230))
    pos = meas.getPosTan(L * prg)
    if pos:
        (px, py), _ = pos
        light(c, px, py, 50, DENDRI, 220)
        c.drawCircle(px, py, 10, fill(lighten(DENDRI, 0.4)))
    ng = smooth(prog(t, NODE_T - 0.3, NODE_T + 0.3))
    light(c, nx, ny, 90, (120, 255, 230), 220 * ng)
    c.restore()
    chip(c, "LYMPHATIC SYSTEM", 960, 110, (150, 255, 240), t, MAP_T + 0.2, NODE_T + 0.2)
    chip(c, "LYMPH NODE · THE BASE", 960, 110, (150, 255, 240), t, NODE_T + 0.3, SEARCH_T + 0.6)


def node_scene(c, t):
    """Inside the lymph node: a row of helper T cells; the dendritic cell shows the fragment down the line."""
    k = in_out(prog(t, NODE_T + 0.6, DURATION))
    cam = Cam(lerp(-200, 220, k), 0, lerp(1.1, 1.0, k))
    lymph_world(c, t, cam)
    cam.push(c, 1.0)
    for i, kc in enumerate(LOCKS):
        x = -780 + i * 240
        y = 60 + 70 * (i % 2) + 10 * math.sin(t * 1.3 + i)
        p = T_TRACKS[i].at(t)
        if i == MATCH_I and t > MATCH_T:
            g = smooth(prog(t, MATCH_T, MATCH_T + 0.4))
            light(c, x, y, 320, GERM, 255 * g, core=0)
            light(c, x, y, 160, (220, 255, 160), 200 * g)
            c.drawCircle(x, y, 110 + 30 * prog(t, MATCH_T, MATCH_T + 0.6), stroke((210, 255, 120), 10, 255 * (1 - 0.5 * prog(t, MATCH_T, MATCH_T + 0.6))))
        dc_x = lerp(-900, -780 + min(MATCH_I, max(0.0, (t - SEARCH_T) / 0.35)) * 240, smooth(prog(t, NODE_T + 0.5, SEARCH_T)))
        look = (clamp((dc_x - x) / 300, -1, 1), 0.3)
        hop = 0.6 * math.sin(math.pi * prog(t, MATCH_T + 0.8, MATCH_T + 1.2)) if i == MATCH_I else 0
        t_cell(c, x, y - 40 * hop, 80, t + i, "helper", p, look, key=kc, seed=i, rim=(170, 210, 255))
    dc_x = lerp(-900, -780 + min(MATCH_I, max(0.0, (t - SEARCH_T) / 0.35)) * 240, smooth(prog(t, NODE_T + 0.5, SEARCH_T)))
    dendritic(c, dc_x, -300 + 10 * math.sin(t * 1.4), 86, t, DC_TRACK.at(t), (0.0, 0.7), carry=GERM, rim=(170, 210, 255))
    if t > MATCH_T:   # lock clicks: fragment flies into the matching receptor
        u = out_back(prog(t, MATCH_T - 0.1, MATCH_T + 0.5), 1.4)
        x = -780 + MATCH_I * 240
        fx, fy = lerp(dc_x + 82, x, u), lerp(-300 - 82, 0, u)
        c.drawPath(blob_path(fx, fy, [22 * (1 + 0.2 * math.sin(k_ * 2.1)) for k_ in range(7)]), fill(GERM))
    cam.pop(c)
    near_blur(c, [(60, 60, 200), (1880, 1020, 220)], t, (90, 120, 200), 0.8)
    chip(c, "MATCH!", 960, 980, GERM, t, MATCH_T + 0.2, DURATION)
    chip(c, "SEARCHING FOR THE ONE THAT FITS", 960, 110, (190, 220, 255), t, SEARCH_T + 0.2, DURATION)


def draw_frame(c, t):
    if t < MAP_T + 0.4:
        xfade(c, t, MAP_T - 0.6, 1.0, battle, body_map_scene, 0.3)
    else:
        xfade(c, t, NODE_T + 0.6, 0.9, body_map_scene, node_scene, 0.5)
    chapter_title(c, t, 3, "THE MESSENGER", DENDRI, 0.2, 2.8)
    fade(c, t, DURATION, 0.5, 0.7)


def sfx_events():
    ev = [(0.2, "swell_soft", 0.6)] + [(2.0 + 0.3 * i, "bubble", 0.4) for i in range(0, 12, 2)]
    ev += [(DC_T - 0.4, "slide", 0.6), (DC_T + 0.5, "chime", 0.6), (GRAB_T - 0.6, "whoosh_soft", 0.5), (GRAB_T, "pop", 0.9), (GRAB_T + 0.05, "shine", 0.6)]
    ev += [(MAP_T - 0.6, "whoosh_long", 0.8), (MAP_T, "riser", 0.6), (NODE_T, "ding", 0.8), (NODE_T + 0.6, "whoosh_long", 0.7)]
    ev += [(SEARCH_T + 0.35 * i, "blip", 0.5) for i in range(MATCH_I)] + [(MATCH_T, "click", 1.0), (MATCH_T + 0.05, "shine", 0.9), (MATCH_T + 0.8, "chime", 0.7)]
    return ev


MUSIC = dict(
    chords=[(0.0, 45, (0, 7, 12, 15, 19)), (DC_T, 48, (0, 7, 12, 16, 19)), (MAP_T, 50, (0, 7, 12, 14, 19)), (NODE_T, 52, (0, 7, 12, 16, 19)),
            (SEARCH_T, 50, (0, 7, 12, 15, 19)), (MATCH_T, 48, (0, 7, 12, 16, 19, 24))],
    plucks=[(VO["M1"], DURATION)], bpm=100, rises=[(MAP_T, NODE_T), (SEARCH_T, MATCH_T)],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
