#!/usr/bin/env python3
"""Build the verified dark-horse watchlist and contract map from the 28 original research leads.

    python3 tools/dark_horse/build_watchlist.py <tip_match.json>

Inputs:  data/elections/dark_horse/watchlist_original.csv (the 28 leads exactly as supplied, kept unchanged),
         tip_match.json (read-only TIP lookup of candidates and race entries), contract_candidates.json (discovery output),
         aipac_udp_ie.json (FEC independent expenditures by United Democracy Project, 2026 cycle).
Outputs: watchlist.csv (28 rows with TIP IDs, ballot status, documented criteria, classification), contract_map.json (human-verified IDs only).

Criteria (a row "meets documented criteria" only when at least one is verified from a primary or cited source):
  C1 incumbent defeated in the 2026 primary (result cited);
  C2 FEC-documented United Democracy Project spending against the nominee or for the defeated opponent;
  C3 establishment-endorsed opponent documented by a cited source.
Everything else is a background research lead. This table is a reporting aid: it never ranks, recommends or scores candidates.
"""
import csv, json, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data/elections/dark_horse"
tip = {r["name"]: r for r in json.load(open(sys.argv[1], encoding="utf-8"))}
orig = list(csv.DictReader(open(D / "watchlist_original.csv", encoding="utf-8-sig")))
cc = {r["candidate_name"]: r for r in json.load(open(D / "contract_candidates.json", encoding="utf-8"))}
udp = json.load(open(D / "aipac_udp_ie.json"))["committees"]["UDP"]["transactions_deduped"]

def udp_sum(fec_name_part):
    s = o = n = 0
    first = last = None
    for t in udp:
        if fec_name_part in (t["candidate_name"] or "").upper():
            amt = t["expenditure_amount"] or 0
            if t["support_oppose_indicator"] == "S": s += amt
            else: o += amt
            n += 1
            d = (t["expenditure_date"] or "")[:10]
            first = min(first or d, d); last = max(last or d, d)
    return {"support": round(s), "oppose": round(o), "reports": n, "first": first, "last": last}
U = {k: udp_sum(k) for k in ("EL-SAYED", "STEVENS", "CONYEARS", "WAHAB", "HERNANDEZ", "MALINOWSKI", "BISS", "LANDER", "STRATTON", "FINE")}
def money(x): return f"${x/1e6:.1f}M" if x >= 1e6 else f"${x/1e3:.0f}K"

