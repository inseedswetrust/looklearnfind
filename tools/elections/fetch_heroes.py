#!/usr/bin/env python3
"""Download hero photographs from Wikimedia Commons with license + credit recorded in data/elections/hero_credits.json.

    python3 tools/elections/fetch_heroes.py
Only CC BY, CC BY-SA, CC0 and public-domain files are accepted. Credit and source URL are printed on the page where the image is used.
"""
import json, re, html, urllib.request, urllib.parse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
UA = {"User-Agent": "LLF-election-desk/1.0 (hello@looklearnfind.com)"}
WANT = {  # key -> (search text that finds the file, width)
    "fl-capitol": ("Old Florida State Capitol, Tallahassee, East view 20160711 1.jpg", 1800),
    "mi-capitol": ("Michigan State Capitol, Capitol Avenue, Lansing, MI - 54383520410", 1800),
    "us-capitol": ("Capitol Building Full View.jpg", 1800),
    "il-capitol": ("Gfp-illinois-springfield-capitol-and-sky.jpg", 1800),
}
def cm(**q):
    q["format"] = "json"
    return json.loads(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(q), headers=UA), timeout=60).read())
credits = {}
for key, (term, w) in WANT.items():
    j = cm(action="query", generator="search", gsrsearch=term, gsrnamespace=6, gsrlimit=1, prop="imageinfo", iiprop="extmetadata|url|size", iiurlwidth=w)
    p = list(j["query"]["pages"].values())[0]
    ii = p["imageinfo"][0]; md = ii["extmetadata"]
    lic = md.get("LicenseShortName", {}).get("value", "")
    assert re.match(r"(?i)(public domain|cc0|cc by)", lic), (key, lic)
    data = urllib.request.urlopen(urllib.request.Request(ii["thumburl"], headers=UA), timeout=90).read()
    (ROOT / "static/img/elections" / f"{key}.jpg").write_bytes(data)
    credits[key] = {"file": p["title"], "license": lic, "credit": re.sub(r"<[^>]+>", "", html.unescape(md.get("Artist", {}).get("value", ""))).strip() or "Wikimedia Commons",
                    "source_page": ii["descriptionurl"], "license_url": md.get("LicenseUrl", {}).get("value", ""), "bytes": len(data)}
    print(key, p["title"], lic, len(data))
(ROOT / "data/elections/hero_credits.json").write_text(json.dumps(credits, indent=1, ensure_ascii=False), encoding="utf-8")
