#!/usr/bin/env python3
"""Coverage matrix: one row per watchlisted race from the latest complete day. Writes data/elections/dark_horse/coverage_matrix.csv.
Alphabetical by state then race. This is a coverage report, not a ranking of candidates."""
import csv, json
from pathlib import Path
B = Path(__file__).resolve().parents[2] / "data/elections/dark_horse"
latest = json.loads((B / "latest.json").read_text())
day = latest["date"]
mk = json.loads((B / latest["markets_path"]).read_text())["rows"]      # follows the pointer, so a revision is honored
pl = json.loads((B / latest["polls_path"]).read_text())
watch = list(csv.DictReader(open(B / "watchlist.csv", encoding="utf-8-sig")))
def key(c): return c["tip_candidate_id"] or f"no_tip:{c['state']}:{c['race']}:{c['candidate_name']}"
rows = []
for c in sorted(watch, key=lambda c: (c["state"], c["race"])):
    k = key(c)
    q = {r["provider"]: r for r in mk if r["candidate_id"] == k}
    cov = pl["coverage"].get(k, {})
    def cell(p):
        r = q.get(p)
        if not r: return "not_monitored" if c["current_ballot_verified"] != "yes" else "no_market"
        return "ok" if r["fetch_status"] == "ok" else r["fetch_status"]
    rows.append({"date": day, "candidate_name": c["candidate_name"], "state": c["state"], "race": c["race"], "race_key": c["race_key"], "tip_candidate_id": c["tip_candidate_id"],
                 "current_ballot_verified": c["current_ballot_verified"], "dark_horse_status": c["dark_horse_status"], "lock_status": c["lock_status"], "nov3_general_status": c["nov3_general_status"],
                 "kalshi": cell("kalshi"), "kalshi_contract_kind": (q.get("kalshi") or {}).get("contract_kind") or "", "kalshi_last": (q.get("kalshi") or {}).get("quoted_price"),
                 "polymarket": cell("polymarket"), "polymarket_contract_kind": (q.get("polymarket") or {}).get("contract_kind") or "", "polymarket_last": (q.get("polymarket") or {}).get("quoted_price"),
                 "polls_votehub": cov.get("polls", 0) if c["current_ballot_verified"] == "yes" else "not_monitored", "poll_status": cov.get("status", "not_monitored"),
                 "latest_poll_field_end": cov.get("latest_field_end") or "", "gap": c["notes"].split("Prior discussion")[0].strip()})
with open(B / "coverage_matrix.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "rows;", sum(r["kalshi"] == "ok" for r in rows), "kalshi ok;", sum(r["polymarket"] == "ok" for r in rows), "polymarket ok;", sum(1 for r in rows if r["poll_status"] == "ok"), "with polls")
