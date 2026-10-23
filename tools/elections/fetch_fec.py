#!/usr/bin/env python3
"""Pull candidate committee totals and independent-expenditure (Schedule E) totals from OpenFEC for the Florida roster.

    FEC_API_KEY=... python3 tools/elections/fetch_fec.py

Reads data/elections/FL/candidates.json. Writes data/elections/FL/finance_fec.json and captures/fec_*.json (raw, hashed).
Never invents values: a candidate with no FEC totals row stays absent and is shown as "No FEC report on file".
Definitions: totals are candidate committee receipts/disbursements for the stated coverage period. Independent expenditures
(Schedule E, by candidate) are spending by outside committees and are never added to candidate receipts.
"""
import json, os, sys, time, hashlib, datetime, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data/elections/FL"
KEY = os.environ["FEC_API_KEY"]
API = "https://api.open.fec.gov/v1"
cands = json.loads((D / "candidates.json").read_text(encoding="utf-8"))["candidates"]
ids = sorted({c["fec_candidate_id"] for c in cands if c["fec_candidate_id"] and c["office"] in ("house", "senate") and c["fec_candidate_id"][0] in "HS"})
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get(path, params):
    q = urllib.parse.urlencode(params, doseq=True) + "&api_key=" + KEY
    url = f"{API}{path}?{q}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "LLF-election-desk"}), timeout=90) as r:
                return json.loads(r.read())
        except Exception as ex:
            if attempt == 3:
                raise
            time.sleep(2 + attempt * 3)

totals, raw = {}, []
for i in range(0, len(ids), 40):
    chunk = ids[i:i + 40]
    j = get("/candidates/totals/", {"candidate_id": chunk, "cycle": 2026, "election_full": "false", "per_page": 100})
    raw.append(j)
    for r in j["results"]:
        totals[r["candidate_id"]] = {k: r.get(k) for k in ("receipts", "disbursements", "cash_on_hand_end_period", "debts_owed_by_committee",
            "individual_itemized_contributions", "individual_unitemized_contributions", "other_political_committee_contributions",
            "political_party_committee_contributions", "candidate_contribution", "coverage_start_date", "coverage_end_date", "last_report_type_full", "last_beginning_image_number")}
(D / "captures" / f"fec_totals_{now[:10]}.json").write_text(json.dumps(raw))

# independent expenditures by candidate (support/oppose), 2026 cycle
ie = {}
iraw = []
for cid in ids:
    page = 1
    while True:
        j = get("/schedules/schedule_e/by_candidate/", {"candidate_id": cid, "cycle": 2026, "election_full": "false", "per_page": 100, "page": page})
        iraw.append(j)
        for r in j["results"]:
            ie.setdefault(cid, []).append({k: r.get(k) for k in ("support_oppose_indicator", "total", "count", "committee_id", "cycle")})
        if page >= j["pagination"]["pages"]:
            break
        page += 1
    time.sleep(0.15)
(D / "captures" / f"fec_ie_by_candidate_{now[:10]}.json").write_text(json.dumps(iraw))

# committee names for IE spenders
cmt_ids = sorted({x["committee_id"] for v in ie.values() for x in v if x["committee_id"]})
names = {}
for i in range(0, len(cmt_ids), 40):
    j = get("/committees/", {"committee_id": cmt_ids[i:i + 40], "per_page": 100})
    for r in j["results"]:
        names[r["committee_id"]] = {"name": r["name"], "type": r.get("committee_type_full"), "designation": r.get("designation_full")}
for v in ie.values():
    for x in v:
        x["committee"] = names.get(x["committee_id"], {})

out = {"as_of_utc": now, "source": "OpenFEC /candidates/totals and /schedules/schedule_e/by_candidate, cycle 2026",
       "candidates_queried": len(ids), "totals": totals, "independent_expenditures": ie}
(D / "finance_fec.json").write_text(json.dumps(out, indent=1))
print({"queried": len(ids), "with_totals": len(totals), "with_ie": len(ie), "committees": len(names)})
