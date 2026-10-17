"""Cosmic objects for the stars video, drawn with the premium kit."""
import math

from orbi import *  # noqa: F401,F403

# ---------------------------------------------------------------- textures (cached, deterministic)
def tex_cloud(seed=11):
    return nebula_texture("cloud", seed, [(0.0, (50, 24, 110)), (0.4, (140, 60, 200)), (0.68, (250, 80, 150)), (1.0, (255, 190, 140))], density=1.0, warp=110, lo=0.3)


def tex_dust(seed=21):
    return nebula_texture("dust", seed, [(0.0, (10, 10, 30)), (0.6, (40, 26, 60)), (1.0, (90, 60, 90))], density=0.9, warp=80, lo=0.45, hi=0.9)


def tex_teal(seed=31):
    return nebula_texture("teal", seed, [(0.0, (10, 30, 70)), (0.5, (30, 120, 170)), (0.8, (60, 210, 200)), (1.0, (200, 255, 240))], density=0.9, warp=120)


def tex_fire(seed=61):
    return nebula_texture("fire", seed, [(0.0, (60, 10, 20)), (0.4, (200, 60, 30)), (0.7, (255, 160, 60)), (1.0, (255, 245, 210))], density=1.0, warp=140, lo=0.25)


def tex_web(seed=71):
    return nebula_texture("web", seed, [(0.0, (10, 14, 40)), (0.6, (50, 70, 150)), (1.0, (140, 170, 255))], density=0.9, warp=160, lo=0.42, hi=0.95)


def tex_ring(seed=41):
    """Planetary-nebula shell: noise masked into a ring."""
    key = ("ring", seed)
    if key in TEX_CACHE:
        return TEX_CACHE[key]
    path = os.path.join(CACHE, f"ring_{seed}.png")
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        s = 900
        n = warped_fbm(s, s, seed, 120, 60)
        yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
        r = np.sqrt((xx - s / 2) ** 2 + (yy - s / 2) ** 2) / (s / 2)
        ring = np.exp(-((r - 0.62 - (n - 0.5) * 0.18) / 0.16) ** 2) + 0.35 * np.exp(-(r / 0.45) ** 2)
        stops = np.array([0, 0.5, 0.8, 1.0], np.float32)
        cols = np.array([(30, 60, 160), (60, 200, 220), (240, 110, 160), (255, 220, 200)], np.float32)
        tint = np.clip(r * 0.9 + (n - 0.5) * 0.4, 0, 1)
        rgb = np.stack([np.interp(tint, stops, cols[:, k]) for k in range(3)], -1)
        a = np.clip(ring * (0.55 + 0.6 * n), 0, 1)
        cv2.imwrite(path, cv2.cvtColor(np.dstack([rgb, a * 255]).astype(np.uint8), cv2.COLOR_RGBA2BGRA))
    TEX_CACHE[key] = skia.Image.open(path)
    return TEX_CACHE[key]


def tex_granules(seed=51):
    """Stellar surface granulation (grey, used as overlay inside star discs)."""
    key = ("gran", seed)
    if key in TEX_CACHE:
        return TEX_CACHE[key]
    path = os.path.join(CACHE, f"gran_{seed}.png")
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        n = fbm(512, 512, seed, 24, 5, 0.6)
        n2 = fbm(512, 512, seed + 1, 90, 4, 0.5)
        v = np.clip(0.55 + (n - 0.5) * 1.3 + (n2 - 0.5) * 0.5, 0, 1)
        g = (v * 255).astype(np.uint8)
        cv2.imwrite(path, cv2.cvtColor(np.dstack([g, g, g, np.full_like(g, 255)]), cv2.COLOR_RGBA2BGRA))
    TEX_CACHE[key] = skia.Image.open(path)
    return TEX_CACHE[key]


