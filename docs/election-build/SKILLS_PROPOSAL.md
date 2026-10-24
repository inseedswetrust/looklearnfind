> **SUPERSEDED 2026-10-24** by the lean editorial reset: the only required exchange is STORY_BRIEF.md and CLAIMS.csv (see docs/election-build/INDEX.md and docs/story-briefs/). The 14-file packet is optional reference. Kept for history.

# Skills Proposal: repeating research, fact-check, write, build, QA and update for another state

**Status:** proposal only. Nothing below is built as a skill or automation. The code listed under "existing" is real and was used to build the Florida pages.

## Answer to the question asked

The smallest set that repeats this cycle with substantive reporting is **five skills and four file contracts**. Writing stays with a person or with the writing model; skills handle everything that has a right answer.

**Contracts (all plain files in git, so ChatGPT and Claude Code read the same thing):**
1. `data/elections/<ST>/` packet: `roster.json`, `candidates.json`, `districts.json`, `finance_fec.json`, `ie_*.json`, `markets.json`, `portraits.json`, `captures/` with hashes. (Exists for FL.)
2. Story file: `content/learn/<slug>.html` with front matter, `<!--openfile-->`, `<!--sources-->`, `<!--corrections-->`, and `[[v:name]]` data macros for every number. (Exists.)
3. `fact_check.csv`: `claim_id,page,claim,value,source,as_of,verdict,notes`; verdicts VERIFIED, ATTRIBUTED, NEEDS_CONTEXT, UNVERIFIED, CONTRADICTED, STALE. (Exists.)
4. `ASSET_MANIFEST.csv` and `status.json` (stage, blocker, hash). Manifest exists; `status.json` is new.

## Dependency diagram

```
election-state-packet ──► llf-factcheck-finalize ──► llf-election-render ──► llf-publication-qa ──► (owner deploys) ──► llf-update-monitor
        │                         ▲                         ▲                       │                                        │
        └── roster/TIP diff ──────┘                         └── packet changes ─────┘◄───────── re-run when sources change ──┘
```

## The five skills

### 1. `election-state-packet` (build first)
| Field | Content |
|---|---|
| Value | cut hours of manual roster, finance, market and map work to one repeatable run |
| Existing | `tools/elections/fetch_fl_roster.py`, `build_fl_geometry.py`, `join_tip.py`, `fetch_fec.py`, `fetch_fec_ie.py`, `fetch_kalshi.py`, `fetch_kalshi_history.py`, `fetch_portraits.py`, `fetch_heroes.py`; TIP `scripts/export/state-packet.mjs` |
| Trigger | new state, or "refresh <state>" |
| Input | `{state, cycle, offices:[GOV,S,H], sources:{roster_url, map_url}}` |
| Tools | state election site, OpenFEC, Kalshi public API, Census, Wikimedia, TIP read-only export |
| Output | the packet folder plus `reconciliation.md` (official vs TIP: added, removed, spelled differently) |
| Checklist | 1 fetch and hash roster pages; 2 parse with all statuses; 3 diff to TIP; 4 fetch map and county file; 5 FEC totals and IEs with dedupe; 6 Kalshi events and quotes; 7 portraits with licenses |
| QA gates | counts per office match expectations; every roster row has a source URL; no unopposed or write-in dropped; FEC dedupe test passes (see tests); every TIP URL checked live |
| Failure states | source blocked (403/429) → recorded as `blocked` with fallback; unmatched candidate → listed, never guessed |
| Provenance | every file hashed and timestamped in `captures/` |
| Security | read-only keys only, from environment, never written to output |
| Human touchpoints | approve any TIP database fix proposed by the diff |
| Tests | golden fixtures: unopposed candidate; amended Schedule E; same transaction on F24 and F3X; memo row; candle end-time to ET day; wrong-person portrait match |

### 2. `llf-factcheck-finalize` (build second)
| Field | Content |
|---|---|
| Value | enforces the gate in `02_FACT_CHECK_AND_FINALIZE_SKILL_SPEC.md` so a draft cannot publish with unverified numbers |
| Existing | `docs/election-build/fact_check.csv` format; `[[v:]]` macros and build-time assertions in `elections.py` |
| Trigger | a draft story file or a changed packet |
| Input | story file, packet, source registry |
| Tools | the packet, WebFetch/search, a source registry (append-only list of approved outlets) |
| Output | `fact_check.csv`, `article_changes.md`, `ledger.json`, `READY` or `BLOCKED` with blockers |
| Checklist | the spec's 12 steps; extract each checkable claim; replace typed numbers with macros; money, market, poll and TIP-grade sub-checks |
| QA gates | no UNVERIFIED, CONTRADICTED or STALE claim on a published page; every number traces to a macro or a cited source; polls have field dates, sample, method, MOE |
| Failure states | paywalled source → claim stays UNVERIFIED and is cut; source conflict → CONTRADICTED with both cited |
| Human touchpoints | reviewer signs off on money, allegation and quote claims; owner approves final |
| Tests | the Florida drafts as regression: the skill must flag the WaPo figures, the $146.2M total, the 73-to-67 framing and the mockup names |

