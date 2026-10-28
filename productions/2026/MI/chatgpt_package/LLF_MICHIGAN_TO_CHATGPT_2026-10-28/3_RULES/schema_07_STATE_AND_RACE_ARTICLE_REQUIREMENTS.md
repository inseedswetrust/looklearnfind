# 01 — Claude assignment: LLF Florida election article schemas, sourcing, and research handoff

**Version:** 2026-10-22 · **Purpose:** design article types and rules, audit TIP's actual database, and return a structured research commission to ChatGPT. This is a SPEC, not approval to publish.

## Locked scope and authority
- **Florida pilot only**, scalable to all 50 states + DC.
- **Only Governor, U.S. Senate and U.S. House candidates.** Explicitly EXCLUDE amendments, referenda, Cabinet, state legislature, judges, voting-mechanics guides and other ballot measures.
- **One state short-form video** plus long-form LLF election coverage; do not produce videos for Delta, Spending or Dark Horse yet. Other series remain future article/video opportunities.
- The website/TIP database is the first inventory of people, races, campaign finance, TIP six issue ratings, published profiles, source links, issue methodology and available features. It is NOT automatically authoritative for who is qualified: compare with the Florida Division of Elections and official candidate rosters.
- No new TIP ratings or score calculations until Claude documents current methodology, data completeness and legitimacy. Display pre-existing ratings only with issue definition, methodology, as-of and data availability. Never invent missing scores or conflate unknown with zero.
- Neutral reporting: describe and cite candidate conduct and attributed editorial positions, do not endorse or rank candidates or use political affinity to infer policy views. Editorial spotlights must use published, consistent newsworthiness criteria.
- Every externally supplied number should carry unit, reporting period, retrieved timestamp, as-of timestamp, provenance and caveats.

## Your first job: inspect TIP and LLF
Inspect existing database, code and public routes rather than guessing table/field names. Confirm connections securely; do NOT send credentials or secrets in the return packet. Return:
1. Actual candidate/race data sources and normalized crosswalks: internal candidate ID, FEC ID (when present), race ID, office, district, current participation, candidate URL, party, source and verification timestamp.
2. Actual TIP issue rubric: list exactly **all six issues** and approved definitions/labels. Earlier draft mentioned five, so resolve by reading the DB / implemented website. Do NOT assume an invented sixth.
3. Exact per-candidate issue fields available: score value, scale/denominator, confidence, coverage count, source, last computed, missingness, and whether values are provisional/approved.
4. Actual campaign finance data fields currently stored and freshness/cutoff.
5. TIP pages/features available **today**: follow/save, compare, ping candidate, Permanent Record, issues or whatever truly exists; don't link unfinished features as live.
6. LLF repo/CMS/content model, images, site navigation, SEO, publication workflow; propose reuse rather than introducing competing structures.
7. Florida roster reconciliation: do not silently add/drop candidates; output discrepancies with a status and source.
8. Florida district boundary vintage and Senate special-election designation if relevant.

## Agreed article schema family

### A. State overview / evergreen guide — one per state
**Slug** `/elections/2026/florida/` or existing LLF convention; canonical evergreen state hub.
**Role:** complete, accessible, frequently updated index of races/candidates within scope; factual context and pointers to deeper reading.
**Required modules in order:**
1. Hero: Florida 2026, as-of stamp, number of included governor/Senate/House contests and candidates; scope explicitly defined.
2. **State Board**: visual complete matrix for governor, Senate and every congressional district in scope; candidate names and party in each tile; scalable poster/interactive table and clean screenshot/graphic export.
3. Highlights summary: explain *why these specific race stories appear* (new spending, market movement, unusual primary, explicit issue records, etc.) without an editorial preferred winner.
4. Governor candidate section; Senate candidate section; House races in numeric district order.
5. Each candidate: full name, party/ballot designation, incumbency, official/campaign/FEC identifiers, TIP candidate link, **six TIP issue ratings if actually available** (with visible missing-data handling), fundraising-to-date (period as labeled), market quote if exact current contract exists.
6. At-a-glance financial/market snapshot with timestamp and methodology. No false side-by-side for incompatible periods/contracts.
7. Spotlight narratives 3–5 races, chosen after new research and justified with objective interest signals (not affiliation).
8. **Explore on TIP** cards linking available functions (candidate page, issue breakdown, records, follow/compare where live).
9. Sources, limitations, correction log, last refreshed, author/reviewer and material-change history.
No ballot measures; no generic voting guide.

