# 03 Content inventory

Counts come from the repository files (`content/`, `data/`), the built `dist/` and, for TIP, the live Supabase database (read-only, 2026-11-04). The row-level version is `CONTENT_INVENTORY.csv` (90 rows: 27 content files, 7 state data bundles, 56 TIP jurisdictions). No private data is included.

**Database access:** LLF has no content database, so every LLF number below is a file count. TIP numbers are actual database counts obtained through the Supabase REST interface with read-only `select` requests. No row contents of user tables (profiles, follows, quiz answers, notifications) were read; only table names and row counts.

## 1. Pages (LLF, built output)

| Type | Count | Notes |
|---|---|---|
| Total built HTML pages | 250 | 231 in the sitemap, 19 not (16 noindex, 3 indexable shells) |
| State hubs | 7 | FL, IL, MI, NY, NJ, MN, PA |
| Governor pages | 6 | FL, IL, MI, NY, MN, PA |
| U.S. Senate pages | 5 | FL, IL, MI, NJ, MN |
| House index pages | 7 | one per state |
| Congressional district pages | 121 | FL 28, IL 17, MI 13, NY 26, NJ 12, MN 8, PA 17 |
| Articles (`/learn/{slug}/`) | 24 | 21 political, 3 sample |
| Find entries | 3 | all sample |
| Threads | 22 curated pages plus a database-driven shell | |
| Topics | 12 | |
| Candidate pages on LLF | **0** | candidates exist only as rows in the directory and as TIP links |
| Candidate directory pages | 8 | 1 national plus 7 state lists (4 noindex) |

Race pages on LLF are the 6 governor and 5 Senate pages plus the 121 district pages: **132 race pages**.

## 2. Published and draft articles
- **Published:** 24 files in `content/learn/`. Publication is the presence of the file; there is no `status`, `draft` or `published` field (Verified by search of all front matter).
- **Draft:** none in `content/`. Drafts, briefs, claims, fact-check reports and returned ChatGPT or Kimi files live under `productions/2026/<ST>/` (articles, stories, qa, inbox, handoff). That folder is the de facto draft area and is not part of the site build.
- **Held:** one article, the Minnesota governor poll piece (`MN-GOV-A`), is recorded as `not_ready` in the Minnesota ledger (original poll page not opened; no second source).

### Political articles by state (21, all dated 2026-10-23 to 2026-11-01)
| State | Count | Articles (format, words) |
|---|---|---|
| MI | 5 | AIPAC and UDP money delta (Spending, 1,067); Michigan Senate delta (Delta, 797); MI-10 outside spending calendar (Spending, 868); MI-13 primary outside spending (Spending, 856); Duggan withdrawn candidate and Kalshi (Reported Feature, 761) |
| FL | 4 | Governor fundraising and polling (Reported Feature, 835); House independent spending (Spending, 620); House new map primaries (State of the Race, 746); Senate special election poll and debate (State of the Race, 812) |
| IL | 3 | IL-04 ballot access (Reported Feature, 621); IL-07 Ford outside money (Spending, 1,045); Senate primary money (Spending, 714) |
| NJ | 3 | NJ-07 Bennett and Kean (Reported Feature, 408); NJ-12 Hamawy primary outside money (443); Senate Booker and Murphy money and debate (356) |
| MN | 2 | Senate quiet campaign poll (Reported Feature, 827); MN-01 outside spending (877) |
| NY | 2 | Governor Hochul and Blakeman polls (State of the Race, 397); NY-17 Conley and Lawler poll and market (339) |
| PA | 2 | Governor poll and party market (State of the Race, 734); PA-01 CLF spending (717) |
| national or none | 0 political | |

Every one of the 21 has an entry in `data/discovery.json` (a build requirement) and a `NewsArticle` JSON-LD block (the three sample articles have none). Each carries an Open File block, a numbered source list, `[[s:n]]` citation markers and a corrections block; 14 of the 21 have a dated entry ("First published" or a correction) and 7 have an empty block. Links to TIP candidate or race pages per article range from 0 to 8.

### Non-political content (6 files, all marked illustrative or placeholder)
`before-you-say-yes-to-the-estimate`, `what-goes-into-the-price-you-pay`, `what-was-tartary` (articles); `a-written-scope-checklist`, `talk-to-your-local-grocer`, `visit-an-old-map-room` (finds). The README states that all sample stories, finds and Ledger rows are illustrative; these are live, indexable and in the sitemap.

### Article types and categories
- **Formats** (public label in front matter): Reported Feature 7, Spending Report 6, State of the Race 6, Delta Report 1, one "Reported feature" (lowercase), plus sample labels Practical, Explained, Field guide and three blank.
- **Categories:** politics 21, economy 2, society 2, everyday-life 2 (stories and finds combined).
- **Topics** on the political articles: `politics` and `candidates`. **Threads:** no political article is assigned to a front-matter thread; relationships come from `data/discovery.json` (`thread` = outside-money, polls-and-markets or districts-and-ballots).
- **Naming inconsistency:** the label "Reported Feature" versus "Reported feature"; sample files use other labels. Slugs encode a month and year in 13 of 21 political articles ("october-2026"), which will read as stale on a living page.

