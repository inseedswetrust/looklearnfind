---
name: darkhorse-source-monitor
description: Run, check and troubleshoot the daily dark-horse monitor (Kalshi and Polymarket quotes, VoteHub race polls) for the verified watchlist. Use when asked to refresh daily data, check status or staleness, add or verify a contract mapping, or explain a coverage gap.
---

# darkhorse-source-monitor

## What it does
Collects dated, normalized snapshots for the watchlisted races and writes them under `data/elections/dark_horse/daily/<date>/`. It never invents a quote, a poll or a probability.

## Run
```
python3 tools/dark_horse/daily.py              # real run (America/New_York date folder)
python3 tools/dark_horse/daily.py --dry-run    # no network
python3 tools/dark_horse/coverage.py           # rebuild coverage_matrix.csv from the latest complete day
python3 tools/dark_horse/alert_if_stale.py     # exit 1 if any source is stale (> 48 h)
python3 -m unittest tests/test_dark_horse.py   # fixtures, no network
```

## Inputs
`data/elections/dark_horse/watchlist.csv` (28 rows; only `current_ballot_verified = yes` rows are monitored), `contract_map.json` (human-verified IDs only, keyed by TIP candidate ID).

## Outputs
`daily/<date>/markets.json|csv`, `polls.json`, `alerts.json` (same-venue, same-contract changes of 3 points or more; no causes), `manifest.json` (capture hashes), `captures/` (raw responses, git-ignored), plus `latest.json` (moves only for a complete day) and `status.json` (per-source freshness).

## Adding a contract mapping (the only way a venue gets queried)
1. Run `python3 tools/dark_horse/discover_contracts.py data/elections/dark_horse/watchlist_original.csv > contract_candidates.json` for proposals.
2. Read the contract's resolution rules. A contract that resolves on the party of the winner is `party_winner`; one that resolves on the named person is `candidate_individual`. Never record one as the other.
3. Add the entry to `contract_map.json` with `checked_by` and `checked_at`. Anything unclear stays unmapped (reported as `unavailable`).

## Stop and return BLOCKED when
the watchlist row has no verified ballot status; a contract's rules cannot be read; a provider returns 403 or repeated 429 (do not retry in a loop); any step would store a credential. Report the exact error.

## Never
average venues, average polls, compute win probabilities, rank candidates, or describe a price movement as caused by an event.

## Contract (v1.1.0)
**Owner** LLF production (Claude Code). **Type** skill driving scripts: `tools/dark_horse/daily.py` (collector), `lock_watchlist.py`, `coverage.py`, `alert_if_stale.py`, `schedule_e.py`, `contracts.py`, `fetch_udp_ie.py` (needs `FEC_API_KEY`).
**Input** `watchlist.csv` (lock_status verified|partial|unverified|background; contest_ids; nov3_general_status) and `contract_map.json`. **Output** `daily/<NY date>/` (immutable; a rerun becomes `revisions/rN/`), `latest.json` (moves forward only, only for a complete day), `status.json`, `coverage_matrix.csv`.
**Quote fields** `price_type` (last_trade), `bid`, `ask`, `observed_at_utc`, `quote_age_hours`, `stale_quote` (true, false or "unknown"). A 404 is `market_not_found`, not an outage; no price is ever invented.
**Fixtures** `tests/test_dark_horse.py` (9) and `tests/test_phase_a.py` (revision-safe pointer, idempotent rerun, stale quote, missing market, wrong-person Polymarket, Schedule E dedupe).
**Failure semantics** a provider error keeps the last complete day as latest and sets the source's `stale` flag after 48 hours; `alert_if_stale.py` exits 1.
## Changelog
1.1.0 (2026-10-23) revision folders, forward-only pointer, stale-quote flag, `market_not_found`, locked watchlist statuses and contest IDs, shared Schedule E dedupe. 1.0.0 (2026-10-23) first collector.
