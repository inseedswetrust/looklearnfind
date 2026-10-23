#!/usr/bin/env python3
"""Deterministic pre-publication gate for LLF election articles. Prints a JSON report and exits 0 (READY) or 2 (BLOCKED).

    python3 tools/qa/factcheck_gate.py <ledger.csv> [--article content/learn/x.html] [--packet release/research_packet]
                                       [--author NAME] [--build] [--out report.json]

The gate checks the CLAIM LEDGER, it does not judge prose. A person or a separate standards agent fills the ledger; this script refuses to call
an article READY unless the ledger is complete and agrees with the packet. Ledger columns (legacy v1 columns first, v2 columns optional):
  claim_id, page, claim, value, source, as_of, verdict, notes   |   type, evidence_ref, reviewer, resolution
Verdicts: VERIFIED, ATTRIBUTED, NEEDS_CONTEXT, UNVERIFIED, CONTRADICTED, STALE. UNVERIFIED/CONTRADICTED/STALE rows must be resolved (removed, replaced
or relabeled) before READY. Type rules (when `type` is present): grade, poll, finance, market, image. The gate never edits a ledger or an article.
"""
import argparse, csv, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOOD = {"VERIFIED", "ATTRIBUTED", "NEEDS_CONTEXT"}
BAD = {"UNVERIFIED", "CONTRADICTED", "STALE"}
REQUIRED = ["claim_id", "page", "claim", "value", "source", "as_of", "verdict", "notes"]


def rows_of(p):
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def resolved(r):
    res = (r.get("resolution") or "").strip().lower()
    if res in ("removed", "replaced", "relabeled", "corrected"):
        return True
    legacy = " ".join([r.get("claim_id") or "", r.get("claim") or "", r.get("notes") or ""]).lower()
    return r["claim_id"].startswith("REMOVED") or r["claim"].startswith("REMOVED") or any(w in legacy for w in ("removed", "replaced", "labeled unexplained"))


