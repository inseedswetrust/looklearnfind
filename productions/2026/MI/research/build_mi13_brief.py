"""Write the MI-A3 STORY_BRIEF.md and CLAIMS.csv from the reconciled MI-13 FEC data (so every number is computed, not typed).

    python productions/2026/MI/research/build_mi13_brief.py
Inputs: mi13_reconciled.json, fec_totals_MI13.json, fec_ie_MI13.json (same folder). Output: ../package_src/stories/MI-A3/
"""
import csv, json
from pathlib import Path

H = Path(__file__).parent
OUT = H.parent / "package_src/stories/MI-A3"
OUT.mkdir(parents=True, exist_ok=True)
rec = json.loads((H / "mi13_reconciled.json").read_text(encoding="utf-8"))
tot = json.loads((H / "fec_totals_MI13.json").read_text(encoding="utf-8"))["totals"]
pull = json.loads((H / "fec_ie_MI13.json").read_text(encoding="utf-8"))
MK, TH = rec["candidates"]["H6MI13254"], rec["candidates"]["H2MI13204"]
mk_t, th_t = tot["H6MI13254"][0], tot["H2MI13204"][0]
m = lambda x: f"${x:,.2f}"
by = lambda c, cid, so: next((x for x in c["committees"] if x["committee_id"] == cid and x["so"] == so), None)
PP_S, PP_O = by(TH, "C00848440", "S"), by(MK, "C00848440", "O")
JD_S, JD_O = by(MK, "C00630665", "S"), by(TH, "C00630665", "O")
WFP, NNU = by(MK, "C00606962", "S"), by(MK, "C00490375", "S")
AP = by(MK, "C00932723", "S")
dates = sorted(r["expenditure_date"][:10] for c in pull["candidates"].values() for r in c["transactions"] if (r.get("expenditure_amount") or 0) > 0)
first, last = dates[0], dates[-1]
pp_total = PP_S["total"] + PP_O["total"]
udp_rows = [r for c in pull["candidates"].values() for r in c["transactions"] if r["committee_id"] == "C00799031"]
assert not udp_rows, "UDP appears in the pull; rewrite the negative claim"
cap = pull["captured_at_utc"]
EV = f"productions/2026/MI/research/mi13_reconciled.json (computed by tools/elections/reconcile_ie.py from fec_ie_MI13.json, pulled {cap})"
FEC = "https://api.open.fec.gov/developers/"
WDIV = "https://gmg-wdiv-prod.cdn.arcpublishing.com/news/local/2026/08/05/donavan-mckinney-wins-us-house-district-13-democratic-primary-election-ap-projects/"
BRIDGE = "https://bridgemi.com/michigan-government/michigan-congressional-primary-results-races-to-watch-as-votes-are-tallied/"