### B. Race detail article — governor, Senate or district House
**Slug** reuse current routing; e.g. `/elections/2026/florida/house-07/`.
**Required modules:** exact seat/office/contest date and ballot status; roster of all participating candidates, not only two; candidate comparison grid with neutral equal treatment; market instrument(s) and dated prices; candidate committee totals (receipts/disbursements/cash on hand, dates); outside expenditures distinct from direct contributions; six TIP issue ratings with approved scale, missingness and clickable rubric/underlying evidence; positions with verbatim quotations where independently verifiable; relevant events timeline; source ledger; linked TIP pages; unresolved questions.
**Optional modules:** notable primary history; issue-specific legislation for officeholders; candidate controversies or ad stories only if high-quality sourcing and context available.
**Do not** count absence of cosponsorship as opposition; do not call a forecast a fact.

### C. LLF reported feature / spotlight article — only when newsworthy
**Slug** `/learn/{descriptive-event-slug}/` or existing LLF convention.
**Core modules:** sharp factual question/headline; why it matters; verified event; documents and two-sided relevant response; financial/market context as applicable; explicitly defined uncertainty; method and cited references; link to state/race guide and TIP candidate records.
**Do not** merely restate the dashboard with no reporting value. Event-based articles may later support Delta / Spending / Dark Horse families, but not separate pilot videos.

### D. Shared evidence/source object (NOT necessarily a new DB table)
Every article gets a source ledger with:
`claim_id, claim_text, entity_id, issue_or_topic, primary_url, document_or_filing_id, excerpt_locator, publisher, event_date, accessed_at_utc, value, unit, date_range, verification_status, discrepancy_note, asset_capture_ref`.
Check whether existing CMS stores this already. Avoid needless extra schema.

## Data points Claude must provide and/or commission
**Mandatory source categories**
- Roster: official Florida qualified candidate list; TIP DB snapshot; FEC candidate crosswalk and filing status; official state district map.
- TIP: **six issue ratings** per candidate; exact issue names, scale, method and primary links for drilldown; candidate fundraising and its as-of/cutoff.
- Finance: FEC committee totals (receipts, individual donations, PAC contributions, disbursements, cash), contribution cutoff/period; **outside spending** by organization, candidate, support vs oppose, date, filing ID; entity relationship to AIPAC/UDP only when documented; state-office finance from Florida appropriate state campaign finance authority.
- Kalshi: official market URL/ticker, instrument description (named candidate vs party contract), bid/ask/last or displayed price **exactly as returned**, timestamp and timezone, market volume/liquidity where available, quote history for delta. Do not present as calibrated win probability.
- Candidate materials: official site, campaign statements, debate/interview clips with rights notes, party, office, social handles when verified, substantive public issue positions with source/time.
- Visual inputs: photo/license log; Florida shape + congressional boundaries; uniform candidates cards; TIP logo/real screenshot; LLF branding.
- Editorial: objective news events; relevant spending and primary dynamics; corrected/contradictory reporting and attributable responses.

**Request for each field:** Claude must mark `IN_DB`, `AVAILABLE_FROM_OFFICIAL_SOURCE`, `THIRD_PARTY`, `NOT_AVAILABLE`, and provide its retrieval location or API plus checked timestamp. Never fill unknown with a guessed value.

