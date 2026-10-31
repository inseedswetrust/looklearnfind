# MI-A3: Who spent in Michigan's 13th District Democratic primary, where the incumbent lost

As of 2026-10-31 (FEC data retrieved 2026-10-31T18:33:29Z; the latest dissemination date in the pull is 2026-08-04) · Status: READY · Race: https://theissuesparty.org/races/2026-H-MI-13 · Format: Spending Report (schema 03, `docs/schemas/03_SPENDING_REPORT.md`) · Length: 800 to 1,100 words

## The one-sentence story
In the August 4 Democratic primary in Michigan's 13th District, Donavan McKinney beat Rep. Shri Thanedar, 52 percent to 48 percent in the final table WDIV published; FEC filings show outside committees reported about $1,727,586.94 supporting McKinney and $1,848,181.00 supporting Thanedar, and one committee, Protect Progress, reported $2,043,345.00 in all (supporting Thanedar $1,774,655.00 and opposing McKinney $268,690.00).

## The conflict and the insight
**Conflict:** an incumbent first elected in 2022 (per Bridge Michigan) whose committee reported $5,935,390.40 cash on hand at Sept 30 (and $2,970,000.00 in loans he made to it this cycle, per FEC) lost to a challenger whose committee reported $1,876,779.88 in receipts through Oct 14. The two dates differ, so the brief does not compare them. **Insight:** the outside money reported in support of each candidate was close ($1,727,586.94 and $1,848,181.00), and the biggest single reporter spent on Thanedar's side. Show who spent for each candidate and against each, dated, and say plainly what the filings do not establish.

State that these are figures committees reported to the FEC, that notice amounts are the filer's own and may change, and that spending is not the same as ads aired or votes moved. Do not say what the money did. Do not say the result was caused by anything.

## Verified facts (all in `CLAIMS.csv`; numbers computed from the files in `inputs/MI-A3/`)
**The result (attributed, unofficial):** WDIV ClickOnDetroit's final table, published Aug 5, 2026, lists McKinney 57,714 (52%) and Thanedar 53,494 (48%) with 100 percent of precincts (346 of 346) and says the Associated Press projected McKinney the winner. The page does not say the figures are unofficial or when AP called it. We could not read the official canvass (the Bureau of Elections results site refused connections), so call the figures "unofficial results published by WDIV". Bridge Michigan (Aug 5) reports AP called the race for McKinney and that Thanedar was first elected in 2022.

**Outside spending reported to the FEC (Schedule E), 2026-01-08 to 2026-08-04, memo rows dropped and each periodic-report row paired with its notice so nothing counts twice:**
| Candidate | Reported supporting | Reported opposing |
|---|---|---|
| Donavan McKinney (D) | $1,727,586.94 | $268,690.00 |
| Shri Thanedar (D) | $1,848,181.00 | $463,165.48 |

**Largest reporters** (names as FEC lists them; committee type as FEC lists it):
- Protect Progress (C00848440, Super PAC, independent expenditure-only): supporting Thanedar $1,774,655.00 (4 rows, 2026-07-18 to 2026-07-28); opposing McKinney $268,690.00 (5 rows, 2026-07-17 to 2026-07-29).
- Justice Democrats PAC (C00630665, hybrid PAC): supporting McKinney $460,546.70 (12 rows); opposing Thanedar $428,888.39 (11 rows).
- Working Families Party PAC (C00606962, hybrid PAC): supporting McKinney $427,788.40 (22 rows).
- National Nurses United for Patient Protection (C00490375, Super PAC): supporting McKinney $400,000.00 (one row, 2026-06-18).
- American Priorities (AP) (C00932723, Super PAC): supporting McKinney $150,000.00.
- 13 other committees reported spending on McKinney's side and 4 on Thanedar's side, each smaller (see `mi13_reconciled.json`).

**The United Democracy Project does not appear.** The committee ID C00799031 has no Schedule E row for either candidate in this pull. A search summary had said AIPAC and others backed Thanedar; the filings we pulled show no spending by UDP in this race. Say only that; do not describe any committee's alignment (see unknowns).

**Candidate committees (cycle to date, FEC candidate totals):** McKinney (H6MI13254), through Oct 14 (PRE-GENERAL): receipts $1,876,779.88, disbursements $1,747,106.34, cash on hand $129,673.54. Thanedar (H2MI13204), through Sept 30 (OCTOBER QUARTERLY): receipts $3,194,222.05, disbursements $4,163,399.35, cash on hand $5,935,390.40, loans made by the candidate $2,970,000.00. The two coverage dates differ, so do not set the receipts side by side as if they were comparable; the candidate totals are cycle to date and include the general-election period for McKinney.

**What happens next:** McKinney is the Democratic nominee in the November general election; the Republican nominee on the Department of State's listing is T.P. Nykoriak (listed as "Nykoriak, T.P."). No outside spending for or against Nykoriak appears in the FEC pull. No poll and no Kalshi contract was found for this district.

## Suggested hook and headlines
- "An incumbent lost his primary. Outside groups reported about the same amount in support of each candidate."
- "Who spent in Michigan's 13th District primary, and where the money went."
Dek idea: McKinney won 52 to 48 in unofficial results. FEC filings show $1,727,586.94 reported for McKinney and $1,848,181.00 for Thanedar, with one committee behind $2,043,345.00 on Thanedar's side of the race.

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
- **Roll-up differences.** FEC's own by-candidate roll-up lags 24/48-hour notices; some committee lines differ from the sums here (for example Working Families Party PAC supporting McKinney: roll-up $297,869.11, notices and reports together $427,788.40). The package's totals follow the pairing method in `reconcile_ie.py`.
- **Not used, on purpose:** nothing about T.P. Nykoriak's past (no court record was opened, no response sought); endorsements seen only in search summaries; any 2022 or 2024 figures about Thanedar; the Michigan Advance analysis (HTTP 403, not circumvented).
- **Do not add** supporting and opposing totals as one pool of money.
- No causal claims, no win probabilities, no endorsements, no rankings.
