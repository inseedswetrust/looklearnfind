# Implementation Report: LLF Florida election pages

**Date:** 2026-10-23 | **Repo:** `looklearnfind` branch `claude/funny-shannon-dg9qoe` | **Status: built, QA'd locally, staged. NOT deployed (blocker below).**

## 1. Deployment status (read this first)

| Item | State |
|---|---|
| Build | `PYTHONUTF8=1 python build.py` builds 110 pages without errors |
| Local QA | 36 of 36 election pages pass `tools/qa/smoke.py`; 1440 and 390 px screenshots show no horizontal overflow (details in section 5) |
| Release file | `release/looklearnfind-elections-update.zip`, 10800 KB, 236 files, SHA-256 `da3600d34438485dcf41ec5706f2760d1750020e0c111b68c0a6490bbdbcaede` (rebuild changes the hash) |
| Live site today | `https://looklearnfind.com/` returns 200. `https://looklearnfind.com/elections/2026/florida/` returns **404** (checked 2026-10-23 15:04 UTC), so none of this is live yet |
| **Blocker** | Production is a hosting.com cPanel account. This session has no cPanel, SFTP or hosting credentials, and by project rule credentials are not entered or stored here. Deployment is the existing manual step: upload the zip and extract over the site folder (`docs/DEPLOY.md` section 3 and "Updating the site"). `llf-data` is outside the site folder, so the database is untouched. |
| Why the update zip omits robots files | The repo's `static/robots.txt` is the pre-launch "Disallow: /" file. The live `robots.txt` currently reads `Allow: /` with Cloudflare directives. Extracting the full zip would replace it and could block search engines from the live site. The update zip leaves robots untouched (`python build.py --zip --keep-live-robots`). |
| Commit | Local commit only. Nothing is pushed to the public GitHub repo until you say so |

**Owner steps to deploy (about 5 minutes):**
1. cPanel > File Manager > the looklearnfind.com site folder.
2. Upload `release/looklearnfind-elections-update.zip`.
3. Right-click > Extract into the site folder itself (overwrite when asked). Delete the zip.
4. Run `python tools/qa/smoke.py https://looklearnfind.com` (or open the 8 URLs in section 2).
5. Tell me; I will run the smoke test against the live URL and record the evidence.

**Decision for you:** the live site still shows "Illustrative sample" stories at `/learn/` while its robots file allows crawling. Our election pages are real reporting. Mixing the two on a crawlable site is a launch-readiness question, not a build question.

## 2. Pages and routes

| Experience | Route (file written) | Mockup | Notes |
|---|---|---|---|
| State landing + State Board | `/elections/2026/florida/` | 01 | all 30 contests, 96 candidates, "Key Ballot Measures" replaced by the House directory link |
| Governor guide | `/elections/2026/florida/governor/` | 02 | 10 tickets, official matching funds, attributed committee money, UNF poll, Kalshi, campaign-page proposals |
| Senate guide | `/elections/2026/florida/senate/` | 03 | 3 candidates, FEC totals, outside spending table, Kalshi, UNF poll |
| House atlas | `/elections/2026/florida/house/` | 04 and 05 | cards view and directory table on one page (both alternatives), map of the 2026 districts |
| District pages (28) | `/elections/2026/florida/house/<n>/` | 04, 05 | every candidate, FEC totals, outside spending, Kalshi, prev/next |
| Delta Report | `/learn/michigan-senate-delta-october-2026/` | 06 | real Kalshi candlesticks; tabs for daily and the debate window |
| Spending Report | `/learn/florida-house-independent-spending-october-2026/` | 07 | **slug changed** from the suggested `florida-house-advertising-surge-...` because the story was rebuilt from FEC filings, not ad-tracker data |
| Governor reported feature | `/learn/florida-governor-fundraising-polling-2026/` | 08 | |
| Methods | `/about/election-methods/` | n/a | roster rules, money definitions, Kalshi, TIP grade formula, corrections |

## 3. Components (reused and created)

| Spec component | Implementation |
|---|---|
| StateLanding | `elections.state_hub()` |
| StateOfficeGuide | `gov_page()`, `senate_page()` |
| HouseDirectory | `house_page()` (cards + table), `district_page(n)` |
| ReportedArticle | `render_report()`; reuses the existing `openfile`, `sources`, `corrections` blocks and numbered `SOURCE nn` footnotes of the Story Reader |
| MarketDeltaChart | `delta_chart()` inline SVG from captured candlesticks, no smoothing |
| SpendingChart | `spend_chart()` weekly bars from deduplicated Schedule E rows |
| CandidateCard | `candidate_card()` with portrait or monogram, FEC totals, issue strip, links |
| TIPIssueRecord | `issue_strip()`, `tip_panel()`: six icons, three states (graded letter, not graded, no TIP record) |
| SourcesBlock | existing story sources markup |

