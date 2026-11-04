# 02 Sitemap and routes

Sources: the built `dist/` (250 HTML pages, built from revision `159302a`), the live LLF `sitemap.xml` and `robots.txt` fetched 2026-11-04, `dist/.htaccess`, `build.py`, `elections.py`, `sidebar.py`, and for TIP the `app/` directory, `app/sitemap.ts`, `app/robots.ts` and the live TIP sitemap. The machine-readable version is `ROUTE_INVENTORY.csv`. "Template" means a URL pattern; "instance" means a real page.

## 1. LookLearnFind (static)

LLF has no router. Every page is a file `dist/<path>/index.html` written by `build.py` (generic pages, stories, finds, topics, threads, candidate directory), `elections.py` (state hubs, governor, Senate, House, districts) or copied from `static/` (shell pages for the Ledger). `.htaccess` supplies three rewrite rules and an API rewrite. There are **no redirects**.

### Route tree (instances in parentheses)
```
/                                              Homepage (1)
/politics/  /economy/  /society/  /everyday-life/   Category landings (4)
/topics/                                       Topics index (1)
  /topics/{slug}/                              Topic pages (12)
/latest/                                       Newest across Look, Learn, Find
/learn/                                        Story index
  /learn/{slug}/                               Articles (24: 21 political, 3 sample)
/find/                                         Find hub
  /find/businesses/ /guides/ /places/ /products/   Type listings (4)
  /find/{type}/{slug}/                         Hand-written finds (3, all sample)
  /find/candidates/                            Candidate directory (all states)
    /find/candidates/{state}/                  7 state lists (FL, IL, MI, MN, NJ, NY, PA)
/look/   /look/add/   /look/entry/             Ledger shells (rewrite: /look/L-042/ -> /look/entry/)
/threads/                                      Threads index
  /threads/{slug}/                             22 curated thread pages
  /threads/t/                                  Shell for database-approved threads (rewrite)
/u/                                            Public profile shell (rewrite: /u/{handle})
/account/  /admin/                             Ledger account and review desk (noindex)
/search/                                       Client-side search over /search-index.json
/about/  /about/how-we-work/  /about/election-methods/  /about/corrections/  /about/who-we-are/
/community/ /contact/ /contribute/ /disclosures/ /privacy/ /terms/
/elections/2026/{state}/                       State hubs (7: florida illinois michigan new-york new-jersey minnesota pennsylvania)
  /governor/                                   6 (no governor race in NJ in 2026)
  /senate/                                     5 (no Senate race in NY or PA in 2026)
  /house/                                      7 House indexes with district map
  /house/{n}/                                  121 district pages (FL 28, IL 17, MI 13, NJ 12, NY 26, MN 8, PA 17)
/elections/2026/dark-horse/status/             Monitor status (noindex)
```
**Missing parents:** `/elections/` and `/elections/2026/` have no page and return HTTP 403 live (Verified with curl on 2026-11-04).

### Non-HTML routes
`/api/{route}` (PHP JSON API, 49 route cases for auth, ledger, threads, profiles, follows, collections, newsletter, contact and admin), `/sitemap.xml`, `/robots.txt`, `/search-index.json` (451 items: 386 candidate, 24 story, 22 thread, 12 topic, 4 page, 3 find), `/threads.json`, `/site-data.json`, `/data/candidates.json` and `.csv`, `/data/discovery/{story-id}.json` (21 files), `/elections/2026/dark-horse/status.json`, `/site.webmanifest`.

### Navigation configuration
- Main nav is `data/site.json` `nav`: Politics, Economy, Society, Everyday life, Topics, Latest, Look, Find, About, then search and account. There is no "Elections" nav item; election content is reached from the Politics landing, the homepage state tiles, the sidebar and article links.
- Homepage state tiles are hard-coded strings in `build.py` (seven tiles).
- The sidebar rail's state registry and hub list come from `data/discovery.json` (`hubs` keyed by state code).
- State hubs link to their governor, Senate, House and district pages from generated markup.

### Canonical URLs, metadata and structured data (Verified on all 250 built pages)
- Every page has a `<link rel="canonical">` built as `https://looklearnfind.com` plus the path. No page has a canonical that differs from its own URL.
- 16 pages carry `<meta name="robots" content="noindex">`: 404, corrections, who-we-are, account, admin, community, disclosures, dark-horse status, four candidate state lists (IL, MN, NY, PA), look/add, privacy, terms and the threads shell. These are excluded from the sitemap.
- Three shell pages are indexable but not in the sitemap (`/look/entry/`, `/search/`, `/u/`).
- JSON-LD appears on 168 pages: `BreadcrumbList` (147), `NewsArticle` (21, one per political article) and `Organization` (21). Race, hub and district pages carry breadcrumbs only; they have no `Event`, `Place` or `ElectionEvent` markup.
- Open Graph and Twitter tags are generated in the page head (`build.py`, around the canonical line).

