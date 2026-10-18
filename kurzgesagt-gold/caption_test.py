"""9 s kinetic-caption motion test + a caption style board.

  python3 caption_test.py          -> out/style/caption_test.mp4 + out/style/caption_board.png
"""
import math, os, sys

from PIL import Image

from kinetic import *  # noqa: F401,F403

PREMIUM, SAMPLES = True, 3
DURATION = 9.0


def draw_frame(c, t):
    shake_ = 0.0
    space_bg(c, t, warm=0.2)
    cx, cy = W / 2, 900
    # beat 1 (0-3 s): two neutron stars spiral in; caption anchored at the top band
    if t < 3.2:
        k = in_cubic(prog(t, 0.0, 3.0))
        rr = lerp(300, 30, k)
        ph = t * (1.2 + 6 * k)
        for s in (0, math.pi):
            neutron_star(c, cx + math.cos(ph + s) * rr, cy + math.sin(ph + s) * rr * 0.45, 26, t)
        phrase(c, ["TWO", "DEAD", "STARS"], W / 2, 360, t, 0.3, 80, hi=1, exit_t=2.0)
        react_collide(c, W / 2, 470, t, 2.2, 120)
    # beat 2 (3-6 s): kilonova; the hero word slams in over the explosion, then settles into the line
    if t >= 3.0:
        kilonova(c, cx, cy, 560, t, prog(t, 3.0, 7.0))
        shake_ = hero(c, "GOLD", W / 2, 1200, t, 3.5, 200, settle=5.0)
        phrase(c, ["IS", "BORN"], W / 2, 1300, t, 5.3, 72, exit_t=6.8)
    # beat 3 (6-9 s): caption moves next to Auri, word acts out its meaning
    if t > 6.2:
        def path(tt):
            return lerp(1300, 760, out_back(prog(tt, 6.2, 7.2), 1.2)), 1450 + 10 * math.sin(tt * 2)
        (x, y), vel = (path(t), ((path(t + 1 / 60)[0] - path(t)[0]) * 60, 0))
        auri(c, x, y, 100, t, pose("laugh" if t > 7.6 else "shocked"), (-0.6, -0.5), vel=vel, env=(255, 170, 110))
        phrase(c, ["SEVERAL", "EARTHS", "OF", "GOLD!"], W / 2, 520, t, 6.9, 76, hi=3, word_dt=0.18)
    if shake_:
        c.translate(shake_ * math.sin(t * 60), shake_ * math.cos(t * 50))
    a = max(1 - smooth(prog(t, 0, 0.4)), smooth(prog(t, DURATION - 0.4, DURATION)))
    if a > 0:
        c.drawPaint(fill((4, 4, 14), 255 * a))


def board(path):
    """One image summarising the treatments, frozen at their best moment."""
    from premium import render_premium
    tiles = []

    def t1(c, t):      # pop + gold spoken word
        space_bg(c, t)
        phrase(c, ["OLDER", "THAN", "THE", "SUN"], W / 2, 900, 2.0, 0.0, 96, hi=3)
        text(c, "POP-IN WORDS · SPOKEN WORD TURNS GOLD", W / 2, 1600, 30, (200, 200, 230), 255, 800, spacing=3)

    def t2(c, t):      # hero slam
        space_bg(c, t, warm=0.3)
        kilonova(c, W / 2, 800, 520, t, 0.3)
        hero(c, "GOLD", W / 2, 1150, 3.62, 3.5, 200)
        text(c, "HERO WORDS SLAM IN AS POLISHED GOLD", W / 2, 1600, 30, (200, 200, 230), 255, 800, spacing=3)

    def t3(c, t):      # collide
        space_bg(c, t)
        react_collide(c, W / 2, 900, 0.62, 0.0, 130)
        text(c, "COLLIDE: THE WORD SMASHES TOGETHER", W / 2, 1600, 30, (200, 200, 230), 255, 800, spacing=3)

    def t4(c, t):      # sank
        space_bg(c, t)
        earth_section(c, W / 2, 1150, 380, t)
        react_sank(c, W / 2, 560, 0.4, 0.0, 130)
        text(c, "SANK: LETTERS DROP", W / 2, 1700, 30, (200, 200, 230), 255, 800, spacing=3)

    def t5(c, t):      # steam / earthquake
        c.drawPaint(fill((30, 22, 40)))
        rock_wall(c, 0, 0, W, H, t, 5, (120, 86, 92))
        react_shake(c, W / 2, 640, 0.15, 0.0, 100)
        react_steam(c, W / 2, 1150, 0.7, 0.0, 130)
        text(c, "EARTHQUAKE SHAKES · STEAM DISSOLVES", W / 2, 1700, 30, WHITE, 255, 800, spacing=3)

    def t6(c, t):      # anchored next to Auri
        space_bg(c, t, warm=0.2)
        auri(c, 760, 1150, 120, t, pose("laugh"), (-0.6, -0.5))
        phrase(c, ["SEVERAL", "EARTHS", "OF", "GOLD!"], W / 2, 760, 2.0, 0.0, 84, hi=3)
        c.drawLine(640, 800, 700, 1010, stroke(WHITE, 4, 120))
        text(c, "CAPTIONS MOVE TO FREE SPACE, NEAR AURI", W / 2, 1600, 30, (200, 200, 230), 255, 800, spacing=3)
    for fn in (t1, t2, t3, t4, t5, t6):
        tiles.append(Image.fromarray(render_premium(fn, 2.0, samples=1)).resize((540, 960)))
    img = Image.new("RGB", (540 * 3, 960 * 2))
    for i, tl in enumerate(tiles):
        img.paste(tl, ((i % 3) * 540, (i // 3) * 960))
    img.save(path)


if __name__ == "__main__":
    import render
    out = os.path.join(HERE, "out", "style")
    board(os.path.join(out, "caption_board.png"))
    if "--board" in sys.argv:
        raise SystemExit
    v = render.render_video("caption_test")
    import audio
    wav = os.path.join(HERE, "build", "caption_test", "mix.wav")
    audio.render_mix(wav, DURATION, [], [(0.3, "pop", 0.5), (0.52, "pop", 0.5), (0.74, "pop", 0.5), (2.2, "whoosh", 0.8), (2.7, "boom", 0.7),
                                          (3.0, "boom", 1.0), (3.5, "shine", 0.9), (3.85, "pop", 1.0), (5.3, "pop", 0.4), (6.2, "whoosh", 0.6),
                                          (6.9, "pop", 0.4), (7.1, "pop", 0.4), (7.3, "pop", 0.4), (7.5, "chime", 0.8)],
                     dict(chords=[(0.0, 45, (0, 7, 12, 15, 19)), (3.0, 48, (0, 7, 12, 16, 19, 24))], plucks=[(0.3, DURATION)], bpm=104, rises=[(1.5, 3.0)]))
    master = os.path.join(HERE, "build", "caption_test", "master.mp4")
    render.mux(v, wav, master)
    render.encode(master, os.path.join(out, "caption_test.mp4"), 22)
    print(os.path.join(out, "caption_test.mp4"))
