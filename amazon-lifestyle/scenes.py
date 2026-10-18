"""Scene presets for kitchen / food lifestyle images.

Each scene has two prompts:
  - "with_product": the AI places the product itself (mode "ai")
  - "empty": the AI paints the set with an empty spot, and compose.py
    drops the real packshot in (mode "composite", label stays exact)

"place" is where the product's base sits in the empty scene, as fractions
of the frame: x = horizontal center, base = vertical position of the
bottom edge, height = product height. "light" is the side the key light
comes from, used for shading and the cast shadow.
"""

REALISM = (
    "Every highlight, shadow and reflection comes from the same light source. "
    "Objects sit firmly on the surface with thin dark contact shadows. "
    "Surfaces have real texture and small imperfections: stone pores, wood grain, "
    "linen creases, a few stray crumbs and granules. Natural highlight roll-off, "
    "subtle fine film grain. Looks like a real commercial food photograph shot on "
    "a full-frame camera, not a 3D render."
)

AVOID = (
    "No CGI look, no plastic-smooth surfaces, no floating objects, no duplicate "
    "products, no invented text, no extra logos, no watermark, no oversaturation."
)

SCENES = {
    "marble-morning": {
        "label": "Marble counter, morning window light",
        "aspect": "1:1",
        "light": "left",
        "reflection": 0.15,
        "place": {"x": 0.58, "base": 0.80, "height": 0.56},
        "set": (
            "a white marble kitchen countertop with soft grey veining beside a large "
            "window, a bright modern kitchen softly blurred behind"
        ),
        "props": (
            "a small ceramic bowl of fine white sweetener granules with a wooden spoon "
            "resting in it, a few stray granules on the marble, two whole dried brown "
            "monk fruits, one cut open, with a few green leaves"
        ),
        "lighting": (
            "soft morning sunlight from a window on the left at a low angle, soft-edged "
            "shadows falling to the right, a faint window-frame shadow on the counter"
        ),
        "camera": "shot from about 15 degrees above, 85mm lens at f/4",
        "grade": "warm, fresh color grade",
    },
    "chai-golden": {
        "label": "Chai on walnut table, golden hour",
        "aspect": "1:1",
        "light": "left",
        "place": {"x": 0.66, "base": 0.78, "height": 0.52},
        "set": "a warm walnut wood table by a window, a cozy kitchen softly blurred behind",
        "props": (
            "a ceramic cup of milky chai with gentle steam rising, a wooden spoon with "
            "white sweetener granules resting on a saucer, a small plate with two "
            "biscuits at the edge of the frame"
        ),
        "lighting": (
            "low golden-hour sunlight from the left through the window, long soft "
            "shadows to the right, steam backlit and glowing"
        ),
        "camera": "shot at eye level, 50mm lens at f/2.8",
        "grade": "warm, cozy color grade",
    },
    "baking-counter": {
        "label": "Healthy baking on oak counter",
        "aspect": "1:1",
        "light": "right",
        "place": {"x": 0.40, "base": 0.79, "height": 0.54},
        "set": "a light oak kitchen counter with a soft linen cloth, a bright kitchen blurred behind",
        "props": (
            "a tray of freshly baked golden cupcakes, a glass bowl of white sweetener "
            "granules, a whisk with a little batter on it, two brown eggs, a scattering "
            "of almonds, light flour dust on the wood"
        ),
        "lighting": (
            "soft daylight from a window on the right, gentle soft shadows falling to "
            "the left"
        ),
        "camera": "shot from about 20 degrees above, 70mm lens at f/4",
        "grade": "bright, airy, warm color grade",
    },
    "coffee-infographic": {
        "label": "Infographic base, empty left half",
        "aspect": "1:1",
        "light": "right",
        "place": {"x": 0.70, "base": 0.82, "height": 0.58},
        "set": (
            "a pale stone counter against a warm beige plaster wall; the left half of "
            "the frame is clean empty wall and counter, kept clear for text"
        ),
        "props": "a cup of black coffee and one whole dried monk fruit, both on the right side",
        "lighting": (
            "hard sunlight from the upper right filtered through leaves outside the "
            "frame, crisp dappled leaf shadows across the wall and counter"
        ),
        "camera": "shot at eye level, 85mm lens at f/4",
        "grade": "warm natural color grade",
    },
    "aplus-banner": {
        "label": "A+ banner, wide golden counter",
        "aspect": "16:9",
        "light": "left",
        "place": {"x": 0.74, "base": 0.84, "height": 0.62},
        "set": (
            "a bright kitchen counter at golden hour; the left two-thirds is softly "
            "blurred counter and window light, kept clean for headline text"
        ),
        "props": (
            "on the right side: a plate of cookies, a cup of tea, a bowl of white "
            "sweetener granules and two monk fruits with leaves"
        ),
        "lighting": (
            "low warm sun from the left, long soft shadows to the right, a warm rim "
            "light on object edges"
        ),
        "camera": "35mm lens at f/5.6, eye level",
        "grade": "warm golden color grade",
    },
}


def product_block(p):
    return (
        f"Use the attached image as the exact product reference: {p['description']}. "
        f"Keep it identical: {p['design']}, same logo, same text, same layout and "
        f"proportions. Do not redesign, retype or add any text. It is "
        f"{p['materials']}."
    )


def prompt_with_product(scene, p):
    s = SCENES[scene]
    return " ".join([
        product_block(p),
        f"Create a photorealistic Amazon lifestyle photo. The product stands upright on "
        f"{s['set']}, as the sharpest and brightest object in the frame, with its front "
        f"label facing the camera. Props: {s['props']}; props stay secondary and some "
        f"are cropped at the frame edges.",
        f"Lighting: {s['lighting']}. {s['camera'][0].upper() + s['camera'][1:]}, focus on the product's logo. "
        f"{s['grade'].capitalize()}. Aspect ratio {s['aspect']}.",
        REALISM, AVOID,
    ])


def prompt_empty(scene):
    s = SCENES[scene]
    pl = s["place"]
    side = "left" if pl["x"] < 0.45 else "right" if pl["x"] > 0.55 else "center"
    return " ".join([
        f"Create a photorealistic Amazon lifestyle background photo: {s['set']}.",
        f"Props: {s['props']}.",
        f"Leave a clear, empty spot on the counter in the {side} part of the frame, "
        f"in the foreground, where a product pouch about half the frame tall will be "
        f"placed later. Nothing stands in that spot. There is no product, no package, "
        f"no pouch, no box and no bottle with a label anywhere in the image.",
        f"Lighting: {s['lighting']}. {s['camera'][0].upper() + s['camera'][1:]}. {s['grade'].capitalize()}. "
        f"Aspect ratio {s['aspect']}.",
        REALISM, AVOID,
    ])
