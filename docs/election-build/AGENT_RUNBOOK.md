# Agent runbook: from "do state X" to articles and a video, with no other direction

Read `CLAUDE.md` first (it points to `docs/production/`, the mandatory lock), then this file. Everything here is a command or a file; nothing depends on remembering a conversation. Version 1.0.0, 2026-10-24. Canonical map of every file: `docs/election-build/INDEX.md`.

**Stop points (a person must act):** independent fact-check of each article; owner approval before anything is uploaded or posted; generating images and clips in the image tool; any database write; any payment or key. Everything else an agent does alone.

## 0. Scope and standing rules
Governor, U.S. Senate and U.S. House only. Neutral reporting: no win probabilities, no causal claims about spending or prices, no rankings or endorsements. R1 candidate links to TIP, R2 race links, "not graded" is never zero, reported numbers are attributed and not called audited, no Oxford comma. Full list: `docs/election-build/PUBLISHING_RULES.md`. Lean standard: a finished, sourced story beats a complete dataset; FEC data is never a gate.

## 1. Set up the state (once)
1. Roster: `python3 tools/elections/fetch_<st>_roster.py` (copy `fetch_fl_roster.py`), then the TIP export (`node scripts/export/state-packet.mjs <ST>` in the TIP repo; copy into `data/elections/<ST>/tip_export/`) and `python3 tools/elections/join_tip.py data/elections/<ST>/tip_export`.
   If the official site blocks automated access (Illinois returns HTTP 403), do not guess: transcribe a secondary tracker with `tools/elections/build_il_roster.py` as the pattern (provenance in the file header), cross-check names and IDs against OpenFEC and TIP, set `isbe_verified`-style columns to PENDING, and list it as a blocker for a person to clear. Join with `LLF_STATE=<ST> python3 tools/elections/join_tip.py <tip_export_dir>`; portraits with `fetch_portraits.py <ST>` (extra people in `data/elections/<ST>/extra_people.json`, re-runs with `LLF_ONLY`).
2. Markets and polls: `python3 tools/elections/fetch_kalshi.py` (adapt the state), the daily collector (`tools/dark_horse/daily.py`), portraits (`fetch_portraits.py`), district geometry (`build_fl_geometry.py` pattern).
3. Optional reference only: `python3 tools/elections/export_packet.py` (the 14-file packet). Nothing below depends on it.
Skill: `election-state-packet`.

## 2. Find the stories (about 15 minutes per article)
Skill `llf-story-scout`. Search the proposed outlet registry (`data/elections/news_source_registry.json`), open the best articles in full, write `STORY_BRIEF.md` with 2 to 3 angles per article, run `python3 tools/story/story_brief_check.py story_brief.json --as-of <today>`. NOT_READY angles stay in the brief with the reason. Record: `python3 tools/workflow/transitions.py record story:<state>-<office> DISCOVERED --actor <you>` then SOURCE_CHECKED with links.

## 3. Write, build and check each article
Skills `llf-article-format`, `llf-election-render`, `llf-factcheck-finalize`.
1. Put source values in `data/elections/<ST>/story_data.json` (each with its source), add components and `[[v:]]` values in `elections.py` following the Florida ones, write `content/learn/<slug>.html` (`layout: report`).
2. Claims file `CLAIMS_ARTICLE_<ST>_<OFFICE>.csv` (`claim,text_location,source_url,source_date,checked_date,status`, plus `type,evidence_ref` on grade, poll, finance, market and image rows).
3. `python3 tools/qa/factcheck_gate.py <claims.csv> --article content/learn/<slug>.html --packet release/research_packet` must print READY, and `python3 build.py --strict` must print 0 violations. The article stays DRAFTED until an independent reader signs the claims (rule R5).
4. Share images: extend `tools/social/render_cards.py`; screenshots: `tools/qa/shots.py` (Windows: `MSYS_NO_PATHCONV=1`; stop any local server before `build.py`).
5. Before publishing: `python3 tools/qa/freshness_check.py`; release zip: `python3 build.py --zip --keep-live-robots`. The owner uploads.

