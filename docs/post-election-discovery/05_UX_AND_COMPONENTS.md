# 05 UX and components

Method: built HTML in `dist/` read directly, the CSS and JS in `static/`, `sidebar.py`, `elections.py` and `build.py` templates, and the TIP `components/` and `app/globals.css`. No screenshots were captured. Where a visual reference exists it is named. Verified means read from built output or source.

## 1. Two separate design systems
| | LLF | TIP |
|---|---|---|
| Look | Warm paper background (`--paper #f5f2eb`), ink text (`--ink #1c1d1b`), teal (`--teal #145b5d`, dark `#0f4145`), yellow accent (`--yellow #dfca00`), dark mast `#1d1d1d` | Dark navy (`--navy #07111F`, `--slate #0F172A`), cyan accent (`#22D3EE`), amber, green, red, purple status colors |
| Type | Self-hosted Newsreader Variable serif for headlines and body (`--serif`), Arial for UI (`--sans`) | Not inspected in detail (Tailwind 4, shadcn and Base UI components, Framer Motion) |
| Implementation | Six hand-written CSS files (`site`, `home`, `elections`, `candidates`, `ledger`, `sidebar`; about 94 KB) and 15 small JS files (about 1,260 lines) | Tailwind CSS tokens in `app/globals.css`, React components in `components/` |
| Responsive | Media queries (max-width 520 to 1180 px); `min-width: 901px` splits the sidebar from the sheet | Not inspected |
| Dark mode | No `prefers-color-scheme` rules in `site.css` (Verified) | Dark by default |

Any post-election feature on LLF inherits the LLF system; features on TIP inherit TIP's. The two do not share tokens, components or templates.

## 2. LLF navigation and layout (Verified)
- **Desktop and mobile navigation.** One `<header class="mast">` with a logo, a `Menu` button (`aria-expanded`, `aria-controls="nav"`, collapses the nav at narrow widths) and a `nav` of nine links plus a search link and a sign-in link. `site.js` toggles the menu.
- **Breadcrumbs.** Present on 147 pages, emitted as visible markup and `BreadcrumbList` JSON-LD.
- **Look / Learn / Find.** These are three nav-level concepts: **Look** is the Ledger at `/look/` (saved and embedded videos), **Learn** is the story set at `/learn/`, **Find** is the guides, listings and candidate directory at `/find/`. Connection between them is by threads (`docs/NEXUS.md`), the `related` field in `data/discovery.json`, and in-page "Keep looking." blocks. There are no page-to-page "transition" components beyond links.
- **State selector.** An `Explore` sheet on article pages carries a "Your politics lens" `<select>` of all 50 states plus DC. `sidebar.js` fetches `/data/discovery/{story-id}.json` (precomputed per story) when the reader changes state. On desktop (`min-width: 901px`) the same content is a rail beside the article. The homepage has seven hard-coded state tiles instead.
- **Related content.** The rail shows the story's hub, guides and up to two `related` stories chosen from `data/discovery.json` only. Selection is deterministic at build time; priority is a commissioning control, not popularity.
- **Search.** `/search/` and `static/js/search.js` search the single `/search-index.json` file in the browser (451 items, with body text for stories). No server search.
- **Filtering and sorting.** `/find/candidates/` filters the candidate table in place (`candidates.js`); without JavaScript the full table shows. The Ledger (`ledger.js`) has category, topic, kind, platform and sort controls backed by the PHP API.

## 3. LLF election page components (`elections.py`, `elections.css`)
State hub sections (read from the Pennsylvania build): a header with a state image and an AI-illustration chip, "What is on the ballot... what does the record show?", an "All N contests, M candidates" board, "Kalshi quotes for the statewide races", "Where to read the money", a six-issue explanation, and a "Keep looking." block. Governor and Senate pages: nominee cards, a Kalshi quote panel with a "No poll is shown" or poll note, and an "Everyone else on our roster" list. District pages: "Who is on the ballot", "Outside spending in this race", markets and a "Keep looking." block. The House index carries an SVG district map built from `districts.json`.

Reusable pieces (functions in `elections.py`): candidate card with portrait or monogram, market quote block (`mk`), bar and chart figures (`result_bars`, Florida-specific), roster and source notes per state, district SVG map, "About this roster" disclosure. All content is escaped, build-time HTML. Candidate pages do not exist on LLF; a candidate row links to the TIP profile.

Images: AI illustrations disclosed with a "AI illustration" corner chip; credits in `data/elections/hero_credits.json`; heroes are 1800 x 1200 JPEGs (about 350 KB) with 3600 x 2400 masters kept in `productions/`; portraits are licensed photographs or generated monograms (`fetch_portraits.py`, 142 files in `dist/img/elections/portraits`). Charts and maps are inline SVG.

## 4. Article layout (`render_story` in `build.py`)
Hero with title, dek and image; "Explore" sheet and rail; numbered body sections with anchors; `[[s:n]]` footnote markers resolved to a Sources list; "Open file" block (question, checked, supported, other, open); dated Corrections block; "Keep looking." Reading experience is fixed, long-form and static.

## 5. TIP presentation (Verified from file names, not rendered)
Candidate hub (`app/(public)/candidates/[fec_candidate_id]/page.tsx`, 1,642 lines) with sections and components in `components/hub` (funding bar, sparkline, stock trades panel, permanent record panel, ping actions, follow button); race comparison (`components/race/RaceCompare.tsx`); D.C. beta hub (`components/states/dc`). Recent TIP commits (October 2026) added a Capitol masthead and comparison layout to race pages and an "Issues Ledger" banner on the hub.

## 6. Naming collision to resolve
"Ledger" already means three things: LLF's **Look Ledger** (a saved-video collection), TIP's **Issues Ledger** (candidate commitments and pings) and the proposed **State Election Ledger**. URLs `/look/` and the `ledger` API routes are already taken on LLF.

## 7. Implemented versus design-only
| Item | Status |
|---|---|
| Approved homepage (`reference/approved-homepage.html`, `reference/homepage/...preview.png`) | **Implemented.** The built homepage reproduces the reference's sections and adds one ("A feed you can steer") |
| Ledger v2 desktop and mobile mockups (`reference/ledger/`) | **Implemented** as `/look/` with `ledger.css` and `ledger.js`; the live ledger is empty |
| Brand and voice guide (`docs/BRAND.md`), copy decks (`docs/copy/`) | Used by the build (`data/copy.json`, `data/seo.json` are generated from the decks) |
| Candidate directory (`docs/election-build/CANDIDATE_DIRECTORY_SPEC.md`) | **Phase 1 implemented and live.** Per-candidate pages on LLF were explicitly ruled out. Phases 2 and 3 are plans |
| Sidebar rail with state lens | **Implemented and live** (commit `3ac6fc6`, 2026-10-31) |
| Favicon concepts (`assets/favicon-concepts/`) | Proposals only; the live favicon is a crop of the logo |
| "Recently developed LLF visual redesign" referred to in the brief | **Not found as a separate artifact in either repository.** The only LLF design documents are the items above. If a separate package from ChatGPT exists, it was not in the repositories audited |
| TIP hub redesign (`docs/hub-redesign/` in the TIP repo) | Partly implemented per recent commits; not audited further |
