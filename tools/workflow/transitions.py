#!/usr/bin/env python3
"""Workflow state machine and append-only transition ledger for LLF election content.

    python3 tools/workflow/transitions.py record <entity> <to_state> --actor NAME [--skill name@ver ...] [--input path ...] [--output path ...]
                                          [--check "name=pass|fail" ...] [--reviewer NAME] [--disposition text] [--url u] [--blocked-reason text]
    python3 tools/workflow/transitions.py show [<entity>]

States (in order): DISCOVERED, ROSTER_VERIFIED, DATA_CAPTURED, RESEARCH_COMMISSIONED, RESEARCH_RETURNED, ARTICLE_DRAFTED, EDITORIAL_QA, ARTICLE_APPROVED,
MOCKUP_APPROVED, GRAPHICS_APPROVED, BUILD_TESTED, OWNER_PUBLISH_APPROVED, DEPLOYED, VERIFIED_LIVE, RETROSPECTIVE_COMPLETE.
A forward move goes to the next state only (no skipping a gate). A rejection goes back to a prior state and needs a correction ID. Entries are never edited.
"""
import argparse, hashlib, json, sys, datetime, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "data/elections/workflow_ledger.jsonl"
STATES = ["DISCOVERED", "ROSTER_VERIFIED", "DATA_CAPTURED", "RESEARCH_COMMISSIONED", "RESEARCH_RETURNED", "ARTICLE_DRAFTED", "EDITORIAL_QA", "ARTICLE_APPROVED",
          "MOCKUP_APPROVED", "GRAPHICS_APPROVED", "BUILD_TESTED", "OWNER_PUBLISH_APPROVED", "DEPLOYED", "VERIFIED_LIVE", "RETROSPECTIVE_COMPLETE"]


# Lean lane (owner reset 2026-10-24): the six states a normal story needs. The 15-state lane above stays available for work that needs graphics, mockup or owner gates.
LEAN_STATES = ["DISCOVERED", "SOURCE_CHECKED", "DRAFTED", "FACT_CHECKED", "APPROVED", "PUBLISHED"]
LEAN_ENTITIES_PREFIX = "story:"          # entities named story:<slug> use the lean lane
# Video lane (2026-10-24): entities named video:<slug>.
VIDEO_STATES = ["BRIEFED", "SCRIPTED", "STORYBOARDED", "ASSETS_GENERATED", "CUT", "QA_PASSED", "PUBLISHED"]


# Canonical production lane (LLF Production Lock v2.0, docs/production/01_END_TO_END_WORKFLOW.md): one entity per state, `production:<state>-<year>`.
PRODUCTION_STATES = ["INTAKE", "SOURCE_CHECKED", "ARTICLE_DRAFTED", "ARTICLE_FACTCHECKED", "ARTICLE_APPROVED", "ARTICLE_PUBLISHED", "VIDEO_SCRIPT_DRAFTED", "VIDEO_SCRIPT_LOCKED",
                     "STORYBOARD_LOCKED", "SHOT_PLAN_READY", "ASSETS_READY", "USER_MJ_PREMIERE_HANDOFF"]
# Separately authorized lane, `render:<state>-<year>`; it can only begin with the owner's explicit request for a rendered video.
RENDER_STATES = ["VIDEO_RENDER_REQUESTED", "VIDEO_EDITED", "VIDEO_QA", "PUBLISHED"]
# Gates enforced in code (Lock v2.0 section 04, tests h and i). The older `story:` and `video:` lanes stay valid for existing entries.
AUTH_STATES = {"ARTICLE_PUBLISHED", "PUBLISHED", "OWNER_PUBLISH_APPROVED", "DEPLOYED", "VIDEO_RENDER_REQUESTED"}      # need the owner's authorization in their own words
FACTCHECK_STATES = {"ARTICLE_FACTCHECKED", "FACT_CHECKED"}                                                          # need a reviewer who is not the actor


def lane_of(entity):
    if entity.startswith("production:"):
        return PRODUCTION_STATES
    if entity.startswith("render:"):
        return RENDER_STATES
    if entity.startswith("video:"):
        return VIDEO_STATES
    return LEAN_STATES if entity.startswith(LEAN_ENTITIES_PREFIX) else STATES


def read(path=LEDGER):
    p = Path(path)
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def current(entity, path=LEDGER):
    s = [e for e in read(path) if e["entity"] == entity]
    return s[-1]["to_state"] if s else None


def sha(p):
    p = Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def record(entity, to, actor, skills=(), inputs=(), outputs=(), checks=None, reviewer=None, disposition="", url=None, blocked_reason=None, correction_id=None, path=LEDGER, now=None, links=None, authorization=None):
    STATES = lane_of(entity)
    if to not in STATES:
        raise ValueError(f"unknown state {to} for {entity}")
    if to in AUTH_STATES and len((authorization or "").strip()) < 10:
        raise ValueError(f"{to} needs authorization: the owner's explicit approval in their own words (nothing is published, deployed or rendered on an inferred permission)")
    if to in FACTCHECK_STATES and (not (reviewer or "").strip() or reviewer.strip().lower() == actor.strip().lower()):
        raise ValueError(f"{to} needs a named reviewer who is not the actor: the drafter does not check their own work")
    cur = current(entity, path)
    if cur is None:
        if to != STATES[0]:
            raise ValueError(f"an entity starts at {STATES[0]}")
    else:
        i, j = STATES.index(cur), STATES.index(to)
        if j > i + 1:
            raise ValueError(f"cannot skip from {cur} to {to}: the next gate is {STATES[i + 1]}")
        if j <= i and not correction_id:
            raise ValueError("moving backward is a rejection and needs --correction-id")
        if j == i + 1 and (checks and any(v != "pass" for v in checks.values())):
            raise ValueError("a failed check cannot advance the entity; record the rejection with a correction ID")
    e = {"entry_id": uuid.uuid4().hex[:12], "entity": entity, "from_state": cur, "to_state": to, "at_utc": now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "actor": actor, "skills": list(skills), "inputs": {str(p): sha(ROOT / p) for p in inputs}, "outputs": {str(p): sha(ROOT / p) for p in outputs}, "checks": checks or {},
         "reviewer": reviewer, "authorization": authorization, "disposition": disposition, "url": url, "links": links or {}, "blocked_reason": blocked_reason, "correction_id": correction_id}
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return e


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("entity"); r.add_argument("to_state"); r.add_argument("--actor", required=True)
    r.add_argument("--skill", action="append", default=[]); r.add_argument("--input", action="append", default=[]); r.add_argument("--output", action="append", default=[])
    r.add_argument("--check", action="append", default=[]); r.add_argument("--reviewer"); r.add_argument("--disposition", default=""); r.add_argument("--url")
    r.add_argument("--blocked-reason"); r.add_argument("--correction-id"); r.add_argument("--authorization")
    s = sub.add_parser("show"); s.add_argument("entity", nargs="?")
    a = ap.parse_args()
    if a.cmd == "record":
        e = record(a.entity, a.to_state, a.actor, a.skill, a.input, a.output, dict(c.split("=", 1) for c in a.check), a.reviewer, a.disposition, a.url, a.blocked_reason, a.correction_id, authorization=a.authorization)
        print(json.dumps(e, indent=1))
    else:
        for e in read():
            if not a.entity or e["entity"] == a.entity:
                print(e["at_utc"], e["entity"], (e["from_state"] or "-"), "->", e["to_state"], e["actor"], e.get("blocked_reason") or "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
