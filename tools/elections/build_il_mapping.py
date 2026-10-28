#!/usr/bin/env python3
"""Verified candidate and race to TIP mapping for Illinois: one row per November candidate.

    python3 tools/elections/build_il_mapping.py        (run after join_tip.py with LLF_STATE=IL and fetch_portraits.py IL)

Columns say which sources agree. `isbe_verified` is always PENDING because the Illinois State Board of Elections site returns HTTP 403 to automated access; a person
with a browser ticks it. Nothing is guessed: a candidate with no TIP record has an empty TIP column and a stated gap.
"""
import csv, json, re, unicodedata, urllib.request, concurrent.futures as cf
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data/elections/IL"
J = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))
cands = J(D / "candidates.json")["candidates"]
entries = {(e["race_key"], e["display_name"]): e for e in J(D / "tip_export/race_entries.json")}
tip_cands = {c["fec_candidate_id"]: c for c in J(D / "tip_export/candidates.json")}
fec = J(D / "captures/fec_candidates_2026-10-28.json")
portraits = J(D / "portraits.json") if (D / "portraits.json").exists() else {}
roster = J(D / "roster.json")
norm = lambda n: [w for w in re.sub(r"[^a-z ]", " ", unicodedata.normalize("NFKD", n).lower()).split() if w not in ("jr", "sr", "ii", "iii")]

def fec_match(c):
    if c["fec_candidate_id"] and any(x["candidate_id"] == c["fec_candidate_id"] for x in fec):
        return "yes (ID)"
    w = norm(c["name"])
    for x in fec:
        fw = norm(x["name"].replace(",", " "))
        if w and fw and w[-1] in fw and w[0] in fw:
            return f"name only ({x['candidate_id']})"
    return "no"

def head(u):
    import time
    code = 0
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "LLF-election-desk"}), timeout=40) as r:
                return r.status
        except Exception as ex:
            code = getattr(ex, "code", 0)
            if code == 404:
                return 404
            time.sleep(2 * (attempt + 1))
    return code

race_key = lambda c: {"governor": "2026-GOV-IL", "senate": "2026-S-IL"}.get(c["office"]) or f"2026-H-IL-{int(c['race'].split('-')[1]):02d}"
race_urls = sorted({f"https://theissuesparty.org/races/{race_key(c)}" for c in cands})
with cf.ThreadPoolExecutor(6) as ex:
    race_http = dict(zip(race_urls, ex.map(head, race_urls)))
# retry any TIP profile that failed once (a single failed request is not a missing page)
for c in cands:
    t = c.get("tip") or {}
    if t and t.get("http_status") not in (200, None):
        s = head(f"https://theissuesparty.org/candidates/{c['tip_page_id']}")
        t["http_status"] = s
        if s == 200:
            t["url"] = f"https://theissuesparty.org/candidates/{c['tip_page_id']}"

rows = []
for c in cands:
    t = c.get("tip") or {}
    rk = race_key(c)
    ent = next((e for (k, n), e in entries.items() if k == rk and c["tip_page_id"] and e["fec_candidate_id"] == c["fec_candidate_id"]), None)
    graded = [(i, g) for i, g in (t.get("grades") or {}).items() if g["state"] == "graded"]
    who = "write-in" if c.get("write_in") else ("incumbent" if c["incumbent"] else "nominee" if c["primary"] or c["office"] != "governor" else "independent or minor party")
    port = next((v for k, v in portraits.items() if v.get("name") == c["name"] and v.get("result") == "ok"), None)
    gaps = []
    if not t.get("url"):
        gaps.append("no TIP profile")
    if t.get("url") and not ent:
        gaps.append("TIP profile exists but no race entry" if c["office"] == "governor" else "no TIP race entry")
    if ent and ent["verification_status"].startswith("National"):
        gaps.append("TIP entry rests on 'National source only'")
    rows.append({"race": rk, "office": c["office"], "district": c["race"].split("-")[1] if c["race"].startswith("house") else "", "name_on_roster": c["name"], "party": c["party"], "category": who,
                 "incumbent": "yes" if c["incumbent"] else "no", "roster_sources": "Green Papers (secondary); official ISBE list not read", "isbe_verified": "PENDING",
                 "fec_cross_check": fec_match(c) if c["office"] != "governor" else "n/a (state office)", "fec_candidate_id": c["fec_candidate_id"] or "", "tip_profile_id": c["tip_page_id"] or "",
                 "tip_profile_url": t.get("url") or "", "tip_http": t.get("http_status") or "", "tip_congressional_profile_url": t.get("grades_url") or "",
                 "tip_race_url": f"https://theissuesparty.org/races/{rk}", "tip_race_http": race_http[f"https://theissuesparty.org/races/{rk}"],
                 "tip_race_entry_status": ent["status"] if ent else "", "tip_entry_verification": ent["verification_status"] if ent else "",
                 "graded_issues_of_6": len(graded), "grades": "; ".join(f"{i.split('_')[0]}={g['grade']}" for i, g in graded), "grade_profile": (t.get("grades_url") or t.get("url") or "") if graded else "",
                 "llf_publication": "none: no Illinois page is published or built on LLF", "portrait": ("licensed: " + port["license"] if port else "none"), "gaps": "; ".join(gaps), "note": c.get("note") or ""})
with open(D / "il_candidate_tip_mapping.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
import collections
print(len(rows), "rows;", "with TIP profile", sum(1 for r in rows if r["tip_profile_url"]), "| TIP gaps", sum(1 for r in rows if r["gaps"]), "| race pages", dict(collections.Counter(race_http.values())))
(D / "il_tip_mapping_summary.json").write_text(json.dumps({"rows": len(rows), "with_tip_profile": sum(1 for r in rows if r["tip_profile_url"]), "gaps": [(r["name_on_roster"], r["gaps"]) for r in rows if r["gaps"]],
                                                           "race_page_http": race_http, "graded_candidates": [(r["name_on_roster"], r["graded_issues_of_6"]) for r in rows if r["graded_issues_of_6"]]}, indent=1), encoding="utf-8")
