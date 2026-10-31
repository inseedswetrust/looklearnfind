# Candidate directory: audit and specification

Written 2026-10-31. Audience: Claude Code sessions that build and refresh state data, and whoever approves the page design. This file does two things: it records how candidate information is stored today (section 1 to 3) and it specifies how it should be stored so that `/find/candidates/` and every other surface fills itself (section 4 onward).

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
8. **No editorial disclosure.** A Find listing promises "why it is here, what we checked and any commercial relationship". The election data has no fields for those, so a generated listing cannot make the promise honestly without them.
9. **Not in the handoff ledger.** The `STATE_LEDGER.json` template has no "registry" stage, so a new state can be finished without its candidates ever reaching the directory.
10. **Liabilities if exposed naively.** Two of five states (Illinois and New York) use secondary rosters from Green Papers because the state board sites returned 403, and Michigan and New Jersey add write-ins from the same source. The state pages for Illinois and New York are currently indexable (checked in `dist/`: no `noindex` on any state hub; only the dark-horse status page sets it), with an on-page "not an official list" note. A directory that lists those people as plain rows would lose that note unless every record carries its roster basis.

## 3. Principle

**One canonical registry, many generated views.** Collection scripts keep writing per-state files (they work and are tested). A new normalizing step merges them into a registry with a stable schema. Every surface (Find, search, state pages, sidebar, JSON feed, stories) reads the registry, never the raw files. Adding a state then means producing its files and running one command; the directory page appears without editing a template.

## 4. Specification

### 4.1 New content type: `candidate` record (data, not prose)
Stored at `data/candidates/<ST>.json` (one file per state, generated, committed) and merged into `dist/data/candidates.json` at build time. Schema file: `data/candidates/candidate.schema.json` (JSON Schema draft 2020-12).

```json
{
  "schema": 1,
  "state": "MI",
  "cycle": 2026,
  "generated_at": "2026-10-31T12:00:00Z",
  "roster": {
    "basis": "official",                  // official | secondary | mixed
    "label": "Michigan Department of State Official Candidate Listing",
    "url": "https://mi-boe.entellitrak.com/...",
    "read_at": "2026-10-28",
    "limitations": ""                     // required when basis != official
  },
  "candidates": [ { ...candidate... } ]
}
```
Candidate:
```json
{
  "llf_id": "MI-S-el-sayed-abdul",        // stable: <ST>-<office letter>[district]-<surname>-<given>; never reused; never changed after publication
  "name": "Abdul El-Sayed",
  "sort_name": "El-Sayed, Abdul",
  "office": "senate",                     // governor | senate | house
  "district": null,                       // integer for house
  "race_key": "2026-S-MI",                // TIP race key; the join to races
  "party": {"code": "DEM", "label": "Democratic Party", "letter": "D"},
  "incumbent": false,
  "running_mate": null,
  "ballot": {"status": "qualified", "write_in": false, "withdrawn": false, "disqualified": false, "note": ""},
  "ids": {"fec": "S6MI00418", "state_record": "…", "tip_slug": "S6MI00418"},
  "links": {
    "tip_profile": "https://theissuesparty.org/candidates/S6MI00418",
    "tip_checked_at": "2026-10-28T20:00Z",
    "tip_http": 200,
    "other_tip_profiles": [],             // same person, other offices (e.g. a House profile for a governor candidate)
    "state_record": "https://…"
  },
  "issues": {
    "graded_count": 0,                    // number of the six issues with a grade; null when no profile
    "grades": {"data_bill_of_rights": {"state": "not_graded"}},
    "as_of": "2026-10-28"
  },
  "portrait": {"file": "S6MI00418.jpg", "license": "CC BY-SA 4.0", "credit": "…", "monogram": false},
  "listing": {                            // the Find-listing disclosure, so the promise on the page is real
    "why": "On the November 3, 2026 general election ballot for U.S. Senate in Michigan, per the official listing.",
    "checked": ["Name, party and office against the official listing (read 2026-10-28)", "TIP profile returns HTTP 200 (2026-10-28)"],
    "limits": ["Grades are TIP's, shown only where the profile shows them", "Listing says nothing about positions beyond the TIP record"],
    "commercial": "No commercial relationship.",
    "review": "auto"                      // auto | reviewed (a person read it) | held (do not publish)
  },
  "coverage": ["michigan-senate-delta-october-2026"],   // LLF story slugs that mention this person; computed, never hand-typed
  "provenance": {"sources": ["roster:mi_boe_2026-10-28", "tip_export:2026-10-28", "portraits:2026-10-28"], "built_by": "tools/elections/build_registry.py"}
}
```
Rules for the record:
- Public fields never include win probabilities, market prices, polling or fundraising totals. Those stay in their reports with their own as-of and caveats. The directory is a **who is on the ballot and where to read the record** surface.
- `graded_count` null means no TIP profile; zero means a profile with no graded issues. "Not graded" is never displayed as a score.
- `listing.review: held` removes a person from every generated surface (used for a roster error or a legal issue) without deleting the record.
- A disqualified or withdrawn candidate stays in the registry with the flag and is **not** listed publicly unless a report refers to them.

