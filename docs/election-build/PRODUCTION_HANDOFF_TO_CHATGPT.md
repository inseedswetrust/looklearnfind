> **SUPERSEDED 2026-10-24** by the lean editorial reset: the only required exchange is STORY_BRIEF.md and CLAIMS.csv (see docs/election-build/INDEX.md and docs/story-briefs/). The 14-file packet is optional reference. Kept for history.

# Production handoff to ChatGPT

**Updated:** 2026-10-23 (after deploy). The Florida pages are **live** at https://looklearnfind.com/elections/2026/florida/ and the TIP changes are live at https://theissuesparty.org. Everything below is specific and not asked twice. Read `IMPLEMENTATION_REPORT.md` first, then `PUBLISHING_RULES.md`.

## What exists now (use it, do not re-research it)
- **Pages (36):** state hub with the State Board, governor guide, Senate guide, House atlas (cards and directory), 28 district pages, methods page, and three reports: Michigan Senate Delta Report, Florida House Spending Report (rebuilt from FEC filings) and the Florida governor feature.
- **Verified Florida packet** in the LLF repo `data/elections/FL/`: official roster (10 governor tickets, 3 Senate, 83 House), 2026 district map, FEC totals and deduplicated independent expenditures, Kalshi quotes (captured 2026-10-23 14:34 UTC), TIP links and Issue Grades, portraits with licenses. Michigan: Kalshi candlesticks and FEC totals in `data/elections/MI/`.
- **Fact ledger:** `fact_check.csv` (51 rows; every claim with source, as-of and verdict). **Asset manifest:** `ASSET_MANIFEST.csv`.
- **Publishing rules (owner, 2026-10-23):** R1 every featured candidate links to their TIP profile; R2 every mentioned race links to that race. Enforced by the build.
- **TIP data fixes applied 2026-10-23:** one profile per person (alias redirects), Florida governor roster, eight missing Florida profiles, 18 duplicate people merged, 17 biographies written from sources. Details in `ONE-PROFILE-PER-CANDIDATE.md` and `CANDIDATE-BIOS-DRAFT-2026-10-23.md`.

## Editorial work still needed (priority order)
1. **Governor rosters for the other 35 states.** TIP's governor rosters are a spring Wikidata snapshot: 0 of 36 races have a roster, 9 lack a whole major party, and several listed people are no longer candidates (Barnes withdrew; Johnson, Bennet and Schweikert lost primaries; Cameron lost a Senate primary). Build each state's list from the state election authority the way Florida's was.
2. **Owner confirmations to resolve with official sources:** Barnes (Wisconsin withdrawal sequence), Lopez (Colorado ballot status as an independent), Bailey (running mate Aaron Del Mar), and the Tennessee, Alabama and Arizona primary dates.
3. **Governor money from filings.** The state campaign finance database blocks automated access. Pull current totals for Donalds (campaign account, Friends of Byron Donalds) and Jolly (campaign account, Florida 2026) in a browser session, with report dates, to replace the Sept 11 press figures.
4. **Original poll releases.** UNF press release PDF (we have WLRN's report of it) and any other October governor or Senate polls you want cited: field dates, sponsor, sample, method, margin of error, question wording.
5. **Kalshi market URLs.** Confirm the market page URLs in a browser (our script was rate-limited); then decide whether to add Michigan debate-day volume context.
6. **Spotlight race articles.** Current objective rule: the two House races with the most independent expenditures reported to the FEC (FL-25, FL-14) plus the Senate race. Approve or revise the rule, then draft race articles from the packet.
7. **Michigan Senate independent spending** (not tallied in the Delta Report).
8. **Challenger statements** on the six TIP issues (only members of Congress have grades). Verbatim quotes with links; no grades created.

## Owner decisions that block or shape work
1. Open Graph cards: keep the site default image, or render data cards per page?
2. The live LLF site still carries "Illustrative sample" stories while its `robots.txt` allows crawling. Keep, or hide samples before promoting election pages?
3. Candidates without a licensed portrait show a monogram. Ask campaigns for photos, or leave?
4. 26 House entries on TIP still read "National source only" although the state list confirms them as qualified. Approve a labeling update?
5. Skills proposal (`SKILLS_PROPOSAL.md`): review before any remaining concept designs are built.

## Do not redo
Roster reconciliation, district geometry, FEC deduplication, Kalshi capture, TIP link checks, the three report drafts (final copy is in `content/learn/`), the 17 biographies, the Florida TIP profile work.

## Corrections to carry forward
The first drafts' ad-tracker figures, the $146.2M and $21M governor totals and the "after the debate" framing were removed or rewritten (see `FACT_CHECK_REPORT.md`). My earlier statement that Florida race "phase" data was stale was wrong as a user-visible issue: no TIP page reads that field.

## Next design work
The six remaining article concepts (party dark horse, AIPAC dark horse, AIPAC candidates still running, and the others) and the state video board, which can use `candidates.json` and `districts.json` directly.
