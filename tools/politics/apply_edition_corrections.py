#!/usr/bin/env python3
"""Apply docs/politics/brand/edition-001/CORRECTIONS.json to the Edition 001 record and approve it on the owner's decision.

Plain-text replacements only; every `old` string must be found. The review table inside the record is not edited. Idempotent: a correction that is already
applied is skipped. The approval is an owner decision, not an independent fact-check pass: fact_check.state is "owner_approved", and the published page carries
an editor's note saying which citations could not be opened.
Usage: python tools/politics/apply_edition_corrections.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "data" / "politics_daily" / "2026-11-05-edition-001.json"
COR = ROOT / "docs" / "politics" / "brand" / "edition-001" / "CORRECTIONS.json"
CLAIMS = ROOT / "docs" / "politics" / "brand" / "edition-001" / "CLAIMS.csv"

NOTE = ("Editor's note, Nov. 5, 2026. Approved for publication by the owner after a partial source review. The Reuters and AP articles listed below could not be opened during "
        "that review, so the claims that rest on them (the expectation that Schumer leads the Senate Democrats, the AP Voter Poll findings, Democratic leaders' stated priorities and "
        "the Reuters report on state races) are not independently verified. Control of Congress is a projection and remains unofficial until results are certified. "
        "Corrections made during review are listed in the update log.")


def walk(o, fn, skip=("review",)):
    if isinstance(o, dict):
        return {k: (v if k in skip else walk(v, fn, skip)) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(x, fn, skip) for x in o]
    return fn(o) if isinstance(o, str) else o


def main():
    rec = json.loads(REC.read_text(encoding="utf-8"))
    cor = json.loads(COR.read_text(encoding="utf-8"))
    applied = []
    for c in cor["corrections"]:
        hits = [0]

        def fn(s, c=c, hits=hits):
            if c["old"] in s:
                hits[0] += s.count(c["old"])
                return s.replace(c["old"], c["new"])
            return s
        rec = walk(rec, fn)
        if hits[0]:
            applied.append(c["id"])
        elif c["new"] and not any(c["new"] in json.dumps(rec, ensure_ascii=False) for _ in (0,)):
            raise SystemExit(f"correction {c['id']}: neither the old nor the new text is present")
    rec["status"] = "approved"
    rec["editor"] = "Owner (approving editor)"
    rec["fact_check"] = {"state": "owner_approved", "reviewer": "", "approved_by": cor["approved_by"], "approved_on": cor["approved_on"],
                         "note": "Owner approval after a partial source review (7 of 15 claims supported, flags corrected or disclosed). Not an independent fact-check pass."}
    rec["editors_note"] = NOTE
    log = [u for u in rec["update_log"] if not u["note"].startswith(("Corrections applied", "Approved for publication"))]
    log.append({"date": cor["approved_on"], "note": "Corrections applied after the source review: " + "; ".join(f"{c['id']} {c['reason']}" for c in cor["corrections"])})
    log.append({"date": cor["approved_on"], "note": "Approved for publication by the owner. Citations that could not be opened (Reuters, AP) are disclosed in the editor's note."})
    rec["update_log"] = log
    # resolutions on the review table (kept in the record, never published)
    by_claim = {}
    for c in cor["corrections"]:
        for cl in c["claims"]:
            by_claim.setdefault(cl, []).append(c["id"])
    for cl in rec.get("review", {}).get("claims", []):
        cl["resolution"] = ("Corrected: " + ", ".join(by_claim[cl["id"]])) if cl["id"] in by_claim else ("Disclosed in the editor's note" if cl["status"] in ("unverified", "partly supported") else "No change needed")
    REC.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("applied:", applied or "(already applied)", "| status:", rec["status"])


if __name__ == "__main__":
    main()
