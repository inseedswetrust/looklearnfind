#!/usr/bin/env python3
"""Find lawful portraits on Wikimedia Commons for roster candidates; record license + credit per image.

    python3 tools/elections/fetch_portraits.py FL

For each candidate: find the person's Wikipedia article (must mention the state and an elected-office/candidate word), take the lead image,
read its Commons license metadata, and keep it only if the license is public domain, CC0 or CC BY / CC BY-SA. Everyone else gets the
neutral monogram card. Output: static/img/elections/portraits/<id>.jpg (<=480px wide), data/elections/<ST>/portraits.json (credit table).
Candidates are never matched on name alone: the article text is checked against state and office words; the match is listed for human review.
"""
import sys, json, re, unicodedata, urllib.request, urllib.error, urllib.parse, time, html
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ST = sys.argv[1].upper()
STATE = {"FL": "Florida", "MI": "Michigan", "IL": "Illinois", "NY": "New York", "NJ": "New Jersey"}[ST]
UA = {"User-Agent": "LLF-election-desk/1.0 (hello@looklearnfind.com)"}
OK = re.compile(r"^(pd|public domain|cc0|cc[- ]by|cc[- ]by[- ]sa|attribution)", re.I)
def api(base, **q):
    q["format"] = "json"
    for attempt in range(5):               # Wikimedia answers 503 when asked too fast: back off and retry
        try:
            with urllib.request.urlopen(urllib.request.Request(base + "?" + urllib.parse.urlencode(q), headers=UA), timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as ex:
            if ex.code not in (429, 503) or attempt == 4:
                raise
            time.sleep(4 * (attempt + 1))
def wp(**q): return api("https://en.wikipedia.org/w/api.php", **q)
def cm(**q): return api("https://commons.wikimedia.org/w/api.php", **q)

def find(name, office):
    base = re.sub(r"\b(Jr|Sr|II|III|IV)\.?$", "", name.replace('"', "")).strip()
    base = re.sub(r"\s+", " ", re.sub(r'\b[A-Z]\.\s', "", base))
    for qtxt in (f'"{base}" {STATE} politician', f'{base} {STATE} congress'):
        j = wp(action="query", list="search", srsearch=qtxt, srlimit=3)
        for s in j["query"]["search"]:
            t = s["title"]
            last, first = base.split()[-1].lower(), base.split()[0].lower()
            tt = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
            if last not in tt or first not in tt:
                continue
            p = wp(action="query", prop="pageimages|extracts", titles=t, piprop="original|name", exintro=1, explaintext=1, exchars=600)
            pg = list(p["query"]["pages"].values())[0]
            ext = pg.get("extract", "")
            if STATE in ext and re.search(r"politician|member of the|candidate|congress|senator|governor|representative|lawyer|attorney general", ext, re.I) and pg.get("pageimage"):
                return t, ext[:160], pg["pageimage"]
    return None

def license_of(fname):
    j = cm(action="query", titles="File:" + fname, prop="imageinfo", iiprop="extmetadata|url", iiurlwidth=480)
    pg = list(j["query"]["pages"].values())[0]
    ii = pg.get("imageinfo", [{}])[0]
    md = ii.get("extmetadata", {})
    lic = md.get("LicenseShortName", {}).get("value", "")
    return lic, re.sub(r"<[^>]+>", "", html.unescape(md.get("Artist", {}).get("value", ""))).strip(), ii.get("thumburl"), ii.get("descriptionurl"), md.get("UsageTerms", {}).get("value", "")

cands = json.loads((ROOT / f"data/elections/{ST}/candidates.json").read_text(encoding="utf-8"))["candidates"]
extra = ROOT / f"data/elections/{ST}/extra_people.json"          # people a story needs who are not on the November roster (defeated primary candidates, retirees)
if extra.exists():
    cands += json.loads(extra.read_text(encoding="utf-8"))
outdir = ROOT / "static/img/elections/portraits"
import os
ONLY = [x.strip() for x in os.environ.get("LLF_ONLY", "").split(",") if x.strip()]      # re-run just these names and merge into the existing credit table
logf = ROOT / f"data/elections/{ST}/portraits.json"
log = json.loads(logf.read_text(encoding="utf-8")) if ONLY and logf.exists() else {}
for c in cands:
    c["id"] = re.sub(r"[^A-Za-z0-9._-]", "_", c["id"])             # file-safe id (quotes in names broke Windows file names)
    if ONLY and c["name"] not in ONLY:
        continue
    if c["party_code"] not in ("DEM", "REP") and not c["incumbent"]:
        continue                       # minor-party and write-in candidates: monogram unless an editor adds a licensed photo by hand
    try:
        hit = find(c["name"], c["office"])
        if not hit:
            log[c["id"]] = {"name": c["name"], "result": "no confident Wikipedia match"}
            continue
        title, ext, fname = hit
        lic, artist, thumb, page, terms = license_of(fname)
        if not OK.match(lic):
            log[c["id"]] = {"name": c["name"], "wikipedia": title, "file": fname, "license": lic, "result": "license not accepted"}
            continue
        data = urllib.request.urlopen(urllib.request.Request(thumb, headers=UA), timeout=60).read()
        (outdir / f"{c['id']}.jpg").write_bytes(data)
        log[c["id"]] = {"name": c["name"], "wikipedia": title, "extract": ext, "file": fname, "license": lic, "credit": artist or "Wikimedia Commons", "source_page": page, "result": "ok", "bytes": len(data)}
    except Exception as ex:
        log[c["id"]] = {"name": c["name"], "result": f"error {ex}"}
    time.sleep(1.0)
(ROOT / f"data/elections/{ST}/portraits.json").write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
import collections
print(collections.Counter(v["result"] for v in log.values()))