## 4. Video: asset pack only (Production Lock v2.0; read `docs/production/03_VIDEO_SKILL_AND_SHOT_CONTRACT.md`)
Skill `llf-video-director` (the one entry point; `llf-footage-scout` is its clip-search sub-procedure). **Output is assets, never a video: no MP4 or preview without the owner's explicit request for a rendered video.**
1. `python3 tools/video/scene_pack.py init <ST>` scaffolds `productions/<year>/<ST>/` and the pack (`SCRIPT.md`, `FACTS.csv`, `STORYBOARD.md`, `SCENES.csv`, `ASSETS.csv`, `TRANSITIONS.csv`, `CLIP_CAPTURE.md`, `MIDJOURNEY_INSTRUCTIONS.md`, `PREMIERE_ASSEMBLY.md`, `DECISION_LOG.md`, `QA.md`). Generic: no other state's facts.
2. Facts from the checked articles' `CLAIMS.csv` into `FACTS.csv` (VERIFIED or ATTRIBUTED only; markets dated with `refresh=true`; polls with field dates).
3. Hooks, then the full script. The owner approves it; only then set `STATUS: LOCKED (approved by <name> on <date>)` in `SCRIPT.md`. Scene art before that fails the check. Timing follows the speech (no fixed segment length; the Florida 18 x 5 layout is a historical example).
4. Storyboard and `SCENES.csv`: per scene REAL_STILL, AI_CONCEPT_STILL, EXACT_DATA_GRAPHIC, REAL_CLIP or COMPOSITE; real people are real licensed stills or clips; exact data is a deterministic overlay.
5. `ASSETS.csv` and `TRANSITIONS.csv`: mostly paired Midjourney start/end images (same aspect ratio), `setting_verified_date` after checking Midjourney's current documentation; ChatGPT generates the conceptual stills.
6. Real clips: `llf-footage-scout` finds and rights-triages (no download by default) into `CLIP_CAPTURE.md`; the owner captures.
7. `python3 tools/video/scene_pack.py check productions/<year>/<ST>/video` must print `pack valid`; then the QA in `llf-publication-qa` (video section). **Stop at the Premiere handoff.**
Florida legacy (example only, refuses other states): `build_video_pack.py`, `build_clip_manifest.py`, `build_florida_infographics.py`, `make_video_manifest.py`.

## 5. Workflow records
Canonical lane per state: `production:<state>-<year>`: INTAKE, SOURCE_CHECKED, ARTICLE_DRAFTED, ARTICLE_FACTCHECKED, ARTICLE_APPROVED, ARTICLE_PUBLISHED, VIDEO_SCRIPT_DRAFTED, VIDEO_SCRIPT_LOCKED, STORYBOARD_LOCKED, SHOT_PLAN_READY, ASSETS_READY, USER_MJ_PREMIERE_HANDOFF. Separately authorized lane `render:<state>-<year>`: VIDEO_RENDER_REQUESTED, VIDEO_EDITED, VIDEO_QA, PUBLISHED (can only begin with the owner's explicit request). Older lanes `story:<slug>` and `video:<slug>` stay valid for existing entries. `python3 tools/workflow/transitions.py record <entity> <STATE> --actor <you> [--input path] [--output path] [--blocked-reason text] [--reviewer name] [--authorization "<owner's words>"]`. Enforced in code: stages cannot be skipped; a failed check cannot advance; a rejection needs `--correction-id`; ARTICLE_PUBLISHED, PUBLISHED, DEPLOYED, OWNER_PUBLISH_APPROVED and VIDEO_RENDER_REQUESTED need `--authorization`; ARTICLE_FACTCHECKED and FACT_CHECKED need a `--reviewer` who is not the actor. Dashboard: `python3 tools/qa/dashboard.py`. Skill versions: `python3 tools/qa/skill_manifest.py`.

## 6. Tests to run before you say anything is done
`python3 -m unittest tests/test_dark_horse.py tests/test_phase_a.py tests/test_factcheck_gate.py tests/test_workflow.py tests/test_story_scout.py tests/test_video_pack.py tests/test_footage_pack.py tests/test_production_lock.py`, `python3 tools/qa/skill_manifest.py --check` and `python3 build.py --strict`.

## 7. When to stop and ask
A claim you cannot source; a fact that changed after the claims were checked; a plate or clip that shows a person, text or number; a clip whose rights status is not `CLEARED`; a money, market or poll figure that needs a person to judge; anything that would publish, post, upload, write to a production database or spend money.
