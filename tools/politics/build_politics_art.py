#!/usr/bin/env python3
"""Build the Politics homepage art derivatives from the recorded source photographs (docs/politics/brand/ASSET_MANIFEST.csv).

Sources (assets/politics_src/, all public domain, see sources.json): jeffries.jpg, schumer.jpg, capitol_full.jpg.
Outputs (static/img/politics/):
  capitol-cut.png       the Capitol, monochrome, sky made transparent so the dome can cross a teal plane (CSS places the plane)
  jeffries-cutout.png   real official portrait, subject extracted, narrow irregular newspaper-paper edge, face unchanged
  schumer-cutout.png    same
The faces are never regenerated, retouched or recoloured beyond the monochrome treatment; only the background is removed.
Deterministic (fixed random seed). Usage: python tools/politics/build_politics_art.py [--debug]
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
SRC, OUT = ROOT / "assets" / "politics_src", ROOT / "static" / "img" / "politics"
PAPER = (246, 243, 234)
rng = np.random.default_rng(20261105)


def grabcut(img, rect, iters=7, hint=None):
    h, w = img.shape[:2]
    mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    x, y, rw, rh = rect
    mask[y:y + rh, x:x + rw] = cv2.GC_PR_FGD
    if hint is not None:
        hint(mask)
    bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(img, mask, None, bgd, fgd, iters, cv2.GC_INIT_WITH_MASK)
    m = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:                                   # keep the largest component only
        m = np.where(lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA])), 255, 0).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    ff = m.copy(); cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 255)
    m = m | cv2.bitwise_not(ff)                     # fill interior holes (tie, hands)
    return cv2.GaussianBlur(m, (5, 5), 0)


def paper_edge(subject_rgba_mask, width_px, rough=0.26):
    """Irregular warm-white perimeter: dilate by a noisy radius, then roughen the boundary slightly."""
    h, w = subject_rgba_mask.shape
    d = cv2.dilate(subject_rgba_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * width_px + 1, 2 * width_px + 1)))
    noise = rng.normal(0, 1, (h // 18 + 2, w // 18 + 2)).astype(np.float32)
    noise = cv2.resize(noise, (w, h), interpolation=cv2.INTER_CUBIC)
    soft = cv2.GaussianBlur(d, (0, 0), 3).astype(np.float32) / 255.0
    edge = np.where(soft >= 0.999, True, (soft + rough * noise) > 0.5)      # roughen the outline only; the interior is never perforated
    e8 = (edge * 255).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(e8)
    if n > 1:                                   # no stray specks outside the paper edge
        e8 = np.where(lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA])), 255, 0).astype(np.uint8)
    return e8


def cutout(name, rect, mono, hint=None, out_w=900, edge=9, crop=None):
    im = cv2.imread(str(SRC / f"{name}.jpg"))
    s = 900 / im.shape[1]
    sm = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    rr = tuple(int(v * s) for v in rect)
    subj = grabcut(sm, rr, hint=(lambda m: hint(m, s)) if hint else None)
    big = cv2.resize(subj, (im.shape[1], im.shape[0]), interpolation=cv2.INTER_CUBIC)
    big = cv2.threshold(cv2.GaussianBlur(big, (0, 0), 2), 127, 255, cv2.THRESH_BINARY)[1]
    ew = max(3, int(edge * im.shape[1] / 1600 * 2.2))
    paper = paper_edge(big, ew)
    rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    if mono:
        g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        g = cv2.createCLAHE(1.6, (8, 8)).apply(g)
        rgb = cv2.cvtColor(g, cv2.COLOR_GRAY2RGB)
    canvas = np.zeros(rgb.shape, np.uint8)
    canvas[:] = PAPER
    alpha = cv2.GaussianBlur(big, (0, 0), 1.1).astype(np.float32) / 255
    out = canvas * (1 - alpha[..., None]) + rgb * alpha[..., None]
    a = cv2.GaussianBlur(paper, (0, 0), 1.0)
    rgba = np.dstack([out.astype(np.uint8), a])
    ys, xs = np.where(a > 8)
    pad = 6
    y0, y1, x0, x1 = max(ys.min() - pad, 0), min(ys.max() + pad, a.shape[0]), max(xs.min() - pad, 0), min(xs.max() + pad, a.shape[1])
    if crop:
        y1 = min(y1, int(crop * rgba.shape[0]))
    img = Image.fromarray(rgba[y0:y1, x0:x1], "RGBA")
    img.thumbnail((out_w, out_w * 2), Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f"{name}-cutout.png", optimize=True)
    return img.size


def capitol():
    hi = SRC / "capitol_hi.jpg"
    im = Image.open(hi if hi.exists() else SRC / "capitol_full.jpg").convert("RGB")
    w, h = im.size
    im = im.crop((int(w * .385), int(h * .0), int(w * .80), int(h * .66)))
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    sky = (b > r + 45) & (b > g + 25)                      # saturated blue: the sky
    mask = (~sky).astype(np.float32)
    mask = cv2.GaussianBlur(mask, (0, 0), 1.2)
    mask = cv2.erode(mask, np.ones((2, 2), np.uint8))
    lum = (0.3 * r + 0.59 * g + 0.11 * b)
    lum = np.clip((lum - 18) * 1.18, 0, 255)
    hh = mask.shape[0]
    fade = np.clip((np.arange(hh)[:, None] - hh * 0.88) / (hh * 0.12), 0, 1)   # the lawn dissolves into the paper
    alpha = mask * (1 - fade)
    out = np.dstack([lum, lum, lum, alpha * 255]).astype(np.uint8)
    img = Image.fromarray(out, "RGBA")
    img.thumbnail((1700, 1700), Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / "capitol-cut.png", optimize=True)
    return img.size


def main():
    def jhint(m, s):                       # flag and backdrop are background; face and suit are foreground
        m[:, : int(120 * s)] = cv2.GC_BGD
        m[: int(120 * s), :] = cv2.GC_BGD
        m[:, int(1150 * s):] = cv2.GC_BGD
        m[int(520 * s): int(700 * s), int(560 * s): int(640 * s)] = cv2.GC_FGD
        m[int(1000 * s):, int(380 * s): int(1100 * s)] = cv2.GC_FGD

    def shint(m, s):
        m[:int(90 * s), :] = cv2.GC_BGD
        m[:, :int(280 * s)] = cv2.GC_BGD
        m[int(1050 * s): int(1330 * s), int(1740 * s):] = cv2.GC_BGD
        m[int(500 * s): int(640 * s), int(760 * s): int(900 * s)] = cv2.GC_FGD
        m[int(1500 * s):, int(700 * s): int(1700 * s)] = cv2.GC_FGD
        m[int(40 * s): int(500 * s), int(600 * s): int(1050 * s)] = cv2.GC_PR_FGD

    sizes = {"capitol": capitol(),
             "jeffries": cutout("jeffries", (150, 150, 1000, 1470), True, jhint, crop=0.70),
             "schumer": cutout("schumer", (300, 60, 1500, 1840), True, shint, crop=0.76)}
    print(sizes)


if __name__ == "__main__":
    main()
