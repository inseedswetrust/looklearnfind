#!/usr/bin/env python3
"""Lock the dark-horse watchlist (contract v1.1.0): four evidence statuses, separate contest IDs, ballot checks with their source.

    python3 tools/dark_horse/lock_watchlist.py

Reads data/elections/dark_horse/watchlist.csv (built by build_watchlist.py) and writes it back with these added columns, plus watchlist.lock.json:
  lock_status        verified | partial | unverified | background   (verified = a documented criterion with a cited source; there is NO ranking field)
  contest_ids        JSON: primary / special / general contest IDs, each with a date or "date_unverified"
  nov3_general_status  on_ballot_official | on_ballot_news_only | not_on_ballot | not_verified
  ballot_check_source  where the ballot status came from, and whether an official source is still pending
All 28 rows are kept as research leads. Facts below were read on 2026-10-23; items marked news_only await an official results page.
"""
import csv, json, datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data/elections/dark_horse"
GEN = "2026-11-03"
MAP = {"meets": "verified", "partial": "partial", "unverified": "unverified", "lead": "background"}

# contest records: (kind, date or None, note). The general is the same date everywhere; primaries and specials differ and are never merged.
C = {
 "Abdul El-Sayed": [("primary", "2026-08-04", "Michigan Democratic primary")],
 "La Shawn Ford": [("primary", "2026-03-17", "Illinois primary date shared with the Biss and Stratton rows; Ford's own vote shares not retrieved")],
 "Daniel Biss": [("primary", "2026-03-17", "Illinois Democratic primary")],
 "Aisha Wahab": [("special_runoff", "2026-08-18", "CA-14 special runoff for the unexpired term"), ("primary", None, "regular-term primary date not verified")],
 "Brad Lander": [("primary", "2026-06-23", "New York Democratic primary")],
 "Analilia Mejia": [("special_primary", "2026-02-05", "NJ-11 special"), ("special_general", "2026-04-16", "NJ-11 special; sworn in 2026-04-20"), ("primary", None, "regular-term primary date not verified")],
 "Juliana Stratton": [("primary", "2026-03-17", "Illinois Democratic primary")],
 "Darializa Avila Chevalier": [("primary", "2026-06-23", "New York Democratic primary")],
 "Melat Kiros": [("primary", "2026-06-30", "Colorado Democratic primary")],
 "Claire Valdez": [("primary", "2026-06-23", "New York Democratic primary")],
 "William Lawrence": [("primary", None, "not verified")],
 "Donavan McKinney": [("primary", "2026-08-04", "Michigan Democratic primary")],
 "Randy Villegas": [("primary", None, "California top-two primary result not verified")],
 "Luke Bronin": [("convention", "2026-05-11", "Connecticut 1st district Democratic convention"), ("primary", "2026-08-11", "Connecticut Democratic primary")],
 "Frederick Douglass Haynes III": [("primary", "2026-03-03", "Texas Democratic primary (news report; official canvass pending)")],
 "Ilhan Omar": [("primary", "2026-08-11", "Minnesota Democratic primary (news report; official canvass pending)")],
 "Al Green": [("primary", "2026-03-03", "TX-18 Democratic primary, went to a runoff"), ("primary_runoff", "2026-05-26", "TX-18 runoff, lost to Christian Menefee (news report; official result pending)")],
}
# ballot status overrides from this pass: (status, source and caveat). Everything else comes from TIP's official-record check.
B = {
 "Al Green": ("not_on_ballot", "News reports (AP via WTOP, 2026-05-27, search summary) say Green lost the TX-18 Democratic runoff to Christian Menefee; he ran in TX-18, NOT TX-09 as the lead listed. Texas Secretary of State result still to be opened."),
 "Frederick Douglass Haynes III": ("on_ballot_news_only", "News reports say Haynes won the 2026-03-03 TX-30 primary and is on the 2026-11-03 ballot; no TIP profile; Texas Secretary of State list still to be opened."),
 "Ilhan Omar": ("on_ballot_news_only", "News reports (Mshale 2026-08-12 and others, search summary) say Omar won the 2026-08-11 MN-05 primary with over 80 percent; TIP's record rests on owner-supplied sources; Minnesota Secretary of State list still to be opened."),
 "Aisha Wahab": ("on_ballot_news_only", "Wikipedia says both finalists stay on the November full-term ballot; no TIP profile; California Secretary of State list still to be opened."),
}

rows = list(csv.DictReader(open(D / "watchlist.csv", encoding="utf-8")))
flds = list(rows[0])
for x in ("lock_status", "contest_ids", "nov3_general_status", "ballot_check_source"):
    if x not in flds:
        flds.append(x)
out = []
for r in rows:
    n = r["candidate_name"]
    contests = [{"contest_id": f"{r['race_key']}-{k.upper()}-{d or 'DATE_UNVERIFIED'}", "kind": k, "date": d or "date_unverified", "note": note} for k, d, note in C.get(n, [("primary", None, "not verified")])]
    contests.append({"contest_id": f"{r['race_key']}-GENERAL-{GEN}", "kind": "general", "date": GEN, "note": "the November general; the only contest the Nov 3 market contracts settle on"})
    r["lock_status"] = MAP[r["dark_horse_status"]]
    r["contest_ids"] = json.dumps(contests)
    if n in B:
        r["nov3_general_status"], r["ballot_check_source"] = B[n]
        if B[n][0] == "not_on_ballot":
            r["current_ballot_verified"] = "no"
            r["lock_status"] = "background"
            if "Not on the 2026-11-03 ballot" not in r.get("notes", ""):
                r["notes"] = (r["notes"] + " | " if r.get("notes") else "") + "Not on the 2026-11-03 ballot in the seat listed (see ballot_check_source)."
    else:
        yes = r["current_ballot_verified"] == "yes"
        r["nov3_general_status"] = "on_ballot_official" if yes else "not_verified"
        r["ballot_check_source"] = ("TIP race entry with 'Official candidate record checked' (state election authority record)" if yes else "no active official TIP race entry")
    out.append(r)
with open(D / "watchlist.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=flds)
    w.writeheader()
    w.writerows(out)
lock = {"contract": "darkhorse-watchlist", "version": "1.1.0", "locked_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "rows": len(out),
        "statuses": {s: sum(1 for r in out if r["lock_status"] == s) for s in ("verified", "partial", "unverified", "background")},
        "ranking_field": None, "ballot_check": {s: sum(1 for r in out if r["nov3_general_status"] == s) for s in sorted({r["nov3_general_status"] for r in out})},
        "rule": "A row is `verified` only when a documented criterion has a cited source. No row is ranked, scored or recommended."}
(D / "watchlist.lock.json").write_text(json.dumps(lock, indent=1), encoding="utf-8")
print(json.dumps(lock))
