# Politics 2.0 install report (local, 2026-11-05)

Authorization: owner reply "Approve, build local". **Nothing committed, pushed, deployed, no results field changed, no TIP campaign created.**

## Installed
- Policy `docs/politics/` v0.1.0, STATUS=LOCKED (approved 2026-11-05), CHANGELOG, SHA256SUMS.txt, URL_BASELINE.txt (232 live sitemap URLs).
- `politics.py`, `data/politics_home.json`, `data/politics_daily/` (empty: no Daily Signal is approved), `static/css/politics.css`; `/politics/` rebuilt (status statement, Daily Signal empty state, Follow the story with earlier reporting labeled, Explore a state, The Record, threads and topics kept, On our radar empty state, verify links, labeled external TIP link) and new `/politics/daily/` index. Per-record pages render once an approved record exists.
- Search index now includes `/politics/`, `/politics/daily/` and the state hub, governor, Senate and House index pages (27 entries).
- `tools/qa/politics_contract_check.py`, `tools/qa/politics_visual_check.py`, `tests/test_politics.py` (15 tests), fixtures in `tests/fixtures/politics/`.
- Pointers added to `CLAUDE.md` and `docs/election-build/INDEX.md`. `DISCOVERY_DIFF.md` and `ASSET_REUSE.csv` in `docs/politics-2-0/`.

## Results
Strict build 251 pages, 0 publishing and 0 shell violations; full unit suite 191 OK (1 skipped Playwright); `shell_check --quick` 0 failures; contract check 0 problems; `politics_visual_check` 8 page checks at 1440, 1024, 390 and 320, 0 failures (one h1, heading order, landmarks, names, alt text, no overflow, 44px targets, visible focus, no failed requests). Screenshots: `screenshots/`. URL preservation: all 232 baseline URLs still built.

## Not done or not verified
- `drawer_check` rerun (606 assertions, 0 failures); full-width `shell_check` not rerun (quick run passed); screen readers and real devices untested.
- The Daily Signal, Accountability Desk, `/elections/2026/` national hub and `/politics/money/` are not built. No official results source is validated, so no result cards exist.
- Live `/politics/` still shows the old layout until you authorize a deploy.
- Pre-election articles keep their original dates; the "earlier reporting" label is on the landing only, not on the articles themselves.
