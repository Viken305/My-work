"""Vector illustrations used as the video's "AI pictures" (no real model output), and the simulated generation steps.

  image(name)       -> float32 RGB array (size x size): "hero", "seed_a".."seed_c", "paris", "noguide",
                       "train_dog", "train_mountain", "train_lighthouse"
  step(k, n=30)     -> the hero as the model's guess at step k: very blurry colour blobs first, detail last
  attn(word)        -> 16x16 map of where the picture "belongs" to a word (from the drawing's own layers)
  embedding(word)   -> 768 illustrative numbers for a word (deterministic, not a real model's)
  MEANING           -> hand-placed 2D meaning-map positions
"""
import hashlib
import math

import cv2
import numpy as np
import skia

S = 512
_CACHE = {}

TOKENS = ["a", "cat", "wearing", "an", "astronaut", "suit", "riding", "a", "bicycle", "on", "the", "moon", ",",
          "digital", "art"]
PROMPT = "a cat wearing an astronaut suit riding a bicycle on the moon, digital art"

# cat colour schemes: fur, darker stripes, eye colour
CATS = {
    "orange": ((236, 140, 58), (186, 92, 34), (120, 200, 90)),
    "grey": ((150, 154, 166), (96, 100, 112), (240, 190, 60)),
    "black": ((44, 42, 50), (22, 20, 26), (250, 210, 70)),
    "cream": ((240, 222, 196), (200, 160, 120), (90, 160, 230)),
}

MEANING = {   # word: (x, y) in 0..1, clustered by meaning
    "cat": (0.18, 0.30), "kitten": (0.25, 0.22), "tiger": (0.12, 0.42), "dog": (0.32, 0.38), "puppy": (0.38, 0.30),
    "moon": (0.78, 0.22), "planet": (0.86, 0.32), "mars": (0.72, 0.36), "star": (0.88, 0.14), "astronaut": (0.64, 0.18),
    "rocket": (0.70, 0.08), "bicycle": (0.62, 0.72), "car": (0.72, 0.80), "train": (0.56, 0.84),
    "paris": (0.22, 0.78), "london": (0.14, 0.70), "city": (0.30, 0.86),
    "pizza": (0.44, 0.56), "apple": (0.50, 0.48), "bread": (0.40, 0.64),
}


# ---------------------------------------------------------------- tiny helpers
def C(rgb, a=255):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(a))


def P(rgb, a=255, stroke=0.0, blur=0.0):
    p = skia.Paint(AntiAlias=True, Color=C(rgb, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def lin(c, rect, cols, vertical=True):
    x0, y0, x1, y1 = rect
    pts = [(x0, y0), (x0, y1)] if vertical else [(x0, y0), (x1, y0)]
    c.drawRect(skia.Rect.MakeLTRB(*rect), skia.Paint(Shader=skia.GradientShader.MakeLinear(pts, [C(k) for k in cols])))


def rad(c, x, y, r, cols, stops=None):
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial((x, y), r, [C(*k) if len(k) == 2 else C(k) for k in cols], stops)))


def path(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def stars(c, seed, n=70, ymax=330):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y, r = rng.uniform(0, S), rng.uniform(0, ymax), rng.uniform(0.6, 1.8)
        c.drawCircle(x, y, r, P((255, 250, 235), rng.uniform(120, 255)))


# ---------------------------------------------------------------- scene pieces
def moon_ground(c, seed=0, tint=(150, 150, 160)):
    g = skia.Path()
    g.moveTo(0, 420)
    g.cubicTo(140, 395, 330, 430, S, 405)
    g.lineTo(S, S)
    g.lineTo(0, S)
    g.close()
    c.drawPath(g, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, 400), (0, S)], [C(tint), C(tuple(v * 0.45 for v in tint))])))
    rng = np.random.default_rng(seed + 5)
    for _ in range(9):
        x, y, w = rng.uniform(10, 500), rng.uniform(440, 500), rng.uniform(18, 60)
        r = skia.Rect.MakeXYWH(x - w / 2, y - w * 0.14, w, w * 0.28)
        c.drawOval(r, P(tuple(v * 0.55 for v in tint)))
        c.drawOval(r.makeOffset(0, 2.5), P(tuple(min(255, v * 1.15) for v in tint), 140, stroke=1.5))


