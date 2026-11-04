# 04 Staging, deployment, regression testing and rollback (follow-ups 6 and 7)

Responds to architecture v1 section 10 items 6 and 7. Everything here is a plan; no staging site, script or deploy was created. Facts about today's process come from `docs/DEPLOY.md`, `docs/production/09_OPERATING_PROCEDURES.md`, the deployment notes from this project's Minnesota and Pennsylvania releases, `tools/qa/`, `build.py` and `dist/.htaccess`.

## 1. How deployment works today (Verified)
1. `python build.py --strict --zip --keep-live-robots` writes `release/looklearnfind-elections-update.zip` (about 29 MB, 570 files). The flag leaves out `robots.txt`; it does **not** leave out the four `.htaccess` files.
2. A tarball of the live docroot is taken on the server (`~/backups/looklearnfind.com-pre-<date>.tgz`, about 26 MB).
3. The zip is copied with `scp` (from a path without spaces) and unzipped over the docroot with `unzip -oq`.
4. URLs are checked with `curl`; `tools/qa/smoke.py <base>` can check a base URL.
5. The owner must say "deploy" in plain words first (the auto-mode classifier also blocks deploy commands until then), and the authorization is recorded in the ledger and decision log.
There is no staging site, no automated deploy, no per-file diff before upload and no continuous deployment from GitHub.

