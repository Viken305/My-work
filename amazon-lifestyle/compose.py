"""Place a real product packshot into a scene photo so it looks shot there.

The label is never redrawn: we cut the product off its white background and
add what the eye checks for realism, all driven by one light direction:
  1. contact shadow: a thin, dark line where the base touches the surface
  2. ambient occlusion: a wider, soft darkening around the base
  3. cast shadow: the product's own silhouette, flattened onto the counter
     and thrown away from the light, sharper near the base, softer far away
  4. light match: the product takes on the scene's color temperature and is
     brighter on the side facing the light, with a soft rim on that edge
  5. grain: the same fine noise over everything so the cutout doesn't look
     cleaner than the photo around it
"""
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter


def cutout(img, tol=12, feather=1.2):
    """RGBA cutout of a product shot on a plain white background.

    Pixels close to white AND connected to the image border become
    transparent, so white areas inside the product (like a white label band)
    stay opaque.
    """
    if img.mode == "RGBA" and img.getextrema()[3][0] < 255:
        return trim(img)  # already has transparency
    rgb = np.asarray(img.convert("RGB")).astype(np.int16)
    near_white = (255 - rgb.min(axis=2)) <= tol
    mask = Image.fromarray(np.where(near_white, 255, 0).astype(np.uint8)).copy()  # own buffer, or floodfill is a no-op
    w, h = mask.size
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if mask.getpixel(seed) == 255:
            ImageDraw.floodfill(mask, seed, 128)
    alpha = np.where(np.asarray(mask) == 128, 0, 255).astype(np.uint8)
    a = Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(feather))
    out = img.convert("RGB").copy()
    out.putalpha(a)
    return trim(out)


def trim(rgba):
    bbox = rgba.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    return rgba.crop(bbox) if bbox else rgba