def earth(c, x, y, r):
    rad(c, x, y, r * 1.5, [((90, 160, 255), 90), ((90, 160, 255), 0)])
    rad(c, x - r * 0.3, y - r * 0.3, r * 1.3, [(110, 180, 255), (30, 80, 190), (10, 30, 90)], [0, 0.6, 1])
    c.save()
    disc = skia.Path()
    disc.addCircle(x, y, r)
    c.clipPath(disc, doAntiAlias=True)
    for dx, dy, w, h in ((-0.4, -0.2, 0.7, 0.5), (0.3, 0.25, 0.5, 0.6), (0.1, -0.55, 0.4, 0.25)):
        c.drawOval(skia.Rect.MakeXYWH(x + dx * r - w * r / 2, y + dy * r - h * r / 2, w * r, h * r), P((90, 170, 90), 230))
    c.drawCircle(x + r * 0.5, y + r * 0.5, r, P((0, 0, 20), 120, blur=r * 0.3))
    c.restore()


def bicycle(c, x, y, frame=(230, 70, 70)):
    """x, y = rear hub. Returns key points (seat, bars, crank, front hub)."""
    rear, front = (x, y), (x + 180, y)
    crank, seat, bars = (x + 80, y), (x + 60, y - 90), (x + 160, y - 100)
    for hx, hy in (rear, front):
        c.drawCircle(hx, hy, 62, P((30, 30, 36), 255, stroke=9))
        c.drawCircle(hx, hy, 62, P((90, 90, 100), 255, stroke=2.5))
        for k in range(12):
            a = k * math.pi / 6
            c.drawLine(hx, hy, hx + 58 * math.cos(a), hy + 58 * math.sin(a), P((200, 200, 210), 150, stroke=1))
        c.drawCircle(hx, hy, 6, P((200, 200, 210)))
    fr = P(frame, 255, stroke=7)
    c.drawPath(path([rear, seat, crank], True), fr)
    c.drawLine(*seat, *(x + 150, y - 85), fr)
    c.drawLine(*crank, *(x + 150, y - 85), fr)
    c.drawLine(*(x + 150, y - 85), *front, fr)
    c.drawLine(*(x + 150, y - 85), *bars, fr)
    c.drawPath(path([bars, (bars[0] + 22, bars[1] - 8), (bars[0] + 28, bars[1] + 6)], False), P((40, 40, 46), 255, stroke=6))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(seat[0] - 22, seat[1] - 10, 44, 12), 6, 6), P((40, 40, 46)))
    c.drawCircle(*crank, 13, P((60, 60, 66)))
    return seat, bars, crank, front