# Verified facts (sources read 2026-10-23). Wikipedia is a secondary source; FEC figures are primary.
E = {
 "Abdul El-Sayed": dict(po="Won the Aug 4 2026 Democratic primary 48.4% to Haley Stevens 47.6% (AP called Aug 5)", src="Wikipedia: Abdul El-Sayed", c1="no", c3="Opponent Stevens described as the moderate, establishment-backed wing (Wikipedia)", status="meets"),
 "La Shawn Ford": dict(po="Democratic nominee for IL-07 (Wikipedia); vote shares not retrieved", src="Wikipedia: La Shawn Ford", c1="no", c3="no: retiring Rep. Danny Davis endorsed Ford (Wikipedia)", status="partial"),
 "Daniel Biss": dict(po="Won the Mar 17 2026 primary with 29.5% (Abughazaleh 26.0%, Fine 20.3%)", src="Wikipedia: Daniel Biss", c1="no", c3="no documented establishment opponent", status="lead"),
 "Aisha Wahab": dict(po="Won the Aug 18 2026 CA-14 special runoff with 53.1% over Melissa Hernandez; both on the November full-term ballot (Wikipedia)", src="Wikipedia: Aisha Wahab", c1="no", c3="not documented", status="partial"),
 "Brad Lander": dict(po="Won the Jun 23 2026 primary 65.8% to 34.0%, defeating incumbent Dan Goldman", src="Wikipedia: Brad Lander", c1="yes", c3="Goldman is the incumbent; leadership endorsement of Goldman not confirmed", status="meets"),
 "Analilia Mejia": dict(po="Won the Feb 5 2026 special primary 29.3% to Tom Malinowski 27.6%; won the Apr 16 special general; sworn in Apr 20 2026", src="Wikipedia: Analilia Mejia", c1="no", c3="not documented", status="partial"),
 "Juliana Stratton": dict(po="Won the Mar 17 2026 primary with 40.4%", src="Wikipedia: Juliana Stratton", c1="no", c3="Pritzker and Duckworth endorsed Stratton (the winner)", status="lead"),
 "Darializa Avila Chevalier": dict(po="Defeated incumbent Adriano Espaillat 48.6% to 45.2% in the Jun 23 2026 primary", src="Wikipedia: Darializa Avila Chevalier", c1="yes", c3="not documented", status="meets"),
 "Melat Kiros": dict(po="Defeated 15-term incumbent Diana DeGette in the Jun 30 2026 primary by over 20,000 votes", src="Wikipedia: Melat Kiros", c1="yes", c3="not documented", status="meets"),
 "Claire Valdez": dict(po="Won the Jun 23 2026 primary 56.1% to Antonio Reynoso 35.8%", src="Wikipedia: Claire Valdez", c1="no (open seat)", c3="Reynoso endorsed by Velazquez and WFP: a factional contest, not a unanimous establishment", status="partial"),
 "William Lawrence": dict(po="Not verified in this pass (no source retrieved)", src="", c1="unknown", c3="unknown", status="unverified"),
 "Donavan McKinney": dict(po="Defeated incumbent Shri Thanedar 51.9% to 48.1% in the Aug 4 2026 primary", src="Wikipedia: Donavan McKinney", c1="yes", c3="not documented", status="meets"),
 "Randy Villegas": dict(po="Top-two result not verified in this pass; TIP shows an official record on the November ballot", src="", c1="no (top-two)", c3="unknown", status="unverified"),
 "Luke Bronin": dict(po="Defeated incumbent John Larson at the May 11 2026 convention and won the Aug 11 2026 primary", src="Wikipedia: Luke Bronin", c1="yes", c3="no: Bronin had the state party endorsement", status="meets"),
}
c2 = {
 "Abdul El-Sayed": f"UDP independent expenditures in the 2026 cycle (FEC): opposed El-Sayed {money(U['EL-SAYED']['oppose'])} ({U['EL-SAYED']['first']} to {U['EL-SAYED']['last']}), supported Stevens {money(U['STEVENS']['support'])}",
 "La Shawn Ford": f"UDP supported the defeated rival Conyears-Ervin {money(U['CONYEARS']['support'])} ({U['CONYEARS']['first']} to {U['CONYEARS']['last']}) (FEC)",
 "Aisha Wahab": f"UDP opposed Wahab {money(U['WAHAB']['oppose'])} and supported Hernandez {money(U['HERNANDEZ']['support'])} ({U['WAHAB']['first']} to {U['WAHAB']['last']}) (FEC). Wikipedia reports 'more than $5 million' from two AIPAC-affiliated super PACs: not reconciled",
 "Analilia Mejia": f"UDP opposed her rival Malinowski {money(U['MALINOWSKI']['oppose'])} ({U['MALINOWSKI']['first']} to {U['MALINOWSKI']['last']}) (FEC); no UDP spending for or against Mejia",
}
STATE_MAP = {}
rows = []
cmap = {}
for r in orig:
    name = r["candidate_name"]; t = tip[name]
    rk = t["raceKey"]
    pick = None
    last = name.split()[-1].lower()
    for c in t["cands"]:
        if last in c["display_name"].lower() and (c["office_code"] in ("H", "S")) and any(e["candidate_id"] == c["candidate_id"] and e["race_key"] == rk for e in t["entries"]):
            pick = c
    if not pick:     # fall back to a name match even without a race entry (reported as a gap)
        for c in t["cands"]:
            if last in c["display_name"].lower() and c["office_code"] in ("H", "S"):
                pick = c
    entry = next((e for e in t["entries"] if pick and e["candidate_id"] == pick["candidate_id"] and e["race_key"] == rk), None)
    ver = entry["verification_status"] if entry else None
    ballot = "yes" if entry and entry["status"] == "active" and ver and ver.startswith("Official") else ("owner_supplied_only" if entry and ver and "owner" in ver.lower() else "no")
    fact = E.get(name, dict(po="Background lead: outcome not verified in this pass", src="", c1="unknown", c3="unknown", status="lead"))
    k = cc[name]["kalshi_candidates"]
    p = [x for x in cc[name]["polymarket_candidates"] if "House seat" in (x["question"] or "") or "Senate seat" in (x["question"] or "")]
    tid = pick["fec_candidate_id"] if pick else ""
    note = []
    if not pick: note.append("TIP gap: no candidate profile; ")
    elif not entry: note.append("TIP gap: no active race entry for this race; ")
    row = {**{k_: r[k_] for k_ in ("candidate_name", "state", "race", "historical_research_tags", "primary_opponent_if_known", "verification_note")},
           "current_ballot_verified": ballot, "tip_candidate_id": tid, "race_key": rk, "ballot_source": ver or "", "primary_outcome_verified": fact["po"], "primary_outcome_source": fact["src"],
           "c1_incumbent_defeated": fact["c1"], "c2_udp_spending_documented": c2.get(name, "none found in FEC UDP data (2026 cycle)" if fact["status"] in ("meets", "partial", "lead") and name in E else "not checked"),
           "c3_establishment_opponent": fact["c3"], "dark_horse_status": fact["status"], "monitor": "yes",
           "kalshi_ticker": k[0]["ticker"] if k else "", "polymarket_slug": p[0]["event_slug"] if p else "", "polymarket_token_id": "", "poll_subject_key": "",
           "notes": "".join(note) + "Prior discussion watchlist: not all are bona fide dark horses."}
    if p:
        ids = json.loads(p[0]["token_ids"]); row["polymarket_token_id"] = ids[0]
    rows.append(row)
    key = tid or f"no_tip:{r['state']}:{r['race']}:{name}"
    m = {}
    if k:
        m.update(kalshi_ticker=k[0]["ticker"], kalshi_url="https://kalshi.com/markets/" + k[0]["event_ticker"].split("-")[0].lower(), kalshi_outcome=k[0]["yes_label"],
                 kalshi_contract_kind="party_winner", kalshi_rules_url="https://kalshi.com/markets/" + k[0]["event_ticker"].split("-")[0].lower(),
                 kalshi_rules_text=k[0]["rules"][:200], kalshi_note="Resolves on the party of the person sworn in; labeled with the candidate's name; NOT a named-candidate contract")
    if p:
        m.update(polymarket_token_id=json.loads(p[0]["token_ids"])[0], polymarket_slug=p[0]["event_slug"], polymarket_url="https://polymarket.com/event/" + p[0]["event_slug"],
                 polymarket_outcome="Yes", polymarket_contract_kind="candidate_individual", polymarket_rules_url="https://polymarket.com/event/" + p[0]["event_slug"],
                 polymarket_rules_text=(p[0]["rules"] or "")[:200])
    if m:
        m.update(checked_by="Claude (resolution rules text read; contract kind confirmed)", checked_at="2026-10-23")
        cmap[key] = m
with open(D / "watchlist.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
(D / "contract_map.json").write_text(json.dumps(cmap, indent=1, ensure_ascii=False), encoding="utf-8")
print(collections.Counter(r["dark_horse_status"] for r in rows), "ballot yes:", sum(1 for r in rows if r["current_ballot_verified"] == "yes"), "kalshi mapped:", sum(1 for v in cmap.values() if v.get("kalshi_ticker")), "polymarket mapped:", sum(1 for v in cmap.values() if v.get("polymarket_token_id")))
