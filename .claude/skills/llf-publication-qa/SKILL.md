---
name: llf-publication-qa
description: Pre-deploy and post-deploy checks for LLF election pages: strict build, link and placeholder tests, responsive screenshots, metadata, cross-links, live HTTP checks and rollback evidence. Use immediately before and after uploading a release zip.
---

# llf-publication-qa

**Version** 1.3.0 · **Owner** LLF production (Claude Code) · **Type** workflow of existing scripts. It never publishes: the owner uploads the zip.

## Before (all must pass)
1. `PYTHONUTF8=1 python3 build.py --strict` → `PUBLISHING RULES: 0 violation(s)`.
2. `python3 tests/links_test.py`, `tests/placeholders_test.py`, `tests/api_test.py` (existing); `python3 -m unittest tests/test_dark_horse.py tests/test_phase_a.py tests/test_factcheck_gate.py tests/test_workflow.py`.
3. `tools/qa/factcheck_gate.py CLAIMS.csv --article <file> --build` → `READY` (the packet is optional; finance data coverage is not checked).
4. `tools/qa/smoke.py` and `tools/qa/shots.py` (375 px and 1280 px). On Windows run with `MSYS_NO_PATHCONV=1` so a leading `/` in a path is not rewritten, and stop the local server before `build.py` (it holds `dist/`).
4a. `python3 tools/qa/freshness_check.py`: Kalshi capture under 24 hours old, and no newer poll in the feed than the one the article cites. Exit 2 means refresh and rebuild first.
4b. Open the page and the share images: `og:image` present and 1200x630, JSON-LD has `image`, the guide pages link to the new article (`Latest reporting` band).
5. Release zip from `python3 build.py --zip --keep-live-robots`; record its SHA-256 and the previous release for rollback (the prior zip stays in `release/`).

## Video (when a video pack exists)
1. `python3 tools/video/build_video_pack.py <spec.json> --check` prints `spec valid` (every number spoken or shown is in the fact sheet; no placeholders).
2. Run `python3 tools/qa/freshness_check.py` and re-read every fact marked REFRESH in `docs/video/FLORIDA_VIDEO_FACT_SHEET.md`; change the spec and rebuild if any moved.
3. Generated plates and clips: open each at full size; reject any with text, numbers, faces, people, flags, logos or red/blue; log picks in `docs/video/generated_assets.csv` with the tool's plan and commercial-use terms.
4. Watch it three ways: muted with captions only, at phone size, and with the narration alone (does every claim hold without the picture?). Check the end card: early-voting dates, link, credits, "Narration is synthetic" and the AI-illustration line.
5. Check the music license covers this use. The owner approves the upload; record `QA_PASSED` then `PUBLISHED` in the `video:<slug>` lane.

## After
`curl -sI` each new route (expect 200), the public `status.json`, the sitemap entry, canonical and Open Graph tags, and a mobile screenshot of the live page. Record time, URL and result in the workflow ledger (`tools/workflow/transitions.py record <entity> DEPLOYED` then `VERIFIED_LIVE`).

## Rollback
Re-upload the previous release zip over the site root (the update zip changes only files it contains). Evidence: the old zip SHA-256 in the release note.

## Failure semantics
Any failed check keeps the entity at `BUILD_TESTED` and records a `blocked_reason`; nothing is "fixed forward" on the live host.

## Changelog
1.3.0 (2026-10-24) video QA section. 1.2.0 (2026-10-24) freshness check, Windows path note, OG and internal-link checks. 1.1.0 (2026-10-24) gate runs on the lean ledger; no packet or finance requirement. 1.0.0 (2026-10-23) first version, consolidating the checks used for the Round 0 deployments.