## 2. How to create a safe staging preview (follow-up 7)
Requirement: the owner (and ChatGPT's reviewers if wanted) can see the real built site, with the `.htaccess` rewrites and the Ledger shells, **without it being indexed or reachable by the public** before approval, and without changing the live docroot.

| Option | Cost | What it gives | Limits and unknowns |
|---|---|---|---|
| **A. Local preview** (exists today) | Free | `tools/qa/rebuild_serve.sh` builds and serves `dist/` at `localhost:8091`; `php -S` with `tests/router.php` mirrors the rewrite rules and the PHP API; `tools/qa/smoke.py` and `tools/qa/shots.py` (Playwright, 1440 and 390 px) run against it | Only on the owner's machine. Not a test of the real server's Apache rules |
| **B. Shareable local preview through a tunnel** | Free tiers exist | Lets a reviewer open the local server through a temporary public URL | Exposes unapproved pages to anyone with the link; tool terms and security were not evaluated |
| **C. A hosting.com subdomain** (for example a staging subdomain with its own folder) | Probably within the existing plan; **Unknown** whether the plan allows another subdomain or add-on | Same Apache, PHP and `.htaccess` as production; deploy with the identical zip procedure into its own docroot; put it behind cPanel Directory Privacy (password) | Needs DNS and an SSL certificate for the subdomain; the build must not point canonicals and Open Graph URLs at the production domain from the staging copy (see section 3); must send `noindex` |
| **D. A password-protected folder on the production domain** | Free | No new DNS | Shares the domain, cookies and robots; easy to leak into indexing or the sitemap if misconfigured; **not recommended** |
| **E. A third-party static host with access control** (for example GitHub Pages, Cloudflare Pages, Netlify, Vercel preview deployments) | Free tiers exist; access control features differ and were not verified | Branch previews | `docs/DEPLOY.md` describes the LLF repository as public, so a Pages preview of an unapproved branch would be public. No hosting-side PHP, so the Ledger API would not run. Confirm each provider's access protection before use |
| **F. Send the zip for review** | Free | Reviewers unzip and serve it locally | Root-relative links (`/css/...`) need a server; opening files directly does not work |

**Recommended combination (opinion):** A for every change, plus C once the owner confirms the plan allows a subdomain, because C is the only option that tests the real server rules and the zip procedure end to end. D and B are weaker; E needs a provider-specific access review. If C is unavailable, A plus a pre-deploy file listing and a live URL regression run (section 4) is the minimum.

## 3. Build changes a staging copy would need (not implemented)
- `config.json` has one `url`; canonicals, Open Graph URLs, sitemap `loc` and JSON-LD use it. A staging build needs an override (for example an environment variable that replaces the base URL and adds `noindex` and `Disallow: /`).
- The staging copy must never include the live `robots.txt` logic: staging gets its own `Disallow: /`.
- Staging data must not contain fabricated results. Placeholders must be visibly marked and removed from the production build.

## 4. Staged deployment, per gate
Applies to plan gates B to E. The owner's authorization is recorded for each deploy (R14).

**Before building**
1. Working tree clean for files in scope; only one Claude session writing to the state (ledger rule).
2. `python build.py --strict` reports 0 violations; the full test suite passes (149 tests today).
3. For a results release: `validate` passes and a reviewer other than the person who captured the data has approved the snapshot.

**Before upload (new checks proposed, using existing tools where noted)**
4. **Route diff:** compare the set of built pages with the live sitemap and last deploy's page list; every previously present URL is present, with an explicit allowed-changes list (a proposed `tools/qa/route_diff.py`).
5. **Canonical and noindex diff:** for the 250 pages that exist today, canonical, `robots` meta and title are unchanged unless listed as intended. Today's expected noindex set is 16 pages.
6. **Article body diff:** for the 24 `/learn/` pages the only difference is the approved banner and related-link block.
7. **Zip listing review:** list the zip, check it contains no `robots.txt`, no unapproved pages and no stray files; compare the four `.htaccess` files with the live copies (hash) and stop on any difference.
8. **Live baseline:** save the live `robots.txt` and `sitemap.xml` hashes and the status of the key URLs.

**Upload**
9. Server backup tarball first (retain at least the previous three); upload; unzip; remove the zip.

**Verify immediately**
10. `tools/qa/smoke.py https://looklearnfind.com` with the updated page list; all 231 sitemap URLs return 200; the two new landing pages return 200; `/elections/2026/dark-horse/status/` still returns 200.
11. `robots.txt` hash equals the baseline; `sitemap.xml` includes the new pages and per-page `lastmod`.
12. Spot-check `view-source` of one hub, one district and one article for canonical, noindex and JSON-LD.
13. TIP deep links from the new sections resolve (the smoke tool already checks these).
14. Record the release in `STATE_LEDGER.json` and the decision log; commit.

**Gate-specific scope**
- **B (structure):** upload only new landing pages and changed hub layouts; no results code path is enabled.
- **C (one-state pilot):** per-state flag on; all other states remain on the previous layout; verify stale and error states by temporarily marking the source stale in a staging build, not in production.
- **D (seven states):** one state per release; do not batch.
- **E (accountability, `/states/{state}/`):** new URLs only after the plan's search-intent review; add redirects only for URLs that move.

## 5. Regression test plan
| Area | Check | Tool |
|---|---|---|
| Routes | every preserved URL returns 200; new URLs return 200; `/elections/` and `/elections/2026/` no longer 403 | proposed `route_diff.py`, `smoke.py` |
| SEO | canonicals, `noindex` set, titles, meta descriptions, `NewsArticle` count 21 and `BreadcrumbList` on 147 existing pages (proposed new crumbs documented) | scripted read of `dist/` (the audit's page-meta script is a model) |
| Sitemap | indexable set equals expected; per-page `lastmod` valid dates; no noindex pages | script |
| Robots | live hash unchanged | curl and hash |
| Content | article bodies unchanged except banner; sources and corrections blocks intact; R1 and R2 links still emitted | strict build, diff |
| Data | JSON validates against `schemas/`; vote sums and percentages recomputed; candidate mapping complete | proposed `validate.py` |
| Display | every number on a results page shows source, retrieved time and as-of; stale and unavailable states render | manual plus screenshot set |
| Layout | no horizontal overflow, tap targets, image alt text at 1440 and 390 px | `tools/qa/shots.py` |
| Accessibility | keyboard path through the hub and race rows; screen-reader check of expandable rows and status chips; contrast of status chips | manual (not covered by existing tools) |
| Links | internal links; TIP deep links; official source links | `smoke.py` |
| Search and discovery | hub pages added to `/search-index.json` if intended; sidebar validation passes | build |
| Ledger shells | `/look/`, `/u/`, threads shell still served by rewrite rules | local `php -S` and live curl |
| Performance | page size of heaviest hub and district pages; search index size | manual |

## 6. Rollback plan
| Situation | Action | Notes |
|---|---|---|
| Any gate fails verification | Restore the previous files from the pre-deploy tarball (`tar xzf ... -C ~` restores the folder; to restore only some paths, extract those paths) | A tarball has been taken before each release, but a restore has not been exercised in this project and its time was not measured |
| `robots.txt` or `.htaccess` damaged | Restore those two files from the baseline copies kept before each deploy, then re-run the verify step | The zip should not contain `robots.txt`; `.htaccess` is in the zip, so this is the likeliest self-inflicted failure |
| Bad numbers on a results page | Set the state's `approved.json` pointer back to the previous snapshot and rebuild that state, or set the per-state results flag off and rebuild; publish a corrections entry | A kill switch per state is part of the proposed design |
| A moved URL 404s | Add a rewrite rule in `.htaccess` (redirect map) and redeploy only that file | No redirect layer exists yet; build it before moving anything |
| Stale data presented as current | Flip the page to its "source stale" state by status job or manual flag; do not delete the number | |
Authorization: a rollback restores a previously authorized state; log it in the ledger. A forward fix that publishes new content needs fresh authorization.

## 7. Contradiction to resolve before automating
Section 7 of the plan says results may be refreshed independently as static JSON. Under `CLAUDE.md` every upload or deploy needs the owner's explicit authorization recorded per action. Independent refreshes would need a standing, scoped, recorded authorization (for example "refresh approved JSON for these sources at this cadence") or each refresh remains a manual deploy. See file 05.
