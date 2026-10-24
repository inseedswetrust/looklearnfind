# Canonical index: schemas, skills, tools and contracts

Single source for "where is X". Everything below is in this repository (branch `claude/funny-shannon-dg9qoe`). Updated 2026-10-23, Round 1 Phase A.

## Article schemas (one page each, in `docs/schemas/`)
| # | Schema | Page | Notes |
|---|---|---|---|
| 1 | State of the Race | `docs/schemas/01_STATE_OF_THE_RACE.md` | state guide plus race modules |
| 2 | Delta Report | `docs/schemas/02_DELTA_REPORT.md` | same-instrument change; reference article `michigan-senate-delta-october-2026` |
| 3 | Spending Report | `docs/schemas/03_SPENDING_REPORT.md` | reference article `florida-house-independent-spending-october-2026` |
| 4 | Dark Horse vs party establishment | `docs/schemas/04_DARK_HORSE_PARTY.md` | needs `lock_status = verified` candidates |
| 5 | Dark Horse vs verified AIPAC/UDP-supported candidate | `docs/schemas/05_DARK_HORSE_AIPAC.md` | FEC Schedule E spending kept apart from news-reported endorsements and ties |
| 6 | AIPAC-supported candidates still running | `docs/schemas/06_AIPAC_CANDIDATES_STILL_RUNNING.md` | |
| 7 | State and race article requirements | `docs/schemas/07_STATE_AND_RACE_ARTICLE_REQUIREMENTS.md` | the guide and race modules |

## Skills (`.claude/skills/<name>/SKILL.md`)
`llf-story-scout` 1.0.0 (new 2026-10-24) · `llf-article-format` 1.1.0 · `llf-factcheck-finalize` 2.0.0 (claim-driven) · `llf-publication-qa` 1.1.0 · `election-state-packet` 1.0.1 (optional) · `darkhorse-source-monitor` 1.1.1 · `llf-delta-editorial` 1.0.0 · `llf-election-render` 1.0.0 · `workflow-retrospective` 1.0.0. `asset-manifest` is a script plus format, not a skill: `tools/qa/make_manifest.py` writes `docs/election-build/ASSET_MANIFEST.csv`; `fl_assets.csv` in the packet adds publication status.

## Scripts and where they live
Collection: `tools/elections/*` (roster, FEC, Kalshi, portraits) and `tools/dark_horse/*` (daily collector, watchlist lock, coverage, Schedule E dedupe, contract guards, verify, cron wrapper). Packet: `tools/elections/export_packet.py`. QA: `tools/qa/factcheck_gate.py`, `smoke.py`, `shots.py`, `dashboard.py`. Workflow: `tools/workflow/transitions.py`. Render: `build.py`, `elections.py`.

## Data contracts
`data/elections/dark_horse/` (watchlist.csv v1.1.0 with `watchlist.lock.json`, contract_map.json, `daily/`, latest.json, status.json, coverage_matrix.csv) · `data/elections/FL/` (official roster, TIP join, FEC, Kalshi) · `data/elections/source_registry.json` · `data/elections/workflow_ledger.jsonl` · `release/research_packet/` (manifest.json lists every file and hash).

## Lean editorial lane (owner reset 2026-10-24)
Required exchange: `STORY_BRIEF.md` (Claude to ChatGPT) and `CLAIMS.csv` (ChatGPT to Claude). Examples: `docs/story-briefs/`. Checker `tools/story/story_brief_check.py`; proposed outlet registry `data/elections/news_source_registry.json`; story board states DISCOVERED, SOURCE_CHECKED, DRAFTED, FACT_CHECKED, APPROVED, PUBLISHED (`story:<slug>` entities in `tools/workflow/transitions.py`; board view in `tools/qa/dashboard.py`). FEC data, the research packet and the 15-state lane are optional infrastructure.

## Tests
`python3 -m unittest tests/test_dark_horse.py tests/test_phase_a.py tests/test_factcheck_gate.py tests/test_workflow.py tests/test_story_scout.py` (54 tests, no network) · `python3 build.py --strict`.
