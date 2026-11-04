# 05 Contradictions with the Production Lock and authorization rules (follow-up 8)

Responds to architecture v1 section 10 item 8. The plan itself says it is "NOT implementation authorization"; this file compares it with `CLAUDE.md`, `docs/production/` (lock v2.0, protocol, procedures), `docs/election-build/PUBLISHING_RULES.md` (R1 to R15) and the source registry. "Conflict" means the plan as written cannot be done without breaking a rule; "Gap" means no rule covers it; "Decision" means the owner must choose. Rule numbers are from `PUBLISHING_RULES.md`.

## A. Direct conflicts (the plan as written would break a rule)

| # | Plan text | Rule | Why it conflicts | Resolution options |
|---|---|---|---|---|
| A1 | Sec. 1 and 11: results "may be refreshed independently using versioned, validated static JSON"; open question: "refreshed only with deployments or with approved JSON payloads independently" | `CLAUDE.md`: nothing is published, uploaded or deployed without the owner's explicit authorization recorded per action; R14 | Each independent refresh is an upload to the live site. Without a recorded authorization for each, it breaks the rule | (1) Every refresh is a normal authorized deploy; (2) the owner records a **standing, scoped authorization** (which sources, which states, what cadence, what validation must pass) in the ledger; (3) refreshes are approved in batches. Option 2 needs the owner's words recorded and a visible limit |
| A2 | Sec. 4: "Results at a glance" rows and sec. 8 "no partisan color coding in rankings or charts" | `CLAUDE.md`: no rankings | The plan uses the word "rankings". Row order must follow the existing convention (state, office, district, then surname, "not a ranking") and no chart may rank candidates or states | Remove "rankings" from the spec; keep the existing "order is not a ranking" note |
| A3 | Sec. 6: a candidate row for every candidate in a result | R1 and the strict build | R1 reports a violation when a featured candidate has no TIP profile (five exist today: Bree Taylor, Paul Mailhot, Jonathan Makeley, Eduardo Jose Castillo Nicasio, Kevin Dwire). Results include write-ins and scattering that have neither an FEC ID nor a TIP profile | Owner waiver and a defined label ("No TIP record yet") for result-only rows, or a TIP profile per listed candidate before results show |
| A4 | Sec. 3, 5 and 7: preserved articles "unchanged except for a conspicuous date-context banner" | Corrections discipline; owner authorization to publish; R7 (log changes in the corrections block) | A banner is a change to a published article. It needs authorization and a corrections-block entry; changing `updated` would say the content changed when it did not | Treat the banner as a template element driven by a registry (the article files are not edited); record one dated corrections line per article or a site-wide note; do not change `updated` |
| A5 | Sec. 5: new formats (Living State Election Report, State Results Analysis, Election Signal, Accountability Follow-up) | `docs/schemas/` holds seven schemas; `llf-article-format` skill; "`format:` is a public label, never a schema name"; never overwrite an installed skill without reading | No schema or skill covers these. A new article cannot pass the lock's QA without one | Draft schemas 08 to 11 and update the skill with the owner's approval; use public labels |

## B. Gaps (no rule exists yet)

