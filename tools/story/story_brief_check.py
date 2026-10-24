#!/usr/bin/env python3
"""Deterministic readiness check for llf-story-scout briefs.

    python3 tools/story/story_brief_check.py story_brief.json [--as-of 2026-10-24]     exit 0 if every angle is READY, 2 if any is NOT_READY

An angle is READY only when its core claim is supported. It never judges newsworthiness or who should win; it only refuses angles the skill's tests forbid:
no article URL or date; lead source not opened (a search snippet is not reporting); a damaging allegation without original material and a response effort;
old coverage labeled as new; a user-facing financial claim without an attributed source and period. A TIP grade that cannot be traced to the profile showing it is
hidden and shown as NOT_GRADED (the angle stays READY). Source-registry growth never edits or approves existing entries.
"""
import json, sys, datetime, copy
from pathlib import Path

RECENT_DAYS = 30


def _d(s):
    try:
        return datetime.date.fromisoformat(s[:10])
    except Exception:
        return None


def check_angle(a, as_of):
    why = []
    srcs = a.get("sources") or []
    lead = [s for s in srcs if s.get("role") == "lead"] or srcs[:1]
    if not lead or not (lead[0].get("url") or "").startswith("http") or not _d(lead[0].get("date") or ""):
        why.append("missing article URL or date for the lead source")
    elif not lead[0].get("opened"):
        why.append("lead source is snippet-only (discovered, not opened and read)")
    al = a.get("damaging_allegation") or {}
    if al.get("present") and not (al.get("original_evidence_url") and al.get("response_sought")):
        why.append("damaging allegation without original evidence and a documented response effort")
    ev = _d(a.get("event_date") or "") or (_d(lead[0].get("date") or "") if lead else None)
    if a.get("labelled_new") and ev and (as_of - ev).days > RECENT_DAYS:
        why.append(f"recycled coverage labeled as new: the event is {(as_of - ev).days} days old")
    for f in a.get("financial_claims") or []:
        if not (f.get("source_url") and f.get("period") and f.get("attributed_to")):
            why.append("financial claim without attributed source and period: " + (f.get("claim") or "?")[:60])
    grades, hidden = [], []
    for g in a.get("tip_grades") or []:
        prof = g.get("source_profile") or ""
        if g.get("grade") and (not prof.startswith("https://theissuesparty.org/candidates/") or "/GOV-" in prof):
            hidden.append(dict(g, grade=None, display="NOT_GRADED", note="grade not traceable to the profile that shows it; hidden"))
        else:
            grades.append(dict(g, display=g.get("grade") or "NOT_GRADED"))
    n = len((a.get("synopsis") or "").split())
    notes = [f"synopsis is {n} words (target about 120)"] if n > 150 else []
    ready = not why
    return {"id": a.get("id"), "status": "READY" if ready else "NOT_READY", "reasons": why, "tip_grades_shown": grades + hidden, "notes": notes,
            "ready_to_write": bool(ready and a.get("ready_to_write", True))}


def check_brief(brief, as_of=None):
    as_of = as_of or datetime.date.today()
    res = [check_angle(a, as_of) for a in brief.get("angles", [])]
    return {"scope": brief.get("scope"), "as_of": str(as_of), "angles": res, "ready_count": sum(1 for r in res if r["status"] == "READY")}


def registry_add(registry, entry):
    """Returns a NEW registry with the entry appended as `proposed`. Existing entries are never modified and nothing is auto-approved for publication."""
    new = copy.deepcopy(registry)
    if any(e["domain"] == entry["domain"] for e in new["sources"]):
        return new
    new["sources"].append(dict(entry, owner_approved=False, status="proposed"))
    return new


if __name__ == "__main__":
    a = sys.argv[1:]
    as_of = datetime.date.fromisoformat(a[a.index("--as-of") + 1]) if "--as-of" in a else datetime.date.today()
    out = check_brief(json.loads(Path(a[0]).read_text(encoding="utf-8")), as_of)
    print(json.dumps(out, indent=1))
    sys.exit(0 if out["ready_count"] == len(out["angles"]) else 2)
