#!/usr/bin/env python3
"""Reconcile a Schedule E pull (fetch_fec_ie.py output) for one House race: notices (F24/F5) against periodic-report rows (F3X).

    python3 tools/elections/reconcile_ie.py productions/2026/MI/research/fec_ie_MI10_MI13.json productions/2026/MI/research/fec_committees_MI10.json OUT.json H6MI10276 H6MI10359

Why a second pass: tools/dark_horse/schedule_e.dedupe keys on transaction_id, amount and exact date. Some committees number the same payment differently on the
notice and on the periodic report (SE.5443 on the F24, SE.5435 on the F3X) or date it a day apart, so the two rows survive and the committee is counted twice.
This pass pairs each F3X row with at most one notice row from the same committee, same support/oppose, same amount to the cent, dates within 7 days, and keeps the notice. Payee is not compared: Pro-Choice Majority Action's notice and report name different payees for one identical payment.
It does not touch the shared function, so published Florida and Illinois numbers are unchanged; check them before reusing this pass there.
Memo rows (memo_code X) are dropped. Amendments keep the latest row as the pull already requested most_recent. Notice amounts can be labeled ESTIMATE by the filer.
"""
import sys, json, re, datetime, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/dark_horse"))
from schedule_e import dedupe

pull_p, comm_p, out_p, *fids = sys.argv[1:]
pull = json.loads(Path(pull_p).read_text(encoding="utf-8"))
comm = json.loads(Path(comm_p).read_text(encoding="utf-8"))["committees"]
norm = lambda s: re.sub(r"[^A-Z0-9]", "", (s or "").upper())
day = lambda r: datetime.date.fromisoformat((r.get("expenditure_date") or r.get("dissemination_date"))[:10])
CUT = "2026-10-24"  # latest dissemination date in the pull; later-dated rows are reported separately


def second_pass(rows):
    notices = [r for r in rows if r["filing_form"] in ("F24", "F5")]
    periodic = [r for r in rows if r["filing_form"] == "F3X"]
    used, paired = set(), 0
    for p in periodic:
        for i, n in enumerate(notices):
            if i in used or n["committee_id"] != p["committee_id"] or n["support_oppose_indicator"] != p["support_oppose_indicator"]:
                continue
            if abs(n["expenditure_amount"] - p["expenditure_amount"]) > 0.005:
                continue
            if abs((day(n) - day(p)).days) <= 7:
                used.add(i); p["_paired"] = True; paired += 1
                break
    kept = notices + [p for p in periodic if not p.get("_paired")]
    return kept, paired


result = {"basis": __doc__.strip().splitlines()[0], "dissemination_cut": CUT, "pull_captured_at_utc": pull["captured_at_utc"], "candidates": {}}
for fid in fids:
    c = pull["candidates"][fid]
    rows, memo = dedupe(c["transactions"])
    after_first = sum(r["expenditure_amount"] for r in rows)
    rows, paired = second_pass(rows)
    late = [r for r in rows if (r.get("dissemination_date") or "")[:10] > CUT or day(r) > datetime.date.fromisoformat("2026-10-28")]
    roll = {(r["committee_id"], r["support_oppose_indicator"]): r for r in c["by_candidate_totals"]}
    by = collections.defaultdict(lambda: {"total": 0.0, "n": 0, "first": "9", "last": "0", "forms": set()})
    for r in rows:
        b = by[(r["committee_id"], r["support_oppose_indicator"])]
        d = (r.get("dissemination_date") or r["expenditure_date"])[:10]
        b["total"] += r["expenditure_amount"]; b["n"] += 1; b["first"] = min(b["first"], d); b["last"] = max(b["last"], d); b["forms"].add(r["filing_form"])
    out = []
    for (cid, so), b in by.items():
        rr = roll.get((cid, so)); m = comm.get(cid, {})
        out.append({"committee_id": cid, "committee": m.get("name"), "committee_type": m.get("committee_type_full"), "org_type": m.get("organization_type_full"),
                    "so": so, "total": round(b["total"], 2), "n": b["n"], "first": b["first"], "last": b["last"], "forms": sorted(b["forms"]),
                    "fec_rollup_total": rr["total"] if rr else None, "fec_rollup_count": rr["count"] if rr else None})
    out.sort(key=lambda r: -r["total"])
    result["candidates"][fid] = {
        "name": c["name"], "rows_after_first_pass": len(c["transactions"]) - memo, "paired_and_removed": paired, "memo_dropped": memo,
        "total_after_first_pass": round(after_first, 2), "support": round(sum(r["total"] for r in out if r["so"] == "S"), 2),
        "oppose": round(sum(r["total"] for r in out if r["so"] == "O"), 2),
        "rows_dated_after_2026-10-24_dissemination_or_2026-10-28_expenditure": [{k: r[k] for k in ("committee_name", "expenditure_amount", "expenditure_date", "dissemination_date", "filing_form")} for r in late],
        "committees": out}
Path(out_p).write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
for fid, v in result["candidates"].items():
    print(f"{v['name']}: first pass {v['total_after_first_pass']:,.2f} -> paired {v['paired_and_removed']} rows -> support {v['support']:,.2f} oppose {v['oppose']:,.2f}; late-dated rows {len(v['rows_dated_after_2026-10-24_dissemination_or_2026-10-28_expenditure'])}")
