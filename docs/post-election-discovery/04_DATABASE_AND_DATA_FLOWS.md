# 04 Database and data flows

Two data layers exist. **TIP** has a real database (Supabase Postgres). **LLF** has files plus a small SQLite file for the Ledger. No credentials, connection strings or personal data appear here.

**How this was inspected.** TIP: the SQL files in `supabase/migrations/` (17 files, which define only part of the schema), the application code, and the live database through the Supabase REST interface using read-only requests (table list from the OpenAPI description, row counts and a handful of non-personal columns). Index definitions beyond those in the migration files, foreign keys not declared in them, and row-level-security policies for most tables **could not be read** through this interface and are marked Unknown. LLF: `static/api/lib/schema.php`, `data/`, `tools/`.

## 1. TIP Postgres (59 relations in the public API)

### Core election entities (live counts in file 03)
| Entity | Table | Identifier | Important columns | Relationships and constraints |
|---|---|---|---|---|
| Jurisdiction (state) | none | two-letter `state` text on `races`, `candidates`, grades | n/a | **There is no states table.** A state is a string. 56 values appear (50 states, DC and territories) |
| Election cycle | none | `cycle` text ('2026') on `races` and `candidates` | `election_kind` (regular or special), `general_election_date`, `primary_date` | No cycle table. `race_key` carries the cycle, so "next election's ballot is just more rows" (migration comment) |
| Race | `races` | `race_key` text, e.g. `2026-GOV-PA`, `2026-S-MN`, `2026-H-PA-01` | `race_title`, `office_code` (H, S, GOV), `state`, `district`, `display_phase`, `primary_status`, `race_status` (upcoming or cancelled), `incumbent_name`, `incumbent_party`, `competitiveness_label`, registration and voting-rule flags, runoff fields, `snap_*` finance snapshot columns, `verification_status` | Referenced by `race_entries.race_key`. **Results scaffolding:** `result_status`, `result_as_of`, `result_source_url`, `runoff_status`, `runoff_date`. A check constraint allows `result_status` values `none`, `pending`, `reported`, `projected`, `certified`. All 574 rows currently hold `none`; no code reads these columns |
| District | none | `district` text on `races` and `candidates` | n/a | No geometry in the database. District shapes exist only in LLF files |
| Candidate | `candidates` | `candidate_id` (bigint) and `fec_candidate_id` (text; non-FEC placeholders like `GOV-PA-SHAPIRO` are used for governors) | 76 columns: names, `slug`, `office_code`, `state`, `district`, `party_code`, `incumbent`, `race_key` (legacy "current race" pointer), FEC and Ballotpedia fields (`bp_*`), social and campaign URLs, photo fields, `snap_*` finance, `verification_status`, AI bio fields with review status | Slugs are not unique per person (`pa-h-2026` appears on many Pennsylvania House rows), so `fec_candidate_id` is the public key used in URLs |
| Ballot entry | `race_entries` | `id` (generated identity) and `source_key` (unique idempotency key such as `2026-PA-GOVERNOR|Printed|Josh Shapiro`) | `race_key`, `candidate_id`, `fec_candidate_id`, `display_name`, `party_label`, `ballot_party_label`, `ballot_type` (printed or write_in), `status` (active, review, withdrawn), `verification_status`, `source_url`, `checked_date` | `race_key` references `races`; `candidate_id` references `candidates` and may be null; unique index on (`candidate_id`, `race_key`) where `candidate_id` is not null; partial index on `race_key` where active. Row-level security: public read of `active` rows only; writes need the service role |
| Issues | `key_issues` (20), `public_interest_commitments` (6) | `slug` | titles, criteria, sort order, status | The six commitments are the graded issues. The 20 `key_issues` are a broader taxonomy |
| Grades | `candidate_issue_grades` | primary key (`fec_candidate_id`, `commitment_slug`) | `aligned`, `against`, `recorded`, `base_pct`, `ping_answer`, `adjustment`, `final_score`, `rounded_score`, `grade` (A+ to F-), `state` (graded or not_graded), `computed_at` | Check constraints: graded iff a grade exists; `recorded = aligned + against`. Index on (`commitment_slug`, `rounded_score` desc) |
| Evidence | `candidate_commitment_statuses` | `id`; (`fec_candidate_id`, `commitment_slug`) | `status`, `categorical_answer`, evidence summary, source URL and date, AI confidence and review fields, ping counts, outreach status | Feeds grades; row-level security not read |
| Legislative record | `legislative_events` (51), `legislative_event_issues` (52), `legislative_participation` (10,133) | `id`, `record_id`, `action_key` | roll call, chamber, tally, source URL, evidence status | Links members to votes; source for "recorded acts" |
| Campaign finance | `fec_candidate_totals` (4,016), `fec_candidate_finance` (7,972), `committees` (7,103), `candidate_committees` (7,160), `source_issue_money_signals` (577) | `fec_candidate_id`, `cycle` | receipts, disbursements, cash, donor breakdowns, top donors and industries, monthly receipts; AIPAC-related signals with `signal_key` | Candidate finance is by candidate committee. Independent expenditures are **not** stored here except as `source_issue_money_signals` entries |
| Articles | **none** | n/a | n/a | TIP stores no articles. LLF articles exist only as files |
| Sources and citations | `candidate_contact_sources` (5,039), `candidate_source_signals` (356), `source_*` tables (congress members, financial disclosures, OpenSecrets summaries, Public Interest grades and finances: up to 163,095 rows) | various | imported third-party data kept separate from published fields | Provenance is per table, not a unified citation model |
| Election results and vote totals | **none** | n/a | n/a | Only the `races.result_*` scaffolding above |
| Editorial metadata | none for editorial content | n/a | n/a | Only AI bio review status on candidates and `verification_status` fields |
| Users and engagement | `profiles` (4), `user_candidate_follows` (4), `user_race_follows` (2), `candidate_match_*` (quiz), `action_parties` (2), `signal_score_events`, `user_civic_dailies`, `dc_priority_lab_*` | UUID-style user ids | not inspected beyond counts | Personal data; not read |

