# Mobile drawer and refinement pass: report

Date 2026-11-04. Local only: **nothing is committed, pushed, built into a release zip or deployed.** Behavior specification: `NAVIGATION_BEHAVIOR_SPEC.md`. Screenshots: `screenshots/`.

## 1. What was done, against the owner decisions

| # | Decision | Result |
|---|---|---|
| 1 | Replace the Explore sheet with a left slide-in drawer | Done. The old `<dialog>` sheet is removed. The rail element is the drawer (one navigation source). Width `min(300px, 85vw)`, charcoal token, translucent backdrop, 240ms transform, scroll lock with exact position restore, visible Close, closes on Close, outside tap, Escape and swipe-left. Menu button 44px, `aria-label="Open navigation"`, `aria-expanded`, `aria-controls`; dialog semantics and focus trap while open; focus restored; closed drawer is `visibility:hidden` and `inert`; works without JavaScript (`:target`); reduced motion respected; contents in the specified order |
| 2 | Slim desktop mast | Kept: Search and Sign in only; the strict build and tests fail anything else |
| 3 | Destinations | Look and Find stay in the mode navigation; About in the utility links; global Browse on every page; the state selector is contextual |
| 4 | Pennsylvania Living State Hub | Live hub **not** updated. Mockup now uses the approved heading "Pennsylvania 2026: What Changed and What Comes Next", the labelled Capitol AI illustration, and the earlier editorial composition (large headline on warm paper beside the image, not white type over a darkened photo). Results modules, race rows and signals remain placeholders gated behind verified data |
| 5 | Contextual outlines | Election-page generators now add stable ids to every `<h2>`; desktop outline in the rail, mobile outline in the drawer; current section highlighted; the in-content outline is hidden at all widths (markup kept) so there is no duplicate column |
| 6 | Editorial recommendations | Reviewed: all 21 registered stories are pre-election reporting and no post-election story exists, so the module is **hidden everywhere** (`data/discovery.json` `recommendations.current_ids` is empty; recorded with date and reason). Story rails now show the state picker, parent link, outline and "Go to the source" |
| 7 | Roster source wording | Corrected on 72 pages with state-specific text (Minnesota Secretary of State, behind a bot check; Pennsylvania Department of State, list not found; Illinois and New York Boards, HTTP 403). The Green Papers attribution and the "not official or complete" statement are unchanged. A Pennsylvania row was added to `DATA_ACCESS_LIMITATIONS.md`; the Minnesota, Illinois and New York rows already existed |
| 8 | National hub link | Not added (the page does not exist and returns 403) |
| 9 | Account and admin | Shell kept. Tested for interference (no overflow, no competing fixed elements); no compact variant proposed. A signed-in editor session was not available to test |
| 10 | Legacy sidebar | Retained behind `global_shell: false`; verified the flag still builds the old layout |
| 11 | 1024px layout | From 901 to 1100px headers, hero images, the article grid and the map head now stack into readable single columns (type sizes unchanged). Article headline at 1024px is two lines at full size; see `screenshots/article-1024.png` |
| 12 | QA | Section 3 |

