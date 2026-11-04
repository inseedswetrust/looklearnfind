# 08 Migration and regression risks

Each risk is labeled **Verified** (evidence in code, files or the live site), **Inferred** or **Unknown**. Ratings are this audit's judgment of consequence if mishandled: High, Medium or Low. Recommendations to address them are in file 09.

## A. Routing and URL preservation

| # | Risk | Basis | Rating |
|---|---|---|---|
| A1 | **No redirect layer exists.** `.htaccess` has an HTTPS redirect, an API rewrite and three Ledger shell rewrites; nothing maps an old URL to a new one. Renaming or moving any article or election page produces a 404 until a rule is written | Verified (`dist/.htaccess`) | High |
| A2 | **The release zip overwrites `.htaccess`.** `looklearnfind-elections-update.zip` contains four `.htaccess` files, so every full deploy replaces the live routing file with the repository's copy. Any hand edit made only on the server will be lost. Whether the live file currently equals the repository's was not compared | Verified (zip listing); live comparison Unknown | Medium |
| A3 | **121 district URLs and 24 article URLs are indexed and linked.** Every district page has at least 5 internal inbound links; every article 6 to 11. Sidebar, "Keep looking" blocks, hubs, the homepage and `data/discovery.json` all store these paths | Verified (inbound-link count from `dist/`) | High |
| A4 | **Two parent URLs are dead ends.** `/elections/` and `/elections/2026/` return 403. A post-election hub that lives there is new; but crawlers and users already trimming URLs hit the 403 today | Verified (curl) | Medium |
| A5 | **Article slugs embed "october-2026" in 13 of 21 political articles.** A living page that keeps the same slug will carry a stale-looking URL; changing the slug triggers A1 | Verified | Medium |
| A6 | **Route stability on TIP.** LLF links to 132 distinct TIP race URLs and 391 candidate URLs from 151 pages. TIP race slugs are `race_key` values and candidate URLs use the FEC ID, so any rekeying, alias merge (`merged_alias` rows exist) or cycle suffix change breaks LLF links. TIP links back to LLF only on candidate pages and only to the homepage | Verified | High |
| A7 | **Shell routes depend on rewrite rules.** `/look/L-xxx/`, `/u/{handle}` and DB-only threads work only through `.htaccess`; moving the site or changing the server breaks them | Verified | Low |

## B. Canonical, sitemap and structured data

| # | Risk | Basis | Rating |
|---|---|---|---|
| B1 | **Canonicals are computed from the output path** (`build.py` around line 264). They are correct today (no mismatches on 250 pages) but change automatically if a path changes. If an old and a new page coexist without a redirect, both self-canonicalize and compete | Verified | Medium |
| B2 | **Sitemap `lastmod` is one site-wide value** (`config.json` `updated`, currently 2026-10-31) and is not refreshed per page; pages published 2026-11-01 already carry the older date. Search engines get no signal that a living page changed | Verified (all 231 live entries read 2026-10-31) | Medium |
| B3 | **Sitemap is generated, not hand-edited**, and excludes `noindex` pages. New page types are included automatically only if the build marks them indexable | Verified | Low |
| B4 | **Structured data covers articles only.** `NewsArticle` appears on the 21 political articles; hub, race and district pages carry only breadcrumbs, so there is no existing markup to preserve or to conflict with for results or events. The three sample articles have none | Verified | Low |
| B5 | **Four candidate state lists are `noindex`** (IL, MN, NY, PA) by design; reworking directory templates could drop that flag unintentionally | Verified | Low |
| B6 | **robots.txt:** the live file is hosting-managed and AI-training crawlers are disallowed; the repository copy is the old `Disallow: /`. Uploading the wrong one deindexes the site. The build has `--keep-live-robots` and `CLAUDE.md` forbids `release/looklearnfind-site.zip` | Verified | High if mishandled |
| B7 | **Search index growth.** One 141,599-byte file loaded in the browser holds story text and 386 candidates. Adding results, races or articles at scale will grow it; no sharding exists | Verified size; effect Inferred | Low |

## C. Content and editorial