# ---------------------------------------------------------------- stars
def star(c, x, y, r, t, rgb=SOLAR, corona=1.0, a=255, rot_speed=4.0, flares=False, spikes_on=False, granule_a=34):
    """Textured star: corona glow, limb-darkened disc, rotating granulation, prominences."""
    if r <= 0.5 or a <= 1:
        return
    if a < 255:
        c.saveLayerAlpha(None, int(a))
    light(c, x, y, min(r * 9.0, r * 1.6 + 520) * corona, rgb, 110 * corona)
    light(c, x, y, min(r * 3.2, r * 1.25 + 260) * corona, lighten(rgb, 0.3), 255 * corona)
    light(c, x, y, r * 1.6 * corona, HOTWHITE, 200 * corona)
    disc = circle_path(x, y, r)
    c.drawPath(disc, shaded(radial((x - r * 0.2, y - r * 0.2), r * 1.15, [HOTWHITE, lighten(rgb, 0.55), lighten(rgb, 0.15), darken(rgb, 0.15)], [0, 0.4, 0.82, 1])))
    c.save()
    c.clipPath(disc, doAntiAlias=True)
    g = tex_granules()
    gp = skia.Paint(AntiAlias=True)
    gp.setAlphaf(granule_a / 255)
    gp.setBlendMode(skia.BlendMode.kMultiply)
    c.save()
    c.translate(x, y)
    c.rotate(t * rot_speed)
    sc = r * 2.4 / g.width()
    c.scale(sc, sc)
    c.drawImage(g, -g.width() / 2, -g.height() / 2, skia.SamplingOptions(skia.FilterMode.kLinear), gp)
    c.restore()
    c.drawPath(disc, shaded(radial((x, y), r, [(WHITE, 0), (WHITE, 0), (darken(rgb, 0.3), 110)], [0, 0.75, 1])))   # limb darkening
    c.restore()
    if flares:
        for k in range(3):
            ph = (t * 0.12 + k / 3) % 1
            ang = math.radians(k * 127 + 40)
            bx, by = x + r * math.cos(ang), y + r * math.sin(ang)
            loop = skia.Path()
            nx, ny = math.cos(ang), math.sin(ang)
            tx, ty = -ny, nx
            h = r * 0.35 * math.sin(math.pi * ph)
            loop.moveTo(bx - tx * r * 0.12, by - ty * r * 0.12)
            loop.cubicTo(bx - tx * r * 0.12 + nx * h * 2, by - ty * r * 0.12 + ny * h * 2, bx + tx * r * 0.12 + nx * h * 2, by + ty * r * 0.12 + ny * h * 2, bx + tx * r * 0.12, by + ty * r * 0.12)
            pp = skia.Paint(AntiAlias=True, Color=col(lighten(rgb, 0.2), 110 * math.sin(math.pi * ph)), Style=skia.Paint.kStroke_Style, StrokeWidth=max(1.5, r * 0.05))
            pp.setBlendMode(skia.BlendMode.kPlus)
            c.drawPath(loop, pp)
    if spikes_on:
        spikes(c, x, y, r * 6, lighten(rgb, 0.4), 200, 4, 45)
    if a < 255:
        c.restore()


def _disk(c, x, y, r_in, r_out, tilt, t, a, half):
    """Smooth accretion disk: filled elliptical gradient + rotating spiral streaks. half: 'back' or 'front'."""
    c.save()
    clip = skia.Rect.MakeXYWH(x - r_out * 2.2, y - r_out, r_out * 4.4, r_out) if half == "back" else skia.Rect.MakeXYWH(x - r_out * 2.2, y, r_out * 4.4, r_out)
    c.clipRect(clip)
    c.translate(x, y)
    c.scale(1, tilt)
    g = skia.Paint(AntiAlias=True, Shader=radial((0, 0), r_out, [((255, 240, 200), 0), ((255, 220, 160), 230 * a / 255), ((240, 110, 120), 150 * a / 255), ((120, 50, 170), 0)],
                                                  [0, r_in / r_out, 0.6, 1]))
    g.setBlendMode(skia.BlendMode.kPlus)
    c.drawCircle(0, 0, r_out, g)
    for k in range(9):
        ph = t * (1.6 - k * 0.08) + k * 0.7
        rr = lerp(r_in * 1.2, r_out * 0.9, k / 8)
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(-rr, -rr, rr * 2, rr * 2), math.degrees(ph) % 360, 70)
        sp = skia.Paint(AntiAlias=True, Color=col((255, 230, 190), 70 * a / 255), Style=skia.Paint.kStroke_Style, StrokeWidth=r_out * 0.03)
        sp.setStrokeCap(skia.Paint.kRound_Cap)
        sp.setBlendMode(skia.BlendMode.kPlus)
        c.drawPath(arc, sp)
    c.restore()


