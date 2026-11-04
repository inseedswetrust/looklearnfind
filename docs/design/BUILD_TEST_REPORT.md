# Build and test report: global shell and design tokens v1

Date 2026-11-04. Repository `159302a` plus uncommitted changes (nothing committed). Windows 10, Python 3.12, Playwright with Microsoft Edge. Local only: no deploy, no upload, no network writes. Rollback flag state during these runs: on (shell enabled).

## 1. Build
| Check | Result |
|---|---|
| `python build.py --strict` | **Built 250 pages.** `PUBLISHING RULES: 0 violation(s)`; `GLOBAL SHELL: 0 violation(s)`; directory gaps unchanged (5 candidates without TIP profiles, not blocking) |
| Legacy build (`LLF_GLOBAL_SHELL=0 python build.py`) | Builds 250 pages (the rollback path works) |
| Page set | 250 pages before and after; no URL added or removed |
| Title, canonical, robots meta, JSON-LD | **0 differences across all 250 pages** (compared with the audit snapshot taken before the change) |
| `sitemap.xml` | 231 URLs, unchanged; `robots.txt` untouched (the repository copy is still the pre-launch file and must not be uploaded; see `CLAUDE.md`) |
| Page `<main>` content | **Identical on all 250 pages** between the shell-on and shell-off builds (SHA-1 of each page's `<main>`). Editorial text, source blocks, footnotes, candidate links and numbers are untouched. (Both builds include the hex palette swap in inline chart colors, which is the only non-structural content-adjacent change; see `IMPLEMENTATION_CHANGES.md`) |
| `tests/links_test.py` | links ok (every internal link and asset resolves) |
| Candidate registry `build_registry.py --check` | OK |

## 2. Unit and regression tests
| Suite | Result |
|---|---|
| `python -m unittest discover -s tests` | **169 tests, OK** (1 skipped: the Playwright render test, which needs `LLF_RENDER_TESTS=1` and was run separately). Before this work: 149 tests |
| New: `tests/test_global_shell.py` | **20 tests** (19 run by default, 1 render test): one shell root, rail, bar, sheet and search on every one of the 250 pages; identical Browse list everywhere; lit word matches the route-to-mode matrix; no second rail, no legacy sidebar assets; skip link and landmarks; canonicals and noindex unchanged; a synthetic new page under six option combinations receives the shell with zero navigation markup of its own; the assertion reports missing and duplicate shells; the strict build runs the assertion; **no template, script or content file may contain shell markup** |
| Changed: `test_illinois_pages`, `test_michigan_pages` | State-isolation tests now exclude the shell block (the state picker names every state); page-content assertions unchanged |
| `tools/qa/skill_manifest.py --check` | current (12 skills; `llf-election-render` 1.1.1) |
| `LLF_RENDER_TESTS=1 python -m unittest tests.test_global_shell.RenderRegression` | OK (about 110 seconds) |

## 3. Render matrix (`python tools/qa/shell_check.py`, Playwright, Edge)
**138 page checks (23 page types x 6 widths), 0 failures.** Result file: `docs/design/shell_check_result.json`.

| Dimension | Values |
|---|---|
| Widths | 1440, 1280, 1024, 900, 390, 320 px |
| Page types | home, Politics, Economy, topics index, a topic, a thread, Latest, Learn index, a story, a sample story, Find, candidate directory, Look, Pennsylvania hub, governor page, House index, race page, Florida hub (separate generator), Florida district, search, About, legal, 404 |

Asserted at every width and page: exactly one shell root, rail, mobile bar and Explore sheet; global search present; no HTTP error and no console error (the PHP API is not served by the static test server, so `/api/` requests are ignored); no horizontal scroll; lit word equals the matrix. Desktop (901 and up): rail visible, `position: fixed`, 236px wide, unchanged position after scrolling 800px, content starts at or beyond the rail edge, mobile bar hidden. Mobile (900 and under): rail hidden, bar visible and fixed at the top after scrolling. Once per width on a story: `/` focuses the right search box, is not captured while typing, opens the Explore sheet on mobile, and Escape closes it.

Fixes made because this matrix failed (details in `IMPLEMENTATION_CHANGES.md`): footnote markers widening the page at 390 and 320px; Ledger controls at 801 to 1100px; home topic grid at 901 to 1100px and 320px; topics index and search button at 320px; the logo's FIND word hidden on the homepage (class clash with the homepage `.find` section).

## 4. Visual review (screenshots)
`docs/design/screenshots/`: desktop 1440x900 and mobile 390x844, viewport (`*.png`) and full page (`*-full.jpg`, cropped at 9,000px), for the **homepage, Pennsylvania hub, individual race page (PA-01) and standard article**. Also: the article and hub Explore sheet on mobile, the rail scrolled to its end on an article, the Pennsylvania hub at 1024px, and the five post-election mockups at both sizes in `mockups/`. Reviewed by eye: rail layout, lit word (LEARN on stories, hubs and race pages; none on the homepage), search, Browse current marker, state picker, recommendations, mobile bar and sheet.

## 5. What was not tested
- Screen readers, Windows high-contrast mode, text zoom to 200 and 400 percent, touch devices (only a mobile viewport was emulated), and browsers other than Edge/Chromium (Safari and Firefox are untested).
- The PHP backend pages (`/look/`, `/account/`, `/admin/`) were checked only as static shells; their JavaScript apps need the API.
- A hosting-side check of `.htaccess` behavior (no server rules changed).
- Print styles.
- Contrast is computed from the palette, not measured on rendered pixels over imagery.
- 1920px and wider screens, and heights under 700px (a laptop-height rule exists but was not exercised).

## 6. Commands to reproduce
```
PYTHONUTF8=1 python build.py --strict
PYTHONUTF8=1 python -m unittest discover -s tests
PYTHONUTF8=1 python tests/links_test.py
PYTHONUTF8=1 python tools/qa/shell_check.py --shots docs/design/screenshots
```
