# Minnesota 2026: decisions and history

Newest last. One entry per stage: what was done, what was decided, what is open.

## 2026-10-31: start, roster, TIP join, markets, local pages
- Read the updated protocol (08, 09, 10, CHAT_REGISTRY) and `handoff.py`; `init MN` created the ledger. New in this state: the registry stage (`build_registry.py`, `gaps.csv`) and its ledger task C3b.
- Roster: the Secretary of State finder is a form and its media-file download returned a Radware captcha. Decision: not retried; roster built from Green Papers (`tools/elections/build_mn_roster.py`), labeled not official, limitation logged.
- Party: Minnesota's Democratic party is the Democratic-Farmer-Labor Party. Decision: party code DEM, label "Democratic-Farmer-Labor"; the roster note explains DFL.
- Races: open governor (Walz out; Klobuchar DFL, Demuth R, Young Green), open Senate Class 2 (Smith retiring; Flanagan DFL, Tafoya R, Whiting L, Simonetti I, Dwire write-in) and 8 House seats. Klobuchar's Senate seat is not up until 2030.
- TIP: governor has no race entries and Klobuchar has two profiles; gap list written, script prepared, nothing written (owner approval needed).
- Kalshi: governor, Senate and all 8 House events found. MN-01 is the closest quote.
- Open: homepage tile and state hero images (image request not yet written), Story Scout, articles, the MN directory-gap line for Steven Young and Kevin Dwire.

## 2026-10-31: Story Scout, briefs and Kimi package
- Scout (standard searches, originals opened): two READY angles. MN-SEN-A (Senate: the Star Tribune/KARE 11 poll at 47% to 43% as reported by MPR News, the Democratic-party contract near 0.91, and a quiet race with about $2 million of outside spending since the primary). MN-01-A (the 1st District: more than $2.5 million of outside spending, most against Rep. Finstad, and the market near 0.40).
- Held: MN-GOV-A (governor). The Star Tribune poll original returned HTTP 429 and only an aggregator line was opened; TIP has no governor race entries yet. Retry later; the checker marks it READY because it counts the aggregator as opened, so the ledger (`not_ready`) is the authority.
- Decisions: no poll is used for MN-01 (the figures found came from campaign releases or an unchecked sponsor) and no race ratings (only campaign sites carried them). The KSTP/SurveyUSA Senate poll (45% to 42%) is not used because its original was not opened. The Republican-side spending figures from MPR ($600,000) and FOX 9 ($400,000) differ and are given as reported.
- Images: `productions/2026/MN/visuals/IMAGE_REQUEST.md` (tile, governor, Senate and MN-01 heroes) for ChatGPT, separate from the Kimi articles package.
- Package: `handoff.py build MN --lane articles --mode fresh` (listing text is the Green Papers dump, labeled not official).
- Open: owner approval of the TIP gap list; image return; fact-check; homepage tile, hero credits and `data/discovery.json` entries when articles arrive; nothing deployed.

## 2026-10-31: TIP gap fixes applied (owner approved, Klobuchar profile GOV-MN-KLOBUCHAR)
- `apply-mn-gap-fixes.mjs` (TIP repo): created needs_review profile GOV-MN-YOUNG, inserted governor entries for Klobuchar, Demuth and Young at `review`, cleared incumbent_name on 2026-GOV-MN, 2026-S-MN and 2026-H-MN-02. First run failed on the `id` column (generated); script fixed and rerun, idempotent.
- Re-exported and rejoined: 24 of 25 linked (Kevin Dwire, a write-in, stays unlinked). Registry gaps now show the governor entries as `tip_entry_review`.
- Open: promoting the governor entries to `active` is a separate owner approval.

- 2026-10-31: owner approved promotion; the three governor entries (Klobuchar, Demuth, Young) are now `active` on TIP. Rows backed up first in the TIP repo (`docs/state-packets/backups/MN-governor-entries-before-promote-2026-10-31.json`); script `promote-mn-governor-entries.mjs`. Re-exported and rejoined; registry refreshed.

## 2026-10-31: drafts and images returned, fact-check
- Kimi drafts (MN-SEN-A, MN-01-A) and ChatGPT images (s7-minnesota, mn-capitol, mn-senate, mn-01) ingested and installed. Added the Minnesota homepage tile, governor hero, hero credits, hub and story entries in `data/discovery.json` (merged around the Michigan entries another session committed).
- Converted with edits: front matter cleaned, Finstad's TIP grades added (his profile now shows four graded issues), openfile notes rewritten.
- Independent fact-check (claude-factcheck-subagent-3): Senate CLEARS_WITH_FIXES, MN-01 BLOCKED (the 'outpaced the Senate race' headline compared different periods). Fixes applied; MN-01 now says spending 'tops $2.5 million' with MPR's comparison attributed. Revised wording not re-run through the gate.
- Open: owner sign-off on the fact-check; deploy approval; governor article still held; the roster is Green Papers (unofficial); the live `data/discovery.json` has sidebar copy that was already approved.