## 3. Coverage by state

| State | Roster source | Candidates (registry) | With TIP page | Market events | District shapes | Last market capture | Articles | Coverage |
|---|---|---|---|---|---|---|---|---|
| FL | Official (Division of Elections) | 96 | 96 | 30 | 28 | 2026-10-23 | 4 | Substantial, oldest data |
| IL | Green Papers (state site blocked) | 54 | 54 | 19 | 17 | 2026-10-28 | 3 | Substantial, unofficial roster |
| MI | Official (Department of State) | 75 | 74 | 15 | 13 | 2026-10-28 | 5 | Substantial |
| NY | Green Papers (board returned 403) | 64 | 62 | 27 | 26 | 2026-10-30 | 2 | Moderate, short articles |
| NJ | Official (Division of Elections) | 40 | 40 | 13 | 12 | 2026-10-31 | 3 | Moderate |
| MN | Green Papers (captcha) | 25 | 24 | 10 | 8 | 2026-10-31 | 2 | Moderate; governor article held |
| PA | Green Papers (list not found) | 37 | 37 | 18 | 17 | 2026-11-01 | 2 | Moderate |
| Other 43 jurisdictions | none | none on LLF | n/a | n/a | n/a | n/a | 0 | **No LLF coverage** |

Totals: 391 registry candidates, 386 in the search index (5 have no TIP profile: Bree Taylor, Paul Mailhot, Jonathan Makeley, Eduardo Jose Castillo Nicasio, Kevin Dwire), 132 market-event feeds, 121 district shapes.

## 4. TIP database (live counts, 2026-11-04)

| Entity | Rows | Notes |
|---|---|---|
| `races` | 574 | all cycle 2026; 487 House, 51 Senate, 36 governor; 512 upcoming, 62 cancelled; 572 regular and 2 special; across 56 jurisdictions; verification status `seed` on every row |
| `race_entries` | 1,419 | 1,318 active, 99 review, 2 withdrawn; 1,308 printed and 111 write-in |
| `candidates` | 6,243 | 5,106 House, 958 Senate, 179 governor; across 56 jurisdictions |
| `candidate_issue_grades` | 2,416 | computed per candidate and issue |
| `candidate_commitment_statuses` | 25,289 | evidence behind grades |
| `key_issues` | 20 | |
| `public_interest_commitments` | 6 | the six graded issues |
| `fec_candidate_totals` | 4,016 | candidate committee totals |
| `fec_candidate_finance` | 7,972 | |
| `committees` | 7,103 | |
| `legislative_events` | 51 | roll calls and actions |
| `legislative_participation` | 10,133 | |
| `source_issue_money_signals` | 577 | AIPAC-related money signals |
| `action_parties` | 2 | |
| `profiles` | 4 | user profiles (count only) |

Candidates by verification status: seed 4,920; unset 965; handoff_roster 169; needs_review 139; merged_alias 18; official_roster_checked 16.

## 5. Tags, sources and cross-links
- **Tags:** `topics` (12 in `data/site.json`), `threads` (22 in `data/threads.json`), discovery `thread` (3).
- **Sources:** each political article has 3 to 10 numbered source rows with outlet, date, URL and a note. Sources are inline comment blocks in the HTML; there is no source table, no source IDs and no way to query "every article that cites outlet X" except by parsing files. `data/elections/source_registry.json` and `news_source_registry.json` (22 lines) list proposed outlets, with `owner_approved` false for every source.
- **Cross-links:** `data/discovery.json` stores up to two `related` articles per story with a reason. TIP links are plain hyperlinks inside body text.
- **Inbound internal links (Verified from `dist/`):** every article has 6 to 11 internal pages linking to it (lowest: the Estimate sample and the Duggan article, 6); every state hub has 34 to 54; every one of the 121 district pages has at least 5. No built election page is an orphan.

## 6. Duplicates, orphans and inconsistencies
- No duplicate article URLs or slugs were found.
- Candidate registry versus search index: 391 versus 386, explained by the 5 candidates without TIP profiles.
- TIP `races` holds 62 `cancelled` rows (for example `2026-S-PA`, `2026-H-PA-00`) and legacy rows for districts that no longer exist (for example PA-18, PA-24, PA-35, PA-36). They are marked cancelled but remain in the table. TIP candidates in the same legacy districts remain.
- TIP candidate `verification_status` is null on 965 rows.
- Two TIP tables are named `backup_20261014_candidates` (6,037 rows) and `backup_20261014_races` (574 rows) and sit in the live schema.
- Pennsylvania's three governor entries were promoted to `active` on 2026-11-01; their candidate profiles remain `needs_review`.
- State article counts are uneven (MI 5, FL 4, MN 2, NY 2, PA 2), and NY and NJ articles are short (339 to 443 words versus 600 to 1,067 elsewhere).
