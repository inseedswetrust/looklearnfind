import json, sys, datetime, collections
from pathlib import Path
R = Path(r"C:\Users\Red Right Hand\Desktop\Issues Party\looklearnfind")
sys.path.insert(0, str(R / "tools/dark_horse"))
from schedule_e import dedupe as sdedupe


def dedupe_ie(rows):  # copy of elections.dedupe_ie (what Florida pages use)
    best = {}
    for r in rows:
        if r.get("memo_code") == "X":
            continue
        k = (r.get("committee_name"), r.get("transaction_id"), r.get("expenditure_amount"), (r.get("expenditure_date") or "")[:10])
        if k not in best or (r.get("is_notice") and not best[k].get("is_notice")):
            best[k] = r
    return list(best.values())


day = lambda r: datetime.date.fromisoformat((r.get("expenditure_date") or r.get("dissemination_date"))[:10])


def pairs(rows):
    notices = [r for r in rows if r.get("filing_form") in ("F24", "F5")]
    periodic = [r for r in rows if r.get("filing_form") == "F3X"]
    used, hits = set(), []
    for p in periodic:
        for i, n in enumerate(notices):
            if i in used or n["committee_id"] != p["committee_id"] or n.get("support_oppose_indicator") != p.get("support_oppose_indicator"):
                continue
            if abs(n["expenditure_amount"] - p["expenditure_amount"]) > 0.005:
                continue
            if abs((day(n) - day(p)).days) <= 7:
                used.add(i); hits.append((n, p)); break
    return hits


def run(label, path, fn):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    tot_all = tot_dbl = nh = 0
    per = []
    forms = collections.Counter()
    for fid, c in d["candidates"].items():
        rows = fn(c["transactions"])
        if isinstance(rows, tuple):
            rows = rows[0]
        rows = [r for r in rows if (r.get("expenditure_amount") or 0) > 0]
        for r in rows:
            forms[r.get("filing_form")] += 1
        h = pairs(rows)
        s = sum(r["expenditure_amount"] for r in rows)
        dbl = sum(p["expenditure_amount"] for n, p in h)
        tot_all += s; tot_dbl += dbl; nh += len(h)
        if h:
            per.append((c.get("name"), c.get("race"), round(s, 2), len(h), round(dbl, 2)))
    print(f"\n== {label}: {path.split(chr(92))[-1] if False else Path(path).name}")
    print("candidates", len(d["candidates"]), "rows by form", dict(forms))
    print(f"total after existing dedupe {tot_all:,.2f}; probable double-counted pairs {nh}; overcount {tot_dbl:,.2f}")
    for x in sorted(per, key=lambda x: -x[4])[:15]:
        print("  ", x)


run("Florida (elections.dedupe_ie)", R / "data/elections/FL/ie_all.json", dedupe_ie)
run("Florida (schedule_e.dedupe)", R / "data/elections/FL/ie_all.json", sdedupe)
run("Dark horse AIPAC/UDP (schedule_e.dedupe)", R / "data/elections/dark_horse/aipac_udp_ie.json", sdedupe)
