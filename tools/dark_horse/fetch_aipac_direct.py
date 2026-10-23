#!/usr/bin/env python3
"""Direct contributions by AIPAC PAC (C00797670) to candidate committees, FEC Schedule B, 2025-2026 transaction period.

    FEC_API_KEY=... python3 tools/dark_horse/fetch_aipac_direct.py     (falls back to the public DEMO_KEY, which is rate limited)

Writes data/elections/dark_horse/aipac_direct_contributions.json. This is a DIFFERENT field from Schedule E independent expenditures
(fetch_udp_ie.py): a direct contribution is money given to a candidate's committee, an independent expenditure is spending that is not
coordinated with a candidate. Rows are kept as filed: amendments are preserved with their amendment indicator and memo rows are flagged,
never silently dropped. Recipients are reported by FEC committee ID and candidate ID where FEC supplies one.
"""
import json, os, time, datetime, urllib.parse, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/elections/dark_horse/aipac_direct_contributions.json"
KEY = os.environ.get("FEC_API_KEY", "DEMO_KEY")
CID = "C00797670"
FIELDS = ("transaction_id", "sub_id", "file_number", "amendment_indicator", "memo_code", "memo_text", "line_number", "disbursement_amount", "disbursement_date",
          "disbursement_description", "disbursement_purpose_category", "recipient_committee_id", "recipient_name", "recipient_state", "report_year", "report_type",
          "two_year_transaction_period", "election_type", "candidate_id", "candidate_name", "candidate_office", "candidate_office_state", "candidate_office_district")


def get(path, **q):
    q["api_key"] = KEY
    u = "https://api.open.fec.gov/v1" + path + "?" + urllib.parse.urlencode(q, doseq=True)
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "LLF-election-desk"}), timeout=90) as r:
                return json.loads(r.read())
        except Exception:
            if a == 3:
                raise
            time.sleep(3 + 5 * a)


rows, last_idx, last_date = [], None, None
while True:
    q = dict(committee_id=CID, two_year_transaction_period=2026, per_page=100, sort="-disbursement_date")
    if last_idx:
        q.update(last_index=last_idx, last_disbursement_date=last_date)
    j = get("/schedules/schedule_b/", **q)
    rows += [{f: r.get(f) for f in FIELDS} for r in j["results"]]
    li = j["pagination"].get("last_indexes")
    if not li or len(j["results"]) < 100:
        break
    last_idx, last_date = li["last_index"], li["last_disbursement_date"]
    time.sleep(0.5)

# a candidate contribution has a candidate ID or is booked on line 23 (contributions to other committees); keep every row, mark the kind
for r in rows:
    r["kind"] = "contribution_to_candidate_committee" if (r["candidate_id"] or str(r["line_number"] or "").endswith("23")) else "other_disbursement"
res = {"captured_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "committee_id": CID, "committee": "AIPAC PAC",
       "source": "OpenFEC /schedules/schedule_b/ (two_year_transaction_period=2026)", "row_count": len(rows),
       "scope_note": "Schedule B disbursements. Contributions to candidates are separate from Schedule E independent expenditures (UDP/AIPAC PAC) and from any other committee.",
       "rows": rows}
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print("rows", len(rows), "to candidates", sum(1 for r in rows if r["kind"] == "contribution_to_candidate_committee"))
