# LLF global shell (design system v1)

Canonical specification for the persistent navigation and the design tokens. Approved direction (owner, 2026-11-04): dark charcoal sidebar, the original LLF logo, a yellow active-word indicator for LOOK / LEARN / FIND, global search and cross-category navigation. Implemented on a local branch only; **not deployed**. Brand rules: `docs/BRAND.md`. Production rules still apply (`CLAUDE.md`, `docs/production/`). Change list: `IMPLEMENTATION_CHANGES.md`. Test report: `BUILD_TEST_REPORT.md`. Conflicts with the supplied package: `CONFLICTS_AND_FLAGS.md`.

## 1. Invariants (must not become optional)
1. **One shell, rendered centrally.** `build.shell()` is the only place a page is written (every call site is listed in section 4). It calls `shared_nav.render()`, so any new page of any type receives the shell with no navigation markup of its own. Do not copy shell markup into a template, a content file or a script.
2. **Exactly one shell root per page:** `<div class="llf-shell" data-llf-global-shell data-llf-nav-version="1">` containing one rail (`#llf-rail`, which is also the mobile drawer), one mobile bar (`.mobile-bar`) and the drawer backdrop. `python build.py --strict` fails on a missing or duplicated root (`shared_nav.check_pages`). Never run two rails: the legacy `sidebar.css` and `sidebar.js` load only when the rollback flag is off.
3. **Desktop (901px and up):** a fixed 236px charcoal rail that stays put on scroll. The content and the mast are offset by `--llf-rail-width`. **Mobile (900px and under):** a fixed 64px bar (logo and menu button) and a **left slide-in drawer**: the same `#llf-rail` element moves off-canvas, so desktop and mobile share one navigation source and one set of links. Nothing covers the content while the drawer is closed. Full behavior: `NAVIGATION_BEHAVIOR_SPEC.md`.
4. **The canonical logo asset is the source of truth** (`/img/logo-cream.png`, used as an alpha mask with one clip per word). The yellow word is the page's **mode**.
5. **Modes are editorial state, not sections.** The mode is supplied by the page model (`page_mode()` and an optional `mode=` argument to `shell()`), never by the active category. Matrix in section 3.
6. **The rail is the primary navigation; Browse and search are global.** The same Browse list (Politics, Economy, Society, Everyday life, Topics, Latest) and the search form appear in the rail on every page, whichever section the reader is in. **The mast repeats no topic links:** on desktop it carries only Search and Sign in (the logo moves to the rail and there is no Menu button). A state picker appears only on political and election pages and never replaces the global links.
7. **Source-first hierarchy:** modest mast, one expansive content canvas, editorial headline and hero, flat bordered modules. No permanent second column beside the content. **In-content outlines are consolidated into the rail on desktop:** the page's own `On this page` or `In this article` list is hidden by CSS when the rail shows the same anchors. The markup, anchors, citations and sources stay in the page for mobile, print and no-CSS readers.
8. **Yellow is for mode, status and navigation focus only,** never a party, a chart series or a wash, and never text on paper. Source, verification and certification states are text-first. The shell never states a result and never calls a race.
9. **No Oxford comma** in any shell or editorial copy. Provenance, dates, update logs, candidate deep links, canonical URLs and screen-reader labels are preserved.
10. **Progressive enhancement.** Every link works without JavaScript; `static/js/shell.js` adds the drawer behavior (focus trap, scroll lock, Escape, backdrop and swipe-left close, focus and scroll restoration), state picker navigation, outline tracking, the logo transition and the `/` shortcut. No tracking, no window globals.

