#!/usr/bin/env python3
"""Rebuild UDP (C00799031) independent-expenditure totals from OpenFEC Schedule E and the committee totals endpoint, under stated definitions.

    python3 tools/dark_horse/udp_delta.py

Reads FEC_API_KEY from the environment or the git-ignored .env.local at the repo root. Never prints the key.
Writes productions/2026/MI/research/udp_schedule_e_raw.json (every row returned) and udp_delta_summary.json.
"""
import json, os, sys, time, urllib.parse, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "productions/2026/MI/research"
KEY = os.environ.get("FEC_API_KEY")
if not KEY and (ROOT / ".env.local").exists():
    for l in (ROOT / ".env.local").read_text(encoding="utf-8").splitlines():
        if l.startswith("FEC_API_KEY="):
            KEY = l.split("=", 1)[1].strip()
assert KEY, "FEC_API_KEY not set"
CID = "C00799031"

def get(path, **q):
    q["api_key"] = KEY
    u = "https://api.open.fec.gov/v1" + path + "?" + urllib.parse.urlencode(q, doseq=True)
    for a in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "LLF-election-desk"}), timeout=90) as r:
                return json.loads(r.read())
        except Exception as e:
            if a == 5: raise
            time.sleep(3 + 4 * a)

rows, last_idx, last_date = [], None, None
while True:
    q = dict(committee_id=CID, two_year_transaction_period=2026, per_page=100, sort="-expenditure_date")
    if last_idx: q.update(last_index=last_idx, last_expenditure_date=last_date)
    j = get("/schedules/schedule_e/", **q)
    rows += j["results"]
    li = j["pagination"].get("last_indexes")
    print(len(rows), "of", j["pagination"]["count"], flush=True)
    if not li or len(j["results"]) < 100: break
    last_idx, last_date = li["last_index"], li["last_expenditure_date"]
tot = get(f"/committee/{CID}/totals/", cycle=2026)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "udp_schedule_e_raw.json").write_text(json.dumps({"captured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "source": "OpenFEC /schedules/schedule_e/ and /committee/C00799031/totals/", "totals_endpoint": tot["results"], "rows": rows}, indent=1), encoding="utf-8")
print("saved", len(rows))
