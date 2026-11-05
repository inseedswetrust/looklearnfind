# Politics 2.0 policy (version 0.1.0, LOCKED, approved 2026-11-05)

Version-controlled, not immutable: change only by a numbered revision recorded in `CHANGELOG.md` with an authorization entry. `tools/qa/politics_contract_check.py` fails when a policy file's hash differs from `SHA256SUMS.txt` without a matching changelog line.

Read this index, then the module you need, before editing anything under Politics.

| File | Holds |
|---|---|
| `05_INVARIANTS_AND_ACCEPTANCE.md` | The ten non-negotiable invariants, acceptance tests |
| `01_INFORMATION_ARCHITECTURE.md` | Routes, pillars, temporal model, landing page |
| `02_EDITORIAL_FORMATS_AND_WORKFLOWS.md` | Daily Signal and the other formats, gates |
| `04_ACCOUNTABILITY_TRACKER.md` and `schemas/` | Position taxonomy and schema |
| `LANDING_COPY.md` | Approved copy deck |
| `DISCOVERY_DIFF.md` | Dated inventory of the eight unknowns |
| `VERSION`, `STATUS`, `CHANGELOG.md`, `SHA256SUMS.txt` | Version control |

## Implementation map (local, not deployed)
- Landing and daily pages: `politics.py`, driven by `data/politics_home.json`, `data/discovery.json` and approved records in `data/politics_daily/*.json`. Written only through `build.shell()`.
- Styles: `static/css/politics.css` (tokens only).
- Checks: `python tools/qa/politics_contract_check.py` and `tests/test_politics.py`.
- Precedence: the Production Lock (`docs/production/`) and the global shell invariants still apply. Where this policy asks for more than a verified source supports, the page shows an intentional empty state, never a result.
