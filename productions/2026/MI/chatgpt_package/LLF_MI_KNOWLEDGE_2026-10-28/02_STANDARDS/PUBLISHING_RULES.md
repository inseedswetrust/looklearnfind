# Publishing rules for LLF election content

Owner rules, 2026-10-23. They are enforced by the build (`elections.py`, run by `build.py`), not left to memory.

## R1. Every featured candidate links to their TIP profile
- A candidate is *featured* when they appear on a candidate card, in a race directory or in the prose of a story.
- On a page, the first mention of each candidate in story prose is linked to their TIP profile. Cards carry a "View on TIP" button.
- If a candidate has no TIP profile (or the TIP URL does not return 200), the page shows "No TIP record yet", links to the LLF race page instead, and the build reports an **R1 violation**.
- **The grades you show must be visible on the TIP page you link.** TIP stores grades against a specific profile. Byron Donalds has two TIP profiles: a governor profile (all six issues "Not graded") and a congressional profile (his House record, with grades). LLF now links his grades to the congressional profile and also links the governor profile, and says so on the card.

## R2. Every mentioned race links to that race
- The first mention of a race in story prose links to the race: Florida races to the LLF race page (`/elections/2026/florida/...`), other states' races to the TIP race page (`https://theissuesparty.org/races/<race_key>`).
- Every LLF race page also carries a "Follow this race on TIP" link.
- Phrases the build recognizes today: `FL-nn`, "Florida's governor race", "governor race", "Florida's Senate race", "Michigan's Senate race". Add new phrases in `RACE_PATTERNS` in `elections.py`.

## How the build enforces them
- `python build.py` prints `PUBLISHING RULES: n violation(s)` with each candidate and page.
- `python build.py --strict` exits with an error when any violation remains. **Build release zips with `--strict` once the list below is cleared.**
- Existing exceptions require a written owner waiver; there are none today.

## Current violations: none
As of 2026-10-23 all 96 qualified Florida governor, Senate and House candidates have a working TIP profile, so `python build.py --strict` passes. The count went 17, then 8, then 0 after two production data fixes to the TIP database (governor roster and one-profile merge; then the eight missing profiles). Backups of every row changed are in the TIP repo under `docs/state-packets/backups/`.

**Build release zips with `--strict` from now on.** A new state will start with violations until its candidates have TIP profiles; that is the rule working as designed.

## Checks that run today
| Check | Where |
|---|---|
| Candidate TIP URL returns 200 | `tools/elections/join_tip.py` (at data time) |
| First mention linked, no profile reported | `autolink()` in `elections.py` (build time) |
| Race mention linked | `autolink()` and `RACE_PATTERNS` |
| Race page links to TIP race page | `race_link_span()` |
| All links resolve | `tools/qa/smoke.py` |


## Added 2026-10-24 (lean reset and audit)
- **R3. Reported numbers are attributed, not audited.** A figure from a news report is written "according to <outlet>" with its period, and never described as verified by LLF. Finance data coverage is not required for any article; only a finance claim the article actually makes needs a source and period.
- **R4. Single-source comparisons say so.** A "tightened", "rose" or "fell" claim needs a same-source comparison; if the earlier figure comes from one report, the body says that.
- **R5. Independent reader.** The drafter does not fact-check their own article. An article stays at DRAFTED until a different person or agent signs the `reviewer` column of its claims file. READY from `factcheck_gate.py` is not approval.
- **R6. Share images and alt text.** Every article has an OG image set through the front-matter `og:` key, charts carry `role="img"` and a plain-language label, portraits only where licensed, and charts never use party colors.
- **R7. Freshness.** Run `tools/qa/freshness_check.py` before publishing and on Oct 31 and Nov 2; log changes in the corrections block.
- **R8. Video facts.** Every number a video says or shows must be in the fact sheet for that segment, with a source and a VERIFIED or ATTRIBUTED status; `build_video_pack.py` refuses otherwise. Facts marked REFRESH are re-read the day of posting.
- **R9. Two layers.** Names, numbers, charts, maps, portraits and credits are deterministic; generated images are abstract backdrops and transitions only, with no person, face, text, number, logo, flag or party color. Generated images and the synthetic narrator are disclosed on the end card and in the caption.
- **R10. Equal treatment on screen.** Candidates shown together get the same portrait size, the same duration and the same animation speed; the incumbent's own words get a segment of their own where the video features a challenger arc.
- **R11. No render without a request.** A video or MP4 is never created, rendered or exported unless the owner explicitly asks for a rendered video. A request for a script, storyboard, images, scene prompts or transitions is not one. Enforced by `build_video_pack.py --render-video --authorization` (records the request; no renderer ships) and the `render:` workflow lane.
- **R12. Script before scene art.** Scene images, prompts and transitions are made only after the owner approves the full script (`STATUS: LOCKED` in `SCRIPT.md`). Enforced by `tools/video/scene_pack.py check`.
- **R13. Real people are real.** Candidates appear as authentic licensed stills or real clips; generated art is illustration, never a likeness and never evidence; exact data is a deterministic overlay; every clip has an explicit rights status (`CLEARED` only with a written basis).
- **R14. Recorded authorization and independence.** Publishing, deploying and rendering stages record the owner's authorization in the workflow ledger; fact-check stages record a reviewer who is not the drafter.
- **R15. Unreadable sources are recorded, not papered over.** A source that cannot be read goes into `docs/production/DATA_ACCESS_LIMITATIONS.md`; results that depend on it are never called official or complete.

