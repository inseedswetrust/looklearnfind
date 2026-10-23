#!/usr/bin/env python3
"""Independent expenditures by United Democracy Project (C00799031) and AIPAC PAC (C00797670) in the 2026 cycle, from OpenFEC Schedule E.

    FEC_API_KEY=... python3 tools/dark_horse/fetch_udp_ie.py

Writes data/elections/dark_horse/aipac_udp_ie.json: per committee, per candidate, support/oppose totals (FEC by-candidate aggregate, periodic
filings) AND de-duplicated transaction-level totals from 24/48-hour notices. These are spending in elections, not donations to candidates.
Direct AIPAC PAC contributions (Schedule B) are NOT included; the file says so.
"""
import json, os, time, datetime, urllib.parse, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/elections/dark_horse"
KEY = os.environ["FEC_API_KEY"]
COMMITTEES = {"UDP": "C00799031", "AIPAC_PAC": "C00797670"}
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
res = {"captured_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "cycle": 2026,
       "scope_note": "Independent expenditures only (FEC Schedule E). Direct PAC contributions to candidates (Schedule B) are not included.", "committees": {}}
for name, cid in COMMITTEES.items():
    by, page = [], 1
    while True:
        j = get("/schedules/schedule_e/by_candidate/", committee_id=cid, cycle=2026, election_full="false", per_page=100, page=page)
        by += [{k: r.get(k) for k in ("candidate_id", "candidate_name", "support_oppose_indicator", "total", "count", "office", "state", "district", "party")} for r in j["results"]]
        if page >= j["pagination"]["pages"]: break
        page += 1
    # transaction level (notices + periodic), de-duplicated on (transaction_id, amount, date)
    tx, last_idx, last_date = {}, None, None
    while True:
        q = dict(committee_id=cid, cycle=2026, per_page=100, sort="-expenditure_date", most_recent="true")
        if last_idx: q.update(last_index=last_idx, last_expenditure_date=last_date)
        j = get("/schedules/schedule_e/", **q)
        for r in j["results"]:
            if r.get("memo_code") == "X": continue
            k = (r.get("transaction_id"), r.get("expenditure_amount"), (r.get("expenditure_date") or "")[:10], r.get("candidate_id"), r.get("support_oppose_indicator"))
            if k not in tx or (r.get("is_notice") and not tx[k]["is_notice"]):
                tx[k] = {f: r.get(f) for f in ("candidate_id", "candidate_name", "support_oppose_indicator", "expenditure_amount", "expenditure_date", "dissemination_date", "payee_name",
                          "expenditure_description", "filing_form", "is_notice", "transaction_id", "sub_id")}
        li = j["pagination"].get("last_indexes")
        if not li or len(j["results"]) < 100: break
        last_idx, last_date = li["last_index"], li["last_expenditure_date"]
        time.sleep(0.2)
    res["committees"][name] = {"committee_id": cid, "by_candidate_aggregate": by, "transactions_deduped": list(tx.values())}
    print(name, "by-candidate rows", len(by), "deduped transactions", len(tx), "total $", round(sum(t["expenditure_amount"] or 0 for t in tx.values())))
(OUT / "aipac_udp_ie.json").write_text(json.dumps(res, indent=1))
