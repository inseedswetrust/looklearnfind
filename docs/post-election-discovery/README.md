# LLF post-election discovery audit

**Audit date:** 2026-11-04 (the day after Election Day).
**Repository revisions:** LookLearnFind `159302a` (branch `claude/funny-shannon-dg9qoe`, 93 commits); The Issues Party `e6e6f4d` (branch `feat/homepage-video`).
**Scope:** discovery only. No application code, routes, schemas, migrations, content or live systems were changed. The only files created are in this folder and the zip beside it.

## The key correction
LookLearnFind is **not** a Next.js and Supabase application. It is a static site built by Python (`build.py`, `elections.py`, `sidebar.py`) with a small PHP and SQLite backend for the Look Ledger. The Next.js 16 and Supabase system is **The Issues Party (TIP)**, a separate repository and site that holds candidate profiles, races and issue grades. Both were audited; each file says which system a finding belongs to.

## What was inspected
| System | How |
|---|---|
| LLF source | `CLAUDE.md`, README, `docs/` (production lock, schemas, runbooks, specs), `build.py`, `elections.py`, `sidebar.py`, `content/`, `data/`, `tools/`, `static/` (CSS, JS, PHP API), `tests/`, state ledgers in `productions/2026/` |
| LLF built output | All 250 pages in `dist/` (titles, canonicals, robots meta, JSON-LD, internal links, headings) |
| LLF live site | `sitemap.xml`, `robots.txt`, a sample of URLs, `/api/me`, `/api/ledger/list`, `/api/threads` (all read-only GET requests) |
| TIP source | `app/` route files, `app/sitemap.ts`, `app/robots.ts`, `middleware.ts`, `next.config.mjs`, `supabase/migrations/`, `components/`, `lib/` |
| TIP live site | `sitemap.xml` |
| TIP database | Read-only REST requests: the table list and column names (from the API description) and row counts and a few non-personal columns for election tables. No user-table rows were read. No writes |

## Limitations and unknowns
- No traffic, ranking, backlink or Search Console data was available.
- The live `.htaccess` and the server cron table were not read.
- TIP index definitions and row-level-security policies for most tables could not be read through the REST interface; the baseline DDL for the core tables is not in the repository.
- Counts of Ledger users, newsletter signups and messages (SQLite) and TIP user rows were not examined.
- LLF `dist/` is the local build from revision `159302a`; it was compared with the live sitemap (identical indexable set, 231 URLs) but live page bodies were not diffed.
- Findings from this session's earlier work (Minnesota and Pennsylvania) are described from the repository and from what was run, not from an independent re-test.
- No screenshots were captured. Component references are by file and function.
- Candidate sources for election results were **not tested**; file 07 marks them Unknown.

## Files
| File | Contents |
|---|---|
| `01_EXECUTIVE_READOUT.md` | Short summary, the system correction, what exists, what does not, constraints |
| `02_SITEMAP_AND_ROUTES.md` | LLF and TIP route trees, nav config, canonical, sitemap, robots, structured data, orphans |
| `03_CONTENT_INVENTORY.md` | Pages, articles by state and format, state coverage, TIP database counts, inconsistencies |
| `04_DATABASE_AND_DATA_FLOWS.md` | TIP entities and relationships, the LLF SQLite schema, file stores and data flows |
| `05_UX_AND_COMPONENTS.md` | Navigation, sidebar, components, design tokens, implemented versus design-only |
| `06_EDITORIAL_WORKFLOW.md` | How articles are written, checked, approved, published and corrected |
| `07_RESULTS_DATA_READINESS.md` | Capability matrix for results, geography, finance and provenance |
| `08_MIGRATION_RISKS.md` | URL, SEO, content and technical risks with evidence |
| `09_ARCHITECTURE_RECOMMENDATIONS.md` | Opinion: reuse, extend, build, decisions, rollout (kept separate from findings) |
| `ROUTE_INVENTORY.csv` | 53 rows: route patterns with instance counts, generator, data dependency, status |
| `CONTENT_INVENTORY.csv` | 90 rows: 27 content files, 7 state data bundles, 56 TIP jurisdictions |

Labels used throughout: **Verified** (observed in code, files, the live site or the database), **Inferred**, **Unknown**.
