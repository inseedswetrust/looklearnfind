# Installed skill versions, reconciliation, QA results and blockers (2026-10-28)

## 1. What was read to establish the production system
Root `CLAUDE.md` (updated on disk by another session during this task: it now lists `llf-footage-scout` and the footage-first video order), `docs/election-build/INDEX.md`, `AGENT_RUNBOOK.md`, `PUBLISHING_RULES.md` (R1 to R10), the schemas in `docs/schemas/`, all `SKILL.md` files, the workflow ledger, the git history (head `a1fe4de` "Florida footage-first pass"; before it `cea45a3` video pack, `f119770` Florida articles, `714e492` Lean Reset), and the Lean Reset and Florida handbacks that live in those commits and in `docs/story-briefs/` and `docs/election-build/`.

## 2. Active skill versions (read from the files, not from the index)
| Skill | Version | Where the version sits | Note |
|---|---|---|---|
| `llf-story-scout` | 1.0.0 | header | used for this pass; checker `tools/story/story_brief_check.py` |
| `llf-article-format` | 1.3.0 | header | lean standard, headline test, update cadence, video pointer |
| `llf-factcheck-finalize` | 2.2.0 | header | claim-driven; lean `CLAIMS.csv`; independence rule; video check |
| `llf-election-render` | 1.1.0 | header | Florida story components |
| `llf-publication-qa` | 1.3.0 | header | freshness, OG, video QA |
| `llf-delta-editorial` | 1.0.0 | "Contract" section only | no header version line |
| `darkhorse-source-monitor` | 1.1.1 | "Contract" section only | collector ran unattended 2026-10-24 (HTTP 200 status feed) |
| `workflow-retrospective` | 1.0.0 | "Contract" section only | video additions appended without a version bump |
| `election-state-packet` | 1.0.1 → **1.0.2 (this pass)** | header | optional infrastructure; now notes the Illinois pattern |
| `llf-video-storyboard` | 1.1.0 | header | footage-first, from a parallel session |
| `llf-footage-scout` | 1.0.0 | header | from a parallel session; footage rights `CLEARED` only with a written basis |
Eleven skills are installed. None was overwritten.

## 3. Conflicts and gaps found (reported, not silently fixed unless noted)
| # | Finding | Action |
|---|---|---|
| 1 | **The governing specification "LLF Canonical Local Workflow & Skills Lock v2.0" is not in the repository, in `docs/`, or in the Downloads folder** (searched file names and contents). | Cannot be reconciled. The tested instructions in the repository were used instead. **Please supply the file**; if it changes a rule, it will be applied without overwriting newer working code. |
| 2 | **`docs/production/` does not exist** although the request names it. | Not invented. Illinois work lives in `docs/illinois/` and `data/elections/IL/` (the established pattern). Say if a `docs/production/` directory was meant to be created or lives in another checkout. |
| 3 | `docs/election-build/INDEX.md` listed stale versions (article-format 1.1.0, fact-check 2.0.0, publication-qa 1.1.0, election-render 1.0.0) and 74 tests. | **Fixed** in this pass to the versions above and 90 tests; Illinois section added. |
| 4 | Three skills (`llf-delta-editorial`, `darkhorse-source-monitor`, `workflow-retrospective`) carry their version only in a "Contract" section, not the header. | Reported; cosmetic. Left as is to avoid editing installed skills without need. |
| 5 | `AGENT_RUNBOOK.md` step 1 assumes an official-site roster fetcher per state; Illinois' official site returns HTTP 403 to automated access. | **Fixed:** one line added describing the fallback (transcribe a secondary tracker, record provenance, mark the official check PENDING, cross-check against FEC and TIP). |
| 6 | `join_tip.py`, `fetch_portraits.py` and `fetch_heroes.py` were Florida or Florida and Michigan only. | **Minimal parameterization** (not a redesign): `LLF_STATE`, optional roster fields (`tip_name`, `source_url`, `party`, `write_in`, `note`), retry on transient TIP failures, `extra_people.json`, `LLF_ONLY`, file-safe IDs, an Illinois hero. Florida output verified unchanged (only two transient failures differed). |
| 7 | The registry/index document `SKILL_AND_ROUTINE_REGISTRY.md` exists only in the Phase A handback ZIP, not in the repository. | Reported; `INDEX.md` is the in-repo map. A refreshed registry can be regenerated from the skill files on request. |
| 8 | The parallel session's footage and infographic work (commit `a1fe4de`) is consistent with `CLAUDE.md`; its tests pass. | None. |

## 4. QA results
- Tests: `tests/test_dark_horse.py test_phase_a.py test_factcheck_gate.py test_workflow.py test_story_scout.py test_video_pack.py test_footage_pack.py`: **90 run, 0 failures** (run before and after the changes).
- `python build.py --strict`: **0 violations**, 113 pages.
- Story checker (`story_brief_check.py`): **3 READY (stories 1 to 3), 2 NOT_READY (stories 4 and 5, with reasons)**.
- Claims gate (`factcheck_gate.py`) on each `CLAIMS.csv`: **READY** for all three (excluded claims are marked REMOVED).
- TIP mapping: 54 rows, 43 live profiles, 19 of 19 race pages HTTP 200, 12 candidates with grades.
- Portraits: 27 licensed images; 17 of the people searched have none (minor-party and write-in candidates were not searched).
- Workflow: six ledger entries (three stories, DISCOVERED then SOURCE_CHECKED).
- Not run on purpose: no page built, no video asset, no FEC research, no article published.

## 5. Blockers
1. Illinois State Board of Elections list: HTTP 403 (official ballot verification PENDING).
2. The Skills Lock v2.0 specification and `docs/production/` are missing (items 1 and 2 above).
3. TIP data fixes (governor entries, corrupted name, "National source only" entries, 11 missing profiles) and the owner's decision on write-in profiles.
4. District geometry and the Illinois configuration step before any page build.
5. Docket check for the Sigcho-Lopez lawsuit and primary records for stories 4 and 5.
6. Several outlets (WTTW, others) return 403 to automated fetches; those facts rest on search summaries and are marked in the briefs.
