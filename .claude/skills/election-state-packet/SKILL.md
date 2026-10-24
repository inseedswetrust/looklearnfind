---
name: election-state-packet
description: Build the machine-readable research packet for one state (official roster reconciled to TIP profiles, TIP issue grades, FEC finance and outside spending, markets, polls, assets, sources, existing pages). Use when starting a new state or refreshing a state's data before research is commissioned.
---

# election-state-packet

**Version** 1.0.1 · **Owner** LLF production (Claude Code session) · **Type** skill that drives deterministic scripts. It does not write prose and does not publish.

**Status (owner reset 2026-10-24): optional infrastructure.** The packet is a supplementary reference, not a required input: an article needs only `STORY_BRIEF.md` and `CLAIMS.csv`. No article gate depends on any packet file, FEC field or finance coverage. Keep the roster, TIP export and TIP grade files current because stories use them; run the FEC steps only when a story needs a specific transaction detail.

## Scripts it runs (in order)
1. `tools/elections/fetch_<state>_roster.py` (Florida: `fetch_fl_roster.py`): official Division of Elections lists, stored with sha256.
2. TIP export (read-only), run in the TIP repo: `node scripts/export/state-packet.mjs <ST>` then copy `race_entries`, `candidates`, `issue_ratings`, `issue_definitions`, `races`, `summary`, `reconciliation` to `data/elections/<ST>/tip_export/`.
3. `tools/elections/join_tip.py data/elections/<ST>/tip_export`: joins roster to TIP; links a profile only if a live GET returns 200.
4. `fetch_fec.py`, `fetch_fec_ie.py` (needs `FEC_API_KEY`), `fetch_kalshi.py`, dark-horse VoteHub capture, `fetch_portraits.py`.
5. `tools/elections/export_packet.py [outdir]`: writes the 14 files and `manifest.json` (sha256, counts, `missing_coverage`).

## Input and output schema
Input: a state code and the upstream sources above. Output: `research_packet/` with `fl_*` files (state prefix changes), `tip_issue_definitions.csv`, `tip_grades.csv` (candidate x six issues, `profile_holding_grade`), `manifest.json`. Hand-written files (`reporting_digest`, `conflicts_and_unknowns`, `story_assignments`) come from `docs/research-packet/` and are never generated.

## Rules
Nothing is filled in: missing is null, listed in `missing_coverage`. The roster is the Division of Elections list, not TIP. A grade belongs to the profile that shows it (the federal ID); governor `GOV-<ST>-` IDs are different profiles. De-duplicate FEC Schedule E with `tools/dark_horse/schedule_e.py`. UDP and AIPAC PAC rows are flagged by committee ID only. Federal FEC and state gubernatorial finance never share a file.

## Fixtures and QA gate
`tests/test_phase_a.py` (`TestScheduleE`, `TestTipGradeProfile`). Gate: roster rows reconcile to 28 districts, six issue rows per federal candidate, `manifest.json` lists every file with a hash.

## Failure semantics
A source that errors leaves its file present, valid and empty with the blocker named in `missing_coverage` and `fl_conflicts_and_unknowns.md`. The script exits nonzero only if the roster or the TIP export is missing.

## Changelog
1.0.1 (2026-10-24) marked optional; no article gate depends on it. 1.0.0 (2026-10-23) first version, from the Florida Round 1 build.
