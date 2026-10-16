"""Cinematic reel renderer: animated gold text *behind* the subject.

Layers (back to front): blurred/graded background -> animated metallic text -> subject cut-out.
Camera: slow push-in with different zoom rates per layer (parallax), then bloom, gold dust,
vignette and film grain. Run:  python3 render.py A|B [--still T1,T2,...] [--scale 0.5]
"""
import math, os, subprocess, sys
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

cv2.setNumThreads(1)
W, H, FPS = 1080, 1920, 30
SW, SH = 1800, 2400            # working resolution of every source layer
HERE = os.path.dirname(os.path.abspath(__file__))
SERIF = os.path.join(HERE, "fonts/CormorantGaramond.ttf")
SANS = os.path.join(HERE, "fonts/Montserrat.ttf")

GOLD_TOP, GOLD_MID, GOLD_BOT = (252, 243, 220), (228, 192, 122), (146, 106, 50)
CREAM = (246, 236, 214)

SETS = {
    "A": dict(
        caption="THE LIME & NOIR EDIT", D=5.4, OV=0.6, grade="A",
        beats=[
            dict(name="A1_wall_side", word="RADIANT", zf=1.10, drift=-1, tw=0.94, bgdark=0.58),
            dict(name="A2_backdrop_look", word="WONDER", zf=1.14, drift=1, tw=0.93, erode=3, ty=-0.015, bgdark=0.50, tint=(1.0, 0.82, 0.88)),
            dict(name="A3_backdrop_smile", word="WOMAN", zf=1.14, drift=-1, tw=0.90, erode=3, ty=-0.03, bgdark=0.50, tint=(1.0, 0.82, 0.88)),
            dict(name="A4_wall_down", word="GRACE", zf=1.10, drift=1, tw=0.90, ty=-0.035, bgdark=0.58),
        ]),
    "B": dict(
        caption="THE MOONLIT EDIT", D=7.4, OV=0.6, grade="B", cap_frac=0.045,
        beats=[
            dict(name="B1_garden_leaves", word="ETHEREAL", zf=1.10, drift=-1, tw=0.94, above=0.15, bgdark=0.80),
            dict(name="B2_closeup", word="TIMELESS", zf=0.80, drift=1, tw=0.94, bgdark=0.80, zpush=0.07, padtop=700, bottom=True, above=0.12),
            dict(name="B3_garden_phone", word="ENCHANTED", zf=1.10, drift=-1, tw=0.94, above=0.15, bgdark=0.80),
        ]),
}


# ---------------------------------------------------------------- helpers
def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def out_expo(x):
    x = min(max(x, 0.0), 1.0)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def out_cubic(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def grade_lut(kind):
    x = np.linspace(0, 1, 256)
    c = x + 0.55 * (x * x * (3 - 2 * x) - x)        # gentle S-curve
    if kind == "A":                                  # rich, warm highlights / cool shadows
        r = c * 1.02 + 0.00
        g = c * 1.00
        b = c * 0.95 + 0.020 * (1 - c)
    else:                                            # golden night, lifted film blacks
        r = c * 1.05 + 0.012
        g = c * 1.00 + 0.006
        b = c * 0.89 + 0.004
    lut = np.stack([r, g, b], -1)
    return (np.clip(lut, 0, 1) * 255).astype(np.uint8)


def apply_lut(img, lut):
    return np.stack([cv2.LUT(img[..., i], lut[:, i]) for i in range(3)], -1)


def make_bg(img_s, m_s):
    """Blurred background with the subject removed (normalised-convolution fill)."""
    hard = (m_s > 0.15).astype(np.uint8)
    dil = cv2.dilate(hard, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (45, 45)))
    valid = cv2.GaussianBlur((1 - dil).astype(np.float32), (0, 0), 4)
    imgf = img_s.astype(np.float32)
    res = None
    for s in (120, 40, 12):
        num = cv2.GaussianBlur(imgf * valid[..., None], (0, 0), s)
        den = cv2.GaussianBlur(valid, (0, 0), s)[..., None]
        est = num / np.maximum(den, 1e-4)
        w = np.clip(den / 0.25, 0, 1)
        res = est if res is None else est * w + res * (1 - w)
    soft = cv2.GaussianBlur(imgf, (0, 0), 9)
    bg = soft * valid[..., None] + res * (1 - valid[..., None])
    return bg


