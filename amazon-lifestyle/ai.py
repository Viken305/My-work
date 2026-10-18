"""Thin wrappers around Nano Banana (Gemini) and ChatGPT (OpenAI) image models.

Keys come from the environment: GEMINI_API_KEY (or GOOGLE_API_KEY) and
OPENAI_API_KEY. Model names can be overridden with GEMINI_IMAGE_MODEL and
OPENAI_IMAGE_MODEL when newer versions come out.
"""
import base64
import io
import os

from PIL import Image

GEMINI_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
OPENAI_MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")

OPENAI_SIZES = {"1:1": "1024x1024", "16:9": "1536x1024", "4:5": "1024x1536", "9:16": "1024x1536"}


def _need(var, *alts):
    for v in (var, *alts):
        if os.environ.get(v):
            return os.environ[v]
    raise SystemExit(f"Set {var} in your environment first (export {var}=...).")


def gemini(prompt, images=(), aspect="1:1"):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=_need("GEMINI_API_KEY", "GOOGLE_API_KEY"))
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=aspect),
    )
    resp = client.models.generate_content(
        model=GEMINI_MODEL, contents=[*images, prompt], config=config
    )
    for part in resp.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            return Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
    raise RuntimeError("Gemini returned no image. Text reply: " + (resp.text or "none"))


def openai_image(prompt, image_path=None, aspect="1:1"):
    from openai import OpenAI

    client = OpenAI(api_key=_need("OPENAI_API_KEY"))
    size = OPENAI_SIZES.get(aspect, "1024x1024")
    if image_path:
        with open(image_path, "rb") as f:
            resp = client.images.edit(
                model=OPENAI_MODEL, image=f, prompt=prompt, size=size,
                quality="high", input_fidelity="high",
            )
    else:
        resp = client.images.generate(model=OPENAI_MODEL, prompt=prompt, size=size, quality="high")
    img = Image.open(io.BytesIO(base64.b64decode(resp.data[0].b64_json))).convert("RGB")
    return crop_to_aspect(img, aspect)


def crop_to_aspect(img, aspect):
    w, h = img.size
    a, b = (int(x) for x in aspect.split(":"))
    target = a / b
    if abs(w / h - target) < 0.01:
        return img
    if w / h > target:
        nw = int(h * target)
        return img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    nh = int(w / target)
    return img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
