# Pennsylvania 2026: TIP gap list (for owner approval; nothing in TIP has been changed)

TIP export: docs/state-packets/PA, 2026-11-01 (24 races, 38 race entries, 169 candidate rows). Roster: data/elections/PA/roster.json, parsed from The Green Papers (capture 2026-11-01) because the Department of State candidate list was not found by a plain request. Scope: Governor and 17 House districts. **Pennsylvania has no U.S. Senate race in 2026** (Class 1 was 2024, Class 3 is 2028). TIP's `2026-S-PA` and `2026-H-PA-00` are already marked `cancelled`.

## Matches
All 34 House rows match a TIP race entry by FEC ID (status `active`). Nothing in the House roster is missing from TIP.

## Gaps that need a TIP write
1. **Governor has no race entries.** TIP has the race `2026-GOV-PA` and `needs_review` profiles for Josh Shapiro (`GOV-PA-SHAPIRO`) and Stacy Garrity (`GOV-PA-GARRITY`), but no `race_entries` row for any ticket. Green Papers lists Shapiro (Democratic, incumbent, running mate Austin Davis), Garrity (Republican, running mate Jason Richey) and Ken Krawchuk (Libertarian, running mate John C. Thomas).
2. **Ken Krawchuk (Libertarian, governor) has no profile.** No FEC ID. A `needs_review` profile (`GOV-PA-KRAWCHUK`, slug `pa-gov-2026-krawchuk`) would follow the Minnesota and Michigan pattern.
3. **Open-seat incumbent field, PA-03.** TIP's `2026-H-PA-03` still names Dwight Evans, who announced on June 30, 2025 that he would not seek re-election (Green Papers: "Open"). The Democratic nominee is Chris Rabb. Clearing `incumbent_name` is proposed (as for NJ-12).

## Gaps that need a decision
4. **Profile status.** The Shapiro and Garrity governor profiles are `needs_review`, not public-ready. Promotion is a separate approval after the entries exist.
5. **Entry labels.** Five entries are "National source only"; 33 are "Official candidate record checked". Leave until the state list can be read.

## Report only (no write)
- Write-ins Abby Tilsner (PA-03) and Sergio Zambrana (PA-12), both Socialist Workers Party, are `review` entries in TIP and appear on Green Papers as write-ins.
- Anthony "Tony" Dastra (Green write-in, governor) withdrew on August 25, 2026 per Green Papers; no TIP entry exists and none is proposed.
- Governor write-ins Tony Lane and James Moore are not listed.
- PA-18 (Timothy Murphy) and PA-24, PA-35, PA-36 rows in TIP are leftovers; Pennsylvania has 17 districts. Nothing on the roster uses them.

## Proposed fixes if approved (idempotent TIP repo script `scripts/export/apply-pa-gap-fixes.mjs`, to be written from the MN pattern, not run)
- Create `needs_review` profile `GOV-PA-KRAWCHUK`.
- Insert three governor `race_entries` with status `review` (Shapiro, Garrity, Krawchuk), ballot type printed.
- Clear `incumbent_name` on `2026-H-PA-03`.
- Promotion of the governor entries to `active` is a separate approval (rows backed up first).