brief = f"""# MI-A3: Who spent in Michigan's 13th District Democratic primary, where the incumbent lost

As of 2026-10-31 (FEC data retrieved {cap}; the latest expenditure in the pull is dated {last}) · Status: READY · Race: https://theissuesparty.org/races/2026-H-MI-13 · Format: Spending Report (schema 03, `docs/schemas/03_SPENDING_REPORT.md`) · Length: 800 to 1,100 words

## The one-sentence story
In the August 4 Democratic primary in Michigan's 13th District, Donavan McKinney beat Rep. Shri Thanedar, 52 percent to 48 percent in the final table WDIV published; FEC filings show outside committees reported about {m(MK['support'])} supporting McKinney and {m(TH['support'])} supporting Thanedar, and one committee, Protect Progress, reported {m(pp_total)} in all (supporting Thanedar {m(PP_S['total'])} and opposing McKinney {m(PP_O['total'])}).

## The conflict and the insight
**Conflict:** an incumbent first elected in 2022 (per Bridge Michigan) whose committee reported {m(th_t['last_cash_on_hand_end_period'])} cash on hand at Sept 30 (and {m(th_t['loans_made_by_candidate'])} in loans he made to it this cycle, per FEC) lost to a challenger whose committee reported {m(mk_t['receipts'])} in receipts through Oct 14. The two dates differ, so the brief does not compare them. **Insight:** the outside money reported in support of each candidate was close ({m(MK['support'])} and {m(TH['support'])}), and the biggest single reporter spent on Thanedar's side. Show who spent for each candidate and against each, dated, and say plainly what the filings do not establish.

State that these are figures committees reported to the FEC, that notice amounts are the filer's own and may change, and that spending is not the same as ads aired or votes moved. Do not say what the money did. Do not say the result was caused by anything.

## Verified facts (all in `CLAIMS.csv`; numbers computed from the files in `inputs/MI-A3/`)
**The result (attributed, unofficial):** WDIV ClickOnDetroit's final table, published Aug 5, 2026, lists McKinney 57,714 (52%) and Thanedar 53,494 (48%) with 100 percent of precincts (346 of 346) and says the Associated Press projected McKinney the winner. The page does not say the figures are unofficial or when AP called it. We could not read the official canvass (the Bureau of Elections results site refused connections), so call the figures "unofficial results published by WDIV". Bridge Michigan (Aug 5) reports AP called the race for McKinney and that Thanedar was first elected in 2022.

**Outside spending reported to the FEC (Schedule E), {first} to {last}, memo rows dropped and each periodic-report row paired with its notice so nothing counts twice:**
| Candidate | Reported supporting | Reported opposing |
|---|---|---|
| Donavan McKinney (D) | {m(MK['support'])} | {m(MK['oppose'])} |
| Shri Thanedar (D) | {m(TH['support'])} | {m(TH['oppose'])} |

**Largest reporters** (names as FEC lists them; committee type as FEC lists it):
- Protect Progress (C00848440, Super PAC, independent expenditure-only): supporting Thanedar {m(PP_S['total'])} ({PP_S['n']} rows, {PP_S['first']} to {PP_S['last']}); opposing McKinney {m(PP_O['total'])} ({PP_O['n']} rows, {PP_O['first']} to {PP_O['last']}).
- Justice Democrats PAC (C00630665, hybrid PAC): supporting McKinney {m(JD_S['total'])} ({JD_S['n']} rows); opposing Thanedar {m(JD_O['total'])} ({JD_O['n']} rows).
- Working Families Party PAC (C00606962, hybrid PAC): supporting McKinney {m(WFP['total'])} ({WFP['n']} rows).
- National Nurses United for Patient Protection (C00490375, Super PAC): supporting McKinney {m(NNU['total'])} (one row, {NNU['first']}).
- American Priorities (AP) (C00932723, Super PAC): supporting McKinney {m(AP['total'])}.
- {len(MK['committees']) - 5} other committees reported spending on McKinney's side and {len(TH['committees']) - 2} on Thanedar's side, each smaller (see `mi13_reconciled.json`).

**The United Democracy Project does not appear.** The committee ID C00799031 has no Schedule E row for either candidate in this pull. A search summary had said AIPAC and others backed Thanedar; the filings we pulled show no spending by UDP in this race. Say only that; do not describe any committee's alignment (see unknowns).

**Candidate committees (cycle to date, FEC candidate totals):** McKinney (H6MI13254), through Oct 14 (PRE-GENERAL): receipts {m(mk_t['receipts'])}, disbursements {m(mk_t['disbursements'])}, cash on hand {m(mk_t['last_cash_on_hand_end_period'])}. Thanedar (H2MI13204), through Sept 30 (OCTOBER QUARTERLY): receipts {m(th_t['receipts'])}, disbursements {m(th_t['disbursements'])}, cash on hand {m(th_t['last_cash_on_hand_end_period'])}, loans made by the candidate {m(th_t['loans_made_by_candidate'])}. The two coverage dates differ, so do not set the receipts side by side as if they were comparable; the candidate totals are cycle to date and include the general-election period for McKinney.

**What happens next:** McKinney is the Democratic nominee in the November general election; the Republican nominee on the Department of State's listing is T.P. Nykoriak (listed as "Nykoriak, T.P."). No outside spending for or against Nykoriak appears in the FEC pull. No poll and no Kalshi contract was found for this district.

## Suggested hook and headlines
- "An incumbent lost his primary. Outside groups reported about the same amount in support of each candidate."
- "Who spent in Michigan's 13th District primary, and where the money went."
Dek idea: McKinney won 52 to 48 in unofficial results. FEC filings show {m(MK['support'])} reported for McKinney and {m(TH['support'])} for Thanedar, with one committee behind {m(pp_total)} on Thanedar's side of the race.

## Structure that fits (schema 03)
1. The result, attributed and marked unofficial; then the headline figure.
2. The filings: who reported, support or oppose, notice versus periodic report, dates (all June to August).
3. Protect Progress in detail, then Justice Democrats PAC, Working Families Party PAC and the rest, grouped by committee type as FEC lists it.
4. The candidates' own committees (state the different coverage dates).
5. What the filings do not establish: ads aired, effect, coordination, who funds each committee, why each spent.
6. What happens next (general election). Table and flow graphic.

## TIP
McKinney https://theissuesparty.org/candidates/H6MI13254 · Thanedar https://theissuesparty.org/candidates/H2MI13204 (R1: link both on first mention) · Race https://theissuesparty.org/races/2026-H-MI-13 · Nykoriak https://theissuesparty.org/candidates/H6MI13312 · LLF district page https://looklearnfind.com/elections/2026/michigan/house/13/. **No grades are used**: neither primary candidate's TIP profile needs one for this story; do not cite a grade, and "not graded" is not a score of zero.

## Unknowns and factual risks (write around them)
- **Official result.** The August 4 canvass was not read. Use "unofficial results published by WDIV" and the AP projection as reported by WDIV and Bridge.
- **Alignment and funders.** The FEC committee record carries no party or alignment for these committees, and we did not open a source describing who funds Protect Progress, Justice Democrats PAC or the others. Do not call any committee aligned with a party, industry or movement; say whom it supported or opposed as the filing records.
- **Estimates.** Notice amounts are the filer's own and later reports may change them. Say "reported".
- **Roll-up differences.** FEC's own by-candidate roll-up lags 24/48-hour notices; some committee lines differ from the sums here (for example Working Families Party PAC supporting McKinney: roll-up {m(WFP['fec_rollup_total'])}, notices and reports together {m(WFP['total'])}). The package's totals follow the pairing method in `reconcile_ie.py`.
- **Not used, on purpose:** nothing about T.P. Nykoriak's past (no court record was opened, no response sought); endorsements seen only in search summaries; any 2022 or 2024 figures about Thanedar; the Michigan Advance analysis (HTTP 403, not circumvented).
- **Do not add** supporting and opposing totals as one pool of money.
- No causal claims, no win probabilities, no endorsements, no rankings.
"""
(OUT / "STORY_BRIEF.md").write_text(brief, encoding="utf-8", newline="\n")

