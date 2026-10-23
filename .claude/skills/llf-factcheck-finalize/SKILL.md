---
name: llf-factcheck-finalize
description: Independent pre-publication fact check for LLF election and market articles: claim ledger, verdicts, publishing rules R1 and R2, and a READY or BLOCKED report. Use before any story or page goes live.
---

# llf-factcheck-finalize

## Inputs
The story file (`content/learn/*.html`), the packet in `data/elections/<ST>/` or `data/elections/dark_horse/`, raw captures, `docs/election-build/fact_check.csv` as the ledger format.

## Steps
1. Extract every checkable claim (headline, dek, numbers, quotes, captions, alt text) into the ledger: `claim_id,page,claim,value,source,as_of,verdict,notes`.
2. Verdicts: VERIFIED, ATTRIBUTED, NEEDS_CONTEXT, UNVERIFIED, CONTRADICTED, STALE. Fix or remove everything UNVERIFIED, CONTRADICTED or STALE.
3. Re-fetch originals for money, markets, polls and results. Money: keep candidate receipts, independent expenditures and transfers apart; de-duplicate 24/48-hour notices against periodic filings and drop memo rows. Markets: record ticker, contract kind, quote type, timestamp. Polls: pollster, sponsor, partisan flag, field dates, sample, method, margin of error.
4. Replace typed numbers with `[[v:name]]` macros where the data exists.
5. R1: every featured candidate links to their TIP profile. R2: every mentioned race links to that race. `python3 build.py --strict` must pass.
6. Run `tools/qa/smoke.py` and `tools/qa/shots.py`; attach results.
7. Output READY or BLOCKED with the blocking claims. A human approves publication.

## Reject
unsupported election odds, ad-tracker figures without a retrievable source, causal explanations of price moves, and any dark-horse label without a verified criterion.
