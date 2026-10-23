#!/usr/bin/env python3
"""Fetch and parse the Florida Division of Elections qualified candidate lists (stdlib only).

    python3 tools/elections/fetch_fl_roster.py

Writes data/elections/FL/roster.json (parsed) and captures/*.html (raw, hashed).
Scope: governor, U.S. Senate, U.S. House. Status 'Qualified' (includes write-ins and unopposed).
"""
import json, re, hashlib, datetime, urllib.request, html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "elections" / "FL"
CAP = OUT / "captures"
CAP.mkdir(parents=True, exist_ok=True)
BASE = "https://dos.elections.myflorida.com/candidates/"
SOURCES = {
    "gov": BASE + "CanList.asp?OfficeCode=GOV&elecid=20261103-GEN",
    "fed": BASE + "CanList.asp?CountyCode=ALL&OfficeGroup=ALL&Party=ALL&StatusCode=ALL&cantype=FED&elecID=20261103-GEN&sortby=OFF",
}
UA = {"User-Agent": "Mozilla/5.0 (LLF election desk; contact hello@looklearnfind.com)"}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
        return r.read()

def cells(row):
    return [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).replace("\xa0", " ").strip()
            for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, flags=re.S)]

def parse_name(raw):
    inc = "*Incumbent" in raw
    raw = raw.replace("*Incumbent", "").strip()
    m = re.match(r"^(.*?)\s*\(([A-Z]{3})\)\s*(?:/\s*(.*))?$", raw)
    if not m:
        return None
    last_first, party, rn = m.group(1).strip(), m.group(2), (m.group(3) or "").strip()
    last, _, first = last_first.partition(",")
    name = f"{first.strip()} {last.strip()}".strip()
    rm = None
    if rn:
        l2, _, f2 = rn.partition(",")
        rm = f"{f2.strip()} {l2.strip()}".strip()
    return {"name": re.sub(r"\s+", " ", name), "party_code": party, "running_mate": rm, "incumbent": inc}

def rows_with_links(page):
    out = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", page, flags=re.S):
        link = re.search(r"CanDetail\.asp\?account=(\d+)", r)
        out.append((cells(r), link.group(1) if link else None))
    return out

def main():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = {"captured_at_utc": now, "sources": {}, "governor": [], "senate": [], "house": {}}
    pages = {}
    for key, url in SOURCES.items():
        raw = get(url)
        (CAP / f"fl_{key}_{now[:10]}.html").write_bytes(raw)
        result["sources"][key] = {"url": url, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        pages[key] = raw.decode("latin-1")
    # governor
    for c, acct in rows_with_links(pages["gov"]):
        if len(c) == 4 and c[0] not in ("Candidate",):
            p = parse_name(c[0])
            if p:
                result["governor"].append({**p, "status": c[1], "primary": c[2].strip(), "state_account": acct})
    # federal: senate block first (3 columns), then district block (4/5 columns)
    fed = pages["fed"]
    heads = [(m.start(), re.sub(r"\s+", " ", m.group(1)).strip()) for m in re.finditer(r"face=arial><b>\s*([^<]+?)\s*</b>", fed)]
    def section(name):
        for i, (pos, h) in enumerate(heads):
            if h == name:
                end = heads[i + 1][0] if i + 1 < len(heads) else len(fed)
                return fed[pos:end]
        raise SystemExit(f"section not found: {name}")
    result["sections_found"] = [h for _, h in heads]
    sen_page, house_page = section("United States Senator"), section("United States Representative")
    for c, acct in rows_with_links(sen_page):
        if len(c) == 4 and c[0] != "Candidate":
            p = parse_name(c[0])
            if p:
                result["senate"].append({**p, "status": c[1], "primary": c[2].strip(), "state_account": acct})
    dist = None
    for c, acct in rows_with_links(house_page):
        if len(c) == 5 and c[0] != "District":
            if c[0].isdigit():
                dist = int(c[0])
            p = parse_name(c[1])
            if p and dist is not None:
                result["house"].setdefault(str(dist), []).append({**p, "status": c[2], "primary": c[3].strip(), "state_account": acct})
    for k in result["house"]:
        result["house"][k] = [x for x in result["house"][k]]
    result["governor_qualified"] = [x for x in result["governor"] if x["status"] == "Qualified"]
    (OUT / "roster.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print({"governor_rows": len(result["governor"]), "governor_qualified": len(result["governor_qualified"]),
           "senate": len(result["senate"]), "districts": len(result["house"]),
           "house_candidates": sum(len(v) for v in result["house"].values())})

if __name__ == "__main__":
    main()