def cat_astronaut(c, x, y, cat="orange", frame=(230, 70, 70), suit=(236, 238, 244)):
    """A cat in a spacesuit on a bicycle; x, y = rear hub."""
    fur, dark, eye = CATS[cat]
    shade = tuple(v * 0.72 for v in suit)
    seat, bars, crank, front = bicycle(c, x, y, frame)
    # tail poking out of the suit
    t = skia.Path()
    t.moveTo(seat[0] - 10, seat[1] - 30)
    t.cubicTo(seat[0] - 70, seat[1] - 20, seat[0] - 80, seat[1] - 100, seat[0] - 50, seat[1] - 120)
    c.drawPath(t, P(fur, 255, stroke=16))
    c.drawPath(t, P(dark, 160, stroke=5))
    # backpack
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(seat[0] - 30, seat[1] - 150, 46, 90), 10, 10), P(shade))
    c.drawRect(skia.Rect.MakeXYWH(seat[0] - 22, seat[1] - 130, 30, 8), P((230, 70, 70)))
    # far leg (darker), torso, near leg
    knee = (crank[0] + 40, crank[1] - 70)
    c.drawPath(path([(seat[0] + 10, seat[1] - 10), knee, (crank[0] - 16, crank[1] + 14)], False), P(shade, 255, stroke=26))
    c.drawPath(path([(seat[0] + 10, seat[1] - 10), knee, (crank[0] + 18, crank[1] - 12)], False), P(suit, 255, stroke=28))
    c.drawPath(path([(seat[0] + 10, seat[1] - 10), knee, (crank[0] + 18, crank[1] - 12)], False), P(shade, 120, stroke=3))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(crank[0] + 6, crank[1] - 24, 34, 18), 8, 8), P((70, 70, 80)))
    c.save()
    c.rotate(-18, seat[0] + 30, seat[1] - 70)
    body = skia.Rect.MakeXYWH(seat[0] - 15, seat[1] - 140, 92, 125)
    c.drawRRect(skia.RRect.MakeRectXY(body, 40, 40), P(suit))
    c.drawRRect(skia.RRect.MakeRectXY(body, 40, 40), P(shade, 120, stroke=3))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(seat[0] + 18, seat[1] - 95, 36, 24), 5, 5), P((70, 110, 200)))
    for k, cc in enumerate(((230, 70, 70), (255, 200, 60), (90, 200, 120))):
        c.drawCircle(seat[0] + 26 + k * 10, seat[1] - 83, 3.5, P(cc))
    c.restore()
    # arm to the handlebar
    sh = (seat[0] + 55, seat[1] - 120)
    c.drawPath(path([sh, (sh[0] + 45, sh[1] + 30), (bars[0] + 6, bars[1] + 2)], False), P(suit, 255, stroke=22))
    c.drawCircle(bars[0] + 8, bars[1] + 2, 12, P((230, 70, 70)))
    # helmet with the cat's face inside
    hx, hy, hr = seat[0] + 70, seat[1] - 175, 58
    c.drawCircle(hx, hy, hr + 8, P(suit))
    c.drawCircle(hx, hy, hr + 8, P(shade, 140, stroke=3))
    rad(c, hx - 10, hy - 10, hr * 1.2, [(40, 60, 110), (14, 20, 44)])
    c.save()
    disc = skia.Path()
    disc.addCircle(hx, hy, hr)
    c.clipPath(disc, doAntiAlias=True)
    fx, fy = hx + 6, hy + 8
    for s in (-1, 1):   # ears
        c.drawPath(path([(fx + s * 12, fy - 26), (fx + s * 36, fy - 56), (fx + s * 38, fy - 14)]), P(fur))
        c.drawPath(path([(fx + s * 17, fy - 27), (fx + s * 33, fy - 47), (fx + s * 34, fy - 20)]), P((240, 150, 160)))
    c.drawOval(skia.Rect.MakeXYWH(fx - 42, fy - 36, 84, 72), P(fur))
    for k in range(3):   # forehead stripes
        c.drawLine(fx - 10 + k * 10, fy - 34, fx - 8 + k * 8, fy - 20, P(dark, 255, stroke=4))
    c.drawOval(skia.Rect.MakeXYWH(fx - 22, fy + 2, 44, 30), P(tuple(min(255, v + 40) for v in fur)))
    for s in (-1, 1):
        ex = fx + s * 17
        c.drawOval(skia.Rect.MakeXYWH(ex - 10, fy - 14, 20, 22), P(eye))
        c.drawOval(skia.Rect.MakeXYWH(ex - 3.5, fy - 12, 7, 18), P((10, 10, 14)))
        c.drawCircle(ex + 4, fy - 8, 3, P((255, 255, 255)))
        for k in (-1, 0, 1):
            c.drawLine(fx + s * 16, fy + 14 + k * 4, fx + s * 50, fy + 10 + k * 9, P((255, 255, 255), 200, stroke=1.4))
    c.drawPath(path([(fx - 6, fy + 6), (fx + 6, fy + 6), (fx, fy + 13)]), P((240, 120, 140)))
    c.drawPath(path([(fx - 10, fy + 16), (fx - 5, fy + 21), (fx, fy + 15), (fx + 5, fy + 21), (fx + 10, fy + 16)], False), P((60, 30, 30), 255, stroke=2))
    c.restore()
    # glass reflection
    arc = skia.Path()
    arc.addArc(skia.Rect.MakeXYWH(hx - hr + 10, hy - hr + 10, (hr - 10) * 2, (hr - 10) * 2), 200, 60)
    c.drawPath(arc, P((255, 255, 255), 170, stroke=6))
    c.drawCircle(hx + 28, hy - 30, 5, P((255, 255, 255), 200))


def scene_moon(c, cat="orange", earth_at=(400, 110), mirror=False, frame=(230, 70, 70), seed=0, sky=((8, 12, 34), (34, 26, 70))):
    lin(c, (0, 0, S, S), [sky[0], sky[1]])
    stars(c, seed)
    earth(c, *earth_at, 46)
    moon_ground(c, seed)
    c.save()
    if mirror:
        c.translate(S, 0)
        c.scale(-1, 1)
    c.drawOval(skia.Rect.MakeXYWH(120, 440, 330, 26), P((0, 0, 0), 110, blur=8))
    cat_astronaut(c, 140, 410, cat, frame)
    c.restore()


