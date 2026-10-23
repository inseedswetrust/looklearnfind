#!/usr/bin/env python3
"""Pull Schedule E independent-expenditure transactions for given candidates (OpenFEC) and reconcile with FEC's own by-candidate totals.

    FEC_API_KEY=... python3 tools/elections/fetch_fec_ie.py FL data/elections/FL/ie_FL14_FL25.json house-14 house-25

Keeps: spender committee, amount, expenditure date, dissemination date, support/oppose, payee, description, filing form, amendment flag, sub_id.
Uses most_recent=true so superseded amendment rows are dropped. Notices (24/48-hour F24) and periodic-report rows are labeled by `is_notice`;
the reconciliation block shows whether the transaction-level sum equals FEC's by_candidate total, so a reader can see any gap instead of a silent double count.
"""
import sys, os, json, urllib.parse, urllib.request, datetime, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
state, outfile, *races = sys.argv[1:]
KEY = os.environ["FEC_API_KEY"]
cands = [c for c in json.loads((ROOT / f"data/elections/{state}/candidates.json").read_text(encoding="utf-8"))["candidates"] if c["race"] in races and c["fec_candidate_id"]]
def get(path, **q):
    q["api_key"] = KEY
    u = "https://api.open.fec.gov/v1" + path + "?" + urllib.parse.urlencode(q, doseq=True)
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "LLF-election-desk"}), timeout=90) as r:
                return json.loads(r.read())
        except Exception:
            if a == 3: raise
            time.sleep(2 + 3 * a)
out = {"captured_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "candidates": {}}
for c in cands:
    rows, last_idx, last_date = [], None, None
    while True:
        q = dict(candidate_id=c["fec_candidate_id"], cycle=2026, per_page=100, sort="-expenditure_date", most_recent="true")
        if last_idx:
            q.update(last_index=last_idx, last_expenditure_date=last_date)
        j = get("/schedules/schedule_e/", **q)
        for r in j["results"]:
            rows.append({k: r.get(k) for k in ("committee_id", "expenditure_amount", "expenditure_date", "dissemination_date", "support_oppose_indicator",
                         "payee_name", "expenditure_description", "filing_form", "amendment_indicator", "is_notice", "memo_code", "sub_id", "transaction_id", "report_year")})
            rows[-1]["committee_name"] = (r.get("committee") or {}).get("name") or r.get("committee_name")
        li = j["pagination"].get("last_indexes")
        if not li or not j["results"] or len(j["results"]) < 100:
            break
        last_idx, last_date = li["last_index"], li["last_expenditure_date"]
        time.sleep(0.2)
    bc = get("/schedules/schedule_e/by_candidate/", candidate_id=c["fec_candidate_id"], cycle=2026, election_full="false", per_page=100)["results"]
    out["candidates"][c["fec_candidate_id"]] = {"name": c["name"], "race": c["race"], "transactions": rows,
        "by_candidate_totals": [{k: x.get(k) for k in ("support_oppose_indicator", "total", "count", "committee_id")} for x in bc]}
    print(c["name"], len(rows), round(sum(r["expenditure_amount"] or 0 for r in rows)), round(sum(x["total"] or 0 for x in bc)))
Path(ROOT, outfile).write_text(json.dumps(out))
