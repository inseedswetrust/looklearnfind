# Minnesota 2026: TIP gap list (for owner approval; nothing in TIP has been changed)

TIP export: docs/state-packets/MN, 2026-10-31 (11 races, 22 race entries, 114 candidate rows). Roster: data/elections/MN/roster.json, parsed from The Green Papers because the Secretary of State list sits behind a captcha and was not read. Scope: Governor (open), U.S. Senate (Class 2, open) and 8 House districts. Registry output: productions/2026/MN/gaps.csv (12 flags, 4 of them need a TIP write).

## Matches
All 17 House rows and 4 of 5 Senate rows match a TIP race entry by FEC ID (status `active`). Nothing in the House is missing from TIP and nothing in TIP is missing from the roster.

## Gaps that need a TIP write
1. **Governor has no race entries.** TIP has the race `2026-GOV-MN` and profiles for Lisa Demuth (`GOV-MN-DEMUTH`) and Amy Klobuchar, but no `race_entries` row for any of the three tickets. Green Papers lists Klobuchar (DFL, running mate Ben Schierer), Demuth (Republican, running mate Ryan Wilson) and Steven Young (Green, running mate Jane Kirby). Tim Walz (`GOV-MN-WALZ`) is not running: he said on January 5, 2026 that he would step out of the race.
2. **Amy Klobuchar has two profiles.** `S6MN00267` (candidate 4327, slug `mn-s-2026`, her Senate record) is tagged to the governor race, and `GOV-MN-KLOBUCHAR` (candidate 8114, slug `mn-gov-2026-klobuchar`) is not tagged to any race. LLF links the second one today. Pick one to carry the governor entry; the other should not be public.
3. **Steven Young (Green, governor) has no profile and no entry.** He has no FEC ID. A `needs_review` profile (`GOV-MN-YOUNG`, slug `mn-gov-2026-young`) would follow the Michigan and New Jersey pattern.
4. **Kevin Dwire (Socialist Workers Party, Senate write-in) has a race entry but no profile.** Status `review`, no FEC ID, "National source only". Leave at `review` (a write-in listed by one secondary source).

## Gaps that need a decision
5. **Open-seat incumbent fields.** TIP's race rows still name the people who are leaving: Tim Walz (governor), Tina Smith (Senate) and Angie Craig (MN-02). None is on the roster. Walz and Smith are retiring and Craig lost the Democratic Senate nomination, so none seeks the seat. Clearing the three `incumbent_name` fields (as was done for NJ-12) is proposed.
6. **Incumbent flag on Walz's candidate row** is still `true`. Proposed: leave it, since he holds the office until January 2027.
7. **Entry labels.** Sixteen entries are "Confirmed from owner-supplied sources" (BallotReady and Ballotpedia, October 14), two are "Official primary or filing record checked" and four are "National source only". Do not change them until the Secretary of State list can be read.

## Report only (no write)
- Peggy Flanagan, DeVelle Jackson, Tom Emmer and Pete Stauber: `profile_unverified` (editor information).
- Rebecca Whiting: no photo and no links on TIP.
- Lisa Demuth: no links on TIP.

## Proposed fixes if approved (idempotent TIP repo script `scripts/export/apply-mn-gap-fixes.mjs`, prepared but not run)
- Create `needs_review` profile `GOV-MN-YOUNG`.
- Insert three governor `race_entries` with status `review` (Klobuchar, Demuth, Young), ballot type printed, linked to the chosen profiles.
- Clear `incumbent_name` on `2026-GOV-MN`, `2026-S-MN` and `2026-H-MN-02`.
- Promoting the three governor entries from `review` to `active` is a separate approval (the Michigan pattern backs up the rows first).