def scene_paris(c):
    lin(c, (0, 0, S, S), [(255, 170, 120), (250, 210, 170)])
    rad(c, 120, 170, 70, [(255, 240, 200), ((255, 220, 160), 0)])
    # Eiffel tower silhouette
    tw = (90, 70, 80)
    c.drawPath(path([(370, 40), (385, 40), (420, 300), (450, 420), (420, 420), (378, 320), (336, 420), (306, 420),
                     (336, 300)]), P(tw))
    for yy, w in ((150, 26), (250, 50)):
        c.drawRect(skia.Rect.MakeXYWH(377 - w, yy, w * 2, 8), P(tw))
    for k in range(6):   # rooftops
        x = k * 90 - 20
        c.drawRect(skia.Rect.MakeXYWH(x, 330 - (k % 3) * 18, 80, 120), P((150, 120, 130)))
        c.drawPath(path([(x - 5, 330 - (k % 3) * 18), (x + 40, 300 - (k % 3) * 18), (x + 85, 330 - (k % 3) * 18)]), P((110, 100, 120)))
    lin(c, (0, 420, S, S), [(120, 110, 120), (70, 64, 72)])
    for k in range(8):
        c.drawLine(k * 70, 470, k * 70 + 40, 470, P((220, 210, 200), 160, stroke=4))
    c.drawOval(skia.Rect.MakeXYWH(120, 440, 330, 26), P((0, 0, 0), 110, blur=8))
    cat_astronaut(c, 140, 410, "orange")


def scene_dog(c):
    lin(c, (0, 0, S, S), [(150, 205, 250), (215, 238, 255)])
    for x, y, r in ((90, 90, 30), (130, 80, 40), (170, 95, 28), (380, 120, 26), (410, 110, 34)):
        c.drawCircle(x, y, r, P((255, 255, 255), 230))
    lin(c, (0, 330, S, S), [(110, 190, 90), (60, 130, 60)])
    gold, dk = (226, 170, 90), (180, 120, 60)
    c.drawOval(skia.Rect.MakeXYWH(140, 270, 240, 120), P(gold))
    for x in (170, 210, 320, 350):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, 360, 26, 90), 12, 12), P(gold if x % 20 else dk))
    t = skia.Path()
    t.moveTo(150, 300)
    t.cubicTo(100, 280, 90, 230, 110, 210)
    c.drawPath(t, P(gold, 255, stroke=22))
    c.drawOval(skia.Rect.MakeXYWH(320, 180, 120, 110), P(gold))
    c.drawOval(skia.Rect.MakeXYWH(395, 230, 70, 50), P((240, 200, 130)))
    c.drawCircle(460, 245, 11, P((40, 30, 30)))
    c.drawOval(skia.Rect.MakeXYWH(318, 195, 40, 90), P(dk))
    c.drawCircle(385, 220, 8, P((40, 30, 30)))
    c.drawPath(path([(430, 275), (445, 300), (455, 280)]), P((230, 100, 110)))


def scene_mountain(c):
    lin(c, (0, 0, S, S), [(60, 50, 120), (250, 150, 120), (255, 210, 150)])
    rad(c, 256, 330, 90, [(255, 240, 200), ((255, 200, 140), 0)])
    for pts, col_ in (([(-40, 400), (150, 170), (330, 400)], (90, 80, 120)), ([(160, 420), (330, 120), (560, 420)], (70, 64, 100))):
        c.drawPath(path(pts), P(col_))
        (x0, y0), (x1, y1), (x2, y2) = pts
        k = 0.3
        c.drawPath(path([(x1 - (x1 - x0) * k, y1 + (y0 - y1) * k), (x1, y1), (x1 + (x2 - x1) * k, y1 + (y2 - y1) * k),
                         (x1 + 10, y1 + (y2 - y1) * k * 0.7), (x1 - 15, y1 + (y0 - y1) * k * 0.9)]), P((250, 245, 250)))
    lin(c, (0, 400, S, S), [(40, 50, 70), (20, 24, 40)])


def scene_lighthouse(c):
    lin(c, (0, 0, S, S), [(20, 30, 70), (80, 90, 150)])
    stars(c, 3, 40, 250)
    beam = path([(300, 140), (S, 60), (S, 220)])
    c.drawPath(beam, P((255, 240, 180), 90, blur=10))
    lin(c, (0, 380, S, S), [(30, 60, 110), (10, 20, 50)])
    for k in range(8):
        c.drawLine(20 + k * 60, 410 + (k % 3) * 25, 60 + k * 60, 410 + (k % 3) * 25, P((200, 220, 255), 120, stroke=3))
    c.drawPath(path([(170, 400), (200, 380), (360, 385), (400, 410)]), P((50, 50, 60)))
    c.drawPath(path([(250, 380), (270, 160), (330, 160), (350, 380)]), P((240, 240, 240)))
    for y0 in (200, 270, 340):
        c.drawPath(path([(268 - (y0 - 160) * 0.09, y0), (332 + (y0 - 160) * 0.09, y0),
                         (332 + (y0 + 30 - 160) * 0.09, y0 + 30), (268 - (y0 + 30 - 160) * 0.09, y0 + 30)]), P((220, 60, 60)))
    c.drawRect(skia.Rect.MakeXYWH(275, 125, 50, 35), P((255, 230, 150)))
    c.drawCircle(300, 142, 40, P((255, 230, 150), 140, blur=16))
    c.drawPath(path([(265, 125), (300, 95), (335, 125)]), P((60, 60, 70)))


