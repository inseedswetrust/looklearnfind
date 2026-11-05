#!/usr/bin/env python3
"""Prepare the Daily Signal chapter and teaser photographs: high-resolution landscape images (16:9, or 3:2 for the leadership composition), never upscaled.

Sources are real, rights-recorded photographs already in assets/politics_src/ (see docs/politics/brand/ASSET_MANIFEST.csv). The Michigan State Capitol is fetched at
2400 px from Wikimedia Commons (CC BY-SA 2.0, w_lemay). Output: static/img/politics/chapters/<name>-1600.jpg and <name>-800.jpg (the leadership composition is 3:2).
The money chapter gets one directional duochrome plane (geometry on part of the picture); the others stay natural colour. Usage: python tools/politics/prepare_chapter_images.py
"""
import io
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets" / "politics_src"
OUT = ROOT / "static" / "img" / "politics" / "chapters"
UA = {"User-Agent": "LLF-election-desk/1.0 (hello@looklearnfind.com)"}


def crop_ratio(im, box, ratio=16 / 9):
    """Crop to the given aspect inside `box` (left, top, right, bottom), centred, never larger than the source."""
    l, t, r, b = box
    w, h = r - l, b - t
    if w / h > ratio:
        nw = int(h * ratio)
        l += (w - nw) // 2
        w = nw
    else:
        nh = int(w / ratio)
        t += (h - nh) // 2
        h = nh
    return im.crop((l, t, l + w, t + h))


def save(im, name, ratio=16 / 9):
    OUT.mkdir(parents=True, exist_ok=True)
    for w in (1600, 800):
        w = min(w, im.width)                # never upscale
        o = im.resize((w, round(w / ratio)), Image.LANCZOS)
        o.save(OUT / f"{name}-{w if w in (1600, 800) else 1600}.jpg", quality=86, optimize=True)
    print(name, im.size)


def duochrome(im):
    """Selective duochrome: monochrome with one directional teal plane across part of the picture."""
    g = ImageOps.colorize(ImageOps.grayscale(im), black=(26, 31, 33), white=(246, 243, 235)).convert("RGB")
    w, h = g.size
    plane = Image.new("RGB", g.size, (22, 167, 155))
    mask = Image.new("L", g.size, 0)
    ImageDraw.Draw(mask).polygon([(int(w * .46), 0), (int(w * .78), 0), (int(w * .52), h), (int(w * .2), h)], fill=235)
    tinted = ImageChops.multiply(g, plane)
    return Image.composite(tinted, g, mask)


def commons(title, width=2400):
    q = urllib.parse.urlencode(dict(action="query", titles=title, prop="imageinfo", iiprop="url|size", iiurlwidth=width, format="json"))
    j = json.loads(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + q, headers=UA), timeout=60).read())
    ii = list(j["query"]["pages"].values())[0]["imageinfo"][0]
    return Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(ii["thumburl"], headers=UA), timeout=120).read())).convert("RGB"), ii


def main():
    t = SRC / "teasers"
    k = Image.open(t / "kansas-capitol.jpg").convert("RGB")                     # 2400x1800
    save(crop_ratio(k, (0, 200, k.width, k.height)), "geography")
    g = Image.open(t / "grocery-prices.jpg").convert("RGB")                     # 2400x1350 with a black bar across the top
    save(crop_ratio(g, (0, int(g.height * 0.15), g.width, g.height)), "voters")
    d = Image.open(t / "dollar-bill.jpg").convert("RGB")                        # 2400x1046
    save(duochrome(crop_ratio(d, (0, 0, d.width, d.height))), "money")
    mi, ii = commons("File:Michigan State Capitol, Capitol Avenue, Lansing, MI - 54383520410.jpg")
    mi.save(SRC / "teasers" / "michigan-capitol-2400.jpg", quality=92)
    save(crop_ratio(mi, (0, int(mi.height * 0.05), mi.width, mi.height)), "states")
    lead = Image.open(ROOT / "static" / "img" / "politics" / "leadership-composite.jpg").convert("RGB")      # 1500x1000, 3:2, built from the real portraits
    OUT.mkdir(parents=True, exist_ok=True)
    lead.save(OUT / "leadership-1500.jpg", quality=88, optimize=True)
    lead.resize((750, 500), Image.LANCZOS).save(OUT / "leadership-750.jpg", quality=86, optimize=True)
    print("leadership", lead.size, "| michigan source", ii["width"], "x", ii["height"])


if __name__ == "__main__":
    main()
