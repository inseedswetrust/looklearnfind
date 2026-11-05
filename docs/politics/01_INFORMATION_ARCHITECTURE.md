# 01 — Politics information architecture

## North star
Politics becomes an active, source-first reporting desk with three pillars: The Record (results and state retrospective), The Daily Signal (daily reporting and related media), and The Accountability Desk (documented positions, commitments, leadership developments, and records). Supporting recurring formats: State of the Record, Follow the Money, Election Signals, Go to the Source. Keep archived `State of the Race` articles under their existing URLs and original labels, with contextual historical banners.

## Main-pane layout `/politics/`
1. Breadcrumb, eyebrow `POLITICS / THE PUBLIC RECORD`, headline `Power changes hands. The record continues.`
2. Featured `The Daily Signal` with dateline, 3 verified highlights, links to evidence, daily article and 2 video slots. Do NOT fabricate counts or publish unpublished assets.
3. `Follow the story` four-pane editorial index: Election 2026, Accountability Desk, Follow the Money, State of the Record.
4. `Explore a state`: state selector showing the seven built states; do not falsely imply nationwide LLF state coverage.
5. `The Record`: latest state reports with result status badges and source-as-of date.
6. `On our radar`: current evidence-led developing coverage (never stale pre-election polls shown as current).
7. `Watch / Read / Verify`: paired shorts and long-form stories, authentic citations and original records.
8. `Keep looking`: newsletter / source submission CTA and links to source directory.

Sidebar remains owned by global generator (desktop rail and mobile slide-in drawer). Site-level category nav remains available throughout. Page-only section anchors may appear in global rail; avoid duplicate right rail.

## Proposed routes (keep existing indexed routes)
| Route | Purpose | Status |
|---|---|---|
| `/politics/` | New central desk | Existing URL, redesign |
| `/politics/daily/` | Dated briefs index | New proposal |
| `/politics/daily/YYYY-MM-DD/` | Daily Signal report | New proposal |
| `/elections/` | Permanent election archive | New; previously 403 |
| `/elections/2026/` | National election index with *covered* states | New; previously 403 |
| `/elections/2026/{state}/` | State living report | Existing seven URL paths; update in place |
| `/elections/2026/{state}/governor/`, `/senate/`, `/house/`, `/house/{n}/` | Original race pages | Preserve all existing paths; no new Senate race where none occurs |
| `/politics/accountability/` | Cross-state/issue directory | New proposal |
| `/politics/accountability/leadership-2027/` | Evidence-based leadership position tracker | New proposal |
| `/politics/money/` | Spending investigations index | New proposal; curated, not a redundant copy of articles |
| `/learn/{slug}/` | Full sourced articles | Preserve indexed originals |
| `/threads/{slug}/` | Existing curated threads | Preserve; connect political articles through generator/discovery mapping |
| `https://theissuesparty.org/candidates/{fec_id}` | Candidate permanent record | External deep link, no LLF duplicate |
| `https://theissuesparty.org/parties` | TIP Action Party discovery | External, separate advocacy context |

## Temporal model
- Pre-election: `State of the Race` including candidate/issue/finance context.
- Counting: `State Election Report` with observed vote totals, explicit unofficial and race-call status.
- Certified: verified results archive, state postmortem, retrospective signals.
- Governing: `State of the Record` focused on actions and commitments; 2026 results remain permanently linkable.
- Do not promote current polls or prediction-market prices as results or current analysis after the election.

## SEO
- State postmortems: unique state-specific analysis, statewide/district result facts, original source links, update log, prominent links to TIP candidate profiles. No mass-thin pages or duplicate boilerplate.
- Retain all existing race/story canonical URLs and verify metadata and breadcrumb JSON-LD. Add `Article` to editorial reporting and appropriate `Dataset` / `ItemList` to machine-readable data where valid; never imply verified data in missing fields.
- Add hubs and the daily editions to search-index.json, as current hub pages are not indexed in the client-side search.
- Release in seven-state waves first, then add new states based on source verification and editorial capacity.
