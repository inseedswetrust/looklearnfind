---
name: llf-factcheck-finalize
description: Independent, claim-driven pre-publication check for LLF election articles: a short claims ledger for the central published claims, publishing rules R1 and R2, quote, grade and image checks, and a READY or BLOCKED result. Use before any story goes live.
---

# llf-factcheck-finalize

**Version** 2.0.0 · **Owner** LLF standards (a reviewer other than the drafter) · **Type** skill plus `tools/qa/factcheck_gate.py`. Claim-driven, not dataset-driven (owner reset 2026-10-24).

## What is checked
Only what the article says. Always: candidate identity and ballot status (Division of Elections roster), names and dates, the headline, the five or so most important material claims, quote accuracy, time-sensitive numbers, the source of every TIP grade, image rights, links, responsive rendering. A disputed or damaging claim needs the original material or court record plus a response or attribution. A market or poll appears only if the story uses it, with source, time and, for markets, party-versus-candidate and quote kind.

## What is NOT required
Finance data coverage. No FEC field, Schedule E or B, donor trace, ad-spend reconciliation or filing deadline is checked unless the article makes that claim, and then only that claim needs a source and period. A story with no finance claim is never BLOCKED for missing finance. A reported figure is cited as reported and not described as audited.

## Ledger (the only mandatory artifact)
`CLAIMS.csv`: `claim,text_location,source_url,source_date,checked_date,status`. Status: VERIFIED, ATTRIBUTED, NEEDS_CONTEXT, UNVERIFIED, REMOVED, REVISED. Optional columns `type`, `evidence_ref`, `reviewer` switch on the typed rules (grade, poll, finance, market, image) for those rows only. The older eight-column ledger (`claim_id,page,claim,value,source,as_of,verdict,notes`) is still read.

## Steps
1. Extract the central claims into `CLAIMS.csv`. Replace typed numbers with `[[v:name]]` macros where the data layer holds them.
2. Open the sources. UNVERIFIED on a material claim means revise or omit; it does not stall the whole piece.
3. R1: the first mention of every featured candidate links to their TIP profile. R2: every mentioned race links to that race. A grade is cited only from the profile that shows it; "not graded" is never zero.
4. `python3 tools/qa/factcheck_gate.py CLAIMS.csv --article content/learn/<file>.html --author <drafter> --build` prints READY (exit 0) or BLOCKED (exit 2). `--build` runs `build.py --strict`.
5. Proportional QA: `tools/qa/smoke.py`, `tools/qa/shots.py` at 375 and 1280 px. A person approves publication; READY is not approval.

## Reject
Unsupported election odds; a search snippet treated as reporting; ad-tracker figures without a retrievable source; causal explanations of price moves; a dark-horse label without a verified criterion; rankings or endorsements.

## Fixtures and failure semantics
`tests/test_factcheck_gate.py` (16): unresolved verdicts, missing source or time, non-independent reviewer, governor-profile grade, ungraded grade, aggregator-only poll, finance row with no total, market without quote kind, NOT FOR PUBLICATION image, macro without a ledger row, and the lean ledger (ready without finance rows; real link, source date and no unresolved doubt required). The gate never edits a ledger or an article.

## Changelog
2.0.0 (2026-10-24) lean `CLAIMS.csv` mode; finance, market and poll checks fire only for rows that make those claims. 1.1.0 (2026-10-23) deterministic gate and typed checks. 1.0.0 (2026-10-23) first ledger procedure.
