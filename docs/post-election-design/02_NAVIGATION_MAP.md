# 02 Current-to-proposed navigation map (follow-up 2)

Responds to architecture v1 section 10 item 2. "Current" is Verified from the built site and source. "Proposed" is a mapping for ChatGPT to review, not a decision. The row-level article mapping is in `CONTENT_MAPPING.csv` (follow-up 3).

## 1. Navigation layers today

| Layer | Today | Source |
|---|---|---|
| Primary nav | Politics, Economy, Society, Everyday life, Topics, Latest, Look, Find, About, search, sign in. **No Elections item** | `data/site.json` `nav` |
| Breadcrumb, hub | Home / Politics / State of the Race / {State} (the last two unlinked on the hub) | `generic_hub()`, `state_hub()` |
| Breadcrumb, office and district pages | Home / Politics / State of the Race (linked to the hub) / Governor, U.S. Senate or U.S. House / {District} | `gov_page()`, `house_page()`, `district_page()` and generic variants |
| Breadcrumb, article | Home / Politics / {format label, unlinked} | `render_report()` line 1239 |
| Politics landing | `/politics/` card list from `content`, categories in `data/site.json` | `gen_categories()` |
| State lens and rail | State select (all states and DC) on article pages; hub and guide links per state from `data/discovery.json` | `sidebar.py`, `static/js/sidebar.js` |
| Homepage | Seven hard-coded state tiles | `gen_home()` |
| Search | One browser-side index of 451 items | `static/js/search.js` |
| Candidate links | Every candidate row and card links to TIP | R1 in `PUBLISHING_RULES.md` |

## 2. Proposed route and navigation map

| Level | Current | Proposed (architecture v1) | Change |
|---|---|---|---|
| Elections entry | `/elections/` 403 | `/elections/` year-independent entry | New page |
| Cycle | `/elections/2026/` 403 | `/elections/2026/` national landing, seven covered states | New page; must not list `dark-horse` as a state; link `/elections/2026/dark-horse/status/` |
| State | `/elections/2026/{state}/` "State of the Race" | Same URL, living **State Election Report** | Same URL; layout and heading change |
| Office | `/governor/`, `/senate/`, `/house/` | Same URLs | Add status and results rows |
| District | `/house/{n}/` | Same URLs | Add status and results rows |
| Breadcrumb | Home / Politics / State of the Race / State | Politics > Elections > 2026 > State > Office > District | **Breadcrumb label and structure change on 132 pages and their JSON-LD**; "State of the Race" also names an article format, so removing it from breadcrumbs reduces a naming collision |
| Primary nav | No Elections item | "Politics > Elections" (a nested path, not necessarily a ninth nav item) | Needs an owner decision: nav item, Politics landing card or both |
| Article | Home / Politics / {format} | Same, plus a historical-context banner and a related follow-up link | Banner mechanism, no URL change |
| Sidebar rail | Hub and guides per state | Same, with a phase label per hub | Data change in `discovery.json` |
| Homepage | Seven tiles | Tiles plus a link to `/elections/2026/` | Template change |

**Cross-site:** TIP candidate and race URLs stay as external destinations. The proposed "Go to the source" section links to official authorities and capture metadata; no LLF candidate pages are created.

## 3. The 21 political articles
Proposed grouping, from plan section 4 item 5 (`Post-election analysis`, `Campaign reporting`, `Money`, `Issues`, `Districts`). Basis: article format and the existing `discovery.json` thread. Counts: **Money 9, Campaign reporting 8, Districts 4, Post-election analysis 0, Issues 0**. No existing article fits "Post-election analysis" or "Issues", so those groups start empty; "Money" and "Campaign reporting" would hold 17 of 21.

