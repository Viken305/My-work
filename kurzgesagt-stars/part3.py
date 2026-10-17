"""Part 3: Chapter 2, Birth. Cloud, shockwave, collapse, protostar, fusion, ignition.

  python3 render.py part3 [--still 3,10]
"""
from story import *  # noqa: F401,F403

PART = "part3"
VO, _end = schedule(PART, first=2.8, gap=0.75, extra={"B4": 0.3})
DURATION = _end + 2.0
TM = Timing(PART, VO)

SHOCK = (TM.word("B2", "shockwave") - 0.6, TM.word("B2", "shockwave") + 2.6)
GRAV_T = TM.word("B2", "gravity") - 0.3
CLUMP = (VO["B3"] - 0.6, VO["B3"])
CORE = (VO["B4"] - 0.5, VO["B4"])
FUSE_T = TM.word("B4", "smashing") - 0.2
IGNITE = TM.word("B4", "a star is born") - 0.4
_rng = np.random.default_rng(23)
SPECKS = [(float(a), float(r)) for a, r in zip(_rng.uniform(0, 6.283, 90), _rng.uniform(120, 520, 90))]
KNOTS = [(320, -60, 1.0), (-260, 160, 0.7), (60, 260, 0.6)]


def cloud(c, t):
    cam = drift_cam(t, 0, CLUMP[1], -260, 260, 40, -40, 1.0, 1.18)
    cam = shake(cam, t, SHOCK[0] + 0.9, 4, 1.5)
    c.drawPaint(shaded(radial((W / 2, H / 2), W * 0.85, [DEEP, VOID])))
    SF.draw(c, t, cam)
    cam.push(c, 0.35)
    draw_texture(c, tex_teal(), 500, -260, 1.6, t * 0.4, 150, skia.BlendMode.kPlus)
    cam.pop(c)
    cam.push(c, 0.55)
    draw_texture(c, tex_cloud(), -200, 80, 1.8, -t * 0.5, 210, skia.BlendMode.kPlus)
    cam.pop(c)
    cam.push(c, 0.75)
    draw_texture(c, tex_cloud(14), 300, -40, 1.3, t * 0.7, 190, skia.BlendMode.kPlus)
    draw_texture(c, tex_dust(), -400, 300, 1.2, t * 0.3, 120)
    # shock front sweeping through
    sk = prog(t, *SHOCK)
    if 0 < sk < 1:
        x = lerp(-1500, 1500, in_out(sk))
        for w, al, bl in ((140, 60, 60), (40, 150, 18), (10, 230, 3)):
            p = skia.Paint(AntiAlias=True, Color=col(AMBER, al * math.sin(math.pi * sk)), Style=skia.Paint.kStroke_Style, StrokeWidth=w)
            p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, bl))
            p.setBlendMode(skia.BlendMode.kPlus)
            c.drawCircle(x - 1400, 0, 1400, p)
    # knots that brighten as the shock passes, then pull gas inward
    g = smooth(prog(t, GRAV_T, GRAV_T + 3.0))
    for kx, ky, s in KNOTS:
        passed = smooth(prog(t, SHOCK[0] + (kx + 1500) / 3000 * (SHOCK[1] - SHOCK[0]), SHOCK[0] + (kx + 1500) / 3000 * (SHOCK[1] - SHOCK[0]) + 0.8))
        light(c, kx, ky, 120 * s * (1 + g), MAGENTA, 140 * passed)
        for i, (a, r) in enumerate(SPECKS[: int(30 * s)]):
            rr = r * s * (1 - 0.75 * g * ((i % 5 + 3) / 7))
            aa = a + g * 2.4 * (600 / max(r, 1))
            c.drawCircle(kx + math.cos(aa) * rr, ky + math.sin(aa) * rr * 0.8, 2.6, add((230, 200, 255), 170 * passed))
    cam.pop(c)

    def path(tt):
        return lerp(-200, W + 200, prog(tt, 1.0, 12.0)), 760 - 140 * math.sin(math.pi * prog(tt, 1.0, 12.0))
    if 1.0 < t < 12.0:
        orbi_on(c, t, path, 44, "wide", (0.6, -0.3), 0.4, rim=MAGENTA)
    label(c, "MOSTLY HYDROGEN · LIGHT-YEARS ACROSS", 960, 1030, (220, 200, 255), 28,
          255 * smooth(prog(t, TM.word("B1", "mostly") - 0.2, TM.word("B1", "mostly") + 0.4)) * (1 - smooth(prog(t, SHOCK[0], SHOCK[0] + 0.5))))
    for (txt, t0, rgb) in (("SHOCKWAVE", SHOCK[0] + 0.4, AMBER), ("GRAVITY TAKES OVER", GRAV_T, (230, 210, 255))):
        a = smooth(prog(t, t0, t0 + 0.4)) * (1 - smooth(prog(t, CLUMP[0], CLUMP[1])))
        if a > 0.01 and (txt != "SHOCKWAVE" or t < GRAV_T):
            c.saveLayerAlpha(None, int(255 * a))
            tag(c, txt, 960, 1020, rgb, 26)
            c.restore()


