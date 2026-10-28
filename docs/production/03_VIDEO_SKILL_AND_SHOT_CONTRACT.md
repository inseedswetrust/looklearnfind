# Asset-first video contract v2.0 — binding for all states

## Creative dependency
**Fact-backed story → full script → editorial approval → beat timings → scene visual selection → still-image prompts & still assets → start/end MJ pairs → real clip capture guidance → Premiere handoff.** Never invent footage or make the video to force-fit template frames.

## Every scene must contain
Scene ID; purpose; exact VO; 9:16 timing; on-screen text; verified fact IDs/date; asset type; image prompt with brand/style/composition/safe area (or real candidate still source/license); exact deterministic data overlay spec; **start/end frame IDs** if transition is planned; specific Midjourney direction; real video candidate/source URL, inspected in/out only if known, rights status; alternative still; approval and QA fields.

## Image + transition strategy
- Prefer two images whose composition and eyeline/geography support a coherent transform. Generate the two **original images**, not simply prompts, when image generation is available and appropriate; label each start/end asset.
- Midjourney applies animation to a starting still and ideally a destination still, usually ~5 seconds as an initial test; use MJ official documentation to confirm current start/end frame interface/settings on production day. It is NOT reliable for meaningful text, poll values, issue grades, politician faces or district contours.
- Stills may stand alone when real photos or careful charts tell the story better. A few single-image camera moves are fine. No requirement to animate each beat.
- For exact data/UI, use HTML/SVG/Illustrator/Premiere overlays; capture official source screenshots when substantively necessary; dates visible.
- Real video: find actual relevant candidate interview/debate/rally/civic event footage, state why it works, source and ownership restrictions. User captures or licenses; do not pretend publication rights are secured automatically.

## Required files
`SCRIPT.md`, `FACTS.csv`, `STORYBOARD.md`, `SCENES.csv`, `ASSETS.csv`, `TRANSITIONS.csv`, `CLIP_CAPTURE.md`, `MIDJOURNEY_INSTRUCTIONS.md`, `PREMIERE_ASSEMBLY.md`, `DECISION_LOG.md`, `QA.md`. Use machine-readable IDs and versioned image files. No auto-rendered MP4.

## Prohibited/QA
- Default MP4 export, silent 90-second proof, or hard-coded Florida 18×5 storyboard: FAIL.
- AI portraits of real candidates presented as actual footage: FAIL.
- Missing copyright status or falsely claimed licensed footage: FAIL.
- Unknown grade displayed as failing grade: FAIL.
- Kalshi 83¢ presented as live, or dated poll without dates: FAIL.
- Video script not confirmed and approved before scene art: FAIL.
- Material numbers/text printed by Midjourney and presented as exact data: FAIL.
