# Amazon lifestyle image generator

Turns a product packshot into kitchen and food lifestyle images for Amazon listings,
using Nano Banana (Gemini) or ChatGPT (OpenAI) for the scenes.

## Two ways to make an image

| Mode | What happens | Label text | Best for |
|---|---|---|---|
| `composite` (default) | The AI paints an empty kitchen set. The code cuts your real packshot off its white background and places it with a contact shadow, soft occlusion, a cast shadow thrown away from the light, light and color matching, an optional counter reflection, and film grain. | Exact. Your real artwork is used, never redrawn. | Products with a lot of text on the pack |
| `ai` | The AI model places the product into the scene itself, using your photo as reference. | Can drift. Check every image. | Hands-in-use shots, products tucked in among props |
| `both` | Runs both modes. | | Comparing results |

## Setup

```bash
cd amazon-lifestyle
pip install -r requirements.txt
export GEMINI_API_KEY=...        # Nano Banana, from aistudio.google.com
export OPENAI_API_KEY=...        # ChatGPT images, from platform.openai.com
```

## Use

```bash
python generate.py --list-scenes
python generate.py --product products/sweetmate-monkfruit.json --scene marble-morning
python generate.py --product products/sweetmate-monkfruit.json --scene all --count 3
python generate.py --product products/sweetmate-monkfruit.json --scene chai-golden --mode both --provider openai
python generate.py --product products/sweetmate-monkfruit.json --scene chai-golden --print-prompts
```

Use your own kitchen photo (no API key needed):

```bash
python generate.py --product products/sweetmate-monkfruit.json \
  --background my_kitchen.jpg --x 0.6 --base 0.82 --height 0.45 --light right --reflection 0.15
```

- `--x` product center, from 0 (left) to 1 (right)
- `--base` where the bottom of the product sits, from 0 (top) to 1 (bottom)
- `--height` product height as a fraction of the frame
- `--light` the side the sunlight comes from in the photo, so the shadows match
- `--reflection` 0 for wood, linen or matte stone; 0.1 to 0.25 for polished marble or glass

Images are saved in `out/`, resized so the longest side is 2000 px. Each AI background is
saved too (`*_background.png`), so you can re-run the placement with different
`--x/--base/--height` without paying for a new image.

## Adding a product

Copy `products/sweetmate-monkfruit.json`, change the text, and put the packshot next to it.
The automatic cutout expects a plain white background. If the cutout isn't clean, export a
transparent PNG (for example from remove.bg or Photoshop) and pass it with `--cutout product.png`.

## Adding a scene

Add an entry to `SCENES` in `scenes.py`: set, props, lighting, camera, grade, the side the
light comes from, and where the empty spot for the product is (`place`).

## Before uploading to Amazon

- Lifestyle images go in the secondary image slots. The main image must be the product
  on pure white.
- Check every `ai` mode image against the real pack: colors, text, net weight.
- AI images are generated at about 1024 to 1536 px and enlarged to 2000 px. That meets
  Amazon's zoom requirement, but it does not add real detail.
