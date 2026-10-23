# Implementation Report: LLF Florida election pages

**Date:** 2026-10-23 | **Repo:** `looklearnfind` branch `claude/funny-shannon-dg9qoe` | **Status: built, QA'd, deployed and verified live (see section 1).**

## 1. Deployment status (updated 2026-10-23, after deploy)

| Item | State |
|---|---|
| LLF site | **Live.** The owner extracted `looklearnfind-elections-update.zip` on 2026-10-23. `https://looklearnfind.com/elections/2026/florida/` and the other 35 election URLs return 200. Live `robots.txt` was left untouched; the sitemap lists the election pages |
| Live evidence (run against the live site, 2026-10-23) | `tools/qa/smoke.py https://looklearnfind.com`: **36/36 pages OK**, 62 internal links 0 broken, 249 external links all reachable except Kalshi market pages (HTTP 429, rate limit) and the Washington Post. `tools/qa/shots.py` on hub, governor, FL-14, the Delta Report and the governor feature at 1440 and 390 px: no horizontal overflow, no missing alt text, no broken images, no console errors |
| TIP site (theissuesparty.org) | **Live** with the one-profile-per-candidate code (alias redirects, "Currently serving in Congress" chip, expandable biography). Release `20261023-11d81b4`, merged on top of the other session's ledger-banner build `4f5029c`. Previous build kept as the rollback (`~/tip/web.prev`) |
| TIP database | Florida governor roster, one-profile merge for 18 people, eight missing Florida profiles and 17 biographies applied on 2026-10-23, each with a backup under `docs/state-packets/backups/` (TIP repo) |
| Publishing rules | R1 (candidate to TIP profile) and R2 (race to race link) enforced at build; `python build.py --strict` passes with 0 violations for all 96 Florida candidates |
| Git | LLF commits local on `claude/funny-shannon-dg9qoe` (`7c75bed` and earlier), TIP commits local on `fix/one-profile-per-candidate` and `deploy/one-profile-plus-ledger-banner`. Nothing is pushed to GitHub |

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

0. **Publishing rules R1 and R2 (added after owner review):** every featured candidate links to a TIP profile and every mentioned race links to its race. See `PUBLISHING_RULES.md`; 17 candidates currently have no working TIP profile (build reports them; `--strict` fails on them). Donalds' grades are linked to his congressional TIP profile, the page where they are visible.

1. TIP `races` still show `display_phase=primary_upcoming`, `verification_status=seed`, `result_status=none` for all Florida races though the state shows primary results; the governor race has no `race_entries`. Applied 2026-10-23 (see `ONE-PROFILE-PER-CANDIDATE.md`).
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