| Group | Articles (state) |
|---|---|
| Money (9) | AIPAC and UDP money delta (MI); Florida House independent spending (FL); IL-07 Ford outside money (IL); Illinois Senate primary money (IL); MI-10 outside spending calendar (MI); MI-13 primary outside spending (MI); MN-01 outside spending (MN); NJ-12 Hamawy primary outside money (NJ); PA-01 CLF spending (PA) |
| Campaign reporting (8) | Florida governor fundraising and polling (FL); Florida Senate special poll and debate (FL); Michigan Senate delta (MI); Duggan withdrawn candidate and Kalshi (MI); MN Senate quiet campaign poll (MN); NJ Senate Booker and Murphy money and debate (NJ); NY governor polls (NY); PA governor poll and party market (PA) |
| Districts (4) | Florida House new map primaries (FL); IL-04 ballot access (IL); NJ-07 Bennett and Kean (NJ); NY-17 Conley and Lawler poll and market (NY) |
| Outside scope (3 non-political) | before-you-say-yes-to-the-estimate; what-goes-into-the-price-you-pay; what-was-tartary |

State counts: MI 5, FL 4, IL 3, NJ 3, MN 2, NY 2, PA 2. Pennsylvania, the plan's pilot candidate, has 2 articles (one Money, one Campaign reporting) and complete district routes; it has no Senate page because Pennsylvania has no 2026 Senate race.

Banner basis: all 21 are pre-election content. Six were written about a primary rather than the general election (FL new map primaries, IL-04, IL Senate primary, MI-10 calendar, MI-13, NJ-12) and may want banner text that says so; 3 mappings are flagged for editor review. Detail is in the CSV.

## 4. The 22 threads
**Finding:** threads are a separate vocabulary from the article-to-discovery system. `data/threads.json` has 22 curated threads. `data/discovery.json` has only 3 thread labels (`outside-money`, `polls-and-markets`, `districts-and-ballots`) used for sidebar selection. An article joins a curated thread through its front-matter `threads:` key. **None of the 21 political articles sets `threads:`**; only the three non-political samples do. Verified on built pages: the five politics threads list no election article (each page's only article link is the generic `/learn/`).

| Thread (category) | Today | Proposed handling (for review) |
|---|---|---|
| midterms-2026 (politics; topics politics, candidates) | no election article | Umbrella for Campaign reporting and Districts groups; related to candidate-forums |
| candidate-forums (politics; candidates) | none | Debate-led pieces: FL Senate poll and debate, NJ Senate money and debate, MN Senate quiet campaign |
| local-ballot (politics) | none | Districts group |
| public-money (politics) | none | Money group |
| following-a-promise (politics) | none | Reserved for the plan's Accountability Follow-ups; empty today |
| grocery-prices, small-shops, price-on-the-shelf, making-a-living, a-business-up-close (economy, 5) | 1 sample article on grocery-prices and small-shops | Unchanged |
| tartaria, world-fairs, shared-room, belonging-nearby, a-story-in-circulation (society, 5) | 1 sample article on tartaria and world-fairs | Unchanged |
| home-estimates, weeknight-cooking, skincare-claims, getting-moving, make-and-mend, care-in-context, second-attempt (everyday life, 7) | 1 sample article on home-estimates | Unchanged |

Total 22: politics 5, economy 5, society 5, everyday life 7. Assigning election articles to these threads means editing each article's front matter, which is a content change that follows the corrections and authorization rules (file 05). The alternative is to extend the generator so a thread can list stories by discovery `thread` or by state without editing article files.

## 5. State lens, sidebar and search
- The state lens already filters by state; a hub's `discovery.json` entry can carry a `phase` string and new post-election story entries can reuse `thread` values or add one (for example `results`).
- `/search-index.json` indexes 24 stories, 22 threads, 12 topics, 4 pages, 3 finds and 386 candidates. Hub pages are **not** in the index (no `hub` item type); a living hub with new content would be unsearchable until added.
- The candidate directory at `/find/candidates/{state}/` remains a Find page; it is not part of the proposed election tree and four of its state lists are `noindex`.