SCENES = {
    "hero": lambda c: scene_moon(c, "orange", (445, 80)),
    "seed_a": lambda c: scene_moon(c, "black", (110, 100), True, (60, 140, 230), 1, ((6, 20, 30), (20, 60, 80))),
    "seed_b": lambda c: scene_moon(c, "grey", (420, 140), False, (250, 190, 50), 2, ((20, 8, 30), (70, 30, 80))),
    "seed_c": lambda c: scene_moon(c, "cream", (130, 120), True, (90, 200, 120), 3, ((4, 4, 12), (30, 30, 50))),
    "paris": scene_paris,
    "train_dog": scene_dog,
    "train_mountain": scene_mountain,
    "train_lighthouse": scene_lighthouse,
}


def _draw(fn, size=S):
    s = skia.Surface(size, size)
    c = s.getCanvas()
    c.clear(C((0, 0, 0)))
    c.scale(size / S, size / S)
    fn(c)
    return s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)


def image(name, size=S):
    key = (name, size)
    if key not in _CACHE:
        if name == "noguide":   # "without the prompt": vague colour blobs with no subject
            base = image("hero", size)
            rng = np.random.default_rng(9)
            blobs = cv2.GaussianBlur(rng.normal(0, 1, (8, 8, 3)).astype(np.float32), (0, 0), 1)
            blobs = cv2.resize(blobs, (size, size), interpolation=cv2.INTER_CUBIC)
            mush = cv2.GaussianBlur(base, (0, 0), size / 18) * 0.6 + 60 + blobs * 30
            _CACHE[key] = np.clip(mush, 0, 255)
        else:
            _CACHE[key] = _draw(SCENES[name], size)
    return _CACHE[key]


def step(k, n=30, name="hero", size=S):
    """The model's guess of the final picture at step k (0..n-1): blur shrinks as steps go on, a little noise left."""
    u = (k + 1) / n
    img = image(name, size)
    sig = size * 0.09 * (1 - u) ** 2.2
    out = cv2.GaussianBlur(img, (0, 0), sig) if sig > 0.3 else img.copy()
    rng = np.random.default_rng(k)
    noise = rng.normal(0, 1, out.shape).astype(np.float32) * 40 * (1 - u) ** 1.5
    return np.clip(out + noise, 0, 255)


def _mask(fn):
    m = _draw(fn).mean(2)
    return (m > 0).astype(np.float32)


def attn(word):
    """16x16 'where this word lives' map, taken from the drawing's own layers."""
    if word == "cat":
        m = _mask(lambda c: cat_astronaut(c, 140, 410))
        m *= 0.4
        face = np.zeros((S, S), np.float32)
        cv2.circle(face, (276, 255), 50, 1.0, -1)   # strongest on the face
        m = np.maximum(m, face)
    elif word == "moon":
        m = _mask(lambda c: moon_ground(c))
    else:
        m = np.ones((S, S), np.float32) * 0.2
    m = cv2.resize(cv2.GaussianBlur(m, (0, 0), 14), (16, 16), interpolation=cv2.INTER_AREA)
    return m


def embedding(word, n=768):
    """Illustrative numbers for a word (stable per word). Not taken from a real model."""
    seed = int(hashlib.md5(word.encode()).hexdigest()[:8], 16)
    return np.random.default_rng(seed).normal(0, 1, n).astype(np.float32)


if __name__ == "__main__":
    import os
    from PIL import Image
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "art")
    os.makedirs(out, exist_ok=True)
    for n in list(SCENES) + ["noguide"]:
        Image.fromarray(image(n).astype(np.uint8)).save(os.path.join(out, f"{n}.png"))
    for k in (2, 8, 16, 29):
        Image.fromarray(step(k).astype(np.uint8)).save(os.path.join(out, f"step_{k}.png"))
    print(out)
