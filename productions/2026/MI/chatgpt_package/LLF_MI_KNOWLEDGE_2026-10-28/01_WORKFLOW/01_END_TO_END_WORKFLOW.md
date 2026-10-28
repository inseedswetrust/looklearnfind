# State Workflow — one command to consistent article and video-asset production

## A. Claude local intake and research
1. Create `productions/2026/<STATE>/` with `research/`, `articles/`, `graphics/`, `video/`, `clips/`, `transitions/`, `release/`, `qa/` and `logs/`.
2. Verify 2026 Governor, U.S. Senate, House roster against official state sources, reconcile real TIP IDs, live routes and six issue names/grades. NOT GRADED is never a poor grade. Preserve complete state race board even if story spotlights some contests.
3. `llf-story-scout`: scan credible national and regional reporting, read actual original sources, find current surprising/illuminating news pegs, retain a growing proposed/approved source registry. Use poll methodology and original exchange quote timestamps where material; don't fabricate causation, prices or vote counts. No exhaustive FEC packet.
4. Hand ChatGPT short `STORY_BRIEF.md`, `CLAIMS.csv`, TIP extracts and relevant photos/link map in an accessible portable package. Include exactly the data already in TIP and identify gaps without repeatedly delegating basic research.

## B. Article writing, review and publication
5. ChatGPT applies the six approved LLF editorial article schemas and existing voice to write substantial articles, source-linked and interesting, with charts, candidate/district reference components and meaningful TIP calls-to-action.
6. Independent fact-check: reviewer other than drafter verifies each *used* claim (numbers, quotes, current candidate status, issue grades, clip/image rights), resolves/omits failures. An article without fundraising claims is not blocked by missing finance. Publish approval by owner remains required.
7. Claude reuses existing responsive LLF templates/design mockups, generates precise data graphics, sources licensed photos, implements CSS, OG/social art, and checks desktop/mobile, keyboard, citation links and freshness. Run strict build and publish only as authorized; return real URLs plus screenshots, claims report and workflow log.

## C. Video creative — ASSETS NOT VIDEO
8. Based on verified articles, ChatGPT + owner develop a high-interest narrative, specific hooks and complete **script**; verify every factual line and lock the script with approval. Do not begin motion generation before script.
9. Create storyboard: purposeful beats with natural durations; define real footage opportunities and visual requirements. A State Board gives full race scope but individual human stories and TIP's six issue records are focal storytelling material. Do not hard-code Florida's 18 scenes.
10. For every scene choose `REAL_STILL`, `AI_CONCEPT_STILL`, `EXACT_DATA_GRAPHIC`, `REAL_CLIP` or `COMPOSITE`; provide image-specific prompts, references and the actual original still assets where available. Candidate likenesses are authentic licensed/official pictures, not AI inventions.
11. Build Midjourney **image-pair transitions**: start asset ID, end asset ID, same composition/ratio, motion intention, prompt, settings researched against official current documentation, fallback single-image animation if appropriate. Names, logos, polls, Kalshi, maps and TIP ratings overlaid deterministically after MJ animation.
12. Search and identify real clips that support the narrative: candidates speaking, debates/forum footage, local events, rallies and neutral place B-roll. Supply exact discoverable source URLs, suggested subject/shot, optional inspected timecodes, rights clearance status and still fallback. Public URL does NOT grant reuse rights. User chooses/captures footage.
13. Deliver script, storyboard, artwork/stills, start/end image pairs, MJ instructions, clip capture list, asset manifest, and Premiere Pro finishing notes. **STOP here. No MP4**.

## D. Optional separately requested production
Only if user explicitly requests edited/rendered video: animate clips in Midjourney, capture footage, Premiere edit, VO/music/captions, QA and export. Never infer permission from previous video planning.

## Workflow stages
`INTAKE → SOURCE_CHECKED → ARTICLE_DRAFTED → ARTICLE_FACTCHECKED → ARTICLE_APPROVED → ARTICLE_PUBLISHED → VIDEO_SCRIPT_DRAFTED → VIDEO_SCRIPT_LOCKED → STORYBOARD_LOCKED → SHOT_PLAN_READY → ASSETS_READY → USER_MJ_PREMIERE_HANDOFF`. Separately authorized: `VIDEO_RENDER_REQUESTED → VIDEO_EDITED → VIDEO_QA → PUBLISHED`.

Append inputs, outputs, actors, skill versions, decision, failures and citations to persistent `WORKFLOW_LOG.md` and keep original rejected angles/sources in audit logs. Never silently rewrite approved skills based on a single example.