## 2. Architecture
| Piece | File | Role |
|---|---|---|
| Shell markup | `shared_nav.py` | `render()` returns the shell HTML (and discovery data for stories); `page_mode()` is the route-to-mode matrix; `toc_from_body()` builds the rail outline from the page's own navigation; `check_pages()` is the strict-build assertion (shell root, rail, bar, sheet, search, and a mast that carries only search and account) |
| Page writer | `build.py` `shell()` | The only page writer. Calls `shared_nav.render`, loads `shell.css` first and `shell.js`, sets `<body class="has-shell" data-format="<mode>">`, keeps the mast, newsletter band and footer |
| Context data | `sidebar.py` | State registry, hub list, discovery selection (`Catalog`) and the story context block (`panel()`), reused inside the single rail |
| Tokens | `static/css/site.css` `:root` | `--llf-*` tokens; legacy names alias them |
| Shell styles | `static/css/shell.css` | Rail and drawer, slim mast, mobile bar, backdrop, recommendations, 901 to 1100px single-column rules, layout-safety rules |
| Shell script | `static/js/shell.js` | Progressive enhancement only |
| Legacy rail | `static/css/sidebar.css`, `static/js/sidebar.js`, `sidebar.render()` | Kept for the rollback flag; retire after parity sign-off |
| Rollback flag | `config.json` `"global_shell": false` or `LLF_GLOBAL_SHELL=0` | Restores the previous layout (rail on stories only) for staging comparison or rollback |
| Tests | `tests/test_global_shell.py`, `tools/qa/shell_check.py` | See section 7 |

Context block rules (`rail-context`): a story gets the state lens (all states, updates the two recommendations) and an outline; a political or election page gets a state picker that opens the chosen hub (no lens, because there is nothing to recommend against); any page with at least two `<h2 id>` headings gets an "On this page" outline; otherwise the block is empty and not rendered.

## 3. Route-to-mode matrix
First match wins (`shared_nav.MODE_ROUTES`). Verified for all 250 built pages by `test_mode_comes_from_the_route_not_the_section`.

| Route | Lit word | Notes |
|---|---|---|
| `/look/`, `/look/add/`, `/look/entry/`, `/u/` | LOOK | Ledger and public profiles |
| `/find/`, `/find/{type}/`, `/find/candidates/` | FIND | Guides, listings, candidate directory |
| `/learn/`, `/learn/{slug}/` | LEARN | Stories |
| `/elections/**` | LEARN | State of the Race reports are reported work |
| `/politics/`, `/politics/daily/**` | LEARN | The Politics landing and Daily Signal are reported work (owner decision 2026-11-05; `/economy/`, `/society/` and the other category pages stay neutral) |
| `/`, `/economy/`, `/society/`, `/everyday-life/`, `/topics/**`, `/threads/**`, `/latest/` | none | Mixed collections |
| `/search/`, `/about/**`, `/community/`, `/contact/`, `/contribute/`, `/disclosures/`, `/privacy/`, `/terms/`, `/account/`, `/admin/`, `/404.html` | none | Utility and legal |

To light a word on a page that the matrix does not cover, pass `mode="look|learn|find"` to `shell()`; do not add section logic to the shell.

## 4. Component map: every `shell()` call site (Verified)
`build.py`: stories (`render_story`), Finds, threads index and thread pages, topics index and pages, category pages, Learn index, Latest, Find hub and type pages, candidate directory and state lists, homepage, search, Ledger shells (`/look/`, `/look/add/`, `/look/entry/`, `/account/`, `/u/`, `/admin/`, `/threads/t/`), generic content pages (about, legal, contact, 404). `elections.py`: `_wrapup` (state hubs, governor, Senate, House index, districts, methods, dark-horse status) and `render_report` (political articles, which pass `rail=(slug, toc)` for the story context block). Florida's separate generator uses the same `_wrapup`, so it receives the shell with no special handling.

## 4b. Typography and hierarchy (refinement pass, 2026-11-04)
Newsreader carries what a reader chooses (Browse destinations at 23px, the search field in italic, the state picker, outline entries, recommendation titles); Arial carries small utility caps (modes, labels, mast). The rail uses hairline rules instead of boxes: the search field is underlined (not a form box), Browse items are separated by hairlines with a yellow dot on the current section, the modes sit as quiet caps with the lit word in yellow, and the state picker and outline use serif with a thin left rule (yellow for the current section). The mast is a slim 52px bar with Search and Sign in only. Recommendation cards are borderless. Deviations from the package: mast labels are 10.5px (not 9px) for legibility.