def protostar(c, x, y, r, t, k=1.0, a=255):
    """Collapsing clump with a spinning accretion disk and polar jets. k: 0 (loose) .. 1 (compact, hot)."""
    if r <= 1:
        return
    tilt = 0.26
    r_out = r * lerp(6.0, 4.0, k)
    _disk(c, x, y, r * 0.9, r_out, tilt, t, a, "back")
    if k > 0.6:
        jk = (k - 0.6) / 0.4
        for s in (-1, 1):
            jet = skia.Path()
            jet.moveTo(x - r * 0.18, y)
            jet.quadTo(x, y + s * r * 3 * jk, x, y + s * r * 7 * jk)
            jet.quadTo(x, y + s * r * 3 * jk, x + r * 0.18, y)
            jet.close()
            jp = skia.Paint(AntiAlias=True, Shader=linear((x, y), (x, y + s * r * 7 * jk), [(TEAL, 230 * a / 255), (TEAL, 0)]))
            jp.setBlendMode(skia.BlendMode.kPlus)
            c.drawPath(jet, jp)
    hot = mix((220, 90, 70), SOLAR, k)
    light(c, x, y, r * 4.0, hot, 170 * a / 255, core=k)
    c.drawCircle(x, y, r * lerp(0.9, 0.6, k), shaded(radial((x, y), r, [HOTWHITE, hot, (hot, 0)], [0, 0.6, 1])))
    _disk(c, x, y, r * 0.9, r_out, tilt, t, a, "front")


def white_dwarf(c, x, y, r, t, a=255):
    light(c, x, y, min(r * 9, r + 260), BLUE_STAR, 140 * a / 255)
    c.drawCircle(x, y, r, shaded(radial((x - r * 0.3, y - r * 0.3), r * 1.3, [WHITE, (210, 225, 255), (150, 170, 230)])))
    if r < 30:
        spikes(c, x, y, r * 10, (210, 225, 255), 180 * a / 255)


def neutron_star(c, x, y, r, t, a=255, beam=22):
    """Pulsar: tiny bright sphere with sweeping beams and magnetic field loops."""
    ang = t * 120
    for s in (0, 180):
        c.save()
        c.translate(x, y)
        c.rotate(ang + s)
        bm = skia.Path()
        bm.moveTo(0, 0)
        bm.lineTo(r * beam, -r * 2.4)
        bm.lineTo(r * beam, r * 2.4)
        bm.close()
        bp = skia.Paint(AntiAlias=True, Shader=linear((0, 0), (r * beam, 0), [(BLUE_STAR, 200 * a / 255), (BLUE_STAR, 0)]))
        bp.setBlendMode(skia.BlendMode.kPlus)
        c.drawPath(bm, bp)
        c.restore()
    for k in range(4):
        rr = r * (3 + k * 1.6)
        p = skia.Path()
        p.addOval(skia.Rect.MakeXYWH(x - rr, y - rr * 0.45, rr * 2, rr * 0.9))
        c.save()
        c.translate(x, y)
        c.rotate(ang * 0.15 + 90)
        c.translate(-x, -y)
        c.drawPath(p, stroke(VIOLET2, 2, 110 * a / 255))
        c.restore()
    light(c, x, y, r * 8, (180, 200, 255), 200 * a / 255, core=1)
    c.drawCircle(x, y, r, fill((230, 240, 255), a))