def protostar_scene(c, t):
    cam = drift_cam(t, CLUMP[0], CORE[1], 0, 0, 0, 0, 1.25, 1.5)
    space(c, t, cam, clouds=("cloud",), a=0.6)
    k = smooth(prog(t, CLUMP[1] - 0.5, CORE[0] + 0.5))
    cam.push(c, 0.9)
    draw_texture(c, tex_cloud(12), -60, 20, lerp(0.7, 0.25, k), t * 30 * k, 230 * (1 - k * 0.6), skia.BlendMode.kPlus)
    for i, (a, r) in enumerate(SPECKS):
        rr = r * lerp(1.0, 0.35, k) * (0.5 + 0.5 * ((t * 0.3 + i * 0.13) % 1))
        aa = a + t * (1.4 + 2.5 * k) * 260 / r
        c.drawCircle(-60 + math.cos(aa) * rr, 20 + math.sin(aa) * rr * 0.3, 2.2, add((255, 210, 180), 150))
    protostar(c, -60, 20, lerp(40, 30, k), t, lerp(0.35, 0.95, k))
    cam.pop(c)

    def path(tt):
        return 1520 + 30 * math.sin(tt * 0.8), 700 + 20 * math.sin(tt * 1.1)
    orbi_on(c, t, path, 100, "squint", (-0.8, -0.2), 0.1, rim=MAGENTA)
    tag(c, "SPINNING · DENSER · HOTTER", 960, 1010, SOLAR, 26)


H_START = [(-1, -1), (1, -1), (-1, 1), (1, 1)]


