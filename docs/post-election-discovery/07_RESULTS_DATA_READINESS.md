# 07 Results data readiness

Rule applied here: a source is **not** said to provide a field unless a capture or a source-registry entry in the repositories shows it did. Candidate sources that were not tested are listed as Unknown. Raw data availability is kept separate from what the site actually does today. Checked 2026-11-04 (the day after Election Day); no results pull was run during this audit.

## 1. Capability matrix

| Capability | Raw data held today | Site functionality today | Evidence |
|---|---|---|---|
| Election results by candidate (general election) | **No** | **No** | No table or file stores votes per candidate for the 2026 general. TIP `races` has no per-candidate result columns. LLF has no results files |
| Race calls and result status | Schema scaffolding only | **No** | TIP `races.result_status` (check constraint: `none`, `pending`, `reported`, `projected`, `certified`), `result_as_of`, `result_source_url`. All 574 rows are `none`. No TIP or LLF code reads them (search of `app/`, `lib/`, `components/`, `elections.py`, `build.py`) |
| Vote counts and percentages | **No** | Partial and manual | Three Florida August 18 primary winners' percentages sit in `data/elections/FL/story_data.json` and feed one hand-built bar chart (`result_bars()`). Source registry entry `fl-doe-election-watch` records Florida Division of Elections statewide and county primary result pages and cite a Democratic Senate primary result read from them |
| Reporting completeness (precincts or percent reporting) | **No** | **No** | No field, table or source entry |
| Certification status | Enum value only | **No** | `certified` exists as an allowed `result_status`; nothing sets it. No state certification source has been read |
| Historical comparisons | Minimal | **No** | Every TIP race and candidate row is cycle 2026. `candidates.bp_last_election` is a free-text last-election date (for example "November 5, 2024") on at least 1,000 rows, without results. No 2022 or 2024 results are stored in either system. Census files hold geography, not past votes |
| Congressional district geography | **Yes** | **Yes** | `data/elections/<ST>/districts.json` (SVG paths and label points) for FL (28), IL (17), MI (13), NY (26), NJ (12), MN (8), PA (17), built from the Census `cb_2024_us_cd119_500k` file (119th Congress districts); Florida uses the state's 2026 plan (EDR, HB 1-D) as a separate registry source. District maps appear on the seven House index pages |
| County-level voting data | **No** (geography overlap for Florida only) | **No** | Florida is the only state with `counties=True`: `data/elections/FL/districts.json` lists each of the 28 districts' largest counties with share of district area and a population, built from the Census county file, and the Florida House pages show them. The other six states have empty `counties` lists and `counties=False`. No county vote totals exist; the registry notes Florida county primary results (`fl-doe-election-watch`) were referenced, but no county results page or dataset is built |
| Campaign finance (candidate committees) | **Yes** | Partial | TIP `fec_candidate_totals` (4,016), `fec_candidate_finance` (7,972), `committees` (7,103); LLF `data/elections/FL/finance_fec.json` and `tools/elections/fetch_fec.py`. LLF state pages set `finance=False` for every state except Florida |
| Independent expenditures | **Yes, narrow** | Partial | `data/elections/FL/ie_*.json`, `tools/elections/fetch_fec_ie.py`, `reconcile_ie.py` (pairs 24 and 48-hour notices with periodic-report rows), `tools/dark_horse/schedule_e.py` and `fetch_udp_ie.py`; TIP `source_issue_money_signals` (577, AIPAC-related). Used in Spending Reports; not a general-purpose store |
| FEC information | **Yes** | Yes | OpenFEC through `FEC_API_KEY` (kept in `looklearnfind/.env.local`, git-ignored, not stored in data). `openfec` and `openfec-candidate-totals` are registry sources. FEC IDs key TIP candidates and the LLF roster |
| Sources and provenance | **Yes** | Yes | Dated, hashed raw captures in `data/elections/<ST>/captures/`; `source_registry.json` (17 sources, `owner_approved` false except `tip-db`); `news_source_registry.json`; `DATA_ACCESS_LIMITATIONS.md`; the article sources blocks |
| Market data after the election | Yes, pre-election | Pre-election snapshots | `markets.json` per state (last captures 2026-10-23 to 2026-11-01) and the daily monitor (last run 2026-11-03). Contracts are party-winner contracts; whether the Kalshi API returns a settled outcome for these markets after resolution **has not been tested** |

## 2. Existing integrations, jobs and services that could carry post-election work
- **Daily monitor** (`tools/dark_horse/daily.py`, `cron_run.sh`): proven pattern for a scheduled fetch that writes dated JSON, keeps last-good data when a provider fails, tracks per-provider staleness and copies a status file to the server. Its coverage is 24 monitored races (21 with a Kalshi mapping, 1 Polymarket, 7 with polls).
- **Per-state fetchers** (`fetch_kalshi.py`, `fetch_portraits.py`, `build_cd_geometry.py`, `build_*_roster.py`, `join_tip.py`): fetch, capture and normalize into `data/elections/<ST>/`.
- **TIP export** (`scripts/export/state-packet.mjs`): exports races, race entries, candidates, grades and finance snapshots per state; the only bridge from the database to LLF.
- **TIP write scripts** with backup and idempotence (`apply-*-gap-fixes.mjs`, `promote-*-governor-entries.mjs`): the established way to change TIP rows.
- **Build-time generators** for hubs, race and district pages (`elections.py`) already render a per-race page for 132 races in seven states; they have no results input.

## 3. Candidate result sources (all Unknown until tested)
Not confirmed to provide any field: state election-results sites (Florida's has been read for the primary; Illinois and New York official sites blocked automated requests during rostering, and Minnesota's Secretary of State is behind a captcha); county sites; Green Papers (read for rosters and general-election status text, not tested for vote totals); Kalshi settlement data; Associated Press or other commercial feeds (no integration, no account, no licence in the repositories); the FEC (no results; finance only). Any results ingestion must also follow R15: an unreadable source is recorded, and nothing it would have provided is called official or complete.

## 4. Gaps that need new infrastructure (observations)
1. A store for per-candidate vote totals, percent reporting, timestamps and source, with a defined meaning for each `result_status` value.
2. A fetch and capture job for each source, including a plan for blocked state sites (the repository's rule is not to circumvent bot checks).
3. A rendering path that reads results rather than only rosters (LLF) and a decision on whether TIP's `races.result_*` columns or a new table is the system of record.
4. County and past-election datasets (none held) and the geography to attach them to (county geometry and overlap exist only for Florida districts).
5. A policy for calls and projections (the editorial rules forbid win probabilities; calls and projections are not covered by any current rule).