## 2. Changed-file inventory
**New:** `tools/qa/drawer_check.py`; `docs/design/NAVIGATION_BEHAVIOR_SPEC.md`; `docs/design/DRAWER_AND_REFINEMENT_REPORT.md`; `docs/design/drawer_check_result.json`; `docs/design/QUESTIONS_FOR_REVIEW.md` (previous round); screenshots under `docs/design/screenshots/` (including `drawer/` and `admin-account/`).
**Changed (code):** `shared_nav.py` (one rail/drawer, trigger, close, backdrop, `ensure_heading_ids`, story context without recommendations, stricter assertion); `build.py` (heading ids for election pages); `elections.py` (state-specific roster wording; `id="map"` on the House index map, which the page's own list already linked to); `sidebar.py` (`recommendations_current()`, `CURRENT_IDS` filter); `static/css/shell.css` (drawer, backdrop, 44px targets, in-content outline hidden, 901 to 1100px single-column rules); `static/js/shell.js` (drawer behavior).
**Changed (data and tests):** `data/discovery.json` (recommendation review entry; version 2026-11-04.1); `tests/test_global_shell.py` (27 tests, drawer markup, hidden recommendations, section ids, mast, parity); `tests/test_illinois_pages.py` and `tests/test_michigan_pages.py` (shell block pattern); `tools/qa/shell_check.py` (drawer-aware, account and admin added, four screenshot widths).
**Changed (docs):** `LLF_GLOBAL_SHELL.md`, `docs/BRAND.md`, `CLAUDE.md`, `.claude/skills/llf-election-render/SKILL.md` and the regenerated skill manifest, `docs/production/DATA_ACCESS_LIMITATIONS.md`, `docs/post-election-design/` (README and regenerated mockups).
**Not changed:** routes, canonical URLs, titles, robots and sitemap generation, the 21 articles and their sources, results data, `.htaccess`, `static/api/`, legacy sidebar assets.

## 3. Test results
| Check | Result |
|---|---|
| `python build.py --strict` | 250 pages; 0 publishing violations; `GLOBAL SHELL: 0 violation(s)` |
| `python -m unittest discover -s tests` | **176 tests OK** (1 skipped: the Playwright test, run separately); previous 173 |
| `tests/links_test.py`, registry check, skill manifest | links ok; registry OK; manifest current |
| `tools/qa/drawer_check.py` | **606 assertions, 0 failures** (home, Pennsylvania hub, race page and article at 320, 390, 768 and 900px with the drawer and 1024px with the rail): closed state, geometry, semantics, focus trap, scroll lock and restoration, backdrop, 44px targets, content order, four closing paths, edge swipe does not open, outline link, `/` shortcut, reduced motion, 240ms transition, no JavaScript, link parity between mobile and desktop |
| `tools/qa/shell_check.py` | **150 checks, 0 failures** (25 page types at 1440, 1280, 1024, 900, 390 and 320px, now including account and admin) |
| Routes and canonical URLs | URL set identical (250 pages); sitemap 231 URLs; **0 differences** in title, canonical, robots meta and JSON-LD on all 250 pages; `robots.txt` untouched |
| Editorial content and source attribution | `<main>` HTML identical on **103 pages, including all 21 articles**. It differs on 147 election pages, and all 147 differences are fully explained by two intended changes (verified by normalizing them away and matching the previous hash): added section ids on `<h2>` headings and the corrected roster sentence on 72 pages. No citation, source block, number or editorial sentence changed |
| Rollback flag | `LLF_GLOBAL_SHELL=0` builds the legacy layout (Menu button and old rail present) |
| Mockups | six widths, no horizontal overflow |

## 4. Not tested or limited
- Real devices: touch behavior was emulated (Chromium touch with synthetic touch events); no iOS Safari, Android Chrome or physical swipe tested. Browsers other than Chromium (Edge) were not run.
- Screen readers, text zoom at 200 and 400 percent, Windows high-contrast mode.
- The CSS `:has()` rule that collapses empty article columns and the `inert` attribute need Safari 15.5+, Chrome 105+ and Firefox 121+; older browsers keep an empty column or a less strict focus trap (links still work).
- A signed-in editor session on `/admin/`.
- Performance of the drawer on low-end phones.

## 5. Outstanding exceptions and unresolved design issues
1. **Live Pennsylvania hub unchanged** (as instructed). Applying the Living State Hub needs the results policy and data source.
2. **Rail outline text on hubs** uses the generated heading text, so entries are long ("What is on the ballot in Pennsylvania, and what does the record show?"). Short labels would need hand-written outline names in the generators.
3. **Static `/data/discovery/*.json` files** (21) are still emitted although nothing reads them while recommendations are hidden; they contain pre-election suggestions. Removing them is a separate decision (they would stay on the live server until deleted).
4. **The wrong-agency sentence** is fixed on 72 pages; 21 Illinois pages still carry the Illinois hub note, which is correct.
5. **National hub link** waits for `/elections/2026/`.
6. **Account and admin**: shell kept; real-session test outstanding.
7. **Legacy rail code** remains until acceptance.
8. **Mockup rail** is generated from the built hub and re-pointed at each mockup's own sections; the mockups are static previews, not generator output.
9. **Reading layout** between 901 and 1100px was verified for the four main page types; other page types (Find, Ledger, topics) pass the overflow check but were not reviewed by eye.
