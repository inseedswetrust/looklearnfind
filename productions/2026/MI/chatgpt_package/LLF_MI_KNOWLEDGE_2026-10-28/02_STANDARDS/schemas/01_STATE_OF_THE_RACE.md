# State of the Race

**Status:** NEW detailed schema drafted by ChatGPT on 2026-10-22 for Claude implementation review; NOT an existing schema authored or approved by Claude.

**Article:** State-level election hub + state video

## Required sections (in order)
1. At-a-glance counted races and candidates, only relevant contests; verification timestamp.
2. **Complete State Board**: governor, Senate, House district tiles; ALL verified qualifying candidates with neutral name and party display, consistent write-in treatment.
3. Governor field, Senate field, 28 district House field for Florida; consistent race rows.
4. **Six TIP issue rating module**: data availability, methodology, candidate grades where supported, no invented composite grade. Provide prominent video placement and contextual state article table.
5. Money and market snapshot: finance period, independent spending explicitly separate and current Kalshi quotes if available.
6. Newsworthy nuggets: 1–3 *current sourced* reporting findings; include news-source quality/date/evidence and official record check. At least one should appear in video with a clearly cited on-screen receipt.
7. 2–3 substantive race spotlights chosen based on documented developments and information value, with complete candidate comparison and explicit selection rationale.
8. Links to all race profiles, TIP candidates/issues and source ledger, updates/corrections.
9. **Video companion:** 90s, complete State Board at start and during walkthrough, ratings module in middle, sourced news nugget, evidence and CTA to TIP + LLF.

## Common contract — required for every article
- Article ID, type, primary state and race IDs, candidate IDs, headline, dek, author, reviewer, original publication time, verification time, next review time, article status.
- Reported fact must have an identifiable original URL/document locator, event date, retrieval time and claim-level source citation. Keep opinion, candidate allegation and inference labeled and attributed.
- Integrate actual TIP links and existing six issue definitions where relevant; render score, scale, method, source coverage and last updated; null ≠ zero. Never invent ratings.
- LLF footer: methods, full source ledger, updated timestamp, correction history, related stories and live TIP candidate/race links.
- Do not publish stale Kalshi prices as current; include exact contract, price side (yes/last/bid/ask), UTC quote timestamp, market-rule URL, liquidity where available. These are quotations, not definitive election probabilities.
- Financial reporting MUST separate direct campaign donations, campaign receipts, outside independent expenditures and ad-tracking totals. State date range, reporting source and any conflicting totals.
- Publishing output: LLF article MD/JSON, cited data packet, original image/chart assets, alt text, social teaser and approval checklist. Video is produced only for State of the Race in Florida pilot.
- Scope: only U.S. Senate, U.S. House and governor; exclude measures, Cabinet, legislative and judicial contests.

