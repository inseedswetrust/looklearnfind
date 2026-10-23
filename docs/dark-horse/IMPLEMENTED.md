# Dark-horse monitor: IMPLEMENTED

**Date:** 2026-10-23. **Status:** collector built, tested, run live, installed as a daily job on the LLF server. First scheduled run: **2026-10-24 08:00 America/New_York** (not yet observed; see "What is not proven").

## What was done against the request

| # | Request | Result |
|---|---|---|
| 1 | Verify the 28 watchlist names against TIP and official rosters | Done. 28 rows kept as supplied (`watchlist_original.csv`); `watchlist.csv` adds TIP IDs, race keys, ballot status, primary outcome (cited), documented criteria and a status. **6 meet a documented criterion, 4 partial, 2 unverified, 16 background leads.** 24 have a ballot verified from TIP's official record; 4 gaps (Wahab and Haynes have no TIP profile; Al Green has no TIP entry for TX-09; Omar's TIP entry rests on owner-supplied sources only) |
| 2 | Reuse Kalshi code; add Polymarket (Gamma + CLOB); no fake URLs or odds | Done. Kalshi lookups follow the existing `tools/elections/fetch_kalshi*.py` approach; Polymarket Gamma for market metadata, CLOB for last trade and book. **Every Kalshi House and Senate contract found is a party-winner contract** (rules: "member of the Democratic Party is sworn in") labeled with the candidate's name; recorded as `party_winner`, never as a named-candidate contract. Polymarket has **two** matched individual-winner contracts (Wahab CA-14, Wiener CA-11); the other search hits were unrelated or derivative markets and were not mapped |
| 3 | VoteHub beta API for race polls | Tested. **VoteHub has race-level polls** (`poll_type=us-senator`, `us-representative`, `governor`) with pollster, sponsor, partisan flag, field dates, sample and original URL. Watchlist coverage: Senate polls for MI, FL, IL, MN; House polls for CA-11, CA-22 and MI-07 only. 270toWin's House page lists no district polls and states no reuse terms, so it was not scraped. VoteHub's terms page returned 403, so licensing is recorded as unverified |
| 4 | Daily folder, manifest, latest pointer, error states, retry, status.json, status view | Done: `daily/<date>/`, `manifest.json` with capture hashes, `latest.json` (moves only for a complete day), `status.json`, `alerts.json`, atomic writes, no blind retry on 429; status page `/elections/2026/dark-horse/status/` (built, ships with the next LLF zip) and a live public `status.json` |
| 5 | Skills from templates and real scripts | Four skills under `.claude/skills/` (paths below). Roles and boundaries in `docs/dark-horse/OPERATIONS.md` |
| 6 | Live tests | **21 Kalshi rows, 1 Polymarket row, 70 poll rows, 0 errors** locally and again on the server. 9 fixture tests pass with no network (`python3 -m unittest tests/test_dark_horse.py`) |
| 7 | Install the daily job | Installed on the LLF hosting account (proof below) |
| 8 | Carry over R1/R2, fact-check ledger, capture hashes | Capture SHA-256 in every `manifest.json`; ledger format and R1/R2 are in the `llf-factcheck-finalize` skill and apply to any article written from this data (none written yet) |
| 9 | Deliverables | This file, `RUN_REPORT.md`, coverage matrix, skills, changed files, job proof |

## Watchlist: what the evidence supports (not a ranking)

Criteria: C1 incumbent defeated (cited), C2 FEC-documented United Democracy Project (UDP) spending against the nominee or for the defeated opponent, C3 establishment-endorsed opponent (cited). Only rows with a verified criterion are `meets`; every other row is a background research lead. UDP independent expenditures come from OpenFEC Schedule E for the 2026 cycle (de-duplicated, 24/48-hour notices preferred). **AIPAC PAC itself reported no independent expenditures.** Direct AIPAC PAC contributions (Schedule B) and other AIPAC-affiliated committees were not pulled.

