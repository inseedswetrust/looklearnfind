#!/usr/bin/env python3
"""Rebuild data/elections/workflow_ledger.jsonl for the Round 1 baseline: three published reports (backfilled from the implementation report, flagged as such)
and the two Florida long-form articles at RESEARCH_COMMISSIONED. Run once after the research packet is final; afterwards only `transitions.py record` appends."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import transitions as t
t.LEDGER.unlink(missing_ok=True)
S = t.STATES
for ent in ("florida-house-independent-spending-october-2026", "florida-governor-fundraising-polling-2026", "michigan-senate-delta-october-2026"):
    for s in S[:S.index("VERIFIED_LIVE") + 1]:
        t.record(ent, s, "claude-code", skills=["llf-factcheck-finalize@1.0.0"] if s == "EDITORIAL_QA" else [], url=f"https://looklearnfind.com/learn/{ent}/" if s in ("DEPLOYED", "VERIFIED_LIVE") else None,
                 disposition="BACKFILL: reconstructed from docs/election-build/IMPLEMENTATION_REPORT.md; timestamp is the backfill time, not the event time")
for ent in ("fl-senate-article", "fl-house-article"):
    for s in S[:S.index("RESEARCH_COMMISSIONED") + 1]:
        t.record(ent, s, "claude-code", skills=["election-state-packet@1.0.0"] if s in ("ROSTER_VERIFIED", "DATA_CAPTURED") else [],
                 outputs=["release/research_packet/manifest.json"] if s in ("DATA_CAPTURED", "RESEARCH_COMMISSIONED") else [], checks={"packet_files": "pass"} if s == "DATA_CAPTURED" else None,
                 disposition="Phase A research packet 1.0.0 returned to ChatGPT; next gate is RESEARCH_RETURNED" if s == "RESEARCH_COMMISSIONED" else "")
print(len(t.read()), "entries")
