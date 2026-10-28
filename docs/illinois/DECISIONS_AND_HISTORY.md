# Illinois workspace: decisions and history

Permanent record for the Illinois 2026 State of the Race. Index of this folder: `README.md`. Newest entries last.

## 2026-10-28 · Discovery pass (Claude Code)
**Instruction received:** the owner's "Illinois 2026 State of the Race" order (establish the production system; initialize Illinois; run Story Scout; return the editorial handoff). Hard limits given: no video assets, no new production architecture, no published articles, no exhaustive FEC research.

| # | Decision | Reason |
|---|---|---|
| 1 | Used `docs/illinois/` and `data/elections/IL/` as the workspace | `docs/production/` does not exist; this follows the pattern used for Florida |
| 2 | Roster transcribed from The Green Papers and cross-checked with OpenFEC and TIP; official check marked PENDING | the State Board of Elections returns HTTP 403 to automated access; nothing was guessed |
| 3 | Included write-ins and minor-party candidates in the roster and mapping | the owner's rule: all candidates appear in the race directory; only a few get features |
| 4 | Parameterized `join_tip.py` with `LLF_STATE` and optional roster fields instead of writing a new joiner | smallest change that reuses the approved Florida logic; Florida output re-checked and unchanged |
| 5 | Used a `tip_name` override for names TIP stores differently (nicknames, middle names, a corrupted character) | matching on first and last token failed for 12 people; the override is data, not code |
| 6 | Did not pull FEC data; used the already-cached UDP figure for one claim and labeled it LLF's de-duplication of FEC filings | lean standard; the owner's order |
| 7 | Ranked stories on documented news value and surprise; kept documented spending apart from described ties | the editorial standard and the AIPAC/UDP wording rule |
| 8 | Marked stories 4 and 5 NOT_READY rather than softening the AIPAC-link language | the link of each committee rests on outlets' characterizations; no primary record opened |
| 9 | Excluded two claims by marking them REMOVED: Ford's 2014 federal case and García's House floor reprimand | each rests on one report without the underlying record or a reason; either can return if sourced |
| 10 | Did not propose a governor story | lopsided race, polls with unstated or disputed sponsors, no documented development |
| 11 | Reported, did not invent, the missing "Skills Lock v2.0" and `docs/production/` | cannot reconcile what is not in the repository or Downloads |
| 12 | Built no pages, no geometry, no video assets and published nothing | the order |
| 13 | Portraits only under public-domain, CC0 and CC BY or BY-SA licenses with credit recorded; the rest are monograms marked NOT FOR PUBLICATION | the asset rights rule; 17 of the people searched have no licensed image |
| 14 | Hero: Illinois State Capitol, public domain | licensed and credited in `hero_credits.json` |

**Corrections to my own tooling during the pass:** quoted nicknames in names broke Windows file names (fixed with file-safe IDs); Wikimedia answered 503 under load (portrait fetch now retries with backoff); a transient TIP 520 made one candidate look unlinked (join and mapping now retry); an early Florida re-run showed two transient failures (confirmed not a data change).

## Files created or changed
Created: `docs/illinois/*`, `data/elections/IL/*` (roster, tip_export, candidates, mapping CSV and summary, assets CSV, portraits, extra_people, captures), `tools/elections/build_il_roster.py`, `tools/elections/build_il_mapping.py`, `static/img/elections/il-capitol.jpg`, licensed portraits under `static/img/elections/portraits/`. Changed: `tools/elections/join_tip.py`, `fetch_portraits.py`, `fetch_heroes.py`, `docs/election-build/INDEX.md`, `AGENT_RUNBOOK.md`, `.claude/skills/election-state-packet/SKILL.md` (1.0.2), `data/elections/workflow_ledger.jsonl`, `data/elections/hero_credits.json`.

## Next (owner and ChatGPT)
1. Select stories from `ILLINOIS_STORY_PROPOSALS_RANKED.md`.
2. ChatGPT writes the articles and visual designs from the briefs; claims files come back with a named independent reviewer.
3. Claude Code then implements, runs the gate and `build.py --strict`, and hands the release zip to the owner. Before pages are built: the configuration step in `ILLINOIS_PAGE_STRUCTURE.md`, geometry, and the TIP fixes.