| Candidate | Race | Status | Primary outcome (source) | UDP spending (FEC) | Establishment opponent |
|---|---|---|---|---|---|
| Abdul El-Sayed | MI SEN | meets | Won the Aug 4 2026 Democratic primary 48.4% to Haley Stevens 47.6% (AP called Aug 5) | UDP independent expenditures in the 2026 cycle (FEC): opposed El-Sayed $20.6M (2026-06-30 to 2026-10-21), supported Stevens $10.5M | Opponent Stevens described as the moderate, establishment-backed wing (Wikipedia) |
| La Shawn Ford | IL HOUSE-07 | partial | Democratic nominee for IL-07 (Wikipedia); vote shares not retrieved | UDP supported the defeated rival Conyears-Ervin $5.0M (2026-02-10 to 2026-03-10) (FEC) | no: retiring Rep. Danny Davis endorsed Ford (Wikipedia) |
| Aisha Wahab | CA HOUSE-14 | partial | Won the Aug 18 2026 CA-14 special runoff with 53.1% over Melissa Hernandez; both on the November full-term bal | UDP opposed Wahab $1.6M and supported Hernandez $825K (2026-08-04 to 2026-08-11) (FEC). Wikipedia reports 'more than $5 million' from two AIPAC-affili | not documented |
| Brad Lander | NY HOUSE-10 | meets | Won the Jun 23 2026 primary 65.8% to 34.0%, defeating incumbent Dan Goldman | none found in FEC UDP data (2026 cycle) | Goldman is the incumbent; leadership endorsement of Goldman not confirmed |
| Analilia Mejia | NJ HOUSE-11 | partial | Won the Feb 5 2026 special primary 29.3% to Tom Malinowski 27.6%; won the Apr 16 special general; sworn in Apr | UDP opposed her rival Malinowski $4.7M (2026-01-17 to 2026-02-02) (FEC); no UDP spending for or against Mejia | not documented |
| Darializa Avila Chevalier | NY HOUSE-13 | meets | Defeated incumbent Adriano Espaillat 48.6% to 45.2% in the Jun 23 2026 primary | none found in FEC UDP data (2026 cycle) | not documented |
| Melat Kiros | CO HOUSE-01 | meets | Defeated 15-term incumbent Diana DeGette in the Jun 30 2026 primary by over 20,000 votes | none found in FEC UDP data (2026 cycle) | not documented |
| Claire Valdez | NY HOUSE-07 | partial | Won the Jun 23 2026 primary 56.1% to Antonio Reynoso 35.8% | none found in FEC UDP data (2026 cycle) | Reynoso endorsed by Velazquez and WFP: a factional contest, not a unanimous establishment |
| William Lawrence | MI HOUSE-07 | unverified | Not verified in this pass (no source retrieved) | not checked | unknown |
| Donavan McKinney | MI HOUSE-13 | meets | Defeated incumbent Shri Thanedar 51.9% to 48.1% in the Aug 4 2026 primary | none found in FEC UDP data (2026 cycle) | not documented |
| Randy Villegas | CA HOUSE-22 | unverified | Top-two result not verified in this pass; TIP shows an official record on the November ballot | not checked | unknown |
| Luke Bronin | CT HOUSE-01 | meets | Defeated incumbent John Larson at the May 11 2026 convention and won the Aug 11 2026 primary | none found in FEC UDP data (2026 cycle) | no: Bronin had the state party endorsement |

Prior leads, corrected: Ford was endorsed by retiring Rep. Danny Davis; Mejia benefited from spending against Malinowski, not for her; Bronin had the state party endorsement; no UDP spending for or against Biss, Lander or Stratton appears in the FEC data (other committees not checked). For Wahab, Wikipedia says more than $5 million from two AIPAC-affiliated super PACs backed Hernandez, while UDP's FEC total in that race is $0.8M supporting Hernandez and $1.6M opposing Wahab: unreconciled.

## Coverage matrix (2026-10-23, every watchlisted race)

