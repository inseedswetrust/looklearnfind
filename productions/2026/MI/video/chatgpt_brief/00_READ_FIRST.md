# Michigan "Final Five Days: Follow the Money": visual production package, round 1 (mockups first)

You are making the visuals, thumbnail, intro and voice copy for a LONG-FORM HORIZONTAL video (about 6 minutes, 1920x1080, 30 fps) and, from the same scenes, vertical versions for short cuts (1080x1920). Claude assembles everything in Remotion after the narration is recorded in ElevenLabs. Same workflow as the Florida and Ford/Koppie videos (see `10_REFERENCE_FROM_EARLIER_VIDEOS/`), with three changes: horizontal master, a vertical version of every scene, and **a mockup gate before you build any layers**.

The words are LOCKED. Do not rewrite, add, cut or reorder narration. Do not add facts. Numbers, names and dates on screen must come from `FACTS.csv` (each has a fact ID). If something you want on screen is not in FACTS.csv, leave it out and tell me.

## The two phases (the gate is mandatory)

**Phase A. Mockups only. Stop after this and wait for my approval.** Return ONE preview sheet (PNG or PDF, nothing else) containing:
1. A style frame: palette, type, card shapes, how a poll, a money chain and a quote card look. Palette and fonts from the TIP brand (`02_BRAND/`).
2. THREE thumbnail concepts for the 1280x720 horizontal thumbnail (brief in `09_THUMBNAIL_BRIEF.md`).
3. For each of the 9 scenes in `03_SCENES.md`: one HORIZONTAL key frame (16:9) and one VERTICAL key frame (9:16) showing the composition at its payoff moment, with the real text on it. Label each with its scene ID. No scene numbers burned into the picture itself.
4. A sketch of the intro: how the chosen thumbnail turns into the opening animation (3 to 5 seconds), as 3 to 4 frames.
Do not build SVG layers, manifests, voice files or covers in phase A. I pick one thumbnail concept and approve or redirect each scene mockup in my reply. Changed scenes get a replacement mockup before you move on.

**Phase B. Only after I approve the mockups in writing**, build the full layered package (spec below), as one zip, with a FILE_MANIFEST.json.

## Phase B deliverables
- **Per scene, two layouts: `H` (1920x1080) and `V` (1080x1920).** Native SVG layers with outlined text, plus an editable text table (`TEXT_SPEC.csv`: asset_id, copy, width, height, font). Separate layouts, not one cropped from the other. Safe areas: H 96 px side and 54 px top/bottom margins; V 60 px sides and 100 px top, 260 px bottom.
- **`SCENE_MANIFEST.json`**: for each scene ID and layout: layers in stacking order with exact coordinates and sizes, motion cues, and for every reveal a `cue_phrase` that appears word for word in that scene's `script` text. Timing is provisional estimates only; I measure the real audio.
- **Stable scene IDs** (`OPEN`, `POLLING`, ...). You may split a scene into beats (`POLLING_a`, `POLLING_b`) when a section has more than one idea. Cue phrases tie each beat to spoken words.
- **Motion cues** per scene (`MOTION_CUES.md`): beginning, development, payoff; what the viewer understands at each stage. Type enters on the spoken word with a short opacity and slight rise, no constant zoom, no glitches, spins, bounce or generic 3D cards. Every source stays legible. Hold the landing long enough to read.
- **Images.** Candidate and real-event photographs in `04_SOURCE_IMAGES/` are references and may be used as photographic layers with credit; never regenerate or alter a real person's face. You may cut out, grade and stylize backgrounds. Generated art is supporting illustration only and is disclosed on the end card. Do not invent a likeness of anyone, including Sean McCann and Shafina Barnett (no official footage; use the mailer image only).
- **Campaign ad clips.** `05_CLIP_REGISTER.md` lists three official 30 second campaign ads (El-Sayed, Rogers, James). You do not get the videos. Design a clip window on each relevant scene (inset or full-bleed, 3 to 5 seconds, muted, with a lower-third credit "Campaign ad, [date]") and name the aspect handling for the V layout. Claude cuts the clips.
- **Intro animation from the thumbnail**: the approved thumbnail as layered SVG (`THUMBNAIL_MASTER.svg`, background, faces or cutouts, headline, wordmark as separate layers) plus motion cues so it resolves into the first scene. Also a V intro.
- **Outro / end card** (H and V): "Our source links are below", the woven closing line, the disclosures, the S1 to S8 source list. Logo and wordmark from `02_BRAND/`, unchanged.
- **Covers.** `YT_THUMBNAIL_1280x720` (under 2 MB; this is the main one), plus `IG_REEL_COVER_1080x1920` (essentials inside the central 1080x1080) for the short cuts. Keep `_WxH` in the file names. PNG and SVG.
- **Voice:** `ELEVENLABS_READ_COPY.txt` (the approved words, paragraph breaks, two or three CAPITALIZED emphasis words per scene at most, no SSML or bracketed cues), `VOICE_DIRECTION.md` (intonation per scene: pace, where to lift, where to lower, where to pause, how to read each number, the words to spell phonetically: PAC = "pack", FEC = "F-E-C", UDP = "U-D-P", WMUK and WDIV letter by letter), and `narration_chunks.json` with one chunk per scene (file prefix, scene ID, start and end estimates). One consistent narrator, calm and plain, never sneering. The tone on the religious-attack section is measured, firm, not angry.
- **Publishing copy**: YouTube title, description (with the S1 to S8 links) and chapter list, and 2 to 3 captions for the short cuts. Neutral: no winner, no endorsement.
- **`FILE_MANIFEST.json`**: every file with size and SHA-256. Every path named in any manifest must exist in the zip. Every `cue_phrase` must appear in its scene `script`. Cover pixel sizes exact.
- A `00_START_HERE.md` in your package declaring scope (standalone) and stating which of these instructions it supersedes.

## Rules that carry over from earlier rounds
1. Keep records, money figures, polls and editorial conclusions visibly distinct. A poll shows its pollster, field dates, n and margin of error on screen for the whole beat. Allegations are attributed with the response where one exists. Do not call anything illegal that the source calls disputed.
2. No winner, no endorsement, no forecast. "Michigan voters decide November 3."
3. UDP is described only as "a super PAC that reports its spending to the FEC" (FEC committee type). No alignment label unless the script says it.
4. The mailer scene must not imply Barnett or the Green Party authorized the mailers.
5. Data-center art: label the photo "Michigan data-center opposition", not Delhi Township.
6. Do not burn scene numbers or folios into the video. Do not show a website screenshot or UI.
7. Return one complete zip per phase, nothing partial. If a file you need is missing from this package, say which one.

## What is in this package
`01_SCRIPT_LOCKED.md` (the words) · `02_BRAND/` (logo, mark, fonts, licenses) · `03_SCENES.md` (nine scenes, estimated lengths, the visuals suggested so far; yours to improve) · `04_SOURCE_IMAGES/` (six references, credits and limits in `IMAGE_INVENTORY.md`) · `05_CLIP_REGISTER.md` · `06_FACTS.csv` · `07_SOURCES.md` · `09_THUMBNAIL_BRIEF.md` · `10_REFERENCE_FROM_EARLIER_VIDEOS/` (a finished scene manifest, text spec, voice copy, voice direction and cover from the Ford/Koppie video, as format examples only; do not copy their content).
