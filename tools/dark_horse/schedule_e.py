"""FEC Schedule E de-duplication shared by the AIPAC/UDP pull and the research packet export.

The same independent expenditure can appear as a 24/48-hour notice (F24) and again in a periodic report (F3X). Memo rows (memo_code 'X') repeat
a line already reported. We keep one row per (transaction_id, amount, date, candidate, support/oppose), prefer the notice, count what was
collapsed and what memo rows were dropped. Rows with a different amount are different rows: an amendment is never merged away.
"""


def dedupe(rows):
    seen, memo = {}, 0
    for r in rows:
        if r.get("memo_code") == "X":
            memo += 1
            continue
        k = (r.get("transaction_id"), r.get("expenditure_amount"), (r.get("expenditure_date") or "")[:10], r.get("candidate_id"), r.get("support_oppose_indicator"))
        if k not in seen:
            seen[k] = {"row": r, "collapsed": 0}
        else:
            seen[k]["collapsed"] += 1
            if r.get("is_notice") and not seen[k]["row"].get("is_notice"):
                seen[k]["row"] = r
    return [dict(v["row"], duplicates_collapsed=v["collapsed"]) for v in seen.values()], memo
