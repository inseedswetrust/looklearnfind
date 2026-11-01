# Fact-check report: Pennsylvania governor poll/market and PA-01 CLF spending articles

Reviewer: independent fact-check subagent. Date: 2026-11-01. No article was edited.

- Governor article (pennsylvania-governor-poll-party-market-2026.html): CLEARS_WITH_FIXES
- PA-01 article (pennsylvania-first-district-clf-spending-2026.html): CLEARS_WITH_FIXES

Sources opened: Quinnipiac release 3970 (fetched; summary), Quinnipiac PDF (fetched but the tool could not decode the binary, so nothing was verified from the PDF itself), City & State PA (fetched), Philadelphia Inquirer (fetched), Jewish Insider (fetched). A web search surfaced Quinnipiac's July 15 release (releaseid=3962; title only, body not opened) and a Central Bucks News headline "Shapiro leads Garrity, 53-40%". Local: markets.json (capture 2026-11-01T15:35:47Z), candidates.json, roster.json, checked with separately written code. WebFetch returns summaries; quotes are as returned.

## Required fixes

### Governor article
1. ATTRIBUTION_FIX (July paragraph; sources; openfile `checked`): the July figures 53/40 are NOT on Quinnipiac release 3970. The fetch said: "The page does not mention July or any July figures." The October release says only that results "cannot be compared to results of earlier surveys of registered voters." The 53/40 comes from Quinnipiac's July 15 release (https://poll.qu.edu/poll-release?releaseid=3962, not opened by me) and a Central Bucks News headline. Fix: open release 3962, confirm 53/40, registered voters and field dates (search summary says July 9-13), add it as source 6, and write: "Quinnipiac's July survey of registered voters, a separate release, had Shapiro at 53 percent and Garrity at 40 percent. In its October release the pollster says the results cannot be compared with earlier surveys of registered voters." Cite [[s:6]] for the July figures and [[s:1]] for the caveat. If 3962 cannot be confirmed, drop the 53/40 figures (mark UNVERIFIED).
2. ATTRIBUTION_FIX ("The larger-looking October difference"): the page never states July's 13-point difference, so "larger-looking" has no support in the text. Fix: "Calling the lead a widening gap would add a trend claim that Quinnipiac's own caution does not support. October shows a 25-point difference and July a 13-point difference, but the pollster says the surveys cannot be compared."
3. Minor: sources line 1 and openfile say "read as a summary"; reader-facing sources line should read "Poll results, field dates and the comparison caveat." The 4% undecided / 1% refused split comes from the release crosstab as summarized (text says "5 percent did not choose a candidate"); the PDF could not be read. Acceptable.

### PA-01 article
1. ATTRIBUTION_FIX (campaigns paragraph 1): "Citing disclosures, the Inquirer reported..." The fetch of the Inquirer did not say the figures cite disclosures. Fix: "The Inquirer reported that Harvie raised about $888,000 and spent $962,000 from July 1 through September 30, 2026, with $721,000 on hand on October 1." Keep the sentence that these are the outlet's reported figures and not a new review of the filings.
2. UNVERIFIED ("Neither outlet explains the difference"): confirmed only from summaries. Fix: "Neither report, as read, explains the difference."
3. Optional: the verbs differ (Inquirer "redirected $3.6 million to give Fitzpatrick a boost"; Jewish Insider "put $4.5 million into the race this week"). Quote or paraphrase both verbs; the "not reconciled" framing is correct.
4. Optional precision: Jewish Insider says the RJC Victory Fund "is launching" its $400,000 campaign "on Sunday" (October 18). Add "set to launch October 18".

## Article 1: Governor

| Claim | Where | Source checked | Verdict | Exact fix |
|---|---|---|---|---|
| Quinnipiac Oct 7, 2026 release | para 1, sources | Quinnipiac 3970; City & State | VERIFIED | none |
| Shapiro 59, Garrity 34, Krawchuk 2 | para 1, poll | Quinnipiac page | VERIFIED | none |
| 4% undecided, 1% refused | poll | Quinnipiac crosstab (summary) | VERIFIED (summary; PDF unreadable) | none |
| 1,159 likely voters, Oct 1-5 | poll | Quinnipiac; City & State | VERIFIED | none |
| MOE 3.9 incl. design effect | poll | Quinnipiac page | VERIFIED | none |
| Shapiro approval 63 / 30 | poll | Quinnipiac page (7% no opinion) | VERIFIED | none |
| First likely-voter survey of the cycle | July section | Quinnipiac wording | VERIFIED | none |
| Cannot be compared with earlier registered-voter surveys | para 1, July | Quinnipiac wording | VERIFIED | none |
| July RV poll Shapiro 53, Garrity 40 | July section | not on release 3970; release 3962 per search | ATTRIBUTION_FIX | Gov fix 1 |
| "Larger-looking October difference" | July section | 13-point July gap not stated on page | ATTRIBUTION_FIX | Gov fix 2 |
| 25-point difference (59 minus 34) | poll | arithmetic | VERIFIED | none |
| Election November 3, 2026 | field | Nov 3, 2026 is a Tuesday; Nov 1 is a Sunday | VERIFIED | none |
| Kalshi capture 2026-11-01T15:35:47Z, GOVPARTYPA-26 | market | markets.json | VERIFIED | none |
| -D last 0.984, bid 0.981, ask 0.984 | market | markets.json | VERIFIED | none |
| -R last 0.022, bid 0.018, ask 0.021 | market | markets.json | VERIFIED | none |
| Rules wording (representative of the party inaugurated as governor pursuant to 2026 election) | market | markets.json | VERIFIED | none |
| Party contracts with candidate labels | market | markets.json yes_label | VERIFIED | none |
| Shapiro, Garrity: no congressional record, all six Not graded | TIP | candidates.json (also Krawchuk all not_graded) | VERIFIED | none |
| Six issue names | TIP | candidates.json issues | VERIFIED | none |
| Roster Shapiro (D, incumbent), Garrity (R), Krawchuk (Libertarian); Green Papers; state list not read | field | roster.json (official_checked null) | VERIFIED | none |
| Headline and dek match evidence | title, dek | "comparison warning" supported by Quinnipiac caveat | VERIFIED | none |
| Kalshi described as party contracts; no causal claims | whole | read | VERIFIED | none |
| Oxford comma | whole file | read in full | VERIFIED (none found) | none |
| Process language in reader-facing text | whole | scan | VERIFIED in body ("read as a summary" in sources line: Gov fix 3) | Gov fix 3 |

