# Candidate directory: audit and specification

Written 2026-10-31; revised the same day on the owner's direction: **no per-candidate pages on LookLearnFind. Every candidate row links to that person's page on theissuesparty.org, and TIP is the source for any person-level information LLF lacks.** Audience: Claude Code sessions that build and refresh state data, and whoever approves the page design. This file does two things: it records how candidate information is stored today (section 1 to 3) and it specifies how it should be stored so that `/find/candidates/` and every other surface fills itself (section 4 onward).

## 1. What is wrong, and why

`https://looklearnfind.com/find/candidates/` says "No candidates listed yet." That page is not broken. It is the generic **Find** listing for `type: candidate`, and it lists only hand-written files in `content/find/` with `kind: find` and `type: candidate`. There are none. Meanwhile the repository holds **329 qualified candidates for five states** that nobody wired to that page, because election data lives in a separate system that only the state-of-the-race pages read.

The two systems:

| System | Where | What reads it | Candidates it holds |
|---|---|---|---|
| Find listings (editorial, hand-written) | `content/find/*.html`, front matter `kind: find`, `type: candidate\|business\|guide\|product\|place`, with `why`, `checked`, `limits`, `know` comment blocks | `build.py` (`load_content`, `gen_find` around line 590), the search index, the sidebar catalog | 0 (the three files present are illustrative samples of other types) |
| Election data (structured, per state) | `data/elections/<ST>/candidates.json` plus `roster.json`, `portraits.json`, `markets.json`, `districts.json` | `elections.py` only, one state at a time through `_load_state()` | 329 |

Nothing connects them. A reader who opens Find, Candidates, or searches for a candidate's name, gets nothing, even though a full profile card for that person exists on a state page.

## 2. Audit: how candidate information is stored today

### 2.1 Inventory (counts as of 2026-10-31)
| State | Candidates | Governor | Senate | House | TIP profile reachable (HTTP 200) | At least one graded issue | Write-ins | No FEC or TIP id | Portrait entries |
|---|---|---|---|---|---|---|---|---|---|
| FL | 96 | 10 | 3 | 83 | 96 | 23 | 0 | 0 | 59 |
| IL | 54 | 11 | 4 | 39 | 54 | 12 | 12 | 11 FEC ids empty | 44 |
| MI | 75 | 5 | 6 | 64 | 74 | 11 | 2 | 0 | 30 |
| NJ | 40 | 0 | 5 | 35 | 39 | 12 | 1 | 0 | 25 |
| NY | 64 | 4 | 0 | 60 | 62 | 21 | 2 | 2 FEC ids empty and 2 without a TIP page | 54 |
| **Total** | **329** | 30 | 18 | 281 | **325** | **79** | 17 | | |

### 2.2 The files per state
- `candidates.json`: `{as_of_utc, issues, candidates[]}`. Each candidate: `id, name, party_code, party, office, race, incumbent, running_mate, status, primary, state_url, fec_candidate_id, tip_page_id, tip{url, grades_url, grades{<issue>:{state,...}}, http_status, checked_at}`. IL, MI, NJ and NY add `tip_name, write_in, note`. This is the best record and the natural base of the registry.
- `roster.json`: the roster as read from the official or secondary source, with `sources`. It duplicates `candidates.json` in a different shape (`governor`, `senate`, `house` sections).
- `portraits.json`: keyed by the candidate `id`. Entries record `result`, license and credit. Images live in `static/img/elections/portraits/<id>.jpg`.
- `markets.json`: Kalshi capture, keyed `governor`, `senate`, `house-NN`. Race-level, not person-level.
- `districts.json`: geometry for district maps. `finance_fec.json` and `ie_all.json`: Florida only.
- `tip_export/*`: read-only export from TIP (candidates, races, race entries, issue definitions, ratings). Source of the grades.
- Michigan additionally keeps `senate_delta/` (older Senate-only files used by one report). Illinois keeps `extra_people.json` and mapping CSVs.

### 2.3 Where the information is used
- `elections.py` renders hub, governor, Senate, House directory and district pages per state, from the active state's files, through the global `FL` dict (named for Florida, the first state). `STATES` in the same file holds the per-state settings (name, slug, district count, source note, official or not, primary date).
- Reported pieces in `content/learn/` link to TIP profiles by hand-written URL and use `[[v:...]]` value macros that read the same data.
- **Not** used by: the Find section, the Candidates topic page, the search index (`write_search_index()` indexes stories, finds, threads, topics and pages only), the sidebar catalog, or any cross-state view. There is no public machine-readable file.