### 4.2 Race record (small, for linking and counts)
`data/candidates/races.json`: `race_key`, `state`, `office`, `district`, `llf_url` (state page), `tip_url`, `candidate_ids[]`, `seat_note`, `primary`, `roster_basis`. Generated from the same sources.

### 4.3 Generated outputs
| Output | Path | Notes |
|---|---|---|
| Directory index (replaces the empty state) | `/find/candidates/` | State tiles with counts and as-of; a filter bar (state, office, party, has portrait, graded or not) over a table; filters are client-side on `/data/candidates.json`; default order: state, office, district, then surname. **No sort by grade, market or money.** If the registry is empty the old empty message still shows |
| Per-state directory | `/find/candidates/<state-slug>/` | All qualified candidates for the state grouped by race with links to the LLF state page, the TIP profile and the state record. Carries the roster basis and limitations line |
| Per-candidate listing | `/find/candidates/<state-slug>/<llf-slug>/` | The standard Find layout filled from `listing` (why, checked, limits, what to know, disclosure line), portrait with credit, TIP link, race link, stories that mention them. `noindex` until `listing.review` is `reviewed` **or** `roster.basis` is `official` (decision D2) |
| Machine feed | `/data/candidates.json`, `/data/candidates.csv` | Same fields as the registry minus internal provenance; documented on the Methods page |
| Search | `search-index.json` entries `t="candidate"` | Name, office, state, party, race; added in `write_search_index()` |
| Sitemap and structured data | `sitemap.xml`, JSON-LD `Person` on listing pages | Only for indexable listings |
| Topic and sidebar | `/topics/candidates/` and the state lens | Reads `coverage` and counts from the registry |
| State pages | existing hub, governor, Senate, House, district pages | Continue to render from per-state files in phase 1; switch to the registry in phase 3 so there is one source |

### 4.4 Builder: `tools/elections/build_registry.py <ST>|--all`
Pure function of repository files, idempotent, no network.
1. Read `roster.json`, `candidates.json`, `portraits.json`, `tip_export/`, `markets.json` (race membership only) for the state.
2. Normalize into 4.1 with the id rules below; write `data/candidates/<ST>.json`.
3. Compute `graded_count`, `coverage` (scan `content/learn/*.html` for TIP profile URLs and `[[c:…]]`), `listing` text from templates by `roster.basis`.
4. Validate (section 6). Exit non-zero on any error; print a diff summary against the previous file (added, removed, changed) so a refresh is reviewable.
5. `--all` also writes `data/candidates/races.json`.

**IDs.** `llf_id = <ST>-<H|S|G>[<dd>]-<surname>-<given>` lower-cased ASCII with hyphens; ties break with a numeric suffix recorded in `data/candidates/id_overrides.json`. Once a page is live the id never changes; renames add an alias, the same rule TIP uses for profiles. Portrait files are renamed to `<llf_id>.jpg` in phase 2 with a redirect map.

