# Agent runbook: from "do state X" to articles and a video, with no other direction

Read `CLAUDE.md` first, then this file. Everything here is a command or a file; nothing depends on remembering a conversation. Version 1.0.0, 2026-10-24. Canonical map of every file: `docs/election-build/INDEX.md`.

**Stop points (a person must act):** independent fact-check of each article; owner approval before anything is uploaded or posted; generating images and clips in the image tool; any database write; any payment or key. Everything else an agent does alone.

## 0. Scope and standing rules
Governor, U.S. Senate and U.S. House only. Neutral reporting: no win probabilities, no causal claims about spending or prices, no rankings or endorsements. R1 candidate links to TIP, R2 race links, "not graded" is never zero, reported numbers are attributed and not called audited, no Oxford comma. Full list: `docs/election-build/PUBLISHING_RULES.md`. Lean standard: a finished, sourced story beats a complete dataset; FEC data is never a gate.

## 1. Set up the state (once)
1. Roster: `python3 tools/elections/fetch_<st>_roster.py` (copy `fetch_fl_roster.py`), then the TIP export (`node scripts/export/state-packet.mjs <ST>` in the TIP repo; copy into `data/elections/<ST>/tip_export/`) and `python3 tools/elections/join_tip.py data/elections/<ST>/tip_export`.
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

## 4. Make the video pack (zero direction)
Skill `llf-video-storyboard`.
1. `python3 tools/video/init_state_spec.py <ST>` writes `data/video/<st>_2026_state_of_the_race.json` from the Florida spec: frame types, animation timelines, plate prompts, transition prompts and timing are kept; narration, on-screen text, params and facts are `<fill>`.
2. Fill the facts from the articles' claims files (status VERIFIED or ATTRIBUTED only; each with source and a "never say"), then the 18 segments (first segment general, last segment the best verified story of the race as an arc, ending on early voting). Narration at most 15 words per segment; every spoken or on-screen number must be in that segment's facts.
3. `python3 tools/video/build_video_pack.py data/video/<st>_2026_state_of_the_race.json` validates (refuses on any problem), renders 1080 x 1920 layer-1 frames (opaque and transparent), the storyboard, the fact sheet, the prompt sheets and the script table. `--check` validates only.
4. Hand `docs/video/fl_video_prompts.csv` to the image tool (a person), log picks in `docs/video/generated_assets.csv`, assemble, then the QA in `llf-publication-qa` (video section). The owner approves the end card, the market and money lines, and the ending.

## 5. Workflow records
Articles: lane `story:<slug>` (DISCOVERED, SOURCE_CHECKED, DRAFTED, FACT_CHECKED, APPROVED, PUBLISHED). Video: lane `video:<slug>` (BRIEFED, SCRIPTED, STORYBOARDED, ASSETS_GENERATED, CUT, QA_PASSED, PUBLISHED). `python3 tools/workflow/transitions.py record <entity> <STATE> --actor <you> [--input path] [--output path] [--blocked-reason text]`; gates cannot be skipped; a failed check cannot advance; a rejection needs `--correction-id`. Dashboard: `python3 tools/qa/dashboard.py`.

## 6. Tests to run before you say anything is done
`python3 -m unittest tests/test_dark_horse.py tests/test_phase_a.py tests/test_factcheck_gate.py tests/test_workflow.py tests/test_story_scout.py tests/test_video_pack.py` and `python3 build.py --strict`.

## 7. When to stop and ask
A claim you cannot source; a fact that changed after the claims were checked; a plate or clip that shows a person, text or number; a money, market or poll figure that needs a person to judge; anything that would publish, post, upload, write to a production database or spend money.
