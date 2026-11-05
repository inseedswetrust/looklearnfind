---
name: llf-video-director
description: Create a state election video script, storyboard, per-scene image directions and assets, mostly paired Midjourney start/end transitions, sourced real-clip suggestions and a Premiere handoff, from checked articles. The single canonical video entry point. Never renders a video or MP4 without an explicit owner request.
---

# llf-video-director

**Version** 2.0.0 · **Owner** LLF production · **Type** skill plus `tools/video/scene_pack.py` · Installed from LLF Canonical Local Workflow & Skills Lock v2.0 (2026-10-24); the package text is kept at `docs/production/skills/llf-video-director.PACKAGE_ORIGINAL.md` and the extensions below were added at install. **One video entry point:** `llf-video-storyboard` is now a legacy alias that points here.

Read first, every time: `docs/production/00_READ_FIRST.md`, `01_END_TO_END_WORKFLOW.md`, `03_VIDEO_SKILL_AND_SHOT_CONTRACT.md`. They are the law; this file is the procedure.

## Hard rules
- **Assets, not video.** Never create or render a preview or final video or MP4 unless the owner explicitly asks for a rendered video. A request for a concept, storyboard, script, images, scene prompts or transitions is not that request. The only door is `build_video_pack.py --render-video --authorization "<owner's words>"`, which records the request and stops (no renderer ships here); the workflow lane `render:<state>-<year>` needs the same authorization.
- **Script first.** Fact-backed story → full script → owner approval (`STATUS: LOCKED` in `SCRIPT.md`, with the approver and date) → beat timings from the script → scene visuals. Scene art before a locked script fails the check. Timing follows speech and picture; there is no fixed segment length. The Florida 18 x 5-second spec is a historical example only.
- **Real people are real.** Candidates appear as authentic licensed or official stills, or real clips. Generated art is supporting illustration, never evidence, never a candidate likeness, never presented as footage.
- **Exact data is deterministic.** Names, numbers, polls, Kalshi quotes, maps, district shapes and TIP grades are overlays made in HTML, SVG or Premiere after any Midjourney animation. Midjourney is never asked for text, numbers, maps, logos or politicians' faces.
- **Rights are explicit.** Every clip has a rights status; a public URL is not permission; `CLEARED` needs a written basis. The owner chooses and captures footage unless they explicitly ask Claude to acquire a specific cleared clip.

