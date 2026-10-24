---
name: llf-publication-qa
description: Pre-deploy and post-deploy checks for LLF election pages: strict build, link and placeholder tests, responsive screenshots, metadata, cross-links, live HTTP checks and rollback evidence. Use immediately before and after uploading a release zip.
---

# llf-publication-qa

**Version** 1.1.0 · **Owner** LLF production (Claude Code) · **Type** workflow of existing scripts. It never publishes: the owner uploads the zip.

## Before (all must pass)
1. `PYTHONUTF8=1 python3 build.py --strict` → `PUBLISHING RULES: 0 violation(s)`.
2. `python3 tests/links_test.py`, `tests/placeholders_test.py`, `tests/api_test.py` (existing); `python3 -m unittest tests/test_dark_horse.py tests/test_phase_a.py tests/test_factcheck_gate.py tests/test_workflow.py`.
3. `tools/qa/factcheck_gate.py CLAIMS.csv --article <file> --build` → `READY` (the packet is optional; finance data coverage is not checked).
4. `tools/qa/smoke.py` and `tools/qa/shots.py` (375 px and 1280 px).
5. Release zip from `python3 build.py --zip --keep-live-robots`; record its SHA-256 and the previous release for rollback (the prior zip stays in `release/`).

## After
`curl -sI` each new route (expect 200), the public `status.json`, the sitemap entry, canonical and Open Graph tags, and a mobile screenshot of the live page. Record time, URL and result in the workflow ledger (`tools/workflow/transitions.py record <entity> DEPLOYED` then `VERIFIED_LIVE`).

## Rollback
Re-upload the previous release zip over the site root (the update zip changes only files it contains). Evidence: the old zip SHA-256 in the release note.

## Failure semantics
Any failed check keeps the entity at `BUILD_TESTED` and records a `blocked_reason`; nothing is "fixed forward" on the live host.

## Changelog
1.1.0 (2026-10-24) gate runs on the lean ledger; no packet or finance requirement. 1.0.0 (2026-10-23) first version, consolidating the checks used for the Round 0 deployments.
