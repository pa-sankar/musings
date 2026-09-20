"""
Hero image prep tool for Musings articles.

Converts a raw PNG (e.g. an AI-generated image) into the site's hero image
convention: {slug}-Image.jpg, 1200x630 JPEG, with optional watermark/logo
removal via clone-fill from a nearby source patch.

Usage:
    python Scripts/process_hero_image.py <input.png> <output.jpg> [options]

Options:
    --width WxH           target size (default 1200x630)
    --patch x0,y0,x1,y1    bounding box (in source pixels) to clone-fill,
                           e.g. a watermark/logo corner. Repeatable.
    --patch-source dx,dy   offset (in source pixels) to sample the fill
                           patch from, relative to each --patch box.
                           Default: shift straight up by 3x the patch height.
    --quality N            JPEG quality (default 90)

Example (removing a bottom-right sparkle logo before cropping to 1200x630):
    python Scripts/process_hero_image.py raw.png slug-Image.jpg \\
        --patch 1224,616,1287,679
"""

import argparse
from PIL import Image, ImageFilter


def clone_fill(im, box, source_offset=None, margin=8, blur=1.0):
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
    p.add_argument("--patch", action="append", default=[], help="x0,y0,x1,y1 region to clone-fill")
    p.add_argument("--patch-source", default=None, help="dx,dy offset to sample fill from")
    p.add_argument("--quality", type=int, default=90)
    args = p.parse_args()

    target_w, target_h = (int(v) for v in args.size.lower().split("x"))
    source_offset = None
    if args.patch_source:
        source_offset = tuple(int(v) for v in args.patch_source.split(","))

    im = Image.open(args.input).convert("RGB")

    for patch_arg in args.patch:
        box = tuple(int(v) for v in patch_arg.split(","))
        clone_fill(im, box, source_offset=source_offset)

    im = crop_to_aspect(im, target_w, target_h)
    im.save(args.output, quality=args.quality)
    print(f"Saved {args.output} ({target_w}x{target_h})")


if __name__ == "__main__":
    main()
