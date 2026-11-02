"""Remove background on hires PNGs, repair small enclosed holes, trim, save 300 DPI."""
import sys, numpy as np; sys.path.insert(0, "src")
from recraft import remove_background, download
from PIL import Image
from scipy import ndimage

def repair_and_trim(src_rgb, cut_path, out_path, max_hole_frac=0.004, margin=60):
    rgb = np.array(Image.open(src_rgb).convert("RGB"))
    rgba = np.array(Image.open(cut_path).convert("RGBA"))
    a = rgba[..., 3]
    solid = a > 128
    holes = ndimage.binary_fill_holes(solid) & ~solid
    lab, n = ndimage.label(holes)
    limit = max_hole_frac * a.size; fixed = 0
    for i, size in enumerate(ndimage.sum(holes, lab, range(1, n + 1)), 1):
        if size < limit:
            m = ndimage.binary_dilation(lab == i, iterations=3)
            rgba[m, :3] = rgb[m]; rgba[m, 3] = 255; fixed += 1
    im = Image.fromarray(rgba)
    bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    bb = (max(bb[0]-margin, 0), max(bb[1]-margin, 0), min(bb[2]+margin, im.width), min(bb[3]+margin, im.height))
    im.crop(bb).save(out_path, dpi=(300, 300))
    return fixed, n

if __name__ == "__main__":
    for name in sys.argv[1:]:
        u, _ = remove_background(f"hires/{name}.png"); download(u, f"hires/{name}_cut.png")
        print(name, "holes fixed/found:", repair_and_trim(f"hires/{name}.png", f"hires/{name}_cut.png", f"final/{name}.png"))