def black_hole(c, x, y, r, t, a=255):
    """Event horizon + photon ring + smooth accretion disk with its gravitationally lensed arc over the top."""
    tilt = 0.2
    lens = skia.Paint(AntiAlias=True, Shader=radial((x, y), r * 3.2, [((255, 200, 120), 0), ((255, 200, 120), 0), (HOTWHITE, 230 * a / 255), (AMBER, 120 * a / 255), ((255, 90, 40), 0)],
                                                     [0, 0.36, 0.42, 0.62, 1]))
    lens.setBlendMode(skia.BlendMode.kPlus)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x - r * 4, y - r * 4, r * 8, r * 4))
    c.drawCircle(x, y, r * 3.2, lens)
    c.restore()
    light(c, x, y, r * 4, AMBER, 70 * a / 255)
    c.drawCircle(x, y, r * 1.08, stroke(HOTWHITE, r * 0.07, 240 * a / 255))
    c.drawCircle(x, y, r, fill((0, 0, 0), a))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x - r * 6, y - 1, r * 12, r * 3))
    c.translate(x, y)
    c.scale(1.7, tilt)
    disk = skia.Paint(AntiAlias=True, Shader=radial((0, 0), r * 3.4, [(HOTWHITE, 0), (HOTWHITE, 0), (HOTWHITE, 255 * a / 255), ((255, 160, 70), 170 * a / 255), ((200, 60, 30), 0)],
                                                     [0, 0.3, 0.36, 0.6, 1]))
    disk.setBlendMode(skia.BlendMode.kPlus)
    c.drawCircle(0, 0, r * 3.4, disk)
    for k in range(10):
        rr = r * (1.3 + k * 0.2)
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(-rr, -rr, rr * 2, rr * 2), (t * (90 - k * 6) + k * 37) % 360, 50)
        sp = skia.Paint(AntiAlias=True, Color=col(HOTWHITE, 90 * a / 255), Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.06)
        sp.setBlendMode(skia.BlendMode.kPlus)
        sp.setStrokeCap(skia.Paint.kRound_Cap)
        c.drawPath(arc, sp)
    c.restore()


def shockwave(c, x, y, r, t, k, a=255):
    """Supernova: expanding shell (k 0..1) with debris filaments, flash, and lens flare."""
    if k <= 0:
        return
    rr = r * out_expo(k)
    fade = 1 - smooth(prog(k, 0.55, 1.0))
    light(c, x, y, rr * 1.4, AMBER, 200 * fade * a / 255)
    sh = skia.Paint(AntiAlias=True, Shader=radial((x, y), rr, [((255, 120, 60), 0), ((255, 120, 60), 0), ((255, 200, 140), 230 * fade), ((140, 80, 255), 0)], [0, 0.7, 0.93, 1]))
    sh.setBlendMode(skia.BlendMode.kPlus)
    c.drawCircle(x, y, rr, sh)
    rng = np.random.default_rng(7)
    for i in range(70):
        ang = rng.uniform(0, 6.28)
        d0 = rng.uniform(0.55, 1.0)
        ln = rng.uniform(0.06, 0.2)
        cc = [AMBER, MAGENTA, TEAL, SOLAR][i % 4]
        p = skia.Paint(AntiAlias=True, Color=col(cc, 200 * fade * a / 255), Style=skia.Paint.kStroke_Style, StrokeWidth=max(1.5, r * 0.006))
        p.setBlendMode(skia.BlendMode.kPlus)
        c.drawLine(x + math.cos(ang) * rr * d0, y + math.sin(ang) * rr * d0, x + math.cos(ang) * rr * (d0 + ln), y + math.sin(ang) * rr * (d0 + ln), p)
    flash = math.exp(-k * 9)
    if flash > 0.02:
        light(c, x, y, r * 1.2 * (1 + k * 3), HOTWHITE, 255 * flash * a / 255, core=2)
        flare(c, x, y, r * 0.25, (160, 190, 255), 230 * flash * a / 255)