# ---------------------------------------------------------------- text
class TextLayer:
    def __init__(self, word, caption, tw_frac, cap_frac=0.075, tr0=0.26, tr1=0.05):
        self.word, self.caption, self.n = word, caption, len(word)
        self.cap_frac = cap_frac
        self.tr0, self.tr1 = tr0, tr1
        f200 = ImageFont.truetype(SERIF, 200)
        f200.set_variation_by_axes([700])
        adv200 = sum(f200.getlength(c) for c in word) / 200
        self.size = int(tw_frac * W / (adv200 + (self.n - 1) * tr1))
        f = ImageFont.truetype(SERIF, self.size)
        f.set_variation_by_axes([700])
        self.pad = int(self.size * 0.2)
        self.base = int(self.size * 1.2)
        self.glyphs = []
        for ch in word:
            adv = f.getlength(ch)
            im = Image.new("L", (int(adv) + 2 * self.pad, int(self.size * 1.6)), 0)
            ImageDraw.Draw(im).text((self.pad, self.base), ch, font=f, fill=255, anchor="ls")
            self.glyphs.append((np.asarray(im, np.float32) / 255, adv))
        # caption
        cf = ImageFont.truetype(SANS, 30)
        cf.set_variation_by_axes([300])
        tr = 0.5 * 30
        cw = int(sum(cf.getlength(c) + tr for c in caption))
        im = Image.new("L", (cw + 20, 60), 0)
        d = ImageDraw.Draw(im)
        x = 10
        for ch in caption:
            d.text((x, 40), ch, font=cf, fill=255, anchor="ls")
            x += cf.getlength(ch) + tr
        self.cap = np.asarray(im, np.float32) / 255

    def place(self, cy):
        """Band geometry (canvas rows that hold the word) for a text centre line cy."""
        self.cy = cy
        self.baseline = int(cy + 0.33 * self.size)
        self.y0 = max(0, int(self.baseline - 0.95 * self.size))
        self.y1 = min(H, int(self.baseline + 0.95 * self.size))
        self.bh = self.y1 - self.y0
        yy = np.arange(self.bh, dtype=np.float32)[:, None] + self.y0
        g = np.clip((yy - (self.baseline - 0.66 * self.size)) / (0.66 * self.size), 0, 1)
        top, mid, bot = (np.array(c, np.float32) for c in (GOLD_TOP, GOLD_MID, GOLD_BOT))
        g3 = g[..., None]
        self.grad = np.where(g3 < 0.5, top + (mid - top) * (g3 / 0.5), mid + (bot - mid) * ((g3 - 0.5) / 0.5))
        xx = np.arange(W, dtype=np.float32)[None, :]
        self.diag = xx + (yy - self.y0) * 0.45

    def render(self, bgw, t, tout):
        """Composite the animated text onto bgw (float32 HxWx3) in place. t = seconds since text start,
        tout = 0..1 exit progress."""
        if t <= 0:
            return
        size = self.size
        q = out_cubic(t / 2.8)
        tr = (self.tr0 + (self.tr1 - self.tr0) * q + 0.012 * min(t / 6, 1)) * size
        total = sum(a for _, a in self.glyphs) + tr * (self.n - 1)
        x = W / 2 - total / 2
        drift = -14 * min(t / 6, 1)                      # slow rise during hold
        mask = np.zeros((self.bh, W), np.float32)
        for i, (gl, adv) in enumerate(self.glyphs):
            p = out_expo((t - i * 0.075) / 1.5)
            a = min(1.0, p * 1.4) * (1 - smooth(tout))
            if a > 0.003:
                patch = gl
                sig = (1 - p) * 9
                if sig > 0.6:
                    patch = cv2.GaussianBlur(gl, (0, 0), sig)
                oy = (1 - p) * 0.16 * size + smooth(tout) * -0.05 * size
                M = np.float32([[1, 0, x - self.pad], [0, 1, self.baseline - self.base - self.y0 + drift + oy]])
                w = cv2.warpAffine(patch, M, (W, self.bh), flags=cv2.INTER_LINEAR)
                np.maximum(mask, w * a, out=mask)
            x += adv + tr
        band = bgw[self.y0:self.y1]
        # soft shadow + glow (quarter res)
        small = cv2.resize(mask, (W // 4, self.bh // 4), interpolation=cv2.INTER_AREA)
        sh = cv2.resize(cv2.GaussianBlur(small, (0, 0), 4), (W, self.bh))
        sh = np.roll(sh, 10, axis=0)
        gl_ = cv2.resize(cv2.GaussianBlur(small, (0, 0), 14), (W, self.bh))
        band *= (1 - 0.45 * sh)[..., None]
        band += gl_[..., None] * np.float32((255, 196, 120)) * 0.20
        # metallic fill with one shine sweep
        pos = -200 + (t - 1.3) / 1.8 * (W + 700)
        shine = np.exp(-((self.diag - pos) ** 2) / (2 * 70.0 ** 2)) * (0.65 if 1.3 < t < 3.3 else 0.0)
        col = self.grad * (1 + 0.55 * shine[..., None]) + 60 * shine[..., None]
        col = np.clip(col, 0, 255)
        band *= (1 - mask)[..., None]
        band += col * mask[..., None]

    def render_caption(self, img, t, tout):
        """Small caption + hairlines, drawn in FRONT of everything near the top of the frame."""
        band = img
        ca = out_cubic((t - 1.6) / 1.2) * (1 - smooth(tout))
        if ca > 0.003:
            cap = self.cap
            ch, cw = cap.shape
            cx0 = int(W / 2 - cw / 2)
            cyy = int(self.cap_frac * H)
            if 0 <= cyy and cyy + ch < H:
                reg = band[cyy:cyy + ch, cx0:cx0 + cw]
                m = cap[..., None] * ca * 0.92
                reg *= (1 - m)
                reg += np.float32(CREAM) * m
            ln = int(out_expo((t - 1.4) / 1.6) * 0.22 * W)
            ly = cyy + 40 - 8
            if ln > 2 and 0 <= ly < H - 2:
                for x0, x1 in ((cx0 - 24 - ln, cx0 - 24), (cx0 + cw + 24, cx0 + cw + 24 + ln)):
                    seg = band[ly:ly + 2, max(x0, 0):min(x1, W)]
                    seg *= (1 - 0.7 * ca)
                    seg += np.float32(GOLD_MID) * 0.7 * ca


# ---------------------------------------------------------------- beat
class Beat:
    def __init__(self, cfg, setcfg, caption):
        self.cfg, self.D, self.OV = cfg, setcfg["D"], setcfg["OV"]
        lut = grade_lut(setcfg["grade"])
        src = cv2.cvtColor(cv2.imread(os.path.join(HERE, "source", self._find(cfg["name"]))), cv2.COLOR_BGR2RGB)
        interp = cv2.INTER_AREA if src.shape[1] > SW else cv2.INTER_CUBIC
        img = cv2.resize(src, (SW, SH), interpolation=interp)
        m = cv2.imread(os.path.join(HERE, "build", cfg["name"] + "_mask.png"), 0)
        m = cv2.resize(m, (SW, SH), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        m = cv2.erode(m, np.ones((3, 3), np.uint8), iterations=cfg.get("erode", 1))
        m = cv2.GaussianBlur(m, (0, 0), 1.4)
        m = np.clip((m - 0.10) / 0.80, 0, 1)
        # edge colour decontamination: pull interior colours outward over the fringe
        core = cv2.erode((m > 0.98).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=3).astype(np.float32)
        imf = img.astype(np.float32)
        num = cv2.GaussianBlur(imf * core[..., None], (0, 0), 7)
        den = cv2.GaussianBlur(core, (0, 0), 7)[..., None]
        clean = num / np.maximum(den, 1e-3)
        cw = cv2.GaussianBlur(core, (0, 0), 2.0)[..., None]
        img_fg = np.where(den > 0.02, imf * cw + clean * (1 - cw), imf)
        # subject bbox
        ys, xs = np.where(m > 0.5)
        self.top, self.bot = ys.min() / SH, ys.max() / SH
        self.left, self.right = xs.min() / SW, xs.max() / SW
        self.cxn = (self.left + self.right) / 2
        # background
        half = lambda a: cv2.resize(a, (SW // 2, SH // 2), interpolation=cv2.INTER_AREA)
        bg = make_bg(half(img), half(m))
        bg = cv2.resize(bg, (SW, SH), interpolation=cv2.INTER_CUBIC)
        gray = bg.mean(-1, keepdims=True)
        bg = gray + (bg - gray) * 0.85
        bg = bg * cfg["bgdark"] * np.float32(cfg.get("tint", (1, 1, 1)))
        self.bg = apply_lut(np.clip(bg, 0, 255).astype(np.uint8), lut)
        fg = apply_lut(np.clip(img_fg, 0, 255).astype(np.uint8), lut).astype(np.float32) * m[..., None]
        self.fg = np.clip(fg, 0, 255).astype(np.uint8)
        self.alpha = (m * 255).astype(np.uint8)
        self.padtop = cfg.get("padtop", 0)
        if self.padtop:
            P = self.padtop
            self.bg = np.pad(self.bg, ((P, 0), (0, 0), (0, 0)), mode="edge")
            self.bg[:P + 150] = cv2.GaussianBlur(self.bg[:P + 150], (0, 0), 35)
            self.fg = np.pad(self.fg, ((P, 0), (0, 0), (0, 0)))
            self.alpha = np.pad(self.alpha, ((P, 0), (0, 0)))
        self.SHe = SH + self.padtop
        # text, anchored to where the head sits mid-move
        bh = self.bot - self.top
        self.text = TextLayer(cfg["word"], caption, cfg["tw"], setcfg.get("cap_frac", 0.075))
        if "above" in cfg:   # sit the word on top of the head (head tucks into the lower part of the letters)
            cy = self._project(self.top * SH + self.padtop, 0.5)[1] - cfg["above"] * self.text.size
        else:
            cy = self._project((self.top + 0.07 * bh) * SH + self.padtop, 0.5)[1] + cfg.get("ty", 0.0) * H
        self.text.place(cy)

    @staticmethod
    def _find(name):
        for f in os.listdir(os.path.join(HERE, "source")):
            if f.startswith(name + "."):
                return f
        raise FileNotFoundError(name)

    # camera ---------------------------------------------------------
    def _cam(self, u, layer):
        e = 0.65 * u + 0.35 * smooth(u)
        zpush = self.cfg.get("zpush", 0.12)
        z = self.cfg["zf"] * (1 + (zpush if layer == "fg" else zpush * 0.45) * e)
        s = z * H / SH
        hw, hh = W / 2 / s, H / 2 / s
        head_y = (self.top + 0.12 * (self.bot - self.top)) * SH + self.padtop
        cx = self.cxn * SW + self.cfg["drift"] * (e - 0.5) * 70 * (1 if layer == "fg" else 0.5)
        if self.cfg.get("bottom"):
            cy = self.SHe - hh
        else:
            cy = self.SHe / 2 + (head_y - self.SHe / 2) * (0.55 * e if layer == "fg" else 0.25 * e)
        cx = min(max(cx, hw), SW - hw)
        cy = min(max(cy, hh), self.SHe - hh) if hh <= self.SHe - hh else self.SHe - hh
        return s, cx, cy

    def _project(self, y_src, u):
        s, _, cy = self._cam(u, "fg")
        return W / 2, H / 2 + s * (y_src - cy)

    def frame(self, t):
        u = t / self.D
        out_t = (t - (self.D - self.OV)) / self.OV
        s, cx, cy = self._cam(u, "bg")
        M = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
        bgw = cv2.warpAffine(self.bg, M, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32)
        t0 = 0.55
        self.text.render(bgw, t - t0, out_t if out_t > 0 else 0)
        s, cx, cy = self._cam(u, "fg")
        M = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
        fg = cv2.warpAffine(self.fg, M, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32)
        a = cv2.warpAffine(self.alpha, M, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32) / 255
        out = bgw * (1 - a[..., None]) + fg
        self.text.render_caption(out, t - t0, out_t if out_t > 0 else 0)
        return out


# ---------------------------------------------------------------- finishing
_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)
_R = np.sqrt(((_XX - W / 2) / (W / 2)) ** 2 + ((_YY - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.42 * np.clip(_R - 0.35, 0, 1) ** 1.6)[..., None].astype(np.float32)
rng0 = np.random.RandomState(7)
PART = [dict(x=rng0.uniform(0, W), y=rng0.uniform(0, H), v=rng0.uniform(25, 70), sw=rng0.uniform(8, 30),
             ph=rng0.uniform(0, 6.28), r=rng0.uniform(2, 6), tw=rng0.uniform(0.6, 1.6)) for _ in range(50)]


def finish(img, T, total, seed):
    # bloom
    low = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    bright = np.clip(low - 150, 0, None)
    bloom = cv2.resize(cv2.GaussianBlur(bright, (0, 0), 6), (W, H), interpolation=cv2.INTER_LINEAR)
    img = img + bloom * 0.55
    # gold dust
    layer = np.zeros((H // 4, W // 4), np.float32)
    for p in PART:
        y = (p["y"] - p["v"] * T) % H
        x = p["x"] + p["sw"] * math.sin(T * 0.7 + p["ph"])
        a = 0.5 + 0.5 * math.sin(T * p["tw"] * 2 + p["ph"])
        cv2.circle(layer, (int(x / 4), int(y / 4)), max(1, int(p["r"] / 4 + 0.5)), float(a), -1, cv2.LINE_AA)
    layer = cv2.resize(cv2.GaussianBlur(layer, (0, 0), 1.3), (W, H), interpolation=cv2.INTER_LINEAR)
    img = img + layer[..., None] * np.float32((255, 205, 130)) * 0.55
    img *= VIG
    # grain
    g = np.random.RandomState(seed).randn(H // 2, W // 2).astype(np.float32) * 5.5
    img += cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    # fades
    f = min(1.0, smooth(T / 0.7), smooth((total - T) / 0.9))
    img *= f
    return np.clip(img, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- timeline
BEATS, STARTS, TOTAL = [], [], 0.0


def build(setkey):
    global BEATS, STARTS, TOTAL
    sc = SETS[setkey]
    BEATS = [Beat(b, sc, sc["caption"]) for b in sc["beats"]]
    step = sc["D"] - sc["OV"]
    STARTS = [i * step for i in range(len(BEATS))]
    TOTAL = STARTS[-1] + sc["D"]
    return sc


def render_frame(i, scale=1.0):
    T = i / FPS
    sc = None
    img = None
    for k, (b, s) in enumerate(zip(BEATS, STARTS)):
        t = T - s
        if 0 <= t < b.D:
            f = b.frame(t)
            if img is None:
                img = f
                first_t = t
            else:  # incoming beat k blends over outgoing k-1
                e = smooth(t / b.OV)
                flash = math.sin(math.pi * min(max(t / b.OV, 0), 1)) ** 2
                img = img * (1 - e) + f * e + flash * 0.30 * np.float32((255, 214, 150)) * 0.5
    out = finish(img, T, TOTAL, 1000 + i)
    if scale != 1.0:
        out = cv2.resize(out, (int(W * scale), int(H * scale)), interpolation=cv2.INTER_AREA)
    return out


def _work(args):
    return render_frame(*args).tobytes()


if __name__ == "__main__":
    key = sys.argv[1]
    scale = float(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 1.0
    build(key)
    print(f"set {key}: {len(BEATS)} beats, {TOTAL:.1f}s", flush=True)
    if "--still" in sys.argv:
        for ts in sys.argv[sys.argv.index("--still") + 1].split(","):
            i = int(float(ts) * FPS)
            im = render_frame(i, scale)
            p = os.path.join(HERE, "build", f"still_{key}_{ts}.png")
            Image.fromarray(im).save(p)
            print(p, flush=True)
        sys.exit(0)
    n = int(TOTAL * FPS)
    ow, oh = int(W * scale), int(H * scale)
    outp = os.path.join(HERE, "out", f"reel_{key}.mp4")
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", outp], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, buf in enumerate(pool.imap(_work, [(i, scale) for i in range(n)], chunksize=3)):
            ff.stdin.write(buf)
            if k % 60 == 0:
                print(f"{k}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("wrote", outp)