| Race | Candidate | TIP ID | Ballot verified | Status | Kalshi | Polymarket | Polls (VoteHub) |
|---|---|---|---|---|---|---|---|
| CA HOUSE-11 | Scott Wiener | H8CA11116 | yes | lead | unavailable | ok 0.75 | 2 (ok) |
| CA HOUSE-14 | Aisha Wahab | none | no | partial | not_monitored | not_monitored | not_monitored (not_monitored) |
| CA HOUSE-17 | Ro Khanna | H4CA12055 | yes | lead | ok (party_winner) 0.986 | unavailable | 0 (no_poll_found) |
| CA HOUSE-22 | Randy Villegas | H6CA22190 | yes | unverified | unavailable | unavailable | 1 (ok) |
| CO HOUSE-01 | Melat Kiros | H6CO01273 | yes | meets | ok (party_winner) 0.973 | unavailable | 0 (no_poll_found) |
| CT HOUSE-01 | Luke Bronin | H6CT01206 | yes | meets | ok (party_winner) 0.955 | unavailable | 0 (no_poll_found) |
| FL SEN | Angie Nixon | S6FL00830 | yes | lead | ok (party_winner) 0.093 | unavailable | 16 (ok) |
| IL HOUSE-03 | Delia Ramirez | H2IL03162 | yes | lead | ok (party_winner) 0.97 | unavailable | 0 (no_poll_found) |
| IL HOUSE-07 | La Shawn Ford | H6IL07354 | yes | partial | ok (party_winner) 0.956 | unavailable | 0 (no_poll_found) |
| IL HOUSE-09 | Daniel Biss | H6IL09228 | yes | lead | ok (party_winner) 0.95 | unavailable | 0 (no_poll_found) |
| IL SEN | Juliana Stratton | S6IL00458 | yes | lead | ok (party_winner) 0.993 | unavailable | 2 (ok) |
| MA HOUSE-07 | Ayanna Pressley | H8MA07032 | yes | lead | ok (party_winner) 0.99 | unavailable | 0 (no_poll_found) |
| MI HOUSE-07 | William Lawrence | H6MI07298 | yes | unverified | unavailable | unavailable | 2 (ok) |
| MI HOUSE-12 | Rashida Tlaib | H8MI13250 | yes | lead | ok (party_winner) 0.982 | unavailable | 0 (no_poll_found) |
| MI HOUSE-13 | Donavan McKinney | H6MI13254 | yes | meets | ok (party_winner) 0.962 | unavailable | 0 (no_poll_found) |
| MI SEN | Abdul El-Sayed | S6MI00418 | yes | meets | ok (party_winner) 0.68 | unavailable | 39 (ok) |
| MN HOUSE-05 | Ilhan Omar | H8MN05239 | owner_supplied_only | lead | not_monitored | not_monitored | not_monitored (not_monitored) |
| MN SEN | Peggy Flanagan | S6MN00440 | yes | lead | ok (party_winner) 0.85 | unavailable | 8 (ok) |
| NJ HOUSE-11 | Analilia Mejia | H6NJ11286 | yes | partial | ok (party_winner) 0.976 | unavailable | 0 (no_poll_found) |
| NJ HOUSE-12 | Adam Hamawy | H6NJ12417 | yes | lead | ok (party_winner) 0.962 | unavailable | 0 (no_poll_found) |
| NY HOUSE-07 | Claire Valdez | H6NY07214 | yes | partial | ok (party_winner) 0.98 | unavailable | 0 (no_poll_found) |
| NY HOUSE-10 | Brad Lander | H6NY10176 | yes | meets | ok (party_winner) 0.972 | unavailable | 0 (no_poll_found) |
| NY HOUSE-13 | Darializa Avila Chevalier | H6NY13279 | yes | meets | ok (party_winner) 0.981 | unavailable | 0 (no_poll_found) |
| NY HOUSE-14 | Alexandria Ocasio-Cortez | H8NY15148 | yes | lead | ok (party_winner) 0.971 | unavailable | 0 (no_poll_found) |
| PA HOUSE-03 | Chris Rabb | H6PA03203 | yes | lead | ok (party_winner) 0.989 | unavailable | 0 (no_poll_found) |
| PA HOUSE-12 | Summer Lee | H2PA18200 | yes | lead | ok (party_winner) 0.987 | unavailable | 0 (no_poll_found) |
| TX HOUSE-09 | Al Green | H4TX09095 | no | lead | not_monitored | not_monitored | not_monitored (not_monitored) |
| TX HOUSE-30 | Frederick Douglass Haynes III | none | no | lead | not_monitored | not_monitored | not_monitored (not_monitored) |