### Sitemap and robots
- `sitemap.xml` is generated by `build.py` from the built page list. Live: **231 URLs**, and all 231 carry `lastmod` 2026-10-31. That value is the site-wide `updated` field in `config.json`, not a per-page date, so pages published on 2026-11-01 (Pennsylvania) also say 2026-10-31. Per-page modification dates are not tracked.
- Live `robots.txt` is the hosting-managed file preserved by `--keep-live-robots` (`Allow: /`, a content-signal line of `search=yes, ai-train=no`, and `Disallow: /` for named AI-training crawlers). The repository's own `dist/robots.txt` is the older pre-launch `Disallow: /` file and **must not be uploaded**.

### Deprecated, duplicated or orphaned (Verified unless marked)
- `release/looklearnfind-site.zip` is an older full build that would overwrite live `robots.txt` (flagged in `CLAUDE.md`).
- `docs/election-build/CANDIDATE_DIRECTORY_SPEC.md` still says the directory is "not yet deployed"; it is live. Documentation drift only.
- `/find/people/` appears in `docs/SITEMAP_AND_COPY.md` but is not built.
- Six sample files (3 articles, 3 finds) are live and indexable although the README says all sample content is illustrative. They sit alongside real reporting.
- `/threads/midterms-2026/` and `/threads/local-ballot/` are curated thread pages; whether they list the election articles was **not checked**.
- Dark Horse monitor status exists as both a page and a JSON file; intended.

## 2. The Issues Party (Next.js)

Next.js 16.2.7 App Router, React 19. Public routes live in `app/(public)`, authenticated routes in `app/account`, `app/following`, `app/admin`, `app/(auth)`.

| Route template | Purpose | Instances (live sitemap) |
|---|---|---|
| `/` | Homepage | 1 |
| `/candidates/[fec_candidate_id]` | Candidate profile hub (grades, finance, record), `Person` JSON-LD, generated OG image, `revalidate = 300` | 6,224 |
| `/candidates/[id]/issues-ledger/[commitment_slug]/ping` | Ping a candidate on a commitment, `revalidate = 60` | not in sitemap |
| `/races`, `/races/[slug]` | Race comparison page keyed by `race_key`; alias handling in `lib/elections/aliases.ts` | 513 URLs: 1 index plus 512 race pages |
| `/states/dc`, `/states/dc/[slug]` | D.C. beta hub (listed only while the beta is public) | 37 |
| `/dc/priority-lab` | D.C. Priority Lab quiz | not in sitemap |
| `/parties`, `/parties/[slug]`, `/parties/let-the-people-know`, `/parties/scan-before-you-decide`, `/parties/committee/[slug]`, `/parties/create`, `/parties/host` | Action Parties | 3 |
| `/p/[code]` | 302 short-link redirect to a party | not in sitemap |
| `/match`, `/money-league`, `/voting`, `/about`, `/privacy`, `/terms`, `/search`, `/notifications` | Tools and utility pages | 4 (voting, about, privacy, terms; the others are not in the sitemap) |
| `/account/*`, `/following`, `/admin/*`, `/sign-in`, `/auth/*` | Authenticated and admin | disallowed in robots |
| `/api/race-labels/[raceKey]`, `/api/social/jobs/poll`, `/api/social/jobs/reconcile`, `/api/admin/dc-priority-lab/export` | Route handlers | n/a |

The live TIP sitemap lists **6,782 URLs** (candidates 6,224, races 513, states 37, parties 3, root 1, voting, about, privacy, terms). `app/sitemap.ts` reads the database with the anon key at request time (`force-dynamic`) and notes that it must be split into shards before about 45,000 URLs. `app/robots.ts` blocks account, admin, auth, following, notifications, api, parties/create and parties/host, and blocks three SEO scraper bots. `middleware.ts` runs only on `/account/*` and `/following/*`. `next.config.mjs` and `vercel.json` define no redirects or rewrites. The only redirects in code are sign-in redirects and `/p/[code]`.

Metadata is produced with `generateMetadata` or `export const metadata` on the candidate, race, state and utility pages. Structured data comes from `components/seo/JsonLd.tsx` and is used on candidate pages (`Person`). Race pages and the D.C. state pages do not import `JsonLd` (Verified by search), so they emit no structured data.

**Unknown:** which TIP routes carry the most search traffic. No analytics were inspected.

## 3. How the two sites connect
LLF article and race pages link to `https://theissuesparty.org/candidates/{fec_candidate_id}` and `/races/{race_key}`. LLF reads TIP through offline exports (`node scripts/export/state-packet.mjs <ST>` in the TIP repo, copied into `data/elections/<ST>/tip_export/`), not through a live API. A TIP change reaches LLF only after a re-export and rebuild. The 5 LLF candidates without TIP profiles render without a link.