### Other observations (Verified)
- Public reads go through the anon key and RLS; the sitemap deliberately uses the anon client. Admin and export scripts use the service role from `.env.local` (not exposed here).
- Two backup tables are in the live schema: `backup_20261014_candidates` and `backup_20261014_races`.
- Migration files cover only 17 of the schema's changes. The original `races`, `candidates` and FEC tables are **not** defined in the repository's migration folder, so the repository cannot rebuild the database from scratch. Unknown: where the baseline DDL lives.
- Seven Supabase Edge Functions exist for the civic daily and signal-score features (`supabase/functions`), unrelated to election content.

### Where TIP data originates
Seeded from FEC candidate data, Ballotpedia (`bp_*` columns) and other imports (for example the Pennsylvania race rows carry `created_at` 2026-06-02); rosters and race entries added per state from handoff exports (`data_source` values such as `handoff_roster` and `official_roster_checked`); issue grades computed by a job from recorded congressional acts and answered pings; finance from OpenFEC; third-party signal tables from OpenSecrets, Public Interest and congressional sources.

## 2. LLF SQLite (Ledger only)
Schema in `static/api/lib/schema.php`: `users`, `sessions`, `resets`, `rate`, `videos` (the saved items), `saves`, `save_threads`, `video_links`, `threads`, `follows`, `collections`, `collection_items`, `reports`, `audit`, `desk`, `desk_items`, `newsletter`, `messages`, `meta`. Indexes include `videos_active`, `saves_video`, `saves_user`, `saves_pub`, `save_threads_t`, `rate_k`. The file is protected by `.htaccess` rules and lives on the server, not in the repository. Live status: the public list endpoint returns zero entries. **Unknown:** counts of users, newsletter signups and messages (not queried; personal data).

## 3. LLF file data (the actual content store)
| Path | Holds |
|---|---|
| `content/learn/*.html`, `content/find/*.html`, `content/*.html` | Articles, finds and pages: front matter plus body with `openfile`, `sources` and `corrections` comment blocks |
| `data/discovery.json` | Sidebar registry: 3 thread names, 21 story entries (states, thread, short headline, priority, up to 2 related), 7 state hubs with guides, 1 national tracker |
| `data/site.json`, `data/threads.json`, `data/copy.json`, `data/seo.json` | Navigation, categories, topics, 22 curated threads, copy and SEO text |
| `data/elections/<ST>/` | `roster.json`, `candidates.json` (roster joined to TIP), `markets.json`, `districts.json` (SVG paths), `portraits.json`, `tip_export/` (8 TIP tables as CSV and JSON, plus `summary.json` and `reconciliation.json`), `captures/` (raw hashed source captures) |
| `data/elections/dark_horse/` | Daily monitor output and watchlist |
| `data/elections/hero_credits.json` | AI-illustration credits for hero images |
| `data/candidates/<ST>.json`, `races.json` | Candidate registry: 391 candidates and race rows, validated by `build_registry.py --check` and a test |
| `productions/2026/<ST>/` | Per-state ledger, briefs, claims, drafts, QA, handoff packages |

## 4. Data flows

```
Green Papers / official state lists --> tools/elections/build_<st>_roster.py --> data/elections/<ST>/roster.json
TIP Supabase --> scripts/export/state-packet.mjs (TIP repo) --> data/elections/<ST>/tip_export/ --> join_tip.py --> candidates.json
                                                                               (checks each TIP URL returns HTTP 200)
Kalshi public API --> fetch_kalshi.py --> markets.json (+ raw capture)
Census cb_2024_us_cd119_500k shapefile --> build_cd_geometry.py --> districts.json
Wikipedia / Wikimedia (licensed only) --> fetch_portraits.py --> static/img/elections/portraits + portraits.json
OpenFEC --> fetch_fec.py, fetch_fec_ie.py, reconcile_ie.py (finance and independent expenditures; optional, never a gate)
Kalshi + Polymarket + VoteHub --> tools/dark_horse/daily.py --> data/elections/dark_horse/daily/<date>/ --> status.json copied to server
data files + content/*.html --> build.py / elections.py / sidebar.py --> dist/ --> zip --> manual upload to hosting.com
```
- **Capture model:** each fetch stores a dated, hashed raw capture so a published number can be traced to a file.
- **TIP to LLF is a snapshot, not a feed.** A TIP edit does not appear on LLF until someone re-exports and rebuilds.
- **Direction of write access:** LLF never writes to TIP. TIP writes (new profiles, race entries, promotions) happen through reviewed scripts in the TIP repo (`apply-*-gap-fixes.mjs`, `promote-*-governor-entries.mjs`) with a row backup first and owner approval recorded.
- **Provenance rules** are enforced by convention and by the QA gate (`tools/qa/factcheck_gate.py`), not by database constraints.