## Sample real rows

| Venue | Candidate | Contract | Kind | Quote type | Price | Bid | Ask | Volume |
|---|---|---|---|---|---|---|---|---|
| polymarket | Scott Wiener | 112035258287671416806059 | candidate_individual | last_trade | 0.75 | 0.77 | 0.79 | 7149.002751 |
| kalshi | Abdul El-Sayed | SENATEMI-26-D | party_winner | last_trade | 0.68 | 0.68 | 0.69 | 3777672.54 |
| kalshi | La Shawn Ford | KXHOUSERACE-IL07-26-D | party_winner | last_trade | 0.956 | 0.966 | 0.993 | 34.03 |
| kalshi | Daniel Biss | KXHOUSERACE-IL09-26-D | party_winner | last_trade | 0.95 | 0.966 | 0.988 | 1971.0 |
| kalshi | Brad Lander | KXHOUSERACE-NY10-26-D | party_winner | last_trade | 0.972 | 0.969 | 0.99 | 633.75 |

## Skills (Claude Code)
- `.claude/skills/darkhorse-source-monitor/SKILL.md`
- `.claude/skills/llf-delta-editorial/SKILL.md`
- `.claude/skills/llf-factcheck-finalize/SKILL.md`
- `.claude/skills/workflow-retrospective/SKILL.md`

## Daily job proof
- Host: LLF hosting account (ascendan@65.181.121.38), private folder `~/llf-data/dark_horse` (mode 700), Python 3.9.25.
- Crontab installed 2026-10-23 (the account had no crontab before; backup `crontab.backup-20261023`): `CRON_TZ=America/New_York`, then `0 8 * * *` running `daily.py`, `alert_if_stale.py` and a copy of `status.json` to the public web folder.
- The exact command was run by hand on the server at 18:45 UTC and succeeded (21 Kalshi, 1 Polymarket, 70 poll rows, exit 0, public status file written).
- **Status URL (live now):** https://looklearnfind.com/elections/2026/dark-horse/status.json
- Staleness: `alert_if_stale.py` exits 1 and prints when a source is over 48 hours old; cron mails the output to the account contact (no MAILTO set).

## What is not proven
- No unattended scheduled run has happened yet. After 12:00 UTC on 2026-10-24 (08:00 EDT) check `ls ~/llf-data/dark_horse/data/elections/dark_horse/daily` and `tail ~/llf-data/dark_horse/logs/daily.log`. This host's cron may not honor `CRON_TZ`; if the run lands at the wrong hour, replace it with a UTC time (12:00 UTC until Nov 1, 13:00 UTC after).
- Server data and repo data are separate. `tools/dark_horse/pull_from_server.sh` backs the server folders up into the repo; `sync_to_server.sh` pushes mapping changes.
- VoteHub licensing, and Polymarket terms for the owner, were not verified; read access works from this network and from the server.
- 17 of 24 monitored races have no poll. Monitored races with no Kalshi market: Scott Wiener, Randy Villegas, William Lawrence.
- The 3-point change threshold in `alerts.json` is a placeholder to calibrate after several real days.

## Changed and new files
LLF repo: `tools/dark_horse/*`, `data/elections/dark_horse/*`, `tests/test_dark_horse.py`, `.claude/skills/*`, `docs/dark-horse/*`, `elections.py` (adds only the status page), `.gitignore`. No existing live page was changed. TIP: read-only lookups only.