## 5. Accessibility notes
- Landmarks: skip link to `#main`; `aside` labelled "LookLearnFind navigation"; `nav` regions labelled Formats and Browse; a labelled `search` form; the drawer gets `role="dialog"` and `aria-modal="true"` only while it is open on a small screen, with a focus trap, `inert` on the page behind it, `aria-expanded` and `aria-controls` on the trigger, and focus returned to the trigger on close; closed, it is `visibility:hidden` and `inert`, so none of its links take focus.
- `aria-current="page"` marks the lit mode and the current Browse section; `aria-current="location"` marks the outline position.
- Focus rings are 3px yellow on dark surfaces. Hit targets are at least 44px high in the rail, bar and sheet.
- Contrast (WCAG ratios, computed): rail text 15.0:1, rail labels 9.9:1, yellow on charcoal 11.5:1, ink on paper 14.5:1, muted on paper 5.0:1, blue on paper 6.3:1. Yellow on paper is 1.3:1, which is why it is never used as text on paper.
- `prefers-reduced-motion` disables the logo sweep and transitions.
- Not covered by tools: screen-reader behavior, zoom to 200 percent and 400 percent, and Windows high-contrast mode. Test these by hand before a release.

## 6. Authoring a new page
1. Build it in a generator function and write it with `shell(title, desc, path, body, nav=..., ...)`. **Do nothing for navigation.**
2. Give each section heading an `id` if you want the "On this page" outline (two or more).
3. If the page is a story, add it to `data/discovery.json` (still required) and pass `rail=(slug, toc)`.
4. Run `python build.py --strict` (0 publishing violations, 0 shell violations) and `python -m unittest tests/test_global_shell.py`.
5. Pick up the page type in `tools/qa/shell_check.py` `PAGES` if it is a new archetype.

## 7. Tests and QA commands
- `python build.py --strict` prints `GLOBAL SHELL: 0 violation(s)` and fails the build otherwise.
- `python -m unittest tests/test_global_shell.py -v`: 20 tests. Every built page has exactly one shell, rail, bar, sheet and search; the Browse list is identical everywhere; the lit word matches the matrix; no second rail or legacy sidebar assets; a synthetic new page (under every option combination) receives the shell; the assertion reports missing and duplicate shells; no template or content file copies shell markup.
- `python tools/qa/shell_check.py` (Playwright; about two minutes; `--quick` for three widths; `--shots <dir>` writes screenshots): at 1440, 1280, 1024, 900, 390 and 320 px, 23 page types: exactly one rail, visible and fixed on desktop and hidden on mobile; one fixed mobile bar on mobile only; content offset by the rail; no horizontal scroll; lit word correct; search present; `/` focuses search but not while typing; Explore opens and closes; no console errors. Also runnable as a unittest with `LLF_RENDER_TESTS=1`.
- The existing suite (`python -m unittest discover -s tests`) and `tests/links_test.py` still pass.

## 8. Archetype examples and screenshots
Screenshots: `docs/design/screenshots/` (`homepage-*`, `pennsylvania-hub-*`, `race-page-*`, `article-*` at 1440, 1024, 390 and 320 px) and `docs/design/screenshots/drawer/` (closed and open drawer at 320, 390, 768 and 900 px). Post-election mockups on the new shell: `docs/post-election-design/mockups/` and `docs/design/screenshots/mockups/`. The mockups use placeholder values only and no result is shown anywhere.

## 9. Known limits
- At 901 to 1100 px the content area is 665 to 864 px wide; the layout-safety rules in `shell.css` adjust the home topic grid and the Ledger controls, and every page type passes the overflow check, but a human review at those widths is advised.
- The logo word clips (0 to 34 percent, 34 to 68 percent and 68 to 100 percent of the height) come from the existing artwork and were checked on screen at 137px and 64px; verify them again if the logo file changes.
- The contextual block on stories reuses `sidebar.panel()`; its two recommendations remain editorial (`data/discovery.json`) and still need review after the election (`sidebar.EXPIRY` is 2026-11-04).
- The yellow in the existing mast nav (`aria-current`) and in a few homepage notations is unchanged and consistent with the "mode, status and focus" rule.
