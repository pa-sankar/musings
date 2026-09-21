"""
Hero image prep tool for Musings articles.

Converts a raw PNG (e.g. an AI-generated image) into the site's hero image
convention: {slug}-Image.jpg, 1200x630 JPEG, with optional watermark/logo
removal (e.g. the Gemini sparkle icon AI image generators tend to stamp in
a corner).

Two removal methods, pick per image:
  - "blur" (default) — feathered local Gaussian-blur infill. Best for
    smooth/gradient backgrounds (sky, out-of-focus table, soft shadow):
    blurs a padded region around the logo heavily, then blends it back in
    with a soft-edged radial mask so there's no visible seam. Only works
    well when the logo sits on a fairly smooth background — it can't
    invent texture that wasn't there.
  - "clone" — clone-stamp from a nearby source patch, then lightly blur
    the seam. Best for textured/detailed backgrounds (stone, wood grain,
    fabric) where a blurred patch would look like an obvious smudge.

Usage:
    python Scripts/process_hero_image.py <input.png> <output.jpg> [options]

Options:
    --size WxH             target size (default 1200x630)
    --patch x0,y0,x1,y1     bounding box (in source pixels) to remove,
                            e.g. a watermark/logo corner. Repeatable.
    --patch-method METHOD   "blur" (default) or "clone"
    --patch-source dx,dy    clone method only: offset (in source pixels)
                            to sample the fill patch from, relative to
                            each --patch box. Default: straight up by 3x
                            the patch height.
    --quality N             JPEG quality (default 90)

Tip for finding a logo's bounding box: crop a suspect corner and inspect
it, or scan for pixels that are brighter/greyer than the surrounding
background:
    python -c "
    from PIL import Image
    im = Image.open('raw.png').convert('RGB'); px = im.load()
    minx=miny=99999; maxx=maxy=0
    for y in range(600, 768):
        for x in range(1150, 1376):
            r,g,b = px[x,y]
            mx,mn = max(r,g,b), min(r,g,b)
            if mx > 100 and (mx-mn) < 25:
                minx,maxx = min(minx,x),max(maxx,x)
                miny,maxy = min(miny,y),max(maxy,y)
    print(minx,miny,maxx,maxy)
    "

Examples:
    # Smooth background (blur infill, default):
    python Scripts/process_hero_image.py raw.png slug-Image.jpg \\
        --patch 1233,625,1278,666

    # Textured background (clone-stamp instead):
    python Scripts/process_hero_image.py raw.png slug-Image.jpg \\
        --patch 1224,616,1287,679 --patch-method clone
"""

import argparse
from PIL import Image, ImageFilter


def blur_fill(im, box, margin=25, blur_radius=20, feather=8):
    """Feathered local-blur infill — no seam, needs a smooth background."""
    x0, y0, x1, y1 = box
    X0, Y0, X1, Y1 = x0 - margin, y0 - margin, x1 + margin, y1 + margin

    region = im.crop((X0, Y0, X1, Y1))
    blurred = region.filter(ImageFilter.GaussianBlur(blur_radius))

    w, h = region.size
    mask = Image.new("L", (w, h), 0)
    mpx = mask.load()
    cx, cy = w / 2, h / 2
    rx, ry = (x1 - x0) / 2 + feather, (y1 - y0) / 2 + feather
    for yy in range(h):
        for xx in range(w):
            dx, dy = (xx - cx) / rx, (yy - cy) / ry
            d = (dx * dx + dy * dy) ** 0.5
            if d <= 1:
                mpx[xx, yy] = 255
            elif d < 1.6:
                mpx[xx, yy] = int(255 * (1.6 - d) / 0.6)

    current = im.crop((X0, Y0, X1, Y1))
    blended = Image.composite(blurred, current, mask)
    im.paste(blended, (X0, Y0))


def clone_fill(im, box, source_offset=None, margin=8, blur=1.0):
    """Clone-stamp from a nearby patch — needs a textured background."""
    x0, y0, x1, y1 = box
    x0 -= margin
    y0 -= margin
    x1 += margin
    y1 += margin
    bw, bh = x1 - x0, y1 - y0

    if source_offset is None:
        dx, dy = 0, -3 * bh
    else:
        dx, dy = source_offset

    src = im.crop((x0 + dx, y0 + dy, x0 + dx + bw, y0 + dy + bh))
    im.paste(src, (x0, y0))

    pad = 6
    region = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)
    patch = im.crop(region).filter(ImageFilter.GaussianBlur(blur))
    im.paste(patch, region[:2])


def crop_to_aspect(im, target_w, target_h):
    w, h = im.size
    target_ratio = target_w / target_h
    src_ratio = w / h

    if src_ratio > target_ratio:
        new_w = round(h * target_ratio)
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    else:
        new_h = round(w / target_ratio)
        top = (h - new_h) // 2
        im = im.crop((0, top, w, top + new_h))

    return im.resize((target_w, target_h), Image.LANCZOS)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--width-height", "--size", dest="size", default="1200x630")
    p.add_argument("--patch", action="append", default=[], help="x0,y0,x1,y1 region to remove")
    p.add_argument("--patch-method", choices=["blur", "clone"], default="blur")
    p.add_argument("--patch-source", default=None, help="clone method: dx,dy offset to sample fill from")
    p.add_argument("--quality", type=int, default=90)
    args = p.parse_args()

    target_w, target_h = (int(v) for v in args.size.lower().split("x"))
    source_offset = None
    if args.patch_source:
        source_offset = tuple(int(v) for v in args.patch_source.split(","))

    im = Image.open(args.input).convert("RGB")

    for patch_arg in args.patch:
        box = tuple(int(v) for v in patch_arg.split(","))
        if args.patch_method == "clone":
            clone_fill(im, box, source_offset=source_offset)
        else:
            blur_fill(im, box)

    im = crop_to_aspect(im, target_w, target_h)
    im.save(args.output, quality=args.quality)
    print(f"Saved {args.output} ({target_w}x{target_h})")


if __name__ == "__main__":
    main()
