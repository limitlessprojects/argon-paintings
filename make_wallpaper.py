#!/usr/bin/env python3
"""Make a 16:9 desktop wallpaper from a 1200x1200 Argon painting.

Pads the square painting onto a larger canvas using the painting's own edge
colours (sampled left/right strips), so nothing is cropped away.

Usage:
    python3 make_wallpaper.py paintings/foo.webp wallpaper.png
    python3 make_wallpaper.py paintings/foo.webp wallpaper.png 2560 1440
"""
import sys
import os

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow required:  pip install pillow")


def edge_color(im, side):
    strip = (0, 0, 24, im.height) if side == "left" else (im.width - 24, 0, im.width, im.height)
    region = im.crop(strip).resize((1, 1), Image.LANCZOS)
    return region.getpixel((0, 0))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 1080

    im = Image.open(src).convert("RGB")
    canvas = Image.new("RGB", (w, h))
    # horizontal gradient between left-edge and right-edge colours
    l, r = edge_color(im, "left"), edge_color(im, "right")
    px = canvas.load()
    for x in range(w):
        t = x / (w - 1)
        col = tuple(round(l[c] + (r[c] - l[c]) * t) for c in range(3))
        for y in range(h):
            px[x, y] = col
    # center the painting, scaled to fit height
    scale = h / im.height
    if scale * im.width > w:
        scale = w / im.width
    art = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    canvas.paste(art, ((w - art.width) // 2, (h - art.height) // 2))
    out_ext = os.path.splitext(dst)[1].lower().lstrip(".")
    fmt = "PNG" if out_ext == "png" else "JPEG"
    canvas.save(dst, fmt, quality=92)
    print(f"{dst}  {canvas.width}x{canvas.height}")


if __name__ == "__main__":
    main()
