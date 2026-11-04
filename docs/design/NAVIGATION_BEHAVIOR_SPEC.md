# Navigation behavior specification (global shell, v1 with the mobile drawer)

Status: implemented locally, not deployed. Owner decisions of 2026-11-04 applied. Companion files: `LLF_GLOBAL_SHELL.md` (invariants and architecture), `DRAWER_AND_REFINEMENT_REPORT.md` (changes and tests). **Central rule: every public page inherits navigation from the shared generator, and mobile navigation is a first-class part of that system.**

## 1. One navigation source
`shared_nav.render()` writes one element, `<aside id="llf-rail">`, plus a mobile bar and a backdrop. On desktop that element is the fixed sidebar; at 900px and under the same element is the slide-in drawer. There is no second navigation structure, no second set of ids and no duplicated links. `shared_nav.check_pages()` (strict build) and `tests/test_global_shell.py` fail a page that has a different arrangement, a second rail, the old Explore sheet, or a mast that carries topic links.

## 2. Breakpoints
| Viewport | Behavior |
|---|---|
| 901px and up | Fixed 236px rail (`#llf-rail`); slim mast with Search and Sign in only; no menu button; no dialog semantics |
| 901 to 1100px | Same rail; the content area is 665 to 864px, so headers, hero images and article grids switch to **single columns** instead of shrinking type |
| 900px and under (320, 390, 768, 900 tested) | Persistent 64px mobile bar; rail becomes the drawer; mast hidden |

## 3. Closed state (mobile)
- Mobile bar: the authentic logo (the word for the current mode lit yellow through `body[data-format]`) and a menu button: 44x44px, three-line icon, `aria-label="Open navigation"`, `aria-controls="llf-rail"`, `aria-expanded="false"`.
- The drawer is off-screen (`translateX(-102%)`), `visibility:hidden` and `inert`: none of its links can take focus or be read by assistive technology.
- No horizontal scroll; the bar is fixed at the top and the page is padded by 64px, so the headline is never covered.

## 4. Open state
- Opens from the left. Width `min(300px, 85vw)`, background `--llf-night` (#1d1e20), 240ms `transform` transition (`cubic-bezier(.22,.7,.2,1)`). A translucent backdrop (`rgba(10,10,12,.58)`) dims the page.
- The page behind is scroll-locked (`body{position:fixed}` with the saved offset) and marked `inert`; the reader's scroll position is restored exactly on close.
- Semantics while open: `role="dialog"`, `aria-modal="true"`; trigger `aria-expanded="true"`. Focus moves to the Close button and is trapped (Tab and Shift+Tab cycle inside).
- **Contents, in this order:** (1) logo with the active word, with a visible **Close** button; (2) Look / Learn / Find; (3) global search; (4) Browse: Politics, Economy, Society, Everyday life, Topics, Latest; (5) state selector on Politics and election pages (it opens the state hub; it never replaces Browse); (6) "On this page" when section anchors exist; (7) "Along this thread" and "On our radar" only when current recommendations exist (see section 8); (8) About, Contribute, Corrections and Sign in.
- Typography, hairline dividers and yellow indicators match the desktop sidebar (serif destinations, small caps labels, yellow dot for the current section, yellow lit mode word).
- Every interactive element in the drawer is at least 44px high.

## 4a. Closing
| Action | Result |
|---|---|
| Close button | closes |
| Tap on the backdrop (outside the drawer) | closes |
| Escape | closes |
| Swipe left inside the drawer (more than 60px, mostly horizontal, under 700ms) | closes |
| Choosing an in-page link (outline, source link) | closes, then scrolls to the section |
| Viewport grows past 900px while open | closes cleanly; the rail becomes the fixed sidebar |
| Close by any route | focus returns to the menu button; scroll position restored; scroll lock and `inert` removed |
A horizontal gesture on the page never opens the drawer; the only way to open it is the button (or `/`).

## 5. Keyboard
`/` opens the drawer (small screens) and focuses search, unless the reader is typing in a field. Tab order inside the open drawer follows the content order above. Escape closes. On desktop `/` just focuses the sidebar search.

## 6. JavaScript off
The trigger is a link to `#llf-rail`; the drawer opens through `:target`, the Close button and backdrop are links to `#main`, and every destination is an ordinary link. Verified in a no-JavaScript browser context. (Only focus containment, scroll lock and gestures need JavaScript.)

## 7. Reduced motion
Under `prefers-reduced-motion: reduce` the drawer and backdrop have no transition (`transition-duration` computes to 0s) and open immediately; the logo sweep is disabled. Verified with reduced motion emulated.

## 8. Contextual blocks
- **State picker:** on `/politics/`, `/elections/**`, `/find/candidates/` and political stories.
- **Outline ("On this page"):** from the page's own section anchors. Election-page generators now add stable ids to every `<h2>` (`shared_nav.ensure_heading_ids`: text-based, at most 48 characters, unique, existing ids untouched). The in-content outline list stays in the markup but is hidden at every width when the rail or drawer shows the same anchors. The current section is highlighted (`aria-current="location"`, yellow rule) and named under the heading when the list is closed.
- **Recommendations:** reviewed 2026-11-04. `data/discovery.json` `recommendations.current_ids` is empty because every story is pre-election reporting, so the module is hidden everywhere and no pre-election piece is implied to be current. Add a story id only after it is verified as post-election and relevant; the module then reappears (state lens included).
- **Mast:** Search and Sign in only. About lives in the utility links; Look and Find are modes.

## 9. Admin and account
The shell stays on `/account/` and `/admin/`. Tested (static shells at 1440, 1024 and 390px): no horizontal scroll, no fixed or sticky page element competes with the rail, bar or drawer. Not tested: a signed-in editor session with real queue data. A compact variant is **not** proposed on this evidence; revisit if a signed-in review finds wide tables or toolbars that collide.

## 10. Rollback
`"global_shell": false` in `config.json` (or `LLF_GLOBAL_SHELL=0`) restores the legacy layout (old rail on stories, mast with Menu button). Legacy assets (`sidebar.css`, `sidebar.js`, `sidebar.render()`) are retained until acceptance testing passes. In legacy mode the recommendation filter also applies, so the old rail shows no suggestions.

## 11. Verification
`python tools/qa/drawer_check.py` (606 assertions: 4 page types at 320, 390, 768 and 900px with the drawer, 1024px with the rail, plus reduced motion, no JavaScript, duration and parity), `python tools/qa/shell_check.py` (150 checks at six widths), `tests/test_global_shell.py` (27 tests) and the full suite. Results: `BUILD_TEST_REPORT.md` and `DRAWER_AND_REFINEMENT_REPORT.md`.
