# Existing Illinois coverage and duplication check (2026-10-28)

## LLF (looklearnfind.com)
| Check | Method | Result |
|---|---|---|
| Illinois landing | `curl` https://looklearnfind.com/elections/2026/illinois/ | HTTP 404 |
| Live sitemap | https://looklearnfind.com/sitemap.xml, filtered for `elections` and `learn` | Florida pages only; no Illinois URL |
| Repository content | grep for Illinois and IL-districts in `content/`, `data/`, `docs/` (excluding captures and release) | no articles or pages; Illinois appears only in the dark-horse files: `data/elections/dark_horse/watchlist.csv` (La Shawn Ford, Daniel Biss, Juliana Stratton, Delia Ramirez rows), `contract_map.json` (Kalshi tickers for IL-3, IL-7, IL-9 and Illinois Senate), `coverage_matrix.csv`, `tip_match.json`, and the dark-horse docs |
| Built `dist/` | `elections.py` builds Florida (and the Michigan report data) only | no Illinois route |
| Daily collector | watchlist covers four Illinois rows (IL-7 Ford, IL-9 Biss, Senate Stratton, IL-3 Ramirez) with Kalshi and poll checks | keeps running; no change |
**Conclusion:** nothing to duplicate or collide with on LLF.

## TIP (theissuesparty.org)
| Check | Result |
|---|---|
| Race pages | `2026-GOV-IL`, `2026-S-IL`, `2026-H-IL-01` to `17` all HTTP 200 (19 of 19) |
| Candidate pages | 43 of 54 November candidates have a live profile (HTTP 200); 11 have none |
| Editorial articles on TIP about Illinois | none found in the export or the repository search; TIP holds candidate and race records only |
| Overlap with what LLF would publish | none: TIP links are the destination of R1 and R2, not a duplicate |
| Data conditions that affect publishing | governor race has no entries; a corrupted name on the IL-04 entry; 5 "National source only" entries; 238 candidate rows versus 43 race entries (197 profiles are for people not on the November ballot, such as primary losers) |

## Watchlist leads reviewed (do not assume they are still newsworthy)
- **La Shawn Ford** (`partial`): the old lead said UDP supported his defeated rival (FEC $5.0M, confirmed: $4,968,500 de-duplicated, Feb 10 to Mar 10) and that retiring Rep. Danny Davis endorsed him, so he is not a dark horse versus the establishment. **Still newsworthy** because the outcome and the documented spending are now final; reframed as story 2 under the AIPAC/UDP franchise, not the establishment franchise.
- **Juliana Stratton** (`background`): "Pritzker and Duckworth endorsed the winner" is not a dark-horse criterion. **Superseded:** the stronger story is how the Senate primary was funded (story 1). The CNI article does not mention a Duckworth endorsement, so do not repeat that point.
- **Daniel Biss** (`background`): newsworthy again through the reported AIPAC-linked targeting; now proposal 5, not ready.
- **Delia Ramirez** (`background`, outcome unverified): renominated per Green Papers; no story found.
