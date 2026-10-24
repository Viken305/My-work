"""Style-guide boards: 4 key frames + palette + type + trade-offs per style -> out/board_<style>.png

  python3 boards.py
"""
import os, sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402

BW, BH = 1920, 1560
BG, INK, MUTED = (244, 242, 238), (22, 22, 26), (110, 108, 116)

STYLES = {
    "style_3b1b": dict(
        name="A  ·  3Blue1Brown style", tag="Dark canvas, glowing precise curves, LaTeX maths. Calm and clever.",
        times=[(1.6, "Title writes itself in"), (4.8, "Wave goes in, echo comes back"),
               (7.6, "Standing wave + the equation"), (11.5, "sin²(kx) becomes hot / cold spots")],
        notes=[("Feels like", "Calm, precise, “I finally get it”."),
               ("Best for", "Mechanisms: waves, forces, graphs, equations."),
               ("Trade-off", "Less playful. Real objects look abstract."),
               ("Build effort", "Medium. Very consistent across episodes.")]),
    "style_kinetic": dict(
        name="B  ·  Kinetic typography + icons", tag="Big slamming words, hard colour cuts, thick-outline icons. Punchy.",
        times=[(1.9, "Hook line slams in"), (5.9, "Counter rolls to 2.45 billion"),
               (8.9, "FLIP. FLIP. FLIP. = HEAT"), (10.4, "Icon microwave with hot / cold dots")],
        notes=[("Feels like", "High energy, scroll-stopping, meme-able."),
               ("Best for", "Shorts / Reels hooks, numbers, quick facts."),
               ("Trade-off", "Less physics on screen; leans on voice + music."),
               ("Build effort", "Lowest. Fastest per minute of video.")]),
    "style_lowpoly": dict(
        name="C  ·  Low-poly 3D", tag="Faceted toy-like models, dusk lighting, orbiting camera, caption chips.",
        times=[(1.5, "Closed oven, mug turning behind glass"), (4.2, "Door swings open, roof lifts off"),
               (7.5, "3D heat map under the standing wave"), (11.0, "Turntable drags the mug through it")],
        notes=[("Feels like", "Tactile, cinematic, “wow, look inside”."),
               ("Best for", "Real objects and 3D space: inside machines."),
               ("Trade-off", "Heaviest to build; equations feel bolted on."),
               ("Build effort", "Highest. Longer renders.")]),
}


def f(face, size):
    return ImageFont.truetype(os.path.join(kit.FONTS, kit.FACES[face]), size)


def board(name, spec):
    import importlib
    kit._init(name)
    mod = importlib.import_module(name)
    img = Image.new("RGB", (BW, BH), BG)
    d = ImageDraw.Draw(img)
    d.text((80, 64), spec["name"], font=f("black", 64), fill=INK)
    d.text((80, 150), spec["tag"], font=f("medium", 32), fill=MUTED)

    fw, fh, gap, gx, gy = 868, 488, 24, 80, 220
    for i, (t, cap) in enumerate(spec["times"]):
        fr = Image.fromarray(kit.frame(mod, t)).resize((fw, fh), Image.LANCZOS)
        x, y = gx + (i % 2) * (fw + gap), gy + (i // 2) * (fh + gap)
        img.paste(fr, (x, y))
        d.rectangle((x - 1, y - 1, x + fw, y + fh), outline=(205, 202, 196))
        label = f"{i + 1}   {cap}"
        tw = d.textlength(label, font=f("semi", 24))
        d.rounded_rectangle((x + 16, y + 16, x + 16 + tw + 32, y + 58), 21, fill=(255, 255, 255))
        d.text((x + 32, y + 23), label, font=f("semi", 24), fill=INK)

    y0 = gy + 2 * fh + gap + 50
    d.text((80, y0), "PALETTE", font=f("bold", 22), fill=MUTED)
    for i, (label, rgb) in enumerate(mod.PALETTE):
        x = 80 + (i % 4) * 150
        y = y0 + 40 + (i // 4) * 110
        d.rounded_rectangle((x, y, x + 130, y + 56), 12, fill=tuple(int(v) for v in rgb), outline=(200, 198, 194))
        d.text((x, y + 64), label, font=f("medium", 18), fill=INK)
        d.text((x, y + 86), "#%02X%02X%02X" % tuple(int(v) for v in rgb), font=f("medium", 16), fill=MUTED)

    d.text((720, y0), "TYPE", font=f("bold", 22), fill=MUTED)
    face, desc = mod.FONTS_USED[0]
    sample = "Aa  Why?" if face != "black" else "AA  WHY?"
    d.text((720, y0 + 36), sample, font=f(face, 76), fill=INK)
    d.text((720, y0 + 136), desc, font=f("medium", 22), fill=MUTED)

    d.text((1180, y0), "AT A GLANCE", font=f("bold", 22), fill=MUTED)
    for i, (k, v) in enumerate(spec["notes"]):
        y = y0 + 40 + i * 50
        d.text((1180, y), k, font=f("bold", 24), fill=INK)
        d.text((1350, y), v, font=f("medium", 24), fill=INK)
    out = os.path.join(kit.OUT, f"board_{name.replace('style_', '')}.png")
    img.save(out)
    print(out)


if __name__ == "__main__":
    for name, spec in STYLES.items():
        board(name, spec)
