"""Remove background (Recraft), then locally: repair falsely-removed paint, keep real gaps,
remove white fringe (alpha decontamination), trim, save 300 DPI."""
import sys, numpy as np; sys.path.insert(0, "src")
from PIL import Image
from scipy import ndimage

BG = 255.0

def repair_and_trim(src_rgb, cut_path, out_path, margin=60, band=3, paint_diff=25, white_reach=6):
    rgb = np.array(Image.open(src_rgb).convert("RGB")).astype(np.float32)
    a = np.array(Image.open(cut_path).convert("RGBA"))[..., 3].astype(np.float32)
    diff = np.abs(rgb - BG).sum(-1)

    # 1) enclosed holes: fill only if the original pixels are paint, not white background
    solid = a > 128
    holes = ndimage.binary_fill_holes(solid) & ~solid
    lab, n = ndimage.label(holes)
    fixed = 0
    if n:
        means = ndimage.mean(diff, lab, range(1, n + 1))
        paint = np.zeros(n + 1, bool); paint[1:] = means >= paint_diff
        fill = paint[lab] & holes
        a[fill] = 255; fixed = int(paint.sum())

    # 1b) flood from the transparent outside through near-white pixels: removes white gaps
    #     between needles/fur and the bright upscaler ring, but keeps enclosed white paint
    near_white = diff < 36
    outside0 = a < 8
    m = near_white | outside0
    if white_reach is None:   # unlimited: for gappy foliage on pale paint-free areas
        reach = ndimage.binary_propagation(outside0, mask=m)
    else:                     # only a thin ring: protects white fur touching the edge
        reach = ndimage.binary_dilation(outside0, iterations=white_reach, mask=m)
    a[reach] = 0
    a = ndimage.grey_erosion(a, size=(3, 3))
    a = ndimage.uniform_filter(a, size=3)

    # 2) edge band: cap alpha by how far the pixel is from white (kills white halo)
    outside = a < 8
    edge = ndimage.binary_dilation(outside, iterations=band) & ~outside
    color_alpha = np.clip(diff / 110.0, 0, 1) * 255
    a[edge] = np.minimum(a[edge], color_alpha[edge])

    # 3) un-mix white from semi-transparent pixels
    al = (a / 255.0)[..., None]
    out = np.where(al > 0.02, (rgb - (1 - al) * BG) / np.maximum(al, 0.02), rgb)
    out = np.clip(out, 0, 255)

    im = Image.fromarray(np.dstack([out, a]).astype(np.uint8), "RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    bb = (max(bb[0]-margin, 0), max(bb[1]-margin, 0), min(bb[2]+margin, im.width), min(bb[3]+margin, im.height))
    im.crop(bb).save(out_path, dpi=(300, 300))
    return fixed, n