# ---------------------------------------------------------------- elements
ELEMENTS = {"H": ("HYDROGEN", (150, 200, 255)), "He": ("HELIUM", (255, 220, 120)), "C": ("CARBON", (120, 120, 140)),
            "O": ("OXYGEN", (255, 110, 110)), "Si": ("SILICON", (180, 150, 255)), "Fe": ("IRON", (230, 140, 90)),
            "Ca": ("CALCIUM", (240, 240, 230)), "Au": ("GOLD", (255, 200, 60)),
            "Li": ("LITHIUM", (255, 120, 200))}


def element_chip(c, x, y, s, sym, a=255, glow_a=120):
    name, rgb = ELEMENTS[sym]
    if a <= 1:
        return
    c.saveLayerAlpha(None, int(a))
    light(c, x, y, s * 1.6, rgb, glow_a)
    c.drawRRect(rrect(x - s * 0.6, y - s * 0.6, s * 1.2, s * 1.2, s * 0.18), shaded(linear((x, y - s * 0.6), (x, y + s * 0.6), [mix(DEEP, rgb, 0.55), mix(DEEP, rgb, 0.25)])))
    c.drawRRect(rrect(x - s * 0.6, y - s * 0.6, s * 1.2, s * 1.2, s * 0.18), stroke(lighten(rgb, 0.4), s * 0.03, 200))
    text(c, sym, x, y + s * 0.16, s * 0.52, WHITE, 255, 800)
    text(c, name, x, y + s * 0.44, s * 0.13, lighten(rgb, 0.5), 230, 800, spacing=s * 0.01)
    c.restore()


def atom_dot(c, x, y, r, rgb, t, a=255):
    light(c, x, y, r * 3, rgb, 120 * a / 255)
    c.drawCircle(x, y, r, shaded(radial((x - r * 0.3, y - r * 0.3), r * 1.3, [lighten(rgb, 0.5), rgb, darken(rgb, 0.3)])))


def onion(c, x, y, r, layers, a=255):
    """Massive-star core: concentric shells of elements (outer -> inner)."""
    for i, sym in enumerate(layers):
        rr = r * (1 - i / len(layers))
        _, rgb = ELEMENTS[sym]
        c.drawCircle(x, y, rr, shaded(radial((x, y), rr, [lighten(rgb, 0.25), rgb, darken(rgb, 0.2)], [0, 0.7, 1])))
        c.drawCircle(x, y, rr, stroke(WHITE, 2, 90))


def earth(c, x, y, r, t, a=255):
    light(c, x, y, r * 1.6, (90, 170, 255), 90 * a / 255)
    disc = circle_path(x, y, r)
    c.drawPath(disc, shaded(radial((x - r * 0.35, y - r * 0.4), r * 1.5, [(80, 160, 255), (40, 96, 220), (20, 40, 120)], [0, 0.55, 1])))
    c.save()
    c.clipPath(disc, doAntiAlias=True)
    for k in range(4):
        cx = x + ((k * 0.6 + t * 0.03) % 2.2 - 1.1) * r * 1.4
        rad = [r * (0.24 + 0.1 * math.sin(j * 1.7 + k * 2.3) + 0.05 * math.cos(j * 3.1 + k)) for j in range(12)]
        c.drawPath(blob_path(cx, y + (k - 1.5) * r * 0.45, rad, k), fill((80, 190, 120)))
    c.drawPath(disc, shaded(linear((x - r, y - r), (x + r, y + r), [((5, 5, 20), 0), ((5, 5, 20), 0), ((5, 5, 20), 200)], [0, 0.5, 1])))
    c.restore()
    c.drawCircle(x, y, r * 1.02, stroke((140, 200, 255), max(1.5, r * 0.03), 160 * a / 255))