def _base_span(alpha):
    """Left/right x of the product's bottom edge (where it touches the surface)."""
    a = np.asarray(alpha) > 128
    rows = np.where(a.any(axis=1))[0]
    bottom = rows[-1]
    band = a[max(0, bottom - max(3, a.shape[0] // 40)): bottom + 1].any(axis=0)
    xs = np.where(band)[0]
    return int(xs[0]), int(xs[-1])


def _scene_tint(bg, box):
    """Average color of the scene around the product, normalized to gray = 1."""
    region = np.asarray(bg.crop(box).convert("RGB")).reshape(-1, 3).astype(np.float32)
    mean = region.mean(axis=0)
    return mean / mean.mean()


def light_match(prod, tint, light="left", tint_amount=0.35, falloff=0.16, rim=0.10):
    rgb = np.asarray(prod.convert("RGB")).astype(np.float32) / 255
    alpha = prod.getchannel("A")
    h, w = rgb.shape[:2]
    # warm/cool the product toward the scene's color
    t = 1 + (tint - 1) * tint_amount
    rgb = rgb * t
    # brighter on the side facing the light, darker on the far side
    ramp = np.linspace(1 + falloff / 2, 1 - falloff / 2, w)
    if light == "right":
        ramp = ramp[::-1]
    rgb = rgb * ramp[None, :, None]
    # slight top-to-bottom falloff: tops catch more light than bases
    rgb = rgb * np.linspace(1.03, 0.95, h)[:, None, None]
    # rim light along the lit edge: inside edge of the alpha, on the light side
    a = np.asarray(alpha).astype(np.float32) / 255
    inner = np.asarray(alpha.filter(ImageFilter.MinFilter(9))).astype(np.float32) / 255
    edge = np.clip(a - inner, 0, 1)
    edge = np.asarray(Image.fromarray((edge * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255
    side = np.linspace(1, 0, w) if light == "left" else np.linspace(0, 1, w)
    rgb = rgb + edge[..., None] * side[None, :, None] * rim
    out = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    out.putalpha(alpha)
    return out


def _shadow_layer(size, alpha, pos, light, length=0.45, spread=0.55, opacity=0.42):
    """Silhouette squashed onto the counter and sheared away from the light."""
    W, H = size
    x0, y0 = pos
    w, h = alpha.size
    sh_h = max(2, int(h * length))
    sil = alpha.resize((w, sh_h), Image.LANCZOS)
    shear = spread * (1 if light == "left" else -1)  # shadow falls away from light
    pad = int(abs(shear) * sh_h) + 4
    canvas = Image.new("L", (w + 2 * pad, sh_h), 0)
    canvas.paste(sil, (pad, 0))
    # affine maps output->input; shift top rows sideways, base row stays put
    sheared = canvas.transform(
        canvas.size, Image.AFFINE, (1, shear, -shear * sh_h, 0, 1, 0), resample=Image.BICUBIC
    )
    layer = Image.new("L", (W, H), 0)
    layer.paste(sheared, (x0 - pad, y0 + h - sh_h))
    # sharper near the base, softer further away
    near = layer.filter(ImageFilter.GaussianBlur(max(2, w * 0.012)))
    far = layer.filter(ImageFilter.GaussianBlur(max(6, w * 0.06)))
    grad = np.zeros((H, W), np.float32)
    top = max(0, y0 + h - sh_h)
    base = min(H, y0 + h)
    grad[top:base] = np.linspace(1, 0, base - top)[:, None]
    grad[:top] = 1
    blend = np.asarray(near) * (1 - grad) + np.asarray(far) * grad
    return Image.fromarray((blend * opacity).astype(np.uint8))


def _contact_layer(size, prod_alpha, pos, opacity_contact=0.85, opacity_ao=0.55):
    W, H = size
    x0, y0 = pos
    w, h = prod_alpha.size
    l, r = _base_span(prod_alpha)
    bw = r - l
    by = y0 + h
    layer = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(layer)
    # wide soft occlusion
    ao = Image.new("L", (W, H), 0)
    ImageDraw.Draw(ao).ellipse(
        [x0 + l - bw * 0.10, by - h * 0.03, x0 + r + bw * 0.10, by + h * 0.045], fill=int(255 * opacity_ao)
    )
    ao = ao.filter(ImageFilter.GaussianBlur(max(4, bw * 0.05)))
    # tight dark contact line
    d.ellipse([x0 + l + bw * 0.01, by - h * 0.008, x0 + r - bw * 0.01, by + h * 0.012], fill=int(255 * opacity_contact))
    layer = layer.filter(ImageFilter.GaussianBlur(max(1.5, bw * 0.008)))
    return ImageChops.lighter(layer, ao)


def _darken(img, mask, color=(25, 20, 18)):
    """Multiply-style darkening with a slightly warm shadow color, not pure black."""
    base = np.asarray(img.convert("RGB")).astype(np.float32)
    m = np.asarray(mask).astype(np.float32)[..., None] / 255
    shade = np.array(color, np.float32)
    out = base * (1 - m) + (base * 0.35 + shade * 0.65) * m
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def _reflection(prod, strength=0.2, length=0.18):
    """Faded mirror image under the product, for glossy surfaces like polished marble."""
    flip = prod.transpose(Image.FLIP_TOP_BOTTOM)
    w, h = flip.size
    fade = np.linspace(strength, 0, int(h * length))
    ramp = np.zeros(h, np.float32)
    ramp[: len(fade)] = fade
    a = np.asarray(flip.getchannel("A")).astype(np.float32) * ramp[:, None]
    flip = flip.filter(ImageFilter.GaussianBlur(max(1, w * 0.004)))
    flip.putalpha(Image.fromarray(a.astype(np.uint8)))
    return flip


def add_grain(img, sigma=3.0, seed=7):
    rng = np.random.default_rng(seed)
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    noise = rng.normal(0, sigma, a.shape[:2])[..., None]  # luminance grain
    return Image.fromarray(np.clip(a + noise, 0, 255).astype(np.uint8))


def place(bg, product, x=0.55, base=0.8, height=0.55, light="left", grain=3.0,
          shadow_length=0.45, shadow_spread=0.9, shadow_opacity=0.45, reflection=0.0):
    """Composite `product` (RGBA cutout) into `bg`.

    x: horizontal center of the product, 0..1
    base: vertical position of the product's bottom edge, 0..1
    height: product height as a fraction of the frame height
    light: "left" or "right", the side the key light comes from
    reflection: 0 for matte surfaces, ~0.15-0.25 for polished stone or glass
    """
    bg = bg.convert("RGB")
    W, H = bg.size
    ph = int(H * height)
    pw = int(product.width * ph / product.height)
    prod = product.resize((pw, ph), Image.LANCZOS)
    x0 = int(W * x - pw / 2)
    y0 = int(H * base - ph)
    box = (max(0, x0 - pw // 2), max(0, y0), min(W, x0 + pw + pw // 2), min(H, y0 + ph + ph // 4))
    prod = light_match(prod, _scene_tint(bg, box), light)
    alpha = prod.getchannel("A")

    shadow = _shadow_layer((W, H), alpha, (x0, y0), light, shadow_length, shadow_spread, shadow_opacity)
    contact = _contact_layer((W, H), alpha, (x0, y0))
    out = _darken(bg, ImageChops.lighter(shadow, contact))
    if reflection:
        refl = _reflection(prod, reflection)
        out.paste(refl, (x0, y0 + ph), refl)
    out.paste(prod, (x0, y0), prod)
    return add_grain(out, grain) if grain else out


def fit_amazon(img, longest=2000):
    """Resize so the longest side is `longest` px (Amazon recommends 2000)."""
    w, h = img.size
    s = longest / max(w, h)
    return img.resize((round(w * s), round(h * s)), Image.LANCZOS)
