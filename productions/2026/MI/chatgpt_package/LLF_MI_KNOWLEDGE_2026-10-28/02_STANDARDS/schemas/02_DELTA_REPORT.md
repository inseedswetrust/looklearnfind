# Delta Report

**Status:** NEW detailed schema drafted by ChatGPT on 2026-10-22 for Claude implementation review; NOT an existing schema authored or approved by Claude.

**Article:** Market movement feature, no Florida video now

## Required sections (in order)
1. Market question and exact candidate/party contract definition.
2. Baseline quote T0, latest T1, difference in *percentage points* and in cents, with timezone and available liquidity/volume.
3. Deterministic time-series graphic and whether contracts remain comparable.
4. Dated timeline of events *around* the movement (fundraising, news, polling, FEC, candidate statements).
5. Verified context; do not state the events caused the market move absent direct evidence.
6. Explanations of thin liquidity, spread, market construction and resolution risk.
7. Attributed expert/participant interpretation if available; unanswered questions; TIP/LLF related links.
Trigger: measurable move crossing documented editorial threshold AND minimum data-quality checks.

## Common contract — required for every article
- Article ID, type, primary state and race IDs, candidate IDs, headline, dek, author, reviewer, original publication time, verification time, next review time, article status.
- Reported fact must have an identifiable original URL/document locator, event date, retrieval time and claim-level source citation. Keep opinion, candidate allegation and inference labeled and attributed.
- Integrate actual TIP links and existing six issue definitions where relevant; render score, scale, method, source coverage and last updated; null ≠ zero. Never invent ratings.
- LLF footer: methods, full source ledger, updated timestamp, correction history, related stories and live TIP candidate/race links.
- Do not publish stale Kalshi prices as current; include exact contract, price side (yes/last/bid/ask), UTC quote timestamp, market-rule URL, liquidity where available. These are quotations, not definitive election probabilities.
- Financial reporting MUST separate direct campaign donations, campaign receipts, outside independent expenditures and ad-tracking totals. State date range, reporting source and any conflicting totals.
- Publishing output: LLF article MD/JSON, cited data packet, original image/chart assets, alt text, social teaser and approval checklist. Video is produced only for State of the Race in Florida pilot.
- Scope: only U.S. Senate, U.S. House and governor; exclude measures, Cabinet, legislative and judicial contests.

