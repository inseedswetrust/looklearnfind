# UX refinement pass: change report

Date 2026-11-04. Local only; **nothing is committed, pushed, built into a release zip or deployed.** Builds on the approved shell (`LLF_GLOBAL_SHELL.md`). Screenshots: `docs/design/screenshots/` (1440, 1024, 390 and 320 px). Test evidence is in section 4.

## 1. What changed

| # | Request | Change |
|---|---|---|
| 1 | Preserve architecture, route-to-mode, rollback, tests, docs | All kept. `shared_nav.py`, the matrix, the `global_shell` flag (verified: shell off restores the Menu button and the old mast), the test suite (now 24 shell tests) and the docs are extended, not replaced |
| 2 | Rail is the primary navigation; simplify the mast | The mast now carries **only Search and Sign in** (`build.mast_html()`); no topic links, no Menu button. The logo lives in the rail. Search and account stay one click away on every page. The strict build and tests fail a page whose mast carries anything else |
| 3 | Premium editorial rail | Newsreader serif for Browse (23px), the italic underlined search field, the state picker, outline and recommendation titles; Arial only for small spaced caps (modes, labels). Hairline rules replace boxes and the dashboard-style selects; the current section is a yellow dot; recommendation cards are borderless; spacing opened up (30px between groups). The authentic logo and the yellow lit word are unchanged (142px) |
| 4 | Consolidate in-content outlines into the rail | The page's own `In this article` and `On this page` lists are hidden on desktop (CSS) when the rail shows the same anchors; the rail outline starts open. `toc_from_body()` builds the rail outline from the page's own list, so the anchors are identical (a test compares them). **The markup stays in the page** for mobile, print and no-CSS readers. Articles with a quick-comparison side card keep their column; others collapse to one column (uses CSS `:has()`; browsers without it keep an empty column, nothing is lost) |
| 5 | Pennsylvania Living State Hub direction | `docs/post-election-design/mockups/site/state-pa.html`: large editorial headline over a photographic-style hero, three integrated results modules overlapping the hero edge (Governor, U.S. House, How to read this), race status rows, Election Signals, Read the reporting grouped by type with an update log, What happens next, and a dark Sources & Evidence section with a source-status table. See section 3 |
| 6 | No unverified results | Every figure is a visibly marked placeholder (`0,000`, `00.0%`, `SAMPLE`); chips show states, not outcomes. No winner statement, no analytical conclusion, no signal without evidence ("Not available yet" cards). The live hub and every article are unchanged |
| 7 | Global search and cross-category navigation everywhere | In the rail on desktop and the Explore sheet on mobile, on every page, whatever the section (tested on Economy, Society, Find, Look, Pennsylvania hub and home) |
| 8 | Tested at four widths | 1440, 1024, 390 and 320 px screenshots; the render matrix still covers six widths |
| 9 | Full regression | Section 4 |

Also fixed during the pass: the placeholder in the rail search was truncated (now "Search the archive"); mockup placeholder and note classes clashed with the site's portrait `.ph` and `.src` classes (renamed `.pv`, `.srcnote`); the hub mockup's evidence table overflowed at 320 px (stacks on small screens).

## 2. Files
New: `docs/design/UX_REFINEMENT_REPORT.md`. Changed: `static/css/shell.css` (rewritten), `build.py` (`mast_html()`, `has-outline` body class, outline source), `shared_nav.py` (`toc_from_body()`, open rail outline, stricter assertion), `tools/qa/shell_check.py` (mast and outline checks, four screenshot widths), `tests/test_global_shell.py` (+4 tests, stricter assertion test), `docs/design/LLF_GLOBAL_SHELL.md` and `docs/BRAND.md` (mast, outline consolidation, typography), `docs/post-election-design/README.md` and the regenerated mockups. The live site's templates, content, data, routes and copy are not touched.

## 3. Pennsylvania Living State Hub: scope note
This is the **mockup** (`state-pa.html`), the approved-direction design artifact. I did not change the live `/elections/2026/pennsylvania/` hub: doing so would add result modules, signals and new headings to an indexed page, which is a content and SEO decision that needs your approval (and results data that does not exist). The mockup's headline "Pennsylvania: what changed and what comes next" is a proposal that stays phase-dependent; the live hub keeps "Pennsylvania: the State of the Race". The hero is the existing Harrisburg Capitol **AI illustration**, labelled as one on the page; a real licensed photograph would replace it.

## 4. Verification (all run locally on this build)
| Check | Result |
|---|---|
| `python build.py --strict` | 250 pages; 0 publishing violations; `GLOBAL SHELL: 0 violation(s)` |
| `python -m unittest discover -s tests` | **173 tests OK** (1 skipped: the Playwright test, run separately below). Before this pass 169 |
| `tests/links_test.py`, registry check, skill manifest | links ok; registry OK; manifest current |
| `tools/qa/shell_check.py` (23 page types x 6 widths) | **138 checks, 0 failures**, now also asserting the mast carries only search and account (visible on desktop) and the in-content outline is hidden beside the rail outline |
| **Routes** | URL set identical (250 pages), sitemap 231 URLs, no page added or removed |
| **Canonical URLs, titles, robots meta, JSON-LD** | **0 differences** on all 250 pages against the pre-shell baseline; `robots.txt` untouched |
| **Editorial content and source attribution** | `<main>` HTML is **identical on all 250 pages** (SHA-1 compared with the previous shell build and with the shell-off build). A test asserts the PA article still holds its source anchors, Open file, corrections and citation URLs |
| Rollback flag | `LLF_GLOBAL_SHELL=0` still builds the old layout (Menu button back) |
| Mockups | Four pages at 1440, 1024, 390 and 320 px: no horizontal overflow |

**Not tested:** screen readers, 200 and 400 percent zoom, Safari and Firefox (the `:has()` rule degrades safely), touch hardware.

## 5. Screenshots (`docs/design/screenshots/`)
`homepage-`, `pennsylvania-hub-`, `race-page-`, `article-` at `1440`, `1024`, `390`, `320` (`.png`), full-page `-1440-full.jpg` and `-390-full.jpg`; `article-390-explore-sheet.png`, `pennsylvania-hub-390-explore-sheet.png` and `article-1440-rail-scrolled.png`; and `mockups/` (`state-pa-`, `national-`, `race-`, `article-` at the four widths, plus full-page hub at 1440 and 390).

## 6. Remaining design decisions for you
1. **Apply the Living State Hub to the live Pennsylvania page?** Needs approval of the new sections and headings, a results policy and a data source (see `docs/post-election-design/`). Until then the live hub is unchanged.
2. **Hero image:** keep the labelled Capitol illustration or commission or license a real photograph.
3. **Mast on desktop:** it is now a bare 52px bar with Search and Sign in. Options: keep it, move Search into the rail only and put Sign in in the rail footer (removing the bar), or add a section title or breadcrumb to it.
4. **Look / Find / About in the mast are gone:** Look and Find are the rail modes, About is in the rail footer. If About should be more prominent, add it to Browse.
5. **Outline for pages without anchors:** state hubs and a few pages have no in-page navigation, so the rail has no outline there. Add `id`s to section headings in the hub generator if you want one.
6. **Rail recommendations** ("Along this thread", "On our radar") are still pre-election editorial picks (`sidebar.EXPIRY` 2026-11-04).
7. **The wrong-agency roster sentence** on 75 pages (`elections.py:798`) from the earlier report is still unfixed.
8. The earlier open items in `CONFLICTS_AND_FLAGS.md` (the `/elections/2026/` link, account and admin carrying the shell, retiring the legacy rail) still stand.
