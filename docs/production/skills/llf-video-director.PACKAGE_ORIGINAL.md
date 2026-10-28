---
name: llf-video-director
description: Create state election video script, storyboard, per-scene image directions/assets, mostly paired Midjourney transitions, sourced real-clip suggestions and Premiere handoff. Never automatically render MP4.
---
# LLF Video Director — 2.0.0
Read `docs/production/00_READ_FIRST.md`, `01_END_TO_END_WORKFLOW.md`, `03_VIDEO_SKILL_AND_SHOT_CONTRACT.md` first. One canonical video skill entrypoint; adapt existing `llf-video-storyboard` rather than duplicating agent behavior.

Inputs: state/year; vetted article briefs and checked claims; TIP candidate and issue records; LLF brand; user/script direction. **Output ONLY**: `SCRIPT.md`, `STORYBOARD.md`, `SCENES.csv`, `ASSETS.csv`, `TRANSITIONS.csv`, `CLIP_CAPTURE.md`, `MIDJOURNEY_INSTRUCTIONS.md`, `PREMIERE_ASSEMBLY.md`, `QA.md`. Use stable IDs and asset rights. Do not export MP4 without explicit later request.

Process: develop evidence-led creative hooks; finalize script first; storyboard beats with duration determined by speech/visuals; for every beat provide bespoke visual prompt, source-backed real candidate stills, exact data overlay, transition start and end frames and MJ prompt (prefer pairs); search actual debate/event/campaign footage with URL, rights and suggested selection; specify Premiere layering. Generated art is supporting illustration, never synthetic evidence. Ensure no Florida hardcoded template/facts in future states.

QA test cases: fresh Michigan contains no Florida entities; asset-only emits no video; all scenes have a source/prompt, pair IDs valid and crop-compatible; ungraded TIP records not negative; market observations dated; external clips require rights review; independent final editorial approval stage; same script across outputs.
