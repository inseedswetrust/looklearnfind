# Canonical decisions / audit history
- 2026-10-24: Owner clarified deliverable is a **production-directed storyboard/script/images/transitions/capture package**, not a rendered video; default MP4 prohibited.
- 2026-10-24: **Two-image Midjourney transitions** are primary; single-image animations acceptable. Real people use real stills; deterministic graphics for exact text, maps, poll, market and six TIP grades. The user can capture footage and assemble in Premiere Pro.
- 2026-10-24: Story/script written and approved before deciding images; creative should be narratively motivated, not generated from 18 pre-existing Florida frames.
- 2026-10-24: Persistent owner-computer local Claude repository is canonical; this ZIP is transport. Claude must create actual startup references and install versioned skills and tests before calling workflow locked.
- 2026-10-24: Lean Story Scout and factcheck only the claims actually used; finance/FEC bulk data not mandatory. Six approved article formats retained; Governor/Senate/House state scope only.
- 2026-10-24: Michigan is next end-to-end test **after** installation; Florida script will be finalized in ChatGPT separately.
- 2026-10-28 (install): The Production Lock v2.0 was installed into `docs/production/` of the existing LLF repository. `llf-video-director` 2.0.0 is the single video entry point; `llf-video-storyboard` is a legacy alias (2.0.0) and `llf-footage-scout` a sub-procedure (1.1.0, no download by default, the owner captures footage).
- 2026-10-28 (install): The fixed 18 x 5-second storyboard and its builder remain only as the Florida historical example, fenced from other states; new states use `tools/video/scene_pack.py` (script-led timing, `SCENES.csv`, `ASSETS.csv`, `TRANSITIONS.csv`). The legacy builder gained `--render-video --authorization` (records the request, renders nothing) and a guard that no video file is left in its output.
- 2026-10-28 (install): Canonical workflow lanes `production:<state>-<year>` (12 stages) and `render:<state>-<year>` were added to `tools/workflow/transitions.py`; publishing, deploying and rendering stages require a recorded owner authorization and fact-check stages a reviewer other than the actor. The older `story:` and `video:` lanes stay valid for existing entries.
- 2026-10-28 (install): The Illinois discovery material was preserved exactly as returned. The State Board of Elections 403 is recorded as a specific data-access limitation (`docs/production/DATA_ACCESS_LIMITATIONS.md`, `docs/illinois/DATA_ACCESS_LIMITATIONS.md`); the roster is not claimed complete or official.
- 2026-10-28 (install): Michigan was not started, no page was published or uploaded, no video was rendered and no new research was done during the install.

## 2026-10-28 owner dispositions of the install's open issues
1. Florida video uses an older script: keep flagged as legacy; it must not overwrite the finalized creative work.
2. Midjourney settings unverified: address when producing the next video, not now.
3. Older footage downloads: preserve existing assets and rights records; not revisited during Illinois production.
4. Multiple workflow lanes: use the `production:` lane going forward.
5. Illinois official roster inaccessible: must be resolved before claiming the Illinois State of the Race directory is complete.
6. `seed_backfill.py` deletes ledger history: do not run it; preserve Illinois research and production state.

## 2026-11-04 owner design decisions: global shell
- **Approved direction (owner, in chat):** dark charcoal persistent sidebar, the original LLF logo, a yellow active-word indicator for Look / Learn / Find, global search and cross-category navigation; implement the supplied design system as the site-wide foundation; update the permanent brand and development instructions; add tests that stop a page being generated without the shell; work locally only, no deploy or publish.
- **Implemented locally** (see `docs/design/IMPLEMENTATION_CHANGES.md`): shared shell in `build.shell()`, palette tokens, mockups on the new shell, tests, instructions.
- **Package decisions that were resolved by the owner's instruction:** exact palette values (the package values were applied), shell on every page including account and admin (the instruction was "every page"), top mast kept, replacement of the stories-only sidebar by the global shell (legacy kept behind a rollback flag).
- **Not authorized and not done:** any deploy or upload, publishing results, the `/elections/` and `/elections/2026/` landing pages, changes to hub headings or titles, a ninth top-level nav item, editorial copy edits, changes to the production lock text.
- **Open for the owner:** the conflicts listed in `docs/design/CONFLICTS_AND_FLAGS.md`.

## 2026-11-04 owner decisions: mobile drawer and refinement (local, not deployed)
- **Approved:** the shared navigation and desktop direction; the slim mast (Search and Sign in only); Look and Find as modes and About in the utility links; the post-election heading direction "Pennsylvania 2026: What Changed and What Comes Next" for the Living State Hub (live hub not to be updated yet; use the labelled Capitol AI illustration; prefer the headline on warm paper beside the image); stable section ids from the generators with outlines in the rail and the drawer; roster source wording corrected with state-specific agency names; the national hub link only after `/elections/2026/` exists and passes checks; shell kept on Account (Admin to be tested); legacy sidebar retained behind the flag.
- **Required and done locally:** a left slide-in navigation drawer replacing the Explore sheet; a readable single-column layout from 901 to 1100px.
- **Recommendations review:** all 21 registered stories are pre-election, so the module is hidden (`recommendations.current_ids` empty in `data/discovery.json`).
- **Not authorized:** commit, push, publish or deploy; results, calls or analytical conclusions.
