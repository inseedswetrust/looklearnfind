---
name: llf-delta-editorial
description: Draft an LLF Delta Report from same-contract market price history and independently sourced events. Use when asked to write or update a market-movement article. Never asserts causes.
---

# llf-delta-editorial

## Inputs
Two or more comparable observations of the SAME venue + contract + quote type (use `tools/elections/fetch_kalshi_history.py` for candlesticks, or the daily `markets.json`), with timestamps, bid/ask, volume, and contemporaneous events that have named sources and times.

## Steps
1. Build the timeline from recorded points only. Convert candle end times to Eastern days correctly (a daily candle ending 04:00 UTC is the previous Eastern day; see `tools/elections/fetch_kalshi_history.py`).
2. Place events on the same timeline with source and time. State what happened before, during and after the event window. Label unexplained moves "unexplained".
3. State the contract kind in the first paragraph (party-winner vs named-candidate) and what a price is not (not a vote share, not a forecast).
4. Keep polls and prices in separate panels.
5. Use data macros `[[v:name]]` for every number (see `elections.py`), so the build fails if data changes.
6. Hand to `llf-factcheck-finalize`. Do not publish.

## Reference
`content/learn/michigan-senate-delta-october-2026.html` is the worked example: the first draft's "fell after the debate" was wrong; most of the move came before it.

## Return BLOCKED when
the two observations are not the same contract and quote type, no sourced event times exist, or the only explanation available is a guess.
