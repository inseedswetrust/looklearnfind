# Michigan 2026: decisions and history

## 2026-10-28, stage 1: roster and TIP join
- **Official list found.** `mielections.us` did not answer and `michigan.gov/sos` returned 403 (not worked around). The Department of State "Candidate Listing Report" that TIP cites (`mi-boe.entellitrak.com`) answered a plain request, so the roster is reconciled to the official list, not just a secondary source. Capture: `data/elections/MI/captures/boe_probe.html` (text in `boe_text.txt`). Michigan pages can therefore say "official list" rather than "not official". Write-ins are not on the printed list.
- **Roster.** `tools/elections/build_mi_roster.py` writes `data/elections/MI/roster.json` (75 rows: 5 Governor, 6 Senate, 64 House; 2 write-ins from Green Papers). `tools/elections/verify_mi_official.py` compares it to the official list: party and surname agree in all 15 races. Four candidates marked DISQ on the official list are left out (Thibodeau, Wilcoxon, S. Campbell, Morton).
- **TIP export** (read-only): `node scripts/export/state-packet.mjs MI`, copied to `data/elections/MI/tip_export/`; `LLF_STATE=MI python tools/elections/join_tip.py data/elections/MI/tip_export` linked 69 of 75. The builder takes each person's TIP name from the race entry by FEC ID because the join matches on the entry name.
- **Overwritten:** `data/elections/MI/candidates.json` was Senate-only (2 people); it now holds all 75 (the old copy is in git).
- **Gaps:** see `TIP_FIX_LIST_FOR_APPROVAL.md`. Waiting on owner approval before any TIP write.
- **Open:** Green Papers lists no independent for Governor; the official list also shows only the five party candidates, so none expected.

## 2026-10-28, stage 1b: TIP gaps applied (owner approved A and B)
- Duplicate check first: surname search of all TIP candidates found none of the five new people elsewhere. Existing duplicates left alone: two Shelby N Campbell rows (MI-13, disqualified) and John James `H2MI10150` / `GOV-MI-JAMES` (merged alias).
- Applied to production: profiles GOV-MI-HUDSON, GOV-MI-BRANDENBURG, GOV-MI-CAMPBELL, HOU-MI10-NKROMO, HOU-MI13-COLEMAN (`needs_review`); 5 governor entries (`review`, using existing Benson 8055 and James 4772 profiles); Nkromo and Coleman entries linked.
- Re-exported and re-joined: 74 of 75 linked. Governor entries are `review`, so TIP's public Governor race page stays empty until they are promoted; LLF links the profiles directly.
- Open: promote the 5 governor entries to `active` (owner's call); the TIP repo files (12_missing_profiles.sql, apply-mi-gap-profiles.mjs, refreshed MI packet) are uncommitted there.

## 2026-10-28, stages 2 to 4: portraits, markets, pages, story scout, hero brief
- **Moved** the old Senate-only delta files to `data/elections/MI/senate_delta/` (candidates, portraits, finance, Kalshi D and R) and pointed `load()` in `elections.py` there, so the Kalshi El-Sayed delta report and the new state pages no longer share `candidates.json` and `portraits.json`.
- **Portraits:** `fetch_portraits.py MI` found 18 licensed images (public domain, CC0, CC BY, BY-SA); 12 had no confident Wikipedia match; everyone else shows a monogram. Credits in `data/elections/MI/portraits.json`.
- **Markets:** `LLF_STATE=MI fetch_kalshi.py` (MI added): governor and Senate events plus House contracts for 9 of 13 districts (none found for MI-03, 04, 07 and 10). The governor event still lists Mike Duggan.
- **Geometry:** Census cb_2024_us_cd119_500k, reusing the zip already in `data/elections/IL/captures/` (no new download), 13 districts.
- **Pages:** `STATES["MI"]` in `elections.py` (hub, governor, Senate, House directory, 13 districts; `--strict` 0 violations). State copy moved into per-state settings (primary date, Senate seat note, governor hero, poll notes) so no Illinois text appears on Michigan pages; the pages say the roster follows the official listing. Governor hero is the existing CC BY-SA Lansing photo (`mi-capitol`). Write-ins use party code WRI.
- **Tests:** `tests/test_michigan_pages.py` (10); 134 passing in total.
- **Not done on purpose:** no Michigan tile on the homepage (needs `s3-michigan.jpg`); nothing deployed.
- **Duggan resolved:** he ended his independent bid on May 21, 2026 (Bridge Michigan, opened), which explains why the official listing has no independent. The governor page notes his stale Kalshi contract.
- **Story scout:** `productions/2026/MI/research/STORY_BRIEF.md` and `story_brief.json` (A1 and A2 READY; A3 and A4 NOT_READY).
- **Hero brief:** `productions/2026/visuals/MICHIGAN_HERO_BRIEF_FOR_CHATGPT.md`.
