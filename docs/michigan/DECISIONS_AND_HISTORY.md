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
- **Not done on purpose:** no Michigan tile on the homepage (needs `s4-michigan.jpg`); nothing deployed.
- **Duggan resolved:** he ended his independent bid on May 21, 2026 (Bridge Michigan, opened), which explains why the official listing has no independent. The governor page notes his stale Kalshi contract.
- **Story scout:** `productions/2026/MI/research/STORY_BRIEF.md` and `story_brief.json` (A1 and A2 READY; A3 and A4 NOT_READY).
- **Hero brief:** `productions/2026/visuals/MICHIGAN_HERO_BRIEF_FOR_CHATGPT.md`.

## 2026-10-28, evening: ChatGPT package, MI-A2 withdrawn, MI-A4 data pulled
- **Gap found:** the first package for ChatGPT held only a story brief and claims; a fresh ChatGPT session also needs the charter, workflow, standards, examples, visual references, return formats and a way to request data. Rebuilt as a full knowledge package by `tools/workflow/build_chatgpt_package.py MI` (authored text in `productions/2026/MI/package_src/`; the zip copies repository files so it cannot drift; scans for secrets; writes `manifest.json` with SHA-256 and the commit).
- **MI-A2 withdrawn:** the live Kalshi Senate delta already reports Marist 50 to 48 (likely), El-Sayed +7 (registered, margin 4.0) and the "69 cents is not a vote share" point. Kept in `package_src/archive/MI-A2/`.
- **Contract definitions:** Kalshi's Senate and governor contracts for Benson, James, El-Sayed and Rogers resolve on party; only Duggan's resolves on a person. The briefs say so.
- **Hero naming:** the Michigan state tile is **S4** (`s4-michigan`) to avoid the S3 homepage social card; a new MI-A1 hero brief (`mi-duggan`, five blank name stands) was added; hero briefs for ChatGPT stay short.
- **MI-A4 / MI-A3:** `fetch_fec_ie.py` now skips TIP-only candidate IDs (it returned HTTP 422 for them). Pulled Schedule E for MI-10 and MI-13 to `productions/2026/MI/research/fec_ie_MI10_MI13.json`. After `schedule_e.dedupe` the MI-10 totals are large (outside spending both for and against Hines and Bouchard, mid-July to late October) and far above FEC's by-candidate roll-up, which lags notices. Not quotable until reconciled. Michigan Advance (MI-A3 lead) returned 403; not circumvented.
- **Next for Claude:** reconcile MI-A4, write its brief and claims, build package v2; implement ChatGPT's MI-A1 when it returns; image processing; deploy only with approval.


## 2026-10-28, late: handoff protocol replaces hand-written handoffs
- **Why:** the Michigan start showed four failures: three overlapping hand-written handoff documents that drifted from the work, no record of which ChatGPT chat held what, no proof a receiving chat understood its job, and no check on what came back.
- **What:** one ledger per state (`productions/2026/MI/STATE_LEDGER.json`) is the source of truth; `tools/workflow/handoff.py` (`init`, `status`, `stamp`, `build`, `verify-readback`, `ingest`) generates the Claude kickoff and the ChatGPT packages from it, checks a READBACK from the receiving chat, and checks returned files. Protocol in `docs/production/08_HANDOFF_PROTOCOL.md`, durable rules and procedures in `09_OPERATING_PROCEDURES.md`, chat routing in `CHAT_REGISTRY.md`, template in `docs/production/templates/state/`. `CLAUDE.md` carries the session protocol. Tests: `tests/test_handoff.py` (5).
- **Removed:** `tools/workflow/build_chatgpt_package.py` and the hand-written package texts (generated now). `HANDOFF_NEW_SESSION.md` and `OPENING_PROMPT.md` are marked superseded.
- **Michigan gaps recorded in the ledger as tasks C1 to C7:** install the returned tile (S4); MI-A4 reconcile and brief; MI-A3 source; ingest and fact-check MI-A1; TIP governor promotion (needs owner); deploy (needs owner); video (blocked).

## 2026-10-28, late: C1 Michigan tile installed
- **What:** ChatGPT's web file (1800x1200, 166,637 bytes, AI illustration) installed as `static/img/elections/s4-michigan.jpg`; `hero_credits.json` entry `s4-michigan` (ai true); third state-tile added in `build.py`; `.state-tiles` grid changed from two columns to three in `static/css/home.css` so the row has no orphan (single column under 700px is unchanged).
- **Checked:** strict build 155 pages, 0 rule violations; 139 tests pass; homepage looked at in the browser at 1400px, three tiles in a row. Not checked at tablet width (700 to 1000px, three narrow tiles). Alt text was not used: tiles carry the "AI illustration" corner label like Florida and Illinois. Nothing deployed.
- **Provenance limit:** ChatGPT generated at 1536x1024 and upscaled; the Florida and Illinois reference images were not given to it, so the match to those tiles is by description.

## 2026-10-28, late: C4 MI-A1 returned, converted and checked
- **Received:** ChatGPT's article, claims and notes (`MI-A1_ARTICLES.zip`) and hero (`MI-A1-HERO.zip`); ingested to `productions/2026/MI/inbox/`. The hero was generated at 1536x1024 and upscaled; the web file is installed as `static/img/elections/mi-duggan.jpg` with an `ai` credit entry.
- **Article:** `content/learn/mike-duggan-withdrawn-candidate-kalshi-michigan.html` (Reported Feature). Strict build 156 pages, 0 rule violations; 139 tests pass.
- **Fact-check (`research/MI-A1_FACTCHECK.md`):** all prices, rules and tickets match the saved Kalshi response and the Department of State listing. Fixed: a joined and elided Duggan quote (Bridge prints two quoted sentences), the May 21 wording (Bridge says "Thursday" and is dated May 21) and an ambiguous "Duggan does not appear on that listing" (a different Duggan, Brian M., is on the listing for a state House seat). Added one sentence on 24-hour volume (317.81 contracts), which ChatGPT's package did not have. Drafting-process wording removed from the open-file box and source notes.
- **Not done:** owner sign-off on the fact-check; deploy; the three governor profiles stay unlinked until the owner approves C5. DR-1 to DR-3 open, none blocking.

## 2026-10-28, late: MI-A1 fact-check signed off
- **Owner sign-off** on `research/MI-A1_FACTCHECK.md` given in chat. Owner said do not deploy yet; nothing deployed. Publication date still to be set at deploy.
