# 01 Sitemap validation and generator plan (follow-up 1)

Responds to `LLF_POST_ELECTION_ARCHITECTURE_V1.md` section 10, item 1. Evidence is the repository at `159302a`, the built `dist/` and live checks on 2026-11-04. Discovery files are in `../post-election-discovery/`. No code was changed.

## 1. Validation of the proposed sitemap

| Architecture v1 statement | Result | Detail |
|---|---|---|
| Preserve `/elections/2026/{state}/`, `governor/`, `senate/`, `house/`, `house/{district}/` | **Confirmed, with two applicability notes** | Seven hubs, 6 governor pages (none for NJ), 5 Senate pages (none for NY or PA), 7 House indexes, 121 district pages. The doc's "only where applicable" is correct and already driven by `senate=False` and `governor=False` in `STATES` |
| Add `/elections/` and `/elections/2026/` | **Confirmed missing; one more gap** | Both return 403 today. `/elections/2026/dark-horse/` also returns 403 (only `/elections/2026/dark-horse/status/` exists). The 2026 landing must list the seven states and must not treat `dark-horse` as a state |
| `/elections/2026/` is a national results landing for seven covered states | Feasible | Needs data from all seven states at once; see the global-state hazard in section 3 |
| Preserve `/learn/{slug}/` URLs | Confirmed | 21 political articles; 13 slugs end in "october-2026" and keep their URLs under the plan |
| TIP candidate and race URLs stay external | Confirmed | LLF links to 132 distinct TIP race URLs and 391 candidate URLs from 151 pages. No LLF candidate pages exist |
| `/states/{state}/` later | No conflict today | No LLF route starts with `/states/`. TIP has `/states/dc` on a different domain. `/find/candidates/{state}/` already exists, so a `/states/{state}/` page would be a third state-scoped tree (election hub, candidate list, state page). The plan already defers it |
| Nav: Politics > Elections > 2026 > State > Office > District | **Differs from today's breadcrumbs** | Today: Home / Politics / State of the Race / {State} on the hub, and ... / State of the Race (linked) / Governor, U.S. Senate or U.S. House / District on children, all with `BreadcrumbList` JSON-LD. The crumb label "State of the Race" is also the name of an article format. See file 02 |
| Hub title "{State}: what changed and what comes next" | **SEO and accuracy flag** | The hub's current `<title>` is "Pennsylvania 2026: State of the Race \| LookLearnFind" and its H1 "Pennsylvania: the State of the Race". Changing the H1 and title changes the page's search target. "What changed" is inaccurate until results exist, so the heading should be phase-dependent (see section 4) |
| "Canonical unchanged" | Confirmed | Canonicals are computed from the path (`build.py`, `canonical = CFG["url"] + path`) |
| "Preserve robots" | Confirmed and critical | Live robots is hosting-managed; the repository copy is `Disallow: /`. Every update zip includes four `.htaccess` files as well |

## 2. Exact generators to extend

All names are in `elections.py` unless noted. Line numbers are at revision `159302a` and will drift.

