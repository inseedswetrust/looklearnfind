#!/usr/bin/env python3
"""Prepare the images supplied with the approved homepage mockup (docs/politics/brand/edition-001/assets/) for the site.

The supplied files are small crops of the mockup. Some contain slivers of the mockup's own text (headline fragments, the top-right section labels). This script
only crops those slivers away (or paints them out of plain paper), upscales with a high-quality filter and saves JPEGs to static/img/politics/supplied/. The
originals stay untouched. No image is generated or redrawn. Usage: python tools/politics/prepare_supplied_images.py
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "politics" / "brand" / "edition-001" / "assets"
OUT = ROOT / "static" / "img" / "politics" / "supplied"

# name -> (source file, crop box left, top, right, bottom, upscale factor)
JOBS = {
    "hero": ("hero_capitol_composite_reference.jpg", (50, 0, 555, 281), 3),
    "leadership": ("jeffries_schumer_composite_reference.jpg", (0, 0, 579, 315), 3),
    "vote": ("vote_state_tile_reference.jpg", (72, 12, 165, 186), 4),
    "money": ("money_tile_reference.jpg", (64, 12, 166, 187), 4),
    "record": ("state_record_tile_reference.jpg", (60, 10, 140, 180), 4),
    "signals": ("election_signals_reference.jpg", (24, 24, 302, 163), 3),
}


def paint_out_labels(im):
    """The hero crop carries the mockup's small section labels at the top right, over plain paper. Remove only those dark text pixels by inpainting."""
    a = np.asarray(im.convert("RGB"))
    h, w = a.shape[:2]
    x0, y0, x1, y1 = int(w * 0.57), 0, w, int(h * 0.24)
    roi = cv2.cvtColor(a[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY)
    mask = np.zeros(a.shape[:2], np.uint8)
    mask[y0:y1, x0:x1] = (roi < 110).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    out = cv2.inpaint(cv2.cvtColor(a, cv2.COLOR_RGB2BGR), mask, 4, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for key, (fname, box, k) in JOBS.items():
        im = Image.open(SRC / fname).convert("RGB")
        if key == "hero":
            im = paint_out_labels(im)
        im = im.crop(box)
        im = im.resize((im.width * k, im.height * k), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
        im.save(OUT / f"{key}.jpg", quality=90, optimize=True)
        print(key, im.size)


if __name__ == "__main__":
    main()