rows = []
def add(claim, loc, url, d, status, typ, ev):
    rows.append([claim, loc, url, d, "", status, typ, ev])
add("WDIV's final table lists McKinney 57,714 (52%) and Thanedar 53,494 (48%) with 346 of 346 precincts and says AP projected McKinney", "lede", WDIV, "2026-08-05", "ATTRIBUTED", "number", "WDIV ClickOnDetroit; opened and read by LLF 2026-10-28; unofficial; canvass not read")
add("Bridge Michigan reports AP called the race for McKinney and that Thanedar was first elected in 2022", "result", BRIDGE, "2026-08-05", "ATTRIBUTED", "status", "Bridge Michigan (Jordyn Hermani); opened and read by LLF 2026-10-28")
for cand, c in (("McKinney", MK), ("Thanedar", TH)):
    add(f"Outside committees reported {m(c['support'])} supporting and {m(c['oppose'])} opposing {cand} (Schedule E, {first} to {last})", "lede / table", FEC, cap[:10], "VERIFIED", "number", EV)
for label, x, cand, so in (("Protect Progress", PP_S, "Thanedar", "supporting"), ("Protect Progress", PP_O, "McKinney", "opposing"), ("Justice Democrats PAC", JD_S, "McKinney", "supporting"),
                           ("Justice Democrats PAC", JD_O, "Thanedar", "opposing"), ("Working Families Party PAC", WFP, "McKinney", "supporting"),
                           ("National Nurses United for Patient Protection", NNU, "McKinney", "supporting"), ("American Priorities (AP)", AP, "McKinney", "supporting")):
    add(f"{label} reported {m(x['total'])} {so} {cand} in {x['n']} Schedule E row(s), disseminated {x['first']} to {x['last']}", "committees", f"https://www.fec.gov/data/committee/{x['committee_id']}/", cap[:10], "VERIFIED", "number",
        EV + f"; FEC committee {x['committee_id']}, type '{x['committee_type']}'")