| # | Gap | Evidence |
|---|---|---|
| B1 | **Results policy.** Nothing governs race calls, "projected", leader language, margins, percent reporting, certification, recounts, county data, historical comparisons or result corrections. The editorial rules forbid win probabilities and causal claims but were written for pre-election reporting. Plan sec. 7 asks for these rules; they must exist before any results are shown | `PUBLISHING_RULES.md` R1 to R15 contain none |
| B2 | **Who may call a race.** Plan: "independent race calls need named source and timestamp". No policy says which organizations are acceptable or whether LLF ever calls a race itself (the lock's neutrality and no-projection posture suggest not) | |
| B3 | **Source approval.** `source_registry.json` has `owner_approved: false` for every source except `tip-db`. Every new results source needs registry entry and owner approval; none is approved | `data/elections/source_registry.json` |
| B4 | **Fact-check for data refresh.** R5 requires a reviewer other than the drafter for articles. Nothing says whether a data snapshot needs a person to approve every refresh or only the first per source | |
| B5 | **Corrections and privacy pages are unfinished.** The plan's "Go to the source" section links to "LLF corrections policy". `/about/corrections/` and `/about/who-we-are/`, and the Privacy, Terms and Disclosures pages, still contain bracketed placeholders (for example `[COMPANY NAME]`, `[ADDRESS]`, `[DATE]`) and are `noindex`. A results launch should not point readers to a placeholder policy | `content/*.html`, built pages |
| B6 | **Follow or subscribe features.** Plan sec. 11 asks about reusing Look Ledger subscription and follow features. The Ledger is live but empty, its privacy and terms pages are placeholders, and the newsletter does not send mail | `docs/DEPLOY.md`, page content |

## C. Scope and authorization decisions for the owner

| # | Decision | Why it matters |
|---|---|---|
| C1 | **Scope beyond Governor, Senate and House.** `CLAUDE.md` limits scope to those three offices. The plan's "governing / accountability", "What happens next ... governing actions", `/states/{state}/` ("government, consequences") and Accountability Follow-ups reach into state government, legislation and promises | Requires an explicit scope change in `CLAUDE.md` and `PUBLISHING_RULES.md` before work starts |
| C2 | **Pennsylvania as the pilot.** The plan chooses it because it has articles and district routes. Under R15 its roster is unofficial (Green Papers) and no Pennsylvania official results source has been identified or tested; Michigan and New Jersey rosters are official and Florida's is official (but Florida's pages are the oldest and structurally different) | A results pilot on an unofficial roster risks omitted or misnamed candidates and "complete" claims the rules forbid |
| C3 | **Standing authorization** for scheduled refreshes (see A1) | |
| C4 | **Nav change.** `docs/BRAND.md` fixes the main navigation (Politics, Economy, Society, Everyday Life, then Topics, Latest, Find, About). Adding Elections as a top-level item changes the brand structure | Owner approval; alternative is a nested path and a Politics landing card |
| C5 | **Name of the section and components.** The plan avoids "State Election Ledger" because of the Look Ledger and TIP Issues Ledger; "Election Signals" and "What Happens Next" are untested names | Owner and brand decision |
| C6 | **Heading and title change on seven indexed hub pages** (from "State of the Race" to "{State}: what changed and what comes next"). Not a rule conflict; it changes the indexed search target and "what changed" is inaccurate before results exist | Make the heading phase-dependent; decide whether the old title text stays in the `<title>` |

## D. Workflow rules that the rollout must respect
- **One Claude session writes to a state at a time** (`handoff.py`, ledger). A Florida refactor or a cross-state layout change touches all seven states and needs the ledgers to be quiescent and stamped first.
- **Handoffs are generated from the ledger**, never hand-written; new gates should be added as ledger stages and lanes so ChatGPT and Claude chats receive generated packages.
- **Fact-check independence (R5, R14)** applies to the new article types and to signals.
- **Reported numbers are attributed (R3) and same-source comparisons are labeled (R4).** "What changed" statements need a sourced baseline.
- **Kalshi snapshots** stay dated and labeled as market quotes, never as outcomes or probabilities; the existing wording ("not forecasts or vote shares") should be reused on archived panels.
- **R15:** a source that blocks automated access is recorded and never circumvented; four state sites already are or may be blocked (Illinois, New York, Minnesota; Pennsylvania's list was not found).
- **R9 and the video lock** are unaffected unless a results video is proposed; any video would follow the lock (script first, no render without an explicit owner request).
- **Do not move or rewrite returned discovery material** (for example `docs/illinois/`); the audit and this design folder are new folders.

## E. Plan statements that are consistent with the rules (no action)
Preserve all URLs and canonicals; keep the hosting-managed robots; no LLF candidate pages and TIP as the candidate destination (R1); no manufactured signals; do not infer coverage for other states; separate leader, call and certification; owner approval before deploy; staged preview; independent fact-check; preserve dated market artifacts; decline to use "State Election Ledger"; avoid percent-reporting inventions.