### 2.4 Problems found (each one blocks automation)
1. **No registry.** There is no single place to ask "all candidates" or "this person". Every consumer re-reads five per-state folders and must know each state's quirks.
2. **Inconsistent identifiers.** `id` is the state Division of Elections number in Florida (`90433`) and a name slug elsewhere (`JB_Pritzker`, `Kathleen_Courtney__Kathy__Hochul`). `tip_page_id` is either a FEC-style id (`H6MI10276`) or a TIP slug (`GOV-MI-BENSON`). There is no stable LLF id that survives a re-pull. Portrait files are named by `id`, so renaming a slug orphans an image.
3. **Schema drift.** FL lacks `tip_name`, `write_in` and `note`; later states have them. Fields are present on every row but mean different things (`state_url` is a per-person page in Florida and a list page elsewhere).
4. **Provenance and trust are per state, not per record.** Whether the roster is official lives in `STATES[...]["official"]` and the `source_note` string. A directory spanning states cannot tell which listings are official (FL, MI, NJ) and which are secondary (IL, NY, from Green Papers because the board's site returned 403).
5. **Duplicate shapes.** `roster.json` and `candidates.json` carry the same people. They can disagree.
6. **Grades have no summary.** To answer "is this person graded" a consumer walks six issue objects. There is no `graded_count` field, so "not graded" versus "graded" is recomputed everywhere (and "not graded" must never read as zero).
7. **Same person, several TIP profiles.** The publishing rules already note this (Donalds has a governor and a congressional profile). Nothing in the data models it, so the build has to special-case it.
8. **Person-level data is copied instead of read from TIP.** TIP already holds, per candidate: party, incumbency, photo, Ballotpedia and website links, finance snapshot, issue ratings and race entries (the Michigan export alone has 217 candidates, 1,302 issue-rating rows, 74 race entries and 18 races). LLF re-copies slices of that into its own files, so the two drift.
9. **Not in the handoff ledger.** The `STATE_LEDGER.json` template has no "registry" stage, so a new state can be finished without its candidates ever reaching the directory.
10. **Liabilities if exposed naively.** Two of five states (Illinois and New York) use secondary rosters from Green Papers because the state board sites returned 403, and Michigan and New Jersey add write-ins from the same source. The state pages for Illinois and New York are currently indexable (checked in `dist/`: no `noindex` on any state hub; only the dark-horse status page sets it), with an on-page "not an official list" note. A directory that lists those people as plain rows would lose that note unless every record carries its roster basis.

## 3. Principle

**TIP owns the person; LLF owns the ballot and the reporting.** Two layers, one registry:

| Layer | Owner | Examples |
|---|---|---|
| Person-level facts | **TIP** (read from the TIP export; never retyped on LLF) | display name, party, incumbency, photo, Ballotpedia and website and social links, finance snapshot, six issue ratings, verification status |
| Ballot-level facts | **LLF** (from the official or secondary roster) | on the November ballot or not, office and district, running mate, write-in, withdrawn or disqualified, roster basis and source, state record URL |
| Reporting links | **LLF** (computed) | LLF stories that mention the person, LLF state page for the race |

A candidate row on LLF therefore shows a few ballot facts and sends the reader to TIP for everything else. No LLF page is created per person. If TIP lacks something (a profile, a photo, a link), the fix is made **on TIP** (with the owner's approval for any TIP write, as in Illinois and Michigan) and LLF picks it up on the next export. LLF does not keep a shadow copy of what TIP should hold.

Collection scripts keep writing per-state files (they work and are tested). A normalizing step merges them with the TIP export into a registry; every surface reads the registry, never the raw files. Adding a state then means producing its files and running one command.

## 4. Specification

### 4.1 Registry record (data only)
Stored at `data/candidates/<ST>.json` (one file per state, generated and committed) and merged into `dist/data/candidates.json` at build time. Schema file: `data/candidates/candidate.schema.json` (JSON Schema draft 2020-12).

```json
{
  "schema": 1, "state": "MI", "cycle": 2026, "generated_at": "2026-10-31T12:00:00Z",
  "tip_export_as_of": "2026-10-28",
  "roster": {"basis": "official", "label": "Michigan Department of State Official Candidate Listing",
             "url": "https://mi-boe.entellitrak.com/...", "read_at": "2026-10-28", "limitations": ""},
  "candidates": [ {
    "llf_id": "MI-S-el-sayed-abdul",
    "name": "Abdul El-Sayed",
    "sort_name": "El-Sayed, Abdul",
    "office": "senate", "district": null, "race_key": "2026-S-MI",
    "party": {"code": "DEM", "letter": "D", "label": "Democratic Party"},
    "incumbent": false,
    "running_mate": null,
    "ballot": {"status": "qualified", "write_in": false, "withdrawn": false, "disqualified": false, "note": ""},
    "ids": {"tip_candidate_id": 8056, "tip_slug": "S6MI00418", "fec": "S6MI00418"},
    "tip": {"url": "https://theissuesparty.org/candidates/S6MI00418", "http": 200, "checked_at": "2026-10-28",
            "graded_count": 0, "profile_status": "seed"},
    "tip_photo": {"available": true, "filename": "..."},
    "links": {"state_record": "https://...", "ballotpedia": "...", "website": "..."},
    "gaps": ["tip_profile_missing"],
    "coverage": ["michigan-senate-delta-october-2026"],
    "provenance": ["roster:mi_boe_2026-10-28", "tip_export:2026-10-28"]
  } ]
}
```
Name, party, incumbency, photo flag and links come from the TIP export. Running mate, ballot flags, roster basis and the state record URL come from the roster. `coverage` and `gaps` are computed.

Rules:
- The row's public link is `tip.url`. If `tip.http` is not 200 the row shows the existing "No TIP record yet" text and the gap is reported (R1).
- Grades are **not** copied into the registry; only `graded_count` (null when there is no profile, zero when the profile has no graded issue). The grades themselves are read on TIP, where "a grade is cited only from the profile that shows it" is already enforced.
- Portraits: LLF's licensed portrait files stay for the state pages. The directory shows a monogram unless decision D4 allows the TIP photo.
- No win probabilities, market prices, polling or money in any public registry field.
- A disqualified or withdrawn person stays in the registry with the flag and is not listed publicly unless a report refers to them. `held: true` removes a person from every surface without deleting the record.

### 4.2 Race record (small)
`data/candidates/races.json`: `race_key`, `state`, `office`, `district`, `llf_url` (state page), `tip_url` (`https://theissuesparty.org/races/<race_key>`), `candidate_ids[]`, `roster_basis`. Generated.

### 4.3 Generated outputs (all on LookLearnFind; no per-candidate pages)
| Output | Path | Notes |
|---|---|---|
| Directory index (replaces the empty state) | `/find/candidates/` | State tiles with counts and as-of, then a filter bar (state, office, party, graded or not) over a table. Each row: name, party letter, office and district, a "View on TIP" link, a link to the LLF race page, and a badge when the roster basis is not official. Filters run client-side on `/data/candidates.json`. Default order: state, office, district, surname. **No sort by grade, market or money** |
| Per-state list | `/find/candidates/<state-slug>/` | The same table for one state, grouped by race, with the roster basis and limitations line. A list, not a profile |
| Machine feed | `/data/candidates.json`, `/data/candidates.csv` | Registry fields without provenance; documented on the Methods page |
| Search | `search-index.json` entries `t="candidate"` | Name, office, state, party; the result URL is the **TIP profile** |
| Topic and sidebar | `/topics/candidates/` and the state lens | Counts and "all candidates in <State>" links from the registry |
| State pages | existing hub, governor, Senate, House and district pages | Unchanged in phase 1; read the registry in phase 3 so there is one source |

The state pages already carry a "View on TIP" button on each candidate card; the directory reuses the same component and link rule.

### 4.4 Builder: `tools/elections/build_registry.py <ST>|--all`
Pure function of repository files, idempotent, no network.
1. Read the state's `roster.json`, `candidates.json`, `tip_export/` (candidates, race entries, issue ratings, races) and `portraits.json`.
2. Take ballot facts from the roster and person facts from the TIP export; write `data/candidates/<ST>.json`.
3. Compute `graded_count`, `coverage` (scan `content/learn/*.html` for the person's TIP URL) and `gaps`.
4. Validate (section 6); exit non-zero on error; print added, removed and changed rows against the previous file so a refresh is reviewable.
5. `--all` also writes `data/candidates/races.json`.

**IDs.** `llf_id = <ST>-<H|S|G>[<dd>]-<surname>-<given>` lower-cased ASCII; ties get a numeric suffix recorded in `data/candidates/id_overrides.json`. Once published the id never changes; renames add an alias. With no LLF person pages the id is only an internal key.

### 4.5 Using TIP for missing information (the gap loop)
A gap is anything the directory wants and the TIP export lacks.

| Gap | Detected by | Fix |
|---|---|---|
| `tip_profile_missing` (on the ballot, no TIP profile; today 4 of 329) | `tip.http` not 200, or no row in the export | Add to the state's TIP fix list; the owner approves; apply as in `docs/michigan/TIP_FIX_LIST_FOR_APPROVAL.md`; re-export |
| `tip_entry_missing` (profile exists, no race entry) | race entries compared with the roster | Same list |
| `tip_entry_review` (entry at `review`, so TIP's public race page is empty) | race entry status | The owner promotes it to `active` |
| `tip_photo_missing`, `tip_links_missing` (the Michigan export has 38 of 217 without a photo and 211 without a campaign website) | empty photo, website or Ballotpedia fields | Reported only; not a blocker; belongs to TIP's own enrichment. LLF never adds its own copy |
| `profile_unverified` | TIP verification status `needs_review` or empty | Shown to the editor, not to the public |

The builder writes `productions/2026/<ST>/gaps.csv`, and the Claude session turns it into the TIP fix list. A state is not done until the list is empty or each remaining gap is accepted by the owner.

## 5. Automation: how a state reaches the directory

Add one stage and one task to the handoff template (`docs/production/templates/state/STATE_LEDGER.template.json`):
- stage `registry`: "Candidate registry built and validated (data/candidates/<ST>.json)", evidence `data/candidates/<ST>.json`.
- Claude task: `python tools/elections/build_registry.py <ST>` after `tip_gaps` and `pages`, before `scout`.

Refresh: rebuild whenever the roster, the TIP export or portraits change; `handoff.py stamp` runs the builder and fails if the registry is older than its sources. The TIP export step (`scripts/export/state-packet.mjs`) stays the only way TIP data enters LLF. After the election a `result` field can be added from official results in a later schema version; until then the directory shows the ballot only.

ChatGPT packages need no change; the registry is Claude-side data.

## 6. Validation (all must pass before `--strict` succeeds)
1. Schema validation of every record.
2. Unique `llf_id`; unique `(state, office, district, party, name)`.
3. Every candidate's `race_key` exists in `races.json`.
4. Every listed candidate (not held, not disqualified) has `tip.http` equal to 200, or the build reports an R1 violation and the row says "No TIP record yet".
5. A roster basis other than official requires non-empty `limitations`, and the directory prints it.
6. No public field contains a probability, a market price, a poll number or a dollar amount.
7. Registry count per state equals the `candidates.json` count minus disqualified and held.
8. No LLF URL under `/find/candidates/` resolves to a single-person page (guards the chosen design).
9. The registry is not older than the TIP export it was built from.

## 7. Migration plan
| Phase | What | Effort | Result |
|---|---|---|---|
| 1 | `build_registry.py` for the five states, schema, validation, `gen_candidates()` with the index, per-state lists and the feed; search entries that link to TIP | 1 to 2 days | `/find/candidates/` lists all 329 people with working TIP links and honest roster labels |
| 2 | Topic and sidebar integration; `gaps.csv` per state; ledger stage and template task; `tests/test_candidate_registry.py` | 1 day | A new state needs its raw files and one command; gaps become the TIP fix list automatically |
| 3 | Switch `elections.py` to read the registry; retire the duplicate `roster.json` shape | 1 to 2 days | One source of truth |

Phase 1 fixes the page you are looking at and changes no existing page.

## 8. Rules that carry over (do not relax)
Neutral reporting: alphabetical within race, no ranking, no endorsement, no market or poll data in the directory. R1 and R2 apply. Grades are TIP's and appear on TIP. "Not graded" is never zero. Official versus secondary rosters are labeled wherever shown. Disqualified and withdrawn people are not listed unless a report refers to them. No Oxford comma in generated text.

## 9. Decisions
- **Resolved by the owner (2026-10-31):** no per-candidate LLF pages; rows link to TIP; TIP supplies missing person-level data.
- **D2.** The existing Illinois and New York state pages are indexable with a disclaimer. The directory rows from those rosters carry a visible "not an official list" badge (specified above). Should the per-state lists for those two states be kept out of search engines until the official lists are read? Recommendation: yes.
- **D3.** Public JSON and CSV feed: yes or no? Recommendation: yes.
- **D4.** Photos in the directory: use TIP's photo if TIP serves it at a stable public URL we may hotlink, or keep monograms and let each row's TIP link show the photo? Recommendation: monograms first; add TIP photos only if TIP confirms hotlinking and licensing.

## 10. Acceptance
`python build.py --strict` reports 0 violations; `/find/candidates/` lists every qualified candidate in the registry with correct counts per state and every row links to its theissuesparty.org profile; no page exists per candidate on LLF; a name search returns the person and lands on TIP; rows from secondary rosters carry the badge; deleting `data/candidates/<ST>.json` and re-running the builder reproduces it byte for byte; `tests/test_candidate_registry.py` passes; the empty message appears only if the registry is empty.
