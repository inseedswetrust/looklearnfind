#!/usr/bin/env python3
"""Exit 1 with a message when any source is stale (> 48 h without a successful pull) or status.json is missing. Cron mails the output to the account contact."""
import json, sys
from pathlib import Path
p = Path(__file__).resolve().parents[2] / "data/elections/dark_horse/status.json"
if not p.exists():
    print("DARK HORSE MONITOR: status.json missing, the daily run has never completed"); sys.exit(1)
s = json.loads(p.read_text())
bad = [f"{k}: stale (last success {v.get('last_success_at')}, last error {v.get('last_error')})" for k, v in s.get("sources", {}).items() if v.get("stale")]
if bad:
    print("DARK HORSE MONITOR STALE > 48h\n" + "\n".join(bad)); sys.exit(1)
print("ok", s.get("last_run_date"))
