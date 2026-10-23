# Fact-Check Report

**Date:** 2026-10-23 | **Machine-readable ledger:** `fact_check.csv` (51 rows) | **Raw captures:** `data/elections/*/captures/`

## Result

| Page | Verified | Attributed | Unverified or removed |
|---|---|---|---|
| State hub, House atlas, district pages | roster, district map, FEC totals, outside spending, Kalshi quotes, TIP grades | | none shown |
| Governor guide + feature | roster, matching funds (official), Kalshi, TIP grades | committee and campaign money (Sept 11 press), UNF poll (via WLRN), campaign-page proposals, Jolly biography | $146.2M and $21M totals; ActiVote, Change Research and St. Pete Polls; Oct 16 matching-fund figures (stale) |
| Senate guide | roster, FEC, outside spending, Kalshi | UNF poll (via WLRN) | none |
| Delta Report | candlesticks, debate date and time, Marist poll, FEC | Kalshi News' description, Al Jazeera's account of the debate | cause of the Oct 9 move (labeled unexplained); "73 to 67 after the debate" rewritten |
| Spending Report | all FEC-based figures | | Washington Post/AdImpact figures removed (page returned 403, no corroboration) |

Nothing marked UNVERIFIED, CONTRADICTED or STALE appears on a published page except where the page says so explicitly.

## Most important corrections made to the first drafts

1. **Delta Report:** the draft (from Kalshi's text) said the market fell from 73 to 67 after the debate. Kalshi's own price history shows four to five cents of the fall had already happened by 7 p.m. on debate day, the debate hour closed at 69¢, and the lowest hourly close came about 17 hours later. A date-mapping bug was also caught during the build: daily candles end at 04:00 UTC and cover the previous Eastern-time day, so every label was one day off until corrected.
2. **Spending Report:** rebuilt from FEC Schedule E. The original relied on a paywalled ad-tracker article. FEC data also needed deduplication: the same transaction appears on both a 24/48-hour notice and a later periodic report, and memo entries repeat other lines. Without that, totals would be overstated.
3. **Governor feature:** the draft's $146.2M and $21M totals and the October 16 matching funds were replaced by the official October 23 table and dated press figures. The governor guide shows what is official and what is attributed side by side.
4. **Scope and mockups:** every candidate name, portrait, amount, market price and district description in the mockups was discarded.
5. **House map:** Florida enacted a new congressional map in May 2026. District descriptions use the official file, not the older map.

## Method notes

- **Roster:** state candidate list pages fetched 2026-10-23, SHA-256 recorded in `data/elections/FL/roster.json`. The state's "Qualified" filter omits unopposed candidates (Frost, FL-10), so all statuses were pulled and filtered to Qualified or Unopposed. House count of 83 matches TIP's own entries; the only discrepancy with TIP's roster is the Senate independent's spelling.
- **Finance definitions:** candidate committee receipts (FEC period shown) are never added to independent expenditures; public matching funds are shown as a separate state payment. Governor candidates file with the state.
- **Independent expenditures:** `most_recent=true` rows; one row per (committee, transaction, amount, date), preferring the 24/48-hour notice; `memo_code=X` excluded. By-candidate FEC totals cover periodic filings only and were not used for charts.
- **Markets:** Kalshi public API; quotes labeled with capture time; candlestick `end_period_ts` mapped to Eastern time (EDT, UTC-4, valid before Nov 1). Charts plot captured points only.
- **Polling:** UNF figures come from WLRN's report of the UNF release (the UNF PDF itself was not retrieved). Marist numbers come from the Marist page.
- **TIP grades:** read from `candidate_issue_grades` (computed 2026-10-21), displayed with the published formula; not recalculated.

## Open items for the next pass

- Re-pull Kalshi quotes and FEC 24/48-hour reports on the day of any update, and again before Nov 3.
- Pull the governor committee totals from the state database through a browser session or an official export.
- Retrieve the UNF PDF and any other October gubernatorial polls' original releases.
- Verify the Kalshi market page URLs in a browser (the script was rate-limited).
- Replace Wikipedia-sourced biography checks with primary sources where possible (Jolly's party history).
