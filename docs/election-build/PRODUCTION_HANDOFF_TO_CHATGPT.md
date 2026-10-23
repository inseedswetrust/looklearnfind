# Production handoff to ChatGPT

**State:** the Florida pages are built and staged, not deployed (see `IMPLEMENTATION_REPORT.md`). Everything below is specific and not asked twice.

## What exists now (use it, do not re-research it)
- Verified Florida packet in `data/elections/FL/`: official roster (10 governor tickets, 3 Senate, 83 House), district map for the 2026 plan, FEC candidate totals and deduplicated independent expenditures, Kalshi quotes (captured 2026-10-23 14:34 UTC), TIP links and Issue Grades, portraits with licenses.
- Michigan Senate: Kalshi candlesticks and FEC totals for the Delta Report.
- A fact ledger: `fact_check.csv`.

## Editorial work still needed (priority order)
1. **Governor money from filings.** The state's campaign finance database blocks automated access. Pull current totals for Donalds (campaign account, Friends of Byron Donalds) and Jolly (campaign account, Florida 2026) from the state system through a browser session, with report dates. Replace the Sept 11 press figures in the governor guide and feature.
2. **Original poll releases.** UNF's press release PDF (we have WLRN's report of it), and original releases for any other October governor or Senate polls you want cited. Required: field dates, sponsor, sample, method, MOE, wording.
3. **Kalshi market URLs.** Confirm the market page URLs (our script was rate-limited with HTTP 429) and, if you want, add the Michigan debate-day Kalshi volume context.
4. **Race articles for spotlights.** Objective rule used so far: the two House races with the most independent expenditures reported to the FEC (FL-25 and FL-14), plus the Senate race. Write or approve the spotlight rule, then draft race articles using the packet.
5. **Michigan Senate independent spending** (not tallied in the Delta Report).
6. **Challenger statements** for the six TIP issues (only incumbents have grades). Verbatim quotes with links; no grades created.

## Design and content questions (each needs one answer from the owner)
1. Open Graph cards: keep the site default image, or render data cards per page?
2. The live site still carries "Illustrative sample" stories while robots allows crawling. Keep as is, or hide samples before promoting election pages?
3. Candidates without a licensed portrait show a monogram. Ask campaigns for photos, or leave?

## Do not redo
Roster reconciliation, district geometry, FEC deduplication, Kalshi capture, TIP link checks, the three report drafts (final copy is in `content/learn/`).

## Known corrections to carry forward
The first drafts' ad-tracker figures, $146.2M and $21M totals, and the "after the debate" framing were removed or rewritten; see `FACT_CHECK_REPORT.md`.

## For TIP (not LLF)
Stale Florida race phase and empty governor roster in the TIP database; the TIP About page says five issues; two 404 candidate URLs; one name spelling. A reviewable SQL proposal is the next step you approved; nothing has been run.

## Next design work (after you review the skills proposal)
The six remaining article concepts (party dark horse, AIPAC dark horse, AIPAC candidates still running, plus the video board). The state video can use `candidates.json` and `districts.json` directly for the board.