def check(ledger, article=None, packet=None, author=None):
    blocks, warns = [], []
    def B(cid, why): blocks.append({"claim_id": cid, "reason": why})
    if not ledger:
        return [{"claim_id": "-", "reason": "empty ledger"}], warns
    miss = [c for c in REQUIRED if c not in ledger[0]]
    if miss:
        return [{"claim_id": "-", "reason": "ledger missing columns: " + ", ".join(miss)}], warns
    ids = [r["claim_id"] for r in ledger]
    for d in {i for i in ids if ids.count(i) > 1}:
        B(d, "duplicate claim_id")
    P = {}
    if packet:
        pk = Path(packet)
        P["grades"] = rows_of(pk / "tip_grades.csv") if (pk / "tip_grades.csv").exists() else []
        P["polls"] = rows_of(pk / "fl_polls.csv") if (pk / "fl_polls.csv").exists() else []
        P["finance"] = rows_of(pk / "fl_candidate_finance.csv") if (pk / "fl_candidate_finance.csv").exists() else []
        P["assets"] = rows_of(pk / "fl_assets.csv") if (pk / "fl_assets.csv").exists() else []
        P["markets"] = json.loads((pk / "fl_markets.json").read_text(encoding="utf-8")) if (pk / "fl_markets.json").exists() else {}
    for r in ledger:
        cid, v = r["claim_id"], (r["verdict"] or "").strip().upper()
        if v not in GOOD | BAD:
            B(cid, f"verdict '{r['verdict']}' is not one of the allowed verdicts")
            continue
        if v in BAD and not resolved(r):
            B(cid, f"{v} and not resolved (removed, replaced or relabeled)")
            continue
        if v in BAD:
            continue                                   # a resolved row has nothing more to prove
        if not (r["source"] or "").strip():
            B(cid, "no source")
        if not (r["as_of"] or "").strip():
            B(cid, "no as_of timestamp")
        if author and (r.get("reviewer") or "").strip().lower() == author.strip().lower():
            B(cid, "reviewer is the author: the gate requires an independent reviewer")
        t = (r.get("type") or "").strip().lower()
        ref = (r.get("evidence_ref") or "").strip()
        if not t:
            continue
        if t == "grade":
            m = re.search(r"/candidates/([A-Z0-9-]+)", ref)
            if not m:
                B(cid, "grade claim needs the TIP profile URL in evidence_ref")
            elif m.group(1).startswith("GOV-"):
                B(cid, "grade cited from a gubernatorial profile ID; the congressional profile holds the grade")
            elif packet:
                hit = [g for g in P["grades"] if g["candidate_id"] == m.group(1) and g["grade_state"] == "graded" and g["profile_holding_grade"].endswith(m.group(1))]
                if not hit:
                    B(cid, f"no graded row for {m.group(1)} in tip_grades.csv (not graded is not a grade)")
        elif t == "poll":
            rows = [p for p in P.get("polls", []) if ref and p["original_poll_url"] == ref]
            if packet and not rows:
                B(cid, "poll original URL not found in fl_polls.csv")
            elif rows and rows[0]["review_status"].startswith("aggregator_listing") and "original reviewed" not in (r["notes"] or "").lower():
                B(cid, "poll rests on an aggregator listing; open the original release and note 'original reviewed' with MOE, mode and sponsor")
            elif rows:
                for k in ("sponsor", "population", "sample_size", "field_start", "field_end"):
                    if not rows[0][k]:
                        B(cid, f"poll row lacks {k}")
        elif t == "finance":
            rows = [f for f in P.get("finance", []) if f["candidate_id"] == ref]
            if packet and (not rows or rows[0]["gaps"]):
                B(cid, "no FEC totals row for this candidate; a missing total cannot be reported as zero")
        elif t == "market":
            n = (r["notes"] or "").lower()
            if not any(k in n for k in ("last", "bid", "ask", "mid")):
                B(cid, "market claim must state the quote kind (bid, ask, last or mid) in notes")
            if "party" not in n and "candidate" not in n:
                B(cid, "market claim must state whether the contract is party-winner or candidate")
            if packet:
                tick = {c["ticker"] for m in P["markets"].get("races", []) if m.get("status") == "ok" for c in m["contracts"]}
                if ref not in tick:
                    B(cid, "ticker not found in fl_markets.json")
        elif t == "image":
            a = [x for x in P.get("assets", []) if x["asset_id"] == ref]
            if packet and not a:
                B(cid, "asset not in fl_assets.csv")
            elif a and a[0]["publication_status"].upper().startswith("NOT FOR"):
                B(cid, "image is NOT FOR PUBLICATION")
            elif a and not (a[0]["license"] and a[0]["attribution"]):
                B(cid, "image lacks license or attribution")
        else:
            warns.append(f"{cid}: unknown type '{t}' (no type rule applied)")
    if article and "evidence_ref" not in ledger[0]:
        warns.append("legacy v1 ledger: data-macro coverage cannot be checked (no evidence_ref column); the gate checked verdicts, sources and timestamps only")
    elif article:
        html = Path(article).read_text(encoding="utf-8")
        macros = sorted(set(re.findall(r"\[\[v:([A-Za-z0-9_]+)\]\]", html)))
        blob = " ".join((r.get("value") or "") + " " + (r.get("evidence_ref") or "") + " " + (r.get("claim") or "") for r in ledger)
        for m in macros:
            if m not in blob:
                B("MACRO", f"data macro [[v:{m}]] has no ledger row")
    return blocks, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    ap.add_argument("--article")
    ap.add_argument("--packet")
    ap.add_argument("--author")
    ap.add_argument("--build", action="store_true", help="also run python3 build.py --strict")
    ap.add_argument("--out")
    a = ap.parse_args()
    blocks, warns = check(rows_of(a.ledger), a.article, a.packet, a.author)
    build = None
    if a.build:
        p = subprocess.run([sys.executable, "build.py", "--strict"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        build = {"exit_code": p.returncode, "tail": p.stdout.strip().splitlines()[-2:]}
        if p.returncode != 0:
            blocks.append({"claim_id": "BUILD", "reason": "build.py --strict failed (R1/R2 or macro error)"})
    rep = {"result": "BLOCKED" if blocks else "READY", "ledger": str(a.ledger), "rows": len(rows_of(a.ledger)), "blocking": blocks, "warnings": warns, "build": build,
           "note": "READY means the ledger is complete and consistent. It does not approve publication: a person does that."}
    s = json.dumps(rep, indent=1)
    if a.out:
        Path(a.out).write_text(s, encoding="utf-8")
    print(s)
    return 2 if blocks else 0


if __name__ == "__main__":
    sys.exit(main())
