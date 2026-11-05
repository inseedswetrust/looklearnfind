# 05 — Permanent Claude DNA: installation, versioning, acceptance

## Scope and source of truth
This package is a *candidate* addition to LLF's existing `docs/production/` lock. It does not supersede production rules or silently change existing `CLAUDE.md`. Installation requires explicit owner approval. Use `docs/politics/` as canonical location after approval. Root `CLAUDE.md` and `docs/election-build/INDEX.md` must point to `docs/politics/INDEX.md` by relative path. For Politics work, read that index and the necessary modular spec before editing.

## Non-negotiable invariants
1. Shared global shell on every generated public page, with persistent charcoal desktop rail and functional mobile drawer. Only shared generator owns navigation and Look/Learn/Find logo state.
2. Politics main-pane sections always: Daily Signal, Follow the Story, Explore a State, The Record, On Our Radar, Watch/Read/Verify and source-first CTA. Empty modules must have intentional states or be omitted (not blank empty cards).
3. Unique canonical URLs preserved; original 21 political articles are not overwritten by postmortems.
4. No election outcome, margin, voter mandate interpretation, market datum or public-position claim without attributable dated evidence.
5. Public accountability status taxonomy strictly enforced: no-response != opposition; public statement != confidential leadership vote.
6. Every published daily article, state report and signal carries story ID, source register, author/editor and update log.
7. Claim verification and video/media QA are separate gates; final human authorization remains required before deploy/post.
8. Data snapshots and analysis copy are versioned separately. Only owner-approved snapshot displayed.
9. TIP public candidate profiles are linked by stable IDs; TIP Action Party participation is an external clearly labeled workflow.
10. No rewrite of reusable assets without asset manifest verification and rights check.

## Bounded install work order for Claude
1. Read current Production Lock, skill manifest, brand CSS, current local UX branch, `docs/NEXUS.md`, results schemas and this package.
2. Produce `DISCOVERY_DIFF.md` ONLY for the eight targeted unknowns in `03_ASSET_REUSE_AND_FINAL_DISCOVERY.md`. No generic rediscovery.
3. Add approved `docs/politics/` policy files with `VERSION`, `STATUS=LOCKED`, owner approval date and a SHA256 checksum manifest. The policy is *version-controlled*, not actually immutable: change by explicit numbered revision only.
4. Wire pointers in root instructions and `docs/election-build/INDEX.md`, then add `tools/qa/politics_contract_check.py` and fixtures. Contract checks verify shell, mode, source dates, card links, missing stories, data staleness, search inclusion and URL preservation.
5. Implement one local `/politics/` prototype and the `/politics/daily/` index with fixtures, then produce 1440/1024/390/320 screenshots and accessibility checks.
6. Do NOT deploy, push, change results fields or create live TIP campaigns as part of this installation.

## QA / acceptance
- Existing strict build and production regression suite pass; zero silent old URL changes.
- Sidebar and drawer parity, focus management and mode indication pass on desktop/mobile.
- Search includes state hubs and all new politics entry points.
- Daily source links, story IDs, editorial gates and post-election context banners have tests.
- `docs/politics/CHANGELOG.md` records each approved change and rationale; CI/release checks fail if spec hash changes without version/changelog/authorization entry.
- Provide proof in `INSTALL_REPORT.md`, changeset, screenshot contact sheet, broken-link and diff report, no unsupported result cards.
