#!/usr/bin/env python3
"""Fetch the rights-clear photographs used by the Daily Signal teasers and the hi-res Capitol hero source from Wikimedia Commons, record their licence and credit,
and write web derivatives. Only public domain, CC0, CC BY and CC BY-SA files are accepted. Nothing is regenerated or retouched beyond crop and resize.

Outputs: assets/politics_src/teasers/<key>.jpg (originals, 2400px wide), static/img/politics/teasers/<key>.jpg (1200x800 crops),
assets/politics_src/teaser_sources.json (licence, creator, page, date downloaded), assets/politics_src/capitol_hi.jpg.
Usage: python tools/politics/fetch_teaser_photos.py
"""
import datetime
import html
import io
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets" / "politics_src"
OUT = ROOT / "static" / "img" / "politics" / "teasers"
UA = {"User-Agent": "LLF-election-desk/1.0 (hello@looklearnfind.com)"}
OK = re.compile(r"(?i)^(public domain|pd\b|cc0|cc[- ]by(?:[- ]sa)?\b)")
strip = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()

# key, exact file title on Commons, crop (left, top, right, bottom fractions) to a 3:2 frame, what it illustrates
PICKS = [
    ("kansas-capitol", "File:Kansas State Capitol, 8th Avenue and Van Buren Street, Topeka, KS - 52391143299.jpg", (0.0, 0.18, 1.0, 0.18 + 0.667 * 3860 / 5147 * 1.0), "Teaser 02: the Kansas State Capitol, Topeka"),
    ("grocery-prices", None, None, "Teaser 03: vegetables and prices in a supermarket"),
    ("dollar-bill", "File:United States one dollar bill, obverse.jpg", (0.52, 0.0, 1.0, 0.0), "Teaser 04: detail of a U.S. one-dollar bill"),
]


def get(url, binary=True):
    d = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
    return d if binary else d.decode("utf-8")


def api(**q):
    q["format"] = "json"
    return json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(q), binary=False))


def info(title, width=2400):
    r = api(action="query", titles=title, prop="imageinfo", iiprop="url|size|extmetadata", iiurlwidth=width)
    ii = list(r["query"]["pages"].values())[0]["imageinfo"][0]
    em = ii["extmetadata"]
    return dict(title=title, page=ii["descriptionurl"], url=ii["thumburl"], orig=[ii["width"], ii["height"]], license=strip(em.get("LicenseShortName", {}).get("value")),
                creator=strip(em.get("Artist", {}).get("value")), date=strip(em.get("DateTimeOriginal", {}).get("value")), credit=strip(em.get("Credit", {}).get("value")))


def find(term, contains):
    r = api(action="query", generator="search", gsrsearch=term, gsrnamespace=6, gsrlimit=10)
    for p in r["query"]["pages"].values():
        if contains.lower() in p["title"].lower():
            return p["title"]
    raise SystemExit(f"not found: {term}")


def crop32(im, box):
    w, h = im.size
    l, t, r, b = box
    x0, x1 = int(l * w), int(r * w)
    cw = x1 - x0
    ch = int(cw * 2 / 3)
    y0 = int(t * h)
    if ch > h - y0:                      # the frame is shorter than 3:2 allows: shrink the crop width, keep it centred
        ch = h - y0
        new_cw = int(ch * 1.5)
        x0 += (cw - new_cw) // 2
        cw = new_cw
    return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((1200, 800), Image.LANCZOS)


def main():
    (SRC / "teasers").mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    for key, title, box, what in PICKS:
        if key == "kansas-capitol":
            title = find("Kansas State Capitol 8th Avenue and Van Buren Street Topeka", "Kansas State Capitol, 8th Avenue and Van Buren Street, Topeka, KS")
            # the wide 5147x3860 w_lemay photograph
            r = api(action="query", generator="search", gsrsearch="Kansas State Capitol 8th Avenue and Van Buren Street Topeka", gsrnamespace=6, gsrlimit=10, prop="imageinfo", iiprop="size")
            for p in r["query"]["pages"].values():
                ii = p["imageinfo"][0]
                if ii["width"] == 5147:
                    title = p["title"]
            box = (0.0, 0.12, 1.0, 0.12)
        elif key == "grocery-prices":
            title = find("Parsley for 99 cents and other vegetables in supermarket", "Parsley for 99 cents")
            box = (0.0, 0.15, 1.0, 0.15)      # the first 15 percent of this frame is a black bar
        i = info(title)
        if not OK.match(i["license"]):
            raise SystemExit(f"licence not accepted for {title}: {i['license']}")
        im = Image.open(io.BytesIO(get(i["url"]))).convert("RGB")
        im.save(SRC / "teasers" / f"{key}.jpg", quality=92)
        crop32(im, box).save(OUT / f"{key}.jpg", quality=84, optimize=True)
        i.update(key=key, illustrates=what, downloaded=datetime.date.today().isoformat())
        out[key] = i
        print(key, i["license"], i["creator"][:30], i["orig"])
    # hi-res Capitol for the hero crop (same public-domain file as the existing hero)
    cap = info("File:Capitol Building Full View.jpg", 4800)
    (SRC / "capitol_hi.jpg").write_bytes(get(cap["url"]))
    out["capitol_hi"] = dict(cap, key="capitol_hi", illustrates="Hero source (hi-res)", downloaded=datetime.date.today().isoformat())
    (SRC / "teaser_sources.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