### 4.5 Build integration (`build.py`)
- `gen_candidates()` runs after `load_content()`; reads `data/candidates/*.json`; writes the pages and feeds above using existing components (`cards()`, `page_head()`, `shell()`).
- `gen_find()` stays as is for non-candidate types. For `type: candidate` it shows generated listings **and** any hand-written `content/find/` candidate files (an editor can still write one, and a hand-written file with the same `llf_id` overrides the generated listing).
- Add a build check: the registry must not be older than the state files it was built from (compare `generated_at` with each source's `as_of`), otherwise `--strict` fails with the state named.

## 5. Automation: how a state reaches the directory

Add one stage and one task to the handoff template (`docs/production/templates/state/STATE_LEDGER.template.json`):
- stage `registry`: "Candidate registry built and validated (data/candidates/<ST>.json)", evidence `data/candidates/<ST>.json`.
- Claude task: `python tools/elections/build_registry.py <ST>` after `pages` and before `scout`.

Refresh cadence per state: rebuild when any of roster, TIP export, portraits change (the ledger's `stamp` step runs the builder and fails if the registry is stale). After the general election, a `status` field per candidate (`won`, `lost`, `runoff`) is added from official results in a later schema version; until then the directory shows the ballot only.

The generated Claude kickoff and ChatGPT packages need no change: the registry is Claude-side data. ChatGPT only sees the `linkmap` Claude already provides.

## 6. Validation (must all pass before `--strict` succeeds)
1. Schema validation of every record against `candidate.schema.json`.
2. Unique `llf_id`; unique `(state, office, district, party, name)`.
3. Every candidate in a published race has `race_key` that exists in `races.json`.
4. `tip_http == 200` for every record shown as linked; otherwise the record shows "No TIP record yet" and the build reports an R1 violation (existing rule).
5. `roster.basis != official` requires non-empty `limitations`, and the page prints it.
6. No public field contains a probability, market price, poll number or dollar amount.
7. Counts: registry candidates per state equal `candidates.json` length minus disqualified and held.
8. Per-candidate listings for a `secondary` roster are `noindex` (decision D2), and every directory row from such a roster shows the limitation.

## 7. Migration plan
| Phase | What | Effort | Result |
|---|---|---|---|
| 1. Quick win | `build_registry.py` for the five states, schema, validation, `gen_candidates()` with the index, per-state directories and the JSON feed; search index entries. No per-person pages yet | 1 to 2 days | `/find/candidates/` shows all 329 people, filterable, with honest roster labels |
| 2. Listings | Per-candidate pages, JSON-LD, sitemap, topic and sidebar integration, rename portraits to `llf_id`, redirect map | 1 to 2 days | Search finds a candidate; each has a page |
| 3. One source | Switch `elections.py` to read the registry; delete the `roster.json` duplicate or generate it from the registry; add the ledger stage and template task; add `tests/test_candidate_registry.py` | 1 to 2 days | A new state needs only its raw files and one command |

Do phase 1 first: it fixes the page you are looking at and does not change any existing page.

## 8. Rules that carry over (do not relax)
Neutral reporting: the directory is alphabetical within race, no ranking, no endorsement, no market or poll data. R1 and R2 apply to generated listings. Grades only from the profile that shows them; "not graded" is never zero. Official versus secondary rosters are labeled on every page that shows them. Portraits are licensed or monograms, with credit. Disqualified and withdrawn people are not listed unless a report refers to them. No Oxford comma in any generated text; the template strings are checked by the existing copy test.

## 9. Decisions for the owner
- **D1.** Per-candidate Find pages (329 and growing), or directory and state pages only? Recommendation: build them, but `noindex` the ones with only a monogram and no reviewed listing.
- **D2.** The existing Illinois and New York state pages are indexable with a disclaimer. Should the new per-candidate listings from those rosters be indexable too? Recommendation: no, keep them `noindex` until the official list is read; consider the same for the state pages.
- **D3.** Public JSON and CSV feed: yes or no? Recommendation: yes; it matches the "show its receipts" brand and costs nothing.

## 10. Acceptance
`python build.py --strict` reports 0 violations; `/find/candidates/` lists every qualified candidate in the registry with the right counts per state; a name search returns the person; per-candidate listings from secondary rosters are `noindex`; deleting a state's `data/candidates/<ST>.json` and re-running the builder reproduces it byte for byte; `tests/test_candidate_registry.py` passes; the empty message appears only if the registry is empty.