## Article 2: PA-01

| Claim | Where | Source checked | Verdict | Exact fix |
|---|---|---|---|---|
| Inquirer Oct 16, 2026 (Sam Janesch) | para 1, sources | Inquirer | VERIFIED | none |
| CLF "redirected $3.6 million" for Fitzpatrick | para 1 | Inquirer | VERIFIED | none |
| Jewish Insider Oct 17: CLF $4.5M that week, first since 2020 | para 2 | Jewish Insider | VERIFIED | none |
| Neither outlet explains the difference | para 2 | summaries only | UNVERIFIED | PA-01 fix 2 |
| DCCC nearly $1M campaign for Harvie that week | outside | Inquirer | VERIFIED | none |
| RJC Victory Fund $400,000 digital and streaming, backs Fitzpatrick, attacks Harvie | outside | Jewish Insider | VERIFIED | PA-01 fix 4 optional |
| Harvie raised ~$888,000, spent $962,000, July 1-Sept 30 | campaigns | Inquirer | VERIFIED | none |
| Harvie $721,000 on hand Oct 1 | campaigns | Inquirer | VERIFIED | none |
| "Citing disclosures" | campaigns | not in fetch result | ATTRIBUTION_FIX | PA-01 fix 1 |
| Fitzpatrick spent $5M over the summer, mostly advertising | campaigns | Inquirer | VERIFIED | none |
| Fitzpatrick $2.4M on hand | campaigns | Inquirer ("heading into October") | VERIFIED | none |
| Summer is not assumed to equal July-Sept | campaigns | Inquirer wording | VERIFIED | none |
| "As of November 1, 2026, the election is two days away" | para 3 | Nov 3 is two days after Nov 1 | VERIFIED | none |
| Kalshi capture 15:35:47 UTC, HOUSEPA1-26 | market | markets.json | VERIFIED | none |
| -D last 0.53, bid 0.52, ask 0.53 | market | markets.json | VERIFIED | none |
| -R last 0.47, bid 0.46, ask 0.47 | market | markets.json | VERIFIED | none |
| Rules: party of House member sworn in for term beginning 2027 | market | markets.json | VERIFIED | none |
| Labels show candidate names | market | markets.json yes_label (Bob Harvie, Brian Fitzpatrick) | VERIFIED | none |
| Fitzpatrick A+ Stock Trading Ban and Universal Healthcare | TIP | candidates.json H6PA08277 | VERIFIED | none |
| Fitzpatrick F- Data Bill of Rights, War-Crime Accountability, US-Israel Military Merger | TIP | candidates.json | VERIFIED | none |
| Citizens United Reform Not graded | TIP | candidates.json | VERIFIED | none |
| Harvie: no congressional record, all six Not graded | TIP | candidates.json H6PA01181 | VERIFIED | none |
| Roster Fitzpatrick (R incumbent), Harvie (D); Green Papers; state list not read | lede | roster.json | VERIFIED | none |
| Headline and dek ("different figures", "not reconciled") | title, dek | $3.6M vs $4.5M | VERIFIED | none |
| Party contracts; no causal claims | whole | read | VERIFIED | none |
| Oxford comma | whole file | read in full | VERIFIED (none found) | none |
| Process language in reader-facing text | whole | scan | VERIFIED (none) | none |

## Other notes
- PA-GOV-A CLAIMS.csv row 3 cites the July 53/40 to release 3970, which does not carry it; that is the root of Gov fix 1.
- CLAIMS rows on the 54/39 House question, "looks like a rout" and the Cook rating are not used in either article.
- Neither article states win probabilities or endorsements. Keep that.
- Kalshi quotes are dated 2026-11-01T15:35:47Z; refresh before any republish.
- Hero alt text not reviewed.

## Resolution (Claude Code, 2026-11-01)
Governor: Quinnipiac's July 15 release (releaseid 3962) was opened and confirms Shapiro 53%, Garrity 40%, registered voters, July 9 to 13; added as source 6, the July field dates stated and the 25-point and 13-point differences given with the pollster's warning. The sources line no longer says "read as a summary". PA-01: "Citing disclosures" removed; "Neither report, as read, explains the difference" now used. Not done: the optional note that the RJC campaign was set to launch Sunday October 18. The Quinnipiac PDF could not be decoded, so the 4% undecided and 1% refused split rests on the release page. The owner signs off the fact-check.
