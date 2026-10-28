# Dark Horse — AIPAC-supported Opponent Defeated

**Status:** NEW detailed schema drafted by ChatGPT on 2026-10-22 for Claude implementation review; NOT an existing schema authored or approved by Claude.

**Article:** Evidence-classified primary retrospective, no Florida video now

## Required sections (in order)
1. Exactly which candidate won which completed election; type and official result.
2. AIPAC involvement classifications **separately:** PAC endorsement; AIPAC PAC contribution; UDP reported supporting opponent; UDP opposing winner; verified affiliated committee; individual donations; speculative alignment.
3. FEC evidence per claim (source committee, transaction, dates, support/oppose direction, exact value).
4. Who was supported/opposed — in particular do not mislabel spending *against* one defeated rival as support for that rival.
5. Report spending vs results in compatible periods, historical/other campaign spending, documented campaign responses.
6. Clear exceptions and disputed affiliations.
7. TIP candidate links, six issues with no inferred alignment and source list.
Trigger: verified primary/general result contradicting a documented expenditure/endorsement objective.

## Common contract — required for every article
- Article ID, type, primary state and race IDs, candidate IDs, headline, dek, author, reviewer, original publication time, verification time, next review time, article status.
- Reported fact must have an identifiable original URL/document locator, event date, retrieval time and claim-level source citation. Keep opinion, candidate allegation and inference labeled and attributed.
- Integrate actual TIP links and existing six issue definitions where relevant; render score, scale, method, source coverage and last updated; null ≠ zero. Never invent ratings.
- LLF footer: methods, full source ledger, updated timestamp, correction history, related stories and live TIP candidate/race links.
- Do not publish stale Kalshi prices as current; include exact contract, price side (yes/last/bid/ask), UTC quote timestamp, market-rule URL, liquidity where available. These are quotations, not definitive election probabilities.
- Financial reporting MUST separate direct campaign donations, campaign receipts, outside independent expenditures and ad-tracking totals. State date range, reporting source and any conflicting totals.
- Publishing output: LLF article MD/JSON, cited data packet, original image/chart assets, alt text, social teaser and approval checklist. Video is produced only for State of the Race in Florida pilot.
- Scope: only U.S. Senate, U.S. House and governor; exclude measures, Cabinet, legislative and judicial contests.

