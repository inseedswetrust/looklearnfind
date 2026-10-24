# Workflow Log: Florida election pages build

Times are order of events in one session on 2026-10-22 to 2026-10-23 (durations were not measured). Columns follow the requested log fields; unused fields are omitted.

## Timeline

| # | stage | tool | action_taken | result | decision / obstacle | next |
|---|---|---|---|---|---|---|
| 1 | read | shell, image viewer | unzipped handoff; read 5 instruction files, 4 article drafts, 8 schemas, 8 mockups | scope: governor, Senate, House; 8 pages | the mockups are AI images with wrong people and numbers | audit data |
| 2 | map | read build.py, site.json, BRAND.md | LLF is a static Python build (`build.py`) + PHP/SQLite; stories use `[[s:n]]` footnotes and an `openfile` block | no election routes exist | D1: add an `election` kind in a new module `elections.py`, reuse Story Reader parts | get roster |
| 3 | roster | curl, Python | fetched state candidate lists (governor, federal) and parsed them | governor 10 qualified; Senate 3; House 83 in 28 districts | obstacle: "Qualified" filter dropped Frost (FL-10, status "Unopposed") and a section header bug mixed in state legislature rows; fixed by pulling all statuses and cutting sections at each header | reconcile with TIP |
| 4 | reconcile | Python | compared official roster to TIP `race_entries` | only difference: Gillespie spelling | TIP governor roster is empty | map |
| 5 | geometry | web search, curl, geopandas | found that Florida enacted a new map in May 2026 (HB 1-D); downloaded the official EDR shapefile and Census counties | 28 districts as SVG paths, county shares | D2: use the official file, not Census 118th/119th boundaries | TIP join |
| 6 | TIP join | Python, HTTP | joined candidates to TIP pages and Issue Grades; checked every TIP URL | 79 live pages, 23 candidates with a grade, 2 URLs 404 | D3: link only URLs that return 200; "not graded" is a dash, never zero | finance |
| 7 | finance | OpenFEC | pulled totals and Schedule E for all roster candidates | 72 with totals | obstacle: by-candidate IE totals ($1.2M for Beltran) vs transaction sums ($10.0M): the by-candidate endpoint covers periodic filings only; 24/48-hour notices carry the recent money | dedupe rule |
| 8 | dedupe | Python | found the same transaction on both an F24 notice and a later F3X; found memo rows | D4: one row per (committee, transaction, amount, date), prefer notice, drop memo X | golden fixture candidate | markets |
| 9 | markets | Kalshi public API | listed Florida events, captured governor, Senate and 26 House contracts; pulled MI candlesticks | quotes and 34 daily plus 803 hourly candles | obstacle: candle `end_period_ts` marks period end; daily candles end 04:00Z = previous Eastern day. Caught before publishing; added `et_day` | polls |
| 10 | polls | WebFetch, search | verified UNF (via WLRN), Marist (page), debate date (ClickOnDetroit) | numbers ledgered | obstacle: Washington Post page blocked; Florida campaign finance site blocked (403) | policy text |
| 11 | policy | WebFetch | read each campaign's issue pages | attributed proposals | D5: campaign statements labeled as such; no property-tax claim beyond what the page says | assets |
| 12 | assets | Wikimedia API | fetched 30 portraits and 3 hero photos with license metadata | found a wrong match (Sydney Gruters matched Joe Gruters) | fix: require first and last name in the article title; D6: monogram for anyone without a license | icons |
| 13 | design | SVG | wrote 6 issue icons | | obstacle: one icon file name did not match the issue slug, so the sprite id was missing; renamed | CSS |
| 14 | build | Python, CSS | wrote `elections.py`, `elections.css`, `elections.js`; added `layout: report` | 110 pages | obstacles: Windows default encoding broke `build.py` (run with `PYTHONUTF8=1`); `%-d` strftime fails on Windows (fixed); class collisions with site.css (`.tile`, `.rail`, `.tabs`) renamed | QA |
| 15 | write | editor | wrote the three reports; numbers in text come from data macros `[[v:name]]`; Delta stats assert against the data | | D7: if data changes, the build fails instead of silently showing old copy | QA |
| 16 | QA | Playwright (Edge) | screenshots at 1440 and 390; overflow and image checks | found footer overflow at 390 and grid overflow on senate and district pages | fixed (`min-width:0`, wrap) | smoke |
| 17 | smoke | `tools/qa/smoke.py` | 36 pages, 62 internal and 200 external links | 36/36 OK; no broken internal links | Kalshi URLs rate-limited | package |
| 18 | package | zip | built update zip without robots files | | D8: do not overwrite the live robots.txt | deploy |
| 19 | deploy | none | not possible from this environment (no cPanel credentials) | **blocked** | concrete owner steps in IMPLEMENTATION_REPORT | owner |

## Decisions