## Procedure
1. Scaffold: `python3 tools/video/scene_pack.py init <ST> [--year 2026]` creates `productions/<year>/<ST>/` (research, articles, graphics, visuals, clips, transitions, video, qa, release, logs with append-only `WORKFLOW_LOG.md` and `DECISIONS.md`) and the pack in `video/`. The scaffold is generic (no other state's names or numbers).
2. Facts: `FACTS.csv`, one row per fact the video may state, from the checked `CLAIMS.csv` files (status VERIFIED or ATTRIBUTED only; type `poll`, `market`, `tip_grade`, `result` and so on; a market fact carries its date and `refresh=true`; a poll fact carries its field dates).
3. Hooks and script: develop evidence-led hooks, write `SCRIPT.md`, get the owner's approval, then set `STATUS: LOCKED (approved by <name> on <date>)`. `QA.md` records `ARTICLE_AUTHOR` and `FACTCHECK_REVIEWER` (different people or agents).
4. Storyboard: `STORYBOARD.md` and `SCENES.csv`. Each scene: id, start, duration (from the speech), narration, purpose, on-screen text, fact IDs, `asset_type` (`REAL_STILL`, `AI_CONCEPT_STILL`, `EXACT_DATA_GRAPHIC`, `REAL_CLIP`, `COMPOSITE`), a still prompt or a real source, deterministic overlay spec, start and end frame IDs where a transition is planned, the Midjourney direction, a suggested real clip URL with inspected in and out only if actually seen, rights status, a fallback still, approval.
5. Assets: `ASSETS.csv` (id, scene, type, creator, source URL, local path, prompt, references, version, license, capture date, sha256, factual overlay, approval, `aspect_ratio`). ChatGPT generates on-brand conceptual stills from the prompts; real stills come from `fl_assets.csv`-style rights tables (state equivalent).
6. Transitions: `TRANSITIONS.csv`, mostly paired Midjourney animations: start asset ID, end asset ID (same composition and aspect ratio), camera action, subject action, duration, prompt, reference notes, `setting_verified_date` (the interface and settings checked against Midjourney's current official documentation on production day), status. Single-image animation is fine where useful.
7. Real clips: for each scene that shows a candidate, search for authentic footage with `llf-footage-scout` (find, inspect, rights-triage, record; do not download), and list it in `CLIP_CAPTURE.md` with source URL, why it works, rights status and the fallback still.
8. Handoff: `MIDJOURNEY_INSTRUCTIONS.md` and `PREMIERE_ASSEMBLY.md` (layer order per scene: base clip or still, transition clip, deterministic overlays, captions, credits and disclosures, music, narration). **Stop. No MP4.**
9. Check: `python3 tools/video/scene_pack.py check productions/<year>/<ST>/video` (exit 2 on any problem). Record stages in the `production:<state>-<year>` lane (`VIDEO_SCRIPT_DRAFTED`, `VIDEO_SCRIPT_LOCKED`, `STORYBOARD_LOCKED`, `SHOT_PLAN_READY`, `ASSETS_READY`, `USER_MJ_PREMIERE_HANDOFF`).

## What the check refuses
Missing pack files; any video file in the pack; unfilled placeholders; a fact without a real source URL, date and VERIFIED or ATTRIBUTED status; a market fact without its date and `refresh=true`; a poll fact without field dates; scene or asset rows while the script is not locked; a locked script whose QA.md lacks an author and a different reviewer; scene timing gaps or overlaps; narration that cannot be spoken in the scene's duration; a spoken or on-screen number not in the scene's facts; an AI-still scene without a prompt, a real still without a source, a real clip without a URL, rights status and fallback, an exact graphic without fact IDs; `CLEARED` without a written license basis; a not-graded TIP fact shown as a failing grade or zero; an AI prompt that names a real person or asks for a likeness; a start/end pair missing from `TRANSITIONS.csv`; transition assets that do not exist, are identical, or differ in aspect ratio; a Midjourney prompt that asks for text, numbers, maps, logos or faces; a "ready" transition without `setting_verified_date`.

## Legacy
`tools/video/build_video_pack.py`, `init_state_spec.py` (needs `--legacy`), the Florida spec and frames, `build_visual_direction.py`, `build_florida_infographics.py` and `docs/video/` are the Florida example. They keep working and keep their tests; they refuse other states and never write a video file. Do not copy the 18 x 5 layout to a new state.

## QA test cases (all automated in `tests/test_production_lock.py`)
A fresh Michigan scaffold contains no Florida entities; the default run emits no video; every scene has a prompt or a real source; paired transitions use both IDs and a matching aspect ratio; not-graded TIP records are never negative; market observations are dated; clips carry explicit rights; the story gate does not require irrelevant finance; nothing is published or rendered without recorded authorization; fact-check reviewer independence is recorded.

## Changelog
2.0.0 (2026-10-28) installed from the Production Lock v2.0 package, with `scene_pack.py`, the production and render lanes, the no-render gate and the legacy fence. Package version 2.0.0 (2026-10-24).

## Politics Creative Lock (added 2026-11-05)
For any Politics image, cutout, cover, homepage or feature art, read `docs/politics/brand/01_POLITICS_BRAND_IDENTITY_CREATIVE_BRIEF.md` first. Real politicians appear only as real, rights-recorded photographs (never a generated likeness); every image gets a row in `docs/politics/brand/ASSET_MANIFEST.csv`; an image with unverified rights or identity stays `usage_status=pending` and unpublished. The lock never overrides source verification, this skill's rules or the global shell.
