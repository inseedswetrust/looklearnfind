#!/usr/bin/env python3
"""Pre-publish freshness check for time-sensitive election articles. Exit 0 = fresh, 2 = stale.

    python3 tools/qa/freshness_check.py [--max-market-hours 24] [--max-day-old-polls 0] [--now 2026-10-24T12:00:00Z]

Markets in these articles are `[[v:]]` or component values read from data/elections/FL/markets.json at BUILD time, so a build older than the capture is stale.
Typed numbers (polls, results) do not update themselves: this check lists the newest poll in the VoteHub capture for each article race so a person can see whether the article is still the latest.
"""
import json, sys, datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
a = sys.argv[1:]
arg = lambda k, d: a[a.index(k) + 1] if k in a else d
now = datetime.datetime.fromisoformat(arg("--now", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")).replace("Z", "+00:00"))
cap = datetime.datetime.fromisoformat(json.loads((ROOT / "data/elections/FL/markets.json").read_text())["captured_at_utc"].replace("Z", "+00:00"))
age = (now - cap).total_seconds() / 3600
out = {"market_capture_age_hours": round(age, 1), "limit_hours": float(arg("--max-market-hours", 24)), "problems": []}
if age > out["limit_hours"]:
    out["problems"].append(f"Kalshi capture is {age:.0f} hours old: run tools/elections/fetch_kalshi.py and rebuild before publishing")
sd = json.loads((ROOT / "data/elections/FL/story_data.json").read_text(encoding="utf-8"))
newest = sd["unf_oct"]["field_end"]
latest = ROOT / "data/elections/dark_horse/latest.json"
try:
    L = json.loads(latest.read_text()); P = json.loads((ROOT / "data/elections/dark_horse" / L["polls_path"]).read_text())
    fl = [p for p in P["polls"] if p.get("race_id") == "SEN" and "S6FL" in str(p.get("candidate_ids"))]
    out["newest_florida_senate_field_end_in_feed"] = max((p["field_end"] for p in fl if p.get("field_end")), default=None)
    if out["newest_florida_senate_field_end_in_feed"] and out["newest_florida_senate_field_end_in_feed"] > newest:
        out["problems"].append(f"a Senate poll fielded through {out['newest_florida_senate_field_end_in_feed']} is newer than the article's poll (field end {newest})")
except Exception as ex:
    out["note"] = f"poll feed not checked: {ex.__class__.__name__}"
print(json.dumps(out, indent=1))
sys.exit(2 if out["problems"] else 0)