| id | context | choice | alternatives | rationale | re-evaluate when |
|---|---|---|---|---|---|
| D1 | where election pages live | new module `elections.py` plus a `layout: report` story variant | rewrite templates in build.py; separate microsite | smallest change to a working static build; keeps brand and search | second state added |
| D2 | district map | official EDR file | Census TIGER 119th | the 2026 map replaced the old one | map ruling in the courts |
| D3 | TIP links and grades | link only on HTTP 200; three chip states | link all; zero for ungraded | avoid dead links; unknown is not zero | TIP launches more pages |
| D4 | independent expenditures | deduped transactions, notices preferred | FEC by-candidate totals | totals were 8x too low for recent weeks | FEC changes its API |
| D5 | governor committee money | press-reported, dated, labeled | omit; show draft totals | state site blocked; unverified draft totals removed | state data retrievable |
| D6 | portraits | licensed only; otherwise monogram | all monograms; mockup faces | owner rule: lawful sources, consistent placeholder otherwise | candidates supply photos |
| D7 | numbers in prose | data macros plus build assertions | typed numbers | avoids stale copy | any |
| D8 | deploy zip | omit robots.txt | full zip | live robots differs from the repo | launch day |
| D9 | Spending Report basis | FEC filings | ad-tracker article | article blocked; FEC is primary | AdImpact data available |

## What cost the most time (design the skills around these)

1. Stale or wrong inputs: mockups, drafts and TIP rows each needed re-verification (roster, phase, finance dates).
2. Sources that block automation: Washington Post (403), Florida campaign finance database (403), Kalshi pages (429).
3. Data-semantics traps that produced wrong numbers until caught: unopposed status, section-header bleed, F24 vs F3X duplicates, memo rows, candle end-time vs ET day, wrong Wikipedia name match.
4. Environment: Windows encoding and date format, class-name collisions with existing CSS, file locks from a running server, robots overwrite risk on deploy.
5. No deployment access from the build environment.

## Improvements for the next state

- Run the roster, FEC and market captures first and diff them against TIP before writing anything.
- Keep prose numbers as macros and keep the build assertions.
- Check the deploy zip against live robots and sitemap before handing it over.
- Add a staging path (a hidden folder on the host) so QA runs against the same server as production.

## 2026-10-23 follow-up: owner review after deploy
| # | action | result | decision |
|---|---|---|---|
| 20 | Owner asked why Donalds shows grades in the article but not on TIP | confirmed: TIP's governor profile `GOV-FL-DONALDS` shows all six issues "Not graded"; the grades live on his congressional profile `H2FL14186` | D10: show grades only with a link to the TIP page where they are visible; link both profiles on the card |
| 21 | Owner set two publishing rules (R1 candidate to TIP profile, R2 race to race link) | implemented as build-time autolink plus a violation report; `--strict` fails the build | D11: rules live in `docs/election-build/PUBLISHING_RULES.md`; 17 candidates have no working TIP profile, listed there |

## 2026-10-23 · Round 1 Phase A (workflow and skills lock)
- Baseline audit: four skills installed (`darkhorse-source-monitor`, `llf-delta-editorial`, `llf-factcheck-finalize`, `workflow-retrospective`), none overwritten; four added (`election-state-packet`, `llf-article-format`, `llf-election-render`, `llf-publication-qa`). `asset-manifest` kept as a script plus format. Reason: the other three are already scripts with a clear owner; a standalone skill would duplicate `make_manifest.py`.
- Decision: the daily job fires at 12:00 and 13:00 UTC and `cron_run.sh` proceeds only when the New York hour is 08. Reason: `CRON_TZ` support on this shared host cannot be inspected (no cron binary or logs are visible in the jail), and a UTC pair is correct on both sides of the 2026-11-01 DST change.
- Decision: a finished day folder is immutable; a rerun becomes `revisions/rN` and `latest.json` moves forward only. Reason: the order forbids overwriting historical snapshots. `--dry-run` now writes only under `dry_runs/`.
- Found while testing: a nested-quote edit made on 2026-10-23 broke the previous-day lookup for a fresh data folder; caught by the new dry-run test and fixed before any unattended run.
- Found: the Kalshi FL capture file was named by date and a rerun overwrote the 14:34Z capture. Fixed: timestamped capture names.
- Found: Al Green lost the TX-18 runoff (news reports, search summary) and was never a TX-09 candidate; his row is now `not_on_ballot`. Haynes, Omar and Wahab are `on_ballot_news_only` until an official list is opened.
- Found: the fact-check ledger had two malformed rows (FC-025, FC-047, a missing `value` column) that the new gate caught; fixed.
- Decision (owner, 2026-10-24): the FEC Schedule B pull for AIPAC PAC is removed from the workflow. With a key supplied, the endpoint ignored a candidate filter and about 38,000 of 39,400 rows were earmarked individual donations passed through the PAC, so it was slow and not informative. `fetch_aipac_direct.py` was deleted. AIPAC and UDP ties are gathered from news by simple searches instead.
- Research: reporting digest built from five opened articles; unopened search-summary items are labeled and not to be used until verified.
