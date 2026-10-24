---
name: llf-video-storyboard
description: Turn checked LLF election articles into a complete 90-second video pack for a state (script, fact sheet, storyboard, deterministic frames, animation timelines, plate and transition prompts for an image tool) from one validated spec file. Use after the articles are DRAFTED or later, whenever a state video is requested.
---

# llf-video-storyboard

**Version** 1.0.0 · **Owner** LLF production · **Type** skill plus scripts `tools/video/init_state_spec.py`, `tools/video/build_video_pack.py`, `tools/video/build_visual_direction.py`. Added 2026-10-24 from the Florida video. The spec file is the single source of truth: the script table, fact sheet, storyboard, prompts and frames are all generated from it, so they cannot disagree.

## When to use
After a state's Senate, House or governor articles exist with claims files. Never before: every fact in the video must already be in a checked claims file.

## Procedure (no other direction needed)
1. `python3 tools/video/init_state_spec.py <ST>` creates `data/video/<st>_2026_state_of_the_race.json` from the Florida spec. Kept as is: timing (18 segments of 5 s), frame types, animation timelines, plate prompts, transition prompts, voice and format rules. Blanked as `<fill>`: facts, narration, on-screen text, parameters.
2. Facts: for each fact the video may state, copy a row from an article's claims file into `facts` with `id`, `statement`, `numbers` (every number the video may say or show, as plain digits, millions as the number), `source`, `status` (VERIFIED or ATTRIBUTED only), `never_say` and `refresh`. Anything with a UNVERIFIED or REMOVED status is not a fact for the video.
3. Segments, in this arc (the Florida arc, reuse it): 1 hook as a question about the numbers; 2 the board of all contests; 3 to 6 the broadest contest (the House: the map, the biggest verified change, three results, the issue-grade explainer); 7 to 11 the middle contest (the governor: three measurements that disagree, each labeled with what it measures and what it does not, then one line saying none is a forecast); 12 to 17 the finale (the best verified story in the Senate race as an arc: setup, the surprising fact, the poll, the movement with its single-source label, the incumbent's own words at equal size, the peak line); 18 early voting and the end card. If the state's best story is elsewhere, keep the shape: general first, story last, civic action at the end.
   - Narration at most 15 words, spoken numbers must be in the segment's facts (use `structural` for plain counts such as "three numbers"), both candidates in any pair get the same portrait size and the same duration, no value words, no prediction.
   - One animation row per moving element, with start, duration and easing, ending inside the 5-second segment.
4. `python3 tools/video/build_video_pack.py data/video/<st>_2026_state_of_the_race.json`. It refuses (exit 2, one `PROBLEM:` line each) if: durations or the transition chain are wrong; narration exceeds the word limit; a spoken or on-screen number is not in the segment's facts; a fact has no source or a bad status; a segment has no fact; a plate prompt asks for people, faces, text, numbers, logos, flags, red or blue; a transition prompt does the same; an animation runs past its segment; disclosures or credits are missing; any `<fill>` remains. When it passes it writes the frames (`release/video/<id>/frames/segNN.png` and `_alpha.png`, `cover.png`), `storyboard.html`, `docs/video/FLORIDA_VIDEO_STORYBOARD.md`, `FLORIDA_VIDEO_FACT_SHEET.md`, `FLORIDA_VISUAL_DIRECTION_AND_PROMPTS.md`, `fl_video_prompts.csv`, `fl_video_animations.csv`, and fills the script table inside `FLORIDA_VIDEO_SCRIPT_AND_PITCH.md` (rename or copy that file's markers for another state).
5. Add the missing frame type if the state needs one: extend `frame_html` in `build_video_pack.py` and add a fixture; do not hand-draw a frame outside the pipeline.
6. Hand `fl_video_prompts.csv` (plates, transitions, extras) to the image tool; a person generates and picks. Log each in `docs/video/generated_assets.csv`.
7. QA (see `llf-publication-qa`, video section). Record `video:<slug>` lane transitions with `tools/workflow/transitions.py`: BRIEFED, SCRIPTED, STORYBOARDED, ASSETS_GENERATED, CUT, QA_PASSED, PUBLISHED.

## Two layers (never mix)
Layer 1 deterministic: every name, number, chart, map, portrait and credit, from data and licensed images. Layer 2 generated: abstract paper backdrops and the motion between segments; never a person, face, text, number, logo, flag or party color; never evidence. Disclose both generated images and synthetic narration on the end card and in the caption.

## Input and output
Input: published or drafted articles and their claims files, `candidates.json`, portraits, markets, district geometry. Output: the pack above. The validator's exit code is the gate.

## Fixtures
`tests/test_video_pack.py` (18): number parsing, a valid Florida spec, and one failing mutation for every rule above, plus the template test (a new state spec is refused until every placeholder is filled) and the video workflow lane.

## Failure semantics
Fix the spec, never the validator, unless the validator is wrong (then add a fixture first). A fact that cannot be sourced is removed from the video, not softened. A figure marked REFRESH is re-read on the day of publication and the spec changed with it.

## Changelog
1.0.0 (2026-10-24) first version, from the Florida State of the Race video.
