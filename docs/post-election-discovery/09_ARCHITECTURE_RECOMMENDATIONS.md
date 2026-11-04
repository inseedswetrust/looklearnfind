# 09 Architecture recommendations

**This file is opinion.** Findings are in files 01 to 08. Everything below is the technical lead's independent view, offered so ChatGPT can design around real constraints. Nothing here was built or tested. Where a choice depends on facts not available to the audit, that is stated.

## 1. What can be reused immediately
- **The state hub generator and its 121 district pages** (`elections.py`): the page skeleton, the roster and market components and the district SVG maps already exist for seven states and need results input, not a rewrite.
- **`data/discovery.json`, `sidebar.py` and the state lens**: a working, deterministic related-content system keyed by state and thread. Post-election items can join it as new `stories` or `hubs` entries.
- **The article format** (front matter, `openfile`, `sources`, `corrections`, `updated` and `dateModified`): already supports dated change notes on a single story, which is the seed of an "editorial ledger" entry.
- **The candidate registry and TIP links** (`data/candidates/`): 391 candidates keyed to TIP FEC IDs.
- **The scheduled monitor pattern** (`tools/dark_horse/`): fetch, capture, keep last-good, mark stale, publish a status file.
- **The production ledger and handoff tooling** (`STATE_LEDGER.json`, `handoff.py`, fact-check gate): proven for briefs, claims, independent review, owner sign-off and deploy. It can drive post-election tasks as another lane.
- **TIP tables `races`, `race_entries`, `candidates`, `candidate_issue_grades` and the `result_status` constraint**: the vocabulary for a results model is already there (none, pending, reported, projected, certified).
- **Provenance habits:** dated hashed captures, `DATA_ACCESS_LIMITATIONS.md`, the source registry.

## 2. What can be extended
- `STATES` configuration in `elections.py` to carry a post-election phase flag per state and per race (pre-election, results pending, reported, certified) that changes which sections a page renders.
- The hub template to add sections for results, signals, a ledger and what happens next, reusing the existing "Keep looking" and card components.
- `discovery.json` `thread` values and `related` links for a signals and accountability thread.
- The sitemap generator to emit per-page `lastmod` from each file's `updated` field.
- The monitor to also watch resolution of the party-winner contracts (feasibility against the Kalshi API is unconfirmed).
- The TIP export script to include results fields once they exist.

## 3. What requires new infrastructure
1. **A results store and ingestion job.** Per race and per candidate: votes, percent, reporting status, source, retrieved-at, and the `result_status` lifecycle. Either TIP tables (preferred if TIP owns races) or LLF JSON files with raw captures (preferred if LLF stays static). See decision D1.
2. **A snapshot and "as of" model** so pre-election pages remain as dated records and post-election pages state what they know.
3. **A per-state living-ledger content type** (dated entries, each with sources, status and author), distinct from a story and from the Look Ledger.
4. **County and historical datasets** and county geometry, if "geographic shifts" and "historical comparisons" are in scope. No county results or past-election data exist today; county-to-district overlap exists only for Florida.
5. **A publishing path that is repeatable and reversible:** scripted deploy with a backup, a dry run listing the files to be changed, and a way to deploy a subset. Today it is manual.
6. **Redirect support** (rules file or generated map) for any moved URL.
7. **A results editorial policy** (calls, projections, margins, corrections, what counts as official).
8. **Possibly a results source agreement.** Options, none tested, in cost order: official state and county sites and files (free, uneven, some blocked to automated requests); FEC data for finance (free); volunteer-assembled archives such as MIT Election Data and Science Lab or OpenElections (free, delayed and incomplete for a live count); commercial feeds from the Associated Press or Decision Desk HQ (paid and licensed; the audit found no account, price or terms); manual entry by an editor from official pages (free, slow, auditable). Which of these supplies which fields is Unknown until each is tested.

## 4. Architecture decisions that must be made first
- **D1. System of record for results:** TIP database, LLF files, or both with one authoritative. This also decides who renders live numbers.
- **D2. Static versus dynamic:** keep LLF static with scheduled rebuilds and uploaded JSON, add client-side fetches from a small API, or move the hub to TIP's Next.js. Constraint: the hosting account has thread and CPU limits (documented in `next.config.mjs`), and LLF has no server runtime besides PHP and SQLite.
- **D3. Where the Living State Hub lives:** under `/elections/2026/{state}/` (existing, indexed), under a new `/states/{state}/` tree (new URLs, needs redirects from existing hubs) or on TIP (TIP has `/states/dc` only). Reusing `/elections/2026/{state}/` preserves equity; it needs a landing at `/elections/` and `/elections/2026/`.
- **D4. Year-proofing:** the hub URL embeds `2026`. A permanent platform needs either a year-agnostic state hub with election pages beneath it or a stated policy that each cycle gets its own tree.
- **D5. What "ledger" means** and what it is called (collision noted in file 05).
- **D6. Which states:** the seven built states first or all 50. Coverage cost per new state is high (roster, TIP gaps, markets, geometry, registry, articles).
- **D7. Candidate pages:** LLF ruled out per-candidate pages (they live on TIP). A results-aware candidate view would either live on TIP or reverse that decision.
- **D8. Pre-election content policy:** freeze, annotate with an "as of" banner or rewrite. The articles currently read as current.
- **D9. Rules for results:** extend `PUBLISHING_RULES.md` before any results appear.

## 5. Greatest regression risk
In order: (1) changing or moving existing indexed URLs without redirects (file 08 A1, A3); (2) overwriting live `.htaccess` or `robots.txt` during a deploy (A2, B6); (3) pre-election pages and market panels presenting stale data as current (C1, C2); (4) a results feature built on unofficial rosters (C3); (5) heavy dynamic work on the shared TIP host (D7).

## 6. A possible incremental rollout
Each step ships on its own and leaves the previous state valid.

1. **Safe fixes, no new features.** Per-page sitemap `lastmod`; a landing page at `/elections/` and `/elections/2026/` (ends the 403s); an "as of" banner on market panels and state hubs; keep all URLs. Decide the sample-content question.
2. **Freeze and archive pre-election pages.** Mark the 24 articles and hub snapshots as pre-election records with dates (using existing `updated` and corrections blocks) without changing URLs.
3. **Define the results model and rules** (D1, D9) and add the schema and an empty results input file or table. No public pages yet.
4. **Ingest results for one state** (a state with an official roster, Michigan or New Jersey, and an official results source that has been tested and found readable) into the store with raw captures; review by a second person per the existing fact-check rule.
5. **Render a results section on that state's hub and race pages** behind a build flag, using existing components; test with the strict build and a new page test; deploy that state only.
6. **Add the State Election Ledger** as a dated-entry content type for that state; migrate relevant article text to ledger entries only if the original URLs keep working.
7. **Add Signals and What Happens Next** sections once data sources are chosen (turnout, spending, geographic shifts, commitments from TIP `candidate_commitment_statuses` and `public_interest_commitments`).
8. **Repeat per state** in the order the ledgers show readiness, with redirects added only where URLs actually move.
9. **Automate** deploy and rebuild once a human-approved, repeatable procedure exists.

## 7. Open questions only the owner can answer
Hosting or budget limits for a results feed; whether LLF should remain static; whether the Look Ledger product continues; the brand name for the new section; whether results are shown as reported-by-source numbers or only after certification; and whether TIP and LLF will share a design system.
