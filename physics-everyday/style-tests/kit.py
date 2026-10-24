"""Shared kit for the style tests: canvas size, easing, paints, fonts, text runs, renderer.

  python3 kit.py style_3b1b              # -> out/style_3b1b.mp4
  python3 kit.py style_3b1b --still 2,6  # -> build/style_3b1b/t02.00.png ...
"""
import importlib, math, os, subprocess, sys
from multiprocessing import Pool

import numpy as np
import skia

W, H, FPS = 1920, 1080, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
OUT = os.path.join(HERE, "out")
BUILD = os.path.join(HERE, "build")


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


def out_expo(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def out_back(x, s=1.7):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    t = clamp(t)
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- paints
def col(rgb, a=255):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(clamp(a, 0, 255)))


def fill(rgb, a=255):
    return skia.Paint(AntiAlias=True, Color=col(rgb, a))


def stroke(rgb, w, a=255):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a), Style=skia.Paint.kStroke_Style, StrokeWidth=w)
    p.setStrokeCap(skia.Paint.kRound_Cap)
    p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def blur(p, sigma):
    if sigma > 0.3:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    return p


def polyline(pts, closed=False):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def trim(path, t):
    """First fraction t of a path (for 'draw-on' strokes)."""
    if t >= 1:
        return path
    m = skia.PathMeasure(path, False)
    out = skia.Path()
    while True:
        m.getSegment(0, m.getLength() * clamp(t), out, True)
        if not m.nextContour():
            break
    return out


# ---------------------------------------------------------------- text
_TF, _FC = {}, {}
FACES = {
    "cm": "cmunrm.ttf", "cm_it": "cmunti.ttf", "cm_bf": "cmunbx.ttf",
    "black": "InterDisplay-Black.otf", "bold": "InterDisplay-Bold.otf",
    "semi": "InterDisplay-SemiBold.otf", "medium": "InterDisplay-Medium.otf",
    "sym": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
}


def font(face, size):
    key = (face, round(size, 1))
    if key not in _FC:
        if face not in _TF:
            _TF[face] = skia.Typeface.MakeFromFile(os.path.join(FONTS, FACES[face]))
        f = skia.Font(_TF[face], size)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        f.setSubpixel(True)
        _FC[key] = f
    return _FC[key]


def measure(s, face, size, spacing=0.0):
    f = font(face, size)
    return f.measureText(s) + spacing * max(0, len(s) - 1)


def text(c, s, x, y, face, size, rgb, a=255, align="center", spacing=0.0, paint=None):
    f = font(face, size)
    w = measure(s, face, size, spacing)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    p = paint or fill(rgb, a)
    if not spacing:
        c.drawString(s, x0, y, f, p)
        return w
    for ch in s:
        c.drawString(ch, x0, y, f, p)
        x0 += f.measureText(ch) + spacing
    return w


def runs_width(runs, size):
    return sum(measure(s, face, size * (0.62 if sub else 1)) for s, face, _, sub in runs)


def draw_runs(c, runs, x, y, size, a=255, align="center", reveal=1.0):
    """Mixed-font line: runs = [(text, face, rgb, is_subscript)]. reveal fades chars in left to right."""
    total = runs_width(runs, size)
    cx = x - total / 2 if align == "center" else x
    n = sum(len(r[0]) for r in runs)
    k = 0
    for s, face, rgb, sub in runs:
        sz = size * (0.62 if sub else 1)
        dy = size * 0.22 if sub else 0
        f = font(face, sz)
        for ch in s:
            ca = a * clamp(reveal * (n + 3) - k - 1, 0, 1) if reveal < 1 else a
            if ca > 0:
                c.drawString(ch, cx, y + dy, f, fill(rgb, ca))
            cx += f.measureText(ch)
            k += 1
    return total


# ---------------------------------------------------------------- render
_MOD = None


def _init(name):
    global _MOD
    sys.path.insert(0, HERE)
    _MOD = importlib.import_module(name)


def frame(mod, t):
    s = skia.Surface(W, H)
    mod.draw(s.getCanvas(), t)
    img = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]
    post = getattr(mod, "post", None)
    return np.ascontiguousarray(post(img, t) if post else img)


def _job(i):
    return frame(_MOD, i / FPS).tobytes()


def render(name):
    _init(name)
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"{name}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    n = int(round(_MOD.DURATION * FPS))
    with Pool(os.cpu_count(), initializer=_init, initargs=(name,)) as pool:
        for k, buf in enumerate(pool.imap(_job, range(n), chunksize=4)):
            ff.stdin.write(buf)
            if k % 90 == 0:
                print(f"{name}: {k}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    print(out)


def stills(name, times):
    from PIL import Image
    _init(name)
    d = os.path.join(BUILD, name)
    os.makedirs(d, exist_ok=True)
    for t in times:
        p = os.path.join(d, f"t{t:05.2f}.png")
        Image.fromarray(frame(_MOD, t)).save(p)
        print(p)


if __name__ == "__main__":
    name = sys.argv[1]
    if "--still" in sys.argv:
        stills(name, [float(x) for x in sys.argv[sys.argv.index("--still") + 1].split(",")])
    else:
        render(name)
