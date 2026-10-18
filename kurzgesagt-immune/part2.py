"""Part 2: Chapter 1, The Walls. Skin builds up layer by layer and defeats a digging bacterium; a pan along three guard
posts (enzymes, mucus, acid); then one cut, a red flash, and the flood.

  python3 render.py part2 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part2"
VO, _end = schedule(PART, first=3.0, gap=0.8)
DURATION = _end + 1.2
TM = Timing(PART, VO)

BUILD = (VO["W1"] + 0.6, TM.word("W1", "stacked") + 1.4)
DIG_T = TM.word("W1", "very few") - 0.6
POSTS_T = VO["W2"] - 0.5
ENZ_T = TM.word("W2", "tears") - 0.2
MUC_T = TM.word("W2", "mucus") - 0.6
ACID_T = TM.word("W2", "stomach") - 0.6
BACK_T = VO["W3"] - 0.6
CUT_T = TM.word("W3", "one tiny cut") + 0.1
FLOOD_T = TM.word("W3", "thousands") - 0.3

DIGGER = Track([(0.0, "smug", 0.0), (DIG_T + 0.3, "determined", 0.3), (DIG_T + 1.6, "focused", 0.4), (DIG_T + 2.6, "shocked", 0.2),
                (DIG_T + 3.2, "worried", 0.5)])
KAI_TRACK = Track([(0.0, "neutral", 0.0), (DIG_T + 2.7, "smug", 0.4), (DIG_T + 3.6, "wink", 0.25), (DIG_T + 4.4, "smug", 0.3),
                   (CUT_T, "shocked", 0.2), (CUT_T + 1.0, "angry", 0.4)])
ENZ_VICTIM = Track([(0.0, "smug", 0.0), (ENZ_T + 0.6, "shocked", 0.2), (ENZ_T + 1.6, "hurt", 0.4)])
MUC_VICTIMS = [Track([(0.0, "smug", 0.0), (MUC_T + 0.9 + 0.3 * i, "shocked", 0.2), (MUC_T + 1.8 + 0.3 * i, "worried", 0.5)]) for i in range(3)]
ACID_VICTIM = Track([(0.0, "smug", 0.0), (ACID_T + 0.9, "shocked", 0.2), (ACID_T + 1.6, "hurt", 0.4)])
FLOOD = Track([(0.0, "smug", 0.0), (FLOOD_T, "laugh", 0.3)])


def skin_scene(c, t, cut=0.0):
    """Skin cross-section with outside air above and tissue below; Kai patrols underneath."""
    k = in_out(prog(t, 0.0, BUILD[1]))
    cam_y = lerp(-120, 40, k) if t < BACK_T else 40
    zoom = lerp(1.15, 1.0, k) if t < BACK_T else lerp(1.0, 1.08, in_out(prog(t, BACK_T, DURATION)))
    shake_ = 14 * math.exp(-max(0.0, t - CUT_T) * 5) * (t > CUT_T)
    c.save()
    c.translate(W / 2 + shake_ * math.sin(t * 60), H / 2 + shake_ * math.cos(t * 51))
    c.scale(zoom, zoom)
    c.translate(-W / 2, -H / 2 - cam_y)
    outside_world(c, t, 520)
    body_world_band = 520
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(-200, body_world_band, W + 400, 900))
    c.translate(0, 160)
    body_world(c, t)
    c.restore()
    # skin builds upward layer by layer
    b = smooth(prog(t, *BUILD)) if t < BACK_T else 1.0
    top = 520 + 320 * (1 - b)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(-200, top, W + 400, 1000))
    skin_wall(c, -200, 520, W + 400, 320, t, cut=cut, cut_x=980)
    c.restore()
    if 0 < b < 1:
        c.drawLine(-200, top, W + 200, top, stroke((255, 240, 230), 4, 200))
    # tissue edge under the skin
    c.drawRect(skia.Rect.MakeXYWH(-200, 836, W + 400, 10), fill((120, 30, 60), 200))
    # Kai under the skin
    kx = 1500 + 30 * math.sin(t * 0.6)
    kai(c, kx, 960, 100, t, KAI_TRACK.at(t), (-0.6, -0.8) if t < CUT_T else (-0.9, -0.5),
        blink_amount(t, KAI_TRACK.change_times(), 3.8, 0.5))
    c.restore()
    return cam_y, zoom


def build_scene(c, t):
    cam_y, zoom = skin_scene(c, t)
    # the digger: lands, digs with frantic wiggle, bonks off
    if DIG_T - 1.0 < t < POSTS_T + 0.5:
        u = t - DIG_T
        x = 760
        if u < 0:
            y = lerp(200, 470, out_cubic(1 + u))
        elif u < 2.6:
            y = 470 + 6 * math.sin(t * 40) + 10 * smooth(prog(u, 0, 2.4))
        else:
            v = prog(u, 2.6, 3.6)
            x = 760 - 240 * v
            y = 480 - 260 * math.sin(math.pi * 0.7 * v)
        sx = W / 2 + (x - W / 2) * zoom
        sy = H / 2 + (y - H / 2 - cam_y) * zoom
        ang = 90 + (0 if u < 2.6 else 400 * prog(u, 2.6, 3.6))
        bacterium(c, sx, sy, 56 * zoom, t, ang, mood=DIGGER.at(t), wiggle=5 if 0 < u < 2.6 else 1)
        if 0 < u < 2.6:
            for j in range(6):   # dust flecks from the dig
                ph = (t * 3 + j / 6) % 1.0
                c.drawCircle(sx + (j - 2.5) * 14 * ph * 3, sy + 50 * zoom - 60 * ph, 5, fill((250, 210, 190), 220 * (1 - ph)))
        if 2.6 < u < 3.0:
            sparkle(c, sx, H / 2 + (520 - H / 2 - cam_y) * zoom, 70, 255, (255, 250, 230))
    chip(c, "SKIN · LAYER UPON LAYER OF DEAD CELLS", 960, 110, (255, 230, 220), t, BUILD[0] + 1.0, POSTS_T)


def posts_scene(c, t):
    """Pan across three guard posts: tears & saliva (enzymes), mucus (sticky trap), stomach (acid)."""
    x0 = -W * 0.9 * (in_out(prog(t, MUC_T - 1.1, MUC_T + 0.1)) + in_out(prog(t, ACID_T - 1.0, ACID_T + 0.1)))
    body_world(c, t, Cam(-x0 * 0.3, 0, 1.0))
    c.save()
    c.translate(x0, 0)
    # post 1: an eye-shaped tear drop with enzymes chewing a bacterium
    cx = W / 2
    drop = skia.Path()
    drop.moveTo(cx, 160)
    drop.cubicTo(cx + 380, 520, cx + 300, 900, cx, 900)
    drop.cubicTo(cx - 300, 900, cx - 380, 520, cx, 160)
    c.drawPath(drop, shaded(linear((cx, 160), (cx, 900), [(120, 180, 235), (70, 120, 200)])))
    c.drawPath(drop, stroke((220, 240, 255), 6, 200))
    c.drawOval(skia.Rect.MakeXYWH(cx - 170, 330, 90, 200), fill(WHITE, 40))
    vic = ENZ_VICTIM.at(t)
    bx, by = cx, 600 + 10 * math.sin(t * 2)
    bite = smooth(prog(t, ENZ_T + 0.6, ENZ_T + 3.0))
    bacterium(c, bx, by, 66, t, 15, mood=vic, wiggle=3 if t > ENZ_T + 0.6 else 1, a=255 * (1 - 0.5 * bite))
    for k in range(5):
        an = k / 5 * 6.28 + t * 0.6
        d = lerp(260, 120, smooth(prog(t, ENZ_T + 0.2, ENZ_T + 1.0)))
        ex, ey = bx + math.cos(an) * d * 1.2, by + math.sin(an) * d * 0.8
        mo = 0.5 + 0.5 * abs(math.sin(t * 8 + k))
        ang = math.degrees(math.atan2(by - ey, bx - ex))
        p = skia.Path()
        p.moveTo(ex, ey)
        p.arcTo(skia.Rect.MakeXYWH(ex - 28, ey - 28, 56, 56), ang + 35 * mo, 360 - 70 * mo, False)
        p.close()
        c.drawPath(p, fill((255, 250, 240)))
        c.drawPath(p, stroke((60, 110, 170), 3))
        c.drawCircle(ex + math.cos(math.radians(ang - 90)) * 12, ey + math.sin(math.radians(ang - 90)) * 12, 4, fill((30, 40, 70)))
    text(c, "TEARS & SALIVA", cx, 980, 34, WHITE, 255, 800, spacing=6)
    text(c, "ENZYMES BREAK BACTERIA APART", cx, 1022, 18, (210, 230, 255), 230, 800, spacing=3)
    # post 2: mucus strands trapping bacteria
    cx = W / 2 + W * 0.9
    for k in range(8):
        p = skia.Path()
        yy = 220 + k * 85
        p.moveTo(cx - 520, yy)
        p.cubicTo(cx - 200, yy - 60 + 30 * math.sin(t + k), cx + 160, yy + 70 + 30 * math.cos(t * 0.8 + k), cx + 520, yy)
        c.drawPath(p, blur(stroke((170, 230, 110), 40, 120), 6))
        c.drawPath(p, stroke((210, 255, 160), 8, 150))
    for i, (sx, sy) in enumerate([(cx - 260, 380), (cx + 40, 560), (cx + 280, 420)]):
        stick = smooth(prog(t, MUC_T + 0.9 + 0.3 * i, MUC_T + 1.6 + 0.3 * i))
        x = lerp(sx - 500, sx, out_cubic(prog(t, MUC_T - 0.2 + 0.3 * i, MUC_T + 0.9 + 0.3 * i)))
        y = sy + 30 * math.sin(t * 2 + i) * (1 - stick) + 4 * math.sin(t * 30 + i) * stick
        bacterium(c, x, y, 50, t, 10 + 20 * i, mood=MUC_VICTIMS[i].at(t), wiggle=6 if stick > 0.5 else 1.2)
        if stick > 0:
            c.drawCircle(x, y, 80, fill((190, 250, 140), 60 * stick))
    text(c, "MUCUS", cx, 980, 34, WHITE, 255, 800, spacing=6)
    text(c, "A STICKY TRAP", cx, 1022, 18, (220, 255, 190), 230, 800, spacing=3)
    # post 3: stomach acid pool with bubbles
    cx = W / 2 + W * 1.8
    pool_y = 560
    c.drawRect(skia.Rect.MakeXYWH(cx - 700, pool_y, 1400, 400), shaded(linear((0, pool_y), (0, pool_y + 400), [ACID, darken(ACID, 0.6)])))
    for k in range(18):
        bx_ = cx - 650 + (k * 79) % 1300
        by_ = pool_y + 380 - ((t * 70 + k * 41) % 380)
        c.drawCircle(bx_, by_, 6 + k % 5, stroke(lighten(ACID, 0.4), 3, 200))
    c.drawLine(cx - 700, pool_y, cx + 700, pool_y, stroke(lighten(ACID, 0.5), 5, 220))
    fall = out_cubic(prog(t, ACID_T, ACID_T + 0.9))
    fizz = smooth(prog(t, ACID_T + 1.0, ACID_T + 3.5))
    bacterium(c, cx, lerp(200, pool_y + 10, fall), 58, t, 20 + 40 * fizz, mood=ACID_VICTIM.at(t), wiggle=4 if fall > 0.9 else 1, a=255 * (1 - 0.8 * fizz))
    if t > ACID_T + 0.9:
        for k in range(8):
            u = ((t - ACID_T) * 1.4 + k / 8) % 1.0
            c.drawCircle(cx + (k - 3.5) * 22, pool_y - 80 * u, 7 * (1 - u) + 2, stroke(lighten(ACID, 0.5), 3, 220 * (1 - u)))
    text(c, "pH ≈ 2", cx + 420, pool_y + 200, 48, darken(ACID, 0.75), 230, 800)
    text(c, "STOMACH ACID", cx, 980, 34, WHITE, 255, 800, spacing=6)
    text(c, "KILLS MANY MICROBES YOU SWALLOW", cx, 1022, 18, (230, 255, 200), 230, 800, spacing=3)
    c.restore()
    near_blur(c, [(-80, 1040, 230), (1990, 60, 200)], t, (190, 70, 100), 0.8)


def cut_scene(c, t):
    cut = out_expo(prog(t, CUT_T, CUT_T + 0.35))
    cam_y, zoom = skin_scene(c, t, cut)
    if t > CUT_T:      # bacteria flood in through the wound
        rng = np.random.default_rng(12)
        p = FLOOD.at(t)
        for i in range(34):
            delay = rng.uniform(0, 1.6)
            u = prog(t, FLOOD_T + delay - 0.6, FLOOD_T + delay + 1.6)
            if u <= 0:
                continue
            ox = 980 + rng.uniform(-260, 260)
            x = lerp(ox, 980 + rng.uniform(-120, 120), u) + rng.uniform(-300, 300) * max(0, u - 0.6)
            y = lerp(250, 760 + rng.uniform(0, 200), in_cubic(u))
            sx = W / 2 + (x - W / 2) * zoom
            sy = H / 2 + (y - H / 2 - cam_y) * zoom
            bacterium(c, sx, sy, 30 * zoom, t + i, 80 + rng.uniform(-30, 30), mood=p, face_on=i % 2 == 0)
        fl = math.exp(-(t - CUT_T) * 4)
        c.drawPaint(fill((255, 40, 60), 150 * fl))
    chip(c, "ONE TINY CUT", 960, 110, (255, 140, 140), t, CUT_T + 0.2, DURATION)


def draw_frame(c, t):
    if t < POSTS_T + 1.0:
        xfade(c, t, POSTS_T, 1.0, build_scene, posts_scene, 0.25)
    else:
        xfade(c, t, BACK_T, 0.9, posts_scene, cut_scene, 0.25)
    chapter_title(c, t, 1, "THE WALLS", (250, 205, 180), 0.2, 2.8)
    if t > DURATION - 0.3:     # hard cut to black
        c.drawPaint(fill((10, 0, 4)))


def sfx_events():
    ev = [(0.2, "swell_soft", 0.6), (BUILD[0], "slide", 0.5)] + [(BUILD[0] + 0.4 * i, "click", 0.4) for i in range(8)]
    ev += [(DIG_T - 0.3, "whoosh_soft", 0.5), (DIG_T, "ticks", 0.6), (DIG_T + 1.2, "ticks", 0.6), (DIG_T + 2.6, "pop", 0.9), (DIG_T + 2.62, "tink", 0.6),
           (DIG_T + 3.6, "ding", 0.6)]
    ev += [(POSTS_T, "whoosh_long", 0.6), (ENZ_T + 0.6, "bubble", 0.6)] + [(ENZ_T + 0.8 + 0.25 * i, "click", 0.4) for i in range(8)]
    ev += [(MUC_T + 0.2, "slide", 0.5)] + [(MUC_T + 0.9 + 0.3 * i, "bubble", 0.7) for i in range(3)]
    ev += [(ACID_T + 0.9, "pop", 0.6), (ACID_T + 1.0, "sizzle", 0.9), (BACK_T, "whoosh_long", 0.6), (CUT_T - 0.6, "riser", 0.6),
           (CUT_T, "boom", 1.0), (CUT_T + 0.02, "flicker", 0.8), (FLOOD_T, "rumble", 1.0), (FLOOD_T + 0.6, "rumble", 0.9)]
    return ev


MUSIC = dict(
    chords=[(0.0, 48, (0, 7, 12, 16, 19)), (DIG_T, 50, (0, 7, 12, 16, 19)), (POSTS_T, 53, (0, 7, 12, 16, 19)), (ACID_T, 51, (0, 7, 12, 15, 19)),
            (BACK_T, 48, (0, 7, 12, 16, 19)), (CUT_T, 42, (0, 6, 12, 15, 18))],
    plucks=[(VO["W1"], CUT_T)], bpm=100, rises=[(BUILD[0], BUILD[1]), (CUT_T - 1.5, CUT_T)],
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