| Need | Existing function | Change |
|---|---|---|
| Two new landing pages | none (parallel to `methods_page()` line 924 and `dark_horse_status_page()` line 944) | Add `elections_index()` and `elections_2026_index()` in `elections.py` and call them from `build(api)` (line 970). Use `_wrapup()` (line 482) for the shell, `_crumbs()` and `_jsonld()` for breadcrumbs and `nav="politics"` |
| State hub living layout | `generic_hub()` (line 813, IL MI NY NJ MN PA) and `state_hub()` (line 510, FL) | Add a `phase` and `status` input to `SX` and render the nine sections from the plan. Extend both, or first fold `state_hub()` into `generic_hub()` (see Florida notes) |
| Governor and Senate pages | `gov_page()`, `senate_page()` (FL) and `generic_gov_page()` (line 864), `generic_senate_page()` (line 898) | Add a results block and a status line; keep Kalshi panels as dated historical artifacts |
| House index and district pages | `house_page()` (line 660) and `district_page(n)` (line 730) | Both branch on `SX["code"] == "FL"` (variable `fl`); add a results row and a phase banner |
| Per-state configuration | `STATES` dict (line 25), `GEOM_NOTE` (line 722), `ROSTER_NOTE` (line 770), loop tuple in `build()` (line 971) | Add `phase`, `results_source`, `results_as_of` keys. The loop tuple `("IL","MI","NY","NJ","MN","PA")` is hard-coded in `build()` and must be edited when a state is added; derive it from `STATES` |
| Race calls, results rows, status chips | none | New helper functions beside `market_card()` (line 293) and `candidate_card()` (line 309); reuse `chip()`, `portrait()`, `utc_stamp()` |
| Historical banner on an article | `render_report(s)` (line 1202) and `render_story(s)` in `build.py` (line 358) | Read a new front-matter key (for example `era: pre-general`) and prepend the banner. The banner text lives in a registry, not in each article |
| Homepage state tiles | `gen_home()` in `build.py` (line 695, hard-coded strings) | Generate from `data/discovery.json` `hubs` instead of strings |
| Sidebar and state lens | `sidebar.py` and `data/discovery.json` | Add a phase field to `hubs`; add new story entries for post-election pieces |
| Per-page `lastmod` | `shell()` in `build.py` (around line 335 appends to `SITEMAP` list) and the sitemap writer (around line 894 uses `CFG["updated"]`) | Make `SITEMAP` a map of path to date; use the article `updated` field or a content hash date; fall back to `CFG["updated"]` |
| Politics landing link to Elections | `gen_categories()` (line 556), nav from `data/site.json` | Add an Elections entry or card without adding a ninth top-level nav item unless the owner approves a nav change |
| Updated discovery validation | `sidebar.py` validates every hub and guide URL against built pages | New landing URLs must exist before they are added to `hubs` |

## 3. Florida special cases and shared-state hazards

1. **Two parallel implementations.** Florida uses `state_hub()`, `gov_page()`, `senate_page()` while six states use the `generic_*` functions. Every new section must be written twice or Florida must be migrated to the generic path first. `FL` pages differ visibly (30 contests, Senate special election, 96 candidates, finance on).
2. **`FL` is the name of the container for whichever state is loaded.** `_load_state(code)` fills the global `FL[...]` dict (roster, candidates, markets, districts, portraits, `by_race`) for any state, so "FL" in code does not mean Florida. A national landing that needs seven states cannot read `FL` at one time. It needs a read-only loader per state, or the already built `data/candidates/races.json` registry.
3. **Mutable module globals** (`SX`, `ST_URL`, `CUR`, `FL`) are set per state inside `build()`. Build order matters; `build()` calls `load()` again at the end so Florida report articles read Florida data. A new page type must not run between states without resetting these.
4. **Florida-only data and builders:** `FL/story_data.json`, `finance_fec.json`, `ie_all.json`, `result_bars()`, `trump_bars()`, `poll_unf()`, `sept_polls()`, `stats_*`, `house_cards_*`, `map_story()` and the `fl` branches in `house_page()` and `district_page()`. `finance=True` and `counties=True` only for Florida (`STATES["FL"]`); the other six set both to False. Florida district pages show each district's largest counties by area share, which has no equivalent in the other states.
5. **Hard-coded Florida district count:** `for i in range(1, 29): district_page(i)` in `build()` runs for Florida before the loop for the other states.
6. **Duplicate definitions:** `_wrapup` (lines 482 and 1400) and `values` (lines 1092 and 1381) are each defined twice; the later definition wins. Check before editing either.
7. **Geometry:** Florida district shapes come from the state's 2026 plan; the other six use the Census 119th Congress file. No result geometry change is needed, but the map note differs (`GEOM_NOTE`).
8. **Oldest data:** Florida markets are dated 2026-10-23, and Florida primary results (3 races) are literals in `story_data.json`.

## 4. Suggested page phase model (for the generator, not yet implemented)
Plan section 7 defines page phases: `pre-election historical`, `counting`, `results reported`, `certification complete`, `governing / accountability`. In `STATES` this becomes a per-state `phase` plus an optional per-race override. Heading and standfirst templates vary by phase so the hub never says "what changed" before there is anything to report. Phase changes are content changes and follow the authorization rules in file 05.

## 5. Order of work inside the generator (smallest safe first)
1. Landing pages and per-page `lastmod` (no change to existing pages).
2. Phase flag in `STATES` plus a status line on the existing hub, with the current copy kept (placeholder state for plan Gate B).
3. Historical-banner mechanism and registry.
4. Fold Florida onto the generic hub, governor and Senate functions, behind a test that compares old and new HTML for unchanged content.
5. Results components, off by default behind a per-state flag.
