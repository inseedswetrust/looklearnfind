# MI-A4: Who is spending in Michigan's open 10th District (U.S. House)

As of 2026-10-28 (FEC data retrieved 2026-10-28 22:07 UTC; latest notice disseminated 2026-10-24) · Status: READY · Race: https://theissuesparty.org/races/2026-H-MI-10 · Format: Spending Report (schema 03, `docs/schemas/03_SPENDING_REPORT.md`) · Length: 800 to 1,100 words

## The one-sentence story
In Michigan's open 10th District, outside groups reported spending $10.1 million against Republican Mike Bouchard and $4.2 million against Democrat Christina Hines through October 24, and one committee, HMP, accounts for $7.2 million of the Bouchard figure, almost all of it three television buys it labeled as estimates.

## The conflict and the insight
**Conflict:** an open seat (Rep. John James is running for governor) with two candidates whose own committees raised a combined $7.0 million through October 14 and outside groups reporting more than twice that against the two of them. **Insight:** one number is not one thing. FEC's own by-candidate total for HMP against Bouchard is $175,719 while the 24-hour notices add up to $7.2 million. Both are true: the first is what periodic reports had recorded through September 22 and the second is what notices have recorded through October 24. A reader who sees only one will be badly misled, so the piece shows both, dated, and says which is which.

State plainly that the figures are what committees reported to the FEC, that notice amounts are the filer's own estimates, and that spending is not the same as ads aired or votes moved. Do not say what the money did.

## Verified facts (all in `CLAIMS.csv`; every number is computed from the FEC files in `inputs/MI-A4/` (`mi10_reconciled.json`, `fec_ie_MI10_MI13.json`, `fec_committees_MI10.json`, `fec_totals_MI10.json`, `reconcile_ie.py`))
**Totals reported by outside committees (Schedule E), through Oct 24 dissemination, memo rows dropped and each periodic-report row paired with its notice so nothing counts twice:**
| Candidate | Reported supporting | Reported opposing |
|---|---|---|
| Christina Hines (D) | $2,537,611.79 | $4,164,104.66 |
| Mike Bouchard (R) | $918,413.55 | $10,135,610.20 |

