# Story assignments for ChatGPT (Phase B)

These are news questions and a paragraph-level spine for each article, not finished copy. Use only facts in the packet; every figure must be traceable to a file and row. Keep the neutral voice, no probabilities, no causal claims about spending or prices. R1: link a candidate on first mention to their TIP profile (`tip_candidate_url` in `fl_candidate_roster.csv`). R2: link every race mentioned (`tip_race_url` in `fl_races.json`). Show TIP's six issue grades only where the profile page displays them (`profile_holding_grade` in `tip_grades.csv`); "not graded" is never zero.

## Article 1: Florida U.S. Senate (Class III special election, Nov 3)

**News questions**
1. Where does the race stand on the newest independent evidence, and how do the polls differ by pollster and sponsor? (S1, S3; `fl_polls.csv`)
2. Who is spending outside the campaigns, for and against whom? (S4; `fl_outside_spending.csv`, rows with `race_id = senate`)
3. What have the candidates said and done on the six TIP issues, and where are there no recorded actions? (`tip_grades.csv`; Moody has two graded issues (war-crime accountability and universal healthcare); Nixon and Gillespie have none graded, which is not a zero)
4. What do prediction markets show, and what do they not show? (`fl_markets.json`: one party contract set, last captured 2026-10-23)

**Paragraph spine**
1. Lead: the special election is for the remainder of the term; three candidates are on the ballot (Moody R, Nixon D, Gillespie NPA). Link each on first mention.
2. The newest poll and how it compares with July and with the September polls (S1, S3). Report ranges with sponsors; no average.
3. The debate decision and the Hope Florida record, with attributions on both sides (S2). Verify the grand jury date first.
4. Money: FEC candidate receipts and cash on hand (`fl_candidate_finance.csv`), then outside spending as filed (S4), with the dedupe note.
5. The six issues: a compact grade table using only profile-visible grades; state which issues have no graded record.
6. Markets: one paragraph on the party-winner contract, bid, ask, last and capture time. Explain it is a party contract.
7. What to watch: early voting (Oct 24 to 31 per search summary; verify with the Division of Elections), and the date of the next FEC report.

**ChatGPT should verify independently:** the UNF original release; the Hope Florida grand jury date and wording; the funders and stated purposes of STRONGER SAFER NATION and NEW DEAL FOR ALL, INC.; the early-voting dates; the sponsor of each September poll.

## Article 2: Florida U.S. House (28 districts)

**News questions**
1. What did the new map change, and which incumbents moved? (H1; `fl_races.json` district vintage and county shares)
2. Which races have the most outside money and what does the FEC record show? (H3, H4; `fl_outside_spending.csv`, FL-25 about $24.9M, FL-14 about $18.6M, FL-6 about $7.3M, FL-13 about $7.0M, FL-22 about $6.3M, de-duplicated)
3. Which districts have a public poll and which have none? (`fl_polls.csv`; 21 races with `no_poll_found`)
4. Where do the nominees stand on the six TIP issues, and how many House nominees have no graded issue? (`tip_grades.csv`)

**Paragraph spine**
1. Lead: 28 districts, 83 candidates on the ballot, one unopposed; the map in force is EOGPCRP2026.
2. The map story (H1): 21 districts reworked, 1 to 7 unchanged. Cite official boundaries and population; mark Trump-margin numbers as reporters' estimates.
3. FL-20 and FL-25 (H2, H3): moved incumbents and the primary results from the official roster; verify the vote counts.
4. Outside money by race (table): support and oppose shown separately, top committees, with the notice-versus-periodic dedupe explained once.
5. Polls and markets: which districts have either; the 21 districts with no poll and the 2 with no Kalshi contract (FL-13 and FL-23), stated plainly.
6. The district atlas: link to each district page; use the existing atlas rather than a new map.
7. The six issues across the delegation: summary counts of graded issues per party, and the candidates with all six graded.

**ChatGPT should verify independently:** each House vote count from the Division of Elections; the funders of NO GOING BACK PAC INC., CONSERVATIVE FIGHTER PAC and DEFEND AMERICAN JOBS; the FL-20 indictment status from a court record; the litigation status of the map.

## Rules that still hold
Scope is Governor, U.S. Senate and U.S. House only. No ballot measures, Cabinet or legislature. Governor rows in the roster are for links only. Do not start the State of the Race video; that follows the live pages. Publication paths are in `fl_existing_pages.json`: new long-form articles are `content/learn/*.html` with `layout: report` and the existing `[[v:]]`, `[[s:]]` and `[[el:]]` macros.