### 3. `llf-election-render` (build third, mostly done)
| Field | Content |
|---|---|
| Value | page implementation from data, no hand-built pages |
| Existing | `elections.py` (hub, governor, senate, house, district, methods, report layout, charts), `elections.css`, `build.py` hooks |
| Trigger | packet or story changed |
| Input | packet, story files, design tokens |
| Output | built pages in `dist/`; update zip |
| QA gates | build assertions pass; no hardcoded state names in templates beyond a `STATE` config (needs generalizing: today routes and some copy say Florida) |
| Failure | a missing data field renders an explicit "not on file" state, never blank or zero |
| Work to make it multi-state | move state strings and office rules into `data/elections/<ST>/config.json`; parameterize the governor/Senate guides by office list |

### 4. `llf-publication-qa`
| Field | Content |
|---|---|
| Value | the checks that caught footer overflow, grid overflow and a missing icon, run every time |
| Existing | `tools/qa/shots.py`, `smoke.py`, `make_manifest.py`, `rebuild_serve.sh` |
| Trigger | before handing a zip over, and again against the live URL after deploy |
| Gates | 1440 and 390 screenshots, overflow, alt text, broken images, internal and TIP links, canonical, og tags, no `noindex` on new pages, robots and sitemap compared with live |
| Output | `QA_EVIDENCE.md` with the numbers and screenshots |
| Human touchpoint | owner uploads the zip; the skill verifies live |

### 5. `llf-update-monitor` (later)
Re-runs the captures on a schedule you approve, diffs against the last packet, and opens a correction task instead of silently rewriting. Triggers: new FEC 24/48-hour report, Kalshi quote beyond a configured move with enough volume, state roster change, new result. Output: a diff and a proposed note for the story's corrections block.

## First three to implement and why
1. `election-state-packet`: it removes the most time and its tests prevent the worst errors (wrong totals, dropped candidates).
2. `llf-factcheck-finalize`: it is the publish gate you require.
3. `llf-publication-qa`: it already exists as scripts; wrapping it is cheap and it prevents shipping a broken page.

## Folder structure

```
.claude/skills/election-state-packet/SKILL.md      -> calls tools/elections/*.py
.claude/skills/llf-factcheck-finalize/SKILL.md     -> reads content/learn/*.html + data/elections/<ST>/
.claude/skills/llf-publication-qa/SKILL.md         -> calls tools/qa/*.py
tools/elections/   tools/qa/   elections.py   data/elections/<ST>/   docs/election-build/
```
Use a skill where judgment or a multi-step procedure repeats (factcheck, update monitor). Keep plain scripts where there is no judgment (fetch, dedupe, geometry, screenshots).

## Logging and dashboard
Per story: `WORKFLOW_LOG.md` (columns `timestamp_utc, project_id, page_id, stage, tool, source_records, asset_ids, file_paths, action_taken, validation_pass, reviewer, decision_id, reason, blocker, next_action`) plus `DECISIONS.md` and `ASSETS.csv`. Persistent state: `production/<state>/status.json` generated from the log; no new database until a second state is in flight.

## Two dry runs
1. **Georgia packet:** run `election-state-packet GA` with the governor and Senate offices; expect a reconciliation diff and a list of blocked sources; no pages written.
2. **Delta refresh:** re-run `fetch_kalshi_history` for MI, rebuild, confirm the build assertions in `stats_delta()` either pass or stop the build, and that `fact_check.csv` rows FC-040 to FC-043 are re-verified.

## Human touchpoints, in one list
Roster discrepancies that touch TIP data; any money, allegation or quote claim; spotlight selection rule; the zip upload; any TIP database write.

## Effort estimate and what the repo already supports
Wrapping the existing scripts as skills 1 and 4: small. Generalizing `elections.py` and the fetchers beyond Florida (state configs, office variations, top-two and runoff states such as CA, WA, LA): the largest piece. The fact-check skill needs a source registry and the ledger format; both are specified above. Not estimated in hours because no durations were measured in this build.