**Largest reporters by side** (name as FEC lists it; form type in brackets):
- Opposing Bouchard: HMP $7,212,674.95 (23 notices, Sept 15 to Oct 24); LCV Victory Fund $564,922.84; Ready for the Fight $563,901.80; Giffords PAC $472,065.90; American Federation of State County & Municipal Employees P E O P L E (FEC's spelling) $459,500.00.
- Supporting Bouchard: No Going Back PAC Inc. $372,461.54; Honor, Duty & Discipline PAC $352,983.87; Patriotic Fund, Inc. $106,621.84; America PAC $77,601.84.
- Opposing Hines: CLF $2,659,832.86 (five periodic-report rows only, Sept 23 to 30); Restoration of America PAC $1,059,150.00 (two notices, Oct 6); No Going Back PAC Inc. $206,626.19; America PAC $201,164.59.
- Supporting Hines: Pro-Choice Majority Action $499,999.87 (July); Giffords PAC $495,191.89; HMP $310,296.80; CFFE PAC $279,679.91; Progressive Turnout Project $144,851.65; American Democracy Committee $125,588.00.

**HMP against Bouchard:** three television-advertising notices, all labeled "ESTIMATE" by the filer, paid to Waterfront Strategies Inc.: $1,553,580.00 (Oct 6), $1,655,618.40 (Oct 13) and $2,752,423.20 (Oct 20), together $5,961,621.60, about 83 percent of HMP's $7.2 million against him.

**The two numbers, reconciled.** FEC's by-candidate roll-up equals the sum of periodic-report (F3X) rows exactly in all 13 committee-and-side lines we could compare (for example HMP against Bouchard $175,718.76, the four September rows). It stops at each committee's last periodic report (late September for most; July for Honor, Duty & Discipline and Pro-Choice Majority Action). Notices (F24 and F5) fill the gap after that. Where both forms exist for the same payment they carry different transaction numbers or dates a day apart for some committees, which is why a simple de-duplication double counts them; `tools/elections/reconcile_ie.py` pairs them. Counting both would have put Hines's supporting total at $2.8 million and Bouchard's opposing total at $10.3 million.

**Candidate committees, through Oct 14 (PRE-GENERAL report, filed Oct 22):** Hines raised $4,159,692.85 and spent $3,152,065.09, with $1,007,627.76 on hand. Bouchard's authorized committees raised $2,884,259.39 and spent $1,310,789.75; his principal committee (Friends of Michael Bouchard Inc, C00925743) had $1,559,984.19 on hand. FEC shows one of his joint nominee funds filed a termination report on Oct 13; that is a different committee from his principal committee, which filed its pre-general report normally. Individual contributions to Hines were $3,380,348.82 and to Bouchard $1,841,619.43.

**The race.** Open seat: Rep. John James (R) is running for governor. Nominees are Christina Hines (D) and Mike Bouchard (R), plus Cubby Nkromo (Green), Mike Saliba (Libertarian) and Andrea Kirby (Working Class Party) on the Michigan Department of State's general-election listing (read Oct 28). No Kalshi contract for this district was found. No poll was found.

## Suggested hook and headlines
- "Outside groups have reported $10.1 million against Mike Bouchard. One committee is behind $7.2 million of it."
- "Michigan's open 10th District: two numbers for the same spending, and why they differ."
Dek idea: FEC's own roll-up shows $175,719 from HMP against Bouchard. The 24-hour notices show $7.2 million. The difference is a reporting calendar.

## Structure that fits (schema 03)
1. What is new: the reported totals and the magnitude against the candidates' own committees (state both and keep them separate; outside spending is not campaign money).
2. The filings: who reported, which form, support or oppose, notice versus periodic report, filed dates, the "estimate" label.
3. HMP in detail: the three buys, their dates and the two figures side by side.
4. The other large reporters on each side, grouped by committee type as FEC lists it.
5. What the filings do not establish: ads aired, effect, coordination, who funds each committee (not in this package).
6. Candidates' own committees and the open seat context. Table and flow graphic.

## TIP
Hines https://theissuesparty.org/candidates/H6MI10276 · Bouchard https://theissuesparty.org/candidates/H6MI10359 · Race https://theissuesparty.org/races/2026-H-MI-10 · LLF district page https://looklearnfind.com/elections/2026/michigan/house/10/. **No graded issues for either** (neither has served in Congress); not graded is not a score of zero. No grades are used.

## Unknowns and factual risks (write around them)
- **Alignment.** The FEC committee record carries no party or alignment for any of these committees. Do not call a committee Democratic-aligned or Republican-aligned. Say whom it supported or opposed, as the filing's support/oppose indicator records it.
- **What HMP and CLF are.** The FEC lists the committees as HMP and CLF; spell out a full name only if you can source it.
- **Estimates.** Notice descriptions say "ESTIMATE". Amounts can change on later reports. Say "reported" and "estimated by the filer", never "spent on airtime".
- **CLF.** The pull has no CLF row after September 30. We do not know whether CLF has not reported newer spending or whether none exists. Do not describe CLF's total as final.
- **Pull limits.** The pull is Schedule E rows for each candidate through the FEC API on Oct 28; one late row is dated Oct 29 (a $1,147.81 Women Vote notice disseminated Oct 24), which is inside the totals and too small to matter. Say "reported through October 24".
- **Do not add** the supporting and opposing totals across candidates as one pool of money: the same ad can be reported once against one candidate and not for the other, and the totals are not additive in that sense.
- **Earlier unattributed figure.** A July outside-spending figure seen in a search summary is not used here. Do not cite it.
- Why each committee spent is not established. No causal claims, no win probabilities, no endorsements.
