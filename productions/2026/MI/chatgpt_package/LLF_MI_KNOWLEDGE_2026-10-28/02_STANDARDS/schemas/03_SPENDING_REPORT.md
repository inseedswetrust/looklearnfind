# Spending Report / Follow the Money

**Status:** NEW detailed schema drafted by ChatGPT on 2026-10-22 for Claude implementation review; NOT an existing schema authored or approved by Claude.

**Article:** FEC/state finance reported feature, no Florida video now

## Required sections (in order)
1. What new spend/finance datum makes this news; contextual baseline and magnitude.
2. Original FEC/state filing (filing ID, committee ID, filed date, spent/disbursed date), party direction and recipient, support versus oppose.
3. Dated comparison with past spending; group by actual entity and transaction type (never mix advertisement spend estimate with FEC disbursement).
4. Source-backed connections only; AIPAC PAC vs UDP IE vs documented affiliate vs ideologically aligned donor.
5. Creative/tactic of an ad or viral story if independently verified and relevant; attribute effects with care.
6. Candidate/campaign responses and what evidence cannot establish.
7. Comparative finance table, flow graphic, TIP links and sources.
Trigger: high verified amount, unusual financing relationship, substantial change or well-documented newsworthy tactic.

## Common contract — required for every article
- Article ID, type, primary state and race IDs, candidate IDs, headline, dek, author, reviewer, original publication time, verification time, next review time, article status.
- Reported fact must have an identifiable original URL/document locator, event date, retrieval time and claim-level source citation. Keep opinion, candidate allegation and inference labeled and attributed.
- Integrate actual TIP links and existing six issue definitions where relevant; render score, scale, method, source coverage and last updated; null ≠ zero. Never invent ratings.
- LLF footer: methods, full source ledger, updated timestamp, correction history, related stories and live TIP candidate/race links.
- Do not publish stale Kalshi prices as current; include exact contract, price side (yes/last/bid/ask), UTC quote timestamp, market-rule URL, liquidity where available. These are quotations, not definitive election probabilities.
- Financial reporting MUST separate direct campaign donations, campaign receipts, outside independent expenditures and ad-tracking totals. State date range, reporting source and any conflicting totals.
- Publishing output: LLF article MD/JSON, cited data packet, original image/chart assets, alt text, social teaser and approval checklist. Video is produced only for State of the Race in Florida pilot.
- Scope: only U.S. Senate, U.S. House and governor; exclude measures, Cabinet, legislative and judicial contests.