## Machine-readable handback assignment (ChatGPT will do research/writing)
Claude should return BOTH:
1. `FLORIDA_RESEARCH_COMMISSION.md` — human-readable explicit research asks with rationale, links, candidates/races to examine, already-known internal facts, verification gaps, priority by data-criticality rather than candidate preference.
2. `FLORIDA_RESEARCH_COMMISSION.json` or CSVs — exportable, including:
- `scope`, `as_of_utc`, `candidate_records[]`, `race_records[]`, `issue_definitions[]`, `issue_ratings[]`, `finance_snapshots[]`, `market_contracts[]`, `candidate_feature_links[]`, `research_tasks[]`, `sources[]`, `unresolved[]`.
- Each `research_task`: `task_id`, `race_id`, `candidate_ids[]`, `question`, `data_fields[]`, `preferred_primary_sources[]`, `existing_data`, `missing_fields`, `required_as_of`, `priority`, `acceptance_test`.
- **Bundle raw export files** from DB only if authorized, excluding secrets/private user data. A markdown-only summary is not enough for large rosters.
- Include issue-rating export **per candidate × six issues**, even when missing; include issue names, score scale, methodology URL, confidence, date.
- Include finance export distinguishing candidate totals from independent expenditures and making reporting periods comparable.
- No fabricated field values or fake URL destinations.
- Claude must add source categories/data fields it finds necessary and explain each addition succinctly.

## After Claude handoff — ChatGPT responsibilities
1. Verify data with current official sources and credible reporting; reconcile conflicts to dated records and mark remaining uncertainty.
2. Write completed State Guide + pertinent Race articles + any approved editorial spotlights in LLF article schema.
3. Decide **which 3–5 Florida races** warrant visual focus based on research; provide objective selection reasons, not predictions or candidate endorsements.
4. Build a **90-second 9:16 storyboard** anchored by the **complete State Board** and moving into verified spotlights. Show the TIP six-issue ratings as a visually prominent module with correct methodology and unknowns; represent all six if legible, otherwise a persistent six-dot key + zoomed full profiles.
5. Create/recommend exact graphics: dimensions, typography, layered editable data overlays, source notations, logos, credits, animation manifest, and versioned assets. Preserve all candidates on the board even if not in focus.
6. Provide Midjourney-ready motion instructions and start/end frame requests for non-evidentiary visual transitions; true numbers, names, rankings, and ballot facts should be rendered deterministically in edit, not generated into video imagery.
7. Prepare approved script and publish pack only after verification/review. No automatic publishing of disputed or incomplete content.

## Editorial constraints and reusable decisions
- Short video's main goal is orient users to ALL races and the six TIP issues without promising 90s of equal commentary per candidate.
- Ratings are highly visible and explicitly **TIP's published methodology**, not proven objective facts. Include date/coverage and clearly identify unscored candidates.
- Distinguish `0`, `unknown`, `not scored`, and `not applicable`.
- No unverified claims that candidates share positions based on Gaza stance, PAC support or party affiliation.
- Do not give short-form airtime on the basis of whose victory is politically desired. Story selection can prioritize verifiable closeness, novelty, documented movements, amount of money or evidence-rich issue disputes.
- Match the site's real branding and preserve original editorial design: paper #f5f2eb; ink #1c1d1b; teal #145b5d; annotation yellow #dfca00. Adapt after inspecting LLF.
- Include clear disclosures for generated illustration/voice, and avoid presenting AI visuals as footage of real events.
- Candidate portraits are licensed/official real photos when legally usable; AI caricatures may be misleading, avoid.
- Preserve exact citations with visible source and date; don't truncate captions or source identifiers inside mobile safe zones.

## Acceptance checklist
- [ ] Governor, Senate, and House only.
- [ ] Full Florida race/candidate coverage; official roster reconciliation.
- [ ] Exactly six TIP issue definitions discovered from live DB/site.
- [ ] All available issue scores and finance data exported with provenance.
- [ ] Missing sources and fields explicitly commissioned to ChatGPT.
- [ ] LLF article templates/schema reviewed against real code.
- [ ] TIP cross-links to live features only.
- [ ] No placeholder or invented Kalshi odds/spending amounts.
- [ ] Future video storyboard/graphics handed back through structured source packet.
