"""Part 6: Chapter 5, The Desert That Feeds a Rainforest. The Sahara rewinds to its green past (lakes, hippos);
then a map: dust plumes stream across the Atlantic and rain down on the Amazon, carrying phosphorus.

  python3 render.py part6 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part6"
VO, _end = schedule(PART, first=3.4, gap=1.35)
DURATION = _end + 2.4
TM = Timing(PART, VO)

GREEN_T = TM.word("S1", "it was green") - 0.4
HIPPO_T = TM.word("S1", "hippos") - 0.4
MAP_T = VO["S2"] - 0.5
DUST_T = TM.word("S2", "winds carry") - 0.3
FALL_T = TM.word("S3", "amazon") - 0.3
PHOS_T = TM.word("S3", "phosphorus") - 0.3
FEED_T = TM.word("S3", "biggest desert helps") - 0.4

NIM_TRACK = Track([(0.0, "neutral", 0.0), (GREEN_T, "shocked", 0.2), (GREEN_T + 1.0, "happy", 0.4), (HIPPO_T + 0.5, "laugh", 0.35), (MAP_T + 0.4, "focused", 0.4),
                   (DUST_T + 1.0, "shocked", 0.2), (FALL_T + 0.5, "happy", 0.4), (FEED_T, "cheer", 0.3)])
HIPPO_TRACK = Track([(0.0, "happy", 0.0), (HIPPO_T + 0.6, "laugh", 0.35), (HIPPO_T + 2.0, "wink", 0.25)])
TREE_TRACK = Track([(0.0, "worried", 0.0), (FALL_T + 0.8, "shocked", 0.2), (PHOS_T + 0.6, "laugh", 0.35), (FEED_T, "cheer", 0.3)])


def hippo(c, x, y, s, t, p):
    c.drawOval(skia.Rect.MakeXYWH(x - s, y - s * 0.55, s * 2, s * 1.1), fill((140, 110, 150)))
    c.drawOval(skia.Rect.MakeXYWH(x + s * 0.55, y - s * 0.75, s * 0.9, s * 0.75), fill((156, 124, 166)))
    for dx in (0.75, 1.2):
        c.drawCircle(x + s * dx, y - s * 0.78, s * 0.12, fill((120, 90, 130)))
    c.drawOval(skia.Rect.MakeXYWH(x - s * 1.4, y + s * 0.05, s * 3.0, s * 0.7), fill((60, 140, 205), 240))   # water hides the body
    face_rig(c, x + s * 1.0, y - s * 0.45, s * 0.5, p, (0.4, 0.0), 0.0)


def scene_sahara(c, t):
    g = in_out(prog(t, GREEN_T - 0.6, GREEN_T + 1.6))
    sky(c, t, mood="day")
    if g < 1:
        c.saveLayerAlpha(None, int(255 * (1 - g)))
        dunes(c, t, 760, DESERT, t * 25)
        c.restore()
    if g > 0:
        c.saveLayerAlpha(None, int(255 * g))
        hills(c, 680, (150, 190, 110), t, 50, 0.003, 0.2, 255, t * 10)
        hills(c, 780, (120, 176, 90), t, 40, 0.004, 1.2, 255, t * 20)
        c.drawOval(skia.Rect.MakeXYWH(260, 800, 1100, 170), shaded(linear((0, 800), (0, 970), [SHALLOW, OCEAN])))
        rng = np.random.default_rng(6)
        for k in range(26):    # grass tufts
            x = rng.uniform(0, W)
            y = rng.uniform(800, 1060)
            if 260 < x < 1360 and 800 < y < 970:
                continue
            for j in range(3):
                c.drawLine(x, y, x + (j - 1) * 10, y - 26, stroke((90, 150, 60), 4))
        tree(c, 1500, 820, 220, 2, t)
        tree(c, 1660, 860, 180, 2, t)
        c.restore()
        hippo(c, 800, 870, 110 * smooth(prog(t, HIPPO_T - 0.3, HIPPO_T + 0.4)), t, HIPPO_TRACK.at(t)) if t > HIPPO_T - 0.3 else None
    yrs = smooth(prog(t, GREEN_T - 0.6, GREEN_T)) * (1 - smooth(prog(t, MAP_T - 0.8, MAP_T - 0.3)))
    text(c, "11,000 – 5,000 YEARS AGO", 960, 140, 50, (200, 240, 160), 255 * yrs, 800, spacing=6)
    chip(c, "THE GREEN SAHARA", 960, 220, (200, 240, 160), t, GREEN_T + 0.6, MAP_T - 0.4)

    def path(tt):
        return 1500 + 20 * math.sin(tt * 0.7), 320 + 12 * math.sin(tt * 1.3)
    nim(c, t, NIM_TRACK, path, 110, look=(-0.6, 0.5), rim=(255, 220, 170), sparkle_=float(HIPPO_T + 0.5 < t < HIPPO_T + 2.0))


def scene_map(c, t):
    """Stylised Atlantic map: Africa right, South America left; dust ribbons blow west and settle on the Amazon."""
    c.drawPaint(shaded(linear((0, 0), (0, H), [OCEAN, OCEAN_DEEP])))
    for k in range(14):
        y = 80 + k * 70
        p = skia.Path()
        p.moveTo(0, y)
        for x in range(0, W + 40, 40):
            p.lineTo(x, y + 6 * math.sin(x * 0.01 + t * 0.8 + k))
        c.drawPath(p, stroke(SHALLOW, 2, 50))
    africa = smooth_closed([(1260, 180), (1420, 120), (1700, 130), (1860, 230), (1900, 400), (1830, 560), (1790, 760), (1700, 940), (1600, 1040), (1540, 900), (1520, 720), (1460, 600), (1330, 560), (1230, 470), (1200, 320)])
    sa = smooth_closed([(300, 380), (480, 360), (620, 430), (740, 520), (720, 640), (620, 760), (540, 900), (460, 1060), (420, 1000), (400, 860), (300, 700), (220, 560), (230, 440)])
    c.drawPath(africa, fill((150, 170, 90)))
    c.drawPath(sa, fill((70, 140, 80)))
    sah = smooth_closed([(1270, 210), (1430, 150), (1700, 160), (1840, 260), (1850, 400), (1700, 440), (1460, 450), (1280, 400)])
    c.drawPath(sah, fill(DESERT))
    ama = smooth_closed([(260, 440), (520, 410), (650, 540), (600, 680), (400, 700), (240, 600)])
    c.drawPath(ama, fill((40, 120, 60)))
    text(c, "SAHARA", 1560, 330, 30, (120, 80, 40), 230, 800, spacing=6)
    text(c, "AMAZON", 440, 570, 30, (200, 240, 190), 230, 800, spacing=6)
    text(c, "ATLANTIC OCEAN", 1000, 700, 26, (180, 220, 255), 200, 800, spacing=8)
    # dust: particles flowing along curved ribbons from the Sahara to the Amazon
    k = smooth(prog(t, DUST_T - 0.5, DUST_T + 0.5))
    rng = np.random.default_rng(9)
    for i in range(420):
        ph = rng.random()
        lane = rng.uniform(-1, 1)
        u = (ph + (t - DUST_T) * 0.12) % 1.0
        if t < DUST_T - 0.5:
            continue
        reach = smooth(prog(t, DUST_T - 0.5, FALL_T + 0.5))
        if u > reach:
            continue
        x = lerp(1450, 470, u)
        y = 340 + 130 * math.sin(math.pi * u) * -1 + lane * 60 + 20 * math.sin(u * 9 + i) + 220 * u
        a = 200 * k * math.sin(math.pi * min(1, u / max(reach, 0.01))) if u < 0.97 else 0
        c.drawCircle(x, y, rng.uniform(3, 8), fill((250, 214, 150), a))
    # phosphorus sparks falling on the Amazon
    if t > PHOS_T - 0.3:
        for i in range(24):
            u = ((t - PHOS_T) * 0.7 + i / 24) % 1.0
            x = 300 + (i * 53) % 320
            y = 420 + u * 260
            c.drawCircle(x, y, 6, add((255, 230, 120), 230 * (1 - u)))
    big_number(c, "MILLIONS OF TONNES", 900, 900, 66, (240, 210, 150), t, DUST_T + 0.6, FALL_T, sub="OF DUST EVERY YEAR")
    chip(c, "PHOSPHORUS · FOOD FOR THE RAINFOREST", 440, 780, (255, 230, 120), t, PHOS_T, DURATION)
    tp = TREE_TRACK.at(t)
    tree(c, 400, 760, 120, 0, t, 255, (40, 130, 60))
    face_rig(c, 400, 760 - 120 * 0.62, 34, tp, (0.6, -0.6), 0.0)

    def path(tt):
        return lerp(1650, 980, smooth(prog(tt, DUST_T, FALL_T + 1))) + 20 * math.sin(tt * 0.7), 560 + 12 * math.sin(tt * 1.3)
    nim(c, t, NIM_TRACK, path, 90, look=(-0.8, 0.0), rim=(255, 220, 170), tint=((240, 200, 140), 70 * k))
    chip(c, "THE BIGGEST DESERT FEEDS THE BIGGEST RAINFOREST", 960, 1010, GOLD, t, FEED_T, DURATION)


def draw_frame(c, t):
    xfade(c, t, MAP_T - 0.4, 0.9, scene_sahara, scene_map, 0.25)
    chapter_title(c, t, 5, "THE DESERT THAT FEEDS A RAINFOREST", DESERT, 0.2, 2.8)
    fade(c, t, DURATION, 0.5, 0.7)


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (1.0, "sizzle", 0.3), (GREEN_T - 0.6, "whoosh_long", 0.7), (GREEN_T, "shimmer", 0.8), (GREEN_T + 0.4, "swell_soft", 0.6),
            (HIPPO_T, "bubble", 0.8), (HIPPO_T + 0.6, "pop", 0.6), (MAP_T - 0.4, "whoosh_long", 0.6), (DUST_T, "whoosh_long", 0.8), (DUST_T + 1.0, "rumble", 0.4),
            (FALL_T, "shimmer", 0.6), (PHOS_T, "chime", 0.7), (FEED_T, "ding", 0.8)]


MUSIC = dict(
    chords=[(0.0, 46, (0, 7, 12, 15, 19)), (GREEN_T, 50, (0, 7, 12, 16, 19)), (HIPPO_T, 52, (0, 7, 12, 16, 21)), (MAP_T, 48, (0, 7, 12, 14, 19)),
            (DUST_T, 46, (0, 7, 12, 16, 19)), (FEED_T, 50, (0, 7, 12, 16, 19, 24))],
    plucks=[(VO["S1"], DURATION)], bpm=96, rises=[(GREEN_T - 1.0, GREEN_T), (FALL_T, FEED_T)], drone=38,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
