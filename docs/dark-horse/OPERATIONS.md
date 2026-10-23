# Dark-horse monitor: operations

## Flow
`daily collector (cron, 08:00 America/New_York) -> validated daily data -> same-contract deltas -> research commission -> editorial agent -> independent fact-check agent -> build-time rules R1/R2 (--strict) -> site QA -> owner publishing approval`

Nothing in this flow publishes political analysis on its own. Collected fields (quotes, polls, freshness) update automatically with their source and timestamp. Prose that explains a price movement or makes a campaign claim is written by the editorial agent from verified research, checked by a separate standards pass, and approved by the owner.

## Agent roles and permission boundaries
| Role | Does | May write | Must not |
|---|---|---|---|
| Research (skill `darkhorse-source-monitor`) | runs the collector, adds mappings after reading contract rules, logs coverage gaps | `data/elections/dark_horse/*` | publish, change a skill, store credentials |
| Editorial (skill `llf-delta-editorial`) | drafts a Delta Report from same-contract history and sourced events | `content/learn/*.html` drafts with `[[v:]]` data macros | assert a cause, rank candidates, call a price a forecast |
| Standards (skill `llf-factcheck-finalize`) | independent claim ledger, R1/R2, QA evidence, READY or BLOCKED | `docs/*/fact_check.csv`, reports | edit the story it is checking |
| Retrospective (skill `workflow-retrospective`) | records lessons and proposes fixtures and changes | log entries, proposals | change a skill or threshold without owner approval |
| Orchestrator (a person or a Claude Code session) | runs stages in order | scripts, builds | skip a gate; publish without approval |
Creative agents (storyboards, assets) are separate and not needed by the daily collector.

## Schedule
- Server: `~/llf-data/dark_horse` on the LLF hosting account. Cron fires `tools/dark_horse/cron_run.sh` at 12:00 and 13:00 UTC; the script proceeds only when the New York hour is 08 (storage in UTC, folders named by New York date). This is correct on both sides of the 2026-11-01 daylight-saving change and does not rely on `CRON_TZ`.
- A finished day folder is immutable: a manual rerun becomes `daily/<date>/revisions/rN/` and `latest.json` moves to it (never backward). `--dry-run` writes only under `dry_runs/`.
- More frequent collection only with owner approval. No retry loop on HTTP 429.
- Verify any folder: `python3 tools/dark_horse/verify_day.py [folder]` (capture hashes, leftover temp files, secrets).

## Backup and recovery
- Daily folders are append-only. `tools/dark_horse/pull_from_server.sh` copies them into `data/elections/dark_horse/server_pull/` (raw captures git-ignored; manifests and normalized data commit-able).
- Code and mapping changes go to the server with `tools/dark_horse/sync_to_server.sh`. The prior crontab (empty) is saved as `crontab.backup-20261023`. To stop the job: `crontab -l | grep -v dark_horse | crontab -`.
- Do not commit raw archives; commit manifests and normalized outputs.

## Contract mapping rule
A venue is queried only for IDs in `contract_map.json`, entered after reading the resolution rules. Party-winner contracts are labeled `party_winner` and are not reported as named-candidate contracts. Deltas compare the same venue, contract and quote type only.

## Acceptance tests (installation) and where each is covered
| Requirement | Evidence |
|---|---|
| Verified Kalshi ticker gives a real dated row | live run: 21 rows, `daily/2026-10-23/markets.json` |
| Verified Polymarket token gives a real, separately stored row with quote type | live run: Wiener CA-11, `price_type = last_trade` |
| Unsupported race is `unavailable` | `test_party_contract_is_labeled_and_unmapped_is_unavailable` |
| Missing poll is `no_poll_found` with the source checked | `test_missing_poll_is_no_poll_found_not_zero`; live: 17 races |
| Party contracts labeled, not presented as candidate contracts | same test; `contract_kind = party_winner` on every Kalshi row |
| Empty data never overwrites `latest.json` | `test_empty_data_does_not_overwrite_latest` |
| Two runs make two folders; deltas same-contract only | `test_two_runs_make_two_folders_and_same_contract_deltas` |
| A 429 keeps prior data and shows the error | `test_rate_limit_keeps_previous_data_and_records_error` (stale flag after 48 h is time-based and not simulated) |
| No TIP ID guessed from a name | `test_no_tip_id_is_guessed_from_name`; unmatched rows get `no_tip:` keys |
| Partisan sponsor stays visible | `test_partisan_sponsor_stays_visible` |
| No credentials in logs or repo | none are used; FEC key is read from the environment only in the FEC pull |
| Website shows only verified candidates with timestamps | status page reads `coverage_matrix.csv` (monitored rows only get quotes) |