Reused from the live site: masthead, footer, `shell()`, `page_head` conventions, `.band`, `.kicker`, `.open-file`, `.sources`, `.corrections`, brand tokens, Newsreader. No microsite, no new framework.

## 4. Exact changed and new files (LLF repo)

- Modified: `build.py` (imports `elections`, renders `layout: report` stories, `--keep-live-robots`, Windows-safe date format), `static/css/site.css` (one line: footer link wrap on phones).
- New code: `elections.py`, `static/css/elections.css`, `static/js/elections.js`, `tools/elections/*.py` (fetch roster, geometry, FEC, Kalshi, portraits, heroes, TIP join), `tools/qa/*` (screenshots, smoke test, manifest, serve).
- New content: three `content/learn/*.html` stories.
- New data: `data/elections/FL/*`, `data/elections/MI/*`, `data/elections/hero_credits.json`.
- New assets: `static/img/elections/*` (3 heroes, 30 portraits), `assets/icons/issue-*.svg` (6 icons).
- Docs: `docs/election-build/*`.
- TIP repo (not deployed): `scripts/export/state-packet.mjs`, `build-commission.mjs`, `docs/florida-handoff/*`, `docs/state-packets/FL/*`.

## 5. QA evidence (local, 2026-10-23)

- `tools/qa/smoke.py http://localhost:8091`: **36/36 pages OK** (200, canonical, og tags, no `noindex`, no template leftovers); 62 internal links, **0 broken**; 200 external links, all reachable except Kalshi market pages (HTTP 429 rate-limit, unverifiable by script) and the Washington Post URL (access error, cited only as an unused source).
- `tools/qa/shots.py` (Edge via Playwright) on hub, governor, senate, house, FL-14, FL-25, the three reports, methods at **1440 and 390 px**: horizontal overflow none after fixes (found and fixed: footer link row at 390; grid children without `min-width:0` on senate and district pages); images without alt: 0; broken images: 0. Screenshots were read for layout on hub, governor, senate, house atlas, spending, delta and a 390 px district page.
- Console: only `/api/me` 404 locally (the PHP backend is not served by the static test server; it exists on the live host).
- Not verified: Lighthouse accessibility score; screen-reader pass; the live host's `/api/me`. Small-target count (17 to 23 per page) comes from existing site nav and footer text links, not election components.
- OG images use the site default (`/img/og-learn.jpg`); data-rendered OG cards are not built yet.

## 6. Where the implementation differs from the mockups

- Mockup people, amounts, market prices, maps and district city names were not used (they were AI-generated and wrong, e.g. other governor candidates, a different third Senate candidate, "FL-7 Tallahassee"). District labels are the largest counties by area from the official 2026 file.
- Party chips are neutral outline letters, not red and blue fills. Candidate photos appear where a license exists (30 portraits); everyone else gets a monogram.
- The House atlas keeps both approved treatments (cards, directory) on one page.
- The Delta chart plots real hourly and daily points; the mockup's smooth curve was illustrative.
- The Spending chart plots FEC independent expenditures by dissemination week; the mockup's multi-day bars were illustrative.
- TIP grade chips: A+ to F- when graded, a dash when not, a dot when TIP has no record. No green or red.

## 7. Data and TIP issues found (for TIP, not LLF)

1. TIP `races` still show `display_phase=primary_upcoming`, `verification_status=seed`, `result_status=none` for all Florida races though the state shows primary results; the governor race has no `race_entries`. A SQL proposal for your review is the next step you approved (nothing has been run).
2. TIP's public About page still says "five Public Interest Commitments"; the database has six.
3. Two TIP candidate URLs return 404 (Salomon Hernandez Sr. `H4FL14166`, Casey Askar `H6FL22248`); LLF omits those links.
4. The TIP row for the Senate independent is spelled "Neil Joseph Gilespie"; the state spells "Neil J. Gillespie".
5. David Jolly and the other governor candidates have no TIP page. Donalds has two TIP rows (governor page and House page).
6. Source `source_issue_money_signals` carries a separate AIPAC-tracking letter grade; LLF does not show it.

## 8. Known limitations and decisions

- Governor campaign and committee totals are press-reported (Sept 11) because the state database blocks automated access. They are labeled and dated.
- Kalshi quotes are a snapshot (captured 2026-10-23 14:34 UTC). The pages state the capture time; there is no auto-refresh.
- Portraits come from Wikipedia lead images with Commons license metadata, not from candidate-owned sources.
- Windows build note: run `PYTHONUTF8=1 python build.py`; on Linux no change is needed.