add(f"Protect Progress's two lines together total {m(pp_total)}", "lede", "https://www.fec.gov/data/committee/C00848440/", cap[:10], "VERIFIED", "number", EV)
add("The United Democracy Project (C00799031) has no Schedule E row for either candidate in the FEC pull", "udp", "https://www.fec.gov/data/committee/C00799031/", cap[:10], "VERIFIED", "absence", "productions/2026/MI/research/fec_ie_MI13.json (no row with committee_id C00799031)")
add(f"McKinney's committee reported receipts of {m(mk_t['receipts'])}, disbursements of {m(mk_t['disbursements'])} and cash on hand of {m(mk_t['last_cash_on_hand_end_period'])} through Oct 14 2026 (PRE-GENERAL)", "committees", "https://www.fec.gov/data/candidate/H6MI13254/", cap[:10], "VERIFIED", "number", "productions/2026/MI/research/fec_totals_MI13.json")
add(f"Thanedar's committee reported receipts of {m(th_t['receipts'])}, disbursements of {m(th_t['disbursements'])}, cash on hand of {m(th_t['last_cash_on_hand_end_period'])} and loans from the candidate of {m(th_t['loans_made_by_candidate'])} through Sept 30 2026 (OCTOBER QUARTERLY)", "committees", "https://www.fec.gov/data/candidate/H2MI13204/", cap[:10], "VERIFIED", "number", "productions/2026/MI/research/fec_totals_MI13.json")
add("The Republican nominee on the Department of State general-election listing for MI-13 is listed as 'Nykoriak, T.P.'", "race", "https://mi-boe.entellitrak.com/etk-mi-boe-prod/page.request.do?page=page.miboePublicReport&electionType=GEN&electionYear=2026", "2026-10-28", "VERIFIED", "name", "data/elections/MI/captures/boe_text.txt")
add("No outside spending for or against Nykoriak appears in the FEC pull", "race", FEC, cap[:10], "VERIFIED", "absence", "productions/2026/MI/research/fec_ie_MI13.json covers McKinney and Thanedar only; Nykoriak's FEC candidate pull in fec_ie_MI10_MI13.json shows 0 rows")
add("Official canvass for the August 4 primary was not read", "unknowns", "", "2026-10-28", "UNKNOWN", "absence", "productions/2026/MI/research/MI-A3_SOURCES.md")
with open(OUT / "CLAIMS.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["claim", "text_location", "source_url", "source_date", "checked_date", "status", "type", "evidence_ref"])
    w.writerows(rows)
print("MI-A3 brief and", len(rows), "claims written to", OUT)
