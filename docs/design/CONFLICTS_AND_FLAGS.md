# Conflicts and flags: design system package versus existing production rules

Instruction followed: where the package conflicts with existing production rules, flag the conflict and do not override the rule. Package: `LLF_POST_ELECTION_DESIGN_SYSTEM_V1.zip` (`docs/CLAUDE_DNA_INSTALL.md`, `DECISIONS_AND_BLOCKERS.md`, templates, CSS, JS). Date 2026-11-04. Nothing here was deployed.

## A. Conflicts: the package text was not applied

| # | Package says | Existing rule | What I did |
|---|---|---|---|
| A1 | `STATE_HUB_STRUCTURE.html`: H1 "Pennsylvania 2026: The Results and What Comes Next" and "The votes tell us who won" | `CLAUDE.md`: neutral reporting, nothing stated as a result unless sourced, reviewed and authorized; no results data exists in either system (discovery audit, file 07); the earlier plan also made the heading phase-dependent | **Not applied.** Hub titles, H1s and copy are unchanged. The template was used only as a structural reference. Owner decision needed when results exist |
| A2 | Rail and sheet link to `/elections/2026/` ("All 2026 election coverage", "2026 elections") | That URL has no page and returns 403; creating the national landing page is plan Gate B and needs authorization; "no production route changes as a byproduct" | **Omitted.** The state picker links straight to the seven existing hubs. Add the link when the landing page is built and approved |
| A3 | `.nav` at 9px (8px from 901 to 1230px), rail labels 9px, and hiding `.story-aside` / `.article-aside` with a forced single-column article | Existing reading size and hit-target conventions; `docs/BRAND.md`; "no lost content" | **Not applied.** Mast nav stays 10px; rail labels are 10px. Those aside classes do not exist in the code. The in-article "In this article" outline and "On this page" boxes are content inside the canvas (the report layout's `rside`), not a shell column, so they were left in place. See flag B4 |
| A4 | Package rail markup (`llf-global-rail`, `llf-modes`, a text-only state context) | `install` doc itself: reuse "the genuine existing shared sidebar pipeline" and merge recommendations, threads and the state filter; never run two rails | **Used the existing pipeline.** The shell keeps the existing brand masks, format links, the state lens and the two editorial recommendations, and adds search and Browse. The package's simplified markup would have dropped the lens and the recommendations. Class names differ from the package (`llf-rail`, `format-nav`, `mobile-bar`, `explore-sheet`) |
| A5 | Browse labels "Politics & government", "All topics", "Latest reporting" | `data/site.json` is the navigation source; the package says preserve its architecture; `BRAND.md` names the sections | **Kept the site.json labels** (Politics, Economy, Society, Everyday life, Topics, Latest) |

## B. Flags for the owner (applied, but a decision is still open)

| # | Item | Detail |
|---|---|---|
| B1 | **Docs updated before "owner approves code".** The package says the mandatory docs update follows owner approval of the code. This request asked for it now | `CLAUDE.md`, `docs/BRAND.md`, `docs/election-build/INDEX.md`, the quickstart, `llf-election-render` (1.1.0 to 1.1.1, manifest regenerated) and the decision log were updated. All are plain edits and can be reverted with git. No lock text was rewritten |
| B2 | **Shell on every page, including `/account/` and `/admin/`** | The package lists this as needing sign-off; the instruction was "every page". Applied. Both are `noindex` and now show the rail and search |
| B3 | **Replacing the stories-only sidebar** | The old rail on 21 stories is replaced by the global shell. `static/css/sidebar.css`, `static/js/sidebar.js` and `sidebar.render()` remain behind `config.json "global_shell": false` / `LLF_GLOBAL_SHELL=0` for rollback. Retire after parity sign-off |
| B4 | **"No permanent second column"** | Satisfied for the shell. Existing election pages and articles still have an in-content side outline (`In this article`, `On this page`). The package's CSS would have removed it; I kept it because it is page content and navigation inside the canvas. Decide whether to move those outlines into the rail (rail outline already appears on pages with `<h2 id>` headings) |
| B5 | **Mast stays.** The package and the owner direction keep the top mast; on desktop it now shows only the brand navigation (the logo moves to the rail) | The rail's Browse list repeats six of the nine mast links by design. Consider removing the duplication after review |
| B6 | **Palette applied site-wide**, including the inline SVG and chart colors in `elections.py` and `build.py` (9 hex values) and about 46 literals in the CSS | Hex values only; no layout or copy change. Teal `#145b5d` is now blue `#28636c`. Charts remain neutral (no party colors) |
| B7 | **Logo word masks.** The package asked for tuning against a real screenshot | The clips (0 to 34, 34 to 68 and 68 to 100 percent of the artwork height) were checked on screen at desktop and mobile sizes and light the correct word. Word classes were renamed `w-look`, `w-learn` and `w-find` because the bare `.find` class collides with the homepage Find section |
| B8 | **Existing state-isolation tests changed.** `test_illinois_pages` and `test_michigan_pages` assert no "Florida" on Illinois and Michigan pages | The state picker names all seven states. Both tests now exclude the shell block (the page content check is unchanged) |
| B9 | **Contextual recommendations are still pre-election editorial picks.** `sidebar.EXPIRY` is 2026-11-04 (today) | Review the "Along this thread" and "On our radar" picks as part of the post-election plan. Not changed |

## C. Existing issues found while testing (not changed)

| # | Finding | Where |
|---|---|---|
| C1 | Wrong agency on race pages: "The roster comes from Green Papers because the State Board of Elections list could not be read" appears on 75 pages (Illinois 21, Minnesota 9, New York 27, Pennsylvania 18). Minnesota's list is behind a captcha (Secretary of State) and Pennsylvania's Department of State list was not found | `elections.py` `_roster_note()`, line 798. Editorial copy; needs a per-state string |
| C2 | The mobile article header was a narrow image strip beside the headline (a two-column rule out-ranked the mobile rule). This predates the shell and was reproduced with the shell off | Fixed in `static/css/elections.css` (one rule); it changes layout only |
| C3 | Consecutive footnote markers (`SOURCE 01` `SOURCE 02`) could not wrap and widened the page at 390px and below | Fixed in `shell.css` (`.fn` as inline-block) |
| C4 | The Ledger controls overflowed between 801 and 1100px and the home topic grid between 901 and 1100px; the home topic grid, topics index and search button also overflowed at 320px in the shell build (not compared with the old build at that width) | Fixed with scoped rules in `shell.css` |
| C5 | `docs/election-build/CANDIDATE_DIRECTORY_SPEC.md` still says the directory is not deployed | Documentation drift, unchanged |

## D. Not authorized and not done
Deploy, upload or publish anything; results or winner statements; the `/elections/` and `/elections/2026/` pages; hub heading or title changes; a ninth top-level nav item; editorial copy edits; changes to lock text; automated results refresh. The post-election mockups contain placeholder values only and are marked as mockups on every page.
