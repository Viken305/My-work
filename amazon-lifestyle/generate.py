"""Generate Amazon lifestyle images for a product.

Modes
  composite  AI paints an empty kitchen scene, then the real packshot is placed
             in it with matching shadows and light. The label stays 100% exact.
  ai         The AI model puts the product into the scene itself. More natural
             interaction with props, but small text on the label may drift.
  both       Run both for every image.

Examples
  python generate.py --list-scenes
  python generate.py --product products/sweetmate-monkfruit.json --scene marble-morning
  python generate.py --product products/sweetmate-monkfruit.json --scene all --count 2 --provider openai
  python generate.py --product products/sweetmate-monkfruit.json --background my_kitchen.jpg --x 0.6 --base 0.82 --height 0.5
"""
import argparse
import json
import re
from pathlib import Path

from PIL import Image

import ai
import compose
from scenes import SCENES, prompt_empty, prompt_with_product


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_product(path):
    path = Path(path)
    p = json.loads(path.read_text())
    p["image_path"] = str(path.parent / p["image"])
    return p


def make_background(provider, scene):
    s = SCENES[scene]
    prompt = prompt_empty(scene)
    if provider == "gemini":
        return ai.gemini(prompt, aspect=s["aspect"])
    return ai.openai_image(prompt, aspect=s["aspect"])


def make_ai_shot(provider, scene, p):
    s = SCENES[scene]
    prompt = prompt_with_product(scene, p)
    if provider == "gemini":
        return ai.gemini(prompt, images=[Image.open(p["image_path"])], aspect=s["aspect"])
    return ai.openai_image(prompt, image_path=p["image_path"], aspect=s["aspect"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--product", help="product JSON file")
    ap.add_argument("--scene", default="marble-morning", help="scene name, or 'all'")
    ap.add_argument("--mode", choices=["composite", "ai", "both"], default="composite")
    ap.add_argument("--provider", choices=["gemini", "openai"], default="gemini",
                    help="gemini = Nano Banana, openai = ChatGPT image model")
    ap.add_argument("--count", type=int, default=1, help="images per scene")
    ap.add_argument("--background", help="use your own scene photo instead of generating one (composite only)")
    ap.add_argument("--cutout", help="product PNG with transparency, if the auto cutout isn't clean")
    ap.add_argument("--x", type=float, help="product center, 0..1 from the left")
    ap.add_argument("--base", type=float, help="product bottom edge, 0..1 from the top")
    ap.add_argument("--height", type=float, help="product height as a fraction of the frame")
    ap.add_argument("--light", choices=["left", "right"], help="side the light comes from")
    ap.add_argument("--reflection", type=float, help="mirror strength on glossy counters, 0 to 0.3")
    ap.add_argument("--out", default="out", help="output folder")
    ap.add_argument("--list-scenes", action="store_true")
    ap.add_argument("--print-prompts", action="store_true", help="show the prompts and stop")
    args = ap.parse_args()

    if args.list_scenes:
        for k, s in SCENES.items():
            print(f"{k:20s} {s['aspect']:5s} {s['label']}")
        return
    if not args.product:
        ap.error("--product is required")

    p = load_product(args.product)
    scenes = list(SCENES) if args.scene == "all" else [args.scene]
    for sc in scenes:
        if sc not in SCENES:
            ap.error(f"unknown scene '{sc}'. Run --list-scenes to see them.")

    if args.print_prompts:
        for sc in scenes:
            print(f"\n== {sc} · composite background ==\n{prompt_empty(sc)}")
            print(f"\n== {sc} · ai with product ==\n{prompt_with_product(sc, p)}")
        return

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    name = slug(p["name"])
    product_cut = compose.cutout(Image.open(args.cutout or p["image_path"]))
    product_cut.save(out / f"{name}_cutout.png")

    for sc in scenes:
        s = SCENES[sc]
        place = {**s["place"], **{k: v for k, v in
                 {"x": args.x, "base": args.base, "height": args.height}.items() if v is not None}}
        light = args.light or s["light"]
        reflection = s.get("reflection", 0.0) if args.reflection is None else args.reflection
        for i in range(1, args.count + 1):
            tag = f"{name}_{sc}_{i:02d}"
            if args.mode in ("composite", "both"):
                if args.background:
                    bg = Image.open(args.background).convert("RGB")
                else:
                    print(f"[{tag}] painting empty scene with {args.provider}…")
                    bg = make_background(args.provider, sc)
                    bg.save(out / f"{tag}_background.png")
                img = compose.place(bg, product_cut, light=light, reflection=reflection, **place)
                compose.fit_amazon(img).save(out / f"{tag}_composite.jpg", quality=95)
                print(f"[{tag}] saved {tag}_composite.jpg")
            if args.mode in ("ai", "both"):
                print(f"[{tag}] generating product shot with {args.provider}…")
                img = make_ai_shot(args.provider, sc, p)
                compose.fit_amazon(img).save(out / f"{tag}_ai.jpg", quality=95)
                print(f"[{tag}] saved {tag}_ai.jpg")


if __name__ == "__main__":
    main()
