#!/usr/bin/env python3
"""Rebuild data/elections/workflow_ledger.jsonl for the Round 1 baseline: three published reports (backfilled from the implementation report, flagged as such)
and the lean story board for the Florida Senate and House articles (SOURCE_CHECKED). Run once after the research packet is final; afterwards only `transitions.py record` appends."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import transitions as t
t.LEDGER.unlink(missing_ok=True)
S = t.STATES
for ent in ("florida-house-independent-spending-october-2026", "florida-governor-fundraising-polling-2026", "michigan-senate-delta-october-2026"):
    for s in S[:S.index("VERIFIED_LIVE") + 1]:
        t.record(ent, s, "claude-code", skills=["llf-factcheck-finalize@1.0.0"] if s == "EDITORIAL_QA" else [], url=f"https://looklearnfind.com/learn/{ent}/" if s in ("DEPLOYED", "VERIFIED_LIVE") else None,
                 disposition="BACKFILL: reconstructed from docs/election-build/IMPLEMENTATION_REPORT.md; timestamp is the backfill time, not the event time",
                 authorization="BACKFILL: the owner uploaded these pages themselves at the time (2026-10-23)", reviewer="backfill (no independent reviewer recorded at the time)")
# lean story board (owner reset 2026-10-24): one entity per article hook set, with links to the brief, candidates, race, images and (later) article and social
BR = "docs/story-briefs/"
for ent, brief, cands, race, imgs in (
    ("story:fl-senate", BR + "STORY_BRIEF_FL_SENATE.md", {"moody": "https://theissuesparty.org/candidates/S6FL00640", "nixon": "https://theissuesparty.org/candidates/S6FL00830"}, "https://theissuesparty.org/races/2026-S-FL", ["static/img/elections/portraits/89119.jpg", "static/img/elections/portraits/90009.jpg"]),
    ("story:fl-house", BR + "STORY_BRIEF_FL_HOUSE.md", {"castor": "https://theissuesparty.org/candidates/H6FL11126", "soto": "https://theissuesparty.org/candidates/H6FL09179", "fine": "https://theissuesparty.org/candidates/H6FL06258", "moskowitz": "https://theissuesparty.org/candidates/H2FL22171"}, "https://theissuesparty.org/races/2026-H-FL-14", ["static/img/elections/portraits/88870.jpg", "static/img/elections/portraits/90492.jpg", "static/img/elections/portraits/88911.jpg"])):
    links = {"brief": brief, "claims": brief.replace("STORY_BRIEF", "CLAIMS").replace(".md", ".csv"), "candidates": cands, "race": race, "images": imgs, "article": None, "social": None}
    t.record(ent, "DISCOVERED", "claude-code", skills=["llf-story-scout@1.0.0"], links=links)
    t.record(ent, "SOURCE_CHECKED", "claude-code", skills=["llf-story-scout@1.0.0"], outputs=[brief], links=links, disposition="2 to 3 angles per article; sources opened; checker output in docs/story-briefs/story_brief_check_output.json")
print(len(t.read()), "entries")