| # | Risk | Basis | Rating |
|---|---|---|---|
| C1 | **Pre-election framing in published pages.** Hubs read "What is on the ballot"; articles use "as of" dates and "ahead of the election"; market panels show quotes captured 2026-10-23 to 2026-11-01; district pages show outside spending as of capture. None has a post-election state. After results, these pages are accurate as dated records but misleading as current pages | Verified (page text) | High |
| C2 | **Kalshi contracts resolve.** Panels show last-trade prices from before resolution. After settlement a price near 1 or 0 on a page that is not marked as historical could be read as a result | Inferred | Medium |
| C3 | **Rosters are partly unofficial** (IL, NY, MN, PA from Green Papers). Post-election results tables built on those rosters could omit or misname candidates and write-ins | Verified | Medium |
| C4 | **Uneven coverage.** 7 of 50 states exist on LLF; a "Living State Hub" for any other state would start from nothing (rosters, markets, geometry, registry) | Verified | High if the plan promises all states |
| C5 | **Sample content is live and indexable** (3 articles, 3 finds) beside real reporting, contradicting the README's pre-launch posture | Verified | Medium |
| C6 | **Editorial rules do not cover results.** No rule addresses race calls, projections, margins or "leads"; existing rules forbid win probabilities and causal claims. The fact-check gate and R1 to R15 assume pre-election reporting | Verified | High |
| C7 | **Corrections discipline.** 7 of 21 political articles have an empty corrections block; changing shared counting rules once already changed live numbers on published pages (documented in the new-state quickstart) | Verified | Medium |
| C8 | **Naming collision:** "Look Ledger" (LLF), "Issues Ledger" (TIP) and the proposed "State Election Ledger" | Verified | Medium |
| C9 | **Dense dependency between content and `data/discovery.json`.** Every politics story needs an entry or the build fails; hubs, guides and related links are validated against built pages | Verified | Medium |

## D. Technical

| # | Risk | Basis | Rating |
|---|---|---|---|
| D1 | **State additions touch many places.** Adding Minnesota and Pennsylvania required edits to `STATES`, `GEOM_NOTE`, `ROSTER_NOTE` and the build loop in `elections.py`, the homepage tile strings in `build.py`, `discovery.json`, three fetch scripts and a roster builder. Adding a new section type to all states will be a similar multi-file change. `elections.py` is 129 KB and `build.py` 68 KB | Verified | Medium |
| D2 | **Florida is special-cased** (hard-coded story data, `result_bars`, finance on) while other states use generic builders, so a shared new component must handle both paths | Verified | Medium |
| D3 | **Manual, unstaged deployment.** One local build, a zip, a server backup, `scp` and `unzip`. No staging site and no automated rollback beyond a tarball. On 2026-10-30 the standard zip would have published unapproved pages, so a partial deploy was hand-built | Verified (deployment notes) | High |
| D4 | **Single-writer rule.** Only one Claude session writes to a state at a time; several sessions also commit to the same branch (`claude/funny-shannon-dg9qoe`). Large cross-state work collides with the per-state ledgers | Verified | Medium |
| D5 | **Local environment fragility.** Windows code-page errors without `PYTHONUTF8=1`; `build.py` fails if run from `dist/` or while a local server holds the folder | Verified | Low |
| D6 | **Test coverage is partial.** 149 tests pass, but page-level tests exist for Illinois and Michigan only; others rely on `build.py --strict` and a smoke script | Verified | Medium |
| D7 | **TIP hosting limits.** TIP runs as a Next.js server on shared hosting; a 2026-10-15 process-limit incident (SWC threads) is documented in `next.config.mjs`, and prior CPU limits drove design choices (`middleware.ts` runs only on two routes). Heavy results rendering or ingestion on TIP must respect those limits | Verified (code comments) | High |
| D8 | **TIP schema baseline is not in the repository.** Migrations cover 17 changes; the original `races`, `candidates` and FEC table definitions are missing, so the database cannot be rebuilt from the repo and index definitions for those tables are unknown | Verified | Medium |
| D9 | **Stale and legacy rows in TIP.** 62 cancelled races, legacy districts (PA-18, PA-24, PA-35, PA-36), 965 candidates with null `verification_status`, two backup tables in the live schema | Verified | Low |
| D10 | **TIP to LLF data is a snapshot.** Any LLF page that shows TIP-derived data can lag the database until a re-export and rebuild | Verified | Medium |
| D11 | **Ledger shell is live but empty.** Public registration and saves are enabled in code; the list returns zero entries. Product direction for it is undecided | Verified; user counts Unknown | Low |

## E. Things not examined
Server logs and analytics (no traffic, ranking or backlink data), the live `.htaccess`, the hosting cron table, real user data in SQLite and TIP, Search Console state, and the performance of either site under load.