def ignition(c, t):
    cam = shake(drift_cam(t, CORE[0], DURATION, 0, 0, 0, 0, 1.0, 1.08), t, IGNITE, 12, 2.2)
    space(c, t, cam, clouds=("cloud",), a=0.45)
    ig = smooth(prog(t, IGNITE - 0.2, IGNITE + 0.5))
    # core cut-away (fades out at ignition)
    ca = 1 - smooth(prog(t, IGNITE - 0.6, IGNITE))
    if ca > 0.01:
        c.saveLayerAlpha(None, int(255 * ca))
        cx, cy = 960, 520
        heat = smooth(prog(t, CORE[1], FUSE_T))
        c.drawCircle(cx, cy, 380, shaded(radial((cx, cy), 380, [mix((200, 90, 50), (255, 220, 160), heat), (150, 50, 40), (60, 18, 30)], [0, 0.55, 1])))
        c.drawCircle(cx, cy, 380, stroke(SOLAR, 4, 160))
        text(c, f"{int(10_000_000 * heat):,} °C", cx, 980, 40, SOLAR, 255 * smooth(prog(t, CORE[1], CORE[1] + 0.4)), 800, spacing=4)
        for cyc in range(3):  # three fusion events in a row
            t0 = FUSE_T + cyc * 1.1
            u = prog(t, t0, t0 + 0.8)
            ox, oy = cx + (cyc - 1) * 230, cy + (cyc % 2) * 60 - 30
            if u < 1:
                for dx, dy in H_START:
                    d = lerp(130, 18, in_cubic(u))
                    atom_dot(c, ox + dx * d, oy + dy * d, 22, BLUE_STAR, t)
                    if u < 0.2 or t < t0:
                        text(c, "H", ox + dx * d, oy + dy * d + 8, 22, INK, 255, 800)
            else:
                fl = math.exp(-(t - t0 - 0.8) * 4)
                light(c, ox, oy, 160, HOTWHITE, 255 * fl, core=fl)
                atom_dot(c, ox, oy, 30, ELEMENTS["He"][1], t)
                text(c, "He", ox, oy + 10, 26, INK, 255, 800)
                for k in range(6):
                    ang = k / 6 * 6.28
                    d = 60 + 260 * (1 - fl)
                    c.drawCircle(ox + math.cos(ang) * d, oy + math.sin(ang) * d, 5, add(SOLAR, 220 * fl))
        label(c, "HYDROGEN → HELIUM", cx, 120, SOLAR, 32, 255 * smooth(prog(t, FUSE_T, FUSE_T + 0.4)))
        c.restore()
    if ig > 0:
        g = out_back(prog(t, IGNITE, IGNITE + 1.3), 1.3)
        star(c, 960, 520, 190 * g, t, SOLAR, 1.2)
        if t < IGNITE + 2.5:
            k = prog(t, IGNITE, IGNITE + 2.5)
            c.drawCircle(960, 520, 200 + 1400 * out_cubic(k), stroke(HOTWHITE, 12 * (1 - k), 230 * (1 - k)))
            flare(c, 960, 520, 220, SOLAR, 255 * (1 - k))
            c.drawPaint(add(HOTWHITE, 220 * math.exp(-(t - IGNITE) * 5)))
        label(c, "A STAR IS BORN", 960, 900, WHITE, 52, 255 * smooth(prog(t, IGNITE + 0.6, IGNITE + 1.2)))

        def path(tt):
            k2 = out_back(prog(tt, IGNITE + 0.3, IGNITE + 1.5), 1.2)
            return lerp(1500, 1620, k2), lerp(760, 680, k2) - 40 * abs(math.sin(tt * 3)) * smooth(prog(tt, IGNITE + 1.5, IGNITE + 2))
        orbi_on(c, t, path, 85, "happy", (-0.8, -0.3), 1.0, rim=SOLAR)


def draw_frame(c, t):
    scenes(c, t, [((0.0, 0.01), CLUMP[1], cloud), (CLUMP, CORE[1], protostar_scene), (CORE, DURATION + 1, ignition)])
    chapter_title(c, t, 2, "BIRTH", MAGENTA, 0.2, 2.5)
    fade(c, t, DURATION, 0.5, 0.6)


def sfx_events():
    return [(0.2, "swell_soft", 0.6), (1.2, "whoosh_long", 0.5), (SHOCK[0], "whoosh_long", 0.9), (SHOCK[0] + 0.9, "rumble", 0.9),
            (GRAV_T, "riser", 0.6), (CLUMP[0], "whoosh", 0.6), (CLUMP[1], "rumble", 0.6), (CORE[0], "whoosh", 0.6)] + \
           [(FUSE_T + i * 1.1 + 0.8, "tink", 0.9) for i in range(3)] + [(FUSE_T + i * 1.1 + 0.8, "chime", 0.5) for i in range(3)] + \
           [(IGNITE - 1.2, "riser", 1.0), (IGNITE, "boom", 1.0), (IGNITE, "shine", 1.0), (IGNITE + 0.1, "whoosh_long", 0.8), (IGNITE + 0.6, "swell_soft", 0.9)]


MUSIC = dict(
    chords=[(0.0, 48, (0, 7, 12, 14, 19)), (SHOCK[0], 44, (0, 7, 12, 15, 19)), (CLUMP[0], 46, (0, 7, 12, 16, 19)),
            (CORE[0], 43, (0, 7, 12, 14, 19)), (IGNITE, 48, (0, 7, 12, 16, 19, 24))],
    plucks=[(VO["B1"], SHOCK[0]), (CLUMP[0], DURATION)], bpm=90, rises=[(FUSE_T, IGNITE)], drone=33,
)

if __name__ == "__main__":
    import sys
    import render
    render.main([PART] + sys.argv[1:])
